#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 14:31 WIB.
Fresh reads from run-2026-11-13-1431-verify.json (block 133312513, ~14:33 WIB)
+ discovery + new-contract probe (Ochre Medallion OCMD, sale opens 14:51 WIB).
previousRatePerMin stays FROZEN (convention question from run 0931 still
undecided by parent); currentRatePerMin computed per interval (~31 min).
Mossbound velocity: previous rate = run 1401 first rate 2.8/min (recorded as
currentRatePerMin in 1401); 6.90/2.8 = 2.46x AND 214 tokens -> velocity PASSES
this run, but gate still FAILED and 70% crossing already reported once by
hot-leg 1424 (14:27 WIB) -> NO re-report; sellout not yet (24 remaining).
Read-only on-chain; only writes the snapshot. No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-1431.bak")
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-13-1431-verify.json"))
BLOCK = verify.get("block")
INTERVAL = 31  # minutes vs run 1401 reads (~14:02-14:10 WIB snapshot)

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
    v["lastReadWib"] = "2026-11-13 ~14:34 WIB"
    return True

def vel(prev_total, new_total, prev_rate):
    n = (new_total or 0) - (prev_total or 0)
    rate = round(n / INTERVAL, 2)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return n, rate, ratio, bool(ratio is not None and ratio >= 1.5 and n >= 20)

# --- Agentx ---
_, _, ax = find_entry("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
n, rate, ratio, passed = vel(ax.get("totalMinted"), 724, ax.get("previousRatePerMin"))
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", totalMinted=724, freeMinted=724,
    FREE_CAP=1111, MAX_SUPPLY=2222, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=65.2, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1431="Run 1431: totalMinted 717->724 (+7, 0.23/mnt vs prev 0.18 = 1.26x, <20 token) -> velocity GAGAL; free 724/1111 = 65.2% (<70% strong lead); slot terbuka; umur ~15.4 jam (mintOpensAt 2026-11-12 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov. Gate website tetap GAGAL (dilaporkan 08:01 + hot-leg 08:29). TIDAK di-preview/TIDAK di-mint. DIAM.")

# --- Zero ---
_, _, z = find_entry("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647")
n, rate, ratio, passed = vel(z.get("totalMinted"), 279, z.get("previousRatePerMin"))
upd("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", totalMinted=279, freeMinted=279,
    FREE_CAP=500, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=55.8, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1431="Run 1431: totalMinted 273->279 (+6, 0.19/mnt vs prev 2.42 = 0.08x, <20 token) -> velocity GAGAL; free 279/500 = 55.8%; slot TERBUKA; umur ~6.7 jam (mintOpensAt 07:55 WIB) <24 jam; website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.")

# --- Royal Rush Agents ---
_, _, rr = find_entry("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3")
n, rate, _, _ = vel(rr.get("totalSupply"), 662, None)
ratio_bl = round(rate / 7.74, 2) if rate else None
upd("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3", totalSupply=662, totalMinted=662,
    freeMinted=642, freeRemaining=358, FREE_MAX=1000, mintOpen=1, paidMinted=20,
    freeClaimedByAgent_user=0, balanceOf_user=0, freePct=64.2,
    mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio_bl,
    velocityLegPasses=False, intervalMinutes=INTERVAL,
    runNote1431="Run 1431: freeMinted 550->642/1000 = 64.2% (+92, 2.97/mnt vs baseline 7.74 = 0.38x) -> velocity GAGAL (melambat vs baseline; previousRate None); umur UNVERIFIED + X UNVERIFIED -> BUKAN kandidat; <70% bukan strong lead. Slot terbuka. DIAM.")

# --- Oliver Agents ---
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810", totalSupply=986, freeMinted=936,
    freeRemaining=64, FREE_MAX=1000, mintOpen=1, mintedCount=986, paidMinted=50,
    balanceOf_user=0,
    runNote1431="Run 1431: freeMinted 934->936/1000 = 93.6% (+2); umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")

# --- OBFG (track_c) ---
upd("0x5314071bba19943f58347ba5dec423e5032a6818", totalSupply=676, totalMinted=676,
    freeMinted=676, FREE_SUPPLY=1230, saleOpen=1, freeAvailable_user=1, balanceOf_user=0,
    freePct=55.0,
    runNote1431="Run 1431: 676/1230 = 55.0% FLAT; umur ~18.6 jam (saleStart 2026-11-12 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov; slot terbuka; gate-blocked (dilaporkan 12 Nov). DIAM.")

