#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 15:49 WIB — leg 1: Sourcify feed poll + shape-check new contracts."""
import json, urllib.request, urllib.error, concurrent.futures, time
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
t0 = time.time()
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
req = urllib.request.Request("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", headers={"User-Agent": "Mozilla/5.0"})
feed = None
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        feed = json.loads(r.read().decode())
except Exception as e:
    feed = {"error": str(e)}
addrs = []
if isinstance(feed, dict) and "results" in feed:
    for c in feed["results"]:
        a = c.get("address") or (c.get("contract") or {}).get("address")
        if a: addrs.append(a)
elif isinstance(feed, list):
    for c in feed:
        a = c.get("address")
        if a: addrs.append(a)
json.dump({"feed_raw": feed, "addrs": addrs}, open(f"{HF}/hot-leg-2026-11-07-1604-sourcify.json", "w"), indent=1)
new = [a for a in addrs if a not in seen and a.lower() not in EXCLUDED]
new_excl = [a for a in addrs if a.lower() in EXCLUDED]
print("feed_addrs:", len(addrs), "new:", len(new), "new_excluded:", new_excl)

FREE_SHARE_VIEWS = ["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeremaining","free_slots","free_supply","free_amount"]
QUOTE_FNS = ["quote","quotefor","quotemint","quotemintfor","cost","costfor","getcost","price","mintprice","feefor"]
GATE_WORDS = ["agentid","agentregistry","agentgate","hasagentid","isagent"]
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for _ in range(2):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                return ("verified", json.loads(resp.read().decode()).get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404: return ("not_verified", None)
        except Exception as e:
            last = str(e)
    return ("error:"+last[:80], None)
def classify(abi):
    funcs = [i.get("name","") for i in abi if isinstance(abi, list) and i.get("type")=="function"]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name","symbol","decimals","totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree","mint","claimfree")]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns, "free_views": free_views, "gate_fns": gate, "token_fns": token_fns, "S1": s1, "S2": s2}
out = []
if new:
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for addr, (st, abi) in zip(new, ex.map(fetch, new)):
            d = {"address": addr, "status": st}
            if abi is not None:
                d.update(classify(abi))
            out.append(d)
json.dump(out, open(f"{HF}/hot-leg-2026-11-07-1604-sourcify-shape.json","w"), indent=1)
for d in out:
    print(d["address"], d["status"], "S1=", d.get("S1"), "S2=", d.get("S2"), "funcs=", d.get("functions"), "mint=", d.get("mint_fns"), "quote=", d.get("quote_fns"), "free=", d.get("free_views"), "gate=", d.get("gate_fns"))
print("elapsed %.1fs" % (time.time()-t0))
