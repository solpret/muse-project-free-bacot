#!/usr/bin/env python3
"""Main run 2026-11-02 20:31 WIB: apply route-1 reread + promotions to snapshot.
Run AFTER scan triage; scan triage additions are merged by the triage step
before this runs, or added separately afterwards. This script is idempotent
for the reread fields (same read block / values)."""
import json, os, shutil, datetime
BASE = os.path.expanduser("~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-2031-read.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-2031.bak.json")
READ_BLOCK = read["block"]  # 131249418, block time 2026-11-02T20:31:54+07:00
READ_WIB = "2026-11-02T20:31:54+07:00"
INTERVAL = 28.85  # minutes, 20:03 -> 20:31:54 (snapshot lastRead 20:03 for reread set)
velocity_pass = []
crossed = []
for name, v in snap["contracts"].items():
    if name not in read:
        continue
    if str(v.get("status", "")).startswith("minted-by-user"):
        continue
    r = read[name]
    old_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply()")
    old_fc = v.get("freeClaimed")
    new_fc = r.get("freeClaimed()")
    old_fs = v.get("FREE_SUPPLY")
    new_fs = r.get("FREE_SUPPLY()")
    if new_ts is not None:
        minted = (new_ts - old_ts) if old_ts is not None else 0
        prev_rate = v.get("currentRatePerMin", v.get("previousRatePerMin"))
        cur_rate = round(minted / INTERVAL, 3) if minted else 0.0
        passes = bool(prev_rate and minted >= 20 and cur_rate >= 1.5 * prev_rate)
        if passes:
            velocity_pass.append((name, minted, cur_rate, prev_rate))
        v["previousTotalSupply"] = old_ts
        v["totalSupply"] = new_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["previousRatePerMin"] = prev_rate
        v["currentRatePerMin"] = cur_rate
        v["velocityLegPasses"] = passes
        v["velocityNote"] = f"Run 20:31 WIB (read block {READ_BLOCK}): {minted:+d} tokens in ~{INTERVAL} min = {cur_rate}/min, ratio vs prior {prev_rate} -> velocity leg {'PASSES' if passes else 'FAILS'}."
    if new_fc is not None:
        v["freeClaimed"] = new_fc
    if new_fs is not None:
        v["FREE_SUPPLY"] = new_fs
    if new_fc is not None and new_fs:
        pct = round(100 * new_fc / new_fs, 2)
        old_pct = v.get("freePctVerified")
        v["freePctVerified"] = pct
        if old_pct is not None and old_pct < 50 <= pct:
            crossed.append((name, old_pct, pct))
    v["userMintedBy"] = r.get("mintedBy(address)")
    v["userFreeUsed"] = r.get("freeUsed(address)")
    v["userBalance"] = r.get("balanceOf(address)")
    v["lastReadBlock"] = READ_BLOCK
    v["lastReadWib"] = READ_WIB

# Nimaluo: promotion to strong lead, gate FAILED -> gate-blocked, never previewed/minted
n = snap["contracts"]["Nimaluo"]
n["status"] = "strong-lead-gate-blocked-2026-11-02"
n["freePctVerified"] = 50.0
n["gateStatus"] = "FAILED-website-only-2026-11-02-2031"
n["gateNote"] = ("Strong-lead legs met 20:31 WIB: age VERIFIED <=48h (first mint 2026-11-02 01:11 WIB, "
    "age ~19.3h), free 414/828 = 50.0% verified, user slot open (mintedBy 0, freeUsed 0, quote(user,1)=0, "
    "freeFor(user,1)=1). Velocity FAILS (+1 in interval). MANDATORY WEBSITE GATE FAILED after methods "
    "(A) raw contract-address search (no site link), (B) Boltbook agata.ai wave post (contract only, no site link), "
    "(C) Sourcify ABI (no URL; contractURI is pure, no link), (D) same-family site patterns (search found no Nimaluo site), "
    "(E) deployer-group owner() 0xa054275580c6d1c9077543907ac5798f2494ecce (group of 10 in reread incl. Malabao, "
    "Nightsable, Mothwraith - factory-wave pattern, NOT exempt), (F) twitterapi.io not applicable (no handle found to confirm), "
    "(G) project-name search + site-document check (no site found). X account optional, absence not a blocker. "
    "DO NOT preview, DO NOT mint under strong-lead direct mint until a verified website is found.")
n["quoteUser1"] = 0
n["freeForUser1"] = 1

