"""Dashboard endpoint probe; does not establish pipeline correctness."""
import sys
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, build_opener

URL = "http://127.0.0.1:8501/_stcore/health"


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def check(url: str = URL, timeout: float = 3.0) -> int:
    try:
        with build_opener(_RejectRedirects).open(url, timeout=timeout) as response:
            if response.status == 200:
                return 0
            print(f"dashboard health: HTTP {response.status}", file=sys.stderr)
    except (URLError, OSError, TimeoutError) as error:
        print(f"dashboard health: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(check())
