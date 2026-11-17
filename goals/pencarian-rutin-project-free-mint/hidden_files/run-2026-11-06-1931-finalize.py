#!/usr/bin/env python3
"""Finalize run 2026-11-06 1931 WIB (parent).
Merges leg-1 re-read (67 NFT + 15 track_c; leg-1 block 132010860),
velocity rows (interval 39.91 min), partial scan output + 5c (if present),
Sourcify feed shape results (subagent B), Boltbook/web findings (subagent A).
Conditional: new early leads / age-exclusions only if their verify files exist.
NOTE: main.py was killed mid-run (runtime reaped the session ~12:42 UTC);
leg-1 NFT section was complete (67 items); TC/binanceai/bridge recovered by
run-2026-11-06-1931-recover.py. Scan killed at enrich 65/167 (chunk phase
complete, 40 Ankr calls, 0 errors). Boltbook-verify script killed by 280s
timeout during Ringgent; its JSON was reconstructed from the log (4 items).
0 preview/mint/claim/approve/sign/transaksi unless a verified candidate
passes ALL gates + safety (none expected this run).
"""
import json, shutil, os

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1931"
NOW_WIB = "2026-11-06 run 1931"

for f in ["onchain-snapshot.json", "onchain-scan-state.json",
          "onchain-scan-seen.json", "track-c-scan-checked.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f}.bak-20261106-1931")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
vel = json.load(open(f"{BASE}/run-{TS}-velocity.json"))
BLOCK = vel.get("block_now") or reread.get("block") or 132005539
merged_nft = 0
merged_tc = 0

# --- 1. Leg-1 NFT re-read merge (non-None only, match by address) ---
addr2name = {}
for name, e in snap.get("contracts", {}).items():
    if not isinstance(e, dict):
        continue
    a = (e.get("address") or "").lower()
    if a:
        addr2name[a] = name
for name, vals in reread.get("reread", {}).items():
    if not isinstance(vals, dict):
        continue
    a = (vals.get("address") or "").lower()
    key = addr2name.get(a) or (name if name in snap.get("contracts", {}) and isinstance(snap["contracts"].get(name), dict) else None)
    if not key:
        continue
    e = snap["contracts"][key]
    for k, v in vals.items():
        if k in ("address",):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_nft += 1

# --- 2. Leg-1 track_c re-read merge (match by sale address) ---
sale2name = {}
for name, e in snap.get("track_c", {}).items():
    if not isinstance(e, dict):
        continue
    s = (e.get("sale") or "").lower()
    if s:
        sale2name[s] = name
for name, vals in reread.get("track_c", {}).items():
    if not isinstance(vals, dict):
        continue
    s = (vals.get("sale") or vals.get("address") or "").lower()
    key = sale2name.get(s) or (name if name in snap.get("track_c", {}) and isinstance(snap["track_c"].get(name), dict) else None)
    if not key:
        continue
    e = snap["track_c"][key]
    for k, v in vals.items():
        if k in ("address", "sale"):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_tc += 1

# --- 3. Velocity rows merge ---
vel_by_name = {}
for row in vel.get("rows", []):
    vel_by_name[row[0]] = row
for name, row in vel_by_name.items():
    e = snap.get("contracts", {}).get(name)
    if not isinstance(e, dict):
        continue
    if row[4] is not None:
        e["mintedInInterval"] = row[4]
    if row[5] is not None:
        e["currentRatePerMin"] = row[5]
    if row[6] is not None:
        e["previousRatePerMin"] = row[6]
    e["velocityLegPasses"] = bool(row[8])
    e["intervalMinutes"] = vel.get("interval_min")
    e["velocityNote"] = f"Run 1931: view {row[1]}, {row[2]}->{row[3]} (+{row[4]}), rate {row[5]}/mnt vs prev {row[6]} = {row[7]}x, passes={row[8]}"

# --- 4. Scan + seen maintenance (if scan JSON exists) ---
added_seen = 0
scan = None
scan_path = f"{BASE}/run-{TS}-scan.json"
if os.path.exists(scan_path):
    scan = json.load(open(scan_path))
    seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
    seen_contracts = seen.setdefault("contracts", {})
    for c in scan.get("contracts", []):
        a = c["address"].lower()
        if a not in seen_contracts:
            seen_contracts[a] = c.get("first_block")
            added_seen += 1
    json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

