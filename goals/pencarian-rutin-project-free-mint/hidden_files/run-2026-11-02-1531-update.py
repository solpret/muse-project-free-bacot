#!/usr/bin/env python3
"""Main run 2026-11-02 15:31 WIB snapshot update."""
import json, shutil, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-1531.bak.json")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-1531-read.json"))
READ_BLOCK = read["block"]  # 131210365
READ_WIB = "2026-11-02T15:40:00+07:00"
INTERVAL_MIN = 23  # snapshot lastRead 15:16:59 -> read ~15:40
GEN = {
    "totalSupply()": "totalSupply", "freeClaimed()": "freeClaimed",
    "FREE_SUPPLY()": "FREE_SUPPLY", "freeMinted()": "freeMinted",
    "freeLeft()": "freeLeft", "mintedBy(address)": "userMintedBy",
    "freeUsed(address)": "userFreeUsed", "balanceOf(address)": "userBalance",
}
vel_pass = []
for name, v in snap["contracts"].items():
    if name not in read or not isinstance(v, dict):
        continue
    if str(v.get("status", "")).startswith("minted-by-user"):
        continue
    r = read[name]
    old_ts = v.get("totalSupply")
    for rk, sk in GEN.items():
        if r.get(rk) is not None:
            v[sk] = r[rk]
    fc, fs, fm, fl = r.get("freeClaimed()"), r.get("FREE_SUPPLY()"), r.get("freeMinted()"), r.get("freeLeft()")
    pct = None
    if fc is not None and fs:
        pct = round(100 * fc / fs, 2)
    elif fm is not None and fl is not None and (fm + fl):
        pct = round(100 * fm / (fm + fl), 2)
    if pct is not None:
        v["freePctVerified"] = pct
    new_ts = r.get("totalSupply()")
    if old_ts is not None and new_ts is not None:
        delta = new_ts - old_ts
        rate = round(delta / INTERVAL_MIN, 3)
        prev = v.get("lastRateTokensPerMin")
        v["previousRatePerMin"] = prev
        v["lastRateTokensPerMin"] = rate
        v["mintedInInterval"] = delta
        v["intervalMinutes"] = INTERVAL_MIN
        passed = bool(prev) and rate >= 1.5 * prev and delta >= 20
        v["velocityLegPasses"] = passed
        if passed:
            vel_pass.append((name, delta, rate, prev))
    v["lastReadBlock"] = READ_BLOCK
    v["lastReadWib"] = READ_WIB
print("velocity passes this run:", vel_pass)

# Track-B pending
pc = snap["pending_claims"]
pc["binanceai.fun"].update({"totalShares": 3108, "lastReadBlock": READ_BLOCK, "lastReadWib": READ_WIB})
pc["hive-pollen"].update({"pollenAgents": 7736, "paidSold": 1035, "lastReadBlock": READ_BLOCK, "lastReadWib": READ_WIB})

# Track-C watchlist numbers from the same read
tc = snap["track_c"]
def upd(key, patch):
    if key in tc and isinstance(tc[key], dict):
        tc[key].update(patch)
        tc[key]["lastReadBlock"] = READ_BLOCK
        tc[key]["lastReadWib"] = READ_WIB
upd("QAGENT", {"freeMinted_note": "18/6666 at 15:31 run read"})
upd("QAGENT-2", {
    "status": "minted-by-user-2026-11-02",
    "userSlot": {"freeAvailable": 0, "freeClaimed": 1, "mintedBy": 1,
                 "note": "Slot flipped by parent execution 2026-11-02 ~15:40 WIB (tx 0xb3ced5e8d37b6703d278d76318e086c8a8596a972ff2bef058d2d4cb70bed3b6, block 131210329; balance 0 -> 10,000,000 QAGENT). This run only records the change; it was already reported by the parent, NOT re-reported here."},
})
# QAGENT-2 fresh numbers from read (freeMinted 4507 at block 131210365, pre-mint read was 4480 at 131210221; post-mint read shows slot used)
tc["QAGENT-2"]["freeMinted_last"] = 4507

