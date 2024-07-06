resource "google_cloud_scheduler_job" "job" {
  name             = "cloud-function-scheduler"
  description      = "Trigger the ${google_cloudfunctions_function.function.name} Cloud Function."
  schedule         = "0 0 * * *" # Every Day
  time_zone        = "Australia/Sydney"
  attempt_deadline = "900s" # 15 mins

  http_target {
    http_method = "GET"
    uri         = google_cloudfunctions_function.function.https_trigger_url

    oidc_token {
      service_account_email = var.sa_email
    }
  }
}


# cloud function
resource "google_cloudfunctions_function" "function" {
  name        = "api-read-cf"
  description = "Cloud Function loads data from API to bucket"
  runtime     = "python37"

  available_memory_mb   = 512
  source_archive_bucket = var.bucket_name
  source_archive_object = var.object
  trigger_http          = true
  entry_point           = "http_handler" # This is the name of the function that will be executed in your Python code
}