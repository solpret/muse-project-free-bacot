import json, sys, time, subprocess, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch, _single as single
from Crypto.Hash import keccak
from ankr import ankr_post
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
REG="0x60b9262456de011f7d15a54cdd8c48baa8b022f"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(addr, sig, arg=False, raw=False):
    data=sel(sig)+(enc(USER) if arg else "")
    for ep in EPS:
        try:
            r=single(ep, "eth_call", [{"to":addr,"data":data},"latest"], 8, retries=0)
            if r is None or r=="0x": return None
            if raw: return r
            return int(r,16)
        except Exception:
            continue
    return {"error":"all-eps-fail"}
def dec_str(h):
    try:
        b=bytes.fromhex(h[2:])
        ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode()
    except Exception: return None
def dec_addr(h):
    try: return "0x"+h[-40:]
    except Exception: return None
def head_block():
    for ep in EPS:
        try: return int(batch([("eth_blockNumber",[])], endpoint=ep, timeout=10)[0],16)
        except Exception: pass
    return None
def block_ts(fb):
    for ep in EPS:
        try:
            b=batch([("eth_getBlockByNumber",[hex(fb), False])], endpoint=ep, timeout=10)
            ts=int(b[0]["timestamp"],16)
            return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
        except Exception: pass
    return None
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
TOPIC0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def logs(addr, frm, to):
    body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":addr,"topics":[TOPIC0, ZERO]})
    r=body.get("result",{})
    if isinstance(r,dict): return r.get("logs",[])
    return r if isinstance(r,list) else []
def first_mint(addr, head):
    # probe backwards in 100k-block windows from head
    cur_to=head
    while cur_to>131000000:
        cur_from=max(131000000, cur_to-99999)
        try:
            ls=logs(addr, cur_from, cur_to)
        except Exception as e:
            print(f"  getLogs {cur_from}-{cur_to} FAIL {str(e)[:100]}"); return None
        if ls:
            fb=int(ls[0]["blockNumber"],16)
            return {"first_block":fb,"first_time_wib":block_ts(fb),"count_in_window":len(ls),"window":[cur_from,cur_to]}
        cur_to=cur_from-1
    return {"first_block":None}
def sourcify(addr):
    try:
        p=subprocess.run(["curl","-s","--max-time","20",f"https://sourcify.dev/server/v2/contracts/56/{addr}"],capture_output=True,text=True)
        j=json.loads(p.stdout)
        if isinstance(j,dict) and j.get("stdJson"):
            return {"status":"verified","match":j.get("stdJson",{}).get("match") or j.get("creationMatch") or "?", "verifiedAt": j.get("stdJson",{}).get("verifiedAt") or j.get("verifiedAt")}
        return {"status":"not_verified","raw":str(j)[:200]}
    except Exception as e:
        return {"status":"error","raw":str(e)[:150]}
def code_has_registry(addr):
    for ep in EPS:
        try:
            c=single(ep,"eth_getCode",[addr,"latest"],8,retries=0)
            if c is None: return None
            return {"len":len(c),"registry_bytes": REG[2:].lower() in c.lower()}
        except Exception: pass
    return None

TARGETS={
 "Zigzoo":"0x09ada5a12293c30d75b97c56e34967e8a4326a3c",
 "Chromeshade":"0x5ba7355fb4001efe5232eb0286e11fd81eee99a4",
 "Ninetailix":"0x809215729bcbff2ef31dea5efd6c12a6b788ba9a",
 "NovaAgent":"0xa6909af663637cd988e712efbc2e73f7076d9154",
}
VIEWS=["totalSupply()","totalMinted()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","mintPrice()","balanceOf(address)","freeClaimed(address)","isFree()","freeMinted(address)","mintedBy(address)","freeLeft()","FREE_HASH()","FREE_PER_WALLET()","freeFor(address)","freeUsed(address)","freeSupply()"]
head=head_block()
print("head:", head)
out={}
for name,addr in TARGETS.items():
    print("="*20, name, addr)
    d={"address":addr}
    for v in VIEWS:
        d[v]=call(addr, v, "(address)" in v)
    d["name"]=dec_str(call(addr,"name()",raw=True) or "")
    d["symbol"]=dec_str(call(addr,"symbol()",raw=True) or "")
    ow=call(addr,"owner()",raw=True)
    d["owner"]=dec_addr(ow) if ow else None
    d["contractURI"]=None
    cu=call(addr,"contractURI()",raw=True)
    if cu:
        try:
            b=bytes.fromhex(cu[2:]); ln=int.from_bytes(b[64:96],"big"); d["contractURI"]=b[96:96+ln].decode(errors="replace")[:500]
        except Exception as e: d["contractURI"]=f"decode-fail {str(e)[:80]}"
    d["sourcify"]=sourcify(addr)
    d["code"]=code_has_registry(addr)
    if head:
        fm=first_mint(addr, head)
        d["first_mint"]=fm
        print(" first_mint:", fm)
    print(" views:", {k:v for k,v in d.items() if k in ("totalSupply()","totalMinted()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","mintPrice()","balanceOf(address)","freeClaimed(address)","FREE_PER_WALLET()")})
    print(" name/symbol/owner:", d["name"], d["symbol"], d["owner"])
    print(" sourcify:", d["sourcify"])
    print(" code:", d["code"])
    print(" contractURI:", d["contractURI"])
    out[name]=d
json.dump(out, open("run-2026-11-08-1001-triage.json","w"), indent=1)
print("WROTE run-2026-11-08-1001-triage.json")
