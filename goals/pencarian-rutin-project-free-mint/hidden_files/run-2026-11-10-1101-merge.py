#!/usr/bin/env python3
"""Merge run 2026-11-10 11:01 WIB into onchain-snapshot.json. CLEAN merge:
data-driven only — no hardcoded per-contract values from earlier runs.
- Generic reread merge (same view-aware velocity logic as 1001 merge).
- INTERVAL computed from block timestamps (prev block 132705990 = run 1001 read
  -> reread block ts via eth_getBlockByNumber; fallback 90.0 noted).
- BLOCK fallback: reread.json block is None when get_block failed at startup
  (RPC flapping); fetch head via binance.org first, else preflight head.
- No new discoveries this run (all Boltbook/sweep/feed items already in snapshot).
- Run notes written ONLY from this run's actual evidence.
Backup first; writes snapshot atomically."""
import json, shutil, subprocess, time, os

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap_path = f"{BASE}/onchain-snapshot.json"
shutil.copy(snap_path, f"{snap_path}.bak-1101-premerge")
snap = json.load(open(snap_path))
rr = json.load(open(f"{BASE}/run-2026-11-10-1101-reread.json"))
TS_WIB = "2026-11-10 11:01 WIB"
PREV_BLOCK = 132705990  # run 1001 reread block

def rpc(ep, payload, timeout=20):
    out = subprocess.run(
        ["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
         "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def block_ts(num):
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                         "params": [hex(num), False]}, timeout=20).get("result", {})
            if r.get("timestamp"):
                return int(r["timestamp"], 16)
        except Exception:
            continue
    return None

def head_block():
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                         "params": []}, timeout=20)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

BLOCK = rr.get("block")
if not BLOCK:
    BLOCK = head_block()
    print("BLOCK fallback: reread block None, head fetched:", BLOCK, flush=True)
if not BLOCK:
    BLOCK = 132712673  # preflight head this run
    print("BLOCK fallback2: preflight head", BLOCK, flush=True)

ts_prev = block_ts(PREV_BLOCK)
ts_new = block_ts(BLOCK)
if ts_prev and ts_new:
    INTERVAL = round((ts_new - ts_prev) / 60, 1)
else:
    INTERVAL = 90.0
print("BLOCK", BLOCK, "ts_prev", ts_prev, "ts_new", ts_new, "INTERVAL", INTERVAL, flush=True)

FREE_FIELDS = ["freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY",
               "mintOpen", "balanceOf_user", "freeClaimed_user"]
updated = 0
vel_pass = []
none_both = 0
for name, entry in snap["contracts"].items():
    if not isinstance(entry, dict):
        continue
    fresh = rr["reread"].get(name)
    if not fresh:
        continue
    view = "totalMinted" if str(entry.get("supplyView", "")).startswith("totalMinted") else "totalSupply"
    new = fresh.get(view)
    if new is None:
        none_both += 1
    else:
        prev = entry.get(view)
        if prev is None:
            entry[view] = new
        else:
            if new <= 10**7 and prev <= 10**7:
                minted = new - prev
                prev_rate = entry.get("currentRatePerMin")
                rate = minted / INTERVAL if INTERVAL > 0 else 0.0
                ratio = (rate / prev_rate) if prev_rate else None
                passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
                if prev > 10_000_000:
                    passes = False
                entry["previousTotalSupply"] = prev
                entry["mintedInInterval"] = minted
                entry["intervalMinutes"] = INTERVAL
                entry["previousRatePerMin"] = prev_rate
                entry["currentRatePerMin"] = rate
                entry["velocityRatio"] = ratio
                entry["velocityLegPasses"] = passes
                if passes:
                    vel_pass.append(name)
            entry[view] = new
        entry["lastReadBlock"] = BLOCK
        entry["lastReadWib"] = TS_WIB
        updated += 1
    for f in FREE_FIELDS:
        if fresh.get(f) is not None:
            entry[f] = fresh[f]
    if fresh.get("balanceOf_user") is not None:
        entry["balanceOf_user"] = fresh["balanceOf_user"]
        entry["userBalance"] = fresh["balanceOf_user"]

tc_updated = 0
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    fresh = rr["track_c"].get(name)
    if not fresh:
        continue
    for f in ("freeMinted", "totalSupply", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if fresh.get(f) is not None:
            entry[f] = fresh[f]
            tc_updated += 1
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = TS_WIB

snap["last_run_wib"] = TS_WIB
snap["timestamp_wib"] = TS_WIB

tmp_path = snap_path + ".tmp-1101"
with open(tmp_path, "w") as f:
    json.dump(snap, f, indent=1, ensure_ascii=False)
os.replace(tmp_path, snap_path)
print("merged. contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]),
      "updated reads:", updated, "tc fields:", tc_updated, "vel_pass:", vel_pass,
      "none_view:", none_both)
json.dump({"block": BLOCK, "interval_min": INTERVAL, "updated": updated,
           "tc_updated": tc_updated, "vel_pass": vel_pass, "none_view": none_both},
          open(f"{BASE}/run-2026-11-10-1101-merge.json", "w"), indent=1)
