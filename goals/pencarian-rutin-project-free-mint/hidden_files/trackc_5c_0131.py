#!/usr/bin/env python3
"""Route 5c ERC-20 backlog shape-check, run 0131 (2026-11-06). Read-only.
From this run's scan output: ERC-20 contracts with window mint_count >= 10,
sorted desc, shape-check at most 20 not already in track-c-scan-checked.json
(nested 'checked' dict + top-level keys, case-insensitive). S1/S2 as in body.
Records newly checked addresses in track-c-scan-checked.json."""
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
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree", "mint", "claimfree")]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns,
            "free_views": free_views, "gate_fns": gate, "token_fns": token_fns,
            "S1": s1, "S2": s2}

def main():
    scan = json.load(open("onchain-scan-2026-11-06-0131.json"))
    checked = json.load(open("track-c-scan-checked.json"))
    checked_set = set()
    if isinstance(checked, dict):
        nested = checked.get("checked")
        if isinstance(nested, dict):
            checked_set |= {k.lower() for k in nested.keys()}
        checked_set |= {k.lower() for k in checked.keys() if k != "checked"}
    cands = sorted([e for e in scan["erc20_mint_contracts_list"] if e.get("mint_count", 0) >= 10],
                   key=lambda e: -e.get("mint_count", 0))
    print("mint_count>=10 in window:", len(cands))
    todo = [e for e in cands if e["address"].lower() not in checked_set][:20]
    dropped = len(cands) - len([e for e in cands if e["address"].lower() not in checked_set])
    print("new to check (max 20):", len(todo), "| already-checked among >=10:", dropped,
          "| remainder dropped (sampling limit):", max(0, len([e for e in cands if e["address"].lower() not in checked_set]) - 20))
    out = []
    for e in todo:
        addr = e["address"]
        r = {"address": addr, "mint_count": e.get("mint_count"), "name": e.get("name"), "symbol": e.get("symbol")}
        status, abi = sourcify_abi(addr)
        r["sourcify"] = status
        if abi is not None:
            r.update(classify(abi))
        else:
            r["S1"] = False
            r["S2"] = False
        out.append(r)
        print(addr, "mints=", e.get("mint_count"), status, "S1=", r["S1"], "S2=", r["S2"],
              ("mint=" + str(r.get("mint_fns")) + " quote=" + str(r.get("quote_fns")) + " free=" + str(r.get("free_views")) + " gate=" + str(r.get("gate_fns"))) if abi is not None else "")
        if isinstance(checked.get("checked"), dict):
            checked["checked"][addr.lower()] = {"run": "0131-2026-11-06", "sourcify": status, "S1": r["S1"], "S2": r["S2"]}
        else:
            checked[addr.lower()] = {"run": "0131-2026-11-06", "sourcify": status, "S1": r["S1"], "S2": r["S2"]}
    json.dump(out, open("trackc-5c-2026-11-06-0131.json", "w"), indent=1)
    json.dump(checked, open("track-c-scan-checked.json", "w"), indent=1)
    print("S1 pass:", [o["address"] for o in out if o.get("S1")])
    print("S2 pass:", [o["address"] for o in out if o.get("S2")])

if __name__ == "__main__":
    main()
