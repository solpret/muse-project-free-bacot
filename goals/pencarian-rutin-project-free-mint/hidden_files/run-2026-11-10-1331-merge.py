#!/usr/bin/env python3
"""Merge run 1331 reread+vel into snapshot. Read-only wrt chain; writes snapshot + backup.
Main events: 3 new EARLY leads (Cinder Agents, Pickgrid Pickaxe, PanduAGENT Phase 2);
YAMA website gate FLIPS to VERIFIED but audit RISK hit blocks the mint (no preview, no execute);
Agent Radar Pass excluded sold-out. Does NOT re-report anything (reporting is the
parent run's final message)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1331"
BLOCK = 132724963
NOW = "2026-11-10 13:01 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1331-premerge")

updated = 0
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    row = vel.get("rows", {}).get(name, {})
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    if row.get("minted") is not None:
        entry["previousTotalSupply"] = row.get("prev")
        entry["mintedInInterval"] = row.get("minted")
        entry["intervalMinutes"] = 60.0
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote1331_1110"] = text

note("SEVENFOLD", "Run 1331 (blok 132724963): totalSupply 1579->1616 (+37, rate 0,617/mnt vs prev 0,85 = 0,73x) velocity GAGAL; freeMinted 1615/3000 = 53,8% (LEWAT 50% tapi velocity gagal -> BUKAN kandidat). Audit MORROW RISK tetap blokir; status strong-lead-reported-2026-11-10-audit-blocked dipertahankan, TIDAK dilaporkan ulang.")
note("Sakura", "Run 1331: totalSupply 1345->1349 (+4, 0,067/mnt, 0,21x) velocity GAGAL; freeMinted 1339/6000 = 22,3% (<25% strong-lead). Tetap early-lead watchlist-only; umur terverifikasi <=48 jam (first mint 01:47 WIB 10 Nov, deadline 2026-11-12 01:47 WIB); website unverified.")
note("THYRK", "Run 1331: totalSupply 3143->3255 (+112, rate 1,867/mnt vs prev 5,233 = 0,36x) velocity GAGAL; freeMinted 3194; bal_user=1 (sudah mint user 08:22 WIB). Slot user terpakai -> TIDAK ada aksi, bukan kandidat. Boltbook: mint(1) kini revert bahkan dari Agent-ID wallet (sim dingin).")
note("Rookling", "Run 1331: velocity LOLOS tapi status age-excluded-2026-11-06 -> TANPA promosi, tetap excluded dari kandidasi.")
note("Thetavox", "Run 1331: totalSupply 1325->1348 (+23, 0,383/mnt vs prev 0,083 = 4,62x) velocity LOLOS TAPI umur UNVERIFIED (Sourcify verifiedAt 2026-11-03, 7 hari lalu, BUKAN launch time; first-mint on-chain TERBLOKIR Ankr 401) + website UNVERIFIED -> TIDAK promosi, tetap watchlist-only-age-website-unverified.")
note("FCAT Agents", "Run 1331: totalSupply 435->439 (+4, 0,067/mnt, 0,29x) velocity GAGAL; freeClaimed 436/888 = 49,1%; umur UNVERIFIED, website null -> watchlist-only.")
note("JINCHAN Agents", "Run 1331: totalSupply 245->248 (+3, 0,05/mnt, 1,0x) velocity GAGAL; freeClaimed 245/888 = 27,6%; umur UNVERIFIED -> watchlist-only.")
note("Roguefall", "Run 1331: totalSupply 1144->1163 (+19, 0,317/mnt, 2,38x) velocity GAGAL (butuh >=20 token, hanya 19); freeMinted 1157/3000 = 38,6%; umur+website UNVERIFIED -> watchlist-only.")
note("SonoWaves", "Run 1331: totalSupply 185->191 (+6, 0,1/mnt, 0,26x) velocity GAGAL; freeMinted 191/6666 = 2,9% (Boltbook agata.ai recheck 12:57 WIB: freeMint() value 0 lolos sim 2 RPC, gate Agent ID — diskusi baru, BUKAN bukti umur). Umur tetap UNVERIFIED (first-mint on-chain TERBLOKIR Ankr 401) -> tetap watchlist-only-age-unverified, TANPA promosi.")
note("Moss Transmission", "Run 1331: totalSupply 207->221 (+14, 0,233/mnt) velocity GAGAL (baseline pertama, ratio None); free views tetap null; umur+free%+website UNVERIFIED -> watchlist-only, tanpa promosi.")
note("Neon Circuit", "Run 1331: totalSupply 367->372 (+5, 0,083/mnt) velocity GAGAL (baseline pertama); free views tetap null; umur+free% UNVERIFIED -> watchlist-only, tanpa promosi.")
note("HIVE Agents", "Run 1331: totalSupply 1259->1259 (blok 132724963, +0) velocity GAGAL; free=None/1000; bal_user=1; status minted-by-user-2026-11-02.")
note("Bubblebruin", "Run 1331: totalSupply 2395->2395 (+0) velocity GAGAL; freeClaimed 2389/7777 = 30,7%; bal_user=1; status minted-by-user-2026-11-01.")
note("Zapcourier", "Run 1331: totalSupply 715->715 (+0) velocity GAGAL; free=712/712 (pool habis); bal_user=1; status minted-by-user-2026-11-02.")

# track_c updates
tc_updated = 0
for k, v in snap.get("track_c", {}).items():
    if not isinstance(v, dict):
        continue
    f = rr.get("track_c", {}).get(k)
    if not f:
        continue
    for key in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if f.get(key) is not None:
            v[key] = f[key]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW
    tc_updated += 1

nusa = snap["track_c"].get("NUSA")
if isinstance(nusa, dict):
    nusa["runNote1331"] = ("Run 1331: freeMinted 365->367/560 (+2, ~30 mnt); freeClaimed(user)=0; gate website TETAP FAILED. "
        "Umur: first mint 2026-11-08 17:05 WIB -> deadline 48 jam 2026-11-10 17:05 WIB (~3,9 jam dari run ini). "
        "TIDAK preview/mint, TIDAK dilaporkan ulang; bila gate tetap gagal sampai deadline -> age-exclude + lapor sekali.")
bome = snap["track_c"].get("BOME-50CD")
if isinstance(bome, dict):
    bome["runNote1331"] = ("Run 1331: totalSupply tidak berubah; mintOpen=0 (sale BELUM dibuka). Tetap watchlist-only-not-open; TIDAK preview/mint.")
vision = snap["track_c"].get("VISION")
if isinstance(vision, dict):
    vision["runNote1331"] = ("Run 1331: totalSupply token 2,52e27 -> 2,5416e27 (+~21,6 share setara); status watchlist-only-age-unverified-2026-11-10 dipertahankan; "
        "sweep AirdropBuzz 9 Nov (182 share saat cek) sudah lama, tanpa perubahan status.")

# YAMA: gate flips VERIFIED, audit RISK blocks execution
yama = snap["track_c"].get("YAMA")
if isinstance(yama, dict):
    yama["websiteGate"] = "VERIFIED run 1331"
    yama["website"] = "https://yamaproject.pages.dev"
    yama["websiteNote"] = ("GATE website LOLOS run 1331 (methods M/G + H/J): AirdropBuzz 'Binance Agent ID' guide (verified 9 Nov) menautkan 'YAMA PROJECT' -> "
        "yamaproject.pages.dev; situs HTTP 200 mencetak kontrak sale persis 0x86D779fc4d83044cCECCb53639f9a98E367D6E46 (2x) + token persis "
        "0xa84EA20a667B3b1859aB9a9984FF5F03D8688aE2 (1x) di index + /skill.md (6.607 B). contractURI() sale+token = None (method H kosong); "
        "ABI grep sale (32 fns) + token (12 fns) tanpa fungsi URL (method J kosong). Gate FAILED 2026-11-09 (methods A/C/G) kini TERBALIK oleh bukti situs ini.")
    yama["auditNote"] = ("Audit Binance run 1331 (fresh): SALE 0x86d779fc... hasResult=false (TIDAK ADA HASIL, bukan pass; code 000000, riskLevel -1, riskAlert null, 0 hit) — "
        "disimpan di audit-1331-yama-86d779.json. TOKEN 0xa84ea20a... hasResult=true, riskLevel 2 LOW, riskAlert null, buy/sell tax 0.0, isVerified true — "
        "NAMUN 1 hit RISK: 'Contract Not Renounced' (isHit=true, riskType=RISK; creator masih pegang kontrol, bisa ubah parameter seperti buy-sell tax) + "
        "1 CAUTION: 'Mintable Detected'. Disimpan di audit-1331-yama-a84ea2.json. TIDAK ADA preseden mint lolos dengan hit RISK (LUCKY777/BITCAT/DRIFTWIRE semua 0 hit RISK).")
    yama["freshRead1331"] = ("Fresh on-chain run 1331 (run-2026-11-10-1331-yama-fresh.py, blok ~132725xxx): quote(user,1)=(1 free share, 0 BNB); freeUsed(user)=false; "
        "sharesOf(user)=0; quotaOf(user)=10; isAgent(user)=1; totalFreeShares 2531, totalPaidShares 1, totalShares 2532, MAX_SHARES 100000 (pool ~97.468 free tersisa); "
        "TOKENS_PER_SHARE 1.000.000; PRICE 0,001 BNB (jalur berbayar); liquidityTargetReached=false; agentIdRegistry = registry resmi; token() cocok; "
        "saldo YAMA user sebelum = 0. Owner/devWallet/treasury/vault TIDAK ada di same-owner-discards.json.")
    yama["status"] = "lead-reported-audit-blocked-2026-11-10"
    yama["blockedNote1331"] = ("STOP run 1331 — TIDAK preview, TIDAK mint: audit token 1 hit RISK 'Contract Not Renounced' (aturan: specific RISK hit = STOP + tanya user). "
        "Semua kaki lain LOLOS (gate website kini terverifikasi, pool + slot + umur + diskusi terverifikasi, quote 0). "
        "Risiko tambahan tercatat (AirdropBuzz 9 Nov): vault owner bisa menarik BNB yang diniatkan untuk likuiditas; liquidityTargetReached=false. "
        "Dilaporkan sekali run ini sebagai perubahan status (gate lolos + audit blokir). TIDAK dilaporkan ulang kecuali audit berubah / user override eksplisit.")
    yama["lastReadBlock"] = BLOCK
    yama["lastReadWib"] = NOW

# binanceai (track-B pending, refund/failed) — fresh read this run
snap["runNote1331_binanceai"] = ("Run 1331 (blok 132727420): binanceai TETAP fase refund/failed (launched=0, failed=1, isRefundPhase=1, totalShares 3110, "
    "tokenClaimed_user=0, saldo TOKEN user 0) — IDENTIK dengan verifikasi terakhir run 1931 2026-11-09. SUDAH dilaporkan sekali - TIDAK dilaporkan ulang.")
snap["runNote1331_grove"] = ("Run 1331 Agent Grove fase 2 watch (blok 132727412): freeOpen=0, freeClaimed(user)=false — tidak berubah; fase 2 belum dibuka.")

# bridge diff (complementary leg)
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
    snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    new_bridge = [a for a in bcontracts if a.lower() not in snap_addrs]
    snap["runNote1331_bridge"] = (f"Run 1331 bridge: {len(bcontracts)} kontrak, {len(new_bridge)} belum di snapshot — 0 baru vs run 1231; "
        "0 promosi (tidak ada yang memenuhi tier).")
except Exception as e:
    snap["runNote1331_bridge"] = f"Run 1331 bridge: baca gagal ({e}); lanjut normal, bridge tidak menggagalkan run."

# new EARLY leads (first-seen this run, agent-shaped, first mints verified on-chain)
snap["contracts"]["Cinder Agents"] = {
    "address": "0x49966cf050a5a9cedd252184875267c0e93dbc00",
    "status": "early-lead-reported-2026-11-10",
    "name": "Cinder Agents", "symbol": "CINDER", "kind": "ERC721",
    "totalSupply": 213, "totalMinted": 213, "freeMinted": 82, "paidMinted": 0,
    "FREE_SUPPLY": 500, "MAX_SUPPLY": 3131,
    "freePctVerified": 16.4,
    "balanceOf_user": 0, "freeClaimed_user": None,
    "owner": "0xc65891d2f7c5d10672bfbd94a78a6a5ec50ac54a", "ownerInDiscards": False,
    "agentRegistry": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "sourcify": "exact_match", "sourcifyVerifiedAt": "2026-11-10T03:11:12Z",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "source": "Boltbook front page EN+ZH run 1331 (post eth45k.ai 'Cinder Agents 204 — freeMinted 73/500, PoW gate', ~12:5x WIB; rujukan post hooya.ai di 175) + verifikasi on-chain run ini",
    "launchNote": ("UMUR UNVERIFIED: tidak ada stated launch time proyek; first-mint on-chain TERBLOKIR (Ankr 401); Sourcify verifiedAt 2026-11-10T03:11:12Z "
        "(10:11 WIB) BUKAN launch time. Pertama terlihat job ini run 1331 (totalSupply 213 saat baca; post Boltbook menyebut 175 lalu 204 sebelumnya)."),
    "websiteNote": "GATE website BELUM DINILAI (early lead; umur+free% belum cukup untuk strong lead). Bila promosi mendekat, gate wajib dinilai penuh (methods A-N) sebelum preview/mint apa pun.",
    "baselineNote": ("EARLY LEAD run 1331: agent-shaped TERVERIFIKASI (registry() = registry Agent ID resmi + bytecode mengandung alamat registry; Sourcify exact_match; "
        "mintFree(nonce) + PoW gate SHA-256(seedFor(wallet):nonce) + verifyProof); freeMinted 82/500 = 16,4% TERVERIFIKASI (paidMinted 0); "
        "totalSupply 213 (naik dari 204 di post Boltbook — minting berjalan); owner 0xc658... BUKAN discards; slot user: balanceOf=0 (freeClaimed(user) view tidak ada — slot UNVERIFIED). "
        "BUKAN strong lead (free% 16,4% < 25% + umur unverified). TIDAK pernah preview/mint. Promosi hanya bila 3 kaki strong lead terpenuhi + website terverifikasi."),
    "velocityVerified": False, "xVerified": False,
}
snap["contracts"]["Pickgrid Pickaxe"] = {
    "address": "0x7f541bcc33abed0e64455565da723e949c6f76f0",
    "status": "early-lead-reported-2026-11-10",
    "name": "Pickgrid Pickaxe", "symbol": "PICKAXE", "kind": "ERC721",
    "totalSupply": 90, "totalMinted": None, "freeMinted": 90, "paidMinted": 0,
    "FREE_SUPPLY": None, "MAX_SUPPLY": None,
    "freePctVerified": None,
    "balanceOf_user": 0, "freeClaimed_user": None,
    "owner": "0x72d0d1c285c5aea222e618924410ee3ffd6b28a4", "ownerInDiscards": False,
    "agentRegistry": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "sourcify": "exact_match", "sourcifyVerifiedAt": "2026-11-10T03:29:23Z",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "source": "Boltbook front page EN+ZH run 1331 (post mbtc100k.ai 'Pickgrid Pickaxe 45/300 — +18, receipt-verified mint', ~12:5x WIB; rujukan post riery.ai di 27) + verifikasi on-chain run ini",
    "launchNote": ("UMUR UNVERIFIED: tidak ada stated launch time proyek; first-mint on-chain TERBLOKIR (Ankr 401); Sourcify verifiedAt 2026-11-10T03:29:23Z "
        "(10:29 WIB) BUKAN launch time. Pertama terlihat job ini run 1331 (totalSupply 90 saat baca; post Boltbook menyebut 27 lalu 45 sebelumnya)."),
    "websiteNote": "GATE website BELUM DINILAI (early lead). Bila promosi mendekat, gate wajib dinilai penuh (methods A-N) sebelum preview/mint apa pun.",
    "baselineNote": ("EARLY LEAD run 1331: agent-shaped TERVERIFIKASI (agentRegistry() = registry Agent ID resmi; Sourcify exact_match; freeMint(agentId)); "
        "freeMinted 90 = totalSupply 90 (semua mint sejauh ini gratis, paidMinted 0); FREE_SUPPLY tidak terbaca (view null) -> free% UNVERIFIED "
        "(klaim Boltbook '45/300' memakai total 300 sebagai MAX, bukan free cap terverifikasi — tidak dipakai sebagai free%); "
        "owner 0x72d0... BUKAN discards; slot user: balanceOf=0 (freeClaimed(user) view tidak ada — slot UNVERIFIED). "
        "BUKAN strong lead (free%+umur unverified). TIDAK pernah preview/mint."),
    "velocityVerified": False, "xVerified": False,
}
snap["contracts"]["PanduAGENT Phase 2"] = {
    "address": "0x9e5dd59b5df1d36de02454a1fd6d77ee5b07778b",
    "status": "early-lead-reported-2026-11-10",
    "name": "PanduAGENT Phase 2", "symbol": "PANDU2", "kind": "ERC721",
    "totalSupply": 154, "totalMinted": 154, "freeMinted": 154, "paidMinted": 0,
    "FREE_SUPPLY": None, "MAX_SUPPLY": 2222,
    "FREE_PER_WALLET": 1, "MAX_PER_WALLET": 5, "mintOpen": 1,
    "freePctVerified": None,
    "balanceOf_user": 0, "freeClaimed_user": None,
    "owner": "0x36f3d56ead5d1d6c2434f94defcef732c5c3cbd2", "ownerInDiscards": False,
    "sourcify": "UNVERIFIED (404)",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "source": "Boltbook front page EN+ZH run 1331 (post raca.ai 'PanduAGENT Phase 2: 133/2,222, semua gratis, paid 0, source unverified', ~12:5x WIB, blok 132724510) + verifikasi on-chain run ini",
    "launchNote": ("UMUR UNVERIFIED: tidak ada stated launch time proyek; first-mint on-chain TERBLOKIR (Ankr 401); Sourcify UNVERIFIED (tidak ada verifiedAt). "
        "Pertama terlihat job ini run 1331 (totalSupply 154 saat baca; post Boltbook menyebut 133 di blok 132724510). Phase 2 adalah deploy baru, BUKAN Phase 1 yang sold out (0x4AB4...cd64)."),
    "websiteNote": "GATE website BELUM DINILAI (early lead). Bila promosi mendekat, gate wajib dinilai penuh (methods A-N) sebelum preview/mint apa pun.",
    "baselineNote": ("EARLY LEAD run 1331: agent-shaped TERVERIFIKASI via bytecode (runtime code mengandung alamat registry Agent ID resmi 0x60B926...; "
        "getter agentRegistry()/registry() tidak ada — BUKAN bukti tidak ada, bytecode adalah bukti konkret) + live free views (freeMinted 154, paidMinted 0, "
        "FREE_PER_WALLET 1, mintOpen 1); Sourcify UNVERIFIED — bentuk dicatat apa adanya, bukan dianggap verified. "
        "freeMinted 154/2222 MAX_SUPPLY = 6,9% hanya INFERENSI vs MAX (free cap terpisah tidak terbaca) -> free% UNVERIFIED; "
        "owner 0x36f3... BUKAN discards; slot user: balanceOf=0 (freeClaimed(user) view tidak ada — slot UNVERIFIED). "
        "BUKAN strong lead (free%+umur unverified). TIDAK pernah preview/mint."),
    "velocityVerified": False, "xVerified": False,
}

# Agent Radar Pass -> excluded (sold out, verified on-chain this run)
ex = snap.setdefault("excluded", {})
ex["Agent Radar Pass"] = {
    "address": "0x0CE20E838CDa5f6ccc8A59ef78Bc0E9bF4628d89",
    "reason": "sold-out-2026-11-10",
    "note": ("Run 1331 (sweep web): MintRadar 'Agent Radar Pass' — soulbound, 1 per Agent ID, 2.222 ever; jendela mint 01 Nov 13:00 UTC -> 08 Nov 13:00 UTC "
        "(SUDAH TUTUP); totalSupply on-chain 2222/2222 = HABIS. Tidak pernah dilaporkan sebagai lead (sold out sebelum sempat dipromosikan)."),
    "excludedWib": NOW,
}

# run-level notes
snap["runNote1331_1110"] = ("Run 1331 (2026-11-10 13:01 WIB, blok 132724963, interval 60 mnt vs run 1231): re-read 648 kontrak + 75 track_c (639,7 dtk). "
    "Velocity LOLOS: ['Rookling', 'Thetavox'] — tanpa promosi (Rookling age-excluded; Thetavox umur+website UNVERIFIED). "
    "EARLY LEAD BARU 3 (Boltbook): Cinder Agents (free 82/500=16,4%), Pickgrid Pickaxe (free 90, free% unverified), PanduAGENT Phase 2 (free 154, free% unverified) — semua agent-shaped, pertama terlihat run ini, TIDAK pernah preview/mint. "
    "YAMA: gate website LOLOS (yamaproject.pages.dev mencetak sale+token persis) TAPI audit token 1 hit RISK 'Contract Not Renounced' -> STOP, TIDAK preview/mint, lapor sekali. "
    "NOVA AGENT: sudah age-excluded run 0601 (first mint 2026-11-02) — post Boltbook baru hanya mint lanjutan, bukan temuan baru. "
    "Pixel Relay: PAID-ONLY (price 0,00008 BNB, ABI tanpa fungsi free) -> bukan lead. Binance Fleet Genesis sold out 1000/1000 -> bukan lead. "
    "Agent Radar Pass excluded sold-out 2222/2222 (jendela tutup 08 Nov). Feed Sourcify 20/20 dicek, 0 S1/0 S2 (1 near-miss 0x9feb...: mint+quote+free views tapi tanpa agent_ref). "
    "Boltbook EN 48.067 B / ZH 48.049 B. Ankr 401 fast-fail (preflight 8,0 dtk, head 132725010); watermark tetap 132512564; gap ~212.446 blok. "
    "Scan leg GAGAL CEPAT; 5c: tanpa output scan baru -> 0 dicek run ini. Sweep web: VISION/AGENT MAO sudah di snapshot (tanpa perubahan); Square/Odaily/PANews 0 baru. "
    "Kandidat baru 0; strong lead baru 0; early lead baru 3; track-C lead/kandidat baru 0; sellout baru 1 (Agent Radar Pass).")
snap["runNote1331_1110_scan"] = ("Run 1331 scan: PRE-FLIGHT GAGAL (Ankr 401 Unauthorized, 8,0 dtk, head 132725010) — outage Ankr sejak 2026-11-09 ~13:33 WIB BERLANJUT. "
    "Scan leg FAST-FAIL per amandemen 2026-11-06; watermark TETAP 132512564; gap ke head ~212.446 blok (backfill OFF atas perintah user).")
snap["runNote1331_1110_discovery"] = ("Run 1331 discovery (routes 2/3/5a/6): Boltbook EN+ZH front page — Cinder Agents + Pickgrid Pickaxe + PanduAGENT Phase 2 (EARLY lead baru, 3x); "
    "NOVA AGENT (age-excluded run 0601, bukan baru); Pixel Relay (paid-only, ABI tanpa free fn); Binance Fleet Genesis (sold out 1000/1000); "
    "SonoWaves (diskusi baru agata.ai, umur tetap UNVERIFIED); THYRK/LUCKY777/SEVENFOLD/Roguefall/Roninagent/Brinedroid (sudah di snapshot, tanpa promosi); "
    "YAMA (post lloyd.ai: 2.516 claimed; gate kini terverifikasi via yamaproject.pages.dev — lihat blockedNote1331). "
    "BoltRewards 0x8269ea16... adalah link footer Boltbook (token BOLT), bukan proyek mint. Chip404 0xa98b... adalah market contract, bukan mint. "
    "Hash21 0xfdb8... adalah tx hash klaim, bukan kontrak. Sourcify feed 20 -> 0 S1/0 S2. Sweep web: VISION + AGENT MAO sudah di snapshot; Agent Radar Pass sold out -> excluded; "
    "AirdropBuzz YAMA docs -> gate YAMA terverifikasi. Square/Odaily (0 flash Agent ID)/PANews (0 mention) 0 baru. twitterapi.io tidak pernah dipanggil.")
snap["runNote1331_1110_5c"] = ("Run 1331 5c: scan leg fast-fail (Ankr 401) -> TIDAK ADA output scan baru -> 0 ERC-20 baru dicek run ini (bukan 0 hasil shape-check; "
    "tidak ada backlog baru). track-c-scan-checked.json tidak berubah.")
snap["runNote1331_1110_age_exclusions"] = ("Run 1331 age-exclusion sweep: TIDAK ADA exclusion baru. Deadline terdekat: NUSA 2026-11-10 17:05 WIB (~3,9 jam lagi, gate tetap FAILED); "
    "SEVENFOLD deadline 2026-11-12 07:33 WIB; Sakura deadline 2026-11-12 01:47 WIB; DRIFTWIRE deadline 2026-11-12 09:37 WIB (sudah minted). "
    "Item lama dengan firstMintWib >48 jam (King's Game, Jinli, 0xf710..., 0xAAEF..., 0x5Ba4...) TIDAK di-exclude: first-mint di sana adalah lower bound / launch UNVERIFIED, "
    "dan exclusion butuh umur TERVERIFIKASI >48 jam (preseden Rose Genesis run 1231).")
snap["last_run_wib"] = NOW
snap["last_run_block"] = BLOCK
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: contracts updated={updated} track_c updated={tc_updated} total contracts={len(snap['contracts'])} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',{}))}")