# --- 5. 5c checked merge (if present) ---
added5c = 0
c5_path = f"{BASE}/run-{TS}-5c-checked.json"
if os.path.exists(c5_path):
    checked5c = json.load(open(c5_path))
    tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    if isinstance(tcchecked, dict) and "checked" in tcchecked and isinstance(tcchecked["checked"], dict):
        checked_dict = tcchecked["checked"]
        store = tcchecked
    else:
        checked_dict = tcchecked if isinstance(tcchecked, dict) else {}
        store = {"checked": checked_dict}
    existing_lower = {k.lower() for k in checked_dict.keys()}
    for r in checked5c.get("checked", []):
        a = r["address"].lower()
        if a not in existing_lower:
            checked_dict[r["address"]] = {"run": "2026-11-06-1931", "S1": r.get("S1"), "S2": r.get("S2"),
                                           "sourcify": r.get("sourcify"), "mint_count": r.get("mint_count")}
            existing_lower.add(a)
            added5c += 1
    json.dump(store, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# --- 6. New early leads from scan first-seen verify (if file exists) ---
new_early = []
fs_path = f"{BASE}/run-{TS}-firstseen-verify.json"
if os.path.exists(fs_path):
    fsverify = json.load(open(fs_path))
    for name, meta in fsverify.get("_meta", {}).items():
        v = fsverify.get(name, {})
        snap["contracts"][f"{name}-1931"] = {
            "address": meta["addr"], "name": name, "symbol": meta.get("symbol"),
            "kind": "ERC721", "status": "early-lead-2026-11-06-1931",
            "agentShape": meta.get("agentShape"),
            "firstSeenBlock": meta.get("first_block"),
            "firstSeenWib": f"2026-11-06 run 1931 (scan window {scan.get('from_block')}-{scan.get('to_block')})" if scan else "2026-11-06 run 1931",
            "windowMints": meta.get("window_mints"), "windowMinters": meta.get("window_minters"),
            "totalSupply": v.get("totalSupply"), "totalPodsMinted": v.get("totalPodsMinted"), "MAX_SUPPLY": v.get("MAX_SUPPLY"),
            "mintOpen": v.get("mintOpen"), "balanceOf_user": v.get("balanceOf_user"),
            "mintedBy_user": v.get("mintedBy_user"), "costOf_user_1": v.get("costOf_user_1"),
            "PRICE": v.get("price"),
            "freePct": v.get("freePct") or "UNVERIFIED (no free view in ABI/contract)",
            "freePool": meta.get("freePool"),
            "userSlot": "costOf(user,1)=0 read on-chain (first mint free in this template); NOT preview-verified (early leads are never previewed)" if v.get("costOf_user_1") == 0 else v.get("userSlot"),
            "age": v.get("ageNote") or "UNVERIFIED (first mint may predate window; launch time not verified)",
            "website": "NOT CHECKED (gate methods not run for early lead; gate applies before execution only)",
            "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
        }
        new_early.append(name)

# --- 7. Boltbook-verify merge (if file exists; existing entries only) ---
bb_path = f"{BASE}/run-{TS}-boltbook-verify.json"
if os.path.exists(bb_path):
    bbverify = json.load(open(bb_path))
    for src, vals in bbverify.items():
        if src.startswith("_"):
            continue
        addr = (vals.get("address") or "").lower()
        key = addr2name.get(addr) if addr else None
        if not key:
            continue
        e = snap["contracts"][key]
        for k, v in vals.items():
            if k in ("address", "sourcify", "firstMint", "firstSeenBlockTs"):
                continue
            if v is not None:
                e[k] = v
        e["lastReadBlock"] = BLOCK
        e["lastReadWib"] = NOW_WIB

# --- 7b. Boltbook NEW watchlist-only adds (verified this run; NOT early leads:
#       STRAWBS: agent-shape/free%/slot/age UNVERIFIED; MERGEBORN: agent-shaped
#       but slot+age UNVERIFIED and NOT first-seen (already in seen file).
#       Never previewed/minted.) ---
bb_path2 = f"{BASE}/run-{TS}-boltbook-verify.json"
if os.path.exists(bb_path2):
    bbv = json.load(open(bb_path2))
    bb_adds = {
     "STRAWBS": {"symbol": "STRAWBS", "kind": "ERC721",
        "status": "watchlist-only-boltbook-2026-11-06",
        "note": "Boltbook boltbook.fun/p/umCzmXhXo4nm: 10.000 Agent-ID strawberries, mint 0 BNB, 1 per Agent-ID wallet, puzzle (12 Base58 transmissions WAKE/TRACE/EXIT); site join.team-red.net/strawbs (named in post). Sourcify NOT verified; totalSupply()/freeClaimed()/freeMinted()/mintOpen() REVERT (non-standard shape); totalMinted 228, MAX_SUPPLY 10000. Agent-shape + free% + slot + age ALL UNVERIFIED — NOT an early lead."},
     "MERGEBORN": {"symbol": "MRGB", "kind": "ERC721",
        "status": "watchlist-only-boltbook-2026-11-06",
        "note": "Boltbook boltbook.fun/p/I1aD1Kut4v05 (follow-up, read 19:21 WIB): freeMint() value 0, 1 free/wallet, lalu mint 0.0005 BNB; Sourcify exact_match (74 fns, per post); freeMinted 631 (post 603/800 at 19:21); free cap 800 per post (FREE_SUPPLY() not read — verify script killed by timeout); totalSupply()/totalMinted()/mintOpen()/quote() REVERT. Slot user + age UNVERIFIED; website/X NOT stated in post. Agent-shaped but NOT first-seen (already in seen file) — NOT an early lead, NOT a strong lead (needs slot+age)."},
    }
    for name, meta in bb_adds.items():
        v = bbv.get(name, {})
        key = name
        snap["contracts"][key] = {"address": v.get("address"), "name": name,
            "symbol": meta["symbol"], "kind": meta["kind"], "status": meta["status"],
            "totalSupply": v.get("totalSupply"), "totalMinted": v.get("totalMinted"),
            "freeMinted": v.get("freeMinted"), "MAX_SUPPLY": v.get("MAX_SUPPLY"),
            "balanceOf_user": v.get("balanceOf_user"),
            "sourcify": v.get("sourcify"), "agent_shaped": v.get("agent_shaped"),
            "note": meta["note"],
            "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB}

# --- 7c. Sold-out moves + excluded-note updates (verified this run) ---
excluded = snap.setdefault("excluded", {})
_mv = snap.get("contracts", {}).pop("Mindvolt-2f47", None)
if _mv is not None:
    excluded["Mindvolt"] = {"address": "0x2f47305baEdC1B1F28461cD6b488404A908B1BEA",
        "symbol": "MINDVOLT", "track": "A", "status": "excluded-sold-out-2026-11-06",
        "note": "Sold out run 1931: totalSupply 700 = MAX_SUPPLY 700 = FREE_SUPPLY 700 (verified on-chain run 1931; freeClaimed 699; mintOpen() 1 stale). Previously early-lead-reported-run2001 (freePct 11.0 stale). Post Boltbook: tutup ~19:25 WIB.",
        "previousStatus": _mv.get("status"), "lastTotalSupply": 700}
_tp = snap.get("contracts", {}).get("Tampesta-6aA5")
if isinstance(_tp, dict):
    _tp["runNote1931"] = "Boltbook post 19:26 WIB (boltbook.fun/p/ufkeMGSY8y8L): 2.222 pixel-storm NFT, free puzzle mint for .ai Agent ID, max 2 free/wallet, paid lane 0.0042 BNB, burn 1 Ombrello = 1 guaranteed mint; site ombrellonft.xyz/tampesta (named in post); RED FLAG in post: NO Sourcify full/partial match at check time (Alphapedia says verified — confirm address vs official site). Opening 21:00 WIB tonight (already in snapshot as upcoming; totalSupply 22 pre-open). No status change."
    _tp["websiteCandidate"] = "ombrellonft.xyz/tampesta (named in Boltbook post, NOT yet verified as printing the exact contracts)"

# --- 7d. Crack (track_c) manual merge: leg-1 reread stores Crack under NFT ---
_crack = reread.get("reread", {}).get("Crack")
if isinstance(_crack, dict) and "Crack" in snap.get("track_c", {}):
    _ce = snap["track_c"]["Crack"]
    for _k, _v in _crack.items():
        if _k in ("address",): continue
        if _v is not None: _ce[_k] = _v
    _ce["lastReadBlock"] = BLOCK
    _ce["lastReadWib"] = NOW_WIB

# --- 8. Sourcify track-c watchlist-only adds (if subagent B file exists) ---
sour_path = f"{BASE}/run-{TS}-sourcify-shape.json"
if os.path.exists(sour_path):
    sdata = json.load(open(sour_path))
    for item in (sdata.get("track_c_watchlist_only") or []):
        key = item["key"]
        if key not in snap.get("track_c", {}):
            snap["track_c"][key] = item["entry"]
            snap["track_c"][key]["lastReadBlock"] = BLOCK
            snap["track_c"][key]["lastReadWib"] = NOW_WIB

snap["last_run"] = "2026-11-06 run 1931"
snap["last_run_wib"] = "2026-11-06 run 1931"
snap["timestamp_wib"] = "2026-11-06T20:00:00+07:00"

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"FINALIZE DONE merged_nft={merged_nft} merged_tc={merged_tc} added_seen={added_seen} added5c={added5c} new_early={new_early}")
print(f"contracts={len(snap.get('contracts',{}))} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',{}))}")
