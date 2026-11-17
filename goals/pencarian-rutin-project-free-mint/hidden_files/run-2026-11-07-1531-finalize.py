#!/usr/bin/env python3
"""Finalize run 1531 (FRESH — written for this run's own data; do NOT reuse the
1501 copy, which hardcodes run-1501 blocks/notes). Applies reread/velocity,
writes run notes. Reloads snapshot at write time; atomic write."""
import json, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132172450
NOW = datetime.now(timezone(timedelta(hours=7)))
TS = NOW.strftime("%Y-%m-%d %H:%M WIB")
RUN = "2026-11-07 run 1531"

re = json.load(open(f"{BASE}/run-2026-11-07-1531-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1531-velocity.json"))

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
    alc["velocityNote1531"] = ("Run 1531 (blok 132172450, interval 10,72 mnt vs run 1501): 2666->2840 (+174, 16,24/mnt, "
        "ratio 5,12 vs prev 3,17/mnt) -> velocity LOLOS ke-2 berturut-turut, TAPI TIDAK promosi: free% UNVERIFIED "
        "(Sourcify NOT_VERIFIED, tanpa ABI — free views/quote tidak bisa dibaca; freePct snapshot None) + status "
        "early-lead-backfill-2026-11-07 (sudah dilaporkan sebagai EARLY; kemungkinan duplikat/redeploy Alchemister "
        "0x69037Db8, owner + nama/simbol sama). Umur terverifikasi first mint 09:49:19 WIB hari ini (~6 jam). "
        "Bukan strong lead/kandidat.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote1531"] = (f"Run 1531 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 1501 (1255) -> velocity GAGAL; "
        "balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.")
war3 = snap["contracts"].get("WAR3-1aa9")
if war3 is not None:
    war3["runNote1531"] = ("Run 1531: totalSupply 605->874 (+269 dalam ~10,7 mnt); velocity TIDAK lolos (belum ada prev rate); "
        "first mint 2026-11-07 14:25:04 WIB, early-lead-backfill; free% snapshot 0,63% (19/3000) << 25% -> BUKAN strong lead. "
        "+269 tidak bisa dibedakan free vs paid (PRICE 0,0017 BNB) karena freeMinted segar None. Butuh baca freeMinted segar run berikut.")

snap["runNote1531_1107"] = (
    "Run 1531: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru dari kaki job ini, "
    "0 track-C lead/kandidat baru dari kaki job ini, 0 pending claim baru/dibuka. 0 perubahan dilaporkan. "
    "Preflight PASS 11,7 dtk: head via fast_rpc batch dulu (ankr eth_blockNumber tidak didukung) — head 132172326, 484 log/50 blok. "
    "Reread 453 kontrak + 67 track_c dalam 721,1 dtk (blok 132172450, interval 1429 blok ~10,7 mnt vs run 1501); free views "
    "(freeClaimed/freeMinted) SEMUA None (453/453, degradasi eth_call seperti run 1401/1431/1501) - nilai snapshot dipertahankan, "
    "BUKAN nol; totalSupply+totalMinted None di 103 kontrak; balanceOf(user) None di 102 kontrak; track_c fresh free views 0/67; slotChanged 0. "
    "Velocity 1 pass, 0 promosi: Alchemister-0xCafEEDDF +174 ratio 5,12 (free% UNVERIFIED, early-lead-backfill, duplikat/redeploy "
    "Alchemister 0x69037Db8). WAR3-1aa9 +269 (first mint 14:25:04 WIB, free% 0,63% -> bukan strong lead; butuh freeMinted segar). "
    "Sold out 35 (identik run 1501, 0 baru; 32 belum berlabel sold-out di snapshot — lag label; 2 artefak unit AnonymousAgent-Token, "
    "WAGagent); near-sellout Dumpster Royalty 637/650 (sisa 13, dari 15 di 1501); HIVE Agents totalSupply 1255 flat, balanceOf(user)=1, minted-by-user. "
    "Scan leg: window 132171382-132172381 (1000 blok, cap) chunk 20/20 selesai (0 error, 40 Ankr calls), enrichment STALL di 62/117 "
    "-> SCAN_EXIT=124 (timeout 700 dtk); 61 kontrak ter-enrich + 353 ERC-20-mint (partial JSON terselamatkan). Watermark TIDAK dimajukan "
    "run ini (milik backfill). Gap: 56 kontrak window tidak ter-enrich (alamat tidak terpulihkan dari output parsial) -> backfill. "
    "Triage scan: 0 first-seen (61 ter-enrich semua sudah dikenal); stuck address 0x1a7a8BbB49e3e8Cf951996789Fd69d4C7524A2B4 sudah dikenal. "
    "5c: 47 ERC-20 >=10, 45 sudah dicek, 2 baru dicek (0x0d1BEE88F4F92273D7E31D9AC19FC3F7E834F57D, 0xDEe25A06Ea550fA5F4A0fBAc20d630297169179A, "
    "keduanya Sourcify not_verified), 0 sale-shape hit. "
    "Sourcify feed 20 kontrak (verified 15:25-15:55 WIB): 0 shape hit baru. CATATAN: cek registry Sourcify-only job ini melewatkan template "
    "AGENT_ID_REGISTRY() (registry via on-chain fn, bukan byte ABI) — hot leg menutup celah itu via baca on-chain. "
    "Discovery (subagent, legs 2/3/6): Boltbook EN+ZH FRESH (curl 15:56 WIB, post 'just now' s.d. ~10 mnt, bukan crawl basi) + author page "
    "0xrifu.ai + sweep EN+ZH + Square/Odaily/PANews/DappBay (321 entri) — 0 item benar-benar baru; semua sudah dikenal; AGENT888 alamat "
    "LENGKAP dipulihkan 0xae9230f154f7fc38edefe6404ce1e37478daa6ae (sudah ada di HF, bukan baru); Nanoirys free mint SUDAH HABIS (233/333); "
    "Ptah cutoff mint 8 Nov 11:44 WIB. "
    "Bridge: tidak berubah (115 entri, terakhir diubah 2026-11-06 02:48; 33 belum di snapshot, 7 same_owner_discarded, 0 promosi). "
    "Pending claims kosong; BINANCEAI: launched() gagal baca run ini (transport OSError, BUKAN nol), failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, tokenBalance(user)=0 — tetap fase refund/failed, tidak ada aksi; "
    "Grove freeOpen 0, freeClaimed_user false (blok 132172669). Age sweep: 0 REMOVE; 43 dipertahankan (minted-by-user/same-owner-discarded/sold-out); "
    "374 umur UNVERIFIED tetap watchlist-only. 5 kontrak absen sejak 2026-11-06-2331 (Mummyhive, LuckyBox-d08e, SnailMail, Jolly, AgentGlyph) "
    "tanpa field address — nilai lama dipertahankan. "
    "KOREKSI PETA WALLET (MEMORY.md ~15:58 WIB): 0xeb23... adalah agent wallet baw, BUKAN wallet utama (utama = 0xcf3c...7418); baw TERKUNCI ke "
    "0xeb23 (user gonta-ganti wallet aktif ke wallet 2/3 di aplikasi Binance, baw tetap 0xeb23); wallet 3 tidak bisa diotomasi via baw. "
    "Slot checks job ini tetap memakai 0xeb23 (wallet eksekusi baw). TIDAK ada eksekusi oleh run ini (tidak ada mint/preview/claim).")
