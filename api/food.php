<?php
/**
 * Food Search & Nutrition API (server-side data sources only).
 *
 * Endpoints:
 *   ?query=chicken breast   — Combined text search
 *   ?barcode=3017620422003  — Barcode lookup
 *   ?fdcId=171705           — Food detail with portion options
 *   ?autocomplete=chic      — Quick suggestions
 */

require_once __DIR__ . '/extra-search.lib.php';

define('USDA_API_KEY', 'fqiLIGccAEaVBbhFXS4RjKuraFldCPBjy4jPtqxb');
define('CACHE_DIR', __DIR__ . '/cache/');
define('CACHE_EXPIRY', 86400); // 24 hours

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('X-Content-Type-Options: nosniff');

// Ensure cache directory exists
if (!is_dir(CACHE_DIR)) { @mkdir(CACHE_DIR, 0755, true); }

/* ===== CACHING ===== */
function get_cache($key) {
    $file = CACHE_DIR . md5($key) . '.json';
    if (file_exists($file) && (time() - filemtime($file)) < CACHE_EXPIRY) {
        return json_decode(file_get_contents($file), true);
    }
    return null;
}
function set_cache($key, $data) {
    $file = CACHE_DIR . md5($key) . '.json';
    @file_put_contents($file, json_encode($data));
}

/* ===== HELPERS ===== */
function safe_float($v) { return isset($v) ? round((float)$v, 2) : null; }

function parse_grams_from_serving($servingText) {
    if (!$servingText) {
        return 100.0;
    }
    if (preg_match('/([\d.]+)\s*g\b/i', (string) $servingText, $m)) {
        $v = (float) $m[1];
        return $v > 0 ? $v : 100.0;
    }
    return 100.0;
}

/** Scale nutrient map from a reference serving size to per 100 g. */
function scale_nutrients_to_100g(array $nutrients, $servingGrams) {
    $servingGrams = (float) $servingGrams;
    if ($servingGrams <= 0 || abs($servingGrams - 100) < 0.5) {
        return $nutrients;
    }
    $factor = 100 / $servingGrams;
    foreach ($nutrients as $key => $val) {
        if ($val !== null && is_numeric($val)) {
            $nutrients[$key] = round((float) $val * $factor, 2);
        }
    }
    return $nutrients;
}

function clean_food_display_name($name, $brand = null) {
    $name = trim((string) ($name ?: 'Unknown'));
    if ($brand) {
        $brand = trim((string) $brand);
        $suffix = ' (' . $brand . ')';
        if ($suffix !== ' ()' && stripos($name, $suffix) !== false) {
            $name = trim(str_ireplace($suffix, '', $name));
        }
        if (strcasecmp($name, $brand) === 0) {
            return '';
        }
    }
    return $name;
}

function dedupe_food_results(array $items) {
    $seen = [];
    $out = [];
    foreach ($items as $item) {
        $key = strtolower(preg_replace('/[^a-z0-9]+/', '', substr($item['name'] ?? '', 0, 48)));
        if ($key === '' || isset($seen[$key])) {
            continue;
        }
        $seen[$key] = true;
        $out[] = $item;
    }
    return $out;
}

function off_context() {
    return stream_context_create([
        'http' => [
            'header' => "User-Agent: MacroAndMeals/1.0 (contact@macroandmeals.com)\r\n",
            'timeout' => 8
        ]
    ]);
}

