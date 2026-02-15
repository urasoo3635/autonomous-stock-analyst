# =============================================================================
# prod 環境設定
# =============================================================================
# ECS Fargate ベースの本番環境。スケーラビリティと可用性を重視。

terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "autonomous-stock-analyst-tfstate"
    key            = "environments/prod/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "autonomous-stock-analyst-tflock"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "ap-northeast-1"
  profile = var.aws_profile

  default_tags {
    tags = {
      Project     = "stock-analyst"
      Environment = "prod"
      ManagedBy   = "terraform"
    }
  }
}

# --- 変数 ---

variable "aws_profile" {
  description = "AWS CLI プロファイル名"
  type        = string
  default     = "default"
}

variable "db_password" {
  description = "RDS マスターパスワード"
  type        = string
  sensitive   = true
}

variable "alarm_email" {
  description = "アラーム通知先メールアドレス"
  type        = string
}

variable "container_image" {
  description = "本番用コンテナイメージ URI"
  type        = string
}

variable "domain_name" {
  description = "ドメイン名（例: stock-analyst.example.com）"
  type        = string
}

# --- モジュール呼び出し ---

module "networking" {
  source = "../../modules/networking"

  project_name         = "stock-analyst"
  environment          = "prod"
  vpc_cidr             = "10.2.0.0/16"
  availability_zones   = ["ap-northeast-1a", "ap-northeast-1c"]
  public_subnet_cidrs  = ["10.2.1.0/24", "10.2.2.0/24"]
  private_subnet_cidrs = ["10.2.10.0/24", "10.2.20.0/24"]
  enable_nat_gateway   = true
}

module "compute" {
  source = "../../modules/compute"

  project_name       = "stock-analyst"
  environment        = "prod"
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  private_subnet_ids = module.networking.private_subnet_ids

  # ECS Fargate を使用（prod 環境）
  use_ec2 = false
  use_ecs = true

  ecs_task_cpu      = 512
  ecs_task_memory   = 1024
  ecs_desired_count = 1
  container_image   = var.container_image
  container_port    = 8000

  # HTTPS
  certificate_arn = module.dns.certificate_arn
}

module "database" {
  source = "../../modules/database"

  project_name          = "stock-analyst"
  environment           = "prod"
  vpc_id                = module.networking.vpc_id
  private_subnet_ids    = module.networking.private_subnet_ids
  app_security_group_id = module.compute.app_security_group_id

  db_instance_class        = "db.t3.medium"
  db_allocated_storage     = 50
  db_max_allocated_storage = 200
  db_name                  = "stock_analyst"
  db_username              = "dbadmin"
  db_password              = var.db_password
}

module "storage" {
  source = "../../modules/storage"

  project_name = "stock-analyst"
  environment  = "prod"
}

module "monitoring" {
  source = "../../modules/monitoring"

  project_name    = "stock-analyst"
  environment     = "prod"
  alarm_email     = var.alarm_email
  ec2_instance_id = ""
  rds_instance_id = "stock-analyst-prod-db"

  log_retention_days = 90
}

module "dns" {
  source = "../../modules/dns"

  project_name              = "stock-analyst"
  environment               = "prod"
  domain_name               = var.domain_name
  alb_dns_name              = module.compute.alb_dns_name
  alb_zone_id               = module.compute.alb_zone_id
  alb_arn                   = module.compute.alb_arn
  enable_global_accelerator = true
}

# --- 出力 ---

output "alb_dns_name" {
  value = module.compute.alb_dns_name
}

output "ecs_cluster_id" {
  value = module.compute.ecs_cluster_id
}

output "ecs_service_name" {
  value = module.compute.ecs_service_name
}

output "rds_endpoint" {
  value     = module.database.rds_endpoint
  sensitive = true
}



output "domain_name" {
  description = "ドメイン名"
  value       = module.dns.domain_name
}

output "name_servers" {
  description = "ネームサーバー（ドメインレジストラに設定が必要）"
  value       = module.dns.name_servers
}

output "static_ips" {
  description = "Global Accelerator の固定 IP アドレス"
  value       = module.dns.static_ips
}
