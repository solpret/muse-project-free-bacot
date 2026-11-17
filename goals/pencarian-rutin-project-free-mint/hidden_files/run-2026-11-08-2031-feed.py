#!/usr/bin/env python3
"""Run 2031 route 5a: Sourcify recently-verified feed shape-check (BSC chain 56).
Reads the feed list (captured via browser.open 19:50 WIB), fetches each
contract's ABI from Sourcify, and classifies mint shape / sale shape S1 / S2.
Read-only. Saves run-2026-11-08-2031-feed.json next to this script.
"""
import json, re, sys, time, urllib.request, pathlib

BASE = pathlib.Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

FEED = [
 ("0xDA24B86580eD5415864459E8aFDCE6CBfa5040ae", "2026-11-08T13:25:56Z"),
 ("0xb1Cd9137B15F8CDE141532c9F1c7F0D336610FA9", "2026-11-08T13:23:48Z"),
 ("0x5C7C5596d11E43BB77a55D7cef3e2Ad00b0011c0", "2026-11-08T13:21:31Z"),
 ("0x333f382119d6515359239CDECDAF7Ed75911245f", "2026-11-08T13:16:49Z"),
 ("0x607feb8bdFC957184dFB497f84c7395f62b5c5f4", "2026-11-08T13:14:56Z"),
 ("0x970532125bFE23c8F3b06a99c5f8E602Ee32958B", "2026-11-08T13:14:31Z"),
 ("0xf4BaCF30fB8F69373F63D99C657F53DD7774Af1D", "2026-11-08T13:12:32Z"),
 ("0x169F9cfC148ba462Bb0073466939e8Eae32C0be5", "2026-11-08T13:12:29Z"),
 ("0xef4Fa905b107A431FcaEB50F1183B712dc3eb9D6", "2026-11-08T13:12:26Z"),
 ("0xaC3f9A33c653FB3CA49056cFA5eDf19101DeBf97", "2026-11-08T13:12:23Z"),
 ("0x6a90E032D50C6FF44608167f7a8634c77ACAeE34", "2026-11-08T13:12:21Z"),
 ("0x3A34FA47A05AA8f1D5ABF1331B98A28d04BE80c9", "2026-11-08T13:11:07Z"),
 ("0x6c35b4f82CF04bf334d1b4443c0509b0e7395AA8", "2026-11-08T13:05:20Z"),
 ("0x30578B073B34714cCC1B4a1aF437EaE17cF0B3f0", "2026-11-08T13:04:12Z"),
 ("0xd80d1e88290186f2Fd3458A4B060F74763cB148b", "2026-11-08T13:02:49Z"),
 ("0x3ED1Ec5e209CfC9A2DCc634A7d9C823C0c3F0339", "2026-11-08T13:02:30Z"),
 ("0x9B1aE96ed1BBEA23572225DEb9fFF4E0E697AD3d", "2026-11-08T13:01:21Z"),
 ("0x05c61Ce4D79460C801bb04FdedE93fE570d498FB", "2026-11-08T13:01:15Z"),
 ("0x2d0C1313c50050698575E49D1cd9bC2B9Be51A4F", "2026-11-08T13:00:02Z"),
 ("0x20a409058c3b2d915aAd7e9A9Bc847304b47436b", "2026-11-08T12:59:19Z"),
]
# Boltbook extras shape-checked in the same run (not feed items)
EXTRA = [("0xc3ce00677dad113f5d466d46c8c7b3a227855a5b", "boltbook ALL ACCESS wave4"),
 ("0xa4835228a47e8dcaa7ff44e2c9fd1c46c94b99da", "boltbook THE KEY wave4"),
 ("0x1de1a2bce14bbc230a21ec7b579a6591f43e1e4a", "boltbook GOLDEN TICKET wave4"),
 ("0x7d6e8528cc918afbd0ba5b0998c8a57860d2ded6", "boltbook BMT Agents"),
 ("0xef870a9b4a529373fb2e174b59ca7a66eb018074", "boltbook Saturnagent"),
 ("0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb", "boltbook Wisp Agent")]
# Boltbook extras shape-checked in the same run (not feed items)


FREE_VIEWS = ["freeclaimed","freeleft","freesupply","freefor","freeused","freeavailable",
              "freesharesremaining","freesharesclaimed","freesharepoolexhausted","freeminted",
              "free","free_count","freecount","freeskunksremaining","free_pool","freepool"]
QUOTE_FNS = ["quote", "cost", "getprice", "price", "costof"]
MINT_FNS = ["mint", "freemint", "mintfree", "claimfree", "claim", "freemint"]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-run2031"})
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
        req2 = urllib.request.Request(url2, headers={"User-Agent": "free-bacot-run2031"})
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
    out = {"run": "2031", "feed_captured_wib": "2026-11-08 20:26 WIB (verifiedAt 12:59:19-13:25:56 UTC)",
           "items": [], "extra": []}
    for addr, verified_at in FEED + EXTRA:
        abi, note = fetch_abi(addr)
        s = shape(abi) if abi else {"shape": "UNKNOWN-abi-unavailable", "note": note}
        rec = {"address": addr, "verifiedAt": verified_at,
               "in_snapshot": addr.lower() in snap_addrs, **s}
        (out["items"] if not verified_at.startswith("boltbook") else out["extra"]).append(rec)
        print(addr, rec["shape"], "in_snapshot" if rec["in_snapshot"] else "NEW", (rec.get("free_views") or "") if abi else note)
        time.sleep(0.5)
    json.dump(out, open(BASE / "run-2026-11-08-2031-feed.json", "w"), indent=1)
    print("saved", BASE / "run-2026-11-08-2031-feed.json")

if __name__ == "__main__":
    main()
