#!/usr/bin/env python3
"""Gate discovery Stampooor + triage RIGBYPASS + 0x8c57 + retry 6 feed ABIs. Threaded. Read-only."""
import json, subprocess, re
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return hex(n)[2:].rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def call(addr, sig, args=""):
    data=sel(sig)+args
    payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}
    for ep in EPS:
        try:
            out=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=30).stdout
            r=json.loads(out)
            if "result" in r: return r["result"]
        except Exception: continue
    return None
def call_str(addr, sig, args=""):
    raw=call(addr,sig,args)
    if not raw or raw=="0x": return None
    try:
        b=bytes.fromhex(raw[2:])
        off=int.from_bytes(b[:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception as e: return f"DECODE_ERR {str(e)[:80]} raw={raw[:120]}"
def get(url, timeout=25):
    try:
        return subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5).stdout
    except Exception as e: return f"ERR {e}"
def abi_fns(addr):
    try:
        meta=json.loads(get("https://sourcify.dev/server/v2/contract/56/"+addr+"?fields=abi"))
        abi=meta.get("abi",[])
        return sorted({e["name"] for e in abi if e.get("type")=="function"}), abi
    except Exception as e:
        return None, str(e)[:150]

ST="0x467696af8c2206B977B24081445104632dc1D459"
RB="0xe657465f0EB4B55877246026BfAe4EC75ef2E160"
E="0x8c570E4787f1dFe50bB9dE334C6f55DaA136a0BE"
tasks={}
def reg(key, fn): tasks[key]=fn
reg("stampooor_contractURI", lambda: call_str(ST,"contractURI()"))
reg("stampooor_tokenURI_1", lambda: call_str(ST,"tokenURI(uint256)",enc_u(1)))
reg("stampooor_freeAvailable_user", lambda: to_int(call(ST,"freeAvailable(address)",enc(USER))))
reg("stampooor_freeUsed_user", lambda: to_int(call(ST,"freeUsed(address)",enc(USER))))
reg("stampooor_freeMinted", lambda: to_int(call(ST,"freeMinted()")))
reg("stampooor_mintOpen", lambda: to_int(call(ST,"mintOpen()")))
reg("stampooor_owner", lambda: call(ST,"owner()"))
reg("rigbypass_totalSupply", lambda: to_int(call(RB,"totalSupply()")))
reg("rigbypass_totalMinted", lambda: to_int(call(RB,"totalMinted()")))
reg("rigbypass_freeMinted", lambda: to_int(call(RB,"freeMinted()")))
reg("rigbypass_FREE_SUPPLY", lambda: to_int(call(RB,"FREE_SUPPLY()")))
reg("rigbypass_MAX_SUPPLY", lambda: to_int(call(RB,"MAX_SUPPLY()")))
reg("rigbypass_mintOpen", lambda: to_int(call(RB,"mintOpen()")))
reg("rigbypass_balanceOf_user", lambda: to_int(call(RB,"balanceOf(address)",enc(USER))))
reg("rigbypass_contractURI", lambda: call_str(RB,"contractURI()"))
reg("rigbypass_mintStart", lambda: to_int(call(RB,"mintStart()")))
reg("e8c57_totalSupply", lambda: to_int(call(E,"totalSupply()")))
reg("e8c57_totalMinted", lambda: to_int(call(E,"totalMinted()")))
reg("e8c57_freeMinted", lambda: to_int(call(E,"freeMinted()")))
out={"started_wib":"2026-11-11 19:01 WIB"}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs={k: ex.submit(fn) for k,fn in tasks.items()}
    for k,f in futs.items():
        try: out[k]=f.result(timeout=120)
        except Exception as e: out[k]=f"ERR {e}"
fns, abi = abi_fns(ST)
out["stampooor_abi_fns"]=fns
out["stampooor_abi_free_fns"]=[f for f in (fns or []) if "free" in f.lower() or "mint" in f.lower()]
if abi and isinstance(abi,list):
    out["stampooor_mint_fn_sigs"]=[{"name":e["name"],"inputs":[(i.get("name"),i.get("type")) for i in e.get("inputs",[])]} for e in abi if e.get("type")=="function" and ("mint" in e["name"].lower() or "free" in e["name"].lower())]
try:
    src=get("https://sourcify.dev/server/v2/contract/56/"+ST+"?fields=sources")
    urls=sorted(set(re.findall(r"https?://[A-Za-z0-9\-._~:/?#@!$&'()*+,;=%]+", src)))
    out["stampooor_sourcify_urls"]=[u for u in urls if "sourcify" not in u][:20]
except Exception as e:
    out["stampooor_sourcify_error"]=str(e)[:150]
fns_rb, _ = abi_fns(RB)
out["rigbypass_abi_fns"]=fns_rb
out["rigbypass_registry"]=[f for f in (fns_rb or []) if "agent" in f.lower() or "registry" in f.lower()]
site=get("https://ribgypass.pages.dev/")
out["rigbypass_site_bytes"]=len(site)
out["rigbypass_site_prints_contract"]=("0xe657465f0EB4B55877246026BfAe4EC75ef2E160" in site)
fns_e, _ = abi_fns(E)
out["e8c57_abi_fns"]=fns_e
# retry 6 feed ABIs
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape(a):
    try:
        meta=json.loads(get("https://sourcify.dev/server/v2/contract/56/"+a+"?fields=abi"))
        abi2=meta.get("abi",[])
        fmap={}
        for e in abi2:
            if e.get("type")=="function": fmap.setdefault(e["name"],[]).append(e)
        names=set(fmap)
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views=sorted(names & FREE_VIEWS)
        agent_ref=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree="mintFree" in fmap and any(len(e.get("inputs",[]))==0 for e in fmap["mintFree"])
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        is_nft=bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
        free_mint_fn=bool(names & {"freeMint","mintFree","claimFree","mint"}) or any(n.lower().startswith("freemint") for n in names)
        return {"address":a,"S1":s1,"S2":s2,"early_shape":bool(is_nft and (agent_ref or free_mint_fn)),"has_mint":has_mint,"has_quote":has_quote,"free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,"is_nft":is_nft,"fn_count":len(names)}
    except Exception as ex:
        return {"address":a,"error":f"{type(ex).__name__}: {str(ex)[:120]}"}
retry_addrs=['0x503A87131aa768b55EC7745107422C9BCe356eb8','0x086F1eF1efb5aF2a066e5d8bdBB19429D3c3675A','0xbd1a0Bf361C6B369979028a3FA98adDe3C9C4eEc','0x1E48004C57C3D4fd4dfCf73F05B00677AbaFe2C8','0x9e95Da84f1bcc8E5570DAAc99A37EB3f95270904','0xc20EfD28341dB67C816B6adb3fb9B66820836294']
with ThreadPoolExecutor(max_workers=6) as ex:
    out["feed_shape_retry"]=list(ex.map(shape, retry_addrs))
# Boltbook grep for Stampooor
import glob
for f in glob.glob(BASE+"run-2026-11-11-1901-boltbook-*.html"):
    try:
        html=open(f,errors="replace").read()
        out["boltbook_stampooor_"+f.split("boltbook-")[-1]]=("stampooor" in html.lower())
    except Exception as e:
        out["boltbook_"+f]="ERR "+str(e)[:80]
json.dump(out,open(BASE+"run-2026-11-11-1901-gate-stampooor.json","w"),indent=1)
print(json.dumps(out,indent=1))
