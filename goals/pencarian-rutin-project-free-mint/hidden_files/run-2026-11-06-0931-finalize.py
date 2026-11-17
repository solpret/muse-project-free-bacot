#!/usr/bin/env python3
"""Run 2026-11-06 0931 WIB finalize (lean).
1. Snapshot: re-read numeric updates (None never overwrites) + velocity notes.
2. bridge-0x93bf08d2 -> snapshot contracts as bridge finding (NOT a lead, no report).
3. MILLION probe note (free views revert = absent, not RPC failure).
4. Scan-state note: route-4 scan FAILED/STALL (7th in sequence incl. 0431..0731 pattern;
   pre-flight OK 5.4s, 0-byte log, ~1s CPU in 3+ min, killed); watermark NOT advanced (131927747).
   5c skipped (no scan output). Backfill gap unchanged: 131919215-131926747 + 131927748-head.
5. last_run fields. Backs up snapshot first. Never touches scan-bridge.json."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-0931"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-0931")
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
 "Cipher Mind":[("totalMinted","totalMinted")],
 "Cyber Lynx Agent":[("totalMinted","totalMinted")],
 "Crack":[("totalSupply","totalSupply"),("totalMinted","totalMinted"),("publicRemaining","publicRemaining")],
}
for name,pairs in NUMMAP.items():
    if name not in C or name not in RR.get("reread",{}): continue
    for snapk,rrk in pairs:
        setv(C[name],snapk,RR["reread"][name].get(rrk))
    C[name]["lastReadBlock"]=BLK
    C[name]["lastReadWib"]="2026-11-06 run 0931"
# velocity notes (interval 0901-read block 131927703 -> 0931-read block 131930977 = 3274 blocks ~24.5 min)
def vel(name, old_supply_key, note):
    e=C.get(name)
    if e is not None: e["runNote0931"]=note
vel("HIVE Agents","totalSupply","Run 0931 (blok 131930977): totalSupply 1253 flat vs run 0901 (1253) -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
vel("KING Agent","totalMinted","Run 0931 (blok 131930977): totalMinted 708->730 (+22, ~24,5 mnt = ~0,90/mnt vs prev ~0,92/mnt = ~0,98x) -> velocity GAGAL (token >=20 terpenuhi, rasio gagal). Free 730/3333=21,90% <25% kaki strong-lead. Slot user terbuka (costOf 0, mintedBy 0, balance 0). Tetap EARLY.")
vel("SEAT-f11e","totalSupply","Run 0931: totalSupply/totalMinted 3532->3562 (+30, ~24,5 mnt = ~1,22/mnt vs prev ~2,24/mnt = ~0,55x) -> velocity GAGAL; free % unverified; watchlist-only.")
vel("Forklings","freeMinted","Run 0931: freeMinted 935->943 (+8, <20) -> velocity GAGAL; 943/2000=47,15% <50%; watchlist-only.")
vel("PassAgentX","freeMinted","Run 0931: totalSupply 3980->3997 (+17), freeMinted 3766->3779 (+13, <20) -> velocity GAGAL; watchlist-only.")
vel("MILLION","totalMinted","Run 0931 (blok 131930977): totalMinted 94->174 (+80 sejak baca sukses terakhir run 0801 blok 131919121, ~89 mnt = ~0,90/mnt) — rate pertama yang terhitung (previous rate null), velocity TIDAK lulus run ini (butuh rasio vs rate sebelumnya). Probe run 0931: freeMinted/freeClaimed/canFreeMint/quote/mintCost SEMUA REVERT di dataseed (fungsi tidak ada, BUKAN gagal RPC); FREE_SUPPLY 500 + agentRegistry()=registry terkonfirmasi. Free leg tetap UNVERIFIED, slot UNVERIFIED, website/X UNVERIFIED. Tetap EARLY, bukan strong lead, bukan kandidat.")
# bridge finding 0x93bf08d2
C["bridge-0x93bf08d2"]={
 "address":"0x93bf08d2936aefe0cd2ceba8f76cb566fdf9e1c9","status":"bridge-finding-2026-11-06-run0931",
 "name":"Unnamed ERC20 (bridge)","kind":"ERC20",
 "note":"Temuan pelengkap scan (bridge run-71, 09:05 WIB): Unnamed ERC20, name()/symbol() EMPTY, PAID mint 0,03 BNB, 1 entity, distribution/tracker-like, gate website_no_pointer_found, contractURI() REVERTS, Sourcify 404. BUKAN agent-shaped, BUKAN lead, TIDAK dilaporkan sebagai lead (aturan bridge). Watchlist-only.",
 "firstSeenWib":"2026-11-06 run 0931","lastReadBlock":BLK}
# track_c DROID totalMinted update
TC=snap.setdefault("track_c",{})
if "DROID" in TC: setv(TC["DROID"],"totalMinted",604)
if "Crack" in TC:
    setv(TC["Crack"],"totalSupply",902); setv(TC["Crack"],"totalMinted",902); setv(TC["Crack"],"publicRemaining",4603)
    TC["Crack"]["runNote0931"]="Run 0931: totalSupply/totalMinted 794->902 (+108 sejak mint), publicRemaining 4723->4603; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 — mint berikutnya BERBAYAR (0,001 BNB), TIDAK diotorisasi."
snap["last_run"]="2026-11-06 run 0931"
snap["last_run_wib"]="2026-11-06T09:31:00+07:00"
snap["runNote0931"]="Run 0931 SILENT: no new candidate/strong/early lead, no track-B change, no track-C lead/candidate, no sellout, no age-exclusion, no lost free slot. Route-4 scan FAILED/STALL (pre-flight OK 5,4 dtk; 0-byte log, ~1 dtk CPU, di-kill setelah ~3 mnt); watermark TIDAK maju (131927747); 5c dilewati. MILLION +80 (94->174) tapi free leg tetap UNVERIFIED (free views revert = fungsi tidak ada). KING +22 velocity GAGAL (rasio ~0,98x). Bridge 0x93bf08d2 ditambahkan sebagai temuan pelengkap scan (bukan lead)."
snap["runNote0931_scan"]="Run 0931: SCAN GAGAL/STALL ke-7 (pola 0431/0531/0601/0631/0701/0731): pre-flight OK 5,4 dtk (head 131931014, 1000 logs), scan 1000 blok terbaru (131930015-131931014) 0 chunk selesai, 0 byte log, ~1 dtk CPU dalam ~3 mnt, di-kill manual. Watermark TIDAK dimajukan (tetap 131927747); seen file TIDAK berubah; 5c dilewati (tanpa output scan). Gap belum ter-cover: 131919215-131926747 (backfill) + 131927748-head."
json.dump(snap,open(f"{BASE}/onchain-snapshot.json","w"),indent=1)
# scan state note
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st["note_0931_scan"]="Run 0931: SCAN GAGAL/STALL ke-7 (timeout 780 tidak ditunggu; pre-flight OK 5,4 dtk, 0 chunk, 0 byte log, ~1 dtk CPU, di-kill ~3 mnt). Watermark TIDAK dimajukan (tetap 131927747); seen TIDAK berubah; 5c dilewati. Gap: 131919215-131926747 (backfill) + 131927748-head."
json.dump(st,open(f"{BASE}/onchain-scan-state.json","w"),indent=1)
print("FINALIZE OK; contracts:",len(C),"track_c:",len(TC))
