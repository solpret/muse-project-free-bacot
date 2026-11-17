"""Finalize run 2026-11-07-0901 (Free Bacot).

NOTE: an earlier draft of this file on disk (written 09:06 WIB, pre-compaction)
carried STALE 0831-era values (block 132113850, Pea Pod 450, '9 velocity passes',
Pulsekeep/Tensortug deletions, no AgentGoats/DragonEgg/ONI updates) and was NEVER
executed (snapshot last_run still 0831). This version replaces it with the
verified 0901 findings. Do not re-run the stale draft.

Actions:
1. Backup snapshot + track-c-scan-checked.json.
2. Load snapshot FRESH (backfill added ONI-d576 + Agent Panda-2820 after 0831).
3. Bulk reread apply (458 contracts + 57 track_c, block 132119643).
4. Velocity pass -> AgentVOLT entry.
5. AgentGoats: fresh values + status strong-lead-gate-blocked-2026-11-07
   (gate (A)-(N) ALL failed; browser follow-up 09:43-09:49 WIB: (B) 11 Boltbook
   posts, zero project links; (N) 3 author profiles, no X/site; (L) BscScan
   Info tab empty). NO preview/mint attempted.
6. DragonEgg: pop from contracts -> excluded-danger (silent setApprovalForAll
   to 0xaa1d... on free mint, verified 2x on-chain).
7. Lumenhold + ENCRYPTED: excluded-age-over-48h (first-read exclusion, NOT reported).
8. ONI-74bD registry exact fix; ONI-d576 fresh 140/140; PeaFunPod 476/4524;
   AgentVOLT deep-dive values.
9. 5c: add missing 0x8CfC36f2 (list + record) and record for 0x49Dc58d7
   (already in list). 4 others already recorded by backfill - untouched.
10. Run note + last_run.
"""
import json, shutil, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-run-0901")
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-run-0901")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-07-0901-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-0901-velocity.json"))
gd = json.load(open(f"{BASE}/run-2026-11-07-0901-goats-dragonegg.json"))
op = json.load(open(f"{BASE}/run-2026-11-07-0901-oni-peapod.json"))
BLOCK = reread["block"]  # 132119643

# 1. bulk reread apply (non-None overwrites only)
n_upd = 0
for k, v in reread["reread"].items():
    if k not in snap["contracts"] or not isinstance(v, dict):
        continue
    e = snap["contracts"][k]
    for f in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if v.get(f) is not None:
            e[f] = v[f]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-07 run 0901"
    n_upd += 1
n_tc = 0
for k, v in reread["track_c"].items():
    if k not in snap.get("track_c", {}) or not isinstance(v, dict):
        continue
    e = snap["track_c"][k]
    for f in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if v.get(f) is not None:
            e[f] = v[f]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-07 run 0901"
    n_tc += 1

# 2. velocity pass -> AgentVOLT
velmap = {p["address"].lower(): p for p in vel["passes"]}
for k, e in snap["contracts"].items():
    a = (e.get("address") or "").lower()
    if a in velmap:
        p = velmap[a]
        e["ratePerMin"] = p["ratePerMin"]
        e["prevRatePerMin"] = p["prevRatePerMin"]
        e["ratioVsPrev"] = p["ratioVsPrev"]
        e["mintedInInterval"] = p["mintedInInterval"]
        e["velocityNote"] = (f"run 0901: +{p['mintedInInterval']} in {p['intervalMin']:.1f} min, "
                             f"rate {p['ratePerMin']:.4f}/min, ratio {p['ratioVsPrev']:.2f} vs prev")

