#!/usr/bin/env python3
"""Hot-leg run 2139 leg 4: lean re-read of open watchlist entries vs the
main job's 2131 reread (block 132025904). Read-only; writes
run-2026-11-06-2139-reread-lean.json. Never writes the main snapshot."""
import json, urllib.request, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2139"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed3.bnbchain.org"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(to, data, timeout=6):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""):
    return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "paused()"]
USER_VIEWS = ["balanceOf(address)", "mintedBy(address)", "freeUsed(address)",
              "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
base = json.load(open(f"{BASE}/run-2026-11-06-2131-reread-lean.json"))
base_reread = base.get("reread", {})

# address map from main job's NFT dict is not importable; rebuild from snapshot
# entries (address field) + 2131 reread addresses.
addr = {}
for name, v in snap["contracts"].items():
    if isinstance(v, dict) and v.get("address"):
        addr[name] = v["address"]
for name, v in base_reread.items():
    if isinstance(v, dict) and v.get("address"):
        addr.setdefault(name, v["address"])

# Select: baseline user slot open (or unknown) AND pool not exhausted AND
# status still watchable (early lead / strong-lead gate-blocked / watchlist).
TERMINAL = ("minted-by-user", "sold-out", "soldout", "age-excluded", "excluded-")
def status_of(name):
    e = snap["contracts"].get(name)
    return e.get("status", "") if isinstance(e, dict) else ""

targets = {}
for name, b in base_reread.items():
    if name not in addr:
        continue
    st = status_of(name)
    if any(t in st for t in TERMINAL):
        continue
    fc, fs = b.get("freeClaimed"), b.get("FREE_SUPPLY")
    if fc is not None and fs is not None and fc >= fs:
        continue  # pool exhausted at baseline
    if b.get("balanceOf_user") not in (0, None):
        continue  # slot already used
    if b.get("mintedBy_user") not in (0, None):
        continue
    targets[name] = addr[name]
print("targets:", len(targets), sorted(targets.keys()))

blk = block()
out = {"block": blk, "baseline_block": base.get("block"), "reread": {}}
t0 = time.time()
for name, a in targets.items():
    r = {"address": a}
    for sig in VIEWS:
        try: r[sig.split("(")[0]] = call(a, sig)
        except Exception: r[sig.split("(")[0]] = None
    for sig in USER_VIEWS:
        try:
            args = enc(USER) if "(address)" in sig else enc(USER) + format(1, "064x")
            r[sig.split("(")[0] + "_user"] = call(a, sig, args)
        except Exception: r[sig.split("(")[0] + "_user"] = None
    out["reread"][name] = r
    print(name, json.dumps(r), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-reread-lean.json", "w"), indent=1)
print("REREAD DONE block", blk, "elapsed", round(time.time() - t0, 1))
