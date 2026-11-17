#!/usr/bin/env python3
"""Fix-up for hot-leg run 2026-11-16 14:04: JADE cost read + apply retry
results + bridge fix (type-guarded) + persist run log."""
import json, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"
JADE = "0x1b8894391a3dcfe7e248c321103265ab52e273e0"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")

# 1) JADE cost(user,1)
data = sel("cost(address,uint256)") + enc_addr(USER) + enc_uint(1)
p = subprocess.run(["curl", "-s", "--max-time", "20", "-X", "POST", EP,
                    "-H", "Content-Type: application/json",
                    "--data", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                          "params": [{"to": JADE, "data": data}, "latest"]})],
                   capture_output=True, text=True)
jade_cost = None
try:
    r = json.loads(p.stdout).get("result")
    if isinstance(r, str): jade_cost = int(r, 16)
except Exception:
    pass
print("JADE cost(user,1):", jade_cost)

# 2) retry results (from the 14:07 retry run, all 16 recovered)
retry = {
    ("AGCLUB", "freeMinted"): 504, ("AGCLUB", "FREE_CAP"): 888,
    ("AGCLUB", "mintOpen"): 1, ("AGCLUB", "balanceOf_user"): 0,
    ("BNBG", "totalMinted"): 69, ("SPARKS", "totalSupply"): 981,
    ("Ledgera", "freeClaimed"): 2689, ("Ledgera", "totalSupply"): 2696,
    ("RaceAgents", "mintOpen"): 1, ("CPASS", "totalMinted"): 1737,
    ("CPASS", "mintOpen"): 1, ("CPASS", "balanceOf_user"): 0,
    ("REOPIR", "freeClaimed"): 559, ("REOPIR", "totalSupply"): 559,
    ("REOPIR", "mintOpen"): 1, ("RAVE", "totalMinted"): 353,
}
run = json.load(open(BASE + "hot-leg-run-2026-11-16-1404.json"))
prev = json.load(open(BASE + "hot-leg-run-2026-11-16-1359.json"))
base = prev["leg4_reread"]["reads"]
diffs = list(run["leg4_reread"].get("diffs_vs_1359", []))
for (name, field), v in retry.items():
    if v is None: continue
    run["leg4_reread"]["reads"][name]["views"][field] = v
    old = base[name]["views"][field]
    if v != old and not any(d["item"] == name and d["field"] == field for d in diffs):
        diffs.append({"item": name, "field": field, "old": old, "new": v})
if jade_cost is not None:
    run["leg4_reread"]["reads"]["JADE"]["views"]["cost_user_1"] = jade_cost
    old = base["JADE"]["views"]["cost_user_1"]
    if jade_cost != old:
        diffs.append({"item": "JADE", "field": "cost_user_1", "old": old, "new": jade_cost})
run["leg4_reread"]["diffs_vs_1359"] = diffs
run["leg4_reread"]["chunk_errors_retry"] = {
    "retried_chunks": [16, 32], "recovered": 16, "still_null": [],
    "note": "JADE cost_user_1 was unmapped in the first pass (suffix _user_1 vs _user1); read separately, value above"}
run["leg4_reread"]["chunk_errors"] = []

# 3) bridge, type-guarded
bridge = json.load(open(BASE + "scan-bridge.json"))
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for sec in ("contracts", "track_c", "pending_claims"):
    for e in (snap.get(sec) or {}).values():
        if isinstance(e, dict):
            for f in ("address", "token"):
                v = e.get(f)
                if isinstance(v, str): snap_addrs.add(v.lower())
contracts = bridge.get("contracts", {})
not_in = [a for a in contracts if isinstance(a, str) and a.lower() not in snap_addrs]
sod = [a for a, v in contracts.items()
       if isinstance(v, dict) and v.get("same_owner_discarded")]
run["bridge_scan"] = {"total": len(contracts), "not_in_snapshot": len(not_in),
                      "not_in_snapshot_list": not_in, "same_owner_discarded": len(sod)}
run["boltbook_en_retry"] = {
    "note": "EN first fetch 302 0 bytes; retry with -L: http 200, 46564 bytes, 8 addresses, 0 new vs seen (same 8 as ZH incl 0x7B86.. already recorded)",
    "http_code": "200", "bytes": 46564, "full_address_contracts": 8, "new": 0}
run["block_note"] = ("block heights across runs inconsistent (1359 log 133883875 vs this run "
                     "133884821 vs fresh eth_blockNumber 133884969); bsc-dataseed node lag suspected; "
                     "block used for ordering only, no decision depends on it")
json.dump(run, open(BASE + "hot-leg-run-2026-11-16-1404.json", "w"), indent=1)
print("FINAL DIFFS:", json.dumps(diffs))
print("BRIDGE:", json.dumps(run["bridge_scan"]))
print("PEPE:", json.dumps(run.get("pepe_reread")))
print("elapsed_s:", run.get("elapsed_s"))
