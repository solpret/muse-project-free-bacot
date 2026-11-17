import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
prev_ts="2026-10-31T22:02:00+07:00"
elapsed=30.0
new={
 "AgentImps":666,"AgentMiner":4564,"AgentPad Pass":1128,"Agentlings":6665,
 "Alibaba & The 70 Thieves":4818,"BeHand Pass":6598,"Brutes":5555,"Fleet Genesis":1000,
 "Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,"OTV":557,
 "PixelVulpes":3333,"SYMBOL":3828,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007}
for name, cur in new.items():
    old=snap["contracts"][name]
    prev_total=old["totalSupply"]
    prev_rate=old["ratePerMinute"]
    delta=cur-prev_total
    rate=round(delta/elapsed,3)
    old["previousTotalSupply"]=prev_total
    old["previousRatePerMinute"]=prev_rate
    old["totalSupply"]=cur
    old["mintedInInterval"]=delta
    old["ratePerMinute"]=rate
snap["timestamp_wib"]="2026-10-31T22:32:00+07:00"
snap["note"]="Snapshot 22:32 WIB run; elapsed ~30.0 min since 22:02 snapshot, block 130881520. NO new main candidate. Agentlings 6645->6665 delta 20 rate 0.667 vs prev 0.333 (2.0x, delta>=20) PASSES velocity but % unverified and known since 27 Oct (>24h) so age FAILS - watchlist only. AgentMiner 4558->4564 delta 6 rate 0.200 vs prev 0.067 (2.99x but delta<20) FAILS velocity; 4564/9999=45.65% passes % alone; already 24h+ age-excluded 20:01 run. BeHand 6585->6598 delta 13 rate 0.433 vs prev 0.133 (3.25x but delta<20) FAILS. Alibaba 4810->4818 delta 8 rate 0.267 vs prev 0.167 (1.60x but delta<20) FAILS. SYMBOL 3821->3828 delta 7 rate 0.233 vs prev 0.100 (2.33x but delta<20) FAILS; 3828/10000=38.28% FAILS %. Flat: Hackou 92/200=46% passes % alone but velocity FAILS; OTV 557/1500=37.1% FAILS; Sonic 2237, danta 2007, AgentPad 1128 flat. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap, open(p,"w"), indent=1)
print("updated")
