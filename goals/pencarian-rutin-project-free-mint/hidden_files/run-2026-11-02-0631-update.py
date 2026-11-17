import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
def gi(d, n):
    v = d.get(n, {}) if isinstance(d, dict) else {}
    return v.get("int") if isinstance(v, dict) else v
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
main = json.load(open(f"{HF}/run-2026-11-02-0631-read.json"))
extra = json.load(open(f"{HF}/run-2026-11-02-0631-read-extra.json"))
cilok = json.load(open(f"{HF}/run-2026-11-02-0631-cilok.json"))
v2 = json.load(open(f"{HF}/run-2026-11-02-0631-verify2.json"))
ver = json.load(open(f"{HF}/run-2026-11-02-0631-verify.json"))
v3 = json.load(open(f"{HF}/run-2026-11-02-0631-verify3.json"))
B_MAIN, B_EXTRA, B_CILOK, B_V2, B_VER = main["block"], extra["block"], cilok["block"], v2["block"], ver["block"]
W_MAIN, W_EXTRA, W_CILOK, W_V2, W_VER = "2026-11-02T06:33:20+07:00", "2026-11-02T06:34:24+07:00", "2026-11-02T06:35:01+07:00", "2026-11-02T06:35:04+07:00", "2026-11-02T06:35:42+07:00"
MAIN_INT, EXTRA_INT, CILOK_INT, V2_INT, VER_INT = 22.23, 21.5, 21.68, 19.43, 24.07

def upd(name, new_total, new_free, interval, block, readwib, total_key="totalSupply", free_key="freeClaimed"):
    c = snap["contracts"][name]
    old_total = c.get("totalSupply") if c.get("totalSupply") is not None else c.get("totalMinted")
    old_rate = c.get("currentRatePerMin")
    minted = new_total - old_total
    rate = round(minted / interval, 3) if interval else None
    passes = bool(old_rate and minted >= 20 and rate >= 1.5 * old_rate)
    ratio = round(rate / old_rate, 2) if old_rate else None
    c["previousTotalSupply"] = old_total
    c[total_key] = new_total
    if new_free is not None: c[free_key] = new_free
    cap = c.get("FREE_SUPPLY") or c.get("FREE_CAP")
    if cap and new_free is not None and free_key == "freeClaimed":
        c["freePctVerified"] = round(new_free / cap * 100, 2)
    c["mintedInInterval"] = minted; c["intervalMinutes"] = interval
    c["previousRatePerMin"] = old_rate; c["currentRatePerMin"] = rate
    c["velocityLegPasses"] = passes
    if old_rate:
        c["velocityNote"] = (f"Run 06:31 WIB: +{minted} tokens in ~{interval} min = {rate}/min, ratio vs prior {old_rate} = {ratio}x, "
                             f"so the velocity leg {'PASSES' if passes else 'still FAILS'}. Stored as new baseline.")
    else:
        c["velocityNote"] = f"Run 06:31 WIB: +{minted} tokens in ~{interval} min = {rate}/min - first comparable rate, so the velocity leg does NOT pass. Stored as new baseline."
    c["lastReadBlock"] = block; c["lastReadWib"] = readwib
    return c

