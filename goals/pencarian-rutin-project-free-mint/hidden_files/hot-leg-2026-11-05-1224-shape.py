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
FEED=['0x924B1c9203EBC3EE3D4Fd2Af758B2DBDD3856e0c','0xD47D8b62A8eB1DdA2B9435fc66B9b84d2b59A797','0x57dEdd1458c5e4832719C9f2f92b3149Bf4Ce6D3','0xD0859Be3d417141767Ec553d172c3F926f5C69E3','0xf5b0c90733b5f787255Cd09D4D2e601bBEa55a7f','0x582008301173905BF49CAdB6565A2Bd6ABfAf347','0xe4e4681f962557D428710572ff0D939c5b6cfddb','0xd24c30629fDDcFa200e8f1Bb4333Ad4079B20459','0xfb3826B1690f80a576b0d910604667958C9Cc558','0x3452E984bFBB2A24F33D633bBFfC8Abbfc3DB80B','0xfb83Bc181eE3356B403d09540b501bdc3C42c211','0x705365fE93b09F50cf0e4934B9EdfdADc340C3f8','0x596EF3AeD1cAd39E7f9310DfaA9d8f3E1214a46F','0x5f6d582EBc7E0854009fA670ADba9ECE2884BD09']
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1224-sourcify-shape.json","w"),indent=1)
