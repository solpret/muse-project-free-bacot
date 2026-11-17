#!/usr/bin/env python3
"""Compact bridge + track_c + snapshot-key check for run 0931. Prints only summaries."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for v in s.get("contracts", {}).values():
    a = v.get("address")
    if a:
        snap_addrs.add(a.lower())
b = json.load(open(BASE + "scan-bridge.json"))
# bridge structure: find list of contract dicts without dumping notes
def collect(obj, out):
    if isinstance(obj, dict):
        a = obj.get("address") or obj.get("contract")
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            out.append(obj)
        for v in obj.values():
            collect(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect(v, out)
items = []
collect(b, items)
print("bridge top keys:", list(b.keys()) if isinstance(b, dict) else type(b).__name__)
print("bridge contract entries:", len(items))
discarded = [it for it in items if it.get("same_owner_discarded")]
print("same_owner_discarded:", len(discarded))
not_in_snap = [it.get("address") for it in items if it.get("address", "").lower() not in snap_addrs]
print("bridge not-in-snapshot:", not_in_snap)
print("track_c keys:", list(s.get("track_c", {}).keys()))
for k, v in s.get("track_c", {}).items():
    print(" TC", k, "| status:", v.get("status"), "| last:", v.get("lastReadWib"))
print("SolNFT:", json.dumps({k: s["contracts"]["SolNFT"].get(k) for k in
      ["address", "status", "totalSupply", "freeClaimed", "FREE_SUPPLY", "FREE_CAP",
       "previousTotalSupply", "previousRatePerMin", "currentRatePerMin", "lastReadWib"]}
      if "SolNFT" in s.get("contracts", {}) else None))
for k in ["Agentx", "Zero", "OLIVER", "JNTM", "OBFG"]:
    v = s.get("contracts", {}).get(k)
    if v:
        print(k, "| prev_ts:", v.get("previousTotalSupply"), "ts:", v.get("totalSupply"),
              "| prev_rate:", v.get("previousRatePerMin"), "rate:", v.get("currentRatePerMin"),
              "| free:", v.get("freeClaimed"), "/", v.get("FREE_SUPPLY") or v.get("FREE_CAP"),
              "| last:", v.get("lastReadWib"))
    else:
        print(k, "| NOT IN SNAPSHOT contracts")
print("excluded count:", len(s.get("excluded", {})))
for name in ["WNO", "NEBULA", "UFO", "NOVRA", "War Need Over"]:
    hits = [k for k in list(s.get("contracts", {}).keys()) + list(s.get("track_c", {}).keys())
            if name.lower() in k.lower()]
    print("search", name, "->", hits)