# New early leads (track A, never previewed/minted)
new_leads = {
    "Chihuolin": {"address": "0x656A1115BEd8E60748508C423e81FA85AA9c762F", "symbol": "CHIHU", "kind": "ERC721",
                  "totalSupply": 54, "freeClaimed": 49, "FREE_SUPPLY": 4354, "freePctVerified": 1.13,
                  "mintOpen": True, "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
                  "firstSeenBlock": 131209923, "firstMintWib": "2026-11-02 15:35:35 WIB",
                  "status": "early-lead-reported-2026-11-02", "lastReadBlock": READ_BLOCK, "lastReadWib": READ_WIB,
                  "velocityLegPasses": False, "xVerified": False,
                  "baselineNote": "EARLY lead reported once run 15:31 WIB (main job, via Sourcify feed shape-check). Never auto-minted/previewed. Agent-shape: Sourcify-verified ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + AGENT_ID registry ref). First mint verified on-chain: 54 Transfer-from-zero logs = totalSupply 54, 49 minters, first block 131209923. Slot open by read (mintedBy 0, freeUsed 0, balance 0, quote(user,1)=0). S1-literal NFT, NOT a track-C sale (Sevaris precedent)."},
    "Bandagrin": {"address": "0x6834a0b5d3bAb31A6d9A5505C2a9534daF46DbaF", "symbol": "BANDA", "kind": "ERC721",
                  "totalSupply": 50, "freeClaimed": 45, "FREE_SUPPLY": 4011, "freePctVerified": 1.12,
                  "mintOpen": True, "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
                  "firstSeenBlock": 131209811, "firstMintWib": "2026-11-02 15:34:45 WIB",
                  "status": "early-lead-reported-2026-11-02", "lastReadBlock": READ_BLOCK, "lastReadWib": READ_WIB,
                  "velocityLegPasses": False, "xVerified": False,
                  "baselineNote": "EARLY lead reported once run 15:31 WIB (main job, via Sourcify feed shape-check). Never auto-minted/previewed. Agent-shape: Sourcify-verified ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + AGENT_ID registry ref). First mint verified on-chain: 50 logs = totalSupply 50, 45 minters, first block 131209811. Slot open by read. S1-literal NFT, NOT a track-C sale."},
    "Pyrevane": {"address": "0xFb8b2865727D7e7b8F8761cDC0cA0DE4E7f4e551", "symbol": "PYREV", "kind": "ERC721",
                 "totalSupply": 55, "freeClaimed": 55, "FREE_SUPPLY": 4173, "freePctVerified": 1.32,
                 "mintOpen": True, "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
                 "firstSeenBlock": 131208300, "firstMintWib": "2026-11-02 15:23:25 WIB",
                 "status": "early-lead-reported-2026-11-02", "lastReadBlock": READ_BLOCK, "lastReadWib": READ_WIB,
                 "velocityLegPasses": False, "xVerified": False,
                 "baselineNote": "EARLY lead reported once run 15:31 WIB (main job, via on-chain scan route 4). Never auto-minted/previewed. Agent-shape: Sourcify-verified ABI + registry-bytes hit + free views. Scan-window first block 131208346 corrected by pre-window check: 1 log at 131208300 (15:23:25 WIB) is the true first mint; 0 logs in 131100000-131149999. Slot open by read (mintedBy 0, freeUsed 0, balance 0, quote(user,1)=0)."},
    "Spectrelle": {"address": "0xC2C955bf4FD205939cE70c86324659E6B416D742", "symbol": "SPECT", "kind": "ERC721",
                  "totalSupply": 45, "freeClaimed": 45, "FREE_SUPPLY": 4004, "freePctVerified": 1.12,
                  "mintOpen": True, "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
                  "firstSeenBlock": 131208286, "firstMintWib": "2026-11-02 15:23:19 WIB",
                  "status": "early-lead-reported-2026-11-02", "lastReadBlock": READ_BLOCK, "lastReadWib": READ_WIB,
                  "velocityLegPasses": False, "xVerified": False,
                  "baselineNote": "EARLY lead reported once run 15:31 WIB (main job, via on-chain scan route 4). Never auto-minted/previewed. Agent-shape: Sourcify-verified ABI + registry-bytes hit + free views. Scan-window first block 131208349 corrected by pre-window check: 3 logs before window, earliest 131208286 (15:23:19 WIB) is the true first mint; 0 logs in 131100000-131149999. Slot open by read."},
}
for k, v in new_leads.items():
    snap["contracts"][k] = v

