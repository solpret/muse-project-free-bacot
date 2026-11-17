#!/usr/bin/env python3
"""Merge run 0031 reread+vel+legs into snapshot. Read-only except snapshot +
hot-leg-seen.json (dedupe for the 20 newly shape-checked contracts).
Run 0031 (jadwal 00:31 WIB 2026-11-11). Age-excluded entries are kept as
tombstones (status age-excluded-2026-11-11), like prior runs' GHOST etc."""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-11-0031"
NOW = "2026-11-11 00:31 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
legs = json.load(open(f"{BASE}/run-{TS}-legs.json"))
BLOCK = rr.get("block")
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0031-premerge")

updated = 0
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    row = vel.get("rows", {}).get(name, {})
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    if row.get("minted") is not None:
        entry["previousTotalSupply"] = row.get("prev")
        entry["mintedInInterval"] = row.get("minted")
        entry["intervalMinutes"] = INTERVAL
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1
print(f"contracts updated: {updated}")

tc_updated = 0
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("track_c", {}).get(name)
    if not f:
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    tc_updated += 1
print(f"track_c updated: {tc_updated}")

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote0031_1111"] = text

def dyn_note(name, extra_txt=""):
    row = vel.get("rows", {}).get(name, {})
    f = rr.get("reread", {}).get(name, {})
    e = snap["contracts"].get(name, {})
    if not row:
        return None
    minted = row.get("minted"); rate = row.get("rate"); ratio = row.get("ratio")
    passes = row.get("passes")
    fm = f.get("freeMinted"); fc = f.get("freeClaimed")
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP") or e.get("agentFreeCap") or e.get("MAX_SUPPLY")
    freetxt = ""
    if fm is not None and cap and cap < 10**12:
        freetxt = f"; freeMinted {fm}/{cap} = {fm/cap*100:.1f}%"
    elif fc is not None and cap and cap < 10**12:
        freetxt = f"; freeClaimed {fc}/{cap} = {fc/cap*100:.1f}%"
    vtxt = "velocity LOLOS" if passes else "velocity GAGAL"
    return (f"Run 0031 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

# ---- SOLDERCATS: probe segar run ini ----
sc = snap["contracts"].get("SOLDERCATS")
if isinstance(sc, dict):
    p = legs.get("probe", {}).get("SOLDERCATS", {})
    if p.get("totalSupply") is not None:
        sc["totalSupply"] = p["totalSupply"]
    if p.get("agentFreeUsed") is not None:
        sc["agentFreeUsed"] = p["agentFreeUsed"]
        sc["agentFree"] = p["agentFreeUsed"]
    sc["runNote0031_1111"] = (
        f"Run 0031: probe segar (nodereal, blok ~{BLOCK}): totalSupply {p.get('totalSupply')} "
        f"(was 395 run 0001), agentFreeUsed {p.get('agentFreeUsed')}/2000 = "
        f"{(p.get('agentFreeUsed') or 0)/2000*100:.2f}% (masih <25% strong lead). Re-read +19/30 mnt = "
        f"0,63/mnt, velocity ratio 0,79 GAGAL run ini. mintOpen 1, "
        f"mintStart 1794321310 = 2026-11-10 21:35 WIB (umur ~3 jam TERVERIFIKASI <24 jam), slot user "
        f"TERBUKA (agentFreeByWallet 0, balanceOf 0). Website SUDAH terverifikasi (metode H, run 2201). "
        f"Tetap early lead; re-read totalSupply 414 (blok {BLOCK}).")
    print("SOLDERCATS updated (still early)")

# ---- NIGHTFORGE: gate rechecked, still failed ----
nf = snap["contracts"].get("NIGHTFORGE")
if isinstance(nf, dict):
    p = legs.get("probe", {}).get("NIGHTFORGE", {})
    if p.get("totalSupply") is not None:
        nf["totalSupply"] = p["totalSupply"]
    if p.get("agentFreeUsed") is not None:
        nf["agentFreeUsed"] = p["agentFreeUsed"]
    nf["runNote0031_1111"] = (
        f"Run 0031: totalSupply {p.get('totalSupply')} (was 674 run 0001), agentFreeUsed "
        f"{p.get('agentFreeUsed')}/2000 = {(p.get('agentFreeUsed') or 0)/2000*100:.1f}% (tetap >=25% strong "
        f"lead). Gate DICEK ULANG run ini (metode H + I + J + G): nightforge.pages.dev home + "
        f"/meta/collection.json + /llms.txt + /skill.md + /launch.json + /agent.json SEMUA tetap halaman "
        f"infografis medis yang sama (23.809 byte, 0 kecocokan kontrak); ABI Sourcify exact_match 87 fns "
        f"tanpa fungsi site/URL (metode J, hanya eip712Domain); pencarian nama proyek tanpa hasil situs "
        f"(metode G) -> gate TETAP GAGAL, TIDAK di-preview/TIDAK di-mint. Status tetap "
        f"strong-lead-gate-blocked-2026-11-10 (sudah dilaporkan sekali run 2131; tidak dilaporkan ulang). "
        f"Deadline umur 2026-11-11 14:36 WIB.")
    print("NIGHTFORGE gate rechecked (still failed)")

note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user-2026-11-02; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") + " Minted-by-user-2026-11-01; tanpa perubahan.")
note("BYTEBLOOM", (dyn_note("BYTEBLOOM") or "") + " Minted-by-user run 2201 (#508); slot terpakai; tanpa perubahan.")
note("EMBERANVIL", (dyn_note("EMBERANVIL") or "") + " Minted-by-user-2026-11-10 (#946); tanpa perubahan.")
note("KERNELMONK", (dyn_note("KERNELMONK") or "") + " Minted-by-user-2026-11-10 (#509); tanpa perubahan.")
note("Lanternfield", (dyn_note("Lanternfield") or "") + " Minted-by-user-2026-11-10 (#516); tanpa perubahan.")
note("Cosmic Sentinel", (dyn_note("Cosmic Sentinel") or "") +
     " Early lead; freeMinted 366/225.000 = 0,16% (jauh <25%); umur UNVERIFIED; tanpa perubahan.")
note("ORBITJANITOR", (dyn_note("ORBITJANITOR") or "") +
     " Minted-by-user run 0001 (#552); re-read 552->592 (+40, velocity GAGAL 0,61x); tanpa perubahan.")
note("Claf Eye", (dyn_note("Claf Eye") or "") +
     " Early lead; velocity LOLOS run ini (+25, 2,50x) TAPI TANPA promosi: free% UNVERIFIED (free views "
     "null) + umur UNVERIFIED + website UNVERIFIED (claf.markets tercatat tapi belum terverifikasi "
     "mencetak kontrak). Tetap early lead.")
note("STALL", (dyn_note("STALL") or "") +
     " Early lead; +43 interval ini, velocity GAGAL (0,81x). Free% + umur UNVERIFIED. Tetap early lead.")
note("THYRK", (dyn_note("THYRK") or "") +
     " Minted-by-user-2026-11-10 (20 THYRK, pending swap, tanpa pair PCS V2); +18 interval ini, "
     "velocity GAGAL (minted <20). Tanpa perubahan.")

# ---- Age exclusions: window 00:01 -> 00:31 WIB (launch epoch 1794243655..1794245455) ----
WIN_LO, WIN_HI = 1794243655, 1794245455
TERMINAL = ("sold-out", "age-excluded", "minted-by-user", "excluded", "promotion-discarded",
            "same-owner-discarded", "paid-only", "upcoming")
newly_excluded = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    st = str(entry.get("status") or "")
    if any(x in st for x in TERMINAL):
        continue
    launch = entry.get("mintStart") or entry.get("saleStart") or entry.get("launchTime")
    if isinstance(launch, (int, float)) and WIN_LO <= launch <= WIN_HI:
        newly_excluded.append((name, launch))
print(f"age-exclusion window check: {newly_excluded if newly_excluded else '0 baru'}")

# ---- Backlog age-exclusions (temuan run 0031: item-item ini lolos dari window check
# run-run sebelumnya karena launch time-nya hanya tercatat di note/bukan field mintStart
# numerik, padahal first-mint-nya terverifikasi dan umurnya sudah >=24 jam) ----
BACKLOG = {
    # name: (evidence, report_once_bool)
    "Golden Agents": ("first mint terverifikasi blok 132445024 ~2026-11-09 02:00 WIB (backfill-confirmed); umur ~46,5 jam; totalSupply 1504/100.000, belum sold out", True),
    "BAHUANG3": ("mintStart on-chain 2026-11-09 05:29 WIB; umur ~43 jam; totalSupply None (tidak terbaca), belum terbukti sold out", True),
    "Riddle Run": ("mintStart 2026-11-09 18:54 WIB; umur ~29,6 jam; totalSupply 265, belum sold out", False),
    "PACK-B8Cf": ("mintStart 2026-11-04 19:30 WIB; umur ~157 jam; totalSupply None, belum terbukti sold out", False),
    "WHALE-B": ("first mint 2026-11-06 16:22 WIB (Boltbook); umur ~104 jam; totalSupply 2141, belum sold out", False),
    "WideWide": ("first mint 2026-11-06 19:39 WIB (backfill); umur ~101 jam; totalSupply None", False),
    "TriEight": ("first mint 2026-11-06 19:44 WIB (backfill); umur ~101 jam; totalSupply None", False),
    "GiraffeValley": ("first mint 2026-11-07 01:19 WIB (backfill); umur ~95 jam; totalSupply None", False),
    "Sage Trials": ("first mint 2026-11-07 01:52 WIB (backfill); umur ~95 jam; totalSupply 68, belum sold out", False),
    "Cedar Kiln": ("first mint 2026-11-08 10:33 WIB; umur ~62 jam; totalSupply None", False),
    "CrudeFi Refinery": ("first mint TERVERIFIKASI 2026-11-08 11:16 WIB; umur ~61 jam; totalSupply None", False),
    "Chiphiveowl": ("first mint 2026-11-08 14:51 WIB; umur ~57,7 jam; totalSupply 751, belum sold out", False),
    "Farmbuxiang": ("first mint 2026-11-08 14:57 WIB; umur ~57,6 jam; totalSupply 690, belum sold out", False),
    "Pixel Laptop": ("first mint 2026-11-08 14:56 WIB; umur ~57,6 jam; totalSupply 1429, belum sold out", False),
    "NEKART": ("first mint 2026-11-08 14:53 WIB; umur ~57,6 jam; totalSupply 889, belum sold out", False),
    "FU": ("first mint 2026-11-08 14:53 WIB; umur ~57,6 jam; totalSupply 369, belum sold out", False),
    "Beast16": ("first mint 2026-11-08 19:50 WIB (backfill); umur ~52,7 jam; totalSupply None", False),
    "Jolly": ("first mint 2026-11-03 23:27 WIB; umur ~169 jam; totalSupply None", False),
}
backlog_excluded = []
for name, (ev, report) in BACKLOG.items():
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["status"] = "age-excluded-2026-11-11"
        e["runNote0031_1111"] = (f"Run 0031 AGE-EXCLUDED (backlog): {ev}. Dihapus dari pantauan aktif "
                                  f"per aturan umur <24 jam (ditemukan saat audit launch-time run 0031; "
                                  f"lolos window check run sebelumnya karena launch time hanya di note). "
                                  f"{'Dilaporkan sekali sebagai age-excluded (pernah dilaporkan).' if report else 'Tidak dilaporkan (belum pernah dilaporkan sebagai lead / umur >48 jam).'}")
        backlog_excluded.append(name)
print(f"backlog age-excluded: {backlog_excluded}")

# ---- New snapshot entries from this run's discovery ----
snap["contracts"]["First-Dollar Grove"] = {
    "address": "0x56466afBcC2FDB847ed2cf5Bf78Ec1B213253611",
    "name": "First-Dollar Grove",
    "status": "checked-not-lead-age-excluded-2026-11-11",
    "totalSupply": 928, "MAX_SUPPLY": 99999, "balanceOf_user": 0,
    "runNote0031_1111": ("Run 0031: ditemukan via sweep ZH (thecolony.uk, dipublikasi 2026-11-08 13:44 WIB, "
                         "346 sudah dimint saat itu); totalSupply kini 928/99.999, MAX_SUPPLY 99.999, "
                         "balanceOf_user 0; tanpa free view (mintStart/freeMinted revert). Launch "
                         "2026-11-08 ~13:44 WIB -> umur ~59 jam >=24 jam -> AGE-EXCLUDED, bukan lead; "
                         "tidak dilaporkan (belum pernah dilaporkan). Site: "
                         "https://jeffzhou0511-ux.github.io/first-dollar-grove/ (tercatat, tidak "
                         "diverifikasi mencetak kontrak karena umur sudah gugur)."),
}
snap["contracts"]["Agent Operators"] = {
    "address": None,
    "name": "Agent Operators",
    "status": "watchlist-only-upcoming-2026-11-11",
    "runNote0031_1111": ("Run 0031: ditemukan via Boltbook (post 2026-11-09): NFT 1.111 supply, gratis "
                         "untuk Binance .ai Agent ID, 1 per wallet; registrasi dibuka s.d. 14 Nov 2026 "
                         "12:00 UTC; mint dibuka 15 Nov 2026 00:00 UTC. Kontrak BELUM dipublikasi "
                         "(tidak ada yang diverifikasi on-chain). Dicatat sebagai upcoming watchlist-only; "
                         "bukan kandidat, tidak di-preview/di-mint. Site di cryptoplay.guide (host afiliasi "
                         "judi — yellow flag dari Boltbook)."),
}
print("added First-Dollar Grove (age-excluded) + Agent Operators (upcoming)")

# ---- hot-leg-seen dedupe for the 20 shape-checked contracts ----
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
now_iso = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
added = 0
for a, s in legs.get("shape", {}).items():
    if a.lower() in {k.lower() for k in seen}:
        continue
    if "error" in s:
        note_txt = f"ABI fetch error: {s['error']}"
        status = "checked-abi-unavailable"
    else:
        note_txt = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                    f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"
    seen[a] = {"first_seen_wib": now_iso, "note": note_txt,
               "source": "sourcify-feed-0031", "status": status}
    added += 1
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"))
print(f"hot-leg-seen: +{added} -> {len(seen)}")

# ---- Top-level run notes ----
vel_passes = vel.get("passes", [])
snap["last_run_wib"] = NOW
snap["last_run"] = 1
snap["runNote0031_1111"] = (
    f"Run 0031 (2026-11-11 00:31 WIB, blok re-read {BLOCK}): re-read {updated} kontrak + {tc_updated} "
    f"track_c (bsc-dataseed, 843,9 dtk). 0 kandidat baru, 0 early lead baru, 0 strong lead baru, "
    f"0 track-C lead/kandidat baru, 0 track-B claim. SOLDERCATS tetap early (probe 414/2000 = 20,7%; "
    f"re-read +19, velocity GAGAL 0,79x). NIGHTFORGE gate dicek ulang (H+I+J+G), tetap gagal "
    f"(nightforge.pages.dev masih infografis medis 23.809 byte, 0 kecocokan kontrak; strong lead 33,75% "
    f"TETAP gate-blocked, tidak di-mint; deadline umur 2026-11-11 14:36 WIB). Claf Eye velocity LOLOS "
    f"(+25, 2,50x) TAPI TANPA promosi (free% + umur + website UNVERIFIED). Velocity LOLOS run ini: "
    f"{vel_passes if vel_passes else 'tidak ada'} (2 artefak ERC-20 + Claf Eye, bukan sinyal kandidat). "
    f"AGE-EXCLUSIONS: 18 backlog (Golden Agents + BAHUANG3 dilaporkan sekali; sisanya diam) + "
    f"First-Dollar Grove (temuan sweep, umur ~59 jam).")
snap["runNote0031_1111_scan"] = (
    "Run 0031 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs (eth_blockNumber) HTTP 401 Unauthorized "
    "(outage sejak ~13:33 WIB 2026-11-09 berlanjut, kini ~35 jam; kuota Ankr 0% s.d. 1 Des 2026). Watermark "
    "TIDAK dimajukan (tetap 132512564; gap ke head ~304.624 blok dan tumbuh). Route 5c: tanpa output scan "
    "baru (tidak ada ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote0031_1111_binanceai"] = (
    "Run 0031 track-B: binanceai.fun TIDAK BERUBAH - launched()=0 (nodereal; dataseed/dataseed2 403), "
    "tokenClaimed(user)=0, token balanceOf(user)=0. Status closed-refund-phase-2026-11-07; sudah "
    "dilaporkan sekali; tidak dilaporkan ulang. pending_claims kosong.")
snap["runNote0031_1111_age_exclusions"] = (
    f"Run 0031 age-exclusions (aturan <24 jam): window 00:01->00:31 WIB: "
    f"{len(newly_excluded)} BARU {newly_excluded if newly_excluded else ''}. BACKLOG (audit launch-time "
    f"run ini, lolos window check sebelumnya karena launch time hanya di note): {backlog_excluded} "
    f"(18 item; Golden Agents + BAHUANG3 dilaporkan sekali karena pernah dilaporkan dan umur 24-48 jam; "
    f"16 lainnya diam — belum pernah dilaporkan sebagai lead atau umur >48 jam). First-Dollar Grove "
    f"(temuan sweep ZH) juga age-excluded (~59 jam, tidak dilaporkan).")
snap["runNote0031_1111_discovery"] = (
    "Run 0031 discovery: Sourcify feed 20 terbaru (verified s.d. 17:33:43Z), 20 kontrak baru di-shape-check "
    "— SEMUA template pabrik 37-fn yang sama (mint/mintWithAgentTokenId + costOf + agent fns, TANPA free "
    "view) -> S1=S2=False, 0 sale-shape, 0 early lead (tanpa first-mint terverifikasi on-chain; scan mati). "
    "Boltbook EN 200 46.437 byte + ZH 200 46.384 byte, 16/15 alamat unik, 0 baru (semua sudah di hot-leg-seen). "
    "Sweep EN+ZH: Agentic Gangster free sold out 111/111 (excluded 1431); AGENT COSMOS sudah di snapshot "
    "(ACOS-3aed, umur >24 jam); First-Dollar Grove baru ditemukan tapi age-excluded (~59 jam); Agent "
    "Operators upcoming (mint 15 Nov, tanpa kontrak) dicatat watchlist-only; NOVRA/MOLT/PACTA/BOOB/ORBITA "
    "free habis/sold out (AirdropBuzz); AGC berbayar; BNB ORBIT age-excluded 10 Nov. Rute 6: Odaily 200 "
    "(264.108 byte) + PANews 200 (119.561 byte), 0 keyword Agent ID/free mint/free share. Bridge: 116 "
    "kontrak, mtime 2026-11-09 01:21 WIB (STALE); tidak ada temuan pelengkap baru. Track_c: 9 perubahan "
    "kecil tanpa promosi (Crack 4190->4191, MALTA, NUSA 383->385 age-excluded, 0x5f76cAb7, JINMA "
    "freeSharesRemaining 659->658 minted-by-user, VISION, COSO v2 742->745 age-excluded, 0x38491597 "
    "379->378 minted-by-user, 11-11 576->578 watchlist-only).")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT MERGED run 0031")
