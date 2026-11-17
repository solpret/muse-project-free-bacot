#!/usr/bin/env python3
"""LEG B discovery run 2026-11-09-0501 (Routes 2/3/5a/6). READ-ONLY.
Rebuilds run-2026-11-09-0501-discovery.json from the artefacts saved by this run.
Does NOT write onchain-snapshot.json / onchain-scan-state.json / onchain-scan-seen.json /
track-c-scan-checked.json / scan-bridge.json.
"""
import json, re, os
HF = os.path.dirname(os.path.abspath(__file__))
RUN = "2026-11-09-0501"
snap = json.load(open(os.path.join(HF, "onchain-snapshot.json")))
known = {v.get("address", "").lower(): k for k, v in snap.get("contracts", {}).items() if isinstance(v, dict)}
disc = json.load(open(os.path.join(HF, "same-owner-discards.json")))
disc_contracts = {e.get("contract", "").lower() for e in disc}
disc_owners = {e.get("owner", "").lower() for e in disc}

def addrs_in(path):
    html = open(os.path.join(HF, path), encoding="utf-8", errors="ignore").read()
    return sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", html)))

bolt = {}
for tag in ("en", "zh"):
    a = addrs_in(f"run-{RUN}-boltbook-{tag}.html")
    bolt[tag] = [{"address": x, "in_snapshot": x.lower() in known,
                  "snapshot_name": known.get(x.lower())} for x in a]
feed = json.load(open(os.path.join(HF, f"run-{RUN}-sourcify-feed.json")))
sourcify = [{"address": r["address"], "verifiedAt": r.get("verifiedAt"), "match": r.get("match"),
             "in_snapshot": r["address"].lower() in known} for r in feed.get("results", [])]
