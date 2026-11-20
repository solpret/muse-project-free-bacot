import json, urllib.request
from eth_utils import keccak
ENDPOINTS=["https://bsc-dataseed.binance.org","https://bsc-dataseed1.binance.org","https://bsc-dataseed1.defibit.io","https://bsc-dataseed2.binance.org"]
def sel(s): return keccak(text=s).hex()[:8]
def call(ep, method, params):
    payload=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(ep, data=payload, headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r: return json.load(r)
def eth_call(ep, to, data):
    j=call(ep,"eth_call",[{"to":to,"data":data},"latest"])
    if "error" in j: raise Exception(str(j["error"]))
    return j["result"]
def try_all(fn):
    for ep in ENDPOINTS:
        try: return fn(ep)
        except Exception: pass
    return None
entries=json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
out={}
for e in entries:
    sc=e.get("sale_contract")
    if not sc: continue
    st={}
    for fname in ["launched()","tradingOpen()","isOpen()","opened()","phase()"]:
        r=try_all(lambda ep, s=sc, f=fname: eth_call(ep,s,"0x"+sel(f)))
        st[fname]=r
    out[e["symbol"]]=st
print(json.dumps(out, indent=1))
