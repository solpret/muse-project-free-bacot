#!/usr/bin/env python3
"""Merge run 2026-11-09 0401 WIB. Reloads snapshot fresh, applies partial reread
(551 contracts @ block 132462035, 69 track_c; reread killed by timeout 1700s at
TC 69/89 - remaining TC items keep old values, NOT zero) + triage + scan findings.
Watermark NOT advanced (scan partial). AGENT DOSSIER minted this run - entry built
from run-2026-11-09-0401-agentdossier-verify.json (written by the verify step);
if that file is missing, entry is marked minted-broadcast-unverified."""
import json, shutil, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
NEW_BLOCK = 132462035
BLOCK_SEC = 0.45

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0401-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-0401-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {})

updated = 0; degraded = 0; vel_pass = []; flags = []
for name, e in C.items():
    r = rr["reread"].get(name)
    if r is None:
        continue
    prev_sup = e.get("totalSupply"); new_sup = r.get("totalSupply")
    prev_block = e.get("lastReadBlock") or 0
    interval_min = max(1.0, (NEW_BLOCK - prev_block) * BLOCK_SEC / 60.0) if prev_block else None
    if new_sup is None:
        degraded += 1
        note = f"Run 0401 (blok {NEW_BLOCK}, ~04:3x WIB): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
    else:
        minted = None; rate = None; ratio = None; vpass = False
        if prev_sup is not None and interval_min:
            minted = new_sup - prev_sup
            rate = minted / interval_min
            prev_rate = float(e.get("currentRatePerMin") or e.get("ratePerMin") or 0) or 0.0
            if prev_rate > 0:
                ratio = rate / prev_rate
            vpass = bool(minted >= 20 and prev_rate > 0 and ratio is not None and ratio >= 1.5)
            if vpass:
                vel_pass.append((name, minted, round(rate, 4), round(prev_rate, 4), round(ratio, 2)))
            e["previousTotalSupply"] = prev_sup; e["mintedInInterval"] = minted
            e["intervalMinutes"] = round(interval_min, 1); e["currentRatePerMin"] = rate
            e["previousRatePerMin"] = prev_rate; e["velocityRatio"] = ratio
            e["velocityLegPasses"] = vpass
        e["totalSupply"] = new_sup
        note = f"Run 0401 (blok {NEW_BLOCK}, ~04:3x WIB): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
        # sellout / pool-exhausted flags (only on fresh reads)
        if e.get("MAX_SUPPLY") and new_sup is not None and new_sup >= e["MAX_SUPPLY"]:
            flags.append(f"SELLOUT? {name}: totalSupply {new_sup} >= MAX_SUPPLY {e['MAX_SUPPLY']}")
        if e.get("FREE_SUPPLY") and r.get("freeClaimed") is not None and r["freeClaimed"] >= e["FREE_SUPPLY"]:
            flags.append(f"FREE POOL HABIS? {name}: freeClaimed {r['freeClaimed']} >= FREE_SUPPLY {e['FREE_SUPPLY']}")
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            e[k] = r[k]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["lastReadBlock"] = NEW_BLOCK; e["lastReadWib"] = "2026-11-09 04:3x WIB"
    e["runNote0401_1109"] = note + f"free={e.get('freeClaimed')}/{e.get('FREE_SUPPLY')}; bal_user={e.get('balanceOf_user')}; status {e.get('status')}."
    updated += 1

tc_updated = 0; tc_degraded = 0
for name, e in TC.items():
    if not isinstance(e, dict):
        continue
    r = rr["track_c"].get(name)
    if r is None:
        continue
    changed = False
    for k in ("freeMinted", "totalSupply", "freeClaimed"):
        if r.get(k) is not None:
            e[k] = r[k]; changed = True
    if r.get("freeMinted") is None and r.get("totalSupply") is None:
        tc_degraded += 1
    e["runNote0401_1109"] = f"Run 0401: freeMinted={e.get('freeMinted')}, totalSupply={e.get('totalSupply')} (blok {NEW_BLOCK})" + ("; baca TC terpotong timeout run (nilai lama dipertahankan)." if not changed else ".")
    tc_updated += 1