bhtb = json.load(open(os.path.join(HF, f"run-{RUN}-bhtb-onchain.json")))
grid = json.load(open(os.path.join(HF, f"run-{RUN}-sourcify-651302-onchain.json")))
novra = json.load(open(os.path.join(HF, f"run-{RUN}-novra-onchain.json")))
out = {
 "run": RUN, "leg": "B", "routes": ["2-boltbook", "3-web-social-sweep", "5a-sourcify", "6-odaily-panews-binance-square"],
 "read_only": True, "no_execution": True,
 "snapshot_contracts": len(known),
 "boltbook": {"en_file": f"run-{RUN}-boltbook-en.html", "zh_file": f"run-{RUN}-boltbook-zh.html",
              "en": bolt["en"], "zh": bolt["zh"],
              "unique_addresses": len({x["address"].lower() for x in bolt["en"] + bolt["zh"]}),
              "new_vs_snapshot": sorted({x["address"] for x in bolt["en"] + bolt["zh"] if not x["in_snapshot"]})},
 "sourcify_feed": {"file": f"run-{RUN}-sourcify-feed.json", "n": len(sourcify), "entries": sourcify,
                   "new_vs_snapshot": len([s for s in sourcify if not s["in_snapshot"]]),
                   "agent_sale_shape": ["0x651302C0043040D48EaAF85605E12F0549aD6D89"],
                   "false_positive_lp_mint": ["0x0A155877Bfb70C302F6E884F8cdF9F8cC6Eb3Cbc","0x26950B15026FC27c6805F3d058e28E96A6389842",
                     "0x42F9d7793aFC9940503b17D4Bfa0adc67dBAAC42","0x98B98198646589175582403D22d333D4464d83d9",
                     "0x9a67C0a41B0F775Ee79F9d0398235A7aBf531C46","0xD79158E72998f3464dA948063AF93C8838f5Df02"]},
 "leads": [
  {"project": "BHTB / 八荒通宝", "contract": "0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467",
   "type": "S2 single-contract token+sale (GenesisToken)", "source": "Boltbook front page, post /p/i9mUcPlR2mOr by dq2.ai, ~05:04 WIB 2026-11-09 (4m ago at fetch), 9 upvotes",
   "author_disclosure": "author states it is their human's own project; paid BNB goes to their wallet",
   "shape": "mintGenesis(shares,agentId,referrerAgentId) payable; quote(shares,wallet); freeClaimed(address); FREE_QUOTA/FREE_TOKENS; agentIdRegistry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; mintEnd(); no owner() fn; Sourcify exact_match",
   "onchain_block": bhtb.get("block"), "name": "八荒通宝", "symbol": "BHTB", "decimals": 18,
   "free_quota": 555, "free_used": 28, "free_remaining": 527, "free_per_share": 5555,
   "paid_price_per_share_bnb": 0.002, "paid_quota": 5000, "paid_sold": 0,
   "quote_1_agent_wallet_wei": 0, "free_claimed_agent_wallet": False, "max_shares_agent_wallet": 10,
   "remaining_shares_agent_wallet": 10, "user_slot": "OPEN (verified on-chain)",
   "start_wib": "2026-11-08 18:44", "mint_end_wib_onchain": "2026-11-13 18:44",
   "mint_end_wib_post_claim": "2026-11-13 19:44 (post text; on-chain 18:44 wins)",
   "launch_age_at_read": "~10.6h", "velocity_note": "post said 23 claimed ~05:04 WIB; on-chain 28 at block 132470505 (~05:20 WIB): +5 in ~16 min post-publicity; 28 total in ~10.6h",
   "payout": "0x45e2c8a09022914ce00cfce9a93dd3fda54d8686", "dev_locked": "19,141,975 BHTB", "lock_until_wib": "2027-11-08 18:44",
   "website_gate": "NOT PASSED - no project website found (only Boltbook post + BscScan + Sourcify repo link)",
   "x_status": "not found", "liquidity": "NONE - post states no LP, not tradable on DEX",
   "same_owner_discard": False, "payout_in_discards": False,
   "classification": "EARLY LEAD / CANDIDATE pending website gate - website-only gate blocks execution; no X; no LP"},
  {"project": "AgentGrid / WATT", "sale_contract": "0x651302C0043040D48EaAF85605E12F0549aD6D89",
   "token_contract": "0xd8FAF2597c8b81eed4befA4A651cccF05196163b",
   "type": "S1 factory-deployed sale (sale+token+vault)", "source": "Sourcify recently-verified feed, verified 2026-11-08 21:48:29Z; no Boltbook post, no website, no X found",
   "shape": "FREE_SHARES, freeUsed, claimShares/mint, registry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, walletOfHandle, refund, finalize, CAP_PER_AGENT, INVITE_BONUS, LP_BNB_RATIO; sale owner()=0x0; token owner()=0x0",
   "onchain_block": grid.get("block"), "token_name": "AgentGrid", "token_symbol": "WATT",
   "free_quota": 500, "free_used": 6, "free_remaining": 494, "tokens_per_share": 112500,
   "total_shares_sold": 6, "paid_count": 0, "cap_per_agent": 8, "max_shares": 4444,
   "start_wib": "~2026-11-09 04:47 (deadline minus 3-day duration)", "deadline_wib": "2026-11-12 04:47",
   "launch_age_at_read": "~55 min", "user_slot": "UNVERIFIED - claimedShares(agent wallet) reverts (read failure, not zero)",
   "factory": "0xca143ce32fe78f1f7019d7d551a6402fc5350c73", "vault": "0x5856C6Ffb46b7Fb45B3B834eA9d90d292548484b",
   "team_wallet": "0xd09157c16ca3f64cf460a53c4d7704aa5966f9d3",
   "website_gate": "NOT PASSED - no website/post found", "x_status": "not found",
   "same_owner_discard": False, "classification": "EARLY LEAD, Sourcify-only; website gate NOT passed; user slot unverified"}
 ],
 "dead_or_closed": [
  {"project": "PokeChain", "contract": "0x4EF929aF00cB93993c3D01834C4DA79200d31e32", "status": "SOLD OUT - Boltbook post: free mint #651 listed, sold out"},
  {"project": "Paw Gang", "contract": "0x587C303982187Ec578dF309d27670327b13202F8", "status": "MINT CLOSED - totalMinted 3,333/3,333"},
  {"project": "UNIT-BOT", "contract": "0xd800efb5f2f44b6afb0cde553e885390a7d38156", "status": "PAID mint 0.001 BNB, supply 394/4444 - not free"},
  {"project": "NOVRA", "contract": "0x75Ac13cF23a8dccC703D1496138251FD7f247890", "status": "FREE POOL EXHAUSTED - freeRemaining()=0 at block 132470959; totalSupply = exactly 72 x 1,000,000 NOVRA (all 72 free shares gone, 0 paid)"},
  {"project": "Agent Zet", "contract": "0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37", "status": "free phase complete 4,000/4,000; paid only now"}
 ],
 "sweep_notes": [
  {"project": "Likhin", "site": "https://likhin.pages.dev", "status": "already in snapshot - known"},
  {"project": "Agent Harvest Land", "contract": "0xacf150d9eC909E3d339Bf4c6D090b18495674E66", "status": "already in snapshot - known"},
  {"project": "Subsonic Tribe", "contract": "0x65DDB3E337c12E5964ead6Cb9b6469203EF4caf1", "status": "already in snapshot - known"},
  {"project": "Agent Periodic Lab", "contract": "0xfE5Ab5ce9b1D86a55d70E7D0573a14D559029C18", "status": "already in snapshot (bridge) - known"},
  {"project": "AgentVOLT", "contract": "0xc58ecec1437777061134c1bddf0ed5ea6eafabf4", "status": "NOT in snapshot; Boltbook post 2 days ago: 1,049/10,000, first share free per Agent ID; website/X unverified; NO on-chain check this run (timebox) - watch note only"},
  {"project": "BNBmeme", "contract": "0xdfe8c254b8cb1cdb2ecf755cbd519e9a23760723", "status": "NOT in snapshot; Oct 26 post, window ~to 10/30 - likely expired, not promoted"},
  {"project": "Laser Agents", "contract": "0x3ed6b33f9ea597a6f210b5e70029ddd92e93ae85", "status": "NOT in snapshot; Oct 25 Binance Square post, no website - not promoted"},
  {"project": "BURN", "contract": "0x7de1606230aa70802caecf1a3e90039a6265b1c4", "status": "NOT in snapshot; Blockspot listing only, first unit free per ID, 4.44M share cap - unverified, not promoted"},
  {"project": "Razor Agent", "site": "https://razoragent.fun", "status": "NOT DEPLOYED - no contracts, skip"}
 ],
 "route6": {"odaily_panews": "no Odaily/PANews item surfaced in news-vertical search; direct newsflash fetch not done (timebox)",
            "binance_square": "one hit: Laser Agents Square post 2026-10-25 (noted above); no new Square lead",
            "status": "PARTIAL"},
 "not_rechecked_per_instructions": ["binanceai.fun pending claim (refund phase, already reported once)"],
 "bridge": {"status": "unchanged, nothing to do (116 contracts, 0 new vs run 0401)"},
 "same_owner_discards_checked": {"discard_owner_count": len(disc_owners), "flagged": []},
 "files_written": [
   f"run-{RUN}-boltbook-en.html", f"run-{RUN}-boltbook-zh.html", f"run-{RUN}-bhtb-post.html",
   f"run-{RUN}-sourcify-feed.json", f"run-{RUN}-bhtb-sourcify.json", f"run-{RUN}-bhtb-sourcify-meta.json",
   f"run-{RUN}-bhtb-metadata.json", f"run-{RUN}-bhtb-abi.json", f"run-{RUN}-bhtb-onchain.py",
   f"run-{RUN}-bhtb-onchain.json", f"run-{RUN}-sourcify-651302-onchain.json", f"run-{RUN}-novra-onchain.json",
   f"run-{RUN}-discovery.py", f"run-{RUN}-discovery.json"],
}
json.dump(out, open(os.path.join(HF, f"run-{RUN}-discovery.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("run", "snapshot_contracts", "route6")}, indent=1))
print("boltbook unique:", out["boltbook"]["unique_addresses"], "new:", out["boltbook"]["new_vs_snapshot"])
print("sourcify n:", out["sourcify_feed"]["n"], "leads:", len(out["leads"]))
