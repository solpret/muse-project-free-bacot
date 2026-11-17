#!/usr/bin/env python3
"""Run 1931 route 5a: Sourcify recently-verified feed shape-check (BSC chain 56).
Reads the feed list (captured via browser.open 19:50 WIB), fetches each
contract's ABI from Sourcify, and classifies mint shape / sale shape S1 / S2.
Read-only. Saves run-2026-11-08-1931-feed.json next to this script.
"""
import json, re, sys, time, urllib.request, pathlib

BASE = pathlib.Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

FEED = [
 ("0x16b7799e73eDCe926a22E0b2C011c27AD0059d24", "2026-11-08T12:43:49Z"),
 ("0xF8D17D7d1c9673A5A24ab322160C4eC5203705f2", "2026-11-08T12:42:00Z"),
 ("0x491DB9BA55fd54bA794F104D2d80E2B1b407369C", "2026-11-08T12:41:49Z"),
 ("0xe6ee2a573047598B2452a879F2188B31d0442dbF", "2026-11-08T12:40:55Z"),
 ("0xFafE4c4CEc5Ed070A4aFDc0f92826c5Ba276Cb80", "2026-11-08T12:40:45Z"),
 ("0xCE40449B773a3E6E5e769ADb4e567179d4828cbd", "2026-11-08T12:40:35Z"),
 ("0xDfDbF9DAFbc94Cb1F827d3364637dDBB26823739", "2026-11-08T12:40:24Z"),
 ("0x5b3735F362ed89b51FBe244509e398BFDDaC8da9", "2026-11-08T12:40:14Z"),
 ("0x50a998cf59Fe719129702125C9078b0B429DA6E7", "2026-11-08T12:40:05Z"),
 ("0x85aa49526287F06cb36d57121BC7abAF58a8787a", "2026-11-08T12:39:55Z"),
 ("0x16691f500541ca35bd63DD878B6D78728C9518AE", "2026-11-08T12:39:46Z"),
 ("0xc79Cb7efEBd121DC4B39eA141C214606595D665A", "2026-11-08T12:39:36Z"),
 ("0x10BA1AA0F56790835a3462371cCbeAa7A4BA1e46", "2026-11-08T12:39:27Z"),
 ("0x5499Aa0d1a7Ee06B92f3d9213774Ae848bC8c9A4", "2026-11-08T12:39:17Z"),
 ("0x04480f1Ba2252CDF89deB022B58d0a03d1B4cF91", "2026-11-08T12:39:08Z"),
 ("0xc594053D4b2FaA311b55dDbFAb2338f7c90D6632", "2026-11-08T12:38:58Z"),
 ("0x1Ce917B3c4236596AA0bA2735DcdE62b0D0ca4c2", "2026-11-08T12:38:49Z"),
 ("0x9975d7064e40D16E1B76B90e56F606D72B385701", "2026-11-08T12:38:39Z"),
 ("0x555ba73dB1b006F3f2C7dB7126d6e4343aDBce02", "2026-11-08T12:38:29Z"),
 ("0x459cbFFFA49530422fD81c3415686eD2187d047D", "2026-11-08T12:38:20Z"),
]
# Boltbook extras shape-checked in the same run (not feed items)
EXTRA = [("0x51d3c0101696956baf928899d5bb57544f00c9b9", "boltbook ORBIT PASS post, verifiedAt 2026-11-08T10:35:16Z")]

FREE_VIEWS = ["freeclaimed","freeleft","freesupply","freefor","freeused","freeavailable",
              "freesharesremaining","freesharesclaimed","freesharepoolexhausted","freeminted",
              "free","free_count","freecount","freeskunksremaining","free_pool","freepool"]
QUOTE_FNS = ["quote", "cost", "getprice", "price", "costof"]
MINT_FNS = ["mint", "freemint", "mintfree", "claimfree", "claim", "freemint"]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-run1931"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:
        return None, f"fetch-error: {e}"
    # v2 contract endpoint may embed abi under 'abi' or require files endpoint
    abi = data.get("abi")
    if abi:
        return abi, data.get("match", "")
    # fallback: metadata -> abi via files endpoint
    try:
        url2 = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
        req2 = urllib.request.Request(url2, headers={"User-Agent": "free-bacot-run1931"})
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
    has_mint = any(any(m in n for m in ("mint",)) for n in low)
    has_free_fn = any("free" in n for n in low)
    free_views = sorted({n for n in names if n.lower() in FREE_VIEWS or "free" in n.lower()})
    quote_fns = sorted({n for n in names if n.lower() in QUOTE_FNS})
    has_quote = bool(quote_fns)
    is_token = bool({"name", "symbol", "decimals", "totalsupply"} & lowset)
    raw = json.dumps(abi).lower()
    registry_ref = REGISTRY.lower() in raw or "agentid" in raw or "agentregistry" in raw or "agentgate" in raw
    gate_fn = any("agent" in n for n in low)
    s1 = has_mint and has_quote and bool(free_views) and (registry_ref or gate_fn)
    s2 = is_token and any(n in ("mintfree", "mintFree") or n.lower() == "mintfree" for n in names) and bool(free_views) and (registry_ref or gate_fn)
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
    out = {"run": "1931", "feed_captured_wib": "2026-11-08 19:50 WIB (verifiedAt 12:38:20-12:43:49 UTC)",
           "items": [], "extra": []}
    for addr, verified_at in FEED + [("0x51d3c0101696956baf928899d5bb57544f00c9b9", "boltbook-extra")]:
        abi, note = fetch_abi(addr)
        s = shape(abi) if abi else {"shape": "UNKNOWN-abi-unavailable", "note": note}
        rec = {"address": addr, "verifiedAt": verified_at,
               "in_snapshot": addr.lower() in snap_addrs, **s}
        (out["items"] if verified_at != "boltbook-extra" else out["extra"]).append(rec)
        print(addr, rec["shape"], "in_snapshot" if rec["in_snapshot"] else "NEW", (rec.get("free_views") or "") if abi else note)
        time.sleep(0.5)
    json.dump(out, open(BASE / "run-2026-11-08-1931-feed.json", "w"), indent=1)
    print("saved", BASE / "run-2026-11-08-1931-feed.json")

if __name__ == "__main__":
    main()
