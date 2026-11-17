#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-08 00:31 WIB (run 0031).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json.
No age removals (0). No promotions (MORPHA velocity passes but free%
unverifiable — all free views revert, age unverified, Sourcify unverified,
proxy ERC-1967). HOG ORBIT strong-lead direct mint EXECUTED by parent this
run (tx 0x28f650d7..., block 132245054, token #421, verified on-chain).
Records discovery/scan dispositions in run notes only (nothing new to
exclude/add). Updates King's Game + Agent Grove + HIVE + binanceai.
Updates last_run + run notes. Watermark NOT advanced (backfill owns it);
scan-state gets note_0031_scan only.
"""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132243569  # velocity fallback block; reread eth_blockNumber race failed (None)

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-08-0031-reread.json"))
vel = json.load(open(HF + "run-2026-11-08-0031-velocity.json"))

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
    c["lastReadWib"] = "2026-11-08 run 0031"
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
    c["runNote0031"] = ("Run 0031 (blok %d): totalSupply %s, minted interval %s, velocity %s."
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
    t["lastReadWib"] = "2026-11-08 run 0031"

# --- Velocity passer detail: MORPHA — velocity passes, NOT promotable ---
mo = snap["contracts"].get("MORPHA")
if mo is not None:
    mo["runNote0031"] = ("Run 0031 (blok 132243569 + single-call re-check run-2026-11-08-0031-passer-free.json): "
                         "velocity PASSES (+25, 1337->1362, ratio 1,6, re-check totalSupply 1365, mintOpen 1, "
                         "balanceOf(user)=0) TAPI free% TIDAK BISA DIVERIFIKASI: SEMUA free view revert, launch age "
                         "unverified, Sourcify unverified, proxy ERC-1967 -> strong-lead leg (b) tidak bisa "
                         "ditegakkan -> BUKAN strong lead, BUKAN kandidat, tetap early-lead, tidak dilaporkan ulang. "
                         "Near-miss: 0xbd4B +51 ratio 1,48; BOT-UNIT collapsed (+2).")

# --- HOG ORBIT: strong-lead direct mint EXECUTED by parent this run ---
hog = snap["contracts"].get("HOG ORBIT")
if hog is not None:
    hog["status"] = "minted-by-user-2026-11-08"
    hog["totalSupply"] = 421
    hog["freeLeft"] = 1083
    hog["freePctVerified"] = 27.73
    hog["balanceOf_user"] = 1
    hog["mintedBy_user"] = 1
    hog["mintTx"] = "0x28f650d774144ce817d672a8fc377935e0f7d602b4134dd1b0669cc5e0d59b38"
    hog["mintBlock"] = 132245054
    hog["mintGas"] = 111214
    hog["mintTokenId"] = 421
    hog["websiteGate"] = "VERIFIED 2026-11-08 run 0031: https://hog-orbit.pages.dev prints exact contract (footer + JS config); tokenURI external_url same site"
    hog["auditNote"] = "Binance audit run 0031: hasResult=false disclosed as NO RESULT, never a pass; no risk hit"
    hog["marketplaceNote"] = "No live venue: site is mint-only, Boltbook post 'no secondary market yet', no contract-matched Element collection -> NOT listed (auto-list rule: no own market live / floor live)"
    hog["rarityNote"] = "Tier not verified (no Rarity/Tier trait). Traits: Background Deep Space, Skin Spotted, Suit Cosmo Blue, Helmet None, Gear Antenna, Eyes X X, Mouth Smile, Hat None. Appended to nft-rarity-inventory.md."
    hog["runNote0031"] = ("Run 0031: STRONG LEAD confirmed + DIRECT MINT EXECUTED by parent. Legs: first mint "
                          "2026-11-07 19:10:57 WIB (age ~5h40m <=48h), free 416/1500 = 27,7% (>=25%), slot open "
                          "(freeOf=1, costOf=0, mintedBy=0), website gate VERIFIED (hog-orbit.pages.dev, tokenURI "
                          "method I), audit hasResult=false (no result). Fresh exec guard blok 132245009: "
                          "totalSupply 420, freeLeft 1084, costOf(user,1)=0. Preview bersih 000000000 (+1 ERC721 "
                          "#421, tanpa authority/allowance/risk). Tx 0x28f650d7..., blok 132245054, receipt 1, gas "
                          "111214 (~0,0000071 BNB); ownerOf(421)=wallet agent, freeLeft 1084->1083, balanceOf 0->1.")

# --- Specials ---
kg = snap["contracts"].get("King's Game")
if kg is not None:
    kg["runNote0031"] = ("Run 0031 (blok 132243804): freeMinted 3, totalMinted 3, balanceOf(user)=0, registry_match "
                         "true — NO CHANGE vs 0001.")
grove = snap["contracts"].get("Agent Grove")
if grove is not None:
    grove["runNote0031"] = ("Run 0031 (blok 132243824): freeOpen 0, freeClaimed(user) false — NO CHANGE vs 0001.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote0031"] = ("Run 0031 (single-call retry blok 132244210): totalSupply 1256, balanceOf(user)=1 — "
                           "NO CHANGE vs 0001; minted-by-user, bukan kandidat.")

snap["last_run"] = "2026-11-08 run 0031"
snap["last_run_wib"] = "2026-11-08T00:31:00+07:00"
snap["timestamp_wib"] = "2026-11-08 run 0031"
snap["runNote0031"] = (
    "Run 0031 (00:31 WIB): reread blok 132243569 (reread eth_blockNumber race gagal, fallback velocity), "
    "445 kontrak + 69 track_c, 968,5 dtk, 114 supply-None (degradasi RPC, nilai lama dipertahankan). "
    "Velocity: 1 passer script — MORPHA +25 ratio 1,6 TAPI free% TIDAK BISA DIVERIFIKASI (semua free view revert "
    "di re-check, age unverified, Sourcify unverified, proxy ERC-1967) -> TIDAK promotable. Near-miss 0xbd4B +51 "
    "ratio 1,48; BOT-UNIT collapsed (+2); bridge-0x6eee003e supply turun (artefak skala). 35 sellout, set identik "
    "0001, 0 sellout baru; age-exclusion: 0 dihapus (kept 49 grandfathered; unverified-launch 382, sama seperti "
    "0001); HIVE/King's Game/Grove tanpa perubahan; track_c 11 drift totalSupply (Crack +9, ORBITA +1,1e25, "
    "PLNK/QuonkersAgent +3e24, Mizzlewick/Hobnorb/Wibblezap/Dribblon/Yammerjack +1e24, Draco +2,5e22, PHNX +5e22), "
    "0 free view terbaca (0/69), 0 sellout. HOG ORBIT: strong lead confirmed + DIRECT MINT sukses (lihat "
    "runNote0031 HOG ORBIT; tx 0x28f650d7..., blok 132245054, token #421)."
)
snap["runNote0031_scan"] = (
    "Run 0031 scan: pre-flight PASS (head 132241305, small ankr_getLogs 50 blok OK 241 logs, 28,1 dtk). "
    "Percobaan 1 GAGAL di eth_blockNumber (timeout semua endpoint, tanpa panggilan Ankr); retry SUKSES. Window "
    "132240684-132241683 (1000 blok terbaru), 134 NFT (132 ERC721 + 2 ERC1155), 345 ERC-20 mint, 40 panggilan "
    "Ankr, 0 error, ~24 mnt, effective coverage PENUH (max first_block NFT 132241682). HIVE tidak ada di window. "
    "Triage: 2 first-seen — LifePass 0x41D45A7C... (200 mints, first mint 00:28:50 WIB) dan NetGain Membership "
    "0x85443fF1... (1 mint, 00:33:52 WIB), keduanya NOT agent-shaped (no registry bytes, no free shape, Sourcify "
    "not_verified/IncompleteRead) -> 0 EARLY lead. Seen +134 (12.211). 5c: 4 ERC-20 baru dicek (mint_count>=10), "
    "0 sale-shape; track-c-scan-checked.json 2.785. WATERMARK TIDAK DIMAJUKAN run ini (milik backfill; backfill "
    "memajukan ke 132238015 selama run); standing gap 132237361-132240683 milik backfill."
)
snap["runNote0031_discovery"] = (
    "Run 0031 discovery: Boltbook boltbook.fun EN 46.207 B / ZH 46.409 B (HTTP 200), 18 alamat mentah, EN=ZH "
    "identik, 0 free-share keyword hit. Klasifikasi: BOLT/Horus/Thetavox/Kappaxis/Pea Fun Pod/Digital Bomb sale "
    "di snapshot; FREEDROP excluded same-owner-discarded (391/500, ~93/jam — pergerakan hitungan saja); Nero "
    "Agent excluded age-over-48h (9.900/10.000); Nova Agent + Omens sudah checked-not-sale-shape (hot leg); "
    "BoltRewards footer + FDROP CREATE2 factory + deployer/EOA = infrastruktur. BARU dicatat (bukan ditambah ke "
    "snapshot, TIDAK promotable dari kaki ini): Tera Card 0x1dBc45CF... (175/15.000, pace nyaris nol, shape-check "
    "gagal/ABI unfetchable) dan Mira Agent 0x2a2a3f5d... (4.900/5.000, 100 free left, shape-check gagal sejak "
    "2026-11-07 20:44 WIB, Sourcify ABI 404). Horus 1.976/2.000 (24 tersisa, tutup ~01:10 WIB); Pea Fun Pod free "
    "window tutup 18:55 WIB 7 Nov; Digital Bomb free 800 habis (quote kini 0,002 BNB). MINTS index 57->58 (ONI "
    "0xd576F638... sudah di snapshot sebagai ONI-d576 early-lead — index menyusul, bukan baru). Sourcify 5a: 20 "
    "kontrak (semua baru vs 0001), 0 S1/S2/0 agent-mint. Square/Odaily/PANews: hanya item lama, 0 site link baru. "
    "DappBay: tanpa listing Tera/Omens/Nova/Mira/HOPKIN, tanpa website evidence. Bridge TIDAK berubah (sha256 "
    "b3f349f1..., 115 kontrak, 7 same_owner_discarded, 0 promosi)."
)
snap["runNote0031_binanceai"] = (
    "Run 0031 track-B binanceai re-check (blok 132243697): launched()=0, failed()=1, isRefundPhase()=1, "
    "totalShares()=3110, tokenClaimed(user)=0, balance=0, pair reserves 0/0 — IDENTIK 0001; masih pending "
    "(refund phase), bukan kegagalan. Tidak ada preview/klaim."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "| track_c:", len(snap.get("track_c", {})),
      "| excluded:", len(snap.get("excluded", {})))
print("updated:", updated, "| none_supply:", none_supply, "| tc_updated:", tc_updated)
print("removed (age-excluded): none")

# --- Scan state: note only, watermark NOT advanced ---
st = json.load(open(HF + "onchain-scan-state.json"))
st["note_0031_scan"] = (
    "Run 0031 scan (00:31 WIB): pre-flight PASS (head 132241305, 241 logs/50 blok, 28,1 dtk). Percobaan 1 "
    "GAGAL di eth_blockNumber (timeout semua endpoint, tanpa panggilan Ankr); retry SUKSES. Window "
    "132240684-132241683 (1000 blok terbaru), 134 NFT (132 ERC721 + 2 ERC1155), 345 ERC-20 mint, 40 Ankr calls, "
    "0 error, ~24 mnt, effective coverage PENUH (max first_block NFT 132241682). Triage 2 first-seen (LifePass "
    "0x41D45A7C..., NetGain 0x85443fF1...), keduanya NOT agent-shaped, 0 EARLY lead. Seen +134 (12.211). 5c: 4 "
    "baru dicek, 0 hit (checked 2.785). WATERMARK TIDAK DIMAJUKAN run ini (milik backfill; backfill memajukan ke "
    "132238015 selama run); standing gap 132237361-132240683 milik backfill."
)
json.dump(st, open(HF + "onchain-scan-state.json", "w"), indent=1)
print("state note_0031_scan written; last_scanned_block still:", st.get("last_scanned_block"))
