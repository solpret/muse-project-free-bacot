#!/usr/bin/env python3
import json, urllib.request, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0xd9cc8c95da13b0600df1b3f6879a1892a0631392"
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
def dec_str(v):
    if not v or v=="deadline": return v
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],"big"); return b[64:64+ln].decode()
    except Exception: return v
def dec_addr(v):
    if not v or v=="deadline": return v
    try: return "0x"+v[-40:]
    except Exception: return v
out={}
for name,sig,args,conv in [
 ("name","name()","",dec_str),("symbol","symbol()","",dec_str),
 ("WEBSITE","WEBSITE()","",dec_str),
 ("FREE_CARDS","FREE_CARDS()","",uint),("freeMinted","freeMinted()","",uint),
 ("MAX_CARDS","MAX_CARDS()","",uint),("totalMinted","totalMinted()","",uint),
 ("paidMinted","paidMinted()","",uint),("PHASE_ONE","PHASE_ONE()","",uint),
 ("WALLET_CAP","WALLET_CAP()","",uint),("saleStart","saleStart()","",uint),
 ("TOKENS_PER_CARD","TOKENS_PER_CARD()","",uint),
 ("freeAvailable_user","freeAvailable(address)",enc(USER),uint),
 ("freeClaimed_user","freeClaimed(address)",enc(USER),uint),
 ("remainingFor_user","remainingFor(address)",enc(USER),uint),
 ("mintedBy_user","mintedBy(address)",enc(USER),uint),
 ("balanceOf_user","balanceOf(address)",enc(USER),uint),
 ("quote_1","quote(uint256)",encu(1),uint),
 ("quoteFor_user1","quoteFor(address,uint256)",enc(USER)+encu(1),uint),
 ("token","token()","",dec_addr),
 ("pair","pair()","",dec_addr),
]:
    out[name]=conv(call(sig,args)); print(name,out[name],flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-06-0954-topa-verify.json","w"),indent=1)
print("DONE")
