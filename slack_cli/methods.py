"""Method catalog system for slack-cli.

The "library card" that gives AI agents dynamic capability to call ANY
Slack API method. Ships a bundled catalog of ~250 methods with param
info, scopes, rate tiers, and token types. The catalog is copied to
~/.slack-cli/methods/catalog.json on first use and can be updated
independently of the CLI version.

Modeled after n8n-cli's node catalog (n8n_cli/nodes.py).
"""

import json
import re
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Optional

# Where we store the user-local catalog cache
CATALOG_DIR = Path.home() / ".slack-cli" / "methods"
CATALOG_FILE = CATALOG_DIR / "catalog.json"
META_FILE = CATALOG_DIR / "meta.json"

# Bundled catalog shipped with the package
BUNDLED_CATALOG = Path(__file__).parent / "catalog_data" / "methods.json"

# Catalog staleness threshold (30 days)
CATALOG_TTL_DAYS = 30
CATALOG_TTL_SECONDS = CATALOG_TTL_DAYS * 86400

# Slack docs URL for live-updating
SLACK_DOCS_METHODS_URL = "https://docs.slack.dev/reference/methods"


def _write_meta(method_count: int) -> None:
    """Write metadata about the catalog."""
    meta = {
        "method_count": method_count,
        "updated_at": time.time(),
        "updated_at_human": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }
    with open(META_FILE, "w") as f:
        json.dump(meta, f, indent=2)


def _read_meta() -> dict:
    """Read catalog metadata."""
    if not META_FILE.exists():
        return {}
    try:
        with open(META_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _check_staleness() -> None:
    """Warn if the catalog is older than 30 days."""
    meta = _read_meta()
    updated_at = meta.get("updated_at", 0)
    if not updated_at:
        return
    age_days = (time.time() - updated_at) / 86400
    if age_days > CATALOG_TTL_DAYS:
        age_int = int(age_days)
        print(
            f"Slack API catalog is {age_int} days old. "
            "Run 'slack-cli methods update' to refresh.",
            file=sys.stderr,
        )


def ensure_catalog(force: bool = False) -> None:
    """Ensure catalog exists. Copy bundled catalog if no local cache.

    Args:
        force: If True, overwrite local cache with bundled data.
    """
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)

    if CATALOG_FILE.exists() and not force:
        _check_staleness()
        return

    if not BUNDLED_CATALOG.exists():
        print(
            "Error: Bundled method catalog not found at "
            f"{BUNDLED_CATALOG}",
            file=sys.stderr,
        )
        print(
            "This is a packaging error. Reinstall slack-cli.",
            file=sys.stderr,
        )
        sys.exit(1)

    shutil.copy2(BUNDLED_CATALOG, CATALOG_FILE)
    # Write meta on first copy
    with open(BUNDLED_CATALOG) as f:
        catalog = json.load(f)
    _write_meta(len(catalog))


def load_catalog() -> list:
    """Load the method catalog. Returns list of method dicts."""
    ensure_catalog()
    with open(CATALOG_FILE) as f:
        return json.load(f)


def search_methods(query: str, limit: int = 20) -> list:
    """Search methods by name, namespace, or description.

    Returns a list of method dicts, ordered by relevance score.
    """
    catalog = load_catalog()
    results = []
    for method in catalog:
        score = _score_match(method, query)
        if score > 0:
            results.append((score, method))
    results.sort(key=lambda x: (-x[0], x[1]["name"]))
    return [m for _, m in results[:limit]]


def _score_match(method: dict, query: str) -> int:
    """Score a method against a search query.

    Scoring:
        100 - Exact name match
         50 - Name contains query
         40 - Namespace exact match
         20 - Description contains query
         10 - Param name contains query
    """
    query_lower = query.lower()
    score = 0

    # Exact name match
    if method["name"].lower() == query_lower:
        score += 100
    # Name contains query
    elif query_lower in method["name"].lower():
        score += 50

    # Namespace match
    if method["namespace"].lower() == query_lower:
        score += 40

    # Description contains query
    if query_lower in method.get("description", "").lower():
        score += 20

    # Param name match
    all_params = method.get("required_params", []) + method.get(
        "optional_params", []
    )
    for p in all_params:
        if query_lower in p.lower():
            score += 10
            break

    return score


