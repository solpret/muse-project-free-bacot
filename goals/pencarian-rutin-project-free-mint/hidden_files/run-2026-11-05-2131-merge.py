#!/usr/bin/env python3
"""FREE BACOT main run 2026-11-05 2131 — parent merge.
Applies route-1 re-read, age-exclusions, AgentGlyph sellout, NIANNIAN
status correction, track-C re-read, NJAR/BINANCEAI, + scan (A) / Boltbook (B)
findings filled in by parent after subagent reports.
Read-only on-chain; only writes snapshot + run notes. No preview/mint."""
import json, shutil, copy
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
RUN = "2131"
READ_BLOCK = 131837412  # first (killed) run BLOCK; reread reads span ~22:00-22:05 WIB
READ_WIB = "2026-11-05 22:03:02 WIB"
INTERVAL_MIN = 49.5  # vs 2101 baseline block 131830817 = 21:13:34 WIB

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot-2131.bak.json")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
r = json.load(open(f"{BASE}/run-2026-11-05-2131-reread-lean.json"))
contracts = s.setdefault("contracts", {})
excluded = s.setdefault("excluded", {})

def upd(name, **kw):
    e = contracts.get(name)
    if e is None:
        print("WARN not in snapshot:", name); return
    for k, v in kw.items():
        if v is not None:
            e[k] = v

# ---- Route 1: fresh readings (null = keep old, never zero) ----
for name, d in r["reread"].items():
    e = contracts.get(name)
    if e is None:
        print("WARN reread item not in snapshot:", name); continue
    for f in ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"]:
        if d.get(f) is not None:
            e[f] = d[f]
    if d.get("balanceOf_user") is not None:
        e["balanceOf_user"] = d["balanceOf_user"]
    e["lastReadBlock"] = READ_BLOCK
    e["lastReadWib"] = f"2026-11-05 run {RUN}"

