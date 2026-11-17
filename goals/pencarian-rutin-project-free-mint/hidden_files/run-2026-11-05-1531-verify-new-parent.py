import json, sys, datetime, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG="60b9262456de011f7d15a54cdd8c48baa8b022f"
def any_mint(addr, lo, hi):
    params={"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(hi),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr}
    body=ankr_post("ankr_getLogs", params, timeout=30)
    logs=(body.get("result",{}) or {}).get("logs",[]) if isinstance(body,dict) else []
    hits=[int(lg["blockNumber"],16) for lg in logs if len(lg.get("topics",[]))==4]
    return (min(hits) if hits else None), len(hits)
def first_mint(addr, lo, hi):
    m,_=any_mint(addr, lo, hi)
    if m is None: return None
    while lo < hi:
        mid=(lo+hi)//2
        mm,_=any_mint(addr, lo, mid)
        if mm is not None: hi=mid
        else: lo=mid+1
    return lo
def block_ts(n):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(n),False]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            return int(out["result"]["timestamp"],16)
        except Exception: continue
    return None
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def rpc(method, params):
    for r in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req=urllib.request.Request(r,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as resp: return json.load(resp)
        except Exception: continue
    return {"error":"rpc-fail"}
def call(to,sig,args=""):
    out=rpc("eth_call",[{"to":to,"data":sel(sig)+args},"latest"])
    if "error" in out: return {"error":str(out["error"])[:80]}
    v=out.get("result")
    if not v or v=="0x": return None
    return v
def cint(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try: return int(v,16)
    except Exception: return v
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
def head():
    out=rpc("eth_blockNumber",[])
    return int(out["result"],16)
CTS={"HashDoge":"0x870126112Ef8863F490B518E19A1c79800E6E4BB","Parking Rush Cars":"0x230F661b80DCa58B9C57b49ed0438e16640bEDb4"}
res={"head":head()}
for name,addr in CTS.items():
    d={}
    code=rpc("eth_getCode",[addr,"latest"]).get("result","")
    d["code_len"]=len(code)//2-1 if code.startswith("0x") else None
    d["registry_bytes_in_code"]=REG in code.lower()
    d["name"]=cstr(call(addr,"name()"))
    d["symbol"]=cstr(call(addr,"symbol()"))
    d["supportsInterface_ERC721"]=cint(call(addr,"supportsInterface(bytes4)","80ac58cd".ljust(64,"0")))
    d["totalSupply"]=cint(call(addr,"totalSupply()"))
    d["owner"]=call(addr,"owner()")
    if isinstance(d["owner"],str) and len(d["owner"])==66: d["owner"]="0x"+d["owner"][26:]
    d["REGISTRY"]=call(addr,"REGISTRY()")
    d["AGENT_REGISTRY"]=call(addr,"AGENT_REGISTRY()")
    d["AGENT_ID"]=call(addr,"AGENT_ID()")
    d["freeMinted"]=cint(call(addr,"freeMinted()"))
    d["freeClaimed"]=cint(call(addr,"freeClaimed()"))
    d["FREE_CAP"]=cint(call(addr,"FREE_CAP()"))
    d["FREE_SUPPLY"]=cint(call(addr,"FREE_SUPPLY()"))
    d["MAX_SUPPLY"]=cint(call(addr,"MAX_SUPPLY()"))
    d["mintOpen"]=cint(call(addr,"mintOpen()"))
    d["balanceOf_user"]=cint(call(addr,"balanceOf(address)",enc(USER)))
    d["canFreeMint_user"]=cint(call(addr,"canFreeMint(address)",enc(USER)))
    d["claimedFree_user"]=cint(call(addr,"claimedFree(address)",enc(USER)))
    d["quote_user1"]=cint(call(addr,"quote(address,uint256)",enc(USER)+"0"*63+"1"))
    fm=first_mint(addr, 131760000, res["head"])
    d["first_mint_block"]=fm
    if fm:
        ts=block_ts(fm)
        d["first_mint_ts"]=ts
        d["first_mint_wib"]=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
    res[name]=d
    print("===",name,json.dumps(d,indent=1))
json.dump(res,open(f"{BASE}/run-2026-11-05-1531-verify-new-parent.json","w"),indent=1)
