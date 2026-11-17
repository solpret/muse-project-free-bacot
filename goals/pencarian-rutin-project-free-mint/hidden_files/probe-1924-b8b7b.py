#!/usr/bin/env python3
"""Follow-up: 0xB8b7 launch/free-pool views + eth_getCode for 4 Boltbook addrs + snapshot membership."""
import json, subprocess, datetime
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EP = "https://bsc-dataseed.binance.org/"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post(payload, timeout=60):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+10).stdout
    return json.loads(out)
HIT="0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb"
views=[("mintOpenTimestamp","mintOpenTimestamp()",[]),("freeRemaining","freeRemaining()",[]),
       ("price","price()",[]),("maxSupply","maxSupply()",[]),("mintPaused","mintPaused()",[]),
       ("freeBlock","freeBlock()",[]),("snapshotTime","snapshotTime()",[]),("tierSizes","tierSizes()",[])]
calls=[]; meta=[]
for key,sig,args in views:
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":HIT,"data":sel(sig)},"latest"]})
    meta.append(key)
res=post(calls)
vals={}
for it,key in zip(res,meta):
    vals[key]=to_int(it["result"][:66]) if isinstance(it,dict) and it.get("result") not in (None,"0x") and len(it["result"])>=66 else (it.get("result") if isinstance(it,dict) else None)
out={"hit_extra":vals}
mts=vals.get("mintOpenTimestamp")
if isinstance(mts,int) and mts>0:
    out["mintOpenTimestamp_utc"]=datetime.datetime.utcfromtimestamp(mts).isoformat()+"Z"
    out["mintOpenTimestamp_wib"]=(datetime.datetime.utcfromtimestamp(mts)+datetime.timedelta(hours=7)).isoformat()+"+07:00"
# code checks for boltbook addrs
bb=["0x23c1bf5333de12bc43ada5fb58aef188929cc139","0x44a6c3b3769d7526eabe1f5e631dbd35a7a7874c",
    "0x6dd26c79f9c570c48b93370ec73de382c243f19f","0xedc6a6891ebf3dc05a6d256e960c7d08efa66617"]
codes=post([{"jsonrpc":"2.0","id":i+1,"method":"eth_getCode","params":[a,"latest"]} for i,a in enumerate(bb)])
out["boltbook_code"]={a:(len(c.get("result",""))-2)//2 if isinstance(c,dict) and c.get("result") else None for a,c in zip(bb,codes)}
# snapshot membership (case-insensitive) for all 5
import re
def collect(obj,acc):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if isinstance(k,str) and re.fullmatch(r"0x[0-9a-fA-F]{40}",k): acc.add(k.lower())
            collect(v,acc)
    elif isinstance(obj,list):
        for v in obj: collect(v,acc)
    elif isinstance(obj,str) and re.fullmatch(r"0x[0-9a-fA-F]{40}",obj): acc.add(obj.lower())
snap=set()
try:
    snapj=json.load(open(BASE+"onchain-snapshot.json")); collect(snapj,snap)
except Exception as e: out["snapshot_error"]=str(e)[:150]
out["snapshot_addrs"]=len(snap)
out["in_snapshot"]={a:(a.lower() in snap) for a in [HIT]+bb}
# also check hot-leg-reported for HIT
try:
    rep=json.load(open(BASE+"hot-leg-reported.json"))
    out["hit_in_hotleg_reported"]=HIT in rep or HIT.lower() in {k.lower() for k in rep}
except Exception as e: out["reported_error"]=str(e)[:150]
json.dump(out,open(BASE+"probe-1924-b8b7b.json","w"),indent=1)
print(json.dumps(out,indent=1))
