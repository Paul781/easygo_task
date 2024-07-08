# File Structure
<img align="left" width="120" height="200" src="image/file_structure.png">
<p>
- cloudfunction folder stores all the python code for cloud function <br>
- dataflow folder stores all the python code for Dataflow <br>
- generated folder saves the zip file for cloud function code <br>
- image folder saves all the picture used by readme file<br>
- infra folder saves all the terraform codes<br>
</p>
<p><br></p>
<p><br></p>
<p><br></p>




# Data Architecture Deisgn
![alt text](image/data_architecture.png)

This project sets up a data pipeline on Google Cloud Platform to ingest weather data from OpenWeatherMap API, process it, and store it following the medallion architecture.

The pipeline runs automatically:
1. The Cloud Function is triggered daily by Cloud Scheduler to ingest new data.
2. Cloud Function will call the Weather API to get the weather data (json file) and save the json file to cloud storage
3. The Dataflow job is triggered by cloud function after the file saved in cloud storage bucket
4. The Dataflow job will extract the raw data from cloud storage bucket (bronze layer) and do data transformation then load the data into Bigquery silver dataset (silver layer)  first then Bigquery Gold dataset (Gold layer)




<p><br></p>

# Data Schema 
![alt text](image/data_model.png)

Data Layers:
- Bronze: Raw JSON data in Cloud Storage
- Silver: Deduplicated, Processed, detailed data in BigQuery Silver dataset
- Gold: Aggregated data (daily averages) in BigQuery Gold dataset

In Bronze layer, it is the raw json file which is get from the Weather API. the json format is as the above diagram showed.

Sliver layer is in Bigquery datawarehouse and sliver dataset. there is one table in this layer:weatherData. column names are listed in the above diagram.

Gold layer is in Bigquery datawarehouse and gold dataset. there are three tables in this layer: one fact table and two dimension tables. weatherFact table is fact table. CityDim and DateDim are dimension tables. column names for those tables are listed in the above diagram.

All the BQ datasets and tables are created by terraform. The initialization for schemas see this terraform file. [here](infra/modules/bigquery/main.tf)

# Instructions for Setup
go to the infra folder, run terraform command locally
$ gcloud auth application-default login
terraform init
terraform plan
terrraform apply --auto-approve


Once all the components are deployed by terraform. Go to the cloud scheduler console and choose the scheduler just built and click the "force run" button on the right side to run the entire pipeline.

can update the lat and lon in cloud function env variable to get the weather data for different city. by default it is melbourne

# create dataflow template after running terraform
python -m main \
--runner DataflowRunner \
--project easygo-task-428510 \
--staging_location gs://easygo-df-bucket/staging \
--temp_location=gs://easygo-df-bucket/temp \
--template_location gs://easygo-df-bucket/templates/weather-etl-job \
--region australia-southeast1


# run the dataflow job
gcloud auth application-default login
pip install -r requirements.txt
python main.py \
  --project=easygo-task-428510 \
  --region=australia-southeast1 \
  --runner=DataflowRunner \
  --temp_location=gs://easygo-df-bucket/temp \
  --staging_location=gs://easygo-df-bucket/staging \
  --job_name=weather-etl-job \
  --experiments=enable_data_sampling

# run unittest for dataflow 
python -m unittest test_main.py    





# Design Choices
### API Selection and Data Ingestion
### Data Architecture Design
scalability, reliability, and efficiency
### ETL Pipelines

# Improvement
terraform state file should be stored in GCS bucket not locally
create customized service account for cf and dataflow to enhance the security control

airflow can be used because it is asyncronized call when cloud function triggers the dataflow, cf will not wait until dataflow job done. need to check the dataflow log to know the job fails or not

because of the limit of time, so many things are hardcoded, should parameterized to make app more reusable and flexible

more unit test for diff scenario
should have cicd to run terraform not run locally
can use airflow to schedule the job


# Assumption
gcloud installed locally
gcloud login to your profile and set up the gcp project

Bronze Layer: stored in Google Cloud Storage. can use the BQ external table to read the data from file in bucket

OpenWeather API key is ready

cloud scheduler run daily so the cloud function only be triggered once per day

gcp project exists， storage，cf，dataflow all necessary api is enabled，
necessary permisssion is granted to developer user

