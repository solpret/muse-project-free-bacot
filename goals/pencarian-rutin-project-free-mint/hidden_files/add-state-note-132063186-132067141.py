#!/usr/bin/env python3
import json
p = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-scan-state.json"
s = json.load(open(p))
s["note_backfill_parallel_132063186_132067141_triage"] = (
    "Triase first-seen: Jager Agent Pass (JAP) 0x951f705feB9dCc95D58b445BE58b869724E50707 - "
    "first mint blok 132063227, 2026-11-07 02:17:17 WIB (umur ~0,7 jam), 61 mint / 61 minter. "
    "AGENT_REGISTRY()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F PERSIS (konstanta, bukan agentRegistry()). "
    "MAX_SUPPLY 777, MAX_FREE_TOTAL 333, freeMinted 178 (53,5%), MAX_FREE_PER_WALLET 1, "
    "freeCount(user)=0 + balanceOf(user)=0 -> slot user terbuka; MINT_PRICE 0,0015 BNB (jalur berbayar). "
    "Owner 0x67230d320f714ac82c6ec253d238cfa309fb1b85 = SAME-OWNER DISCARD (grup deployer: Cz Agent, "
    "MAMESUKE, Whale Agent, 2026-11-03) -> HANYA dicatat di log, TIDAK dilaporkan, TIDAK masuk snapshot. "
    "Jager Agent (JAGER) 0xD8EBDDE362B0a72F7D61b5eD990742B940E30D27 - first mint blok 132067118, "
    "02:46:29 WIB (umur ~0,2 jam), 2 mint, AGENT_REGISTRY() PERSIS, MAX_SUPPLY 1110, freeMinted 12, "
    "owner SAMA (discard) -> hanya dicatat di log. Track-C 5c: 56 kandidat mint_count>=10, 15 baru dicek "
    "(maks 20/run), 0 sale-shape hit. Watermark 132067141; head 132068778 saat cek (~03:00) -> gap 1.637 "
    "blok < 2.000: backfill mengejar head; laporan mengejar-head SUDAH pernah 4x di timeline goal dan "
    "cron tetap jalan atas keputusan parent - tidak dilaporkan ulang. TIDAK pernah di-preview/mint "
    "(job backfill read-only)."
)
json.dump(s, open(p, "w"), indent=1)
print("state note added; watermark:", s["last_scanned_block"])
