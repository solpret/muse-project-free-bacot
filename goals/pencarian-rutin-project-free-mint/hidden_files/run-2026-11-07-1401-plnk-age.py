#!/usr/bin/env python3
"""PLNK first-mint age check: binary search sharesSold(block) for first block
with sharesSold>0, then timestamp that block (fast_rpc, NOT Ankr). Read-only."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
ADDR="0xec266bdd979b19d8a2f1266ef0610b4791dbd24b"
def shares_at(blk):
    for attempt in range(3):
        try:
            r=race("eth_call", [{"to": ADDR, "data": sel("sharesSold()")}, hex(blk)])
            return int(r,16)
        except Exception as e:
            time.sleep(4)
    return None
head=int(race("eth_blockNumber", []), 16)
print("head:", head, flush=True)
lo, hi = head-60000, head
# verify hi>0 and lo==0 (or find a zero)
v_hi=shares_at(hi); print("sharesSold(head):", v_hi, flush=True)
v_lo=shares_at(lo); print("sharesSold(head-60000):", v_lo, flush=True)
if v_lo is None or v_hi is None:
    print("HISTORICAL CALLS FAILED - age UNVERIFIED", flush=True); sys.exit(2)
if v_lo>0:
    print("sharesSold already >0 at head-60000: launch EARLIER than window - age UNVERIFIED (need wider search)", flush=True); sys.exit(3)
while lo+1<hi:
    mid=(lo+hi)//2
    v=shares_at(mid)
    print(f"mid {mid} sharesSold={v}", flush=True)
    if v is None:
        print("mid call failed, aborting binary search", flush=True); sys.exit(2)
    if v>0: hi=mid
    else: lo=mid
print("FIRST BLOCK sharesSold>0:", hi, flush=True)
blk=race("eth_getBlockByNumber", [hex(hi), False])
ts=int(blk["timestamp"],16)
import datetime
print("first-block timestamp:", ts, datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat(), flush=True)
json.dump({"head":head,"first_block_shares_gt0":hi,"timestamp":ts}, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-1401-plnk-age.json","w"), indent=1)
