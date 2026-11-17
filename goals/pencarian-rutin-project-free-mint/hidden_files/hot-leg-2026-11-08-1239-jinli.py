import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
EP = "https://bsc-dataseed1.bnbchain.org/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def call(sig, arg=None):
    data = sel(sig)
    if arg == "USER": data += enc(USER)
    try:
        r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=EP, timeout=30)
        return r[0]
    except Exception as ex:
        return f"ERR {type(ex).__name__}: {ex}"
views = {
 "freeClaimed()": None, "FREE_SUPPLY()": None, "MAX_SUPPLY()": None,
 "totalSupply()": None, "mintOpen()": None, "mintedBy(address)": "USER",
 "balanceOf(address)": "USER", "owner()": None, "contractURI()": None,
 "tokenURI(uint256)": None, "name()": None, "symbol()": None,
 "AGENT_ID()": None, "isFreeEligible(address)": "USER",
 "freeClaimed(address)": "USER",
}
out = {}
for sig, arg in views.items():
    v = call(sig, arg)
    out[sig] = v
try:
    blk = int(batch([("eth_blockNumber", [])], endpoint=EP, timeout=30)[0], 16)
except Exception as ex:
    blk = f"ERR {ex}"
def ti(v):
    try: return int(v, 16)
    except Exception: return v
res = {"block": blk, "address": ADDR}
for k, v in out.items():
    if k in ("contractURI()", "tokenURI(uint256)", "name()", "symbol()"):
        res[k] = v
    else:
        res[k] = ti(v)
print(json.dumps(res, indent=1))
json.dump(res, open("hot-leg-2026-11-08-1239-jinli.json", "w"), indent=1)
