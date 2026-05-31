data "aws_vpc" "custom" {
  filter {
    name   = "tag:Name"
    values = [var.custom_vpc_name]
  }
}

data "aws_lb" "app" {
  name = var.alb_name
}

data "aws_lb_target_group" "frontend" {
  name = var.frontend_tg_name
}

data "aws_lb_target_group" "portfolio" {
  name = var.portfolio_tg_name
}

data "aws_lb_target_group" "market" {
  name = var.market_tg_name
}

data "aws_security_group" "backend" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.custom.id]
  }

  filter {
    name   = "group-name"
    values = [var.backend_sg_name]
  }
}

data "aws_route_table" "app_rt_az1" {
  vpc_id = data.aws_vpc.custom.id

  filter {
    name   = "tag:Name"
    values = [var.private_app_rt_az1_name]
  }
}

data "aws_route_table" "app_rt_az2" {
  vpc_id = data.aws_vpc.custom.id

  filter {
    name   = "tag:Name"
    values = [var.private_app_rt_az2_name]
  }
}

data "aws_route53_zone" "this" {
  count        = var.route53_zone_id == "" ? 1 : 0
  name         = "${var.domain_name}."
  private_zone = false
}

data "aws_vpc" "default" {
  count   = var.enable_default_vpc_rds_peering ? 1 : 0
  default = true
}

data "aws_db_instance" "existing" {
  count                  = var.enable_default_vpc_rds_peering && var.existing_rds_instance_identifier != "" ? 1 : 0
  db_instance_identifier = var.existing_rds_instance_identifier
}

locals {
  zone_id = var.route53_zone_id != "" ? var.route53_zone_id : data.aws_route53_zone.this[0].zone_id

  default_vpc_id          = var.enable_default_vpc_rds_peering ? data.aws_vpc.default[0].id : null
  default_vpc_cidr        = var.enable_default_vpc_rds_peering ? data.aws_vpc.default[0].cidr_block : null
  default_main_rt_id      = var.enable_default_vpc_rds_peering ? data.aws_vpc.default[0].main_route_table_id : null
  default_route_table_ids = var.enable_default_vpc_rds_peering ? toset(length(var.default_vpc_route_table_ids) > 0 ? var.default_vpc_route_table_ids : [local.default_main_rt_id]) : toset([])
  resolved_rds_sg_id      = var.enable_default_vpc_rds_peering ? (var.existing_rds_sg_id != "" ? var.existing_rds_sg_id : (var.existing_rds_instance_identifier != "" ? data.aws_db_instance.existing[0].vpc_security_groups[0] : "")) : ""
}

resource "aws_route53_record" "apex" {
  count           = var.create_route53_alias_records ? 1 : 0
  zone_id         = local.zone_id
  name            = var.domain_name
  type            = "A"
  allow_overwrite = true

  alias {
    name                   = data.aws_lb.app.dns_name
    zone_id                = data.aws_lb.app.zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www" {
  count           = var.create_route53_alias_records ? 1 : 0
  zone_id         = local.zone_id
  name            = "www.${var.domain_name}"
  type            = "A"
  allow_overwrite = true

  alias {
    name                   = data.aws_lb.app.dns_name
    zone_id                = data.aws_lb.app.zone_id
    evaluate_target_health = false
  }
}

resource "aws_acm_certificate" "app" {
  count             = var.create_acm_certificate ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"
  subject_alternative_names = [
    "www.${var.domain_name}",
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.name_prefix}-acm"
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = var.create_acm_certificate ? {
    for dvo in aws_acm_certificate.app[0].domain_validation_options :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = local.zone_id
}

resource "aws_acm_certificate_validation" "app" {
  count                   = var.create_acm_certificate ? 1 : 0
  certificate_arn         = aws_acm_certificate.app[0].arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}

resource "aws_lb_listener" "https" {
  count             = var.create_https_listener ? 1 : 0
  load_balancer_arn = data.aws_lb.app.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = var.alb_ssl_policy
  certificate_arn   = var.create_acm_certificate ? aws_acm_certificate_validation.app[0].certificate_arn : var.existing_acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = data.aws_lb_target_group.frontend.arn
  }
}

locals {
  https_listener_arn = var.create_https_listener ? aws_lb_listener.https[0].arn : var.existing_https_listener_arn
}

resource "aws_lb_listener_rule" "portfolio_auth" {
  count        = var.create_https_path_rules ? 1 : 0
  listener_arn = local.https_listener_arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = data.aws_lb_target_group.portfolio.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/auth*"]
    }
  }
}

