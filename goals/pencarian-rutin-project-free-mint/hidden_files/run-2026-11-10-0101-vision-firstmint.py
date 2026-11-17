#!/usr/bin/env python3
"""VISION first-mint block via binary search on eth_getCode (deploy) + totalSupply (first mint).
Read-only. Uses dataseed eth_call/eth_getCode at historical blocks."""
import json, subprocess, time
ADDR="0x5f76cab7b054e088563d5098e17bd0dc430e61ae"
EP="https://bsc-dataseed1.bnbchain.org/"
TS="0x70c615b4000000000000000000000000000000000000000000000000000000000"  # totalSupply() selector wrong placeholder
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
TS_SEL=sel("totalSupply()")
def rpc_call(method, params, timeout=25):
    payload={"jsonrpc":"2.0","id":1,"method":method,"params":params}
    for attempt in range(2):
        try:
            out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
            r=json.loads(out)
            if "result" in r: return r["result"]
        except Exception as e:
            time.sleep(2)
    return None
def has_code(blk):
    r=rpc_call("eth_getCode",[ADDR,hex(blk)])
    return bool(r and r!="0x" and r!="0x0")
def supply(blk):
    r=rpc_call("eth_call",[{"to":ADDR,"data":TS_SEL},hex(blk)])
    if r is None or r=="0x": return None
    try: return int(r,16)
    except Exception: return None
def block_ts(blk):
    r=rpc_call("eth_getBlockByNumber",[hex(blk),False])
    if isinstance(r,dict) and r.get("timestamp"):
        return int(r["timestamp"],16)
    return None
# 1) deploy block: code appears first in [132590000, 132625000]
lo,hi=132590000,132625000
assert has_code(hi), "no code at hi"
while lo<hi:
    mid=(lo+hi)//2
    if has_code(mid): hi=mid
    else: lo=mid+1
deploy=lo
print("DEPLOY_BLOCK",deploy,flush=True)
# 2) first block with totalSupply>0 in [deploy, 132621755]
lo,hi=deploy,132621755
s_hi=supply(hi); print("supply@hi",s_hi,flush=True)
while lo<hi:
    mid=(lo+hi)//2
    s=supply(mid)
    if s is None:
        print("supply None at",mid,"- retry once"); s=supply(mid)
    if s and s>0: hi=mid
    else: lo=mid+1
first=lo
ts=block_ts(first)
print("FIRST_MINT_BLOCK",first,"TS",ts,flush=True)
import datetime
if ts:
    print("FIRST_MINT_WIB",datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"),flush=True)
    print("FIRST_MINT_UTC",datetime.datetime.fromtimestamp(ts,datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),flush=True)
json.dump({"deploy_block":deploy,"first_mint_block":first,"first_mint_ts":ts},open("run-2026-11-10-0101-vision-firstmint.json","w"),indent=1)
