#!/usr/bin/env python3
"""Merge run 2026-11-18 10:01 WIB re-read into onchain-snapshot.json (lean merge).
Fixes the 0931-merge name mismatch: PLAN names (EIM, Matrix, AgentBubble) are
resolved to snapshot entries by ADDRESS, not by FIELDS key. Velocity baseline is
the 0931 REREAD (authoritative last read), NOT the snapshot's stored supply:
the 0931 merge never wrote EIM totalMinted (630 stale vs 0931 read 650) because
its FIELDS key 'Everything Is Mine (EIM)' did not match the PLAN name 'EIM'.
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1001-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-0931-reread.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~10:01 WIB"
BLOCK = reread["block"]
PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")

addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k

# 0931 rates (per 0931 run log) for the movers; others fall back to snapshot stored rate.
RATE0931 = {"SPARKS": 1.436, "EIM": 0.684, "STOCK AGENT": 0.581, "Mine Card": 0.616,
            "PunchCard": 0.137, "Kitebots": 0.0153, "RaceAgents": 0.0301,
            "AgentEcho": None, "CPASS": 0.0, "Matrix": 0.0, "AgentBubble": 0.0301}

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
    # velocity vs 0931 reread baseline
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
        prev_rate = RATE0931.get(name)
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
        snap["contracts"][key]["runNote1001_1118"] = text
    else:
        print("NOTE MISS", key)

note("Everything Is Mine (EIM)",
 f"Run 1001 (blok {BLOCK}, interval ~31,1 mnt vs run 0931): totalMinted 650->663 (+13, 0,418/mnt vs rate 0931 0,684 = 0,61x) -> velocity GAGAL (<20 token dan rasio <1,5x). KOREKSI baseline: snapshot menyimpan 630 (stale - merge 0931 tidak menulis totalMinted karena FIELDS key tidak cocok dengan PLAN name 'EIM'); baseline benar = reread 0931 (650). Free% UNVERIFIED (semua free view revert), umur UNVERIFIED, X unverified, slot user UNVERIFIED. Bukan kandidat, bukan strong lead. Tetap early-lead-reported-2026-11-17.")
note("SPARKS",
 f"Run 1001 (blok {BLOCK}): totalSupply 1167->1169 (+2, 0,064/mnt vs rate 0931 1,436 = 0,04x) -> velocity GAGAL (<20). Free% UNVERIFIED, umur UNVERIFIED, slot user UNVERIFIED. Bukan kandidat/strong lead. Tetap watchlist-only.")
note("Mine Card",
 f"Run 1001 (blok {BLOCK}): totalSupply 1230->1242 (+12, 0,386/mnt vs rate 0931 0,616 = 0,63x) -> velocity GAGAL (<20 dan rasio <1,5x). Free% UNVERIFIED. Bukan kandidat. DIAM.")
note("STOCK AGENT",
 f"Run 1001 (blok {BLOCK}): totalSupply 641->645 (+4, 0,129/mnt vs rate 0931 0,581 = 0,22x) -> velocity GAGAL (<20 dan rasio <1,5x). Free inferred 645/1111 = 58,0% (freeLeft 466) - di atas 50% kandidat TAPI di bawah 70% strong lead; umur UNVERIFIED; website gate BELUM terverifikasi. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat, bukan strong lead. Tetap early-lead-reported-2026-11-18-0031.")
note("Agent Bubble",
 f"Run 1001 (blok {BLOCK}): freeMinted 1888/2222 = 85,0% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply flat 2033, balanceOf(user)=0. Tetap watchlist-only.")
note("Lumenhold",
 f"Run 1001 (blok {BLOCK}): freeClaimed 1252/1500 = 83,5% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply flat 1257. Tetap watchlist-only-age-unverified.")
note("Matrix Agents",
 f"Run 1001 (blok {BLOCK}): freeMinted 611/1000 = 61,1% (<70%), totalSupply 608 flat vs reread 0931 (608) -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat. Tetap early-lead-reported-2026-11-15.")
note("AGCLUB",
 f"Run 1001 (blok {BLOCK}): freeMinted 527/888 = 59,3% (<70%), totalMinted flat 527 -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat. Tetap watchlist-only.")
note("PunchCard",
 f"Run 1001 (blok {BLOCK}): totalSupply 1328->1330 (+2, 0,064/mnt vs rate 0931 0,137 = 0,47x) -> velocity GAGAL. freeMinted 1308/5555 = 23,5%. Bukan kandidat. DIAM.")
note("ADRAW",
 f"Run 1001 (blok {BLOCK}): freeMinted 313 flat, totalSupply view revert (bukan 0). Tetap watchlist-only-age-unverified. DIAM.")
note("HIVE Agents",
 f"Run 1001 (blok {BLOCK}): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin",
 f"Run 1001 (blok {BLOCK}): totalSupply 2620 FLAT, freeClaimed 2614/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM.")
note("THE WALL",
 "Run 1001: Boltbook recheck (teks post, BUKAN baca on-chain run ini): 5.389/20.000 = 26,9% free - masih <50%, tanpa promosi. Tetap watchlist-only.")
note("CAT402",
 f"Run 1001 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON",
 f"Run 1001 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")
note("JADE",
 f"Run 1001 (blok {BLOCK}): cost user 0,0005 BNB (BUKAN gratis), freeClaimed 188, totalSupply flat 191. DIAM.")

snap["contracts"].setdefault("bsccat", {})["runNote1001_1118"] = (
 f"Run 1001: freeMinted 523->524 (blok {BLOCK}); pool views lain revert. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1001_1118"] = (
 f"Run 1001: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1001"] = (f"Run 1001 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
                     "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1001"] = (f"Run 1001 (blok {BLOCK}): openedAt 0, freeSharesLeft 624->623, "
                     "freeClaimed 376->377 - pool BELUM dibuka, tanpa perubahan status. DIAM.")
ac = snap["contracts"]["ARKT-claim-62a7"]
ac["runNote1001"] = "Run 1001: totalSupply 3 flat, totalMinted 3, hasClaimed(user) 0 - tanpa perubahan. DIAM."

snap["runNote1001_1118"] = (
 "Run 1001 (blok re-read %d, interval ~31,1 mnt vs 0931): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead. "
 "Velocity: TIDAK ADA yang lolos (mint terbanyak EIM +13 <20; Mine Card +12; STOCK +4; SPARKS +2). "
 "AgentBubble 85,0%% + Lumenhold 83,5%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. "
 "STOCK free inferred 58,0%% (<70%%). CAT402 sold out (100/100); DRAGON pool habis; pepe pool habis. "
 "Boltbook: 2 lead baru dicek on-chain (MechaWar 0x94bd, Vitaliq Scans 0xad0d) - keduanya BUKAN agent-shaped (tanpa registry/AgentGate/free view) -> log only, tidak masuk snapshot. "
 "Sourcify baru 0xB4fb: S1/S2 false -> checked-not-sale-shape. "
 "binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 623). DIAM." % BLOCK)
snap["checkedNotSaleShape1001_1118"] = (
 "Sourcify feed top BERUBAH vs 0931 (verifiedAt 2026-11-18T03:03:02Z): 1 kontrak baru 0xB4fb7f305A1903b83DDfb28c2BDc021534661cB1 - "
 "13 fns, tanpa mint/quote/free view/agent ref, totalMinted 1 -> S1=False S2=False -> checked-not-sale-shape.")
snap["boltbook_new_1001"] = (
 "Boltbook EN+ZH (43.979/42.819 byte, HTTP 200): 10 alamat distinct, sama EN=ZH. Baru vs 0931: MechaWar 0x94bd (totalMinted 211/7.777, tanpa free view/registry/AgentGate - BUKAN agent-shaped, log only; hot-leg sudah melihatnya, tidak melaporkannya), "
 "Vitaliq Scans 0xad0d (quiz-gated free mint, Sourcify verified 53 fns, tanpa quote/free view/agent ref/registry bytes - BUKAN agent-shaped, log only). "
 "0x79b5 + 0xe8db = hash transaksi (bukan kontrak); 0x0B2b = kontrak sUSDai Arbitrum (bukan free mint BSC). "
 "Sudah di snapshot: ME24 0x391a (Gear Machine 464/3.362 = 13,8%), LumenFindings 0x4158 (FIND exp41 sealed 176/300), THE WALL 0xa804 (5.389/20.000 = 26,9%), BoltRewards 0x8269 (infra), BOLT 0xBbDd (non-lead).")
snap["last_run_wib"] = NOW
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1001_scan"] = ("Run 2026-11-18 10:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 1,6 dtk, head 134236435); "
                        "401 auth-wide, gagal total ke-52 berturut-turut main job. Watermark TETAP 134086385; gap ~150.050 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
