provider "aws" {
    alias = "uw2"
    region = "us-west-2"
}

resource "aws_s3_bucket" "bucket"{
    provider = aws.uw2
    bucket = "quadball-os-landing"
}