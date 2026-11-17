import json, urllib.request, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:100]}
            return out["result"]
        except Exception: continue
    return {"error":"rpc-fail"}
def cint(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try: return int(v,16)
    except Exception: return v
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
def block_ts(n):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(n),False]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            return int(out["result"]["timestamp"],16)
        except Exception: continue
    return None
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
HEAD=131773336
def first_mint(addr):
    lo, hi = 131755000, HEAD
    first=None
    while lo<=hi:
        end=min(lo+1999, hi)
        try:
            body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(end),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr}, timeout=30)
            logs=(body.get("result",{}) or {}).get("logs",[]) if isinstance(body,dict) else []
            for lg in logs:
                if len(lg.get("topics",[]))==4:
                    b=int(lg["blockNumber"],16)
                    if first is None or b<first[0]: first=(b, lg.get("transactionHash"))
        except Exception as e:
            print("LOGS-ERR",addr,lo,end,str(e)[:100]); return {"error":str(e)[:100]}
        if first is not None:
            break
        lo=end+1
    return first
def abi_of(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        return d.get("abi") or d.get("stdJson",{}).get("abi") or []
    except Exception as e: return {"error":str(e)[:80]}
CANDS=[
 ("Neurolucha","0x56eBED63452Bb02B975ceE02949DA3C02466725b"),
 ("Roguefall","0x5fe03829a2f94a8bA3906459258b1305F0e68934"),
 ("Agent Goats","0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6"),
 ("Hirelings-A","0xff61A6e13776B0823E18d960b3f9ee2C78685601"),
 ("Agent Owls","0x50B4bD215c409C975c940d5CF23B56D8F3ecfd3b"),
 ("Forklings","0xD7B3FD33e0b465B0e374906F60567D317b758FD8"),
 ("Auspibots","0x3E56Ace6760ba03F3Ff669C51bcCa662bB96f955"),
 ("Hirelings-B","0xcbE18caA6d2A8BEaC563972d7457E8Afbb0E7C4a"),
]
res={}
for name,addr in CANDS:
    d={}
    abi=abi_of(addr)
    fns=sorted({f.get("name") for f in abi if isinstance(abi,list) and f.get("type")=="function" and f.get("name")}) if isinstance(abi,list) else []
    d["abi_functions"]=fns
    d["registry_fn"]=[f for f in fns if "AGENT" in f.upper() or f in ("agentRegistry","registry")]
    for fn in ["name()","symbol()","totalSupply()","freeMinted()","paidMinted()","FREE_CAP()","FREE_SUPPLY()","MAX_SUPPLY()","claimedFree(address)","canFreeMint(address)","balanceOf(address)","mintOpen()"]:
        arg=enc(USER) if "address" in fn else ""
        v=raw(addr, sel(fn)+arg)
        d[fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
    for fn in ["owner()","AGENT_ID()","agentRegistry()"]:
        v=raw(addr, sel(fn)); d[fn]=cint(v)
    cu=raw(addr, sel("contractURI()")); d["contractURI()"]=cstr(cu)
    tu=raw(addr, sel("tokenURI(uint256)")+format(1,"064x")); d["tokenURI(1)"]=cstr(tu)
    fm=first_mint(addr)
    d["first_mint_block"]=fm[0] if fm and isinstance(fm,tuple) else None
    d["first_mint_tx"]=fm[1] if fm and isinstance(fm,tuple) else None
    if fm and isinstance(fm,tuple):
        ts=block_ts(fm[0]); d["first_mint_ts"]=ts
        d["first_mint_wib"]=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
    res[name]=d
    print(name, json.dumps(d)[:900])
json.dump(res, open(f"{BASE}/run-2026-11-05-1401-verify-new.json","w"), indent=1)
print("DONE")