# Excluded (never reported as leads; recorded so later runs do not re-detect them as new)
snap.setdefault("excluded", {})
snap["excluded"]["Gondolux"] = {
    "address": "0xd37af310f2da74c8babe301f2a8f8494f40e0c14", "symbol": "GONDOLUX", "track": "A",
    "status": "excluded-age-over-48h-2026-11-02",
    "note": "Boltbook post presented it as fresh (block 131210071), but on-chain first mint is block 130573157, 2026-10-30 07:58:37 WIB (bracketed by 0 logs in 130400000-130500000 and 130500000-130550000; 103 logs in 130500000-130573964) -> age ~3d8h at run, OVER 48h, not sold out (free 2969/4000 = 74.23% at block 131212737, slot open, mintOpen 1). Age rule excludes it; website also unverified (methods A/B/C/D/E/F/G: raw address + name search no site, Boltbook post no site link, Sourcify ABI no URL, same-family no evidence, owner 0x190f factory group, no handle). NOT reported as a lead/candidate, NOT previewed/minted. Element market mention in the post is a fallback market, not project-website evidence.",
}
snap["excluded"]["WUMPO"] = {
    "sale": "0x493B6BD3fD88DE1D86Ce0DeA45168D2eF8182cAa", "token": "0xf4f075eAdBBa0c6DF22BCA92c43B437D9BDdb040", "symbol": "WUMPO", "track": "C",
    "status": "excluded-age-over-48h-2026-11-02",
    "note": "Website gate WOULD pass (wumpo.monster/skill.md prints sale + token contracts exactly, method G standard) and sale shape S1 passes (Sourcify exact_match, mint + quoteFor + freeSharesAvailable/freeSharesGiven + registry()), free pool 7558/7777 open, user slot open (hasAgentId 1, sharesOf 0, freeSharesAvailable 2, quoteFor(user,1)=(cost 0, freeShares 1)) - BUT age EXCLUDES: first-ever sale mint block 130813800, 2026-10-31 14:03:52 WIB (0 zero-from logs before it back to 130000000; tx to sale contract, mint selector, value 285071772314222 wei) -> ~49.8h at run, OVER 48h. Independently, the 'free' mint is NOT value-0: feeFor(user,1) = 285071772314222 wei (~0.000285 BNB to treasury), so it also fails the value-0 safety condition for track-C auto-mint. NOT reported as a lead/candidate, NOT previewed/minted.",
}
snap["excluded"]["OAGENT"] = {
    "address": "0x60509085Cea233c3Ca1842767379185bFce2b440", "symbol": "OUNIT", "track": "A",
    "status": "excluded-paid-2026-11-02",
    "note": "Boltbook post + site oagent.pages.dev verified, but mint is PAID (first unit 0.0001 BNB + PoW, per the site's own Mint Specs) and totalSupply 6/3333 at read - NOT free gas-only, so excluded from Free Bacot. Not reported as a lead.",
}

