#!/usr/bin/env python3
"""Merge run 1501 (scheduled 2026-11-11 15:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1501-reread.json (block 132933140, 61 contracts + 22 track_c),
run-2026-11-11-1501-legs.json (feed 4 new: 1 early-shape-by-name-only 0xB756, 3 not-sale-shape;
Boltbook urllib FAIL both, curl OK via separate fetch; bridge 116/0 new/7 discarded;
binanceai launched 0; RigForge 726/0/274),
run-2026-11-11-1501-boltbook-en/zh.html (curl OK, 16 addrs, 1 new = AgentRune),
run-2026-11-11-1501-probe.json (AgentRune + 0xB756 classification),
run-2026-11-11-1501-agentrune-alpha.html (Boltbook Alphapedia page),
run-2026-11-11-1501-nightforge.json (fresh direct reads: totalSupply 755, agentFreeUsed 752/2000),
hot-leg-2026-11-11-1454-runlog.md (CAP7/SHINE/Mihao/BA3C/FDD3 status ~15:00 WIB).
Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1501-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1501-legs.json"))
probe = json.load(open(BASE + "run-2026-11-11-1501-probe.json"))
nf_fresh = json.load(open(BASE + "run-2026-11-11-1501-nightforge.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1501-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 15:01 WIB"

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
        e["runNote1501"] = ("Run 1501 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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

# --- per-item run notes (prio) ---
def note(name, text):
    if isinstance(C.get(name), dict):
        C[name]["runNote1501"] = text

note("SUDOSAINTS", "Run 1501 (blok %s): totalSupply 567->572 (+5, <20) velocity GAGAL; freeMinted 572/7777 = 7,35%% (jauh di bawah 70%% strong lead); balanceOf(user)=0, slot terbuka; tetap EARLY lead (dilaporkan run 1401). TIDAK di-preview/dimint." % BLOCK)
note("Stampooor Stamp Packs", "Run 1501 (blok %s): totalSupply view None (degradasi lean) tapi totalMinted=761 (752->761, +9, <20) velocity GAGAL; freeMinted 761/1200 = 63,4%% (di bawah 70%% strong lead; hot-leg 1454 baca sama 761/1200); balanceOf(user)=0; tetap EARLY. BUKAN agent-shaped (S1/S2 false) - bukan kandidat strong lead track-A walau melewati 70%% tanpa verifikasi ulang shape+umur+website." % BLOCK)
note("0x7Eb9", "Run 1501 (blok %s): totalSupply view None (degradasi lean) tapi totalMinted=665 (653->665, +12, <20) velocity GAGAL; balanceOf(user)=0; tetap EARLY." % BLOCK)
note("Twill Fullery", "Run 1501 (blok %s): totalSupply 139->142 (+3, <20) velocity GAGAL; balanceOf(user)=0; tetap EARLY (free%%/umur unverified)." % BLOCK)
note("AgentPals", "Run 1501 (blok %s): totalSupply view None (degradasi lean) tapi totalMinted=93 (FLAT vs 1431); freeMinted 93/300 = 31,0%% (hot-leg 1454 baca sama); balanceOf(user)=0; tetap watchlist-only, jauh di bawah 70%%. Deadline umur ~06:33 WIB 12 Nov." % BLOCK)
note("ABYSSCABLE", "Run 1501 (blok %s): totalSupply 794->802 (+8, <20) velocity GAGAL; agentFreeUsed 802/2000 = 40,1%% (hot-leg 1454: agentFreeUsed = totalSupply); balanceOf(user)=0; deadline umur ~19:39 WIB hari ini. BUKAN promosi." % BLOCK)
note("STALL", "Run 1501 (blok %s): totalSupply 1912->1927 (+15, <20) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("WORKER", "Run 1501 (blok %s): totalSupply 662->665 (+3) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("WORKER #1", "Run 1501 (blok %s): totalSupply 702->704 (+2) velocity GAGAL; balanceOf(user)=0." % BLOCK)

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

# --- AGE-EXCLUSIONS: NIGHTFORGE + NIGHTFORGE B (both already reported by hot-leg; remove only, do NOT re-report) ---
removed = []
for name, hotleg_ref in (("NIGHTFORGE", "hot-leg 1434 pukul 14:43 WIB (#age-excluded-20261111-1437)"),
                         ("NIGHTFORGE B", "hot-leg 1449 pukul ~14:56 WIB (#age-excluded-20261111-1451)")):
    if name in C:
        e = C.pop(name)
        removed.append(name)
        snap["runNote1501_age_exclusion_" + ("nightforge" if name == "NIGHTFORGE" else "nightforge_b")] = (
            "%s %s AGE-EXCLUDED run 1501 (dikeluarkan dari snapshot; laporan sekali SUDAH dilakukan %s - run ini TIDAK melaporkan ulang). "
            "Verifikasi segar run ini: totalSupply %s, mintStart() %s = %s, umur >=24 jam, belum sold out, slot user TERBUKA (balanceOf 0). "
            % (name, e.get("address"), hotleg_ref,
               nf_fresh.get("totalSupply") if name == "NIGHTFORGE" else 360,
               nf_fresh.get("mintStart") if name == "NIGHTFORGE" else 1794297070,
               nf_fresh.get("mintStartWib") if name == "NIGHTFORGE" else "2026-11-10 14:51 WIB"))

# --- AgentRune: NEW EARLY LEAD ---
ar = probe.get("AgentRune", {})
arv = (ar.get("views") or {})
if "AgentRune" not in C:
    C["AgentRune"] = {
        "address": "0xc1fc0bb36d2be928809e4b3e6aa94b3dd2946f53",
        "name": "AgentRune", "symbol": "ARUNE", "kind": "ERC721",
        "status": "early-lead-reported-2026-11-11",
        "totalSupply": 168, "freeMinted": 165, "MAX_SUPPLY": 4443,
        "freePctOfMax": round(165 / 4443 * 100, 2),
        "freePctNote": "freeMinted 165/MAX_SUPPLY 4443 = 3,71% dari max; FREE_SUPPLY/free-cap view TIDAK ADA di kontrak -> % kuota gratis UNVERIFIED (tidak diganti % total supply).",
        "mintActive": 1,
        "priceFor_user": 0, "freeUsed_user": 0, "balanceOf_user": 0,
        "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
        "owner": "0x36f3d56ead5d1d6c2434f94defcef732c5c3cbd2",
        "ownerInDiscards": False,
        "ownerNote": "Owner sama dengan SnakeAgentNFT + SAKURA + PanduAGENT Phase 2 + SonoWaves + Hakuna (keluarga deployer 0x36f3... yang sama); owner TIDAK ada di same-owner-discards.json (61 entri, dicek run ini).",
        "sourcify": "UNVERIFIED (404 saat probe run 1501)",
        "bytecodeRegistry": True,
        "bytecodeLen": 13971,
        "gate": "website_unverified",
        "xVerified": False,
        "discussion": "Boltbook b/alpha post sun1122.ai ~15:00 WIB (1 mnt sebelum fetch run ini): 'AgentRune (ARUNE, BSC): free mint live, 164 minted'; Alphapedia https://boltbook.fun/alphapedia/agentrune (submitted by amzgaming.ai, added 2026-11-11): totalSupply 149 blok 132922913, mint(1) value 0 lolos static eth_call dari wallet Agent ID + revert NoAgentId dari dead address; gate agentIdCheckRequired() ON.",
        "firstSeenBlock": 132933140, "firstSeenWib": "2026-11-11 15:01 WIB",
        "launchNote": "Umur <24 jam TERVERIFIKASI sebagai batas atas (preseden SUDOSAINTS run 1401): first public post Boltbook sun1122.ai ~15:00 WIB hari ini + minting live on-chain (149 blok 132922913 -> 164 saat post -> 168 probe run ini). First-mint event persis UNVERIFIED (Ankr 401 memblokir cek getLogs); tidak ada mintStart()/startTime view di kontrak; Sourcify UNVERIFIED (tanpa verifiedAt). Deadline konservatif ~15:00 WIB 12 Nov (24 jam dari first public post).",
        "velocityVerified": False,
        "currentRatePerMin": None, "previousRatePerMin": None, "velocityRatio": None,
        "velocityLegPasses": False,
        "lastReadBlock": BLOCK, "lastReadWib": TS,
        "baselineNote": "EARLY lead dilaporkan sekali run 1501: agent-shaped TERVERIFIKASI (agentIdRegistry() = registry Binance 0x60B926...22F; registry bytes di bytecode 13.971 byte; agentIdCheckRequired() ON per Alphapedia; mint(1) value 0 lolos static eth_call dari wallet user run ini - triase, BUKAN preview). First mints terverifikasi on-chain (149 -> 164 -> 168 dalam run ini). Free 165/4443 = 3,71% dari MAX (free-cap view tidak ada -> % kuota UNVERIFIED); slot user TERBUKA (priceFor=0, freeUsed=0, balanceOf=0). Website UNVERIFIED (contractURI kosong, tokenURI(1) kosong, tidak ada situs proyek; Alphapedia Boltbook bukan situs proyek). X UNVERIFIED. Sourcify UNVERIFIED. TIDAK PERNAH di-preview/dimint sebagai early lead; promosi hanya bila 3 kaki strong lead terpenuhi + gate website lolos.",
        "runNote1501": "Run 1501: klasifikasi early lead oleh job utama (temuan Boltbook front page EN+ZH via curl, 1 alamat baru). Lihat baselineNote.",
    }

# --- 0xB756 (Pawlands Founder Pass): feed early-shape by mint-name only -> checked, NOT agent-shaped, no mints ---
b756 = probe.get("0xB756", {})
b756v = (b756.get("views") or {})
key_b756 = "Feed-ERC20-0xB756267d"
if key_b756 not in TC:
    TC[key_b756] = {
        "address": "0xB756267d8932b5d0c74CA49FC455309317b7B0B4",
        "status": "checked-not-agent-shaped-2026-11-11",
        "note": ("Run 1501 Sourcify feed (verified 07:48-08:04Z): early_shape=True HANYA karena fn 'mint' + is_nft; "
                 "probe run ini: Sourcify exact_match 54 fns (Pawlands Founder Pass / PFPASS: BASE_PRICE, fundingDeadline, launch, refund, taxes - bentuk funding/launchpad, BUKAN sale-shape); "
                 "agent_ref=False, free_views=[], registry TIDAK ada di bytecode, agentRegistry view tidak ada; totalSupply=0, totalMinted=0 (BELUM ADA mint). "
                 "BUKAN agent-shaped -> BUKAN early lead, BUKAN track-C. Jangan di-shape-check ulang."),
        "lastReadWib": TS}

# --- feed-new: 3 remaining contracts, all S1/S2/early False -> checked-not-sale-shape ---
feed_shapes = legs.get("feed_shape", {}).get("shapes", [])
for s in feed_shapes:
    addr = s.get("address")
    if not addr or addr.lower() == "0xb756267d8932b5d0c74ca49fc455309317b7b0b4": continue
    key = "Feed-ERC20-" + addr[:10]
    if key in TC: continue
    TC[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-11",
               "note": ("Run 1501 Sourcify feed (verified 07:48-08:04Z): S1=False S2=False early=False; "
                        "mint=%s quote=%s free_views=%s agent_ref=%s is_nft=%s is_token=%s fns=%s. Bukan lead track-C."
                        % (s.get("has_mint"), s.get("has_quote"), s.get("free_views"), s.get("agent_ref"),
                           s.get("is_nft"), s.get("is_token"), s.get("fn_count"))),
               "lastReadWib": TS}

# --- Mihao (0x1f82): hot-leg S1 discovery, pre-launch -> add to track_c watchlist-only (NOT reported as lead, NOT previewed/minted) ---
if "Mihao" not in TC:
    TC["Mihao"] = {
        "sale": "0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1",
        "address": "0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1",
        "token": "0x11f60bb08b6cf755c2174c597f30c0f738beb117",
        "name": "Mihao", "symbol": "MIHAO", "kind": "track-c-sale-S1",
        "status": "watchlist-only-pre-launch-2026-11-11",
        "FREE_MAX": 100, "freeMinted": 0, "totalMinted": 0, "MAX_SHARES": 4440000,
        "BASE_PRICE": "0,003 BNB", "TOKENS_PER_SHARE": 75000000,
        "saleEnd": "2026-11-14 14:26 WIB", "opened": False, "paused": False,
        "agentRegistry": "0xa4a7...63dc1c (kontrak, 440 byte) BUKAN registry standar 0x60B9...022F - kaki registry S1 questionable",
        "quoteFor_1_useFree": "0,003 BNB (1 free + 1 paid share) - mint murni-gratis BELUM terverifikasi",
        "identityOf_user": "0x0 (belum ada identity terdaftar di sale ini)",
        "claimable_user": 0,
        "launchNote": "PRE-LAUNCH: opened=false, totalMinted=0, freeMinted=0. Umur launch UNVERIFIED. Ditemukan hot-leg 1449 (Sourcify feed S1 PASS, Sourcify exact_match LumenMintV2); re-check hot-leg 1454: tetap pre-launch FLAT. Ditambahkan ke snapshot track_c oleh job utama run 1501.",
        "website": None, "gate": "website_not_checked_prelaunch",
        "lastReadWib": TS,
        "note": "Watchlist-only per body leg (3): pre-launch TIDAK dilaporkan sebagai lead, TIDAK di-preview/dimint. Re-check run berikut: opened/freeMinted/totalMinted/identityOf."}

# --- RigForge re-check (legs script values; freeTaken None = encoding issue in legs script, hot-leg 1454 confirmed =1) ---
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
                  "Re-check run 1501 (blok %s): freeSharesLeft %s/1000 (727 pukul 15:00 hot-leg, 735 pukul 14:19, 746 pukul 14:01), openedAt %s (pool BELUM buka - collectShares belum bisa), "
                  "freeClaimed %s, freeTaken(agentId)=1 (hot-leg 1454; baca legs run ini None karena encoding string), freeBooked(wallet)=10000 RIG. Booking utuh. Marketplace/rarity TIDAK berlaku (bukan NFT)."
                  % (BLOCK, rigv.get("freeSharesLeft"), rigv.get("openedAt"), rigv.get("freeClaimed")))

# --- CAP7 / SHINE: no fresh prio read this run; status per hot-leg 1454 (~15:00 WIB), unchanged ---
snap["runNote1501_prio"] = ("Run 1501 prio: TIDAK ada baca prio baru run ini; status per hot-leg 1454 (~15:00 WIB, tidak berubah): "
    "CAP7 freeMinted 225/640 (35,2%%), phase 1, soldOut 0, slot user balanceOf 0 - gate FAILED (sweep penuh A-N run 1131), TIDAK di-preview/dimint. "
    "SHINE startTime 1794394800 (2026-11-11 18:00 WIB, pre-launch), launched/freeClaimed revert seperti biasa. "
    "Mihao pre-launch FLAT (opened 0, freeMinted 0, totalMinted 0) - tetap watchlist-only. BA3C pre-launch; FDD3 FLAT freeMinted 15/500 (3,0%%).")

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["runNote1501"] = ("Run 1501 (blok reread %s): 1 EARLY lead BARU - AgentRune 0xc1fc0b... (ARUNE, 168/4443, freeMinted 165, slot user terbuka, agent-shaped terverifikasi via agentIdRegistry() + registry bytes, umur <24 jam batas atas via first public post ~15:00 WIB, website/X/Sourcify UNVERIFIED) - dilaporkan sekali run ini, TIDAK di-preview/dimint. "
    "0 kandidat baru / 0 strong-lead mint / 0 track-B dibuka / 0 track-C lead baru. "
    "Velocity LOLOS: tidak ada (semua interval <20 token; SUDOSAINTS +5, STALL +15, NIGHTFORGE +6 sebelum exclusion, ABYSSCABLE +8). "
    "Stampooor totalMinted 761/1200 = 63,4%% (<70%% strong lead), tetap EARLY. AgentPals FLAT 93/300 = 31,0%%. Twill Fullery +3 tetap EARLY. "
    "NIGHTFORGE + NIGHTFORGE B dikeluarkan dari snapshot (age-excluded; laporan sekali SUDAH oleh hot-leg 1434/1449 - TIDAK dilaporkan ulang run ini). "
    "0xB756 (Pawlands Founder Pass) checked-not-agent-shaped (totalSupply 0, tanpa mint). RigForge pool belum buka (freeSharesLeft 726/1000, openedAt 0, booking 10000 RIG utuh). "
    "Mihao ditambahkan ke track_c sebagai watchlist-only pre-launch (temuan hot-leg 1449). binanceai launched()=0 tetap refund/pending." % BLOCK)
snap["runNote1501_scan"] = ("Run 1501 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized (11,6 dtk, run 1431: 11,6 dtk). "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh; backfill OFF. Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote1501_rigforge"] = ("RigForge re-check run 1501 (blok %s): freeSharesLeft 726/1000 (727 pukul 15:00 hot-leg, 735 pukul 14:19, 746 pukul 14:01), openedAt 0 (pool BELUM buka), "
    "freeClaimed 274, freeBooked(wallet)=10000 RIG. Booking utuh; collectShares baru bisa sesudah pool buka." % BLOCK)
snap["runNote1501_binanceai"] = "Run 1501: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase, isRefundPhase=1, sudah dilaporkan sekali). pending_claims kosong; TIDAK di-preview/diklaim."
snap["runNote1501_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru. Bridge TIDAK ditulis.")
snap["runNote1501_discovery"] = ("Discovery run 1501: Sourcify feed 20 kontrak (verified 07:48-08:04Z): 4 baru - 0 S1/S2 PASS; 1 early-shape-by-name-only 0xB756 (Pawlands Founder Pass, checked-not-agent-shaped, totalSupply 0); "
    "3 checked-not-sale-shape (0xad6e, 0xbA8a, 0x6cE3). Boltbook EN+ZH urllib FAIL ke-4 kalinya berturut-turut (RemoteDisconnected/IncompleteRead) tapi curl OK "
    "(EN 45.922 byte, ZH 46.137 byte, 16 alamat tiap bahasa; 1 baru = AgentRune). Sweep EN+ZH: 0 proyek baru "
    "(Agentic Gangster free-pool-exhausted; Golden Agents age-excluded; Lucky Moments early-lead-reported; MOLT AGENT pool habis; First-Dollar Grove age-excluded; AgentForge 15 hari - age-excluded by publikasi 27 Okt). "
    "Odaily newsflash: 0 item Agent ID/free-mint (makro/pasar saja).")
snap["runNote1501_agentrune"] = ("AgentRune EARLY lead run 1501: kontrak 0xc1fc0bb36d2be928809e4b3e6aa94b3dd2946f53, AgentRune/ARUNE ERC-721, MAX_SUPPLY 4443 (baca on-chain). "
    "Agent-shape TERVERIFIKASI: agentIdRegistry() = 0x60B926...22F (registry Binance); registry bytes di bytecode 13.971 byte; agentIdCheckRequired() ON (Alphapedia); "
    "mint(1) value 0 lolos static eth_call dari wallet user (triage run ini, BUKAN preview). "
    "First mints terverifikasi on-chain: 149 (blok 132922913, baca Alphapedia) -> 164 (post sun1122.ai ~15:00 WIB) -> 168 (probe run ini). "
    "FreeMinted 165/4443 = 3,71% dari MAX; FREE_SUPPLY/free-cap view TIDAK ADA -> % kuota gratis UNVERIFIED. Slot user TERBUKA (priceFor=0, freeUsed=0, balanceOf=0). "
    "Umur <24 jam terverifikasi batas atas [first public post ~15:00 WIB 11 Nov]; first-mint persis unverified (Ankr 401). "
    "Website UNVERIFIED (contractURI kosong, tokenURI(1) kosong; Alphapedia Boltbook bukan situs proyek). X UNVERIFIED. Sourcify UNVERIFIED (404). "
    "Owner 0x36f3d56e... (keluarga SnakeAgentNFT/SAKURA/PanduAGENT/SonoWaves/Hakuna); owner + kontrak BERSIH dari same-owner-discards.json (61 entri). "
    "Dilaporkan sekali sebagai EARLY lead; TIDAK di-preview/dimint.")
snap["runNote1501_age_exclusions"] = ("Run 1501 AGE-EXCLUSIONS (2 item, keduanya SUDAH dilaporkan sekali oleh hot-leg - run ini hanya mengeluarkan dari snapshot, TIDAK melaporkan ulang): "
    "NIGHTFORGE 0x22f43b... (mintStart 2026-11-10 14:37 WIB; verifikasi segar run ini totalSupply 755, agentFreeUsed 752/2000 = 37,6%%, mintOpen 1, slot user terbuka; umur 24 jam 31 mnt; dilaporkan hot-leg 1434 pukul 14:43 WIB) dan "
    "NIGHTFORGE B 0x051f04... (mintStart 2026-11-10 14:51 WIB; reread run ini totalSupply 360; dilaporkan hot-leg 1449 pukul ~14:56 WIB). "
    "Deadline umur yang masih berjalan: ABYSSCABLE ~19:39 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); "
    "AgentPals ~06:33 WIB 12 Nov; SUDOSAINTS konservatif 00:24 WIB 12 Nov; AgentRune konservatif ~15:00 WIB 12 Nov.")
snap["last_run_note"] = ("Run 1501: 1 EARLY lead baru - AgentRune (168/4443, freeMinted 165, slot terbuka, agent-shaped terverifikasi, umur <24 jam batas atas). "
                         "NIGHTFORGE + NIGHTFORGE B age-excluded (sudah dilaporkan hot-leg; dikeluarkan dari snapshot). Scan FAST-FAIL (Ankr 401). "
                         "RigForge pool belum buka (726/1000). binanceai launched()=0 tetap pending.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated, "removed", removed)
