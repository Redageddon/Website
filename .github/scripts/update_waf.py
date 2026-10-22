#!/usr/bin/env python3
"""Rebuild the Cloudflare WAF allowlist rule for the root site from this repo.

Allowed paths = every file Cloudflare Pages will serve + every _redirects source.
The rule is found by its name (RULE_NAME) and only its expression is replaced.

Run with --dry-run (or without CF_API_TOKEN) to just print the expression.
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

HOST = os.environ.get("SITE_HOST", "redageddon.com")
RULE_NAME = os.environ.get("RULE_NAME", "Root site allowlist")
API = "https://api.cloudflare.com/client/v4"
MAX_EXPR = 4096  # Cloudflare's expression length limit


def encode(path):
    # Match what browsers send: percent-encode anything outside RFC 3986 path chars.
    return urllib.parse.quote(path, safe="/!$&'()*+,;=:@-._~")


def add_with_slash(paths, path):
    path = path.rstrip("/") or "/"
    paths.add(path)
    if path != "/":
        paths.add(path + "/")


def site_paths():
    files = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True
    ).stdout.splitlines()

    paths = {"/"}
    for f in files:
        # Pages doesn't serve dotfiles or its own config files (_redirects, _headers).
        if any(part.startswith((".", "_")) for part in f.split("/")):
            continue
        p = "/" + f
        paths.add(p)
        if p.endswith("/index.html"):
            add_with_slash(paths, p[: -len("index.html")])
        elif p.endswith(".html"):
            add_with_slash(paths, p[: -len(".html")])  # Pages pretty URLs

    if os.path.exists("_redirects"):
        with open("_redirects") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                src = line.split()[0]
                if src.startswith(("http://", "https://")):
                    continue
                if "*" in src or ":" in src:
                    sys.exit(
                        f"Redirect '{src}' uses a wildcard or placeholder, which an exact-match "
                        "allowlist can't cover. Remove it or handle it in the rule by hand."
                    )
                add_with_slash(paths, src)

    return sorted(encode(p) for p in paths)


def build_expression(paths):
    items = " ".join(json.dumps(p) for p in paths)
    expr = f"(http.host eq {json.dumps(HOST)} and not http.request.uri.path in {{{items}}})"
    if len(expr) > MAX_EXPR:
        sys.exit(f"Expression is {len(expr)} chars, over Cloudflare's {MAX_EXPR} limit.")
    return expr


def cf(method, path, body=None):
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {os.environ['CF_API_TOKEN']}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)["result"]
    except urllib.error.HTTPError as err:
        sys.exit(f"Cloudflare API {method} {path} failed ({err.code}): {err.read().decode()}")


def main():
    expr = build_expression(site_paths())

    if "--dry-run" in sys.argv or not os.environ.get("CF_API_TOKEN"):
        print(expr)
        return

    zone = os.environ["CF_ZONE_ID"]
    ruleset = cf("GET", f"/zones/{zone}/rulesets/phases/http_request_firewall_custom/entrypoint")
    rule = next(
        (r for r in ruleset.get("rules", []) if r.get("description") == RULE_NAME), None
    )
    if rule is None:
        sys.exit(f"No custom rule named '{RULE_NAME}' found. Create it in the dashboard first.")

    if rule["expression"] == expr:
        print("Rule already matches the repo. Nothing to do.")
        return

    cf(
        "PATCH",
        f"/zones/{zone}/rulesets/{ruleset['id']}/rules/{rule['id']}",
        {
            "action": rule["action"],
            "expression": expr,
            "description": RULE_NAME,
            "enabled": rule.get("enabled", True),
        },
    )
    print(f"Updated '{RULE_NAME}':\n{expr}")


if __name__ == "__main__":
    main()
