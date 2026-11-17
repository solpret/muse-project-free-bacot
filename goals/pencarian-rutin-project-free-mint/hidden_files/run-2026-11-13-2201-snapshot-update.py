#!/usr/bin/env python3
"""Snapshot update for free-mint-search run 2026-11-13 22:01 WIB.
Applies run-2026-11-13-2201-verify.json + triage + sweep outcomes.
Read-only on chain; only edits the local snapshot JSON."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-13-2201-verify.json"))
triage = json.load(open(BASE + "run-2026-11-13-2201-triage.json"))
BLOCK = verify["block"]
RUN = "2201"
NOTE = "2026-11-13 ~22:01 WIB"

contracts = snap.setdefault("contracts", {})
by_addr = {}
for k, v in contracts.items():
    if isinstance(v, dict) and v.get("address"):
        by_addr[v["address"].lower()] = k

KEYMAP = {
    "HIVE": "HIVE Agents", "Pickgrid": "Pickgrid Pickaxe", "OLIVER": "Oliver Agents",
    "RoyalRush": "Royal Rush Agents", "Mossbound": "Mossbound Key", "Slate": "Slate Insignia",
    "Ochre": "Ochre Medallion", "DragonAgent": "Dragon Agent", "VioletWaybill": "Violet Waybill",
    "CinderCrucible": "Cinder Crucible", "BUBB": "Agent Bubble", "MossSignal": "Moss Signal",
    "AgentCosmos": "AGENT COSMOS", "HANAMI": "HANAMI BLOOM", "FROST": "Frostagent",
    "BUILD": "BUILD", "Moon": "Moon", "Zora": "Zora Agent", "D8DA": "0xd8dA6BF2",
    "LNFT": "Laptop NFT", "APGB": "AlphaPulse Genesis Badge",
    "B9F3": "checked-0x9f3c-2131", "CDD8": "checked-0xcdd8-2131",
    "Mihao": "Mihao", "Kitebots": "Kitebots", "JAGENT": "JAGENT",
    "AgentGrove": "Agent Grove", "PromptPirates": "PROMPTPIRATES", "RamRaiders": "RAMRAIDERS",
    "LuckyCatch": "Lucky Catch", "Cobalt": "Cobalt Agent", "Thor": "Thor", "Vexa": "Vexa",
    "SynergyPass": "SYNERGYPASS", "SudoSaints": "SUDOSAINTS", "AgentRune": "AgentRune",
    "Eb9": "0x7Eb9", "OBFG": "OBFG", "NOTV": "NOTV", "JNTM": "JNTM", "Agentx": "Agentx",
    "OUTY": "OUTY", "PX24": "PX24", "SKRR": "SKRR", "ME30": "ME30", "CY24": "CY24",
    "MECHA": "MECHA", "Zero": "Zero", "BC1B": "BC1B",
}

def interval_min(prev_block):
    if not prev_block:
        return 30.0
    return max(1.0, (BLOCK - prev_block) * 0.45 / 60.0)

updated = []
for name, rd in verify["reads"].items():
    views = rd.get("views") or {}
    addr = rd.get("address")
    key = KEYMAP.get(name) or by_addr.get((addr or "").lower())
    if name in ("BinanceAI-mint", "BinanceAI-token"):
        continue
    if name == "AgentMuse":
        # track_c entry (sale contract)
        tc = snap.setdefault("track_c", {}).get("AgentMuse")
        if isinstance(tc, dict):
            tc["freeClaimed"] = views.get("freeClaimed")
            tc["bookedTotal"] = views.get("bookedTotal")
            tc["bookedOf_user"] = views.get("bookedOf_user")
            tc["lastReadBlock"] = BLOCK
            tc["lastReadWib"] = NOTE
            tc["runNote2201"] = ("Run 2201: freeClaimed %s/888, bookedOf(user)=FREE_OSK utuh; "
                                 "minted-by-user, DIAM." % views.get("freeClaimed"))
            updated.append("track_c:AgentMuse")
        continue
    if name == "GoldVein":
        continue  # handled below (sold out -> remove)
    if key is None or key not in contracts:
        continue
    e = contracts[key]
    if not isinstance(e, dict):
        continue
    prev_block = e.get("lastReadBlock")
    prev_ts = e.get("totalSupply")
    iv = interval_min(prev_block if isinstance(prev_block, int) else None)
    new_ts = views.get("totalSupply")
    if new_ts is None:
        new_ts = views.get("totalMinted")
    minted = None
    rate = None
    if isinstance(new_ts, int) and isinstance(prev_ts, int):
        minted = new_ts - prev_ts
        rate = round(minted / iv, 4) if iv else None
    # store fresh reads
    if isinstance(new_ts, int):
        e["totalSupply"] = new_ts
    for f in ("freeMinted", "freeClaimed", "freeRemaining", "FREE_SUPPLY", "FREE_CAP",
              "FREE_MAX", "MAX_SUPPLY", "mintOpen", "saleOpen", "freeAvailable_user",
              "freeClaimed_user", "balanceOf_user", "freeLeft", "freeCount"):
        if views.get(f) is not None:
            e[f] = views[f]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOTE
    # velocity
    prev_rate = e.get("previousRatePerMin")
    vel = False
    if minted is not None and rate is not None:
        if prev_rate not in (None, 0) and minted >= 20 and rate >= 1.5 * prev_rate:
            vel = True
        e["previousTotalSupply"] = prev_ts
        e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(iv, 1)
        e["currentRatePerMin"] = rate
        e["previousRatePerMin"] = rate
        e["velocityLegPasses"] = vel
    # free % where a free cap is known
    fc = e.get("freeClaimed") if isinstance(e.get("freeClaimed"), int) else e.get("freeMinted")
    cap = None
    for cf in ("FREE_SUPPLY", "FREE_CAP", "FREE_MAX"):
        if isinstance(e.get(cf), int):
            cap = e[cf]
            break
    if isinstance(fc, int) and cap:
        e["freePctVerified"] = round(100.0 * fc / cap, 2)
    e["runNote" + RUN] = ("Run 2201 (blok %d): totalSupply %s (prev %s, +%s, %.3f/mnt, "
                          "velocity %s); free %s; bal_user %s; DIAM."
                          % (BLOCK, new_ts, prev_ts,
                             minted if minted is not None else "?",
                             rate if rate is not None else -1,
                             "LOLOS" if vel else "GAGAL",
                             e.get("freePctVerified", "?"),
                             views.get("balanceOf_user")))
    updated.append(key)

# ---- status syncs (already-reported changes; no re-report) ----
contracts["OBFG"]["status"] = "age-excluded-2026-11-13"
contracts["Oliver Agents"]["status"] = "age-excluded-2026-11-13"
contracts["Oliver Agents"]["runNote" + RUN] = (
    "Run 2201: totalSupply 1026, freeMinted 976/1000 = 97,6%, freeRemaining 24. "
    "Age-excluded SUDAH dilaporkan hot leg 21:00 WIB 13 Nov (first-seen 12 Nov ~13:01 WIB, "
    "umur >=31,9 jam). TIDAK dilaporkan ulang. DIAM.")
contracts["OBFG"]["runNote" + RUN] = (
    "Run 2201 (blok %d): 707/1230 = 57,5%% (+3). Age-excluded SUDAH dilaporkan hot leg "
    "20:02 WIB 13 Nov (saleStart 12 Nov 20:01 WIB). TIDAK dilaporkan ulang. DIAM." % BLOCK)

# Agentx: crossed 70% this run but user declined override ('biarkan saja') -> log only
ax = contracts.get("Agentx", {})
ax["runNote" + RUN] = ("Run 2201 (blok %d): freeMinted 778/1111 = 70,03%% (crossed >70%%), "
    "slot terbuka, mintOpen 1, deadline umur 23:11 WIB. TIDAK dilaporkan/ditawarkan ulang: "
    "user sudah menolak override ('biarkan saja'); gate website tetap gagal. DIAM." % BLOCK)
ax["freePctVerified"] = 70.03
ax["totalSupply"] = verify["reads"]["Agentx"]["views"].get("totalMinted")
ax["lastReadBlock"] = BLOCK
ax["lastReadWib"] = NOTE

# ---- track_c: GoldVein sold out -> report once (in final message) + remove ----
tc = snap.setdefault("track_c", {})
gv = tc.pop("GoldVein", None)
snap["runNote2201_sellout_goldvein"] = (
    "Run 2201: GoldVein free lane SOLD OUT 500/500 (21:31: 497/500; bacaan segar blok %d "
    "freeSold 500, freeClaimed(user)=0 - slot user TIDAK terpakai). Dilaporkan sekali run ini "
    "sebagai perubahan track-C + dihapus dari track_c. Gate tetap gagal (dilaporkan 2031); "
    "tidak pernah di-mint." % BLOCK)
# RESUME-BC1B age-excluded -> report once + remove
bc = tc.pop("RESUME-BC1B", None)
snap["runNote2201_ageexcl_bc1b"] = (
    "Run 2201: RESUME-BC1B AGE-EXCLUDED (saleStart on-chain 1794488398 = 12 Nov 19:59:58 WIB; "
    "umur ~26 jam >24 jam saat run ini; freeCount 470/3000 = 15,7%%, slot terbuka, gate tetap "
    "gagal). Dilaporkan sekali run ini sebagai perubahan track-C + dihapus dari track_c.")
# VISION (0x5f76cAb7-5a-hit): age-excluded per run-note keputusan sebelumnya, silent
if "0x5f76cAb7-5a-hit" in tc:
    tc.pop("0x5f76cAb7-5a-hit")
    snap["runNote2201_ageexcl_vision"] = (
        "Run 2201: VISION 0x5f76cAb7 AGE-EXCLUDED + dihapus dari track_c (dicek 9 Nov, 182 share "
        "terbit; umur >=4 hari). Tidak pernah dilaporkan sebagai lead -> DIAM (keputusan "
        "age-exclusion sudah dicatat run sebelumnya; entri lingering dibersihkan).")

# ---- new entries ----
contracts["MORFO"] = {
    "address": "0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",
    "name": "MORFO TRADE CARD", "symbol": "MORFOCARD", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-13",
    "totalSupply": None, "totalMinted": 415, "MAX_SUPPLY": 25000,
    "mintOpen": 1, "freePctVerified": None,
    "firstSeenWib": "2026-11-13T11:16:48+07:00",
    "firstSeenSource": "Sourcify feed (hot-leg-seen) + Boltbook ZH front page run 2201",
    "launchNote": ("Deployed/verified 13 Nov 11:16:05 WIB (Sourcify verifiedAt 2026-11-13T04:16:05Z, "
                   "exact_match, 45 fns) -> umur <24 jam (dibatasi deployment hari ini); "
                   "launch time tepat UNVERIFIED (tanpa mintStart view)."),
    "baselineNote": ("EARLY LEAD dilaporkan sekali run 2201: agent-shaped (registry bytes "
                     "0x60B9...022F di bytecode + Sourcify exact_match), totalMinted 415/25000, "
                     "mintOpen 1, mint() lolos Agent-ID wallet (Boltbook). Free% UNVERIFIED "
                     "(tanpa free view); umur launch tepat UNVERIFIED; website UNVERIFIED; "
                     "X UNVERIFIED. Bukan strong lead/kandidat. Tidak pernah preview/mint."),
    "lastReadBlock": BLOCK, "lastReadWib": NOTE,
    "runNote" + RUN: "Run 2201: EARLY LEAD baru (lihat baselineNote). DIAM setelah laporan sekali.",
}
contracts["ME24"] = {
    "address": "0x391a13af7819e36a84f16754c133ca39d08d273d",
    "name": "Gear Machine", "symbol": "ME24", "kind": "ERC721",
    "status": "watchlist-only-age-unverified-2026-11-13",
    "totalSupply": 132, "MAX_SUPPLY": 1706, "mintOpen": 1,
    "price": 80000000000000, "freePctVerified": None,
    "firstSeenWib": "2026-11-13T11:22:52+07:00",
    "firstSeenSource": "Boltbook (hot-leg-seen) + Boltbook EN/ZH front page run 2201",
    "launchNote": ("Umur launch UNVERIFIED: tanpa mintStart view; Sourcify verifiedAt "
                   "2026-11-10T06:08:25Z (kontrak sudah ada sejak 10 Nov) -> first mint BUKAN "
                   "di run ini; first-seen job 13 Nov 11:22 WIB. Bukan early lead (first mints "
                   "tidak terverifikasi di run ini). Clone family 7.398 byte (saudara "
                   "PX24/SKRR/ME30/CY24)."),
    "baselineNote": ("Watchlist-only run 2201: agent-shaped (registry bytes + Sourcify "
                     "exact_match), totalSupply 132/1706 = 7,7%%, mintOpen 1, mint(1)@0 lolos "
                     "static call (Boltbook). Free% UNVERIFIED (tanpa free view); website "
                     "UNVERIFIED; X UNVERIFIED. Tidak dilaporkan (bukan early lead)."),
    "lastReadBlock": BLOCK, "lastReadWib": NOTE,
    "runNote" + RUN: "Run 2201: pertama dibaca job ini (132/1706). Watchlist-only, DIAM.",
}
contracts["FERO"] = {
    "address": "0x76FB0A89c8618A1d7Cf3E2123ae43E5aeb36f2F4",
    "name": "Ferrous Relics", "symbol": "FERO", "kind": "ERC721",
    "status": "watchlist-only-upcoming-2026-11-13",
    "totalSupply": None, "totalMinted": 0, "MAX_SUPPLY": 3333,
    "market": "0x8a1982a51E74817a7dB7B8F980C970ED1f5A4074",
    "website": "https://ferrous-relics.github.io/ferrous-relics/",
    "windowWib": "2026-11-13 23:00 -> 2026-11-16 23:00",
    "launchNote": ("BELUM BUKA saat run 2201 (totalMinted 0; window buka 13 Nov 23:00 WIB). "
                   "Free lane 1 Agent ID: 333 box, 1/wallet - BUTUH posting link situs di X + "
                   "paste URL post di situs untuk permit EIP-712 (social-gated). Free lane 2 X: "
                   "200 box. Paid 2.800 box @ 0,001 BNB. Sourcify exact_match (NFT + market)."),
    "baselineNote": ("UPCOMING watchlist item run 2201 (Boltbook ACCESSION LEDGER). Bukan kandidat "
                     "(belum launch). Website TERVERIFIKASI (site GitHub Pages + post Boltbook "
                     "mencetak kontrak persis). Pantau saat window buka 23:00 WIB."),
    "lastReadBlock": BLOCK, "lastReadWib": NOTE,
    "runNote" + RUN: "Run 2201: upcoming (buka 23:00 WIB). Dilaporkan sekali sebagai upcoming.",
}
for name, addr, first_seen, pct, extra in [
    ("Vorn Agent", "0x8c2f7bec2d7b31d9c706d25eb4d008f0754ce255", "2026-11-09T20:03:03+07:00", "98,0% (4.900/5.000)", "Boltbook: first detected 2026-11-06 17:17 WIB."),
    ("Sable Agent", "0x23d356173ff227d5bf6d622f4a8907f208871d76", "2026-11-07T13:09:38+07:00", "98,0% (4.901/5.001)", "Gelombang 'X Agent' 6.799 byte (saudara Vorn/Ember/Frie/Thor/Vexa/Cobalt/Zora)."),
    ("Ember Agent", "0x4241866a617161c73762dfc693a3597439b9d1e5", "2026-11-12T12:57:55+07:00", "95,8% (4.790/5.000)", "Gelombang 'X Agent' 6.799 byte; +4.000 sejak bacaan 790 (Boltbook)."),
    ("Frie Agent", "0x6fdb4d8e9868540dafadc9b23ce9bbdbcd1e8da5", "2026-11-12T17:45:59+07:00", "99,0% (9.901/10.001)", "Gelombang 'X Agent' 6.799 byte."),
    ("Azimuth Spillway", "0x85f1522401aaf9e3f19e7f79cc4b2fb3969a8f77", "2026-11-11T00:56:03+07:00", "22,2% (240/1.081)", "Clone family 7.407 byte; price() 0,00008 BNB."),
    ("SnakeAgent", "0xf7c1ba2286cee6eef10cc264664168fd015127b1", "2026-11-11T06:25:59+07:00", "22,6% (1.006/4.444 freeMinted)", "freeMinted 1.006, totalSupply 1.019; registry bytes TRUE."),
]:
    key = name
    contracts[key] = {
        "address": addr, "name": name, "kind": "ERC721",
        "status": "age-excluded-2026-11-13",
        "launchNote": ("AGE-EXCLUDED run 2201: first-seen job %s -> umur >=24 jam (launch <= "
                       "first-seen). %s" % (first_seen, extra)),
        "baselineNote": ("Dicatat age-excluded run 2201 (triase Boltbook). Free %s. Tidak pernah "
                         "dilaporkan sebagai lead -> DIAM." % pct),
        "lastReadBlock": BLOCK, "lastReadWib": NOTE,
        "runNote" + RUN: "Run 2201: age-excluded (first-seen %s). DIAM." % first_seen,
    }
contracts["Wraith"] = {
    "address": "0x4a318eb842c8c95876e895258bc70d0bee767def",
    "name": "Wraith", "symbol": "WRAITH", "kind": "ERC721",
    "status": "checked-not-agent-shaped-2026-11-13",
    "totalMinted": 2574, "MAX_SUPPLY": 5555,
    "launchNote": ("Boltbook post 22:09 WIB 13 Nov klaim 2.311/5.555; bacaan run 2201 totalMinted "
                   "2.574. First-seen job 11 Nov 04:29 WIB (sourcify-feed)."),
    "baselineNote": ("BUKAN agent-shaped: registry bytes TIDAK ada di bytecode (6.570 byte); "
                     "tanpa free view/quote/agent (S1=S2=False, hot leg 11 Nov). Bukan early "
                     "lead, bukan kandidat. Tidak dilaporkan."),
    "lastReadBlock": BLOCK, "lastReadWib": NOTE,
    "runNote" + RUN: "Run 2201: checked-not-agent-shaped. DIAM.",
}
# pending claim re-check
pc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(pc, dict):
    pc["launched"] = verify["reads"]["BinanceAI-mint"]["views"].get("launched")
    pc["tokenClaimed_user"] = verify["reads"]["BinanceAI-mint"]["views"].get("tokenClaimed_user")
    pc["isRefundPhase"] = verify["reads"]["BinanceAI-mint"]["views"].get("isRefundPhase")
    pc["failed"] = verify["reads"]["BinanceAI-mint"]["views"].get("failed")
    pc["refundClaimed_user"] = verify["reads"]["BinanceAI-mint"]["views"].get("refundClaimed_user")
    pc["lastReadWib"] = NOTE
    pc["runNote" + RUN] = ("Run 2201: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, "
                           "failed()=1, refundClaimed(user)=0 - refund phase TIDAK BERUBAH "
                           "(sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM.")

snap["last_run_wib"] = NOTE
snap["last_run_note"] = ("Run 2201: 56/56 verify OK (blok %d); 1 early lead baru (MORFO); 1 upcoming "
    "(FERO, buka 23:00 WIB); 2 perubahan track-C dilaporkan sekali (GoldVein sold out, BC1B "
    "age-excluded); 6 age-excluded baru dicatat diam (Vorn/Sable/Ember/Frie/Azimuth/SnakeAgent); "
    "Agentx 70,03%% tapi user tolak override -> diam; scan leg fast-fail (Ankr 401), watermark "
    "TETAP 132512564; 0 kandidat, 0 strong lead baru, 0 auto-mint." % BLOCK)
snap["runNote2201"] = snap["last_run_note"]
snap["runNote2201_scan"] = ("Run 2201 scan leg FAST-FAIL: pre-flight ankr_getLogs 50 blok gagal "
    "HTTP 401 Unauthorized dalam 11,7 dtk (head 133375786); watermark TETAP 132512564; 5c dilewati; "
    "lanjut route lain.")
snap["runNote2201_triage"] = ("Run 2201 triase Boltbook (10 kontrak): MORFO early lead; ME24 watchlist-only "
    "(verifiedAt 10 Nov, first mints bukan di run ini); Vorn/Sable/Ember/Frie/Azimuth/SnakeAgent "
    "age-excluded (first-seen 7-12 Nov); Wraith bukan agent-shaped; FERO upcoming (totalMinted 0). "
    "Sourcify feed 20 kontrak: 5 baru vs seen (0x2379 tax-token, 4x owner/recover-only) - 0 S1/S2/early.")
snap["runNote2201_discovery"] = ("Run 2201 discovery: Boltbook EN+ZH dibaca langsung (25+ post); sweep EN+ZH 0 proyek "
    "baru (Golden Agents/RIGBYPASS/STAMP PASS/UFO/VISION/NEBULA/NOVRA/JOLT/HOPKIN/BN Agent File "
    "semua dikenal/sudah ditangani); bridge 3 entri, 0 baru vs snapshot; route 6 dilewati run ini "
    "(Boltbook+Sourcify+on-chain sudah menutup item segar; retry run berikut bila perlu).")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("UPDATED:", len(updated), "entries")
print("updated keys:", updated)
print("track_c keys now:", sorted(snap.get("track_c", {}).keys())[:8], "... total", len(snap.get("track_c", {})))
print("contracts total:", len(snap.get("contracts", {})))
