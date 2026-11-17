#!/usr/bin/env python3
"""Route 5a Sourcify feed shape-check, run 0401 (2026-11-10 04:01 WIB). Read-only.
S1: mint fn + quote/cost fn + free-share view + registry ref/AgentGate.
S2: contract IS the token + no-arg free-mint fn + free views + registry ref/AgentGate.
Skips addresses already in hot-leg-seen or the snapshot (dedupe, case-insensitive)."""
import json, sys, time, urllib.request, urllib.error

FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeremaining",
                    "free_slots", "free_supply", "free_amount"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "quotemintfor", "cost", "costfor",
             "getcost", "price", "mintprice", "feefor"]
GATE_WORDS = ["agentid", "agentregistry", "agentgate", "hasagentid", "isagent"]

def sourcify_abi(address, tries=3):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                return ("verified", data.get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return ("error:retry-exhausted", None)

def classify(abi):
    funcs = []
    if isinstance(abi, list):
        for item in abi:
            if item.get("type") == "function":
                funcs.append(item.get("name", ""))
    low = [f.lower() for f in funcs]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree", "mint", "claimfree") ]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns,
            "free_views": free_views, "gate_fns": gate, "token_fns": token_fns,
            "S1": s1, "S2": s2}

def main():
    feed = json.load(open("run-2026-11-10-0401-sourcify-feed.json"))
    addrs = [(it["address"], it.get("verifiedAt")) for it in feed.get("results", [])]
    try:
        hl = json.load(open("hot-leg-seen.json"))
        hl_keys = {k.lower() for k in hl.keys()}
    except Exception:
        hl_keys = set()
    snap = json.load(open("onchain-snapshot.json"))
    snap_addrs = {v.get("address", "").lower() for v in snap["contracts"].values() if isinstance(v, dict)}
    tc = snap.get("track_c", {})
    snap_addrs |= {str(v.get("sale", "")).lower() for v in tc.values() if isinstance(v, dict)}
    snap_addrs |= {str(v.get("token", "")).lower() for v in tc.values() if isinstance(v, dict)}
    out = []
    for addr, vat in addrs:
        r = {"address": addr, "verifiedAt": vat}
        if addr.lower() in hl_keys:
            r["skip"] = "hot-leg-seen"
        elif addr.lower() in snap_addrs:
            r["skip"] = "in-snapshot"
        else:
            status, abi = sourcify_abi(addr)
            r["sourcify"] = status
            if abi is not None:
                r.update(classify(abi))
            else:
                r["S1"] = False; r["S2"] = False
        out.append(r)
        print(addr, vat, r.get("skip") or r.get("sourcify"), "S1=" + str(r.get("S1")), "S2=" + str(r.get("S2")))
    json.dump(out, open("run-2026-11-10-0401-5a.json", "w"), indent=1)
    print("S1 pass:", [o["address"] for o in out if o.get("S1")])
    print("S2 pass:", [o["address"] for o in out if o.get("S2")])

if __name__ == "__main__":
    main()
