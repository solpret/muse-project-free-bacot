#!/usr/bin/env python3
"""Compact probe of the 22 re-find contracts (read-only): owner/PRICE/MAX/FREE/freeClaimed/totalSupply/user slot.
Plus control walk-back for Hoopsy (validates walk-back method: expect many mints before in-window first_block)."""
import json, datetime, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def rpc(m,p,timeout=10):
    last=None
    for ep in EPS:
        try: return _single(ep,m,p,timeout,retries=0)
        except Exception as e: last=e
    raise last
def sel(s): return "0x"+keccak(s.encode()).hex()[:8]
def call(a,d): return rpc("eth_call",[{"to":a,"data":d},"latest"])
def u256(h):
    if not isinstance(h,str) or not h.startswith("0x") or len(h)<66: return None
    return int(h[-64:],16)
def addr_of(h):
    if not isinstance(h,str) or not h.startswith("0x") or len(h)<66: return None
    return "0x"+h[-40:]
def enc_addr(a): return "0x"+"00"*12+a[2:].lower()
split=json.load(open('run-2026-11-08-1531-firstseen-split.json'))
disc=json.load(open('same-owner-discards.json'))
d_owners={r.get("owner","").lower() for r in disc if isinstance(r,dict)}
out={}
for c in split['refind']:
    a=c['address']; r={"name":c['name'],"symbol":c['symbol'],"scan_mints":c['mint_count'],"scan_first_block":c['first_block'],"earlier_scan":c['earlier_scan'],"registry_bytes":c['registry_bytes_hit'],"sourcify":c['sourcify'],"free_shaped":c['free_shaped']}
    for nm,sig,dec in [("PRICE","PRICE()",u256),("MAX_SUPPLY","MAX_SUPPLY()",u256),("FREE_SUPPLY","FREE_SUPPLY()",u256),("totalSupply","totalSupply()",u256),("freeClaimed","freeClaimed()",u256),("owner","owner()",addr_of)]:
        try: r[nm]=dec(call(a,sel(sig)))
        except Exception as e: r[nm+"_error"]=str(e)[:60]
    for nm,sig in [("freeUsed_user","freeUsed(address)"),("mintedBy_user","mintedBy(address)")]:
        try: r[nm]=u256(call(a,sel(sig)+enc_addr(USER)[2:]))
        except Exception as e: r[nm+"_error"]=str(e)[:60]
    o=(r.get("owner") or "").lower()
    r["owner_in_discards"]=o in d_owners if o else None
    print(f"{r['name']}/{r['symbol']} {a[:10]} PRICE={r.get('PRICE')} MAX={r.get('MAX_SUPPLY')} FREE_SUP={r.get('FREE_SUPPLY')} freeClaimed={r.get('freeClaimed')} totalSupply={r.get('totalSupply')} userFreeUsed={r.get('freeUsed_user')} mintedBy={r.get('mintedBy_user')} discards={r['owner_in_discards']} reg={c['registry_bytes_hit']} free={c['free_shaped']}",flush=True)
    out[a]=r
# control walk-back Hoopsy
a="0xE1a438A132659Fea25AFD7712Ed7F203e62cC420"; fb=132361319; earliest=None; tot=0; errs=[]
frm=132340000
while frm<fb:
    to=min(frm+1999,fb-1)
    try:
        logs=rpc("eth_getLogs",[{"fromBlock":hex(frm),"toBlock":hex(to),"address":a,"topics":[TRANSFER,ZERO]}],timeout=15)
        for lg in (logs or []):
            b=int(lg.get("blockNumber","0x0"),16); tot+=1
            if earliest is None or b<earliest: earliest=b
    except Exception as e: errs.append(f"{frm}-{to}: {str(e)[:80]}")
    frm=to+1
print(f"CONTROL Hoopsy mints_before_window={tot} earliest={earliest} errors={errs}",flush=True)
out["_control_hoopsy_walkback"]={"mints_before_window":tot,"earliest_mint_block":earliest,"errors":errs}
json.dump(out,open('run-2026-11-08-1531-refind.json','w'),indent=1)
print("saved run-2026-11-08-1531-refind.json",flush=True)
