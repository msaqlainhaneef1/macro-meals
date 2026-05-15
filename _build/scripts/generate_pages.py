#!/usr/bin/env python3
"""Generate all essential pages, blog section, and update sitemap."""
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
ROOT = os.path.join(REPO_ROOT, 'public_html')
DOMAIN = 'macroandmeals.com'
URL = f'https://{DOMAIN}'
BRAND = 'Macro &amp; Meals'
BRAND_RAW = 'Macro & Meals'
YEAR = datetime.now().year

# Common header template (nav dropdowns populated by main.js)
def header():
    return '''<header class="header">
<div class="header-inner">
<a href="/" class="logo"><div class="logo-icon">MM</div>Macro &amp; Meals</a>
<nav class="nav-desktop"><button class="nav-btn" data-cat="nutrition">Nutrition Calculators <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg></button><button class="nav-btn" data-cat="menu">Menu <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg></button><button class="nav-btn" data-cat="vitamins">Vitamins &amp; Micronutrients <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg></button><button class="nav-btn" data-cat="body">Body Composition &amp; Health <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg></button><button class="nav-btn" data-cat="diet">Diet &amp; Macro Calculators <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg></button><button class="nav-btn" data-cat="pregnancy">Pregnancy &amp; Specialty <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg></button></nav>
<button class="mobile-toggle" id="mobile-toggle"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg></button>
</div>
<div class="nav-dropdown" id="dropdown-nutrition"><div class="nav-dropdown-inner"></div></div>
<div class="nav-dropdown" id="dropdown-menu"><div class="nav-dropdown-inner"></div></div>
<div class="nav-dropdown" id="dropdown-vitamins"><div class="nav-dropdown-inner"></div></div>
<div class="nav-dropdown" id="dropdown-body"><div class="nav-dropdown-inner"></div></div>
<div class="nav-dropdown" id="dropdown-diet"><div class="nav-dropdown-inner"></div></div>
<div class="nav-dropdown" id="dropdown-pregnancy"><div class="nav-dropdown-inner"></div></div>
<div class="mobile-nav" id="mobile-nav"></div>
</header>'''

def footer():
    return f'''<footer class="footer">
<div class="footer-inner">
<div class="footer-brand"><a href="/" class="logo"><div class="logo-icon">MM</div>Macro &amp; Meals</a><p>Your trusted source for nutrition calculators and health tools. Free, accurate, and easy to use.</p></div>
<div><h4>Quick Links</h4><ul><li><a href="/">Home</a></li><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li><li><a href="/privacy-policy/">Privacy Policy</a></li><li><a href="/terms-conditions/">Terms &amp; Conditions</a></li><li><a href="/disclaimer/">Disclaimer</a></li></ul></div>
<div><h4>Popular Calculators</h4><ul><li><a href="/bmi-calculator/">BMI Calculator</a></li><li><a href="/bmr-calculator/">BMR Calculator</a></li><li><a href="/tdee-calculator/">TDEE Calculator</a></li><li><a href="/protein-calculator/">Protein Calculator</a></li><li><a href="/calorie-deficit-calculator/">Calorie Deficit Calculator</a></li><li><a href="/keto-macro-calculator/">Keto Macro Calculator</a></li></ul></div>
<div><h4>Restaurant Calculators</h4><ul><li><a href="/starbucks-nutrition-calculator/">Starbucks</a></li><li><a href="/chipotle-nutrition-calculator/">Chipotle</a></li><li><a href="/mcdonalds-calories-calculator/">McDonald\'s</a></li><li><a href="/subway-nutrition-calculator/">Subway</a></li><li><a href="/five-guys-nutrition-calculator/">Five Guys</a></li><li><a href="/panda-express-nutrition-calculator/">Panda Express</a></li></ul></div>
</div>
<div class="footer-bottom">&copy; {YEAR} {BRAND} &mdash; All rights reserved.</div>
</footer>
<script src="/js/site-config.js"></script>
<script src="/js/scripts-config.js"></script>
<script src="/js/main.js"></script>'''

def page(slug, title, description, body_content, extra_head='', extra_scripts='', schema_type='WebPage', noindex=False):
    canonical = f'{URL}/{slug}/' if slug else f'{URL}/'
    robots = '<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index,follow">'
    schema = f'{{"@context":"https://schema.org","@type":"{schema_type}","name":"{title}","url":"{canonical}","description":"{description}"}}'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {BRAND_RAW}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND_RAW}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
{robots}
<link rel="stylesheet" href="/css/style.css">
{extra_head}
<script type="application/ld+json">{schema}</script>
</head>
<body>
{header()}

{body_content}

