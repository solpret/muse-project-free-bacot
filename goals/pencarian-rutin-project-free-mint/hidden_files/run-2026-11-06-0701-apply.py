#!/usr/bin/env python3
"""Run 2026-11-06 0701 WIB: apply leg-1 + track-C re-reads to the snapshot (fresh reads only,
None never overwrites), remove sold-out bridge-Agent Harvest Land-2, record scan stall #5.
Backups written first. Block-rate note: BSC now ~0.45s/block (4257 blocks in 31.9 min between
0631 and 0701 reads) - the body's '~600 blocks per 30 min' assumption is stale; 2000-block cap
now covers only ~15 min, gap grows ~2000 blocks/run."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0701"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-0701")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-0701")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
r = json.load(open(f"{BASE}/run-2026-11-06-0701-reread-lean.json"))["reread"]
tc = json.load(open(f"{BASE}/run-2026-11-06-0701-reread-tc.json"))["track_c"]
blk = json.load(open(f"{BASE}/run-2026-11-06-0701-reread-lean.json")).get("block")

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
    for f in ("freeClaimed", "freeMinted", "FREE_SUPPLY"):
        if vals.get(f) is not None:
            e[f] = vals[f]
    if vals.get("balanceOf_user") is not None:
        e["balanceOf_user"] = vals["balanceOf_user"]
    e["lastReadBlock"] = blk
    e["lastReadWib"] = "2026-11-06 run 0701"

k = s["contracts"]["KING Agent"]
k["velocityNote0701"] = ("Run 0701 (blok 131909600, 07:04:31 WIB): totalMinted 515->562 (+47 dalam 31,9 mnt "
    "= 1,47/mnt vs prev 1,35 = 1,09x) -> velocity GAGAL (butuh >=1,5x DAN >=20 token). "
    "Free % inferensi 562/3333=16,9% <25% kaki strong-lead; remainingFree 2771. Slot user terbuka "
    "(costOf 0, mintedBy 0, balance 0, agentGateOn 1, mintOpen 1). Tetap EARLY, bukan promosi, NEVER preview/mint.")
k["currentRatePerMin"] = 1.47
k["previousRatePerMin"] = 1.35
k["mintedInInterval"] = 47
k["intervalMinutes"] = 31.9
k["remainingFree"] = 2771
k["freePctVerified"] = None

m = s["contracts"]["MILLION"]
m["runNote0701"] = ("Run 0701: totalMinted 74->84 (+10 dalam 31,9 mnt, <20) -> velocity GAGAL. "
    "FREE_SUPPLY 500; freeMinted/freeClaimed gagal baca (nilai lama dipertahankan). Tetap EARLY, bukan promosi.")
h = s["contracts"]["HIVE Agents"]
h["runNote0701"] = ("Run 0701 (blok 131909600): totalSupply 1253 flat vs run 0631 (1253) -> velocity GAGAL; "
    "balanceOf(user)=1; minted-by-user, bukan kandidat.")
for name, note in [
    ("Thronemind", "Run 0701: totalSupply 657->659 (+2), freeMinted 659; canFreeMint(user)=1; strong-lead-gate-blocked, tidak berubah."),
    ("Hashseers", "Run 0701: totalSupply 593 flat, freeMinted 593; canFreeMint(user)=1; strong-lead-gate-blocked, tidak berubah."),
    ("Smeltbots", "Run 0701: freeMinted 611 flat; canFreeMint(user)=1; strong-lead-gate-blocked, tidak berubah."),
    ("Forklings", "Run 0701: totalSupply 919->921 (+2), freeMinted 921; strong-lead-gate-blocked, tidak berubah."),
    ("Agent Frogs", "Run 0701: totalSupply 430->432 (+2), freeClaimed 432; strong-lead-gate-blocked, tidak berubah."),
    ("PassAgentX", "Run 0701: totalSupply 3938->3943 (+5), freeMinted 3725; early lead, tidak berubah."),
    ("SEAT-f11e", "Run 0701: totalMinted 2725->3019 (+294); watchlist-only, free % unverified, bukan promosi."),
    ("Mummyhive", "Run 0701: freeClaimed 582 (totalSupply gagal baca, nilai lama dipertahankan); tidak berubah."),
    ("Layerloom", "Run 0701: totalSupply 662, freeMinted 662; strong-lead-gate-blocked, tidak berubah."),
    ("Mossminds", "Run 0701: totalSupply 899, claimedFree(user)=0, balanceOf(user)=0; promotion-discarded-same-owner, tidak berubah."),
    ("Jolly", "Run 0701: freeMinted 3647 (totalSupply/totalMinted gagal baca); balanceOf(user)=0; tidak berubah."),
    ("SnailMail", "Run 0701: totalSupply 306, costOf(user,1)=0, mintsLeft 10, mintOpen 1, mintedBy(user)=0; tidak berubah."),
    ("wheelz", "Run 0701: totalSupply 312, mintsLeft 10, mintOpen 1; tidak berubah."),
    ("StarAgent-7d39", "Run 0701: totalSupply 1107 (bacaan pertama sukses setelah gagal run 0631); early lead, tidak berubah."),
    ("WAGagent", "Run 0701: totalSupply 10000000000000000000000000000 (nilai aneh, token-decimals view - bukan supply NFT); track-c-lead-gate-blocked, tidak berubah."),
    ("Tumblebots", "Run 0701: totalSupply 657, freeMinted 657; strong-lead-gate-blocked, tidak berubah."),
    ("AgentGlyph", "Run 0701: totalSupply 513, freeClaimed 512, FREE_SUPPLY 512 (pool habis); tidak berubah."),
    ("Pacture", "Run 0701: freeMinted 7700, freeClaimed(user)=1; tidak berubah."),
    ("LuckyBox-d08e", "Run 0701: totalSupply 626, quote(user,1)=0, freeUsed(user)=0; tidak berubah."),
]:
    e = s["contracts"].get(name)
    if e is not None:
        e["runNote0701"] = note

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
s["track_c"]["OSK"]["note0701"] = "Run 0701: opened None (gagal baca), totalMinted 2278 - tetap belum dibuka."
s["track_c"]["DROID"]["note0701"] = "Run 0701: opened 0, totalMinted 587 (freeMinted gagal baca run ini) - tetap belum dibuka."
s["track_c"]["IMARS"]["note0701"] = ("Run 0701: opened 1, freeMinted 300/300 FREE_SHARES - TERBUKA tapi pool gratis HABIS "
    "(diketahui sejak run 0601); BUKAN lead, tidak dilaporkan ulang.")
s["track_c"]["QAGENT-2"]["note0701"] = "Run 0701: freeMinted 6666 flat, sharesMinted 6702, freeClaimed(user)=1 (claimed-by-user); tidak berubah."
s["track_c"]["ASOC-43cE"]["note0701"] = "Run 0701: freeClaimed(user)=0, saleEnded=0 - tidak berubah."
s["track_c"]["SENBAZURU-b215"]["note0701"] = "Run 0701: opened 1, launched 0 - tetap belum launched (claimed-by-user)."
s["track_c"]["SAFUAI"]["note0701"] = "Run 0701: opened 1 - checked-not-a-lead, tidak berubah."

# --- Agent Harvest Land: free pool SOLD OUT -> remove from watchlist ---
ah = s["contracts"].pop("bridge-Agent Harvest Land-2", None)
s["runNote0701_agentharvest"] = ("REMOVED run 0701: bridge-Agent Harvest Land-2 (0xacf150d9eC909E3d339Bf4c6D090b18495674E66) "
    "free pool SOLD OUT - freeMinted 5000/5000 FREE_SUPPLY (was 4660/5000 run 2026-11-03), totalMinted 5620, "
    "read block 131910731, balanceOf(user)=0. Dilaporkan sekali sebagai sellout run ini, lalu dihapus dari snapshot. "
    "Website evidence ditemukan leg 3 run ini (agent-harvest.pages.dev, /skill.md HTTP 200 mencetak kontrak incl. "
    "HarvestLand, X https://x.com/agentharvest_ai) - tiba di run yang sama dengan sellout, jadi tidak ada promosi.")
assert ah is not None, "Agent Harvest entry missing!"

s["runNote0701"] = ("Run 0701: 1 perubahan dilaporkan - Agent Harvest Land free pool SOLD OUT (5000/5000), dihapus dari "
    "watchlist. Selain itu SILENT: no new candidate/strong lead/early lead/track-C; scan route 4 GAGAL/STALL ke-5 "
    "berturut-turut (timeout 780, 0 byte log, SCAN_EXIT=124). KING totalMinted 515->562 (+47, velocity 1,09x GAGAL, "
    "free inferensi 16,9% <25%); MILLION 74->84 (+10); HIVE flat 1253; SEAT +294 (watchlist-only). Boltbook newest post "
    "unchanged (2026-11-05T09:20:52Z); Sourcify 4 kontrak baru dicek (S1/S2=false semua); Odaily/PANews 0 mention "
    "Agent ID; bridge 0 not-in-snapshot; binanceai tetap refund/failed (launched=0).")
s["runNote0701_scan"] = ("Run 0701: SCAN GAGAL/STALL ke-5 berturut-turut. Percobaan 1 (satu-satunya): timeout 780, 0 byte log, "
    "SCAN_EXIT=124 - pola sama run 0431/0531/0601/0631. Watermark TIDAK dimajukan (tetap 131895548); seen file TIDAK "
    "berubah; 5c dilewati (tanpa output scan). Window belum ter-scan: 131895549-131911216+ (gap ~15.700 blok). "
    "CATATAN BLOCK-RATE: BSC kini ~0,45 dtk/blok (4257 blok dalam 31,9 mnt antar bacaan 0631->0701; terverifikasi via "
    "timestamp blok 131905343=06:32:35 dan 131909600=07:04:31 WIB) - asumsi body '~600 blok per 30 mnt' sudah usang; "
    "cap 2000 blok kini hanya menutup ~15 mnt, gap tumbuh ~2000 blok/run.")
s["last_run_wib"] = "2026-11-06 run 0701"
s["last_run"] = "2026-11-06-0701"
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)

st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["note_0701_scan_failed"] = ("Run 0701: SCAN GAGAL/STALL ke-5 berturut-turut (timeout 780, 0 byte log, SCAN_EXIT=124; "
    "pola sama run 0431/0531/0601/0631). Watermark TIDAK dimajukan (tetap 131895548); seen file TIDAK berubah; "
    "5c dilewati. Window belum ter-scan: 131895549-131911216+ (gap ~15.700 blok). Block-rate BSC ~0,45 dtk/blok "
    "terverifikasi run ini - cap 2000 blok hanya menutup ~15 mnt.")
st["last_scan_failed_wib"] = "2026-11-06 run 0701"
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)

# --- hot-leg-seen: 4 Sourcify contracts shape-checked this run ---
hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
shape = json.load(open(f"{BASE}/run-2026-11-06-0701-sourcify-shape.json"))
for c in shape:
    a = c["address"]
    if a not in hl:
        hl[a] = {"first_seen_wib": "2026-11-06T07:08:00+07:00",
                 "note": f"S1={c.get('S1')} S2={c.get('S2')} mint={bool(c.get('mint_fns'))} "
                         f"quote={bool(c.get('quote_fns'))} free={c.get('free_views')} agent={bool(c.get('gate_fns'))}",
                 "source": "sourcify-feed",
                 "status": "checked-not-sale-shape"}
json.dump(hl, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("snapshot + scan-state + hot-leg-seen updated; backups 0701 written; contracts now:",
      len(s["contracts"]), "hot-leg-seen:", len(hl))
