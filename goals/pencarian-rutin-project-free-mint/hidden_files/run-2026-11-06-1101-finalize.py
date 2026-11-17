#!/usr/bin/env python3
"""Run 2026-11-06 1101 WIB finalize.
1. Snapshot numeric updates (None never overwrites) + velocity notes.
   Interval 1031-read blok 131937922 (~10:37 WIB) -> 1101-read blok 131941958
   (~11:07 WIB) = 4036 blok ~30,3 mnt.
2. Scan first-seen (correct dedupe vs seen["contracts"], lowercase keys):
   2 TRUE first-seen: Goblin Protocol (not agent-shaped, log only) + Bianren
   (agent-shaped EARLY lead, reported once). The other 21 triaged contracts
   were already in the seen file (first_block Nov 1-4) — NOT first-seen, NOT
   leads; most age-excluded by seen first_block (Nov 1-3) or 48h-boundary
   hits; Labyrinthos free 91,7% is moot (first seen Nov 3 10:49, >48h).
3. Seen file: all scan-window contracts not yet in seen["contracts"].
4. Scan-state: watermark -> 131942908 (scan SUKSES); skipped gap
   131937879-131941908 (4030 blok, backfill).
5. Track-C: Crack totalSupply 1091, publicRemaining 4414. Never touches
   scan-bridge.json.
GATE_STATUS_BIANREN is filled in by hand after the browser site check."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1101"
GATE_STATUS_BIANREN = "GATE WEBSITE BELUM LOLOS (run 1101): website dari tokenURI https://bbyr4.pages.dev TIDAK BISA DIVERIFIKASI - browser: DNS name_not_resolved (3x percobaan, 11:55 WIB); curl VM: empty reply (HTTP 000). Situs tidak termuat sama sekali, tidak mencetak kontrak. Tidak ada eksekusi (mint/preview) sampai website terverifikasi; early lead tetap dilacak."
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1101")
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
 "Crack": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted"), ("publicRemaining", "publicRemaining")],
}
# capture pre-update values for delta notes
OLD = {}
for name, pairs in NUMMAP.items():
    if name in C and name in RR.get("reread", {}):
        OLD[name] = {snapk: C[name].get(snapk) for snapk, _ in pairs}
for name, pairs in NUMMAP.items():
    if name not in C or name not in RR.get("reread", {}):
        continue
    for snapk, rrk in pairs:
        setv(C[name], snapk, RR["reread"][name].get(rrk))
    C[name]["lastReadBlock"] = BLK
    C[name]["lastReadWib"] = "2026-11-06 run 1101"
# track_c readable values
TC = snap.setdefault("track_c", {})
TCMAP = {
 "OSK": [("opened", "opened")],
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
        C[name]["runNote1101"] = note
vel("HIVE Agents", "Run 1101 (blok 131941958): totalSupply 1253 flat vs run 1031 (1253) -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
vel("KING Agent", "Run 1101 (blok 131941958): totalMinted 759->792 (+33, ~30,3 mnt = 1,089/mnt vs prev 0,616/mnt = 1,77x) -> velocity LULUS (>=1,5x DAN >=20 token). Free 792/3333=23,76% <25% kaki strong-lead -> TETAP EARLY, bukan strong lead, bukan kandidat. Slot user terbuka (costOf 0, mintedBy 0, balance 0).")
vel("MILLION", "Run 1101 (blok 131941958): totalMinted 178->182 (+4, <20) -> velocity GAGAL. Free leg tetap UNVERIFIED (free views revert). Tetap EARLY.")
vel("SEAT-f11e", "Run 1101: totalSupply/totalMinted 3648->3726 (+78, ~30,3 mnt = 2,574/mnt vs prev 1,497/mnt = 1,72x) -> velocity LULUS (>=1,5x DAN >=20 token). Free % tetap UNVERIFIED (tanpa free view) -> TIDAK BISA promosi; watchlist-only.")
vel("Forklings", "Run 1101: freeMinted 951->955 (+4, <20) -> velocity GAGAL; 955/2000=47,75% <50%; strong-lead gate-blocked, watchlist-only.")
vel("PassAgentX", "Run 1101: totalSupply 4009->4018 (+9), freeMinted 3791->3800 (+9, <20) -> velocity GAGAL; watchlist-only.")
vel("FOD Agent", "Run 1101: totalMinted 500 flat vs run 1031 (500) -> velocity GAGAL; costOf(user,1)=0,0005 BNB (paid leg); tetap EARLY.")
vel("Thronemind", "Run 1101: totalSupply 673->684 (+11, <20) -> velocity GAGAL; watchlist-only.")
vel("Hashseers", "Run 1101: totalSupply 607->608 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("Smeltbots", "Run 1101: totalSupply 625->626 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("Agent Frogs", "Run 1101: totalSupply 438->439 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("StarAgent-7d39", "Run 1101: totalSupply 1119->1122 (+3, <20) -> velocity GAGAL; watchlist-only.")
vel("Layerloom", "Run 1101: totalSupply 719->724 (+5, <20) -> velocity GAGAL; watchlist-only.")
vel("Tumblebots", "Run 1101: totalSupply 680->684 (+4, <20) -> velocity GAGAL; watchlist-only.")
vel("Mossminds", "Run 1101: totalSupply 940->948 (+8, <20) -> velocity GAGAL; watchlist-only.")
vel("Jolly", "Run 1101: totalMinted 3667->3668 (+1, <20) -> velocity GAGAL; watchlist-only.")
vel("LuckyBox-d08e", "Run 1101: totalSupply 633->636 (+3, <20) -> velocity GAGAL; watchlist-only.")
vel("SnailMail", "Run 1101: totalSupply 315 flat vs run 1031 (315) -> velocity GAGAL; watchlist-only.")
vel("Mummyhive", "Run 1101: totalSupply 600 flat vs run 1031 (600) -> velocity GAGAL; watchlist-only.")
vel("wheelz", "Run 1101: totalSupply 317 flat vs run 1031 (317) -> velocity GAGAL; watchlist-only.")
# rate fields for next run
if "KING Agent" in C:
    C["KING Agent"]["previousTotalSupply"] = 759; C["KING Agent"]["mintedInInterval"] = 33
    C["KING Agent"]["intervalMinutes"] = 30.3; C["KING Agent"]["currentRatePerMin"] = 1.089
    C["KING Agent"]["previousRatePerMin"] = 0.616; C["KING Agent"]["velocityLegPasses"] = True
    C["KING Agent"]["velocityNote"] = "Run 1101: velocity LULUS (1,089/mnt vs prev 0,616 = 1,77x, +33 token); free 23,76% <25% -> tetap EARLY."
if "MILLION" in C:
    C["MILLION"]["previousTotalSupply"] = 178; C["MILLION"]["mintedInInterval"] = 4
    C["MILLION"]["intervalMinutes"] = 30.3; C["MILLION"]["currentRatePerMin"] = 0.132
    C["MILLION"]["previousRatePerMin"] = 0.059; C["MILLION"]["velocityLegPasses"] = False
if "SEAT-f11e" in C:
    C["SEAT-f11e"]["previousTotalSupply"] = 3648; C["SEAT-f11e"]["mintedInInterval"] = 78
    C["SEAT-f11e"]["intervalMinutes"] = 30.3; C["SEAT-f11e"]["currentRatePerMin"] = 2.574
    C["SEAT-f11e"]["previousRatePerMin"] = 1.497; C["SEAT-f11e"]["velocityLegPasses"] = True
    C["SEAT-f11e"]["velocityNote"] = "Run 1101: velocity LULUS (2,574/mnt vs prev 1,497 = 1,72x, +78 token); free % UNVERIFIED -> watchlist-only, tidak bisa promosi."
# Track-C Crack update
if "Crack" in TC:
    setv(TC["Crack"], "totalSupply", 1091); setv(TC["Crack"], "totalMinted", 1091); setv(TC["Crack"], "publicRemaining", 4414)
    TC["Crack"]["runNote1101"] = "Run 1101: totalSupply/totalMinted 1059->1091 (+32), publicRemaining 4446->4414; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 — mint berikutnya BERBAYAR (0,001 BNB), TIDAK diotorisasi."
# Bianren EARLY lead (reported once run 1101)
C["Bianren"] = {
 "address": "0xd24A02198e12B35faDE9DD8334Fb7f6333CD05eF",
 "status": "early-lead-reported-2026-11-06",
 "name": "Bianren",
 "symbol": "\u5f7c\u5cb8\u4eba",
 "kind": "ERC721",
 "totalSupply": None,
 "totalMinted": 17,
 "freeMinted": 17,
 "FREE_POOL": 2000,
 "freeRemaining": 1983,
 "FREE_PER_WALLET": 10,
 "MAX_SUPPLY": 10000,
 "freePctVerified": 0.85,
 "mintOpen": True,
 "quote_user_1": 187409993595285,
 "userSlotNote": "Slot UNVERIFIED: quote(user,1)=187409993595285 wei (~0,000187 BNB, bukan 0); mintedBy/freeUsed gagal baca; balanceOf(user)=0. FREE_PER_WALLET 10, freeRemaining 1983. Bukan strong lead (free 0,85% <25%). TIDAK PERNAH auto-mint/preview sebagai early lead.",
 "firstSeenBlock": 131941489,
 "firstMintWib": "2026-11-06 11:03:45 WIB",
 "scanWindow": "131941909-131942908",
 "scanMints": 5,
 "scanMinters": 1,
 "lastReadBlock": 131945028,
 "lastReadWib": "2026-11-06 run 1101",
 "xVerified": False,
 "velocityVerified": False,
 "velocityLegPasses": False,
 "previousTotalSupply": 17,
 "launchNote": "First mint TERVERIFIKASI LENGKAP: 16 log Transfer-from-zero ditemukan == totalMinted 16 saat triase (blok earliest 131941489, 2026-11-06 11:03:45 WIB); umur ~47 mnt saat scan (<=48 jam). Pencarian mundur tanpa berhenti di chunk kosong (4 chunk, 16 log).",
 "baselineNote": "EARLY lead dilaporkan sekali run 1101. Agent-shape terverifikasi: registry=True, Sourcify verified, free funcs FREE_PER_WALLET/FREE_POOL/freeMinted/freeOf/freeRemaining + mint/mintOpen. Free 17/2000=0,85% (jauh <25% strong leg); slot user UNVERIFIED (quote bukan 0); X UNVERIFIED; velocity belum terhitung (baseline pertama run ini). Tidak pernah auto-mint/preview.",
 "gateNote": GATE_STATUS_BIANREN,
 "websiteFromTokenURI": "https://bbyr4.pages.dev",
 "supplyView": "totalMinted",
}
snap["last_run"] = "2026-11-06 run 1101"
snap["last_run_wib"] = "2026-11-06T11:01:00+07:00"
snap["runNote1101"] = "Run 1101: 1 EARLY lead baru dilaporkan sekali: Bianren (0xd24A02198e12B35faDE9DD8334Fb7f6333CD05eF) — first mint terverifikasi lengkap 2026-11-06 11:03:45 WIB (16 log == totalMinted 16), umur ~47 mnt, agent-shaped (registry+free funcs), free 17/2000=0,85% <25%, slot UNVERIFIED (quote ~0,000187 BNB), X UNVERIFIED. Bukan strong lead, bukan kandidat, TIDAK di-mint/preview. Goblin Protocol first-seen tapi bukan agent-shaped (log only). Route-4 scan SUKSES: window 131941909-131942908, 40 panggilan Ankr, 0 error, 222 NFT + 426 ERC20-mint, 2 true first-seen. Koreksi metodologi: dedupe first-seen HARUS vs seen[\"contracts\"] (lowercase) — hitungan awal 78 first-seen SALAH (memakai top-level keys); 21 kontrak triase sudah ada di seen (first_block 1-4 Nov) dan BUKAN lead baru. KING velocity LULUS (1,77x, +33) tapi free 23,76% <25% -> tetap EARLY. SEAT velocity LULUS (1,72x, +78) tapi free % unverified -> watchlist-only. 5a: 3 baru Sourcify, 0 sale shape. 5c: 42 ERC20 mint>=10, 8 baru dicek, 0 sale shape. Track B binanceai tetap refund/failed. Bridge 0 baru."
snap["runNote1101_scan"] = "Run 1101: SCAN SUKSES (pre-flight OK 5,7 dtk; head 131941978; 20 chunk selesai + shape-check). Watermark 131937878 -> 131942908. Gap 131937879-131941908 (4030 blok) belum ter-cover (backfill). 2 true first-seen: Bianren (EARLY lead, dilaporkan sekali) + Goblin Protocol (bukan agent-shaped, log only). 5c: 8 ERC20 baru dicek, 0 sale shape. Catatan: backward-search first-mint berhenti di chunk kosong pertama TIDAK bisa diandalkan untuk minter berjeda (Thundra/Dunora/Labyrinthos dsb. punya first_block seen 3 Nov meski burst terbaru hari ini); pakai seen first_block + tes boundary-48h sebagai sinyal umur, dan pencarian lengkap tanpa henti untuk first-seen sejati (Bianren: 16 log == supply)."
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
# seen file: append scan-window contracts not yet in seen["contracts"]
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = seen.setdefault("contracts", {})
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-06-1101.json"))
sc_l = {k.lower() for k in sc}
added = 0
for c in scan["contracts"]:
    a = c["address"].lower()
    if a not in sc_l:
        sc[a] = c["first_block"]; added += 1
seen["_meta"]["last_scan_wib"] = "2026-11-06 run 1101"
seen["_meta"]["last_scan_window"] = "131941909-131942908"
seen["_meta"]["last_scan_added"] = added
seen["_meta"]["last_updated_wib"] = "2026-11-06 run 1101"
seen["_meta"]["note_1101"] = "Run 1101: 2 true first-seen appended (Bianren 彼岸人 + Goblin Protocol GBLN) + top-up scan-window contracts. Bianren: agent-shaped EARLY lead, first mint 2026-11-06 11:03:45 WIB (16 log == totalMinted 16), free 17/2000=0,85%, slot unverified (quote ~0,000187 BNB). Goblin Protocol bukan agent-shaped (registry False, not_verified, tanpa free funcs)."
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
# scan state
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"] = 131942908
st["last_scan_window_from"] = 131941909
st["last_scan_window_to"] = 131942908
st["last_scan_wib"] = "run 2026-11-06-1101"
st["ankr_calls"] = 40
st["errors"] = []
st["nft_contracts"] = 222
st["erc20_mint_contracts"] = 426
st["skipped_gap"] = "131937879-131941908 (4030 blok; window dari watermark 131937878 ke head 131942908 = 5030 blok > cap 1000; scan menutup 1000 blok terbaru 131941909-131942908)"
st["note_1101_scan"] = "Run 1101: SCAN SUKSES (pre-flight OK 5,7 dtk; head 131941978). 20 chunk selesai + shape-check, 40 panggilan Ankr, 0 error. Watermark 131937878 -> 131942908. 2 true first-seen (Bianren EARLY + Goblin log-only). 5c: 8 ERC20 baru dicek, 0 sale shape. Gap 131937879-131941908 belum ter-cover (backfill)."
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("FINALIZE OK; contracts:", len(C), "track_c:", len(TC), "seen added:", added)
