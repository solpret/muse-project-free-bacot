#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 14:01 WIB.
Fresh reads from run-2026-11-13-1401-verify.json (block 133308381, ~14:02 WIB)
+ discovery + Mossbound gate (methods A-N; L blocked by Cloudflare bot wall).
previousRatePerMin stays FROZEN (convention question from run 0931 still
undecided by parent); currentRatePerMin computed per interval (~30 min).
Read-only on-chain; only writes the snapshot. No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-13-1401-verify.json"))
reads = verify["reads"]
BLOCK = verify.get("block")
INTERVAL = 30  # minutes vs run 1331 reads (~13:40 WIB snapshot)

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
    v["lastReadWib"] = "2026-11-13 ~14:10 WIB"
    return True

def vel(prev_total, new_total, prev_rate):
    n = (new_total or 0) - (prev_total or 0)
    rate = round(n / INTERVAL, 2)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return n, rate, ratio, bool(ratio is not None and ratio >= 1.5 and n >= 20)

# --- Agentx (contracts) ---
_, _, ax = find_entry("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
n, rate, ratio, passed = vel(ax.get("totalMinted"), 717, ax.get("previousRatePerMin"))
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", totalMinted=717, freeMinted=717,
    FREE_CAP=1111, MAX_SUPPLY=2222, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=64.5, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1401="Run 1401: totalMinted 716->717 (+1, 0.03/mnt vs prev 0.18 = 0.18x, <20 token) -> velocity GAGAL; free 717/1111 = 64.5% (<70% strong lead); slot terbuka; umur ~14.9 jam (mintOpensAt 2026-11-12 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov. Gate website tetap GAGAL (dilaporkan 08:01 + hot-leg 08:29). TIDAK di-preview/TIDAK di-mint. DIAM.")

# --- Zero (contracts) ---
_, _, z = find_entry("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647")
n, rate, ratio, passed = vel(z.get("totalMinted"), 273, z.get("previousRatePerMin"))
upd("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", totalMinted=273, freeMinted=273,
    FREE_CAP=500, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=54.6, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1401="Run 1401: totalMinted 269->273 (+4, 0.13/mnt vs prev 2.42 = 0.06x, <20 token) -> velocity GAGAL; free 273/500 = 54.6%; slot TERBUKA; umur ~6.1 jam (mintOpensAt 07:55 WIB) <24 jam; website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.")

# --- Royal Rush Agents (contracts) ---
_, _, rr = find_entry("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3")
n, rate, ratio, passed = vel(rr.get("totalSupply"), 570, rr.get("previousRatePerMin"))
upd("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3", totalSupply=570, totalMinted=570,
    freeMinted=550, freeRemaining=450, FREE_MAX=1000, mintOpen=1, paidMinted=20,
    freeClaimedByAgent_user=0, balanceOf_user=0, freePct=55.0,
    mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1401="Run 1401: freeMinted 530->550/1000 = 55.0% (+20, 0.67/mnt vs baseline 7.74 = 0.09x) -> velocity GAGAL (melambat); umur UNVERIFIED + X UNVERIFIED -> BUKAN kandidat; <70% bukan strong lead. Slot terbuka. DIAM.")

# --- Oliver Agents (contracts) ---
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810", totalSupply=984, freeMinted=934,
    freeRemaining=66, FREE_MAX=1000, mintOpen=1, mintedCount=984, paidMinted=50,
    balanceOf_user=0,
    runNote1401="Run 1401: freeMinted 931->934/1000 = 93.4% (+3); umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")

# --- OBFG (track_c) ---
_, _, ob = find_entry("0x5314071bba19943f58347ba5dec423e5032a6818")
upd("0x5314071bba19943f58347ba5dec423e5032a6818", totalSupply=676, totalMinted=676,
    freeMinted=676, FREE_SUPPLY=1230, saleOpen=1, freeAvailable_user=1, balanceOf_user=0,
    freePct=55.0,
    runNote1401="Run 1401: 672->676/1230 = 55.0% (+4); umur ~18.1 jam (saleStart 2026-11-12 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov; slot terbuka; gate-blocked (dilaporkan 12 Nov). DIAM.")

