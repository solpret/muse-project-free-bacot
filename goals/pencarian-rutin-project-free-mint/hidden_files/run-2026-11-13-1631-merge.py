#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 16:31 WIB.
Fresh reads run-2026-11-13-1631-verify.json (block 133328495, ~16:35 WIB)
+ discovery (feed 20, 1 new: Violet Waybill 0x36D9 S1-shape via ABI, 0 mints
  -> upcoming-prelaunch, saleStart 16:51:03 WIB; Boltbook EN retry OK 47.129 B,
  0 new; ZH 41.844 B, 0 new) + binanceai refund-state re-read (fresh this run:
  launched=0, isRefundPhase=1, failed=1, unchanged).
previousRatePerMin stays FROZEN (convention question from run 0931 still undecided).
No new candidate / strong lead / early lead / track-B change / track-C change
-> SILENT, no chat report. Read-only on-chain; only writes the snapshot.
No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-1631.bak")
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-13-1631-verify.json"))
BLOCK = verify.get("block")
INTERVAL = 30
def find_entry(addr):
    a = addr.lower()
    for top in ("contracts", "track_c"):
        for k, v in snap.get(top, {}).items():
            if isinstance(v, dict) and str(v.get("address", "")).lower() == a:
                return top, k, v
            if isinstance(v, dict) and str(v.get("sale", "")).lower() == a:
                return top, k, v
    return None, None, None
def upd(addr, **fields):
    top, k, v = find_entry(addr)
    if v is None:
        print("NOT FOUND:", addr); return False
    v.update(fields); v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = "2026-11-13 ~16:35 WIB"
    return True
def vel(prev_total, new_total, prev_rate):
    n = (new_total or 0) - (prev_total or 0)
    rate = round(n / INTERVAL, 2)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return n, rate, ratio, bool(ratio is not None and ratio >= 1.5 and n >= 20)
# Agentx
_, _, ax = find_entry("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
n, rate, ratio, passed = vel(ax.get("totalMinted"), 741, ax.get("previousRatePerMin"))
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", totalMinted=741, freeMinted=741,
    FREE_CAP=1111, MAX_SUPPLY=2222, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=66.7, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1631="Run 1631: totalMinted 738->741 (+3, 0.10/mnt vs prev 0.18 = 0.56x, <20 token) -> velocity GAGAL; free 741/1111 = 66.7% (<70% strong lead); slot terbuka; umur ~17.4 jam (mintOpensAt 2026-11-12 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov. Gate website tetap GAGAL (dilaporkan 08:01 + hot-leg 08:29). TIDAK di-preview/TIDAK di-mint. DIAM.")
# Zero
_, _, z = find_entry("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647")
n, rate, ratio, passed = vel(z.get("totalMinted"), 289, z.get("previousRatePerMin"))
upd("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", totalMinted=289, freeMinted=289,
    FREE_CAP=500, MAX_SUPPLY=10000, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=57.8, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1631="Run 1631: totalMinted 287->289 (+2, 0.07/mnt vs prev 2.42 = 0.03x) -> velocity GAGAL; free 289/500 = 57.8% (<70%); slot TERBUKA; umur ~8.7 jam (mintOpensAt 07:55 WIB 13 Nov) <24 jam. Website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.")
# RoyalRush (velocity on freeMinted, same basis as 1601 note)
_, _, rr = find_entry("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3")
n, rate, ratio, passed = vel(rr.get("freeMinted"), 809, rr.get("currentRatePerMin"))
upd("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3", totalSupply=829, freeMinted=809,
    freeRemaining=191, paidMinted=20, mintOpen=1, balanceOf_user=0,
    freePct=80.9, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1631="Run 1631: freeMinted 796->809/1000 = 80.9% (+13, 0.43/mnt vs rate 1601 0.73 = 0.59x) -> velocity GAGAL; umur TETAP UNVERIFIED + X UNVERIFIED -> BUKAN strong lead walau >70%. Slot terbuka. DIAM.")