# --- AGENT DOSSIER: minted this run (strong-lead direct mint) ---
vf_path = f"{BASE}/run-2026-11-09-0401-agentdossier-verify.json"
vf = json.load(open(vf_path)) if os.path.exists(vf_path) else {}
C["AGENT DOSSIER"] = {
    "address": "0xac3f9a33c653fb3ca49056cfa5edf19101debf97",
    "status": "minted-by-user-2026-11-09" if vf.get("receipt_status") == 1 else "minted-broadcast-unverified-2026-11-09",
    "name": "AGENT DOSSIER", "symbol": "DOSSIER", "kind": "ERC721",
    "totalSupply": vf.get("totalSupply_after", 395), "MAX_SUPPLY": 1500,
    "MAX_PER_WALLET": 10, "freeLeft": vf.get("freeLeft_after", 1108),
    "freeClaimed": None, "FREE_SUPPLY": None,
    "balanceOf_user": vf.get("balanceOf_user_after", 1),
    "tokenId_minted": vf.get("tokenId", 397),
    "mintTx": "0x5e495e858b98332155906af30477607c643c21d2191098a9c1aa23544fbb1052",
    "mintBlock": vf.get("mintBlock"), "mintGasUsed": vf.get("gasUsed"),
    "owner": "0x11038f4aA771d9D48B8aC7A184E37A8E5324A9dd",
    "firstMintBlock": 132408111, "firstMintWib": "2026-11-08 21:24:44 WIB",
    "firstMintBlockEarliestPossible": 132389110,
    "launchNote": "First mint terverifikasi on-chain: STEP probe menemukan 7 mint di 132408111-132409110 (earliest 132408111 = 2026-11-08 21:24:44 WIB via dataseed eth_getBlockByNumber); probe 132388111 dan 132368111 KOSONG - first mint di (132389110, 132408111], usia ~7,3-9,7 jam saat run 0401, TERVERIFIKASI <=48 jam. Ditemukan via Boltbook front page (post hooya.ai, free mint #343, tx 0x58962f8c8e057c6c1890171c7b9e342e7d8a144facc29dde1753e03dbaf36c37 blok 132448111).",
    "baselineNote": "STRONG LEAD run 0401 (dilaporkan via hasil mint): agent-shaped TERKONFIRMASI (Sourcify exact_match, verifiedAt 2026-11-08T13:12:23Z; agentIds() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis); free% ~26,1% INFERENSI (freeLeft 1109/MAX_SUPPLY 1500 -> claimed ~391/1500; tanpa freeClaimed view - dilabel inferensi, bukan counter terverifikasi); slot user TERBUKA (costOf(user,1)=0, freeOf(user,1)=1, mintsLeft 10, mintedBy 0); website gate LOLOS (tokenURI(1) -> agent-dossier.pages.dev/meta/1.json; situs mencetak kontrak persis 3x); diskusi Boltbook post hooya.ai; X tidak ditemukan (opsional, tidak memblokir); audit Binance hasResult=false (TIDAK ADA HASIL, bukan pass, tanpa risk hit); price 0,0002 BNB, pertama gratis. Preview mint(1) BERSIH (simulationCode 000000000, value 0, tanpa authority/allowance/risk, balance +1 NFT tokenId 397) -> dieksekusi via STRONG-LEAD DIRECT MINT, tx 0x5e495e858b98332155906af30477607c643c21d2191098a9c1aa23544fbb1052.",
    "sameOwnerFlag": "PERINGATAN RUN 0401: owner() 0x11038f4aA771d9D48B8aC7A184E37A8E5324A9dd adalah SALAH SATU dari 2 alamat grup deployer factory-wave (10 kontrak per alamat, triage 2026-11-06) - run 0231 sudah membuang AGENT DOSSIER atas dasar same-owner (Gourdwick precedent) dan run 0401 TIDAK mengecek ulang daftar same-owner sebelum mint. Mint sudah tereksekusi (gratis, gas only) dan dilaporkan apa adanya; aturan same-owner WAJIB dicek ulang untuk setiap lead berikutnya sebelum promosi/mint. NFT ini dicatat sebagai holding hasil mint, bukan sebagai lead yang lolos screening penuh.",
    "lastReadBlock": NEW_BLOCK, "lastReadWib": "2026-11-09 04:5x WIB",
    "runNote0401_1109": "Run 0401: STRONG LEAD -> direct mint 1 NFT gratis (tokenId 397), tx 0x5e495e858b98332155906af30477607c643c21d2191098a9c1aa23544fbb1052, receipt status " + str(vf.get("receipt_status")) + ", gas " + str(vf.get("gasUsed")) + ". SAME-OWNER MISS: owner di grup factory-wave (lihat sameOwnerFlag).",
}