resource "aws_lb_listener_rule" "portfolio_customers" {
  count        = var.create_https_path_rules ? 1 : 0
  listener_arn = local.https_listener_arn
  priority     = 11

  action {
    type             = "forward"
    target_group_arn = data.aws_lb_target_group.portfolio.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/customers*"]
    }
  }
}

resource "aws_lb_listener_rule" "portfolio_portfolios" {
  count        = var.create_https_path_rules ? 1 : 0
  listener_arn = local.https_listener_arn
  priority     = 12

  action {
    type             = "forward"
    target_group_arn = data.aws_lb_target_group.portfolio.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/portfolio*"]
    }
  }
}

resource "aws_lb_listener_rule" "portfolio_legacy" {
  count        = var.create_https_path_rules ? 1 : 0
  listener_arn = local.https_listener_arn
  priority     = 13

  action {
    type             = "forward"
    target_group_arn = data.aws_lb_target_group.portfolio.arn
  }

  condition {
    path_pattern {
      values = ["/api/portfolio*"]
    }
  }
}

resource "aws_lb_listener_rule" "market_v1" {
  count        = var.create_https_path_rules ? 1 : 0
  listener_arn = local.https_listener_arn
  priority     = 20

  action {
    type             = "forward"
    target_group_arn = data.aws_lb_target_group.market.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/market*"]
    }
  }
}

resource "aws_lb_listener_rule" "market_legacy" {
  count        = var.create_https_path_rules ? 1 : 0
  listener_arn = local.https_listener_arn
  priority     = 21

  action {
    type             = "forward"
    target_group_arn = data.aws_lb_target_group.market.arn
  }

  condition {
    path_pattern {
      values = ["/api/market*"]
    }
  }
}

resource "aws_vpc_peering_connection" "default_rds" {
  count       = var.enable_default_vpc_rds_peering ? 1 : 0
  vpc_id      = data.aws_vpc.custom.id
  peer_vpc_id = local.default_vpc_id
  auto_accept = true

  tags = {
    Name = "${var.name_prefix}-custom-to-default-rds-peer"
  }
}

resource "aws_vpc_peering_connection_options" "requester" {
  count                     = var.enable_default_vpc_rds_peering ? 1 : 0
  vpc_peering_connection_id = aws_vpc_peering_connection.default_rds[0].id

  requester {
    allow_remote_vpc_dns_resolution = true
  }

  accepter {
    allow_remote_vpc_dns_resolution = true
  }
}

resource "aws_route" "custom_to_default_az1" {
  count                     = var.enable_default_vpc_rds_peering ? 1 : 0
  route_table_id            = data.aws_route_table.app_rt_az1.id
  destination_cidr_block    = local.default_vpc_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.default_rds[0].id
}

resource "aws_route" "custom_to_default_az2" {
  count                     = var.enable_default_vpc_rds_peering ? 1 : 0
  route_table_id            = data.aws_route_table.app_rt_az2.id
  destination_cidr_block    = local.default_vpc_cidr
  vpc_peering_connection_id = aws_vpc_peering_connection.default_rds[0].id
}

resource "aws_route" "default_to_custom" {
  for_each                  = local.default_route_table_ids
  route_table_id            = each.value
  destination_cidr_block    = data.aws_vpc.custom.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.default_rds[0].id
}

resource "aws_vpc_security_group_ingress_rule" "rds_from_custom_vpc" {
  count             = var.enable_default_vpc_rds_peering && local.resolved_rds_sg_id != "" ? 1 : 0
  security_group_id = local.resolved_rds_sg_id
  from_port         = 5432
  to_port           = 5432
  ip_protocol       = "tcp"
  cidr_ipv4         = data.aws_vpc.custom.cidr_block
  description       = "PostgreSQL from custom VPC via peering"
}
