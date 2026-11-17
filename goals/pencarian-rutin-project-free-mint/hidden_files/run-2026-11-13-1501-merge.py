#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 15:01 WIB.
Fresh reads from run-2026-11-13-1501-verify.json (block 133316425, ~15:03 WIB)
+ discovery (0 new feed contracts) + OCMD gate check A-N (run-2026-11-13-1501-gate.json).
previousRatePerMin stays FROZEN (convention question from run 0931 still
undecided by parent); currentRatePerMin computed per interval (~30 min).
OCMD: freeMinted 102/210 = 48.6% (<50% candidate, <70% strong lead), slot open,
age verified (saleStart 14:51:07 WIB), velocity first-rate (no previous rate ->
do NOT pass on velocity alone), gate website FAILED (A-N; L Cloudflare-blocked,
K GitHub API rate-limited - limitations, not absence). Watchlist-only-open.
Mossbound: SOLD OUT 325/325 - already reported once by hot-leg 1444, no re-report.
Read-only on-chain; only writes the snapshot. No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-1501.bak")
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-13-1501-verify.json"))
BLOCK = verify.get("block")
INTERVAL = 30  # minutes vs run 1431 reads (~14:33 WIB snapshot)

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
    v["lastReadWib"] = "2026-11-13 ~15:04 WIB"
    return True

def vel(prev_total, new_total, prev_rate):
    n = (new_total or 0) - (prev_total or 0)
    rate = round(n / INTERVAL, 2)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return n, rate, ratio, bool(ratio is not None and ratio >= 1.5 and n >= 20)

# --- Agentx ---
_, _, ax = find_entry("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492")
n, rate, ratio, passed = vel(ax.get("totalMinted"), 732, ax.get("previousRatePerMin"))
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492", totalMinted=732, freeMinted=732,
    FREE_CAP=1111, MAX_SUPPLY=2222, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=65.9, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1501="Run 1501: totalMinted 724->732 (+8, 0.27/mnt vs prev 0.18 = 1.48x, <20 token) -> velocity GAGAL; free 732/1111 = 65.9% (<70% strong lead); slot terbuka; umur ~16.2 jam (mintOpensAt 2026-11-12 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov. Gate website tetap GAGAL (dilaporkan 08:01 + hot-leg 08:29). TIDAK di-preview/TIDAK di-mint. DIAM.")

# --- Zero ---
_, _, z = find_entry("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647")
n, rate, ratio, passed = vel(z.get("totalMinted"), 280, z.get("previousRatePerMin"))
upd("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", totalMinted=280, freeMinted=280,
    FREE_CAP=500, mintOpen=1, freeClaimed_user=0, balanceOf_user=0,
    freePct=56.0, mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1501="Run 1501: totalMinted 279->280 (+1) -> velocity GAGAL; free 280/500 = 56.0%; slot TERBUKA; umur ~7.5 jam (mintOpensAt 07:55 WIB) <24 jam; website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.")

# --- Royal Rush Agents ---
_, _, rr = find_entry("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3")
n, rate, _, _ = vel(rr.get("totalSupply"), 764, None)
ratio_bl = round(rate / 7.74, 2) if rate else None
upd("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3", totalSupply=764, totalMinted=764,
    freeMinted=744, freeRemaining=256, FREE_MAX=1000, mintOpen=1, paidMinted=20,
    freeClaimedByAgent_user=0, balanceOf_user=0, freePct=74.4,
    mintedInInterval=n, currentRatePerMin=rate, velocityRatio=ratio_bl,
    velocityLegPasses=False, intervalMinutes=INTERVAL,
    runNote1501="Run 1501: freeMinted 642->744/1000 = 74.4% (+102, 3.40/mnt vs baseline 7.74 = 0.44x) -> velocity GAGAL (melambat); umur TETAP UNVERIFIED + X UNVERIFIED -> BUKAN strong lead/kandidat walau >70%. Slot terbuka. DIAM.")

