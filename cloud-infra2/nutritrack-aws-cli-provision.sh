#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

export AWS_PAGER=""

# ============================================================
# Variables
# ============================================================
REGION="${REGION:-us-east-1}"
AZ1="${AZ1:-us-east-1a}"
AZ2="${AZ2:-us-east-1b}"

PROJECT="${PROJECT:-NutriTrack}"
ENVIRONMENT="${ENVIRONMENT:-prod}"
MANAGED_BY="${MANAGED_BY:-aws-cli}"

NAME_PREFIX="${NAME_PREFIX:-nutritrack-prod}"
VPC_NAME="${VPC_NAME:-${NAME_PREFIX}-vpc}"
VPC_CIDR="${VPC_CIDR:-10.0.0.0/16}"

PUBLIC_SUBNET_AZ1_NAME="${PUBLIC_SUBNET_AZ1_NAME:-${NAME_PREFIX}-public-subnet-az1}"
PUBLIC_SUBNET_AZ1_CIDR="${PUBLIC_SUBNET_AZ1_CIDR:-10.0.1.0/24}"
PUBLIC_SUBNET_AZ2_NAME="${PUBLIC_SUBNET_AZ2_NAME:-${NAME_PREFIX}-public-subnet-az2}"
PUBLIC_SUBNET_AZ2_CIDR="${PUBLIC_SUBNET_AZ2_CIDR:-10.0.2.0/24}"

PRIVATE_APP_SUBNET_AZ1_NAME="${PRIVATE_APP_SUBNET_AZ1_NAME:-${NAME_PREFIX}-private-app-subnet-az1}"
PRIVATE_APP_SUBNET_AZ1_CIDR="${PRIVATE_APP_SUBNET_AZ1_CIDR:-10.0.11.0/24}"
PRIVATE_APP_SUBNET_AZ2_NAME="${PRIVATE_APP_SUBNET_AZ2_NAME:-${NAME_PREFIX}-private-app-subnet-az2}"
PRIVATE_APP_SUBNET_AZ2_CIDR="${PRIVATE_APP_SUBNET_AZ2_CIDR:-10.0.12.0/24}"

PRIVATE_DB_SUBNET_AZ1_NAME="${PRIVATE_DB_SUBNET_AZ1_NAME:-${NAME_PREFIX}-private-db-subnet-az1}"
PRIVATE_DB_SUBNET_AZ1_CIDR="${PRIVATE_DB_SUBNET_AZ1_CIDR:-10.0.21.0/24}"

IGW_NAME="${IGW_NAME:-${NAME_PREFIX}-igw}"
NATGW_AZ1_NAME="${NATGW_AZ1_NAME:-${NAME_PREFIX}-natgw-az1}"
NATGW_AZ2_NAME="${NATGW_AZ2_NAME:-${NAME_PREFIX}-natgw-az2}"
EIP_NAT_AZ1_NAME="${EIP_NAT_AZ1_NAME:-${NAME_PREFIX}-eip-nat-az1}"
EIP_NAT_AZ2_NAME="${EIP_NAT_AZ2_NAME:-${NAME_PREFIX}-eip-nat-az2}"

PUBLIC_RT_NAME="${PUBLIC_RT_NAME:-${NAME_PREFIX}-public-rt}"
PRIVATE_APP_RT_AZ1_NAME="${PRIVATE_APP_RT_AZ1_NAME:-${NAME_PREFIX}-private-app-rt-az1}"
PRIVATE_APP_RT_AZ2_NAME="${PRIVATE_APP_RT_AZ2_NAME:-${NAME_PREFIX}-private-app-rt-az2}"
PRIVATE_DB_RT_NAME="${PRIVATE_DB_RT_NAME:-${NAME_PREFIX}-private-db-rt}"

BASTION_SG_NAME="${BASTION_SG_NAME:-${NAME_PREFIX}-bastion-sg}"
ALB_SG_NAME="${ALB_SG_NAME:-${NAME_PREFIX}-alb-sg}"
FRONTEND_SG_NAME="${FRONTEND_SG_NAME:-${NAME_PREFIX}-frontend-sg}"
BACKEND_SG_NAME="${BACKEND_SG_NAME:-${NAME_PREFIX}-backend-sg}"
MYSQL_SG_NAME="${MYSQL_SG_NAME:-${NAME_PREFIX}-mysql-sg}"

ALB_NAME="${ALB_NAME:-${NAME_PREFIX}-alb}"
FRONTEND_TG_NAME="${FRONTEND_TG_NAME:-${NAME_PREFIX}-frontend-tg}"
PORTFOLIO_TG_NAME="${PORTFOLIO_TG_NAME:-${NAME_PREFIX}-portfolio-tg}"
MARKET_TG_NAME="${MARKET_TG_NAME:-${NAME_PREFIX}-market-tg}"

FRONTEND_INSTANCE_NAME="${FRONTEND_INSTANCE_NAME:-${NAME_PREFIX}-frontend}"
BACKEND_INSTANCE_NAME="${BACKEND_INSTANCE_NAME:-${NAME_PREFIX}-backend}"
MYSQL_INSTANCE_NAME="${MYSQL_INSTANCE_NAME:-${NAME_PREFIX}-mysql}"
BASTION_INSTANCE_NAME="${BASTION_INSTANCE_NAME:-${NAME_PREFIX}-bastion}"

FRONTEND_INSTANCE_TYPE="${FRONTEND_INSTANCE_TYPE:-t3.small}"
BACKEND_INSTANCE_TYPE="${BACKEND_INSTANCE_TYPE:-t3.medium}"
MYSQL_INSTANCE_TYPE="${MYSQL_INSTANCE_TYPE:-t3.medium}"
BASTION_INSTANCE_TYPE="${BASTION_INSTANCE_TYPE:-t3.micro}"

FRONTEND_VOLUME_GB="${FRONTEND_VOLUME_GB:-30}"
BACKEND_VOLUME_GB="${BACKEND_VOLUME_GB:-40}"
MYSQL_VOLUME_GB="${MYSQL_VOLUME_GB:-50}"
BASTION_VOLUME_GB="${BASTION_VOLUME_GB:-20}"

