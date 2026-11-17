#!/usr/bin/env python3
"""Run 97 anomaly confirmation via Ankr raw eth_call (read-only): e3a8 name(),
c90a decimals(), contractURI() for both rotation tokens."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as m
from Crypto.Hash import keccak
def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def call(addr, sig):
    try:
        d = m.ankr_post("eth_call", [{"to": addr, "data": sel4(sig)}, "latest", "56"])
        return (d.get("result") or d)
    except Exception as e:
        return f"ERROR:{str(e)[:120]}"
def dec_str(h):
    try:
        if not isinstance(h, str) or len(h) < 130: return f"raw:{h}"[:160]
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130+ln*2]).decode("utf-8", "replace")
    except Exception as e:
        return f"decode-err:{e}"
out = {}
out["e3a8_name"] = dec_str(call("0xe3a8e1ca392b316c42d780c3cf15202f80f37777", "name()"))
print("e3a8 name:", out["e3a8_name"], flush=True)
out["c90a_decimals"] = call("0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777", "decimals()")
print("c90a decimals raw:", out["c90a_decimals"], flush=True)
out["c90a_contractURI"] = dec_str(call("0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777", "contractURI()"))
print("c90a contractURI:", out["c90a_contractURI"], flush=True)
out["e3a8_contractURI"] = dec_str(call("0xe3a8e1ca392b316c42d780c3cf15202f80f37777", "contractURI()"))
print("e3a8 contractURI:", out["e3a8_contractURI"], flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run97-token-meta3.json", "w"), indent=1)
print("saved run97-token-meta3.json")
