import json, urllib.request, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
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
def first_mint(addr):
    # chunked getLogs from 131755000 (before gap) to 131769375, Transfer from zero, 4 topics
    lo, hi = 131755000, 131769375
    first=None
    while lo<=hi:
        end=min(lo+1999, hi)
        try:
            logs=ankr_post("ankr_getLogs", [{"fromBlock":hex(lo),"toBlock":hex(end),"address":addr,"topics":[TRANSFER, ZERO]}])
            logs=logs.get("result",[]) if isinstance(logs,dict) else logs
            for lg in logs:
                if len(lg.get("topics",[]))==4:
                    b=int(lg["blockNumber"],16)
                    if first is None or b<first[0]: first=(b, lg["transactionHash"])
            if first and first[0]<=lo+1999: pass
        except Exception as e:
            print("LOGS-ERR",addr,lo,end,str(e)[:100])
        lo=end+1
        if first and first[0]<lo-2000: break
    return first
res={}
for name,addr in [("Smeltbots","0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e"),("Tumblebots","0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17")]:
    d={}
    for fn in ["name()","symbol()","totalSupply()","freeMinted()","paidMinted()","FREE_CAP()","MAX_SUPPLY()","claimedFree(address)","canFreeMint(address)","balanceOf(address)","mintOpen()"]:
        arg=enc(USER) if "address" in fn else ""
        v=raw(addr, sel(fn)+arg)
        d[fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
    fm=first_mint(addr)
    d["first_mint_block"]=fm[0] if fm else None
    d["first_mint_tx"]=fm[1] if fm else None
    if fm:
        ts=block_ts(fm[0]); d["first_mint_ts"]=ts
        import datetime; d["first_mint_wib"]=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
    res[name]=d
    print(name, json.dumps(d,indent=1))
json.dump(res, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1331-verify-new.json","w"), indent=1)
