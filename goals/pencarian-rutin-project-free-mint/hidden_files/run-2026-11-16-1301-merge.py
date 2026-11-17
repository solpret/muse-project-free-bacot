#!/usr/bin/env python3
"""Merge run 2026-11-16 13:01 WIB reread into onchain-snapshot.json + Lunar Atlas triage.
Interval 17.47 min (block timestamps: 133876357 ts 1794807989 -> 133876357 ts 1794809037 = 1048s).
36/36 reads OK. Velocity: TIDAK ADA yang LOLOS run ini. Matrix TURUN dari LOLOS run 1231 (+39) ke GAGAL (+1, 0,057/mnt vs prev 0,955 = 0,06x, <20) - free% 53,9% tetap <70%, umur/X unverified -> tetap early lead, TIDAK preview/mint. SPARKS +4 GAGAL (0,85x, <20); MORFO +1 GAGAL; Bold Leonidas +3 GAGAL (1,17x tapi <20); Zephyra 0 GAGAL. LumenFindings totalSpecimens +64 BUKAN velocity mint (counter eksperimen, item age-excluded) - velocityLegPasses dipaksa False.
PEPE 0x7E92... (Boltbook hensyah08.ai, freeMinted 222/500): user SUDAH MINT 2026-11-16 ~10:47 WIB (tx 0xfef4abcc..., hot-leg-reported) - BUKAN lead, tidak dilaporkan, tanpa entri snapshot.
Backdoor Pass BDPASS 0x9c6a... (Boltbook cskh.ai/drhmwt.ai, totalSupply 1320/20000 terverifikasi on-chain): Sourcify exact_match verifiedAt 2026-11-08T16:41:51Z; ABI 24 fungsi TANPA free view, TANPA registry/agent ref, TANPA quote; registry bytes TIDAK ada di bytecode; mint flatlined (0 mint dalam 800 blok) -> BUKAN agent-shaped, BUKAN lead - log only, tanpa entri snapshot.
Read-only except the snapshot write Read-only except the snapshot write + backup. No preview/mint."""
import json, shutil, re
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-1301")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-1301-reread.json"))
reads = r["reads"]; BLK = r["block"]; INTERVAL = 17.47
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
# Prev-interval (run 1201) rates from run-1201 runlog, for items whose snapshot rate field is stale (0.0)
PREV_RATE_OVERRIDE = {"SPARKS": 0.269, "MORFO": 0.073, "Bold Leonidas": 0.147}
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
    entry["lastReadWib"] = "2026-11-16 ~13:01 WIB"
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
        entry["runNote1301_1116"] = text
    else:
        log.append(f"NOTE-SKIP {name}: no entry")

