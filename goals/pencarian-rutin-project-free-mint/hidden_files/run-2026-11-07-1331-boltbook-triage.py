#!/usr/bin/env python3
"""Parent triage run 1331: Boltbook new contracts (Kora, Nero, Luma, Chipagent)
+ fresh reads for bridge Agentdragon/Wuyuhive (age-exclusion record).
Read-only; writes run-2026-11-07-1331-boltbook-triage.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch, race
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
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","freeClaimed(address)","balanceOf(address)","name()","symbol()"]
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
def read_views(addr):
    calls=[]; keys=[]
    for sig in VIEWS:
        base=sig.split("(")[0]
        if "(address)" in sig:
            data=sel(sig)+enc(USER); key=base+"_user"
        else:
            data=sel(sig); key=base
        calls.append(("eth_call",[{"to":addr,"data":data},"latest"])); keys.append(key)
    for ep in EPS:
        try:
            res=batch(calls, endpoint=ep, timeout=10)
            out={}
            for k,r in zip(keys,res):
                v=r.get("result") if isinstance(r,dict) else None
                if k in ("name","symbol"):
                    out[k]=v
                else:
                    out[k]=ti(v) if v else None
            return out, ep
        except Exception as e:
            last=e; continue
    return {"error":str(last)}, None
head=int(race("eth_blockNumber",[]),16)
print("HEAD",head,flush=True)
out={"head":head,"contracts":{}}
for name,addr in {**NEW,**BRIDGE}.items():
    d,ep=read_views(addr)
    out["contracts"][name]={"address":addr,"views":d,"endpoint":ep}
    print(name,json.dumps(d),flush=True)
# age bracket: totalSupply at historical blocks for the 4 NEW ones
# 48h ~ 384000 blocks at 0.45s/block
levels=[20000,40000,80000,160000,320000,384000]
ts_sel=sel("totalSupply()")
for name,addr in NEW.items():
    brack={}
    for lv in levels:
        blk=head-lv
        ok=False
        for ep in EPS:
            try:
                res=batch([("eth_call",[{"to":addr,"data":ts_sel},hex(blk)])],endpoint=ep,timeout=10)
                r=res[0]
                if isinstance(r,dict) and "result" in r:
                    brack[lv]=ti(r["result"]); ok=True; break
            except Exception:
                continue
        if not ok: brack[lv]=None
    out["contracts"][name]["ageBracket"]=brack
    print(name,"BRACKET",json.dumps(brack),flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-07-1331-boltbook-triage.json","w"),indent=1)
print("TRIAGE DONE",flush=True)
