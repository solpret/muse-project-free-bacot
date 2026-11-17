#!/usr/bin/env python3
"""Merge run 1401 (scheduled 2026-11-11 14:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1401-reread.json (block 132925106, 60 contracts + 22 track_c),
run-2026-11-11-1401-legs.json (feed 4 new all not-sale-shape; Boltbook urllib FAIL both,
curl OK; bridge 116/0 new; binanceai launched 0),
boltbook-en/zh-1401.html (curl OK), run-2026-11-11-1401-rigforge-recheck.json,
run-2026-11-11-1401-prio.json (CAP7+SHINE), run-2026-11-11-1401-probe-sudo.json
(SUDOSAINTS early-lead classification), ABYSSCABLE agentFreeUsed direct read 792.
Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1401-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1401-legs.json"))
rigv = json.load(open(BASE + "run-2026-11-11-1401-rigforge-recheck.json"))
prio = json.load(open(BASE + "run-2026-11-11-1401-prio.json"))
sudo = json.load(open(BASE + "run-2026-11-11-1401-probe-sudo.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1401-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 14:01 WIB"

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
        e["runNote1401"] = ("Run 1401 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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

# --- ABYSSCABLE: agentFreeUsed direct read (bukan di LEAN batch) ---
ab = C.get("ABYSSCABLE")
if isinstance(ab, dict):
    ab["previousTotalSupply"] = ab.get("totalSupply")
    ab["totalSupply"] = 792
    ab["agentFreeUsed"] = 792
    ab["freePct"] = round(792 / 2000 * 100, 2)
    ab["mintedInInterval"] = 792 - 787
    ab["lastReadBlock"] = BLOCK
    ab["lastReadWib"] = TS
    ab["runNote1401"] = ("Run 1401 (blok %s, agentFreeUsed baca langsung): totalSupply 787->792 (+5), "
                         "agentFreeUsed 792/2000 = 39,6%% (di bawah 50%% track-A dan 70%% strong lead); "
                         "mintOpen 1, balanceOf(user)=0. Velocity GAGAL (+5 < 20). BUKAN promosi. "
                         "Deadline umur ~19:39 WIB hari ini." % BLOCK)

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

# --- feed-new: 4 contracts, all S1/S2/early False -> checked-not-sale-shape ---
feed_shapes = legs.get("feed_shape", {}).get("shapes", [])
for s in feed_shapes:
    addr = s.get("address")
    if not addr: continue
    key = "Feed-ERC20-" + addr[:10]
    if key in TC: continue
    TC[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-11",
               "note": ("Run 1401 Sourcify feed (verified 06:54-07:03Z): S1=False S2=False early=False; "
                        "mint=%s quote=%s free_views=%s agent_ref=%s is_nft=%s is_token=%s fns=%s. Bukan lead track-C."
                        % (s.get("has_mint"), s.get("has_quote"), s.get("free_views"), s.get("agent_ref"),
                           s.get("is_nft"), s.get("is_token"), s.get("fn_count"))),
               "lastReadWib": TS}

# --- SUDOSAINTS: NEW EARLY LEAD (classified by this main run; hot leg deferred it) ---
if "SUDOSAINTS" not in C:
    C["SUDOSAINTS"] = {
        "address": "0x869d330bb48e7ab32da16745ef9a36a69d34f12f",
        "name": "SUDOSAINTS", "symbol": "SUDO", "kind": "ERC721",
        "status": "early-lead-reported-2026-11-11",
        "totalSupply": 558, "freeMinted": 558, "MAX_SUPPLY": 7777,
        "freePctVerified": round(558 / 7777 * 100, 2),
        "mintOpen": 1, "mintActive": 1,
        "priceFor_user": 0, "freeUsed_user": 0, "balanceOf_user": 0,
        "holdsAgentId_user": 1,
        "owner": "0x42c7e3214a0f1024fc477257282ce3734a707dc9",
        "ownerInDiscards": False,
        "sourcify": "exact_match", "sourcifyFns": 103,
        "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
        "website": "https://sudosaints.pages.dev/",
        "websiteEvidence": "chain.json di situs mencetak kontrak NFT persis + registry Binance + token HALO; situs dicapai via baseURI() on-chain",
        "xVerified": False,
        "discussion": "Boltbook b/alpha post grandtheftauto6.ai ~13:12 WIB (blok 132918159, 529/7777) - audit on-chain + kontrak",
        "firstSeenBlock": 132918159, "firstSeenWib": "2026-11-11 13:12 WIB",
        "deployBlock": 132815788, "deployWib": "2026-11-11 00:24:16 WIB",
        "launchNote": "Umur <24 jam TERVERIFIKASI sebagai batas atas: launch di [deploy 00:24 WIB (blok 132815788, timestamp terverifikasi on-chain via chain.json) , first-sighting 13:12 WIB] -> umur saat 14:01 antara ~0,8 jam dan ~13,6 jam. Waktu first-mint persis UNVERIFIED (Ankr 401 memblokir cek log). Deadline konservatif 00:24 WIB 12 Nov (24 jam dari deploy).",
        "velocityVerified": False,
        "currentRatePerMin": None, "previousRatePerMin": None, "velocityRatio": None,
        "velocityLegPasses": False,
        "lastReadBlock": 132925315, "lastReadWib": TS,
        "baselineNote": "EARLY lead dilaporkan sekali run 1401: agent-shaped terverifikasi (Sourcify exact_match 103 fns; agentIdRegistry()=registry Binance; holdsAgentId(user)=1) + first mints terverifikasi on-chain (529 blok 132918159 -> 537 13:14 -> 545 13:19 -> 555 13:59 -> 558 14:01). Free 558/7777 = 7,17%% (di bawah 50%% track-A dan 70%% strong lead); slot user TERBUKA (priceFor=0, freeUsed=false, balanceOf=0). Website TERVERIFIKASI (chain.json). X UNVERIFIED (situs hanya tautan x.com kosong, tanpa handle). TIDAK PERNAH di-preview/dimint sebagai early lead; promosi hanya bila 3 kaki strong lead terpenuhi.",
        "runNote1401": "Run 1401: klasifikasi early lead oleh job utama (hot leg 1314 menemukan, 1319 menunda ke job utama). Lihat baselineNote.",
    }

# --- RigForge re-check (read-only): pool still closed, booking intact ---
rf = TC.get("RigForge")
if isinstance(rf, dict):
    rf["freeSharesLeft"] = rigv.get("freeSharesLeft")
    rf["openedAt"] = rigv.get("openedAt")
    rf["freeTaken_agentId"] = rigv.get("freeTaken_agentId")
    rf["freeBooked_user"] = rigv.get("freeBooked_user")
    rf["lastReadBlock"] = rigv.get("block_now")
    rf["lastReadWib"] = TS
    rf["note"] = ("Track-C lead MINTED by user 11 Nov 12:12 WIB (tx 0xe766..., blok 132910090, freeBooked 10000 RIG). "
                  "Re-check run 1401 (blok %s): freeSharesLeft %s/1000, openedAt %s (pool BELUM buka - collectShares belum bisa), "
                  "freeTaken(agentId)=%s, freeBooked(wallet)=10000 RIG. Marketplace/rarity TIDAK berlaku (bukan NFT)."
                  % (rigv.get("block_now"), rigv.get("freeSharesLeft"), rigv.get("openedAt"), rigv.get("freeTaken_agentId")))
# --- CAP7 + SHINE priority re-check (read-only) ---
cap7 = prio.get("CAP7") or {}
if isinstance(TC.get("CAP7"), dict):
    e = TC["CAP7"]
    for k in ("freeMinted", "sharesMinted", "paidMinted", "soldOut", "phase", "FREE_SHARES"):
        if cap7.get(k) is not None: e[k] = cap7[k]
    e["lastReadBlock"] = prio.get("block"); e["lastReadWib"] = TS
shine = prio.get("SHINE") or {}
if isinstance(TC.get("SHINE"), dict):
    e = TC["SHINE"]
    for k in ("launch", "launchBlock", "freeClaimed", "sharesSold"):
        if shine.get(k) is not None: e[k] = shine[k]
    e["lastReadBlock"] = prio.get("block"); e["lastReadWib"] = TS

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["runNote1401"] = ("Run 1401 (blok reread %s): 1 EARLY lead BARU - SUDOSAINTS (0x869d33..., 558/7777 = 7,17%% free, slot user terbuka, website terverifikasi via chain.json, umur <24 jam terverifikasi batas atas, X unverified) - dilaporkan sekali run ini, TIDAK di-preview/dimint. "
    "0 kandidat baru / 0 strong-lead mint / 0 track-B / 0 track-C lead baru. "
    "Twill Fullery velocity LOLOS (+24, 1,85x) tapi TETAP EARLY (free%% + umur UNVERIFIED, gate website belum dinilai). "
    "Stampooor 721->735 (+14, 0,54x) velocity GAGAL; 735/1200 = 61,25%% (di atas 50%% track-A, di bawah 70%% strong lead; X/website unverified) tetap EARLY. "
    "0x7Eb9 620->635 (+15, 0,27x) velocity GAGAL, tetap EARLY. "
    "NIGHTFORGE 746->746 (+0) velocity GAGAL, 37,1%%; deadline umur 14:37 WIB hari ini; ABYSSCABLE 787->792 (agentFreeUsed 792/2000 = 39,6%%) deadline ~19:39 WIB; AgentPals 92/300 (30,7%%) deadline ~06:33 WIB 12 Nov. "
    "0 sellout baru, 0 slot user berubah, 0 age-exclusion baru. RigForge pool belum buka (freeSharesLeft 746/1000, openedAt 0)." % BLOCK)
snap["runNote1401_scan"] = ("Run 1401 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized. "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh; backfill OFF. Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote1401_rigforge"] = ("RigForge re-check run 1401 (blok %s): freeSharesLeft 746/1000 (747 pukul 13:59 hot-leg, 766 pukul 13:31, 813 pukul 13:01), openedAt 0 (pool BELUM buka), "
    "sharesLeftFor(agentId)=10, agentShares=0, freeTaken(agentId)=1, freeBooked(wallet)=10000 RIG. Booking utuh; collectShares baru bisa sesudah pool buka." % rigv.get("block_now"))
snap["runNote1401_prio"] = ("Run 1401 prio (blok %s): CAP7 freeMinted 225/640 (35,2%%), phase 1, soldOut 0, slot user balanceOf 0 - gate FAILED (sweep penuh A-N run 1131), TIDAK di-preview/dimint. "
    "SHINE launch=0, freeClaimed=0, sharesSold=0 - masih upcoming (buka 18:00 WIB hari ini)." % prio.get("block"))
snap["runNote1401_binanceai"] = "Run 1401: launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims: binanceai.fun tetap pending, TIDAK di-preview/diklaim."
snap["runNote1401_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru.")
snap["runNote1401_discovery"] = ("Discovery run 1401: Sourcify feed 20 kontrak (verified 06:54-07:03Z): 4 baru, semuanya bukan sale-shape/early "
    "(0xe90D5BEb, 0xc5A4A7B1, 0xB3ca4b94, 0x4b2B1A41) -> checked-not-sale-shape. Boltbook EN+ZH urllib FAIL (RemoteDisconnected/IncompleteRead) tapi curl OK "
    "(EN 45.581 byte, 10 alamat; ZH 45.672 byte, 10 alamat; 0 baru vs snapshot+hot-leg-seen). Sweep EN+ZH: 0 proyek baru "
    "(Agentic Gangster free-pool-exhausted, sudah tercatat; MOLT AGENT free pool habis; Golden Agents sudah di snapshot 1,67%%; "
    "Agent Operators upcoming, kontrak belum terbit; AGENT COSMOS sudah di snapshot; NOVRA/WNO sudah track_c). "
    "Odaily newsflash 200 + PANews 200: 0 item Agent ID/free-mint.")
snap["runNote1401_sudo"] = ("SUDOSAINTS early-lead run 1401: kontrak 0x869d330bb48e7ab32da16745ef9a36a69d34f12f, SUDOSAINTS/SUDO ERC-721, MAX_SUPPLY 7777. "
    "Agent-shape TERVERIFIKASI: Sourcify exact_match (103 fns); agentIdRegistry() = 0x60B926...22F (registry Binance); holdsAgentId(user)=1; freeMinted/freeUsed/mint/priceFor/quoteBulk. "
    "First mints terverifikasi on-chain: 529 (blok 132918159, post Boltbook 13:12) -> 537 (13:14) -> 545 (13:19) -> 555 (13:59) -> 558 (14:01). "
    "Free 558/7777 = 7,17%%; slot user TERBUKA (priceFor=0, freeUsed=false, balanceOf=0). Umur <24 jam terverifikasi batas atas [deploy 00:24 WIB blok 132815788 - first-sighting 13:12 WIB]; "
    "first-mint persis unverified (Ankr 401). Website TERVERIFIKASI: sudosaints.pages.dev (via baseURI on-chain) + chain.json mencetak kontrak NFT persis + registry + token HALO. "
    "X UNVERIFIED (situs hanya tautan x.com kosong). Diskusi TERVERIFIKASI: post Boltbook b/alpha grandtheftauto6.ai ~13:12 WIB. "
    "Discards BERSIH (kontrak + owner 0x42c7e321... tidak ada di 61 entri). Dilaporkan sekali sebagai EARLY lead; TIDAK di-preview/dimint.")
snap["runNote1401_age_exclusions"] = ("0 age-exclusion baru run ini (window 13:31->14:01 WIB). Deadline umur yang masih berjalan: NIGHTFORGE 2026-11-11 14:37 WIB; "
    "ABYSSCABLE ~19:39 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); "
    "AgentPals ~06:33 WIB 12 Nov; SUDOSAINTS konservatif 00:24 WIB 12 Nov. Tidak ada item lain yang dihapus dari snapshot.")
snap["last_run_note"] = ("Run 1401: 1 EARLY lead baru - SUDOSAINTS (558/7777 = 7,17%%, slot terbuka, website terverifikasi, umur <24 jam). "
                         "Twill Fullery velocity LOLOS (+24, 1,85x) tapi tetap EARLY (free%%/umur unverified). Scan FAST-FAIL (Ankr 401). "
                         "RigForge pool belum buka (746/1000). binanceai launched()=0 tetap pending.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated)
