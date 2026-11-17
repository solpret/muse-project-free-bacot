#!/usr/bin/env python3
"""Merge run 2026-11-09 0531 WIB. Reloads snapshot fresh, applies reread
(553 contracts @ block 132475627, 75 track_c) + discovery + triage + verify.
Scan leg SUCCEEDED at pre-flight (13.8s) and ran (window 132475203-132476202,
1000 blocks, cap); chunk loop complete, enrichment still in progress at merge
time (23/66) — scan output partial, contracts_raw inventory complete.
scan-state.json and onchain-scan-seen.json NOT touched (backfill owns the
watermark and writes concurrently; same precedent as run 0501).
Velocity: STRICT rule (prev_rate > 0 required, ratio >= 1.5, minted >= 20).
No execution this run.
"""
import json, shutil, os, sys
sys.set_int_max_str_digits(100000)
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
NEW_BLOCK = 132475627
BLOCK_SEC = 0.45

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0531-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-0531-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {})

updated = 0; degraded = 0; vel_pass = []; flags = []; not_reread = []
for name, e in C.items():
    r = rr["reread"].get(name)
    if r is None:
        not_reread.append(name)
        continue
    prev_sup = e.get("totalSupply"); new_sup = r.get("totalSupply")
    prev_block = e.get("lastReadBlock") or 0
    interval_min = max(1.0, (NEW_BLOCK - prev_block) * BLOCK_SEC / 60.0) if prev_block else None
    if new_sup is None:
        degraded += 1
        note = f"Run 0531 (blok {NEW_BLOCK}, ~06:3x WIB): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
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
        note = f"Run 0531 (blok {NEW_BLOCK}, ~06:3x WIB): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
        if e.get("MAX_SUPPLY") and new_sup is not None and new_sup >= e["MAX_SUPPLY"]:
            flags.append(f"SELLOUT? {name}: totalSupply {new_sup} >= MAX_SUPPLY {e['MAX_SUPPLY']}")
        if e.get("FREE_SUPPLY") and r.get("freeClaimed") is not None and r["freeClaimed"] >= e["FREE_SUPPLY"]:
            flags.append(f"FREE POOL HABIS? {name}: freeClaimed {r['freeClaimed']} >= FREE_SUPPLY {e['FREE_SUPPLY']}")
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            e[k] = r[k]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["lastReadBlock"] = NEW_BLOCK; e["lastReadWib"] = "2026-11-09 06:3x WIB"
    e["runNote0531_1109"] = note + f"free={e.get('freeClaimed')}/{e.get('FREE_SUPPLY')}; bal_user={e.get('balanceOf_user')}; status {e.get('status')}."
    updated += 1

# SHACHO CLUB: velocity pass must NOT override same-owner discard
if "SHACHO CLUB" in C:
    C["SHACHO CLUB"]["runNote0531_1109"] = (C["SHACHO CLUB"].get("runNote0531_1109", "") +
        " PERINGATAN: status tetap promotion-discarded-same-owner-2026-11-08 (ownerInDiscards=True) - velocity TIDAK meng-override discard; jangan promosikan, jangan eksekusi.")

# Alchemister: velocity LOLOS but free pool unknown; 48h crossing ~09:49 WIB today
if "Alchemister-0xCafEEDDF" in C:
    C["Alchemister-0xCafEEDDF"]["runNote0531_1109"] = (C["Alchemister-0xCafEEDDF"].get("runNote0531_1109", "") +
        " WATCH: velocity LOLOS run ini (+177, 5,43/mnt, 3,13x) TAPI free pool unknown + X unverified -> BUKAN strong lead/kandidat. firstMint 2026-11-07 09:49 WIB: melewati 48 jam ~09:49 WIB hari ini bila belum sold out (MAX 15000, kini 6137) -> run berikut WAJIB age-exclude bila lewat.")

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
    e["runNote0531_1109"] = f"Run 0531: freeMinted={e.get('freeMinted')}, totalSupply={e.get('totalSupply')} (blok {NEW_BLOCK})" + (". Nilai lama dipertahankan bila None (degradasi)." if not changed else ".")
    tc_updated += 1

