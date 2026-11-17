import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
new={
 "AgentImps":666,"AgentMiner":4536,"AgentPad Pass":1128,"Agentlings":6576,
 "Alibaba & The 70 Thieves":4782,"BeHand Pass":6553,"Brutes":5555,
 "Fleet Genesis":1000,"Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,
 "OTV":557,"PixelVulpes":3333,"SYMBOL":3789,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
}
elapsed=30.61
for name, cur in new.items():
    e=snap["contracts"][name]
    prev=e["totalSupply"]
    e["previousTotalSupply"]=prev
    e["previousRatePerMinute"]=e["ratePerMinute"]
    e["totalSupply"]=cur
    d=cur-prev if prev is not None else 0
    e["mintedInInterval"]=d
    e["ratePerMinute"]=round(d/elapsed,3)
snap["timestamp_wib"]="2026-10-31T20:02:00+07:00"
snap["note"]=("Snapshot 20:02 WIB run; elapsed ~30.6 min since 19:32 snapshot, block 130861519. NO new main candidate. "
 "AgentMiner 4512->4536 delta 24 rate 0.784 vs prev 0.300 (2.61x, delta>=20) PASSES velocity AND 4536/9999=45.36% PASSES % -- first run it passes BOTH on-chain legs -- BUT formally AGE-EXCLUDED this run: first observed minting 2026-10-28 (totalSupply 2729 in 28 Oct run logs), so minting open >=3 days, >24h and not sold out; plus X discussion UNVERIFIED (no project-stated X, AgentMiner-specific searches found no discussion) and free quota for user wallet unverified. NOT a candidate; recorded as 24h+ age exclusion, not an active watchlist priority. "
 "BeHand 6546->6553 delta 7 FAILS velocity. Agentlings 6568->6576 delta 8 FAILS. Alibaba 4774->4782 delta 8 FAILS. SYMBOL 3783->3789 delta 6 FAILS and 37.89% FAILS. Hackou flat 92/200=46% passes % alone but velocity FAILS. OTV flat 557/1500=37.1% FAILS. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(p,"w"), indent=1)
print("updated")
