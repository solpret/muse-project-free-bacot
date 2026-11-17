#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 16:01 WIB.
Fresh reads run-2026-11-13-1601-verify.json (block 133324418, ~16:03 WIB)
+ discovery (feed 20, 1 new 0xb153 checked-not-sale-shape; Boltbook EN+ZH 0 new)
+ binanceai refund-state re-read (launched=0, isRefundPhase=1, failed=1, unchanged).
previousRatePerMin stays FROZEN (convention question from run 0931 still undecided).
Slate Insignia: FIRST MINTS verified on-chain this run (18/480, opened 15:50:57 WIB)
-> EARLY LEAD, reported once this run (first 30-min run to verify first mints;
added 1531 as upcoming-prelaunch with 0 mints, never reported before).
Read-only on-chain; only writes the snapshot. No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-1601.bak")
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-13-1601-verify.json"))
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
    v["lastReadWib"] = "2026-11-13 ~16:05 WIB"
    return True
def vel(prev_total, new_total, prev_rate):
    n = (new_total or 0) - (prev_total or 0)
    rate = round(n / INTERVAL, 2)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return n, rate, ratio, bool(ratio is not None and ratio >= 1.5 and n >= 20)
# Agentx
_, _, ax = find_entry("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
n, rate, ratio, passed = vel(ax.get("totalMinted"), 738, ax.get("previousRatePerMin"))
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", totalMinted=738, freeMinted=738,
    FREE_CAP=1111, MAX_SUPPLY=2222, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=66.4, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1601="Run 1601: totalMinted 734->738 (+4, 0.13/mnt vs prev 0.18 = 0.74x, <20 token) -> velocity GAGAL; free 738/1111 = 66.4% (<70% strong lead); slot terbuka; umur ~16.9 jam (mintOpensAt 2026-11-12 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov. Gate website tetap GAGAL (dilaporkan 08:01 + hot-leg 08:29). TIDAK di-preview/TIDAK di-mint. DIAM.")
# Zero
_, _, z = find_entry("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647")
n, rate, ratio, passed = vel(z.get("totalMinted"), 287, z.get("previousRatePerMin"))
upd("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", totalMinted=287, freeMinted=287,
    FREE_CAP=500, MAX_SUPPLY=10000, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=57.4, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1601="Run 1601: totalMinted 284->287 (+3, 0.10/mnt vs prev 2.42 = 0.04x) -> velocity GAGAL; free 287/500 = 57.4% (<70%); slot TERBUKA; umur ~8.2 jam (mintOpensAt 07:55 WIB 13 Nov) <24 jam. Website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.")
# RoyalRush (2e34)
_, _, rr = find_entry("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3")
n, rate, ratio, passed = vel(rr.get("totalMinted"), 816, rr.get("currentRatePerMin"))
upd("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3", totalSupply=816, freeMinted=796,
    freeRemaining=204, paidMinted=20, mintOpen=1, balanceOf_user=0,
    freePct=79.6, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1601="Run 1601: freeMinted 774->796/1000 = 79.6% (+22, 0.73/mnt vs rate 1531 1.00 = 0.73x) -> velocity GAGAL; umur TETAP UNVERIFIED + X UNVERIFIED -> BUKAN strong lead walau >70%. Slot terbuka. DIAM.")
# AgentLabs
_, _, al = find_entry("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
n, rate, ratio, passed = vel(al.get("totalSpecimens"), 2246, al.get("previousRatePerMin"))
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7", totalSpecimens=2246,
    currentExperiment=2, genesisOpen=1, balanceOf_user=0,
    mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1601="Run 1601: totalSpecimens 2229->2246 (+17, 0.57/mnt vs prev 3.298 = 0.17x, <20 token) -> velocity GAGAL; experiment 2 berjalan; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")
# OBFG track-C
_, _, ob = find_entry("0x5314071bba19943f58347ba5dec423e5032a6818")
upd("0x5314071bba19943f58347ba5dec423e5032a6818", totalSupply=685, totalMinted=685,
    freeMinted=685, FREE_SUPPLY=1230, saleOpen=1, freeAvailable_user=1, balanceOf_user=0,
    freePct=55.7,
    runNote1601="Run 1601: 683->685/1230 = 55.7% (+2), umur ~20.0 jam (saleStart 2026-11-12 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov, slot terbuka (freeAvailable=1). Gate-blocked SUDAH dilaporkan 12 Nov. DIAM.")
# BC1B
upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053", freeCount=467, balanceOf_user=0,
    runNote1601="Run 1601: freeCount 467 FLAT (15.6%). DIAM.")
# MECHA
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", totalMinted=1929, freeClaimed=1928,
    runNote1601="Run 1601: freeClaimed 1928/4444 = 43.4% FLAT (<50%). DIAM.")
# Pickgrid
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0", freeMinted=216, FREE_CAP=300,
    runNote1601="Run 1601: freeMinted 216 FLAT, umur UNVERIFIED. DIAM.")
# OLIVER
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810", totalSupply=992, freeMinted=942,
    freeRemaining=58, FREE_MAX=1000, MAX_SUPPLY=5000, mintOpen=1, balanceOf_user=0,
    runNote1601="Run 1601: totalSupply 990->992, freeMinted 938->942/1000 = 94.2% (+2), freeRemaining 58. Umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")
