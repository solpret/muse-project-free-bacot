#!/usr/bin/env python3
"""Merge run 1931 (scheduled 2026-11-11 19:31 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1931-reread.json (63 contracts + 23 track_c; head block
132968876), run-2026-11-11-1931-legs.json, run-2026-11-11-1931-triage.json.
Writes snapshot (with .bak). ABYSSCABLE age-excluded (deadline 19:38:21 WIB
passed during this run); AgentPals -> minted-by-user (hot-leg 1909 mint)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1931-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1931-legs.json"))
triage = json.load(open(BASE + "run-2026-11-11-1931-triage.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1931-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
TS = "2026-11-11 19:31 WIB"

def vel(name, new_supply, interval=30.0):
    e = C.get(name)
    if not isinstance(e, dict): return None
    old = e.get("totalSupply")
    if old is None or new_supply is None: return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / interval, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = interval
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = round(rate / prev_rate, 2) if prev_rate and prev_rate > 0 else None
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

vel_pass, vel_fail, batch_fail = [], [], []
for name, d in reread["reread"].items():
    if name not in C: continue
    e = C[name]
    if d.get("_batch_fail"):
        batch_fail.append(name)
        e["runNote1931_1111"] = ("Run 1931 (blok %s): baca batch GAGAL (transport) - nilai lama "
            "dipertahankan, BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None: ns = d.get("totalMinted")
    if ns is not None:
        r = vel(name, ns)
        if r and e.get("velocityLegPasses"): vel_pass.append((name, r))
        elif r: vel_fail.append((name, r))
    else:
        e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
    for k in ("totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None: e[k] = d[k]
    if d.get("totalSupply") is not None: e["totalSupply"] = d["totalSupply"]

def note(name, text):
    if isinstance(C.get(name), dict):
        C[name]["runNote1931_1111"] = text

# --- AgentPals: minted by hot-leg 1909, free pool now sold out ---
ap = C.get("AgentPals")
if isinstance(ap, dict):
    ap["status"] = "minted-by-user-2026-11-11"
    ap["gate"] = ("website_unverified_metadata-worker-disputed; KEPUTUSAN GATE METODE (I) user 11 Nov ~19:36 WIB: "
        "pantau 3 hari s.d. 14 Nov 2026 apakah proyek jalan + ada value; sementara tetap butuh situs proyek, "
        "metadata worker saja TIDAK cukup; review cron runonce 14 Nov ~19:37 WIB")
    note("AgentPals",
     "Run 1931: freeMinted 300/300 = FREE POOL SOLD OUT (262 pre-mint -> 269 pasca-mint -> 300); balanceOf(user)=1 "
     "(#268, hot-leg 1909, tx 0x6ed2eade4928e135d03a1f3a256fa7a92ac52490320c077bbc2c1356ab9a36f5, blok 132967594, "
     "receipt 1, gas 172342 [koreksi parent 19:31 WIB dari 172726], fee ~0,0000550 BNB). Status -> minted-by-user. "
     "TIDAK dilaporkan ulang (mint sudah dilaporkan hot-leg + sengketa gate sudah dilaporkan ke user ~19:30 WIB). "
     "KEPUTUSAN GATE user ~19:36 WIB: pantau AgentPals 3 hari s.d. 14 Nov; metadata tokenURI host saja SEMENTARA TIDAK cukup "
     "sebagai bukti website; strong lead yang buktinya hanya metadata-worker ditandai sama. PALS claim via HolderRewards "
     "BELUM diklaim, butuh verifikasi terpisah; jangan auto-claim.")

# --- Stampooor: still strong lead, gate blocked, no tier change -> no re-report ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["status"] = "strong-lead-gate-blocked-2026-11-11"
    note("Stampooor Stamp Packs",
     "Run 1931: freeMinted 848->851/1200 = 70,92%% (>70%%, tetap strong lead); umur TERVERIFIKASI <24 jam "
     "(mintStart 1794362419 = 11 Nov 09:00:19 WIB; deadline ~09:00 WIB 12 Nov); slot user TERBUKA (balanceOf 0, "
     "mintOpen 1). Velocity +10/30 mnt (<20) GAGAL - tidak relevan untuk strong-lead direct mint. GATE WEBSITE tetap "
     "GAGAL (sudah dilaporkan sekali run 1901; gate-blocked-recheck menangani cek ulang situs). TIDAK di-preview, "
     "TIDAK di-mint, TIDAK dilaporkan ulang (tidak ada perubahan tier).")

# --- ABYSSCABLE: age-excluded (deadline 19:38:21 WIB passed during this run) ---
ab = C.pop("ABYSSCABLE", None)
ab_evidence = None
if isinstance(ab, dict):
    ab_evidence = {
        "address": ab.get("address"),
        "mintStart": ab.get("mintStart"),
        "mintStart_wib": "2026-11-10 19:38:21 WIB",
        "deadline_wib": "2026-11-11 19:38:21 WIB",
        "last_read_block": BLOCK,
        "last_totalSupply": 830,
        "free_pct_note": "~828/2000 = 41,4% (tidak sold out)",
        "removed_run": "1931",
        "reason": "Umur peluncuran >= 24 jam (mintStart 1794314301) dan belum sold out -> dikeluarkan dari pantauan aktif per aturan umur <24 jam.",
    }
    ae = snap.setdefault("age_exclusions", [])
    if isinstance(ae, list):
        ae.append(ab_evidence)
    elif isinstance(ae, dict):
        ae["ABYSSCABLE-1931"] = ab_evidence

note("0x7Eb9", "Run 1931: totalSupply 914->933 (+19, <20) velocity GAGAL (rate 0,6333/mnt vs prev 2,2333 = 0,28x); "
     "balanceOf(user)=0. Tetap early-lead-reported; BUKAN promosi.")
note("Kitebots", "Run 1931: totalSupply 1217->1229 (+12, <20) velocity GAGAL. Free%% UNVERIFIED, umur UNVERIFIED, "
     "X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint.")
note("RIMEVAULT", "Run 1931: totalSupply 1036->1040 (+4) velocity GAGAL; balanceOf=1 (minted-by-user). Deadline umur ~21:28 WIB hari ini.")
note("MYCELIX", "Run 1931: totalSupply 616->616 (+0) velocity GAGAL; balanceOf(user)=1 (minted-by-user). Deadline umur ~21:47 WIB hari ini.")
note("SOLDERCATS", "Run 1931: totalSupply 541->541 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:35 WIB hari ini.")
note("LCDSPRITE", "Run 1931: totalSupply 581->581 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:52 WIB hari ini.")
note("REWINDCLUB", "Run 1931: totalSupply 561->561 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:49 WIB hari ini.")
note("RAMRAIDERS", "Run 1931: totalSupply=freeMinted 558->559 (+1) velocity GAGAL; 559/7777 = 7,19%%; balanceOf(user)=0. "
     "Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur konservatif ~00:30 WIB 12 Nov.")
note("HANAMI BLOOM", "Run 1931: totalSupply=freeMinted 109->109 (+0) velocity GAGAL; 109/3.333 = 3,27%%; balanceOf(user)=0. "
     "Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur ~12:59 WIB 12 Nov.")

# --- Track C reread: store fresh values, flag material changes ---
tc_changes = []
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict) or not isinstance(d, dict): continue
    e = TC[name]
    if d.get("_batch_fail"): continue
    for k in ("totalSupply","freeMinted","freeSharesRemaining","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None and e.get(k) != d[k]:
            if k in ("freeMinted","freeSharesRemaining"):
                tc_changes.append((name, k, e.get(k), d[k]))
            e[k] = d[k]
    e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS

# --- Triaged / checked (not agent-shaped, never reported as leads) ---
C["OCTOCODER-0x3a84"] = {
    "address": "0x3a84F41c71ba67CD62493B12448C175B0aD2F741",
    "name": "OCTOCODER", "symbol": "OCTO",
    "status": "checked-not-agent-shaped-2026-11-11",
    "totalSupply": 0, "MAX_SUPPLY": 4444,
    "mintStart": 1794400238, "mintStart_wib": "2026-11-11 19:30:38 WIB",
    "note": ("Run 1931 triase feed-retry: Sourcify verified, 85 fns (freeMintX, freeLeft, FIRST_FREE_CAP 2000, "
        "X_FREE_CAP 1000, mintStart/mintEnd), totalSupply 0 (BELUM ada mint pertama), TAPI TIDAK ADA referensi "
        "registry Agent ID 0x60B926...22F di sources maupun bytecode, agentRegistry() revert -> BUKAN agent-shaped, "
        "BUKAN early lead. Dicatat checked saja, tidak dilaporkan."),
}
C["checked-0xe10a-1931"] = {
    "address": "0xe10a2432d9c4bcde9e896c0a0beaf36d674e946c",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1931 triase Boltbook-new: Sourcify 404 (NOT verified), totalSupply tidak terbaca -> bentuk agent "
        "tidak dapat dibuktikan; BUKAN early lead. Dicatat checked saja, tidak dilaporkan."),
}
C["checked-0x62dC-1931"] = {
    "address": "0x62dC2216079671561b1CFF0564dEa23A6e01C275",
    "status": "checked-not-agent-shaped-2026-11-11",
    "totalSupply": 1000000000000000000000000000,
    "note": ("Run 1931 triase feed-retry (curl): Sourcify verified, 33 fns (mint, totalSpotsMinted), TANPA free view, "
        "tanpa agent ref, totalSupply 1e27 (token-like) -> BUKAN sale-shape S1/S2, BUKAN early lead. Dicatat checked saja."),
}

snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["runNote1931"] = (
    "Run 1931 (blok %s): LAPOR SEKALI - 1 age-exclusion (ABYSSCABLE, deadline 19:38:21 WIB lewat saat run berjalan; "
    "mintStart 1794314301 = 10 Nov 19:38:21 WIB, totalSupply terakhir 830, free ~41%%, tidak sold out). "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, 0 track-C lead baru. "
    "AgentPals free pool SOLD OUT 300/300 (minted-by-user #268 hot-leg 1909; TIDAK dilaporkan ulang; keputusan gate metode (I) "
    "user ~19:36 WIB dicatat di entri AgentPals). Stampooor tetap strong lead gate-blocked 851/1200 = 70,92%%, slot terbuka, "
    "TIDAK dilaporkan ulang (tanpa perubahan tier). Velocity: 0 lolos (0x7Eb9 +19 <20; Stampooor +10; Kitebots +12). "
    "Sourcify feed 20 kontrak (verified 12:02-12:32Z), 17 baru, 0 S1/S2/early; triase retry: OCTOCODER 0x3a84 bukan agent-shaped "
    "(0 mint, tanpa registry ref), 0x62dC bukan sale-shape, Boltbook-new 0xe10a Sourcify 404. Boltbook EN 44.303 byte / ZH "
    "42.571 byte, 6 alamat, 1 baru (0xe10a). Bridge: 116 kontrak, mtime 2026-11-08 18:21 WIB (STALE), 0 not_in_snapshot, "
    "7 same_owner_discarded, 0 temuan pelengkap. Track B: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase). "
    "RigForge: freeSharesLeft 689/1000 (692 pukul 19:01), openedAt 0 (pool BELUM buka), freeClaimed 311, freeBooked(wallet) "
    "= 10000 RIG utuh. Scan (route 4): FAST-FAIL pre-flight Ankr HTTP 401 Unauthorized - outage berlanjut sejak ~13:33 WIB "
    "2026-11-09. Watermark TIDAK dimajukan (tetap 132512564); gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM). "
    "Track-C 5c dilewati (tidak ada output scan baru). Sweep EN+ZH: Agentic Gangster free habis 111/111 (dikonfirmasi), "
    "RIGBYPASS excluded (pool habis), Horus AI fase gratis sold out (fase 2 berbayar), First-Dollar Grove / AGENT MAO / "
    "AgentGoldMiner / Pixel Fox / Coracle / Oathbots semuanya proyek lama (Okt-awal Nov), bukan kandidat baru. "
    "Route 6: Odaily newsflash 0 item Agent ID/free-mint (272.479 byte); PANews 0 item (123.939 byte). "
    "AGE: ABYSSCABLE dikeluarkan (di atas); deadline berjalan: RIMEVAULT ~21:28, SOLDERCATS ~21:35, MYCELIX ~21:47, "
    "REWINDCLUB ~21:49, LCDSPRITE ~21:52 (11 Nov); RAMRAIDERS konservatif ~00:30 WIB 12 Nov; HANAMI BLOOM ~12:59 WIB 12 Nov; "
    "Stampooor ~09:00 WIB 12 Nov." % BLOCK)
snap["runNote1931_scan"] = (
    "Run 1931 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. "
    "Watermark TETAP 132512564; gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM).")
snap["timestamp_wib"] = TS

with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE vel_pass=%s vel_fail=%s batch_fail=%s tc_changes=%s abyss_removed=%s" % (
    vel_pass, len(vel_fail), batch_fail, tc_changes, ab_evidence is not None))
print("VEL_FAIL:", vel_fail)
print("TC_CHANGES:", tc_changes)
