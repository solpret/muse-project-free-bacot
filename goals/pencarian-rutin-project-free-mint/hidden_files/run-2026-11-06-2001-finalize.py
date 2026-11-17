#!/usr/bin/env python3
"""Finalize run 2026-11-06 2001 WIB (parent).
Merges leg-1 re-read (68 NFT + 15 track_c; leg-1 block 132013586),
velocity rows (interval 20.45 min), full scan output + 5c,
Sourcify feed shape results (subagent B), Boltbook/web findings (subagent A).
Conditional: new early leads / age-exclusions only if their verify files exist.
NOTE: main.py completed in foreground (LEG1 711.9s, block 132013586). Scan SUCCEEDED
full (window 132014272-132015271, 143 NFT, 431 ERC20, 40 Ankr, 0 errors,
partial=false). 0 new early leads (3 true first-seen, none agent-shaped).
MERGEBORN gate check completed incl. BscScan live-browser read (method L).
WeZards free pool exhausted -> excluded + report once. MERGEBORN ->
strong-lead-gate-blocked (age + free% verified, website gate FAILED).
0 preview/mint/claim/approve/sign/transaksi unless a verified candidate
passes ALL gates + safety (none expected this run).
"""
import json, shutil, os

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2001"
NOW_WIB = "2026-11-06 run 2001"

