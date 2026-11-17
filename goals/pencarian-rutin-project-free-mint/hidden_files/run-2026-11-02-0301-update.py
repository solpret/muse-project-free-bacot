#!/usr/bin/env python3
"""Run 0301 snapshot update. Applies route-1 re-reads + track-C/B re-reads.
Scan/seen/state updates are applied separately after scan triage."""
import json, os
base = os.path.expanduser("~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
snap = json.load(open(base + "onchain-snapshot.json"))
read = json.load(open(base + "run-2026-11-02-0301-read.json"))
extra = json.load(open(base + "run-2026-11-02-0301-read-extra.json"))
cilok = json.load(open(base + "run-2026-11-02-0301-cilok-baseline.json"))
verify = json.load(open(base + "run-2026-11-02-0301-sourcify-verify.json"))
def gi(d, n):
    v = d.get(n, {}) if isinstance(d, dict) else {}
    return v.get("int") if isinstance(v, dict) else v

# (name, total, free, fsup, interval, block, wib, note-template)
updates = [
    ("HIVE Agents", 756, None, 1000, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Bubblebruin", 802, 801, 7777, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Zapcourier", 332, 332, 712, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Mothwraith", 299, 298, 869, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Cryonyx", 324, 323, 809, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Cathodex", 353, 353, 763, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Malabao", 318, 318, 844, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Slimelings", 1529, None, None, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Voltabyte", 222, 222, 925, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Saturnin", 181, 181, 838, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Kirinova", 304, 304, 711, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Ghostbloom", 218, 218, 942, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Junepup", 237, 237, 724, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Vorpry", 217, None, None, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Gourdwick", 304, 304, 868, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Kitsunaru", 286, 286, 865, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Nightsable", 266, 266, 794, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Lensorb", 272, 272, 776, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Nimaluo", 281, 280, 828, 27.53, 131110914, "2026-11-02T03:12:51+07:00"),
    ("Agents NormiePunks", 470, None, None, 28.37, 131111115, "2026-11-02T03:14:22+07:00"),
    ("Medusine", 212, 212, 868, 28.37, 131111115, "2026-11-02T03:14:22+07:00"),
    ("Hotpotsage", 195, 195, 784, 28.37, 131111115, "2026-11-02T03:14:22+07:00"),
    ("Mummyrelic", 178, 178, 785, 28.37, 131111115, "2026-11-02T03:14:22+07:00"),
    ("Ravenhex", 193, 193, 925, 28.37, 131111115, "2026-11-02T03:14:22+07:00"),
    ("Orbitmarshal", 168, 168, 831, 28.37, 131111115, "2026-11-02T03:14:22+07:00"),
    ("Lighthouse Agent", 351, None, 483, 28.37, 131111115, "2026-11-02T03:14:22+07:00"),
]
for name, total, free, fsup, interval, block, wib in updates:
    c = snap["contracts"][name]
    prev_total = c.get("totalSupply")
    prev_rate = c.get("currentRatePerMin")
    minted = total - prev_total if prev_total is not None else None
    rate = round(minted / interval, 3) if minted is not None else None
    ratio = round(rate / prev_rate, 2) if (rate is not None and prev_rate) else None
    passes = bool(rate is not None and prev_rate and rate >= 1.5 * prev_rate and minted >= 20)
    c["previousTotalSupply"] = prev_total
    c["totalSupply"] = total
    if free is not None:
        c["freeClaimed"] = free
    if fsup is not None:
        c["FREE_SUPPLY"] = fsup
    if free is not None and fsup:
        c["freePctVerified"] = round(100.0 * free / fsup, 2)
    if name == "HIVE Agents":
        c["freePctInference"] = round(100.0 * total / 1000, 2)
    c["mintedInInterval"] = minted
    c["intervalMinutes"] = interval
    c["previousRatePerMin"] = prev_rate
    c["currentRatePerMin"] = rate
    c["velocityNote"] = (f"Run 03:01 WIB: +{minted} tokens in ~{interval} min = {rate}/min, "
        f"ratio vs prior {prev_rate} = {ratio}x, so the velocity leg {'PASSES' if passes else 'still FAILS'}. Stored as new baseline.")
    c["velocityLegPasses"] = passes
    c["velocityVerified"] = passes
    c["lastReadBlock"] = block
    c["lastReadWib"] = wib
    if name == "Slimelings":
        c["mintedCount"] = gi(read["Slimelings"], "mintedCount()")
        c["freeCount"] = gi(read["Slimelings"], "freeCount()")
    if name == "Vorpry":
        c["totalMinted"] = gi(read["Vorpry"], "totalMinted()")
        c["openLeft"] = gi(read["Vorpry"], "openLeft()")
    print(name, "minted", minted, "rate", rate, "ratio", ratio, "passes", passes)
# Mirror Pair
mp = snap["contracts"]["Mirror Pair"]
mp["lastReadBlock"] = 131110914
mp["lastReadWib"] = "2026-11-02T03:12:51+07:00"
mp["velocityNote"] = "Run 03:01 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
# Cilok Cats: still totalMinted 1, no new mint
cc = snap["contracts"]["Cilok Cats: White Paw Genesis"]
cc["previousTotalSupply"] = cc.get("totalSupply")
cc["totalSupply"] = 1
cc["totalMinted"] = cilok["totalMinted()"]
cc["freeMinted"] = cilok["freeMinted()"]
cc["freeClaimed"] = cilok["freeMinted()"]
cc["freePctVerified"] = 0.1
cc["mintedInInterval"] = 0
cc["currentRatePerMin"] = 0.0
cc["velocityNote"] = "Run 03:01 WIB: still totalMinted 1 (was 1) at block 131111397 - no new mint since the 03:12 WIB baseline; still the sole owner mint, velocity not computable. Stored as new baseline."
cc["velocityLegPasses"] = False
cc["lastReadBlock"] = cilok["block"]
cc["lastReadWib"] = "2026-11-02T03:16:00+07:00"
# New early leads: Gearpixel + Skelebop (Sourcify feed, first mints verified in-run)
for nm, addr, vkey, vat in [
    ("Gearpixel", "0x9560703c474Ed34df8415Aa715991D15B9b3c47e", "0x9560703c474Ed34df8415Aa715991D15B9b3c47e", "2026-11-01T20:15:13Z"),
    ("Skelebop", "0xaB5183443e2B82333A4b173e55bb38cCe7c46b01", "0xaB5183443e2B82333A4b173e55bb38cCe7c46b01", "2026-11-01T20:15:06Z"),
]:
    v = verify[vkey]
    fm = v["first_mints"]
    snap["contracts"][nm] = {
        "address": addr,
        "status": "early-lead-reported-2026-11-02",
        "name": v["name"],
        "symbol": v["symbol"],
        "kind": "ERC721",
        "totalSupply": v["totalSupply()"],
        "freeClaimed": v["freeClaimed()"],
        "FREE_SUPPLY": v["FREE_SUPPLY()"],
        "MAX_SUPPLY": v["MAX_SUPPLY()"],
        "freePctVerified": round(100.0 * v["freeClaimed()"] / v["FREE_SUPPLY()"], 2),
        "mintOpen": True,
        "userMintedBy": 0,
        "userFreeUsed": 0,
        "userBalance": 0,
        "userSlotNote": "Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
        "firstSeenBlock": fm["first_block"],
        "scanMints": fm["count"],
        "scanMinters": fm["distinct_minters"],
        "lastReadBlock": verify["head"],
        "lastReadWib": "2026-11-02T03:17:00+07:00",
        "xVerified": False,
        "velocityVerified": False,
        "launchNote": (f"First mint verified on-chain: first Transfer-from-zero at block {fm['first_block']}, {fm['first_wib']} "
            f"(Ankr getLogs address-filtered from block 131060000; {fm['count']} logs = totalSupply {v['totalSupply()']} at verify time, so all mints ever are in range); "
            f"no project-stated launch time found; Sourcify verifiedAt {vat} is verification time, NOT launch time. "
            "First-seen by this job in run 03:01 WIB via Sourcify feed."),
        "baselineNote": ("EARLY lead reported once 2026-11-02 run 03:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI "
            "(mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry "
            "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % far below 50%; X unverified; velocity not yet computable (first baseline stored this run)."),
        "previousTotalSupply": None,
        "mintedInInterval": None,
        "intervalMinutes": None,
        "currentRatePerMin": None,
        "previousRatePerMin": None,
        "velocityNote": "Run 03:01 WIB: first baseline stored; velocity not yet computable (never passed on velocity alone).",
        "velocityLegPasses": False,
    }
    print("added early lead", nm)
# Track B pending
snap["pending_claims"]["binanceai.fun"]["totalShares_last"] = 3104
snap["pending_claims"]["binanceai.fun"]["lastCheckBlock"] = 131110914
snap["pending_claims"]["binanceai.fun"]["lastCheckWib"] = "2026-11-02T03:12:51+07:00"
snap["pending_claims"]["hive-pollen"]["pollenAgents"] = 7549
snap["pending_claims"]["hive-pollen"]["pollenSlice_raw"] = "13246787653993906477679"
snap["pending_claims"]["hive-pollen"]["pollenSlice_estimate"] = "~13,247 HIVE at 18 decimals (shrinks as more agents join; agentInfo claimable reads 0 pre-launch, so the slice is an estimate, not a fixed claimable)"
snap["pending_claims"]["hive-pollen"]["lastCheckBlock"] = 131110914
snap["pending_claims"]["hive-pollen"]["lastCheckWib"] = "2026-11-02T03:12:51+07:00"
# Track C
tc = snap["track_c"]
tc["BNBbaby"].update({"sharesMinted": 9349, "freeMinted": 9038, "paidShares": 311,
    "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["DOG"].update({"sharesMinted": 1090, "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["BNBPIG"].update({"sharesMinted": 4922, "freeMinted": 4750, "paidShares": 172,
    "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["SAMBARIO"].update({"cardsSold": 201, "freeCardsRemaining": 3132,
    "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["a7Be"].update({"sharesMinted": 421, "freeSharesMinted": 408,
    "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["NIUBI"].update({"sharesMinted": 60, "freeMinted": 59,
    "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["QILIN"].update({"cardsSold": 4831, "freeCardsRemaining": 216,
    "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["SAFU Tower"].update({"freeClaimed_total": 4444,
    "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["零元购"].update({"soldFree": 76, "totalSold": 77,
    "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["JUBAO"].update({"freeClaimed": 15, "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["ZCMAO"].update({"freeClaimed": 16, "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["JINLONG"].update({"freeClaimed": 15, "lastCheckBlock": 131110914, "lastCheckWib": "2026-11-02T03:12:51+07:00"})
tc["JINLI"].update({"freeClaimed": 2255, "freeRemaining": 745,
    "lastCheckBlock": 131111115, "lastCheckWib": "2026-11-02T03:14:22+07:00"})
tc["BIAO"].update({"freeClaimed": 0, "freeRemaining": 4444,
    "lastCheckBlock": 131111115, "lastCheckWib": "2026-11-02T03:14:22+07:00"})
tc["兕"].update({"soldFree": 66, "freeRemaining": 2934,
    "lastCheckBlock": 131111115, "lastCheckWib": "2026-11-02T03:14:22+07:00"})
snap["timestamp_wib"] = "2026-11-02T03:01:00+07:00"
json.dump(snap, open(base + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]))
