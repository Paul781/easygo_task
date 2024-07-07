# buckets
module "bucket" {
  source = "./modules/bucket"
  bucket_storage_class = var.bucket_storage_class
  location = var.location
}

# service accounts and IAM roles
module "service_account" {
  source     = "./modules/service_account"
  cf_project = module.cloud_function.cf-project
  cf_region  = module.cloud_function.cf-region
  cf_name    = module.cloud_function.cf-name
}

# cloud scheduler and cloud function
module "cloud_function" {
  source     = "./modules/cloud_function"
  sa_email  = module.service_account.cf-invoker-service-account-email
  bucket_name = module.bucket.cf-bucket-name
  object = module.bucket.archive-object-name
}

module "bigquery" {
    source = "./modules/bigquery"
    location = var.location
}


