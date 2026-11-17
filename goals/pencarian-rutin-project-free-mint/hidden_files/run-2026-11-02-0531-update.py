#!/usr/bin/env python3
"""Run 0531 snapshot update. Read-only inputs; writes onchain-snapshot.json."""
import json, copy
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
def gi(d, n):
    v = d.get(n, {}) if isinstance(d, dict) else {}
    return v.get("int") if isinstance(v, dict) else v
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
main = json.load(open(f"{HF}/run-2026-11-02-0531-read.json"))
extra = json.load(open(f"{HF}/run-2026-11-02-0531-read-extra.json"))
cilok = json.load(open(f"{HF}/run-2026-11-02-0531-cilok.json"))
verify = json.load(open(f"{HF}/run-2026-11-02-0531-verify.json"))
MAIN_INT, EXTRA_INT, CILOK_INT = 32.23, 33.43, 33.72
B_MAIN, B_EXTRA, B_CILOK = main["block"], extra["block"], cilok["block"]
W_MAIN, W_EXTRA, W_CILOK = "2026-11-02T05:35:58+07:00", "2026-11-02T05:37:45+07:00", "2026-11-02T05:38:05+07:00"

def upd(name, new_total, new_free, free_cap, interval, block, readwib, total_key="totalSupply"):
    c = snap["contracts"][name]
    old_total = c.get("totalSupply") if c.get("totalSupply") is not None else c.get("totalMinted")
    old_rate = c.get("currentRatePerMin")
    minted = new_total - old_total
    rate = round(minted / interval, 3) if interval else None
    passes = bool(old_rate is not None and minted >= 20 and rate >= 1.5 * old_rate)
    ratio = round(rate / old_rate, 2) if old_rate else None
    c["previousTotalSupply"] = old_total
    c[total_key] = new_total
    if new_free is not None: c["freeClaimed"] = new_free
    if free_cap and new_free is not None: c["freePctVerified"] = round(new_free / free_cap * 100, 2)
    c["mintedInInterval"] = minted; c["intervalMinutes"] = interval
    c["previousRatePerMin"] = old_rate; c["currentRatePerMin"] = rate
    c["velocityLegPasses"] = passes
    if old_rate:
        c["velocityNote"] = (f"Run 05:31 WIB: +{minted} tokens in ~{interval} min = {rate}/min, ratio vs prior {old_rate} = {ratio}x, "
                             f"so the velocity leg {'PASSES' if passes else 'still FAILS'}. Stored as new baseline.")
    else:
        c["velocityNote"] = f"Run 05:31 WIB: +{minted} tokens in ~{interval} min = {rate}/min - first comparable rate, so the velocity leg does NOT pass. Stored as new baseline."
    c["lastReadBlock"] = block; c["lastReadWib"] = readwib
    return c

# HIVE (inference)
h = snap["contracts"]["HIVE Agents"]; old = h["totalSupply"]; new = gi(main["HIVE"], "totalSupply()")
minted = new - old; rate = round(minted / MAIN_INT, 3)
h["previousTotalSupply"] = old; h["totalSupply"] = new; h["mintedInInterval"] = minted
h["intervalMinutes"] = MAIN_INT; h["previousRatePerMin"] = h["currentRatePerMin"]; h["currentRatePerMin"] = rate
h["velocityLegPasses"] = False; h["freePctInference"] = round(new / 1000 * 100, 1)
h["velocityNote"] = f"Run 05:31 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {h['previousRatePerMin']} = {round(rate / h['previousRatePerMin'], 2)}x, so the velocity leg still FAILS. Stored as new baseline."
h["lastReadBlock"] = B_MAIN; h["lastReadWib"] = W_MAIN

main_map = [("Bubblebruin", 7777), ("Zapcourier", 712), ("Mothwraith", 869), ("Cryonyx", 809),
            ("Cathodex", 763), ("Malabao", 844), ("Voltabyte", 925), ("Saturnin", 838),
            ("Kirinova", 711), ("Ghostbloom", 942), ("Junepup", 724), ("Gourdwick", 868),
            ("Kitsunaru", 865), ("Nightsable", 794), ("Lensorb", 776), ("Nimaluo", 828),
            ("Orbitty", 884), ("Neonwolfy", 850), ("Sphinxel", 799), ("Witchlet", 929),
            ("Venuspi", 840), ("Neonraven", 722), ("Griffinko", 712), ("Tangpinku", 875)]
