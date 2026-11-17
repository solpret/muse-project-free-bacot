import json, re, subprocess, time
from eth_hash.auto import keccak
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OCHRE="0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D"
def sel(s): return "0x"+keccak(s.encode()).hex()[:8]
def curl(url,data=None,timeout=15):
    cmd=["curl","-sS","-m",str(timeout),"-A","Mozilla/5.0"]
    if data is not None: cmd+=["-H","Content-Type: application/json","-d",data]
    cmd.append(url)
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout+5)
        return p.stdout if p.returncode==0 and p.stdout else None
    except Exception: return None
gate={"checked_wib":time.strftime("%Y-%m-%dT%H:%M:%S+07:00",time.gmtime(time.time()+7*3600)),
      "trigger":"Ochre strong-lead legs met (165/210=78.6%, age verified saleStart 14:51:07 WIB, slot open)"}
# (H) contractURI single call
raw=curl("https://bsc-dataseed.binance.org/",data=json.dumps({"jsonrpc":"2.0","id":0,"method":"eth_call","params":[{"to":OCHRE,"data":sel("contractURI()")},"latest"]}),timeout=25)
try:
    res=json.loads(raw).get("result") if raw and raw.lstrip().startswith("{") else None
    gate["contractURI_raw_head"]=(res or "")[:200]
    if res and len(res)>=130:
        b=bytes.fromhex(res[2:]); ln=int.from_bytes(b[64:96],"big")
        gate["contractURI"]=b[96:96+ln].decode("utf-8","replace")
except Exception as e:
    gate["contractURI_error"]=str(e)
# (C) Sourcify metadata URLs
meta=curl(f"https://sourcify.dev/server/v2/contract/56/{OCHRE}/metadata.json",timeout=15)
gate["sourcify_metadata_urls"]=sorted(set(re.findall(r"https?://[^\s\"'<>]+",meta or "")))[:10] if meta else []
# (D) candidate sites
cands=["https://ochremedallion.vercel.app/","https://ochre-medallion.vercel.app/",
       "https://ochremedallion.pages.dev/","https://ochre-medallion.pages.dev/",
       "https://ochremedallion.deed.page/","https://ochremedallion.surge.sh/"]
for u in gate.get("sourcify_metadata_urls",[])[:3]:
    if u not in cands: cands.append(u)
# also any URL inside contractURI
if gate.get("contractURI"):
    for u in re.findall(r"https?://[^\s\"'<>]+",gate["contractURI"]):
        if u not in cands: cands.append(u)
for site in cands:
    body=curl(site,timeout=10)
    gate[site]="fetch-failed" if body is None else {"bytes":len(body),
        "prints_contract": OCHRE.lower() in body.lower() or OCHRE[2:].lower() in body.lower()}
gate["gate_verified"]=bool(any(isinstance(v,dict) and v.get("prints_contract") for v in gate.values()))
json.dump(gate,open(f"{HF}/hot-leg-2026-11-13-1509-ochre-gate.json","w"),indent=1)
print(json.dumps(gate,indent=1))
