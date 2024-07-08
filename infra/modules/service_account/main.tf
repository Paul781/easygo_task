resource "google_service_account" "cf-invoker-service_account" {
  account_id   = "cloud-function-invoker"
  display_name = "Cloud Function Invoker Service Account"
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = var.cf_project
  region         = var.cf_region
  cloud_function = var.cf_name

  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:${google_service_account.cf-invoker-service_account.email}"
}