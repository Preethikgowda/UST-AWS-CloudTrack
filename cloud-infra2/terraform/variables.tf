variable "region" {
  type    = string
  default = "us-east-1"
}

variable "name_prefix" {
  type    = string
  default = "nutritrack-prod"
}

variable "domain_name" {
  type    = string
  default = "invest-iq.online"
}

variable "route53_zone_id" {
  type    = string
  default = ""
}

variable "custom_vpc_name" {
  type    = string
  default = "nutritrack-prod-vpc"
}

variable "alb_name" {
  type    = string
  default = "nutritrack-prod-alb"
}

variable "frontend_tg_name" {
  type    = string
  default = "nutritrack-prod-frontend-tg"
}

variable "portfolio_tg_name" {
  type    = string
  default = "nutritrack-prod-portfolio-tg"
}

variable "market_tg_name" {
  type    = string
  default = "nutritrack-prod-market-tg"
}

variable "backend_sg_name" {
  type    = string
  default = "nutritrack-prod-backend-sg"
}

variable "private_app_rt_az1_name" {
  type    = string
  default = "nutritrack-prod-private-app-rt-az1"
}

variable "private_app_rt_az2_name" {
  type    = string
  default = "nutritrack-prod-private-app-rt-az2"
}

variable "create_route53_alias_records" {
  type    = bool
  default = true
}

variable "create_acm_certificate" {
  type    = bool
  default = true
}

variable "existing_acm_certificate_arn" {
  type    = string
  default = ""
}

variable "create_https_listener" {
  type    = bool
  default = true
}

variable "existing_https_listener_arn" {
  type    = string
  default = ""
}

variable "create_https_path_rules" {
  type    = bool
  default = true
}

variable "alb_ssl_policy" {
  type    = string
  default = "ELBSecurityPolicy-TLS13-1-2-2021-06"
}

variable "enable_default_vpc_rds_peering" {
  type    = bool
  default = false
}

variable "existing_rds_sg_id" {
  type    = string
  default = ""
}

variable "existing_rds_instance_identifier" {
  type    = string
  default = ""
}

variable "default_vpc_route_table_ids" {
  type    = list(string)
  default = []
}
