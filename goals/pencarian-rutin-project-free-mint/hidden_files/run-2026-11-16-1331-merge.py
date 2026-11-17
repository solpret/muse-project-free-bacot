#!/usr/bin/env python3
"""Merge run 2026-11-16 13:31 WIB reread into onchain-snapshot.json + Flare-bd6f triage.
Interval 31.52 min (block timestamps: 133876357 ts 1794809037 -> 133880559 ts 1794810928).
36/36 reads OK (127.6 dtk). Velocity: TIDAK ADA yang LOLOS run ini. SPARKS +6 GAGAL (0.83x, <20);
NOISE +4 GAGAL (2.22x tapi <20); MORFO +2 GAGAL (1.11x, <20); Matrix +1 GAGAL (0.55x); Bold Leonidas +2 GAGAL (0.37x);
Ledgera +4 GAGAL; sisanya 0/flat. LumenFindings totalSpecimens +93 BUKAN velocity mint (counter eksperimen) - velocityLegPasses dipaksa False.
BARU dicek run ini: Flare Agent KETIGA 0xbd6ff7ed... (Boltbook tetternice.ai, recheck 13:31, klaim 4900/5000 free 98%) -
totalSupply 4900/MAX_SUPPLY 5000 terverifikasi on-chain, registry bytes ADA di bytecode (agent-shaped), TAPI Sourcify NOT verified,
free views (freeClaimed/freeMinted/FREE_SUPPLY) revert -> free% UNVERIFIED (4900/5000 adalah % MAX, bukan kuota gratis),
umur UNVERIFIED (first-mint check TERBLOKIR: Ankr 401 + bsc-dataseed eth_getLogs -32005 limit exceeded bahkan di jendela 100 blok),
mintedBy(user)=0, balanceOf(user)=0, owner 0xe0808a338d96171fa9bde4d4d1897692392a0cbb -> watchlist-only, masuk snapshot (preseden Flare-628a),
BUKAN lead/kandidat/strong lead, TIDAK dilaporkan, TIDAK preview/mint.
UNSOLVABLE 0x9e95da84... (Boltbook dieuxuan50.ai, 401/25062 free 1,6%) = proyek Unsolvable milik user sendiri - BUKAN kandidat Free Bacot, log only.
Audit post 0xc528122c... (drzein.ai, "Low-Level Dispatcher Audit") bukan proyek mint - log only.
Read-only except the snapshot write + backup. No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-1331")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-1331-reread.json"))
reads = r["reads"]; BLK = r["block"]; INTERVAL = 31.52
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
 "freeClaimedByAgent_masgayut_ai","freeSupply","maxSupply","hasClaimedFree_user","mintEnd","mintEnded",
 "PAID_PRICE","PAID_SUPPLY"]
# Prev-interval (run 1301) rates, for items whose snapshot rate field is stale (0.0)
PREV_RATE_OVERRIDE = {"SPARKS": 0.229, "MORFO": 0.057, "Bold Leonidas": 0.172}
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
    entry["lastReadWib"] = "2026-11-16 ~13:31 WIB"
    if old_prim is not None and new_prim is not None:
        prev_rate = entry.get("currentRatePerMin")
        if not prev_rate:
            prev_rate = PREV_RATE_OVERRIDE.get(name)
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

# LumenFindings guard: totalSpecimens is an experiment counter, never mint velocity
_lf, _ = find_entry("LumenFindings")
if _lf is not None:
    _lf["velocityLegPasses"] = False
    _lf["velocityNote"] = "totalSpecimens BUKAN velocity mint (counter eksperimen); velocityLegPasses dipaksa False."

def note(name, text):
    entry, where = find_entry(name)
    if entry is not None:
        entry["runNote1331_1116"] = text
    else:
        log.append(f"NOTE-SKIP {name}: no entry")

note("SPARKS", "Run 1331 (blok 133880559, interval 31,52 mnt vs run 1301): totalSupply 964->970 (+6, 0,190/mnt vs prev 0,229 = 0,83x, <20 token) -> velocity GAGAL; free%/umur/website MASIH UNVERIFIED -> tetap early lead, TIDAK preview/mint.")
note("MORFO", "Run 1331 (blok 133880559): totalMinted 881->883 (+2, 0,063/mnt vs prev 0,057 = 1,11x, <20 token) -> velocity GAGAL.")
note("NOISE", "Run 1331 (blok 133880559): totalMinted 1356->1360 (+4, 0,127/mnt vs prev 0,057 = 2,22x TAPI <20 token) -> velocity GAGAL.")
note("AgentNOVA", "Run 1331 (blok 133880559): totalSupply 653 FLAT -> velocity GAGAL.")
note("Bold Leonidas", "Run 1331 (blok 133880559): totalSupply 794->796 (+2, 0,063/mnt vs prev 0,172 = 0,37x, <20 token) -> velocity GAGAL; mintPriceFor(user,1)=0 (slot gratis TERBUKA), balanceOf(user)=0, mintOpen=1; free%/umur/website MASIH UNVERIFIED -> tetap early lead.")
note("Matrix Agents", "Run 1331 (blok 133880559): totalSupply 536->537 (+1, 0,032/mnt vs prev 0,057 = 0,55x, <20 token) -> velocity GAGAL; freeMinted 540/1000 = 54,0% (<70% ambang strong lead), umur MASIH UNVERIFIED, X unverified -> tetap early lead, BUKAN kandidat/strong lead, TIDAK preview/mint. Anomali freeMinted (540) > totalSupply (537) BERLANJUT; freeClaimedByAgent(user)=0.")
note("Ledgera", "Run 1331 (blok 133880559): totalSupply 2692->2696 (+4, 0,127/mnt, <20) -> velocity GAGAL; freeClaimed 2689/5000 = 53,8% - BUKAN kandidat/strong lead.")
note("CPASS", "Run 1331 (blok 133880559): totalMinted 1737 FLAT -> velocity GAGAL.")
note("HIVE", "Run 1331 (blok 133880559): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Zero", "Run 1331 (blok 133880559): totalSupply/freeClaimed GAGAL baca run ini (degradasi RPC, BUKAN nol); nilai lama dipertahankan, velocity TIDAK dihitung. balanceOf(user)=0.")
note("ALIEN", "Run 1331 (blok 133880559): totalSupply 0 TETAP, mintOpen=0 (BELUM DIBUKA), FREE_SUPPLY 1000/MAX_SUPPLY 1300, isFreePhase=1 -> tetap UPCOMING watchlist-only.")
note("WANGCAI", "Run 1331 (blok 133880559): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.")
note("YUANBAO", "Run 1331 (blok 133880559): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.")
note("LumenFindings", "Run 1331 (blok 133880559): totalSpecimens 6293->6386 (+93) - counter spesimen eksperimen, BUKAN velocity mint (item age-excluded); velocityLegPasses dipaksa False run ini. DIAM.")
note("DogeRageFi", "Run 1331 (blok 133880559): totalMinted 227 FLAT, freeSupply 432 TETAP, mintOpen 1, mintedBy(user)=0, balanceOf(user)=0. Umur presisi MASIH UNVERIFIED; gate website MASIH GAGAL -> watchlist-only, DIAM.")
note("ORBIT", "Run 1331 (blok 133880559): freeClaimed 293->294/888, claimOpen 1, hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM. (totalSupply adalah jumlah token, bukan hitungan NFT - velocity tidak dihitung dari angka itu.)")
note("RigForge", "Run 1331 (blok 133880559): freeSharesLeft 639, openedAt 0, freeClaimed 361 - DIAM.")
note("JADE", "Run 1331 (blok 133880559): totalSupply 191 FLAT (free pool tetap 0). DIAM.")
note("RAVE", "Run 1331 (blok 133880559): totalMinted 334->335 (+1), freeMinted 335/3000 = 11,2% (free% kuota UNVERIFIED - tanpa FREE_SUPPLY view). DIAM.")
note("AGCLUB", "Run 1331 (blok 133880559): totalMinted 486->487 (+1), freeMinted 487/888 = 54,8% (FREE_CAP 888), mintOpen 1, balanceOf(user)=0 -> velocity GAGAL (0,032/mnt).")
note("Zephyra", "Run 1331 (blok 133880559): totalMinted 923 FLAT -> velocity GAGAL; priceFor(user,1)=0, mintedBy(user)=0, hasAgentId(user)=1.")
# RigForge / DogeRageFi field copy (track_c, not in PRIMARY)
for nm, fields in (("RigForge", ["freeSharesLeft","openedAt","freeClaimed","freeBooked_user"]),
                   ("DogeRageFi", ["totalMinted","freeSupply","maxSupply","mintOpen","mintedBy_user","balanceOf_user"])):
    rd = reads.get(nm); entry, where = find_entry(nm)
    if rd is not None and entry is not None:
        views = rd.get("views") or {}
        for k in fields:
            if views.get(k) is not None: entry[k] = views[k]
        entry["lastReadBlock"] = BLK
        entry["lastReadWib"] = "2026-11-16 ~13:31 WIB"
    else:
        log.append(f"TRACKC-SKIP {nm}: read={rd is not None} entry={where}")
# Track-B binanceai.fun pending claim
ba = reads.get("BinanceAI-mint", {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
for k in ("launched","failed","isRefundPhase","totalShares"):
    if ba.get(k) is not None: pc[k] = ba[k]
if ba.get("tokenClaimed_user") is not None: pc["tokenClaimed_user"] = ba["tokenClaimed_user"]
pc["lastReadWib"] = "2026-11-16 ~13:31 WIB"
pc["runNote1331"] = "Run 1331: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133880559) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
bmentry, _ = find_entry("BinanceAI-mint")
if bmentry is not None:
    for k in ("launched","failed","isRefundPhase","totalShares"):
        if ba.get(k) is not None: bmentry[k] = ba[k]
    bmentry["lastReadBlock"] = BLK; bmentry["lastReadWib"] = "2026-11-16 ~13:31 WIB"
# Agent Grove grove-check
gr = json.load(open(BASE + "run-2026-11-16-1331-grove-check.json"))
ge, _ = find_entry("Agent Grove")
if ge is not None:
    ge["runNote1331_1116"] = "Run 1331: grove-check (blok 133880559): freeOpen=0/false, freeClaimed(user)=0 -> MASIH BELUM DIBUKA, tetap upcoming watchlist-only. DIAM."
    ge["freeOpen"] = gr.get("freeOpen")
    ge["lastReadBlock"] = gr.get("block")
    ge["lastReadWib"] = "2026-11-16 ~13:31 WIB"
# NEW: Flare Agent third contract 0xbd6ff7ed... -> snapshot watchlist-only (precedent Flare-628a)
s.setdefault("contracts", {})["Flare Agent-bd6f"] = {
    "address": "0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599",
    "status": "watchlist-only-age-unverified-2026-11-16",
    "name": "Flare Agent",
    "kind": "ERC721",
    "totalSupply": 4900,
    "MAX_SUPPLY": 5000,
    "mintOpen": None,
    "code_len": 6799,
    "registryBytesInCode": True,
    "sourcify": "not_verified",
    "freePctVerified": None,
    "freePctNote": "free% UNVERIFIED: freeClaimed/freeMinted/FREE_SUPPLY semua revert; 4900/5000 adalah % MAX_SUPPLY, bukan kuota gratis terverifikasi.",
    "launchNote": "Umur UNVERIFIED: first-mint check TERBLOKIR dua jalur (Ankr 401 + bsc-dataseed eth_getLogs -32005 limit exceeded bahkan jendela 100 blok). Post Boltbook tetternice.ai 13:31 WIB adalah 'recheck', bukan pengumuman launch.",
    "baselineNote": "Kontrak KETIGA bernama Flare Agent (snapshot sudah punya 0xe2deb475... ts 9901, pertama terlihat 2026-11-09; dan 0x628a90f0... ts 9900, triase 2026-11-14). Triase run 1331: totalSupply 4900/MAX_SUPPLY 5000 terverifikasi on-chain, registry bytes ADA di bytecode (agent-shaped), Sourcify NOT verified, free views revert, mintedBy(user)=0, balanceOf(user)=0, owner 0xe0808a338d96171fa9bde4d4d1897692392a0cbb. free%/umur/website UNVERIFIED -> watchlist-only, BUKAN lead/kandidat/strong lead, TIDAK dilaporkan, TIDAK preview/mint.",
    "owner": "0xe0808a338d96171fa9bde4d4d1897692392a0cbb",
    "mintedBy_user": 0,
    "balanceOf_user": 0,
    "xVerified": False,
    "velocityVerified": False,
    "velocityLegPasses": False,
    "firstSeenWib": "2026-11-16 ~13:31 WIB",
    "firstSeenSource": "Boltbook tetternice.ai recheck 13:31 WIB",
    "lastReadBlock": BLK,
    "lastReadWib": "2026-11-16 ~13:31 WIB",
}
# Bridge comparison (read-only)
_br = json.load(open(BASE + "scan-bridge.json")).get("contracts", {})
_snap_addrs = { (v.get("address") or "").lower() for v in list(s.get("contracts", {}).values()) + list(s.get("track_c", {}).values()) if isinstance(v, dict) }
_br_addrs = { k.lower() for k in _br.keys() }
_missing = sorted(_br_addrs - _snap_addrs)
_disc = sum(1 for v in _br.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
s["runNote1331_1116_bridge"] = f"Run 1331 bridge (read-only): {len(_br)} kontrak bridge, {len(_br_addrs & _snap_addrs)}/{len(_br)} sudah di snapshot, {len(_missing)} baru: {_missing if _missing else 'tidak ada'}, {_disc} same_owner_discarded. Tidak ada temuan pelengkap baru / promosi run ini. Job ini tidak menulis bridge."
s["runNote1331_1116"] = ("Run 1331 (13:31 WIB): re-read 36/36 OK blok 133880559 (127,6 dtk, interval 31,52 mnt vs run 1301 dari timestamp blok). "
 "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview. "
 "Velocity: TIDAK ADA yang lolos; SPARKS +6 GAGAL (0,83x, <20); NOISE +4 GAGAL (2,22x tapi <20); MORFO +2 GAGAL (1,11x, <20); Matrix +1 GAGAL (0,55x) - free% 54,0% <70%, umur/X unverified, tetap early lead; Bold Leonidas +2 GAGAL (0,37x); Ledgera +4 GAGAL; sisanya 0/flat. "
 "LumenFindings totalSpecimens +93 BUKAN velocity (counter eksperimen) - velocityLegPasses dipaksa False. "
 "BARU dicek run ini: Flare Agent KETIGA 0xbd6ff7ed... (Boltbook tetternice.ai, klaim 4900/5000 free 98%) - totalSupply 4900/5000 terverifikasi on-chain, registry bytes ADA (agent-shaped), TAPI Sourcify NOT verified, free views revert (free% UNVERIFIED), umur UNVERIFIED (first-mint check terblokir: Ankr 401 + bsc-dataseed getLogs -32005 bahkan 100 blok) -> watchlist-only, masuk snapshot, BUKAN lead, TIDAK dilaporkan; "
 "UNSOLVABLE 0x9e95da84... (Boltbook dieuxuan50.ai, 401/25062 free 1,6%) = proyek Unsolvable milik user sendiri, BUKAN kandidat Free Bacot, log only; "
 "audit post 0xc528122c... (drzein.ai) bukan proyek mint, log only. "
 "Track-B binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund). ALIEN + Agent Grove masih BELUM DIBUKA. "
 "Boltbook EN 200 (46.152 byte) / ZH 200 (46.299 byte): 9/9 alamat, 3 'baru' vs snapshot (Flare-bd6f + UNSOLVABLE + audit post, ketiganya bukan lead). "
 "Sweep EN+ZH: hanya proyek lama (Agentic Gangster 9 Nov, Meow Cards 10 Nov, RIGBYPASS 10 Nov, AGENT MAO paused, QILIN/SAFU/PROXY 1 Nov, BN Agent Trials musim berakhir 8 Nov, Xuanwu 24 Okt). "
 "Odaily newsflash ~13:37 WIB: 0 kata 'agent'. Scan leg FAST-FAIL (Ankr 401, 7,07 dtk); watermark TETAP 132512564 (head 133880280, gap 1.367.716). "
 "Sourcify 10 terbaru (top verifiedAt 06:33:12Z = 13:33 WIB): 0 S1/S2 (9 IncompleteRead/RemoteDisconnected, semua retry via curl OK). Track-C 5c: TIDAK JALAN (tidak ada output scan - Ankr 401). Bridge 116/116 sudah di snapshot, 0 baru. Verdict akhir: DIAM (tidak ada laporan chat).")
s["last_run_note"] = ("Run 1331: DIAM - 0 kandidat/strong/early/track-B/track-C baru. Velocity tidak ada yang lolos. "
 "Flare Agent ketiga (0xbd6f...) masuk snapshot sebagai watchlist-only (free%/umur UNVERIFIED, first-mint check terblokir dua jalur). Ankr 401 berlanjut; watermark scan tertahan di 132512564.")
s["last_run_wib"] = "2026-11-16 ~13:31 WIB"
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(s["contracts"]), "| track_c now:", len(s.get("track_c", {})))
print("\n".join(log))
print("MERGE DONE")
