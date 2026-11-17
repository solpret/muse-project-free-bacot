#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-07 21:01 WIB (run 2101).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json,
adds King's Game early lead (parent-verified), records Nidavellir as
excluded (free window closed), updates last_run + run notes.
Writes snapshot + scan-state note only. Watermark NOT advanced (backfill owns it)."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132214131

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-07-2101-reread.json"))
vel = json.load(open(HF + "run-2026-11-07-2101-velocity.json"))
age = json.load(open(HF + "run-2026-11-07-2101-age-sweep.json"))
kgame = json.load(open(HF + "run-2026-11-07-2101-kgame-verify.json"))

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
    c["lastReadWib"] = "2026-11-07 run 2101"
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
    c["runNote2101"] = ("Run 2101 (blok %d): totalSupply %s, minted interval %s, velocity %s."
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
    t["lastReadWib"] = "2026-11-07 run 2101"

# King's Game early lead (parent-verified at block 132216765)
snap["contracts"]["King's Game"] = {
    "address": "0x9eA27f3F0919DaF6a4401CFd09563162d395061D",
    "name": "King's Game", "symbol": "KGAME", "kind": "ERC721",
    "status": "early-lead-2026-11-07",
    "firstSeenBlock": 132213748,
    "firstMintWib": "2026-11-07 21:06:29 WIB",
    "scanWindow": "132213162-132214161",
    "scanMints": 1, "scanMinters": 1,
    "agentRegistry": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "registry_match": True,
    "totalMinted": 3, "freeMinted": 3,
    "totalSupply": None, "FREE_SUPPLY": None, "MAX_SUPPLY": None, "mintOpen": None,
    "freePctVerified": None,
    "freeClaimed_user": None,
    "balanceOf_user": 0,
    "contractURI": None,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Launch time UNVERIFIED (first mint seen 2026-11-07 21:06:29 WIB is a lower bound; no project-stated launch time found; raw contract-address search returned no project site/post).",
    "gate": "website UNVERIFIED (method A raw address search: no project hit; Sourcify IncompleteRead, ABI unreadable); X UNVERIFIED.",
    "note": ("EARLY lead run 2101 (reported once): agent-shaped STRICT — agentRegistry() on-chain = registry "
             "0x60B9...022F (parent-verified block 132216765); freeMinted 0 at triage -> 3 at verify (minting live); "
             "totalSupply/FREE_SUPPLY/MAX_SUPPLY/mintOpen/contractURI/freeClaimed(user) all REVERT (views absent) — "
             "free% UNVERIFIED, user slot UNVERIFIED. NEVER preview/mint as early lead; promote only on strong-lead legs."),
    "lastReadBlock": 132216765,
    "lastReadWib": "2026-11-07 run 2101",
}

# Nidavellir — discovered via sweep, website verified but free window closed -> excluded, no report
snap.setdefault("excluded", {})["Nidavellir"] = {
    "address": "0xd527109571b039298b65bCB26313dcbED0978c97",
    "name": "Nidavellir Gold", "symbol": "Gull NFT",
    "track": "A", "status": "excluded-free-window-closed-2026-11-07",
    "website": "https://nidavellirbsc.vercel.app/mint.html",
    "note": ("Run 2101 sweep find (NOT a lead, no report): site verified (mint page prints exact contract + registry + "
             "mint/free rules, method G); on-chain block 132214769 totalSupply 1121/MAX_SUPPLY 4444, mintOpen=1; "
             "FREE slot CLOSED for user: freeWindowOpen()=0, freeRemaining(user)=0 (free quota only within first 1000 slots, "
             "supply already 1121; paid only 0.001 BNB each). Launch time UNVERIFIED (first-mint getLogs probe failed on "
             "all public RPC endpoints — inconclusive, not proof of age). Sourcify NOT verified."),
}

snap["last_run"] = "2026-11-07 run 2101"
snap["last_run_wib"] = "2026-11-07 21:01 WIB"
snap["runNote2101"] = (
    "Run 2101 (21:01-~21:35 WIB): 0 candidate, 0 new strong lead minted, 0 new track-C lead/kandidat, "
    "0 pending claim baru/terbuka/gagal. 1 EARLY LEAD BARU (dilaporkan sekali): King's Game KGAME "
    "0x9eA27f3F0919DaF6a4401CFd09563162d395061D (first mint 21:06:29 WIB, agentRegistry() = registry 0x60B9...022F "
    "parent-verified blok 132216765, freeMinted 0->3; free%/umur/website/X/slot user UNVERIFIED; TIDAK di-preview/di-mint). "
    "1 temuan sweep BUKAN lead: Nidavellir (situs terverifikasi, jendela gratis TUTUP freeWindowOpen=0, freeRemaining user=0) "
    "-> excluded, tanpa laporan. 0 age-exclusion (StarAgent-7d39 sudah excluded run 2131 tgl 2026-11-06; catatan run 2031 "
    "tentang deadline StarAgent ~21:26 WIB adalah rujukan basi — tidak ada aksi). 0 sold-out baru (35 set sama dgn run 2001). "
    "Velocity: 2 pass — NeoGods (+28, 1.65x) + ETHBack (2.83x, artefak token fungible 18 desimal, bukan sinyal mint NFT); "
    "keduanya free% UNVERIFIED -> bukan kandidat. Scan OK (1000 blok 132213162-132214161, 138 NFT, 489 ERC-20, 0 error, "
    "3 true first-seen, 1 early lead KGAME; GDOG Synth + AgentCard Miner bukan agent-shaped). 5c: 6 baru dicek, 0 sale shape. "
    "Sourcify feed: 20 dicek, 0 S1/S2. Boltbook: 8 alamat baru di front page, semua didisposisikan, 0 lead. Bridge: file tidak "
    "berubah sejak 2026-11-06 02:48, 0 promosi, 7 same_owner_discarded tidak dipromosikan. Binanceai tetap refund/failed "
    "(launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed user=0) — sudah dilaporkan sekali run 1701, "
    "tidak dilaporkan ulang. Grove: freeOpen 0, freeClaimed(user) false — identik run 2001."
)
snap["runNote2101_scan"] = (
    "Scan run 2101 SUKSES. Pre-flight OK 4.6 dtk (head 132214123, 255 logs / 50 blok). Window 132213162-132214161 "
    "(1000 blok, cap), 20/20 chunk + enrich, 40 panggilan Ankr, 0 error, partial=false, ~16 mnt. 138 NFT (135 ERC721 + "
    "3 ERC1155, 636 mint), 489 ERC-20 mint. 3 true first-seen (GDOG Synth, AgentCard Miner, King's Game) - 1 early lead "
    "(King's Game). Watermark TIDAK dimajukan (backfill owns it, 132188665). Gap terlewati cap 132188666-132213123 "
    "(24.458 blok) milik backfill. Seen file: triage append 209 entri (total nested 11084). track-c-scan-checked.json: "
    "6 alamat baru (checked list 2599 -> 2605)."
)
snap["runNote2101_binanceai"] = (
    "Run 2101: BINANCEAI launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, "
    "tokenBalance(user)=0 — tetap refund/failed, pending_claims kosong, tidak dilaporkan ulang."
)

with open(HF + "onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
import os
os.replace(HF + "onchain-snapshot.json.tmp", HF + "onchain-snapshot.json")

st = json.load(open(HF + "onchain-scan-state.json"))
st["note_2101_scan"] = snap["runNote2101_scan"]
with open(HF + "onchain-scan-state.json.tmp", "w") as f:
    json.dump(st, f, indent=1)
os.replace(HF + "onchain-scan-state.json.tmp", HF + "onchain-scan-state.json")

print(f"contracts updated: {updated} (supply-None {none_supply}); track_c updated: {tc_updated}")
print(f"contracts total now: {len(snap['contracts'])}; track_c: {len(snap.get('track_c', {}))}; excluded: {len(snap.get('excluded', {}))}")
