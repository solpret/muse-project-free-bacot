import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
C = "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v,16) if v else None
print("freeUsed() total:", iv(call(C, sel("freeUsed()"))))
print("freeTakenBy(user):", iv(call(C, sel("freeTakenBy(address)")+enc_addr(USER))))
print("paidTakenBy(user):", iv(call(C, sel("paidTakenBy(address)")+enc_addr(USER))))
g = call(C, sel("gate()")); print("gate raw:", g, "-> addr:", "0x"+g[-40:] if g else None)
# block timestamp of first mint block 132189223 via dataseed (Ankr returns fake now-timestamps)
for ep in EPS:
    try:
        b=_single(ep,"eth_getBlockByNumber",["0x7e10c27",False],8,retries=0)
        print("first-mint block ts:", int(b["timestamp"],16), "->", __import__("datetime").datetime.fromtimestamp(int(b["timestamp"],16), __import__("datetime").timezone(__import__("datetime").timedelta(hours=7))).isoformat())
        break
    except Exception as e: print("blk err", str(e)[:100])
