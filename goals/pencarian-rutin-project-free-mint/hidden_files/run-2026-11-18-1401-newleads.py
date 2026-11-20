#!/usr/bin/env python3
"""Triage Boltbook-new 0x4158 (FIND exp43, web3shop.ai) run 1401. Read-only, chunked <=5."""
import json, subprocess
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
def get(url, timeout=25):
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),url], capture_output=True, timeout=timeout+5)
    return json.loads(r.stdout.decode())
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def post(payload, timeout=25):
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, timeout=timeout+5)
    return json.loads(r.stdout.decode())
def batch_chunked(addr, views, chunk=5):
    out={}
    for i in range(0, len(views), chunk):
        part=views[i:i+chunk]
        calls=[]
        for j,(label,sig,arg) in enumerate(part):
            data="0x"+sel(sig)
            if arg=="user": data+=enc_addr(USER)
            elif arg=="one": data+="%064x"%1
            elif arg=="user1": data+=enc_addr(USER)+"%064x"%1
            calls.append({"jsonrpc":"2.0","id":j+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        resp=post(calls)
        by={it["id"]:it for it in resp if isinstance(it,dict)} if isinstance(resp,list) else {}
        for j,(label,sig,arg) in enumerate(part):
            it=by.get(j+1,{})
            if "result" in it and it["result"] not in (None,"0x"):
                try: out[label]=int(it["result"],16)
                except Exception: out[label]=it["result"]
            elif "error" in it: out[label]="revert"
            else: out[label]=None
        print(f"  chunk {i//chunk+1} OK ({len(part)} calls)", flush=True)
    return out
ADDR="0x4158B701EaA30E8FaDBaA526F70780A38318c1C4"
try:
    meta=get(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi")
    abi=meta.get("abi") or []
    names={e["name"] for e in abi if e.get("type")=="function"}
    print("sourcify verified:", bool(abi), "verifiedAt:", meta.get("verifiedAt"), "n_fns:", len(names))
    print("fns:", sorted(names))
    shape={"verified":bool(abi),"verifiedAt":meta.get("verifiedAt"),"n_fns":len(names),
      "has_mint":any(n.lower().startswith("mint") for n in names),
      "has_quote":bool(names&{"quote","cost","getQuote","mintCost","price","getPrice"}),
      "free_views":sorted(names&{"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}),
      "agent_ref":bool(names&{"agentId","agentRegistry","agentIdRegistry","holdsAgentId","registry","getAgentId","agentGate","AgentGate","AGENT_ID_REGISTRY","hasAgentId","AGENT_ID"}),
      "is_token":bool(names&{"name","symbol","decimals","totalSupply"})}
    print("shape:", shape)
except Exception as e:
    shape={"verified":False,"error":f"{type(e).__name__}: {str(e)[:120]}"}
    print("sourcify error:", shape)
code=post([{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]}])
codelen=len(code[0].get("result","")) if isinstance(code,list) else 0
regbytes="60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code[0].get("result","").lower() if isinstance(code,list) else "")
print("codelen:",codelen,"registry_bytes:",regbytes)
VIEWS=[("totalSupply","totalSupply()",None),("totalMinted","totalMinted()",None),
 ("participants","participants()",None),("isSealed","isSealed()",None),
 ("experimentEnd","experimentEnd()",None),("experimentStart","experimentStart()",None),
 ("mintOpen","mintOpen()",None),("freeMinted","freeMinted()",None),
 ("freeClaimed","freeClaimed()",None),("freeLeft","freeLeft()",None),
 ("FREE_SUPPLY","FREE_SUPPLY()",None),("MAX_SUPPLY","MAX_SUPPLY()",None),
 ("name","name()",None),("symbol","symbol()",None),
 ("agentRegistry","agentRegistry()",None),("agentId","agentId()",None),
 ("holdsAgentId_user","holdsAgentId(address)","user"),
 ("quote_user_1","quote(address,uint256)","user1"),
 ("cost_user_1","cost(address,uint256)","user1"),
 ("balanceOf_user","balanceOf(address)","user"),
 ("mintedBy_user","mintedBy(address)","user"),
 ("freeMintedBy_user","freeMintedBy(address)","user"),
 ("price","price()",None),("PRICE","PRICE()",None),("paused","paused()",None),
 ("owner","owner()",None)]
views=batch_chunked(ADDR,VIEWS,chunk=5)
print("views:",views)
json.dump({"address":ADDR,"shape":shape,"codelen":codelen,"registry_bytes":regbytes,"views":views},
          open(f"{HF}/run-2026-11-18-1401-newleads.json","w"), indent=1)
print("saved run-2026-11-18-1401-newleads.json")
