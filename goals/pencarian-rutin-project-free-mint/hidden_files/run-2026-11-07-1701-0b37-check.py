import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to, data):
    try:
        r = race("eth_call", [{"to": to, "data": data}, "latest"])
        return r
    except Exception as e:
        return f"ERR:{type(e).__name__}"
ADDR="0x0b37150c92169Cc7f8953711c0bf6d461dc19111"
def dec_str(h):
    try:
        b=bytes.fromhex(h[2:])
        off=int.from_bytes(b[32:64],'big'); ln=int.from_bytes(b[64:96],'big')
        return b[off+32:off+32+ln].decode()
    except Exception: return None
def dec_int(h):
    try: return int(h,16)
    except Exception: return None
out={}
for sig,fn in [("name()","str"),("symbol()","str"),("totalSupply()","int"),("AGENT_ID_REGISTRY()","addr"),("agentRegistry()","addr"),("AGENT_ID()","addr"),("FREE_SUPPLY()","int"),("freeClaimed()","int"),("freeSupply()","int"),("MAX_SUPPLY()","int")]:
    r=call(ADDR, sel(sig))
    if fn=="str": out[sig]=dec_str(r) if isinstance(r,str) and r.startswith("0x") else r
    elif fn=="addr": out[sig]=("0x"+r[-40:]) if isinstance(r,str) and r.startswith("0x") and len(r)>=42 else r
    else: out[sig]=dec_int(r) if isinstance(r,str) and r.startswith("0x") else r
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-07-1701-0b37-check.json","w"), indent=1)
