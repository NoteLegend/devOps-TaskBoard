variable "aws_region" {
  type    = string
  default = "ap-south-1"
}
variable "aws_account_id" {
  type        = string
  description = "Explicit agreed account; prevents accidental cross-account apply"
  validation {
    condition     = can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "Supply a 12-digit AWS account ID."
  }
}
variable "cluster_name" {
  type    = string
  default = "taskboard-eks"
}
variable "kubernetes_version" {
  type    = string
  default = "1.35"
}
variable "github_repository" {
  type    = string
  default = "NoteLegend/devOps-TaskBoard"
}
variable "github_oidc_subject_prefix" {
  type        = string
  description = "Exact sub_claim_prefix returned by GitHub actions/oidc/customization/sub; includes immutable IDs when enabled."
  validation {
    condition     = startswith(var.github_oidc_subject_prefix, "repo:") && !strcontains(var.github_oidc_subject_prefix, "*") && !strcontains(var.github_oidc_subject_prefix, ":ref:")
    error_message = "Use the exact repo subject prefix from GitHub, without wildcards or the branch suffix."
  }
}
variable "create_github_oidc_provider" {
  type        = bool
  default     = true
  description = "Set false if the account already has GitHub's OIDC provider"
}
variable "operator_role_arn" {
  type        = string
  description = "Persistent IAM role/user ARN for the approved local operator (not STS session ARN)"
}
variable "public_access_cidrs" {
  type        = list(string)
  default     = ["0.0.0.0/0"]
  description = "API network access; AWS authentication and EKS authorization still required. GitHub hosted runners have dynamic IPs."
}

# AWS-recommended compatible builds queried in ap-south-1 on 2026-10-16.
variable "addon_versions" {
  type = map(string)
  default = {
    "vpc-cni"            = "v1.22.4-eksbuild.3"
    "kube-proxy"         = "v1.35.3-eksbuild.52"
    "coredns"            = "v1.13.2-eksbuild.51"
    "aws-ebs-csi-driver" = "v1.67.0-eksbuild.1"
    "metrics-server"     = "v0.9.0-eksbuild.13"
  }
}
variable "node_ami_release_version" {
  type    = string
  default = "1.35.8-20261012"
}

variable "worker_instance_type" {
  type        = string
  default     = "m7i-flex.large"
  description = "Free-plan eligible x86_64 workers, verified in Mumbai; usage consumes promotional credits."
}
