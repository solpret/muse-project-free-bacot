#!/usr/bin/env python3
"""Triage RAMRAIDERS 0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b — Boltbook recheck
post 2026-11-11 17:33 WIB (agata.ai): 549/7.777, mint(1) value 0, UNGATED,
Sourcify exact_match. Hot leg first saw it 00:30 WIB PRE-LAUNCH (supply 0).
Read-only; writes run-2026-11-11-1731-ramraiders.json."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR="0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT="masgayut.ai"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def dec_str(hexdata):
    try:
        b=bytes.fromhex(hexdata[2:])
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def call(to,data,timeout=25):
    payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5)
            res=json.loads(r.stdout)
            if "result" in res: return res["result"]
        except Exception: continue
    return None
def enc_dyn_string(s):
    b=s.encode(); pad=(32-len(b)%32)%32
    return (32).to_bytes(32,"big").hex()+len(b).to_bytes(32,"big").hex()+b.hex()+"00"*pad
out={"address":ADDR}
out["block"]=None
for ep in EPS:
    try:
        r=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],capture_output=True,text=True,timeout=30)
        out["block"]=int(json.loads(r.stdout)["result"],16); break
    except Exception: continue
views=["totalSupply()","totalMinted()","freeMinted()","freeUsed()","freeClaimed()","MAX_SUPPLY()","mintActive()","deckRemaining()","priceFor(address)","holdsAgentId(address)","freeUsed(address)","balanceOf(address)","name()","symbol()"]
for v in views:
    base=v.split("(")[0]
    if "(address)" in v: data=sel(v)+enc(USER); key=base+"_user"
    else: data=sel(v); key=base
    raw=call(ADDR,data)
    out[key]=to_int(raw) if base not in ("name","symbol") else dec_str(raw) if raw else None
# agentId string-arg views
out["priceFor_agentId"]=to_int(call(ADDR,sel("priceFor(string)")+enc_dyn_string(AGENT)))
out["holdsAgentId_agentId"]=to_int(call(ADDR,sel("holdsAgentId(string)")+enc_dyn_string(AGENT)))
out["freeUsed_agentId"]=to_int(call(ADDR,sel("freeUsed(string)")+enc_dyn_string(AGENT)))
# Sourcify ABI shape (curl)
try:
    r=subprocess.run(["curl","-sL","--max-time","30",f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"],capture_output=True,text=True,timeout=35)
    meta=json.loads(r.stdout); abi=meta.get("abi",[])
    names={e["name"] for e in abi if e.get("type")=="function"}
    src=json.dumps(meta)
    out["sourcify"]={"match":meta.get("match"),"fn_count":len(names),
      "registry_ref":("0x60b9262456de011f7d15a54cdd8c48baaa8b022f" in src.lower()),
      "free_views":sorted(names & {"freeMinted","freeUsed","freeClaimed","freeSharesRemaining","freeLeft","freeAvailable","freeFor"}),
      "has_mint":any(n.lower().startswith("mint") for n in names),
      "has_quote":bool(names & {"quote","cost","getQuote","mintCost","price","getPrice","priceFor","quoteBulk"}),
      "is_nft":bool(names & {"tokenURI","ownerOf","safeTransferFrom"})}
except Exception as ex:
    out["sourcify"]={"error":f"{type(ex).__name__}: {str(ex)[:120]}"}
print(json.dumps(out,indent=1),flush=True)
json.dump(out,open(BASE+"run-2026-11-11-1731-ramraiders.json","w"),indent=1)
