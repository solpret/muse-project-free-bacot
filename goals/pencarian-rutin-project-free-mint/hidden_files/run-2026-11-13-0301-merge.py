#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 03:01 WIB.
Address-exact matching only. Updates numeric fields + lastReadWib.
OUTY: minted/freeSold tetap 2/1500, FREE_FEE 0.0001 BNB TETAP (NOT gas-only).
No new feed/Boltbook contracts: all 32 shape targets already in hot-leg-seen
(legs seen-parse failed transiently mid-write; cross-checked by text grep).
0x9625 early_shape=true like run 0201 - already checked-not-agent-shaped, NOT a lead.
DragonAgent early_shape=true - already in snapshot as early lead, NOT new.
Backup: /tmp/onchain-snapshot-2026-11-13-0301.bak (taken before run)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-13 ~03:10 WIB"
BLOCK = 133220567
shutil.copy(BASE + "onchain-snapshot.json", "/tmp/onchain-snapshot-2026-11-13-0301.bak")
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
def by_addr(addr, sec="contracts"):
    for k, v in snap.get(sec, {}).items():
        if isinstance(v, dict) and (v.get("address") or v.get("sale") or "").lower() == addr.lower():
            return k, v
    return None, None
def upd(addr, fields, sec="contracts"):
    k, v = by_addr(addr, sec)
    if v is None:
        print("WARN not in snapshot:", addr); return None
    v.update(fields); v["lastReadWib"] = NOW
    return k
INTERVAL_MIN = 28.2  # block delta 133220567-133216806 = 3761 blocks x ~0.45 dtk
def vel(old_total, new_total, prev_rate):
    if old_total is None or new_total is None: return {}
    minted = new_total - old_total
    rate = round(minted / INTERVAL_MIN, 3)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return {"previousTotalSupply": old_total, "mintedInInterval": minted,
            "intervalMinutes": INTERVAL_MIN, "currentRatePerMin": rate,
            "previousRatePerMin": prev_rate, "velocityRatio": ratio,
            "velocityLegPasses": bool(minted >= 20 and prev_rate and rate >= 1.5 * prev_rate)}

# --- SolNFT: 306 -> 307 (+1, <20) velocity FAIL; 307/333 = 92.2% ---
k, v = by_addr("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
    {"totalMinted": 307, "freeMinted": 307, "FREE_CAP": 333, "mintOpen": 1,
     "freeClaimed_user": 0, "balanceOf_user": 0,
     **vel(306, 307, prev_rate)})
# --- Agentx: 337 -> 337 (flat) velocity FAIL; 337/1111 = 30.3% ---
k, v = by_addr("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
    {"totalMinted": 337, "freeMinted": 337, "FREE_CAP": 1111, "MAX_SUPPLY": 2222,
     "mintOpen": 1, "mintOpensAt": 1794499865, "price": 5000000000000000,
     "freeClaimed_user": 0, "balanceOf_user": 0, "holdsAgentId_user": 1,
     "mintsBy_user": 0, "name": "Agentx", "symbol": "AGENTX", "nextTokenId": 338,
     **vel(337, 337, prev_rate)})
# --- AgentLabs: 846 -> 939 (+93, rate 3.298 vs prev 1.141 = 2.89x) velocity PASSES ---
# Still early - DIAM: NO free cap (free % not measurable), so no strong-lead promotion.
# Experiment 1 unsealed, ends 1794528000 (07:00 WIB 13 Nov).
k, v = by_addr("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7",
    {"totalSpecimens": 939, "participants": 916, "experimentEnd": 1794528000,
     "priceFor_user": 0, "isSealed": 0, "balanceOf_user": 0,
     **vel(846, 939, prev_rate)})
# --- OUTY: tetap minted 2, freeSold 2/1500; FREE_FEE 0.0001 BNB (NOT gas-only) ---
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412",
    {"minted": 2, "freeSold": 2, "paidSold": 0, "FREE_SUPPLY": 1500,
     "PAID_CAP": 15000, "START": 1794510227, "FREE_END": 1794596627,
     "FREE_FEE": 100000000000000, "PRICE": 3000000000000000, "phase": 1,
     "freeOpen": 1, "paidOpen": 0, "freeQuotaOf_user": 1, "quotaOf_user": 10,
     "balanceOf_user": 0,
     "notFreeNote": "Run 0301 (blok 133220567): OUTY minted/freeSold tetap 2/1500. FREE_FEE()=100000000000000 wei = 0.0001 BNB TETAP - jalur 'free' berbayar, BUKAN gas-only, GAGAL kriteria (1) Free Bacot; bukan kandidat/lead, tidak di-preview/di-mint, tidak dilaporkan ke chat."})