def get_method(name: str) -> Optional[dict]:
    """Get a single method by exact name. Returns dict or None."""
    catalog = load_catalog()
    for method in catalog:
        if method["name"] == name:
            return method
    # Case-insensitive fallback
    name_lower = name.lower()
    for method in catalog:
        if method["name"].lower() == name_lower:
            return method
    return None


def list_methods(namespace: Optional[str] = None) -> list:
    """List all methods, optionally filtered by namespace."""
    catalog = load_catalog()
    if namespace:
        ns_lower = namespace.lower()
        return [m for m in catalog if m["namespace"].lower() == ns_lower]
    return catalog


def list_namespaces() -> list:
    """List all unique namespaces with method counts."""
    catalog = load_catalog()
    counts = {}
    for m in catalog:
        ns = m["namespace"]
        counts[ns] = counts.get(ns, 0) + 1
    return sorted(counts.items(), key=lambda x: x[0])


# ---------------------------------------------------------------------------
# Human-readable output helpers
# ---------------------------------------------------------------------------


def format_method_summary(method: dict) -> str:
    """One-line summary: name | description | tier | token_types."""
    name = method.get("name", "")
    desc = method.get("description", "")[:50]
    tier = method.get("rate_tier", "")
    tokens = ",".join(method.get("token_types", []))
    return f"{name:<42} {desc:<52} {tier:<8} {tokens}"


def format_method_detail(method: dict) -> str:
    """Full detail view with params, scopes, rate info."""
    lines = []
    lines.append(f"Method:       {method.get('name', '')}")
    lines.append(f"Description:  {method.get('description', '')}")
    lines.append(f"Namespace:    {method.get('namespace', '')}")
    lines.append(f"Token Types:  {', '.join(method.get('token_types', []))}")
    lines.append(f"Rate Tier:    {method.get('rate_tier', '')}")

    rate_note = method.get("rate_note", "")
    if rate_note:
        lines.append(f"Rate Note:    {rate_note}")

    deprecated = method.get("deprecated", False)
    if deprecated:
        lines.append(f"DEPRECATED:   Yes")

    paginated = method.get("paginated", False)
    if paginated:
        lines.append(f"Paginated:    Yes (cursor key: {method.get('response_key', 'N/A')})")

    doc_url = method.get("doc_url", "")
    if doc_url:
        lines.append(f"Docs:         {doc_url}")

    # Scopes
    scopes = method.get("required_scopes", {})
    if scopes:
        lines.append("")
        lines.append("Scopes:")
        for token_type, scope_list in scopes.items():
            lines.append(f"  {token_type}: {', '.join(scope_list)}")

    # Required params
    required = method.get("required_params", [])
    if required:
        lines.append("")
        lines.append("Required Params:")
        descs = method.get("param_descriptions", {})
        for p in required:
            desc = descs.get(p, "")
            if desc:
                lines.append(f"  {p:<24} {desc}")
            else:
                lines.append(f"  {p}")

    # Optional params
    optional = method.get("optional_params", [])
    if optional:
        lines.append("")
        lines.append("Optional Params:")
        descs = method.get("param_descriptions", {})
        for p in optional:
            desc = descs.get(p, "")
            if desc:
                lines.append(f"  {p:<24} {desc}")
            else:
                lines.append(f"  {p}")

    return "\n".join(lines)


