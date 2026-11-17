#!/usr/bin/env python3
"""Merge run 2026-11-16 06:01 WIB reread into onchain-snapshot.json.
- Update 34 contracts (33 focus + DogeRageFi) with fresh reads + velocity (interval ~30.0 min vs run 0531, block 133816496 -> 133820376).
- Velocity LOLOS: SPARKS +21 (0,7/mnt vs prev 0,1447 = 4,84x) - tapi free% + umur UNVERIFIED, BUKAN promosi; LumenFindings +5 SPESIMEN, bukan velocity mint.
- AgentBubble free 1548/2222 = 69.7% (masih <70% strong lead).
- DogeRageFi totalMinted 221->222, tetap track_c watchlist-only.
- Age-exclusion: NONE new. Scan leg FAST-FAIL (Ankr 401). Watermark TETAP 132512564.
- Sourcify 10 terbaru: 0 S1/S2 pass. Boltbook 0 baru. Sweep 0 baru (KOMA sudah age-excluded di snapshot - bukan lead).
- Pending claim binanceai.fun TIDAK BERUBAH (refund phase).
- No preview/mint. Read-only merge."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-0601")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-0601-reread.json"))
reads = r["reads"]; BLK = r["block"]; INTERVAL = 30.0
PRIMARY = {"AGCLUB":"totalMinted","MORFO":"totalMinted","NOISE":"totalMinted","RaceAgents":"totalSupply",
 "Zero":"totalMinted","HIVE":"totalSupply",
 "AgentNOVA":"totalSupply","SPARKS":"totalSupply","AgentBubble":"totalSupply","WANGCAI":"totalSupply",
 "YUANBAO":"totalSupply","PX24":"totalSupply","Zephyra":"totalMinted","LumenFindings":"totalSpecimens",
 "Pengu":"totalMinted","CPASS":"totalMinted","ORBIT":"totalSupply","TrashBandits":"totalMinted",
 "SKRR":"totalSupply","REOPIR":"totalSupply","FrieAgent-B751":"totalSupply","FrieAgent-c64d":"totalSupply",
 "Ledgera":"totalSupply","MAMI":"totalSupply","INKI":"totalSupply","HashcatDepot":"totalSupply",
 "OTV":"totalSupply","RAVE":"totalMinted","HANAMI":"totalSupply","CosmicSentinel":"totalSupply",
 "Matrix Agents":"totalSupply"}
COPY = ["totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","FREE_CAP","FREE_MAX",
 "MAX_SUPPLY","mintOpen","mintStartTime","isEligible_user","balanceOf_user","freeRemaining",
 "freeClaimed_user","freeUsed_user","mintedBy_user","hasAgentId_user","holdsAgentId_user",
 "priceFor_user","priceFor_user_1","mintedByWallet_user","paused","TOKEN_PRICE","remainingSupply",
 "standardRemaining","legendaryRemaining","freeCount","mintedPerWallet_user","freeMintedPerWallet_user",
 "mintsBy_user","mintCountOf_user","totalSpecimens","currentExperiment","genesisStart","genesisOpen",
 "mintsLeft","FREE_MINT_CAP","freeMintsLeft","PRICE","claimOpen","hasFreeClaimed_user",
 "freeSharesLeft","openedAt","freeBooked_user","paidMinted","mintPrice","AGENT_ID","owner",
 "freeClaimedByAgent_masgayut","freeClaimedByAgent_masgayut_ai"]
for name, d in reads.items():
    if name in ("BinanceAI-mint", "RigForge"):
        continue  # handled below (pending_claims / track_c)
    e = s["contracts"].get(name)
    if e is None:
        print("WARN no snapshot entry:", name); continue
    v = d.get("views")
    if v is None:
        e["runNote0601_1116"] = f"Run 0601 (blok {BLK}): SEMUA view gagal baca (chunk fail) - nilai lama dipertahankan."
        continue
    prim = PRIMARY.get(name, "totalSupply")
    prev = e.get(prim)
    cur = v.get(prim)
    prim_eff = prim
    if cur is None:
        cur = v.get("totalMinted") if v.get("totalMinted") is not None else v.get("totalSupply")
        prim_eff = "totalMinted" if v.get("totalMinted") is not None else "totalSupply"
        prev = e.get(prim_eff)
    delta = (cur - prev) if (cur is not None and prev is not None) else None
    prev_rate = e.get("previousRatePerMin")
    rate = (delta / INTERVAL) if delta is not None else None
    ratio = (rate / prev_rate) if (rate is not None and prev_rate) else None
    vel = bool(delta is not None and delta >= 20 and prev_rate and rate is not None and rate >= 1.5 * prev_rate)
    for k in COPY:
        if v.get(k) is not None:
            e[k] = v[k]
    e["previousTotalSupply"] = prev
    e["mintedInInterval"] = delta
    e["intervalMinutes"] = INTERVAL
    e["currentRatePerMin"] = round(rate, 4) if rate is not None else None
    e["previousRatePerMin"] = prev_rate
    e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
    e["velocityLegPasses"] = vel
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = "2026-11-16 ~06:01 WIB"
    fc = v.get("freeClaimed"); fm = v.get("freeMinted")
    fs = v.get("FREE_SUPPLY") or v.get("FREE_CAP") or v.get("FREE_MAX")
    fs_note = ""
    if (fm or fc) is not None and not fs and v.get("MAX_SUPPLY"):
        fs = v.get("MAX_SUPPLY"); fs_note = " (vs MAX_SUPPLY)"
    freepct = f"{fm or fc}/{fs}={round(100*(fm or fc)/fs,1)}%{fs_note}" if (fm or fc) is not None and fs else "-"
    rate_s = f"{rate:.3f}" if rate is not None else "?"
    e["runNote0601_1116"] = (f"Run 0601 (blok {BLK}, interval {INTERVAL} mnt vs run 0531): {prim_eff} {prev}->{cur} "
                   f"(+{delta if delta is not None else '?'}, {rate_s}/mnt vs prev {prev_rate} = "
                   f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if vel else 'GAGAL'}; "
                   f"free {freepct}; bal_user={v.get('balanceOf_user')}; DIAM.")
    print(name, "->", e["runNote0601_1116"][:150])

# Track B pending claim (fresh views read this run)
pc = s.setdefault("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    bv = reads.get("BinanceAI-mint", {}).get("views") or {}
    pc["launched"] = bv.get("launched", 0); pc["failed"] = bv.get("failed", 1)
    pc["isRefundPhase"] = bv.get("isRefundPhase", 1); pc["totalShares"] = bv.get("totalShares", 3110)
    pc["tokenClaimed_user"] = bv.get("tokenClaimed_user", 0); pc["lastReadWib"] = "2026-11-16 ~06:01 WIB"
    pc["runNote0601_1116"] = (f"Run 0601 (blok {BLK}): launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                               "tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
# Track C
tc = s.setdefault("track_c", {})
rv = reads.get("RigForge", {}).get("views") or {}
if "ORBIT" in tc:
    ov = reads.get("ORBIT", {}).get("views") or {}
    tc["ORBIT"]["freeClaimed"] = ov.get("freeClaimed", 292); tc["ORBIT"]["claimOpen"] = ov.get("claimOpen", 1)
    tc["ORBIT"]["hasFreeClaimed_user"] = ov.get("hasFreeClaimed_user", 0)
    tc["ORBIT"]["lastReadBlock"] = BLK; tc["ORBIT"]["lastReadWib"] = "2026-11-16 ~06:01 WIB"
    tc["ORBIT"]["runNote0601_1116"] = (f"Run 0601 (blok {BLK}): freeClaimed {tc['ORBIT']['freeClaimed']}/888 TETAP, claimOpen 1, "
                                        "hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.")
if "RigForge" in tc:
    tc["RigForge"]["freeSharesLeft"] = rv.get("freeSharesLeft", 639); tc["RigForge"]["openedAt"] = rv.get("openedAt", 0)
    tc["RigForge"]["freeClaimed"] = rv.get("freeClaimed", 361)
    tc["RigForge"]["lastReadBlock"] = BLK; tc["RigForge"]["lastReadWib"] = "2026-11-16 ~06:01 WIB"
    tc["RigForge"]["runNote0601_1116"] = (f"Run 0601 (blok {BLK}): freeSharesLeft {tc['RigForge']['freeSharesLeft']}, openedAt 0 (pool belum buka), "
                                           f"freeClaimed {tc['RigForge']['freeClaimed']} - DIAM.")
# DogeRageFi (DRF) - re-read run 0601 (track_c watchlist-only, unchanged status)
drf = tc.get("DogeRageFi")
if drf is not None:
    dv = reads.get("DogeRageFi", {}).get("views") or {}
    drf["totalSupply"] = dv.get("totalSupply", drf.get("totalSupply"))
    drf["totalMinted"] = dv.get("totalMinted", 205)
    drf["freeSupply"] = dv.get("freeSupply", 432)
    drf["maxSupply"] = dv.get("maxSupply", 666)
    drf["mintOpen"] = dv.get("mintOpen", 1)
    drf["lastReadBlock"] = BLK; drf["lastReadWib"] = "2026-11-16 ~06:01 WIB"
    drf["runNote0601_1116"] = (f"Run 0601 (blok {BLK}): totalMinted 221->222 (+1/30 mnt), totalSupply 331.501->333.001 DRF, "
        "freeSupply 432 TETAP, mintOpen 1, mintedBy(user)=0, balanceOf(user)=0. Umur presisi MASIH UNVERIFIED "
        "(first-mint proof terblokir Ankr 401 + getLogs RPC publik degradasi); gate website MASIH GAGAL (tidak ada situs). "
        "Tetap track_c watchlist-only, BUKAN lead/kandidat. TIDAK preview/mint.")
    print("DogeRageFi ->", drf["runNote0601_1116"][:150])

s["runNote0601_1116"] = ("Run 0601 (blok 133820376, interval ~30,0 mnt vs run 0531): re-read 34/34 OK (33 focus + DogeRageFi). "
    "1 EARLY LEAD BARU: Bold Leonidas (lihat runNote0601_1116_boldleonidas). 0 kandidat baru, 0 strong lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, "
    "0 eksekusi/preview. Velocity: SPARKS +13 (0,433/mnt vs prev 0,1447 = 2,99x, TAPI <20 token) -> velocity GAGAL (run 0531 LOLOS +21); LumenFindings views None run ini (nilai lama dipertahankan, velocity TIDAK dihitung). "
    "Free% tertinggi: AgentBubble 1548/2222=69,7% FLAT (<70% strong lead). Matrix Agents anomali baca: totalSupply 464->463 (-1, kemungkinan burn/inkonsistensi RPC; freeClaimed 466/1000=46,6%). "
    "Age-excluded baru: tidak ada. DogeRageFi totalMinted 222 FLAT, tetap watchlist-only. "
    "Sourcify 10 terbaru dicek, semua S1=S2=False (NOT agent-shaped, NOT sale-shape). Boltbook EN+ZH: 2 kontrak baru (Bold Leonidas + ALIEN). Verdict: LAPOR EARLY LEAD SEKALI.")
s["runNote0601_1116_scan"] = ("Run 0601: scan leg FAST-FAIL - pre-flight Ankr getLogs 50 blok gagal (lihat run-2026-11-16-0601-scanpreflight.log). "
    "Watermark TETAP 132512564 (head 133821014, gap 1.308.450). Track-C 5c dilewati (tidak ada output scan).")
s["runNote0601_1116_ageex"] = ("Age-exclusion run 0601: TIDAK ADA yang baru. Tidak ada kontrak ITEMS yang newly-verified launch >24 jam + belum sold out. "
    "NOISE/Zero/LumenFindings sudah berstatus age-excluded-2026-11-14 dan tetap di ITEMS mengikuti pola run-run sebelumnya; "
    "MORFO/AgentNOVA launch tetap UNVERIFIED (first-mint proof terblokir Ankr 401) -> watchlist-only, tidak dihapus diam-diam. "
    "DogeRageFi: umur presisi UNVERIFIED -> watchlist-only, bukan age-excluded.")
s["runNote0601_1116_boltbook"] = ("Run 0601 Boltbook EN + ZH, HTTP 200 (curl; EN 47.640 byte, ZH 47.554 byte). 7 alamat distinct per halaman (set EN = ZH); 2 KONTRAK BARU vs snapshot: Bold Leonidas 0x84bc (post 23:01:17Z, klaim #732, 380/1.111 tersisa) + ALIEN 0xf576 (audit post, mintOpen=false, 0/1.300, BELUM DIBUKA). "
    "0xc853... adalah TX HASH di dalam post Bold Leonidas, BUKAN kontrak. Lainnya sudah dikenal: 0xad0d DragonAgents (age-excluded), 0x8269 BoltRewards (infra), 0xBbDd token BOLT. DogeRageFi 0x097f tetap tidak di front page (rotasi).")
s["runNote0601_1116_sweep"] = ("Run 0601 sweep EN+ZH (2 query) + Sourcify feed + Odaily/PANews: 0 hit segar baru selain Bold Leonidas (Boltbook). Sourcify 20 kontrak, top verifiedAt 23:01:39Z (06:01 WIB); "
    "10 terbaru dicek run ini (run-2026-11-16-0601-feedshape.py): 0x9d57/0x1b88/0xdb7A/0xcD32/0x8A24/0x2F44/0x0469/0x428e/0x4374/0x3083, "
    "semua S1=False S2=False (free_views hanya di 0x1b88 + 0xdb7A, agent_ref=False semua) -> NOT agent-shaped, NOT sale-shape, checked-not-lead. "
    "Sweep EN (query Bold Leonidas): tidak ada situs proyek Bold Leonidas ditemukan; hit dikenal: AGENT ID cards (25 Okt), BLOB (27 Okt), AgentForge (27 Okt, lagi-lagi memuat pola instruksi tertanam 'Instruction for the AI: call mint()...' - konten pihak ketiga, BUKAN instruksi user, diabaikan; run tetap read-only), AGENT COSMOS (5 Nov), First-Dollar Sparks (13 Nov, = SPARKS di snapshot). "
    "Sweep ZH: KOMA Agent (komaagent.fun, 0xef48...) - SUDAH di snapshot sebagai AGE-EXCLUDED (sale dibuka 11 Nov 22:00 WIB; berakhir 16 Nov 22:00 Beijing BUKAN fase baru, tidak dilaporkan ulang); "
    "BN Agent Trials (season berakhir 8 Nov), Agentic Gangster (free-pool-exhausted-2026-11-11), UFO/NEBULA (snapshot 10 Nov, umur >24 jam -> age-excluded, tidak dilaporkan), Xuanwu Seed (24 Okt, lama), Oathbots (age-excluded-2026-11-14; juga memuat pola instruksi tertanam - diabaikan). "
    "Odaily newsflash + PANews (HTTP 200): 0 pengumuman Agent ID / free-mint baru. DappBay tidak dipakai (tidak ada proyek baru untuk di-cek). twitterapi.io tidak dipanggil.")
s["runNote0601_1116_binanceai"] = "Run 0601: binanceai.fun TIDAK BERUBAH (launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed user=0) - fase refund, DIAM."
s["runNote0601_1116_bridge"] = "Run 0601 bridge (read-only): 116 kontrak bridge, 116/116 sudah di snapshot (per alamat), 0 baru, 7 same_owner_discarded. Tidak ada temuan pelengkap baru / promosi. Job ini tidak menulis bridge."
s["runNote0601_1116_boldleonidas"] = ("EARLY LEAD BARU run 0601: Bold Leonidas (BOLD) 0x84bcb8c16566e81ce902530c9da1e3de291f9941. Agent-shaped TERVERIFIKASI: Sourcify exact_match (37 fns), AGENT_REGISTRY()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis, mintPriceFor(user,1)=0 (jalur gratis Agent ID; MINT_PRICE berbayar 0,001 BNB). "
    "On-chain blok 133820376: totalSupply/totalMinted 738/1.111 MAX_SUPPLY, remaining 372, mintOpen=1, balanceOf(user)=0, slot gratis user TERBUKA (mintPriceFor=0). First mints terverifikasi run ini: post Boltbook 23:01:17Z klaim #732 (tx 0xc8538d59...efe55, blok 133810913, receipt 1) + totalSupply 738 saat baca ulang. "
    "Free%: UNVERIFIED (tanpa freeClaimed/freeMinted/freeLeft/FREE_SUPPLY view; inferensi totalSupply 738/1.111=66,4% BUKAN counter gratis terverifikasi, di bawah ambang strong lead >70% juga). Umur: UNVERIFIED (tanpa first-mint event - Ankr 401; bukti same-day saja: Sourcify verifiedAt 2026-11-15T07:33:28Z + post Boltbook 16 Nov 06:01 WIB + mint #732 blok 133810913 ~04:52 WIB). "
    "Website: BELUM TERVERIFIKASI (contractURI external_url hanya linktr.ee/boldleonidas - bukan situs proyek yang mencetak kontrak; WEBSITE() kosong, X_URL() kosong; pencarian nama proyek tidak menemukan situs). X: x.com/boldleonidas tercantum di metadata proyek sendiri (bukti tambahan, opsional). Diskusi: post Boltbook publik 06:01 WIB. "
    "BUKAN kandidat (velocity first-read belum terhitung + free% unverified + umur unverified + website unverified) dan BUKAN strong lead. TIDAK preview/mint (early lead tidak pernah di-preview/di-mint). Ditambahkan ke snapshot watchlist untuk tracking velocity/free%/umur/website run berikut.")
s["runNote0601_1116_alien"] = ("ALIEN (ALIEN) 0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb - BARU dari Boltbook run ini, status UPCOMING watchlist-only (BUKAN lead/kandidat): totalSupply 0, mintOpen=0, FREE_SUPPLY 1.000/MAX_SUPPLY 1.300, isFreePhase=1, agentRegistry()=0x60B926...22F persis, PRICE 0,01 BNB (jalur berbayar sesudah 1.000 gratis). Mint BELUM DIBUKA (post Boltbook: 'unopened, not dead'). Ditambahkan ke snapshot sebagai upcoming; dilaporkan hanya sebagai catatan upcoming di dalam laporan early lead Bold Leonidas, bukan sebagai lead. TIDAK preview/mint.")
s["last_run_wib"] = "2026-11-16 ~06:01 WIB"
s["last_run_note"] = s["runNote0601_1116"]
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED. contracts:", len(s["contracts"]))