/* ===== USDA NUTRIENT EXTRACTION ===== */
function extract_usda_nutrients($foodNutrients) {
    $map = [];
    foreach ($foodNutrients as $n) {
        if (isset($n['nutrient']['name'])) {
            $name = strtolower($n['nutrient']['name']);
            $unit = strtoupper($n['nutrient']['unitName'] ?? '');
            $val = isset($n['amount']) ? (float) $n['amount'] : (isset($n['value']) ? (float) $n['value'] : null);
        } else {
            $name = strtolower($n['nutrientName'] ?? '');
            $unit = strtoupper($n['unitName'] ?? '');
            $val = isset($n['value']) ? (float) $n['value'] : (isset($n['amount']) ? (float) $n['amount'] : null);
        }
        if ($val === null) continue;

        // Macros
        if (strpos($name, 'energy') !== false && $unit === 'KCAL') $map['calories'] = $val;
        elseif ($name === 'protein') $map['protein'] = $val;
        elseif (strpos($name, 'total lipid (fat)') !== false) $map['fat'] = $val;
        elseif (strpos($name, 'carbohydrate, by difference') !== false) $map['carbs'] = $val;
        elseif (strpos($name, 'fiber, total dietary') !== false) $map['fiber'] = $val;
        elseif (strpos($name, 'total sugars') !== false || $name === 'sugars, total including nlea') $map['sugars'] = $val;
        elseif (strpos($name, 'fatty acids, total saturated') !== false) $map['saturated_fat'] = $val;
        elseif (strpos($name, 'fatty acids, total trans') !== false) $map['trans_fat'] = $val;
        elseif ($name === 'cholesterol') $map['cholesterol'] = $val;
        elseif ($name === 'sodium, na') $map['sodium'] = $val;
        // Vitamins
        elseif ($name === 'vitamin a, rae') $map['vitamin_a'] = $val;
        elseif (strpos($name, 'vitamin c, total ascorbic') !== false) $map['vitamin_c'] = $val;
        elseif (strpos($name, 'vitamin d (d2 + d3)') !== false || $name === 'vitamin d (d2 + d3), international units') $map['vitamin_d'] = $val;
        elseif (strpos($name, 'vitamin e (alpha-tocopherol)') !== false) $map['vitamin_e'] = $val;
        elseif (strpos($name, 'vitamin k (phylloquinone)') !== false) $map['vitamin_k'] = $val;
        elseif ($name === 'thiamin') $map['thiamin'] = $val;
        elseif ($name === 'riboflavin') $map['riboflavin'] = $val;
        elseif ($name === 'niacin') $map['niacin'] = $val;
        elseif (strpos($name, 'vitamin b-6') !== false) $map['vitamin_b6'] = $val;
        elseif (strpos($name, 'folate, dfe') !== false) $map['folate'] = $val;
        elseif (strpos($name, 'vitamin b-12') !== false) $map['vitamin_b12'] = $val;
        // Minerals
        elseif ($name === 'calcium, ca') $map['calcium'] = $val;
        elseif ($name === 'iron, fe') $map['iron'] = $val;
        elseif ($name === 'magnesium, mg') $map['magnesium'] = $val;
        elseif ($name === 'phosphorus, p') $map['phosphorus'] = $val;
        elseif ($name === 'potassium, k') $map['potassium'] = $val;
        elseif ($name === 'zinc, zn') $map['zinc'] = $val;
        elseif ($name === 'copper, cu') $map['copper'] = $val;
        elseif ($name === 'manganese, mn') $map['manganese'] = $val;
        elseif ($name === 'selenium, se') $map['selenium'] = $val;
        // Water & energy kJ
        elseif ($name === 'water') $map['water'] = $val;
        elseif (strpos($name, 'energy') !== false && $unit === 'KJ') $map['energy_kj'] = $val;
        // Fatty acids breakdown
        elseif (strpos($name, 'fatty acids, total monounsaturated') !== false) $map['monounsaturated_fat'] = $val;
        elseif (strpos($name, 'fatty acids, total polyunsaturated') !== false) $map['polyunsaturated_fat'] = $val;
        // Caffeine
        elseif ($name === 'caffeine') $map['caffeine'] = $val;
    }
    return $map;
}

/* ===== USDA SEARCH (multiple results) ===== */
function fetch_usda_search($query, $limit = 8) {
    $url = "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=" . USDA_API_KEY
         . "&query=" . urlencode($query)
         . "&pageSize=" . $limit
         . "&dataType=SR%20Legacy,Foundation,Branded";

    $response = @file_get_contents($url);
    if (!$response) return [];

    $data = json_decode($response, true);
    if (!isset($data['foods']) || empty($data['foods'])) return [];

    $results = [];
    foreach ($data['foods'] as $food) {
        $nutrients = extract_usda_nutrients($food['foodNutrients'] ?? []);
        if (empty($nutrients['calories']) && empty($nutrients['protein'])) {
            continue;
        }

        $brand = $food['brandOwner'] ?? $food['brandName'] ?? null;
        $name = clean_food_display_name(
            ucwords(strtolower($food['description'] ?? 'Unknown Food')),
            $brand
        );
        if ($name === '') {
            continue;
        }

        $serving = $food['servingSize']
            ? ($food['servingSize'] . ' ' . ($food['servingSizeUnit'] ?? 'g'))
            : '100g';
        $servingG = parse_grams_from_serving($serving);
        $dataType = $food['dataType'] ?? '';
        if ($dataType === 'Branded' && $servingG > 0 && abs($servingG - 100) > 0.5) {
            $nutrients = scale_nutrients_to_100g($nutrients, $servingG);
        }

        $results[] = [
            'id' => 'usda_' . ($food['fdcId'] ?? ''),
            'fdcId' => $food['fdcId'] ?? null,
            'name' => $name,
            'brand' => $brand,
            'serving' => $serving,
            'servingGrams' => $servingG,
            'nutrients' => $nutrients,
            'foodType' => $dataType === 'Branded' ? 'branded' : 'standard',
            '_origin' => 'standard',
        ];
    }
    return $results;
}

