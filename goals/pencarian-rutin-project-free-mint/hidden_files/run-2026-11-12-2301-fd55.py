import json, subprocess
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(data, ep="https://bsc-dataseed.binance.org/"):
    out=subprocess.run(["curl","-sL","--max-time","20","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":"0xfd55F5b70F6eb6E59CEb6FF5c449f0cd1A3a5C0F","data":data},"latest"]})],capture_output=True,text=True,timeout=25).stdout
    return json.loads(out).get("result")
def dec(h):
    if not h or h=="0x": return None
    b=bytes.fromhex(h[2:])
    if len(b)>=64:
        off=int.from_bytes(b[:32],"big"); ln=int.from_bytes(b[32:64],"big")
        if 0<ln<10000 and off+32+ln<=len(b):
            try: return b[32+off:32+off+ln].decode("utf-8",errors="replace")
            except Exception: pass
    return b.decode("utf-8",errors="replace").strip("\x00")
print("name:", dec(call(sel("name()"))))
print("symbol:", dec(call(sel("symbol()"))))
print("tokenURI(1):", dec(call(sel("tokenURI(uint256)")+"00"*31+"01")))
