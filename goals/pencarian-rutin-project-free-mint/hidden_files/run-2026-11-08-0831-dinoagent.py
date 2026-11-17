#!/usr/bin/env python3
"""Run 0831 URGENT: fresh DinoAgent verify (gate now PASSES - site prints exact contract in skill.md).
Read-only. Writes run-2026-11-08-0831-dinoagent.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xcE19D6A5FF15e088D4bf23614242927139084895"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def single(addr, data, timeout=10):
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)
            return res[0]
        except Exception:
            continue
    return None

def view(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    return to_int(single(addr, data))

out = {"address": ADDR}
for sig in ["totalSupply()", "totalMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeClaimed()",
            "freeMinted()", "freeLeft()", "mintOpen()", "FREE_PER_WALLET()", "MAX_PER_WALLET()",
            "PRICE()", "freeSupply()", "maxSupply()", "soldOutAt()", "freeFor(address)"]:
    key = sig.split("(")[0]
    if "(address)" in sig:
        out[key + "_user"] = view(ADDR, sig, USER)
    else:
        out[key] = view(ADDR, sig)
    print(sig, "=", out[key + "_user"] if "(address)" in sig else out[key], flush=True)
out["freeClaimed_user"] = view(ADDR, "freeClaimed(address)", USER)
out["mintedBy_user"] = view(ADDR, "mintedBy(address)", USER)
out["balanceOf_user"] = view(ADDR, "balanceOf(address)", USER)
out["quote_user_1"] = view(ADDR, "quote(address,uint256)", USER, 1) if False else None
# mintFree() is no-arg per site skill.md; check freeFor(user) already done; also try quote(address,uint256) via raw
import subprocess
print("user:", {k: out[k] for k in ("freeFor_user","freeClaimed_user","mintedBy_user","balanceOf_user")}, flush=True)
head = None
for ep in EPS:
    try:
        res = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
        head = int(res[0], 16); break
    except Exception:
        continue
out["head"] = head
print("head:", head, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-08-0831-dinoagent.json", "w"), indent=1)
print("DINO-VERIFY DONE", flush=True)
