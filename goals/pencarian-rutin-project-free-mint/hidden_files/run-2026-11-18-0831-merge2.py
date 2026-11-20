#!/usr/bin/env python3
"""Merge step 2 run 2026-11-18 08:31 WIB: 4 age-exclusion removals (queued by run 0801),
checked-not-sale-shape record, run note, last_run, scan-state note. Read-only legs only.
Never writes scan-bridge.json. No preview/mint/claim."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
NOW="2026-11-18 ~08:31 WIB"
BLOCK=134226357  # age-sweep read block; main re-read block 134224438

# --- 4 AGE-EXCLUSION REMOVALS (live-verified this run, all not sold out, age >> 24h) ---
removed={
 "Alchemister": "AGE-EXCLUDED run 0831: firstSeen 2026-11-07T07:56:07+07:00 (scan first-seen, block 132108393; launch <= firstSeen) -> umur ~11 hari 1 jam (>=24 jam) terverifikasi; live read run ini blok 134226357: totalSupply 3717/15000 MAX_SUPPLY, mintOpen 1 -> BELUM sold out. Dihapus dari snapshot, dilaporkan sekali.",
 "BotWar Arena Test": "AGE-EXCLUDED run 0831: firstSeen 2026-11-07T08:35:23+07:00 (block 132113626) -> umur ~11 hari (>=24 jam) terverifikasi; live read run ini blok 134226357: totalSupply 201/2222 MAX_SUPPLY, mintOpen 1 -> BELUM sold out. Dihapus dari snapshot, dilaporkan sekali.",
 "ONI-d576": "AGE-EXCLUDED run 0831: firstSeen 2026-11-07T08:51:03+07:00 (block 132115715) -> umur ~11 hari (>=24 jam) terverifikasi; live read run ini blok 134226357: totalMinted 1010/4444 MAX_SUPPLY, freeMinted 1000/1000 FREE_POOL (free pool HABIS) -> BELUM sold out total. Dihapus dari snapshot, dilaporkan sekali.",
 "KIJIN": "AGE-EXCLUDED run 0831: firstSeen 2026-11-09 00:32:53 WIB (block 132433188) -> umur ~9 hari 8 jam (>=24 jam) terverifikasi; live read run ini blok 134226357: totalMinted 2655/15000 maxSupply, freeRemaining 2345/5000 -> BELUM sold out. Dihapus dari snapshot, dilaporkan sekali.",
}
for k, note in removed.items():
    if k in snap.get("contracts", {}):
        del snap["contracts"][k]
        print("REMOVED", k)
    else:
        print("ALREADY-GONE", k)
    snap[f"removed0831_{k.lower().replace(' ','_').replace('-','_')}"] = note

# --- fix the sed-copied 0801 note strings to 0831 values ---
pc=snap.get("pending_claims",{}).get("binanceai.fun")
if isinstance(pc,dict):
    pc["runNote0831"]="Run 0831 (blok 134224438): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0, totalShares=3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM."
rf=(snap.get("track_c",{}) or {}).get("RigForge")
if isinstance(rf,dict):
    rf["runNote0831"]="Run 0831 (blok 134224438): openedAt 0, freeSharesLeft 624, freeClaimed 376 - belum dibuka. DIAM."
ac=snap.get("contracts",{}).get("ARKT-claim-62a7")
if isinstance(ac,dict):
    ac["runNote0831"]="Run 0831: totalSupply 3 flat, totalMinted 3, paused 0, hasClaimed(user) 0 - tanpa perubahan. Early lead sudah dilaporkan sekali run 0331; tanpa perubahan."

snap["checkedNotSaleShape0831_1118"]={
 "sourcify_0831": "Feed top BERUBAH vs 0801 (verifiedAt top 2026-11-18T01:35:03Z): 3 kontrak baru vs hot-leg-seen (hot-leg 0829 terakhir 01:29 UTC). 0x2798eA91f26F623D1F90a427F15c6720813CdE4b (verifiedAt 01:35:03Z, 22 fns, tanpa mint/free views, tokenRegistry bukan Agent ID registry, registry-bytes NO) -> checked-not-agent-shaped. 0x41c554d9Ec3e3eDAB8729940C0673713C8b0e29c (verifiedAt 01:32:47Z, 31 fns: claimFree/claimPaid/carve + FREE_SLOTS/myFree + AGENT_ID/agentIdOf, TANPA fungsi mint, TANPA quote/cost) -> S1 FALSE + S2 FALSE -> checked-not-sale-shape; probe on-chain blok 134226523: FREE_SLOTS 200, carveOpen 1, registerOpen 1, registeredCount 2, ENTRY_FEE 0,02 BNB, ENTRY_TOKENS 5000, registered(user) 0, agentIdOf(user) 0, myFree(user) 1 - game carve signer-gated, BUKAN NFT mint / share sale / klaim entitlement (tanpa LP hook, tanpa website/diskusi) -> BUKAN lead, TIDAK di-preview/di-mint. 0xd55e9f4F66C3cf00C66D199C3E0D03d8491149f9 (verifiedAt 01:32:43Z, 12 fns: mint/minters/setMinter + agentIdOf, tanpa free views/quote, totalSupply 2, registry-bytes NO) -> checked-not-agent-shaped.",
 "boltbook_new_0831": "Boltbook EN+ZH (44.899/43.365 byte, HTTP 200): 8+8 alamat, 1 tampak-baru 0x3091fec6e86036951fc131029bcd768f55ed2a92 = ACARD (post aliq.ai ~6 mnt lalu: 'ACARD free 264 to 0, DRAGON 888 of 888'): Sourcify exact_match verifiedAt 2026-11-16T16:03:33Z, ABI freeMint/freeMintedByWallet/paidQuote/freeRemaining/AGENT_ID_REGISTRY (S1 shape) TAPI live read blok 134226523: totalMinted 1890/2222, freeMinted 1888, freeRemaining 0 -> FREE POOL HABIS + umur >24 jam (verified 16 Nov) -> BUKAN lead, tidak dilaporkan, tidak di-preview/di-mint. LODE Miner (post hensyah08.ai: totalMinted 850/4.444) + Pickhash (3271/7777) disebut di front page TANPA alamat kontrak di teks -> tidak bisa diverifikasi on-chain dari leg ini; pencarian web 'LODE Miner LMINER BSC contract' tidak menemukan alamat kontrak (hasil: AgentMiner token lain, Agent Oil Rig 4 Nov, BINANCE ALPHA BOT free allocation habis 11/11) -> dicatat saja, bukan lead.",
}
snap["last_run"]="free-mint-search 2026-11-18 08:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; 4 REMOVAL age-excluded (Alchemister, BotWar Arena Test, ONI-d576, KIJIN) - dilaporkan sekali"
snap["last_run_wib"]="2026-11-18 ~08:31 WIB"
snap["runNote0831_1118"]="Run 0831 (blok re-read 134224438, interval ~31,3 mnt vs 0801): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead. REMOVAL 4x AGE-EXCLUDED (live-verified run ini, blok age-sweep 134226357, semua belum sold out, umur terverifikasi >=24 jam): Alchemister (firstSeen 7 Nov 07:56 WIB, totalSupply 3717/15000, mintOpen 1), BotWar Arena Test (firstSeen 7 Nov 08:35 WIB, totalSupply 201/2222, mintOpen 1), ONI-d576 (firstSeen 7 Nov 08:51 WIB, totalMinted 1010/4444, freeMinted 1000/1000 FREE_POOL habis), KIJIN (firstSeen 9 Nov 00:32 WIB, totalMinted 2655/15000, freeRemaining 2345/5000) - keempatnya dihapus dari snapshot, dilaporkan sekali. Scan FAST-FAIL (Ankr 401 ke-49 berturut-turut main job, elapsed 5,7 dtk, head 134224438; watermark tetap 134086385; gap ~138.053 blok). Re-read 212 calls, 0 chunk error. Velocity: EIM +44 (567->611, 1,41/mnt vs prev 1,47 = 0,96x) GAGAL; Mine Card +30 (1164->1194, 0,96/mnt vs prev 1,20 = 0,80x) GAGAL; Stromboat +23 (totalMinted 226->249, 0,73/mnt vs prev 0,90 = 0,81x) GAGAL, free 250/667=37,5%; ARKYN +19 (<20) GAGAL; RAVE +11, STOCK +11, Matrix +5, AgentEcho +6 (<20) GAGAL; lainnya flat/+1..+3 GAGAL. AgentBubble 84,9% (freeMinted 1887/2222) + Lumenhold 83,5% (freeClaimed 1252/1500) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. STOCK AGENT free 616/1111=55,4% (umur UNVERIFIED + X unverified, slot user terbuka quote 0); Matrix 60,3% (603/1000), AGCLUB 59,3% (527/888) di bawah 70%. PunchCard 23,4% (1301/5555). HIVE flat 1263, Bubblebruin flat 2620 (freeClaimed 2614/7777=33,6%). THYRK slot user sudah terpakai. JADE cost user 0,0005 BNB (bukan gratis). CAT402 sold out (freeCatsClaimed 100/100). PIXELFROGS mintOpen 0. DRAGON free pool habis 1000/1000, bal 1. ARKT flat 323/1000, hasClaimed 0. ARKT-claim-62a7 totalSupply 3 flat, hasClaimed 0. bsccat freeMinted 523 flat; pepe free pool habis 500/500 + user sudah mint. Sourcify feed top BERUBAH (verifiedAt 01:35:03Z): 3 baru, 0 hit S1/S2 (0x41c5 near-miss game carve, 0x2798 + 0xd55e bukan agent-shaped) -> checked-not-sale-shape. Boltbook EN+ZH (44.899/43.365 byte, HTTP 200): 8+8 alamat, 1 tampak-baru ACARD 0x3091... (free pool HABIS 0, umur >24 jam) -> bukan lead. Sweep EN+ZH: 0 baru (Oathbots 28 Okt, Agentic Gangster 9 Nov free sold out 111/111, STAMP PASS 9 Nov, RIGBYPASS 10 Nov, AGENT COSMOS 5 Nov, BN Agent Trials musim berakhir 8 Nov, QILIN/SAFU/PROXY/Transfire 1 Nov, AGENTID 25 Okt, Subsonic Tribe 26 Okt - semuanya berumur >24 jam / pool habis). Odaily newsflash (277.595 byte) + PANews (118.606 byte), keduanya HTTP 200: 0 hit Agent ID/free-mint/free-share. Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0, totalShares 3110). RigForge belum dibuka (openedAt 0, freeSharesLeft 624, freeClaimed 376)."

st=json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0831_scan"]=("Run 2026-11-18 08:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 5,7 dtk, head 134224438); 401 auth-wide, gagal total ke-49 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~138.053 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json","w"), indent=1)
json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
