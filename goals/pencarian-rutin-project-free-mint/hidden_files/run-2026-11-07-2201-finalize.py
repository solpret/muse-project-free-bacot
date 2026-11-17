#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-07 22:01 WIB (run 2201).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json,
removes AGENTIC PERP + Crimson Eclipse (age-excluded 48.2h),
records discovery/scan dispositions as excluded (sold-out / paid-only /
same-owner-discarded / not-agent-shaped), updates King's Game + Agent Grove,
updates last_run + run notes. Watermark NOT advanced (backfill owns it).
Snapshot + run log only. No mint/preview/claim."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132221547

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-07-2201-reread.json"))
vel = json.load(open(HF + "run-2026-11-07-2201-velocity.json"))

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
    c["lastReadWib"] = "2026-11-07 run 2201"
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
    c["runNote2201"] = ("Run 2201 (blok %d): totalSupply %s, minted interval %s, velocity %s."
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
    t["lastReadWib"] = "2026-11-07 run 2201"

# --- Age exclusions (verified >48h, not sold out) ---
removed = []
for name, addr, first_mint, cur, mx in [
    ("AGENTIC PERP", "0xf1CE53a4BA97a9BaE4b6CBd15f917D42983a4fBB",
     "2026-11-05 21:49:08 WIB", 71, 5000),
    ("Crimson Eclipse", "0x0d37F4cc06c5d0F74DDE1C29e4986F3050e85c48",
     "2026-11-05 21:50:04 WIB", None, 1111),
]:
    old = snap["contracts"].pop(name, None)
    if old is not None:
        removed.append(name)
        snap.setdefault("excluded", {})[name] = {
            "address": addr, "track": "A",
            "status": "excluded-age-over-48h-2026-11-07",
            "note": ("AGE-EXCLUDED run 2201: first mint terverifikasi %s (48,2 jam pada run ini, >48 jam); "
                     "supply %s/%s, belum sold out; status sebelumnya %s; tidak pernah dilaporkan sebagai lead/kandidat."
                     % (first_mint, cur, mx, old.get("status"))),
        }

# --- Dispositions from discovery + scan legs (recorded as excluded, never re-reported) ---
def add_excluded(key, entry):
    snap.setdefault("excluded", {}).setdefault(key, entry)

add_excluded("Agentdragon", {
    "address": "0x2df7435f5bce0577bee213e13da68313c74d7d0b", "track": "A",
    "status": "excluded-sold-out-2026-11-07",
    "note": ("Run 2201 hot-leg 2149 follow-up, blok 132222086: totalSupply 2000 = MAX_SUPPLY 2000, "
             "freeClaimed 1994/2000; Boltbook: 'free lane closed — 2,000/2,000'. SOLD OUT; never a lead."),
})
add_excluded("Coracle Agents", {
    "address": "0x2FCefA216dA37751E102399aCbe1dCC86Dc96eCf", "track": "A",
    "status": "excluded-sold-out-2026-11-07",
    "note": ("Run 2201 sweep, blok 132222635: totalSupply 10.000 = MAX_SUPPLY 10.000 (SOLD OUT); "
             "mintPrice 0,0005 BNB; mintedByWallet(user) 2 (both free mints already used), quote(user,1) 0,0005 BNB. "
             "Site coracle-agents.pages.dev verified (prints exact contract). Never a lead."),
})
add_excluded("Piggy Agent", {
    "address": "0x70385fa94577cb845983d9b6752f2dde2486c837", "track": "A",
    "status": "excluded-sold-out-2026-11-07",
    "note": ("Run 2201 sweep, blok 132223419: totalSupply 10.000 = MAX_SUPPLY 10.000 (SOLD OUT); FREE_SUPPLY 1.000 "
             "exhausted; mintedBy(user) 1, quote(user) 0,00067 BNB. Site piggyagent.space prints exact contract + X "
             "@piggyagentnft. Sourcify verifiedAt 2026-10-24 (age >48h anyway). Never a lead."),
})
add_excluded("Agent Zet", {
    "address": "0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37", "track": "A",
    "status": "excluded-free-phase-complete-2026-11-07",
    "note": ("Run 2201 sweep, blok 132222635: site agentzet.vercel.app states free phase complete 4.000/4.000, "
             "0 free slots; on-chain totalSupply 4.124/4.444 MAX_SUPPLY. Paid-only now; never a lead."),
})
add_excluded("Nomio", {
    "address": "0xC9747B35800eB4A0A3221EB45cb9FcDE7463728C", "track": "A",
    "status": "excluded-paid-only-2026-11-07",
    "note": ("Run 2201 Boltbook: PAID-ONLY — mint() 0,00027 BNB, 'No free lane: mint() at value 0 reverts for every "
             "wallet' (Boltbook dual-RPC post); hot-leg 2149 shape S1/S2 false. Never a lead."),
})
add_excluded("FREEDROP-9293", {
    "address": "0x9293756219863F27Daa1363C7BB92C3b3874Ac2b", "track": "A",
    "status": "excluded-same-owner-discarded-2026-11-07",
    "note": ("Run 2201: agent-shaped (registry bytes + agentRegistry() match), 167/500 minted, mintActive 1, "
             "first mint NOT found in last 10.000 blocks (age + free% unverified); scan triage: 42 mints/42 minters "
             "in window 132221382-132222381. Owner 0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3 IS in "
             "same-owner-discards.json -> SAME-OWNER DISCARD (overrides discovery-leg watchlist-only suggestion). "
             "Never promoted/reported as lead, not added to snapshot contracts."),
})
add_excluded("a46d-unnamed", {
    "address": "0xa46D33862124Da90385cEb58acba63718729DEe0", "track": "A",
    "status": "excluded-same-owner-discarded-2026-11-07",
    "note": ("Run 2201 hot-leg 2149 follow-up, blok 132222086: S1 shape, Sourcify exact_match verifiedAt "
             "2026-11-07T14:48:15Z; totalSupply/totalMinted 0, MAX_SUPPLY 100, FREE_CAP 50, mintActive 1, user slot "
             "open; NO mints yet -> not an early lead; age unverified; website gate FAILED (A/B/C/D/G/H/I/J/M). "
             "Owner 0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3 IS in same-owner-discards.json (same owner as "
             "0x9293...) -> SAME-OWNER DISCARD. Never promoted/reported as lead, not added to snapshot contracts."),
})
add_excluded("dotBots", {
    "address": "0x4123F0f5ca048780C0c91aBC0c7ac12c77a0bF69", "track": "A",
    "status": "excluded-paid-only-2026-11-07",
    "note": ("Run 2201 scan triage: first-seen 22:08:06 WIB, 2 mints/2 minters; registry() matches but verified ABI "
             "has NO free-mint/free view — mint is paid (unitPrice 0,000136 BNB, tier USD prices, Underpaid error); "
             "live totalMinted 129/2222, mintOpen true, canMint(user) true. PAID-ONLY confirmed; never a lead."),
})
add_excluded("OPC NFT Green Card", {
    "address": "0xEF47c2f2bEDAbF7D547A32d91563302567474035", "track": "A",
    "status": "excluded-not-agent-shaped-2026-11-07",
    "note": ("Run 2201 scan triage: first-seen 22:10:21 WIB, 54 mints/1 minter; NOT agent-shaped (no registry bytes, "
             "no free shape, Sourcify not_verified). Never a lead."),
})

# --- Specials ---
kg = snap["contracts"].get("King's Game")
if kg is not None:
    kg["runNote2201"] = ("Run 2201: freeMinted 3, totalMinted 3, balanceOf(user)=0, registry_match true — NO CHANGE vs "
                         "2131 (single-call retry; LEAN batch all-None = whole-batch-revert quirk).")
grove = snap["contracts"].get("Agent Grove")
if grove is not None:
    grove["runNote2201"] = ("Run 2201 (blok 132223465): freeOpen 0, freeClaimed(user) false — NO CHANGE vs 2131.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote2201"] = ("Run 2201 (blok 132221547): totalSupply 1256, balanceOf(user)=1 — NO CHANGE vs 2131; "
                           "minted-by-user, bukan kandidat.")

snap["last_run"] = "2026-11-07 run 2201"
snap["last_run_wib"] = "2026-11-07T22:01:00+07:00"
snap["timestamp_wib"] = "2026-11-07 run 2201"
snap["runNote2201_1107"] = (
    "Run 2201 (22:01 WIB): reread blok 132221547, 445 kontrak + 69 track_c, 105 supply-None (degradasi RPC, nilai "
    "lama dipertahankan); velocity: 1 pass SPURIOUS (bridge-0x6eee ERC-20 AnthroBit, raw-unit scale, freePct None — "
    "BUKAN promosi); 35 sellout, set identik 2131, 0 sellout baru; age-exclusion: AGENTIC PERP + Crimson Eclipse "
    "dihapus (first mint 2026-11-05 ~21:49/21:50 WIB, 48,2 jam); 0 promosi; HIVE/King's Game/Grove tanpa perubahan; "
    "track_c 10 drift totalSupply saja, 0 perubahan pool/slot, 0 sellout."
)
snap["runNote2201_1107_scan"] = (
    "Run 2201 scan: pre-flight OK 13,8 dtk (head 132221526, 251 logs/50 blok). Attempt 1 GAGAL bersih: "
    "onchain_nft_scan.py crash di eth_blockNumber — fast_rpc._single timeout 8 dtk di semua dataseed, sementara "
    "fast_rpc.batch() ke endpoint sama sukses 4,3 dtk (head 132222300). Attempt 2 SUKSES via onchain_nft_scan_2201.py "
    "(rpc_call dialihkan ke fast_rpc.batch, skrip asli tak disentuh): window 132221382-132222381 (1000 blok), "
    "110 NFT (868 mint), 483 ERC-20 mint, 40 panggilan Ankr, 0 error, partial=False, ~17 mnt. Patch batch DIADOPSI ke "
    "onchain_nft_scan.py kanonis run ini (diff hanya import + rpc_call) — _single stall adalah pola stall historis. "
    "Triage: 3 first-seen, 0 EARLY lead (OPC NFT not-agent-shaped; FREEDROP-9293 same-owner discard; dotBots "
    "paid-only). Seen file +221 (total nested 11.416). 5c: 57 ERC-20 mint_count>=10, 49 sudah dicek, 8 baru dicek, "
    "0 sale-shape; track-c-scan-checked.json 2.659. Watermark TIDAK dimajukan (132197165, milik backfill); gap "
    "terlewati cap 132197166-132221381 (24.216 blok) milik backfill."
)
snap["runNote2201_1107_discovery"] = (
    "Run 2201 discovery: Boltbook boltbook.fun EN+ZH identik, 7 alamat, 0 proyek baru. Hot-leg 2149 follow-up: "
    "0xa46D... watchlist-only -> SAME-OWNER DISCARD (owner 0xcbcadc7c... di same-owner-discards.json; 0 mint, gate "
    "gagal); Agentdragon 0x2df7... SOLD OUT 2000/2000; 0x9293... -> SAME-OWNER DISCARD (owner sama). Sweep: Coracle + "
    "Piggy SOLD OUT, Agent Zet free phase complete, Nomio paid-only — semua excluded, bukan lead. TRACE (tracea.cc) "
    "website terverifikasi tapi alamat kontrak tidak established — unverified, bukan lead. Sourcify 5a: 20 dicek, "
    "0 S1/S2 (7 ABI tetap unavailable sesudah retry — cakupan shape tidak penuh jendela ini). Square: hanya item "
    "dikenal (WHALE A 0x8a3e... sold out 5.000/5.000 ~03:10 WIB, alamat lengkap tidak tercatat — hanya di run log). "
    "Odaily/PANews: 0 item Agent ID. Bridge tidak berubah (sha256 b3f349f1...), 0 promosi. Track-B binanceai identik "
    "run 1701-2131 (launched 0, failed 1, refund 1) — tidak dilaporkan ulang."
)
snap["runNote2201_1107_binanceai"] = (
    "Run 2201 track-B binanceai re-check: launched()=0, failed()=1, isRefundPhase()=1, totalShares()=3110, "
    "tokenClaimed(user)=0, balance=0, pair reserves 0/0 — IDENTIK run 1701-2131; sudah dilaporkan sekali, tidak "
    "dilaporkan ulang. Tidak ada preview/klaim."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "| track_c:", len(snap.get("track_c", {})),
      "| excluded:", len(snap.get("excluded", {})))
print("updated:", updated, "| none_supply:", none_supply, "| tc_updated:", tc_updated)
print("removed (age-excluded):", removed)
