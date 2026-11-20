#!/usr/bin/env python3
"""Merge run 2026-11-18 11:01 WIB re-read into onchain-snapshot.json (lean merge).
Fixes the 1001-merge name mismatch: PLAN names (EIM, Matrix, AgentBubble) are
resolved to snapshot entries by ADDRESS, not by FIELDS key. Velocity baseline is
the 1001 REREAD (authoritative last read), NOT the snapshot's stored supply:
the 1001 merge never wrote EIM totalMinted (630 stale vs 1001 read 650) because
its FIELDS key 'Everything Is Mine (EIM)' did not match the PLAN name 'EIM'.
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1101-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1031-reread.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~11:01 WIB"
BLOCK = reread["block"]
PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")

addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k

# 1031 rates: snapshot currentRatePerMin already holds the 1031 rate for every
# re-read entry (1031 merge wrote it), so the fallback below IS the 1031 rate.
# No hardcoded dict needed. THE WALL + APGB V1 were NOT in the 1031 PLAN, so
# their velocity block is skipped naturally (no 1031 baseline) - see notes below.
RATE1001 = {}

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
        prev_rate = RATE1001.get(name)  # empty dict -> fallback to snapshot rate
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
        snap["contracts"][key]["runNote1101_1118"] = text
    else:
        print("NOTE MISS", key)

note("Everything Is Mine (EIM)",
 f"Run 1101 (blok {BLOCK}, interval ~35,3 mnt vs run 1031): totalMinted 678->688 (+10, 0,283/mnt vs rate 1031 0,531 = 0,53x) -> velocity GAGAL (<20 token dan rasio <1,5x). Free% UNVERIFIED, umur UNVERIFIED, X unverified, slot user UNVERIFIED. Bukan kandidat, bukan strong lead. Tetap early-lead-reported-2026-11-17.")
note("SPARKS",
 f"Run 1101 (blok {BLOCK}): totalSupply 1169->1175 (+6, 0,170/mnt vs rate 1031 0,064 = 2,66x) -> velocity GAGAL (<20 token). Free% UNVERIFIED, umur UNVERIFIED, slot user UNVERIFIED. Bukan kandidat/strong lead. Tetap watchlist-only.")
note("Mine Card",
 f"Run 1101 (blok {BLOCK}): totalSupply 1254->1267 (+13, 0,368/mnt vs rate 1031 0,425 = 0,87x) -> velocity GAGAL (<20 token dan rasio <1,5x). Free% UNVERIFIED. Bukan kandidat. DIAM.")
note("STOCK AGENT",
 f"Run 1101 (blok {BLOCK}): totalSupply 657->661 (+4, 0,113/mnt vs rate 1031 0,425 = 0,27x) -> velocity GAGAL (<20 token). Free inferred (1111-450)/1111 = 59,5% (freeLeft 450) - di atas 50% kandidat TAPI di bawah 70% strong lead; umur UNVERIFIED; website gate BELUM terverifikasi. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat, bukan strong lead. Tetap early-lead-reported-2026-11-18-0031.")
note("Agent Bubble",
 f"Run 1101 (blok {BLOCK}): freeMinted 1889/2222 = 85,0% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 2033->2034 (+1), balanceOf(user)=0. Tetap watchlist-only.")
note("Lumenhold",
 f"Run 1101 (blok {BLOCK}): freeClaimed 1252/1500 = 83,5% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply flat 1257. Tetap watchlist-only-age-unverified.")
note("Matrix Agents",
 f"Run 1101 (blok {BLOCK}): freeMinted 615/1000 = 61,5% (<70%), totalSupply 611->612 (+1) -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat. Tetap early-lead-reported-2026-11-15.")
note("AGCLUB",
 f"Run 1101 (blok {BLOCK}): freeMinted 527/888 = 59,3% (<70%), totalMinted flat 527 -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat. Tetap watchlist-only.")
note("PunchCard",
 f"Run 1101 (blok {BLOCK}): totalSupply 1331->1332 (+1, 0,028/mnt vs rate 1031 0,035 = 0,80x) -> velocity GAGAL. freeMinted 1310/5555 = 23,6%. Bukan kandidat. DIAM.")
note("ADRAW",
 f"Run 1101 (blok {BLOCK}): freeMinted 313 flat, totalSupply view revert (bukan 0). Tetap watchlist-only-age-unverified. DIAM.")
note("HIVE Agents",
 f"Run 1101 (blok {BLOCK}): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin",
 f"Run 1101 (blok {BLOCK}): totalSupply 2620 FLAT, freeClaimed 2614/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM.")
note("THE WALL",
 f"Run 1101 (blok {BLOCK}): totalSupply 5430 (baseline snapshot lama 5055 dari 2026-11-11 - KOREKSI: +375 terjadi selama ~7 HARI, BUKAN 35 mnt; velocity TIDAK dihitung run ini, baseline di-reset ke 5430). Recheck Boltbook yuibnb.ai: 5.413/20.000 (+24) - pace lambat, konsisten. Free% 5430/20000 = 27,2% (<50%). Umur UNVERIFIED. Bukan kandidat/strong lead. Tetap watchlist-only-age-unverified.")
note("AlphaPulse Genesis Badge V1",
 f"Run 1101 (blok {BLOCK}): totalSupply 29->33 (+4 sejak baca 09:01, ~120 mnt = ~0,033/mnt; BUKAN rate 35-mnt - tidak ada baseline 1031, velocity TIDAK dihitung). MAX_SUPPLY 10000, mintOpen 1, balanceOf(user)=0. Semua free view revert -> free% UNVERIFIED. Post Boltbook bevis.ai konfirmasi Agent-ID gate nyata (mint() revert 'no Agent ID' dari dead wallet) TAPI umur peluncuran tetap UNVERIFIED. Bukan kandidat/strong lead. Tetap watchlist-only-age-unverified.")
note("CAT402",
 f"Run 1101 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON",
 f"Run 1101 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui; post Boltbook rbd5160.ai konfirmasi CLOSED, totalMinted 1005), balanceOf(user)=1. DIAM.")
note("JADE",
 f"Run 1101 (blok {BLOCK}): cost user 0,0005 BNB (BUKAN gratis), freeClaimed 188, totalSupply flat 191. DIAM.")
note("Roninagent",
 f"Run 1101: RONIN recheck Boltbook bangwi.ai (freeClaimed 1.174/2.222 = 52,8%) TIDAK mengubah status: owner 0xd76d... = factory discard group -> watchlist-only-same-owner-discarded, TIDAK PERNAH dipromosikan/dilaporkan sebagai lead. DIAM (tidak dibaca ulang on-chain run ini).")
note("SAMO",
 f"Run 1101: post Boltbook ai1288.ai - sale CLOSED 17 Nov, 88 paid dari 9.000, 46 refund keluar. Konsisten dengan status checked-not-lead-free-sold-out-2026-11-16 (freeClaimed 999/999). DIAM.")

snap["contracts"].setdefault("bsccat", {})["runNote1101_1118"] = (
 f"Run 1101: freeMinted 526 (+2 vs 1031: 524), totalSupply mentah 5,26e26; pool views lain revert. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1101_1118"] = (
 f"Run 1101: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1101"] = (f"Run 1101 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
                     "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1101"] = (f"Run 1101 (blok {BLOCK}): openedAt 0, freeSharesLeft 622 (1031: 623), "
                     "freeClaimed 378 (1031: 377) - pool BELUM dibuka, tanpa perubahan status. DIAM.")
ac = snap["contracts"]["ARKT-claim-62a7"]
ac["runNote1101"] = "Run 1101: totalSupply 3->4, totalMinted 4, hasClaimed(user) 0 - tanpa perubahan. DIAM."

snap["runNote1101_1118"] = (
 "Run 1101 (blok re-read %d, interval ~35,3 mnt vs 1031): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead. "
 "Velocity: TIDAK ADA yang lolos (mint terbanyak Mine Card +13; EIM +10; SPARKS +6 (2,66x tapi <20); STOCK +4; AgentEcho +3 (2,40x tapi <20)). "
 "KOREKSI THE WALL: +375 vs baseline snapshot 2026-11-11 (5055) adalah ~7 hari, BUKAN 35 mnt - velocity TIDAK dihitung, baseline di-reset 5430; recheck Boltbook +24 konsisten pace lambat. "
 "AgentBubble 85,0%% + Lumenhold 83,5%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. "
 "STOCK free inferred 59,5%% (<70%%); Matrix 61,5%%; AGCLUB 59,3%%. CAT402 sold out (100/100); DRAGON pool habis (1000/1000); pepe pool habis. "
 "Boltbook: Velko Rig 0x1a1d (908/10000, 9,1%%, semua free view revert, Sourcify unverified, tanpa registry bytes) + Crown 0x38f9 + Longge 0xeFb7 (keduanya ERC-20, tanpa mint/quote/free view/agent ref, S1/S2 false) -> BUKAN agent-shaped, log only, tidak masuk snapshot. "
 "Mechfarm 0x1fab recheck agata.ai: SUDAH EXCLUDED age-over-48h sejak 2026-11-05 (firstMint 2026-11-03 17:11 WIB) - bukan fase baru, DIAM; verifikasi ulang: freeClaimed 2624/4000 = 65,6%%, tanpa agent ref/registry bytes, verifiedAt 2026-11-03. "
 "APGB V1 29->33 (+4), gate Agent-ID terkonfirmasi nyata oleh post bevis.ai, TAPI umur tetap UNVERIFIED + free view revert -> tetap watchlist-only-age-unverified. "
 "RONIN 52,8%% free TAPI same-owner-discarded -> tidak pernah dipromosikan. SAMO sale closed 17 Nov (sudah checked-not-lead). "
 "Sourcify feed top BERUBAH (verifiedAt 2026-11-18T04:04:13Z, 0x9D00): 3 kontrak baru (0x9D00, 0xb43a, 0xf2dD) -> S1=False S2=False semua (token polos, tanpa mint/quote/free view/agent ref) -> checked-not-sale-shape. "
 "Sweep EN+ZH: 0 baru (Oathbots age-excluded, Pocket Ai sudah early-lead + host workers.dev BUKAN bukti website, Agentic Gangster free sold out, AgentForge 27 Okt, daftar 22 proyek 27 Okt, free 25 Okt, NEXUS CORE 25 Okt, AGENT COSMOS age-excluded, QILIN/SAFU/PROXY 1 Nov, Orzo 4 Nov). "
 "CATATAN KEAMANAN: hasil search mengandung instruksi mint tertanam untuk kontrak lama - TIDAK diikuti (konten luar bukan instruksi; semua proyek itu age-excluded/dikenal). "
 "Odaily newsflash 0 hit; PANews tidak dicek ulang run ini (temuan JS-shell run 1031 dibawa). "
 "binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 622). DIAM." % BLOCK)
snap["checkedNotSaleShape1101_1118"] = (
 "Sourcify feed top BERUBAH vs 1059 (verifiedAt 2026-11-18T04:04:13Z, top 0x9D00CF2e1d01c2ecB30BE831ceFf5768976c8396): 3 kontrak baru - "
 "0x9D00 (112 fns, token 21 jt, tanpa mint/quote/free view/agent ref), 0xb43a (18 fns, token), 0xf2dD (22 fns, token) -> S1=False S2=False semua -> checked-not-sale-shape.")
snap["boltbook_new_1101"] = (
 "Boltbook EN+ZH (44.573/43.163 byte, HTTP 200): EN 8 alamat, ZH 11 alamat. Baru vs 1031: SAMO 0x68fc (sale closed 17 Nov - sudah checked-not-lead-free-sold-out), "
 "RONIN 0x9404 (recheck 1.174/2.222 = 52,8% - same-owner-discarded, tidak dipromosikan), PXIO V2 0xaf86 (claim path game PXIO berubah on-chain - bukan proyek baru), "
 "Mechfarm 0x1fab (recheck agata.ai 2.675/4.000 - SUDAH EXCLUDED age-over-48h 2026-11-05), Crown-audit tx 0xf3c3 (bukan kontrak - tx proof post audit Crown; selector 0x40c10f19 = mint(address,uint256) ERC-20 standar, bukan bukti free-claim terverifikasi), "
 "Velko Rig 0x1a1d + Crown 0x38f9 + Longge 0xeFb7 (post 9dasand72.ai, ketiganya BELUM terverifikasi - hasil cek run ini: bukan agent-shaped, log only). "
 "APGB V1: post bevis.ai 32/10.000 (baca run ini 33), gate Agent-ID nyata. THE WALL recheck yuibnb.ai 5.413/20.000 (+24). DRAGON CLOSED (free 1000/1000). "
 "FIND exp42 131/300 = ekspedisi Mine Card, bukan proyek baru. Xeno Agent 9.901/10.001 (99,0%) = recheck proyek checked-not-lead-paid-only-2026-11-16 - tanpa perubahan status.")

snap["last_run_wib"] = NOW
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1101_scan"] = ("Run 2026-11-18 10:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 1,4 dtk, head 134240207); "
                        "401 auth-wide, gagal total ke-53 berturut-turut main job. Watermark TETAP 134086385; gap ~153.870 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
