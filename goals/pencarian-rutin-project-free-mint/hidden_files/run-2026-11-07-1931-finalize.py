#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-07 19:31 WIB (run 1931).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json,
plus the BOBBIE strong-lead direct mint (parent-executed) and Leg 2/4/5 notes.
Read-only inputs; writes snapshot only."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132203703

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-07-1931-reread.json"))
vel = json.load(open(HF + "run-2026-11-07-1931-velocity.json"))
age = json.load(open(HF + "run-2026-11-07-1931-age-sweep.json"))

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
    c["lastReadWib"] = "2026-11-07 run 1931"
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
            c["freePctInference"] = vrow["freePct"]
    c["runNote1931"] = (
        f"Run 1931 (blok {BLOCK}): totalSupply {c.get('totalSupply')} "
        f"(prev {c.get('previousTotalSupply')}), minted interval "
        f"{vrow['mintedInInterval'] if vrow else 'n/a'}, "
        f"velocity {'LOLOS' if (vrow and vrow['velocityPasses']) else 'GAGAL'}"
        f"{' — free% UNVERIFIED, no promotion' if (vrow and vrow['velocityPasses']) else ''}; "
        f"balanceOf(user)={c.get('balanceOf_user', c.get('userBalance'))}; "
        f"free views None (degradasi eth_call, nilai snapshot dipertahankan)."
        if vrow else
        f"Run 1931 (blok {BLOCK}): totalSupply {c.get('totalSupply')}; "
        f"free views None (degradasi eth_call, nilai snapshot dipertahankan)."
    )

# track_c reread
tc_updated = 0
tc_none = 0
for name, rd in reread.get("track_c", {}).items():
    t = snap.get("track_c", {}).get(name)
    if t is None:
        continue
    tc_updated += 1
    if rd.get("totalSupply") is not None:
        t["totalSupply"] = rd["totalSupply"]
    else:
        tc_none += 1
    for f in ("freeMinted", "freeSharesRemaining"):
        if rd.get(f) is not None:
            t[f] = rd[f]
    if rd.get("balanceOf_user") is not None:
        t["balanceOf_user"] = rd["balanceOf_user"]
    t["lastReadBlock"] = BLOCK
    t["lastReadWib"] = "2026-11-07 run 1931"

# age exclusions: remove the 3 candidates
removed = []
for cand in age["candidates"]:
    name = cand["name"]
    if name in snap["contracts"]:
        entry = snap["contracts"].pop(name)
        removed.append(name)
        snap.setdefault("age_exclusions", []).append({
            "name": name,
            "address": cand["address"],
            "firstMintWib": cand["firstMintWib"],
            "ageHours": cand["ageHours"],
            "supply": cand.get("curSupply"),
            "maxSupply": cand.get("maxSupply"),
            "status_before": cand.get("status"),
            "removed_run": "2026-11-07 run 1931",
            "removed_wib": "2026-11-07 ~20:25 WIB",
            "reason": f"Umur peluncuran terverifikasi {cand['ageHours']} jam (>48 jam) dan belum sold out "
                      f"({cand.get('curSupply')}/{cand.get('maxSupply')}); dihapus dari watchlist aktif per aturan umur 48 jam.",
        })

# BOBBIE — strong-lead direct mint executed by parent this run
b = snap["contracts"].get("BOBBIE")
assert b is not None, "BOBBIE missing from snapshot"
b["status"] = "minted-by-user-2026-11-07"
b["freeAllocated"] = 1572
b["freePctVerified"] = 78.6
b["totalMinted"] = 1655
b["totalMintedNote1931"] = ("publicMinted 1655 via /api/mint-window blok 132205331; "
                             "eth_call totalMinted() gagal transient (RemoteDisconnected) run ini.")
