#!/usr/bin/env python3
"""Parent merge run 2331 part 2 — FF/VV strong-lead entries with gate (L) outcome (browser verified:
no Website/Social field on either BscScan token page). No execution."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB = "2026-11-09 00:42 WIB"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2331-premerge2")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = s["contracts"]

C["FrankensteinFriends"] = {
    "address": "0xedfd9e6517ad4491ac6c7c98508566e2490ce708",
    "status": "strong-lead-gate-failed-2026-11-08-2331",
    "name": "FrankensteinFriends", "symbol": "FRAFRI", "kind": "ERC721",
    "saleShape": "S1 VERIFIED run 2331 (Sourcify exact_match; mint + quote + free views FREE_PER_WALLET/FREE_SUPPLY/freeClaimed/freeFor/freeLeft/freeUsed + registry ref).",
    "totalSupply": 718, "totalMinted": None, "freeClaimed": 689, "FREE_SUPPLY": 696,
    "freePctVerified": 99.0, "MAX_SUPPLY": 995, "mintOpen": 1,
    "balanceOf_user": 0, "mintedBy_user": 0, "freeUsed_user": 0, "freeLeft_user": 1,
    "quote_user_1": 0,
    "userSlotNote": "Slot TERBUKA: freeLeft(user)=1, freeUsed(user)=0, quote(user,1)=0 (baca segar run 2331).",
    "firstSeenBlock": 132421120, "firstMintWib": "2026-11-08 23:02:21 WIB",
    "creator": "0x90e8b1c93c80758e2bd5032c7acec382501cb84b",
    "creationTx": "0x99f312f9bd909161d97ae8ff62c7ec82c5971deff68e7f1cf0ec23c6aaedb37e",
    "creationBlock": 130925876, "creationTimeUtc": "2026-10-31 21:04:42 UTC",
    "bscscanNote": "BscScan token page dibaca live browser run 2331 (00:11-00:25 WIB 9 Nov): MAX TOTAL SUPPLY 719 FRAFRI (vs totalSupply 718 saat baca on-chain 23:57 WIB - +1 mint), holders 690, transfers 727. Deploy 31 Okt 2026 != launch: launch = first mint 8 Nov 23:02:21 WIB (umur terverifikasi).",
    "lastReadBlock": 132428482, "lastReadWib": "2026-11-08 23:57 WIB",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint VERIFIED on-chain: blok 132421120 = 2026-11-08 23:02:21 WIB (jendela [132420334, 132429334] dicari chunked; tidak ada mint di [132420334, 132421119]. Jendela awal [132411334, 132420333] BELUM terverifikasi - dataseed eth_getLogs semua -32005 limit exceeded; TAPI first mint 23:02:21 konsisten dengan radar zhi19 #717 ~23:10-23:15 WIB dan deploy 31 Okt - launch malam ini terverifikasi). Umur ~1 jam saat dibaca - TERVERIFIKASI <=48 jam.",
    "baselineNote": "STRONG LEAD dilaporkan sekali run 2331 sebagai GATE-BLOCKED (bukan kandidat): 3 kaki strong lead LOLOS (umur terverifikasi <=48 jam + free 689/696=99,0% + slot user terbuka), TAPI gate website GAGAL - TIDAK di-preview/TIDAK di-mint. Satu owner dengan VampireVibes (0x90e8b1c93c80758e2bd5032c7acec382501cb84b, factory wave, bukan di same-owner-discards.json). Bila website terverifikasi kemudian -> jalur direct-mint strong lead; bila sold out / lewat umur / slot hilang -> laporkan sekali + hapus.",
    "gateNote": ("GATE website FAILED (metode A-N dicoba, run 2331): (A) raw contract-address search tanpa hasil; "
        "(B) Boltbook dibaca penuh tanpa tautan; (C) Sourcify source/metadata tanpa URL; (G) project-name search tanpa situs yang mencetak kontrak; "
        "(H) contractURI base64 on-chain JSON tanpa external_link; (I) tokenURI #1 base64 JSON (traits: Armor Monster, Blade Frankenstein, Mask Monster, City Moon) tanpa URL; "
        "(J) ABI tanpa fungsi situs; (K) GitHub code search tanpa hasil; (M) site: filters tanpa hit yang mencetak kontrak; "
        "(N) hop author-bio tidak bisa diselesaikan (tanpa tautan profil author); "
        "(L) BscScan token page via live browser (00:11-00:25 WIB 9 Nov): TIDAK ADA kolom Website/Social/Official Site - hanya 'Click here to update the token information'. "
        "X unverified (akun X opsional, tidak menggagalkan gate)."),
    "runNote2331_1108": "Run 2331: STRONG LEAD gate-blocked - dilaporkan sekali (gate FAILED, metode A-N, termasuk (L) BscScan tanpa website). TIDAK di-preview/di-mint.",
}
C["VampireVibes"] = {
    "address": "0xa5fb4e0e83837e9c7035b47c2f02d7db075563de",
    "status": "strong-lead-gate-failed-2026-11-08-2331",
    "name": "VampireVibes", "symbol": "VAMPIREVIBES", "kind": "ERC721",
    "saleShape": "S1 VERIFIED run 2331 (Sourcify exact_match; mint + quote + free views FREE_PER_WALLET/FREE_SUPPLY/freeClaimed/freeFor/freeLeft/freeUsed + registry ref).",
    "totalSupply": 687, "totalMinted": None, "freeClaimed": 659, "FREE_SUPPLY": 675,
    "freePctVerified": 97.6, "MAX_SUPPLY": 965, "mintOpen": 1,
    "balanceOf_user": 0, "mintedBy_user": 0, "freeUsed_user": 0, "freeLeft_user": 1,
    "quote_user_1": 0,
    "userSlotNote": "Slot TERBUKA: freeLeft(user)=1, freeUsed(user)=0, quote(user,1)=0 (baca segar run 2331).",
    "firstSeenBlock": 132421220, "firstMintWib": "2026-11-08 23:03:06 WIB",
    "creator": "0x90e8b1c93c80758e2bd5032c7acec382501cb84b",
    "creationTx": "0x622352320dcdef7ad6ebb8d6ddb396bb99c89714b4b7fc8c9ba4a420ed95d350",
    "creationBlock": 130920098, "creationTimeUtc": "2026-10-31 20:21:22 UTC",
    "bscscanNote": "BscScan token page dibaca live browser run 2331 (00:11-00:25 WIB 9 Nov, via tab t3 sesudah Cloudflare gagal di t4): MAX TOTAL SUPPLY 691 VAMPIREVIBES (vs totalSupply 687 saat baca on-chain 23:57 WIB - +4 mint), holders 662, transfers 702. Deploy 31 Okt 2026 != launch: launch = first mint 8 Nov 23:03:06 WIB (umur terverifikasi).",
    "lastReadBlock": 132428482, "lastReadWib": "2026-11-08 23:57 WIB",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint VERIFIED on-chain: blok 132421220 = 2026-11-08 23:03:06 WIB (sweep 2 tahap: jendela [132422238, head] menemukan 132422915 (23:15:49) yang BUKAN first mint - radar #685 sudah tercapai ~23:10-23:15; sweep jendela awal [132413238, 132422237] menemukan first mint di chunk 132420238-132421237 = blok 132421220. Satu chunk sempat gagal koneksi Ankr, di-retry dengan sukses). Umur ~1 jam saat dibaca - TERVERIFIKASI <=48 jam.",
    "baselineNote": "STRONG LEAD dilaporkan sekali run 2331 sebagai GATE-BLOCKED (bukan kandidat): 3 kaki strong lead LOLOS (umur terverifikasi <=48 jam + free 659/675=97,6% + slot user terbuka), TAPI gate website GAGAL - TIDAK di-preview/TIDAK di-mint. Satu owner dengan FrankensteinFriends (0x90e8b1c93c80758e2bd5032c7acec382501cb84b, factory wave, bukan di same-owner-discards.json). Bila website terverifikasi kemudian -> jalur direct-mint strong lead; bila sold out / lewat umur / slot hilang -> laporkan sekali + hapus.",
    "gateNote": ("GATE website FAILED (metode A-N dicoba, run 2331): (A) raw contract-address search tanpa hasil; "
        "(B) Boltbook dibaca penuh tanpa tautan; (C) Sourcify source/metadata tanpa URL; (G) project-name search tanpa situs yang mencetak kontrak; "
        "(H) contractURI base64 on-chain JSON tanpa external_link; (I) tokenURI #1 base64 JSON (traits: Armor Vampire, Blade Plasma, Mask Hood, City Vibe) tanpa URL; "
        "(J) ABI tanpa fungsi situs; (K) GitHub code search tanpa hasil; (M) site: filters tanpa hit yang mencetak kontrak; "
        "(N) hop author-bio tidak bisa diselesaikan (tanpa tautan profil author); "
        "(L) BscScan token page via live browser (00:11-00:25 WIB 9 Nov): TIDAK ADA kolom Website/Social/Official Site - hanya 'Click here to update the token information'. "
        "X unverified (akun X opsional, tidak menggagalkan gate)."),
    "runNote2331_1108": "Run 2331: STRONG LEAD gate-blocked - dilaporkan sekali (gate FAILED, metode A-N, termasuk (L) BscScan tanpa website). TIDAK di-preview/di-mint.",
}

# finalize top-level notes
s["runNote2331_1108"] = (
    "Run 2331 (23:31 WIB 8 Nov - 00:42 WIB 9 Nov): re-read blok 132428482 (542 kontrak + 72 track_c, 0 batch_fail, 122 degraded - naik dari 40 di 2301, RPC degradasi); "
    "scan window 132427550-132428549 PARTIAL (pre-flight OK 12,9 dtk; 40 Ankr calls, 0 error; enrichment killed 700s timeout di 67/97, partial=true, 66 NFT + 273 ERC-20; 31 NFT window TIDAK ter-enrich - gap cakupan). "
    "Watermark TIDAK dimajukan (milik backfill; skipped gap 132422006-132427549). 5c: 10 baru dicek, 0 hit S1/S2 (semua Sourcify-unverified). "
    "Velocity strict: 20 lolos, 0 promosi. EARLY LEAD BARU: Lucky Cat (gate()=registry, free 5/2000, first mint 23:53:58 WIB) - dilaporkan sekali. "
    "STRONG LEADS gate-blocked: FrankensteinFriends (free 99,0%, first mint 23:02:21 WIB) + VampireVibes (free 97,6%, first mint 23:03:06 WIB) - "
    "3 kaki LOLOS, gate website FAILED metode A-N (termasuk (L) BscScan live browser 00:11-00:25 WIB 9 Nov: tanpa kolom website/social di kedua halaman; creator sama 0x90e8b1c93c80758e2bd5032c7acec382501cb84b; deploy 31 Okt 2026 != launch) - dilaporkan sekali, TIDAK di-preview/di-mint. "
    "Age-exclusion: 5 dihapus (AgentBox 83,2j; Data Synth 63,8j; Zero Genesis 63,7j; Cipher Mind 62,7j; Cyber Lynx 62,6j) - dilaporkan sekali. "
    "Vesperfang free pool SOLD OUT 773/773 + mint revert 0x788a686f terverifikasi (dicatat, bukan lead). "
    "Binanceai tetap refund phase. Bridge: 116 kontrak, 0 baru. 0 kandidat, 0 auto-mint.")
s["runNote2331_1108_triage_new"] = (
    "Triase parent: FrankensteinFriends 0xedfd9e65 (totalSupply 718, free 689/696=99,0%, slot user TERBUKA, AGENT gate=registry via ABI; "
    "first mint blok 132421120 = 2026-11-08 23:02:21 WIB, jendela awal [132411334,132420333] belum terverifikasi - dataseed -32005); "
    "VampireVibes 0xa5fb4e0e (totalSupply 687, free 659/675=97,6%, slot user TERBUKA; first mint blok 132421220 = 2026-11-08 23:03:06 WIB, sweep 2 tahap selesai); "
    "keduanya satu owner 0x90e8b1c93c80758e2bd5032c7acec382501cb84b (factory wave); gate website (A)(C)(G)(H)(I)(J)(K) tanpa hasil; "
    "(L) BscScan live browser 00:11-00:25 WIB 9 Nov: kedua halaman TANPA kolom website/social (hanya 'Click here to update the token information'); "
    "FF creation tx 0x99f312f9... block 130925876, 31 Okt 2026 21:04:42 UTC, MAX TOTAL SUPPLY 719, holders 690, transfers 727; "
    "VV creation tx 0x62235232... block 130920098, 31 Okt 2026 20:21:22 UTC, MAX TOTAL SUPPLY 691, holders 662, transfers 702. "
    "Gate FAILED untuk keduanya -> strong-lead gate-blocked, dilaporkan sekali, TIDAK di-preview/di-mint. "
    "BNBirds (unverified, free ~99,4% habis) + MiChan (unverified, flag DANGEROUS) dicatat bukan lead. OPEC dicatat bukan agent-shaped.")

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(s, f, indent=1)
print("snapshot saved; contracts now:", len(s["contracts"]))
print("FF/VV in snapshot:", "FrankensteinFriends" in s["contracts"], "VampireVibes" in s["contracts"])
print("DONE merge part 2")
