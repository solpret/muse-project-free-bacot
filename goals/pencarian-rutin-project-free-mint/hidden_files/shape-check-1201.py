#!/usr/bin/env python3
"""Route 5a shape-check for Sourcify feed contracts (run 2026-11-07-1031).
S1: mint fn + quote/cost fn + free-share view + registry/AgentGate.
S2: contract IS token + no-arg free-mint fn + free views + registry/AgentGate.
Read-only: Sourcify ABI fetch + eth_getCode bytes check."""
import json
import sys
import urllib.request
import urllib.error

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single  # noqa: E402

REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/"]

FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeslots", "freesupply"]
QUOTE_FNS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]


def sourcify_abi(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return ("verified", json.loads(resp.read().decode()).get("abi"))
    except urllib.error.HTTPError as e:
        return ("not_verified" if e.code == 404 else f"http_{e.code}", None)
    except Exception as e:  # noqa: BLE001
        return (f"error:{type(e).__name__}", None)


def rpc_call(method, params, timeout=8):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def main():
    feed = json.load(open("sourcify-feed-1201-new.json"))
    results = []
    for item in feed.get("results", []):
        addr = item["address"]
        verified_at = item.get("verifiedAt")
        status, abi = sourcify_abi(addr)
        fns = []
        if isinstance(abi, list):
            for it in abi:
                if it.get("type") == "function":
                    fns.append(it)
        names = [f.get("name", "") for f in fns]
        lower = [n.lower() for n in names]
        has_mint = any("mint" in n for n in lower)
        has_quote = any(any(q in n for q in QUOTE_FNS) for n in lower)
        free_views = [n for n in names if n.lower() in FREE_SHARE_VIEWS]
        has_free_view = bool(free_views)
        gate_names = [n for n in names
                      if "agentregistry" in n.lower() or "agentgate" in n.lower()
                      or "agentid" in n.lower()]
        # bytecode registry check
        reg_bytes = False
        try:
            code = rpc_call("eth_getCode", [addr, "latest"])
            if isinstance(code, str) and len(code) > 2:
                reg_bytes = REGISTRY_BYTES in code[2:].lower()
        except Exception as e:  # noqa: BLE001
            reg_bytes = f"error:{e}"
        registry_ref = bool(gate_names) or reg_bytes is True
        # S1
        s1 = has_mint and has_quote and has_free_view and registry_ref
        # S2: token fns + no-arg free mint + free views + registry
        token_fns = {"name", "symbol", "decimals", "totalsupply"}
        has_token = token_fns <= set(lower)
        noarg_free_mint = False
        for f in fns:
            nm = f.get("name", "").lower()
            if nm in ("mintfree", "freemint", "claimfree", "mintfreeshare"):
                if len(f.get("inputs", [])) == 0:
                    noarg_free_mint = True
        s2 = has_token and noarg_free_mint and has_free_view and registry_ref
        results.append({
            "address": addr, "verifiedAt": verified_at, "sourcify": status,
            "name_fns": names[:40],
            "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free_views, "gate_names": gate_names,
            "registry_bytes": reg_bytes, "S1": s1, "S2": s2,
            "has_token_fns": has_token, "noarg_free_mint": noarg_free_mint,
        })
        print(f"{addr} verifiedAt={verified_at} sourcify={status} "
              f"mint={has_mint} quote={has_quote} free_views={free_views} "
              f"gate={gate_names} reg_bytes={reg_bytes} S1={s1} S2={s2}",
              flush=True)
    json.dump(results, open("sourcify-feed-1201-shape.json", "w"), indent=1)
    hits = [r for r in results if r["S1"] or r["S2"]]
    print(f"SHAPE HITS: {len(hits)} of {len(results)}")
    for h in hits:
        print("HIT:", h["address"], "S1" if h["S1"] else "", "S2" if h["S2"] else "")


if __name__ == "__main__":
    main()
