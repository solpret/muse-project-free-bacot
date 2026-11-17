#!/usr/bin/env python3
"""Run 2026-11-06 1031 WIB triage: 3 agent-shaped-ish first-seen (Sushimon, CRT Codes,
Shenlong) full on-chain verification + first-mint bound; 5c ERC20 shape-check (max 20 new).
DGDreams + Catagent are NOT agent-shaped (verified this run) -> log only, no triage reads."""
import json, urllib.request, urllib.error, time, sys, datetime
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
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return None
def call(to,sig,args=""): return raw(to,sel(sig)+args)
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

scan=json.load(open(f"{BASE}/onchain-scan-2026-11-06-1031.json"))
out={"scan_window":[scan["from_block"],scan["to_block"]],"first_seen_triage":{},"erc20_5c":[]}
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","freeLeft()","freeFor(address)","FREE_SUPPLY()","FREE_PER_WALLET()","FREE_MINTS()","freeMintsLeft()","mintedBy(address)","freeUsed(address)","balanceOf(address)","mintOpen()","quote(address,uint256)","owner()","name()","symbol()","MAX_SUPPLY()","PRICE()","mintPrice()","mintUnitPriceWei()","nextMintPriceWei()"]
TARGETS={
 "0xCCB1cc543e5ca7208770aeb67B333a8B657c9f07":"Sushimon",
 "0x06CEA7974A82f8044Ed0deb667f033Ae58EaC195":"CRT Codes",
 "0xd823a14507Af2507a670FaC4eD08316Db7dCA553":"Shenlong",
}
for addr,name in TARGETS.items():
    c=[x for x in scan["contracts"] if x["address"].lower()==addr.lower()][0]
    d={"name":name,"scan":c}
    for sig in VIEWS:
        key=sig.split("(")[0]
        try:
            if "address" in sig and "uint256" in sig: v=call(addr,sig,enc(USER)+enc_uint(1)); key+="_user_1"
            elif "address" in sig: v=call(addr,sig,enc(USER)); key+="_user"
            else: v=call(addr,sig)
        except Exception as e: v=f"ERR:{e}"
        d[key]=v
    ts=block_ts(c["first_block"])
    d["window_first_block_ts"]=ts
    if ts: d["window_first_block_wib"]=wib(ts)
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=10) as r: abi=json.loads(r.read().decode()).get("abi")
        funcs=[it.get("name","") for it in abi if isinstance(it,dict) and it.get("type")=="function"]
        d["sourcify_funcs"]=funcs
        d["agent_gate_funcs"]=[f for f in funcs if any(g in f.lower() for g in ("agentid","agent_id","agentregistry","agent_registry","agentgate","agent_gate","hasagentid","isagent"))]
        d["free_funcs"]=[f for f in funcs if "free" in f.lower()]
    except Exception as e:
        d["sourcify_funcs"]=f"ERR:{e}"; d["agent_gate_funcs"]=[]
    out["first_seen_triage"][addr]=d
    print(addr, name, {k:d[k] for k in ("totalSupply","totalMinted","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","FREE_PER_WALLET","FREE_MINTS","freeMintsLeft","mintOpen","quote_user_1","mintedBy_user","freeUsed_user","balanceOf_user","MAX_SUPPLY","PRICE","mintPrice","window_first_block_wib","agent_gate_funcs","free_funcs")}, flush=True)
json.dump(out,open(f"{BASE}/run-{TS}-triage.json","w"),indent=1)
print("TRIAGE VIEWS DONE", flush=True)
