#!/usr/bin/env python3
"""Run 2026-11-06 1131 WIB finalize (SILENT run — no new candidate/lead).
1. Snapshot numeric updates (None never overwrites) + velocity notes.
   Interval 1101-read blok 131941958 (11:07:16 WIB) -> 1131-read blok
   131949225 (12:01:47 WIB) = 7267 blok = 54.52 mnt (block timestamps).
2. Scan first-seen (correct dedupe vs seen["contracts"], lowercase):
   1 TRUE first-seen: PACTURE NFT 0x55387dcf5E5d11c01f7264714de42aF3afB1DEc5
   (ERC721, 7 mints/1 minter, registry=False, Sourcify verified, NO free
   funcs, mint funcs only totalMinted) -> NOT agent-shaped, log only,
   NOT a lead, NOT added to snapshot as lead.
3. Seen file: all scan-window contracts not yet in seen["contracts"].
4. Scan-state: watermark -> 131950389 (scan SUKSES); skipped gap
   131942909-131949389 (6481 blok, backfill).
5. Track-C: Crack totalSupply 1144, publicRemaining 4361.
6. Thronemind velocity LULUS run ini (+48, 0.880/mnt vs 0.363 run 1101 =
   2.42x, >=20 token); free 732/2000=36.6% >=25%; slot terbuka; umur
   ~23.4h TERVERIFIKASI <=48h -> 3 kaki strong lead terpenuhi + velocity
   lulus, TAPI gate website TETAP GAGAL (re-check nama run ini 0 hit;
   metode A-N penuh sudah dilakukan run 1601) -> tetap
   strong-lead-gate-blocked, TIDAK di-preview/di-mint, TIDAK dilaporkan
   ulang (sudah dilaporkan sekali run 1601).
7. Mossminds velocity LULUS (+40, 0.734/mnt vs 0.264 = 2.78x); free
   985/2880=34.2% >=25% TAPI status promotion-discarded-same-owner ->
   TIDAK PERNAH dipromosikan/dilaporkan; log only.
8. StarAgent-7d39 velocity LULUS (+143, 2.623/mnt vs ~0.099 = ~26x)
   TAPI free % UNVERIFIED + umur UNVERIFIED -> watchlist-only.
9. Never touches scan-bridge.json.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1131"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1131")
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
 "Nebula Ape Agent": [("totalMinted", "totalMinted")],
 "Shadow Yeti Agent": [("totalMinted", "totalMinted")],
 "Silent Hydra Agent": [("totalMinted", "totalMinted")],
 "Cipher Wraith Agent": [("totalMinted", "totalMinted")],
 "Umbra Lynx Agent": [("totalMinted", "totalMinted")],
 "Data Synth": [("totalMinted", "totalMinted")],
 "Zero Genesis": [("totalMinted", "totalMinted")],
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
    C[name]["lastReadWib"] = "2026-11-06 run 1131"
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
        C[name]["runNote1131"] = note
vel("HIVE Agents", "Run 1131 (blok 131949225, interval 54,52 mnt vs run 1101): totalSupply 1253 flat -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
vel("KING Agent", "Run 1131 (blok 131949225): totalMinted 792->828 (+36, 0,660/mnt vs prev 1,089 = 0,61x) -> velocity GAGAL; free 828/3333=24,85% <25% -> tetap EARLY, bukan strong lead, bukan kandidat. Slot user terbuka (costOf 0, mintedBy 0, balance 0).")
vel("MILLION", "Run 1131 (blok 131949225): totalMinted 182->187 (+5, <20) -> velocity GAGAL. Free leg tetap UNVERIFIED. Tetap EARLY.")
vel("SEAT-f11e", "Run 1131: totalSupply/totalMinted 3726->3837 (+111, 2,036/mnt vs prev 2,574 = 0,79x) -> velocity GAGAL. Free % tetap UNVERIFIED -> TIDAK BISA promosi; watchlist-only.")
vel("Forklings", "Run 1131: freeMinted 955->965 (+10, <20) -> velocity GAGAL; 965/2000=48,25% <50%; strong-lead gate-blocked, watchlist-only.")
vel("PassAgentX", "Run 1131: totalSupply 4018->4035 (+17), freeMinted 3800->3817 (+17, <20) -> velocity GAGAL; watchlist-only.")
vel("FOD Agent", "Run 1131: totalMinted 500 flat vs run 1101 (500) -> velocity GAGAL; costOf(user,1)=0,0005 BNB (paid leg); tetap EARLY.")
vel("Thronemind", "Run 1131 (blok 131949225, interval 54,52 mnt): totalSupply 684->732 (+48, 0,880/mnt vs prev run-1101 0,363 = 2,42x) -> velocity LULUS (>=1,5x DAN >=20 token). Free 732/2000=36,6% >=25%; slot terbuka (canFreeMint=1, claimedFree=0, balance 0); umur TERVERIFIKASI ~23,4 jam <=48 jam. TAPI gate website TETAP GAGAL (re-check nama + alamat run ini: 0 hit relevan; metode A-N penuh sudah dilakukan run 1601 incl. BscScan browser tanpa tautan website/sosial) -> tetap strong-lead-gate-blocked, TIDAK di-preview/di-mint, TIDAK dilaporkan ulang (sudah dilaporkan sekali run 1601).")
vel("Hashseers", "Run 1131: totalSupply 608->610 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("Smeltbots", "Run 1131: totalSupply 626->628 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("Agent Frogs", "Run 1131: totalSupply 439->441 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("StarAgent-7d39", "Run 1131: totalSupply 1122->1265 (+143, 2,623/mnt vs prev ~0,099 = ~26x) -> velocity LULUS (>=1,5x DAN >=20 token). TAPI free % UNVERIFIED (tanpa free view) + umur peluncuran UNVERIFIED -> TIDAK BISA promosi; watchlist-only. Lonjakan +143 dicatat, bukan sinyal beli.")
vel("Layerloom", "Run 1131: totalSupply 724->730 (+6, <20) -> velocity GAGAL; watchlist-only.")
vel("Tumblebots", "Run 1131: totalSupply 684->687 (+3, <20) -> velocity GAGAL; watchlist-only.")
vel("Mossminds", "Run 1131: totalSupply 948->988 (+40, 0,734/mnt vs prev 0,264 = 2,78x) -> velocity LULUS; free 985/2880=34,2% >=25%. TAPI status promotion-discarded-same-owner -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead (aturan bridge); log only.")
vel("Jolly", "Run 1131: totalMinted 3668->3678 (+10, <20) -> velocity GAGAL; watchlist-only.")
vel("LuckyBox-d08e", "Run 1131: totalSupply 636->638 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("SnailMail", "Run 1131: totalSupply 315->319 (+4, <20) -> velocity GAGAL; watchlist-only.")
vel("Mummyhive", "Run 1131: totalSupply 600 flat vs run 1101 (600) -> velocity GAGAL; watchlist-only.")
vel("wheelz", "Run 1131: totalSupply 317->321 (+4, <20) -> velocity GAGAL; watchlist-only.")
vel("Cipher Mind", "Run 1131: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("Cyber Lynx Agent", "Run 1131: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("CantonTron", "Run 1131: totalMinted 63->394 (+331) — lonjakan besar; track-C gate-failed, sudah dilaporkan sekali hot leg 10:10 WIB; TIDAK dilaporkan ulang (dedupe lintas job); TIDAK di-preview/di-mint.")
vel("Bianren", "Run 1131: totalMinted 17->18 (+1, <20) -> velocity GAGAL; free 18/2000=0,9% <25%; slot user tetap UNVERIFIED (quote ~0,000187 BNB); gate website tetap BELUM LOLOS (bbyr4.pages.dev gagal DNS run 1101, tidak dicoba ulang run ini); tetap EARLY, TIDAK di-preview/di-mint.")
# rate fields for next run
if "KING Agent" in C:
    C["KING Agent"]["previousTotalSupply"] = 792; C["KING Agent"]["mintedInInterval"] = 36
    C["KING Agent"]["intervalMinutes"] = 54.52; C["KING Agent"]["currentRatePerMin"] = 0.660
    C["KING Agent"]["previousRatePerMin"] = 1.089; C["KING Agent"]["velocityLegPasses"] = False
    C["KING Agent"]["velocityNote"] = "Run 1131: velocity GAGAL (0,660/mnt vs prev 1,089 = 0,61x, +36 token); free 24,85% <25% -> tetap EARLY."
if "SEAT-f11e" in C:
    C["SEAT-f11e"]["previousTotalSupply"] = 3726; C["SEAT-f11e"]["mintedInInterval"] = 111
    C["SEAT-f11e"]["intervalMinutes"] = 54.52; C["SEAT-f11e"]["currentRatePerMin"] = 2.036
    C["SEAT-f11e"]["previousRatePerMin"] = 2.574; C["SEAT-f11e"]["velocityLegPasses"] = False
    C["SEAT-f11e"]["velocityNote"] = "Run 1131: velocity GAGAL (2,036/mnt vs prev 2,574 = 0,79x, +111 token); free % UNVERIFIED -> watchlist-only."
if "MILLION" in C:
    C["MILLION"]["previousTotalSupply"] = 182; C["MILLION"]["mintedInInterval"] = 5
    C["MILLION"]["intervalMinutes"] = 54.52; C["MILLION"]["currentRatePerMin"] = 0.092
    C["MILLION"]["previousRatePerMin"] = 0.132; C["MILLION"]["velocityLegPasses"] = False
if "Thronemind" in C:
    C["Thronemind"]["previousTotalSupply"] = 684; C["Thronemind"]["mintedInInterval"] = 48
    C["Thronemind"]["intervalMinutes"] = 54.52; C["Thronemind"]["currentRatePerMin"] = 0.880
    C["Thronemind"]["previousRatePerMin"] = 0.363; C["Thronemind"]["velocityLegPasses"] = True
    C["Thronemind"]["velocityNote"] = "Run 1131: velocity LULUS (0,880/mnt vs prev 0,363 = 2,42x, +48 token); free 36,6% >=25%; slot terbuka; umur ~23,4 jam. Gate website TETAP GAGAL -> tetap strong-lead-gate-blocked, tidak dilaporkan ulang."
if "Mossminds" in C:
    C["Mossminds"]["previousTotalSupply"] = 948; C["Mossminds"]["mintedInInterval"] = 40
    C["Mossminds"]["intervalMinutes"] = 54.52; C["Mossminds"]["currentRatePerMin"] = 0.734
    C["Mossminds"]["previousRatePerMin"] = 0.264; C["Mossminds"]["velocityLegPasses"] = True
    C["Mossminds"]["velocityNote"] = "Run 1131: velocity LULUS (0,734/mnt vs prev 0,264 = 2,78x, +40 token); free 34,2% >=25%. TAPI same-owner-discarded -> tidak pernah dipromosikan/dilaporkan."
if "StarAgent-7d39" in C:
    C["StarAgent-7d39"]["previousTotalSupply"] = 1122; C["StarAgent-7d39"]["mintedInInterval"] = 143
    C["StarAgent-7d39"]["intervalMinutes"] = 54.52; C["StarAgent-7d39"]["currentRatePerMin"] = 2.623
    C["StarAgent-7d39"]["previousRatePerMin"] = 0.099; C["StarAgent-7d39"]["velocityLegPasses"] = True
    C["StarAgent-7d39"]["velocityNote"] = "Run 1131: velocity LULUS (2,623/mnt vs prev ~0,099 = ~26x, +143 token). TAPI free % UNVERIFIED + umur UNVERIFIED -> watchlist-only, tidak bisa promosi."
if "Bianren" in C:
    C["Bianren"]["previousTotalSupply"] = 17; C["Bianren"]["mintedInInterval"] = 1
    C["Bianren"]["intervalMinutes"] = 54.52; C["Bianren"]["currentRatePerMin"] = 0.018
    C["Bianren"]["previousRatePerMin"] = None; C["Bianren"]["velocityLegPasses"] = False
    C["Bianren"]["velocityNote"] = "Run 1131: interval pertama (+1 token, 0,018/mnt) -> velocity TIDAK lolos (butuh >=20 token + rate sebelumnya); free 0,9% <25%; tetap EARLY."
if "Crack" in TC:
    setv(TC["Crack"], "totalSupply", 1144); setv(TC["Crack"], "totalMinted", 1144); setv(TC["Crack"], "publicRemaining", 4361)
    TC["Crack"]["runNote1131"] = "Run 1131: totalSupply/totalMinted 1091->1144 (+53), publicRemaining 4414->4361; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 — mint berikutnya BERBAYAR (0,001 BNB), TIDAK diotorisasi."
snap["last_run"] = "2026-11-06 run 1131"
snap["last_run_wib"] = "2026-11-06T11:31:00+07:00"
snap["runNote1131"] = "Run 1131 (SILENT): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 pending claim baru/dibuka, 0 lead/kandidat track-C baru. Scan SUKSES: window 131949390-131950389 (1000 blok, cap amendment), 40 panggilan Ankr, 0 error, 185 NFT + 294 ERC20-mint, 1 true first-seen (PACTURE NFT 0x55387dcf, bukan agent-shaped, log only). Thronemind velocity LULUS (+48, 2,42x) + free 36,6% + slot terbuka + umur ~23,4 jam, TAPI gate website TETAP GAGAL (re-check 0 hit) -> tetap strong-lead-gate-blocked, tidak dilaporkan ulang. Mossminds velocity LULUS (+40, 2,78x) + free 34,2% TAPI same-owner-discarded -> tidak dipromosikan. StarAgent-7d39 velocity LULUS (+143, ~26x) TAPI free % + umur UNVERIFIED -> watchlist-only. KING velocity GAGAL (0,61x) + free 24,85% <25% -> tetap EARLY. SEAT velocity GAGAL (0,79x) + free % unverified. Bianren +1 token, free 0,9%, slot unverified -> tetap EARLY. 5a: 1 baru Sourcify (0x98CB454b, mint+quote+agent tanpa free view -> bukan sale shape). 5c: 57 ERC20 mint>=10, 20 baru dicek, 0 sale shape. Track B binanceai tetap refund/failed. Bridge 0 baru. Boltbook 0 hit (newest 2026-11-05T09:20:52Z). Sweep: hanya proyek lama/dikenal (Piggy, Subsonic, Razor belum deploy, AGENT MAO paused). Odaily/PANews 0 mention Agent ID/free mint."
snap["runNote1131_scan"] = "Run 1131: SCAN SUKSES (pre-flight OK 10,7 dtk; head 131950320; 20 chunk selesai + shape-check, ~10 mnt). Watermark 131942908 -> 131950389. Gap 131942909-131949389 (6481 blok) belum ter-cover (backfill). 1 true first-seen: PACTURE NFT 0x55387dcf5E5d11c01f7264714de42aF3afB1DEc5 (7 mints/1 minter, registry=False, Sourcify verified, tanpa free funcs) -> bukan agent-shaped, log only. 5c: 20 ERC20 baru dicek, 0 sale shape."
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
# seen file: append scan-window contracts not yet in seen["contracts"]
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = seen.setdefault("contracts", {})
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-06-1131.json"))
sc_l = {k.lower() for k in sc}
added = 0
for c in scan["contracts"]:
    a = c["address"].lower()
    if a not in sc_l:
        sc[a] = c["first_block"]; added += 1
seen["_meta"]["last_scan_wib"] = "2026-11-06 run 1131"
seen["_meta"]["last_scan_window"] = "131949390-131950389"
seen["_meta"]["last_scan_added"] = added
seen["_meta"]["last_updated_wib"] = "2026-11-06 run 1131"
seen["_meta"]["note_1131"] = "Run 1131: 1 true first-seen (PACTURE NFT 0x55387dcf, 7 mints/1 minter, registry=False, Sourcify verified, tanpa free funcs) -> bukan agent-shaped, log only. + top-up scan-window contracts."
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
# scan state
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"] = 131950389
st["last_scan_window_from"] = 131949390
st["last_scan_window_to"] = 131950389
st["last_scan_wib"] = "run 2026-11-06-1131"
st["ankr_calls"] = 40
st["errors"] = []
st["nft_contracts"] = 185
st["erc20_mint_contracts"] = 294
st["skipped_gap"] = "131942909-131949389 (6481 blok; window dari watermark 131942908 ke head 131950389 = 7481 blok > cap 1000; scan menutup 1000 blok terbaru 131949390-131950389)"
st["note_1131_scan"] = "Run 1131: SCAN SUKSES (pre-flight OK 10,7 dtk; head 131950320; 20 chunk selesai + shape-check, ~10 mnt, 40 panggilan Ankr, 0 error). Watermark 131942908 -> 131950389. 1 true first-seen (PACTURE NFT, bukan agent-shaped, log only). 5c: 20 ERC20 baru dicek, 0 sale shape. Gap 131942909-131949389 belum ter-cover (backfill)."
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("FINALIZE OK; contracts:", len(C), "track_c:", len(TC), "seen added:", added)
