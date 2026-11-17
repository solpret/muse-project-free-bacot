#!/usr/bin/env python3
"""Main run 2026-11-02 21:31 WIB: apply route-1 reread + promotions to snapshot.
Run AFTER scan triage data is ready; scan-triage additions for the 21:01
cluster are included here (they were verified in this run). Idempotent for
reread fields (same read block / values)."""
import json, os, shutil
BASE = os.path.expanduser("~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-2131-read.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-2131.bak.json")
READ_BLOCK = read["block"]  # 131257481, block time 2026-11-02T21:32:23+07:00
READ_WIB = "2026-11-02T21:32:23+07:00"
INTERVAL = 60.48  # minutes, 20:31:54 -> 21:32:23 (21:01 main run left no snapshot update)
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
    old_fm = v.get("freeMinted")
    new_fm = r.get("freeMinted()")
    old_fl = v.get("freeLeft")
    new_fl = r.get("freeLeft()")
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
        v["velocityNote"] = f"Run 21:31 WIB (read block {READ_BLOCK}): {minted:+d} tokens in ~{INTERVAL} min = {cur_rate}/min, ratio vs prior {prev_rate} -> velocity leg {'PASSES' if passes else 'FAILS'}."
    if new_fc is not None:
        v["freeClaimed"] = new_fc
    if new_fs is not None:
        v["FREE_SUPPLY"] = new_fs
    if new_fm is not None:
        v["freeMinted"] = new_fm
    if new_fl is not None:
        v["freeLeft"] = new_fl
    # free %: freeClaimed/FREE_SUPPLY, else freeMinted/(freeMinted+freeLeft),
    # else freeMinted/FREE_SUPPLY (AZET-style, no freeClaimed view).
    fc = new_fc if new_fc is not None else old_fc
    fs = new_fs if new_fs is not None else old_fs
    fm = new_fm if new_fm is not None else old_fm
    fl = new_fl if new_fl is not None else old_fl
    pct = None
    if fc is not None and fs:
        pct = round(100 * fc / fs, 2)
    elif fm is not None and fl is not None and (fm + fl):
        pct = round(100 * fm / (fm + fl), 2)
    elif fm is not None and fs:
        pct = round(100 * fm / fs, 2)
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
print("crossed:", crossed)

GATE_NOTE_TMPL = ("Strong-lead legs met 21:31 WIB run: {legs}. "
    "MANDATORY WEBSITE GATE FAILED after methods (A) raw contract-address search (no site link), "
    "(B) Boltbook front pages EN+ZH (no mention, no link), (C) Sourcify/on-chain metadata "
    "(contractURI is a fully on-chain data URI, no external URL; single-contract Sourcify path used by "
    "this job is /v2/contract/56/<address>, the plural /v2/contracts/56/<address> path returns Cannot GET), "
    "(D) same-family site patterns (search found no project site), (E) deployer-group owner() {owner} "
    "(factory-wave pattern, NOT exempt), (F) twitterapi.io not applicable (no handle found to confirm), "
    "(G) project-name search + site-document check (no site found; same-name matches are not linkage). "
    "DappBay category-AI search also found no listing (absence proves nothing; gate fails on (A)-(G)). "
    "X account optional, absence not a blocker. DO NOT preview, DO NOT mint under strong-lead direct mint "
    "until a verified website is found.")

# Kitsunaru: promotion to strong lead, gate FAILED
k = snap["contracts"]["Kitsunaru"]
k["status"] = "strong-lead-gate-blocked-2026-11-02"
k["gateStatus"] = "FAILED-website-only-2026-11-02-2131"
k["gateNote"] = GATE_NOTE_TMPL.format(
    legs="age VERIFIED <=48h (first mint 2026-11-02 01:10:56 WIB, age ~20.4h), free 434/865 = 50.17% verified, "
         "user slot open (mintedBy 0, freeUsed 0, quote(user,1)=0, freeFor(user,1)=1, balance 0); velocity FAILS (+4 in interval)",
    owner="0xa054275580c6d1c9077543907ac5798f2494ecce (group of 10 in this run's reread incl. Malabao, Nightsable, Mothwraith)")

# Gargrowl: promotion to strong lead, gate FAILED
g = snap["contracts"]["Gargrowl"]
g["status"] = "strong-lead-gate-blocked-2026-11-02"
g["gateStatus"] = "FAILED-website-only-2026-11-02-2131"
g["gateNote"] = GATE_NOTE_TMPL.format(
    legs="age VERIFIED <=48h (first mint 2026-11-02 16:24:41 WIB, age ~5.1h), free 1271/1950 = 65.18% verified, "
         "user slot open (mintedBy 0, freeUsed 0, quote(user,1)=0, freeFor(user,1)=1, balance 0); velocity PASSES (+624 in interval, 10.317/min, 16.5x prior 0.624)",
    owner="0xd76d5918fb337667b22fe37ae2055b5542cf8dc9 (group of 38 in this run's reread)")

