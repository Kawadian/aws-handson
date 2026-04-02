#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import socket
import threading
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import count
from typing import Any

BOOT_TIME = time.time()
REQUEST_COUNTER = 0
MEMOS: list[dict[str, Any]] = []
MEMO_IDS = count(1)
STATE_LOCK = threading.Lock()
MAX_BODY_SIZE = 8 * 1024
MAX_MEMO_LENGTH = 120
MAX_NUMBERS = 20


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "CloudFrontEc2Demo/1.0"

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_common_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        self._record_request()

        if self.path == "/health":
            self._write_json(HTTPStatus.OK, {"status": "ok", "time": utc_now()})
            return

        if self.path == "/api/state":
            self._write_json(HTTPStatus.OK, self._build_state())
            return

        self._write_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def do_POST(self) -> None:  # noqa: N802
        self._record_request()

        if self.path == "/api/memos":
            payload = self._read_json_body()
            if payload is None:
                return
            self._handle_create_memo(payload)
            return

        if self.path == "/api/calculate":
            payload = self._read_json_body()
            if payload is None:
                return
            self._handle_calculate(payload)
            return

        self._write_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")

    def _set_common_headers(self) -> None:
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")

    def _write_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._set_common_headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any] | None:
        length_header = self.headers.get("Content-Length")
        try:
            content_length = int(length_header or "0")
        except ValueError:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid Content-Length"})
            return None

        if content_length <= 0:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "Request body is required"})
            return None

        if content_length > MAX_BODY_SIZE:
            self._write_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Request body is too large"})
            return None

        raw_body = self.rfile.read(content_length)
        try:
            data = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "Body must be valid JSON"})
            return None

        if not isinstance(data, dict):
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "JSON body must be an object"})
            return None

        return data

    def _record_request(self) -> None:
        global REQUEST_COUNTER
        with STATE_LOCK:
            REQUEST_COUNTER += 1

    def _build_state(self) -> dict[str, Any]:
        with STATE_LOCK:
            return {
                "hostname": socket.gethostname(),
                "pid": os.getpid(),
                "bootTime": datetime.fromtimestamp(BOOT_TIME, tz=timezone.utc).isoformat(),
                "serverTime": utc_now(),
                "uptimeSeconds": round(time.time() - BOOT_TIME, 2),
                "requestCount": REQUEST_COUNTER,
                "memoCount": len(MEMOS),
                "memos": list(MEMOS),
            }

    def _handle_create_memo(self, payload: dict[str, Any]) -> None:
        text = str(payload.get("text", "")).strip()
        if not text:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "text is required"})
            return

        if len(text) > MAX_MEMO_LENGTH:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {"error": f"text must be {MAX_MEMO_LENGTH} characters or fewer"},
            )
            return

        memo = {
            "id": next(MEMO_IDS),
            "text": text,
            "savedAt": utc_now(),
        }
        with STATE_LOCK:
            MEMOS.append(memo)

        self._write_json(
            HTTPStatus.CREATED,
            {
                "message": "memo saved",
                "saved": memo,
                "memoCount": len(MEMOS),
            },
        )

    def _handle_calculate(self, payload: dict[str, Any]) -> None:
        raw_numbers = payload.get("numbers")
        if not isinstance(raw_numbers, list) or not raw_numbers:
            self._write_json(HTTPStatus.BAD_REQUEST, {"error": "numbers must be a non-empty array"})
            return

        if len(raw_numbers) > MAX_NUMBERS:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {"error": f"numbers can contain up to {MAX_NUMBERS} items"},
            )
            return

        numbers: list[float] = []
        for value in raw_numbers:
            if isinstance(value, bool):
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "numbers must contain numeric values only"})
                return
            try:
                number = float(value)
            except (TypeError, ValueError):
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "numbers must contain numeric values only"})
                return
            if not math.isfinite(number):
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "numbers must be finite"})
                return
            numbers.append(number)

        total = round(sum(numbers), 4)
        average = round(total / len(numbers), 4)
        self._write_json(
            HTTPStatus.OK,
            {
                "input": numbers,
                "count": len(numbers),
                "sum": total,
                "average": average,
                "processedAt": utc_now(),
            },
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CloudFront + EC2 handson demo server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DemoHandler)
    print(f"Server started on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
