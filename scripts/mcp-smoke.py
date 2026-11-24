#!/usr/bin/env python3
"""Read-only SafeSell AI MCP connection check using Python 3's standard library."""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ENDPOINT = "https://safesellai.com/mcp"
TOKEN_VAR = "SAFESELLAI_API_KEY"


def request(verb, headers, message=None):
    body = json.dumps(message).encode("utf-8") if message is not None else None
    req = Request(ENDPOINT, data=body, headers=headers, method=verb)
    with urlopen(req, timeout=20) as response:
        response_headers = response.headers
        payload = response.read().decode("utf-8")
    if not payload.strip():
        return response_headers, None
    if response_headers.get_content_type() != "text/event-stream":
        return response_headers, json.loads(payload)
    for event in payload.replace("\r\n", "\n").split("\n\n"):
        data = "\n".join(
            line[5:].lstrip(" ")
            for line in event.split("\n")
            if line.startswith("data:")
        )
        if data:
            reply = json.loads(data)
            if reply.get("id") == (message or {}).get("id"):
                return response_headers, reply
    raise RuntimeError("MCP response contained no matching event")


def result(reply):
    if not reply or "result" not in reply:
        code = (reply or {}).get("error", {}).get("code", "unknown")
        raise RuntimeError(f"MCP request did not return a result (code {code})")
    return reply["result"]


def call(headers, rpc_id, name, arguments):
    _, reply = request(
        "POST",
        headers,
        {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        },
    )
    value = result(reply)
    if value.get("isError"):
        raise RuntimeError(f"{name} returned a tool error")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account", action="store_true", help=f"use {TOKEN_VAR}")
    parser.add_argument("--feature", help="list matching website operations (requires --account)")
    args = parser.parse_args()
    if args.feature and not args.account:
        parser.error("--feature requires --account")
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if args.account:
        token = os.environ.get(TOKEN_VAR, "").strip()
        if not token:
            parser.error(f"set {TOKEN_VAR} in the process environment")
        headers["Authorization"] = f"Bearer {token}"

    res_headers, init = request(
        "POST",
        headers,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "safesellai-skill-smoke", "version": "1.0.0"},
            },
        },
    )
    negotiated = result(init)
    session = res_headers.get("Mcp-Session-Id")
    headers["MCP-Protocol-Version"] = negotiated["protocolVersion"]
    if session:
        headers["Mcp-Session-Id"] = session
    try:
        request("POST", headers, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        names = set()
        params = {}
        while True:
            _, reply = request(
                "POST",
                headers,
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": params},
            )
            page = result(reply)
            names.update(tool["name"] for tool in page["tools"])
            cursor = page.get("nextCursor")
            if not cursor:
                break
            params = {"cursor": cursor}
        print(f"Protocol {negotiated['protocolVersion']}")
        print("Tools:", ", ".join(sorted(names)))
        name = "get_balance" if args.account else "guest_info"
        if name not in names:
            raise RuntimeError(f"{name} is not advertised for this connection")
        call(headers, 3, name, {})
        print(f"{name}: OK")
        if args.feature:
            if "website_tools" not in names:
                raise RuntimeError("website_tools is not advertised for this connection")
            catalogue = call(headers, 4, "website_tools", {"feature": args.feature})
            for item in catalogue.get("content", []):
                if item.get("type") == "text":
                    print(item["text"])
    finally:
        if session:
            try:
                request("DELETE", headers)
            except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError):
                pass


if __name__ == "__main__":
    try:
        main()
    except HTTPError as exc:
        print(f"HTTP {exc.code} from SafeSell AI MCP", file=sys.stderr)
        sys.exit(1)
    except (URLError, TimeoutError, RuntimeError, ValueError) as exc:
        print(f"MCP check failed: {exc}", file=sys.stderr)
        sys.exit(1)
