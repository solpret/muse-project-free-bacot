#!/usr/bin/env python3
"""Read-only verification of the two run-60 22-wallet token:
name/symbol/decimals/totalSupply/owner via fast_rpc eth_call; Sourcify ABI grep for
mint/claim/free/buy/airdrop; tokenURI decode. No preview/mint/sign."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import fast_rpc
from eth_abi import encode
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def call(addr, sig, args=b""):
    data = sel(sig)+args.hex()
    try:
        r = fast_rpc.race("eth_call", [{"to": addr, "data": data}, "latest"])
        return r
    except Exception as e:
        return f"ERR:{e}"
def dec_str(h):
    try:
        b=bytes.fromhex(h[2:])
        # dynamic string: offset(32)+len(32)+data
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="replace")
    except Exception:
        return h
def dec_uint(h):
    try: return int(h,16)
    except Exception: return h
for tok in ["0xfcd04501ebaddcda73095a75e078a8e5292f7777"]:
    print("TOKEN", tok)
    print("  name:", dec_str(call(tok,"name()") or ""))
    print("  symbol:", dec_str(call(tok,"symbol()") or ""))
    print("  decimals:", dec_uint(call(tok,"decimals()") or ""))
    print("  totalSupply:", dec_uint(call(tok,"totalSupply()") or ""))
    o=call(tok,"owner()") or ""
    print("  owner:", ("0x"+o[-40:]) if o.startswith("0x") and len(o)>=42 else o)
    tu=call(tok,"tokenURI()") or ""
    print("  tokenURI:", dec_str(tu) if tu.startswith("0x") else tu)
    # Sourcify ABI
    try:
        url=f"https://repo.sourcify.dev/contracts/full_match/56/{tok}/metadata.json"
        req=urllib.request.Request(url, headers={"User-Agent":"Muse-scan/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            meta=json.load(r)
        abi=meta.get("output",{}).get("abi",[])
        fns=[f.get("name","") for f in abi if f.get("type")=="function"]
        print("  sourcify: verified, functions:", len(fns))
        print("  mint/claim/free/buy/airdrop fns:", [f for f in fns if any(k in f.lower() for k in ("mint","claim","free","buy","airdrop"))] or "NONE")
    except Exception as e:
        print("  sourcify: not verified / error:", str(e)[:150])
