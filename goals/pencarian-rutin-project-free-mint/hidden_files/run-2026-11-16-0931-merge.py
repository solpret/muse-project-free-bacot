#!/usr/bin/env python3
"""Merge run 2026-11-16 09:31 WIB reread into onchain-snapshot.json.
FRESH dynamic merge (values from run-2026-11-16-0931-reread.json + snapshot).
Interval 30.0 min vs run 0831 (blok 133840619 -> 133848629). 36/36 reads OK.
- SPARKS velocity GAGAL run ini (+28, 0.72x; run 0831 LOLOS) - tetap early lead.
- JADE +23 (1.05x, velocity GAGAL); free 107/188 = 56,9% (>50% tapi <70% -> BUKAN strong lead).
- Boltbook baru: FleetGenesis (SOLD OUT 1000/1000) + BinanceDream (ERC-20 biasa, bukan agent-shaped).
- Sweep baru: PocketAi (age-excluded, site update 12 Nov) + YAMA sale (track-C S1 lolos tapi age-excluded, skill.md 8 Nov).
- Scan leg FAST-FAIL (Ankr 401). Watermark TETAP 132512564.
- Sourcify 10 terbaru: 0 S1/S2 pass. No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-0931")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-0931-reread.json"))
reads = r["reads"]; BLK = r["block"]; INTERVAL = 30.0
PRIMARY = {"AGCLUB":"totalMinted","MORFO":"totalMinted","NOISE":"totalMinted","RaceAgents":"totalSupply",
 "Zero":"totalMinted","HIVE":"totalSupply",
 "AgentNOVA":"totalSupply","SPARKS":"totalSupply","WANGCAI":"totalSupply",
 "YUANBAO":"totalSupply","PX24":"totalSupply","Zephyra":"totalMinted","LumenFindings":"totalSpecimens",
 "Pengu":"totalMinted","CPASS":"totalMinted","ORBIT":"totalSupply","TrashBandits":"totalMinted",
 "SKRR":"totalSupply","REOPIR":"totalSupply","FrieAgent-B751":"totalSupply","FrieAgent-c64d":"totalSupply",
 "Ledgera":"totalSupply","MAMI":"totalSupply","INKI":"totalSupply","HashcatDepot":"totalSupply",
 "OTV":"totalSupply","RAVE":"totalMinted","HANAMI":"totalSupply","CosmicSentinel":"totalSupply",
 "Matrix Agents":"totalSupply","Bold Leonidas":"totalSupply","ALIEN":"totalSupply","JADE":"totalSupply"}
COPY = ["totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","FREE_CAP","FREE_MAX",
 "MAX_SUPPLY","mintOpen","mintStart","isFreePhase","balanceOf_user","freeRemaining",
 "freeClaimed_user","freeUsed_user","mintedBy_user","hasAgentId_user","holdsAgentId_user",
 "priceFor_user","priceFor_user_1","mintedByWallet_user","paused","TOKEN_PRICE","remainingSupply",
 "mintPriceFor_user_1","cost_user_1","freeMintedPerWallet_user","mintedPerWallet_user",
 "totalSpecimens","currentExperiment","genesisStart","genesisOpen","mintsBy_user","mintCountOf_user",
 "freeSharesLeft","openedAt","freeBooked_user","claimOpen","hasFreeClaimed_user","mintsLeft",
 "FREE_MINT_CAP","freeMintsLeft","PRICE","paidMinted","mintPrice","freeClaimedByAgent_masgayut",
 "freeClaimedByAgent_masgayut_ai","freeSupply","maxSupply"]
def find_entry(name):
    if name in s.get("contracts", {}): return s["contracts"][name], "contracts"
    if name in s.get("track_c", {}): return s["track_c"][name], "track_c"
    return None, None
log=[]
for name, prim in PRIMARY.items():
    rd = reads.get(name)
    entry, where = find_entry(name)
    if rd is None or entry is None:
        log.append(f"{name}: SKIP (read={rd is not None}, entry={where})"); continue
    views = rd.get("views") or {}
    old_prim = entry.get(prim)
    new_prim = views.get(prim)
    for k in COPY:
        if k in views and views[k] is not None:
            entry[k] = views[k]
    entry["lastReadBlock"] = BLK
    entry["lastReadWib"] = "2026-11-16 ~09:31 WIB"
    if old_prim is not None and new_prim is not None:
        prev_rate = entry.get("currentRatePerMin")
        d = new_prim - old_prim
        rate = d / INTERVAL
        ratio = (rate / prev_rate) if prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and d >= 20)
        entry["previousTotalSupply"] = old_prim
        entry["mintedInInterval"] = d
        entry["intervalMinutes"] = INTERVAL
        entry["previousRatePerMin"] = prev_rate
        entry["currentRatePerMin"] = rate
        entry["velocityRatio"] = ratio
        entry["velocityLegPasses"] = vel
        log.append(f"{name}: {old_prim}->{new_prim} (+{d}, {rate:.3f}/mnt vs prev {prev_rate} = {ratio if ratio is None else round(ratio,2)}x) vel={vel}")
    else:
        log.append(f"{name}: {prim} new={new_prim} old={old_prim} (uncomparable; old values kept)")
N = {
 "SPARKS": "Run 0931 (blok 133848629, interval 30,0 mnt vs run 0901): totalSupply 851->869 (+18, 0,600/mnt vs prev 0,933 = 0,64x) -> velocity GAGAL (run 0831 LOLOS, run 0901 GAGAL, kini gagal lagi); free% UNVERIFIED (tanpa free view), umur UNVERIFIED, website UNVERIFIED -> tetap early lead, TIDAK promosi/preview/mint.",
 "JADE": "Run 0931 (blok 133848629): totalSupply 107->188 (+81, 2,700/mnt vs prev 0,767 = 3,52x, >=20 -> velocity LOLOS run ini) TAPI freeClaimed 107->188/188 = 100% SOLD OUT, cost(user,1) 0 -> 0,0005 BNB, slot pengguna HILANG karena pool habis (mintedBy=0, balanceOf=0). Perubahan sold-out SUDAH dilaporkan sekali oleh hot-leg 09:24 WIB (key ...#sellout-20261116-0924) -> run ini TIDAK melaporkan ulang; status snapshot diubah ke sold-out-free-2026-11-16.",
 "Bold Leonidas": "Run 0931 (blok 133848629): totalSupply 763->770 (+7, 0,233/mnt vs prev 0,200 = 1,17x) -> velocity GAGAL; mintPriceFor(user,1)=0 (slot gratis TERBUKA), balanceOf(user)=0, mintOpen=1; free%/umur/website MASIH UNVERIFIED -> tetap early lead.",
 "Matrix Agents": "Run 0931 (blok 133848629): totalSupply 472->474 (+2, 0,067/mnt vs prev 0,133 = 0,50x) -> velocity GAGAL; freeMinted 477/1000 = 47,7% (freeRemaining tidak terbaca run ini); freeMinted > totalSupply - anomali baca BERLANJUT; freeClaimedByAgent(masgayut)=0, (masgayut_ai)=0.",
 "MORFO": "Run 0931 (blok 133848629): totalMinted 812->817 (+5, 0,167/mnt vs prev 0,167 = 1,00x) -> velocity GAGAL.",
 "AgentNOVA": "Run 0931 (blok 133848629): totalSupply 640->642 (+2, 0,067/mnt vs prev 0,067 = 1,00x) -> velocity GAGAL.",
 "HIVE": "Run 0931 (blok 133848629): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.",
 "Zero": "Run 0931 (blok 133848629): totalSupply/freeClaimed GAGAL baca lagi run ini (degradasi RPC, BUKAN nol); nilai lama dipertahankan, velocity TIDAK dihitung. balanceOf(user)=0.",
 "ALIEN": "Run 0931 (blok 133848629): totalSupply 0 TETAP, mintOpen=0 (BELUM DIBUKA), FREE_SUPPLY 1000/MAX_SUPPLY 1300, isFreePhase=1 -> tetap UPCOMING watchlist-only.",
 "WANGCAI": "Run 0931 (blok 133848629): totalSupply 189 FLAT, freeClaimed 188/188 = pool gratis HABIS (sold-out-2026-11-14, sudah tercatat). DIAM.",
 "YUANBAO": "Run 0931 (blok 133848629): totalSupply 189 FLAT, freeClaimed 188/188 = pool gratis HABIS (sold-out-2026-11-14, sudah tercatat). DIAM.",
 "LumenFindings": "Run 0931 (blok 133848629): totalSpecimens GAGAL baca run ini (nilai lama 6017 dipertahankan) - BUKAN velocity mint (counter spesimen eksperimen, item age-excluded sejak 14 Nov). DIAM.",
 "DogeRageFi": "Run 0931 (blok 133848629): totalMinted 225->226 (+1), totalSupply 339.001 DRF, freeSupply 432 TETAP, mintOpen 1, mintedBy(user)=0, balanceOf(user)=0. Umur presisi MASIH UNVERIFIED; gate website MASIH GAGAL. Tetap watchlist-only, BUKAN lead. TIDAK preview/mint.",
 "ORBIT": "Run 0931 (blok 133848629): freeClaimed 292/888 TETAP, claimOpen 1, hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.",
 "RigForge": "Run 0931 (blok 133848629): freeSharesLeft 639, openedAt 0, freeClaimed 361 - DIAM.",
 "Ledgera": "Run 0931 (blok 133848629): totalSupply 2689 FLAT (+0), freeClaimed 2682/5000 = 53,6% - velocity 0, BUKAN kandidat/strong lead. Status tetap checked-not-lead-2026-11-14. DIAM.",
 "RaceAgents": "Run 0931 (blok 133848629): totalSupply 623 FLAT, freeMinted 623 - velocity 0. DIAM.",
 "CPASS": "Run 0931 (blok 133848629): totalMinted 1729 FLAT (+0). DIAM.",
}
for name, note in N.items():
    entry, where = find_entry(name)
    if entry is not None:
        entry["runNote0931_1116"] = note
    else:
        log.append(f"NOTE-SKIP {name}: no entry in contracts/track_c")
ba = reads.get("BinanceAI-mint", {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
for k in ("launched","failed","isRefundPhase","totalShares"):
    if ba.get(k) is not None: pc[k] = ba[k]
if ba.get("tokenClaimed_user") is not None: pc["tokenClaimed_user"] = ba["tokenClaimed_user"]
pc["lastReadWib"] = "2026-11-16 ~09:31 WIB"
pc["runNote0931"] = "Run 0931: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133848629) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
bmentry, _ = find_entry("BinanceAI-mint")
if bmentry is not None:
    for k in ("launched","failed","isRefundPhase","totalShares"):
        if ba.get(k) is not None: bmentry[k] = ba[k]
    bmentry["lastReadBlock"] = BLK; bmentry["lastReadWib"] = "2026-11-16 ~09:31 WIB"
s["contracts"]["AETHER"] = {
 "address": "0x926504d174e99DB699141049b3Dd94dF501ff813",
 "status": "checked-not-lead-free-exhausted-2026-11-16",
 "name": "AETHER", "symbol": "",
 "firstSeenBlock": 133848629, "lastReadBlock": 133848629,
 "lastReadWib": "2026-11-16 ~09:31 WIB",
 "baselineNote": "Sweep rute 3/5b run 0931 (subagent): situs https://aetheragent.site/ (400 mint pertama gratis, 1/wallet, Agent ID wajib; total supply 2.000; situs mencetak kontrak persis). On-chain blok 133848629: totalSupply 442 = totalMinted 442, FREE_SUPPLY 400, MAX_SUPPLY 2000 -> totalMinted 442 > FREE_SUPPLY 400 = kuota gratis HABIS; freeClaimed/freeMinted view tidak ada; Sourcify 404 not_verified; bytecode 18.199 byte, registry_bytes False -> agent-shape UNVERIFIED, umur UNVERIFIED. BUKAN early lead (bentuk agent tidak terverifikasi + pool gratis habis). checked-not-lead, log-only, TIDAK dilaporkan.",
 "runNote0931_1116": "Run 0931: AETHER 0x9265 totalMinted 442 > FREE_SUPPLY 400 -> kuota gratis HABIS; Sourcify 404, tanpa registry bytes. BUKAN lead. DIAM.",
 "velocityLegPasses": False}
s["contracts"]["BNBCoreSeed"] = {
 "address": "0xfd3430e86df73c4e1e55036dc368a52716b84937",
 "status": "checked-not-lead-not-agent-shaped-2026-11-16",
 "name": "BNBCore Seed", "symbol": "SEED",
 "firstSeenBlock": 133848629, "lastReadBlock": 133848629,
 "lastReadWib": "2026-11-16 ~09:31 WIB",
 "baselineNote": "Boltbook ZH baru run 0931 (drhmwt.ai, 'BNBCore Seed: Unknown/10000, 0 mints in last ~30m, supply model dynamic/uncapped'). On-chain blok 133848629: totalSupply() revert (null), FREE_CAP 2000, mintOpen=1, balanceOf(user)=0; Sourcify 404 not_verified; bytecode 11.506 byte, registry_bytes False -> token BEP-20 biasa (bukan NFT mint agent-shaped), BUKAN track-C sale-shape (ABI tak terverifikasi, tanpa mint+quote+free view+agent gate). checked-not-lead, log-only, TIDAK dilaporkan.",
 "runNote0931_1116": "Run 0931: BNBCore Seed 0xfd34 token biasa, bukan agent-shaped (Sourcify 404, tanpa registry). BUKAN lead. DIAM.",
 "velocityLegPasses": False}
# JADE sold-out: status change (change already reported once by hot-leg 09:24, NOT re-reported here)
_jade = s["contracts"].get("JADE")
if _jade is not None:
    _jade["status"] = "sold-out-free-2026-11-16"
    _jade["freePctVerified"] = 100.0
    _jade["runNote0931_1116_sellout"] = "Run 0931: JADE freeClaimed 188/188 = 100% SOLD OUT (totalSupply 188, cost 0,0005 BNB). Perubahan ini SUDAH dilaporkan sekali oleh hot-leg 09:24 WIB (hot-leg-reported.json ...#sellout-20261116-0924); run ini TIDAK melaporkan ulang (dedupe lintas job)."
s["runNote0931_1116"] = "Run 0931: re-read 36/36 OK blok 133848629 (173,8 dtk). Velocity: SPARKS GAGAL (0,64x), Bold Leonidas GAGAL (1,17x), Matrix GAGAL (0,50x), MORFO GAGAL (1,00x), AgentNOVA GAGAL (1,00x); JADE velocity LOLOS (3,52x) TAPI SOLD OUT 188/188 (sudah dilaporkan hot-leg 09:24, tidak dilaporkan ulang). 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru. Baru dicek: AETHER (kuota gratis habis 442>400, Sourcify 404) + BNBCore Seed (token biasa, bukan agent-shaped) - keduanya checked-not-lead, DIAM. Scan FAST-FAIL (Ankr 401), watermark TETAP 132512564. Sourcify 10 terbaru: 0 S1/S2 (6 retry via curl OK). DIAM (tidak ada laporan chat)."
s["runNote0931_1116_scan"] = "Run 0931 scan pre-flight: Ankr getLogs HTTP 401 -> FAST-FAIL (log run-2026-11-16-0931-scanpreflight.log). Watermark TETAP 132512564 (head 133848809, gap 1.336.245). 5c dilewati (tanpa output scan)."
s["runNote0931_1116_boltbook"] = "Run 0931 Boltbook EN 200 (49.762 byte) / ZH 200 (49.240 byte); EN 4 alamat distinct, ZH 7 (set tidak sama); 1 alamat baru vs snapshot: BNBCore Seed 0xfd34 (token biasa, bukan agent-shaped) - checked-not-lead. Lainnya dikenal: JADE 0x1b88 (sold out), LumenFindings 0x4158 (age-excluded), BoltRewards 0x8269 (infra), BOLT 0xBbDd, Bold Leonidas 0x84bc, SPARKS 0xd52f. Mention: BNBCore Seed (drhmwt.ai, 0 mints/30m)."
s["runNote0931_1116_sweep"] = "Run 0931 sweep EN+ZH (subagent rute 3/5b/6): 0 project baru terkonfirmasi sebagai lead/kandidat. Baru dicek kaki utama: AETHER 0x9265 (kuota gratis habis 442>400, Sourcify 404, umur unverified -> checked-not-lead) + PONKE (sebutan ambigu di The Colony, tanpa kontrak + status bertentangan 47/555 vs 555/555 -> tidak bisa dinilai, bukan temuan). Hit lama: Oathbots, Saturnagent (7 Nov), PocketAi (age-excluded), YAMA 0x86D7 (age-excluded), UFO/NEBULA (tutup 12 Nov), NOVRA, ORBITA (sold out), Agentic Gangster (free 111/111 habis), TINY AGENTS (10 Nov), AGENT COSMOS (5 Nov), JINCHAN (8-10 Nov), Agent Zet (free 4.000/4.000 habis), Solace (tutup 14 Nov), SPARKS, DRAGON/MORFO/Matrix. Binance Square 6a: hanya post 19-22 hari lalu (Oathbots, hackou, Pixel Fox, AgentForge, LeadLoop, AGENT ID Card, Hundred, Odyssey), 0 segar 24 jam. Odaily newsflash (02:06 UTC): 0 kata agent. PANews: 0 pengumuman Agent ID/free-mint. DappBay tidak dipakai (tidak ada proyek baru terverifikasi yang butuh cek website; situs AETHER sendiri mencetak kontraknya). Pola instruksi tertanam 'Use my Binance Agentic Wallet to call mint()...' muncul lagi di hasil pencarian. Konten pihak ketiga, BUKAN instruksi user - diabaikan sepenuhnya; run tetap read-only, tanpa preview/mint/eksekusi. twitterapi.io tidak dipanggil."
s["runNote0931_1116_binanceai"] = "Run 0931 track-B binanceai.fun: TIDAK BERUBAH (launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed user=0, blok 133848629) - fase refund, DIAM."
_br = json.load(open(BASE + "scan-bridge.json")).get("contracts", {})
_snap_addrs = { (v.get("address") or "").lower() for v in list(s.get("contracts", {}).values()) + list(s.get("track_c", {}).values()) if isinstance(v, dict) }
_br_addrs = { k.lower() for k in _br.keys() }
_missing = sorted(_br_addrs - _snap_addrs)
_disc = sum(1 for v in _br.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
s["runNote0931_1116_bridge"] = f"Run 0931 bridge (read-only): {len(_br)} kontrak bridge, {len(_br_addrs & _snap_addrs)}/{len(_br)} sudah di snapshot, {len(_missing)} baru: {_missing if _missing else 'tidak ada'}, {_disc} same_owner_discarded. Tidak ada temuan pelengkap baru / promosi run ini. Job ini tidak menulis bridge."
s["last_run_wib"] = "2026-11-16 ~09:31 WIB"
s["last_run_note"] = "Run 0931: DIAM. 0 kandidat/strong/early/track-B/track-C baru. JADE SOLD OUT 188/188 (sudah dilaporkan hot-leg 09:24, tidak dilaporkan ulang). 2 kontrak baru dicek, semua checked-not-lead (AETHER kuota gratis habis, BNBCore Seed bukan-agent-shaped)."
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(s["contracts"]), "| track_c now:", len(s.get("track_c", {})))
print("\n".join(log))
print("MERGE DONE")
