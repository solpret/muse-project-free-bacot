#!/usr/bin/env python3
"""Merge run 2001 fresh reads into onchain-snapshot.json.
Read-only on-chain already done; this only updates snapshot fields + run notes.
Backup onchain-snapshot-2026-11-13-2001.bak made before running.
KEY CHANGE: OBFG age-excluded (saleStart 2026-11-12 20:01:16 WIB, read ~20:06 WIB
13 Nov -> age ~24h05m >= 24h, free 696/1230 not sold out) -> removed from track_c."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-2001.bak")
s = json.load(open(BASE + "onchain-snapshot.json"))
C = s.setdefault("contracts", {})
TC = s.setdefault("track_c", {})
V = json.load(open(BASE + "run-2026-11-13-2001-verify.json"))["reads"]
X = json.load(open(BASE + "run-2026-11-13-2001-verify-extra.json"))["reads"]
BLK = 133356621
BLKX = 133356885

def upd(name, **kw):
    e = C.setdefault(name, {})
    e.update(kw)
    return e

def v(name, key, default=None):
    return V.get(name, {}).get("views", {}).get(key, default)

upd("HIVE Agents", totalSupply=v("HIVE", "totalSupply"), balanceOf_user=v("HIVE", "balanceOf_user"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001 (blok 133356621): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("Agentx", totalMinted=v("Agentx", "totalMinted"), freeMinted=v("Agentx", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    previousRatePerMin=0.1, currentRatePerMin=0.125,
    runNote2001="Run 2001 (blok 133356621): totalMinted 760->764, freeMinted 764/1111 = 68,8% (+4, ~0,13/mnt vs prev 0,10 = 1,25x, <20 token) -> velocity GAGAL; slot terbuka (freeClaimed_user=0). Umur ~21 jam <24 jam, deadline 23:11 WIB 13 Nov. Gate website tetap GAGAL. DIAM.")
upd("Zero", totalMinted=v("Zero", "totalMinted"), freeMinted=v("Zero", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: totalMinted 300->302, freeMinted 302/500 = 60,4% (+2, <20) -> velocity GAGAL; slot TERBUKA (freeClaimed_user=0). Umur ~12,2 jam <24 jam. Website/X UNVERIFIED -> BUKAN kandidat, BUKAN strong lead (<70%). DIAM.")
upd("OLIVER", totalSupply=v("OLIVER", "totalSupply"), freeMinted=v("OLIVER", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: totalSupply 1015->1016, freeMinted 965->966/1000 = 96,6% (+1) -> velocity GAGAL; umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")
upd("AgentLabs", totalSpecimens=v("AgentLabs", "totalSpecimens"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: totalSpecimens 2360->2364 (+4, <20) -> velocity GAGAL. TETAP BUKAN kandidat/promosi: free% UNVERIFIED + X UNVERIFIED + website UNVERIFIED; experiment 2 berjalan; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")
upd("AgentMuse", freeClaimed=v("AgentMuse", "freeClaimed"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: freeClaimed 402->405/888 = 45,6% (+3). <50% -> BUKAN kandidat. DIAM.")
upd("MECHA", totalMinted=v("MECHA", "totalMinted"), freeClaimed=v("MECHA", "freeClaimed"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    previousRatePerMin=0.67, currentRatePerMin=0.06,
    runNote2001="Run 2001: freeClaimed 1953->1955 (+2, ~0,06/mnt vs baseline 0,67 = 0,09x) -> velocity GAGAL. Free ~44,0% (<50%) -> BUKAN kandidat. DIAM.")
upd("Pickgrid", freeMinted=v("Pickgrid", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: freeMinted 216 FLAT, umur UNVERIFIED. DIAM.")
upd("BC1B", freeCount=v("BC1B", "freeCount"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: freeCount 470 FLAT (15,7%). DIAM.")
upd("OUTY", freeSold=v("OUTY", "freeSold"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: freeSold 37->38/1500 (+1); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")
upd("Mihao", totalSupply=X["Mihao"]["views"]["totalSupply"],
    lastReadBlock=BLKX, lastReadWib="2026-11-13 ~20:06 WIB",
    runNote2001="Run 2001 (blok 133356885): totalSupply 471->478 (+7, <20) -> velocity GAGAL; mintStart 14:15:55 WIB -> umur ~5,8 jam <24 jam TERVERIFIKASI; website TERVERIFIKASI; free% UNVERIFIED (PRICE 0,0003 BNB berbayar); slot UNVERIFIED. BUKAN kandidat/strong lead. DIAM.")
# OBFG AGE-EXCLUSION: remove from track_c, record evidence
obfg_old = TC.pop("OBFG", None)
s["age_excluded_2001_OBFG"] = {
    "address": "0x5314071bba19943f58347ba5dec423e5032a6818",
    "saleStart": 1794488476, "saleStartWib": "2026-11-12 20:01:16 WIB",
    "freeMinted": 696, "FREE_SUPPLY": 1230, "freePct": 56.6,
    "lastReadBlock": BLK, "lastReadWib": "2026-11-13 ~20:06 WIB",
    "note": "Run 2001: AGE-EXCLUDED - umur ~24 jam 05 mnt (>=24 jam) pada bacaan blok 133356621, free pool 696/1230 BELUM sold out, slot user masih terbuka tapi gate website tetap GAGAL. Dihapus dari track_c; dilaporkan sekali run ini sebagai age-exclusion. Jangan re-add kecuali fase/batch mint baru terverifikasi.",
}
upd("JNTM", freeClaimed=v("JNTM", "freeClaimed"), totalMinted=v("JNTM", "totalMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: SELLOUT terkonfirmasi ulang 1000/1000; sudah dilaporkan sekali -> DIAM.")
upd("Mossbound", totalSupply=v("Mossbound", "totalSupply"), freeMinted=v("Mossbound", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: SELLOUT terkonfirmasi ulang 325/325; sudah dilaporkan sekali -> DIAM.")
upd("Ochre", totalSupply=v("Ochre", "totalSupply"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: SELLOUT terkonfirmasi ulang 210/210; sudah dilaporkan sekali -> DIAM.")
upd("RoyalRush", totalSupply=v("RoyalRush", "totalSupply"), freeMinted=v("RoyalRush", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: freeMinted 881->887/1000 = 88,7% (+6, <20) -> velocity GAGAL. ANOMALI BACAAN: totalSupply 888->884 (TURUN 4) sementara freeMinted naik 6 - diduga inkonsistensi baca RPC, BUKAN burn; freeMinted dipakai sebagai counter. TETAP BUKAN strong lead/kandidat: umur TETAP UNVERIFIED + X UNVERIFIED walau free >70% + slot terbuka. DIAM.")
upd("Slate Insignia", totalSupply=v("Slate", "totalSupply"), freeMinted=v("Slate", "freeMinted"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: totalSupply 88->89, freeMinted 87->88/480 = 18,3% (+1, <20) -> velocity GAGAL. Umur ~4,4 jam. Website/X UNVERIFIED, slot user UNVERIFIED. BUKAN kandidat (<50%), BUKAN strong lead (<70%). DIAM.")
upd("Violet Waybill", totalSupply=v("VioletWaybill", "totalSupply"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: totalSupply 119->122 (+3, <20) -> velocity GAGAL. Umur ~3,3 jam. Website/X UNVERIFIED, slot terbuka (costOf=0). BUKAN kandidat, BUKAN strong lead. DIAM.")
upd("Dragon Agent", totalSupply=v("DragonAgent", "totalSupply"),
    lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
    runNote2001="Run 2001: totalSupply 983->986 (+3, <20) -> velocity GAGAL; umur TETAP UNVERIFIED. DIAM.")
for k in ["PX24", "SKRR", "ME30", "CY24"]:
    upd(k, totalSupply=v(k, "totalSupply"), lastReadBlock=BLK, lastReadWib="2026-11-13 ~20:01 WIB",
        runNote2001=f"Run 2001: totalSupply {v(k, 'totalSupply')} (+{0 if k in ('SKRR','CY24') else 1 if k=='PX24' else 2} vs 1931, <20) -> velocity GAGAL. DIAM.")
notv = TC.setdefault("NOTV", {})
notv.update({"totalMinted": 0, "totalSupply": 0, "lastReadBlock": BLK, "lastReadWib": "2026-11-13 ~20:01 WIB",
             "runNote2001": "Run 2001: totalMinted MASIH 0 (FREE_SHARES 2000) - belum ada mint pertama walau freeStart 18:00 WIB sudah lewat. Umur launch TETAP UNVERIFIED. Bukan lead. DIAM."})
upd("Cinder Crucible", totalSupply=X["CinderCrucible"]["views"]["totalSupply"],
    freeMinted=X["CinderCrucible"]["views"]["freeMinted"],
    lastReadBlock=BLKX, lastReadWib="2026-11-13 ~20:06 WIB",
    runNote2001="Run 2001 (blok 133356885): totalMinted 90->94, freeMinted 94/325 = 28,9% (+4, ~0,13/mnt vs prev 0,30 = 0,42x, <20) -> velocity GAGAL; slot TERBUKA (freeAvailable=1, costOf=0); umur ~2,3 jam (saleStart 17:51:01 WIB) <24 jam. GATE WEBSITE TETAP GAGAL. TIDAK di-preview/TIDAK di-mint. DIAM (sudah dilaporkan sekali).")
upd("APEX", totalMinted=X["Apex"]["views"]["totalMinted"], freeMinted=X["Apex"]["views"]["freeMinted"],
    freeClaimed_user=X["Apex"]["views"]["freeClaimed_user"], balanceOf_user=X["Apex"]["views"]["balanceOf_user"],
    lastReadBlock=BLKX, lastReadWib="2026-11-13 ~20:06 WIB",
    runNote2001="Run 2001 (blok 133356885): freeMinted 200/200 FREE_CAP - FREE POOL TETAP SOLD OUT (totalMinted 206). Slot user SUDAH TERPAKAI (freeClaimed_user=1, balanceOf_user=1, #175). Sudah dilaporkan sekali run 1931 -> DIAM.")
upd("MossSignal", totalSupply=X["MossSignal"]["views"]["totalSupply"],
    lastReadBlock=BLKX, lastReadWib="2026-11-13 ~20:06 WIB",
    runNote2001="Run 2001 (blok 133356885): totalSupply 786->804 (+18, ~0,56/mnt vs prev 0,20 = 2,8x TAPI <20 token) -> velocity GAGAL; 95,0%+ INFERENSI total-supply, TANPA free counter; slot user TERBUKA (costOf=0); website TERVERIFIKASI; umur launch TETAP UNVERIFIED. BUKAN strong lead/kandidat. DIAM.")
upd("AgentBubble", totalSupply=X["AgentBubble"]["views"]["totalSupply"],
    totalMinted=X["AgentBubble"]["views"]["totalMinted"], freeMinted=X["AgentBubble"]["views"]["freeMinted"],
    lastReadBlock=BLKX, lastReadWib="2026-11-13 ~20:06 WIB",
    previousRatePerMin=4.27, currentRatePerMin=5.28,
    runNote2001="Run 2001 (blok 133356885): totalSupply 765->934, freeMinted 664->833 (+169, ~5,28/mnt vs prev 4,27 = 1,24x) -> velocity GAGAL (<1,5x walau >=20 token). TETAP BUKAN kandidat/strong lead: free% UNVERIFIED (tanpa FREE_SUPPLY; 833/2222 MAX = 37,5% dari max, bukan kuota gratis), umur launch TETAP UNVERIFIED, X UNVERIFIED. Website TERVERIFIKASI (agentbubbles.pages.dev). DIAM.")
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
pc.update({"launched": v("BinanceAI-mint", "launched"), "tokenClaimed_user": v("BinanceAI-mint", "tokenClaimed_user"),
           "lastReadWib": "2026-11-13 ~20:01 WIB",
           "runNote2001": "Run 2001: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM."})
# Discovery notes (run-level, top-level keys like prior runs)
s["runNote2001"] = ("Run 2001: 1 PERUBAHAN - OBFG AGE-EXCLUDED (umur ~24j05m, free 696/1230, gate gagal). "
    "0 kandidat/strong/early/track-C baru. APEX tetap sold out 200/200. AgentBubble +169 mint tapi velocity GAGAL (1,24x).")
s["runNote2001_scan"] = ("Run 2001: SCAN FAST-FAIL (pre-flight Ankr getLogs HTTP 401 Unauthorized). "
    "Outage Ankr sejak 2026-11-09 berlanjut. Watermark TETAP 132512564; gap ke head ~844.000 blok (head 133356885) - sudah dilaporkan 9 Nov, TIDAK lapor ulang. 5c dilewati (tanpa output scan).")
s["runNote2001_discovery"] = ("Run 2001: Sourcify feed 20 kontrak, 0 baru vs hot-leg-seen (rentang verifikasi 12:09-12:52 UTC); "
    "Boltbook EN 44.866 B / ZH 43.208 B, 0 alamat baru vs snapshot. Alamat ZH 0xc64da7479c5abc8e6dfadeb4d17502ebcf9837e5 dicek: Sourcify tanpa ABI (match None), "
    "selector-probe: totalSupply/mint/name/symbol ada, TANPA free view, TANPA agent registry -> BUKAN agent-shaped, bukan lead. "
    "Sweep rute 3: Meow Cards (NFT 0xb8164afefc53910d7a74cece15a60a9e0c86089e, totalSupply 1142/10000, balanceOf_user=0, site meow-cards.pages.dev terverifikasi) - "
    "pengumuman proyek 2026-11-10 14:40 UTC menyatakan mint live -> umur ~70 jam >24 jam -> AGE-EXCLUDED (belum pernah dilaporkan, jadi diam per aturan); "
    "Agentic Gangster/STAMP PASS sudah dikenal (free pool habis / sold out). Bridge read-only: 116 kontrak, tidak berubah, tanpa promosi/perubahan.")
st = json.load(open(BASE + "onchain-scan-state.json"))
st["note_2001_scan"] = s["runNote2001_scan"]
json.dump(st, open(BASE + "onchain-scan-state.json", "w"), indent=1)
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK; OBFG removed from track_c:", obfg_old is not None, "| OBFG in track_c now:", "OBFG" in TC)
