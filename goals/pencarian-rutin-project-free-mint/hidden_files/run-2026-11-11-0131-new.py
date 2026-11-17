#!/usr/bin/env python3
"""Run 0131: verify 6 Boltbook-new contracts fresh on-chain. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr,views):
    calls=[];keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if isinstance(it,dict) and "error" in it else ti(it.get("result")) if isinstance(it,dict) else None) for it,k in zip(res,keys)}
        except Exception: continue
    return None
def raw(addr,sig):
    # returns raw hex result or None (for owner/address/string views)
    data=sel(sig)
    for ep in EPS:
        try:
            res=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
            if isinstance(res,dict) and "result" in res and res["result"] not in (None,"0x"): return res["result"]
        except Exception: continue
    return None
VIEWS=["totalSupply()","totalMinted()","agentFreeUsed()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","mintStart()","canMint(address)","balanceOf(address)","agentFreeByWallet(address)","freeLeft()","paidMinted()"]
ADDRS={
 "Pico Alcazar":"0xdf95946fe4ea475e7180f77817f9e34b459121f2",
 "Tiling Hammock":"0x5f872b5c147a5ebe79b63a06f79b920e51648e31",
 "Hexel Pantry":"0x4a8e51016829632ae15f574a837c17c5bf1bc50b",
 "GangDotFun":"0x64af2a4aa164aefec5c09c405ad894065d34633f",
 "Dragon Agent":"0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6",
 "Arcane Stones":"0x23f3De28E55C392F24A217B2B1602C90e0292f35",
 "ORBITJANITOR":"0x8d5a0555446d37afaba75e36da318646a4b32420",
 "STALL":"0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308",
}
out={}
for name,addr in ADDRS.items():
    t=time.time()
    v=batch(addr,VIEWS) or {}
    owner_raw=raw(addr,"owner()")
    owner=None
    if owner_raw:
        try: owner="0x"+owner_raw[-40:]
        except Exception: pass
    reg_raw=raw(addr,"REGISTRY()") or raw(addr,"AGENT_REGISTRY()") or raw(addr,"agentRegistry()")
    out[name]={"address":addr,"views":v,"owner":owner,"registry_raw":reg_raw}
    print(name, v, "owner=",owner, f"({time.time()-t:.1f}s)", flush=True)
json.dump(out,open("run-2026-11-11-0131-new.json","w"),indent=1)
print("DONE")
