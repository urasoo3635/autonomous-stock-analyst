# Terraform リモートステート設定
# 注意: 初回は backend ブロックをコメントアウトして `terraform init` し、
# S3 バケットと DynamoDB テーブルを作成した後に有効化すること。

terraform {
  backend "s3" {
    bucket         = "autonomous-stock-analyst-tfstate"
    key            = "terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "autonomous-stock-analyst-tflock"
    encrypt        = true
  }
}
