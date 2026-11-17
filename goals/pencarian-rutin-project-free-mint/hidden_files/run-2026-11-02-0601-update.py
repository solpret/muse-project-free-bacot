import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
def gi(d, n):
    v = d.get(n, {}) if isinstance(d, dict) else {}
    return v.get("int") if isinstance(v, dict) else v
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
main = json.load(open(f"{HF}/run-2026-11-02-0601-read.json"))
extra = json.load(open(f"{HF}/run-2026-11-02-0601-read-extra.json"))
cilok = json.load(open(f"{HF}/run-2026-11-02-0601-cilok.json"))
v2 = json.load(open(f"{HF}/run-2026-11-02-0601-verify2.json"))
B_MAIN, B_EXTRA, B_CILOK, B_V2 = main["block"], extra["block"], cilok["block"], v2["block"]
W_MAIN, W_EXTRA, W_CILOK, W_V2 = "2026-11-02T06:12:00+07:00", "2026-11-02T06:13:30+07:00", "2026-11-02T06:14:00+07:00", "2026-11-02T06:17:00+07:00"
MAIN_INT, EXTRA_INT, CILOK_INT, V2_INT = 35.5, 36.0, 36.0, 33.0

def upd(name, src, new_total, new_free, interval, block, readwib, total_key="totalSupply", free_key="freeClaimed"):
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
        c["velocityNote"] = (f"Run 06:01 WIB: +{minted} tokens in ~{interval} min = {rate}/min, ratio vs prior {old_rate} = {ratio}x, "
                             f"so the velocity leg {'PASSES' if passes else 'still FAILS'}. Stored as new baseline.")
    else:
        c["velocityNote"] = f"Run 06:01 WIB: +{minted} tokens in ~{interval} min = {rate}/min - first comparable rate, so the velocity leg does NOT pass. Stored as new baseline."
    c["lastReadBlock"] = block; c["lastReadWib"] = readwib
    return c

