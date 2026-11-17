#!/usr/bin/env python3
"""Run 0131 parent verification: HOPKIN GENESIS age/free, KAGENT phase, Horus confirm.
Read-only; writes run-2026-11-08-0131-hopkin-kagent.json (own file)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch, race
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
HOPKIN = "0x2728c134d79d34a977d6d35d8a3014abb5c97ed4"
KAGENT = "0xb34105002B19EF0ce43B59011fE848df5c8B174f"
HORUS = "0x794aD67a5590C7e5848E49181297F9cC7C6CE00E"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

out = {"run": "0131", "wib": "2026-11-08 ~02:00 WIB"}
# 1. block timestamp of HOPKIN first-seen block (lower bound on launch)
try:
    blk = batch([("eth_getBlockByNumber", [hex(131387835), False])])
    ts = int(blk[0]["timestamp"], 16) if blk and blk[0] else None
    import datetime
    out["hopkin_first_seen_block_ts"] = ts
    out["hopkin_first_seen_block_wib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
except Exception as e:
    out["hopkin_first_seen_block_err"] = str(e)

def call(to, sig, args=""):
    try:
        r = batch([("eth_call", [{"to": to, "data": sel(sig) + args}, "latest"])])
        return to_int(r[0]) if r else None
    except Exception as e:
        return f"ERR:{e}"[:120]

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "name()", "symbol()"]
for label, addr in [("hopkin", HOPKIN), ("horus", HORUS)]:
    d = {}
    for sig in VIEWS:
        base = sig.split("(")[0]
        key = base + ("_user" if "(address)" in sig else "")
        d[key] = call(addr, sig, enc(USER) if "(address)" in sig else "")
    d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + format(1, "064x"))
    d["registry_bytes"] = None
    out[label] = d
# KAGENT phase
out["kagent_phase"] = call(KAGENT, "phase()")
out["kagent_totalSupply"] = call(KAGENT, "totalSupply()")
out["kagent_balance_user"] = call(KAGENT, "balanceOf(address)", enc(USER))
# code check for registry bytes on HOPKIN
try:
    code = batch([("eth_getCode", [HOPKIN, "latest"])])[0]
    out["hopkin_registry_bytes"] = REG[2:].lower() in (code or "").lower()
    out["hopkin_code_len"] = len(code or "")
except Exception as e:
    out["hopkin_code_err"] = str(e)
json.dump(out, open(f"{BASE}/run-2026-11-08-0131-hopkin-kagent.json", "w"), indent=1)
print(json.dumps(out, indent=1))