{footer()}
{extra_scripts}
</body>
</html>'''

def write_page(slug, content):
    d = os.path.join(ROOT, slug)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, 'index.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  + {slug}/index.html')


# ═══════════════════════════════════════════════════════════════
# ESSENTIAL PAGES
# ═══════════════════════════════════════════════════════════════

def create_about():
    body = f'''<section class="hero"><div class="container"><h1>About {BRAND_RAW}</h1><p>Your trusted source for free nutrition calculators and health tools.</p></div></section>
<div class="content-section">
<h2>Our Mission</h2>
<p>At {BRAND_RAW}, we believe everyone deserves access to accurate, easy-to-use nutrition and health tools. Our mission is to empower individuals to make informed decisions about their diet, fitness, and overall well-being.</p>

<h2>What We Offer</h2>
<p>We provide over 100 free calculators covering a wide range of health and nutrition topics:</p>
<ul>
<li><strong>Restaurant Nutrition Calculators</strong> — Track calories and macros at your favorite restaurants including Starbucks, Chipotle, McDonald's, Subway, and 50+ more.</li>
<li><strong>Health &amp; Body Composition</strong> — Calculate BMI, BMR, TDEE, body fat percentage, ideal body weight, and more using medically-validated formulas.</li>
<li><strong>Diet &amp; Macro Tools</strong> — Get personalized macro targets for weight loss, keto diets, protein intake, and carbohydrate needs.</li>
<li><strong>Vitamin Calculators</strong> — Determine your daily vitamin requirements based on age, gender, and lifestyle factors.</li>
<li><strong>Pregnancy &amp; Specialty</strong> — Due date calculators, ovulation predictors, pregnancy weight gain trackers, and more.</li>
</ul>

<h2>Our Commitment to Accuracy</h2>
<p>All our calculators use peer-reviewed formulas and official nutrition data. Restaurant nutrition data is sourced from official restaurant nutrition guides and FDA databases. Medical calculators follow guidelines from organizations like the WHO, NIH, and CDC.</p>

<h2>Privacy First</h2>
<p>All calculations happen directly in your browser. We never store your personal health data on our servers. Your information stays private and secure.</p>

<h2>Our Team</h2>
<p>{BRAND_RAW} is built by a team of nutrition enthusiasts, developers, and health professionals dedicated to making nutrition information accessible to everyone. We continuously update our tools and data to ensure accuracy and relevance.</p>

<h2>Contact Us</h2>
<p>Have questions, feedback, or suggestions? We'd love to hear from you. Visit our <a href="/contact/">contact page</a> to get in touch.</p>
</div>'''
    write_page('about', page('about', 'About Us',
        f'Learn about {BRAND_RAW} — your trusted source for free nutrition calculators and health tools.',
        body))

def create_contact():
    body = f'''<section class="hero"><div class="container"><h1>Contact Us</h1><p>Have questions, feedback, or suggestions? We'd love to hear from you.</p></div></section>
<div class="content-section">
<h2>Get In Touch</h2>
<p>We value your feedback and are here to help. Whether you have a question about one of our calculators, want to report an issue, or have a suggestion for a new tool, please don't hesitate to reach out.</p>

<h2>Email</h2>
<p>For general inquiries, feedback, or support:<br><strong>contact@{DOMAIN}</strong></p>

<h2>Business Inquiries</h2>
<p>For advertising, partnerships, or business-related matters:<br><strong>business@{DOMAIN}</strong></p>

<h2>Report an Issue</h2>
<p>Found a bug or incorrect data? Please let us know:</p>
<ul>
<li>Which calculator or page the issue is on</li>
<li>What you expected to see vs. what you saw</li>
<li>Your browser and device type</li>
</ul>
<p>We strive to fix reported issues within 48 hours.</p>

<h2>Frequently Asked Questions</h2>
<p>Before reaching out, you might find your answer in our calculator-specific FAQ sections. Each calculator page includes detailed FAQs about formulas, accuracy, and usage.</p>

<h2>Response Time</h2>
<p>We aim to respond to all inquiries within 1-2 business days. For urgent matters, please include "URGENT" in your subject line.</p>
</div>'''
    write_page('contact', page('contact', 'Contact Us',
        f'Get in touch with {BRAND_RAW}. Questions, feedback, support, and business inquiries.',
        body))

def create_disclaimer():
    body = f'''<section class="hero"><div class="container"><h1>Disclaimer</h1><p>Important information about using our calculators and health tools.</p></div></section>
<div class="content-section">
<p><strong>Last Updated:</strong> May {YEAR}</p>

<h2>General Disclaimer</h2>
<p>The information provided by {BRAND_RAW} ({DOMAIN}) is for general informational and educational purposes only. All information on the site is provided in good faith; however, we make no representation or warranty of any kind, express or implied, regarding the accuracy, adequacy, validity, reliability, availability, or completeness of any information on the site.</p>

<h2>Not Medical Advice</h2>
<p>The calculators and tools on this website are NOT substitutes for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay seeking it because of something you have read on this website.</p>

