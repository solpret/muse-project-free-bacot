#!/usr/bin/env python3
"""Run 2026-11-06 1001 WIB triage: 2 agent-shaped first-seen (CantonTron, Qilinara)
full on-chain verification + first-mint bound; 5c ERC20 shape-check (max 20 new)."""
import json, urllib.request, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-1001"
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

scan=json.load(open(f"{BASE}/onchain-scan-2026-11-06-1001.json"))
out={"scan_window":[scan["from_block"],scan["to_block"]],"first_seen_triage":{},"erc20_5c":[]}
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","freeLeft()","freeFor(address)","FREE_SUPPLY()","FREE_PER_WALLET()","mintedBy(address)","freeUsed(address)","balanceOf(address)","mintOpen()","quote(address,uint256)","owner()","name()","symbol()"]
for addr in ["0x921150815bF267a17bb372E44e6e3f44a05f54af","0x46d0eE06a3b919091B006D7818C3Ae405E0f3774"]:
    c=[x for x in scan["contracts"] if x["address"].lower()==addr.lower()][0]
    d={"scan":c}
    for sig in VIEWS:
        key=sig.split("(")[0]
        try:
            if "address" in sig and "uint256" in sig: v=call(addr,sig,enc(USER)+enc_uint(1)); key+="_user_1"
            elif "address" in sig: v=call(addr,sig,enc(USER)); key+="_user"
            else: v=call(addr,sig)
        except Exception as e: v=f"ERR:{e}"
        d[key]=v
    # owner is address type -> raw hex; decode
    # first-mint timestamp
    ts=block_ts(c["first_block"])
    d["first_mint_block_ts"]=ts
    import datetime
    if ts: d["first_mint_wib"]=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    # Sourcify ABI for agent gate
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=10) as r: abi=json.loads(r.read().decode()).get("abi")
        funcs=[it.get("name","") for it in abi if isinstance(it,dict) and it.get("type")=="function"]
        d["sourcify_funcs"]=funcs
        d["agent_gate_funcs"]=[f for f in funcs if any(g in f.lower() for g in ("agentid","agent_id","agentregistry","agent_registry","agentgate","agent_gate","hasagentid","isagent"))]
    except Exception as e:
        d["sourcify_funcs"]=f"ERR:{e}"; d["agent_gate_funcs"]=[]
    out["first_seen_triage"][addr]=d
    print(addr, {k:d[k] for k in ("totalSupply","totalMinted","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","mintOpen","quote_user_1","mintedBy_user","freeUsed_user","balanceOf_user","first_mint_wib","agent_gate_funcs")}, flush=True)

# ---- 5c: ERC20 mint_count>=10, max 20 new, skip checked ----
checked=json.load(open(f"{BASE}/track-c-scan-checked.json")) if __import__("os").path.exists(f"{BASE}/track-c-scan-checked.json") else {}
checked_l={k.lower() for k in checked}
cands=[e for e in scan["erc20_mint_contracts_list"] if e["mint_count"]>=10]
print("5c candidates mint>=10:",len(cands),flush=True)
new=[e for e in cands if e["address"].lower() not in checked_l][:20]
print("5c new to check:",len(new),[e["address"] for e in new],flush=True)
GATE_WORDS=["agentid","agent_id","agentregistry","agent_registry","agentgate","agent_gate","hasagentid","isagent"]
FREE_SHARE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeremaining","free_slots","free_supply","free_amount"]
QUOTE_FNS=["quote","quotefor","quotemint","quotemintfor","cost","costfor","getcost","price","mintprice","feefor"]
def classify(abi):
    funcs=[it.get("name","") for it in abi if isinstance(it,dict) and it.get("type")=="function"]
    mint_fns=[f for f in funcs if "mint" in f.lower()]
    quote_fns=[f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views=[f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate=[f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns=[f for f in funcs if f.lower() in ("name","symbol","decimals","totalsupply")]
    noarg_free=[f for f in funcs if f.lower() in ("mintfree","mint","claimfree")]
    s1=bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2=len(token_fns)>=3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"mint_fns":mint_fns,"quote_fns":quote_fns,"free_views":free_views,"gate_fns":gate,"token_fns":token_fns,"S1":s1,"S2":s2}
import datetime
now_wib=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
for e in new:
    a=e["address"]; r={"address":a,"mint_count":e["mint_count"],"distinct_minters":e["distinct_minters"]}
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=10) as resp: abi=json.loads(resp.read().decode()).get("abi")
        r["sourcify"]="verified"; r.update(classify(abi))
    except urllib.error.HTTPError as ex:
        r["sourcify"]="not_verified" if ex.code==404 else f"error:{ex.code}"; r["S1"]=False; r["S2"]=False
    except Exception as ex:
        r["sourcify"]=f"error:{ex}"; r["S1"]=False; r["S2"]=False
    out["erc20_5c"].append(r)
    checked[a]={"checked_wib":now_wib,"source":"scan-1001-5c","S1":r.get("S1"),"S2":r.get("S2"),"sourcify":r["sourcify"],"mint_count_window":e["mint_count"]}
    print("5c",a,"S1=",r.get("S1"),"S2=",r.get("S2"),r["sourcify"],r.get("mint_fns"),r.get("quote_fns"),r.get("free_views"),r.get("gate_fns"),flush=True)
json.dump(checked,open(f"{BASE}/track-c-scan-checked.json","w"),indent=1)
json.dump(out,open(f"{BASE}/run-{TS}-triage.json","w"),indent=1)
print("TRIAGE DONE; 5c sale shapes:",[r["address"] for r in out["erc20_5c"] if r.get("S1") or r.get("S2")])