note("SPARKS", "Run 1301 (blok 133876357, interval 17,47 mnt vs run 1231): totalSupply 960->964 (+4, 0,229/mnt vs prev 0,269 = 0,85x, <20 token) -> velocity GAGAL; free%/umur/website MASIH UNVERIFIED -> tetap early lead, TIDAK preview/mint.")
note("MORFO", "Run 1301 (blok 133876357): totalMinted 880->881 (+1, 0,057/mnt vs prev 0,073 = 0,78x, <20 token) -> velocity GAGAL.")
note("AgentNOVA", "Run 1301 (blok 133876357): totalSupply 652->653 (+1, <20) -> velocity GAGAL.")
note("Bold Leonidas", "Run 1301 (blok 133876357): totalSupply 791->794 (+3, 0,172/mnt vs prev 0,147 = 1,17x, <20 token) -> velocity GAGAL; mintPriceFor(user,1)=0 (slot gratis TERBUKA), balanceOf(user)=0, mintOpen=1; free%/umur/website MASIH UNVERIFIED -> tetap early lead.")
note("Matrix Agents", "Run 1301 (blok 133876357): totalSupply 535->536 (+1, 0,057/mnt vs prev 0,955 = 0,06x, <20 token) -> velocity GAGAL (TURUN dari LOLOS run 1231 +39); freeMinted 539/1000 = 53,9% (<70% ambang strong lead), umur MASIH UNVERIFIED, X unverified -> tetap early lead, BUKAN kandidat/strong lead, TIDAK preview/mint. Anomali freeMinted (539) > totalSupply (536) BERLANJUT; freeClaimedByAgent(user)=0.")
note("Ledgera", "Run 1301 (blok 133876357): totalSupply 2692 FLAT, freeClaimed 2685/5000 = 53,7% - BUKAN kandidat/strong lead (velocity 0).")
note("CPASS", "Run 1301 (blok 133876357): totalMinted 1737 FLAT -> velocity GAGAL.")
note("HIVE", "Run 1301 (blok 133876357): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Zero", "Run 1301 (blok 133876357): totalSupply/freeClaimed GAGAL baca run ini (degradasi RPC, BUKAN nol); nilai lama dipertahankan, velocity TIDAK dihitung. balanceOf(user)=0.")
note("ALIEN", "Run 1301 (blok 133876357): totalSupply 0 TETAP, mintOpen=0 (BELUM DIBUKA), FREE_SUPPLY 1000/MAX_SUPPLY 1300, isFreePhase=1 -> tetap UPCOMING watchlist-only.")
note("WANGCAI", "Run 1301 (blok 133876357): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.")
note("YUANBAO", "Run 1301 (blok 133876357): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.")
note("LumenFindings", "Run 1301 (blok 133876357): totalSpecimens 6229->6293 (+64) - counter spesimen eksperimen, BUKAN velocity mint (item age-excluded); velocityLegPasses dipaksa False run ini. DIAM.")
note("DogeRageFi", "Run 1301 (blok 133876357): totalMinted 227 FLAT, freeSupply 432 TETAP, mintOpen 1, mintedBy(user)=0, balanceOf(user)=0. Umur presisi MASIH UNVERIFIED; gate website MASIH GAGAL -> watchlist-only, DIAM.")
note("ORBIT", "Run 1301 (blok 133876357): freeClaimed 293/888 FLAT, claimOpen 1, hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.")
note("RigForge", "Run 1301 (blok 133876357): freeSharesLeft 639, openedAt 0, freeClaimed 361 - DIAM.")
note("JADE", "Run 1301 (blok 133876357): totalSupply 191 FLAT (free pool tetap 0). DIAM.")
note("RAVE", "Run 1301 (blok 133876357): totalMinted 334 FLAT, freeMinted 334/3000 = 11,1% (free% kuota UNVERIFIED - tanpa FREE_SUPPLY view). DIAM.")
note("AGCLUB", "Run 1301 (blok 133876357): totalMinted 486 FLAT, freeMinted 486/888 = 54,7% (FREE_CAP 888), mintOpen 1, balanceOf(user)=0 -> velocity GAGAL (0).")
note("NOISE", "Run 1301 (blok 133876357): totalMinted 1355->1356 (+1, <20) -> velocity GAGAL.")
note("Zephyra", "Run 1301 (blok 133876357): totalMinted 923 FLAT -> velocity GAGAL; priceFor(user,1)=0, mintedBy(user)=0, hasAgentId(user)=1.")
# RigForge / DogeRageFi field copy (track_c, not in PRIMARY)
for nm, fields in (("RigForge", ["freeSharesLeft","openedAt","freeClaimed","freeBooked_user"]),
                   ("DogeRageFi", ["totalMinted","freeSupply","maxSupply","mintOpen","mintedBy_user","balanceOf_user"])):
    rd = reads.get(nm); entry, where = find_entry(nm)
    if rd is not None and entry is not None:
        views = rd.get("views") or {}
        for k in fields:
            if views.get(k) is not None: entry[k] = views[k]
        entry["lastReadBlock"] = BLK
        entry["lastReadWib"] = "2026-11-16 ~13:01 WIB"
    else:
        log.append(f"TRACKC-SKIP {nm}: read={rd is not None} entry={where}")
