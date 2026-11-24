terraform {
  backend "s3" {
    bucket         = "online-boutique-tfstate-bucket"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "online-boutique-tfstate-lock"
  }
}
