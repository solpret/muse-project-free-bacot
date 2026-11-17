#!/usr/bin/env python3
"""Merge run 2026-11-12 22:31 WIB into onchain-snapshot.json.
- AgcNFT: early -> STRONG LEAD (gate-blocked, reported once this run).
- SolNFT: velocity LOLOS run ini, 192/333 = 57,7% (tetap early watchlist).
- fa22: track_c -> excluded (free pool SOLD OUT 111/111).
- Steady 0x4919: ADD as early-lead-reported-2026-11-12.
- last_run_wib / last_run_note updated. Backup taken before write."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s = json.load(open(BASE + "onchain-snapshot.json"))

# --- AgcNFT: promote early -> strong lead (gate-blocked) ---
a = s["contracts"]["AgcNFT"]
a["status"] = "strong-lead-gate-blocked-2026-11-12"
a["totalMinted"] = 246
a["freeMinted"] = 246
a["freePctVerified"] = 73.8
a["lastReadBlock"] = 133186585
a["lastReadWib"] = "2026-11-12 22:59 WIB"
a["velocityVerified"] = False
a["runNote2231"] = ("Run 2231 (blok 133186585, ~22:59 WIB): freeMinted 246/333 = 73,8% "
  "(199 pukul 22:25 -> 246; +47 dalam ~34 mnt = 1,38/mnt vs rate sebelumnya 3,72/mnt = 0,37x -> velocity GAGAL). "
  "PROMOSI early->STRONG LEAD: umur terverifikasi via mintOpensAt 1794494012 = 21:33:32 WIB (<24 jam), "
  "free >70% terverifikasi on-chain, slot user terbuka (freeClaimed(user)=0, balanceOf(user)=0). "
  "X UNVERIFIED; GATE WEBSITE GAGAL (A 0-hit alamat kontrak; B Boltbook EN+ZH absen; C metadata Sourcify tanpa URL; "
  "G pencarian nama hanya AGC coin agcc.fun = same-name BUKAN linkage; I contractURI() revert/None; J tanpa fungsi site) "
  "-> dilapor sekali sebagai strong lead gate-blocked; TIDAK preview/mint.")

# --- SolNFT: velocity passes, still early watchlist ---
b = s["contracts"]["SolNFT"]
b["totalMinted"] = 192
b["freeMinted"] = 192
b["freePctVerified"] = 57.7
b["lastReadBlock"] = 133186585
b["lastReadWib"] = "2026-11-12 22:59 WIB"
b["velocityVerified"] = True
b["runNote2231"] = ("Run 2231 (blok 133186585, ~22:59 WIB): freeMinted 192/333 = 57,7% "
  "(71 pukul 22:25 -> 192; +121 dalam ~34 mnt = 3,56/mnt vs rate baseline pertama 1,48/mnt = 2,4x DAN >=20 token "
  "-> velocity LOLOS run ini). BUKAN strong lead (57,7% < 70%), BUKAN kandidat (X + gate UNVERIFIED) -> tetap early-lead watchlist. "
  "Umur terverifikasi via mintOpensAt 1794493918 = 21:31:58 WIB; slot user terbuka (freeClaimed(user)=0, balanceOf(user)=0).")

# --- fa22: sold out -> move track_c to excluded ---
fa = s["track_c"].pop("AgentGenesis-fa22", None)
assert fa is not None, "fa22 missing from track_c"
fa["status"] = "excluded-sold-out-free-pool-2026-11-12"
fa["soldOutNote"] = ("Run 2231 (blok 133186585, ~22:59 WIB): freeMinted 111/111 FREE_CAP = 100% "
  "(91/111 pukul 22:25 -> 111/111; totalMinted 111). Free pool HABIS. Lead gate-blocked yang dilaporkan run 2201 kini "
  "ditutup sebagai sold-out; dilaporkan sekali sebagai perubahan + dihapus dari track_c aktif. TIDAK pernah di-preview/di-mint.")
s.setdefault("excluded", {})["AgentGenesis-fa22"] = fa

# --- Steady 0x4919: new early lead ---
s["contracts"]["Steady"] = {
  "address": "0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
  "name": "Steady", "symbol": "STEADY", "kind": "ERC721",
  "status": "early-lead-reported-2026-11-12",
  "totalSupply": 181, "freeClaimed": 181, "FREE_SUPPLY": 555, "MAX_SUPPLY": 1111,
  "mintOpen": 1, "mintOpensAt": None,
  "freePctVerified": 32.6,
  "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
  "userSlotNote": "Slot TERBUKA: freeUsed(user)=0, mintedBy(user)=0, balanceOf(user)=0 (fast-batch run 2231, blok 133186585).",
  "firstSeenBlock": None, "firstSeenWib": "2026-11-12 ~22:18 WIB (hot-leg 2209, freeClaimed 13)",
  "sourcifyVerifiedAt": "2026-11-12T15:12:47Z",
  "lastReadBlock": 133186585, "lastReadWib": "2026-11-12 22:59 WIB",
  "xVerified": False, "velocityVerified": False,
  "launchNote": ("Umur UNVERIFIED: verifiedAt 22:12:47 WIB BUKAN launch time; mintStart/saleStart/mintOpensAt "
    "tidak ada view (None); koroborasi first-mint via getLogs GAGAL 2 jalur: Ankr 401 (outage sejak 9 Nov) + "
    "eth_getLogs publik bsc-dataseed mengembalikan 0 log dalam 10 chunk 1000-blok (kontrol OBFG yang pasti mint di jendela sama "
    "juga 0 log -> endpoint tidak menyajikan log, bukan bukti tidak ada mint)."),
  "baselineNote": ("EARLY lead dilaporkan sekali run 2231 (temuan feed Sourcify hot-leg 2209, S1 PASS: mint+quote+freeClaimed/freeMinted+agent ref; "
    "contractURI base64: 'Steady is 1111 Calm capybara... Mint is gated to .ai Agent ID holders'). "
    "Free 181/555 = 32,6% (13 pukul ~22:18 -> 181 pukul ~23:00, laju ~4,2/mnt). BUKAN strong lead (<70%), BUKAN kandidat (<50% + X + gate unverified). "
    "Website UNVERIFIED (A 0-hit alamat kontrak; C metadata Sourcify tanpa URL; G pencarian nama tanpa hit proyek; I contractURI tanpa external_url). "
    "Tidak pernah di-preview/di-mint (early lead)."),
  "gate": "website_unverified",
  "website": None,
}

# --- MECHA compact update ---
m = s["contracts"].get("MECHA")
if isinstance(m, dict):
    m["totalMinted"] = 1853
    m["freeClaimed"] = 1852
    m["lastReadBlock"] = 133185233
    m["runNote2231"] = ("Run 2231 (blok 133185233): totalMinted 1853 (+1 vs 2201), freeClaimed 1852/4444 = 41,7%, "
      "freeAvailable(user)=2; velocity GAGAL (+1 <20); umur + gate UNVERIFIED -> tetap watchlist-only EARLY.")

s["runNote2231"] = ("Run 2231 (jadwal 22:31 WIB, eksekusi ~22:31-23:10 WIB): 0 kandidat baru, 1 strong lead baru "
  "(AgcNFT promosi early->strong, gate-blocked), 1 early lead baru (Steady 0x4919), 1 track-C sold-out (fa22 111/111), "
  "0 track-B dibuka. Pre-flight FAIL (Ankr 401; outage sejak 9 Nov) - scan fast-fail, watermark TETAP 132512564; 5c dilewati. "
  "Feed 20 kontrak (verifiedAt 14:50:39-15:35:49Z), 1 baru vs hot-leg-seen (0x2239..., 44 fns, quote saja, BUKAN agent-shaped). "
  "Boltbook EN 44.927 byte (10 alamat) / ZH 43.236 byte (10 alamat), 0 baru. Bridge 116 kontrak, 0 not-in-snapshot, "
  "7 same-owner-discarded (STALE mtime 2026-11-08). Verify 35 target (blok 133185233, 403,1 dtk): 19 terbaca, 16 BATCH-FAIL "
  "(nilai lama dipertahankan, BUKAN nol). Fast-batch v2 (blok 133186585, 43,7 dtk): SolNFT/AgcNFT/fa22/NOTV-0415/0x4919 semua terbaca. "
  "BinanceLife 18 (tetap; deadline 23:29:05 WIB malam ini - run 23:01 bila masih 18/10000 + belum sold out -> age-excluded). "
  "binanceai launched 0 (klaim masih tutup). OBFG 412/1230 (33,5%, gate-blocked, tanpa perubahan). NOTV-0415 totalMinted 0 (belum dibuka). "
  "Sweep EN+ZH + leg 6 (Odaily/PANews 0 item): hanya proyek dikenal/diexclude; AgentLabs (platform eksperimen harian, tanpa kontrak) + "
  "Agent Operators (mint buka 15 Nov, tanpa kontrak) dicatat bukan lead. 0 eksekusi (tidak ada preview/mint).")
s["last_run_wib"] = "2026-11-12 22:31 WIB"
s["last_run_note"] = s["runNote2231"]
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; contracts:", len(s["contracts"]), "| track_c:", len(s["track_c"]), "| excluded:", len(s.get("excluded", {})))
print("fa22 in excluded:", "AgentGenesis-fa22" in s.get("excluded", {}))
print("Steady in contracts:", "Steady" in s["contracts"])
print("AgcNFT status:", s["contracts"]["AgcNFT"]["status"])
print("SolNFT status:", s["contracts"]["SolNFT"]["status"])