# --- BHTB / AgentGrid fresh free-pool reads (blok 132478744) ---
if "BHTB" in TC and isinstance(TC["BHTB"], dict):
    TC["BHTB"]["freeUsed"] = 96
    TC["BHTB"]["freeRemaining"] = 555 - 96
    TC["BHTB"]["runNote0531_1109"] = ("Run 0531: freeUsed 28->96/555 (459 free tersisa, blok 132478744); freeClaimed(user)=0, slot user tetap OPEN. "
        "Gate tetap NOT PASSED (deep-dive 0501: tanpa website/X/LP) -> TIDAK preview/mint. Pool menguras cepat (+68 sejak 0501) tapi gate memblokir eksekusi.")
if "AgentGrid" in TC and isinstance(TC["AgentGrid"], dict):
    TC["AgentGrid"]["freeUsed"] = 19
    TC["AgentGrid"]["freeRemaining"] = 500 - 19
    TC["AgentGrid"]["runNote0531_1109"] = ("Run 0531: freeUsed 6->19/500 (481 free tersisa, blok 132478744); slot user tetap UNVERIFIED (claimedShares reverts). "
        "Gate tetap NOT PASSED -> TIDAK preview/mint.")

# --- Beast / BAHUANG3: new EARLY LEAD (track A), gate NOT PASSED ---
C["BAHUANG3"] = {
    "address": "0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591",
    "status": "early-lead-2026-11-09",
    "name": "BAHUANG3 / 八荒神兽·八部众·史", "symbol": "BAHUANG3", "kind": "ERC721",
    "totalMinted": 412, "freeMinted": 412, "FREE_CAP": 6000, "PAID_CAP": 3000,
    "freePctVerified": round(412 / 6000 * 100, 1),
    "mintStart": 1794176990, "mintEnd": 1794608990,
    "mintStartWib": "2026-11-09 05:29:50", "mintEndWib": "2026-11-14 05:29:50",
    "firstMintBlock": 132474152, "firstMintWib": "2026-11-09 05:40:07",
    "freeAllowance_user": 2, "userSlot": "OPEN (freeAllowance(agent wallet)=2, balance 0)",
    "payout": "0x45e2c8a09022914ce00cfce9a93dd3fda54d8686",
    "agentId": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "saleShape": "S1 VERIFIED run 0531: Sourcify exact_match, mint+quote+freeMinted/freeCount/freeAllowance+agentId registry; registry bytes hit True; scan window 132475203-132476202: 127 mints / 32 minters, first block 132475336.",
    "launchNote": "Usia TERVERIFIKASI ~50 mnt (mintStart on-chain 2026-11-09 05:29:50 WIB + first mint blok 132474152 = 05:40:07 WIB via Ankr getLogs binary search + dataseed timestamp). Ditemukan via Sourcify recently-verified feed (verified 2026-11-08 22:30:20Z) + scan cross-check.",
    "website": None, "gate": "NOT PASSED (run 0531): no project website found - metode A,G,H,I,C,B,N dicoba; tokenURI Arweave JSON tanpa external_url; (L) BscScan token-info via live browser didelegasikan, hasil pending saat merge - lihat run log. Payout = wallet author BHTB (dq2.ai), bukan di discards.",
    "xStatus": "not found",
    "tokenURI": "https://arweave.net/DM7ayfWzaANA2YZgmwKUm_Td5N3k15lzRB8CFPH631U/{n}.json",
    "sameOwnerDiscard": False,
    "lastReadBlock": 132476750, "lastReadWib": "2026-11-09 06:0x WIB",
    "velocityLegPasses": False,
    "runNote0531_1109": "Run 0531: EARLY LEAD baru. Free 412/6000 = 6,9%, slot user OPEN (allowance 2), usia ~50 mnt terverifikasi. GATE BLOKIR: website tidak ditemukan -> TIDAK preview/mint (early lead memang tidak pernah di-preview/di-mint). Dilaporkan sekali sebagai early lead + alasan gate.",
}
# --- LIFTCAT: new EARLY LEAD (track A), first mint verified ---
C["LIFTCAT"] = {
    "address": "0x53aA0c94b9f670866a5EDbc42A66bf5cAB59c92a",
    "status": "early-lead-2026-11-09",
    "name": "LIFTCAT", "symbol": "LIFTCAT", "kind": "ERC721",
    "totalMinted": 190, "freeMinted": 190, "FREE_CAP": 222, "MAX_SUPPLY": 1111,
    "freePctVerified": round(190 / 222 * 100, 1),
    "mintOpen": 1,
    "firstMintBlock": 132471058, "firstMintWib": "2026-11-09 05:16:55",
    "owner": "0x13333df46ab3e95f4166370d571e7b73aad06370",
    "saleShape": "Agent-shaped VERIFIED run 0531: registry bytes True, Sourcify exact_match, free funcs FREE_CAP/FREE_PER_WALLET/freeCount/freeMint/freeMinted; scan window: 10 mints / 10 minters, first block 132475221.",
    "launchNote": "Usia TERVERIFIKASI ~1,8 jam (first mint blok 132471058 = 2026-11-09 05:16:55 WIB via Ankr getLogs binary search + dataseed timestamp; Sourcify verifiedAt 2026-11-08T22:16:37Z).",
    "userSlot": "UNVERIFIED - tidak ada per-user free view di ABI (freeClaimed(address) revert/tidak ada; freeCount() global) - TIDAK bisa verifikasi slot tanpa preview, dan early lead tidak pernah di-preview.",
    "website": None, "gate": "NOT CHECKED run ini (early lead: gate hanya relevan bila promosi ke strong lead; website/X belum dicoba)",
    "xStatus": "not checked",
    "sameOwnerDiscard": False,
    "lastReadBlock": 132478744, "lastReadWib": "2026-11-09 06:5x WIB",
    "velocityLegPasses": False,
    "runNote0531_1109": "Run 0531: EARLY LEAD baru. Free 190/222 = 85,6% (!), usia ~1,8 jam terverifikasi, owner bukan di discards. Slot user UNVERIFIED (tanpa per-user view) + velocity belum terhitung (baseline pertama) -> BUKAN strong lead/kandidat. TIDAK preview/mint. Dilaporkan sekali sebagai early lead.",
}
# --- Compasyn: BLOCKED (same-owner discard + age-excluded + gate failed) ---
C["Compasyn"] = {
    "address": "0xcd1bb8013e924e26ed4131a69304f2969c4f8d28",
    "status": "promotion-discarded-same-owner-2026-11-09",
    "name": "Compasyn", "symbol": "CMPN", "kind": "ERC721",
    "totalSupply": 520, "freeClaimed": 515, "FREE_SUPPLY": 1490, "MAX_SUPPLY": 2129,
    "freePctVerified": round(515 / 1490 * 100, 1),
    "mintOpen": 1, "FREE_PER_WALLET": 1, "MAX_PER_WALLET": 50,
    "firstMintBlock": 131395780, "firstMintWib": "2026-11-03 14:49:54",
    "owner": "0x310cea29c4827efc82b1d7ff4c70b7332d236917",
    "sameOwnerDiscard": True,
    "discardDetail": "owner 0x310c... = owner Neuroveil 0x7BCA844AD4cD95b5B30ecC3885dfBab45F38e99b + Homunqul 0x5539dD54c00094Cbd186f08AA2d8fF3A8c098ddE (discarded 2026-11-03 same-owner cluster).",
    "launchNote": "Usia ~5,7 hari (first mint 2026-11-03 14:49:54 WIB) -> AGE-EXCLUDED (>48 jam). Ditemukan via Boltbook front page (post cskh.ai recheck blok 132,475,490 + hooya.ai free mint #127 tx blok 132,459,053).",
    "website": None, "gate": "NOT PASSED (run 0531): no project website found - metode A,G,H,I,C,B dicoba; post hooya.ai sendiri menyatakan 'No official site/X publishes this contract'.",
    "xStatus": "not found",
    "lastReadBlock": 132476750, "lastReadWib": "2026-11-09 06:0x WIB",
    "velocityLegPasses": False,
    "runNote0531_1109": "Run 0531: BLOCKED tiga alasan independen: (1) same-owner discard (owner Neuroveil/Homunqul) - STOP, jangan preview/eksekusi; (2) age-excluded ~5,7 hari; (3) website gate NOT passed. Dilaporkan sekali sebagai blocked, BUKAN lead. Jangan promosikan, jangan eksekusi.",
}
# --- LUCKY LIFE: BLOCKED (same-owner discard, costOf/mintsLeft wave) ---
C["LUCKY LIFE"] = {
    "address": "0x6D318F9e4147b7A9B1eC8196BA1799592e5ae44a",
    "status": "promotion-discarded-same-owner-2026-11-09",
    "name": "LUCKY LIFE", "symbol": "LUCKY", "kind": "ERC721",
    "totalSupply": 276, "freeLeft": 1612, "MAX_SUPPLY": 1888,
    "mintOpen": 1,
    "owner": "0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd",
    "sameOwnerDiscard": True,
    "discardDetail": "owner 0x1103... = owner gelombang costOf/mintsLeft 10 kontrak (Toucan Play, jelly.exe, Los Flamingos, Moonhowlers, Counting Sheep, Tusk & Trunk, getpuffr, Hippo Social Club, LLAMA DRAMA, Danger Noodles) + SHACHO CLUB, discarded 2026-11-06/08.",
    "launchNote": "First mint UNVERIFIED (23 mint lebih awal dalam probe [132400000, first-1]; Sourcify verifiedAt 2026-11-07T12:10:46Z). Tidak relevan - discard memblokir apa pun.",
    "website": None, "gate": "NOT CHECKED (discard memblokir duluan)",
    "xStatus": "not checked",
    "lastReadBlock": 132478744, "lastReadWib": "2026-11-09 06:5x WIB",
    "velocityLegPasses": False,
    "runNote0531_1109": "Run 0531: BLOCKED - same-owner discard (gelombang costOf/mintsLeft 0x1103...). STOP, jangan promosikan, jangan eksekusi. Dilaporkan sekali sebagai blocked.",
}
# --- Chipbotcore: watchlist-only, first mint unverified ---
C["Chipbotcore"] = {
    "address": "0xc6ee7c22c5bDd919f5775ab38c53BD86c167D56f",
    "status": "watchlist-only-first-seen-2026-11-09",
    "name": "Chipbotcore", "symbol": "CHIPBOTCORE", "kind": "ERC721",
    "totalSupply": 508, "freeClaimed": 503, "FREE_SUPPLY": 3333,
    "freePctVerified": round(503 / 3333 * 100, 1),
    "mintOpen": 1,
    "owner": "0x6f244724f61d8c7fc9af40dd37ff7c82bf2b8f5d",
    "saleShape": "S1-shaped ABI (mint+quote+freeClaimed/freeFor/freeLeft/freeUsed+agent), registry bytes True, Sourcify exact_match; scan window: 1 mint, first block 132475401.",
    "launchNote": "First mint UNVERIFIED (tidak ada mint dalam probe [132400000, 132475400] ~10 jam sebelum window, TAPI kontrak terverifikasi 2026-11-03T13:03:06Z - first mint bisa lebih tua; binary search penuh belum dilakukan run ini).",
    "userSlot": "UNVERIFIED (freeClaimed(user) revert/tidak ada view)",
    "website": None, "gate": "NOT CHECKED run ini",
    "xStatus": "not checked",
    "sameOwnerDiscard": False,
    "lastReadBlock": 132478744, "lastReadWib": "2026-11-09 06:5x WIB",
    "velocityLegPasses": False,
    "runNote0531_1109": "Run 0531: watchlist-only (first-seen scan, agent-shaped, 1 mint di window). First mint UNVERIFIED -> BUKAN early lead. Free 15,1%. Perlu binary search first-mint bila mau promosi; tidak dilaporkan sebagai lead.",
}
# --- Pending triage items (verify3 still running at merge; triage-only data) ---
C["0x51D3C010"] = {
    "address": "0x51D3C0101696956Baf928899D5BB57544F00C9B9",
    "status": "watchlist-only-first-seen-2026-11-09",
    "name": "0x51D3C010 (nama belum dibaca)", "kind": "ERC721",
    "saleShape": "S1-shaped ABI (mint+quote+freeLeft/freeOf/setFree+agent, mintWithAgentTokenId), registry bytes True, Sourcify exact_match; scan window: 1 mint, first block 132475903. Pola ABI IDENTIK dengan LUCKY LIFE (gelombang costOf/mintsLeft 0x1103...) - owner BELUM dibaca saat merge (verify3 masih jalan) - diduga kuat same-owner discard, WAJIB cek owner sebelum promosi apa pun.",
    "launchNote": "First mint UNVERIFIED.",
    "userSlot": "UNVERIFIED", "website": None, "gate": "NOT CHECKED",
    "xStatus": "not checked", "sameOwnerDiscard": "UNVERIFIED (suspect: same wave as LUCKY LIFE)",
    "lastReadBlock": 132476202, "lastReadWib": "2026-11-09 06:5x WIB",
    "velocityLegPasses": False,
    "runNote0531_1109": "Run 0531: watchlist-only (first-seen scan, agent-shaped, 1 mint di window). Verify3 belum selesai saat merge - nama/owner/free belum dibaca. JANGAN promosikan sebelum owner dicek (kemungkinan same-owner discard gelombang 0x1103...).",
}
C["0xCf8d6492"] = {
    "address": "0xCf8d64926c7299192794f6bbfe733A8f211Efe13",
    "status": "watchlist-only-first-seen-2026-11-09",
    "name": "0xCf8d6492 (nama belum dibaca)", "kind": "ERC721",
    "saleShape": "Registry bytes True, Sourcify exact_match, mint funcs ada TAPI tanpa free view (free=[]) - bentuk free TIDAK terbukti; scan window: 5 mints / 5 minters, first block 132475207.",
    "launchNote": "First mint UNVERIFIED.",
    "userSlot": "UNVERIFIED", "website": None, "gate": "NOT CHECKED",
    "xStatus": "not checked", "sameOwnerDiscard": "UNVERIFIED",
    "lastReadBlock": 132476202, "lastReadWib": "2026-11-09 06:5x WIB",
    "velocityLegPasses": False,
    "runNote0531_1109": "Run 0531: watchlist-only (first-seen scan, registry hit tapi tanpa free view). Verify3 belum selesai saat merge. BUKAN early lead (free shape tidak terbukti).",
}
C["0xF4F2A871"] = {
    "address": "0xF4F2A87100Bb8fECF562cF4cCaC6D615C424316c",
    "status": "watchlist-only-first-seen-2026-11-09",
    "name": "0xF4F2A871 (nama belum dibaca)", "kind": "ERC721",
    "saleShape": "Registry bytes True, Sourcify exact_match, free func freePerWallet, mint funcs (mintedByAgentId); scan window: 1 mint, first block 132475293.",
    "launchNote": "First mint UNVERIFIED.",
    "userSlot": "UNVERIFIED", "website": None, "gate": "NOT CHECKED",
    "xStatus": "not checked", "sameOwnerDiscard": "UNVERIFIED",
    "lastReadBlock": 132476202, "lastReadWib": "2026-11-09 06:5x WIB",
    "velocityLegPasses": False,
    "runNote0531_1109": "Run 0531: watchlist-only (first-seen scan, agent-shaped, 1 mint di window). Verify3 belum selesai saat merge. BUKAN early lead (first mint unverified).",
}

