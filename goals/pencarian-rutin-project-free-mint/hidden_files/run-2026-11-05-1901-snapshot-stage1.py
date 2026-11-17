#!/usr/bin/env python3
"""Snapshot stage-1 update run 1901: route-1 re-read values + rates, age-exclusions, NJAR/track-C. No subagent results yet."""
import json, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
r19 = json.load(open(f"{BASE}/run-2026-11-05-1901-reread-lean.json"))
age = json.load(open(f"{BASE}/run-2026-11-05-1901-age-probe.json"))
njar = json.load(open(f"{BASE}/run-2026-11-05-1901-njar-probe.json"))
INTERVAL = 46.0  # 18:38:23 -> 19:24:23 WIB per block timestamps 131810135 -> 131816269
BLOCK = r19["block"]
KEYMAP = {"DumpsterRoyalty": "Dumpster Royalty", "SlowSteady": "Slow & Steady",
          "DoNotDisturb": "Do Not Disturb", "MothClub": "Moth Club",
          "MonkeBusiness": "Monke Business", "VeryGoodBoys": "Very Good Boys",
          "SnailMail": "Snail Mail"}
updated, skipped = [], []
for lk, d in r19["reread"].items():
    sk = KEYMAP.get(lk, lk)
    e = snap["contracts"].get(sk)
    if e is None:
        skipped.append(lk); continue
    old_ts = e.get("totalSupply")
    new_ts = d.get("totalSupply")
    if new_ts is None and isinstance(d.get("totalMinted"), int):
        new_ts = d["totalMinted"]  # supply proxy for free-only templates (1831 precedent)
    if new_ts is None and lk == "AgentPass-Dd3c" and isinstance(d.get("freeMinted"), int):
        new_ts = d["freeMinted"]  # free-only template, freeMinted == totalMinted
    if isinstance(new_ts, int):
        e["previousTotalSupply"] = old_ts
        e["totalSupply"] = new_ts
        if isinstance(old_ts, int):
            minted = new_ts - old_ts
            prev_rate = e.get("currentRatePerMin")
            rate = round(minted / INTERVAL, 3)
            e["previousRatePerMin"] = prev_rate
            e["currentRatePerMin"] = rate
            e["mintedInInterval"] = minted
            e["intervalMinutes"] = INTERVAL
            e["velocityLegPasses"] = bool(prev_rate and rate >= 1.5 * prev_rate and minted >= 20)
            e["velocityNote"] = (f"Run 1901: +{minted} in {INTERVAL} min = {rate}/min vs prev {prev_rate} "
                                 f"-> {'PASS' if e['velocityLegPasses'] else 'FAIL'}"
                                 if prev_rate else f"Run 1901: +{minted} in {INTERVAL} min = {rate}/min, first interval baseline, velocity cannot pass")
        e["lastReadBlock"] = BLOCK
        e["lastReadWib"] = "2026-11-05 run 1901"
    else:
        e["lastReadBlock"] = BLOCK
        e["velocityNote"] = "Run 1901: totalSupply/totalMinted read FAILED (null) - old values kept, not zero"
    for f in ("freeClaimed", "freeMinted"):
        if isinstance(d.get(f), int): e[f] = d[f]
    if isinstance(d.get("balanceOf_user"), int): e["balanceOf_user"] = d["balanceOf_user"]
    for f in ("costOf_user_1", "mintsLeft_user", "mintOpen", "mintedBy_user", "price",
              "freeUsed_user", "canFreeMint_user", "claimedFree_user", "quote_user_1"):
        if d.get(f) is not None: e[f] = d[f]
    updated.append(sk)
# free % refresh for the 3 new early leads
kb = snap["contracts"].get("Kitebots")
if kb: kb["freePctVerified"] = round(433/3280*100, 2)
af = snap["contracts"].get("AgentFounder")
if af: af["freePctVerified"] = round(80/222*100, 2)
ap = snap["contracts"].get("AgentPass-Dd3c")
if ap: ap["freePctVerified"] = round(41/222*100, 2)
# age-exclusions (verified fresh this run, block unknown - eth_blockNumber failed, reads OK)
for name in ["Niubimind", "Shogunode", "Botkirin"]:
    e = snap["contracts"].pop(name, None)
    if e is None: continue
    rd = age["reads"][name]
    fc = rd["freeClaimed"]; cap = rd["FREE_SUPPLY_snapshot"]
    pct = round(fc/cap*100, 2) if isinstance(fc, int) else None
    snap.setdefault("excluded", {})[name] = dict(e)
    snap["excluded"][name]["status"] = "excluded-age-over-48h-2026-11-05"
    snap["excluded"][name]["note"] = (f"AGE-EXCLUDED run 1901: first mint {rd['firstMintWib']} (>48h at read ~19:25 WIB 2026-11-05), "
        f"totalSupply {rd['totalSupply']}, freeClaimed {fc}/{cap} = {pct}% (not sold out), mintOpen {rd['mintOpen']}. Removed from contracts per 48h rule, reported once run 1901.")
# Pumpkinagent: NOT yet 48h at read (19:25 WIB; crosses 19:34:09) - keep, flag for next run
pk = snap["contracts"].get("Pumpkinagent")
if pk:
    rd = age["reads"]["Pumpkinagent"]
    pk["note"] = (f"Run 1901: age 47h51m at read 19:25 WIB (first mint {rd['firstMintWib']}, crosses 48h 19:34:09 WIB today); "
                  f"totalSupply {rd['totalSupply']}, freeClaimed {rd['freeClaimed']}/2222 = 41.7%, NOT sold out - next run (1931) to age-exclude if still not sold out.")
    pk["totalSupply"] = rd["totalSupply"]; pk["freeClaimed"] = rd["freeClaimed"]
# track_c: NJAR fresh probe
nj = snap.get("track_c", {}).get("NJAR")
if nj:
    nj["giftsClaimed"] = njar["giftsClaimed"]; nj["giftsLeft"] = 2000 - njar["giftsClaimed"]
    nj["ageNote"] = "VERIFIED <=48h: saleStart on-chain 1793869237 = 2026-11-05 16:00:37 WIB; age ~3h27m at probe block 131816295 (~19:25 WIB)."
    nj["gateNote"] = (nj.get("gateNote","") + " Run 1901: methods (H) contractURI + (I) tokenURI/uri on sale AND token contracts = all null (no URL evidence). "
                      "Gate still FAILED; subagent B re-running name search this run.")
    nj["userSlot"] = {"giftTaken": False, "hasAgentId": True}
q = snap.get("track_c", {}).get("QAGENT-2")
if q: q["sharesMinted"] = 6702  # confirmed run 1901 re-read; free pool still 6666/6666 exhausted
snap["timestamp_wib"] = "2026-11-05 run 1901 (stage1)"
snap["last_run_wib"] = "2026-11-05 run 1901"
snap["last_run"] = "1901"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("updated contracts:", len(updated))
print("skipped (not in snapshot):", skipped)
print("contracts now:", len(snap["contracts"]), "| excluded now:", len(snap.get("excluded", {})))
print("age-excluded this stage: Niubimind, Shogunode, Botkirin")
