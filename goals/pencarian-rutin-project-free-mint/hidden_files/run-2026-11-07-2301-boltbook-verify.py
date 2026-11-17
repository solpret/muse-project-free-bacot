#!/usr/bin/env python3
"""Boltbook 2301 lean verify: Sable / HOG ORBIT / helm.ai (new vs 2231, not in snapshot).
Read-only; _fast_single sequential fallback. Targeted views only (2231 lesson)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 240
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def raw(to, data, block="latest", frm=None, value=None):
    if time.time() > DEADLINE: return "deadline"
    tx = {"to": to, "data": data}
    if frm: tx["from"] = frm
    if value is not None: tx["value"] = value
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [tx, block], 8, retries=0)
            if v is None or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception: continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def getcode(to):
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_getCode", [to, "latest"], 8, retries=0)
            if v: return v
        except Exception: continue
    return None

blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v: blk = int(v, 16); break
    except Exception: continue
print("head block:", blk, flush=True)

HOG = "0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5"
HELM = "0xe0df49c281b8584f03ed21beac0e5002ec4a0599"
SABLE = "0x23d356173ff227d5bf6d622f4a8907f208871d76"
out = {"run": "2301", "block": blk, "contracts": {}}

for addr in (HOG, HELM):
    row = {}
    for v in ["totalSupply()", "MAX_SUPPLY()", "freeLeft()", "price()", "mintOpen()",
              "MAX_PER_WALLET()", "bogo()", "mintsLeft(address)", "agentIds()",
              "owner()", "treasury()", "name()", "symbol()"]:
        if v.endswith("(address)"):
            row[v] = call(addr, v, enc(USER))
        else:
            row[v] = call(addr, v)
    for v, k in [("costOf(address,uint256)", "costOf_user_1"),
                 ("freeOf(address,uint256)", "freeOf_user_1"),
                 ("mintedBy(address)", "mintedBy_user"),
                 ("balanceOf(address)", "balanceOf_user")]:
        row[k] = call(addr, v, enc(USER) + format(1, "064x") if "uint256" in v else enc(USER))
    code = getcode(addr)
    row["registry_bytes_in_code"] = (REGISTRY in code.lower()) if code else None
    row["code_len"] = len(code) if code else None
    out["contracts"][addr] = row
    print(addr, row, flush=True)

# Sable: no Sourcify ABI; probe standard selectors + mint(1) value-0 sim
row = {}
for v in ["totalSupply()", "MAX_SUPPLY()", "mintOpen()", "freeLeft()", "price()",
          "agentIds()", "agentRegistry()", "registry()"]:
    row[v] = call(SABLE, v)
for v, k in [("costOf(address,uint256)", "costOf_user_1"),
             ("freeOf(address,uint256)", "freeOf_user_1"),
             ("mintedBy(address)", "mintedBy_user"),
             ("balanceOf(address)", "balanceOf_user")]:
    row[k] = call(SABLE, v, enc(USER) + format(1, "064x") if "uint256" in v else enc(USER))
# mint(uint256) sim value 0 from user: raw returns None on revert via most RPCs
mint_data = sel("mint(uint256)") + format(1, "064x")
row["mint1_value0_sim"] = raw(SABLE, mint_data, frm=USER, value="0x0")
row["mint1_value0_sim_raw"] = row["mint1_value0_sim"]
code = getcode(SABLE)
row["registry_bytes_in_code"] = (REGISTRY in code.lower()) if code else None
row["code_len"] = len(code) if code else None
out["contracts"][SABLE] = row
print(SABLE, row, flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-07-2301-boltbook-onchain.json", "w"), indent=1)
print("DONE", flush=True)
