#!/usr/bin/env python3
"""Run 0401 snapshot update. Readings from run-2026-11-02-0401-read*.json.
Intervals: main block 131117714 (04:03:51 WIB) vs snapshot lastRead 131114145
(03:37:05 WIB) = 26.77 min; extra block 131117870 (04:05:02) vs 131114295
(03:38:13) = 26.82 min; cilok block 131117956 (04:05:40) vs 131114488
(03:39:40) = 26.00 min. Velocity passes only if rate >= 1.5x previous AND
>= 20 tokens in interval; a first rate never passes."""
import json, copy
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(HF + "onchain-snapshot.json"))
C = snap["contracts"]

def vel(key, new_total, interval, prev_rate, prev_total_field="totalSupply"):
    old = C[key]
    minted = new_total - old["totalSupply"]
    rate = round(minted / interval, 3)
    passes = bool(prev_rate is not None and minted >= 20 and rate >= 1.5 * prev_rate)
    old["previousTotalSupply"] = old["totalSupply"]
    old["totalSupply"] = new_total
    old["mintedInInterval"] = minted
    old["intervalMinutes"] = round(interval, 2)
    old["previousRatePerMin"] = prev_rate
    old["currentRatePerMin"] = rate
    old["velocityLegPasses"] = passes
    old["velocityNote"] = (f"Run 04:01 WIB: +{minted} tokens in ~{interval:.2f} min = "
                           f"{rate}/min, ratio vs prior {prev_rate} = "
                           f"{round(rate / prev_rate, 2) if prev_rate else 'n/a'}x, so the velocity leg "
                           f"{'PASSES' if passes else 'still FAILS' if prev_rate is not None else 'does NOT pass (first rate, never passed on a first rate)'}. "
                           "Stored as new baseline.")
    old["velocityVerified"] = passes
    return minted, rate, passes

MAIN_T, EXTRA_T, CILOK_T = "2026-11-02T04:03:51+07:00", "2026-11-02T04:05:02+07:00", "2026-11-02T04:05:40+07:00"
MAIN_B, EXTRA_B, CILOK_B = 131117714, 131117870, 131117956

def touch(key, block, wib):
    C[key]["lastReadBlock"] = block
    C[key]["lastReadWib"] = wib

# --- main-read contracts (26.77 min) ---
updates_main = {
    "HIVE Agents": (763, 0.083, None),  # free % inference, handled below
    "Bubblebruin": (806, 0.073, 805),
    "Zapcourier": (357, 0.182, 357),
    "Mothwraith": (305, 0.182, 304),
    "Cryonyx": (336, 0.254, 335),
    "Cathodex": (378, 0.145, 378),
    "Malabao": (342, 0.182, 342),
    "Slimelings": (1630, 2.064, None),
    "Voltabyte": (228, 0.145, 228),
    "Saturnin": (187, 0.145, 187),
    "Kirinova": (313, 0.145, 313),
    "Ghostbloom": (221, 0.182, 221),
    "Junepup": (242, 0.036, 242),
    "Vorpry": (226, 0.218, None),
    "Gourdwick": (323, 0.69, 323),
    "Kitsunaru": (309, 0.908, 309),
    "Nightsable": (279, 0.581, 279),
    "Lensorb": (295, 0.726, 295),
    "Nimaluo": (294, 0.726, 293),
    "Orbitty": (131, None, 131),
    "Neonwolfy": (94, None, 94),
    "Sphinxel": (125, None, 125),
}
for key, (tot, prev_rate, free) in updates_main.items():
    vel(key, tot, 26.77, prev_rate)
    touch(key, MAIN_B, MAIN_T)
    if free is not None:
        C[key]["freeClaimed"] = free