# --- top-level run note ---
s["last_run"] = "0531"
s["last_run_wib"] = NOW_STR
s["last_run_note"] = (
    f"Run 0531 (05:31 WIB 9 Nov - {NOW_STR}): re-read blok {NEW_BLOCK} ({updated} kontrak + {tc_updated} track_c, {degraded} totalSupply=None degraded (nilai lama dipertahankan, bukan nol), {tc_degraded} TC all-null; {len(not_reread)} kontrak tidak ter-baca ulang run ini). "
    f"Velocity STRICT (prev_rate>0, ratio>=1.5, >=20 token): {len(vel_pass)} lolos {vel_pass}. "
    "MeowBark/Zhenzhu/bridge-0x93bf = artefak satuan-mentah ERC-20, bukan promosi. Alchemister-0xCafEEDDF +177 (5,43/mnt, 3,13x) velocity LOLOS TAPI free pool unknown + X unverified -> BUKAN strong lead/kandidat; firstMint 2026-11-07 09:49 WIB, melewati 48 jam ~09:49 WIB hari ini -> run berikut WAJIB age-exclude bila belum sold out (MAX 15000, kini 6137). "
    "0 sellout / pool-habis BARU (semua flag pada baca segar sudah pada cap di nilai snapshot 0501 - 0 crossing interval ini). "
    "Scan leg BERHASIL pre-flight (Ankr getLogs 50 blok OK 13,8 dtk, 1000 logs) + scan jalan: window 132475203-132476202 (1000 blok, cap), 66 NFT contracts raw (65 ERC721 + 1 ERC1155), 275 ERC20-mint, enrichment masih jalan saat merge (23/66). Watermark TIDAK dimajukan run ini (backfill owns it; last_scanned_block tetap 132460664 per scan-state; skipped gap 132460665-132475202 milik backfill). "
    "5c: 42 kandidat ERC20 mc>=10, 10 baru dicek (0 dibuang sampling limit), 0 sale-shape hit (semua Sourcify not_verified; registry_bytes=true tapi ABI unverified = bentuk unknown). "
    "Boltbook EN+ZH (45.829/46.981 byte): 10 alamat unik, 6 baru vs snapshot (2 wallet/tx-hash bukan kontrak; 2 sudah dicek hot-leg; Compasyn baru; 0xf1d1650d sudah di scan-seen). Sourcify feed 20 entri (verified 22:12-22:47 UTC), 2 sale-shape hit (Beast + Compasyn via Boltbook). Sweep: MOLT/Nidavellir/Subsonic/Piggy/Believers/Agent Zet (dikenal/excluded/dead, tidak dilaporkan ulang). Route 6 parsial (news-vertical kosong; fetch langsung Odaily/PANews tidak sempat). "
    "EARLY LEAD BARU (dilaporkan sekali, TIDAK dieksekusi): BAHUANG3 0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591 (free 412/6000=6,9%, slot OPEN allowance 2, usia ~50 mnt terverifikasi via mintStart+first mint 05:40:07 WIB, website gate NOT PASSED) dan LIFTCAT 0x53aA0c94b9f670866a5EDbc42A66bf5cAB59c92a (free 190/222=85,6%, first mint 05:16:55 WIB terverifikasi, slot user UNVERIFIED - tanpa per-user view, velocity belum terhitung). "
    "BLOCKED (dilaporkan sekali, BUKAN lead): Compasyn 0xcd1bb8013e924e26ed4131a69304f2969c4f8d28 (same-owner discard Neuroveil/Homunqul + age-excluded ~5,7 hari + website gate NOT passed) dan LUCKY LIFE 0x6D318F9e4147b7A9B1eC8196BA1799592e5ae44a (same-owner discard gelombang costOf/mintsLeft 0x1103...). "
    "Watchlist-only baru: Chipbotcore (first mint unverified), 0x51D3C010 (diduga same-wave LUCKY LIFE, owner belum dibaca), 0xCf8d6492 (tanpa free view), 0xF4F2A871. "
    "BHTB freeUsed 28->96/555 (459 tersisa, blok 132478744), slot OPEN, gate tetap NOT PASSED. AgentGrid freeUsed 6->19/500 (481 tersisa), slot tetap UNVERIFIED, gate tetap NOT PASSED. "
    "Bridge: 116 kontrak, 0 promosi (9 di luar snapshot = temuan pelengkap scan unassigned + 1 same_owner_discarded Krillfarm; Glitchpilotfox di luar snapshot karena dihapus 0501 age-excluded). binanceai.fun TIDAK dicek ulang (refund phase, sudah dilaporkan sekali). "
    "FLAGS reread: " + ("; ".join(flags) if flags else "tidak ada sellout/pool-habis baru pada baca segar (0 crossing interval ini).") +
    " Backfill cron: TIDAK diubah run ini (read-only; status enabled vs perintah nonaktif user 2026-11-08 tetap butuh keputusan user/main agent). "
    "Method (L) BscScan token-info untuk Beast via live browser didelegasikan (task browser-task:421843eb) - hasil pending saat merge; gate Beast sudah NOT PASSED atas metode A-K,M,N.")