# 3. AgentVOLT deep-dive fresh values (totalSupply 2834 > reread 2812; later read)
av = snap["contracts"].get("AgentVOLT (round 1)")
if av:
    av["totalSupply"] = 2834
    av["MAX_SUPPLY"] = 10000
    av["MAX_PER_WALLET"] = 10
    av["hasFreeMinted_user"] = 0
    av["mintedPerWallet_user"] = 0
    av["balanceOf_user"] = 0
    av["velocityNote"] = ("run 0901: velocity LULUS (+239, 5.5009/min, ratio 10.28) TAPI free% "
                          "TETAP UNVERIFIED (tidak ada free counter; free vs paid tidak bisa "
                          "dibedakan dari totalSupply) + umur UNVERIFIED + X unverified + "
                          "website null (MINTS) -> tetap watchlist-only, bukan strong lead/kandidat. "
                          "Tidak di-preview/mint.")

# 4. AgentGoats -> strong-lead-gate-blocked (fresh values block 132122126)
g = snap["contracts"].get("Agent Goats")
if g:
    gv = gd["AgentGoats"]
    g["totalSupply"] = gv["totalSupply()"]
    g["freeClaimed"] = gv["freeClaimed()"]
    g["FREE_SUPPLY"] = gv["FREE_SUPPLY()"]
    g["MAX_SUPPLY"] = gv["MAX_SUPPLY()"]
    g["MAX_PER_WALLET"] = gv["MAX_PER_WALLET()"]
    g["mintOpen"] = gv["mintOpen()"]
    g["balanceOf_user"] = 0
    g["mintedBy_user"] = gv["mintedBy(address)"]
    g["price_paid_bnb"] = 0.0002
    g["owner"] = "0x23F5CDd233925eA83369A495b95f825eD710fBaa"
    g["AGENT_ID_registry_exact"] = True
    g["firstMintBlock"] = 131764404
    g["firstMintWib"] = "2026-11-05 12:55:17 WIB"
    g["firstMintTx"] = "0xaa695698d59ee375dd822b3d940e3ba25932cf789e8f802780d873ce01a1f92e"
    g["ageDeadlineWib"] = "2026-11-07 12:55:17 WIB"
    g["status"] = "strong-lead-gate-blocked-2026-11-07"
    g["gateStatus"] = "FAILED"
    g["gateNote"] = (
        "STRONG LEAD 3 kaki terverifikasi (umur <=48h, free 514/1111 = 46,26%, slot user terbuka) "
        "TAPI GATE WEBSITE GAGAL TOTAL metode (A)-(N), TIDAK di-preview/di-mint. "
        "(A) alamat mentah nihil; (G) nama proyek nihil; (H) contractURI base64 tanpa external_link; "
        "(I) tokenURI(1) tanpa external_url; (J) ABI tanpa fungsi situs; (C) metadata Sourcify 0 URL; "
        "(K) GitHub nihil (search-index saja, bukan bukti tidak ada repo); (M) site: filters nihil; "
        "(E) single owner, tanpa pola factory-wave; "
        "(B) browser 09:43-09:49 WIB: 11 posting Boltbook AgentGoats dibaca satu per satu, TIDAK ADA "
        "satu pun tautan situs proyek/X/dokumentasi (kontrak hanya teks biasa); "
        "(N) browser: 3 profil penulis (modemeta.ai, nineteen9seven.ai, airaatz.ai) TANPA handle X "
        "dan TANPA tautan situs di bio; "
        "(L) browser: halaman token BscScan dibaca, tab Info KOSONG (tanpa website/sosial); catatan: "
        "percobaan awal sempat kena looping Cloudflare challenge sebelum environment diganti dan "
        "halaman akhirnya terbaca. Dilaporkan sekali sebagai strong lead gate-blocked run 0901.")
    g["lastReadBlock"] = gd["block"]
    g["lastReadWib"] = "2026-11-07 run 0901"

# 5. DragonEgg -> excluded-danger (pop from contracts, record in excluded)
ex = snap.setdefault("excluded", {})
dk = "0xb0cc430fa9EfD6dfb8605dF570F9ACc449c8F7F1"
dv = gd["DragonEgg"]
if dk in snap["contracts"]:
    snap["contracts"].pop(dk)
