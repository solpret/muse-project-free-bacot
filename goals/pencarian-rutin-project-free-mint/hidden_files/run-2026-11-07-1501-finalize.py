#!/usr/bin/env python3
"""Finalize run 1501 (FRESH — written for this run's own data; do NOT reuse the
1431 copy, which hardcodes run-1431 blocks/notes/removals already applied).
Applies reread/velocity, records the 5 hot-leg gate-blocked track-C leads in
track_c (reported once by hot leg 15:35 WIB — NO new chat report from this run),
writes run notes. Reloads snapshot at write time; atomic write."""
import json, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132171021
NOW = datetime.now(timezone(timedelta(hours=7)))
TS = NOW.strftime("%Y-%m-%d %H:%M WIB")
RUN = "2026-11-07 run 1501"

re = json.load(open(f"{BASE}/run-2026-11-07-1501-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1501-velocity.json"))

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
updated = 0; none_free = 0
for name, d in re["reread"].items():
    c = snap["contracts"].get(name)
    if c is None: continue
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if d.get(k) is not None: c[k] = d[k]
    if d.get("balanceOf_user") is not None: c["balanceOf_user"] = d["balanceOf_user"]
    if d.get("freeClaimed") is None and d.get("freeMinted") is None: none_free += 1
    c["lastReadBlock"] = REREAD_BLOCK
    c["lastReadWib"] = RUN
    updated += 1
for name, d in re.get("track_c", {}).items():
    tc = snap.get("track_c", {}).get(name)
    if isinstance(tc, dict):
        if d.get("totalSupply") is not None: tc["totalSupply"] = d["totalSupply"]
        if d.get("freeMinted") is not None: tc["freeMinted"] = d["freeMinted"]
        if d.get("freeSharesRemaining") is not None: tc["freeSharesRemaining"] = d["freeSharesRemaining"]
        tc["lastReadBlock"] = REREAD_BLOCK
        tc["lastReadWib"] = RUN

# velocity notes (this run's own numbers)
alc = snap["contracts"].get("Alchemister-0xCafEEDDF")
if alc is not None:
    alc["velocityNote1501"] = ("Run 1501 (blok 132171021, interval 42,8 mnt vs run 1431): 2342->2666 (+324, 7,58/mnt, "
        "ratio 2,39 vs prev 3,17/mnt) -> velocity LOLOS, TAPI TIDAK promosi: free% UNVERIFIED (tidak ada free view "
        "segar maupun snapshot) + status early-lead-backfill-2026-11-07 (sudah dilaporkan sebagai EARLY, duplicate "
        "Alchemister 0x69037Db8). Bukan strong lead/kandidat.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote1501"] = (f"Run 1501 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 1431 (1255) -> velocity GAGAL; "
        "balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.")
war3 = snap["contracts"].get("WAR3-1aa9")
if war3 is not None:
    war3["runNote1501"] = ("Run 1501: totalSupply 171->605 (+434 dalam ~43 mnt); velocity TIDAK lolos (prev rate 0, rasio "
        "tidak terhitung); first mint 2026-11-07 14:25:04 WIB, early-lead-backfill; free% snapshot 0,63% (19/3000) << 25% "
        "-> BUKAN strong lead. +434 tidak bisa dibedakan free vs paid (PRICE 0,0017 BNB) karena freeMinted segar None. "
        "Butuh baca freeMinted segar run berikut.")

