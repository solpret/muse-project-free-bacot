#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 15:31 WIB.
Fresh reads from run-2026-11-13-1531-verify.json (block 133320439, ~15:33 WIB)
+ discovery (2 new feed contracts: Slate Insignia S1-positive NFT, 0xA100 not
sale-shape) + Slate deep-verify (run-2026-11-13-1531-new5893-views.json) +
binanceai refund-state read (launched=0, isRefundPhase=1, failed=1).
previousRatePerMin stays FROZEN (convention question from run 0931 still
undecided by parent); currentRatePerMin computed per interval (~30 min).
OCMD: SOLD OUT 210/210 - already reported ONCE by hot-leg 1519 (15:23 WIB),
NO re-report here; snapshot status -> sold-out.
Slate Insignia: NEW upcoming (saleStart 15:50:57 WIB, 0 mints) - added to
snapshot as upcoming watchlist item, NOT an early lead (no first mints yet),
NOT a candidate; website unverified (contractURI on-chain, no URL; search A+G
0 hits). No chat report this run (silence rule).
Read-only on-chain; only writes the snapshot. No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-1531.bak")
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-13-1531-verify.json"))
BLOCK = verify.get("block")
INTERVAL = 30  # minutes vs run 1501 reads (~15:04 WIB snapshot)

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
        print("NOT FOUND:", addr, fields.get("name"))
        return False
    v.update(fields)
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = "2026-11-13 ~15:35 WIB"
    return True

def vel(prev_total, new_total, prev_rate):
    n = (new_total or 0) - (prev_total or 0)
    rate = round(n / INTERVAL, 2)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return n, rate, ratio, bool(ratio is not None and ratio >= 1.5 and n >= 20)

# --- Agentx ---
_, _, ax = find_entry("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
n, rate, ratio, passed = vel(ax.get("totalMinted"), 734, ax.get("previousRatePerMin"))
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", totalMinted=734, freeMinted=734,
    FREE_CAP=1111, MAX_SUPPLY=2222, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=66.1, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1531="Run 1531: totalMinted 732->734 (+2, 0.07/mnt vs prev 0.18 = 0.37x, <20 token) -> velocity GAGAL; free 734/1111 = 66.1% (<70% strong lead); slot terbuka; umur ~16.7 jam (mintOpensAt 2026-11-12 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov. Gate website tetap GAGAL (dilaporkan 08:01 + hot-leg 08:29). TIDAK di-preview/TIDAK di-mint. DIAM.")

# --- Zero ---
_, _, z = find_entry("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647")
n, rate, ratio, passed = vel(z.get("totalMinted"), 284, z.get("previousRatePerMin"))
upd("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", totalMinted=284, freeMinted=284,
    FREE_CAP=500, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=56.8, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1531="Run 1531: totalMinted 280->284 (+4) -> velocity GAGAL; free 284/500 = 56.8%; slot TERBUKA; umur ~7.9 jam (mintOpensAt 07:55 WIB) <24 jam; website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.")

# --- Royal Rush Agents ---
_, _, rr = find_entry("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3")
n, rate, _, _ = vel(rr.get("totalSupply"), 794, None)
ratio_bl = round(rate / 7.74, 2) if rate else None
upd("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3", totalSupply=794, totalMinted=794,
    freeMinted=774, freeRemaining=226, FREE_MAX=1000, mintOpen=1, paidMinted=20,
    freeClaimedByAgent_user=0, balanceOf_user=0, freePct=77.4,
    mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio_bl,
    velocityLegPasses=False, intervalMinutes=INTERVAL,
    runNote1531="Run 1531: freeMinted 744->774/1000 = 77.4% (+30, 1.00/mnt vs baseline 7.74 = 0.13x) -> velocity GAGAL (melambat); umur TETAP UNVERIFIED + X UNVERIFIED -> BUKAN strong lead/kandidat walau >70%. Slot terbuka. DIAM.")

# --- Oliver Agents ---
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810", totalSupply=990, freeMinted=940,
    freeRemaining=60, FREE_MAX=1000, mintOpen=1, mintedCount=990, paidMinted=50,
    balanceOf_user=0,
    runNote1531="Run 1531: freeMinted 938->940/1000 = 94.0% (+2); umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")

# --- OBFG (track_c) ---
upd("0x5314071bba19943f58347ba5dec423e5032a6818", totalSupply=683, totalMinted=683,
    freeMinted=683, FREE_SUPPLY=1230, saleOpen=1, freeAvailable_user=1, balanceOf_user=0,
    freePct=55.5,
    runNote1531="Run 1531: 683/1230 = 55.5% (+4); umur ~19.9 jam (saleStart 2026-11-12 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov; slot terbuka; gate-blocked (dilaporkan 12 Nov). DIAM.")

