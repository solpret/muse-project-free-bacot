import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
def topic(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return '0x'+k.hexdigest()
AB='0x08393dad165d90e7258501fE1dfb5F3498644011'
FROM=131763362
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def block_ts(n):
    body=json.dumps({"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[hex(n),False],"id":1}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json"}, method='POST')
            with urllib.request.urlopen(req, timeout=10) as r:
                j=json.load(r)
            if j.get('result'): return int(j['result']['timestamp'],16)
        except Exception: pass
    return None
def getlogs(topics):
    logs=[]; page=None; calls=0
    while True:
        params={"blockchain":"bsc","fromBlock":hex(FROM),"toBlock":"latest",
                "address":AB.lower(),"topics":topics,"pageSize":1000}
        if page: params["pageToken"]=page
        body=ankr_post("ankr_getLogs", params, timeout=30); calls+=1
        res=body.get('result',{}) if isinstance(body,dict) else {}
        ls=res.get('logs',[]) or []
        logs.extend(ls)
        page=res.get('nextPageToken')
        if not page or calls>=10: break
    return logs, calls
out={}
for label,sig in [('BoxOpened','BoxOpened(address,uint256,uint32,uint256,uint256)'),
                  ('FreeBoxOpened','FreeBoxOpened(address,uint256,bytes32)'),
                  ('XBoxOpened','XBoxOpened(address,uint256,bytes32)')]:
    try:
        logs,calls=getlogs([topic(sig)])
        blocks=sorted(int(l['blockNumber'],16) for l in logs) if logs else []
        minters=len({l['topics'][1] for l in logs if len(l.get('topics',[]))>1})
        # pricePaid for BoxOpened = data word 4 (seedBlock is word3? data: boxId,configId,seedBlock,pricePaid -> words 0..3; pricePaid word 3)
        paid_zero=0; paid_nz=0
        if label=='BoxOpened':
            for l in logs:
                d=l.get('data','0x')
                try:
                    bb=bytes.fromhex(d[2:])
                    pp=int.from_bytes(bb[96:128],'big')
                    if pp==0: paid_zero+=1
                    else: paid_nz+=1
                except Exception: pass
        first_ts=block_ts(blocks[0]) if blocks else None
        print(f"{label}: logs={len(logs)} firstBlock={blocks[0] if blocks else None} lastBlock={blocks[-1] if blocks else None} minters={minters} calls={calls} firstTs={first_ts} paidZero={paid_zero} paidNz={paid_nz}",flush=True)
        out[label]={'logs':len(logs),'firstBlock':blocks[0] if blocks else None,'lastBlock':blocks[-1] if blocks else None,'minters':minters,'calls':calls,'firstTs':first_ts,'paidZero':paid_zero,'paidNz':paid_nz}
    except Exception as e:
        print(f"{label}: ERROR {e}",flush=True); out[label]={'error':str(e)}
json.dump(out,open('run-2026-11-05-2031-agentbox-firstopens.json','w'),indent=1)
print('saved')
