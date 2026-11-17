#!/usr/bin/env python3
"""Merge run 2026-11-09 03:01 WIB. Reloads snapshot fresh, applies the partial
(degraded) reread + lead triage + partial scan findings on top. Watermark is NOT
advanced (scan partial/failed). New entries are added ONLY if absent (protects
against a concurrent 03:31-run merge overwriting)."""
import json, shutil
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0301-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-0301-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {})
NEW_BLOCK = rr.get("block")
updated = 0; degraded = 0
for name, e in C.items():
    r = rr["reread"].get(name)
    if r is None:
        continue
    new_sup = r.get("totalSupply")
    if new_sup is None:
        degraded += 1
        note = (f"Run 0301 (blok {NEW_BLOCK}, 03:03-03:13 WIB): totalSupply None "
                "(dataseed down, eth_call batch gagal, nilai lama dipertahankan); ")
    else:
        note = f"Run 0301 (blok {NEW_BLOCK}): totalSupply {e.get('totalSupply')}->{new_sup}; "
        e["totalSupply"] = new_sup
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            e[k] = r[k]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["lastReadBlock"] = NEW_BLOCK; e["lastReadWib"] = "2026-11-09 03:13 WIB"
    e["runNote0301_1109"] = note + f"free={e.get('freeClaimed')}/{e.get('FREE_SUPPLY')}; bal_user={e.get('balanceOf_user')}; status {e.get('status')}."
    updated += 1

# --- new watchlist entries (added only if absent) ---
def add_entry(name, entry):
    if name in C:
        print(f"SKIP {name}: already in snapshot (status {C[name].get('status')}), keeping existing entry")
        return False
    C[name] = entry
    print(f"ADDED {name}")
    return True

add_entry("ALL ACCESS", {
    "address": "0xc3ce00677dad113f5d466d46c8c7b3a227855a5b",
    "status": "watchlist-only-age-unverified-0301",
    "name": "ALL ACCESS", "symbol": None, "kind": "ERC721",
    "totalSupply": 1320, "MAX_SUPPLY": 1500, "price": 200000000000000,
    "costOf_user": 0, "mintsLeft_user": 10, "MAX_PER_WALLET": 10, "bogo": 0,
    "freeLeft": None, "freeOf_user": None, "mintOpen": None,
    "mintedBy_user": None, "balanceOf_user": None,
    "agentIds": None, "owner": None,
    "firstMintBlockEarliestSeen": 132423205,
    "lastReadBlock": 132456769, "lastReadWib": "2026-11-09 03:35 WIB",
    "xVerified": False, "velocityVerified": False, "websiteVerified": False,
    "launchNote": ("Usia peluncuran UNVERIFIED. Walkback Ankr getLogs (walkback1 14 chunk + "
        "walkback2 20 chunk, total 34.000 blok ke belakang) menemukan mint hingga blok 132423205 "
        "(~23:28 WIB 8 Nov menurut estimasi 0,45 dtk/blok - BUKAN timestamp blok terverifikasi), "
        "TANPA menemukan batas peluncuran (tidak ada 5 chunk kosong berurutan). First mint "
        "sebenarnya <= 132423205, bisa lebih awal. KOREKSI PENTING: angka leads2 "
        "'first_mint_block 132456377 / 03:26:48 WIB' DIBUANG - fungsi first_mint() leads2 "
        "mengembalikan mint paling awal di chunk TERBARU yang bermint, bukan first mint "
        "(bug: return pada chunk pertama yang berisi log). Boltbook Radar 03:06 WIB sudah "
        "menunjukkan 1.311/1.500, jadi proyek sudah mint jauh sebelum 03:26."),
    "baselineNote": ("Ditemukan via Boltbook Radar + Wave-4 (crawl 03:06 WIB): 1.311/1.500, mint cost 0 BNB, "
        "+11/pass. Agent-shaped TERKONFIRMASI via ABI Sourcify (38 fns: agentIds, agentTokenIdOf, "
        "mintWithAgentTokenId, mintedByAgent, freeLeft, freeOf, costOf, mintOpen, setMintOpen/setPrice/"
        "setFree/withdraw/treasury, teamMint). Baca segar OnFinality run ini: totalSupply 1320/1500, "
        "price()=0,0002 BNB, costOf(user,1)=0, mintsLeft(user)=10/10, MAX_PER_WALLET=10, bogo=0. "
        "freeLeft/freeOf/mintOpen/mintedBy/balanceOf/agentIds/owner TIDAK TERBACA (OnFinality 429/timeout, "
        "3x retry tiap view) - free% UNVERIFIED, slot user diduga terbuka dari costOf=0 (BUKAN preview). "
        "Website UNVERIFIED: Colony mencantumkan agentpad.trade, tapi situs itu launchpad bonding-curve "
        "yang TIDAK mencetak kontrak ini (dicek browser.open 03:37 WIB) - bukan bukti website. "
        "Owner UNVERIFIED (owner() gagal dibaca); post Wave-4 memperingatkan ke-4 lane berbagi satu owner "
        "dengan kontrol owner-only - catatan hati-hati, belum terverifikasi sendiri. X UNVERIFIED. "
        "BUKAN early lead (first mint belum terverifikasi), BUKAN strong lead (umur + free% unverified), "
        "TIDAK di-preview/di-mint. Verifikasi lanjutan (walkback lebih dalam + free views) untuk run berikut."),
    "runNote0301_1109": "Run 0301: ditambahkan sebagai watchlist-only-age-unverified.",
})

