import json, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1339"
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE="0xb21583A08581278BcF925351a99C61A4562C62f0"
TOKEN="0xc50c9b132af459Fa7b351Fd6f3AAeeFd8E9E1E96"
REG="0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data,frm=None):
    tx={"to":to,"data":data}
    if frm: tx["from"]=frm
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[tx,"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:100]}
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
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
out={"block":block()}
sale_calls=[("phase()",None),("freeClaimed()",None),("paidSold()",None),("endsAt()",None),("opensAt()",None),("FREE_CAP()",None),("freeCap()",None),("registry()",None),("hasFreeShare(address)",USER),("freeVested(address)",USER),("paidSharesOf(address)",USER),("buyCapNow()",None),("buybackRemaining()",None)]
for fn,frm in sale_calls:
    v=raw(SALE,sel(fn)+(enc(frm) if frm else "")); out["sale:"+fn]=cint(v)
tok_calls=[("name()",None),("symbol()",None),("decimals()",None),("totalSupply()",None),("balanceOf(address)",USER)]
for fn,frm in tok_calls:
    v=raw(TOKEN,sel(fn)+(enc(frm) if frm else "")); out["token:"+fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
out["registry:balanceOf(user)"]=cint(raw(REG,sel("balanceOf(address)")+enc(USER)))
# code check: sale + token have code
for rpc in RPCS:
    try:
        for label,addr in [("sale",SALE),("token",TOKEN)]:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: code=json.load(r)["result"]
            out["code:"+label]=len(code)
        break
    except Exception: continue
print(json.dumps(out,indent=1))
json.dump(out,open(f"{BASE}/hot-leg-{TS}-senbazuru-probe.json","w"),indent=1)
