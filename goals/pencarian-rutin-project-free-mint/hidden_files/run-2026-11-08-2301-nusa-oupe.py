#!/usr/bin/env python3
"""Run 2301 web: re-check NUSA token tradingOpen() + OUPE cards freeClaimed()/FREE_MAX().
Read-only eth_call via public BSC dataseeds (same pattern as run-2026-11-08-2201-oupe-triage.py).
Saves run-2026-11-08-2301-nusa-oupe.json next to this script."""
import json, pathlib, urllib.request
from Crypto.Hash import keccak

BASE = pathlib.Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org", "https://bsc-dataseed1.defibit.io",
       "https://bsc-dataseed2.bnbchain.org"]
NUSA_TOKEN = "0x6f91Fc7160Dc873b98a0B21Bdd974AE546FCC19a"
OUPE = "0x7cd1C2a0EE1DB8Bb3CE82270ec2610Be74A1285d"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def eth_call(addr, data, ep):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("result")

def read(addr, sig, ep):
    try:
        raw = eth_call(addr, sel(sig), ep)
        if raw in (None, "0x", ""):
            return None, f"empty result ({ep})"
        return int(raw, 16), ep
    except Exception as e:
        return None, f"{type(e).__name__}: {e} ({ep})"

out = {"run": "2301", "reads": {}}
for label, addr, sig in [
        ("NUSA_token_tradingOpen", NUSA_TOKEN, "tradingOpen()"),
        ("OUPE_freeClaimed", OUPE, "freeClaimed()"),
        ("OUPE_FREE_MAX", OUPE, "FREE_MAX()")]:
    val, note = None, None
    for ep in EPS:
        val, note = read(addr, sig, ep)
        if val is not None:
            break
    out["reads"][label] = {"contract": addr, "sig": sig, "value": val, "via": note}
    print(label, "=", val, "|", note)

json.dump(out, open(BASE / "run-2026-11-08-2301-nusa-oupe.json", "w"), indent=1)
print("saved", BASE / "run-2026-11-08-2301-nusa-oupe.json")
