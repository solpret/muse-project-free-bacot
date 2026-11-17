#!/usr/bin/env python3
"""Finalize run 2026-11-06 1901 WIB (parent).
Merges leg-1 re-read (62 NFT + 18 track_c; leg-1 block 132005539),
velocity rows (interval 31.72 min), scan output + 5c (if present),
Sourcify feed shape results (subagent B), Boltbook/web findings (subagent A).
Conditional: new early leads / age-exclusions only if their verify files exist.
0 preview/mint/claim/approve/sign/transaksi unless a verified candidate
passes ALL gates + safety (none expected this run).
"""
import json, shutil, os

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1901"
NOW_WIB = "2026-11-06 run 1901"

for f in ["onchain-snapshot.json", "onchain-scan-state.json",
          "onchain-scan-seen.json", "track-c-scan-checked.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f}.bak-20261106-1901")

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
    e["velocityNote"] = f"Run 1901: view {row[1]}, {row[2]}->{row[3]} (+{row[4]}), rate {row[5]}/mnt vs prev {row[6]} = {row[7]}x, passes={row[8]}"

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
            checked_dict[r["address"]] = {"run": "2026-11-06-1901", "S1": r.get("S1"), "S2": r.get("S2"),
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
        snap["contracts"][f"{name}-1901"] = {
            "address": meta["addr"], "name": name, "symbol": meta.get("symbol"),
            "kind": "ERC721", "status": "early-lead-2026-11-06-1901",
            "agentShape": meta.get("agentShape"),
            "firstSeenBlock": meta.get("first_block"),
            "firstSeenWib": f"2026-11-06 run 1901 (scan window {scan.get('from_block')}-{scan.get('to_block')})" if scan else "2026-11-06 run 1901",
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
#       agent-shape / free-pool / age unverified; never previewed/minted) ---
bb_path2 = f"{BASE}/run-{TS}-boltbook-verify.json"
if os.path.exists(bb_path2):
    bbv = json.load(open(bb_path2))
    bb_adds = {
     "ApeAgent": {"symbol": "APEAGENT", "kind": "ERC721",
        "status": "watchlist-only-boltbook-noted-2026-11-06",
        "note": "Boltbook lloyd.ai /p/skuGZal9P9LZ ~18:56 WIB: mint(1) value 0, 1 gratis/wallet lalu 0,001 BNB, max 10; totalMinted 256/4444 (5,8% total — free % UNVERIFIED, no free view); Sourcify NOT verified; NO Agent ID gate (eksplisit di post); first mint block 132001583 = 2026-11-06 18:34:33 WIB (earliest found in 3000-block backward walk; true first mint at or before) — agent-shape UNVERIFIED, NOT an early lead."},
     "Stickman": {"symbol": "STICKMAN", "kind": "ERC721",
        "status": "watchlist-only-boltbook-noted-2026-11-06",
        "note": "Boltbook sanity.ai /p/sCAVq2-DKIb8; site stickmanmaster.xyz (belum diverifikasi run ini); supply 4444, 1 gratis/wallet; totalSupply=totalMinted 417/4444 (9,4% total — free % UNVERIFIED, freeMinted() null); Sourcify NOT verified; first mint block 132004178 = 2026-11-06 18:54:01 WIB (earliest found in 1000-block walk) — agent-shape + age UNVERIFIED, NOT an early lead; decoy 0xd8B956e5D50fFB592ed06FBc37664056c2C18165 tanpa code."},
     "ACC": {"symbol": "ACC", "kind": "ERC20-claim",
        "status": "watchlist-only-boltbook-noted-2026-11-06-red-flag",
        "note": "Boltbook grandtheftauto6.ai /p/bROAOqK7Jsw2; fungible token, claim() static ok value 0, mint(1)/mint(2)/freeMint() revert, tanpa pair V2 WBNB; totalSupply 14.300.000.000 (loncat +14.299.995.698 dari bacaan 4.302) = RED FLAG; Sourcify VERIFIED; decimals 18; balanceOf(user)=0 — bentuk track B/C UNVERIFIED, BUKAN kandidat/lead."},
    }
    for name, meta in bb_adds.items():
        v = bbv.get(name, {})
        if name == "ApeAgent":
            snap["contracts"]["Ape Agent"] = {"address": v.get("address"), "name": "Ape Agent",
                "symbol": meta["symbol"], "kind": meta["kind"], "status": meta["status"],
                "totalMinted": v.get("totalMinted"), "MAX_SUPPLY": v.get("MAX_SUPPLY"),
                "balanceOf_user": v.get("balanceOf_user"), "firstMintBlock": (v.get("firstMint") or {}).get("firstMintBlock"),
                "firstMintWib": "2026-11-06 18:34:33 WIB (blok 132001583, earliest found)",
                "sourcify": v.get("sourcify"), "note": meta["note"],
                "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB}
        elif name == "Stickman":
            snap["contracts"]["Stickman"] = {"address": v.get("address"), "name": "Stickman",
                "symbol": meta["symbol"], "kind": meta["kind"], "status": meta["status"],
                "totalSupply": v.get("totalSupply"), "totalMinted": v.get("totalMinted"),
                "MAX_SUPPLY": v.get("MAX_SUPPLY"), "balanceOf_user": v.get("balanceOf_user"),
                "firstMintBlock": (v.get("firstMint") or {}).get("firstMintBlock"),
                "firstMintWib": "2026-11-06 18:54:01 WIB (blok 132004178, earliest found)",
                "sourcify": v.get("sourcify"), "note": meta["note"],
                "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB}
        else:
            snap["contracts"]["ACC"] = {"address": v.get("address"), "name": "ACC",
                "symbol": meta["symbol"], "kind": meta["kind"], "status": meta["status"],
                "totalSupply": v.get("totalSupply"), "decimals": v.get("decimals"),
                "balanceOf_user": v.get("balanceOf_user"), "sourcify": v.get("sourcify"),
                "note": meta["note"], "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB}

# --- 7c. Sold-out moves + excluded-note updates (verified this run) ---
excluded = snap.setdefault("excluded", {})
_dm = snap.get("contracts", {}).pop("Dragonmind", None)
if _dm is not None:
    excluded["Dragonmind"] = {"address": "0x84Ce3C8662C081232ae505195f3c3a7f1a9f4ac0",
        "symbol": "DRAGONMIND", "track": "A", "status": "excluded-sold-out-2026-11-06",
        "note": "Sold out run 1901: totalSupply 777 = MAX_SUPPLY 777 (verified on-chain run 1901; post hensyah08.ai /p/Q9PnwbxkPo25 blok 132005254 = 2026-11-06 19:02:05 WIB). Previously early-lead-reported-2026-11-04 (totalSupply 143, freeClaimed 143/777).",
        "previousStatus": _dm.get("status"), "lastTotalSupply": 777}
_hv = json.load(open(bb_path2)).get("HashOre", {}) if os.path.exists(bb_path2) else {}
if _hv.get("totalSupply") == 10000 and _hv.get("MAX_SUPPLY") == 10000:
    excluded["HashOre"] = {"address": "0x828e7073Ef57Ed778E4acF82cC45BC43eF760b54",
        "symbol": "HASHORE", "track": "A", "status": "excluded-sold-out-2026-11-06",
        "note": "Sold out 10.000/10.000 (totalSupply=totalMinted=MAX_SUPPLY=10000, verified on-chain run 1901; post akeyy.ai /p/OO052Gh9Gu9X, mining selesai). New to snapshot — recorded as excluded, never a lead.",
        "previousStatus": None, "lastTotalSupply": 10000}
_ap = excluded.get("Agent Panda")
if isinstance(_ap, dict):
    _ap["note"] = (_ap.get("note", "") + " | Run 1901 REOPEN VERIFIED on-chain: totalMinted 8193/10000, mintOpen 1 (was CLOSED mintOpen 0 at 8115); lane dibuka lagi, minting berlanjut (+63 lalu +15). Item TETAP age-excluded (~88 jam) — TIDAK di-re-add ke watchlist aktif: reopen lane saja bukan fase/batch baru terverifikasi. Free mint butuh PoW (brute-force keccak256 ~2^25 hash; FREE_PER_WALLET_AGENT 2).")
    _ap["lastReadWib"] = NOW_WIB

# --- 8. Sourcify track-c watchlist-only adds (if subagent B file exists) ---
sour_path = f"{BASE}/run-{TS}-sourcify-shape.json"
if os.path.exists(sour_path):
    sdata = json.load(open(sour_path))
    for item in sdata.get("track_c_watchlist_only", []):
        key = item["key"]
        if key not in snap.get("track_c", {}):
            snap["track_c"][key] = item["entry"]
            snap["track_c"][key]["lastReadBlock"] = BLOCK
            snap["track_c"][key]["lastReadWib"] = NOW_WIB

snap["last_run"] = "2026-11-06 run 1901"
snap["last_run_wib"] = "2026-11-06 run 1901"
snap["timestamp_wib"] = "2026-11-06T19:30:00+07:00"

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"FINALIZE DONE merged_nft={merged_nft} merged_tc={merged_tc} added_seen={added_seen} added5c={added5c} new_early={new_early}")
print(f"contracts={len(snap.get('contracts',{}))} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',{}))}")
