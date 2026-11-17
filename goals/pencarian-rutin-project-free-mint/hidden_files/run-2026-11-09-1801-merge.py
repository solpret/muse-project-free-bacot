#!/usr/bin/env python3
"""Merge run 1801 reread + triage + focused checks into onchain-snapshot.json.
Preserves old values when fresh reads are None (read artifact, not zero).
Writes run-2026-11-09-1801-merge.json (summary)."""
import json, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-1801-reread.json"))
tri = json.load(open(f"{BASE}/run-2026-11-09-1801-triage-new.json"))
focus = json.load(open(f"{BASE}/run-2026-11-09-1801-trackc-focus.json"))
INTERVAL = 15.8  # minutes, block timestamps 132571528 (17:50:41) -> 132573635 (18:06:29)
BLOCK = rr.get("block")
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
n_upd = 0
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict):
        continue
    prev_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply")
    # velocity (only when both supplies are ints)
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4)
        v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
    # fresh non-None values overwrite
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    # free pct recompute
    fs = v.get("FREE_SUPPLY")
    fc = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fc, int):
        v["freePctVerified"] = round(100.0 * fc / fs, 2)
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = "2026-11-09 18:0x WIB"
    v["runNote1801_1109"] = (
        f"Run 1801 (blok {BLOCK}, interval {INTERVAL} mnt vs run 1731): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')}; bal_user={v.get('balanceOf_user')}; "
        f"status {v.get('status')}."
    )
    n_upd += 1
# track_c reread merge (lean views only)
n_tc = 0
for name, v in track_c.items():
    if not isinstance(v, dict):
        continue
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict):
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = "2026-11-09 18:0x WIB"
    v[f"runNote1801_1109"] = f"Run 1801 (blok {BLOCK}): totalSupply={r.get('totalSupply')} freeMinted={r.get('freeMinted')} freeSharesRemaining={r.get('freeSharesRemaining')} bal_user={r.get('balanceOf_user')}."
    n_tc += 1
# focused track_c notes
FOCUS_NOTES = {
 "DROID": "Run 1801 (blok 132575087): opened 0 (MASIH BELUM DIBUKA), freeMinted 736/2000 FREE_SHARES, totalMinted 736, paused 0 - tetap watchlist-only-not-open.",
 "OSK": "Run 1801 (blok 132575087): opened 0 (MASIH BELUM DIBUKA; saleStart 2026-11-03 23:32:53 WIB, saleEnd 2026-11-06 23:32:53 WIB sudah lewat tanpa dibuka), totalMinted 2278 - tetap watchlist-only-not-open.",
 "IMARS": "Run 1801 (blok 132575087): opened 1 (terbuka sejak run 0231, sudah dilaporkan), freeMinted 300/300 FREE_SHARES (pool gratis habis), totalMinted 624 - tetap excluded, BUKAN lead.",
 "NIULAI": "Run 1801 (blok 132575087): launched 0 (MASIH BELUM DIBUKA), freeClaimed 4444/4444 freeShares, phase 4 - tetap watchlist-only-not-open.",
 "KillZero-K0-sale": "Run 1801 (blok 132575087): launched 0 (MASIH BELUM DIBUKA), totalFreeClaimed 0, FREE_SHARES 0, totalMintCount 216 - tetap watchlist-only-not-open.",
 "0x260bf39a-sale": "Run 1801 (blok 132575087): launched 0, launchTime 0 (MASIH BELUM DIBUKA), FREE_SLOTS 500, freeClaimed 500/500 (pool terisi penuh sebelum dibuka) - tetap watchlist-only-not-open; bila kelak dibuka, pool gratis sudah habis.",
 "BoxBigem-3Ee9": "Run 1801 (blok 132575087): freeMinted 7.76e26/1e28 FREE_POOL (7,76%), freeRemaining 9.224e27, mintStart 2026-11-04 21:30 WIB, mintEnd 2026-11-07 21:30 WIB (jendela mint sudah lewat), umur unverified - tetap watchlist-only-age-unverified.",
 "DeY": "Run 1801 (blok 132575087): freeCount 2/1000 FREE_SLOTS (998 tersisa), freeByAddress(user)=0 (slot TERBUKA) - tetap track-c-lead-gate-blocked (tidak ada website terverifikasi).",
 "FANBEIMAO-824d": "Run 1801 (blok 132575087): freeCap 2000, freeSold 1124 (naik dari 894 run 2101; 876 tersisa), isFreeOpen 0 - tetap track-c-lead-gate-blocked (tidak ada website terverifikasi).",
}
for k, note in FOCUS_NOTES.items():
    if k in track_c and isinstance(track_c[k], dict):
        track_c[k]["runNote1801_1109_focus"] = note
