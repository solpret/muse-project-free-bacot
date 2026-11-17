#!/usr/bin/env python3
"""Finalize run 1731 — applies reread/velocity to snapshot (reload at write
time), removes 10 age-excluded contracts, adds NULLRAID (strong lead) +
NeoGods (watchlist-only) + ADCHAR (early lead), light BinanceAI re-check
note (already reported once run 1701 — NOT re-reported), scan-partial note
in state (watermark NOT advanced by this run; backfill owns it).
Atomic snapshot write. Also appends ADCHAR to onchain-scan-seen.json."""
import json, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132185959
NOW = datetime.now(timezone(timedelta(hours=7)))
TS = NOW.strftime("%Y-%m-%d %H:%M WIB")
RUN = "2026-11-07 run 1731"

re = json.load(open(f"{BASE}/run-2026-11-07-1731-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1731-velocity.json"))
age = json.load(open(f"{BASE}/run-2026-11-07-1731-age-sweep.json"))
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-07-1731.json"))

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
updated = 0; none_free = 0
for name, d in re["reread"].items():
    c = snap["contracts"].get(name)
    if c is None: continue
    old_ts = c.get("totalSupply")
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if d.get(k) is not None: c[k] = d[k]
    if d.get("totalSupply") is not None and old_ts is not None:
        c["previousTotalSupply"] = old_ts
    if d.get("balanceOf_user") is not None: c["balanceOf_user"] = d["balanceOf_user"]
    if d.get("freeClaimed") is None and d.get("freeMinted") is None: none_free += 1
    c["lastReadBlock"] = REREAD_BLOCK
    c["lastReadWib"] = RUN
    updated += 1
for name, d in re.get("track_c", {}).items():
    tc = snap.get("track_c", {}).get(name)
    if isinstance(tc, dict):
        if d.get("totalSupply") is not None: tc["totalSupply"] = d["totalSupply"]
        if d.get("freeMinted") is not None: tc["freeMinted"] = d["freeMinted"]
        if d.get("freeSharesRemaining") is not None: tc["freeSharesRemaining"] = d["freeSharesRemaining"]
        tc["lastReadBlock"] = REREAD_BLOCK
        tc["lastReadWib"] = RUN

vel_updated = 0
for row in vel.get("rows", []):
    name = row.get("name")
    c = snap["contracts"].get(name)
    if c is None: continue
    cur = row.get("curSupply")
    if cur is None or cur > 1000000: continue
    c["mintedInInterval"] = row.get("mintedInInterval")
    c["intervalMinutes"] = row.get("intervalMin")
    c["currentRatePerMin"] = row.get("ratePerMin")
    c["previousRatePerMin"] = row.get("prevRatePerMin")
    c["velocityLegPasses"] = row.get("velocityPasses")
    c["velocityRatio"] = row.get("ratioVsPrev")
    vel_updated += 1

# --- Age sweep: REMOVE 10 contracts (>48h, verified first mint, not sold out) ---
removed = []
for r in age.get("candidates", []):
    name = r["name"]
    if name in snap["contracts"]:
        removed.append({
            "name": name, "address": r.get("address"),
            "firstMintWib": r.get("firstMintWib"), "ageHours": r.get("ageHours"),
            "curSupply": r.get("curSupply"), "maxSupply": r.get("maxSupply"),
            "status": r.get("status"), "removed_run": RUN,
        })
        del snap["contracts"][name]
snap["age_exclusions_1731"] = removed

# --- Per-contract run notes ---
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote1731"] = (f"Run 1731 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 1701 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.")
cog = snap["contracts"].get("Cogito-COG-A")
if cog is not None:
    cog["velocityNote1731"] = (f"Run 1731 (blok {REREAD_BLOCK}): totalSupply 5242->5275 (+33, rate 0,95/mnt, ratio 26,0 vs prev "
        "0,0364) -> velocity LOLOS tapi rasio artifak basis rendah (prev interval hanya +1); free% UNVERIFIED (semua free view revert, "
        "MAX_SUPPLY null); umur + website/X UNVERIFIED (watchlist-only-boltbookfun) -> BUKAN strong lead dan BUKAN kandidat. Tetap watchlist-only.")
