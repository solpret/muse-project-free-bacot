#!/usr/bin/env python3
"""Fresh track-C blocked-lead status re-read, run 2026-11-02 09:01 WIB. Read-only, NO preview retry."""
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
        try:
            v = _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            try: return int(v, 16) if v else None
            except Exception: return v
        except Exception: pass
    return None
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
out = {"block": block()}
# BIAO sale (from 0801 trackc-read; address in snapshot track_c)
snap = json.load(open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"))
biao = snap["track_c"]["BIAO"].get("address") or snap["track_c"]["BIAO"].get("sale") if "BIAO" in snap["track_c"] else None
print("BIAO sale in snapshot:", biao)
print("track_c keys:", list(snap["track_c"].keys()))
out["biao_sale"] = biao
if biao:
    for fn, arg in [("phase()", ""), ("freeClaimed()", ""), ("sold()", ""), ("tradingOpen()", ""), ("poolCreated()", ""), ("startedAt()", "")]:
        out["BIAO_" + fn] = call(biao, sel(fn) + arg)
bnb = snap["track_c"]["BNBbaby"]
sale = bnb["sale"]
for fn, arg in [("sharesMinted()", ""), ("freeMinted()", ""), ("freeAvailable(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:]), ("mintedBy(address)", enc_addr(USER)[2:])]:
    out["BNBbaby_" + fn] = call(sale, sel(fn) + arg)
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0901-trackc-read.json", "w"), indent=1)
