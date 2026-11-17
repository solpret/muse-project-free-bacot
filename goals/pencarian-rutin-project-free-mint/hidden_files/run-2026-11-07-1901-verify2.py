#!/usr/bin/env python3
"""Corrected re-verify run 1901 first-seen (5 contracts, identical template):
keccak256 selectors via pycryptodome (NOT hashlib.sha3_256), slow pacing
to avoid dataseed 429. Reads: totalSupply, MAX_SUPPLY, price, mintOpen,
freeLeft, costOf(user,1), mintsLeft(user), mintedBy(user), owner.
Read-only. Writes run-2026-11-07-1901-verify2.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/", "https://bsc.publicnode.com/"]
ADDRS = [("0x3C7D328027Ca0068e7CD8709D64D9161Bc35de93", "BRAINROT ZOO/ROT"),
         ("0x7bc0B487feBCBB1caA781148bf05A8Cd72D02Ec5", "HOG ORBIT/HOG"),
         ("0x69Dc6eB49E4cA2508C09778a211F8D6DFECE0049", "RESET 2016/R2016"),
         ("0xB4B5320e22B187d8C3dFFF0c03AF1675B4a76519", "NO NUT NOV/NNN"),
         ("0x6D318F9e4147b7A9B1eC8196BA1799592e5ae44a", "LUCKY LIFE/LUCKY")]

def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(to, data):
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 12, retries=0)
            if isinstance(r, str):
                return r
            return {"error": str(r)[:100]}
        except Exception as e:
            last = str(e)[:100]
            time.sleep(1.5)
    return {"error": last}

def u(v):
    return int(v, 16) if isinstance(v, str) else v

out = {}
for a, name in ADDRS:
    v = {"name": name}
    calls = [
        ("totalSupply", sel("totalSupply()")),
        ("MAX_SUPPLY", sel("MAX_SUPPLY()")),
        ("MAX_PER_WALLET", sel("MAX_PER_WALLET()")),
        ("price", sel("price()")),
        ("mintOpen", sel("mintOpen()")),
        ("freeLeft", sel("freeLeft()")),
        ("costOf_user_1", sel("costOf(address,uint256)") + USER[2:].lower().rjust(64, "0") + format(1, "064x")),
        ("mintsLeft_user", sel("mintsLeft(address)") + USER[2:].lower().rjust(64, "0")),
        ("mintedBy_user", sel("mintedBy(address)") + USER[2:].lower().rjust(64, "0")),
        ("owner", sel("owner()")),
        ("treasury", sel("treasury()")),
    ]
    for label, data in calls:
        r = call(a, data)
        if isinstance(r, str) and len(r) >= 66 and label in ("owner", "treasury"):
            v[label] = "0x" + r[-40:]
        elif isinstance(r, str):
            try:
                v[label] = int(r, 16)
            except Exception:
                v[label] = r[:66]
        else:
            v[label] = r
        time.sleep(0.7)
    # freeOf(user,1) — agent-token-id semantics unclear; try (user,1)
    r = call(a, sel("freeOf(address,uint256)") + USER[2:].lower().rjust(64, "0") + format(1, "064x"))
    v["freeOf_user_1"] = int(r, 16) if isinstance(r, str) else r
    time.sleep(0.7)
    out[a] = v
    print(a, name, json.dumps(v), flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-07-1901-verify2.json", "w"), indent=1)
print("VERIFY2 DONE", flush=True)