# --- status changes / new entries ---
# 1. Osiris Guardians -> age-excluded
osiris = contracts.get("Osiris Guardians")
if osiris is not None:
    osiris["status"] = "age-excluded-2026-11-09"
    osiris["ageExclusionEvidence1801"] = (
        "Launch <= 2026-11-04 01:31:46 WIB: bridge (scan-tracked run-17) mencatat free mint Osiris #490 "
        "dalam jendela blok 131471151-131483364; jendela itu terverifikasi independen run ini via dataseed "
        "eth_getBlockByNumber: blok 131471151 = 2026-11-04 00:15:20 WIB, blok 131483364 = 2026-11-04 01:46:58 WIB "
        "(mint 01:31:46 jatuh di dalam jendela). Umur saat run 1801 ~5 hari 17 jam > 48 jam. "
        "Belum sold out: freeMinted 1275/2222 = 57,4% (run 1731, blok 132571528, 17:50 WIB); "
        "Boltbook recheck 1248/2222 ~17:29 WIB. Deep-dive getLogs langsung gagal run ini: "
        "Ankr 401 (pre-flight) + dataseed eth_getLogs -32005 limit exceeded di semua ukuran jendela. "
        "Dihapus dari watchlist aktif (status dipertahankan agar tidak ditambahkan ulang); dilaporkan sekali run 1801."
    )
    osiris["launchNote"] = "Usia peluncuran TERVERIFIKASI >48 jam (lihat ageExclusionEvidence1801)."
# 2. ALL ACCESS -> sold out
aa = contracts.get("ALL ACCESS")
if aa is not None:
    aa["status"] = "sold-out-2026-11-09"
    aa["soldOutEvidence1801"] = ("totalSupply 1500/1500 (triage run 1801 blok 132574569; reread 1499 blok 132573635; "
        "Boltbook recheck 1483/1500 ~17:34 WIB). Cap 1500 per post Boltbook. Watchlist-only, bukan lead yang dilaporkan - log saja.")
# 3. LIKHIN note: free pool exhausted per site stats
lik = contracts.get("LIKHIN")
if lik is not None:
    lik["runNote1801_1109_likhin"] = ("Run 1801 (sweep): /api/stats likhin.pages.dev segar: freeMinted 2.000/2.000, "
        "totalMinted 2.072, freePhase false - pool gratis HABIS, kini hanya paid mulai 0,0005 BNB/share. "
        "Bukan lead; watchlist-only, log saja.")