CLUSTER_OWNER = "0xecc3b1db6baff284957d81f5afd5a3441dcafaff"
CLUSTER_GATE = ("Strong-lead legs met 21:31 WIB run (verified from the 21:01 scan triage + fresh reads in this run): "
    "age VERIFIED <=48h (first mint {first}, age under 1h), free {free} verified, user slot open "
    "(freeMintedByWallet(user)=0, balance 0, remainingFreeSupply {rem} > 0, freeLimitPerWallet 1). "
    "MANDATORY WEBSITE GATE FAILED after methods (A) raw contract-address search (no site link), "
    "(B) Boltbook front pages EN+ZH (no mention, no link), (C) Sourcify/on-chain metadata (contractURI is a "
    "fully on-chain data URI, no external URL), (D) same-family site patterns (search found no project site), "
    "(E) deployer-group owner() 0xecc3b1db6baff284957d81f5afd5a3441dcafaff (10-contract wave incl. all cluster "
    "contracts below, factory-wave pattern, NOT exempt), (F) twitterapi.io not applicable (no handle found to "
    "confirm), (G) project-name search + site-document check (no site found). DappBay search found no listing "
    "(absence proves nothing; gate fails on (A)-(G)). X account optional, absence not a blocker. "
    "DO NOT preview, DO NOT mint under strong-lead direct mint until a verified website is found.")
CLUSTER = [
    ("Chain Rascals", "0x5606C2d70e390dd0ec0B0C3079d567063faD415C", "RASC", 131253058, "2026-11-02T20:59:12+07:00", 23, 60, 88, 28),
    ("AI Gremlins", "0x1DfC6d367d107921CEB93cd7f7FC7f50d553FA55", "GREML", 131253126, "2026-11-02T20:59:43+07:00", 22, 57, 77, 20),
    ("Byte Punks", "0xf7f329477603d6Df2E89bdef41f82Aa122c14A4f", "BPUNK", 131252690, "2026-11-02T20:56:26+07:00", 17, 55, 77, 22),
    ("Bot Cats", "0x961F7999F616EE70252A6aFf711584B9cdd9404c", "BCATS", 131252750, "2026-11-02T20:56:53+07:00", 12, 44, 88, 44),
    ("Neural Frogs", "0xcdeF985C3B7179880b78DB8DD3e266eC97420f5C", "NFRG", 131252870, "2026-11-02T20:57:47+07:00", 11, 40, 77, 37),
]
for name, addr, sym, fb, fwib, sm, tfm, fa, rem in CLUSTER:
    pct = round(100 * tfm / fa, 2)
    snap["contracts"][name] = {
        "address": addr, "status": "strong-lead-gate-blocked-2026-11-02",
        "name": name, "symbol": sym, "kind": "ERC721",
        "totalFreeMinted": tfm, "freeAllocation": fa, "remainingFreeSupply": rem,
        "freePctVerified": pct, "mintOpen": True,
        "userFreeMintedByWallet": 0, "userBalance": 0,
        "userSlotNote": "Slot open by read: freeMintedByWallet(user)=0, balance 0, remainingFreeSupply > 0, freeLimitPerWallet 1 - NOT preview-verified (gate-blocked strong leads are never previewed).",
        "firstSeenBlock": fb, "firstMintWib": fwib, "scanMints": sm,
        "lastReadBlock": READ_BLOCK, "lastReadWib": READ_WIB,
        "xVerified": False, "velocityVerified": False,
        "launchNote": f"First mint verified on-chain: first Transfer-from-zero in the 21:01 scan window at block {fb}, {fwib} (scan-window first block; earlier mints before the window not excluded by this read, stated plainly). Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job via the 21:01 on-chain scan, triaged in the 21:31 run (the 21:01 main run left no log/snapshot update).",
        "baselineNote": ("EARLY-to-STRONG promotion in the same run: agent-shape verified by the on-chain scan "
            "(Sourcify verified ABI with mintFree + freeAllocation + freeLimitPerAgentId + freeLimitPerWallet + "
            "freeMintedByAgentId + freeMintedByWallet + remainingFreeSupply + totalFreeMinted, registry bytes in "
            "bytecode) and fresh on-chain reads. Promoted directly to strong lead on all 3 legs, then GATE-BLOCKED "
            "on the website-only gate - never previewed/minted. X unverified (optional, not a blocker)."),
        "gateStatus": "FAILED-website-only-2026-11-02-2131",
        "gateNote": CLUSTER_GATE.format(first=fwib, free=f"{tfm}/{fa} = {pct}%", rem=rem),
        "supplyView": "totalFreeMinted",
    }

