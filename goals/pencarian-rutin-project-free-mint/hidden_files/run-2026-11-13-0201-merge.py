#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 02:01 WIB.
Address-exact matching only. Updates numeric fields + lastReadWib;
OUTY opened (upcoming -> opened, but FREE_FEE 0.0001 BNB = NOT gas-only free,
so NOT a candidate/lead - recorded only, no report); records 10 new
feed/boltbook contracts as checked-not-agent-shaped.
Backup: /tmp/onchain-snapshot-2026-11-13-0201.bak (taken before run)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-13 ~02:15 WIB"
BLOCK = 133212827
shutil.copy(BASE + "onchain-snapshot.json", "/tmp/onchain-snapshot-2026-11-13-0201.bak")
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
INTERVAL_MIN = 28.2  # block delta 133212827-133209073 = 3754 blocks x ~0.45 dtk
def vel(old_total, new_total, prev_rate):
    if old_total is None or new_total is None: return {}
    minted = new_total - old_total
    rate = round(minted / INTERVAL_MIN, 3)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return {"previousTotalSupply": old_total, "mintedInInterval": minted,
            "intervalMinutes": INTERVAL_MIN, "currentRatePerMin": rate,
            "previousRatePerMin": prev_rate, "velocityRatio": ratio,
            "velocityLegPasses": bool(minted >= 20 and prev_rate and rate >= 1.5 * prev_rate)}

# --- SolNFT: 299 -> 303 (+4, <20) velocity FAIL; 303/333 = 91.0% ---
k, v = by_addr("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
    {"totalMinted": 303, "freeMinted": 303, "FREE_CAP": 333, "mintOpen": 1,
     "freeClaimed_user": 0, "balanceOf_user": 0,
     **vel(299, 303, prev_rate)})
# --- Agentx: 303 -> 323 (+20, rate 0.709 vs prev 0.387 = 1.83x) velocity PASSES ---
# Still NOT a candidate: 323/1111 = 29.1% < 50%, X + website unverified. Early - DIAM.
k, v = by_addr("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
    {"totalMinted": 323, "freeMinted": 323, "FREE_CAP": 1111, "MAX_SUPPLY": 2222,
     "mintOpen": 1, "mintOpensAt": 1794499865, "price": 5000000000000000,
     "freeClaimed_user": 0, "balanceOf_user": 0, "holdsAgentId_user": 1,
     "mintsBy_user": 0, "name": "Agentx", "symbol": "AGENTX", "nextTokenId": 324,
     **vel(303, 323, prev_rate)})
# --- AgentLabs: 793 -> 812 (+19, <20, rate 0.674 vs prev 1.127 = 0.60x) FAIL ---
k, v = by_addr("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7",
    {"totalSpecimens": 812, "participants": 790, "experimentEnd": 1794528000,
     "priceFor_user": 0, "isSealed": 0, "balanceOf_user": 0,
     **vel(793, 812, prev_rate)})
# --- OUTY OPENED: minted 0->1, freeSold 0->1, freeOpen 0->1, phase 0->1 ---
# FREE_FEE 100000000000000 wei = 0.0001 BNB: the "free" lane is NOT gas-only,
# so OUTY fails criterion (1) and is NOT a Free Bacot candidate/lead.
# Recorded only (status change), never previewed/minted, no chat report.
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412",
    {"status": "watchlist-only-opened-fee-not-free-2026-11-13",
     "minted": 1, "freeSold": 1, "paidSold": 0, "FREE_SUPPLY": 1500,
     "PAID_CAP": 15000, "START": 1794510227, "FREE_END": 1794596627,
     "FREE_FEE": 100000000000000, "PRICE": 3000000000000000, "phase": 1,
     "freeOpen": 1, "paidOpen": 0, "freeQuotaOf_user": 1, "quotaOf_user": 10,
     "balanceOf_user": 0,
     "notFreeNote": "Run 0201 (blok 133212827): OUTY DIBUKA 02:03:47 WIB (START 1794510227), freeSold pertama 1/1500. TAPI FREE_FEE()=100000000000000 wei = 0.0001 BNB - jalur 'free' berbayar, BUKAN gas-only, jadi GAGAL kriteria (1) Free Bacot; bukan kandidat/lead, tidak di-preview/di-mint, tidak dilaporkan ke chat."},
    sec="track_c")
