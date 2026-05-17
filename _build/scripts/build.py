#!/usr/bin/env python3
"""
Macro & Meals — Build Script
Rebrands all pages, fixes unicode escapes, creates missing pages,
generates sitemap.xml, and ensures consistent structure.

Component files in public_html/components/ are the single source of truth:
  header.html      — Standard site header (nav, logo, dropdowns)
  footer.html      — Standard site footer (links, copyright)
  head-common.html — Common <head> tags (favicon, manifest, theme)
  scripts.html     — Common script tags loaded before </body>
  back-to-top.html — Back-to-top scroll button
  cookie-banner.html — GDPR/CCPA cookie consent banner

Edit the component files, then run: python3 build.py
All 127+ pages will be updated automatically.
"""
import os, re, glob, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.path.dirname(BUILD_DIR)
ROOT = REPO_ROOT  # Website files are at repo root (flat structure for Hostinger)
COMPONENTS_DIR = os.path.join(ROOT, 'components')
DOMAIN = 'macroandmeals.com'
URL = f'https://{DOMAIN}'
BRAND = 'Macro & Meals'
BRAND_SHORT = 'Macro And Meals'
ABBR = 'MM'
OLD_DOMAIN = 'nutritioncalculators.net'
OLD_BRAND = 'NutritionCalculators'
OLD_BRAND_DOT = 'NutritionCalculators.net'

# Unicode escape → real emoji mapping
UNICODE_MAP = {
    r'\u26a1': '⚡', r'\u2696\ufe0f': '⚖️', r'\ud83d\udd25': '🔥',
    r'\ud83c\udf4e': '🍎', r'\ud83d\udca7': '💧', r'\ud83c\udfcb\ufe0f': '🏋️',
    r'\u2694\ufe0f': '⚔️', r'\u26a0\ufe0f': '⚠️', r'\ud83d\udea8': '🚨',
    r'\ud83c\udf4f': '🍏', r'\ud83e\udd69': '🥩', r'\ud83c\udf5e': '🍞',
    r'\ud83e\udd51': '🥑', r'\ud83d\udcca': '📊', r'\ud83d\udcc9': '📉',
    r'\ud83d\udcc5': '📅', r'\ud83e\udd30': '🤰', r'\ud83d\udc76': '👶',
    r'\ud83c\udfc5': '🏅', r'\ud83d\udcaa': '💪', r'\ud83d\udccf': '📏',
    r'\u2764\ufe0f': '❤️', r'\ud83e\udde0': '🧠', r'\ud83c\udf1e': '🌞',
    r'\ud83d\udc8a': '💊', r'\ud83c\udf4a': '🍊', r'\u2600\ufe0f': '☀️',
    r'\ud83e\ude7a': '🩺', r'\ud83c\udfe5': '🏥', r'\ud83d\ude0a': '😊',
    r'\ud83e\udd47': '🥇', r'\ud83e\udd48': '🥈', r'\ud83e\udd49': '🥉',
    r'\ud83d\udee1\ufe0f': '🛡️', r'\u2753': '❓', r'\u2714\ufe0f': '✔️',
    r'\ud83d\udcda': '📚', r'\ud83d\udcdd': '📝', r'\ud83d\udca1': '💡',
    r'\ud83c\udf0e': '🌎', r'\ud83c\udfaf': '🎯', r'\ud83d\udd2c': '🔬',
    r'\ud83d\udca8': '💨', r'\ud83e\uddc2': '🧂',
    r'\ud83c\udf54': '🍔', r'\ud83c\udf5f': '🍟', r'\ud83c\udf2e': '🌮',
    r'\ud83c\udf2f': '🌯', r'\ud83c\udf55': '🍕', r'\ud83c\udf63': '🍣',
    r'\ud83c\udf5c': '🍜', r'\u2615': '☕', r'\ud83e\udd64': '🥤',
    r'\ud83c\udf57': '🍗', r'\ud83e\udd56': '🥖', r'\ud83e\udd57': '🥗',
    r'\ud83e\udd59': '🥙', r'\ud83e\udd61': '🥡', r'\ud83c\udf36\ufe0f': '🌶️',
    r'\ud83c\udf5a': '🍚', r'\ud83c\udfe0': '🏠', r'\ud83c\udfea': '🏪',
    r'\ud83d\udeb6': '🚶', r'\ud83d\udc63': '👣', r'\ud83d\udd04': '🔄',
}

