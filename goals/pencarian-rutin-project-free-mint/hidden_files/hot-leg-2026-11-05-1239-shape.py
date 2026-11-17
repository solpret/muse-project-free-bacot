import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:60]}
            return out["result"]
        except Exception: continue
    return {"error":"rpc-fail"}
def cint(v):
    if isinstance(v,dict): return v
    try: return int(v,16) if v and v!="0x" else 0
    except Exception: return v
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
FEED=['0x6C09a253EAcE1Af2019C83eF41FE752b9613b6AF','0x481f5963bf10CbA972d52F138740155B2cda7059','0x7EDafd03507A0a97E6c4FD149aee541a9aFB8908','0x4104849762331e454673b7eAe2da517cf88D0829']
VIEWS=["name()","symbol()","decimals()","totalSupply()","freeMinted()","FREE_SLOTS()","FREE_SUPPLY()","FREE_AMOUNT()","freeSharesRemaining()","agentRegistry()"]
jobs=[]
for a in FEED:
    for fn in VIEWS: jobs.append((a,fn,None))
    jobs.append((a,"freeClaimed(address)",USER))
def run(item):
    a,fn,frm=item
    v=raw(a, sel(fn)+(enc(frm) if frm else ""))
    if fn in ("name()","symbol()"): return (a,fn,cstr(v))
    return (a,fn,cint(v))
out={}
with ThreadPoolExecutor(max_workers=12) as ex:
    for a,fn,v in ex.map(run,jobs): out.setdefault(a,{})[fn]=v
print(json.dumps(out,indent=1))
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1239-sourcify-shape.json","w"),indent=1)
