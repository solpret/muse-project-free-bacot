#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-08 00:01 WIB (run 0001).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json.
No age removals (0). No promotions (BOT-UNIT velocity passes but free%
unverifiable — all free views revert; bridge-0x6eee003e is a raw-unit scale
artifact, NOT a pass). Updates HOG ORBIT / helm.ai supplies. Records
discovery/scan dispositions in run notes only (nothing new to exclude/add).
Updates King's Game + Agent Grove + HIVE. Updates last_run + run notes.
Watermark NOT advanced (backfill owns it); scan-state gets note_0001_scan only.
Snapshot + run log only. No mint/preview/claim.
"""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132237391

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-08-0001-reread.json"))
vel = json.load(open(HF + "run-2026-11-08-0001-velocity.json"))

vel_by_name = {row["name"]: row for row in vel["rows"]}
updated = 0
none_supply = 0
for name, rd in reread["reread"].items():
    c = snap["contracts"].get(name)
    if c is None:
        continue
    updated += 1
    if rd.get("totalSupply") is not None:
        c["previousTotalSupply"] = c.get("totalSupply")
        c["totalSupply"] = rd["totalSupply"]
    else:
        none_supply += 1
    for f in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if rd.get(f) is not None:
            c[f] = rd[f]
    if rd.get("balanceOf_user") is not None:
        c["balanceOf_user"] = rd["balanceOf_user"]
    if rd.get("freeClaimed_user") is not None:
        c["freeClaimed_user"] = rd["freeClaimed_user"]
    c["lastReadBlock"] = BLOCK
    c["lastReadWib"] = "2026-11-08 run 0001"
    vrow = vel_by_name.get(name)
    if vrow:
        c["mintedInInterval"] = vrow["mintedInInterval"]
        c["intervalMinutes"] = vrow["intervalMin"]
        c["currentRatePerMin"] = vrow["ratePerMin"]
        c["previousRatePerMin"] = vrow["prevRatePerMin"]
        c["velocityRatio"] = vrow["ratioVsPrev"]
        c["velocityLegPasses"] = vrow["velocityPasses"]
        if vrow.get("freePct") is not None:
            c["freePctVerified"] = vrow["freePct"]
    c["runNote0001"] = ("Run 0001 (blok %d): totalSupply %s, minted interval %s, velocity %s."
                        % (BLOCK, c.get("totalSupply"), c.get("mintedInInterval"), c.get("velocityLegPasses")))

# track_c reread (fresh values where readable; None keeps old value)
tc_updated = 0
for name, rd in reread.get("track_c", {}).items():
    t = snap.get("track_c", {}).get(name)
    if t is None:
        continue
    tc_updated += 1
    for f in ("totalSupply", "freeMinted", "freeSharesRemaining"):
        if rd.get(f) is not None:
            t[f] = rd[f]
    if rd.get("balanceOf_user") is not None:
        t["balanceOf_user"] = rd["balanceOf_user"]
    if rd.get("freeClaimed_user") is not None:
        t["freeClaimed_user"] = rd["freeClaimed_user"]
    t["lastReadBlock"] = BLOCK
    t["lastReadWib"] = "2026-11-08 run 0001"

# --- Velocity passer detail: BOT-UNIT — velocity passes, NOT promotable ---
bu = snap["contracts"].get("BOT-UNIT")
if bu is not None:
    bu["runNote0001"] = ("Run 0001 (blok 132237391 + single-call re-check run-2026-11-08-0001-passer-free.json, "
                         "blok 132239017): velocity PASSES (+259, 1531->1790, rate 8,74/mnt, ratio 65,78, first "
                         "mint 2026-11-07 02:56:47 WIB, age ~21,1 jam verified <=48h, status early-lead) TAPI "
                         "free% TIDAK BISA DIVERIFIKASI: totalSupply 1790, mintOpen 1, balanceOf(user)=0, NAMUN "
                         "SEMUA free view revert (freeMints/freeMinted/freeClaimed/FREE_SUPPLY/FREE_CAP/MAX_SUPPLY/"
                         "freeLeft/freeSupply + semua user free-slot view) — kontrak tidak mengekspos free counter "
                         "-> strong-lead leg (b) tidak bisa ditegakkan -> BUKAN strong lead, BUKAN kandidat, tetap "
                         "early-lead, tidak dilaporkan ulang.")

# --- HOG ORBIT / helm.ai: supply drift only; gate still failed, no promotion path ---
hog = snap["contracts"].get("HOG ORBIT")
if hog is not None:
    hog["runNote0001"] = ("Run 0001 (blok 132237391): totalSupply %s (was 360, +38), velocity belum terhitung "
                          "(baseline pertama, ratio None) — gate website FAILED (run 2301), tetap watchlist-only, "
                          "tanpa jalur promosi." % hog.get("totalSupply"))
helm = snap["contracts"].get("helm.ai")
if helm is not None:
    helm["runNote0001"] = ("Run 0001 (blok 132237391): totalSupply %s (was 358, +16), velocity belum terhitung "
                           "(baseline pertama, ratio None) — gate website FAILED (run 2301), tetap watchlist-only, "
                           "tanpa jalur promosi." % helm.get("totalSupply"))

# --- bridge-0x6eee003e scale artifact note ---
br = snap["contracts"].get("bridge-0x6eee003e2aebe75be551ac509eb485cc25e404fb")
if br is not None:
    br["runNote0001"] = ("Run 0001: velocity script passer (+4,53e21 raw unit, ratio 14,75) — ARTEFAK SKALA "
                         "(18 desimal, totalSupply ~1,78e24), perlakuan sama seperti 2331: raw-unit rows TIDAK "
                         "lolos. Tanpa free counter, launch unverified, status watchlist-only-scan-complement -> "
                         "BUKAN promotable.")

# --- Specials ---
kg = snap["contracts"].get("King's Game")
if kg is not None:
    kg["runNote0001"] = ("Run 0001 (blok 132239077): freeMinted 3, totalMinted 3, balanceOf(user)=0, registry_match "
                         "true — NO CHANGE vs 2331.")
grove = snap["contracts"].get("Agent Grove")
if grove is not None:
    grove["runNote0001"] = ("Run 0001 (blok 132239095): freeOpen 0, freeClaimed(user) false — NO CHANGE vs 2331.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote0001"] = ("Run 0001 (blok 132237391): totalSupply 1256, balanceOf(user)=1 — NO CHANGE vs 2331; "
                           "minted-by-user, bukan kandidat.")

snap["last_run"] = "2026-11-08 run 0001"
snap["last_run_wib"] = "2026-11-08T00:01:00+07:00"
snap["timestamp_wib"] = "2026-11-08 run 0001"
snap["runNote0001"] = (
    "Run 0001 (00:01 WIB): reread blok 132237391, 445 kontrak + 69 track_c, 677,9 dtk, 104 supply-None (degradasi "
    "RPC, nilai lama dipertahankan; 5 kontrak snapshot tanpa field address tidak bisa di-re-read: Mummyhive, "
    "LuckyBox-d08e, SnailMail, Jolly, AgentGlyph); velocity: 2 passer script — BOT-UNIT +259 ratio 65,78 umur "
    "~21,1 jam TAPI free% TIDAK BISA DIVERIFIKASI (semua free view revert di re-check blok 132239017; "
    "run-2026-11-08-0001-passer-free.json) -> TIDAK promotable; bridge-0x6eee003e artefak skala raw-unit -> "
    "TIDAK lolos. Passer 2331 NULLRAID kini gagal (+10, ratio 0,39); 0xbd4B +22 ratio 0,21; Horus AI +21 ratio 1,07; "
    "AgentVOLT +10 ratio 0,73 — semua gagal. HOG ORBIT +38 dan helm.ai +16, ratio None (rate pertama terhitung "
    "run berikutnya), gate tetap gagal. 35 sellout, set identik 2331, 0 sellout baru; age-exclusion: 0 dihapus "
    "(kept 49 grandfathered; unverified-launch 382, sama seperti 2331); HIVE/King's Game/Grove tanpa perubahan; "
    "track_c 9 drift totalSupply saja (LuckyBox-LUCK +1, Crack +8, ORBITA +9e24, QuonkersAgent/HobnorbAgent/"
    "WibblezapAgent/DribblonAgent/YammerjackAgent +1e24, PHNX +2,5e22), 0 free view terbaca (0/69), 0 sellout."
)
snap["runNote0001_scan"] = (
    "Run 0001 scan: pre-flight PASS (head 132237334, small ankr_getLogs 50 blok OK 401 logs, 4,5 dtk). Scan "
    "SUKSES percobaan pertama, 0 error: window 132236361-132237360 (1000 blok terbaru), 125 NFT (120 ERC721 + 5 "
    "ERC1155, 1105 mint), 348 ERC-20 mint, 40 panggilan Ankr, ~15 mnt; effective coverage PENUH (max first_block "
    "NFT 132237340, ERC-20 132237357) — TIDAK ada lubang di window ini. HIVE tidak ada di window. Triage: 1 "
    "first-seen — TCG-VAULT Founder (TCGVF) 0xA791B93157fD62b68fAcd7a4785F27F2E8C53Bb3, 1 mint/1 minter, first mint "
    "00:02:02 WIB — NOT agent-shaped (no registry bytes, no free shape, Sourcify IncompleteRead) -> 0 EARLY lead. "
    "Seen file +145 (total nested 12.075). 5c: 4 ERC-20 baru dicek (mint_count>=10), 0 sale-shape; "
    "track-c-scan-checked.json 2.781. WATERMARK TIDAK DIMAJUKAN run ini (milik backfill); standing gap "
    "132229264-132236360 (kecuali window 2331 yang sudah ter-cover 132232440-132233439) tetap milik backfill. "
    "Sourcify flaky saat enrichment (banyak IncompleteRead/RemoteDisconnected) tapi semua kontrak tetap dapat verdict."
)
snap["runNote0001_discovery"] = (
    "Run 0001 discovery: Boltbook boltbook.fun EN 45.216 B / ZH 45.231 B (HTTP 200; bare EN URL 302 ke /?lang=en), "
    "6 alamat, EN=ZH identik, IDENTIK dengan set hot-leg 2359 — 0 alamat baru; 0 free-share keyword hit. Klasifikasi: "
    "BOLT + AgentBook di snapshot; Brinedroid 0xa0694012... di snapshot watchlist-only-same-owner-discarded (post baru: "
    "1.109/2.222, freeClaimed 1.104, pace +3,2/mnt — tanpa perubahan tier); FREEDROP 0x92937562... excluded "
    "same-owner-discarded (post baru: 292->348/500 dalam 31 mnt, author mint #355 — pergerakan hitungan saja, TIDAK "
    "PERNAH promotable); FU 0xed33074b... TIDAK di snapshot tapi sudah dispositioned (run 2001 triage lead:false, NOT "
    "agent-shaped; hot-leg 1954 checked-not-sale-shape) meski ada post baru (299 minted, 734 free left) — dicatat saja, "
    "TIDAK ditambahkan ke snapshot, TIDAK dipromosikan; 0x8269ea16... footer BoltRewards. MINTS index identik 2331 "
    "(57 proyek, 0 entri baru). Sourcify 5a: 20 kontrak (11 baru vs 2331), 0 S1/S2/0 agent-mint (near-miss sama "
    "0x56155fd1...). Square/Odaily/PANews: hanya item lama (Paw Gang, Ptah, MINTS), 0 site link baru. DappBay tidak "
    "diperlukan. Bridge TIDAK berubah (sha256 b3f349f1..., 115 kontrak, 7 same_owner_discarded, 0 promosi). "
    "AccordTrace (Ed25519 passports, bukan .ai Agent ID) dan agentideth.com $AGI (Ethereum L1, bukan BSC) dicek dan "
    "di luar scope."
)
snap["runNote0001_binanceai"] = (
    "Run 0001 track-B binanceai re-check (blok 132239151): launched()=0, failed()=1, isRefundPhase()=1, "
    "totalShares()=3110, tokenClaimed(user)=0, balance=0, pair reserves 0/0 — IDENTIK run 1701-2331; sudah "
    "dilaporkan sekali, tidak dilaporkan ulang. Tidak ada preview/klaim."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "| track_c:", len(snap.get("track_c", {})),
      "| excluded:", len(snap.get("excluded", {})))
print("updated:", updated, "| none_supply:", none_supply, "| tc_updated:", tc_updated)
print("removed (age-excluded): none")

# --- Scan state: note only, watermark NOT advanced ---
st = json.load(open(HF + "onchain-scan-state.json"))
st["note_0001_scan"] = (
    "Run 0001 scan (00:01 WIB): pre-flight PASS (head 132237334, 401 logs/50 blok, 4,5 dtk). Window "
    "132236361-132237360 (1000 blok terbaru), 125 NFT (120 ERC721 + 5 ERC1155, 1105 mint), 348 ERC-20 mint, 40 "
    "Ankr calls, ~15 mnt, 0 error, effective coverage PENUH (max first_block NFT 132237340). Triage 1 "
    "first-seen (TCG-VAULT Founder 0xA791B931..., NOT agent-shaped), 0 EARLY lead. Seen +145 (12.075). 5c: 4 baru "
    "dicek, 0 hit (checked 2.781). WATERMARK TIDAK DIMAJUKAN run ini (milik backfill); standing gap "
    "132229264-132236360 milik backfill."
)
json.dump(st, open(HF + "onchain-scan-state.json", "w"), indent=1)
print("state note_0001_scan written; last_scanned_block still:", st.get("last_scanned_block"))
