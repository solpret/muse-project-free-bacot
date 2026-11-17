import json, sys, time, re, urllib.request
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home()/"workspace/fast_exec"))
import fast_rpc
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def dec_str(h):
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
for addr,label,token_id in [("0x5072e410ec06f8444f9c64d9bb6289935835b7ad","Constella (CSTL) NFT, run-39, future1001.ai #7 free",7),
                            ("0xecd2eed46c70c7ea047ad17d5773f70918bd7f46","ETHBack_Dividen_Tracker ERC20 mint-pattern, run-39, 0x2325 aggregator paid 0.06 BNB",None)]:
    e={"label":label}
    for fn in ["contractURI()","owner()"]:
        try: e[fn]={"raw":dec_str(call(addr,sel(fn))) if fn=="contractURI()" else call(addr,sel(fn))}
        except Exception as ex: e[fn]={"error":str(ex)[:300]}
        time.sleep(4)
    if token_id is not None:
        try:
            r=call(addr, sel("tokenURI(uint256)")+f"{token_id:064x}")
            raw=dec_str(r)
            e["tokenURI"]={"raw_prefix": (raw[:200] if raw else raw)}
            if raw and raw.startswith("data:application/json;base64,"):
                import base64
                j=json.loads(base64.b64decode(raw.split(",",1)[1]).decode())
                e["tokenURI"]["json_keys"]=sorted(j.keys())
                e["tokenURI"]["external_url"]=j.get("external_url"); e["tokenURI"]["website"]=j.get("website")
        except Exception as ex: e["tokenURI"]={"error":str(ex)[:300]}
        time.sleep(4)
    else: e["tokenURI"]={"n/a":"ERC20, no tokenId"}
    for f in ("sources","abi"): e[f"sourcify_{f}"]=sourcify(addr,f); time.sleep(2)
    out[addr]=e; print(json.dumps({addr:e},indent=1),flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run39-pointer.json","w"), indent=1)
print("saved run39-pointer.json")
