import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home()/"workspace/fast_exec"))
import fast_rpc
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def decode_str(h):
    try:
        b=bytes.fromhex(h[2:])
        if len(b)<96: return None
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
c="0xc7c171e479f6ad8a728e77b7484bb7d0b4984d0f"
tx="0xaf658b6c5a22c982d807d2edac733517f07f477d3a1778c70039de14841b295d"
r=fast_rpc.race("eth_getTransactionReceipt",[tx])
print("receipt status",r.get("status"),"block",r.get("blockNumber"),"logs",len(r.get("logs") or []))
for lg in r.get("logs") or []:
    print(" log",lg.get("address"),lg.get("topics"),lg.get("data"))
for fn in ("name()","symbol()","owner()","decimals()"):
    out=None
    for attempt in range(3):
        try:
            out=fast_rpc.race("eth_call",[{"to":c,"data":sel(fn)},"latest"]); break
        except Exception as e:
            print(fn,"attempt",attempt,"ERR",str(e)[:200]); time.sleep(8)
    if fn=="decimals()":
        print(fn, int(out,16) if out else None, out)
    elif fn=="owner()":
        print(fn, ("0x"+out[-40:]) if out else None, out)
    else:
        print(fn, decode_str(out) if out else None, out)
    time.sleep(6)