def format_search_results(methods: list, limit: int = 20) -> str:
    """Format search results as a table."""
    methods = methods[:limit]
    if not methods:
        return "No methods found."

    lines = []
    lines.append(f"{'Method':<42} {'Description':<52} {'Tier':<8} {'Tokens'}")
    lines.append("-" * 115)
    for m in methods:
        lines.append(format_method_summary(m))
    lines.append(f"\n{len(methods)} result(s)")
    return "\n".join(lines)


def format_namespaces(namespaces: list) -> str:
    """Format namespace list with counts."""
    if not namespaces:
        return "No namespaces found."

    lines = []
    lines.append(f"{'Namespace':<30} {'Methods'}")
    lines.append("-" * 40)
    total = 0
    for ns, count in namespaces:
        lines.append(f"{ns:<30} {count}")
        total += count
    lines.append(f"\n{len(namespaces)} namespace(s), {total} method(s) total")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI-facing commands (called from cli.py)
# ---------------------------------------------------------------------------


def cmd_search(query: str, limit: int = 20, as_json: bool = False) -> None:
    """Search the method catalog by keyword."""
    results = search_methods(query, limit=limit)
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        print(format_search_results(results, limit=limit))


def cmd_get(name: str, as_json: bool = False) -> None:
    """Get details for a specific method."""
    method = get_method(name)
    if not method:
        print(
            f"Method '{name}' not found. Try: slack-cli methods search {name}",
            file=sys.stderr,
        )
        sys.exit(1)
    if as_json:
        print(json.dumps(method, indent=2))
    else:
        print(format_method_detail(method))


def cmd_list(namespace: Optional[str] = None, as_json: bool = False) -> None:
    """List all methods, optionally filtered by namespace."""
    methods = list_methods(namespace=namespace)
    if as_json:
        print(json.dumps(methods, indent=2))
    else:
        print(format_search_results(methods, limit=len(methods)))


def cmd_namespaces(as_json: bool = False) -> None:
    """List all namespaces."""
    namespaces = list_namespaces()
    if as_json:
        print(json.dumps(dict(namespaces), indent=2))
    else:
        print(format_namespaces(namespaces))


def _fetch_live_methods() -> list:
    """Fetch method names from docs.slack.dev.

    Returns list of method name strings found on the page.
    """
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        SLACK_DOCS_METHODS_URL,
        headers={"User-Agent": "slack-cli/0.2.0 (catalog updater)"},
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"Warning: Could not fetch live methods: {e}", file=sys.stderr)
        return []

    # Extract method names: look for patterns like `method.name` in backtick blocks
    # or in href patterns like /reference/methods/chat.postmessage
    found = set()

    # Pattern 1: href links to method pages
    href_matches = re.findall(
        r'href="[^"]*?/reference/methods/([a-z][a-zA-Z0-9._]+)"',
        html,
    )
    for m in href_matches:
        # Convert URL slug to method name (dots preserved, underscores in camelCase)
        found.add(m)

    # Pattern 2: backtick-wrapped method names in the page
    backtick_matches = re.findall(r"`([a-z][a-zA-Z0-9]+(?:\.[a-zA-Z][a-zA-Z0-9]*)+)`", html)
    for m in backtick_matches:
        found.add(m)

    return sorted(found)


