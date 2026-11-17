import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to, data):
    try: return race("eth_call", [{"to": to, "data": data}, "latest"])
    except Exception as e: return f"ERR:{type(e).__name__}"
ADDR="0x08BE8a0727b6fc801171c1F4F4Dd547EA44Ca339"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def enc(a): return a[2:].lower().rjust(64,"0")
def di(h):
    try: return int(h,16)
    except Exception: return None
out={}
for sig in ["totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","totalMinted()"]:
    r=call(ADDR, sel(sig)); out[sig]=di(r) if isinstance(r,str) and r.startswith("0x") else r
for sig in ["balanceOf(address)","freeClaimed(address)","mintedBy(address)"]:
    r=call(ADDR, sel(sig)+enc(USER)); out[sig+"(user)"]=di(r) if isinstance(r,str) and r.startswith("0x") else r
try:
    blk=int(race("eth_blockNumber", []),16)
except Exception: blk=None
out["block"]=blk
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-07-1701-m3m3-check.json","w"), indent=1)
