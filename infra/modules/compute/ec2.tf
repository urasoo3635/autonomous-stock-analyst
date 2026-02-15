# =============================================================================
# EC2 インスタンス（dev / staging 環境用）
# =============================================================================

# 最新の Amazon Linux 2023 AMI を取得
data "aws_ami" "amazon_linux" {
  count       = var.use_ec2 ? 1 : 0
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# SSH アクセス用セキュリティグループ
resource "aws_security_group" "ec2_ssh" {
  count = var.use_ec2 ? 1 : 0

  name        = "${var.project_name}-${var.environment}-ec2-ssh-sg"
  description = "SSH access for EC2"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidrs
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2-ssh-sg"
  }
}

# EC2 用 IAM ロール
resource "aws_iam_role" "ec2" {
  count = var.use_ec2 ? 1 : 0
  name  = "${var.project_name}-${var.environment}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2-role"
  }
}

resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  count      = var.use_ec2 ? 1 : 0
  role       = aws_iam_role.ec2[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ec2_ecr" {
  count      = var.use_ec2 ? 1 : 0
  role       = aws_iam_role.ec2[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "ec2" {
  count = var.use_ec2 ? 1 : 0
  name  = "${var.project_name}-${var.environment}-ec2-profile"
  role  = aws_iam_role.ec2[0].name
}

# EC2 インスタンス
resource "aws_instance" "app" {
  count = var.use_ec2 ? 1 : 0

  ami                    = data.aws_ami.amazon_linux[0].id
  instance_type          = var.ec2_instance_type
  key_name               = var.ec2_key_name != "" ? var.ec2_key_name : null
  subnet_id              = var.public_subnet_ids[0]
  iam_instance_profile   = aws_iam_instance_profile.ec2[0].name
  vpc_security_group_ids = [aws_security_group.app.id, aws_security_group.ec2_ssh[0].id]

  user_data = base64encode(<<-EOF
    #!/bin/bash
    # Docker インストール
    dnf update -y
    dnf install -y docker
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ec2-user

    # Docker Compose インストール
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
  EOF
  )

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-app"
  }
}

# ALB ターゲットグループへの登録
resource "aws_lb_target_group_attachment" "ec2" {
  count = var.use_ec2 ? 1 : 0

  target_group_arn = aws_lb_target_group.app.arn
  target_id        = aws_instance.app[0].id
  port             = var.container_port
}
