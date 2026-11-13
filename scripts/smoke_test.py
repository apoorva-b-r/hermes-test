#!/usr/bin/env python3
"""
smoke_test.py - Smoke test runner for Fernhill Payments demo estate.
Uses Python standard library only.
"""

import argparse
import http.client
import json
import os
import sys
import urllib.parse


TEST_CASES = [
    # (method, host_alias, path, expected_status)
    ("HEAD", "api", "/v2/invoices", 200),
    ("HEAD", "api", "/v2/invoices/4812", 200),
    ("HEAD", "api", "/v2/customers", 200),
    ("HEAD", "api", "/admin/export", 405),
    ("POST", "api", "/admin/export", 202),
    ("HEAD", "api", "/internal/metrics", 401),
    ("HEAD", "api", "/v1/invoices", 200),
    ("HEAD", "api", "/v1/orders", 410),
    ("HEAD", "api", "/legacy/report", 200),
    ("HEAD", "api", "/v2/reports/monthly", 404),
    ("HEAD", "legacy", "/api/v1/accounts", 200),
    ("HEAD", "legacy", "/api/v1/accounts/acc_001", 200),
    ("HEAD", "legacy", "/api/v1/accounts/sync", 405),
    ("HEAD", "legacy", "/api/v1/debug/config", 200),
    ("GET", "legacy", "/openapi.json", 404),
    ("HEAD", "admin", "/admin/users", 401),
    ("HEAD", "admin", "/status", 200),
    ("GET", "www", "/", 200),
    ("GET", "www", "/assets/app.js", 200),
]


def send_request(url, method):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme == "https":
        conn = http.client.HTTPSConnection(parsed.netloc, timeout=10)
    else:
        conn = http.client.HTTPConnection(parsed.netloc, timeout=10)

    path = parsed.path
    if parsed.query:
        path += "?" + parsed.query
    if not path:
        path = "/"

    try:
        conn.request(method, path)
        resp = conn.getresponse()
        status = resp.status
        resp.read()  # Drain response
        conn.close()
        return status
    except Exception as e:
        conn.close()
        return f"ERROR: {e}"


def main():
    parser = argparse.ArgumentParser(description="Run Fernhill smoke tests.")
    parser.add_argument("--local", action="store_true", help="Test against local services on ports 3000-3003")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    platform_dir = os.path.dirname(script_dir)
    config_path = os.path.join(platform_dir, "demo.config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    domain = config["domain"]

    if args.local:
        host_map = {
            "api": "http://localhost:3001",
            "legacy": "http://localhost:3002",
            "admin": "http://localhost:3003",
            "www": "http://localhost:3000",
        }
    else:
        host_map = {
            "api": f"https://api.{domain}",
            "legacy": f"https://legacy.{domain}",
            "admin": f"https://admin.{domain}",
            "www": f"https://www.{domain}",
        }

    failures = 0
    print(f"\nRunning smoke test ({'local mode' if args.local else 'remote mode: ' + domain})...\n")

    for method, alias, path, expected in TEST_CASES:
        base_url = host_map[alias]
        full_url = f"{base_url}{path}"
        actual = send_request(full_url, method)

        if actual == expected:
            result = "PASS"
        else:
            result = "FAIL"
            failures += 1

        print(f"{method:5} {full_url:45} expected: {expected:<4} actual: {str(actual):<4} [{result}]")

    print(f"\nTotal: {len(TEST_CASES)}, Passed: {len(TEST_CASES) - failures}, Failed: {failures}\n")

    if failures > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
