#!/usr/bin/env python3
"""Merge run 1801 (scheduled 2026-11-11 18:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1801-reread.json (block 132957644, 63 contracts + 23 track_c),
run-2026-11-11-1801-legs.json (Boltbook EN 43.763 byte / 15 addrs, ZH 42.053 / 17 addrs,
0 new; bridge 116/0 new/7 discarded; binanceai launched 0; RigForge 700/0/300,
freeBooked 10000 RIG), run-2026-11-11-1801-feed.json (curl retry after urllib
RemoteDisconnected: 20 contracts, verified 10:51-11:02Z, 8 new),
run-2026-11-11-1801-shape-retry.json (0 S1/S2; 6x loose early_shape, all no agent_ref),
run-2026-11-11-1801-feed-triage.json (5x totalSupply 0; 0xE244 totalSupply 3333/totalMinted 1,
free path unverified; registry bytes in 5/6 = factory template, non-discriminating).
Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1801-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1801-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1801-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 18:01 WIB"

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
        e["runNote1801_1111"] = ("Run 1801 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
                            "BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
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
        C[name]["runNote1801_1111"] = text

note("RIMEVAULT", "Run 1801 (blok %s): totalSupply 977->1021 (+44, 1,4667/mnt vs prev 0,8667 = 1,69x) -> velocity LOLOS. Minted-by-user 11 Nov (balanceOf=1) - BUKAN kandidat/promosi." % BLOCK)
note("Stampooor Stamp Packs", "Run 1801 (blok %s): totalMinted 820->828 (+8, <20; 0,2667/mnt vs prev 0,3 = 0,89x) velocity GAGAL; freeMinted 828/1200 = 69,0%% (masih di bawah 70%% strong lead, butuh >840); balanceOf(user)=0; tetap EARLY. TIDAK di-preview/dimint." % BLOCK)
note("AgentPals", "Run 1801 (blok %s): totalMinted/freeMinted 115->116 (+1, <20; 0,0333/mnt vs prev 0,1333 = 0,25x) velocity GAGAL; 116/300 = 38,67%%; balanceOf(user)=0; tetap watchlist-only, jauh di bawah 70%%. Website tetap UNVERIFIED. Deadline umur ~06:33 WIB 12 Nov." % BLOCK)
note("RAMRAIDERS", "Run 1801 (blok %s): totalSupply=freeMinted 551->553 (+2, <20; 0,0667/mnt, rate pertama di snapshot -> velocity TIDAK lulus); 553/7777 = 7,11%%; balanceOf(user)=0 (slot terbuka). Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur konservatif ~00:30 WIB 12 Nov." % BLOCK)
note("0x7Eb9", "Run 1801 (blok %s): totalMinted 815->882 (+67, 2,2333/mnt vs prev 2,2333 = 1,0x) -> velocity GAGAL (rasio <1,5x). Free%% + umur UNVERIFIED, website/X UNVERIFIED. Tetap EARLY lead; TIDAK di-preview/dimint." % BLOCK)
note("Skywe Legion", "Run 1801 (blok %s): totalSupply 573->618 (+45, 1,5/mnt vs prev 1,8 = 0,83x) -> velocity GAGAL. Free%% UNVERIFIED (FREE_SUPPLY tidak ada), umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint." % BLOCK)
note("HANAMI BLOOM", "Run 1801 (blok %s): totalSupply=freeMinted 102->109 (+7, <20; 0,2333/mnt vs prev 0,0333 = 7,01x) velocity GAGAL (<20 token); 109/3,333 = 3,27%%; balanceOf(user)=0; umur ~5 jam (mint-start ~12:59 WIB, deadline ~12:59 WIB 12 Nov). Tetap EARLY lead; TIDAK di-preview/dimint." % BLOCK)
note("ABYSSCABLE", "Run 1801 (blok %s): totalSupply 821->822 (+1, <20; 0,0333/mnt vs prev 0,1 = 0,33x) velocity GAGAL; balanceOf(user)=0; deadline umur ~19:39 WIB hari ini. BUKAN promosi." % BLOCK)
note("AgentRune", "Run 1801 (blok %s): totalSupply 187->190 (+3, <20; 0,1/mnt vs prev 0,0333 = 3,0x) velocity GAGAL (<20); freeMinted 187/4443 = 4,21%% dari MAX (FREE_SUPPLY/free-cap view TIDAK ADA -> %% kuota gratis tetap UNVERIFIED); balanceOf(user)=0; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("SUDOSAINTS", "Run 1801 (blok %s): totalSupply 596->597 (+1, 0,25x) velocity GAGAL; freeMinted 597/7777 = 7,67%% (jauh di bawah 70%% strong lead); balanceOf(user)=0; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("Foundry Faces", "Run 1801 (blok %s): totalSupply() tetap revert, totalMinted 829->846 (+17 via totalMinted); free views SEMUA None; balanceOf(user)=0; umur + free%% + website tetap UNVERIFIED; tetap watchlist-only-age-unverified. BUKAN promosi (velocity dihitung dari totalSupply, bukan totalMinted)." % BLOCK)
note("Kitebots", "Run 1801 (blok %s): totalSupply 1182->1192 (+10, 0,3333/mnt vs prev 2,2 = 0,15x) velocity GAGAL. TANPA promosi: free%% UNVERIFIED (FREE_SUPPLY tidak ada; 1192/4000 MAX = 29,8%% BUKAN %% kuota gratis), umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint." % BLOCK)
note("Cosmic Sentinel", "Run 1801 (blok %s): totalSupply 468->471 (+3, 0,1/mnt vs prev 0,0667 = 1,5x) velocity GAGAL (<20); freeMinted 466; balanceOf(user)=0." % BLOCK)
note("MYCELIX", "Run 1801 (blok %s): totalSupply 614->615 (+1) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov); deadline umur ~21:47 WIB hari ini." % BLOCK)
note("SOLDERCATS", "Run 1801 (blok %s): totalSupply 539->540 (+1) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:35 WIB hari ini." % BLOCK)
note("LCDSPRITE", "Run 1801 (blok %s): totalSupply 580->580 (+0) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:52 WIB hari ini." % BLOCK)
note("REWINDCLUB", "Run 1801 (blok %s): totalSupply 559->560 (+1) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:49 WIB hari ini." % BLOCK)
note("ORBITJANITOR", "Run 1801 (blok %s): totalSupply 718->718 (+0) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov)." % BLOCK)
note("EMBERANVIL", "Run 1801 (blok %s): totalSupply 1118->1121 (+3, 0,75x) velocity GAGAL (<20); balanceOf(user)=1." % BLOCK)
note("BYTEBLOOM", "Run 1801 (blok %s): totalSupply 819->820 (+1) velocity GAGAL; balanceOf(user)=1." % BLOCK)

tc_updated = []
tc = reread.get("track_c", {})
if isinstance(tc, dict):
    for name, d in tc.items():
        if name not in TC or not isinstance(TC.get(name), dict): continue
        e = TC[name]
        changed = False
        for k in ("totalSupply","freeMinted","freeClaimed"):
            if d.get(k) is not None and e.get(k) != d[k]:
                e[k] = d[k]; changed = True
        e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
        if changed: tc_updated.append(name)
if isinstance(TC.get("VISION"), dict):
    TC["VISION"]["runNote1801_1111"] = ("Run 1801 (blok %s): totalSupply 3,3948e27 -> 3,4038e27 (+9,0 jt token); freeMinted view tetap None; "
        "status watchlist-only-age-unverified, TIDAK promosi." % BLOCK)

# --- feed-new 8 checked-not-agent-shaped (curl retry run ini) ---
TC["Feed-wave-1801-2026-11-11"] = {
    "status": "checked-not-agent-shaped-2026-11-11",
    "addresses": ["0xE2444a7419C4f76d68DE91b719f24C8A80e1aE4d","0x433F98f0BE4Fe8C57a2Cc4036C9E75AF48108f58",
        "0xa594971e339510944a384Dd60e173733E76bEF5F","0x8A7Be94d1C36A60BCdD155D37faF84403B8a26ae",
        "0x0adD0E9396481cf7F2387A896ae8CaCb956d7aD0","0x12F6E9B79717548E1f37d3D25FB4AdE4C11079Bc"],
    "note": ("Run 1801 Sourcify feed (verifiedAt 2026-11-11T10:51-11:02Z, curl retry setelah urllib RemoteDisconnected): "
        "6 kontrak template NFT (ABI 29-35 fns, mint+quote, TANPA free view, TANPA agent ref di ABI) + 0x8A7B (84 fns, freeLeft ADA tapi "
        "TANPA quote/agent ref) + 0x44B0 (10 fns, tanpa mint/quote) + 0x7a01 (17 fns, tanpa shape). "
        "Registry bytes ADA di bytecode 5/6 template - itu template factory yang sama (code_len 14816, sama dengan gelombang 1731), "
        "TIDAK diskriminatif (diketahui 81%% kontrak template). GAGAL S1/S2 dan BUKAN early lead: first mints TIDAK terverifikasi "
        "(Ankr getLogs 401), free path UNVERIFIED. Triase on-chain: 5x totalSupply 0 (belum minting), 0xE244 totalSupply 3333/totalMinted 1 "
        "tapi free views None. Dicatat checked saja; tidak masuk watchlist kontrak."),
    "lastReadWib": TS}
TC["Feed-ERC20-0x44B0a50d"] = {"address": "0x44B0a50db86ab9871a48bE303F306A33870aeF9e",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1801 Sourcify feed: ABI 10 fns, TANPA mint/quote/free view/agent ref, token True, BUKAN NFT. "
        "GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja."),
    "lastReadWib": TS}
TC["Feed-0x7a01BC9B"] = {"address": "0x7a01BC9B2A07a01373D1eD3D2a613641CE7Cd8fa",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1801 Sourcify feed: ABI 17 fns, TANPA mint/quote/free view/agent ref, BUKAN token/NFT. "
        "GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja."),
    "lastReadWib": TS}

# --- RigForge re-check ---
rf = TC.get("RigForge")
if isinstance(rf, dict):
    rigv = legs.get("rigforge", {})
    rf["freeSharesLeft"] = rigv.get("freeSharesLeft")
    rf["openedAt"] = rigv.get("openedAt")
    rf["freeClaimed"] = rigv.get("freeClaimed")
    rf["freeBooked_user"] = rigv.get("freeBooked_user")
    rf["lastReadBlock"] = BLOCK
    rf["lastReadWib"] = TS
    rf["note"] = ("Track-C lead MINTED by user 11 Nov 12:12 WIB (tx 0xe766..., blok 132910090, freeBooked 10000 RIG). "
                  "Re-check run 1801 (blok %s): freeSharesLeft %s/1000 (704 pukul 17:31, 700 pukul 18:01), openedAt %s (pool BELUM buka - collectShares belum bisa), "
                  "freeClaimed %s, freeBooked(wallet)=10000 RIG. Booking utuh. Marketplace/rarity TIDAK berlaku (bukan NFT)."
                  % (BLOCK, rigv.get("freeSharesLeft"), rigv.get("openedAt"), rigv.get("freeClaimed")))

# --- patch legs.json feed info from curl retry ---
try:
    feed = json.load(open(BASE + "run-2026-11-11-1801-feed.json"))
    items = feed.get("results", [])
    legs["feed"] = {"n": len(items),
                    "newest_verifiedAt": items[0].get("verifiedAt") if items else None,
                    "oldest_verifiedAt": items[-1].get("verifiedAt") if items else None,
                    "via": "curl retry (urllib RemoteDisconnected first attempt)"}
    json.dump(legs, open(BASE + "run-2026-11-11-1801-legs.json", "w"), indent=1)
except Exception:
    pass

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["runNote1801_1111"] = ("Run 1801 (blok reread %s): 0 kandidat baru / 0 strong-lead baru / 0 early lead baru / 0 track-B dibuka / 0 track-C lead baru. "
    "Velocity LOLOS: 1 - RIMEVAULT +44 (1,69x) - minted-by-user, TANPA promosi. "
    "Stampooor 828/1200 = 69,0%% (masih di bawah 70%% strong lead, butuh >840), AgentPals 116/300 = 38,67%%. "
    "RAMRAIDERS 553/7777 = 7,11%%, velocity GAGAL (+2). "
    "Feed baru 8: 0 S1/S2; 6x template 35-fn + 2 lain BUKAN agent-shaped (registry bytes = template factory), dicatat checked saja. "
    "RigForge pool belum buka (freeSharesLeft 700/1000, openedAt 0, booking 10000 RIG utuh). binanceai launched()=0 tetap pending." % BLOCK)
snap["runNote1801_1111_scan"] = ("Run 1801 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized (12,2 dtk). "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh (~445.000 blok, head %s; sudah dilaporkan sekali untuk watermark ini 9 Nov - DIAM, tidak lapor ulang); backfill OFF. Track-C 5c dilewati (tidak ada output scan baru)." % BLOCK)
snap["runNote1801_1111_rigforge"] = ("RigForge re-check run 1801 (blok %s): freeSharesLeft 700/1000 (704 pukul 17:31, 700 pukul 18:01), openedAt 0 (pool BELUM buka), "
    "freeClaimed 300, freeBooked(wallet)=10000 RIG. Booking utuh; collectShares baru bisa sesudah pool buka." % BLOCK)
snap["runNote1801_1111_binanceai"] = "Run 1801: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong; TIDAK di-preview/diklaim."
snap["runNote1801_1111_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru. Bridge TIDAK ditulis.")
snap["runNote1801_1111_discovery"] = ("Discovery run 1801: Sourcify feed 20 kontrak (verified 10:51-11:02Z, curl retry): 8 baru - 0 S1/S2; 6x template NFT "
    "(mint+quote, tanpa free view/agent ref di ABI; registry bytes di bytecode = template factory, tidak diskriminatif) + 0x8A7B (freeLeft, tanpa quote/agent) "
    "+ 0x44B0 (10 fns) + 0x7a01 (17 fns) - BUKAN agent-shaped, BUKAN early lead (first mints tak terverifikasi, Ankr 401); 5x totalSupply 0, 0xE244 totalSupply 3333/totalMinted 1 "
    "tapi free path UNVERIFIED. Dicatat checked saja. "
    "Boltbook EN OK via curl (43.763 byte, 15 alamat), ZH OK via curl (42.053 byte, 17 alamat); 0 alamat baru. "
    "Sweep EN+ZH (browser.search): 0 proyek baru (Agentic Gangster pool habis 11 Nov; Golden Agents age-excluded 11 Nov; BNB ORBIT age-excluded 10 Nov; "
    "BLOB Miner excluded; AGENT MAO site paused 530; Agent Operators belum launching - mint buka 15 Nov, tanpa kontrak). "
    "Odaily newsflash: 0 item Agent ID/free-mint. PANews: 0 item free-mint (hanya berita AI-agent umum).")
snap["runNote1801_1111_age"] = ("Run 1801 AGE: tidak ada age-exclusion baru. Deadline umur yang masih berjalan: ABYSSCABLE ~19:39 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, "
    "MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); RAMRAIDERS konservatif ~00:30 WIB 12 Nov; AgentPals ~06:33 WIB 12 Nov; "
    "HANAMI BLOOM ~12:59 WIB 12 Nov.")
snap["last_run_note"] = ("Run 1801: 0 kandidat/strong/early/track-C lead baru. Velocity LOLOS 1 (RIMEVAULT, minted-by-user) tanpa promosi. "
                         "Stampooor 828/1200 = 69,0%% (<70%%), AgentPals 116/300 = 38,67%%. Scan FAST-FAIL (Ankr 401). "
                         "RigForge pool belum buka (700/1000). binanceai launched()=0 tetap pending.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated)