# --- Oliver Agents ---
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810", totalSupply=988, freeMinted=938,
    freeRemaining=62, FREE_MAX=1000, mintOpen=1, mintedCount=988, paidMinted=50,
    balanceOf_user=0,
    runNote1501="Run 1501: freeMinted 936->938/1000 = 93.8% (+2); umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")

# --- OBFG (track_c) ---
upd("0x5314071bba19943f58347ba5dec423e5032a6818", totalSupply=679, totalMinted=679,
    freeMinted=679, FREE_SUPPLY=1230, saleOpen=1, freeAvailable_user=1, balanceOf_user=0,
    freePct=55.2,
    runNote1501="Run 1501: 679/1230 = 55.2% (+3); umur ~19.4 jam (saleStart 2026-11-12 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov; slot terbuka; gate-blocked (dilaporkan 12 Nov). DIAM.")

# --- AgentMuse (track_c) ---
upd("0x779fa133848d23052B7345F63B3b2E5309cd13ed", freeClaimed=336, FREE_SHARES=888,
    bookedTotal=33600000000000000000000000, openedAt=0,
    bookedOf_user=100000000000000000000000,
    runNote1501="Run 1501: freeClaimed 336/888 = 37.8% FLAT; user sudah mint (bookedOf utuh). DIAM.")

# --- AgentLabs ---
_, _, al = find_entry("0x639329f5dc4317c44D9Fed961a1217ba845012F7")
n, rate, ratio, passed = vel(al.get("totalSpecimens"), 2219, al.get("previousRatePerMin"))
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7", totalSpecimens=2219, priceFor_user=0,
    holdsAgentId_user=1, balanceOf_user=0, genesisOpen=1, currentExperiment=2,
    specimensInInterval=n, currentRatePerMin=rate, velocityRatio=ratio,
    velocityLegPasses=passed, intervalMinutes=INTERVAL,
    runNote1501="Run 1501: totalSpecimens 2200->2219 (+19, 0.63/mnt vs prev 3.298 = 0.19x, <20 token) -> velocity GAGAL; experiment 2 berjalan; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.")

# --- OUTY ---
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412", minted=26, freeSold=26, paidSold=0,
    FREE_SUPPLY=1500, FREE_FEE=100000000000000, phase=1, freeOpen=1, paidOpen=0,
    freeQuotaOf_user=1, quotaOf_user=10, balanceOf_user=0,
    runNote1501="Run 1501: freeSold 26/1500 FLAT; FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")

# --- MECHA / Pickgrid / PX24-group / HIVE / DragonAgent ---
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", totalMinted=1929, freeClaimed=1928,
    runNote1501="Run 1501: freeClaimed 1928/4444 = 43.4% FLAT (<50%). DIAM.")
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0", freeMinted=216, FREE_CAP=300,
    runNote1501="Run 1501: freeMinted 216/300 FLAT, umur UNVERIFIED. DIAM.")
_, _, px = find_entry("0xe712510fcb27935e657e41ebb97982d6b133136c")
if px is not None:
    px["runNote1501"] = "Run 1501: BACA GAGAL lagi (batch-fail, nilai lama dipertahankan, BUKAN nol)."
    px["lastReadBlock"] = BLOCK; px["lastReadWib"] = "2026-11-13 ~15:04 WIB"
upd("0x9081f02876c173d0c69f042959cfd0d61c668b17", totalSupply=509, MAX_SUPPLY=1682,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1501="Run 1501: SKRR 509 FLAT. DIAM.")
upd("0xa545c8726bcf4acf840dac521b369911fe2abc8d", totalSupply=281, MAX_SUPPLY=1950,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1501="Run 1501: ME30 279->281 (+2). DIAM.")
upd("0x731d879ee2cd4bbf32efef9178d51d5c1441d052", totalSupply=458, MAX_SUPPLY=1703,
    mintOpen=1, balanceOf_user=0, costOf_user_1=0,
    runNote1501="Run 1501: CY24 458 FLAT. DIAM.")