mc = json.load(open(f"{HF}/run-2026-11-02-0631-mintedcheck.json"))
B_MC = mc["block"]
MINTED_INFO = {
 "HIVE Agents": ("0xe8f572619f4f45d649ca6a214bdb0e20144f9b2e439d1fa94509aab819b419f9", 131137961, 109476, 808),
 "Cathodex": ("0x76bea3b197e66841306ff462cfae41c5caea57a8f36bb7f3bac54b6637fc7a2f", 131138115, 136128, 421),
 "Kirinova": ("0x789e6bc86219adc0894c38848135ec54541840403dad7ef27e28f97f0bf482fa", 131138215, 136128, 377),
 "Zapcourier": ("0x9c0586c9324af9ac3dd09367582f143d99afb6a99a588e3b0f670bdd03440af6", 131138282, 136128, 387),
}
# The 4 pre-existing strong leads were minted by the separate 06:36-06:44 WIB execution under the
# 2026-11-02 ~06:33 strong-lead direct-mint rule (NOT by this run). Preserve minted-by-user status;
# this run only verifies ownership + receipts and refreshes totals. NEVER re-mint, NEVER re-report.
_h = snap["contracts"]["HIVE Agents"]
_h.update({"previousTotalSupply": _h["totalSupply"], "totalSupply": mc["HIVE"]["totalSupply()"],
           "mintedInInterval": None, "intervalMinutes": None,
           "previousRatePerMin": _h.get("currentRatePerMin"), "currentRatePerMin": None, "velocityLegPasses": False,
           "freePctInference": round(mc["HIVE"]["totalSupply()"] / 1000 * 100, 1),
           "velocityNote": "Run 06:31 WIB: minted-by-user (separate 06:36-06:44 WIB execution); velocity no longer tracked. Fresh totalSupply 809 at mintedcheck block; user slot USED (freeMintedBy 1, balance 1, ownerOf #808 = user wallet, receipt status 1).",
           "status": "minted-by-user-2026-11-02",
           "mintTx": MINTED_INFO["HIVE Agents"][0], "mintBlock": MINTED_INFO["HIVE Agents"][1], "mintGas": MINTED_INFO["HIVE Agents"][2], "mintTokenId": 808,
           "lastReadBlock": B_MC, "lastReadWib": "2026-11-02T06:46:59+07:00"})
for _nm, _mc_key in [("Cathodex", "Cathodex"), ("Kirinova", "Kirinova"), ("Zapcourier", "Zapcourier")]:
    _c = snap["contracts"][_nm]
    _tx, _blk, _gas, _tid = MINTED_INFO[_nm]
    _c.update({"previousTotalSupply": _c["totalSupply"], "totalSupply": mc[_mc_key]["totalSupply()"],
               "freeClaimed": mc[_mc_key]["freeClaimed()"],
               "freePctVerified": round(mc[_mc_key]["freeClaimed()"] / _c["FREE_SUPPLY"] * 100, 2),
               "mintedInInterval": None, "intervalMinutes": None,
               "previousRatePerMin": _c.get("currentRatePerMin"), "currentRatePerMin": None, "velocityLegPasses": False,
               "velocityNote": f"Run 06:31 WIB: minted-by-user (separate 06:36-06:44 WIB execution); velocity no longer tracked. Fresh totalSupply {mc[_mc_key]['totalSupply()']} at mintedcheck block; user slot USED (mintedBy 1, freeUsed 1, balance 1, ownerOf #{_tid} = user wallet, receipt status 1).",
               "status": "minted-by-user-2026-11-02",
               "mintTx": _tx, "mintBlock": _blk, "mintGas": _gas, "mintTokenId": _tid,
               "lastReadBlock": B_MC, "lastReadWib": "2026-11-02T06:46:59+07:00"})
main_map = ["Bubblebruin","Zapcourier","Mothwraith","Cryonyx","Cathodex","Malabao","Voltabyte","Saturnin","Kirinova",
            "Ghostbloom","Junepup","Orbitty","Neonwolfy","Sphinxel","Witchlet","Venuspi","Neonraven","Griffinko","Tangpinku",
            "Gourdwick","Kitsunaru","Nightsable","Lensorb","Nimaluo"]
for nm in main_map:
    upd(nm, gi(main[nm], "totalSupply()"), gi(main[nm], "freeClaimed()"), MAIN_INT, B_MAIN, W_MAIN)
