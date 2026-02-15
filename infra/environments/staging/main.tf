# =============================================================================
# staging 環境設定
# =============================================================================
# EC2 ベースの検証環境。本番相当の動作確認を行う。

terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "autonomous-stock-analyst-tfstate"
    key            = "environments/staging/terraform.tfstate"
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
      Environment = "staging"
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
  default     = ""
}

# --- モジュール呼び出し ---

module "networking" {
  source = "../../modules/networking"

  project_name         = "stock-analyst"
  environment          = "staging"
  vpc_cidr             = "10.1.0.0/16"
  availability_zones   = ["ap-northeast-1a", "ap-northeast-1c"]
  public_subnet_cidrs  = ["10.1.1.0/24", "10.1.2.0/24"]
  private_subnet_cidrs = ["10.1.10.0/24", "10.1.20.0/24"]
  enable_nat_gateway   = true
}

module "compute" {
  source = "../../modules/compute"

  project_name       = "stock-analyst"
  environment        = "staging"
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  private_subnet_ids = module.networking.private_subnet_ids

  # EC2 を使用（staging 環境）
  use_ec2           = true
  ec2_instance_type = "t3.small"
  use_ecs           = false

  container_port = 8000
}

module "database" {
  source = "../../modules/database"

  project_name          = "stock-analyst"
  environment           = "staging"
  vpc_id                = module.networking.vpc_id
  private_subnet_ids    = module.networking.private_subnet_ids
  app_security_group_id = module.compute.app_security_group_id

  db_instance_class    = "db.t3.small"
  db_allocated_storage = 30
  db_name              = "stock_analyst"
  db_username          = "dbadmin"
  db_password          = var.db_password
}

module "storage" {
  source = "../../modules/storage"

  project_name = "stock-analyst"
  environment  = "staging"
}

module "monitoring" {
  source = "../../modules/monitoring"

  project_name    = "stock-analyst"
  environment     = "staging"
  alarm_email     = var.alarm_email
  ec2_instance_id = module.compute.ec2_instance_id != null ? module.compute.ec2_instance_id : ""
  rds_instance_id = "stock-analyst-staging-db"

  log_retention_days = 14
}

# --- 出力 ---

output "alb_dns_name" {
  value = module.compute.alb_dns_name
}

output "ec2_public_ip" {
  value = module.compute.ec2_public_ip
}

output "rds_endpoint" {
  value     = module.database.rds_endpoint
  sensitive = true
}
