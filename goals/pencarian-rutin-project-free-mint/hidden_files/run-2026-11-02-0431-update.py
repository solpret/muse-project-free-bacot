#!/usr/bin/env python3
"""Run 0431 snapshot update. Intervals: main 33.63 min (04:03:51->04:37:29),
extra 33.37 min (04:05:02->04:38:24), cilok 33.20 min (04:05:40->04:38:52),
wave 21.83 min (04:15:39->04:37:29), pixcade 27.83 min (04:09:39->04:37:29).
Velocity passes only if rate >= 1.5x previous AND >= 20 tokens; a first rate never passes."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(HF + "onchain-snapshot.json"))
C = snap["contracts"]
def vel(key, new_total, interval, prev_rate, total_field="totalSupply"):
    old = C[key]
    minted = new_total - old[total_field]
    rate = round(minted / interval, 3)
    passes = bool(prev_rate is not None and minted >= 20 and rate >= 1.5 * prev_rate)
    old["previousTotalSupply"] = old[total_field]
    old[total_field] = new_total
    old["mintedInInterval"] = minted
    old["intervalMinutes"] = round(interval, 2)
    old["previousRatePerMin"] = prev_rate
    old["currentRatePerMin"] = rate
    old["velocityLegPasses"] = passes
    old["velocityNote"] = (f"Run 04:31 WIB: +{minted} tokens in ~{interval:.2f} min = {rate}/min, ratio vs prior {prev_rate} = "
                           f"{round(rate / prev_rate, 2) if prev_rate else 'n/a'}x, so the velocity leg "
                           f"{'PASSES' if passes else 'still FAILS' if prev_rate is not None else 'does NOT pass (first rate, never passed on a first rate)'}. Stored as new baseline.")
    old["velocityVerified"] = passes
    return minted, rate, passes
def touch(key, block, wib):
    C[key]["lastReadBlock"] = block; C[key]["lastReadWib"] = wib
MAIN_T, EXTRA_T, CILOK_T = "2026-11-02T04:37:29+07:00", "2026-11-02T04:38:24+07:00", "2026-11-02T04:38:52+07:00"
MAIN_B, EXTRA_B, CILOK_B = 131122197, 131122320, 131122381
# prev rates taken from snapshot currentRatePerMin at 0401
prev = {k: C[k].get("currentRatePerMin") for k in C}
updates_main = {
    "HIVE Agents": (781, prev["HIVE Agents"], None),
    "Bubblebruin": (814, prev["Bubblebruin"], 813),
    "Zapcourier": (363, prev["Zapcourier"], 363),
    "Mothwraith": (314, prev["Mothwraith"], 313),
    "Cryonyx": (348, prev["Cryonyx"], 347),
    "Cathodex": (389, prev["Cathodex"], 389),
    "Malabao": (351, prev["Malabao"], 351),
    "Slimelings": (1661, prev["Slimelings"], None),
    "Voltabyte": (237, prev["Voltabyte"], 237),
    "Saturnin": (197, prev["Saturnin"], 197),
    "Kirinova": (322, prev["Kirinova"], 322),
    "Ghostbloom": (233, prev["Ghostbloom"], 233),
    "Junepup": (254, prev["Junepup"], 254),
    "Vorpry": (227, prev["Vorpry"], None),
    "Gourdwick": (329, prev["Gourdwick"], 329),
    "Kitsunaru": (319, prev["Kitsunaru"], 319),
    "Nightsable": (285, prev["Nightsable"], 285),
    "Lensorb": (310, prev["Lensorb"], 310),
    "Nimaluo": (305, prev["Nimaluo"], 304),
    "Orbitty": (193, prev["Orbitty"], 193),
    "Neonwolfy": (125, prev["Neonwolfy"], 125),
    "Sphinxel": (169, prev["Sphinxel"], 169),
}
for key, (tot, pr, free) in updates_main.items():
    vel(key, tot, 33.63, pr); touch(key, MAIN_B, MAIN_T)
    if free is not None: C[key]["freeClaimed"] = free
C["HIVE Agents"]["freePctInference"] = round(781/1000*100, 1)
C["HIVE Agents"]["freePctNote"] = "Inference only: totalSupply 781 + totalPaid 0 -> 781/1000 FREE_SUPPLY = 78.1%; no freeClaimed view on contract."
for key, cap in [("Bubblebruin",7777),("Zapcourier",712),("Mothwraith",869),("Cryonyx",809),("Cathodex",763),("Malabao",844),("Voltabyte",925),("Saturnin",838),("Kirinova",711),("Ghostbloom",942),("Junepup",724),("Gourdwick",868),("Kitsunaru",865),("Nightsable",794),("Lensorb",776),("Nimaluo",828),("Orbitty",884),("Neonwolfy",850),("Sphinxel",799)]:
    C[key]["freePctVerified"] = round(C[key]["freeClaimed"]/cap*100, 2)
C["Mirror Pair"]["lastReadBlock"] = MAIN_B; C["Mirror Pair"]["lastReadWib"] = MAIN_T
C["Mirror Pair"]["mintedPairs"] = 2
C["Mirror Pair"]["velocityNote"] = "Run 04:31 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
C["Slimelings"]["mintedCount"] = 1643; C["Slimelings"]["freeCount"] = 1633
C["Vorpry"]["openLeft"] = 1576
# wave-5 (first comparable rate, never passes)
for key, tot, free, cap in [("Witchlet",60,60,929),("Venuspi",67,67,840),("Neonraven",70,70,722),("Griffinko",76,76,712),("Tangpinku",96,96,875)]:
    vel(key, tot, 21.83, None); touch(key, MAIN_B, MAIN_T)
    C[key]["freeClaimed"] = free; C[key]["freePctVerified"] = round(free/cap*100, 2)
# Pixcade (first comparable rate, never passes; supply view totalMinted)
old = C["Pixcade"]; minted = 183 - old["totalMinted"]; rate = round(minted/27.83, 3)
old["previousTotalSupply"] = None; old["previousTotalMinted"] = old["totalMinted"]; old["totalMinted"] = 183; old["freeMinted"] = 183
old["mintedInInterval"] = minted; old["intervalMinutes"] = 27.83; old["previousRatePerMin"] = None; old["currentRatePerMin"] = rate
old["velocityLegPasses"] = False; old["velocityVerified"] = False
old["velocityNote"] = f"Run 04:31 WIB: +{minted} tokens in ~27.83 min = {rate}/min, first comparable rate - does NOT pass (never passed on a first rate). Stored as new baseline."
old["freePctVerified"] = round(183/1500*100, 2); old["lastReadBlock"] = MAIN_B; old["lastReadWib"] = MAIN_T
# extra
updates_extra = {"Agents NormiePunks": (1905, prev["Agents NormiePunks"], None), "Medusine": (287, prev["Medusine"], 287),
    "Hotpotsage": (286, prev["Hotpotsage"], 286), "Mummyrelic": (249, prev["Mummyrelic"], 249),
    "Ravenhex": (263, prev["Ravenhex"], 263), "Orbitmarshal": (272, prev["Orbitmarshal"], 272)}
for key, (tot, pr, free) in updates_extra.items():
    vel(key, tot, 33.37, pr); touch(key, EXTRA_B, EXTRA_T)
    if free is not None: C[key]["freeClaimed"] = free
for key, cap in [("Medusine",868),("Hotpotsage",784),("Mummyrelic",785),("Ravenhex",925),("Orbitmarshal",831)]:
    C[key]["freePctVerified"] = round(C[key]["freeClaimed"]/cap*100, 2)
# cilok
for key, tot, free, cap in [("Gearpixel",198,198,832),("Skelebop",185,185,902)]:
    vel(key, tot, 33.20, prev[key]); touch(key, CILOK_B, CILOK_T)
    C[key]["freeClaimed"] = free; C[key]["freePctVerified"] = round(free/cap*100, 2)
C["Cilok Cats: White Paw Genesis"]["lastReadBlock"] = CILOK_B; C["Cilok Cats: White Paw Genesis"]["lastReadWib"] = CILOK_T
C["Cilok Cats: White Paw Genesis"]["totalMinted"] = 1; C["Cilok Cats: White Paw Genesis"]["freeMinted"] = 1
# Cathodex promotion: age verified (first mint 2026-11-01 23:18 WIB, ~5.3h), free 389/763=50.99% verified, slot open -> all 3 strong legs
C["Cathodex"]["status"] = "strong-lead-promoted-2026-11-02"
C["Cathodex"]["baselineNote"] = ("PROMOTED to strong lead in run 04:31 WIB (reported once): first mint 2026-11-01 23:18 WIB (age ~5.3h, verified via first-mint bound), "
    "free 389/763 = 50.99% verified (crossed 50% this run from 49.54% at 04:01 WIB), user slot open (mintedBy 0, freeUsed 0, quote 0, balance 0). "
    "X still UNVERIFIED and velocity FAILS (+11 < 20), so NOT a candidate. Never auto-minted, never previewed.")
# NEW: NULLSECTOR (early) and Root Agent (strong, inference %)
C["NULLSECTOR"] = {
    "address": "0x9395e207F9928657237DE96ffB12340094c073cd", "status": "early-lead-reported-2026-11-02",
    "name": "NULLSECTOR", "symbol": "NULL", "kind": "ERC721",
    "totalSupply": 432, "MAX_SUPPLY": 4321, "freePctVerified": None, "mintOpen": True,
    "userMintedBy": None, "userFreeUsed": None, "userBalance": 0,
    "userSlotNote": "Slot open by read: freeClaimed(user)=false, balanceOf(user)=0 - NOT preview-verified (early leads are never previewed).",
    "firstSeenBlock": 130811138, "scanMints": 432, "scanMinters": 428,
    "lastReadBlock": 131122868, "lastReadWib": "2026-11-02T04:55:00+07:00",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 130811138, 2026-10-31 13:43:54 WIB (Ankr getLogs from startBlock 130811113; 432 logs = totalSupply 432, so no earlier mint exists); no project-stated launch time found; Sourcify verifiedAt 2026-11-01T21:30:42Z (verification time, NOT launch time). First-seen by this job in run 04:31 WIB via Sourcify feed (hot leg 04:34 WIB explicitly left NFT early detection to the main job).",
    "baselineNote": "EARLY lead reported once 2026-11-02 run 04:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mintFree + mintPaid + freeClaimed(address) + AGENT_ID) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % UNVERIFIED (no free-cap view; freeClaimed is per-user, paidMinted view reverts); X unverified; velocity not yet computable (first baseline stored this run). Age ~39h at report, VERIFIED ≤48h via first-mint bound.",
}
C["Root Agent"] = {
    "address": "0x900a89FA78b64D6C26B76A314FEd1d6caE9e7a74", "status": "strong-lead-promoted-2026-11-02",
    "name": "Root Agent", "symbol": "ROOT", "kind": "ERC721",
    "totalMinted": 337, "FREE_SUPPLY": 422, "MAX_SUPPLY": 1690, "freePctVerified": None,
    "freePctInference": round(337/422*100, 2), "mintOpen": True,
    "userMintedBy": 0, "userBalance": 0,
    "userSlotNote": "Slot open by read: mintedBy(user)=0, balanceOf(user)=0, costFor(1)=0, currentPrice()=0 - NOT preview-verified (strong leads are never previewed/minted).",
    "firstSeenBlock": 131119415, "scanMints": 335, "scanMinters": 129,
    "lastReadBlock": 131122868, "lastReadWib": "2026-11-02T04:55:00+07:00",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131119415, 2026-11-02 04:16:37 WIB (Ankr getLogs from block 131060000; 335 logs = totalMinted 335 at log head, so no earlier mint exists); no project-stated launch time found; Sourcify verifiedAt 2026-11-01T21:18:10Z (verification time, NOT launch time). First-seen by this job in run 04:31 WIB via Sourcify feed.",
    "baselineNote": "STRONG lead reported once 2026-11-02 run 04:31 WIB (reported directly at strong tier, not as early first: all 3 strong legs met at first verification). Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + costFor + FREE_SUPPLY + agentIdRegistry) and agentIdRegistry() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % is INFERENCE ONLY: totalMinted 337 / FREE_SUPPLY 422 = 79.86% with currentPrice()=0 and costFor(1/2/5)=0; no verified freeClaimed counter exists on this contract. X unverified; velocity not yet computable (first baseline stored this run), so NOT a candidate.",
    "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None, "currentRatePerMin": None, "previousRatePerMin": None,
    "velocityLegPasses": False, "velocityNote": "Run 04:31 WIB: first baseline stored (totalMinted 337); velocity not yet computable, never passed on a first rate.",
}
# pending claims
pc = snap["pending_claims"]
pc["binanceai.fun"]["lastCheckBlock"] = MAIN_B; pc["binanceai.fun"]["lastCheckWib"] = MAIN_T; pc["binanceai.fun"]["totalShares_last"] = 3104; pc["binanceai.fun"]["launched"] = False
pc["hive-pollen"]["lastCheckBlock"] = MAIN_B; pc["hive-pollen"]["lastCheckWib"] = MAIN_T; pc["hive-pollen"]["pollenAgents"] = 7562; pc["hive-pollen"]["launched"] = False
# track_c updates
tc = snap["track_c"]
def upd(k, **kw):
    if k in tc: tc[k].update(kw)
upd("BNBbaby", sharesMinted=9710, freeMinted=9388, paidShares=322)
upd("DOG", sharesMinted=1146)
upd("BNBPIG", sharesMinted=5154, freeMinted=4982, paidShares=172)
upd("SAMBARIO", cardsSold=203, cardsRemaining=7574, freeCardsRemaining=3130, freeGiven=203)
upd("a7Be", sharesMinted=425, freeSharesMinted=412, paidSharesMinted=13)
upd("NIUBI", sharesMinted=65, freeMinted=64)
upd("QILIN", cardsSold=4866, cardsRemaining=5134, freeCardsRemaining=181, freeGiven=4819)
upd("BIAO", freeClaimed=0)
upd("兕", soldFree=71, freeRemaining=2929)
snap["timestamp_wib"] = "2026-11-02T04:31:00+07:00"
snap["note"] = "Run 04:31 WIB: contracts=40 (38 + NULLSECTOR early + Root Agent strong); Cathodex promoted early->strong (389/763=50.99% verified); no track-A candidate; no track-B change; no new track-C lead/candidate."
json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("contracts", len(snap["contracts"]), "Cathodex%", C["Cathodex"]["freePctVerified"], "RootInf%", C["Root Agent"]["freePctInference"])
