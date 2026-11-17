#!/usr/bin/env python3
"""Run 2026-11-06 1031 WIB finalize.
1. Snapshot numeric updates (None never overwrites) + velocity notes.
   Interval 1001-read blok 131933381 (10:02:56 WIB) -> 1031-read blok 131937922 (10:37:00 WIB) = 34,1 mnt.
2. Scan first-seen: 5 true first-seen; 3 agent-shaped-ish (Sushimon, CRT Codes, Shenlong) ALL
   AGE-EXCLUDED (>48h: first mint Nov 1 21:31 / Nov 2 08:02 / Nov 1 21:15 WIB) -> NOT added to
   snapshot, NOT reported (Qilinara precedent run 1001). DGDreams + Catagent NOT agent-shaped.
3. Seen file: all scan-window contracts not yet in seen (5 first-seen + 3 in-snapshot).
4. Scan-state: watermark -> 131937878 (scan SUKSES); skipped gap 131933580-131936878 (backfill).
5. Track-C: Crack totalSupply 1059, publicRemaining 4446. Never touches scan-bridge.json."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-1031"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1031")
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=snap.setdefault("contracts",{})
RR=json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
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
    C[name]["lastReadWib"]="2026-11-06 run 1031"
# track_c readable values
TC=snap.setdefault("track_c",{})
TCMAP={
 "OSK":[("opened","opened")],
 "DROID":[("opened","opened"),("freeMinted","freeMinted")],
 "IMARS":[("opened","opened"),("freeMinted","freeMinted")],
 "QAGENT-2":[("freeMinted","freeMinted"),("sharesMinted","sharesMinted")],
 "SENBAZURU-b215":[("opened","opened"),("launched","launched"),("phase","phase")],
 "SAFUAI":[("opened","opened"),("totalMinted","totalMinted")],
 "NIULAI":[("launched","launched"),("phase","phase")],
 "KillZero-K0-sale":[("launched","launched")],
 "ShibAgent-R2":[("phase","phase")],
 "Ikigai-Ihigi":[("freeMinted","freeMinted"),("phase","phase")],
 "ASOC-43cE":[("saleEnded","saleEnded")],
}
for name,pairs in TCMAP.items():
    if name not in TC or name not in RR.get("track_c",{}): continue
    for snapk,rrk in pairs:
        setv(TC[name],snapk,RR["track_c"][name].get(rrk))
def vel(name,note):
    if name in C: C[name]["runNote1031"]=note
vel("HIVE Agents","Run 1031 (blok 131937922): totalSupply 1253 flat vs run 1001 (1253) -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
vel("KING Agent","Run 1031 (blok 131937922): totalMinted 738->759 (+21, 34,1 mnt = 0,616/mnt vs prev 0,44/mnt = 1,40x) -> velocity GAGAL (rasio <1,5x; token >=20 terpenuhi). Free 759/3333=22,77% <25% kaki strong-lead. Slot user terbuka (costOf 0, mintedBy 0, balance 0). Tetap EARLY.")
vel("MILLION","Run 1031 (blok 131937922): totalMinted 178 flat vs hot leg 1029 (178); +2 vs run 1001 (176), <20 -> velocity GAGAL. Free leg tetap UNVERIFIED (free views revert). Tetap EARLY, bukan strong lead, bukan kandidat.")
vel("SEAT-f11e","Run 1031: totalSupply/totalMinted 3597->3648 (+51, 34,1 mnt = 1,497/mnt vs prev 1,94/mnt = 0,77x) -> velocity GAGAL (rasio gagal); free % unverified; watchlist-only.")
vel("Forklings","Run 1031: freeMinted 946->951 (+5, <20) -> velocity GAGAL; 951/2000=47,55% <50%; watchlist-only.")
vel("PassAgentX","Run 1031: totalSupply 4004->4009 (+5), freeMinted 3786->3791 (+5, <20) -> velocity GAGAL; watchlist-only.")
vel("FOD Agent","Run 1031: totalMinted 500 flat vs run 1001 (500) -> velocity GAGAL; costOf(user,1)=0,0005 BNB (paid leg); tetap EARLY.")
vel("Thronemind","Run 1031: totalSupply 671->673 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("Hashseers","Run 1031: totalSupply 605->607 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("Smeltbots","Run 1031: freeMinted 622->625 (+3, <20) -> velocity GAGAL; watchlist-only.")
vel("Agent Frogs","Run 1031: totalSupply 437->438 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("StarAgent-7d39","Run 1031: totalSupply 1117->1119 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("Layerloom","Run 1031: totalSupply 702->719 (+17, <20) -> velocity GAGAL; watchlist-only.")
vel("Tumblebots","Run 1031: totalSupply 678->680 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("Mossminds","Run 1031: totalSupply 932->940 (+8, <20) -> velocity GAGAL; watchlist-only.")
vel("Jolly","Run 1031: totalMinted 3663->3667 (+4, <20) -> velocity GAGAL; watchlist-only.")
vel("LuckyBox-d08e","Run 1031: totalSupply 632->633 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("SnailMail","Run 1031: totalSupply 311->315 (+4, <20) -> velocity GAGAL; watchlist-only.")
# rate fields for next run
if "KING Agent" in C:
    C["KING Agent"]["previousTotalSupply"]=738; C["KING Agent"]["mintedInInterval"]=21
    C["KING Agent"]["intervalMinutes"]=34.1; C["KING Agent"]["currentRatePerMin"]=0.616
    C["KING Agent"]["previousRatePerMin"]=0.44; C["KING Agent"]["velocityLegPasses"]=False
if "MILLION" in C:
    C["MILLION"]["previousTotalSupply"]=176; C["MILLION"]["mintedInInterval"]=2
    C["MILLION"]["intervalMinutes"]=34.1; C["MILLION"]["currentRatePerMin"]=0.059
    C["MILLION"]["previousRatePerMin"]=0.11; C["MILLION"]["velocityLegPasses"]=False
if "SEAT-f11e" in C:
    C["SEAT-f11e"]["previousTotalSupply"]=3597; C["SEAT-f11e"]["mintedInInterval"]=51
    C["SEAT-f11e"]["intervalMinutes"]=34.1; C["SEAT-f11e"]["currentRatePerMin"]=1.497
    C["SEAT-f11e"]["previousRatePerMin"]=1.94; C["SEAT-f11e"]["velocityLegPasses"]=False
# Track-C Crack update
if "Crack" in TC:
    setv(TC["Crack"],"totalSupply",1059); setv(TC["Crack"],"totalMinted",1059); setv(TC["Crack"],"publicRemaining",4446)
    TC["Crack"]["runNote1031"]="Run 1031: totalSupply/totalMinted 963->1059 (+96), publicRemaining 4542->4446; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 — mint berikutnya BERBAYAR (0,001 BNB), TIDAK diotorisasi."
snap["last_run"]="2026-11-06 run 1031"
snap["last_run_wib"]="2026-11-06T10:31:00+07:00"
snap["runNote1031"]="Run 1031 SILENT: no new candidate/strong/early lead, no track-B change, no track-C lead/candidate, no sellout, no age-exclusion of a watchlist item, no lost free slot. Route-4 scan SUKSES: window 131936879-131937878, 40 panggilan Ankr, 0 error, 185 NFT + 329 ERC20-mint, 5 first-seen. Sushimon (agent-shaped, free 2662/7000=38,03%, slot open) TAPI first mint 2026-11-01 21:31:30 WIB (109,5 jam >48 jam) -> AGE-EXCLUDED, tidak masuk snapshot, tidak dilaporkan. CRT Codes (registry+WEBSITE/X_LINK, tanpa free view) first mint 2026-11-02 08:02:49 WIB (98,9 jam) -> AGE-EXCLUDED. Shenlong (registry+FREE_MINTS) first mint 2026-11-01 21:15:13 WIB (109,7 jam) -> AGE-EXCLUDED. DGDreams (Boltbook 10:25 WIB) + Catagent bukan agent-shaped, log only. 5c: 36 ERC20 mint>=10, 8 baru dicek, 0 sale shape. KING +21 velocity GAGAL (1,40x); SEAT +51 rasio 0,77x GAGAL; Forklings 47,55% <50%."
snap["runNote1031_scan"]="Run 1031: SCAN SUKSES (pre-flight OK 9,0 dtk retry pertama timeout transient; head 131937828; 20 chunk selesai + shape-check, total ~16 mnt). Watermark 131933579 -> 131937878. Gap 131933580-131936878 (3299 blok) belum ter-cover (backfill). 5 first-seen: Sushimon (age-excluded 109,5 jam), CRT Codes (age-excluded 98,9 jam), Shenlong (age-excluded 109,7 jam), DGDreams (bukan agent-shaped), Catagent (bukan agent-shaped). 5c: 8 ERC20 baru dicek, 0 sale shape."
json.dump(snap,open(f"{BASE}/onchain-snapshot.json","w"),indent=1)
# seen file: append scan-window contracts not yet in seen
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc=seen.setdefault("contracts",{})
scan=json.load(open(f"{BASE}/onchain-scan-2026-11-06-1031.json"))
added=0
for c in scan["contracts"]:
    a=c["address"].lower()
    if a not in sc:
        sc[a]=c["first_block"]; added+=1
seen["_meta"]["last_scan_wib"]="2026-11-06 run 1031"
seen["_meta"]["last_scan_window"]="131936879-131937878"
seen["_meta"]["last_scan_added"]=added
seen["_meta"]["last_updated_wib"]="2026-11-06 run 1031"
seen["_meta"]["note_1031"]="Run 1031: 5 first-seen appended (Sushimon SUSHIMON, CRT Codes CRT, Shenlong SHENLONG, DGDreams DGB-BNB, Catagent CATAGENT) + 3 in-snapshot top-up. Sushimon agent-shaped (AGENT_ID + free views, free 2662/7000=38,03%, quote(user,1)=0, slot open) tapi first mint 2026-11-01 21:31:30 WIB (109,5 jam) -> AGE-EXCLUDED. CRT Codes agent-shaped (AGENT_REGISTRY + WEBSITE https://crtcodes.pages.dev + X_LINK https://x.com/CRTCodes, tanpa free view, quote 0) tapi first mint 2026-11-02 08:02:49 WIB (98,9 jam) -> AGE-EXCLUDED. Shenlong agent-shaped (agentRegistry + FREE_MINTS=4, freeMintsLeft(user)=4, mintPrice 0,002 BNB) tapi first mint 2026-11-01 21:15:13 WIB (109,7 jam) -> AGE-EXCLUDED. DGDreams + Catagent bukan agent-shaped."
json.dump(seen,open(f"{BASE}/onchain-scan-seen.json","w"),indent=1)
# scan state
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"]=131937878
st["last_scan_window_from"]=131936879
st["last_scan_window_to"]=131937878
st["last_scan_wib"]="run 2026-11-06-1031"
st["ankr_calls"]=40
st["errors"]=[]
st["nft_contracts"]=185
st["erc20_mint_contracts"]=329
st["skipped_gap"]="131933580-131936878 (3299 blok; window dari watermark 131933579 ke head 131937878 = 4299 blok > cap 1000; scan menutup 1000 blok terbaru 131936879-131937878)"
st["note_1031_scan"]="Run 1031: SCAN SUKSES (pre-flight OK 9,0 dtk setelah retry pertama timeout transient fast_rpc; head 131937828, 1000 logs). 20 chunk selesai + shape-check, total ~16 mnt, 40 panggilan Ankr, 0 error. Watermark 131933579 -> 131937878. 5 first-seen, 3 agent-shaped (Sushimon, CRT Codes, Shenlong) SEMUA age-excluded (>48 jam: 109,5 / 98,9 / 109,7 jam). 5c: 8 ERC20 baru dicek, 0 sale shape. Gap 131933580-131936878 belum ter-cover (backfill). Catatan: proses wait-loop run ini sempat self-match pgrep (pola pgrep cocok dengan cmdline wait-loop sendiri) — scan selesai normal, JSON tertulis 10:51 WIB."
json.dump(st,open(f"{BASE}/onchain-scan-state.json","w"),indent=1)
print("FINALIZE OK; contracts:",len(C),"track_c:",len(TC),"seen added:",added)
