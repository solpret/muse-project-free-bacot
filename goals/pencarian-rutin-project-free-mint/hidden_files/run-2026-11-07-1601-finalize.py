#!/usr/bin/env python3
"""Finalize run 1601 — applies reread/velocity, writes run notes.
Reloads snapshot at write time; atomic write."""
import json, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132175076
NOW = datetime.now(timezone(timedelta(hours=7)))
TS = NOW.strftime("%Y-%m-%d %H:%M WIB")
RUN = "2026-11-07 run 1601"

re = json.load(open(f"{BASE}/run-2026-11-07-1601-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1601-velocity.json"))

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
updated = 0; none_free = 0
for name, d in re["reread"].items():
    c = snap["contracts"].get(name)
    if c is None: continue
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if d.get(k) is not None: c[k] = d[k]
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

onlyai = snap["contracts"].get("ONLYAI-Crystals")
if onlyai is not None:
    onlyai["velocityNote1601"] = ("Run 1601 (blok 132175076, interval 19,7 mnt vs run 1531): 1768->1794 (+26, "
        "1,32/mnt, ratio 2,53 vs prev 0,52/mnt) -> velocity LOLOS, TAPI TIDAK promosi: free% UNVERIFIED "
        "(semua free view revert; Sourcify IncompleteRead; freePct snapshot None) + slot user UNVERIFIED; "
        "launch terverifikasi 2026-11-07 01:00 WIB (~15,5 jam, <=48 jam). Bukan strong lead (butuh >=25% free "
        "terverifikasi + slot terbuka) dan bukan kandidat (butuh 50% free + X + website). Tetap watchlist.")
alc = snap["contracts"].get("Alchemister-0xCafEEDDF")
if alc is not None:
    alc["velocityNote1601"] = ("Run 1601 (blok 132175076): +79 dalam interval, rate 4,01/mnt, ratio 1,26 vs prev "
        "-> velocity GAGAL (<1,5x). Free% tetap UNVERIFIED; status early-lead-backfill; bukan strong lead/kandidat.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote1601"] = (f"Run 1601 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 1531 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.")
war3 = snap["contracts"].get("WAR3-1aa9")
if war3 is not None:
    war3["runNote1601"] = ("Run 1601: totalSupply 874->1057 (+183 dalam ~19,7 mnt, 9,29/mnt); velocity TIDAK lolos "
        "(belum ada prev rate); first mint 2026-11-07 14:25:04 WIB, early-lead-backfill; free% snapshot 0,63% "
        "(19/3000) << 25% -> BUKAN strong lead. +183 tidak bisa dibedakan free vs paid (PRICE 0,0017 BNB) "
        "karena freeMinted segar None. Butuh baca freeMinted segar run berikut.")

