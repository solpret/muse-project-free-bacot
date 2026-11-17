import json, subprocess, time
EPS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc-dataseed.binance.org"]
def call(to,data,tag):
    payload=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]})
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-s","--max-time","25","-X","POST","-H","Content-Type: application/json","-d",payload,ep],capture_output=True,text=True,timeout=30)
            d=json.loads(r.stdout)
            if "result" in d: return {"tag":tag,"to":to,"data":data,"result":d["result"],"endpoint":ep}
            err=d.get("error")
        except Exception as e: err=str(e)
    return {"tag":tag,"to":to,"data":data,"result":None,"error":str(err)}
BHTB="0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467"
SALE="0x651302C0043040D48EaAF85605E12F0549aD6D89"
TOK="0xd8FAF2597c8b81eed4befA4A651cccF05196163b"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
pad=USER[2:].lower().rjust(64,"0")
out=[]
# (H) contractURI() 0xe8a3d485 ; (I) tokenURI(1) 0xc87b56dd + uint256(1)
out.append(call(BHTB,"0xe8a3d485","BHTB contractURI()"))
out.append(call(BHTB,"0xc87b56dd"+"0"*63+"1","BHTB tokenURI(1)"))
out.append(call(SALE,"0xe8a3d485","AgentGrid sale contractURI()"))
out.append(call(TOK,"0xe8a3d485","AgentGrid token contractURI()"))
out.append(call(TOK,"0xc87b56dd"+"0"*63+"1","AgentGrid token tokenURI(1)"))
# AgentGrid claimedShares(address): selector keccak('claimedShares(address)')[:4] - compute via known? use cast-less: try 0x... need selector; compute with python sha3
from hashlib import sha3_256
import binascii
def sel(sig):
    # keccak-256
    try:
        from Crypto.Hash import keccak
        k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
    except Exception:
        return None
s=sel("claimedShares(address)")
print("claimedShares selector:",s)
if s: out.append(call(SALE,s+pad,"AgentGrid sale claimedShares(user) retry"))
# BHTB: also try external metadata-ish: name/symbol already known; try tokenURI via metadata file saved earlier? skip
# decode helper: try utf8/base64 decode of returndata
def try_decode(hexstr):
    if not hexstr or hexstr=="0x": return None
    try:
        b=bytes.fromhex(hexstr[2:])
        # abi string: offset(32)+len(32)+data
        if len(b)>=64:
            ln=int.from_bytes(b[32:64],"big")
            raw=b[64:64+ln]
            try: return raw.decode("utf-8")
            except Exception: return raw[:500].hex()
        return b.decode("utf-8","replace")
    except Exception as e: return f"<decode err {e}>"
for o in out:
    o["decoded"]=try_decode(o.get("result"))
    print(json.dumps(o)[:800],flush=True)
json.dump(out,open("run-2026-11-09-0501-deepdive-calls.json","w"),indent=1)
print("saved calls json")
