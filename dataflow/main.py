import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
import json
from datetime import datetime
import argparse

def generate_city_key(city, country):
    return f"{city}_{country}".replace(" ", "_").lower()

class ParseJson(beam.DoFn):
    def process(self, element):
        return [json.loads(element)]


class DeduplicateByKey(beam.DoFn):
    def process(self, element, existing_keys):
        key = element['city_key']
        if key not in existing_keys:
            yield element

class TransformForSilver(beam.DoFn):
    def process(self, element):
        try:
            return [{
                'city': element['name'] if element['name'] else "Unknown",
                'timestamp': element['timestamp'],
                'country': element['sys']['country'],
                'latitude': element['coord']['lat'],
                'longitude': element['coord']['lon'],
                'temp_celsius': round(element['main']['temp'] - 273.15,2), #from Kelvin to Celsius 
                'temp_fahrenheit': round((element['main']['temp'] - 273.15) * 9/5 + 32,2),
                'humidity': element['main']['humidity'],
                'pressure': element['main']['pressure'],
                'wind_speed': element['wind']['speed'],
                'description': element['weather'][0]['description']
            }]
        except KeyError as e:
            print(f"KeyError: {e} - Skipping this element")
            return [{
                'city': "Unknown",
                'timestamp': "1900-01-01T00:00:00",
                'country': "Unknown",
                'latitude': 0.0,
                'longitude': 0.0,
                'temp_celsius':None,
                'temp_fahrenheit': None,
                'humidity': None,
                'pressure': None,
                'wind_speed': None,
                'description': None
            }]

class PrepareForGoldLayer(beam.DoFn):
    def process(self, element):
        try:
            date_obj = datetime.strptime(element['timestamp'].split('T')[0], '%Y-%m-%d')
            date_key = int(date_obj.strftime('%Y%m%d')) if date_obj else 19000101
            city_key = generate_city_key(element['city'], element['country'])
            return [{
                'date_key': date_key,
                'city_key': city_key if  city_key else "Unknow",  
                'avg_temp_celsius': element['temp_celsius'],
                'avg_humidity': float(element['humidity']),
                'avg_pressure': float(element['pressure']),
                'avg_wind_speed': element['wind_speed']
            }]
        except KeyError as e:
            print(f"KeyError: {e} - Skipping this element")
            return [{
                'date_key': 19000101,
                'city_key': "Unknow",  
                'avg_temp_celsius': 0.0,
                'avg_humidity': 0.0,
                'avg_pressure': 0.0,
                'avg_wind_speed': 0.0
            }]
    
class PrepareDateDim(beam.DoFn):
    def process(self, element):
        try:
            date_obj = datetime.strptime(element['timestamp'].split('T')[0], '%Y-%m-%d')
            date_key = int(date_obj.strftime('%Y%m%d')) if date_obj else 19000101
            
            return [{
                'date_key': date_key,
                'full_date': date_obj.date() if date_obj else None,
                'year': date_obj.year if date_obj else 1900,
                'month': date_obj.month if date_obj else 1,
                'day': date_obj.day if date_obj else 1,
                'day_of_week': date_obj.weekday(),
                'day_name': date_obj.strftime('%A'),
                'month_name': date_obj.strftime('%B'),
                'quarter': (date_obj.month - 1) // 3 + 1
            }]
        except KeyError as e:
            print(f"KeyError: {e} - Skipping this element")
            return [{
                'date_key': 19000101,
                'full_date': None,
                'year': 1900 ,
                'month': 1 ,
                'day': 1,
                'day_of_week': None,
                'day_name': None,
                'month_name': None,
                'quarter': None
            }]
    
class PrepareCityDim(beam.DoFn):
    def process(self, element):
        city_key = generate_city_key(element['city'], element['country'])
        try:
            return [{
                'city_key': city_key if city_key else "Unknown",  
                'city_name': element['city'],
                'country': element['country'],
                'latitude': element['latitude'],
                'longitude':  element['longitude'] 
            }]
        except KeyError as e:
            print(f"KeyError: {e} - Skipping this element")
            return [{
                'city_key': "Unknown",  
                'city_name': "Unknown",
                'country': "Unknown",
                'latitude':  0.0,
                'longitude':  0.0
            }]