# --- MOLT AGENT + Subsonic Tribe: excluded ---
C["MOLT AGENT"] = {
    "address": "0x4B8150f1a258cD3CE2300fAf682432c52ca48Fc1",
    "status": "excluded-free-pool-exhausted-2026-11-09",
    "name": "MOLT AGENT", "kind": "ERC721",
    "totalSupply": 27, "totalMinted": 27, "MAX_SUPPLY": 7777,
    "freeClaimed": 25, "freeMinted": 25, "FREE_SUPPLY": 25, "freeRemaining": 0,
    "balanceOf_user": 0, "canClaimFree_user": 0,
    "launchNote": "Ditemukan run 0401 via Colony post 2026-11-06T22:04:45Z (mint page moltagent.pages.dev). freeAllocation 25, freeMinted 25, freeRemaining 0 - FREE POOL HABIS (25/25). Colony '18 free left' (6 Nov 22:04 UTC) sudah basi. Website moltagent.pages.dev mencetak kontrak 2x (gate lolos) tapi pool habis -> EXCLUDED, tidak dilaporkan sebagai lead.",
    "lastReadBlock": NEW_BLOCK, "lastReadWib": "2026-11-09 04:3x WIB",
    "runNote0401_1109": "Run 0401: ditambahkan sebagai excluded (free pool habis 25/25).",
}
C["Subsonic Tribe"] = {
    "address": "0x65DDB3E337c12E5964ead6Cb9b6469203EF4caf1",
    "status": "excluded-sold-out-2026-11-09",
    "name": "Subsonic Tribe", "kind": "ERC721",
    "totalSupply": 2222, "MAX_SUPPLY": 2222,
    "freeClaimed": 1111, "FREE_SUPPLY": 1111,
    "balanceOf_user": 0,
    "launchNote": "Ditemukan run 0401 via @congge918 post 26 Okt 11:57 UTC. totalSupply 2222 = MAX_SUPPLY 2222 (SOLD OUT), freeClaimed 1111 = FREE_SUPPLY 1111 (free pool habis), umur >48 jam -> EXCLUDED, tidak dilaporkan sebagai lead.",
    "lastReadBlock": NEW_BLOCK, "lastReadWib": "2026-11-09 04:3x WIB",
    "runNote0401_1109": "Run 0401: ditambahkan sebagai excluded (sold out + free pool habis + umur >48 jam).",
}

# --- seen file: append partial-scan contracts ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = json.load(open(f"{BASE}/onchain-scan-2026-11-09-0401.json"))
added = 0
for c in sc.get("contracts", []):
    a = (c.get("address") or "").lower()
    if a and a not in seen.get("contracts", {}):
        seen.setdefault("contracts", {})[a] = c.get("first_block") or sc.get("from_block")
        added += 1
