import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
elapsed=30  # 07:03 -> ~07:33 WIB
new={
 "AgentImps":666,"AgentMiner":4629,"AgentPad Pass":1129,"Agentlings":6853,
 "Alibaba & The 70 Thieves":4891,"BeHand Pass":6680,"Brutes":5555,
 "Fleet Genesis":1000,"Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,
 "OTV":558,"PixelVulpes":3333,"SYMBOL":3930,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
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
snap["timestamp_wib"]="2026-11-01T07:33:00+07:00"
snap["note"]=("Snapshot 07:33 WIB run; elapsed 30 min since 07:03 snapshot, block 130953582 at read time. NO new main candidate. NO velocity pass (both legs rate>=1.5x AND delta>=20 required): Agentlings 6839->6853 delta 14 rate 0.467 vs prev 0.233 (ratio 2.00x but delta <20, FAILS); SYMBOL 3922->3930 delta 8 rate 0.267 vs prev 0.133 (ratio 2.01x but delta <20, FAILS), 3930/10000=39.30% FAILS %; AgentMiner 4620->4629 delta 9 rate 0.300 vs prev 0.0 (delta <20, FAILS), 4629/9999=46.30% passes % alone but 24h+ age exclusion stands; BeHand 6678->6680 delta 2 rate 0.067 vs prev 0.067 (ratio 1.00x, FAILS, delta <20). Flat: AgentPad 1129, Alibaba 4891, Sonic 2237, danta 2007, AgentImps 666, OTV 558. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(p,"w"), indent=1)
print("written")