def fix_unicode_escapes(text):
    """Replace \\uXXXX escape sequences in HTML with actual UTF-8 characters."""
    # Sort by length descending to match longer sequences first (surrogate pairs)
    for esc, emoji in sorted(UNICODE_MAP.items(), key=lambda x: -len(x[0])):
        text = text.replace(esc, emoji)

    def replace_surrogates(m):
        """Handle surrogate pairs: \\uD83E\\uDDD1 -> actual emoji."""
        try:
            hi = int(m.group(1), 16)
            lo = int(m.group(2), 16)
            cp = 0x10000 + (hi - 0xD800) * 0x400 + (lo - 0xDC00)
            return chr(cp)
        except:
            return m.group(0)

    def replace_single(m):
        """Handle single \\uXXXX (non-surrogate)."""
        try:
            cp = int(m.group(1), 16)
            if 0xD800 <= cp <= 0xDFFF:
                return m.group(0)
            return chr(cp)
        except:
            return m.group(0)

    # Only replace in HTML content, not inside <script> tags
    parts = re.split(r'(<script[\s>].*?</script>)', text, flags=re.DOTALL)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:  # Outside script tags
            # First handle surrogate pairs
            part = re.sub(r'\\u([dD][89aAbB][0-9a-fA-F]{2})\\u([dD][cCdDeEfF][0-9a-fA-F]{2})', replace_surrogates, part)
            # Then handle remaining single escapes
            part = re.sub(r'\\u([0-9a-fA-F]{4})', replace_single, part)
        result.append(part)
    return ''.join(result)

def rebrand(text):
    """Replace old branding with new."""
    # Domain replacements
    text = text.replace(f'https://{OLD_DOMAIN}', URL)
    text = text.replace(f'http://{OLD_DOMAIN}', URL)
    text = text.replace(OLD_DOMAIN, DOMAIN)
    # Brand name replacements (careful order)
    text = text.replace(f'About {OLD_BRAND_DOT}', f'About {BRAND}')
    text = text.replace(f'At {OLD_BRAND_DOT}', f'At {BRAND}')
    text = text.replace(OLD_BRAND_DOT, BRAND)
    # Logo text
    text = re.sub(
        r'(<div class="logo-icon">)\w+</div>\s*NutritionCalculators',
        f'\\1{ABBR}</div>{BRAND}',
        text
    )
    text = re.sub(
        r'(<div class="logo-icon">)\w+</div>\s*Macro & Meals',
        f'\\1{ABBR}</div>{BRAND}',
        text
    )
    # Title tags
    text = re.sub(
        r'(\| )NutritionCalculators\.net',
        f'\\1{BRAND}',
        text
    )
    # OG site_name
    text = text.replace(
        f'content="{OLD_BRAND_DOT}"',
        f'content="{BRAND}"'
    )
    text = text.replace(
        f'content="{OLD_BRAND}"',
        f'content="{BRAND}"'
    )
    # Footer copyright
    text = re.sub(
        r'&copy; \d+ NutritionCalculators\.net',
        f'&copy; {datetime.now().year} {BRAND}',
        text
    )
    # Schema.org
    text = text.replace(f'"name":"{OLD_BRAND}"', f'"name":"{BRAND}"')
    text = text.replace(f'"name":"{OLD_BRAND_DOT}"', f'"name":"{BRAND}"')
    # User agent in PHP
    text = text.replace(f'NutritionCalculators/1.0', f'MacroAndMeals/1.0')
    text = text.replace(f'contact@nutritioncalculators.net', f'contact@{DOMAIN}')
    # htaccess comments
    text = text.replace('NUTRITION CALCULATORS', 'MACRO & MEALS')
    text = text.replace('nutritioncalculators.net to nutritioncalculators.net', 
                        f'{DOMAIN} to {DOMAIN}')
    return text

def ensure_script_tags(html):
    """Ensure site-config.js and scripts-config.js are loaded."""
    if 'site-config.js' not in html:
        html = html.replace(
            '<script src="/js/main.js"></script>',
            '<script src="/js/site-config.js"></script>\n<script src="/js/scripts-config.js"></script>\n<script src="/js/main.js"></script>'
        )
    return html

# ---------------------------------------------------------------------------
# Component loader — reads HTML partials from components/ directory
# ---------------------------------------------------------------------------
def load_component(name):
    """Read a component file and return its contents (without HTML comments)."""
    path = os.path.join(COMPONENTS_DIR, name)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Strip HTML comment lines (<!-- ... -->) for cleaner injection
    content = re.sub(r'<!--[\s\S]*?-->\n?', '', content)
    return content.strip()

