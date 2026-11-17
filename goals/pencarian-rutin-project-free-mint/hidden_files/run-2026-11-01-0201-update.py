import json
snap_path="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(snap_path))
prev_ts=snap["timestamp_wib"]
# new readings at block 130909567, elapsed 30 min (01:32 -> 02:02)
new={
 "AgentImps":666,"AgentMiner":4608,"AgentPad Pass":1129,"Agentlings":6758,
 "Alibaba & The 70 Thieves":4873,"BeHand Pass":6644,"Brutes":5555,"Fleet Genesis":1000,
 "Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,"OTV":557,
 "PixelVulpes":3333,"SYMBOL":3900,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
}
for name,val in new.items():
    e=snap["contracts"][name]
    prev=e["totalSupply"]; prev_rate=e["ratePerMinute"]
    delta=val-prev if prev is not None else 0
    rate=round(delta/30,3)
    e["previousTotalSupply"]=prev; e["totalSupply"]=val; e["mintedInInterval"]=delta
    e["previousRatePerMinute"]=prev_rate; e["ratePerMinute"]=rate
snap["timestamp_wib"]="2026-11-01T02:02:00+07:00"
snap["note"]="Snapshot 02:02 WIB run; elapsed 30 min since 01:32 snapshot, block 130909567 at read time. NO new main candidate. NO velocity pass this run: Agentlings 6736->6758 delta 22 rate 0.733 vs prev 0.5 (ratio 1.47x <1.5x, velocity FAILS despite delta>=20); AgentMiner 4603->4608 delta 5 rate 0.167 vs prev 0.433, 4608/9999=46.08% passes % alone but velocity FAILS and age-excluded; SYMBOL 3892->3900 delta 8 rate 0.267 vs prev 0.3, 3900/10000=39.0% FAILS >=45%; Alibaba 4865->4873 delta 8 rate 0.267 vs prev 0.2; BeHand 6637->6644 delta 7 rate 0.233 vs prev 0.2. Flat: AgentPad 1129, OTV 557/1500=37.1% FAILS %, Sonic 2237, danta 2007. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666, Hackou 92. Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap,open(snap_path,"w"),indent=1,ensure_ascii=False)
print("updated", prev_ts)