<h2>Nutrition Data Accuracy</h2>
<p>Restaurant nutrition data is sourced from official restaurant nutrition guides and publicly available FDA databases. However, actual nutrition values may vary based on location, preparation method, portion size, and recipe changes. We update our data regularly but cannot guarantee real-time accuracy.</p>

<h2>Calculator Formulas</h2>
<p>Our health calculators use well-established, peer-reviewed formulas from medical literature and guidelines from organizations such as WHO, NIH, and CDC. However, individual results may vary, and these tools should be used as screening aids, not diagnostic instruments.</p>

<h2>External Links</h2>
<p>This website may contain links to external websites that are not provided or maintained by or in any way affiliated with {BRAND_RAW}. We do not guarantee the accuracy, relevance, timeliness, or completeness of any information on these external websites.</p>

<h2>Limitation of Liability</h2>
<p>Under no circumstance shall {BRAND_RAW} have any liability to you for any loss or damage of any kind incurred as a result of the use of the site or reliance on any information provided on the site. Your use of the site and your reliance on any information on the site is solely at your own risk.</p>
</div>'''
    write_page('disclaimer', page('disclaimer', 'Disclaimer',
        f'Disclaimer for {BRAND_RAW}. Important information about using our calculators and health tools.',
        body))

def create_privacy_policy():
    body = f'''<section class="hero"><div class="container"><h1>Privacy Policy</h1><p>How {BRAND_RAW} handles your data and protects your privacy.</p></div></section>
<div class="content-section">
<p><strong>Last Updated:</strong> May {YEAR}</p>

<h2>1. Information We Collect</h2>
<p>{BRAND_RAW} is designed with privacy first. All calculator inputs and results are processed entirely in your browser. We do not collect, store, or transmit any personal health data you enter into our calculators.</p>
<p>We may collect the following non-personal information automatically:</p>
<ul>
<li>Browser type and version</li>
<li>Operating system</li>
<li>Referring website</li>
<li>Pages visited and time spent</li>
<li>General geographic location (country/region level)</li>
</ul>

<h2>2. Cookies &amp; Tracking Technologies</h2>
<p>We use cookies and similar tracking technologies to enhance your experience:</p>
<ul>
<li><strong>Essential Cookies</strong> — Required for basic site functionality</li>
<li><strong>Analytics Cookies</strong> — Help us understand how visitors use our site (e.g., Google Analytics)</li>
<li><strong>Advertising Cookies</strong> — Used by ad networks to serve relevant ads (e.g., Google AdSense)</li>
</ul>
<p>You can control cookie settings through your browser preferences. For more details, see our <a href="/cookie-policy/">Cookie Policy</a>.</p>

<h2>3. Google AdSense &amp; Third-Party Advertising</h2>
<p>We use Google AdSense to display advertisements. Google and its partners may use cookies to serve ads based on your prior visits to our website or other websites. You can opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Google Ad Settings</a>.</p>

<h2>4. Google Analytics</h2>
<p>We use Google Analytics to analyze website traffic. Google Analytics uses cookies to collect anonymous usage data. This data helps us improve our website and user experience. You can opt out by installing the <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">Google Analytics Opt-out Browser Add-on</a>.</p>

<h2>5. Data Security</h2>
<p>We use HTTPS encryption for all pages. Since we don't collect personal health data, there is no personal health data at risk. We follow industry best practices to protect our infrastructure.</p>

<h2>6. Children's Privacy (COPPA)</h2>
<p>Our site is not directed at children under 13. We do not knowingly collect information from children under 13. If you believe a child has provided us with personal information, please contact us immediately.</p>

<h2>7. Your Rights (GDPR/CCPA)</h2>
<p>Depending on your jurisdiction, you may have the right to:</p>
<ul>
<li>Access the personal data we hold about you</li>
<li>Request deletion of your data</li>
<li>Opt out of data selling (we do not sell personal data)</li>
<li>Withdraw consent for cookie tracking</li>
</ul>

<h2>8. External Links</h2>
<p>Our site may contain links to external websites. We are not responsible for the privacy practices of those websites.</p>

<h2>9. Changes to This Policy</h2>
<p>We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last Updated" date.</p>

<h2>10. Contact Us</h2>
<p>If you have questions about this Privacy Policy, please contact us through our <a href="/contact/">contact page</a> or email us at contact@{DOMAIN}.</p>
</div>'''
    write_page('privacy-policy', page('privacy-policy', 'Privacy Policy',
        f'Privacy Policy for {BRAND_RAW}. Learn how we handle your data and protect your privacy.',
        body))

def create_terms():
    body = f'''<section class="hero"><div class="container"><h1>Terms &amp; Conditions</h1><p>Please read these terms carefully before using our services.</p></div></section>
<div class="content-section">
<p><strong>Last Updated:</strong> May {YEAR}</p>

