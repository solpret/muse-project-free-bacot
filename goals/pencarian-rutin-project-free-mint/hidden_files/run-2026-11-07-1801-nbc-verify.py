#!/usr/bin/env python3
"""NBC early-lead verification run 1801 (parent). Read-only except own output."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NBC = "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return to_int(r[0])
        except Exception:
            continue
    return None
def call_str(addr, sig):
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])], endpoint=ep, timeout=10)
            raw = bytes.fromhex(r[0][2:])
            # string: offset(32)+len(32)+data
            ln = int.from_bytes(raw[32:64], "big")
            return raw[64:64+ln].decode(errors="replace")
        except Exception:
            continue
    return None
out = {"contract": NBC, "started_wib": "2026-11-07 ~18:22 WIB"}
out["name"] = call_str(NBC, "name()")
out["symbol"] = call_str(NBC, "symbol()")
for v in ["totalSupply()", "totalMinted()", "freeTotal()", "freeUsed()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "freeLeft()"]:
    out[v] = call(NBC, v)
out["freeUsed_user"] = call(NBC, "freeUsed(address)", USER)
out["freeClaimed_user"] = call(NBC, "freeClaimed(address)", USER)
out["freeTakenBy_user"] = call(NBC, "freeTakenBy(address)", USER)
out["balanceOf_user"] = call(NBC, "balanceOf(address)", USER)
# quote(user,1): quote(address,uint256)
try:
    data = sel("quote(address,uint256)") + enc(USER) + "1".rjust(64, "0")
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": NBC, "data": data}, "latest"])], endpoint=ep, timeout=10)
            out["quote_user_1_raw"] = r[0]
            break
        except Exception:
            continue
except Exception as e:
    out["quote_error"] = str(e)
# first-mint block timestamp via fast_rpc (NEVER Ankr for timestamps)
for ep in EPS:
    try:
        r = batch([("eth_getBlockByNumber", [hex(132189223), False])], endpoint=ep, timeout=10)
        b = r[0]
        out["first_block"] = 132189223
        out["first_block_timestamp"] = int(b["timestamp"], 16)
        out["first_block_number_hex"] = b.get("number")
        break
    except Exception as e:
        out["block_ts_error"] = str(e)
# head
for ep in EPS:
    try:
        r = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
        out["head"] = int(r[0], 16)
        break
    except Exception:
        continue
print(json.dumps(out, indent=1), flush=True)
json.dump(out, open("run-2026-11-07-1801-nbc-verify.json", "w"), indent=1)