# AgentLabs
_, _, al = find_entry("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
n, rate, ratio, passed = vel(al.get("totalSpecimens"), 2261, al.get("previousRatePerMin"))
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7", totalSpecimens=2261,
    currentExperiment=2, genesisOpen=1, balanceOf_user=0,
    mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1631="Run 1631: totalSpecimens 2246->2261 (+15, 0.50/mnt vs prev 3.298 = 0.15x, <20 token) -> velocity GAGAL; experiment 2 berjalan; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")
# OBFG track-C
upd("0x5314071bba19943f58347ba5dec423e5032a6818", totalSupply=686, totalMinted=686,
    freeMinted=686, FREE_SUPPLY=1230, saleOpen=1, freeAvailable_user=1, balanceOf_user=0,
    freePct=55.8,
    runNote1631="Run 1631: 685->686/1230 = 55.8% (+1), umur ~20.6 jam (saleStart 2026-11-12 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov, slot terbuka (freeAvailable=1). Gate-blocked SUDAH dilaporkan 12 Nov. DIAM.")
# BC1B
upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053", freeCount=469, balanceOf_user=0,
    runNote1631="Run 1631: freeCount 467->469 (15.6%). DIAM.")
# MECHA
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", totalMinted=1930, freeClaimed=1929,
    runNote1631="Run 1631: freeClaimed 1928->1929/4444 = 43.4% (<50%). DIAM.")
# Pickgrid
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0", freeMinted=216, FREE_CAP=300,
    runNote1631="Run 1631: freeMinted 216 FLAT, umur UNVERIFIED. DIAM.")
# OLIVER
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810", totalSupply=995, freeMinted=945,
    freeRemaining=55, FREE_MAX=1000, MAX_SUPPLY=5000, mintOpen=1, balanceOf_user=0,
    freePct=94.5,
    runNote1631="Run 1631: totalSupply 992->995, freeMinted 942->945/1000 = 94.5% (+3), freeRemaining 55. Umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")
# Slate - early lead, first rate baseline now computable
_, _, sl = find_entry("0x5893199322A5300775912ebD236d8f1fEFC700Db")
n, rate, ratio, passed = vel(sl.get("totalMinted"), 41, sl.get("previousRatePerMin"))
upd("0x5893199322A5300775912ebD236d8f1fEFC700Db", totalSupply=41, totalMinted=41,
    freeMinted=40, freeRemaining=440, FREE_SUPPLY=480, FREE_PER_WALLET=1,
    MAX_SUPPLY=800, saleStart=1794559857, saleOpen=1, mintOpen=1, isFreeOpen=1,
    balanceOf_user=0, freePct=8.3,
    mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1631="Run 1631: totalSupply 18->41, freeMinted 18->40/480 = 8.3% (+22, 0.73/mnt; baseline rate pertama, TANPA prev rate -> velocity TIDAK lolos sendirian). Umur ~45 mnt (buka 15:50:57 WIB). Website/X UNVERIFIED, slot user UNVERIFIED (freeClaimed view null). BUKAN kandidat (<50%), BUKAN strong lead (<70%). TIDAK di-preview/TIDAK di-mint. DIAM.")
# HIVE, AgentMuse, NOTV, Mossbound, Ochre, OUTY, PX24-group, DragonAgent
upd("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", totalSupply=1263, balanceOf_user=1,
    runNote1631="Run 1631: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("0x779fa133848d23052B7345F63B3b2E5309cd13ed", freeClaimed=357, FREE_SHARES=888,
    bookedOf_user=100000000000000000000000,
    runNote1631="Run 1631: freeClaimed 344->357/888 = 40.2% (+13), bookedOf(user) utuh. DIAM.")
upd("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", totalSupply=0, totalMinted=0,
    FREE_SHARES=2000, freeStart=1794567600,
    runNote1631="Run 1631: 0/2000, freeStart 18:00 WIB 13 Nov - belum buka. DIAM.")