# --- LuckyCatch / MECHA / Steady ---
upd("0xD405C90079c594DA2456F5b37B4158A12f1382e5",
    {"totalSupply": 21, "agentFreeCount": 20, "paidSold": 1, "mintOpen": 1, "balanceOf_user": 0})
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
    {"totalMinted": 1874, "freeClaimed": 1873, "freeAvailable_user": 2, "balanceOf_user": 0})
k, v = by_addr("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
    {"totalSupply": 413, "freeClaimed": 413, "FREE_SUPPLY": 555, "mintOpen": 1,
     "freeUsed_user": 0, "balanceOf_user": 0, **vel(403, 413, prev_rate)})
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
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810", {"totalSupply": 922, "freeMinted": 872, "mintOpen": 1, "balanceOf_user": 0})
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
# --- track_c: BHTB / AgentGrid / BC1B (unchanged) ---
upd("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
    {"freeUsed": 229, "FREE_QUOTA": 555, "mintEnd": 1794570281, "freeClaimed_user": 0, "balanceOf_user": 0}, sec="track_c")
upd("0x651302C0043040D48EaAF85605E12F0549aD6D89",
    {"FREE_SHARES": 500, "freeUsed": 21}, sec="track_c")
upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
    {"freeCount": 446, "FREE_CAP": 3000, "saleStart": 1794488398,
     "freeMinted_user": 0, "balanceOf_user": 0}, sec="track_c")
# --- 10 new feed/boltbook contracts checked this run: 0 S1/S2 ---
# 6x 47-fn factory wave (early_shape=True: mint + agent ref, TAPI tanpa free
# views dan tanpa quote; first-mint TIDAK bisa diverifikasi karena Ankr 401,
# jadi BUKAN early lead) + 1x 14-fn tanpa mint + 2x Sourcify 404 + 1x 54-fn
# (mint+quote, tanpa free views, tanpa agent ref).
for short, addr, note in [
    ("Feed-0x2d61", "0x2d61347D9b48De99cBdF0D8D7a2DD73f5B15E90D", "47 fns, mint, agent_ref, no quote, no free views"),
    ("Feed-0x9625", "0x9625391531E31Baf61ac9f3061a4Da38EB49684A", "47 fns, mint, agent_ref, no quote, no free views"),
    ("Feed-0x3A82", "0x3A82dd3c9Df165D89259a8ec1eCC6CF91D7AEC4E", "47 fns, mint, agent_ref, no quote, no free views"),
    ("Feed-0xBa5d", "0xBa5dd9f1eE470FDF39EF7A82Cf09B2C44A917bC8", "47 fns, mint, agent_ref, no quote, no free views"),
    ("Feed-0x55eE", "0x55eEFba7263Fa518f11A6cDAAe4c403B082DB3fE", "47 fns, mint, agent_ref, no quote, no free views"),
    ("Feed-0x1E84", "0x1E84079e0766AB7cBe182085DEd86443ad9b1433", "47 fns, mint, agent_ref, no quote, no free views"),
    ("Feed-0x1bc2", "0x1bc2d52B737d75E6e7874E646b616552fE7acDF5", "14 fns, no mint, no quote, no agent ref"),
    ("Feed-0x1721", "0x17210dc7e19499b6071a3d0d9b24f5418d270c4b", "Boltbook-new; Sourcify 404 unverified"),
    ("Feed-0xb9df", "0xb9df7dc77dbfca12974d40e63720b5bf125cbd8e", "Boltbook-new; Sourcify 404 unverified"),
    ("Feed-0x731d", "0x731d879ee2cd4bbf32efef9178d51d5c1441d052", "Boltbook-new; 54 fns, mint+quote, no free views, no agent ref"),
]:
    if short in track_c:
        print("SKIP exists:", short); continue
    track_c[short] = {"sale": addr, "status": "checked-not-agent-shaped-2026-11-13",
                      "note": f"Run 0201 feed Sourcify (verifiedAt 18:54-19:07Z) / Boltbook-new: S1=False S2=False; {note}. First-mint unverifiable (Ankr 401) - NOT an early lead.",
                      "lastReadWib": NOW}
