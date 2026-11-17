import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,data):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
            v=r.get("result")
            if v and v!="0x": return v
        except Exception: continue
    return None
def dec_str(h):
    if not h: return None
    b=bytes.fromhex(h[2:])
    if len(b)>=64:
        off=int.from_bytes(b[:32],"big"); ln=int.from_bytes(b[32:64],"big")
        if 0<ln<10000 and off+32+ln<=len(b):
            try: return b[32+off:32+off+ln].decode("utf-8",errors="replace")
            except Exception: pass
    try: return b.decode("utf-8",errors="replace").strip("\x00")
    except Exception: return h[:200]
def dec_int(h):
    try: return int(h,16) if h and h!="0x" else None
    except Exception: return None
T={
 "SolNFT":"0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
 "AgcNFT":"0xdAc222886b887fC5b6262889B189B8eb57e99794",
 "NEW-fd55":"0xfd55F5b70F6eb6E59CEb6FF5c449f0cd1A3a5C0F",
}
out={}
for name,addr in T.items():
    d={}
    for fn in ["FREE_CAP()","FREE_SUPPLY()","MAX_SUPPLY()"]:
        d[fn]=dec_int(call(addr,sel(fn)))
    for fn in ["name()","symbol()","contractURI()"]:
        d[fn]=dec_str(call(addr,sel(fn)))
    # tokenURI(1)
    import binascii
    data=sel("tokenURI(uint256)")+"00"*31+"01"
    d["tokenURI(1)"]=dec_str(call(addr,data))
    out[name]=d
    print(name, json.dumps(d,ensure_ascii=False)[:800], flush=True)
json.dump(out,open(BASE+"run-2026-11-12-2301-strings.json","w"),indent=1)