# --- AgentMuse (track_c) ---
_, _, am = find_entry("0x779fa133848d23052B7345F63B3b2E5309cd13ed")
if am is not None:
    upd("0x779fa133848d23052B7345F63B3b2E5309cd13ed", freeClaimed=329, FREE_SHARES=888,
        bookedTotal=32900000000000000000000000, openedAt=0,
        bookedOf_user=100000000000000000000000,
        runNote1431="Run 1431: freeClaimed 319->329/888 = 37.0% (+10); user sudah mint (bookedOf utuh). DIAM.")
else:
    print("AgentMuse not found by address")

# --- AgentLabs ---
_, _, al = find_entry("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
n, rate, ratio, passed = vel(al.get("totalSpecimens"), 2200, al.get("previousRatePerMin"))
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7", totalSpecimens=2200, priceFor_user=0,
    holdsAgentId_user=1, balanceOf_user=0, genesisOpen=1, currentExperiment=2,
    specimensInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1431="Run 1431: totalSpecimens 2181->2200 (+19, 0.61/mnt vs prev 3.298 = 0.19x, <20 token) -> velocity GAGAL; experiment 2 berjalan; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")

# --- OUTY ---
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", minted=26, freeSold=26, paidSold=0,
    FREE_SUPPLY=1500, FREE_FEE=100000000000000, phase=1, freeOpen=1, paidOpen=0,
    freeQuotaOf_user=1, quotaOf_user=10, balanceOf_user=0,
    runNote1431="Run 1431: freeSold 25->26/1500 (+1); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")

# --- MECHA / Pickgrid / PX24-group / HIVE / DragonAgent ---
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", totalMinted=1925, freeClaimed=1924,
    runNote1431="Run 1431: freeClaimed 1924/4444 = 43.2% FLAT (<50%). DIAM.")
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0", freeMinted=216, FREE_CAP=300,
    runNote1431="Run 1431: freeMinted 216/300 FLAT, umur UNVERIFIED. DIAM.")
_, _, px = find_entry("0xe712510fcb27935e657e41ebb97982d6b133136c")
if px is not None:
    px["runNote1431"] = "Run 1431: BACA GAGAL lagi (batch-fail, nilai lama dipertahankan, BUKAN nol)."
    px["lastReadBlock"] = BLOCK; px["lastReadWib"] = "2026-11-13 ~14:34 WIB"
upd("0x9081f02876c173d0c69f042959cfd0d61c668b17", totalSupply=509, MAX_SUPPLY=1682,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1431="Run 1431: SKRR 509 FLAT. DIAM.")
upd("0xa545c8726bcf4acf840dac521b369911fe2abc8d", totalSupply=279, MAX_SUPPLY=1950,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1431="Run 1431: ME30 277->279 (+2). DIAM.")
upd("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", totalSupply=458, MAX_SUPPLY=1703,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1431="Run 1431: CY24 457->458 (+1). DIAM.")
upd("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", totalSupply=1263, balanceOf_user=1,
    runNote1431="Run 1431: HIVE totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", totalSupply=972, balanceOf_user=0,
    runNote1431="Run 1431: DragonAgent totalSupply 972 FLAT; free views NULL -> free % UNVERIFIED. DIAM.")

# --- NOTV / BC1B (track_c) ---
_, _, nt = find_entry("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01")
if nt is not None:
    upd("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", totalSupply=0, totalMinted=0,
        FREE_SHARES=2000, freeStart=1794567600,
        runNote1431="Run 1431: totalMinted 0, freeStart 18:00 WIB 13 Nov - belum buka. DIAM.")
_, _, bc = find_entry("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053")
if bc is not None:
    upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053", totalSupply=1000000000000000000000000000,
        freeCount=466, balanceOf_user=0,
        runNote1431="Run 1431: BC1B/RESUME freeCount 466 FLAT. DIAM.")

# --- JNTM sellout confirmed again ---
snap["runNote1431_jntm"] = ("Run 1431: JNTM sellout TERKONFIRMASI ulang (freeClaimed 1000/1000, freeLeft 0, "
    "totalMinted 1174, paidMinted 174); sudah dihapus dari track_c + dicatat di sellouts run 1331. DIAM.")

# --- binanceai.fun pending claim ---
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["launched"] = 0; pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-13 ~14:34 WIB"
    pc["runNote1431"] = "Run 1431: launched()=0, tokenClaimed(user)=0 - tetap belum buka/pending (sudah dilaporkan sekali sebagai PENDING CLAIM). DIAM."

