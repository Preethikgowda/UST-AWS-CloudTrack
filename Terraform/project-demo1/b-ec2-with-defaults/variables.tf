variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "ami_id" {
  type    = string
  default = "ami-05cf1e9f73fbad2e2"
}

variable "instance_name" {
  type    = string
  default = "EC2-WithDefaults"
}
