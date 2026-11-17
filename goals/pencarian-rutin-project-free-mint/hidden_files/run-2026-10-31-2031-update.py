import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
new={
 "AgentImps":666,"AgentMiner":4548,"AgentPad Pass":1128,"Agentlings":6610,
 "Alibaba & The 70 Thieves":4791,"BeHand Pass":6561,"Brutes":5555,
 "Fleet Genesis":1000,"Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,
 "OTV":557,"PixelVulpes":3333,"SYMBOL":3798,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
}
elapsed=30.0
for name, cur in new.items():
    e=snap["contracts"][name]
    prev=e["totalSupply"]
    e["previousTotalSupply"]=prev
    e["previousRatePerMinute"]=e["ratePerMinute"]
    e["totalSupply"]=cur
    d=cur-prev if prev is not None else 0
    e["mintedInInterval"]=d
    e["ratePerMinute"]=round(d/elapsed,3)
snap["timestamp_wib"]="2026-10-31T20:32:00+07:00"
snap["note"]=("Snapshot 20:32 WIB run; elapsed ~30.0 min since 20:02 snapshot, block 130865529. NO new main candidate. "
 "Agentlings 6576->6610 delta 34 rate 1.133 vs prev 0.261 (4.34x, delta>=20) PASSES velocity BUT % unverified (max supply still not stated), X unverified, and known since 27 Oct (>24h) so NOT a candidate. "
 "AgentMiner 4536->4548 delta 12 rate 0.400 vs prev 0.784 (0.51x) FAILS velocity; already 24h+ age-excluded 20:01 run, not re-reported. "
 "Alibaba 4782->4791 delta 9 FAILS. BeHand 6553->6561 delta 8 FAILS. SYMBOL 3789->3798 delta 9 FAILS velocity (delta<20 despite 1.53x ratio) and 37.98% FAILS. Hackou flat 92/200=46% passes % alone but velocity FAILS. OTV flat 557/1500=37.1% FAILS. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(p,"w"), indent=1)
print("updated")