add_entry("Hexrotta", {
    "address": "0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9",
    "status": "watchlist-only-age-unverified-0301",
    "name": "Hexrotta", "symbol": "HEXRTA", "kind": "ERC721",
    "totalSupply": None, "MAX_SUPPLY": 1121,
    "freeClaimed": None, "freeMinted": None,
    "firstMintBlockEarliestSeen": 132451927,
    "lastReadBlock": 132456769, "lastReadWib": "2026-11-09 03:50 WIB",
    "xVerified": False, "velocityVerified": False, "websiteVerified": False,
    "launchNote": ("Usia peluncuran UNVERIFIED (dugaan segar, belum terkonfirmasi). Walkback1 Ankr: mint "
        "paling awal dalam jendela 14 chunk = blok 132451927 (~03:04 WIB 9 Nov menurut estimasi "
        "0,45 dtk/blok), dengan 3 chunk kosong berurutan sebelumnya - sugestif peluncuran segar tapi "
        "minting jarang (1-5 mint/chunk) sehingga 3 chunk kosong BUKAN bukti batas peluncuran. "
        "Walkback2 perpanjangan sedang berjalan saat merge (Ankr error/timeout) - belum selesai. "
        "First mint sebenarnya <= 132451927."),
    "baselineNote": ("Ditemukan via Boltbook (crawl 03:06 WIB): 659/1.121, freeClaimed 646 (57,6%), mintOpen true, "
        "+5 mint dalam ~11 menit - SEMUA angka dari post Boltbook, BUKAN baca on-chain sendiri "
        "(leads2 views totalSupply/freeClaimed/freeMinted/mintOpen/price/costOf GAGAL semua karena "
        "OnFinality 429/timeout saat merge). Agent-shape BELUM terverifikasi (ABI belum dibaca run ini). "
        "Website UNVERIFIED (tidak ada situs ditemukan). X UNVERIFIED. BUKAN early/strong lead, "
        "TIDAK di-preview/di-mint. Verifikasi lanjutan untuk run berikut."),
    "runNote0301_1109": "Run 0301: ditambahkan sebagai watchlist-only-age-unverified.",
})

