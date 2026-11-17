import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
# elapsed 29 min: prev snapshot 18:33 WIB, reads ~19:02 WIB, block 130853534
new={
 "AgentImps":666,"AgentMiner":4503,"AgentPad Pass":1128,"Agentlings":6555,
 "Alibaba & The 70 Thieves":4759,"BeHand Pass":6522,"Brutes":5555,"Fleet Genesis":1000,
 "Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,"OTV":557,"PixelVulpes":3333,
 "SYMBOL":3774,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
}
elapsed=29
for name,val in new.items():
    e=snap["contracts"][name]
    prev=e["totalSupply"]
    e["previousTotalSupply"]=prev
    e["previousRatePerMinute"]=e["ratePerMinute"]
    e["totalSupply"]=val
    e["mintedInInterval"]=val-prev if prev is not None else None
    e["ratePerMinute"]=round((val-prev)/elapsed,3) if prev is not None else None
snap["timestamp_wib"]="2026-10-31T19:02:00+07:00"
snap["note"]="Snapshot 19:02 WIB run; elapsed ~29 min since 18:33 snapshot, block 130853534. NO new main candidate. AgentMiner 4495->4503 delta 8 rate 0.276 vs prev 0.500 (0.55x) FAILS velocity, though 4503/9999=45.03% now passes % alone. Agentlings 6534->6555 delta 21 rate 0.724 vs prev 0.500 (1.45x, below 1.5x) FAILS velocity despite delta>=20. Alibaba 4756->4759 delta 3 FAILS; % unverified, no project-stated X, known since 28 Oct. SYMBOL 3764->3774 delta 10 FAILS (delta<20) and 37.7% FAILS. Hackou 90->92 delta 2 FAILS velocity though 92/200=46% passes % alone. BeHand delta 5 FAILS. OTV flat 557/1500=37.1% FAILS. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap,open(p,"w"),indent=1,ensure_ascii=False)
print("updated")
