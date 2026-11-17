import json, subprocess, time
from eth_hash.auto import keccak
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD=USER[2:].lower().rjust(64,"0")
def sel(s): return "0x"+keccak(s.encode()).hex()[:8]
PLAN=[
 ("OBFG","0x5314071bba19943f58347ba5dec423e5032a6818",[("freeMinted",False),("FREE_SUPPLY",False),("saleOpen",False),("freeAvailable",True)]),
 ("Mossbound","0xe589A94316C68d4A4f008f841Deb7e9612445244",[("freeMinted",False),("FREE_SUPPLY",False),("saleOpen",False),("mintOpen",False),("saleStart",False),("isFreeOpen",False),("freeRemaining",False),("freeAvailable",True)]),
 ("Ochre","0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D",[("freeMinted",False),("FREE_SUPPLY",False),("saleOpen",False),("mintOpen",False),("isFreeOpen",False),("saleStart",False),("totalSupply",False),("freeClaimed",True),("freeAvailable",True)]),
 ("JNTM","0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",[("freeClaimed",False),("FREE_LOTS_CAP",False),("opened",False)]),
]
reqs,keys=[],[]
for name,addr,views in PLAN:
    for fn,u in views:
        reqs.append({"jsonrpc":"2.0","id":len(reqs),"method":"eth_call","params":[{"to":addr,"data":sel(fn+("(address)" if u else "()"))+(PAD if u else "")},"latest"]})
        keys.append((name,fn+("_user" if u else "")))
body=subprocess.run(["curl","-sS","-m","30","-H","Content-Type: application/json","-d",json.dumps(reqs),"https://bsc-dataseed.binance.org/"],capture_output=True,text=True,timeout=40).stdout
out={"retry_wib":time.strftime("%Y-%m-%dT%H:%M:%S+07:00",time.gmtime(time.time()+7*3600)),"reads":{},"raw_ok":bool(body)}
try:
    items=json.loads(body); by={it.get("id"):it for it in items if isinstance(it,dict)}
    for cid,(name,fn) in enumerate(keys):
        it=by.get(cid,{}); r=it.get("result")
        v=None
        if r and r!="0x" and len(r)>=66:
            try: v=int(r[-64:],16)
            except Exception: v=None
        out["reads"].setdefault(name,{})[fn]=v
        out["reads"][name][fn+"_err"]=it.get("error")
except Exception as e:
    out["parse_error"]=str(e)
json.dump(out,open(f"{HF}/hot-leg-2026-11-13-1509-retry.json","w"),indent=1)
print(json.dumps(out,indent=1))
