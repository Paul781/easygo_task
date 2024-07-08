output "cf-bucket-name" {
  value = google_storage_bucket.cf-bucket.name
}

output "archive-object-name" {
  value = google_storage_bucket_object.archive.name
}