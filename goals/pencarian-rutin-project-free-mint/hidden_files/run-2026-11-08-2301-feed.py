#!/usr/bin/env python3
"""Run 2301 route 5a: Sourcify recently-verified feed shape-check (BSC chain 56).
Feed captured via browser.open 22:16 WIB (verifiedAt 14:38:26-15:09:07 UTC).
Same shape logic as run-2026-11-08-2031-feed.py. Read-only.
Saves run-2026-11-08-2301-feed.json next to this script.
"""
import json, time, urllib.request, pathlib

BASE = pathlib.Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

FEED = [
 ("0x332EFB8A690Fd31cB174683f23ff81eD0a4d7F29", "2026-11-08T16:17:24Z"),
 ("0xC874d1706BB687e3ED1a1c0Cec0328C71f517c5E", "2026-11-08T16:15:56Z"),
 ("0x5160C9A62b48544696f3F12081377098EddfA34e", "2026-11-08T16:14:36Z"),
 ("0x1D45176318eb9B9613F4dF62aed8A070D9F1aB71", "2026-11-08T16:04:54Z"),
 ("0xD743c793b23D1adE2099892B010d4F4530d44E0a", "2026-11-08T16:04:45Z"),
 ("0xB12e5b1F6FAE946b05428DCa5eaf3b45337fDB82", "2026-11-08T16:04:08Z"),
 ("0xcc9f9530B558addd9525d3fB10f483CC8D769C05", "2026-11-08T16:03:34Z"),
 ("0xA036460E8117B903b5191Dc48AfC8441f20Eb3C3", "2026-11-08T16:03:28Z"),
 ("0xee5df6033087FE02fD20de179f3A105A549d8489", "2026-11-08T16:01:24Z"),
 ("0x5e9f29c4b8b23dD3aB3cAbB4a59c875983dCB036", "2026-11-08T15:56:33Z"),
 ("0x22A9C28C2Ca94E467848D97452A72cCCE22ADF66", "2026-11-08T15:56:32Z"),
 ("0x0eB254c365C8a50Bdb4C6E3c3Eb056916CA1A6Ea", "2026-11-08T15:56:27Z"),
 ("0x7F00b3Aa3A3e41dc145180C4ED8a24eE568eaED4", "2026-11-08T15:56:08Z"),
 ("0x252B2724A94043f2C2b46AC85c0305A10fc52cf5", "2026-11-08T15:52:46Z"),
 ("0xbF068824a4d6620a10494a1331A65dac4233666A", "2026-11-08T15:52:45Z"),
 ("0x33D67B9A91D9b3B6dE447fd6B6C6b96e8d2E76ea", "2026-11-08T15:52:39Z"),
 ("0x260e1601544f368a0a38658b9Ec40823ceE3f900", "2026-11-08T15:50:59Z"),
 ("0xCe977d67a93C12F6f306b331507431A0C7590C51", "2026-11-08T15:50:59Z"),
 ("0x5cD95F73ff88415305561a368eA39E87994eA6eA", "2026-11-08T15:50:51Z"),
 ("0x94a0d68A168339Af7cE4af0effFe73511E2720b8", "2026-11-08T15:44:58Z"),
]
# Boltbook extras shape-checked in the same run (not feed items)
EXTRA = [("0x356E46EE71fA2780307De7b3F2D6d1522c9cc5C3", "recheck-2301 UNKNOWN run 2201 (fetch timeout)"),
 ("0x4Ce4ff25543bFae75583753150DfC0f6C93A5065", "recheck-2301 UNKNOWN run 2201 (fetch timeout)"),
 ("0x280f7056BC38f92C0E8dA291fB5fF70bc45556eA", "recheck-2301 UNKNOWN run 2201 (fetch timeout)"),
 ("0x75676757b35191c5E4C50890c8775aeCbe1ef9F6", "recheck-2301 UNKNOWN run 2201 (fetch timeout)"),
 ("0x1732Dd1ADcbbaDF5a2FA28222073C78965dD75B3", "recheck-2301 UNKNOWN run 2201 (fetch timeout)"),
 ("0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb", "boltbook Wisp Agent (Sourcify 404 run 2031 + 2131 + 2201, re-check ke-5)"),
 ("0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9", "boltbook Hexrotta HEXRTA (Boltbook 23:1x post, NEW run 2301)")]

FREE_VIEWS = ["freeclaimed","freeleft","freesupply","freefor","freeused","freeavailable",
              "freesharesremaining","freesharesclaimed","freesharepoolexhausted","freeminted",
              "free","free_count","freecount","freeskunksremaining","free_pool","freepool"]
QUOTE_FNS = ["quote", "cost", "getprice", "price", "costof"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-run2301"})
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
        req2 = urllib.request.Request(url2, headers={"User-Agent": "free-bacot-run2301"})
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
    out = {"run": "2301", "feed_captured_wib": "2026-11-08 23:20 WIB (verifiedAt 15:44:58-16:17:24 UTC); GAP 15:09:07-15:44:58Z never polled (limit-20 sampling gap)",
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
    json.dump(out, open(BASE / "run-2026-11-08-2301-feed.json", "w"), indent=1)
    print("saved", BASE / "run-2026-11-08-2301-feed.json")

if __name__ == "__main__":
    main()
