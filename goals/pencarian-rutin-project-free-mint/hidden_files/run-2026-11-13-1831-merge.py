#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 18:31 WIB.
Reads run-2026-11-13-1831-verify.json (block 133344393),
run-2026-11-13-1831-verify-boltbook.json (block 133344868),
run-2026-11-13-1831-discovery.json.
Updates snapshot in place (backup first). No preview/mint.
Velocity interval: 1801 verify block 133340429 (~18:03) -> 1831 verify block
133344393 (~18:33) = 3964 blocks ~29.7 min; verify-new 133340993 (~18:07) ->
133344868 (~18:37) = 3875 blocks ~29.1 min. Rates computed run-to-run
(delta vs run 1801), same convention as runs 0931-1801 (previousRatePerMin
field frozen in snapshot; see runlog note).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SNAP = BASE + "onchain-snapshot.json"
shutil.copy(SNAP, BASE + "onchain-snapshot-2026-11-13-1831.bak")
s = json.load(open(SNAP))
C = s["contracts"]
TC = s.get("track_c", {})
PC = s.get("pending_claims", {})
V = json.load(open(BASE + "run-2026-11-13-1831-verify.json"))["reads"]
N = json.load(open(BASE + "run-2026-11-13-1831-verify-boltbook.json"))
BLOCK_V = 133344393
BLOCK_N = 133344868

def note1831(e, text):
    if e is None:
        print("note1831 skipped (missing entry)")
        return
    e["runNote1831"] = text

def upd_contract(key, blk=BLOCK_V, **kw):
    e = C.get(key)
    if e is None:
        print("MISSING contract entry:", key)
        return None
    e.update(kw)
    e["lastReadBlock"] = blk
    return e

