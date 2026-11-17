#!/usr/bin/env python3
"""Finalize run 1631 — applies reread/velocity, removes DinoEra (age-excluded),
records scan partial in state (watermark NOT advanced). Reloads snapshot at
write time; atomic write."""
import json, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132177648
NOW = datetime.now(timezone(timedelta(hours=7)))
TS = NOW.strftime("%Y-%m-%d %H:%M WIB")
RUN = "2026-11-07 run 1631"

re = json.load(open(f"{BASE}/run-2026-11-07-1631-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1631-velocity.json"))

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

# velocity fields for NFT-sized rows only (skip token supplies > 1e6)
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
    hive["runNote1631"] = (f"Run 1631 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 1601 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.")
war3 = snap["contracts"].get("WAR3-1aa9")
if war3 is not None:
    war3["runNote1631"] = ("Run 1631: totalSupply 1057->1225 (+168 dalam ~19,3 mnt, 8,71/mnt); velocity TIDAK lolos "
        "(belum ada prev rate); first mint 2026-11-07 14:25:04 WIB, early-lead-backfill; free% snapshot 0,63% "
        "(19/3000) << 25% -> BUKAN strong lead. +168 tidak bisa dibedakan free vs paid (PRICE 0,0017 BNB) "
        "karena freeMinted segar None.")
alc = snap["contracts"].get("Alchemister-0xCafEEDDF")
if alc is not None:
    alc["velocityNote1631"] = ("Run 1631 (blok 132177648): +40 dalam interval, rate 2,07/mnt, ratio 0,65 vs prev "
        "-> velocity GAGAL (<1,5x). Free% tetap UNVERIFIED; status early-lead-backfill; bukan strong lead/kandidat.")
onlyai = snap["contracts"].get("ONLYAI-Crystals")
if onlyai is not None:
    onlyai["velocityNote1631"] = ("Run 1631 (blok 132177648): +10 dalam interval, ratio 0,99 -> velocity GAGAL; "
        "streak pass run 1601 berakhir. Free% UNVERIFIED (semua free view None); slot user UNVERIFIED; "
        "launch terverifikasi 2026-11-07 01:00 WIB (~15,8 jam, <=48 jam). Tetap watchlist.")

# AGE EXCLUSION — DinoEra (48h rule)
dino = snap["contracts"].pop("DinoEra", None)
dino_removed = dino is not None
if dino_removed:
    rec = {"name": "DinoEra", "address": "0xb7ae3eF58f4507a29115DEc6Eb8De7fEEcc3b6C4",
           "firstMintWib": "2026-11-05T16:17:48+07:00", "ageHours": 48.5,
           "supply": 61, "maxSupply": 10000, "free": "4/6000 = 0,07%",
           "status_before": "early-lead-reported-run1601",
           "removed_run": RUN, "removed_wib": TS,
           "reason": "Umur peluncuran terverifikasi 48,5 jam (>48 jam) dan belum sold out (61/10000); "
                     "dihapus dari watchlist aktif per aturan umur 48 jam; dilaporkan sekali run ini."}
    snap.setdefault("age_exclusions", []).append(rec)