for nm, cap in main_map:
    upd(nm, gi(main[nm], "totalSupply()"), gi(main[nm], "freeClaimed()"), cap, MAIN_INT, B_MAIN, W_MAIN)
# Slimelings / Vorpry / MirrorPair
sl = snap["contracts"]["Slimelings"]; old = sl["totalSupply"]; new = gi(main["Slimelings"], "totalSupply()")
minted = new - old; rate = round(minted / MAIN_INT, 3); old_rate = sl["currentRatePerMin"]
sl.update({"previousTotalSupply": old, "totalSupply": new, "mintedCount": gi(main["Slimelings"], "mintedCount()"),
           "freeCount": gi(main["Slimelings"], "freeCount()"), "mintedInInterval": minted, "intervalMinutes": MAIN_INT,
           "previousRatePerMin": old_rate, "currentRatePerMin": rate, "velocityLegPasses": False,
           "velocityNote": f"Run 05:31 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {old_rate} = {round(rate / old_rate, 2)}x, so the velocity leg still FAILS. Stored as new baseline.",
           "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN})
vo = snap["contracts"]["Vorpry"]; old = vo["totalSupply"]; new = gi(main["Vorpry"], "totalSupply()")
minted = new - old; rate = round(minted / MAIN_INT, 3); old_rate = vo["currentRatePerMin"]
vo.update({"previousTotalSupply": old, "totalSupply": new, "totalMinted": gi(main["Vorpry"], "totalMinted()"),
           "openLeft": gi(main["Vorpry"], "openLeft()"), "mintedInInterval": minted, "intervalMinutes": MAIN_INT,
           "previousRatePerMin": old_rate, "currentRatePerMin": rate, "velocityLegPasses": False,
           "velocityNote": f"Run 05:31 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {old_rate} = {round(rate / old_rate, 2)}x, so the velocity leg still FAILS. Stored as new baseline.",
           "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN})
mp = snap["contracts"]["Mirror Pair"]
mp.update({"mintedPairs": gi(main["MirrorPair"], "mintedPairs()"), "totalBonds": gi(main["MirrorPair"], "totalBonds()"),
           "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN,
           "velocityNote": "Run 05:31 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."})
# Extra wave
upd("Agents NormiePunks", gi(extra["Agents NormiePunks"], "totalSupply()"), None, None, EXTRA_INT, B_EXTRA, W_EXTRA)
for nm, cap in [("Medusine", 868), ("Hotpotsage", 784), ("Mummyrelic", 785), ("Ravenhex", 925), ("Orbitmarshal", 831)]:
    upd(nm, gi(extra[nm], "totalSupply()"), gi(extra[nm], "freeClaimed()"), cap, EXTRA_INT, B_EXTRA, W_EXTRA)
# Cilok file
c = snap["contracts"]["Cilok Cats: White Paw Genesis"]; old = c.get("totalMinted")
new = gi(cilok["Cilok"], "totalMinted()"); minted = new - old; rate = round(minted / CILOK_INT, 3) if CILOK_INT else 0
c.update({"previousTotalSupply": old, "totalMinted": new, "freeMinted": gi(cilok["Cilok"], "freeMinted()"),
          "mintedInInterval": minted, "intervalMinutes": CILOK_INT, "previousRatePerMin": c.get("currentRatePerMin"),
          "currentRatePerMin": rate, "velocityLegPasses": False,
          "velocityNote": f"Run 05:31 WIB: +{minted} tokens in ~{CILOK_INT} min = {rate}/min, no new mint; velocity leg still FAILS. Stored as new baseline.",
          "lastReadBlock": B_CILOK, "lastReadWib": W_CILOK})
upd("Gearpixel", gi(cilok["Gearpixel"], "totalSupply()"), gi(cilok["Gearpixel"], "freeClaimed()"), 832, CILOK_INT, B_CILOK, W_CILOK)
upd("Skelebop", gi(cilok["Skelebop"], "totalSupply()"), gi(cilok["Skelebop"], "freeClaimed()"), 902, CILOK_INT, B_CILOK, W_CILOK)
# NULLSECTOR (verify2 values read from stdout: totalSupply 560, block 131131069, 05:44:02 WIB; interval 37.4 vs 0501 verify)
ns = snap["contracts"]["NULLSECTOR"]; old = ns["totalSupply"]; new = 560; minted = new - old; rate = round(minted / 37.4, 3); old_rate = ns["currentRatePerMin"]
ns.update({"previousTotalSupply": old, "totalSupply": new, "mintedInInterval": minted, "intervalMinutes": 37.4,
           "previousRatePerMin": old_rate, "currentRatePerMin": rate, "velocityLegPasses": False,
           "velocityNote": f"Run 05:31 WIB: +{minted} tokens in ~37.4 min = {rate}/min, ratio vs prior {old_rate} = {round(rate / old_rate, 2)}x, so the velocity leg still FAILS. Stored as new baseline.",
           "lastReadBlock": 131131069, "lastReadWib": "2026-11-02T05:44:02+07:00"})
# Pixcade: free pool exhausted -> REMOVE
pix = snap["contracts"].pop("Pixcade", None)
# New early leads
snap["contracts"]["Onimaru"] = {
    "address": "0xD1D3b730b154838b7B5F0c072dE7bA66FFBbe72b", "status": "early-lead-reported-2026-11-02",
    "name": "Onimaru", "symbol": "ONIM", "kind": "ERC721", "totalMinted": 2, "freeMinted": 2,
    "FREE_CAP": 3000, "MAX_SUPPLY": 4000, "freePctVerified": 0.07, "freeOn": True,
    "price_paid_lane": "0.0005 BNB", "registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "userMintedBy": 0, "userBalance": 0, "walletInfo_user": [0, 0, 1, 1, 10],
    "userSlotNote": "Slot open by read: mintedBy(user)=0, balance 0 - NOT preview-verified (early leads are never previewed). quote(address,1) returned [0,1] (ambiguous shape, not used as slot proof).",
    "firstSeenBlock": 131130494, "scanMints": 2, "scanMinters": 2,
    "lastReadBlock": verify["head"], "lastReadWib": "2026-11-02T05:44:00+07:00",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131130494, 2026-11-02 05:39:43 WIB (Ankr getLogs address-filtered from block 131060000; 2 logs = totalMinted 2, so all mints ever are in range); no project-stated launch time found; Sourcify verifiedAt 2026-11-01T22:35:42Z (verification time, NOT launch time). First-seen by this job in run 05:31 WIB via Sourcify feed.",
    "baselineNote": "EARLY lead reported once 2026-11-02 run 05:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeMinted + FREE_CAP) and registry() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 0.07, far below 50%; X unverified; velocity not yet computable.",
    "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None,
    "currentRatePerMin": None, "previousRatePerMin": None, "velocityLegPasses": False,
    "velocityNote": "Run 05:31 WIB: first baseline stored (totalMinted 2); velocity not yet computable."}
snap["contracts"]["Rootlinks"] = {
    "address": "0x25F6DF83D43496583BC7190f02E68A15C3E3bB25", "status": "early-lead-reported-2026-11-02",
    "name": "Rootlinks", "symbol": "RLNK", "kind": "ERC721", "totalMinted": 1, "freeMinted": 1,
    "FREE_CAP": 1000, "PAID_CAP": 2805, "MAX_SUPPLY": 5555, "freePctVerified": 0.1, "mintOpen": True,
    "mintStart": 1793572508, "mintStartWib": "2026-11-02T05:35:08+07:00", "mintEnd": 1793831708,
    "price_paid_lane": "0.003 BNB", "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "userBalance": 0,
    "userSlotNote": "Slot open by read: balance 0, paidMinted 0, free lane mintFree() open - NOT preview-verified (early leads are never previewed).",
    "firstSeenBlock": 131130464, "scanMints": 1, "scanMinters": 1,
    "lastReadBlock": verify["head"], "lastReadWib": "2026-11-02T05:44:00+07:00",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131130464, 2026-11-02 05:39:30 WIB (Ankr getLogs address-filtered from block 131060000; 1 log = totalMinted 1, so all mints ever are in range); mintStart() on-chain 2026-11-02 05:35:08 WIB corroborates a launch-minutes window; Sourcify verifiedAt 2026-11-01T22:34:27Z (verification time, NOT launch time). First-seen by this job in run 05:31 WIB via Sourcify feed.",
    "baselineNote": "EARLY lead reported once 2026-11-02 run 05:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (no-arg mintFree() + freeMinted + FREE_CAP + agentIdRegistry) and agentIdRegistry() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 0.1, far below 50%; X unverified; velocity not yet computable.",
    "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None,
    "currentRatePerMin": None, "previousRatePerMin": None, "velocityLegPasses": False,
    "velocityNote": "Run 05:31 WIB: first baseline stored (totalMinted 1); velocity not yet computable."}
# Track C updates
tc = snap["track_c"]
tc["BNBbaby"].update({"sharesMinted": gi(main["BNBbaby"], "sharesMinted()"), "freeMinted": gi(main["BNBbaby"], "freeMinted()"), "paidShares": gi(main["BNBbaby"], "paidShares()")})
tc["DOG"].update({"sharesMinted": gi(main["DOG"], "sharesMinted()")})
tc["QILIN"].update({"cardsSold": gi(main["QILIN"], "cardsSold()"), "freeCardsRemaining": gi(main["QILIN"], "freeCardsRemaining()"), "cardsRemaining": gi(main["QILIN"], "cardsRemaining()"), "freeGiven": gi(main["QILIN"], "freeGiven()")})
tc["SAMBARIO"].update({"cardsSold": gi(main["SAMBARIO"], "cardsSold()"), "freeCardsRemaining": gi(main["SAMBARIO"], "freeCardsRemaining()"), "freeGiven": gi(main["SAMBARIO"], "freeGiven()")})
tc["a7Be"].update({"sharesMinted": gi(main["a7Be"], "sharesMinted()"), "freeSharesMinted": gi(main["a7Be"], "freeSharesMinted()")})
tc["零元购"].update({"soldFree": gi(main["ZeroYuanGou"], "soldFree()"), "soldPaid": gi(main["ZeroYuanGou"], "soldPaid()"), "totalSold": gi(main["ZeroYuanGou"], "totalSold()")})
tc["BIAO"].update({"freeClaimed": gi(extra["BIAO"], "freeClaimed()")})
tc["兕"].update({"soldFree": gi(extra["XI"], "soldFree()"), "freeRemaining": 3000 - gi(extra["XI"], "soldFree()")})
tc["JUBAO"].update({"freeClaimed": gi(main["JUBAO"], "freeClaimed()")})
tc["ZCMAO"].update({"freeClaimed": gi(main["ZCMAO"], "freeClaimed()")})
tc["JINLONG"].update({"freeClaimed": gi(main["JINLONG"], "freeClaimed()")})
# Pending claims (unchanged)
snap["pending_claims"]["binanceai.fun"].update({"launched": False, "totalShares": gi(main["TrackB_MINT"], "totalShares()")})
snap["pending_claims"]["hive-pollen"].update({"launched": False, "pollenAgents": gi(main["Pollen_MINT"], "pollenAgents()"), "paidSold": gi(main["Pollen_MINT"], "paidSold()")})
snap["timestamp_wib"] = "2026-11-02T05:31:00+07:00"
snap["note"] = ("Run 05:31 WIB: contracts = 40 (39 previous - Pixcade removed: free pool exhausted 1500/1500, reported once; + Onimaru + Rootlinks added as EARLY leads, reported once). "
                "No track-A candidate passes all criteria; no new strong lead; no new track-C lead/candidate; pending claims unchanged. "
                "Velocity passes recorded (no promotion: % below 50% and/or X unverified): Neonraven, Orbitty, Neonwolfy, Gearpixel, Skelebop.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "| Pixcade removed:", pix is not None)
for nm in ("Neonraven", "Orbitty", "Neonwolfy", "Gearpixel", "Skelebop", "Kirinova", "Zapcourier", "Cathodex"):
    c = snap["contracts"][nm]; print(nm, c.get("totalSupply"), c.get("freePctVerified"), "velPass", c.get("velocityLegPasses"), c.get("velocityNote"))
