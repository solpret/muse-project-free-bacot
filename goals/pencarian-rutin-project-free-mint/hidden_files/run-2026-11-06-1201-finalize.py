#!/usr/bin/env python3
"""Run 2026-11-06 1201 WIB finalize (SILENT except KING promotion handling).
1. Snapshot numeric updates (None never overwrites) + velocity notes.
   Interval 1131-read blok 131949225 (12:01:47 WIB) -> 1201-read blok
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
   last_main_scan_window_* + note_1201_scan.
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
TS = "2026-11-06-1201"
KING_GATE = "BLOCKED"  # patched after gate verdict: BLOCKED | PASS | MINTED
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1201")
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
    C[name]["lastReadWib"] = "2026-11-06 run 1201"
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
        C[name]["runNote1201"] = note
vel("HIVE Agents", "Run 1201 (blok 131952795, interval 26,78 mnt vs run 1131): totalSupply 1253 flat -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
vel("KING Agent", "Run 1201 (blok 131952795): totalMinted 828->845 (+17, <20, 0,635/mnt vs prev 0,660 = 0,96x) -> velocity GAGAL. Free 845/3333 = 25,36% >=25% (freeQuota 3333, remainingFree 2488) -> kaki strong-lead (b) TERPENUHI pertama kali; umur ~8 jam TERVERIFIKASI; slot terbuka (costOf 0, mintedBy 0, balance 0) -> PROMOSI ke strong lead; gate website dicek run ini (lihat king-gate.md).")
vel("MILLION", "Run 1201 (blok 131952795): totalMinted 187 flat vs run 1131 (187) -> velocity GAGAL. Free leg tetap UNVERIFIED. Tetap EARLY.")
vel("SEAT-f11e", "Run 1201: totalSupply/totalMinted 3837->3884 (+47, 1,755/mnt vs prev 2,036 = 0,86x) -> velocity GAGAL. Free % tetap UNVERIFIED -> TIDAK BISA promosi; watchlist-only.")
vel("Forklings", "Run 1201: freeMinted 965->970 (+5, <20) -> velocity GAGAL; 970/2000=48,5% <50%; sudah strong-lead-gate-blocked sejak 2026-11-05, tidak dilaporkan ulang.")
vel("PassAgentX", "Run 1201: totalSupply 4035->4047 (+12), freeMinted 3817->3829 (+12, <20) -> velocity GAGAL; watchlist-only.")
vel("FOD Agent", "Run 1201: totalMinted 500 flat vs run 1131 (500) -> velocity GAGAL; costOf(user,1)=0,0005 BNB (paid leg); tetap EARLY.")
vel("Thronemind", "Run 1201 (blok 131952795, interval 26,78 mnt): totalSupply 732->740 (+8, <20, 0,299/mnt vs prev 0,880 = 0,34x) -> velocity GAGAL. Free 740/2000=37,0% >=25%; slot terbuka (canFreeMint=1, claimedFree=0, balance 0); umur ~24 jam. Sudah strong-lead-gate-blocked (gate website TETAP GAGAL, re-check nama run ini 0 hit) -> TIDAK di-preview/di-mint, TIDAK dilaporkan ulang.")
vel("Hashseers", "Run 1201: totalSupply 610->612 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("Smeltbots", "Run 1201: totalSupply 628 flat vs run 1131 (628) -> velocity GAGAL; watchlist-only.")
vel("Agent Frogs", "Run 1201: totalSupply 441->456 (+15, <20) -> velocity GAGAL; watchlist-only.")
vel("StarAgent-7d39", "Run 1201: totalSupply 1265->1350 (+85, 3,174/mnt vs prev 2,623 = 1,21x <1,5x) -> velocity GAGAL. Free % UNVERIFIED + umur UNVERIFIED -> TIDAK BISA promosi; watchlist-only.")
vel("Layerloom", "Run 1201: totalSupply 730->735 (+5, <20) -> velocity GAGAL; watchlist-only.")
vel("Tumblebots", "Run 1201: totalSupply 687->691 (+4, <20) -> velocity GAGAL; watchlist-only.")
vel("Mossminds", "Run 1201: totalSupply 988->990 (+2, <20, 0,075/mnt vs prev 0,734 = 0,10x) -> velocity GAGAL; free 987/2880=34,3% >=25%. TAPI status promotion-discarded-same-owner -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead; log only.")
vel("Jolly", "Run 1201: totalMinted 3678->3680 (+2, <20) -> velocity GAGAL; watchlist-only.")
vel("LuckyBox-d08e", "Run 1201: totalSupply 638 flat vs run 1131 (638) -> velocity GAGAL; watchlist-only.")
vel("SnailMail", "Run 1201: totalSupply 319 flat vs run 1131 (319) -> velocity GAGAL; watchlist-only.")
vel("Mummyhive", "Run 1201: totalSupply 600 flat vs run 1131 (600) -> velocity GAGAL; watchlist-only.")
vel("wheelz", "Run 1201: totalSupply 321 flat vs run 1131 (321) -> velocity GAGAL; watchlist-only.")
vel("Cipher Mind", "Run 1201: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("Cyber Lynx Agent", "Run 1201: totalSupply 3333, totalMinted 1 flat (paid template, PRICE 0,0005 BNB, spotsLeft 3332); watchlist-only.")
vel("CantonTron", "Run 1201: totalMinted 394->419 (+25) — interval pertama dengan rate (belum ada rate sebelumnya) -> TIDAK BISA lolos velocity sendirian; baseline dicatat. Track-C gate-failed, sudah dilaporkan sekali hot leg 10:10 WIB; TIDAK dilaporkan ulang; TIDAK di-preview/di-mint.")
vel("Bianren", "Run 1201: totalMinted 18->21 (+3, <20) -> velocity GAGAL; free 21/2000=1,05% <25%; slot user tetap UNVERIFIED (quote ~0,000187 BNB); gate website tetap BELUM LOLOS; tetap EARLY, TIDAK di-preview/di-mint.")
# rate fields for next run
if "KING Agent" in C:
    C["KING Agent"]["previousTotalSupply"] = 828; C["KING Agent"]["mintedInInterval"] = 17
    C["KING Agent"]["intervalMinutes"] = 26.78; C["KING Agent"]["currentRatePerMin"] = 0.635
    C["KING Agent"]["previousRatePerMin"] = 0.660; C["KING Agent"]["velocityLegPasses"] = False
    C["KING Agent"]["velocityNote"] = "Run 1201: velocity GAGAL (0,635/mnt vs prev 0,660 = 0,96x, +17 token <20); free 25,36% >=25% -> promosi strong lead (gate dicek run ini)."
if "SEAT-f11e" in C:
    C["SEAT-f11e"]["previousTotalSupply"] = 3837; C["SEAT-f11e"]["mintedInInterval"] = 47
    C["SEAT-f11e"]["intervalMinutes"] = 26.78; C["SEAT-f11e"]["currentRatePerMin"] = 1.755
    C["SEAT-f11e"]["previousRatePerMin"] = 2.036; C["SEAT-f11e"]["velocityLegPasses"] = False
    C["SEAT-f11e"]["velocityNote"] = "Run 1201: velocity GAGAL (1,755/mnt vs prev 2,036 = 0,86x, +47 token); free % UNVERIFIED -> watchlist-only."
if "MILLION" in C:
    C["MILLION"]["previousTotalSupply"] = 187; C["MILLION"]["mintedInInterval"] = 0
    C["MILLION"]["intervalMinutes"] = 26.78; C["MILLION"]["currentRatePerMin"] = 0.0
    C["MILLION"]["previousRatePerMin"] = 0.092; C["MILLION"]["velocityLegPasses"] = False
if "Thronemind" in C:
    C["Thronemind"]["previousTotalSupply"] = 732; C["Thronemind"]["mintedInInterval"] = 8
    C["Thronemind"]["intervalMinutes"] = 26.78; C["Thronemind"]["currentRatePerMin"] = 0.299
    C["Thronemind"]["previousRatePerMin"] = 0.880; C["Thronemind"]["velocityLegPasses"] = False
    C["Thronemind"]["velocityNote"] = "Run 1201: velocity GAGAL (0,299/mnt vs prev 0,880 = 0,34x, +8 token <20); free 37,0% >=25%; slot terbuka; umur ~24 jam. Sudah strong-lead-gate-blocked."
if "Mossminds" in C:
    C["Mossminds"]["previousTotalSupply"] = 988; C["Mossminds"]["mintedInInterval"] = 2
    C["Mossminds"]["intervalMinutes"] = 26.78; C["Mossminds"]["currentRatePerMin"] = 0.075
    C["Mossminds"]["previousRatePerMin"] = 0.734; C["Mossminds"]["velocityLegPasses"] = False
    C["Mossminds"]["velocityNote"] = "Run 1201: velocity GAGAL (0,075/mnt vs prev 0,734 = 0,10x, +2 token); free 34,3% >=25%. TAPI same-owner-discarded -> tidak pernah dipromosikan/dilaporkan."
if "StarAgent-7d39" in C:
    C["StarAgent-7d39"]["previousTotalSupply"] = 1265; C["StarAgent-7d39"]["mintedInInterval"] = 85
    C["StarAgent-7d39"]["intervalMinutes"] = 26.78; C["StarAgent-7d39"]["currentRatePerMin"] = 3.174
    C["StarAgent-7d39"]["previousRatePerMin"] = 2.623; C["StarAgent-7d39"]["velocityLegPasses"] = False
    C["StarAgent-7d39"]["velocityNote"] = "Run 1201: velocity GAGAL (3,174/mnt vs prev 2,623 = 1,21x <1,5x, +85 token). Free % UNVERIFIED + umur UNVERIFIED -> watchlist-only."
if "Bianren" in C:
    C["Bianren"]["previousTotalSupply"] = 18; C["Bianren"]["mintedInInterval"] = 3
    C["Bianren"]["intervalMinutes"] = 26.78; C["Bianren"]["currentRatePerMin"] = 0.112
    C["Bianren"]["previousRatePerMin"] = 0.018; C["Bianren"]["velocityLegPasses"] = False
    C["Bianren"]["velocityNote"] = "Run 1201: velocity GAGAL (+3 token, 0,112/mnt); free 1,05% <25%; tetap EARLY."
if "Crack" in TC:
    setv(TC["Crack"], "totalSupply", 1170); setv(TC["Crack"], "totalMinted", 1170); setv(TC["Crack"], "publicRemaining", 4335)
    TC["Crack"]["runNote1201"] = "Run 1201: totalSupply/totalMinted 1144->1170 (+26), publicRemaining 4361->4335; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 — mint berikutnya BERBAYAR (0,001 BNB), TIDAK diotorisasi."
# KING promotion outcome (patched per gate verdict before running)
if KING_GATE == "BLOCKED":
    if "KING Agent" in C:
        C["KING Agent"]["status"] = "strong-lead-gate-blocked-2026-11-06"
        C["KING Agent"]["gateNote1201"] = "PROMOSI ke strong lead run 1201 (dilaporkan sekali, gate-blocked, TIDAK di-mint): 3 kaki lolos — umur TERVERIFIKASI ~8 jam (first mint 2026-11-06 04:31:20 WIB), free 845/3333 = 25,36% (freeQuota 3333, remainingFree 2488), slot user terbuka (costOf 0, mintedBy 0, balance 0). Gate website GAGAL (metode A-N, lihat king-gate.md); X UNVERIFIED (opsional, bukan blocker). Bukan kandidat. Tidak dilaporkan ulang."
elif KING_GATE == "PASS":
    if "KING Agent" in C:
        C["KING Agent"]["status"] = "strong-lead-2026-11-06"
        C["KING Agent"]["gateNote1201"] = "PROMOSI ke strong lead run 1201: 3 kaki lolos; gate website LOLOS (lihat king-gate.md). Lanjut safety check + preview sebelum eksekusi (langkah terpisah)."
elif KING_GATE == "MINTED":
    if "KING Agent" in C:
        C["KING Agent"]["status"] = "minted-by-user-2026-11-06"
        C["KING Agent"]["gateNote1201"] = "PROMOSI ke strong lead run 1201 + DIRECT MINT berhasil (lihat king-gate.md + mint report)."
snap["last_run"] = "2026-11-06 run 1201"
snap["last_run_wib"] = "2026-11-06T12:01:00+07:00"
snap["runNote1201"] = ("Run 1201: KING Agent PROMOSI EARLY->strong lead (free 845/3333=25,36% >=25%, umur ~8 jam, slot terbuka); gate website " + ("GAGAL (A-N) -> dilaporkan sekali sebagai strong lead gate-blocked, TIDAK di-mint." if KING_GATE == "BLOCKED" else ("LOLOS -> lanjut safety/preview (langkah terpisah)." if KING_GATE == "PASS" else "LOLOS + DIRECT MINT berhasil.")) +
 " Selain itu SILENT: 0 kandidat baru, 0 early lead baru, 0 pending claim baru/dibuka, 0 lead/kandidat track-C baru. Scan SUKSES: window 131951813-131952812 (1000 blok, cap amendment), pre-flight OK 3,0 dtk, 40 panggilan Ankr, 0 error, 156 NFT + 333 ERC20-mint, 2 true first-seen (FLEECE Sharks & Fish 0x5444E1c9 + Node Investment NFT 0x67F858D0 — keduanya bukan agent-shaped, log only). 5a: 0 baru Sourcify. 5c: 14 ERC20 baru dicek, 0 sale shape. Track B binanceai tetap refund/failed. Bridge 0 baru. Boltbook 0 hit (newest 2026-11-05T09:20:52Z). Sweep: hanya proyek lama/dikenal (Ptah, AGENT MAO paused, Subsonic dkk, $SWARM paid sale, AgentID ETH out-of-scope). Odaily/PANews 0 mention Agent ID/free mint. Watermark bersama tetap di posisi backfill 131913548 (main scan menutup 1000 blok terbaru; gap 131913549-131951812 ditutup backfill).")
snap["runNote1201_scan"] = "Run 1201: SCAN SUKSES (pre-flight OK 3,0 dtk; head 131952763; 20 chunk selesai + shape-check, 40 panggilan Ankr, 0 error). Window 131951813-131952812 (1000 blok terbaru, cap amendment). Watermark bersama TIDAK dimajukan (tetap 131913548, posisi backfill — preseden 1031) agar gap 131913549-131951812 (~38k blok) tidak dilewati diam-diam. 2 true first-seen: FLEECE Sharks & Fish 0x5444E1c9 (10 mints/1 minter, first mint 12:25:18 WIB, registry=False, Sourcify not_verified) + Node Investment NFT 0x67F858D0 (1 mint/1 minter, first mint 12:21:12 WIB, registry=False, Sourcify not_verified) -> keduanya bukan agent-shaped, log only. 5c: 14 ERC20 baru dicek, 0 sale shape."
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
# seen file: append scan-window contracts not yet in seen["contracts"]
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = seen.setdefault("contracts", {})
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-06-1201.json"))
sc_l = {k.lower() for k in sc}
added = 0
for c in scan["contracts"]:
    a = c["address"].lower()
    if a not in sc_l:
        sc[a] = c["first_block"]; added += 1
seen.setdefault("_meta", {})["last_scan_wib"] = "2026-11-06 run 1201"
seen["_meta"]["last_scan_window"] = "131951813-131952812"
seen["_meta"]["last_scan_added"] = added
seen["_meta"]["last_updated_wib"] = "2026-11-06 run 1201"
seen["_meta"]["note_1201"] = "Run 1201: 2 true first-seen (FLEECE Sharks & Fish 0x5444E1c9, 10 mints/1 minter, first mint 12:25:18 WIB; Node Investment NFT 0x67F858D0, 1 mint/1 minter, first mint 12:21:12 WIB) — keduanya registry=False, Sourcify not_verified, tanpa free funcs -> bukan agent-shaped, log only. + top-up scan-window contracts."
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
# scan state: keep shared watermark at backfill position; record main-scan coverage
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_main_scan_window_from"] = 131951813
st["last_main_scan_window_to"] = 131952812
st["last_scan_wib"] = "run 2026-11-06-1201 (main scan; shared watermark kept at backfill 131913548)"
st["ankr_calls"] = 40
st["errors"] = []
st["nft_contracts"] = 156
st["erc20_mint_contracts"] = 333
st["skipped_gap"] = "131913549-131951812 (~38.264 blok; window dari watermark bersama 131913548 ke head 131952812 > cap 1000; main scan menutup 1000 blok terbaru 131951813-131952812; gap ditutup bertahap oleh backfill)"
st["note_1201_scan"] = "Run 1201: SCAN SUKSES (pre-flight OK 3,0 dtk; head 131952763; 20 chunk selesai + shape-check, 40 panggilan Ankr, 0 error). Watermark bersama TIDAK dimajukan (tetap 131913548, posisi backfill — preseden 1031) agar gap 131913549-131951812 tidak dilewati diam-diam; cakupan main scan tersimpan di onchain-scan-2026-11-06-1201.json. 2 true first-seen (FLEECE + Node Investment NFT, bukan agent-shaped, log only). 5c: 14 ERC20 baru dicek, 0 sale shape."
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("FINALIZE OK; contracts:", len(C), "track_c:", len(TC), "seen added:", added, "KING_GATE:", KING_GATE)
