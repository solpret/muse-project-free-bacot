#!/usr/bin/env python3
"""Merge run 2026-11-18 19:31 WIB re-read into onchain-snapshot.json (lean merge).
Reread via Quicknode tunnel: 291 calls, 5 chunk errors (calls 260-284,
bsccat views only - TimeoutError, egress degradasi). Block 134314259,
interval ~36,1 mnt vs 1901 (4809 blok x 0,45 dtk).
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. AgentBubble: velocity LOLOS (+56,
1,551/mnt, 49,9x) + free 88,3% TERVERIFIKASI + website TERVERIFIKASI, TAPI
umur TERBUKTI >24 jam (pertama teramati job ini 13 Nov ~17:31 WIB, 475 sudah
minted; masih terbuka 18 Nov 19:31, belum sold out) -> AGE-EXCLUDED, keluar
dari watchlist aktif (stub dipertahankan, status age-excluded-2026-11-18).
AONE track-C: freeMinted 5959 -> 7442 (minted-by-user, kuota user 0).
Read-only except snapshot. None/err values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1931-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1901-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~19:31 WIB"
BLOCK = reread["block"]; PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")
addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k
updated, missed, vel_pass = [], [], []
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name); continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply"); pval = pv.get("totalSupply"); view = "totalSupply"
    if not isinstance(fresh, int):
        fresh = v.get("totalMinted"); pval = pv.get("totalMinted"); view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if vel:
            vel_pass.append((name, minted, round(rate, 4), round(ratio, 2)))
        e["previousTotalSupply"] = pval; e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4); e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel; e["supplyView"] = view
    e["lastReadWib"] = NOW; e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (not in snapshot): {missed}")
print("velocity PASS:", vel_pass)

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote1931_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1931 (blok {BLOCK}, interval ~36,1 mnt vs 1901): freeMinted/totalMinted 365->370 (+5, <20) -> velocity GAGAL. free 370/999 = 37,0% (<50% kandidat, <70% strong lead). mintStart on-chain 1794922323 = 2026-11-17 20:32:03 WIB (umur ~23 jam, deadline 24 jam 20:32 WIB hari ini - run 20:31 nanti sudah lewat umur bila belum sold out). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 1931 (blok {BLOCK}): totalSupply 782->787 (+5), freeLeft 329->324 (FREE_SUPPLY 1111, inferred free 787/1111 = 70,8% - MELEWATI 70% secara INFERENSI SAJA, bukan free counter terverifikasi, jadi BUKAN strong lead; umur + website tetap UNVERIFIED). quote(user,1)=0, freeMintedByWallet 0, balance 0 -> slot TERBUKA. Velocity GAGAL (+5 <20). Tetap EARLY LEAD.")
note("DGF CARD", f"Run 1931 (blok {BLOCK}): totalMinted 1655->1657 (+2) -> velocity GAGAL. Umur/free% tetap UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD.")
note("AgentNOVA", f"Run 1931 (blok {BLOCK}): totalSupply 786->787 (+1) -> velocity GAGAL (<20). Bukan kandidat.")
note("Agent Bubble", f"Run 1931 (blok {BLOCK}): totalSupply 2051->2107 (+56, 1,551/mnt vs prev 0,0311 = 49,9x, >=20) -> velocity LOLOS. freeMinted 1906->1962/2222 = 88,3% TERVERIFIKASI (>70%). Website TERVERIFIKASI (contractURI). TAPI umur TERBUKTI >24 JAM: pertama teramati job ini 13 Nov ~17:31 WIB dengan 475 sudah minted, masih terbuka 18 Nov 19:31, belum sold out (2107/2222) -> AGE-EXCLUDED, keluar dari watchlist aktif. Tidak pernah dilaporkan sebagai lead -> DIAM sesuai aturan (silent removal). JANGAN baca ulang di run berikut kecuali fase/batch baru terverifikasi. Probe run ini: 17 kandidat view start-time (saleStart/mintStart/startTime/launchTime/dll) SEMUA revert (fungsi tidak ada); contractURI ter-decode (nama Agent Bubble, first mint free lalu 0,00016 BNB, X https://x.com/Agent_Bubblez, website https://agentbubbles.pages.dev, tanpa tanggal launch).")
note("Lumenhold", f"Run 1931 (blok {BLOCK}): freeClaimed 1256/1500 = 83,7% FLAT, totalSupply 1261 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Ledgera", f"Run 1931 (blok {BLOCK}): freeClaimed 2703/5000 = 54,1% FLAT, totalSupply 2710 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note("Vitaliq Scans", f"Run 1931 (blok {BLOCK}): totalSupply revert (fungsi tidak ada, sama seperti 1901), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~12,5 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("HIVE Agents", f"Run 1931 (blok {BLOCK}): totalSupply 1264 FLAT vs 1901, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 1931 (blok {BLOCK}): freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("EIM", f"Run 1931 (blok {BLOCK}): totalMinted 771->774 (+3 vs 1901) -> velocity GAGAL (<20). Bukan kandidat.")
note("PunchCard", f"Run 1931 (blok {BLOCK}): totalMinted 1352 FLAT, freeMinted 1330 FLAT, slot TERBUKA (mintPriceFor 0, mintedCount 0) -> velocity GAGAL. Umur/website UNVERIFIED. Bukan kandidat.")
note("Bubblebruin", f"Run 1931 (blok {BLOCK}): totalSupply 2622->2626 (+4), freeClaimed 2616->2620/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note("THE WALL", f"Run 1931 (blok {BLOCK}): totalSupply 5508->5513 (+5) -> velocity GAGAL. Bukan kandidat.")
note("Mine Card", f"Run 1931 (blok {BLOCK}): totalSupply 1353->1361 (+8, kenaikan ke-2 run ini) -> velocity GAGAL (+8 <20). Bukan kandidat.")

# ---- Agent Bubble age-exclusion (stub kept per workspace precedent:
# Pyrevane-age-excluded, VISION checked-age-excluded, QUBITFOX) ----
ab = snap.get("contracts", {}).get("Agent Bubble")
if isinstance(ab, dict):
    ab["status"] = "age-excluded-2026-11-18"
    ab["ageExcludedEvidence"] = ("Run 1931: pertama teramati job ini 13 Nov ~17:31 WIB "
        "(Boltbook, totalSupply 475 sudah minted) -> mint terbukti terbuka sejak <=13 Nov 17:31; "
        "masih terbuka 18 Nov 19:31 WIB (blok 134314259, totalSupply 2107/2222, freeMinted 1962/2222, "
        "mintOpen 1, belum sold out) -> umur >=5 hari >24 jam. Exact launch timestamp tetap UNVERIFIED "
        "(17 view start-time revert; contractURI tanpa tanggal launch), tapi kondisi penghapusan "
        "terpenuhi: terbuka >=24 jam + belum sold out. Velocity LOLOS run ini (+56, 49,9x) dan free 88,3% "
        "tidak mengubah vonis: umur tidak akan pernah <24 jam lagi. Tidak pernah dilaporkan sebagai lead -> DIAM.")
    print("Agent Bubble -> age-excluded-2026-11-18")
else:
    print("Agent Bubble entry MISSING!")

# ---- AONE track-C update ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 7442
    aone["freeRemaining"] = 2558
    aone["lastReadWib"] = NOW
    aone["note1931"] = ("Run 1931 (blok 134314259): freeMinted 5959 -> 7442 (+1483 dalam ~36,1 mnt, ~41/mnt - pool menguras cepat), "
        "FREE_TOTAL 10000, tersisa 2558. LAUNCH 1794999600 = 2026-11-18 18:00 WIB (date -d terverifikasi). "
        "Kuota user SUDAH 0 (minted-by-user 18:17 WIB, hero #3330/#3331). Tidak ada eksekusi ulang. DIAM.")
    print("AONE updated: freeMinted 7442, freeRemaining 2558")
else:
    print("AONE MISSING from track_c!")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote1931"] = ("Run 1931: launched=0, failed=1, tokenClaimed(user)=0 (blok 134314259) - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

# ---- Agent Vein triage record (sweep hit, already-known project) ----
snap.setdefault("contracts", {}).setdefault("AgentVein-proxy", {})["runNote1931_1118"] = (
    "Run 1931 sweep (route 3) menemukan ulang Agent Vein (site agent-miner-vein.vercel.app, klaim site: free phase 165/1000, "
    "sale 0/40000): token 0x17cc... core() dibaca on-chain = proxy 0x869d... (sama dengan entri ini) -> proyek yang sama, "
    "BUKAN baru. Implementasi 0x534b... tetap belum terverifikasi per cek 16 Nov; re-cek Sourcify run ini TIMEOUT (transport, "
    "bukan bukti verifikasi) -> verdict checked-not-lead TETAP. Umur juga >24 jam (pertama terlihat 16 Nov ~11:01 WIB). "
    "Bukan lead/kandidat, TIDAK di-preview/di-mint. DIAM.")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 19:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, "
    "0 track-C lead; AgentBubble AGE-EXCLUDED (velocity LOLOS +56/49,9x, free 88,3% terverifikasi, website terverifikasi, "
    "TAPI umur terbukti >24 jam: teramati terbuka 13 Nov 17:31 WIB) - DIAM (tidak pernah dilaporkan); "
    "PUNNY 37,0%, deadline 24 jam 20:32 WIB hari ini; STOCK AGENT inferred 70,8% (bukan counter terverifikasi) - tetap EARLY LEAD; "
    "AONE freeMinted 7442/10000, kuota user 0.")
snap["runNote1931_1118"] = (
    f"Run 1931 (blok {BLOCK}, interval ~36,1 mnt vs 1901): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "Scan leg FAST-FAIL: Ankr pre-flight HTTP 401 (14,7 dtk); watermark TIDAK maju. "
    "Reread Quicknode 291 calls, 5 chunk error (calls 260-284, bsccat views saja - TimeoutError; nilai lama dipertahankan); elapsed run 940,8 dtk. "
    "Perbaikan env run ini: percobaan pertama skrip 1931 mati ImportError (eth_hash tanpa backend keccak); "
    "pip install --user eth-hash[pycryptodome] -> keccak OK (18160ddd), rerun jalan. "
    "Velocity: 1 LOLOS - AgentBubble +56 (1,551/mnt vs prev 0,0311 = 49,9x, >=20 token); lainnya maks +8 Mine Card, +5 THE WALL/STOCK/PUNNY, +4 Bubblebruin, +3 EIM/ALIEN, +2 DGF - semua <20 token. "
    "AgentBubble: velocity LOLOS + free 1962/2222 = 88,3% TERVERIFIKASI + website TERVERIFIKASI (contractURI) TAPI umur TERBUKTI >24 jam "
    "(pertama teramati 13 Nov ~17:31 WIB, 475 sudah minted; masih terbuka 18 Nov 19:31, 2107/2222, belum sold out) -> AGE-EXCLUDED, "
    "keluar dari watchlist aktif (stub dipertahankan, status age-excluded-2026-11-18); tidak pernah dilaporkan sebagai lead -> DIAM. "
    "Probe 17 view start-time AgentBubble SEMUA revert (fungsi tidak ada); contractURI ter-decode (first mint free lalu 0,00016 BNB, X Agent_Bubblez, website agentbubbles.pages.dev, tanpa tanggal launch). "
    "PUNNY 370/999 = 37,0% (<50%), umur terverifikasi ~23 jam (deadline 24 jam 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD. "
    "STOCK AGENT inferred 787/1111 = 70,8% (INFERENSI totalSupply, bukan free counter terverifikasi; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold 1256/1500 = 83,7% FLAT. "
    "Ledgera 54,1% FLAT, Bubblebruin 33,7%, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user). "
    "Vitaliq Scans: genesisStart 07:00 WIB (umur ~12,5 jam TERVERIFIKASI <24 jam), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "AONE track-C: freeMinted 5959 -> 7442 (+1483/~36 mnt, ~41/mnt), tersisa 2558, LAUNCH 18:00 WIB; kuota user 0 (minted-by-user 18:17 WIB). DIAM. "
    "Boltbook EN+ZH segar (44.903/43.207 byte, HTTP 200): 6 alamat, 0 lead baru - Burnagent 0x262b sold out 200/200 (cek 7 Nov); "
    "0xd8ec/0xe31d adalah false positive (potongan tx hash dari post AGC, bukan kontrak); lainnya dikenal. "
    "Sourcify feed: 20 alamat, top verifiedAt 2026-11-18T12:51:00Z; 7 ter-shape-check, 0 S1/S2; 13 shape-check GAGAL TimeoutError (egress degradasi, belum terperiksa - bukan lolos). "
    "Sweep EN+ZH + share-sale (browser.search): 0 proyek segar baru - hanya proyek lama yang dikenal (Oathbots age-excluded, Agentic Gangster 9 Nov, "
    "LeadLoop/NEXUS/hackou Okt, JINCHAN tutup 10 Nov, BN Agent Trials season berakhir 8 Nov, QILIN/SAFU/传火人/PROXY 1 Nov, UFO tutup 12 Nov, "
    "NEBULA/VISION/JINMA/YAMA/NOVRA/PACTA sudah di track_c). "
    "Agent Vein (sweep): token 0x17cc core() = proxy 0x869d yang sudah checked-not-lead 16 Nov (implementasi unverified); re-cek Sourcify timeout; umur >24 jam -> bukan lead. DIAM. "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "DIAM (tidak ada laporan ke chat utama)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