# ---- Velocity notes (interval 49.5 min vs 2101 baseline block 131830817) ----
VEL = {
 "HIVE Agents": "Run 2131 (blok 131837412, 22:03:02 WIB, interval 49,5 mnt vs run 2101): 1253 flat -> velocity GAGAL.",
 "Thronemind": "Run 2131: 624->631 (+7, 0,142/mnt vs prev 0,11 = 1,29x, <20 token) -> velocity GAGAL.",
 "Hashseers": "Run 2131: 567->572 (+5, 0,101/mnt vs prev 0,082 = 1,23x, <20) -> velocity GAGAL.",
 "Smeltbots": "Run 2131: 578->581 (+3, 0,061/mnt vs prev 0,137 = 0,44x) -> velocity GAGAL.",
 "Forklings": "Run 2131: 719->753 (+34, 0,687/mnt vs prev 0,904 = 0,76x) -> velocity GAGAL.",
 "Agent Frogs": "Run 2131: 386->389 (+3, <20) -> velocity GAGAL.",
 "PassAgentX": "Run 2131: 3608->3634 (+26, 0,526/mnt vs prev 0,877 = 0,60x) -> velocity GAGAL.",
 "StarAgent-7d39": "Run 2131: 1055->1061 (+6, 0,121/mnt vs prev 0,082 = 1,48x, <20 dan <1,5x) -> velocity GAGAL.",
 "wheelz": "Run 2131: 248->266 (+18, 0,364/mnt vs prev 0,384 = 0,95x, <20) -> velocity GAGAL.",
 "Layerloom": "Run 2131: 603->615 (+12, 0,243/mnt vs prev 0,11 = 2,21x tapi +12 <20) -> velocity GAGAL.",
 "Tumblebots": "Run 2131: 600->614 (+14, 0,283/mnt vs prev 0,137 = 2,07x tapi +14 <20) -> velocity GAGAL.",
 "AgentGlyph": "Run 2131: 504->512 (+8); freeClaimed 512/512 = 100% -> FREE POOL HABIS (lihat sellout).",
 "Neurolucha": "Run 2131: 378 flat -> velocity GAGAL.",
 "Kitebots": "Run 2131: 570->608 (+38, 0,768/mnt vs prev 1,094 = 0,70x) -> velocity GAGAL.",
 "Roguefall": "Run 2131: 236 flat -> velocity GAGAL.",
 "Agent Goats": "Run 2131: 123 flat -> velocity GAGAL.",
 "Agent Owls": "Run 2131: 131 flat -> velocity GAGAL.",
 "Hirelings-A": "Run 2131: 128 flat -> velocity GAGAL.",
 "Hirelings-B": "Run 2131: 94 flat -> velocity GAGAL.",
 "Auspibots": "Run 2131: 145 flat -> velocity GAGAL.",
 "Driftnauts": "Run 2131: 602->604 (+2, 0,040/mnt vs prev 3,269 = 0,01x) -> velocity GAGAL.",
 "Jolly": "Run 2131: totalMinted 3424->3471 (+47, 0,950/mnt vs prev 0,475 = 2,00x, >=20) -> velocity LULUS run ini; TETAP strong-lead-gate-blocked (gate FAILED, sudah dilaporkan) -> TIDAK ada promosi/eksekusi. Age-exclude 23:27 WIB malam ini (first mint 2026-11-03 23:27:33 WIB).",
 "AgentFounder": "Run 2131: totalMinted 101 (totalSupply read null); freeMinted/freeClaimed null (bacaan gagal, BUKAN nol). Delta mixed-view (totalSupply 80 -> totalMinted 101) TIDAK dipakai sebagai velocity pass (counter tidak konsisten: freeMinted tercatat 98 > totalSupply 80). Free % tetap 44,14% (98/222, lama) <50%; slot user UNVERIFIED -> tetap EARLY, bukan strong lead/kandidat.",
 "Agent Coffee": "Run 2131: totalSupply 391->597 (+206, 4,16/mnt) tapi previousRatePerMin null (baseline belum ada) -> velocity TIDAK lulus run ini per aturan (record baseline saja). Free % tetap UNVERIFIED; website UNVERIFIED (run 1501) -> tetap EARLY.",
 "GHOST": "Run 2131: totalSupply 258->267 (+9), freeMinted 224->232; FREE_SUPPLY() tetap tidak merespons -> free % UNVERIFIED. Interval pertama (baseline) -> velocity TIDAK lulus run ini. Slot: quote(user,1)=0, mintOpen=1 (freeClaimed(user)/balance null run ini, nilai lama 0 dipertahankan). Tetap EARLY.",
 "Sonofluidic": "Run 2131: totalSupply 169->186 (+17), freeMinted 169->186 = 8,23% dari FREE_SUPPLY 2260 (<25%). Interval pertama (baseline) -> velocity TIDAK lulus run ini. Slot: mintOpen=1 (freeClaimed(user)/balance null run ini, nilai lama 0 dipertahankan). Tetap EARLY.",
 "Mossminds": "Run 2131: totalSupply/totalMinted null (bacaan gagal, BUKAN nol); freeMinted 456->607 = 21,08% dari FREE_CAP 2880 (<25%). Velocity TIDAK dihitung (totalSupply null; konvensi run sebelumnya: null -> nilai lama dipertahankan, velocity tidak dihitung). canFreeMint(user)=1, claimedFree(user)=0 segar. Tetap EARLY.",
 "SEAT-f11e": "Run 2131: totalSupply null (bacaan gagal, BUKAN nol; nilai lama 2127 dipertahankan) -> velocity TIDAK dihitung.",
 "Cachejack": "Run 2131: totalSupply null (bacaan gagal, BUKAN nol; nilai lama 371 dipertahankan) -> velocity TIDAK dihitung.",
 "AgentMiner": "Run 2131: totalSupply null (bacaan gagal, BUKAN nol; nilai lama 593 dipertahankan) -> velocity TIDAK dihitung.",
 "BNB CACHE Server": "Run 2131: semua supply view null (bacaan gagal, BUKAN nol; nilai lama dipertahankan) -> velocity TIDAK dihitung.",
 "Mummyhive": "Run 2131: totalSupply 600 flat -> velocity GAGAL.",
 "WAGagent": "Run 2131: totalSupply tidak berubah (nilai raksasa = totalSupply token, bukan NFT count) -> velocity GAGAL; track-C lead gate-blocked, tidak berubah.",
 "LuckyBox-d08e": "Run 2131: totalSupply 488 (bacaan pertama run ini; baseline lama null) -> velocity TIDAK dihitung.",
 "SnailMail": "Run 2131: totalSupply 266 (bacaan pertama run ini; baseline lama null) -> velocity TIDAK dihitung.",
 "AgentBox": "Run 2131: semua supply view null (bacaan gagal, BUKAN nol) -> velocity TIDAK dihitung; tetap EARLY.",
}
for name, note in VEL.items():
    if name in contracts:
        contracts[name]["velocityNote2131"] = note
        contracts[name]["currentRatePerMin"] = {
            "Jolly": 0.950, "Agent Coffee": 4.16, "GHOST": 0.182, "Sonofluidic": 0.343,
            "Thronemind": 0.142, "Hashseers": 0.101, "Smeltbots": 0.061, "Forklings": 0.687,
            "PassAgentX": 0.526, "StarAgent-7d39": 0.121, "wheelz": 0.364, "Layerloom": 0.243,
            "Tumblebots": 0.283, "Kitebots": 0.768, "Driftnauts": 0.040,
        }.get(name, contracts[name].get("currentRatePerMin"))
        contracts[name]["previousTotalSupply"] = {
            "HIVE Agents": 1253, "Thronemind": 624, "Hashseers": 567, "Smeltbots": 578,
            "Forklings": 719, "Agent Frogs": 386, "PassAgentX": 3608, "StarAgent-7d39": 1055,
            "wheelz": 248, "Layerloom": 603, "Tumblebots": 600, "AgentGlyph": 504,
            "Neurolucha": 378, "Kitebots": 570, "Roguefall": 236, "Agent Goats": 123,
            "Agent Owls": 131, "Hirelings-A": 128, "Hirelings-B": 94, "Auspibots": 145,
            "Driftnauts": 602, "Jolly": 3424, "Mummyhive": 600,
        }.get(name, contracts[name].get("previousTotalSupply"))
