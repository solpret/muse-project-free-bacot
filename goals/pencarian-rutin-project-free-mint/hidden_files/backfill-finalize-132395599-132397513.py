#!/usr/bin/env python3
"""Finalisasi triase backfill run 2026-11-08 20:01 WIB, window 132395599-132397513.
KOREKSI: snapshot contracts bersarang di snap['contracts'] (bukan top-level).
Read-only + penulisan state. TIDAK ada preview/mint/eksekusi."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"

triage = {
    "run": "backfill 2026-11-08 20:01 WIB",
    "window": "132395599-132397513",
    "driver": "backfill-parallel-132395599-132397513.json",
    "driver_exit": 0,
    "chunks": "1/1 (hanya 1 worker: head hanya 1.915 blok di depan watermark saat scan mulai)",
    "watermark_before": 132395598,
    "watermark_after": 132397513,
    "head_at_scan_start": 132397513,
    "head_at_20_31_wib": 132400243,
    "gap_at_20_31_wib": 2730,
    "first_seen_total": 7,
    "first_seen": [
        {
            "address": "0x81b51C61B96A89F5c0a6Da9803F3A422dfa1fC3e",
            "name": "7NFT", "symbol": "7NFT", "kind": "ERC721",
            "mint_count": 205, "distinct_minters": 4,
            "first_block": 132397378, "last_block": 132397479,
            "registry_bytes_hit": False, "sourcify": "not_verified",
            "disposition": "NOT agent-shaped (Sourcify not_verified, tanpa registry hit, tanpa free shape) -> log saja, bukan lead, tidak masuk snapshot."
        },
        {
            "address": "0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE",
            "name": "Gloop", "symbol": "GLOOP", "kind": "ERC721",
            "mint_count": 140, "distinct_minters": 140,
            "first_block": 132395620, "last_block": 132397501,
            "registry_bytes_hit": True, "sourcify": "exact_match",
            "verify": {
                "AGENT_REGISTRY()": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f (PERSIS registry Agent ID)",
                "totalMinted()": 1137, "TOTAL_SUPPLY()": 3333,
                "mintOpen()": True, "MINT_START()": 1794139200,
                "difficultyBits()": 21, "hasMinted(user)": False,
                "owner()": "0x72b9050747bc33d6fef0d76d49b0c7840da47e3b",
                "owner_in_discards": False,
                "first_block_ts": 1794142260, "first_mint_wib": "2026-11-08 19:51:00 WIB"
            },
            "disposition": "Agent-shaped TERVERIFIKASI, TAPI BUKAN lead baru: ini deployment KEDUA Gloop (owner 0x72b9... sama dengan Gloop pertama 0x79d1821b... yang sudah dilaporkan sebagai EARLY lead run 1901; MINT_START + TOTAL_SUPPLY sama). Kontrak ini SUDAH dilacak hot-leg (totalMinted 894->966->1003->1137) dengan keputusan berdiri tanpa promosi (PoW nonce race difficultyBits 21, scope outstanding, website belum terverifikasi) + TIDAK ada fungsi free-mint (jalur gratis TIDAK terverifikasi). TIDAK dilaporkan ulang sebagai EARLY, TIDAK masuk snapshot."
        },
        {
            "address": "0xaCeF3B62B958ED7F49dFc73885609b4d270B9bD0",
            "name": "Beast16", "symbol": "BEAST16", "kind": "ERC721",
            "mint_count": 13, "distinct_minters": 13,
            "first_block": 132395601, "last_block": 132397496,
            "registry_bytes_hit": True, "sourcify": "exact_match",
            "verify": {
                "AGENT_ID()": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f (PERSIS registry Agent ID)",
                "MAX_SUPPLY()": 4444, "totalMinted()": 182,
                "PRICE()": 474008419811561, "currentPrice()": 474008419811561,
                "mintOpen()": True, "OPEN_TIME()": 1794139200,
                "freeUsed(user)": False, "mintedBy(user)": 0,
                "holdsAgentId(user)": True, "soldOut()": False,
                "balanceOf(user)": 0,
                "owner()": "0xd1c14248730bd7cccdf9be9ae47ee272109e53cf",
                "owner_in_discards": False,
                "first_block_ts": 1794142251, "first_mint_wib": "2026-11-08 19:50:51 WIB"
            },
            "disposition": "EARLY LEAD (temuan backfill): SUDAH ada di snapshot sebagai upcoming-prelaunch (Sourcify feed run 1831, totalMinted 0, mintOpen 0) -> run ini memverifikasi LAUNCH: first mint 19:50:51 WIB (umur ~35 mnt, <=48 jam), totalMinted 182/4444, mintOpen true, agent-shaped terverifikasi + jalur gratis ada (mintFree nonpayable, freeUsed(user)=false, slot TERBUKA, holdsAgentId=true). Free % TIDAK terverifikasi (tidak ada FREE_CAP/freeMinted view) -> BUKAN strong lead. Status snapshot DIPROMOSIKAN ke early-lead-backfill-2026-11-08, dilaporkan SEKALI (tag 'temuan backfill'). TIDAK di-preview/di-mint."
        },
        {
            "address": "0xd80D0095746999c93AE837B1DE1569d5814405dC",
            "name": "402", "symbol": "402", "kind": "ERC721",
            "mint_count": 5, "distinct_minters": 5,
            "first_block": 132395729, "last_block": 132397180,
            "registry_bytes_hit": True, "sourcify": "exact_match",
            "verify": {
                "agentIdRegistry()": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f (PERSIS registry Agent ID)",
                "FREE_CAP()": 402, "freeMinted()": 334, "FREE_PER_WALLET()": 1,
                "freeCount(user)": 1, "balanceOf(user)": 1,
                "PRICE()": 42000000000000, "MAX_SUPPLY()": 4020,
                "totalMinted()": 334, "paidMintedCount()": 0,
                "mintOpen()": True,
                "owner()": "0x13333df46ab3e95f4166370d571e7b73aad06370",
                "owner_in_discards": False,
                "first_block_ts": 1794142309, "first_mint_wib": "2026-11-08 19:51:49 WIB"
            },
            "disposition": "Agent-shaped terverifikasi, free pool 334/402 = 83,1%, TAPI SUDAH DIMILIKI user: status snapshot 'minted-by-user-2026-11-08-1531' (STRONG LEAD run 1531 -> auto-mint freeMint(1), tx 0xadf21f79ac6ec04d018c62b5d8bfec85e13c0ebfa748e5a4a8fa2bc79bc903f5, blok 132367660, token #174). Slot user terpakai (freeCount=1, balanceOf=1). BUKAN lead baru, TIDAK dilaporkan, TIDAK diubah di snapshot."
        },
        {
            "address": "0x47feee72353358a61618cE640265F9f406f88E47",
            "kind": "ERC721", "mint_count": 1, "distinct_minters": 1,
            "first_block": 132395696, "last_block": 132395696,
            "sourcify": "404 (not_verified)",
            "disposition": "Bukan agent-shaped (Sourcify 404, tanpa ABI) -> log saja."
        },
        {
            "address": "0xc5C6153e1ff3D05F5424091856F31Bab857DE68c",
            "kind": "ERC721", "mint_count": 1, "distinct_minters": 1,
            "first_block": 132395800, "last_block": 132395800,
            "sourcify": "404 (not_verified)",
            "disposition": "Bukan agent-shaped (Sourcify 404, tanpa ABI) -> log saja."
        },
        {
            "address": "0xAAEF5BB8A7363B5997F17149d554640DC35f306d",
            "name": "EMBER", "symbol": "EMBR", "kind": "ERC721",
            "mint_count": 1, "distinct_minters": 1,
            "first_block": 132396078, "last_block": 132396078,
            "registry_bytes_hit": True, "sourcify": "exact_match",
            "verify": {
                "agentRegistry()": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f (PERSIS registry Agent ID)",
                "MAX_SUPPLY()": 5555, "totalSupply()": 293, "totalMinted()": 293,
                "mintActive()": True, "price()": 1000000000000000,
                "mintCost(1)": 0, "freeUsed(user)": False,
                "owner()": "0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3",
                "owner_in_discards": True,
                "first_block_ts": 1794142466, "first_mint_wib": "2026-11-08 19:54:26 WIB"
            },
            "disposition": "SAME-OWNER DISCARD: agent-shaped terverifikasi + mintCost(1)=0 + slot terbuka, TAPI owner() 0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3 ADA di same-owner-discards.json -> catat di log saja, JANGAN laporkan, TIDAK masuk snapshot."
        }
    ],
    "track_c_5c": {
        "erc20_total": 727,
        "mint_count_ge_10": 86,
        "already_checked": 71,
        "new_checked_this_run": 15,
        "sale_shape_hits": 0,
        "new": [
            {"address": "0x520d9A1DCE6aFC253Fd81CB0Bbf983CDA1020f81", "mint_count": 110, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0x40Aec18c5aE4fd49970758023C15fd05598FE70c", "mint_count": 96, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0xb50dC583cC6F83750c36789F52d51E12dA664444", "mint_count": 81, "result": "exact_match; mintable ERC20 (mint/minter, quoteToken, pair, router, charity); tanpa agentRegistry/AgentGate, tanpa free-share view -> S1=False S2=False"},
            {"address": "0x35148ED78B58739CDAfC570C02F8cBee1BF342E5", "mint_count": 46, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0x01e0CD7bB99db6b7291D95eccA32042BeC320f73", "mint_count": 36, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0xEBCD0F24167a805dc08472d244D78A250489Ee53", "mint_count": 30, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0x332EFB8A690Fd31cB174683f23ff81eD0a4d7F29", "mint_count": 26, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0x6f91Fc7160Dc873b98a0B21Bdd974AE546FCC19a", "mint_count": 23, "result": "exact_match; plain mintable ERC20 (mint/minter/openTrading); tanpa registry/free view -> S1=False S2=False"},
            {"address": "0xB8A203626169E418982A2cB69f920c07C93a11B3", "mint_count": 19, "result": "match (Beacon proxy); ABI tanpa fungsi -> S1=False S2=False"},
            {"address": "0xb42ea00b9b2706575bfbfB50995277e5f09cfFfF", "mint_count": 16, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0xb69c7e3358404aCd305b4047657c40488825781a", "mint_count": 14, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0xEBbA172c2Dfdd677873102390bfd54aFe0B40D5f", "mint_count": 13, "result": "exact_match; plain ERC20 (mintTo/minter); tanpa registry/free view -> S1=False S2=False"},
            {"address": "0x96d8B43DB569bD917ffF11FE1f6E3AeAE60C5c82", "mint_count": 13, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0x13830D475C0e3D3a03aAc600522dc6Dbe3332b5b", "mint_count": 10, "result": "Sourcify 404 not_verified -> S1=False S2=False"},
            {"address": "0xeA37A8DE1de2d9D10772EEB569e28Bfa5Cb17707", "mint_count": 10, "result": "exact_match (ERC1967 proxy); ABI tanpa fungsi -> S1=False S2=False"}
        ]
    },
    "catch_up_step4": "Watermark menyentuh head saat scan selesai (132397513 = head saat scan mulai; gap ~1.300 saat scan selesai) TAPI head kini 132400243, gap 2.730 dan tumbuh ~133 blok/mnt. Laporan 'backfill mengejar head' SUDAH disampaikan 2x hari ini (02:08 dan 03:16 WIB) -> TIDAK diulang sebagai rekomendasi nonaktif baru run ini; cron tetap aktif (next run 20:16 WIB) dan parent yang memutuskan penonaktifan.",
    "no_execution": "Read-only + penulisan state. TIDAK ada preview/mint/klaim/approve/sign/swap."
}

with open(HF + "backfill-triage-132395599-132397513.json", "w") as f:
    json.dump(triage, f, indent=1)

# ---------- 2. Snapshot: PROMOSIKAN Beast16 (sudah ada sbg upcoming-prelaunch) ----------
snap = json.load(open(HF + "onchain-snapshot.json"))
entry = snap["contracts"]["Beast16"]
assert entry["status"] == "upcoming-prelaunch-2026-11-08", entry["status"]
entry.update({
    "status": "early-lead-backfill-2026-11-08",
    "totalMinted": 182,
    "mintOpen": 1,
    "balanceOf_user": 0,
    "userBalance": 0,
    "sourcify": "exact_match",
    "agent_shaped": True,
    "firstSeenBlock": 132395601,
    "firstMintWib": "2026-11-08 19:50:51 WIB",
    "lastReadBlock": 132400243,
    "lastReadWib": "2026-11-08 20:31 WIB",
    "velocityVerified": False,
    "velocityLegPasses": False,
    "xVerified": False,
    "freePctNote": "UNVERIFIED: tidak ada FREE_CAP/freeMinted view di ABI; free % tidak bisa dihitung.",
    "launchNote": "LAUNCH TERVERIFIKASI backfill run 20:01 WIB: first mint 2026-11-08 19:50:51 WIB, blok 132395601 (umur ~35 mnt saat verifikasi, <=48 jam). OPEN_TIME 1794139200 = 2026-11-08 19:06:40 WIB.",
    "note": "EARLY LEAD temuan backfill run 132395599-132397513 (dilaporkan sekali). Sebelumnya upcoming-prelaunch (Sourcify feed run 1831, totalMinted 0, mintOpen 0). AGENT_ID()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry Agent ID, persis). mintOpen=true, MAX_SUPPLY 4444, totalMinted 182. Jalur gratis: mintFree(uint256) nonpayable, freeUsed(user)=false (slot TERBUKA), holdsAgentId(user)=true, mintedBy(user)=0, balanceOf(user)=0. PRICE/currentPrice 474008419811561 wei (~0,000474 BNB, jalur berbayar mintPaid). Free % TIDAK terverifikasi (tidak ada FREE_CAP/freeMinted view) -> BUKAN strong lead (butuh free% >=25% + website terverifikasi). Owner 0xd1c14248730bd7cccdf9be9ae47ee272109e53cf (bukan same-owner discard). TIDAK pernah di-preview/di-mint."
})
snap["runNote_backfill_132395599_132397513"] = (
    "Backfill run 20:01 WIB: 1/1 chunk (132395599-132397513), watermark 132395598->132397513, "
    "7 first-seen. 1 EARLY LEAD: Beast16 dipromosikan dari upcoming-prelaunch (launch terverifikasi first mint 19:50:51 WIB). "
    "Gloop 0x183C... deployment kedua (owner sama), sudah dilacak hot-leg, tanpa promosi (PoW race). "
    "402 sudah dimiliki user sejak run 1531 (token #174), bukan lead. EMBER same-owner discard. 7NFT + 2 kontrak 1-mint bukan agent-shaped. "
    "Track-C 5c: 15 baru dicek, 0 sale-shape. Gap ke head saat scan selesai ~0, kini 2.730 (head 132400243)."
)
with open(HF + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)

# ---------- 3. track-c-scan-checked.json: tambah 15 ----------
chk = json.load(open(HF + "track-c-scan-checked.json"))
added = 0
for item in triage["track_c_5c"]["new"]:
    a = item["address"]
    if a not in chk:
        chk[a] = {"source": "backfill-132395599-132397513-5c",
                  "status": "checked-not-sale-shape",
                  "mint_count": item["mint_count"],
                  "note": item["result"]}
        added += 1
    if a not in chk.get("checked", []):
        chk.setdefault("checked", []).append(a)
with open(HF + "track-c-scan-checked.json", "w") as f:
    json.dump(chk, f, indent=1)

# ---------- 4. State note ----------
state = json.load(open(HF + "onchain-scan-state.json"))
state["note_backfill_132395599_132397513"] = (
    "Backfill run 20:01 WIB OK (1/1 chunk, exit 0, ~606 dtk): watermark 132395598->132397513; "
    "7 first-seen; 1 EARLY LEAD Beast16 (promosi dari upcoming-prelaunch); Track-C 5c 15 baru dicek 0 sale-shape."
)
state["note_backfill_132395599_132397513_triage"] = (
    "Triase: Gloop 0x183C deployment kedua, sudah dilacak hot-leg (PoW race, tanpa promosi); "
    "402 sudah dimiliki user sejak run 1531 (#174); EMBER same-owner discard; 7NFT + 2x 1-mint bukan agent-shaped."
)
with open(HF + "onchain-scan-state.json", "w") as f:
    json.dump(state, f, indent=1)

print("triage rewritten; Beast16 status now:", snap["contracts"]["Beast16"]["status"])
print("track-c added this run:", added, "| checked list len:", len(chk["checked"]))
print("state notes added")
