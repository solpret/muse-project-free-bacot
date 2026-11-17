#!/usr/bin/env python3
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-03-0131-read.json"))
rd = json.load(open(BASE + "run-2026-11-03-0131-river-deco.json"))
READ_BLOCK = read["block"]  # 131289528
INTERVAL_MIN = 30.0  # lastRead ~01:03 WIB -> route1 read ~01:33 WIB
for name, v in snap["contracts"].items():
    if str(v.get("status", "")).startswith("minted-by-user"):
        continue
    r = read.get(name)
    if not r:
        continue
    old_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply()")
    if new_ts is not None:
        if old_ts is not None and new_ts != old_ts:
            prev_rate = v.get("currentRatePerMin")
            rate = round((new_ts - old_ts) / INTERVAL_MIN, 3) if new_ts > old_ts else 0.0
            v["previousTotalSupply"] = old_ts
            v["mintedInInterval"] = new_ts - old_ts
            v["intervalMinutes"] = INTERVAL_MIN
            if prev_rate is not None:
                v["previousRatePerMin"] = prev_rate
            v["currentRatePerMin"] = rate
            v["velocityLegPasses"] = bool(prev_rate and prev_rate > 0 and rate >= 1.5 * prev_rate and (new_ts - old_ts) >= 20)
        v["totalSupply"] = new_ts
    fc = r.get("freeClaimed()"); fs = r.get("FREE_SUPPLY()")
    if fc is not None: v["freeClaimed"] = fc
    if fs is not None: v["FREE_SUPPLY"] = fs
    if fc is not None and fs: v["freePctVerified"] = round(100 * fc / fs, 2)
    mb = r.get("mintedBy(address)"); fu = r.get("freeUsed(address)"); bal = r.get("balanceOf(address)")
    if mb is not None: v["userMintedBy"] = mb
    if fu is not None: v["userFreeUsed"] = fu
    if bal is not None: v["userBalance"] = bal
    v["lastReadBlock"] = READ_BLOCK
    v["lastReadWib"] = "2026-11-03T01:33:00+07:00"
# River / Deco / Aura / Moth extra reads (block 131289715, ~28 min after 01:05 read)
for name in ["River Agent", "Deco Agent", "Aura Agents", "Moth Agent"]:
    v = snap["contracts"].get(name)
    if not v: continue
    d = rd[name]
    tm = d.get("totalMinted()"); ts = d.get("totalSupply()")
    new_total = tm if tm is not None else ts
    old_total = v.get("totalMinted") if v.get("totalMinted") is not None else v.get("totalSupply")
    if new_total is not None and old_total is not None and new_total != old_total:
        prev_rate = v.get("currentRatePerMin")
        rate = round((new_total - old_total) / 28.0, 3)
        v["previousTotalSupply"] = old_total
        v["mintedInInterval"] = new_total - old_total
        v["intervalMinutes"] = 28.0
        if prev_rate is not None: v["previousRatePerMin"] = prev_rate
        v["currentRatePerMin"] = rate
        v["velocityLegPasses"] = bool(prev_rate and prev_rate > 0 and rate >= 1.5 * prev_rate and (new_total - old_total) >= 20)
        v["totalMinted"] = tm if tm is not None else v.get("totalMinted")
        if ts is not None: v["totalSupply"] = ts
    if d.get("FREE_SUPPLY()") is not None: v["FREE_SUPPLY"] = d["FREE_SUPPLY()"]
    if d.get("mintedBy(address)") is not None: v["userMintedBy"] = d["mintedBy(address)"]
    v["lastReadBlock"] = 131289715
    v["lastReadWib"] = "2026-11-03T01:33:00+07:00"
# Neonpurrix sold out -> remove
removed = []
if "Neonpurrix" in snap["contracts"]:
    del snap["contracts"]["Neonpurrix"]; removed.append("Neonpurrix (sold out 1797/1797)")
# Fangcount -> strong lead, gate-blocked (website NOT found via A-G)
f = snap["contracts"]["Fangcount"]
f["status"] = "strong-lead-gate-blocked-2026-11-03"
f["gateNote"] = ("Gate website-only FAILED 2026-11-03 01:33 WIB: (A) raw contract-address search -> unrelated results only; "
  "(B) Boltbook front pages (hot-leg 01:34 read) contain no 0x75A2 post; main-run Boltbook fetch failed (RemoteDisconnected) but hot-leg read is the complement; "
  "(C) Sourcify stdJson contains no URLs; (D) no same-family site pattern surfaced; (E) deployer group = same owner() as Crtdroid (factory-wave pattern, not exempt); "
  "(G) project-name search 'Fangcount' -> no project site. X optional, not a blocker. NOT previewed, NOT minted.")
