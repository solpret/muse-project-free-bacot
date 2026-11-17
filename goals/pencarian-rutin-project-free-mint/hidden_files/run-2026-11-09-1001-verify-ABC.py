#!/usr/bin/env python3
"""Verify Subagent-A findings fresh on-chain (curl transport; Ankr down).
Gacha Gang (A), BI NIU (C), ORDIagent (upcoming C). READ-ONLY."""
import json, subprocess, urllib.request, time
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep, payload, timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(to, data):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]})
            if isinstance(r,dict) and "result" in r and r["result"] not in (None,"0x"):
                return r["result"]
            if isinstance(r,dict) and r.get("result")=="0x": return "0x"
        except Exception: continue
    return None
def u(v):
    if v is None: return None
    try: return int(v,16)
    except Exception: return v
def dec_str(v):
    if not isinstance(v,str) or not v.startswith("0x"): return v
    try:
        ln=int(v[66:130],16); return bytes.fromhex(v[130:130+ln*2]).decode()
    except Exception: return v
def abi(addr):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"free-bacot/1.0"})
        d=json.load(urllib.request.urlopen(req,timeout=20))
        return d.get("abi",[])
    except Exception as e:
        return f"ERR {e}"
def views(addr, sigs):
    out={}
    for sig in sigs:
        fn=sig.split("(")[0]
        args=""
        if "(address)" in sig: args="00"*12+USER[2:].lower()
        elif "(address,uint256)" in sig: args="00"*12+USER[2:].lower()+"%064x"%1
        elif "(uint256)" in sig: args="%064x"%1
        out[fn]=u(call(addr, sel(sig)+args))
    return out
def head():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            return int(r["result"],16)
        except Exception: continue
    return None
res={"head":head(),"wib":"2026-11-09 ~11:0x WIB"}

# --- Gacha Gang ---
G="0x7182f4230cbd53294366a344d13ddd041c4e734c"
g_abi=abi(G)
g_fns=sorted({e.get("name") for e in g_abi if isinstance(e,dict) and e.get("type")=="function"}) if isinstance(g_abi,list) else g_abi
res["gacha_abi_fns"]=g_fns
g_sigs=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","freeLeft()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","owner()","contractURI()","name()","symbol()","balanceOf(address)","freeClaimed(address)","mintedBy(address)","freeOf(address)","costOf(address,uint256)","mintStart()","START_TIME()","startTime()","deploymentTime()","saleStart()","SALE_START()"]
res["gacha"]=views(G,[s for s in g_sigs if s.split("(")[0] in (g_fns if isinstance(g_fns,list) else [])])
for k in ("owner","contractURI","name","symbol"):
    pass
# string views decoded separately
for sig in ("name()","symbol()","contractURI()"):
    if sig.split("(")[0] in (g_fns if isinstance(g_fns,list) else []):
        res["gacha"][sig.split("(")[0]]=dec_str(call(G, sel(sig)))
ow=res["gacha"].get("owner")
if isinstance(ow,int): res["gacha"]["owner"]="0x"+"%040x"%ow

# --- BI NIU ---
B="0xE259F36D1632d61812a8E85d5736CacCA1B7c820"
b_abi=abi(B)
b_fns=sorted({e.get("name") for e in b_abi if isinstance(e,dict) and e.get("type")=="function"}) if isinstance(b_abi,list) else b_abi
res["biniu_abi_fns"]=b_fns
b_sigs=["freeSharesRemaining()","freeSharesClaimed()","totalShares()","sharesMinted()","totalMinted()","launched()","saleClockStart()","failed()","mintOpen()","saleOpen()","isOpen()","token()","pair()","AGENT_ID_REGISTRY()","agentId()","registry()","name()","symbol()","decimals()","totalSupply()","quote(address,uint256)","freeClaimed(address)","freeAvailable(address)","mintedBy(address)","balanceOf(address)"]
res["biniu"]=views(B,[s for s in b_sigs if s.split("(")[0] in (b_fns if isinstance(b_fns,list) else [])])
for k in ("token","pair","AGENT_ID_REGISTRY","agentId","registry"):
    v=res["biniu"].get(k)
    if isinstance(v,int): res["biniu"][k]="0x"+"%040x"%v
for sig in ("name()","symbol()"):
    if sig.split("(")[0] in (b_fns if isinstance(b_fns,list) else []):
        res["biniu"][sig.split("(")[0]]=dec_str(call(B, sel(sig)))

# --- ORDIagent ---
O="0x7D10516D08f3bE98aaFD9Ac4169E6Cc30D6bCeB8"
o_abi=abi(O)
o_fns=sorted({e.get("name") for e in o_abi if isinstance(e,dict) and e.get("type")=="function"}) if isinstance(o_abi,list) else o_abi
res["ordi_abi_fns"]=o_fns
o_sigs=["isOpen()","sold()","saleStart()","freeClaimed()","freeSharesRemaining()","totalShares()","token()","pair()","quote(address,uint256)","name()","symbol()","launched()","saleClockStart()","failed()","mintOpen()"]
res["ordi"]=views(O,[s for s in o_sigs if s.split("(")[0] in (o_fns if isinstance(o_fns,list) else [])])
for k in ("token","pair"):
    v=res["ordi"].get(k)
    if isinstance(v,int): res["ordi"][k]="0x"+"%040x"%v
for sig in ("name()","symbol()"):
    if sig.split("(")[0] in (o_fns if isinstance(o_fns,list) else []):
        res["ordi"][sig.split("(")[0]]=dec_str(call(O, sel(sig)))

json.dump(res, open("run-2026-11-09-1001-verify-ABC.json","w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False)[:6000])
