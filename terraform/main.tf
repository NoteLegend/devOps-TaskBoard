data "aws_availability_zones" "available" {
  state = "available"
}
module "vpc" {
  source               = "terraform-aws-modules/vpc/aws"
  version              = "6.2.0"
  name                 = "${var.cluster_name}-vpc"
  cidr                 = "10.20.0.0/16"
  azs                  = slice(data.aws_availability_zones.available.names, 0, 2)
  private_subnets      = ["10.20.1.0/24", "10.20.2.0/24"]
  public_subnets       = ["10.20.101.0/24", "10.20.102.0/24"]
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true
  public_subnet_tags   = { "kubernetes.io/role/elb" = "1" }
  private_subnet_tags  = { "kubernetes.io/role/internal-elb" = "1" }
}
module "eks" {
  source                                   = "terraform-aws-modules/eks/aws"
  version                                  = "21.26.0"
  name                                     = var.cluster_name
  kubernetes_version                       = var.kubernetes_version
  upgrade_policy                           = { support_type = "STANDARD" }
  vpc_id                                   = module.vpc.vpc_id
  subnet_ids                               = module.vpc.private_subnets
  endpoint_public_access                   = true
  endpoint_private_access                  = true
  endpoint_public_access_cidrs             = var.public_access_cidrs
  enable_irsa                              = true
  authentication_mode                      = "API"
  enable_cluster_creator_admin_permissions = false
  access_entries = {
    operator = {
      principal_arn = var.operator_role_arn
      policy_associations = {
        admin = {
          policy_arn   = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = { type = "cluster" }
        }
      }
    }
    deployment = {
      principal_arn     = aws_iam_role.github_deploy.arn
      kubernetes_groups = ["taskboard-deployers"]
    }
  }
  addons = {
    vpc-cni            = { addon_version = var.addon_versions["vpc-cni"], before_compute = true }
    kube-proxy         = { addon_version = var.addon_versions["kube-proxy"], }
    coredns            = { addon_version = var.addon_versions["coredns"], }
    aws-ebs-csi-driver = { addon_version = var.addon_versions["aws-ebs-csi-driver"], service_account_role_arn = aws_iam_role.irsa["ebs"].arn }
    metrics-server     = { addon_version = var.addon_versions["metrics-server"], }
  }
  eks_managed_node_groups = {
    main = {
      instance_types                 = ["t3.medium"]
      ami_type                       = "AL2023_x86_64_STANDARD"
      use_latest_ami_release_version = false
      ami_release_version            = var.node_ami_release_version
      min_size                       = 2
      max_size                       = 2
      desired_size                   = 2
      block_device_mappings = {
        root = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 20
            volume_type           = "gp3"
            encrypted             = true
            delete_on_termination = true
          }
        }
      }
    }
  }
  cloudwatch_log_group_retention_in_days = 7
}
locals {
  oidc_host = replace(module.eks.cluster_oidc_issuer_url, "https://", "")
  service_accounts = {
    ebs = "system:serviceaccount:kube-system:ebs-csi-controller-sa"
    alb = "system:serviceaccount:kube-system:aws-load-balancer-controller"
  }
}
resource "aws_iam_role" "irsa" {
  for_each = local.service_accounts
  name     = "${var.cluster_name}-${each.key}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = module.eks.oidc_provider_arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = { StringEquals = {
        "${local.oidc_host}:sub" = each.value
        "${local.oidc_host}:aud" = "sts.amazonaws.com"
      } }
    }]
  })
}
resource "aws_iam_role_policy_attachment" "ebs" {
  role       = aws_iam_role.irsa["ebs"].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}
resource "aws_iam_policy" "alb" {
  name   = "${var.cluster_name}-alb"
  policy = file("${path.module}/lbc-iam-policy.json")
}
resource "aws_iam_role_policy_attachment" "alb" {
  role       = aws_iam_role.irsa["alb"].name
  policy_arn = aws_iam_policy.alb.arn
}
