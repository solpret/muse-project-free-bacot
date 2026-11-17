import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
old={k:dict(v) for k,v in snap["contracts"].items()}
# elapsed 30 min (06:33 -> ~07:03)
elapsed=30
new={
 "AgentImps":666,"AgentMiner":4620,"AgentPad Pass":1129,"Agentlings":6839,
 "Alibaba & The 70 Thieves":4891,"BeHand Pass":6678,"Brutes":5555,
 "Fleet Genesis":1000,"Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,
 "OTV":558,"PixelVulpes":3333,"SYMBOL":3922,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
}
for name,val in new.items():
    e=snap["contracts"][name]
    prev_total=e["totalSupply"]
    prev_rate=e["ratePerMinute"]
    delta=val-prev_total if prev_total is not None else None
    rate=round(delta/elapsed,3) if delta is not None else None
    e["previousTotalSupply"]=prev_total
    e["previousRatePerMinute"]=prev_rate
    e["totalSupply"]=val
    e["mintedInInterval"]=delta
    e["ratePerMinute"]=rate
    print(name, prev_total, "->", val, "delta", delta, "rate", rate, "prevRate", prev_rate)
# failed-read contracts preserved null fields unchanged (per prior runs, their totalSupply stays null)
snap["timestamp_wib"]="2026-11-01T07:03:00+07:00"
snap["note"]=("Snapshot 07:03 WIB run; elapsed 30 min since 06:33 snapshot, block 130949622 at read time. NO new main candidate. NO velocity pass (both legs rate>=1.5x AND delta>=20 required): Agentlings 6832->6839 delta 7 rate 0.233 vs prev 0.032 (ratio 7.28x but delta <20, FAILS); Alibaba 4886->4891 delta 5 rate 0.167 vs prev 0.065 (ratio 2.57x but delta <20, FAILS); SYMBOL 3918->3922 delta 4 rate 0.133 vs prev 0.032 (ratio 4.16x but delta <20, FAILS), 3922/10000=39.22% FAILS %; BeHand 6676->6678 delta 2 rate 0.067 vs prev 0.065 (ratio 1.03x, FAILS, delta <20). Flat: AgentMiner 4620, AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666, OTV 558. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(p,"w"), indent=1)
print("written")
