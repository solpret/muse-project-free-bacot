#!/usr/bin/env python3
"""Finalize run 0231: apply reread+velocity to snapshot (read-modify-write once).
- velocity rows -> totalSupply/previousTotalSupply/rates/velocityLegPasses/lastReadBlock
- freeClaimed/freePct only when fresh non-None (None = unreadable, keep old)
- runNote0231 only where supply changed, velocity passed, or core-wave item
- track_c IMARS -> excluded (opened, free pool 0); add Ninetailix age-excluded
- top-level note_0231_run summary"""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
vel = json.load(open(f"{BASE}/run-2026-11-08-0231-velocity.json"))
re = json.load(open(f"{BASE}/run-2026-11-08-0231-reread.json"))
BLOCK = vel["block"]  # 132259484
CORE = {"HIVE Agents","Bubblebruin","Zapcourier","Cryonyx","Cathodex","Kirinova",
        "Gourdwick","Lensorb","Hotpotsage","Neonraven","Hachiko","SynapseSquad",
        "SeanceSociety","Plutopop","Ghoulipop","Servobun","Xianyulo","Vesperfang","Ioforge"}
def num(x):
    if isinstance(x,bool): return None
    if isinstance(x,int): return x
    if isinstance(x,str):
        try: return int(x,16) if x.startswith("0x") else int(x)
        except Exception: return None
    return None
updated=0; noted=0
for row in vel.get("rows",[]):
    name=row.get("name"); s=snap["contracts"].get(name)
    if s is None: continue
    cur=num(row.get("curSupply")); prev=num(row.get("prevSupply"))
    changed = cur is not None and cur != num(s.get("totalSupply"))
    if cur is not None: s["totalSupply"]=cur
    if prev is not None: s["previousTotalSupply"]=prev
    s["mintedInInterval"]=row.get("mintedInInterval")
    s["intervalMinutes"]=row.get("intervalMin")
    s["currentRatePerMin"]=row.get("ratePerMin")
    s["previousRatePerMin"]=row.get("prevRatePerMin")
    s["velocityLegPasses"]=bool(row.get("velocityPasses"))
    s["velocityRatio"]=row.get("ratioVsPrev")
    s["lastReadBlock"]=BLOCK
    s["lastReadWib"]="2026-11-08 run 0231"
    fc=row.get("freeCounter")
    if fc is not None:
        s["freeClaimed"]=fc
        if row.get("freePct") is not None: s["freePctVerified"]=row["freePct"]
    bal=num(row.get("balanceOf_user"))
    if bal is not None: s["balanceOf_user"]=bal
    updated+=1
    if changed or row.get("velocityPasses") or name in CORE:
        minted=row.get("mintedInInterval")
        s["runNote0231"]=(f"Run 0231 (blok {BLOCK}): totalSupply {cur} (prev {prev}), "
            f"minted interval {minted}, velocity {'LOLOS' if row.get('velocityPasses') else 'GAGAL'}"
            f" (rate {row.get('ratePerMin')}/mnt, ratio {row.get('ratioVsPrev')}); "
            f"balanceOf(user)={bal if bal is not None else 'tidak terbaca (nilai lama dipertahankan)'}; "
            f"status {s.get('status')}.")
        noted+=1
# velocity-pass annotations (no promotion: Alchemister free% unverified; Cybermoth age >48h)
for nm,why in [("Alchemister","velocity LOLOS 3.12x (+30) TAPI TIDAK promosi: free% UNVERIFIED (free counter tidak terbaca run ini), X/website unverified; tetap early-lead."),
               ("Cybermoth","velocity LOLOS 2.6x (+25), free 34.03% TAPI TIDAK promosi: umur >48 jam (terdeteksi 2026-11-04 14:31); tetap watchlist-only.")]:
    if nm in snap["contracts"]:
        snap["contracts"][nm]["runNote0231"]=snap["contracts"][nm].get("runNote0231","")+" "+why
# track_c IMARS: opened 0->1 with free pool already 0 -> excluded, report once
tc=snap.get("track_c",{})
im=tc.get("IMARS")
if isinstance(im,dict):
    im["status"]="excluded-opened-free-pool-exhausted-2026-11-08"
    im["note0231"]=("Run 0231 (blok 132260121): opened 0 -> 1 (BARU DIBUKA), freeMinted 300/300 FREE_SHARES "
        "(pool gratis HABIS sejak run 1601), totalMinted 624. Dibuka tanpa pool gratis -> MATI sebagai lead gratis. "
        "Dilaporkan sekali run ini; hapus dari tracking aktif.")
# Ninetailix age-excluded (track_c, S1 sale-shape per hot leg; first mint verified)
tc["Ninetailix"]={
 "address":"0x809215729bcbff2ef31dea5efd6c12a6b788ba9a",
 "status":"age-excluded-2026-11-08",
 "note":"Boltbook ZH run 0231 (post drzein.ai ~02:46 WIB, klaim 3->17 agent dalam 3 mnt @ 02:26 WIB); hot leg shape-check 02:44:38 WIB S1=True (mint+quote+freeClaimed/freeFor/freeLeft/freeUsed+agent). First mint terverifikasi blok 131064636 = 2026-11-01 21:25:41 WIB (timestamp blok via dataseed) -> umur ~6,5 hari > 48 jam -> AGE-EXCLUDED. Bukan early lead (bukan first-seen; sudah di scan 2026-11-01 2131). State run 0231 blok 132261154: totalSupply 428, freeClaimed 429/518 (82,8%), FREE_SUPPLY 518, MAX_SUPPLY 691, mintOpen 1, mintedBy(user)=0, freeLeft(user)=1 (slot terbuka tapi umur menggugurkan). Klaim post '3->17' tidak cocok dengan totalSupply 428, tidak dipakai sebagai bukti fase baru. Tidak dilaporkan sebagai lead.",
 "firstMintBlock":131064636,"firstMintWib":"2026-11-01 21:25:41 WIB",
 "totalSupply":428,"freeClaimed":429,"FREE_SUPPLY":518,"MAX_SUPPLY":691,
 "freePct":82.8,"mintOpen":1,"userSlotOpen":True}
snap["track_c"]=tc
snap["note_0231_run"]=("Run 0231: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat baru, "
 "0 pembukaan track-B. Re-read 443 kontrak + 69 track_c (blok 132259484); velocity LOLOS: Alchemister (3.12x, free% unverified, tanpa promosi), "
 "Cybermoth (2.6x, free 34.03%, umur >48h, tanpa promosi). Scan window 132258428-132259427 partial (enrich 96/108, 0 first-seen); 5c 1 baru dicek no-shape. "
 "binanceai launched 0/failed 1/refund 1 (identik); Grove freeOpen 0; bridge tidak berubah; Sourcify 20 kontrak 0 hit. "
 "Perubahan status: IMARS dibuka (opened 0->1) tapi pool gratis 0 -> excluded; Ninetailix age-excluded (first mint 2026-11-01 21:25 WIB). "
 "Seen dinormalisasi ke lowercase (12733 -> 11099 alamat unik); track-c-scan-checked 2876 -> 2877. Aturan diam: tidak ada laporan chat kecuali perubahan IMARS (sekali).")
json.dump(snap,open(f"{BASE}/onchain-snapshot.json","w"),indent=1)
print("contracts updated:",updated,"noted:",noted)
print("snapshot rewritten OK")