# --- AgentMuse (track_c) ---
_, _, am = find_entry("0x779fa133848d23052B7345F63B3b2E5309cd13ed")
if am is not None:
    upd("0x779fa133848d23052B7345F63B3b2E5309cd13ed", freeClaimed=319, FREE_SHARES=888,
        bookedTotal=31900000000000000000000000, openedAt=0,
        bookedOf_user=100000000000000000000000,
        runNote1401="Run 1401: freeClaimed 318->319/888 = 35.9% (+1); user sudah mint (bookedOf utuh). DIAM.")
else:
    print("AgentMuse not found by address; keys:", [k for k in snap.get('track_c',{}) if 'Muse' in k])

# --- AgentLabs (contracts) ---
_, _, al = find_entry("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
n, rate, ratio, passed = vel(al.get("totalSpecimens"), 2181, al.get("previousRatePerMin"))
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7", totalSpecimens=2181, priceFor_user=0,
    holdsAgentId_user=1, balanceOf_user=0, genesisOpen=1, currentExperiment=2,
    specimensInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1401="Run 1401: totalSpecimens 2160->2181 (+21, experiment 2 berjalan); deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")

# --- OUTY (contracts) ---
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", minted=25, freeSold=25, paidSold=0,
    FREE_SUPPLY=1500, FREE_FEE=100000000000000, phase=1, freeOpen=1, paidOpen=0,
    freeQuotaOf_user=1, quotaOf_user=10, balanceOf_user=0,
    runNote1401="Run 1401: freeSold 23->25/1500 (+2); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")

# --- MECHA / Pickgrid / PX24-group / HIVE / DragonAgent ---
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", totalMinted=1925, freeClaimed=1924,
    runNote1401="Run 1401: freeClaimed 1924/4444 = 43.2% FLAT (<50%). DIAM.")
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0", freeMinted=216, FREE_CAP=300,
    runNote1401="Run 1401: freeMinted 216/300 FLAT, umur UNVERIFIED. DIAM.")
# PX24 read failed again (empty summary) - retain old values, note only
_, _, px = find_entry("0xe712510fcb27935e657e41ebb97982d6b133136c")
if px is not None:
    px["runNote1401"] = "Run 1401: BACA GAGAL lagi (batch-fail, nilai lama dipertahankan, BUKAN nol)."
    px["lastReadBlock"] = BLOCK; px["lastReadWib"] = "2026-11-13 ~14:10 WIB"
upd("0x9081f02876c173d0c69f042959cfd0d61c668b17", totalSupply=509, MAX_SUPPLY=1682,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1401="Run 1401: SKRR 509 FLAT. DIAM.")
upd("0xa545c8726bcf4acf840dac521b369911fe2abc8d", totalSupply=277, MAX_SUPPLY=1950,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1401="Run 1401: ME30 273->277 (+4). DIAM.")
upd("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", totalSupply=457, MAX_SUPPLY=1703,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1401="Run 1401: CY24 457 FLAT. DIAM.")
upd("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", totalSupply=1263, balanceOf_user=1,
    runNote1401="Run 1401: HIVE totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", totalSupply=972, balanceOf_user=0,
    runNote1401="Run 1401: DragonAgent totalSupply 972 FLAT; free views NULL -> free % UNVERIFIED. DIAM.")

# --- NOTV / BC1B (track_c) ---
_, _, nt = find_entry("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01")
if nt is not None:
    upd("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", totalSupply=0, totalMinted=0,
        FREE_SHARES=2000, freeStart=1794567600,
        runNote1401="Run 1401: totalMinted 0, freeStart 18:00 WIB 13 Nov - belum buka. DIAM.")