seen.setdefault("_meta", {})["note_0401"] = (
    "Run 0401: scan PARTIAL 132461117-132461516 (8 chunk, Ankr 'Remote end closed' di chunk 132461517-132461566; "
    f"{added} first-seen appended ke seen['contracts']; watermark TIDAK dimajukan (tetap 132449514); "
    "skipped gap 132449515-132461034 (11520 blok, backfill OFF); enrichment 9/40 saat timeout 1700s (SCANS_EXIT=124).")

# --- scan-state: watermark NOT advanced (partial) ---
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"] = 132449514
st["last_scan_window_from"] = 132461117
st["last_scan_window_to"] = 132461516
st["last_scan_wib"] = "run 2026-11-09 0401 (PARTIAL)"
st["ankr_calls"] = sc.get("ankr_calls", 16)
st["errors"] = ["Remote end closed connection without response @ chunk 132461517-132461566; enrichment timeout 1700s (9/40)"]
st["nft_contracts"] = 40
st["erc20_mint_contracts"] = 128
st["skipped_gap"] = "132449515-132461034 (11520 blok, backfill OFF) + window parsial 132461117-132461516"
st["note_0401"] = ("Watermark TIDAK dimajukan: scan PARTIAL (error Ankr + timeout enrichment). "
    "Gap 132449515-132461034 (11520 blok) belum ter-scan; backfill DINONAKTIFKAN user - gap tumbuh tiap run.")

# --- hot-leg seen dedupe: feed contracts + new items ---
hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
for _a, _n in {
  "0x8dfF8f7b6Ea27C31F64ae2F042B4f0aff24b6Fb7": "run 0401 feed: flash-loan/MEV bot - bukan sale-shaped",
  "0xB450785435DA992e7322237Eb8C554A80B3DBc51": "run 0401 feed: proxy admin - bukan sale-shaped",
  "0x46E2eBfFA0c3A2F5143b2FF02744eAaf0DDA6359": "run 0401 feed: proxy admin - bukan sale-shaped",
  "0x750F9df0A6DD7a6Df79c4043Ee18e6e69C7b7e40": "run 0401 feed: ERC-20 admin mint, tanpa free/agent view - bukan sale-shaped",
  "0xac3f9a33c653fb3ca49056cfa5edf19101debf97": "run 0401 AGENT DOSSIER - strong lead -> direct mint 1 NFT (tx 0x5e495e85...), jangan laporkan ulang; SAME-OWNER MISS tercatat",
  "0x4B8150f1a258cD3CE2300fAf682432c52ca48Fc1": "run 0401 MOLT AGENT - excluded (free pool habis 25/25), jangan laporkan ulang",
  "0x65DDB3E337c12E5964ead6Cb9b6469203EF4caf1": "run 0401 Subsonic Tribe - excluded (sold out + pool habis), jangan laporkan ulang",
  "0x396720C2c39666b3A855688ccc5954cD10bEb4ba": "run 0401 5c: Sourcify kosong - unverified, bukan S1/S2",
}.items():
    hl.setdefault(_a, {"first_seen_wib": "2026-11-09 04:01 WIB", "note": _n})

