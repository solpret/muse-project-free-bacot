#!/usr/bin/env python3
"""Leg 3 verify for 0x921150815bF267a17bb372E44e6e3f44a05f54af (S1, verified 09:55 WIB)."""
import json, urllib.request, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0x921150815bF267a17bb372E44e6e3f44a05f54af"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
DL=time.time()+60
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def encu(n): return format(n,"064x")
def call(sig,args=""):
    data=sel(sig)+args
    for rpc in RPCS:
        if time.time()>DL: return "deadline"
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=5) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            return v
        except Exception: continue
    return None
def uint(v):
    if v is None or v=="deadline": return v
    try: return int(v,16)
    except Exception: return v
def string(v):
    if not v or v=="deadline": return v
    try:
        b=bytes.fromhex(v[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode()
    except Exception: return v
out={}
for name,sig,args,conv in [
 ("name","name()","",string),("symbol","symbol()","",string),
 ("MAX_SUPPLY","MAX_SUPPLY()","",uint),("totalMinted","totalMinted()","",uint),
 ("CLAIM_AMOUNT","CLAIM_AMOUNT()","",uint),("BASE_PRICE","BASE_PRICE()","",uint),
 ("MAX_PRICE","MAX_PRICE()","",uint),("mintOpen","mintOpen()","",uint),
 ("freeUsed_user","freeUsed(address)",enc(USER),uint),
 ("costFor_1","costFor(uint256)",encu(1),uint),
 ("agentIdRegistry","agentIdRegistry()","",lambda v: "0x"+v[-40:] if v and v!="deadline" else v),
 ("ctToken","ctToken()","",lambda v: "0x"+v[-40:] if v and v!="deadline" else v),
 ("treasury","treasury()","",lambda v: "0x"+v[-40:] if v and v!="deadline" else v),
 ("owner","owner()","",lambda v: "0x"+v[-40:] if v and v!="deadline" else v),
 ("balanceOf_user","balanceOf(address)",enc(USER),uint),
 ("priceAt_1","priceAt(uint256)",encu(1),uint),
]:
    out[name]=conv(call(sig,args))
    print(name, out[name], flush=True)
# block + first-mint search via eth_getLogs (Transfer from 0x0), recent 20000 blocks
blk=None
for rpc in RPCS:
    try:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
        req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=5) as r: blk=int(json.load(r)["result"],16); break
    except Exception: continue
out["block"]=blk
print("BLOCK",blk,flush=True)
if blk:
    tfr="0x"+keccak.new(digest_bits=256,data=b"Transfer(address,address,uint256)").hexdigest()
    zero="0x"+"0"*64
    logs=None
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":hex(blk-20000),"toBlock":"latest","address":ADDR,"topics":[tfr,zero]}]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: logs=json.load(r).get("result"); break
        except Exception as e:
            print("logs fail",rpc,repr(e),flush=True); continue
    if logs is not None:
        out["first_mint_logs"]=len(logs)
        print("FIRST-MINT LOGS (last 20000 blocks):",len(logs),flush=True)
        if logs:
            first=logs[0]; out["first_mint_block"]=int(first["blockNumber"],16); out["first_mint_tx"]=first["transactionHash"]
            print("FIRST MINT block",out["first_mint_block"],"tx",out["first_mint_tx"],flush=True)
            # get block timestamp
            for rpc in RPCS:
                try:
                    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[first["blockNumber"],False]}).encode()
                    req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
                    with urllib.request.urlopen(req,timeout=5) as r: b=json.load(r)["result"]
                    out["first_mint_time_utc"]=int(b["timestamp"],16)
                    print("FIRST MINT time UTC",out["first_mint_time_utc"],flush=True); break
                except Exception: continue
json.dump(out,open(f"{BASE}/run-2026-11-06-0954-9211-verify.json","w"),indent=1)
print("DONE")
