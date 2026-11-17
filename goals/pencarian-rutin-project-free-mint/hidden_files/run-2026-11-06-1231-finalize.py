#!/usr/bin/env python3
"""Run 2026-11-06 1231 WIB finalize (SILENT; no new promotion).
1. Snapshot numeric updates (None never overwrites) + velocity notes.
   Interval 1131-read blok 131949225 (12:01:47 WIB) -> 1231-read blok
   131952795 (12:28:34 WIB) = 3570 blok = 26.78 mnt (block timestamps).
2. Scan first-seen (correct dedupe vs seen["contracts"], lowercase):
   2 TRUE first-seen: FLEECE Sharks & Fish 0x5444E1c9 (ERC721, 10 mints/
   1 minter, first block 131952360, first mint 12:25:18 WIB, registry=
   False, Sourcify NOT verified, no free funcs) and Node Investment NFT
   0x67F858D0 (ERC721, 1 mint/1 minter, first block 131951814, first mint
   12:21:12 WIB, registry=False, Sourcify NOT verified) -> BOTH NOT
   agent-shaped, log only, NOT leads, NOT added to snapshot as leads.
3. Seen file: all scan-window contracts not yet in seen["contracts"].
4. Scan-state: shared watermark KEPT at backfill position 131913548
   (1031 precedent: main scan covered the NEWEST 1000 blocks
   131951813-131952812 while backfill sits at 131913548; advancing the
   shared watermark to 131952812 would silently skip the backfill gap
   131913549-131951812, ~38k blocks). Main-scan coverage recorded in
   last_main_scan_window_* + note_1231_scan.
5. Track-C: Crack totalSupply/totalMinted 1170, publicRemaining 4335.
6. KING Agent PROMOTION (decided after gate verdict; see KING_GATE
   block below): free 845/3333 = 25.36% >= 25% (freeQuota 3333,
   remainingFree 2488), age VERIFIED ~8h, slot open -> all three
   strong-lead legs met for the first time. Gate discovery (A)-(N)
   runs in a separate step; outcome recorded in king-gate.md.
7. Never touches scan-bridge.json.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1231"
KING_GATE = "BLOCKED"  # patched after gate verdict: BLOCKED | PASS | MINTED
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1231")
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
    C[name]["lastReadWib"] = "2026-11-06 run 1231"
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
        C[name]["runNote1231"] = note
vel("HIVE Agents", "Run 1231 (blok 131956609, interval 28,6 mnt vs run 1201): totalSupply 1253 flat -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
vel("KING Agent", "Run 1231 (blok 131956609): totalMinted gagal baca (None, nilai lama 845 dipertahankan); remainingFree 2488->2475 (+13 free claimed, 858/3333 = 25,74% >=25%, 0,455/mnt vs prev 0,635 = 0,72x, <20) -> velocity GAGAL. Slot terbuka (costOf 0, mintedBy 0, balance 0). Status tetap strong-lead-gate-blocked-2026-11-06 (gate website GAGAL run 1201); TIDAK dilaporkan ulang, TIDAK di-preview/di-mint.")
vel("MILLION", "Run 1231 (blok 131956609): totalMinted 187->188 (+1, <20) -> velocity GAGAL. Free leg tetap UNVERIFIED. Tetap EARLY.")
vel("SEAT-f11e", "Run 1231: totalSupply/totalMinted 3884->4039 (+155, 5,420/mnt vs prev 1,755 = 3,09x >=1,5x DAN >=20 token) -> velocity LOLOS. TAPI free % tetap UNVERIFIED -> TIDAK BISA promosi; watchlist-only.")
vel("Forklings", "Run 1231: freeMinted 970->974 (+4, <20) -> velocity GAGAL; 974/2000=48,7% <50%; sudah strong-lead-gate-blocked sejak 2026-11-05, tidak dilaporkan ulang.")
vel("PassAgentX", "Run 1231: totalSupply 4047->4052 (+5), freeMinted 3829->3834 (+5, <20) -> velocity GAGAL; watchlist-only.")
vel("FOD Agent", "Run 1231: totalMinted 500 flat vs run 1201 (500) -> velocity GAGAL; costOf(user,1)=0,0005 BNB (paid leg); tetap EARLY.")
vel("Thronemind", "Run 1231 (blok 131956609, interval 28,6 mnt): totalSupply 740 flat vs run 1201 (740) -> velocity GAGAL. Free 740/2000=37,0% >=25%; slot terbuka (canFreeMint=1, claimedFree=0, balance 0); umur ~24,5 jam. Sudah strong-lead-gate-blocked -> TIDAK di-preview/di-mint, TIDAK dilaporkan ulang.")
vel("Hashseers", "Run 1231: totalSupply 610->612 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("Smeltbots", "Run 1231: totalSupply 628 flat vs run 1201 (628) -> velocity GAGAL; watchlist-only.")
vel("Agent Frogs", "Run 1231: totalSupply 441->456 (+15, <20) -> velocity GAGAL; watchlist-only.")
vel("StarAgent-7d39", "Run 1231: totalSupply 1350->1409 (+59, 2,063/mnt vs prev 3,174 = 0,65x <1,5x) -> velocity GAGAL. Free % UNVERIFIED + umur UNVERIFIED -> TIDAK BISA promosi; watchlist-only.")
vel("Layerloom", "Run 1231: totalSupply 730->735 (+5, <20) -> velocity GAGAL; watchlist-only.")
vel("Tumblebots", "Run 1231: totalSupply 687->691 (+4, <20) -> velocity GAGAL; watchlist-only.")
vel("Mossminds", "Run 1231: totalSupply 990->992 (+2, <20, 0,070/mnt vs prev 0,075 = 0,93x) -> velocity GAGAL; free 989/2880=34,3% >=25%. TAPI status promotion-discarded-same-owner -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead; log only.")
vel("Jolly", "Run 1231: totalMinted 3678->3680 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("LuckyBox-d08e", "Run 1231: totalSupply 638 flat vs run 1201 (638) -> velocity GAGAL; watchlist-only.")
vel("SnailMail", "Run 1231: totalSupply 319 flat vs run 1201 (319) -> velocity GAGAL; watchlist-only.")
vel("Mummyhive", "Run 1231: totalSupply 600 flat vs run 1201 (600) -> velocity GAGAL; watchlist-only.")
vel("wheelz", "Run 1231: totalSupply 321 flat vs run 1201 (321) -> velocity GAGAL; watchlist-only.")
vel("Cipher Mind", "Run 1231: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("Cyber Lynx Agent", "Run 1231: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("CantonTron", "Run 1231: totalMinted 419->430 (+11, <20) -> velocity GAGAL. Track-C gate-failed, sudah dilaporkan sekali hot leg 10:10 WIB; TIDAK dilaporkan ulang; TIDAK di-preview/di-mint.")
vel("Bianren", "Run 1231: totalMinted 21 flat vs run 1201 (21) -> velocity GAGAL; free 21/2000=1,05% <25%; slot user tetap UNVERIFIED (quote ~0,000187 BNB); gate website tetap BELUM LOLOS; tetap EARLY, TIDAK di-preview/di-mint.")
# rate fields for next run
if "KING Agent" in C:
    C["KING Agent"]["previousTotalSupply"] = 845; C["KING Agent"]["mintedInInterval"] = 13
    C["KING Agent"]["intervalMinutes"] = 28.6; C["KING Agent"]["currentRatePerMin"] = 0.455
    C["KING Agent"]["previousRatePerMin"] = 0.635; C["KING Agent"]["velocityLegPasses"] = False
    C["KING Agent"]["velocityNote"] = "Run 1231: velocity GAGAL (0,455/mnt via remainingFree delta vs prev 0,635 = 0,72x, +13 token <20; totalMinted gagal baca run ini); free 25,74% >=25% -> tetap strong-lead-gate-blocked."
if "SEAT-f11e" in C:
    C["SEAT-f11e"]["previousTotalSupply"] = 3884; C["SEAT-f11e"]["mintedInInterval"] = 155
    C["SEAT-f11e"]["intervalMinutes"] = 28.6; C["SEAT-f11e"]["currentRatePerMin"] = 5.42
    C["SEAT-f11e"]["previousRatePerMin"] = 1.755; C["SEAT-f11e"]["velocityLegPasses"] = True
    C["SEAT-f11e"]["velocityNote"] = "Run 1231: velocity LOLOS (5,420/mnt vs prev 1,755 = 3,09x, +155 token); free % UNVERIFIED -> watchlist-only, TIDAK BISA promosi."
if "MILLION" in C:
    C["MILLION"]["previousTotalSupply"] = 187; C["MILLION"]["mintedInInterval"] = 1
    C["MILLION"]["intervalMinutes"] = 28.6; C["MILLION"]["currentRatePerMin"] = 0.035
    C["MILLION"]["previousRatePerMin"] = 0.0; C["MILLION"]["velocityLegPasses"] = False
if "Thronemind" in C:
    C["Thronemind"]["previousTotalSupply"] = 740; C["Thronemind"]["mintedInInterval"] = 0
    C["Thronemind"]["intervalMinutes"] = 28.6; C["Thronemind"]["currentRatePerMin"] = 0.0
    C["Thronemind"]["previousRatePerMin"] = 0.299; C["Thronemind"]["velocityLegPasses"] = False
    C["Thronemind"]["velocityNote"] = "Run 1231: velocity GAGAL (0,000/mnt vs prev 0,299, +0 token); free 37,0% >=25%; slot terbuka; umur ~24,5 jam. Sudah strong-lead-gate-blocked."
if "Mossminds" in C:
    C["Mossminds"]["previousTotalSupply"] = 990; C["Mossminds"]["mintedInInterval"] = 2
    C["Mossminds"]["intervalMinutes"] = 28.6; C["Mossminds"]["currentRatePerMin"] = 0.07
    C["Mossminds"]["previousRatePerMin"] = 0.075; C["Mossminds"]["velocityLegPasses"] = False
    C["Mossminds"]["velocityNote"] = "Run 1231: velocity GAGAL (0,070/mnt vs prev 0,075 = 0,93x, +2 token); free 34,3% >=25%. TAPI same-owner-discarded -> tidak pernah dipromosikan/dilaporkan."
if "StarAgent-7d39" in C:
    C["StarAgent-7d39"]["previousTotalSupply"] = 1350; C["StarAgent-7d39"]["mintedInInterval"] = 59
    C["StarAgent-7d39"]["intervalMinutes"] = 28.6; C["StarAgent-7d39"]["currentRatePerMin"] = 2.063
    C["StarAgent-7d39"]["previousRatePerMin"] = 3.174; C["StarAgent-7d39"]["velocityLegPasses"] = False
    C["StarAgent-7d39"]["velocityNote"] = "Run 1231: velocity GAGAL (2,063/mnt vs prev 3,174 = 0,65x, +59 token). Free % UNVERIFIED + umur UNVERIFIED -> watchlist-only."
if "Bianren" in C:
    C["Bianren"]["previousTotalSupply"] = 21; C["Bianren"]["mintedInInterval"] = 0
    C["Bianren"]["intervalMinutes"] = 28.6; C["Bianren"]["currentRatePerMin"] = 0.0
    C["Bianren"]["previousRatePerMin"] = 0.112; C["Bianren"]["velocityLegPasses"] = False
    C["Bianren"]["velocityNote"] = "Run 1231: velocity GAGAL (+0 token, 0,000/mnt); free 1,05% <25%; tetap EARLY."
if "Crack" in TC:
    setv(TC["Crack"], "totalSupply", 1461); setv(TC["Crack"], "totalMinted", 1463); setv(TC["Crack"], "publicRemaining", 4037)
TC["Crack"]["runNote1231"] = "Run 1231: totalSupply/totalMinted 1170->1461/1463 (+291/+293), publicRemaining 4335->4037; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 — mint berikutnya BERBAYAR (0,001 BNB), TIDAK diotorisasi."
# KING drift (already strong-lead-gate-blocked in run 1201; no re-promotion, no re-report)
if "KING Agent" in C:
    C["KING Agent"]["remainingFree"] = 2475
    C["KING Agent"]["gateNote1231"] = "Run 1231 drift: remainingFree 2488->2475 (free claimed 858/3333 = 25,74% >=25%); slot tetap terbuka (costOf 0, mintedBy 0, balance 0); totalMinted gagal baca run ini. Status tetap strong-lead-gate-blocked-2026-11-06 (gate website GAGAL run 1201, metode A-N); TIDAK dilaporkan ulang, TIDAK di-preview/di-mint."
snap["last_run"] = "2026-11-06 run 1231"
snap["last_run_wib"] = "2026-11-06T12:31:00+07:00"
snap["runNote1231"] = ("Run 1231: SILENT — 0 kandidat baru, 0 early lead baru, 0 pending claim baru/dibuka, 0 lead/kandidat track-C baru, 0 promosi baru. SEAT-f11e velocity LOLOS (5,420/mnt, 3,09x, +155) tapi free % UNVERIFIED -> watchlist-only, bukan promosi. KING Agent drift saja (remainingFree 2488->2475, free 25,74%); status tetap strong-lead-gate-blocked-2026-11-06, tidak dilaporkan ulang. Scan SUKSES: window 131955635-131956634 (1000 blok, cap amendment), pre-flight OK 6,2 dtk, 40 panggilan Ankr, 0 error, 155 NFT + 387 ERC20-mint, 2 true first-seen (Standboy 0x6043a590 + Stickman 0x345b0eb3 — keduanya bukan agent-shaped, log only). 5a: 1 baru Sourcify (0x919CEdeb, bukan sale shape). 5c: 20 ERC20 baru dicek, 0 sale shape. Track B binanceai tetap refund/failed. Bridge 0 baru. Boltbook 0 hit (newest 2026-11-05T09:20:52Z). Sweep: hanya proyek lama/dikenal (daftar 22 proyek Substack 10 hari, AGENT MAO paused, Ptah). Odaily/PANews 0 mention Agent ID/free mint. Watermark bersama tetap di posisi backfill 131913548 (main scan menutup 1000 blok terbaru; gap 131913549-131955634 ditutup backfill).")
snap["runNote1231_scan"] = "Run 1231: SCAN SUKSES (pre-flight OK 6,2 dtk; head 131956609; 20 chunk selesai + shape-check, 40 panggilan Ankr, 0 error). Window 131955635-131956634 (1000 blok terbaru, cap amendment). Watermark bersama TIDAK dimajukan (tetap 131913548, posisi backfill — preseden 1031) agar gap 131913549-131955634 (~42k blok) tidak dilewati diam-diam. 2 true first-seen: Standboy 0x6043a590 (67 mints/67 minters, first mint 12:50:10 WIB, registry_bytes_hit=True tapi Sourcify not_verified + agentRegistry()/free views semua revert/null -> bukan agent-shaped) + Stickman 0x345b0eb3 (35 mints/35 minters, first mint 12:50:01 WIB, registry=False, Sourcify not_verified, PRICE 0,0015 BNB paid) -> keduanya bukan agent-shaped, log only. 5c: 20 ERC20 baru dicek, 0 sale shape."
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
# seen file: append scan-window contracts not yet in seen["contracts"]
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = seen.setdefault("contracts", {})
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-06-1231.json"))
sc_l = {k.lower() for k in sc}
added = 0
for c in scan["contracts"]:
    a = c["address"].lower()
    if a not in sc_l:
        sc[a] = c["first_block"]; added += 1
seen.setdefault("_meta", {})["last_scan_wib"] = "2026-11-06 run 1231"
seen["_meta"]["last_scan_window"] = "131955635-131956634"
seen["_meta"]["last_scan_added"] = added
seen["_meta"]["last_updated_wib"] = "2026-11-06 run 1231"
seen["_meta"]["note_1231"] = "Run 1231: 2 true first-seen (Standboy 0x6043a590, 67 mints/67 minters, first mint 12:50:10 WIB; Stickman 0x345b0eb3, 35 mints/35 minters, first mint 12:50:01 WIB) — keduanya bukan agent-shaped (Standboy: registry-bytes hit tapi Sourcify not_verified + agentRegistry/free views null; Stickman: registry=False, PRICE 0,0015 BNB paid), log only. + top-up scan-window contracts."
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
# scan state: keep shared watermark at backfill position; record main-scan coverage
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_main_scan_window_from"] = 131955635
st["last_main_scan_window_to"] = 131956634
st["last_scan_wib"] = "run 2026-11-06-1231 (main scan; shared watermark kept at backfill 131913548)"
st["ankr_calls"] = 40
st["errors"] = []
st["nft_contracts"] = 155
st["erc20_mint_contracts"] = 387
st["skipped_gap"] = "131913549-131955634 (~42.086 blok; window dari watermark bersama 131913548 ke head 131956634 > cap 1000; main scan menutup 1000 blok terbaru 131955635-131956634; gap ditutup bertahap oleh backfill)"
st["note_1231_scan"] = "Run 1231: SCAN SUKSES (pre-flight OK 6,2 dtk; head 131956609; 20 chunk selesai + shape-check, 40 panggilan Ankr, 0 error). Watermark bersama TIDAK dimajukan (tetap 131913548, posisi backfill — preseden 1031) agar gap 131913549-131955634 tidak dilewati diam-diam; cakupan main scan tersimpan di onchain-scan-2026-11-06-1231.json. 2 true first-seen (Standboy + Stickman, bukan agent-shaped, log only). 5c: 20 ERC20 baru dicek, 0 sale shape."
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("FINALIZE OK; contracts:", len(C), "track_c:", len(TC), "seen added:", added, "KING_GATE:", KING_GATE)
