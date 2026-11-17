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
FEED=['0x64a5Dd4632f995180655Fbcc71625ab5A8E37308', '0xe587dC71eFdc93F454d9E992D275D32bC782f01B', '0x08E276D8B3433B750428B12dE6b1EE9b83f76940', '0x056721518206DCe5c1cED9a53ab433353f39285c', '0xE2C2440BfF6b890D81A9E3e2FA18ed92d1A390fC', '0x2F244F88566005A2E5f2e783Dae98d6BE4bDef81', '0x178E69089b574aab45a78701869872b3F4bb9691', '0x050094418be7dc8510776E882a858D9bF70dDF1e', '0xb9a89b7290224aBa18be68DC844F7E63EE29dC88', '0xfc13a1e0231cEfFcf7C06CaD8B6E4727F423354b', '0xC309a65ADDf67BfcB8576A2A37c122dF1De2DdD8', '0x9E714e00F259a41E6C2f2Fd03DEfae8f1BCb5A03', '0xfa32E87c78Ec2f81dcBAba6150967BC7cd97b6Ea']
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
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-1254-sourcify-shape.json","w"),indent=1)
