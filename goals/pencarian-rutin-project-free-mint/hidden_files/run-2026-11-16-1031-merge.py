#!/usr/bin/env python3
"""Merge run 2026-11-16 10:01 WIB reread into onchain-snapshot.json.
FRESH dynamic merge (values from run-2026-11-16-1031-reread.json + snapshot).
Interval 30.0 min vs run 0931 (blok 133848629 -> 133852948). 36/36 reads OK.
- SPARKS +23 (1.28x) GAGAL; MORFO +19 (3.80x tapi <20) GAGAL; AgentNOVA +8 (4.00x tapi <20) GAGAL.
- JADE tetap SOLD OUT 188/188 (sudah dilaporkan hot-leg 09:24, tidak dilaporkan ulang).
- Baru dicek: NEUPEN (bukan agent-shaped, situs ada tapi 0 sebutan agent) + FROGY (0 mint, registry-bytes saja) - keduanya checked-not-lead, DIAM.
- Scan leg FAST-FAIL (Ankr 401). Watermark TETAP 132512564.
- Sourcify 10 terbaru: 0 S1/S2 (6 retry via curl OK). No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-1031")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-1031-reread.json"))
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
    entry["lastReadWib"] = "2026-11-16 ~10:01 WIB"
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
 "SPARKS": "Run 1031 (blok 133852948, interval 30,0 mnt vs run 0931): totalSupply 869->892 (+23, 0,767/mnt vs prev 0,600 = 1,28x) -> velocity GAGAL (butuh >=1,5x); free% UNVERIFIED (tanpa free view), umur UNVERIFIED, website UNVERIFIED -> tetap early lead, TIDAK promosi/preview/mint.",
 "MORFO": "Run 1031 (blok 133852948): totalMinted 817->836 (+19, 0,633/mnt vs prev 0,167 = 3,80x TAPI hanya 19 token < 20) -> velocity GAGAL (aturan >=20 token/interval).",
 "AgentNOVA": "Run 1031 (blok 133852948): totalSupply 642->650 (+8, 0,267/mnt vs prev 0,067 = 4,00x TAPI hanya 8 token < 20) -> velocity GAGAL (aturan >=20 token/interval).",
 "Bold Leonidas": "Run 1031 (blok 133852948): totalSupply 770->775 (+5, 0,167/mnt vs prev 0,233 = 0,71x) -> velocity GAGAL; mintPriceFor(user,1)=0 (slot gratis TERBUKA), balanceOf(user)=0, mintOpen=1; free%/umur/website MASIH UNVERIFIED -> tetap early lead.",
 "Matrix Agents": "Run 1031 (blok 133852948): totalSupply 474->477 (+3, 0,100/mnt vs prev 0,067 = 1,50x TAPI hanya 3 token < 20) -> velocity GAGAL; freeMinted 480/1000 = 48,0%; freeMinted > totalSupply - anomali baca BERLANJUT; freeClaimedByAgent(masgayut)=0, (masgayut_ai)=0.",
 "Ledgera": "Run 1031 (blok 133852948): totalSupply 2689->2692 (+3, 0,100/mnt vs prev 0) -> velocity GAGAL; freeClaimed 2685/5000 = 53,7% - BUKAN kandidat/strong lead. Status tetap checked-not-lead-2026-11-14. DIAM.",
 "CPASS": "Run 1031 (blok 133852948): totalMinted 1729->1737 (+8, 0,267/mnt vs prev 0,033 = 8,00x TAPI hanya 8 token < 20) -> velocity GAGAL.",
 "HIVE": "Run 1031 (blok 133852948): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.",
 "Zero": "Run 1031 (blok 133852948): totalSupply/freeClaimed GAGAL baca lagi run ini (degradasi RPC, BUKAN nol); nilai lama dipertahankan, velocity TIDAK dihitung. balanceOf(user)=0.",
 "ALIEN": "Run 1031 (blok 133852948): totalSupply 0 TETAP, mintOpen=0 (BELUM DIBUKA), FREE_SUPPLY 1000/MAX_SUPPLY 1300, isFreePhase=1 -> tetap UPCOMING watchlist-only.",
 "WANGCAI": "Run 1031 (blok 133852948): totalSupply 189 FLAT, freeClaimed 188/188 = pool gratis HABIS (sold-out-2026-11-14, sudah tercatat). DIAM.",
 "YUANBAO": "Run 1031 (blok 133852948): totalSupply 189 FLAT, freeClaimed 188/188 = pool gratis HABIS (sold-out-2026-11-14, sudah tercatat). DIAM.",
 "LumenFindings": "Run 1031 (blok 133852948): totalSpecimens 6026->6114 (+88) - BUKAN velocity mint (counter spesimen eksperimen, item age-excluded sejak 14 Nov). DIAM.",
 "DogeRageFi": "Run 1031 (blok 133852948): totalMinted 226 FLAT, totalSupply 339.001 DRF, freeSupply 432 TETAP, mintOpen 1, mintedBy(user)=0, balanceOf(user)=0. Umur presisi MASIH UNVERIFIED; gate website MASIH GAGAL. Tetap watchlist-only, BUKAN lead. TIDAK preview/mint.",
 "ORBIT": "Run 1031 (blok 133852948): freeClaimed 292/888 TETAP, claimOpen 1, hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.",
 "RigForge": "Run 1031 (blok 133852948): freeSharesLeft 639, openedAt 0, freeClaimed 361 - DIAM.",
 "JADE": "Run 1031 (blok 133852948): totalSupply 188 TETAP, freeClaimed 188/188 = 100% SOLD OUT, cost(user,1)=0,0005 BNB. Sudah dilaporkan sekali oleh hot-leg 09:24 WIB; run ini TIDAK melaporkan ulang. Status tetap sold-out-free-2026-11-16.",
 "RAVE": "Run 1031 (blok 133852948): totalMinted 334 FLAT, freeMinted 334/3000 = 11,1%. DIAM.",
}
for name, note in N.items():
    entry, where = find_entry(name)
    if entry is not None:
        entry["runNote1031_1116"] = note
    else:
        log.append(f"NOTE-SKIP {name}: no entry in contracts/track_c")
ba = reads.get("BinanceAI-mint", {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
for k in ("launched","failed","isRefundPhase","totalShares"):
    if ba.get(k) is not None: pc[k] = ba[k]
if ba.get("tokenClaimed_user") is not None: pc["tokenClaimed_user"] = ba["tokenClaimed_user"]
pc["lastReadWib"] = "2026-11-16 ~10:01 WIB"
pc["runNote1031"] = "Run 1031: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133852948) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
bmentry, _ = find_entry("BinanceAI-mint")
if bmentry is not None:
    for k in ("launched","failed","isRefundPhase","totalShares"):
        if ba.get(k) is not None: bmentry[k] = ba[k]
    bmentry["lastReadBlock"] = BLK; bmentry["lastReadWib"] = "2026-11-16 ~10:01 WIB"
# NEUPEN + FROGY as checked-not-lead
s["contracts"]["NEUPEN"] = {
 "address": "0x91a1b0e9ee45ff34ef41df920041cccfe4ada26d",
 "status": "checked-not-lead-not-agent-shaped-2026-11-16",
 "name": "Neural Net Penguins", "symbol": "NEUPEN",
 "firstSeenBlock": 133853171, "lastReadBlock": 133853171,
 "lastReadWib": "2026-11-16 ~10:01 WIB",
 "baselineNote": "BARU dari Boltbook EN+ZH run 1031 (census nanomind.ai 10:02 WIB: freeClaimed 792/7.000, mintOpen 1, 3 free/wallet; pertama disebut di sweep note 15 Nov 16:01 tapi belum pernah diverifikasi on-chain/ditambah snapshot). On-chain blok 133853171: totalSupply 800, freeClaimed 795/7000 = 11,4%, FREE_SUPPLY 7000, MAX_SUPPLY 7777, FREE_PER_WALLET 3, mintOpen=1, mintedBy(user)=0, balanceOf(user)=0; Sourcify exact_match 39 fns: mint()+quote()+free views (freeClaimed/freeFor/freeLeft/freeUsed) TAPI TANPA registry/AgentGate (agent_ref=False; registry_bytes False) -> BUKAN agent-shaped. contractURI/externalUrl -> https://neural-net-penguins.668823.xyz (HTTP 200, mencetak kontrak persis) TAPI 0 sebutan 'agent' di situs, tanpa narasi Agent ID, tanpa X ditemukan -> kriteria narasi Binance Agentic Wallet GAGAL; free% 11,4% <50%; umur UNVERIFIED. BUKAN early lead (bukan agent-shaped), BUKAN kandidat/strong lead. checked-not-lead, log-only, TIDAK dilaporkan.",
 "runNote1031_1116": "Run 1031: NEUPEN 0x91a1 freeClaimed 795/7000 = 11,4%, mintOpen 1, slot user terbuka (mintedBy=0) TAPI bukan agent-shaped (Sourcify tanpa registry/AgentGate, registry_bytes False) + situs tanpa narasi agent + umur unverified -> checked-not-lead. DIAM.",
 "velocityLegPasses": False}
s["contracts"]["FROGY"] = {
 "address": "0x51367fbd6d140f22892db62c1b7812088dd8f821",
 "status": "checked-not-lead-not-agent-shaped-2026-11-16",
 "name": "FROGY", "symbol": "FROGY",
 "firstSeenBlock": 133853171, "lastReadBlock": 133853171,
 "lastReadWib": "2026-11-16 ~10:01 WIB",
 "baselineNote": "BARU dari Boltbook EN+ZH run 1031 (tale.ai 10:01 WIB: totalSupply 0/999, counter flat 0; sudah di hot-leg-seen sejak 2026-11-02 21:19 WIB, S1/S2 false saat itu). On-chain blok 133853171: totalSupply() revert, totalMinted 0, MAX_SUPPLY 999, mintOpen revert; Sourcify 404 not_verified; bytecode 7.700 byte, registry_bytes TRUE (hanya hit bytes, tanpa ABI/free view terverifikasi) -> bentuk agent TIDAK terverifikasi (bytecode saja bukan bukti agent-shaped); 0 mint = BUKAN early lead (first mint belum ada); website/X tidak ditemukan (sweep: hanya token meme lain tak terkait). checked-not-lead / upcoming-0-mints, log-only, TIDAK dilaporkan.",
 "runNote1031_1116": "Run 1031: FROGY 0x5136 totalMinted 0, MAX_SUPPLY 999, Sourcify 404, registry-bytes saja, tanpa website/X -> checked-not-lead. DIAM.",
 "velocityLegPasses": False}
s["runNote1031_1116"] = "Run 1031: re-read 36/36 OK blok 133852948 (102,0 dtk). Velocity: SPARKS GAGAL (1,28x), MORFO GAGAL (3,80x tapi 19<20), AgentNOVA GAGAL (4,00x tapi 8<20), Bold Leonidas GAGAL (0,71x), Matrix GAGAL (1,50x tapi 3<20), CPASS GAGAL (8,00x tapi 8<20), Ledgera GAGAL; JADE tetap SOLD OUT 188/188 (sudah dilaporkan hot-leg 09:24, tidak dilaporkan ulang). 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru. Baru dicek: NEUPEN (bukan agent-shaped, situs ada tapi 0 sebutan agent) + FROGY (0 mint, registry-bytes saja) - keduanya checked-not-lead, DIAM. Scan FAST-FAIL (Ankr 401), watermark TETAP 132512564. Sourcify 10 terbaru: 0 S1/S2 (6 retry via curl OK). DIAM (tidak ada laporan chat)."
s["runNote1031_1116_scan"] = "Run 1031 scan pre-flight: Ankr getLogs HTTP 401 -> FAST-FAIL (log run-2026-11-16-1031-scanpreflight.log). Watermark TETAP 132512564 (head 133853061, gap 1.340.497). 5c dilewati (tanpa output scan)."
s["runNote1031_1116_boltbook"] = "Run 1031 Boltbook EN 200 (45.842 byte) / ZH 200 (46.094 byte); EN+ZH 5 alamat distinct (set sama); 3 alamat 'baru' vs snapshot-keys: FROGY 0x5136 (totalSupply 0/999, tale.ai 10:01 WIB - checked-not-lead) + NEUPEN 0x91a1 (census nanomind.ai 10:02 WIB, freeClaimed 792/7.000 - checked-not-lead, bukan agent-shaped) + BOLT 0xBbDd (infra, dikenal). Lainnya dikenal: BoltRewards 0x8269 (infra), 0x779f (dikenal). Mention baru: FROGY (tale.ai), NEUPEN census (nanomind.ai)."
s["runNote1031_1116_sweep"] = "Run 1031 sweep EN+ZH (subagent rute 3/5b/6): 0 project baru terkonfirmasi sebagai lead/kandidat. Perubahan status: Dragon Agents free lane TUTUP 2026-11-16 ~08:41 WIB (freeClaimed 888/888, hanya paid 0,0002 BNB tersisa; sudah age-excluded dari watchlist, dicatat saja); PONKE free habis 555/555 (tutup 16 Nov 19:00 WIB). Age-excluded yang muncul: LUMO (0x1E34, publikasi ~10 Nov, klaim butuh permit EIP-712 + posting X manual), STAMP PASS (0x202d, 9 Nov), RIGBYPASS (0xe657, 10 Nov). Hit lama: PocketAi, Oathbots, LeadLoop, NEXUS CORE, AGENT ID Card, Saturnagent (totalSupply 1.818/2.000), AGENT COSMOS, Agent Zet, YAMA, NOVRA, UFO/NEBULA, VISION, BAYC sale (free 2.000/2.000 habis). Binance Square 6a: hanya post 25 Okt-5 Nov, 0 segar 16 Nov. Odaily newsflash (10:08 WIB): 16 flash terbaru soal ETF/Nvidia/pasar, 0 kata agent. PANews (10:08 WIB): Vitalik/ETH, Nvidia, Solana Breakpoint, 0 pengumuman Agent ID/free-mint. DappBay tidak dipakai (tidak ada proyek baru yang butuh cek website; situs NEUPEN sendiri mencetak kontraknya). FROGY/NEUPEN: tanpa website/X publik selain situs NEUPEN via contractURI. twitterapi.io tidak dipanggil."
s["runNote1031_1116_binanceai"] = "Run 1031 track-B binanceai.fun: TIDAK BERUBAH (launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed user=0, blok 133852948) - fase refund, DIAM."
_br = json.load(open(BASE + "scan-bridge.json")).get("contracts", {})
_snap_addrs = { (v.get("address") or "").lower() for v in list(s.get("contracts", {}).values()) + list(s.get("track_c", {}).values()) if isinstance(v, dict) }
_br_addrs = { k.lower() for k in _br.keys() }
_missing = sorted(_br_addrs - _snap_addrs)
_disc = sum(1 for v in _br.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
s["runNote1031_1116_bridge"] = f"Run 1031 bridge (read-only): {len(_br)} kontrak bridge, {len(_br_addrs & _snap_addrs)}/{len(_br)} sudah di snapshot, {len(_missing)} baru: {_missing if _missing else 'tidak ada'}, {_disc} same_owner_discarded. Tidak ada temuan pelengkap baru / promosi run ini. Job ini tidak menulis bridge."
s["last_run_wib"] = "2026-11-16 ~10:01 WIB"
s["last_run_note"] = "Run 1031: DIAM. 0 kandidat/strong/early/track-B/track-C baru. 2 kontrak baru dicek, semua checked-not-lead (NEUPEN bukan-agent-shaped, FROGY 0 mint). Dragon Agents + PONKE free habis (dicatat, sudah di luar watchlist)."
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(s["contracts"]), "| track_c now:", len(s.get("track_c", {})))
print("\n".join(log))
print("MERGE DONE")
