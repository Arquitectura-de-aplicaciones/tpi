variable "region" {}

resource "aws_lambda_function" "example_lambda" {
  function_name = "lambda-${var.region}"
  handler       = "index.handler"
  runtime       = "nodejs20.x"
  role          = aws_iam_role.lambda_role.arn
  filename      = "function.zip"
}

resource "aws_sns_topic" "example_topic" {
  name = "sns-topic-${var.region}"
}

resource "aws_db_instance" "example_db" {
  instance_class   = "db.t2.micro"
  engine           = "mysql"
  engine_version   = "5.7"
  allocated_storage = 20
  db_name          = "mydb"
  username         = "user"
  password         = "pass"
  multi_az         = true
}

resource "aws_instance" "example_instance" {
  ami           = "ami-xxxxxxx"
  instance_type = "t2.micro"
}

resource "aws_s3_bucket" "example_bucket" {
  bucket = "my-example-bucket-${var.region}"
}

resource "aws_cloudwatch_log_group" "example_log_group" {
  name = "/aws/lambda/${aws_lambda_function.example_lambda.function_name}"
}

resource "aws_wafv2_web_acl" "example_acl" {
  name        = "example-acl-${var.region}"
  scope       = "REGIONAL"
  description = "Example ACL for ${var.region}"
  default_action {
    allow {}
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "exampleAclMetric"
    sampled_requests_enabled   = true
  }
}

resource "aws_lb" "example_lb" {
  name               = "lb-${var.region}"
  load_balancer_type = "application"
}

resource "aws_api_gateway_rest_api" "example_api" {
  name        = "example-api-${var.region}"
}

resource "aws_shield_protection" "example_protection" {
  name        = "example-protection-${var.region}"
  resource_arn = aws_lb.example_lb.arn
}

resource "aws_route53_record" "example_dns" {
  zone_id = var.route53_zone_id
  name    = "api.${var.region}.example.com"
  type    = "A"
  alias {
    name                   = aws_lb.example_lb.dns_name
    zone_id                = aws_lb.example_lb.zone_id
    evaluate_target_health = true
  }
}
