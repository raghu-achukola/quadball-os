provider "aws" {
    alias = "uw2"
    region = "us-west-2"
}

resource "aws_s3_bucket" "landing-bucket"{
    provider = aws.uw2
    bucket = "quadball-os-landing"
}

resource "aws_s3_bucket" "processed-bucket"{
    provider = aws.uw2
    bucket = "quadball-os-processed-statsheet-data"
}
