import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed.bnbchain.org","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
OUT="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1031-probe.json"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
        try:
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=20) as r: out=json.load(r)
            if "error" in out: return {"error":out["error"]}
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception as e: last=e; continue
    return {"error":str(last)}
def call(to,sig,args=""): return raw(to,sel(sig)+args)
def block():
    for rpc in RPCS:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
        try:
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=20) as r: return int(json.load(r)["result"],16)
        except Exception: continue
def callstr(to,fn):
    v=raw(to,sel(fn+"()"))
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception as e: return {"decode_error":str(e)}
res={"block":block()}
DYOR="0x86956Bc830EB62110820Ae79164BeF61c7E31936"
res["DYOR"]={"totalSupply":call(DYOR,"totalSupply()"),"MAX_SUPPLY":call(DYOR,"MAX_SUPPLY()"),"mintOpen":call(DYOR,"mintOpen()"),"balanceOf_user":call(DYOR,"balanceOf(address)",enc(USER)),"freeClaimed":call(DYOR,"freeClaimed()"),"agentRegistry":raw(DYOR,sel("agentRegistry()"))}
ACOS="0x3aeda314ec05bc22e3c26a543e16df2b8cc8fe69"
res["ACOS"]={"totalSupply":call(ACOS,"totalSupply()"),"MAX_SUPPLY":call(ACOS,"MAX_SUPPLY()"),"mintOpen":call(ACOS,"mintOpen()"),"balanceOf_user":call(ACOS,"balanceOf(address)",enc(USER))}
VOLT="0xc58ecec1437777061134c1bddf0ed5ea6eafabf4"
res["AgentVOLT"]={"name":callstr(VOLT,"name"),"symbol":callstr(VOLT,"symbol"),"totalSupply":call(VOLT,"totalSupply()"),"MAX_SUPPLY":call(VOLT,"MAX_SUPPLY()"),"FREE_SUPPLY":call(VOLT,"FREE_SUPPLY()"),"freeClaimed":call(VOLT,"freeClaimed()"),"freeMinted":call(VOLT,"freeMinted()"),"mintOpen":call(VOLT,"mintOpen()"),"balanceOf_user":call(VOLT,"balanceOf(address)",enc(USER)),"mintedBy_user":call(VOLT,"mintedBy(address)",enc(USER)),"agentRegistry":raw(VOLT,sel("agentRegistry()")),"agentId":raw(VOLT,sel("agentId()"))}
KAG="0xb34105002b19ef0ce43b59011fe848df5c8b174f"
res["KAGENT"]={"name":callstr(KAG,"name"),"symbol":callstr(KAG,"symbol"),"totalSupply":call(KAG,"totalSupply()"),"freeClaimed":call(KAG,"freeClaimed()"),"freeClaimed_user":call(KAG,"freeClaimed(address)",enc(KAG) and enc(USER)),"balanceOf_user":call(KAG,"balanceOf(address)",enc(USER)),"agentRegistry":raw(KAG,sel("agentRegistry()"))}
print(json.dumps(res,indent=1))
with open(OUT,"w") as f: json.dump(res,f,indent=1)
