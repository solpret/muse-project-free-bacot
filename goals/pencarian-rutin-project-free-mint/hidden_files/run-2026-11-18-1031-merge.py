#!/usr/bin/env python3
"""Merge run 2026-11-18 10:31 WIB re-read into onchain-snapshot.json (lean merge).
Fixes the 1001-merge name mismatch: PLAN names (EIM, Matrix, AgentBubble) are
resolved to snapshot entries by ADDRESS, not by FIELDS key. Velocity baseline is
the 1001 REREAD (authoritative last read), NOT the snapshot's stored supply:
the 1001 merge never wrote EIM totalMinted (630 stale vs 1001 read 650) because
its FIELDS key 'Everything Is Mine (EIM)' did not match the PLAN name 'EIM'.
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1031-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1001-reread.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~10:31 WIB"
BLOCK = reread["block"]
PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")

addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k

# 1001 rates (per 1001 run log) for the movers; others fall back to snapshot stored rate.
RATE1001 = {"SPARKS": 0.064, "EIM": 0.418, "STOCK AGENT": 0.129, "Mine Card": 0.386,
            "PunchCard": 0.064, "Kitebots": 0.0322, "RaceAgents": 0.0301,
            "AgentEcho": 0.1608, "CPASS": 0.0965, "Matrix": 0.0, "AgentBubble": None}

SUPPLY_VIEWS = ["totalSupply", "totalMinted"]
updated, missed = [], []
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name)
        continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    # velocity vs 1001 reread baseline
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply")
    pval = pv.get("totalSupply")
    view = "totalSupply"
    if fresh is None or not isinstance(fresh, int):
        fresh = v.get("totalMinted")
        pval = pv.get("totalMinted")
        view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = RATE1001.get(name)
        if prev_rate is None:
            prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        e["previousTotalSupply"] = pval
        e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4)
        e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel
        e["supplyView"] = view
    e["lastReadWib"] = NOW
    e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (no snapshot key): {missed}")

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote1031_1118"] = text
    else:
        print("NOTE MISS", key)

note("Everything Is Mine (EIM)",
 f"Run 1031 (blok {BLOCK}, interval ~28,2 mnt vs run 1001): totalMinted 663->678 (+15, 0,531/mnt vs rate 1001 0,418 = 1,27x) -> velocity GAGAL (<20 token dan rasio <1,5x). Free% UNVERIFIED (semua free view revert), umur UNVERIFIED, X unverified, slot user UNVERIFIED. Bukan kandidat, bukan strong lead. Tetap early-lead-reported-2026-11-17.")
note("SPARKS",
 f"Run 1031 (blok {BLOCK}): totalSupply 1169->1173 (+4, 0,142/mnt vs rate 1001 0,064 = 2,21x) -> velocity GAGAL (<20 token). Free% UNVERIFIED, umur UNVERIFIED, slot user UNVERIFIED. Bukan kandidat/strong lead. Tetap watchlist-only.")
note("Mine Card",
 f"Run 1031 (blok {BLOCK}): totalSupply 1242->1254 (+12, 0,425/mnt vs rate 1001 0,386 = 1,10x) -> velocity GAGAL (<20 token dan rasio <1,5x). Free% UNVERIFIED. Bukan kandidat. DIAM.")
note("STOCK AGENT",
 f"Run 1031 (blok {BLOCK}): totalSupply 645->657 (+12, 0,425/mnt vs rate 1001 0,129 = 3,30x) -> velocity GAGAL (<20 token, meski rasio >1,5x). Free inferred 657/1111 = 59,1% (freeLeft 454) - di atas 50% kandidat TAPI di bawah 70% strong lead; umur UNVERIFIED; website gate BELUM terverifikasi. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat, bukan strong lead. Tetap early-lead-reported-2026-11-18-0031.")
note("Agent Bubble",
 f"Run 1031 (blok {BLOCK}): freeMinted 1888/2222 = 85,0% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply flat 2033, balanceOf(user)=0. Tetap watchlist-only.")
note("Lumenhold",
 f"Run 1031 (blok {BLOCK}): freeClaimed 1252/1500 = 83,5% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply flat 1257. Tetap watchlist-only-age-unverified.")
note("Matrix Agents",
 f"Run 1031 (blok {BLOCK}): freeMinted 614/1000 = 61,4% (<70%), totalSupply 608->611 (+3) -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat. Tetap early-lead-reported-2026-11-15.")
note("AGCLUB",
 f"Run 1031 (blok {BLOCK}): freeMinted 527/888 = 59,3% (<70%), totalMinted flat 527 -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat. Tetap watchlist-only.")
note("PunchCard",
 f"Run 1031 (blok {BLOCK}): totalSupply 1330->1331 (+1, 0,035/mnt vs rate 1001 0,064 = 0,55x) -> velocity GAGAL. freeMinted 1309/5555 = 23,6%. Bukan kandidat. DIAM.")
note("ADRAW",
 f"Run 1031 (blok {BLOCK}): freeMinted 313 flat, totalSupply view revert (bukan 0). Tetap watchlist-only-age-unverified. DIAM.")
note("HIVE Agents",
 f"Run 1031 (blok {BLOCK}): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin",
 f"Run 1031 (blok {BLOCK}): totalSupply 2620 FLAT, freeClaimed 2614/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM.")
note("THE WALL",
 "Run 1031: THE WALL tidak muncul di front page Boltbook run ini (rotasi front page, EN hanya 3 alamat); nilai terakhir 5.389/20.000 = 26,9% (run 1001) dipertahankan. Tetap watchlist-only.")
note("CAT402",
 f"Run 1031 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON",
 f"Run 1031 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")
note("JADE",
 f"Run 1031 (blok {BLOCK}): cost user 0,0005 BNB (BUKAN gratis), freeClaimed 188, totalSupply flat 191. DIAM.")

snap["contracts"].setdefault("bsccat", {})["runNote1031_1118"] = (
 f"Run 1031: freeMinted 524 FLAT (blok {BLOCK}); pool views lain revert. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1031_1118"] = (
 f"Run 1031: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1031"] = (f"Run 1031 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
                     "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1031"] = (f"Run 1031 (blok {BLOCK}): openedAt 0, freeSharesLeft 623 FLAT, "
                     "freeClaimed 377 FLAT - pool BELUM dibuka, tanpa perubahan status. DIAM.")
ac = snap["contracts"]["ARKT-claim-62a7"]
ac["runNote1031"] = "Run 1031: totalSupply 3 flat, totalMinted 3, hasClaimed(user) 0 - tanpa perubahan. DIAM."

snap["runNote1031_1118"] = (
 "Run 1031 (blok re-read %d, interval ~28,2 mnt vs 1001): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead. "
 "Velocity: TIDAK ADA yang lolos (mint terbanyak EIM +15 <20; Mine Card +12; STOCK +12 (3,30x tapi <20); SPARKS +4 (2,21x tapi <20)). "
 "AgentBubble 85,0%% + Lumenhold 83,5%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. "
 "STOCK free inferred 59,1%% (<70%%). CAT402 sold out (100/100); DRAGON pool habis; pepe pool habis. "
 "Boltbook: 1 lead baru dicek on-chain (LMINER 0xc726, post bdnoman.ai) - Sourcify NOT verified (match null), tanpa registry bytes/free view/quote -> BUKAN agent-shaped, log only, tidak masuk snapshot. "
 "Sourcify feed top TIDAK BERUBAH vs 1001 (verifiedAt 03:23:19Z, 0xBe98/0x0E44 sudah dicek hot-leg 1024: S1/S2 false); kontrak baru pasca-fetch 0x00fE (03:34:53Z, 3 fns USDT/checkZeroBalance/drainZeroAddress) -> S1/S2 false, checked-not-sale-shape. "
 "Sweep EN+ZH: 0 baru (Oathbots age-excluded, Agentic Gangster free sold out, STAMP PASS/RIGBYPASS/AGENT COSMOS >24 jam, UFO/NEBULA 10 Nov, BN Agent Trials/Xuanwu Seed 25 Okt). "
 "Odaily 0 hit; PANews hanya shell JS (4.190 byte, tidak bisa dinilai isinya). "
 "binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 623 FLAT). DIAM." % BLOCK)
snap["checkedNotSaleShape1031_1118"] = (
 "Sourcify feed top TIDAK BERUBAH vs 1001 (verifiedAt 2026-11-18T03:23:19Z, top 0xBe989731AF03a4A3D668400b38DAE523f44ECa2F) - 0 kontrak baru dalam fetch run ini; "
 "0xBe98 + 0x0E44 sudah dicek hot-leg 1024 (S1=False S2=False). Kontrak baru pasca-fetch 0x00fE3CCD1d08d135FB35B5bFD6F38581e37bDa4c (verifiedAt 2026-11-18T03:34:53Z, 3 fns: USDT/checkZeroBalance/drainZeroAddress, "
 "tanpa mint/quote/free view/agent ref) -> S1=False S2=False -> checked-not-sale-shape.")
snap["boltbook_new_1031"] = (
 "Boltbook EN+ZH (44.638/43.238 byte, HTTP 200): EN 3 alamat, ZH 4 alamat (front page ROTASI - jauh lebih sedikit dari 10 alamat run 1001). Baru vs 1001: LMINER (LODE Miner) 0xc726a15534acd29ed2f06b47d7f19eb1fa015f62 "
 "(ZH only, post bdnoman.ai ~4 mnt lalu: minted #856 free, 4.444 LODE miners, mint(uint256), free lane mint(1) 0 BNB) - dicek on-chain: Sourcify NOT verified (match null), ABI kosong (n_fns 0), "
 "registry bytes False, semua free view/quote revert; totalMinted 856 + MAX_SUPPLY 4444 cocok dengan post TAPI free shape + agent-shape TIDAK terverifikasi -> BUKAN agent-shaped, log only, tidak masuk snapshot, tidak dilaporkan. "
 "Sudah di snapshot: LumenFindings 0x4158 (FIND exp42 burst 102->117 dalam 16 mnt per teks post; exp41 sealed 176/300 carried), BoltRewards 0x8269 (infra), BOLT 0xBbDd (non-lead). "
 "THE WALL tidak muncul di front page run ini (rotasi).")
snap["last_run_wib"] = NOW
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1031_scan"] = ("Run 2026-11-18 10:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 1,4 dtk, head 134240207); "
                        "401 auth-wide, gagal total ke-53 berturut-turut main job. Watermark TETAP 134086385; gap ~153.870 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
