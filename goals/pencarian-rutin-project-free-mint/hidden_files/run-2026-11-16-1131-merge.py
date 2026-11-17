#!/usr/bin/env python3
"""Merge run 2026-11-16 11:31 WIB reread into onchain-snapshot.json.
FRESH dynamic merge (values from run-2026-11-16-1131-reread.json + snapshot).
Interval 30.0 min vs run 1101 (blok 133860836 -> 133864749). 37/37 reads OK.
- WOMEN totalMinted 319->333, freeMinted 333/333, freeRemaining 0 -> FREE POOL SOLD OUT.
  Strong lead gate-blocked reported once run 1031; now SOLD OUT -> report once + REMOVE from snapshot.
- Velocity: SEMUA GAGAL (MORFO +16 5.33x TAPI <20; SPARKS +10 0.77x; Bold Leonidas +4 4.0x TAPI <20;
  AgentNOVA +1; Matrix +1; CPASS +0; RAVE 334 FLAT; LumenFindings counter 6204->6222 bukan velocity).
- BNBPIG (baru dari sweep ZH run ini, Square 1 Nov): sale-shape S1 PASS, tapi freeMinted 5000/5000 = HABIS,
  mintingOpen=0, freeAvailable(user)=0 -> checked-not-lead-free-sold-out, masuk track_c, DIAM.
- Scan leg FAST-FAIL (Ankr 401). Watermark TETAP 132512564.
- Sourcify 10 terbaru: 0 S1/S2 (6 retry via curl OK). No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-1131")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-1131-reread.json"))
reads = r["reads"]; BLK = r["block"]; INTERVAL = 30.0
PRIMARY = {"AGCLUB":"totalMinted","MORFO":"totalMinted","NOISE":"totalMinted","RaceAgents":"totalSupply",
 "Zero":"totalMinted","HIVE":"totalSupply",
 "AgentNOVA":"totalSupply","SPARKS":"totalSupply","WANGCAI":"totalSupply",
 "YUANBAO":"totalSupply","PX24":"totalSupply","Zephyra":"totalMinted","LumenFindings":"totalSpecimens",
 "Pengu":"totalMinted","CPASS":"totalMinted","ORBIT":"totalSupply","TrashBandits":"totalMinted",
 "SKRR":"totalSupply","REOPIR":"totalSupply","FrieAgent-B751":"totalSupply","FrieAgent-c64d":"totalSupply",
 "Ledgera":"totalSupply","MAMI":"totalSupply","INKI":"totalSupply","HashcatDepot":"totalSupply",
 "OTV":"totalSupply","RAVE":"totalMinted","HANAMI":"totalSupply","CosmicSentinel":"totalSupply",
 "Matrix Agents":"totalSupply","Bold Leonidas":"totalSupply","ALIEN":"totalSupply","JADE":"totalSupply","WOMEN":"totalMinted"}
COPY = ["totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","FREE_CAP","FREE_MAX",
 "MAX_SUPPLY","mintOpen","mintStart","isFreePhase","balanceOf_user","freeRemaining",
 "freeClaimed_user","freeUsed_user","mintedBy_user","hasAgentId_user","holdsAgentId_user",
 "priceFor_user","priceFor_user_1","mintedByWallet_user","paused","TOKEN_PRICE","remainingSupply",
 "mintPriceFor_user_1","cost_user_1","freeMintedPerWallet_user","mintedPerWallet_user",
 "totalSpecimens","currentExperiment","genesisStart","genesisOpen","mintsBy_user","mintCountOf_user",
 "freeSharesLeft","openedAt","freeBooked_user","claimOpen","hasFreeClaimed_user","mintsLeft",
 "FREE_MINT_CAP","freeMintsLeft","PRICE","paidMinted","mintPrice","freeClaimedByAgent_masgayut",
 "freeClaimedByAgent_masgayut_ai","freeSupply","maxSupply","hasClaimedFree_user","mintStart","mintEnd","mintEnded","paidMinted","PAID_PRICE","PAID_SUPPLY","freeRemaining"]
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
    entry["lastReadWib"] = "2026-11-16 ~11:31 WIB"
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
 "SPARKS": "Run 1131 (blok 133864749, interval 30,0 mnt vs run 1101): totalSupply 912->922 (+10, 0,333/mnt vs prev 0,433 = 0,77x) -> velocity GAGAL; free%/umur/website MASIH UNVERIFIED -> tetap early lead, TIDAK preview/mint.",
 "MORFO": "Run 1131 (blok 133864749): totalMinted 844->860 (+16, 0,533/mnt vs prev 0,100 = 5,33x TAPI <20 token) -> velocity GAGAL.",
 "AgentNOVA": "Run 1131 (blok 133864749): totalSupply 651->652 (+1) -> velocity GAGAL.",
 "Bold Leonidas": "Run 1131 (blok 133864749): totalSupply 777->781 (+4, 0,133/mnt vs prev 0,033 = 4,00x TAPI <20 token) -> velocity GAGAL; mintPriceFor(user,1)=0 (slot gratis TERBUKA), balanceOf(user)=0, mintOpen=1; free%/umur/website MASIH UNVERIFIED -> tetap early lead.",
 "Matrix Agents": "Run 1131 (blok 133864749): totalSupply 478->479 (+1) -> velocity GAGAL; anomali freeMinted > totalSupply BERLANJUT.",
 "Ledgera": "Run 1131 (blok 133864749): totalSupply 2692 FLAT, freeClaimed 2685/5000 = 53,7% - BUKAN kandidat/strong lead.",
 "CPASS": "Run 1131 (blok 133864749): totalMinted 1737 FLAT -> velocity GAGAL.",
 "HIVE": "Run 1131 (blok 133864749): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.",
 "Zero": "Run 1131 (blok 133864749): totalSupply/freeClaimed GAGAL baca run ini (degradasi RPC, BUKAN nol); nilai lama dipertahankan, velocity TIDAK dihitung. balanceOf(user)=0.",
 "ALIEN": "Run 1131 (blok 133864749): totalSupply 0 TETAP, mintOpen=0 (BELUM DIBUKA), FREE_SUPPLY 1000/MAX_SUPPLY 1300, isFreePhase=1 -> tetap UPCOMING watchlist-only.",
 "WANGCAI": "Run 1131 (blok 133864749): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.",
 "YUANBAO": "Run 1131 (blok 133864749): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.",
 "LumenFindings": "Run 1131 (blok 133864749): totalSpecimens 6204->6222 - counter spesimen eksperimen, BUKAN velocity mint (item age-excluded). DIAM.",
 "DogeRageFi": "Run 1131 (blok 133864749): totalMinted 226, totalSupply 339.001 DRF, freeSupply 432 TETAP, mintOpen 1, mintedBy(user)=0, balanceOf(user)=0. Umur presisi MASIH UNVERIFIED; gate website MASIH GAGAL -> watchlist-only, DIAM.",
 "ORBIT": "Run 1131 (blok 133864749): freeClaimed 292/888 TETAP, claimOpen 1, hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.",
 "RigForge": "Run 1131 (blok 133864749): freeSharesLeft 639, openedAt 0, freeClaimed 361 - DIAM.",
 "JADE": "Run 1131 (blok 133864749): totalSupply 191 FLAT (free pool tetap 0). Sudah dilaporkan sold-out oleh hot-leg 09:24, TIDAK dilaporkan ulang. DIAM.",
 "RAVE": "Run 1131 (blok 133864749): totalMinted 334 FLAT, freeMinted 334/3000 = 11,1% (free% kuota UNVERIFIED - tanpa FREE_SUPPLY view). DIAM.",
 "WOMEN": "Run 1131 (blok 133864749): totalMinted 319->333 (+14), freeMinted 333/333 = 100%, freeRemaining 0 -> FREE POOL SOLD OUT. Strong lead gate-blocked (dilaporkan sekali run 1031) kini HABIS -> LAPOR SEKALI sold-out + HAPUS dari snapshot run ini. TIDAK preview/mint (pool habis).",
}
for name, note in N.items():
    entry, where = find_entry(name)
    if entry is not None:
        entry["runNote1131_1116"] = note
    else:
        log.append(f"NOTE-SKIP {name}: no entry in contracts/track_c")
ba = reads.get("BinanceAI-mint", {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
for k in ("launched","failed","isRefundPhase","totalShares"):
    if ba.get(k) is not None: pc[k] = ba[k]
if ba.get("tokenClaimed_user") is not None: pc["tokenClaimed_user"] = ba["tokenClaimed_user"]
pc["lastReadWib"] = "2026-11-16 ~11:31 WIB"
pc["runNote1131"] = "Run 1131: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133864749) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
bmentry, _ = find_entry("BinanceAI-mint")
if bmentry is not None:
    for k in ("launched","failed","isRefundPhase","totalShares"):
        if ba.get(k) is not None: bmentry[k] = ba[k]
    bmentry["lastReadBlock"] = BLK; bmentry["lastReadWib"] = "2026-11-16 ~11:31 WIB"
# BNBPIG - baru dari sweep ZH run 1131 (Binance Square 1 Nov, site bnbpig.pages.dev)
s.setdefault("track_c", {})["BNBPIG"] = {
 "address": "0xFd3D4E0D7A81534AdDD11f96FdD8008f942097F9",
 "token": "0x936B97CD42F482eF96c7903448E2522dc9e1bd4F",
 "pair": "0x814B4b5F5767dAe3FEd42605681478801975097C",
 "status": "checked-not-lead-free-sold-out-2026-11-16",
 "name": "BNBPIG",
 "site": "https://bnbpig.pages.dev",
 "freeMinted": 5000, "MAX_FREE": 5000, "sharesMinted": 5234, "MAX_SHARES": 15000,
 "poolOpen": 1, "mintingOpen": 0, "freeAvailable_user": 0, "freeClaimed_user": 0,
 "deadline": 1793802809,
 "firstSeenBlock": 133865268, "lastReadBlock": 133865268,
 "lastReadWib": "2026-11-16 ~11:31 WIB",
 "baselineNote": "BARU dari sweep ZH run 1131 (Binance Square 1 Nov 2026, post 383702295717157: free pool 4954/5000 saat itu, pool belum dibuka). Site bnbpig.pages.dev HTTP 200 (40.071 byte) masih menampilkan poolOpen=false di JS. On-chain blok 133865268: sale-shape S1 PASS (Sourcify exact_match, mint + quote + freeAvailable/freeClaimed/freeMinted + agentId/hasAgentId) TAPI freeMinted 5000/5000 = 100% HABIS, mintingOpen=0, freeAvailable(user)=0, quote(user,1) revert (minting tertutup). Token 0x936B...bd4F, pair 0x814B...097C, deadline 1793802809. -> checked-not-lead free-sold-out, DIAM (tidak pernah dilaporkan sebagai lead).",
 "runNote1131_1116": "Run 1131: BNBPIG freeMinted 5000/5000 = 100% SOLD OUT free (mintingOpen=0) -> checked-not-lead. DIAM.",
 "velocityLegPasses": False}
# Agent Grove grove-check (file run-2026-11-16-1131-grove-check.json, blok 133865087 ~11:31 WIB)
gr = s["contracts"].get("Agent Grove")
if gr is not None:
    gr["runNote1131_1116"] = "Run 1131: grove-check (blok 133865087): freeOpen=false, freeClaimed(user)=false -> MASIH BELUM DIBUKA, tetap upcoming watchlist-only. DIAM."
    gr["lastReadBlock"] = 133865087
    gr["lastReadWib"] = "2026-11-16 ~11:31 WIB"
# WOMEN sold out -> REMOVE from snapshot (tombstone kept in top-level notes)
women = s["contracts"].pop("WOMEN", None)
s["runNote1131_1116"] = "Run 1131: re-read 37/37 OK blok 133864749 (246,5 dtk). Velocity: SEMUA GAGAL (MORFO +16 5,33x TAPI <20; SPARKS +10 0,77x; Bold Leonidas +4 4,00x TAPI <20; AgentNOVA +1; Matrix +1; CPASS +0; RAVE totalMinted 334 FLAT). 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru. WOMEN FREE POOL SOLD OUT (freeMinted 333/333, freeRemaining 0) - LAPOR SEKALI + HAPUS dari snapshot run ini. BNBPIG baru dicek: free pool 5000/5000 habis -> checked-not-lead (track_c), DIAM. Scan FAST-FAIL (Ankr 401), watermark TETAP 132512564. Sourcify 10 terbaru: 0 S1/S2 (6 retry via curl OK). 1 laporan chat: WOMEN sold-out."
s["runNote1131_1116_scan"] = "Run 1131 scan pre-flight: Ankr getLogs HTTP 401 -> FAST-FAIL (log run-2026-11-16-1131-scanpreflight.log). Watermark TETAP 132512564 (head 133864957, gap 1.352.393). 5c dilewati (tanpa output scan)."
s["runNote1131_1116_boltbook"] = "Run 1131 Boltbook EN 200 (47.490 byte) / ZH 200 (47.712 byte); EN+ZH 11 alamat distinct (set sama); 10 in-snapshot, 1 'baru' palsu: 0x181b... = tx hash HIHI10 (bukan kontrak). WOMEN muncul di front page via post cskh.ai: '333/1.000 minted (0 free left)' - terkonfirmasi on-chain run ini (freeMinted 333/333). Lainnya dikenal: GMC 0x0887, BUBB 0x0d72, ONLYAI Crystals 0x1564, NEUPEN 0x91a1, MATRIX 0x1f66, BOLD 0x84bc, DRAGON 0xad0d, BoltRewards 0x8269 (infra), BOLT 0xBbDd."
s["runNote1131_1116_sweep"] = "Run 1131 sweep EN+ZH (rute 3/5b/6): EN - Agentic Gangster + RIGBYPASS (keduanya sudah checked-not-lead free habis, tidak dicek ulang) + MOLT AGENT (6 Nov, free habis per AirdropBuzz, tidak dicek ulang) + AGENT MAO (situs 530, paused, lama) + BAS Medium (analisis Agent ID, tanpa proyek baru). ZH - AGENT COSMOS 0x3Aed (sudah di snapshot, age-excluded 12 Nov) + First-Dollar Grove 0x5646 (sudah di snapshot, age-excluded 11 Nov) + BNBPIG (BARU dicek run ini: sale-shape S1 PASS tapi freeMinted 5000/5000 habis, mintingOpen=0 -> checked-not-lead, track_c) + First-Dollar Sparks (SPARKS, sudah di snapshot early lead) + QILIN/SAFU/PROXY/Transmisi (1 Nov, lama). Odaily newsflash (11:3x WIB): HTTP 200, 0 kata 'agent'. PANews tidak dicek terpisah run ini (sweep search tidak menemukan pengumuman segar 16 Nov). DappBay tidak dipakai (tidak ada proyek baru yang butuh cek bukti website). Catatan keamanan: tidak ada pola instruksi tertanam baru di hasil pencarian run ini; run tetap read-only, tanpa preview/mint/eksekusi. twitterapi.io tidak dipanggil."
s["runNote1131_1116_binanceai"] = "Run 1131 track-B binanceai.fun: TIDAK BERUBAH (launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed user=0, blok 133864749) - fase refund, DIAM."
s["runNote1131_1116_women_soldout"] = "WOMEN SOLD OUT run 1131: totalMinted 319->333, freeMinted 333/333 = 100%, freeRemaining 0 (blok 133864749). Strong lead gate-blocked dilaporkan sekali run 1031 (free 282/333 = 84,7%, gate website gagal: women-nft.surge.sh tidak mencetak kontrak). Pool habis sebelum gate terbuka; TIDAK ADA mint (user tidak sempat mint; hasClaimedFree(user)=0, balanceOf=0). Entri DIHAPUS dari snapshot run ini; jangan dilaporkan ulang."
_br = json.load(open(BASE + "scan-bridge.json")).get("contracts", {})
_snap_addrs = { (v.get("address") or "").lower() for v in list(s.get("contracts", {}).values()) + list(s.get("track_c", {}).values()) if isinstance(v, dict) }
_br_addrs = { k.lower() for k in _br.keys() }
_missing = sorted(_br_addrs - _snap_addrs)
_disc = sum(1 for v in _br.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
s["runNote1131_1116_bridge"] = f"Run 1131 bridge (read-only): {len(_br)} kontrak bridge, {len(_br_addrs & _snap_addrs)}/{len(_br)} sudah di snapshot, {len(_missing)} baru: {_missing if _missing else 'tidak ada'}, {_disc} same_owner_discarded. Tidak ada temuan pelengkap baru / promosi run ini. Job ini tidak menulis bridge."
s["last_run_wib"] = "2026-11-16 ~11:31 WIB"
s["last_run_note"] = "Run 1131: WOMEN SOLD OUT (free 333/333) - lapor sekali + hapus dari snapshot. 0 kandidat/strong/early/track-B/track-C baru. BNBPIG baru dicek, free pool habis -> checked-not-lead. Ankr 401 berlanjut; watermark 132512564, gap 1.352.393."
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(s["contracts"]), "| track_c now:", len(s.get("track_c", {})))
print("WOMEN removed:", women is not None)
print("\n".join(log))
print("MERGE DONE")
