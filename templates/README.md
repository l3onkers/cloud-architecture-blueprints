# 🧰 Reusable System Design & Cloud Architecture Templates

This directory provides standardized, placeholder-free starter templates for authoring new cloud architecture blueprints in this portfolio—either manually or via the **G.A.I.A. Autonomous Swarm** (`make new-blueprint NAME=03-gcp-gke-ai-gateway`).

---

## 📦 Template Catalog

| Template Bundle | Target Layer | Description |
| :--- | :--- | :--- |
| [`architecture-blueprint/`](./architecture-blueprint/) | **Layer 0 & 6 (APOLLO + MINERVA)** | Master architecture `README.tpl.md`, Architecture Decision Record (`adr-0001-template.md`), and Zero Trust Security Audit report (`security-audit.tpl.md`). |
| [`terraform-skeleton/`](./terraform-skeleton/) | **Layer 1 (DEMETER)** | Production Terraform foundation with remote state locking, parameterized domain variables (`var.domain_name`), KMS encryption, and least-privilege IAM tags. |
| [`kubernetes-gitops-skeleton/`](./kubernetes-gitops-skeleton/) | **Layers 2, 4 & 5 (AETHER + APOLLO + HEPHAESTUS)** | Dual-ALB Kubernetes Gateway API perimeter (`GatewayClass`, `Gateway`, `HTTPRoute`), Argo CD `AppProject` + `Application` with Image Updater annotations, and OpenTelemetry Jaeger `:4317` collector baseline. |

---

## 🚀 Scaffolding a New Blueprint

Use the portfolio CLI or `Makefile` from the repository root to instantiate a new architecture directory pre-populated with all 6 layer folders and templates:

```bash
make new-blueprint NAME=03-aws-serverless-event-mesh
```