alc = snap["contracts"].get("Alchemister-0xCafEEDDF")
if alc is not None:
    alc["velocityNote1731"] = (f"Run 1731 (blok {REREAD_BLOCK}): totalSupply 3290->3439 (+149, rate 4,27/mnt, ratio 0,35 vs prev) "
        "-> velocity GAGAL (melambat). free% UNVERIFIED; website UNVERIFIED; BUKAN strong lead/kandidat. Tetap early-lead-backfill.")
bot = snap["contracts"].get("BOT-UNIT")
if bot is not None:
    bot["velocityNote1731"] = (f"Run 1731 (blok {REREAD_BLOCK}): totalSupply 1385->1390 (+5, rate 0,14/mnt, ratio 0,04 vs prev) "
        "-> velocity GAGAL. Umur first mint 2026-11-07 02:56:47 WIB (<=48 jam); website https://bot-unit.xyz terverifikasi; slot user "
        "terbuka; TAPI free% UNVERIFIED -> BUKAN strong lead/kandidat. Tetap early lead (dilaporkan run 0931).")
hor = snap["contracts"].get("Horus AI")
if hor is not None:
    hor["velocityNote1731"] = (f"Run 1731 (blok {REREAD_BLOCK}): totalSupply 1569->1596 (+27, rate 0,77/mnt, ratio 0,42 vs prev) "
        "-> velocity GAGAL. Umur ~21 jam; freeSupply 2000/10000 tapi free path PARTIAL/UNVERIFIED -> BUKAN strong lead/kandidat. "
        "Tetap early-lead-backfill.")
mor = snap["contracts"].get("MORPHA")
if mor is not None:
    mor["velocityNote1731"] = (f"Run 1731 (blok {REREAD_BLOCK}): totalSupply 391->640 (+249, rate 7,14/mnt, ratio 1,46 vs prev) "
        "-> velocity GAGAL tipis (di bawah 1,5x). free% UNVERIFIED. BUKAN strong lead/kandidat.")

