<?php
/**
 * Advanced Food Search & Nutrition API
 * Integrates USDA FoodData Central and Open Food Facts.
 * 
 * Endpoints:
 *   ?query=chicken breast        — Text search (returns up to 10 results)
 *   ?barcode=3017620422003       — Barcode lookup (Open Food Facts)
 *   ?fdcId=171705                — USDA food detail by FDC ID
 *   ?autocomplete=chic           — Quick autocomplete suggestions
 */

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
        $name = strtolower($n['nutrientName'] ?? '');
        $val = isset($n['value']) ? (float)$n['value'] : null;
        $unit = strtoupper($n['unitName'] ?? '');
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
        if (empty($nutrients['calories']) && empty($nutrients['protein'])) continue;

        $results[] = [
            'id' => 'usda_' . ($food['fdcId'] ?? ''),
            'fdcId' => $food['fdcId'] ?? null,
            'name' => ucwords(strtolower($food['description'] ?? 'Unknown Food')),
            'brand' => $food['brandOwner'] ?? $food['brandName'] ?? null,
            'category' => $food['foodCategory'] ?? null,
            'dataType' => $food['dataType'] ?? null,
            'serving' => $food['servingSize'] ? ($food['servingSize'] . ' ' . ($food['servingSizeUnit'] ?? 'g')) : '100g',
            'servingText' => $food['householdServingFullText'] ?? null,
            'nutrients' => $nutrients,
            'source' => 'USDA FoodData Central',
            'sourceIcon' => 'usda'
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

    return [
        'id' => 'usda_' . $food['fdcId'],
        'fdcId' => $food['fdcId'],
        'name' => ucwords(strtolower($food['description'] ?? 'Unknown Food')),
        'brand' => $food['brandOwner'] ?? $food['brandName'] ?? null,
        'category' => $food['foodCategory'] ?? null,
        'dataType' => $food['dataType'] ?? null,
        'ingredients' => $food['ingredients'] ?? null,
        'serving' => isset($food['servingSize']) ? ($food['servingSize'] . ' ' . ($food['servingSizeUnit'] ?? 'g')) : '100g',
        'servingText' => $food['householdServingFullText'] ?? null,
        'nutrients' => $nutrients,
        'source' => 'USDA FoodData Central',
        'sourceIcon' => 'usda'
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
        'source' => 'Open Food Facts',
        'sourceIcon' => 'off'
    ];
}

/* ===== COMBINED SEARCH ===== */
function search_food($query) {
    $cache_key = 'search_v2_' . strtolower(trim($query));
    $cached = get_cache($cache_key);
    if ($cached) return $cached;

    // Fetch from both sources in parallel (or sequential in PHP)
    $usda = fetch_usda_search($query, 6);
    $off = fetch_off_search($query, 4);

    // Merge results — USDA first (more accurate for whole foods), OFF for packaged
    $results = array_merge($usda, $off);

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
            echo json_encode(['success' => true, 'data' => $cached, 'type' => 'barcode']);
            exit;
        }
        $result = fetch_off_barcode($barcode);
        if ($result) {
            set_cache($cache_key, $result);
            echo json_encode(['success' => true, 'data' => $result, 'type' => 'barcode']);
        } else {
            echo json_encode(['success' => false, 'error' => 'Product not found for barcode: ' . $barcode]);
        }
        exit;
    }

    // USDA detail by FDC ID
    if (isset($_GET['fdcId']) && !empty(trim($_GET['fdcId']))) {
        $fdcId = intval($_GET['fdcId']);
        $cache_key = 'fdc_v2_' . $fdcId;
        $cached = get_cache($cache_key);
        if ($cached) {
            echo json_encode(['success' => true, 'data' => $cached, 'type' => 'detail']);
            exit;
        }
        $result = fetch_usda_detail($fdcId);
        if ($result) {
            set_cache($cache_key, $result);
            echo json_encode(['success' => true, 'data' => $result, 'type' => 'detail']);
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

    // No valid params
    echo json_encode([
        'success' => false,
        'error' => 'Missing parameter. Use ?query=, ?barcode=, ?fdcId=, or ?autocomplete=',
        'endpoints' => [
            'search' => '?query=chicken breast',
            'barcode' => '?barcode=3017620422003',
            'detail' => '?fdcId=171705',
            'autocomplete' => '?autocomplete=chick'
        ]
    ]);
    exit;
}
?>