/* ===== USDA DETAIL (single food by FDC ID) ===== */
function fetch_usda_detail($fdcId) {
    $url = "https://api.nal.usda.gov/fdc/v1/food/" . intval($fdcId) . "?api_key=" . USDA_API_KEY;
    $response = @file_get_contents($url);
    if (!$response) return null;

    $food = json_decode($response, true);
    if (!$food || !isset($food['fdcId'])) return null;

    $nutrients = extract_usda_nutrients($food['foodNutrients'] ?? []);

    $portions = [['desc' => '100 g (standard)', 'grams' => 100]];
    if (!empty($food['foodPortions'])) {
        foreach ($food['foodPortions'] as $portion) {
            if (empty($portion['gramWeight'])) {
                continue;
            }
            $unit = is_array($portion['measureUnit'] ?? null)
                ? ($portion['measureUnit']['name'] ?? 'serving')
                : ($portion['measureUnit'] ?? 'serving');
            $label = trim(($portion['amount'] ?? '') . ' ' . ($portion['modifier'] ?? $unit));
            $grams = (float) $portion['gramWeight'];
            $portions[] = [
                'desc' => $label . ' (' . round($grams) . ' g)',
                'grams' => $grams,
            ];
        }
    }

    return [
        'id' => 'food_' . $food['fdcId'],
        'fdcId' => $food['fdcId'],
        'name' => clean_food_display_name(
            ucwords(strtolower($food['description'] ?? 'Unknown Food')),
            $food['brandOwner'] ?? $food['brandName'] ?? null
        ),
        'serving' => isset($food['servingSize']) ? ($food['servingSize'] . ' ' . ($food['servingSizeUnit'] ?? 'g')) : '100g',
        'nutrients' => $nutrients,
        'portions' => $portions,
        '_origin' => 'standard',
    ];
}

/* ===== OPEN FOOD FACTS — BARCODE LOOKUP ===== */
function fetch_off_barcode($barcode) {
    $fields = 'product_name,brands,categories,nutriments,nutriscore_grade,nova_group,ecoscore_grade,image_url,serving_size,allergens,allergens_tags,ingredients_text,quantity';
    $url = "https://world.openfoodfacts.org/api/v2/product/" . urlencode($barcode) . ".json?fields=" . $fields;

    $response = @file_get_contents($url, false, off_context());
    if (!$response) return null;

    $data = json_decode($response, true);
    if (!isset($data['product']) || $data['status'] !== 1) return null;

    return format_off_product($data['product'], $barcode);
}

/* ===== OPEN FOOD FACTS — TEXT SEARCH ===== */
function fetch_off_search($query, $limit = 5) {
    $fields = 'product_name,brands,categories,nutriments,nutriscore_grade,nova_group,ecoscore_grade,image_url,serving_size,allergens,allergens_tags,ingredients_text,quantity,code';
    $url = "https://world.openfoodfacts.org/cgi/search.pl"
         . "?search_terms=" . urlencode($query)
         . "&search_simple=1&action=process&json=1"
         . "&page_size=" . $limit
         . "&fields=" . $fields;

    $response = @file_get_contents($url, false, off_context());
    if (!$response) return [];

    $data = json_decode($response, true);
    if (!isset($data['products']) || empty($data['products'])) return [];

    $results = [];
    foreach ($data['products'] as $p) {
        $item = format_off_product($p, $p['code'] ?? null);
        if ($item) $results[] = $item;
    }
    return $results;
}