# --- AgentMuse (track_c) ---
upd("0x779fa133848d23052B7345F63B3b2E5309cd13ed", freeClaimed=342, FREE_SHARES=888,
    bookedTotal=34200000000000000000000000, openedAt=0,
    bookedOf_user=100000000000000000000000,
    runNote1531="Run 1531: freeClaimed 336->342/888 = 38.5% (+6); user sudah mint (bookedOf utuh). DIAM.")

# --- AgentLabs ---
_, _, al = find_entry("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
n, rate, ratio, passed = vel(al.get("totalSpecimens"), 2229, al.get("previousRatePerMin"))
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7", totalSpecimens=2229, priceFor_user=0,
    holdsAgentId_user=1, balanceOf_user=0, genesisOpen=1, currentExperiment=2,
    specimensInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1531="Run 1531: totalSpecimens 2219->2229 (+10, 0.33/mnt vs prev 3.298 = 0.10x, <20 token) -> velocity GAGAL; experiment 2 berjalan; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")

# --- OUTY ---
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", minted=27, freeSold=27, paidSold=0,
    FREE_SUPPLY=1500, FREE_FEE=100000000000000, phase=1, freeOpen=1, paidOpen=0,
    freeQuotaOf_user=1, quotaOf_user=10, balanceOf_user=0,
    runNote1531="Run 1531: freeSold 26->27/1500 (+1); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")

# --- MECHA / Pickgrid / PX24-group / HIVE / DragonAgent ---
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", totalMinted=1929, freeClaimed=1928,
    runNote1531="Run 1531: freeClaimed 1928/4444 = 43.4% FLAT (<50%). DIAM.")
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0", freeMinted=216, FREE_CAP=300,
    runNote1531="Run 1531: freeMinted 216/300 FLAT, umur UNVERIFIED. DIAM.")
_, _, px = find_entry("0xe712510fcb27935e657e41ebb97982d6b153136c")
if px is not None:
    px["runNote1531"] = "Run 1531: BACA GAGAL lagi (batch-fail, nilai lama dipertahankan, BUKAN nol)."
    px["lastReadBlock"] = BLOCK; px["lastReadWib"] = "2026-11-13 ~15:35 WIB"
upd("0x9081f02876c173d0c69f042959cfd0d61c668b17", totalSupply=509, MAX_SUPPLY=1682,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1531="Run 1531: SKRR 509 FLAT. DIAM.")
upd("0xa545c8726bcf4acf840dac521b369911fe2abc8d", totalSupply=284, MAX_SUPPLY=1950,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1531="Run 1531: ME30 281->284 (+3). DIAM.")
upd("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", totalSupply=458, MAX_SUPPLY=1703,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1531="Run 1531: CY24 458 FLAT. DIAM.")
upd("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", totalSupply=1263, balanceOf_user=1,
    runNote1531="Run 1531: HIVE totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", totalSupply=972, balanceOf_user=0,
    runNote1531="Run 1531: DragonAgent totalSupply 972 FLAT; free views NULL -> free % UNVERIFIED. DIAM.")

# --- NOTV / BC1B (track_c) ---
_, _, nt = find_entry("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01")
if nt is not None:
    upd("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", totalSupply=0, totalMinted=0,
        FREE_SHARES=2000, freeStart=1794567600,
        runNote1531="Run 1531: totalMinted 0, freeStart 18:00 WIB 13 Nov - belum buka. DIAM.")
_, _, bc = find_entry("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053")
if bc is not None:
    upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053", totalSupply=1000000000000000000000000000,
        freeCount=467, balanceOf_user=0,
        runNote1531="Run 1531: BC1B/RESUME freeCount 467 FLAT. DIAM.")

# --- JNTM sellout confirmed again ---
snap["runNote1531_jntm"] = ("Run 1531: JNTM sellout TERKONFIRMASI ulang (freeClaimed 1000/1000, freeLeft 0, "
    "totalMinted 1193, paidMinted 193); sudah dihapus dari track_c + dicatat di sellouts run 1331. DIAM.")

# --- binanceai.fun pending claim (refund phase unchanged, already reported 2 Nov) ---
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["launched"] = 0; pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-13 ~15:35 WIB"
    pc["runNote1531"] = ("Run 1531: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, "
        "refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov); "
        "tetap pending, TIDAK dilaporkan ulang. DIAM.")

