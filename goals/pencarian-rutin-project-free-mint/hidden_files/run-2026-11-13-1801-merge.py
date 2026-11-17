#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 18:01 WIB.
Reads run-2026-11-13-1801-verify.json (block 133340429),
run-2026-11-13-1801-verify-boltbook.json (block 133340993),
/tmp/cinder-gate.json (BscScan method-L verdict for Cinder Crucible).
Updates snapshot in place (backup first). No preview/mint.
Velocity interval: 1731 verify block 133336349 (~17:35) -> 1801 verify block
133340429 (~18:03) = 4080 blocks ~30.6 min; verify-new 133336984 (~17:40) ->
133340993 (~18:07) = 4009 blocks ~30.1 min.
"""
import json, os, shutil, sys
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SNAP = BASE + "onchain-snapshot.json"
shutil.copy(SNAP, BASE + "onchain-snapshot-2026-11-13-1801.bak")
s = json.load(open(SNAP))
C = s["contracts"]
TC = s.get("track_c", {})
PC = s.get("pending_claims", {})
V = json.load(open(BASE + "run-2026-11-13-1801-verify.json"))["reads"]
N = json.load(open(BASE + "run-2026-11-13-1801-verify-boltbook.json"))
BLOCK_V = 133340429
BLOCK_N = 133340993
gate = {}
try:
    gate = json.load(open("/tmp/cinder-gate.json"))
except Exception:
    gate = {"verdict": "pending", "note": "BscScan method-L verdict not yet written"}

def note1801(e, text):
    e["runNote1801"] = text

def upd_contract(key, **kw):
    e = C.get(key)
    if e is None:
        print("MISSING contract entry:", key)
        return None
    e.update(kw)
    e["lastReadBlock"] = kw.pop("blk", BLOCK_V)
    return e

# ---- verify.py targets (block 133340429) ----
e = upd_contract("HIVE Agents", totalSupply=1263, balanceOf_user=1, blk=BLOCK_V)
note1801(e, "Run 1801: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
e = upd_contract("AgentLabs", totalSpecimens=2311, currentExperiment=2, genesisOpen=1,
                 genesisStart=1794492248, balanceOf_user=0, blk=BLOCK_V)
note1801(e, "Run 1801: totalSpecimens 2291->2311 (+20, 0.65/mnt vs prev 0.71 = 0.92x) -> velocity GAGAL; free% UNVERIFIED + X UNVERIFIED + website UNVERIFIED; experiment 2; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")
e = upd_contract("Agentx", totalMinted=748, freeMinted=748, freeClaimed_user=0, mintOpen=1,
                 balanceOf_user=0, blk=BLOCK_V)
note1801(e, "Run 1801: totalMinted 746->748 (+2, 0.065/mnt) -> velocity GAGAL; free 748/1111 = 67,3% (<70% strong lead); slot terbuka (freeClaimed_user=0); umur ~19,0 jam (mintOpensAt 12 Nov 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov; gate website tetap GAGAL. DIAM.")
e = upd_contract("Zero", totalMinted=296, freeMinted=296, freeClaimed_user=0,
                 balanceOf_user=0, blk=BLOCK_V)
note1801(e, "Run 1801: totalMinted 294->296 (+2) -> velocity GAGAL; free 296/500 = 59,2%; slot TERBUKA (freeClaimed_user=0); umur ~10,2 jam (mintOpensAt 07:55 WIB) <24 jam; website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.")
e = upd_contract("Oliver Agents", totalSupply=1010, freeMinted=960, balanceOf_user=0, blk=BLOCK_V)
note1801(e, "Run 1801: totalSupply 1008->1010, freeMinted 958->960/1000 = 96,0% (+2, <20) -> velocity GAGAL; umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")
e = upd_contract("Royal Rush Agents", totalSupply=877, freeMinted=870, freeClaimedByAgent_user=0,
                 freeRemaining=130, paidMinted=20, balanceOf_user=0, blk=BLOCK_V)
e["velocityLegPasses"] = True
e["currentRatePerMin"] = 1.05
e["previousRatePerMin"] = 0.44
note1801(e, "Run 1801: totalSupply 845->877 (+32, 1,05/mnt vs prev 0,44 = 2,39x, >=20 token) -> velocity LOLOS. TETAP BUKAN strong lead/kandidat: umur TETAP UNVERIFIED + X UNVERIFIED walau free 870/1000 = 87,0% + slot terbuka (freeClaimedByAgent=0). DIAM.")
e = upd_contract("Slate Insignia", totalSupply=82, totalMinted=82, freeMinted=81,
                 balanceOf_user=0, blk=BLOCK_V)
note1801(e, "Run 1801: totalSupply 64->82, freeMinted 63->81/480 = 16,9% (+18, 0,60/mnt vs prev 0,64 = 0,94x, <20 token) -> velocity GAGAL; umur ~2,4 jam (buka 15:50:57 WIB); website/X UNVERIFIED, slot user UNVERIFIED. BUKAN kandidat (<50%), BUKAN strong lead (<70%). DIAM.")
e = upd_contract("Violet Waybill", totalSupply=93, totalMinted=93, freeMinted=92,
                 freeAvailable_user=1, costOf_user_1=0, balanceOf_user=0, blk=BLOCK_V)
note1801(e, "Run 1801: totalSupply 62->93, freeMinted 61->92/1230 = 7,5% (+31, 1,01/mnt vs prev 1,15 = 0,88x) -> velocity GAGAL; umur ~1,3 jam (saleStart 16:51 WIB); website/X UNVERIFIED, slot terbuka (freeMintedBy=0, costOf=0). BUKAN kandidat, BUKAN strong lead. DIAM.")
e = upd_contract("MECHA", totalMinted=1934, freeClaimed=1933, blk=BLOCK_V)
note1801(e, "Run 1801: freeClaimed 1933 FLAT (43,5%). DIAM.")
for k in ("Pickgrid Pickaxe", "Pickgrid"):
    e = C.get(k)
    if e is not None:
        e.update({"freeMinted": 216, "lastReadBlock": BLOCK_V})
        note1801(e, "Run 1801: freeMinted 216 FLAT, umur UNVERIFIED. DIAM.")
e = upd_contract("OUTY", freeSold=35, paidSold=0, FREE_FEE=100000000000000, phase=1,
                 freeOpen=1, freeQuotaOf_user=1, balanceOf_user=0, blk=BLOCK_V)
note1801(e, "Run 1801: freeSold 34->35/1500 (+1); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")
for k, ts in (("PX24", 524), ("SKRR", 515), ("ME30", 289), ("CY24", 461), ("DragonAgent", 981)):
    e = C.get(k)
    if e is not None:
        e.update({"totalSupply": ts, "balanceOf_user": 0, "lastReadBlock": BLOCK_V})
        note1801(e, f"Run 1801: totalSupply {ts} FLAT; umur TETAP UNVERIFIED. DIAM.")
    else:
        print("MISSING contract entry:", k)

# ---- verify-new targets (block 133340993) ----
e = upd_contract("Moss Signal", totalSupply=765, costOf_user_1=0, balanceOf_user=0, blk=BLOCK_N)
note1801(e, "Run 1801: totalSupply 765 FLAT (95,0% INFERENSI total-supply; TANPA free counter); slot user TERBUKA (costOf=0); website TERVERIFIKASI; umur launch TETAP UNVERIFIED (first-mint via eth_getLogs gagal total run 1731 - Ankr 401 + dataseed tolak range besar). BUKAN strong lead/kandidat. DIAM.")
e = upd_contract("Agent Bubble", totalSupply=524, totalMinted=524, freeMinted=423,
                 balanceOf_user=0, blk=BLOCK_N)
e["currentRatePerMin"] = 1.63
note1801(e, "Run 1801: totalSupply 475->524, freeMinted 374->423/2222 = 19,0% (+49, 1,63/mnt; tanpa prev rate -> baseline, velocity TIDAK lolos sendirian); website TERVERIFIKASI; umur TETAP UNVERIFIED. BUKAN kandidat (<50%), BUKAN strong lead (<70%). DIAM.")
e = upd_contract("Mihao", totalSupply=451, balanceOf_user=0, blk=BLOCK_N)
note1801(e, "Run 1801: totalSupply 438->451 (+13, <20) -> velocity GAGAL; mintStart 14:15:55 WIB -> umur ~3,9 jam <24 jam TERVERIFIKASI; website TERVERIFIKASI; free% UNVERIFIED (PRICE 0,0003 BNB berbayar; free lane mintFree belum diverifikasi); slot UNVERIFIED. BUKAN kandidat/strong lead. DIAM.")

# ---- Cinder Crucible: track-C lead, gate verdict from /tmp/cinder-gate.json ----
e = C.get("Cinder Crucible")
e.update({"totalSupply": 43, "totalMinted": 43, "freeMinted": 43, "freeRemaining": 282,
          "saleOpen": 1, "mintOpen": 1, "isFreeOpen": 1, "freeAvailable_user": 1,
          "freeMintedBy_user": 0, "costOf_user_1": 0, "balanceOf_user": 0,
          "saleEnd": 1794729109, "owner": "0x0000000000000000000000000000000000000000",
          "lastReadBlock": BLOCK_N, "lastReadWib": "2026-11-13 ~18:07 WIB"})
if gate.get("verdict") == "website_failed":
    e["status"] = "lead-gate-blocked-2026-11-13"
    e["gate"] = "website_failed"
    e["gateNote"] = ("Gate GAGAL run 1801: tidak ada website terverifikasi ditemukan metode A-N "
                     "(detail di runlog 1801). TIDAK di-preview/TIDAK di-mint. Dilaporkan sekali sebagai TRACK-C LEAD gate-blocked.")
    note1801(e, "Run 1801: SALE BUKA 17:51:01 WIB (saleStart on-chain); totalMinted 0->43, freeMinted 43/325 = 13,2% (freeRemaining 282); slot TERBUKA (freeAvailable=1, freeMintedBy=0, costOf=0, hasAgentId=1); umur ~16 mnt <24 jam TERVERIFIKASI; S1-shape LOLOS. TRACK-C LEAD tapi GATE WEBSITE GAGAL (metode A-N, lihat runlog) -> TIDAK di-preview/TIDAK di-mint; dilaporkan sekali sebagai lead gate-blocked.")
elif gate.get("verdict") == "website_verified":
    e["status"] = "lead-website-verified-2026-11-13"
    e["gate"] = "website_verified"
    e["website"] = gate.get("website")
    note1801(e, "Run 1801: SALE BUKA 17:51:01 WIB; freeMinted 43/325 = 13,2%; slot TERBUKA; umur <24 jam TERVERIFIKASI; S1-shape LOLOS; website TERVERIFIKASI: " + str(gate.get("website")) + ". TRACK-C LEAD - eksekusi di bawah TRACK-C LEAD DIRECT MINT menunggu audit + preview (lihat runlog).")
else:
    e["status"] = "lead-gate-pending-2026-11-13"
    note1801(e, "Run 1801: SALE BUKA 17:51:01 WIB; freeMinted 43/325 = 13,2%; slot TERBUKA; umur <24 jam TERVERIFIKASI; S1-shape LOLOS. Gate verdict BELUM final (BscScan method-L pending) - TIDAK di-preview/TIDAK di-mint run ini.")

# ---- Apex: website VERIFIED (apex-nft.pages.dev prints exact contract), age VERIFIED via first-mint bound ----
e = upd_contract("Apex", totalMinted=13, freeMinted=13, mintOpen=1, freeClaimed_user=0,
                 balanceOf_user=0, blk=BLOCK_N)
e["website"] = "https://apex-nft.pages.dev/"
e["ageVerified"] = True
e["ageNote"] = ("First mint terverifikasi on-chain run 1801: totalMinted 0 (blok 133336984, "
                "~17:40 WIB) -> 13 (blok 133340993, ~18:07 WIB); mint pertama dalam jendela "
                "~17:40-18:07 WIB 13 Nov -> umur <1 jam <24 jam TERVERIFIKASI.")
note1801(e, "Run 1801: LAUNCHED (totalMinted 0->13, freeMinted 13/200 FREE_CAP = 6,5%); website TERVERIFIKASI (apex-nft.pages.dev mencetak kontrak persis, HTTP 200); umur TERVERIFIKASI via first-mint bound (<1 jam). S1 GAGAL (tanpa quote), S2 belum terbukti; free% 6,5% <50%/<70%, X UNVERIFIED -> BUKAN kandidat/strong lead/lead track-C. Watchlist-only. DIAM.")

# ---- track_c ----
o = TC.get("OBFG")
if o:
    o.update({"totalSupply": 689, "totalMinted": 689, "freeMinted": 689, "freePct": 56.0,
              "saleOpen": 1, "freeAvailable_user": 1, "balanceOf_user": 0,
              "lastReadBlock": BLOCK_V, "lastReadWib": "2026-11-13 ~18:03 WIB"})
    o["runNote1801"] = ("Run 1801: freeMinted 688->689/1230 = 56,0% (+1, 0,033/mnt, velocity GAGAL <20 token), "
                        "umur ~22,0 jam (saleStart 12 Nov 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov, "
                        "slot terbuka (freeAvailable=1). Gate website tetap GAGAL. DIAM.")
n = TC.get("NOTV")
if n:
    n.update({"totalSupply": 0, "totalMinted": 0, "lastReadBlock": BLOCK_V,
              "lastReadWib": "2026-11-13 ~18:03 WIB"})
    n["runNote1801"] = ("Run 1801: freeStart 18:00 WIB 13 Nov SUDAH LEWAT tapi totalMinted MASIH 0 "
                        "(FREE_SHARES 2000); belum ada mint pertama. Umur launch TETAP UNVERIFIED. "
                        "Bukan lead. Cek run berikut.")
am = TC.get("AgentMuse")
if am:
    am.update({"freeClaimed": 389, "lastReadBlock": BLOCK_V, "lastReadWib": "2026-11-13 ~18:03 WIB"})
    am["runNote1801"] = "Run 1801: freeClaimed 379->389/888 = 43,8% (+10). <50% -> BUKAN kandidat. DIAM."
j = TC.get("JNTM")
if j:
    j.update({"freeClaimed": 1000, "totalMinted": 1202, "lastReadBlock": BLOCK_V,
              "lastReadWib": "2026-11-13 ~18:03 WIB"})
    j["runNote1801"] = "Run 1801: SELLOUT terkonfirmasi ulang (freeClaimed 1000/1000); totalMinted 1202 (paid lanjut). Sudah dilaporkan sekali -> TIDAK lapor ulang. DIAM."
bc = TC.get("RESUME-BC1B") or TC.get("BC1B")
if bc:
    bc.update({"freeCount": 469, "lastReadBlock": BLOCK_V, "lastReadWib": "2026-11-13 ~18:03 WIB"})
    bc["runNote1801"] = "Run 1801: freeCount 469 FLAT (15,6%). DIAM."
else:
    print("BC1B track_c key not found; keys:", [k for k in TC if "BC1B" in k or "RESUME" in k])

# ---- pending_claims: binanceai.fun ----
b = PC.get("binanceai.fun")
if b:
    b.update({"launched": 0, "tokenClaimed_user": 0, "isRefundPhase": 1, "failed": 1,
              "refundClaimed_user": 0, "lastReadWib": "2026-11-13 ~18:03 WIB"})
    b["runNote1801"] = ("Run 1801: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, "
                        "refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). "
                        "Tetap pending, TIDAK dilaporkan ulang. DIAM.")

# ---- top-level ----
s["last_run"] = "2026-11-13T18:03+07:00"
s["last_run_wib"] = "2026-11-13 ~18:03 WIB"
s["last_run_note"] = ("Run 1801: " + ("Cinder Crucible TRACK-C LEAD gate-blocked (dilaporkan sekali); "
                     if gate.get("verdict") == "website_failed" else
                     "Cinder Crucible TRACK-C LEAD, gate " + str(gate.get("verdict")) + "; ") +
                     "Apex website+umur terverifikasi (watchlist-only); RoyalRush velocity lolos tapi umur/X unverified; "
                     "lainnya diam. Scan leg fast-fail (Ankr 401).")
s["runNote1801"] = ("Run 1801 (blok 133340429 verify / 133340993 verify-new): " +
    ("Cinder Crucible TRACK-C LEAD gate-blocked, dilaporkan sekali. " if gate.get("verdict") == "website_failed" else "") +
    "Apex website + umur terverifikasi (watchlist-only, bukan lead). RoyalRush velocity LOLOS (+32, 2,39x) tapi umur + X unverified -> tanpa promosi. "
    "OBFG 689/1230 (56,0%), deadline 20:01 WIB; Agentx 748/1111 (67,3%), deadline 23:11 WIB; AgentLabs deadline 21:04 WIB. "
    "NOTV freeStart 18:00 lewat, totalMinted masih 0. binanceai refund phase tidak berubah. DIAM selain Cinder.")
s["runNote1801_scan"] = ("Scan leg FAST-FAIL run 1801: Ankr pre-flight HTTP 401 Unauthorized "
    "(outage sejak 2026-11-09 berlanjut; run 1731 juga 401). Watermark TETAP 132512564; gap ke head "
    "~828.000 blok (head 133340429) - sudah dilaporkan 9 Nov, TIDAK lapor ulang. 5c dilewati (tanpa output scan).")
json.dump(s, open(SNAP, "w"), indent=1)
print("MERGE OK; gate verdict:", gate.get("verdict"))
