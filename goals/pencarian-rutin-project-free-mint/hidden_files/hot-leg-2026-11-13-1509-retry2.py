import json, subprocess, time
from eth_hash.auto import keccak
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD=USER[2:].lower().rjust(64,"0")
def sel(s): return "0x"+keccak(s.encode()).hex()[:8]
def single(to,data,timeout=25):
    try:
        p=subprocess.run(["curl","-sS","-m",str(timeout),"-H","Content-Type: application/json","-d",
            json.dumps({"jsonrpc":"2.0","id":0,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}),
            "https://bsc-dataseed.binance.org/"],capture_output=True,text=True,timeout=timeout+5)
        body=p.stdout or ""
        if body.lstrip().startswith("{"):
            r=json.loads(body)
            res=r.get("result")
            if res and res!="0x" and len(res)>=66:
                return int(res[-64:],16)
            return {"raw":res,"err":r.get("error")}
        return {"raw":body[:120]}
    except Exception as e:
        return {"exc":str(e)}
OCHRE="0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D"
OBFG="0x5314071bba19943f58347ba5dec423e5032a6818"
out={"retry2_wib":time.strftime("%Y-%m-%dT%H:%M:%S+07:00",time.gmtime(time.time()+7*3600)),"Ochre":{},"OBFG":{}}
for fn,u in [("freeMinted",False),("FREE_SUPPLY",False),("saleOpen",False),("isFreeOpen",False),("freeAvailable",True),("totalSupply",False)]:
    out["Ochre"][fn+("_user" if u else "")]=single(OCHRE, sel(fn+("(address)" if u else "()"))+(PAD if u else ""))
for fn,u in [("freeMinted",False),("FREE_SUPPLY",False),("freeAvailable",True)]:
    out["OBFG"][fn+("_user" if u else "")]=single(OBFG, sel(fn+("(address)" if u else "()"))+(PAD if u else ""))
oc=out["Ochre"]
if isinstance(oc.get("freeMinted"),int) and isinstance(oc.get("FREE_SUPPLY"),int):
    out["Ochre_pct"]=round(oc["freeMinted"]/oc["FREE_SUPPLY"]*100,1)
    out["Ochre_70pct_crossed"]=bool(oc["freeMinted"]>oc["FREE_SUPPLY"]*0.7)
    out["Ochre_soldout"]=bool(oc["freeMinted"]>=oc["FREE_SUPPLY"])
    out["Ochre_slot_open"]=bool(oc.get("freeAvailable_user")==1)
json.dump(out,open(f"{HF}/hot-leg-2026-11-13-1509-retry2.json","w"),indent=1)
print(json.dumps(out,indent=1))
