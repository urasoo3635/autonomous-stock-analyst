# =============================================================================
# GitHub Actions 用 IAM OIDC設定
# キーレス認証でセキュリティを向上させる
#
# 使い方:
#   cd infra/environments/prod
#   terraform apply -target=module.iam
#
# GitHub Secrets に以下を設定:
#   - AWS_ROLE_ARN : このファイルで作成するロールの ARN
# =============================================================================

variable "github_org" {
  description = "GitHub 組織名（個人リポジトリの場合はユーザー名）"
  type        = string
}

variable "github_repo" {
  description = "GitHub リポジトリ名"
  type        = string
  default     = "autonomous-stock-analyst"
}

# GitHub OIDC プロバイダー（アカウントに1つだけ作成）
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = ["sts.amazonaws.com"]

  # GitHub Actions の OIDC サムプリント（2023年以降は AWS が自動検証）
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = {
    Name = "github-actions-oidc"
  }
}

# GitHub Actions 用 IAM ロール
resource "aws_iam_role" "github_actions" {
  name = "${var.project_name}-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            # main ブランチへの push のみ許可
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main"
          }
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-github-actions-role"
  }
}

# ECR へのイメージ push 権限
resource "aws_iam_role_policy" "github_actions_ecr" {
  name = "${var.project_name}-github-actions-ecr"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ECRGetAuthorizationToken"
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = ["*"]
      },
      {
        Sid    = "ECRPushPull"
        Effect = "Allow"
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
        ]
        Resource = [
          "arn:aws:ecr:*:*:repository/${var.project_name}-*"
        ]
      }
    ]
  })
}

# ECS へのデプロイ権限（最小権限）
resource "aws_iam_role_policy" "github_actions_ecs" {
  name = "${var.project_name}-github-actions-ecs"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECSDeployAccess"
        Effect = "Allow"
        Action = [
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition",
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeClusters",
        ]
        Resource = ["*"]
      },
      {
        Sid    = "PassRoleForECS"
        Effect = "Allow"
        Action = ["iam:PassRole"]
        Resource = [
          "arn:aws:iam::*:role/${var.project_name}-*-ecs-*"
        ]
      }
    ]
  })
}

output "github_actions_role_arn" {
  description = "GitHub Actions 用 IAM ロール ARN（GitHub Secrets: AWS_ROLE_ARN に設定）"
  value       = aws_iam_role.github_actions.arn
}
