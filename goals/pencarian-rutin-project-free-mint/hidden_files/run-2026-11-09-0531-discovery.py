#!/usr/bin/env python3
"""LEG B discovery run 2026-11-09-0531 (Routes 2/3/5a/6). READ-ONLY.
Builds run-2026-11-09-0531-discovery.json from this run's artefacts.
Does NOT write onchain-snapshot.json / onchain-scan-state.json /
onchain-scan-seen.json / track-c-scan-checked.json / scan-bridge.json.
"""
import json, re, os, sys
sys.set_int_max_str_digits(100000)
HF = os.path.dirname(os.path.abspath(__file__))
RUN = "2026-11-09-0531"
snap = json.load(open(os.path.join(HF, "onchain-snapshot.json")))
known = {v.get("address", "").lower(): k for k, v in snap.get("contracts", {}).items() if isinstance(v, dict)}
known_tc = {}
for k, v in snap.get("track_c", {}).items():
    if isinstance(v, dict):
        for f in ("address", "sale", "token"):
            if v.get(f):
                known_tc[str(v[f]).lower()] = k
disc = json.load(open(os.path.join(HF, "same-owner-discards.json")))
disc_contracts = {e.get("contract", "").lower() for e in disc}
disc_owners = {e.get("owner", "").lower() for e in disc}

def addrs_in(path):
    html = open(os.path.join(HF, path), encoding="utf-8", errors="ignore").read()
    return sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", html)))

bolt = {}
for tag in ("en", "zh"):
    a = addrs_in(f"run-{RUN}-boltbook-{tag}.html")
    bolt[tag] = [{"address": x, "in_snapshot": x.lower() in known or x.lower() in known_tc,
                  "snapshot_name": known.get(x.lower()) or known_tc.get(x.lower())} for x in a]
feed = json.load(open(os.path.join(HF, f"run-{RUN}-sourcify-feed.json")))
sourcify = [{"address": r["address"], "verifiedAt": r.get("verifiedAt"), "match": r.get("match"),
             "in_snapshot": r["address"].lower() in known or r["address"].lower() in known_tc}
            for r in feed.get("results", [])]
shape = json.load(open(os.path.join(HF, f"run-{RUN}-shape.json")))
shape_hits = [s for s in shape if s.get("S1") or s.get("S2")]
verify = json.load(open(os.path.join(HF, f"run-{RUN}-verify.json")))
verify2 = json.load(open(os.path.join(HF, f"run-{RUN}-verify2.json")))
bridge = json.load(open(os.path.join(HF, "scan-bridge.json")))
bridge_contracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
bridge_new = [a for a in bridge_contracts
              if a.lower() not in known and a.lower() not in known_tc]
bridge_discarded = [a for a in bridge_contracts
                    if bridge_contracts[a].get("same_owner_discarded")]