# --- OBFG: 538 -> 546 (+8), 546/1230 = 44.4%; track-C lead gate-blocked - DIAM ---
# (OBFG has no structured snapshot entry - runNote only, pattern since 2101.)
# --- BC1B: freeCount 447 -> 448/3000 = 14.9% - DIAM ---
upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
    {"freeCount": 448, "FREE_CAP": 3000, "saleStart": 1794488398,
     "freeMinted_user": 0, "balanceOf_user": 0}, sec="track_c")
# --- LuckyCatch / MECHA / Steady ---
upd("0xD405C90079c594DA2456F5b37B4158A12f1382e5",
    {"totalSupply": 21, "agentFreeCount": 20, "paidSold": 1, "mintOpen": 1, "balanceOf_user": 0})
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
    {"totalMinted": 1874, "freeClaimed": 1873, "freeAvailable_user": 2, "balanceOf_user": 0})
k, v = by_addr("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
    {"totalSupply": 433, "freeClaimed": 433, "FREE_SUPPLY": 555, "mintOpen": 1,
     "freeUsed_user": 0, "balanceOf_user": 0, **vel(421, 433, prev_rate)})
# --- other re-reads ---
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", {"totalSupply": 962, "balanceOf_user": 0})
upd("0x11986f3DF799a28bB97921F49406a7197b1d34d2", {"totalSupply": 93, "mintOpen": 1, "balanceOf_user": 0})
upd("0x467696af8c2206B977B24081445104632dc1D459",
    {"totalMinted": 932, "freeMinted": 932, "FREE_SUPPLY": 1200, "balanceOf_user": 1, "freeAvailable_user": 0})
upd("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2",
    {"totalMinted": 301, "freeMinted": 300, "FREE_SUPPLY": 300, "balanceOf_user": 1})
upd("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
    {"totalSupply": 1263, "FREE_SUPPLY": 1000, "MAX_SUPPLY": 10000, "balanceOf_user": 1})
upd("0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
    {"totalSupply": 2529, "freeClaimed": 2523, "FREE_SUPPLY": 7777, "mintOpen": 1, "balanceOf_user": 1})
upd("0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC",
    {"totalSupply": 717, "freeClaimed": 712, "FREE_SUPPLY": 712, "mintOpen": 1, "balanceOf_user": 1})
# retries
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810", {"totalSupply": 924, "freeMinted": 874, "mintOpen": 1, "balanceOf_user": 0})
upd("0x7ef49be2a9ade4fae0888f4065c8f122a146f6d0", {"totalSupply": 4900, "totalMinted": 4900, "balanceOf_user": 0})
upd("0xb8a990e16fd66d398cc27d0c8bdb11524bc0dc8e",
    {"totalMinted": 292, "freeMinted": 292, "FREE_SUPPLY": 1111, "freeClaimed_user": 0, "balanceOf_user": 0})
upd("0xad0d8ac3d61fc8ab397b7136c69fcbf1281a4998",
    {"totalSupply": 563, "freeClaimed": 559, "FREE_SUPPLY": 888, "mintOpen": 1, "balanceOf_user": 0})
upd("0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69", {"totalSupply": 5294, "mintOpen": 1, "balanceOf_user": 0})
upd("0x486d0947caa3d70c19e38f6c789489d39291e9e7", {"totalSupply": 3000, "mintOpen": 1, "balanceOf_user": 0})
upd("0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4",
    {"totalSupply": 327, "totalMinted": 327, "freeMinted": 325, "FREE_SUPPLY": 325, "mintOpen": 1, "freeAvailable_user": 0, "balanceOf_user": 0})
upd("0x8aa9d6a09caf475593852e681b58b26dc94edd56", {"totalSupply": 4901, "totalMinted": 4901, "balanceOf_user": 0})
upd("0x6c17af4fac529e5679686e121a75e85b1063cd45", {"totalSupply": 4900, "totalMinted": 4900, "balanceOf_user": 0})
# --- track_c: BHTB / AgentGrid ---
upd("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
    {"freeUsed": 247, "FREE_QUOTA": 555, "mintEnd": 1794570281, "freeClaimed_user": 0, "balanceOf_user": 0}, sec="track_c")
