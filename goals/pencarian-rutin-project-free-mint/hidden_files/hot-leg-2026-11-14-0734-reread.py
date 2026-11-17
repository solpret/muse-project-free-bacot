#!/usr/bin/env python3
"""0734 reread: single targeted re-read of the 5 PLAN entries that returned
all/partial None in the 0734 run (one RPC chunk likely failed, same as 0729).
Read-only, chunked <=24 calls, 1s sleep between chunks. Distinguishes read
failure from genuine change, esp. WANGCAI % vs 70% line (132/188) and Kicks sellout."""
import json, subprocess, time
from eth_hash.auto import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
PLAN = [
 ("Kicks", "0x5726100e0D9ACB20cFB13e80e0fe42DF146730A8",
  [("freeMinted", False), ("FREE_CAP", False), ("freeCount", True), ("mintOpen", False),
   ("totalMinted", False), ("balanceOf", True)]),
 ("WANGCAI", "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd",
  [("freeClaimed", False), ("FREE_SUPPLY", False), ("totalSupply", False),
   ("mintOpen", False), ("mintedBy", True), ("AGENT_ID", False)]),
 ("YUANBAO", "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E",
  [("freeClaimed", False), ("FREE_SUPPLY", False), ("totalSupply", False),
   ("mintOpen", False), ("mintedBy", True), ("AGENT_ID", False)]),
 ("DragonAgents", "0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998",
  [("freeClaimed", False), ("FREE_SUPPLY", False), ("totalSupply", False),
   ("mintOpen", False), ("mintedBy", True)]),
 ("CRACE", "0x7B1ca439312368dE8652b9B5d7A54cA74A884680",
  [("freeMinted", False), ("FREE_QUOTA", False), ("mintOpen", False), ("totalSupply", False), ("freeClaimed", True)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
out = {"reread_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time()+7*3600)), "reads": {}, "raw": {}}
for i in range(0, len(reqs), 24):
    if i > 0:
        time.sleep(1)
    chunk = reqs[i:i+24]
    body = subprocess.run(["curl","-sS","-m","60","-A","Mozilla/5.0","-H","Content-Type: application/json","-d",json.dumps(chunk),"https://bsc-dataseed.binance.org/"], capture_output=True, text=True, timeout=70).stdout
    if not body:
        body = subprocess.run(["curl","-sS","-m","60","-A","Mozilla/5.0","-H","Content-Type: application/json","-d",json.dumps(chunk),"https://bsc-dataseed1.bnbchain.org/"], capture_output=True, text=True, timeout=70).stdout
    try:
        resp = json.loads(body) if body else {}
        items = resp if isinstance(resp, list) else [resp]
        by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
        for c in chunk:
            cid = c["id"]
            name, fn = keys[cid]
            res = by_id.get(cid, {}).get("result")
            out["raw"].setdefault(name, {})[fn] = res
            v = None
            if res and res != "0x" and len(res) >= 66:
                try: v = int(res[-64:], 16)
                except Exception: v = None
            out["reads"].setdefault(name, {})[fn] = v
    except Exception as e:
        out.setdefault("error", []).append(str(e)[:200])
print(json.dumps(out, indent=1))
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0734-reread.json","w"), indent=1)