add_entry("AgentPad Pass", {
    "address": "0x01c106835091c09D5c69737631Af133530093C89",
    "status": "watchlist-only-age-unverified-0301",
    "name": "AgentPad Pass", "symbol": None, "kind": "ERC721",
    "totalSupply": None, "MAX_SUPPLY": 10000,
    "firstMintBlockEarliestSeen": 132443310,
    "lastReadBlock": 132456769, "lastReadWib": "2026-11-09 03:50 WIB",
    "xVerified": False, "velocityVerified": False, "websiteVerified": False,
    "launchNote": ("Usia peluncuran UNVERIFIED. Walkback1 Ankr: mint hingga blok 132443310 dalam jendela "
        "14 chunk, tanpa batas peluncuran. Colony (thecolony.ai MINTS index, checked 03:17 WIB) "
        "mencantumkan added_at 2026-10-29T20:15Z - itu waktu index menambahkan, BUKAN waktu launch, "
        "tapi mengindikasikan proyek sudah live sejak 29 Okt (>48 jam) - first mint belum dilokalisasi "
        "untuk membuktikan. BUKAN early/strong lead sampai umur terverifikasi."),
    "baselineNote": ("Ditemukan via Boltbook (crawl 03:06 WIB): 5.345/10.000 (53,45%), +30 lalu +9/jam. "
        "Colony: status free_live, score 89, agent gate confirmed on-chain, zero-value mint simulated, "
        "risk low, minted 5345/10000, mint_function mint(), website agentpad.trade. Website UNVERIFIED: "
        "agentpad.trade adalah launchpad bonding-curve yang TIDAK mencetak kontrak ini (dicek 03:37 WIB). "
        "Baca on-chain sendiri GAGAL (leads2 views 429/timeout saat merge). X UNVERIFIED. "
        "TIDAK di-preview/di-mint."),
    "runNote0301_1109": "Run 0301: ditambahkan sebagai watchlist-only-age-unverified.",
})

add_entry("AgentX", {
    "address": "0x59D96D8B4B82Abb350868E897F25F8e021360823",
    "status": "watchlist-only-age-unverified-0301",
    "name": "AgentX", "symbol": None, "kind": "ERC721",
    "totalSupply": None, "MAX_SUPPLY": 2500,
    "firstMintBlockEarliestSeen": 132450367,
    "lastReadBlock": 132456769, "lastReadWib": "2026-11-09 03:50 WIB",
    "xVerified": False, "velocityVerified": False, "websiteVerified": False,
    "launchNote": ("Usia peluncuran UNVERIFIED. Alamat ditemukan run ini via Colony MINTS index "
        "(bukan dari Boltbook - post Boltbook hanya menyebut nama 'AgentX' tanpa alamat). Colony "
        "added_at 2026-11-06T04:35Z (~11:35 WIB 6 Nov, ~64 jam lalu) mengindikasikan >48 jam, tapi itu "
        "waktu index menambahkan, BUKAN waktu launch. Walkback1 Ankr: mint hingga blok 132450367 "
        "dalam jendela 14 chunk, tanpa batas peluncuran. First mint sebenarnya <= 132450367."),
    "baselineNote": ("Colony: status free_live, score 85, minted 2098/2500, '1 free per Agent ID, then 0.002 BNB', "
        "agent gate confirmed on-chain, zero-value mint simulated, risk low, website NULL. Boltbook post "
        "'Four gas-only free mints: GOAT, Bubblebruin, AgentX, Agent Eggs' = bukti diskusi. "
        "Website UNVERIFIED (tidak ada situs; Colony website null). Agent-shape BELUM terverifikasi sendiri "
        "(ABI belum dibaca run ini). Baca on-chain sendiri belum dilakukan (di luar leads2). "
        "BUKAN early/strong lead, TIDAK di-preview/di-mint."),
    "runNote0301_1109": "Run 0301: ditambahkan sebagai watchlist-only-age-unverified (alamat dari Colony index).",
})

