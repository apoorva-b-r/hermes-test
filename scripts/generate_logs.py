#!/usr/bin/env python3
"""
generate_logs.py - Synthetic log generator for Fernhill Payments demo estate.
Uses Python standard library only.
"""

import datetime
import json
import os
import random
import sys
from collections import Counter


def main():
    random.seed(7)

    # Resolve paths relative to repository root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    platform_dir = os.path.dirname(script_dir)
    config_path = os.path.join(platform_dir, "demo.config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    domain = config["domain"]
    output_dir = os.path.abspath(os.path.join(platform_dir, "..", "fernhill-uploads", "logs"))
    os.makedirs(output_dir, exist_ok=True)

    # 120-day window ending now (UTC)
    now = datetime.datetime.now(datetime.timezone.utc)
    window_start = now - datetime.timedelta(days=120)
    first_hour_end = window_start + datetime.timedelta(hours=1)
    last_hour_start = now - datetime.timedelta(hours=1)

    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
        "curl/8.4.0"
    ]

    def random_client_ip():
        if random.random() < 0.5:
            return f"203.0.113.{random.randint(1, 254)}"
        else:
            return f"198.51.100.{random.randint(1, 254)}"

    # -------------------------------------------------------------
    # 1. api-access.log (nginx combined format, 20,000 lines)
    # -------------------------------------------------------------
    api_log_count = 20000
    api_log_path = os.path.join(output_dir, "api-access.log")

    # Generate sorted timestamps
    t_start = random.uniform(window_start.timestamp(), first_hour_end.timestamp())
    t_end = random.uniform(last_hour_start.timestamp(), now.timestamp())
    middle_timestamps = [random.uniform(t_start, t_end) for _ in range(api_log_count - 2)]
    api_timestamps = sorted([t_start] + middle_timestamps + [t_end])

    # Weights: invoices 40%, invoice_id 25%, customers 20%, metrics 5%, health 5%, favicon 4%, scanner 1%
    categories = ["invoices", "invoice_id", "customers", "metrics", "health", "favicon", "scanner"]
    weights = [40, 25, 20, 5, 5, 4, 1]

    api_lines = []
    never_api_routes = [
        "/v1/invoices",
        "/v1/orders",
        "/legacy/report",
        "/admin/export",
        "/v2/reports/monthly"
    ]

    for ts in api_timestamps:
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        cat = random.choices(categories, weights=weights, k=1)[0]
        method = "GET"

        if cat == "invoices":
            path = "/v2/invoices"
            status = 200
            bytes_sent = 60
        elif cat == "invoice_id":
            inv_id = random.randint(1000, 9999)
            path = f"/v2/invoices/{inv_id}"
            status = 200
            bytes_sent = 58
        elif cat == "customers":
            path = "/v2/customers"
            status = 200
            bytes_sent = 36
        elif cat == "metrics":
            path = "/internal/metrics"
            status = 200 if random.random() < 0.20 else 401
            bytes_sent = 17 if status == 200 else 24
        elif cat == "health":
            path = "/health"
            status = 200
            bytes_sent = 11
        elif cat == "favicon":
            path = "/favicon.ico"
            status = 404
            bytes_sent = 21
        elif cat == "scanner":
            path = random.choice(["/wp-admin", "/.env", "/phpmyadmin"])
            status = 404
            bytes_sent = 21
        else:
            raise ValueError(f"Unknown category: {cat}")

        # Check NEVER routes
        for never_r in never_api_routes:
            if never_r in path:
                raise RuntimeError(f"FATAL: NEVER route '{never_r}' generated in api-access.log!")

        ip = random_client_ip()
        ua = random.choice(user_agents)
        referer = f"https://www.{domain}/" if ("invoices" in path or "customers" in path) and random.random() < 0.7 else "-"
        time_local = dt.strftime("%d/%b/%Y:%H:%M:%S +0000")

        line = f'{ip} - - [{time_local}] "{method} {path} HTTP/1.1" {status} {bytes_sent} "{referer}" "{ua}"'
        api_lines.append(line)

    with open(api_log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(api_lines) + "\n")

    # -------------------------------------------------------------
    # 2. legacy-access.jsonl (3,000 lines)
    # -------------------------------------------------------------
    legacy_log_count = 3000
    legacy_log_path = os.path.join(output_dir, "legacy-access.jsonl")

    t_start_leg = random.uniform(window_start.timestamp(), first_hour_end.timestamp())
    t_end_leg = random.uniform(last_hour_start.timestamp(), now.timestamp())
    middle_leg = [random.uniform(t_start_leg, t_end_leg) for _ in range(legacy_log_count - 2)]
    legacy_timestamps = sorted([t_start_leg] + middle_leg + [t_end_leg])

    never_legacy_routes = ["/api/v1/debug/config"]
    legacy_lines = []

    for ts in legacy_timestamps:
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        iso_ts = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        r = random.random()
        if r < 0.50:
            method = "GET"
            path = "/api/v1/accounts"
            status = 200
        elif r < 0.85:
            method = "GET"
            acc_num = random.randint(1, 999)
            path = f"/api/v1/accounts/acc_{acc_num:03d}"
            status = 200
        else:
            method = "POST"
            path = "/api/v1/accounts/sync"
            status = 202

        for never_r in never_legacy_routes:
            if never_r in path:
                raise RuntimeError(f"FATAL: NEVER route '{never_r}' generated in legacy-access.jsonl!")

        record = {
            "timestamp": iso_ts,
            "method": method,
            "path": path,
            "status": status,
            "host": f"legacy.{domain}",
            "duration_ms": round(random.uniform(5.0, 45.0), 2)
        }
        legacy_lines.append(json.dumps(record))

    with open(legacy_log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(legacy_lines) + "\n")

    # -------------------------------------------------------------
    # 3. web-session.har (browser session loading www.<domain> today)
    # -------------------------------------------------------------
    har_log_path = os.path.join(output_dir, "web-session.har")

    # Read web content if available
    web_dir = os.path.join(platform_dir, "apps", "web")
    index_file = os.path.join(web_dir, "index.html")
    app_js_file = os.path.join(web_dir, "assets", "app.js")

    html_content = "<!DOCTYPE html>\n<html><head><title>Fernhill Payments</title></head><body><h1>Fernhill Payments</h1><ul id=\"invoices\"></ul><script src=\"/assets/app.js\"></script></body></html>"
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            html_content = f.read()

    js_content = "console.log('Fernhill Payments');"
    if os.path.exists(app_js_file):
        with open(app_js_file, "r", encoding="utf-8") as f:
            js_content = f.read()

    invoices_json = json.dumps([{"id": 4812, "customerId": 17, "total": 129.5, "currency": "GBP"}])
    customers_json = json.dumps([{"id": 17, "name": "Placeholder Ltd"}])

    # Today UTC around 10:00:00
    session_start = now.replace(hour=10, minute=0, second=0, microsecond=0)
    if session_start > now:
        session_start = now - datetime.timedelta(hours=2)

    def make_har_entry(started_dt, method, url, status, content_type, body_text):
        content_bytes = len(body_text.encode("utf-8"))
        wait_time = round(random.uniform(15.0, 35.0), 2)
        receive_time = round(random.uniform(2.0, 8.0), 2)
        total_time = round(wait_time + receive_time + 5.0, 2)

        return {
            "pageref": "page_1",
            "startedDateTime": started_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "time": total_time,
            "request": {
                "method": method,
                "url": url,
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": [
                    {"name": "Host", "value": url.split("//")[1].split("/")[0]},
                    {"name": "User-Agent", "value": user_agents[0]},
                    {"name": "Accept", "value": "*/*"}
                ],
                "queryString": [],
                "headersSize": -1,
                "bodySize": 0
            },
            "response": {
                "status": status,
                "statusText": "OK",
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": [
                    {"name": "Content-Type", "value": content_type},
                    {"name": "Content-Length", "value": str(content_bytes)}
                ],
                "content": {
                    "size": content_bytes,
                    "mimeType": content_type,
                    "text": body_text
                },
                "redirectURL": "",
                "headersSize": -1,
                "bodySize": content_bytes
            },
            "cache": {},
            "timings": {
                "blocked": 0.5,
                "dns": 1.2,
                "connect": 3.3,
                "send": 0.2,
                "wait": wait_time,
                "receive": receive_time,
                "ssl": -1
            }
        }

    t1 = session_start
    t2 = t1 + datetime.timedelta(milliseconds=120)
    t3 = t2 + datetime.timedelta(milliseconds=180)
    t4 = t3 + datetime.timedelta(milliseconds=90)

    har_entries = [
        make_har_entry(t1, "GET", f"https://www.{domain}/", 200, "text/html; charset=utf-8", html_content),
        make_har_entry(t2, "GET", f"https://www.{domain}/assets/app.js", 200, "application/javascript; charset=utf-8", js_content),
        make_har_entry(t3, "GET", f"https://api.{domain}/v2/invoices", 200, "application/json; charset=utf-8", invoices_json),
        make_har_entry(t4, "GET", f"https://api.{domain}/v2/customers", 200, "application/json; charset=utf-8", customers_json),
    ]

    har_data = {
        "log": {
            "version": "1.2",
            "creator": {
                "name": "Fernhill Generator",
                "version": "1.0"
            },
            "pages": [
                {
                    "startedDateTime": t1.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                    "id": "page_1",
                    "title": "Fernhill Payments",
                    "pageTimings": {
                        "onContentLoad": 150.0,
                        "onLoad": 420.0
                    }
                }
            ],
            "entries": har_entries
        }
    }

    with open(har_log_path, "w", encoding="utf-8") as f:
        json.dump(har_data, f, indent=2)

    # -------------------------------------------------------------
    # Verification & Summary Reporting
    # -------------------------------------------------------------
    print("\n=======================================================")
    print("LOG GENERATION REPORT & ROUTE VERIFICATION")
    print("=======================================================")

    # 1. Verify api-access.log
    with open(api_log_path, "r", encoding="utf-8") as f:
        read_api_lines = [l.strip() for l in f if l.strip()]

    print(f"\n1. {os.path.basename(api_log_path)}:")
    print(f"   Line count: {len(read_api_lines)}")

    # Extract first and last timestamp
    first_time_str = read_api_lines[0].split("[")[1].split("]")[0]
    last_time_str = read_api_lines[-1].split("[")[1].split("]")[0]
    print(f"   First timestamp: {first_time_str}")
    print(f"   Last timestamp:  {last_time_str}")

    api_route_counts = Counter()
    for l in read_api_lines:
        for never_r in never_api_routes:
            if never_r in l:
                print(f"CRITICAL ERROR: Found forbidden route '{never_r}' in line: {l}", file=sys.stderr)
                sys.exit(1)
        # Parse route pattern
        req_part = l.split('"')[1]
        method, path, _ = req_part.split()
        if path.startswith("/v2/invoices/"):
            route_key = f"{method} /v2/invoices/<id>"
        else:
            route_key = f"{method} {path}"
        api_route_counts[route_key] += 1

    print("   Route counts:")
    for r, c in api_route_counts.most_common():
        pct = (c / len(read_api_lines)) * 100
        print(f"     {r:30} : {c:6d} ({pct:5.2f}%)")

    # 2. Verify legacy-access.jsonl
    with open(legacy_log_path, "r", encoding="utf-8") as f:
        read_legacy_records = [json.loads(l) for l in f if l.strip()]

    print(f"\n2. {os.path.basename(legacy_log_path)}:")
    print(f"   Line count: {len(read_legacy_records)}")
    print(f"   First timestamp: {read_legacy_records[0]['timestamp']}")
    print(f"   Last timestamp:  {read_legacy_records[-1]['timestamp']}")

    legacy_route_counts = Counter()
    for rec in read_legacy_records:
        for never_r in never_legacy_routes:
            if never_r in rec["path"]:
                print(f"CRITICAL ERROR: Found forbidden route '{never_r}' in record: {rec}", file=sys.stderr)
                sys.exit(1)
        if rec["path"].startswith("/api/v1/accounts/acc_"):
            route_key = f"{rec['method']} /api/v1/accounts/acc_<id>"
        else:
            route_key = f"{rec['method']} {rec['path']}"
        legacy_route_counts[route_key] += 1

    print("   Route counts:")
    for r, c in legacy_route_counts.most_common():
        pct = (c / len(read_legacy_records)) * 100
        print(f"     {r:30} : {c:6d} ({pct:5.2f}%)")

    # 3. Verify web-session.har
    with open(har_log_path, "r", encoding="utf-8") as f:
        read_har = json.load(f)

    entries = read_har["log"]["entries"]
    print(f"\n3. {os.path.basename(har_log_path)}:")
    print(f"   Entry count: {len(entries)}")
    print(f"   First timestamp: {entries[0]['startedDateTime']}")
    print(f"   Last timestamp:  {entries[-1]['startedDateTime']}")
    print("   Documented requests:")
    for ent in entries:
        req = ent["request"]
        res = ent["response"]
        print(f"     {req['method']:6} {req['url']:45} -> {res['status']} ({res['content']['mimeType']})")

    print("\nAll NEVER routes verified absent. Log generation complete.\n")


if __name__ == "__main__":
    main()
