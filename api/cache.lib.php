<?php
/**
 * API response cache — zero disk usage on hosting.
 *
 * Layers (fastest first):
 *   1. Request memory  — dedupes within one HTTP request
 *   2. APCu (optional) — shared in-RAM cache when the PHP extension is enabled
 *
 * Browser caching is handled separately via api_send_json() Cache-Control / ETag.
 */

const API_CACHE_PREFIX = 'mm_v1_';

/** @var array<string, array{exp: int, data: mixed}> */
$GLOBALS['_api_request_cache'] = [];

const API_CACHE_TTL_SEARCH = 1800;      // 30 min — popular queries
const API_CACHE_TTL_AUTOCOMPLETE = 900; // 15 min
const API_CACHE_TTL_DETAIL = 86400;     // 24 h — stable food records
const API_CACHE_TTL_BARCODE = 86400;  // 24 h

function api_cache_key(string $logicalKey): string {
    return API_CACHE_PREFIX . hash('sha256', $logicalKey);
}

function api_cache_apcu_available(): bool {
    return function_exists('apcu_enabled') && apcu_enabled();
}

/**
 * @return mixed|null
 */
function api_cache_get(string $logicalKey, int $ttl) {
    $key = api_cache_key($logicalKey);
    $now = time();

    if (isset($GLOBALS['_api_request_cache'][$key])) {
        $entry = $GLOBALS['_api_request_cache'][$key];
        if ($entry['exp'] >= $now) {
            return $entry['data'];
        }
        unset($GLOBALS['_api_request_cache'][$key]);
    }

    if (api_cache_apcu_available()) {
        $success = false;
        $stored = apcu_fetch($key, $success);
        if ($success && is_array($stored) && isset($stored['exp'], $stored['data']) && $stored['exp'] >= $now) {
            $GLOBALS['_api_request_cache'][$key] = $stored;
            return $stored['data'];
        }
        if ($success) {
            apcu_delete($key);
        }
    }

    return null;
}

/**
 * @param mixed $data
 */
function api_cache_set(string $logicalKey, $data, int $ttl): bool {
    if ($data === null) {
        return false;
    }
    $key = api_cache_key($logicalKey);
    $entry = ['exp' => time() + max(1, $ttl), 'data' => $data];
    $GLOBALS['_api_request_cache'][$key] = $entry;

    if (api_cache_apcu_available()) {
        return apcu_store($key, $entry, $ttl + 60);
    }
    return true;
}

function api_cache_delete(string $logicalKey): void {
    $key = api_cache_key($logicalKey);
    unset($GLOBALS['_api_request_cache'][$key]);
    if (api_cache_apcu_available()) {
        apcu_delete($key);
    }
}

/**
 * Load from cache or compute, then store on success.
 *
 * @template T
 * @param callable():T $loader
 * @return T
 */
function api_cache_remember(string $logicalKey, int $ttl, callable $loader) {
    $cached = api_cache_get($logicalKey, $ttl);
    if ($cached !== null) {
        return $cached;
    }
    $data = $loader();
    $empty = $data === null || $data === false || $data === [];
    if (!$empty) {
        api_cache_set($logicalKey, $data, $ttl);
    }
    return $data;
}

/**
 * JSON response with optional browser cache (no files on disk).
 *
 * @param array<string, mixed> $payload
 */
function api_send_json(array $payload, int $browserMaxAge = 0): void {
    $json = json_encode($payload, JSON_UNESCAPED_UNICODE);
    if ($json === false) {
        $json = '{"success":false,"error":"Response encoding failed"}';
    }

    if ($browserMaxAge > 0) {
        header('Cache-Control: public, max-age=' . $browserMaxAge . ', stale-while-revalidate=300');
        $etag = '"' . hash('sha256', $json) . '"';
        header('ETag: ' . $etag);
        $inm = trim($_SERVER['HTTP_IF_NONE_MATCH'] ?? '', " \t\n\r\0\x0B\"");
        $etagBare = trim($etag, '"');
        if ($inm !== '' && ($inm === $etagBare || $inm === $etag)) {
            http_response_code(304);
            exit;
        }
    } else {
        header('Cache-Control: no-store');
    }

    echo $json;
}