def load_all_components():
    """Load all component files into a dict. Called once at build start."""
    components = {}
    for name in ['header.html', 'footer.html', 'head-common.html',
                 'scripts.html', 'back-to-top.html', 'cookie-banner.html',
                 'breadcrumbs.html', 'scroll-progress.html', 'social-share.html',
                 'announcement-bar.html', 'print-styles.html', 'gtm-noscript.html']:
        filepath = os.path.join(COMPONENTS_DIR, name)
        if os.path.exists(filepath):
            components[name] = load_component(name)
            print(f'  Loaded component: {name}')
        else:
            print(f'  WARNING: Component not found: {name}')
    # Process dynamic placeholders in footer
    if 'footer.html' in components:
        components['footer.html'] = components['footer.html'].replace(
            '{{YEAR}}', str(datetime.now().year)
        )
    return components

# These will be populated at build time by load_all_components()
COMPONENTS = {}

FAVICON_TAGS = '''<link rel="icon" type="image/svg+xml" href="/img/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#22c55e">'''

def ensure_favicon(html):
    """Ensure favicon and manifest tags are in <head>."""
    if 'favicon.svg' in html:
        return html
    html = html.replace('</head>', FAVICON_TAGS + '\n</head>')
    return html

def update_logo(html):
    """Replace text logo with SVG logo in header and footer."""
    svg_logo = '<img src="/img/logo.svg" alt="Macro &amp; Meals" class="logo-img" width="160" height="40">'
    html = re.sub(
        r'<a href="/" class="logo"><div class="logo-icon">\w+</div>Macro (?:&amp;|&) Meals</a>',
        f'<a href="/" class="logo">{svg_logo}</a>',
        html
    )
    return html

def standardize_header(html):
    """Replace the entire <header>...</header> block with the component version."""
    header = COMPONENTS.get('header.html', '')
    if header:
        html = re.sub(
            r'<header class="header">.*?</header>',
            header,
            html,
            flags=re.DOTALL
        )
    return html

def standardize_footer(html):
    """Replace the entire <footer>...</footer> block with the component version."""
    footer = COMPONENTS.get('footer.html', '')
    if footer:
        html = re.sub(
            r'<footer class="footer">.*?</footer>',
            footer,
            html,
            flags=re.DOTALL
        )
    return html

