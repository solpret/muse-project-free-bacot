import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def block_ts(n):
    body=json.dumps({"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[hex(n),False],"id":1}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json"}, method='POST')
            with urllib.request.urlopen(req, timeout=10) as r:
                j=json.load(r)
            if j.get('result'): return int(j['result']['timestamp'],16)
        except Exception:
            pass
    return None
def first_mint(addr, from_block):
    logs=[]; page=None; calls=0
    while True:
        params={"blockchain":"bsc","fromBlock":hex(from_block),"toBlock":"latest",
                "address":addr.lower(),"topics":[TRANSFER, ZERO],"pageSize":1000}
        if page: params["pageToken"]=page
        body=ankr_post("ankr_getLogs", params, timeout=30); calls+=1
        res=body.get('result',{}) if isinstance(body,dict) else {}
        ls=res.get('logs',[]) or []
        logs.extend(ls)
        page=res.get('nextPageToken')
        if not page or calls>=10: break
    if not logs: return None, 0, calls
    blocks=sorted(int(l['blockNumber'],16) for l in logs)
    minters=len({l['topics'][2] for l in logs if len(l.get('topics',[]))>2})
    return blocks[0], len(logs), calls, minters, blocks[-1]
out={}
for label, addr, fb in [
    ("Mossminds","0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a",131810000),
    ("AetherCore","0xe460d44d4A5eb9BEF848C0815d689827f6890D59",131810000),
    ("EmberByte","0xeC8A897a0De48a6fbfb83646f790581a2280aDB3",131810000),
]:
    try:
        b, n, calls, minters, lastb = first_mint(addr, fb)
        ts = block_ts(b) if b else None
        print(f"{label}: firstBlock={b} logsInRange={n} minters={minters} lastBlock={lastb} ankrCalls={calls} ts={ts}", flush=True)
        out[label]={'firstBlock':b,'logsInRange':n,'minters':minters,'lastBlock':lastb,'ankrCalls':calls,'firstMintTs':ts,'fromBlock':fb}
    except Exception as e:
        print(f"{label}: ERROR {e}", flush=True)
        out[label]={'error':str(e)}
json.dump(out, open('run-2026-11-05-1931-firstmints.json','w'), indent=1)
print('saved run-2026-11-05-1931-firstmints.json', flush=True)
