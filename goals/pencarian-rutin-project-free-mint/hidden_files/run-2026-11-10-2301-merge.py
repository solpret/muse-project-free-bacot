#!/usr/bin/env python3
"""Merge run 2301 reread+vel+legs into snapshot. Read-only except snapshot +
hot-leg-seen.json (dedupe for the 11 newly shape-checked contracts).
Run 2301 (jadwal 23:01 WIB)."""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-2301"
NOW = "2026-11-10 23:01 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
legs = json.load(open(f"{BASE}/run-{TS}-legs.json"))
BLOCK = rr.get("block")
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2301-premerge")

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
        e["runNote2301_1110"] = text

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
    return (f"Run 2301 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
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
    sc["runNote2301_1110"] = (
        f"Run 2301: probe segar (nodereal, blok ~{BLOCK}): totalSupply {p.get('totalSupply')} "
        f"(was 245 run 2231), agentFreeUsed {p.get('agentFreeUsed')}/2000 = "
        f"{(p.get('agentFreeUsed') or 0)/2000*100:.2f}% (masih <25% strong lead; pace melambat: "
        f"re-read +46/30 mnt = 1,53/mnt vs 4,03/mnt run 2231, velocity ratio 0,38 GAGAL; 25% baru "
        f"~01:15 WIB bila pace ini bertahan). mintOpen 1, "
        f"mintStart 1794321310 = 2026-11-10 21:35 WIB (umur ~1,4 jam TERVERIFIKASI <24 jam), slot user "
        f"TERBUKA (agentFreeByWallet 0, balanceOf 0). Website SUDAH terverifikasi (metode H, run 2201). "
        f"Tetap early lead; pantauan lanjut untuk promosi ke strong lead bila free% >=25%.")
    print("SOLDERCATS updated (still early)")

# ---- NIGHTFORGE: gate rechecked, still failed ----
nf = snap["contracts"].get("NIGHTFORGE")
if isinstance(nf, dict):
    p = legs.get("probe", {}).get("NIGHTFORGE", {})
    if p.get("totalSupply") is not None:
        nf["totalSupply"] = p["totalSupply"]
    if p.get("agentFreeUsed") is not None:
        nf["agentFreeUsed"] = p["agentFreeUsed"]
    nf["runNote2301_1110"] = (
        f"Run 2301: totalSupply {p.get('totalSupply')} (was 661 run 2231), agentFreeUsed "
        f"{p.get('agentFreeUsed')}/2000 = {(p.get('agentFreeUsed') or 0)/2000*100:.1f}% (tetap >=25% strong "
        f"lead). Gate DICEK ULANG run ini (metode H + I + J + G): nightforge.pages.dev home + "
        f"/meta/collection.json + /llms.txt + /skill.md + /launch.json + /agent.json SEMUA tetap halaman "
        f"infografis medis yang sama (23.809 byte, 0 kecocokan kontrak); contractURI() menunjuk domain yang "
        f"sama (metode I, bukan bukti baru); ABI Sourcify exact_match 87 fns tanpa fungsi site/URL "
        f"(metode J, hanya eip712Domain); pencarian nama proyek tanpa hasil situs (metode G) -> gate TETAP "
        f"GAGAL, TIDAK di-preview/TIDAK di-mint. Status tetap strong-lead-gate-blocked-2026-11-10 (sudah "
        f"dilaporkan sekali run 2131; tidak dilaporkan ulang). Deadline umur 2026-11-11 14:37 WIB.")
    print("NIGHTFORGE gate rechecked (still failed)")

note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user-2026-11-02; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") + " Minted-by-user-2026-11-01; tanpa perubahan.")
note("Zapcourier", (dyn_note("Zapcourier") or "") + " Minted-by-user-2026-11-02; free pool habis (712/712); tanpa perubahan.")
note("BYTEBLOOM", (dyn_note("BYTEBLOOM") or "") + " Minted-by-user run 2201 (#508); slot terpakai; tanpa perubahan.")
note("EMBERANVIL", (dyn_note("EMBERANVIL") or "") + " Minted-by-user-2026-11-10 (#946); tanpa perubahan.")
note("KERNELMONK", (dyn_note("KERNELMONK") or "") + " Minted-by-user-2026-11-10 (#509); tanpa perubahan.")
note("Lanternfield", (dyn_note("Lanternfield") or "") + " Minted-by-user-2026-11-10 (#516); tanpa perubahan.")
note("Cosmic Sentinel", (dyn_note("Cosmic Sentinel") or "") +
     " Early lead; freeMinted 341/225.000 = 0,15% (jauh <25%); umur UNVERIFIED; tanpa perubahan.")
note("ORBITJANITOR", (dyn_note("ORBITJANITOR") or "") +
     " Early lead run 2201; probe segar run ini: agentFreeUsed 404/2000 = 20,2% (masih <25%), "
     "mintOpen 1, mintStart 1794320692 = 2026-11-10 21:24 WIB, slot user TERBUKA (agentFreeByWallet 0); "
     "velocity GAGAL (ratio 1,03); website sudah terverifikasi; tanpa perubahan status run ini.")
note("ORBITJANITOR", (dyn_note("ORBITJANITOR") or "") +
     " Early lead run 2201; tanpa perubahan status run ini.")
note("Golden Agents", (dyn_note("Golden Agents") or "") +
     " Early lead; free% UNVERIFIED (tanpa view free); tanpa perubahan.")

# ---- Age exclusions: window 22:31 -> 23:01 WIB (launch epoch 1794238255..1794240055) ----
WIN_LO, WIN_HI = 1794238255, 1794240055
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

# ---- hot-leg-seen dedupe for the 11 shape-checked contracts ----
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
now_iso = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
added = 0
for a, s in legs.get("shape", {}).items():
    if a.lower() in {k.lower() for k in seen}:
        continue
    src = "boltbook-zh-2301" if a.lower() in {"0x88081347e712749a2d01e6c597b13fe0cc2478a5",
                                              "0xf769be14784bf61273028cb66f3e6a34b68eec9f"} else "sourcify-feed-2301"
    if "error" in s:
        note_txt = f"ABI fetch error: {s['error']}"
        status = "checked-abi-unavailable"
    else:
        note_txt = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                    f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"
    seen[a] = {"first_seen_wib": now_iso, "note": note_txt,
               "source": "sourcify-feed-2301", "status": status}
    added += 1
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"))
print(f"hot-leg-seen: +{added} -> {len(seen)}")

# ---- Top-level run notes ----
vel_passes = vel.get("passes", [])
snap["last_run_wib"] = NOW
snap["last_run"] = 2301
snap["runNote2301_1110"] = (
    f"Run 2301 (2026-11-10 23:01 WIB, blok re-read {BLOCK}): re-read {updated} kontrak + {tc_updated} "
    f"track_c (bsc-dataseed). TIDAK ADA mint/claim/preview run ini. SOLDERCATS tetap early "
    f"(agentFreeUsed 294/2000 = 14,70%, naik dari 245 run 2231; pace melambat 1,53/mnt, velocity GAGAL; "
    f"website sudah terverifikasi; pantauan lanjut). ORBITJANITOR tetap early (agentFreeUsed 404/2000 = 20,2%, "
    f"velocity GAGAL). NIGHTFORGE gate dicek ulang (H+I+J+G), tetap gagal (nightforge.pages.dev masih infografis "
    f"medis, 0 kecocokan kontrak; strong lead 33,05% TETAP gate-blocked, tidak di-mint). 0 kandidat baru, "
    f"0 early lead baru, 0 track-C lead/kandidat baru, 0 track-B claim. Velocity LOLOS run ini: "
    f"{vel_passes if vel_passes else 'tidak ada'}.")
snap["runNote2301_1110_scan"] = (
    "Run 2301 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs (eth_blockNumber) HTTP 401 Unauthorized "
    "(outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. 1 Des 2026). Watermark TIDAK dimajukan "
    "(tetap 132512564; gap ke head ~292.950 blok dan tumbuh). Route 5c: tanpa output scan baru (tidak ada "
    "ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote2301_1110_binanceai"] = (
    "Run 2301 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, tokenClaimed(user)=0 (direct eth_call, "
    "blok ~132805514). Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang. "
    "pending_claims kosong.")
snap["runNote2301_1110_age_exclusions"] = (
    f"Run 2301 age-exclusions (aturan <24 jam): {len(newly_excluded)} BARU {newly_excluded if newly_excluded else ''}. "
    "Tidak ada entri non-terminal lain dengan launch terverifikasi di jendela 2026-11-09 22:31-23:01 WIB yang "
    "melewati 24 jam run ini.")
snap["runNote2301_1110_discovery"] = (
    "Run 2301 discovery: Sourcify feed 20 terbaru (verified 15:41-16:05Z), 0 kontrak baru di-shape-check "
    "(semua sudah di hot-leg-seen), 0 sale-shape S1/S2. Boltbook EN 200 44.863 byte + ZH 200 45.591 byte, "
    "12 alamat unik, semuanya sudah dikenal (ORBITJANITOR, THYRK, HACKOUCOINPASS, 0x88081347, 0xf769be14). "
    "Sweep: Agentic Gangster sudah excluded run 1431 (free sold out 111/111, dikonfirmasi agentboard 122/1.111 paid "
    "open); First-Dollar Grove 0x56466a...253611 BARU dari sweep — agent-shaped + site mencetak kontrak, TAPI "
    "launch <=2026-11-08 20:44 WIB (~50 jam) -> age-excluded, tidak pernah dilaporkan -> diam, masuk daftar "
    "excluded; free% UNVERIFIED. Agent Grove fase 2 belum buka on-chain (grove-watch 23:01 WIB, freeOpen 0). "
    "AGENT COSMOS sudah di snapshot (ACOS-3aed). Rute 6: Odaily 200 + PANews 200, 0 keyword Agent ID/free "
    "mint/free share. Bridge: 116 kontrak, mtime 2026-11-09 01:21 WIB (STALE, tidak berubah).")

# ---- First-Dollar Grove: sweep find, age-excluded (never reported -> silent) ----
snap.setdefault("excluded", {})["First-Dollar Grove"] = {
    "address": "0x56466afBcC2FDB847ed2cf5Bf78Ec1B213253611",
    "symbol": "GROVE", "track": "A", "status": "excluded-age-over-24h-2026-11-10",
    "note": ("Sweep run 2301 (thecolony.uk, publikasi 2026-11-08 20:44 WIB, 346 sudah termint saat "
             "publikasi -> launch <=2026-11-08 20:44 WIB, umur ~50 jam >=24 jam). Agent-shaped "
             "(AGENT_ID_REGISTRY() = registry persis 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F); site "
             "jeffzhou0511-ux.github.io/first-dollar-grove/config.js mencetak kontrak persis (website gate "
             "WOULD pass); totalSupply 911 / totalMinted 947 / MAX_SUPPLY 99999; free views "
             "(freeClaimed/freeMinted/FREE_SUPPLY/mintOpen/freeOpen) revert -> free% UNVERIFIED. Tidak pernah "
             "dilaporkan -> diam per aturan age-exclusion; tidak masuk watchlist aktif.")}
print("First-Dollar Grove -> excluded (age >24h, never reported)")


json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT MERGED run 2301")