<h2>1. Acceptance of Terms</h2>
<p>By accessing and using {BRAND_RAW} ({DOMAIN}), you agree to be bound by these Terms and Conditions. If you do not agree, please do not use our website.</p>

<h2>2. Use of Calculators</h2>
<p>Our calculators are provided for informational and educational purposes only. They are not substitutes for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers before making health decisions based on calculator results.</p>

<h2>3. Accuracy of Information</h2>
<p>While we strive to provide accurate nutrition data and calculations using peer-reviewed formulas, official restaurant nutrition guides, and FDA databases, we cannot guarantee the accuracy of all information. Nutrition values may vary by location, preparation method, and serving size.</p>

<h2>4. Intellectual Property</h2>
<p>All content on this website, including calculators, text, graphics, logos, and code, is the property of {BRAND_RAW} and is protected by international copyright laws. You may not reproduce, distribute, modify, or create derivative works without our explicit written permission.</p>

<h2>5. Permitted Use</h2>
<p>You are granted a limited, non-exclusive, non-transferable license to access and use our website for personal, non-commercial purposes. You may:</p>
<ul>
<li>Use our calculators for personal health tracking</li>
<li>Share links to our pages</li>
<li>Print results for personal use</li>
</ul>

<h2>6. Prohibited Conduct</h2>
<p>You agree not to:</p>
<ul>
<li>Use the site for any unlawful purpose</li>
<li>Attempt to gain unauthorized access to our systems</li>
<li>Scrape, harvest, or systematically download data from our site</li>
<li>Use automated tools (bots, crawlers) in a manner that burdens our servers</li>
<li>Reproduce our content without permission</li>
<li>Impersonate any person or entity</li>
</ul>

<h2>7. Limitation of Liability</h2>
<p>{BRAND_RAW} shall not be liable for any direct, indirect, incidental, special, consequential, or punitive damages arising from your use of our calculators or reliance on information provided on this website.</p>

<h2>8. Indemnification</h2>
<p>You agree to indemnify and hold harmless {BRAND_RAW} from any claims, losses, or damages arising from your use of the website or violation of these terms.</p>

<h2>9. Third-Party Links</h2>
<p>Our site may contain links to third-party websites. We are not responsible for the content, privacy practices, or terms of these external sites.</p>

<h2>10. Modifications</h2>
<p>We reserve the right to modify these Terms and Conditions at any time. Changes will be effective upon posting to this page. Your continued use of the site after changes constitutes acceptance.</p>

<h2>11. Governing Law</h2>
<p>These Terms shall be governed by and construed in accordance with applicable laws, without regard to conflict of law principles.</p>

<h2>12. Contact</h2>
<p>For questions about these Terms, please visit our <a href="/contact/">contact page</a> or email contact@{DOMAIN}.</p>
</div>'''
    write_page('terms-conditions', page('terms-conditions', 'Terms &amp; Conditions',
        f'Terms and Conditions for using {BRAND_RAW} nutrition calculators and health tools.',
        body))

def create_cookie_policy():
    body = f'''<section class="hero"><div class="container"><h1>Cookie Policy</h1><p>How {BRAND_RAW} uses cookies and similar technologies.</p></div></section>
<div class="content-section">
<p><strong>Last Updated:</strong> May {YEAR}</p>

<h2>What Are Cookies?</h2>
<p>Cookies are small text files placed on your device when you visit a website. They help websites remember your preferences and understand how you interact with the site.</p>

<h2>How We Use Cookies</h2>
<p>{BRAND_RAW} uses the following types of cookies:</p>

<h2>1. Essential Cookies</h2>
<p>These cookies are necessary for the website to function properly. They enable basic features like page navigation and access to secure areas. The website cannot function properly without these cookies.</p>

<h2>2. Analytics Cookies</h2>
<p>We use analytics cookies (such as Google Analytics) to understand how visitors interact with our website. These cookies collect information anonymously, including:</p>
<ul>
<li>Number of visitors</li>
<li>Pages visited and time spent</li>
<li>Bounce rates</li>
<li>Traffic sources</li>
</ul>

<h2>3. Advertising Cookies</h2>
<p>We display advertisements through Google AdSense. These cookies are used to:</p>
<ul>
<li>Serve ads relevant to your interests</li>
<li>Limit the number of times you see an ad</li>
<li>Measure the effectiveness of advertising campaigns</li>
</ul>
<p>Third-party advertisers may also place cookies on your device.</p>

<h2>4. Functional Cookies</h2>
<p>These cookies remember your preferences (such as unit preferences in calculators) to provide a more personalized experience.</p>

<h2>Managing Cookies</h2>
<p>You can control and manage cookies in several ways:</p>
<ul>
<li><strong>Browser Settings</strong> — Most browsers allow you to refuse or delete cookies through settings</li>
<li><strong>Google Ad Settings</strong> — <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Manage ad personalization</a></li>
<li><strong>Google Analytics Opt-out</strong> — <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">Install the opt-out add-on</a></li>
<li><strong>Network Advertising Initiative</strong> — <a href="https://optout.networkadvertising.org/" target="_blank" rel="noopener">Opt out of targeted advertising</a></li>
</ul>
<p>Please note that disabling cookies may affect the functionality of some features on our website.</p>

