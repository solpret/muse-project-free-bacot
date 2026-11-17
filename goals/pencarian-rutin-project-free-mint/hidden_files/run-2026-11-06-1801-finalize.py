#!/usr/bin/env python3
"""Finalize run 2026-11-06 1801 WIB (parent).
Merges leg-1 re-read (48 NFT + 18 track_c; leg-1 block() None -> velocity
block_now 132000142), velocity rows (0 passes), targeted Boltbook verifies
(Mindvolt 676/675, Hivefacai 658/657, Botphoenix 599/600 still NOT sold out),
NEW EARLY lead Blox 0xeABF... (verified ABI AgentGate, 9 mints/9 minters,
totalSupply 21; free % / age / slot UNVERIFIED), 5 shape-unknown first-seen
(Imps/Oni/Wisps/Spuds/Yokai -> seen only, per STRAWBS precedent), 5c (11 new
checked, 0 sale shape), Sourcify new 0x3058 (mint+quote+agent, NO free view
-> not track C). Scan PARTIAL (killed by 780s timeout at enrich 185/194;
chunk phase OK, 40 Ankr calls, 0 errors, window 131997467-131998466).
Watermark NOT advanced (backfill owns it; gap 131989173-131997466 backfill's).
No age exclusions (QF deadline 21:00:37, Soul 23:53:44, StarAgent ~21:26 all
later tonight). 0 preview/mint/claim/approve/sign/transaksi.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB = "2026-11-06 run 1801"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1801")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-1801")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-1801")
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-20261106-1801")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-06-1801-reread-lean.json"))
checked5c = json.load(open(f"{BASE}/run-2026-11-06-1801-5c-checked.json"))
vel = json.load(open(f"{BASE}/run-2026-11-06-1801-velocity.json"))
scan = json.load(open(f"{BASE}/run-2026-11-06-1801-scan.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))

BLOCK = vel.get("block_now") or 132000142
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

# --- 3. Velocity rows merge (store current/prev rates + pass flag) ---
vel_by_name = {}
for row in vel.get("rows", []):
    # row: [name, view, prev_val, now_val, delta, rate_now, rate_prev, ratio, passes]
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
    e["velocityNote"] = f"Run 1801: view {row[1]}, {row[2]}->{row[3]} (+{row[4]}), rate {row[5]}/mnt vs prev {row[6]} = {row[7]}x, passes={row[8]}"

# --- 4. Targeted Boltbook verifies (Mindvolt / Hivefacai / Botphoenix) ---
targeted = {
    "Mindvolt-2f47": {"totalSupply": 676, "freeClaimed": 675, "FREE_SUPPLY": 700,
                      "MAX_SUPPLY": 700, "balanceOf_user": 0, "mintedBy_user": 0,
                      "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
                      "velocityNote": "Run 1801 targeted: totalSupply 676, freeClaimed 675/700 = 96,43% (was 670/700); slot terbuka; gate website TETAP FAILED; progres saja."},
    "Hivefacai-d337": {"totalSupply": 658, "freeClaimed": 657, "FREE_SUPPLY": 700,
                       "MAX_SUPPLY": 700, "mintOpen": 1, "balanceOf_user": 0,
                       "mintedBy_user": 0, "lastReadBlock": BLOCK,
                       "lastReadWib": NOW_WIB,
                       "velocityNote": "Run 1801 targeted: totalSupply 658, freeClaimed 657/700 = 93,86% (was 634/700 per post Boltbook); slot terbuka; gate TETAP FAILED; progres saja."},
    "Botphoenix-221f": {"totalSupply": 600, "freeClaimed": 599, "FREE_SUPPLY": 600,
                        "MAX_SUPPLY": 600, "mintOpen": 1, "balanceOf_user": 0,
                        "mintedBy_user": 0, "lastReadBlock": BLOCK,
                        "lastReadWib": NOW_WIB,
                        "velocityNote": "Run 1801 targeted: freeClaimed 599/600 FLAT vs 1731 — BUKAN sold out (post Boltbook 'SOLD OUT 600/600' tetap salah); 1 slot gratis tersisa; slot terbuka."},
}
for key, vals in targeted.items():
    e = snap.get("contracts", {}).get(key)
    if not isinstance(e, dict):
        print("TARGETED SKIP (not in snapshot):", key)
        continue
    for k, v in vals.items():
        if v is not None:
            e[k] = v

# --- 5. NEW EARLY lead: Blox ---
snap["contracts"]["Blox-eABF"] = {
    "address": "0xeABF447e81f29482449f4669f97e105b60b237F7",
    "status": "early-lead-2026-11-06-1801",
    "totalSupply": 21,
    "MAX_SUPPLY": 1999,
    "mintOpen": 1,
    "balanceOf_user": 0,
    "mintedBy_user": 0,
    "firstSeenBlock": 131997610,
    "firstSeenWib": "2026-11-06 ~18:13 WIB (scan window 131997467-131998466)",
    "windowMints": 9,
    "windowMinters": 9,
    "agentGateEvidence": "Sourcify VERIFIED exact_match: mintWithAgentTokenId, agentIds, agentTokenIdOf, mintedByAgent (AgentGate); NO free-mint fn / free-supply constant in ABI; NO quote/price fn in ABI",
    "freePct": "UNVERIFIED (no free view; quote null — no quote fn in ABI)",
    "userSlot": "UNVERIFIED (balanceOf 0, mintedBy 0, but no quote/cost fn to prove free)",
    "age": "UNVERIFIED (first seen this window; totalSupply 21 > 9 window mints, so first mint predates window; launch time not verified)",
    "website": "NOT CHECKED (gate methods not run for early lead; gate applies before execution only)",
    "lastReadBlock": BLOCK,
    "lastReadWib": NOW_WIB,
}

# --- 6. Seen-file maintenance: all scan contracts appended (first_seen block) ---
seen_contracts = seen.setdefault("contracts", {})
added_seen = 0
for c in scan.get("contracts", []):
    a = c["address"].lower()
    if a not in seen_contracts:
        seen_contracts[a] = c.get("first_block")
        added_seen += 1
# The 6 first-seen (incl. Blox) are now in seen via the loop above; the 5
# shape-unknown stay seen-only (not in snapshot) per STRAWBS precedent.
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

# --- 7. 5c checked merge ---
store = tcchecked
if isinstance(store, dict) and "checked" in store and isinstance(store["checked"], dict):
    checked_dict = store["checked"]
else:
    checked_dict = store if isinstance(store, dict) else {}
    store = {"checked": checked_dict}
added5c = 0
existing_lower = {k.lower() for k in checked_dict.keys()}
for r in checked5c.get("checked", []):
    a = r["address"].lower()
    if a not in existing_lower:
        checked_dict[r["address"]] = {"run": "2026-11-06-1801", "S1": r.get("S1"), "S2": r.get("S2"),
                                       "sourcify": r.get("sourcify"), "mint_count": r.get("mint_count")}
        existing_lower.add(a)
        added5c += 1
json.dump(store, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# --- 8. Run notes ---
snap["runNote1801_1106"] = (
    "Run 1801: SILENT except 1 NEW EARLY lead (Blox, see report). 0 kandidat, 0 strong lead baru, "
    "0 sellout, 0 age-exclusion, 0 pending claim baru/terbuka/gagal, 0 track-C lead/kandidat baru, "
    "0 slot user hilang. 0 preview/mint/claim/approve/sign/transaksi. "
    "Leg 1 (532,8 dtk, block velocity 132000142, interval 37,59 mnt vs 1731): velocity 0 LOLOS "
    "(SEAT 0,54x, PassAgentX 0,17x, AgentB-c047 0,25x, Soul 0,19x). KING totalMinted 942 "
    "(free 942/3333 = 28,26%, slot terbuka, gate TETAP FAILED). CATAI totalMinted 76 FLAT, PRICE 0,001 BNB, "
    "free views tetap null -> tetap EARLY. Driftnauts freeMinted 811 FLAT, slot terbuka, gate FAILED. "
    "Quantumfarm totalSupply 649 (was 646), freeClaimed null run ini (RPC degraded, bukan perubahan); "
    "deadline 48 jam 2026-11-06 21:00:37 WIB (belum lewat). Soul Agent totalSupply 1536 (was 1532), "
    "quoteFor 0, slot terverifikasi; deadline 23:53:44 WIB (belum lewat). StarAgent semua null (degraded). "
    "Mindvolt 676/freeClaimed 675/700, Hivefacai 658/657/700 (progres saja, gate FAILED). "
    "Botphoenix freeClaimed 599/600 FLAT — BUKAN sold out, post Boltbook 'SOLD OUT' tetap salah. "
    "Track C tanpa perubahan substansi (FABE launched null run ini — hot-leg 1804: launched()=0, "
    "freeSharesRemaining 2821, share held; SENBAZURU launched 0/opened 1/hasFreeShare 1; DROID 622 flat; "
    "IMARS 300/300 pool habis; QAGENT-2 6666 flat; SAFUAI opened 1). Track B: binanceai failed=1 + "
    "refund phase=1 (sudah excluded, tidak dilaporkan ulang). Bridge 115 kontrak, 7 discarded, "
    "0 not in snapshot. Subsonic Tribe freeClaimed 1111/1111 = pool gratis HABIS (excluded, dari sweep web, "
    "post 26 Okt); BNBmeme mintOpen 0 (tutup); DOTTAI BERBAYAR 0,05 BNB (bukan free). "
    "Sourcify baru 0x3058: mint+quote+agent tapi TANPA free view -> bukan track C."
)
snap["runNote1801_scan_1106"] = (
    "Run 1801: SCAN PARTIAL (timeout 780 dtk memotong enrichment di 185/194; chunk phase SELESAI, "
    "40 panggilan Ankr, 0 error, partial=true, JSON usable). Window 131997467-131998466 (1000 blok, cap 1000). "
    "184 NFT enriched, 347 ERC-20 mint. Pre-flight OK 5,6 dtk (head 131998436). "
    "Triase: 6 first-seen (absen seen+snapshot): Blox -> EARLY LEAD BARU (lihat snapshot Blox-eABF); "
    "Imps/Oni/Wisps/Spuds/Yokai -> registry_bytes=true tapi Sourcify IncompleteRead (bentuk unknown, "
    "BUKAN agent-shaped dari bytecode saja, preseden STRAWBS 1731) -> masuk seen saja, bukan lead. "
    "Watermark TIDAK dimajukan (backfill owns it; backfill di 131989172). Skipped gap 131989173-131997466 "
    "milik backfill. 5c: 49 ERC-20 mint_count>=10, 38 sudah dicek, 11 baru dicek (0 dibuang sampling limit), "
    "0 sale shape (semua Sourcify not_verified; registry_bytes=true tapi ABI unverified = bentuk unknown). "
    "Seen: +184 kontrak."
)
snap["last_run"] = "2026-11-06 run 1801"
snap["last_run_wib"] = "2026-11-06 run 1801"
snap["timestamp_wib"] = "2026-11-06T18:45:00+07:00"

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"FINALIZE DONE merged_nft={merged_nft} merged_tc={merged_tc} added_seen={added_seen} added5c={added5c}")
print(f"contracts={len(snap.get('contracts',{}))} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',[]))}")
