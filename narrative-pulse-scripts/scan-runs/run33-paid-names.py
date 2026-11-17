import sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home()/"workspace/fast_exec"))
import fast_rpc
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def dec(h):
    try:
        b=bytes.fromhex(h[2:])
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
for c in ["0x72d99b2e591efbff4909508bfa802720a8ec7777","0x75cc33784db98ca72a8b4cb39151d2c419587777","0xf589cf21d3c641b4ccfdbef6e916af1d1a887777"]:
    for fn in ("name()","symbol()"):
        out=None
        for a in range(3):
            try: out=fast_rpc.race("eth_call",[{"to":c,"data":sel(fn)},"latest"]); break
            except Exception as e: print(c,fn,"ERR",str(e)[:150]); time.sleep(8)
        print(c,fn,dec(out) if out else None)
        time.sleep(6)
