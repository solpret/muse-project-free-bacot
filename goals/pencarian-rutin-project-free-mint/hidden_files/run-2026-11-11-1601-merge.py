#!/usr/bin/env python3
"""Merge run 1601 (scheduled 2026-11-11 16:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1601-reread.json (block 132941099, 60 contracts + 23 track_c),
run-2026-11-11-1601-legs.json (feed 1 new: Digital Nexus 0x8a79, S1/S2 false, early_shape loose-True but NOT agent-shaped;
Boltbook EN 43.710 byte / ZH 42.077 byte via curl, 19 addrs each, 0 new; bridge 116/0 new/7 discarded;
binanceai launched 0; RigForge 715/0/285),
run-2026-11-11-1601-probe-bbnew.json (HANAMI BLOOM 0x8A74: totalSupply=freeMinted=97/3333),
run-2026-11-11-1601-probe-feed8a79.json (Digital Nexus: name DNEX, totalSupply 3333, totalMinted 1, no free views/agent),
run-2026-11-11-1601-bbpost-QAuNYE3t4uFt.html (Boltbook post belski.ai: minted #1621 free ~12:59 WIB, two-gate Agent ID route table).
Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1601-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1601-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1601-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 16:01 WIB"

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
        e["runNote1601"] = ("Run 1601 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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
        C[name]["runNote1601"] = text

note("AgentRune", "Run 1601 (blok %s): totalSupply 176->179 (+3, <20) velocity GAGAL; freeMinted 173->176 (176/4443 = 3,96%% dari MAX; FREE_SUPPLY/free-cap view TIDAK ADA -> %% kuota gratis tetap UNVERIFIED); balanceOf(user)=0, slot terbuka; website/X/Sourcify tetap UNVERIFIED; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("SUDOSAINTS", "Run 1601 (blok %s): totalSupply 575->579 (+4, <20) velocity GAGAL; freeMinted 579/7777 = 7,44%% (jauh di bawah 70%% strong lead); balanceOf(user)=0, slot terbuka; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("Stampooor Stamp Packs", "Run 1601 (blok %s): totalMinted 772->787 (+15, <20) velocity GAGAL; freeMinted 787/1200 = 65,6%% (masih di bawah 70%% strong lead; hot-leg 1559 baca 785/1200); balanceOf(user)=0; tetap EARLY. Website/umur unverified. TIDAK di-preview/dimint." % BLOCK)
note("0x7Eb9", "Run 1601 (blok %s): totalMinted 677->687 (+10, <20) velocity GAGAL; balanceOf(user)=0; tetap EARLY." % BLOCK)
note("Twill Fullery", "Run 1601 (blok %s): totalSupply 150->155 (+5, <20) velocity GAGAL; balanceOf(user)=0; tetap EARLY (free%%/umur unverified)." % BLOCK)
note("AgentPals", "Run 1601 (blok %s): totalMinted/freeMinted=100 (95->100, +5, <20) velocity GAGAL; freeMinted 100/300 = 33,3%% (hot-leg 1559 baca 99/300); balanceOf(user)=0; tetap watchlist-only, jauh di bawah 70%%. Website tetap UNVERIFIED. Deadline umur ~06:33 WIB 12 Nov." % BLOCK)
note("ABYSSCABLE", "Run 1601 (blok %s): totalSupply 806->813 (+7, <20) velocity GAGAL; agentFreeUsed 812/2000 = 40,6%% (hot-leg 1559); balanceOf(user)=0; deadline umur ~19:39 WIB hari ini. BUKAN promosi." % BLOCK)
note("STALL", "Run 1601 (blok %s): totalSupply 1935->1939 (+4, <20) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("WORKER", "Run 1601 (blok %s): totalSupply 667->668 (+1) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("Kitebots", "Run 1601 (blok %s): totalSupply 993->999 (+6, <20) velocity GAGAL; balanceOf(user)=0; tetap watchlist-only-age-unverified." % BLOCK)

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
    TC["Mihao"]["runNote1601"] = ("Run 1601 (blok %s): freeMinted 0, totalMinted 0, opened 0 - tetap FLAT pre-launch; "
        "watchlist-only, TIDAK dilaporkan sebagai lead, TIDAK di-preview/dimint." % BLOCK)
if isinstance(TC.get("11-11"), dict):
    TC["11-11"]["runNote1601"] = ("Run 1601 (blok %s): freeMinted 626 FLAT vs run 1531. Perubahan watchlist biasa, bukan promosi." % BLOCK)

# --- feed-new: Digital Nexus 0x8a79 — S1/S2 false; early_shape loose-True tapi BUKAN early lead ---
TC["Feed-ERC20-0x8a7917F5"] = {"address": "0x8a7917F55D1b0eE7b2BefF519f55cBaC07906c0D",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1601 Sourcify feed (verified 08:11-09:00Z): S1=False S2=False; legs-script early_shape=True HANYA karena is_nft + mint() ada "
             "(definisi longgar). Probe segar run ini: name Digital Nexus (DNEX), MAX_SUPPLY 3333, totalSupply 3333, totalMinted 1, "
             "freeClaimed/freeMinted/FREE_SUPPLY/mintOpen/owner SEMUA revert (tidak ada free view), agent_ref False, free_views []. "
             "TIDAK ada free-mint function (hanya plain mint), TIDAK ada free-supply constant, TIDAK ada registry/AgentGate -> BUKAN agent-shaped, "
             "BUKAN early lead, BUKAN track-C. Dicatat checked saja; tidak masuk watchlist kontrak."),
    "lastReadWib": TS}

# --- HANAMI BLOOM 0x8A74: EARLY lead baru (Boltbook hot-leg 15:59 -> verifikasi run ini) ---
C["HANAMI BLOOM"] = {
    "address": "0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640",
    "status": "early-lead-reported-2026-11-11",
    "name": "HANAMI BLOOM", "symbol": None, "kind": "ERC721",
    "totalSupply": 97, "totalMinted": 97, "freeMinted": 97, "FREE_SUPPLY": None, "MAX_SUPPLY": 3333,
    "freePctVerified": 2.91, "mintOpen": None, "balanceOf_user": 0, "freeClaimed_user": None,
    "firstSeenBlock": None,
    "discovery": "Boltbook front page EN+ZH (hot-leg 15:59) -> post /p/QAuNYE3t4uFt belski.ai",
    "launchNote": ("Umur TERVERIFIKASI <24 jam: poster belski.ai mint #1621 GRATIS via mintFree() ~12:59 WIB 11 Nov (gas ~Rp350); "
                   "totalSupply=freeMinted=92/3,333 pukul 15:47-15:58 WIB (post), 97/3,333 pada baca segar run 1601 (blok 132941099). "
                   "Mint-start ~12:59 WIB -> umur ~3 jam saat run. First-mint corroboration: poster memegang #1621."),
    "agentNote": ("Agent-shape: mintFree() + freeMinted + MAX_SUPPLY terverifikasi on-chain via eth_call; gate Agent ID DIBUKTIKAN via route table poster "
                  "(dua node RPC sepakat): mintFree() dari wallet Agent ID dengan kuota terpakai revert 0x0b97edb8, dari fresh wallet tanpa Agent ID revert 0xf947691f "
                  "di SEMUA route; jatah gratis 1 per Agent-ID wallet. Sourcify TIDAK terverifikasi (404) -> ABI/registry TIDAK bisa dicek langsung; "
                  "owner() mengembalikan data non-address (UNVERIFIED; poster menyatakan owner checked OK saat mint). Owner TIDAK ada di same-owner-discards.json (73 entri)."),
    "website": None, "websiteNote": "UNVERIFIED: tidak ada situs di post Boltbook; pencarian nama+kontrak tidak menemukan situs proyek. X: UNVERIFIED (tidak ada handle di post).",
    "velocityNote": "Bacaan PERTAMA run ini (97/3333): belum ada rate sebelumnya -> velocity TIDAK lolos sendirian; 92->97 dalam ~10 mnt (~0,5/mnt, nyaris beku 3 jam).",
    "slotNote": "User balanceOf 0 (belum pegang). Slot user UNVERIFIED - early lead TIDAK PERNAH di-preview/disimulasikan; sim mintFree() TIDAK dilakukan run ini.",
    "runNote1601": ("EARLY LEAD BARU run 1601 (blok %s): HANAMI BLOOM 0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640, totalSupply=freeMinted=97/3,333 (2,91%%), "
                    "MAX_SUPPLY 3333, umur ~3 jam (mint pertama poster ~12:59 WIB), gate Agent ID dua-selektor (0x0b97edb8 kuota terpakai / 0xf947691f tanpa Agent ID), "
                    "website/X UNVERIFIED, Sourcify UNVERIFIED, velocity bacaan pertama. Dilaporkan SEKALI sebagai EARLY lead; TIDAK di-preview/dimint." % BLOCK),
    "lastReadBlock": BLOCK, "lastReadWib": TS}

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
                  "Re-check run 1601 (blok %s): freeSharesLeft %s/1000 (716 pukul 15:54 hot-leg, 715 pukul 15:59 hot-leg), openedAt %s (pool BELUM buka - collectShares belum bisa), "
                  "freeClaimed %s, freeBooked(wallet)=10000 RIG. Booking utuh. Marketplace/rarity TIDAK berlaku (bukan NFT)."
                  % (BLOCK, rigv.get("freeSharesLeft"), rigv.get("openedAt"), rigv.get("freeClaimed")))

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["runNote1601"] = ("Run 1601 (blok reread %s): 1 EARLY LEAD BARU - HANAMI BLOOM 0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640 (97/3,333 = 2,91%%, umur ~3 jam, gate Agent ID dua-selektor, website/X UNVERIFIED). "
    "0 kandidat baru / 0 strong-lead mint / 0 track-B dibuka / 0 track-C lead baru. "
    "Velocity LOLOS: tidak ada (semua interval <20 token; AgentRune +3, SUDOSAINTS +4, STALL +4, ABYSSCABLE +7, Twill Fullery +5, Stampooor +15, 0x7Eb9 +10, AgentPals +5). "
    "Stampooor totalMinted 787/1200 = 65,6%% (<70%% strong lead), tetap EARLY. AgentPals 100/300 = 33,3%%, tetap watchlist-only. "
    "Digital Nexus 0x8a79 (feed baru): BUKAN agent-shaped (tanpa free view/agent), dicatat checked saja. "
    "RigForge pool belum buka (freeSharesLeft 715/1000, openedAt 0, booking 10000 RIG utuh). binanceai launched()=0 tetap pending." % BLOCK)
snap["runNote1601_scan"] = ("Run 1601 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized. "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh; backfill OFF. Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote1601_rigforge"] = ("RigForge re-check run 1601 (blok %s): freeSharesLeft 715/1000 (716 pukul 15:54, 715 pukul 15:59 hot-leg), openedAt 0 (pool BELUM buka), "
    "freeClaimed 285, freeBooked(wallet)=10000 RIG. Booking utuh; collectShares baru bisa sesudah pool buka." % BLOCK)
snap["runNote1601_binanceai"] = "Run 1601: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong; TIDAK di-preview/diklaim."
snap["runNote1601_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru. Bridge TIDAK ditulis.")
snap["runNote1601_discovery"] = ("Discovery run 1601: Sourcify feed 20 kontrak (verified 08:11-09:00Z): 1 baru - Digital Nexus 0x8a79, 0 S1/S2; BUKAN agent-shaped (probe segar: tanpa free view/agent, totalMinted 1), dicatat checked-not-agent-shaped. "
    "Boltbook EN+ZH urllib FAIL (RemoteDisconnected/IncompleteRead) tapi curl OK (EN 43.710 byte, ZH 42.077 byte, 19 alamat tiap bahasa; 0 baru vs seen/snapshot - 0x8A74 sudah di hot-leg-seen via hot-leg 1559). "
    "HANAMI BLOOM 0x8A74 diverifikasi segar run ini dari post belski.ai /p/QAuNYE3t4uFt (mint #1621 gratis ~12:59 WIB, gate Agent ID dua-selektor) -> EARLY LEAD BARU. "
    "Sweep EN+ZH: 0 proyek baru (Agentic Gangster free pool SOLD OUT 111/111 - menguatkan status snapshot checked-free-pool-exhausted; Golden Agents age-excluded; NOVRA pool exhausted; WNO minted-by-user; Oathbots 28 Okt age-excluded). "
    "Odaily newsflash: 0 item Agent ID/free-mint (makro/CPI/BTC saja).")
snap["runNote1601_hanami"] = ("HANAMI BLOOM 0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640 - EARLY LEAD BARU run 1601: totalSupply=freeMinted=97/3,333 (2,91%%), MAX_SUPPLY 3333, "
    "umur TERVERIFIKASI ~3 jam (poster belski.ai mint #1621 gratis via mintFree() ~12:59 WIB 11 Nov; 92/3,333 pukul 15:47-15:58 WIB -> 97 run ini). "
    "Gate Agent ID: mintFree() wallet Agent ID kuota-terpakai revert 0x0b97edb8, fresh wallet tanpa Agent ID revert 0xf947691f di semua route (dua node RPC sepakat, route table poster). "
    "Sourcify UNVERIFIED (404), website UNVERIFIED, X UNVERIFIED, owner() non-address (UNVERIFIED; owner tidak ada di discards), velocity bacaan pertama, slot user UNVERIFIED (tidak di-preview - early lead TIDAK PERNAH di-preview). "
    "Dilaporkan SEKALI sebagai EARLY lead; promosi ke strong lead butuh >70%% + slot terbuka + umur <24 jam; ke kandidat butuh semua kaki + website + safety.")
snap["runNote1601_age"] = ("Run 1601 AGE: tidak ada age-exclusion baru. Deadline umur yang masih berjalan: ABYSSCABLE ~19:39 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, "
    "MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); SUDOSAINTS konservatif ~00:24 WIB 12 Nov; AgentPals ~06:33 WIB 12 Nov; AgentRune konservatif ~15:00 WIB 12 Nov; HANAMI BLOOM ~12:59 WIB 12 Nov.")
snap["last_run_note"] = ("Run 1601: EARLY LEAD BARU HANAMI BLOOM 0x8A74 (97/3,333, umur ~3 jam, gate Agent ID). 0 kandidat/strong/track-C lead baru. "
                         "Stampooor 787/1200 = 65,6%%, AgentPals 100/300 = 33,3%%. Scan FAST-FAIL (Ankr 401). "
                         "RigForge pool belum buka (715/1000). binanceai launched()=0 tetap pending.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated)
