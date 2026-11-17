#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 02:31 WIB.
Address-exact matching only. Updates numeric fields + lastReadWib.
OUTY: minted 1->2, freeSold 1->2, FREE_FEE still 0.0001 BNB = NOT gas-only
free -> recorded only, no report. NOTE: OUTY lives in `contracts`
(0201 merge bug used sec="track_c" - NOT repeated here).
No new feed/Boltbook contracts (feed_new [], boltbook_new []).
Backup: /tmp/onchain-snapshot-2026-11-13-0231.bak (taken before run)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-13 ~02:40 WIB"
BLOCK = 133216806
shutil.copy(BASE + "onchain-snapshot.json", "/tmp/onchain-snapshot-2026-11-13-0231.bak")
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
INTERVAL_MIN = 29.8  # block delta 133216806-133212827 = 3979 blocks x ~0.45 dtk
def vel(old_total, new_total, prev_rate):
    if old_total is None or new_total is None: return {}
    minted = new_total - old_total
    rate = round(minted / INTERVAL_MIN, 3)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return {"previousTotalSupply": old_total, "mintedInInterval": minted,
            "intervalMinutes": INTERVAL_MIN, "currentRatePerMin": rate,
            "previousRatePerMin": prev_rate, "velocityRatio": ratio,
            "velocityLegPasses": bool(minted >= 20 and prev_rate and rate >= 1.5 * prev_rate)}

# --- SolNFT: 303 -> 306 (+3, <20) velocity FAIL; 306/333 = 91.9% ---
k, v = by_addr("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
    {"totalMinted": 306, "freeMinted": 306, "FREE_CAP": 333, "mintOpen": 1,
     "freeClaimed_user": 0, "balanceOf_user": 0,
     **vel(303, 306, prev_rate)})
# --- Agentx: 323 -> 337 (+14, <20, rate 0.470 vs prev 0.709 = 0.66x) FAIL ---
# Still NOT a candidate: 337/1111 = 30.3% < 50%, X + website unverified. Early - DIAM.
k, v = by_addr("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
    {"totalMinted": 337, "freeMinted": 337, "FREE_CAP": 1111, "MAX_SUPPLY": 2222,
     "mintOpen": 1, "mintOpensAt": 1794499865, "price": 5000000000000000,
     "freeClaimed_user": 0, "balanceOf_user": 0, "holdsAgentId_user": 1,
     "mintsBy_user": 0, "name": "Agentx", "symbol": "AGENTX", "nextTokenId": 338,
     **vel(323, 337, prev_rate)})
# --- AgentLabs: 812 -> 846 (+34, rate 1.141 vs prev 0.674 = 1.69x) velocity PASSES ---
# Still early - DIAM: NO free cap (first specimen per wallet per experiment
# free; free % not measurable), so no strong-lead promotion possible.
k, v = by_addr("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7",
    {"totalSpecimens": 846, "participants": 824, "experimentEnd": 1794528000,
     "priceFor_user": 0, "isSealed": 0, "balanceOf_user": 0,
     **vel(812, 846, prev_rate)})
# --- OUTY: minted 1->2, freeSold 1->2; FREE_FEE still 0.0001 BNB (NOT gas-only) ---
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412",
    {"minted": 2, "freeSold": 2, "paidSold": 0, "FREE_SUPPLY": 1500,
     "PAID_CAP": 15000, "START": 1794510227, "FREE_END": 1794596627,
     "FREE_FEE": 100000000000000, "PRICE": 3000000000000000, "phase": 1,
     "freeOpen": 1, "paidOpen": 0, "freeQuotaOf_user": 1, "quotaOf_user": 10,
     "balanceOf_user": 0,
     "notFreeNote": "Run 0231 (blok 133216806): OUTY minted 1->2, freeSold 1->2/1500. FREE_FEE()=100000000000000 wei = 0.0001 BNB TETAP - jalur 'free' berbayar, BUKAN gas-only, GAGAL kriteria (1) Free Bacot; bukan kandidat/lead, tidak di-preview/di-mint, tidak dilaporkan ke chat."})
# --- OBFG: 519 -> 538 (+19), 538/1230 = 43.7%; track-C lead gate-blocked - DIAM ---
upd("0x5314071bba19943f58347ba5dec423e5032a6818",
    {"totalSupply": 538, "totalMinted": 538, "freeMinted": 538,
     "FREE_SUPPLY": 1230, "saleStart": 1794488476,
     "saleOpen": 1, "freeAvailable_user": 1, "balanceOf_user": 0})
# --- BC1B: freeCount 446 -> 447/3000 = 14.9% - DIAM ---
upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
    {"freeCount": 447, "FREE_CAP": 3000, "saleStart": 1794488398,
     "freeMinted_user": 0, "balanceOf_user": 0}, sec="track_c")
# --- LuckyCatch / MECHA / Steady ---
upd("0xD405C90079c594DA2456F5b37B4158A12f1382e5",
    {"totalSupply": 21, "agentFreeCount": 20, "paidSold": 1, "mintOpen": 1, "balanceOf_user": 0})
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
    {"totalMinted": 1874, "freeClaimed": 1873, "freeAvailable_user": 2, "balanceOf_user": 0})
