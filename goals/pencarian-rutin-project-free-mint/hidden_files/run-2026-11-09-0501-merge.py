#!/usr/bin/env python3
"""Merge run 2026-11-09 0501 WIB. Reloads snapshot fresh, applies reread
(554 contracts @ block 132471277, 73 track_c; 5 contracts + 16 track_c not
re-read this run keep old values, NOT zero) + coordinator triage + discovery.
Scan leg FAST-FAILED at pre-flight (Ankr unreachable x2) -> no scan output,
watermark NOT advanced, scan-state.json and seen file NOT touched this run
(avoids collision with concurrent backfill writes).
Velocity: STRICT rule per established merge implementation (prev_rate > 0
required, ratio >= 1.5, minted >= 20); prev-rate-0 passes from the
coordinator's loose velocity.json (ratio=inf) are recorded as not-countable,
per prior-run practice. No execution this run.
"""
import json, shutil, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
NEW_BLOCK = 132471277
BLOCK_SEC = 0.45

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0501-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-0501-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-09-0501-velocity.json"))
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
        note = f"Run 0501 (blok {NEW_BLOCK}, ~05:3x WIB): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
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
        note = f"Run 0501 (blok {NEW_BLOCK}, ~05:3x WIB): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
        if e.get("MAX_SUPPLY") and new_sup is not None and new_sup >= e["MAX_SUPPLY"]:
            flags.append(f"SELLOUT? {name}: totalSupply {new_sup} >= MAX_SUPPLY {e['MAX_SUPPLY']}")
        if e.get("FREE_SUPPLY") and r.get("freeClaimed") is not None and r["freeClaimed"] >= e["FREE_SUPPLY"]:
            flags.append(f"FREE POOL HABIS? {name}: freeClaimed {r['freeClaimed']} >= FREE_SUPPLY {e['FREE_SUPPLY']}")
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            e[k] = r[k]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["lastReadBlock"] = NEW_BLOCK; e["lastReadWib"] = "2026-11-09 05:3x WIB"
    e["runNote0501_1109"] = note + f"free={e.get('freeClaimed')}/{e.get('FREE_SUPPLY')}; bal_user={e.get('balanceOf_user')}; status {e.get('status')}."
    updated += 1

# SHACHO CLUB: velocity pass must NOT override same-owner discard
if "SHACHO CLUB" in C:
    C["SHACHO CLUB"]["runNote0501_1109"] = (C["SHACHO CLUB"].get("runNote0501_1109", "") +
        " PERINGATAN: velocity LOLOS run ini TAPI status tetap promotion-discarded-same-owner-2026-11-08 (ownerInDiscards=True) - velocity TIDAK meng-override discard; jangan promosikan, jangan eksekusi.")

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
    e["runNote0501_1109"] = f"Run 0501: freeMinted={e.get('freeMinted')}, totalSupply={e.get('totalSupply')} (blok {NEW_BLOCK})" + (". Nilai lama dipertahankan bila None (degradasi)." if not changed else ".")
    tc_updated += 1

