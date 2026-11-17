import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return hex(n)[2:].rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:80]}
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
def caddr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try: return "0x"+v[2:][-40:]
    except Exception: return v
WAGA="0x06a6f51D30556f4262e38485C09556fE81e6A984"
JADA="0x0Da7DB45f8C8fcDC69A2CF9c5f53619Cd7937b5E"
AGMIN="0x8670e99062ead2cE5402754aeDE769602FDf38b8"
jobs=[]
def add(a,fn,args=None,kind="int"):
    jobs.append((a,fn,args,kind))
add(WAGA,"AGENT_ID()",None,"addr"); add(WAGA,"FREE_PER_WALLET()"); add(WAGA,"MAX_MINTS()"); add(WAGA,"MAX_SUPPLY()"); add(WAGA,"MINT_AMOUNT()"); add(WAGA,"PRICE()"); add(WAGA,"quote(address,uint256)",(USER,1)); add(WAGA,"mintOpen()"); add(WAGA,"totalMints()"); add(WAGA,"mintedBy(address)",(USER,)); add(WAGA,"freeLeft(address)",(USER,))
add(JADA,"AGENT_REGISTRY()",None,"addr"); add(JADA,"WEBSITE()",None,"str"); add(JADA,"TWITTER()",None,"str"); add(JADA,"PRICE()"); add(JADA,"quote(address,uint256)",(USER,1)); add(JADA,"spotsLeft()"); add(JADA,"totalSpotsMinted()"); add(JADA,"MAX_SPOTS()"); add(JADA,"PER_SPOT()"); add(JADA,"CAP()"); add(JADA,"mintedBy(address)",(USER,)); add(JADA,"poolBalance()")
add(AGMIN,"AGENT_REGISTRY()",None,"addr"); add(AGMIN,"PRICE()"); add(AGMIN,"RIGS_PER_MINT()"); add(AGMIN,"quote(address,uint256)",(USER,1)); add(AGMIN,"mintOpen()"); add(AGMIN,"MAX_SUPPLY()"); add(AGMIN,"freeLeft(address)",(USER,)); add(AGMIN,"freeFor(address)",(USER,)); add(AGMIN,"freeUsed(address)",(USER,)); add(AGMIN,"mintedBy(address)",(USER,)); add(AGMIN,"RIGS()",None,"addr"); add(AGMIN,"soldOut()")
def run(item):
    a,fn,args,kind=item
    data=sel(fn)
    if args:
        for x in args:
            data+= enc(x) if isinstance(x,str) and x.startswith("0x") else enc_uint(x)
    v=raw(a,data)
    if kind=="str": return (a,fn,cstr(v))
    if kind=="addr": return (a,fn,caddr(v))
    return (a,fn,cint(v))
out={}
with ThreadPoolExecutor(max_workers=12) as ex:
    for a,fn,v in ex.map(run,jobs): out.setdefault(a,{})[fn]=v
print(json.dumps(out,indent=1))
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1304-probe-waga-jada-agmin.json","w"),indent=1)