# --- Mossbound Key: SOLD OUT (already reported once by hot-leg 1444) ---
upd("0xe589A94316C68d4A4f008f841Deb7e9612445244", totalSupply=325, totalMinted=325,
    freeMinted=325, freeRemaining=0, FREE_SUPPLY=325, FREE_PER_WALLET=1,
    saleOpen=1, mintOpen=1, isFreeOpen=0, freeAvailable_user=0, balanceOf_user=0,
    MAX_SUPPLY=500, freePct=100.0,
    status="sold-out-2026-11-13",
    runNote1531="Run 1531: SOLD OUT terkonfirmasi ulang (freeMinted 325/325 = 100%). Sellout SUDAH dilaporkan sekali oleh hot-leg 1444 -> TIDAK lapor ulang. DIAM.")

# --- Ochre Medallion (OCMD): SOLD OUT 210/210 - already reported once by hot-leg 1519 ---
upd("0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D", totalSupply=210, totalMinted=210,
    freeMinted=210, freeRemaining=0, FREE_SUPPLY=210, FREE_PER_WALLET=1,
    saleOpen=1, mintOpen=1, isFreeOpen=0, freeAvailable_user=0, balanceOf_user=0,
    MAX_SUPPLY=300, freePct=100.0,
    status="sold-out-2026-11-13",
    mintedInInterval=108, currentRatePerMin=3.6, velocityRatio=1.06,
    velocityLegPasses=False, intervalMinutes=INTERVAL,
    runNote1531=("Run 1531: SOLD OUT 210/210 = 100% (102->210, +108, 3,60/mnt). Sellout SUDAH dilaporkan "
        "sekali oleh hot-leg 1519 pukul 15:23 WIB (#sellout-20261113-1519) -> TIDAK lapor ulang. "
        "Gate website tetap GAGAL (run 1501, A-N) - tidak pernah bisa di-mint. DIAM."))

# --- Slate Insignia (NEW, upcoming/pre-launch): add to snapshot ---
snap.setdefault("contracts", {})["Slate Insignia"] = {
    "address": "0x5893199322A5300775912ebD236d8f1fEFC700Db",
    "name": "Slate Insignia", "symbol": "SLIN",
    "status": "upcoming-prelaunch-2026-11-13",
    "totalSupply": 0, "totalMinted": 0, "freeMinted": 0, "freeRemaining": 0,
    "FREE_SUPPLY": 480, "FREE_PER_WALLET": 1, "MAX_SUPPLY": 800,
    "paidSupply": 320, "price": 1500000000000000, "mintPrice": 1500000000000000,
    "saleStart": 1794559857, "saleEnd": 1794732657,
    "saleOpen": 0, "mintOpen": 0, "isFreeOpen": 0,
    "agentIdRegistry": 552192074493313695968015109214105588393044541999,
    "freeAvailable_user": 0, "freeMintedBy_user": 0, "balanceOf_user": 0,
    "freePct": 0.0, "gate": "website_unverified", "website": None,
    "websiteVerified": False,
    "lastReadBlock": BLOCK, "lastReadWib": "2026-11-13 ~15:35 WIB",
    "runNote1531": ("Run 1531: BARU dari Sourcify feed (verifiedAt 2026-11-13T08:31:09Z). ERC-721 agent-shaped "
        "(Sourcify 84 fns: freeMint/claimFree/mintFree, FREE_SUPPLY 480, isFreeOpen, agentIdRegistry = registry "
        "0x60B926...22F persis). Sale BELUM BUKA: saleStart 15:50:57 WIB 13 Nov (saleEnd 15:50:57 WIB 15 Nov), "
        "totalSupply 0 / freeMinted 0 / saleOpen 0 - BUKAN early lead (belum ada first mint), BUKAN kandidat. "
        "Website UNVERIFIED (contractURI fully on-chain base64 tanpa URL; pencarian alamat + nama proyek 0 hit). "
        "Ditambahkan ke snapshot sebagai upcoming; dibaca ulang tiap run + hot-leg 5 mnt mengawasi pembukaan. DIAM."),
}

# --- Feed-0xA100: checked, not sale-shape ---
snap.setdefault("track_c", {})["Feed-0xA100"] = {
    "address": "0xA1005C6C42ad0505F35f2D21c98B95D45047CdC3",
    "name": "Feed-0xA100",
    "status": "checked-not-sale-shape-2026-11-13",
    "note": ("Run 1531 discovery: Sourcify feed baru (verifiedAt 2026-11-13T08:33:10Z), ABI 6 fns, "
        "S1 false (tanpa mint fn, tanpa quote, tanpa free view, tanpa agent ref) - BUKAN lead track-C / early lead. Dicatat saja."),
    "lastReadWib": "2026-11-13 ~15:35 WIB",
}

