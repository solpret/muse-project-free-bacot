import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v, 16) if v else None
def blk():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
out={"block": blk()}
N="0x9395e207F9928657237DE96ffB12340094c073cd"
out["NULLSECTOR"]={"totalSupply": iv(call(N, sel("totalSupply()"))), "MAX_SUPPLY": iv(call(N, sel("MAX_SUPPLY()"))),
  "mintOpen": iv(call(N, sel("mintOpen()"))), "freeClaimed_user": iv(call(N, sel("freeClaimed(address)")+enc_addr(USER)[2:])),
  "balance_user": iv(call(N, sel("balanceOf(address)")+enc_addr(USER)[2:]))}
O="0xD1D3b730b154838b7B5F0c072dE7bA66FFBbe72b"
out["Onimaru"]={"totalMinted": iv(call(O, sel("totalMinted()"))), "freeMinted": iv(call(O, sel("freeMinted()"))),
  "FREE_CAP": iv(call(O, sel("FREE_CAP()"))), "mintedBy_user": iv(call(O, sel("mintedBy(address)")+enc_addr(USER)[2:])),
  "balance_user": iv(call(O, sel("balanceOf(address)")+enc_addr(USER)[2:]))}
R="0x25F6DF83D43496583BC7190f02E68A15C3E3bB25"
out["Rootlinks"]={"totalMinted": iv(call(R, sel("totalMinted()"))), "freeMinted": iv(call(R, sel("freeMinted()"))),
  "FREE_CAP": iv(call(R, sel("FREE_CAP()"))), "mintOpen": iv(call(R, sel("mintOpen()"))),
  "balance_user": iv(call(R, sel("balanceOf(address)")+enc_addr(USER)[2:]))}
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-02-0631-verify2.json","w"), indent=1)
