#!/usr/bin/env python3
"""Merge run 2026-11-11 0431 readings into onchain-snapshot.json.
Read-only except the snapshot (backup first)."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-0431"
BLOCK = 132849154
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0431-premerge")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0431-reread.json"))
freeprobe = json.load(open(BASE + "run-2026-11-11-0431-freeprobe.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

def upd(name, **kw):
    e = contracts.setdefault(name, {})
    e.update(kw)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 04:31 WIB"
    return e

# Priority re-reads: totalSupply from LEAN (block 132849154), velocity vs run 0401
VEL = {
 "NIGHTFORGE": "Run 0431 (blok 132849154): totalSupply 708->709 (+1), agentFreeUsed 705->708 (+3, probe blok ~132851xxx) -> velocity GAGAL (<20). Free 708/2000 = 35,4% (>=25% ✓), slot terbuka (bal_user 0), umur terverifikasi <24 jam (deadline 14:37 WIB), TAPI gate website TETAP BLOCKED -> TIDAK di-mint.",
 "SOLDERCATS": "Run 0431 (blok 132849154): totalSupply 458->461 (+3), agentFreeUsed 458->462 (+4, probe) -> velocity GAGAL (<20). Free 462/2000 = 23,1% (<25%). Tetap EARLY.",
 "REWINDCLUB": "Run 0431 (blok 132849154): totalSupply 418->421 (+3), agentFreeUsed 418->424 (+6, probe) -> velocity GAGAL (<20). Free 424/2000 = 21,2% (<25%). Tetap EARLY.",
 "LCDSPRITE": "Run 0431 (blok 132849154): totalSupply 471->475 (+4), agentFreeUsed 471->477 (+6, probe) -> velocity GAGAL (<20). Free 477/2000 = 23,85% (<25%). Tetap EARLY.",
 "Pico Alcazar": "Run 0431 (blok 132849154): totalSupply 285->300 (+15) -> velocity GAGAL (<20). Tetap EARLY.",
 "Tiling Hammock": "Run 0431 (blok 132849154): totalSupply 274->286 (+12) -> velocity GAGAL (<20). Tetap EARLY.",
 "Hexel Pantry": "Run 0431 (blok 132849154): totalSupply 283->295 (+12) -> velocity GAGAL (<20). Tetap EARLY.",
 "STALL": "Run 0431 (blok 132849154): totalSupply 1652->1670 (+18) -> velocity GAGAL (<20). Tetap EARLY.",
 "Arcane Stones": "Run 0431 (blok 132849154): totalSupply 650 flat -> velocity GAGAL. Tetap EARLY.",
 "Cosmic Sentinel": "Run 0431 (blok 132849154): totalSupply 400 flat; freeMinted 395/225.000 = 0,18% -> tetap watchlist-only.",
 "Dragon Agent": "Run 0431 (blok 132849154): totalSupply 906 flat -> velocity GAGAL; umur + free% TETAP UNVERIFIED. Watchlist-only.",
 "GangDotFun": "Run 0431 (blok 132849154): freeMinted 367->374 (+7); tanpa Agent-ID gate -> tetap watchlist-only first-read.",
 "Kitebots": "Run 0431 (blok 132849154): totalSupply 983->984 (+1), freeMinted 984 -> velocity GAGAL.",
 "WORKER": "Run 0431 (blok 132849154): totalSupply 358->360 (+2) -> velocity GAGAL; umur + free% TETAP UNVERIFIED; website PASSED; slot terbuka; watchlist-only, TIDAK di-preview/TIDAK di-mint.",
 "Skywe Legion": "Run 0431: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; umur + free% + website TETAP UNVERIFIED; watchlist-only.",
 "NIGHTFORGE B": "Run 0431 (blok 132849154): totalSupply 326 flat -> velocity GAGAL.",
 "RIMEVAULT": "Run 0431 (blok 132849154): totalSupply 504->506 (+2 pasca-mint user #504 run 0401); bal_user=1; minted-by-user, bukan kandidat.",
 "MYCELIX": "Run 0431 (blok 132849154): totalSupply 508->511 (+3 pasca-mint user #508 run 0401); bal_user=1; minted-by-user, bukan kandidat.",
 "ORBITJANITOR": "Run 0431 (blok 132849154): totalSupply 641 flat; bal_user=1; minted-by-user, bukan kandidat.",
 "EMBERANVIL": "Run 0431 (blok 132849154): totalSupply 1035->1039 (+4); bal_user=1; minted-by-user, bukan kandidat.",
 "BYTEBLOOM": "Run 0431 (blok 132849154): totalSupply 576->578 (+2); bal_user=1; minted-by-user, bukan kandidat.",
}
for name, note in VEL.items():
    r = reread.get("reread", {}).get(name, {})
    e = upd(name)
    if r.get("totalSupply") is not None:
        e["previousTotalSupply"] = e.get("totalSupply")
        e["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None:
        e["freeMinted"] = r["freeMinted"]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["runNote0431_1111"] = note
    e["velocityLegPasses"] = False
# free-probe values (later block, same run)
for name, d in freeprobe.items():
    e = contracts.get(name, {})
    if d.get("agentFreeUsed()") is not None:
        e["agentFreeUsed"] = d["agentFreeUsed()"]
    if d.get("paidMinted()") is not None:
        e["paidMinted"] = d["paidMinted()"]

# Track-C re-reads
for name, v in reread.get("track_c", {}).items():
    e = track_c.get(name)
    if not isinstance(e, dict):
        continue
    if v.get("freeMinted") is not None:
        e["freeMinted"] = v["freeMinted"]
    if v.get("totalSupply") is not None:
        e["totalSupply"] = v["totalSupply"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 04:31 WIB"
tc = track_c.get("MOODENG", {})
tc["runNote0431"] = "Run 0431: freeMinted 451->458 (+7); agent-shape TETAP UNVERIFIED + website UNVERIFIED -> watchlist-only, TIDAK di-preview/TIDAK di-mint."
for k in ("NIUBI", "DROID", "960E-sale", "FUGUI-set1-991", "FUGUI-set2", "11-11"):
    if isinstance(track_c.get(k), dict):
        track_c[k]["runNote0431"] = "Run 0431: tanpa perubahan (freeMinted flat vs run 0401)."

# NEBULA -> track_c minted-by-user
track_c["NEBULA"] = {
 "address": "0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68",
 "status": "minted-by-user-2026-11-11",
 "name": "NEBULA",
 "symbol": "NEB",
 "kind": "ERC20-sale-single-contract",
 "website": "https://nebula-neb.pages.dev",
 "x": "https://x.com/nebulaneal",
 "MAX_SHARES": 5000,
 "TOKENS_PER_SHARE": 1000,
 "PRICE": 1000000000000000,
 "totalShares": 967,
 "totalFreeShares": 958,
 "totalPaidShares": 9,
 "freeMinted": 958,
 "userFreeUsed": 1,
 "userBalance": 1000,
 "userSlotNote": "Slot USED by user mint run 0431 (tx 0x65b5844f22c5bff06b6c84b1e8a3369f8772c8b4b67cfe9f0eaa3d1bf8ab4ea2, blok 132851962, receipt 1, gas 129.731, fee ~0,0000098577 BNB); freeUsed(user) 0->1, balanceOf 0->1000 NEB; do not re-report as slot change",
 "mintTx": "0x65b5844f22c5bff06b6c84b1e8a3369f8772c8b4b67cfe9f0eaa3d1bf8ab4ea2",
 "mintBlock": 132851962,
 "mintGas": 129731,
 "audit": "Binance hasResult=true, riskLevel 2 LOW, riskAlert null, buyTax 0.0/sellTax 0.0, isVerified true; satu-satunya hit CAUTION Newly Created Token, TIDAK ada item RISK yang isHit.",
 "preview": "simulationCode 000000000, balance change +1e21 NEB (1000 NEB = TOKENS_PER_SHARE), authority/allowance [], risks [], requestId 5cc83a589dc046ae90968afceb9aa9bf",
 "launchNote": "Launch diumumkan @nebulaneal ~10:50 UTC / 17:50 WIB 10 Nov 2026 (post 'is live', 1 post, relatif '11h' saat dibaca browser 21:50 UTC; tanggal absolut tak terbaca tanpa login). Koroborasi: Sourcify verifiedAt 2026-11-10T10:24:24Z; AirdropBuzz snapshot 15:58 UTC 10 Nov: 305 free shares; on-chain 944 free shares 04:45 WIB 11 Nov. Umur ~11 jam saat mint. First-mint log TIDAK terverifikasi on-chain run ini (Ankr 401 + public RPC eth_getLogs -32005 + historical eth_getCode -32000 missing trie node); file run-2026-11-11-0431-nebula-deploy.json berisi hasil binary-search yang SALAH (RPC gagal dibaca sebagai 'tidak ada kode') dan TIDAK BOLEH dipakai.",
 "gate": "website_verified (nebula-neb.pages.dev mencetak kontrak persis, 2 kecocokan di homepage + skill.md; X https://x.com/nebulaneal tercantum di skill.md)",
 "shape": "S1: mint(uint256,address) + quote(address,uint256)->(freeShares,costBnb) + free views (totalFreeShares/freeUsed) + agentIdRegistry() = 0x60B9...022F",
 "pendingSwap": "1000 NEB didaftarkan di pending-swaps.json (run 0431): PCS V2 pair NEB/WBNB = 0x0, tidak bisa di-swap; pantau sampai pair terbentuk + likuiditas > 0 + quote >= 2x gas.",
 "firstSeenWib": "2026-11-11 ~04:31 WIB",
 "lastReadBlock": 132852087,
 "lastReadWib": "2026-11-11 05:05 WIB",
}

# AgentPals -> contracts upcoming watchlist-only
contracts["AgentPals"] = {
 "address": "0xD265a929D0E50bD5ee4675e4E97F38D8380802E2",
 "status": "watchlist-only-upcoming-2026-11-11",
 "name": "AgentPals",
 "symbol": "APAL",
 "kind": "ERC721",
 "registry()": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "FREE_SUPPLY": 300,
 "MAX_SUPPLY": 1111,
 "freeMinted": 0,
 "totalMinted": 0,
 "freePhaseStart": 0,
 "priorityActive": 0,
 "PRIORITY_CAP": 200,
 "PRIORITY_WINDOW": 43200,
 "paidPrice": 500000000000000,
 "baseURI": "https://AGENTPALS_WORKER_TBD/",
 "owner": "0x9e07f754116315298d8aaf3e24181de2907b4623",
 "palsToken": "0x01B0150501dec67a26BBF079129Dd2fEf81EB2dd",
 "agtc": "0x7bcc29c5405286b4dd8b5b23fe7097f9ee65e4e5",
 "hasFreeMinted_user": 0,
 "balanceOf_user": 0,
 "firstSeenWib": "2026-11-11 ~04:31 WIB",
 "lastReadBlock": 132849745,
 "lastReadWib": "2026-11-11 04:31 WIB",
 "source": "Sourcify feed run 0431 (verified 2026-11-10T21:31:02Z = 04:31:02 WIB) + baca on-chain; S1 shape (mint/mintFree + quote-ish EVOLVE_COST + FREE_SUPPLY/freeMinted + registry)",
 "gate": "website_unverified (baseURI placeholder AGENTPALS_WORKER_TBD; pencarian nama + alamat kontrak 0 hasil; Sourcify metadata tanpa URL; tanpa contractURI)",
 "baselineNote": "UPCOMING watchlist-only run 0431 (temuan feed Sourcify recently-verified): registry() = registry persis 0x60B9...022F, freePhaseStart=0, totalMinted=0, FREE_SUPPLY 300, MAX 1111, name AgentPals / APAL. BELUM launching (0 mint, fase gratis belum dibuka) -> BUKAN early lead (belum ada first mint), BUKAN kandidat, TIDAK di-preview/di-mint; dilaporkan sekali sebagai upcoming watchlist-only. Promosi hanya bila first mint terverifikasi on-chain + umur <24 jam + gate website lolos.",
}

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK contracts:", len(contracts), "track_c:", len(track_c))
print("NEBULA in track_c:", "NEBULA" in track_c, "| AgentPals in contracts:", "AgentPals" in contracts)