b["mintEndsAt"] = "2026-11-16 14:40:09 WIB (on-chain, koreksi: tercatat 2026-11-07 00:40 WIB SALAH)"
b["mintTx"] = "0x6813257cfa75abda36407e880073ac45f6bc4bf5b8ecf3d0a5adbd8e01ec536d"
b["mintBlock"] = 132206400
b["mintGas"] = 173182
b["mintSequence"] = 1585
b["mintTargetBlock"] = 132206420
b["settleTx"] = "0xf911ab16cefafec1ac6b573cfe840861a9a188e374a0cdd71414b47e889c7749"
b["settleBlock"] = 132206533
b["settleGas"] = 197910
b["mintTokenId"] = 4023
b["userBalance"] = 1
b["balanceOf_user"] = 1
b["mintedBy_user"] = 1
b["userSlot"] = {"mintedBy": 1, "freeUsed": 1, "slotOpen": False,
                 "note": "Slot TERPAKAI oleh mint run 1931 (free 1/1); next mint berbayar, TIDAK diotorisasi"}
b["websiteNote"] = ("TERVERIFIKASI run 1931: https://bobbiebsc.com mencetak kontrak persis 5x "
                    "(31.456 B); /api/config nft cocok + protocolVersion 4 + mintMode future-block; "
                    "/api/mint-window status open; X https://x.com/BobbieBSC")
b["gateNote1931"] = "Gate website LOLOS run 1931 (metode G/I: situs + tokenURI external_url cocok)."
b["auditNote1931"] = ("Binance audit run 1931: hasResult=false (TIDAK ADA HASIL, bukan lolos), "
                      "isSupported=true, riskLevel -1, tanpa RISK hit, riskAlert null.")
b["previewNote1931"] = ("Preview bersih 000000000 di kedua langkah v4: mint(1,1,0x0,0,0x) tanpa "
                        "perubahan saldo/authority/allowance/risk; settleMint(1585) +1 ERC721 #4023.")
b["voucherNote1931"] = ("Voucher KOSONG (0x) valid untuk base free right: kode kontrak (Sourcify "
                        "exact_match) hanya memvalidasi signature voucher bila voucher.length > 0; "
                        "voucher server hanya untuk hak sosial ke-2 (socialGranted).")
b["rarityNote1931"] = ("Tier Epic (trait 'Tier' metadata tokenURI "
                       "https://assets.bobbiebsc.com/metadata/4023.json); traits: Background epic, "
                       "Hat 1, Hair 3, Accessory 2, Eyes 1, Outfit 5, Avatar 2. Dicatat di nft-rarity-inventory.md.")
b["marketplaceNote1931"] = ("TIDAK ada venue live: transfer TERKUNCI on-chain (_update revert "
                            "'TransfersLocked' sampai saleFinalized; mint-window finalized=false); market "
                            "native 0xfA239D919Db60E1b497E9E8CA26CA79689a180AF belum bisa trading -> TIDAK di-list.")
b["strongLeadNote1931"] = ("Strong lead saat mint: umur ~29,5 jam (mintStartsAt on-chain 2026-11-06 "
                           "14:40:09 WIB, first mint 14:46:04 WIB), free 1572/2000 = 78,6% (>=25%), slot "
                           "user terbuka (quote(user,1,false) = (1,0,0,1577), mintedBy 0, freeUsed 0, "
                           "eligible 1, balance 0). X unverified (opsional, bukan gate).")
b["lastReadBlock"] = 132206533
b["lastReadWib"] = "2026-11-07 run 1931"

