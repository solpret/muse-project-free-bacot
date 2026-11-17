import json, urllib.request, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _post as _fr_post
from ankr import ankr_post
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,'0')
def enc_u(n): return format(n,'064x')
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def single(addr, data):
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout=8, retries=0)
            if not isinstance(out,dict): continue
            if out.get("error"): return "ERR"
            r=out.get("result")
            if r is None: return None
            if r=="0x": return 0
            if r.startswith("0x") and len(r)<=66: return int(r,16)
            return r
        except Exception: continue
    return "ERR:all-fail"
def block_ts(blk):
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]}, timeout=8, retries=0)
            ts=out.get("result",{}).get("timestamp")
            if ts: return int(ts,16)
        except Exception: continue
    return None
def fmt_ts(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
def sourcify(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        d=json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e:
        return None, f"ERROR {e}"
    abi=d.get("abi")
    if not isinstance(abi,list): return None, "no-abi"
    fns=[e.get("name","") for e in abi if e.get("type")=="function"]
    return fns, "verified"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"0"*64
def walkback(addr, first_seen, label, max_chunks=80):
    hi=first_seen; found=None
    for i in range(max_chunks):
        lo=max(0, hi-999)
        try:
            res=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(hi),"address":addr,"topics":[TRANSFER,ZERO],"pageSize":1000}, timeout=55)
            logs=res.get("result",{}).get("logs",[]) if isinstance(res,dict) else []
        except Exception as e:
            print(f"{label} walkback chunk {lo}-{hi} ERROR {e}", flush=True); return None
        print(f"{label} walkback {lo}-{hi}: {len(logs)} logs", flush=True)
        if len(logs)==0: break
        found=min(int(l.get("blockNumber","0x0"),16) for l in logs)
        hi=lo-1
    if found is None: print(label, "NO from-zero logs in probed range"); return None
    ts=block_ts(found)
    print(label, "FIRST MINT block", found, fmt_ts(ts))
    return found, ts
TARGETS={
 "Dafeiyu":"0xd8de64acb25a87d98f1e170bf082a01427772511",
 "PawGang":"0x587C303982187Ec578dF309d27670327b13202F8",
 "PassAgentX":"0x08b1a979dd997492eecc010fe986ea2e2925e620",
}
for name,addr in TARGETS.items():
    print("="*20, name, addr)
    fns, st = sourcify(addr)
    print(" Sourcify:", st, "fns:", fns if fns else "")
    for v in ["totalSupply()","totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","freeClaimed()","freeMinted()","freeLeft()","mintOpen()","PRICE()","mintPrice()"]:
        print(f"  {v} = {single(addr, sel(v))}")
    print("  quote(1) =", single(addr, sel('quote(uint256)')+enc_u(1)))
    print("  freeClaimed(user) =", single(addr, sel('freeClaimed(address)')+enc_addr(USER)))
    print("  mintedBy(user) =", single(addr, sel('mintedBy(address)')+enc_addr(USER)))
    print("  freeUsed(user) =", single(addr, sel('freeUsed(address)')+enc_addr(USER)))
    print("  balanceOf(user) =", single(addr, sel('balanceOf(address)')+enc_addr(USER)))
    print("  owner =", single(addr, sel('owner()')))
    print("  contractURI =", str(single(addr, sel('contractURI()')))[:300])
walkback(TARGETS["Dafeiyu"], 132297424, "Dafeiyu")
walkback(TARGETS["PassAgentX"], 132355000, "PassAgentX")