# Slate - EARLY LEAD this run
upd("0x5893199322A5300775912ebD236d8f1fEFC700Db", totalSupply=18, totalMinted=18,
    freeMinted=18, freeRemaining=462, FREE_SUPPLY=480, FREE_PER_WALLET=1,
    MAX_SUPPLY=800, saleStart=1794559857, saleOpen=1, mintOpen=1, isFreeOpen=1,
    balanceOf_user=0, status="early-lead-reported-2026-11-13",
    freePct=3.75,
    runNote1601="Run 1601: EARLY LEAD dilaporkan sekali. First mints TERVERIFIKASI on-chain run ini: totalSupply/freeMinted 0->18/480 = 3.75% (buka 15:50:57 WIB 13 Nov, saleStart on-chain; umur ~14 mnt <24 jam). Agent-shaped (84 fns, freeMint/claimFree/mintFree, FREE_SUPPLY 480, agentIdRegistry = registry resmi). Website UNVERIFIED (run 1531: contractURI on-chain base64 tanpa URL; pencarian alamat + nama 0 hit); X UNVERIFIED; slot user UNVERIFIED (freeClaimed(address) view null, balanceOf user 0). BUKAN kandidat (<50%), BUKAN strong lead (<70%). TIDAK di-preview/TIDAK di-mint.")
# HIVE, AgentMuse, NOTV, JNTM, Mossbound, Ochre, OUTY, PX24-group, DragonAgent
upd("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", totalSupply=1263, balanceOf_user=1,
    runNote1601="Run 1601: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("0x779fa133848d23052B7345F63B3b2E5309cd13ed", freeClaimed=344, FREE_SHARES=888,
    bookedOf_user=100000000000000000000000,
    runNote1601="Run 1601: freeClaimed 344/888 = 38.8% FLAT, bookedOf(user) utuh. DIAM.")
upd("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", totalSupply=0, totalMinted=0,
    FREE_SHARES=2000, freeStart=1794567600,
    runNote1601="Run 1601: 0/2000, freeStart 18:00 WIB 13 Nov - belum buka. DIAM.")
upd("0xe589A94316C68d4A4f008f841Deb7e9612445244", totalSupply=326, totalMinted=326,
    freeMinted=325, freeRemaining=0,
    runNote1601="Run 1601: freeMinted 325/325 = 100% SOLD OUT terkonfirmasi ulang (sudah dilaporkan sekali hot-leg 1444). DIAM.")
upd("0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D", totalSupply=211, totalMinted=211,
    freeMinted=210, freeRemaining=0,
    runNote1601="Run 1601: freeMinted 210/210 = 100% SOLD OUT terkonfirmasi ulang (sudah dilaporkan sekali hot-leg 1519). DIAM.")
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", minted=28, freeSold=28,
    FREE_FEE=100000000000000,
    runNote1601="Run 1601: freeSold 27->28/1500 (+1); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")
upd("0xa545c8726bcf4acf840dac521b369911fe2abc8d", totalSupply=288,
    runNote1601="Run 1601: ME30 totalSupply 284->288 (+4); umur UNVERIFIED. DIAM.")
upd("0x9081f02876c173d0c69f042959cfd0d61c668b17", totalSupply=510,
    runNote1601="Run 1601: SKRR totalSupply 509->510 (+1); umur UNVERIFIED. DIAM.")
upd("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", totalSupply=459,
    runNote1601="Run 1601: CY24 totalSupply 458->459 (+1); umur UNVERIFIED. DIAM.")
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", totalSupply=974,
    runNote1601="Run 1601: DragonAgent totalSupply 972->974 (+2); free views NULL -> free % UNVERIFIED. DIAM.")
# PX24 batch-fail again: retain old values, note only
px24 = json.load(open(BASE + "run-2026-11-13-1601-px24.json"))
upd("0xe712510fcb27935e657e41ebb97982d6b123136c", totalSupply=px24.get("totalSupply"),
    MAX_SUPPLY=px24.get("MAX_SUPPLY"), mintOpen=px24.get("mintOpen"), balanceOf_user=0,
    runNote1601="Run 1601: totalSupply 522->523 (+1); umur UNVERIFIED. KOREKSI BUG: skrip verify 1531/1601 memakai alamat PX24 salah (...153136c) sehingga baca selalu gagal; alamat benar dari snapshot ...123136c terbaca normal run ini. DIAM.")
# binanceai pending claim
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
pc["launched"] = 0; pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-13 ~16:05 WIB"
pc["runNote1601"] = "Run 1601: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM."
# Feed-0xb153 checked
snap.setdefault("track_c", {})["Feed-0xb153"] = {
    "address": "0xb153deE2AF7107949bEed51A82fF70d7e380fdCD", "name": "Feed-0xb153",
    "status": "checked-not-sale-shape-2026-11-13",
    "note": "Run 1601 discovery: Sourcify feed baru (verifiedAt 2026-11-13T09:03:42Z), ABI 11 fns, TANPA mint/quote/free view/agent ref. GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja.",
    "lastReadWib": "2026-11-13 ~16:05 WIB"}
snap["last_run"] = "2026-11-13T16:05+07:00"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged, block", BLOCK)