ex["DragonEgg"] = {
    "address": dk,
    "track": "A",
    "status": "excluded-danger-2026-11-07",
    "note": (
        "BAHAYA - JANGAN DI-SENTUH: free mint diam-diam memberi setApprovalForAll ke operator "
        "0xaa1d9dc61e9ca3fab984de87f7ad4e2b9f6d6978 atas SELURUH koleksi DragonEgg minter. "
        "Bukti (1) mint pertama tx 0x8d3f9852617d7c5b9f5ddb3d905821323fe4673ab5fc463111eada6136d3f7ba "
        "(blok 132116386, status 1) memancarkan ApprovalForAll owner "
        "0xb8891f60f0421bfae430cf8c2b6a00efaeea745b -> operator -> approved=TRUE; "
        "(2) revoke tx 0x51d986cb42b481b1a391206e57909d45aa9eb5da76870701dd330aa09abbfd48 "
        "(blok 132116592, status 1) memancarkan ApprovalForAll owner "
        "0x049b01c4ebe0463080a98ffc0f8c4e46fbcee3e1 -> operator -> approved=FALSE. "
        "State segar run 0901: totalMinted 110, freeMinted 110, FREE_CAP 111 (1 gratis tersisa), "
        "MAX_SUPPLY 333, launchTime 2026-11-07 07:14:57 WIB, first mint 08:56:05 WIB, "
        "agentIdRegistry() persis, mintOpen 1, freeUsed(user)=0, balanceOf(user)=0. "
        "Ditemukan via Boltbook front page run 0901; TIDAK PERNAH di-preview/di-mint; "
        "dilaporkan sekali sebagai peringatan bahaya run 0901."),
}

# 6. Lumenhold + ENCRYPTED -> excluded-age-over-48h (first-read exclusion, NOT reported)
ex["Lumenhold"] = {
    "address": "0x9701980b0afd825134390ee46fb3bd675a2f356f",
    "track": "A",
    "status": "excluded-age-over-48h-2026-11-07",
    "note": ("Age-excluded run 0901 via first-seen lower bound: first-seen blok 131559780 "
             "(~69,9 jam), 635/2143, free 631/1500, belum sold out. First-read exclusion "
             "(preseden Hourglas) - TIDAK dilaporkan."),
}
ex["ENCRYPTED"] = {
    "address": "0xef565b1c95ed99a86965e85d7b5356efaa0c359c",
    "track": "A",
    "status": "excluded-age-over-48h-2026-11-07",
    "note": ("Age-excluded run 0901 via first-seen lower bound: first-seen blok 131656382 "
             "(~57,9 jam), 649/8888, belum sold out. First-read exclusion (preseden Hourglas) - "
             "TIDAK dilaporkan."),
}

# 7. ONI-74bD: registry now reads exact (fix stale 'revert' note)
o74 = snap["contracts"].get("ONI-74bD")
if o74:
    o74v = op["ONI-74bD"]
    o74["mintOpensAt"] = o74v["mintOpensAt"]
    o74["totalMinted"] = o74v["totalMinted"]
    o74["freeMinted"] = o74v["freeMinted"]
    o74["FREE_POOL"] = o74v["FREE_POOL"]
    o74["MAX_SUPPLY"] = o74v["MAX_SUPPLY"]
    o74["poolSeeded"] = o74v["poolSeeded"]
    o74["registryExact"] = True
    o74["token"] = "0xc12E2d8d4476C99Fd5Ae4700C87746A996C991a2"
    o74["pair"] = 0
    o74["baselineNote"] = ("Feed Sourcify run 0901 + baca segar run 0901: ABI 63 fns incl mintFree/mintPaid/"
                           "claim/rarityOf/registry; totalMinted 0, freeMinted 0, poolSeeded 0, pair 0 -> "
                           "BELUM launching (0 mint). registry() kini TERBACA = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F "
                           "PERSIS (run 0831 masih revert). Mint buka 2026-11-07 12:00 WIB.")
    o74["lastReadBlock"] = op["block"]
    o74["lastReadWib"] = "2026-11-07 run 0901"

