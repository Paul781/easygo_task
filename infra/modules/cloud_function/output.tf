output "cf-name" {
  value = google_cloudfunctions_function.function.name
}

output "cf-project" {
  value = google_cloudfunctions_function.function.project
}

output "cf-region" {
  value = google_cloudfunctions_function.function.region
}
