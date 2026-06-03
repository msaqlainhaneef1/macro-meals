# Macro & Meals

Free nutrition calculators and health tools for 50+ restaurants, BMI, BMR, TDEE, macros, vitamins, and more.

**Live site:** [macroandmeals.com](https://macroandmeals.com)

---

## Quick Start

```bash
# Start local dev server
make serve
# Open http://localhost:8080

# Or build + serve
make dev
```

## Project Structure

This repo uses a **flat structure** — website files live at the root for direct Hostinger deployment. Build tools are in `_build/`.

```
macroandmeals/
├── index.html                     # Homepage
├── 404.html                       # Custom 404 page
├── sitemap.xml                    # Auto-generated sitemap
├── sitemap.xsl                    # Sitemap browser stylesheet
├── robots.txt                     # Auto-generated robots
├── site.webmanifest               # PWA manifest
├── .htaccess                      # Apache config (redirects, security, caching)
├── Makefile                       # Easy build/dev/lint/zip commands
├── README.md                      # This file
│
├── components/                    # Reusable HTML components
│   ├── header.html                # Site header (logo, nav, dropdowns)
│   ├── footer.html                # Site footer (links, copyright)
│   ├── head-common.html           # Common <head> tags (GA4, GTM, favicon)
│   ├── gtm-noscript.html          # GTM noscript iframe
│   ├── scripts.html               # Common JS includes
│   ├── breadcrumbs.html           # Breadcrumb navigation + schema.org
│   ├── scroll-progress.html       # Reading progress bar
│   ├── social-share.html          # Social sharing buttons
│   ├── back-to-top.html           # Scroll-to-top button
│   ├── cookie-banner.html         # GDPR/CCPA cookie consent
│   ├── announcement-bar.html      # Promotional announcement bar
│   └── print-styles.html          # Print-friendly stylesheet
│
├── css/
│   ├── style.css                  # Main stylesheet
│   └── blog.css                   # Blog-specific styles
│
├── js/
│   ├── site-config.js             # Branding & config
│   ├── scripts-config.js          # Analytics IDs (GA4, AdSense, GTM)
│   ├── main.js                    # PAGE_REGISTRY, nav, internal linking
│   ├── restaurant.js              # JSON-driven restaurant calculator
│   ├── calculator.js              # Shared calculator utilities
│   ├── menu.js                    # Menu page renderer
│   ├── search.js                  # Search functionality
│   └── contact.js                 # Contact form handler
│
├── img/                           # Logo, favicon, icons
├── data/restaurants/              # JSON restaurant data files
│
├── [calculator-pages]/            # 126 calculator & content pages
│   └── index.html
│
└── _build/                        # Build tools (blocked from web access)
    ├── scripts/
    │   ├── build.py               # Build script — injects components into all pages
    │   ├── generate_pages.py      # Generate policy & blog pages
    │   └── extract_restaurant_data.py
    ├── config/
    │   └── config.json            # Centralized site configuration
    └── server.py                  # Local dev server with 404 routing
```

## Component System

All shared UI elements live in `components/`. Edit a component file, then run the build to update all 126+ pages.

```bash
# Edit a component
nano components/header.html

# Rebuild all pages
make build
```

### Available Components

| Component | Description |
|-----------|-------------|
| `header.html` | Logo + 6 navigation dropdowns |
| `footer.html` | 4-column footer (Quick Links, Calculators, Restaurants) |
| `head-common.html` | GA4, GTM, site verification, favicon, manifest |
| `gtm-noscript.html` | GTM noscript iframe (after `<body>`) |
| `scripts.html` | Common JS files loaded before `</body>` |
| `breadcrumbs.html` | Auto-generated breadcrumbs with schema.org |
| `scroll-progress.html` | Green reading progress bar |
| `social-share.html` | Twitter, Facebook, LinkedIn, WhatsApp share buttons |
| `back-to-top.html` | Scroll-to-top button |
| `cookie-banner.html` | GDPR/CCPA cookie consent banner |
| `announcement-bar.html` | Top promo bar (disabled by default) |
| `print-styles.html` | Print-friendly CSS |

## Deployment (Hostinger)

This repo is structured for direct Hostinger Git deployment:

1. In Hostinger panel → **Advanced** → **Git**
2. Repository: `git@github.com:microandmeals/macroandmeals.git`
3. Branch: `main`
4. Click **Create** → **Pull Now**

All website files are at the repo root, so they deploy directly to `public_html/`.

### API caching (nutrition search)
Food API responses are cached in **PHP memory (APCu)** when available — no files are written under `api/cache/`. Enable the **APCu** extension in Hostinger → **PHP Configuration** for best performance. Browsers also cache JSON responses via `Cache-Control` / `ETag`.

### Auto-deploy (optional)
1. Copy the **Webhook URL** from Hostinger Git section
2. GitHub repo → **Settings** → **Webhooks** → **Add webhook**
3. Paste URL, set content type to `application/json`, select "Just the push event"

## Adding New Content

### New Restaurant Calculator
1. Create JSON file in `data/restaurants/your-restaurant.json`
2. Create page directory: `mkdir your-restaurant-nutrition-calculator`
3. Copy template: `cp chipotle-nutrition-calculator/index.html your-restaurant-nutrition-calculator/index.html`
4. Update title, meta tags, and data source path
5. Add to `PAGE_REGISTRY` in `js/main.js`
6. Run `make build`

### New Blog Post
1. Create directory: `mkdir -p blog/your-post-slug`
2. Copy template: `cp blog/how-to-calculate-your-daily-calorie-needs/index.html blog/your-post-slug/index.html`
3. Update content
4. Run `make build`

## Make Commands

| Command | Description |
|---------|-------------|
| `make build` | Rebuild all pages from components |
| `make serve` | Start dev server on port 8080 |
| `make dev` | Build + serve |
| `make sitemap` | Regenerate sitemap.xml only |
| `make count` | Count total HTML pages |
| `make lint` | Check for common issues |
| `make zip` | Create distributable zip |
