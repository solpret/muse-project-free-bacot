import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
def logs_for(addr, from_block):
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
    return logs, calls
# FEED-A detail: tokenIds + distinct minters
logs, calls = logs_for("0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A", 131780000)
print("FEED-A logs:", len(logs), "calls:", calls, flush=True)
tids=[int(l['topics'][3],16) if len(l.get('topics',[]))>3 else None for l in logs]
print("  tokenIds min/max:", min(t for t in tids if t is not None), max(t for t in tids if t is not None), "distinct:", len(set(tids)), flush=True)
print("  distinct to:", len(set(l['topics'][2] for l in logs)), flush=True)
print("  block range:", min(int(l['blockNumber'],16) for l in logs), max(int(l['blockNumber'],16) for l in logs), flush=True)
print("  sample topics0:", logs[0].get('topics'), "addr:", logs[0].get('address'), flush=True)
# Night Shift wide search
logs2, calls2 = logs_for("0x427aed3f7427b48e45f5e648105aa1b77724cf14", 131490000)
print("NightShift logs from 131490000:", len(logs2), "calls:", calls2, flush=True)
if logs2:
    b0=min(int(l['blockNumber'],16) for l in logs2)
    print("  earliest block in range:", b0, flush=True)
    body=json.dumps({"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[hex(b0),False],"id":1}).encode()
    req=urllib.request.Request("https://bsc-dataseed.binance.org/", data=body, headers={"Content-Type":"application/json"}, method='POST')
    with urllib.request.urlopen(req, timeout=10) as r:
        j=json.load(r)
    print("  earliest ts:", int(j['result']['timestamp'],16), flush=True)
    json.dump({'ns_firstBlock':b0,'ns_firstTs':int(j['result']['timestamp'],16),'ns_logs':len(logs2)}, open('run-2026-11-05-1901-firstmints2.json','w'))
