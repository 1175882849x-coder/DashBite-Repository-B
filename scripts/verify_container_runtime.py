"""Check the two manual-smoke fixes in a disposable Compose project.

Run after building the runtime image: python scripts/verify_container_runtime.py
No application writers start. Cleanup deletes only this script's unique temporary volume.
"""
import json
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen
import uuid

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {args}\n{result.stdout}{result.stderr}")
    return result.stdout.strip()


def main():
    project = "dashbite-b-regression-" + uuid.uuid4().hex[:8]
    with tempfile.TemporaryDirectory(prefix="dashbite-compose-") as scratch:
        override = Path(scratch) / "ports.yaml"
        override.write_text('services:\n  dashboard:\n    ports: !override\n      - "127.0.0.1::8501"\n', encoding="utf-8")
        compose = ["docker", "compose", "-p", project, "-f", str(ROOT / "compose.yaml"), "-f", str(override)]
        try:
            run(*compose, "up", "-d", "--no-deps", "--no-build", "dashboard")
            container = run(*compose, "ps", "-q", "dashboard")
            network = json.loads(run("docker", "network", "inspect", project + "_default"))[0]
            assert network["EnableIPv4"] is True and network["EnableIPv6"] is False
            details = json.loads(run("docker", "inspect", container))[0]
            endpoint = details["NetworkSettings"]["Networks"][project + "_default"]
            assert endpoint["IPAddress"] and not endpoint["GlobalIPv6Address"]
            port = run(*compose, "port", "dashboard", "8501").rsplit(":", 1)[1]
            url = f"http://127.0.0.1:{port}/_stcore/health"
            deadline = time.monotonic() + 60
            while True:
                try:
                    with urlopen(url, timeout=3) as response:
                        assert response.status == 200
                    break
                except (URLError, OSError):
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(1)
            print("PASS: explicit IPv4 network, IPv4 container address, host-published health HTTP 200")
            code = ('import os,runpy; os.chdir("/tmp"); '
                    'runpy.run_path("/app/pipeline/dashboard/app.py", run_name="regression_import"); '
                    'print("PASS: real dashboard script imports pipeline from /tmp using image environment")')
            print(run(*compose, "exec", "-T", "dashboard", "python", "-c", code))
            # Prove the check detects the original missing-PYTHONPATH failure.
            negative = subprocess.run(compose + ["exec", "-T", "-e", "PYTHONPATH=", "dashboard", "python", "-c", code],
                                      cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            assert negative.returncode != 0 and "No module named 'pipeline'" in negative.stderr
            print("PASS: removing PYTHONPATH reproduces ModuleNotFoundError (negative control)")
        finally:
            run(*compose, "down", "-v")
            print(f"Removed disposable project {project} and its volume")


if __name__ == "__main__":
    main()
