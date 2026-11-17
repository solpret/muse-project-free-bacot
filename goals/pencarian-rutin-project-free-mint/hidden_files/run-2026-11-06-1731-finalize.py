#!/usr/bin/env python3
"""Finalize run 2026-11-06 1731 WIB (parent).
Merges leg-1 re-read (47 NFT + 18 track_c; leg-1 block() was None, fallback
block 131991379 from velocity analysis), velocity rows, KING free % 27.87,
NEW strong lead Driftnauts (gate-blocked), NEW EARLY lead CATAI, Soul
quoteFor now readable (still EARLY), QF free 609/777 (gate still failed),
Ghostbot SOLD OUT (removed), WHALE real AGE-EXCLUDED (first-mint corrected
to <=2026-11-01 13:22:20 WIB; snapshot Nov-4 first-mint was wrong; removed),
binanceai FAILED/REFUND phase (recorded in excluded), 152 scan contracts
appended to seen file (seen-file maintenance), 7 newly 5c-checked ERC-20
recorded. Scan SUCCEEDED (1000-block window 131990465-131991464, watermark
untouched, backfill owns it; backfill advanced to 131989172). Backs up
shared files first. 0 preview/mint/claim/approve/sign/transaksi.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB = "2026-11-06 run 1731"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1731")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-1731")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-1731")
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-20261106-1731")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-06-1731-reread-lean.json"))
checked5c = json.load(open(f"{BASE}/run-2026-11-06-1731-5c-checked.json"))
vel = json.load(open(f"{BASE}/run-2026-11-06-1731-velocity.json"))
scan = json.load(open(f"{BASE}/run-2026-11-06-1731-scan.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
verify = json.load(open(f"{BASE}/run-2026-11-06-1731-verify.json"))

BLOCK = reread.get("block") or vel.get("block_now") or 131991379
merged_nft = 0
merged_tc = 0

# --- 1. Leg-1 NFT re-read merge (non-None values only, match by address) ---
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
        if k in ("sale", "address"):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_tc += 1

# --- 3. Velocity rows ---
INTERVAL_MIN = vel.get("interval_min")
for row in vel.get("rows", []):
    name, view, prev, now, delta, rate, prev_rate, ratio, passed = row
    if name not in snap.get("contracts", {}):
        continue
    e = snap["contracts"][name]
    if prev is not None:
        e["previousTotalSupply"] = prev
    if delta is not None:
        e["mintedInInterval"] = delta
    if INTERVAL_MIN is not None:
        e["intervalMinutes"] = INTERVAL_MIN
    if rate is not None:
        e["currentRatePerMin"] = rate
    if prev_rate is not None:
        e["previousRatePerMin"] = prev_rate
    e["supplyView"] = view
    e["velocityLegPasses"] = passed

# --- 4. KING Agent free % update ---
king = snap["contracts"].get("KING Agent")
if king is not None:
    king["freePctVerified"] = 28.11
    king["totalMinted"] = 937
    king["remainingFree"] = 2396
    king["velocityNote"] = (
        "Run 1731: free % terverifikasi 28,11% (freeQuota 3333, remainingFree 2396, "
        "free claimed 937; totalMinted 937 verify; costOf null run ini). Sudah "
        "strong-lead-gate-blocked -> perubahan status kaki, bukan promosi baru."
    )

# --- 5. Driftnauts: re-check only (already strong-lead-gate-blocked) ---
dr = snap["contracts"].get("Driftnauts")
if dr is not None:
    dr["freeMinted"] = 811
    dr["freePctVerified"] = 30.72
    dr["canFreeMint_user"] = 1
    dr["claimedFree_user"] = 0
    dr["balanceOf_user"] = 0
    dr["lastReadBlock"] = BLOCK
    dr["lastReadWib"] = NOW_WIB
    dr["velocityNote"] = (
        "Run 1731: freeMinted 811 (was 805), free 811/2640 = 30,72%; slot user TERBUKA "
        "(canFreeMint=1, claimedFree=0, balanceOf=0); gate website TETAP FAILED "
        "(tidak ada bukti website baru run ini) -> TIDAK di-preview/di-mint; "
        "deadline 48 jam 2026-11-07 14:48:12 WIB."
    )

# --- 6. CATAI: re-check only (stays EARLY) ---
cat = snap["contracts"].get("CATAI")
if cat is not None:
    cat["totalMinted"] = 76
    cat["PRICE"] = 1000000000000000
    cat["quote_user_1"] = None
    cat["mintedBy_user"] = 0
    cat["balanceOf_user"] = 0
    cat["lastReadBlock"] = BLOCK
    cat["lastReadWib"] = NOW_WIB
    cat["quoteNote"] = (
        "Run 1731: totalMinted 76 FLAT (was 76); free views tetap null; PRICE()=0,001 BNB "
        "terbaca; quote(user,1) tetap null (RPC degraded, bukan bukti berbayar) -> kaki "
        "strong-lead (b) free % dan (c) slot MASIH UNVERIFIED -> tetap EARLY, bukan "
        "strong lead, TIDAK dilaporkan ulang. Deadline 2026-11-08 17:15:44 WIB."
    )

# --- 7. Soul Agent: progress (still EARLY) ---
soul = snap["contracts"].get("Soul Agent")
if soul is not None:
    soul["totalSupply"] = 1532
    soul["totalMinted"] = 1532
    soul["mintedPerWallet_user"] = 0
    soul["balanceOf_user"] = 0
    soul["quoteFor_user_1"] = 0
    soul["quoteNote"] = (
        "Run 1731: totalSupply/totalMinted 1532 (was 1506); quoteFor(user,1)=0 tetap "
        "terbaca (slot terverifikasi). TAPI kaki (b) free % MASIH inferensi saja "
        "(1532/3000 dari konstanta tier, tanpa freeClaimed view) -> tetap EARLY, "
        "bukan strong lead, TIDAK dilaporkan ulang. Deadline 2026-11-06 23:53:44 WIB."
    )
    soul["lastReadBlock"] = BLOCK
    soul["lastReadWib"] = NOW_WIB

# --- 8. Quantumfarm: free 645/777, gate still failed ---
qf = snap["contracts"].get("Quantumfarm")
if qf is not None:
    qf["totalSupply"] = 646
    qf["freeClaimed"] = 645
    qf["freePctVerified"] = 83.01
    qf["quote_user_1"] = 0
    qf["mintedBy_user"] = 0
    qf["freeUsed_user"] = 0
    qf["balanceOf_user"] = 0
    qf["mintOpen"] = 1
    qf["websiteNote"] = (
        qf.get("websiteNote", "")
        + " Re-check run 1731: tidak ada bukti website baru (tidak ada post/site baru "
        "di Boltbook/sweep); gate TETAP FAILED. Deadline 48 jam 2026-11-06 21:00:37 WIB "
        "malam ini (belum lewat saat run ini)."
    )
    qf["lastReadBlock"] = BLOCK
    qf["lastReadWib"] = NOW_WIB

# --- 9. Velocity notes: AgentB-c047 PASSED (stays EARLY), PassAgentX failed ---
ab = snap["contracts"].get("AgentB-c047")
if ab is not None:
    ab["velocityNote"] = (
        "Run 1731: velocity LOLOS (+33 totalMinted 724->757, 1,1730/mnt vs prev 0,6878 = "
        "1,71x, interval 28,13 mnt). TAPI kaki strong-lead (b) free % MASIH UNVERIFIED "
        "(tanpa free view; total 757/10000 = 7,57% <25% bila seluruh koleksi gratis) "
        "-> tetap EARLY, bukan strong lead, TIDAK dilaporkan ulang."
    )
pax = snap["contracts"].get("PassAgentX")
if pax is not None:
    pax["velocityNote"] = (
        "Run 1731: velocity GAGAL (+49 freeMinted 4250->4299, 1,7418/mnt vs prev 2,7152 = "
        "0,64x, interval 28,13 mnt); free % tetap UNVERIFIED -> tetap EARLY, bukan "
        "promosi, TIDAK dilaporkan."
    )

# --- 10. NO removals this run; Botphoenix + StarAgent updates ---
removed = []
bp = snap["contracts"].get("Botphoenix-221f")
if bp is not None:
    bp["freeClaimed"] = 599
    bp["freePctVerified"] = 99.83
    bp["quote_user_1"] = 0
    bp["mintedBy_user"] = 0
    bp["balanceOf_user"] = 0
    bp["lastReadBlock"] = BLOCK
    bp["lastReadWib"] = NOW_WIB
    bp["velocityNote"] = (
        "Run 1731: freeClaimed 599/600 = 99,83% (was 229) — BUKAN sold out: 1 slot gratis "
        "tersisa. Post Boltbook cst.ai ~17:50 WIB yang mengklaim 'SOLD OUT 600/600' "
        "SALAH/prematur (verifikasi on-chain run ini: freeClaimed=599). quote(user,1)=0, "
        "mintedBy(user)=0, balanceOf(user)=0 -> slot terbuka. Tetap EARLY (age UNVERIFIED), "
        "TIDAK dilaporkan ulang; sellout hanya bila freeClaimed=600 terverifikasi."
    )
sa = snap["contracts"].get("StarAgent")
if sa is not None:
    sa["totalSupply"] = 1675
    sa["balanceOf_user"] = 0
    sa["lastReadBlock"] = BLOCK
    sa["lastReadWib"] = NOW_WIB
    sa["velocityNote"] = (
        "Run 1731: totalSupply 1675 (was null di 1701, 1672 di leg 1); free views tetap "
        "null -> tanpa kesimpulan kaki. Deadline 48 jam ~2026-11-06 21:26 WIB malam ini "
        "(belum lewat saat run ini)."
    )

# --- 11. Run notes ---
snap["runNote1731_1106"] = (
    "Run 1731: 1 STRONG LEAD BARU dipromosikan (Driftnauts EARLY->STRONG, free 805/2640=30,49%) TAPI GATE WEBSITE FAILED -> dilaporkan sekali sebagai strong lead terblokir gate, TIDAK di-preview/di-mint. "
    "1 EARLY LEAD BARU (CATAI, first mint 2026-11-06 17:15:44 WIB, AGENT_ID registry exact) -> dilaporkan sekali sebagai EARLY. "
    "1 SELLOUT (Ghostbot 666/666 terverifikasi on-chain) -> dilaporkan sekali + dihapus. "
    "1 AGE-EXCLUSION (WHALE asli 0x8a3e...: first mint <=2026-11-01 13:22 WIB, koreksi first-mint snapshot lama yang salah) -> dilaporkan sekali + dihapus; klon WHALE 0xf81b... juga age-excluded (log saja, look-alike). "
    "1 TRACK-B GAGAL (binanceai.fun failed()=1 + isRefundPhase()=1, klaim 1.000.000 TOKEN mati) -> dilaporkan sekali + dihapus dari tracking. "
    "0 kandidat baru, 0 auto-mint/claim, 0 slot user hilang. "
    "Quantumfarm free 609/777=78,38%, quote 0, slot terbuka; gate re-check (A/G/M) tetap FAILED; deadline 21:00:37 WIB malam ini. "
    "Soul Agent quoteFor(user,1)=0 kini terbaca (slot terverifikasi) TAPI free % masih inferensi -> tetap EARLY, TIDAK dilaporkan ulang. "
    "KING Agent free % kini 27,87% (929/3333) — sudah strong-lead-gate-blocked, perubahan kaki saja. "
    "StarAgent semua view null run ini (RPC degraded) — tanpa kesimpulan; deadline ~21:26 WIB malam ini. "
    "PassAgentX velocity GAGAL run ini (+150 freeMinted, 0,21x) -> tetap EARLY. "
    "Leg 1 blok fallback 131991379 (block() gagal semua RPC), interval 55,25 mnt vs run 1601; 47 NFT + 18 track_c dibaca ulang. "
    "Velocity: 0 LOLOS (LuckyBox 1,45x tapi delta 8 <20; BOBBIE +82 baseline pertama). "
    "Track B binanceai: launched=0, failed=1, isRefundPhase=1, totalShares=3110; pending_claims tetap kosong. "
    "Track C tanpa perubahan substansi (NIULAI/QAGENT-2/SAFUAI bacaan pulih/null silih berganti; FABE launched null). "
    "Bridge 115 kontrak, 7 same_owner_discarded, 0 not in snapshot. "
    "Leg 2 Boltbook: boltbook.fun EN+ZH feed sebenarnya. Post baru: WHALE NFT (klon 0xf81b... — awas look-alike; asli 0x8a3e...), Driftnauts (mkhanh.ai, 804/4.000), M3MO (sudah age-excluded), Abyssagent (same-owner-discarded, bukan lead), Ghostbot closed 666/666, AgentGlyph free pool habis 512/512 (sudah tercatat sold out), BOBBIE paused. "
    "Leg 5a Sourcify 20 kontrak, 0 baru vs hot-leg-seen, 0 sale shape. Leg 3/5b sweep 0 baru (Coracle dikenal; Razor Agent contracts not deployed; AGENT MAO paused site 530; Periodic Lab sudah di snapshot). "
    "Leg 6 komplemen 0 proyek baru (Square/Odaily/PANews hanya item lama 30 Okt + Ptah + AGENT MAO; DappBay tidak dicek langsung run ini — absen bukan bukti). "
    "RPC degraded sepanjang run (dataseed1 403; publicnode 403; null = UNVERIFIED, bukan nol)."
)
snap["runNote1731_scan_1106"] = (
    "Run 1731: SCAN SUKSES. Pre-flight OK 5,7 dtk (head 131989660, 356 logs / 50 blok). "
    "Window 131990465-131991464 (1000 blok, cap 1000), 40 panggilan Ankr, 0 error, partial=false. "
    "152 NFT, 395 ERC-20 mint. Triase: 4 'first-seen' menurut definisi file (absen dari seen + snapshot); 2 ada di file backfill-*.json; 2 benar-benar baru: "
    "STRAWBS: WAKE PROTOCOL 0x9Bed... (14 mint/14 minter, registry_bytes=true, Sourcify NOT verified, totalMinted 69) -> bentuk unknown, BUKAN agent-shaped dari bytecode saja (preseden 1601) -> bukan early lead, masuk seen saja; "
    "CATAI 0x4aB8... (1 mint di window, registry_bytes=true, Sourcify verified ABI 24 fns: mint/quote/PRICE/AGENT_ID, AGENT_ID() on-chain = registry exact, first mint 131991079 = 2026-11-06 17:15:44 WIB, totalMinted 76, MAX_SUPPLY 5000) -> EARLY LEAD BARU, dilaporkan sekali. "
    "Backfill first-seen 0x8028... (Ivy Bond NFT) + 0x01b5... (1 mint) sudah ada di seen utama; shape-check: keduanya Sourcify verified TAPI tanpa mint/free/gate fns (0x01b5 hanya admin mint) -> bukan agent-shaped, bukan lead. "
    "Watermark TIDAK dimajukan run ini (backfill owns it; backfill sudah di 131989172 saat finalize, mencakup 131987165-131989172). "
    "Skipped gap 131989173-131990464 milik backfill. "
    "5c: 46 ERC-20 mint_count>=10, 39 sudah dicek, 7 baru dicek (0 dibuang sampling limit), 0 sale shape (semua Sourcify not_verified; registry_bytes=true tapi ABI unverified = bentuk unknown)."
)
snap["last_run"] = "2026-11-06 run 1731"
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 1731: Driftnauts EARLY->STRONG lead TAPI GATE FAILED -> dilaporkan sekali, TIDAK di-mint; EARLY baru CATAI -> dilaporkan sekali; "
    "Ghostbot SOLD OUT + WHALE AGE-EXCLUDED (first-mint dikoreksi) + binanceai FAILED/REFUND -> masing-masing dilaporkan sekali + dihapus. "
    "0 kandidat, 0 auto-mint/claim. Scan SUKSES, 1 EARLY baru dari scan.")
snap["timestamp_wib"] = NOW_WIB

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)

# --- 12. Scan-state note (watermark untouched) ---
state["note_1731_scan"] = snap["runNote1731_scan_1106"]
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1, ensure_ascii=False)

# --- 13. Seen file: append ALL scan contracts (seen-file maintenance) ---
store = seen.setdefault("contracts", {})
added = 0
for c in scan.get("contracts", []):
    a = (c.get("address") or "").lower()
    if not a:
        continue
    fb = c.get("first_block")
    if a not in store:
        store[a] = fb
        added += 1
seen.setdefault("_meta", {})["last_scan_wib"] = NOW_WIB
seen["_meta"]["last_scan_window"] = "131995732-131996731"
seen["_meta"]["last_scan_added"] = added
seen["_meta"]["contracts_count"] = len(store)
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1, ensure_ascii=False)

# --- 14. Merge 5c checked (7 new) ---
raw = checked5c.get("checked", [])
new_entries = {}
if isinstance(raw, list):
    for item in raw:
        a = (item.get("address") or "").lower()
        if a:
            new_entries[a] = item
elif isinstance(raw, dict):
    new_entries = {k.lower(): v for k, v in raw.items()}
store5c = tcchecked.setdefault("checked", {}) if isinstance(tcchecked, dict) else {}
before = len(store5c)
for a, v in new_entries.items():
    if a not in store5c:
        store5c[a] = v
after = len(store5c)
json.dump(tcchecked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1, ensure_ascii=False)

print(f"merged_nft={merged_nft} merged_trackc={merged_tc}")
print(f"contracts_now={len(snap['contracts'])} track_c_now={len(snap['track_c'])} excluded_now={len(snap.get('excluded', {}))}")
print(f"removed={removed}")
print(f"seen_added={added} seen_total={len(store)}")
print(f"5c before={before} after={after} new={len(new_entries)}")
print("backups: onchain-snapshot.json.bak-20261106-1731 (+state/seen/tcchecked)")
