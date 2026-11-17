import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR="0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(sig, args_hex="", block="latest"):
    data=sel(sig)+args_hex
    for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/"]:
        try:
            r=batch([("eth_call",[{"to":ADDR,"data":data},block])],endpoint=ep,timeout=10)
            return r[0]
        except Exception as e:
            last=e
    return f"ERR {last}"
def dec_str(hexs):
    try:
        b=bytes.fromhex(hexs[2:])
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[32+off:64+off] if False else b[off:off+32],"big")
        # standard ABI: first word offset, then at offset: length, then data
        ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception as e:
        return f"DECODE-ERR {e} raw={hexs[:200]}"
out={}
out["contractURI_raw"]=call("contractURI()")
out["contractURI"]=dec_str(out["contractURI_raw"]) if out["contractURI_raw"].startswith("0x") else out["contractURI_raw"]
# tokenURI for token 1 and token 0
for tid in (1,0,224):
    raw=call("tokenURI(uint256)", format(tid,"064x"))
    out[f"tokenURI_{tid}_raw"]=raw
    out[f"tokenURI_{tid}"]=dec_str(raw) if isinstance(raw,str) and raw.startswith("0x") and len(raw)>10 else raw
# name/symbol
for fn in ("name()","symbol()","AGENT_ID()"):
    raw=call(fn)
    out[fn]=dec_str(raw) if isinstance(raw,str) and raw.startswith("0x") and len(raw)>10 else raw
print(json.dumps(out,indent=1,ensure_ascii=False))
json.dump(out,open("hot-leg-2026-11-08-1009-jinli-gate.json","w"),indent=1,ensure_ascii=False)
