#!/usr/bin/env python3
"""Boltbook 2301 lean verify: 4 quiet census lanes (Driftnauts/Rigorb/Tumblebots/Forklings).
Read-only; _fast_single sequential fallback. Targeted views only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
DEADLINE = time.time() + 240
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def raw(to, data, frm=None, value=None):
    if time.time() > DEADLINE: return "deadline"
    tx = {"to": to, "data": data}
    if frm: tx["from"] = frm
    if value is not None: tx["value"] = value
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [tx, "latest"], 8, retries=0)
            if v is None or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception: continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)

blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v: blk = int(v, 16); break
    except Exception: continue
print("head block:", blk, flush=True)
out = {"run": "2301", "block": blk, "contracts": {}}
GAME = ["0x6a926234d3767f2eeb3db12c1b4c9e2912c5589b",
        "0x02f10432eaf9cbf72e1ac9b9208af601aadd6b17",
        "0xd7b3fd33e0b465b0e374906f60567d317b758fd8"]
for addr in GAME:
    row = {}
    for v in ["totalSupply()", "freeMinted()", "FREE_CAP()", "MAX_SUPPLY()", "PRICE()", "REGISTRY()"]:
        row[v] = call(addr, v)
    row["canFreeMint_user"] = call(addr, "canFreeMint(address)", enc(USER))
    row["claimedFree_user"] = call(addr, "claimedFree(address)", enc(USER))
    row["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    # freeMint() no-arg sim from user, value 0 (nonpayable)
    row["freeMint_sim"] = raw(addr, sel("freeMint()"), frm=USER, value="0x0")
    out["contracts"][addr] = row
    print(addr, row, flush=True)
RIG = "0x72d977237f7b3931a08434cebd0d3814fe13539e"
row = {}
for v in ["totalSupply()", "MAX_SUPPLY()", "AGENT_ID_REGISTRY()", "mintOpen()"]:
    row[v] = call(RIG, v)
row["mintedCountOf_user"] = call(RIG, "mintedCountOf(address)", enc(USER))
row["balanceOf_user"] = call(RIG, "balanceOf(address)", enc(USER))
row["priceFor_user_1"] = call(RIG, "priceFor(address,uint256)", enc(USER) + format(1, "064x"))
row["mint1_value0_sim"] = raw(RIG, sel("mint(uint256)") + format(1, "064x"), frm=USER, value="0x0")
out["contracts"][RIG] = row
print(RIG, row, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-2301-boltbook-onchain-census.json", "w"), indent=1)
print("DONE", flush=True)
