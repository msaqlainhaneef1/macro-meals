<?php
/**
 * Dynamic Sitemap Generator for Macro & Meals
 * Automatically detects all HTML pages and assigns proper priorities.
 * Serves as a fallback when sitemap.xml is stale.
 *
 * Access: https://macroandmeals.com/sitemap.php
 */
header('Content-type: application/xml; charset="utf-8"');

$baseUrl = 'https://macroandmeals.com';

// Directories to skip (not content pages)
$skipDirs = ['css', 'js', 'img', 'components', 'data', 'api', 'cache', 'fonts', 'assets'];

// High-traffic calculators (priority 0.9)
$highTrafficCalcs = [
    'bmi-calculator', 'bmr-calculator', 'tdee-calculator',
    'calorie-deficit-calculator', 'protein-calculator',
    'keto-macro-calculator', 'macro-calculator-for-weight-loss',
    'body-fat-calculator', 'ideal-body-weight-calculator',
];

// High-traffic restaurants (priority 0.9)
$highTrafficRestaurants = [
    'chipotle-nutrition-calculator', 'mcdonalds-calories-calculator',
    'starbucks-nutrition-calculator', 'subway-nutrition-calculator',
    'taco-bell-nutrition-calculator', 'wendys-nutrition-calculator',
    'five-guys-nutrition-calculator', 'panda-express-nutrition-calculator',
    'burger-king-calories-calculator',
];

// Essential/policy pages (priority 0.5)
$essentialPages = [
    'about', 'contact', 'privacy-policy', 'terms-conditions',
    'disclaimer', 'cookie-policy', 'dmca', 'accessibility', 'sitemap-page',
];

function getPageMeta($slug) {
    global $highTrafficCalcs, $highTrafficRestaurants, $essentialPages;

    if (in_array($slug, $highTrafficCalcs) || in_array($slug, $highTrafficRestaurants)) {
        return ['0.9', 'weekly'];
    }
    if (preg_match('/-nutrition-calculator$|-calories-calculator$/', $slug)) {
        return ['0.8', 'weekly'];
    }
    if (preg_match('/-menu$/', $slug)) {
        return ['0.7', 'weekly'];
    }
    if (preg_match('/-calculator$|-converter$/', $slug)) {
        return ['0.8', 'weekly'];
    }
    if (in_array($slug, $essentialPages)) {
        return ['0.5', 'monthly'];
    }
    if (strpos($slug, 'blog') === 0) {
        return ['0.7', 'weekly'];
    }
    return ['0.6', 'monthly'];
}

echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
echo '<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>' . "\n";
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"' . "\n";
echo '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' . "\n";
echo '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9' . "\n";
echo '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">' . "\n";

// Homepage
$homeMod = date('c', filemtime('index.html'));
echo "  <url>\n";
echo "    <loc>" . htmlspecialchars($baseUrl . '/') . "</loc>\n";
echo "    <lastmod>" . $homeMod . "</lastmod>\n";
echo "    <changefreq>daily</changefreq>\n";
echo "    <priority>1.0</priority>\n";
echo "  </url>\n";

// Collect all page directories
$pages = [];
$directories = glob('*', GLOB_ONLYDIR);
foreach ($directories as $dir) {
    if (in_array($dir, $skipDirs)) continue;
    if (!file_exists($dir . '/index.html')) continue;

    $slug = $dir;
    $meta = getPageMeta($slug);
    $lastmod = date('c', filemtime($dir . '/index.html'));
    $pages[] = [
        'loc'        => $baseUrl . '/' . $slug . '/',
        'lastmod'    => $lastmod,
        'priority'   => $meta[0],
        'changefreq' => $meta[1],
    ];
}

// Check for blog subdirectories
if (is_dir('blog')) {
    $blogPosts = glob('blog/*', GLOB_ONLYDIR);
    foreach ($blogPosts as $post) {
        if (!file_exists($post . '/index.html')) continue;
        $slug = $post;
        $lastmod = date('c', filemtime($post . '/index.html'));
        $pages[] = [
            'loc'        => $baseUrl . '/' . $slug . '/',
            'lastmod'    => $lastmod,
            'priority'   => '0.7',
            'changefreq' => 'weekly',
        ];
    }
}

// Sort by priority descending, then alphabetically
usort($pages, function($a, $b) {
    $pd = floatval($b['priority']) - floatval($a['priority']);
    if ($pd != 0) return ($pd > 0) ? 1 : -1;
    return strcmp($a['loc'], $b['loc']);
});

// Output
foreach ($pages as $page) {
    echo "  <url>\n";
    echo "    <loc>" . htmlspecialchars($page['loc']) . "</loc>\n";
    echo "    <lastmod>" . $page['lastmod'] . "</lastmod>\n";
    echo "    <changefreq>" . $page['changefreq'] . "</changefreq>\n";
    echo "    <priority>" . $page['priority'] . "</priority>\n";
    echo "  </url>\n";
}

echo '</urlset>';
?>