snap["runNote1531_scan"] = (
    "Run 1531 SCAN: preflight getLogs PASS 11,7 dtk (head 132172326 via fast_rpc batch bsc-dataseed1, 484 log/50 blok). "
    "Window 132171382-132172381 (1000 blok, cap) chunk 20/20 SELESAI (0 error, 40 Ankr calls; 117 NFT contracts, 353 ERC-20-mint). "
    "Enrichment STALL di 62/117 (timeout 700 dtk, SCAN_EXIT=124) — pola stall enrichment berulang; "
    "partial JSON terselamatkan (61 kontrak ter-enrich). 56 kontrak window tidak ter-enrich (alamat tidak terpulihkan dari output parsial) "
    "-> backfill. Watermark TIDAK dimajukan run ini (milik backfill).")
snap["runNote1531_triage"] = (
    "Run 1531 TRIAGE: scan 0 first-seen (61 ter-enrich semua sudah dikenal). Stuck address "
    "0x1a7a8BbB49e3e8Cf951996789Fd69d4C7524A2B4 sudah dikenal (seen). "
    "5c: 47 ERC-20 mint_count>=10, 45 sudah dicek, 2 baru dicek (0x0d1BEE88F4F92273D7E31D9AC19FC3F7E834F57D, "
    "0xDEe25A06Ea550fA5F4A0fBAc20d630297169179A, keduanya Sourcify not_verified), 0 sale-shape hit; track-c-scan-checked.json bertambah 2.")
snap["runNote1531_binanceai"] = (
    "Run 1531: BINANCEAI launched() GAGAL BACA (transport OSError; BUKAN nol — status terakhir dipertahankan). failed()=1, "
    "isRefundPhase()=1, totalShares()=3110, tokenClaimed(user)=0, tokenBalance(user)=0. Status dipertahankan: launched=0, failed=1, "
    "isRefundPhase=1 — tetap fase refund/failed; pending_claims kosong; tidak ada aksi. "
    "Grove: freeOpen 0, freeClaimed_user false (blok 132172669).")
snap["last_run"] = "2026-11-07-1531"
snap["timestamp_wib"] = TS
snap["last_run_note"] = snap["runNote1531_1107"]
snap["last_run_wib"] = TS

with open(f"{BASE}/onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(f"{BASE}/onchain-snapshot.json.tmp", f"{BASE}/onchain-snapshot.json")
print(f"FINALIZE DONE updated={updated} none_free_views={none_free} "
      f"contracts_now={len(snap['contracts'])} excluded_now={len(snap.get('excluded', {}))} "
      f"track_c_now={len(snap.get('track_c', {}))} ts={TS}")
