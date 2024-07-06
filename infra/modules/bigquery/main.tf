# Create a BigQuery dataset for the silver layer
resource "google_bigquery_dataset" "weather_silver" {
  dataset_id                  = "weather_silver"
  friendly_name               = "Weather Data Silver Layer"
  description                 = "This dataset contains the silver layer table for weather data"
  location                    = var.location
  default_table_expiration_ms = null  # Set to null for no expiration
}

# Create the WeatherSilver table
resource "google_bigquery_table" "weather_silver" {
  dataset_id = google_bigquery_dataset.weather_silver.dataset_id
  table_id   = "WeatherData"

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = <<EOF
[
  {
    "name": "city",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Name of the city"
  },
  {
    "name": "temp_celsius",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Temperature in Celsius"
  },
  {
    "name": "temp_fahrenheit",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Temperature in Fahrenheit"
  },
  {
    "name": "humidity",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Humidity percentage"
  },
  {
    "name": "pressure",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Atmospheric pressure in hPa"
  },
  {
    "name": "wind_speed",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Wind speed in meters per second"
  },
  {
    "name": "description",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Text description of weather conditions"
  },
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "Timestamp of data collection"
  }
]
EOF

  deletion_protection = false
}
# Create a BigQuery dataset for gold layer
resource "google_bigquery_dataset" "weather_gold" {
  dataset_id                  = "weather_gold"
  friendly_name               = "Weather Data Gold Layer"
  description                 = "This dataset contains the gold layer tables for weather data"
  location                    = var.location
  default_table_expiration_ms = null  # Set to null for no expiration
}

# Create WeatherFact table
resource "google_bigquery_table" "weather_fact" {
  dataset_id = google_bigquery_dataset.weather_gold.dataset_id
  table_id   = "WeatherFact"

#   time_partitioning {
#     type = "DAY"
#     field = "date_key"
#   }

  schema = <<EOF
[
  {
    "name": "date_key",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "Date key for joining with DateDim"
  },
  {
    "name": "city_key",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "City key for joining with CityDim"
  },
  {
    "name": "avg_temp_celsius",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Average temperature in Celsius"
  },
  {
    "name": "avg_humidity",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Average humidity"
  },
  {
    "name": "avg_pressure",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Average pressure"
  },
  {
    "name": "avg_wind_speed",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "Average wind speed"
  }
]
EOF

  deletion_protection = false
}

# Create DateDim table
resource "google_bigquery_table" "date_dim" {
  dataset_id = google_bigquery_dataset.weather_gold.dataset_id
  table_id   = "DateDim"

  schema = <<EOF
[
  {
    "name": "date_key",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "Unique identifier for the date"
  },
  {
    "name": "full_date",
    "type": "DATE",
    "mode": "REQUIRED",
    "description": "Full date in DATE format"
  },
  {
    "name": "year",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "Year"
  },
  {
    "name": "month",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "Month number (1-12)"
  },
  {
    "name": "day",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "Day of the month"
  },
  {
    "name": "day_of_week",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "Day of the week (0-6)"
  },
  {
    "name": "day_name",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Name of the day"
  },
  {
    "name": "month_name",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Name of the month"
  },
  {
    "name": "quarter",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "Quarter of the year (1-4)"
  }
]
EOF

  deletion_protection = false
}

# Create CityDim table
resource "google_bigquery_table" "city_dim" {
  dataset_id = google_bigquery_dataset.weather_gold.dataset_id
  table_id   = "CityDim"

  schema = <<EOF
[
  {
    "name": "city_key",
    "type": "INTEGER",
    "mode": "REQUIRED",
    "description": "Unique identifier for the city"
  },
  {
    "name": "city_name",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Name of the city"
  },
  {
    "name": "country",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Country of the city"
  },
  {
    "name": "latitude",
    "type": "FLOAT",
    "mode": "REQUIRED",
    "description": "Latitude of the city"
  },
  {
    "name": "longitude",
    "type": "FLOAT",
    "mode": "REQUIRED",
    "description": "Longitude of the city"
  }
]
EOF

  deletion_protection = false
}