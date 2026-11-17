#!/usr/bin/env python3
"""Finalize run 2026-11-06 2031 WIB (parent).
Merges leg-1 re-read, velocity rows, full scan output + 5c,
Sourcify feed shape results (subagent B), Boltbook/web findings (subagent A),
Hourglas gate deep-dive (subagent C, if present), targeted re-reads
(Tampesta / Quantumfarm / StarAgent).
CHANGES THIS RUN:
- Quantumfarm AGE-EXCLUDED (48h deadline 2026-11-06 21:00:37 WIB passed;
  freeClaimed 676/777 fresh ~21:15, mintOpen 1, not sold out) -> excluded + report once.
- Hourglas (scan first-seen, agent-shaped, free 2827/7000=40.4%, slot open)
  AGE-EXCLUDED on first read (first mint <= block 131228435, ~4.1+ days before
  head 132024370) -> excluded, NO chat report (first-read exclusion precedent, TOPA).
- Tampesta opened 21:00 WIB (totalSupply 22->440 in ~15 min); free%/slot
  UNVERIFIED, puzzle-gated free lane -> stays watchlist-only, no promotion.
- StarAgent 48h deadline ~21:26-21:27 WIB falls exactly at finalize; NOT
  clearly passed -> DEFERRED to next run (must re-read + age-exclude if unsold out).
0 preview/mint/claim/approve/sign/transaksi unless a verified candidate
passes ALL gates + safety (none this run).
"""
import json, shutil, os

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2031"
NOW_WIB = "2026-11-06 run 2031"

for f in ["onchain-snapshot.json", "onchain-scan-state.json",
          "onchain-scan-seen.json", "track-c-scan-checked.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f}.bak-20261106-2031")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
vel = json.load(open(f"{BASE}/run-{TS}-velocity.json"))
BLOCK = vel.get("block_now") or reread.get("block") or 132022546
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
    e["velocityNote"] = f"Run 2031: view {row[1]}, {row[2]}->{row[3]} (+{row[4]}), rate {row[5]}/mnt vs prev {row[6]} = {row[7]}x, passes={row[8]}"

# --- 4. Scan + seen maintenance ---
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