snap["timestamp_wib"] = NOW
snap["note"] = ("Run 15:31 WIB: reread block 131210365; no new >=50% promotion (Nightsable 49.87%, NightshadeClub 49.54% still below); "
                 "no new sold-out; no age removals (oldest verified first-seen ~16.7h). New early leads reported once: Chihuolin, Bandagrin (Sourcify feed), "
                 "Pyrevane, Spectrelle (scan triage). Gondolux age-excluded (>48h, first mint 2026-10-30) + website-unverified; WUMPO track-C age-excluded "
                 "(first sale mint 2026-10-31 14:03 WIB) + feeFor > 0; OAGENT paid, excluded. QAGENT-2 slot flipped to minted by parent execution ~15:40 WIB "
                 "(recorded, not re-reported). Scan 15:31: window 131208321-131210320 (2000 cap, gap 131207431-131208320), 221 NFT + 455 ERC-20 contracts, "
                 "34 Ankr calls, 1 chunk error 131209171-131209220 (targeted page-1 retry: 5 mint contracts, none agent-shaped). Route 5c: 20 ERC-20 shape-checked, "
                 "all Sourcify 404, 0 sale shapes. Route 6: Square search-index no site links for Gondolux/WUMPO beyond wumpo.monster (already used); "
                 "Odaily + DappBay fetches failed (browser_open network grant) - legs skipped, not evidence of absence.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(snap["contracts"]), "excluded:", len(snap["excluded"]), "ts:", NOW)

# scan-seen: append first-seen true (7) + chunk-retry new (5)
seen = json.load(open(BASE + "onchain-scan-seen.json"))
sample = next(iter(seen["contracts"].values()), {})
print("seen value sample:", json.dumps(sample)[:300])
for addr, fb, note in [
    ("0xFb8b2865727D7e7b8F8761cDC0cA0DE4E7f4e551", 131208300, "early-lead-reported run 15:31"),
    ("0xC2C955bf4FD205939cE70c86324659E6B416D742", 131208286, "early-lead-reported run 15:31"),
    ("0xC4e48E40E64905B551Eb2D1513C2489421783c43", None, "scan first-seen run 15:31, not agent-shaped (Sourcify unverified, no free shape)"),
    ("0x2802fD9fE3882AE7B0BF03d59bcDA81068719E00", None, "scan first-seen run 15:31, not agent-shaped (verified, no registry/free)"),
    ("0x15F9203687422b9805D2924A06B475435c232d51", None, "scan first-seen run 15:31, not agent-shaped (Sourcify unverified, no free shape)"),
    ("0x74af0f878368e039eb0652C8524Bb8B34a01731C", None, "scan first-seen run 15:31, not agent-shaped"),
    ("0x2b1784a01e6c5fBAE04ECfF0F344E7081E78aFB8", None, "scan first-seen run 15:31, not agent-shaped"),
    ("0x22a2c54b15287472f4adbe7587226e3c998cdd96", None, "chunk-retry 131209171-131209220 run 15:31, plain ERC-20 mint, not agent-shaped"),
    ("0x35803e77c3163fed8a942536c1c8e0d5bf90f906", None, "chunk-retry run 15:31, plain ERC-20 mint, not agent-shaped"),
    ("0x5f84cf68dd0a86b25c46ce3e0e603568f94f2034", None, "chunk-retry run 15:31, plain ERC-20 mint, not agent-shaped"),
    ("0x826923122a8521be36358bdc53d3b4362b6f46e5", None, "chunk-retry run 15:31, plain ERC-20 mint, not agent-shaped"),
    ("0xf1ee33b00f015d955259dc206184fc9e401b741c", None, "chunk-retry run 15:31, Sourcify 404, not agent-shaped on bytecode alone"),
]:
    if addr not in seen["contracts"]:
        entry = {"first_block": fb, "note": note, "run": "2026-11-02-1531"} if isinstance(sample, dict) else note
        seen["contracts"][addr] = entry
json.dump(seen, open(BASE + "onchain-scan-seen.json", "w"), indent=1)
print("scan-seen contracts now:", len(seen["contracts"]))

# scan state
state = json.load(open(BASE + "onchain-scan-state.json"))
state.update({
    "last_scanned_block": 131210320, "last_scan_window_from": 131208321, "last_scan_window_to": 131210320,
    "last_scan_wib": NOW, "ankr_calls": 34, "errors": 1, "nft_contracts": 221, "erc20_mint_contracts": 455,
    "skipped_gap": "131207431-131208320 (890 blocks, 2000-block cap)",
    "note": ("Scan 15:31 run: 221 contracts (window), 455 ERC-20 mint contracts, 34 Ankr calls, 1 chunk error 131209171-131209220 "
             "(Transfer chunk timeout; targeted retry recovered page 1 only: 5 mint contracts, none agent-shaped - residual page-2+ risk noted in run log). "
             "First-seen true: 7 scan + 5 chunk-retry, appended to scan-seen."),
    "last_scan_window": "131208321-131210320", "ankr_calls_last_scan": 34, "errors_last_scan": 1,
    "from_block": 131208321, "to_block": 131210320, "last_scan": NOW, "last_scan_run": "2026-11-02-1531",
    "contracts_in_window": 221, "erc20_mint_contracts_in_window": 455,
})
json.dump(state, open(BASE + "onchain-scan-state.json", "w"), indent=1)

# track-c checked: add 20
chk = json.load(open(BASE + "track-c-scan-checked.json"))
todo = json.load(open(BASE + "run-2026-11-02-1531-trackc-erc20-todo.json"))
for e in todo:
    if e["address"] not in chk["checked"]:
        chk["checked"].append(e["address"])
chk["note"] = "Run 15:31: 20 ERC-20 added (all Sourcify 404, 0 sale shapes); remainder of 68-contract >=10 backlog dropped as sampling limit."
json.dump(chk, open(BASE + "track-c-scan-checked.json", "w"), indent=1)
print("track-c checked now:", len(chk["checked"]))
