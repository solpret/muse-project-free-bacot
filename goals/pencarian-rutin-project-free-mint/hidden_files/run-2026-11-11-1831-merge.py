#!/usr/bin/env python3
"""Merge run 1831 (scheduled 2026-11-11 18:31 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1831-reread.json (63 contracts + 23 track_c; head block
UNREADABLE this run - eth_blockNumber timed out on all 3 dataseeds),
run-2026-11-11-1831-legs.json (Boltbook EN FAIL urllib+curl, ZH 42.791 byte /
15 addrs / 0 new; bridge 116/0 new/7 discarded; binanceai launched 0;
RigForge freeSharesLeft 695 / openedAt 0 / freeClaimed 305 / freeBooked 10000 RIG),
run-2026-11-11-1831-feed.json (curl retry: 20 contracts, verified 11:20:46-11:35:37Z,
6 new), run-2026-11-11-1831-shape-retry.json (0 S1/S2),
run-2026-11-11-1831-feed-triage.json (0xfA07 totalSupply 0; 0x83E4 totalSupply 0,
freeLeft garbage). Sweep EN+ZH: Agentic Gangster pool habis (known), MOLT/AGENT COSMOS
age >24h + free exhausted, BURN excluded, UFO already in track_c. Route 6: Odaily 0,
PANews 0. Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1831-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1831-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1831-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
TS = "2026-11-11 18:31 WIB"

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
        e["runNote1831_1111"] = ("Run 1831 (blok head TIDAK terbaca): baca batch GAGAL (transport) - nilai lama "
            "dipertahankan, BUKAN nol; velocity TIDAK dihitung run ini; status %s." % e.get("status"))
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
        C[name]["runNote1831_1111"] = text

note("Stampooor Stamp Packs", "Run 1831: baca batch GAGAL (transport) - totalMinted/freeMinted TERAKHIR 828/1200 = 69,0%% (run 1801) dipertahankan; status strong-lead run ini TIDAK DAPAT DITENTUKAN (butuh >840 untuk >70%%); TIDAK dipromosikan, TIDAK di-preview/dimint. Cek ulang run berikut.")
note("AgentPals", "Run 1831: totalMinted/freeMinted 116->124 (+8, <20; 0,2667/mnt vs prev 0,0333 = 8,0x) velocity GAGAL (<20 token); 124/300 = 41,33%%; balanceOf(user)=0; tetap watchlist-only, jauh di bawah 70%%. Website tetap UNVERIFIED. Deadline umur ~06:33 WIB 12 Nov.")
note("RAMRAIDERS", "Run 1831: totalSupply=freeMinted 553->558 (+5, <20; 0,1667/mnt) velocity GAGAL; 558/7777 = 7,18%%; balanceOf(user)=0 (slot terbuka). Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur konservatif ~00:30 WIB 12 Nov.")
note("RIMEVAULT", "Run 1831: totalSupply 1021->1030 (+9, <20) velocity GAGAL; balanceOf=1 (minted-by-user 11 Nov) - BUKAN kandidat/promosi. Deadline umur ~21:28 WIB hari ini.")
note("ABYSSCABLE", "Run 1831: totalSupply 822->823 (+1, <20) velocity GAGAL; balanceOf(user)=0; deadline umur ~19:39 WIB hari ini. BUKAN promosi.")
note("Skywe Legion", "Run 1831: totalMinted 618->641 (+23, 0,7667/mnt vs prev 1,5 = 0,51x) velocity GAGAL (rasio <1,5x). Free%% UNVERIFIED, umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint.")
note("HANAMI BLOOM", "Run 1831: totalSupply=freeMinted 109->109 (+0) velocity GAGAL; 109/3,333 = 3,27%%; balanceOf(user)=0; umur ~5,5 jam (deadline ~12:59 WIB 12 Nov). Tetap EARLY lead; TIDAK di-preview/dimint.")
note("Kitebots", "Run 1831: totalSupply 1192->1206 (+14, <20; 0,4667/mnt vs prev 0,3333 = 1,4x) velocity GAGAL (<20). TANPA promosi: free%% UNVERIFIED, umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint.")
note("Cosmic Sentinel", "Run 1831: totalSupply 471->471 (+0) velocity GAGAL; freeMinted 466; balanceOf(user)=0.")
note("Foundry Faces", "Run 1831: totalSupply() tetap revert, totalMinted 846->866 (+20 via totalMinted); free views SEMUA None; balanceOf(user)=0; umur + free%% + website tetap UNVERIFIED; tetap watchlist-only-age-unverified. BUKAN promosi (velocity dihitung dari totalSupply, bukan totalMinted).")
note("MYCELIX", "Run 1831: totalSupply 615->615 (+0) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov); deadline umur ~21:47 WIB hari ini.")
note("SOLDERCATS", "Run 1831: totalSupply 540->540 (+0) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:35 WIB hari ini.")
note("LCDSPRITE", "Run 1831: totalSupply 580->580 (+0) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:52 WIB hari ini.")
note("REWINDCLUB", "Run 1831: totalSupply 560->560 (+0) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:49 WIB hari ini.")
note("ORBITJANITOR", "Run 1831: totalSupply 718->720 (+2) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov).")
note("EMBERANVIL", "Run 1831: totalSupply 1121->1122 (+1) velocity GAGAL; balanceOf(user)=1.")
note("BYTEBLOOM", "Run 1831: totalSupply 820->820 (+0) velocity GAGAL; balanceOf(user)=1.")

tc_updated, tc_fail = [], []
tc = reread.get("track_c", {})
if isinstance(tc, dict):
    for name, d in tc.items():
        if name not in TC or not isinstance(TC.get(name), dict): continue
        e = TC[name]
        if d.get("_batch_fail"):
            tc_fail.append(name); continue
        changed = False
        for k in ("totalSupply","freeMinted","freeClaimed"):
            if d.get(k) is not None and e.get(k) != d[k]:
                e[k] = d[k]; changed = True
        e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
        if changed: tc_updated.append(name)

# Feed wave 1831 -> track_c checked-only
TC["Feed-wave-1831-2026-11-11"] = {
    "status": "checked-not-agent-shaped-2026-11-11",
    "addresses": ["0xfA07E35e9fb5bd3dc030E61C1709b9DFe3525da5","0xbceB023351423956Df834A82E590346C7768Ce82","0xef4882e029b8d58F81960c433D852a5b0A352965","0x83E4099A56975072696C80634311Ce7430487E35","0xAd793982c445789c04F090078248Ae4B7fB57625","0xC9F05DB3C95ae13c686C226d122B712a312203ce"],
    "note": ("Run 1831 Sourcify feed (curl retry setelah urllib timeout): 20 kontrak, verified 11:20:46-11:35:37Z, "
      "6 baru - 0 S1/S2. 0x83E4 (84 fns, mint+freeLeft, TANPA quote/agent) + 0xfA07 (31 fns, mint, TANPA free view/agent) "
      "loose early_shape saja; triase: totalSupply KEDUANYA 0 (belum ada mint pertama) -> BUKAN early lead (first mints "
      "tak terverifikasi - Ankr 401; free path UNVERIFIED). 0xbceB (9 fns, token biasa), 0xef48 (64 fns, mint tanpa "
      "free/agent), 0xAd79 (10 fns, token), 0xC9F0 (17 fns) BUKAN agent-shaped. Dicatat checked saja."),
    "lastReadWib": TS,
}
if isinstance(TC.get("UFO"), dict):
    TC["UFO"]["runNote1831_1111"] = ("Run 1831: totalSupply sale tetap 9e30 (klaim artikel 9.000.000.000.000 UFO); "
        "status tetap watchlist-only-shape-unverified-permit-gate-2026-11-11 (free pool/user slot belum terverifikasi, "
        "gate permit X-post). Sale tutup 12 Nov 22:05 WIB. TIDAK di-preview/dimint.")

snap["last_run"] = 1
snap["last_run_wib"] = TS
snap["runNote1831_1111"] = (
    "Run 1831 (blok head TIDAK terbaca - eth_blockNumber timeout di 3 dataseed): 0 kandidat baru / 0 strong-lead baru / "
    "0 early lead baru / 0 track-B dibuka / 0 track-C lead baru. Velocity LOLOS: 0. Batch-fail transport: 8 kontrak "
    "(SUDOSAINTS, AgentRune, Stampooor, 0x7Eb9, Pico Alcazar, Tiling Hammock, Hexel Pantry, STALL) - nilai lama "
    "dipertahankan. Stampooor 828/1200 = 69,0%% (run 1801) TIDAK DAPAT DITENTUKAN run ini (baca gagal; butuh >840). "
    "AgentPals 124/300 = 41,33%%. RAMRAIDERS 558/7777 = 7,18%%. Feed baru 6: 0 S1/S2; 2 loose early_shape, triase "
    "totalSupply 0 - BUKAN early lead. RigForge pool belum buka (freeSharesLeft 695/1000, openedAt 0, booking 10000 RIG "
    "utuh). binanceai launched()=0 tetap pending (refund phase). Scan FAST-FAIL pre-flight Ankr HTTP 401 (outage sejak "
    "~13:33 WIB 2026-11-09, kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564). Track-C 5c dilewati "
    "(tidak ada output scan baru). Boltbook EN GAGAL (urllib+curl timeout); ZH 42.791 byte / 15 alamat / 0 baru. "
    "Sweep: 0 proyek baru. Route 6: Odaily 0, PANews 0. AGE: tidak ada age-exclusion baru (ABYSSCABLE deadline ~19:39 WIB).")
snap["runNote1831_1111_scan"] = (
    "Run 1831 scan: PRE-FLIGHT FAIL (timeout 32,7 dtk) + probe langsung ankr_getLogs HTTP 401 Unauthorized "
    "(22,4 dtk) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB (~53 jam). Scan leg TIDAK dijalankan (amendemen "
    "2026-11-06). Watermark tetap 132512564; gap ke head tumbuh (terakhir terukur ~445.080 blok pukul 18:01 WIB, "
    "sudah dilaporkan sekali 9 Nov - DIAM). 5c dilewati (tanpa output scan).")
snap["runNote1831_1111_binanceai"] = (
    "Run 1831 track-B: binanceai.fun launched()=0 (raw 0x00..00) - TIDAK BERUBAH (refund phase, sudah dilaporkan "
    "sekali). pending_claims kosong.")
snap["runNote1831_1111_rigforge"] = (
    "Run 1831 RigForge: freeSharesLeft 695/1000 (700 pukul 18:01), openedAt 0 (pool BELUM buka), freeClaimed 305, "
    "freeBooked(wallet)=10000 RIG utuh.")

with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE vel_pass=%s vel_fail=%d batch_fail=%s tc_updated=%s" % (vel_pass, len(vel_fail), batch_fail, tc_updated))
