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
FEED=['0x1B72ceC52A74537b06F713FCebA0e491f53679aE', '0xB65bD00E1d1cb6B9A7194A54F1f98E8305a28e65', '0x02899FBAE7D2ACCd6afA3fd7659c38eE4568c577', '0x78A09325DcB8d8fF7082D8dce1dBBeED06334059', '0x18042D2E0bFd11fc2cc8ee1E59a6601e530C3dF5', '0x410305316a954977D81674BaEc3f7987f6b6a2d3', '0x21B3ea5D24752B3eF51c29A473678097Fa6dA7b8', '0x8F7Ef1CF7e455fE707E5b63B4DD625C942648c9e', '0x21E80873ffd0d140d3F9C8d69829A3D3f001d388', '0x9536d1454D8a6605676DDE448A65d925c573B860', '0x4F975cEb4d012a8Da443F79dc7aB96C01429391F', '0x7eF0e92e7be5b5Db4217F4072dC06C9086F6267a', '0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688', '0xe411E1062a2292A6BDC4FD0AA11c17feb9B80C99', '0xD430dfE66A912A61ee5f1E367Aaff034dC118DEd', '0x99537479B01f17D8571d15b4Ee0424bB4064850a', '0x7124D4b3b198B8ACb7c5764EE7A8cd53830390BE', '0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90', '0xB2060E73F3Bf14e5D8425731e810f85C76958806', '0x4cf24f2E88BD7281ceDCa35e2C6DD0720E9cDC12']
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1249-sourcify-shape.json","w"),indent=1)