function format_off_product($p, $barcode = null) {
    $n = $p['nutriments'] ?? [];
    if (empty($p['product_name'])) return null;

    $nutrients = [
        'calories' => safe_float($n['energy-kcal_100g'] ?? null),
        'protein' => safe_float($n['proteins_100g'] ?? null),
        'fat' => safe_float($n['fat_100g'] ?? null),
        'carbs' => safe_float($n['carbohydrates_100g'] ?? null),
        'fiber' => safe_float($n['fiber_100g'] ?? null),
        'sugars' => safe_float($n['sugars_100g'] ?? null),
        'saturated_fat' => safe_float($n['saturated-fat_100g'] ?? null),
        'trans_fat' => safe_float($n['trans-fat_100g'] ?? null),
        'sodium' => safe_float(isset($n['sodium_100g']) ? $n['sodium_100g'] * 1000 : null), // g -> mg
        'cholesterol' => safe_float($n['cholesterol_100g'] ?? null),
        'potassium' => safe_float($n['potassium_100g'] ?? null),
        'calcium' => safe_float($n['calcium_100g'] ?? null),
        'iron' => safe_float($n['iron_100g'] ?? null),
        'vitamin_a' => safe_float($n['vitamin-a_100g'] ?? null),
        'vitamin_c' => safe_float($n['vitamin-c_100g'] ?? null),
        'vitamin_d' => safe_float($n['vitamin-d_100g'] ?? null),
        'salt' => safe_float($n['salt_100g'] ?? null),
        'energy_kj' => safe_float($n['energy-kj_100g'] ?? $n['energy_100g'] ?? null),
    ];

    // Parse allergens
    $allergens = [];
    if (!empty($p['allergens_tags'])) {
        foreach ($p['allergens_tags'] as $a) {
            $allergens[] = ucfirst(str_replace('en:', '', $a));
        }
    }

    return [
        'id' => 'off_' . ($barcode ?: uniqid()),
        'barcode' => $barcode,
        'name' => $p['product_name'],
        'brand' => $p['brands'] ?? null,
        'category' => $p['categories'] ?? null,
        'serving' => $p['serving_size'] ?? '100g',
        'quantity' => $p['quantity'] ?? null,
        'image' => $p['image_url'] ?? null,
        'nutrients' => $nutrients,
        'nutriscore' => $p['nutriscore_grade'] ?? null,
        'nova' => $p['nova_group'] ?? null,
        'ecoscore' => $p['ecoscore_grade'] ?? null,
        'allergens' => $allergens,
        'ingredients' => $p['ingredients_text'] ?? null,
        '_origin' => 'packaged',
    ];
}

function food_type_from_item($item) {
    if (!empty($item['foodType'])) {
        return $item['foodType'];
    }
    $origin = $item['_origin'] ?? '';
    if ($origin === 'packaged' || !empty($item['barcode'])) {
        return 'packaged';
    }
    if (!empty($item['brand'])) {
        return 'branded';
    }
    return 'standard';
}

function sanitize_food_item($item) {
    if (!$item || !is_array($item)) {
        return null;
    }
    $nuts = $item['nutrients'] ?? [];
    $serving = $item['serving'] ?? '100g';
    $grams = $item['servingGrams'] ?? null;
    if ($grams === null && preg_match('/([\d.]+)\s*g\b/i', $serving, $gm)) {
        $grams = (float) $gm[1];
    }

    $displayName = clean_food_display_name($item['name'] ?? 'Unknown', $item['brand'] ?? null);
    if ($displayName === '') {
        return null;
    }

    $out = [
        'id' => $item['id'] ?? ('food_' . uniqid()),
        'fdcId' => $item['fdcId'] ?? null,
        'barcode' => $item['barcode'] ?? null,
        'name' => $displayName,
        'serving' => $serving,
        'servingGrams' => $grams ?: 100,
        'foodType' => food_type_from_item($item),
        'nutrients' => $nuts,
        'image' => $item['image'] ?? null,
    ];
    if (!empty($item['portions'])) {
        $out['portions'] = $item['portions'];
    }
    return $out;
}

function sanitize_food_list($items) {
    $out = [];
    foreach ($items as $item) {
        $clean = sanitize_food_item($item);
        if ($clean) {
            $out[] = $clean;
        }
    }
    return $out;
}

function normalize_extra_item($item) {
    $grams = $item['servingGrams'] ?? null;
    if ($grams === null && !empty($item['serving'])) {
        $grams = parse_grams_from_serving($item['serving']);
    }
    $grams = $grams ?: 100;
    $nuts = $item['nutrients'] ?? [];
    if ($grams > 0 && abs($grams - 100) > 0.5) {
        $nuts = scale_nutrients_to_100g($nuts, $grams);
    }
    $name = clean_food_display_name($item['name'] ?? 'Unknown', null);
    if ($name === '') {
        return null;
    }
    return [
        'id' => 'food_' . substr(md5($name . ($item['serving'] ?? '')), 0, 12),
        'name' => $name,
        'serving' => $item['serving'] ?? '100g',
        'servingGrams' => $grams,
        'nutrients' => $nuts,
        'foodType' => $item['foodType'] ?? 'general',
    ];
}