def cmd_update(as_json: bool = False, live: bool = False) -> None:
    """Update the local catalog.

    If --live, attempts to fetch from docs.slack.dev and add new methods.
    Otherwise, resets to the bundled catalog.
    """
    if live:
        # Fetch live method list
        print("Fetching live method list from docs.slack.dev...", file=sys.stderr)
        live_methods = _fetch_live_methods()

        # Load current catalog
        ensure_catalog()
        catalog = load_catalog()
        existing_names = set(m["name"] for m in catalog)

        added = []
        deprecated_count = 0

        if live_methods:
            # Add newly discovered methods
            for name in live_methods:
                if name not in existing_names:
                    # Derive namespace from method name
                    parts = name.split(".")
                    namespace = ".".join(parts[:-1]) if len(parts) > 1 else parts[0]
                    new_entry = {
                        "name": name,
                        "description": f"Slack API method: {name}",
                        "namespace": namespace,
                        "required_scopes": {},
                        "token_types": ["bot"],
                        "rate_tier": "tier2",
                        "rate_note": "",
                        "required_params": [],
                        "optional_params": [],
                        "param_descriptions": {},
                        "response_key": None,
                        "paginated": False,
                        "deprecated": False,
                        "doc_url": f"https://docs.slack.dev/reference/methods/{name}",
                    }
                    catalog.append(new_entry)
                    added.append(name)

            # Mark methods not in live list as potentially deprecated
            live_set = set(live_methods)
            for m in catalog:
                if (
                    m["name"] not in live_set
                    and not m.get("deprecated")
                    and "admin" not in m["name"]  # admin methods often not listed
                ):
                    m["deprecated"] = True
                    deprecated_count += 1

        # Save updated catalog
        catalog.sort(key=lambda x: x["name"])
        with open(CATALOG_FILE, "w") as f:
            json.dump(catalog, f, indent=2)
        _write_meta(len(catalog))

        namespaces = set(m["namespace"] for m in catalog)
        info = {
            "method_count": len(catalog),
            "namespace_count": len(namespaces),
            "added": len(added),
            "deprecated": deprecated_count,
            "new_methods": added,
            "catalog_path": str(CATALOG_FILE),
        }
        if as_json:
            print(json.dumps(info, indent=2))
        else:
            print(f"Method catalog updated from docs.slack.dev.")
            print(f"  Methods: {info['method_count']}")
            print(f"  Namespaces: {info['namespace_count']}")
            print(f"  Added: {info['added']}")
            print(f"  Newly deprecated: {info['deprecated']}")
            print(f"  Path: {info['catalog_path']}")
            if added:
                print(f"\nNew methods:")
                for name in added:
                    print(f"  + {name}")
    else:
        # Reset to bundled catalog
        ensure_catalog(force=True)
        catalog = load_catalog()
        _write_meta(len(catalog))
        namespaces = set(m["namespace"] for m in catalog)
        info = {
            "method_count": len(catalog),
            "namespace_count": len(namespaces),
            "catalog_path": str(CATALOG_FILE),
        }
        if as_json:
            print(json.dumps(info, indent=2))
        else:
            print(f"Method catalog reset to bundled data.")
            print(f"  Methods: {info['method_count']}")
            print(f"  Namespaces: {info['namespace_count']}")
            print(f"  Path: {info['catalog_path']}")


def cmd_info(as_json: bool = False) -> None:
    """Show catalog status."""
    if not CATALOG_FILE.exists():
        print("No catalog cached. Run: slack-cli methods update")
        return

    catalog = load_catalog()
    namespaces = set(m["namespace"] for m in catalog)
    meta = _read_meta()
    updated_at = meta.get("updated_at_human", "unknown")
    updated_ts = meta.get("updated_at", 0)
    age_days = int((time.time() - updated_ts) / 86400) if updated_ts else None

    info = {
        "method_count": len(catalog),
        "namespace_count": len(namespaces),
        "catalog_path": str(CATALOG_FILE),
        "bundled_path": str(BUNDLED_CATALOG),
        "bundled_exists": BUNDLED_CATALOG.exists(),
        "last_updated": updated_at,
        "age_days": age_days,
    }
    if as_json:
        print(json.dumps(info, indent=2))
    else:
        print(f"Method catalog:")
        print(f"  Methods: {info['method_count']}")
        print(f"  Namespaces: {info['namespace_count']}")
        print(f"  Cache: {info['catalog_path']}")
        print(f"  Last updated: {updated_at}")
        if age_days is not None:
            stale = " (STALE -- run 'slack-cli methods update')" if age_days > CATALOG_TTL_DAYS else ""
            print(f"  Age: {age_days} days{stale}")
