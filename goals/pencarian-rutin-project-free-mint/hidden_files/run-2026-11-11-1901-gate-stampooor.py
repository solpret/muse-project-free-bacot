#!/usr/bin/env python3
"""Gate discovery for Stampooor (strong-lead cross 841/1200) + triage RIGBYPASS + 0x8c57 + retry 6 failed feed ABIs.
Read-only. Writes run-2026-11-11-1901-gate-stampooor.json."""
import json, subprocess, time, base64, re
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
    except Exception as e: return f"DECODE_ERR {e} raw={raw[:200]}"
def get(url, timeout=25):
    try:
        out=subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5).stdout
        return out
    except Exception as e: return f"ERR {e}"

out={"started_wib":"2026-11-11 19:01 WIB"}
ST="0x467696af8c2206B977B24081445104632dc1D459"
# --- Stampooor gate: contractURI / tokenURI / slot ---
out["stampooor_contractURI"]=call_str(ST,"contractURI()")
out["stampooor_tokenURI_1"]=call_str(ST,"tokenURI(uint256)",enc_u(1))
out["stampooor_tokenURI_841"]=call_str(ST,"tokenURI(uint256)",enc_u(841))
out["stampooor_freeAvailable_user"]=to_int(call(ST,"freeAvailable(address)",enc(USER)))
out["stampooor_freeUsed_user"]=to_int(call(ST,"freeUsed(address)",enc(USER)))
out["stampooor_freeMinted"]=to_int(call(ST,"freeMinted()"))
out["stampooor_totalMinted"]=to_int(call(ST,"totalMinted()"))
out["stampooor_mintOpen"]=to_int(call(ST,"mintOpen()"))
out["stampooor_owner"]=call(ST,"owner()")
out["stampooor_mintStart"]=to_int(call(ST,"mintStart()"))
# Sourcify ABI + sources grep for URLs
try:
    meta=json.loads(get("https://sourcify.dev/server/v2/contract/56/"+ST+"?fields=abi"))
    abi=meta.get("abi",[])
    fns=sorted({e["name"] for e in abi if e.get("type")=="function"})
    out["stampooor_abi_fns"]=fns
    out["stampooor_abi_free_fns"]=[f for f in fns if "free" in f.lower() or "mint" in f.lower()]
except Exception as e:
    out["stampooor_abi_error"]=str(e)[:200]
try:
    src=get("https://sourcify.dev/server/v2/contract/56/"+ST+"?fields=sources")
    urls=sorted(set(re.findall(r"https?://[A-Za-z0-9\-._~:/?#@!$&'()*+,;=%]+", src)))
    out["stampooor_sourcify_urls"]=[u for u in urls if not u.startswith("https://sourcify")][:20]
except Exception as e:
    out["stampooor_sourcify_error"]=str(e)[:200]
# Boltbook html grep
for f in ["run-2026-11-11-1901-boltbook-en.html","run-2026-11-11-1901-boltbook-zh.html"]:
    try:
        html=open(BASE+f,errors="replace").read()
        out[f"boltbook_stampooor_{f.split('-')[-1]}"]="Stampooor" in html or "stampooor" in html.lower()
    except Exception as e:
        out[f"boltbook_stampooor_{f}"]="no file: "+str(e)[:100]
