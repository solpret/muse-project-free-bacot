#!/usr/bin/env python3
"""Fix merge-1031 errors: HIVE missed (key mismatch), AgentBubble mixed-metric
velocity, B77D/Zephyra missing baselines, Zero failed-read block advance."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s=json.load(open(BASE+"onchain-snapshot.json"))
BLK=133472775
# HIVE (reread key HIVE): totalSupply 1263 flat vs 0931 (blok 133464854), bal 1
h=s["contracts"]["HIVE Agents"]
h["totalSupply"]=1263; h["balanceOf_user"]=1; h["balanceOf"]=1
h["previousTotalSupply"]=1263; h["mintedInInterval"]=0; h["intervalMinutes"]=59.4
h["previousRatePerMin"]=h.get("currentRatePerMin"); h["currentRatePerMin"]=0.0
h["velocityRatio"]=None; h["velocityLegPasses"]=False
h["lastReadBlock"]=BLK; h["lastReadWib"]="2026-11-14 ~10:35 WIB"
h["runNote1031_1114"]="Run 1031 (blok 133472775, interval ~59,4 mnt vs run 0931): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM."
# AgentBubble: velocity on totalSupply (1471->1502), free% on freeMinted 1361/2222
ab=s["contracts"]["AgentBubble"]
ab["totalSupply"]=1502; ab["freeMinted"]=1361
ab["previousTotalSupply"]=1502; ab["mintedInInterval"]=31; ab["intervalMinutes"]=59.4
ab["previousRatePerMin"]=0.313; ab["currentRatePerMin"]=0.522; ab["velocityRatio"]=1.67
ab["velocityLegPasses"]=True
ab["lastReadBlock"]=BLK; ab["lastReadWib"]="2026-11-14 ~10:35 WIB"
ab["runNote1031_1114"]="Run 1031 (blok 133472775, interval ~59,4 mnt vs run 0931): totalSupply 1471->1502 (+31, 0,522/mnt vs prev 0,313 = 1,67x) -> velocity LOLOS, TAPI free 1361/2222 = 61,3% (<70%), X + website unverified -> TIDAK promosi. DIAM."
# B77D: baseline 613 (run 0931 blok 133464854; 1001 juga 613) -> 712
b=s["contracts"]["B77D"]
b["totalMinted"]=712
b["previousTotalSupply"]=712; b["mintedInInterval"]=99; b["intervalMinutes"]=28.6
b["previousRatePerMin"]=5.97; b["currentRatePerMin"]=3.46; b["velocityRatio"]=0.58
b["velocityLegPasses"]=False
b["lastReadBlock"]=BLK; b["lastReadWib"]="2026-11-14 ~10:35 WIB"
b["runNote1031_1114"]="Run 1031 (blok 133472775, interval ~28,6 mnt vs run 1001 blok 133468967, totalMinted 613): 613->712 (+99, 3,46/mnt vs prev 5,97 = 0,58x) -> velocity GAGAL; free% tetap UNVERIFIED (freeCount null) -> bukan strong lead. DIAM."
# Zephyra: 841 -> 842
z=s["contracts"]["Zephyra"]
z["totalMinted"]=842
z["previousTotalSupply"]=842; z["mintedInInterval"]=1; z["intervalMinutes"]=59.4
z["previousRatePerMin"]=None; z["currentRatePerMin"]=0.017; z["velocityRatio"]=None
z["velocityLegPasses"]=False
z["lastReadBlock"]=BLK; z["lastReadWib"]="2026-11-14 ~10:35 WIB"
z["runNote1031_1114"]="Run 1031 (blok 133472775, interval ~59,4 mnt vs run 0931): totalMinted 841->842 (+1, 0,017/mnt) -> velocity GAGAL; free% UNVERIFIED; umur UNVERIFIED; website UNVERIFIED; X UNVERIFIED. Tetap early lead, DIAM."
# Zero: read failed this run - restore lastReadBlock, keep old values
ze=s["contracts"]["Zero"]
ze["lastReadBlock"]=133464854; ze["lastReadWib"]="2026-11-14 ~09:31 WIB"
ze["runNote1031_1114"]="Run 1031: totalSupply/freeClaimed GAGAL baca (null, degradasi eth_call) - nilai lama dipertahankan, velocity TIDAK dihitung; age-excluded sudah dilaporkan run 0931 (deadline 07:55 WIB lewat), DIAM."
json.dump(s,open(BASE+"onchain-snapshot.json","w"),indent=1)
print("FIX OK; snapshot contracts:",len(s["contracts"]))
print("HIVE:",h["totalSupply"],"AgentBubble vel:",ab["velocityLegPasses"],"B77D vel:",b["velocityLegPasses"],"Zephyra:",z["totalMinted"])
