#!/usr/bin/env python3
"""Run 1631 age-sweep fresh reads (precedent runs 1431/1501).
Threaded, 8s timeout, 3 RPCs. Read-only. For each of the 21 candidates
(firstMintWib verified first-mint >48h, eligible status, not sold out):
totalSupply/totalMinted/freeClaimed/freeMinted/FREE_SUPPLY/FREE_CAP/
MAX_SUPPLY/balanceOf(user). Null = read failure, never zero.
"""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-1631"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org",
        "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

def read_item(item):
    name, addr = item
    d = {"address": addr}
    d["totalSupply"] = call(addr, "totalSupply()")
    if not isinstance(d["totalSupply"], int):
        d["totalMinted"] = call(addr, "totalMinted()")
    d["freeClaimed"] = call(addr, "freeClaimed()")
    d["freeMinted"] = call(addr, "freeMinted()")
    d["FREE_SUPPLY"] = call(addr, "FREE_SUPPLY()")
    d["FREE_CAP"] = call(addr, "FREE_CAP()")
    d["MAX_SUPPLY"] = call(addr, "MAX_SUPPLY()")
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    print(name, d, flush=True)
    return name, d

cands = json.load(open(f"{BASE}/run-{TS}-age-candidates.json"))
items = [(k, v["address"]) for k, v in cands.items()]
blk = block()
print("BLOCK", blk, flush=True)
out = {"block": blk, "reads": {}}
t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_item, items):
        out["reads"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-age-reads.json", "w"), indent=1)
print("DONE in %.1fs, block %s" % (time.time() - t0, blk), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-age-reads.json", "w"), indent=1)
