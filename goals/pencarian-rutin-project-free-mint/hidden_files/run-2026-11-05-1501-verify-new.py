import json, sys, datetime, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1501"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def any_mint(addr, lo, hi):
    params={"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(hi),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr}
    body=ankr_post("ankr_getLogs", params, timeout=30)
    logs=(body.get("result",{}) or {}).get("logs",[]) if isinstance(body,dict) else []
    for lg in logs:
        if len(lg.get("topics",[]))==4:
            return int(lg["blockNumber"],16)
    return None
def first_mint(addr, lo, hi):
    if any_mint(addr, lo, hi) is None:
        return None
    while lo < hi:
        mid=(lo+hi)//2
        if any_mint(addr, lo, mid) is not None:
            hi=mid
        else:
            lo=mid+1
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
def enc_u(n): return format(n,"064x")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=12) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:60]}
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return {"error":"rpc-fail"}
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
def call(to,sig,args=""):
    return raw(to, sel(sig)+args)
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None

res={"block":block()}
# 1) first-mint walk-back (low bound 131760000; extend if earliest hits the bound)
for name,addr in [("Agent Coffee","0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010"),
                  ("Driftnauts","0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b")]:
    lo=131760000; hi=131780181
    b=first_mint(addr,lo,hi)
    note=""
    if b is None:
        # no mint in range: search lower window
        b2=first_mint(addr,131740000,lo-1)
        b=b2; note="found in lower window 131740000-131759999" if b2 else "NO mint found >=131740000"
    elif b<=lo+5:
        note="earliest at search low bound - may be earlier"
    ts=block_ts(b) if b else None
    wib=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
    res[name+"_firstMint"]={"block":b,"ts":ts,"wib":wib,"note":note}
    print(name,"firstMint",res[name+"_firstMint"],flush=True)

# 2) fresh free-pool reads
AC="0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010"
DR="0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b"
ac={}
for fn in ["name()","symbol()","totalSupply()","freeMinted()","freeClaimed()","FREE_CAP()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","owner()"]:
    v=call(AC,fn)
    ac[fn]=cstr(v) if fn in ("name()","symbol()") else v
ac["quote(user,1)"]=call(AC,"quote(address,uint256)",enc(USER)+enc_u(1))
ac["freeLeft(user)"]=call(AC,"freeLeft(address)",enc(USER))
ac["freeUsed(user)"]=call(AC,"freeUsed(address)",enc(USER))
ac["mintedBy(user)"]=call(AC,"mintedBy(address)",enc(USER))
ac["balanceOf(user)"]=call(AC,"balanceOf(address)",enc(USER))
ac["contractURI()"]=cstr(call(AC,"contractURI()"))
ac["AGENT_REGISTRY()"]=call(AC,"AGENT_REGISTRY()")
res["Agent Coffee_read"]=ac
print("Agent Coffee",json.dumps(ac),flush=True)
dr={}
for fn in ["name()","symbol()","totalSupply()","freeMinted()","paidMinted()","FREE_CAP()","FREE_PCT()","MAX_SUPPLY()","PAID_CAP()","owner()"]:
    v=call(DR,fn)
    dr[fn]=cstr(v) if fn in ("name()","symbol()") else v
dr["canFreeMint(user)"]=call(DR,"canFreeMint(address)",enc(USER))
dr["claimedFree(user)"]=call(DR,"claimedFree(address)",enc(USER))
dr["quote(user,1)"]=call(DR,"quote(address,uint256)",enc(USER)+enc_u(1))
dr["balanceOf(user)"]=call(DR,"balanceOf(address)",enc(USER))
dr["contractURI()"]=cstr(call(DR,"contractURI()"))
dr["REGISTRY()"]=call(DR,"REGISTRY()")
res["Driftnauts_read"]=dr
print("Driftnauts",json.dumps(dr),flush=True)
json.dump(res,open(f"{BASE}/run-{TS}-verify-new.json","w"),indent=1)
print("DONE block",res["block"])
