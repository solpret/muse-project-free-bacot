#!/usr/bin/env python3
"""Main run 2026-11-02 23:01 WIB: apply route-1 reread to snapshot."""
import json, os, shutil
BASE = os.path.expanduser("~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-2301-read.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-2301.bak.json")
READ_BLOCK = read["block"]  # 131269524, block time 2026-11-02T23:02:45+07:00
READ_WIB = "2026-11-02T23:02:45+07:00"
INTERVAL = 30.48  # minutes, 22:32:16 -> 23:02:45 (read-block times)
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
    old_fc = v.get("freeClaimed"); new_fc = r.get("freeClaimed()")
    old_fs = v.get("FREE_SUPPLY"); new_fs = r.get("FREE_SUPPLY()")
    old_fm = v.get("freeMinted"); new_fm = r.get("freeMinted()")
    old_fl = v.get("freeLeft"); new_fl = r.get("freeLeft()")
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
        v["velocityNote"] = f"Run 23:01 WIB (read block {READ_BLOCK}): {minted:+d} tokens in ~{INTERVAL} min = {cur_rate}/min, ratio vs prior {prev_rate} -> velocity leg {'PASSES' if passes else 'FAILS'}."
    if new_fc is not None: v["freeClaimed"] = new_fc
    if new_fs is not None: v["FREE_SUPPLY"] = new_fs
    if new_fm is not None: v["freeMinted"] = new_fm
    if new_fl is not None: v["freeLeft"] = new_fl
    fc = new_fc if new_fc is not None else old_fc
    fs = new_fs if new_fs is not None else old_fs
    fm = new_fm if new_fm is not None else old_fm
    fl = new_fl if new_fl is not None else old_fl
    pct = None
    if fc is not None and fs: pct = round(100 * fc / fs, 2)
    elif fm is not None and fl is not None and (fm + fl): pct = round(100 * fm / (fm + fl), 2)
    elif fm is not None and fs: pct = round(100 * fm / fs, 2)
    if pct is not None:
        old_pct = v.get("freePctVerified")
        v["freePctVerified"] = pct
        if old_pct is not None and old_pct < 50 <= pct:
            crossed.append((name, old_pct, pct))
    v["userMintedBy"] = r.get("mintedBy(address)")
    v["userFreeUsed"] = r.get("freeUsed(address)")
    v["userBalance"] = r.get("balanceOf(address)")
    v["lastReadBlock"] = READ_BLOCK
    v["lastReadWib"] = READ_WIB
print("velocity_pass:", velocity_pass)
print("crossed_50:", crossed)
# Nanobee velocity-pass annotation (already gate-blocked strong lead; NOT a candidate, NO re-report)
nb = snap["contracts"].get("Nanobee")
if nb:
    nb["velocityLegNote2301"] = "Run 23:01 WIB: velocity leg PASSES (+68 in 30.48 min = 2.231/min vs prior 0.034) and free 83.64% + age verified + slot open, BUT website-only gate already FAILED (17:01 WIB, methods A-G) and X unverified -> still NOT a candidate, NO preview/mint, NO re-report (already reported as gate-blocked strong lead)."
