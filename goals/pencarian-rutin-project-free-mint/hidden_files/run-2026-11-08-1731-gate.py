#!/usr/bin/env python3
"""Gate check (H: contractURI) for run 1731 early leads BAHUANG2 + MONOLITH. Read-only."""
import sys, json, base64
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
from eth_hash.auto import keccak

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def selector(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def raw_call(addr, data, timeout=15):
    last = None
    for ep in EPS:
        try:
            return batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    raise last

def dec_str(h):
    if not h or h == "0x":
        return None
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64:
            return None
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception as e:
        return f"ERR:{e}"

def decode_uri(u):
    if not u:
        return None
    if u.startswith("data:application/json;base64,"):
        try:
            return json.loads(base64.b64decode(u.split(",", 1)[1]).decode())
        except Exception as e:
            return {"_decode_err": str(e)}
    return {"_raw": u}

out = {}
for name, addr in [("BAHUANG2", "0x57CC350b844484Eac0DE444526d295C90F9cCbB5"),
                   ("MONOLITH", "0xcdA4A0EF9C0a626b2450168fd8F90f62C51A569b")]:
    try:
        r = raw_call(addr, selector("contractURI()"))
        s = dec_str(r)
    except Exception as e:
        s = f"ERR:{type(e).__name__}:{e}"
    out[name] = {"contractURI_raw": s, "contractURI_decoded": decode_uri(s) if isinstance(s, str) else None}
    # tokenURI(1) for MONOLITH, tokenURI(0) fallback
    for tid in ([1, 0] if name == "MONOLITH" else [0]):
        try:
            r = raw_call(addr, selector("tokenURI(uint256)") + format(tid, "064x"))
            s = dec_str(r)
        except Exception as e:
            s = f"ERR:{type(e).__name__}:{e}"
        out[name][f"tokenURI({tid})_raw"] = s
        out[name][f"tokenURI({tid})_decoded"] = decode_uri(s) if isinstance(s, str) else None
        if isinstance(s, str) and s:
            break

json.dump(out, open("run-2026-11-08-1731-gate.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False)[:4000])
