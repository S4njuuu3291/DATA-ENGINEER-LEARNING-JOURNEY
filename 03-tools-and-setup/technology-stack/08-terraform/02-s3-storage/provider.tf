terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Optional: Uncomment untuk menggunakan Terraform Cloud
  # cloud {
  #   organization = "your-org-name"
  #
  #   workspaces {
  #     name = "learning-terraform"
  #   }
  # }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region

  access_key = var.aws_access_key
  secret_key = var.aws_secret_key

  # Optionally allow skipping requesting account ID
  skip_metadata_api_check = true
  skip_region_validation  = false

  default_tags {
    tags = {
      Environment = "Learning"
      Project     = "Terraform-Fundamentals"
      ManagedBy   = "Terraform"
      Chapter     = "02-s3-storage"
    }
  }
}
