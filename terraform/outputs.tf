output "cluster_name" { value = module.eks.cluster_name }
output "cluster_endpoint" { value = module.eks.cluster_endpoint }
output "vpc_id" { value = module.vpc.vpc_id }
output "aws_region" { value = var.aws_region }
output "alb_role_arn" { value = aws_iam_role.irsa["alb"].arn }
output "deployment_role_arn" { value = aws_iam_role.github_deploy.arn }
