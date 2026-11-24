# ==============================================================================
# Cloud Architecture Blueprints — Portfolio Makefile
# ==============================================================================

ARCH ?= 01-aws-eks-online-boutique-platform
PORT ?= 8080
NAME ?= 03-new-cloud-blueprint

.PHONY: help list validate test-e2e serve new-blueprint

help:
	@echo "=============================================================================="
	@echo " 🏛️  Cloud Architecture Blueprints — Portfolio Commands"
	@echo "=============================================================================="
	@echo "  make list                          List all architectures & reusable templates"
	@echo "  make validate                      Run 6-layer validation battery on catalog"
	@echo "  make test-e2e ARCH=<slug>          Run live HTTP E2E customer journey test"
	@echo "  make serve ARCH=<slug> PORT=8080   Start local Storefront & Gateway simulator"
	@echo "  make new-blueprint NAME=<id-slug>  Scaffold a new 6-layer blueprint from templates"
	@echo "=============================================================================="

list:
	@python3 scripts/portfolio-cli.py list

validate:
	@python3 scripts/portfolio-cli.py validate

test-e2e:
	@python3 scripts/portfolio-cli.py test-e2e $(ARCH)

serve:
	@python3 scripts/portfolio-cli.py serve $(ARCH) $(PORT)

new-blueprint:
	@python3 scripts/portfolio-cli.py new-blueprint $(NAME)
