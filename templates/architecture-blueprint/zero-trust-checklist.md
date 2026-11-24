# 🛡️ MINERVA Zero Trust Security Audit Checklist

- [ ] **State & Data Encryption:** Remote Terraform state, Kubernetes secrets (KMS), block volumes (`gp3`), and managed caches/databases enforce encryption at rest and TLS in transit.
- [ ] **Instance Metadata Hardening:** All compute nodes and bastion hosts enforce IMDSv2 (`http_tokens = "required"`).
- [ ] **Control Plane Isolation:** Kubernetes API server public endpoint is disabled or locked to explicit CIDR allowlists; private subnet placement enforced for all worker nodes.
- [ ] **Hybrid Least-Privilege IAM:** Controllers use scoped OIDC IRSA or EKS Pod Identity roles without wildcard `*` resource permissions on sensitive APIs.
- [ ] **Dual-Gateway Perimeter Separation:** Customer traffic (`app-alb-gateway`) is isolated from administrative planes (`platform-alb-gateway`) via namespace label selectors (`gateway-access`).
- [ ] **Non-Root Container Execution:** All application and observability pods enforce `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, and drop `ALL` Linux capabilities.
- [ ] **Supply Chain Vulnerability Gate:** CI pipeline scans every built container image with Aqua `Trivy` (`exit-code: '1'` on `CRITICAL,HIGH`) prior to registry publication.
- [ ] **Secret & Domain Hygiene:** Zero hardcoded credentials, private keys, or personal domains exist in tracked files.