<h2>Changes to This Policy</h2>
<p>We may update this Cookie Policy from time to time. Changes will be posted on this page.</p>

<h2>Contact</h2>
<p>If you have questions about our use of cookies, please contact us through our <a href="/contact/">contact page</a>.</p>
</div>'''
    write_page('cookie-policy', page('cookie-policy', 'Cookie Policy',
        f'Cookie Policy for {BRAND_RAW}. How we use cookies and tracking technologies.',
        body))

def create_dmca():
    body = f'''<section class="hero"><div class="container"><h1>DMCA Policy</h1><p>Digital Millennium Copyright Act notice and takedown procedures.</p></div></section>
<div class="content-section">
<p><strong>Last Updated:</strong> May {YEAR}</p>

<h2>Copyright Notice</h2>
<p>{BRAND_RAW} respects the intellectual property rights of others and expects its users to do the same. In accordance with the Digital Millennium Copyright Act (DMCA), we will respond expeditiously to claims of copyright infringement committed using our website.</p>

<h2>Filing a DMCA Takedown Notice</h2>
<p>If you believe that content on our website infringes your copyright, please send a written notification containing:</p>
<ul>
<li>A physical or electronic signature of the copyright owner or authorized agent</li>
<li>Identification of the copyrighted work claimed to have been infringed</li>
<li>Identification of the material that is claimed to be infringing, including its URL</li>
<li>Your contact information (address, telephone number, email)</li>
<li>A statement that you have a good faith belief that the use is not authorized</li>
<li>A statement, under penalty of perjury, that the information in the notification is accurate and that you are authorized to act on behalf of the copyright owner</li>
</ul>

<h2>Send DMCA Notices To</h2>
<p>Email: dmca@{DOMAIN}<br>
Please include "DMCA Takedown Notice" in the subject line.</p>

<h2>Counter-Notification</h2>
<p>If you believe your content was wrongly removed due to a DMCA notice, you may file a counter-notification containing:</p>
<ul>
<li>Your physical or electronic signature</li>
<li>Identification of the material that was removed and its former location</li>
<li>A statement under penalty of perjury that you have a good faith belief the material was removed by mistake</li>
<li>Your name, address, and telephone number</li>
<li>Consent to the jurisdiction of your local federal court</li>
</ul>

<h2>Repeat Infringers</h2>
<p>{BRAND_RAW} will terminate access for users who are repeat copyright infringers.</p>
</div>'''
    write_page('dmca', page('dmca', 'DMCA Policy',
        f'DMCA Policy for {BRAND_RAW}. Copyright notice and takedown procedures.',
        body))

def create_accessibility():
    body = f'''<section class="hero"><div class="container"><h1>Accessibility Statement</h1><p>Our commitment to making nutrition tools accessible to everyone.</p></div></section>
<div class="content-section">
<p><strong>Last Updated:</strong> May {YEAR}</p>

<h2>Our Commitment</h2>
<p>{BRAND_RAW} is committed to ensuring digital accessibility for people with disabilities. We are continually improving the user experience for everyone and applying the relevant accessibility standards.</p>

<h2>Standards</h2>
<p>We aim to conform to the Web Content Accessibility Guidelines (WCAG) 2.1, Level AA. These guidelines explain how to make web content more accessible for people with disabilities and more user-friendly for everyone.</p>

<h2>Accessibility Features</h2>
<p>Our website includes the following accessibility features:</p>
<ul>
<li><strong>Semantic HTML</strong> — Proper heading hierarchy and landmark regions</li>
<li><strong>Keyboard Navigation</strong> — All interactive elements are accessible via keyboard</li>
<li><strong>Color Contrast</strong> — Sufficient contrast ratios for text readability</li>
<li><strong>Responsive Design</strong> — Works on all screen sizes and devices</li>
<li><strong>Form Labels</strong> — All form inputs have associated labels</li>
<li><strong>Alt Text</strong> — Descriptive text for images where applicable</li>
<li><strong>Focus Indicators</strong> — Visible focus indicators for keyboard users</li>
<li><strong>No Auto-Play</strong> — No auto-playing media content</li>
</ul>

<h2>Known Limitations</h2>
<p>While we strive for full accessibility, some areas may have limitations:</p>
<ul>
<li>Some calculator result charts may not be fully accessible to screen readers</li>
<li>Some third-party content (ads) may not meet accessibility standards</li>
</ul>

