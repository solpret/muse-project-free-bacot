import json
snap_path="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(snap_path))
prev_ts=snap["timestamp_wib"]
# new readings at block 130905527, elapsed 30 min (01:02 -> 01:32)
new={
 "AgentImps":666,"AgentMiner":4603,"AgentPad Pass":1129,"Agentlings":6736,
 "Alibaba & The 70 Thieves":4865,"BeHand Pass":6637,"Brutes":5555,"Fleet Genesis":1000,
 "Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,"OTV":557,
 "PixelVulpes":3333,"SYMBOL":3892,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
}
for name,val in new.items():
    e=snap["contracts"][name]
    prev=e["totalSupply"]; prev_rate=e["ratePerMinute"]
    delta=val-prev if prev is not None else 0
    rate=round(delta/30,3)
    e["previousTotalSupply"]=prev; e["totalSupply"]=val; e["mintedInInterval"]=delta
    e["previousRatePerMinute"]=prev_rate; e["ratePerMinute"]=rate
snap["timestamp_wib"]="2026-11-01T01:32:00+07:00"
snap["note"]="Snapshot 01:32 WIB run; elapsed 30 min since 01:02 snapshot, block 130905527 at read time. NO new main candidate. NO velocity pass this run (highest delta 15, below 20 threshold): Agentlings 6721->6736 delta 15 rate 0.5 vs prev 0.267 (1.87x but delta<20); AgentMiner 4590->4603 delta 13 rate 0.433 vs prev 0.267 (1.62x but delta<20), 4603/9999=46.03% passes % alone but age-excluded; SYMBOL 3883->3892 delta 9 rate 0.3 vs prev 0.833, 3892/10000=38.9% FAILS >=45%; Alibaba 4859->4865 delta 6; BeHand 6631->6637 delta 6. Flat: AgentPad 1129, OTV 557/1500=37.1% FAILS %, Sonic 2237, danta 2007. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666, Hackou 92. Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap,open(snap_path,"w"),indent=1,ensure_ascii=False)
print("updated", prev_ts)
