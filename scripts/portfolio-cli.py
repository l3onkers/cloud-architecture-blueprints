#!/usr/bin/env python3
"""
Cloud Architecture Blueprints — Portfolio Automation CLI
Commands:
  python3 scripts/portfolio-cli.py list
  python3 scripts/portfolio-cli.py validate [architecture_slug]
  python3 scripts/portfolio-cli.py test-e2e [architecture_slug]
  python3 scripts/portfolio-cli.py serve [architecture_slug] [port]
  python3 scripts/portfolio-cli.py new-blueprint <id-slug>
"""

import os
import shutil
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARCH_DIR = os.path.join(REPO_ROOT, "architectures")
TPL_DIR = os.path.join(REPO_ROOT, "templates")
DEFAULT_ARCH = "01-aws-eks-online-boutique-platform"


def list_blueprints():
    print("==============================================================================")
    print(" 🏛️  CLOUD ARCHITECTURE BLUEPRINTS — PORTFOLIO CATALOG")
    print("==============================================================================")
    entries = sorted(
        d for d in os.listdir(ARCH_DIR) if os.path.isdir(os.path.join(ARCH_DIR, d))
    )
    for idx, slug in enumerate(entries, 1):
        full = os.path.join(ARCH_DIR, slug)
        has_tf = os.path.isdir(os.path.join(full, "infra", "terraform"))
        has_k8s = os.path.isdir(os.path.join(full, "k8s"))
        has_sim = os.path.isfile(os.path.join(full, "scripts", "dev-server.py"))
        mode = "Full 6-Layer Verified System" if (has_tf and has_k8s and has_sim) else "Reference Blueprint Starter"
        print(f"  [{idx}] {slug}")
        print(f"      Type: {mode}")
        print(f"      Path: architectures/{slug}/")
    print("\nReusable Templates (templates/):")
    for t in sorted(d for d in os.listdir(TPL_DIR) if os.path.isdir(os.path.join(TPL_DIR, d))):
        print(f"  - templates/{t}/")
    print("==============================================================================")


def validate_blueprints(target_slug=None):
    slugs = [target_slug] if target_slug else sorted(
        d for d in os.listdir(ARCH_DIR) if os.path.isdir(os.path.join(ARCH_DIR, d))
    )
    overall_rc = 0
    for slug in slugs:
        runner = os.path.join(ARCH_DIR, slug, "tests", "validate", "run-all.sh")
        if os.path.isfile(runner):
            print(f"\n▶ Running 6-Layer Validation Battery for [{slug}]...")
            rc = subprocess.call(["bash", runner])
            if rc != 0:
                overall_rc = rc
        else:
            readme = os.path.join(ARCH_DIR, slug, "README.md")
            if os.path.isfile(readme):
                print(f"  ✓ [{slug}] Starter Blueprint README verified ({readme})")
            else:
                print(f"  ✗ [{slug}] Missing README.md")
                overall_rc = 1
    sys.exit(overall_rc)


def run_e2e(target_slug=DEFAULT_ARCH):
    e2e_script = os.path.join(ARCH_DIR, target_slug, "tests", "validate", "test-live-e2e.py")
    if not os.path.isfile(e2e_script):
        print(f"Error: E2E runner not found at {e2e_script}", file=sys.stderr)
        sys.exit(1)
    sys.exit(subprocess.call([sys.executable, e2e_script]))


def serve_blueprint(target_slug=DEFAULT_ARCH, port="8080"):
    server_script = os.path.join(ARCH_DIR, target_slug, "scripts", "dev-server.py")
    if not os.path.isfile(server_script):
        print(f"Error: Local simulator not found at {server_script}", file=sys.stderr)
        sys.exit(1)
    sys.exit(subprocess.call([sys.executable, server_script, str(port)]))


def new_blueprint(slug):
    dest = os.path.join(ARCH_DIR, slug)
    if os.path.exists(dest):
        print(f"Error: Blueprint directory architectures/{slug} already exists.", file=sys.stderr)
        sys.exit(1)
    for sub in [
        "docs/adr",
        "docs/assets",
        "infra/terraform",
        "k8s/platform",
        "k8s/networking",
        "k8s/app",
        "k8s/observability",
        "k8s/argocd",
        "k8s/chaos",
        "services",
        "scripts",
        "tests/validate",
    ]:
        os.makedirs(os.path.join(dest, sub), exist_ok=True)

    with open(os.path.join(TPL_DIR, "architecture-blueprint", "README.tpl.md"), "r", encoding="utf-8") as f:
        readme_tpl = f.read().replace("{{BLUEPRINT_TITLE}}", f"Blueprint — {slug}")
    with open(os.path.join(dest, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_tpl)

    shutil.copy2(
        os.path.join(TPL_DIR, "architecture-blueprint", "adr-0001-template.md"),
        os.path.join(dest, "docs", "adr", "0001-initial-architecture.md"),
    )
    shutil.copy2(
        os.path.join(TPL_DIR, "architecture-blueprint", "zero-trust-checklist.md"),
        os.path.join(dest, "docs", "SECURITY_AUDIT.md"),
    )
    for tf_file in ("versions.tf", "variables.tf"):
        shutil.copy2(
            os.path.join(TPL_DIR, "terraform-skeleton", tf_file),
            os.path.join(dest, "infra", "terraform", tf_file),
        )
    shutil.copy2(
        os.path.join(TPL_DIR, "kubernetes-gitops-skeleton", "gateway-and-argocd.yaml"),
        os.path.join(dest, "k8s", "networking", "gateway-and-argocd.yaml"),
    )
    print(f"✓ Scaffolded new 6-layer architecture blueprint at: architectures/{slug}/")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        list_blueprints()
    elif cmd == "validate":
        validate_blueprints(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "test-e2e":
        run_e2e(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_ARCH)
    elif cmd == "serve":
        arch = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_ARCH
        port = sys.argv[3] if len(sys.argv) > 3 else "8080"
        serve_blueprint(arch, port)
    elif cmd == "new-blueprint":
        if len(sys.argv) < 3:
            print("Usage: portfolio-cli.py new-blueprint <id-slug>", file=sys.stderr)
            sys.exit(1)
        new_blueprint(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