# --- Mossbound Key: 301/325 = 92.6%, velocity now PASSES, gate still FAILED ---
_, _, mb = find_entry("0xe589A94316C68d4A4f008f841Deb7e9612445244")
n_mb = 301 - (mb.get("freeMinted") or 0)
rate_mb = round(n_mb / INTERVAL, 2)
ratio_mb = round(rate_mb / 2.8, 2)  # vs run 1401 first rate 2.8/min
upd("0xe589A94316C68d4A4f008f841Deb7e9612445244", totalSupply=301, totalMinted=301,
    freeMinted=301, freeRemaining=24, FREE_SUPPLY=325, FREE_PER_WALLET=1,
    saleOpen=1, mintOpen=1, isFreeOpen=1, freeAvailable_user=1, balanceOf_user=0,
    MAX_SUPPLY=500, freePct=92.6,
    status="watchlist-only-open-2026-11-13",
    gate="website_failed",
    website=None, websiteVerified=False,
    mintedInInterval=n_mb, currentRatePerMin=rate_mb, velocityRatio=ratio_mb,
    velocityLegPasses=True, intervalMinutes=INTERVAL,
    velocityNote=("Run 1431: rate 214 token/~31 mnt = 6,90/mnt vs rate pertama run 1401 (2,8/mnt) = 2,46x "
        "AND >=20 token -> velocity LOLOS run ini (previous rate = first rate 1401; previousRatePerMin snapshot tetap frozen "
        "per konvensi yang belum diputuskan parent). BUKAN kandidat: gate website GAGAL + diskusi X belum ada. "
        "Strong-lead legs (umur+>70%+slot) terpenuhi, TAPI gate-blocked 70% SUDAH dilaporkan sekali oleh hot-leg 1424 (14:27 WIB) -> TIDAK lapor ulang."),
    runNote1431="Run 1431: freeMinted 87->301/325 = 92,6% (+214, 6,90/mnt, velocity LOLOS 2,46x vs rate pertama 2,8); freeRemaining 24; slot user TERBUKA; umur TERVERIFIKASI ~42 mnt <24 jam; gate website TETAP GAGAL (A-N run 1401). BUKAN kandidat/strong lead (gate-blocked); 70% SUDAH dilaporkan sekali hot-leg 1424 - TIDAK lapor ulang; sellout belum (24 tersisa, bisa habis <5 mnt) - pantau hot-leg. TIDAK di-preview/TIDAK di-mint.")

# --- NEW: Ochre Medallion (OCMD) - upcoming, sale opens 14:51 WIB ---
snap.setdefault("contracts", {})["Ochre Medallion"] = {
    "address": "0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D",
    "name": "Ochre Medallion", "symbol": "OCMD",
    "status": "watchlist-only-upcoming-2026-11-13",
    "source": "sourcify-feed-2026-11-13-1431",
    "totalSupply": 0, "totalMinted": 0, "freeMinted": 0, "freeRemaining": 0,
    "FREE_SUPPLY": 210, "FREE_PER_WALLET": 1, "MAX_SUPPLY": 300,
    "saleStart": 1794556267, "saleStartWib": "2026-11-13 14:51:07 WIB",
    "saleEnd": 1794729067, "saleOpen": 0, "mintOpen": 0, "isFreeOpen": 0,
    "freeAvailable_user": 0, "balanceOf_user": 0,
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "gate": "not-yet-checked", "website": None, "websiteVerified": False,
    "lastReadBlock": BLOCK, "lastReadWib": "2026-11-13 ~14:34 WIB",
    "runNote1431": ("Run 1431: BARU dari Sourcify feed (verifiedAt 2026-11-13T07:31:19Z = 14:31:19 WIB). "
        "S1 sale-shape lolos via ABI Sourcify (77 fns: mint/freeMint/claimFree + quote + free views + agent registry); "
        "decimals() null -> NFT (ERC-721), bukan share-sale fungible. Sale BELUM buka (saleOpen=0, saleStart 14:51:07 WIB, ~17 mnt lagi), "
        "0 mint -> BUKAN early lead (butuh first mints terverifikasi) dan BUKAN kandidat; watchlist-only-upcoming, TIDAK di-preview/TIDAK di-mint. "
        "Pantau hot-leg + run 1501 saat sale buka; gate website belum dicek (tugas saat buka).")}

