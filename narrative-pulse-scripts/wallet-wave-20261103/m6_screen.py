import json, sys, urllib.request, time
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr
b = json.load(open('/tmp/m6_breadth.json'))
cands = sorted([w for w, cs in b.items() if len(cs) >= 5])
extra = ["0x9ea96d42cdcb4fc5c8ded51f3a711a996679b95e", "0x075c1bed7dcca884dd990737b6df734b651c1c65"]
for e in extra:
    if e not in cands: cands.append(e)
print("screening", len(cands), "wallets")
def rpc(method, params):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req = urllib.request.Request("https://bsc-dataseed.binance.org/", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)["result"]
latest = int(rpc("eth_blockNumber", []), 16)
win30 = latest - 5760000
print("latest:", latest, "win30 from:", win30)
known = json.load(open('/tmp/m6_known.json'))
allk = {}
for k, vs in known.items():
    for v in vs: allk[v.lower()] = k
out = {}
for w in cands:
    code = rpc("eth_getCode", [w, "latest"])
    is_eoa = (code == "0x")
    try:
        r = ankr.ankr_post("ankr_getTransactionsByAddress", {"blockchain":"bsc","address":[w],"pageSize":1000,
                                                             "fromBlock":hex(win30),"toBlock":hex(latest)})
        res = r.get("result", {})
        txs = res.get("transactions", [])
        capped = bool(res.get("nextPageToken"))
    except Exception as e:
        txs, capped = [], "ERR:"+str(e)[:60]
    funders = {}
    for t in txs:
        if t.get('input','') not in ('0x',''): continue
        try: val = int(t.get('value','0x0'),16)/1e18
        except Exception: continue
        if val <= 0: continue
        if t.get('to','').lower() == w.lower():
            f = t.get('from','').lower()
            e2 = funders.setdefault(f, {'total':0.0,'count':0})
            e2['total'] += val; e2['count'] += 1
    top_f = sorted(funders.items(), key=lambda x:-x[1]['total'])[:3]
    out[w] = {"breadth": len(b[w]) if w in b else None, "contracts": sorted(b[w]) if w in b else [],
              "eoa": is_eoa, "code_len": len(code),
              "tx30d_page1": len(txs), "tx30d_capped": capped,
              "top_funders": [(f, round(v['total'],4), v['count']) for f,v in top_f],
              "overlap": allk.get(w.lower())}
    print(w, "| breadth:", out[w]["breadth"], "| eoa:", is_eoa, "| tx30d:", len(txs), "capped:", capped,
          "| funders:", out[w]["top_funders"], "| overlap:", out[w]["overlap"])
    time.sleep(0.2)
json.dump({"latest": latest, "results": out}, open('/tmp/m6_screen.json','w'), indent=1)