# --- binanceai claim (track B): unchanged, refund/failed ---
b = snap.get("binanceai_claim", {})
b.update({"launched": 0, "failed": 1, "isRefundPhase": 1, "tokenClaimed_user": 0,
          "tokenBalance_user": 0, "lastReadBlock": BLOCK, "lastReadWib": NOW,
          "runNote0201_1113": f"Run 0201 (blok {BLOCK}): launched()=0 TETAP, failed()=1, isRefundPhase()=1, tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 - tetap refund/failed, tidak dilaporkan ulang."})
snap["binanceai_claim"] = b
# --- run notes ---
snap["runNote0201_1113"] = ("Run 0201 (blok 133212827, verify 74,7 dtk, interval ~28,2 mnt vs run 0131): "
  "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. "
  "OUTY DIBUKA 02:03:47 WIB (freeSold 1/1500) TAPI FREE_FEE 0.0001 BNB - bukan gas-only, bukan kandidat/lead, dicatat saja. "
  "SolNFT 303/333 = 91,0% (+4) tetap strong-lead-gate-blocked - DIAM (30 slot tersisa). "
  "Agentx 323/1111 = 29,1% (+20) velocity LOLOS (0,709/mnt vs prev 0,387 = 1,83x) tapi <50% + X/website unverified - tetap early, DIAM. "
  "AgentLabs 812 spesimen (+19, rate 0,674 vs prev 1,127 = 0,60x) velocity GAGAL, belum seal (seal 07:00 WIB) - DIAM. "
  "Steady 413/555 = 74,4% (+10) umur MASIH UNVERIFIED (sweep run ini 0 hasil baru soal Steady) -> tidak promosi - DIAM. "
  "OBFG 519/1230 = 42,2% tetap track-C lead gate-blocked - DIAM. BC1B 446/3000 tetap - DIAM. "
  "LuckyCatch 21 tetap (deadline umur 04:06:03 WIB 13 Nov). MECHA 1874 tetap, umur unverified. "
  "Scan leg fast-fail (Ankr 401); watermark tetap 132512564. Feed 20, 7 baru + Boltbook 3 baru, 0 S1/S2/early; "
  "bridge 116, 0 baru. Binanceai tetap refund/failed. Odaily 0 item Agent ID. Sweep: semua dikenal/excluded (Burn Agent, Agentic Gangster, Meow Cards, MOLT, RIGBYPASS, UFO, NEBULA).")
snap["runNote0201_1113_scan"] = ("Run 0201 route 4: SCAN FAST-FAIL - pre-flight ankr_getLogs HTTP 401 Unauthorized. "
  "Watermark TIDAK dimajukan (tetap 132512564); gap ke head terus tumbuh (head 133212827 saat run). Route 5c dilewati (tanpa output scan baru). Ankr outage sejak 9 Nov.")
snap["runNote0201_1113_outy"] = ("Run 0201 OUTY: 0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412 DIBUKA 02:03:47 WIB 13 Nov (START 1794510227, blok 133212827): "
  "minted 0->1, freeSold 0->1/1500, freeOpen 0->1, phase 0->1, freeQuotaOf(user)=1. FREE_FEE()=100000000000000 wei = 0.0001 BNB "
  "-> jalur 'free' berbayar, BUKAN gas-only, GAGAL kriteria (1) Free Bacot. Bukan kandidat/lead, tidak di-preview/di-mint, tidak dilaporkan ke chat; status snapshot -> watchlist-only-opened-fee-not-free-2026-11-13.")
snap["runNote0201_1113_obfg"] = ("Run 0201 (blok 133212827): OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 freeMinted 511->519/1230 (42,2%), "
  "totalSupply 519, saleStart 1794488476 (20:01:16 WIB 12 Nov), saleOpen=1, freeAvailable(user)=1. "
  "Tetap track-C lead gate-blocked - DIAM.")
snap["runNote0201_1113_binanceai"] = ("Run 0201 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, "
  "tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 (blok 133212827) - tetap refund/failed, tidak dilaporkan ulang.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = "Run 0201: 0 kandidat/strong/early/track-C baru; OUTY dibuka tapi FREE_FEE 0.0001 BNB (bukan gas-only, dicatat saja); scan fast-fail Ankr 401."
snap["timestamp_wib"] = NOW
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK; contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]))
