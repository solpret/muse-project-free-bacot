#!/usr/bin/env python3
"""Verify Boltbook 09:31-run leads on-chain + Sourcify ABI. Read-only."""
import json, subprocess, concurrent.futures, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0),None
        except Exception as e: err=f"{type(e).__name__}:{str(e)[:120]}"
    return None,err
def code(to):
    for ep in EPS:
        try: return _single(ep,"eth_getCode",[to,"latest"],8,retries=0),None
        except Exception as e: err=str(e)[:120]
    return None,err
TESTS=[("totalSupply()",""),("totalMinted()",""),("freeClaimed()",""),("freeMinted()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("freeLeft()",""),("freeRemaining()",""),("mintOpen()",""),("mintedBy(address)",enc(USER)),("freeUsed(address)",enc(USER)),("freeClaimed(address)",enc(USER)),("balanceOf(address)",enc(USER)),("owner()",""),("name()",""),("symbol()",""),("opened()",""),("poolOpen()",""),("mintingOpen()",""),("FREE_CAP()",""),("freeSharesLeft()",""),("sharesSold()",""),("sharesMinted()","")]
TARGETS={
 "TRACE":"0xe5E2c43746F3A5E713C246592095D7cf82E808Cc",
 "CastDeep":"0x37f8f181ab2f2b2D4209AA9c77c34d8E8566C360",
 "SYMBOL":"0x993C822E7d9bBC75aa6b5095bD90a011Ff38cF71",
 "Zorith":"0x3e31b2718f64e131265dc6ba84fdafa65438ae45",
 "Pelora":"0xfaedb8533073ca2712af208bc56509726646529c",
 "BNBbaby-browser":"0xBB7eD59ca41eA03cf20084a9c6de94244B7B2637",
 "BNBbaby-snapshot":"0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637",
 "DPEG-mint":"0xEc77268Fbb7e8b62D1dE8b913440d301c7B8CF55",
 "Unbroken":"0x4443EA727b0761De5ff91Ac5E9F5F65C5E3C8b8c",
}
def work(item):
    n,a=item; out={"address":a}
    c,err=code(a); out["has_code"]=bool(c and c!="0x"); out["code_err"]=err
    for name,arg in TESTS:
        v,e=call(a,sel(name)+arg)
        try: iv=int(v,16) if v else None
        except Exception: iv=None
        # name()/symbol() are strings; keep raw
        out[name]=iv if name not in ("name()","symbol()") else v
        if name=="owner()" and v and len(v)>=42: out["owner_addr"]="0x"+v[-40:]
    r=subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],capture_output=True,text=True).stdout
    try: abi=json.loads(r).get("abi",[]) if r.startswith("{") else []
    except Exception: abi=[]
    fns=sorted({f.get("name") for f in abi if f.get("type")=="function"})
    txt=json.dumps(abi).lower()
    out["sourcify_fns"]=fns
    out["sourcify_agent"]=("60b9262456de011f7d15a54cdd8c48baaa8b022f" in txt) or any(f in fns for f in ["agentGate","agentId","agentRegistry","isAgent","AGENT_ID","hasAgentId"])
    out["sourcify_verified"]=bool(abi)
    return n,out
res={}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for n,o in ex.map(work,TARGETS.items()): res[n]=o
json.dump(res,open(BASE+"run-2026-11-03-0931-boltbook-verify.json","w"),indent=1)
for n,o in res.items():
    ints={k:v for k,v in o.items() if isinstance(v,int)}
    print(n, o["address"], "code:",o["has_code"], ints, "owner:",o.get("owner_addr"), "agent:",o["sourcify_agent"], "verified:",o["sourcify_verified"])
    print("   fns:", o["sourcify_fns"])
