# 🏦 Blueprint 02 — Azure AKS Zero-Trust FinTech Ledger (Starter Reference)

<p align="center">
  <img src="https://img.shields.io/badge/Cloud-Azure%20AKS%201.31-0078D4?logo=microsoftazure&logoColor=white" alt="Azure AKS">
  <img src="https://img.shields.io/badge/IaC-Terraform%20%3E%3D%201.7-7B42BC?logo=terraform&logoColor=white" alt="Terraform">
  <img src="https://img.shields.io/badge/Mesh-Istio%20Strict%20mTLS-466BB0?logo=istio&logoColor=white" alt="Istio">
  <img src="https://img.shields.io/badge/Database-Azure%20PostgreSQL%20%2B%20Flyway-336791?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Status-Starter%20Blueprint-a855f7" alt="Starter Blueprint">
</p>

> **Multi-Cloud Companion Reference demonstrating how the G.A.I.A. 6-Layer Methodology adapts from AWS EKS to Azure AKS with Istio mTLS and PostgreSQL Flyway migrations.**

---

## 1. Architecture Overview

While [**Blueprint 01 (`01-aws-eks-online-boutique-platform`)**](../01-aws-eks-online-boutique-platform/README.md) showcases a complete, production-verified AWS EKS e-commerce platform, **Blueprint 02** provides the Azure AKS architectural reference pattern governed by `demeter-terraform-azure-base`, `aether-istio-ingress`, `eleuthia-net-api-cqrs`, and `poseidon-flyway-migration`.

```mermaid
flowchart LR
    Client["Client / Partner API"] --> WAF["Azure App Gateway WAF v2"]
    WAF --> IstioGW["Istio IngressGateway (TLS 1.3)"]
    subgraph AKS["Azure AKS 1.31 Private Cluster (VNet 10.10.0.0/16)"]
        IstioGW --> LedgerAPI[".NET 8 CQRS Ledger API (strict mTLS)"]
        LedgerAPI --> OutboxWorker[".NET 8 Settlement Worker"]
        OTel["Jaeger / OTel Collector :4317"]
    end
    LedgerAPI --> PG["Azure Database for PostgreSQL Flexible Server (Private Endpoint)"]
    LedgerAPI -.-> OTel
```

---

## 2. GAIA Skills Mapped to This Blueprint

- **Layer 1 (DEMETER):** `demeter-terraform-azure-base` (Azure Blob Storage state backend, VNet, Private AKS cluster, Azure PostgreSQL Flexible Server, Entra Workload Identity).
- **Layer 2 (AETHER):** `aether-istio-ingress` (`Gateway`, `VirtualService`, `PeerAuthentication` with `mtls.mode: STRICT`).
- **Layer 3 (ELEUTHIA + POSEIDON):** `eleuthia-net-api-cqrs` + `eleuthia-net-worker` + `poseidon-flyway-migration` (idempotent double-entry ledger schema migrations).
- **Layer 4 (APOLLO):** `apollo-observability-stack` (Prometheus, Grafana, Jaeger OTLP `:4317`).
- **Layer 5 (HEPHAESTUS):** `hephaestus-net-cicd` + `hephaestus-argocd-gitops`.
- **Layer 6 (MINERVA + ARTEMIS + HADES):** `minerva-review`, `artemis-k6-load-test`, `hades-chaos-mesh-experiment`.
