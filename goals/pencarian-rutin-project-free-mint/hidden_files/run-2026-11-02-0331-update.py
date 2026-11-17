#!/usr/bin/env python3
"""Run 0331 snapshot update (contracts + pending + track_c). Scan/seen/state applied separately after scan triage."""
import json, os
base = os.path.expanduser("~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
snap = json.load(open(base + "onchain-snapshot.json"))
read = json.load(open(base + "run-2026-11-02-0331-read.json"))
extra = json.load(open(base + "run-2026-11-02-0331-read-extra.json"))
cilok = json.load(open(base + "run-2026-11-02-0331-cilok.json"))
verify = json.load(open(base + "run-2026-11-02-0331-sourcify-verify.json"))
def gi(d, n):
    v = d.get(n, {}) if isinstance(d, dict) else {}
    return v.get("int") if isinstance(v, dict) else v

# (name, total, free, fsup, interval, block, wib)
updates = [
    ("HIVE Agents", 758, None, 1000, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Bubblebruin", 803, 802, 7777, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Zapcourier", 350, 350, 712, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Mothwraith", 300, 299, 869, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Cryonyx", 331, 330, 809, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Cathodex", 356, 356, 763, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Malabao", 321, 321, 844, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Slimelings", 1579, None, None, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Voltabyte", 226, 226, 925, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Saturnin", 185, 185, 838, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Kirinova", 310, 310, 711, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Ghostbloom", 219, 219, 942, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Junepup", 239, 239, 724, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Vorpry", 220, None, None, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Gourdwick", 317, 317, 868, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Kitsunaru", 302, 302, 865, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Nightsable", 275, 275, 794, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Lensorb", 289, 289, 776, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Nimaluo", 290, 289, 828, 24.23, 131114145, "2026-11-02T03:37:05+07:00"),
    ("Agents NormiePunks", 1160, None, None, 23.85, 131114295, "2026-11-02T03:38:13+07:00"),
    ("Medusine", 244, 244, 868, 23.85, 131114295, "2026-11-02T03:38:13+07:00"),
    ("Hotpotsage", 229, 229, 784, 23.85, 131114295, "2026-11-02T03:38:13+07:00"),
    ("Mummyrelic", 206, 206, 785, 23.85, 131114295, "2026-11-02T03:38:13+07:00"),
    ("Ravenhex", 222, 222, 925, 23.85, 131114295, "2026-11-02T03:38:13+07:00"),
    ("Orbitmarshal", 203, 203, 831, 23.85, 131114295, "2026-11-02T03:38:13+07:00"),
    ("Gearpixel", 86, 86, 832, 22.67, 131114488, "2026-11-02T03:39:40+07:00"),
    ("Skelebop", 92, 92, 902, 22.67, 131114488, "2026-11-02T03:39:40+07:00"),
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
    if free is not None: c["freeClaimed"] = free
    if fsup is not None: c["FREE_SUPPLY"] = fsup
    if free is not None and fsup: c["freePctVerified"] = round(100.0 * free / fsup, 2)
    if name == "HIVE Agents": c["freePctInference"] = round(100.0 * total / 1000, 2)
    c["mintedInInterval"] = minted
    c["intervalMinutes"] = interval
    c["previousRatePerMin"] = prev_rate
    c["currentRatePerMin"] = rate
    if prev_rate:
        c["velocityNote"] = (f"Run 03:31 WIB: +{minted} tokens in ~{interval} min = {rate}/min, "
            f"ratio vs prior {prev_rate} = {ratio}x, so the velocity leg {'PASSES' if passes else 'still FAILS'}. Stored as new baseline.")
    else:
        c["velocityNote"] = (f"Run 03:31 WIB: +{minted} tokens in ~{interval} min = {rate}/min; no previous rate to compare, "
            "so the velocity leg does NOT pass (never passed on a first rate). Stored as new baseline.")
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
mp["mintedPairs"] = gi(read["MirrorPair"], "mintedPairs()")
mp["lastReadBlock"] = 131114145; mp["lastReadWib"] = "2026-11-02T03:37:05+07:00"
mp["velocityNote"] = "Run 03:31 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
# Cilok
ci = snap["contracts"]["Cilok Cats: White Paw Genesis"]
ci["totalMinted"] = gi(cilok["Cilok"], "totalMinted()")
ci["totalSupply"] = ci["totalMinted"]
ci["freeMinted"] = gi(cilok["Cilok"], "freeMinted()")
ci["freeClaimed"] = ci["freeMinted"]
ci["previousTotalSupply"] = 1; ci["mintedInInterval"] = 0
ci["velocityNote"] = "Run 03:31 WIB: still totalMinted 1 (was 1) at block 131114488 - no new mint; still the sole owner mint, velocity not computable."
ci["lastReadBlock"] = 131114488; ci["lastReadWib"] = "2026-11-02T03:39:40+07:00"
# Lighthouse REMOVED: free tier exhausted / paid-only (costFor 0 -> 0.0005 BNB, totalMinted 351 -> 483 = FREE_SUPPLY)
lh = snap["contracts"].pop("Lighthouse Agent", None)
print("Lighthouse removed:", bool(lh))
# New early leads from Sourcify verify
import datetime
def wib(ts): return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
new_leads = [
    ("Orbitty", "0xE08289849427a82e336A64662bD951FcA4DE8d8E", "ORBITTY"),
    ("Neonwolfy", "0x9f320879e96d493d7ed18a3c1025c0d7ADFDd11b", "NEONWOLFY"),
    ("Sphinxel", "0x4ec6086B7DEF22A0D95823BCB6e9ec8840B2d5C4", "SPHINXEL"),
]
for nm, addr, sym in new_leads:
    v = verify[addr]; fm = v["first_mints"]
    tot = v["totalSupply()"]; free = v["freeClaimed()"]; fsup = v["FREE_SUPPLY()"]
    snap["contracts"][nm] = {
        "address": addr, "status": "early-lead-reported-2026-11-02", "name": nm, "symbol": sym, "kind": "ERC721",
        "totalSupply": tot, "freeClaimed": free, "FREE_SUPPLY": fsup, "MAX_SUPPLY": v["MAX_SUPPLY()"],
        "freePctVerified": round(100.0 * free / fsup, 2) if free is not None and fsup else None,
        "mintOpen": True, "userMintedBy": v["mintedBy_user"], "userFreeUsed": v["freeUsed_user"], "userBalance": v["balance_user"],
        "userSlotNote": "Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
        "firstSeenBlock": fm["first_block"], "scanMints": fm["count"], "scanMinters": fm["distinct_minters"],
        "lastReadBlock": verify["head"], "lastReadWib": "2026-11-02T03:42:45+07:00",
        "xVerified": False, "velocityVerified": False,
        "launchNote": f"First mint verified on-chain: first Transfer-from-zero at block {fm['first_block']}, {wib(fm['first_ts'])} (Ankr getLogs address-filtered from block 131060000; {fm['count']} logs in range vs totalSupply {tot} at verify time" + (" - logs trail supply by 2, stated plainly, first block still verified" if fm['count'] != tot else ", so all mints ever are in range") + "); no project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 03:31 WIB via Sourcify feed.",
        "baselineNote": "EARLY lead reported once 2026-11-02 run 03:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % far below 50%; X unverified; velocity not yet computable (first baseline stored this run).",
        "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None, "currentRatePerMin": None, "previousRatePerMin": None,
        "velocityNote": "Run 03:31 WIB: first baseline stored; velocity not yet computable (never passed on velocity alone).",
        "velocityLegPasses": False,
    }
    print("added early lead", nm, tot, free, fsup)
# Pixcade: watchlist-only, NOT launched (0 mints)
px = verify["0x21136e5ecBE886572b59a7e5B5D576fcE9534b89"]
snap["contracts"]["Pixcade"] = {
    "address": "0x21136e5ecBE886572b59a7e5B5D576fcE9534b89", "status": "watchlist-only-upcoming-2026-11-02", "name": "Pixcade", "symbol": "PXCD", "kind": "ERC721",
    "totalSupply": None, "totalMinted": 0, "freeClaimed": None, "freeMinted": 0, "FREE_SUPPLY": None, "MAX_SUPPLY": 3000,
    "freePctVerified": None, "mintOpen": None, "userBalance": 0,
    "userSlotNote": "No slot to check: 0 mints ever; never previewed.",
    "firstSeenBlock": None, "scanMints": 0, "scanMinters": 0,
    "lastReadBlock": verify["head"], "lastReadWib": "2026-11-02T03:42:45+07:00",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "NOT launched: totalMinted 0 and 0 Transfer-from-zero logs (Ankr getLogs address-filtered from block 131060000) at verify time; Sourcify ABI shows registry() reads 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F plus freeMint/freeClaimed/freeMinted/freeMintOpen, but no mint has occurred. First-seen by this job in run 03:31 WIB via Sourcify feed.",
    "baselineNote": "Watchlist-only UPCOMING item (not an early lead: no first mint verified). Never auto-minted/previewed. Promotes to early lead only when first mints are verified on-chain.",
    "velocityLegPasses": False,
}
print("added watchlist-only Pixcade")
# Pending claims
pc = snap["pending_claims"]["binanceai.fun"]
pc["launched"] = bool(gi(read["TrackB_MINT"], "launched()"))
pc["tokenClaimed"] = bool(gi(read["TrackB_MINT"], "tokenClaimed(address)"))
pc["totalShares_last"] = gi(read["TrackB_MINT"], "totalShares()")
pc["lastCheckBlock"] = read["block"]; pc["lastCheckWib"] = "2026-11-02T03:37:05+07:00"
hp = snap["pending_claims"]["hive-pollen"]
hp["launched"] = bool(gi(read["Pollen_MINT"], "launched()"))
hp["phase"] = gi(read["Pollen_MINT"], "phase()")
hp["pollenAgents"] = gi(read["Pollen_MINT"], "pollenAgents()")
hp["paidSold"] = gi(read["Pollen_MINT"], "paidSold()")
sl = gi(read["Pollen_MINT"], "pollenSlice()")
if sl: hp["pollenSlice_raw"] = str(sl); hp["pollenSlice_estimate"] = f"~{sl/1e18:,.0f} HIVE at 18 decimals (shrinks as more agents join; agentInfo claimable reads 0 pre-launch, so the slice is an estimate, not a fixed claimable)"
hp["lastCheckBlock"] = read["block"]; hp["lastCheckWib"] = "2026-11-02T03:37:05+07:00"
# Track C numerics
tc = snap["track_c"]
def upd(key, **kw):
    if key in tc: tc[key].update(kw)
upd("BNBbaby", sharesMinted=gi(read["BNBbaby"], "sharesMinted()"), freeMinted=gi(read["BNBbaby"], "freeMinted()"), paidShares=gi(read["BNBbaby"], "paidShares()"))
upd("DOG", sharesMinted=gi(read["DOG"], "sharesMinted()"))
upd("BNBPIG", sharesMinted=gi(read["BNBPIG"], "sharesMinted()"), freeMinted=gi(read["BNBPIG"], "freeMinted()"), paidShares=gi(read["BNBPIG"], "paidShares()"))
upd("SAMBARIO", cards="totalCards 7777, cardsSold 201, cardsRemaining 7576, freeCardCap 3333, freeCardsRemaining 3132, freeGiven 201")
upd("a7Be", sharesMinted=gi(read["a7Be"], "sharesMinted()"), freeSharesMinted=gi(read["a7Be"], "freeSharesMinted()"))
upd("NIUBI", sharesMinted=gi(read["NIUBI"], "sharesMinted()"), freeMinted=gi(read["NIUBI"], "freeMinted()"))
upd("QILIN", cards="totalCards 10000, cardsSold 4840, cardsRemaining 5160, freeCardCap 5000, freeCardsRemaining 207, freeGiven 4793")
upd("SAFU Tower", freeClaimed_total=gi(read["SAFU"], "freeClaimed()"))
upd("JUBAO", freeClaimed_total=gi(read["JUBAO"], "freeClaimed()"))
upd("ZCMAO", freeClaimed_total=gi(read["ZCMAO"], "freeClaimed()"))
upd("JINLONG", freeClaimed_total=gi(read["JINLONG"], "freeClaimed()"))
upd("JINLI", freeClaimed=gi(extra["JINLI"], "freeClaimed()"), freeRemaining=3000 - gi(extra["JINLI"], "freeClaimed()"))
upd("BIAO", freeClaimed=gi(extra["BIAO"], "freeClaimed()"), freeRemaining=4444 - (gi(extra["BIAO"], "freeClaimed()") or 0))
upd("兕", soldFree=gi(extra["XI"], "soldFree()"), freeRemaining=3000 - gi(extra["XI"], "soldFree()"))
snap["timestamp_wib"] = "2026-11-02T03:31:00+07:00"
json.dump(snap, open(base + "onchain-snapshot.json", "w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
