#!/usr/bin/env python3
"""2331 run: totals check for 40 first-seen scan candidates. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:100]}"
    return None, err
tri=json.load(open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-2331-triage.json'))
cands=tri['cands']
out={}
blk=None
for ep in EPS:
    try: blk=int(_single(ep,"eth_blockNumber",[],8,retries=0),16); break
    except Exception: pass
for c in cands:
    a=c['address']; row={}
    for fn in ["totalSupply()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()"]:
        v,err=call(a, sel(fn))
        row[fn]={"int": int(v,16) if v and len(v)<=66 else None, "error": err if v is None else None}
    row['window_mints']=c['mint_count']; row['window_minters']=c['distinct_minters']
    row['first_block']=c['first_block']; row['name']=c.get('name'); row['symbol']=c.get('symbol')
    out[a]=row
res={"block": blk, "rows": out}
json.dump(res, open('/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-2331-triage-reads.json','w'), indent=1)
for a,row in out.items():
    ts=row['totalSupply()']['int']; wm=row['window_mints']
    verdict=""
    if ts is None: verdict="totalSupply unreadable"
    elif ts==wm: verdict="TOTAL == WINDOW (first mints in window)"
    elif ts is not None and wm>0 and ts<=wm+15: verdict="TOTAL close to window (likely first mints + post-window growth)"
    else: verdict=f"CONTINUATION (total {ts} >> window {wm})"
    print(f"{row['name']} {a} total={ts} freeClaimed={row['freeClaimed()']['int']} FREE_SUPPLY={row['FREE_SUPPLY()']['int']} window={wm} -> {verdict}")
