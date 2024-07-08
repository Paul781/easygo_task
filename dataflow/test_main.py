import unittest
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to
from apache_beam import Create, ParDo
from main import TransformForSilver 

class TestTransformForSilver(unittest.TestCase):

    def test_transform_for_silver_valid_input(self):
        # Arrange
        input_data = {
            'name': 'London',
            'timestamp': '2023-07-08T12:00:00',
            'sys': {'country': 'GB'},
            'coord': {'lat': 51.5074, 'lon': -0.1278},
            'main': {'temp': 293.15, 'humidity': 70, 'pressure': 1013},
            'wind': {'speed': 5.1},
            'weather': [{'description': 'cloudy'}]
        }

        expected_output = [{
            'city': 'London',
            'timestamp': '2023-07-08T12:00:00',
            'country': 'GB',
            'latitude': 51.5074,
            'longitude': -0.1278,
            'temp_celsius': 20.0,
            'temp_fahrenheit': 68.0,
            'humidity': 70,
            'pressure': 1013,
            'wind_speed': 5.1,
            'description': 'cloudy'
        }]

       
        with TestPipeline() as p:
            output = (
                p | Create([input_data])
                  | ParDo(TransformForSilver())
            )
            assert_that(output, equal_to(expected_output))

    def test_transform_for_silver_missing_data(self):
        
        input_data = {
            # Missing 'name' and other fields
            'timestamp': '2023-07-08T12:00:00',
        }

        expected_output = [{
            'city': 'Unknown',
            'timestamp': '1900-01-01T00:00:00',
            'country': 'Unknown',
            'latitude': 0.0,
            'longitude': 0.0,
            'temp_celsius': None,
            'temp_fahrenheit': None,
            'humidity': None,
            'pressure': None,
            'wind_speed': None,
            'description': None
        }]

        with TestPipeline() as p:
            output = (
                p | Create([input_data])
                  | ParDo(TransformForSilver())
            )
            assert_that(output, equal_to(expected_output))

if __name__ == '__main__':
    unittest.main()