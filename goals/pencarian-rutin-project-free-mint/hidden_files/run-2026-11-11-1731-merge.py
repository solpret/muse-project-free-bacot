#!/usr/bin/env python3
"""Merge run 1731 (scheduled 2026-11-11 17:31 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1731-reread.json (block 132953022, 62 contracts + 23 track_c),
run-2026-11-11-1731-legs.json (feed 20, verified 10:21-10:32Z, 14 new; Boltbook EN
44.533 byte / 9 addrs, ZH 42.806 byte / 9 addrs; bridge 116/0 new/7 discarded;
binanceai launched 0; RigForge 704/0/296, freeBooked 10000 RIG),
run-2026-11-11-1731-shape-retry.json (curl retry 13 IncompleteRead: 0 S1/S2,
11x 35-fn generic-mint NFT wave, 0xc6D5 token-no-mint, 0x7935 23-fn no-shape),
run-2026-11-11-1731-ramraiders.json (block 132953896: RAMRAIDERS 551/7777,
freeMinted 551, mintActive 1, priceFor(user) 0, holdsAgentId 1, freeUsed(user) 0,
Sourcify exact_match 103 fns; contractURI/tokenURI reads returned no data).
RAMRAIDERS added as EARLY lead (reported once via this run's result).
Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1731-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1731-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1731-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 17:31 WIB"

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
        e["runNote1731_1111"] = ("Run 1731 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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
        C[name]["runNote1731_1111"] = text

note("0x7Eb9", "Run 1731 (blok %s): totalMinted 748->815 (+67, 2,2333/mnt vs prev 0,6 = 3,72x) -> velocity LOLOS. TAPI TANPA promosi: free%% + umur UNVERIFIED, website/X UNVERIFIED. Tetap EARLY lead; TIDAK di-preview/dimint." % BLOCK)
note("Skywe Legion", "Run 1731 (blok %s): totalSupply 519->573 (+54, 1,8/mnt vs prev 0,0333 = 54,05x) -> velocity LOLOS. TAPI TANPA promosi: free%% UNVERIFIED (FREE_SUPPLY tidak ada), umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint." % BLOCK)
note("RIMEVAULT", "Run 1731 (blok %s): totalSupply 951->977 (+26, 0,8667/mnt vs prev 0,2667 = 3,25x) -> velocity LOLOS. Minted-by-user 11 Nov (balanceOf=1) - BUKAN kandidat/promosi." % BLOCK)
note("Stampooor Stamp Packs", "Run 1731 (blok %s): totalMinted 811->820 (+9, <20; 0,3/mnt vs prev 0,2667 = 1,12x) velocity GAGAL; freeMinted 820/1200 = 68,3%% (masih di bawah 70%% strong lead); balanceOf(user)=0; tetap EARLY. TIDAK di-preview/dimint." % BLOCK)
note("AgentPals", "Run 1731 (blok %s): totalMinted/freeMinted 111->115 (+4, <20; 0,1333/mnt vs prev 0,2667 = 0,5x) velocity GAGAL; 115/300 = 38,3%%; balanceOf(user)=0; tetap watchlist-only, jauh di bawah 70%%. Website tetap UNVERIFIED. Deadline umur ~06:33 WIB 12 Nov." % BLOCK)
note("HANAMI BLOOM", "Run 1731 (blok %s): totalSupply=freeMinted 101->102 (+1, <20) velocity GAGAL; 102/3,333 = 3,06%%; balanceOf(user)=0; umur ~4 jam (mint-start ~12:59 WIB, deadline ~12:59 WIB 12 Nov). Tetap EARLY lead; TIDAK di-preview/dimint." % BLOCK)
note("ABYSSCABLE", "Run 1731 (blok %s): totalSupply 818->821 (+3, <20; 0,1/mnt vs prev 0,1333 = 0,75x) velocity GAGAL; balanceOf(user)=0; deadline umur ~19:39 WIB hari ini. BUKAN promosi." % BLOCK)
note("AgentRune", "Run 1731 (blok %s): totalSupply 186->187 (+1, <20) velocity GAGAL; freeMinted 187/4443 = 4,21%% dari MAX (FREE_SUPPLY/free-cap view TIDAK ADA -> %% kuota gratis tetap UNVERIFIED); balanceOf(user)=0; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("SUDOSAINTS", "Run 1731 (blok %s): totalSupply 592->596 (+4, 2,0x) velocity GAGAL; freeMinted 596/7777 = 7,66%% (jauh di bawah 70%% strong lead); balanceOf(user)=0; tetap EARLY lead. TIDAK di-preview/dimint." % BLOCK)
note("Foundry Faces", "Run 1731 (blok %s): totalSupply() tetap revert, totalMinted 799->829 (+30 via totalMinted); free views SEMUA None; balanceOf(user)=0; umur + free%% + website tetap UNVERIFIED; tetap watchlist-only-age-unverified. BUKAN promosi (velocity dihitung dari totalSupply, bukan totalMinted)." % BLOCK)
note("STALL", "Run 1731 (blok %s): totalSupply 1942->1946 (+4) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("Twill Fullery", "Run 1731 (blok %s): totalSupply 158->164 (+6, 6,01x) velocity GAGAL (<20); balanceOf(user)=0; tetap EARLY (free%%/umur unverified)." % BLOCK)
note("WORKER", "Run 1731 (blok %s): totalSupply 676->679 (+3) velocity GAGAL; balanceOf(user)=0." % BLOCK)
note("Kitebots", "Run 1731 (blok %s): totalSupply 1116->1182 (+66, 2,2/mnt vs prev 3,7 = 0,59x) velocity GAGAL. TANPA promosi: free%% UNVERIFIED (FREE_SUPPLY tidak ada; 1182/4000 MAX = 29,55%% BUKAN %% kuota gratis), umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint." % BLOCK)
note("MYCELIX", "Run 1731 (blok %s): totalSupply 613->614 (+1) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov); deadline umur ~21:47 WIB hari ini." % BLOCK)
note("SOLDERCATS", "Run 1731 (blok %s): totalSupply 538->539 (+1) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:35 WIB hari ini." % BLOCK)
note("LCDSPRITE", "Run 1731 (blok %s): totalSupply 578->580 (+2) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:52 WIB hari ini." % BLOCK)
note("REWINDCLUB", "Run 1731 (blok %s): totalSupply 557->559 (+2) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:49 WIB hari ini." % BLOCK)
note("ORBITJANITOR", "Run 1731 (blok %s): totalSupply 717->718 (+1) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov)." % BLOCK)
note("EMBERANVIL", "Run 1731 (blok %s): totalSupply 1114->1118 (+4, 2,0x) velocity GAGAL (<20); balanceOf(user)=1." % BLOCK)
note("BYTEBLOOM", "Run 1731 (blok %s): totalSupply 816->819 (+3) velocity GAGAL; balanceOf(user)=1." % BLOCK)

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
    TC["VISION"]["runNote1731_1111"] = ("Run 1731 (blok %s): totalSupply 3,3876e27 -> 3,3948e27 (+7,2 jt token); freeMinted view tetap None; "
        "status watchlist-only-age-unverified, TIDAK promosi." % BLOCK)

# --- RAMRAIDERS: EARLY lead baru (Boltbook recheck -> triase run ini) ---
rr = json.load(open(BASE + "run-2026-11-11-1731-ramraiders.json"))
C["RAMRAIDERS"] = {
    "address": "0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b",
    "status": "early-lead-reported-2026-11-11",
    "name": "RAMRAIDERS", "symbol": "RAID", "kind": "ERC721",
    "totalSupply": rr.get("totalSupply"), "freeMinted": rr.get("freeMinted"),
    "FREE_SUPPLY": 7777, "MAX_SUPPLY": rr.get("MAX_SUPPLY"),
    "freePctVerified": round(100 * rr["freeMinted"] / 7777, 2) if rr.get("freeMinted") else None,
    "mintActive": rr.get("mintActive"), "deckRemaining": rr.get("deckRemaining"),
    "priceFor_user": rr.get("priceFor_user"), "holdsAgentId_user": rr.get("holdsAgentId_user"),
    "freeUsed_user": rr.get("freeUsed_user"), "balanceOf_user": rr.get("balanceOf_user"),
    "freeSlotUserOpen": True,
    "firstSeenBlock": None,
    "firstSeenWib": "2026-11-11 17:31 WIB (job ini, via Boltbook)",
    "hotLegFirstSeenWib": "2026-11-11 00:30:24 WIB (pre-launch)",
    "launchNote": ("Pre-launch 2026-11-11 00:30 WIB (hot-leg leg3: totalSupply 0, mintActive 0, deckRemaining 7777/7777); "
        "549 minted per Boltbook recheck 17:33 WIB (agata.ai), 551 terverifikasi on-chain blok 132953896 ~17:40 WIB. "
        "Launch dalam (00:30, 17:33] WIB 11 Nov -> umur <24 jam terverifikasi via bound dua pembacaan on-chain; "
        "blok/jam first-mint eksak UNVERIFIED (Ankr getLogs 401, Transfer-from-zero tidak bisa dibaca). "
        "Deadline umur konservatif ~00:30 WIB 12 Nov."),
    "discussion": "Boltbook recheck post 2026-11-11 17:33 WIB oleh agata.ai (b/alpha): 549/7.777, mint(1) value 0 lolos, UNGATED, Sourcify exact_match.",
    "xVerified": False, "velocityVerified": False, "velocityLegPasses": False,
    "currentRatePerMin": None, "previousRatePerMin": None,
    "website": None, "websiteVerified": False,
    "websiteNote": ("contractURI()/tokenURI(1) run ini mengembalikan tanpa data (tidak ada pointer); "
        "gate website BELUM dijalankan (early lead tidak pernah di-preview/dimint) - run berikut jalankan metode gate (A)-(N)."),
    "sourcifyMatch": rr.get("sourcify", {}).get("match"), "fnCount": rr.get("sourcify", {}).get("fn_count"),
    "agentShape": "agent-shaped: Sourcify exact_match 103 fns, free views freeMinted/freeUsed, mint+quote, holdsAgentId gate (holdsAgentId(user)=1); registry 0x60B9...022F tercatat hot-leg leg3 0024 (cek registry_ref run ini False karena alamat hanya di bytecode, bukan di JSON ABI).",
    "baselineNote": ("EARLY lead dilaporkan sekali run 1731. BUKAN kandidat (7,08% < 50%), BUKAN strong lead (7,08% < 70%), "
        "velocity belum terhitung (pembacaan pertama di snapshot), X + website UNVERIFIED. TIDAK PERNAH di-preview/dimint sebagai early lead."),
    "lastReadBlock": rr.get("block"), "lastReadWib": TS,
    "runNote1731_1111": ("Run 1731 (blok %s): EARLY lead baru - totalSupply=freeMinted 551/7777 = 7,08%%, mintActive 1, deckRemaining 7226, "
        "priceFor(user)=0, holdsAgentId(user)=1, freeUsed(user)=0, balanceOf(user)=0 (slot terbuka). "
        "Dilaporkan sekali sebagai EARLY lead; masuk watchlist untuk tracking velocity." % rr.get("block")),
}

# --- feed-new checked-not-agent-shaped (curl retry run ini) ---
TC["Feed-NFT-wave-35fn-2026-11-11"] = {
    "status": "checked-not-agent-shaped-2026-11-11",
    "addresses": ["0xbC1Ee9A9e1E9C61E3bF6073351cc79E6a284ce34","0xA77Bfe8072b4F3Abe9338D11d9B8AdF4DBFC9116",
        "0x704C1D17564E06991d0B898f882Fbc699fcFd9eD","0x6016E57585375B93C52Eea127f2dE751e08C012A",
        "0xe80bf8FE70105273B73D98CD14A1B3be3F31De94","0x6b2101041131Fc272EC94A8f3881B09af945107d",
        "0xe881812b2d6347e1446D2851136C5cBD9E6C03be","0xccd54b2361fA556faD30Df0267DAbf11aDE2FeaB",
        "0x32Dd9EF2eB52Cd999aCb9bce6fC9604FbE6963F7","0x9081f02876c173d0C69f042959CfD0d61C668b17",
        "0x803093925D77277122aAE684eb0C71E530Da3Fbc"],
    "note": ("Run 1731 Sourcify feed (verifiedAt 2026-11-11T10:21-10:32Z): 11 kontrak template sama (ABI 35 fns, is_nft True, mint+quote ADA) "
        "tapi TANPA free view, TANPA agent ref (registry/AgentGate), TANPA fungsi free-mint (mint() generik bukan free-mint). "
        "GAGAL S1/S2 dan BUKAN early lead (butuh registry/AgentGate/free-mint function/free-supply constant). "
        "First mints TIDAK terverifikasi (scan Ankr 401). Dicatat checked saja; tidak masuk watchlist kontrak."),
    "lastReadWib": TS}
TC["Feed-ERC20-0xc6D5961A"] = {"address": "0xc6D5961Ab6499Ce214f210e29d36C3e04040770e",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1731 Sourcify feed: ABI 50 fns, quote ADA, agent_ref True (nama registry di ABI) tapi TANPA fungsi mint dan TANPA free view; "
        "is_token True, BUKAN NFT. GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja."),
    "lastReadWib": TS}
TC["Feed-0x7935d9AC"] = {"address": "0x7935d9AC76F6d5ce60b1B7530990F78AB0A1c2C2",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1731 Sourcify feed: ABI 23 fns, TANPA mint/quote/free view/agent ref, BUKAN token/NFT. "
        "GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja."),
    "lastReadWib": TS}
TC["Feed-ERC20-0xbd42DD31"] = {"address": "0xbd42DD317D90bfA8d61cC0bef67B3B91D00Bd68F",
    "status": "checked-not-agent-shaped-2026-11-11",
    "note": ("Run 1731 Sourcify feed: ABI 1 fn, TANPA mint/quote/free view/agent ref, BUKAN token/NFT. "
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
                  "Re-check run 1731 (blok %s): freeSharesLeft %s/1000 (709 pukul 17:01, 704 pukul 17:31), openedAt %s (pool BELUM buka - collectShares belum bisa), "
                  "freeClaimed %s, freeBooked(wallet)=10000 RIG. Booking utuh. Marketplace/rarity TIDAK berlaku (bukan NFT)."
                  % (BLOCK, rigv.get("freeSharesLeft"), rigv.get("openedAt"), rigv.get("freeClaimed")))

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["runNote1731_1111"] = ("Run 1731 (blok reread %s): 1 EARLY lead baru - RAMRAIDERS 551/7777 = 7,08%% (dilaporkan sekali); "
    "0 kandidat baru / 0 strong-lead mint / 0 track-B dibuka / 0 track-C lead baru. "
    "Velocity LOLOS: 3 - 0x7Eb9 +67 (3,72x), Skywe Legion +54 (54,05x), RIMEVAULT +26 (3,25x) - SEMUA TANPA promosi "
    "(free%%/umur/X unverified, atau minted-by-user). "
    "Stampooor 820/1200 = 68,3%% (<70%% strong lead), AgentPals 115/300 = 38,3%%. "
    "Feed baru 14: 0 S1/S2; 11x template 35-fn + 3 lain BUKAN agent-shaped (curl retry), dicatat checked saja. "
    "RigForge pool belum buka (freeSharesLeft 704/1000, openedAt 0, booking 10000 RIG utuh). binanceai launched()=0 tetap pending." % BLOCK)
snap["runNote1731_1111_scan"] = ("Run 1731 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized. "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh (sudah dilaporkan sekali untuk watermark ini 9 Nov - DIAM, tidak lapor ulang); backfill OFF. Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote1731_1111_rigforge"] = ("RigForge re-check run 1731 (blok %s): freeSharesLeft 704/1000 (709 pukul 17:01, 704 pukul 17:31), openedAt 0 (pool BELUM buka), "
    "freeClaimed 296, freeBooked(wallet)=10000 RIG. Booking utuh; collectShares baru bisa sesudah pool buka." % BLOCK)
snap["runNote1731_1111_binanceai"] = "Run 1731: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong; TIDAK di-preview/diklaim."
snap["runNote1731_1111_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru. Bridge TIDAK ditulis.")
snap["runNote1731_1111_discovery"] = ("Discovery run 1731: Sourcify feed 20 kontrak (verified 10:21-10:32Z): 14 baru - 0 S1/S2; 11x template 35-fn (mint+quote, tanpa free view/agent) "
    "BUKAN agent-shaped, BUKAN early lead (curl retry setelah urllib IncompleteRead x13); 0xc6D5 token tanpa mint/free; 0x7935 23 fns tanpa shape; 0xbd42 1 fn. Dicatat checked saja. "
    "Boltbook EN OK (44.533 byte, 9 alamat), ZH OK via curl (42.806 byte, 9 alamat); 1 alamat baru = owner RAMRAIDERS (0x6f17...) -> RAMRAIDERS 0x98dc... ditriase -> EARLY lead baru. "
    "Sweep EN+ZH (browser.search): 0 proyek baru (BURN excluded-free-sold-out 9 Nov; WNO minted-by-user 10 Nov; NOVRA pool habis 8 Nov; Agentic Gangster pool habis 11 Nov; "
    "Horus AI free phase sold out 2000/2000 + soulbound; Oathbots age-excluded ~14 hari; First-Dollar Grove age-excluded ~3 hari; AGENT MAO site paused 530; UFO/NEBULA sudah terlacak). "
    "Odaily newsflash (text fetch, 1 item terbaca): 0 item Agent ID/free-mint (hanya Gate Flash Swap). PANews homepage (text fetch): 0 item Agent ID/free-mint.")
snap["runNote1731_1111_age"] = ("Run 1731 AGE: tidak ada age-exclusion baru. Deadline umur yang masih berjalan: ABYSSCABLE ~19:39 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, "
    "MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); AgentPals ~06:33 WIB 12 Nov; HANAMI BLOOM ~12:59 WIB 12 Nov; "
    "RAMRAIDERS konservatif ~00:30 WIB 12 Nov (launch dalam (00:30, 17:33] WIB 11 Nov).")
snap["last_run_note"] = ("Run 1731: 1 EARLY lead baru (RAMRAIDERS 551/7777 = 7,08%%). 0 kandidat/strong/track-C lead baru. Velocity LOLOS 3 (0x7Eb9, Skywe Legion, RIMEVAULT) tanpa promosi. "
                         "Stampooor 820/1200 = 68,3%%, AgentPals 115/300 = 38,3%%. Scan FAST-FAIL (Ankr 401). "
                         "RigForge pool belum buka (704/1000). binanceai launched()=0 tetap pending.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated)
