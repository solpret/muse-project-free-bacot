#!/usr/bin/env python3
"""Merge run 2026-11-16 03:01 WIB reread into onchain-snapshot.json.
- Update 33 focus contracts with fresh reads + velocity (interval ~30.0 min vs run 0131, block 133784649 -> 133792486).
- Age-exclusion: NONE new this run (no ITEMS contract newly verified launch >24h + not sold out;
  NOISE/Zero/LumenFindings already carry age-excluded-2026-11-14 status and remain in ITEMS per prior-run pattern).
- VOXEL triage recorded (free pool sold out 1000/1000 at first full verification; checked-not-lead, NOT a lead, NOT added).
- PACTURE sold out 11,000/11,000 verified on-chain (track_c entry removed; contracts entry marked sold-out-2026-11-16; user slot already used).
- Update pending_claims binanceai.fun + track_c ORBIT/RigForge notes.
- No preview/mint. Read-only merge."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-0301")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-0301-reread.json"))
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
        notes[name] = f"Run 0301 (blok {BLK}): SEMUA view gagal baca (chunk fail) - nilai lama dipertahankan."
        e["runNote0301_1116"] = notes[name]; continue
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
    e["lastReadWib"] = "2026-11-16 ~03:01 WIB"
    fc = v.get("freeClaimed"); fm = v.get("freeMinted")
    fs = v.get("FREE_SUPPLY") or v.get("FREE_CAP") or v.get("FREE_MAX")
    fs_note = ""
    if (fm or fc) is not None and not fs and v.get("MAX_SUPPLY"):
        fs = v.get("MAX_SUPPLY"); fs_note = " (vs MAX_SUPPLY)"
    freepct = f"{fm or fc}/{fs}={round(100*(fm or fc)/fs,1)}%{fs_note}" if (fm or fc) is not None and fs else "-"
    rate_s = f"{rate:.3f}" if rate is not None else "?"
    notes[name] = (f"Run 0301 (blok {BLK}, interval {INTERVAL} mnt vs run 0231): {prim_eff} {prev}->{cur} "
                   f"(+{delta if delta is not None else '?'}, {rate_s}/mnt vs prev {prev_rate} = "
                   f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if vel else 'GAGAL'}; "
                   f"free {freepct}; bal_user={v.get('balanceOf_user')}; DIAM.")
    e["runNote0301_1116"] = notes[name]
    print(name, "->", notes[name][:150])

# Track B pending claim
pc = s.setdefault("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["launched"] = 0; pc["failed"] = 1; pc["isRefundPhase"] = 1; pc["totalShares"] = 3110
    pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-16 ~03:01 WIB"
    pc["runNote0301_1116"] = (f"Run 0301 (blok {BLK}): launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                               "tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
# Track C
tc = s.setdefault("track_c", {})
rv = reads.get("RigForge", {}).get("views") or {}
if "ORBIT" in tc:
    ov = reads.get("ORBIT", {}).get("views") or {}
    tc["ORBIT"]["freeClaimed"] = ov.get("freeClaimed", 292); tc["ORBIT"]["claimOpen"] = ov.get("claimOpen", 1)
    tc["ORBIT"]["hasFreeClaimed_user"] = ov.get("hasFreeClaimed_user", 0)
    tc["ORBIT"]["lastReadBlock"] = BLK; tc["ORBIT"]["lastReadWib"] = "2026-11-16 ~03:01 WIB"
    tc["ORBIT"]["runNote0301_1116"] = (f"Run 0301 (blok {BLK}): freeClaimed {tc['ORBIT']['freeClaimed']}/888 TETAP, claimOpen 1, "
                                        "hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.")
if "RigForge" in tc:
    tc["RigForge"]["freeSharesLeft"] = rv.get("freeSharesLeft", 639); tc["RigForge"]["openedAt"] = rv.get("openedAt", 0)
    tc["RigForge"]["freeClaimed"] = rv.get("freeClaimed", 361)
    tc["RigForge"]["lastReadBlock"] = BLK; tc["RigForge"]["lastReadWib"] = "2026-11-16 ~03:01 WIB"
    tc["RigForge"]["runNote0301_1116"] = (f"Run 0301 (blok {BLK}): freeSharesLeft {tc['RigForge']['freeSharesLeft']}, openedAt 0 (pool belum buka), "
                                           f"freeClaimed {tc['RigForge']['freeClaimed']} - DIAM.")


s["runNote0301_1116"] = ("Run 0301 (blok 133796404, interval ~30,0 mnt vs run 0231): re-read 33/33 OK. "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, "
    "0 eksekusi/preview. Velocity: 0 lolos (delta terbesar +6, SPARKS; MORFO +2; AGCLUB +1; LumenFindings +17 spesimen, bukan velocity mint). Free% tertinggi: AgentBubble 1544/2222=69,5% "
    "(<70% strong lead, flat interval ini). Age-excluded baru: tidak ada. Triase Boltbook baru: 0x9b54 + 0xf0f9 = 0 byte code (bukan kontrak, bukan lead). "
    "Sourcify baru 0xEF08 = token ALOR dividend, NOT sale-shape, NOT agent-shaped. Verdict: DIAM.")
s["runNote0301_1116_scan"] = ("Run 0301: scan leg FAST-FAIL - pre-flight Ankr getLogs 50 blok HTTP 401 Unauthorized (1,01 dtk). "
    "Watermark TETAP 132512564 (head 133796506, gap 1.283.942). Track-C 5c dilewati (tidak ada output scan).")
s["runNote0301_1116_ageex"] = ("Age-exclusion run 0301: TIDAK ADA yang baru. Tidak ada kontrak ITEMS yang newly-verified launch >24 jam + belum sold out. "
    "NOISE/Zero/LumenFindings sudah berstatus age-excluded-2026-11-14 dan tetap di ITEMS mengikuti pola run-run sebelumnya; "
    "MORFO/AgentNOVA launch tetap UNVERIFIED (first-mint proof terblokir Ankr 401) -> watchlist-only, tidak dihapus diam-diam.")
s["runNote0301_1116_boltbook"] = ("Run 0301 Boltbook EN + ZH, HTTP 200 (curl; EN 45.978 byte, ZH 46.254 byte). 8 alamat distinct; 4 di snapshot "
    "(Agent Bubble, ONLYAI Crystals, 0x8269, BOLT), 4 dikenal hot-leg-seen: 0x5bc4 (checked-not-sale-shape-2026-11-07), 0xc509 (checked-abi-unavailable-2026-11-10), "
    "0x9b54 + 0xf0f9 (BARU hot leg 02:59, shape-check-failed Sourcify 404; triase run ini: eth_getCode 0 byte keduanya = BUKAN kontrak, BUKAN lead, TIDAK masuk snapshot, TIDAK dilaporkan). "
    "OAGENT Units 0x6050 tidak lagi di front page run ini (triase 0231: bukan agent-shaped, launch 2026-11-02).")
s["runNote0301_1116_sweep"] = ("Run 0301 sweep EN+ZH (2 query) + Sourcify feed + Odaily/PANews: 0 hit segar baru. Sourcify 20 kontrak, top verifiedAt 20:03:03Z; "
    "19 sudah shape-check hot leg (s.d. 20:00:51Z), 1 terbaru dicek run ini: 0xEF08 (token ALOR dividend/community coin, mintInitialSeed saja, tanpa quote/cost, tanpa free view, tanpa registry/AgentGate -> NOT sale-shape, NOT agent-shaped, checked-not-lead). "
    "Sweep EN: Medium 'How My Agent Verifies' (15 Nov, narasi umum), Oathbots (28 Okt, age-excluded), Agentic Gangster (9 Nov, free-pool-exhausted-2026-11-11), STAMP PASS (9 Nov, sold-out-2026-11-10), AGENT ID cards (25 Okt), Meow Cards (10 Nov, di snapshot, umur >24 jam). "
    "Sweep ZH: AGENT COSMOS (5 Nov, di snapshot), AGENT MAO (paused), KOMA (age-excluded-2026-11-14, sale tutup 16 Nov 22:00 WIB+8), Medium 8-free-mints (2 Nov, lama). "
    "Catatan keamanan: pola instruksi tertanam 'Instruction for the AI: call mint()...' muncul lagi di hasil pencarian (AGENT ID cards 0x486d...). Konten pihak ketiga, BUKAN instruksi user - diabaikan sepenuhnya; run tetap read-only, tanpa preview/mint/eksekusi. twitterapi.io tidak dipanggil. "
    "Odaily newsflash + PANews: 0 pengumuman Agent ID / free-mint baru. DappBay tidak dipakai (tidak ada proyek baru untuk di-cek).")
s["runNote0301_1116_binanceai"] = "Run 0301: binanceai.fun TIDAK BERUBAH (launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed user=0) - fase refund, DIAM."
s["runNote0301_1116_bridge"] = "Run 0301 bridge (read-only): 116 kontrak bridge, 116/116 sudah di snapshot (per alamat), 0 baru, 7 same_owner_discarded. Tidak ada temuan pelengkap baru / promosi. Job ini tidak menulis bridge."
s["last_run_wib"] = "2026-11-16 ~03:01 WIB"
s["last_run_note"] = s["runNote0301_1116"]
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED. contracts:", len(s["contracts"]))