EARLY = [
    ("Prompt Dogs", "0x26D47f91a72035778a768Fbc7D6F78949f9e5A2B", "PDOG", 131252818, "2026-11-02T20:57:24+07:00", 11, 44, 100, 56),
    ("Agent Raccoons", "0x3Ff101ca8786A88AfF24674380cd0E811E442797", "RACC", 131252937, "2026-11-02T20:58:17+07:00", 11, 40, 100, 60),
]
for name, addr, sym, fb, fwib, sm, tfm, fa, rem in EARLY:
    pct = round(100 * tfm / fa, 2)
    snap["contracts"][name] = {
        "address": addr, "status": "early-lead-reported-2026-11-02",
        "name": name, "symbol": sym, "kind": "ERC721",
        "totalFreeMinted": tfm, "freeAllocation": fa, "remainingFreeSupply": rem,
        "freePctVerified": pct, "mintOpen": True,
        "userFreeMintedByWallet": 0, "userBalance": 0,
        "userSlotNote": "Slot appears open by read: freeMintedByWallet(user)=0, balance 0, remainingFreeSupply > 0 - NOT preview-verified (early leads are never previewed).",
        "firstSeenBlock": fb, "firstMintWib": fwib, "scanMints": sm,
        "lastReadBlock": READ_BLOCK, "lastReadWib": READ_WIB,
        "xVerified": False, "velocityVerified": False,
        "launchNote": f"First mint verified on-chain: first Transfer-from-zero in the 21:01 scan window at block {fb}, {fwib}. Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job via the 21:01 on-chain scan, triaged in the 21:31 run.",
        "baselineNote": ("EARLY lead reported once 2026-11-02 run 21:31 WIB. Never auto-minted/previewed. Agent-shape verified "
            "by the on-chain scan (Sourcify verified ABI with mintFree + freeAllocation + free views, registry bytes in "
            "bytecode). Free % below 50% (or unverified for candidacy); X unverified; velocity not yet computable. "
            "Gate website NOT yet checked for early leads (gate is checked at promotion)."),
        "supplyView": "totalFreeMinted",
    }

SOLDOUT = [
    ("Pixel Operators", "0x127F979E67383D882181fE6D408f30D954991317", "PXOP", 131253195, "2026-11-02T21:00:14+07:00", 55, 55),
    ("Neural Nomads", "0x0594Be0719F16BD2e30B3b238f4336B0AB891dAd", "NNOM", 131253249, "2026-11-02T21:00:38+07:00", 55, 55),
    ("Genesis Bots", "0xdDF44Ae265172aB3141ecABaA3d823Edd9129581", "GBOT", 131253329, "2026-11-02T21:01:14+07:00", 33, 33),
]
for name, addr, sym, fb, fwib, tfm, fa in SOLDOUT:
    snap.setdefault("excluded", {})[name] = {
        "address": addr, "symbol": sym, "track": "A",
        "status": "excluded-sold-out-at-detection-2026-11-02",
        "note": (f"First-seen via the 21:01 on-chain scan (first block {fb}, {fwib}), triaged in the 21:31 run. "
                 f"At detection the free pool was already exhausted: totalFreeMinted {tfm} = freeAllocation {fa}, "
                 "remainingFreeSupply 0. Same deployer group 0xecc3b1db6baff284957d81f5afd5a3441dcafaff as the "
                 "21:01 cluster. Recorded as sold out at detection, NOT reported as a lead, never previewed/minted."),
    }

# Track B pollen reread
hp = snap["pending_claims"].get("hive-pollen")
if hp:
    hp["launched"] = False
    hp["phase"] = 1
    hp["pollenAgents"] = 7799
    hp["paidSold"] = 1045
    hp["lastReadBlock"] = READ_BLOCK
    hp["lastReadWib"] = READ_WIB

snap["timestamp_wib"] = READ_WIB
snap["note"] = ("Main run 21:31 WIB: route-1 read block 131257481 + Sourcify feed (fresh 21:34 WIB, cross-checked "
    "against hot-leg 21:34 shape-checks) + Boltbook EN/ZH + sweep + route 6 + scan triage (21:01 scan output + "
    "2131 scan). Kitsunaru + Gargrowl promoted to strong lead then GATE-BLOCKED (website-only gate failed, no "
    "preview/mint). 21:01 cluster: 5 promoted to strong lead then GATE-BLOCKED, 2 new early leads, 3 sold out at "
    "detection (excluded, not reported). Pollen track-B still pending. No execution in this run.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot updated, contracts:", len(snap["contracts"]), "excluded:", len(snap.get("excluded", {})))
