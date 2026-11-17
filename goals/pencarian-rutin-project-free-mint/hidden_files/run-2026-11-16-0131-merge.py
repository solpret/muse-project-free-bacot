#!/usr/bin/env python3
"""Merge run 2026-11-16 01:31 WIB reread into onchain-snapshot.json.
- Update 33 focus contracts with fresh reads + velocity (interval ~30.0 min vs run 0101, block 133780435 -> 133784649).
- Age-exclusion: NONE new this run (no ITEMS contract newly verified launch >24h + not sold out;
  NOISE/Zero/LumenFindings already carry age-excluded-2026-11-14 status and remain in ITEMS per prior-run pattern).
- NURU triage recorded (free pool sold out 222/222 at first verification; checked-not-lead, NOT a lead, NOT added).
- Update pending_claims binanceai.fun + track_c ORBIT/RigForge notes.
- No preview/mint. Read-only merge."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-0131")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-0131-reread.json"))
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
        notes[name] = f"Run 0131 (blok {BLK}): SEMUA view gagal baca (chunk fail) - nilai lama dipertahankan."
        e["runNote0131_1116"] = notes[name]; continue
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
    e["lastReadWib"] = "2026-11-16 ~01:31 WIB"
    fc = v.get("freeClaimed"); fm = v.get("freeMinted")
    fs = v.get("FREE_SUPPLY") or v.get("FREE_CAP") or v.get("FREE_MAX")
    fs_note = ""
    if (fm or fc) is not None and not fs and v.get("MAX_SUPPLY"):
        fs = v.get("MAX_SUPPLY"); fs_note = " (vs MAX_SUPPLY)"
    freepct = f"{fm or fc}/{fs}={round(100*(fm or fc)/fs,1)}%{fs_note}" if (fm or fc) is not None and fs else "-"
    rate_s = f"{rate:.3f}" if rate is not None else "?"
    notes[name] = (f"Run 0131 (blok {BLK}, interval {INTERVAL} mnt vs run 0101): {prim_eff} {prev}->{cur} "
                   f"(+{delta if delta is not None else '?'}, {rate_s}/mnt vs prev {prev_rate} = "
                   f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if vel else 'GAGAL'}; "
                   f"free {freepct}; bal_user={v.get('balanceOf_user')}; DIAM.")
    e["runNote0131_1116"] = notes[name]
    print(name, "->", notes[name][:150])

# Track B pending claim
pc = s.setdefault("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["launched"] = 0; pc["failed"] = 1; pc["isRefundPhase"] = 1; pc["totalShares"] = 3110
    pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-16 ~01:31 WIB"
    pc["runNote0131_1116"] = (f"Run 0131 (blok {BLK}): launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                               "tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
# Track C
tc = s.setdefault("track_c", {})
rv = reads.get("RigForge", {}).get("views") or {}
if "ORBIT" in tc:
    ov = reads.get("ORBIT", {}).get("views") or {}
    tc["ORBIT"]["freeClaimed"] = ov.get("freeClaimed", 292); tc["ORBIT"]["claimOpen"] = ov.get("claimOpen", 1)
    tc["ORBIT"]["hasFreeClaimed_user"] = ov.get("hasFreeClaimed_user", 0)
    tc["ORBIT"]["lastReadBlock"] = BLK; tc["ORBIT"]["lastReadWib"] = "2026-11-16 ~01:31 WIB"
    tc["ORBIT"]["runNote0131_1116"] = (f"Run 0131 (blok {BLK}): freeClaimed {tc['ORBIT']['freeClaimed']}/888 TETAP, claimOpen 1, "
                                        "hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.")
if "RigForge" in tc:
    tc["RigForge"]["freeSharesLeft"] = rv.get("freeSharesLeft", 639); tc["RigForge"]["openedAt"] = rv.get("openedAt", 0)
    tc["RigForge"]["freeClaimed"] = rv.get("freeClaimed", 361)
    tc["RigForge"]["lastReadBlock"] = BLK; tc["RigForge"]["lastReadWib"] = "2026-11-16 ~01:31 WIB"
    tc["RigForge"]["runNote0131_1116"] = (f"Run 0131 (blok {BLK}): freeSharesLeft {tc['RigForge']['freeSharesLeft']}, openedAt 0 (pool belum buka), "
                                           f"freeClaimed {tc['RigForge']['freeClaimed']} - DIAM.")

s["runNote0131_1116"] = ("Run 0131 (blok 133784649, interval ~30,0 mnt vs run 0101): re-read 33/33 OK. "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, "
    "0 eksekusi/preview. Velocity: 0 lolos (delta terbesar +6, REOPIR). Free% tertinggi: AgentBubble 1543/2222=69,5% "
    "(<70% strong lead). Age-excluded baru: tidak ada. NURU triase run ini: free pool HABIS 222/222 saat pertama diverifikasi "
    "(checked-not-lead, tidak dilaporkan). Verdict: DIAM.")
s["runNote0131_1116_scan"] = ("Run 0131: scan leg FAST-FAIL - pre-flight Ankr getLogs 50 blok HTTP 401 Unauthorized (1,31 dtk). "
    "Watermark TETAP 132512564 (head 133784455, gap 1.271.891). Track-C 5c dilewati (tidak ada output scan).")
s["runNote0131_1116_ageex"] = ("Age-exclusion run 0131: TIDAK ADA yang baru. Tidak ada kontrak ITEMS yang newly-verified launch >24 jam + belum sold out. "
    "NOISE/Zero/LumenFindings sudah berstatus age-excluded-2026-11-14 dan tetap di ITEMS mengikuti pola run-run sebelumnya; "
    "MORFO/AgentNOVA launch tetap UNVERIFIED (first-mint proof terblokir Ankr 401) -> watchlist-only, tidak dihapus diam-diam.")
s["runNote0131_1116_boltbook"] = ("Run 0131 Boltbook EN (46.111 byte) + ZH (46.311 byte), HTTP 200. 10 EN / 10 ZH alamat distinct; 7 baru vs run 0101: "
    "DRAGON 0xad0d... (age-excluded-2026-11-14, recheck 845/1888, freeClaimed 841/888, 47 left); LumenFindings 0x4158... (age-excluded, recheck FIND exp22 sealed 207); "
    "Lion's Share 0x6ac0... (age-excluded-2026-11-08, recheck #194 1.134/1.450 flat ~1 jam); VORTIQ 0x83f2... (checked-not-agent-shaped, hot leg 00:09 WIB, no Agent ID gate, recheck post 01:28 UTC); "
    "BAGENT 0x9ca1... (excluded-paid-2026-11-09, writeup lama 2026-11-11); Pi pair 0x0d2f... (checked-not-sale-shape 2026-11-07, post koreksi angka, bukan mint); "
    "Pi token 0xdaad... (BARU dicek run ini: plain ERC-20 totalSupply 800B, decimals 18, registry_bytes FALSE -> checked-not-lead, bukan mint); "
    "NURU 0x9d7f... (BARU, triase penuh run ini - lihat runNote0131_1116_nuru).")
s["runNote0131_1116_nuru"] = ("NURU 0x9d7ffe074fb139cad8e69190fd2d1da19540cff7 triase run ini (post Boltbook cskh.ai ~01:28 WIB, klaim 214/222 free claimed, 8 left, 48h window, "
    "Agent ID gated, Sourcify-verified, freeMint() value 0): Sourcify verified; ABI AGENT_ID_REGISTRY + freeMint no-arg + FREE_SUPPLY 222 + MAX_SUPPLY 1000 + MINT_DURATION 172800 + "
    "mintStart 1794763078 = 2026-11-16 00:17 WIB + mintEnd 2026-11-18 00:17 WIB + PAID_PRICE 0,006 BNB; code 7.591 byte, registry_bytes TRUE; "
    "verifikasi sendiri ~01:37 WIB via eth_call dataseed: freeMinted 222/222 = 100%, freeRemaining 0, totalMinted 222, paidMinted 0, hasClaimedFree(user)=0. "
    "Vonis: agent-shaped + launch TERVERIFIKASI <24 jam (00:17 WIB, umur ~1 jam 20 mnt saat probe) TAPI free pool HABIS saat pertama diverifikasi "
    "(8 kursi terakhir terambil antara post ~01:28 WIB dan probe ~01:37 WIB) -> BUKAN lead/kandidat, TIDAK dilaporkan (tidak pernah dilaporkan sebagai lead), "
    "TIDAK masuk snapshot sebagai lead; dicatat checked-not-lead (free-exhausted). Website/X tidak dikejar lanjut karena pool sudah habis (gate moot).")
s["runNote0131_1116_sweep"] = ("Run 0131 sweep EN+ZH (3 query) + Sourcify feed + Odaily/PANews: 0 hit segar baru. Sourcify 20 kontrak, top verifiedAt 18:34:15Z; "
    "15 sudah shape-check hot leg (S1/S2 false, agent false), 4 terbaru dicek run ini: 0x1aAE920F (merchant/collect USDT, S1/S2 false), 0xc66C25e7 (airdrop/liquidity token, S1/S2 false), "
    "0x3ab9C948 (paid NFT mint, mint+costOf+price, tanpa free view, tanpa agent, S1/S2 false), 0xCF974333 (vesting, S1/S2 false) - semua NOT sale-shape, NOT agent-shaped. "
    "Sweep: Oathbots, Agentic Gangster (free-pool-exhausted), LeadLoop, NEXUS CORE, hackou, AGENT ID cards (semua 25 Okt / sudah tercatat); KOMA (age-excluded-2026-11-14, sale tutup 16 Nov 22:00 WIB+8); "
    "First-Dollar Grove (age-excluded); Xuanwu Seed (mint buka 25 Okt, umur >24 jam, tidak di snapshot, bukan lead); Rulz Share (age-excluded run 0031); WNO (gate-failed watchlist-only); "
    "NOVRA (age-excluded-2026-11-12, free pool 0); UFO/NEBULA (UFO tutup 12 Nov); AgentVOLT (snapshot watchlist-only-unverified-2026-11-07, artikel 9 hari lalu, bukan segar). "
    "Odaily newsflash + PANews: 0 pengumuman Agent ID / free-mint. DappBay tidak dipakai (tidak ada proyek baru untuk di-cek).")
s["runNote0131_1116_binanceai"] = "Run 0131: binanceai.fun TIDAK BERUBAH (launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed user=0) - fase refund, DIAM."
s["runNote0131_1116_bridge"] = "Run 0131 bridge (read-only): 116 kontrak bridge, 116/116 sudah di snapshot (per alamat), 0 baru, 7 same_owner_discarded. Tidak ada temuan pelengkap baru / promosi. Job ini tidak menulis bridge."
s["last_run_wib"] = "2026-11-16 ~01:31 WIB"
s["last_run_note"] = s["runNote0131_1116"]
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED. contracts:", len(s["contracts"]))