def run(argv=None, save_main_session=True):
    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    
    current_time = datetime.now()
    date_folder = current_time.strftime("%Y/%m/%d")

    with beam.Pipeline(options=pipeline_options) as p:
        # Read and transform data
        transformed_data = (p
            | 'Read from GCS' >> beam.io.ReadFromText(f'gs://easygo-bronze-bucket/{date_folder}/*.json')
            | 'Parse JSON' >> beam.ParDo(ParseJson())
            | 'Transform for Silver' >> beam.ParDo(TransformForSilver())
            | 'Add Key' >> beam.Map(lambda elem: ((elem['city'], elem['timestamp']), elem))
            | 'Group by Key' >> beam.GroupByKey()
            | 'Take First to deduplicate' >> beam.Map(lambda key_value: next(iter(key_value[1])))
        )

        # Read existing keys from BigQuery
        existing_keys = (p 
            | 'Read existing keys' >> beam.io.ReadFromBigQuery(
                query='SELECT city_key FROM `easygo-task-428510.weather_gold.CityDim`',
                use_standard_sql=True)
            | 'Extract keys' >> beam.Map(lambda row: row['city_key'])
            | 'Create set' >> beam.combiners.ToSet()
        )

        # Write to Silver layer
        transformed_data | 'Write to Silver BigQuery' >> beam.io.WriteToBigQuery(
            table='easygo-task-428510.weather_silver.WeatherData',
            schema ='city:STRING,country:STRING,latitude:FLOAT,longitude:FLOAT,temp_celsius:FlOAT,temp_fahrenheit:FlOAT,humidity:INTEGER,pressure:INTEGER,wind_speed:FLOAT,description:STRING,timestamp:TIMESTAMP',
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        )

        # Prepare data for Gold layer
        gold_data = (transformed_data 
            | 'Prepare for Gold' >> beam.ParDo(PrepareForGoldLayer())
            | 'Group by City and Date' >> beam.Map(lambda x: ((x['city_key'], x['date_key']), x))
            | 'Group by Key for Aggregation' >> beam.GroupByKey()
            | 'Aggregate Data' >> beam.Map(lambda kv: {
                'date_key': kv[0][1],
                'city_key': kv[0][0],
                'avg_temp_celsius': sum([item['avg_temp_celsius'] for item in kv[1]]) / len(kv[1]),
                'avg_humidity': sum([item['avg_humidity'] for item in kv[1]]) / len(kv[1]),
                'avg_pressure': sum([item['avg_pressure'] for item in kv[1]]) / len(kv[1]),
                'avg_wind_speed': sum([item['avg_wind_speed'] for item in kv[1]]) / len(kv[1])
            })
        )

        # Write to WeatherFact table
        gold_data | 'Write to WeatherFact' >> beam.io.WriteToBigQuery(
            table='easygo-task-428510.weather_gold.WeatherFact',
            schema ='date_key:INTEGER,city_key:STRING,avg_temp_celsius:FLOAT,avg_humidity:FLOAT,avg_pressure:FLOAT,avg_wind_speed:FLOAT',
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
        )

        # Prepare and write DateDim
        (transformed_data 
            | 'Prepare DateDim' >> beam.ParDo(PrepareDateDim())
            | 'Key by date_key' >> beam.Map(lambda row: (row['date_key'], row))
            | 'Group by date_key' >> beam.GroupByKey()
            | 'Take first of each group' >> beam.Map(lambda key_value: next(iter(key_value[1])))
            | 'Write to DateDim' >> beam.io.WriteToBigQuery(
                table='easygo-task-428510.weather_gold.DateDim',
                schema='date_key:INTEGER,full_date:DATE,year:INTEGER,month:INTEGER,day:INTEGER,day_of_week:INTEGER,day_name:STRING,month_name:STRING, quarter:INTEGER',
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

        # Prepare and write CityDim
        (transformed_data 
            | 'Prepare CityDim' >> beam.ParDo(PrepareCityDim())
            | 'Key by city_key' >> beam.Map(lambda row: (row['city_key'], row))
            | 'Group by city_key' >> beam.GroupByKey()
            | 'Take first of each group for city' >> beam.Map(lambda key_value: next(iter(key_value[1])))
            | 'Deduplicate by key' >> beam.ParDo(DeduplicateByKey(), existing_keys=beam.pvalue.AsSingleton(existing_keys))
            | 'Write to CityDim' >> beam.io.WriteToBigQuery(
                table='easygo-task-428510.weather_gold.CityDim',
                schema='city_key:STRING,city_name:STRING,country:STRING,latitude:FLOAT,longitude:FLOAT',
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == '__main__':
    run()