FRONTEND_AMI_ID="${FRONTEND_AMI_ID:-}"
BACKEND_AMI_ID="${BACKEND_AMI_ID:-}"
MYSQL_AMI_ID="${MYSQL_AMI_ID:-}"
BASTION_AMI_SSM_PARAM="${BASTION_AMI_SSM_PARAM:-/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64}"
MYSQL_AMI_SSM_PARAM="${MYSQL_AMI_SSM_PARAM:-/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64}"

EC2_KEY_PAIR_NAME="${EC2_KEY_PAIR_NAME:-${NAME_PREFIX}-keypair}"
SSH_PUBLIC_KEY_PATH="${SSH_PUBLIC_KEY_PATH:-$HOME/.ssh/${NAME_PREFIX}-keypair.pub}"
MY_IP_CIDR="${MY_IP_CIDR:-}"

ALB_HTTP_PORT="${ALB_HTTP_PORT:-80}"
FRONTEND_PORT="${FRONTEND_PORT:-80}"
PORTFOLIO_PORT="${PORTFOLIO_PORT:-8000}"
MARKET_PORT="${MARKET_PORT:-8001}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
SSH_PORT="${SSH_PORT:-22}"

COMMON_TAGS=(
  "Key=Project,Value=${PROJECT}"
  "Key=Environment,Value=${ENVIRONMENT}"
  "Key=ManagedBy,Value=${MANAGED_BY}"
)

# ============================================================
# Helpers
# ============================================================
log() {
  printf '\n[%s] %s\n' "$(date +'%Y-%m-%d %H:%M:%S')" "$*" >&2
}

fatal() {
  printf '\n[ERROR] %s\n' "$*" >&2
  exit 1
}

require_binary() {
  command -v "$1" >/dev/null 2>&1 || fatal "Required binary not found: $1"
}

is_none() {
  [[ -z "${1:-}" || "${1}" == "None" ]]
}

tag_ec2() {
  local resource_id="$1"
  local name_value="$2"
  shift 2
  aws ec2 create-tags \
    --region "$REGION" \
    --resources "$resource_id" \
    --tags "Key=Name,Value=${name_value}" "${COMMON_TAGS[@]}" "$@"
}

tag_elbv2() {
  local resource_arn="$1"
  local name_value="$2"
  shift 2
  aws elbv2 add-tags \
    --region "$REGION" \
    --resource-arns "$resource_arn" \
    --tags "Key=Name,Value=${name_value}" "${COMMON_TAGS[@]}" "$@"
}

safe_authorize_sg_rule() {
  local sg_id="$1"
  local description="$2"
  shift 2
  local tmp_err
  tmp_err="$(mktemp)"

  if aws ec2 authorize-security-group-ingress \
    --region "$REGION" \
    --group-id "$sg_id" \
    "$@" 2>"$tmp_err"; then
    log "Added SG rule: ${description}"
  else
    if grep -q "InvalidPermission.Duplicate" "$tmp_err"; then
      log "SG rule already present: ${description}"
    else
      cat "$tmp_err" >&2
      rm -f "$tmp_err"
      fatal "Failed to add SG rule: ${description}"
    fi
  fi

  rm -f "$tmp_err"
}

get_or_create_vpc() {
  log "Creating or reusing VPC"
  local vpc_id
  vpc_id="$(aws ec2 describe-vpcs \
    --region "$REGION" \
    --filters "Name=tag:Name,Values=${VPC_NAME}" "Name=cidr-block,Values=${VPC_CIDR}" \
    --query "Vpcs[0].VpcId" \
    --output text 2>/dev/null || true)"

  if is_none "$vpc_id"; then
    vpc_id="$(aws ec2 create-vpc \
      --region "$REGION" \
      --cidr-block "$VPC_CIDR" \
      --query "Vpc.VpcId" \
      --output text)"
    tag_ec2 "$vpc_id" "$VPC_NAME" "Key=ResourceType,Value=vpc"
    log "Created VPC: ${vpc_id}"
  else
    log "Reused VPC: ${vpc_id}"
  fi

  aws ec2 modify-vpc-attribute --region "$REGION" --vpc-id "$vpc_id" --enable-dns-support
  aws ec2 modify-vpc-attribute --region "$REGION" --vpc-id "$vpc_id" --enable-dns-hostnames
  printf '%s\n' "$vpc_id"
}

get_or_create_internet_gateway() {
  local vpc_id="$1"
  log "Creating or reusing Internet Gateway"
  local igw_id
  igw_id="$(aws ec2 describe-internet-gateways \
    --region "$REGION" \
    --filters "Name=tag:Name,Values=${IGW_NAME}" "Name=attachment.vpc-id,Values=${vpc_id}" \
    --query "InternetGateways[0].InternetGatewayId" \
    --output text 2>/dev/null || true)"

  if is_none "$igw_id"; then
    igw_id="$(aws ec2 create-internet-gateway \
      --region "$REGION" \
      --query "InternetGateway.InternetGatewayId" \
      --output text)"
    tag_ec2 "$igw_id" "$IGW_NAME" "Key=ResourceType,Value=internet-gateway"
    log "Created IGW: ${igw_id}"
  else
    log "Reused IGW: ${igw_id}"
  fi

  local attached_vpc
  attached_vpc="$(aws ec2 describe-internet-gateways \
    --region "$REGION" \
    --internet-gateway-ids "$igw_id" \
    --query "InternetGateways[0].Attachments[?VpcId=='${vpc_id}']|[0].VpcId" \
    --output text 2>/dev/null || true)"

  if is_none "$attached_vpc"; then
    log "Attaching IGW to VPC"
    aws ec2 attach-internet-gateway \
      --region "$REGION" \
      --internet-gateway-id "$igw_id" \
      --vpc-id "$vpc_id"
  fi

  printf '%s\n' "$igw_id"
}

