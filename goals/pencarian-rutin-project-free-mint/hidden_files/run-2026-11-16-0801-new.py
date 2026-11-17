#!/usr/bin/env python3
"""Verify 2 new Boltbook contracts run 2026-11-16 08:01 WIB (read-only).
JADE 0x1b88 (YuTu Agents) + NURU 0x9d7f. Sourcify ABI/bytecode + eth_call batch via bsc-dataseed."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"): d += enc_u(int(a, 16))
        else: d += enc_u(int(a))
    return d
def post(ep, payload, timeout=60):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+10).stdout
    return json.loads(out)
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ITEMS = {
 "JADE": ("0x1b8894391a3dcfe7e248c321103265ab52e273e0", [
    ("totalSupply","totalSupply()",""),("totalMinted","totalMinted()",""),
    ("freeMinted","freeMinted()",""),("freeClaimed","freeClaimed()",""),
    ("FREE_SUPPLY","FREE_SUPPLY()",""),("FREE_CAP","FREE_CAP()",""),("FREE_MAX","FREE_MAX()",""),
    ("MAX_SUPPLY","MAX_SUPPLY()",""),("mintOpen","mintOpen()",""),
    ("mintStart","mintStart()",""),("START_TIME","START_TIME()",""),("startTime","startTime()",""),
    ("saleActive","saleActive()",""),("contractURI","contractURI()",""),
    ("tokenURI_1","tokenURI(uint256)","1"),("owner","owner()",""),
    ("mintedBy_user","mintedBy(address)",USER),("balanceOf_user","balanceOf(address)",USER),
    ("freeClaimed_user","freeClaimed(address)",USER),("mintPriceFor_user_1","mintPriceFor(address,uint256)",USER+",1"),
 ]),
 "NURU": ("0x9d7ffe074fb139cad8e69190fd2d1da19540cff7", [
    ("totalSupply","totalSupply()",""),("totalMinted","totalMinted()",""),
    ("freeMinted","freeMinted()",""),("freeClaimed","freeClaimed()",""),
    ("FREE_SUPPLY","FREE_SUPPLY()",""),("PAID_SUPPLY","PAID_SUPPLY()",""),
    ("paidMinted","paidMinted()",""),("PAID_PRICE","PAID_PRICE()",""),
    ("MAX_SUPPLY","MAX_SUPPLY()",""),("mintOpen","mintOpen()",""),
    ("mintStart","mintStart()",""),("contractURI","contractURI()",""),
    ("owner","owner()",""),("balanceOf_user","balanceOf(address)",USER),
 ]),
}
out = {}
for name,(addr,views) in ITEMS.items():
    calls=[]; meta=[]
    for key,sig,arg in views:
        args=[]
        if arg:
            for p in arg.split(","):
                p=p.strip()
                args.append(p if p.startswith("0x") else int(p))
        calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call",
                      "params":[{"to":addr,"data":build(sig,args)},"latest"]})
        meta.append(key)
    res=None; ep_used=None
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=60)
            if isinstance(r,list) and len(r)==len(calls): res=r; ep_used=ep; break
        except Exception as e: print(name,"ep fail",ep,str(e)[:80]); continue
    vals={}
    if res:
        for it,key in zip(res,meta):
            if isinstance(it,dict) and "error" not in it and it.get("result") not in (None,"0x"):
                rr=it["result"]
                vals[key]= to_int(rr[:66]) if len(rr)>=66 and rr[:66]!='0x'+'0'*64 or True else rr
                # keep raw for strings
                if len(rr)>66: vals[key+"_raw"]=rr
                else: vals[key]=to_int(rr)
            else: vals[key]=None
    out[name]={"address":addr,"views":vals,"ep":ep_used}
    print(name, json.dumps(vals))
# block + Sourcify
blk=None
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=30)
        if isinstance(r,dict) and r.get("result"): blk=int(r["result"],16); break
    except Exception: continue
out["block"]=blk
REG="60b9262456de011f7d15a54cdd8c48baa8b022f"
for name in ("JADE","NURU"):
    addr=ITEMS[name][0]
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,creationMatch,runtimeMatch", headers={"User-Agent":"free-mint-search/0801"})
        with urllib.request.urlopen(req, timeout=30) as r: meta=json.loads(r.read().decode())
        abi=meta.get("abi",[])
        names={e["name"] for e in abi if e.get("type")=="function"}
        out[name]["sourcify"]={"creationMatch":meta.get("creationMatch"),"runtimeMatch":meta.get("runtimeMatch"),
            "n_fns":len(names),
            "agent_ref":sorted(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","hasAgentId","holdsAgentId"}),
            "free_views":sorted(names & {"freeMinted","freeClaimed","freeRemaining","freeLeft","freeSupply","freeFor","freeUsed","freeAvailable","freeSharesRemaining"}),
            "mint_fns":sorted(n for n in names if n.lower().startswith("mint")),
            "all_names":sorted(names)}
        print(name,"sourcify:",json.dumps(out[name]["sourcify"])[:600])
    except Exception as e:
        out[name]["sourcify"]={"error":f"{type(e).__name__}: {str(e)[:150]}"}
        print(name,"sourcify ERROR",out[name]["sourcify"])
    try:
        r=post(EPS[0],{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]},timeout=30)
        code=r.get("result","") if isinstance(r,dict) else ""
        out[name]["bytecode_len"]=len(code)//2-1 if code.startswith("0x") else None
        out[name]["registry_bytes"]=REG in code.lower()
        print(name,"bytecode_len",out[name]["bytecode_len"],"registry_bytes",out[name]["registry_bytes"])
    except Exception as e:
        out[name]["bytecode_len"]=None; out[name]["registry_bytes"]=None
        print(name,"code ERROR",str(e)[:100])
json.dump(out, open(BASE+"run-2026-11-16-0801-new.json","w"), indent=1)
print("BLOCK", blk)
