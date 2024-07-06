resource "google_storage_bucket" "bronze-bucket" {
  name     = "easygo-bronze-bucket"
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