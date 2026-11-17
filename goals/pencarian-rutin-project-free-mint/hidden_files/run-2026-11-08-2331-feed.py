#!/usr/bin/env python3
"""Run 2331 route 5a: Sourcify recently-verified feed shape-check (BSC chain 56).
Feed captured via browser.open 22:16 WIB (verifiedAt 14:38:26-15:09:07 UTC).
Same shape logic as run-2026-11-08-2031-feed.py. Read-only.
Saves run-2026-11-08-2331-feed.json next to this script.
"""
import json, time, urllib.request, pathlib

BASE = pathlib.Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

FEED = [
 ("0x98C716d82A219Ce5cf25579dDAb95bF8db24a052", "2026-11-08T16:39:49Z"),
 ("0xCc4425A7F63148CA1A70c9504B171811349aC84A", "2026-11-08T16:49:24Z"),
 ("0xc1BD667EfFF832992d0166A3187CCD289A26Af8E", "2026-11-08T16:51:50Z"),
 ("0xB3AC4612E609fce2B98c2f6602D5EFCeeB61C473", "2026-11-08T16:53:36Z"),
 ("0xca93c24bD06eFf6136E346169A44ea1b16f889F3", "2026-11-08T16:56:16Z"),
]
EXTRA = [("0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb", "boltbook Wisp Agent (Sourcify 404 run 2031 + 2131 + 2201 + 2301, re-check ke-6)")]

FREE_VIEWS = ["freeclaimed","freeleft","freesupply","freefor","freeused","freeavailable",
              "freesharesremaining","freesharesclaimed","freesharepoolexhausted","freeminted",
              "free","free_count","freecount","freeskunksremaining","free_pool","freepool"]
QUOTE_FNS = ["quote", "cost", "getprice", "price", "costof"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-run2331"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:
        return None, f"fetch-error: {e}"
    abi = data.get("abi")
    if abi:
        return abi, data.get("match", "")
    try:
        url2 = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
        req2 = urllib.request.Request(url2, headers={"User-Agent": "free-bacot-run2331"})
        with urllib.request.urlopen(req2, timeout=30) as r:
            data2 = json.load(r)
        return data2.get("abi"), data2.get("match", "")
    except Exception as e:
        return None, f"abi-fetch-error: {e} (meta keys: {list(data.keys())})"

def shape(abi):
    if not abi:
        return {"shape": "UNKNOWN-abi-unavailable"}
    names = []
    for e in abi:
        if isinstance(e, dict) and e.get("name"):
            names.append(e["name"])
    low = [n.lower() for n in names]
    lowset = set(low)
    has_mint = any("mint" in n for n in low)
    free_views = sorted({n for n in names if n.lower() in FREE_VIEWS or "free" in n.lower()})
    quote_fns = sorted({n for n in names if n.lower() in QUOTE_FNS})
    has_quote = bool(quote_fns)
    is_token = bool({"name", "symbol", "decimals", "totalsupply"} & lowset)
    raw = json.dumps(abi).lower()
    registry_ref = REGISTRY.lower() in raw or "agentid" in raw or "agentregistry" in raw or "agentgate" in raw
    gate_fn = any("agent" in n for n in low)
    s1 = has_mint and has_quote and bool(free_views) and (registry_ref or gate_fn)
    s2 = is_token and any(n.lower() == "mintfree" for n in names) and bool(free_views) and (registry_ref or gate_fn)
    mint_shape = has_mint and (bool(free_views) or "free" in raw)
    return {
        "functions": names,
        "has_mint": has_mint,
        "free_views": free_views,
        "quote_fns": quote_fns,
        "is_token": is_token,
        "registry_ref_or_gate": bool(registry_ref or gate_fn),
        "S1": s1,
        "S2": s2,
        "mint_shape": mint_shape,
        "shape": ("SALE-S1" if s1 else "SALE-S2" if s2 else "MINT-SHAPE" if mint_shape else "NOT-AGENT-SHAPED"),
    }

def main():
    snap = json.load(open(BASE / "onchain-snapshot.json"))
    snap_addrs = {v.get("address", "").lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    for v in snap.get("track_c", {}).values():
        if isinstance(v, dict):
            for f in ("sale", "token"):
                if v.get(f):
                    snap_addrs.add(str(v[f]).lower())
    seen = json.load(open(BASE / "hot-leg-seen.json"))
    out = {"run": "2331", "feed_captured_wib": "2026-11-08 23:57 WIB (verifiedAt 16:23:56-16:56:16 UTC); 5 of 10 new items already shape-checked by hot-leg 23:44 (all not-sale-shape); GAP 16:17:24-16:23:56Z covered by hot-leg 23:44 poll",
           "items": [], "extra": []}
    for addr, verified_at in FEED + EXTRA:
        abi, note = fetch_abi(addr)
        s = shape(abi) if abi else {"shape": "UNKNOWN-abi-unavailable", "note": note}
        rec = {"address": addr, "verifiedAt": verified_at,
               "in_snapshot": addr.lower() in snap_addrs,
               "in_hotleg_seen": seen.get(addr.lower(), {}).get("status") if isinstance(seen.get(addr.lower()), dict) else None,
               **s}
        (out["items"] if not verified_at.startswith("boltbook") else out["extra"]).append(rec)
        print(addr, rec["shape"], "in_snapshot" if rec["in_snapshot"] else "NEW-vs-snapshot",
              "seen:" + str(rec["in_hotleg_seen"]) if rec["in_hotleg_seen"] else "not-in-hotleg-seen",
              (rec.get("free_views") or "") if abi else note)
        time.sleep(0.5)
    json.dump(out, open(BASE / "run-2026-11-08-2331-feed.json", "w"), indent=1)
    print("saved", BASE / "run-2026-11-08-2331-feed.json")

if __name__ == "__main__":
    main()