out = {
 "run": RUN, "leg": "B", "routes": ["2-boltbook", "3-web-social-sweep", "5a-sourcify", "6-odaily-panews-binance-square"],
 "read_only": True, "no_execution": True,
 "snapshot_contracts": len(known), "snapshot_track_c": len(snap.get("track_c", {})),
 "boltbook": {"en_file": f"run-{RUN}-boltbook-en.html", "zh_file": f"run-{RUN}-boltbook-zh.html",
              "en": bolt["en"], "zh": bolt["zh"],
              "unique_addresses": len({x["address"].lower() for x in bolt["en"] + bolt["zh"]}),
              "new_vs_snapshot": sorted({x["address"] for x in bolt["en"] + bolt["zh"]
                                          if not x["in_snapshot"]})},
 "sourcify_feed": {"file": f"run-{RUN}-sourcify-feed.json", "n": len(sourcify), "entries": sourcify,
                   "new_vs_snapshot": len([s for s in sourcify if not s["in_snapshot"]])},
 "shape_hits": shape_hits,
 "bridge": {"contracts": len(bridge_contracts), "new_vs_snapshot": bridge_new,
            "same_owner_discarded": len(bridge_discarded),
            "note": "bridge mtime unchanged 2026-11-08 18:21 UTC; read-only, never written by this job"},
 "leads": [
  {"project": "BAHUANG3 / 八荒神兽·八部众·史 (Shanhaijing Beasts Season 3)",
   "contract": "0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591",
   "type": "ERC-721 NFT, agent-gated free mint (S1-shaped ABI: mint+quote+freeMinted/freeCount/freeAllowance+agentId registry)",
   "source": "Sourcify recently-verified feed (verified 2026-11-08 22:30:20Z) + on-chain scan window 132475203-132476202 cross-check (127 mints / 32 minters in window, first block 132475336)",
   "shape": "FREE_CAP 6000, PAID_CAP 3000, freeMint/freeMinted/freeCount/freeAllowance, mint/mintStart/mintEnd, agentId()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, payout 0x45e2c8a09022914ce00cfce9a93dd3fda54d8686 (same payout wallet as BHTB — same author dq2.ai), Sourcify exact_match",
   "onchain_block": verify.get("block"), "name": "八荒神兽·八部众·史", "symbol": "BAHUANG3",
   "free_cap": 6000, "free_minted": 412, "total_minted": 412, "free_pct": round(412 / 6000 * 100, 1),
   "paid_count": 0, "free_allowance_user": 2, "user_slot": "OPEN (freeAllowance(agent wallet)=2, balance 0)",
   "mint_start_wib": "2026-11-09 05:29:50", "mint_end_wib": "2026-11-14 05:29:50",
   "first_mint_block": 132474152, "first_mint_wib": "2026-11-09 05:40:07",
   "launch_age_at_read": "~50 min (VERIFIED via mintStart on-chain + first-mint block 132474152)",
   "token_uri": "https://arweave.net/DM7ayfWzaANA2YZgmwKUm_Td5N3k15lzRB8CFPH631U/{n}.json (metadata: Shanhaijing beast cards, e.g. 帝江/毕方; NO external_url/website field)",
   "website_gate": "NOT PASSED - no project website found (methods A,G,H,I,C,B,N tried; method L BscScan token-info via live browser delegated, result pending at discovery build; see run log)",
   "x_status": "not found", "same_owner_discard": False,
   "payout_in_discards": False,
   "classification": "EARLY LEAD - first mints verified on-chain this run, agent-shaped, age verified ~50 min, free 6.9%, slot user OPEN; website gate NOT passed -> TIDAK preview/mint; velocity not yet computable (first baseline this run)"},
  {"project": "Compasyn (CMPN) — BLOCKED, not a lead",
   "contract": "0xcd1bb8013e924e26ed4131a69304f2969c4f8d28",
   "type": "ERC-721 NFT, agent-gated free mint (S1-shaped ABI)",
   "source": "Boltbook front page EN+ZH, posts by cskh.ai (recheck block 132,475,490) + hooya.ai (free mint #127, tx block 132,459,053)",
   "shape": "mint+quote+freeClaimed/freeFor/freeLeft/freeUsed, FREE_SUPPLY 1490, MAX_SUPPLY 2129, AGENT_ID registry, PRICE 0.00006 BNB constant, Sourcify match (NOT exact_match)",
   "onchain_block": verify.get("block"), "name": "Compasyn", "symbol": "CMPN",
   "total_supply": 520, "free_claimed": 515, "free_supply": 1490, "free_pct": round(515 / 1490 * 100, 1),
   "mint_open": 1, "free_per_wallet": 1, "quote_user_1": 0, "free_used_user": 0,
   "user_slot": "OPEN by read (quote 0, freeUsed 0, balance 0) — IRRELEVANT, blocked below",
   "first_mint_block": 131395780, "first_mint_wib": "2026-11-03 14:49:54",
   "launch_age_at_read": "~5 days 15.5 h — AGE-EXCLUDED (>48 h)",
   "owner": "0x310cea29c4827efc82b1d7ff4c70b7332d236917",
   "same_owner_discard": True,
   "discard_detail": "owner 0x310c... is the same owner as Neuroveil 0x7BCA844AD4cD95b5B30ecC3885dfBab45F38e99b and Homunqul 0x5539dD54c00094Cbd186f08AA2d8fF3A8c098ddE, both discarded 2026-11-03 as same-owner cluster",
   "website_gate": "NOT PASSED - no project website found (methods A,G,H,I,C,B tried; hooya.ai post itself states 'No official site/X publishes this contract')",
   "x_status": "not found",
   "classification": "BLOCKED on THREE independent grounds: (1) same-owner discard — STOP per mandatory pre-preview discards check, never preview/execute; (2) age-excluded ~5.7 days > 48 h; (3) website gate NOT passed. Recorded in snapshot as promotion-discarded-same-owner-2026-11-09 so later runs do not re-report. Reported once as blocked, never as a lead."},
 ],
 "dead_or_closed": [
  {"project": "Piggy Agent", "site": "https://piggyagent.space/", "status": "NOT LAUNCHED (0/10,000 minted) + in body excluded list (already checked) - not re-added, not reported as lead"},
  {"project": "Believers", "site": "https://believers-virid.vercel.app/#/docs", "status": "SOLD OUT 1,111/1,111, mint closed - dead, not in snapshot, not reported"},
  {"project": "Agent Zet", "contract": "0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37", "status": "free phase complete 4,000/4,000 (paid only) - known, not re-reported"},
  {"project": "MOLT AGENT", "contract": "0x4B8150f1a258cD3CE2300fAf682432c52ca48Fc1", "status": "already in snapshot - known"},
  {"project": "Nidavellir", "contract": "0xd527109571b039298b65bCB26313dcbED0978c97", "status": "already in snapshot - known"},
 ],
 "sweep_notes": [
  {"project": "AgentForge", "contract": "0xf11ea7f1a9768bce1622c9a04f00d5f7da1e8c16", "status": "Binance Square post 2026-10-27 (12 days old) - known/old, not a new lead"},
  {"project": "Pixel Fox", "contract": "0x9134ae94ab0739cf0e0f4f5e9cacfa5e1d029b0c", "status": "Square post 2026-10-25 (14 days old) - known/old"},
  {"project": "PocketDragons", "contract": "0x2cff830264343f29d4924160096f1271a8a14ace", "status": "Square post 2026-10-24 (15 days old) - known/old"},
  {"project": "AgentVOLT", "contract": "0xc58ecec1437777061134c1bddf0ed5ea6eafabf4", "status": "watch note from run 0501 (Boltbook post 2 days old, 1,049/10,000) - not re-checked this run (timebox)"},
 ],
 "route6": {"odaily_panews": "no Odaily/PANews item surfaced in news-vertical search this run; direct newsflash fetch not done (timebox)",
            "binance_square": "hits were old (AgentForge/Pixel Fox/PocketDragons Oct 24-27); no new Square lead",
            "status": "PARTIAL"},
 "not_rechecked_per_instructions": ["binanceai.fun pending claim (refund phase, already reported once)"],
 "same_owner_discards_checked": {"discard_owner_count": len(disc_owners), "flagged": ["Compasyn owner 0x310cea29c4827efc82b1d7ff4c70b7332d236917 (Neuroveil/Homunqul cluster)"]},
 "files_written": [
   f"run-{RUN}-boltbook-en.html", f"run-{RUN}-boltbook-zh.html",
   f"run-{RUN}-sourcify-feed.json", f"run-{RUN}-shape.json",
   f"run-{RUN}-verify.json", f"run-{RUN}-verify2.json",
   f"run-{RUN}-compasyn-post1.html", f"run-{RUN}-compasyn-post2.html",
   f"run-{RUN}-discovery.py", f"run-{RUN}-discovery.json"],
}
json.dump(out, open(os.path.join(HF, f"run-{RUN}-discovery.json"), "w"), indent=1)
print("boltbook unique:", out["boltbook"]["unique_addresses"], "new:", out["boltbook"]["new_vs_snapshot"])
print("sourcify n:", out["sourcify_feed"]["n"], "shape hits:", len(shape_hits))
print("bridge:", out["bridge"]["contracts"], "contracts,", len(bridge_new), "new vs snapshot,", len(bridge_discarded), "same_owner_discarded")
print("leads:", len(out["leads"]))