def ensure_common_head(html):
    """Ensure common head tags (analytics, favicon, manifest, theme) are present from component."""
    head_common = COMPONENTS.get('head-common.html', '')
    if not head_common:
        return html
    # Remove old GA4/GTM/verification tags to avoid duplicates
    html = re.sub(r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=[^"]*"></script>\s*', '', html)
    html = re.sub(r'<script>\s*window\.dataLayer\s*=.*?</script>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\(function\(w,d,s,l,i\).*?</script>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'<meta name="google-site-verification"[^>]*/?>\s*', '', html)
    # Remove old favicon/manifest/theme-color tags (will be re-added from component)
    html = re.sub(r'<link rel="icon"[^>]*/?>\s*', '', html)
    html = re.sub(r'<link rel="apple-touch-icon"[^>]*/?>\s*', '', html)
    html = re.sub(r'<link rel="manifest"[^>]*/?>\s*', '', html)
    html = re.sub(r'<meta name="theme-color"[^>]*/?>\s*', '', html)
    # Remove old stylesheet links to avoid duplicates
    html = re.sub(r'<link rel="stylesheet" href="/css/style\.css">\s*', '', html)
    # Remove old LLM discoverability tags to avoid duplicates
    html = re.sub(r'<link rel="alternate" type="text/plain" href="/llms[^"]*"[^>]*>\s*', '', html)
    html = re.sub(r'<meta name="llms:[^"]*"[^>]*/?>\s*', '', html)
    # Remove HTML comment blocks for LLM discoverability that may have been injected
    html = re.sub(r'<!-- LLM Discoverability[^>]*-->\s*', '', html)
    # Inject component before </head>
    html = html.replace('</head>', head_common + '\n</head>')
    return html

def ensure_common_scripts(html):
    """Ensure common script tags are present from component."""
    scripts = COMPONENTS.get('scripts.html', '')
    if not scripts:
        return html
    # Only add if site-config.js is not already present
    if 'site-config.js' in html:
        return html
    # Inject before </body>
    html = html.replace('</body>', scripts + '\n</body>')
    return html

def inject_back_to_top(html):
    """Add back-to-top button before </body> if not already present."""
    component = COMPONENTS.get('back-to-top.html', '')
    if not component or 'back-to-top' in html:
        return html
    html = html.replace('</body>', component + '\n</body>')
    return html

def inject_cookie_banner(html):
    """Add cookie consent banner before </body> if not already present."""
    component = COMPONENTS.get('cookie-banner.html', '')
    if not component or 'cookie-banner' in html:
        return html
    html = html.replace('</body>', component + '\n</body>')
    return html

# Pages that should NOT get breadcrumbs or share buttons
NO_BREADCRUMBS_SHARE = {
    '404.html', 'index.html',
    'about/index.html', 'contact/index.html',
    'privacy-policy/index.html', 'terms-conditions/index.html',
    'disclaimer/index.html', 'dmca/index.html',
    'cookie-policy/index.html', 'accessibility/index.html',
    'sitemap-page/index.html',
    'blog/index.html',
    'blog/how-to-calculate-your-daily-calorie-needs/index.html',
}

def inject_breadcrumbs(html, filepath=''):
    """Add or replace breadcrumb navigation after <header>."""
    import re
    # Always remove existing breadcrumbs first
    html = re.sub(r'<nav class="breadcrumbs"[^>]*>.*?</script>\s*', '', html, flags=re.DOTALL)
    # Skip injection for non-content pages
    rel = os.path.relpath(filepath, ROOT) if filepath else ''
    if rel in NO_BREADCRUMBS_SHARE:
        return html
    component = COMPONENTS.get('breadcrumbs.html', '')
    if not component:
        return html
    html = html.replace('</header>', '</header>\n' + component)
    return html

def inject_scroll_progress(html):
    """Add scroll progress bar after <body> if not already present."""
    component = COMPONENTS.get('scroll-progress.html', '')
    if not component or 'scroll-progress' in html:
        return html
    html = html.replace('<body>', '<body>\n' + component)
    return html

def inject_social_share(html, filepath=''):
    """Add or replace social share buttons before <footer>."""
    import re
    # Always remove existing social-share first
    html = re.sub(r'<div class="social-share"[^>]*>.*?</script>\s*', '', html, flags=re.DOTALL)
    # Skip injection for non-content pages
    rel = os.path.relpath(filepath, ROOT) if filepath else ''
    if rel in NO_BREADCRUMBS_SHARE:
        return html
    component = COMPONENTS.get('social-share.html', '')
    if not component:
        return html
    html = html.replace('<footer class="footer">', component + '\n<footer class="footer">')
    return html

def inject_announcement_bar(html):
    """Add announcement bar at top of <body> if not already present."""
    component = COMPONENTS.get('announcement-bar.html', '')
    if not component or 'announcement-bar' in html:
        return html
    html = html.replace('<body>', '<body>\n' + component)
    return html

def inject_print_styles(html):
    """Add print stylesheet to <head> if not already present."""
    component = COMPONENTS.get('print-styles.html', '')
    if not component or '@media print' in html:
        return html
    html = html.replace('</head>', component + '\n</head>')
    return html

def inject_gtm_noscript(html):
    """Add GTM noscript iframe right after <body> if not already present."""
    component = COMPONENTS.get('gtm-noscript.html', '')
    if not component or 'googletagmanager.com/ns.html' in html:
        return html
    html = html.replace('<body>', '<body>\n' + component)
    return html

def fix_favicon_refs(html):
    """Fix old favicon-32.png references to favicon-32x32.png."""
    html = html.replace('favicon-32.png', 'favicon-32x32.png')
    html = html.replace('#10b981', '#22c55e')
    return html

def process_html_file(filepath):
    """Apply all transformations to an HTML file."""
    # Skip component files themselves
    if os.path.join(ROOT, 'components') in filepath:
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = fix_unicode_escapes(content)
    content = rebrand(content)
    content = ensure_script_tags(content)
    content = ensure_favicon(content)
    content = update_logo(content)
    content = standardize_header(content)
    content = standardize_footer(content)
    content = ensure_common_head(content)
    content = ensure_common_scripts(content)
    content = fix_favicon_refs(content)
    content = inject_announcement_bar(content)
    content = inject_scroll_progress(content)
    content = inject_breadcrumbs(content, filepath)
    content = inject_social_share(content, filepath)
    content = inject_back_to_top(content)
    content = inject_cookie_banner(content)
    content = inject_print_styles(content)
    content = inject_gtm_noscript(content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  ✓ {os.path.relpath(filepath, ROOT)}')

def process_all_files():
    """Process every HTML, PHP, and config file."""
    print('Processing HTML files...')
    for html_file in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
        process_html_file(html_file)
    
    print('\nProcessing PHP files...')
    for php_file in glob.glob(os.path.join(ROOT, '**', '*.php'), recursive=True):
        with open(php_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = rebrand(content)
        with open(php_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  ✓ {os.path.relpath(php_file, ROOT)}')
    
    print('\nProcessing .htaccess...')
    htaccess = os.path.join(ROOT, '.htaccess')
    if os.path.exists(htaccess):
        with open(htaccess, 'r', encoding='utf-8') as f:
            content = f.read()
        content = rebrand(content)
        with open(htaccess, 'w', encoding='utf-8') as f:
            f.write(content)
        print('  ✓ .htaccess')

# ---------------------------------------------------------------------------
# Page categorization for sitemap priorities and changefreq
# ---------------------------------------------------------------------------
SKIP_DIRS = {'css', 'js', 'img', 'components', 'data', 'api', 'cache'}

ESSENTIAL_PAGES = {'about', 'contact', 'privacy-policy', 'terms-conditions',
                   'disclaimer', 'cookie-policy', 'dmca', 'accessibility',
                   'sitemap-page'}

BLOG_DIRS = {'blog'}

HIGH_TRAFFIC_CALCULATORS = {
    'bmi-calculator', 'bmr-calculator', 'tdee-calculator',
    'calorie-deficit-calculator', 'protein-calculator',
    'keto-macro-calculator', 'macro-calculator-for-weight-loss',
    'body-fat-calculator', 'ideal-body-weight-calculator',
}

HIGH_TRAFFIC_RESTAURANTS = {
    'chipotle-nutrition-calculator', 'mcdonalds-calories-calculator',
    'starbucks-nutrition-calculator', 'subway-nutrition-calculator',
    'taco-bell-nutrition-calculator', 'wendys-nutrition-calculator',
    'five-guys-nutrition-calculator', 'panda-express-nutrition-calculator',
    'burger-king-calories-calculator',
}


def categorize_page(slug):
    """Return (priority, changefreq) based on page type and importance."""
    if slug in ('.', ''):
        return '1.0', 'daily'

    if slug in HIGH_TRAFFIC_CALCULATORS or slug in HIGH_TRAFFIC_RESTAURANTS:
        return '0.9', 'weekly'

    if slug.endswith('-nutrition-calculator') or slug.endswith('-calories-calculator'):
        return '0.8', 'weekly'

    if slug.endswith('-menu'):
        return '0.7', 'weekly'

    if slug.endswith('-calculator') or slug.endswith('-converter'):
        return '0.8', 'weekly'

    if slug in ESSENTIAL_PAGES:
        return '0.5', 'monthly'

    if slug.startswith('blog'):
        return '0.7', 'weekly'

    return '0.6', 'monthly'


def generate_sitemap():
    """Generate advanced sitemap.xml with proper priorities, changefreq, and real lastmod dates."""
    pages = []

    # Collect all index.html files (including root)
    all_index_files = []
    root_index = os.path.join(ROOT, 'index.html')
    if os.path.exists(root_index):
        all_index_files.append(root_index)
    for html_file in glob.glob(os.path.join(ROOT, '*', 'index.html')):
        all_index_files.append(html_file)
    # Also check blog subdirectories
    for html_file in glob.glob(os.path.join(ROOT, 'blog', '*', 'index.html')):
        all_index_files.append(html_file)

    for html_file in all_index_files:
        rel = os.path.relpath(html_file, ROOT)
        slug = os.path.dirname(rel)

        # Skip asset/internal directories
        top_dir = slug.split(os.sep)[0] if slug not in ('.', '') else ''
        if top_dir in SKIP_DIRS:
            continue

        # Get actual file modification date
        mtime = os.path.getmtime(html_file)
        lastmod = datetime.fromtimestamp(mtime).strftime('%Y-%m-%dT%H:%M:%S+00:00')

        priority, changefreq = categorize_page(slug)

        if slug in ('.', ''):
            loc = '/'
        else:
            loc = f'/{slug}/'

        pages.append((loc, priority, changefreq, lastmod))

    # Sort: homepage first, then by priority descending, then alphabetically
    pages.sort(key=lambda x: (x[0] != '/', -float(x[1]), x[0]))

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>')
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    xml.append('        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
    xml.append('        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9')
    xml.append('        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">')

    for loc, priority, changefreq, lastmod in pages:
        xml.append('  <url>')
        xml.append(f'    <loc>{URL}{loc}</loc>')
        xml.append(f'    <lastmod>{lastmod}</lastmod>')
        xml.append(f'    <changefreq>{changefreq}</changefreq>')
        xml.append(f'    <priority>{priority}</priority>')
        xml.append('  </url>')
    xml.append('</urlset>')

    sitemap_path = os.path.join(ROOT, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml))

    # Count by priority for summary
    p_counts = {}
    for _, p, _, _ in pages:
        p_counts[p] = p_counts.get(p, 0) + 1
    summary = ', '.join(f'P{p}={c}' for p, c in sorted(p_counts.items(), reverse=True))
    print(f'\n✓ Generated sitemap.xml with {len(pages)} URLs ({summary})')


def generate_sitemap_xsl():
    """Generate an XSL stylesheet so sitemap.xml renders nicely in browsers."""
    xsl = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9">
<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Macro &amp; Meals — Sitemap</title>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <style>
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0;padding:2rem;background:#f8fafc;color:#1e293b}
    h1{color:#22c55e;margin-bottom:.25rem}
    p.info{color:#64748b;margin-bottom:1.5rem;font-size:.95rem}
    table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1)}
    th{background:#22c55e;color:#fff;padding:.75rem 1rem;text-align:left;font-weight:600;font-size:.85rem;text-transform:uppercase;letter-spacing:.05em}
    td{padding:.6rem 1rem;border-bottom:1px solid #e2e8f0;font-size:.9rem}
    tr:hover td{background:#f0fdf4}
    a{color:#22c55e;text-decoration:none}
    a:hover{text-decoration:underline}
    .priority{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.8rem;font-weight:600}
    .p10{background:#dcfce7;color:#166534}.p09{background:#d1fae5;color:#065f46}.p08{background:#e0f2fe;color:#075985}
    .p07{background:#fef3c7;color:#92400e}.p06{background:#f1f5f9;color:#475569}.p05{background:#f1f5f9;color:#64748b}
    #count{color:#64748b;font-size:.85rem;margin-top:1rem}
  </style>
</head>
<body>
  <h1>Macro &amp; Meals — XML Sitemap</h1>
  <p class="info">This sitemap contains <xsl:value-of select="count(sitemap:urlset/sitemap:url)"/> URLs for search engine crawlers.</p>
  <table>
    <tr><th>#</th><th>URL</th><th>Priority</th><th>Change Freq</th><th>Last Modified</th></tr>
    <xsl:for-each select="sitemap:urlset/sitemap:url">
      <tr>
        <td><xsl:value-of select="position()"/></td>
        <td><a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a></td>
        <td>
          <xsl:variable name="p" select="sitemap:priority"/>
          <span>
            <xsl:attribute name="class">priority <xsl:choose>
              <xsl:when test="$p='1.0'">p10</xsl:when>
              <xsl:when test="$p='0.9'">p09</xsl:when>
              <xsl:when test="$p='0.8'">p08</xsl:when>
              <xsl:when test="$p='0.7'">p07</xsl:when>
              <xsl:when test="$p='0.6'">p06</xsl:when>
              <xsl:otherwise>p05</xsl:otherwise>
            </xsl:choose></xsl:attribute>
            <xsl:value-of select="sitemap:priority"/>
          </span>
        </td>
        <td><xsl:value-of select="sitemap:changefreq"/></td>
        <td><xsl:value-of select="substring(sitemap:lastmod,1,10)"/></td>
      </tr>
    </xsl:for-each>
  </table>
  <p id="count">Total: <xsl:value-of select="count(sitemap:urlset/sitemap:url)"/> URLs</p>
</body>
</html>
</xsl:template>
</xsl:stylesheet>'''
    xsl_path = os.path.join(ROOT, 'sitemap.xsl')
    with open(xsl_path, 'w', encoding='utf-8') as f:
        f.write(xsl)
    print('✓ Generated sitemap.xsl (browser-friendly stylesheet)')


def generate_robots_txt():
    """Generate robots.txt — allow all bots (search engines + AI crawlers)."""
    content = f"""# ============================================================
# Macro & Meals — robots.txt
# https://macroandmeals.com
# ============================================================

# Allow all crawlers (search engines, AI, social media, audit tools)
User-agent: *
Allow: /

# Sitemap location (absolute URL required)
Sitemap: {URL}/sitemap.xml

# LLM-friendly content (llmstxt.org standard)
# llms.txt: {URL}/llms.txt
# llms-full.txt: {URL}/llms-full.txt
"""
    with open(os.path.join(ROOT, 'robots.txt'), 'w') as f:
        f.write(content)
    print('✓ Generated robots.txt (allow all bots)')

def extract_page_info(html_file):
    """Extract title, description, and h1 from an HTML file."""
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    title_match = re.search(r'<title>([^<]+)</title>', content)
    title = title_match.group(1).replace(' | Macro & Meals', '').strip() if title_match else ''

    desc_match = re.search(r'name="description"\s+content="([^"]+)"', content)
    desc = desc_match.group(1).strip() if desc_match else ''

    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
    h1 = h1_match.group(1).strip() if h1_match else title

    return title, desc, h1


def generate_llms_txt():
    """Generate llms.txt and llms-full.txt following the llmstxt.org standard."""

    # Collect all pages with metadata
    pages = []
    root_index = os.path.join(ROOT, 'index.html')
    if os.path.exists(root_index):
        title, desc, h1 = extract_page_info(root_index)
        pages.append(('/', title or 'Home', desc, 'home'))

    for html_file in sorted(glob.glob(os.path.join(ROOT, '*', 'index.html'))):
        rel = os.path.relpath(html_file, ROOT)
        slug = os.path.dirname(rel)
        top_dir = slug.split(os.sep)[0]
        if top_dir in SKIP_DIRS:
            continue
        title, desc, h1 = extract_page_info(html_file)
        # Categorize
        if slug in ESSENTIAL_PAGES:
            cat = 'policy'
        elif slug.endswith(('-nutrition-calculator', '-calories-calculator')):
            cat = 'restaurant'
        elif slug.endswith('-menu'):
            cat = 'menu'
        elif slug.endswith(('-calculator', '-converter')):
            cat = 'calculator'
        elif slug.startswith('blog'):
            cat = 'blog'
        else:
            cat = 'other'
        pages.append((f'/{slug}/', title, desc, cat))

    # Blog subdirectories
    for html_file in sorted(glob.glob(os.path.join(ROOT, 'blog', '*', 'index.html'))):
        rel = os.path.relpath(html_file, ROOT)
        slug = os.path.dirname(rel)
        title, desc, h1 = extract_page_info(html_file)
        pages.append((f'/{slug}/', title, desc, 'blog'))

    # Group pages by category
    categories = {
        'calculator': [],
        'restaurant': [],
        'menu': [],
        'blog': [],
        'policy': [],
        'other': [],
    }
    for loc, title, desc, cat in pages:
        if cat != 'home':
            categories[cat].append((loc, title, desc))

    # ── llms.txt (concise summary with links) ──
    llms_lines = []
    llms_lines.append(f'# {BRAND}')
    llms_lines.append('')
    llms_lines.append(f'> {BRAND} ({URL}) provides free nutrition calculators and health tools '
                      f'for 50+ restaurants, BMI, BMR, TDEE, macros, vitamins, and more. '
                      f'All tools are free, no login required.')
    llms_lines.append('')
    llms_lines.append(f'{BRAND} helps users make informed dietary decisions with accurate '
                      f'nutrition data from popular restaurant chains and science-backed health calculators. '
                      f'The site covers restaurant nutrition analysis with meal builders, body composition '
                      f'calculators, macro and calorie tracking tools, vitamin intake guides, and pregnancy/fertility tools.')
    llms_lines.append('')

    # Health Calculators
    llms_lines.append('## Health & Fitness Calculators')
    llms_lines.append('')
    for loc, title, desc in sorted(categories['calculator'], key=lambda x: x[1]):
        line = f'- [{title}]({URL}{loc})'
        if desc:
            line += f': {desc[:120]}'
        llms_lines.append(line)
    llms_lines.append('')

    # Restaurant Calculators
    llms_lines.append('## Restaurant Nutrition Calculators')
    llms_lines.append('')
    for loc, title, desc in sorted(categories['restaurant'], key=lambda x: x[1]):
        line = f'- [{title}]({URL}{loc})'
        if desc:
            line += f': {desc[:120]}'
        llms_lines.append(line)
    llms_lines.append('')

    # Menus
    if categories['menu']:
        llms_lines.append('## Restaurant Menus')
        llms_lines.append('')
        for loc, title, desc in sorted(categories['menu'], key=lambda x: x[1]):
            line = f'- [{title}]({URL}{loc})'
            if desc:
                line += f': {desc[:120]}'
            llms_lines.append(line)
        llms_lines.append('')

    # Blog
    if categories['blog']:
        llms_lines.append('## Blog')
        llms_lines.append('')
        for loc, title, desc in sorted(categories['blog'], key=lambda x: x[1]):
            line = f'- [{title}]({URL}{loc})'
            if desc:
                line += f': {desc[:120]}'
            llms_lines.append(line)
        llms_lines.append('')

    # Optional section (policy pages)
    llms_lines.append('## Optional')
    llms_lines.append('')
    for loc, title, desc in sorted(categories['policy'], key=lambda x: x[1]):
        llms_lines.append(f'- [{title}]({URL}{loc})')
    if categories['other']:
        for loc, title, desc in sorted(categories['other'], key=lambda x: x[1]):
            llms_lines.append(f'- [{title}]({URL}{loc})')
    llms_lines.append('')

    llms_path = os.path.join(ROOT, 'llms.txt')
    with open(llms_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(llms_lines))

    # ── llms-full.txt (expanded with full descriptions) ──
    full_lines = []
    full_lines.append(f'# {BRAND} — Complete Site Reference')
    full_lines.append('')
    full_lines.append(f'> {BRAND} ({URL}) is a free nutrition and health calculator platform '
                      f'with 50+ restaurant nutrition tools, 20+ health calculators, meal builders, '
                      f'and science-backed fitness tools. No login required. All data is sourced from '
                      f'official restaurant nutrition guides and peer-reviewed health formulas.')
    full_lines.append('')
    full_lines.append('## Site Overview')
    full_lines.append('')
    full_lines.append(f'- **Domain**: {URL}')
    full_lines.append(f'- **Total Pages**: {len(pages)}')
    full_lines.append(f'- **Restaurant Calculators**: {len(categories["restaurant"])}')
    full_lines.append(f'- **Health Calculators**: {len(categories["calculator"])}')
    full_lines.append(f'- **Restaurant Menus**: {len(categories["menu"])}')
    full_lines.append(f'- **Blog Posts**: {len(categories["blog"])}')
    full_lines.append(f'- **Sitemap**: {URL}/sitemap.xml')
    full_lines.append('')

    # Detailed sections
    section_map = [
        ('Health & Fitness Calculators', 'calculator',
         'Science-backed health and fitness calculators covering BMI, BMR, TDEE, body fat, '
         'macros, vitamins, pregnancy tools, and more. Each calculator includes step-by-step '
         'instructions, formulas used, result interpretation, and FAQ.'),
        ('Restaurant Nutrition Calculators', 'restaurant',
         'Nutrition calculators for 50+ popular restaurant chains. Each tool includes full menu '
         'data with calories, protein, carbs, fat, fiber, and sodium per item. Features an '
         'interactive meal builder to track total nutrition across multiple items.'),
        ('Restaurant Menus', 'menu',
         'Browse full menus with nutrition data for popular restaurant chains.'),
        ('Blog', 'blog',
         'Expert nutrition articles, guides, and tips for healthy eating and meal planning.'),
    ]

    for section_title, cat_key, section_desc in section_map:
        if not categories[cat_key]:
            continue
        full_lines.append(f'## {section_title}')
        full_lines.append('')
        full_lines.append(section_desc)
        full_lines.append('')
        for loc, title, desc in sorted(categories[cat_key], key=lambda x: x[1]):
            full_lines.append(f'### [{title}]({URL}{loc})')
            if desc:
                full_lines.append('')
                full_lines.append(desc)
            full_lines.append('')

    # Policy pages
    full_lines.append('## Optional')
    full_lines.append('')
    full_lines.append('Legal and policy pages.')
    full_lines.append('')
    for loc, title, desc in sorted(categories['policy'], key=lambda x: x[1]):
        full_lines.append(f'- [{title}]({URL}{loc})')
    if categories['other']:
        for loc, title, desc in sorted(categories['other'], key=lambda x: x[1]):
            full_lines.append(f'- [{title}]({URL}{loc})')
    full_lines.append('')

    full_path = os.path.join(ROOT, 'llms-full.txt')
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(full_lines))

    print(f'✓ Generated llms.txt ({len(pages)} pages) and llms-full.txt')


if __name__ == '__main__':
    print('Loading components...')
    COMPONENTS = load_all_components()
    print()
    process_all_files()
    generate_sitemap()
    generate_sitemap_xsl()
    generate_robots_txt()
    generate_llms_txt()
    print(f'\n✅ Build complete! ({len(COMPONENTS)} components loaded)')