contracts["Jolly"]["velocityVerified"] = True
contracts["Jolly"]["velocityLegPasses"] = True
contracts["GHOST"]["previousTotalSupply"] = 258
contracts["GHOST"]["currentRatePerMin"] = 0.182
contracts["GHOST"]["previousRatePerMin"] = None
contracts["Sonofluidic"]["previousTotalSupply"] = 169
contracts["Sonofluidic"]["currentRatePerMin"] = 0.343
contracts["Sonofluidic"]["previousRatePerMin"] = None
contracts["Sonofluidic"]["freePctVerified"] = 8.23
contracts["Agent Coffee"]["previousTotalSupply"] = 391
contracts["Agent Coffee"]["previousRatePerMin"] = None
contracts["Mossminds"]["freeMinted"] = 607
contracts["Mossminds"]["freePctVerified"] = 21.08
contracts["AgentGlyph"]["totalSupply"] = 512
contracts["AgentGlyph"]["freeClaimed"] = 512
contracts["AgentGlyph"]["freePctVerified"] = 100.0

# ---- AgentGlyph: free pool sellout -> report once + remove from active ----
ag = contracts.pop("AgentGlyph")
ag["status"] = "excluded-sold-out-free-pool-2026-11-05"
ag["selloutNote2131"] = ("Run 2131: freeClaimed 512/512 = 100% (FREE_SUPPLY 512), totalSupply 512, "
    "mintOpen=1, quote(user,1)=0,0001 BNB (paid lane). Free pool HABIS; slot gratis user hilang. "
    "Dilaporkan sekali sebagai perubahan + dihapus dari kontrak aktif.")
excluded["AgentGlyph"] = ag

