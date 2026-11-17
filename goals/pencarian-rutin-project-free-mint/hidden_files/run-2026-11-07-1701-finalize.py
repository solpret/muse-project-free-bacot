#!/usr/bin/env python3
"""Finalize run 1701 — generic: applies reread/velocity to snapshot (reload at
write time), records BINANCEAI refund-phase closure, scan-partial note in
state (watermark NOT advanced by this run; backfill advanced it separately).
Atomic snapshot write."""
import json, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132181309
NOW = datetime.now(timezone(timedelta(hours=7)))
TS = NOW.strftime("%Y-%m-%d %H:%M WIB")
RUN = "2026-11-07 run 1701"

re = json.load(open(f"{BASE}/run-2026-11-07-1701-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1701-velocity.json"))

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

hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote1701"] = (f"Run 1701 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 1631 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.")
alc = snap["contracts"].get("Alchemister-0xCafEEDDF")
if alc is not None:
    alc["velocityNote1701"] = ("Run 1701 (blok 132181309): totalSupply 2959->3290 (+331, rate 12,06/mnt, ratio 5,81 vs prev) "
        "-> velocity LOLOS; free% tetap UNVERIFIED (free views None run ini + tidak ada ABI Sourcify); website UNVERIFIED; "
        "xVerified False; BUKAN strong lead (kaki free% >=25% tidak terverifikasi) dan BUKAN kandidat. Tetap early-lead-backfill.")
bot = snap["contracts"].get("BOT-UNIT")
if bot is not None:
    bot["velocityNote1701"] = ("Run 1701 (blok 132181309): totalSupply 1282->1385 (+103, rate 3,75/mnt, ratio 72,42 vs prev "
        "0,05) -> velocity LOLOS; umur first mint 2026-11-07 02:56:47 WIB (~14,3 jam, <=48 jam); website https://bot-unit.xyz "
        "terverifikasi; slot user terbuka (quote 0, hasFreeMint True); TAPI free% UNVERIFIED (tidak ada counter free yang terbaca) "
        "-> BUKAN strong lead (kaki >=25% tidak terverifikasi) dan BUKAN kandidat. Tetap early lead (dilaporkan run 0931).")
hor = snap["contracts"].get("Horus AI")
if hor is not None:
    hor["velocityNote1701"] = ("Run 1701 (blok 132181309): totalSupply 1518->1569 (+51, rate 1,86/mnt, ratio 1,71 vs prev) "
        "-> velocity LOLOS; umur first mint 2026-11-06 20:12:51 WIB (~21 jam, <=48 jam); freeSupply 2000/10000 terbaca tapi free path "
        "PARTIAL/UNVERIFIED (tanpa ABI, tanpa quote) -> free% tidak terverifikasi -> BUKAN strong lead dan BUKAN kandidat. "
        "xVerified False. Tetap early-lead-backfill.")

# TRACK B — BINANCEAI refund/failed phase (verified 2x: script + direct eth_call)
snap["binanceai_claim"] = {
    "status": "closed-refund-phase-2026-11-07",
    "mint": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    "token": "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c",
    "userShares": 1, "tokenClaimed_user": 0, "tokenBalance_user": 0,
    "launched": 0, "failed": 1, "isRefundPhase": 1, "totalShares": 3110,
    "verified_run": RUN, "verified_wib": TS, "block": 132183305,
    "verify_method": "binanceai-grove.py (race) + direct eth_call bsc-dataseed1 (keccak selectors) — kedua pembacaan cocok",
    "note": "Klaim tidak pernah terbuka (launched 0 sejak 2026-11-01); proyek masuk fase refund/failed. Dilaporkan sekali run ini; "
            "dihapus dari tracking pending claim per aturan track B. Share user gratis (free share, tanpa pembayaran) sehingga "
            "tidak ada dana user yang perlu di-refund dari klaim ini.",
}
snap["runNote1701_binanceai"] = (
    "Run 1701: BINANCEAI (binanceai.fun) MASUK FASE REFUND/FAILED — failed()=1, isRefundPhase()=1, launched()=0, "
    "totalShares()=3110, tokenClaimed(user)=0, tokenBalance(user)=0 (blok 132183305; terverifikasi 2x: skrip + direct eth_call). "
    "Klaim tidak pernah terbuka sejak pending 2026-11-01. Dilaporkan sekali run ini; tracking pending claim DIHAPUS. "
    "Share user gratis (tanpa pembayaran) — tidak ada dana yang perlu di-refund."
)