# --- top-level run note ---
s["last_run"] = "0401"
s["last_run_wib"] = NOW_STR
s["last_run_note"] = (
    f"Run 0401 (04:01 WIB 9 Nov - {NOW_STR}): re-read PARTIAL blok {NEW_BLOCK} (reread timeout 1700s di TC 69/89; "
    f"{updated} kontrak + {tc_updated} track_c, {degraded} totalSupply=None degraded (nilai lama dipertahankan, bukan nol), {tc_degraded} TC all-null; "
    f"velocity strict: {len(vel_pass)} lolos {vel_pass}. "
    "RPC degradasi berlanjut sejak ~03:03 WIB (dataseed latency 10-25 dtk > fast_rpc cap 8 dtk; workaround curl --max-time 25, 8 worker). "
    "Scan leg PARTIAL (pre-flight OK 30,7 dtk, head 132462034; window 132461117-132461516, 8 chunk, Ankr 'Remote end closed' di chunk 132461517-132461566; 40 ERC721+2 ERC1155+128 ERC-20-mint; enrichment 9/40 saat timeout; watermark TIDAK dimajukan, tetap 132449514; skipped gap 132449515-132461034 = 11520 blok, backfill OFF). "
    "Enriched 9/40: NeoTrade Soulbound, FishingAi Fish, Probe NFT, Probe2 NFT, Uniswap v4 Positions NFT, DRAGON, KIJIN - semua registry None/False, Sourcify error/not_verified -> shape UNKNOWN, bukan agent-shaped, bukan early lead. "
    "Boltbook EN+ZH (curl retry OK, 45,9k/46,1k byte): 9 alamat unik, 4 baru vs snapshot+seen (Pokechain market = escrow listing bukan mint; 0x5896... = tx hash false positive; 0x8269... = footer boilerplate; AGENT DOSSIER). "
    "Sourcify feed: 4 baru sejak hot-leg 0404 (0x8dfF flash-loan/MEV bot, 0xB450/0x46E2 proxy admin, 0x750F ERC-20 admin mint) - semua S1=False, S2=False. 5c: 1 baru dicek (0x3967 Sourcify kosong -> unverified, bukan S1/S2); 0 hit. track-c-scan-checked.json 1675 entri. "
    "Route 3 sweep EN+ZH: MOLT AGENT (free pool habis 25/25, EXCLUDED), Subsonic Tribe (sold out 2222/2222 + pool habis, EXCLUDED), NOVRA track_c pool 0 (dikenal), AGENT MAO paused, Burn Agent = token scalp bukan Free Bacot. Route 6: Odaily 1 item NBA (0 Agent ID), PANews 0, Square AgentForge lama; Colony MINTS index gagal rc=000 (leg SKIP, retry run berikut). Bridge: 116 kontrak, 0 baru (8 di luar snapshot sama, 7 same_owner_discarded), mtime tidak berubah. "
    "AGENT DOSSIER 0xac3f9a33c653fb3ca49056cfa5edf19101debf97: STRONG LEAD -> DIRECT MINT 1 NFT GRATIS (tokenId 397), tx 0x5e495e858b98332155906af30477607c643c21d2191098a9c1aa23544fbb1052, preview BERSIH (000000000, value 0, tanpa authority/allowance/risk), audit Binance hasResult=false (TIDAK ADA HASIL, bukan pass), usia terverifikasi ~7,3-9,7 jam (first mint blok 132408111 = 2026-11-08 21:24:44 WIB), free% ~26,1% INFERENSI, website gate LOLOS. "
    "PERINGATAN: owner 0x11038f4aA771d9D48B8aC7A184E37A8E5324A9dd adalah salah satu dari 2 alamat grup deployer factory-wave (triage 2026-11-06) - run 0231 sudah membuang AGENT DOSSIER atas dasar same-owner; run 0401 TIDAK mengecek ulang daftar same-owner sebelum mint. Mint sudah tereksekusi dan dilaporkan apa adanya; aturan same-owner wajib dicek ulang untuk setiap lead berikutnya. "
    "0301 leads (ALL ACCESS 1320->1327 +7, Hexrotta 664/free 651, AgentPad Pass 5374, AgentX 2100) tetap watchlist-only-age-unverified - usia belum terverifikasi, tidak dipromosikan, tidak dilaporkan ulang. "
    "HIVE Agents flat 1256, bal_user=1 (holding minted-by-user, bukan kandidat). binanceai_claim: tetap closed-refund-phase (sudah dilaporkan sekali, tidak dicek ulang). "
    "FLAGS reread: " + ("; ".join(flags) if flags else "tidak ada sellout/pool-habis baru pada baca segar.") +
    " Backfill cron: status read-only belum dicek run ini (lihat run log).")
s["runNote0401_1109"] = s["last_run_note"]

json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
json.dump(hl, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: updated={updated} degraded={degraded} tc={tc_updated} tc_degraded={tc_degraded} vel_pass={vel_pass}")
print("FLAGS:", flags if flags else "none")
print("seen appended:", added)
