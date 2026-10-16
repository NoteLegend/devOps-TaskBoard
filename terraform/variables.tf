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
