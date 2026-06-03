<?php
/**
 * PHP dev-server router for local development.
 *
 * Usage:
 *   php -S localhost:8080 -t . _build/php-router.php
 *
 * Goal:
 * - Let the built-in server serve existing files normally (including .php APIs).
 * - Fall back to local `404.html` for everything else (matching the Python server behavior).
 */

declare(strict_types=1);

$docRoot = realpath(__DIR__ . '/..');
$requestPath = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
if ($requestPath === false) {
    $requestPath = '/';
}

$fsPath = $docRoot . $requestPath;

// If the requested path points to an actual file or directory, let the built-in server handle it.
// (This ensures API PHP files like /api/nutrition-proxy.php execute correctly.)
if (is_file($fsPath) || is_dir($fsPath)) {
    return false;
}

$errorPage = $docRoot . '/404.html';
if (is_file($errorPage)) {
    http_response_code(404);
    header('Content-Type: text/html; charset=utf-8');
    readfile($errorPage);
    return true;
}

http_response_code(404);
header('Content-Type: text/plain; charset=utf-8');
echo '404 Not Found';
return true;

