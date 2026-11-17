#!/usr/bin/env python3
"""Hot-leg 2026-11-16 19:19 WIB — CORRECTION part 2.
Finishes the 0x1652... shape-check (get_code hardened with retries),
then applies all 4 corrected results + proper bridge check.
The part-1 script crashed before writing, so results 1-3 are re-applied here."""
import json, os, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
STAMP = "2026-11-16-1919"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedBy"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

# results already verified in correction part 1 (stdout, before the crash)
RES = {
 "0x870aD5f304871eC0c63BE1e976406e0b095A32CD": {"shape": "checked-not-sale-shape", "fns": 21, "mint": False, "quote": False, "free_views": [], "registry": False, "token": True, "mintFree": False},
 "0x6a79aE60464E8B77D1fa701857d45e129401B0cd": {"shape": "checked-not-sale-shape", "fns": 20, "mint": False, "quote": False, "free_views": [], "registry": False, "token": True, "mintFree": False},
 "0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab": {"shape": "checked-not-sale-shape", "fns": 85, "mint": True, "quote": True, "free_views": [], "registry": True, "token": True, "mintFree": False},
}

def curl_json(url, timeout=30):
    p = subprocess.run(["curl", "-sS", "--max-time", str(timeout), url],
                       capture_output=True, text=True, timeout=timeout + 5)
    if p.returncode != 0 or not p.stdout.strip():
        return None, f"curl rc={p.returncode} err={p.stderr[:100]}"
    return json.loads(p.stdout), None

def get_code(addr):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                          "params": [addr, "latest"]})
    for ep in ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/"):
        for _ in range(2):
            try:
                p = subprocess.run(["curl", "-sS", "--max-time", "25", "-X", "POST",
                                    "-H", "Content-Type: application/json", "-d", payload, ep],
                                   capture_output=True, text=True, timeout=30)
                if p.stdout.strip():
                    return json.loads(p.stdout).get("result", "") or ""
            except Exception:
                pass
            time.sleep(1)
    return ""

a = "0x165282e726A43988cBF9167684F73CCA6D482822"
d, err = curl_json(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=metadata,abi")
lines = []
if not d:
    RES[a] = {"shape": "abi-unavailable", "err": err}
    lines.append(f"CORRECTION {a}: ABI UNAVAILABLE ({err}) — not a shape verdict, retry next run")
else:
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
    RES[a] = {"shape": shape, "fns": len(names), "mint": has_mint, "quote": has_quote,
              "free_views": free_views, "registry": has_reg, "token": is_token,
              "mintFree": has_mintfree}
    lines.append(f"CORRECTION {a}: fns={len(names)} mint={has_mint} quote={has_quote} "
                 f"free={free_views} reg={has_reg} token={is_token} mintFree={has_mintfree} => {shape}")
print(lines[-1], flush=True)

fs_path = os.path.join(BASE, f"hot-leg-{STAMP}-feedshape.json")
fs = json.load(open(fs_path))
fs.update(RES)
json.dump(fs, open(fs_path, "w"), indent=1)

seen = json.load(open(os.path.join(BASE, "hot-leg-seen.json")))
for addr, r in RES.items():
    if addr in seen:
        seen[addr]["note"] = ("CORRECTED 19:19 run (proper ?fields=metadata,abi fetch): " +
                              json.dumps(r)[:600])
        seen[addr]["status"] = r["shape"]
json.dump(seen, open(os.path.join(BASE, "hot-leg-seen.json"), "w"), indent=1, sort_keys=True)

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