C["HIVE Agents"]["freePctInference"] = 76.3
C["HIVE Agents"]["freePctNote"] = "Inference only: totalSupply 763 + totalPaid 0 -> 763/1000 FREE_SUPPLY = 76.3%; no freeClaimed view on contract."
C["Bubblebruin"]["freePctVerified"] = round(805 / 7777 * 100, 2)
C["Zapcourier"]["freePctVerified"] = round(357 / 712 * 100, 2)
C["Mothwraith"]["freePctVerified"] = round(304 / 869 * 100, 2)
C["Cryonyx"]["freePctVerified"] = round(335 / 809 * 100, 2)
C["Cathodex"]["freePctVerified"] = round(378 / 763 * 100, 2)
C["Malabao"]["freePctVerified"] = round(342 / 844 * 100, 2)
C["Voltabyte"]["freePctVerified"] = round(228 / 925 * 100, 2)
C["Saturnin"]["freePctVerified"] = round(187 / 838 * 100, 2)
C["Kirinova"]["freePctVerified"] = round(313 / 711 * 100, 2)
C["Ghostbloom"]["freePctVerified"] = round(221 / 942 * 100, 2)
C["Junepup"]["freePctVerified"] = round(242 / 724 * 100, 2)
C["Gourdwick"]["freePctVerified"] = round(323 / 868 * 100, 2)
C["Kitsunaru"]["freePctVerified"] = round(309 / 865 * 100, 2)
C["Nightsable"]["freePctVerified"] = round(279 / 794 * 100, 2)
C["Lensorb"]["freePctVerified"] = round(295 / 776 * 100, 2)
C["Nimaluo"]["freePctVerified"] = round(293 / 828 * 100, 2)
C["Orbitty"]["freePctVerified"] = round(131 / 884 * 100, 2)
C["Neonwolfy"]["freePctVerified"] = round(94 / 850 * 100, 2)
C["Sphinxel"]["freePctVerified"] = round(125 / 799 * 100, 2)
# Zapcourier promotion: age verified via first mint 2026-11-01 23:18 WIB (<=48h),
# free % 50.14% verified, user slot open -> all 3 strong-lead legs met.
C["Zapcourier"]["status"] = "strong-lead-promoted-2026-11-02"
C["Zapcourier"]["baselineNote"] = ("PROMOTED to strong lead in run 04:01 WIB (reported once): first mint "
    "2026-11-01 23:18 WIB (age ~4.8h, verified via first-mint bound), free 357/712 = 50.14% "
    "verified, user slot open (mintedBy 0, freeUsed 0, quote 0). X still UNVERIFIED and velocity "
    "still FAILS (+7 < 20), so NOT a candidate. Never auto-minted, never previewed.")
C["Mirror Pair"]["lastReadBlock"] = MAIN_B
C["Mirror Pair"]["lastReadWib"] = MAIN_T
C["Mirror Pair"]["mintedPairs"] = 2
C["Mirror Pair"]["velocityNote"] = "Run 04:01 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
C["Slimelings"]["mintedCount"] = 1612
C["Slimelings"]["freeCount"] = 1602
C["Vorpry"]["openLeft"] = 1577

# --- extra-read contracts (26.82 min) ---
updates_extra = {
    "Agents NormiePunks": (1640, 28.931, None),
    "Medusine": (272, 1.342, 272),
    "Hotpotsage": (254, 1.426, 254),
    "Mummyrelic": (232, 1.174, 232),
    "Ravenhex": (251, 1.216, 251),
    "Orbitmarshal": (235, 1.468, 235),
}
for key, (tot, prev_rate, free) in updates_extra.items():
    vel(key, tot, 26.82, prev_rate)
    touch(key, EXTRA_B, EXTRA_T)
    if free is not None:
        C[key]["freeClaimed"] = free
C["Medusine"]["freePctVerified"] = round(272 / 868 * 100, 2)
C["Hotpotsage"]["freePctVerified"] = round(254 / 784 * 100, 2)
C["Mummyrelic"]["freePctVerified"] = round(232 / 785 * 100, 2)
C["Ravenhex"]["freePctVerified"] = round(251 / 925 * 100, 2)
C["Orbitmarshal"]["freePctVerified"] = round(235 / 831 * 100, 2)

# --- cilok-read contracts (26.00 min) ---
for key, (tot, prev_rate, free) in {
    "Gearpixel": (138, 3.132, 138),
    "Skelebop": (129, 3.397, 129),
}.items():
    vel(key, tot, 26.00, prev_rate)
    touch(key, CILOK_B, CILOK_T)
    C[key]["freeClaimed"] = free