# --- New: NULLRAID (strong lead) ---
snap["contracts"]["NULLRAID First Breach"] = {
    "address": "0xdec01cdfb41e7871fb7ca7b12b1572ce292743c0",
    "status": "strong-lead-2026-11-07",
    "website": "https://nullraid.xyz",
    "websiteEvidence": "Situs mencetak kontrak persis 0xdec01cdfb41e7871fb7ca7b12b1572ce292743c0 (fetch browser.open run 1731, L129-130) + identitas cocok (5.555 First Breach, 1.111 free, fase Free/Early/Public) + tautan X https://x.com/nullraidxyz",
    "xAccount": "https://x.com/nullraidxyz (ditautkan situs sendiri + prompt mint situs; status 2118980799181869394)",
    "firstMintWib": "2026-11-07 15:15:27 WIB",
    "firstMintBlock": 132166957,
    "firstMintTx": "0xec74b288510bc720001476411e00bb57c47444782e995b5553bc491114c633d2",
    "totalSupply": 480, "freeMints": 480, "FREE_CAP": 1111, "MAX_SUPPLY": 5555,
    "freePct": 43.2, "phase": 1, "price": 0, "paused": 0, "remainingInPhase": 631,
    "phaseCap": 1111, "phaseMinted": 480,
    "freeClaims_user": False, "primaryMints_user": 0, "FREE_WALLET_CAP": 1,
    "balanceOf_user": 0,
    "lastReadBlock": REREAD_BLOCK, "lastReadWib": RUN,
    "note": ("Strong lead run 1731 (READ-ONLY run, TIDAK dieksekusi — menunggu keputusan parent): umur terverifikasi first mint "
        "2026-11-07 15:15:27 WIB (~2,7 jam, <=48 jam); free 480/1111 = 43,2% (>=25%); slot user terbuka (freeClaims(user)=false, "
        "FREE_WALLET_CAP=1, balanceOf(user)=0); website gate LOLOS (nullraid.xyz mencetak kontrak persis); narasi Binance Agentic Wallet / "
        "Agent ID (prompt mint situs mewajibkan skill Binance Agentic Wallet + Agent ID); diskusi publik: post Boltbook superhera.ai "
        "17:30 WIB + X @nullraidxyz. BUKAN kandidat: free% 43,2% < 50% dan velocity belum terhitung (tanpa prev rate). "
        "Sumber: run-2026-11-07-1731-nullraid-neogods.py + browser.open nullraid.xyz + leg2-1731.md."),
}
# --- New: NeoGods (watchlist-only) ---
snap["contracts"]["NeoGods"] = {
    "address": "0x2746bb6c6ec8fc968b8f0159618af1bb30ab593d",
    "status": "watchlist-only-2026-11-07",
    "totalSupply": 1700, "MAX_SUPPLY": 3333,
    "firstMintWib": "2026-11-07 09:54:06 WIB",
    "firstMintBlock": 132124121,
    "lastReadBlock": REREAD_BLOCK, "lastReadWib": RUN,
    "note": ("Watchlist-only run 1731: ditemukan via Boltbook superhera.ai 17:30 WIB (1.613/3.333 di post, 1.700/3.333 terverifikasi on-chain "
        "run ini); umur terverifikasi first mint 2026-11-07 09:54:06 WIB (~8 jam, <=48 jam); TAPI free% UNVERIFIED (semua free view revert, "
        "tanpa counter free) DAN website gate GAGAL (post menyatakan 'no website or socials confirmed'; contractURI None) -> BUKAN strong "
        "lead/kandidat. Sudah di hot-leg-seen (17:20 WIB, checked-not-sale-shape) + onchain-scan-seen (blok 131060640) — bukan first-seen run ini."),
}
# --- New: ADCHAR (early lead) ---
snap["contracts"]["ADCHAR"] = {
    "address": "0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044",
    "status": "early-lead-2026-11-07",
    "name": "代理者卡", "symbol": "ADCHAR",
    "totalSupply": None, "nextTokenId": 5,
    "firstSeenBlock": 132186401, "firstSeenWib": "2026-11-07 ~17:47 WIB",
    "mintCountWindow": 2, "distinctMintersWindow": 2,
    "lastReadBlock": REREAD_BLOCK, "lastReadWib": RUN,
    "note": ("Early lead run 1731: first-seen scan window 132185451-132186450 (mint pertama blok 132186401, 2 mint / 2 minter); Sourcify verified; "
        "agent-shaped: agentRegistry() -> wrapper 0x14bc39BF88e134D890a21F74eEA9DdB747433De9 yang registry()-nya = Agent ID registry "
        "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (terverifikasi on-chain run ini); claim() tanpa argumen, nonpayable (free, gas only); "
        "hasClaimed(user)=false (slot terbuka); nextTokenId=5 (4 token minted). Kaki lain UNVERIFIED: umur peluncuran (first-seen bukan launch time), "
        "free% (totalSupply/MAX_SUPPLY/free views revert), website/X (belum dicari). TIDAK PERNAH auto-mint/preview sebagai early lead. "
        "Sumber: onchain-scan-2026-11-07-1731.json + abi-adchar-1731.json + abi-14bc39-1731.json."),
}

# --- TRACK B — BINANCEAI light re-check (already reported once run 1701; NOT re-reported) ---
snap["binanceai_claim"] = {
    "status": "closed-refund-phase-2026-11-07",
    "mint": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    "token": "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c",
    "userShares": 1, "tokenClaimed_user": 0, "tokenBalance_user": 0,
    "launched": 0, "failed": 1, "isRefundPhase": 1, "totalShares": 3110,
    "verified_run": RUN, "verified_wib": TS, "block": None,
    "verify_method": "binanceai-grove.py (race) run 1731 — nilai IDENTIK run 1701 (block number race gagal, semua endpoint timeout, tapi pembacaan kontrak berhasil)",
    "note": "Re-check ringan run 1731: tetap fase refund/failed (failed=1, isRefundPhase=1, launched=0). SUDAH dilaporkan sekali run 1701 — TIDAK dilaporkan ulang run ini. Share user gratis — tidak ada dana yang perlu di-refund.",
}
snap["runNote1731_binanceai"] = (
    "Run 1731: BINANCEAI re-check ringan — nilai IDENTIK run 1701 (failed()=1, isRefundPhase()=1, launched()=0, totalShares()=3110, "
    "tokenClaimed(user)=0, tokenBalance(user)=0; block number race gagal/timeout tapi pembacaan kontrak berhasil). Sudah dilaporkan sekali run 1701; "
    "tracking pending claim tetap DITUTUP; TIDAK dilaporkan ulang. Grove: freeOpen 0, freeClaimed_user false."
)

