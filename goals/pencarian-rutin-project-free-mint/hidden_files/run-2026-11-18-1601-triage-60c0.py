#!/usr/bin/env python3
"""Triage Boltbook-new 0x60c070855ba8a99b78565669fe7962f617acbb15 + 7 new Sourcify addrs (run 1601). Read-only."""
import json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPC="https://bsc-dataseed.binance.org/"
def sel(s): return keccak(s.encode())[:4].hex()
def call(to, sig, arg=None):
    data="0x"+sel(sig)
    if arg=="user": data+="0"*24+"eb237F6f9FB4e826739F0954e9768914F28b2c2E".lower()
    elif arg=="one": data+="%064x"%1
    payload=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}]
    r=subprocess.run(["curl","-s","--max-time","25",RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=30)
    j=json.loads(r.stdout.decode())
    res=j[0].get("result") if isinstance(j,list) else j.get("result")
    if not res or res=="0x": return None
    try: return int(res,16)
    except: return res
def sourcify(addr):
    r=subprocess.run(["curl","-s","-L","--max-time","30",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"],capture_output=True,timeout=35)
    try: return json.loads(r.stdout.decode())
    except: return {"error": r.stdout.decode()[:200]}
out={}
# 0x60c0 triage
A="0x60c070855ba8a99b78565669fe7962f617acbb15"
meta=sourcify(A)
abi=meta.get("abi") or []
names={e["name"] for e in abi if e.get("type")=="function"}
out["60c0"]={"sourcify_verified": bool(abi), "n_fns": len(names), "fns": sorted(names)[:60],
 "has_mint": any("mint" in n.lower() for n in names),
 "free_views": sorted(n for n in names if "free" in n.lower()),
 "agent_ref": sorted(n for n in names if "agent" in n.lower() or "registry" in n.lower()),
 "has_quote": any(n.lower() in ("quote","cost","getquote","mintcost","price","getprice") for n in names),
 "metadata": str(meta.get("metadata"))[:300] if meta.get("metadata") else None}
views={}
for label,sig,arg in [("totalSupply","totalSupply()",None),("totalMinted","totalMinted()",None),
 ("freeMinted","freeMinted()",None),("freeClaimed","freeClaimed()",None),("freeLeft","freeLeft()",None),
 ("FREE_SUPPLY","FREE_SUPPLY()",None),("MAX_SUPPLY","MAX_SUPPLY()",None),("mintOpen","mintOpen()",None),
 ("balanceOf_user","balanceOf(address)","user"),("name","name()",None),("symbol","symbol()",None)]:
    try: views[label]=call(A,sig,arg)
    except Exception as e: views[label]=f"err:{type(e).__name__}"
out["60c0"]["views"]=views
# 7 new Sourcify addrs shape-check
FREE={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
AGENT={"agentId","agentRegistry","agentIdRegistry","holdsAgentId","registry","getAgentId","agentGate","AgentGate","AGENT_ID_REGISTRY","hasAgentId","AGENT_ID"}
QUOTE={"quote","cost","getQuote","mintCost","price","getPrice"}
for addr in ["0xE14E3247ccb686e5C7d924308B4f576B8C90D3b1","0x99aA65eF0a817dCC711388fFA1911601477AF66E","0xea3c4398dFfBbd8b2D46d5705eB9895d7b460828","0x2Da07eff97B2a52D1da171E5066AbB515e785202","0x1fed854bE873C86d25a7AF8c0B8EC38FfA247777","0x274acC953B5CC01ee381A113A521394d9ec0613f","0xadaC4C010f32703A9eF9506539F55Cf74b8318c7"]:
    m=sourcify(addr); ab=m.get("abi") or []
    ns={e["name"] for e in ab if e.get("type")=="function"}
    has_mint=any("mint" in n.lower() for n in ns)
    fv=sorted(n for n in ns if n in FREE)
    ag=sorted(n for n in ns if n in AGENT)
    q=sorted(n for n in ns if n in QUOTE)
    is_token=bool({"name","symbol","decimals","totalSupply"} & ns)
    s1=bool(has_mint and q and fv and ag)
    s2=bool(is_token and any(n in ns for n in ("mintFree","freeMint")) and fv and ag)
    out[addr]={"n_fns":len(ns),"has_mint":has_mint,"free_views":fv,"agent_ref":ag,"quote":q,"is_token":is_token,"S1":s1,"S2":s2,"verifiedAt":m.get("verifiedAt") or (m.get("metadata") or {}).get("verifiedAt") if isinstance(m.get("metadata"),dict) else None}
json.dump(out,open(f"{HF}/run-2026-11-18-1601-triage-60c0.json","w"),indent=1)
print(json.dumps(out,indent=1)[:5000])
