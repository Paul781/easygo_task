# easygo_task


Usage:
go to the infra folder
$ gcloud auth application-default login
terraform init
terraform plan
terrraform apply --auto-approve




improvement:
terraform state file should be stored in GCS bucket not locally
create customized service account for cf and dataflow to enhance the security control

assumption:
gcloud installed locally
gcloud login to your profile and set up the gcp project