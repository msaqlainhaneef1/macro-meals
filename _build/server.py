#!/usr/bin/env python3
"""Local dev server with custom 404 page support.

Usage: python3 server.py [port]
Serves files from public_html/ with automatic 404.html fallback.
"""
import http.server
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Repo root (flat structure)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        # Check if the requested path exists
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            index = os.path.join(path, 'index.html')
            if not os.path.exists(index):
                self.send_custom_404()
                return
        elif not os.path.exists(path):
            self.send_custom_404()
            return
        super().do_GET()

    def send_custom_404(self):
        error_page = os.path.join(ROOT, '404.html')
        if os.path.exists(error_page):
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            with open(error_page, 'rb') as f:
                content = f.read()
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, 'File not found')


if __name__ == '__main__':
    with http.server.HTTPServer(('', PORT), Handler) as httpd:
        print(f'Serving Macro & Meals at http://localhost:{PORT}')
        print(f'Root: {ROOT}')
        print(f'Custom 404: {os.path.join(ROOT, "404.html")}')
        httpd.serve_forever()