snap["runNote1731_1107"] = (
    "Run 1731: 1 STRONG LEAD BARU + 1 EARLY LEAD BARU + 10 AGE-EXCLUSION. 0 kandidat baru, 0 track-C lead/kandidat baru, 0 pending claim baru/dibuka. "
    "STRONG LEAD: NULLRAID First Breach 0xdec01cdfb41e7871fb7ca7b12b1572ce292743c0 — umur terverifikasi first mint 2026-11-07 15:15:27 WIB (~2,7 jam); "
    "free 480/1111 = 43,2% (>=25%); slot user terbuka (freeClaims(user)=false, FREE_WALLET_CAP=1, balanceOf=0); website gate LOLOS (nullraid.xyz mencetak "
    "kontrak persis); narasi Binance Agentic Wallet/Agent ID; diskusi: post Boltbook superhera.ai 17:30 WIB + X @nullraidxyz. BUKAN kandidat (free% <50%, "
    "velocity belum terhitung). Run ini READ-ONLY — TIDAK dieksekusi; menunggu keputusan parent. "
    "EARLY LEAD: ADCHAR (代理者卡) 0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044 — first-seen scan window 132185451-132186450 (blok 132186401, 2 mint/2 minter); "
    "agent-shaped via wrapper 0x14bc39... -> registry 0x60B9...; claim() no-arg nonpayable; hasClaimed(user)=false; nextTokenId=5; umur/free%/website/X UNVERIFIED. "
    "WATCHLIST-ONLY BARU: NeoGods 0x2746bb6c6ec8fc968b8f0159618af1bb30ab593d — 1700/3333, first mint 09:54 WIB (~8 jam); free% UNVERIFIED + website gate GAGAL "
    "(post: 'no website or socials confirmed') -> bukan strong lead/kandidat. "
    "AGE-EXCLUSION (10, first mint 2026-11-05 ~17:18-17:19 WIB, 48,2 jam, dihapus dari snapshot): Dumpster Royalty 637/650, SIDEWAYS 342/555, Hoard 413/640, "
    "Slow & Steady 335/600, Monke Business 328/700, Very Good Boys 352/680, Do Not Disturb 386/525, Moth Club 446/666, Snail Mail 348/500, wheelz 340/620 — "
    "semuanya early-lead-reported-2026-11-05, belum sold out. "
    "Preflight PASS 10,6 dtk: head 132185381, 351 log/50 blok. "
    "Reread 452 kontrak + 67 track_c dalam 535,4 dtk (blok 132185959); free views (freeClaimed/freeMinted) SEMUA None (452/452, degradasi eth_call persisten) - "
    "nilai snapshot dipertahankan, BUKAN nol; totalSupply None di 103 kontrak; slotChanged 0. "
    "Velocity 1 pass: Cogito-COG-A +33 ratio 26,0 (artifak basis rendah, prev +1) — free% + umur + website UNVERIFIED -> BUKAN strong lead/kandidat. "
    "MORPHA +249 ratio 1,46 GAGAL tipis; Alchemister +149 ratio 0,35 GAGAL; WAR3 +121 ratio 0,61 GAGAL; Horus +27 ratio 0,42 GAGAL; BOT-UNIT +5 ratio 0,04 GAGAL. "
    "Sold out 35 (identik run 1701, 0 baru); near-sellout Dumpster Royalty 637/650 (sisa 13, flat — ikut terhapus age-exclusion). "
    "HIVE Agents totalSupply 1255 flat, balanceOf(user)=1, minted-by-user. "
    "Track C: 8 baris berubah (Crack 3221->3227, ORBITA 492M->527M, PLNK 512M->535M, Quonkers 163M->167M, Hobnorb 111M->112M, Wibblezap 125M->133M, "
    "Dribblon 99M->100M, Yammerjack 118M->119M). "
    "Scan leg: window 132185451-132186450 (1000 blok, cap; head 132186450), chunk 20/20 selesai (0 error), enrichment STALL di 113/166 -> timeout 700 dtk "
    "(SCAN_EXIT=124, pola stall berulang); 112 kontrak ter-enrich + 386 ERC-20-mint (partial JSON terselamatkan). 2 upaya background scan mati ~10:35 UTC "
    "(proses ter-reap) — scan sukses via foreground exec. Watermark TIDAK dimajukan run ini (tetap 132181588, milik backfill; backfill paralel menutup "
    "132181589-132184219 saat run ini). Gap tercatat 132181589-132185450 (backfill menutup bertahap). "
    "Triage scan: 1 first-seen (ADCHAR, di atas); 111 ter-enrich lain sudah dikenal. "
    "5c: 386 ERC-20, 51 >=10, 47 sudah dicek, 4 baru dicek (0xfAa7..., 0x3AD5..., 0xcC43..., 0xA879... — semuanya Sourcify not_verified), 0 sale-shape hit; "
    "checked list kini 2470 alamat. "
    "Sourcify feed 20 kontrak: 0 shape hit baru. CATATAN: 18/20 fetch ABI gagal 'Connection refused' (sourcify.dev tak terjangkau) — hanya 1 yang benar-benar "
    "dievaluasi (0x67135CDa... mint + freeLeft tapi tanpa registry -> no-shape); 19 lainnya INCONCLUSIVE, bukan verified no-shape. "
    "Track B: pending_claims kosong; BINANCEAI re-check identik run 1701 (refund/failed, sudah dilaporkan — tidak dilaporkan ulang); Grove freeOpen 0, "
    "freeClaimed_user false. "
    "Discovery (subagent, legs 2/3/6): Boltbook EN+ZH FRESH (curl 17:33 WIB, HTTP 200, 25 kartu, isi identik, rotasi penuh vs 1701) + 4 author post deep-read — "
    "NeoGods + NULLRAID (di atas); nama baru tanpa kontrak: Paw Gang (buka malam ini 20:00 WIB, pawgang.pages.dev), Wuyuhive (kontrak terpotong). "
    "Sweep EN+ZH + Square/Odaily/PANews/DappBay — 0 proyek baru. M3M3: census gate deadline 5 Nov lewat (31/8.900, refund phase per situs), mint masih LIVE. "
    "Razor Agent genesis BELUM dimulai (pair masih kosong). WHALE NFT kontrak B ~1.832/5.000, tanpa website/X -> gate GAGAL, bukan kandidat. "
    "Bridge: tidak berubah (mtime 2026-11-06 02:48); 33 kontrak tidak di snapshot (1 same_owner_discarded=True, 32 temuan seeded 2026-11-03 sudah dilaporkan) — 0 promosi. "
    "Age sweep: REMOVE 10 (di atas); 44 dipertahankan; 374 umur UNVERIFIED tetap watchlist-only."
)
snap["last_run"] = RUN
snap["last_run_wib"] = TS
tmp = f"{BASE}/onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, f"{BASE}/onchain-snapshot.json")