f["strongLeadNote"] = ("Promoted 2026-11-03 01:33 WIB: (a) age VERIFIED first mint 2026-11-02 10:48:42 WIB (~14.7h); "
  "(b) freeClaimed 436/866 = 50.35% verified free view; (c) slot open mintedBy=0, freeUsed=0, quote(user,1)=0, mintOpen=1. Block 131289528.")
# River Agent -> strong lead (inference %), gate-blocked
rv = snap["contracts"]["River Agent"]
rv["status"] = "strong-lead-gate-blocked-2026-11-03"
rv["gateNote"] = ("Gate website-only FAILED 2026-11-03 01:33 WIB: (A) raw contract-address search -> unrelated River tokens only; "
  "(B) Boltbook front pages (hot-leg 01:34) contain no 0x211A post; (C) Sourcify stdJson contains no URLs; (D) no same-family site pattern surfaced; "
  "(E) factory-template deployer group; (G) project-name search 'River Agent' -> unrelated River protocol only. X optional, not a blocker. NOT previewed, NOT minted.")
rv["strongLeadNote"] = ("Promoted 2026-11-03 01:33 WIB: (a) age VERIFIED first mint 2026-11-03 00:31:21 WIB (~1h); "
  "(b) totalMinted 156/271 FREE_SUPPLY = 57.57% INFERENCE ONLY (no freeClaimed view; costFor(1)=0 supports free lane, but totalMinted may include paid mints — NOT a verified free counter); "
  "(c) slot open mintedBy=0, costFor(1)=0. Block 131289715. Velocity also passes this interval (+83 in ~28 min, 2.96/min vs prior 1.2/min) but gate blocks execution.")
# Hongbao track-C lead, gate-blocked
snap.setdefault("track_c", {})["Hongbao-HONGBAO"] = {
  "sale": "0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97",
  "token": "0xcdce49721d2fed646d4c1a34a51ec001cd879449",
  "name": "Hongbao", "symbol": "HONGBAO", "kind": "ERC20 share sale S1",
  "status": "lead-gate-blocked-recorded-2026-11-03",
  "saleShape": "PASS (S1): mint(uint256) + quote(uint256) pure + freeClaimed/freeClaimedBy/freeSharesGiven + agentRegistry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact, Sourcify verified (verifiedAt 2026-11-02T18:26:21Z, NOT launch time)",
  "mintOpen": 1, "TOTAL_SHARES": 10000, "totalSharesSold": 6, "freeClaimed": 6, "freeSharesGiven": 6,
  "PRICE_paid": "0.001 BNB", "TOKENS_PER_SHARE": "50000 HONGBAO", "MAX_SHARES_PER_WALLET": 10,
  "deadlineWib": "2026-11-09T11:56:05+07:00",
  "userSlot": "hasAgentId(user)=1, freeClaimedBy(user)=false, sharesOf(user)=0, quote(0)=0",
  "freePoolNote": "No FREE_SHARES/freeRemaining view in ABI; free pool inferred open: TOTAL_SHARES 10000 vs totalSharesSold 6, mintOpen=1, user free slot open — inference, not a verified free-remaining counter.",
  "launchNote": "First Claimed event block 131180684 = 2026-11-02 11:56:14 WIB (Ankr getLogs, 6 Claimed logs total, matching totalSharesSold 6); age ~13.6h at 01:33 WIB, VERIFIED <=48h.",
  "gateNote": ("Gate website-only FAILED 2026-11-03: (A) raw sale/token address search -> no project site; (B) Boltbook front pages (hot-leg 01:34) contain no 0x834e/0xcdce post; "
    "(C) Sourcify metadata contains no URLs; (G) project-name search 'Hongbao HONGBAO agent' -> only unrelated Solana HONGBAO + Binance Red Packet articles. X optional, not a blocker. NOT previewed, NOT minted."),
  "lastReadBlock": 131290095, "lastReadWib": "2026-11-03T01:33:00+07:00"}
snap["timestamp_wib"] = "2026-11-03T01:33:00+07:00"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "removed:", removed)
print("Fangcount:", snap["contracts"]["Fangcount"]["status"], snap["contracts"]["Fangcount"].get("freePctVerified"))
print("River:", snap["contracts"]["River Agent"]["status"], "rate", snap["contracts"]["River Agent"].get("currentRatePerMin"), "vel", snap["contracts"]["River Agent"].get("velocityLegPasses"))
print("Deco totalMinted:", snap["contracts"]["Deco Agent"].get("totalMinted"), "vel", snap["contracts"]["Deco Agent"].get("velocityLegPasses"))