k, v = by_addr("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
    {"totalSupply": 421, "freeClaimed": 421, "FREE_SUPPLY": 555, "mintOpen": 1,
     "freeUsed_user": 0, "balanceOf_user": 0, **vel(413, 421, prev_rate)})
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
    {"totalSupply": 562, "freeClaimed": 558, "FREE_SUPPLY": 888, "mintOpen": 1, "balanceOf_user": 0})
upd("0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69", {"totalSupply": 5292, "mintOpen": 1, "balanceOf_user": 0})
upd("0x486d0947caa3d70c19e38f6c789489d39291e9e7", {"totalSupply": 3000, "mintOpen": 1, "balanceOf_user": 0})
upd("0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4",
    {"totalSupply": 327, "totalMinted": 327, "freeMinted": 325, "FREE_SUPPLY": 325, "mintOpen": 1, "freeAvailable_user": 0, "balanceOf_user": 0})
upd("0x8aa9d6a09caf475593852e681b58b26dc94edd56", {"totalSupply": 4901, "totalMinted": 4901, "balanceOf_user": 0})
upd("0x6c17af4fac529e5679686e121a75e85b1063cd45", {"totalSupply": 4900, "totalMinted": 4900, "balanceOf_user": 0})
# --- track_c: BHTB / AgentGrid (unchanged except BHTB freeUsed) ---
upd("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
    {"freeUsed": 242, "FREE_QUOTA": 555, "mintEnd": 1794570281, "freeClaimed_user": 0, "balanceOf_user": 0}, sec="track_c")
upd("0x651302C0043040D48EaAF85605E12F0549aD6D89",
    {"FREE_SHARES": 500, "freeUsed": 21}, sec="track_c")
# --- binanceai claim (track B): unchanged, refund/failed ---
b = snap.get("binanceai_claim", {})
b.update({"launched": 0, "failed": 1, "isRefundPhase": 1, "tokenClaimed_user": 0,
          "tokenBalance_user": 0, "lastReadBlock": BLOCK, "lastReadWib": NOW,
          "runNote0231_1113": f"Run 0231 (blok {BLOCK}): launched()=0 TETAP, failed()=1, isRefundPhase()=1, tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 - tetap refund/failed, tidak dilaporkan ulang."})
snap["binanceai_claim"] = b
# --- run notes ---
snap["runNote0231_1113"] = ("Run 0231 (blok 133216806, verify 90,2 dtk, interval ~29,8 mnt vs run 0201): "
  "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. "
  "OUTY minted 1->2, freeSold 2/1500, FREE_FEE 0.0001 BNB TETAP - bukan gas-only, dicatat saja. "
  "SolNFT 306/333 = 91,9% (+3) tetap strong-lead-gate-blocked - DIAM (27 slot tersisa). "
  "Agentx 337/1111 = 30,3% (+14) velocity GAGAL (0,470/mnt vs prev 0,709 = 0,66x) - tetap early, DIAM. "
  "AgentLabs 846 spesimen (+34, rate 1,141 vs prev 0,674 = 1,69x) velocity LOLOS, tapi tanpa free cap -> tidak bisa jadi strong lead; belum seal (seal 07:00 WIB) - DIAM. "
  "Steady 421/555 = 75,9% (+8) velocity GAGAL, umur MASIH UNVERIFIED (sweep run ini 0 hasil baru soal Steady) -> tidak promosi - DIAM. "
  "OBFG 538/1230 = 43,7% (+19) tetap track-C lead gate-blocked - DIAM. BC1B 447/3000 tetap - DIAM. "
  "LuckyCatch 21 tetap (deadline umur 04:06:03 WIB 13 Nov). MECHA 1874 tetap, umur unverified. "
  "Scan leg fast-fail (Ankr 401); watermark tetap 132512564. Feed 20, 0 baru + Boltbook 0 baru; bridge 116, 0 baru. "
  "Binanceai tetap refund/failed. Odaily 0 item Agent ID. Sweep: semua dikenal/excluded (Oathbots, Agentic Gangster, MOLT, TINY AGENTS, Golden Agents, Pocket Ai, Believers, AgentGoldMiner, AGENT COSMOS, AGC).")
snap["runNote0231_1113_scan"] = ("Run 0231 route 4: SCAN FAST-FAIL - pre-flight ankr_getLogs HTTP 401 Unauthorized. "
  "Watermark TIDAK dimajukan (tetap 132512564); gap ke head terus tumbuh (head 133216806 saat run). Route 5c dilewati (tanpa output scan baru). Ankr outage sejak 9 Nov.")
snap["runNote0231_1113_obfg"] = ("Run 0231 (blok 133216806): OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 freeMinted 519->538/1230 (43,7%), "
  "totalSupply 538, saleStart 1794488476 (20:01:16 WIB 12 Nov), saleOpen=1, freeAvailable(user)=1. "
  "Tetap track-C lead gate-blocked - DIAM.")
snap["runNote0231_1113_binanceai"] = ("Run 0231 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, "
  "tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 (blok 133216806) - tetap refund/failed, tidak dilaporkan ulang.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = "Run 0231: 0 kandidat/strong/early/track-C baru; OUTY freeSold 2/1500, FREE_FEE 0.0001 BNB tetap (bukan gas-only, dicatat saja); AgentLabs velocity lolos tapi tanpa free cap (tetap early); scan fast-fail Ankr 401."
snap["timestamp_wib"] = NOW
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK; contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]))
