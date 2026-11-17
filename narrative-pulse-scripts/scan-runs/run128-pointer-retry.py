#!/usr/bin/env python3
"""Run 127 pointer retry (read-only): re-read contractURI()/tokenURI() for the 2
pointer targets whose contractURI first-pass reads failed via fast_rpc race timeouts.
Merges results into run128-pointer.json. No preview/mint/sign/login."""
import json, sys, time, base64
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def dec_str(h):
    try:
        if not isinstance(h, str) or not h.startswith("0x"):
            return None
        b = bytes.fromhex(h[2:])
        if len(b) < 96:
            return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception:
        return None

def call_retry(addr, data, tries=3):
    last = None
    for i in range(tries):
        try:
            return fast_rpc.race("eth_call", [{"to": addr, "data": data}, "latest"])
        except Exception as e:
            last = e
            time.sleep(5)
    raise last

TARGETS = [
    ("0xbf3488e453c68e9771c26d448e99d0ec5395135f", "Agentlings", 7812),
    ("0x9da90fe302a987d979c21d7c3ae421cb0b2cf8b0", "AgentOrb", 2063),
]
d = json.load(open("run128-pointer.json"))
for addr, name, tid in TARGETS:
    e = d[addr]
    # contractURI retry if first pass failed
    if isinstance(e.get("contractURI"), dict) and "error" in e["contractURI"]:
        try:
            e["contractURI_retry"] = {"raw": dec_str(call_retry(addr, sel("contractURI()")))}
            print(f"{name} contractURI retry OK: {str(e['contractURI_retry']['raw'])[:120]}", flush=True)
        except Exception as ex:
            e["contractURI_retry"] = {"error": str(ex)[:300]}
            print(f"{name} contractURI retry FAILED: {ex}", flush=True)
        time.sleep(3)
    # tokenURI retry if first pass produced no raw URI
    if not e.get("tokenURI_raw"):
        data = sel("tokenURI(uint256)") + f"{tid:064x}"
        try:
            raw = dec_str(call_retry(addr, data))
            e["tokenURI_retry_raw"] = raw
            print(f"{name} tokenURI retry OK: {str(raw)[:120]}", flush=True)
            if raw and raw.startswith("data:application/json;base64,"):
                try:
                    dec = base64.b64decode(raw.split(",", 1)[1]).decode(errors="replace")
                    e["tokenURI_retry_decoded"] = dec[:2000]
                    print(f"  decoded: {dec[:200]}", flush=True)
                except Exception as ex:
                    print(f"  base64 decode failed: {ex}", flush=True)
        except Exception as ex:
            e["tokenURI_retry"] = {"error": str(ex)[:300]}
            print(f"{name} tokenURI retry FAILED: {ex}", flush=True)
        time.sleep(3)
json.dump(d, open("run128-pointer.json", "w"), indent=1)
print("saved run128-pointer.json (merged retry)")
