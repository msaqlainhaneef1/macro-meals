# ============================================================
# Macro & Meals — Build & Development Commands
# ============================================================
# Usage:
#   make build     — Rebuild all pages from components
#   make serve     — Start local dev server on port 8080
#   make dev       — Build + serve (full dev workflow)
#   make sitemap   — Regenerate sitemap.xml only
#   make clean     — Remove generated files
#   make count     — Count total pages
#   make lint      — Check HTML for common issues
#   make zip       — Create distributable zip file
# ============================================================

.PHONY: build serve dev sitemap clean count lint zip help

# Default target
help:
	@echo "Macro & Meals — Available Commands:"
	@echo "  make build     Rebuild all pages from components"
	@echo "  make serve     Start local dev server (port 8080)"
	@echo "  make dev       Build + serve"
	@echo "  make sitemap   Regenerate sitemap.xml only"
	@echo "  make clean     Remove generated files"
	@echo "  make count     Count total pages"
	@echo "  make lint      Check HTML for common issues"
	@echo "  make zip       Create distributable zip"
	@echo "  make help      Show this help"

# Build all pages from component files
build:
	@echo "Building all pages..."
	python3 _build/scripts/build.py
	@echo ""

# Start local development server
serve:
	@echo "Starting dev server at http://localhost:8080"
	php -S localhost:8080 -t . _build/php-router.php

# Full dev workflow: build then serve
dev: build serve

# Regenerate sitemap only (quick)
sitemap:
	@cd _build/scripts && python3 -c "from build import generate_sitemap, generate_sitemap_xsl, generate_robots_txt; generate_sitemap(); generate_sitemap_xsl(); generate_robots_txt()"

# Remove generated/temporary files
clean:
	@rm -f sitemap.xml sitemap.xsl robots.txt
	@echo "Cleaned generated files."

# Count total HTML pages
count:
	@echo "Total HTML pages:"
	@find . -name "index.html" -o -name "404.html" | grep -v components | grep -v _build | grep -v node_modules | wc -l

# Basic HTML lint checks
lint:
	@echo "Checking for common issues..."
	@echo "--- Missing titles ---"
	@grep -rL "<title>" --include="*.html" . | grep -v components | grep -v _build || echo "  All pages have titles"
	@echo "--- Missing canonical ---"
	@grep -rL "canonical" --include="*.html" . | grep -v components | grep -v _build | grep -v 404 || echo "  All pages have canonical URLs"
	@echo "--- Old branding ---"
	@grep -rl "NutritionCalculators" --include="*.html" . | grep -v components | grep -v _build || echo "  No old branding found"
	@echo "--- Missing favicon ---"
	@grep -rL "favicon" --include="*.html" . | grep -v components | grep -v _build || echo "  All pages have favicon"
	@echo ""
	@echo "Lint complete."

# Create distributable zip
zip:
	@echo "Creating distribution zip..."
	@zip -r macroandmeals-dist.zip \
		. \
		-x ".git/*" \
		-x "*.pyc" \
		-x "__pycache__/*" \
		-x "macroandmeals-dist.zip"
	@echo "Created: macroandmeals-dist.zip"
