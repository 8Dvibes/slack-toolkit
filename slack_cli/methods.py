"""Method catalog system for slack-cli.

The "library card" that gives AI agents dynamic capability to call ANY
Slack API method. Ships a bundled catalog of ~250 methods with param
info, scopes, rate tiers, and token types. The catalog is copied to
~/.slack-cli/methods/catalog.json on first use and can be updated
independently of the CLI version.

Modeled after n8n-cli's node catalog (n8n_cli/nodes.py).
"""

import json
import shutil
import sys
from pathlib import Path
from typing import List, Optional

# Where we store the user-local catalog cache
CATALOG_DIR = Path.home() / ".slack-cli" / "methods"
CATALOG_FILE = CATALOG_DIR / "catalog.json"

# Bundled catalog shipped with the package
BUNDLED_CATALOG = Path(__file__).parent / "catalog_data" / "methods.json"


def ensure_catalog(force: bool = False) -> None:
    """Ensure catalog exists. Copy bundled catalog if no local cache.

    Args:
        force: If True, overwrite local cache with bundled data.
    """
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)

    if CATALOG_FILE.exists() and not force:
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


def cmd_update(as_json: bool = False) -> None:
    """Force-update the local catalog from bundled data."""
    ensure_catalog(force=True)
    catalog = load_catalog()
    namespaces = set(m["namespace"] for m in catalog)
    info = {
        "method_count": len(catalog),
        "namespace_count": len(namespaces),
        "catalog_path": str(CATALOG_FILE),
    }
    if as_json:
        print(json.dumps(info, indent=2))
    else:
        print(f"Method catalog updated.")
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
    info = {
        "method_count": len(catalog),
        "namespace_count": len(namespaces),
        "catalog_path": str(CATALOG_FILE),
        "bundled_path": str(BUNDLED_CATALOG),
        "bundled_exists": BUNDLED_CATALOG.exists(),
    }
    if as_json:
        print(json.dumps(info, indent=2))
    else:
        print(f"Method catalog:")
        print(f"  Methods: {info['method_count']}")
        print(f"  Namespaces: {info['namespace_count']}")
        print(f"  Cache: {info['catalog_path']}")