# 4. New: Onyx Agent (watchlist-only)
contracts["Onyx Agent"] = {
 "address": "0x23ff20cd84d16d7c1ce53a29c7d2c726de8cbb3d",
 "status": "watchlist-only-age-unverified-2026-11-09",
 "name": "Onyx Agent", "kind": "ERC721",
 "totalSupply": 4790, "MAX_SUPPLY": 5000,
 "freeClaimed": None, "FREE_SUPPLY": None,
 "freePctVerified": None, "mintOpen": None,
 "userBalance": 0, "freeClaimed_user": None,
 "xVerified": False, "velocityVerified": False,
 "website": None,
 "gate": "FAILED (methods A/G/H/I run 1801: contract-address search 0 hit; project-name search hanya produk Onyx lain; contractURI() None; tokenURI(1) ipfs://agent-id/quar-4965/1 tanpa URL - template sama dengan Frost/Quar Agent; post Boltbook tanpa URL situs)",
 "launchNote": "Usia peluncuran UNVERIFIED (Boltbook recheck 17:32 WIB 9 Nov bukan waktu launch; tidak ada mintStart; Sourcify UNVERIFIED; first-mint walkback tidak bisa - Ankr 401 + dataseed getLogs -32005).",
 "baselineNote": "Ditemukan via Boltbook front page run 1801 (post https://boltbook.fun/p/C6TEZs1yH3yY, recheck 17:32 WIB: free 4.790/5.000 = 95,8% klaim post - itu totalSupply/MAX_SUPPLY, BUKAN free counter terverifikasi). Triase on-chain run 1801 (blok 132574569): totalSupply 4790, semua free view revert/None (freeClaimed/freeMinted/FREE_SUPPLY/mintOpen/mintStart), registry bytes TRUE (satu-satunya bukti agent-shape, weak discriminator), Sourcify UNVERIFIED (404), owner() None, tokenURI(1) ipfs://agent-id/quar-4965/1 (template sama dengan Frost/Quar Agent). Tidak ada di same-owner-discards.json (60 entri). Free% UNVERIFIED, slot UNVERIFIED, website TIDAK DITEMUKAN. BUKAN lead/kandidat; TIDAK pernah preview/mint.",
 "lastReadBlock": 132574569, "lastReadWib": "2026-11-09 18:2x WIB",
 "runNote1801_1109": "Run 1801: baru masuk snapshot sebagai watchlist-only-age-unverified (lihat baselineNote).",
}
# 5. New: TIME CARDS Genesis (upcoming)
contracts["TIME CARDS Genesis"] = {
 "address": "0xc5624B61beE1971E6Aa3AB5f403236Ab32C2B6cd",
 "status": "watchlist-only-upcoming-2026-11-09",
 "name": "TIME CARDS Genesis", "kind": "ERC721",
 "totalSupply": 0, "FREE_SUPPLY": 2000, "freeMinted": 0,
 "freePctVerified": 0.0, "mintOpen": None,
 "userBalance": 0, "freeClaimed_user": None,
 "xVerified": False, "velocityVerified": False,
 "website": None,
 "launchNote": "Pembukaan TERVERIFIKASI on-chain: freeStart() 1794229740 = 2026-11-09 20:09:00 WIB (cocok dengan post Boltbook 13:09 UTC); FREE_DURATION 259200 dtk (72 jam, tutup 2026-11-12 20:09 WIB); MINT_WINDOW 600; dripStart 2026-11-12 20:09:20 WIB.",
 "baselineNote": "Ditemukan via Boltbook front page run 1801 (post https://boltbook.fun/p/8UnQGRGs1sg4: PRE-OPEN, buka 13:09 UTC hari ini s.d. 12 Nov, 1 per wallet Agent ID). Triase on-chain run 1801 (blok 132574569): totalSupply 0, FREE_SUPPLY 2000, freeMinted 0, registry bytes TRUE, Sourcify exact_match (ABI: claimFree/claimedFree/freeStart/dripStart/MINT_WINDOW/FREE_DURATION). UPCOMING ONLY - belum bisa mint; TIDAK pernah preview/mint. Hot-leg/cron berikut memantau pembukaan.",
 "lastReadBlock": 132574569, "lastReadWib": "2026-11-09 18:2x WIB",
 "runNote1801_1109": "Run 1801: baru masuk snapshot sebagai watchlist-only-upcoming (buka 20:09 WIB hari ini).",
}
# 6. New: Swarm Agent (excluded - not agent-gated + age >48h)
contracts["Swarm Agent"] = {
 "address": "0xD612Ded8F2b4818c0A9d2465f06eBf1B745f0E17",
 "status": "excluded-not-agent-gated-age-over-48h-2026-11-09",
 "name": "Swarm Agent", "kind": "ERC721",
 "totalSupply": None, "freeClaimed": None,
 "website": "https://www.swarmarena.online/",
 "xVerified": False, "velocityVerified": False,
 "baselineNote": "Ditemukan via sweep route 3/5b run 1801 (situs mencetak kontrak persis 0xD612Ded8F2b4818c0A9d2465f06eBf1B745f0E17, ERC-721 5.555 supply, royalty 2%; mint #1 gratis 1/wallet, #2-#3 @ 0,00006 BNB). GUGUR: (i) situs bilang 'Connect any EVM wallet' - TIDAK ADA gate Agent ID yang dinyatakan, narasi Binance Agentic Wallet tidak terpenuhi; (ii) diumumkan The Colony 2026-11-06 10:06 UTC -> umur ~73 jam saat run ini > 48 jam. /skill.md situs 404. Triase on-chain run 1801: semua view None, registry bytes FALSE, Sourcify 404. Bukan lead; TIDAK pernah preview/mint.",
 "lastReadBlock": 132574569, "lastReadWib": "2026-11-09 18:2x WIB",
}
# 7. New: ENIGMAAGENT (excluded - sold out per site)
contracts["ENIGMAAGENT"] = {
 "address": "0x213A879D11a85b54483CEA2cdEC5D9026958Add3",
 "status": "excluded-sold-out-2026-11-09",
 "name": "ENIGMAAGENT", "kind": "ERC721",
 "totalSupply": None, "freeClaimed": None,
 "website": "https://enigmaagent-site.pages.dev/",
 "xVerified": False, "velocityVerified": False,
 "baselineNote": "Ditemukan via sweep route 3/5b run 1801 (agent.json situs mencetak kontrak NFT persis + market + token ENIG 0xBdC710f1B8F2649d6a4C6B28218ea9945b3c2F1b; free mint via PoW puzzle mint(nonce), maks 1/wallet, gas only; own market V2 live). SOLD OUT per situs: publicSupply 3.338/3.338 (fase 4 berakhir di 3.337). Triase on-chain run 1801: semua view None, registry bytes TRUE, Sourcify 404 - tidak bisa verifikasi sold-out on-chain; status per situs. Bukan lead; TIDAK pernah preview/mint.",
 "lastReadBlock": 132574569, "lastReadWib": "2026-11-09 18:2x WIB",
}
# 8. New track_c: ORDIagent sale (excluded - free pool exhausted)
track_c["ORDIagent-sale-7D10"] = {
 "sale": "0x7D10516D08f3bE98aaFD9Ac4169E6Cc30D6bCeB8",
 "token": "0xF969219E0529287Bc05EC8c34103503ff7f30a4A",
 "pair": "0x698Fe50F0cF952CC9ba0F84cc34a8038AABEFaEe",
 "name": "ORDIagent", "status": "excluded-free-pool-exhausted-2026-11-09",
 "saleShape": "Track-C (dari post Boltbook run 1801; shape S1 tidak dicek penuh - pool sudah habis saat ditemukan)",
 "freeClaimed": 1000, "FREE_SHARES": 1000,
 "note": "Ditemukan via Boltbook front page run 1801 (post ORDIagent/BAHUANG3): free lane 1.000/1.000 HABIS dalam 52 detik (buka 18:00 HKT = 17:00 WIB). Triase on-chain run 1801: freeClaimed 1000, FREE_SHARES 1000 (terverifikasi on-chain) -> pool gratis HABIS. Bukan lead; TIDAK pernah preview/mint.",
 "lastReadBlock": 132574569, "lastReadWib": "2026-11-09 18:2x WIB",
}
# --- top-level run notes ---
snap["runNote1801_1109"] = (
 "Run 1801: re-read 603 kontrak + 82 track_c (blok 132573635, interval 15,8 mnt vs run 1731 - block timestamp 132571528 17:50:41 WIB -> 132573635 18:06:29 WIB). "
 "Velocity LOLOS: bridge-0xe5e2c437 (11,55x, +41), Beatmind (38,65x, +61 - same-owner-discarded), Night Shift (79x, +25 - age-excluded), "
 "Neon District CY01 (2,49x, +33 - checked-not-lead, free% unverified), Zhenzhu (artefak ERC-20). TIDAK ADA promosi: semua velocity-pass gagal kaki lain "
 "(free% unverified / age unverified / website none / discarded / age-excluded). Rose Genesis +132 (prev rate 0 -> velocity GAGAL per aturan). "
 "Age-exclusion baru: 1 - Osiris Guardians (lihat ageExclusionEvidence1801). Sellout baru: 1 - ALL ACCESS (1500/1500, watchlist-only, log saja). "
 "Track-C sellout baru: 1 - ORDIagent sale 0x7D10 (freeClaimed 1000/1000, log saja). "
 "Scan leg FAST-FAIL (Ankr pre-flight 2x HTTP 401, outage sejak ~13:33 WIB; watermark tetap 132512564). "
 "EKSEKUSI: 0. Baru masuk snapshot: Onyx Agent (watchlist-only-age-unverified), TIME CARDS Genesis (upcoming, buka 20:09 WIB), "
 "Swarm Agent (excluded), ENIGMAAGENT (excluded-sold-out), ORDIagent-sale-7D10 (track_c excluded). "
 "Track-B binanceai: TIDAK BERUBAH (launched 0, failed 1, refund 1, totalShares 3110, blok 132573826). Bridge: tidak berubah (mtime 2026-11-08 18:21)."
)
snap["runNote1801_1109_scan"] = (
 "Run 1801 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (132571600-132571649), 2 attempts: "
 "ATTEMPT 1 FAIL 7,1 dtk HTTP 401 Unauthorized; ATTEMPT 2 FAIL 8,0 dtk HTTP 401 Unauthorized "
 "(kredensial custom.ankr ditolak rpc.ankr.com; outage sejak ~13:33 WIB 2026-11-09). Watermark TIDAK dimajukan (tetap 132512564; "
 "gap ke head ~60.000+ blok dan tumbuh - milik backfill, ikut gagal 401). Route 5c: tanpa output scan baru."
)
snap["runNote1801_1109_binanceai"] = (
 "Run 1801 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
 "tokenClaimed(user)=0 (probe dataseed, blok 132573826). Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang."
)
snap["runNote1801_1109_age_exclusions"] = (
 "Run 1801 age-exclusions baru: 1 - Osiris Guardians (launch <= 2026-11-04 01:31:46 WIB, umur ~5,7 hari > 48 jam, "
 "belum sold out free 57,4%; bukti di ageExclusionEvidence1801; dilaporkan sekali). "
 "Item lain: tidak ada age-exclusion baru (umur unverified tetap watchlist-only)."
)
snap["runNote1801_1109_early_leads"] = (
 "Run 1801 early leads: TIDAK ADA early lead baru. Sourcify feed 20 terbaru (verifiedAt 17:29-18:05 WIB): "
 "shape-check 6 terbaru (0x20Ac20DF, 0xC40D6428, 0x11C39a60, 0xD9B4D451, 0x08F5DB63, 0x831D586c) - semuanya BUKAN agent-shaped "
 "(tanpa registry, tanpa mint/free views). Boltbook: Onyx Agent baru (watchlist-only, bukan early lead - free% unverified, "
 "tanpa first-mint terverifikasi); TIME CARDS Genesis (upcoming, belum buka); JOLT klaim BERBAYAR (bukan track B)."
)
snap["last_run_wib"] = "2026-11-09 18:2x WIB"
snap["last_run_note"] = ("Run 1801: 603 kontrak + 82 track_c re-read (blok 132573635); 0 eksekusi; 0 promosi; "
 "1 age-exclusion (Osiris Guardians, dilaporkan sekali); scan fast-fail Ankr 401 (watermark 132512564); "
 "binanceai tetap refund; 2 watchlist-only baru (Onyx Agent, TIME CARDS Genesis upcoming 20:09 WIB).")
snap["timestamp_wib"] = "2026-11-09 18:2x WIB"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
summary = {"contracts_updated": n_upd, "track_c_updated": n_tc, "block": BLOCK,
           "interval_minutes": INTERVAL,
           "new_entries": ["Onyx Agent","TIME CARDS Genesis","Swarm Agent","ENIGMAAGENT"],
           "new_track_c": ["ORDIagent-sale-7D10"],
           "status_changes": {"Osiris Guardians":"age-excluded-2026-11-09","ALL ACCESS":"sold-out-2026-11-09"}}
json.dump(summary, open(f"{BASE}/run-2026-11-09-1801-merge.json","w"), indent=1)
print("MERGE DONE", summary)