create_or_reuse_subnet() {
  local vpc_id="$1"
  local subnet_name="$2"
  local subnet_cidr="$3"
  local subnet_az="$4"
  local map_public_ip="$5"
  shift 5
  local extra_tags=("$@")
  local subnet_id

  subnet_id="$(aws ec2 describe-subnets \
    --region "$REGION" \
    --filters "Name=vpc-id,Values=${vpc_id}" "Name=tag:Name,Values=${subnet_name}" "Name=cidr-block,Values=${subnet_cidr}" \
    --query "Subnets[0].SubnetId" \
    --output text 2>/dev/null || true)"

  if is_none "$subnet_id"; then
    subnet_id="$(aws ec2 create-subnet \
      --region "$REGION" \
      --vpc-id "$vpc_id" \
      --cidr-block "$subnet_cidr" \
      --availability-zone "$subnet_az" \
      --query "Subnet.SubnetId" \
      --output text)"
    tag_ec2 "$subnet_id" "$subnet_name" "Key=ResourceType,Value=subnet" "${extra_tags[@]}"
    log "Created subnet ${subnet_name}: ${subnet_id}"
  else
    log "Reused subnet ${subnet_name}: ${subnet_id}"
    tag_ec2 "$subnet_id" "$subnet_name" "Key=ResourceType,Value=subnet" "${extra_tags[@]}"
  fi

  if [[ "$map_public_ip" == "true" ]]; then
    aws ec2 modify-subnet-attribute \
      --region "$REGION" \
      --subnet-id "$subnet_id" \
      --map-public-ip-on-launch
  else
    aws ec2 modify-subnet-attribute \
      --region "$REGION" \
      --subnet-id "$subnet_id" \
      --no-map-public-ip-on-launch
  fi

  printf '%s\n' "$subnet_id"
}

ensure_eip() {
  local eip_name="$1"
  local allocation_id

  allocation_id="$(aws ec2 describe-addresses \
    --region "$REGION" \
    --filters "Name=tag:Name,Values=${eip_name}" \
    --query "Addresses[0].AllocationId" \
    --output text 2>/dev/null || true)"

  if is_none "$allocation_id"; then
    allocation_id="$(aws ec2 allocate-address \
      --region "$REGION" \
      --domain vpc \
      --query "AllocationId" \
      --output text)"
    tag_ec2 "$allocation_id" "$eip_name" "Key=ResourceType,Value=elastic-ip"
    log "Allocated EIP ${eip_name}: ${allocation_id}"
  else
    log "Reused EIP ${eip_name}: ${allocation_id}"
  fi

  printf '%s\n' "$allocation_id"
}

ensure_nat_gateway() {
  local nat_name="$1"
  local subnet_id="$2"
  local eip_name="$3"
  local nat_id

  nat_id="$(aws ec2 describe-nat-gateways \
    --region "$REGION" \
    --filter "Name=tag:Name,Values=${nat_name}" \
    --query "NatGateways[?State!='deleted']|[0].NatGatewayId" \
    --output text 2>/dev/null || true)"

  if is_none "$nat_id"; then
    local allocation_id
    allocation_id="$(ensure_eip "$eip_name")"
    nat_id="$(aws ec2 create-nat-gateway \
      --region "$REGION" \
      --subnet-id "$subnet_id" \
      --allocation-id "$allocation_id" \
      --query "NatGateway.NatGatewayId" \
      --output text)"
    tag_ec2 "$nat_id" "$nat_name" "Key=ResourceType,Value=nat-gateway"
    log "Created NAT Gateway ${nat_name}: ${nat_id}"
  else
    log "Reused NAT Gateway ${nat_name}: ${nat_id}"
  fi

  aws ec2 wait nat-gateway-available --region "$REGION" --nat-gateway-ids "$nat_id"
  printf '%s\n' "$nat_id"
}

create_or_reuse_route_table() {
  local vpc_id="$1"
  local rt_name="$2"
  local rt_id

  rt_id="$(aws ec2 describe-route-tables \
    --region "$REGION" \
    --filters "Name=vpc-id,Values=${vpc_id}" "Name=tag:Name,Values=${rt_name}" \
    --query "RouteTables[0].RouteTableId" \
    --output text 2>/dev/null || true)"

  if is_none "$rt_id"; then
    rt_id="$(aws ec2 create-route-table \
      --region "$REGION" \
      --vpc-id "$vpc_id" \
      --query "RouteTable.RouteTableId" \
      --output text)"
    tag_ec2 "$rt_id" "$rt_name" "Key=ResourceType,Value=route-table"
    log "Created route table ${rt_name}: ${rt_id}"
  else
    log "Reused route table ${rt_name}: ${rt_id}"
    tag_ec2 "$rt_id" "$rt_name" "Key=ResourceType,Value=route-table"
  fi

  printf '%s\n' "$rt_id"
}

ensure_route() {
  local route_table_id="$1"
  local destination_cidr="$2"
  local target_kind="$3"
  local target_id="$4"
  local current_target=""

  case "$target_kind" in
    gateway-id)
      current_target="$(aws ec2 describe-route-tables \
        --region "$REGION" \
        --route-table-ids "$route_table_id" \
        --query "RouteTables[0].Routes[?DestinationCidrBlock=='${destination_cidr}']|[0].GatewayId" \
        --output text 2>/dev/null || true)"
      ;;
    nat-gateway-id)
      current_target="$(aws ec2 describe-route-tables \
        --region "$REGION" \
        --route-table-ids "$route_table_id" \
        --query "RouteTables[0].Routes[?DestinationCidrBlock=='${destination_cidr}']|[0].NatGatewayId" \
        --output text 2>/dev/null || true)"
      ;;
    *)
      fatal "Unsupported target kind: ${target_kind}"
      ;;
  esac

  if [[ "$current_target" == "$target_id" ]]; then
    log "Route already correct on ${route_table_id}: ${destination_cidr} -> ${target_id}"
    return 0
  fi

  if is_none "$current_target"; then
    log "Creating route on ${route_table_id}: ${destination_cidr} -> ${target_id}"
    aws ec2 create-route \
      --region "$REGION" \
      --route-table-id "$route_table_id" \
      --destination-cidr-block "$destination_cidr" \
      --"${target_kind}" "$target_id" >/dev/null
  else
    log "Replacing route on ${route_table_id}: ${destination_cidr} -> ${target_id}"
    aws ec2 replace-route \
      --region "$REGION" \
      --route-table-id "$route_table_id" \
      --destination-cidr-block "$destination_cidr" \
      --"${target_kind}" "$target_id" >/dev/null
  fi
}

