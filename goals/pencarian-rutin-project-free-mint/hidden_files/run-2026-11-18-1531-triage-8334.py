#!/usr/bin/env python3
"""Triage 0x8334 (Sourcify feed 14:44 WIB, ERC721 claim-gated, agentId). Read-only, chunked <=5."""
import json, subprocess
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def post(payload, timeout=25):
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, timeout=timeout+5)
    return json.loads(r.stdout.decode())
def batch(addr, views, chunk=5):
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
        print(f"  chunk {i//chunk+1} OK", flush=True)
    return out
ADDR="0x8334C7d0e8aF217EEA5251A0A181e628971535e1"
code=post([{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]}])
codelen=len(code[0].get("result","")) if isinstance(code,list) else 0
reg="60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code[0].get("result","").lower() if isinstance(code,list) else "")
print("codelen:",codelen,"registry_bytes:",reg)
VIEWS=[("totalSupply","totalSupply()",None),("totalMinted","totalMinted()",None),
 ("name","name()",None),("symbol","symbol()",None),
 ("agentId","agentId()",None),("MAX_PER_WALLET","MAX_PER_WALLET()",None),
 ("MAX_AUTH_WINDOW","MAX_AUTH_WINDOW()",None),("paused","paused()",None),
 ("claimSigner","claimSigner()",None),("redeemer","redeemer()",None),
 ("owner","owner()",None),("hasClaimed_user","hasClaimed(address)","user"),
 ("mintedTo_user","mintedTo(address)","user"),
 ("balanceOf_user","balanceOf(address)","user")]
views=batch(ADDR,VIEWS,chunk=5)
print("views:",views)
# decode name/symbol if hex strings
for k in ("name","symbol"):
    v=views.get(k)
    if isinstance(v,str) and v.startswith("0x"):
        try:
            b=bytes.fromhex(v[2:])
            print(k,"decoded:",b[64:].split(b"\x00")[0])
        except Exception as e: print(k,"decode fail",e)
json.dump({"address":ADDR,"codelen":codelen,"registry_bytes":reg,"views":views},
          open(f"{HF}/run-2026-11-18-1531-triage-8334.json","w"), indent=1)
print("saved run-2026-11-18-1531-triage-8334.json")
