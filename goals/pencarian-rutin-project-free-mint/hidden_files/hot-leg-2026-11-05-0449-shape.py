import json, urllib.request
from Crypto.Hash import keccak
RPC="https://bsc-dataseed.bnbchain.org"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=20) as r: out=json.load(r)
    except Exception as e: return {"error":str(e)}
    if "error" in out: return {"error":out["error"]}
    v=out["result"]
    if not v or v=="0x": return None
    return v
def dec(v):
    if v is None or isinstance(v,dict): return v
    try: return int(v,16)
    except: return v
def txt(v):
    if v is None or isinstance(v,dict): return v
    try:
        b=bytes.fromhex(v[2:])
        # abi string: offset 32, len 32
        ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
    except Exception as e: return v
targets={
 "AgentVOLT":"0xc58ecec1437777061134c1bddf0ed5ea6eafabf4",
 "scanledger-30e7":"0x30e75a60e4511d378121dc5b1571f613bd71d848",
 "scanledger-6156":"0x6156cdd4cd89827968e65abad1f4e043086797ca",
}
res={}
for name,addr in targets.items():
    d={}
    d["name"]=txt(call(addr,sel("name()")))
    d["symbol"]=txt(call(addr,sel("symbol()")))
    d["decimals"]=dec(call(addr,sel("decimals()")))
    d["totalSupply"]=dec(call(addr,sel("totalSupply()")))
    for fn in ["freeMinted()","freeClaimed()","FREE_SLOTS()","FREE_SUPPLY()","freeSharesRemaining()","agentRegistry()","registry()"]:
        d[fn]=call(addr,sel(fn))
    res[name]=d
print(json.dumps(res,indent=1))
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0449-shape.json","w"),indent=1)
