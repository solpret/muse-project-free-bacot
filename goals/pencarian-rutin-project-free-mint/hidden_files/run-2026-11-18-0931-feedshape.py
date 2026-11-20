#!/usr/bin/env python3
"""Shape-check new Sourcify top 0x6E05 (verifiedAt 2026-11-18T02:04:35Z). Read-only."""
import json, subprocess
from eth_hash.auto import keccak
ADDR="0x6E0517d503d8b876FAaD288CA0277754941c0865"
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def get(url,timeout=25):
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),url],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
meta=get(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi")
abi=meta.get("abi",[])
fns={}
for e in abi:
    if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
names=set(fns)
has_mint=any(n.lower().startswith("mint") for n in names)
has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
free_views=sorted(names & FREE_VIEWS)
agent_ref=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
is_token=bool(names & {"name","symbol","decimals","totalSupply"})
s1=has_mint and has_quote and bool(free_views) and agent_ref
mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
print("verifiedAt:",meta.get("verifiedAt"),"match:",meta.get("match"),"n_fns:",len(names))
print("S1:",s1,"S2:",s2,"has_mint:",has_mint,"has_quote:",has_quote,"free_views:",free_views,"agent_ref:",agent_ref,"is_token:",is_token)
print("FNS:",sorted(names))
# on-chain probe: code + registry bytes + totalSupply
def post(payload,timeout=25):
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),"https://bsc-dataseed.binance.org/","-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
code=post([{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]}])[0].get("result","")
print("codelen:",len(code),"registry-bytes:","60b9262456de011f7d15a54cdd8c48baa8b022f" in code.lower())
sel=keccak(b"totalSupply()")[:4].hex()
ts=post([{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":"0x"+sel},"latest"]}])
print("totalSupply:", ts[0].get("result"))
json.dump({"address":ADDR,"verifiedAt":meta.get("verifiedAt"),"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,"n_fns":len(names),"codelen":len(code),"totalSupply":ts[0].get("result")},open("run-2026-11-18-0931-feedshape.json","w"),indent=1)
