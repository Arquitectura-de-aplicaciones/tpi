terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
  backend "s3" {
    bucket  = "tpi-tfstate"
    key     = "terraform.tfstate"
    region  = "us-west-2"
    encrypt = true
  }
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "web_server" {
  ami           = "ami-830c94e3"
  instance_type = "t2.nano"
  tags = {
    Name = "web_server"
  }
}

/*
resource "aws_instance" "backend_server" {
  ami           = "ami-830c94e3"
  instance_type = "t3.nano"
  tags = {
    Name = "backend_server"
  }
}
*/

resource "aws_db_instance" "primary_db" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t2.micro"
  db_name              = "BackendDatabase"
  username             = "user"
  password             = "pass"
  parameter_group_name = "default.mysql5.7"
  tags = {
    Name = "primary_db"
  }
}

/*
resource "aws_db_instance" "read_replica" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "5.7.44"
  instance_class       = "db.t3.micro" 
  db_name              = "BackendDatabaseReadReplica"
  username             = "user"
  password             = "$QtDv%$2tA6dq^"
  parameter_group_name = "default.mysql5.7"
  tags = {
    Name = "ReadReplica"
  }
}*/

resource "aws_lambda_function" "data_processing" {
  function_name = "data_processing"
  handler       = "index.handler"
  runtime       = "nodejs20.x"
  role          = aws_iam_role.lambda_role.arn
  s3_bucket     = "tpi-tfstate"
  s3_key        = "function.zip"
  memory_size   = "128"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_s3_bucket" "logs_storage" {
  bucket = "log_storage_tpi"
}