# --- RIGBYPASS ---
RB="0xe657465f0EB4B55877246026BfAe4EC75ef2E160"
out["rigbypass_totalSupply"]=to_int(call(RB,"totalSupply()"))
out["rigbypass_totalMinted"]=to_int(call(RB,"totalMinted()"))
out["rigbypass_freeMinted"]=to_int(call(RB,"freeMinted()"))
out["rigbypass_freeClaimed"]=to_int(call(RB,"freeClaimed()"))
out["rigbypass_FREE_SUPPLY"]=to_int(call(RB,"FREE_SUPPLY()"))
out["rigbypass_MAX_SUPPLY"]=to_int(call(RB,"MAX_SUPPLY()"))
out["rigbypass_mintOpen"]=to_int(call(RB,"mintOpen()"))
out["rigbypass_balanceOf_user"]=to_int(call(RB,"balanceOf(address)",enc(USER)))
out["rigbypass_freeAvailable_user"]=to_int(call(RB,"freeAvailable(address)",enc(USER)))
out["rigbypass_contractURI"]=call_str(RB,"contractURI()")
out["rigbypass_mintStart"]=to_int(call(RB,"mintStart()"))
try:
    meta=json.loads(get("https://sourcify.dev/server/v2/contract/56/"+RB+"?fields=abi"))
    abi=meta.get("abi",[])
    fns=sorted({e["name"] for e in abi if e.get("type")=="function"})
    out["rigbypass_abi_fns"]=fns
    out["rigbypass_registry"]=[f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
except Exception as e:
    out["rigbypass_abi_error"]=str(e)[:200]
site=get("https://ribgypass.pages.dev/")
out["rigbypass_site_bytes"]=len(site)
out["rigbypass_site_prints_contract"]=("0xe657465f0EB4B55877246026BfAe4EC75ef2E160" in site) or ("0xe657465f0eb4b55877246026bfae4ec75ef2e160" in site.lower())
out["rigbypass_site_prints_token"]=("0xbC624D074fcFEe8B2EE42fdeA736d1ddFfEfb3A2" in site) or ("0xbc624d074fcfee8b2ee42fdea736d1ddffe fb3a2".replace(" ","") in site.lower())
# --- 0x8c57 early-shape triage ---
E="0x8c570E4787f1dFe50bB9dE334C6f55DaA136a0BE"
out["e8c57_totalSupply"]=to_int(call(E,"totalSupply()"))
out["e8c57_totalMinted"]=to_int(call(E,"totalMinted()"))
out["e8c57_freeMinted"]=to_int(call(E,"freeMinted()"))
out["e8c57_FREE_SUPPLY"]=to_int(call(E,"FREE_SUPPLY()"))
try:
    meta=json.loads(get("https://sourcify.dev/server/v2/contract/56/"+E+"?fields=abi"))
    abi=meta.get("abi",[])
    fns=sorted({e["name"] for e in abi if e.get("type")=="function"})
    out["e8c57_abi_fns"]=fns
except Exception as e:
    out["e8c57_abi_error"]=str(e)[:200]
# --- retry 6 failed feed ABIs via curl ---
retry_addrs=['0x503A87131aa768b55EC7745107422C9BCe356eb8','0x086F1eF1efb5aF2a066e5d8bdBB19429D3c3675A','0xbd1a0Bf361C6B369979028a3FA98adDe3C9C4eEc','0x1E48004C57C3D4fd4dfCf73F05B00677AbaFe2C8','0x9e95Da84f1bcc8E5570DAAc99A37EB3f95270904','0xc20EfD28341dB67C816B6adb3fb9B66820836294']
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
shapes=[]
for a in retry_addrs:
    try:
        meta=json.loads(get("https://sourcify.dev/server/v2/contract/56/"+a+"?fields=abi"))
        abi=meta.get("abi",[])
        fns={}
        for e in abi:
            if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
        names=set(fns)
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views=sorted(names & FREE_VIEWS)
        agent_ref=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        is_nft=bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
        free_mint_fn=bool(names & {"freeMint","mintFree","claimFree","mint"}) or any(n.lower().startswith("freemint") for n in names)
        shapes.append({"address":a,"S1":s1,"S2":s2,"early_shape":bool(is_nft and (agent_ref or free_mint_fn)),"has_mint":has_mint,"has_quote":has_quote,"free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,"is_nft":is_nft,"fn_count":len(names)})
    except Exception as ex:
        shapes.append({"address":a,"error":f"{type(ex).__name__}: {str(ex)[:120]}"})
out["feed_shape_retry"]=shapes
json.dump(out,open(BASE+"run-2026-11-11-1901-gate-stampooor.json","w"),indent=1)
print(json.dumps(out,indent=1)[:9000])