# ---- Age-exclusions (verified first mint >48h at read, not sold out) ----
AGE = [
 ("Odbeast-3Bf0", "first mint terverifikasi 2026-11-03 17:15:24 WIB (firstMintWib; Ankr getLogs) = 52,9 jam; freeMinted 42 (MAX_SUPPLY 4477; dulu 42/4000 = 1,1%), totalSupply null run ini (bacaan gagal, BUKAN nol) -> belum sold out."),
 ("Chipbotcore", "first mint terverifikasi 2026-11-03 20:03:12 WIB (blok 131437541, Ankr) = 50,0 jam; freeClaimed terakhir 301/3333 = 9,0%, mintOpen=1 segar, FREE_SUPPLY/MAX_SUPPLY 3333 -> belum sold out."),
 ("Cuprihive", "first mint terverifikasi 2026-11-03 20:01:26 WIB (blok 131437305, Ankr) = 50,0 jam; freeClaimed terakhir 383/3333 = 11,5%, mintOpen=1 segar, FREE_SUPPLY/MAX_SUPPLY 3333 -> belum sold out."),
 ("Peony Agent", "first mint terverifikasi blok 131293278 = 2026-11-03 02:00:55 WIB (eth_getBlockByNumber) = 68,0 jam; totalMinted segar 426/1763 = 24,2% (FREE_SUPPLY 425; free pool ~penuh tapi koleksi belum sold out) -> belum sold out."),
 ("QAFUAI", "first mint terverifikasi blok 131293860 = 2026-11-03 02:05:17 WIB = 68,0 jam; freeMinted segar 95, MAX_SUPPLY 10000, mintOpen=1 -> belum sold out."),
 ("Analyxis", "first mint terverifikasi blok 131395859 = 2026-11-03 14:50:30 WIB = 55,2 jam; totalSupply segar 316, freeClaimed 311/1439 = 21,6%, mintOpen=1 -> belum sold out."),
 ("Compasyn", "first mint terverifikasi blok 131395989 = 2026-11-03 14:51:28 WIB = 55,2 jam; totalSupply segar 406, freeClaimed 401/1490 = 26,9%, mintOpen=1 -> belum sold out."),
]
for name, ev in AGE:
    e = contracts.pop(name, None)
    if e is None:
        print("WARN age-exclusion target missing:", name); continue
    e["status"] = "excluded-age-over-48h-2026-11-05"
    e["ageExclusionNote2131"] = f"Run 2131 AGE-EXCLUDED (>48 jam, belum sold out): {ev} Dihapus dari kontrak aktif, dipindah ke excluded."
    excluded[name] = e
    print("age-excluded:", name)

# ---- NIANNIAN: user-named + minted by user 2026-11-03 ~17:20 WIB (#1195) -> correct status, retain ----
if "NIANNIAN" in contracts:
    contracts["NIANNIAN"]["status"] = "minted-by-user-2026-11-03"
    contracts["NIANNIAN"]["correctionNote2131"] = ("KOREKSI run 2131: NIANNIAN adalah user-named (nianniangent.fun) dan SUDAH di-mint "
        "user 2026-11-03 ~17:20 WIB (NianNian #1195, free, kuota gratis terpakai — memory 2026-11-03). Status lama "
        "'watchlist-only-not-early' SALAH; dikoreksi ke minted-by-user. Exempt dari tes umur 48 jam (user-named + sudah di-mint). "
        "Bacaan segar run ini semua null (RPC gagal baca view kontrak, BUKAN nol) — nilai lama dipertahankan. TIDAK di-age-exclude.")
    print("NIANNIAN status corrected to minted-by-user")

# ---- PeachClub: age >48h BUT sold-out state unreadable -> retain with flag ----
if "PeachClub" in contracts:
    contracts["PeachClub"]["ageNote2131"] = ("Run 2131: first mint terverifikasi blok 131394942 = 2026-11-03 14:43:37 WIB (>48 jam, ~55,3 jam) "
        "NAMUN status sold-out TIDAK BISA diverifikasi: semua view supply (totalSupply/totalMinted/freeClaimed/freeMinted/FREE_SUPPLY/MAX_SUPPLY/mintOpen) "
        "null dalam 2x percobaan RPC (bacaan gagal, BUKAN nol) dan snapshot tidak menyimpan nilai lama. Age-exclusion DITUNDA sampai ada bacaan "
        "supply yang berhasil — jangan hapus atas dasar tanpa bukti.")
    print("PeachClub retained (sold-out unverifiable)")

