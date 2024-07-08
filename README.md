# easygo_task

file structure and explain

solution design diagram and explain

data schema and explain
raw json file bronze, sliver and gold

![alt text](https://github.com/Paul781/easygo_task/blob/dev/image/file_structure.png?raw=true)

Usage:
go to the infra folder, run terraform command locally
$ gcloud auth application-default login
terraform init
terraform plan
terrraform apply --auto-approve


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

improvement:
terraform state file should be stored in GCS bucket not locally
create customized service account for cf and dataflow to enhance the security control

airflow can be used because it is asyncronized call when cloud function triggers the dataflow, cf will not wait until dataflow job done. need to check the dataflow log to know the job fails or not

because of the limit of time, so many things are hardcoded, should parameterized to make app more reusable and flexible

more unit test for diff scenario
should have cicd to run terraform not run locally
can use airflow to schedule the job


assumption:
gcloud installed locally
gcloud login to your profile and set up the gcp project

Bronze Layer: stored in Google Cloud Storage. can use the BQ external table to read the data from file in bucket

OpenWeather API key is ready

cloud scheduler run daily so the cloud function only be triggered once per day

gcp project exists， storage，cf，dataflow all necessary api is enabled，
necessary permisssion is granted to developer user