# --- BHTB: new S2 early lead (track_c), website gate NOT passed ---
TC["BHTB"] = {
    "sale": "0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
    "token": "0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
    "name": "BHTB / 八荒通宝", "symbol": "BHTB", "kind": "S2 token+sale",
    "status": "early-lead-2026-11-09",
    "saleShape": "S2 VERIFIED run 0501: Sourcify exact_match, contract GenesisToken: mintGenesis(shares,agentId,referrerAgentId) payable; quote(shares,wallet); freeClaimed(address); FREE_QUOTA/FREE_TOKENS; agentIdRegistry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; mintEnd(); no owner() fn.",
    "FREE_QUOTA": 555, "freeUsed": 28, "freeRemaining": 527,
    "FREE_TOKENS": 5555, "paidPricePerShareBnb": 0.002, "paidSold": 0,
    "quote_user_1": 0, "freeClaimed_user": False,
    "maxShares_user": 10, "remainingShares_user": 10,
    "userSlot": "OPEN (verified on-chain run 0501, blok 132470505)",
    "startTimeWib": "2026-11-08T18:44:00+07:00", "mintEndWib": "2026-11-13T18:44:00+07:00",
    "launchNote": "Usia TERVERIFIKASI ~10,6 jam (startTime on-chain 2026-11-08 18:44 WIB; mintEnd on-chain 2026-11-13 18:44 WIB - klaim post 19:44 ditolak, on-chain menang). Ditemukan via Boltbook front page post /p/i9mUcPlR2mOr by dq2.ai ~05:04 WIB 2026-11-09 (9 upvotes; author menyatakan proyek human-nya sendiri, paid BNB ke wallet-nya). Velocity: 23 claimed ~05:04 -> 28 ~05:20 (+5 dlm ~16 mnt). Payout 0x45e2c8a09022914ce00cfce9a93dd3fda54d8686 (bukan di same-owner-discards). DEV_LOCKED 19.141.975 BHTB, lockUntil 2027-11-08 18:44 WIB.",
    "website": None, "gate": "NOT PASSED (run 0501): no project website found - hanya Boltbook post + BscScan + Sourcify; deep-dive metode A-N berjalan terpisah run ini.",
    "xStatus": "not found", "liquidity": "NONE - post menyatakan tidak ada LP, tidak tradable di DEX",
    "sameOwnerDiscard": False,
    "lastReadBlock": 132470505, "lastReadWib": "2026-11-09 05:2x WIB",
    "runNote0501_1109": "Run 0501: EARLY LEAD baru (S2). Free 527/555, slot user OPEN, usia ~10,6 jam terverifikasi. GATE BLOKIR: website tidak ditemukan -> TIDAK bisa eksekusi (website-only gate); TIDAK preview/mint. Dilaporkan sekali sebagai early lead + alasan gate.",
}
# --- AgentGrid / WATT: new S1 early lead (track_c), website gate NOT passed ---
TC["AgentGrid"] = {
    "sale": "0x651302C0043040D48EaAF85605E12F0549aD6D89",
    "token": "0xd8FAF2597c8b81eed4befA4A651cccF05196163b",
    "name": "AgentGrid", "symbol": "WATT", "kind": "S1 factory sale",
    "status": "early-lead-2026-11-09",
    "saleShape": "S1 VERIFIED run 0501: FREE_SHARES, freeUsed, claimShares/mint, registry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, walletOfHandle, refund, finalize, CAP_PER_AGENT 8, INVITE_BONUS, LP_BNB_RATIO; sale owner()=0x0; token owner()=0x0 (renounced). Factory 0xca143ce32fe78f1f7019d7d551a6402fc5350c73, vault 0x5856C6Ffb46b7Fb45B3B834eA9d90d292548484b, teamWallet 0xd09157c16ca3f64cf460a53c4d7704aa5966f9d3.",
    "FREE_SHARES": 500, "freeUsed": 6, "freeRemaining": 494,
    "TOKENS_PER_SHARE": 112500, "paidCount": 0, "CAP_PER_AGENT": 8,
    "deadlineWib": "2026-11-12T04:47:00+07:00",
    "launchNote": "Usia ~55 mnt saat baca (DERIVASI: deadline on-chain 2026-11-12 04:47 WIB minus durasi 3 hari -> start ~2026-11-09 04:47 WIB; BUKAN stated launch time proyek - label derivasi, bukan verifikasi penuh). Ditemukan via Sourcify recently-verified feed (verified 2026-11-08 21:48:29Z); tanpa Boltbook post, website, atau X.",
    "userSlot": "UNVERIFIED - claimedShares(agent wallet) reverts (read failure, bukan nol)",
    "website": None, "gate": "NOT PASSED (run 0501): no website/post found; deep-dive metode A-N berjalan terpisah run ini.",
    "xStatus": "not found",
    "sameOwnerDiscard": False,
    "lastReadBlock": 132470772, "lastReadWib": "2026-11-09 05:2x WIB",
    "runNote0501_1109": "Run 0501: EARLY LEAD baru (S1, Sourcify-only). Free 494/500, usia ~55 mnt (derivasi deadline-durasi). Slot user UNVERIFIED + GATE BLOKIR (website tidak ditemukan) -> TIDAK bisa eksekusi; TIDAK preview/mint. Dilaporkan sekali sebagai early lead + alasan gate.",
}
# --- NOVRA: re-confirm pool exhausted (already recorded 2026-11-08) ---
if "NOVRA" in TC and isinstance(TC["NOVRA"], dict):
    TC["NOVRA"]["freeRemaining"] = 0
    TC["NOVRA"]["runNote0501_1109"] = ("Run 0501: re-konfirmasi freeRemaining()=0 (blok 132470959); totalSupply = tepat 72 x 1.000.000 NOVRA (72 free share habis, 0 paid). "
        "Status tetap track-c-free-pool-exhausted-2026-11-08 (sudah tercatat) - bukan perubahan baru, tidak dilaporkan ulang.")