sl = snap["contracts"]["Slimelings"]; old = sl["totalSupply"]; new = gi(main["Slimelings"], "totalSupply()")
minted = new - old; rate = round(minted / MAIN_INT, 3); old_rate = sl["currentRatePerMin"]
sl.update({"previousTotalSupply": old, "totalSupply": new, "mintedCount": gi(main["Slimelings"], "mintedCount()"),
           "freeCount": gi(main["Slimelings"], "freeCount()"), "mintedInInterval": minted, "intervalMinutes": MAIN_INT,
           "previousRatePerMin": old_rate, "currentRatePerMin": rate,
           "velocityLegPasses": bool(old_rate and minted >= 20 and rate >= 1.5 * old_rate),
           "velocityNote": f"Run 06:31 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {old_rate} = {round(rate / old_rate, 2)}x, so the velocity leg still FAILS. Stored as new baseline.",
           "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN})
vo = snap["contracts"]["Vorpry"]; old = vo["totalSupply"]; new = gi(main["Vorpry"], "totalSupply()")
minted = new - old; rate = round(minted / MAIN_INT, 3); old_rate = vo["currentRatePerMin"]
vo.update({"previousTotalSupply": old, "totalSupply": new, "totalMinted": gi(main["Vorpry"], "totalMinted()"),
           "openLeft": gi(main["Vorpry"], "openLeft()"), "mintedInInterval": minted, "intervalMinutes": MAIN_INT,
           "previousRatePerMin": old_rate, "currentRatePerMin": rate, "velocityLegPasses": False,
           "velocityNote": f"Run 06:31 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {old_rate} = 0.0x, so the velocity leg still FAILS. Stored as new baseline.",
           "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN})
mp = snap["contracts"]["Mirror Pair"]
mp.update({"mintedPairs": gi(main["MirrorPair"], "mintedPairs()"), "totalBonds": gi(main["MirrorPair"], "totalBonds()"),
           "velocityNote": "Run 06:31 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable.",
           "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN})
for nm in ["Agents NormiePunks","Medusine","Hotpotsage","Mummyrelic","Ravenhex","Orbitmarshal"]:
    upd(nm, gi(extra[nm], "totalSupply()"), gi(extra[nm], "freeClaimed()"), EXTRA_INT, B_EXTRA, W_EXTRA)
ci = snap["contracts"]["Cilok Cats: White Paw Genesis"]; old = ci["totalMinted"]; new = gi(cilok["Cilok"], "totalMinted()")
ci.update({"previousTotalSupply": old, "totalMinted": new, "freeMinted": gi(cilok["Cilok"], "freeMinted()"),
           "mintedInInterval": new - old, "intervalMinutes": CILOK_INT, "previousRatePerMin": ci["currentRatePerMin"],
           "currentRatePerMin": round((new - old) / CILOK_INT, 3), "velocityLegPasses": False,
           "velocityNote": f"Run 06:31 WIB: +{new - old} tokens in ~{CILOK_INT} min - no new mint; velocity not applicable.",
           "lastReadBlock": B_CILOK, "lastReadWib": W_CILOK})
for nm in ["Gearpixel","Skelebop"]:
    upd(nm, gi(cilok[nm], "totalSupply()"), gi(cilok[nm], "freeClaimed()"), CILOK_INT, B_CILOK, W_CILOK)
for nm, src in [("NULLSECTOR", v2["NULLSECTOR"]), ("Onimaru", v2["Onimaru"]), ("Rootlinks", v2["Rootlinks"])]:
    c = snap["contracts"][nm]
    old = c.get("totalSupply") if c.get("totalSupply") is not None else c.get("totalMinted")
    new = src.get("totalSupply") if src.get("totalSupply") is not None else src.get("totalMinted")
    free = src.get("freeMinted")
    old_rate = c.get("currentRatePerMin")
    minted = new - old; rate = round(minted / V2_INT, 3)
    passes = bool(old_rate and minted >= 20 and rate >= 1.5 * old_rate)
    c["previousTotalSupply"] = old
    if "totalSupply" in src and src["totalSupply"] is not None: c["totalSupply"] = new
    else: c["totalMinted"] = new
    if free is not None: c["freeMinted"] = free
    cap = c.get("FREE_SUPPLY") or c.get("FREE_CAP")
    if cap and free is not None: c["freePctVerified"] = round(free / cap * 100, 2)
    c.update({"mintedInInterval": minted, "intervalMinutes": V2_INT, "previousRatePerMin": old_rate,
              "currentRatePerMin": rate, "velocityLegPasses": passes,
              "velocityNote": f"Run 06:31 WIB: +{minted} tokens in ~{V2_INT} min = {rate}/min, ratio vs prior {old_rate} = {round(rate / old_rate, 2) if old_rate else None}x, so the velocity leg still FAILS. Stored as new baseline.",
              "lastReadBlock": B_V2, "lastReadWib": W_V2})
# BHACK: totalMinted 22 -> 40, free 40/60 = 66.67%; velocity first comparable? previousRate None -> does NOT pass; also +18 < 20
bh = snap["contracts"]["BINANCE HACK"]; old = bh["totalMinted"]; new = ver["BHACK"]["totalMinted()"]
minted = new - old; rate = round(minted / VER_INT, 3)
bh.update({"previousTotalSupply": old, "totalMinted": new, "totalFreeMinted": ver["BHACK"]["totalFreeMinted()"],
           "totalPaidMinted": ver["BHACK"]["totalPaidMinted()"], "freePctVerified": round(ver["BHACK"]["totalFreeMinted()"] / ver["BHACK"]["freeAllocation()"] * 100, 2),
           "mintedInInterval": minted, "intervalMinutes": VER_INT, "previousRatePerMin": bh.get("currentRatePerMin"),
           "currentRatePerMin": rate, "velocityLegPasses": False,
           "velocityNote": f"Run 06:31 WIB: +{minted} tokens in ~{VER_INT} min = {rate}/min - first comparable rate and <20 tokens, so the velocity leg does NOT pass. Stored as new baseline.",
           "status": "strong-lead-promoted-2026-11-02",
           "baselineNote": "PROMOTED to strong lead in run 06:31 WIB (reported once): first mint 2026-11-02 05:56:16 WIB (age <1h, verified via first-mint bound), free 40/60 = 66.67% verified (crossed 50% this run from 36.67% at 06:01 WIB), user slot open (freeMintedByAgentId 0, mintedByAgentId 0, balance 0). X still UNVERIFIED and velocity FAILS (+18 < 20, first comparable rate), so NOT a candidate under the old body. Under the 2026-11-02 ~06:33 strong-lead direct-mint rule (effective next runs, body updated 07:01 WIB), this strong lead is eligible for direct preview+mint in the next run if all safety guards pass. This run performed NO preview/mint (its body predates the rule update).",
           "lastReadBlock": B_VER, "lastReadWib": W_VER})
# VOLC: totalMinted 300 -> 459, free % still UNVERIFIED
vc = snap["contracts"]["Volcano Agent"]; old = vc["totalMinted"]; new = ver["VOLC"]["totalMinted()"]
minted = new - old; rate = round(minted / VER_INT, 3)
vc.update({"previousTotalSupply": old, "totalMinted": new, "mintedInInterval": minted, "intervalMinutes": VER_INT,
           "previousRatePerMin": vc.get("currentRatePerMin"), "currentRatePerMin": rate, "velocityLegPasses": False,
           "velocityNote": f"Run 06:31 WIB: +{minted} tokens in ~{VER_INT} min = {rate}/min - first comparable rate, so the velocity leg does NOT pass. Stored as new baseline.",
           "baselineNote": "EARLY lead reported once 2026-11-02 run 06:01 WIB. Never auto-minted/previewed. Run 06:31 WIB: totalMinted 459 (was 300), FREE_SUPPLY 468, costFor(1) still 0, user slot open (mintedBy 0, balance 0). Free % still UNVERIFIED (no freeClaimed total view; 459/468 NOT used as a %). X unverified. Remains an EARLY lead only.",
           "lastReadBlock": B_VER, "lastReadWib": W_VER})
# New early/strong leads from Sourcify feed verification (verify3)
snap["contracts"]["PIXEL FROGS"] = {
   "address": "0xBd144C91F0bcA43Ee86a47a07488710D33281E8b", "status": "early-lead-reported-2026-11-02",
   "name": "PIXEL FROGS", "symbol": "PFROG", "kind": "ERC721",
   "totalSupply": v3["Bd14"]["totalSupply()"], "freeClaimed": None, "MAX_SUPPLY": 10000,
   "freePctVerified": None, "mintOpen": True,
   "userMintedBy": None, "userFreeUsed": 0, "userBalance": 0,
   "userSlotNote": "Slot open by read: freeClaimed(user)=0, quote(user,1)=(freeCount 1, cost 0), walletInfo(user) free slot 1, balance 0 - NOT preview-verified (early leads are never previewed).",
   "firstSeenBlock": v3["Bd14"]["first_mints"]["first_block"], "scanMints": v3["Bd14"]["first_mints"]["count"],
   "scanMinters": v3["Bd14"]["first_mints"]["distinct_minters"],
   "lastReadBlock": v3["head"], "lastReadWib": "2026-11-02T06:37:47+07:00",
   "xVerified": False, "velocityVerified": False,
   "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131136346, 2026-11-02 06:23:37 WIB (Ankr getLogs address-filtered from block 131060000; 24 logs = totalSupply 24, so all mints ever are in range); mintStart() 2026-11-02 06:23:16 WIB corroborates launch minute. Sourcify verifiedAt 2026-11-01T23:23:47Z (verification time, NOT launch time). First-seen by this job in run 06:31 WIB via Sourcify feed.",
   "baselineNote": "EARLY lead reported once 2026-11-02 run 06:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed + AGENT_ID) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % UNVERIFIED (freeClaimed is per-user; no free total view); X unverified; velocity not yet computable (first baseline stored this run).",
   "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None, "currentRatePerMin": None,
   "previousRatePerMin": None, "velocityLegPasses": False,
   "velocityNote": "Run 06:31 WIB: first baseline stored (totalSupply 24); velocity not yet computable.",
}
snap["contracts"]["Hachiko"] = {
   "address": "0x48c977d13ef156475F086F907D8da9583E1E072E", "status": "strong-lead-reported-2026-11-02",
   "name": "Hachiko", "symbol": "HACHI", "kind": "ERC721",
   "totalSupply": v3["C48c"]["totalSupply()"], "freeClaimed": v3["C48c"]["freeClaimed()"], "freeCap": 1000,
   "freePctVerified": 50.0, "mintOpen": True,
   "userBalance": 0,
   "userSlotNote": "Slot open by read: quote(user,1)=0, balanceOf(user)=0, free pool 500/1000 remaining - NOT preview-verified (strong leads are never previewed); mintedByAgent/freeUsedByAgent views revert for the user's key, stated plainly.",
   "firstSeenBlock": v3["C48c"]["first_mints"]["first_block"], "scanMints": v3["C48c"]["first_mints"]["count"],
   "scanMinters": v3["C48c"]["first_mints"]["distinct_minters"],
   "lastReadBlock": v3["head"], "lastReadWib": "2026-11-02T06:37:47+07:00",
   "xVerified": False, "velocityVerified": False,
   "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131135228, 2026-11-02 06:15:14 WIB (Ankr getLogs address-filtered from block 131060000; 498 logs vs totalSupply 500 - logs trail supply by 2, stated plainly, first block still verified). Sourcify verifiedAt 2026-11-01T23:10:45Z (verification time, NOT launch time). First-seen by this job in run 06:31 WIB via Sourcify feed.",
   "baselineNote": "STRONG LEAD reported once 2026-11-02 run 06:31 WIB (new detection meeting all 3 strong legs at first read): first mint 2026-11-02 06:15:14 WIB (age <30 min, verified via first-mint bound), free 500/1000 = 50.00% verified (exactly at the 50% threshold), user slot open (quote 0, balance 0). X still UNVERIFIED and velocity not yet computable (first baseline), so NOT a candidate under the old body. Under the 2026-11-02 ~06:33 strong-lead direct-mint rule (effective next runs, body updated 07:01 WIB), this strong lead is eligible for direct preview+mint in the next run if all safety guards pass. This run performed NO preview/mint (its body predates the rule update).",
   "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None, "currentRatePerMin": None,
   "previousRatePerMin": None, "velocityLegPasses": False,
   "velocityNote": "Run 06:31 WIB: first baseline stored (totalSupply 500); velocity not yet computable.",
}
snap["contracts"]["Orchard Agent"] = {
   "address": "0xD1dc944F2ad3720c38636B40Fc93A1119003CBA4", "status": "early-lead-reported-2026-11-02",
   "name": "Orchard Agent", "symbol": "ORCHARD", "kind": "ERC721",
   "totalMinted": v3["D1dc"]["totalMinted()"], "FREE_SUPPLY": 410, "MAX_SUPPLY": 1423,
   "freePctVerified": None, "mintOpen": True,
   "userMintedBy": 0, "userBalance": 0,
   "userSlotNote": "Slot open by read: mintedBy(user)=0, costFor(1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
   "firstSeenBlock": v3["D1dc"]["first_mints"]["first_block"], "scanMints": v3["D1dc"]["first_mints"]["count"],
   "scanMinters": v3["D1dc"]["first_mints"]["distinct_minters"],
   "lastReadBlock": v3["head"], "lastReadWib": "2026-11-02T06:37:47+07:00",
   "xVerified": False, "velocityVerified": False,
   "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131137120, 2026-11-02 06:29:25 WIB (Ankr getLogs address-filtered from block 131060000; 168 logs = totalMinted 168, so all mints ever are in range). Sourcify verifiedAt 2026-11-01T23:30:24Z (verification time, NOT launch time). First-seen by this job in run 06:31 WIB via Sourcify feed.",
   "baselineNote": "EARLY lead reported once 2026-11-02 run 06:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + costFor + FREE_SUPPLY + agentIdRegistry) and agentIdRegistry() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % UNVERIFIED (no freeClaimed total view; 168/410 NOT used as a %); X unverified; velocity not yet computable (first baseline stored this run).",
   "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None, "currentRatePerMin": None,
   "previousRatePerMin": None, "velocityLegPasses": False,
   "velocityNote": "Run 06:31 WIB: first baseline stored (totalMinted 168); velocity not yet computable.",
}
snap["contracts"]["Meadow Agent"] = {
   "address": "0x22A1fb5C254d18Fb0187DD27A3a070d768c982fa", "status": "early-lead-reported-2026-11-02",
   "name": "Meadow Agent", "symbol": "MEADOW", "kind": "ERC721",
   "totalMinted": v3["A22A"]["totalMinted()"], "FREE_SUPPLY": 381, "MAX_SUPPLY": 1587,
   "freePctVerified": None, "mintOpen": True,
   "userMintedBy": 0, "userBalance": 0,
   "userSlotNote": "Slot open by read: mintedBy(user)=0, costFor(1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
   "firstSeenBlock": v3["A22A"]["first_mints"]["first_block"], "scanMints": v3["A22A"]["first_mints"]["count"],
   "scanMinters": v3["A22A"]["first_mints"]["distinct_minters"],
   "lastReadBlock": v3["head"], "lastReadWib": "2026-11-02T06:37:47+07:00",
   "xVerified": False, "velocityVerified": False,
   "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131134654, 2026-11-02 06:10:55 WIB (Ankr getLogs address-filtered from block 131060000; 320 logs vs totalMinted 321 - logs trail supply by 1, stated plainly, first block still verified). Sourcify verifiedAt 2026-11-01T23:11:52Z (verification time, NOT launch time). First-seen by this job in run 06:31 WIB via Sourcify feed.",
   "baselineNote": "EARLY lead reported once 2026-11-02 run 06:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + costFor + FREE_SUPPLY + agentIdRegistry) and agentIdRegistry() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % UNVERIFIED (no freeClaimed total view; 321/381 NOT used as a %); X unverified; velocity not yet computable (first baseline stored this run).",
   "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None, "currentRatePerMin": None,
   "previousRatePerMin": None, "velocityLegPasses": False,
   "velocityNote": "Run 06:31 WIB: first baseline stored (totalMinted 321); velocity not yet computable.",
}
# Track B pending
snap["pending_claims"]["binanceai.fun"].update({"totalShares": gi(main["TrackB_MINT"], "totalShares()"), "totalShares_last": gi(main["TrackB_MINT"], "totalShares()"),
    "launched": False, "tokenClaimed": False, "lastCheckBlock": B_MAIN, "lastCheckWib": W_MAIN})
snap["pending_claims"]["hive-pollen"].update({"pollenAgents": gi(main["Pollen_MINT"], "pollenAgents()"),
    "paidSold": gi(main["Pollen_MINT"], "paidSold()"), "launched": False, "lastCheckBlock": B_MAIN, "lastCheckWib": W_MAIN})
# Track C values (main read)
tc = snap["track_c"]
def tcup(key, **kw):
    if key in tc: tc[key].update(kw)
tcup("BNBbaby", sharesMinted=gi(main["BNBbaby"], "sharesMinted()"), freeMinted=gi(main["BNBbaby"], "freeMinted()"),
     paidShares=gi(main["BNBbaby"], "paidShares()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcup("DOG", sharesMinted=gi(main["DOG"], "sharesMinted()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcup("QILIN", cardsSold=gi(main["QILIN"], "cardsSold()"), freeCardsRemaining=gi(main["QILIN"], "freeCardsRemaining()"),
     freeGiven=gi(main["QILIN"], "freeGiven()"), cardsRemaining=gi(main["QILIN"], "cardsRemaining()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcup("SAFU Tower", freeClaimed_total=gi(main["SAFU"], "freeClaimed()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcup("SAMBARIO", cardsSold=gi(main["SAMBARIO"], "cardsSold()"), freeCardsRemaining=gi(main["SAMBARIO"], "freeCardsRemaining()"),
     freeGiven=gi(main["SAMBARIO"], "freeGiven()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcup("a7Be", sharesMinted=gi(main["a7Be"], "sharesMinted()"), freeSharesMinted=gi(main["a7Be"], "freeSharesMinted()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
# NIUBI / ZeroYuanGou / JUBAO / ZCMAO / JINLONG / BIAO / XI keys vary; update generically where present
for key, src, mapping in [
    ("NIUBI", main.get("NIUBI", {}), {"sharesMinted": "sharesMinted()", "freeMinted": "freeMinted()"}),
    ("ZeroYuanGou", main.get("ZeroYuanGou", {}), {"soldFree": "soldFree()"}),
    ("JUBAO", main.get("JUBAO", {}), {"freeClaimed": "freeClaimed()"}),
    ("ZCMAO", main.get("ZCMAO", {}), {"freeClaimed": "freeClaimed()"}),
    ("JINLONG", main.get("JINLONG", {}), {"freeClaimed": "freeClaimed()"}),
]:
    if key in tc:
        for outk, ink in mapping.items(): tc[key][outk] = gi(src, ink)
        tc[key].update({"lastCheckBlock": B_MAIN, "lastCheckWib": W_MAIN})
if "BIAO" in tc:
    tc["BIAO"].update({"freeClaimed": gi(extra["BIAO"], "freeClaimed()"), "sold": gi(extra["BIAO"], "sold()"), "lastCheckBlock": B_EXTRA, "lastCheckWib": W_EXTRA})
# XI key name in snapshot may be the character; try both
for key in list(tc.keys()):
    if key in ("XI", "\u5175"):
        tc[key].update({"soldFree": gi(extra["XI"], "soldFree()"), "lastCheckBlock": B_EXTRA, "lastCheckWib": W_EXTRA})
snap["timestamp_wib"] = "2026-11-02T06:31:00+07:00"
snap["note"] = ("Run 06:31 WIB: contracts = 46 (42 previous + PIXEL FROGS + Hachiko + Orchard Agent + Meadow Agent added; "
    "BINANCE HACK PROMOTED to strong lead, Hachiko reported as new STRONG LEAD; Velmora + Grove Agent verified but free pool exhausted, recorded only, not reported). "
    "HIVE Agents / Cathodex / Kirinova / Zapcourier were minted by the separate 06:36-06:44 WIB execution under the 2026-11-02 ~06:33 strong-lead direct-mint rule (this run performed NO execution); their minted-by-user statuses are PRESERVED here with fresh totals + receipt verification, never reverted to strong-lead. "
    "No track-A candidate passes all criteria; no new track-C lead/candidate; pending claims unchanged. Velocity passes recorded (no promotion: % below 50% and X unverified): "
    "Voltabyte, Junepup, Nightsable, Nimaluo, Neonwolfy, Griffinko, Gearpixel, Skelebop.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot updated, contracts:", len(snap["contracts"]))