for f in ["onchain-snapshot.json", "onchain-scan-state.json",
          "onchain-scan-seen.json", "track-c-scan-checked.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f}.bak-20261106-2001")

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
            checked_dict[r["address"]] = {"run": "2026-11-06-2001", "S1": r.get("S1"), "S2": r.get("S2"),
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

# --- 7. Deep-dive / correction merge (run 2001; existing entries only) ---
deep = json.load(open(f"{BASE}/run-2026-11-06-2001-deepdive.json"))
corr = json.load(open(f"{BASE}/run-2026-11-06-2001-correction.json"))
_dd = {
 "BOBBIE": {"totalMinted": deep.get("BOBBIE", {}).get("totalMinted()"),
            "MAX_SUPPLY": deep.get("BOBBIE", {}).get("MAX_SUPPLY()"),
            "FREE_SUPPLY": deep.get("BOBBIE", {}).get("FREE_SUPPLY()"),
            "paused": deep.get("BOBBIE", {}).get("paused()"),
            "runNote2001": "Run 2001 deep-dive: totalMinted 788 (was 666 subagent-A ~20:15, 327 snapshot 1931); FREE_SUPPLY 2000, MAX_SUPPLY 10000, paused 0, mintedBy(user)=0; freeMinted/freeClaimed/quote all null (RPC degraded) -> free% UNVERIFIED, slot UNVERIFIED. Stays early lead; NO promotion."},
 "AgentVOLT-e0DE": {"totalSupply": deep.get("AgentVOLT-real", {}).get("totalSupply()"),
            "MAX_SUPPLY": deep.get("AgentVOLT-real", {}).get("MAX_SUPPLY()"),
            "runNote2001": "Run 2001 deep-dive: Sourcify exact_match 31 fns, free fns TOKENS_PER_FREE_MINT/freeMint/hasFreeMinted, NO gate fns, registry_bytes false; totalSupply 1747, MAX_SUPPLY 10000; free views/quote null -> free%/slot/age UNVERIFIED. Already early-lead-reported-2026-11-04; no re-report."},
 "Horus AI": {"totalSupply": corr.get("Horus_reprobe", {}).get("totalSupply()"),
            "mintOpen": corr.get("Horus_reprobe", {}).get("mintOpen()"),
            "runNote2001": "Run 2001: scan first-seen (27 mints/19 minters, window) + triage + correction: Sourcify NOT verified, registry_bytes TRUE, free views (freeMinted/freeClaimed/quote/costOf) all null, totalSupply 149, mintOpen 1. Registry-bytes alone is NOT agent-shaped (factory template common) -> NOT a new early lead. Already in snapshot as early-lead-backfill; readings updated only."},
 "MERGEBORN": {"freeMinted": 636, "FREE_CAP": 800, "freeClaimed_user": 0,
            "status": "strong-lead-gate-blocked-2026-11-06",
            "ageVerified": "2026-11-05 07:30:33 WIB (first Transfer-from-zero, block 131721125; binary-search bracket 131720302-131721865)",
            "runNote2001": "Run 2001 PROMOTED watchlist-only -> strong-lead-gate-blocked: age VERIFIED <=48h (first mint 2026-11-05 07:30:33 WIB, deadline 2026-11-07 07:30:33 WIB); freeMinted 636/800 = 79.5% (FREE_CAP 800 verified on-chain); freeClaimed(user)=0 (slot likely open; quote() unreadable). WEBSITE GATE FAILED (methods A/B/C/G/H/I/J/L): contract-address search no site; Boltbook post p/I1aD1Kut4v05 (read via browser.open) has NO site/X links, confirms freeMint() value 0, 1 free/wallet, then mint 0.0005 BNB, freeMinted 603/800 at 19:21, pace 0.27/min, risks 'unaudited, owner-controlled'; name search no site; contractURI() None; tokenURI(1) base64 JSON has NO external_url; ABI grep no site fn; BscScan token page (live browser read 20:49 WIB) shows NO website/social links, contract NOT BscScan-verified (Sourcify exact_match 56 fns differs from BscScan status), holders 649, transfers 667, reputation UNKNOWN. NOTE: specialist journal records the Cloudflare challenge persisting on first attempt; planner summary reports full read after environment change - either way method (L) yields NO website evidence. NO preview/mint executed (gate blocks). Report once as gate-blocked strong lead."},
}
for _k, _vals in _dd.items():
    _e = snap.get("contracts", {}).get(_k)
    if not isinstance(_e, dict):
        continue
    for _kk, _vv in _vals.items():
        if _vv is not None:
            _e[_kk] = _vv
    _e["lastReadBlock"] = BLOCK
    _e["lastReadWib"] = NOW_WIB

# --- 7b. Sidecoo NEW watchlist-only add (agent-shaped, legs unverified) ---
snap["contracts"]["Sidecoo"] = {
    "address": "0x409Cfe3747f1ac20f267B50BCbB6a4E9406DA3a8", "name": "Sidecoo Daily",
    "symbol": "SCDAILY", "kind": "ERC721", "status": "watchlist-only-2026-11-06",
    "totalSupply": 15470, "totalMinted": 15470,
    "note": "Boltbook run 2001 (drzein.ai): 15,435 minted, 100% in-chain SVG bytecode, bare mint(1). Correction run 2001: Sourcify exact_match 60 fns, gate AGENT_ID, free fns freeMint, quote PRICE+quote, registry_bytes true -> AGENT-SHAPED. BUT freeMinted/freeClaimed null, MAX_SUPPLY unbounded (2^256-1), quote(user,1) garbage (selector collision), launch time / website / X NOT stated -> free% + slot + age ALL UNVERIFIED. NOT an early lead (already in seen file, not first-seen), NOT a strong lead. Added to snapshot as watchlist-only on first read.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB}

# --- 7c. Sold-out / free-exhausted moves (verified this run) ---
excluded = snap.setdefault("excluded", {})
_wz = snap.get("contracts", {}).pop("WeZards", None)
if _wz is not None:
    excluded["WeZards"] = {"address": "0xe4d7Ec33Fcf7D93cBE7F4D46d0ef35F437956aab",
        "symbol": "WeZards", "track": "A", "status": "excluded-free-sold-out-2026-11-06",
        "note": "Free pool EXHAUSTED run 2001 (deep-dive): freeMinted 2500/2500, remainingFreeAllocation 0, totalMinted 2519, MAX_SUPPLY 5000, mintOpen 1; hasClaimedFree(user)=0, balanceOf(user)=0 (user never claimed). Previously early-lead-2026-11-06-1431. Report once + removed from active watchlist.",
        "previousStatus": _wz.get("status"), "freeMinted": 2500, "totalMinted": 2519}
excluded["TOPA"] = {"address": "0xd9cc8c95da13b0600df1b3f6879a1892a0631392",
    "symbol": "TOPA", "track": "A", "status": "excluded-free-exhausted-2026-11-06",
    "note": "First seen run 2001 (Boltbook, dieuduong369.ai: 2,000 free cards then paid). Deep-dive run 2001: Sourcify exact_match 71 fns, gate agentIds/isAgent, free fns FREE_CARDS/freeAvailable/freeMinted, quote+quoteFor, registry_bytes true -> agent-shaped; BUT freeMinted 2000/2000, totalMinted 2042 -> free pool EXHAUSTED on first read. Never a lead; recorded as excluded, NOT reported as a lead.",
    "freeMinted": 2000, "totalMinted": 2042}
_tp = snap.get("contracts", {}).get("Tampesta-6aA5")
if isinstance(_tp, dict):
    _tp["runNote2001"] = "Run 2001 (subagent A): totalSupply still 22 pre-open; opens 21:00 WIB tonight; Sourcify-mismatch red flag from run 1931 still stands. No status change."
_qf = snap.get("contracts", {}).get("Quantumfarm")
if isinstance(_qf, dict):
    _qf["runNote2001"] = "Run 2001: totalSupply 666, freeClaimed 665/777 = 85.6%, mintOpen null, mintedBy(user)=0; 48h deadline 2026-11-06 21:00:37 WIB NOT yet passed at run end (~20:55 WIB) -> NO age-exclusion this run; next run (21:01/21:31) MUST re-read and age-exclude if still not sold out. Gate FAILED (unchanged)."
_sa = snap.get("contracts", {}).get("StarAgent-7d39")
if isinstance(_sa, dict):
    _sa["runNote2001"] = "Run 2001: velocity PASSES (totalSupply 1725->1747, +22, 2.39x prev rate, interval 20.45 min) but NOT a candidate: free% UNVERIFIED (no free view), X unverified, website unverified. 48h deadline ~21:26 WIB tonight; next run MUST re-read and age-exclude if still not sold out. Stays early-lead-reported-run2131."
_so = snap.get("contracts", {}).get("Soul Agent")
if isinstance(_so, dict):
    _so["runNote2001"] = "Run 2001: totalSupply/totalMinted 1558, FREE_MINTS_PER_WALLET 2, mintedPerWallet(user)=0, quoteFor(user,1)=0; 48h deadline 2026-11-06 23:53:44 WIB (not passed). No change."

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

snap["last_run"] = "2026-11-06 run 2001"
snap["last_run_wib"] = "2026-11-06 run 2001"
snap["timestamp_wib"] = "2026-11-06T21:00:00+07:00"

snap["runNote2001"] = "Run 2001 (20:01-~21:00 WIB): 0 candidate, 0 new strong lead minted, 0 new early lead, 0 track-C lead/kandidat, 0 pending claim baru/terbuka/gagal. 1 FREE-SOLD-OUT: WeZards (freeMinted 2500/2500) -> excluded + report once. 1 PROMOSI: MERGEBORN watchlist-only -> strong-lead-gate-blocked (age verified 2026-11-05 07:30:33 WIB, free 636/800 = 79.5%, slot likely open; website gate FAILED incl. BscScan live read - no site/social) -> report once, NO preview/mint. 1 velocity pass: StarAgent (+22, 2.39x) - not a candidate (free%/X/website unverified). TOPA free-exhausted on first read -> excluded, no report. Sidecoo added watchlist-only (agent-shaped, legs unverified). Scan OK (1000 blok, 143 NFT, 431 ERC20, 0 error, 3 true first-seen, 0 lead). 5c: 7 new checked, 0 sale shape. Sourcify feed: 0 S1/S2. Quantumfarm deadline 21:00:37 WIB + StarAgent ~21:26 WIB not passed during this run - next run must age-exclude if unsold-out."
snap["runNote2001_scan"] = "Run 2001 scan SUKSES. Pre-flight OK 4.0 dtk (head 132013505, 278 logs / 50 blok). Window 132014272-132015271 (1000 blok, cap 1000), 20/20 chunk + 143/143 enrich, 40 panggilan Ankr, 0 error, partial=false, ~8.4 mnt. 143 NFT, 431 ERC-20 mint. 3 true first-seen (Horus AI 27 mints/19 minters, NestedNFT, CuteWizard) - 0 early lead (Horus: Sourcify unverified + free views null, registry-bytes only; NestedNFT/CuteWizard: not agent-shaped). Watermark TIDAK dimajukan (backfill owns it). Skipped gap milik backfill. 5c: 60 ERC-20 mint_count>=10, 53 sudah dicek, 7 baru dicek (cap 20, 0 dibuang sampling limit), 0 sale shape (semua Sourcify not_verified; registry_bytes=true pada kebanyakan - sinyal factory template)."
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"FINALIZE DONE merged_nft={merged_nft} merged_tc={merged_tc} added_seen={added_seen} added5c={added5c} new_early={new_early}")
print(f"contracts={len(snap.get('contracts',{}))} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',{}))}")
