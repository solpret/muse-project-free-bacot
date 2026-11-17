#!/usr/bin/env python3
"""Merge run 2026-11-16 01:01 WIB reread into onchain-snapshot.json.
- Update 35 focus contracts with fresh reads + velocity (interval ~30.5 min vs run 0031, block 133776368 -> 133780435).
- Age-exclusion: B77D (launch verified 14 Nov 08:05-08:34 WIB, age ~40.5h, early lead reported once 14 Nov 0831 -> report once) +
  AbsurdAgentNFT (mintStart 14 Nov 17:00 WIB, first mints bounded 15:31-23:01 14 Nov, age ~32h, never reported as lead -> silent removal).
  Delete B77D, AbsurdAgentNFT, AbsurdAgentNFT-72C1 from contracts.
- Update pending_claims binanceai.fun + track_c ORBIT/RigForge notes.
- No preview/mint. Read-only merge."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-0101-reread.json"))
reads = r["reads"]; BLK = r["block"]; INTERVAL = 30.5
PRIMARY = {"AGCLUB":"totalMinted","MORFO":"totalMinted","NOISE":"totalMinted","RaceAgents":"totalSupply",
 "AbsurdAgentNFT":"totalMinted","B77D":"totalMinted","Zero":"totalMinted","HIVE":"totalSupply",
 "AgentNOVA":"totalSupply","SPARKS":"totalSupply","AgentBubble":"totalSupply","WANGCAI":"totalSupply",
 "YUANBAO":"totalSupply","PX24":"totalSupply","Zephyra":"totalMinted","LumenFindings":"totalSpecimens",
 "Pengu":"totalMinted","CPASS":"totalMinted","ORBIT":"totalSupply","TrashBandits":"totalMinted",
 "SKRR":"totalSupply","REOPIR":"totalSupply","FrieAgent-B751":"totalSupply","FrieAgent-c64d":"totalSupply",
 "Ledgera":"totalSupply","MAMI":"totalSupply","INKI":"totalSupply","HashcatDepot":"totalSupply",
 "OTV":"totalSupply","RAVE":"totalMinted","HANAMI":"totalSupply","CosmicSentinel":"totalSupply",
 "Matrix Agents":"totalSupply"}
# view keys to copy verbatim when read succeeded
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
        notes[name] = f"Run 0101 (blok {BLK}): SEMUA view gagal baca (chunk fail) - nilai lama dipertahankan."
        e["runNote0101_1116"] = notes[name]; continue
    prim = PRIMARY.get(name, "totalSupply")
    prev = e.get(prim)
    cur = v.get(prim)
    if cur is None:
        cur = v.get("totalMinted") if v.get("totalMinted") is not None else v.get("totalSupply")
        prim_eff = "totalMinted" if v.get("totalMinted") is not None else "totalSupply"
        prev = e.get(prim_eff)
    else:
        prim_eff = prim
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
    e["lastReadWib"] = "2026-11-16 ~01:01 WIB"
    fc = v.get("freeClaimed"); fm = v.get("freeMinted")
    fs = v.get("FREE_SUPPLY") or v.get("FREE_CAP") or v.get("FREE_MAX")
    freepct = f"{fm or fc}/{fs}={round(100*(fm or fc)/fs,1)}%" if (fm or fc) is not None and fs else "-"
    rate_s = f"{rate:.3f}" if rate is not None else "?"
    notes[name] = (f"Run 0101 (blok {BLK}, interval {INTERVAL} mnt vs run 0031): {prim_eff} {prev}->{cur} "
                   f"(+{delta if delta is not None else '?'}, {rate_s}/mnt vs prev {prev_rate} = "
                   f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if vel else 'GAGAL'}; "
                   f"free {freepct}; bal_user={v.get('balanceOf_user')}; DIAM.")
    e["runNote0101_1116"] = notes[name]
    print(name, "->", notes[name][:150])

# Track B pending claim
pc = s.setdefault("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["launched"] = 0; pc["failed"] = 1; pc["isRefundPhase"] = 1; pc["totalShares"] = 3110
    pc["tokenClaimed_user"] = 0; pc["lastReadWib"] = "2026-11-16 ~01:01 WIB"
    pc["runNote0101_1116"] = (f"Run 0101 (blok {BLK}): launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                               "tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
# Track C
tc = s.setdefault("track_c", {})
if "ORBIT" in tc:
    tc["ORBIT"]["freeClaimed"] = 292; tc["ORBIT"]["claimOpen"] = 1; tc["ORBIT"]["hasFreeClaimed_user"] = 0
    tc["ORBIT"]["lastReadBlock"] = BLK; tc["ORBIT"]["lastReadWib"] = "2026-11-16 ~01:01 WIB"
    tc["ORBIT"]["runNote0101_1116"] = (f"Run 0101 (blok {BLK}): freeClaimed 292/888 TETAP, claimOpen 1, "
                                        "hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.")
if "RigForge" in tc:
    tc["RigForge"]["freeSharesLeft"] = 639; tc["RigForge"]["openedAt"] = 0; tc["RigForge"]["freeClaimed"] = 361
    tc["RigForge"]["lastReadBlock"] = BLK; tc["RigForge"]["lastReadWib"] = "2026-11-16 ~01:01 WIB"
    tc["RigForge"]["runNote0101_1116"] = (f"Run 0101 (blok {BLK}): freeSharesLeft 639, openedAt 0 (pool belum buka), "
                                           "freeClaimed 361 - DIAM.")

# Age-exclusions
removed = []
for key in ["B77D", "AbsurdAgentNFT", "AbsurdAgentNFT-72C1"]:
    if key in s["contracts"]:
        del s["contracts"][key]; removed.append(key)
print("REMOVED:", removed, "| contracts now:", len(s["contracts"]))

s["runNote0101_1116"] = ("Run 0101 (blok 133780435, interval ~30,5 mnt vs run 0031): re-read 35/35 OK. "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, "
    "0 eksekusi/preview. Velocity: 0 lolos (delta terbesar +2, MORFO). Free% tertinggi: AgentBubble 1542/2222=69,4% "
    "(<70% strong lead). Age-excluded: B77D (dilaporkan sekali) + AbsurdAgentNFT (diam). Verdict: DIAM + 1 laporan age-exclusion (B77D).")
s["runNote0101_1116_scan"] = ("Run 0101: scan leg FAST-FAIL - pre-flight Ankr getLogs 50 blok HTTP 401 Unauthorized (1,10 dtk). "
    "Watermark TETAP 132512564 (head 133780727, gap 1.268.163). Track-C 5c dilewati (tidak ada output scan).")
s["runNote0101_1116_ageex"] = ("Age-exclusion run 0101: (1) B77D 0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe - launch TERVERIFIKASI "
    "14 Nov 08:05-08:34 WIB (first-mint run 0831 14 Nov), umur ~40,5 jam >24 jam, totalMinted 1285, belum sold out, free% UNVERIFIED; "
    "early lead DILAPORKAN SEKALI run 0831 14 Nov -> dilaporkan sekali sebagai age-excluded run ini, DIHAPUS dari snapshot + ITEMS. "
    "(2) AbsurdAgentNFT 0x72c14121681F1133545947B0735563835CC07B67 - mintStartTime on-chain 1794650400 = 14 Nov 17:00 WIB, first mint "
    "terkoroborasi bounded 15:31-23:01 WIB 14 Nov (totalMinted 0->240), umur ~32 jam >24 jam, totalMinted 241/2222, belum sold out; "
    "TIDAK PERNAH dilaporkan sebagai lead (watchlist-only-upcoming saja) -> DIHAPUS DIAM-DIAM dari snapshot (2 entri: AbsurdAgentNFT + "
    "AbsurdAgentNFT-72C1) + ITEMS, dicatat di run log saja.")
s["runNote0101_1116_boltbook"] = ("Run 0101 Boltbook EN (48.542 byte) + ZH (48.249 byte), HTTP 200. 6 EN / 5 ZH alamat distinct; 4 baru vs run 0031, "
    "semuanya sudah ditriase hot leg / tercatat: KERNELMONK 0x016b... (snapshot minted-by-user-2026-11-10, recheck 888/5555); Golden Agents 0x4233... "
    "(age-excluded-2026-11-11 + watchlist-only-2026-11-15, 2.222/100.000); DRAGON 0xad0d... (snapshot age-excluded-2026-11-14, recheck 844/1888, "
    "freeClaimed 840/888); Vexa Agent 0xb1d8... (BARU dicek run ini: Sourcify 404, registry_bytes FALSE di bytecode 6.799 byte, totalSupply 9901/10000 "
    "terkonfirmasi on-chain, tanpa free view, mint(1)/mint(2)/freeMint() revert di value 0 + paid 0,001 BNB per post Boltbook -> BUKAN agent-shaped + "
    "BUKAN free -> checked-not-lead, tidak masuk snapshot, tidak dilaporkan).")
s["runNote0101_1116_sweep"] = ("Run 0101 sweep EN+ZH (3 query) + Sourcify feed + Odaily/PANews: 0 hit segar baru. Sourcify 20 kontrak, top verifiedAt 18:03:00Z; "
    "10 baru vs run 0031 - 9 sudah shape-check hot leg (S1/S2 false, agent false), 1 dicek run ini 0x68801a54 (Sourcify 404, registry_bytes FALSE, "
    "totalSupply 1e27 = plain ERC-20 -> NOT sale-shape, NOT agent-shaped). Sweep: Oathbots, Agentic Gangster (free-pool-exhausted), LeadLoop, "
    "NEXUS CORE, hackou, AGENT ID cards, Agent Koi (semua 25 Okt / sudah tercatat); KOMA (age-excluded-2026-11-14, sale tutup 16 Nov 22:00 WIB+8); "
    "First-Dollar Grove (age-excluded); Xuanwu Seed (mint buka 25 Okt, umur >24 jam, tidak di snapshot, bukan lead); ORBITA (closed 8 Nov); "
    "Rulz Share (age-excluded run 0031); UFO/NEBULA (UFO tutup 12 Nov); NOVRA (age-excluded-2026-11-12, free pool 0). Odaily newsflash + PANews: "
    "0 pengumuman Agent ID baru. DappBay tidak dipakai (tidak ada proyek baru untuk di-cek).")
s["runNote0101_1116_binanceai"] = "Run 0101: binanceai.fun TIDAK BERUBAH (launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed user=0) - fase refund, DIAM."
s["runNote0101_1116_bridge"] = "Run 0101 bridge (read-only): 116 kontrak bridge, 116/116 sudah di snapshot (per alamat), 0 baru, 7 same_owner_discarded. Tidak ada temuan pelengkap baru / promosi. Job ini tidak menulis bridge."
s["runNote0101_1116_vexa"] = ("Vexa Agent 0xb1d8a50d689d62626a252ed642b122db77f89caa triase run ini: post Boltbook grandtheftauto6.ai ~01:00 WIB klaim 9.901/10.000 "
    "(99 free left); verifikasi sendiri via eth_call dataseed: totalSupply 9901 TERKONFIRMASI, code 6.799 byte, registry_bytes FALSE (tanpa referensi "
    "registry Agent ID), freeClaimed/FREE_SUPPLY/mintOpen/mintPrice/PRICE/priceFor/costFor SEMUA revert (tanpa free view), Sourcify 404 (unverified). "
    "Post Boltbook: mint(1)/mint(2)/freeMint() revert di value 0, paid 0,001 BNB. Vonis: BUKAN agent-shaped + BUKAN free (paid-only) -> checked-not-lead, "
    "tidak masuk snapshot, tidak dilaporkan. Catatan: lonjakan +9.000 dari angka 901 sebelumnya (post menyebut counter-check) tidak diverifikasi lanjut - tidak relevan karena bukan free.")
s["last_run_wib"] = "2026-11-16 ~01:01 WIB"
s["last_run_note"] = s["runNote0101_1116"]
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED. contracts:", len(s["contracts"]))