# --- top-level run note ---
s["last_run"] = "0501"
s["last_run_wib"] = NOW_STR
s["last_run_note"] = (
    f"Run 0501 (05:01 WIB 9 Nov - {NOW_STR}): re-read blok {NEW_BLOCK} ({updated} kontrak + {tc_updated} track_c, {degraded} totalSupply=None degraded (nilai lama dipertahankan, bukan nol), {tc_degraded} TC all-null; {len(not_reread)} kontrak tidak ter-baca ulang run ini). "
    f"Velocity STRICT (prev_rate>0, ratio>=1.5, >=20 token): {len(vel_pass)} lolos {vel_pass}. "
    "Koreksi vs velocity.json koordinator (17 lolos, interval nominal 60 mnt, ratio=inf dihitung lolos): 5 lolos-in-f palsu karena prev rate 0 (AURISLE, MONOLITH, Meow Cards + 2 artefak ERC-20) - per praktik mapan run sebelumnya prev rate 0 = ratio None = velocity TIDAK lolos; tidak ada promosi yang hilang karena ketiganya tetap early lead/watchlist (free% unverified / usia unverified). "
    "Scan leg FAST-FAIL di pre-flight (Ankr getLogs 50 blok gagal 2x: RemoteDisconnected ~32 dtk + ~18 dtk, ~05:07-05:08 WIB) - onchain_nft_scan.py TIDAK dijalankan; watermark TIDAK dimajukan (tetap 132449514); gap dari 132449514 terus tumbuh; 5c 0/0 (tanpa output scan). Ankr tampak unreachable dari VM, konsisten degradasi RPC sejak ~03:03 WIB. "
    "Boltbook EN+ZH (46.327/46.480 byte): 10 alamat unik, 6 baru vs snapshot. Sourcify feed 20 entri, 1 agent-sale shape (AgentGrid). Sweep: Likhin, Agent Harvest Land, Subsonic Tribe, Agent Periodic Lab (dikenal). Route 6 parsial (news-vertical kosong; fetch langsung Odaily/PANews tidak sempat). "
    "EARLY LEAD BARU (dilaporkan sekali, gate-blocked, TIDAK dieksekusi): BHTB 0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467 (S2, free 527/555, slot OPEN, usia ~10,6 jam terverifikasi, website TIDAK ditemukan, tanpa X, tanpa LP) dan AgentGrid 0x651302C0043040D48EaAF85605E12F0549aD6D89 (S1, free 494/500, usia ~55 mnt derivasi, slot user UNVERIFIED, website TIDAK ditemukan). Keduanya masuk track_c sebagai early-lead; deep-dive website metode A-N + usia Glitchpilotfox berjalan terpisah (subagent) - hasilnya dilipat sesudah merge bila mengubah status. "
    "Dead/closed re-konfirmasi: NOVRA free pool habis (sudah tercatat 2026-11-08, bukan perubahan baru), PokeChain sold out, Paw Gang mint closed 3.333/3.333, UNIT-BOT paid 0,001 BNB, Agent Zet free phase complete. "
    "SHACHO CLUB velocity LOLOS (+32, 2,39x) TAPI tetap promotion-discarded-same-owner (ownerInDiscards=True) - TIDAK dipromosikan/dieksekusi. "
    "Alchemister +137 (17,9x) free pool unknown, firstMint 2026-11-07 09:49 WIB - melewati 48 jam ~09:49 WIB hari ini bila belum sold out (watch, eksklusi di run berikut bila lewat). "
    "Leg A percobaan pertama mati eksternal ~05:14-05:16 (orphaned process group di-reap runtime); percobaan kedua (direct exec, resume dari partial) selesai EXIT=0 638,1 dtk. "
    "AGENT DOSSIER 397->399 (+2 pihak lain), bal_user 1. HIVE Agents flat 1256, bal_user=1 (holding). binanceai_claim tidak dicek ulang (refund phase, sudah dilaporkan sekali). Bridge: 116 kontrak, 0 baru (8 di luar snapshot sama, 7 same_owner_discarded), mtime tidak berubah 2026-11-08 18:21. "
    "FLAGS reread: " + ("; ".join(flags) if flags else "tidak ada sellout/pool-habis baru pada baca segar (26 flag = semua sudah dikenal).") +
    " Backfill cron: TIDAK diubah run ini (read-only; status enabled vs perintah nonaktif user 2026-11-08 tetap butuh keputusan user/main agent).")
