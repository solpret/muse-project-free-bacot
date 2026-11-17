#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 01:31 WIB.
Address-exact matching only. Updates numeric fields + lastReadWib;
removes GAME (sold out 333/333, reported once this run); records 7 new
feed contracts as checked-not-agent-shaped.
Backup: /tmp/onchain-snapshot-2026-11-13-0131.bak (taken before run)."""
import json, copy, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-13 ~01:50 WIB"
BLOCK = 133209073
shutil.copy(BASE + "onchain-snapshot.json", "/tmp/onchain-snapshot-2026-11-13-0131.bak")
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
verify = json.load(open(BASE + "run-2026-11-13-0131-verify.json"))["reads"]
INTERVAL_MIN = 28.4  # block delta 133209073-133205288 = 3785 blocks x ~0.45 dtk
def vel(old_total, new_total, prev_rate):
    if old_total is None or new_total is None: return {}
    minted = new_total - old_total
    rate = round(minted / INTERVAL_MIN, 3)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return {"previousTotalSupply": old_total, "mintedInInterval": minted,
            "intervalMinutes": INTERVAL_MIN, "currentRatePerMin": rate,
            "previousRatePerMin": prev_rate, "velocityRatio": ratio,
            "velocityLegPasses": bool(minted >= 20 and prev_rate and rate >= 1.5 * prev_rate)}

# --- SolNFT: 297 -> 299 (+2, <20) velocity FAIL ---
k, v = by_addr("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
    {"totalMinted": 299, "freeMinted": 299, "FREE_CAP": 333, "mintOpen": 1,
     "freeClaimed_user": 0, "balanceOf_user": 0,
     **vel(297, 299, prev_rate)})
# --- GAME SELLOUT 333/333 -> remove (reported once this run; hot-leg-reported
#     has it only as strong-lead-gate-blocked 01:08, NOT as sellout) ---
k, v = by_addr("0x9c204b333538F853cD5FD8306277130514B86F04")
if v is not None:
    print("REMOVING GAME (sold out 333/333):", k); del contracts[k]
else:
    print("GAME already absent")
# --- Agentx: 292 -> 303 (+11, <20) velocity FAIL ---
k, v = by_addr("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
    {"totalMinted": 303, "freeMinted": 303, "FREE_CAP": 1111, "MAX_SUPPLY": 2222,
     "mintOpen": 1, "mintOpensAt": 1794499865, "price": 5000000000000000,
     "freeClaimed_user": 0, "balanceOf_user": 0, "holdsAgentId_user": 1,
     "mintsBy_user": 0, "name": "Agentx", "symbol": "AGENTX", "nextTokenId": 304,
     **vel(292, 303, prev_rate)})
# --- AgentLabs: 761 -> 793 (+32, rate ~1.13 vs prev ~1.52 = 0.74x) FAIL ---
k, v = by_addr("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7",
    {"totalSpecimens": 793, "participants": 771, "experimentEnd": 1794528000,
     "priceFor_user": 0, "isSealed": 0, "balanceOf_user": 0,
     **vel(761, 793, prev_rate)})
# --- LuckyCatch / MECHA / Steady ---
upd("0xD405C90079c594DA2456F5b37B4158A12f1382e5",
    {"totalSupply": 21, "agentFreeCount": 20, "paidSold": 1, "mintOpen": 1, "balanceOf_user": 0})
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
    {"totalMinted": 1872, "freeClaimed": 1871, "freeAvailable_user": 2, "balanceOf_user": 0})
k, v = by_addr("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf")
prev_rate = v.get("currentRatePerMin") if v else None
upd("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
    {"totalSupply": 403, "freeClaimed": 403, "FREE_SUPPLY": 555, "mintOpen": 1,
     "freeUsed_user": 0, "balanceOf_user": 0, **vel(398, 403, prev_rate)})
# --- other re-reads ---
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", {"totalSupply": 962, "balanceOf_user": 0})
upd("0x11986f3DF799a28bB97921F49406a7197b1d34d2", {"totalSupply": 93, "mintOpen": 1, "balanceOf_user": 0})
upd("0x467696af8c2206B977B24081445104632dc1D459",
    {"totalMinted": 931, "freeMinted": 931, "FREE_SUPPLY": 1200, "balanceOf_user": 1, "freeAvailable_user": 0})
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
upd("0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69", {"totalSupply": 5290, "mintOpen": 1, "balanceOf_user": 0})
upd("0x486d0947caa3d70c19e38f6c789489d39291e9e7", {"totalSupply": 3000, "mintOpen": 1, "balanceOf_user": 0})
upd("0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4",
    {"totalSupply": 327, "totalMinted": 327, "freeMinted": 325, "FREE_SUPPLY": 325, "mintOpen": 1, "freeAvailable_user": 0, "balanceOf_user": 0})
upd("0x8aa9d6a09caf475593852e681b58b26dc94edd56", {"totalSupply": 4901, "totalMinted": 4901, "balanceOf_user": 0})
upd("0x6c17af4fac529e5679686e121a75e85b1063cd45", {"totalSupply": 4900, "totalMinted": 4900, "balanceOf_user": 0})
# --- track_c: BHTB / AgentGrid / BC1B / OUTY ---
upd("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
    {"freeUsed": 229, "FREE_QUOTA": 555, "mintEnd": 1794570281, "freeClaimed_user": 0, "balanceOf_user": 0}, sec="track_c")
upd("0x651302C0043040D48EaAF85605E12F0549aD6D89",
    {"FREE_SHARES": 500, "freeUsed": 21}, sec="track_c")
upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
    {"freeCount": 446, "FREE_CAP": 3000, "saleStart": 1794488398,
     "freeMinted_user": 0, "balanceOf_user": 0}, sec="track_c")
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412",
    {"minted": 0, "freeSold": 0, "paidSold": 0, "FREE_SUPPLY": 1500, "START": 1794510227,
     "freeOpen": 0, "freeQuotaOf_user": 1, "balanceOf_user": 0}, sec="track_c")
# --- 7 feed contracts checked this run: 0 S1/S2/early (no free views, no agent ref) ---
for short, addr in [
    ("Feed-0xA4F8", "0xA4F8220Aee07089A1d8fE32a38c8eFDCe872157D"),
    ("Feed-0x3044", "0x304494d06915f83Bfd678EFB6b0a931B9C745C92"),
    ("Feed-0xbD11", "0xbD1143A9B2d5Ca8341032C7Bf9B9c5b7C58aFC41"),
    ("Feed-0x841D", "0x841DD83f2686a8aC5640a07D0965fcac3c53A202"),
    ("Feed-0x3c3D", "0x3c3D5aBF88Ef5F32a0B5b300ae71b952242d9EBE"),
    ("Feed-0xfC48", "0xfC48e1170A5dbD0c36B35BA8436Df3714AD26044"),
    ("Feed-0xE258", "0xE258C743ED45135824CD2a76d3013EB5A9ac1235")]:
    track_c[short] = {"sale": addr, "status": "checked-not-agent-shaped-2026-11-13",
                      "note": "Run 0131 feed Sourcify (verifiedAt 18:24-18:33Z): S1=False S2=False early_shape=False; 56-fn factory wave (kecuali 0xE258: 8 fns, tanpa mint) - tanpa free views, tanpa agent ref.",
                      "lastReadWib": NOW}
# --- binanceai claim (track B): unchanged, refund/failed ---
b = snap.get("binanceai_claim", {})
b.update({"launched": 0, "failed": 1, "isRefundPhase": 1, "tokenClaimed_user": 0,
          "tokenBalance_user": 0, "lastReadBlock": BLOCK, "lastReadWib": NOW,
          "runNote0131_1113": f"Run 0131 (blok {BLOCK}): launched()=0 TETAP, failed()=1, isRefundPhase()=1, tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 - tetap refund/failed, tidak dilaporkan ulang."})
snap["binanceai_claim"] = b
# --- run notes ---
snap["runNote0131_1113"] = ("Run 0131 (blok 133209073, verify 64,7 dtk, interval ~28,4 mnt vs run 0101): "
  "1 SELLOUT (GAME 333/333, dilaporkan sekali + dihapus dari snapshot). 0 kandidat baru, 0 strong lead baru, "
  "0 early lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. SolNFT 299/333 = 89,8% (+2) tetap "
  "strong-lead-gate-blocked - DIAM. Agentx 303/1111 = 27,3% (+11) tetap early - DIAM. AgentLabs 793 spesimen "
  "(+32, rate 1,13/mnt vs prev ~1,52 = 0,74x) velocity GAGAL - DIAM. Steady 403/555 = 72,6% (+5) umur MASIH "
  "UNVERIFIED (pencarian indeks run ini 0 hasil baru) -> tidak promosi - DIAM. OBFG 511/1230 = 41,6% tetap "
  "track-C lead gate-blocked - DIAM. BC1B 446/3000 tetap - DIAM. OUTY masih upcoming (START 02:03:47 WIB 13 Nov) - DIAM. "
  "Velocity: 0 lolos. Scan leg fast-fail (Ankr 401); watermark tetap 132512564. Feed 20, 7 baru, 0 S1/S2/early; "
  "Boltbook EN/ZH 0 baru; bridge 116, 0 baru. Binanceai tetap refund/failed. Odaily 0 item Agent ID.")
snap["runNote0131_1113_scan"] = ("Run 0131 route 4: SCAN FAST-FAIL - pre-flight ankr_getLogs HTTP 401 Unauthorized. "
  "Watermark TIDAK dimajukan (tetap 132512564); gap ke head terus tumbuh (head 133209073 saat run). Route 5c dilewati (tanpa output scan baru). Ankr outage sejak 9 Nov.")
snap["runNote0131_1113_game"] = ("Run 0131 GAME SELLOUT: 0x9c204b333538F853cD5FD8306277130514B86F04 totalMinted 330->333/333 = 100%, "
  "freeMinted 333, FREE_CAP 333, mintOpen 1, freeClaimed(user)=0, balanceOf(user)=0 - slot user tidak pernah terpakai. "
  "Strong-lead-gate-blocked berakhir; dilaporkan sekali + dihapus dari snapshot. Hot-leg-reported hanya mencatatnya sebagai strong-lead-gate-blocked 01:08 WIB, BUKAN sellout.")
snap["runNote0131_1113_obfg"] = ("Run 0131 (blok 133209073): OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 freeMinted 500->511/1230 (41,6%), "
  "totalSupply 511, saleStart 1794488476 (20:01:16 WIB 12 Nov, umur ~5,8 jam), saleOpen=1, freeAvailable(user)=1. "
  "Tetap track-C lead gate-blocked - DIAM. (Tetap tanpa entri terstruktur, hanya runNote per run.)")
snap["runNote0131_1113_binanceai"] = ("Run 0131 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, "
  "tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 (blok 133209073) - tetap refund/failed, tidak dilaporkan ulang.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = "Run 0131: 1 SELLOUT (GAME 333/333, dilaporkan sekali + dihapus); 0 kandidat/strong/early/track-C baru; scan fast-fail Ankr 401."
snap["timestamp_wib"] = NOW
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK; contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]))
