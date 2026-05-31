output "custom_vpc_id" {
  value = data.aws_vpc.custom.id
}

output "alb_dns_name" {
  value = data.aws_lb.app.dns_name
}

output "route53_zone_id" {
  value = local.zone_id
}

output "https_listener_arn" {
  value = local.https_listener_arn
}

output "certificate_arn" {
  value = var.create_acm_certificate ? aws_acm_certificate_validation.app[0].certificate_arn : var.existing_acm_certificate_arn
}

output "vpc_peering_id" {
  value = var.enable_default_vpc_rds_peering ? aws_vpc_peering_connection.default_rds[0].id : null
}
