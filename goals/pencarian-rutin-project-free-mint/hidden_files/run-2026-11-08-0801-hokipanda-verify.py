#!/usr/bin/env python3
"""Parent verification of HokiPanda strong lead + HokiKoi single-call retry. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
HP = "0x4b61A7767dA68f18266907b2Eb7C9A1EE3d24517"
HK = "0x74055b4Afe2d8c7347e8D4c0fc23e704405F7A36"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return str(n).rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(addr, sig, args=None):
    data = sel(sig)
    if args:
        for a in args: data += a
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return r[0]
        except Exception:
            continue
    return None
def call_int(addr, sig, args=None):
    return to_int(call(addr, sig, args))
def call_str(addr, sig, args=None):
    raw = call(addr, sig, args)
    if not raw or raw == "0x": return None
    try:
        h = raw[2:]
        # string: offset(64) + len(64) + data
        ln = int(h[64:128], 16)
        return bytes.fromhex(h[128:128+ln*2]).decode("utf-8", "replace")
    except Exception:
        return raw
out = {"wib": "2026-11-08 ~08:31 WIB", "hokipanda": {}, "hokikoi_retry": {}}
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=10)[0], 16)
except Exception as e:
    out["block"] = None
    print("BLOCK-FAIL", e, flush=True)
hp = out["hokipanda"]
hp["address"] = HP
hp["name"] = call_str(HP, "name()")
hp["symbol"] = call_str(HP, "symbol()")
hp["totalMinted"] = call_int(HP, "totalMinted()")
hp["totalSupply"] = call_int(HP, "totalSupply()")
hp["freeMinted"] = call_int(HP, "freeMinted()")
hp["FREE_CAP"] = call_int(HP, "FREE_CAP()")
hp["FREE_PER_WALLET"] = call_int(HP, "FREE_PER_WALLET()")
hp["paidMintedCount"] = call_int(HP, "paidMintedCount()")
hp["mintOpen"] = call_int(HP, "mintOpen()")
hp["freeCount_user"] = call_int(HP, "freeCount(address)", [enc(USER)])
hp["balanceOf_user"] = call_int(HP, "balanceOf(address)", [enc(USER)])
hp["owner"] = call(HP, "owner()")
hp["agentIdRegistry"] = call(HP, "agentIdRegistry()")
hp["contractURI"] = call_str(HP, "contractURI()")
hp["tokenURI_1"] = call_str(HP, "tokenURI(uint256)", [enc_u(1)])
hp["PRICE"] = call_int(HP, "PRICE()")
hp["priceFor_user_1"] = None
hk = out["hokikoi_retry"]
hk["totalMinted"] = call_int(HK, "totalMinted()")
hk["freeMinted"] = call_int(HK, "freeMinted()")
hk["FREE_CAP"] = call_int(HK, "FREE_CAP()")
hk["freeCount_user"] = call_int(HK, "freeCount(address)", [enc(USER)])
hk["balanceOf_user"] = call_int(HK, "balanceOf(address)", [enc(USER)])
hk["mintOpen"] = call_int(HK, "mintOpen()")
print(json.dumps(out, indent=1), flush=True)
json.dump(out, open("run-2026-11-08-0801-hokipanda-verify.json", "w"), indent=1)
