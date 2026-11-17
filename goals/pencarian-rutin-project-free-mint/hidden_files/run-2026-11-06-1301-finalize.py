#!/usr/bin/env python3
"""Run 2026-11-06 1301 WIB finalize.
Outcome: SILENT except one reportable change (M3MO age-exclusion).
- Leg 1 re-read block 131959349; interval vs run 1231 read block 131956609
  (12:57:10 WIB -> 13:17:43 WIB) = 1233 s = 20.55 min.
- Scan FAILED (SCAN_EXIT=124, timeout 780s in enrichment phase; chunks 20/20
  done 131958381-131959380, 190 ERC721 + 4 ERC1155 + 426 ERC20-mint, but NO
  JSON written -> no first-seen triage, 5c skipped). Watermark NOT advanced
  by main scan (shared watermark 131921548 = backfill position).
- M3MO age-excluded: first mint verified block 131371874, 2026-11-03 11:50:33 WIB,
  age 73.6h > 48h, totalMinted 4780/10000 (not sold out) -> removed from
  active watchlist per the 48h rule, recorded in excluded.
- 5a: 2 NEW Sourcify addresses, both already in hot-leg-seen (SKIP), neither
  sale shape. 5c skipped (no scan output). Bridge 0 new. BinanceAI unchanged
  (refund/failed). Boltbook 0 hits (newest 2026-11-05T09:20:52Z).
- Never touches scan-bridge.json.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1301"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1301")
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
    C[name]["lastReadWib"] = "2026-11-06 run 1301"
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
        C[name]["runNote1301"] = note
vel("HIVE Agents", "Run 1301 (blok 131959349, interval 20,55 mnt vs run 1231): totalSupply 1253 flat -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
vel("KING Agent", "Run 1301 (blok 131959349): totalMinted kini terbaca 867 (1231: gagal baca, nilai lama 845); remainingFree 2475->2466 (+9 free claimed, 867/3333 = 26,01% >=25%, 0,438/mnt vs prev 0,455 = 0,96x, <20) -> velocity GAGAL. Slot terbuka (costOf 0, mintedBy 0, balance 0). Status tetap strong-lead-gate-blocked-2026-11-06 (gate website GAGAL run 1201); TIDAK dilaporkan ulang, TIDAK di-preview/di-mint.")
vel("MILLION", "Run 1301 (blok 131959349): totalMinted 188 flat vs run 1231 (188) -> velocity GAGAL. Free leg tetap UNVERIFIED. Tetap EARLY.")
vel("SEAT-f11e", "Run 1301: totalSupply/totalMinted 4039->4077 (+38, 1,849/mnt vs prev 5,420 = 0,34x) -> velocity GAGAL (1231 sempat LOLOS 3,09x). Free % tetap UNVERIFIED -> watchlist-only, TIDAK BISA promosi.")
vel("Forklings", "Run 1301: freeMinted 974->976 (+2, <20) -> velocity GAGAL; 976/2000=48,8% <50%; sudah strong-lead-gate-blocked sejak 2026-11-05, tidak dilaporkan ulang.")
vel("PassAgentX", "Run 1301: totalSupply 4052->4054 (+2), freeMinted 3834->3836 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("FOD Agent", "Run 1301: totalMinted 500 flat vs run 1231 (500) -> velocity GAGAL; costOf(user,1)=0,0005 BNB (paid leg); tetap EARLY.")
vel("Thronemind", "Run 1301 (blok 131959349, interval 20,55 mnt): totalSupply 740->741 (+1, 0,049/mnt vs prev 0,299 = 0,16x) -> velocity GAGAL. Free 741/2000=37,05% >=25%; slot terbuka (canFreeMint=1, claimedFree=0, balance 0); umur ~25 jam. Sudah strong-lead-gate-blocked -> TIDAK di-preview/di-mint, TIDAK dilaporkan ulang.")
vel("Hashseers", "Run 1301: totalSupply 612->613 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("Smeltbots", "Run 1301: totalSupply 628->629 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("Agent Frogs", "Run 1301: totalSupply 456->474 (+18, <20) -> velocity GAGAL; watchlist-only.")
vel("StarAgent-7d39", "Run 1301: totalSupply 1409->1452 (+43, 2,092/mnt vs prev 2,063 = 1,01x <1,5x) -> velocity GAGAL. Free % UNVERIFIED + umur UNVERIFIED -> watchlist-only.")
vel("Layerloom", "Run 1301: totalSupply 735 flat vs run 1231 (735) -> velocity GAGAL; watchlist-only.")
vel("Tumblebots", "Run 1301: totalSupply 691 flat vs run 1231 (691) -> velocity GAGAL; watchlist-only.")
vel("Mossminds", "Run 1301: totalSupply gagal baca (None, nilai lama 992 dipertahankan); freeMinted 989->994 (+5, <20) -> velocity GAGAL. Free 994/2880=34,5% >=25%. TAPI status promotion-discarded-same-owner -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead; log only.")
vel("Jolly", "Run 1301: totalMinted 3680->3681 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("LuckyBox-d08e", "Run 1301: totalSupply 641 flat vs run 1231 (641) -> velocity GAGAL; watchlist-only.")
vel("SnailMail", "Run 1301: totalSupply 319 flat vs run 1231 (319) -> velocity GAGAL; watchlist-only.")
vel("Mummyhive", "Run 1301: totalSupply 600 flat vs run 1231 (600) -> velocity GAGAL; watchlist-only.")
vel("wheelz", "Run 1301: totalSupply 321 flat vs run 1231 (321) -> velocity GAGAL; watchlist-only.")
vel("Cipher Mind", "Run 1301: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("Cyber Lynx Agent", "Run 1301: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("CantonTron", "Run 1301: totalMinted 430->439 (+9, <20) -> velocity GAGAL. Track-C gate-failed, sudah dilaporkan sekali hot leg 10:10 WIB; TIDAK dilaporkan ulang; TIDAK di-preview/di-mint.")
vel("Bianren", "Run 1301: totalMinted 21 flat vs run 1231 (21) -> velocity GAGAL; free 21/2000=1,05% <25%; slot user tetap UNVERIFIED (quote ~0,000187 BNB); gate website tetap BELUM LOLOS; tetap EARLY, TIDAK di-preview/di-mint.")
if "KING Agent" in C:
    C["KING Agent"]["previousTotalSupply"] = 858; C["KING Agent"]["mintedInInterval"] = 9
    C["KING Agent"]["intervalMinutes"] = 20.55; C["KING Agent"]["currentRatePerMin"] = 0.438
    C["KING Agent"]["previousRatePerMin"] = 0.455; C["KING Agent"]["velocityLegPasses"] = False
    C["KING Agent"]["velocityNote"] = "Run 1301: velocity GAGAL (0,438/mnt via remainingFree delta vs prev 0,455 = 0,96x, +9 token <20; totalMinted kini terbaca 867, cocok dengan free claimed 867); free 26,01% >=25% -> tetap strong-lead-gate-blocked."
if "SEAT-f11e" in C:
    C["SEAT-f11e"]["previousTotalSupply"] = 4039; C["SEAT-f11e"]["mintedInInterval"] = 38
    C["SEAT-f11e"]["intervalMinutes"] = 20.55; C["SEAT-f11e"]["currentRatePerMin"] = 1.849
    C["SEAT-f11e"]["previousRatePerMin"] = 5.42; C["SEAT-f11e"]["velocityLegPasses"] = False
    C["SEAT-f11e"]["velocityNote"] = "Run 1301: velocity GAGAL (1,849/mnt vs prev 5,420 = 0,34x, +38 token); free % UNVERIFIED -> watchlist-only, TIDAK BISA promosi."
if "MILLION" in C:
    C["MILLION"]["previousTotalSupply"] = 188; C["MILLION"]["mintedInInterval"] = 0
    C["MILLION"]["intervalMinutes"] = 20.55; C["MILLION"]["currentRatePerMin"] = 0.0
    C["MILLION"]["previousRatePerMin"] = 0.035; C["MILLION"]["velocityLegPasses"] = False
if "Thronemind" in C:
    C["Thronemind"]["previousTotalSupply"] = 740; C["Thronemind"]["mintedInInterval"] = 1
    C["Thronemind"]["intervalMinutes"] = 20.55; C["Thronemind"]["currentRatePerMin"] = 0.049
    C["Thronemind"]["previousRatePerMin"] = 0.0; C["Thronemind"]["velocityLegPasses"] = False
    C["Thronemind"]["velocityNote"] = "Run 1301: velocity GAGAL (0,049/mnt vs prev 0,000, +1 token); free 37,05% >=25%; slot terbuka; umur ~25 jam. Sudah strong-lead-gate-blocked."
if "Mossminds" in C:
    C["Mossminds"]["previousTotalSupply"] = 992; C["Mossminds"]["mintedInInterval"] = 5
    C["Mossminds"]["intervalMinutes"] = 20.55; C["Mossminds"]["currentRatePerMin"] = 0.243
    C["Mossminds"]["previousRatePerMin"] = 0.07; C["Mossminds"]["velocityLegPasses"] = False
    C["Mossminds"]["velocityNote"] = "Run 1301: velocity GAGAL (freeMinted +5, <20 token; totalSupply gagal baca run ini); free 34,5% >=25%. TAPI same-owner-discarded -> tidak pernah dipromosikan/dilaporkan."
if "StarAgent-7d39" in C:
    C["StarAgent-7d39"]["previousTotalSupply"] = 1409; C["StarAgent-7d39"]["mintedInInterval"] = 43
    C["StarAgent-7d39"]["intervalMinutes"] = 20.55; C["StarAgent-7d39"]["currentRatePerMin"] = 2.092
    C["StarAgent-7d39"]["previousRatePerMin"] = 2.063; C["StarAgent-7d39"]["velocityLegPasses"] = False
    C["StarAgent-7d39"]["velocityNote"] = "Run 1301: velocity GAGAL (2,092/mnt vs prev 2,063 = 1,01x, +43 token). Free % UNVERIFIED + umur UNVERIFIED -> watchlist-only."
if "Bianren" in C:
    C["Bianren"]["previousTotalSupply"] = 21; C["Bianren"]["mintedInInterval"] = 0
    C["Bianren"]["intervalMinutes"] = 20.55; C["Bianren"]["currentRatePerMin"] = 0.0
    C["Bianren"]["previousRatePerMin"] = 0.0; C["Bianren"]["velocityLegPasses"] = False
    C["Bianren"]["velocityNote"] = "Run 1301: velocity GAGAL (+0 token, 0,000/mnt); free 1,05% <25%; tetap EARLY."
if "Crack" in TC:
    setv(TC["Crack"], "totalSupply", 1700); setv(TC["Crack"], "totalMinted", 1701); setv(TC["Crack"], "publicRemaining", 3804)
    TC["Crack"]["runNote1301"] = "Run 1301: totalSupply/totalMinted 1461/1463->1700/1701 (+239/+238), publicRemaining 4037->3804; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 — mint berikutnya BERBAYAR (0,001 BNB), TIDAK diotorisasi."
# M3MO age-exclusion: first mint verified block 131371874, 2026-11-03 11:50:33 WIB;
# age ~73.6h at check (run 1301, ~13:35 WIB), totalMinted 4780/10000 (not sold out).
m3mo = C.pop("bridge-M3MO-2", None)
if m3mo is not None:
    ex = snap.setdefault("excluded", {})
    ex["bridge-M3MO-2"] = {
        "address": "0x08be8a0727b6fc801171c1f4f4dd547ea44ca339",
        "symbol": "M3MO",
        "track": "A",
        "status": "excluded-age-over-48h-2026-11-06",
        "note": "Age-excluded run 1301: first mint TERVERIFIKASI blok 131371874, 2026-11-03 11:50:33 WIB (Ankr getLogs address-filtered, chunk 131370000-131371999, 11 logs; sumber: first-mint-T). Umur ~73,6 jam >48 jam pada run 1301 (~13:35 WIB) dan BELUM sold out (bacaan segar run 1301: totalMinted 4780/10000, head 131959442). Dihapus dari watchlist aktif per aturan 48 jam; status lama watchlist-only-scan-bridge-2026-11-03. Dilaporkan sekali sebagai perubahan ke parent run 1301; tidak di-preview/di-mint. Catatan: totalSupply() revert (kontrak totalMinted-only); percobaan binary search totalMinted(block) gagal karena dataseed 'missing trie node' untuk blok historis — first mint di atas dari getLogs, bukan dari binary search.",
        "previous_status": "watchlist-only-scan-bridge-2026-11-03",
        "firstMintWib": "2026-11-03 11:50:33",
        "firstMintBlock": 131371874,
        "lastReading": "totalMinted 4780/10000 (run 1301, head 131959442)",
    }
    print("M3MO age-excluded and moved to excluded.", flush=True)
else:
    print("M3MO already absent from contracts.", flush=True)
snap["last_run"] = "2026-11-06 run 1301"
snap["last_run_wib"] = "2026-11-06T13:01:00+07:00"
snap["runNote1301"] = ("Run 1301: SILENT kecuali 1 perubahan — M3MO (bridge-M3MO-2) AGE-EXCLUDED: first mint terverifikasi 2026-11-03 11:50:33 WIB (blok 131371874), umur ~73,6 jam >48 jam, totalMinted 4780/10000 (belum sold out) -> dihapus dari watchlist aktif, dicatat di excluded. 0 kandidat baru, 0 early lead baru, 0 promosi baru, 0 pending claim baru/dibuka, 0 lead/kandidat track-C baru. SEAT-f11e velocity kembali GAGAL (1,849/mnt, 0,34x, +38) setelah LOLOS run 1231; free % tetap UNVERIFIED -> watchlist-only. KING Agent drift saja (remainingFree 2475->2466, totalMinted kini terbaca 867, free 26,01%); status tetap strong-lead-gate-blocked-2026-11-06, tidak dilaporkan ulang. SCAN GAGAL: pre-flight OK 4,0 dtk, chunk 20/20 selesai (131958381-131959380, 190 ERC721 + 4 ERC1155 + 426 ERC20-mint), lalu timeout 780 dtk di fase enrichment pasca-chunk tanpa JSON -> tidak ada triase first-seen, 5c dilewati; watermark TIDAK dimajukan (tetap 131921548 posisi backfill). 5a: 2 alamat baru Sourcify (0xE12A32c9, 0xe81bE376), keduanya sudah ada di hot-leg-seen, bukan sale shape. Track B binanceai tetap refund/failed. Bridge 0 baru. Boltbook 0 hit (newest 2026-11-05T09:20:52Z). Sweep: hanya proyek lama/dikenal (Razor = kontrak sama yang sudah excluded; M3MO sudah di watchlist; AgentRob rantai Robinhood, di luar scope BSC; AGENT MAO paused; JAGENT paid). Odaily/PANews 0 mention Agent ID/free mint.")
snap["runNote1301_scan"] = "Run 1301: SCAN GAGAL (SCAN_EXIT=124, timeout 780 dtk). Pre-flight OK 4,0 dtk (head 131959348, 50 blok, 279 logs). Chunk phase 20/20 selesai ~5 mnt (131958381-131959380, ERC721 190, ERC1155 4, ERC20-mint 426), lalu stall di fase enrichment pasca-chunk (eth_getCode + Sourcify ABI + name/symbol per kontrak, tanpa progress logging di fase itu) — proses di-kill timeout sebelum json.dump, TIDAK ADA onchain-scan-2026-11-06-1301.json. Watermark bersama TIDAK dimajukan (tetap 131921548, posisi backfill). Triase first-seen + 5c DILEWATI (tanpa output scan). Jendela 131958381-131959380 akan ditutup backfill bertahap; first-seen di jendela itu belum bisa ditentukan run ini."
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
# seen file: NO additions (scan JSON lost) - record that explicitly
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen.setdefault("_meta", {})["note_1301"] = "Run 1301: SCAN GAGAL (timeout 780 di fase enrichment, tanpa JSON) -> TIDAK ADA penambahan seen file run ini. Jendela 131958381-131959380 belum ter-cover; first-seen di jendela itu belum bisa ditentukan; backfill akan menutupnya bertahap."
seen["_meta"]["last_updated_wib"] = "2026-11-06 run 1301"
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
# scan state: keep shared watermark at backfill position; record failed main-scan attempt
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_main_scan_window_from"] = 131958381
st["last_main_scan_window_to"] = 131959380
st["last_scan_wib"] = "run 2026-11-06-1301 (main scan FAILED; shared watermark kept at backfill 131921548)"
st["ankr_calls"] = 40
st["errors"] = ["Enrichment phase stall (post-chunk, no progress logging): SCAN_EXIT=124, timeout 780s, no JSON written"]
st["nft_contracts"] = 190
st["erc20_mint_contracts"] = 426
st["skipped_gap"] = "131921549-131958380 (~36.832 blok; window dari watermark bersama 131921548 ke head 131959380 > cap 1000; main scan menutup 1000 blok terbaru 131958381-131959380 tapi GAGAL di enrichment tanpa JSON; gap ditutup bertahap oleh backfill)"
st["note_1301_scan"] = "Run 1301: SCAN GAGAL (SCAN_EXIT=124, timeout 780 dtk di fase enrichment pasca-chunk; chunk 20/20 selesai 131958381-131959380, ERC721 190, ERC1155 4, ERC20-mint 426, tapi TIDAK ADA JSON). Pre-flight OK 4,0 dtk (head 131959348). Watermark bersama TIDAK dimajukan (tetap 131921548, posisi backfill). Triase + 5c dilewati. Pelajaran: fase enrichment butuh progress logging + penulisan parsial (seperti catatan run 0901/1002) agar data chunk tidak hilang saat timeout."
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("FINALIZE OK; contracts:", len(C), "track_c:", len(TC),
      "excluded:", len(snap.get("excluded", {})), "M3MO moved:", m3mo is not None)
