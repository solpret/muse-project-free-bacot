import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
new={
 "AgentImps":666,"AgentMiner":4495,"AgentPad Pass":1128,"Agentlings":6534,
 "Alibaba & The 70 Thieves":4756,"BeHand Pass":6517,"Brutes":5555,"Fleet Genesis":1000,
 "Floppy Agents":3333,"Hackou AI Pass":90,"Noir Brokers":3333,"OTV":557,"PixelVulpes":3333,
 "SYMBOL":3764,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
}
for name,val in new.items():
    e=snap["contracts"][name]
    prev=e["totalSupply"]
    e["previousTotalSupply"]=prev
    e["previousRatePerMinute"]=e["ratePerMinute"]
    e["totalSupply"]=val
    e["mintedInInterval"]=val-prev if prev is not None else None
    e["ratePerMinute"]=round((val-prev)/30,3) if prev is not None else None
snap["timestamp_wib"]="2026-10-31T18:33:00+07:00"
snap["note"]="Snapshot 18:33 WIB run; elapsed ~30 min since 18:02 snapshot, block 130849537. NO new main candidate. Alibaba velocity PASSES alone (4721->4756 delta 35 rate 1.167 vs prev 0.133, 8.77x, >=20) but minted % UNVERIFIED (no verified cap since first watchlist appearance 2026-10-28), no project-stated X account found in sweep, and known since 28 Oct (>24h) - NOT a candidate, watchlist only. AgentMiner 4480->4495 delta 15 rate 0.500 vs prev 0.333 (1.50x but delta <20) FAILS velocity and 4495/9999=44.95% FAILS >=45% (just under). Agentlings 6519->6534 delta 15 rate 0.500 vs 0.933 (0.54x) FAILS. BeHand 6509->6517 delta 8 FAILS. SYMBOL 3758->3764 delta 6 FAILS and 3764/10000=37.6% FAILS. OTV 557/1500=37.1% flat FAILS. Hackou 90/200=45.0% meets % alone but delta 0 FAILS velocity. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap,open(p,"w"),indent=1,ensure_ascii=False)
print("updated")
