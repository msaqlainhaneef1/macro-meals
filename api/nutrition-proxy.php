<?php
/**
 * Macro & Meals — Server-side nutrition search (keys never sent to browser).
 */
require_once __DIR__ . '/extra-search.lib.php';
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Cache-Control: public, max-age=1800');

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

if (($action === 'search' || $action === 'search_cn' || $action === 'search_fs') && $query) {
    $raw = extra_search_combined($query);
    $results = [];
    foreach ($raw as $row) {
        $item = [
            'name' => $row['name'] ?? 'Unknown',
            'serving' => $row['serving'] ?? '100g',
            'servingGrams' => $row['servingGrams'] ?? 100,
            'foodType' => $row['foodType'] ?? 'general',
            'nutrients' => $row['nutrients'] ?? [],
        ];
        $results[] = $item;
    }
    echo json_encode(['success' => true, 'results' => $results]);
    exit;
}

echo json_encode(['success' => false, 'results' => []]);
