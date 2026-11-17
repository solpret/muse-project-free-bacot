#!/usr/bin/env python3
"""Finalize run 2026-11-06 1601 WIB (parent).
Merges leg-1 re-read (45 NFT + 18 track_c, blok 131984013), velocity rows,
KING free % update, NEW strong lead Quantumfarm (gate-blocked), Soul Agent
re-added (early-lead-reported-2026-11-05; already reported, NOT re-reported),
185 scan contracts appended to seen file (seen-file maintenance), 8 newly
5c-checked ERC-20 recorded. Scan SUCCEEDED (1000-block window, watermark
untouched, backfill owns it). Backs up shared files first.
THE WALL age-excluded on discovery: NOT added to snapshot, NOT reported.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB = "2026-11-06 run 1601"

# --- Soul (L) BscScan result: filled in after browser handoff ---
SOUL_L_NOTE = "halaman token BscScan via browser (16:52-16:58 WIB): TANPA website/tautan sosial/More Info (tab Info kosong, hanya 'Click here to update the token information'); token Soul Agent (SOULAGENT) BEP-721, MAX TOTAL SUPPLY 1.506, HOLDERS 1.002"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1601")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-1601")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-1601")
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-20261106-1601")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-06-1601-reread-lean.json"))
checked5c = json.load(open(f"{BASE}/run-2026-11-06-1601-5c-checked.json"))
vel = json.load(open(f"{BASE}/run-2026-11-06-1601-velocity.json"))
scan = json.load(open(f"{BASE}/run-2026-11-06-1601-scan.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))

BLOCK = reread["block"]  # 131984013
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
    if passed:
        if name == "PassAgentX":
            e["velocityNote"] = (
                "Run 1601: velocity LOLOS pertama kali (+262 freeMinted 3838->4100, "
                "13,1082/mnt vs prev 0,3287 = 39,88x, interval ~20 mnt); free % "
                "UNVERIFIED (tanpa free view) -> tetap EARLY, bukan strong lead, "
                "bukan promosi, TIDAK dilaporkan ke chat."
            )
        elif name == "Crack":
            e["velocityNote"] = (
                "Run 1601: velocity LOLOS (+158 totalMinted 2377->2535, 7,9049/mnt vs "
                "prev 2,271 = 3,48x); sudah minted-by-user (Crack #792) -> informatif "
                "saja, bukan promosi."
            )

# --- 4. KING Agent free % update (remainingFree 2413 -> claimed 920/3333 = 27,60%) ---
king = snap["contracts"].get("KING Agent")
if king is not None:
    king["freePctVerified"] = 27.60
    king["velocityNote"] = (
        "Run 1601: free % terverifikasi 27,60% (freeQuota 3333, remainingFree 2413, "
        "free claimed 920; totalMinted gagal baca run ini). Sudah strong-lead-"
        "gate-blocked -> perubahan status kaki, bukan promosi baru."
    )

# --- 5. NEW strong lead: Quantumfarm (gate-blocked, reported once via mint outcome = blocked) ---
snap["contracts"]["Quantumfarm"] = {
    "address": "0xA6Cf213F21C68b87f03Aa7d2a005e78F651eE010",
    "name": "Quantumfarm",
    "symbol": "QUANTUMFARM",
    "kind": "ERC721",
    "status": "strong-lead-gate-blocked-2026-11-06",
    "agentShape": "Sourcify verified ABI (66 fns): mint/mintOpen/mintedBy, quote/PRICE, free views FREE_SUPPLY/freeClaimed/freeFor/freeLeft/freeUsed, gate AGENT_ID()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact. Scan registry_bytes_hit=true.",
    "firstSeenBlock": 131637153,
    "firstMintBlock": 131637153,
    "firstMintWib": "2026-11-04 21:00:37 WIB",
    "totalSupply": 581,
    "freeClaimed": 580,
    "FREE_SUPPLY": 777,
    "MAX_SUPPLY": 777,
    "freePctVerified": 74.65,
    "mintOpen": 1,
    "mintedBy_user": 0,
    "freeUsed_user": 0,
    "balanceOf_user": 0,
    "quote_user_1": 0,
    "owner": "0x6f244724f61d8c7fc9af40dd37ff7c82bf2b8f5d",
    "ownerNote": "Owner sama dengan deployer Saturnode (grup deployer tercatat; factory wave TIDAK exempt dari gate).",
    "launchNote": "Launch VERIFIED <=48h: first mint Transfer-from-zero blok 131637153 = 2026-11-04 21:00:37 WIB (Ankr getLogs wide 131500000-131636973 = 0 log sebelum blok itu); umur ~44 jam saat verifikasi ~17:00 WIB 2026-11-06; deadline 48 jam 2026-11-06 21:00:37 WIB.",
    "xVerified": False,
    "velocityVerified": False,
    "websiteNote": "Website GATE FAILED run 1601, metode (A)-(N) dicoba: (A) pencarian alamat mentah tanpa hasil; (B) post Boltbook tnam.ai /p/NDyNysBgcxiJ tanpa tautan situs/X (hanya BscScan + sebutan halaman Alphapedia tanpa URL, URL-nya tidak ditemukan); (C) metadata Sourcify tanpa URL proyek; (D) pola same-family tanpa hasil; (E) owner grup Saturnode, bukan exempt; (F) twitterapi.io mati, tanpa handle ditemukan; (G) pencarian nama tanpa situs proyek; (H) contractURI kosong; (I) tokenURI(1) on-chain penuh base64 JSON tanpa external_url/website; (J) tanpa fungsi situs di ABI; (K) pencarian GitHub tanpa repo (code search butuh auth); (L) halaman token BscScan via browser: TANPA website/tautan sosial/More Info (tab Info kosong, hanya 'Click here to update the token information'); (M) site:vercel/pages.dev/deed.page/surge.sh tanpa hasil; (N) profil registry Alphapedia URL tidak ditemukan, author-bio hop tanpa situs. TIDAK di-preview/di-mint; dilaporkan sekali sebagai strong lead terblokir gate (preseden Ghoulito 2026-11-02).",
    "userSlotNote": "Slot user TERBUKA: quote(user,1)=0, freeUsed(user)=0, mintedBy(user)=0, balanceOf(user)=0 (verify2 blok 131985606).",
    "freeSlotUserOpen": True,
    "lastReadBlock": 131985606,
    "lastReadWib": NOW_WIB,
    "baselineNote": "STRONG LEAD baru run 1601 (umur VERIFIED <=48h + free 74,65% + slot terbuka) TAPI gate website FAILED -> TIDAK di-preview/di-mint. Dilaporkan sekali sebagai strong lead terblokir gate. Promosi/mint hanya bila website terverifikasi + semua guard lolos; bila lewat 48 jam (2026-11-06 21:00:37 WIB) tanpa website -> age-excluded + hapus.",
    "tokenURI1Note": "tokenURI(1) on-chain base64 JSON: name 'Quantumfarm #1', deskripsi 777 robot farmer titanium, art full on-chain; traits Character 'Quantum robot farmer', Accent 'Holographic seedling', Light 'Soft rim light', Background 'Blue-violet gradient'; tanpa external_url.",
    "boltbookNote": "Boltbook tnam.ai ~16:20 WIB 2026-11-06: 553/777 minted, +49/41 mnt (~+72/jam) pada blok 131984186; bytecode 10.212 byte.",
}

# --- 6. Soul Agent re-added (EARLY, already reported 2026-11-05 run 0001; NOT re-reported) ---
snap["contracts"]["Soul Agent"] = {
    "address": "0x8fdb9411753c58476a41f7b88a44989f8d687d63",
    "name": "Soul Agent",
    "symbol": "SOULAGENT",
    "kind": "ERC721",
    "status": "early-lead-reported-2026-11-05",
    "agentShape": "Sourcify exact_match ABI (35 fns): mint, quoteFor, FREE_MINTS_PER_WALLET, FREE_TIER_END, agentId, hasAgentId, mintedPerWallet, tokenURI; agentId() on-chain = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F. Scan registry_bytes_hit=true (6 mint/4 minter di window 1601).",
    "firstSeenBlock": 131660224,
    "firstMintBlock": 131660224,
    "firstMintWib": "2026-11-04 23:53:44 WIB",
    "totalSupply": 1488,
    "totalMinted": 1488,
    "FREE_MINTS_PER_WALLET": 2,
    "FREE_TIER_END": 3000,
    "priceBefore3000": 516500000000000,
    "priceAfter3000": 860800000000000,
    "freePctNote": "Free % 1488/3000 = 49,6% HANYA INFERENSI dari konstanta tier (tanpa freeClaimed view; bukan free counter terverifikasi) -> kaki strong-lead (b) BELUM terpenuhi.",
    "mintedPerWallet_user": 0,
    "balanceOf_user": 0,
    "quoteFor_user_1": None,
    "quoteNote": "quoteFor(user,1) gagal baca (null = UNVERIFIED) -> kaki strong-lead (c) slot gratis BELUM terverifikasi -> tetap EARLY, bukan strong lead.",
    "baseURI": "ipfs://QmdujoV4umgvWTLqU1bAXJhhLPGP1Vu26t6GteY16RXZSe/",
    "owner": "0xbabac936c2536934cdf9b68f2f2cfacfbbccd273",
    "ownerNote": "Owner TIDAK ada di same-owner-discards.json.",
    "launchNote": "Launch VERIFIED <=48h: first mint blok 131660224 = 2026-11-04 23:53:44 WIB; umur ~40,9 jam saat verifikasi ~16:45 WIB 2026-11-06; deadline 48 jam 2026-11-06 23:53:44 WIB.",
    "xVerified": False,
    "velocityVerified": False,
    "websiteNote": (
        "Website GATE FAILED run 1601, metode (A)-(N): (A) pencarian alamat mentah tanpa hasil; "
        "(B) post Boltbook kipauuu.ai /p/l2L54OvfTvwl ~16:10 WIB: 'No official site or docs found - contract only, verified on-chain', tanpa tautan situs/X; "
        "(C) metadata Sourcify tanpa URL proyek; (D) pola same-family tanpa hasil; (E) owner 0xbabac936... bukan same-owner discarded; "
        "(F) twitterapi.io mati, tanpa handle ditemukan; (G) pencarian nama tanpa situs proyek; (H) contractURI kosong; "
        "(I) tokenURI(1) via Pinata tanpa external_url/website; (J) tanpa fungsi situs di ABI (hanya URL dok EIP-165); "
        "(K) pencarian GitHub tanpa repo proyek (code search butuh auth); (L) " + SOUL_L_NOTE + "; "
        "(M) site:vercel/pages.dev/deed.page/surge.sh tanpa hasil; (N) profil registry URL tidak ditemukan, author-bio hop tanpa situs. "
        "Early lead tidak pernah di-preview/di-mint; gate dicatat untuk promosi kelak."
    ),
    "userSlotNote": "Slot user (inferensi): mintedPerWallet(user)=0, balanceOf(user)=0; quoteFor(user,1) UNVERIFIED.",
    "lastReadBlock": 131985606,
    "lastReadWib": NOW_WIB,
    "baselineNote": "EARLY lead dilaporkan sekali run 2026-11-05-0001 (bersama HACKED); hot leg 0029 melihatnya 00:29 WIB tapi TIDAK melaporkannya (deteksi early-lead NFT tugas job utama); run 0131 re-read (719->1034). TIDAK dilaporkan ulang run 1601. Absen dari snapshot + semua backup 1301-1531 tanpa catatan penghapusan di run log -> ditambahkan kembali run 1601 dengan status asli + bacaan segar. Promosi ke strong lead hanya bila 3 kaki terpenuhi (free % terverifikasi >=25% + quote user 0); ke kandidat hanya bila SEMUA kriteria + safety lolos.",
    "tokenURI1Note": "tokenURI(1) metadata (Pinata): name '灵魂特工 #1', deskripsi 5.555 Soul Agents di BNB, Agent ID-gated; image ipfs://bafybeidrl76boyxktd4t2mc7i4sdusmdm3cfadfcqjyw2lemljqn6o3sme/soul-agent-char-mecha-guardian.webp; traits 角色 机甲守卫, 稀有度 普通, 版本 260/286, 力量 46, 守护 63; tanpa external_url.",
    "boltbookNote": "Boltbook kipauuu.ai ~16:10 WIB 2026-11-06: 'minted 2 free today, 2 per wallet, free tier to 3,000'; moez.ai juga mem-posting Soul Agent ~16:10 WIB.",
}

# --- 7. Run notes ---
snap["runNote1601_1106"] = (
    "Run 1601: 1 STRONG LEAD BARU (Quantumfarm) TAPI GATE WEBSITE FAILED -> dilaporkan sekali sebagai strong lead terblokir gate, TIDAK di-preview/di-mint. "
    "0 kandidat baru, 0 auto-mint/claim, 0 EARLY lead baru (Soul Agent sudah dilaporkan 2026-11-05, TIDAK dilaporkan ulang; ditambahkan kembali ke snapshot karena absen tanpa catatan penghapusan). "
    "THE WALL age-excluded saat ditemukan (first mint 2026-11-01 13:21 WIB, ~127 jam) -> log saja, TIDAK masuk snapshot, TIDAK dilaporkan. "
    "Leg 1 blok 131984013, interval ~20 mnt vs run 1531; 45 NFT + 18 track_c dibaca ulang. "
    "Velocity: PassAgentX LOLOS pertama kali (+262 freeMinted 3838->4100, 13,11/mnt vs prev 0,3287 = 39,88x) TAPI free % UNVERIFIED -> tetap EARLY, bukan promosi, TIDAK dilaporkan. "
    "Crack +158 (7,90/mnt, 3,48x) LOLOS tapi sudah minted-by-user -> informatif saja. AgentB-c047 GAGAL (0,71x). "
    "KING Agent free % kini 27,60% (freeQuota 3333, remainingFree 2413, claimed 920) — sudah strong-lead-gate-blocked, perubahan kaki saja. "
    "StarAgent totalSupply 1609 (+10, umur ~43 jam) — melewati 48 jam ~21:26 WIB malam ini bila belum sold out. "
    "WeZards freeMinted 65/2500 = 2,6%, slot terbuka, tetap EARLY. HIVE totalSupply 1255 flat; minted-by-user (grandfathered). "
    "BOBBIE totalMinted 245 + AgentPad Agent 57: baseline pertama run ini. "
    "Track B binanceai tetap refund/failed (launched=0, failed=None, isRefundPhase=None, totalShares=3110, tokenClaimed(user)=0, tokenBalance(user)=0); pending_claims tetap kosong. "
    "Track C tanpa perubahan substansi (NIULAI phase null->4; ASOC-43cE freeClaimed_user null->0; sisanya null/bacaan pulih). "
    "Bridge 115 kontrak, 7 same_owner_discarded, 0 not in snapshot. "
    "Leg 2 Boltbook: boltbook.ai front page JS shell tanpa teks post; boltbook.fun EN+ZH adalah feed sebenarnya. Post baru: THE WALL (tesnetra.ai, age-excluded), Soul Agent (kipauuu.ai + moez.ai, ~16:10 WIB), Quantumfarm (tnam.ai, 553/777). TeslAgent Model 3 PAID (0,002 BNB/2 share) — bukan lead. "
    "Leg 5a Sourcify 20 kontrak, 2 baru vs hot-leg-seen, 0 sale shape. Leg 3/5b sweep 0 baru (Coracle dikenal; Razor Agent track C 'contracts are not deployed yet'; Piggy Agent excluded; AGENT MAO dikenal, site 530). "
    "Leg 6 komplemen 0 proyek baru (Square/Odaily/PANews 0 mention; DappBay tanpa THE WALL/Soul Agent — absen bukan bukti). "
    "RPC degraded sepanjang run (dataseed1 403; null = UNVERIFIED, bukan nol)."
)
snap["runNote1601_scan_1106"] = (
    "Run 1601: SCAN SUKSES. Pre-flight OK 11,0 dtk (head 131985107, 256 logs / 50 blok). "
    "Window 131984139-131985138 (1000 blok, cap 1000), 40 panggilan Ankr, 0 error, partial=false. "
    "185 NFT, 416 ERC-20 mint. Triase: 111 'first-seen' menurut definisi file (absen dari seen + snapshot) TAPI SEMUA 111 ada di file backfill-*.json -> 0 benar-benar baru; 57 registry_bytes_hit=true, semua di backfill. "
    "0 EARLY lead baru dari scan. Penyebab: seen file utama stale vs cakupan backfill (backfill tidak pernah memperbarui seen file) -> run ini menambahkan SEMUA 185 kontrak scan ke seen file (pemeliharaan seen). "
    "Watermark TIDAK dimajukan run ini (backfill owns it; backfill sudah di 131985479 saat finalize, mencakup window run ini). "
    "Skipped gap 131981413-131984107 milik backfill. "
    "5c: 61 ERC-20 mint_count>=10, 53 sudah dicek, 8 baru dicek (0 dibuang sampling limit), 0 sale shape (semua Sourcify not_verified; 7/8 registry_bytes=true tapi ABI unverified = bentuk unknown, bukan agent-shaped dari bytecode saja). "
    "Top ERC-20 0x78573aB46e5436e126d3eA1fDEf8766Cce4Efd2b (735 mint) sudah dicek, unverified; 0x3dCa077eb687Df96cC987Da0035c8FAD89Ae716C dicek, no-shape."
)
snap["last_run"] = "2026-11-06 run 1601"
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 1601: 1 strong lead baru (Quantumfarm) GATE FAILED -> dilaporkan sekali, TIDAK di-mint. "
    "0 kandidat, 0 EARLY baru, 0 track-B/track-C baru, 0 sellout, 0 age-exclusion (THE WALL age-excluded saat ditemukan, log saja). "
    "PassAgentX velocity PASS pertama kali tapi tetap EARLY (free % unverified). Scan SUKSES, 0 baru.")
snap["timestamp_wib"] = NOW_WIB

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)

# --- 8. Scan-state note (watermark untouched) ---
state["note_1601_scan"] = snap["runNote1601_scan_1106"]
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1, ensure_ascii=False)

# --- 9. Seen file: append ALL 185 scan contracts (seen-file maintenance) ---
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
    # already present: keep earliest first_block (do not overwrite)
seen.setdefault("_meta", {})["last_scan_wib"] = NOW_WIB
seen["_meta"]["last_scan_window"] = "131984139-131985138"
seen["_meta"]["last_scan_added"] = added
seen["_meta"]["contracts_count"] = len(store)
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1, ensure_ascii=False)

# --- 10. Merge 5c checked (8 new) ---
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
print(f"contracts_now={len(snap['contracts'])} track_c_now={len(snap['track_c'])}")
print(f"seen_added={added} seen_total={len(store)}")
print(f"5c before={before} after={after} new={len(new_entries)}")
print("backups: onchain-snapshot.json.bak-20261106-1601 (+state/seen/tcchecked)")
