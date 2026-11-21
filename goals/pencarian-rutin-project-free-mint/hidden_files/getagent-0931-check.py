#!/usr/bin/env python3
"""GETAGENT track-C verification, run 0931 2026-11-20. Read-only."""
import json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
MINT="0x233188403A5301220cc40f47446628d722e00F6c"
TOKEN="0xc83B8b406F43BB89aDd0941bAA3Cba153B5221E1"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC="https://bsc-dataseed.binance.org/"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24+a[2:].lower()
def enc(sig,arg=None):
    d="0x"+sel(sig)
    if arg=="user": d+=enc_addr(USER)
    elif arg=="one": d+="%064x"%1
    return d
# Sourcify ABI
o=subprocess.run(["curl","-sL","--max-time","25",f"https://sourcify.dev/server/v2/contract/56/{MINT}?fields=abi,creationMatch,match"],capture_output=True,text=True).stdout
try: meta=json.loads(o)
except Exception as e: meta={"error":str(e)[:100],"raw":o[:200]}
abi=meta.get("abi",[]) if isinstance(meta,dict) else []
fns={}
for e in abi:
    if e.get("type")=="function":
        fns.setdefault(e["name"],[]).append(e)
names=set(fns)
print("SOURCIFY match:", meta.get("match") if isinstance(meta,dict) else None, "| n_fns:", len(names))
print("FN NAMES:", sorted(names))
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining","freeQuotaNow"}
has_mint=any(n.lower().startswith("mint") for n in names)
has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
free_views=sorted(names & FREE_VIEWS)
agent_ref=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","hasAgentId"})
s1=has_mint and has_quote and bool(free_views) and agent_ref
is_token=bool(names & {"name","symbol","decimals","totalSupply"})
mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
print("S1:",s1,"S2:",s2,"has_mint:",has_mint,"has_quote:",has_quote,"free_views:",free_views,"agent_ref:",agent_ref,"is_token:",is_token,"mintfree:",mintfree)
# on-chain reads: use only selectors that exist in ABI where known; try common views
sigs=[("freeQuotaNow","freeQuotaNow()",None),("totalMints","totalMints()",None),("mintedCount","mintedCount()",None),
("totalMinted","totalMinted()",None),("mintCount","mintCount()",None),("price","price()",None),
("PRICE","PRICE()",None),("mintPrice","mintPrice()",None),("freeMintsLeft","freeMintsLeft()",None),
("mints_user","mints(address)","user"),("minted_user","minted(address)","user"),
("hasMintedFree_user","hasMintedFree(address)","user"),("freeClaimed_user","freeClaimed(address)","user"),
("questListed_user","questListed(address)","user"),("agentId","agentId()",None),
("agentRegistry","agentRegistry()",None),("MAX_MINTS","MAX_MINTS()",None),("maxMints","maxMints()",None),
("totalSupply_tok","totalSupply()",None)]
calls=[];labels=[]
for k,sig,arg in sigs:
    calls.append({"to":MINT,"data":enc(sig,arg)}); labels.append(k)
calls.append({"to":TOKEN,"data":enc("totalSupply()",None)}); labels.append("token_totalSupply")
payload=[{"jsonrpc":"2.0","id":j+1,"method":"eth_call","params":[{"to":c["to"],"data":c["data"]},"latest"]} for j,c in enumerate(calls)]
o=subprocess.run(["curl","-sL","--max-time","60","-X","POST",RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True)
try: resp=json.loads(o.stdout)
except Exception as e: resp=[]; print("RPC parse err:",e,o.stdout[:200])
by={it["id"]:it for it in resp if isinstance(it,dict)}
blk=subprocess.run(["curl","-sL","--max-time","20","-X","POST",RPC,"-H","Content-Type: application/json","-d",json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])],capture_output=True,text=True).stdout
try: block=int(json.loads(blk)[0]["result"],16)
except Exception: block=None
print("BLOCK:",block)
for j,k in enumerate(labels):
    it=by.get(j+1,{})
    if "result" in it and it["result"] not in (None,"0x"):
        v=it["result"]
        try: print(k,"=",int(v,16))
        except Exception: print(k,"=",v[:120])
    elif "error" in it: print(k,"= ERROR",str(it["error"])[:120])
    else: print(k,"= None")
