#!/usr/bin/env python3
"""Run 2101: Nidavellir free views + first-mint launch time. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NID = "0xd527109571b039298b65bCB26313dcbED0978c97"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def read_one(to, data):
    try: return to_int(race("eth_call", [{"to": to, "data": data}, "latest"]))
    except Exception: return None
out = {}
for sig in ["freeWindowOpen()", "FREE_SUPPLY_LIMIT()", "PRICE()", "freeRemaining(address)", "remainingFor(address)", "totalSupply()", "mintOpen()"]:
    d = sel(sig) + enc(USER) if "address" in sig else sel(sig)
    out[sig] = read_one(NID, d)
    print(sig, "=", out[sig], flush=True)
# first mint: Transfer(address,address,uint256) topic0
k = keccak.new(digest_bits=256); k.update(b"Transfer(address,address,uint256)")
topic0 = "0x" + k.hexdigest()
zero = "0x" + "0"*64
head = int(race("eth_blockNumber", []), 16)
print("head", head, flush=True)
# binary search for first mint: check 1000-block chunks backwards from head, but
# first probe wide windows to find earliest mint block cheaply
def logs(frm, to):
    try:
        return race("eth_getLogs", [{"fromBlock": hex(frm), "toBlock": hex(to), "address": NID,
              "topics": [topic0, zero]}])
    except Exception as e:
        print("getLogs fail", frm, to, e, flush=True); return None
# probe: last 200k blocks in 20k chunks to find earliest chunk with a mint
found_from = None
step = 20000
lo = head
while lo > head - 400000 and lo > 0:
    frm = max(0, lo - step)
    r = logs(frm, lo)
    if r:
        print(f"chunk {frm}-{lo}: {len(r)} mints", flush=True)
        found_from = (frm, lo, len(r))
        break
    lo = frm - 1
    print(f"chunk {frm}-{lo+1}: 0", flush=True)
out["probe"] = found_from
if found_from:
    # narrow within that chunk in 1000-block steps from the start
    frm0 = found_from[0]
    cur = frm0
    first = None
    while cur <= found_from[1]:
        r = logs(cur, min(cur+999, found_from[1]))
        if r:
            first = r[0]; print("first mint log:", json.dumps(first), flush=True); break
        cur += 1000
    if first:
        blk = int(first["blockNumber"], 16)
        out["first_mint_block"] = blk
        out["first_mint_tx"] = first.get("transactionHash")
        try:
            b = race("eth_getBlockByNumber", [hex(blk), False])
            out["first_mint_ts"] = int(b["timestamp"], 16)
            print("first mint block", blk, "ts", out["first_mint_ts"], flush=True)
        except Exception as e:
            print("block ts fail", e, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-2101-nidavellir-free.json", "w"), indent=1)
print("DONE", json.dumps(out), flush=True)