s["runNote0501_1109"] = s["last_run_note"]

# --- hot-leg seen dedupe (fresh load right before save) ---
try:
    hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
    for _a, _n in {
        "0xffca030c6c69a5b75392aafaf5bf1980c0ed0467": "run 0501 BHTB - early lead S2 (free 527/555, slot OPEN, usia ~10,6 jam) TAPI website gate NOT PASSED (tanpa website/X/LP) - jangan laporkan ulang sebagai lead baru; hanya perubahan/promosi",
        "0x651302c0043040d48eaaf85605e12f0549ad6d89": "run 0501 AgentGrid sale - early lead S1 (free 494/500, usia ~55 mnt derivasi) TAPI website gate NOT PASSED + slot user UNVERIFIED - jangan laporkan ulang sebagai lead baru",
        "0xd8faf2597c8b81eed4befa4a651cccf05196163b": "run 0501 AgentGrid token WATT - pasangan sale 0x6513..., early lead yang sama",
        "0x75ac13cf23a8dccc703d1496138251fd7f247890": "run 0501 NOVRA - re-konfirmasi free pool habis (sudah tercatat 2026-11-08), bukan perubahan baru",
        "0x4ef929af00cb93993c3d01834c4da79200d31e32": "run 0501 PokeChain - sold out, jangan laporkan ulang",
        "0x587c303982187ec578df309d27670327b13202f8": "run 0501 Paw Gang - mint closed 3.333/3.333, jangan laporkan ulang",
        "0xd800efb5f2f44b6afb0cde553e885390a7d38156": "run 0501 UNIT-BOT - paid 0,001 BNB, bukan free",
        "0xff8bfef2c0d16bda6e8667812bca35ecb42a1a37": "run 0501 Agent Zet - free phase complete 4.000/4.000, paid only",
    }.items():
        hl.setdefault(_a, {"first_seen_wib": "2026-11-09 05:01 WIB", "note": _n})
    json.dump(hl, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
    print("hot-leg-seen updated")
except Exception as ex:
    print("hot-leg-seen SKIP:", ex)

json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: updated={updated} degraded={degraded} not_reread={len(not_reread)} tc={tc_updated} tc_degraded={tc_degraded} vel_pass={vel_pass}")
print("FLAGS:", flags if flags else "none")
