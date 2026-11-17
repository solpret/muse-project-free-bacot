#!/usr/bin/env python3
"""Run 2026-11-06 0631 WIB: apply leg-1 + track-C re-reads to the snapshot (fresh reads only,
None never overwrites), record scan stall #4 in scan-state. Backups written first."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0631"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-0631")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-0631")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
r = json.load(open(f"{BASE}/run-2026-11-06-0631-reread-lean.json"))["reread"]
tc = json.load(open(f"{BASE}/run-2026-11-06-0631-reread-tc.json"))["track_c"]
blk = json.load(open(f"{BASE}/run-2026-11-06-0631-reread-lean.json")).get("block")

# --- Track A contracts: fresh totalSupply/totalMinted only ---
for name, vals in r.items():
    e = s["contracts"].get(name)
    if e is None:
        continue
    fresh_ts = vals.get("totalSupply")
    fresh_tm = vals.get("totalMinted")
    if fresh_ts is not None:
        e["previousTotalSupply"] = e.get("totalSupply")
        e["totalSupply"] = fresh_ts
    if fresh_tm is not None:
        e["previousTotalSupply"] = e.get("totalMinted", e.get("totalSupply"))
        e["totalMinted"] = fresh_tm
    if vals.get("balanceOf_user") is not None:
        e["balanceOf_user"] = vals["balanceOf_user"]
    e["lastReadBlock"] = blk
    e["lastReadWib"] = "2026-11-06 run 0631"

k = s["contracts"]["KING Agent"]
k["velocityNote0631"] = ("Run 0631 (blok 131905343): totalMinted 423->515 (+92 sejak bacaan sukses run 0531, "
    "~68 mnt = 1,35/mnt vs prev 1,73 = 0,78x) -> velocity GAGAL (butuh >=1,5x DAN >=20 token). "
    "Free % inferensi 515/3333=15,5% <25% kaki strong-lead. Slot user: costOf/mintedBy/balanceOf gagal baca run ini "
    "(nilai lama terbuka dipertahankan). Tetap EARLY, bukan promosi, NEVER preview/mint.")
k["currentRatePerMin"] = 1.35
k["previousRatePerMin"] = 1.73
k["mintedInInterval"] = 92
k["intervalMinutes"] = 68
k["freePctVerified"] = None

m = s["contracts"]["MILLION"]
m["runNote0631"] = ("Run 0631: totalMinted/freeMinted/freeClaimed gagal baca (nilai lama totalMinted 74 dipertahankan); "
    "FREE_SUPPLY 500 terkonfirmasi ulang, balanceOf(user)=0. Velocity TIDAK terhitung. Tetap EARLY, bukan promosi.")
h = s["contracts"]["HIVE Agents"]
h["runNote0631"] = ("Run 0631 (blok 131905343): totalSupply 1253 flat vs run 0601 (1253) -> velocity GAGAL; "
    "balanceOf(user) gagal baca run ini (nilai lama 1 dipertahankan); minted-by-user, bukan kandidat.")
for name, note in [
    ("Thronemind", "Run 0631: totalSupply 653->657 (+4); strong-lead-gate-blocked, tidak berubah."),
    ("Hashseers", "Run 0631: totalSupply 593 flat; strong-lead-gate-blocked, tidak berubah."),
    ("Smeltbots", "Run 0631: totalSupply 611 flat; strong-lead-gate-blocked, tidak berubah."),
    ("Forklings", "Run 0631: totalSupply 916->919 (+3); strong-lead-gate-blocked, tidak berubah."),
    ("Agent Frogs", "Run 0631: totalSupply 413->430 (+17), freeClaimed 413->430; strong-lead-gate-blocked, tidak berubah."),
    ("PassAgentX", "Run 0631: totalSupply 3901->3938 (+37); early lead, tidak berubah."),
    ("SEAT-f11e", "Run 0631: totalSupply 2576->2724 (+148), totalMinted 2626->2725; watchlist-only, free % unverified, bukan promosi."),
    ("Mummyhive", "Run 0631: totalSupply 600 (bacaan pertama; freeClaimed lama 582); tidak berubah."),
    ("Layerloom", "Run 0631: freeMinted 660 flat; strong-lead-gate-blocked, tidak berubah."),
    ("Mossminds", "Run 0631: claimedFree(user)=0, balanceOf(user)=0; promotion-discarded-same-owner, tidak berubah."),
    ("Jolly", "Run 0631: balanceOf(user)=0; totalMinted gagal baca (nilai lama 3645 dipertahankan)."),
    ("SnailMail", "Run 0631: mintedBy(user)=0, price()=0.0002 BNB; totalSupply gagal baca (nilai lama 305 dipertahankan)."),
    ("wheelz", "Run 0631: mintedBy(user)=0, price()=0.0002 BNB; totalSupply gagal baca (nilai lama 311 dipertahankan)."),
    ("StarAgent-7d39", "Run 0631: semua supply view gagal baca (nilai lama 1106 dipertahankan); early lead, tidak berubah."),
    ("WAGagent", "Run 0631: semua supply view gagal baca; track-c-lead-gate-blocked, tidak berubah."),
    ("Tumblebots", "Run 0631: semua supply view gagal baca (nilai lama 656 dipertahankan); strong-lead-gate-blocked, tidak berubah."),
    ("AgentGlyph", "Run 0631: semua view gagal baca (freeClaimed lama 512/512, pool habis); tidak berubah."),
    ("Pacture", "Run 0631: semua view gagal baca (freeMinted lama 7700 dipertahankan); tidak berubah."),
    ("LuckyBox-d08e", "Run 0631: quote(user,1)=0; totalSupply gagal baca (nilai lama 621 dipertahankan); tidak berubah."),
]:
    e = s["contracts"].get(name)
    if e is not None:
        e["runNote0631"] = note

# --- Track C: fresh reads only ---
TCMAP = {"OSK": "OSK", "DROID": "DROID", "IMARS": "IMARS", "QAGENT-2": "QAGENT-2",
         "ASOC-43cE": "ASOC-43cE", "SENBAZURU-b215": "SENBAZURU-b215", "SAFUAI": "SAFUAI"}
for snap_key, tc_key in TCMAP.items():
    e = s["track_c"].get(snap_key)
    v = tc.get(tc_key)
    if e is None or v is None:
        continue
    for f in ("opened", "launched", "freeMinted", "totalMinted", "sharesMinted",
              "freeSharesRemaining", "saleEnded"):
        if v.get(f) is not None:
            e[f] = v[f]
    if v.get("freeClaimed_user") is not None:
        e["freeClaimed_user"] = v["freeClaimed_user"]
s["track_c"]["OSK"]["note0631"] = "Run 0631: opened 0 - tetap belum dibuka."
s["track_c"]["DROID"]["note0631"] = "Run 0631: opened 0, freeMinted/totalMinted 587 flat vs run 0601 - tetap belum dibuka."
s["track_c"]["IMARS"]["note0631"] = ("Run 0631: opened 1, freeMinted 300/300 FREE_SHARES - TERBUKA tapi pool gratis HABIS "
    "(diketahui sejak run 0601); BUKAN lead, tidak dilaporkan ulang.")
s["track_c"]["QAGENT-2"]["note0631"] = "Run 0631: freeMinted 6666 flat, freeClaimed(user)=1 (claimed-by-user); tidak berubah."
s["track_c"]["ASOC-43cE"]["note0631"] = "Run 0631: freeClaimed(user)=0, saleEnded=0 - tidak berubah."
s["track_c"]["SENBAZURU-b215"]["note0631"] = "Run 0631: opened 1, launched 0 - tetap belum launched (claimed-by-user)."
s["track_c"]["SAFUAI"]["note0631"] = "Run 0631: opened 1 - checked-not-a-lead, tidak berubah."

s["runNote0631"] = ("Run 0631 SILENT: no new candidate/strong lead/early lead/track-C; scan route 4 GAGAL/STALL ke-4 "
    "berturut-turut (timeout 780, 0 byte log, ~3 dtk CPU). KING totalMinted 423->515 (+92, velocity 0,78x GAGAL, "
    "free inferensi 15,5% <25%); HIVE flat 1253; SEAT +148 (watchlist-only). Boltbook newest post unchanged "
    "(2026-11-05T09:20:52Z); Sourcify 20 kontrak baru, 13 sudah dicek hot leg 0619, 7 dicek run ini (S1/S2=false semua, "
    "3 ABI retry-exhausted); Odaily/PANews 0 mention Agent ID; bridge 0 not-in-snapshot; binanceai tetap refund/failed.")
s["runNote0631_scan"] = ("Run 0631: SCAN GAGAL/STALL ke-4 berturut-turut. Percobaan 1 (satu-satunya): timeout 780, 0 byte log, "
    "~3 dtk CPU, di-kill (SCAN_EXIT=124) - pola sama run 0431/0531/0601. Watermark TIDAK dimajukan (tetap 131895548); "
    "seen file TIDAK berubah; 5c dilewati (tanpa output scan). Window belum ter-scan: 131895549-131906xxx+ "
    "(gap ~10.800 blok dilewati cap 2000).")
s["last_run_wib"] = "2026-11-06 run 0631"
s["last_run"] = "2026-11-06-0631"
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)

st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["note_0631_scan_failed"] = ("Run 0631: SCAN GAGAL/STALL ke-4 berturut-turut (timeout 780, 0 byte log, ~3 dtk CPU, "
    "SCAN_EXIT=124; pola sama run 0431/0531/0601). Watermark TIDAK dimajukan (tetap 131895548); seen file TIDAK berubah; "
    "5c dilewati. Window belum ter-scan: 131895549-131906372+ (gap ~10.824 blok dilewati cap 2000).")
st["last_scan_failed_wib"] = "2026-11-06 run 0631"
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("snapshot + scan-state updated; backups 0631 written")