C["Gearpixel"]["freePctVerified"] = round(138 / 832 * 100, 2)
C["Skelebop"]["freePctVerified"] = round(129 / 902 * 100, 2)
C["Cilok Cats: White Paw Genesis"]["lastReadBlock"] = CILOK_B
C["Cilok Cats: White Paw Genesis"]["lastReadWib"] = CILOK_T
C["Cilok Cats: White Paw Genesis"]["velocityNote"] = "Run 04:01 WIB: totalMinted still 1 - no new mint; velocity not computable."

# --- Pixcade: promoted from watchlist-only upcoming to EARLY lead ---
C["Pixcade"] = {
    "address": "0x21136e5ecBE886572b59a7e5B5D576fcE9534b89",
    "status": "early-lead-reported-2026-11-02",
    "name": "Pixcade", "symbol": "PXCD", "kind": "ERC721",
    "totalSupply": None, "totalMinted": 24, "freeMinted": 24,
    "FREE_CAP": 1500, "MAX_SUPPLY": 3000,
    "freePctVerified": round(24 / 1500 * 100, 2),
    "freeMintOpen": True,
    "userSlotNote": ("Slot NOT conclusively verified by a dedicated view: mintedBy/freeUsed views "
        "revert (no such view); balanceOf(user)=0, isAgent(user)=true, walletInfo(user) words "
        "[0,0,0,0,0,1,7] not interpreted as a mint. NOT preview-verified (early leads are never previewed)."),
    "firstSeenBlock": 131117663,
    "firstMintWib": "2026-11-02T04:03:29+07:00",
    "scanMints": 23, "scanMinters": 23,
    "lastReadBlock": 131118486, "lastReadWib": "2026-11-02T04:08:00+07:00",
    "xVerified": False, "velocityVerified": False,
    "launchNote": ("First mint verified on-chain: first Transfer-from-zero at block 131117663, "
        "2026-11-02 04:03:29 WIB (Ankr getLogs address-filtered from block 131060000; 23 logs in "
        "range = totalMinted 23 at verify time, 23 distinct minters, so no earlier mint exists; "
        "at the main read totalMinted was 2, growing to 24 by the follow-up read). No project-stated "
        "launch time found; Sourcify verifiedAt 2026-11-01T20:36:07Z is verification time, NOT launch time. "
        "First-seen by this job in run 04:01 WIB via the watchlist-only upcoming entry (totalMinted 0 at 03:31 WIB)."),
    "baselineNote": ("EARLY lead reported once 2026-11-02 run 04:01 WIB (promotion from watchlist-only "
        "upcoming). Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (freeMint + "
        "freeMinted + freeMintOpen + FREE_CAP) and registry() reads "
        "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 1.60% verified, far below 50%; "
        "X unverified; velocity not yet computable (supply view is totalMinted, totalSupply() reverts; "
        "first baseline stored this run)."),
    "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None,
    "currentRatePerMin": None, "previousRatePerMin": None, "velocityLegPasses": False,
    "supplyView": "totalMinted (totalSupply() reverts)",
}
# --- 5 new wave early leads (first baselines; velocity not yet computable) ---
wave = {
    "Witchlet": ("0x626cd91e26Da5AC49B713Ab14894f54AbC4DC4DB", "WITCHLET", 131119025, "2026-11-02T04:13:41+07:00", 11, 11, 929, 1162),
    "Venuspi": ("0xaB453745b37634C27d65b347B3aC514882cB2F37", "VENUSPI", 131118956, "2026-11-02T04:13:10+07:00", 16, 16, 840, 1051),
    "Neonraven": ("0xcc5608A7F5A5Bc8F1bEABcD010A8C0066a0243Ae", "NEONRAVEN", 131118952, "2026-11-02T04:13:09+07:00", 17, 16, 722, 903),
    "Griffinko": ("0xB5a083bd9E8E330085e8F459F13f080d4F8fE5B4", "GRIFFINKO", 131118948, "2026-11-02T04:13:07+07:00", 18, 18, 712, 891),
    "Tangpinku": ("0x33D66b461E55d6969ACfAe0C95dACf158F8d04B0", "TANGPINKU", 131118939, "2026-11-02T04:13:03+07:00", 23, 23, 875, 1094),
}
for name, (addr, sym, fblk, fwib, tot, logs, fs, ms) in wave.items():
    trail = "" if logs == tot else f" (logs trail supply by {tot - logs}, stated plainly, first block still verified)"
    C[name] = {
        "address": addr, "status": "early-lead-reported-2026-11-02",
        "name": name, "symbol": sym, "kind": "ERC721",
        "totalSupply": tot, "freeClaimed": tot, "FREE_SUPPLY": fs, "MAX_SUPPLY": ms,
        "freePctVerified": round(tot / fs * 100, 2), "mintOpen": True,
        "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
        "userSlotNote": ("Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, "
            "balance 0 - NOT preview-verified (early leads are never previewed)."),
        "firstSeenBlock": fblk, "scanMints": logs, "scanMinters": logs,
        "lastReadBlock": 131119286, "lastReadWib": "2026-11-02T04:14:00+07:00",
        "xVerified": False, "velocityVerified": False,
        "launchNote": (f"First mint verified on-chain: first Transfer-from-zero at block {fblk}, "
            f"{fwib} WIB (Ankr getLogs address-filtered from block 131060000; {logs} logs in range "
            f"vs totalSupply {tot} at verify time{trail}, {logs} distinct minters, so no earlier mint "
            "exists); no project-stated launch time found; Sourcify verifiedAt is verification time, "
            "NOT launch time. First-seen by this job in run 04:01 WIB via Sourcify feed."),
        "baselineNote": ("EARLY lead reported once 2026-11-02 run 04:01 WIB. Never auto-minted/previewed. "
            "Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + "
            "FREE_SUPPLY) and AGENT_ID() reads the registry "
            "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % far below 50%; X unverified; "
            "velocity not yet computable (first baseline stored this run)."),
        "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None,
        "currentRatePerMin": None, "previousRatePerMin": None, "velocityLegPasses": False,
    }

