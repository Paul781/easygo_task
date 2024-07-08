variable "project_id" {
  type = string
  default = "easygo-task-428510"
  description = "The project identifier"
}
variable "project_region" {
  type = string
  default = "australia-southeast1"
  description = "The project region"
}
variable "bucket_storage_class" {
        type = string
        default = "STANDARD"
}

variable "location" {
  default = "australia-southeast1"
}