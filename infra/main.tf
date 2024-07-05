# buckets
resource "google_storage_bucket" "bronze-bucket" {
  name     = "easygo-bronze-bucket"
  location = var.location
  storage_class = var.bucket_storage_class
  force_destroy = false
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "silver-bucket" {
  name     = "easygo-silver-bucket"
  location = var.location
  storage_class = var.bucket_storage_class
  force_destroy = false
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "gold-bucket" {
  name     = "easygo-gold-bucket"
  location = var.location
  storage_class = var.bucket_storage_class
  force_destroy = false
  uniform_bucket_level_access = true
}


resource "google_storage_bucket" "cf-bucket" {
  name     = "easygo-cf-bucket"
  location = var.location
  storage_class = var.bucket_storage_class
  force_destroy = false
  uniform_bucket_level_access = true
}


data "archive_file" "src" {
  type        = "zip"
  source_dir  = "${path.root}/../cloudfunction" # Directory where your Python source code is
  output_path = "${path.root}/../generated/src.zip"
}

resource "google_storage_bucket_object" "archive" {
  name   = "${data.archive_file.src.output_md5}.zip"
  bucket = google_storage_bucket.cf-bucket.name
  source = "${path.root}/../generated/src.zip"
}

# dataflow-bucket



# service accounts and IAM roles
resource "google_service_account" "cf-invoker-service_account" {
  account_id   = "cloud-function-invoker"
  display_name = "Cloud Function Invoker Service Account"
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:${google_service_account.cf-invoker-service_account.email}"
}


# cloud scheduler
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
      service_account_email = google_service_account.cf-invoker-service_account.email
    }
  }
}


# cloud function
resource "google_cloudfunctions_function" "function" {
  name        = "api-read-cf"
  description = "Cloud Function loads data from API to bucket"
  runtime     = "python37"

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.cf-bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  entry_point           = "http_handler" # This is the name of the function that will be executed in your Python code
}