ensure_route_table_association() {
  local route_table_id="$1"
  local subnet_id="$2"
  local current_route_table_id=""
  local association_id=""

  current_route_table_id="$(aws ec2 describe-route-tables \
    --region "$REGION" \
    --filters "Name=association.subnet-id,Values=${subnet_id}" \
    --query "RouteTables[0].RouteTableId" \
    --output text 2>/dev/null || true)"

  if [[ "$current_route_table_id" == "$route_table_id" ]]; then
    log "Subnet ${subnet_id} already associated with ${route_table_id}"
    return 0
  fi

  association_id="$(aws ec2 describe-route-tables \
    --region "$REGION" \
    --filters "Name=association.subnet-id,Values=${subnet_id}" \
    --query "RouteTables[0].Associations[0].RouteTableAssociationId" \
    --output text 2>/dev/null || true)"

  if is_none "$association_id"; then
    log "Associating subnet ${subnet_id} with ${route_table_id}"
    aws ec2 associate-route-table \
      --region "$REGION" \
      --route-table-id "$route_table_id" \
      --subnet-id "$subnet_id" >/dev/null
  else
    log "Replacing route table association for subnet ${subnet_id} -> ${route_table_id}"
    aws ec2 replace-route-table-association \
      --region "$REGION" \
      --association-id "$association_id" \
      --route-table-id "$route_table_id" >/dev/null
  fi
}

create_or_reuse_sg() {
  local vpc_id="$1"
  local sg_name="$2"
  local sg_description="$3"
  local sg_id

  sg_id="$(aws ec2 describe-security-groups \
    --region "$REGION" \
    --filters "Name=vpc-id,Values=${vpc_id}" "Name=group-name,Values=${sg_name}" \
    --query "SecurityGroups[0].GroupId" \
    --output text 2>/dev/null || true)"

  if is_none "$sg_id"; then
    sg_id="$(aws ec2 create-security-group \
      --region "$REGION" \
      --group-name "$sg_name" \
      --description "$sg_description" \
      --vpc-id "$vpc_id" \
      --query "GroupId" \
      --output text)"
    tag_ec2 "$sg_id" "$sg_name" "Key=ResourceType,Value=security-group"
    log "Created SG ${sg_name}: ${sg_id}"
  else
    log "Reused SG ${sg_name}: ${sg_id}"
    tag_ec2 "$sg_id" "$sg_name" "Key=ResourceType,Value=security-group"
  fi

  printf '%s\n' "$sg_id"
}

ensure_key_pair() {
  local key_exists="false"
  local key_material_path="$SSH_PUBLIC_KEY_PATH"

  if aws ec2 describe-key-pairs \
    --region "$REGION" \
    --key-names "$EC2_KEY_PAIR_NAME" >/dev/null 2>&1; then
    key_exists="true"
    log "Key pair already exists in AWS: ${EC2_KEY_PAIR_NAME}"
  fi

  if [[ "$key_exists" == "true" ]]; then
    if [[ -f "$key_material_path" ]]; then
      log "Local key material already exists: ${key_material_path}"
    else
      log "WARNING: AWS key pair exists, but local key file is missing: ${key_material_path}"
      log "You will not be able to SSH with the private key unless you recover it from backup."
    fi
    return 0
  fi

  mkdir -p "$(dirname "$key_material_path")"

  if [[ -f "$key_material_path" ]]; then
    local first_line
    first_line="$(head -n 1 "$key_material_path" || true)"

    if [[ "$first_line" == ssh-* || "$first_line" == ecdsa-* || "$first_line" == sk-ssh-* ]]; then
      log "Importing existing public key material from: ${key_material_path}"
      aws ec2 import-key-pair \
        --region "$REGION" \
        --key-name "$EC2_KEY_PAIR_NAME" \
        --public-key-material "fileb://${key_material_path}" >/dev/null
      return 0
    fi

    if grep -q "BEGIN .*PRIVATE KEY" "$key_material_path"; then
      local derived_pub_key
      derived_pub_key="$(mktemp)"
      log "Deriving public key from existing private key: ${key_material_path}"
      ssh-keygen -y -f "$key_material_path" > "$derived_pub_key"
      aws ec2 import-key-pair \
        --region "$REGION" \
        --key-name "$EC2_KEY_PAIR_NAME" \
        --public-key-material "fileb://${derived_pub_key}" >/dev/null
      rm -f "$derived_pub_key"
      return 0
    fi

    fatal "Unsupported key file format at ${key_material_path}. Use a private key (.pem) or public key starting with ssh-"
  fi

  log "Creating new EC2 key pair and saving private key to: ${key_material_path}"
  aws ec2 create-key-pair \
    --region "$REGION" \
    --key-name "$EC2_KEY_PAIR_NAME" \
    --key-type rsa \
    --key-format pem \
    --query "KeyMaterial" \
    --output text > "$key_material_path"

  chmod 400 "$key_material_path"
  if command -v ssh-keygen >/dev/null 2>&1; then
    ssh-keygen -y -f "$key_material_path" > "${key_material_path}.pub" || true
  fi
  log "Created key pair: ${EC2_KEY_PAIR_NAME}"
}

resolve_ssm_ami() {
  local parameter_name="$1"
  aws ssm get-parameter \
    --region "$REGION" \
    --name "$parameter_name" \
    --query "Parameter.Value" \
    --output text
}

validate_ami() {
  local ami_id="$1"
  local ami_label="$2"
  aws ec2 describe-images \
    --region "$REGION" \
    --image-ids "$ami_id" \
    >/dev/null 2>&1 || fatal "Invalid ${ami_label} AMI ID: ${ami_id}"
}