upd("0xe589A94316C68d4A4f008f841Deb7e9612445244", totalSupply=326, totalMinted=326,
    freeMinted=325, freeRemaining=0,
    runNote1631="Run 1631: freeMinted 325/325 = 100% SOLD OUT terkonfirmasi ulang (sudah dilaporkan sekali hot-leg 1444). DIAM.")
upd("0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D", totalSupply=211, totalMinted=211,
    freeMinted=210, freeRemaining=0,
    runNote1631="Run 1631: freeMinted 210/210 = 100% SOLD OUT terkonfirmasi ulang (sudah dilaporkan sekali hot-leg 1519). DIAM.")
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", minted=29, freeSold=29,
    FREE_FEE=100000000000000,
    runNote1631="Run 1631: freeSold 28->29/1500 (+1); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")
upd("0xa545c8726bcf4acf840dac521b369911fe2abc8d", totalSupply=289,
    runNote1631="Run 1631: ME30 totalSupply 288->289 (+1); umur UNVERIFIED. DIAM.")
upd("0x9081f02876c173d0c69f042959cfd0d61c668b17", totalSupply=511,
    runNote1631="Run 1631: SKRR totalSupply 510->511 (+1); umur UNVERIFIED. DIAM.")
upd("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", totalSupply=460,
    runNote1631="Run 1631: CY24 totalSupply 459->460 (+1); umur UNVERIFIED. DIAM.")
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", totalSupply=981,
    runNote1631="Run 1631: DragonAgent totalSupply 974->981 (+7); free views NULL -> free % UNVERIFIED. DIAM.")
upd("0xe712510fcb27935e657e41ebb97982d6b123136c", totalSupply=524,
    MAX_SUPPLY=1731, mintOpen=1, balanceOf_user=0,
    runNote1631="Run 1631: totalSupply 523->524 (+1); umur UNVERIFIED. DIAM.")
# binanceai pending claim (fresh refund fields read this run)
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
pc["launched"] = 0; pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-13 ~16:35 WIB"
pc["runNote1631"] = "Run 1631: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM."
# Violet Waybill - NEW upcoming-prelaunch (feed 1631, S1-shape via ABI, 0 mints)
snap.setdefault("contracts", {})["Violet Waybill"] = {
    "address": "0x36D9A4392E3d9ff05B6929C82D536367E9c1bc8d", "name": "Violet Waybill",
    "symbol": "VLWB",
    "status": "upcoming-prelaunch-2026-11-13",
    "totalSupply": 0, "totalMinted": 0, "freeMinted": 0, "freeRemaining": 0,
    "FREE_SUPPLY": 1230, "FREE_PER_WALLET": 1, "MAX_SUPPLY": 1500,
    "PRICE": 180000000000000, "saleStart": 1794563463, "saleEnd": 1794736263,
    "saleOpen": 0, "mintOpen": 0, "isFreeOpen": 0,
    "agentIdRegistry": 552192074493313695968015109214105588393044541999,
    "freePct": 0.0, "balanceOf_user": 0, "hasAgentId_user": 1,
    "quote_user_1": 0, "freeAvailable_user": 0, "remainingQuota_user": 0,
    "lastReadBlock": BLOCK, "lastReadWib": "2026-11-13 ~16:35 WIB",
    "note": "Run 1631 discovery: Sourcify feed baru (verifiedAt 2026-11-13T09:31:15Z), ABI 77 fns S1-shape (mint/claimFree/mintFree + quote + free views + agentIdRegistry = registry resmi). contractURI base64 TANPA external_link/website. 0 mint = BELUM LAUNCH (saleStart 16:51:03 WIB 13 Nov, buka ~15 mnt lagi) -> upcoming-prelaunch, TIDAK dilaporkan sebagai early lead (first mint belum terverifikasi), TIDAK di-preview/di-mint. Pantau first mint di run berikut.",
    "runNote1631": "Run 1631: ditambahkan sebagai upcoming-prelaunch. 0/1230 free, saleOpen=0, quote(user,1)=0 (belum buka). Website UNVERIFIED, X UNVERIFIED. DIAM."}
snap["last_run"] = "2026-11-13T16:35+07:00"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged, block", BLOCK)
