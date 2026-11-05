variable "aws_region" {
  description = "AWS region for the deployment."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Short project name used in resource names and tags."
  type        = string
  default     = "mediconnect"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "cea"
}

variable "vpc_cidr" {
  description = "CIDR range for the MediConnect VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Two Availability Zones used by the network."
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]

  validation {
    condition     = length(var.availability_zones) == 2
    error_message = "Exactly two Availability Zones are required."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDRs for public subnets."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "app_subnet_cidrs" {
  description = "CIDRs for private application subnets."
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "db_subnet_cidrs" {
  description = "CIDRs for private database subnets."
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24"]
}

variable "db_name" {
  description = "PostgreSQL database name."
  type        = string
  default     = "mediconnect"
}

variable "db_username" {
  description = "PostgreSQL master username."
  type        = string
  default     = "mediconnect_admin"
}

variable "db_instance_class" {
  description = "RDS instance class for the CEA deployment."
  type        = string
  default     = "db.t3.micro"
}

variable "application_secret_arn" {
  description = "ARN of the manually-created Secrets Manager secret containing backend application settings."
  type        = string
  sensitive   = true
}

variable "image_tag" {
  description = "Immutable ECR image tag deployed by ECS."
  type        = string
  default     = "manual-2"
}