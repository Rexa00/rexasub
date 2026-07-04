#!/usr/bin/env python3
import base64
import json
import os
import re
import socket
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))
from pathlib import Path
from typing import Callable, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = REPO_ROOT / "subscription.txt"
HISTORY_FILE = REPO_ROOT / "ips.txt"
URL = os.getenv(
    "SUB_URL",
    "https://nova-atlas-gate-0848.rexa-network.workers.dev/sub?token=8da804c17b73eb0f8abb3abf3589d8ec",
)


def decode_payload(payload: str) -> str:
    payload = payload.strip()
    if not payload:
        raise ValueError("Received an empty payload")

    try:
        decoded = base64.b64decode(payload, validate=True).decode("utf-8")
        if decoded:
            return decoded
    except Exception:
        pass

    return payload


def extract_ips_from_text(text: str, resolver: Optional[Callable[[str], List[str]]] = None) -> List[str]:
    hosts = []

    hosts.extend(re.findall(r"(?:(?:vless|trojan|http|https)://[^@\s/]+@([A-Za-z0-9.-]+))", text))
    hosts.extend(re.findall(r"(?:^|[?&])(host|sni|add|server|address)=([A-Za-z0-9.-]+)", text))
    hosts.extend(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text))

    if text.startswith("vmess://"):
        payload = text[len("vmess://") :]
        try:
            decoded = base64.b64decode(payload).decode("utf-8")
            obj = json.loads(decoded)
            add = obj.get("add")
            if isinstance(add, str) and add:
                hosts.append(add)
        except Exception:
            pass

    unique_ips: List[str] = []
    seen = set()
    for host in hosts:
        if isinstance(host, tuple):
            host = host[1]
        host = str(host).strip()
        if not host:
            continue
        if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", host):
            candidate = host
        elif host.lower() == "localhost":
            candidate = "127.0.0.1"
        else:
            if resolver is None:
                try:
                    resolved = [item[4][0] for item in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)]
                except OSError:
                    continue
            else:
                try:
                    resolved = resolver(host)
                except Exception:
                    continue
            for ip in resolved:
                if ip not in seen:
                    seen.add(ip)
                    unique_ips.append(ip)
            continue

        if candidate not in seen:
            seen.add(candidate)
            unique_ips.append(candidate)

    return unique_ips


def fetch_payload(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def write_subscription_output(lines: List[str], output_file: Path, history_file: Path) -> None:
    now_utc = datetime.now(timezone.utc)
    now_tehran = now_utc.astimezone(TEHRAN_TZ)
    timestamp = now_tehran.strftime("%Y-%m-%dT%H:%M:%SZ")
    full_timestamp = now_tehran.strftime("%Y-%m-%d %H:%M:%S")

    with history_file.open("a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{timestamp}\t{line}\n")

    content = "# خروجی آماده‌ی کپی و استفاده\n"
    content += f"# تولید شده در: {full_timestamp}\n"
    content += "# سازگار با Hiddify, V2Ray, Clash, Sing-Box و سایر اپ‌ها\n"
    content += "\n".join([f"{timestamp} {line}" for line in lines]) + "\n"
    output_file.write_text(content, encoding="utf-8")


def main() -> int:
    try:
        payload = fetch_payload(URL)
        decoded = decode_payload(payload)
        ips = extract_ips_from_text(decoded)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to fetch or decode payload: {exc}", file=sys.stderr)
        return 1

    if not ips:
        print("No IPs found")
        return 0

    lines = [f"vless://{ip}:443" for ip in ips]
    write_subscription_output(lines, OUTPUT_FILE, HISTORY_FILE)
    print("لینک‌های آماده‌ی استفاده ذخیره شدند:", ", ".join(lines))
    return 0


if __name__ == "__main__":
    main()
