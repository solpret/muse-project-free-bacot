#!/usr/bin/env python3
"""Fix run-1431 merge velocity bug: the merge used snapshot previousTotalSupply/
previousRatePerMin, which for several items lag one run behind the 1401 read.
Recompute from the 1331/1401/1431 reread JSONs (ground truth) and repair the
snapshot velocity fields. No preview/mint."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r1331 = json.load(open(BASE + "run-2026-11-14-1331-reread.json"))
r1401 = json.load(open(BASE + "run-2026-11-14-1401-reread.json"))
r1431 = json.load(open(BASE + "run-2026-11-14-1431-reread.json"))
C = snap["contracts"]
SUPPLY_KEY = {
 "WoozCode": "totalSnippets", "MORFO": "totalMinted", "NOISE": "totalMinted",
 "DragonAgents": "totalSupply", "AngelEye-77D9": "totalSupply", "AngelEye-07bD": "totalSupply",
 "NovaRemnants": "totalRemnants", "RaceAgents": "totalSupply", "AbsurdAgentNFT": "totalMinted",
 "B77D": "totalMinted", "Zero": "totalSupply", "HIVE": "totalSupply",
 "AgentZENITH": "totalSupply", "AgentNOVA": "totalSupply", "SPARKS": "totalSupply",
 "AgentBubble": "totalSupply", "WANGCAI": "totalSupply", "YUANBAO": "totalSupply",
 "NOTV": "totalSupply", "PX24": "totalSupply", "Zephyra": "totalMinted",
 "LumenFindings": "totalSpecimens", "Pengu": "totalMinted", "CPASS": "totalMinted",
 "SPEC": "totalSpecimens", "TrashBandits": "totalMinted", "SKRR": "totalSupply",
 "REOPIR": "totalSupply", "FrieAgent-B751": "totalSupply", "FrieAgent-c64d": "totalSupply",
 "Ledgera": "totalSupply", "MAMI": "totalSupply", "INKI": "totalSupply", "OTV": "totalSupply",
}
INT1401 = (r1401["block"] - r1331["block"]) * 0.45 / 60.0
INT1431 = (r1431["block"] - r1401["block"]) * 0.45 / 60.0
print(f"intervals: 1401={INT1401:.2f} min, 1431={INT1431:.2f} min")
def sup(reads, name):
    v = reads.get(name, {}).get("views")
    if not v: return None
    return v.get(SUPPLY_KEY[name])
# 1401 values for the 3 Boltbook items (not in 1401 reread set; from run-1401 boltbook note)
EXTRA1401 = {"Ledgera": 2329, "MAMI": 220, "INKI": 212}
fixed = []
for name in r1431["reads"]:
    if name not in SUPPLY_KEY:
        continue
    e = C[name]
    new_ts = sup(r1431["reads"], name)
    old_ts = sup(r1401["reads"], name)
    if old_ts is None:
        old_ts = EXTRA1401.get(name)
    if new_ts is None or old_ts is None:
        print(f"{name}: skip (new={new_ts} old={old_ts})"); continue
    base_ts = sup(r1331["reads"], name)
    prev_rate = None
    if base_ts is not None:
        prev_rate = (old_ts - base_ts) / INT1401
    minted = new_ts - old_ts
    rate = minted / INT1431
    ratio = (rate / prev_rate) if prev_rate else None
    passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
    e["previousTotalSupply"] = old_ts
    e["previousRatePerMin"] = round(prev_rate, 4) if prev_rate is not None else None
    e["currentRatePerMin"] = round(rate, 4)
    e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
    e["velocityLegPasses"] = passes
    e["mintedInInterval"] = minted
    e["intervalMinutes"] = round(INT1431, 1)
    e["runNote1431_1114"] = (f"Run 1431 (blok {r1431['block']}, interval ~{INT1431:.1f} mnt vs run 1401): "
        f"{old_ts}->{new_ts} (+{minted}, {rate:.4f}/mnt vs prev "
        f"{round(prev_rate,4) if prev_rate is not None else None} = "
        f"{round(ratio,2) if ratio is not None else None}x) -> velocity "
        f"{'LOLOS' if passes else 'GAGAL'}")
    fixed.append((name, old_ts, new_ts, minted, round(rate,4),
                  round(prev_rate,4) if prev_rate is not None else None,
                  round(ratio,2) if ratio is not None else None, passes))
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("fixed", len(fixed))
for row in fixed:
    print(row)