# --- pending claims ---
snap["pending_claims"]["binanceai.fun"].update(
    {"launched": False, "tokenClaimed": False, "totalShares_last": 3104,
     "lastCheckBlock": MAIN_B, "lastCheckWib": MAIN_T})
snap["pending_claims"]["hive-pollen"].update(
    {"launched": False, "pollenAgents": 7556, "paidSold": 1010,
     "lastCheckBlock": MAIN_B, "lastCheckWib": MAIN_T})

# --- track_c updates; JINLI removed (sold out, change already reported by hot leg 03:44 WIB) ---
tc = snap["track_c"]
tc["BNBbaby"].update({"sharesMinted": 9561, "freeMinted": 9240, "paidShares": 321})
tc["DOG"].update({"sharesMinted": 1135})
tc["BNBPIG"].update({"sharesMinted": 5070, "freeMinted": 4898, "freeRemaining": 102})
tc["SAMBARIO"].update({"cardsSold": 202, "cardsRemaining": 7575, "freeCardsRemaining": 3131})
tc["a7Be"].update({"sharesMinted": 424, "freeSharesMinted": 411})
tc["NIUBI"].update({"sharesMinted": 64, "freeMinted": 63})
tc["QILIN"].update({"cardsSold": 4850, "freeCardsRemaining": 197, "freeGiven": 4803})
tc["SAFU Tower"].update({"freeClaimed_total": 4444})
tc["零元购"].update({"soldFree": 76, "totalSold": 77})
tc["JUBAO"].update({"freeClaimed": 15})
tc["ZCMAO"].update({"freeClaimed": 16})
tc["JINLONG"].update({"freeClaimed": 15})
tc["BIAO"].update({"freeClaimed": 0})
tc["兕"].update({"soldFree": 68, "freeRemaining": 2932})
jinli = tc.pop("JINLI", None)
snap["timestamp_wib"] = "2026-11-02T04:01:00+07:00"
snap["note"] = ("Run 04:01 WIB: contracts = 39 (33 previous - 0 removed + Pixcade promoted from "
    "watchlist-only upcoming + 5 new wave early leads); Zapcourier promoted early -> strong lead "
    "(50.14% verified free, age verified, slot open; X unverified, velocity fails, NOT a candidate); "
    "Cathodex and Malabao velocity PASSES this run but free % below 50% (49.54% / 40.52%), so NO promotion; "
    "JINLI removed from track_c (free pool sold out 3000/3000; sellout already reported once by hot leg "
    "03:44 WIB, not re-reported here). No track-A candidate, no track-B opening, no track-C candidate; "
    "no preview, mint, or transaction performed.")
json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]), "track_c:", len(tc), "JINLI removed:", jinli is not None)