/* ===== COMBINED SEARCH ===== */
function search_food($query) {
    $cache_key = 'search_v4_' . strtolower(trim($query));
    $cached = get_cache($cache_key);
    if ($cached) {
        return $cached;
    }

    $usda = fetch_usda_search($query, 6);
    $off = fetch_off_search($query, 4);
    $extra = extra_search_combined($query);
    $extraNorm = [];
    foreach ($extra as $row) {
        $norm = normalize_extra_item($row);
        if ($norm) {
            $extraNorm[] = $norm;
        }
    }

    $results = dedupe_food_results(sanitize_food_list(array_merge($usda, $off, $extraNorm)));

    if (!empty($results)) {
        set_cache($cache_key, $results);
    }
    return $results;
}

/* ===== AUTOCOMPLETE ===== */
function autocomplete($query) {
    $cache_key = 'auto_v2_' . strtolower(trim($query));
    $cached = get_cache($cache_key);
    if ($cached) return $cached;

    $url = "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=" . USDA_API_KEY
         . "&query=" . urlencode($query) . "&pageSize=6&dataType=SR%20Legacy,Foundation";
    $response = @file_get_contents($url);
    $suggestions = [];
    if ($response) {
        $data = json_decode($response, true);
        foreach (($data['foods'] ?? []) as $f) {
            $suggestions[] = [
                'name' => ucwords(strtolower($f['description'] ?? '')),
                'category' => $f['foodCategory'] ?? '',
                'calories' => null
            ];
            // Extract calories
            foreach (($f['foodNutrients'] ?? []) as $n) {
                if (strtolower($n['nutrientName'] ?? '') === 'energy' && ($n['unitName'] ?? '') === 'KCAL') {
                    $suggestions[count($suggestions)-1]['calories'] = (float)$n['value'];
                    break;
                }
            }
        }
    }
    if (!empty($suggestions)) set_cache($cache_key, $suggestions);
    return $suggestions;
}

/* ===== HANDLE API REQUEST ===== */
if (basename($_SERVER['SCRIPT_FILENAME']) === 'food.php') {

    // Barcode lookup
    if (isset($_GET['barcode']) && !empty(trim($_GET['barcode']))) {
        $barcode = trim($_GET['barcode']);
        $cache_key = 'barcode_v2_' . $barcode;
        $cached = get_cache($cache_key);
        if ($cached) {
            echo json_encode(['success' => true, 'data' => sanitize_food_item($cached), 'type' => 'barcode']);
            exit;
        }
        $result = fetch_off_barcode($barcode);
        if ($result) {
            $clean = sanitize_food_item($result);
            set_cache($cache_key, $result);
            echo json_encode(['success' => true, 'data' => $clean, 'type' => 'barcode']);
        } else {
            echo json_encode(['success' => false, 'error' => 'Product not found for barcode: ' . $barcode]);
        }
        exit;
    }

    // USDA detail by FDC ID
    if (isset($_GET['fdcId']) && !empty(trim($_GET['fdcId']))) {
        $fdcId = intval($_GET['fdcId']);
        $cache_key = 'fdc_v4_' . $fdcId;
        $cached = get_cache($cache_key);
        if ($cached) {
            echo json_encode(['success' => true, 'data' => sanitize_food_item($cached), 'type' => 'detail']);
            exit;
        }
        $result = fetch_usda_detail($fdcId);
        if ($result) {
            set_cache($cache_key, $result);
            echo json_encode(['success' => true, 'data' => sanitize_food_item($result), 'type' => 'detail']);
        } else {
            echo json_encode(['success' => false, 'error' => 'Food not found for FDC ID: ' . $fdcId]);
        }
        exit;
    }

    // Autocomplete
    if (isset($_GET['autocomplete']) && !empty(trim($_GET['autocomplete']))) {
        $query = trim($_GET['autocomplete']);
        $suggestions = autocomplete($query);
        echo json_encode(['success' => true, 'data' => $suggestions, 'type' => 'autocomplete']);
        exit;
    }

    // Text search (default)
    if (isset($_GET['query']) && !empty(trim($_GET['query']))) {
        $query = trim($_GET['query']);
        $results = search_food($query);
        if (!empty($results)) {
            echo json_encode(['success' => true, 'data' => $results, 'count' => count($results), 'type' => 'search']);
        } else {
            echo json_encode(['success' => false, 'error' => 'No results found for: ' . $query, 'data' => []]);
        }
        exit;
    }

    echo json_encode(['success' => false, 'error' => 'Invalid request']);
    exit;
}
?>
