import sys, json, time, subprocess, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def rpc(m,p,timeout=10):
    last=None
    for ep in EPS:
        try: return _single(ep,m,p,timeout,retries=0)
        except Exception as e: last=e
    raise last
def keccak_sel(sig):
    from Crypto.Hash import keccak
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def call(addr, sig, args_hex=""):
    sel=keccak_sel(sig); data=sel+args_hex
    try:
        out=rpc("eth_call",[{"to":addr,"data":data},"latest"])
        return out
    except Exception as e:
        return f"ERR:{e}"
def dec_int(h):
    try:
        if isinstance(h,str) and h.startswith("0x") and len(h)>=66: return int(h[2:66],16)
    except Exception: pass
    return None
def dec_bool(h):
    v=dec_int(h); return None if v is None else bool(v)
def dec_addr(h):
    try:
        if isinstance(h,str) and h.startswith("0x") and len(h)>=66: return "0x"+h[-40:]
    except Exception: pass
    return None
def sourcify(addr):
    # curl first (urllib IncompleteRead seen in scan), fallback urllib
    for attempt in range(2):
        try:
            r=subprocess.run(["curl","-sS","--max-time","25",f"https://sourcify.dev/server/v2/contract/56/{addr}"],capture_output=True,text=True,timeout=40)
            if r.returncode==0 and r.stdout.strip():
                d=json.loads(r.stdout)
                return ("verified", d.get("abi"), d.get("creationMatch"), d.get("match"), d)
            return (f"curl_rc{ r.returncode}:{r.stderr[:100]}", None, None, None, None)
        except Exception as e:
            print("sourcify curl err",e,flush=True)
    return ("error",None,None,None,None)
first=json.load(open('run-2026-11-06-1501-firstseen.json'))
disc=json.load(open('same-owner-discards.json'))
disc_owners={d.get('owner','').lower() for d in disc}
disc_contracts={d.get('contract','').lower() for d in disc}
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
out={}
for c in first:
    addr=c['address']; print("="*100,flush=True); print(addr,c['name'],c['symbol'],"first_block",c['first_block'],flush=True)
    st,abi,cm,match,raw=sourcify(addr)
    print("sourcify:",st,"match:",match,"creationMatch:",cm,flush=True)
    verified_at=None
    if raw:
        # v2 response: standardJson / metadata may carry verifiedAt? print keys
        print("sourcify keys:",list(raw.keys()),flush=True)
        md=raw.get("metadata") or {}
        print("metadata keys:",list(md.keys()) if isinstance(md,dict) else md,flush=True)
    fns=[]
    if isinstance(abi,list):
        fns=[f.get("name") for f in abi if f.get("type")=="function"]
    print("fn count:",len(fns),"fns:",fns,flush=True)
    free=[f for f in fns if "free" in f.lower() and not f.lower().startswith("freeze")]
    print("free funcs:",free,flush=True)
    owner=dec_addr(call(addr,"owner()"))
    print("owner:",owner,"in_discards:",(owner or "").lower() in disc_owners,"contract_in_discards:",addr.lower() in disc_contracts,flush=True)
    views={}
    for sig,label,dec in [("PRICE()","PRICE",dec_int),("MAX_SUPPLY()","MAX_SUPPLY",dec_int),("totalSupply()","totalSupply",dec_int),("totalMinted()","totalMinted",dec_int),("mintOpen()","mintOpen",dec_bool),("AGENT_REGISTRY()","AGENT_REGISTRY",dec_addr),("AGENT_ID_REGISTRY()","AGENT_ID_REGISTRY",dec_addr),("agentRegistry()","agentRegistry",dec_addr),("freeSupply()","freeSupply",dec_int),("freeLeft()","freeLeft",dec_int),("freeClaimed()","freeClaimed",dec_int),("freeMinted()","freeMinted",dec_int),("FREE_SUPPLY()","FREE_SUPPLY",dec_int),("FREE_SLOTS()","FREE_SLOTS",dec_int),("spotsLeft()","spotsLeft",dec_int),("launched()","launched",dec_bool)]:
        v=call(addr,sig)
        views[label]=dec(v) if not (isinstance(v,str) and v.startswith("ERR")) else v
    print("views:",views,flush=True)
    # quote checks: quote(uint256) with arg 1
    q1=call(addr,"quote(uint256)","0"*63+"1")
    print("quote(1):",dec_int(q1) if isinstance(q1,str) else q1,flush=True)
    out[addr]={"name":c['name'],"symbol":c['symbol'],"kind":c['kind'],"mint_count":c['mint_count'],"distinct_minters":c['distinct_minters'],"first_block":c['first_block'],"registry_bytes_hit":c['registry_bytes_hit'],"scan_sourcify":c['sourcify'],"sourcify_retry":st,"fn_count":len(fns),"fns":fns,"free_funcs":free,"owner":owner,"owner_in_discards":(owner or "").lower() in disc_owners,"contract_in_discards":addr.lower() in disc_contracts,"views":views,"quote1":dec_int(q1) if isinstance(q1,str) else q1}
json.dump(out,open('run-2026-11-06-1501-triage-detail.json','w'),indent=1)
print("WROTE triage-detail",flush=True)
