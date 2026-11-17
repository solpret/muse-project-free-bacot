#!/usr/bin/env python3
"""Hot-leg 06:59 run - Leg 3 on-chain verification of new S1 sale-shape 0xd3bE54Ae65F837d0646709fFBc2A5eFB0b034846 + first mint."""
import json, urllib.request, datetime
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0xd3bE54Ae65F837d0646709fFBc2A5eFB0b034846"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed.binance.org","https://rpc.ankr.com/bsc"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def post(rpc, method, params, timeout=20):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
def raw(to,data,timeout=8):
    for rpc in RPCS:
        try:
            o=post(rpc,"eth_call",[{"to":to,"data":data},"latest"],timeout=timeout)
            if "error" in o: continue
            v=o.get("result")
            if not v or v=="0x": return None
            return v
        except Exception: continue
    return "deadline"
def call(sig,args=""): return raw(ADDR, sel(sig)+args)
def as_int(v):
    if v is None or v=="deadline": return v
    try: return int(v,16)
    except Exception: return v
def as_str(v):
    if v is None or v=="deadline": return v
    try:
        b=bytes.fromhex(v[2:])
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode("utf-8","replace")
    except Exception as e: return f"decode-err {e}: {v[:120]}"
def as_addr(v):
    if v is None or v=="deadline": return v
    return "0x"+v[-40:]
out={}
out["block"]=None
for rpc in RPCS:
    try:
        o=post(rpc,"eth_blockNumber",[],timeout=6)
        out["block"]=int(o["result"],16); out["via"]=rpc; break
    except Exception: continue
for sig in ["totalSupply()","totalMints()","MAX_MINTS()","MAX_SUPPLY()","MINT_AMOUNT()","PRICE()","mintOpen()","FREE_PER_WALLET()","MAX_PER_WALLET()","decimals()"]:
    out[sig.split("(")[0]]=as_int(call(sig))
out["name"]=as_str(call("name()"))
out["symbol"]=as_str(call("symbol()"))
out["AGENT_ID"]=as_addr(call("AGENT_ID()"))
out["owner"]=as_addr(call("owner()"))
out["quote_user1"]=as_int(call("quote(address,uint256)",enc(USER)+enc_uint(1)))
out["freeLeft_user"]=as_int(call("freeLeft(address)",enc(USER)))
out["mintedBy_user"]=as_int(call("mintedBy(address)",enc(USER)))
out["balanceOf_user"]=as_int(call("balanceOf(address)",enc(USER)))
out["contractURI"]=as_str(call("contractURI()"))
# first mint via Transfer from zero
TOPIC0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
fm={}
for fb in ["0x7dd8a20","0x7d00000"]:
    done=False
    for rpc in RPCS:
        try:
            o=post(rpc,"eth_getLogs",[{"fromBlock":fb,"toBlock":"latest","address":ADDR,"topics":[TOPIC0,ZERO]}],timeout=30)
            if "error" in o: continue
            logs=o.get("result",[])
            fm["fromBlock"]=fb; fm["logs"]=len(logs); fm["via"]=rpc
            if logs:
                first=logs[0]
                blk=int(first["blockNumber"],16)
                ts=post(rpc,"eth_getBlockByNumber",[first["blockNumber"],False],timeout=10).get("result",{}).get("timestamp")
                ts=int(ts,16) if ts else None
                wib=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
                fm.update({"first_mint_block":blk,"ts":ts,"wib":wib,"tx":first["transactionHash"]})
                done=True
            break
        except Exception as e:
            fm.setdefault("errors",[]).append(f"{rpc}:{type(e).__name__}")
    if done: break
out["first_mint"]=fm
json.dump(out,open(f"{BASE}/hot-leg-2026-11-07-0659-leg3.json","w"),indent=1)
print(json.dumps(out,indent=1))
