#!/usr/bin/env python3
"""Merge STAGE 2 run 2026-11-09 1731 WIB — Marbleworks + Motor Agent strong-lead
direct mints (executed), ORDIagent track-C sellout removal, new watchlist adds
(Frost Agent, Quar Agent, 0x13A1Ebc9, track-C 0x260bf39a), Osiris updates.
Read-only w.r.t. chain; never mints/previews. Writes onchain-snapshot.json
(atomic, backup already taken) + run-2026-11-09-1731-merge-stage2.json."""
import json, shutil
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
r1731 = json.load(open(f"{HF}/run-2026-11-09-1731-reread.json"))
m1 = json.load(open(f"{HF}/run-2026-11-09-1731-merge-stage1.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
disc = json.load(open(f"{HF}/same-owner-discards.json"))
disc_contracts = {str(x.get("contract", "")).lower() for x in disc if isinstance(x, dict)}
disc_owners = {str(x.get("owner", "")).lower() for x in disc if isinstance(x, dict)}
frost_owner_hex = hex(1281680467088011730010719489715294596164986997947)
frost_owner_addr = "0x" + frost_owner_hex[2:].rjust(40, "0")
print("Frost/Quar shared owner:", frost_owner_addr, "in discards owners:", frost_owner_addr.lower() in disc_owners)

# ---- 1. Marbleworks: minted-by-user ----
m = contracts["Marbleworks"]
m.update({
    "status": "minted-by-user-2026-11-09",
    "totalSupply": 460, "freeClaimed": 448, "FREE_SUPPLY": 1111, "freePctVerified": 40.3,
    "freeSlotUserOpen": False, "userBalance": 1,
    "mintTx": "0x595e39380ed2019f6eb3de69aceb5532ea07fc10defe156b9ecd6cf0bbc120c0",
    "mintBlock": 132571367, "mintGas": 207591, "mintTokenId": 458,
    "lastReadBlock": 132571367,
    "mintNote1731": "Strong-lead direct mint run 1731 (promosi dari early lead run 1631): freeMinted 432/1111=38.9% saat triase (blok 132570073), mintStart 2026-11-09 17:01:08 WIB (umur ~0.8 jam), slot terbuka freeAvailable=1/freeUsed=0, quote(user,1) cost 0. Website marbleworks.surge.sh terverifikasi run 1631 (mencetak kontrak persis). Same-owner: kontrak tidak ada di discards (60 entri); owner()=0. Audit Binance: code 000000, hasResult=false (TIDAK ADA HASIL, bukan lolos), isSupported=true, riskLevel -1, riskItems [], riskAlert null. Preview BERSIH (requestId a66ab545dfc84ae1aca673a97007e52f): simulationCode 000000000, value 0, authority/allowance kosong, risks kosong; balanceChanges +1 ERC721 (simulasi tokenId 456) + 10.000 MWGL. Eksekusi: orderId 26110900002029461198, BROADCASTED. Verifikasi: receipt status 1, blok 132571367, gas 207591, tokenId AKTUAL 458 (log Transfer 0x0->wallet agent; preview 456 bergeser karena pool bergerak cepat), balanceOf 0->1, freeUsed(user) 0->1, freeMinted 432->448, MWGL balance 10.000 (0x458ba0b810ff314b1D7d41a0F0f209706dcf949b). Rarity: tier NOT verified — tokenURI(458) trait Tier 'Unrevealed', revealed()=0, tierOf reverts pre-reveal (0xb2c9bc88); tier proyek verbatim: Sulphide/Onionskin/Cat's Eye/Swirl/Agate/Clearie (reveal sesudah sale berakhir). Marketplace: TIDAK ada own market live (situs hanya halaman mint/reveal/claim, tanpa market) -> TIDAK di-listing; MWGL tanpa pair terverifikasi -> ditahan. Mint window berakhir 2026-11-14 17:01:08 WIB.",
})

# ---- 2. Motor Agent: minted-by-user ----
mo = contracts["Motor Agent"]
mo.update({
    "status": "minted-by-user-2026-11-09",
    "totalSupply": 1289, "freeClaimed": 1256, "FREE_SUPPLY": 2000, "freePctVerified": 62.8,
    "freeSlotUserOpen": False, "userBalance": 1,
    "mintTx": "0x1faa1e314eb461a32c260cf7f93a5f73defa02d314e921898667ee7eb101b18c",
    "mintBlock": 132572217, "mintGas": 262160, "mintTokenId": 1282,
    "lastReadBlock": 132572217,
    "website": "https://motor-agent.xyz",
    "mintNote1731": "Strong-lead direct mint run 1731 (promosi dari early lead): agentFreeUsed 1092/2000=54.6% saat triase (AGENT_FREE_CAP view terverifikasi), mintStart 2026-11-09 16:08:18 WIB (umur ~1.9 jam), slot terbuka freeUsedByWallet(user)=0/mintedBy=0, PRICE 0.001 BNB (jalur berbayar) tapi mint(1) value 0 TERBUKTI gratis via preview bersih. Website LOLOS segar run ini (motor-agent.xyz HTML mencetak kontrak persis 0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5). Same-owner: kontrak tidak ada di discards (60 entri); kontrak tanpa owner(). Audit Binance: code 000000, hasResult=false (TIDAK ADA HASIL, bukan lolos), isSupported=true, riskLevel -1, riskItems [], riskAlert null. Preview BERSIH (requestId 5ee1016223d94ab4a18a3871d35c0ced): simulationCode 000000000, value 0, authority/allowance kosong, risks kosong; balanceChanges +1 ERC721 (simulasi tokenId 1271). Eksekusi: orderId 26110900002029470695, BROADCASTED. Verifikasi: receipt status 1, blok 132572217, gas 262160, tokenId AKTUAL 1282 (log Transfer), balanceOf 0->1, freeUsedByWallet(user) 0->1, agentFreeUsed 1092->1256, ownerOf(1282)=wallet agent, modelOf=84 (Model No. 85), tierOf=4. Rarity: tier 'Common' (metadata https://motor-agent.xyz/meta/3962.json: 'Sparrow 100 #22/85', Model Sparrow 100, Class Light Commuter, Serial 22, Model Supply 85, Value USD 2200). Marketplace: TIDAK ada own market live (situs: 'BNB market ... coming soon') -> TIDAK di-listing. MOTA: claimable(user) 10.000 MOTA (TOKEN 0xfdd44c29af794249318930cebbf9cc3dfff9e4b1), saldo MOTA 0 — BELUM di-klaim (claimRewards() langkah terpisah, bukan otorisasi mint). Mint window (mintEnd) 2026-11-16 16:08:18 WIB.",
})

# ---- 3. ORDIagent track-C: sold out -> remove ----
ordi = track_c.pop("ORDIagent", None)
snap.setdefault("excluded", {})["ORDIagent"] = {
    "sale": "0x7D10516D08f3bE98aaFD9Ac4169E6Cc30D6bCeB8",
    "token": "0xf969219e0529287bc05ec8c34103503ff7f30a4a",
    "status": "excluded-free-pool-exhausted-2026-11-09",
    "note": "Free pool HABIS terverifikasi on-chain run 1731: freeClaimed()=1000 = FREE_SHARES 1000 (triage2 single-call, blok 132570073); saleStart 1794218400 = 2026-11-09 18:00 WIB; Boltbook 2 post independen (18:00:52, 2 node) mengonfirmasi 1.000/1.000 habis dalam 52 detik. Status lama watchlist-only-not-open-2026-11-09. Dihapus dari track_c; dilaporkan sekali.",
}
print("ORDIagent removed from track_c:", ordi is not None)

# ---- 4. New watchlist adds ----
contracts["Frost Agent"] = {
    "address": "0x09f893bab23d14ad296a17092c6611aac5a0932b", "status": "watchlist-only-age-unverified-2026-11-09",
    "name": "Frost Agent", "kind": "ERC721", "totalSupply": 4900, "MAX_SUPPLY": 5000,
    "freeClaimed": None, "FREE_SUPPLY": None, "xVerified": False, "velocityVerified": False,
    "launchNote": "Usia peluncuran UNVERIFIED (tidak ada mintStart; Sourcify UNVERIFIED; Boltbook post 17:29 WIB 9 Nov hanya recheck, bukan waktu launch).",
    "baselineNote": "Ditemukan via Boltbook front page run 1731 (post recheck 17:29 WIB: 4.900/5.000 free 98%). Triase on-chain run 1731 (blok 132570073): totalSupply/totalMinted 4900, MAX_SUPPLY 5000, registry bytes TRUE, owner sama dengan Quar Agent (template sama, tokenURI ipfs://agent-id/quar-4965/1 untuk keduanya), Sourcify UNVERIFIED (404). Semua free view revert/None (freeMinted/freeClaimed/FREE_SUPPLY/mintStart/mintEnd/mintOpen) -> free% UNVERIFIED, slot UNVERIFIED, website TIDAK DITEMUKAN. BUKAN lead/kandidat; TIDAK pernah preview/mint. Free% 98% dari Boltbook adalah totalSupply/MAX_SUPPLY, BUKAN free counter terverifikasi.",
    "lastReadBlock": 132570073, "lastReadWib": "2026-11-09 17:5x WIB",
    "owner_shared_with": "Quar Agent 0x192721682c64acb6cd31b1589783cecd513ed825",
    "owner_in_discards": frost_owner_addr.lower() in disc_owners,
}
contracts["Quar Agent"] = {
    "address": "0x192721682c64acb6cd31b1589783cecd513ed825", "status": "watchlist-only-age-unverified-2026-11-09",
    "name": "Quar Agent", "kind": "ERC721", "totalSupply": 4900, "MAX_SUPPLY": 5000,
    "freeClaimed": None, "FREE_SUPPLY": None, "xVerified": False, "velocityVerified": False,
    "launchNote": "Usia peluncuran UNVERIFIED (tidak ada mintStart; Sourcify UNVERIFIED; Boltbook post 17:35 WIB 9 Nov hanya recheck, bukan waktu launch).",
    "baselineNote": "Ditemukan via Boltbook post run 1731 (https://boltbook.fun/p/ByrzMYdeTqNE: 4.900/5.000 free 98%, 100 slots tersisa; poster belum mint, menunggu pace). Triase on-chain run 1731: totalSupply/totalMinted 4900, MAX_SUPPLY 5000, registry bytes TRUE, owner sama dengan Frost Agent (template sama, tokenURI ipfs://agent-id/quar-4965/1 untuk keduanya), Sourcify UNVERIFIED. Semua free view revert/None -> free% UNVERIFIED, slot UNVERIFIED, website TIDAK DITEMUKAN. BUKAN lead/kandidat; TIDAK pernah preview/mint.",
    "lastReadBlock": 132570073, "lastReadWib": "2026-11-09 17:5x WIB",
    "owner_shared_with": "Frost Agent 0x09f893bab23d14ad296a17092c6611aac5a0932b",
    "owner_in_discards": frost_owner_addr.lower() in disc_owners,
}
contracts["0x13A1Ebc9-new"] = {
    "address": "0x13A1Ebc988977f8AF0c2983027FF72f4D81BEF00", "status": "watchlist-only-not-open-2026-11-09",
    "name": "0x13A1Ebc9 (unnamed)", "kind": "ERC721", "totalSupply": 0, "FREE_SUPPLY": 50,
    "freeClaimed": None, "xVerified": False, "velocityVerified": False,
    "launchNote": "Usia peluncuran UNVERIFIED (Sourcify verifiedAt 2026-11-09T10:34:24Z = 17:34 WIB; verifiedAt BUKAN launch time; mintOpen 0).",
    "baselineNote": "Ditemukan via Sourcify feed run 1731 (verifiedAt 17:34 WIB). Shape: FREE_SUPPLY 50, freeRemaining 50, mintOpen 0, totalSupply 0, registry bytes TRUE, ABI (registry, eligibility, quoteMintPrice, tokenAgentId). Mint BELUM BUKA -> watchlist-only, bukan lead; TIDAK pernah preview/mint.",
    "lastReadBlock": 132570073, "lastReadWib": "2026-11-09 17:5x WIB",
}
track_c["0x260bf39a-sale"] = {
    "sale": "0x260bf39a6f3aB5E459856297178CC0DF6003374a",
    "token": "0x260bf39a6f3aB5E459856297178CC0DF6003374a",
    "status": "watchlist-only-not-open-2026-11-09",
    "name": "0x260bf39a (unnamed token+sale)",
    "saleShape": "S2 (single-contract token+sale): name/symbol/decimals/totalSupply + claimFree + freeClaimed/FREE_SLOTS + AGENT_ID view + registry bytes TRUE.",
    "note": "Ditemukan via Sourcify feed run 1731 (verifiedAt 17:33 WIB). Triase on-chain run 1731: launched()=0, launchTime()=0 (BELUM BUKA), FREE_SLOTS 500, freeClaimed 362, freeClaimedAddr(user)=0 (slot terbuka), PRICE 0.002 BNB, totalSupply 51.100.000 token. Umur UNVERIFIED (launchTime 0). BUKAN lead (belum buka + umur unverified); TIDAK pernah preview/mint. Pantau run berikut.",
    "lastReadBlock": 132570073, "lastReadWib": "2026-11-09 17:5x WIB",
}

# ---- 5. Osiris updates ----
o = contracts.get("Osiris Guardians")
if o:
    o.update({
        "freeClaimed": 1275, "freePctVerified": 57.4, "mintOpen": 1,
        "website": "https://guardians-of-the-afterlife.pages.dev",
        "freeSlotUserOpen": True,
        "runNote1731_1109": "Run 1731: freeMinted 1275/2222 = 57.4% (naik dari 1248 Boltbook 17:37), paidMinted 13, mintOpen 1, hasFreeMinted(user)=0 (slot TERBUKA), registry bytes TRUE, Sourcify exact_match. Website TERverifikasi run ini: guardians-of-the-afterlife.pages.dev (87.644 byte) mencetak kontrak persis (OSIRIS_NFT_ADDRESS). Umur MASIH UNVERIFIED: tidak ada mintStart di ABI; situs tidak menyatakan waktu launch mint (hanya snapshot 10 Nov + claim buka 11 Nov); walkback first-mint tidak bisa (Ankr 401). BUKAN strong lead (umur unverified) -> tetap watchlist-only-pelengkap-scan, TIDAK preview/mint. Dilaporkan hanya bila promosi/perubahan.",
    })

# ---- 6. run notes ----
snap["last_run_wib"] = "2026-11-09 18:1x WIB"
snap["last_run"] = "1731"
snap["runNote1731_1109"] = (
    f"Run 1731: re-read {len(r1731.get('reread', {}))} kontrak + {len(r1731.get('track_c', {}))} track_c "
    f"(blok {r1731.get('block')}, interval 50.06 mnt vs run 1631). Velocity LOLOS 0. Promosi 0 (di luar 2 eksekusi di bawah). "
    "Age-exclusions baru: 0. Scan leg FAST-FAIL (Ankr pre-flight 2x HTTP 401, outage sejak ~13:33 WIB; watermark tetap 132512564). "
    "EKSEKUSI 2 (strong-lead direct mint): Marbleworks #458 (tx 0x595e39380ed2019f6eb3de69aceb5532ea07fc10defe156b9ecd6cf0bbc120c0, blok 132571367, receipt 1, gas 207591) + "
    "Motor Agent #1282 (tx 0x1faa1e314eb461a32c260cf7f93a5f73defa02d314e921898667ee7eb101b18c, blok 132572217, receipt 1, gas 262160). "
    "Track-C sellout baru: ORDIagent (freeClaimed 1000/1000) — dihapus dari track_c. "
    "Track-B binanceai: TIDAK BERUBAH (launched 0, failed 1, isRefundPhase 1). Bridge: tidak berubah (mtime 2026-11-08 18:21). "
    "Baru masuk snapshot: Frost Agent + Quar Agent (watchlist-only, template sama, free unverified) + 0x13A1Ebc9 (not-open) + track-C 0x260bf39a (not-open). "
    "Osiris: website terverifikasi, free 57.4%, slot terbuka, umur tetap unverified — tetap watchlist-only. "
    "Onyx Agent: alamat tidak didapat (Boltbook post gagal dibuka 429, tidak diulang) — gap dicatat."
)
snap["runNote1731_1109_scan"] = (
    "Run 1731 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok, 2 attempts: "
    "ATTEMPT 1 FAIL 11.0 dtk HTTP 401 Unauthorized; ATTEMPT 2 FAIL 12.5 dtk HTTP 401 Unauthorized "
    "(kredensial custom.ankr ditolak rpc.ankr.com; outage sejak ~13:33 WIB 2026-11-09). "
    "Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~59.000 blok dan tumbuh — milik backfill, ikut gagal 401). "
    "Route 5c: tanpa output scan baru (0 sale-shape dari scan; 0x260bf39a dari feed Sourcify, bukan scan)."
)
snap["runNote1731_1109_mint"] = (
    "Run 1731 mints: (1) Marbleworks #458 — strong-lead direct mint, tx 0x595e39380ed2019f6eb3de69aceb5532ea07fc10defe156b9ecd6cf0bbc120c0, "
    "blok 132571367, receipt 1, gas 207591, value 0, mint() no-arg; free 432/1111=38.9% + umur 0.8 jam + slot terbuka; website marbleworks.surge.sh; "
    "audit hasResult=false (tanpa hasil); preview bersih; tier Unrevealed (pre-reveal); TIDAK ada own market live -> TIDAK di-listing; +10.000 MWGL. "
    "(2) Motor Agent #1282 — strong-lead direct mint, tx 0x1faa1e314eb461a32c260cf7f93a5f73defa02d314e921898667ee7eb101b18c, "
    "blok 132572217, receipt 1, gas 262160, value 0, mint(1); agentFreeUsed 1092/2000=54.6% + umur 1.9 jam + slot terbuka; website motor-agent.xyz "
    "(HTML mencetak kontrak persis, diverifikasi segar); audit hasResult=false (tanpa hasil); preview bersih; tier Common ('Sparrow 100 #22/85'); "
    "TIDAK ada own market live (market 'coming soon') -> TIDAK di-listing; 10.000 MOTA claimable (belum di-klaim, langkah terpisah)."
)
snap["runNote1731_1109_early_leads"] = (
    "Run 1731 early leads: TIDAK ADA early lead baru (Sourcify 6 terbaru 17:28-17:36 WIB: 0xa705707F ERC-20 biasa; 0x13A1Ebc9 agent-shaped not-open; "
    "0x260bf39a track-C S2 not-open; 0xaA972433/0xB65390e3 infra admin; 0x32CBF1f5 memecoin-ish — semuanya checked-not-lead/watchlist-only, bukan early lead "
    "karena tidak ada first mint terverifikasi)."
)
snap["runNote1731_1109_binanceai"] = (
    "Run 1731 track-B: binanceai.fun TIDAK BERUBAH — launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 "
    "(probe dataseed triage, blok 132570073). Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang."
)

def save_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f: json.dump(obj, f, indent=1)
    import os
    os.replace(tmp, path)

save_atomic(f"{HF}/onchain-snapshot.json", snap)
report = {"run": "2026-11-09-1731", "stage": 2, "contracts": len(contracts), "track_c": len(track_c),
          "mints": ["Marbleworks #458", "Motor Agent #1282"],
          "ordiagent_removed": ordi is not None,
          "adds": ["Frost Agent", "Quar Agent", "0x13A1Ebc9", "track-C 0x260bf39a"],
          "frost_quar_owner": frost_owner_addr, "frost_quar_owner_in_discards": frost_owner_addr.lower() in disc_owners}
json.dump(report, open(f"{HF}/run-2026-11-09-1731-merge-stage2.json", "w"), indent=1)
print("MERGE STAGE 2 DONE. contracts:", len(contracts), "track_c:", len(track_c))
