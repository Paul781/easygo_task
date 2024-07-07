import os
import logging
import requests
import json
from datetime import datetime
from google.cloud import storage

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

    except Exception as e:
        print(f"Error uploading to Cloud Storage: {e}")
        return f"Error: Failed to upload data to Cloud Storage - {str(e)}"


   
    response_body = 'Weather data successfully fetched and stored'
    return response_body
