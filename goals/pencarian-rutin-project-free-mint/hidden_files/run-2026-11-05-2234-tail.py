#!/usr/bin/env python3
"""Hot-leg 2234 tail: Pacture recheck + bridge (read-only). Main script died at service restart."""
import json, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-2234"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception: continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None
blk = block()
PACT = "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9"
p = {"sale": PACT, "block": blk}
for name, sig, args in [("opened","opened()",""),("launched","launched()",""),("freeMinted","freeMinted()",""),
  ("totalMinted","totalMinted()",""),("sharesMinted","sharesMinted()",""),("paidShares","paidShares()",""),
  ("saleEnded","saleEnded()",""),("phase","phase()",""),("freeSharesRemaining","freeSharesRemaining()",""),
  ("freeClaimed_user","freeClaimed(address)",enc(USER)),("hasFreeShare_user","hasFreeShare(address)",enc(USER))]:
    p[name] = call(PACT, sig, args)
print("PACTURE-RECHECK", p, flush=True)
json.dump(p, open(f"{BASE}/run-{TS}-pacture-recheck.json", "w"), indent=1)
try:
    br = json.load(open(f"{BASE}/scan-bridge.json"))
    cons = br.get("contracts", {})
    snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_text = json.dumps(snap)
    not_in_snap = [c for c in cons if c.lower() not in snap_text.lower()]
    discarded = [c for c, v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE", len(cons), "discarded", len(discarded), "not_in_snapshot", len(not_in_snap), flush=True)
    json.dump({"total": len(cons), "discarded": len(discarded), "not_in_snapshot": len(not_in_snap),
               "not_in_snapshot_list": not_in_snap}, open(f"{BASE}/hot-leg-{TS}-bridge.json", "w"), indent=1)
except Exception as e:
    print("BRIDGE-ERROR", e, flush=True)
print("TAIL-DONE", flush=True)
