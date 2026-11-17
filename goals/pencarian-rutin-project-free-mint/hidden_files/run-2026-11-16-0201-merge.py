#!/usr/bin/env python3
"""Merge run 2026-11-16 02:01 WIB reread into onchain-snapshot.json.
- Update 33 focus contracts with fresh reads + velocity (interval ~30.0 min vs run 0131, block 133784649 -> 133788846).
- Age-exclusion: NONE new this run (no ITEMS contract newly verified launch >24h + not sold out;
  NOISE/Zero/LumenFindings already carry age-excluded-2026-11-14 status and remain in ITEMS per prior-run pattern).
- VOXEL triage recorded (free pool sold out 1000/1000 at first full verification; checked-not-lead, NOT a lead, NOT added).
- PACTURE sold out 11,000/11,000 verified on-chain (track_c entry removed; contracts entry marked sold-out-2026-11-16; user slot already used).
- Update pending_claims binanceai.fun + track_c ORBIT/RigForge notes.
- No preview/mint. Read-only merge."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-0201")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-0201-reread.json"))
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
notes = {}
for name, d in reads.items():
    if name in ("BinanceAI-mint", "RigForge"):
        continue  # handled below (pending_claims / track_c)
    e = s["contracts"].get(name)
    if e is None:
        print("WARN no snapshot entry:", name); continue
    v = d.get("views")
    if v is None:
        notes[name] = f"Run 0201 (blok {BLK}): SEMUA view gagal baca (chunk fail) - nilai lama dipertahankan."
        e["runNote0201_1116"] = notes[name]; continue
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
    e["lastReadWib"] = "2026-11-16 ~02:01 WIB"
    fc = v.get("freeClaimed"); fm = v.get("freeMinted")
    fs = v.get("FREE_SUPPLY") or v.get("FREE_CAP") or v.get("FREE_MAX")
    fs_note = ""
    if (fm or fc) is not None and not fs and v.get("MAX_SUPPLY"):
        fs = v.get("MAX_SUPPLY"); fs_note = " (vs MAX_SUPPLY)"
    freepct = f"{fm or fc}/{fs}={round(100*(fm or fc)/fs,1)}%{fs_note}" if (fm or fc) is not None and fs else "-"
    rate_s = f"{rate:.3f}" if rate is not None else "?"
    notes[name] = (f"Run 0201 (blok {BLK}, interval {INTERVAL} mnt vs run 0131): {prim_eff} {prev}->{cur} "
                   f"(+{delta if delta is not None else '?'}, {rate_s}/mnt vs prev {prev_rate} = "
                   f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if vel else 'GAGAL'}; "
                   f"free {freepct}; bal_user={v.get('balanceOf_user')}; DIAM.")
    e["runNote0201_1116"] = notes[name]
    print(name, "->", notes[name][:150])

# Track B pending claim
pc = s.setdefault("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["launched"] = 0; pc["failed"] = 1; pc["isRefundPhase"] = 1; pc["totalShares"] = 3110
    pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-16 ~02:01 WIB"
    pc["runNote0201_1116"] = (f"Run 0201 (blok {BLK}): launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                               "tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
# Track C
tc = s.setdefault("track_c", {})
rv = reads.get("RigForge", {}).get("views") or {}
if "ORBIT" in tc:
    ov = reads.get("ORBIT", {}).get("views") or {}
    tc["ORBIT"]["freeClaimed"] = ov.get("freeClaimed", 292); tc["ORBIT"]["claimOpen"] = ov.get("claimOpen", 1)
    tc["ORBIT"]["hasFreeClaimed_user"] = ov.get("hasFreeClaimed_user", 0)
    tc["ORBIT"]["lastReadBlock"] = BLK; tc["ORBIT"]["lastReadWib"] = "2026-11-16 ~02:01 WIB"
    tc["ORBIT"]["runNote0201_1116"] = (f"Run 0201 (blok {BLK}): freeClaimed {tc['ORBIT']['freeClaimed']}/888 TETAP, claimOpen 1, "
                                        "hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.")
if "RigForge" in tc:
    tc["RigForge"]["freeSharesLeft"] = rv.get("freeSharesLeft", 639); tc["RigForge"]["openedAt"] = rv.get("openedAt", 0)
    tc["RigForge"]["freeClaimed"] = rv.get("freeClaimed", 361)
    tc["RigForge"]["lastReadBlock"] = BLK; tc["RigForge"]["lastReadWib"] = "2026-11-16 ~02:01 WIB"
    tc["RigForge"]["runNote0201_1116"] = (f"Run 0201 (blok {BLK}): freeSharesLeft {tc['RigForge']['freeSharesLeft']}, openedAt 0 (pool belum buka), "
                                           f"freeClaimed {tc['RigForge']['freeClaimed']} - DIAM.")


# PACTURE sold out (track_c) - verified on-chain this run via triage (sharesMinted 11000, soldOut 1, freeClaimed(user)=1)
tc = s.setdefault("track_c", {})
if "Pacture" in tc:
    s["runNote0201_1116_pacture"] = ("PACTURE 0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9 SOLD OUT terverifikasi run ini: sharesMinted 11.000/11.000, soldOut=1 "
        "(blok 133789288, eth_call dataseed); freeMinted 7.700; freeClaimed(user)=1, mintedBy(user)=1 (slot user SUDAH TERPAKAI sejak 2026-11-05, bukan lead). "
        "Token yang tadinya terkunci sampai sell-out kini unlock (transfer terbuka); pool/DEX belum ada per post Boltbook ~02:00 WIB. "
        "Dilaporkan SEKALI run ini + track_c entry DIHAPUS; contracts entry ditandai sold-out-2026-11-16.")
    if "Pacture" in s.get("contracts", {}):
        s["contracts"]["Pacture"]["status"] = "sold-out-2026-11-16"
        s["contracts"]["Pacture"]["runNote0201_1116"] = s["runNote0201_1116_pacture"]
        s["contracts"]["Pacture"]["lastReadBlock"] = 133789288
        s["contracts"]["Pacture"]["lastReadWib"] = "2026-11-16 ~02:01 WIB"
    del tc["Pacture"]

s["runNote0201_1116"] = ("Run 0201 (blok 133788846, interval ~30,0 mnt vs run 0131): re-read 33/33 OK. "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, "
    "0 eksekusi/preview. Velocity: 0 lolos (delta terbesar +14, LumenFindings specimens). Free% tertinggi: AgentBubble 1544/2222=69,5% "
    "(<70% strong lead). Age-excluded baru: tidak ada. VOXEL triase run ini: free pool HABIS 1000/1000 saat pertama diverifikasi penuh "
    "(checked-not-lead, tidak dilaporkan). PACTURE sold out 11.000/11.000 terverifikasi on-chain (laporan sekali + track_c dihapus). Verdict: LAPOR SEKALI (Pacture sold-out).")
s["runNote0201_1116_scan"] = ("Run 0201: scan leg FAST-FAIL - pre-flight Ankr getLogs 50 blok HTTP 401 Unauthorized (1,16 dtk). "
    "Watermark TETAP 132512564 (head 133788822, gap 1.276.258). Track-C 5c dilewati (tidak ada output scan).")
s["runNote0201_1116_ageex"] = ("Age-exclusion run 0201: TIDAK ADA yang baru. Tidak ada kontrak ITEMS yang newly-verified launch >24 jam + belum sold out. "
    "NOISE/Zero/LumenFindings sudah berstatus age-excluded-2026-11-14 dan tetap di ITEMS mengikuti pola run-run sebelumnya; "
    "MORFO/AgentNOVA launch tetap UNVERIFIED (first-mint proof terblokir Ankr 401) -> watchlist-only, tidak dihapus diam-diam.")
s["runNote0201_1116_boltbook"] = ("Run 0201 Boltbook EN + ZH, HTTP 200 (browser.open; ZH 45.246 byte via curl, EN curl 302-artifact). "
    "Baru vs run 0131: Compasyn 0xCd1b... (promotion-discarded-same-owner-2026-11-09, bukan lead); RONIN 0x9404... (Roninagent, watchlist-only-same-owner-discarded-2026-11-03, bukan lead); "
    "Voxel World Pixel 0x097e... (BARU, triase penuh run ini - lihat runNote0201_1116_voxel); Legacy Code Bees 0x44a6... (checked-not-agent-shaped-2026-11-16, recheck 212/7.777); "
    "Pathwyrm 0xf100... (watchlist-only-age-unverified-2026-11-12, recheck 390/2.131 = 18,3%); DRAGON 0xad0d... (age-excluded-2026-11-14, recheck 847/1.888, free 843/888, 45 left); "
    "PACTURE 0x95AF... (sold out 11.000/11.000 - lihat runNote0201_1116_pacture); NOISE 0xba53... (age-excluded, recheck 1.339/3.333); Agent Nakamigos 0x2d70... (20.000/20.000, excluded/owned); "
    "LumenFindings FIND exp23 (age-excluded, 146/300 live leg); SPEC exp4 (563/617, gap 54 beku).")
s["runNote0201_1116_voxel"] = ("VOXEL World Pixel 0x097E34c0A1657537aA0D94d171D39AB3954Fee57 triase run ini (Boltbook front page EN+ZH + Sourcify feed verifiedAt 2026-11-15T18:55:00Z; "
    "post cross-check ~02:11 WIB: freeMinted 695, FREE_SUPPLY 1000, mintOpen, FREE_MAX_PER_WALLET 4, freeMint(1) value 0 sim clean, hasAgentId true): "
    "Sourcify exact_match; getCode 39.174 byte, registry_bytes TRUE; verifikasi sendiri via eth_call dataseed: freeMinted 954/1000 = 95,4%, totalMinted 954, mintOpen 1, "
    "hasAgentId(user)=1, balanceOf(user)=0; owner 0x2f2146666221191f946d12acc925546902208f2a (bukan discards); user-slot views (freeClaimed/mintedBy/freeUsed/dll.) semua revert - slot user dinilai dari balanceOf 0 + FREE_MAX_PER_WALLET 4. "
    "NAMUN re-read ~02:17 WIB: freeMinted 1000/1000 = 100%, totalMinted 1000, freeMint(1) sim REVERT 'Free Mint sold out' -> free pool HABIS saat pertama diverifikasi penuh "
    "(46 kursi terakhir terambil antara probe 954 dan sim ~02:17 WIB, pace ~9/mnt). Vonis: agent-shaped + free% >70% TAPI pool habis -> BUKAN lead/kandidat/strong lead, TIDAK dilaporkan "
    "(tidak pernah dilaporkan sebagai lead), TIDAK masuk snapshot sebagai lead; dicatat checked-not-lead (free-exhausted, preseden NURU run 0131). "
    "Umur peluncuran tetap UNVERIFIED (tanpa mintStart; first-mint proof terblokir: Ankr 401 + eth_getLogs public RPC limit-exceeded bahkan jendela 10 blok + BscScan free tidak mencakup BSC; "
    "Sourcify verifiedAt 01:55 WIB + post Boltbook hari ini hanya batas atas, bukan verifikasi launch). Website/X tidak dikejar lanjut karena pool sudah habis (gate moot).")
s["runNote0201_1116_sweep"] = ("Run 0201 sweep EN+ZH (2 query) + Sourcify feed + Odaily/PANews: 0 hit segar baru. Sourcify 20 kontrak, top verifiedAt 19:06:48Z; "
    "19 sudah shape-check hot leg (s.d. 19:00:36Z), 1 terbaru dicek run ini: 0x2664bbc1 (plain ERC-20, totalSupply 100.000.000, decimals 18, code 7.272 byte, registry_bytes FALSE, tanpa mint/free view -> NOT sale-shape, NOT agent-shaped, checked-not-lead). "
    "Sweep EN: Oathbots (28 Okt, known), Agentic Gangster (9 Nov, free-pool-exhausted), STAMP PASS (9 Nov, sold-out-free-pool-exhausted-2026-11-10 di snapshot), AGENT ID cards (25 Okt); "
    "Sweep ZH: KOMA (age-excluded-2026-11-14, sale tutup 16 Nov 22:00 WIB+8), BN Agent Trials (season berakhir 8 Nov), Xuanwu Seed (24 Okt, age-excluded), Medium 8-free-mints (2 Nov, lama). "
    "Odaily newsflash + PANews: 0 pengumuman Agent ID / free-mint. DappBay tidak dipakai (tidak ada proyek baru untuk di-cek).")
s["runNote0201_1116_binanceai"] = "Run 0201: binanceai.fun TIDAK BERUBAH (launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed user=0) - fase refund, DIAM."
s["runNote0201_1116_bridge"] = "Run 0201 bridge (read-only): 116 kontrak bridge, 116/116 sudah di snapshot (per alamat), 0 baru, 7 same_owner_discarded. Tidak ada temuan pelengkap baru / promosi. Job ini tidak menulis bridge."
s["last_run_wib"] = "2026-11-16 ~02:01 WIB"
s["last_run_note"] = s["runNote0201_1116"]
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED. contracts:", len(s["contracts"]))
