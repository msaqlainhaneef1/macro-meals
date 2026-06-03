<?php
/**
 * Supplemental food search (server-side only).
 */

if (!defined('CN_KEY')) {
    define('CN_KEY', 'A91m82TSa73KuwFIgpHmcQ==Cm9TPIglOxGQ99B4');
}
if (!defined('FS_CLIENT_ID')) {
    define('FS_CLIENT_ID', 'bb21c49d786d488086d1ebaa3db4e6f2');
    define('FS_CLIENT_SECRET', '21b7741e427c485f85957c5e4fab891a');
}

function extra_api_get($url, $headers = []) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 8,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_USERAGENT => 'MacroAndMeals/1.0',
        CURLOPT_SSL_VERIFYPEER => true,
    ]);
    $r = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return ($code >= 200 && $code < 300) ? json_decode($r, true) : null;
}

function extra_api_post($url, $headers, $body) {
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

function extra_r2($v) {
    return round($v ?? 0, 1);
}

function extra_search_calorieninjas($query) {
    $data = extra_api_get(
        'https://api.calorieninjas.com/v1/nutrition?query=' . urlencode($query),
        ['X-Api-Key: ' . CN_KEY]
    );
    $results = [];
    if ($data && isset($data['items'])) {
        foreach ($data['items'] as $item) {
            $sg = (float) ($item['serving_size_g'] ?? 100);
            if ($sg <= 0) {
                $sg = 100;
            }
            $results[] = [
                'name' => ucwords($item['name'] ?? 'Unknown'),
                'serving' => $sg . 'g',
                'servingGrams' => $sg,
                'nutrients' => [
                    'calories' => extra_r2($item['calories']),
                    'protein' => extra_r2($item['protein_g']),
                    'carbs' => extra_r2($item['carbohydrates_total_g']),
                    'fat' => extra_r2($item['fat_total_g']),
                    'fiber' => extra_r2($item['fiber_g']),
                    'sugars' => extra_r2($item['sugar_g']),
                    'sodium' => extra_r2($item['sodium_mg']),
                    'potassium' => extra_r2($item['potassium_mg']),
                    'cholesterol' => extra_r2($item['cholesterol_mg']),
                    'saturated_fat' => extra_r2($item['fat_saturated_g']),
                ],
                'foodType' => 'general',
            ];
        }
    }
    return $results;
}

function extra_search_fatsecret($query) {
    $tokenFile = sys_get_temp_dir() . '/mm_fs_token.json';
    $token = null;
    if (file_exists($tokenFile)) {
        $tc = json_decode(file_get_contents($tokenFile), true);
        if ($tc && isset($tc['exp']) && $tc['exp'] > time() + 60) {
            $token = $tc['token'];
        }
    }
    if (!$token) {
        $td = extra_api_post(
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
    if (!$token) {
        return $results;
    }

    $params = http_build_query([
        'method' => 'foods.search',
        'search_expression' => $query,
        'format' => 'json',
        'max_results' => 6,
    ]);
    $data = extra_api_get(
        'https://platform.fatsecret.com/rest/server.api?' . $params,
        ['Authorization: Bearer ' . $token]
    );

    if ($data && isset($data['foods']['food'])) {
        $foods = $data['foods']['food'];
        if (isset($foods['food_id'])) {
            $foods = [$foods];
        }
        foreach ($foods as $f) {
            $desc = $f['food_description'] ?? '';
            $p = ['cal' => 0, 'pro' => 0, 'carb' => 0, 'fat' => 0, 'serving' => 'Per serving', 'sg' => 100];
            if (preg_match('/^Per (.+?) -/', $desc, $m)) {
                $p['serving'] = trim($m[1]);
                if (preg_match('/([\d.]+)\s*g\b/', $p['serving'], $gm)) {
                    $p['sg'] = floatval($gm[1]);
                }
            }
            if (preg_match('/Calories:\s*([\d.]+)/', $desc, $m)) {
                $p['cal'] = floatval($m[1]);
            }
            if (preg_match('/Fat:\s*([\d.]+)g/', $desc, $m)) {
                $p['fat'] = floatval($m[1]);
            }
            if (preg_match('/Carbs:\s*([\d.]+)g/', $desc, $m)) {
                $p['carb'] = floatval($m[1]);
            }
            if (preg_match('/Protein:\s*([\d.]+)g/', $desc, $m)) {
                $p['pro'] = floatval($m[1]);
            }

            $results[] = [
                'name' => $f['food_name'] ?? 'Unknown',
                'serving' => $p['serving'],
                'servingGrams' => $p['sg'],
                'nutrients' => [
                    'calories' => $p['cal'],
                    'protein' => $p['pro'],
                    'carbs' => $p['carb'],
                    'fat' => $p['fat'],
                ],
                'foodType' => 'branded',
            ];
        }
    }
    return $results;
}

function extra_search_combined($query) {
    $cn = extra_search_calorieninjas($query);
    $fs = extra_search_fatsecret($query);
    return array_merge($cn, $fs);
}
