# 📜 Changelog

All notable changes to **Cloud Architecture Blueprints** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2026-11-25

### 🚀 Added
- **GitHub Packages & Release Automation:** Added `package.json` (`@l3onkers/cloud-architecture-blueprints`), `CHANGELOG.md`, and `.github/workflows/release.yml` to automatically publish versioned packages to GitHub Packages and generate GitHub Releases on SemVer tags.

### 🔧 Fixed & Improved
- **Domain-Agnostic Harness Sync:** Synchronized all 44 domain-agnostic G.A.I.A. `v1.2.1` governed skills and generalized the Zero Trust validation runner (`tests/validate/run-all.sh`).
- **CI/CD Hardening & Terraform Formatting:** Applied canonical `terraform fmt` alignment across Layer 1 AWS Terraform modules, updated `aquasecurity/trivy-action@v0.35.0`, and configured `PYTHONPATH` for monorepo microservice test discovery.
- **Portfolio Showcase Layout:** Enhanced the root `README.md` with the hero banner, compact horizontal 6-layer Mermaid diagram, and properly scaled architecture topology preview.

---

## [1.0.0] - 2026-11-24

### 🚀 Added
- **Blueprint 01 (`architectures/01-aws-eks-online-boutique-platform/`)**: Complete 6-layer production architecture on AWS EKS 1.34 (24 Terraform HCL files, Dual-ALB Kubernetes Gateway API + ExternalDNS, 11 Online Boutique microservices + 4 HPAs + compilable `.NET 8` / `Python FastAPI` / `React` source code, 3-pillar Observability with Prometheus/Grafana/Slack + ECK + Jaeger OTLP `:4317`, Argo CD + Image Updater GitOps, Chaos Mesh experiments, `k6` + `Playwright` suites, 3 ADRs, and MINERVA Zero Trust Security Audit).
- **Blueprint 02 (`architectures/02-azure-aks-fintech-ledger-blueprint/`)**: Multi-cloud Azure AKS 1.31 + Istio strict mTLS + PostgreSQL Flyway reference starter.
- **Reusable System Design Kit (`templates/`)**: Architecture Blueprint, ADR, Zero Trust Checklist, Multi-AZ Terraform skeleton, and Kubernetes Gateway API + Argo CD templates.
- **Portfolio CLI & Local Simulator (`Makefile`, `scripts/portfolio-cli.py`)**: Zero-dependency local Storefront & Gateway simulator (`make serve`), live E2E test runner (`make test-e2e`), and 6-layer validation battery (`make validate`).
