"""Snapshot update for run 2026-11-02 08:01 WIB (non-scan parts only).
Scan watermark / seen / 5c are deferred to the scan-completion handoff.
Merge discipline: re-read current snapshot, touch only verified fields.
"""
import json, shutil, datetime

B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
NOW_WIB = NOW.strftime("%Y-%m-%dT%H:%M:%S+07:00")
READ_BLOCK = 131154283
TRACKC_BLOCK = 131152308

shutil.copy(B + "onchain-snapshot.json", B + "onchain-snapshot-2026-11-02-0801.bak.json")
snap = json.load(open(B + "onchain-snapshot.json"))
read = json.load(open(B + "run-2026-11-02-0801-read.json"))
trackc = json.load(open(B + "run-2026-11-02-0801-trackc-read.json"))

def iv(entry, fn):
    d = entry.get(fn)
    if isinstance(d, dict) and d.get("error") is None:
        return d.get("int")
    return None

def parse_wib(s):
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None

updated = []
for name, entry in snap["contracts"].items():
    r = read.get(name)
    if not r:
        continue
    # supply view (adapter: totalSupply else totalMinted)
    new_total = iv(r, "totalSupply()")
    view = "totalSupply"
    if new_total is None:
        new_total = iv(r, "totalMinted()")
        view = "totalMinted"
    old_total = entry.get("totalSupply") if entry.get("totalSupply") is not None else entry.get("totalMinted")
    if new_total is not None:
        entry[view] = new_total
        entry["supplyView"] = view
    # free counter
    fc = iv(r, "freeClaimed()")
    if fc is not None:
        entry["freeClaimed"] = fc
    else:
        fm = iv(r, "freeMinted()")
        if fm is not None:
            entry["freeMinted"] = fm
    # caps
    for fn, field in [("FREE_SUPPLY()", "FREE_SUPPLY"), ("freeSupply()", "freeSupply"),
                      ("FREE_CAP()", "FREE_CAP"), ("MAX_SUPPLY()", "MAX_SUPPLY")]:
        v = iv(r, fn)
        if v is not None:
            entry[field] = v
    mo = iv(r, "mintOpen()")
    if mo is not None:
        entry["mintOpen"] = bool(mo)
    mb = iv(r, "mintedBy(address)")
    if mb is not None:
        entry["userMintedBy"] = mb
    fu = iv(r, "freeUsed(address)")
    if fu is not None:
        entry["userFreeUsed"] = fu
    bal = iv(r, "balanceOf(address)")
    if bal is not None:
        entry["userBalance"] = bal
    # free % where counter + cap both known
    counter = entry.get("freeClaimed") if entry.get("freeClaimed") is not None else entry.get("freeMinted")
    cap = entry.get("FREE_SUPPLY") or entry.get("freeSupply") or entry.get("FREE_CAP")
    if counter is not None and cap:
        entry["freePctVerified"] = round(counter / cap * 100, 2)
    # velocity vs this contract's own lastReadWib
    if new_total is not None and old_total is not None:
        minted = new_total - old_total
        prev_rate = entry.get("currentRatePerMin")
        old_t = parse_wib(entry.get("lastReadWib") or "")
        mins = (NOW - old_t).total_seconds() / 60.0 if old_t else None
        entry["previousTotalSupply"] = old_total
        entry["mintedInInterval"] = minted
        if mins:
            entry["intervalMinutes"] = round(mins, 2)
            rate = minted / mins if mins > 0 else 0
            entry["currentRatePerMin"] = round(rate, 3)
            if prev_rate is not None:
                entry["previousRatePerMin"] = prev_rate
                passes = rate >= 1.5 * prev_rate and minted >= 20
                entry["velocityLegPasses"] = passes
                entry["velocityNote"] = (
                    f"Run 08:01 WIB: +{minted} tokens in ~{mins:.1f} min = {rate:.3f}/min, "
                    f"ratio vs prior {prev_rate} = {(rate / prev_rate if prev_rate else 0):.2f}x -> "
                    f"velocity leg {'PASSES' if passes else 'FAILS'}."
                )
            else:
                entry["velocityLegPasses"] = False
                entry["velocityNote"] = (
                    f"Run 08:01 WIB: +{minted} tokens in ~{mins:.1f} min = {rate:.3f}/min; "
                    "no previous rate yet, velocity not yet computable."
                )
    entry["lastReadBlock"] = READ_BLOCK
    entry["lastReadWib"] = NOW_WIB
    updated.append(name)

