#!/usr/bin/env python3
"""Merge run 1031 re-read + checks into onchain-snapshot.json (read fresh values,
compute velocity, add run notes). No preview/mint. Writes snapshot back."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s=json.load(open(BASE+"onchain-snapshot.json"))
r=json.load(open(BASE+"run-2026-11-14-1031-reread.json"))
BLK=r["block"]; READS=r["reads"]
# (snapshot key, supply-view key in reread views, free-pct denominator or None)
MAP={
 "WoozCode":("totalSnippets",None),
 "MORFO":("totalMinted",None),
 "NOISE":("totalMinted",None),
 "DragonAgents":("freeClaimed",888),
 "AngelEye-77D9":("totalSupply",None),
 "AngelEye-07bD":("totalSupply",None),
 "NovaRemnants":("totalRemnants",None),
 "RaceAgents":("freeMinted",1000),
 "AbsurdAgentNFT":("totalMinted",None),
 "B77D":("totalMinted",None),
 "Zero":("totalSupply",None),
 "HIVE Agents":("totalSupply",None),
 "AgentZENITH":("totalSupply",None),
 "AgentNOVA":("totalSupply",None),
 "SPARKS":("totalSupply",None),
 "AgentBubble":("freeMinted",2222),
 "WANGCAI":("freeClaimed",188),
 "YUANBAO":("freeClaimed",188),
 "NOTV":("totalSupply",None),
 "PX24":("totalSupply",None),
 "SKRR":("totalSupply",None),
 "Zephyra":("totalMinted",None),
 "LumenFindings":("totalSpecimens",None),
 "Pengu":("freeMinted",999),
}
KEYMAP={"HIVE":"HIVE Agents"}
notes=[]
for rk,(svk,den) in MAP.items():
    sk=KEYMAP.get(rk,rk)
    entry=s["contracts"].get(sk)
    if entry is None:
        notes.append(f"{sk}: NOT in snapshot, skipped"); continue
    views=(READS.get(rk) or {}).get("views")
    if not views:
        notes.append(f"{sk}: no views"); continue
    # store all fresh views
    for k,v in views.items():
        if v is not None: entry[k]=v
    prev=entry.get("previousTotalSupply")
    cur=views.get(svk)
    prev_blk=entry.get("lastReadBlock")
    interval_min=None
    if prev_blk and BLK>prev_blk:
        interval_min=round((BLK-prev_blk)*0.45/60,1)
    if cur is not None and prev is not None and interval_min:
        minted=cur-prev
        rate=round(minted/interval_min,4) if interval_min else 0.0
        prev_rate=entry.get("currentRatePerMin")
        ratio=None
        if prev_rate and prev_rate>0: ratio=round(rate/prev_rate,2)
        vel=bool(minted>=20 and ratio is not None and ratio>=1.5)
        entry["previousTotalSupply"]=cur
        entry["mintedInInterval"]=minted
        entry["intervalMinutes"]=interval_min
        entry["previousRatePerMin"]=prev_rate
        entry["currentRatePerMin"]=rate
        entry["velocityRatio"]=ratio
        entry["velocityLegPasses"]=vel
        entry["runNote1031_1114"]=f"Run 1031 (blok {BLK}, interval ~{interval_min} mnt vs blok {prev_blk}): {prev}->{cur} (+{minted}, {rate}/mnt vs prev {prev_rate} = {ratio}x) -> velocity {'LOLOS' if vel else 'GAGAL'}; free% {'%.1f%%'%(cur/den*100) if den else 'UNVERIFIED'}."
        notes.append(entry["runNote1031_1114"])
    else:
        entry["previousTotalSupply"]=cur if cur is not None else prev
        entry["runNote1031_1114"]=f"Run 1031 (blok {BLK}): {svk}={cur} (prev {prev}, interval n/a) - velocity tidak dihitung; free% {'%.1f%%'%(cur/den*100) if den and cur is not None else 'UNVERIFIED'}."
        notes.append(entry["runNote1031_1114"])
    entry["lastReadBlock"]=BLK
    entry["lastReadWib"]="2026-11-14 ~10:35 WIB"
# Lumen extras
lum=s["contracts"]["LumenFindings"]
lum["currentExperiment"]=10; lum["genesisStart"]=1794534187; lum["genesisOpen"]=1
lum["websiteGate1031"]="TERVERIFIKASI run 1031: lumenresearch.ltd (pointer baseTokenURI, metode I) diambil 15.933 byte dan MENCETAK kontrak persis 0x4158B701EaA30E8FaDBaA526F70780A38318c1C4 + registry 0x60B9... (2x). Gate website LUMEN = LULUS."
lum["ageNote1031"]="genesisStart on-chain 1794534187 = 13 Nov 08:43 WIB (nilai terjadwal, mendahului mint aktual); mint aktual pertama terverifikasi exp8 04:00-07:00 WIB 14 Nov (172 spesimen 05:31) -> umur dari first-mint ~6,6 jam <24 jam, tetap aktif. % free tetap UNVERIFIED (tanpa free-cap view); X unverified; status tetap watchlist-only (bukan early lead: sudah ada snapshot entry sebelum minting; penanganan sama dengan run 0531 + 1001)."
lum["runNote1031_1114"]="Run 1031: totalSpecimens 2436 (prev 1920), currentExperiment 10, genesisOpen 1, priceFor(user)=0, slot gratis terbuka, balanceOf(user)=0. Website gate kini TERVERIFIKASI (lihat websiteGate1031). Tetap watchlist-only, DIAM."
# Pengu extras
pg=s["contracts"]["Pengu"]
pg["runNote1031_1114"]="Run 1031 (blok 133472775): freeMinted 51/999 = 5,1% (prev 41 ~10:24, +10, baseline velocity pertama ~0,93/mnt), totalMinted 51, mintOpen 1, freeClaimed(user)=false, slot terbuka, holdsAgentId=1. Jauh dari 70% -> tetap early lead, DIAM."
pg["previousTotalSupply"]=51; pg["currentRatePerMin"]=0.93; pg["velocityLegPasses"]=False
# Zephyra
ze=s["contracts"]["Zephyra"]
ze["runNote1031_1114"]="Run 1031: totalMinted 842 (prev 841, +1) -> velocity GAGAL; free% UNVERIFIED; umur UNVERIFIED; website UNVERIFIED; X UNVERIFIED. Tetap early lead, DIAM."
# binanceai pending claim
pc=s["pending_claims"]["binanceai.fun"]
pc["lastReadWib"]="2026-11-14 ~10:35 WIB"; pc["lastReadBlock"]=BLK
pc["runNote1031"]="Run 1031: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, DIAM."
# checked-not-agent-shaped entries (Pickhash, ARCADEWARDEN)
s["contracts"]["checked-Pickhash-1031"]={"address":"0x2296367f74b2ec266cf4667d98501ae7110f5a58","name":"Pickhash","symbol":"PICK","status":"checked-not-agent-shaped-2026-11-14","note":"Boltbook 1031 (post ~10:24 WIB, 1.198/10.000). ABI: mint+price+agent-named fn, TANPA free view. Deep-check: registry bytes in code FALSE, AGENT_ID() null, totalSupply 1240, mintOpen 1, no free views -> BUKAN agent-shaped, BUKAN early lead, BUKAN track C. Tidak masuk watchlist."}
s["contracts"]["checked-ARCADEWARDEN-1031"]={"address":"0xdb7257dbf18ca1539159c64534ffd68ef14c2f32","name":"ARCADEWARDEN","symbol":"COIN","status":"checked-not-agent-shaped-2026-11-14","note":"Boltbook 1031 (post ~10:28 WIB, 742 minted, Sourcify exact_match). ABI: mint + freeLeft, TANPA agent ref. Deep-check: registry bytes in code FALSE, AGENT_ID() null, totalSupply 742/3000, mintOpen 1, freeLeft() garbage (bukan free pool valid) -> BUKAN agent-shaped, BUKAN early lead, BUKAN track C. Tidak masuk watchlist."}
# feedshape summary note (13 addresses: 5 full + 8 fast)
s["runNote1031_1114_feedshape"]="Run 1031 feedshape: 13 alamat baru dicek (8 feed Sourcify verifiedAt 03:15-03:31Z + 5 Boltbook). 5 pertama via full script (S1/S2 False semua; AGENT_ID None; totalSupply token-like 2,1e22/1e27/1e26) - script dibunuh ~430 dtk karena egress lambat, dilanjut fast ABI-only 6,4 dtk untuk 8 sisanya (S1/S2 False semua). 3 alamat BAGENT-miner (0x4bfc/0xc755/0xe4eE, rotasi implementasi 12/13/14 Nov, ABI kosong) = bukan proyek free-mint. 0 early lead, 0 track-C. Pickhash + ARCADEWARDEN deep-check terpisah (lihat checked-...-1031)."
s["runNote1031_1114"]="Run 1031 WIB 2026-11-14 ~10:31-10:50: re-read 25/25 OK blok 133472775 (115,2 dtk); scan leg fast-fail Ankr 401 (5,2 dtk), watermark tetap 132512564; Sourcify feed 20, 8 baru vs 1009; Boltbook EN 45.572 + ZH 45.344 byte, 12 alamat unik, 5 baru (Pickhash, 3x BAGENT-miner, ARCADEWARDEN); sweep EN+ZH 0 baru (Agentic Gangster/KOMA/First-Dollar Grove/AGENT COSMOS dikenal); Odaily 0 pengumuman Agent ID; bridge 116 kontrak, 0 baru, mtime 8 Nov 18:21 UTC; binanceai tetap refund phase. 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B, 0 track-C. WANGCAI 127/188=67,6% (<70%), YUANBAO 116/188=61,7%, RaceAgents 51,6%, B77D velocity GAGAL (1,55 vs 5,97/mnt), Pengu 51/999=5,1%, Zephyra 842 (+1), LumenFindings website gate kini TERVERIFIKASI (lumenresearch.ltd mencetak kontrak) tapi tetap watchlist-only. DIAM (tanpa laporan chat)."
s["last_run_wib"]="2026-11-14 ~10:35 WIB"
s["timestamp_wib"]="2026-11-14 ~10:35 WIB"
json.dump(s,open(BASE+"onchain-snapshot.json","w"),indent=1)
print("MERGE OK; notes:")
for n in notes: print(" -",n)
