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
FEED=['0x9aDFb363840a36f34A5ca49DA220FD9571B6FAAC', '0x4C15490C942996D8AC3c061A324bb47Ca7244F8E', '0x89924dE9fAFc996f3B473cB6113116374a56bea2', '0xb93157Cd2e58af4C9264DEE05b91Dc3C4f92d728', '0x0cB827F0180D159736277D54300EeeeD42F2d1c9', '0x125d75e3D64ECE51832a2C2bBD2796cC2DFDe52F', '0xcd3515EAb26c0b3a395c278B0bbe941f47BF6803', '0xB089f2fC0F7f9c32D78531237c04f37803cBE0bb', '0x6fbA2AfC7e0e1a7e221c7aBD9473aa54D2fAA1B9']
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1259-sourcify-shape.json","w"),indent=1)