# Track-B pending pollen update (read extras)
snap["pending_claims"]["hive-pollen"]["lastReadBlock"] = READ_BLOCK
snap["pending_claims"]["hive-pollen"]["lastReadWib"] = READ_WIB
snap["pending_claims"]["hive-pollen"]["pollenAgents"] = 7812
snap["pending_claims"]["hive-pollen"]["launched"] = 0
snap["pending_claims"]["hive-pollen"]["phase"] = 1
snap["pending_claims"]["hive-pollen"]["note"] = "Re-checked 23:01 run: launched still 0, phase 1, pollenAgents 7812 (was 7808 in 22:31 run), paidSold 1045 unchanged - still PENDING, never previewed while not open. Next triggers: launched flips true (-> auto-claim check), refund/failed phase (-> report once + remove)."
# FU track-C lead (reported once this run as LEAD + blocking reason; NEVER previewed/minted)
snap.setdefault("track_c", {})["FU-hongbao"] = {
    "sale": "0xCfEfbf03fA11d2Bf441c3fD12C92e6390D109381",
    "token": "0xaBE87e980873d96af3D51251029C33E6e43FD843",
    "name": "FU hongbao",
    "site": "https://fuhongbao.com",
    "status": "lead-reported-2026-11-02-blocked-no-mint",
    "saleShape": "S1-LIKE, DISCLOSED AS UNVERIFIED-ABI: mint(uint256) selector 0xa0712d68 in bytecode + site docs; quote(address,uint256) selector 0x8f79306e verified on-chain quote(user,1)=0; free views FREE_CAP()=1000 + freeGiven()=85 verified on-chain (915 free remaining); registry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exactly on-chain + registry bytes in bytecode. Sourcify 404 (ABI UNVERIFIED) - shape NOT verified via Sourcify ABI, unlike strict 5a feed test.",
    "freePool": "FREE_CAP 1000, freeGiven 85 -> 915 remaining (read block 131269524 area; site /api/stats freeRemaining 916 at opened 85, timing difference only)",
    "opened": 86, "mintOpen": 1, "paused": 0, "price_paid": "0.002 BNB",
    "userSlot": "quote(user,1)=0 on-chain; site /api/verify eligible true, quotaRemaining 20, freeAvailable true, priceNext 0 (site claims only, quote is the on-chain proof)",
    "launchNote": "First Opened event verified on-chain: block 131243407, 2026-11-02 19:46:49 WIB (Ankr address-filtered Opened topic walk, 0 events in 129000000-131243406, index 1 = first envelope); age ~3.3h at 23:06 WIB, VERIFIED <=48h.",
    "websiteGate": "PASSES (method G): https://fuhongbao.com/skill.md prints both contracts exactly + registry + treasury; Boltbook posts (biawak.ai, tealive.ai) link the site. X account: site /api/stats x=null; X optional under website-only gate, absence not a blocker.",
    "discussion": "Boltbook posts 2026-11-02: biawak.ai (first packet free, 46/7,777 note) + tealive.ai (on-chain re-check: treasury EOA 99.72% supply, 49 packets opened at post time). Recorded as discussion evidence, not as a buy recommendation.",
    "blockers": "NO MINT this run: (1) Sourcify ABI unverified - strict sale-shape via verified ABI not met (DROID precedent); (2) Binance audit NOT run for FU in this run; (3) preview balance-match condition cannot be pre-satisfied: reward is a RANDOM tier (8,888,888-777,777,777 FU), not a fixed tokensPerShare/quote tokensOut amount; (4) liquidity risk disclosed: site stats splits treasuryPct 100 / liquidityPct 0, no LP hook verified, treasury EOA holds 99.72% of FU supply per Boltbook re-check - received FU has no verified market. Lead reported once 23:01 run with these blockers; a future mint needs a fresh explicit user decision (or a verified-ABI + audit + preview pass), never silent auto-mint on this record alone.",
    "firstSeenWib": "2026-11-02T23:0x+07:00 (Boltbook front page EN+ZH, main run 23:01 WIB)",
}
# Museai age-excluded
snap.setdefault("excluded", {})["Museai"] = {
    "address": "0xcbf6c4c0d46bd858fd384a484e343cb8cd0c50e5",
    "symbol": "MUSE",
    "track": "A",
    "status": "excluded-age-over-48h-2026-11-02",
    "note": "Boltbook front-page lead 23:01 run (husky.ai AgenticMint tracker: minted tokenIds 4298/4303, value 0). Agent-shape verified: Sourcify ABI (mint + quote + freeAvailable/freeClaimed/freePoolSize/freeUsedBy + AGENT_ID_REGISTRY) + on-chain totalMinted 6001, freeClaimed 5954/7999=74.4%, freeAvailable(user)=2, slot open, priceWei 0.0005 BNB. BUT age EXCLUDES: first Transfer-from-zero block 130404678, 2026-10-29 10:54:07 WIB (Ankr address-filtered walk, 0 logs in 130000000-130399999; Sourcify verifiedAt 2026-10-29T04:02:18Z) -> ~4d12h at run, OVER 48h, not sold out. NOT reported as a lead/candidate, NOT previewed/minted.",
}
snap["timestamp_wib"] = READ_WIB
snap["note"] = "Main run 23:01 WIB: route-1 read block 131269524 + Sourcify feed (50 items, 4 newest shape-checked, none pass S1/S2) + Boltbook EN+ZH (FU lead + Museai age-excluded + Mars/MOLT/DINO triaged, no other new lead) + sweep EN+ZH (old/generic only) + route 6 (Odaily EN, no Agent-ID item; PANews/DappBay skipped, reasons in run log) + scan triage PENDING at snapshot write (scan 2301 still running; triage applied in a follow-up step if it yields first-seen). ONE new track-C lead reported once: FU hongbao (lead + blockers, NO mint/preview). Velocity pass: Nanobee only (already gate-blocked, no change report). No new candidate, no new strong lead, no new early lead, no track-B opening. Pollen still pending."
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot updated, contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]), "excluded:", len(snap["excluded"]))