# Track-B binanceai.fun pending claim
ba = reads.get("BinanceAI-mint", {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
for k in ("launched","failed","isRefundPhase","totalShares"):
    if ba.get(k) is not None: pc[k] = ba[k]
if ba.get("tokenClaimed_user") is not None: pc["tokenClaimed_user"] = ba["tokenClaimed_user"]
pc["lastReadWib"] = "2026-11-16 ~13:01 WIB"
pc["runNote1301"] = "Run 1301: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133876357) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
bmentry, _ = find_entry("BinanceAI-mint")
if bmentry is not None:
    for k in ("launched","failed","isRefundPhase","totalShares"):
        if ba.get(k) is not None: bmentry[k] = ba[k]
    bmentry["lastReadBlock"] = BLK; bmentry["lastReadWib"] = "2026-11-16 ~13:01 WIB"
# Agent Grove grove-check
gr = json.load(open(BASE + "run-2026-11-16-1301-grove-check.json"))
ge, _ = find_entry("Agent Grove")
if ge is not None:
    ge["runNote1301_1116"] = "Run 1301: grove-check (blok 133876357): freeOpen=0/false, freeClaimed(user)=0 -> MASIH BELUM DIBUKA, tetap upcoming watchlist-only. DIAM."
    ge["freeOpen"] = gr.get("freeOpen")
    ge["lastReadBlock"] = gr.get("block")
    ge["lastReadWib"] = "2026-11-16 ~13:01 WIB"
# Bridge comparison (read-only)
_br = json.load(open(BASE + "scan-bridge.json")).get("contracts", {})
_snap_addrs = { (v.get("address") or "").lower() for v in list(s.get("contracts", {}).values()) + list(s.get("track_c", {}).values()) if isinstance(v, dict) }
_br_addrs = { k.lower() for k in _br.keys() }
_missing = sorted(_br_addrs - _snap_addrs)
_disc = sum(1 for v in _br.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
s["runNote1301_1116_bridge"] = f"Run 1301 bridge (read-only): {len(_br)} kontrak bridge, {len(_br_addrs & _snap_addrs)}/{len(_br)} sudah di snapshot, {len(_missing)} baru: {_missing if _missing else 'tidak ada'}, {_disc} same_owner_discarded. Tidak ada temuan pelengkap baru / promosi run ini. Job ini tidak menulis bridge."
s["runNote1301_1116"] = ("Run 1301 (13:01 WIB): re-read 36/36 OK blok 133876357 (84,1 dtk, interval 17,47 mnt vs run 1231 dari timestamp blok). "
 "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview. "
 "Velocity: TIDAK ADA yang lolos; Matrix TURUN dari LOLOS run 1231 ke GAGAL (+1, 0,06x) - free% 53,9% <70%, umur/X unverified, tetap early lead; "
 "SPARKS +4 GAGAL (0,85x, <20); MORFO +1 GAGAL; Bold Leonidas +3 GAGAL (1,17x tapi <20); Zephyra 0 GAGAL; sisanya 0/flat. "
 "LumenFindings totalSpecimens +64 BUKAN velocity (counter eksperimen) - velocityLegPasses dipaksa False. "
 "BARU dicek run ini: PEPE 0x7E92... (Boltbook hensyah08.ai, freeMinted 222/500) - user SUDAH MINT ~10:47 WIB (tx 0xfef4abcc...), BUKAN lead, diam; "
 "Backdoor Pass BDPASS 0x9c6a... (Boltbook cskh.ai/drhmwt.ai, totalSupply 1320/20000 terverifikasi on-chain, Sourcify exact_match verifiedAt 2026-11-08) - ABI tanpa free view/registry/quote, registry bytes TIDAK ada, mint flatlined -> BUKAN agent-shaped, BUKAN lead, log only. "
 "Track-B binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund). ALIEN + Agent Grove masih BELUM DIBUKA. "
 "Boltbook EN 200 (45.463 byte) / ZH 200 (45.830 byte): 9/8 alamat, 2 'baru' vs snapshot (PEPE + BDPASS, keduanya bukan lead). "
 "Sweep EN+ZH: hanya proyek lama (Oathbots 28 Okt, LeadLoop, hackou, AgentForge, Pixel Fox, AGENT ID cards, First-Dollar Grove, Coracle, Agentic Gangster 9 Nov, AGENT COSMOS, congge918 26 Okt). "
 "Odaily newsflash ~13:0x WIB: 0 kata 'agent'. Scan leg FAST-FAIL (Ankr 401, 1,08 dtk); watermark TETAP 132512564 (head 133876382, gap 1.363.818). "
 "Sourcify 10 terbaru (top verifiedAt 06:00:22Z = 13:00 WIB): 0 S1/S2 (8 IncompleteRead/RemoteDisconnected, semua retry via curl OK). Bridge 116/116 sudah di snapshot, 0 baru. Verdict akhir: DIAM (tidak ada laporan chat).")
s["last_run_note"] = ("Run 1301: DIAM - 0 kandidat/strong/early/track-B/track-C baru. Matrix velocity TURUN dari lolos ke gagal. "
 "PEPE user sudah mint; BDPASS bukan agent-shaped. Ankr 401 berlanjut; watermark scan tertahan di 132512564.")
s["last_run_wib"] = "2026-11-16 ~13:01 WIB"
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(s["contracts"]), "| track_c now:", len(s.get("track_c", {})))
print("\n".join(log))
print("MERGE DONE")