upd("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", totalSupply=1263, balanceOf_user=1,
    runNote1501="Run 1501: HIVE totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", totalSupply=972, balanceOf_user=0,
    runNote1501="Run 1501: DragonAgent totalSupply 972 FLAT; free views NULL -> free % UNVERIFIED. DIAM.")

# --- NOTV / BC1B (track_c) ---
_, _, nt = find_entry("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01")
if nt is not None:
    upd("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", totalSupply=0, totalMinted=0,
        FREE_SHARES=2000, freeStart=1794567600,
        runNote1501="Run 1501: totalMinted 0, freeStart 18:00 WIB 13 Nov - belum buka. DIAM.")
_, _, bc = find_entry("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053")
if bc is not None:
    upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053", totalSupply=1000000000000000000000000000,
        freeCount=467, balanceOf_user=0,
        runNote1501="Run 1501: BC1B/RESUME freeCount 467 FLAT. DIAM.")

# --- JNTM sellout confirmed again ---
snap["runNote1501_jntm"] = ("Run 1501: JNTM sellout TERKONFIRMASI ulang (freeClaimed 1000/1000, freeLeft 0, "
    "totalMinted 1193, paidMinted 193); sudah dihapus dari track_c + dicatat di sellouts run 1331. DIAM.")

# --- binanceai.fun pending claim ---
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["launched"] = 0; pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-13 ~15:04 WIB"
    pc["runNote1501"] = "Run 1501: launched()=0, tokenClaimed(user)=0 - tetap belum buka/pending (sudah dilaporkan sekali sebagai PENDING CLAIM). DIAM."

# --- Mossbound Key: SOLD OUT (already reported once by hot-leg 1444) ---
upd("0xe589A94316C68d4A4f008f841Deb7e9612445244", totalSupply=325, totalMinted=325,
    freeMinted=325, freeRemaining=0, FREE_SUPPLY=325, FREE_PER_WALLET=1,
    saleOpen=1, mintOpen=1, isFreeOpen=0, freeAvailable_user=0, balanceOf_user=0,
    MAX_SUPPLY=500, freePct=100.0,
    status="sold-out-2026-11-13",
    runNote1501="Run 1501: SOLD OUT terkonfirmasi (freeMinted 325/325 = 100%, freeRemaining 0, isFreeOpen=0, freeAvailable_user=0). Sellout SUDAH dilaporkan sekali oleh hot-leg 1444 -> TIDAK lapor ulang. DIAM.")

# --- Ochre Medallion (OCMD): now open, 102/210 = 48.6%, gate FAILED ---
upd("0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D", totalSupply=102, totalMinted=102,
    freeMinted=102, freeRemaining=108, FREE_SUPPLY=210, FREE_PER_WALLET=1,
    saleOpen=1, mintOpen=1, isFreeOpen=1, freeAvailable_user=1, balanceOf_user=0,
    MAX_SUPPLY=300, freePct=48.6,
    status="watchlist-only-open-2026-11-13",
    gate="website_failed",
    website=None, websiteVerified=False,
    mintedInInterval=102, currentRatePerMin=3.4, velocityRatio=None,
    velocityLegPasses=False, intervalMinutes=INTERVAL,
    velocityNote=("Run 1501: +102 token sejak run 1431 (0 mint, sale belum buka) = 3,40/mnt, TAPI tidak ada "
        "previous rate (interval pertama sejak sale buka 14:51:07 WIB) -> velocity TIDAK lolos atas dasar "
        "velocity saja (aturan: tanpa previous rate, catat snapshot, jangan loloskan)."),
    runNote1501=("Run 1501: freeMinted 0->102/210 = 48,6% (sale buka 14:51:07 WIB, umur ~13 mnt <24 jam, "
        "saleEnd 2026-11-15 14:51:07 WIB); slot user TERBUKA (freeAvailable=1, quote cost 0); "
        "<50% -> BUKAN kandidat, <70% -> BUKAN strong lead. GATE website GAGAL (metode A-N run ini: "
        "contractURI/tokenURI fully on-chain base64 tanpa URL apa pun; Sourcify 77 fns tanpa site/URL fn dan "
        "tanpa URL di metadata; pencarian alamat + nama proyek 0 hit; site:vercel/pages/deed 0 hit; "
        "Boltbook EN/ZH alamat tidak muncul; The Colony projects.json 0 hit 'ochre'; "
        "GitHub code-search API rate-limited (K tidak konklusif); BscScan metode L terblokir Cloudflare "
        "bot wall di text-fetch DAN live browser (3x bot-challenge, Ray ID a59c53015c0d1421) - L tidak "
        "konklusif, bukan bukti tidak ada). TIDAK di-preview/TIDAK di-mint. DIAM."))

