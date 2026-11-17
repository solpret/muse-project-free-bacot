#!/usr/bin/env python3
"""On-chain verify S1-hit NFT 0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78.
Read-only eth_call via curl. Writes run-2026-11-11-2101-eee3-verify.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR="0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return ("%064x"%n)
def call(to, data, timeout=25):
    payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
                "-H","Content-Type: application/json","-d",json.dumps(payload)],
                capture_output=True,text=True,timeout=timeout+5)
            res=json.loads(r.stdout)
            if "result" in res: return res["result"]
        except Exception: continue
    return None
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def to_str(v):
    # decode ABI string return: offset(32)+len(32)+data
    try:
        if not v or v=="0x": return None
        b=bytes.fromhex(v[2:])
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def block():
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json",
                "-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],
                capture_output=True,text=True,timeout=30)
            return int(json.loads(r.stdout)["result"],16)
        except Exception: continue
    return None
out={"address":ADDR,"block":block(),"started_wib":"2026-11-11 21:01 WIB"}
views={
 "name()":"str","symbol()":"str","maxSupply()":"int","freePoolSize()":"int",
 "freePerWallet()":"int","priceWei()":"int","totalMinted()":"int","freeClaimed()":"int",
 "freeAvailable(address)":"int","freeUsedBy(address)":"int","hasAgentId(address)":"int",
 "AGENT_ID_REGISTRY()":"addr","balanceOf(address)":"int","mintedBy(address)":"int",
 "owner()":"addr","baseURI()":"str","maxPerWallet()":"int",
}
for sig,kind in views.items():
    base=sig.split("(")[0]
    data=sel(sig)+(enc(USER) if "(address)" in sig else "")
    raw=call(ADDR,data)
    if kind=="str": out[base]=to_str(raw)
    elif kind=="addr": out[base]=("0x"+raw[-40:]) if raw and len(raw)>=42 else None
    else: out[base]=to_int(raw)
    print(base, "=", out[base], flush=True)
# quote(address,uint256) -> (freeCount, cost)
qdata=sel("quote(address,uint256)")+enc(USER)+enc_u(1)
raw=call(ADDR,qdata)
if raw and len(raw)>=130:
    out["quote_freeCount"]=int(raw[2:66],16)
    out["quote_cost"]=int(raw[66:130],16)
else:
    out["quote_raw"]=raw
print("quote(user,1) freeCount=", out.get("quote_freeCount"), "cost=", out.get("quote_cost"), flush=True)
# tokenURI(0) if minted, tokenURI(1)
for tid in (0,1):
    raw=call(ADDR, sel("tokenURI(uint256)")+enc_u(tid))
    out[f"tokenURI_{tid}"]=to_str(raw)
    print(f"tokenURI({tid}) =", out[f"tokenURI_{tid}"], flush=True)
json.dump(out, open(BASE+"run-2026-11-11-2101-eee3-verify.json","w"), indent=1)
print("VERIFY DONE")
