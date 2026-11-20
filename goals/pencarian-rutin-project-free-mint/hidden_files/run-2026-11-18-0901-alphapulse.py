#!/usr/bin/env python3
"""AlphaPulse Genesis Badge V1 0xE09A - shape + on-chain probe, run 0901. Read-only."""
import json, subprocess
from eth_hash.auto import keccak
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC="https://bsc-dataseed.binance.org/"
def sel(s): return keccak(s.encode())[:4].hex()
def enc(a): return "0"*24+a[2:].lower()
def encode(sig,arg=None):
    d="0x"+sel(sig)
    if arg=="user": d+=enc(USER)
    elif arg=="one": d+="%064x"%1
    elif arg=="user1": d+=enc(USER)+"%064x"%1
    return d
def post(payload, timeout=25):
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
# Sourcify ABI
try:
    r=subprocess.run(["curl","-s","-L","--max-time","25",f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"],capture_output=True,timeout=30)
    meta=json.loads(r.stdout.decode())
    abi=meta.get("abi",[])
    fns=sorted({e["name"] for e in abi if e.get("type")=="function"})
    print("SOURCIFY verifiedAt:", meta.get("verifiedAt"), "match:", meta.get("match"), "n_fns:", len(fns))
    print("FNS:", fns)
except Exception as e:
    print("SOURCIFY FAIL:", type(e).__name__, str(e)[:200])
    fns=[]
# on-chain probe
VIEWS=[("totalSupply","totalSupply()",None),("totalMinted","totalMinted()",None),
("MAX_SUPPLY","MAX_SUPPLY()",None),("FREE_SUPPLY","FREE_SUPPLY()",None),
("freeMinted","freeMinted()",None),("freeClaimed","freeClaimed()",None),
("freeLeft","freeLeft()",None),("freeRemaining","freeRemaining()",None),
("mintOpen","mintOpen()",None),("mintedBy_user","mintedBy(address)","user"),
("balanceOf_user","balanceOf(address)","user"),
("cost_user_1","cost(address,uint256)","user1"),
("quote_user_1","quote(address,uint256)","user1"),
("freeMintedByWallet_user","freeMintedByWallet(address)","user"),
("agentRegistry","agentRegistry()",None),("AGENT_ID_REGISTRY","AGENT_ID_REGISTRY()",None),
("name","name()",None),("symbol","symbol()",None)]
calls=[(ADDR,encode(s,a)) for _,s,a in VIEWS]
payload=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":t,"data":d},"latest"]} for i,(t,d) in enumerate(calls)]
resp=post(payload)
by={it["id"]:it for it in resp if isinstance(it,dict)}
out={}
for i,(label,sig,arg) in enumerate(VIEWS):
    it=by.get(i+1,{})
    if "result" in it and it["result"] not in (None,"0x"):
        v=it["result"]
        if sig in ("name()","symbol()"):
            try:
                b=bytes.fromhex(v[2:])
                ln=int.from_bytes(b[64:96],"big"); out[label]=b[96:96+ln].decode(errors="replace")
            except Exception: out[label]=v
        else:
            try: out[label]=int(v,16)
            except Exception: out[label]=v
    elif "error" in it: out[label]="err"
    else: out[label]=None
blk=post([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])
print("BLOCK:", int(blk[0]["result"],16))
print(json.dumps(out,indent=1))
# code + registry bytes
code=post([{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]}])
c=(code[0].get("result") or "").lower()
print("codelen:", len(c), "registry-bytes:", "60b9262456de011f7d15a54cdd8c48baa8b022f" in c)
json.dump({"address":ADDR,"fns":fns,"views":out,"block":int(blk[0]["result"],16),"registry_bytes":"60b9262456de011f7d15a54cdd8c48baa8b022f" in c}, open(f"{HF}/run-2026-11-18-0901-alphapulse.json","w"), indent=1)
