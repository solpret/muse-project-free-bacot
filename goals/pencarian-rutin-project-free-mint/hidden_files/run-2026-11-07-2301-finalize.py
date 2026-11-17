#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-07 23:01 WIB (run 2301).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json.
No age removals (0 candidates). No promotions (0xbd4B/Ink Koi freePct verified
35.76% < 50%; AgentVOLT/Horus freePct unverified). Adds HELM + HOG to watchlist
(website-gate-failed near-misses). Records discovery/scan dispositions as
excluded (age / sold-out / dead-lane / unverified). Updates King's Game +
Agent Grove + HIVE. Updates last_run + run notes. Watermark NOT advanced
(backfill owns it); scan-state gets note_2301_scan only.
Snapshot + run log only. No mint/preview/claim."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132229422

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-07-2301-reread.json"))
vel = json.load(open(HF + "run-2026-11-07-2301-velocity.json"))

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
    c["lastReadWib"] = "2026-11-07 run 2301"
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
    c["runNote2301"] = ("Run 2301 (blok %d): totalSupply %s, minted interval %s, velocity %s."
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
    t["lastReadWib"] = "2026-11-07 run 2301"

# --- Velocity passer detail: Ink Koi 0xbd4B — freePct VERIFIED 35.76% < 50% ---
inkoi = snap["contracts"].get("0xbd4B4e7189ae9356514664146b0eD683601200A9")
if inkoi is not None:
    inkoi["freePctVerified"] = 35.76
    inkoi["freeMinted"] = 993
    inkoi["FREE_SUPPLY"] = 2777
    inkoi["MAX_SUPPLY"] = 5555
    inkoi["mintOpen"] = 1
    inkoi["freeClaimed_user"] = 1
    inkoi["runNote2301"] = ("Run 2301 (blok 132229422 + single-call re-check run-2026-11-07-2301-passer-free.json): "
                             "velocity PASSES (+107, 861->968, ratio 4.86, age verified ~5.8h, first mint 2026-11-07 "
                             "17:13:03 WIB) BUT freePct VERIFIED 993/2777 = 35.76% < 50% -> FAILS the free-quota leg, "
                             "NOT promotable. balanceOf(user)=1 (already held). METHOD NOTE: reread LEAN batch "
                             "fails whole-batch on reverting no-arg freeClaimed(), so velocity freePct=None can hide "
                             "a readable free counter — passers were single-call re-checked; verdict stands on "
                             "verified data.")

# --- Watchlist additions: HELM + HOG (website-gate-failed near-misses, discovery leg) ---
snap["contracts"].setdefault("helm.ai", {
    "address": "0xe0df49c281b8584f03ed21beac0e5002ec4a0599",
    "name": "helm.ai", "symbol": "HELM", "kind": "ERC721", "track": "A",
    "status": "watchlist-only-website-gate-failed-2026-11-07",
    "source": "boltbook-2026-11-07-run-2301",
    "firstSeenBlock": 132181803, "firstMintWib": "2026-11-07 17:06 WIB",
    "totalSupply": 337, "MAX_SUPPLY": 555, "freeLeft": 218,
    "note": ("Run 2301 Boltbook (boltbook.fun): agent-shaped (registry bytes + agentIds() = registry "
             "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F), totalSupply 337/555 (60,7%), freeLeft 218, price "
             "0,0002 BNB, mintOpen 1, costOf(user,1)=0, freeOf(user,1)=1, mintedBy(user)=0, balanceOf(user)=0, "
             "mint(1) value-0 sim PASSES from user wallet AND fresh no-Agent-ID wallet. Sourcify exact_match, "
             "verifiedAt 2026-11-07T07:29:20Z. Age ~6h < 48h. BUT WEBSITE GATE FAILS: helm.ai is an unrelated "
             "autonomous-driving company; no project site found (Boltbook posts link none; tokenURI(1)='1.json'). "
             "NOT promotable — watchlist-only. Same 0x1103 deployer/template as HOG/GACHA/OMENS. If a project "
             "site appears later, re-check first."),
})
snap["contracts"].setdefault("HOG ORBIT", {
    "address": "0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5",
    "name": "HOG ORBIT", "symbol": "HOG", "kind": "ERC721", "track": "A",
    "status": "watchlist-only-website-gate-failed-2026-11-07",
    "source": "boltbook-2026-11-07-run-2301",
    "firstSeenBlock": 132198351, "firstMintWib": "2026-11-07 19:10 WIB",
    "totalSupply": 319, "MAX_SUPPLY": 1500, "freeLeft": 1181,
    "note": ("Run 2301 Boltbook (boltbook.fun): totalSupply 319/1.500 (21,3% < 25% strong-lead threshold), freeLeft "
             "1.181, price 0,0002 BNB, mintOpen 1, costOf(user,1)=0, freeOf(user,1)=1, mintedBy(user)=0, "
             "balanceOf(user)=0, mintsLeft(user)=10, mint(1) value-0 sim PASSES from user wallet AND fresh "
             "no-Agent-ID wallet. Sourcify exact_match, verifiedAt 2026-11-07T12:10:47Z. Age ~4h. Registry bytes + "
             "agentIds() = registry. BUT WEBSITE GATE FAILS (no site found; tokenURI(1)='/1.json') + below 25% -> "
             "NOT a lead. Watchlist-only. Owner powers live (setFree/setMintOpen/setPrice/setTreasury/teamMint)."),
})

# --- Dispositions from discovery + scan legs (recorded as excluded, never re-reported) ---
def add_excluded(key, entry):
    snap.setdefault("excluded", {}).setdefault(key, entry)

for name, addr, cap, pct, seen in [
    ("Driftnauts", "0x6a926234d3767f2eeb3db12c1b4c9e2912c5589b", "FREE_CAP 2.640", "33,0%", "2026-11-05 14:53 WIB"),
    ("Rigorb", "0x72d977237f7b3931a08434cebd0d3814fe13539e", "10.000", "14,7%", "2026-11-05 04:48 WIB"),
    ("Tumblebots", "0x02f10432eaf9cbf72e1ac9b9208af601aadd6b17", "FREE_CAP 2.000", "37,5%", "2026-11-05 13:17 WIB"),
    ("Forklings", "0xd7b3fd33e0b465b0e374906f60567d317b758fd8", "FREE_CAP 2.000", "53,6%", "2026-11-05 06:25 WIB"),
]:
    add_excluded(name, {
        "address": addr, "track": "A",
        "status": "excluded-age-over-48h-2026-11-07",
        "note": ("Run 2301 Boltbook census post 07NU0LSME7_M: agent-shaped (REGISTRY() = "
                 "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F), free route sim PASSES (4/4 RPCs), canFreeMint(user)=1, "
                 "claimedFree(user)=0, balanceOf(user)=0 — but first-seen %s (>48h ago), AGE-EXCLUDED. Stalled. "
                 "Free cap %s, minted %s. Never a lead." % (seen, cap, pct)),
    })
add_excluded("Sable Agent", {
    "address": "0x23d356173ff227d5bf6d622f4a8907f208871d76", "track": "A",
    "status": "excluded-free-lane-dead-2026-11-07",
    "note": ("Run 2301 Boltbook: totalSupply 4.901/5.000 (98%), price 0,001 BNB, free lane DEAD per Boltbook 2-RPC "
             "post (mint sim reverts); own sim re-run transport-inconclusive (all 4 dataseed endpoints errored). "
             "Sourcify NOT verified (404). Excluded — dead free lane + 98% + unverified."),
})
add_excluded("Coracle Agents", {
    "address": "0x2FCefA216dA37751E102399aCbe1dCC86Dc96eCf", "track": "A",
    "status": "excluded-sold-out-age-2026-11-07",
    "note": ("Run 2301 sweep: website coracle-agents.pages.dev VERIFIED (site prints exact NFT contract), but "
             "SOLD OUT totalSupply 10.000/10.000 + age-excluded (Sourcify verifiedAt 2026-10-27T07:59:04Z). "
             "mintOpen 1, FREE_PER_WALLET 2, mintPrice 0,0005 BNB, balanceOf(user) 0. Never a lead."),
})
add_excluded("Nidavellir", {
    "address": "0xd527109571b039298b65bCB26313dcbED0978c97", "track": "A",
    "status": "excluded-age-unverified-2026-11-07",
    "note": ("Run 2301 sweep: site prints contract, but AGE-EXCLUDED (first-seen blok 131051369 = 2026-11-01 19:46 "
             "WIB, ~6 days) + Sourcify UNVERIFIED (404). totalSupply 1.121/4.444, mintOpen 1, balanceOf(user) 0. "
             "Never a lead."),
})
mints9 = {
    "Vault Agent": ("0xec4f41F60EC868742DE65CAbE6bF9bEA8607b599", "2026-11-03T10:03:33Z"),
    "Xuanwu Seed": ("0x05fd19702029c473683d6188cD856e59038278F4", "2026-10-24T14:47:03Z"),
    "Ombrello": ("0xdAf379E1f0A51Cb9FaaAefF243f26b33Ca8bdDeD", "2026-10-30T18:11:32Z"),
    "Hackou AI Pass": ("0x1e107C43b542eF0d4153d67C1c1a887be60FE3EE", "2026-10-28T18:32:13Z"),
    "Agentic Pixels": ("0x51D87A14B0c0736608e71AEfe8c571faE5Cf19ca", "2026-10-28T01:41:52Z"),
    "Brushborn": ("0x5d43566e40E2e6D396EC10224363E5cAcFc40Cf0", "2026-10-27T07:36:36Z"),
    "CIOW Citizens": ("0xa81b3DcD5c181C0E2E1603e49487ca4ACc814974", "2026-10-29T07:44:58Z"),
    "CZ ID": ("0xb3bc98fb678a99FA890F6242cB332D08feF3104b", "2026-10-31T14:57:10Z"),
    "AGENT NFT": ("0x02A3aC26012cc7017F5cf4e4d481Ee243f9CcEB4", "2026-10-31T04:57:10Z"),
}
for name, (addr, vat) in mints9.items():
    add_excluded(name, {
        "address": addr, "track": "A",
        "status": "excluded-age-over-48h-2026-11-07",
        "note": ("Run 2301 MINTS index (mints-bnb.pages.dev/projects.json) 'unconfirmed' entry: Sourcify verifiedAt "
                 "%s — AGE-EXCLUDED. Index itself marks it unconfirmed, zero_value_mint_simulated=false. Record "
                 "only; never a lead." % vat),
    })
add_excluded("Ticker Pets (TPET)", {
    "address": "not printed in posts", "track": "A",
    "status": "excluded-free-lane-closed-2026-11-07",
    "note": ("Run 2301 Boltbook: free lane CLOSED 555/555. Contract address not printed in posts seen — recorded "
             "without address, never a lead."),
})

# --- Specials ---
kg = snap["contracts"].get("King's Game")
if kg is not None:
    kg["runNote2301"] = ("Run 2301 (blok 132231840): freeMinted 3, totalMinted 3, balanceOf(user)=0, registry_match true — "
                         "NO CHANGE vs 2231.")
grove = snap["contracts"].get("Agent Grove")
if grove is not None:
    grove["runNote2301"] = ("Run 2301 (blok 132231862): freeOpen 0, freeClaimed(user) false — NO CHANGE vs 2231.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote2301"] = ("Run 2301 (blok 132229422): totalSupply 1256, balanceOf(user)=1 — NO CHANGE vs 2231; "
                           "minted-by-user, bukan kandidat.")

snap["last_run"] = "2026-11-07 run 2301"
snap["last_run_wib"] = "2026-11-07T23:01:00+07:00"
snap["timestamp_wib"] = "2026-11-07 run 2301"
snap["runNote2301_1107"] = (
    "Run 2301 (23:01 WIB): reread blok 132229422, 443 kontrak + 69 track_c, 104 supply-None (degradasi RPC, nilai "
    "lama dipertahankan; 5 kontrak snapshot tanpa field address tidak bisa di-re-read: Mummyhive, LuckyBox-d08e, "
    "SnailMail, Jolly, AgentGlyph — baseline stale 132039757); velocity: 3 passer — Ink Koi 0xbd4B +107 ratio 4,86 "
    "umur ~5,8 jam TAPI freePct TERVERIFIKASI 993/2777 = 35,76% < 50% (single-call re-check, run-2026-11-07-2301-"
    "passer-free.json) -> gagal kaki 50%, sudah dipegang user (balance 1); AgentVOLT +69 ratio 1,51 umur "
    "unverified, tanpa free counter; Horus AI +22 ratio 2,25 umur ~26,8 jam, tanpa freeMinted view — SEMUA tidak "
    "promotable; 35 sellout, set identik 2231, 0 sellout baru; age-exclusion: 0 dihapus; HIVE/King's Game/Grove "
    "tanpa perubahan; track_c 5 drift totalSupply saja (Crack 3539->3553, ORBITA, PLNK, Draco Coin, PHNX), 0 free "
    "view terbaca (0/69), 0 sellout. METHOD NOTE: reread LEAN batch gagal whole-batch saat no-arg freeClaimed() "
    "revert -> fallback MINIMAL; freePct=None di velocity bisa menyembunyikan free counter yang terbaca — passer "
    "dicek ulang single-call; sim '0x' (empty success) harus dibaca PASS, bukan gagal (sim-fix lesson run ini)."
)
snap["runNote2301_1107_scan"] = (
    "Run 2301 scan: pre-flight OK 9,7 dtk (head 132229361, 365 logs/50 blok). Scan SUKSES percobaan pertama "
    "(onchain_nft_scan.py kanonis sudah membawa patch batch 2201): window 132228414-132229413 (1000 blok terbaru), "
    "132 NFT (125 ERC721 + 7 ERC1155, 558 mint), 393 ERC-20 mint, 34 panggilan Ankr, ~19,5 mnt; 1 ERROR data-loss: "
    "Transfer chunk 132229264-132229313 Remote end closed -> handler break, 150 blok terakhir (132229264-132229413) "
    "TIDAK ter-scan (effective coverage 132228414-132229263; output JSON tetap partial=False — misleading). Lubang "
    "150 blok hanya tertutup via backfill triage; scan rutin berikut tidak menutupnya (window mulai head-999). "
    "HIVE tidak ada di window. Triage: 4 first-seen, 0 EARLY lead — MooDengMarch 0x09e6..., AgentCard Miner "
    "0x4151..., Rift Beasts 0x22E4..., Chizong Miner 0xeeF9... (semua NOT agent-shaped, no registry/free signal; "
    "bukan same-owner discard). Seen file +168 (total nested 11.750). 5c: 6 ERC-20 baru dicek (mint_count>=10), 0 "
    "sale-shape; track-c-scan-checked.json 2.709. Watermark TIDAK dimajukan (milik backfill, tetap 132213365); "
    "gap ke watermark milik backfill."
)
snap["runNote2301_1107_discovery"] = (
    "Run 2301 discovery: Boltbook boltbook.fun EN+ZH, 12 alamat, 7 baru vs 2231. helm.ai 0xe0df... NEAR-MISS "
    "terdekat: agent-shaped, 337/555 (60,7%), freeLeft 218, sim mint(1) value-0 PASS dari wallet user DAN wallet "
    "fresh tanpa Agent ID, umur ~6 jam, Sourcify exact_match — TAPI WEBSITE GATE GAGAL (helm.ai perusahaan "
    "autonomous-driving yang tidak terkait; tidak ada situs proyek) -> watchlist-only, TIDAK dilaporkan sebagai "
    "lead. HOG ORBIT 0x7bc0... 319/1.500 (21,3% < 25%), sim PASS, umur ~4 jam, tanpa website -> watchlist-only. "
    "Census four (Driftnauts 0x6a92..., Rigorb 0x72d9..., Tumblebots 0x02f1..., Forklings 0xd7b3...) free route "
    "PASS tapi first-seen 4-5 Nov -> AGE-EXCLUDED. Sable Agent 0x23d3... free lane DEAD + 98% + unverified. "
    "Sweep: MINTS index 57 proyek, 9 'unconfirmed' baru — SEMUA age-excluded (verifiedAt 24 Okt-3 Nov). Coracle "
    "0x2fce... situs terverifikasi tapi SOLD OUT 10.000/10.000 + umur. Nidavellir 0xd527... umur ~6 hari + "
    "unverified. TPET free lane CLOSED 555/555. Sourcify 5a: 20 kontrak (verifiedAt 22:55-23:20 WIB), 0 S1/S2/0 "
    "agent-mint (curl langsung; near-miss 0x5615... mint+freeClaimed tanpa registry). Square: Paw Gang konfirmasi, "
    "JAGENT paid, Ptah, Daily Brief — 0 lead baru. Odaily/PANews: 0 item segar. DappBay tidak diperlukan. Bridge "
    "tidak berubah (sha256 b3f349f1...), 115 kontrak, 33 di luar snapshot, 0 promosi. Track-B binanceai identik "
    "run 1701-2231 (launched 0, failed 1, refund 1) — tidak dilaporkan ulang. Limitasi: historical eth_call gagal "
    "'header not found' (dataseed prune); Ankr eth_getLogs kini butuh API key (Unauthorized) — age bersandar "
    "scan first-seen + Sourcify verifiedAt; sim Sable transport-inconclusive; alamat KZMB/GACHA/OMENS tidak "
    "pernah tercetak penuh."
)
snap["runNote2301_1107_binanceai"] = (
    "Run 2301 track-B binanceai re-check (blok 132231895): launched()=0, failed()=1, isRefundPhase()=1, "
    "totalShares()=3110, tokenClaimed(user)=0, balance=0, pair reserves 0/0 — IDENTIK run 1701-2231; sudah "
    "dilaporkan sekali, tidak dilaporkan ulang. Tidak ada preview/klaim."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "| track_c:", len(snap.get("track_c", {})),
      "| excluded:", len(snap.get("excluded", {})))
print("updated:", updated, "| none_supply:", none_supply, "| tc_updated:", tc_updated)
print("removed (age-excluded): none")

# --- Scan state: note only, watermark NOT advanced ---
st = json.load(open(HF + "onchain-scan-state.json"))
st["note_2301_scan"] = (
    "Run 2301 scan (23:01 WIB): pre-flight OK 9,7 dtk (head 132229361, 365 logs/50 blok). Window 132228414-"
    "132229413 (1000 blok terbaru), 132 NFT (125 ERC721 + 7 ERC1155, 558 mint), 393 ERC-20 mint, 34 Ankr calls, "
    "~19,5 mnt. DATA-LOSS: Transfer chunk 132229264-132229313 Remote end closed -> handler break, 150 blok "
    "terakhir (132229264-132229413) TIDAK ter-scan (effective coverage s.d. 132229263; JSON partial=False "
    "misleading). Lubang hanya tertutup via backfill triage. Triage 4 first-seen, 0 EARLY lead. Seen +168 "
    "(11.750). 5c: 6 baru dicek, 0 hit (checked 2.709). WATERMARK TIDAK DIMAJUKAN run ini (tetap 132213365, "
    "milik backfill); gap ke watermark milik backfill."
)
json.dump(st, open(HF + "onchain-scan-state.json", "w"), indent=1)
print("state note_2301_scan written; last_scanned_block still:", st.get("last_scanned_block"))