launch_or_reuse_instance() {
  local instance_name="$1"
  local ami_id="$2"
  local instance_type="$3"
  local subnet_id="$4"
  local sg_id="$5"
  local key_name="$6"
  local volume_size="$7"
  local role="$8"
  local associate_public_ip="${9:-false}"
  local instance_id

  instance_id="$(aws ec2 describe-instances \
    --region "$REGION" \
    --filters "Name=tag:Name,Values=${instance_name}" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --query "Reservations[0].Instances[0].InstanceId" \
    --output text 2>/dev/null || true)"

  if is_none "$instance_id"; then
    local run_args=(
      aws ec2 run-instances
      --region "$REGION"
      --image-id "$ami_id"
      --instance-type "$instance_type"
      --subnet-id "$subnet_id"
      --security-group-ids "$sg_id"
      --key-name "$key_name"
      --block-device-mappings "DeviceName=/dev/xvda,Ebs={VolumeSize=${volume_size},VolumeType=gp3,DeleteOnTermination=true}"
      --tag-specifications
      "ResourceType=instance,Tags=[{Key=Name,Value=${instance_name}},{Key=Project,Value=${PROJECT}},{Key=Environment,Value=${ENVIRONMENT}},{Key=ManagedBy,Value=${MANAGED_BY}},{Key=Role,Value=${role}}]"
      "ResourceType=volume,Tags=[{Key=Name,Value=${instance_name}-root},{Key=Project,Value=${PROJECT}},{Key=Environment,Value=${ENVIRONMENT}},{Key=ManagedBy,Value=${MANAGED_BY}}]"
      --query "Instances[0].InstanceId"
      --output text
    )

    if [[ "$associate_public_ip" == "true" ]]; then
      run_args+=(--associate-public-ip-address)
    fi

    instance_id="$("${run_args[@]}")"
    log "Launched instance ${instance_name}: ${instance_id}"
  else
    log "Reused instance ${instance_name}: ${instance_id}"
    tag_ec2 "$instance_id" "$instance_name" "Key=Role,Value=${role}"
  fi

  local state
  state="$(aws ec2 describe-instances \
    --region "$REGION" \
    --instance-ids "$instance_id" \
    --query "Reservations[0].Instances[0].State.Name" \
    --output text)"

  if [[ "$state" == "stopped" ]]; then
    log "Starting instance ${instance_name}"
    aws ec2 start-instances --region "$REGION" --instance-ids "$instance_id" >/dev/null
  fi

  aws ec2 wait instance-running --region "$REGION" --instance-ids "$instance_id"
  aws ec2 wait instance-status-ok --region "$REGION" --instance-ids "$instance_id"

  local private_ip public_ip
  private_ip="$(aws ec2 describe-instances \
    --region "$REGION" \
    --instance-ids "$instance_id" \
    --query "Reservations[0].Instances[0].PrivateIpAddress" \
    --output text)"
  public_ip="$(aws ec2 describe-instances \
    --region "$REGION" \
    --instance-ids "$instance_id" \
    --query "Reservations[0].Instances[0].PublicIpAddress" \
    --output text 2>/dev/null || true)"

  printf '%s\t%s\t%s\n' "$instance_id" "$private_ip" "${public_ip:-None}"
}

ensure_target_group() {
  local tg_name="$1"
  local port="$2"
  local health_path="$3"
  local tg_id

  tg_id="$(aws elbv2 describe-target-groups \
    --region "$REGION" \
    --names "$tg_name" \
    --query "TargetGroups[0].TargetGroupArn" \
    --output text 2>/dev/null || true)"

  if is_none "$tg_id"; then
    tg_id="$(aws elbv2 create-target-group \
      --region "$REGION" \
      --name "$tg_name" \
      --protocol HTTP \
      --port "$port" \
      --target-type instance \
      --vpc-id "$VPC_ID" \
      --health-check-protocol HTTP \
      --health-check-path "$health_path" \
      --health-check-enabled \
      --matcher HttpCode=200-399 \
      --query "TargetGroups[0].TargetGroupArn" \
      --output text)"
    tag_elbv2 "$tg_id" "$tg_name" "Key=ResourceType,Value=target-group"
    log "Created target group ${tg_name}: ${tg_id}"
  else
    log "Reused target group ${tg_name}: ${tg_id}"
    tag_elbv2 "$tg_id" "$tg_name" "Key=ResourceType,Value=target-group"
  fi

  printf '%s\n' "$tg_id"
}

