#!/usr/bin/env python3
"""Smoke-test admin-frontend against a mock admin API."""

from __future__ import annotations

import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[2]
ADMIN_FRONTEND_DIR = ROOT_DIR / "admin-frontend"
MOCK_STATUS = {
    "artifactCount": 7,
    "rawFiles": {
        "total": 9,
        "fetched": 8,
        "fetchFailed": 1,
        "processPending": 2,
        "processProcessed": 6,
        "processFailed": 1,
    },
    "crawlFiles": {"completed": 6, "failed": 1},
    "crawlUsers": {"completed": 3, "pending": 2},
    "latest": {
        "fetchedAt": "2026-01-01T00:02:00+00:00",
        "processedAt": "2026-01-01T00:03:00+00:00",
        "scannedAt": "2026-01-01T00:04:00+00:00",
    },
    "recentErrors": [
        {
            "kind": "fetch",
            "player": "mock-player",
            "name": "morgue-mock-player-20260101-000001.txt",
            "message": "mock fetch failure",
            "at": "2026-01-01T00:05:00+00:00",
        }
    ],
}


class MockAdminApiHandler(BaseHTTPRequestHandler):
    request_count = 0

    def do_GET(self) -> None:
        if self.path != "/admin/crawl-status":
            self.send_response(404)
            self.end_headers()
            return

        type(self).request_count += 1
        body = json.dumps(MOCK_STATUS).encode("utf-8")
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    chrome = _find_chrome()
    if chrome is None:
        print("google-chrome or chromium is required for this smoke test.", file=sys.stderr)
        return 1

    mock_port = _free_port()
    frontend_port = _free_port()
    mock_server = ThreadingHTTPServer(("127.0.0.1", mock_port), MockAdminApiHandler)
    mock_process = None
    frontend_process: subprocess.Popen[str] | None = None

    try:
        mock_process = _serve_in_background(mock_server)
        frontend_process = _start_frontend(mock_port, frontend_port)
        frontend_url = f"http://127.0.0.1:{frontend_port}"
        _wait_for_url(frontend_url, frontend_process)
        dom = _render_dom(chrome, frontend_url)
        _assert_rendered(dom)
        if MockAdminApiHandler.request_count < 1:
            raise AssertionError("admin frontend did not request /admin/crawl-status")
    finally:
        if frontend_process is not None:
            _terminate(frontend_process)
        if mock_process is not None:
            mock_server.shutdown()
            mock_process.join(timeout=5)

    print("admin frontend mock smoke test passed")
    return 0


def _find_chrome() -> str | None:
    for name in ("google-chrome", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    return None


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _serve_in_background(server: ThreadingHTTPServer):
    import threading

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def _start_frontend(mock_port: int, frontend_port: int) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["VITE_ADMIN_API_URL"] = f"http://127.0.0.1:{mock_port}"
    return subprocess.Popen(
        [
            "npm",
            "run",
            "dev",
            "--",
            "--host",
            "127.0.0.1",
            "--port",
            str(frontend_port),
            "--strictPort",
        ],
        cwd=ADMIN_FRONTEND_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )


def _wait_for_url(url: str, process: subprocess.Popen[str]) -> None:
    last_error: Exception | None = None
    for _ in range(100):
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"admin frontend dev server exited early:\n{output}")
        try:
            with urlopen(Request(url), timeout=1) as response:
                if response.status < 500:
                    return
        except (OSError, URLError) as exc:
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(f"admin frontend dev server did not become ready: {last_error}")


def _render_dom(chrome: str, url: str) -> str:
    result = subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--virtual-time-budget=5000",
            "--dump-dom",
            url,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return result.stdout


def _assert_rendered(dom: str) -> None:
    expected_fragments = [
        "Crawl Admin",
        "Needs attention",
        "Artifacts",
        ">7<",
        "Raw files",
        ">9<",
        "Pending process",
        ">2<",
        "mock-player",
        "mock fetch failure",
        "completed",
    ]
    missing = [fragment for fragment in expected_fragments if fragment not in dom]
    if missing:
        raise AssertionError(f"rendered admin frontend is missing expected mock data: {missing}")


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