add_entry("AgentBox", {
    "address": "0x08393dad165d90e7258501fE1dfb5F3498644011",
    "status": "age-excluded-2026-11-09",
    "name": "AgentBox", "symbol": None, "kind": "ERC721",
    "totalSupply": None, "MAX_SUPPLY": None,
    "firstSeenBlock": None, "firstSeenWib": "2026-11-05 12:50 WIB",
    "lastReadBlock": 132456769, "lastReadWib": "2026-11-09 03:50 WIB",
    "xVerified": False, "velocityVerified": False, "websiteVerified": False,
    "launchNote": ("AGE-EXCLUDED: pertama terlihat 2026-11-05 12:50 WIB via feed Sourcify (hot-leg) - "
        "launch <= 5 Nov 12:50 WIB, umur >= ~87 jam saat run ini (>48 jam). Colony added_at "
        "2026-11-07 18:12 WIB lebih lambat dari first-seen, tidak mengubah kesimpulan. "
        "Tidak ada fase/batch mint baru yang terverifikasi."),
    "baselineNote": ("Hot-leg 2026-11-05 shape-check: S1=False S2=False, not sale-shape (semua view revert). "
        "Colony 2026-11-09: status free_live, site agentboxnft.xyz, minted unknown. Sebagai NFT, "
        "agent-shape belum terverifikasi - tidak relevan karena umur sudah gugur. Tidak dilaporkan "
        "sebagai lead, tidak di-preview/di-mint."),
    "runNote0301_1109": "Run 0301: ditambahkan sebagai age-excluded (first-seen 2026-11-05).",
})

# --- seen file: scan contracts (all already seen) + meta note ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = json.load(open(f"{BASE}/onchain-scan-2026-11-09-0301.json"))
added = 0
for c in sc.get("contracts_raw", []):
    a = (c.get("address") or "").lower()
    if a and a not in seen.get("contracts", {}):
        seen.setdefault("contracts", {})[a] = c.get("first_block") or sc.get("from_block")
        added += 1
seen.setdefault("_meta", {})["note_0301"] = (
    "Run 0301: scan PARTIAL (chunk 2 Ankr error 'Remote end closed connection', enrichment "
    "dihentikan manual 03:37 WIB untuk membebaskan OnFinality bagi verifikasi lead; hanya 50 blok "
    "132455451-132455500 ter-scan, 13 ERC721 + 34 ERC-20-mint; 0 first-seen (13/13 sudah di seen; "
    "Golden Agents, KIJIN, Kitebots sudah di snapshot); watermark TIDAK dimajukan. "
    f"{added} first-seen appended ke seen['contracts']. "
    "Skipped gap 132449515-132455450 (backfill OFF untuk watermark job ini; backfill-parallel konkuren "
    "berjalan 03:25 WIB mencakup 132451315-132456182 - gap mungkin tertutup backfill, bukan job ini).")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

