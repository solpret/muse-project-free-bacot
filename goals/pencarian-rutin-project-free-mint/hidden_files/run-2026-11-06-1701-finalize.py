#!/usr/bin/env python3
"""Finalize run 2026-11-06 1701 WIB (parent).
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
NOW_WIB = "2026-11-06 run 1701"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1701")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-1701")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-1701")
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-20261106-1701")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-06-1701-reread-lean.json"))
checked5c = json.load(open(f"{BASE}/run-2026-11-06-1701-5c-checked.json"))
vel = json.load(open(f"{BASE}/run-2026-11-06-1701-velocity.json"))
scan = json.load(open(f"{BASE}/run-2026-11-06-1701-scan.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
verify = json.load(open(f"{BASE}/run-2026-11-06-1701-verify.json"))

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
    king["freePctVerified"] = 27.87
    king["velocityNote"] = (
        "Run 1701: free % terverifikasi 27,87% (freeQuota 3333, remainingFree 2404, "
        "free claimed 929; totalMinted 929). Sudah strong-lead-gate-blocked -> "
        "perubahan status kaki, bukan promosi baru."
    )

# --- 5. Driftnauts PROMOTED to strong lead (gate-blocked) ---
dr = snap["contracts"].get("Driftnauts")
if dr is not None:
    dr["status"] = "strong-lead-gate-blocked-2026-11-06"
    dr["totalSupply"] = 805
    dr["freeMinted"] = 805
    dr["FREE_CAP"] = 2640
    dr["freePctVerified"] = 30.49
    dr["canFreeMint_user"] = 1
    dr["claimedFree_user"] = 0
    dr["balanceOf_user"] = 0
    dr["owner"] = "0x4e9b1D076fDa3605Ad63f81a94A8693342a08DBA"
    dr["ownerNote"] = "Owner TIDAK ada di same-owner-discards.json."
    dr["launchNote"] = (
        "Launch VERIFIED <=48h: first mint blok 131779452 = 2026-11-05 14:48:12 WIB "
        "(run 1501); umur ~26,7 jam saat verifikasi ~17:15 WIB 2026-11-06; "
        "deadline 48 jam 2026-11-07 14:48:12 WIB."
    )
    dr["websiteNote"] = (
        "Website GATE FAILED run 1701, metode (A)-(N): (A) pencarian alamat mentah tanpa hasil; "
        "(B) post Boltbook mkhanh.ai /p/0r8nfIBC8oJO ~17:03 WIB (804/4.000, sebutan halaman Alphapedia) tanpa tautan situs/X di kutipan front page; "
        "halaman penuh post gagal di-fetch (timeout, bukan bukti absen); "
        "(C) metadata Sourcify tanpa URL proyek (0 tautan http); "
        "(D) pola same-family tanpa hasil; (E) owner 0x4e9b1D07... bukan same-owner discarded; "
        "(F) twitterapi.io mati, tanpa handle ditemukan; "
        "(G) pencarian nama tanpa situs proyek (hanya Drifters/Drift Protocol yang tidak terkait); "
        "(H) contractURI kosong; (I) tokenURI(1) gagal baca di semua RPC run ini (bukan bukti absen); "
        "(J) tanpa fungsi situs di ABI (66 fns); "
        "(K) pencarian GitHub tanpa repo proyek (code search butuh auth); "
        "(L) halaman token BscScan via text fetch 403 (bukan bukti absen; live-browser check tidak tersedia di run ini); "
        "(M) site:pages.dev/vercel.app tanpa hasil; "
        "(N) pencarian Alphapedia tanpa halaman proyek ditemukan. "
        "TIDAK di-preview/di-mint; dilaporkan sekali sebagai strong lead terblokir gate (preseden Ghoulito 2026-11-02 / Quantumfarm 1601)."
    )
    dr["userSlotNote"] = (
        "Slot user TERBUKA: canFreeMint(user)=1, claimedFree(user)=0, balanceOf(user)=0 "
        "(verify run 1701); quote(user,1) revert (selector quote berbeda — slot dibuktikan canFreeMint+claimedFree, sama seperti baseline run 1501)."
    )
    dr["freeSlotUserOpen"] = True
    dr["baselineNote"] = (
        "PROMOSI run 1701: EARLY -> STRONG LEAD (umur VERIFIED <=48h + free 805/2640 = 30,49% "
        "terverifikasi on-chain + slot terbuka) TAPI gate website FAILED -> TIDAK di-preview/di-mint. "
        "Dilaporkan sekali sebagai strong lead terblokir gate. Promosi/mint hanya bila website "
        "terverifikasi + semua guard lolos; bila lewat 48 jam (2026-11-07 14:48:12 WIB) tanpa website -> age-excluded + hapus."
    )
    dr["lastReadBlock"] = BLOCK
    dr["lastReadWib"] = NOW_WIB

# --- 6. NEW EARLY lead: CATAI ---
snap["contracts"]["CATAI"] = {
    "address": "0x4aB809dc6e0C62a82d5Bff2F128C9FA30D752297",
    "name": "CATAI",
    "symbol": "CATAI",
    "kind": "ERC721",
    "status": "early-lead-reported-2026-11-06",
    "agentShape": "Sourcify verified ABI (24 fns): mint/mintedBy/totalMinted, PRICE/quote, gate AGENT_ID(); AGENT_ID() on-chain = 552192074493313695968015109214105588393044541999 = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact. Scan registry_bytes_hit=true.",
    "firstSeenBlock": 131991079,
    "firstMintBlock": 131991079,
    "firstMintWib": "2026-11-06 17:15:44 WIB",
    "totalMinted": 76,
    "MAX_SUPPLY": 5000,
    "freePctNote": "Free % UNVERIFIED: tanpa free view (freeClaimed/freeMinted/FREE_SUPPLY semua null); PRICE()/quote(user,1) gagal baca run ini (RPC degraded, bukan bukti berbayar).",
    "mintedBy_user": 0,
    "balanceOf_user": 0,
    "quote_user_1": None,
    "quoteNote": "quote(user,1) gagal baca (null = UNVERIFIED) -> kaki strong-lead (c) slot gratis BELUM terverifikasi -> tetap EARLY, bukan strong lead.",
    "launchNote": "Launch VERIFIED <=48h: first mint blok 131991079 = 2026-11-06 17:15:44 WIB (Ankr getLogs backwards, 0 log sebelum blok itu s.d. 131989081); umur ~40 menit saat verifikasi ~17:55 WIB 2026-11-06; deadline 48 jam 2026-11-08 17:15:44 WIB.",
    "xVerified": False,
    "velocityVerified": False,
    "websiteNote": "Gate (A)-(N) BELUM dijalankan (early lead tidak pernah di-preview/di-mint; gate dicatat saat promosi).",
    "lastReadBlock": BLOCK,
    "lastReadWib": NOW_WIB,
    "baselineNote": "EARLY lead baru run 1701 (scan window 131990465-131991464: 1 mint di window, first-seen sejati, bukan di backfill). Dilaporkan sekali sebagai EARLY. Promosi ke strong lead hanya bila 3 kaki terpenuhi (umur <=48h + free % terverifikasi >=25% + quote user 0) + gate website lolos; ke kandidat hanya bila SEMUA kriteria + safety lolos.",
}

# --- 7. Soul Agent: quoteFor now readable (progress, still EARLY) ---
soul = snap["contracts"].get("Soul Agent")
if soul is not None:
    soul["totalSupply"] = 1506
    soul["totalMinted"] = 1506
    soul["mintedPerWallet_user"] = 0
    soul["balanceOf_user"] = 0
    soul["quoteFor_user_1"] = 0
    soul["quoteNote"] = (
        "quoteFor(user,1)=0 TERBACA run 1701 (sebelumnya null) -> kaki strong-lead (c) slot "
        "terverifikasi: quote 0 + mintedPerWallet(user)=0 + balanceOf(user)=0. "
        "TAPI kaki (b) free % MASIH inferensi saja (1506/3000 = 50,2% dari konstanta tier, "
        "tanpa freeClaimed view) -> tetap EARLY, bukan strong lead, TIDAK dilaporkan ulang."
    )
    soul["lastReadBlock"] = BLOCK
    soul["lastReadWib"] = NOW_WIB

# --- 8. Quantumfarm: free 609/777, gate re-check still failed ---
qf = snap["contracts"].get("Quantumfarm")
if qf is not None:
    qf["freeClaimed"] = 609
    qf["freePctVerified"] = 78.38
    qf["quote_user_1"] = 0
    qf["balanceOf_user"] = 0
    qf["websiteNote"] = (
        qf.get("websiteNote", "")
        + " Re-check run 1701 (A/G/M): pencarian alamat mentah + nama proyek tanpa situs proyek "
        "(hanya QuantiFarm/QuantFarming yang tidak terkait); gate TETAP FAILED. Deadline 48 jam "
        "2026-11-06 21:00:37 WIB."
    )
    qf["lastReadBlock"] = BLOCK
    qf["lastReadWib"] = NOW_WIB

# --- 9. PassAgentX velocity note ---
pax = snap["contracts"].get("PassAgentX")
if pax is not None:
    pax["velocityNote"] = (
        "Run 1701: velocity GAGAL (+150 freeMinted 4100->4250, 2,7152/mnt vs prev 13,1082 = 0,21x, "
        "interval 55,25 mnt); free % tetap UNVERIFIED -> tetap EARLY, bukan promosi, TIDAK dilaporkan."
    )

# --- 10. Removals: Ghostbot (sold out) + WHALE real (age-excluded, first-mint corrected) ---
removed = []
if "Ghostbot-0c65" in snap.get("contracts", {}):
    del snap["contracts"]["Ghostbot-0c65"]
    removed.append("Ghostbot-0c65")
if "WHALE" in snap.get("contracts", {}):
    del snap["contracts"]["WHALE"]
    removed.append("WHALE")
ex = snap.setdefault("excluded", {})
ex["Ghostbot-0c65"] = {
    "address": "0x0c654bef00dad6925f64b72151c4a504f1c00bcd",
    "name": "Ghostbot",
    "status": "excluded-sold-out-2026-11-06",
    "totalSupply": 666, "MAX_SUPPLY": 666,
    "note": "SOLD OUT run 1701: totalSupply 666/666 terverifikasi on-chain (dataseed1, re-check setelah bacaan pertama null); post Boltbook 17:01 WIB 'Ghostbot closed at 666'. Dilaporkan sekali + dihapus dari watchlist aktif.",
    "lastReadWib": NOW_WIB,
}
ex["WHALE-real-8a3e"] = {
    "address": "0x8a3e3eea10e1fa7d6fa768550f8e572a15eb90d0",
    "name": "WHALE",
    "status": "excluded-age-over-48h-2026-11-06",
    "firstMintBlock": 131000213,
    "firstMintWib": "<=2026-11-01 13:22:20 WIB",
    "note": "AGE-EXCLUDED run 1701: first mint TERVERIFIKASI <=2026-11-01 13:22:20 WIB (Ankr getLogs wide 131000000-131609521: 219 log, earliest blok 131000213; kemungkinan lebih awal lagi sebelum 131000000). Umur >5 hari >> 48 jam. KOREKSI: firstMintWib snapshot lama (2026-11-04 17:33:19 WIB, blok 131609522) SALAH — pencarian Ankr run lama terbatasi dan melewatkan mint-mint awal. Dilaporkan sekali + dihapus dari watchlist aktif.",
    "lastReadWib": NOW_WIB,
}
ex["WHALE-clone-f81b"] = {
    "address": "0xf81b542c41f982a7d7a8e2ee8cab5feee6203218",
    "name": "WHALE (clone/look-alike)",
    "status": "excluded-age-over-48h-2026-11-06",
    "firstMintBlock": 131063786,
    "firstMintWib": "2026-11-01 21:19:18 WIB",
    "note": "LOOK-ALIKE contract (bukan WHALE asli 0x8a3e...): halaman Alphapedia WHALE NFT memperingatkan 'a look-alike contract at 0xf81b... is circulating - only mint from the contract on this page' (website asli whale-nft.netlify.app). First mint 2026-11-01 21:19:18 WIB (Ankr getLogs) -> umur >48 jam -> age-excluded. TIDAK PERNAH jadi lead; JANGAN mint dari alamat ini. Log saja.",
    "lastReadWib": NOW_WIB,
}
ex["binanceai-failed-2026-11-06"] = {
    "address": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    "name": "binanceai.fun (track B)",
    "status": "excluded-failed-refund-2026-11-06",
    "note": "FAILED/REFUND PHASE run 1701: failed()=1 + isRefundPhase()=1 terverifikasi (2 RPC), launched()=0, totalShares 3110. Klaim 1.000.000 TOKEN (pending claim seeded 2026-11-01) MATI — tidak akan terbuka. Dilaporkan sekali + dihapus dari tracking. pending_claims snapshot memang kosong (catatan pending tidak pernah masuk snapshot); dicatat di excluded agar tidak dilaporkan ulang.",
    "lastReadWib": NOW_WIB,
}

# --- 11. Run notes ---
snap["runNote1701_1106"] = (
    "Run 1701: 1 STRONG LEAD BARU dipromosikan (Driftnauts EARLY->STRONG, free 805/2640=30,49%) TAPI GATE WEBSITE FAILED -> dilaporkan sekali sebagai strong lead terblokir gate, TIDAK di-preview/di-mint. "
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
snap["runNote1701_scan_1106"] = (
    "Run 1701: SCAN SUKSES. Pre-flight OK 5,7 dtk (head 131989660, 356 logs / 50 blok). "
    "Window 131990465-131991464 (1000 blok, cap 1000), 40 panggilan Ankr, 0 error, partial=false. "
    "152 NFT, 395 ERC-20 mint. Triase: 4 'first-seen' menurut definisi file (absen dari seen + snapshot); 2 ada di file backfill-*.json; 2 benar-benar baru: "
    "STRAWBS: WAKE PROTOCOL 0x9Bed... (14 mint/14 minter, registry_bytes=true, Sourcify NOT verified, totalMinted 69) -> bentuk unknown, BUKAN agent-shaped dari bytecode saja (preseden 1601) -> bukan early lead, masuk seen saja; "
    "CATAI 0x4aB8... (1 mint di window, registry_bytes=true, Sourcify verified ABI 24 fns: mint/quote/PRICE/AGENT_ID, AGENT_ID() on-chain = registry exact, first mint 131991079 = 2026-11-06 17:15:44 WIB, totalMinted 76, MAX_SUPPLY 5000) -> EARLY LEAD BARU, dilaporkan sekali. "
    "Backfill first-seen 0x8028... (Ivy Bond NFT) + 0x01b5... (1 mint) sudah ada di seen utama; shape-check: keduanya Sourcify verified TAPI tanpa mint/free/gate fns (0x01b5 hanya admin mint) -> bukan agent-shaped, bukan lead. "
    "Watermark TIDAK dimajukan run ini (backfill owns it; backfill sudah di 131989172 saat finalize, mencakup 131987165-131989172). "
    "Skipped gap 131989173-131990464 milik backfill. "
    "5c: 46 ERC-20 mint_count>=10, 39 sudah dicek, 7 baru dicek (0 dibuang sampling limit), 0 sale shape (semua Sourcify not_verified; registry_bytes=true tapi ABI unverified = bentuk unknown)."
)
snap["last_run"] = "2026-11-06 run 1701"
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 1701: Driftnauts EARLY->STRONG lead TAPI GATE FAILED -> dilaporkan sekali, TIDAK di-mint; EARLY baru CATAI -> dilaporkan sekali; "
    "Ghostbot SOLD OUT + WHALE AGE-EXCLUDED (first-mint dikoreksi) + binanceai FAILED/REFUND -> masing-masing dilaporkan sekali + dihapus. "
    "0 kandidat, 0 auto-mint/claim. Scan SUKSES, 1 EARLY baru dari scan.")
snap["timestamp_wib"] = NOW_WIB

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)

# --- 12. Scan-state note (watermark untouched) ---
state["note_1701_scan"] = snap["runNote1701_scan_1106"]
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
seen["_meta"]["last_scan_window"] = "131990465-131991464"
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
print("backups: onchain-snapshot.json.bak-20261106-1701 (+state/seen/tcchecked)")