_, _, bc = find_entry("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053")
if bc is not None:
    upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053", totalSupply=1000000000000000000000000000,
        freeCount=465, balanceOf_user=0,
        runNote1401="Run 1401: BC1B/RESUME freeCount 465 FLAT. DIAM.")

# --- JNTM sellout confirmed (already in sellouts) ---
_, _, _jt = find_entry("0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b")
# JNTM removed from track_c at 1331; verify read confirms: freeClaimed 1000, freeLeft 0.
# No snapshot change needed; note in runNote1401.
snap["runNote1401_jntm"] = ("Run 1401: JNTM sellout TERKONFIRMASI ulang (freeClaimed 1000/1000, freeLeft 0, "
    "totalMinted 1152, paidMinted 152); sudah dihapus dari track_c + dicatat di sellouts run 1331. DIAM.")

# --- binanceai.fun pending claim ---
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["launched"] = 0; pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-13 ~14:10 WIB"
    pc["runNote1401"] = "Run 1401: launched()=0, tokenClaimed(user)=0 - tetap belum buka/pending (sudah dilaporkan sekali sebagai PENDING CLAIM). DIAM."

# --- Mossbound Key (contracts): upcoming -> open ---
_, _, mb = find_entry("0xe589A94316C68d4A4f008f841Deb7e9612445244")
upd("0xe589A94316C68d4A4f008f841Deb7e9612445244", totalSupply=87, totalMinted=87,
    freeMinted=87, freeRemaining=238, FREE_SUPPLY=325, FREE_PER_WALLET=1,
    saleOpen=1, mintOpen=1, isFreeOpen=1, freeAvailable_user=1, balanceOf_user=0,
    MAX_SUPPLY=500, freePct=26.8,
    status="watchlist-only-open-2026-11-13",
    gate="website_failed",
    website=None, websiteVerified=False,
    currentRatePerMin=2.8,  # first rate: 87 token / ~31 mnt sejak first read 0 (13:31); no previous rate -> velocity NOT passable
    velocityLegPasses=False,
    velocityNote="Run 1401: rate pertama 87 token/~31 mnt = 2,8/mnt; previousRate belum ada -> velocity TIDAK BISA lolos run ini (aturan: tanpa previous rate, catat snapshot, jangan loloskan atas velocity saja).",
    runNote1401="Run 1401: SALE DIBUKA 13:51:55 WIB. freeMinted 0->87/325 = 26,8% (82 hot-leg 13:59 -> 87, ~1,7/mnt, melambat dari burst awal ~25/mnt); freeRemaining 238; slot user TERBUKA (freeAvailable=1, quote cost 0); umur TERVERIFIKASI ~10 mnt <24 jam. BUKAN lead/kandidat (26,8% <50%, velocity belum bisa lolos, gate website GAGAL, diskusi belum ada) - TIDAK di-preview/TIDAK di-mint.",
    websiteNote=("Gate website GAGAL run 1401, metode A-N penuh: (A) pencarian alamat kontrak 0 hasil relevan; "
        "(B) Boltbook EN+ZH tanpa sebutan; (C) Sourcify exact_match, metadata tanpa URL; (D) site: vercel/pages/deed/surge 0 hasil; "
        "(E) owner()=0x0, agentIdRegistry()=registry Binance; (G) pencarian nama 'Mossbound Key' 0 hasil relevan; "
        "(H) contractURI fully on-chain base64 JSON, tanpa external_link; (I) tokenURI #1 fully on-chain, tanpa external_url; "
        "(J) siteURL()/website()/baseURI() null; (K) GitHub 0 hasil relevan (true code search butuh auth - limitasi dicatat); "
        "(L) BscScan token page TIDAK BISA dibaca - Cloudflare bot wall (browser task 14:05-14:17 WIB, Ray ID a59bfefcf95b76b0, 2x bot-challenge gagal) - BUKAN bukti tidak ada; "
        "(M) site: filters 0 hasil; (N) registry hop tanpa profil/situs. Bila melewati 50%/70% tanpa website -> gate-blocked, lapor sekali + alasan, tidak pernah preview/mint."),
    gateNote="Gate website GAGAL (metode A-N run 1401; L terblokir Cloudflare, bukan bukti absen). TIDAK di-preview/TIDAK di-mint.")

