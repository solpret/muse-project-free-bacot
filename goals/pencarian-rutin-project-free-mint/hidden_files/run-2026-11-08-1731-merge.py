#!/usr/bin/env python3
"""Merge run 1731 (2026-11-08 17:31 WIB) into snapshot/state/seen/track-c-checked. Parent merge only."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
S = HF + "onchain-snapshot.json"
snap = json.load(open(S))
reread = json.load(open(HF + "run-2026-11-08-1731-reread.json"))
HEAD = reread["block"]  # 132377439
WIB = "2026-11-08 17:31 WIB"
contracts = snap["contracts"]

# --- 1. re-read numeric updates (non-None only) ---
NUM = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"]
updated = 0
for name, rd in reread["reread"].items():
    e = contracts.get(name)
    if e is None:
        continue
    changed = False
    for f in NUM:
        v = rd.get(f)
        if v is not None and e.get(f) != v:
            e[f] = v
            changed = True
    e["lastReadBlock"] = HEAD
    e["lastReadWib"] = WIB
    if changed:
        updated += 1
print("contracts updated (numeric change):", updated, "of", len(reread["reread"]))

# --- 2. track_c updates ---
tc = snap["track_c"]
tc_updated = 0
for name, rd in reread["track_c"].items():
    e = tc.get(name)
    if e is None:
        continue
    for f in ["totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"]:
        v = rd.get(f)
        if v is not None and e.get(f) != v:
            e[f] = v
            tc_updated += 1
    e["lastReadWib"] = WIB
print("track_c fields updated:", tc_updated)

# --- 3. per-contract run notes 1731 ---
notes = {
    "Gourdmare": "Run 1731: velocity PASS (+61, 66.34x) free% VERIFIED 66.1% - TAPI status promotion-discarded-same-owner-2026-11-03 - TIDAK PERNAH dipromosikan/dilaporkan.",
    "Ink Koi": "Run 1731: velocity PASS (+162, 16.47x) free% VERIFIED 69.5% (1929/2777, 848 tersisa), umur first mint 2026-11-07 17:13:03 WIB - TAPI slot user SUDAH terpakai (freeClaimed(user)=1, balance 1) - BUKAN kandidat/strong lead, tidak promosi.",
    "HIVE Agents": "Run 1731: totalSupply flat 1256, balanceOf(user)=1, status minted-by-user - tanpa perubahan.",
    "Oddlode Drills": "Run 1731: totalSupply 824->995 (99.5% free, freeMinted 995/1000) - hampir sold out, minted-by-user, bukan promosi.",
    "Paw Gang": "Run 1731 (read-only): totalMinted 3002->3110 (+108), mintOpen 1, balance 0; PoW tetap memblokir (tidak dicoba ulang di VM).",
    "Bubblebruin": "Run 1731: totalSupply 2077->2081 (+4), free% 26.7% (2075/7777), minted-by-user - tanpa perubahan.",
    "Jinli Agents": "Run 1731: 277->280 (+3), free% 31.2%, slot terbuka, gate website tetap GAGAL (tidak berubah) - tidak di-mint, tidak dilaporkan ulang.",
    "Dafeiyu": "Run 1731: 666 (0), free view degraded (None = artefak RPC), slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.",
    "Chiphiveowl": "Run 1731: 584 (0), free% 72.4%, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.",
    "Farmbuxiang": "Run 1731: 480 (0), free% 68.4%, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.",
}
for name, note in notes.items():
    if name in contracts:
        contracts[name]["runNote1731_1108"] = note

# --- 4. REMOVE CATAI (age-exclusion, 48.3h) -> excluded ---
catai = contracts.pop("CATAI", None)
print("CATAI removed:", catai is not None)
if catai is not None:
    snap.setdefault("excluded", {})["CATAI"] = {
        "address": "0x4aB809dc6e0C62a82d5Bff2F128C9FA30D752297",
        "reason": "AGE-EXCLUDED run 1731: launch terverifikasi firstMintWib 2026-11-06 17:15:44 WIB (firstMintBlock 131991079), umur 48.3 jam saat run 1731 (deadline 48 jam 2026-11-08 17:15:44 WIB), totalSupply 76/5000, free% UNVERIFIED, belum sold out. Dihapus dari watchlist per aturan 48 jam, dilaporkan sekali run 1731.",
        "removed_wib": "2026-11-08 17:31 WIB",
        "status_before": catai.get("status"),
    }

# --- 5. ADD BAHUANG2 (early lead) ---
contracts["BAHUANG2"] = {
    "address": "0x57CC350b844484Eac0DE444526d295C90F9cCbB5",
    "status": "early-lead-reported-2026-11-08",
    "name": "BAHUANG2",
    "symbol": "BAHUANG2",
    "kind": "ERC721",
    "totalSupply": 194,
    "totalMinted": 194,
    "freeClaimed": None,
    "freeMinted": 196,
    "FREE_CAP": 3000,
    "FREE_PER_WALLET": 2,
    "FREE_REWARD": None,
    "freeCount_user": 0,
    "mintStart": 1794133293,
    "mintEnd": 1794565293,
    "costWei_1": 430744843984217,
    "freePctVerified": 6.53,
    "firstMintWib": "2026-11-08 17:21:43 WIB",
    "firstMintBlock": 132375730,
    "firstMintTx": "0x085210b23124e0bafd81c6a9e10b5a24da97afab8e53d8560557f9521e8845bf",
    "agentId": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "scanMints": 114,
    "scanMinters": 57,
    "scanWindow": "132376462-132377461",
    "sourcify": "verified",
    "website_gate": "NOT VERIFIED run 1731 (parent): contractURI() reverts (tidak ada fn), tokenURI(0) reverts; pencarian nama tanpa hit proyek; TIDAK ADA situs terverifikasi - gate akan GAGAL bila dicek untuk eksekusi.",
    "x_discussion": "NOT FOUND run 1731: pencarian nama + Boltbook tanpa sebutan proyek.",
    "launchNote": "Launch VERIFIED <=48h: first mint blok 132375730 = 2026-11-08 17:21:43 WIB (Ankr getLogs, 4 Transfer log di blok itu); mintStart 1794133293 = 17:21:33 WIB mengkoroborasi. Umur ~14-18 menit saat verifikasi.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1731. Agent-shape: agentId() = registry persis + FREE_CAP/FREE_PER_WALLET/freeCount/freeMint/freeMinted. freeMinted 32 (17:19) -> 196 (17:35) = +164 dalam ~16 menit, 6.53% dari FREE_CAP 3000 - di bawah ambang strong lead 25% dan kandidat 50%. Slot user TERBUKA (freeCount(user)=0, FREE_PER_WALLET 2). owner() tidak ada di ABI -> same-owner check N/A. TIDAK PERNAH di-preview/di-mint sebagai early lead. Catatan: totalMinted terbaca 194 vs freeMinted 196 - selisih 2, dicatat apa adanya (counter berbeda).",
    "velocityNote": "freeMinted 32->196 dalam ~16 menit; baseline pertama disimpan run ini, velocity belum terhitung (butuh rate sebelumnya).",
    "lastReadBlock": HEAD,
    "lastReadWib": WIB,
}
print("BAHUANG2 added as early lead")

# --- 6. ADD MONOLITH (early lead) ---
contracts["MONOLITH"] = {
    "address": "0xcdA4A0EF9C0a626b2450168fd8F90f62C51A569b",
    "status": "early-lead-reported-2026-11-08",
    "name": "MONOLITH",
    "symbol": "MNTH",
    "kind": "ERC721",
    "totalSupply": 8,
    "totalMinted": None,
    "freeClaimed": None,
    "freeMinted": None,
    "FREE_CAP": None,
    "freePctVerified": None,
    "firstMintWib": "2026-11-08 17:32:27 WIB",
    "firstMintBlock": 132377160,
    "agentRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "owner": "0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3",
    "scanMints": 7,
    "scanMinters": 7,
    "scanWindow": "132376462-132377461",
    "sourcify": "not_verified",
    "contractURI": "data:application/json;base64 (decoded: name MONOLITH, description 'Monoliths on BNB Chain. An ancient stone, carved with glowing runes. Paid mints earn 100 $GLYPH per day.', seller_fee 500, fee_recipient = owner 0xcbcad...; TIDAK ADA external_link/URL)",
    "tokenURI_1": "Free mint. This token earns no $GLYPH - only paid mints earn 100 $GLYPH per day.",
    "website_gate": "NOT VERIFIED run 1731 (parent): contractURI tanpa external_link/URL; pencarian nama hanya menemukan mnlth.app (platform atribusi artis AI, C2PA) = same-name, BUKAN linkage. TIDAK ADA situs terverifikasi - gate akan GAGAL bila dicek untuk eksekusi.",
    "x_discussion": "NOT FOUND run 1731: pencarian nama + Boltbook tanpa sebutan proyek.",
    "launchNote": "First OBSERVED mint blok 132377160 = 2026-11-08 17:32:27 WIB (dataseed block timestamp), tokenId 1-7, 7 minter berbeda; CAVEAT: token 0 minted SEBELUM window (waktu unverified; walk-back atas skipped gap tidak dilakukan) - umur <=48h LIKELY tapi menit pertama tidak 100% terverifikasi.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1731. Agent-shape: agentRegistry() = registry persis + registry-bytes hit; free views (freeMinted/FREE_CAP/freeLeft/freeClaimed) SEMUA revert - gratis dibuktikan via nilai tx: 7/7 mint in-window value=0 BNB (7 minter berbeda). free% UNVERIFIED (tanpa free-cap view; totalSupply 8). Slot user UNVERIFIED (freeClaimed(agent) revert). Same-owner: owner 0xcbcad... = EXCEPTION di same-owner-discards.json ('TIDAK dibuang oleh aturan same-owner', BNB Faucet) -> BUKAN discard. TIDAK PERNAH di-preview/di-mint sebagai early lead.",
    "lastReadBlock": HEAD,
    "lastReadWib": WIB,
}
print("MONOLITH added as early lead")

# --- 7. ADD NUSA to track_c (lead already reported hot-leg 17:04) ---
tc["NUSA"] = {
    "sale": "0x7D08289E962f5aEc00d56D67322eb2FD056B687c",
    "token": "0x6f91Fc7160Dc873b98a0B21Bdd974AE546FCC19a",
    "tokenName": "NUSA",
    "tokenSymbol": "NUSA",
    "status": "track-c-lead-reported-hot-leg-2026-11-08-1704",
    "saleShape": "S1 PASS (mint + quote + freeRemaining/freeUsed + agentIdRegistry/isAgent), Sourcify exact_match, verifiedAt 2026-11-08T10:03:49Z",
    "MAX_FREE": 560,
    "freeMinted": 14,
    "sharesMinted": 14,
    "paidShares": 0,
    "soldOut": 0,
    "closed": 0,
    "freeAvailable_user": True,
    "freeClaimed_user": False,
    "hasMinted_user": False,
    "quotaOf_user": 7,
    "firstMintWib": "2026-11-08 17:05:23 WIB",
    "ageNote": "VERIFIED <=48h: first mint 17:05:23 WIB (hot-leg 17:04). Umur ~45 menit saat run 1731.",
    "gate": "FAILED (hot-leg 17:04, methods A-H): Sourcify metadata tanpa URL; contractURI() absent/reverts; pencarian nama hanya menemukan token NUSA Base-chain berbeda (Nusantara/NusaChain) = same-name, BUKAN linkage; Boltbook front page absent. Gate TIDAK LOLOS - TIDAK di-preview/TIDAK di-mint. Re-verifikasi hanya bila bukti gate dipersengketakan.",
    "poolNote": "freeMinted 4 (17:04) -> 9 (17:19) -> 11 (17:24) -> 12 (17:34) -> 13 (17:44) -> 14 (run 1731 ~17:50) -> 18 (17:49 hot-leg); 18/560 = 3.21% - jauh di bawah ambang strong lead 25%.",
    "source": "Sourcify recently-verified feed hot-leg 17:04 + verifikasi on-chain run 1731",
    "lastReadWib": WIB,
}
print("NUSA added to track_c (lead already reported 17:04)")

# --- 8. NOVRA -> excluded (checked-not-lead, free pool 0) ---
snap.setdefault("excluded", {})["NOVRA"] = {
    "address": "0x75Ac13cF23a8dccC703D1496138251FD7f247890",
    "reason": "Checked-not-lead, free pool 0: S1/S2 sale-shape PASS (mint + quote + freeRemaining/freeUsed + agentIdRegistry/isAgent, Sourcify exact_match) + umur terverifikasi (first mint 2026-11-07 15:24:57 WIB) TAPI freeRemaining=0 sejak hot-leg 2026-11-07 15:34 WIB (quote(user,1) = 0 free share, cost 0.001 BNB = berbayar); diverifikasi ulang run 1731: freeRemaining=0, totalSupply 73e24 (73 share), MAX_SHARES 2222, balanceOf(user)=0. Situs https://novranetwork.pages.dev/ MENCETAK kontrak persis (2x, dibaca run 1731) - gate situs akan lolos, tapi pool gratis HABIS jadi bukan lead. TIDAK PERNAH dilaporkan sebagai lead (dicatat checked-not-lead-free-pool-zero sejak 2026-11-07). Artikel thecolony.ai yang menyebut 26 free tersisa 2026-11-07 15:37 WIB sudah basi/salah vs on-chain (freeRemaining=0 sejak 15:34).",
    "checked_wib": "2026-11-08 17:31 WIB",
}
print("NOVRA recorded as excluded (free pool 0)")

# --- 9. run notes ---
snap["runNote1731_1108"] = (
    "Run 1731 (17:31 WIB, selesai ~17:55 WIB): 2 EARLY LEAD BARU dilaporkan sekali (BAHUANG2 0x57CC350b844484Eac0DE444526d295C90F9cCbB5, first mint 17:21:43 WIB, freeMinted 196/3000 = 6.53%, slot user TERBUKA, agentId()=registry persis; MONOLITH 0xcdA4A0EF9C0a626b2450168fd8F90f62C51A569b, 7 mint gratis value 0, 7 minter, first observed 17:32:27 WIB, agentRegistry()=registry persis, owner 0xcbcad... = EXCEPTION same-owner (TIDAK dibuang)). Keduanya BUKAN kandidat/strong lead, TIDAK di-preview/TIDAK di-mint; website+X keduanya NOT VERIFIED (BAHUANG2 contractURI revert; MONOLITH contractURI tanpa external_link; pencarian nama tanpa hit proyek). "
    "CATAI 0x4aB809dc6e0C62a82d5Bff2F128C9FA30D752297 AGE-EXCLUDED (launch 2026-11-06 17:15:44 WIB, umur 48.3 jam > 48 jam, supply 76/5000, belum sold out) -> dihapus dari watchlist, dilaporkan sekali. "
    "NUSA (track-C lead, sudah dilaporkan hot-leg 17:04) masuk track_c: freeMinted 14/560, slot terbuka, gate website GAGAL (metode A-H hot-leg) - TIDAK di-preview/TIDAK di-mint. NOVRA: freeRemaining tetap 0 (pool habis sejak 2026-11-07 15:34) -> excluded, bukan lead. Kiko9393 tetap watchlist-only (0 mint). MarsAgent mintOpen=0 terkonfirmasi (sudah dilaporkan hot-leg 17:19 - tidak dilaporkan ulang; tidak ada di snapshot). "
    "Scan route 4 PENUH (window 132376462-132377461, 111 NFT/1005 mint, 292 ERC20, 40 Ankr calls, 0 error, partial=false; pre-flight 5.2 dtk); watermark 132373209 -> 132377461; skipped gap 132373210-132376461 (3.252 blok, backfill off). First-seen 5: BAHUANG2 + MONOLITH (early), OBSIDIAN CARD same-owner-discarded, Aequitas Boost + Barrels for Rum bukan agent-shaped. 5c: 2 baru dicek, 0 hit. Feed Sourcify 20 item: NUSA (sudah dilaporkan), Kiko9393 (0 mint), token '69' pool habis 69/69. "
    "Re-read blok 132377439: 506/511 kontrak + 70/86 track_c; velocity pass 2 (Gourdmare same-owner, Ink Koi slot terpakai) - tanpa promosi; 0 sellout baru; 0 perubahan slot user; Oddlode 995/1000 (99.5%); Paw Gang +108 tetap PoW-blocked; binanceai tetap refund phase (launched 0, failed 1). "
    "Boltbook EN (302 -> /?lang=en, 46.183 B) + ZH (46.385 B): 14 alamat, tanpa proyek baru (5 'baru vs snapshot+seen' terjelaskan: topic hash KAGENT, AGC proyek user, BoltRewards infra, token KAGENT fase refund, FLOAT memecoin). Rute 3: hanya item lama. Rute 6: Odaily/PANews 0 sebutan; DappBay listing AI generik. Bridge: tidak berubah sejak 2026-11-06."
)
snap["runNote1731_1108_scan"] = (
    "Scan run 1731: pre-flight LULUS 5.2 dtk (50 blok, 324 log); window 132376462-132377461 (head 132377461, cap 1000); 20/20 chunk + 111/111 enrich, 0 error, 40 Ankr calls; 111 NFT (106 ERC721 + 5 ERC1155) / 1005 mint / 292 ERC20-mint; HIVE tidak di window; watermark -> 132377461; skipped gap 132373210-132376461 (3.252 blok, backfill OFF). First-seen 5 (BAHUANG2 early, MONOLITH early, OBSIDIAN same-owner, Aequitas + Barrels bukan agent-shaped). Seen 11.491 -> 11.496 kunci. 5c: 41 ERC20 mint_count>=10, 39 sudah dicek, 2 baru dicek, 0 hit S1/S2; track-c-scan-checked 1513 -> 1515. Ankr total run 56 (preflight 1 + scan 40 + BAHUANG2 1 + MONOLITH 14)."
)
snap["last_run"] = "free-mint-search 2026-11-08 1731 WIB"
snap["last_run_wib"] = "2026-11-08 17:55 WIB"
json.dump(snap, open(S, "w"), indent=1)
print("contracts now:", len(snap["contracts"]), "track_c now:", len(snap["track_c"]), "excluded now:", len(snap.get("excluded", {})))

# --- 10. scan state ---
st = json.load(open(HF + "onchain-scan-state.json"))
st["last_scanned_block"] = 132377461
st["last_scan_window_from"] = 132376462
st["last_scan_window_to"] = 132377461
st["last_scan_wib"] = "2026-11-08 17:34-17:47 WIB"
st["last_scan_gap_skipped"] = "132373210-132376461 (3252 blocks; window from watermark to head 4203 blocks > cap 1000; scan covered most recent 1000 only; backfill OFF)"
st["last_scan_ankr_calls"] = 40
st["last_scan_errors"] = 0
st["nft_contracts_last_scan"] = 111
st["erc20_mint_contracts_last_scan"] = 292
st["head_at_scan_start"] = 132377412
st["last_scan_gap_skipped_1731"] = "132373210-132376461 (3252 blocks)"
json.dump(st, open(HF + "onchain-scan-state.json", "w"), indent=1)
print("scan-state watermark -> 132377461")

# --- 11. seen: add 5 first-seen (lowercase -> first block) ---
seen = json.load(open(HF + "onchain-scan-seen.json"))
new_seen = {
    "0x57cc350b844484eac0de444526d295c90f9cbb5": 132375730,
    "0xcda4a0ef9c0a626b2450168fd8f90f62c51a569b": 132377160,
    "0x57e3f981791c3be85d74e74a2f402d7d00f6ed9c": 132377391,
    "0xf415e7a2de78ab57a4428a75d0062e8a999d8b0f": 132377402,
    "0x4bb41db7e49dfa27000ef299e372ac649a197752": 132376926,
}
before = len(seen.get("contracts", {}))
for k, v in new_seen.items():
    seen.setdefault("contracts", {})[k] = v
json.dump(seen, open(HF + "onchain-scan-seen.json", "w"), indent=1)
print("seen contracts:", before, "->", len(seen["contracts"]))

# --- 12. track-c-scan-checked: add 2 addresses ---
chk = json.load(open(HF + "track-c-scan-checked.json"))
added = 0
for addr in ["0xEBbA172c2Dfdd677873102390bfd54aFe0B40D5f", "0xb50dC583cC6F83750c36789F52d51E12dA664444"]:
    if isinstance(chk, dict) and "checked" in chk and isinstance(chk["checked"], list):
        if addr not in chk["checked"] and addr.lower() not in [str(x).lower() for x in chk["checked"]]:
            chk["checked"].append(addr)
            added += 1
    elif isinstance(chk, dict):
        if addr not in chk and addr.lower() not in [str(x).lower() for x in chk.keys()]:
            chk[addr] = {"checked_wib": "2026-11-08 17:31 WIB", "run": "1731", "shape": "no-shape"}
            added += 1
    elif isinstance(chk, list):
        if addr not in chk:
            chk.append(addr)
            added += 1
json.dump(chk, open(HF + "track-c-scan-checked.json", "w"), indent=1)
print("track-c-scan-checked added:", added, "total keys:", len(chk))
print("DONE")
