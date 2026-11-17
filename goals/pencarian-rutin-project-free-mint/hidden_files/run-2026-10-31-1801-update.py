import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
new={
 "AgentImps":666,"AgentMiner":4480,"AgentPad Pass":1128,"Agentlings":6519,
 "Alibaba & The 70 Thieves":4721,"BeHand Pass":6509,"Brutes":5555,"Fleet Genesis":1000,
 "Floppy Agents":3333,"Hackou AI Pass":90,"Noir Brokers":3333,"OTV":557,"PixelVulpes":3333,
 "SYMBOL":3758,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
}
for name,val in new.items():
    e=snap["contracts"][name]
    prev=e["totalSupply"]
    e["previousTotalSupply"]=prev
    e["previousRatePerMinute"]=e["ratePerMinute"]
    e["totalSupply"]=val
    e["mintedInInterval"]=val-prev if prev is not None else None
    e["ratePerMinute"]=round((val-prev)/30,3) if prev is not None else None
snap["timestamp_wib"]="2026-10-31T18:02:00+07:00"
snap["note"]="Snapshot 18:02 WIB run; elapsed ~30 min since 17:32 snapshot, block 130845540. NO new main candidate. AgentMiner 4470->4480 delta 10 rate 0.333 vs prev 0.033 (10.10x, but delta <20) FAILS velocity and 4480/9999=44.8% FAILS >=45%. Agentlings 6491->6519 delta 28 rate 0.933 vs prev 1.400 (0.67x) FAILS velocity; minted % UNVERIFIED (no verified cap), no project-stated X account, known since 27 Oct (>24h evidence) - NOT a candidate. SYMBOL 3756->3758 delta 2 FAILS velocity and 3758/10000=37.6% FAILS >=45%. BeHand 6499->6509 delta 10 rate 0.333 vs 0.300 (1.11x, <20) FAILS. Alibaba delta 4 FAILS. OTV 557/1500=37.1% flat FAILS. Hackou 90/200=45.0% meets % alone but delta 0 FAILS velocity. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap,open(p,"w"),indent=1,ensure_ascii=False)
print("updated")
