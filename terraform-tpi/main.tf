provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "us-west-2"
  region = "us-west-2"
}

module "region_us_east_1" {
  source   = "./modules/region_deploy"
  providers = {
    aws = aws.us-east-1
  }
  region = "us-east-1"
}

module "region_us_west_2" {
  source   = "./modules/region_deploy"
  providers = {
    aws = aws.us-west-2
  }
  region = "us-west-2"
}
