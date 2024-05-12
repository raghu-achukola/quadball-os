resource "aws_iam_role" "snowflake_iam_role" {
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
              "s3:PutObject",
              "s3:GetObject",
              "s3:GetObjectVersion",
              "s3:DeleteObject",
              "s3:DeleteObjectVersion"
            ],
            "Resource": "arn:aws:s3:::quadball-os-landing/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": "arn:aws:s3:::quadball-os-landing",
        }
    ]
  })
}

            "Principal": {
                "AWS": "765351438123"
            },
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "0000"
                }
            }