import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
elapsed=30.5
new={
 "AgentImps":666,"AgentMiner":4579,"AgentPad Pass":1128,"Agentlings":6698,
 "Alibaba & The 70 Thieves":4837,"BeHand Pass":6616,"Brutes":5555,"Fleet Genesis":1000,
 "Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,"OTV":557,
 "PixelVulpes":3333,"SYMBOL":3847,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007}
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
snap["timestamp_wib"]="2026-11-01T00:02:00+07:00"
snap["note"]="Snapshot 00:02 WIB run; elapsed ~30.5 min since 23:32 snapshot, block 130893548 at read time. NO new main candidate. NO contract passes velocity: SYMBOL 3833->3847 delta 14 rate 0.459 vs prev 0.167 (2.75x BUT delta<20) FAILS; Agentlings 6687->6698 delta 11 rate 0.361 vs prev 0.261 (1.38x, delta<20) FAILS; AgentMiner 4576->4579 delta 3 rate 0.098 vs prev 0.229 FAILS, 4579/9999=45.80% passes % alone, age-excluded 20:01 run stands; BeHand 6612->6616 delta 4 rate 0.131 vs prev 0.131 FAILS; Alibaba 4832->4837 delta 5 rate 0.164 vs prev 0.196 FAILS. Flat: OTV 557/1500=37.1% FAILS %, AgentPad 1128, Sonic 2237, danta 2007. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666, Hackou 92. Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap, open(p,"w"), indent=1)
print("updated")