# seen file: append ADCHAR (first-seen this run)
seen_path = f"{BASE}/onchain-scan-seen.json"
seen = json.load(open(seen_path))
seen.setdefault("contracts", {})["0x6e8b05c2dd1c625d839f33f60b837d9af25e6044"] = 132186401
seen["_meta"]["contracts_count"] = len(seen["contracts"])
with open(seen_path, "w") as f:
    json.dump(seen, f, indent=1)

# state note (scan partial; watermark untouched by this run)
st_path = f"{BASE}/onchain-scan-state.json"
st = json.load(open(st_path))
st["note_1731_scan_partial"] = (
    "Run 1731 scan (route 4): window 132185451-132186450 (1000 blok, cap dari head 132186450), chunk 20/20 selesai "
    "(0 error), enrichment STALL di 113/166 -> timeout 700 dtk (SCAN_EXIT=124, pola stall berulang seperti run 1601/1631/1701); "
    "112 kontrak ter-enrich + 386 ERC-20-mint (partial JSON terselamatkan, partial=True). 2 upaya background scan mati ~10:35 UTC "
    "(proses ter-reap saat handoff subagent) — scan sukses via foreground exec. Watermark TIDAK dimajukan run ini "
    "(tetap 132181588, milik backfill; backfill paralel menutup 132181589-132184219 saat run ini). Gap tercatat 132181589-132185450. "
    "Triage scan 1 first-seen (ADCHAR 0x6E8b05... early lead); 5c 0 hit."
)
with open(st_path, "w") as f:
    json.dump(st, f, indent=1)
print(f"FINALIZE-1731 updated={updated} none_free={none_free} vel_updated={vel_updated} removed_age={len(removed)} contracts={len(snap['contracts'])} track_c={len(snap.get('track_c', {}))} ts={TS}", flush=True)
for r in removed:
    print(" REMOVED-AGE", r["name"], r["firstMintWib"], f"{r['ageHours']}h", r["curSupply"], "/", r["maxSupply"], flush=True)
