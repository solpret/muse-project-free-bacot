#!/usr/bin/env python3
"""Merge run 2131 reread + triage + 5a + s1verify + binanceai + grove into onchain-snapshot.json.
INTERVAL 34.6 min (block 132597982 ~21:10 WIB -> 132602589 ~21:45 WIB).
Reports due this run: (1) EARLY LEAD PIXEL MONSTERS (PXMON) 0x3f508d88; (2) TIME CARDS sold out 2000/2000.
No execution: PXMON is early-lead only (never preview/mint); TIME CARDS was gate-blocked strong lead.
Read-only except snapshot."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL = 34.6; BLOCK = 132602589
NOW_WIB = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-2131-reread.json"))
contracts = snap.setdefault("contracts", {}); track_c = snap.setdefault("track_c", {})
n_upd = 0; vel_pass = []
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict): continue
    prev_ts = v.get("totalSupply"); new_ts = r.get("totalSupply")
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts; v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4); v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if v["velocityLegPasses"]: vel_pass.append((name, minted, round(ratio, 2)))
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None: v[k] = r[k]
    fs = v.get("FREE_SUPPLY"); fcl = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fcl, int):
        v["freePctVerified"] = round(100.0 * fcl / fs, 2)
    elif isinstance(fs, int) and fs and isinstance(v.get("freeMinted"), int):
        v["freePctVerified"] = round(100.0 * v["freeMinted"] / fs, 2)
    v["lastReadBlock"] = BLOCK; v["lastReadWib"] = NOW_WIB
    v["runNote2131_1109"] = (f"Run 2131 (blok {BLOCK}, interval {INTERVAL} mnt vs run 2101): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')} fm={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd += 1
n_tc = 0
for name, v in track_c.items():
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict) or not isinstance(v, dict): continue
    if r.get("totalSupply") is not None: v["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None: v["freeMinted"] = r["freeMinted"]
    if r.get("freeSharesRemaining") is not None: v["freeSharesRemaining"] = r["freeSharesRemaining"]
    if r.get("balanceOf_user") is not None: v["balanceOf_user"] = r["balanceOf_user"]
    v["lastReadBlock"] = BLOCK; v["lastReadWib"] = NOW_WIB
    n_tc += 1
# --- TIME CARDS sold out ---
tc = contracts.get("TIME CARDS Genesis")
tc_soldout = False
if isinstance(tc, dict) and tc.get("freeMinted") == 2000 and tc.get("FREE_SUPPLY") == 2000:
    tc["status"] = "sold-out-2026-11-09"
    tc_soldout = True
# --- NEW: PIXEL MONSTERS early lead ---
contracts["PIXEL MONSTERS"] = {
    "address": "0x3f508d8826517123Fdd39c776e55F85Fa188E5fD",
    "name": "PIXEL MONSTERS", "symbol": "PXMON", "kind": "ERC721",
    "status": "early-lead-2026-11-09",
    "totalSupply": 61, "freeMinted": 61, "freeLeft": 1939, "FREE_CAP": 2000,
    "freePctVerified": 3.05, "MAX_SUPPLY": 6000, "mintOpen": 1,
    "mintStart": 1794234933, "mintStartWib": "2026-11-09 21:35:33 WIB",
    "mintEnd": 1794494133, "mintEndWib": "2026-11-12 21:35:33 WIB",
    "paidMinted": 0, "earlyBirdLeft": 300, "remaining": 5938,
    "freeClaimed_user": 0, "balanceOf_user": 0,
    "verifiedAt": "2026-11-09T14:36:09Z", "registry_bytes": True,
    "sourcify": "exact_match",
    "website": None, "websiteNote": "UNVERIFIED run 2131: metode (A) pencarian alamat kontrak + (G) pencarian nama proyek hanya menemukan Pixelmon Ethereum yang tidak terkait; metode (I) tokenURI(1) ter-decode (Thornox 荆棘犀 #1, Rarity Rare, art on-chain SVG) tanpa external_url/external_link. Tidak ada situs proyek ditemukan.",
    "x": "OPTIONAL, unverified; tidak ada bukti diskusi publik run ini; absence never gates execution",
    "firstSeenBlock": 132603670, "firstSeenWib": "2026-11-09 21:36 WIB",
    "lastReadBlock": 132603670, "lastReadWib": NOW_WIB,
    "tokenURI_note": "token #1 Thornox 荆棘犀 #1, Rarity Rare, Type Grass, Card No. 8; deskripsi: PIXEL MONSTERS - pixel monster trading cards for .ai Agent ID wallets on BNB Chain. Art fully on-chain.",
    "runNote2131_1109": "Run 2131 EARLY LEAD (dilaporkan sekali): first-seen via feed Sourcify (verifiedAt 2026-11-09T14:36:09Z); S1-shape (mint+quote+free views+agent) + registry bytes TRUE di bytecode; first mints terverifikasi on-chain (totalSupply 61, freeMinted 61); mintStart 2026-11-09 21:35:33 WIB (umur terverifikasi <=48 jam); free 61/2000 = 3,05%; slot user terbuka (freeClaimed user 0, bal 0). BUKAN kandidat/strong lead (free% <25%); TIDAK PERNAH preview/mint sebagai early lead. Website + X discussion unverified.",
}
# --- NEW: Nova Agent 0x232816a2 age-excluded ---
contracts["Nova Agent-2328"] = {
    "address": "0x232816a2f556b9448f15f3baa3bf9a988922033d",
    "name": "Nova Agent", "kind": "ERC721",
    "status": "age-excluded-2026-11-09",
    "totalSupply": 9900, "totalMinted": 9900, "MAX_SUPPLY": 10000,
    "registry_bytes": True, "balanceOf_user": 0,
    "firstDetected": "2026-11-03 19:02 WIB",
    "firstDetectedSource": "Boltbook post /p/0Tr4g9WtSXrd by tungquan42.ai (recheck 21:35 WIB 2026-11-09)",
    "sourcify": "UNVERIFIED (per post)",
    "lastReadBlock": 132603122, "lastReadWib": NOW_WIB,
    "runNote2131_1109": "Run 2131: baru via Boltbook front page; 9.900/10.000 free (99,0%) per post, terkonfirmasi on-chain totalSupply 9900/10000. AGE-EXCLUDED: pertama terdeteksi monitor 2026-11-03 19:02 WIB (>48 jam sebelum run, ~6 hari) dan belum sold out -> gugur per aturan umur; TIDAK dilaporkan sebagai lead/kandidat. Kontrak Nova Agent kedua (0x0e881e6b...) sudah ada di snapshot sebagai watchlist-only-2026-11-08 (ts flat 9901 run ini).",
}
# --- NEW: Flare Agent watchlist-only age-unverified ---
contracts["Flare Agent"] = {
    "address": "0xe2deb47514bbfd19550866c8820bce04e8a8d416",
    "name": "Flare Agent", "kind": "ERC721",
    "status": "watchlist-only-age-unverified-2026-11-09",
    "totalSupply": 9901, "MAX_SUPPLY": 10000,
    "registry_bytes": True, "balanceOf_user": 0,
    "sourcify": "UNVERIFIED (per post)",
    "firstSeenWib": "2026-11-09 21:42 WIB",
    "firstSeenSource": "Boltbook post /p/hsVgKC8CZDMy by duyenvu75.ai",
    "lastReadBlock": 132603122, "lastReadWib": NOW_WIB,
    "runNote2131_1109": "Run 2131: baru via Boltbook front page; 9.901/10.001 free (99,0%) per post, terkonfirmasi on-chain totalSupply 9901/10000 (angka post 10.001 vs MAX_SUPPLY 10.000 tidak klop persis). UMUR UNVERIFIED: post tanpa waktu launch; tidak ada view mintStart/startTime/SALE_START/launchTime di kontrak; BscScan txlist gagal (respons non-JSON). Template sama dengan Nova (code_len 13598, registry bytes TRUE) tapi umur tidak boleh diasumsikan dari Nova. Website + X unverified. BUKAN lead; TIDAK dilaporkan; watchlist-only.",
}
# --- NEW: CHIPS excluded free-exhausted ---
contracts["CHIPS (Chipmunks)"] = {
    "address": "0xb2625d56a7fc855bf7432b5584b390a4b4d9c7fd",
    "name": "CHIPS", "symbol": "CHIPS", "kind": "ERC721",
    "status": "excluded-free-exhausted-2026-11-09",
    "totalSupply": 3349, "totalMinted": 3349, "MAX_SUPPLY": 6666, "mintOpen": 1,
    "registry_bytes": False, "balanceOf_user": 0, "freeMinted_user": 0,
    "lastReadBlock": 132603122, "lastReadWib": NOW_WIB,
    "runNote2131_1109": "Run 2131: baru via Boltbook post /p/QTpeJozgC240 (zanbryan.ai, blok 132.602.061): totalSupply 3.343/6.666 terkonfirmasi on-chain 3349/6666. FREE LANE TUTUP GLOBAL: mint(1) value 0 revert 0x788a686f (free quota exhausted) untuk semua wallet; satu-satunya jalan berbayar quote 0,0009667 BNB. -> EXCLUDED (bukan free mint lagi); TIDAK dilaporkan sebagai lead.",
}
# --- NEW track_c: 0x4Bc1A172 sale, not yet open ---
track_c["0x4Bc1A172-sale"] = {
    "sale": "0x4Bc1A1723a5D8A893695f78c8b2cD39028478d43",
    "token": "0x8f37cbd8c1b9214f2550ce49a1365275b42ac588",
    "name": None, "status": "watchlist-only-not-open-2026-11-09",
    "saleShape": "S1: mint+quoteCost/quoteTokens+freeMinted+REGISTRY()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact + registry bytes TRUE; token() = 0x8f37cbd8c1b9214f2550ce49a1365275b42ac588 (juga ada di feed Sourcify run ini)",
    "MAX_FREE_SHARES": 100, "freeMinted": 0, "MAX_SHARES": 1000, "TOTAL_SHARES": 1000,
    "TOKENS_PER_SHARE": 100000000000000000000000,
    "SALE_START": 1794286800, "SALE_START_WIB": "2026-11-10 12:00:00 WIB",
    "SALE_END": 1794373200, "SALE_END_WIB": "2026-11-11 12:00:00 WIB",
    "saleActive": 0, "mintOpen": 0, "opened": 0, "openedAt": 0,
    "totalMinted": 0, "totalSold": 0, "soldOut": 0,
    "sharesOf_user": 0, "quoteCost_user_1": None, "quoteTokens_user_1": None,
    "verifiedAt": "2026-11-09T14:25:54Z",
    "lastReadBlock": 132603670, "lastReadWib": NOW_WIB,
    "runNote2131_1109": "Run 2131: S1 hit ke-2 dari feed Sourcify (25 alamat). Sale BELUM BUKA (saleActive 0, opened 0, SALE_START 2026-11-10 12:00 WIB) -> watchlist-only-not-open, BUKAN lead/kandidat track-C; TIDAK dilaporkan; dicek ulang saat buka. Free pool 100/100 belum tersentuh; quoteCost/quoteTokens revert (sale belum buka, wajar).",
}
snap["last_run"] = 2131
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 2131: 612 kontrak + 85 track_c re-read (blok 132602589, 473,4 dtk); "
    "1 EARLY LEAD BARU PIXEL MONSTERS (PXMON) 0x3f508d88 (free 61/2000=3,05%, mintStart 2026-11-09 21:35:33 WIB, registry bytes, Sourcify exact_match); "
    "TIME CARDS Genesis SOLD OUT 2000/2000 (strong lead gate-blocked -> sold-out, lapor sekali); "
    "Nova 0x232816a2 age-excluded (terdeteksi 2026-11-03); Flare watchlist-only umur unverified; CHIPS free lane tutup global -> excluded; "
    "sale 0x4Bc1A172 S1-hit belum buka (buka 2026-11-10 12:00 WIB); scan fast-fail Ankr 401 (watermark 132512564, gap ~90 rb blok); binanceai tetap refund; Grove belum buka.")
snap["runNote2131_1109"] = snap["last_run_note"]
snap["runNote2131_1109_scan"] = ("Run 2131 route 4: SCAN FAST-FAIL - Ankr pre-flight HTTP 401 (4,0 dtk, head 132602588), "
    "outage sejak ~13:33 WIB 2026-11-09; watermark TETAP 132512564, gap ~90.024 blok ke head saat preflight. "
    "Backfill bukan tugas job ini.")
snap["runNote2131_1109_binanceai"] = ("Run 2131 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (probe dataseed, blok 132602607). "
    "Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote2131_1109_5a"] = ("Run 2131 route 5a: 25 alamat feed Sourcify (14:05-14:41Z), 2 S1 hit. (1) 0x3f508d88 PIXEL MONSTERS -> EARLY LEAD "
    "(terverifikasi on-chain run ini, blok 132603670). (2) 0x4Bc1A172 share sale -> S1 terverifikasi, sale BELUM BUKA (SALE_START 2026-11-10 12:00 WIB) -> watchlist-only-not-open. "
    "23 lainnya S1/S2 False. 5c: tidak ada output scan baru (scan fast-fail sejak 13:33); tidak ada ERC-20 baru dicek run ini.")
snap["runNote2131_1109_early_leads"] = ("Run 2131 EARLY LEAD: PIXEL MONSTERS (PXMON) 0x3f508d8826517123Fdd39c776e55F85Fa188E5fD - "
    "Sourcify exact_match verifiedAt 2026-11-09T14:36:09Z; freeMint/freeLeft/freeMinted + FREE_CAP 2000 + registry 0x60B926...22F di bytecode; "
    "first mints terverifikasi on-chain (totalSupply 61, freeMinted 61, blok 132603670); mintStart 2026-11-09 21:35:33 WIB (umur <=48 jam terverifikasi); "
    "free 61/2000 = 3,05%; slot user terbuka (freeClaimed user 0, bal 0); token #1 Thornox 荆棘犀 #1 (Rare, on-chain art); "
    "website UNVERIFIED (metode A/G/I); X discussion UNVERIFIED. Hot leg melihatnya di feed 21:39/21:44 tapi TIDAK melaporkannya (leg3 none) - job utama melaporkan sekali sebagai EARLY. "
    "Bukan kandidat/strong lead; TIDAK preview/mint.")
snap["runNote2131_1109_velocity"] = ("Run 2131 velocity LOLOS: " + "; ".join(f"{n} +{m} ({r}x)" for n, m, r in vel_pass) +
    ". Tidak ada yang promotable: TIME CARDS sold out; Dragon Agent free%/umur unverified (tetap early lead); Undead NFTs free% unverified; "
    "Sidecoo/Rose/Aura/PixelSentinels/AgentX free%/umur unverified; Borealux free% 51,73% tapi umur+website unverified + velocity ratio tidak terkonfirmasi; Skyagent sudah age-excluded.")
snap["runNote2131_1109_discovery"] = ("Run 2131 rute 2: Boltbook EN 44.867 byte + ZH 45.087 byte, rc 200; 13 alamat unik; baru: Nova 0x232816a2 (age-excluded), "
    "Flare 0xe2deb475 (watchlist-only umur unverified), CHIPS 0xb2625d56 (free-exhausted -> excluded); 0x8269... = BoltRewards (footer, bukan proyek); 0xe17b... = tx hash TIME CARDS. "
    "Stickman 556/4.444 tanpa alamat di post (pace <1/jam, 12,5%) - tidak bisa ditriase, bukan lead. SENSHI 3/10.000, PAID ladder mulai $0,50 (senshisaga.vercel.app, X @senshisaganft) - bukan free mint, checked-not-lead, tanpa alamat di post. "
    "Rute 3: sweep EN - MOLT AGENT sudah di snapshot (bukan baru); HOPKIN sudah di snapshot, season berakhir 2026-11-09 12:00 UTC; sisanya (AgentForge, Pixel Fox, BLOB, PocketDragons, Radar Pass) sudah lewat umur/checked. "
    "Rute 6: Odaily 255.496 byte + PANews 119.240 byte, rc 200, 0 mention Agent ID/free-mint. DappBay tidak dikonsultasikan (tidak ada kandidat yang memerlukannya). "
    "Bridge: tidak berubah (mtime 2026-11-08 18:21 UTC); 8 alamat bridge tidak ada di snapshot semuanya temuan scan ERC-20 yang sudah diklasifikasi NOT-a-lead oleh scan job (ORE, ETHBack tracker x2, IKIGAI, AGC token, KRILL same-owner-discarded, PANBA, unnamed ERC20) - tidak ditambahkan ke snapshot, tidak dilaporkan.")
snap["runNote2131_1109_grove"] = ("Run 2131 Grove: freeOpen=0 (blok 132601005, grove-check job 21:31 WIB, file run-2026-11-09-2131-grove-check.json) - belum buka.")
snap["runNote2131_1109_fma"] = ("Run 2131 FMA: totalSupply 482.000 -> 505.000 token (505 mint, +23); freeMinted view gagal baca run ini (nilai lama 482 dipertahankan); status tetap watchlist-only-age-website-unverified-2026-11-09.")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE {NOW_WIB} updated={n_upd} track_c={n_tc} vel_pass={vel_pass} tc_soldout={tc_soldout}")
print("contracts now:", len(snap["contracts"]), "track_c now:", len(snap["track_c"]))