# --- top-level run note ---
s["last_run"] = "0301"
s["last_run_wib"] = NOW_STR
s["last_run_note"] = (
    f"Run 0301 (03:01 WIB 9 Nov - {NOW_STR}): INFRASTRUKTUR RUSAK SEPANJANG RUN. "
    f"Route 1 re-read GAGAL TOTAL: {updated} kontrak dibaca (blok {NEW_BLOCK}), {degraded} totalSupply=None "
    "(dataseed BSC semua timeout sejak ~03:03 WIB - GET 404 ~6 dtk tapi POST JSON-RPC timeout; fast_rpc "
    "membakar ~8 dtk/endpoint lalu gagal; nilai lama dipertahankan, velocity TIDAK terhitung). "
    "Workaround: OnFinality https://bnb.api.onfinality.io/public (single call ~4 dtk, BATCH 429, public endpoint "
    "429 berat saat beban bersama - leads2/scan/backfill/03:31 berebut); OnFinality TIDAK dukung historical state "
    "(eth_call blok lama error -32000 'historical state not available') - tes umur via totalSupply blok lama MUSTAHIL. "
    "Ankr getLogs OK tapi flapping (timeout + 'Remote end closed connection' berulang, juga di backfill). "
    "Route 4 scan PARTIAL: pre-flight OK 19,7 dtk; window 132455451-132456450, chunk 1 saja (13 ERC721 + 34 ERC-20-mint), "
    "chunk 2 error; enrichment 4/13 lalu dihentikan manual untuk prioritas verifikasi lead; 0 first-seen; watermark "
    "TIDAK dimajukan (tetap 132449514); skipped gap 132449515-132455450. 5c: 1 dicek (0xCfb9 yield/vToken, bukan S1/S2), 0 hit. "
    "Route 5a feed: 5 baru, semua sudah di hot-leg-seen (shape-checked 03:21, S1/S2 false), 0 lead. "
    "Boltbook EN+ZH 03:06/03:11 WIB: 3 lead baru diverifikasi parsial - ALL ACCESS 0xc3ce (1320/1500, costOf(user)=0, "
    "mintsLeft 10/10, agent-shaped ABI, website UNVERIFIED, umur UNVERIFIED - walkback 34 chunk tanpa batas, mint hingga "
    "blok 132423205; leads2 'first mint 03:26:48' DIBUANG karena bug walkback leads2), Hexrotta 0x2525 (Boltbook 659/1121, "
    "freeClaimed 646, walkback earliest 132451927 ~03:04 WIB sugestif segar tapi belum terkonfirmasi, views leads2 gagal), "
    "AgentPad Pass 0x01c1 (Boltbook 5345/10000, Colony free_live score 89, website UNVERIFIED, umur UNVERIFIED) - ketiganya "
    "watchlist-only-age-unverified, TIDAK dilaporkan sebagai lead, TIDAK di-preview/di-mint. "
    "Route 6 Colony MINTS index (BARU, projects.json 03:35 WIB, 56 proyek, 39 free_live): AgentX 0x59D9 alamat ditemukan "
    "(2098/2500, 1 free/Agent ID, added 6 Nov - umur UNVERIFIED, watchlist-only); Crack 0xAeA1 = sudah di track_c "
    "(minted-by-user-2026-11-06, CRACK #792); AgentBox 0x0839 age-excluded (first-seen 5 Nov). "
    "Route 3 web sweep EN+ZH: 0 kandidat baru (hanya item 25-27 Okt, age-excluded; MiniCoin/OUPE/Pixel Fox/AgentForge tua). "
    "Bridge: 116 kontrak, 0 baru. Route 6 Odaily/PANews: 0 penyebutan. "
    "Backfill-parallel KONKUREN berjalan 03:25 WIB (3 worker, 132451315-132456182) padahal user menonaktifkan backfill "
    "2026-11-08 - perlu dicek status cron-nya; watermark file tetap milik job ini (132449514). "
    "0 kandidat, 0 strong lead, 0 early lead, 0 auto-mint. leads2 + walkback2 Hexrotta/APASS masih berjalan saat merge; "
    "hasil akhirnya untuk run berikut.")
s["runNote0301_1109"] = s["last_run_note"]
# --- scan-state: do NOT advance watermark; record failure ---
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"] = 132449514
st["last_scan_window_from"] = 132455451
st["last_scan_window_to"] = 132455500
st["last_scan_wib"] = "run 2026-11-09 0301 (PARTIAL)"
st["ankr_calls"] = 1
st["errors"] = ["Transfer chunk 132455501-132455550: Remote end closed connection without response",
                "Enrichment stopped manually 03:37 WIB to free OnFinality for lead verification"]
st["nft_contracts"] = 13
st["erc20_mint_contracts"] = 34
st["skipped_gap"] = "132449515-132455450 (5936 blok; backfill OFF untuk job ini; backfill-parallel konkuren 03:25 WIB mencakup 132451315-132456182)"
st["note_0301"] = ("Watermark TIDAK dimajukan (tetap 132449514) karena scan PARTIAL/gagal. Dataseed BSC down sejak "
    "~03:03 WIB; OnFinality public single-call OK tapi 429 berat + tanpa historical state; Ankr getLogs flapping. "
    "Backfill-parallel konkuren berjalan 03:25 WIB meski user menonaktifkan backfill 2026-11-08 - status cron perlu dicek.")
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE updated={updated} degraded={degraded} seen_added={added}")
print("contracts now:", len(s["contracts"]), "track_c now:", len(s["track_c"]))