snap["runNote1701_1107"] = (
    "Run 1701: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru dari kaki job ini, "
    "0 track-C lead/kandidat baru, 0 pending claim baru/dibuka. 1 PERUBAHAN dilaporkan: BINANCEAI masuk fase refund/failed "
    "(failed()=1, isRefundPhase()=1, launched()=0 — terverifikasi 2x) -> klaim pending ditutup + tracking dihapus. "
    "Preflight PASS 18,2 dtk: head 132181209, 640 log/50 blok. "
    "Reread 452 kontrak + 67 track_c dalam 683,8 dtk (blok 132181309); free views (freeClaimed/freeMinted) SEMUA None (452/452, "
    "degradasi eth_call persisten) - nilai snapshot dipertahankan, BUKAN nol; totalSupply None di 103 kontrak; slotChanged 0. "
    "Velocity 3 pass: Alchemister-0xCafEEDDF +331 ratio 5,81; BOT-UNIT +103 ratio 72,42; Horus AI +51 ratio 1,71 — ketiganya "
    "BUKAN strong lead/kandidat karena free% UNVERIFIED (BOT-UNIT: website + slot user terverifikasi, tapi tanpa counter free; "
    "Alchemister: website unverified; Horus: free path partial). WAR3-1aa9 +156 ratio 0,65 GAGAL; ONLYAI-Crystals +18 ratio 1,26 GAGAL; "
    "MORPHA +134 tanpa prev rate. Sold out 35 (identik run 1631, 0 baru); near-sellout Dumpster Royalty 637/650 (sisa 13, flat); "
    "HIVE Agents totalSupply 1255 flat, balanceOf(user)=1, minted-by-user. "
    "Track C: 6 baris berubah (Crack 3216->3221, ORBITA 451M->492M, PLNK 502M->512M, Quonkers 150M->163M, Hobnorb 108M->111M, "
    "Wibblezap 111M->125M). "
    "Scan leg: window 132180645-132181644 (1000 blok, cap) chunk 20/20 selesai (0 error, 40 Ankr calls), enrichment STALL di 66/139 "
    "-> timeout 700 dtk (pola stall berulang); 65 kontrak ter-enrich + 375 ERC-20-mint (partial JSON terselamatkan). Watermark TIDAK "
    "dimajukan run ini (backfill paralel memajukannya terpisah 132179195->132181588). Gap 132174075-132180644 ditutup backfill. "
    "Triage scan: 0 first-seen (65 ter-enrich semua sudah dikenal; registry excluded). "
    "5c: 375 ERC-20, 56 >=10, 51 sudah dicek, 5 baru dicek (0xD6AF..., 0x46c2..., 0x4De9..., 0x74Eb..., 0x0CAc... — semuanya Sourcify "
    "not_verified), 0 sale-shape hit; checked list kini 2466 alamat. "
    "Sourcify feed 20 kontrak: 0 shape hit baru (S1/S2/agent-mint). 0xbd4B... punya mint+free_supply/freeClaimed/freeMinted tapi tanpa "
    "registry -> no-shape, bukan lead. 0x0b37... semua view gagal baca (OSError) — tetap unverified, bukan lead. "
    "Track B: Grove freeOpen 0, freeClaimed_user false (blok 132183305). pending_claims kosong. "
    "Backfill overlap 132179196-132181588: 3 first-seen (Abyssora 0x3B8A... 16 mint, 0xD1c4... PRICE 0,0005 BNB = paid, 0xAccE... "
    "semua view gagal) — ketiganya BUKAN agent-shaped (registry False/not_verified, tanpa free-mint terverifikasi) -> bukan early lead, "
    "tidak ada aksi run ini; triase milik job backfill. "
    "Discovery (subagent, legs 2/3/6): Boltbook EN+ZH FRESH (curl ~17:03-17:10 WIB, 25 kartu post, isi identik) + 8 author post deep-read "
    "— 0 lead baru (ORBITA, WAR3, NIGHT, Shard Id, M3MO, Dark x Loot, FORGE/Deltavane/HIPPO tanpa kontrak). Sweep EN+ZH + Square/Odaily/"
    "PANews/DappBay — 0 lead baru. M3M3 totalMinted segar 5712 (+11 vs 1631), mintOpen 1, balanceOf(user)=0, umur >48 jam (age-excluded). "
    "Razor Agent genesis BELUM dimulai (pair masih kosong di params.json). WHALE NFT kontrak B 1829/5000 (36,6%) tapi tanpa website/X "
    "-> gate website GAGAL, bukan kandidat; kontrak A sold out 5000/5000. "
    "Bridge: tidak berubah (mtime 2026-11-06 02:48; 0 promosi). Age sweep: REMOVE 0; 44 dipertahankan; 374 umur UNVERIFIED tetap watchlist-only."
)
snap["last_run"] = RUN
snap["last_run_wib"] = TS
tmp = f"{BASE}/onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, f"{BASE}/onchain-snapshot.json")

# state note (scan partial; watermark untouched by this run)
st_path = f"{BASE}/onchain-scan-state.json"
st = json.load(open(st_path))
st["note_1701_scan_partial"] = (
    "Run 1701 scan (route 4): window 132180645-132181644 (1000 blok, cap dari head 132181644), chunk 20/20 selesai "
    "(0 error, 40 Ankr calls), enrichment STALL di 66/139 -> timeout 700 dtk (pola stall berulang seperti run 1601/1631); "
    "65 kontrak ter-enrich + 375 ERC-20-mint (partial JSON terselamatkan, partial=True). Watermark TIDAK dimajukan run ini "
    "(tetap milik backfill; backfill paralel memajukan 132179195->132181588 terpisah). Gap 132174075-132180644 ditutup backfill. "
    "Triage scan 0 first-seen; 5c 0 hit."
)
with open(st_path, "w") as f:
    json.dump(st, f, indent=1)
print(f"FINALIZE-1701 updated={updated} none_free={none_free} vel_updated={vel_updated} contracts={len(snap['contracts'])} track_c={len(snap.get('track_c', {}))} ts={TS}", flush=True)