<h2>Feedback</h2>
<p>We welcome your feedback on the accessibility of {BRAND_RAW}. If you encounter accessibility barriers, please let us know:</p>
<ul>
<li>Email: accessibility@{DOMAIN}</li>
<li>Visit our <a href="/contact/">contact page</a></li>
</ul>
<p>We try to respond to accessibility feedback within 2 business days.</p>
</div>'''
    write_page('accessibility', page('accessibility', 'Accessibility Statement',
        f'Accessibility statement for {BRAND_RAW}. Our commitment to making nutrition tools accessible to everyone.',
        body))

def create_sitemap_page():
    body = f'''<section class="hero"><div class="container"><h1>Sitemap</h1><p>Browse all pages and tools available on {BRAND_RAW}.</p></div></section>
<div class="content-section">
<h2>Main Pages</h2>
<ul>
<li><a href="/">Home</a></li>
<li><a href="/about/">About Us</a></li>
<li><a href="/contact/">Contact Us</a></li>
<li><a href="/blog/">Blog</a></li>
<li><a href="/privacy-policy/">Privacy Policy</a></li>
<li><a href="/terms-conditions/">Terms &amp; Conditions</a></li>
<li><a href="/disclaimer/">Disclaimer</a></li>
<li><a href="/cookie-policy/">Cookie Policy</a></li>
<li><a href="/dmca/">DMCA Policy</a></li>
<li><a href="/accessibility/">Accessibility</a></li>
</ul>

<h2>All Calculators &amp; Tools</h2>
<p>A complete auto-generated list of all tools is available below. The list updates automatically as new tools are added.</p>
<div id="sitemap-tools"></div>
</div>'''
    extra = '''<script>
(function(){
  if (typeof PAGE_REGISTRY === 'undefined') return;
  var container = document.getElementById('sitemap-tools');
  if (!container) return;
  var cats = {};
  PAGE_REGISTRY.forEach(function(p){
    if (!cats[p.cat]) cats[p.cat] = [];
    cats[p.cat].push(p);
  });
  var catLabels = typeof CAT_LABELS !== 'undefined' ? CAT_LABELS : {};
  Object.keys(cats).forEach(function(cat){
    var h3 = document.createElement('h2');
    h3.textContent = catLabels[cat] || cat;
    container.appendChild(h3);
    var ul = document.createElement('ul');
    cats[cat].forEach(function(p){
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '/' + p.slug + '/';
      a.textContent = p.icon + ' ' + p.title;
      li.appendChild(a);
      ul.appendChild(li);
    });
    container.appendChild(ul);
  });
})();
</script>'''
    write_page('sitemap-page', page('sitemap-page', 'Sitemap',
        f'Complete sitemap of {BRAND_RAW}. Browse all calculators, tools, and pages.',
        body, extra_scripts=extra))


# ═══════════════════════════════════════════════════════════════
# BLOG SECTION
# ═══════════════════════════════════════════════════════════════

def create_blog_listing():
    body = f'''<section class="hero"><div class="container"><h1>Blog</h1><p>Expert nutrition tips, calculator guides, and health insights from {BRAND_RAW}.</p></div></section>
<section class="section">
<div class="container">
<div class="blog-grid">

<article class="blog-card">
<a href="/blog/how-to-calculate-your-daily-calorie-needs/" class="blog-card-link">
<div class="blog-card-img" style="background:linear-gradient(135deg,#10b981,#059669);">
<span class="blog-card-cat">Nutrition Guide</span>
</div>
<div class="blog-card-body">
<time datetime="2026-05-13">May 13, 2026</time>
<h2>How to Calculate Your Daily Calorie Needs: A Complete Guide</h2>
<p>Learn the science behind TDEE, BMR, and activity multipliers to find your perfect calorie intake for weight loss, maintenance, or muscle gain.</p>
<span class="blog-read-more">Read More &rarr;</span>
</div>
</a>
</article>

</div>
</div>
</section>'''
    extra_head = '<link rel="stylesheet" href="/css/blog.css">'
    write_page('blog', page('blog', 'Blog',
        f'Nutrition tips, calculator guides, and health insights from {BRAND_RAW}.',
        body, extra_head=extra_head, schema_type='CollectionPage'))

def create_sample_blog_post():
    body = f'''<section class="blog-hero">
<div class="container">
<div class="blog-meta">
<a href="/blog/" class="blog-back">&larr; Back to Blog</a>
<span class="blog-cat-tag">Nutrition Guide</span>
</div>
<h1>How to Calculate Your Daily Calorie Needs: A Complete Guide</h1>
<div class="blog-info">
<time datetime="2026-05-13">May 13, 2026</time>
<span class="blog-divider">·</span>
<span>8 min read</span>
<span class="blog-divider">·</span>
<span>By {BRAND_RAW} Team</span>
</div>
</div>
</section>

<article class="blog-content">
<div class="container blog-container">

<div class="blog-body">

