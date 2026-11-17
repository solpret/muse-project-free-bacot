#!/usr/bin/env python3
"""Merge run 1631 (scheduled 2026-11-11 16:31 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1631-reread.json (block 132945148, 62 contracts + 23 track_c),
run-2026-11-11-1631-legs.json (feed 4 new, 0 S1/S2, early_shape loose-True 0xa813;
Boltbook EN 44.698 byte / ZH 43.015 byte via curl, 11 addrs each, 2 'new' = false positives
(wallet 0x48de + tx hash 0x5371); bridge 116/0 new/7 discarded;
binanceai launched 0; RigForge 711/0/289, freeBooked 10000 RIG),
run-2026-11-11-1631-probe-feed-a813.json (0xa813: mint+quote+AGENT_REGISTRY but NO free
view/function, totalMinted 1, totalSupply 3333=MAX -> NOT agent-shaped, NOT track-C),
web sweep (browser.search EN+ZH + Odaily newsflash): 0 new projects.
Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1631-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1631-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1631-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 16:31 WIB"

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
        e["runNote1631"] = ("Run 1631 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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
        C[name]["runNote1631"] = text

note("0x7Eb9", "Run 1631 (blok %s): totalMinted 687->730 (+43, 1,4333/mnt vs prev 0,3333 = 4,30x) -> velocity LOLOS. TAPI TANPA promosi: free%% UNVERIFIED (tidak ada free view; 730/8888 MAX = 8,2%% BUKAN %% kuota gratis), umur UNVERIFIED, website/X UNVERIFIED (quote(user,1)=0 sejak run 0901 tidak dibaca ulang run ini). Tetap EARLY lead; TIDAK di-preview/dimint. Deep-dive umur via Ankr getLogs TIDAK mungkin run ini (Ankr 401)." % BLOCK)
note("HANAMI BLOOM", "Run 1631 (blok %s): totalSupply=freeMinted 97->100 (+3, <20) velocity GAGAL; 100/3,333 = 3,00%%; balanceOf(user)=0; umur ~3,5 jam (mint-start ~12:59 WIB, deadline ~12:59 WIB 12 Nov). Tetap EARLY lead; TIDAK di-preview/dimint." % BLOCK)
note("Stampooor Stamp Packs", "Run 1631 (blok %s): totalMinted 787->803 (+16, <20; 0,5333/mnt vs prev 0,5 = 1,07x) velocity GAGAL; freeMinted 803/1200 = 66,9%% (masih di bawah 70%% strong lead); balanceOf(user)=0; tetap EARLY. TIDAK di-preview/dimint." % BLOCK)
note("AgentPals", "Run 1631 (blok %s): totalMinted/freeMinted 100->103 (+3, <20) velocity GAGAL; 103/300 = 34,3%%; balanceOf(user)=0; tetap watchlist-only, jauh di bawah 70%%. Website tetap UNVERIFIED. Deadline umur ~06:33 WIB 12 Nov." % BLOCK)
note("ABYSSCABLE", "Run 1631 (blok %s): totalSupply 813->814 (+1, <20) velocity GAGAL; balanceOf(user)=0; deadline umur ~19:39 WIB hari ini. BUKAN promosi." % BLOCK)
note("AgentRune", "Run 1631 (blok %s): totalSupply 179->183 (+4, <20) velocity GAGAL; freeMinted 180/4443 = 4,05%% dari MAX (FREE_SUPPLY/free-cap view TIDAK ADA -> %% kuota gratis tetap UNVERIFIED); balanceOf(user)=0; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("SUDOSAINTS", "Run 1631 (blok %s): totalSupply 579->590 (+11, <20) velocity GAGAL; freeMinted 590/7777 = 7,59%% (jauh di bawah 70%% strong lead); balanceOf(user)=0; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("Foundry Faces", "Run 1631 (blok %s): bacaan totalSupply PERTAMA yang berhasil: 754 (snapshot sebelumnya None); free views SEMUA None; balanceOf(user)=0; umur + free%% + website tetap UNVERIFIED; tetap watchlist-only-age-unverified. BUKAN promosi." % BLOCK)
note("STALL", "Run 1631 (blok %s): totalSupply 1939->1942 (+3, <20) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("Twill Fullery", "Run 1631 (blok %s): totalSupply 155->157 (+2, <20) velocity GAGAL; balanceOf(user)=0; tetap EARLY (free%%/umur unverified)." % BLOCK)
note("WORKER", "Run 1631 (blok %s): totalSupply 668->673 (+5) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("Kitebots", "Run 1631 (blok %s): totalSupply 999->1005 (+6, <20) velocity GAGAL; freeMinted 1005; balanceOf(user)=0; tetap watchlist-only-age-unverified." % BLOCK)
note("RIMEVAULT", "Run 1631 (blok %s): totalSupply 940->943 (+3) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov); deadline umur ~21:28 WIB hari ini." % BLOCK)
note("MYCELIX", "Run 1631 (blok %s): totalSupply 608->609 (+1) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov); deadline umur ~21:47 WIB hari ini." % BLOCK)
note("SOLDERCATS", "Run 1631 (blok %s): totalSupply 538->538 (+0) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:35 WIB hari ini." % BLOCK)
note("LCDSPRITE", "Run 1631 (blok %s): totalSupply 572->574 (+2) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:52 WIB hari ini." % BLOCK)
note("REWINDCLUB", "Run 1631 (blok %s): totalSupply 552->554 (+2) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:49 WIB hari ini." % BLOCK)

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
    TC["Mihao"]["runNote1631"] = ("Run 1631 (blok %s): freeMinted 0, totalMinted 0, opened 0 - tetap FLAT pre-launch; "
        "watchlist-only, TIDAK dilaporkan sebagai lead, TIDAK di-preview/dimint." % BLOCK)

# --- feed-new 0xa813: checked-not-agent-shaped (probe run ini) ---
TC["Feed-ERC20-0xa8137C1b"] = {"address": "0xa8137C1b286D9db7cB84f9e15Bd35E14FB190E05",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1631 Sourcify feed (verifiedAt 2026-11-11T09:31:10Z): legs-script early_shape=True HANYA karena is_nft + mint() ada "
             "(definisi longgar). Probe segar run ini: ABI punya AGENT_REGISTRY + mint + quote + mintedBy + spotsLeft + PRICE + TREASURY, "
             "TAPI TANPA free view/fungsi free-mint (freeMinted/freeClaimed/FREE_SUPPLY/mintFree/claimFree semua revert/tidak ada), "
             "totalMinted 1, totalSupply 3333 = MAX_SUPPLY, name()/symbol() kosong, balanceOf(user)=0. Registry bytes ada di bytecode, "
             "tapi tanpa jalur gratis -> GAGAL S1 (butuh free view) dan BUKAN early lead (butuh free-mint function / free-supply constant). "
             "Bukan lead track-C. Dicatat checked saja; tidak masuk watchlist kontrak."),
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
                  "Re-check run 1631 (blok %s): freeSharesLeft %s/1000 (715 pukul 16:01, 711 pukul 16:31), openedAt %s (pool BELUM buka - collectShares belum bisa), "
                  "freeClaimed %s, freeBooked(wallet)=10000 RIG. Booking utuh. Marketplace/rarity TIDAK berlaku (bukan NFT)."
                  % (BLOCK, rigv.get("freeSharesLeft"), rigv.get("openedAt"), rigv.get("freeClaimed")))

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["runNote1631"] = ("Run 1631 (blok reread %s): 0 kandidat baru / 0 strong-lead mint / 0 early lead baru / 0 track-B dibuka / 0 track-C lead baru. "
    "Velocity LOLOS: 1 - 0x7Eb9 +43 (1,4333/mnt vs prev 0,3333 = 4,30x) TAPI TANPA promosi (free%% + umur UNVERIFIED). "
    "Stampooor 803/1200 = 66,9%% (<70%% strong lead), AgentPals 103/300 = 34,3%%, HANAMI BLOOM 100/3,333 = 3,00%%. "
    "Feed baru 0xa813: BUKAN agent-shaped (tanpa free view/fungsi), dicatat checked saja. "
    "RigForge pool belum buka (freeSharesLeft 711/1000, openedAt 0, booking 10000 RIG utuh). binanceai launched()=0 tetap pending." % BLOCK)
snap["runNote1631_scan"] = ("Run 1631 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized. "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh; backfill OFF. Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote1631_rigforge"] = ("RigForge re-check run 1631 (blok %s): freeSharesLeft 711/1000 (715 pukul 16:01, 711 pukul 16:31), openedAt 0 (pool BELUM buka), "
    "freeClaimed 289, freeBooked(wallet)=10000 RIG. Booking utuh; collectShares baru bisa sesudah pool buka." % BLOCK)
snap["runNote1631_binanceai"] = "Run 1631: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong; TIDAK di-preview/diklaim."
snap["runNote1631_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru. Bridge TIDAK ditulis.")
snap["runNote1631_discovery"] = ("Discovery run 1631: Sourcify feed 20 kontrak (verified 09:12-09:35Z): 4 baru - 0x2B69/0x2E64/0x0861 bukan agent-shaped (tanpa mint/quote/agent/free view), "
    "0xa813 BUKAN agent-shaped (mint+quote+AGENT_REGISTRY tapi TANPA free view/fungsi; totalMinted 1), dicatat checked saja. "
    "Boltbook EN+ZH urllib FAIL (IncompleteRead) tapi curl OK (EN 44.698 byte, ZH 43.015 byte, 11 alamat tiap bahasa); 2 'baru' adalah false positive: 0x48de = wallet user di post Mars Nexus, 0x5371 = hash tx terpotong - BUKAN kontrak proyek. "
    "Sweep EN+ZH (browser.search): 0 proyek baru (Oathbots age-excluded; Agentic Gangster free pool SOLD OUT 111/111; Golden Agents age-excluded; MOLT AGENT sudah excluded-free-pool-exhausted; NOVRA pool exhausted; WNO minted-by-user; Agent Operators upcoming, mint buka 15 Nov). "
    "Odaily newsflash: 0 item Agent ID/free-mint (makro/CPI/BTC saja).")
snap["runNote1631_age"] = ("Run 1631 AGE: tidak ada age-exclusion baru. Deadline umur yang masih berjalan: ABYSSCABLE ~19:39 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, "
    "MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); SUDOSAINTS konservatif ~00:24 WIB 12 Nov; AgentPals ~06:33 WIB 12 Nov; AgentRune konservatif ~15:00 WIB 12 Nov; HANAMI BLOOM ~12:59 WIB 12 Nov.")
snap["last_run_note"] = ("Run 1631: 0 kandidat/strong/early/track-C lead baru. Velocity LOLOS 1 (0x7Eb9 +43, 4,30x) tanpa promosi (free%% + umur unverified). "
                         "Stampooor 803/1200 = 66,9%%, AgentPals 103/300 = 34,3%%. Scan FAST-FAIL (Ankr 401). "
                         "RigForge pool belum buka (711/1000). binanceai launched()=0 tetap pending.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated)
