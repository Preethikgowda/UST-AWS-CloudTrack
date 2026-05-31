provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "simple_ec2" {
  ami           = "ami-05cf1e9f73fbad2e2"  
  instance_type = "t2.micro"

  tags = {
    Name = "demo"
  }
}
