import json, urllib.request, base64
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,sig,arg=""):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":sel(sig)+arg},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:80]}
            v=out["result"]
            if not v or v=="0x": return None
            return v
        except Exception: continue
    return {"error":"rpc-fail"}
def dec_str(v):
    if not isinstance(v,str) or len(v)<130: return v
    try:
        h=v[2:]; off=int(h[:64],16); ln=int(h[off*2:off*2+64],16)
        return bytes.fromhex(h[off*2+64:off*2+64+ln*2]).decode(errors="replace")
    except Exception: return v
def fetch(url):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=20) as r: return r.read().decode(errors="replace")
    except Exception as e: return {"error":str(e)[:120]}
CTS={"Layerloom":"0x1B72ceC52A74537b06F713FCebA0e491f53679aE","Tumblebots":"0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17"}
res={}
for name,addr in CTS.items():
    d={}
    d["contractURI_raw"]=call(addr,"contractURI()")
    d["contractURI"]=dec_str(d["contractURI_raw"]) if isinstance(d["contractURI_raw"],str) else d["contractURI_raw"]
    d["tokenURI_1_raw"]=call(addr,"tokenURI(uint256)","0"*63+"1")
    tu=dec_str(d["tokenURI_1_raw"]) if isinstance(d["tokenURI_1_raw"],str) else d["tokenURI_1_raw"]
    d["tokenURI_1"]=tu
    if isinstance(tu,str) and tu.startswith("data:application/json;base64,"):
        try: d["tokenURI_1_decoded"]=base64.b64decode(tu.split(",",1)[1]).decode(errors="replace")
        except Exception as e: d["tokenURI_1_decoded"]={"error":str(e)[:80]}
    d["owner_raw"]=call(addr,"owner()")
    if isinstance(d["owner_raw"],str) and len(d["owner_raw"])==66:
        d["owner"]="0x"+d["owner_raw"][26:]
    # Sourcify metadata + source
    meta=fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=metadata,creationMatch,runtimeMatch")
    d["sourcify"]=meta if isinstance(meta,dict) else meta[:3000]
    if isinstance(meta,str):
        try:
            mj=json.loads(meta)
            md=json.loads(mj.get("stdJson",{}).get("metadata","{}")) if isinstance(mj,dict) else {}
            d["sourcify_meta_urls"]=str(md)[:1500]
            src=fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}/source")
            d["sourcify_source_urls"]=[l for l in (src if isinstance(src,str) else "") .splitlines() if "http" in l.lower()][:10]
            abi=mj.get("abi") if isinstance(mj,dict) else None
            if abi:
                fns=[f.get("name") for f in abi if f.get("type")=="function"]
                d["abi_functions"]=fns
                d["abi_site_functions"]=[f for f in fns if any(w in f.lower() for w in ["site","url","domain","website","external","link"])]
        except Exception as e:
            d["sourcify_parse_error"]=str(e)[:120]
    res[name]=d
    print("===",name)
    print(" contractURI:",str(d["contractURI"])[:300])
    print(" tokenURI_1:",str(d.get("tokenURI_1_decoded") or d["tokenURI_1"])[:400])
    print(" owner:",d.get("owner"),"| abi_site_functions:",d.get("abi_site_functions"),"| source_urls:",d.get("sourcify_source_urls"))
json.dump(res,open("run-2026-11-05-1531-gate.json","w"),indent=1)
