#!/usr/bin/env python3
"""Merge run 2026-11-10 08:31 WIB into onchain-snapshot.json. Read-only on
state except the snapshot itself. Adds Roguefall (watchlist-only) + BOME
(track_c watchlist-only)."""
import json, shutil, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap_path = f"{BASE}/onchain-snapshot.json"
shutil.copy(snap_path, f"{snap_path}.bak-0831-premerge")
snap = json.load(open(snap_path))
rr = json.load(open(f"{BASE}/run-2026-11-10-0831-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-10-0831-vel.json"))
BLOCK = rr["block"]
INTERVAL = vel["interval_minutes"]  # 29.95
TS_WIB = "2026-11-10 08:31 WIB"

updated = 0
for name, entry in snap["contracts"].items():
    if not isinstance(entry, dict):
        continue
    fresh = rr["reread"].get(name)
    if not fresh:
        continue
    ts = fresh.get("totalSupply")
    if ts is None:
        continue  # degradasi eth_call: nilai lama dipertahankan
    prev = entry.get("totalSupply")
    if prev is None:
        entry["totalSupply"] = ts
        entry["lastReadBlock"] = BLOCK
        entry["lastReadWib"] = TS_WIB
        updated += 1
        continue
    minted = ts - prev
    prev_rate = entry.get("currentRatePerMin")
    rate = minted / INTERVAL if INTERVAL > 0 else 0.0
    ratio = (rate / prev_rate) if prev_rate else None
    passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
    # Guard artefak suplai token raksasa (bukan mint NFT): totalSupply > 10jt
    if prev > 10_000_000:
        passes = False
    entry["previousTotalSupply"] = prev
    entry["totalSupply"] = ts
    entry["mintedInInterval"] = minted
    entry["intervalMinutes"] = INTERVAL
    entry["previousRatePerMin"] = prev_rate
    entry["currentRatePerMin"] = rate
    entry["velocityRatio"] = ratio
    entry["velocityLegPasses"] = passes
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = TS_WIB
    updated += 1