# --- Run notes ---
snap["runNote1531"] = ("Run free-mint-search 2026-11-13 15:31 WIB (selesai ~15:45 WIB). TIDAK ADA laporan chat: "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat baru, 0 perubahan track-B. "
    "Ochre Medallion SOLD OUT 210/210 - sudah dilaporkan sekali hot-leg 1519 (15:23 WIB), tidak lapor ulang. "
    "BARU: Slate Insignia (SLIN) 0x5893199322A5300775912ebD236d8f1fEFC700Db - upcoming, sale buka 15:50:57 WIB, "
    "FREE_SUPPLY 480/800, 0 mint, website unverified - masuk snapshot, bukan lead/kandidat. "
    "23 target dibaca segar blok 133320439; PX24 baca gagal lagi (nilai lama dipertahankan). "
    "BinanceAI pending tetap refund phase (launched=0, isRefundPhase=1, failed=1; sudah dilaporkan 2 Nov).")
snap["runNote1531_scan"] = ("Scan leg FAST-FAIL run 1531: Ankr pre-flight HTTP 401 Unauthorized "
    "(outage sejak 2026-11-09 berlanjut; run 1501 juga 401). Watermark TETAP 132512564; "
    "gap ke head terus tumbuh. 5c dilewati (tanpa output scan).")
snap["runNote1531_discovery"] = ("Discovery run 1531: Sourcify feed 20 (verifiedAt 08:16:36-08:33:10Z), 2 baru vs hot-leg-seen: "
    "0x5893 Slate Insignia (S1-positive, NFT) + 0xA100 (6 fns, bukan sale-shape). "
    "Boltbook EN fetch GAGAL (0 byte, bukan 0 alamat); ZH 42.859 B, 14 alamat, 0 baru. "
    "Bridge (read-only): 116 kontrak, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "OCMD + Slate tidak ada di bridge (Slate sudah masuk hot-leg-seen 15:37 sebagai probe-possible-sale).")
snap["runNote1531_slate"] = ("Slate Insignia (SLIN) 0x5893199322A5300775912ebD236d8f1fEFC700Db - verifikasi run 1531: "
    "Sourcify exact (84 fns, nama SLIN); agentIdRegistry = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis; "
    "FREE_SUPPLY 480, FREE_PER_WALLET 1, MAX_SUPPLY 800, paidSupply 320, PRICE/mintPrice 0,0015 BNB; "
    "saleStart 1794559857 = 15:50:57 WIB 13 Nov, saleEnd 15:50:57 WIB 15 Nov; saleOpen/mintOpen/isFreeOpen = 0; "
    "totalSupply/totalMinted/freeMinted = 0 (belum ada mint). contractURI base64 JSON on-chain: deskripsi menyebut "
    "kontrak persis tapi TANPA URL apa pun -> BUKAN bukti website. Pencarian 'Slate Insignia' + alamat kontrak 0 hit "
    "proyek (metode A+G). Website + X UNVERIFIED. Status: upcoming-prelaunch; BUKAN early lead (0 mint), "
    "BUKAN kandidat/strong lead. Hot-leg 1534 sudah mencatatnya di hot-leg-seen (probe-possible-sale, 15:37 WIB); "
    "jalur hot-leg 5 mnt mengawasi pembukaan sale 15:50 WIB.")
snap["runNote1531_ocmd"] = ("Ochre Medallion (OCMD) 0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D - SELLOUT run 1531: "
    "freeMinted 102->210/210 = 100%, freeRemaining 0, isFreeOpen 0, freeAvailable_user 0. "
    "Sellout SUDAH dilaporkan sekali oleh hot-leg 1519 pukul 15:23 WIB (#sellout-20261113-1519; sebelumnya "
    "strong-lead-legs-met-but-gate-blocked dilaporkan hot-leg 1509 pukul 15:13:50 WIB) -> job ini TIDAK lapor ulang. "
    "Status snapshot -> sold-out-2026-11-13. Gate website tetap GAGAL (run 1501, A-N).")
snap["last_run_wib"] = "2026-11-13 ~15:45 WIB"
snap["last_run"] = "2026-11-13T15:45+07:00"
snap["timestamp_wib"] = "2026-11-13 ~15:45 WIB"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
