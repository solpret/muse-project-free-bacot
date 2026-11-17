#!/usr/bin/env python3
"""Snapshot update for run 2026-11-02 09:01 WIB (non-scan parts; scan deferred to handoff)."""
import json, shutil, datetime
B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
NOW_WIB = NOW.strftime("%Y-%m-%dT%H:%M:%S+07:00")
READ_BLOCK = 131159081
shutil.copy(B + "onchain-snapshot.json", B + "onchain-snapshot-2026-11-02-0901.bak.json")
snap = json.load(open(B + "onchain-snapshot.json"))
read = json.load(open(B + "run-2026-11-02-0901-read.json"))
verify = json.load(open(B + "run-2026-11-02-0901-verify.json"))
def iv(entry, fn):
    d = entry.get(fn)
    if isinstance(d, dict) and d.get("error") is None:
        return d.get("int")
    return None
def parse_wib(s):
    try: return datetime.datetime.fromisoformat(s)
    except Exception: return None
for name, entry in snap["contracts"].items():
    r = read.get(name)
    if not r: continue
    new_total = iv(r, "totalSupply()"); view = "totalSupply"
    if new_total is None:
        new_total = iv(r, "totalMinted()"); view = "totalMinted"
    old_total = entry.get("totalSupply") if entry.get("totalSupply") is not None else entry.get("totalMinted")
    if new_total is not None:
        entry[view] = new_total; entry["supplyView"] = view
    fc = iv(r, "freeClaimed()")
    if fc is not None: entry["freeClaimed"] = fc
    else:
        fm = iv(r, "freeMinted()")
        if fm is not None: entry["freeMinted"] = fm
    for fn, field in [("FREE_SUPPLY()", "FREE_SUPPLY"), ("freeSupply()", "freeSupply"),
                      ("FREE_CAP()", "FREE_CAP"), ("MAX_SUPPLY()", "MAX_SUPPLY")]:
        v = iv(r, fn)
        if v is not None: entry[field] = v
    mo = iv(r, "mintOpen()")
    if mo is not None: entry["mintOpen"] = bool(mo)
    mb = iv(r, "mintedBy(address)")
    if mb is not None: entry["userMintedBy"] = mb
    fu = iv(r, "freeUsed(address)")
    if fu is not None: entry["userFreeUsed"] = fu
    bal = iv(r, "balanceOf(address)")
    if bal is not None: entry["userBalance"] = bal
    counter = entry.get("freeClaimed") if entry.get("freeClaimed") is not None else entry.get("freeMinted")
    cap = entry.get("FREE_SUPPLY") or entry.get("freeSupply") or entry.get("FREE_CAP")
    if counter is not None and cap: entry["freePctVerified"] = round(counter / cap * 100, 2)
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
                entry["velocityNote"] = (f"Run 09:01 WIB (read block {READ_BLOCK}): +{minted} tokens in ~{mins:.1f} min = {rate:.3f}/min, "
                    f"ratio vs prior {prev_rate} = {(rate / prev_rate if prev_rate else 0):.2f}x -> velocity leg {'PASSES' if passes else 'FAILS'}.")
            else:
                entry["velocityLegPasses"] = False
                entry["velocityNote"] = (f"Run 09:01 WIB (read block {READ_BLOCK}): +{minted} tokens in ~{mins:.1f} min = {rate:.3f}/min; "
                    "no previous rate yet, velocity not yet computable.")
    entry["lastReadBlock"] = READ_BLOCK
    entry["lastReadWib"] = NOW_WIB
# Mirror Pair manual (no totalSupply view)
mp = snap["contracts"]["Mirror Pair"]
mp_r = read.get("Mirror Pair", {})
mp["mintedPairs"] = iv(mp_r, "mintedPairs()")
mp["hasPaired_user"] = iv(mp_r, "hasPaired(address)")
mp["hasAgentId_user"] = iv(mp_r, "hasAgentId(address)")
mp["userBalance"] = iv(mp_r, "balanceOf(address)")
mp["lastReadBlock"] = READ_BLOCK; mp["lastReadWib"] = NOW_WIB
# ---- 6 strong-lead direct mints: post-mint overrides from verify.json ----
MINTS = {
 "Lensorb": ("0xf12fc0668575cd3c8f0bdff8b11b4e6d17cd6c55844da82b8de6905d0f631c16", 131159627, 392),
 "Hotpotsage": ("0xfc616ac93769d5af2e03682f8990f9eeae778d6913d171c72aee910542eb1fa8", 131159630, 398),
 "Plutopop": ("0x29ce300d774d3b3cf883e96cc2b245a8740799948392116753d83865dcc27acc", 131159634, 516),
 "Ghoulipop": ("0xe07caf6101faf4e253b5191016f95580320882ba87a9101256f168350c2f976d", 131159638, 541),
 "Servobun": ("0x9a0d81f9f34aef7c03146625f7422d89414bc74c0dfa6128977451a1dca33483", 131159642, 517),
 "Xianyulo": ("0xbb26fc50eb20f4cf9816da860aa12f253e549eeb4e7d798145bbd59fe5ed0e64", 131159646, 507),
}
for name, (tx, blk, tok) in MINTS.items():
    e = snap["contracts"][name]; v = verify[name]
    e["status"] = "minted-by-user-2026-11-02"
    e["totalSupply"] = v["totalSupply()"]; e["freeClaimed"] = v["freeClaimed()"]
    cap = e.get("FREE_SUPPLY")
    if cap: e["freePctVerified"] = round(v["freeClaimed()"] / cap * 100, 2)
    e["userMintedBy"] = 1; e["userFreeUsed"] = 1; e["userBalance"] = 1
    e["mintTx"] = tx; e["mintBlock"] = blk; e["mintGas"] = v["gasUsed"]; e["mintTokenId"] = tok
    e["lastReadBlock"] = blk; e["lastReadWib"] = NOW_WIB
