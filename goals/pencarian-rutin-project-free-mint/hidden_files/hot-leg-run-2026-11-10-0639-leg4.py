#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-10 06:39 WIB. Legs 1-3 done inline before this
script (feed 20, 3 NEW all non-sale-shape; Boltbook EN 302/0B, ZH OK 7 addrs
all seen). Leg 4: lean fresh batch eth_call via bsc-dataseed, hard-capped.
Bridge leg read-only (all bridge contracts already in snapshot except a few
noted for main job; none same_owner_discarded among the new ones except
0x0aa11f32 which is already snapshot-discarded anyway). Writes only own
hot-leg state files + run JSON. No preview/mint. No snapshot writes."""
import json, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.bnbchain.org"
T0 = time.time()

def sel(sig):
    h = keccak.new(digest_bits=256); h.update(sig.encode()); return "0x" + h.hexdigest()[:8]

def call(addr, sig, arg=None):
    data = sel(sig)
    if arg is not None:
        data += "000000000000000000000000" + arg[2:].lower()
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(RPC, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.load(r)
        res = d.get("result")
        if not res or res == "0x":
            return None
        return int(res, 16)
    except Exception as e:
        return f"ERR:{type(e).__name__}"

jobs = [
    ("SAKURA", "0xF2705A84602369069782624279837A08bdbBf6D6",
     [("totalSupply()", None), ("freeClaimed()", None)]),
    ("THYRK", "0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e",
     [("totalSupply()", None), ("freeMinted()", None)]),
    ("Golden Agents", "0x4233C62919CC03168a361C547117c1553C375bfC",
     [("totalSupply()", None)]),
    ("ADVAGENT sale", "0x7635ef16370ef490298649a188c9205d1d7fda67",
     [("freeClaimed(address)", USER)]),
    ("NUSA sale", "0x7D08289E962f5aEc00d56D67322eb2FD056B687c",
     [("freeRemaining()", None), ("freeUsed(address)", USER)]),
    ("VISION sale", "0x5f76cAb7B054e088563D5098E17bD0dc430e61aE",
     [("totalFreeShares()", None), ("freeUsed(address)", USER)]),
    ("BHTB", "0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
     [("freeMinted()", None), ("freeClaimed(address)", USER)]),
    ("AgentGrid sale", "0x651302C0043040D48EaAF85605E12F0549aD6D89",
     [("freeUsed(address)", USER)]),
]

out = {}
for name, addr, calls in jobs:
    out[name] = {"address": addr, "reads": {}}
    for sig, arg in calls:
        out[name]["reads"][sig] = call(addr, sig, arg)
        if time.time() - T0 > 60:
            out[name]["reads"][sig] = "SKIPPED-timecap"
print(json.dumps(out, indent=1))
print("elapsed", round(time.time() - T0, 1))
with open(BASE + "hot-leg-run-2026-11-10-0634-leg4.json", "w") as f:
    json.dump({"run": "2026-11-10 06:39 WIB", "leg4": out,
               "elapsed_s": round(time.time() - T0, 1)}, f, indent=1)