# 5 hot-leg gate-blocked track-C leads -> track_c (reported once by hot leg 15:35 WIB; NO new report)
HOT5 = [
    ("QuonkersAgent", "0xe8b5E3ca9f4F51366f9f4860ed70b8e929e80470", "QNKR", 132165054,
     "0x668dd26e8a7e9b9393ae8097826d787a857967b772ca7f6a9c666e5f4bbb9332", "2026-11-07 15:01:11", 41),
    ("HobnorbAgent", "0xab3F2dA0b63F5A823510095263789E9e6F26329a", "HBNB", 132164485,
     "0x4250c4d984660e4c72ab1f27650a1bbf24f59bf528e1129944d495f1c17e5d35", "2026-11-07 14:56:55", 50),
    ("WibblezapAgent", "0x8717fc8751b8Ebd6832EA145974AA77D86bE9EaD", "WBZP", 132165176,
     "0x3ef2e3c4e72fd3fdad3e423ddf80bf1d1f7a384c1944959f928e67cffe726c63", "2026-11-07 15:02:06", 43),
    ("DribblonAgent", "0x16A8aFdc97F8Cf48617bF15E47b4dA2217ea04A5", "DRBL", 132164465,
     "0xe0e39feece05eab73f4e16aaf07ea0df41242aef79ad35b6dcfb955c19b4a443", "2026-11-07 14:56:46", 45),
    ("YammerjackAgent", "0x2a71CEF7101B8b19c4ab18BeD40C3ec5EC87B9b7", "YMJK", 132164621,
     "0x07681b86620c8ce6f913b58faff72799cfa8a864a4cbb198617a66efac7fba17", "2026-11-07 14:57:56", 68),
]
added_tc = 0
for name, sale, sym, fb, ftx, fwib, sold in HOT5:
    if name in snap.get("track_c", {}):
        continue
    snap.setdefault("track_c", {})[name] = {
        "sale": sale, "token": sale, "name": name, "symbol": sym,
        "status": "lead-gate-blocked-2026-11-07",
        "saleShape": ("S1 (mint + quote(address,uint256)->(isFree,cost) + freeUsed + "
                      "AGENT_ID_REGISTRY()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; Sourcify verified, "
                      "identical template to GLPX/PLNK/CRBK/MZWK/KZMB)"),
        "sharesSold": sold, "MAX_SHARES": 1000, "FREE_PER_AGENT": 1, "MAX_PER_WALLET": 20,
        "MAX_PER_TX": 10, "TOKENS_PER_SHARE": 1000000, "PRICE_PER_SHARE": 0.00015,
        "AGENT_PRICE_PER_SHARE": 0.0001,
        "quote_user_1": "free=1,cost=0", "freeUsed_user": 0, "mintedBy_user": 0,
        "isAgent_user": 1, "balanceOf_user": 0,
        "firstMintBlock": fb, "firstMintTx": ftx, "firstMintWib": fwib,
        "ageHoursAtVerify": 0.6,
        "gateNote": ("MANDATORY WEBSITE GATE FAILED (website-only, 2026-11-02 ~14:14 WIB): methods (A)-(N) run by hot leg "
                     "15:35 WIB — no verified project website (Boltbook EN+ZH 0 mentions; Sourcify metadata zero URLs; "
                     "same-family patterns unreachable; treasury 0xf82048ff58ba63fc3904e1a3f54c0ca9e99bf8cc shared with "
                     "GLPX/PLNK/CRBK/MZWK/KZMB factory wave; project-name searches no site). X absence alone would not fail; "
                     "missing verified website does. Gate failure is a scope block, not a contract safety failure."),
        "boundary": ("LEAD ONLY, GATE-BLOCKED. Reported ONCE by hot leg 2026-11-07 15:35 WIB (hot-leg-reported.json). "
                     "NEVER previewed/minted by this run. TRACK-C LEAD DIRECT MINT does NOT trigger: mandatory website "
                     "gate failed first. Do NOT re-report unless gate evidence appears or state changes (sellout/slot lost)."),
        "lastReadBlock": 132169357, "lastReadWib": "2026-11-07 15:35 WIB (hot leg)",
    }
    added_tc += 1
print(f"HOT5-ADDED to track_c: {added_tc}")

snap["runNote1501_1107"] = (
    "Run 1501: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru dari kaki job ini, "
    "0 track-C lead/kandidat baru dari kaki job ini (5 track-C lead gate-blocked sudah dilaporkan hot leg 15:35 WIB, "
    "dicatat di track_c run ini tanpa laporan ulang), 0 pending claim baru/dibuka. 0 perubahan dilaporkan. "
    "Preflight FIXED: head via fast_rpc batch dulu (ankr eth_blockNumber tidak didukung) — PASS 7,5 dtk, head 132169471, 236 log/50 blok. "
    "Reread 453 kontrak + 62 track_c dalam 695,7 dtk (blok 132171021, interval 42,8 mnt vs run 1431); free views "
    "(freeClaimed/freeMinted) SEMUA None (453/453, degradasi eth_call seperti run 1401/1431) - nilai snapshot dipertahankan, "
    "BUKAN nol; totalSupply+totalMinted None di 103 kontrak; balanceOf(user) None di 102 kontrak; slotChanged 0. "
    "Velocity 1 pass, 0 promosi: Alchemister-0xCafEEDDF +324 ratio 2,39 (free% UNVERIFIED, early-lead-backfill, duplicate). "
    "WAR3-1aa9 +434 (first mint 14:25:04 WIB, free% 0,63% -> bukan strong lead; butuh freeMinted segar). "
    "Sold out 35 (identik run 1431, 0 baru); near-sellout Dumpster Royalty 635/650 flat; HIVE Agents totalSupply 1255 flat, balanceOf(user)=1, minted-by-user. "
    "Scan leg: window 132168529-132169528 (1000 blok, cap) chunk 20/20 selesai (0 error, 40 Ankr calls), enrichment STALL di 92/160 "
    "-> SCAN_EXIT=124 (timeout 780 dtk); 91 kontrak ter-enrich + 349 ERC-20-mint (partial JSON terselamatkan). Watermark TIDAK dimajukan "
    "run ini (milik backfill). Gap: 69 kontrak window tidak ter-enrich (alamat tidak terpulihkan dari output parsial) -> backfill. "
    "Triage scan: 1 first-seen 0xe65215428421449ba7D46A4686a2b52E35c15f30 (NFT/NFT, 2 mint/1 minter, first block 132169326) — BUKAN agent-shaped "
    "(verifikasi langsung: ABI 27 fns mintBatch/rewardToken/treeToken, tanpa registry/agentGate/free view; seen only, tidak masuk snapshot, "
    "tidak dilaporkan). 5c: 51 ERC-20 >=10, 50 sudah dicek, 1 baru dicek (0x75Ac13cF, no-shape), 0 sale-shape hit. "
    "Sourcify feed 20 kontrak (verified 15:04-15:33 WIB): 0 shape hit baru. CATATAN: cek registry Sourcify-only job ini melewatkan template "
    "AGENT_ID_REGISTRY() (registry via on-chain fn, bukan byte ABI) — 4 dari 5 lead hot leg lolos dari cek ini; hot leg menutup celah itu "
    "via baca on-chain. Discovery (subagent, legs 2/3/6): Boltbook EN+ZH + sweep EN+ZH + Square/Odaily/PANews/DappBay — 0 item benar-benar baru; "
    "semua yang muncul sudah dikenal; AGENT888/BAOracle hanya truncated/tanpa alamat (tidak bisa diverifikasi sebagai baru). "
    "Bridge: tidak berubah (115 entri, terakhir diubah 2026-11-06 02:48; 33 belum di snapshot, 7 same_owner_discarded, 0 promosi). "
    "Pending claims kosong; BINANCEAI: launched() gagal baca run ini (transport OSError, BUKAN nol), failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, tokenBalance(user)=None — tetap fase refund/failed (status run 1401 dipertahankan), tidak ada aksi; "
    "Grove freeOpen 0, freeClaimed_user false. Age sweep: 0 REMOVE; 43 dipertahankan (minted-by-user/same-owner-discarded/sold-out); "
    "374 umur UNVERIFIED tetap watchlist-only. TIDAK ada eksekusi oleh run ini (tidak ada mint/preview/claim).")