# ---- Neonraven post-mint override (exec-check block 131154506, mint block 131154550)
nr = snap["contracts"]["Neonraven"]
nr["status"] = "minted-by-user-2026-11-02"
nr["totalSupply"] = 370
nr["freeClaimed"] = 362
nr["freePctVerified"] = 50.14
nr["userMintedBy"] = 1
nr["userFreeUsed"] = 1
nr["userBalance"] = 1
nr["mintTx"] = "0x0dea14b45665ae73a64f832a6e457028683c5bea586e7c8a597eb12b83da272b"
nr["mintBlock"] = 131154550
nr["mintGas"] = 136128
nr["mintTokenId"] = 370
nr["mintedInInterval"] = 14
nr["currentRatePerMin"] = 0.251
nr["previousRatePerMin"] = 0.356
nr["velocityLegPasses"] = False
nr["velocityNote"] = ("Run 08:01 WIB exec-check (block 131154506): +14 in ~55.8 min = 0.251/min, "
                      "ratio vs prior 0.356 = 0.70x -> velocity leg FAILS (not required under strong-lead direct-mint rule).")
nr["lastReadBlock"] = 131154550
nr["lastReadWib"] = NOW_WIB
nr["userSlotNote"] = ("Slot USED by this run's strong-lead direct mint (Neonraven #370, tx "
                      "0x0dea14b45665ae73a64f832a6e457028683c5bea586e7c8a597eb12b83da272b); next mint is paid, NOT authorized.")
nr["rarityNote"] = ("Tier not verified (no Rarity/Tier trait). tokenURI traits: Character=Raven humanoid, "
                    "Outfit=Neon armor, Light=Neon rim light, Background=Rainy neon city. Appended to nft-rarity-inventory.md.")
nr["marketplaceNote"] = ("No live venue verified: contract-matched web search returned only unrelated Raven/Neon "
                         "collections on other chains; no own project market and no Element collection page found for this contract.")
nr["auditNote"] = ("Binance audit run 08:01 WIB: hasResult=false disclosed as NO RESULT, never a pass; riskItems empty.")
nr["siteNote"] = ("No project site found; verified Sourcify source + ABI + on-chain state are the inspection basis.")
nr["xNote"] = ("X UNVERIFIED (targeted search found no project X account and no readable project discussion; "
               "not required under the strong-lead direct-mint rule).")

# ---- Track C: 9 minted
MINTED = {
    "JUBAO":   dict(tx="0x04bcd2df1b123a31cc78727d5df647302c9eda915f0705e6504a13fe26a4cf6a", block=131152715, gas=130910,
                       bal_before="0", bal_after="50000000000000000000000000", flag="freeClaimedById(user)=true", pool="freeClaimed total 19 -> 20 / 4444 FREE_SHARES"),
    "ZCMAO":   dict(tx="0x665d47846a2e59dd29cae306c803da9f702a1b6c2af01f08f408032dbf3576e2", block=131152850, gas=130910,
                       bal_before="0", bal_after="50000000000000000000000000", flag="freeClaimedById(user)=true", pool="freeClaimed total 38 -> 39 / 4444 FREE_SHARES"),
    "JINLONG": dict(tx="0xd1e6b1e4cae2503a6d7a3edddf85b40c017208637b91b3fdd24c903fea2a3585", block=131152951, gas=130910,
                       bal_before="0", bal_after="50000000000000000000000000", flag="freeClaimedById(user)=true", pool="freeClaimed total 158 -> 159 / 4444 FREE_SHARES"),
    "DOG":     dict(tx="0x650f4851c738a6f364eee9e14b09c051f28d202ff4ee2e1ca27f484afd1d1110", block=131153165, gas=131528,
                       bal_before="0", bal_after="10000000000000000000000000", flag="freeClaimed(agentId)=true, sharesByWallet=1", pool="sharesMinted 1208 -> 1209 (free pool 4000 FREE_SHARES)"),
    "a7Be":    dict(tx="0x0c32b260c3cbfa5a79fdd995e372ad2ebbf432e7e0b1833df71eea359f39bd22", block=131153226, gas=139040,
                       bal_before="0", bal_after="10000000000000000000000000", flag="freeClaimed(agentId)=true, sharesByWallet=1", pool="freeSharesMinted 431 -> 432 / 4000 FREE_SHARES"),
    "SAMBARIO":dict(tx="0x4aab9991b6a6e8ff86c532b5e2bef8bc8ec3228e66b6e7c0a0aba73b4690126c", block=131153543, gas=130201,
                       bal_before="0", bal_after="100000000000000000000000", flag="freeClaimed(user)=true, quotaLeft 10 -> 9", pool="cardsSold 205 -> 206, freeCardsRemaining 3128 -> 3127 / 3333 freeCardCap"),
    "Velmora": dict(tx="0x56638a714e3fcc39ea27c7de7fc05677df04c56cf5d40e41f693177970d3ec6c", block=131153605, gas=119749,
                       bal_before="0", bal_after="10000000000000000000000000", flag="claimedBy(user)=1, freeTaken(user)=true", pool="freeClaimedShares 327 -> 334 / 5000 FREE_SHARES (other wallets claimed in between)"),
    "零元购":   dict(tx="0xa8750c47660684bdf7d9f0ce0365d2a3c3ccb9a7beb1d4294b0e2ccddbbb242a", block=131153860, gas=94450,
                       bal_before="0", bal_after="1000000000000000000000000000000000000000000000", flag="freeById(keccak('masgayut'))=true", pool="soldFree 77 -> 78 / 2000 FREE_TOTAL, totalSold 88 -> 89"),
    "兕":      dict(tx="0x57c457f34b9994bdc66f5842e40f503749c960b7c3163dc29fd14d660254b18e", block=131153960, gas=121596,
                       bal_before="0", bal_after="1000000000000000000000000000000000000000000000", flag="hasMintedById=true", pool="soldFree 74 -> 75 / 3000 FREE_POOL"),
}
for name, m in MINTED.items():
    e = snap["track_c"][name]
    e["status"] = "minted-by-user-2026-11-02"
    e["mintTx"] = m["tx"]
    e["mintBlock"] = m["block"]
    e["mintGas"] = m["gas"]
    e["balanceBefore"] = m["bal_before"]
    e["balanceAfter"] = m["bal_after"]
    e["freeFlagAfter"] = m["flag"]
    e["poolAfter"] = m["pool"]
    e["userSlotNote"] = "Slot USED by this run's track-C lead direct mint; free flag flipped true. Marketplace/rarity N/A (not an NFT)."
    e["lastCheckBlock"] = m["block"]
    e["lastCheckWib"] = NOW_WIB
    e["lastReadBlock"] = m["block"]
    e["lastReadWib"] = NOW_WIB