s["runNote0531_1109"] = s["last_run_note"]

# --- hot-leg seen dedupe (fresh load right before save) ---
try:
    hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
    for _a, _n in {
        "0x2ccb3fa957e69abd46a6651cc1444ef2ea9bd591": "run 0531 BAHUANG3 - early lead (free 412/6000=6,9%, slot OPEN, usia ~50 mnt) TAPI website gate NOT PASSED - jangan laporkan ulang sebagai lead baru; hanya perubahan/promosi",
        "0x53aa0c94b9f670866a5edbc42a66bf5cAB59c92a": "run 0531 LIFTCAT - early lead (free 190/222=85,6%, first mint 05:16:55 WIB) TAPI slot user UNVERIFIED + velocity belum terhitung - jangan laporkan ulang sebagai lead baru; hanya perubahan/promosi",
        "0xcd1bb8013e924e26ed4131a69304f2969c4f8d28": "run 0531 Compasyn - BLOCKED: same-owner discard (Neuroveil/Homunqul) + age-excluded ~5,7 hari + website gate NOT PASSED - jangan promosikan, jangan eksekusi, jangan laporkan ulang",
        "0x6d318f9e4147b7a9b1ec8196ba1799592e5ae44a": "run 0531 LUCKY LIFE - BLOCKED: same-owner discard gelombang costOf/mintsLeft 0x1103... - jangan promosikan, jangan eksekusi, jangan laporkan ulang",
        "0xc6ee7c22c5bdd919f5775ab38c53bd86c167d56f": "run 0531 Chipbotcore - watchlist-only (first mint unverified, free 15,1%) - bukan early lead; hanya perubahan/promosi",
        "0x51d3c0101696956baf928899d5bb57544f00c9b9": "run 0531 0x51D3C010 - watchlist-only, diduga same-wave LUCKY LIFE (owner belum dibaca saat merge) - cek owner sebelum promosi apa pun",
        "0xcf8d64926c7299192794f6bbfe733a8f211efe13": "run 0531 0xCf8d6492 - watchlist-only (registry hit tapi tanpa free view) - bukan early lead",
        "0xf4f2a87100bb8fecf562cf4ccac6d615c424316c": "run 0531 0xF4F2A871 - watchlist-only (first mint unverified) - bukan early lead",
    }.items():
        hl.setdefault(_a, {"first_seen_wib": "2026-11-09 06:3x WIB", "note": _n})
    json.dump(hl, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
    print("hot-leg-seen updated")
except Exception as ex:
    print("hot-leg-seen SKIP:", ex)

json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: updated={updated} degraded={degraded} not_reread={len(not_reread)} tc={tc_updated} tc_degraded={tc_degraded} vel_pass={vel_pass}")
print("FLAGS:", flags if flags else "none")
