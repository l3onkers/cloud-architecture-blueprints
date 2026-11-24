module "vpc" {
  source = "./modules/vpc"

  aws_region      = var.aws_region
  project_name    = var.project_name
  cluster_name    = var.cluster_name
  vpc_cidr        = var.vpc_cidr
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

module "bastion" {
  source = "./modules/bastion"

  project_name         = var.project_name
  vpc_id               = module.vpc.vpc_id
  vpc_cidr             = var.vpc_cidr
  public_subnet_id     = module.vpc.public_subnet_ids[0]
  bastion_allowed_cidr = var.bastion_allowed_cidr
}

module "eks" {
  source = "./modules/eks"

  project_name             = var.project_name
  cluster_name             = var.cluster_name
  cluster_version          = var.cluster_version
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  bastion_security_group_id = module.bastion.security_group_id
}

module "iam" {
  source = "./modules/iam"

  project_name      = var.project_name
  cluster_name      = var.cluster_name
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.oidc_provider_url
  hosted_zone_arn   = module.dns_acm.hosted_zone_arn
}

module "elasticache" {
  source = "./modules/elasticache"

  project_name             = var.project_name
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  eks_node_security_group_id = module.eks.node_security_group_id
}

module "dns_acm" {
  source = "./modules/dns_acm"

  project_name = var.project_name
  domain_name  = var.domain_name
}