# ---- 2 new early leads ----
sv = json.load(open(B + "run-2026-11-02-0901-sourcify-verify.json"))
NEW = {
 "Vesperfang": ("0x2a91b304eE74162007730CF1da24C1d8C137c627", "VESPER"),
 "Ioforge": ("0x259b5Da3f44a44C89bcA5EE2297582c41c758d0F", "IOFRGE"),
}
for name, (addr, sym) in NEW.items():
    d = sv[addr]; st = d["state"]; fm = d["first_mint"]
    snap["contracts"][name] = {
     "address": addr, "status": "early-lead-reported-2026-11-02", "name": name, "symbol": sym, "kind": "ERC721",
     "totalSupply": st["totalSupply()"], "freeClaimed": st["freeClaimed()"],
     "FREE_SUPPLY": st["FREE_SUPPLY()"], "MAX_SUPPLY": st["MAX_SUPPLY()"],
     "freePctVerified": round(st["freeClaimed()"] / st["FREE_SUPPLY()"] * 100, 2),
     "mintOpen": bool(st["mintOpen()"]), "userMintedBy": st["mintedBy(address)"],
     "userFreeUsed": st["freeUsed(address)"], "userBalance": st["balanceOf(address)"],
     "userSlotNote": "Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
     "firstSeenBlock": fm["block"], "scanMints": fm["count_in_range"], "scanMinters": fm["minters"],
     "lastReadBlock": sv["head"], "lastReadWib": NOW_WIB, "xVerified": False, "velocityVerified": False,
     "launchNote": f"First mint verified on-chain: first Transfer-from-zero at block {fm['block']}, {fm['wib']} (Ankr getLogs address-filtered from block 131060000; {fm['count_in_range']} logs in range vs totalSupply {st['totalSupply()']} at verify time - Ioforge logs trail supply by 1, stated plainly, first block still verified); no project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 09:01 WIB via Sourcify feed.",
     "baselineNote": "EARLY lead reported once 2026-11-02 run 09:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify exact_match ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() in ABI. Free % below 50%; X unverified (web search found no project X account/discussion, only unrelated items); velocity not yet computable (first baseline stored this run).",
     "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None,
     "currentRatePerMin": None, "previousRatePerMin": None,
     "velocityNote": "Run 09:01 WIB: first baseline stored; velocity not yet computable.",
     "velocityLegPasses": False, "supplyView": "totalSupply",
    }
# ---- Track-B pending ----
tb = read["TrackB_MINT"]; pl = read["Pollen_MINT"]
pc = snap["pending_claims"]
pc["binanceai.fun"]["launched"] = bool(iv(tb, "launched()"))
pc["binanceai.fun"]["tokenClaimed"] = bool(iv(tb, "tokenClaimed(address)"))
pc["binanceai.fun"]["totalShares"] = iv(tb, "totalShares()")
pc["binanceai.fun"]["totalShares_last"] = iv(tb, "totalShares()")
pc["binanceai.fun"]["lastCheckBlock"] = READ_BLOCK; pc["binanceai.fun"]["lastCheckWib"] = NOW_WIB
pc["hive-pollen"]["launched"] = bool(iv(pl, "launched()"))
pc["hive-pollen"]["phase"] = iv(pl, "phase()")
pc["hive-pollen"]["pollenAgents"] = iv(pl, "pollenAgents()")
pc["hive-pollen"]["pollenSlice_raw"] = str(iv(pl, "pollenSlice()"))
pc["hive-pollen"]["paidSold"] = iv(pl, "paidSold()")
pc["hive-pollen"]["lastCheckBlock"] = READ_BLOCK; pc["hive-pollen"]["lastCheckWib"] = NOW_WIB
# ---- Track-C blocked leads: fresh read, status unchanged ----
tc = json.load(open(B + "run-2026-11-02-0901-trackc-read.json"))
snap["track_c"]["BIAO"]["lastReadBlock"] = tc["block"]; snap["track_c"]["BIAO"]["lastReadWib"] = NOW_WIB
snap["track_c"]["BIAO"]["phase"] = tc["BIAO_phase()"]; snap["track_c"]["BIAO"]["freeClaimed_total"] = tc["BIAO_freeClaimed()"]
snap["track_c"]["BIAO"]["sold"] = tc["BIAO_sold()"]
snap["track_c"]["BNBbaby"]["sharesMinted"] = tc["BNBbaby_sharesMinted()"]
snap["track_c"]["BNBbaby"]["freeMinted"] = tc["BNBbaby_freeMinted()"]
snap["track_c"]["BNBbaby"]["lastReadBlock"] = tc["block"]; snap["track_c"]["BNBbaby"]["lastReadWib"] = NOW_WIB
snap["timestamp_wib"] = NOW_WIB
snap["note"] = ("Run 09:01 WIB: 6 strong-lead direct mints (Lensorb #392, Hotpotsage #398, Plutopop #516, "
 "Ghoulipop #541, Servobun #517, Xianyulo #507); 2 new early leads (Vesperfang, Ioforge); "
 "track-C blocked leads BIAO/BNBbaby unchanged (not retried, not re-reported); track-B pending still NOT open. "
 "Scan leg + route 5c pending at snapshot write time (handoff amends).")
json.dump(snap, open(B + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "timestamp:", NOW_WIB)
for n in ["Lensorb","Hotpotsage","Plutopop","Ghoulipop","Servobun","Xianyulo","Vesperfang","Ioforge"]:
    e = snap["contracts"][n]
    print(n, e["status"], e.get("totalSupply"), e.get("freeClaimed"), "/", e.get("FREE_SUPPLY"), e.get("freePctVerified"))