# ---- Track-C re-read ----
tc = s.setdefault("track_c", {})
for k, d in r["track_c"].items():
    e = tc.get(k)
    if e is None:
        print("WARN track_c item not in snapshot:", k); continue
    for f in ["freeMinted", "freeSharesRemaining", "totalMinted", "sharesMinted",
              "opened", "launched", "phase", "saleEnded"]:
        if d.get(f) is not None:
            e[f] = d[f]
    e["lastReadBlock"] = READ_BLOCK
    e["lastReadWib"] = f"2026-11-05 run {RUN}"
njar = r.get("njar", {})
if "NJAR" in tc:
    if njar.get("giftsClaimed") is not None:
        tc["NJAR"]["giftsClaimed"] = njar["giftsClaimed"]
    tc["NJAR"]["lastReadBlock"] = READ_BLOCK
    tc["NJAR"]["lastReadWib"] = f"2026-11-05 run {RUN}"
    tc["NJAR"]["runNote2131"] = ("Run 2131: giftsClaimed 511->530 (+19), live=1, paidSharesSold=3; giftTaken/hasAgent null "
        "(nilai lama dipertahankan). Gate TETAP GAGAL (sudah dilaporkan blocked) -> tidak berubah tier, TIDAK di-preview/di-mint.")
    print("NJAR giftsClaimed ->", njar.get("giftsClaimed"))

s["runNote2131_binanceai"] = ("Run 2131: BINANCEAI launched=0, failed=null (bacaan gagal run ini; terakhir 1 di run 2101), "
    "isRefundPhase=1, tokenClaimed(user)=0 — tetap refund/failed, pending_claims kosong, tidak dilaporkan ulang.")
s["last_run"] = f"2026-11-05-{RUN}"
s["last_run_wib"] = f"2026-11-05 run {RUN}"

# NOTE: runNote2131 (main) + runNote2131_scan are appended by parent after
# subagent A/B reports arrive; scan additions (new first-seen contracts)
# are merged in a second pass below (placeholders).
s["runNote2131_age_exclusions"] = (
    "Run 2131 AGE-EXCLUSIONS (7 item, dilaporkan sekali sebagai perubahan): Odbeast-3Bf0 "
    "(first mint 2026-11-03 17:15:24 WIB, freeMinted 42/4000), Chipbotcore (first mint 2026-11-03 "
    "20:03:12 WIB, 301/3333, mintOpen=1), Cuprihive (first mint 2026-11-03 20:01:26 WIB, 383/3333, "
    "mintOpen=1), Peony Agent (first mint blok 131293278 = 2026-11-03 02:00:55 WIB, totalMinted 426/1763), "
    "QAFUAI (first mint blok 131293860 = 2026-11-03 02:05:17 WIB, freeMinted 95, mintOpen=1), Analyxis "
    "(first mint blok 131395859 = 2026-11-03 14:50:30 WIB, 311/1439, mintOpen=1), Compasyn (first mint blok "
    "131395989 = 2026-11-03 14:51:28 WIB, 401/1490, mintOpen=1) — semuanya first mint terverifikasi >48 jam "
    "dan belum sold out per bacaan segar run 2131 -> DIHAPUS dari kontrak aktif, dipindah ke excluded "
    "(status excluded-age-over-48h-2026-11-05). DIPERTAHANKAN: NIANNIAN (dikoreksi ke minted-by-user 2026-11-03, "
    "user-named + sudah di-mint, exempt umur), PeachClub (first mint >48 jam tapi status sold-out TIDAK bisa "
    "diverifikasi — semua view supply null 2x percobaan; exclusion ditunda sampai ada bacaan), semua item "
    "minted-by-user lain, dan promotion-discarded-same-owner. Jolly lewat 48 jam 2026-11-05 23:27 WIB "
    "(belum saat run ini; velocity LULUS run ini tapi gate tetap FAILED).")
s["runNote2131_sellout"] = (
    "Run 2131 SELLOUT (1 item, dilaporkan sekali sebagai perubahan): AgentGlyph freeClaimed 512/512 = 100% "
    "(FREE_SUPPLY 512), totalSupply 512 — free pool HABIS, slot gratis user hilang (quote(user,1)=0,0001 BNB, paid lane). "
    "Dihapus dari kontrak aktif (status excluded-sold-out-free-pool-2026-11-05).")

json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("MERGE PART 1 DONE: contracts now", len(s["contracts"]), "| excluded now", len(s["excluded"]))
