#!/usr/bin/env python3
"""Merge run 2026-11-10 09:01 WIB into onchain-snapshot.json. Read-only on
state except the snapshot itself. Backup first. View-aware velocity: uses the
operative supply view per contract (totalSupply or totalMinted per supplyView)
so a view-mix cannot fake a velocity pass (Tigora lesson run 0901).
Removals-as-sold-out: Lenx Agent Pass + Night Bandits Club (status sold-out,
entries kept per snapshot convention like Jiayoupanda/Gondolux).
Adds: SEVENFOLD (watchlist-only), ConcheryPass + UMBRA (checked-not-lead
age-excluded)."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap_path = f"{BASE}/onchain-snapshot.json"
shutil.copy(snap_path, f"{snap_path}.bak-0901-premerge")
snap = json.load(open(snap_path))
rr = json.load(open(f"{BASE}/run-2026-11-10-0901-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-10-0901-vel.json"))
BLOCK = rr["block"]
INTERVAL = vel["interval_min"]  # 31.5
TS_WIB = "2026-11-10 09:01 WIB"

FREE_FIELDS = ["freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY",
               "mintOpen", "balanceOf_user", "freeClaimed_user"]

updated = 0
for name, entry in snap["contracts"].items():
    if not isinstance(entry, dict):
        continue
    fresh = rr["reread"].get(name)
    if not fresh:
        continue
    view = "totalMinted" if str(entry.get("supplyView", "")).startswith("totalMinted") else "totalSupply"
    new = fresh.get(view)
    if new is None:
        # keep old values on read failure; still refresh free views below
        pass
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
            entry[view] = new
        entry["lastReadBlock"] = BLOCK
        entry["lastReadWib"] = TS_WIB
        updated += 1
    for f in FREE_FIELDS:
        if fresh.get(f) is not None:
            entry[f] = fresh[f]
    # balanceOf_user lives under a different key in reread output
    if fresh.get("balanceOf_user") is not None:
        entry["balanceOf_user"] = fresh["balanceOf_user"]
        entry["userBalance"] = fresh["balanceOf_user"]

# --- track_c: refresh freeMinted/totalSupply (non-None only) ---
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

def note(name, key, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e[key] = text

note("FCAT Agents", "runNote0901_1110",
     "Run 0901 (blok 132693151, interval 31,5 mnt): totalSupply 347->358 (+11), "
     "freeClaimed 358/888 = 40,3% TERVERIFIKASI (naik dari 39,1% run 0831); "
     "velocity GAGAL (0,35/mnt vs prev 0,60 = 0,58x). Slot TERBUKA (bal 0). "
     "Umur UNVERIFIED + website GATE FAILED — tetap watchlist-only, BELUM strong lead. TIDAK preview/mint.")
note("JINCHAN Agents", "runNote0901_1110",
     "Run 0901 (blok 132693151): totalSupply 208->214 (+6), freeClaimed 214/888 = 24,1% "
     "TERVERIFIKASI (naik dari 23,4% run 0831). <25% strong-lead leg. Velocity GAGAL "
     "(0,19/mnt vs prev 0,53 = 0,36x). Slot terbuka (bal 0). Umur/website UNVERIFIED. Tetap watchlist-only.")
note("THYRK", "runNote0901_1110",
     "Run 0901 (blok 132693151): totalSupply 1935->2173 (+238), freeMinted 2154 (tanpa free cap; "
     "% leg N/A). Velocity GAGAL (7,56/mnt vs prev 5,34 = 1,41x < 1,5x). Slot user TERPAKAI "
     "(bal 1, mint #6849). Website thyrk.fun TERVERIFIKASI. Umur presisi UNVERIFIED. Tetap early lead.")
note("Sakura", "runNote0901_1110",
     "Run 0901 (blok 132693151): totalSupply 1246->1263 (+17), freeMinted 1253/6000 = 20,9% "
     "(<25% dan <50%). Velocity GAGAL (0,54/mnt vs prev 1,20 = 0,45x). Slot UNVERIFIED "
     "(freeClaimed user revert), website GATE FAILED. Tetap early lead.")
note("Roguefall", "runNote0901_1110",
     "Run 0901 (blok 132693151, interval pertama 24,4 mnt sejak baca 0831 blok 132689899): "
     "totalSupply 983->1022 (+39), freeMinted 1016/2000 = 50,8% TERVERIFIKASI "
     "(naik dari 48,85%). Rate interval pertama 1,60/mnt = BASELINE (velocity TIDAK lulus "
     "pada interval pertama). Slot TERBUKA (bal 0). Umur UNVERIFIED + website GATE FAILED — "
     "tetap watchlist-only, BUKAN strong lead/kandidat. TIDAK preview/mint.")
note("Roguefall", "velocityNote0901",
     "Run 0901: rate interval pertama 1,60/mnt (39 token / 24,4 mnt) = baseline; velocity TIDAK lulus.")
e = snap["contracts"].get("Roguefall")
if isinstance(e, dict):
    e["previousTotalSupply"] = 983
    e["mintedInInterval"] = 39
    e["intervalMinutes"] = 24.4
    e["previousRatePerMin"] = None
    e["currentRatePerMin"] = 1.598360655737705
    e["velocityRatio"] = None
    e["velocityLegPasses"] = False
    e["freePctVerified"] = 50.8
note("HIVE Agents", "runNote0901_1110",
     "Run 0901 (blok 132693151): totalSupply 1259->1259 (+0), velocity GAGAL; "
     "free=None/1000; bal_user=1; status minted-by-user-2026-11-02.")
note("Bubblebruin", "runNote0901_1110",
     "Run 0901 (blok 132693151): totalSupply 2394->2395 (+1), freeClaimed 2389/7777 = 30,7%; "
     "velocity GAGAL; bal_user=1; status minted-by-user-2026-11-01.")
note("Tigora-E8c4", "runNote0901_1110",
     "Run 0901: KOREKSI analisis velocity — +420 semu (view-mixing: totalSupply snapshot 619 "
     "yang basi vs totalMinted segar 1039). View operative totalMinted: 1038->1039 (+1), "
     "rate 0,06/mnt vs prev 0,074 = 0,86x -> velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED, "
     "website UNVERIFIED. Tetap early lead, TIDAK promosi.")
note("MONOLITH", "runNote0901_1110",
     "Run 0901 (blok 132693151): totalSupply 644->645 (+1), velocity GAGAL. "
     "Deadline umur 2026-11-10 17:32 WIB belum lewat (~8 jam lagi). Age-watch.")
note("King's Game", "runNote0901_1110",
     "Run 0901 (blok 132693566, special2): totalMinted/freeMinted flat 3, balanceOf(user)=0. "
     "Launch UNVERIFIED (first-seen 2026-11-07 21:06 hanya lower bound) — deadline 48 jam "
     "atas first-seen sudah lewat, tapi preseden run-run sebelumnya: tetap age-watch (launch "
     "tidak terverifikasi, tidak dihapus). Tanpa perubahan.")
note("Lenx Agent Pass", "runNote0901_1110",
     "Run 0901 SELLOUT (dilaporkan sekali run ini): freeMinted 1000/1000 = FREE_CAP, "
     "freeRemaining 0 (baca segar special2 blok 132693566). freeMinted sudah terbaca 1000 sejak "
     "run 0701, tapi run 0701-0831 menahan kesimpulan karena totalSupply basi 128 tampak tidak "
     "konsisten; freeRemaining=0 kini menguatkan sebagai view kedua -> sellout TERVERIFIKASI. "
     "User tidak pernah mint (bal 0, freeClaimed(user)=0). Status -> sold-out-2026-11-10.")
snap["contracts"]["Lenx Agent Pass"]["status"] = "sold-out-2026-11-10"
snap["contracts"]["Lenx Agent Pass"]["freeRemaining"] = 0
snap["contracts"]["Lenx Agent Pass"]["freeMinted"] = 1000
snap["contracts"]["Lenx Agent Pass"]["totalMinted"] = 1000
note("Night Bandits Club", "runNote0901_1110",
     "Run 0901 SELLOUT + AGE-EXCLUDED (dilaporkan sekali run ini): freeUsed 444/444 = freeTotal "
     "(baca segar special2 blok 132693566; baca sukses terakhir 250/444 pada 2026-11-07 18:47 WIB; "
     "LEAN re-read tidak mencakup freeUsed sehingga tidak terlihat di run-run sebelumnya). "
     "Umur juga lewat 48 jam (launch terverifikasi 2026-11-07 18:02:28 WIB, deadline 2026-11-09 "
     "18:02 WIB). User tidak pernah mint (bal 0, freeTakenBy=0). Status -> sold-out-2026-11-10.")
snap["contracts"]["Night Bandits Club"]["status"] = "sold-out-2026-11-10"
snap["contracts"]["Night Bandits Club"]["freeUsed"] = 444
snap["contracts"]["Night Bandits Club"]["freeTotal"] = 444

# --- SEVENFOLD: baru dari Boltbook run 0901, watchlist-only ---
snap["contracts"]["SEVENFOLD"] = {
    "address": "0x4ca724a354db4f743607ecc1a5f117b2e617c8ae",
    "name": "SEVENFOLD",
    "symbol": "SVN",
    "kind": "ERC721",
    "status": "watchlist-only-2026-11-10-discovery-0901",
    "totalSupply": 630,
    "MAX_SUPPLY": 7777,
    "agentFreeCap": 3000,
    "agentFreeUsed": 629,
    "freeMinted": 629,
    "freePctVerified": 20.97,
    "mintOpen": 1,
    "mintStart": 1794270788,
    "mintEnd": 1794702788,
    "PRICE": 1700000000000000,
    "userBalance": 0,
    "mintedBy_user": 0,
    "freeUsedByWallet_user": 0,
    "firstSeenBlock": 132691611,
    "firstSeenWib": "2026-11-10 07:33:08 WIB",
    "discovery": "Boltbook front page run 0901 (post bunnysuny.ai 'SEVENFOLD at 500 after 80 minutes') "
                 "-> follow-up post /p/K2mvBW1Q_K1i; alamat mint lengkap dari post. Hot leg sudah "
                 "melihat kontrak ini 07:34 WIB (checked-not-sale-shape, track C saja).",
    "agentShape": "TERVERIFIKASI: Sourcify exact_match; REGISTRY() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F "
                  "(registry resmi); agentFreeCap/agentFreeUsed/freeMinted/mintStart/mintEnd/freeMintX di ABI.",
    "launchNote": "Umur TERVERIFIKASI: mintStart() on-chain = 2026-11-10 07:33:08 WIB; umur ~1,5 jam "
                  "saat run 0901 (<=48 jam). mintEnd 2026-11-15 07:33:08 WIB.",
    "website": None,
    "xVerified": False,
    "websiteVerified": False,
    "velocityVerified": False,
    "baselineNote": "Watchlist-only run 0901: umur terverifikasi <=48 jam + slot user TERBUKA "
                    "(bal 0, mintedBy 0, freeUsedByWallet 0), TAPI free 629/3000 = 21,0% (<25% "
                    "strong-lead leg) dan first mint BUKAN di run ini (first-seen hot leg 07:34 WIB) "
                    "-> BUKAN early lead (aturan first-mint-di-run) dan BUKAN strong lead. Website/X "
                    "UNVERIFIED. TIDAK preview/mint, TIDAK dilaporkan ke chat.",
    "lastReadBlock": 132696655,
    "lastReadWib": "2026-11-10 09:01 WIB",
}

# --- ConcheryPass: S1 baru dari feed, age-excluded ---
snap["contracts"]["ConcheryPass"] = {
    "address": "0xcb65F7Ec831cF8a27093664B1AA933b09579FA4D",
    "name": "Conchery",
    "symbol": "CNCHRY",
    "kind": "ERC721",
    "status": "checked-not-lead-age-excluded-2026-11-10",
    "totalSupply": 670,
    "totalMinted": 671,
    "MAX_SUPPLY": 5555,
    "FREE_SUPPLY": 1111,
    "freeMinted": 641,
    "freePctVerified": 57.7,
    "mintOpen": 1,
    "mintStart": 1792203553,
    "mintEnd": 1792645873,
    "userBalance": 0,
    "firstSeenWib": "2026-11-10 09:01 WIB",
    "discovery": "Route 5a Sourcify feed run 0901 (baru vs feed 0831; verifiedAt 2026-11-10T01:44:03Z).",
    "agentShape": "TERVERIFIKASI: Sourcify exact_match; mint() + quote(address,uint256) + free views "
                  "(freeAvailable/freeMinted/freeUsed) + AGENT_ID_REGISTRY() = registry resmi "
                  "(terkonfirmasi on-chain via eth_call). Bentuk S1 LOLOS.",
    "launchNote": "Umur TERVERIFIKASI >48 jam: mintStart() on-chain = 2026-10-21 04:19 WIB "
                  "(mintEnd 2026-10-26 11:51 WIB) -> AGE-EXCLUDED, bukan kandidat/lead. Keanehan: "
                  "mintEnd sudah lewat tapi mintOpen() masih true.",
    "website": None,
    "xVerified": False,
    "velocityVerified": False,
    "baselineNote": "Checked-not-lead run 0901: S1 lolos + free 641/1111 = 57,7% + slot user terbuka "
                    "(freeUsed=false, freeAvailable=1, quote(user,1)=0) TAPI umur >48 jam terverifikasi "
                    "-> AGE-EXCLUDED. TIDAK preview/mint, TIDAK dilaporkan ke chat.",
    "lastReadBlock": 132693151,
    "lastReadWib": "2026-11-10 09:01 WIB",
}

# --- UMBRA: sweep rute 3, age-excluded dari tanggal post ---
snap["contracts"]["UMBRA Agents"] = {
    "address": "0x9C0309dC71F89d7f4F0b55d934213C28F10C9e23",
    "name": "UMBRA Agents",
    "kind": "ERC721",
    "status": "checked-not-lead-age-excluded-2026-11-10",
    "firstSeenWib": "2026-11-10 09:01 WIB",
    "discovery": "Route 3 sweep run 0901 (browser.search).",
    "launchNote": "Umur >48 jam dari sumber post 2026-10-27 (~14 hari lalu); launch on-chain "
                  "TIDAK diverifikasi run ini. Dicatat sebagai proyek lama agar tidak di-triage ulang.",
    "website": None,
    "xVerified": False,
    "velocityVerified": False,
    "baselineNote": "Checked-not-lead run 0901: umur jauh >48 jam dari tanggal post -> AGE-EXCLUDED. "
                    "TIDAK preview/mint, TIDAK dilaporkan ke chat.",
    "lastReadBlock": BLOCK,
    "lastReadWib": TS_WIB,
}

# --- track_c notes ---
tc = snap.get("track_c", {})
if isinstance(tc.get("NUSA"), dict):
    tc["NUSA"]["freeMinted"] = 363
    tc["NUSA"]["runNote0901_1110"] = (
        "Run 0901 (blok 132693566, special2): freeMinted 362->363 (+1); sharesMinted 370; "
        "soldOut=0, closed=0; freeAvailable(user)=1, freeClaimed(user)=0, saldo token user=0. "
        "Slot user masih terbuka, TAPI gate TETAP FAILED (hot-leg 17:04, methods A-H) -> "
        "TIDAK di-preview/TIDAK di-mint (TRACK-C LEAD DIRECT MINT butuh gate lolos). "
        "Umur: first mint 2026-11-08 17:05:23 WIB, deadline 48 jam 2026-11-10 17:05 WIB belum lewat.")
if isinstance(tc.get("BOME-50CD"), dict):
    tc["BOME-50CD"]["runNote0901_1110"] = (
        "Run 0901 (blok 132693566, special2): TIDAK BERUBAH — mintOpen=0, opened=0, "
        "FREE_CAP=1000, freeLotsMinted=0 (pool 1000/1000), freeUsed(user)=0. Sale masih belum dibuka.")
if isinstance(tc.get("FOUNT"), dict):
    tc["FOUNT"]["runNote0901_1110"] = (
        "Run 0901: freeMinted flat 1000, totalSupply 1e27, balance user=0. Tanpa perubahan.")
if isinstance(tc.get("PACTA"), dict):
    tc["PACTA"]["runNote0901_1110"] = (
        "Run 0901: freeMinted flat 55, sharesMinted=57, soldOut=0, freeClaimed(user)=0. "
        "Status excluded-free-pool-exhausted-2026-11-09, tanpa perubahan.")
if isinstance(tc.get("COSO v2"), dict):
    tc["COSO v2"]["runNote0901_1110"] = (
        "Run 0901: freeMinted 643->651 (+8). Status age-excluded-2026-11-10, tanpa perubahan status.")

snap["runNote0901_1110_binanceai"] = (
    "Run 0901 track-B: binanceai.fun TIDAK BERUBAH — launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0 (blok 132693566, special2). "
    "Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote0901_1110_grove"] = (
    "Run 0901 Grove: TIDAK BERUBAH — freeOpen=0, freeMinted=2500/2500, FREE_SUPPLY=2500, "
    "MAX_SUPPLY=12500, freeClaimed(user)=0, balance user=0 (blok 132693566, special2).")

snap["runNote0901_1110"] = (
    "Run 0901 (2026-11-10 09:01-09:5x WIB, blok 132693151, interval 31,5 mnt): re-read 633 kontrak + "
    "75 track_c, 131 totalSupply None (degradasi eth_call, nilai lama dipertahankan). "
    "Velocity LOLOS (terkoreksi): 0 — Tigora +420 adalah artefak view-mixing (totalMinted +1, 0,86x); "
    "THYRK +238 tapi 1,41x <1,5x; Roguefall baseline pertama 1,60/mnt (tidak lulus). "
    "SELLOUT BARU (dilaporkan sekali): Lenx Agent Pass (free 1000/1000, freeRemaining 0) + "
    "Night Bandits Club (freeUsed 444/444; umur juga lewat 48 jam). Keduanya user tidak pernah mint. "
    "FCAT 40,3% verified, JINCHAN 24,1% verified — tetap watchlist-only. Sakura 20,9% "
    "verified, THYRK free% N/A (tanpa free cap) — tetap early lead. "
    "SEVENFOLD BARU watchlist-only (umur terverifikasi 07:33 WIB, free 629/3000=21,0%, slot terbuka; "
    "bukan early/strong lead). ConcheryPass S1 baru tapi AGE-EXCLUDED (mintStart 2026-10-21). "
    "UMBRA age-excluded (post 27 Okt). NUSA freeMinted 363, gate tetap FAILED. BOME-50CD masih belum "
    "dibuka. Binanceai/Grove tidak berubah. Ankr 401 fast-fail; watermark tetap 132512564.")
snap["runNote0901_1110_scan"] = (
    "Route 4 scan: FAST-FAIL. Pre-flight ankr_getLogs 50 blok (head 132693339): FAIL 7,9 dtk "
    "HTTP 401 Unauthorized. Kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. Scan leg TIDAK "
    "dijalankan; watermark tetap 132512564; gap ke head ~180.775 blok dan tumbuh. 5c dilewati "
    "(tanpa output scan).")
snap["last_run_wib"] = "2026-11-10 09:01 WIB"
snap["timestamp_wib"] = "2026-11-10 09:01 WIB"

json.dump(snap, open(snap_path, "w"), indent=1, ensure_ascii=False)
print("merged. contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]),
      "updated reads:", updated, "tc fields:", tc_updated)