snap["runNote1501_scan"] = (
    "Run 1501 SCAN: preflight getLogs PASS 7,5 dtk (head 132169471 via fast_rpc batch bsc-dataseed1, 236 log/50 blok). "
    "Window 132168529-132169528 (1000 blok, cap) chunk 20/20 SELESAI (0 error, 40 Ankr calls; 160 NFT contracts, 349 ERC-20-mint). "
    "Enrichment STALL di 92/160 (timeout 780 dtk, SCAN_EXIT=124) — ke-5 kalinya pola stall enrichment (1301/1331/1401/1431/1501); "
    "partial JSON terselamatkan (91 kontrak ter-enrich). 69 kontrak window tidak ter-enrich (alamat tidak terpulihkan dari output parsial) "
    "-> backfill. Watermark TIDAK dimajukan run ini (milik backfill; backfill aktif lagi sejak 15:04 WIB).")
snap["runNote1501_triage"] = (
    "Run 1501 TRIAGE: scan 1 first-seen 0xe65215428421449ba7D46A4686a2b52E35c15f30 (NFT/NFT, 2 mint/1 minter, first block 132169326, "
    "tx 0x9b11cab1aa8e66bbe8966755c665501da26a8e330be92db9b5e6c9adbc4fd5bc) — BUKAN agent-shaped: ABI Sourcify 27 fns "
    "(mintBatch, MAX_MINT_BATCH, totalMinted, rewardToken, treeToken, imageURI; tanpa registry/agentRegistry/agentId fn, tanpa "
    "free-mint function/free-supply constant); seen only. Stuck address 0x099096C6028FcF7Db9AA3ca7FE23AE3fA70b5F58 sudah dikenal "
    "(seen). 5c: 51 ERC-20 mint_count>=10, 50 sudah dicek, 1 baru dicek (0x75Ac13cF23a8dccC703D1496138251FD7f247890, mint+freeUsed, "
    "tanpa registry -> no-shape), 0 sale-shape hit; track-c-scan-checked.json bertambah 1.")
snap["runNote1501_binanceai"] = (
    "Run 1501: BINANCEAI launched() GAGAL BACA (transport OSError; BUKAN nol — status terakhir dipertahankan). failed()=1, "
    "isRefundPhase()=1, totalShares()=3110, tokenClaimed(user)=0, tokenBalance(user)=None (gagal baca). Status terakhir run 1401 "
    "dipertahankan: launched=0, failed=1, isRefundPhase=1 — tetap fase refund/failed; pending_claims kosong; tidak ada aksi. "
    "Grove: freeOpen 0, freeClaimed_user false (blok 132169556).")
snap["last_run"] = "2026-11-07-1501"
snap["timestamp_wib"] = TS
snap["last_run_note"] = snap["runNote1501_1107"]
snap["last_run_wib"] = TS

with open(f"{BASE}/onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(f"{BASE}/onchain-snapshot.json.tmp", f"{BASE}/onchain-snapshot.json")
print(f"FINALIZE DONE updated={updated} none_free_views={none_free} hot5_added={added_tc} "
      f"contracts_now={len(snap['contracts'])} excluded_now={len(snap.get('excluded', {}))} "
      f"track_c_now={len(snap.get('track_c', {}))} ts={TS}")
