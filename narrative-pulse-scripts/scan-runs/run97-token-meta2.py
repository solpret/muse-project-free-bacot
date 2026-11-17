#!/usr/bin/env python3
"""Run 97 re-verification (read-only): name/symbol/totalSupply/decimals for the
two new rotation tokens, second pass after fast_rpc timeouts in pass 1."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak
def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def call(addr, sig):
    try:
        r = fast_rpc.race("eth_call", [{"to": addr, "data": sel4(sig)}, "latest"])
    except Exception as e:
        return f"ERROR:{str(e)[:100]}"
    if not isinstance(r, str): return f"raw:{r}"
    return r
def dec_str(h):
    try:
        if not isinstance(h, str) or len(h) < 130: return f"raw:{h}"[:120]
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130+ln*2]).decode("utf-8", "replace")
    except Exception as e:
        return f"decode-err:{e}"
def dec_u(h):
    try: return int(h, 16)
    except Exception: return f"raw:{h}"[:80]
for label, a in [("c90a","0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777"),
                 ("e3a8","0xe3a8e1ca392b316c42d780c3cf15202f80f37777")]:
    name = dec_str(call(a, "name()"))
    sym = dec_str(call(a, "symbol()"))
    ts = dec_u(call(a, "totalSupply()"))
    dec = dec_u(call(a, "decimals()"))
    print(label, a, "| name:", name, "| symbol:", sym, "| totalSupply:", ts, "| decimals:", dec, flush=True)
    json.dump({label: {"name": name, "symbol": sym, "totalSupply": ts, "decimals": dec}},
              open(f"/home/hatch/workspace/narrative-pulse/scan-runs/run97-token-meta2-{label}.json", "w"), indent=1)
print("done")