# --- Run notes ---
snap["runNote1501"] = ("Run free-mint-search 2026-11-13 15:01 WIB (selesai ~15:15 WIB). TIDAK ADA laporan chat: "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat baru, 0 perubahan track-B. "
    "Ochre Medallion 102/210 = 48,6% (sale buka 14:51 WIB), gate website GAGAL (A-N; L Cloudflare-blocked, K rate-limited) - "
    "watchlist-only-open. Mossbound Key SOLD OUT 325/325 (sudah dilaporkan hot-leg 1444, tidak lapor ulang). "
    "23 target dibaca segar blok 133316425; PX24 baca gagal lagi (nilai lama dipertahankan).")
snap["runNote1501_scan"] = ("Scan leg FAST-FAIL run 1501: Ankr pre-flight HTTP 401 Unauthorized "
    "(outage sejak 2026-11-09 berlanjut; run 1301 timeout, 1331/1401/1431 401, run ini 401). Watermark TETAP 132512564; "
    "gap ke head terus tumbuh. 5c dilewati (tanpa output scan).")
snap["runNote1501_discovery"] = ("Discovery run 1501: Sourcify feed 20 (verifiedAt 07:00:27-07:57:19Z), 0 baru vs hot-leg-seen. "
    "Boltbook EN 44.422 B / ZH 42.899 B, 0 alamat baru. Bridge (read-only, per hot-leg 1459): 116 kontrak, "
    "7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. OCMD + 0xCb49 tidak ada di bridge.")
snap["runNote1501_ocmd_gate"] = ("Ochre Medallion (OCMD) 0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D - GATE run 1501: "
    "GAGAL. (H) contractURI() base64 JSON: nama + deskripsi saja, TANPA external_link/URL apa pun. "
    "(I) tokenURI(1) base64 JSON sama, tanpa URL. (J) ABI Sourcify 77 fns, tanpa fungsi site/URL/domain/external. "
    "(C) metadata Sourcify tanpa URL. (A) pencarian alamat kontrak 0 hit. (G) pencarian 'Ochre Medallion' NFT "
    "0 hit proyek. (M) site:vercel.app/pages.dev/deed.page 0 hit. (B) Boltbook EN/ZH alamat tidak muncul. "
    "(K) GitHub code-search API rate-limited (unauthenticated) - tidak konklusif. (L) BscScan text-fetch 403 + "
    "live browser 3x bot-challenge gagal (Cloudflare, Ray ID a59c53015c0d1421) - tidak konklusif, bukan bukti tidak ada. "
    "(N) tidak berlaku - OCMD NFT, bukan Agent ID registry profile. The Colony projects.json: 0 hit 'ochre'. "
    "Gate tercatat di snapshot; bila OCMD melewati 50%/70% di run berikut, gate TIDAK perlu diulang dari nol "
    "kecuali bukti baru muncul; bila tetap tanpa website saat melewati ambang, laporkan sekali sebagai "
    "gate-blocked (bukan kandidat/lead).")
snap["last_run_wib"] = "2026-11-13 ~15:15 WIB"
snap["last_run"] = "2026-11-13T15:15+07:00"
snap["timestamp_wib"] = "2026-11-13 ~15:15 WIB"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