# --- New feed contract checked (not sale-shape) ---
snap.setdefault("track_c", {})["Feed-0x20C0"] = {
    "address": "0x20C0766cC6fF12e0D4D1c457aF7B0491b95a5555",
    "name": "Feed-0x20C0",
    "status": "checked-not-sale-shape-2026-11-13",
    "note": ("Run 1401 discovery: Sourcify feed baru (verifiedAt 2026-11-13T07:02:07Z), ABI 29 fns, "
             "S1 false (tanpa mint fn, tanpa free view, tanpa agent ref) - BUKAN lead track-C / early lead. Dicatat saja."),
    "lastReadWib": "2026-11-13 ~14:10 WIB"}

# --- Run notes ---
snap["runNote1401"] = ("Run free-mint-search 2026-11-13 14:01 WIB (selesai ~14:20 WIB). TIDAK ADA laporan chat: "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat baru, 0 perubahan track-B. "
    "Mossbound Key buka 13:51:55 WIB, 87/325 = 26,8%, slot terbuka, gate website GAGAL penuh (A-N; L terblokir Cloudflare) - "
    "bukan lead, tidak di-preview/di-mint. JNTM sellout terkonfirmasi ulang. 21 target dibaca segar blok 133308381; "
    "PX24 baca gagal lagi (nilai lama dipertahankan).")
snap["runNote1401_scan"] = ("Scan leg FAST-FAIL run 1401: Ankr pre-flight HTTP 401 Unauthorized "
    "(outage sejak 2026-11-09 berlanjut; run 1301 timeout, 1331 401, run ini 401). Watermark TETAP 132512564; "
    "gap ke head terus tumbuh. 5c dilewati (tanpa output scan).")
snap["runNote1401_discovery"] = ("Discovery run 1401: Sourcify feed 20 (verifiedAt 06:11:00-07:02:07Z), 1 baru "
    "0x20C0766c - bukan sale-shape (ABI 29 fns, tanpa mint/free/agent). Boltbook EN 45.187 B / ZH 43.484 B, 0 alamat baru. "
    "Bridge (read-only): 116 kontrak, 7 same-owner-discarded - sama seperti run 1331, tanpa promosi/perubahan. "
    "Sweep rute 3: hanya proyek lama/dikenal (AGENT COSMOS, Agentic Gangster free sold out, Anubis/Osiris, Cosmic Sentinel, AGENT MAO paused) - tidak ada lead baru. "
    "Odaily newsflash tidak dibaca ulang run ini (0 item Agent ID/free-mint run 1331).")
snap["runNote1401_mossbound"] = ("Mossbound Key (MSKY) 0xe589A94316C68d4A4f008f841Deb7e9612445244 - gate penuh run 1401: "
    "website UNVERIFIED (metode A-N; detail di websiteNote entri). Sale buka 13:51:55 WIB, free 87/325 = 26,8%, slot terbuka, "
    "umur terverifikasi ~10 mnt. BUKAN lead/kandidat/strong lead. Pantau hot-leg + run 1431; bila >50% atau >70% tanpa website -> "
    "gate-blocked, lapor sekali + alasan, tidak pernah preview/mint.")
snap["last_run_wib"] = "2026-11-13 ~14:20 WIB"
snap["last_run"] = "2026-11-13T14:20+07:00"
snap["timestamp_wib"] = "2026-11-13 ~14:20 WIB"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; contracts:", len(snap.get("contracts", {})))
