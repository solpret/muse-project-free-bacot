#!/usr/bin/env python3
"""First-seen agent-shaped triage, run 2026-11-01 20:31 WIB.
Reads totalSupply + free counters for scan first-seen contracts that are
Sourcify-verified AND carry a free-mint function/free-supply constant.
A contract whose on-chain total/freeClaimed far exceeds its scan-window
mint count did NOT have its first mints in this run (continuation, not
an early lead). REVERT = view absent, not zero. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

scan = json.load(open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-scan-2026-11-01-2031.json"))
seen = json.load(open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-scan-seen.json"))
seen_addrs = {a.lower() for a in seen.get("contracts", {})} | {a.lower() for a in seen.get("known_older_leads", {})}
EXCLUDED_NAMES = {"Piggy Agent", "Laser Agents"}
cands = []
for c in scan["contracts"]:
    if c["address"].lower() in seen_addrs:
        continue
    if c["sourcify"] != "verified" or not c["free_shaped"]:
        continue
    if c["name"] in EXCLUDED_NAMES:
        continue
    cands.append(c)
print(f"candidates: {len(cands)}")
VIEWS = ["totalSupply()", "FREE_SUPPLY()", "FREE_CAP()", "freeClaimed()", "freeLeft()", "freeMinted()"]
calls, meta = [], []
for c in cands:
    for v in VIEWS:
        calls.append((c["address"], sel(v))); meta.append((c["address"], v))

def batch_read(calls, meta):
    """Batch with per-item revert tolerance: on batch failure naming an
    item id, mark it revert and retry the rest."""
    results = {}
    todo = list(range(len(calls)))
    while todo:
        sub = [calls[i] for i in todo]
        try:
            out = batch([("eth_call", [{"to": to, "data": data}, "latest"]) for to, data in sub])
            for j, i in enumerate(todo):
                results[i] = out[j]
            break
        except Exception as e:
            msg = str(e)
            import re
            m = re.search(r"batch item (\d+) error", msg)
            if m:
                bad_sub = int(m.group(1)) - 1
                bad = todo[bad_sub]
                results[bad] = None  # revert/absent
                todo = todo[:bad_sub] + todo[bad_sub + 1:]
                continue
            # Unparseable batch failure: fall back to singles for remainder
            from fast_rpc import _single
            for i in todo:
                to, data = calls[i]
                try:
                    results[i] = _single("https://bsc-dataseed.binance.org/", "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
                except Exception:
                    results[i] = None
            break
    return results

res = batch_read(calls, meta)
out = {}
for c in cands:
    d = {"scan_mints": c["mint_count"], "scan_minters": c["distinct_minters"],
         "scan_first_block": c["first_block"], "scan_last_block": c["last_block"],
         "registry": c["registry_bytes_hit"], "free_shaped": c["free_shaped"], "name": c["name"]}
    for v in VIEWS:
        idx = meta.index((c["address"], v)) if (c["address"], v) in meta else None
        raw = res.get(idx) if idx is not None else None
        try: d[v] = int(raw, 16) if raw else None
        except Exception: d[v] = None
        if raw is None: d[v + "_revert"] = True
    out[c["address"]] = d
print(json.dumps(out, indent=1))
with open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-2031-earlycheck.json", "w") as f:
    json.dump(out, f, indent=1)
