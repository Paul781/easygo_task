import os
import logging
import requests
import json
from datetime import datetime
from google.cloud import storage
from google.cloud import dataflow_v1beta3
from google.cloud.dataflow_v1beta3.types import LaunchTemplateParameters, RuntimeEnvironment

def http_handler(request):
    api_key = "e2408ac071e218ec873f0a4ccde2e0fb"
    lat = os.environ['lat']
    lon = os.environ['lon']

    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'

    # Fetch data from API
    try:
        response = requests.get(url)
        data = response.json()

        # Add timestamp
        current_time = datetime.now()
        data['timestamp'] = datetime.now().isoformat()

        # Prepare for Cloud Storage
        storage_client = storage.Client()
        bucket = storage_client.bucket("easygo-bronze-bucket")
        # Create a folder structure based on date
        date_folder = current_time.strftime("%Y/%m/%d")
        blob_name = f'{date_folder}/weather_data_{current_time.strftime("%Y%m%d_%H%M%S")}.json'
        blob = bucket.blob(blob_name)

        # Upload to Cloud Storage
        blob.upload_from_string(json.dumps(data))


        # Trigger Dataflow job
        project_id = "easygo-task-428510"
        job_name = f'weather-etl-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        template_path = "gs://easygo-df-bucket/templates/weather-etl-job"
        region = "australia-southeast1"

        # Set up the client
        client = dataflow_v1beta3.TemplatesServiceClient()

        # Set up the runtime environment
        runtime_environment = RuntimeEnvironment(
            temp_location='gs://easygo-df-bucket/temp'
        )

        # Set up the launch parameters
        launch_parameters = LaunchTemplateParameters(
            job_name=job_name,
            parameters={},  # Add any template parameters here
            environment=runtime_environment
        )

        # Launch the template
        response = client.launch_template(
            request={
                "project_id": project_id,
                "gcs_path": template_path,
                "launch_parameters": launch_parameters,
                "location": region,
            }
        )


        return f'Data ingested and Dataflow job triggered: {response.job.id}'

    except Exception as e:
        print(f"Error uploading to Cloud Storage: {e}")
        return f"Error: Failed to upload data to Cloud Storage - {str(e)}"


   
    response_body = 'Weather data successfully fetched and stored'
    return response_body
