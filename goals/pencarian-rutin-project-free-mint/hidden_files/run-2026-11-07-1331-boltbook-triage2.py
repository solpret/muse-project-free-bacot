#!/usr/bin/env python3
"""Parent triage run 1331 v2: per-view individual calls (one revert must not
kill the batch). Read-only; writes run-2026-11-07-1331-boltbook-triage2.json."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NEW={
 "Kora Agent":"0x67251c3b2830728316f3a0816df57fda5dc959bf",
 "Nero Agent":"0x26929b87f80b7f126fa56dc26e59a774990641f1",
 "Luma Agent":"0xf198c48534c5853ee3cb3be62a990d3395a73358",
 "Chipagent":"0xc3d831db5f018ab9977724352ec773ba0ac3ae4a",
}
BRIDGE={
 "Agentdragon":"0x2df7435f5bce0577bee213e13da68313c74d7d0b",
 "Wuyuhive":"0x250e800025a9a7861970e253bab6975a57f80567",
}
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
    try: return int(v,16)
    except Exception: return None
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","freeClaimed(address)","balanceOf(address)"]
def call_view(addr,sig,block="latest"):
    data=sel(sig)+(enc(USER) if "(address)" in sig else "")
    try:
        r=race("eth_call",[{"to":addr,"data":data},block])
        if isinstance(r,str): return ti(r)
        if isinstance(r,dict) and "result" in r: return ti(r["result"])
        return f"UNEXPECTED:{str(r)[:80]}"
    except Exception as e:
        return f"ERR:{type(e).__name__}"
head=int(race("eth_blockNumber",[]),16)
print("HEAD",head,flush=True)
out={"head":head,"contracts":{}}
for name,addr in {**NEW,**BRIDGE}.items():
    d={}
    for sig in VIEWS:
        d[sig.split("(")[0]+("_user" if "(address)" in sig else "")]=call_view(addr,sig)
    out["contracts"][name]={"address":addr,"views":d}
    print(name,json.dumps(d),flush=True)
for name,addr in NEW.items():
    brack={}
    for lv in [20000,40000,80000,160000,320000,384000]:
        brack[lv]=call_view(addr,"totalSupply()",hex(head-lv))
    out["contracts"][name]["ageBracket"]=brack
    print(name,"BRACKET",json.dumps(brack),flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-07-1331-boltbook-triage2.json","w"),indent=1)
print("TRIAGE2 DONE",flush=True)
