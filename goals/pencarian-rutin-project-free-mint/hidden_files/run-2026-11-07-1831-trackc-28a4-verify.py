#!/usr/bin/env python3
"""Run 1831 parent: on-chain verify track-C S1 hit 0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224.
Read-only except own output."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(sig, arg=None, arg2=None):
    data = sel(sig) + (enc(arg) if arg else "") + (arg2.rjust(64, "0") if arg2 else "")
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return to_int(r[0])
        except Exception:
            continue
    return None
def call_str(sig):
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": ADDR, "data": sel(sig)}, "latest"])], endpoint=ep, timeout=10)
            raw = bytes.fromhex(r[0][2:])
            ln = int.from_bytes(raw[32:64], "big")
            return raw[64:64+ln].decode(errors="replace")
        except Exception:
            continue
    return None
def head():
    for ep in EPS:
        try:
            r = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
            return int(r[0], 16)
        except Exception:
            continue
    return None
def block_ts(blk):
    for ep in EPS:
        try:
            r = batch([("eth_getBlockByNumber", [hex(blk), False])], endpoint=ep, timeout=10)
            return int(r[0]["timestamp"], 16)
        except Exception:
            continue
    return None

out = {"contract": ADDR, "head": head()}
out["name"] = call_str("name()"); out["symbol"] = call_str("symbol()")
out["decimals"] = call("decimals()")
for v in ["totalSupply()", "totalMints()", "mintOpen()", "price()", "MAX_CAP()", "maxPerWallet()",
          "freeSharesRemaining()", "freeClaimed()", "freeLeft()", "freeUsed()", "freeAvailable()"]:
    out[v] = call(v)
out["isFreeMintAvailable_user"] = call("isFreeMintAvailable(address)", USER)
out["currentPriceFor_user"] = call("currentPriceFor(address)", USER)
out["mintsOf_user"] = call("mintsOf(address)", USER)
out["balanceOf_user"] = call("balanceOf(address)", USER)
out["agentRegistry"] = None
# agentRegistry() returns address: decode raw
for ep in EPS:
    try:
        r = batch([("eth_call", [{"to": ADDR, "data": sel("agentRegistry()")}, "latest"])], endpoint=ep, timeout=10)
        out["agentRegistry"] = "0x" + r[0][-40:]
        break
    except Exception:
        continue
# first mint block: scan says first_block 132194728; timestamp it
out["first_block_scan"] = 132194728
ts = block_ts(132194728)
out["first_mint_ts"] = ts
if ts:
    import datetime
    out["first_mint_wib"] = (datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))).strftime("%Y-%m-%d %H:%M:%S WIB")
# ABI function names for the record
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi", headers={"User-Agent": "curl/8"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        d = json.loads(resp.read().decode())
    out["abi_functions"] = sorted(set(f.get("name","") for f in d.get("abi",[]) if isinstance(f, dict)))
except Exception as ex:
    out["abi_error"] = str(ex)[:150]
json.dump(out, open(f"{BASE}/run-2026-11-07-1831-trackc-28a4-verify.json","w"), indent=1)
print(json.dumps(out, indent=1))