# ---- verify.py targets (block 133344393) ----
e = upd_contract("HIVE Agents", totalSupply=1263, balanceOf_user=1)
note1831(e, "Run 1831: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
e = upd_contract("AgentLabs", totalSpecimens=2337, currentExperiment=2, genesisOpen=1,
                 genesisStart=1794492248, balanceOf_user=0)
note1831(e, "Run 1831: totalSpecimens 2311->2337 (+26, 0,88/mnt vs prev 0,65 = 1,35x) -> velocity GAGAL (<1,5x); free% UNVERIFIED + X UNVERIFIED + website UNVERIFIED; experiment 2; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")
e = upd_contract("Agentx", totalMinted=757, freeMinted=757, freeClaimed_user=0, mintOpen=1,
                 balanceOf_user=0)
note1831(e, "Run 1831: totalMinted 748->757 (+9, <20) -> velocity GAGAL; free 757/1111 = 68,1% (<70% strong lead); slot terbuka (freeClaimed_user=0); umur ~19,5 jam (mintOpensAt 12 Nov 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov; gate website tetap GAGAL. DIAM.")
e = upd_contract("Zero", totalMinted=296, freeMinted=296, freeClaimed_user=0,
                 balanceOf_user=0)
note1831(e, "Run 1831: totalMinted 296 FLAT -> velocity GAGAL; free 296/500 = 59,2%; slot TERBUKA (freeClaimed_user=0); umur ~10,7 jam (mintOpensAt 07:55 WIB) <24 jam; website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.")
e = upd_contract("Oliver Agents", totalSupply=1010, freeMinted=960, balanceOf_user=0)
note1831(e, "Run 1831: totalSupply 1010 FLAT, freeMinted 960/1000 = 96,0% -> velocity GAGAL; umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")
e = upd_contract("Royal Rush Agents", totalSupply=877, freeMinted=870, freeClaimedByAgent_user=0,
                 freeRemaining=130, paidMinted=20, balanceOf_user=0)
e["velocityLegPasses"] = False
e["currentRatePerMin"] = 0.0
e["previousRatePerMin"] = 1.05
note1831(e, "Run 1831: totalSupply 877 FLAT (+0) -> velocity GAGAL (run 1801 sempat LOLOS, kini 0 token); TETAP BUKAN strong lead/kandidat: umur TETAP UNVERIFIED + X UNVERIFIED walau free 870/1000 = 87,0% + slot terbuka (freeClaimedByAgent=0). DIAM.")
e = upd_contract("Slate Insignia", totalSupply=84, totalMinted=84, freeMinted=83,
                 balanceOf_user=0)
note1831(e, "Run 1831: totalSupply 82->84, freeMinted 81->83/480 = 17,3% (+2, <20) -> velocity GAGAL; umur ~2,9 jam (buka 15:50:57 WIB); website/X UNVERIFIED, slot user UNVERIFIED. BUKAN kandidat (<50%), BUKAN strong lead (<70%). DIAM.")
e = upd_contract("Violet Waybill", totalSupply=110, totalMinted=110, freeMinted=109,
                 freeAvailable_user=1, costOf_user_1=0, balanceOf_user=0)
note1831(e, "Run 1831: totalSupply 93->110, freeMinted 92->109/1230 = 8,9% (+17, <20) -> velocity GAGAL; umur ~1,8 jam (saleStart 16:51 WIB); website/X UNVERIFIED, slot terbuka (freeMintedBy=0, costOf=0). BUKAN kandidat, BUKAN strong lead. DIAM.")
e = upd_contract("MECHA", totalMinted=1934, freeClaimed=1933)
note1831(e, "Run 1831: freeClaimed 1933 FLAT (43,5%). DIAM.")
for k in ("Pickgrid Pickaxe", "Pickgrid"):
    e = C.get(k)
    if e is not None:
        e.update({"freeMinted": 216, "lastReadBlock": BLOCK_V})
        note1831(e, "Run 1831: freeMinted 216 FLAT, umur UNVERIFIED. DIAM.")
e = upd_contract("OUTY", freeSold=35, paidSold=0, FREE_FEE=100000000000000, phase=1,
                 freeOpen=1, freeQuotaOf_user=1, balanceOf_user=0)
note1831(e, "Run 1831: freeSold 35 FLAT/1500; FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")
for k, ts in (("PX24", 524), ("SKRR", 516), ("ME30", 289), ("CY24", 462)):
    e = C.get(k)
    if e is not None:
        e.update({"totalSupply": ts, "balanceOf_user": 0, "lastReadBlock": BLOCK_V})
        note1831(e, f"Run 1831: totalSupply {ts}; umur TETAP UNVERIFIED. DIAM.")
    else:
        print("MISSING contract entry:", k)
for k in ("Dragon Agent", "DragonAgent"):
    e = C.get(k)
    if e is not None:
        e.update({"totalSupply": 983, "balanceOf_user": 0, "lastReadBlock": BLOCK_V})
        note1831(e, "Run 1831: totalSupply 981->983 (+2); umur TETAP UNVERIFIED. DIAM.")
# AgentMuse lives in track_c only (not contracts) - updated in the track_c section below.

# ---- verify-new targets (block 133344868) ----
e = upd_contract("Moss Signal", totalSupply=771, costOf_user_1=0, balanceOf_user=0, blk=BLOCK_N)
note1831(e, "Run 1831: totalSupply 765->771 (+6); 95,0%+ INFERENSI total-supply, TANPA free counter; slot user TERBUKA (costOf=0); website TERVERIFIKASI; umur launch TETAP UNVERIFIED. BUKAN strong lead/kandidat. DIAM.")
e = upd_contract("Agent Bubble", totalSupply=581, totalMinted=581, freeMinted=480,
                 balanceOf_user=0, blk=BLOCK_N)
e["currentRatePerMin"] = 1.96
e["previousRatePerMin"] = 1.63
note1831(e, "Run 1831: totalSupply 524->581, freeMinted 423->480/2222 = 21,6% (+57, 1,96/mnt vs prev 1,63 = 1,20x) -> velocity GAGAL (<1,5x); website TERVERIFIKASI; umur TETAP UNVERIFIED. BUKAN kandidat (<50%), BUKAN strong lead (<70%). DIAM.")
e = upd_contract("Mihao", totalSupply=456, balanceOf_user=0, blk=BLOCK_N)
note1831(e, "Run 1831: totalSupply 451->456 (+5, <20) -> velocity GAGAL; mintStart 14:15:55 WIB -> umur ~4,4 jam <24 jam TERVERIFIKASI; website TERVERIFIKASI; free% UNVERIFIED (PRICE 0,0003 BNB berbayar); slot UNVERIFIED. BUKAN kandidat/strong lead. DIAM.")

# ---- Cinder Crucible: track-C lead, gate still failed (light re-check D+M) ----
e = C.get("Cinder Crucible")
e.update({"totalSupply": 66, "totalMinted": 66, "freeMinted": 66, "freeRemaining": 259,
          "saleOpen": 1, "mintOpen": 1, "isFreeOpen": 1, "freeAvailable_user": 1,
          "freeMintedBy_user": 0, "costOf_user_1": 0, "balanceOf_user": 0,
          "saleEnd": 1794739861, "owner": "0x0000000000000000000000000000000000000000",
          "lastReadBlock": BLOCK_N, "lastReadWib": "2026-11-13 ~18:37 WIB"})
e["status"] = "lead-gate-blocked-2026-11-13"
e["gate"] = "website_failed"
note1831(e, "Run 1831: totalMinted 43->66, freeMinted 66/325 = 20,3% (+23, 0,79/mnt vs prev ~2,69 = 0,29x) -> velocity GAGAL; slot TERBUKA (freeAvailable=1, costOf=0); umur ~1,9 jam <24 jam TERVERIFIKASI; S1-shape LOLOS. GATE WEBSITE TETAP GAGAL (re-check ringan metode D+M run ini: cinder-crucible/cindercrucible .pages.dev HTTP 000, .vercel.app 404/000 - tetap tanpa situs yang mencetak kontrak; gate penuh A-N sudah dicoba run 1801) -> TIDAK di-preview/TIDAK di-mint; sudah dilaporkan sekali run 1801, TIDAK lapor ulang. Catatan: saleEnd segar 1794739861 (tepat 48 jam sesudah saleStart), berbeda dari baca 1801 (1794729109) - flip-flop antar-run, tidak meng-gate apa pun; sale tetap buka.")

# ---- Apex: legs progress - % crosses 50% + velocity passes, X still unverified ----
e = upd_contract("Apex", totalMinted=112, freeMinted=110, mintOpen=1, freeClaimed_user=0,
                 balanceOf_user=0, blk=BLOCK_N)
e["website"] = "https://apex-nft.pages.dev/"
e["ageVerified"] = True
e["freePct"] = 55.0
e["velocityLegPasses"] = True
e["currentRatePerMin"] = 3.33
e["previousRatePerMin"] = 0.43
e["status"] = "watchlist-only-2026-11-13"
e["xNote"] = ("X discussion TETAP UNVERIFIED run 1831 (deep-dive: HTML situs tanpa link x.com/twitter; "
              "metadata /metadata/1 tanpa social/external_url; pencarian alamat kontrak + nama proyek tanpa hit proyek ini).")
note1831(e, "Run 1831: PERUBAHAN KAKI (dicatat, TIDAK dilaporkan - bukan kandidat/strong lead): totalMinted 13->112, freeMinted 110/200 FREE_CAP = 55,0% (+97, 3,33/mnt vs prev ~0,43 = ~7,7x, >=20 token) -> kaki % (>=50%) LOLOS + velocity LOLOS; umur TERVERIFIKASI (first-mint bound run 1801); website TERVERIFIKASI; slot TERBUKA (freeClaimed_user=0). TAPI X discussion TETAP UNVERIFIED (deep-dive run ini: situs tanpa link X, metadata tanpa social, pencarian kontrak+nama tanpa hit) -> BUKAN kandidat; 55,0% <70% -> BUKAN strong lead. Watchlist-only. DIAM (diam per aturan - bukan tier event).")

# ---- contracts-side OBFG ----
o = C.get("OBFG")
if o:
    o.update({"totalSupply": 692, "totalMinted": 692, "freeMinted": 692, "freePct": 56.3,
              "lastReadBlock": BLOCK_V, "lastReadWib": "2026-11-13 ~18:33 WIB"})
    note1831(o, "Run 1831: freeMinted 689->692/1230 = 56,3% (+3, <20) -> velocity GAGAL; umur ~22,5 jam (saleStart 12 Nov 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov; slot terbuka; gate website tetap GAGAL. DIAM.")

# ---- track_c ----
o = TC.get("OBFG")
if o:
    o.update({"totalSupply": 692, "totalMinted": 692, "freeMinted": 692, "freePct": 56.3,
              "saleOpen": 1, "freeAvailable_user": 1, "balanceOf_user": 0,
              "lastReadBlock": BLOCK_V, "lastReadWib": "2026-11-13 ~18:33 WIB"})
    o["runNote1831"] = ("Run 1831: freeMinted 689->692/1230 = 56,3% (+3, 0,10/mnt, velocity GAGAL <20 token), "
                        "umur ~22,5 jam (saleStart 12 Nov 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov, "
                        "slot terbuka (freeAvailable=1). Gate website tetap GAGAL. DIAM.")
n = TC.get("NOTV")
if n:
    n.update({"totalSupply": 0, "totalMinted": 0, "lastReadBlock": BLOCK_V,
              "lastReadWib": "2026-11-13 ~18:33 WIB"})
    n["runNote1831"] = ("Run 1831: freeStart 18:00 WIB 13 Nov SUDAH LEWAT tapi totalMinted MASIH 0 "
                        "(FREE_SHARES 2000); belum ada mint pertama. Umur launch TETAP UNVERIFIED. "
                        "Bukan lead. Cek run berikut.")
am = TC.get("AgentMuse")
if am:
    am.update({"freeClaimed": 395, "lastReadBlock": BLOCK_V, "lastReadWib": "2026-11-13 ~18:33 WIB"})
    am["runNote1831"] = "Run 1831: freeClaimed 389->395/888 = 44,5% (+6). <50% -> BUKAN kandidat. DIAM."
j = TC.get("JNTM")
if j:
    j.update({"freeClaimed": 1000, "totalMinted": 1202, "lastReadBlock": BLOCK_V,
              "lastReadWib": "2026-11-13 ~18:33 WIB"})
    j["runNote1831"] = "Run 1831: SELLOUT terkonfirmasi ulang (freeClaimed 1000/1000); totalMinted 1202 (paid lanjut). Sudah dilaporkan sekali -> TIDAK lapor ulang. DIAM."
bc = TC.get("RESUME-BC1B") or TC.get("BC1B")
if bc:
    bc.update({"freeCount": 469, "lastReadBlock": BLOCK_V, "lastReadWib": "2026-11-13 ~18:33 WIB"})
    bc["runNote1831"] = "Run 1831: freeCount 469 FLAT (15,6%). DIAM."
else:
    print("BC1B track_c key not found; keys:", [k for k in TC if "BC1B" in k or "RESUME" in k])

# ---- feed contracts checked this run (Sourcify feed, new vs hot-leg-seen) ----
feed_checked = {
    "Feed-0x091a": ("0x091aFe448ebe41A0bdbd45c026A5e00B704E8DB7", 29, "mint+quote+agent, tanpa free view"),
    "Feed-0xFa19": ("0xFa196C05919A5d86117997c0B8F2dCc554A7695A", 29, "mint+quote+agent, tanpa free view"),
    "Feed-0xA9Ec": ("0xA9EcdA1C463E6e44D9735A2C5190A6433263f126", 14, "tanpa mint/quote/free/agent"),
}
for key, (addr, nfns, shape) in feed_checked.items():
    TC[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-13",
               "lastReadWib": "2026-11-13 ~18:31 WIB",
               "note": (f"Sourcify feed run 1831 (verifiedAt 11:31-11:33Z): ABI {nfns} fns, {shape} -> "
                        "S1 GAGAL (tanpa free-share view), S2 GAGAL (tanpa free view); ERC-20 totalSupply "
                        "1e27 / 4,196e26 (bukan sale-shape). BUKAN lead, BUKAN early lead "
                        "(tanpa bukti free-mint + first-mint tidak terverifikasi on-chain). Tidak masuk watchlist.")}

# ---- pending_claims: binanceai.fun ----
b = PC.get("binanceai.fun")
if b:
    b.update({"launched": 0, "tokenClaimed_user": 0, "isRefundPhase": 1, "failed": 1,
              "refundClaimed_user": 0, "lastReadWib": "2026-11-13 ~18:33 WIB"})
    b["runNote1831"] = ("Run 1831: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, "
                        "refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). "
                        "Tetap pending, TIDAK dilaporkan ulang. DIAM.")

# ---- top-level ----
s["last_run"] = "2026-11-13T18:33+07:00"
s["last_run_wib"] = "2026-11-13 ~18:33 WIB"
s["last_run_note"] = ("Run 1831: Apex kaki % + velocity LOLOS (55,0%, +97) tapi X TETAP UNVERIFIED -> "
                      "watchlist-only, DIAM (bukan tier event, tidak dilaporkan). Cinder gate tetap GAGAL (re-check D+M). "
                      "OBFG 692/1230 (56,3%), deadline 20:01 WIB; Agentx 757/1111 (68,1%), deadline 23:11 WIB; "
                      "AgentLabs deadline 21:04 WIB. RoyalRush velocity kembali GAGAL (0 token). "
                      "3 kontrak feed baru dicek, bukan sale-shape. Scan leg fast-fail (Ankr 401).")
s["runNote1831"] = ("Run 1831 (blok 133344393 verify / 133344868 verify-new): 0 kandidat baru, 0 strong lead baru/promosi, "
    "0 early lead baru, 0 pending claim baru/dibuka, 0 track-C lead/kandidat baru. Apex: free 13->110/200 = 55,0% "
    "(+97, 3,33/mnt, ~7,7x) -> % + velocity LOLOS, tapi X TETAP UNVERIFIED (deep-dive: situs tanpa link X, metadata "
    "tanpa social, pencarian kontrak+nama tanpa hit) -> BUKAN kandidat; <70% -> BUKAN strong lead; watchlist-only, DIAM. "
    "Cinder Crucible 43->66/325 = 20,3%, gate website TETAP GAGAL (re-check D+M), sudah dilaporkan sekali run 1801. "
    "OBFG 692/1230 (56,3%), deadline 20:01 WIB; Agentx 757/1111 (68,1%), deadline 23:11 WIB; AgentLabs deadline 21:04 WIB; "
    "tidak ada age-exclusion run ini. binanceai refund phase tidak berubah. DIAM selain pencatatan Apex.")
s["runNote1831_scan"] = ("Scan leg FAST-FAIL run 1831: Ankr pre-flight HTTP 401 Unauthorized "
    "(outage sejak 2026-11-09 berlanjut; run 1801 juga 401). Watermark TETAP 132512564; gap ke head "
    "~832.000 blok (head 133344393) - sudah dilaporkan 9 Nov, TIDAK lapor ulang. 5c dilewati (tanpa output scan).")
json.dump(s, open(SNAP, "w"), indent=1)
print("MERGE OK")
