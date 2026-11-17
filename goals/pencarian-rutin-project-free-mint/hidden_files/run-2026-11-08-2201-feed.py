#!/usr/bin/env python3
"""Run 2201 route 5a: Sourcify recently-verified feed shape-check (BSC chain 56).
Feed captured via browser.open 22:16 WIB (verifiedAt 14:38:26-15:09:07 UTC).
Same shape logic as run-2026-11-08-2031-feed.py. Read-only.
Saves run-2026-11-08-2201-feed.json next to this script.
"""
import json, time, urllib.request, pathlib

BASE = pathlib.Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

FEED = [
 ("0x319f04149Cd19220b8Fa67f3218fE0E85836a500", "2026-11-08T15:09:07Z"),
 ("0xD4b0756740e4883fFCdC0121D2A073ccF0D2B0c5", "2026-11-08T15:06:47Z"),
 ("0x8Ceba5BA4aEefB71F009807C7fF9D5200E76E7AD", "2026-11-08T15:06:39Z"),
 ("0xaaDAB49bE5Ecaf30f04d17bb65F35ac8494e5Fbb", "2026-11-08T15:06:34Z"),
 ("0x63a2FBe7c82808A5dF6FA3a5654205616f530f4D", "2026-11-08T15:05:23Z"),
 ("0xC0e5F7A6470d012B5957C7dD05AB29C42c910C87", "2026-11-08T15:03:53Z"),
 ("0xb31D2c624e5198cD7E52CDa22867ac7100Ba8DAA", "2026-11-08T14:58:11Z"),
 ("0x356E46EE71fA2780307De7b3F2D6d1522c9cc5C3", "2026-11-08T14:57:21Z"),
 ("0x4Ce4ff25543bFae75583753150DfC0f6C93A5065", "2026-11-08T14:53:31Z"),
 ("0x280f7056BC38f92C0E8dA291fB5fF70bc45556eA", "2026-11-08T14:52:24Z"),
 ("0x75676757b35191c5E4C50890c8775aeCbe1ef9F6", "2026-11-08T14:52:22Z"),
 ("0x1732Dd1ADcbbaDF5a2FA28222073C78965dD75B3", "2026-11-08T14:52:21Z"),
 ("0xf4dC5600D2546E1e52b8cA81169D3Cec53264b68", "2026-11-08T14:49:58Z"),
 ("0xD7bF3e5Ae047Cd0e7a3Da29FA75f2A8c0FC7b65D", "2026-11-08T14:49:46Z"),
 ("0x7c1B4a6652FAe734584694f7a0C6362e9afaEe8f", "2026-11-08T14:48:48Z"),
 ("0x2b76b4Cc9707Cdb736bC464dde7412ccA1bf9e2d", "2026-11-08T14:48:06Z"),
 ("0x86d9890eAb08a0D1FB4001E6d9567ac0C889Ba4c", "2026-11-08T14:48:06Z"),
 ("0x7cd1C2a0EE1DB8Bb3CE82270ec2610Be74A1285d", "2026-11-08T14:47:54Z"),
 ("0x0209CCf8bD8f5686817AD2899BFe3D8AC06b3edc", "2026-11-08T14:43:01Z"),
 ("0xAbae09566a83A82D7f79e0182893fFbDc7A18115", "2026-11-08T14:38:26Z"),
]
# Boltbook extras shape-checked in the same run (not feed items)
EXTRA = [("0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb", "boltbook Wisp Agent (Sourcify 404 run 2031 + 2131, re-check ke-4)")]

FREE_VIEWS = ["freeclaimed","freeleft","freesupply","freefor","freeused","freeavailable",
              "freesharesremaining","freesharesclaimed","freesharepoolexhausted","freeminted",
              "free","free_count","freecount","freeskunksremaining","free_pool","freepool"]
QUOTE_FNS = ["quote", "cost", "getprice", "price", "costof"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-run2201"})
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
        req2 = urllib.request.Request(url2, headers={"User-Agent": "free-bacot-run2201"})
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
    out = {"run": "2201", "feed_captured_wib": "2026-11-08 22:16 WIB (verifiedAt 14:38:26-15:09:07 UTC)",
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
    json.dump(out, open(BASE / "run-2026-11-08-2201-feed.json", "w"), indent=1)
    print("saved", BASE / "run-2026-11-08-2201-feed.json")

if __name__ == "__main__":
    main()
