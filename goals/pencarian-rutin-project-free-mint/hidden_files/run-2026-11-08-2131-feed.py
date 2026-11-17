#!/usr/bin/env python3
"""Run 2131 route 5a: Sourcify recently-verified feed shape-check (BSC chain 56).
Feed captured via browser.open 21:34 WIB (verifiedAt 14:00:37-14:31:50 UTC).
Same shape logic as run-2026-11-08-2031-feed.py. Read-only.
Saves run-2026-11-08-2131-feed.json next to this script.
"""
import json, time, urllib.request, pathlib

BASE = pathlib.Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

FEED = [
 ("0x8a7a7D5a14175054162c65DDBA4416f4fa72527B", "2026-11-08T14:31:50Z"),
 ("0x6A3722e20d1C9727c290a1b3Cccd5330180d9dE4", "2026-11-08T14:29:41Z"),
 ("0x48B7307480a7d4B7f6F84E044ea9a6D3A6b88F80", "2026-11-08T14:22:16Z"),
 ("0xc47679F1721dc2D07Ad4C8a366fB668Ee4c9945A", "2026-11-08T14:21:02Z"),
 ("0xa5Dbf96Ae47D98696b0719c051b2023A9e9Ad7DF", "2026-11-08T14:20:46Z"),
 ("0x9360E55bB68c90325BCd03f5Fb28BBbF5Ca6739f", "2026-11-08T14:20:37Z"),
 ("0x66aEaEAbd2cE9f668F5Ee06483ceb27AB6d57D5C", "2026-11-08T14:15:37Z"),
 ("0xfc0AA259BAF1973ea3C6f488197b999cedDF837C", "2026-11-08T14:15:09Z"),
 ("0x26E009350Ef80cb542785d57c27c686a582bf605", "2026-11-08T14:14:14Z"),
 ("0xd71a8095e437942414Af2613560493Ae1fD666c1", "2026-11-08T14:11:24Z"),
 ("0xD9FFD1FaF9E4f1cc52e8ae521315eD606f36E35b", "2026-11-08T14:08:39Z"),
 ("0xD836C35Db6fffE22bCb0fCB21062B5e810785c2B", "2026-11-08T14:07:14Z"),
 ("0x567059347Ca1AF24D83Ee0549892Cc20dF7bECa7", "2026-11-08T14:06:04Z"),
 ("0xb2d530c09f9EA3790906312B01C2abc474D2f8Aa", "2026-11-08T14:05:58Z"),
 ("0x1a2E46c22Cb516aa833ffc461A9C30Dc93c55b57", "2026-11-08T14:05:46Z"),
 ("0x7d47e12919EB32011012AAeCaa41dD0f7b7f36Ea", "2026-11-08T14:04:26Z"),
 ("0x21E18aF4015e991Ef28d21445e304c654212E76e", "2026-11-08T14:04:18Z"),
 ("0x070DE9bA926Fd048a62EFd020C3Bd95A34F5ad43", "2026-11-08T14:04:17Z"),
 ("0xa1269485458f923E8C3aF644660c3F9D39C4753f", "2026-11-08T14:02:43Z"),
 ("0xc1BBbbB78eF33a26D1aB0Df020b8A2b9F7a51b27", "2026-11-08T14:00:37Z"),
]
# Boltbook extras shape-checked in the same run (not feed items)
EXTRA = [("0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb", "boltbook Wisp Agent (Sourcify 404 run 2031, re-check)")]

FREE_VIEWS = ["freeclaimed","freeleft","freesupply","freefor","freeused","freeavailable",
              "freesharesremaining","freesharesclaimed","freesharepoolexhausted","freeminted",
              "free","free_count","freecount","freeskunksremaining","free_pool","freepool"]
QUOTE_FNS = ["quote", "cost", "getprice", "price", "costof"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-run2131"})
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
        req2 = urllib.request.Request(url2, headers={"User-Agent": "free-bacot-run2131"})
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
    out = {"run": "2131", "feed_captured_wib": "2026-11-08 21:34 WIB (verifiedAt 14:00:37-14:31:50 UTC)",
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
    json.dump(out, open(BASE / "run-2026-11-08-2131-feed.json", "w"), indent=1)
    print("saved", BASE / "run-2026-11-08-2131-feed.json")

if __name__ == "__main__":
    main()
