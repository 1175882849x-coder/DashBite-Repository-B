import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from pipeline.healthcheck import check


@pytest.mark.unit
@pytest.mark.parametrize("status, expected", [(200, 0), (204, 1), (503, 1)])
def test_http_status(status, expected):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(status)
            self.end_headers()
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert check(f"http://127.0.0.1:{server.server_port}/_stcore/health") == expected
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.unit
def test_connection_failure():
    server = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
    port = server.server_port
    server.server_close()
    assert check(f"http://127.0.0.1:{port}") == 1


@pytest.mark.unit
def test_request_timeout():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            time.sleep(0.2)
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert check(f"http://127.0.0.1:{server.server_port}", timeout=0.02) == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

@pytest.mark.unit
def test_redirect_is_not_a_healthy_endpoint():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302 if self.path == '/_stcore/health' else 200)
            if self.path == '/_stcore/health':
                self.send_header('Location', '/login')
            self.end_headers()
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert check(f'http://127.0.0.1:{server.server_port}/_stcore/health') == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
