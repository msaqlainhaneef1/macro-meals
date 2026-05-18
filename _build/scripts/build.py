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
    # Remove old deferred analytics block (will be re-added from component)
    html = re.sub(r"<script>\s*window\.addEventListener\('load'.*?</script>\s*", '', html, flags=re.DOTALL)
    html = re.sub(r'<meta name="google-site-verification"[^>]*/?>\s*', '', html)
    # Remove old favicon/manifest/theme-color tags (will be re-added from component)
    html = re.sub(r'<link rel="icon"[^>]*/?>\s*', '', html)
    html = re.sub(r'<link rel="apple-touch-icon"[^>]*/?>\s*', '', html)
    html = re.sub(r'<link rel="manifest"[^>]*/?>\s*', '', html)
    html = re.sub(r'<meta name="theme-color"[^>]*/?>\s*', '', html)
    # Remove old stylesheet links to avoid duplicates
    html = re.sub(r'<link rel="stylesheet" href="/css/style\.css"[^>]*>\s*', '', html)
    # Remove old Google Fonts link to avoid duplicates
    html = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>\s*', '', html)
    # Remove old preload tags to avoid duplicates
    html = re.sub(r'<link rel="preload"[^>]*>\s*', '', html)
    # Remove old preconnect/dns-prefetch to avoid duplicates
    html = re.sub(r'<link rel="preconnect"[^>]*>\s*', '', html)
    html = re.sub(r'<link rel="dns-prefetch"[^>]*>\s*', '', html)
    # Remove old LLM discoverability tags to avoid duplicates
    html = re.sub(r'<link rel="alternate" type="text/plain" href="/llms[^"]*"[^>]*>\s*', '', html)
    html = re.sub(r'<meta name="llms:[^"]*"[^>]*/?>\s*', '', html)
    # Remove HTML comment blocks for LLM discoverability and DNS prefetch
    html = re.sub(r'<!-- LLM Discoverability[^>]*-->\s*', '', html)
    html = re.sub(r'<!-- DNS Prefetch[^>]*-->\s*', '', html)
    # Inject component before </head>
    html = html.replace('</head>', head_common + '\n</head>')
    return html

def ensure_common_scripts(html):
    """Ensure common script tags are present from component."""
    scripts = COMPONENTS.get('scripts.html', '')
    if not scripts:
        return html
    # Remove old script tags (with or without defer) to avoid duplicates
    html = re.sub(r'<script\s[^>]*src="/js/site-config\.js"[^>]*></script>\s*', '', html)
    html = re.sub(r'<script\s[^>]*src="/js/scripts-config\.js"[^>]*></script>\s*', '', html)
    html = re.sub(r'<script\s[^>]*src="/js/main\.js"[^>]*></script>\s*', '', html)
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

