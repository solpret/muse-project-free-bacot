import json, sys, time, re
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home()/"workspace/fast_exec"))
import fast_rpc, urllib.request
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def decode_str(h):
    try:
        b=bytes.fromhex(h[2:])
        if len(b)<96: return None
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
def call(a,d):
    return fast_rpc.race("eth_call",[{"to":a,"data":d},"latest"])
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
out={}
for addr,label in [("0xea2390207d2e36779b47bf9839d37746e805c4ed","Bored Ape Yacht (BAYC) ERC20 950 tokens, run-37, doctordefi.ai free mint via sale 0xa178..."),
                   ("0x9f894d1fb964d410c4406277f90e78fac1b370e2","ETHBack_Dividen_Tracker ERC20 mint-pattern 12.4669..., run-37, 0x2325 aggregator paid 0.06 BNB")]:
    e={"label":label}
    for fn in ["contractURI()","owner()"]:
        try: e[fn]={"raw":decode_str(call(addr,sel(fn)))}
        except Exception as ex: e[fn]={"error":str(ex)[:300]}
        time.sleep(4)
    e["tokenURI"]={"n/a":"ERC20, no tokenId"}
    for f in ("sources","abi"): e[f"sourcify_{f}"]=sourcify(addr,f); time.sleep(2)
    out[addr]=e; print(json.dumps({addr:e},indent=1),flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run37-pointer.json","w"), indent=1)
print("saved run37-pointer.json")
