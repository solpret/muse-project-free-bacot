#!/usr/bin/env python3
"""Triage2 run 1001: full ABI + MAX_SUPPLY/free views + true first-mint via wide
Ankr getLogs (address-filtered Transfer-from-zero) for CantonTron + Qilinara."""
import json, urllib.request, time, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-1001"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def raw(to,data,timeout=8):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return None
def call(to,sig,args=""): return raw(to,sel(sig)+args)
def block_ts(blk):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=8) as r: out=json.load(r)
            return int(out["result"]["timestamp"],16)
        except Exception: continue
    return None
def wib(ts):
    return datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None

out={}
for addr in ["0x921150815bF267a17bb372E44e6e3f44a05f54af","0x46d0eE06a3b919091B006D7818C3Ae405E0f3774"]:
    d={}
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=10) as r: j=json.loads(r.read().decode())
        abi=j.get("abi"); d["verifiedAt"]=j.get("verifiedAt")
        funcs=[it.get("name","") for it in abi if isinstance(it,dict) and it.get("type")=="function"]
        d["all_funcs"]=funcs
    except Exception as e:
        d["all_funcs"]=f"ERR:{e}"; abi=None
    # extra views from ABI
    for sig in ["MAX_SUPPLY()","maxSupply()","totalPaid()","freeSupply()","freeMintedBy(address)","totalSupply()","totalMinted()","freeClaimed()","PRICE()","price()","costOf(address,uint256)"]:
        key=sig.split("(")[0]
        try:
            if "address" in sig and "uint256" in sig: v=call(addr,sig,enc(USER)+enc_uint(1)); key+="_user_1"
            elif "address" in sig: v=call(addr,sig,enc(USER)); key+="_user"
            else: v=call(addr,sig)
        except Exception as e: v=f"ERR:{e}"
        d[key]=v
    # wide first-mint check: Transfer-from-zero, address-filtered, 131900000..latest, chunked 2000
    TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ZERO="0x"+"00"*32
    logs=[]; errs=[]
    fb=131900000
    head=None
    try:
        body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(fb),"toBlock":"latest","pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr.lower()},timeout=60)
        logs=body.get("result",{}).get("logs",[]) if isinstance(body,dict) else []
        print(addr,"wide getLogs single call:",len(logs),"logs",flush=True)
    except Exception as e:
        errs.append(f"single-call:{e}"); print(addr,"wide single call FAILED",repr(e),flush=True)
        # chunked fallback 2000-block chunks from 131900000
        import subprocess
        cur=fb
        # get head first via dataseed
        try:
            body2=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req2=urllib.request.Request(RPCS[0],data=body2,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req2,timeout=8) as r: head=int(json.load(r)["result"],16)
        except Exception: head=None
        if head:
            while cur<=head:
                to=min(cur+1999,head)
                try:
                    b=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(cur),"toBlock":hex(to),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr.lower()},timeout=30)
                    logs+=b.get("result",{}).get("logs",[]) if isinstance(b,dict) else []
                except Exception as e2:
                    errs.append(f"chunk {cur}-{to}:{e2}")
                cur=to+1
            print(addr,"chunked fallback total logs:",len(logs),flush=True)
    d["wide_logs_count"]=len(logs); d["wide_errors"]=errs
    if logs:
        first=min(int(l["blockNumber"],16) for l in logs)
        d["first_mint_block"]=first
        d["first_mint_ts"]=block_ts(first)
        d["first_mint_wib"]=wib(d["first_mint_ts"])
        d["distinct_minters_wide"]=len({l["topics"][2][-40:] for l in logs if len(l.get("topics",[]))>=3})
    print(addr,"first_mint:",d.get("first_mint_block"),d.get("first_mint_wib"),"logs:",len(logs),"MAX_SUPPLY:",d.get("MAX_SUPPLY"),"totalMinted:",d.get("totalMinted"),"totalSupply:",d.get("totalSupply"),"freeClaimed:",d.get("freeClaimed"),flush=True)
    out[addr]=d
json.dump(out,open(f"{BASE}/run-{TS}-triage2.json","w"),indent=1)
print("TRIAGE2 DONE")
