import sys, json, urllib.request, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch, race
from Crypto.Hash import keccak
ADDR="0x77e38295603a06654a6ed3ed0849e6aa50749963"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def dec_str(hexv):
    b=bytes.fromhex(hexv[2:])
    ln=int.from_bytes(b[32:64],"big")
    return b[64:64+ln].decode(errors="replace")
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
def call(sig,args=None):
    data=sel(sig)
    if args:
        for a in args:
            data+= a[2:].lower().rjust(64,"0") if isinstance(a,str) and a.startswith("0x") else format(a,"064x")
    for ep in EPS:
        try:
            r=batch([("eth_call",[{"to":ADDR,"data":data},"latest"])],endpoint=ep,timeout=8)
            return r[0]
        except Exception:
            continue
    return None
out={}
out["name"]=dec_str(call("name()"))
out["symbol"]=dec_str(call("symbol()"))
out["tokenURI_1"]=dec_str(call("tokenURI(uint256)",[1]))[:2000]
print(json.dumps(out,indent=1))
# --- first mint via Ankr getLogs (Transfer from zero) ---
TOPIC0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
def post(rpc, method, params, timeout=30):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
fm={}
for frm in ("0x7c8c000","0x7a00000"):  # ~130.9M, then ~128.5M fallback
    try:
        o=post("https://rpc.ankr.com/bsc","eth_getLogs",
               [{"fromBlock":frm,"toBlock":"latest","address":ADDR,"topics":[TOPIC0,ZERO]}],timeout=30)
        if "error" in o:
            fm={"error":str(o["error"])[:200],"fromBlock":frm}; print("ankr error",fm); continue
        logs=o.get("result",[])
        fm={"fromBlock":frm,"logs_returned":len(logs)}
        if logs:
            first=logs[0]
            blk=int(first["blockNumber"],16)
            fm["first_mint_block"]=blk; fm["first_mint_tx"]=first["transactionHash"]
            fm["first_tokenId"]=int(first["topics"][3],16)
            # timestamp via dataseed (Ankr timestamps are fake 'now')
            blk_hex=first["blockNumber"]
            ts=None
            for ep in EPS:
                try:
                    b=post(ep,"eth_getBlockByNumber",[blk_hex,False],timeout=10)
                    ts=int(b["result"]["timestamp"],16); break
                except Exception:
                    continue
            if ts:
                wib=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7)))
                fm["first_mint_wib"]=wib.strftime("%Y-%m-%d %H:%M:%S")
                fm["first_mint_ts"]=ts
                now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
                fm["age_hours"]=round((now.timestamp()-ts)/3600,2)
            print(json.dumps(fm,indent=1)); break
        else:
            print("no logs from",frm); continue
    except Exception as e:
        fm={"error":f"{type(e).__name__}:{e}","fromBlock":frm}; print("EXC",fm); continue
json.dump({"meta":out,"firstmint":fm},open("hot-leg-2026-11-08-0544-pumpkin2.json","w"),indent=1)