# ---- Track C: 2 blocked (kept in track_c, NOT removed, NOT re-reported next run unless status changes)
snap["track_c"]["BIAO"]["status"] = "blocked-preview-2026-11-02"
snap["track_c"]["BIAO"]["blockedPreview"] = {
    "error": "351805 Transaction simulation failed: execution reverted (claimFree() preview)",
    "diagnosis": ("info() = [price 0.002 BNB, 0, 0, 1, deadline 1793818866, perShare 5e22, 0, 0, 0]; phase 1, "
                  "tradingOpen false, poolCreated false, poolPending false, startedAt 1793559666, freeClaimed total still 0, "
                  "sold 0; remainingQuota returns 9 for numeric ids 0 and 1 alike (not id-specific); registry "
                  "tokenOfOwnerByIndex/tokenByIndex calls revert. Cause of the revert UNDETERMINED from ABI + reads alone "
                  "(sale window open in time, yet claimFree reverts; per-user numeric-agentId encoding could not be resolved). "
                  "STOP per guard: no execution, no retry with invented calldata, no paid fallback."),
    "lastReadBlock": TRACKC_BLOCK,
}
snap["track_c"]["BIAO"]["lastReadBlock"] = TRACKC_BLOCK
snap["track_c"]["BIAO"]["lastReadWib"] = NOW_WIB
snap["track_c"]["BNBbaby"]["status"] = "blocked-preview-2026-11-02"
snap["track_c"]["BNBbaby"]["blockedPreview"] = {
    "error": "351805 Transaction simulation failed: Insufficient balance (mint(1) preview)",
    "diagnosis": ("User USDT balance 0.706865222998515225 (< 1 USDT); PRICE() = 1e18 wei, quote(uint256) pure returns 1e18, "
                  "usdt() = 0x55d398326f99059ff775485246999027b3197955, paidRemainingFor(user)=10, paidBy(user)=0, while "
                  "freeAvailable(user)=1, freeClaimed(user)=0, mintedBy(user)=0. Simulation consistent with a 1 USDT charge "
                  "against a 0.7068 USDT balance: the free path did NOT apply in simulation despite the free reads; exact reason "
                  "undetermined from ABI + reads alone (Sourcify source-file endpoints returned 404, mint logic unreadable). "
                  "STOP per guard: no execution, no USDT approval, no top-up, no paid fallback. Earlier 'slot open' inference was "
                  "insufficient; the preview is the binding check."),
    "lastReadBlock": TRACKC_BLOCK,
}
snap["track_c"]["BNBbaby"]["lastReadBlock"] = TRACKC_BLOCK
snap["track_c"]["BNBbaby"]["lastReadWib"] = NOW_WIB

# ---- Pending claims (still NOT open, already reported once, never re-reported as pending)
pc = snap["pending_claims"]
pc["binanceai.fun"]["launched"] = False
pc["binanceai.fun"]["totalShares"] = 3107
pc["binanceai.fun"]["totalShares_last"] = 3107
pc["binanceai.fun"]["lastCheckBlock"] = READ_BLOCK
pc["binanceai.fun"]["lastCheckWib"] = NOW_WIB
pc["hive-pollen"]["launched"] = False
pc["hive-pollen"]["pollenAgents"] = 7622
pc["hive-pollen"]["paidSold"] = 1023
pc["hive-pollen"]["lastCheckBlock"] = READ_BLOCK
pc["hive-pollen"]["lastCheckWib"] = NOW_WIB

snap["timestamp_wib"] = NOW_WIB
json.dump(snap, open(B + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print("contracts updated:", len(updated))
print("now:", NOW_WIB, "read block:", READ_BLOCK)
print("Neonraven:", json.dumps(snap["contracts"]["Neonraven"], indent=1)[:600])
