import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
ADDR = "0xbd4B4e7189ae9356514664146b0eD683601200A9"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_uint(n): return format(n, "064x")
def enc(a): return a[2:].lower().rjust(64, "0")
def call(sig, arg=""):
    data = sel(sig) + arg
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": ADDR, "data": data}, "latest"], 8, retries=0)
        except Exception as e:
            last = e
    return f"ERROR: {last}"
def to_int(v):
    try: return int(v, 16)
    except Exception: return v
def decode_str(raw):
    try:
        b = bytes.fromhex(raw[2:])
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"DECODE-FAIL {e}"
out = {}
o712 = call("ownerOf(uint256)", enc_uint(712))
out["ownerOf_712_raw"] = o712
try: out["ownerOf_712"] = "0x" + bytes.fromhex(o712[2:])[-20:].hex()
except Exception: out["ownerOf_712"] = o712
out["patternOf_712"] = to_int(call("patternOf(uint256)", enc_uint(712)))
out["stageOf_712"] = to_int(call("stageOf(uint256)", enc_uint(712)))
out["level_712"] = to_int(call("level(uint256)", enc_uint(712)))
ib = call("imageBase()")
out["imageBase"] = decode_str(ib) if isinstance(ib, str) and ib.startswith("0x") else ib
tu = call("tokenURI(uint256)", enc_uint(712))
out["tokenURI_712_raw"] = (tu[:300] if isinstance(tu, str) else tu)
out["tokenURI_712"] = decode_str(tu) if isinstance(tu, str) and tu.startswith("0x") and "ERROR" not in tu else tu
print(json.dumps(out, indent=1))
json.dump(out, open("inkkoi-postmint.json","w"), indent=1)
