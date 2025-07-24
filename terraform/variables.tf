# terraform/variables.tf
variable "aws_region" {
  description = "The AWS region where resources will be deployed."
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Name for the project, used in resource naming and tags."
  type        = string
  default     = "SpikePolars"
}

variable "environment" {
  description = "The deployment environment (e.g., dev, prod, staging)."
  type        = string
  default     = "demo"
}

variable "data_source_bucket_name" {
  description = "Name of the S3 bucket containing the input CSV files."
  type        = string
  default     = "spike-polars-data"
}

variable "data_destination_prefix" {
  description = "Prefix/folder within the data source bucket for processed Parquet files."
  type        = string
  default     = "destination"
}

variable "ecr_repo_name" {
  type    = string
  default = "spike/spikepolars"
}
