#!/usr/bin/env python3
"""Run 2026-11-06 1031 WIB first-mint bounds for Sushimon / CRT Codes / Shenlong.
ankr_getLogs address-filtered Transfer-from-zero, fromBlock 131060000, paginated.
Also CRT WEBSITE()/X_LINK()/TELEGRAM() string reads + Shenlong slot re-reads."""
import json, sys, time, datetime, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-1031"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def raw(to,data,timeout=8):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            return v
        except Exception: continue
    return None
def raw_int(to,data,timeout=8):
    v=raw(to,data,timeout)
    if v is None: return None
    try: return int(v,16)
    except Exception: return v
def call(to,sig,args=""): return raw_int(to,sel(sig)+args)
def decode_str(hexdata):
    if not isinstance(hexdata,str) or not hexdata.startswith("0x"): return None
    b=bytes.fromhex(hexdata[2:])
    if len(b)>=64:
        try:
            ln=int.from_bytes(b[32:64],"big")
            if 0<ln<=len(b)-64: return b[64:64+ln].decode("utf-8","replace")
        except Exception: pass
    if len(b)==32: return b.rstrip(b"\x00").decode("utf-8","replace") or None
    return None
def block_ts(blk):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=8) as r: out=json.load(r)
            return int(out["result"]["timestamp"],16)
        except Exception: continue
    return None
def wib(ts):
    return datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")

TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
TARGETS={
 "0xCCB1cc543e5ca7208770aeb67B333a8B657c9f07":("Sushimon",2662),
 "0x06CEA7974A82f8044Ed0deb667f033Ae58EaC195":("CRT Codes",3049),
 "0xd823a14507Af2507a670FaC4eD08316Db7dCA553":("Shenlong",4209),
}
latest=int(_single("https://bsc-dataseed1.bnbchain.org","eth_blockNumber",[],8,retries=0),16)
print("head",latest,flush=True)
out={"head":latest,"first_mint":{}}
for addr,(name,supply) in TARGETS.items():
    logs=[]; page_token=None; pages=0
    t0=time.time()
    while True:
        params={"blockchain":"bsc","address":addr.lower(),"fromBlock":hex(131060000),"toBlock":hex(latest),
                "pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO]}
        if page_token: params["pageToken"]=page_token
        try:
            body=ankr_post("ankr_getLogs",params,timeout=30)
        except Exception as e:
            print(name,"ankr ERR",e,flush=True); break
        res=body.get("result",{}) if isinstance(body,dict) else {}
        logs.extend(res.get("logs",[]))
        page_token=res.get("nextPageToken")
        pages+=1
        if not page_token or pages>=15: break
        time.sleep(2.2)
    first_block=min((int(l["blockNumber"],16) for l in logs),default=None)
    ts=block_ts(first_block) if first_block else None
    d={"logs":len(logs),"pages":pages,"supply_ref":supply,"first_block":first_block,
       "first_mint_wib":wib(ts) if ts else None,"elapsed":round(time.time()-t0,1),
       "complete":(len(logs)==supply)}
    if ts:
        age_h=(time.time()-ts)/3600
        d["age_hours_at_read"]=round(age_h,2)
        d["age_le_48h"]=age_h<=48
    out["first_mint"][addr]=d
    print(name,addr,"logs",len(logs),"supply",supply,"complete",d["complete"],
          "first_block",first_block,"first_mint",d["first_mint_wib"],"age_h",d.get("age_hours_at_read"),"<=48h",d.get("age_le_48h"),flush=True)

# CRT site constants
CRT="0x06CEA7974A82f8044Ed0deb667f033Ae58EaC195"
crt={}
for sig in ["WEBSITE()","X_LINK()","TELEGRAM()"]:
    v=raw(CRT,sel(sig),timeout=8)
    crt[sig]=decode_str(v) if v else None
crt["nextMintPriceWei_user"]=call(CRT,"nextMintPriceWei()")
crt["mintUnitPriceWei"]=call(CRT,"mintUnitPriceWei()")
print("CRT site consts:",crt,flush=True)
out["crt_site"]=crt
# Shenlong slot re-reads
SH="0xd823a14507Af2507a670FaC4eD08316Db7dCA553"
sh={"freeMintsLeft_user":call(SH,"freeMintsLeft(address)",enc(USER)),
    "mintedBy_user":call(SH,"mintedBy(address)",enc(USER)),
    "quote_user_1":call(SH,"quote(address,uint256)",enc(USER)+enc_uint(1)),
    "totalSupply":call(SH,"totalSupply()"),
    "mintOpen":call(SH,"mintOpen()") if True else None}
print("Shenlong re-read:",sh,flush=True)
out["shenlong_reread"]=sh
json.dump(out,open(f"{BASE}/run-{TS}-firstmint.json","w"),indent=1)
print("FIRSTMINT DONE",flush=True)
