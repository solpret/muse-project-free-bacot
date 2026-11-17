import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
d=json.load(open(BASE+"hot-leg-run-2026-11-10-1324-leg4.json"))
base=json.load(open(BASE+"hot-leg-run-2026-11-10-1255-leg4.json"))
base_items=base.get("items") or base.get("leg4") or {}
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def calldata(field):
    if field.endswith("_user1"): return sel(f"{field[:-6]}(address,uint256)")+enc_addr(USER)+enc_uint(1)
    if field.endswith("_user"): return sel(f"{field[:-5]}(address)")+enc_addr(USER)
    return sel(f"{field}()")
def post(ep,payload):
    p=subprocess.run(["curl","-s","--max-time","15","-X","POST",ep,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True,timeout=20)
    try: return json.loads(p.stdout)
    except Exception: return {"_err":p.stdout[:200]+p.stderr[:200]}
jobs=[]
for rf in d["read_failed"]:
    name,field=rf["item"],rf["field"]
    addr=d["items"][name]["address"]
    cd=calldata(field)
    if cd: jobs.append((name,field,addr,cd))
print("retry jobs:",len(jobs))
ep="https://bsc-dataseed1.binance.org/"
recovered=0; still=[]
for i in range(0,len(jobs),25):
    chunk=jobs[i:i+25]
    payload=json.dumps([{"jsonrpc":"2.0","id":j,"method":"eth_call","params":[{"to":to,"data":data},"latest"]} for j,(_,_,to,data) in enumerate(chunk)])
    resp=post(ep,payload)
    if isinstance(resp,dict): resp=[resp] if "_err" not in resp else []
    for j,item in enumerate(resp):
        n,f,_,_=chunk[j]
        ok=False
        if isinstance(item,dict) and "result" in item and isinstance(item["result"],str):
            try:
                v=int(item["result"],16)
                d["items"][n][f]=v; recovered+=1; ok=True
                bv=(base_items.get(n) or {}).get(f)
                if bv is not None and v!=bv: d["diffs"].append({"item":n,"field":f,"was":bv,"now":v,"via":"dataseed-retry"})
            except Exception: pass
        if not ok: still.append({"item":n,"field":f})
d["read_failed"]=still
d["retry"]={"ep":ep,"recovered":recovered,"still_failed":len(still)}
json.dump(d,open(BASE+"hot-leg-run-2026-11-10-1324-leg4.json","w"),indent=1)
print("recovered:",recovered,"still_failed:",len(still))
print("new diffs:",[x for x in d["diffs"] if x.get("via")=="dataseed-retry"])
