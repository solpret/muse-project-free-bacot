#!/usr/bin/env python3
"""Run 0231 snapshot update. Applies route-1 re-reads + track-C/B re-reads.
Scan/seen/state updates are applied separately after scan triage."""
import json, os
base = os.path.expanduser("~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
snap = json.load(open(base + "onchain-snapshot.json"))
read = json.load(open(base + "run-2026-11-02-0231-read.json"))
extra = json.load(open(base + "run-2026-11-02-0231-read-extra.json"))
def gi(d, n):
    v = d.get(n, {}) if isinstance(d, dict) else {}
    return v.get("int") if isinstance(v, dict) else v

# (name, read_key, read_dict, new_total, new_free, free_supply, interval, block, wib, velocity_note)
updates = [
    ("HIVE Agents", "HIVE", read, 755, None, 1000, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +5 tokens in ~38.63 min = 0.129/min, ratio vs prior 0.238 = 0.54x and <20 tokens, so the velocity leg still FAILS (outcome unchanged vs 02:01 - no change report). Stored as new baseline."),
    ("Bubblebruin", "Bubblebruin", read, 800, 799, 7777, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +4 tokens in ~38.63 min = 0.104/min, ratio vs prior 0.119 = 0.87x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Zapcourier", "Zapcourier", read, 327, 327, 712, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +7 tokens in ~38.63 min = 0.181/min, ratio vs prior 0.475 = 0.38x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Mothwraith", "Mothwraith", read, 294, 294, 869, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +8 tokens in ~38.63 min = 0.207/min, ratio vs prior 0.475 = 0.44x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Cryonyx", "Cryonyx", read, 317, 317, 809, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +9 tokens in ~38.63 min = 0.233/min, ratio vs prior 0.534 = 0.44x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Cathodex", "Cathodex", read, 349, 349, 763, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +10 tokens in ~38.63 min = 0.259/min, ratio vs prior 0.802 = 0.32x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Malabao", "Malabao", read, 313, 313, 844, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +6 tokens in ~38.63 min = 0.155/min, ratio vs prior 0.713 = 0.22x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Slimelings", "Slimelings", read, 1480, None, None, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +255 tokens in ~38.63 min = 6.60/min, ratio vs prior 18.85 = 0.35x, so the velocity leg now FAILS again (was passing at 02:01 but never promoted - free % unverified + X unverified). Recorded only: NOT a promotion and NOT a candidate - remains EARLY only, never previewed/minted. Stored as new baseline."),
    ("Voltabyte", "Voltabyte", read, 218, 218, 925, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +14 tokens in ~38.63 min = 0.362/min, ratio vs prior 0.742 = 0.49x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Saturnin", "Saturnin", read, 177, 177, 838, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +12 tokens in ~38.63 min = 0.311/min, ratio vs prior 0.475 = 0.65x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Kirinova", "Kirinova", read, 300, 300, 711, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +36 tokens in ~38.63 min = 0.932/min, ratio vs prior 1.425 = 0.65x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Ghostbloom", "Ghostbloom", read, 213, 213, 942, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +12 tokens in ~38.63 min = 0.311/min, ratio vs prior 0.861 = 0.36x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Junepup", "Junepup", read, 236, 236, 724, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +10 tokens in ~38.63 min = 0.259/min, ratio vs prior 1.009 = 0.26x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Vorpry", "Vorpry", read, 211, None, None, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +9 tokens in ~38.63 min = 0.233/min, ratio vs prior 0.653 = 0.36x, so the velocity leg still FAILS. Stored as new baseline."),
    ("Gourdwick", "Gourdwick", read, 285, 285, 868, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +70 tokens in ~38.63 min = 1.812/min, ratio vs prior 2.371 = 0.76x, so the velocity leg still FAILS (second computable rate). Stored as new baseline."),
    ("Kitsunaru", "Kitsunaru", read, 261, 261, 865, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +67 tokens in ~38.63 min = 1.734/min, ratio vs prior 2.006 = 0.86x, so the velocity leg still FAILS (second computable rate). Stored as new baseline."),
    ("Nightsable", "Nightsable", read, 250, 250, 794, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +67 tokens in ~38.63 min = 1.734/min, ratio vs prior 1.641 = 1.06x, so the velocity leg still FAILS (second computable rate). Stored as new baseline."),
    ("Lensorb", "Lensorb", read, 252, 252, 776, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +67 tokens in ~38.63 min = 1.734/min, ratio vs prior 2.261 = 0.77x, so the velocity leg still FAILS (second computable rate). Stored as new baseline."),
    ("Nimaluo", "Nimaluo", read, 261, 261, 828, 38.63, 131107241, "2026-11-02T02:46:36+07:00",
     "Run 02:31 WIB: +54 tokens in ~38.63 min = 1.398/min, ratio vs prior 1.97 = 0.71x, so the velocity leg still FAILS (second computable rate). Stored as new baseline."),
    ("Agents NormiePunks", "Agents NormiePunks", extra, 362, None, None, 31.62, 131107333, "2026-11-02T02:46:44+07:00",
     "Run 02:31 WIB: +336 tokens in ~31.62 min = 10.626/min; first computable rate (previous rate was null), so the velocity leg is NOT passed on velocity alone. Stored as new baseline."),
    ("Medusine", "Medusine", extra, 141, 141, 868, 31.62, 131107333, "2026-11-02T02:46:44+07:00",
     "Run 02:31 WIB: +113 tokens in ~31.62 min = 3.574/min; first computable rate (previous rate was null), so the velocity leg is NOT passed on velocity alone. Stored as new baseline."),
    ("Hotpotsage", "Hotpotsage", extra, 128, 128, 784, 31.62, 131107333, "2026-11-02T02:46:44+07:00",
     "Run 02:31 WIB: +102 tokens in ~31.62 min = 3.226/min; first computable rate (previous rate was null), so the velocity leg is NOT passed on velocity alone. Stored as new baseline."),
    ("Mummyrelic", "Mummyrelic", extra, 116, 116, 785, 31.62, 131107333, "2026-11-02T02:46:44+07:00",
     "Run 02:31 WIB: +96 tokens in ~31.62 min = 3.036/min; first computable rate (previous rate was null), so the velocity leg is NOT passed on velocity alone. Stored as new baseline."),
    ("Ravenhex", "Ravenhex", extra, 134, 134, 925, 31.62, 131107333, "2026-11-02T02:46:44+07:00",
     "Run 02:31 WIB: +100 tokens in ~31.62 min = 3.163/min; first computable rate (previous rate was null), so the velocity leg is NOT passed on velocity alone. Stored as new baseline."),
    ("Orbitmarshal", "Orbitmarshal", extra, 110, 110, 831, 31.62, 131107333, "2026-11-02T02:46:44+07:00",
     "Run 02:31 WIB: +87 tokens in ~31.62 min = 2.751/min; first computable rate (previous rate was null), so the velocity leg is NOT passed on velocity alone. Stored as new baseline."),
    ("Lighthouse Agent", "Lighthouse Agent", extra, 218, None, 483, 31.62, 131107333, "2026-11-02T02:46:44+07:00",
     "Run 02:31 WIB: +117 totalMinted in ~31.62 min = 3.700/min; first computable rate (previous rate was null), so the velocity leg is NOT passed on velocity alone. Free tier still open (costFor(1)=0, currentPrice()=0). Stored as new baseline."),
]
for name, key, src, total, free, fsup, interval, block, wib, note in updates:
    c = snap["contracts"][name]
    prev_total = c.get("totalSupply")
    prev_rate = c.get("currentRatePerMin")
    minted = total - prev_total if prev_total is not None else None
    rate = round(minted / interval, 3) if minted is not None else None
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
    c["velocityNote"] = note
    c["velocityLegPasses"] = False
    c["velocityVerified"] = False
    c["lastReadBlock"] = block
    c["lastReadWib"] = wib
    if name == "Slimelings":
        c["mintedCount"] = gi(src[key], "mintedCount()")
        c["freeCount"] = gi(src[key], "freeCount()")
    if name == "Vorpry":
        c["totalMinted"] = gi(src[key], "totalMinted()")
        c["openLeft"] = gi(src[key], "openLeft()")
# Mirror Pair: no velocity, pairs unchanged
mp = snap["contracts"]["Mirror Pair"]
mp["lastReadBlock"] = 131107241
mp["lastReadWib"] = "2026-11-02T02:46:36+07:00"
mp["velocityNote"] = "Run 02:31 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
# Track B pending
snap["pending_claims"]["binanceai.fun"]["totalShares_last"] = 3104
snap["pending_claims"]["binanceai.fun"]["lastCheckBlock"] = 131107241
snap["pending_claims"]["binanceai.fun"]["lastCheckWib"] = "2026-11-02T02:46:36+07:00"
snap["pending_claims"]["hive-pollen"]["pollenAgents"] = 7541
snap["pending_claims"]["hive-pollen"]["pollenSlice_raw"] = "13260840737302744994032"
snap["pending_claims"]["hive-pollen"]["pollenSlice_estimate"] = "~13,261 HIVE at 18 decimals (shrinks as more agents join; agentInfo claimable reads 0 pre-launch, so the slice is an estimate, not a fixed claimable)"
snap["pending_claims"]["hive-pollen"]["lastCheckBlock"] = 131107241
snap["pending_claims"]["hive-pollen"]["lastCheckWib"] = "2026-11-02T02:46:36+07:00"
# Track C: update pools + remove RuninAI (sellout already reported by hot leg 02:39 WIB)
tc = snap["track_c"]
tc["BNBbaby"].update({"sharesMinted": 9205, "freeMinted": 8900, "paidShares": 305,
    "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["DOG"].update({"sharesMinted": 1064, "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["BNBPIG"].update({"sharesMinted": 4803, "freeMinted": 4633, "paidShares": 170,
    "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["SAMBARIO"].update({"cardsSold": 200, "freeCardsRemaining": 3133,
    "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["a7Be"].update({"sharesMinted": 417, "freeSharesMinted": 404,
    "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["NIUBI"].update({"sharesMinted": 55, "freeMinted": 54,
    "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["QILIN"].update({"cardsSold": 4802, "freeCardsRemaining": 245,
    "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["SAFU Tower"].update({"freeClaimed_total": 4444,
    "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["零元购"].update({"soldFree": 76, "totalSold": 77,
    "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["JUBAO"].update({"freeClaimed": 15, "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["ZCMAO"].update({"freeClaimed": 16, "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["JINLONG"].update({"freeClaimed": 15, "lastCheckBlock": 131107241, "lastCheckWib": "2026-11-02T02:46:36+07:00"})
tc["JINLI"].update({"freeClaimed": 1945, "freeRemaining": 1055,
    "lastCheckBlock": 131107333, "lastCheckWib": "2026-11-02T02:46:44+07:00"})
tc["BIAO"].update({"freeClaimed": 0, "freeRemaining": 4444,
    "lastCheckBlock": 131107333, "lastCheckWib": "2026-11-02T02:46:44+07:00"})
tc["兕"].update({"soldFree": 61, "freeRemaining": 2939,
    "lastCheckBlock": 131107333, "lastCheckWib": "2026-11-02T02:46:44+07:00"})
removed = tc.pop("RuninAI", None)
print("RuninAI removed:", removed is not None)
snap["timestamp_wib"] = "2026-11-02T02:31:00+07:00"
json.dump(snap, open(base + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]), sorted(snap["track_c"].keys()))
