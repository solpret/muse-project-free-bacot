#!/usr/bin/env python3
"""Hot-leg 1739 leg4 v2: targeted re-read of 1729 leg4 items + 2 new leads.
LEAN batch, fallback MINIMAL on revert (same as main 1731 run); lead views called singly.
Read-only; writes only own run file."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def batch_views(addr, calls_spec):
    calls, keys = [], []
    for sig, args in calls_spec:
        data = sel(sig)
        for a in args:
            data += enc(a) if isinstance(a,str) and a.startswith("0x") else enc_u(a)
        key = sig.split("(")[0] + ("_user" if args else "")
        calls.append(("eth_call", [{"to": addr, "data": data}, "latest"]))
        keys.append(key)
    for ep in EPS:
        try:
            res = batch(calls, endpoint=ep, timeout=8)
            return {k: to_int(v) for k, v in zip(keys, res)}
        except Exception:
            continue
    return None
def single_view(addr, sig, args):
    return batch_views(addr, [(sig, args)])
prev=json.load(open(f"{BASE}/hot-leg-run-2026-11-07-1729.json"))
items=prev["leg4_reread"]["items"]
prev_block=prev["leg4_reread"]["block"]
out={"block":None,"items":{},"leads":{},"started_wib":"2026-11-07 17:39 WIB"}
try:
    b=batch([("eth_blockNumber",[])], endpoint=EPS[0], timeout=8)
    out["block"]=int(b[0],16)
except Exception as e:
    print("BLOCK-FAIL",e,flush=True)
print("BLOCK",out["block"],"prev",prev_block,flush=True)
LEAN=[("totalSupply()",[]),("totalMinted()",[]),("freeClaimed()",[]),("freeMinted()",[]),("FREE_SUPPLY()",[]),("mintOpen()",[]),("balanceOf(address)",[USER]),("freeClaimed(address)",[USER])]
MINIMAL=[("totalSupply()",[]),("balanceOf(address)",[USER])]
for name, it in items.items():
    addr=it["address"]
    got=batch_views(addr, LEAN)
    d={"address":addr}
    if got is None:
        got=batch_views(addr, MINIMAL)
        if got is not None:
            d.update(got)
            for k in ["totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","mintOpen","freeClaimed_user"]:
                d.setdefault(k,None)
            d["_fallback"]="minimal"
        else:
            for k in ["totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"]:
                d[k]=None
            d["_fallback"]="rpc-fail"
    else:
        d.update(got)
    out["items"][name]=d
    print(f"{name} ts={d.get('totalSupply')} fc={d.get('freeClaimed')} fm={d.get('freeMinted')} bal={d.get('balanceOf_user')} fcU={d.get('freeClaimed_user')} {d.get('_fallback','')}",flush=True)
LEAD_VIEWS=[("totalMints()",[]),("MAX_MINTS()",[]),("mintOpen()",[]),("freeLeft(address)",[USER]),("quote(address,uint256)",[USER,1]),("mintedBy(address)",[USER]),("balanceOf(address)",[USER])]
leads={"CipherAgent":"0x158b5e25015758a94703A27c152889451E5d52E5","MarsAgent":"0x2231FdAe405c33dc4993f8C577c453802FF1AcE9"}
prev_leads=prev["leg3_s1_verify"]
for name, addr in leads.items():
    d={"address":addr}
    for sig, args in LEAD_VIEWS:
        r=single_view(addr, sig, args)
        key=sig.split("(")[0]+("_user" if args else "")
        d[key]= (list(r.values())[0] if r else None)
    out["leads"][name]=d
    p=prev_leads[name]
    print(f"{name} totalMints={d.get('totalMints')} (prev {p.get('totalMints')}) freeLeft={d.get('freeLeft_user')} quote={d.get('quote_user')} mintedBy={d.get('mintedBy_user')} bal={d.get('balanceOf_user')}",flush=True)
json.dump(out,open(f"{BASE}/hot-leg-2026-11-07-1739-reread.json","w"),indent=1)
print("REREAD DONE",flush=True)
