#!/usr/bin/env python3
"""Hot-leg 15:49 — shape-check 5 Boltbook-new addresses not in main snapshot."""
import json, urllib.request, urllib.error, concurrent.futures
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NEW = ["0x3dec6a08d911484fbded0732e3979b3081e672a4","0x41469589ba5c72e4e55e549b90126a892a9ff0ce","0x923c6faeb74e1a838c2e13d53449b90deaab8fea","0x9270127cbca7c85ef09983df53c4b002b25bd34a","0xce0815c936d31c64092270bd4ee6421c64f2e0a0"]
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
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    for addr, (st, abi) in zip(NEW, ex.map(fetch, NEW)):
        d = {"address": addr, "status": st, "source": "boltbook-frontpage"}
        if abi is not None: d.update(classify(abi))
        out.append(d)
json.dump(out, open(f"{HF}/hot-leg-2026-11-07-1549-boltbook-shape.json","w"), indent=1)
for d in out:
    print(d["address"], d["status"], "S1=", d.get("S1"), "S2=", d.get("S2"), "funcs=", d.get("functions"), "mint=", d.get("mint_fns"), "quote=", d.get("quote_fns"), "free=", d.get("free_views"), "gate=", d.get("gate_fns"))