# 8. ONI-d576: fresh values from retry (reread batch returned all-None)
od = snap["contracts"].get("ONI-d576")
if od:
    odr = op["ONI-d576-retry"]
    od["totalMinted"] = odr["totalMinted()"]
    od["freeMinted"] = odr["freeMinted()"]
    od["MAX_SUPPLY"] = odr["MAX_SUPPLY()"]
    od["poolSeeded"] = odr["poolSeeded()"]
    od["registryExact"] = True
    od["token"] = "0xe3a376d0985ef9b7d13e69de1a9179146e34fbef"
    od["owner"] = "0xe9a232aefaa230a38bc9fec961eea19134903308"
    od["mintOpensAt"] = odr["mintOpensAt()"]
    od["balanceOf_user"] = odr["balanceOf(user)"]
    od["freeClaimed_user"] = None  # read FAILED run ini (OSError; backfill juga gagal) -> UNVERIFIED
    od["velocityNote"] = ("run 0901: totalMinted 37 (triase backfill ~09:08) -> 140 (~09:25), "
                          "freeMinted 140 = semua mint gratis, FREE_POOL 1000 -> free 14,0% <25% "
                          "-> BUKAN strong lead. Early lead MILIK JOB BACKFILL (triase "
                          "132114146-132116365) - run ini TIDAK melaporkannya ulang; update nilai "
                          "segar saja. freeClaimed(user) GAGAL baca (OSError) -> slot user UNVERIFIED.")
    od["lastReadBlock"] = op["block"]
    od["lastReadWib"] = "2026-11-07 run 0901"

# 9. Pea Fun Pod: fresh 476/4524 (was stale 450/4561)
pp = snap["contracts"].get("PeaFunPod-1901")
if pp:
    ppv = op["PeaFunPod"]
    pp["freePodsClaimed"] = ppv["freePodsClaimed"]
    pp["freePodsRemaining"] = ppv["freePodsRemaining"]
    pp["FREE_PODS_TOTAL"] = ppv["FREE_PODS_TOTAL"]
    pp["totalPodsMinted"] = ppv["totalPodsMinted"]
    pp["freeWindowOpen"] = ppv["freeWindowOpen"]
    pp["freeClaimedBy_user"] = ppv["freeClaimedBy_user"]
    pp["gateStartWib"] = "2026-11-06 18:55 WIB"
    pp["freeWindowClosesAtWib"] = "2026-11-07 18:55 WIB"
    pp["registryExact"] = True
    pp["velocityNote"] = ("run 0901: free 476/5000 = 9,52% <25% -> BUKAN strong lead; "
                          "gateStart 2026-11-06 18:55 WIB; slot user terbuka (freeClaimedBy=0); "
                          "window tutup 2026-11-07 18:55 WIB. Tetap early lead.")
    pp["lastReadBlock"] = op["block"]
    pp["lastReadWib"] = "2026-11-07 run 0901"

# 10. 5c: complete the 6 addresses from run-0901 5c check.
# 4 already have backfill per-address records (NOT overwritten); note the Sourcify
# discrepancy: run-0901 5c read them as not_verified, backfill records say verified.
# Sale-shape verdict is identical either way (S1=False S2=False).
tc = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_lower = {a.lower() for a in tc.get("checked", [])}
added_list = []
added_rec = []
for addr in ("0x49Dc58d7AfEFa8b7CBF7e6E9C2f97f8b689EF2Bb",
             "0x8CfC36f2a7265fCf14c97a9ba8aC60FcC642Fc0b"):
    if addr.lower() not in checked_lower:
        tc.setdefault("checked", []).append(addr)
        added_list.append(addr)
    if addr not in tc:
        tc[addr] = {"source": "run-2026-11-07-0901-5c", "status": "checked-not-sale-shape",
                    "note": ("Sourcify not_verified per run-0901 5c read (window 132118743-132119742); "
                             "S1=False S2=False, no sale shape")}
        added_rec.append(addr)
