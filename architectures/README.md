# 🏛️ Cloud Architecture Blueprints — System Catalog

This directory houses production-grade, full-stack cloud architecture blueprints forged and verified by the **G.A.I.A. Autonomous Swarm**. Every blueprint is structured across **6 deterministic layers** (Cloud IaC, Perimeter & Mesh Networking, Application Workloads, 3-Pillar Observability, CI/CD + GitOps, and Chaos/QA/Zero Trust Audit).

---

## 📊 Blueprint Comparison Matrix

| ID | Blueprint Name | Cloud & Orchestrator | Networking & Ingress | Data & Stateful Layer | Observability Stack | GitOps & CI/CD | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **01** | [**AWS EKS Online Boutique Platform**](./01-aws-eks-online-boutique-platform/README.md) | AWS (`us-east-1`) · **EKS 1.34** (`workers` + `workers-autoscaler min 0`, Hybrid `IRSA` + `Pod Identity`) | **Kubernetes Gateway API** (`app-alb-gateway` & `platform-alb-gateway` HTTPS 443) + `ExternalDNS` + `Route 53` + `ACM` | **ElastiCache Redis 7.1** (Multi-AZ TLS) + **EBS gp3** CSI Driver | **Prometheus + Grafana + Alertmanager (Slack)** · **ECK (Filebeat + ES + Kibana)** · **Jaeger OTLP gRPC `:4317`** | GitHub Actions Matrix (`detect-changes` $\to$ `Build` $\to$ `Trivy` $\to$ `GHCR`) + **Argo CD & Image Updater** | ✅ **Verified v1.0.0** |
| **02** | [**Azure AKS Zero-Trust FinTech Ledger**](./02-azure-aks-fintech-ledger-blueprint/README.md) *(Starter Reference)* | Azure (`westeurope`) · **AKS 1.31** (Workload Identity + Key Vault CSI) | **Istio Service Mesh** (`Gateway` + `VirtualService` strict mTLS) + Azure Application Gateway WAF v2 | **Azure Database for PostgreSQL Flexible Server** + **Flyway** SQL Migrations | **Prometheus + Grafana** · **OpenTelemetry Collector** $\to$ **Jaeger** | GitHub Actions + **Trivy** + **Argo CD** | 🧩 **Blueprint Template** |

---

## 🧭 6-Layer Standard Inside Every Blueprint

Every architecture directory (`architectures/<id>-<slug>/`) follows a uniform layout:

```text
architectures/<id>-<slug>/
├── README.md                  # Full architecture documentation, topology diagram & runbook
├── docker-compose.yml         # Local multi-container developer topology
├── docs/
│   ├── assets/                # High-resolution topology diagrams
│   ├── adr/                   # Architecture Decision Records (0001..000N)
│   └── SECURITY_AUDIT.md      # MINERVA Zero Trust compliance report
├── infra/
│   └── terraform/             # DEMETER modular Terraform IaC (VPC/VNet, EKS/AKS, IAM, Data)
├── k8s/
│   ├── platform/              # Cluster controllers, StorageClasses, Autoscalers, CSI drivers
│   ├── networking/            # AETHER Gateway API / Istio Service Mesh & ExternalDNS
│   ├── <app-namespace>/       # ELEUTHIA microservice deployments, Services & HPAs
│   ├── observability/         # APOLLO monitoring, logging, and OTLP tracing manifests
│   ├── argocd/                # HEPHAESTUS AppProjects, Applications & Image Updater configs
│   └── chaos/                 # HADES Chaos Mesh fault-injection experiments
├── services/                  # Compilable microservice source code & multi-stage non-root Dockerfiles
├── scripts/
│   └── dev-server.py          # Zero-dependency local Gateway & Storefront simulator
└── tests/
    ├── k6/                    # ARTEMIS k6 load & SLO benchmark scripts
    ├── playwright/            # ARTEMIS Playwright E2E browser suites
    └── validate/              # Automated local validation & live E2E test runners
```
