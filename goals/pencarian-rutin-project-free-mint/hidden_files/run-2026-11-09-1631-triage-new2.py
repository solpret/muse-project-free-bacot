#!/usr/bin/env python3
"""Run 1631 triage-2: 0xCc844748 full reads, spot-sale pair registry reads, Flare selector scan. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        elif "(address,uint256)" in sig: data=sel(sig)+enc(USER)+"0"*64; key=base+"_user_1"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
def raw_call(addr,data):
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            if isinstance(r,dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def get_code(addr):
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]},timeout=25)
            if isinstance(r,dict) and r.get("result"): return r["result"]
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
out={"block":get_block(),"triage2":{}}
# 0xCc844748 full reads
V=["AGENT_ID_REGISTRY()","FREE_SUPPLY()","freeMinted()","freeAvailable()","freeUsed()","MAX_SUPPLY()","mintStart()","mintEnd()","mintOpen()","totalSupply()","totalMinted()","paidMinted()","PRICE()","TOKEN()","balanceOf(address)","freeUsed(address)","soldOut()","revealed()"]
r=raw_batch("0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0",V)
# AGENT_ID_REGISTRY returns address (32-byte) - decode separately
reg_raw=raw_call("0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0", sel("AGENT_ID_REGISTRY()"))
tok_raw=raw_call("0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0", sel("TOKEN()"))
def dec_addr(h):
    try: return "0x"+h[-40:] if h and len(h)>=42 else None
    except Exception: return None
out["triage2"]["0xCc844748"]={"reads":r,"AGENT_ID_REGISTRY":dec_addr(reg_raw),"TOKEN":dec_addr(tok_raw)}
print("CC84", json.dumps(out["triage2"]["0xCc844748"]), flush=True)
# spot-sale pair
for label,addr in [("SPOT-A","0xb79BA612aBe9BB82e727AB394b2c094C6507d76d"),("SPOT-B","0x448f01b6366b333e3e8046645c35181FFF51De5b")]:
    rr=raw_batch(addr,["AGENT_REGISTRY()","spotsLeft()","totalSpotsMinted()","MAX_SPOTS()","PRICE()","PER_SPOT()","totalSupply()","mintedBy(address)"])
    reg2=raw_call(addr, sel("AGENT_REGISTRY()"))
    out["triage2"][label]={"address":addr,"reads":rr,"AGENT_REGISTRY":dec_addr(reg2)}
    print(label, json.dumps(out["triage2"][label]), flush=True)
# Flare selector scan: extract PUSH4 selectors from runtime code, match known
code=get_code("0xe2deb47514bbfd19550866c8820bce04e8a8d416")
KNOWN={"freeMint()":"freeMint","mintFree()":"mintFree","claimFree()":"claimFree","claimFree(address)":"claimFree(ref)","mint()":"mint","mint(uint256)":"mint(n)","mint(address)":"mint(to)","freeClaimed(address)":"freeClaimed(addr)","freeMinted(address)":"freeMinted(addr)","hasFreeMinted(address)":"hasFreeMinted","freeClaimedByAgent(bytes32)":"freeClaimedByAgent","claimable(address)":"claimable","freeLeft()":"freeLeft","freeMinted()":"freeMinted","freeClaimed()":"freeClaimed","freeAvailable()":"freeAvailable","mintStart()":"mintStart","mintEnd()":"mintEnd","mintOpen()":"mintOpen","quote(address,uint256)":"quote","price()":"price","PRICE()":"PRICE","agentRegistry()":"agentRegistry","AGENT_REGISTRY()":"AGENT_REGISTRY"}
sels={}
if code:
    b=bytes.fromhex(code[2:])
    for i in range(len(b)-4):
        if b[i]==0x63:
            s="0x"+b[i+1:i+5].hex()
            sels[s]=sels.get(s,0)+1
found={}
for sig,name in KNOWN.items():
    s=sel(sig)
    if s in sels: found[sig]=s
out["triage2"]["Flare-selectors"]={"found_known":found,"n_selectors":len(sels)}
print("FLARE-SEL", json.dumps(found), "total selectors in code:", len(sels), flush=True)
with open(f"{BASE}/run-2026-11-09-1631-triage-new2.json","w") as f: json.dump(out,f,indent=1)
print("TRIAGE2 DONE block", out["block"], flush=True)
