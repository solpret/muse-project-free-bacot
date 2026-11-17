import json
p="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap=json.load(open(p))
# elapsed 30 min: prev snapshot 19:02 WIB, reads ~19:32 WIB, block 130857527
new={
 "AgentImps":666,"AgentMiner":4512,"AgentPad Pass":1128,"Agentlings":6568,
 "Alibaba & The 70 Thieves":4774,"BeHand Pass":6546,"Brutes":5555,"Fleet Genesis":1000,
 "Floppy Agents":3333,"Hackou AI Pass":92,"Noir Brokers":3333,"OTV":557,"PixelVulpes":3333,
 "SYMBOL":3783,"Sonic Protocol":2237,"UMBRA Agents":3000,"danta":2007,
}
elapsed=30
for name,val in new.items():
    e=snap["contracts"][name]
    prev=e["totalSupply"]
    e["previousTotalSupply"]=prev
    e["previousRatePerMinute"]=e["ratePerMinute"]
    e["totalSupply"]=val
    e["mintedInInterval"]=val-prev if prev is not None else None
    e["ratePerMinute"]=round((val-prev)/elapsed,3) if prev is not None else None
snap["timestamp_wib"]="2026-10-31T19:32:00+07:00"
snap["note"]="Snapshot 19:32 WIB run; elapsed ~30 min since 19:02 snapshot, block 130857527. NO new main candidate. BeHand 6522->6546 delta 24 rate 0.800 vs prev 0.172 (4.65x, delta>=20) PASSES velocity alone, but cap/X/launch all UNVERIFIED after this run's deep-dive routes (browser.search BeHand + contract-address search, no project-stated X/cap/launch found) so NOT a candidate; stays on active unverified list. AgentMiner 4503->4512 delta 9 rate 0.300 vs prev 0.276 (1.09x) FAILS velocity though 4512/9999=45.12% passes % alone. Agentlings 6555->6568 delta 13 FAILS velocity. Alibaba 4759->4774 delta 15 rate 0.500 vs prev 0.103 (4.85x) but delta<20 FAILS velocity; % unverified, known since 28 Oct. SYMBOL 3774->3783 delta 9 FAILS and 37.83% FAILS. Hackou flat 92/200=46% passes % alone but velocity FAILS. OTV flat 557/1500=37.1% FAILS. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap,open(p,"w"),indent=1,ensure_ascii=False)
print("updated")
