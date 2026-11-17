#!/usr/bin/env python3
"""Hot-leg 1639 retry: re-read only the contracts whose reads came back null
in the main 1639 run (first RPC chunks failed). Chunked <=24 calls, bsc-dataseed.
Read-only; writes only hot-leg-run-2026-11-13-1639-retry.json."""
import json, subprocess, time
from eth_hash.auto import keccak
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD=USER[2:].lower().rjust(64,"0")
def sel(sig): return "0x"+keccak(sig.encode()).hex()[:8]
def curl(url,data=None,timeout=25):
    cmd=["curl","-sS","-m",str(timeout),"-A","Mozilla/5.0"]
    if data is not None: cmd+=["-H","Content-Type: application/json","-d",data]
    cmd.append(url)
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout+5)
        return p.stdout if p.returncode==0 and p.stdout else None
    except Exception: return None
def rpc_chunked(calls,timeout=25):
    out=[]
    for i in range(0,len(calls),24):
        chunk=calls[i:i+24]
        body=curl("https://bsc-dataseed.binance.org/",data=json.dumps(chunk),timeout=timeout)
        if not body:
            out+=[(c["id"],None,"fetch-failed") for c in chunk]; continue
        try:
            resp=json.loads(body); items=resp if isinstance(resp,list) else [resp]
            by={it.get("id"):it for it in items if isinstance(it,dict)}
            for c in chunk:
                it=by.get(c["id"],{}); out.append((c["id"],it.get("result"),it.get("error")))
        except Exception as e:
            out+=[(c["id"],None,f"parse-failed: {e}") for c in chunk]
    return out
def now_wib(): return time.strftime("%Y-%m-%dT%H:%M:%S+07:00",time.gmtime(time.time()+7*3600))
t0=time.time()
PLAN=[
 ("OBFG","0x5314071bba19943f58347ba5dec423e5032a6818",[("freeMinted",False),("FREE_SUPPLY",False),("saleOpen",False),("freeAvailable",True)]),
 ("Agentx","0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",[("freeMinted",False),("FREE_CAP",False),("freeClaimed",True),("mintOpen",False)]),
 ("Zero","0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",[("freeMinted",False),("FREE_CAP",False),("mintOpen",False),("freeClaimed",True)]),
 ("OLIVER","0xad86e4d52e55709d1bda08f922853d4b109e0810",[("freeMinted",False),("FREE_MAX",False),("freeRemaining",False),("mintOpen",False),("freeClaimed",True),("freeClaimedByAgent",True)]),
 ("Pickgrid","0x7f541bcc33abed0e64455565da723e949c6f76f0",[("freeMinted",False),("FREE_CAP",False),("FREE_SUPPLY",False)]),
 ("BC1B","0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",[("freeCount",False),("FREE_CAP",False)]),
 ("MECHA","0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",[("freeClaimed",False)]),
 ("AgentMuse","0x779fa133848d23052B7345F63B3b2E5309cd13ed",[("freeClaimed",False),("FREE_SHARES",False),("openedAt",False),("bookedOf",True)]),
 ("NOTV","0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",[("totalMinted",False),("freeStart",False)]),
 ("JNTM","0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",[("freeClaimed",False),("FREE_LOTS_CAP",False),("opened",False),("freeLeft",False)]),
 ("Mossbound","0xe589A94316C68d4A4f008f841Deb7e9612445244",[("freeMinted",False),("FREE_SUPPLY",False),("freeRemaining",False),("freeAvailable",True)]),
 ("Ochre","0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D",[("freeMinted",False),("FREE_SUPPLY",False),("freeRemaining",False),("freeAvailable",True)]),
]
reqs,keys=[],[]
for name,addr,views in PLAN:
    for fn,uarg in views:
        data=sel(fn+("(address)" if uarg else "()"))+(USER_PAD if uarg else "")
        reqs.append({"jsonrpc":"2.0","id":len(reqs),"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append((name,fn+("_user" if uarg else "")))
reads={}
for cid,r,err in rpc_chunked(reqs,timeout=25):
    name,fn=keys[cid]
    v=None
    if r and r!="0x" and len(r)>=66:
        try: v=int(r[-64:],16)
        except Exception: v=None
    reads.setdefault(name,{})[fn]=v
flags={}
ax=reads.get("Agentx",{})
if ax.get("freeMinted") is not None and ax.get("FREE_CAP"):
    flags["Agentx_pct"]=round(ax["freeMinted"]/ax["FREE_CAP"]*100,1)
    flags["Agentx_70pct_crossed"]=bool(ax["freeMinted"]>ax["FREE_CAP"]*0.7)
    flags["Agentx_slot_open"]=bool(ax.get("freeClaimed_user")==0)
    flags["Agentx_mintOpen"]=ax.get("mintOpen")
ob=reads.get("OBFG",{})
if ob.get("freeMinted") is not None and ob.get("FREE_SUPPLY"):
    flags["OBFG_pct"]=round(ob["freeMinted"]/ob["FREE_SUPPLY"]*100,1)
    flags["OBFG_soldout"]=bool(ob["freeMinted"]>=ob["FREE_SUPPLY"])
    flags["OBFG_slot_open"]=bool(ob.get("freeAvailable_user")==1)
    flags["OBFG_saleOpen"]=ob.get("saleOpen")
ze=reads.get("Zero",{})
if ze.get("freeMinted") is not None and ze.get("FREE_CAP"):
    flags["Zero_pct"]=round(ze["freeMinted"]/ze["FREE_CAP"]*100,1)
    flags["Zero_slot_open"]=bool(ze.get("freeClaimed_user")==0)
ol=reads.get("OLIVER",{})
if ol.get("freeMinted") is not None and ol.get("FREE_MAX"):
    flags["OLIVER_pct"]=round(ol["freeMinted"]/ol["FREE_MAX"]*100,1)
    flags["OLIVER_freeRemaining"]=ol.get("freeRemaining")
    flags["OLIVER_soldout"]=bool((ol.get("freeRemaining") or 1)==0)
pk=reads.get("Pickgrid",{})
if pk.get("freeMinted") is not None:
    flags["Pickgrid_freeMinted"]=pk["freeMinted"]
    if pk.get("FREE_CAP"): flags["Pickgrid_pct_FREE_CAP"]=round(pk["freeMinted"]/pk["FREE_CAP"]*100,1)
bc=reads.get("BC1B",{})
if bc.get("freeCount") is not None and bc.get("FREE_CAP"):
    flags["RESUME_pct"]=round(bc["freeCount"]/bc["FREE_CAP"]*100,1)
for n in ("MECHA","AgentMuse","NOTV","JNTM","Mossbound","Ochre"):
    flags[n+"_reads"]=reads.get(n,{})
out={"run":"free-mint-hot-leg 2026-11-13 16:39 WIB retry","started_wib":now_wib(),"reads":reads,"flags":flags,"elapsed_s":round(time.time()-t0,1)}
json.dump(out,open(f"{HF}/hot-leg-2026-11-13-1639-retry.json","w"),indent=1)
print(json.dumps(out,indent=1))