<p class="blog-intro">Understanding your daily calorie needs is the foundation of any nutrition plan. Whether you want to lose weight, build muscle, or simply maintain your current physique, knowing how many calories your body needs is the first step. In this guide, we'll break down the science behind calorie calculations and show you exactly how to find your number.</p>

<div class="blog-toc">
<h3>Table of Contents</h3>
<ol>
<li><a href="#what-are-calories">What Are Calories?</a></li>
<li><a href="#bmr">Understanding BMR</a></li>
<li><a href="#tdee">What Is TDEE?</a></li>
<li><a href="#formulas">Popular Formulas</a></li>
<li><a href="#activity">Activity Multipliers</a></li>
<li><a href="#goals">Adjusting for Goals</a></li>
<li><a href="#tools">Tools to Help</a></li>
</ol>
</div>

<h2 id="what-are-calories">1. What Are Calories?</h2>
<p>A calorie is a unit of energy. Specifically, it's the amount of energy needed to raise the temperature of 1 gram of water by 1 degree Celsius. When we talk about food calories, we're actually referring to kilocalories (kcal) — 1 food calorie = 1,000 scientific calories.</p>
<p>Your body uses calories from three macronutrients:</p>
<ul>
<li><strong>Protein</strong> — 4 calories per gram</li>
<li><strong>Carbohydrates</strong> — 4 calories per gram</li>
<li><strong>Fat</strong> — 9 calories per gram</li>
</ul>

<h2 id="bmr">2. Understanding Basal Metabolic Rate (BMR)</h2>
<p>Your Basal Metabolic Rate (BMR) is the number of calories your body burns at complete rest — just to keep your organs functioning, your heart beating, and your lungs breathing. BMR typically accounts for 60-70% of your total daily energy expenditure.</p>
<p>Several factors affect your BMR:</p>
<ul>
<li><strong>Age</strong> — BMR decreases with age (about 1-2% per decade after 20)</li>
<li><strong>Gender</strong> — Men typically have higher BMR due to more muscle mass</li>
<li><strong>Height &amp; Weight</strong> — Larger bodies require more energy</li>
<li><strong>Body Composition</strong> — Muscle burns more calories than fat</li>
</ul>
<div class="blog-callout">
<strong>Try It:</strong> Use our <a href="/bmr-calculator/">BMR Calculator</a> to find your basal metabolic rate in seconds.
</div>

<h2 id="tdee">3. What Is TDEE (Total Daily Energy Expenditure)?</h2>
<p>TDEE is your BMR plus the energy you burn through daily activities and exercise. It represents the total number of calories you burn in a day. This is the number you need to know for any diet plan.</p>
<p>TDEE = BMR × Activity Multiplier</p>
<div class="blog-callout">
<strong>Calculate Yours:</strong> Our <a href="/tdee-calculator/">TDEE Calculator</a> does all the math for you automatically.
</div>

<h2 id="formulas">4. Popular Calorie Calculation Formulas</h2>
<p>There are several well-validated formulas for calculating BMR:</p>

<h3>Mifflin-St Jeor Equation (Most Accurate)</h3>
<p>Considered the gold standard by the American Dietetic Association:</p>
<ul>
<li><strong>Men:</strong> BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age) + 5</li>
<li><strong>Women:</strong> BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age) - 161</li>
</ul>

<h3>Harris-Benedict Equation (Classic)</h3>
<p>One of the earliest and most widely used formulas:</p>
<ul>
<li><strong>Men:</strong> BMR = 88.362 + (13.397 × weight in kg) + (4.799 × height in cm) - (5.677 × age)</li>
<li><strong>Women:</strong> BMR = 447.593 + (9.247 × weight in kg) + (3.098 × height in cm) - (4.330 × age)</li>
</ul>

<h2 id="activity">5. Activity Multipliers</h2>
<p>Multiply your BMR by the appropriate activity factor to get your TDEE:</p>
<div class="blog-table-wrap">
<table class="blog-table">
<thead><tr><th>Activity Level</th><th>Multiplier</th><th>Description</th></tr></thead>
<tbody>
<tr><td>Sedentary</td><td>1.2</td><td>Desk job, little or no exercise</td></tr>
<tr><td>Lightly Active</td><td>1.375</td><td>Light exercise 1-3 days/week</td></tr>
<tr><td>Moderately Active</td><td>1.55</td><td>Moderate exercise 3-5 days/week</td></tr>
<tr><td>Very Active</td><td>1.725</td><td>Hard exercise 6-7 days/week</td></tr>
<tr><td>Extra Active</td><td>1.9</td><td>Very hard exercise or physical job</td></tr>
</tbody>
</table>
</div>

