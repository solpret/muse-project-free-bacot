#!/usr/bin/env python3
"""Hot-leg 2026-11-16 19:19 WIB — CORRECTION.
1) Re-shape-check the 4 feed-new contracts with the correct endpoint
   (?fields=metadata,abi) — the main run omitted the fields query and got
   0 fns for all four, which is a fetch artifact, not a shape verdict.
   Also checks bytecode for the registry address (1904 pattern).
2) Proper bridge check: bridge['contracts'] keys vs snapshot
   contracts/track_c/pending_claims keys.
Updates hot-leg-2026-11-16-1919-feedshape.json and hot-leg-seen.json notes
for the 4 contracts, and appends correction lines to the runlog."""
import json, os, subprocess

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
STAMP = "2026-11-16-1919"
NEW = ["0x870aD5f304871eC0c63BE1e976406e0b095A32CD",
       "0x6a79aE60464E8B77D1fa701857d45e129401B0cd",
       "0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab",
       "0x165282e726A43988cBF9167684F73CCA6D482822"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedBy"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

def curl_json(url, timeout=30):
    p = subprocess.run(["curl", "-sS", "--max-time", str(timeout), url],
                       capture_output=True, text=True, timeout=timeout + 5)
    if p.returncode != 0 or not p.stdout.strip():
        return None, f"curl rc={p.returncode} err={p.stderr[:100]}"
    return json.loads(p.stdout), None

def get_code(addr):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                          "params": [addr, "latest"]})
    p = subprocess.run(["curl", "-sS", "--max-time", "25", "-X", "POST",
                        "-H", "Content-Type: application/json", "-d", payload,
                        "https://bsc-dataseed.binance.org/"],
                       capture_output=True, text=True, timeout=30)
    return json.loads(p.stdout).get("result", "") or ""

res = {}
lines = []
for a in NEW:
    d, err = curl_json(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=metadata,abi")
    if not d:
        res[a] = {"shape": "abi-unavailable", "err": err}
        lines.append(f"CORRECTION {a}: ABI UNAVAILABLE ({err}) — not a shape verdict, retry next run")
        print(a, "ABI UNAVAILABLE:", err, flush=True)
        continue
    abi = d.get("abi") or d.get("metadata", {}).get("output", {}).get("abi") or []
    names = [f.get("name", "") for f in abi if f.get("type") == "function"]
    has_mint = any(n.startswith("mint") for n in names)
    has_quote = any("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower() for n in names)
    free_views = [n for n in names if n in FREE_VIEWS]
    code = get_code(a)
    has_reg = REG in code.lower() or any("agentidregistry" in n.lower() or "agentgate" in n.lower() for n in names)
    is_token = any(n in names for n in ("name", "symbol", "decimals", "totalSupply"))
    has_mintfree = "mintFree" in names
    s1 = has_mint and has_quote and bool(free_views) and has_reg
    s2 = is_token and has_mintfree and bool(free_views) and has_reg
    shape = "S1" if s1 else ("S2" if s2 else "checked-not-sale-shape")
    res[a] = {"shape": shape, "fns": len(names), "mint": has_mint, "quote": has_quote,
              "free_views": free_views, "registry": has_reg, "token": is_token,
              "mintFree": has_mintfree}
    lines.append(f"CORRECTION {a}: fns={len(names)} mint={has_mint} quote={has_quote} "
                 f"free={free_views} reg={has_reg} token={is_token} mintFree={has_mintfree} => {shape}")
    print(lines[-1], flush=True)

# merge into feedshape file
fs_path = os.path.join(BASE, f"hot-leg-{STAMP}-feedshape.json")
fs = json.load(open(fs_path))
fs.update(res)
json.dump(fs, open(fs_path, "w"), indent=1)

# update seen notes for the 4 contracts
seen = json.load(open(os.path.join(BASE, "hot-leg-seen.json")))
for a, r in res.items():
    if a in seen:
        seen[a]["note"] = ("CORRECTED 19:19 run (proper ?fields=metadata,abi fetch): " +
                           json.dumps(r)[:600])
        seen[a]["status"] = r["shape"]
json.dump(seen, open(os.path.join(BASE, "hot-leg-seen.json"), "w"), indent=1, sort_keys=True)

# proper bridge check
bridge = json.load(open(os.path.join(BASE, "scan-bridge.json")))
snap = json.load(open(os.path.join(BASE, "onchain-snapshot.json")))
snap_addrs = set()
for sec in ("contracts", "track_c", "pending_claims"):
    v = snap.get(sec)
    if isinstance(v, dict):
        snap_addrs |= {k.lower() for k in v}
bridge_addrs = {k.lower() for k in bridge.get("contracts", {})}
outside = sorted(bridge_addrs - snap_addrs)
same_owner = [k for k, v in bridge.get("contracts", {}).items()
              if isinstance(v, dict) and v.get("same_owner_discarded")]
lines.append(f"Bridge (CORRECTED): mtime 2026-11-08 18:21:53 UTC, "
             f"{len(bridge_addrs)} contracts, {len(outside)} outside snapshot: {outside[:10]}; "
             f"same_owner_discarded in bridge: {len(same_owner)}")
print(lines[-1], flush=True)

with open(os.path.join(BASE, f"hot-leg-{STAMP}-runlog.md"), "a") as f:
    f.write("\n## Correction (same run)\n\n" +
            "\n".join(f"- {l}" for l in lines) + "\n")
print("DONE")
