<?php
/**
 * Macro & Meals — Nutrition API Proxy
 * Hides API keys for CalorieNinjas and FatSecret
 * USDA and Open Food Facts are called directly from client (public/free)
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Cache-Control: public, max-age=1800');

// --- API Keys (server-side only) ---
define('CN_KEY', 'A91m82TSa73KuwFIgpHmcQ==Cm9TPIglOxGQ99B4');
define('FS_CLIENT_ID', 'bb21c49d786d488086d1ebaa3db4e6f2');
define('FS_CLIENT_SECRET', '21b7741e427c485f85957c5e4fab891a');

// --- Rate limiting ---
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$rateFile = sys_get_temp_dir() . '/mm_rate_' . md5($ip);
$now = time();
if (file_exists($rateFile)) {
    $rd = json_decode(file_get_contents($rateFile), true);
    if ($rd && $rd['t'] > $now - 2 && $rd['c'] > 8) {
        http_response_code(429);
        echo json_encode(['error' => 'Rate limited', 'results' => []]);
        exit;
    }
    $rd = ($rd && $rd['t'] > $now - 2) ? ['t' => $rd['t'], 'c' => $rd['c'] + 1] : ['t' => $now, 'c' => 1];
} else {
    $rd = ['t' => $now, 'c' => 1];
}
@file_put_contents($rateFile, json_encode($rd));

// --- Input ---
$action = $_GET['action'] ?? '';
$query = trim($_GET['q'] ?? '');

function apiGet($url, $headers = []) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 8,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_USERAGENT => 'MacroAndMeals/1.0 (macroandmeals.com)',
        CURLOPT_SSL_VERIFYPEER => true,
    ]);
    $r = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return ($code >= 200 && $code < 300) ? json_decode($r, true) : null;
}

function apiPost($url, $headers, $body) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 8,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $body,
        CURLOPT_SSL_VERIFYPEER => true,
    ]);
    $r = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return ($code >= 200 && $code < 300) ? json_decode($r, true) : null;
}

function r2($v) { return round($v ?? 0, 1); }

// ======== CalorieNinjas ========
if ($action === 'search_cn' && $query) {
    $data = apiGet(
        'https://api.calorieninjas.com/v1/nutrition?query=' . urlencode($query),
        ['X-Api-Key: ' . CN_KEY]
    );
    $results = [];
    if ($data && isset($data['items'])) {
        foreach ($data['items'] as $item) {
            $results[] = [
                'source' => 'calorieninjas',
                'name' => ucwords($item['name'] ?? 'Unknown'),
                'serving' => ($item['serving_size_g'] ?? 100) . 'g',
                'serving_g' => $item['serving_size_g'] ?? 100,
                'calories' => r2($item['calories']),
                'protein' => r2($item['protein_g']),
                'carbs' => r2($item['carbohydrates_total_g']),
                'fat' => r2($item['fat_total_g']),
                'fiber' => r2($item['fiber_g']),
                'sugar' => r2($item['sugar_g']),
                'sodium' => r2($item['sodium_mg']),
                'potassium' => r2($item['potassium_mg']),
                'cholesterol' => r2($item['cholesterol_mg']),
                'saturated_fat' => r2($item['fat_saturated_g']),
            ];
        }
    }
    echo json_encode(['results' => $results]);
    exit;
}

// ======== FatSecret ========
if ($action === 'search_fs' && $query) {
    // Get token
    $tokenFile = sys_get_temp_dir() . '/mm_fs_token.json';
    $token = null;
    if (file_exists($tokenFile)) {
        $tc = json_decode(file_get_contents($tokenFile), true);
        if ($tc && isset($tc['exp']) && $tc['exp'] > time() + 60) {
            $token = $tc['token'];
        }
    }
    if (!$token) {
        $td = apiPost(
            'https://oauth.fatsecret.com/connect/token',
            ['Content-Type: application/x-www-form-urlencoded'],
            'grant_type=client_credentials&client_id=' . FS_CLIENT_ID . '&client_secret=' . FS_CLIENT_SECRET . '&scope=basic'
        );
        if ($td && isset($td['access_token'])) {
            $token = $td['access_token'];
            @file_put_contents($tokenFile, json_encode(['token' => $token, 'exp' => time() + ($td['expires_in'] ?? 86400)]));
        }
    }

    $results = [];
    if ($token) {
        $params = http_build_query([
            'method' => 'foods.search',
            'search_expression' => $query,
            'format' => 'json',
            'max_results' => 8,
        ]);
        $data = apiGet(
            'https://platform.fatsecret.com/rest/server.api?' . $params,
            ['Authorization: Bearer ' . $token]
        );
        if ($data && isset($data['foods']['food'])) {
            $foods = $data['foods']['food'];
            if (isset($foods['food_id'])) $foods = [$foods];
            foreach ($foods as $f) {
                $desc = $f['food_description'] ?? '';
                $p = ['cal' => 0, 'pro' => 0, 'carb' => 0, 'fat' => 0, 'serving' => 'Per serving', 'sg' => 100];
                if (preg_match('/^Per (.+?) -/', $desc, $m)) {
                    $p['serving'] = trim($m[1]);
                    if (preg_match('/([\d.]+)\s*g\b/', $p['serving'], $gm)) $p['sg'] = floatval($gm[1]);
                }
                if (preg_match('/Calories:\s*([\d.]+)/', $desc, $m)) $p['cal'] = floatval($m[1]);
                if (preg_match('/Fat:\s*([\d.]+)g/', $desc, $m)) $p['fat'] = floatval($m[1]);
                if (preg_match('/Carbs:\s*([\d.]+)g/', $desc, $m)) $p['carb'] = floatval($m[1]);
                if (preg_match('/Protein:\s*([\d.]+)g/', $desc, $m)) $p['pro'] = floatval($m[1]);

                $results[] = [
                    'source' => 'fatsecret',
                    'name' => $f['food_name'] ?? 'Unknown',
                    'brand' => $f['brand_name'] ?? '',
                    'serving' => $p['serving'],
                    'serving_g' => $p['sg'],
                    'calories' => $p['cal'],
                    'protein' => $p['pro'],
                    'carbs' => $p['carb'],
                    'fat' => $p['fat'],
                    'fiber' => 0,
                    'sugar' => 0,
                    'sodium' => 0,
                    'potassium' => 0,
                    'cholesterol' => 0,
                    'saturated_fat' => 0,
                    'food_id' => $f['food_id'] ?? '',
                ];
            }
        }
    }
    echo json_encode(['results' => $results]);
    exit;
}

// Fallback
echo json_encode(['error' => 'Invalid action or missing query', 'results' => []]);
