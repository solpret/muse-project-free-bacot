import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
c = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked = c["checked"]
s = set(checked)
new = json.load(open("/tmp/trackc5c-candidates.json"))[:20]
added = []
for x in new:
    a = x["address"]
    if a not in s:
        checked.append(a)
        s.add(a)
        added.append(a)
    c[a] = {"source": "backfill-132179196-132181588-5c",
            "status": "checked-not-sale-shape",
            "mint_count": x["mint_count"],
            "note": "S1=False S2=False (no agentRegistry/AgentGate; no free+quote+registry combo)"}
# correct the nearest one with detail
c["0x78573aB46e5436e126d3eA1fDEf8766Cce4Efd2b"] = {
    "source": "backfill-132179196-132181588-5c", "status": "checked-not-sale-shape",
    "mint_count": 346,
    "note": "ShibAgentFission verified: FREE_SHARES/freeClaimed(uint256)/freeMinted/tokensPerShare/quoteFor/mint present, but NO agentRegistry() view; identityRegistry only in constructor Config; registry bytes 0x60B9 absent from deployed bytecode -> S1 registry leg fails"}
json.dump(c, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
print("added", len(added), "checked total", len(checked))
rec = {"window": "132179196-132181588", "run_wib": "2026-11-07 ~17:2x",
       "erc20_unique_merged": 611, "mint_count_ge10": 95, "new_ge10": 80,
       "checked_this_run": 20, "checked_total": len(checked), "sale_shape_hits": 0,
       "nearest": {"address": "0x78573aB46e5436e126d3eA1fDEf8766Cce4Efd2b",
                   "note": "ShibAgentFission, verified, FREE_SHARES/freeClaimed(uint256)/freeMinted/tokensPerShare/quoteFor/mint, identityRegistry only in constructor Config struct, NO agentRegistry() view, registry bytes 0x60B9 absent from deployed bytecode -> S1 registry leg FAILS, not a sale-shape lead",
                   "mint_count": 346, "distinct_minters": 1},
       "other_verified": {"0x74536226D1549A2c96B5BfB63a5351967abE8511": "sharedEquity/sharedLP token, no free views, no quote, no registry -> not sale-shape"},
       "not_verified": ["0xE07150DD3A870fF0115Fc4e3c80529f92e294D89", "0xFaD229b3155a73fD8dB851E079558A884b009999",
                        "0xCfb9beF5F7B748aC72311F057f3a888BC73334D9", "0x302DF4C0E3DD5Dcb36D59344b60D11D05617Fe5e",
                        "0x333D05767067FF4C5167cf1a03BAa6782De33333", "0xC6EA899c6D3B5869786983A9A29e3c380202CC40",
                        "0xD27A1C0d6A76b2f9DA1b6D81Ae85D57B08df503e", "0xE6efCdEf2b720d1eca2b69eDB7ef357725680BEa"],
       "plain_mintable": ["0x10834340776f2D6ec557dFFd65048bfb9Bae0627", "0x22a2C54b15287472F4aDBe7587226E3c998CdD96",
                          "0x35803e77c3163FEd8A942536C1c8e0d5bF90f906", "0x5ce033B2bFCa3Af30b3e8C8457DeaF776A8b695a",
                          "0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6", "0x826923122A8521Be36358Bdc53d3B4362B6f46E5",
                          "0x88886f0fD371dfF856291bAdcEd45922bC888888", "0x8e6442663A4F8C50b6132c68d42A30E7DFE4Ae15",
                          "0xa6344A67780e2da01928FEFd9E558D792d7986dc"]}
json.dump(rec, open(f"{BASE}/trackc-5c-backfill-132179196-132181588.json", "w"), indent=1)
print("5c record saved")
