import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
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
out = {"block": blk()}
CASES = [
 ("HIVE", "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", 808, ["totalSupply()","FREE_SUPPLY()","totalPaid()"]),
 ("Cathodex", "0x0AC5591d1B980C7bE16861d722E59E21E2624868", 421, ["totalSupply()","freeClaimed()","FREE_SUPPLY()"]),
 ("Kirinova", "0x68a971C9D2b54Ae86dAF59CD665E40f3E087fb7F", 377, ["totalSupply()","freeClaimed()","FREE_SUPPLY()"]),
 ("Zapcourier", "0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC", 387, ["totalSupply()","freeClaimed()","FREE_SUPPLY()"]),
]
for name, C, tid, fns in CASES:
    r = {}
    for fn in fns: r[fn] = iv(call(C, sel(fn)))
    r["ownerOf_token"] = call(C, sel("ownerOf(uint256)")+enc_uint(tid)[2:])
    r["balance_user"] = iv(call(C, sel("balanceOf(address)")+enc_addr(USER)[2:]))
    r["mintedBy_user"] = iv(call(C, sel("mintedBy(address)")+enc_addr(USER)[2:]))
    r["freeMintedBy_user"] = iv(call(C, sel("freeMintedBy(address)")+enc_addr(USER)[2:]))
    r["freeUsed_user"] = iv(call(C, sel("freeUsed(address)")+enc_addr(USER)[2:]))
    out[name] = r; print(name, json.dumps(r))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0631-mintedcheck.json","w"), indent=1)
