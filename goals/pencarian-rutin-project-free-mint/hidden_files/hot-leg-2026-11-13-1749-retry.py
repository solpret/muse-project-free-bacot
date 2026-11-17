#!/usr/bin/env python3
"""Hot-leg 1749 retry (single attempt): re-read only the change-sensitive items
that returned null in the 1749 run - Agentx (67.1% at 1739, 70pct=778),
OBFG (55.9% at 1744), Zero, OLIVER, 2e34, NEW5893, VIOLET. One batch per
endpoint, dataseed then dataseed1 fallback. Read-only."""
import json, subprocess, time
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD = USER[2:].lower().rjust(64, "0")
def sel(s): return "0x" + keccak(s.encode()).hex()[:8]
def post(url, data, timeout=25):
    try:
        p = subprocess.run(["curl","-sS","-m",str(timeout),"-A","Mozilla/5.0",
            "-H","Content-Type: application/json","-d",data,url],
            capture_output=True, text=True, timeout=timeout+5)
        return p.stdout if p.returncode==0 and p.stdout else None
    except Exception: return None
PLAN = [
 ("Agentx","0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",[("freeMinted",False),("FREE_CAP",False),("freeClaimed",True),("mintOpen",False)]),
 ("OBFG","0x5314071bba19943f58347ba5dec423e5032a6818",[("freeMinted",False),("FREE_SUPPLY",False),("saleOpen",False),("freeAvailable",True)]),
 ("Zero","0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",[("freeMinted",False),("FREE_CAP",False),("mintOpen",False),("freeClaimed",True)]),
 ("OLIVER","0xad86e4d52e55709d1bda08f922853d4b109e0810",[("freeMinted",False),("FREE_MAX",False),("freeRemaining",False),("mintOpen",False),("freeClaimed",True)]),
 ("2e34","0x2e34d33256C920C33b2a03FEC132A2c74061d5D3",[("freeMinted",False),("freeRemaining",False),("FREE_MAX",False),("mintOpen",False)]),
 ("NEW5893","0x5893199322A5300775912ebD236d8f1fEFC700Db",[("freeMinted",False),("FREE_SUPPLY",False),("saleOpen",False),("mintOpen",False),("totalSupply",False),("saleStart",False),("freeClaimed",True)]),
 ("VIOLET","0x36D9A4392E3d9ff05B6929C82D536367E9c1bc8d",[("freeMinted",False),("FREE_SUPPLY",False),("saleOpen",False),("mintOpen",False),("isFreeOpen",False),("saleStart",False),("totalSupply",False),("freeClaimed",True),("freeAvailable",True)]),
]
calls, keys = [], []
for name, addr, views in PLAN:
    for fn, u in views:
        calls.append({"jsonrpc":"2.0","id":len(calls),"method":"eth_call",
            "params":[{"to":addr,"data":sel(fn+("(address)" if u else "()"))+(PAD if u else "")},"latest"]})
        keys.append((name, fn+("_user" if u else "")))
body = post("https://bsc-dataseed.binance.org/", json.dumps(calls))
endpoint = "bsc-dataseed.binance.org"
if not body:
    body = post("https://bsc-dataseed1.binance.org/", json.dumps(calls)); endpoint = "bsc-dataseed1.binance.org"
out = {"run":"free-mint-hot-leg 2026-11-13 17:49 WIB retry","endpoint":endpoint,"started_wib":time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time()+7*3600))}
reads = {}
if body:
    try:
        resp = json.loads(body); items = resp if isinstance(resp,list) else [resp]
        by = {it.get("id"):it for it in items if isinstance(it,dict)}
        for cid,(name,fn) in enumerate(keys):
            r = by.get(cid,{}).get("result"); v=None
            if r and r!="0x" and len(r)>=66:
                try: v=int(r[-64:],16)
                except Exception: v=None
            reads.setdefault(name,{})[fn]=v
    except Exception as e: out["parse_error"]=str(e)
else: out["error"]="both endpoints fetch-failed"
out["reads"]=reads
out["reads_ok"]=sum(1 for n in reads if any(v is not None for v in reads[n].values()))
f={}
ax=reads.get("Agentx",{})
if ax.get("freeMinted") is not None and ax.get("FREE_CAP"):
    f["Agentx_pct"]=round(ax["freeMinted"]/ax["FREE_CAP"]*100,1)
    f["Agentx_70pct_crossed"]=bool(ax["freeMinted"]>ax["FREE_CAP"]*0.7)
    f["Agentx_strong_lead_legs"]=bool(f["Agentx_70pct_crossed"] and ax.get("freeClaimed_user")==0 and ax.get("mintOpen")==1)
    f["Agentx_gate"]="website_failed (reported 08:29; re-check only if 70pct crossed)"
ob=reads.get("OBFG",{})
if ob.get("freeMinted") is not None and ob.get("FREE_SUPPLY"):
    f["OBFG_pct"]=round(ob["freeMinted"]/ob["FREE_SUPPLY"]*100,1)
    f["OBFG_soldout"]=bool(ob["freeMinted"]>=ob["FREE_SUPPLY"])
    f["OBFG_slot_lost"]=bool(ob.get("freeAvailable_user")==0)
    f["OBFG_70pct_crossed"]=bool(ob["freeMinted"]>ob["FREE_SUPPLY"]*0.7)
ze=reads.get("Zero",{})
if ze.get("freeMinted") is not None and ze.get("FREE_CAP"):
    f["Zero_pct"]=round(ze["freeMinted"]/ze["FREE_CAP"]*100,1)
ol=reads.get("OLIVER",{})
if ol.get("freeMinted") is not None and ol.get("FREE_MAX"):
    f["OLIVER_pct"]=round(ol["freeMinted"]/ol["FREE_MAX"]*100,1)
    f["OLIVER_soldout"]=bool((ol.get("freeRemaining") or 1)==0)
te=reads.get("2e34",{})
if te.get("freeMinted") is not None and te.get("FREE_MAX"):
    f["2e34_pct"]=round(te["freeMinted"]/te["FREE_MAX"]*100,1)
n5=reads.get("NEW5893",{})
if n5.get("freeMinted") is not None and n5.get("FREE_SUPPLY"):
    f["NEW5893_pct"]=round(n5["freeMinted"]/n5["FREE_SUPPLY"]*100,1)
    f["NEW5893_saleStart"]=n5.get("saleStart")
    f["NEW5893_totalSupply"]=n5.get("totalSupply")
    f["NEW5893_slot_user"]=n5.get("freeClaimed_user")
vl=reads.get("VIOLET",{})
if vl.get("freeMinted") is not None and vl.get("FREE_SUPPLY"):
    f["VIOLET_pct"]=round(vl["freeMinted"]/vl["FREE_SUPPLY"]*100,1)
    f["VIOLET_totalSupply"]=vl.get("totalSupply")
    f["VIOLET_slot_user"]={"freeClaimed_user":vl.get("freeClaimed_user"),"freeAvailable_user":vl.get("freeAvailable_user")}
out["flags"]=f
json.dump(out, open(f"{HF}/hot-leg-2026-11-13-1749-retry.json","w"), indent=1)
print(json.dumps(out, indent=1))
