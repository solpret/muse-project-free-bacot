#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 15:34 WIB — leg 1 shape-check for 12 new Sourcify-feed contracts.
Read-only. Uses Sourcify ABI (singular /contract/ endpoint, ?fields=abi).
Same S1/S2 classify logic as feed_shape_0001.py. Concurrent, timeout 12s, 2 tries."""
import json, urllib.request, urllib.error, concurrent.futures

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeremaining",
                    "free_slots", "free_supply", "free_amount"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "quotemintfor", "cost", "costfor",
             "getcost", "price", "mintprice", "feefor"]
GATE_WORDS = ["agentid", "agentregistry", "agentgate", "hasagentid", "isagent"]

NEW = [
    "0x53646dc5b2575E040f83eE710a8A4BD62E7B9432",
    "0x50E4506E76E816ed5e74557B4b8a57037D927777",
    "0x10A500AC748aDfDB4b06ae9d4f6F2Aa79fd349A0",
    "0xE9eBad625A69ffEc5934886f5251c5f85F00716f",
    "0x1f67A40693D4bEAD33D57e7DC04E508A41618c36",
    "0xe2Fcef1a5A1D6df9e56Fe5c0da8c87654194d6f8",
    "0xB7F8524722277Af712f370676144ddb4a19Dfe09",
    "0x75Ac13cF23a8dccC703D1496138251FD7f247890",
    "0x414847eEB73476beA35faed539A9C3136F397Df4",
    "0xdE46494bb92D815022c7333D640d564eac50DfAE",
    "0x5BBDD49356B4170ABc9B1c1Cb37cc4CCc4b769ca",
    "0x39ae9b9F25203975d3a15ECceE37F50407e38D41",
]

def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for attempt in range(2):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
                return ("verified", data.get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
        except Exception as e:
            last = str(e)
    return ("error:" + last[:80], None)

def classify(abi):
    funcs = [i.get("name", "") for i in abi if isinstance(abi, list) and i.get("type") == "function"]
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

out = []
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    results = list(ex.map(fetch, NEW))
for addr, (status, abi) in zip(NEW, results):
    r = {"address": addr, "sourcify": status}
    if abi is not None:
        r.update(classify(abi))
    else:
        r["S1"] = False; r["S2"] = False
    out.append(r)
    print(addr, status, "S1=" + str(r["S1"]), "S2=" + str(r["S2"]),
          ("mint=" + str(r.get("mint_fns")) + " quote=" + str(r.get("quote_fns")) +
           " free=" + str(r.get("free_views")) + " gate=" + str(r.get("gate_fns"))) if abi is not None else "")
json.dump(out, open(f"{HF}/hot-leg-2026-11-07-1534-shape.json", "w"), indent=1)
print("S1 pass:", [o["address"] for o in out if o.get("S1")])
print("S2 pass:", [o["address"] for o in out if o.get("S2")])
print("transport-fail:", [o["address"] for o in out if o.get("sourcify", "").startswith("error")])
