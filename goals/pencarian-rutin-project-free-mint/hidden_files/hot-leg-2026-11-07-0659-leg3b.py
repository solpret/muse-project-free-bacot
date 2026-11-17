#!/usr/bin/env python3
"""Hot-leg 06:59 run - retry Mempool first-mint (chunked getLogs, recent first) + contractURI + Sourcify metadata."""
import json, urllib.request, datetime, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0xd3bE54Ae65F837d0646709fFBc2A5eFB0b034846"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed.binance.org","https://rpc.ankr.com/bsc","https://bsc.publicnode.com"]
TOPIC0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
def post(rpc, method, params, timeout=25):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
out={"block":132102253}
# current block fresh
for rpc in RPCS:
    try:
        o=post(rpc,"eth_blockNumber",[],timeout=6); out["block"]=int(o["result"],16); break
    except Exception: continue
cur=out["block"]
print("current block:",cur)
fm={}; found=None
# chunks of 10000 blocks backwards from current, max 6 chunks (~60k blocks ~ 3h)
for i in range(6):
    hi=cur - i*10000
    lo=hi - 9999
    got=False
    for rpc in RPCS:
        try:
            o=post(rpc,"eth_getLogs",[{"fromBlock":hex(lo),"toBlock":hex(hi),"address":ADDR,"topics":[TOPIC0,ZERO]}],timeout=25)
            if "error" in o:
                fm.setdefault("chunk_errors",[]).append(f"{lo}-{hi} {rpc}: {o['error'].get('message','?')[:80]}"); continue
            logs=o.get("result",[])
            fm[f"chunk_{lo}_{hi}"]=len(logs)
            if logs:
                first=logs[0]; blk=int(first["blockNumber"],16)
                ts=post(rpc,"eth_getBlockByNumber",[first["blockNumber"],False],timeout=10).get("result",{}).get("timestamp")
                ts=int(ts,16) if ts else None
                wib=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
                found={"first_mint_block":blk,"ts":ts,"wib":wib,"tx":first["transactionHash"],"logs_in_chunk":len(logs),"via":rpc}
                got=True
            break
        except Exception as e:
            fm.setdefault("chunk_errors",[]).append(f"{lo}-{hi} {rpc}: {type(e).__name__}")
    if got: break
fm["found"]=found
out["first_mint"]=fm
# contractURI retry (single call, dataseed1 first)
def raw(data,timeout=8):
    for rpc in RPCS:
        try:
            o=post(rpc,"eth_call",[{"to":ADDR,"data":data},"latest"],timeout=timeout)
            if "error" in o: continue
            v=o.get("result")
            if not v or v=="0x": return None
            return v
        except Exception: continue
    return "deadline"
v=raw(sel("contractURI()"))
if v and v!="deadline":
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],"big"); out["contractURI"]=b[64:64+ln].decode("utf-8","replace")
    except Exception as e: out["contractURI"]=f"decode-err {e}"
else:
    out["contractURI"]=v
# Sourcify metadata via curl (fields=metadata)
try:
    p=subprocess.run(["curl","-s","-m","20",f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=metadata"],capture_output=True,timeout=25)
    md=json.loads(p.stdout.decode("utf-8","ignore"))
    out["sourcify_metadata"]=md.get("metadata") or md
    print("metadata keys:", list((md.get("metadata") or {}).keys()))
except Exception as e:
    out["sourcify_metadata_error"]=str(e)
json.dump(out,open(f"{BASE}/hot-leg-2026-11-07-0659-leg3b.json","w"),indent=1)
print(json.dumps(out,indent=1)[:3000])
