terraform {
  backend "s3" {
    bucket = "quadball-os-terraform-bucket"
    key    = "state.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
    region = "us-west-2"
}