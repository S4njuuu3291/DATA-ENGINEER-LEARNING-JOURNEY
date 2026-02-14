# Local values untuk configuration yang tidak perlu dijadikan variable
locals {
  terraform_version = "1.0+"

  common_tags = {
    terraform_version = local.terraform_version
    created_date      = "2026-02-13"
  }
}
