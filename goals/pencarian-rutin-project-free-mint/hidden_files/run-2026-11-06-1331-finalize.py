#!/usr/bin/env python3
"""Run 2026-11-06 1331 WIB finalize (parent).
Outcome: SILENT (0 kandidat/lead/promosi baru). Satu temuan verifikasi baru:
StarAgent-7d39 umur TERVERIFIKASI ~40,2 jam (first mint blok 131640557) -> tetap
<=48 jam, TIDAK age-excluded; tetap EARLY (velocity GAGAL + free % UNVERIFIED).
- Leg 1 re-read blok 131962334; interval vs run 1301 (blok 131959349, 13:17:43 WIB)
  ~22,39 mnt (estimasi 2985 blok x 0,45 dtk; timestamp blok tak terbaca, RPC degradasi).
  Semua velocity GAGAL kecuali CantonTron (track-C gate-failed, tidak berlaku).
- Leg 2 Boltbook: newest tetap 2026-11-05T09:20:52Z, 0 hit.
- Leg 3 sweep + Leg 6: tidak ada proyek baru; Odaily/PANews 0 mention; Square 0 link baru.
- Leg 4 SCAN GAGAL (enrichment stall pasca-chunk, pola sama run 1301; chunk 20/20
  selesai 131961352-131962351, ERC721 177, ERC1155 6, ERC20-mint 418, tapi TIDAK ADA
  JSON; proses hilang ~06:50:30 UTC karena RUNTIME RESTART, sebelum timeout 780 habis).
  Triase + 5c dilewati. Watermark TIDAK dimajukan scan ini (backfill paralel
  memajukan 131921548 -> 131927548 selama run ini).
- Leg 5a: 1 alamat baru Sourcify (0x57910724...), bukan sale shape. 5c dilewati.
- Track B binanceai tetap refund/failed. Bridge 0 baru. Track-C tanpa perubahan.
- Never touches scan-bridge.json. Dated run-note keys (runNote1331_1106) dipakai
  agar tidak menimpa runNote1331 lama (2026-11-03) di snapshot.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1331"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1331")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = snap.setdefault("contracts", {})
RR = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
BLK = RR["block"]
def setv(e, k, v):
    if v is not None:
        e[k] = v
NUMMAP = {
 "HIVE Agents": [("totalSupply", "totalSupply")],
 "KING Agent": [("totalMinted", "totalMinted"), ("remainingFree", "remainingFree")],
 "Mummyhive": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "Thronemind": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Hashseers": [("freeMinted", "freeMinted")],
 "Smeltbots": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Forklings": [("freeMinted", "freeMinted")],
 "Agent Frogs": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "PassAgentX": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "SEAT-f11e": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "LuckyBox-d08e": [("totalSupply", "totalSupply")],
 "Tumblebots": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Mossminds": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Jolly": [("totalMinted", "totalMinted"), ("freeMinted", "freeMinted")],
 "AgentGlyph": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "Layerloom": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Pacture": [("freeMinted", "freeMinted")],
 "MILLION": [("totalMinted", "totalMinted")],
 "FOD Agent": [("totalMinted", "totalMinted")],
 "StarAgent-7d39": [("totalSupply", "totalSupply")],
 "SnailMail": [("totalSupply", "totalSupply")],
 "wheelz": [("totalSupply", "totalSupply")],
 "Cipher Mind": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Cyber Lynx Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "CantonTron": [("totalMinted", "totalMinted")],
 "Bianren": [("totalMinted", "totalMinted"), ("freeMinted", "freeMinted"),
             ("freeRemaining", "freeRemaining")],
 "Crack": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted"),
           ("publicRemaining", "publicRemaining")],
}
for name, pairs in NUMMAP.items():
    if name not in C or name not in RR.get("reread", {}):
        continue
    for snapk, rrk in pairs:
        setv(C[name], snapk, RR["reread"][name].get(rrk))
    C[name]["lastReadBlock"] = BLK
    C[name]["lastReadWib"] = "2026-11-06 run 1331"
TC = snap.setdefault("track_c", {})
TCMAP = {
 "OSK": [("opened", "opened"), ("totalMinted", "totalMinted")],
 "DROID": [("opened", "opened"), ("freeMinted", "freeMinted")],
 "IMARS": [("opened", "opened"), ("freeMinted", "freeMinted")],
 "QAGENT-2": [("freeMinted", "freeMinted"), ("sharesMinted", "sharesMinted")],
 "SENBAZURU-b215": [("opened", "opened"), ("launched", "launched"), ("phase", "phase")],
 "SAFUAI": [("opened", "opened"), ("totalMinted", "totalMinted")],
 "NIULAI": [("launched", "launched"), ("phase", "phase")],
 "KillZero-K0-sale": [("launched", "launched")],
 "ShibAgent-R2": [("phase", "phase")],
 "Ikigai-Ihigi": [("freeMinted", "freeMinted"), ("phase", "phase")],
 "ASOC-43cE": [("saleEnded", "saleEnded")],
}
for name, pairs in TCMAP.items():
    if name not in TC or name not in RR.get("track_c", {}):
        continue
    for snapk, rrk in pairs:
        setv(TC[name], snapk, RR["track_c"][name].get(rrk))
def vel(name, note):
    if name in C:
        C[name]["runNote1331"] = note
vel("HIVE Agents", "Run 1331 (blok 131962334, interval ~22,39 mnt vs run 1301): totalSupply 1253 flat -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
vel("KING Agent", "Run 1331 (blok 131962334): totalMinted 867->875 (+8, 0,357/mnt vs prev 0,438 = 0,82x, <20) -> velocity GAGAL. remainingFree 2466->2458; free 875/3333 = 26,25% >=25%; slot terbuka (costOf 0, mintedBy 0, balance 0). Status tetap strong-lead-gate-blocked-2026-11-06; TIDAK dilaporkan ulang, TIDAK di-preview/di-mint.")
vel("MILLION", "Run 1331 (blok 131962334): totalMinted 188->189 (+1, <20) -> velocity GAGAL. Free leg tetap UNVERIFIED. Tetap EARLY.")
vel("SEAT-f11e", "Run 1331: totalSupply/totalMinted 4077->4101 (+24, 1,072/mnt vs prev 1,849 = 0,58x) -> velocity GAGAL. Free % tetap UNVERIFIED -> watchlist-only, TIDAK BISA promosi.")
vel("Forklings", "Run 1331: freeMinted 976->977 (+1, <20) -> velocity GAGAL; 977/2000=48,85% <50%; sudah strong-lead-gate-blocked sejak 2026-11-05, tidak dilaporkan ulang. costOf/mintsLeft/mintOpen read-fail run ini (nilai lama dipertahankan).")
vel("PassAgentX", "Run 1331: totalSupply 4054->4055 (+1, <20) -> velocity GAGAL; freeMinted 3836 flat; watchlist-only.")
vel("FOD Agent", "Run 1331: totalMinted 500 flat -> velocity GAGAL; costOf(user,1)=0,005 BNB (paid leg); tetap EARLY.")
vel("Thronemind", "Run 1331 (blok 131962334, interval ~22,39 mnt): totalSupply 741->742 (+1, 0,045/mnt vs prev 0,049 = 0,91x) -> velocity GAGAL. Free 742/2000=37,1% >=25%; slot terbuka (canFreeMint=1, claimedFree=0, balance 0). Sudah strong-lead-gate-blocked -> TIDAK di-preview/di-mint, TIDAK dilaporkan ulang.")
vel("Hashseers", "Run 1331: totalSupply 613 flat, freeMinted 613 flat -> velocity GAGAL; watchlist-only.")
vel("Smeltbots", "Run 1331: totalSupply 629->632 (+3, <20) -> velocity GAGAL; watchlist-only.")
vel("Agent Frogs", "Run 1331: totalSupply 474->481 (+7, <20), freeClaimed 481/1111=43,29% -> velocity GAGAL; watchlist-only.")
vel("StarAgent-7d39", "Run 1331: totalSupply 1452->1489 (+37, 1,653/mnt vs prev 2,092 = 0,79x) -> velocity GAGAL. Free % UNVERIFIED. UMUR KINI TERVERIFIKASI ~40,2 jam (first mint blok 131640557, estimasi 2026-11-04 21:26 WIB) -> tetap <=48 jam, TIDAK age-excluded; tetap EARLY.")
vel("Layerloom", "Run 1331: totalSupply 735->736 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("Tumblebots", "Run 1331: totalSupply 691 flat -> velocity GAGAL; watchlist-only.")
vel("Mossminds", "Run 1331: totalSupply kini terbaca 999 (1301: None); freeMinted 994->996 (+2, <20) -> velocity GAGAL. Free 996/2880=34,6% >=25%. TAPI status promotion-discarded-same-owner -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead; log only.")
vel("Jolly", "Run 1331: totalMinted 3681->3683 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("LuckyBox-d08e", "Run 1331: totalSupply 641 flat -> velocity GAGAL; watchlist-only.")
vel("SnailMail", "Run 1331: totalSupply 319->320 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("Mummyhive", "Run 1331: totalSupply 600 flat -> velocity GAGAL; watchlist-only.")
vel("wheelz", "Run 1331: totalSupply 321->322 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("Cipher Mind", "Run 1331: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("Cyber Lynx Agent", "Run 1331: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("CantonTron", "Run 1331: totalMinted 439->464 (+25, 1,117/mnt vs prev 0,438 = 2,55x, >=20 — lolos matematika velocity track-A, TAPI ia track-C gate-failed: kaki velocity tidak meng-gate track C dan gate sudah gagal -> TIDAK ada promosi/aksi. Sudah dilaporkan sekali hot leg 10:10 WIB; TIDAK dilaporkan ulang; TIDAK di-preview/di-mint.")
vel("Bianren", "Run 1331: totalMinted 21 flat -> velocity GAGAL; free 21/2000=1,05% <25%; slot user tetap UNVERIFIED (quote ~0,000187 BNB); gate website tetap BELUM LOLOS; tetap EARLY, TIDAK di-preview/di-mint.")
if "KING Agent" in C:
    C["KING Agent"]["previousTotalSupply"] = 867; C["KING Agent"]["mintedInInterval"] = 8
    C["KING Agent"]["intervalMinutes"] = 22.39; C["KING Agent"]["currentRatePerMin"] = 0.357
    C["KING Agent"]["previousRatePerMin"] = 0.438; C["KING Agent"]["velocityLegPasses"] = False
    C["KING Agent"]["velocityNote"] = "Run 1331: velocity GAGAL (0,357/mnt vs prev 0,438 = 0,82x, +8 token <20); free 26,25% >=25% -> tetap strong-lead-gate-blocked."
if "SEAT-f11e" in C:
    C["SEAT-f11e"]["previousTotalSupply"] = 4077; C["SEAT-f11e"]["mintedInInterval"] = 24
    C["SEAT-f11e"]["intervalMinutes"] = 22.39; C["SEAT-f11e"]["currentRatePerMin"] = 1.072
    C["SEAT-f11e"]["previousRatePerMin"] = 1.849; C["SEAT-f11e"]["velocityLegPasses"] = False
    C["SEAT-f11e"]["velocityNote"] = "Run 1331: velocity GAGAL (1,072/mnt vs prev 1,849 = 0,58x, +24 token); free % UNVERIFIED -> watchlist-only, TIDAK BISA promosi."
if "MILLION" in C:
    C["MILLION"]["previousTotalSupply"] = 188; C["MILLION"]["mintedInInterval"] = 1
    C["MILLION"]["intervalMinutes"] = 22.39; C["MILLION"]["currentRatePerMin"] = 0.045
    C["MILLION"]["previousRatePerMin"] = 0.0; C["MILLION"]["velocityLegPasses"] = False
if "Thronemind" in C:
    C["Thronemind"]["previousTotalSupply"] = 741; C["Thronemind"]["mintedInInterval"] = 1
    C["Thronemind"]["intervalMinutes"] = 22.39; C["Thronemind"]["currentRatePerMin"] = 0.045
    C["Thronemind"]["previousRatePerMin"] = 0.049; C["Thronemind"]["velocityLegPasses"] = False
    C["Thronemind"]["velocityNote"] = "Run 1331: velocity GAGAL (0,045/mnt vs prev 0,049 = 0,91x, +1 token); free 37,1% >=25%; slot terbuka. Sudah strong-lead-gate-blocked."
if "Mossminds" in C:
    C["Mossminds"]["previousTotalSupply"] = 992; C["Mossminds"]["mintedInInterval"] = 2
    C["Mossminds"]["intervalMinutes"] = 22.39; C["Mossminds"]["currentRatePerMin"] = 0.089
    C["Mossminds"]["previousRatePerMin"] = 0.243; C["Mossminds"]["velocityLegPasses"] = False
    C["Mossminds"]["velocityNote"] = "Run 1331: velocity GAGAL (freeMinted +2, <20 token; totalSupply kini terbaca 999); free 34,6% >=25%. TAPI same-owner-discarded -> tidak pernah dipromosikan/dilaporkan."
if "StarAgent-7d39" in C:
    C["StarAgent-7d39"]["previousTotalSupply"] = 1452; C["StarAgent-7d39"]["mintedInInterval"] = 37
    C["StarAgent-7d39"]["intervalMinutes"] = 22.39; C["StarAgent-7d39"]["currentRatePerMin"] = 1.653
    C["StarAgent-7d39"]["previousRatePerMin"] = 2.092; C["StarAgent-7d39"]["velocityLegPasses"] = False
    C["StarAgent-7d39"]["velocityNote"] = "Run 1331: velocity GAGAL (1,653/mnt vs prev 2,092 = 0,79x, +37 token). Free % UNVERIFIED; umur kini TERVERIFIKASI ~40,2 jam -> tetap EARLY."
    # Age verification run 1331 (first mint via Ankr getLogs address-filtered)
    C["StarAgent-7d39"]["firstMintBlock"] = 131640557
    C["StarAgent-7d39"]["firstMintWib"] = "2026-11-04 ~21:26 (ESTIMASI dari anchor blok 131959349 = 13:17:43 WIB; timestamp blok tak terbaca karena RPC degradasi)"
    C["StarAgent-7d39"]["ageVerifiedWib"] = "2026-11-06 run 1331"
    C["StarAgent-7d39"]["launchNote"] = ("Umur TERVERIFIKASI run 1331: first mint blok 131640557 (Ankr getLogs "
        "address-filtered, Transfer-from-zero; range 131591156-131641155: 258 mint logs, earliest 131640557; "
        "range sebelumnya 131541156-131591155: 0 logs). Timestamp blok tak terbaca (RPC degradasi) -> estimasi "
        "dari anchor blok 131959349 = 13:17:43 WIB: first mint ~2026-11-04 21:26 WIB, umur ~40,2 jam pada 13:40 WIB "
        "-> <=48 jam, TIDAK age-excluded. Sourcify verifiedAt 2026-11-04T14:26:16Z adalah waktu verifikasi, BUKAN launch.")
if "Bianren" in C:
    C["Bianren"]["previousTotalSupply"] = 21; C["Bianren"]["mintedInInterval"] = 0
    C["Bianren"]["intervalMinutes"] = 22.39; C["Bianren"]["currentRatePerMin"] = 0.0
    C["Bianren"]["previousRatePerMin"] = 0.0; C["Bianren"]["velocityLegPasses"] = False
    C["Bianren"]["velocityNote"] = "Run 1331: velocity GAGAL (+0 token, 0,000/mnt); free 1,05% <25%; tetap EARLY."
if "Crack" in TC:
    setv(TC["Crack"], "totalSupply", 1835); setv(TC["Crack"], "totalMinted", 1835); setv(TC["Crack"], "publicRemaining", 3670)
    TC["Crack"]["runNote1331"] = ("Run 1331: totalSupply/totalMinted 1700/1701->1835/1835 (+135/+134), publicRemaining 3804->3670; "
        "freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 — mint berikutnya BERBAYAR (0,001 BNB), TIDAK diotorisasi.")
snap["last_run"] = "2026-11-06 run 1331"
snap["last_run_wib"] = "2026-11-06T13:31:00+07:00"
snap["runNote1331_1106"] = ("Run 1331: SILENT (0 kandidat baru, 0 early lead baru, 0 promosi baru, 0 pending claim baru/dibuka, "
    "0 lead/kandidat track-C baru, 0 age-exclusion, 0 sellout, 0 slot hilang). Satu temuan verifikasi baru: StarAgent-7d39 umur kini "
    "TERVERIFIKASI ~40,2 jam (first mint blok 131640557, estimasi 2026-11-04 21:26 WIB) -> tetap <=48 jam, TIDAK age-excluded; tetap EARLY "
    "(velocity GAGAL 0,79x + free % UNVERIFIED). SEAT-f11e velocity GAGAL (1,072/mnt, 0,58x, +24); free % tetap UNVERIFIED. KING Agent drift saja "
    "(remainingFree 2466->2458, totalMinted 867->875, free 26,25%); tetap strong-lead-gate-blocked, tidak dilaporkan ulang. CantonTron +25 "
    "(1,117/mnt, 2,55x) lolos matematika velocity track-A tapi track-C gate-failed -> tanpa aksi. SCAN GAGAL: pre-flight OK 9,0 dtk, chunk 20/20 "
    "selesai (131961352-131962351, 177 ERC721 + 6 ERC1155 + 418 ERC20-mint), lalu stall di fase enrichment pasca-chunk tanpa JSON; proses hilang "
    "~06:50:30 UTC karena RUNTIME RESTART (bukan timeout 780); triase + 5c dilewati; watermark TIDAK dimajukan scan ini (backfill paralel "
    "131921548 -> 131927548 selama run ini). 5a: 1 alamat baru Sourcify (0x57910724...), bukan sale shape. Track B binanceai tetap refund/failed. "
    "Bridge 0 baru. Boltbook 0 hit (newest 2026-11-05T09:20:52Z). Sweep: hanya proyek lama/dikenal (Razor excluded; M3MO age-excluded run 1301; "
    "JAGENT paid; AGENT MAO paused). Odaily/PANews 0 mention Agent ID/free mint.")
snap["runNote1331_scan_1106"] = ("Run 1331: SCAN GAGAL (enrichment stall pasca-chunk, pola sama run 1301; chunk 20/20 selesai 131961352-131962351, "
    "ERC721 177, ERC1155 6, ERC20-mint 418, tapi TIDAK ADA JSON; proses hilang ~06:50:30 UTC karena RUNTIME RESTART mematikan sesi exec latar, "
    "sebelum timeout 780 habis, tanpa exit code tercatat; stall enrichment ~4 mnt tanpa output, CPU ~2 dtk, tetap nyata sebelum restart). "
    "Pre-flight OK 9,0 dtk (head 131962329, 334 logs). Watermark bersama TIDAK dimajukan scan ini; backfill paralel memajukan 131921548 -> "
    "131927548 selama run ini. Triase + 5c dilewati. Gap 131921549-131961351 + window 131961352-131962351 (data hilang) belum ter-cover; "
    "backfill lanjut. Pelajaran: fase enrichment butuh progress logging + penulisan parsial agar data chunk tidak hilang saat stall.")
snap["last_run_note"] = snap["runNote1331_1106"]
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
# seen file: NO additions (scan JSON lost) - record explicitly (read fresh first)
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen.setdefault("_meta", {})["note_1331"] = ("Run 1331: SCAN GAGAL (enrichment stall + runtime restart, tanpa JSON) -> TIDAK ADA penambahan "
    "seen file run ini. Jendela 131961352-131962351 belum ter-cover; first-seen di jendela itu belum bisa ditentukan; backfill akan menutupnya bertahap.")
seen["_meta"]["last_updated_wib"] = "2026-11-06 run 1331"
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
# scan state: ONLY add the note + main-scan window fields; do NOT touch the shared
# watermark (last_scanned_block / last_scan_wib) - owned by the parallel backfill.
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_main_scan_window_from"] = 131961352
st["last_main_scan_window_to"] = 131962351
st["note_1331_scan"] = ("Run 1331: SCAN GAGAL (enrichment stall pasca-chunk, pola sama run 1301; chunk 20/20 selesai "
    "131961352-131962351, ERC721 177, ERC1155 6, ERC20-mint 418, tapi TIDAK ADA JSON; proses hilang ~06:50:30 UTC "
    "karena RUNTIME RESTART, sebelum timeout 780 habis, tanpa exit code tercatat). Pre-flight OK 9,0 dtk (head 131962329). "
    "Watermark bersama TIDAK dimajukan scan ini; backfill paralel memajukan 131921548 -> 131927548 selama run ini. "
    "Triase + 5c dilewati. Gap 131921549-131961351 + window 131961352-131962351 (data hilang) belum ter-cover.")
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("FINALIZE OK; contracts:", len(C), "track_c:", len(TC),
      "excluded:", len(snap.get("excluded", {})),
      "scan-state watermark (untouched by finalize):", st.get("last_scanned_block"))
