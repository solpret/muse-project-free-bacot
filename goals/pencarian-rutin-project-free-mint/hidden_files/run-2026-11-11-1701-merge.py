#!/usr/bin/env python3
"""Merge run 1701 (scheduled 2026-11-11 17:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1701-reread.json (block 132949132, 62 contracts + 23 track_c),
run-2026-11-11-1701-legs.json (feed 20, verified 09:56-10:04Z, 3 new; urllib
shape-check IncompleteRead x3 -> retried via curl: 0x2255 not agent-shaped
(no mint/quote/free/agent), 0xb5d1 + 0x7344 mint+quote but NO free view/agent
-> NOT agent-shaped, NOT S1/S2/early; Boltbook EN fail in legs but manual curl
retry OK 46.606 byte / 14 addrs / 0 new; ZH 42.851 byte / 11 addrs / 0 new;
bridge 116/0 new/7 discarded; binanceai launched 0; RigForge 709/0/291,
freeBooked 10000 RIG), web sweep EN+ZH + Odaily + PANews: 0 new projects
(AGENT COSMOS age-excluded ~6 hari, Oathbots age-excluded, Agentic Gangster
sold out, MOLT AGENT excluded, UFO/NEBULA already tracked).
Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1701-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1701-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1701-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 17:01 WIB"

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
        e["runNote1701"] = ("Run 1701 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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
        C[name]["runNote1701"] = text

note("0x7Eb9", "Run 1701 (blok %s): totalMinted 730->748 (+18, <20; 0,6/mnt vs prev 1,4333 = 0,42x) -> velocity GAGAL. Free%% + umur UNVERIFIED, website/X UNVERIFIED. Tetap EARLY lead; TIDAK di-preview/dimint." % BLOCK)
note("HANAMI BLOOM", "Run 1701 (blok %s): totalSupply=freeMinted 100->101 (+1, <20) velocity GAGAL; 101/3,333 = 3,03%%; balanceOf(user)=0; umur ~4 jam (mint-start ~12:59 WIB, deadline ~12:59 WIB 12 Nov). Tetap EARLY lead; TIDAK di-preview/dimint." % BLOCK)
note("Stampooor Stamp Packs", "Run 1701 (blok %s): totalMinted 803->811 (+8, <20; 0,2667/mnt vs prev 0,5333 = 0,5x) velocity GAGAL; freeMinted 811/1200 = 67,6%% (masih di bawah 70%% strong lead); balanceOf(user)=0; tetap EARLY. TIDAK di-preview/dimint." % BLOCK)
note("AgentPals", "Run 1701 (blok %s): totalMinted/freeMinted 103->111 (+8, <20; 0,2667/mnt vs prev 0,1 = 2,67x) velocity GAGAL; 111/300 = 37,0%%; balanceOf(user)=0; tetap watchlist-only, jauh di bawah 70%%. Website tetap UNVERIFIED. Deadline umur ~06:33 WIB 12 Nov." % BLOCK)
note("ABYSSCABLE", "Run 1701 (blok %s): totalSupply 814->818 (+4, <20; 0,1333/mnt vs prev 0,0333 = 4,0x) velocity GAGAL; balanceOf(user)=0; deadline umur ~19:39 WIB hari ini. BUKAN promosi." % BLOCK)
note("AgentRune", "Run 1701 (blok %s): totalSupply 183->186 (+3, <20) velocity GAGAL; freeMinted 186/4443 = 4,19%% dari MAX (FREE_SUPPLY/free-cap view TIDAK ADA -> %% kuota gratis tetap UNVERIFIED); balanceOf(user)=0; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("SUDOSAINTS", "Run 1701 (blok %s): totalSupply 590->592 (+2, <20) velocity GAGAL; freeMinted 592/7777 = 7,61%% (jauh di bawah 70%% strong lead); balanceOf(user)=0; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("Foundry Faces", "Run 1701 (blok %s): totalMinted 754->799 (+45; totalSupply() revert, view totalMinted dipakai); free views SEMUA None; balanceOf(user)=0; umur + free%% + website tetap UNVERIFIED; tetap watchlist-only-age-unverified. BUKAN promosi (velocity dihitung dari totalSupply, bukan totalMinted)." % BLOCK)
note("STALL", "Run 1701 (blok %s): totalSupply 1942 flat (+0) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("Twill Fullery", "Run 1701 (blok %s): totalSupply 157->158 (+1, <20) velocity GAGAL; balanceOf(user)=0; tetap EARLY (free%%/umur unverified)." % BLOCK)
note("WORKER", "Run 1701 (blok %s): totalSupply 673->676 (+3) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("Kitebots", "Run 1701 (blok %s): totalSupply 1005->1116 (+111, 3,7/mnt vs prev 0,2 = 18,5x) -> velocity LOLOS. TAPI TANPA promosi: free%% UNVERIFIED (FREE_SUPPLY tidak ada; 1116/4000 MAX = 27,9%% BUKAN %% kuota gratis), umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint." % BLOCK)
note("RIMEVAULT", "Run 1701 (blok %s): totalSupply 943->951 (+8) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov); deadline umur ~21:28 WIB hari ini." % BLOCK)
note("MYCELIX", "Run 1701 (blok %s): totalSupply 609->613 (+4) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov); deadline umur ~21:47 WIB hari ini." % BLOCK)
note("SOLDERCATS", "Run 1701 (blok %s): totalSupply 538->538 (+0) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:35 WIB hari ini." % BLOCK)
note("LCDSPRITE", "Run 1701 (blok %s): totalSupply 574->578 (+4) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:52 WIB hari ini." % BLOCK)
note("REWINDCLUB", "Run 1701 (blok %s): totalSupply 554->557 (+3) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:49 WIB hari ini." % BLOCK)

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
if isinstance(TC.get("Mihao"), dict):
    TC["Mihao"]["runNote1701"] = ("Run 1701 (blok %s): freeMinted 0, totalMinted 0, opened 0 - tetap FLAT pre-launch; "
        "watchlist-only, TIDAK dilaporkan sebagai lead, TIDAK di-preview/dimint." % BLOCK)
if isinstance(TC.get("VISION"), dict):
    TC["VISION"]["runNote1701"] = ("Run 1701 (blok %s): totalSupply 3.3876e27 -> 3.3948e27 (+7,2 jt token); freeMinted view tetap None; "
        "status watchlist-only-age-unverified, TIDAK promosi." % BLOCK)

# --- feed-new checked-not-agent-shaped (curl retry run ini) ---
TC["Feed-ERC20-0x22558846"] = {"address": "0x225588460d2Cd46648692052362775C011952d07",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1701 Sourcify feed (verifiedAt 2026-11-11T09:56-10:04Z): urllib shape-check IncompleteRead, retry curl run ini: "
             "ABI 28 fns, TANPA mint/quote/free view/agent ref; is_token True, BUKAN NFT. GAGAL S1/S2 dan BUKAN early lead. "
             "Dicatat checked saja; tidak masuk watchlist kontrak."),
    "lastReadWib": TS}
TC["Feed-ERC20-0xb5d1041F"] = {"address": "0xb5d1041F0C8Dd1Cc19838d60e777457a9f6Dd20b",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1701 Sourcify feed: urllib shape-check IncompleteRead, retry curl run ini: ABI 29 fns, mint+quote ADA tapi "
             "TANPA free view/fungsi free-mint dan TANPA agent ref (registry/AgentGate). GAGAL S1 (butuh free view + agent) dan "
             "BUKAN early lead (butuh registry/AgentGate/free-mint function/free-supply constant; mint() generik bukan free-mint). "
             "Dicatat checked saja; tidak masuk watchlist kontrak."),
    "lastReadWib": TS}
TC["Feed-ERC20-0x734425cB"] = {"address": "0x734425cBb1dCD2C45c642420dc88a6F879e2BB0D",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1701 Sourcify feed: hot-leg 1659 curl timeout + urllib IncompleteRead run ini, retry curl run ini: ABI 35 fns, "
             "mint+quote ADA tapi TANPA free view/fungsi free-mint dan TANPA agent ref. GAGAL S1/S2 dan BUKAN early lead "
             "(alasan sama seperti 0xb5d1). Dicatat checked saja; tidak masuk watchlist kontrak."),
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
                  "Re-check run 1701 (blok %s): freeSharesLeft %s/1000 (711 pukul 16:31, 709 pukul 17:01), openedAt %s (pool BELUM buka - collectShares belum bisa), "
                  "freeClaimed %s, freeBooked(wallet)=10000 RIG. Booking utuh. Marketplace/rarity TIDAK berlaku (bukan NFT)."
                  % (BLOCK, rigv.get("freeSharesLeft"), rigv.get("openedAt"), rigv.get("freeClaimed")))

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["runNote1701"] = ("Run 1701 (blok reread %s): 0 kandidat baru / 0 strong-lead mint / 0 early lead baru / 0 track-B dibuka / 0 track-C lead baru. "
    "Velocity LOLOS: 1 - Kitebots +111 (3,7/mnt vs prev 0,2 = 18,5x) TAPI TANPA promosi (free%% + umur + X UNVERIFIED). "
    "Stampooor 811/1200 = 67,6%% (<70%% strong lead), AgentPals 111/300 = 37,0%%, HANAMI BLOOM 101/3,333 = 3,03%%. "
    "Feed baru 3 (0x2255/0xb5d1/0x7344): BUKAN agent-shaped (curl retry), dicatat checked saja. "
    "RigForge pool belum buka (freeSharesLeft 709/1000, openedAt 0, booking 10000 RIG utuh). binanceai launched()=0 tetap pending." % BLOCK)
snap["runNote1701_scan"] = ("Run 1701 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized. "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh; backfill OFF. Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote1701_rigforge"] = ("RigForge re-check run 1701 (blok %s): freeSharesLeft 709/1000 (711 pukul 16:31, 709 pukul 17:01), openedAt 0 (pool BELUM buka), "
    "freeClaimed 291, freeBooked(wallet)=10000 RIG. Booking utuh; collectShares baru bisa sesudah pool buka." % BLOCK)
snap["runNote1701_binanceai"] = "Run 1701: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong; TIDAK di-preview/diklaim."
snap["runNote1701_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru. Bridge TIDAK ditulis.")
snap["runNote1701_discovery"] = ("Discovery run 1701: Sourcify feed 20 kontrak (verified 09:56-10:04Z): 3 baru - 0x2255 bukan agent-shaped (tanpa mint/quote/free/agent), "
    "0xb5d1 + 0x7344 mint+quote tapi TANPA free view/agent -> BUKAN agent-shaped, BUKAN S1/S2/early (curl retry setelah urllib IncompleteRead; 0x7344 juga timeout di hot-leg 1659). Dicatat checked saja. "
    "Boltbook EN gagal di legs (urllib+curl) tapi retry manual curl OK (46.606 byte, 14 alamat, 0 baru); ZH OK via curl (42.851 byte, 11 alamat, 0 baru). "
    "Sweep EN+ZH (browser.search): 0 proyek baru (Oathbots age-excluded; Agentic Gangster free pool SOLD OUT 111/111; BLOB Miner excluded; AGENT COSMOS age-excluded ~6 hari sejak publikasi 2026-11-05, tidak pernah dilaporkan job ini -> dicatat run log saja; MOLT AGENT excluded-free-pool-exhausted; AGENT MAO site paused 530; UFO/NEBULA sudah terlacak - NEBULA minted-by-user, UFO permit-gated watchlist-only). "
    "Odaily newsflash: 0 item Agent ID/free-mint. PANews: 0 item Agent ID/free-mint.")
snap["runNote1701_age"] = ("Run 1701 AGE: tidak ada age-exclusion baru. Deadline umur yang masih berjalan: ABYSSCABLE ~19:39 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, "
    "MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); SUDOSAINTS konservatif ~00:24 WIB 12 Nov; AgentPals ~06:33 WIB 12 Nov; AgentRune konservatif ~15:00 WIB 12 Nov; HANAMI BLOOM ~12:59 WIB 12 Nov.")
snap["last_run_note"] = ("Run 1701: 0 kandidat/strong/early/track-C lead baru. Velocity LOLOS 1 (Kitebots +111, 18,5x) tanpa promosi (free%% + umur + X unverified). "
                         "Stampooor 811/1200 = 67,6%%, AgentPals 111/300 = 37,0%%. Scan FAST-FAIL (Ankr 401). "
                         "RigForge pool belum buka (709/1000). binanceai launched()=0 tetap pending.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated)
