import json, sys, datetime, urllib.request, re
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
LUCK="0xd08ef372B52C29255fEd7004f59bF41571451894"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com"]
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:60]}
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return {"error":"rpc-fail"}
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
def block_ts(n):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(n),False]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            return int(out["result"]["timestamp"],16)
        except Exception: continue
    return None
HEAD=block()
print("HEAD",HEAD)
# --- Lucky Box extra counters ---
extra={}
for fn in ["totalSupply()","openNonce()","prizeMinted()","remainderMinted()","GBOX()","ALC()","PRIZE_POOL_CAP()","USDT_MAX_WINNERS()","REMAINDER_PER_BOX()"]:
    extra[fn]=raw(LUCK,sel(fn))
print("LUCK extra",extra)
# --- first mint probe: window head-30000 .. head (~25h) ---
def any_mint(addr, lo, hi):
    params={"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(hi),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr}
    try:
        body=ankr_post("ankr_getLogs", params, timeout=30)
    except Exception as e:
        print("ankr_getLogs error",str(e)[:100]); return "ERR"
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
lo=HEAD-30000
b=first_mint(LUCK,lo,HEAD)
ts=block_ts(b) if b else None
wib=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
print("LUCK firstMint", {"block":b,"ts":ts,"wib":wib})
res={"head":HEAD,"luck_extra":extra,"luck_first_mint":{"block":b,"ts":ts,"wib":wib}}
# --- Boltbook new addresses: context + shape ---
html_en=open(f"{BASE}/hot-leg-1604-boltbook-en.html").read()
html_zh=open(f"{BASE}/hot-leg-1604-boltbook-zh.html").read()
for a in ["0x9E7Cc3E1F21AcCb89E98c78778b0eCe3B798Ec9D","0xf1addb99fc10a1b4a9ba97a8253a3c3ab8fb4a64"]:
    for lang,html in [("en",html_en),("zh",html_zh)]:
        idx=html.lower().find(a.lower())
        if idx>=0:
            ctx=re.sub(r"\s+"," ",html[max(0,idx-400):idx+400])
            print(f"BOLTBOOK {lang} {a}: ...{ctx}...")
        else:
            print(f"BOLTBOOK {lang} {a}: NOT FOUND in html")
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        abi=d.get("abi") or []
        fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
        print("SHAPE",a,"fns",fns)
        res[a]={"abi_functions":fns}
    except Exception as e:
        print("SHAPE",a,"error",str(e)[:100]); res[a]={"error":str(e)[:100]}
json.dump(res,open(f"{BASE}/run-2026-11-05-1604-luck.json","w"),indent=1)
print("DONE")
