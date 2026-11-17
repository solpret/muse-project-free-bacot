#!/usr/bin/env python3
"""Merge run-68 inbound part b from its segments (read-only bookkeeping).
Segments:
 - b-part1: contracts 400-849 of the sorted set (first 450 of part b), run by the
   04:05 worker; killed at [450/571] before saving JSON. Only aggregates survive
   in run68-inbound-b.log: logs=2774, hits=0, failed=5 (0xd1d3../0xd1dc../0xd1e6../
   0xd1e7../0xd200..), truncated=0. The 5 failed were retried as
   run68-inbound-b-retry.json (5 contracts, 2 logs, 0 hits, 0 failed).
 - b2: contracts 850-970 (last 121 of part b), run68-inbound-b2.json.
 - b2retry: retry of b2's failed contracts, run68-inbound-b2-retry.json (if any).
Output: run68-inbound-b.json (full part b, 571 contracts) for run68-state-update.py.
No preview/mint/sign/login."""
import json
from pathlib import Path
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
b2 = json.load(open(D / "run68-inbound-b2.json"))
bretry = json.load(open(D / "run68-inbound-b-retry.json"))
b2retry = {}
p = D / "run68-inbound-b2-retry.json"
if p.exists():
    b2retry = json.load(open(p))
part1 = {"contracts_checked": 450, "total_logs": 2774, "hits": [], "failed": [
    {"contract": "0xd1d3b730b154838b7b5f0c072de7ba66ffbbe72b", "error": "Remote end closed connection without response (retried, see b-retry)"},
    {"contract": "0xd1dc944f2ad3720c38636b40fc93a1119003cba4", "error": "Remote end closed connection without response (retried, see b-retry)"},
    {"contract": "0xd1e6b1e4cae2503a6d7a3edddf85b40c01720863", "error": "Remote end closed connection without response (retried, see b-retry)"},
    {"contract": "0xd1e75de8e6b46e09a90126a122373fac79578300", "error": "Remote end closed connection without response (retried, see b-retry)"},
    {"contract": "0xd2001b3ef8fb923af515628e717f6ac1bc4a36e1", "error": "Remote end closed connection without response (retried, see b-retry)"}],
    "truncated": []}
retried_ok = set()
if b2retry:
    b2retry_failed = {f["contract"] for f in b2retry.get("failed", [])}
    retried_ok = {c for c in [f["contract"] for f in b2["failed"]] if c not in b2retry_failed}
merged = {
    "from": 131877959, "to": 131886469,
    "contracts_checked": part1["contracts_checked"] + b2["contracts_checked"],
    "total_logs": part1["total_logs"] + b2["total_logs"] + bretry["total_logs"] + b2retry.get("total_logs", 0),
    "hits": part1["hits"] + b2["hits"] + bretry["hits"] + b2retry.get("hits", []),
    "failed": (b2retry.get("failed", []) if b2retry else b2["failed"]),
    "truncated": part1["truncated"] + b2["truncated"] + bretry["truncated"] + b2retry.get("truncated", []),
    "note": ("Part b merged from segments: part1 (contracts 400-849, aggregate-only from "
             "run68-inbound-b.log after the 04:05 worker was interrupted at [450/571]; "
             "its 5 transient-failed contracts retried clean via run68-inbound-b-retry.json) "
             "+ b2 (contracts 850-970, run68-inbound-b2.json) + b2-retry (if any). "
             "Failed list holds only contracts still failing after retry (6 of b2's 7 "
             "recovered on retry and are excluded)."),
}
json.dump(merged, open(D / "run68-inbound-b.json", "w"), indent=1)
print("merged run68-inbound-b.json:", merged["contracts_checked"], "contracts,",
      merged["total_logs"], "logs,", len(merged["hits"]), "hits,",
      len(merged["failed"]), "failed,", len(merged["truncated"]), "truncated")
for f in merged["failed"]:
    print("  STILL FAILED:", f["contract"], f.get("error", "")[:120])
