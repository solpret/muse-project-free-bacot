#!/usr/bin/env python3
"""Hot-leg 11:42 tail re-read (read-only). Same early_tests as main script."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:160]}"
    return None, err
def collect(to, tests):
    out = {}
    for name, arg in tests:
        val, err = call(to, sel(name)+arg)
        try: iv = int(val,16) if val else None
        except Exception: iv = None
        out[name] = iv
    return out
def block():
    for ep in EPS:
        try: return int(_single(ep,"eth_blockNumber",[],8,retries=0),16)
        except Exception: pass
    return None
early = [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintedBy(address)",enc_addr(USER)[2:]),("freeUsed(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:])]
TAIL = {
 "Hexagent":"0x7BA27f90c7b509af1dFBDa2a788Fe4488ff3aab4",
 "Dronagent":"0x307157fb80A63bD4C845f44f5a55Dd90127D8C50",
 "Sentrix":"0xb7dce0412BB89dE075413855875D1DB31AC89E8f",
 "Hackagent":"0xc13f995d7e2ab6B4267Dec8eeB2761464056d07b",
 "Animora":"0x150699b44B36b542B9F954272bDD0aC3fDD9519b",
 "Golemar":"0x4e06728894F3f31CbB32B97d6905639FfE2a147B",
 "Homunqul":"0x5539dD54c00094Cbd186f08AA2d8fF3A8c098ddE",
 "Praxion":"0xEA1e4AA5ecD147035eB005aDc8013959bA852799",
 "Eidolyn":"0x94c4834B186938F95EDC67FF0536Ac17F3102523",
 "DigDownV2":"0xF464550f1d744793893C0ce09b89269Ed726d796",
 "Dronefarm5063":"0x5063025fb6ab1859b91c312237a772cA21DB44e6",
}
out = {"block": block()}
for n,a in TAIL.items():
    out[n] = collect(a, early)
    print(n, out[n])
json.dump(out, open(BASE+"hot-leg-2026-11-03-1204-reread-tail.json","w"), indent=1)
print("TAIL block", out["block"])
