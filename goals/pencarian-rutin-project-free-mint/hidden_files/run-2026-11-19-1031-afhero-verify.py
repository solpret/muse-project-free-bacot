#!/usr/bin/env python3
"""Run 2026-11-19 10:31 WIB: fresh on-chain verification of AgentForge Hero
(AFHERO) 0xA65944F2093e6dcFD1d1a7a4f6744f924068f878, first detected by hot-leg
1024 via Sourcify feed. Read-only; no preview/mint/claim."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
A = "0xA65944F2093e6dcFD1d1a7a4f6744f924068f878"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def data(sig, args=()):
    d = "0x" + sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) else "%064x" % a
    return d
def curl_json(payload, timeout=40):
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200: raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    return json.loads(raw.decode())
views = [
 ("name","name()",()),("symbol","symbol()",()),
 ("registry","registry()",()),("token","token()",()),
 ("FREE_MINTS_PER_WALLET","FREE_MINTS_PER_WALLET()",()),
 ("MAX_MINTS_PER_WALLET","MAX_MINTS_PER_WALLET()",()),
 ("MAX_SUPPLY","MAX_SUPPLY()",()),("baseMinted","baseMinted()",()),
 ("PAID_MINT_PRICE","PAID_MINT_PRICE()",()),("seasonEnd","seasonEnd()",()),
 ("seasonPool","seasonPool()",()),("snapshotDone","snapshotDone()",()),
 ("freeMinted_user","freeMinted(address)",(USER,)),
 ("mintCountOf_user","mintCountOf(address)",(USER,)),
 ("balanceOf_user","balanceOf(address)",(USER,)),
 ("owner","owner()",()),
]
calls = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call",
          "params":[{"to":A,"data":data(sig,args)},"latest"]} for i,(k,sig,args) in enumerate(views)]
blk = curl_json({"jsonrpc":"2.0","id":99,"method":"eth_blockNumber","params":[]})
if isinstance(blk, list): blk = blk[0] if blk else {}
block = int(blk["result"],16)
res = curl_json(calls)
out = {"run":"free-mint-search 2026-11-19 10:31 WIB (afhero-verify)","address":A,"block":block,"views":{}}
by_id = {it["id"]: it for it in res if isinstance(it,dict)}
for i,(k,sig,args) in enumerate(views):
    it = by_id.get(i+1,{})
    r = it.get("result")
    if "error" in it or r in (None,"0x"):
        out["views"][k] = {"error": str(it.get("error"))[:120] if "error" in it else "empty"}
    elif k in ("name","symbol"):
        try:
            b=bytes.fromhex(r[2:]); off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
            out["views"][k]=b[off+32:off+32+ln].decode()
        except Exception as e: out["views"][k]={"error":str(e)[:80]}
    elif k in ("registry","token","owner"):
        out["views"][k]="0x"+r[-40:]
    else:
        try: out["views"][k]=int(r,16)
        except Exception: out["views"][k]=r
json.dump(out, open(f"{HF}/run-2026-11-19-1031-afhero-verify.json","w"), indent=1)
print(json.dumps(out, indent=1))