<h2 id="goals">6. Adjusting for Your Goals</h2>
<p>Once you know your TDEE, adjust based on your goal:</p>
<ul>
<li><strong>Weight Loss:</strong> Eat 500-750 calories below TDEE (lose ~0.5-0.7 kg/week)</li>
<li><strong>Maintenance:</strong> Eat at your TDEE</li>
<li><strong>Muscle Gain:</strong> Eat 250-500 calories above TDEE</li>
</ul>
<div class="blog-callout blog-callout-warning">
<strong>Important:</strong> Never go below 1,200 calories/day for women or 1,500 calories/day for men without medical supervision. Extreme calorie restriction can be dangerous.
</div>

<h2 id="tools">7. Tools to Help You Track</h2>
<p>Here are the {BRAND_RAW} calculators that can help you on your journey:</p>
<div class="blog-tools-grid">
<a href="/bmr-calculator/" class="blog-tool-card"><span class="blog-tool-icon">🔥</span><span>BMR Calculator</span></a>
<a href="/tdee-calculator/" class="blog-tool-card"><span class="blog-tool-icon">⚡</span><span>TDEE Calculator</span></a>
<a href="/calorie-deficit-calculator/" class="blog-tool-card"><span class="blog-tool-icon">📉</span><span>Calorie Deficit Calculator</span></a>
<a href="/protein-calculator/" class="blog-tool-card"><span class="blog-tool-icon">🥩</span><span>Protein Calculator</span></a>
<a href="/bmi-calculator/" class="blog-tool-card"><span class="blog-tool-icon">⚖️</span><span>BMI Calculator</span></a>
<a href="/keto-macro-calculator/" class="blog-tool-card"><span class="blog-tool-icon">🥑</span><span>Keto Macro Calculator</span></a>
</div>

<h2>Conclusion</h2>
<p>Calculating your daily calorie needs doesn't have to be complicated. Start with your BMR, factor in your activity level to get your TDEE, then adjust based on your goals. Use our free calculators to make the process quick and accurate.</p>
<p>Remember: these numbers are starting points. Everyone's body is different, so monitor your progress and adjust as needed. And always consult a healthcare provider before making significant dietary changes.</p>

<div class="blog-share">
<h3>Found this helpful? Share it:</h3>
<div class="blog-share-btns">
<a href="https://twitter.com/intent/tweet?url={URL}/blog/how-to-calculate-your-daily-calorie-needs/&text=How+to+Calculate+Your+Daily+Calorie+Needs" target="_blank" rel="noopener" class="share-btn share-twitter">Twitter</a>
<a href="https://www.facebook.com/sharer/sharer.php?u={URL}/blog/how-to-calculate-your-daily-calorie-needs/" target="_blank" rel="noopener" class="share-btn share-facebook">Facebook</a>
<a href="https://www.linkedin.com/shareArticle?mini=true&url={URL}/blog/how-to-calculate-your-daily-calorie-needs/" target="_blank" rel="noopener" class="share-btn share-linkedin">LinkedIn</a>
</div>
</div>

</div>

<aside class="blog-sidebar">
<div class="sidebar-card">
<h3>Popular Calculators</h3>
<ul>
<li><a href="/bmi-calculator/">BMI Calculator</a></li>
<li><a href="/bmr-calculator/">BMR Calculator</a></li>
<li><a href="/tdee-calculator/">TDEE Calculator</a></li>
<li><a href="/protein-calculator/">Protein Calculator</a></li>
<li><a href="/calorie-deficit-calculator/">Calorie Deficit</a></li>
</ul>
</div>
<div class="sidebar-card">
<h3>Related Posts</h3>
<p class="sidebar-note">More articles coming soon. Stay tuned!</p>
</div>
</aside>

</div>
</article>'''
    extra_head = '<link rel="stylesheet" href="/css/blog.css">'
    schema = f'''{{"@context":"https://schema.org","@type":"BlogPosting","headline":"How to Calculate Your Daily Calorie Needs: A Complete Guide","datePublished":"2026-05-13","dateModified":"2026-05-13","author":{{"@type":"Organization","name":"{BRAND_RAW}"}},"publisher":{{"@type":"Organization","name":"{BRAND_RAW}","url":"{URL}"}},"url":"{URL}/blog/how-to-calculate-your-daily-calorie-needs/","description":"Learn the science behind TDEE, BMR, and activity multipliers to find your perfect calorie intake."}}'''
    write_page('blog/how-to-calculate-your-daily-calorie-needs', page(
        'blog/how-to-calculate-your-daily-calorie-needs',
        'How to Calculate Your Daily Calorie Needs: A Complete Guide',
        'Learn the science behind TDEE, BMR, and activity multipliers to find your perfect calorie intake for weight loss, maintenance, or muscle gain.',
        body, extra_head=extra_head, schema_type='BlogPosting'))


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('Creating essential pages...')
    create_about()
    create_contact()
    create_disclaimer()
    create_privacy_policy()
    create_terms()
    create_cookie_policy()
    create_dmca()
    create_accessibility()
    create_sitemap_page()
    
    print('\nCreating blog section...')
    create_blog_listing()
    create_sample_blog_post()
    
    print('\nDone!')