snap["runNote1601_1107"] = (
    "Run 1601: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru dari kaki job ini, "
    "0 track-C lead/kandidat baru dari kaki job ini, 0 pending claim baru/dibuka. 0 perubahan dilaporkan. "
    "Preflight PASS 19,0 dtk: head via fast_rpc batch dulu (ankr eth_blockNumber tidak didukung) — head 132175023, 247 log/50 blok. "
    "Reread 453 kontrak + 67 track_c dalam 715,3 dtk (blok 132175076, interval 2626 blok ~19,7 mnt vs run 1531); free views "
    "(freeClaimed/freeMinted) SEMUA None (453/453, degradasi eth_call seperti run 1401/1431/1501/1531) - nilai snapshot dipertahankan, "
    "BUKAN nol; totalSupply+totalMinted None di 103 kontrak; balanceOf(user) None di 102 kontrak; track_c fresh free views 0/67; slotChanged 0. "
    "Velocity 1 pass, 0 promosi: ONLYAI-Crystals +26 ratio 2,53 (free% UNVERIFIED — semua free view revert, Sourcify IncompleteRead; "
    "slot user UNVERIFIED; launch terverifikasi 01:00 WIB ~15,5 jam). Alchemister-0xCafEEDDF +79 ratio 1,26 (velocity GAGAL); "
    "WAR3-1aa9 +183 (belum ada prev rate; free% 0,63% -> bukan strong lead). "
    "Sold out 35 (identik run 1531, 0 baru); near-sellout Dumpster Royalty 637/650 (sisa 13, flat vs 1531); HIVE Agents totalSupply 1255 flat, balanceOf(user)=1, minted-by-user. "
    "Scan leg: window 132174059-132175058 (1000 blok, cap) chunk 20/20 selesai (0 error, 40 Ankr calls), enrichment STALL di 62/175 "
    "-> SCAN_EXIT=124 (timeout 700 dtk); 61 kontrak ter-enrich + 380 ERC-20-mint (partial JSON terselamatkan). Watermark TIDAK dimajukan "
    "run ini (milik backfill; backfill paralel 132171166-132174074 sedang jalan). Gap: 113 kontrak window tidak ter-enrich "
    "(alamat tidak terpulihkan dari output parsial) -> backfill. "
    "Triage scan: 0 first-seen (61 ter-enrich semua sudah dikenal); stuck address 0x1a7a8BbB49e3e8Cf951996789Fd69d4C7524A2B4 sudah dikenal. "
    "5c: 42 ERC-20 >=10, 36 sudah dicek, 6 baru dicek (0x839750eB54A0BA54D27975C30b1369219DA7f1d8, 0xb22b374DACddBFdee72647c953454e7aDa7f91ba, "
    "0xF05b0F9C2Cd52056D30850Ac1101788e88bA4b7D, 0xaB5708ADB73a1B1Ce998d49DBF648b5f430b7014, 0x93560283bc2e07f2b2b976cEbf3685dE42687AcD, "
    "0xA2eB0437ed80cB716Df99B28A138b9c240270fF8, semuanya Sourcify not_verified), 0 sale-shape hit. "
    "Sourcify feed 20 kontrak: 0 shape hit baru. "
    "Track B: BINANCEAI launched()=0, failed()=1, isRefundPhase()=1, totalShares()=3110, tokenClaimed(user)=0 — tetap fase refund/failed, "
    "tidak ada aksi; Grove freeOpen 0, freeClaimed_user false (blok 132175322). pending_claims kosong. "
    "Discovery (subagent, legs 2/3/6): Boltbook EN+ZH FRESH (curl 16:16 WIB, post 37 dtk s.d. ~12 mnt, 25 post identik EN/ZH) + 3 author post "
    "deep-read + sweep EN+ZH + Square/Odaily/PANews/DappBay (321 entri) — 0 item benar-benar baru; semua sudah dikenal. NOVRA free lane "
    "CLOSED (72/72, freeRemaining 0, blok ~132173917); Godceo (ODCEO) nama tanpa alamat kontrak — tidak bisa diverifikasi sebagai baru; "
    "Odyssey mining vault 0xFfcFF68E44c41021fb20894F540FE3AA51549157 komponen proyek KNOWN Odyssey, bukan proyek baru; Xigo snippet masih "
    "iklan free padahal pool habis (stale). Ptah cutoff mint 8 Nov 11:44 WIB. "
    "Bridge: tidak berubah (115 entri, terakhir diubah 2026-11-06 02:48; 33 belum di snapshot — semuanya first-seen 3-6 Nov, sudah lewat "
    "umur 48 jam; 7 same_owner_discarded; 0 promosi). "
    "Age sweep: 0 REMOVE; 44 dipertahankan (minted-by-user/same-owner-discarded/sold-out); 374 umur UNVERIFIED tetap watchlist-only. "
    "Aturan diam berlaku — tidak ada laporan chat dari run ini."
)
snap["last_run"] = RUN
snap["last_run_wib"] = TS
tmp = f"{BASE}/onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, f"{BASE}/onchain-snapshot.json")
print(f"FINALIZE-1601 updated={updated} none_free={none_free} contracts={len(snap['contracts'])} track_c={len(snap.get('track_c', {}))} ts={TS}", flush=True)
