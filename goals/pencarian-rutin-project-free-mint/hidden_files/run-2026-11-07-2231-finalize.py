#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-07 22:31 WIB (run 2231).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json.
No age removals (0 candidates). Marks Tri333 minted-by-user (hot-leg mint
22:46 WIB, tx 0x5b70a6787d41f1e4bd69de033fd54dc5c1950100c343136a6506db715e4d0dc5).
Records discovery/scan dispositions as excluded (age / sold-out / pool-exhausted /
same-owner-discarded / no-website-no-AgentID). Updates King's Game + Agent Grove + HIVE.
Updates last_run + run notes. Watermark NOT advanced (backfill owns it).
Snapshot + run log only. No mint/preview/claim."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132225884

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-07-2231-reread.json"))
vel = json.load(open(HF + "run-2026-11-07-2231-velocity.json"))

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
    c["lastReadWib"] = "2026-11-07 run 2231"
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
    c["runNote2231"] = ("Run 2231 (blok %d): totalSupply %s, minted interval %s, velocity %s."
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
    t["lastReadWib"] = "2026-11-07 run 2231"

# --- Tri333 minted by hot-leg run 22:46 WIB (after this leg's reread block;
# this run's Tri333 supply read returned None, so values come from the mint verification) ---
tri = snap["contracts"].get("Tri333")
if tri is not None:
    tri["status"] = "minted-by-user-2026-11-07"
    tri["balanceOf_user"] = 1
    tri["freeCount_user"] = 1
    tri["freeMinted"] = 592
    tri["totalMinted"] = 592
    tri["mintedTokenId"] = 590
    tri["mintTx"] = "0x5b70a6787d41f1e4bd69de033fd54dc5c1950100c343136a6506db715e4d0dc5"
    tri["mintBlock"] = 132227104
    tri["runNote2231"] = ("Run 2231: Tri333 #590 MINTED by hot-leg run 22:46 WIB (tx 0x5b70a678..., blok 132227104, "
                          "receipt 1, gas 113.390); freeMinted 589 -> 592 (26,6%); freeCount user 0 -> 1 (slot ke-2 "
                          "masih terbuka); rarity tier NOT verified (metadata generik); marketplace: TIDAK ada own "
                          "market -> TIDAK di-listing otomatis. Status snapshot -> minted-by-user; later runs do not "
                          "re-report. This run's own Tri333 supply read returned None (RPC degradation).")

# --- Dispositions from discovery + scan legs (recorded as excluded, never re-reported) ---
def add_excluded(key, entry):
    snap.setdefault("excluded", {}).setdefault(key, entry)

add_excluded("PIXEL BOYZ", {
    "address": "0xafb50403c0838d5b45f8748138ba33a70e23b8cf", "track": "A",
    "status": "excluded-age-over-48h-2026-11-07",
    "note": ("Run 2231 Boltbook (boltbook.fun): agent-shaped (agentRegistry = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F), "
             "free 4.467/6.000 = 74,45%, freeAllocationRemaining 1.533, freeSaleActive 1, user slot open "
             "(walletFreeRemaining 2, freeMintedByWallet 0, hasAgentId 1), website pixelboyz.shop VERIFIED (prints "
             "exact contract). BUT launch age >48h: bridge first-seen 2026-11-03 23:42-23:49 WIB + Sourcify verifiedAt "
             "2026-11-02T14:18:28Z. AGE-EXCLUDED (bridge re-read, bukan lead baru — tidak dilaporkan ulang). "
             "First-mint binary search stalled on infra run ini (killed ~470 dtk, zero output); age verdict rests on "
             "bridge first-seen + Sourcify verifiedAt."),
})
add_excluded("Xigo", {
    "address": "0x796387D8106a2edb83e00c4f877e4358Ec721d49", "track": "C",
    "status": "excluded-free-pool-exhausted-age-2026-11-07",
    "note": ("Run 2231 sweep: site xigo.shop VERIFIED (prints exact contracts; MintSale 0x7963...). On-chain blok "
             "132226816: startTime/endTime match site (window ended 2026-11-05), launched=1, free tier 1.000/1.000 "
             "FULLY CLAIMED (totalSupply 4.187.200.000 = 1.000 free + 26 paid shares), freeAvailableFor(user)=0, age "
             "~5 days. Track-C sale: free pool exhausted + age-excluded; $SWARM paid-only. Never a lead."),
})
add_excluded("Binance Fleet Genesis", {
    "address": "0x5bc4fb61270c2628c93bf507c4ba125b868d34ff", "track": "A",
    "status": "excluded-sold-out-2026-11-07",
    "note": ("Run 2231 Boltbook: SOLD OUT totalSupply 1.000/1.000. Never a lead."),
})
add_excluded("MiniCoin", {
    "address": "0x7e624dc2", "track": "A",
    "status": "excluded-no-website-no-agentid-2026-11-07",
    "note": ("Run 2231 sweep: MiniCoin COI 0x7e624dc2... — no website, no Agent ID evidence, no cap; not a lead. "
             "Address prefix only recorded by discovery leg; full address not established — record kept at prefix "
             "level, never re-reported as a lead."),
})
add_excluded("REWARD-cfe5", {
    "address": "0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40", "track": "A",
    "status": "excluded-same-owner-discarded-2026-11-07",
    "note": ("Run 2231 scan triage: first-seen 22:33:02 WIB (blok 132225284), REWARD (RWD) ERC721, 4 mints/4 minters. "
             "Registry bytes hit + agentRegistry() matches, but owner 0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3 IS in "
             "same-owner-discards.json (same owner as FREEDROP run 2201) -> SAME-OWNER DISCARD. Never promoted/reported "
             "as lead, not added to snapshot contracts."),
})

# --- Specials ---
kg = snap["contracts"].get("King's Game")
if kg is not None:
    kg["runNote2231"] = ("Run 2231 (blok 132225965): freeMinted 3, totalMinted 3, balanceOf(user)=0, registry_match true — "
                         "NO CHANGE vs 2201 (same views revert as expected).")
grove = snap["contracts"].get("Agent Grove")
if grove is not None:
    grove["runNote2231"] = ("Run 2231 (blok 132227895): freeOpen 0, freeClaimed(user) false — NO CHANGE vs 2201.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote2231"] = ("Run 2231 (blok 132225884): totalSupply 1256, balanceOf(user)=1 — NO CHANGE vs 2201; "
                           "minted-by-user, bukan kandidat.")

snap["last_run"] = "2026-11-07 run 2231"
snap["last_run_wib"] = "2026-11-07T22:31:00+07:00"
snap["timestamp_wib"] = "2026-11-07 run 2231"
snap["runNote2231_1107"] = (
    "Run 2231 (22:31 WIB): reread blok 132225884, 443 kontrak + 69 track_c, 104 supply-None (degradasi RPC, nilai "
    "lama dipertahankan; 5 kontrak snapshot tanpa field address tidak bisa di-re-read: Mummyhive, LuckyBox-d08e, "
    "SnailMail, Jolly, AgentGlyph — baseline stale 132039757); velocity: 6 passer (Alchemister-0xCafEEDDF +742 "
    "ratio 34,82 umur ~12,7 jam; BOT-UNIT +103 ratio 48,34 umur ~19,6 jam; Alchemister +128 ratio 6,32; AgentVOLT "
    "+56; MORPHA +55; NULLRAID +23) — SEMUA freePct None (tidak ada free counter terbaca on-chain), jadi kaki 50% "
    "free-quota UNVERIFIED untuk semua passer dan TIDAK ADA promosi; 35 sellout, set identik 2201, 0 sellout baru; "
    "age-exclusion: 0 dihapus; HIVE/King's Game/Grove tanpa perubahan; track_c 5 drift totalSupply saja (ORBITA, "
    "QuonkersAgent, Draco Coin, PHNX, Crack 3523->3539), 0 free view terbaca (0/69), 0 sellout. Tri333 #590 sudah "
    "di-mint hot-leg 22:46 WIB (tx 0x5b70a678..., blok 132227104) — status snapshot -> minted-by-user."
)
snap["runNote2231_1107_scan"] = (
    "Run 2231 scan: pre-flight OK 4,4 dtk (head 132225827, 210 logs/50 blok). Scan SUKSES percobaan pertama "
    "(onchain_nft_scan.py kanonis sudah membawa patch batch 2201; tidak di-patch ulang): window 132224859-132225858 "
    "(1000 blok terbaru), 117 NFT (112 ERC721 + 5 ERC1155, 1.275 mint), 371 ERC-20 mint, 39 panggilan Ankr, "
    "partial=False, ~17 mnt; 1 error transient (TransferSingle chunk 132225309-132225358 Remote end closed, chunk "
    "tetap selesai). HIVE tidak ada di window. Triage: 1 first-seen, 0 EARLY lead (REWARD 0xcfE5... same-owner "
    "discard; Tri333 in-window tapi sudah di snapshot / sudah di-mint). Seen file +154 (total nested 11.574). 5c: "
    "7 ERC-20 baru dicek (mint_count>=10), 0 sale-shape; track-c-scan-checked.json 2.666. Watermark TIDAK dimajukan "
    "(milik backfill); gap ke watermark milik backfill."
)
snap["runNote2231_1107_discovery"] = (
    "Run 2231 discovery: Boltbook boltbook.fun EN+ZH, 17 alamat, 0 proyek baru. PIXEL BOYZ 0xafb5... near-miss: "
    "agent-shaped, free 4.467/6.000 (74,45%), slot user terbuka, website pixelboyz.shop terverifikasi — TAPI umur "
    ">48 jam (bridge first-seen 2026-11-03 23:42 WIB + Sourcify verifiedAt 2026-11-02) -> AGE-EXCLUDED, bridge "
    "re-read, tidak dilaporkan ulang. BRAINROT ZOO 0x3c7d... bukan lead (321/1.667 = 19,3% <25%, tanpa Agent ID "
    "gate, umur unverified) — watchlist-only, TIDAK ditambah ke snapshot (bukan agent-shaped). Binance Fleet "
    "Genesis 0x5bc4... SOLD OUT 1.000/1.000. AGCC minter 0x6288... + token AGC 0x63de... = skema deposit 24 jam, "
    "bukan free mint (user sudah pegang ~456.444 AGC) — tidak ditambah ke snapshot. Sweep: Xigo (xigo.shop) sale "
    "track-C terverifikasi situsnya tapi free pool 1.000/1.000 habis + umur ~5 hari -> excluded; MiniCoin COI "
    "0x7e62... tanpa website/Agent ID -> excluded. Sourcify 5a: 20 kontrak (verifiedAt 22:25-22:33 WIB), 0 S1/S2/0 "
    "agent-mint (feed urllib gagal 2x RemoteDisconnected, fallback curl pulih). Square: tanpa lead baru (JAGENT "
    "paid, Ptah, MiniCoin). Odaily/PANews: 0 item Agent ID. DappBay tidak diperlukan. Bridge tidak berubah (sha256 "
    "b3f349f1...), 115 kontrak, 33 di luar snapshot, 0 promosi; 7 same_owner_discarded tidak disentuh. Track-B "
    "binanceai identik run 1701-2231 (launched 0, failed 1, refund 1) — tidak dilaporkan ulang."
)
snap["runNote2231_1107_binanceai"] = (
    "Run 2231 track-B binanceai re-check (blok 132225894): launched()=0, failed()=1, isRefundPhase()=1, "
    "totalShares()=3110, tokenClaimed(user)=0, balance=0, pair reserves 0/0 — IDENTIK run 1701-2201; sudah "
    "dilaporkan sekali, tidak dilaporkan ulang. Tidak ada preview/klaim."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "| track_c:", len(snap.get("track_c", {})),
      "| excluded:", len(snap.get("excluded", {})))
print("updated:", updated, "| none_supply:", none_supply, "| tc_updated:", tc_updated)
print("removed (age-excluded): none")
