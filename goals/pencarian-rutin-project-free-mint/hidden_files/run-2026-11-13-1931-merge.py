#!/usr/bin/env python3
"""Merge run 1931 fresh reads into onchain-snapshot.json.
Read-only on-chain already done; this only updates snapshot fields + run notes.
Backup onchain-snapshot-2026-11-13-1931.bak made before running."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s = json.load(open(BASE + "onchain-snapshot.json"))
C = s.setdefault("contracts", {})
TC = s.setdefault("track_c", {})
V = json.load(open(BASE + "run-2026-11-13-1931-verify.json"))["reads"]
X = json.load(open(BASE + "run-2026-11-13-1931-verify-extra.json"))["reads"]
BLK = 133352321

def upd(name, **kw):
    e = C.setdefault(name, {})
    e.update(kw)
    return e

def v(name, key, default=None):
    return V.get(name, {}).get("views", {}).get(key, default)

# Track-A watchlist re-reads (verify block 133352321)
upd("HIVE Agents", totalSupply=v("HIVE", "totalSupply"), balanceOf_user=v("HIVE", "balanceOf_user"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931 (blok 133352321): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("Agentx", totalMinted=v("Agentx", "totalMinted"), freeMinted=v("Agentx", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    previousRatePerMin=0.1, currentRatePerMin=0.1,
    runNote1931="Run 1931 (blok 133352321): totalMinted 757->760, freeMinted 760/1111 = 68,4% (+3, ~0,10/mnt vs prev 0,18 = 0,55x) -> velocity GAGAL (<20 token); slot terbuka (freeClaimed_user=0). Umur ~20,4 jam <24 jam, deadline 23:11 WIB. Gate website tetap GAGAL. DIAM.")
upd("Zero", totalMinted=v("Zero", "totalMinted"), freeMinted=v("Zero", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: totalMinted 296->300, freeMinted 300/500 = 60,0% (+4, <20) -> velocity GAGAL; slot TERBUKA (freeClaimed_user=0). Umur ~11,7 jam <24 jam. Website/X UNVERIFIED -> BUKAN kandidat (<50% dan <70%), BUKAN strong lead. DIAM.")
upd("OLIVER", totalSupply=v("OLIVER", "totalSupply"), freeMinted=v("OLIVER", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: totalSupply 1012->1015, freeMinted 965/1000 = 96,5% (+3) -> velocity GAGAL; umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")
upd("AgentLabs", totalSpecimens=v("AgentLabs", "totalSpecimens"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: totalSpecimens 2348->2360 (+12, <20) -> velocity GAGAL. TETAP BUKAN kandidat/promosi: free% UNVERIFIED + X UNVERIFIED + website UNVERIFIED; experiment 2 berjalan; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")
upd("AgentMuse", freeClaimed=v("AgentMuse", "freeClaimed"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: freeClaimed 400->402/888 = 45,3% (+7). <50% -> BUKAN kandidat. DIAM.")
upd("MECHA", totalMinted=v("MECHA", "totalMinted"), freeClaimed=v("MECHA", "freeClaimed"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    previousRatePerMin=0.0, currentRatePerMin=0.67,
    runNote1931="Run 1931: freeClaimed 1933->1953 (+20, ~0,67/mnt) - 20 token TERCAPAI tapi TANPA rate sebelumnya (prev None) -> velocity TIDAK lulus run ini (baseline rate baru tersimpan). Free ~44,0% (<50%) -> BUKAN kandidat. DIAM.")
upd("Pickgrid", freeMinted=v("Pickgrid", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: freeMinted 216 FLAT, umur UNVERIFIED. DIAM.")
upd("BC1B", freeCount=v("BC1B", "freeCount"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: freeCount 470 FLAT (15,7%). DIAM.")
upd("OUTY", freeSold=v("OUTY", "freeSold"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: freeSold 37 FLAT/1500; FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")
upd("Mihao", totalSupply=X["Mihao"]["views"]["totalSupply"],
    lastReadBlock=133352561, lastReadWib="2026-11-13 ~19:35 WIB",
    runNote1931="Run 1931 (blok 133352561): totalSupply 462->471 (+9, <20) -> velocity GAGAL; mintStart 14:15:55 WIB -> umur ~5,3 jam <24 jam TERVERIFIKASI; website TERVERIFIKASI; free% UNVERIFIED (PRICE 0,0003 BNB berbayar); slot UNVERIFIED. BUKAN kandidat/strong lead. DIAM.")
# Track-C / sellouts
obfg = TC.setdefault("OBFG", {})
obfg.update({"totalSupply": 694, "totalMinted": 694, "freeMinted": 694, "freePct": 56.4,
             "lastReadBlock": BLK, "lastReadWib": "2026-11-13 ~19:31 WIB",
             "runNote1931": "Run 1931 (blok 133352321): freeMinted 693->694/1230 = 56,4% (+1, 0,03/mnt) -> velocity GAGAL; umur ~23,5 jam <24 jam, deadline 20:01 WIB 13 Nov (26 mnt lagi saat run); slot terbuka. Gate website tetap GAGAL. DIAM."})
upd("JNTM", freeClaimed=v("JNTM", "freeClaimed"), totalMinted=v("JNTM", "totalMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: SELLOUT terkonfirmasi ulang 1000/1000; sudah dilaporkan sekali -> DIAM.")
upd("Mossbound", totalSupply=v("Mossbound", "totalSupply"), freeMinted=v("Mossbound", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: SELLOUT terkonfirmasi ulang 325/325; sudah dilaporkan sekali -> DIAM.")
upd("Ochre", totalSupply=v("Ochre", "totalSupply"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: SELLOUT terkonfirmasi ulang 210/210; sudah dilaporkan sekali -> DIAM.")
upd("RoyalRush", totalSupply=v("RoyalRush", "totalSupply"), freeMinted=v("RoyalRush", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: totalSupply 879->888, freeMinted 872->881/1000 = 88,1% (+9, <20) -> velocity GAGAL. TETAP BUKAN strong lead/kandidat: umur TETAP UNVERIFIED + X UNVERIFIED walau free >70% + slot terbuka. DIAM.")
upd("Slate Insignia", totalSupply=v("Slate", "totalSupply"), freeMinted=v("Slate", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: totalSupply 85->88, freeMinted 84->87/480 = 18,1% (+3, <20) -> velocity GAGAL. Umur ~3,9 jam. Website/X UNVERIFIED, slot user UNVERIFIED. BUKAN kandidat (<50%), BUKAN strong lead (<70%). DIAM.")
upd("Violet Waybill", totalSupply=v("VioletWaybill", "totalSupply"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: totalSupply 113->119 (+6, <20) -> velocity GAGAL. Umur ~2,8 jam. Website/X UNVERIFIED, slot terbuka (costOf=0). BUKAN kandidat, BUKAN strong lead. DIAM.")
upd("Dragon Agent", totalSupply=v("DragonAgent", "totalSupply"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
    runNote1931="Run 1931: totalSupply 983 FLAT; umur TETAP UNVERIFIED. DIAM.")
for k in ["PX24", "SKRR", "ME30", "CY24"]:
    upd(k, totalSupply=v(k, "totalSupply"), lastReadBlock=BLK, lastReadWib="2026-11-13 ~19:31 WIB",
        runNote1931=f"Run 1931: totalSupply {v(k, 'totalSupply')} FLAT. DIAM.")
# Track-C NOTV (still 0) + Cinder
notv = TC.setdefault("NOTV", {})
notv.update({"totalMinted": 0, "totalSupply": 0, "lastReadBlock": BLK, "lastReadWib": "2026-11-13 ~19:31 WIB",
             "runNote1931": "Run 1931: totalMinted MASIH 0 (FREE_SHARES 2000) - belum ada mint pertama walau freeStart 18:00 WIB sudah lewat. Umur launch TETAP UNVERIFIED. Bukan lead. DIAM."})
upd("Cinder Crucible", totalSupply=X["CinderCrucible"]["views"]["totalSupply"],
    freeMinted=X["CinderCrucible"]["views"]["freeMinted"],
    lastReadBlock=133352561, lastReadWib="2026-11-13 ~19:35 WIB",
    runNote1931="Run 1931 (blok 133352561): totalMinted 81->90, freeMinted 90/325 = 27,7% (+9, <20) -> velocity GAGAL; slot TERBUKA (freeAvailable=1, costOf=0); umur ~2,9 jam (saleStart 17:51:01 WIB) <24 jam. GATE WEBSITE TETAP GAGAL. TIDAK di-preview/TIDAK di-mint. DIAM (sudah dilaporkan sekali).")
# APEX: free pool SOLD OUT (change) - minted-by-user, slot used
upd("APEX", totalMinted=X["Apex"]["views"]["totalMinted"], freeMinted=X["Apex"]["views"]["freeMinted"],
    freeClaimed_user=X["Apex"]["views"]["freeClaimed_user"], balanceOf_user=X["Apex"]["views"]["balanceOf_user"],
    lastReadBlock=133352561, lastReadWib="2026-11-13 ~19:35 WIB",
    runNote1931="Run 1931 (blok 133352561): PERUBAHAN - freeMinted 200/200 FREE_CAP = FREE POOL SOLD OUT (totalMinted 206; run 1901: 170/200). Slot user SUDAH TERPAKAI (freeClaimed_user=1, balanceOf_user=1, #175). Dilaporkan sekali run ini sebagai perubahan sellout; bukan kandidat/lead lagi.")
# Moss Signal + Agent Bubble (verify-extra, not snapshot-tracked before for BUBB)
upd("MossSignal", totalSupply=X["MossSignal"]["views"]["totalSupply"],
    lastReadBlock=133352561, lastReadWib="2026-11-13 ~19:35 WIB",
    runNote1931="Run 1931 (blok 133352561): totalSupply 780->786 (+6); 95,0%+ INFERENSI total-supply, TANPA free counter; slot user TERBUKA (costOf=0); website TERVERIFIKASI; umur launch TETAP UNVERIFIED. BUKAN strong lead/kandidat. DIAM.")
# Track-B pending binanceai (refund phase unchanged)
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
pc.update({"launched": 0, "tokenClaimed_user": 0, "lastReadWib": "2026-11-13 ~19:31 WIB",
           "runNote1931": "Run 1931: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM."})
# Scan state note (fast-fail, watermark unchanged)
st = json.load(open(BASE + "onchain-scan-state.json"))
st["note_1931_scan"] = ("Run 1931: SCAN FAST-FAIL (pre-flight Ankr getLogs HTTP 401 Unauthorized, "
    "bukan timeout seperti run 1901). Outage Ankr sejak 2026-11-09 berlanjut. Watermark TETAP 132512564; "
    "gap ke head ~840.000 blok (head 133352561) - sudah dilaporkan 9 Nov, TIDAK lapor ulang. 5c dilewati (tanpa output scan).")
json.dump(st, open(BASE + "onchain-scan-state.json", "w"), indent=1)
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK")