# --- New feed contract checked (not sale-shape) ---
snap.setdefault("track_c", {})["Feed-0xCb49"] = {
    "address": "0xCb49E27AE034577777affbFEe4a607C6eF39ce29",
    "name": "Feed-0xCb49",
    "status": "checked-not-sale-shape-2026-11-13",
    "note": ("Run 1431 discovery: Sourcify feed baru (verifiedAt 2026-11-13T07:34:32Z), ABI 28 fns, "
             "S1 false (tanpa mint fn, tanpa free view, tanpa agent ref) - BUKAN lead track-C / early lead. Dicatat saja."),
    "lastReadWib": "2026-11-13 ~14:34 WIB"}

# --- Run notes ---
snap["runNote1431"] = ("Run free-mint-search 2026-11-13 14:31 WIB (selesai ~14:35 WIB). TIDAK ADA laporan chat: "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat baru, 0 perubahan track-B. "
    "Mossbound Key 301/325 = 92,6% (velocity lolos 2,46x), gate website TETAP GAGAL; 70% sudah dilaporkan sekali hot-leg 1424 - tidak lapor ulang; "
    "sellout belum (24 tersisa). Ochre Medallion (OCMD) BARU terverifikasi Sourcify 14:31:19 WIB, sale buka 14:51:07 WIB, 0 mint - "
    "watchlist-only-upcoming. 22 target dibaca segar blok 133312513; PX24 baca gagal lagi (nilai lama dipertahankan).")
snap["runNote1431_scan"] = ("Scan leg FAST-FAIL run 1431: Ankr pre-flight HTTP 401 Unauthorized "
    "(outage sejak 2026-11-09 berlanjut; run 1301 timeout, 1331 401, 1401 401, run ini 401). Watermark TETAP 132512564; "
    "gap ke head terus tumbuh. 5c dilewati (tanpa output scan).")
snap["runNote1431_discovery"] = ("Discovery run 1431: Sourcify feed 20 (verifiedAt 06:37:39-07:34:32Z), 2 baru vs hot-leg-seen: "
    "0xF3A8A59F Ochre Medallion (OCMD) - S1 lolos via ABI (77 fns), NFT, sale buka 14:51:07 WIB, 0 mint, upcoming-only; "
    "0xCb49E27A - bukan sale-shape (ABI 28 fns, tanpa mint/free/agent). Boltbook EN 45.063 B / ZH 43.361 B, 0 alamat baru. "
    "Bridge (read-only): 116 kontrak, 7 same-owner-discarded - sama seperti run 1401, tanpa promosi/perubahan. "
    "Feed trio hot-leg 1429 (0x2278/0xA298/0x98e7) sudah masuk hot-leg-seen, tidak dicek ulang.")
snap["runNote1431_mossbound"] = ("Mossbound Key (MSKY) 0xe589A94316C68d4A4f008f841Deb7e9612445244 - run 1431: "
    "freeMinted 301/325 = 92,6% (blok 133312513), freeRemaining 24, slot user TERBUKA, umur terverifikasi ~42 mnt, "
    "velocity LOLOS (6,90/mnt = 2,46x rate pertama 2,8). Gate website TETAP GAGAL (A-N run 1401; L terblokir Cloudflare). "
    "70% crossing SUDAH dilaporkan sekali hot-leg 1424 (14:27 WIB) -> run ini TIDAK lapor ulang. Sellout belum; bila habis, "
    "hot-leg/run berikut laporkan sekali sebagai perubahan. TIDAK di-preview/TIDAK di-mint.")
snap["runNote1431_ocmd"] = ("Ochre Medallion (OCMD) 0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D - BARU run 1431: "
    "Sourcify verified 14:31:19 WIB, S1 sale-shape lolos (ABI 77 fns), NFT agent-shaped (agentIdRegistry = registry Binance, decimals null), "
    "FREE_SUPPLY 210 / MAX_SUPPLY 300 / FREE_PER_WALLET 1, saleStart 14:51:07 WIB, saleEnd 2026-11-15 14:51:07 WIB, "
    "saleOpen=0, 0 mint. Watchlist-only-upcoming; gate website belum dicek - tugas saat sale buka (hot-leg + run 1501).")
snap["last_run_wib"] = "2026-11-13 ~14:35 WIB"
snap["last_run"] = "2026-11-13T14:35+07:00"
snap["timestamp_wib"] = "2026-11-13 ~14:35 WIB"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
