#!/usr/bin/env python3
"""Historical check: was supply already minted BEFORE this scan window (block 131814306)?
+ block timestamps for first_block of each first-seen. READ-ONLY."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_utils import keccak
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def rpc_call(method, params, timeout=10):
    last=None
    for ep in EPS:
        try: return _single(ep, method, params, timeout, retries=0)
        except Exception as e: last=e
    raise last
def sel(sig): return "0x"+keccak(text=sig).hex()[:8]
def call_at(addr, sig, block):
    try:
        out = rpc_call("eth_call", [{"to": addr, "data": sel(sig)}, hex(block)])
        return None if out in (None,"0x") else int(out,16)
    except Exception as e: return f"ERR:{str(e)[:60]}"
import datetime
d=json.load(open('run-2026-11-05-1901-scan-firstseen.json'))
WSTART=131814306
out={}
for r in d['results']:
    a=r['address']
    fb=r['first_block']
    try:
        blk=rpc_call("eth_getBlockByNumber", [hex(fb), False])
        ts=int(blk['timestamp'],16)
        tstr=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime('%Y-%m-%d %H:%M:%S WIB')
    except Exception as e:
        ts=None; tstr=f"ERR {e}"
    before={s: call_at(a, s, WSTART) for s in ["totalSupply()","freeMinted()","freeClaimed()","totalMinted()"]}
    out[a]={"name":r['name'],"symbol":r['symbol'],"first_block":fb,"first_block_time_wib":tstr,
            "verdict":r['verdict'],"supply_before_window":before,
            "supply_now":r['onchain_views']}
    print(a, r['name'], '| first mint block', fb, tstr, '| before-window:', before, '| now:', r['onchain_views'])
json.dump(out, open('run-2026-11-05-1901-history.json','w'), indent=1)
print('WROTE run-2026-11-05-1901-history.json')