# Only error pages should NOT get breadcrumbs or share buttons
NO_BREADCRUMBS_SHARE = {
    '404.html',
    'index.html',
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

def inject_skip_to_content(html):
    """Remove any skip-to-content links (no longer used)."""
    html = re.sub(r'<a class="skip-to-content"[^>]*>[^<]*</a>\s*', '', html)
    return html

def optimize_images(html):
    """Add loading=lazy and decoding=async to below-fold images."""
    def add_lazy(match):
        tag = match.group(0)
        if 'loading=' in tag:
            return tag
        # Skip above-the-fold logo in header (has fetchpriority or class="logo-img" in header)
        if 'fetchpriority' in tag:
            return tag
        # Skip logos that already have loading=lazy (footer logo from component)
        if 'logo' in tag.lower() and 'loading="lazy"' in tag:
            return tag
        # Header logo — don't add lazy
        if 'class="logo-img"' in tag and 'loading=' not in tag and 'fetchpriority' not in tag:
            return tag
        tag = tag.replace('<img ', '<img loading="lazy" decoding="async" ')
        return tag
    html = re.sub(r'<img\s[^>]+>', add_lazy, html)
    return html

def add_script_defer(html):
    """Add defer attribute to common script tags only.
    
    Only defers the three common scripts (site-config, scripts-config, main).
    Page-specific scripts like calculator.js and restaurant.js are NOT deferred
    because inline scripts immediately after them depend on their functions.
    Also removes defer from page-specific scripts if previously added.
    """
    safe_to_defer = ['site-config.js', 'scripts-config.js', 'main.js']
    def fix_defer(match):
        tag = match.group(0)
        if 'src=' not in tag:
            return tag
        is_safe = any(s in tag for s in safe_to_defer)
        if is_safe:
            if 'defer' not in tag and 'async' not in tag:
                tag = tag.replace('<script ', '<script defer ')
        else:
            # Remove defer from page-specific scripts (they have inline dependents)
            tag = tag.replace(' defer ', ' ').replace(' defer"', '"').replace('"defer ', '"')
            tag = re.sub(r'\s+defer(?=[\s>])', '', tag)
        return tag
    html = re.sub(r'<script\s[^>]*src=[^>]*></script>', fix_defer, html)
    return html

# ---------------------------------------------------------------------------
# Internal Linking System — auto-generates related links for every page
# ---------------------------------------------------------------------------

# Page metadata: slug → {title, icon, cat, tags}
# Tags drive relevancy scoring. Pages sharing more tags rank higher.
PAGE_DATA = {
    # --- Restaurant Nutrition Calculators ---
    'starbucks-nutrition-calculator': {'title': 'Starbucks Nutrition Calculator', 'icon': '☕', 'cat': 'nutrition', 'tags': {'coffee', 'drinks', 'restaurant', 'fast-food', 'calories'}},
    'chipotle-nutrition-calculator': {'title': 'Chipotle Nutrition Calculator', 'icon': '🌯', 'cat': 'nutrition', 'tags': {'mexican', 'burrito', 'bowl', 'restaurant', 'fast-food', 'calories'}},
    'wawa-nutrition-calculator': {'title': 'Wawa Nutrition Calculator', 'icon': '🏪', 'cat': 'nutrition', 'tags': {'convenience', 'sandwich', 'restaurant', 'fast-food', 'calories'}},
    'whataburger-nutrition-calculator': {'title': 'Whataburger Nutrition Calculator', 'icon': '🍔', 'cat': 'nutrition', 'tags': {'burger', 'restaurant', 'fast-food', 'calories'}},
    'mcdonalds-calories-calculator': {'title': "McDonald's Nutrition Calculator", 'icon': '🍟', 'cat': 'nutrition', 'tags': {'burger', 'fries', 'restaurant', 'fast-food', 'calories'}},
    'subway-nutrition-calculator': {'title': 'Subway Nutrition Calculator', 'icon': '🥖', 'cat': 'nutrition', 'tags': {'sandwich', 'sub', 'restaurant', 'fast-food', 'calories'}},
    'taco-bell-nutrition-calculator': {'title': 'Taco Bell Nutrition Calculator', 'icon': '🌮', 'cat': 'nutrition', 'tags': {'mexican', 'taco', 'restaurant', 'fast-food', 'calories'}},
    'five-guys-nutrition-calculator': {'title': 'Five Guys Nutrition Calculator', 'icon': '🍔', 'cat': 'nutrition', 'tags': {'burger', 'fries', 'restaurant', 'fast-food', 'calories'}},
    'panda-express-nutrition-calculator': {'title': 'Panda Express Nutrition Calculator', 'icon': '🥡', 'cat': 'nutrition', 'tags': {'asian', 'chinese', 'restaurant', 'fast-food', 'calories'}},
    'qdoba-nutrition-calculator': {'title': 'Qdoba Nutrition Calculator', 'icon': '🌯', 'cat': 'nutrition', 'tags': {'mexican', 'burrito', 'restaurant', 'fast-food', 'calories'}},
    'arbys-nutrition-calculator': {'title': "Arby's Nutrition Calculator", 'icon': '🥩', 'cat': 'nutrition', 'tags': {'sandwich', 'roast-beef', 'restaurant', 'fast-food', 'calories'}},
    'dutch-bros-nutrition-calculator': {'title': 'Dutch Bros Nutrition Calculator', 'icon': '☕', 'cat': 'nutrition', 'tags': {'coffee', 'drinks', 'restaurant', 'fast-food', 'calories'}},
    'sheetz-nutrition-calculator': {'title': 'Sheetz Nutrition Calculator', 'icon': '🏪', 'cat': 'nutrition', 'tags': {'convenience', 'sandwich', 'restaurant', 'fast-food', 'calories'}},
    'papa-johns-nutrition-calculator': {'title': "Papa John's Nutrition Calculator", 'icon': '🍕', 'cat': 'nutrition', 'tags': {'pizza', 'restaurant', 'fast-food', 'calories'}},
    'mod-pizza-calories-calculator': {'title': 'MOD Pizza Nutrition Calculator', 'icon': '🍕', 'cat': 'nutrition', 'tags': {'pizza', 'restaurant', 'fast-food', 'calories'}},
    'wingstop-calories-calculator': {'title': 'Wingstop Calories Calculator', 'icon': '🍗', 'cat': 'nutrition', 'tags': {'chicken', 'wings', 'restaurant', 'fast-food', 'calories'}},
    'blaze-pizza-calories-calculator': {'title': 'Blaze Pizza Nutrition Calculator', 'icon': '🍕', 'cat': 'nutrition', 'tags': {'pizza', 'restaurant', 'fast-food', 'calories'}},
    'burger-king-calories-calculator': {'title': 'Burger King Nutrition Calculator', 'icon': '🍔', 'cat': 'nutrition', 'tags': {'burger', 'fries', 'restaurant', 'fast-food', 'calories'}},
    'cupbop-nutrition-calculator': {'title': 'Cupbop Nutrition Calculator', 'icon': '🍜', 'cat': 'nutrition', 'tags': {'asian', 'korean', 'restaurant', 'fast-food', 'calories'}},
    'salad-master-nutrition-calculator': {'title': 'Salad Master Nutrition Calculator', 'icon': '🥗', 'cat': 'nutrition', 'tags': {'salad', 'healthy', 'restaurant', 'fast-food', 'calories'}},
    'cava-nutrition-calculator': {'title': 'CAVA Nutrition Calculator', 'icon': '🥙', 'cat': 'nutrition', 'tags': {'mediterranean', 'bowl', 'healthy', 'restaurant', 'fast-food', 'calories'}},
    'naked-juice-nutrition-calculator': {'title': 'Naked Juice Nutrition Calculator', 'icon': '🥤', 'cat': 'nutrition', 'tags': {'juice', 'drinks', 'smoothie', 'restaurant', 'calories'}},
    'jersey-mikes-calories-calculator': {'title': "Jersey Mike's Nutrition Calculator", 'icon': '🥖', 'cat': 'nutrition', 'tags': {'sandwich', 'sub', 'restaurant', 'fast-food', 'calories'}},
    'cafe-rio-calories-calculator': {'title': 'Cafe Rio Nutrition Calculator', 'icon': '🌯', 'cat': 'nutrition', 'tags': {'mexican', 'burrito', 'restaurant', 'fast-food', 'calories'}},
    'bibibop-calories-calculator': {'title': 'BIBIBOP Nutrition Calculator', 'icon': '🍚', 'cat': 'nutrition', 'tags': {'asian', 'korean', 'bowl', 'restaurant', 'fast-food', 'calories'}},
    'carls-jr-calories-calculator': {'title': "Carl's Jr Nutrition Calculator", 'icon': '🍔', 'cat': 'nutrition', 'tags': {'burger', 'restaurant', 'fast-food', 'calories'}},
    'chilis-calories-calculator': {'title': "Chili's Nutrition Calculator", 'icon': '🌶️', 'cat': 'nutrition', 'tags': {'casual-dining', 'restaurant', 'calories'}},
    'applebees-nutrition-calculator': {'title': "Applebee's Nutrition Calculator", 'icon': '🍎', 'cat': 'nutrition', 'tags': {'casual-dining', 'restaurant', 'calories'}},
    'daves-hot-chicken-nutrition-calculator': {'title': "Dave's Hot Chicken Nutrition Calculator", 'icon': '🍗', 'cat': 'nutrition', 'tags': {'chicken', 'spicy', 'restaurant', 'fast-food', 'calories'}},
    'albaik-nutrition-calculator': {'title': 'Al Baik Nutrition Calculator', 'icon': '🍗', 'cat': 'nutrition', 'tags': {'chicken', 'restaurant', 'fast-food', 'calories'}},
    'bolay-nutrition-calculator': {'title': 'Bolay Nutrition Calculator', 'icon': '🥗', 'cat': 'nutrition', 'tags': {'bowl', 'healthy', 'restaurant', 'fast-food', 'calories'}},
    'bolthouse-farms-nutrition-calculator': {'title': 'Bolthouse Farms Nutrition Calculator', 'icon': '🥤', 'cat': 'nutrition', 'tags': {'juice', 'drinks', 'smoothie', 'healthy', 'calories'}},
    'brassica-nutrition-calculator': {'title': 'Brassica Nutrition Calculator', 'icon': '🥗', 'cat': 'nutrition', 'tags': {'salad', 'healthy', 'restaurant', 'fast-food', 'calories'}},
    'black-rock-coffee-nutrition-calculator': {'title': 'Black Rock Coffee Nutrition Calculator', 'icon': '☕', 'cat': 'nutrition', 'tags': {'coffee', 'drinks', 'restaurant', 'calories'}},
    'blank-street-coffee-calories-calculator': {'title': 'Blank Street Coffee Nutrition Calculator', 'icon': '☕', 'cat': 'nutrition', 'tags': {'coffee', 'drinks', 'restaurant', 'calories'}},
    'dig-nutrition-calculator': {'title': 'Dig Nutrition Calculator', 'icon': '🥗', 'cat': 'nutrition', 'tags': {'healthy', 'bowl', 'restaurant', 'fast-food', 'calories'}},
    'smoothie-king-nutrition-calculator': {'title': 'Smoothie King Nutrition Calculator', 'icon': '🥤', 'cat': 'nutrition', 'tags': {'smoothie', 'drinks', 'healthy', 'restaurant', 'calories'}},
    'sonic-drive-in-nutrition-calculator': {'title': 'Sonic Drive-In Nutrition Calculator', 'icon': '🍔', 'cat': 'nutrition', 'tags': {'burger', 'drinks', 'restaurant', 'fast-food', 'calories'}},
    'wendys-nutrition-calculator': {'title': "Wendy's Nutrition Calculator", 'icon': '🍔', 'cat': 'nutrition', 'tags': {'burger', 'fries', 'restaurant', 'fast-food', 'calories'}},
    'jimmy-johns-calories-calculator': {'title': "Jimmy John's Nutrition Calculator", 'icon': '🥖', 'cat': 'nutrition', 'tags': {'sandwich', 'sub', 'restaurant', 'fast-food', 'calories'}},
    'raising-canes-calculator': {'title': "Raising Cane's Nutrition Calculator", 'icon': '🍗', 'cat': 'nutrition', 'tags': {'chicken', 'restaurant', 'fast-food', 'calories'}},
    'tropical-smoothie-cafe-nutrition-calculator': {'title': 'Tropical Smoothie Cafe Nutrition Calculator', 'icon': '🥤', 'cat': 'nutrition', 'tags': {'smoothie', 'drinks', 'healthy', 'restaurant', 'calories'}},
    'sweetgreen-nutrition-calculator': {'title': 'Sweetgreen Nutrition Calculator', 'icon': '🥗', 'cat': 'nutrition', 'tags': {'salad', 'healthy', 'bowl', 'restaurant', 'calories'}},
    'nandos-nutrition-calculator': {'title': "Nando's Nutrition Calculator", 'icon': '🍗', 'cat': 'nutrition', 'tags': {'chicken', 'restaurant', 'fast-food', 'calories'}},
    'mellow-mushroom-nutrition-calculator': {'title': 'Mellow Mushroom Nutrition Calculator', 'icon': '🍕', 'cat': 'nutrition', 'tags': {'pizza', 'restaurant', 'casual-dining', 'calories'}},
    'mucho-burrito-nutrition-calculator': {'title': 'Mucho Burrito Nutrition Calculator', 'icon': '🌯', 'cat': 'nutrition', 'tags': {'mexican', 'burrito', 'restaurant', 'fast-food', 'calories'}},
    'nifty-fifty-nutrition-calculator': {'title': 'Nifty Fifty Nutrition Calculator', 'icon': '🍔', 'cat': 'nutrition', 'tags': {'burger', 'retro', 'restaurant', 'calories'}},
    'jamba-juice-nutrition-calculator': {'title': 'Jamba Juice Nutrition Calculator', 'icon': '🥤', 'cat': 'nutrition', 'tags': {'juice', 'smoothie', 'drinks', 'healthy', 'restaurant', 'calories'}},
    'via-313-nutrition-calculator': {'title': 'Via 313 Nutrition Calculator', 'icon': '🍕', 'cat': 'nutrition', 'tags': {'pizza', 'restaurant', 'calories'}},
    'zao-asian-cafe-nutrition-calculator': {'title': 'Zao Asian Cafe Nutrition Calculator', 'icon': '🍜', 'cat': 'nutrition', 'tags': {'asian', 'restaurant', 'fast-food', 'calories'}},
    'taim-mediterranean-kitchen-nutrition-calculator': {'title': 'Taim Mediterranean Kitchen Nutrition Calculator', 'icon': '🥙', 'cat': 'nutrition', 'tags': {'mediterranean', 'healthy', 'restaurant', 'calories'}},
    'outback-steakhouse-menu': {'title': 'Outback Steakhouse Menu', 'icon': '🥩', 'cat': 'nutrition', 'tags': {'steak', 'casual-dining', 'restaurant', 'calories'}},

    # --- Restaurant Menus ---
    'chipotle-menu': {'title': 'Chipotle Menu', 'icon': '🌯', 'cat': 'menu', 'tags': {'mexican', 'burrito', 'menu', 'restaurant'}},
    'dutch-bros-menu': {'title': 'Dutch Bros Menu', 'icon': '☕', 'cat': 'menu', 'tags': {'coffee', 'drinks', 'menu', 'restaurant'}},
    'five-guys-menu': {'title': 'Five Guys Menu', 'icon': '🍔', 'cat': 'menu', 'tags': {'burger', 'fries', 'menu', 'restaurant'}},
    'starbucks-menu': {'title': 'Starbucks Menu', 'icon': '☕', 'cat': 'menu', 'tags': {'coffee', 'drinks', 'menu', 'restaurant'}},
    'taco-bell-menu': {'title': 'Taco Bell Menu', 'icon': '🌮', 'cat': 'menu', 'tags': {'mexican', 'taco', 'menu', 'restaurant'}},
    'panda-express-menu': {'title': 'Panda Express Menu', 'icon': '🥡', 'cat': 'menu', 'tags': {'asian', 'chinese', 'menu', 'restaurant'}},
    'qdoba-menu': {'title': 'Qdoba Menu', 'icon': '🌯', 'cat': 'menu', 'tags': {'mexican', 'burrito', 'menu', 'restaurant'}},
    'sheetz-menu': {'title': 'Sheetz Menu', 'icon': '🏪', 'cat': 'menu', 'tags': {'convenience', 'sandwich', 'menu', 'restaurant'}},
    'wawa-menu': {'title': 'Wawa Menu', 'icon': '🏪', 'cat': 'menu', 'tags': {'convenience', 'sandwich', 'menu', 'restaurant'}},
    'whataburger-menu': {'title': 'Whataburger Menu', 'icon': '🍔', 'cat': 'menu', 'tags': {'burger', 'menu', 'restaurant'}},
    'sushi-menu': {'title': 'Sushi Menu', 'icon': '🍣', 'cat': 'menu', 'tags': {'sushi', 'japanese', 'menu', 'restaurant'}},

    # --- Body Composition & Health ---
    'bmi-calculator': {'title': 'BMI Calculator', 'icon': '⚖️', 'cat': 'body', 'tags': {'bmi', 'weight', 'health', 'body-composition', 'obesity'}},
    'bmi-nih-calculator': {'title': 'BMI NIH Calculator', 'icon': '⚖️', 'cat': 'body', 'tags': {'bmi', 'weight', 'health', 'body-composition', 'nih'}},
    'bmr-calculator': {'title': 'BMR Calculator', 'icon': '🔥', 'cat': 'body', 'tags': {'bmr', 'metabolism', 'calories', 'energy', 'body-composition'}},
    'body-fat-calculator': {'title': 'Body Fat Calculator', 'icon': '📊', 'cat': 'body', 'tags': {'body-fat', 'body-composition', 'weight', 'fitness'}},
    'body-shape-calculator': {'title': 'Body Shape Calculator', 'icon': '📐', 'cat': 'body', 'tags': {'body-shape', 'body-composition', 'measurements'}},
    'ffmi-calculator': {'title': 'FFMI Calculator', 'icon': '💪', 'cat': 'body', 'tags': {'ffmi', 'muscle', 'fitness', 'body-composition', 'bodybuilding'}},
    'bsa-calculator': {'title': 'BSA Calculator', 'icon': '📏', 'cat': 'body', 'tags': {'bsa', 'body-surface', 'medical', 'body-composition'}},
    'bri-calculator': {'title': 'BRI Calculator', 'icon': '📊', 'cat': 'body', 'tags': {'bri', 'body-roundness', 'health', 'body-composition'}},
    'absi-calculator': {'title': 'ABSI Calculator', 'icon': '📊', 'cat': 'body', 'tags': {'absi', 'body-shape', 'health', 'body-composition'}},
    'army-body-fat-calculator': {'title': 'Army Body Fat Calculator', 'icon': '🎖️', 'cat': 'body', 'tags': {'body-fat', 'military', 'fitness', 'body-composition'}},
    'us-marine-body-fat-calculator': {'title': 'US Marine Body Fat Calculator', 'icon': '🎖️', 'cat': 'body', 'tags': {'body-fat', 'military', 'fitness', 'body-composition'}},
    'anorexic-bmi-calculator': {'title': 'Anorexic BMI Calculator', 'icon': '⚖️', 'cat': 'body', 'tags': {'bmi', 'underweight', 'eating-disorder', 'health'}},
    'face-shape-calculator': {'title': 'Face Shape Calculator', 'icon': '😊', 'cat': 'body', 'tags': {'face', 'shape', 'measurements', 'body-composition'}},
    'ideal-body-weight-calculator': {'title': 'Ideal Body Weight Calculator', 'icon': '⚖️', 'cat': 'body', 'tags': {'weight', 'ideal', 'health', 'body-composition'}},
    'lean-body-mass-calculator': {'title': 'Lean Body Mass Calculator', 'icon': '💪', 'cat': 'body', 'tags': {'lean-mass', 'muscle', 'body-fat', 'body-composition', 'fitness'}},
    'overweight-calculator': {'title': 'Overweight Calculator', 'icon': '⚖️', 'cat': 'body', 'tags': {'weight', 'bmi', 'obesity', 'health'}},
    'waist-to-hip-ratio-calculator': {'title': 'Waist to Hip Ratio Calculator', 'icon': '📏', 'cat': 'body', 'tags': {'waist', 'hip', 'body-fat', 'health', 'body-composition'}},
    'skinfold-body-fat-calculator': {'title': 'Skinfold Body Fat Calculator', 'icon': '📊', 'cat': 'body', 'tags': {'body-fat', 'skinfold', 'fitness', 'body-composition'}},
    'height-calculator': {'title': 'Height Calculator', 'icon': '📏', 'cat': 'body', 'tags': {'height', 'growth', 'children', 'body-composition'}},
    'bedridden-patient-height-calculator': {'title': 'Bedridden Patient Height Calculator', 'icon': '🏥', 'cat': 'body', 'tags': {'height', 'medical', 'patient', 'body-composition'}},
    'baby-percentile-calculator': {'title': 'Baby Percentile Calculator', 'icon': '👶', 'cat': 'body', 'tags': {'baby', 'growth', 'percentile', 'children', 'health'}},
    'gfr-calculator': {'title': 'GFR Calculator', 'icon': '🩺', 'cat': 'body', 'tags': {'gfr', 'kidney', 'medical', 'health'}},
    'karvonen-formula-calculator': {'title': 'Karvonen Formula Calculator', 'icon': '❤️', 'cat': 'body', 'tags': {'heart-rate', 'cardio', 'fitness', 'exercise'}},
    'one-rep-max-calculator': {'title': 'One Rep Max Calculator', 'icon': '🏋️', 'cat': 'body', 'tags': {'strength', 'weightlifting', 'fitness', 'exercise'}},

    # --- Diet & Macro Calculators ---
    'tdee-calculator': {'title': 'TDEE Calculator', 'icon': '⚡', 'cat': 'diet', 'tags': {'tdee', 'calories', 'energy', 'metabolism', 'weight-loss'}},
    'calorie-deficit-calculator': {'title': 'Calorie Deficit Calculator', 'icon': '📉', 'cat': 'diet', 'tags': {'calorie-deficit', 'weight-loss', 'calories', 'diet'}},
    'protein-calculator': {'title': 'Protein Calculator', 'icon': '🥩', 'cat': 'diet', 'tags': {'protein', 'macros', 'muscle', 'diet', 'nutrition'}},
    'carbohydrate-calculator': {'title': 'Carbohydrate Calculator', 'icon': '🍞', 'cat': 'diet', 'tags': {'carbs', 'macros', 'diet', 'nutrition'}},
    'keto-macro-calculator': {'title': 'Keto Macro Calculator', 'icon': '🥑', 'cat': 'diet', 'tags': {'keto', 'macros', 'low-carb', 'diet', 'weight-loss'}},
    'macro-calculator-for-weight-loss': {'title': 'Macro Calculator for Weight Loss', 'icon': '📊', 'cat': 'diet', 'tags': {'macros', 'weight-loss', 'diet', 'calories'}},
    'water-fasting-calculator': {'title': 'Water Fasting Calculator', 'icon': '💧', 'cat': 'diet', 'tags': {'fasting', 'water', 'weight-loss', 'diet'}},
    'protein-molecular-weight-calculator': {'title': 'Protein Molecular Weight Calculator', 'icon': '🔬', 'cat': 'diet', 'tags': {'protein', 'molecular', 'science', 'biochemistry'}},
    'steps-to-calories-calculator': {'title': 'Steps to Calories Calculator', 'icon': '👣', 'cat': 'diet', 'tags': {'steps', 'calories', 'walking', 'exercise', 'fitness'}},
    'steps-to-miles-calculator': {'title': 'Steps to Miles Calculator', 'icon': '👣', 'cat': 'diet', 'tags': {'steps', 'miles', 'walking', 'exercise', 'distance'}},
    'kj-to-calories-converter': {'title': 'kJ to Calories Converter', 'icon': '🔄', 'cat': 'diet', 'tags': {'conversion', 'calories', 'kilojoules', 'energy'}},
    'maintenance-fluid-calculator': {'title': 'Maintenance Fluid Calculator', 'icon': '💧', 'cat': 'diet', 'tags': {'fluid', 'hydration', 'medical', 'health'}},

    # --- Vitamins & Micronutrients ---
    'vitamin-a-calculator': {'title': 'Vitamin A Calculator', 'icon': '💊', 'cat': 'vitamins', 'tags': {'vitamin-a', 'vitamins', 'micronutrients', 'health'}},
    'vitamin-b-calculator': {'title': 'Vitamin B Calculator', 'icon': '💊', 'cat': 'vitamins', 'tags': {'vitamin-b', 'vitamins', 'micronutrients', 'health', 'energy'}},
    'vitamin-c-calculator': {'title': 'Vitamin C Calculator', 'icon': '🍊', 'cat': 'vitamins', 'tags': {'vitamin-c', 'vitamins', 'micronutrients', 'immunity', 'health'}},
    'vitamin-d-calculator': {'title': 'Vitamin D Calculator', 'icon': '☀️', 'cat': 'vitamins', 'tags': {'vitamin-d', 'vitamins', 'micronutrients', 'bone', 'health'}},
    'vitamin-e-calculator': {'title': 'Vitamin E Calculator', 'icon': '💊', 'cat': 'vitamins', 'tags': {'vitamin-e', 'vitamins', 'micronutrients', 'antioxidant', 'health'}},
    'vitamin-k-calculator': {'title': 'Vitamin K Calculator', 'icon': '💊', 'cat': 'vitamins', 'tags': {'vitamin-k', 'vitamins', 'micronutrients', 'blood', 'health'}},
    'cholesterol-ratio-calculator': {'title': 'Cholesterol Ratio Calculator', 'icon': '🩺', 'cat': 'vitamins', 'tags': {'cholesterol', 'heart', 'health', 'lipids'}},
    'ldl-cholesterol-calculator': {'title': 'LDL Cholesterol Calculator', 'icon': '🩺', 'cat': 'vitamins', 'tags': {'cholesterol', 'ldl', 'heart', 'health', 'lipids'}},

    # --- Pregnancy & Specialty ---
    'due-date-calculator': {'title': 'Due Date Calculator', 'icon': '📅', 'cat': 'pregnancy', 'tags': {'pregnancy', 'due-date', 'baby', 'health'}},
    'conception-calculator': {'title': 'Conception Calculator', 'icon': '📅', 'cat': 'pregnancy', 'tags': {'conception', 'pregnancy', 'fertility', 'health'}},
    'ovulation-calculator': {'title': 'Ovulation Calculator', 'icon': '📅', 'cat': 'pregnancy', 'tags': {'ovulation', 'fertility', 'pregnancy', 'cycle'}},
    'pregnancy-calculator': {'title': 'Pregnancy Calculator', 'icon': '🤰', 'cat': 'pregnancy', 'tags': {'pregnancy', 'trimester', 'baby', 'health'}},
    'pregnancy-weight-gain-calculator': {'title': 'Pregnancy Weight Gain Calculator', 'icon': '⚖️', 'cat': 'pregnancy', 'tags': {'pregnancy', 'weight', 'health', 'baby'}},
    'menses-calculator': {'title': 'Menses Calculator', 'icon': '📅', 'cat': 'pregnancy', 'tags': {'period', 'cycle', 'menstruation', 'health'}},
    'ivf-success-rate-calculator': {'title': 'IVF Success Rate Calculator', 'icon': '🏥', 'cat': 'pregnancy', 'tags': {'ivf', 'fertility', 'pregnancy', 'medical'}},

    # --- Essential/Utility pages ---
    'about': {'title': 'About Macro & Meals', 'icon': 'ℹ️', 'cat': 'essential', 'tags': {'about', 'company'}},
    'contact': {'title': 'Contact Us', 'icon': '📧', 'cat': 'essential', 'tags': {'contact', 'support'}},
    'privacy-policy': {'title': 'Privacy Policy', 'icon': '🔒', 'cat': 'legal', 'tags': {'privacy', 'legal'}},
    'terms-conditions': {'title': 'Terms & Conditions', 'icon': '📜', 'cat': 'legal', 'tags': {'terms', 'legal'}},
    'disclaimer': {'title': 'Disclaimer', 'icon': '⚠️', 'cat': 'legal', 'tags': {'disclaimer', 'legal'}},
    'cookie-policy': {'title': 'Cookie Policy', 'icon': '🍪', 'cat': 'legal', 'tags': {'cookies', 'legal', 'privacy'}},
    'dmca': {'title': 'DMCA', 'icon': '©️', 'cat': 'legal', 'tags': {'dmca', 'legal', 'copyright'}},
    'accessibility': {'title': 'Accessibility', 'icon': '♿', 'cat': 'legal', 'tags': {'accessibility', 'legal'}},
    'sitemap-page': {'title': 'Sitemap', 'icon': '🗺️', 'cat': 'essential', 'tags': {'sitemap', 'navigation'}},
    'blog': {'title': 'Blog', 'icon': '📝', 'cat': 'blog', 'tags': {'blog', 'articles', 'nutrition'}},
    'blog/how-to-calculate-your-daily-calorie-needs': {'title': 'How to Calculate Your Daily Calorie Needs', 'icon': '📝', 'cat': 'blog', 'tags': {'blog', 'calories', 'tdee', 'nutrition', 'weight-loss', 'diet'}},
}

# Expert cross-category links: manually curated high-value connections
CROSS_LINKS = {
    'bmi-calculator': ['body-fat-calculator', 'ideal-body-weight-calculator', 'tdee-calculator', 'bmr-calculator', 'overweight-calculator'],
    'bmr-calculator': ['tdee-calculator', 'calorie-deficit-calculator', 'bmi-calculator', 'macro-calculator-for-weight-loss'],
    'tdee-calculator': ['calorie-deficit-calculator', 'bmr-calculator', 'macro-calculator-for-weight-loss', 'protein-calculator'],
    'calorie-deficit-calculator': ['tdee-calculator', 'macro-calculator-for-weight-loss', 'keto-macro-calculator', 'bmr-calculator'],
    'protein-calculator': ['macro-calculator-for-weight-loss', 'keto-macro-calculator', 'tdee-calculator', 'calorie-deficit-calculator'],
    'keto-macro-calculator': ['macro-calculator-for-weight-loss', 'calorie-deficit-calculator', 'protein-calculator', 'tdee-calculator'],
    'body-fat-calculator': ['bmi-calculator', 'lean-body-mass-calculator', 'skinfold-body-fat-calculator', 'ffmi-calculator'],
    'ideal-body-weight-calculator': ['bmi-calculator', 'body-fat-calculator', 'overweight-calculator', 'bmr-calculator'],
    'lean-body-mass-calculator': ['body-fat-calculator', 'ffmi-calculator', 'protein-calculator', 'bmi-calculator'],
    'ffmi-calculator': ['lean-body-mass-calculator', 'body-fat-calculator', 'one-rep-max-calculator', 'protein-calculator'],
    'waist-to-hip-ratio-calculator': ['body-fat-calculator', 'bmi-calculator', 'body-shape-calculator', 'absi-calculator'],
    'steps-to-calories-calculator': ['steps-to-miles-calculator', 'tdee-calculator', 'calorie-deficit-calculator'],
    'steps-to-miles-calculator': ['steps-to-calories-calculator', 'tdee-calculator'],
    'cholesterol-ratio-calculator': ['ldl-cholesterol-calculator', 'bmi-calculator', 'body-fat-calculator'],
    'ldl-cholesterol-calculator': ['cholesterol-ratio-calculator', 'bmi-calculator'],
    'due-date-calculator': ['pregnancy-calculator', 'conception-calculator', 'pregnancy-weight-gain-calculator'],
    'pregnancy-calculator': ['due-date-calculator', 'pregnancy-weight-gain-calculator', 'conception-calculator'],
    'ovulation-calculator': ['conception-calculator', 'menses-calculator', 'due-date-calculator'],
    'conception-calculator': ['ovulation-calculator', 'due-date-calculator', 'pregnancy-calculator'],
    'menses-calculator': ['ovulation-calculator', 'conception-calculator', 'due-date-calculator'],
    # Ensure no orphan pages — connect niche pages to related ones
    'nifty-fifty-nutrition-calculator': ['burger-king-calories-calculator', 'sonic-drive-in-nutrition-calculator', 'five-guys-nutrition-calculator'],
    'via-313-nutrition-calculator': ['blaze-pizza-calories-calculator', 'mod-pizza-calories-calculator', 'papa-johns-nutrition-calculator'],
    'taim-mediterranean-kitchen-nutrition-calculator': ['cava-nutrition-calculator', 'sweetgreen-nutrition-calculator', 'dig-nutrition-calculator'],
    'protein-molecular-weight-calculator': ['protein-calculator', 'macro-calculator-for-weight-loss'],
    'sushi-menu': ['panda-express-menu', 'zao-asian-cafe-nutrition-calculator'],
}

# Menu ↔ Calculator pairings
MENU_CALC_PAIRS = {
    'chipotle-menu': 'chipotle-nutrition-calculator',
    'dutch-bros-menu': 'dutch-bros-nutrition-calculator',
    'five-guys-menu': 'five-guys-nutrition-calculator',
    'starbucks-menu': 'starbucks-nutrition-calculator',
    'taco-bell-menu': 'taco-bell-nutrition-calculator',
    'panda-express-menu': 'panda-express-nutrition-calculator',
    'qdoba-menu': 'qdoba-nutrition-calculator',
    'sheetz-menu': 'sheetz-nutrition-calculator',
    'wawa-menu': 'wawa-nutrition-calculator',
    'whataburger-menu': 'whataburger-nutrition-calculator',
}

# Category display labels
CAT_DISPLAY = {
    'nutrition': '🍔 Restaurant Nutrition Calculators',
    'menu': '📋 Restaurant Menus',
    'body': '⚖️ Body Composition & Health',
    'diet': '🥩 Diet & Macro Calculators',
    'vitamins': '💊 Vitamins & Micronutrients',
    'pregnancy': '🤰 Pregnancy & Specialty',
}


def get_related_pages(slug, count=6):
    """Return top related pages for a given slug using tag-based relevancy scoring."""
    if slug not in PAGE_DATA:
        return []
    
    current = PAGE_DATA[slug]
    current_tags = current.get('tags', set())
    current_cat = current.get('cat', '')
    
    # Score all other pages
    scores = []
    for other_slug, other_data in PAGE_DATA.items():
        if other_slug == slug:
            continue
        # Skip legal/essential pages from related suggestions
        if other_data.get('cat') in ('legal', 'essential'):
            continue
        
        other_tags = other_data.get('tags', set())
        other_cat = other_data.get('cat', '')
        
        # Tag overlap score (primary relevancy signal)
        shared = len(current_tags & other_tags)
        score = shared * 10
        
        # Same category bonus
        if current_cat == other_cat:
            score += 5
        
        # Cross-link bonus (expert-curated connections, bidirectional)
        if slug in CROSS_LINKS and other_slug in CROSS_LINKS[slug]:
            score += 20
        if other_slug in CROSS_LINKS and slug in CROSS_LINKS[other_slug]:
            score += 20
        
        # Menu ↔ Calculator bonus
        if slug in MENU_CALC_PAIRS and MENU_CALC_PAIRS[slug] == other_slug:
            score += 25
        inv_pairs = {v: k for k, v in MENU_CALC_PAIRS.items()}
        if slug in inv_pairs and inv_pairs[slug] == other_slug:
            score += 25
        
        if score > 0:
            scores.append((score, other_slug, other_data))
    
    # Sort by score descending, then alphabetically for ties
    scores.sort(key=lambda x: (-x[0], x[1]))
    return [(s, d) for _, s, d in scores[:count]]


def inject_internal_links(html, filepath):
    """Inject internal linking section into every page."""
    slug = os.path.relpath(os.path.dirname(filepath), ROOT)
    if slug == '.':
        slug = ''
    
    # Skip homepage, 404
    basename = os.path.basename(filepath) if slug == '' else slug
    if basename in ('index.html', '') or slug == '':
        return html
    if '404' in filepath:
        return html
    
    # Remove any existing related section (will be regenerated)
    html = re.sub(
        r'<div class="related-section">.*?</div>\s*</div>\s*(?=</div>\s*</section>|</section>)',
        '', html, flags=re.DOTALL
    )
    # Also remove old standalone related sections
    html = re.sub(
        r'<div class="related-section">.*?</div>\s*</div>(?=\s*<footer)',
        '', html, flags=re.DOTALL
    )
    
    related = get_related_pages(slug, count=6)
    
    if not related:
        # For unknown pages, show popular calculators as fallback
        fallback_slugs = ['bmi-calculator', 'tdee-calculator', 'calorie-deficit-calculator',
                          'protein-calculator', 'chipotle-nutrition-calculator', 'starbucks-nutrition-calculator']
        related = [(s, PAGE_DATA[s]) for s in fallback_slugs if s in PAGE_DATA and s != slug]
    
    if not related:
        return html
    
    # Build the related section HTML
    cards = []
    for rel_slug, rel_data in related:
        title = rel_data['title']
        icon = rel_data['icon']
        href = f'/{rel_slug}/'
        cards.append(
            f'<a href="{href}" class="related-card">'
            f'<span class="rc-icon">{icon}</span>'
            f'<span class="rc-text">{title}</span></a>'
        )
    
    # Add "Explore All Calculators" link back to homepage
    cards.append(
        '<a href="/" class="related-card related-card-all">'
        '<span class="rc-icon">🏠</span>'
        '<span class="rc-text">All Calculators</span></a>'
    )
    
    section_html = (
        '<div class="related-section">'
        '<h2>Related Tools You May Like</h2>'
        '<div class="related-grid">'
        + ''.join(cards) +
        '</div></div>'
    )
    
    # Also build a "Category Explorer" for cross-category discovery
    current_data = PAGE_DATA.get(slug, {})
    current_cat = current_data.get('cat', '')
    
    # Pick 2-3 other categories to suggest
    other_cats = [c for c in ['body', 'diet', 'nutrition', 'vitamins', 'pregnancy']
                  if c != current_cat and c in CAT_DISPLAY][:3]
    
    if other_cats:
        cat_links = []
        for cat in other_cats:
            # Find the most popular page in that category
            cat_pages = [(s, d) for s, d in PAGE_DATA.items()
                         if d.get('cat') == cat and s in HIGH_TRAFFIC_CALCULATORS | HIGH_TRAFFIC_RESTAURANTS]
            if not cat_pages:
                cat_pages = [(s, d) for s, d in PAGE_DATA.items() if d.get('cat') == cat]
            if cat_pages:
                rep_slug, rep_data = cat_pages[0]
                label = CAT_DISPLAY.get(cat, cat)
                cat_links.append(
                    f'<a href="/{rep_slug}/" class="cat-explore-link">{label}</a>'
                )
        
        if cat_links:
            section_html += (
                '<div class="category-explorer">'
                '<h3>Explore More Categories</h3>'
                '<div class="cat-explore-grid">'
                + ''.join(cat_links) +
                '</div></div>'
            )
    
    # Inject before </section> (last one) or before <footer>
    if '</section>' in html:
        # Insert before the last </section>
        last_section = html.rfind('</section>')
        if last_section != -1:
            html = html[:last_section] + section_html + '\n' + html[last_section:]
    elif '<footer' in html:
        footer_pos = html.find('<footer')
        if footer_pos != -1:
            html = html[:footer_pos] + section_html + '\n' + html[footer_pos:]
    
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
    content = inject_skip_to_content(content)
    content = inject_announcement_bar(content)
    content = inject_scroll_progress(content)
    content = inject_breadcrumbs(content, filepath)
    content = inject_social_share(content, filepath)
    content = inject_back_to_top(content)
    content = inject_cookie_banner(content)
    content = inject_print_styles(content)
    content = inject_gtm_noscript(content)
    # Internal linking (auto-generated related pages)
    content = inject_internal_links(content, filepath)
    # Performance optimizations (safe — no design impact)
    content = optimize_images(content)
    content = add_script_defer(content)
    
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


def minify_assets():
    """Minify CSS and JS files for smaller payloads."""
    try:
        import csscompressor
        css_file = os.path.join(ROOT, 'css', 'style.css')
        if os.path.exists(css_file):
            with open(css_file, 'r', encoding='utf-8') as f:
                original = f.read()
            # Don't minify if already minified (no newlines = already minified)
            if '\n' in original and len(original) > 1000:
                minified = csscompressor.compress(original)
                with open(css_file, 'w', encoding='utf-8') as f:
                    f.write(minified)
                saved = len(original) - len(minified)
                pct = (saved / len(original)) * 100 if len(original) > 0 else 0
                print(f'  ✓ style.css: {len(original):,} → {len(minified):,} bytes ({pct:.0f}% smaller)')
            else:
                print(f'  ⏭ style.css: already minified')
    except ImportError:
        print('  ⚠ csscompressor not installed, skipping CSS minification')

    try:
        from jsmin import jsmin
        js_dir = os.path.join(ROOT, 'js')
        if os.path.isdir(js_dir):
            for js_file in sorted(glob.glob(os.path.join(js_dir, '*.js'))):
                with open(js_file, 'r', encoding='utf-8') as f:
                    original = f.read()
                if '\n' in original and len(original) > 100:
                    minified = jsmin(original)
                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(minified)
                    saved = len(original) - len(minified)
                    pct = (saved / len(original)) * 100 if len(original) > 0 else 0
                    name = os.path.basename(js_file)
                    print(f'  ✓ {name}: {len(original):,} → {len(minified):,} bytes ({pct:.0f}% smaller)')
                else:
                    print(f'  ⏭ {os.path.basename(js_file)}: already minified')
    except ImportError:
        print('  ⚠ jsmin not installed, skipping JS minification')


if __name__ == '__main__':
    print('Loading components...')
    COMPONENTS = load_all_components()
    print()
    process_all_files()
    print('\nMinifying CSS & JS...')
    minify_assets()
    generate_sitemap()
    generate_sitemap_xsl()
    generate_robots_txt()
    generate_llms_txt()
    print(f'\n✅ Build complete! ({len(COMPONENTS)} components loaded)')