json.dump(tc, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# 11. run note
snap["runNote0901_1107"] = (
    "Run 0901: 0 kandidat, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat, "
    "0 pending claim baru/dibuka. Preflight PASS 4,6 dtk (head 132117848). Reread 458 kontrak + "
    "57 track_c, blok 132119643. Scan SUKSES window 132118743-132119742 (1000 blok, cap), 20/20 "
    "chunks + 138/138 enrich, 40 Ankr calls, 0 error, 138 NFT + 327 ERC-20 mint; 0 first-seen "
    "sejati (53 known-snapshot, 84 known-seen, 1 registry). Velocity 1 pass (AgentVOLT +239, "
    "5.5009/min, ratio 10,28) tapi free% UNVERIFIED -> watchlist-only. Sold out 34 (set 0831 + "
    "Tampesta-6aA5 2222/2222). Age: Agentyyds + Glitchdroid sold out 600/600 -> skip; 0 deletions. "
    "BINANCEAI tetap refund/failed (launched 0, failed 1, isRefundPhase 1); Grove freeOpen 0. "
    "Sourcify feed 20 baru, 0 hit S1/S2; 1 agent-mint = ONI-d576 (sudah ditriase backfill). "
    "5c: 6 dicek, 0 sale-shape (4 sudah tercatat backfill; 2 dilengkapi run ini). "
    "DRAGONEGG BAHAYA -> excluded-danger (setApprovalForAll diam-diam ke 0xaa1d..., bukti 2 tx). "
    "AGENT GOATS promosi early -> strong lead (umur <=48h, free 514/1111 = 46,26%, slot terbuka) "
    "TAPI GATE WEBSITE GAGAL TOTAL (A)-(N) incl. browser (B)/(N)/(L) 09:43-09:49 WIB -> TIDAK "
    "di-preview/di-mint; status strong-lead-gate-blocked-2026-11-07; deadline umur 2026-11-07 "
    "12:55:17 WIB. Lumenhold + ENCRYPTED age-excluded via first-seen (>48h, first-read, TIDAK "
    "dilaporkan). ONI-d576 140/140 (14,0%, backfill-owned, tidak dilaporkan ulang); ONI-74bD "
    "upcoming, mint buka 12:00 WIB, registry kini exact; Pea Fun Pod 476/5000 (9,52%). "
    "Watermark TIDAK dimajukan run ini (backfill owns it; last_scanned_block 132122532 saat finalize). "
    "0 preview/mint/claim. Catatan: draft finalize 09:06 WIB di disk ternyata stale (nilai era 0831) "
    "dan TIDAK PERNAH dieksekusi - diganti versi ini.")
snap["last_run_wib"] = "2026-11-07 09:01 WIB"
snap["timestamp_wib"] = "2026-11-07 09:01 WIB"
snap["last_run"] = "2026-11-07-0901"

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"contracts updated: {n_upd}, track_c updated: {n_tc}")
print("contracts now:", len(snap["contracts"]), "track_c:", len(snap.get("track_c", {})))
print("5c list added:", added_list, "records added:", added_rec)
print("excluded now has DragonEgg:", "DragonEgg" in snap.get("excluded", {}),
      "Lumenhold:", "Lumenhold" in snap.get("excluded", {}),
      "ENCRYPTED:", "ENCRYPTED" in snap.get("excluded", {}))
print("Agent Panda-2820 still present:", "Agent Panda-2820" in snap["contracts"])
print("Agent Goats status:", snap["contracts"].get("Agent Goats", {}).get("status"))
