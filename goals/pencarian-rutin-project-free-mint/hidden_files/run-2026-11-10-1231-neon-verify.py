import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
ADDR="0xfe0f456fb78efbde4427b81b025b6838321156ab"
VIEWS=["name()","symbol()","totalSupply()","totalMinted()","freeClaimed()","freeMinted()","freeLeft()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","owner()","balanceOf(address)","freeClaimed(address)","freeMinted(address)","priceFor(uint256)","quote(address,uint256)","agentRegistry()","agentId()","contractURI()","price()","mintStart()","freeSupply()"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def decode_str(h):
    try:
        b=bytes.fromhex(h[2:])
        if len(b)<96: return None
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode("utf-8","replace")
    except Exception: return None
calls=[];keys=[]
for i,sig in enumerate(VIEWS):
    base=sig.split("(")[0]
    if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
    elif "(uint256)" in sig: data=sel(sig)+"0"*63+"1"; key=base+"_1"
    elif "(address,uint256)" in sig: data=sel(sig)+enc(USER)+"0"*63+"1"; key=base+"_user1"
    else: data=sel(sig); key=base
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]}); keys.append(key)
outd={}
for ep in EPS:
    try:
        res=post(ep,calls)
        if not isinstance(res,list) or len(res)!=len(calls): continue
        for item,key in zip(res,keys):
            if not isinstance(item,dict) or "error" in item: outd[key]=None
            else:
                raw=item.get("result")
                if key in ("name","symbol","contractURI"): outd[key]=decode_str(raw) if raw else None
                elif key in ("owner","agentRegistry","agentId"): outd[key]=("0x"+raw[-40:]) if raw and len(raw)>=42 else raw
                else: outd[key]=to_int(raw)
        outd["_ep"]=ep; break
    except Exception: continue
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",headers={"User-Agent":"free-bacot/1231"})
    d=json.loads(urllib.request.urlopen(req,timeout=30).read().decode())
    sc={"verified":True,"match":d.get("match"),"verifiedAt":d.get("verifiedAt"),"fns":sorted({e["name"] for e in d.get("abi",[]) if e.get("type")=="function"})}
except Exception as e: sc={"verified":False,"error":f"{type(e).__name__}: {str(e)[:100]}"}
print("NeonCircuit",ADDR)
print("reads:",{k:v for k,v in outd.items() if v is not None})
print("sourcify:",sc)
disc=json.load(open(f"{BASE}/same-owner-discards.json"))
owners={str(x.get('owner','')).lower() for x in disc if isinstance(x,dict)}
print("owner in discards:", str(outd.get('owner') or '').lower() in owners, "| contract in discards:", ADDR.lower() in {str(x.get('contract','')).lower() for x in disc if isinstance(x,dict)})
json.dump({"reads":outd,"sourcify":sc},open(f"{BASE}/run-2026-11-10-1231-neon-verify.json","w"),indent=1)
