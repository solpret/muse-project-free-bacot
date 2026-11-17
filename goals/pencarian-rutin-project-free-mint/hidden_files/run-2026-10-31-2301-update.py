import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
elapsed=30.0
new={
 "AgentImps":666,"AgentMiner":4569,"AgentPad Pass":1128,"Agentlings":6679,
 "Alibaba & The 70 Thieves":4826,"BeHand Pass":6608,"Brutes":5555,"Fleet Genesis":1000,
 "Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,"OTV":557,
 "PixelVulpes":3333,"SYMBOL":3833,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007}
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
snap["timestamp_wib"]="2026-10-31T23:02:00+07:00"
snap["note"]="Snapshot 23:02 WIB run; elapsed ~30.0 min since 22:32 snapshot, block 130885515. NO new main candidate. NO contract passes velocity this run: Agentlings 6665->6679 delta 14 rate 0.467 vs prev 0.667 (0.70x, delta<20) FAILS; BeHand 6598->6608 delta 10 rate 0.333 vs prev 0.433 FAILS; Alibaba 4818->4826 delta 8 rate 0.267 vs prev 0.267 (1.00x) FAILS; AgentMiner 4564->4569 delta 5 rate 0.167 vs prev 0.200 FAILS, 4569/9999=45.70% passes % alone, age-excluded 20:01 run stands; SYMBOL 3828->3833 delta 5 rate 0.167 vs prev 0.233 FAILS, 3833/10000=38.33% FAILS %. Flat: Hackou 92/200=46% passes % alone but velocity FAILS; OTV 557/1500=37.1% FAILS; Sonic 2237, danta 2007, AgentPad 1128 flat. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap, open(p,"w"), indent=1)
print("updated")
