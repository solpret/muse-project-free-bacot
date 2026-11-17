#!/usr/bin/env python3
"""Merge run 1531 (scheduled 2026-11-11 15:31 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1531-reread.json (block 132937260, 60 contracts + 23 track_c),
run-2026-11-11-1531-legs.json (feed 2 new: 0 S1/S2/early; Boltbook urllib FAIL both,
curl OK 0 new; bridge 116/0 new/7 discarded; binanceai launched 0; RigForge 724/0/276),
run-2026-11-11-1531-boltbook-en/zh.html (curl OK, 10 addrs each, 0 new),
run-2026-11-11-1531-probe-mihao2.json (Mihao2 0x34eA fresh: pre-launch FLAT),
hot-leg-2026-11-11-1519-runlog.md (latest hot-leg; FDD3 +1, Stampooor 769, CAP7/SHINE unchanged).
Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1531-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1531-legs.json"))
probe_m2 = json.load(open(BASE + "run-2026-11-11-1531-probe-mihao2.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1531-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 15:31 WIB"

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
        e["runNote1531"] = ("Run 1531 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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
        C[name]["runNote1531"] = text

note("AgentRune", "Run 1531 (blok %s): totalSupply 168->176 (+8, <20) velocity GAGAL; freeMinted 165->173 (173/4443 = 3,89%% dari MAX; FREE_SUPPLY/free-cap view TIDAK ADA -> %% kuota gratis tetap UNVERIFIED); balanceOf(user)=0, slot terbuka; website/X/Sourcify tetap UNVERIFIED; tetap EARLY lead (dilaporkan run 1501). TIDAK di-preview/dimint. Deadline konservatif ~15:00 WIB 12 Nov." % BLOCK)
note("SUDOSAINTS", "Run 1531 (blok %s): totalSupply 572->575 (+3, <20) velocity GAGAL; freeMinted 575/7777 = 7,39%% (jauh di bawah 70%% strong lead); balanceOf(user)=0, slot terbuka; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("Stampooor Stamp Packs", "Run 1531 (blok %s): totalSupply view None (degradasi lean) tapi totalMinted=772 (761->772, +11, <20) velocity GAGAL; freeMinted 772/1200 = 64,3%% (masih di bawah 70%% strong lead; hot-leg 1519 baca 769/1200); balanceOf(user)=0; tetap EARLY. BUKAN agent-shaped (S1/S2 false) - bukan kandidat strong lead track-A walau melewati 70%% tanpa verifikasi ulang shape+umur+website." % BLOCK)
note("0x7Eb9", "Run 1531 (blok %s): totalSupply view None (degradasi lean) tapi totalMinted=677 (665->677, +12, <20) velocity GAGAL; balanceOf(user)=0; tetap EARLY." % BLOCK)
note("Twill Fullery", "Run 1531 (blok %s): totalSupply 142->150 (+8, <20) velocity GAGAL; balanceOf(user)=0; tetap EARLY (free%%/umur unverified)." % BLOCK)
note("AgentPals", "Run 1531 (blok %s): totalSupply view None (degradasi lean) tapi totalMinted/freeMinted=95 (93->95, +2, <20) velocity GAGAL; freeMinted 95/300 = 31,7%% (hot-leg 1519 baca 94/300); balanceOf(user)=0; tetap watchlist-only, jauh di bawah 70%%. Deadline umur ~06:33 WIB 12 Nov." % BLOCK)
note("ABYSSCABLE", "Run 1531 (blok %s): totalSupply 802->806 (+4, <20) velocity GAGAL; agentFreeUsed 806/2000 = 40,3%%; balanceOf(user)=0; deadline umur ~19:39 WIB hari ini. BUKAN promosi." % BLOCK)
note("STALL", "Run 1531 (blok %s): totalSupply 1927->1935 (+8, <20) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("WORKER", "Run 1531 (blok %s): totalSupply 665->667 (+2) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("WORKER #1", "Run 1531 (blok %s): totalSupply 704 FLAT vs 1501 (704) velocity GAGAL; balanceOf(user)=0." % BLOCK)

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
    TC["Mihao"]["runNote1531"] = ("Run 1531 (blok %s): freeMinted 0, totalMinted 0, opened 0 - tetap FLAT pre-launch (sama seperti hot-leg 1519); "
        "watchlist-only, TIDAK dilaporkan sebagai lead, TIDAK di-preview/dimint." % BLOCK)
if isinstance(TC.get("11-11"), dict):
    TC["11-11"]["runNote1531"] = ("Run 1531 (blok %s): freeMinted 617->626 (+9). Perubahan watchlist biasa, bukan promosi." % BLOCK)

# --- feed-new: 2 contracts, both S1/S2/early False -> checked-not-sale-shape ---
feed_shapes = legs.get("feed_shape", {}).get("shapes", [])
for s in feed_shapes:
    addr = s.get("address")
    if not addr: continue
    key = "Feed-ERC20-" + addr[:10]
    if key in TC: continue
    TC[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-11",
               "note": ("Run 1531 Sourcify feed (verified 07:51-08:34Z): S1=False S2=False early=False; "
                        "mint=%s quote=%s free_views=%s agent_ref=%s is_nft=%s is_token=%s fns=%s. Bukan lead track-C."
                        % (s.get("has_mint"), s.get("has_quote"), s.get("free_views"), s.get("agent_ref"),
                           s.get("is_nft"), s.get("is_token"), s.get("fn_count"))),
               "lastReadWib": TS}

# --- Mihao2 (0x34eA): hot-leg 1514 S1 discovery, fresh verify run ini -> add to track_c watchlist-only pre-launch ---
m2v = (probe_m2.get("views") or {})
if "Mihao2" not in TC:
    TC["Mihao2"] = {
        "sale": "0x34eA49e9BC199418f121366BdBEa8fDbab10c26b",
        "address": "0x34eA49e9BC199418f121366BdBEa8fDbab10c26b",
        "token": "0x11f60bb08b6cf755c2174c597f30c0f738beb117",
        "name": "Mihao2", "symbol": "MIHAO", "kind": "track-c-sale-S1",
        "status": "watchlist-only-pre-launch-2026-11-11",
        "FREE_SHARES": 500, "FREE_MAX": 500, "freeMinted": 0, "freeClaimedCount": 0,
        "totalMinted": 0, "freePhaseActive": 1, "opened": False, "paused": False,
        "saleEnd": "2026-11-14 15:12 WIB", "MAX_SHARES": 8000,
        "agentRegistry": "0xa4a7656b00c443a2972666a325838cf8b663dc1c (kontrak, BUKAN registry standar 0x60B9...022F - kaki registry S1 questionable, sama seperti Mihao 0x1f82)",
        "identityOf_user": 0,
        "quoteFor_1_free": "TIDAK TERBACA run ini (quoteFor(uint256,bool) null - encoding/signature; hot-leg 1514 baca cost 0)",
        "launchNote": "PRE-LAUNCH: opened=0, totalMinted=0, freeMinted=0 (verifikasi segar run 1531; sama seperti hot-leg 1514). Umur launch UNVERIFIED (belum ada mint pertama sama sekali). Sale KEDUA proyek Mihao (token MIHAO sama dengan sale 0x1f82), LumenMintV3, S1 PASS (mint + quoteFor + freeClaimed/freeMinted + agentRegistry). saleEnd 1794643960 = 2026-11-14 15:12 WIB (baca segar run ini; hot-leg 1514 menulis 2026-11-12 00:29 WIB - KOREKSI: angka hot-leg salah, yang dipakai baca segar ini). Discards: bersih (kontrak tidak ada di same-owner-discards.json).",
        "website": None, "gate": "website_not_checked_prelaunch",
        "lastReadWib": TS,
        "note": "Watchlist-only per body leg (3): pre-launch TIDAK dilaporkan sebagai lead, TIDAK di-preview/dimint. Re-check run berikut: opened/freeMinted/totalMinted/identityOf."}

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
                  "Re-check run 1531 (blok %s): freeSharesLeft %s/1000 (726 pukul 15:01 run 1501, 727 pukul 15:00 hot-leg), openedAt %s (pool BELUM buka - collectShares belum bisa), "
                  "freeClaimed %s, freeTaken(agentId)=1 (hot-leg 1519; baca legs run ini None karena encoding string), freeBooked(wallet)=10000 RIG. Booking utuh. Marketplace/rarity TIDAK berlaku (bukan NFT)."
                  % (BLOCK, rigv.get("freeSharesLeft"), rigv.get("openedAt"), rigv.get("freeClaimed")))

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["runNote1531"] = ("Run 1531 (blok reread %s): 0 kandidat baru / 0 early lead baru / 0 strong-lead mint / 0 track-B dibuka / 0 track-C lead baru. "
    "Velocity LOLOS: tidak ada (semua interval <20 token; AgentRune +8, SUDOSAINTS +3, STALL +8, ABYSSCABLE +4, Twill Fullery +8, RIMEVAULT +12, Stampooor +11, 0x7Eb9 +12). "
    "AgentRune 168->176, freeMinted 173/4443 = 3,89%% - tetap EARLY. Stampooor totalMinted 772/1200 = 64,3%% (<70%% strong lead), tetap EARLY. AgentPals 95/300 = 31,7%%, tetap watchlist-only. "
    "Mihao2 0x34eA (sale kedua Mihao, S1) ditambahkan ke track_c sebagai watchlist-only pre-launch (verifikasi segar run ini; saleEnd koreksi 2026-11-14 15:12 WIB). "
    "RigForge pool belum buka (freeSharesLeft 724/1000, openedAt 0, booking 10000 RIG utuh). binanceai launched()=0 tetap refund/pending." % BLOCK)
snap["runNote1531_scan"] = ("Run 1531 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized (~10 dtk, sama seperti run 1501). "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh; backfill OFF. Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote1531_rigforge"] = ("RigForge re-check run 1531 (blok %s): freeSharesLeft 724/1000 (726 pukul 15:01 run 1501, 727 pukul 15:00 hot-leg, 735 pukul 14:19), openedAt 0 (pool BELUM buka), "
    "freeClaimed 276, freeBooked(wallet)=10000 RIG. Booking utuh; collectShares baru bisa sesudah pool buka." % BLOCK)
snap["runNote1531_binanceai"] = "Run 1531: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase, isRefundPhase=1, sudah dilaporkan sekali). pending_claims kosong; TIDAK di-preview/diklaim."
snap["runNote1531_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru. Bridge TIDAK ditulis.")
snap["runNote1531_discovery"] = ("Discovery run 1531: Sourcify feed 20 kontrak (verified 07:51-08:34Z): 2 baru - 0 S1/S2/early PASS; "
    "keduanya checked-not-sale-shape (0xB3AE mint+quote tanpa free view/agent; 0x1003 tanpa mint/quote/free/agent). "
    "Boltbook EN+ZH urllib FAIL (RemoteDisconnected/IncompleteRead) tapi curl OK (EN 45.168 byte, ZH 45.371 byte, 10 alamat tiap bahasa; 0 baru). "
    "Sweep EN+ZH: 0 proyek baru (Oathbots 0xb777... publikasi 28 Okt - age-excluded, tidak masuk snapshot; PocketDragons 0x2cff... + AIAgentChips 0x1fe9... publikasi 24 Okt - age-excluded, tidak masuk snapshot; "
    "AGENT COSMOS sudah watchlist-only 4 Nov; Subsonic Tribe excluded-sold-out; PixelFox checked-sold-out; Agentic Gangster free-pool-exhausted; First-Dollar Grove age-excluded; UFO/NEBULA sudah di track_c). "
    "Odaily newsflash: 0 item Agent ID/free-mint (makro/pasar saja).")
snap["runNote1531_agentrune"] = ("AgentRune run 1531: totalSupply 168->176 (+8), freeMinted 165->173 (3,89%% dari MAX 4443); velocity GAGAL (<20); slot user terbuka (balanceOf 0); "
    "website/X/Sourcify tetap UNVERIFIED; tetap EARLY lead. TIDAK di-preview/dimint. Deadline konservatif ~15:00 WIB 12 Nov.")
snap["runNote1531_mihao2"] = ("Mihao2 0x34eA49e9BC199418f121366BdBEa8fDbab10c26b (sale kedua Mihao, token MIHAO 0x11f60b... sama dengan sale 0x1f82, LumenMintV3, S1 PASS): "
    "verifikasi segar run 1531 - FREE_SHARES 500, FREE_MAX 500, freeMinted 0, freeClaimedCount 0, totalMinted 0, freePhaseActive 1, opened 0, paused 0, "
    "saleEnd 1794643960 = 2026-11-14 15:12 WIB (KOREKSI atas hot-leg 1514 yang menulis 2026-11-12 00:29 WIB), MAX_SHARES 8000, identityOf(user) 0, "
    "agentRegistry 0xa4a7656b... (kontrak, bukan registry standar - kaki registry S1 questionable). Umur launch UNVERIFIED (0 mint). "
    "Ditambahkan ke track_c sebagai watchlist-only pre-launch; TIDAK dilaporkan sebagai lead, TIDAK di-preview/dimint. Discards bersih.")
snap["runNote1531_prio"] = ("Run 1531 prio: TIDAK ada baca prio baru run ini selain reread utama; status per hot-leg 1519 (~15:20 WIB): "
    "CAP7 freeMinted 225/640 (35,2%%), gate FAILED (sweep penuh A-N run 1131), TIDAK di-preview/dimint. "
    "SHINE startTime 1794394800 (2026-11-11 18:00 WIB, pre-launch), launched/freeClaimed revert seperti biasa. "
    "FDD3 freeMinted 24/500 (4,8%%, +1 vs 1514), BA3C pre-launch FLAT, BotFighters 65/500 (13,0%%) - ketiganya watchlist-only hot-leg, tanpa promosi. "
    "Mihao 0x1f82 FLAT pre-launch (opened 0, freeMinted 0, totalMinted 0) - tetap watchlist-only. LOWB 1000/1000 SOLD OUT (sudah dilaporkan 1424, tidak dilaporkan ulang).")
snap["runNote1531_age"] = ("Run 1531 AGE: tidak ada age-exclusion baru. Deadline umur yang masih berjalan: ABYSSCABLE ~19:39 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, "
    "MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); SUDOSAINTS konservatif ~00:24 WIB 12 Nov; AgentPals ~06:33 WIB 12 Nov; AgentRune konservatif ~15:00 WIB 12 Nov.")
snap["last_run_note"] = ("Run 1531: DIAM - 0 kandidat/early/strong/track-C lead baru. AgentRune 176 (+8), Stampooor 772/1200 = 64,3%%, AgentPals 95/300 = 31,7%%. "
                         "Mihao2 ditambahkan ke track_c watchlist-only pre-launch (saleEnd koreksi 14 Nov 15:12 WIB). Scan FAST-FAIL (Ankr 401). "
                         "RigForge pool belum buka (724/1000). binanceai launched()=0 tetap pending.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated)