ensure_listener() {
  local alb_arn="$1"
  local default_tg_arn="$2"
  local listener_arn

  listener_arn="$(aws elbv2 describe-listeners \
    --region "$REGION" \
    --load-balancer-arn "$alb_arn" \
    --query "Listeners[?Port==\`${ALB_HTTP_PORT}\`]|[0].ListenerArn" \
    --output text 2>/dev/null || true)"

  if is_none "$listener_arn"; then
    listener_arn="$(aws elbv2 create-listener \
      --region "$REGION" \
      --load-balancer-arn "$alb_arn" \
      --protocol HTTP \
      --port "$ALB_HTTP_PORT" \
      --default-actions "Type=forward,TargetGroupArn=${default_tg_arn}" \
      --query "Listeners[0].ListenerArn" \
      --output text)"
    log "Created HTTP listener: ${listener_arn}"
  else
    log "Reused HTTP listener: ${listener_arn}"
    aws elbv2 modify-listener \
      --region "$REGION" \
      --listener-arn "$listener_arn" \
      --default-actions "Type=forward,TargetGroupArn=${default_tg_arn}" >/dev/null
  fi

  printf '%s\n' "$listener_arn"
}

ensure_listener_rule() {
  local listener_arn="$1"
  local priority="$2"
  local path_pattern="$3"
  local target_tg_arn="$4"
  local rule_arn

  rule_arn="$(aws elbv2 describe-rules \
    --region "$REGION" \
    --listener-arn "$listener_arn" \
    --query "Rules[?Priority=='${priority}']|[0].RuleArn" \
    --output text 2>/dev/null || true)"

  if is_none "$rule_arn"; then
    rule_arn="$(aws elbv2 create-rule \
      --region "$REGION" \
      --listener-arn "$listener_arn" \
      --priority "$priority" \
      --conditions "Field=path-pattern,Values=${path_pattern}" \
      --actions "Type=forward,TargetGroupArn=${target_tg_arn}" \
      --query "Rules[0].RuleArn" \
      --output text)"
    log "Created listener rule ${priority} for ${path_pattern}"
  else
    log "Listener rule already exists for priority ${priority}: ${rule_arn}"
  fi
}

register_target() {
  local target_group_arn="$1"
  local instance_id="$2"
  local port="$3"
  local label="$4"

  aws elbv2 register-targets \
    --region "$REGION" \
    --target-group-arn "$target_group_arn" \
    --targets "Id=${instance_id},Port=${port}" >/dev/null

  log "Registered ${label} target: ${instance_id}:${port}"
}

wait_for_target_healthy() {
  local target_group_arn="$1"
  local instance_id="$2"
  local port="$3"
  local label="$4"
  local attempt=1
  local max_attempts=40

  while (( attempt <= max_attempts )); do
    local state
    state="$(aws elbv2 describe-target-health \
      --region "$REGION" \
      --target-group-arn "$target_group_arn" \
      --targets "Id=${instance_id},Port=${port}" \
      --query "TargetHealthDescriptions[0].TargetHealth.State" \
      --output text 2>/dev/null || true)"

    if [[ "$state" == "healthy" ]]; then
      log "${label} target is healthy"
      return 0
    fi

    log "Waiting for ${label} target health (${state:-unknown}) [${attempt}/${max_attempts}]"
    sleep 15
    ((attempt++))
  done

  fatal "${label} target did not become healthy in time"
}

# ============================================================
# Pre-flight
# ============================================================
require_binary aws
require_binary ssh-keygen

if [[ -z "$MY_IP_CIDR" ]]; then
  fatal "Set MY_IP_CIDR to your public IP in CIDR form, for example 203.0.113.10/32"
fi

if [[ -z "$FRONTEND_AMI_ID" ]]; then
  fatal "Set FRONTEND_AMI_ID to the frontend AMI you want to launch"
fi

if [[ -z "$BACKEND_AMI_ID" ]]; then
  fatal "Set BACKEND_AMI_ID to the backend AMI you want to launch"
fi

log "Verifying AWS identity"
aws sts get-caller-identity --region "$REGION" >/dev/null

validate_ami "$FRONTEND_AMI_ID" "frontend"
validate_ami "$BACKEND_AMI_ID" "backend"

if [[ -z "$MYSQL_AMI_ID" ]]; then
  MYSQL_AMI_ID="$(resolve_ssm_ami "$MYSQL_AMI_SSM_PARAM")"
fi
validate_ami "$MYSQL_AMI_ID" "mysql"

BASTION_AMI_ID="$(resolve_ssm_ami "$BASTION_AMI_SSM_PARAM")"
validate_ami "$BASTION_AMI_ID" "bastion"

log "Using region ${REGION}"
log "Using availability zones ${AZ1} and ${AZ2}"

# ============================================================
# 1) Network
# ============================================================
VPC_ID="$(get_or_create_vpc)"
IGW_ID="$(get_or_create_internet_gateway "$VPC_ID")"

PUBLIC_SUBNET_AZ1_ID="$(create_or_reuse_subnet "$VPC_ID" "$PUBLIC_SUBNET_AZ1_NAME" "$PUBLIC_SUBNET_AZ1_CIDR" "$AZ1" true "Key=Tier,Value=public")"
PUBLIC_SUBNET_AZ2_ID="$(create_or_reuse_subnet "$VPC_ID" "$PUBLIC_SUBNET_AZ2_NAME" "$PUBLIC_SUBNET_AZ2_CIDR" "$AZ2" true "Key=Tier,Value=public")"
PRIVATE_APP_SUBNET_AZ1_ID="$(create_or_reuse_subnet "$VPC_ID" "$PRIVATE_APP_SUBNET_AZ1_NAME" "$PRIVATE_APP_SUBNET_AZ1_CIDR" "$AZ1" false "Key=Tier,Value=private-app")"
PRIVATE_APP_SUBNET_AZ2_ID="$(create_or_reuse_subnet "$VPC_ID" "$PRIVATE_APP_SUBNET_AZ2_NAME" "$PRIVATE_APP_SUBNET_AZ2_CIDR" "$AZ2" false "Key=Tier,Value=private-app")"
PRIVATE_DB_SUBNET_AZ1_ID="$(create_or_reuse_subnet "$VPC_ID" "$PRIVATE_DB_SUBNET_AZ1_NAME" "$PRIVATE_DB_SUBNET_AZ1_CIDR" "$AZ1" false "Key=Tier,Value=private-db")"

NATGW_AZ1_ID="$(ensure_nat_gateway "$NATGW_AZ1_NAME" "$PUBLIC_SUBNET_AZ1_ID" "$EIP_NAT_AZ1_NAME")"
NATGW_AZ2_ID="$(ensure_nat_gateway "$NATGW_AZ2_NAME" "$PUBLIC_SUBNET_AZ2_ID" "$EIP_NAT_AZ2_NAME")"

PUBLIC_RT_ID="$(create_or_reuse_route_table "$VPC_ID" "$PUBLIC_RT_NAME")"
PRIVATE_APP_RT_AZ1_ID="$(create_or_reuse_route_table "$VPC_ID" "$PRIVATE_APP_RT_AZ1_NAME")"
PRIVATE_APP_RT_AZ2_ID="$(create_or_reuse_route_table "$VPC_ID" "$PRIVATE_APP_RT_AZ2_NAME")"
PRIVATE_DB_RT_ID="$(create_or_reuse_route_table "$VPC_ID" "$PRIVATE_DB_RT_NAME")"

ensure_route "$PUBLIC_RT_ID" "0.0.0.0/0" "gateway-id" "$IGW_ID"
ensure_route "$PRIVATE_APP_RT_AZ1_ID" "0.0.0.0/0" "nat-gateway-id" "$NATGW_AZ1_ID"
ensure_route "$PRIVATE_APP_RT_AZ2_ID" "0.0.0.0/0" "nat-gateway-id" "$NATGW_AZ2_ID"
ensure_route "$PRIVATE_DB_RT_ID" "0.0.0.0/0" "nat-gateway-id" "$NATGW_AZ1_ID"

ensure_route_table_association "$PUBLIC_RT_ID" "$PUBLIC_SUBNET_AZ1_ID"
ensure_route_table_association "$PUBLIC_RT_ID" "$PUBLIC_SUBNET_AZ2_ID"
ensure_route_table_association "$PRIVATE_APP_RT_AZ1_ID" "$PRIVATE_APP_SUBNET_AZ1_ID"
ensure_route_table_association "$PRIVATE_APP_RT_AZ2_ID" "$PRIVATE_APP_SUBNET_AZ2_ID"
ensure_route_table_association "$PRIVATE_DB_RT_ID" "$PRIVATE_DB_SUBNET_AZ1_ID"

# ============================================================
# 2) Security Groups
# ============================================================
BASTION_SG_ID="$(create_or_reuse_sg "$VPC_ID" "$BASTION_SG_NAME" "NutriTrack bastion security group")"
ALB_SG_ID="$(create_or_reuse_sg "$VPC_ID" "$ALB_SG_NAME" "NutriTrack ALB security group")"
FRONTEND_SG_ID="$(create_or_reuse_sg "$VPC_ID" "$FRONTEND_SG_NAME" "NutriTrack frontend security group")"
BACKEND_SG_ID="$(create_or_reuse_sg "$VPC_ID" "$BACKEND_SG_NAME" "NutriTrack backend security group")"
MYSQL_SG_ID="$(create_or_reuse_sg "$VPC_ID" "$MYSQL_SG_NAME" "NutriTrack MySQL security group")"

safe_authorize_sg_rule \
  "$BASTION_SG_ID" \
  "SSH from personal IP" \
  --protocol tcp \
  --port "$SSH_PORT" \
  --cidr "$MY_IP_CIDR"

safe_authorize_sg_rule \
  "$ALB_SG_ID" \
  "HTTP from internet" \
  --protocol tcp \
  --port "$ALB_HTTP_PORT" \
  --cidr 0.0.0.0/0

safe_authorize_sg_rule \
  "$FRONTEND_SG_ID" \
  "HTTP from ALB" \
  --ip-permissions "IpProtocol=tcp,FromPort=${FRONTEND_PORT},ToPort=${FRONTEND_PORT},UserIdGroupPairs=[{GroupId=${ALB_SG_ID}}]"

safe_authorize_sg_rule \
  "$FRONTEND_SG_ID" \
  "SSH from bastion" \
  --ip-permissions "IpProtocol=tcp,FromPort=${SSH_PORT},ToPort=${SSH_PORT},UserIdGroupPairs=[{GroupId=${BASTION_SG_ID}}]"

safe_authorize_sg_rule \
  "$BACKEND_SG_ID" \
  "Portfolio service from ALB" \
  --ip-permissions "IpProtocol=tcp,FromPort=${PORTFOLIO_PORT},ToPort=${PORTFOLIO_PORT},UserIdGroupPairs=[{GroupId=${ALB_SG_ID}}]"

safe_authorize_sg_rule \
  "$BACKEND_SG_ID" \
  "Market service from ALB" \
  --ip-permissions "IpProtocol=tcp,FromPort=${MARKET_PORT},ToPort=${MARKET_PORT},UserIdGroupPairs=[{GroupId=${ALB_SG_ID}}]"

safe_authorize_sg_rule \
  "$BACKEND_SG_ID" \
  "SSH from bastion" \
  --ip-permissions "IpProtocol=tcp,FromPort=${SSH_PORT},ToPort=${SSH_PORT},UserIdGroupPairs=[{GroupId=${BASTION_SG_ID}}]"

safe_authorize_sg_rule \
  "$MYSQL_SG_ID" \
  "MySQL from backend" \
  --ip-permissions "IpProtocol=tcp,FromPort=${MYSQL_PORT},ToPort=${MYSQL_PORT},UserIdGroupPairs=[{GroupId=${BACKEND_SG_ID}}]"

safe_authorize_sg_rule \
  "$MYSQL_SG_ID" \
  "SSH from bastion" \
  --ip-permissions "IpProtocol=tcp,FromPort=${SSH_PORT},ToPort=${SSH_PORT},UserIdGroupPairs=[{GroupId=${BASTION_SG_ID}}]"

# ============================================================
# 3) Key Pair
# ============================================================
ensure_key_pair

# ============================================================
# 4) Load Balancer
# ============================================================
log "Creating or reusing Application Load Balancer"
ALB_ARN="$(aws elbv2 describe-load-balancers \
  --region "$REGION" \
  --names "$ALB_NAME" \
  --query "LoadBalancers[0].LoadBalancerArn" \
  --output text 2>/dev/null || true)"

if is_none "$ALB_ARN"; then
  ALB_ARN="$(aws elbv2 create-load-balancer \
    --region "$REGION" \
    --name "$ALB_NAME" \
    --subnets "$PUBLIC_SUBNET_AZ1_ID" "$PUBLIC_SUBNET_AZ2_ID" \
    --security-groups "$ALB_SG_ID" \
    --scheme internet-facing \
    --type application \
    --ip-address-type ipv4 \
    --query "LoadBalancers[0].LoadBalancerArn" \
    --output text)"
  tag_elbv2 "$ALB_ARN" "$ALB_NAME" "Key=ResourceType,Value=application-load-balancer"
  log "Created ALB: ${ALB_ARN}"
else
  log "Reused ALB: ${ALB_ARN}"
fi

aws elbv2 wait load-balancer-available --region "$REGION" --load-balancer-arns "$ALB_ARN"
ALB_DNS_NAME="$(aws elbv2 describe-load-balancers \
  --region "$REGION" \
  --load-balancer-arns "$ALB_ARN" \
  --query "LoadBalancers[0].DNSName" \
  --output text)"

FRONTEND_TG_ARN="$(ensure_target_group "$FRONTEND_TG_NAME" "$FRONTEND_PORT" "/health")"
PORTFOLIO_TG_ARN="$(ensure_target_group "$PORTFOLIO_TG_NAME" "$PORTFOLIO_PORT" "/health")"
MARKET_TG_ARN="$(ensure_target_group "$MARKET_TG_NAME" "$MARKET_PORT" "/health")"

LISTENER_ARN="$(ensure_listener "$ALB_ARN" "$FRONTEND_TG_ARN")"

ensure_listener_rule "$LISTENER_ARN" 10 "/api/v1/auth*" "$PORTFOLIO_TG_ARN"
ensure_listener_rule "$LISTENER_ARN" 11 "/api/v1/customers*" "$PORTFOLIO_TG_ARN"
ensure_listener_rule "$LISTENER_ARN" 12 "/api/v1/portfolio*" "$PORTFOLIO_TG_ARN"
ensure_listener_rule "$LISTENER_ARN" 13 "/api/portfolio*" "$PORTFOLIO_TG_ARN"
ensure_listener_rule "$LISTENER_ARN" 20 "/api/v1/market*" "$MARKET_TG_ARN"
ensure_listener_rule "$LISTENER_ARN" 21 "/api/market*" "$MARKET_TG_ARN"

# ============================================================
# 5) Compute Instances
# ============================================================
log "Launching or reusing bastion, frontend, backend, and MySQL instances"

read -r BASTION_INSTANCE_ID BASTION_PRIVATE_IP BASTION_PUBLIC_IP <<<"$(launch_or_reuse_instance \
  "$BASTION_INSTANCE_NAME" \
  "$BASTION_AMI_ID" \
  "$BASTION_INSTANCE_TYPE" \
  "$PUBLIC_SUBNET_AZ1_ID" \
  "$BASTION_SG_ID" \
  "$EC2_KEY_PAIR_NAME" \
  "$BASTION_VOLUME_GB" \
  "Bastion" \
  true)"

read -r FRONTEND_INSTANCE_ID FRONTEND_PRIVATE_IP FRONTEND_PUBLIC_IP <<<"$(launch_or_reuse_instance \
  "$FRONTEND_INSTANCE_NAME" \
  "$FRONTEND_AMI_ID" \
  "$FRONTEND_INSTANCE_TYPE" \
  "$PRIVATE_APP_SUBNET_AZ1_ID" \
  "$FRONTEND_SG_ID" \
  "$EC2_KEY_PAIR_NAME" \
  "$FRONTEND_VOLUME_GB" \
  "Frontend" \
  false)"

read -r BACKEND_INSTANCE_ID BACKEND_PRIVATE_IP BACKEND_PUBLIC_IP <<<"$(launch_or_reuse_instance \
  "$BACKEND_INSTANCE_NAME" \
  "$BACKEND_AMI_ID" \
  "$BACKEND_INSTANCE_TYPE" \
  "$PRIVATE_APP_SUBNET_AZ2_ID" \
  "$BACKEND_SG_ID" \
  "$EC2_KEY_PAIR_NAME" \
  "$BACKEND_VOLUME_GB" \
  "Backend" \
  false)"

read -r MYSQL_INSTANCE_ID MYSQL_PRIVATE_IP MYSQL_PUBLIC_IP <<<"$(launch_or_reuse_instance \
  "$MYSQL_INSTANCE_NAME" \
  "$MYSQL_AMI_ID" \
  "$MYSQL_INSTANCE_TYPE" \
  "$PRIVATE_DB_SUBNET_AZ1_ID" \
  "$MYSQL_SG_ID" \
  "$EC2_KEY_PAIR_NAME" \
  "$MYSQL_VOLUME_GB" \
  "MySQL" \
  false)"

log "Registering instances with target groups"
register_target "$FRONTEND_TG_ARN" "$FRONTEND_INSTANCE_ID" "$FRONTEND_PORT" "frontend"
register_target "$PORTFOLIO_TG_ARN" "$BACKEND_INSTANCE_ID" "$PORTFOLIO_PORT" "portfolio"
register_target "$MARKET_TG_ARN" "$BACKEND_INSTANCE_ID" "$MARKET_PORT" "market"

wait_for_target_healthy "$FRONTEND_TG_ARN" "$FRONTEND_INSTANCE_ID" "$FRONTEND_PORT" "frontend"
wait_for_target_healthy "$PORTFOLIO_TG_ARN" "$BACKEND_INSTANCE_ID" "$PORTFOLIO_PORT" "portfolio"
wait_for_target_healthy "$MARKET_TG_ARN" "$BACKEND_INSTANCE_ID" "$MARKET_PORT" "market"

# ============================================================
# Summary
# ============================================================
cat <<EOF
VPC_ID=${VPC_ID}
IGW_ID=${IGW_ID}
ALB_ARN=${ALB_ARN}
ALB_DNS_NAME=${ALB_DNS_NAME}
PUBLIC_SUBNET_AZ1_ID=${PUBLIC_SUBNET_AZ1_ID}
PUBLIC_SUBNET_AZ2_ID=${PUBLIC_SUBNET_AZ2_ID}
PRIVATE_APP_SUBNET_AZ1_ID=${PRIVATE_APP_SUBNET_AZ1_ID}
PRIVATE_APP_SUBNET_AZ2_ID=${PRIVATE_APP_SUBNET_AZ2_ID}
PRIVATE_DB_SUBNET_AZ1_ID=${PRIVATE_DB_SUBNET_AZ1_ID}
NATGW_AZ1_ID=${NATGW_AZ1_ID}
NATGW_AZ2_ID=${NATGW_AZ2_ID}
PUBLIC_RT_ID=${PUBLIC_RT_ID}
PRIVATE_APP_RT_AZ1_ID=${PRIVATE_APP_RT_AZ1_ID}
PRIVATE_APP_RT_AZ2_ID=${PRIVATE_APP_RT_AZ2_ID}
PRIVATE_DB_RT_ID=${PRIVATE_DB_RT_ID}
BASTION_SG_ID=${BASTION_SG_ID}
ALB_SG_ID=${ALB_SG_ID}
FRONTEND_SG_ID=${FRONTEND_SG_ID}
BACKEND_SG_ID=${BACKEND_SG_ID}
MYSQL_SG_ID=${MYSQL_SG_ID}
FRONTEND_TG_ARN=${FRONTEND_TG_ARN}
PORTFOLIO_TG_ARN=${PORTFOLIO_TG_ARN}
MARKET_TG_ARN=${MARKET_TG_ARN}
BASTION_INSTANCE_ID=${BASTION_INSTANCE_ID}
BASTION_PRIVATE_IP=${BASTION_PRIVATE_IP}
BASTION_PUBLIC_IP=${BASTION_PUBLIC_IP}
FRONTEND_INSTANCE_ID=${FRONTEND_INSTANCE_ID}
FRONTEND_PRIVATE_IP=${FRONTEND_PRIVATE_IP}
BACKEND_INSTANCE_ID=${BACKEND_INSTANCE_ID}
BACKEND_PRIVATE_IP=${BACKEND_PRIVATE_IP}
MYSQL_INSTANCE_ID=${MYSQL_INSTANCE_ID}
MYSQL_PRIVATE_IP=${MYSQL_PRIVATE_IP}
EOF
