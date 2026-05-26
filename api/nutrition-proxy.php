<?php
/**
 * Macro & Meals — Nutrition API Proxy
 * Aggregates data from CalorieNinjas, FatSecret, and Open Food Facts
 * Keeps all API keys server-side (never exposed to client)
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Cache-Control: public, max-age=3600');

// --- API Keys (server-side only) ---
define('CALORIE_NINJAS_KEY', 'A91m82TSa73KuwFIgpHmcQ==Cm9TPIglOxGQ99B4');
define('FATSECRET_CLIENT_ID', 'bb21c49d786d488086d1ebaa3db4e6f2');
define('FATSECRET_CLIENT_SECRET', '21b7741e427c485f85957c5e4fab891a');

// --- Rate limiting (simple file-based) ---
$rateFile = sys_get_temp_dir() . '/mm_api_rate_' . md5($_SERVER['REMOTE_ADDR'] ?? 'unknown');
$now = time();
if (file_exists($rateFile)) {
    $data = json_decode(file_get_contents($rateFile), true);
    if ($data && $data['time'] > $now - 2 && $data['count'] > 5) {
        http_response_code(429);
        echo json_encode(['error' => 'Rate limit exceeded. Please wait a moment.']);
        exit;
    }
    if ($data && $data['time'] > $now - 2) {
        $data['count']++;
    } else {
        $data = ['time' => $now, 'count' => 1];
    }
} else {
    $data = ['time' => $now, 'count' => 1];
}
file_put_contents($rateFile, json_encode($data));

// --- Input ---
$action = $_GET['action'] ?? 'search';
$query = trim($_GET['q'] ?? '');

if (empty($query) && $action === 'search') {
    echo json_encode(['error' => 'Missing search query', 'results' => []]);
    exit;
}

// --- Helper: cURL request ---
function apiRequest($url, $headers = [], $postData = null) {
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 8,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_USERAGENT => 'MacroAndMeals/1.0 (macroandmeals.com)',
        CURLOPT_SSL_VERIFYPEER => true,
    ]);
    if ($postData) {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    }
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($httpCode >= 200 && $httpCode < 300) {
        return json_decode($response, true);
    }
    return null;
}

// ==============================
// CalorieNinjas Search
// ==============================
function searchCalorieNinjas($query) {
    $url = 'https://api.calorieninjas.com/v1/nutrition?query=' . urlencode($query);
    $data = apiRequest($url, ['X-Api-Key: ' . CALORIE_NINJAS_KEY]);
    $results = [];
    if ($data && isset($data['items'])) {
        foreach ($data['items'] as $item) {
            $results[] = [
                'source' => 'calorieninjas',
                'name' => ucwords($item['name'] ?? 'Unknown'),
                'serving' => ($item['serving_size_g'] ?? 100) . 'g',
                'serving_g' => $item['serving_size_g'] ?? 100,
                'calories' => round($item['calories'] ?? 0, 1),
                'protein' => round($item['protein_g'] ?? 0, 1),
                'carbs' => round($item['carbohydrates_total_g'] ?? 0, 1),
                'fat' => round($item['fat_total_g'] ?? 0, 1),
                'fiber' => round($item['fiber_g'] ?? 0, 1),
                'sugar' => round($item['sugar_g'] ?? 0, 1),
                'sodium' => round($item['sodium_mg'] ?? 0, 1),
                'potassium' => round($item['potassium_mg'] ?? 0, 1),
                'cholesterol' => round($item['cholesterol_mg'] ?? 0, 1),
                'saturated_fat' => round($item['fat_saturated_g'] ?? 0, 1),
            ];
        }
    }
    return $results;
}

// ==============================
// FatSecret Search (OAuth 2.0)
// ==============================
function getFatSecretToken() {
    $cacheFile = sys_get_temp_dir() . '/mm_fatsecret_token.json';
    if (file_exists($cacheFile)) {
        $cached = json_decode(file_get_contents($cacheFile), true);
        if ($cached && isset($cached['expires_at']) && $cached['expires_at'] > time() + 60) {
            return $cached['access_token'];
        }
    }
    $data = apiRequest(
        'https://oauth.fatsecret.com/connect/token',
        ['Content-Type: application/x-www-form-urlencoded'],
        'grant_type=client_credentials'
            . '&client_id=' . FATSECRET_CLIENT_ID
            . '&client_secret=' . FATSECRET_CLIENT_SECRET
            . '&scope=basic'
    );
    if ($data && isset($data['access_token'])) {
        $data['expires_at'] = time() + ($data['expires_in'] ?? 86400);
        file_put_contents($cacheFile, json_encode($data));
        return $data['access_token'];
    }
    return null;
}

function searchFatSecret($query) {
    $token = getFatSecretToken();
    if (!$token) return [];

    $url = 'https://platform.fatsecret.com/rest/server.api';
    $params = http_build_query([
        'method' => 'foods.search',
        'search_expression' => $query,
        'format' => 'json',
        'max_results' => 10,
    ]);
    $data = apiRequest($url . '?' . $params, ['Authorization: Bearer ' . $token]);
    $results = [];
    if ($data && isset($data['foods']['food'])) {
        $foods = $data['foods']['food'];
        if (isset($foods['food_id'])) $foods = [$foods];
        foreach ($foods as $food) {
            $desc = $food['food_description'] ?? '';
            $parsed = parseFatSecretDescription($desc);
            $results[] = [
                'source' => 'fatsecret',
                'name' => $food['food_name'] ?? 'Unknown',
                'brand' => $food['brand_name'] ?? '',
                'serving' => $parsed['serving'] ?? 'Per serving',
                'serving_g' => $parsed['serving_g'] ?? 100,
                'calories' => $parsed['calories'] ?? 0,
                'protein' => $parsed['protein'] ?? 0,
                'carbs' => $parsed['carbs'] ?? 0,
                'fat' => $parsed['fat'] ?? 0,
                'fiber' => 0,
                'sugar' => 0,
                'sodium' => 0,
                'potassium' => 0,
                'cholesterol' => 0,
                'saturated_fat' => 0,
                'food_id' => $food['food_id'] ?? '',
            ];
        }
    }
    return $results;
}

function parseFatSecretDescription($desc) {
    $result = ['serving' => '', 'serving_g' => 100, 'calories' => 0, 'protein' => 0, 'carbs' => 0, 'fat' => 0];
    if (preg_match('/^Per (.+?) -/', $desc, $m)) {
        $result['serving'] = trim($m[1]);
        if (preg_match('/(\d+\.?\d*)g/', $result['serving'], $gm)) {
            $result['serving_g'] = floatval($gm[1]);
        }
    }
    if (preg_match('/Calories:\s*([\d.]+)/', $desc, $m)) $result['calories'] = floatval($m[1]);
    if (preg_match('/Fat:\s*([\d.]+)g/', $desc, $m)) $result['fat'] = floatval($m[1]);
    if (preg_match('/Carbs:\s*([\d.]+)g/', $desc, $m)) $result['carbs'] = floatval($m[1]);
    if (preg_match('/Protein:\s*([\d.]+)g/', $desc, $m)) $result['protein'] = floatval($m[1]);
    return $result;
}

// ==============================
// FatSecret Food Detail
// ==============================
function getFatSecretDetail($foodId) {
    $token = getFatSecretToken();
    if (!$token) return null;

    $url = 'https://platform.fatsecret.com/rest/server.api';
    $params = http_build_query([
        'method' => 'food.get.v4',
        'food_id' => $foodId,
        'format' => 'json',
        'include_sub_categories' => 'true',
    ]);
    $data = apiRequest($url . '?' . $params, ['Authorization: Bearer ' . $token]);
    if ($data && isset($data['food'])) {
        return $data['food'];
    }
    return null;
}

// ==============================
// Open Food Facts Search
// ==============================
function searchOpenFoodFacts($query) {
    $url = 'https://world.openfoodfacts.org/cgi/search.pl?' . http_build_query([
        'search_terms' => $query,
        'search_simple' => 1,
        'action' => 'process',
        'json' => 1,
        'page_size' => 10,
        'fields' => 'product_name,brands,nutriments,image_front_small_url,serving_size',
    ]);
    $data = apiRequest($url);
    $results = [];
    if ($data && isset($data['products'])) {
        foreach ($data['products'] as $product) {
            $n = $product['nutriments'] ?? [];
            $name = $product['product_name'] ?? '';
            if (empty($name)) continue;
            $brand = $product['brands'] ?? '';
            if ($brand) $name .= ' (' . $brand . ')';
            $results[] = [
                'source' => 'openfoodfacts',
                'name' => $name,
                'serving' => $product['serving_size'] ?? '100g',
                'serving_g' => 100,
                'calories' => round($n['energy-kcal_100g'] ?? $n['energy-kcal'] ?? 0, 1),
                'protein' => round($n['proteins_100g'] ?? $n['proteins'] ?? 0, 1),
                'carbs' => round($n['carbohydrates_100g'] ?? $n['carbohydrates'] ?? 0, 1),
                'fat' => round($n['fat_100g'] ?? $n['fat'] ?? 0, 1),
                'fiber' => round($n['fiber_100g'] ?? $n['fiber'] ?? 0, 1),
                'sugar' => round($n['sugars_100g'] ?? $n['sugars'] ?? 0, 1),
                'sodium' => round(($n['sodium_100g'] ?? $n['sodium'] ?? 0) * 1000, 1),
                'potassium' => round(($n['potassium_100g'] ?? $n['potassium'] ?? 0) * 1000, 1),
                'cholesterol' => round(($n['cholesterol_100g'] ?? 0) * 1000, 1),
                'saturated_fat' => round($n['saturated-fat_100g'] ?? $n['saturated-fat'] ?? 0, 1),
                'image' => $product['image_front_small_url'] ?? '',
            ];
        }
    }
    return $results;
}

// ==============================
// Route
// ==============================
switch ($action) {
    case 'search':
        $allResults = [];
        // CalorieNinjas (primary — always reliable)
        $cn = searchCalorieNinjas($query);
        $allResults = array_merge($allResults, $cn);
        // FatSecret (may fail on non-whitelisted IPs)
        $fs = searchFatSecret($query);
        $allResults = array_merge($allResults, $fs);
        // Open Food Facts (free, may be slow)
        $off = searchOpenFoodFacts($query);
        $allResults = array_merge($allResults, $off);

        // Deduplicate by name similarity
        $seen = [];
        $unique = [];
        foreach ($allResults as $r) {
            $key = strtolower(preg_replace('/[^a-z0-9]/', '', $r['name']));
            if (!isset($seen[$key])) {
                $seen[$key] = true;
                $unique[] = $r;
            }
        }

        echo json_encode([
            'query' => $query,
            'count' => count($unique),
            'results' => $unique,
            'sources' => [
                'calorieninjas' => count($cn),
                'fatsecret' => count($fs),
                'openfoodfacts' => count($off),
            ],
        ]);
        break;

    case 'detail':
        $foodId = $_GET['food_id'] ?? '';
        $source = $_GET['source'] ?? '';
        if ($source === 'fatsecret' && $foodId) {
            $detail = getFatSecretDetail($foodId);
            echo json_encode(['food' => $detail]);
        } else {
            echo json_encode(['error' => 'Invalid detail request']);
        }
        break;

    default:
        echo json_encode(['error' => 'Unknown action']);
        break;
}
