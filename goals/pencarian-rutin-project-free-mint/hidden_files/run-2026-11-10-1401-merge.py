#!/usr/bin/env python3
"""Merge run 1401 reread+vel into snapshot. Read-only wrt chain; writes snapshot + backup.
Main events: ELSY AGENT strong-lead DIRECT MINT (2 NFTs #880/#881, tx verified);
Arcane Stones EARLY lead baru; Orbit Atlas watchlist-only-unverified;
Hakuna Agent already-triaged (not agent-shaped, Nov 7) - log only.
Does NOT re-report anything (reporting is the parent run's final message)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1401"
BLOCK = 132733154
NOW = "2026-11-10 14:01 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1401-premerge")

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
        e["runNote1401_1110"] = text

def dyn_note(name, extra=""):
    row = vel.get("rows", {}).get(name, {})
    f = rr.get("reread", {}).get(name, {})
    e = snap["contracts"].get(name, {})
    if not row:
        return None
    minted = row.get("minted"); rate = row.get("rate"); ratio = row.get("ratio")
    passes = row.get("passes")
    fm = f.get("freeMinted"); fc = f.get("freeClaimed")
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP") or e.get("MAX_SUPPLY")
    freetxt = ""
    if fm is not None and cap:
        freetxt = f"; freeMinted {fm}/{cap} = {fm/cap*100:.1f}%"
    elif fc is not None and cap:
        freetxt = f"; freeClaimed {fc}/{cap} = {fc/cap*100:.1f}%"
    vtxt = "velocity LOLOS" if passes else "velocity GAGAL"
    return (f"Run 1401 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra}")

for n in ["HIVE Agents", "Bubblebruin", "Zapcourier", "SEVENFOLD", "Sakura", "THYRK",
          "Cinder Agents", "Pickgrid Pickaxe", "PanduAGENT Phase 2", "Forge Pass",
          "Lucky Moments (LUMO)", "AgenticGangsterNFT", "Rose Genesis", "DRIFTWIRE",
          "FCAT Agents", "JINCHAN Agents", "Roguefall", "Thetavox", "Rookling"]:
    t = dyn_note(n)
    if t:
        note(n, t)

note("SEVENFOLD", (dyn_note("SEVENFOLD") or "") +
     " Audit MORROW RISK tetap blokir; BUKAN kandidat (velocity gagal). Status strong-lead-reported-2026-11-10-audit-blocked dipertahankan.")
note("Rose Genesis", (dyn_note("Rose Genesis") or "") +
     " TANPA promosi: umur UNVERIFIED + free path UNVERIFIED (tanpa free views) + xVerified false -> tetap watchlist-only-mature-newly-noticed.")
note("DRIFTWIRE", (dyn_note("DRIFTWIRE") or "") +
     " Sudah minted-by-user (#745 run 1231) -> velocity lolos tidak relevan, TANPA promosi.")
note("Cinder Agents", (dyn_note("Cinder Agents") or "") +
     " Tetap early lead (free% 18,4% <25% + umur unverified + website belum dinilai).")
note("Pickgrid Pickaxe", (dyn_note("Pickgrid Pickaxe") or "") +
     " Kaki strong lead 2/3 (free% 41,3% + slot terbuka) tapi umur TETAP UNVERIFIED -> MASIH early lead.")
note("AgenticGangsterNFT", (dyn_note("AgenticGangsterNFT") or "") +
     " Free 62,2% tapi umur UNVERIFIED + freeMint() butuh EIP-712 challenge server -> tetap watchlist-only-age-unverified.")
note("Forge Pass", (dyn_note("Forge Pass") or "") +
     " Baseline velocity pertama (ratio None). Tetap early lead (umur+website UNVERIFIED; owner pegang withdraw/setForgeToken).")
note("Lucky Moments (LUMO)", (dyn_note("Lucky Moments (LUMO)") or "") +
     " Tetap early lead; claimFree butuh izin EIP-712 server (gateSigner) -> agen TIDAK BISA klaim.")

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
    nusa["runNote1401"] = ("Run 1401: freeMinted 369->370/560 (+1); freeClaimed(user)=0; gate website TETAP FAILED. "
        "Umur: first mint 2026-11-08 17:05 WIB -> deadline 48 jam 2026-11-10 17:05 WIB (~2,5 jam dari run ini). "
        "TIDAK preview/mint, TIDAK dilaporkan ulang; bila gate tetap gagal sampai deadline -> age-exclude + lapor sekali.")
yama = snap["track_c"].get("YAMA")
if isinstance(yama, dict):
    yama["runNote1401"] = ("Run 1401: baca ulang track_c GAGAL lagi (semua field null, seperti run 1331) — status lead-reported-audit-blocked-2026-11-10 "
        "dipertahankan, tanpa perubahan. Audit token 1 hit RISK 'Contract Not Renounced' tetap blokir; deadline umur ~15:18 WIB hari ini "
        "(bila lewat tanpa mint -> age-exclude + lapor sekali). TIDAK preview/mint.")
    yama["lastReadBlock"] = BLOCK
    yama["lastReadWib"] = NOW

# ELSY AGENT — strong-lead DIRECT MINT (executed this run)
snap["contracts"]["ELSY AGENT"] = {
    "address": "0x9e2c16ee581e0d4f0a36ae70205c5599bbb9b22f",
    "status": "minted-by-user-2026-11-10",
    "name": "ELSY AGENT", "symbol": "ELSY", "kind": "ERC721",
    "totalSupply": 881, "totalMinted": None, "freeMinted": 881, "paidMinted": None,
    "FREE_SUPPLY": 1111, "MAX_SUPPLY": 3333,
    "FREE_PER_WALLET": 2, "MAX_PER_WALLET": 10, "mintOpen": 1,
    "freePctVerified": 75.2,
    "balanceOf_user": 2, "freeClaimed_user": None,
    "freeMintedByWallet_user": 2, "mintedByWallet_user": 2,
    "owner": "0xc6805e05b6f1babda47da1cac5f04ec02d6b8c1a", "ownerInDiscards": False,
    "agentRegistry": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "sourcify": "exact_match", "sourcifyVerifiedAt": "2026-11-10T05:44:28Z",
    "lastReadBlock": 132736572, "lastReadWib": "2026-11-10 14:47 WIB",
    "mintTx": "0xdb09e20fc92089fdbdf6dab6f09a1d22b7f268b960562098a183a0045bdd3a88",
    "mintBlock": 132736572, "mintGas": 163553,
    "mintOrderId": "26111000002031038322",
    "previewRequestId": "345869aed7204b27aca3b72cf89d10a2",
    "mintTokenIds": [880, 881],
    "mintQty": 2,
    "source": "Boltbook front page run 1401 (post bunnysuny.ai 'ELSY AGENT: 747 minted in 70 minutes, free tier 747/1,111', 05:40 UTC launch; + drhmwt.ai 813/3333 + grandtheftauto6.ai 813/3333) + verifikasi on-chain run ini",
    "launchNote": ("UMUR TERVERIFIKASI <=48 jam: launch dinyatakan 05:40 UTC = 12:40 WIB 2026-11-10 (post bunnysuny.ai 'New Agent-ID mint at 05:40 UTC, verified source'); "
        "hot-leg pertama melihat kontrak 12:39:38 WIB; Sourcify verifiedAt 12:44:28 WIB; totalSupply 747 di blok 132,731,614. Umur ~2 jam saat mint. "
        "Deployment-block proof TIDAK tersedia: eth_getCode historis gagal 'missing trie node' (-32000) di semua RPC (tanpa archive state); "
        "first-mint Transfer juga tak terverifikasi (eth_getLogs -32005). Batasan ini dicatat, bukan disembunyikan."),
    "website": "https://elsy-agent.surge.sh/",
    "websiteNote": ("GATE website TERVERIFIKASI run 1401 via method (I) tokenURI: tokenURI(1) = https://elsy-agent.surge.sh/1.json; "
        "situs HTTP 200 (9.404 B) berjudul 'ELSY AGENT — Mint' dan mencetak kontrak ELSY persis 0x9e2c16ee581e0d4f0a36ae70205c5599bbb9b22f. "
        "Metode lain: (A) pencarian alamat/nama tanpa situs lain; (G) site: pages.dev/vercel.app/deed.page tanpa hasil; (J) ABI tanpa fungsi URL; (H) contractURI() kosong."),
    "auditNote": ("Audit Binance run 1401 (fresh, audit-1401-elsy-9e2c.json): hasResult=false (TIDAK ADA HASIL, bukan pass; code 000000, riskLevel -1, riskAlert null) — "
        "diungkap sebagai tidak ada hasil. Tidak ada hit RISK. Sesuai otorisasi strong-lead direct mint + perluasan 2026-11-03, hasResult=false bukan penghambat."),
    "baselineNote": ("STRONG LEAD -> DIRECT MINT run 1401 (otorisasi user 2026-11-02): umur terverifikasi <=48 jam (~2 jam) + free 835/1111 = 75,2% TERVERIFIKASI "
        "(freeLeft 276) + slot user terbuka (hasAgentId=1, freeMintedByWallet=0, freeQtyFor(user,2)=2, quote(user,2)=0) + website TERVERIFIKASI + audit diungkap + preview bersih. "
        "Preview: simulationCode 000000000, tanpa error, value 0, tanpa authority/allowance/risk, balance change +2 NFT (#880 0x36e + #881 0x36f simulasi). "
        "Eksekusi mint(2) value 0: receipt status 1, blok 132736572, gas 163553; token aktual #880 + #881 (preview-simulasi #878/#879 sudah kedaluwarsa karena minter lain — token aktual dibuktikan dari log Transfer receipt). "
        "ownerOf(880)=ownerOf(881)=wallet agent; balanceOf=2; freeMintedByWallet=2; freeLeft 230 pasca-mint. GRATIS (gas saja)."),
    "rarityNote": ("Rarity pasca-mint (metadata proyek sendiri, verbatim): #880 Variant 'Forest', Pattern 'Chevron', Style 'Retro'; "
        "#881 Variant 'Ember', Pattern 'Chevron', Style 'Retro'. TIDAK ADA trait Rarity/Tier -> tier NOT VERIFIED, tidak dibuat-buat. Tercatat di nft-rarity-inventory.md."),
    "marketNote": ("Market pasca-mint: situs proyek HANYA halaman mint (tanpa seksi market/list/floor, tanpa market contract) -> own market TIDAK live terverifikasi -> "
        "TIDAK di-auto-list. Element sebagai fallback TIDAK bisa dieksekusi otomatis (butuh connect manual wallet user + API key) — detail listing manual disiapkan di laporan: "
        "kontrak 0x9e2c16ee581e0d4f0a36ae70205c5599bbb9b22f, token #880 + #881. TIDAK diklaim ter-listing."),
    "velocityVerified": False, "xVerified": False,
}

# Arcane Stones — EARLY lead baru
snap["contracts"]["Arcane Stones"] = {
    "address": "0x23f3De28E55C392F24A217B2B1602C90e0292f35",
    "status": "early-lead-reported-2026-11-10",
    "name": "Arcane Stones", "symbol": None, "kind": "ERC721",
    "totalSupply": 355, "totalMinted": None, "freeMinted": None, "paidMinted": None,
    "FREE_SUPPLY": None, "MAX_SUPPLY": 4111,
    "freePctVerified": None,
    "balanceOf_user": 0, "freeClaimed_user": None,
    "owner": "0x68bc72e819d0e3058c35f1f78169f91906d3d5fa", "ownerInDiscards": False,
    "marketAddress": "0x85e624e0C10A04619351fc5277F1D81c80707517",
    "marketMinPrice": 500000000000000,
    "agentRegistry": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "sourcify": "UNVERIFIED (404)",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "source": "Boltbook front page run 1401 (post ghoffar26.ai 'Arcane Stones — Mint Update: 248/4,111', ~14:3x WIB, menautkan https://arcanestones.pages.dev/) + verifikasi on-chain run ini",
    "launchNote": ("UMUR UNVERIFIED: tidak ada stated launch time proyek; tidak ada mintStart/freeStart view; Sourcify UNVERIFIED (tidak ada verifiedAt); "
        "first-mint on-chain TERBLOKIR (Ankr 401 + eth_getLogs -32005). Pertama terlihat job ini run 1401 (totalSupply 355 saat baca; post Boltbook menyebut 248 ~10 mnt sebelumnya — minting berjalan cepat, +107/10 mnt)."),
    "website": "https://arcanestones.pages.dev/",
    "websiteNote": ("GATE website TERVERIFIKASI run 1401: situs HTTP 200 + /config.js (10.784 B) mencetak kontrak NFT persis 0x23f3De28E55C392F24A217B2B1602C90e0292f35 + "
        "market persis 0x85e624e0C10A04619351fc5277F1D81c80707517 + registry resmi. Situs menyatakan 'free mint, gas only, 1 per Agent ID, no presale, no team allocation'."),
    "baselineNote": ("EARLY LEAD run 1401: agent-shaped TERVERIFIKASI via bytecode (eth_getCode 9.281 byte mengandung alamat registry Agent ID resmi) + site config.js; "
        "Sourcify UNVERIFIED — dicatat apa adanya. mint() no-arg nonpayable (ABI situs) = jalur gratis; free% INFERENSI 355/4111 = 8,6% (seluruh koleksi gratis per situs; tanpa free counter view) -> di bawah 25% strong lead. "
        "Slot user TERBUKA (mintedByAgentId(user tokenId)=0, balanceOf=0). Owner BUKAN discards. Tier on-chain: tierOf() Common 60% / Rare 25% / Epic 10% / Legendary 5% (reveal setelah sold out). "
        "Own market ADA di situs (MIN_PRICE 0,0005 BNB) — relevan bila nanti ter-mint. BUKAN strong lead (free% <25% + umur unverified). TIDAK pernah preview/mint."),
    "velocityVerified": False, "xVerified": False,
}

# Orbit Atlas — watchlist-only-unverified
snap["contracts"]["Orbit Atlas"] = {
    "address": "0xd455a3963bb7ae70f6a52a66d0c4bda306dbddee",
    "status": "watchlist-only-unverified-2026-11-10",
    "name": "Orbit Atlas", "symbol": None, "kind": "ERC721",
    "totalSupply": 236, "totalMinted": None, "freeMinted": None, "paidMinted": None,
    "FREE_SUPPLY": None, "MAX_SUPPLY": 875,
    "FREE_PER_WALLET": None, "MAX_PER_WALLET": 10, "mintOpen": 1,
    "freePctVerified": None,
    "balanceOf_user": 0, "freeClaimed_user": None,
    "owner": "0x3fbe2b54baf80d33e2ef6e46cb972959536eca17", "ownerInDiscards": False,
    "sourcify": "exact_match",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "source": "Boltbook front page run 1401 (post jahangirbd.ai 'Orbit Atlas 169/875' ~14:0x WIB + drhmwt.ai 154 sebelumnya; hot-leg pertama melihat 09:09 WIB) + verifikasi on-chain run ini",
    "launchNote": ("UMUR UNVERIFIED: tidak ada stated launch time; tidak ada mintStart/freeStart view; first-mint probe eth_getLogs (nodereal, 4x chunk 1000 blok) "
        "gagal -32005 'limit exceeded' di semua chunk; hot-leg first-seen 09:09 WIB hari ini hanya batas bawah keberadaan, bukan launch time."),
    "websiteNote": ("GATE website UNVERIFIED (methods A/G: pencarian nama/alamat tanpa situs proyek; H: contractURI() kosong; tokenURI belum dibaca; "
        "bila promosi mendekat, lengkapi methods I/J/K/L/M/N sebelum preview/mint apa pun)."),
    "baselineNote": ("WATCHLIST-ONLY run 1401: agent-shape TIDAK MENENTUKAN (ABI exact_match: mintWithAgentTokenId + agentIds + agentTokenIdOf + mintedByAgent ADA, "
        "TAPI tanpa registry_ref di ABI, tanpa fungsi AgentGate, tanpa free views — bukan bukti agent-shaped penuh, bukan pula bukti bukan); "
        "freeMinted/freeClaimed null -> free% UNVERIFIED (totalSupply 236/875 = 27,0% hanya vs MAX, bukan free counter); price() 0,000069 BNB = ada jalur berbayar; "
        "owner BUKAN discards; slot user: balanceOf=0 (freeClaimed(user) view tidak ada — slot UNVERIFIED). BUKAN early lead (first-mint tak terverifikasi + agent-shape tak menentukan). "
        "TIDAK pernah preview/mint."),
    "velocityVerified": False, "xVerified": False,
}

# binanceai (track-B, refund/failed) — fresh read this run
snap["runNote1401_1110_binanceai"] = ("Run 1401 (fresh read run-2026-11-10-1401-binanceai.py): binanceai TETAP fase refund/failed "
    "(launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed_user=0, saldo TOKEN user 0) — IDENTIK run 1331/1931. "
    "SUDAH dilaporkan sekali - TIDAK dilaporkan ulang.")
snap["binanceai_claim"] = dict(snap.get("binanceai_claim", {}))
snap["binanceai_claim"].update({"status": "closed-refund-phase-2026-11-07",
    "verified_run": "2026-11-10 run 1401", "verified_wib": "2026-11-10 14:4x WIB",
    "note": "Re-check run 1401: tetap fase refund/failed (failed=1, isRefundPhase=1, launched=0, totalShares 3110, tokenClaimed user 0, saldo TOKEN user 0). SUDAH dilaporkan sekali - TIDAK dilaporkan ulang."})

# bridge diff (complementary leg)
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
    snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    snap_addrs |= {str(v.get("sale", "")).lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict)}
    snap_addrs |= {str(v.get("token", "")).lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict)}
    new_bridge = [a for a in bcontracts if a.lower() not in snap_addrs]
    snap["runNote1401_bridge"] = (f"Run 1401 bridge: {len(bcontracts)} kontrak, {len(new_bridge)} belum di snapshot — 0 baru vs run 1331; "
        "0 promosi (tidak ada yang memenuhi tier).")
except Exception as e:
    snap["runNote1401_bridge"] = f"Run 1401 bridge: baca gagal ({e}); lanjut normal, bridge tidak menggagalkan run."

# run-level notes
snap["runNote1401_1110"] = ("Run 1401 (2026-11-10 14:01-14:5x WIB, blok 132733154, interval 60 mnt vs run 1331): re-read 653 kontrak + 75 track_c (560,5 dtk). "
    "Velocity LOLOS: ['Rose Genesis', 'DRIFTWIRE'] — tanpa promosi (Rose Genesis umur+free% UNVERIFIED; DRIFTWIRE sudah minted-by-user). "
    "STRONG-LEAD DIRECT MINT 1: ELSY AGENT — 2 NFT gratis (#880 Forest + #881 Ember), tx 0xdb09e20fc92089fdbdf6dab6f09a1d22b7f268b960562098a183a0045bdd3a88, blok 132736572, gas 163553, receipt 1, verifikasi on-chain lengkap. "
    "EARLY LEAD BARU 1 (Boltbook): Arcane Stones (totalSupply 355/4111, website terverifikasi via config.js, agent-shaped via bytecode registry, umur UNVERIFIED, free% inferensi 8,6%). "
    "WATCHLIST BARU 1: Orbit Atlas (totalSupply 236/875, agent-shape tak menentukan, umur+website+free% UNVERIFIED). "
    "Hakuna Agent: sudah ditriase 2026-11-07 (BUKAN agent-shaped, first mint 2026-11-07 15:59 WIB) — post Boltbook baru hanya recheck, TANPA laporan. "
    "Onyx Agent: sudah di snapshot (watchlist-only-age-unverified, gate FAILED) — post recheck 4.790/5.000 sama, TANPA perubahan. "
    "AgenticGangsterNFT: free 69/111 = 62,2% tapi umur UNVERIFIED + freeMint butuh EIP-712 challenge server -> tetap watchlist-only. "
    "YAMA: baca ulang track_c GAGAL lagi (semua null) — status audit-blocked dipertahankan; deadline umur ~15:18 WIB hari ini. NUSA freeMinted 369->370, gate FAILED, deadline 17:05 WIB hari ini. "
    "Feed Sourcify 20/20 dicek, 0 S1/0 S2 (1 near-miss 0xFdca...: quote+freeClaimed+agent_ref tapi tanpa fungsi mint). "
    "Boltbook EN 46.378 B / ZH 46.320 B (+ fetch ke-2 EN 45.941 B). Ankr 401 fast-fail (preflight 8,2 dtk, head 132733179); watermark tetap 132512564; gap ~220.615 blok. "
    "Scan leg GAGAL CEPAT; 5c: tanpa output scan baru -> 0 dicek run ini. Sweep web EN+ZH: Agentic Gangster sudah di snapshot (watchlist-only); MOLT AGENT pool habis; Horus AI fase 1 sold out; "
    "AlphaPulse (APLS) PAID-ONLY (1 share = 1 USDT, tanpa jalur gratis) -> bukan lead; Square/Odaily/PANews 0 baru. "
    "Kandidat baru 0; strong lead baru 1 (ELSY, di-mint); early lead baru 1 (Arcane Stones); track-C lead/kandidat baru 0; sellout baru 0.")
snap["runNote1401_1110_scan"] = ("Run 1401 scan: PRE-FLIGHT GAGAL (Ankr 401 Unauthorized, 8,2 dtk, head 132733179) — outage Ankr sejak 2026-11-09 ~13:33 WIB BERLANJUT. "
    "Scan leg FAST-FAIL per amandemen 2026-11-06; watermark TETAP 132512564; gap ke head ~220.615 blok (backfill OFF atas perintah user).")
snap["runNote1401_1110_discovery"] = ("Run 1401 discovery (routes 2/3/5a/6): Boltbook EN+ZH front page — ELSY AGENT (strong lead -> direct mint 2 NFT) + Arcane Stones (EARLY lead baru) + "
    "Orbit Atlas (watchlist-only-unverified) + Hakuna Agent (sudah ditriase Nov 7, bukan agent-shaped) + Onyx Agent (sudah di snapshot, gate FAILED) + Forge Pass 418/20000 + LUMO 19/1500 "
    "(EIP-712 gate tetap blokir) + BITCAT sale (sudah minted user, freeClaimed 958/1000, 42 tersisa) + Pickgrid 124/300 + PanduAGENT 219. "
    "BoltRewards 0x8269ea16... adalah link footer Boltbook, bukan proyek mint. Sourcify feed 20 -> 0 S1/0 S2. Sweep web: Agentic Gangster (sudah snapshot, watchlist-only); "
    "MOLT AGENT pool habis; Horus AI fase 1 sold out; AlphaPulse APLS paid-only; AirdropBuzz YAMA/MALTA sudah diketahui; Odaily + PANews 0 mention Agent ID. twitterapi.io tidak pernah dipanggil.")
snap["runNote1401_1110_5c"] = ("Run 1401 5c: scan leg fast-fail (Ankr 401) -> TIDAK ADA output scan baru -> 0 ERC-20 baru dicek run ini (bukan 0 hasil shape-check; "
    "tidak ada backlog baru). track-c-scan-checked.json tidak berubah.")
snap["runNote1401_1110_age_exclusions"] = ("Run 1401 age-exclusion sweep: TIDAK ADA exclusion baru. Deadline terdekat: YAMA ~15:18 WIB hari ini (audit-blocked; bila lewat tanpa mint -> age-exclude + lapor sekali); "
    "NUSA 2026-11-10 17:05 WIB (~2,5 jam lagi, gate tetap FAILED); Sakura deadline 2026-11-12 01:47 WIB; SEVENFOLD deadline 2026-11-12 07:33 WIB; LUMO deadline 2026-11-17 12:01 WIB. "
    "Item lama dengan firstMintWib >48 jam TIDAK di-exclude: launch UNVERIFIED, exclusion butuh umur TERVERIFIKASI >48 jam (preseden Rose Genesis run 1231).")
snap["last_run_wib"] = NOW
snap["last_run_block"] = BLOCK
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: contracts updated={updated} track_c updated={tc_updated} total contracts={len(snap['contracts'])} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',{}))}")
