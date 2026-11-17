#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 03:31 WIB.
Address-exact matching only. Updates numeric fields + lastReadWib/lastReadBlock.
OUTY: minted/freeSold 2->8, FREE_FEE 0.0001 BNB TETAP (NOT gas-only).
VISION + UFO: AGE-EXCLUDED, removed from track_c (never reported as leads -> silent
per AGENTS.md convention; recorded in run notes + runlog only).
0xF1E0: retry shape-check OK - sell contract (6 fns, no mint/quote/free/agent) -> checked-not-agent-shaped.
0xf1b0: Boltbook-new, Sourcify 404 (unverified) -> checked-not-agent-shaped.
Backup: /tmp/onchain-snapshot-2026-11-13-0331.bak (taken before run)."""
import json, shutil
from datetime import datetime, timedelta, timezone
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d ~%H:%M WIB")
BLOCK = 133224677
shutil.copy(BASE + "onchain-snapshot.json", "/tmp/onchain-snapshot-2026-11-13-0331.bak")
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
    v.update(fields); v["lastReadWib"] = NOW; v["lastReadBlock"] = BLOCK
    return k
INTERVAL_MIN = 30.8  # block delta 133224677-133220567 = 4110 blocks x ~0.45 dtk
def vel(old_total, new_total, prev_rate):
    if old_total is None or new_total is None: return {}
    minted = new_total - old_total
    rate = round(minted / INTERVAL_MIN, 3)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return {"previousTotalSupply": old_total, "mintedInInterval": minted,
            "intervalMinutes": INTERVAL_MIN, "currentRatePerMin": rate,
            "previousRatePerMin": prev_rate, "velocityRatio": ratio,
            "velocityLegPasses": bool(minted >= 20 and prev_rate and rate >= 1.5 * prev_rate)}

# --- SolNFT: 307 -> 308 (+1, <20) velocity FAIL; 308/333 = 92.5% ---
k, v = by_addr("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
    {"totalMinted": 308, "freeMinted": 308, "FREE_CAP": 333, "mintOpen": 1,
     "freeClaimed_user": 0, "balanceOf_user": 0,
     **vel(307, 308, prev_rate)})
# --- Agentx: 337 -> 343 (+6, <20) velocity FAIL; 343/1111 = 30.9% ---
k, v = by_addr("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
    {"totalMinted": 343, "freeMinted": 343, "FREE_CAP": 1111, "MAX_SUPPLY": 2222,
     "mintOpen": 1, "mintOpensAt": 1794499865, "price": 5000000000000000,
     "freeClaimed_user": 0, "balanceOf_user": 0, "holdsAgentId_user": 1,
     "mintsBy_user": 0, "name": "Agentx", "symbol": "AGENTX", "nextTokenId": 344,
     **vel(337, 343, prev_rate)})
# --- AgentLabs: 939 -> 1011 (+72, rate 2.338 vs prev 3.298 = 0.71x) velocity FAIL ---
# Still early - DIAM: NO free cap (free % not measurable), so no strong-lead promotion.
# Experiment 1 unsealed, ends 1794528000 (07:00 WIB 13 Nov). Block read failed in agentlabs script (views OK).
k, v = by_addr("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7",
    {"totalSpecimens": 1011, "participants": 983, "experimentEnd": 1794528000,
     "priceFor_user": 0, "isSealed": 0, "balanceOf_user": 0,
     **vel(939, 1011, prev_rate)})
# --- OUTY: minted/freeSold 2 -> 8/1500; FREE_FEE 0.0001 BNB (NOT gas-only) ---
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412",
    {"minted": 8, "freeSold": 8, "paidSold": 0, "FREE_SUPPLY": 1500,
     "PAID_CAP": 15000, "START": 1794510227, "FREE_END": 1794596627,
     "FREE_FEE": 100000000000000, "PRICE": 3000000000000000, "phase": 1,
     "freeOpen": 1, "paidOpen": 0, "freeQuotaOf_user": 1, "quotaOf_user": 10,
     "balanceOf_user": 0,
     "notFreeNote": "Run 0331 (blok 133224677): OUTY minted/freeSold 2->8/1500 (+6 free mints). FREE_FEE()=100000000000000 wei = 0.0001 BNB TETAP - jalur 'free' berbayar, BUKAN gas-only, GAGAL kriteria (1) Free Bacot; bukan kandidat/lead, tidak di-preview/di-mint, tidak dilaporkan ke chat."})
# --- BC1B: freeCount 448/3000 = 14.9% (flat) - DIAM ---
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
    {"totalSupply": 445, "freeClaimed": 444, "FREE_SUPPLY": 555, "mintOpen": 1,
     "freeUsed_user": 0, "balanceOf_user": 0, **vel(433, 445, prev_rate)})
# --- other re-reads ---
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", {"totalSupply": 962, "balanceOf_user": 0})
upd("0x11986f3DF799a28bB97921F49406a7197b1d34d2", {"totalSupply": 93, "mintOpen": 1, "balanceOf_user": 0})
upd("0x467696af8c2206B977B24081445104632dc1D459",
    {"totalMinted": 932, "freeMinted": 932, "FREE_SUPPLY": 1200, "balanceOf_user": 1, "freeAvailable_user": 0})
upd("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2",
    {"totalMinted": 301, "freeMinted": 300, "FREE_SUPPLY": 300, "balanceOf_user": 1})
k, v = by_addr("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
    {"totalSupply": 1263, "FREE_SUPPLY": 1000, "MAX_SUPPLY": 10000, "balanceOf_user": 1,
     **vel(1263, 1263, prev_rate)})
k, v = by_addr("0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
    {"totalSupply": 2530, "freeClaimed": 2524, "FREE_SUPPLY": 7777, "mintOpen": 1, "balanceOf_user": 1,
     **vel(2529, 2530, prev_rate)})
k, v = by_addr("0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC",
    {"totalSupply": 717, "freeClaimed": 712, "FREE_SUPPLY": 712, "mintOpen": 1, "balanceOf_user": 1,
     **vel(717, 717, prev_rate)})
# retries
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810", {"totalSupply": 926, "freeMinted": 876, "mintOpen": 1, "balanceOf_user": 0})
upd("0x7ef49be2a9ade4fae0888f4065c8f122a146f6d0", {"totalSupply": 4900, "totalMinted": 4900, "balanceOf_user": 0})
upd("0xb8a990e16fd66d398cc27d0c8bdb11524bc0dc8e",
    {"totalMinted": 294, "freeMinted": 294, "FREE_SUPPLY": 1111, "freeClaimed_user": 0, "balanceOf_user": 0})
upd("0xad0d8ac3d61fc8ab397b7136c69fcbf1281a4998",
    {"totalSupply": 566, "freeClaimed": 562, "FREE_SUPPLY": 888, "mintOpen": 1, "balanceOf_user": 0})
upd("0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69", {"totalSupply": 5295, "mintOpen": 1, "balanceOf_user": 0})
upd("0x486d0947caa3d70c19e38f6c789489d39291e9e7", {"totalSupply": 3000, "mintOpen": 1, "balanceOf_user": 0})
upd("0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4",
    {"totalSupply": 327, "totalMinted": 327, "freeMinted": 325, "FREE_SUPPLY": 325, "mintOpen": 1, "freeAvailable_user": 0, "balanceOf_user": 0})
upd("0x8aa9d6a09caf475593852e681b58b26dc94edd56", {"totalSupply": 4901, "totalMinted": 4901, "balanceOf_user": 0})
upd("0x6c17af4fac529e5679686e121a75e85b1063cd45", {"totalSupply": 4900, "totalMinted": 4900, "balanceOf_user": 0})
# --- track_c: BHTB / AgentGrid ---
upd("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
    {"freeUsed": 251, "FREE_QUOTA": 555, "mintEnd": 1794570281, "freeClaimed_user": 0, "balanceOf_user": 0}, sec="track_c")
upd("0x651302C0043040D48EaAF85605E12F0549aD6D89",
    {"FREE_SHARES": 500, "freeUsed": 21}, sec="track_c")
# --- OBFG: no structured snapshot entry (runNote only, pattern since 2101) ---
obfg_k, obfg_v = by_addr("0x5314071bba19943f58347ba5dec423e5032a6818", sec="track_c")
if obfg_v is None:
    print("OBFG: no structured track_c entry (runNote only, as before)")
# --- binanceai claim (track B): unchanged, refund/failed ---
b = snap.get("binanceai_claim", {})
b.update({"launched": 0, "failed": 1, "isRefundPhase": 1, "tokenClaimed_user": 0,
          "tokenBalance_user": 0, "lastReadBlock": BLOCK, "lastReadWib": NOW,
          "runNote0331_1113": f"Run 0331 (blok {BLOCK}): launched()=0 TETAP, failed()=1, isRefundPhase()=1, tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 - tetap refund/failed, tidak dilaporkan ulang."})
snap["binanceai_claim"] = b
# --- VISION age-exclusion: remove from track_c (silent: never reported as lead) ---
vision = snap.get("track_c", {}).pop("VISION", None)
if vision is not None:
    snap["runNote0331_1113_vision_excluded"] = (
        "Run 0331 AGE-EXCLUDED + REMOVED dari track_c: VISION 0x5f76cab7b054e088563d5098e17bd0dc430e61ae. "
        "Bukti umur: sale TERBUKTI sudah buka selambatnya 10 Nov 15:58 UTC (snapshot live AirdropBuzz: 305 free shares, blok 132804382; "
        "observasi pertama 9 Nov ~17:05 UTC, 182 shares, tercatat di launchNote) -> umur saat baca ini (12 Nov 20:36 UTC) >=52 jam, "
        "melewati 24 jam; free pool MASIH terbuka (baca segar blok 133225014: totalShares 2089/100000, totalFreeShares 2082, "
        "freeUsed(user)=0, sharesOf(user)=0) -> belum sold out -> age-excluded per aturan. "
        "Tidak dilaporkan ke chat: VISION tidak pernah dilaporkan sebagai lead (watchlist-only-age-unverified sejak 10 Nov), "
        "jadi penghapusan diam sesuai konvensi AGENTS.md. Bila fase/batch mint baru terverifikasi, boleh masuk lagi via discovery segar.")
    print("VISION removed from track_c")
else:
    print("VISION not found in track_c (already removed?)")
# --- UFO age-exclusion + window closed: remove from track_c (silent: never reported as lead) ---
ufo = snap.get("track_c", {}).pop("UFO", None)
if ufo is not None:
    snap["runNote0331_1113_ufo_excluded"] = (
        "Run 0331 AGE-EXCLUDED + REMOVED dari track_c: UFO 0xE4059eA596392AcA14100af6CDC9481c330E2728. "
        "Bukti umur: launch ~10 Nov 22:05 WIB (Sourcify verifiedAt 22:06:52 WIB 10 Nov + artikel The Colony jendela 2 hari) -> umur ~53 jam; "
        "saleEnd on-chain 1794495945 = 12 Nov 15:05:45 UTC / 22:05:45 WIB, SUDAH LEWAT saat baca ini (baca segar blok 133225014: FREE_SHARES 1000, "
        "totalSupply 9e30) -> jendela penjualan TUTUP + umur >24 jam. Shape tetap unverified + permit gate (share-first) tidak pernah terpenuhi. "
        "Tidak dilaporkan ke chat: UFO tidak pernah dilaporkan sebagai lead (watchlist-only-shape-unverified-permit-gate sejak 11 Nov), "
        "jadi penghapusan diam sesuai konvensi AGENTS.md.")
    print("UFO removed from track_c")
else:
    print("UFO not found in track_c (already removed?)")
# --- checked-not-agent-shaped: feed 0xF1E0 + Boltbook 0xf1b0 ---
track_c["Feed-0xF1E0"] = {
    "sale": "0xF1E0D4461273d9923181716E3691Db5126900629",
    "status": "checked-not-agent-shaped-2026-11-13",
    "note": "Run 0331 feed Sourcify (verifiedAt 19:12-20:33Z 12 Nov): legs shape-check GAGAL transport (IncompleteRead), retry curl OK: 6 fns (owner, rescue, sellBatch, sellBatchV3, sellFor, sellForV3) - SELL contract, no mint, no quote, no free views, no agent ref, not a token. S1=False S2=False. First-mint unverifiable (Ankr 401) - NOT an early lead.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
track_c["Boltbook-0xf1b0"] = {
    "sale": "0xf1b0f2dd53b46c18ceb839838b6caf64e9f95fb7",
    "status": "checked-not-agent-shaped-2026-11-13",
    "note": "Run 0331 Boltbook-new (EN+ZH 7 alamat): Sourcify 404 (unverified, no ABI) - shape unknown, NOT agent-shaped on Sourcify. First-mint unverifiable (Ankr 401) - NOT an early lead.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
# --- run notes ---
snap["runNote0331_1113"] = ("Run 0331 (blok 133224677, verify 64,3 dtk, interval ~30,8 mnt vs run 0301): "
  "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. "
  "OUTY minted/freeSold 2->8/1500 (+6), FREE_FEE 0.0001 BNB TETAP - bukan gas-only, dicatat saja. "
  "SolNFT 308/333 = 92,5% (+1) tetap strong-lead-gate-blocked - DIAM (25 slot tersisa). "
  "Agentx 343/1111 = 30,9% (+6) velocity GAGAL - tetap early, DIAM. "
  "AgentLabs 1011 spesimen (+72, rate 2,338 vs prev 3,298 = 0,71x) velocity GAGAL run ini; tanpa free cap -> tetap early, belum seal (seal 07:00 WIB) - DIAM. "
  "Steady 445/555 = 80,2% (+12, <20) velocity GAGAL, umur MASIH UNVERIFIED (sweep run ini 0 hasil baru soal Steady) -> tidak promosi - DIAM. "
  "OBFG 551/1230 = 44,8% (+5) tetap track-C lead gate-blocked - DIAM. BC1B 448/3000 - DIAM. "
  "LuckyCatch 21 tetap (deadline umur 04:06:03 WIB 13 Nov, ~30 mnt lagi). MECHA 1874 tetap, umur unverified. "
  "VISION + UFO AGE-EXCLUDED dan dihapus dari track_c (diam, keduanya tidak pernah dilaporkan sebagai lead). "
  "Scan leg fast-fail (Ankr 401); watermark tetap 132512564. Feed 20 (verifiedAt 19:12-20:33Z) + Boltbook EN+ZH 7 alamat, 1 feed-new (0xF1E0, sell contract, checked-not-agent-shaped via retry) + 1 Boltbook-new (0xf1b0, Sourcify 404). "
  "Boltbook EN+ZH terbaca normal run ini (44.786 / 43.128 byte). "
  "Binanceai tetap refund/failed. Odaily + PANews 0 item Agent ID. Sweep: semua dikenal/excluded (Oathbots, Agentic Gangster, RIGBYPASS, MOLT, AGENT MAO, AGENT COSMOS, Pixel Fox, Coracle, First-Dollar Grove, Meow Cards age-excluded, NOVRA age-excluded, NEBULA minted-by-user, XIGO pool-closed).")
snap["runNote0331_1113_scan"] = ("Run 0331 route 4: SCAN FAST-FAIL - pre-flight ankr_getLogs HTTP 401 Unauthorized. "
  "Watermark TIDAK dimajukan (tetap 132512564); gap ke head terus tumbuh (head 133224677 saat run). Route 5c dilewati (tanpa output scan baru). Ankr outage sejak 9 Nov.")
snap["runNote0331_1113_obfg"] = ("Run 0331 (blok 133224677): OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 freeMinted 546->551/1230 (44,8%), "
  "totalSupply 551, saleStart 1794488476 (20:01:16 WIB 12 Nov), saleOpen=1, freeAvailable(user)=1. "
  "Tetap track-C lead gate-blocked - DIAM.")
snap["runNote0331_1113_binanceai"] = ("Run 0331 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, "
  "tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 (blok 133224677) - tetap refund/failed, tidak dilaporkan ulang.")
snap["runNote0331_1113_staleblock"] = ("Run 0331 CATATAN KOREKSI LAPANGAN: field lastReadBlock di entri snapshot (132821400, lastReadWib '03:10 WIB') "
  "TIDAK konsisten dengan head live (~133,22M) - angka itu usang/salah label dari run lama (blok 132821400 ~2 hari sebelum 133220567 run 0301); "
  "merge run ini menulis lastReadBlock=133224677 untuk semua kontrak yang dibaca ulang. Nilai historis di runNote lama tidak diubah.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = "Run 0331: 0 kandidat/strong/early/track-C baru; OUTY freeSold 2->8/1500, FREE_FEE 0.0001 BNB tetap (bukan gas-only, dicatat saja); AgentLabs velocity gagal run ini (+72, 0.71x); VISION + UFO age-excluded + dihapus dari track_c (diam); scan fast-fail Ankr 401; Boltbook EN+ZH normal; 0xF1E0 checked-not-agent-shaped."
snap["timestamp_wib"] = NOW
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK; contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]))