# --- 5. 5c checked merge ---
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
            checked_dict[r["address"]] = {"run": "2026-11-06-2031", "S1": r.get("S1"), "S2": r.get("S2"),
                                           "sourcify": r.get("sourcify"), "mint_count": r.get("mint_count")}
            existing_lower.add(a)
            added5c += 1
    json.dump(store, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# --- 6. Targeted re-reads (Tampesta / Quantumfarm / StarAgent) ---
targ = {}
targ_path = f"{BASE}/run-{TS}-targeted.json"
if os.path.exists(targ_path):
    targ = json.load(open(targ_path))
_tp = snap.get("contracts", {}).get("Tampesta-6aA5")
if isinstance(_tp, dict) and "Tampesta-6aA5" in targ:
    _t = targ["Tampesta-6aA5"]
    _tp["totalSupply"] = _t.get("totalSupply()")
    _tp["totalMinted"] = _t.get("totalMinted()")
    _tp["maxSupply"] = _t.get("maxSupply()")
    _tp["status"] = "watchlist-only-2026-11-06"
    _tp["runNote2031"] = ("Run 2031: OPENED 21:00 WIB tonight - totalSupply 22->440 in ~15 min "
        "(public minting live, fast); free views (freeClaimed/freeMinted/FREE_SUPPLY) all null, "
        "quote null, publicMinted/phase/paused null -> free% + slot UNVERIFIED; free lane is "
        "puzzle-gated (server-signed pass per Boltbook) so no auto-mint path. NOT a strong lead "
        "(free% + slot unverified), NOT a candidate. Stays watchlist-only; next run re-reads for "
        "free% / velocity baseline (this read is the baseline).")
    _tp["lastReadBlock"] = BLOCK
    _tp["lastReadWib"] = NOW_WIB
_sa = snap.get("contracts", {}).get("StarAgent-7d39")
if isinstance(_sa, dict):
    _sa["totalSupply"] = 1784
    _sa["runNote2031"] = ("Run 2031: totalSupply 1747->1773 (velocity, +26, 0.36x, FAILS) -> 1782 "
        "(targeted ~21:19) -> 1784 (final ~21:27); mintOpen 1, still minting, free% UNVERIFIED, "
        "X/website unverified. 48h deadline ~21:26-21:27 WIB falls EXACTLY at finalize - NOT clearly "
        "passed, so NO age-exclusion this run; next run (21:31/22:01) MUST re-read fresh and "
        "age-exclude if still not sold out. Stays early-lead-reported-run2131.")
    _sa["lastReadBlock"] = BLOCK
    _sa["lastReadWib"] = NOW_WIB

# --- 7. Age exclusions ---
excluded = snap.setdefault("excluded", {})
_qf = snap.get("contracts", {}).pop("Quantumfarm", None)
if _qf is not None:
    excluded["Quantumfarm"] = {"address": "0xA6Cf213F21C68b87f03Aa7d2a005e78F651eE010",
        "symbol": "QUANTUMFARM", "track": "A", "status": "excluded-age-2026-11-06",
        "note": ("AGE-EXCLUDED run 2031: first mint verified 2026-11-04 21:00:37 WIB; 48h deadline "
            "2026-11-06 21:00:37 WIB PASSED during this run. Fresh re-read ~21:15 WIB: totalSupply 677, "
            "freeClaimed 676/777 (86.9%), mintOpen 1, quote(user,1)=0, mintedBy(user)=0 - still minting, "
            "free pool NOT exhausted (101 left). Previously strong-lead-gate-blocked. Removed from active "
            "watchlist per 48h rule; report once."),
        "previousStatus": _qf.get("status"), "freeClaimed": 676, "FREE_SUPPLY": 777,
        "firstMintWib": "2026-11-04 21:00:37 WIB", "deadlineWib": "2026-11-06 21:00:37 WIB"}
_tri = {}
tri_path = f"{BASE}/run-{TS}-triage.json"
if os.path.exists(tri_path):
    _tri = json.load(open(tri_path))
_hg = _tri.get("Hourglas", {})
excluded["Hourglas"] = {"address": "0xc2027F9407eA355eeD5845Bb5e653aeed671f212",
    "symbol": "HOURGLAS", "track": "A", "status": "excluded-age-2026-11-06",
    "note": ("AGE-EXCLUDED on first read run 2031 (never a lead, no chat report per first-read "
        "exclusion precedent): scan first-seen, agent-shaped (Sourcify verified 65 fns, gate AGENT_ID, "
        "free views FREE_SUPPLY/freeClaimed/freeFor/freeLeft/freeUsed, registry_bytes true); "
        "freeClaimed 2827/7000 = 40.4%, mintOpen 1, mintedBy(user)=0, quote(user,1)=0. BUT first mint "
        "<= block 131228435 (wide-probe min; 132 Transfer-from-zero logs in [131224370-132024370], "
        ">=1000 more in [130424370-131224370], totalSupply 2827) - ~4.1+ days before head 132024370 "
        "(~21:26 WIB), far beyond 48h. Gate deep-dive (subagent C) recorded separately; age alone excludes."),
    "freeClaimed": 2827, "FREE_SUPPLY": 7000, "MAX_SUPPLY": 7777,
    "firstMintBlockMax": 131228435, "agentShaped": True}

# --- 8. Sourcify track-c watchlist-only adds (if any) ---
sour_path = f"{BASE}/run-{TS}-sourcify-shape.json"
if os.path.exists(sour_path):
    sdata = json.load(open(sour_path))
    for item in (sdata.get("track_c_watchlist_only") or []):
        key = item["key"]
        if key not in snap.get("track_c", {}):
            snap["track_c"][key] = item["entry"]
            snap["track_c"][key]["lastReadBlock"] = BLOCK
            snap["track_c"][key]["lastReadWib"] = NOW_WIB

# --- 9. Hourglas gate file (subagent C) - record verdict in excluded note if present ---
gate_path = f"{BASE}/run-{TS}-hourglas-gate.json"
gate_note = "gate deep-dive pending at finalize (subagent C still running); age-exclusion stands regardless."
if os.path.exists(gate_path):
    gdata = json.load(open(gate_path))
    gate_note = "gate deep-dive: " + str(gdata.get("verdict", gdata.get("summary", "see file")))[:400]
    excluded["Hourglas"]["gate"] = gate_note
excluded["Hourglas"]["note"] += " " + gate_note

snap["last_run"] = "2026-11-06 run 2031"
snap["last_run_wib"] = "2026-11-06 run 2031"
snap["timestamp_wib"] = "2026-11-06T21:30:00+07:00"

snap["runNote2031"] = ("Run 2031 (20:31-~21:30 WIB): 0 candidate, 0 new strong lead minted, 0 new early lead, "
    "0 track-C lead/kandidat, 0 pending claim baru/terbuka/gagal. 1 AGE-EXCLUSION: Quantumfarm (deadline 21:00:37 WIB "
    "passed; free 676/777, still minting) -> excluded + report once. 1 AGE-EXCLUSION on first read (no report): Hourglas "
    "(agent-shaped, free 2827/7000=40.4%, slot open, BUT first mint <= block 131228435, ~4.1+ days old) -> excluded. "
    "Tampesta OPENED 21:00 WIB (totalSupply 22->440 in ~15 min); free%/slot UNVERIFIED, puzzle-gated -> stays watchlist-only, "
    "no promotion. StarAgent deadline ~21:26-21:27 WIB exactly at finalize -> DEFERRED, next run must age-exclude if unsold out. "
    "Velocity: 0 passed (interval 67.2 min; StarAgent +26 0.36x, Quantumfarm +6 0.91x, WHALE-A +110 no prev rate). "
    "MERGEBORN still gate-blocked (free ~655-657/800 per Boltbook). BINANCEAI still refund/failed (launched 0, isRefundPhase 1). "
    "Scan OK (1000 blok, 189 NFT, 465 ERC20, 0 error, 6 true first-seen, 1 agent-shaped Hourglas -> age-excluded). "
    "5c: 49 ERC-20 mint>=10, all already checked, 0 new, 0 sale shape. Sourcify feed: 30 contracts, 3 new checked, 0 S1/S2. "
    "Boltbook/web: nothing new. Bridge 115/7/0.")
snap["runNote2031_scan"] = ("Run 2031 scan SUKSES. Pre-flight OK 9.2 dtk (head 132020629, 306 logs / 50 blok). "
    "Window 132021234-132022233 (1000 blok, cap 1000), 20/20 chunk + 189/189 enrich, 40 panggilan Ankr, 0 error, "
    "partial=false. 189 NFT, 465 ERC-20 mint. 6 true first-seen (Press, Hourglas, CatsApi, FOUNTAIN, CortexCrew, "
    "Influencer Rank) - 1 agent-shaped (Hourglas, age-excluded). Watermark TIDAK dimajukan (backfill owns it). "
    "5c: 49 ERC-20 mint_count>=10, 49 sudah dicek, 0 baru dicek, 0 sale shape.")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"FINALIZE DONE merged_nft={merged_nft} merged_tc={merged_tc} added_seen={added_seen} added5c={added5c}")
print(f"contracts={len(snap.get('contracts',{}))} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',{}))}")
