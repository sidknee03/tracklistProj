terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region"     { default = "us-east-1" }
variable "db_password"    { sensitive = true }
variable "db_username"    { default = "musicuser" }
variable "db_name"        { default = "musicdash" }
variable "ecr_image_uri"  { description = "Full ECR URI for the API image, e.g. 123456.dkr.ecr.us-east-1.amazonaws.com/music-api:latest" }

# ── VPC (default VPC for simplicity) ──────────────────────────────────────────
data "aws_vpc" "default"            { default = true }
data "aws_subnets" "default"        { filter { name = "vpc-id" values = [data.aws_vpc.default.id] } }

# ── Security groups ────────────────────────────────────────────────────────────
resource "aws_security_group" "rds" {
  name   = "music-rds-sg"
  vpc_id = data.aws_vpc.default.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # tighten in prod
  }
  egress { from_port = 0; to_port = 0; protocol = "-1"; cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_security_group" "ecs" {
  name   = "music-ecs-sg"
  vpc_id = data.aws_vpc.default.id

  ingress { from_port = 8000; to_port = 8000; protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] }
  egress  { from_port = 0;    to_port = 0;    protocol = "-1";  cidr_blocks = ["0.0.0.0/0"] }
}

# ── RDS PostgreSQL ─────────────────────────────────────────────────────────────
resource "aws_db_subnet_group" "main" {
  name       = "music-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids
}

resource "aws_db_instance" "postgres" {
  identifier           = "music-analytics-db"
  engine               = "postgres"
  engine_version       = "16"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  db_name              = var.db_name
  username             = var.db_username
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot  = true
  publicly_accessible  = true
}

# ── ECS Fargate ───────────────────────────────────────────────────────────────
resource "aws_ecs_cluster" "main" {
  name = "music-analytics-cluster"
}

resource "aws_iam_role" "ecs_task_exec" {
  name = "music-ecs-task-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Effect = "Allow"; Principal = { Service = "ecs-tasks.amazonaws.com" }; Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_exec" {
  role       = aws_iam_role.ecs_task_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "api" {
  family                   = "music-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_exec.arn

  container_definitions = jsonencode([{
    name  = "api"
    image = var.ecr_image_uri
    portMappings = [{ containerPort = 8000 }]
    environment = [
      { name = "DATABASE_URL", value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.address}:5432/${var.db_name}" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options   = { "awslogs-group" = "/ecs/music-api"; "awslogs-region" = var.aws_region; "awslogs-stream-prefix" = "ecs" }
    }
  }])
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/music-api"
  retention_in_days = 7
}

resource "aws_ecs_service" "api" {
  name            = "music-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }
}

# ── Outputs ───────────────────────────────────────────────────────────────────
output "rds_endpoint"    { value = aws_db_instance.postgres.address }
output "ecs_cluster"     { value = aws_ecs_cluster.main.name }
