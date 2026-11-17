#!/usr/bin/env python3
"""On-chain read CAP7 + AGENT MUSE via curl JSON-RPC batch (same path as reread.py)."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def data(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=enc_u(int(a))
    return d
def dec_str(h):
    try:
        b=bytes.fromhex(h[2:]); ln=int.from_bytes(b[32:64],'big')
        return b[64:64+ln].decode('utf-8','replace')
    except Exception: return None
def dec_int(h):
    try: return int(h,16) if h and h!="0x" else None
    except Exception: return None
CAP7="0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd"
MUSE="0x779fa133848d23052B7345F63B3b2E5309cd13ed"
calls=[]; labels=[]
def add(label,to,sig,args=[]):
    labels.append(label); calls.append({"to":to,"data":data(sig,args)})
add("cap7.name",CAP7,"name()",[])
add("cap7.symbol",CAP7,"symbol()",[])
add("cap7.FREE_SHARES",CAP7,"FREE_SHARES()",[])
add("cap7.freeMinted",CAP7,"freeMinted()",[])
add("cap7.TOTAL_SHARES",CAP7,"TOTAL_SHARES()",[])
add("cap7.sharesMinted",CAP7,"sharesMinted()",[])
add("cap7.saleStart",CAP7,"saleStart()",[])
add("cap7.phase",CAP7,"phase()",[])
add("cap7.registry",CAP7,"registry()",[])
add("cap7.costOf_user_1",CAP7,"costOf(address,uint256)",[USER,1])
add("cap7.freeClaimed_user",CAP7,"freeClaimed(address)",[USER])
add("cap7.soldOut",CAP7,"soldOut()",[])
add("cap7.deadline",CAP7,"deadline()",[])
add("cap7.PAID_SHARES",CAP7,"PAID_SHARES()",[])
add("cap7.paidMinted",CAP7,"paidMinted()",[])
add("muse.seatsTaken",MUSE,"seatsTaken()",[])
add("muse.FREE_SHARES",MUSE,"FREE_SHARES()",[])
add("muse.freeClaimed_user",MUSE,"freeClaimed(address)",[USER])
add("muse.openedAt",MUSE,"openedAt()",[])
add("muse.quote_user_1",MUSE,"quote(address,uint256)",[USER,1])
add("muse.website",MUSE,"website()",[])
add("muse.x",MUSE,"x()",[])
add("muse.agentIdOf_user",MUSE,"agentIdOf(address)",[USER])
add("muse.STAGE",MUSE,"STAGE()",[])
add("muse.DOORS_OPEN",MUSE,"DOORS_OPEN()",[])
add("muse.paidSold",MUSE,"paidSold()",[])
add("muse.progress",MUSE,"progress()",[])
payload=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":c["to"],"data":c["data"]},"latest"]} for i,c in enumerate(calls)]
blk=None
for ep in EPS:
    try:
        out=subprocess.run(["curl","-sL","--max-time","120","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=130).stdout
        j=json.loads(out)
        if isinstance(j,list) and any(x.get("result") for x in j):
            blk=ep; res=j; break
    except Exception as e:
        print("ep fail",ep,e)
if blk is None:
    print("ALL ENDPOINTS FAILED"); raise SystemExit(1)
print("batch ok via",blk)
outd={}
for lab,r in zip(labels,res):
    v=r.get("result")
    if v is None: outd[lab]=None; continue
    if lab.endswith(("name","symbol","website","x")): outd[lab]=dec_str(v)
    elif lab.endswith("registry"): outd[lab]="0x"+v[-40:] if len(v)>=42 else v
    else: outd[lab]=dec_int(v)
# block number
try:
    o=subprocess.run(["curl","-sL","--max-time","30","-X","POST",blk,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],capture_output=True,text=True,timeout=40).stdout
    outd["block"]=int(json.loads(o)["result"],16)
except Exception as e:
    outd["block"]=None
json.dump(outd, open("run-2026-11-15-2301-cap7-muse.json","w"), indent=1)
print(json.dumps(outd, indent=1))
