#!/usr/bin/env python3
"""free-mint-search run 2026-11-18 01:01 WIB - first-read/re-read of STOCK AGENT + THYRK.
STOCK AGENT: early lead reported 0031; re-read for velocity baseline + free% check.
THYRK: watchlist-only-age-unverified; re-read for state change only.
Read-only. Writes run-2026-11-18-0101-firstread.json only."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC_URL = "https://bsc-dataseed.binance.org/"
T0 = time.time()
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def encode(sig, arg):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    elif arg == "one": d += "%064x" % 1
    elif arg == "user1": d += enc_addr(USER) + "%064x" % 1
    return d
def curl_json(url, payload, timeout=25):
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),url,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, timeout=timeout+5)
    if r.returncode != 0 or not r.stdout: raise IOError(f"curl failed rc={r.returncode}")
    return json.loads(r.stdout.decode())
def rpc_batch(calls, timeout=25):
    payload=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]} for i,(to,data) in enumerate(calls)]
    resp=curl_json(RPC_URL,payload,timeout=timeout)
    if not isinstance(resp,list): raise IOError(f"non-list: {str(resp)[:200]}")
    by={it["id"]:it for it in resp if isinstance(it,dict)}
    res=[]
    for i in range(len(calls)):
        it=by.get(i+1,{})
        if "result" in it and it["result"] not in (None,"0x"):
            try: res.append(int(it["result"],16))
            except Exception: res.append(it["result"])
        elif "error" in it: res.append(f"err:{str(it['error'])[:80]}")
        else: res.append(None)
    return res
VIEWS=[("totalSupply","totalSupply()",None),("totalMinted","totalMinted()",None),
 ("freeMinted","freeMinted()",None),("freeClaimed","freeClaimed()",None),
 ("freeLeft","freeLeft()",None),("freeSupply","freeSupply()",None),
 ("FREE_SUPPLY","FREE_SUPPLY()",None),("MAX_SUPPLY","MAX_SUPPLY()",None),
 ("mintOpen","mintOpen()",None),("mintPrice","mintPrice()",None),
 ("cost_user_1","cost(address,uint256)","user1"),("quote_user_1","quote(address,uint256)","user1"),
 ("freeMintedByWallet_user","freeMintedByWallet(address)","user"),
 ("mintedCount_user","mintedCount(address)","user"),
 ("freeClaimed_user","freeClaimed(address)","user"),
 ("freeUsed_user","freeUsed(address)","user"),
 ("balanceOf_user","balanceOf(address)","user")]
targets={"STOCK AGENT":"0xba7068233da805bdebcc167be361c219002e6b7f",
         "THYRK":"0x4d90ffc3075fb8897edff6d7c6269c906664a20e"}
calls,meta=[],[]
for name,addr in targets.items():
    for label,sig,arg in VIEWS:
        calls.append((addr,encode(sig,arg))); meta.append((name,label))
res=[]
for i in range(0,len(calls),20):
    res+=rpc_batch(calls[i:i+20])
out={"run":"free-mint-search 2026-11-18 01:01 WIB first-read (STOCK AGENT + THYRK re-read)","results":{}}
for (name,label),val in zip(meta,res):
    out["results"].setdefault(name,{"address":targets[name],"views":{}})["views"][label]=val
try:
    blk=curl_json(RPC_URL,[{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])
    out["block"]=int(blk[0]["result"],16)
except Exception as e:
    out["block"]=f"error: {str(e)[:120]}"
out["elapsed_s"]=round(time.time()-T0,1)
json.dump(out,open(f"{HF}/run-2026-11-18-0101-firstread.json","w"),indent=1)
print(json.dumps(out,indent=1,default=str))