snap["last_run"] = "2026-11-07 run 1931"
snap["last_run_wib"] = "2026-11-07 20:25 WIB"
snap["timestamp_wib"] = "2026-11-07 20:25 WIB"
snap["runNote1931_1107"] = (
    "Run 1931: reread 446/451 kontrak (blok 132203703, 811 dtk; 105 supply None = degradasi eth_call, "
    "nilai lama dipertahankan); velocity 1 LOLOS (MORPHA +114, 3,29/mnt, rasio 1,51x) — free% UNVERIFIED -> "
    "0 promosi; 4 pelolos 1901 gagal velocity run ini (rasio 0,30-0,47). Sold-out 35 (0 baru); slot berubah 0 "
    "di snapshot utama (Ink Koi balance 0->1 adalah mint #712 sendiri 19:38 WIB, sudah dilaporkan hot-leg 1929). "
    "Age-exclusion 3 dihapus: Agent Pioneers, Mooji Ark, Night Shift Rigs (semua ~48,2-48,3 jam, belum sold out). "
    "BOBBIE strong-lead direct mint BERHASIL: #4023 gratis (commit 0x6813257c... blok 132206400 + settle "
    "0xf911ab16... blok 132206533; ownerOf(4023) = wallet agent). Bridge tidak berubah (0 promosi). "
    "Scan SUKSES partial=false (preflight PASS 15 dtk; window 132202724-132203723; 127 NFT + 353 ERC-20); "
    "4 first-seen, 0 lead (Proof of AGI, Gacha Gang Machine, ADCHAR, Yarrow Isthmus). Sourcify feed 0 hit; "
    "5c 13 dicek 0 hit. Track B: binanceai refund phase, Grove belum buka — tanpa perubahan. KZMB sharesSold "
    "719-725/1.000, gate tetap gagal, tidak dilapor ulang. BRAINROT ZOO: same-owner discard (owner "
    "0x11038f4a...), bukan lead, tidak masuk snapshot. 1 eksekusi (BOBBIE) — laporan mint ke chat utama."
)
snap["runNote1931_1107_scan"] = (
    "Run 1931 scan: preflight PASS 15 dtk (head 132203682, 305 log); window 132202724-132203723 (1000 blok, cap); "
    "gap 132188666-132202723 (14.058 blok) untuk backfill; watermark TIDAK dimajukan (tetap 132188665, milik backfill); "
    "chunk 20/20, 0 error, 40 panggilan Ankr, ~18 mnt; 127 NFT (123 ERC721 + 4 ERC1155) + 353 ERC-20-mint; "
    "partial=false. 4 first-seen: Proof of AGI (not agent-shaped), Gacha Gang Machine (not agent-shaped), "
    "ADCHAR (not agent-shaped), Yarrow Isthmus (agent-shaped, tanpa free view -> kemungkinan paid-only, bukan lead). "
    "Seen file +167 -> 10.747. Caveat: Sourcify error:IncompleteRead massal — enrichment terbatas pada registry_bytes_hit run ini."
)
snap["runNote1931_1107_gate_forwards"] = (
    "BRAINROT ZOO 0x3C7D328027Ca0068e7CD8709D64D9161Bc35de93 (Boltbook jamaica.ai 19:46 WIB): totalSupply 197/1667, "
    "freeLeft 1.469 (~11,9%), first mint 2026-11-07 19:10:00 WIB, website terverifikasi via tokenURI "
    "(brainrot-zoo.pages.dev mencetak kontrak + registry) — TAPI same-owner DISCARD: owner/treasury "
    "0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd (gelombang 10 kontrak, dibuang run 0001 2026-11-06 01:40 WIB; "
    "dikonfirmasi ulang run 1901). BUKAN lead, TIDAK masuk snapshot, TIDAK dilaporkan. "
    "HOPKIN GENESIS: DITOLAK umur (first mint 2026-11-03 13:50:18 WIB, ~4,3 hari >48 jam); hopkinagent.fun tidak "
    "mencetak kontrak. HORUS: NFT soulbound permanen (ERC-5192), exit hanya burn -> 10.000 HOAI, terkunci sampai "
    "8.000 paid mint / mintOpen mati; LP 0 BNB. Gacha (klaster 0x1103) 267/888 = 30,1% tapi tanpa website -> gate gagal. "
    "KZMB sharesSold 725/1.000 (leg 2) / 719 (leg 5, blok 132204163) — gate tetap gagal, sudah dilaporkan 10:45 WIB."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print(f"contracts updated: {updated} (none_supply {none_supply}); track_c updated: {tc_updated} (none {tc_none})")
print(f"removed age-excluded: {removed}")
print(f"contracts now: {len(snap['contracts'])}; track_c: {len(snap['track_c'])}; age_exclusions: {len(snap['age_exclusions'])}")
print("BOBBIE status:", snap["contracts"]["BOBBIE"]["status"])
