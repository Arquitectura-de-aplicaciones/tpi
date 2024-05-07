terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }

}

provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "test_instance" {
  ami           = "ami-830c94e3"
  instance_type = "t2.nano"
  tags = {
    Name = "test_instance"
  }
}

resource "aws_instance" "test_instance_2" {
  ami           = "ami-830c94e3"
  instance_type = "t3.nano"
  tags = {
    Name = "test_instance_2"
  }
}

resource "aws_instance" "test_instance_3" {
  ami           = "ami-830c94e3"
  instance_type = "t2.nano"
  tags = {
    Name = "test_instance_3"
  }
}

resource "aws_db_instance" "example_db" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t2.micro"
  db_name              = "Backend Database"
  username             = "user"
  password             = "pass"
  parameter_group_name = "default.mysql5.7"
  tags = {
    Name = "Backend DB"
  }
}



