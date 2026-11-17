#!/usr/bin/env python3
"""Verify LIFTDAEMON 0xbd1a0bf361c6b369979028a3fa98adde3c9c4eec for run 1631. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TO="0xbd1a0bf361c6b369979028a3fa98adde3c9c4eec"
REG="60b9262456de011f7d15a54cdd8c48baa8b022f"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep,method,params,timeout=60):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json",
        "-d",json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})],
        capture_output=True,text=True,timeout=timeout+10).stdout
    try: return json.loads(out).get("result")
    except Exception: return None
def ti(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def call(to,sig,args=[]):
    d=sel(sig)
    for a in args:
        d+= a[2:].lower().rjust(64,"0") if isinstance(a,str) and a.startswith("0x") and len(a)==42 else format(int(a),"064x")
    for ep in EPS:
        r=post(ep,"eth_call",[{"to":to,"data":d},"latest"])
        if r is not None: return ti(r)
    return None
head=None
for ep in EPS:
    r=post(ep,"eth_blockNumber",[])
    if r: head=int(r,16); break
print("head:",head)
views={}
for name,sig,args in [("totalSupply","totalSupply()",[]),("firstFreeUsed","firstFreeUsed()",[]),
    ("FIRST_FREE_CAP","FIRST_FREE_CAP()",[]),("paidMinted","paidMinted()",[]),
    ("mintOpen","mintOpen()",[]),("PRICE","PRICE()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintStart","mintStart()",[]),("startTime","startTime()",[]),("START_TIME","START_TIME()",[]),
    ("windowStart","windowStart()",[]),("balanceOf_user","balanceOf(address)",[USER]),
    ("xFreeUsed","xFreeUsed()",[]),("X_FREE_CAP","X_FREE_CAP()",[])]:
    views[name]=call(TO,sig,args)
print(json.dumps(views,indent=1))
code=None
for ep in EPS:
    r=post(ep,"eth_getCode",[TO,"latest"])
    if r: code=r; break
print("codeLen:", len(code)//2-1 if code else None, "hasRegistryBytes:", (REG.lower() in (code or "").lower()))
# age probe: any Transfer-from-zero in a 1000-block window ~24h ago (192000 blocks back)?
import time
for back in (192000,):
    frm=head-back; to_b=frm+999
    print("probe window:",frm,to_b)
    for ep in ["https://bsc-rpc.publicnode.com/","https://bsc-dataseed.binance.org/"]:
        r=post(ep,"eth_getLogs",[{"fromBlock":hex(frm),"toBlock":hex(to_b),"address":TO,
            "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                      "0x0000000000000000000000000000000000000000000000000000000000000000"]}],timeout=60)
        if isinstance(r,list):
            print("  ",ep,"->",len(r),"logs")
            break
        print("  ",ep,"->",str(r)[:120])
# Sourcify verifiedAt
out=subprocess.run(["curl","-sL","--max-time","30",f"https://sourcify.dev/server/v2/contract/56/{TO}"],
    capture_output=True,text=True,timeout=40).stdout
try:
    m=json.loads(out); print("sourcify verifiedAt:",m.get("verifiedAt"),"match:",m.get("match"))
    abi=m.get("abi",[])
    names=sorted({e["name"] for e in abi if e.get("type")=="function"})
    print("fns:",names)
except Exception as e: print("sourcify err:",str(e)[:200])
json.dump({"head":head,"views":views,"codeHasRegistry": (REG.lower() in (code or "").lower())},
    open("run-2026-11-16-1631-lift.json","w"),indent=1)
