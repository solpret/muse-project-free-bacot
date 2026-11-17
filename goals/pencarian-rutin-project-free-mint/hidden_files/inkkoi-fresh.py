import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single, batch
from Crypto.Hash import keccak
ADDR = "0xbd4B4e7189ae9356514664146b0eD683601200A9"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return v
def single(sig, arg=""):
    data = sel(sig) + arg
    for ep in EPS:
        try:
            return to_int(_single(ep, "eth_call", [{"to": ADDR, "data": data}, "latest"], 8, retries=0))
        except Exception:
            continue
    return None
out = {}
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16)
except Exception as e:
    out["block"] = f"ERR {e}"
out["totalSupply"] = single("totalSupply()")
out["freeMinted"] = single("freeMinted()")
out["FREE_SUPPLY"] = single("FREE_SUPPLY()")
out["mintOpen"] = single("mintOpen()")
out["freeClaimed_user"] = single("freeClaimed(address)", enc(USER))
out["balanceOf_user"] = single("balanceOf(address)", enc(USER))
print(json.dumps(out, indent=1))
json.dump(out, open("inkkoi-fresh.json","w"), indent=1)
