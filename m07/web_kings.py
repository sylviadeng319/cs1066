'''Local web server for the Kings browser interface.'''

import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from kings import KingsGame, rules

WEB_DIR = Path(__file__).resolve().parent / 'web'
STATIC_FILES = {
    '/': ('index.html', 'text/html; charset=utf-8'),
    '/index.html': ('index.html', 'text/html; charset=utf-8'),
    '/style.css': ('style.css', 'text/css; charset=utf-8'),
    '/game.js': ('game.js', 'text/javascript; charset=utf-8'),
}

game = None


class KingsHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write('%s - %s\n' % (self.address_string(), format % args))

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filename, content_type):
        path = WEB_DIR / filename
        if not path.is_file():
            self.send_error(404)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get('Content-Length', '0') or 0)
        raw = self.rfile.read(length) if length else b''
        if not raw:
            return {}
        return json.loads(raw.decode('utf-8'))

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/state':
            if game is None:
                self._send_json({'phase': 'splash'})
            else:
                self._send_json(game.state())
            return
        if path == '/api/rules':
            self._send_json({'rules': rules})
            return
        if path in STATIC_FILES:
            self._send_file(*STATIC_FILES[path])
            return
        self.send_error(404)

    def do_POST(self):
        global game
        path = urlparse(self.path).path
        try:
            data = self._read_json()
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json({'error': 'Bad request'}, 400)
            return

        if path == '/api/new':
            game = KingsGame(vs_ai=bool(data.get('vs_ai', True)))
            self._send_json(game.state())
            return

        if game is None:
            self._send_json({'error': 'Start a new game first.'}, 400)
            return

        if path == '/api/ai':
            self._send_json(game.play_ai())
            return

        if path == '/api/action':
            action = data.get('action')
            player = data.get('player')
            if action == 'stock':
                result = game.take_stock(player)
            elif action == 'discard':
                result = game.take_discard(player)
            elif action == 'drop3':
                result = game.drop_three(player, data.get('indices', []))
            elif action == 'discard_card':
                result = game.discard_card(player, data.get('index'))
            else:
                self._send_json({'error': 'Unknown action'}, 400)
                return
            self._send_json(result)
            return

        self.send_error(404)


def run_server(port=8765, open_browser=True):
    host = '127.0.0.1'
    server = None
    for candidate in range(port, port + 15):
        try:
            server = HTTPServer((host, candidate), KingsHandler)
            port = candidate
            break
        except OSError:
            continue
    if server is None:
        raise RuntimeError('Could not find an open port for the Kings table.')

    url = f'http://{host}:{port}/'
    print(f'Kings is ready at {url}')
    print('Press Ctrl+C to stop.')
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nClosing the table.')
        server.server_close()


if __name__ == '__main__':
    run_server()
