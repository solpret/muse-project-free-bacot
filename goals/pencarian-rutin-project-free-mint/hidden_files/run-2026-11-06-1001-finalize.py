#!/usr/bin/env python3
"""Run 2026-11-06 1001 WIB finalize.
1. Snapshot numeric updates (None never overwrites) + velocity notes.
   Interval 0931-read blok 131930977 -> 1001-read blok 131933381 = 2404 blok ~18,0 mnt.
2. CantonTron -> contracts + track_c as gate-failed-blocked (already reported by hot leg 10:10 WIB; NOT re-reported).
   Qilinara -> NOT added (age-excluded: first mint 2026-11-02 16:49:46 WIB, 89,7 jam >48 jam).
3. Seen file: 6 first-seen appended to nested contracts (lowercase).
4. Scan-state: watermark -> 131933579 (scan SUKSES pertama setelah 7 gagal); skipped gap 131927748-131932579 (backfill).
5. Track-C: Crack totalSupply 963, publicRemaining 4542. Never touches scan-bridge.json."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-1001"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1001")
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=snap.setdefault("contracts",{})
RR=json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
TG=json.load(open(f"{BASE}/run-{TS}-reread-targeted.json"))
BLK=RR["block"]
def setv(e,k,v):
    if v is not None: e[k]=v
NUMMAP={
 "HIVE Agents":[("totalSupply","totalSupply")],
 "KING Agent":[("totalMinted","totalMinted"),("remainingFree","remainingFree")],
 "Mummyhive":[("totalSupply","totalSupply"),("freeClaimed","freeClaimed")],
 "Thronemind":[("totalSupply","totalSupply"),("freeMinted","freeMinted")],
 "Hashseers":[("freeMinted","freeMinted")],
 "Smeltbots":[("totalSupply","totalSupply"),("freeMinted","freeMinted")],
 "Forklings":[("freeMinted","freeMinted")],
 "Agent Frogs":[("totalSupply","totalSupply"),("freeClaimed","freeClaimed")],
 "PassAgentX":[("totalSupply","totalSupply"),("freeMinted","freeMinted")],
 "SEAT-f11e":[("totalSupply","totalSupply"),("totalMinted","totalMinted")],
 "LuckyBox-d08e":[("totalSupply","totalSupply")],
 "Tumblebots":[("totalSupply","totalSupply"),("freeMinted","freeMinted")],
 "Mossminds":[("totalSupply","totalSupply"),("freeMinted","freeMinted")],
 "Jolly":[("totalMinted","totalMinted"),("freeMinted","freeMinted")],
 "AgentGlyph":[("totalSupply","totalSupply"),("freeClaimed","freeClaimed")],
 "Layerloom":[("totalSupply","totalSupply"),("freeMinted","freeMinted")],
 "Pacture":[("freeMinted","freeMinted")],
 "Nebula Ape Agent":[("totalMinted","totalMinted")],
 "Shadow Yeti Agent":[("totalMinted","totalMinted")],
 "Silent Hydra Agent":[("totalMinted","totalMinted")],
 "Cipher Wraith Agent":[("totalMinted","totalMinted")],
 "Umbra Lynx Agent":[("totalMinted","totalMinted")],
 "Data Synth":[("totalMinted","totalMinted")],
 "Zero Genesis":[("totalMinted","totalMinted")],
 "MILLION":[("totalMinted","totalMinted")],
 "FOD Agent":[("totalMinted","totalMinted")],
 "StarAgent-7d39":[("totalSupply","totalSupply")],
 "SnailMail":[("totalSupply","totalSupply")],
 "Crack":[("totalSupply","totalSupply"),("totalMinted","totalMinted"),("publicRemaining","publicRemaining")],
}
for name,pairs in NUMMAP.items():
    if name not in C or name not in RR.get("reread",{}): continue
    for snapk,rrk in pairs:
        setv(C[name],snapk,RR["reread"][name].get(rrk))
    C[name]["lastReadBlock"]=BLK
    C[name]["lastReadWib"]="2026-11-06 run 1001"
# targeted 4 (Cipher Mind, Cyber Lynx, Storm Sprite, Void Jaguar): totalMinted still 1
for name in ["Cipher Mind","Cyber Lynx Agent","Storm Sprite Agent","Void Jaguar Agent"]:
    if name in C and name in TG:
        setv(C[name],"totalMinted",TG[name].get("totalMinted"))
        C[name]["lastReadBlock"]=BLK
        C[name]["lastReadWib"]="2026-11-06 run 1001"
# velocity notes (interval ~18,0 mnt: 2404 blok x ~0,45 dtk)
def vel(name,note):
    if name in C: C[name]["runNote1001"]=note
vel("HIVE Agents","Run 1001 (blok 131933381): totalSupply 1253 flat vs run 0931 (1253) -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
vel("KING Agent","Run 1001 (blok 131933381): totalMinted 730->738 (+8, ~18,0 mnt = ~0,44/mnt vs prev ~0,90/mnt = ~0,49x) -> velocity GAGAL (token <20 DAN rasio gagal). Free 738/3333=22,14% <25% kaki strong-lead. Slot user terbuka (costOf 0, mintedBy 0, balance 0). Tetap EARLY.")
vel("MILLION","Run 1001 (blok 131933381): totalMinted 174->176 (+2, <20) -> velocity GAGAL. Free leg tetap UNVERIFIED (free views revert = fungsi tidak ada, probe run 0931). Tetap EARLY, bukan strong lead, bukan kandidat.")
vel("SEAT-f11e","Run 1001: totalSupply/totalMinted 3562->3597 (+35, ~18,0 mnt = ~1,94/mnt vs prev 2,384/mnt = ~0,81x) -> velocity GAGAL (token >=20 terpenuhi, rasio gagal); free % unverified; watchlist-only.")
vel("Forklings","Run 1001: freeMinted 943->946 (+3, <20) -> velocity GAGAL; 946/2000=47,30% <50%; watchlist-only.")
vel("PassAgentX","Run 1001: totalSupply 3997->4004 (+7), freeMinted 3779->3786 (+7, <20) -> velocity GAGAL; watchlist-only.")
vel("FOD Agent","Run 1001: totalMinted 500 flat vs run 0931 (500) -> velocity GAGAL; costOf(user,1)=0,0005 BNB (paid leg); tetap EARLY.")
vel("Cipher Mind","Run 1001 (targeted): totalMinted tetap 1, spotsLeft 3332, PRICE 0,0005 BNB — template paid-only, tidak ada pergerakan; tetap EARLY.")
vel("Cyber Lynx Agent","Run 1001 (targeted): totalMinted tetap 1, spotsLeft 3332, PRICE 0,0005 BNB — template paid-only, tidak ada pergerakan; tetap EARLY.")
vel("Storm Sprite Agent","Run 1001 (targeted): totalMinted tetap 1, spotsLeft 3332, PRICE 0,0005 BNB — template paid-only, tidak ada pergerakan; tetap EARLY.")
vel("Void Jaguar Agent","Run 1001 (targeted): totalMinted tetap 1, spotsLeft 3332, PRICE 0,0005 BNB — template paid-only, tidak ada pergerakan; tetap EARLY.")
# rate fields for next run
if "KING Agent" in C:
    C["KING Agent"]["previousTotalSupply"]=730; C["KING Agent"]["mintedInInterval"]=8
    C["KING Agent"]["intervalMinutes"]=18.0; C["KING Agent"]["currentRatePerMin"]=0.44
    C["KING Agent"]["previousRatePerMin"]=0.90; C["KING Agent"]["velocityLegPasses"]=False
if "MILLION" in C:
    C["MILLION"]["previousTotalSupply"]=174; C["MILLION"]["mintedInInterval"]=2
    C["MILLION"]["intervalMinutes"]=18.0; C["MILLION"]["currentRatePerMin"]=0.11
    C["MILLION"]["previousRatePerMin"]=None; C["MILLION"]["velocityLegPasses"]=False
if "SEAT-f11e" in C:
    C["SEAT-f11e"]["previousTotalSupply"]=3562; C["SEAT-f11e"]["mintedInInterval"]=35
    C["SEAT-f11e"]["intervalMinutes"]=18.0; C["SEAT-f11e"]["currentRatePerMin"]=1.94
    C["SEAT-f11e"]["previousRatePerMin"]=2.384; C["SEAT-f11e"]["velocityLegPasses"]=False
# CantonTron -> contracts + track_c (gate-failed, already reported by hot leg 10:10 WIB)
C["CantonTron"]={
 "address":"0x921150815bF267a17bb372E44e6e3f44a05f54af","status":"track-c-blocked-gate-failed-2026-11-06",
 "name":"CantonTron","symbol":"CBOT","kind":"ERC721",
 "totalMinted":63,"MAX_SUPPLY":3333,"mintOpen":1,
 "freeUsed_user":0,"balanceOf_user":0,
 "firstSeenBlock":131932802,"firstMintWib":"2026-11-06 09:50:40 WIB",
 "ageNote":"VERIFIED <=48h: first mint Transfer-from-zero blok 131931747 = 2026-11-06 09:50:40 WIB (Ankr getLogs address-filtered 131900000..latest: 65 logs, earliest 131931747; totalMinted 63 saat baca). Sourcify verifiedAt 2026-11-06T02:55:32Z (09:55:32 WIB). Umur ~35 mnt saat triase.",
 "freeNote":"Free % UNVERIFIED: tidak ada freeClaimed/freeMinted/freeLeft/FREE_SUPPLY view (ABI: freeMint + freeUsed saja); totalMinted 63/3333 = 1,9% dari MAX_SUPPLY. Bukan strong lead (butuh >=25% free terverifikasi).",
 "gateNote":"MANDATORY WEBSITE GATE FAILED — sudah dilaporkan hot leg 2026-11-06 10:10 WIB sebagai track-C lead blocked (S1, age verified, slot open); metode gate A/B/C/G/H/I/J/K/L/M dicoba hot leg, tidak ada website ditemukan; pencarian nama run 1001 juga 0 hit CantonTron. TIDAK PERNAH di-preview/di-mint. TIDAK dilaporkan ulang run ini (dedupe lintas job).",
 "lastReadBlock":BLK,"lastReadWib":"2026-11-06 run 1001"}
TC=snap.setdefault("track_c",{})
TC["CantonTron"]={
 "sale":"0x921150815bF267a17bb372E44e6e3f44a05f54af","token":"0x921150815bF267a17bb372E44e6e3f44a05f54af",
 "status":"blocked-gate-failed-2026-11-06",
 "saleShape":"PASS (S1): mint/freeMint + costFor/priceAt + freeUsed + agentIdRegistry = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify verified",
 "name":"CantonTron","symbol":"CBOT","kind":"ERC721",
 "totalMinted":63,"MAX_SUPPLY":3333,"mintOpen":1,"freeUsed_user":0,"balanceOf_user":0,
 "ageNote":"VERIFIED <=48h: first mint 2026-11-06 09:50:40 WIB (blok 131931747).",
 "gateNote":"GATE FAILED (hot leg 10:10 WIB): metode A/B/C/G/H/I/J/K/L/M, tidak ada website. TIDAK PERNAH di-preview/di-mint.",
 "firstSeenWib":"2026-11-06 run 1001","lastReadBlock":BLK}
# Track-C Crack update
if "Crack" in TC:
    setv(TC["Crack"],"totalSupply",963); setv(TC["Crack"],"totalMinted",963); setv(TC["Crack"],"publicRemaining",4542)
    TC["Crack"]["runNote1001"]="Run 1001: totalSupply/totalMinted 902->963 (+61), publicRemaining 4603->4542; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 — mint berikutnya BERBAYAR (0,001 BNB), TIDAK diotorisasi."
snap["last_run"]="2026-11-06 run 1001"
snap["last_run_wib"]="2026-11-06T10:01:00+07:00"
snap["runNote1001"]="Run 1001 SILENT: no new candidate/strong/early lead, no track-B change, no track-C lead/candidate, no sellout, no age-exclusion of a watchlist item, no lost free slot. Route-4 scan SUKSES (pertama setelah 7 gagal): window 131932580-131933579, 40 panggilan Ankr, 0 error, 216 NFT + 286 ERC20-mint, 6 first-seen. CantonTron: agent-shaped, first mint 09:50:40 WIB terverifikasi, TAPI sudah dilaporkan hot leg 10:10 WIB sebagai track-C lead blocked (gate website FAILED) — TIDAK dilaporkan ulang; masuk snapshot track_c + contracts sebagai blocked. Qilinara: agent-shaped tapi first mint 2026-11-02 16:49:46 WIB (89,7 jam >48 jam) + free 278/1907=14,58% <25% — AGE-EXCLUDED, tidak masuk snapshot, tidak dilaporkan. 5c: 40 ERC20 mint>=10, 13 baru dicek, 0 sale shape. KING +8 velocity GAGAL; MILLION +2; SEAT +35 rasio 0,81x GAGAL."
snap["runNote1001_scan"]="Run 1001: SCAN SUKSES (pre-flight OK 2,7 dtk, head 131933312; 20 chunk selesai + shape-check ~14 mnt, total ~15 mnt). Watermark 131927747 -> 131933579. Gap 131927748-131932579 (4832 blok) belum ter-cover (backfill). 6 first-seen: CantonTron (agent-shaped, gate-failed, hot-leg-reported), Qilinara (agent-shaped, age-excluded 89,7 jam), GDEX RBOX + GladiatorDex Weapon/Shield + Einstein NFT (bukan agent-shaped, log only)."
json.dump(snap,open(f"{BASE}/onchain-snapshot.json","w"),indent=1)
# seen file: append 6 first-seen
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc=seen.setdefault("contracts",{})
scan=json.load(open(f"{BASE}/onchain-scan-2026-11-06-1001.json"))
added=0
for c in scan["contracts"]:
    a=c["address"].lower()
    if a not in sc:
        sc[a]=c["first_block"]; added+=1
seen["_meta"]["last_scan_wib"]="2026-11-06 run 1001"
seen["_meta"]["last_scan_window"]="131932580-131933579"
seen["_meta"]["last_scan_added"]=added
seen["_meta"]["last_updated_wib"]="2026-11-06 run 1001"
seen["_meta"]["note_1001"]="Run 1001: 6 first-seen appended (CantonTron CBOT, Qilinara QILIN, GDEX RBOX, GladiatorDex Weapon, GladiatorDex Shield, Einstein NFT EINNFT). CantonTron agent-shaped (registry+freeMint, first mint 09:50:40 WIB) tapi gate-failed + hot-leg-reported 10:10 WIB. Qilinara agent-shaped (registry+free views) tapi first mint 2026-11-02 16:49:46 WIB (89,7 jam) -> age-excluded. 4 sisanya bukan agent-shaped."
json.dump(seen,open(f"{BASE}/onchain-scan-seen.json","w"),indent=1)
# scan state
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"]=131933579
st["last_scan_window_from"]=131932580
st["last_scan_window_to"]=131933579
st["last_scan_wib"]="run 2026-11-06-1001"
st["ankr_calls"]=40
st["errors"]=[]
st["nft_contracts"]=216
st["erc20_mint_contracts"]=286
st["skipped_gap"]="131927748-131932579 (4832 blok; window dari watermark 131927747 ke head 131933579 = 5832 blok > cap 1000; scan menutup 1000 blok terbaru 131932580-131933579)"
st["note_1001_scan"]="Run 1001: SCAN SUKSES (pertama setelah 7 gagal/stall 0431-0931). Pre-flight OK 2,7 dtk (head 131933312, 482 logs). 20 chunk selesai, shape-check ~14 mnt, total ~15 mnt, 40 panggilan Ankr, 0 error. Watermark 131927747 -> 131933579. 6 first-seen, 2 agent-shaped (CantonTron gate-failed, Qilinara age-excluded). 5c: 13 ERC20 baru dicek, 0 sale shape. Gap 131927748-131932579 belum ter-cover (backfill)."
json.dump(st,open(f"{BASE}/onchain-scan-state.json","w"),indent=1)
print("FINALIZE OK; contracts:",len(C),"track_c:",len(TC),"seen added:",added)
