#!/usr/bin/env python3
"""Check new contracts run 2026-11-16 09:31 WIB: AETHER 0x9265 (sweep) + 0xfd34 (Boltbook ZH new). Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed.binance.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def build(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=enc_u(int(a))
    return d
def call(addr,sig,args=[],block="latest"):
    payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":build(sig,args)},block]}
    for ep in EPS:
        for attempt in range(2):
            try:
                out=subprocess.run(["curl","-sL","--max-time","30","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=40).stdout
                j=json.loads(out)
            except Exception:
                continue
            r=j.get("result")
            if r and r!="0x" and "error" not in j: return r
    return None
def toint(r):
    try: return int(r,16)
    except Exception: return None
def callstr(addr,sig):
    r=call(addr,sig)
    if r is None: return None
    try:
        b=bytes.fromhex(r[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode(errors="ignore")
    except Exception: return None
def abi(addr):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"free-mint-search/0931"})
        with urllib.request.urlopen(req,timeout=20) as resp: return json.loads(resp.read().decode())
    except Exception as e: return {"error":str(e)[:150]}
for label,addr in [("AETHER","0x926504d174e99DB699141049b3Dd94dF501ff813"),("BOLTBOOK-ZH-NEW","0xfd3430e86df73c4e1e55036dc368a52716b84937")]:
    print("==",label,addr)
    print(" name:",callstr(addr,"name()"),"| symbol:",callstr(addr,"symbol()"))
    print(" totalSupply:",toint(call(addr,"totalSupply()") or "0x") if call(addr,"totalSupply()") else None)
    for v in ["totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_CAP()","MAX_SUPPLY()","mintOpen()","paused()","owner()","contractURI()"]:
        r=call(addr,v)
        print("  ",v, toint(r) if r and len(r)>=66 else r)
    print("  cost(user,1):", toint(call(addr,"cost(address,uint256)",[USER,1]) or "0x") if call(addr,"cost(address,uint256)",[USER,1]) else None)
    print("  mintedBy(user):", toint(call(addr,"mintedBy(address)",[USER]) or "0x") if call(addr,"mintedBy(address)",[USER]) else None)
    print("  balanceOf(user):", toint(call(addr,"balanceOf(address)",[USER]) or "0x") if call(addr,"balanceOf(address)",[USER]) else None)
    m=abi(addr)
    if "abi" in m:
        names={e["name"] for e in m["abi"] if e.get("type")=="function"}
        print("  sourcify: verified, n_fns",len(names))
        print("  fns:",sorted(names)[:60])
        print("  agent_ref:",bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_REGISTRY","AGENT_ID"}))
        print("  has_mint:",any(n.lower().startswith("mint") for n in names),"| free_views:",sorted(names & {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}))
    else:
        print("  sourcify:",m)
    # code size
    p={"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}
    code=""
    for ep in EPS:
        try:
            out=subprocess.run(["curl","-sL","--max-time","30","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=40).stdout
            code=json.loads(out).get("result","")
            if code: break
        except Exception: continue
    print("  code_bytes:",(len(code)-2)//2 if code.startswith("0x") else None,"| registry_bytes:", "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code.lower())
