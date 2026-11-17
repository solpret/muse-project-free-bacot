import json, sys, time, re, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path.home()/"workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def dec_str(h):
    try:
        b=bytes.fromhex(h[2:])
        if len(b)<96: return None
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
def call(a,d): return fast_rpc.race("eth_call",[{"to":a,"data":d},"latest"])
def sourcify(addr, fields):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields={fields}"
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"Muse-scan/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body=resp.read().decode(errors="replace")
        return {"http_status":resp.status,"body_len":len(body),
                "urls_found":sorted(set(re.findall(r'https?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+', body)))[:30],
                "site_fn_words":sorted(set(re.findall(r'\b(?:website|siteURL|siteUrl|domain|external(?:_url|Url|Link)?)\b', body)))}
    except Exception as e: return {"error":str(e)[:300]}
addr="0x76439992cce24651080040a6f9c62eb6387ae672"
e={"label":"ETHBack_Dividen_Tracker ERC20 mint-pattern, run-40, 0x2325 aggregator paid 0.03 BNB"}
for fn in ["contractURI()","owner()"]:
    try: e[fn]={"raw":dec_str(call(addr,sel(fn))) if fn=="contractURI()" else call(addr,sel(fn))}
    except Exception as ex: e[fn]={"error":str(ex)[:300]}
    time.sleep(4)
e["tokenURI"]={"n/a":"ERC20, no tokenId"}
for f in ("sources","abi"): e[f"sourcify_{f}"]=sourcify(addr,f); time.sleep(2)
print(json.dumps({addr:e},indent=1),flush=True)
json.dump({addr:e}, open("/home/hatch/workspace/narrative-pulse/scan-runs/run40-pointer.json","w"), indent=1)
print("saved run40-pointer.json")