snap["runNote1631_1107"] = (
    "Run 1631: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru dari kaki job ini, "
    "0 track-C lead/kandidat baru dari kaki job ini, 0 pending claim baru/dibuka. 1 PERUBAHAN dilaporkan: "
    "DinoEra AGE-EXCLUDED (first mint terverifikasi 2026-11-05 16:17:48 WIB, umur 48,5 jam > 48 jam, supply 61/10000 "
    "belum sold out, free 4/6000 = 0,07%) — dihapus dari watchlist aktif, dilaporkan sekali. "
    "Preflight PASS 16,3 dtk: head via fast_rpc batch dulu — head 132177509, 323 log/50 blok. "
    "Reread 453 kontrak + 67 track_c dalam 667,4 dtk (blok 132177648, interval 2572 blok ~19,3 mnt vs run 1601); free views "
    "(freeClaimed/freeMinted) SEMUA None (453/453, degradasi eth_call persisten seperti run 1401-1601) - nilai snapshot dipertahankan, "
    "BUKAN nol; totalSupply None di 103 kontrak; track_c fresh free views 0/67; slotChanged 0. "
    "Velocity 0 pass: WAR3-1aa9 +168 (belum ada prev rate; free% 0,63% -> bukan strong lead), Alchemister-0xCafEEDDF +40 ratio 0,65 "
    "(GAGAL), AgentVOLT (round 1) +34 ratio 0,66 (GAGAL), Horus AI +21 ratio 0,19 (GAGAL); ONLYAI-Crystals streak pass 1601 berakhir "
    "(+10, ratio 0,99). Strong-lead screening 10 hit awal semua gugur (same-owner-discarded 7, minted-by-user 1, age-excluded 2). "
    "Sold out 35 (identik run 1601, 0 baru); near-sellout Dumpster Royalty 637/650 (sisa 13, flat); HIVE Agents totalSupply 1255 flat, balanceOf(user)=1, minted-by-user. "
    "Track C: 9 baris berubah (ORBITA 426M->451M, PLNK 496M->502M, Quonkers 134M->150M, Hobnorb 99M->108M, Wibblezap 96M->111M, "
    "Dribblon 93M->99M, Yammerjack 116M->118M, LuckyBox-LUCK 677->680); ORBITA balanceOf(user) tetap 1e24 = 1.000.000 ORBITA "
    "(sama dengan mintedAmount 1 share free, bukan saldo baru). "
    "Scan leg: window 132176536-132177535 (1000 blok, cap) chunk 20/20 selesai (0 error, 40 Ankr calls), enrichment STALL di 63/196 "
    "-> timeout 700 dtk (pola stall berulang seperti run 1601); 62 kontrak ter-enrich + 339 ERC-20-mint (partial JSON terselamatkan). "
    "Watermark TIDAK dimajukan (milik backfill). Gap 132174075-132176509 (2435 blok) tidak ter-scan run ini -> backfill. "
    "Triage scan: 0 first-seen (62 ter-enrich semua sudah dikenal; registry excluded). "
    "5c: 339 ERC-20, 52 >=10, 46 sudah dicek, 6 baru dicek (0x3323dEe31c97C2514b01Ae5dfAaBbd980b226Cba, "
    "0xA0717F8934101163C6A67FC3037Fb8529587a1b8, 0x7AF6290a04E4FA7fA443E584330b5c48aF6D2229, "
    "0x6927C7693d4B188ef9B147D53ae0c042b0B15D8f, 0xfD034F695589b54a80D5CBCa04D94129d5003a8B, "
    "0x81EbCa8Ef74f47fBC03f6AA53C9932e9cf716763 — semuanya Sourcify not_verified), 0 sale-shape hit. "
    "Sourcify feed 20 kontrak: 0 shape hit baru (S1/S2/agent-mint). 0x0b37150c92169Cc7f8953711c0bf6d461dc19111 punya claimFree/mintFree "
    "+ freeUsed tapi tanpa registry di ABI; cek on-chain langsung gagal total (OSError, degradasi RPC) — tetap unverified, bukan lead. "
    "Track B: BINANCEAI launched()=0, totalShares()=3110, tokenClaimed(user)=0, tokenBalance(user)=0 — masih pending, tidak ada aksi; "
    "failed()/isRefundPhase() gagal baca sementara (OSError, bukan perubahan state); Grove freeOpen 0, freeClaimed_user false (blok 132178140). pending_claims kosong. "
    "Discovery (subagent, legs 2/3/6): Boltbook EN+ZH FRESH (curl ~16:34-16:36 WIB, 24 kartu post, blok ~132176867-132177041) + 3 author post "
    "deep-read (BOT-UNIT/AGOAT/ORCHIDIA, NIGHT 9350/10000, ORBIT free habis — ketiganya tanpa alamat kontrak) + sweep EN+ZH + Square/Odaily/PANews/DappBay — "
    "0 lead baru. M3M3 AGENT/M3MO (0x08BE8a0727b6fc801171c1F4F4Dd547EA44Ca339) muncul di sweep tapi SUDAH dikenal job ini (first-seen blok 131646932, "
    "run 2026-11-04-2201-scan; umur >48 jam, age-excluded); cek on-chain run ini: totalMinted 5701, mintOpen 1, balanceOf(user) 0, free views gagal baca. "
    "Razor Agent genesis belum dimulai (startGenesis() belum dipanggil, pair kosong) — tetap upcoming watchlist Track C. "
    "WHALE NFT kontrak B (0xf81b542c41f982a7d7a8e2ee8cab5feee6203218) masih minting tapi tanpa website/X — gate website gagal, bukan kandidat. "
    "Bridge: tidak berubah (115 entri, terakhir diubah 2026-11-06 02:48; 0 promosi). "
    "Age sweep: REMOVE 1 (DinoEra); 44 dipertahankan (minted-by-user/same-owner-discarded/sold-out); 374 umur UNVERIFIED tetap watchlist-only."
)
snap["last_run"] = RUN
snap["last_run_wib"] = TS
tmp = f"{BASE}/onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, f"{BASE}/onchain-snapshot.json")
print(f"FINALIZE-1631 updated={updated} none_free={none_free} vel_updated={vel_updated} dino_removed={dino_removed} contracts={len(snap['contracts'])} track_c={len(snap.get('track_c', {}))} ts={TS}", flush=True)