# --- catatan item kunci run 0831 ---
def note(name, key, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e[key] = text

note("FCAT Agents", "runNote0831_1110",
     "Run 0831 (blok 132688952, interval 29,95 mnt): totalSupply 329->347 (+18), "
     "freeClaimed 347/888 = 39,1% TERVERIFIKASI (naik dari 37,0% run 0801); "
     "velocity GAGAL (0,60/mnt vs prev 0,80 = 0,75x). Slot TERBUKA (bal 0). "
     "Umur UNVERIFIED + website GATE FAILED — tetap watchlist-only, BELUM strong lead. TIDAK preview/mint.")
note("JINCHAN Agents", "runNote0831_1110",
     "Run 0831 (blok 132688952): totalSupply 192->208 (+16), freeClaimed 208/888 = 23,4% "
     "TERVERIFIKASI (naik dari 21,6% run 0801). <25% strong-lead leg. Velocity GAGAL "
     "(0,53/mnt vs prev 0,73 = 0,73x). Slot terbuka (bal 0). Umur/website UNVERIFIED. Tetap watchlist-only.")
note("THYRK", "runNote0831_1110",
     "Run 0831 (blok 132688952): totalSupply 1775->1935 (+160), freeMinted 1925/7777 = 24,7% "
     "— INFERENSI bila semua mint gratis, BUKAN verified; % leg N/A (tanpa free cap). "
     "Velocity GAGAL (5,34/mnt vs prev 4,49 = 1,19x). Slot user TERPAKAI (bal 1, mint #6849). "
     "Website thyrk.fun TERVERIFIKASI. Umur presisi UNVERIFIED. Tetap early lead.")
note("Sakura", "runNote0831_1110",
     "Run 0831 (blok 132688952): totalSupply 1210->1246 (+36), freeMinted 1236/6000 = 20,6% "
     "(<25% dan <50%). Velocity LOLOS run ini (1,20/mnt vs prev 0,80 = 1,51x; +36 token) "
     "TAPI kaki lain gagal: free% <25%, website GATE FAILED, slot UNVERIFIED. Tetap early lead, "
     "BUKAN strong lead/kandidat. TIDAK preview/mint.")
note("HIVE Agents", "runNote0831_1110",
     "Run 0831 (blok 132688952): totalSupply 1259->1259 (+0), velocity GAGAL; "
     "free=None/1000; bal_user=1; status minted-by-user-2026-11-02.")
note("Bubblebruin", "runNote0831_1110",
     "Run 0831 (blok 132688952): totalSupply 2392->2394 (+2), freeClaimed 2388/7777 = 30,7%; "
     "velocity GAGAL; bal_user=1; status minted-by-user-2026-11-01.")
note("Cosmogent", "runNote0831_1110",
     "Run 0831: totalSupply 653->706 (+53), velocity LOLOS (1,77/mnt vs prev 0,76 = 2,31x) "
     "TAPI status watchlist-only-same-owner-discarded-2026-11-03 (owner factory discard group) "
     "-> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead. Tanpa perubahan.")
note("Roninagent", "runNote0831_1110",
     "Run 0831: totalSupply 766->808 (+42), velocity LOLOS (1,40/mnt vs prev 0,50 = 2,81x) "
     "TAPI status watchlist-only-same-owner-discarded-2026-11-03 (owner factory discard group) "
     "-> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead. Tanpa perubahan.")
note("Agent Grove", "runNote0831_1110",
     "Run 0831: totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
     "freeMinted 2500 (fase 1 penuh); bal_user=0. Tanpa perubahan.")
note("MONOLITH", "runNote0831_1110",
     "Run 0831: totalSupply 639->644 (+5). Deadline umur 2026-11-10 17:32 WIB belum lewat. Age-watch.")

# --- Roguefall: baru dari sweep rute 3 (MintRadar), watchlist-only ---
snap["contracts"]["Roguefall"] = {
    "address": "0x5fe03829a2f94a8ba3906459258b1305f0e68934",
    "name": "Roguefall",
    "symbol": "RFALL",
    "kind": "ERC721",
    "status": "watchlist-only-age-website-unverified-2026-11-10",
    "totalSupply": 983,
    "freeMinted": 977,
    "FREE_CAP": 2000,
    "MAX_SUPPLY": 4000,
    "freePctVerified": 48.85,
    "mintOpen": 1,
    "canFreeMint_user": 1,
    "claimedFree_user": 0,
    "userBalance": 0,
    "firstSeenBlock": 132689899,
    "firstSeenWib": "2026-11-10 08:31 WIB",
    "discovery": "Route 3 sweep via MintRadar (datt.my): 430 mints, no flags, Agent ID mint; "
                 "bukan dari scan Ankr (outage 401) maupun Boltbook.",
    "agentShape": "TERVERIFIKASI: Sourcify exact_match, REGISTRY() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F "
                  "(registry resmi), freeMint()/FREE_CAP/canFreeMint/claimedFree/freeMinted di ABI.",
    "launchNote": "Umur UNVERIFIED: Sourcify verifiedAt 2026-11-04T23:28:03Z BUKAN launch time; "
                  "tidak ada stated launch time proyek; MintRadar burst 430 mint ~4 jam sebelum run "
                  "bukan bukti launch. contractURI() revert; tokenURI #1 base64 JSON tanpa external_url.",
    "website": None,
    "xVerified": False,
    "velocityVerified": False,
    "baselineNote": "Watchlist-only run 0831: free 977/2000 = 48,85% TERVERIFIKASI (>=25% strong leg), "
                    "slot user TERBUKA (canFreeMint=1, claimedFree=0, bal 0), TAPI umur UNVERIFIED "
                    "dan website GATE belum terverifikasi -> BUKAN early lead (first mint bukan di run ini; "
                    "totalSupply sudah 983) dan BUKAN strong lead (umur unverified). TIDAK preview/mint, "
                    "TIDAK dilaporkan ke chat (watchlist-only).",
    "lastReadBlock": BLOCK,
    "lastReadWib": TS_WIB,
}

# --- BOME 0x50CD...: track-C watchlist-only (bentuk S1 lolos, belum open) ---
snap["track_c"]["BOME-50CD"] = {
    "sale": "0x50CDd91b31cED977D2776825BBaD72e99FF0830E",
    "token": "0x50CDd91b31cED977D2776825BBaD72e99FF0830E",
    "name": "BOME",
    "symbol": "BOME",
    "status": "watchlist-only-not-open-age-unverified-2026-11-10",
    "shape": "S1",
    "saleShape": "LOLOS: mint(id,quantity,...) + previewMint quote + free views "
                 "(FREE_CAP, freeLotsMinted, freeUsed, freeCredits, freeInfo) + "
                 "identityRegistry (identity() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F resmi). "
                 "Single-contract token+sale (BomeMint).",
    "FREE_CAP": 1000,
    "freeLotsMinted": 0,
    "freePoolRemaining": 1000,
    "freeUsed_user": 0,
    "mintOpen": 0,
    "opened": 0,
    "totalSupply": 0x33b2e3c9fd0803ce7ffc180,
    "verifiedAt": "2026-11-10T01:13:37Z",
    "firstSeenWib": "2026-11-10 08:31 WIB",
    "discovery": "Route 5a Sourcify feed run 0831 (baru vs feed run 0801).",
    "baselineNote": "Watchlist-only run 0831: sale-shape S1 TERVERIFIKASI on-chain incl. registry resmi, "
                    "free pool 1000/1000, slot user terbuka (freeUsed=0), TAPI mintOpen=0/opened=0 "
                    "(sale BELUM dibuka) dan umur launch UNVERIFIED (verifiedAt bukan launch) -> "
                    "BUKAN lead/kandidat track C. TIDAK preview/mint, TIDAK dilaporkan. "
                    "Nama BOME = tabrakan nama dengan memecoin BOME Solana — verifikasi selalu by contract.",
    "lastReadBlock": 132689505,
    "lastReadWib": TS_WIB,
}

snap["runNote0831_1110"] = (
    "Run 0831 (2026-11-10 08:31-09:0x WIB, blok 132688952, interval 29,95 mnt): re-read 632 kontrak + "
    "74 track_c, 139 totalSupply None (degradasi eth_call, nilai lama dipertahankan). Velocity LOLOS 3 "
    "NFT: Sakura 1,51x (+36) — bukan promosi (free% 20,6% <25%, gate FAILED); Cosmogent 2,31x + Roninagent "
    "2,81x — keduanya same-owner-discarded, TIDAK PERNAH dipromosikan. THYRK +160 velocity GAGAL 1,19x. "
    "FCAT 39,1% verified, JINCHAN 23,4% verified — tetap watchlist-only. Sellout baru: 0. "
    "Baru: Roguefall (watchlist-only, umur/website unverified) + BOME-50CD track_c watchlist-only "
    "(S1 lolos, mintOpen=0). Binanceai tidak berubah (launched=0, refund). Ankr 401 fast-fail. Run DIAM.")
snap["runNote0831_1110_scan"] = (
    "Route 4 scan: FAST-FAIL. Pre-flight ankr_getLogs 50 blok (head 132689605): FAIL 6,0 dtk "
    "HTTP 401 Unauthorized (retry tidak dilakukan — pola 401 persisten). Kelanjutan outage Ankr sejak "
    "2026-11-09 ~13:33 WIB. Scan leg TIDAK dijalankan; watermark tetap 132512564; gap ke head "
    "~177.000 blok dan tumbuh. 5c dilewati (tanpa output scan).")
snap["last_run_wib"] = "2026-11-10 08:31 WIB"
snap["timestamp_wib"] = "2026-11-10 08:31 WIB"

json.dump(snap, open(snap_path, "w"), indent=1, ensure_ascii=False)
print("merged. contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]), "updated reads:", updated)
