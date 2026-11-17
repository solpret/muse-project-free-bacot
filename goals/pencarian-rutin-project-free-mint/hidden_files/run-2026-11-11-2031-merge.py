#!/usr/bin/env python3
"""Merge run 2031 (scheduled 2026-11-11 20:31 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-2031-reread.json (62 contracts + 23 track_c; head block
132977042), run-2026-11-11-2031-legs.json, run-2026-11-11-2031-triage.json.
Writes snapshot (with .bak). No age-exclusion this run (next deadlines 21:28+).
No new candidate / strong lead / early lead / track-B opening / track-C lead.
Triaged: 0xC3e4923B (no mint), 0x39b57bA7 (mint+quote+agent, no free view),
0xd612a555 (Boltbook, 0 functions) - all checked-not-sale-shape, already
seen+recorded by hot-leg 20:29 run.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-2031-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-2031-legs.json"))
triage = json.load(open(BASE + "run-2026-11-11-2031-triage.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2031-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
TS = "2026-11-11 20:31 WIB"

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
        e["runNote2031_1111"] = ("Run 2031 (blok %s): baca batch GAGAL (transport) - nilai lama "
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
        C[name]["runNote2031_1111"] = text

# --- Stampooor: still strong lead, gate blocked, no tier change -> no re-report ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["status"] = "strong-lead-gate-blocked-2026-11-11"
    note("Stampooor Stamp Packs",
     "Run 2031: freeMinted 852->852/1200 = 71,00% (>70%, tetap strong lead); umur TERVERIFIKASI <24 jam "
     "(mintStart 1794362419 = 11 Nov 09:00:19 WIB; deadline ~09:00 WIB 12 Nov); slot user TERBUKA (balanceOf 0, "
     "mintOpen 1). Velocity +0/30 mnt GAGAL - tidak relevan untuk strong-lead direct mint. GATE WEBSITE tetap "
     "GAGAL (sudah dilaporkan sekali run 1901; gate-blocked-recheck menangani cek ulang situs). TIDAK di-preview, "
     "TIDAK di-mint, TIDAK dilaporkan ulang (tidak ada perubahan tier).")

note("0x7Eb9", "Run 2031: totalMinted 942->957 (+15, <20) velocity GAGAL (rate 0,5000/mnt vs prev 0,3000 = 1,67x "
     "tapi diff <20); balanceOf(user)=0. Tetap early-lead-reported; BUKAN promosi.")
note("Kitebots", "Run 2031: totalSupply 1232->1233 (+1, <20) velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED, "
     "X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint.")
note("RIMEVAULT", "Run 2031: totalSupply 1043->1049 (+6) velocity GAGAL; balanceOf=1 (minted-by-user). Deadline umur ~21:28 WIB hari ini.")
note("MYCELIX", "Run 2031: totalSupply 618->619 (+1) velocity GAGAL; balanceOf(user)=1 (minted-by-user). Deadline umur ~21:47 WIB hari ini.")
note("SOLDERCATS", "Run 2031: totalSupply 541->543 (+2) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:35 WIB hari ini.")
note("LCDSPRITE", "Run 2031: totalSupply 581->582 (+1) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:52 WIB hari ini.")
note("REWINDCLUB", "Run 2031: totalSupply 561->562 (+1) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:49 WIB hari ini.")
note("RAMRAIDERS", "Run 2031: totalSupply 561->561 (+0) velocity GAGAL; balanceOf(user)=0. "
     "Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur konservatif ~00:30 WIB 12 Nov.")
note("HANAMI BLOOM", "Run 2031: totalSupply 109->110 (+1) velocity GAGAL; balanceOf(user)=0. "
     "Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur ~12:59 WIB 12 Nov.")
note("BYTEBLOOM", "Run 2031: totalSupply 824->828 (+4, <20; baseline 19:31 WIB, batch fail run 2001) velocity GAGAL; "
     "balanceOf(user)=1 (minted-by-user).")
note("Dragon Agent", "Run 2031: totalSupply 931->932 (+1, <20; baseline 19:31 WIB, batch fail run 2001) velocity GAGAL; "
     "balanceOf(user)=0.")
note("Foundry Faces", "Run 2031: totalSupply tetap None (view revert), totalMinted 1090->1251 (+161 sejak 11:31 WIB, "
     "interval ~9 jam - BUKAN rate 30 mnt); velocity TIDAK dihitung (totalSupply() revert + baseline terakhir 11:31); "
     "free% UNVERIFIED; balanceOf(user)=0. BUKAN promosi.")
note("AgentPals", "Run 2031: totalMinted 300->300 (+0); free pool SOLD OUT 300/300; balanceOf(user)=1 (#268). "
     "Status minted-by-user-2026-11-11; TIDAK dilaporkan ulang. Keputusan gate metode (I) user ~19:36 WIB tetap berlaku "
     "(pantau 3 hari s.d. 14 Nov 2026; metadata worker saja SEMENTARA TIDAK cukup sebagai bukti website).")

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

# --- RigForge re-check (legs) ---
rig = TC.get("RigForge")
if isinstance(rig, dict):
    rig["freeSharesLeft"] = legs.get("rigforge", {}).get("freeSharesLeft")
    rig["openedAt"] = legs.get("rigforge", {}).get("openedAt")
    rig["freeClaimed"] = legs.get("rigforge", {}).get("freeClaimed")
    rig["freeBooked_user"] = 10000
    rig["lastReadBlock"] = BLOCK; rig["lastReadWib"] = TS

# --- Triaged / checked (not leads, never reported as leads) ---
C["checked-0xC3e4-2031"] = {
    "address": "0xC3e4923B06ae62000F9d74ed0393bDAb4d0B1425",
    "status": "checked-not-sale-shape-2026-11-11",
    "note": ("Run 2031 triase feed-new (Sourcify verified 13:33:34Z): 22 fns, has_mint False, has_quote False, "
        "free_views [], agent_ref False, is_token False. BUKAN S1/S2, BUKAN early-shape. Sudah dicatat hot-leg-seen.json "
        "oleh hot-leg run 20:29 (checked-not-sale-shape). Dicatat checked; tidak dilaporkan."),
}
C["checked-0x39b5-2031"] = {
    "address": "0x39b57bA7c31dDe3d9a75b067f994EcC9AF9DD60A",
    "status": "checked-not-sale-shape-2026-11-11",
    "note": ("Run 2031 triase feed-new (Sourcify verified 13:33:34Z): 10 fns, has_mint True, has_quote True, "
        "agent_ref True, TAPI free_views [] (near-miss S1 - tanpa free-share view, S1 gagal). is_token True, is_nft False. "
        "BUKAN S1/S2, BUKAN early-shape (bukan NFT). Sudah dicatat hot-leg-seen.json oleh hot-leg run 20:29. "
        "Dicatat checked; tidak dilaporkan."),
}
C["checked-0xd612-2031"] = {
    "address": "0xd612a555d4e7a1f01012991af447f35a1fb91e3f",
    "status": "checked-not-sale-shape-2026-11-11",
    "note": ("Run 2031 triase Boltbook-new (front page EN+ZH): Sourcify verified TAPI ABI 0 fungsi (fn_count 0) - "
        "tidak ada mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Sudah dicatat hot-leg-seen.json oleh hot-leg "
        "run 20:29 (boltbook-2029, checked-not-sale-shape). Dicatat checked; tidak dilaporkan."),
}

snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["runNote2031"] = (
    "Run 2031 (blok %s): DIAM - 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, "
    "0 track-C lead baru, 0 age-exclusion. Stampooor tetap strong lead gate-blocked 852/1200 = 71,00%%, slot terbuka, "
    "TIDAK dilaporkan ulang (tanpa perubahan tier). Velocity: 0 lolos (0x7Eb9 +15 <20 meski rasio 1,67x; Stampooor +0; "
    "Kitebots +1; RIMEVAULT +6). Batch fail: 0 (BYTEBLOOM 824->828 +4, Dragon Agent 931->932 +1, pulih terbaca). Foundry Faces: totalSupply "
    "tetap None, totalMinted 1090->1251 (+161 sejak 11:31, interval ~9 jam - bukan rate 30 mnt, velocity tidak dihitung). Track-C: 11-11 freeMinted 626->628 (+2, bukan promosi); lainnya datar. "
    "Sourcify feed 20 kontrak (verified 13:14:47-13:33:34Z), 2 baru (0xC3e4, 0x39b5) - keduanya 0 S1/S2/early-shape, "
    "sudah dicek + dicatat hot-leg run 20:29; triase curl retry 0 baru. Boltbook EN 45.361 byte / ZH 43.619 byte, "
    "9 alamat, 1 baru (0xd612, ABI 0 fungsi, bukan lead; sudah dicatat hot-leg 20:29). Bridge: 116 kontrak, mtime "
    "2026-11-08 18:21 WIB (STALE), 0 not_in_snapshot, 7 same_owner_discarded, 0 temuan pelengkap. Track B: binanceai.fun "
    "launched()=0 - TIDAK BERUBAH (refund phase). RigForge: freeSharesLeft 685/1000 (687 pukul 20:01), openedAt 0 "
    "(pool BELUM buka), freeClaimed 315, freeBooked(wallet) = 10000 RIG utuh. Scan (route 4): FAST-FAIL pre-flight Ankr "
    "HTTP 401 Unauthorized - outage berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK "
    "dimajukan (tetap 132512564); gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM). Track-C 5c dilewati (tidak "
    "ada output scan baru). Sweep EN+ZH: 0 proyek baru (Agentic Gangster free habis - dikonfirmasi 20:01; RIGBYPASS "
    "excluded; MOLT AGENT free habis; WNO/NOVRA/TINY/Grove/Agentite sudah dikenal; NAOMI GENESIS snippet '338 free left' "
    "BASI vs bacaan on-chain 20:01 freeMinted 777/777 sold out - tetap excluded). Route 6: Odaily newsflash 0 item "
    "Agent ID/free-mint; PANews 0 item. AGE: tidak ada exclusion run ini; deadline berjalan: RIMEVAULT ~21:28, "
    "SOLDERCATS ~21:35, MYCELIX ~21:47, REWINDCLUB ~21:49, LCDSPRITE ~21:52 (11 Nov); RAMRAIDERS konservatif ~00:30 WIB "
    "12 Nov; HANAMI BLOOM ~12:59 WIB 12 Nov; Stampooor ~09:00 WIB 12 Nov." % BLOCK)
snap["runNote2031_scan"] = (
    "Run 2031 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. "
    "Watermark TETAP 132512564; gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM).")
snap["timestamp_wib"] = TS

with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE vel_pass=%s vel_fail=%s batch_fail=%s tc_changes=%s" % (
    vel_pass, len(vel_fail), batch_fail, tc_changes))
print("VEL_FAIL:", vel_fail)
print("TC_CHANGES:", tc_changes)
