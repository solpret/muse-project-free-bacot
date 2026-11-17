#!/usr/bin/env python3
"""Merge run 2231 reread+vel+legs into snapshot. Read-only except snapshot +
hot-leg-seen.json (dedupe for the 11 newly shape-checked contracts).
Run 2231 (jadwal 22:31 WIB)."""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-2231"
NOW = "2026-11-10 22:31 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
legs = json.load(open(f"{BASE}/run-{TS}-legs.json"))
BLOCK = rr.get("block")
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2231-premerge")

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
        e["runNote2231_1110"] = text

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
    return (f"Run 2231 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
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
    sc["runNote2231_1110"] = (
        f"Run 2231: probe segar (nodereal, blok ~{BLOCK}): totalSupply {p.get('totalSupply')} "
        f"(was 205 run hot-leg 22:29), agentFreeUsed {p.get('agentFreeUsed')}/2000 = "
        f"{(p.get('agentFreeUsed') or 0)/2000*100:.2f}% (masih <25% strong lead). mintOpen 1, "
        f"mintStart 1794321310 = 2026-11-10 21:35 WIB (umur ~1,3 jam TERVERIFIKASI <24 jam), slot user "
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
    nf["runNote2231_1110"] = (
        f"Run 2231: totalSupply {p.get('totalSupply')} (was 659 run 2201), agentFreeUsed "
        f"{p.get('agentFreeUsed')}/2000 = {(p.get('agentFreeUsed') or 0)/2000*100:.1f}% (tetap >=25% strong "
        f"lead). Gate DICEK ULANG run ini (metode H): nightforge.pages.dev home + /meta/collection.json + "
        f"/llms.txt + /skill.md + /launch.json + /agent.json SEMUA mengembalikan halaman infografis medis yang "
        f"sama (23.809 byte, 0 kecocokan kontrak, tidak ada kata 'nightforge') -> gate TETAP GAGAL, TIDAK "
        f"di-preview/TIDAK di-mint. Status tetap strong-lead-gate-blocked-2026-11-10 (sudah dilaporkan sekali "
        f"run 2131; tidak dilaporkan ulang). Deadline umur 2026-11-11 14:37 WIB.")
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
     " Early lead run 2201; tanpa perubahan status run ini.")
note("Golden Agents", (dyn_note("Golden Agents") or "") +
     " Early lead; free% UNVERIFIED (tanpa view free); tanpa perubahan.")

# ---- Age exclusions: window 22:01 -> 22:31 WIB (launch epoch 1794236455..1794238255) ----
WIN_LO, WIN_HI = 1794236455, 1794238255
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
    src = "boltbook-zh-2231" if a.lower() in {"0x88081347e712749a2d01e6c597b13fe0cc2478a5",
                                              "0xf769be14784bf61273028cb66f3e6a34b68eec9f"} else "sourcify-feed-2231"
    if "error" in s:
        note_txt = f"ABI fetch error: {s['error']}"
        status = "checked-abi-unavailable"
    else:
        note_txt = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                    f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"
    seen[a] = {"first_seen_wib": now_iso, "note": note_txt,
               "source": "sourcify-feed-2231", "status": status}
    added += 1
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"))
print(f"hot-leg-seen: +{added} -> {len(seen)}")

# ---- Top-level run notes ----
vel_passes = vel.get("passes", [])
snap["last_run_wib"] = NOW
snap["last_run"] = 2231
snap["runNote2231_1110"] = (
    f"Run 2231 (2026-11-10 22:31 WIB, blok re-read {BLOCK}): re-read {updated} kontrak + {tc_updated} "
    f"track_c (bsc-dataseed). TIDAK ADA mint/claim/preview run ini. SOLDERCATS tetap early "
    f"(agentFreeUsed 245/2000 = 12,25%, naik dari 205 run hot-leg 22:29; website sudah terverifikasi; "
    f"pantauan lanjut). NIGHTFORGE gate dicek ulang, tetap gagal (nightforge.pages.dev masih infografis medis, "
    f"0 kecocokan kontrak; strong lead 32,9% TETAP gate-blocked, tidak di-mint). 0 kandidat baru, 0 early lead "
    f"baru, 0 track-C lead/kandidat baru, 0 track-B claim. Velocity LOLOS run ini: {vel_passes if vel_passes else 'tidak ada'}.")
snap["runNote2231_1110_scan"] = (
    "Run 2231 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs (eth_blockNumber) HTTP 401 Unauthorized "
    "(outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. 1 Des 2026). Watermark TIDAK dimajukan "
    "(tetap 132512564; gap ke head ~290.000 blok dan tumbuh). Route 5c: tanpa output scan baru (tidak ada "
    "ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote2231_1110_binanceai"] = (
    "Run 2231 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, tokenClaimed(user)=0 (direct eth_call, "
    "blok ~132803571). Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang. "
    "pending_claims kosong.")
snap["runNote2231_1110_age_exclusions"] = (
    f"Run 2231 age-exclusions (aturan <24 jam): {len(newly_excluded)} BARU {newly_excluded if newly_excluded else ''}. "
    "Tidak ada entri non-terminal lain dengan launch terverifikasi di jendela 2026-11-09 22:01-22:31 WIB yang "
    "melewati 24 jam run ini.")
snap["runNote2231_1110_discovery"] = (
    "Run 2231 discovery: Sourcify feed 20 terbaru (verified 15:22-15:46Z), 11 kontrak baru di-shape-check, "
    "0 sale-shape S1/S2 (terdekat 0x8aB5Ddc1: mint+mintCost+AGENT_ID tapi tanpa free view; 0x5db9022B: "
    "freeClaimed+agentSigner tanpa mint). Boltbook EN GAGAL fetch (302, 0 byte); ZH 45.748 byte, 9 alamat: "
    "2 baru (0x88081347, 0xf769be14, Sourcify unverified, bukan sale-shape), sisanya dikenal (ORBITJANITOR, "
    "HACKOUCOINPASS, GEM-era). Sweep: Agentic Gangster sudah excluded run 1431 (pool habis 111/111, challenge-gated); "
    "Golden Agents / BNB ORBIT / PixelFox sudah di snapshot. Rute 6: Odaily 200 + PANews 200, 0 keyword "
    "Agent ID/free mint/free share. Bridge: 116 kontrak, mtime 2026-11-09 01:21 WIB (STALE, tidak berubah).")

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT MERGED run 2231")