# Citadel Agent: NEW early lead (Sourcify route; scan cross-check handled in triage log)
snap["contracts"]["Citadel Agent"] = {
    "address": "0x25536eB0E05FCF40EfA7798B0A871E653E34F3B2",
    "status": "early-lead-reported-2026-11-02",
    "name": "Citadel Agent",
    "symbol": "CITADEL",
    "kind": "ERC721",
    "totalMinted": 92,
    "FREE_SUPPLY": 381,
    "MAX_SUPPLY": 1527,
    "freePctVerified": None,
    "mintOpen": True,
    "userMintedBy": 0,
    "userBalance": 0,
    "userSlotNote": "Slot appears open by mintedBy(user)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
    "firstSeenBlock": 131248756,
    "firstMintWib": "2026-11-02T20:26:56+07:00",
    "scanMints": 89,
    "scanMinters": 31,
    "lastReadBlock": READ_BLOCK,
    "lastReadWib": READ_WIB,
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": ("First mint verified on-chain: first Transfer-from-zero at block 131248756, 2026-11-02 20:26:56 WIB "
        "(Ankr address-filtered getLogs 131230000-131249600, paged; 0 logs in 131200000-131230000; 89 logs, 31 distinct minters). "
        "Sourcify verifiedAt 2026-11-02T13:29:05Z is verification time, NOT launch time."),
    "baselineNote": ("EARLY lead reported once 2026-11-02 run 20:31 WIB. Never auto-minted/previewed. Agent-shape verified: "
        "Sourcify ABI (mint + agentIdRegistry + FREE_SUPPLY + MAX_SUPPLY + totalMinted + mintedBy) and agentIdRegistry() "
        "returns registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain, registry bytes in bytecode. "
        "Free % UNVERIFIED (no freeClaimed/freeMinted view responds; totalMinted/MAX = 6.0% and totalMinted/FREE_SUPPLY = 24.1% "
        "are NOT free %). Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety."),
    "supplyView": "totalMinted",
}

# Falls Agent: NEW early lead from on-chain scan (verified individually below in run log)
snap["contracts"]["Falls Agent"] = {
    "address": "0xf371A2E6d029304625e7FD27D76a5DE5DD3be204",
    "status": "early-lead-reported-2026-11-02",
    "name": "Falls Agent",
    "symbol": "FALLS",
    "kind": "ERC721",
    "totalMinted": 173,
    "FREE_SUPPLY": 308,
    "MAX_SUPPLY": 1234,
    "freePctVerified": None,
    "mintOpen": True,
    "userMintedBy": 0,
    "userBalance": 0,
    "userSlotNote": "Slot appears open by mintedBy(user)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
    "firstSeenBlock": 131246705,
    "firstMintWib": "2026-11-02T20:11:33+07:00",
    "scanMints": 113,
    "scanMinters": 35,
    "lastReadBlock": READ_BLOCK,
    "lastReadWib": READ_WIB,
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": ("First mint verified on-chain: first Transfer-from-zero at block 131246705, 2026-11-02 20:11:33 WIB "
        "(Ankr address-filtered getLogs: 50 logs in 131200000-131247417, 63 logs in scan window; scan first_block 131247456 "
        "is NOT the first mint - earlier mints predate the scan window). Sourcify verifiedAt 2026-11-02T12:12:41Z is "
        "verification time, NOT launch time. Owner 0x369d834566b0d553743ad8ff2dec352c8362364c (same as Onyx Agent)."),
    "baselineNote": ("EARLY lead reported once 2026-11-02 run 20:31 WIB. Never auto-minted/previewed. Agent-shape verified: "
        "Sourcify verified ABI (mint + agentIdRegistry + FREE_SUPPLY + MAX_SUPPLY + totalMinted + mintedBy) and agentIdRegistry() "
        "returns registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain, registry bytes in bytecode. "
        "Free % UNVERIFIED (no freeClaimed/freeMinted view responds; totalMinted/MAX = 14.0% and totalMinted/FREE_SUPPLY = 56.2% "
        "are NOT free %). Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety."),
    "supplyView": "totalMinted",
}

# Track B pending claims
pc = snap["pending_claims"]["binanceai.fun"]
# Change already reported once by hot-leg run 20:24 (confirmed by this run's independent read).
# Per body, a pending claim entering refund/failed phase is reported once and removed from tracking:
# removal is done here; the once-report belongs to the hot-leg 20:24 run, so this run does NOT re-report it.
del snap["pending_claims"]["binanceai.fun"]
pollen = snap["pending_claims"]["hive-pollen"]
pollen["launched"] = False
pollen["phase"] = 1
pollen["pollenAgents"] = 7793
pollen["paidSold"] = 1045
pollen["lastReadBlock"] = READ_BLOCK
pollen["lastReadWib"] = READ_WIB

snap["timestamp_wib"] = "2026-11-02T20:31:54+07:00"
snap["note"] = ("Main run 20:31 WIB complete: route-1 read block 131249418 + Sourcify feed (cached 13:03 UTC, "
    "cross-checked against hot-leg 20:29 feed/shape) + Boltbook EN/ZH + sweep + route 6 + scan (see scan log). "
    "Nimaluo promoted to strong lead then GATE-BLOCKED (website-only gate failed, no preview/mint). "
    "Citadel Agent new early lead. binanceai.fun pending claim REMOVED after refund/failed confirmation "
    "(change first reported by hot-leg 20:24 run, not re-reported here).")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("VELOCITY_PASS", velocity_pass)
print("CROSSED>=50", crossed)
print("contracts now", len(snap["contracts"]))
print("pending_claims now", list(snap["pending_claims"].keys()))