upd("0x651302C0043040D48EaAF85605E12F0549aD6D89",
    {"FREE_SHARES": 500, "freeUsed": 21}, sec="track_c")
# --- binanceai claim (track B): unchanged, refund/failed ---
b = snap.get("binanceai_claim", {})
b.update({"launched": 0, "failed": 1, "isRefundPhase": 1, "tokenClaimed_user": 0,
          "tokenBalance_user": 0, "lastReadBlock": BLOCK, "lastReadWib": NOW,
          "runNote0301_1113": f"Run 0301 (blok {BLOCK}): launched()=0 TETAP, failed()=1, isRefundPhase()=1, tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 - tetap refund/failed, tidak dilaporkan ulang."})
snap["binanceai_claim"] = b
# --- run notes ---
snap["runNote0301_1113"] = ("Run 0301 (blok 133220567, verify 89,2 dtk, interval ~28,2 mnt vs run 0231): "
  "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. "
  "OUTY minted/freeSold tetap 2/1500, FREE_FEE 0.0001 BNB TETAP - bukan gas-only, dicatat saja. "
  "SolNFT 307/333 = 92,2% (+1) tetap strong-lead-gate-blocked - DIAM (26 slot tersisa). "
  "Agentx 337/1111 = 30,3% (flat) velocity GAGAL - tetap early, DIAM. "
  "AgentLabs 939 spesimen (+93, rate 3,298 vs prev 1,141 = 2,89x) velocity LOLOS, tapi tanpa free cap -> tidak bisa jadi strong lead; belum seal (seal 07:00 WIB) - DIAM. "
  "Steady 433/555 = 78,0% (+12, <20) velocity GAGAL, umur MASIH UNVERIFIED (sweep run ini 0 hasil baru soal Steady) -> tidak promosi - DIAM. "
  "OBFG 546/1230 = 44,4% (+8) tetap track-C lead gate-blocked - DIAM. BC1B 448/3000 - DIAM. "
  "LuckyCatch 21 tetap (deadline umur 04:06:03 WIB 13 Nov). MECHA 1874 tetap, umur unverified. "
  "Scan leg fast-fail (Ankr 401); watermark tetap 132512564. Feed 20 + Boltbook ZH 12 alamat, 0 baru (semua sudah di hot-leg-seen; legs seen-parse gagal sesaat saat hot leg menulis file, cross-check via text grep); "
  "shape-check 32 target: 11 OK (0 S1/S2; early_shape=true hanya 0x9625 - sudah checked-not-agent-shaped run 0201 - dan DragonAgent - sudah early di snapshot), 21 gagal transport Sourcify (RemoteDisconnected/IncompleteRead) - bukan bukti bukan-agent-shaped, hot leg retry. "
  "Boltbook EN GAGAL (urllib + curl), hanya ZH terbaca (42.339 byte, 12 alamat). "
  "Binanceai tetap refund/failed. Odaily + PANews 0 item Agent ID. Sweep: semua dikenal/excluded (Oathbots, Agentic Gangster, RIGBYPASS, MOLT, AGENT MAO, AGENT COSMOS, Pixel Fox, Coracle, First-Dollar Grove).")
snap["runNote0301_1113_scan"] = ("Run 0301 route 4: SCAN FAST-FAIL - pre-flight ankr_getLogs HTTP 401 Unauthorized. "
  "Watermark TIDAK dimajukan (tetap 132512564); gap ke head terus tumbuh (head 133220567 saat run). Route 5c dilewati (tanpa output scan baru). Ankr outage sejak 9 Nov.")
snap["runNote0301_1113_obfg"] = ("Run 0301 (blok 133220567): OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 freeMinted 538->546/1230 (44,4%), "
  "totalSupply 546, saleStart 1794488476 (20:01:16 WIB 12 Nov), saleOpen=1, freeAvailable(user)=1. "
  "Tetap track-C lead gate-blocked - DIAM.")
snap["runNote0301_1113_binanceai"] = ("Run 0301 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, "
  "tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 (blok 133220567) - tetap refund/failed, tidak dilaporkan ulang.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = "Run 0301: 0 kandidat/strong/early/track-C baru; OUTY freeSold 2/1500, FREE_FEE 0.0001 BNB tetap (bukan gas-only, dicatat saja); AgentLabs velocity lolos (+93) tapi tanpa free cap (tetap early); scan fast-fail Ankr 401; Boltbook EN gagal, hanya ZH."
snap["timestamp_wib"] = NOW
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK; contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]))