# HIVE (inference)
h = snap["contracts"]["HIVE Agents"]; old = h["totalSupply"]; new = gi(main["HIVE"], "totalSupply()")
minted = new - old; rate = round(minted / MAIN_INT, 3)
h.update({"previousTotalSupply": old, "totalSupply": new, "mintedInInterval": minted, "intervalMinutes": MAIN_INT,
          "previousRatePerMin": h["currentRatePerMin"], "currentRatePerMin": rate, "velocityLegPasses": False,
          "freePctInference": round(new / 1000 * 100, 1),
          "velocityNote": f"Run 06:01 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {h['previousRatePerMin']} = {round(rate / h['previousRatePerMin'], 2)}x, so the velocity leg still FAILS. Stored as new baseline.",
          "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN})
main_map = ["Bubblebruin","Zapcourier","Mothwraith","Cryonyx","Cathodex","Malabao","Voltabyte","Saturnin","Kirinova",
            "Ghostbloom","Junepup","Orbitty","Neonwolfy","Sphinxel","Witchlet","Venuspi","Neonraven","Griffinko","Tangpinku"]
for nm in main_map:
    upd(nm, main, gi(main[nm], "totalSupply()"), gi(main[nm], "freeClaimed()"), MAIN_INT, B_MAIN, W_MAIN)
# Slimelings
sl = snap["contracts"]["Slimelings"]; old = sl["totalSupply"]; new = gi(main["Slimelings"], "totalSupply()")
minted = new - old; rate = round(minted / MAIN_INT, 3); old_rate = sl["currentRatePerMin"]
sl.update({"previousTotalSupply": old, "totalSupply": new, "mintedCount": gi(main["Slimelings"], "mintedCount()"),
           "freeCount": gi(main["Slimelings"], "freeCount()"), "mintedInInterval": minted, "intervalMinutes": MAIN_INT,
           "previousRatePerMin": old_rate, "currentRatePerMin": rate,
           "velocityLegPasses": bool(old_rate and minted >= 20 and rate >= 1.5 * old_rate),
           "velocityNote": f"Run 06:01 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {old_rate} = {round(rate / old_rate, 2)}x, so the velocity leg still FAILS. Stored as new baseline.",
           "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN})
# Vorpry
vo = snap["contracts"]["Vorpry"]; old = vo["totalSupply"]; new = gi(main["Vorpry"], "totalSupply()")
minted = new - old; rate = round(minted / MAIN_INT, 3); old_rate = vo["currentRatePerMin"]
vo.update({"previousTotalSupply": old, "totalSupply": new, "totalMinted": gi(main["Vorpry"], "totalMinted()"),
           "openLeft": gi(main["Vorpry"], "openLeft()"), "mintedInInterval": minted, "intervalMinutes": MAIN_INT,
           "previousRatePerMin": old_rate, "currentRatePerMin": rate, "velocityLegPasses": False,
           "velocityNote": f"Run 06:01 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {old_rate} = {round(rate / old_rate, 2)}x, so the velocity leg still FAILS. Stored as new baseline.",
           "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN})
# Mirror Pair
mp = snap["contracts"]["Mirror Pair"]
mp.update({"mintedPairs": gi(main["MirrorPair"], "mintedPairs()"), "totalBonds": gi(main["MirrorPair"], "totalBonds()"),
           "velocityNote": "Run 06:01 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable.",
           "lastReadBlock": B_MAIN, "lastReadWib": W_MAIN})
# Extra wave
for nm in ["Agents NormiePunks","Medusine","Hotpotsage","Mummyrelic","Ravenhex","Orbitmarshal"]:
    upd(nm, extra, gi(extra[nm], "totalSupply()"), gi(extra[nm], "freeClaimed()"), EXTRA_INT, B_EXTRA, W_EXTRA)
# Cilok + Gearpixel/Skelebop
ci = snap["contracts"]["Cilok Cats: White Paw Genesis"]; old = ci["totalMinted"]; new = gi(cilok["Cilok"], "totalMinted()")
ci.update({"previousTotalSupply": old, "totalMinted": new, "freeMinted": gi(cilok["Cilok"], "freeMinted()"),
           "mintedInInterval": new - old, "intervalMinutes": CILOK_INT, "previousRatePerMin": ci["currentRatePerMin"],
           "currentRatePerMin": round((new - old) / CILOK_INT, 3), "velocityLegPasses": False,
           "velocityNote": f"Run 06:01 WIB: +{new - old} tokens in ~{CILOK_INT} min - no new mint; velocity leg still FAILS. Stored as new baseline.",
           "lastReadBlock": B_CILOK, "lastReadWib": W_CILOK})
for nm in ["Gearpixel","Skelebop"]:
    upd(nm, cilok, gi(cilok[nm], "totalSupply()"), gi(cilok[nm], "freeClaimed()"), CILOK_INT, B_CILOK, W_CILOK)
# Verify2: NULLSECTOR
ns = snap["contracts"]["NULLSECTOR"]; old = ns["totalSupply"]; new = v2["NULLSECTOR"]["totalSupply"]
minted = new - old; rate = round(minted / V2_INT, 3); old_rate = ns["currentRatePerMin"]
ns.update({"previousTotalSupply": old, "totalSupply": new, "mintedInInterval": minted, "intervalMinutes": V2_INT,
           "previousRatePerMin": old_rate, "currentRatePerMin": rate, "velocityLegPasses": False,
           "velocityNote": f"Run 06:01 WIB: +{minted} tokens in ~{V2_INT} min = {rate}/min, ratio vs prior {old_rate} = {round(rate / old_rate, 2)}x, so the velocity leg still FAILS. Stored as new baseline.",
           "lastReadBlock": B_V2, "lastReadWib": W_V2})
# Verify2: Onimaru / Rootlinks (first comparable rate -> does NOT pass)
oni = snap["contracts"]["Onimaru"]; oni.update({"totalMinted": v2["Onimaru"]["totalMinted"], "freeMinted": v2["Onimaru"]["freeMinted"],
    "freePctVerified": round(v2["Onimaru"]["freeMinted"] / 3000 * 100, 2), "userMintedBy": v2["Onimaru"]["mintedBy_user"],
    "userBalance": v2["Onimaru"]["balance_user"], "previousTotalSupply": 2, "mintedInInterval": v2["Onimaru"]["totalMinted"] - 2,
    "intervalMinutes": 33.0, "previousRatePerMin": None, "currentRatePerMin": round((v2["Onimaru"]["totalMinted"] - 2) / 33.0, 3),
    "velocityLegPasses": False,
    "velocityNote": "Run 06:01 WIB: +684 tokens in ~33 min - first comparable rate (no previous rate), so the velocity leg does NOT pass. Stored as new baseline. Free % 22.83% still below 50%; remains EARLY lead only.",
    "lastReadBlock": B_V2, "lastReadWib": W_V2})
roo = snap["contracts"]["Rootlinks"]; roo.update({"totalMinted": v2["Rootlinks"]["totalMinted"], "freeMinted": v2["Rootlinks"]["freeMinted"],
    "freePctVerified": round(v2["Rootlinks"]["freeMinted"] / 1000 * 100, 2), "userBalance": v2["Rootlinks"]["balance_user"],
    "previousTotalSupply": 1, "mintedInInterval": v2["Rootlinks"]["totalMinted"] - 1, "intervalMinutes": 33.0,
    "previousRatePerMin": None, "currentRatePerMin": round((v2["Rootlinks"]["totalMinted"] - 1) / 33.0, 3),
    "velocityLegPasses": False,
    "velocityNote": "Run 06:01 WIB: +198 tokens in ~33 min - first comparable rate (no previous rate), so the velocity leg does NOT pass. Stored as new baseline. Free % 19.80% still below 50%; remains EARLY lead only.",
    "lastReadBlock": B_V2, "lastReadWib": W_V2})
# Kirinova promotion to strong lead
ki = snap["contracts"]["Kirinova"]
ki["status"] = "strong-lead-promoted-2026-11-02"
ki["baselineNote"] = ("PROMOTED to strong lead in run 06:01 WIB (reported once): first mint 2026-11-02 00:13:31 WIB (age ~6h, verified via first-mint bound), "
    "free 359/711 = 50.49% verified (crossed 50% this run from 47.40% at 05:31 WIB), user slot open (mintedBy 0, freeUsed 0, quote 0, balance 0). "
    "X still UNVERIFIED and velocity FAILS (+22, ratio 1.11x), so NOT a candidate. Never auto-minted, never previewed.")
# New early leads
snap["contracts"]["BINANCE HACK"] = {
    "address": "0x072154bD66Ac9D65Fd29fabCEe1ca1dD52342c5c", "status": "early-lead-reported-2026-11-02",
    "name": "BINANCE HACK", "symbol": "BHACK", "kind": "ERC721",
    "totalMinted": 22, "totalFreeMinted": 22, "freeAllocation": 60, "paidAllocation": 440, "maxSupply": 500,
    "freePctVerified": 36.67, "mintPrice_paid_lane": "0.0005 BNB",
    "registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "userSlotNote": "Slot open by read: freeMintedByAgentId(user)=0, mintedByAgentId(user)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
    "firstSeenBlock": 131132699, "scanMints": 22, "scanMinters": 22,
    "lastReadBlock": 131134748, "lastReadWib": "2026-11-02T06:16:00+07:00", "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131132699, 2026-11-02 05:56:16 WIB (Ankr getLogs address-filtered from block 131060000; 22 logs = totalMinted 22, so all mints ever are in range); no project-stated launch time found; Sourcify verifiedAt 2026-11-01T22:55:20Z (verification time, NOT launch time). First-seen by this job in run 06:01 WIB via Sourcify feed.",
    "baselineNote": "EARLY lead reported once 2026-11-02 run 06:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + mintFree + agentRegistry + freeAllocation/freeMintedByAgentId/totalFreeMinted) and agentRegistry() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 36.67% verified, below 50%; X unverified; velocity not yet computable (first baseline stored this run).",
    "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None, "currentRatePerMin": None,
    "previousRatePerMin": None, "velocityLegPasses": False,
    "velocityNote": "Run 06:01 WIB: first baseline stored (totalMinted 22); velocity not yet computable."}
snap["contracts"]["Volcano Agent"] = {
    "address": "0x0b32Ab148B57043fBc6F37d762449112387Fa662", "status": "early-lead-reported-2026-11-02",
    "name": "Volcano Agent", "symbol": "VOLC", "kind": "ERC721",
    "totalMinted": 300, "FREE_SUPPLY": 468, "MAX_SUPPLY": 1864, "MAX_PER_WALLET": 5,
    "freePctVerified": None, "PRICE_paid_lane": "0.0005 BNB", "costFor_1": 0,
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "userSlotNote": "Slot open by read: mintedBy(user)=0, costFor(1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
    "firstSeenBlock": 131131149, "scanMints": 300, "scanMinters": 126,
    "lastReadBlock": 131134748, "lastReadWib": "2026-11-02T06:16:00+07:00", "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131131149, 2026-11-02 05:44:38 WIB (Ankr getLogs address-filtered from block 131060000; 300 logs = totalMinted 300, so all mints ever are in range); no project-stated launch time found; Sourcify verifiedAt 2026-11-01T22:45:28Z (verification time, NOT launch time). First-seen by this job in run 06:01 WIB via Sourcify feed.",
    "baselineNote": "EARLY lead reported once 2026-11-02 run 06:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + costFor + FREE_SUPPLY + agentIdRegistry) and agentIdRegistry() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % UNVERIFIED (no freeClaimed total view; 300/468 NOT used as a %); X unverified; velocity not yet computable (first baseline stored this run).",
    "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None, "currentRatePerMin": None,
    "previousRatePerMin": None, "velocityLegPasses": False,
    "velocityNote": "Run 06:01 WIB: first baseline stored (totalMinted 300); velocity not yet computable."}
# Track C updates
tc = snap["track_c"]
def tcu(key, **kw):
    if key in tc: tc[key].update(kw)
tcu("BNBbaby", sharesMinted=gi(main["BNBbaby"], "sharesMinted()"), freeMinted=gi(main["BNBbaby"], "freeMinted()"),
    paidShares=gi(main["BNBbaby"], "paidShares()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcu("DOG", sharesMinted=gi(main["DOG"], "sharesMinted()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcu("QILIN", cardsSold=gi(main["QILIN"], "cardsSold()"), freeCardsRemaining=gi(main["QILIN"], "freeCardsRemaining()"),
    freeGiven=gi(main["QILIN"], "freeGiven()"), cardsRemaining=gi(main["QILIN"], "cardsRemaining()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcu("SAFU Tower", lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcu("SAMBARIO", cardsSold=gi(main["SAMBARIO"], "cardsSold()"), freeCardsRemaining=gi(main["SAMBARIO"], "freeCardsRemaining()"),
    freeGiven=gi(main["SAMBARIO"], "freeGiven()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcu("a7Be", sharesMinted=gi(main["a7Be"], "sharesMinted()"), freeSharesMinted=gi(main["a7Be"], "freeSharesMinted()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcu("NIUBI", sharesMinted=gi(main["NIUBI"], "sharesMinted()"), freeMinted=gi(main["NIUBI"], "freeMinted()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcu("JUBAO", freeClaimed=gi(main["JUBAO"], "freeClaimed()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcu("ZCMAO", freeClaimed=gi(main["ZCMAO"], "freeClaimed()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
tcu("JINLONG", freeClaimed=gi(main["JINLONG"], "freeClaimed()"), lastCheckBlock=B_MAIN, lastCheckWib=W_MAIN)
# 零元购 key check
for k in list(tc.keys()):
    if "元" in k or "Zero" in k:
        tc[k].update({"soldFree": gi(main["ZeroYuanGou"], "soldFree()"), "lastCheckBlock": B_MAIN, "lastCheckWib": W_MAIN})
tcu("BIAO", freeClaimed=gi(extra["BIAO"], "freeClaimed()"), lastCheckBlock=B_EXTRA, lastCheckWib=W_EXTRA)
for k in list(tc.keys()):
    if k == "兕" or k == "XI":
        tc[k].update({"soldFree": gi(extra["XI"], "soldFree()"), "lastCheckBlock": B_EXTRA, "lastCheckWib": W_EXTRA})
# Pending claims
pc = snap["pending_claims"]
pc["binanceai.fun"].update({"launched": False, "totalShares": gi(main["TrackB_MINT"], "totalShares()"), "tokenClaimed": False,
    "lastCheckBlock": B_MAIN, "lastCheckWib": W_MAIN})
pc["hive-pollen"].update({"launched": False, "phase": gi(main["Pollen_MINT"], "phase()"), "pollenAgents": gi(main["Pollen_MINT"], "pollenAgents()"),
    "paidSold": gi(main["Pollen_MINT"], "paidSold()"), "lastCheckBlock": B_MAIN, "lastCheckWib": W_MAIN})
snap["timestamp_wib"] = "2026-11-02T06:01:00+07:00"
snap["note"] = ("Run 06:01 WIB: contracts = 42 (40 previous + BINANCE HACK + Volcano Agent added as EARLY leads, reported once; Kirinova PROMOTED to strong lead, reported once). "
    "No track-A candidate passes all criteria; no new track-C lead/candidate; pending claims unchanged. Velocity passes: none this run (Slimelings ratio 1.38x fails; all others fail on count and/or ratio).")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "track_c:", list(tc.keys()))
