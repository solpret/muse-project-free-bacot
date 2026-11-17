#!/usr/bin/env python3
"""Run 0131 merge: update priority reads + add NP trio / GangDotFun / Agentic Gangster. No executions."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=s["contracts"]
BLOCK=132825163
def upd(name, note, **kw):
    e=C.setdefault(name, {})
    e.update(kw)
    e["runNote0131_1111"]=note
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-11 01:31 WIB"
# priority re-reads (agentFreeUsed fresh)
upd("REWINDCLUB","Run 0131 (blok 132825163): totalSupply 376->380 (+4, ~0,12/mnt vs pace Boltbook ~1,5/mnt = 0,08x, <20 token) velocity GAGAL; agentFreeUsed 380/2000 = 19,0% (<25%); slot terbuka (agentFreeByWallet 0, balanceOf 0); website terverifikasi; tetap EARLY, tanpa promosi.",
    totalSupply=380, agentFreeUsed=380, balanceOf_user=0, agentFreeByWallet_user=0)
upd("LCDSPRITE","Run 0131 (blok 132825163): totalSupply 421->424 (+3, ~0,09/mnt vs ~1,6/mnt = 0,06x, <20) velocity GAGAL; agentFreeUsed 424/2000 = 21,2% (<25%); slot terbuka; website terverifikasi; tetap EARLY, tanpa promosi.",
    totalSupply=424, agentFreeUsed=424, balanceOf_user=0, agentFreeByWallet_user=0)
upd("RIMEVAULT","Run 0131 (blok 132825163): totalSupply 416->427 (+11, ~0,32/mnt vs pace 1,4-2,9/mnt = 0,11-0,23x, <20) velocity GAGAL; agentFreeUsed 427/2000 = 21,35% (<25%); slot terbuka; website terverifikasi; tetap EARLY, tanpa promosi.",
    totalSupply=427, agentFreeUsed=427, balanceOf_user=0, agentFreeByWallet_user=0)
upd("MYCELIX","Run 0131 (blok 132825163): totalSupply 450->452 (+2, ~0,06/mnt vs ~0,8/mnt = 0,08x, <20) velocity GAGAL; agentFreeUsed 452/2000 = 22,6% (<25%); slot terbuka; website terverifikasi; tetap EARLY, tanpa promosi.",
    totalSupply=452, agentFreeUsed=452, balanceOf_user=0, agentFreeByWallet_user=0)
upd("NIGHTFORGE","Run 0131 (blok 132825163): totalSupply 683->685 (+2); agentFreeUsed 682/2000 = 34,1% (tetap >=25% strong-leg %); slot terbuka (agentFreeByWallet 0, balanceOf 0); TETAP GATE-BLOCKED (website unverified) - TIDAK di-mint; deadline umur 2026-11-11 14:37 WIB.",
    totalSupply=685, agentFreeUsed=682, balanceOf_user=0, agentFreeByWallet_user=0)
upd("SOLDERCATS","Run 0131 (blok 132825163): totalSupply 427->435 (+8, <20) velocity GAGAL; agentFreeUsed 435/2000 = 21,75% (<25%); slot terbuka; gate website PASSED (metode H); tetap EARLY, tanpa promosi.",
    totalSupply=435, agentFreeUsed=435, balanceOf_user=0, agentFreeByWallet_user=0)
upd("EMBERANVIL","Run 0131: totalSupply 1025, balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.", totalSupply=1025, balanceOf_user=1)
upd("BYTEBLOOM","Run 0131: totalSupply 566 (was 563), balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.", totalSupply=566, balanceOf_user=1)
upd("ORBITJANITOR","Run 0131: totalSupply 605->618 (+13); agentFreeUsed 618; balanceOf(user)=1, agentFreeByWallet(user)=1 - slot terpakai (minted-by-user #552 run 0001); tanpa perubahan.",
    totalSupply=618, agentFreeUsed=618, balanceOf_user=1, agentFreeByWallet_user=1)
upd("STALL","Run 0131: totalSupply 1587->1601 (+14); mintOpen 1; balanceOf(user)=0; owner 0x3d018a51905e3bc6ea01e5d731e6a0ce89929fd7 (bukan di discards); registry-bytes TRUE; contractURI None; free% + umur TETAP UNVERIFIED - tetap EARLY, tanpa promosi.",
    totalSupply=1601, balanceOf_user=0)
upd("Arcane Stones","Run 0131: totalSupply 642->644 (+2); balanceOf(user)=0; registry-bytes TRUE; contractURI None; website terverifikasi (arcanestones.pages.dev); umur TETAP UNVERIFIED - tetap EARLY, tanpa promosi.",
    totalSupply=644, balanceOf_user=0)
upd("Dragon Agent","Run 0131: totalSupply 904 (tetap); canMint(user)=1, balanceOf(user)=0, slot terbuka; REGISTRY() persis; registry-bytes TRUE; contractURI None; free% UNVERIFIED; umur TETAP UNVERIFIED - DITAHAN preseden run 2026-11-10 (launch unverified), BUKAN age-excluded; tetap EARLY, tanpa promosi.",
    totalSupply=904, canMint_user=1, balanceOf_user=0)
# new entries
C["Pico Alcazar"]={
 "address":"0xdf95946fe4ea475e7180f77817f9e34b459121f2","name":"Pico Alcazar","symbol":"NP01","kind":"ERC721",
 "status":"early-lead-reported-2026-11-11","totalSupply":240,"MAX_SUPPLY":1164,"mintOpen":1,"balanceOf_user":0,
 "owner":"0x08df7970bb2c632908e3df036d0439420d9ce858","registryBytes":True,
 "firstSeenBlock":132829733,"firstSeenWib":"2026-11-11 ~01:20 WIB",
 "website":None,
 "baselineNote":"EARLY LEAD BARU run 0131 (dilaporkan sekali; TIDAK di-preview/TIDAK di-mint). Boltbook EN post ~01:20 WIB (blok 132829733): 224/1.164, mintOpen; verifikasi on-chain run ini: totalSupply 240, MAX 1164, mintOpen 1, balanceOf(user)=0; registry-bytes TRUE (bytecode mengandung 0x60B926...022F); sim Boltbook: mint(1) value 0 lolos dari wallet Agent ID, revert tanpa Agent ID; price() 0,00005 BNB (paid tier), MAX_PER_WALLET 10. Free% UNVERIFIED (tanpa free view; total 240/1164=20,6% adalah % total, BUKAN % kuota gratis); umur UNVERIFIED (tanpa mintStart; first-seen run ini); website UNVERIFIED (post: no site found; contractURI() None; name-search tanpa situs). Owner 0x08df... sama dengan Tiling Hammock + Hexel Pantry (seri NP01/NP02/NP03), bukan di same-owner-discards. Sourcify per-contract via browser task masih pending saat merge (bentuk agent sudah via registry-bytes).",
 "runNote0131_1111":"Run 0131: EARLY LEAD BARU (lihat baselineNote)."}
C["Tiling Hammock"]={
 "address":"0x5f872b5c147a5ebe79b63a06f79b920e51648e31","name":"Tiling Hammock","symbol":"NP02","kind":"ERC721",
 "status":"early-lead-reported-2026-11-11","totalSupply":237,"MAX_SUPPLY":1043,"mintOpen":1,"balanceOf_user":0,
 "owner":"0x08df7970bb2c632908e3df036d0439420d9ce858","registryBytes":True,
 "firstSeenBlock":132829733,"firstSeenWib":"2026-11-11 ~01:20 WIB",
 "website":None,
 "baselineNote":"EARLY LEAD BARU run 0131 (dilaporkan sekali; TIDAK di-preview/TIDAK di-mint). Boltbook EN post ~01:20 WIB (blok 132829733): 227/1.043, mintOpen; verifikasi on-chain run ini: totalSupply 237, MAX 1043, mintOpen 1, balanceOf(user)=0; registry-bytes TRUE; sim Boltbook mint(1) value 0 lolos (Agent ID). Free% UNVERIFIED (tanpa free view; total 237/1043=22,7% adalah % total); umur UNVERIFIED (tanpa mintStart); website UNVERIFIED (post: no site found; contractURI() None; name-search tanpa situs). Owner sama NP trio 0x08df..., bukan di discards.",
 "runNote0131_1111":"Run 0131: EARLY LEAD BARU (lihat baselineNote)."}
C["Hexel Pantry"]={
 "address":"0x4a8e51016829632ae15f574a837c17c5bf1bc50b","name":"Hexel Pantry","symbol":"NP03","kind":"ERC721",
 "status":"early-lead-reported-2026-11-11","totalSupply":250,"MAX_SUPPLY":1213,"mintOpen":1,"balanceOf_user":0,
 "owner":"0x08df7970bb2c632908e3df036d0439420d9ce858","registryBytes":True,
 "firstSeenBlock":132829733,"firstSeenWib":"2026-11-11 ~01:20 WIB",
 "website":None,
 "baselineNote":"EARLY LEAD BARU run 0131 (dilaporkan sekali; TIDAK di-preview/TIDAK di-mint). Boltbook EN post ~01:20 WIB (blok 132829733): 238/1.213, mintOpen; verifikasi on-chain run ini: totalSupply 250, MAX 1213, mintOpen 1, balanceOf(user)=0; registry-bytes TRUE; sim Boltbook mint(1) value 0 lolos (Agent ID). Free% UNVERIFIED (tanpa free view; total 250/1213=20,6% adalah % total); umur UNVERIFIED (tanpa mintStart); website UNVERIFIED (post: no site found; contractURI() None; name-search tanpa situs). Owner sama NP trio 0x08df..., bukan di discards.",
 "runNote0131_1111":"Run 0131: EARLY LEAD BARU (lihat baselineNote)."}
C["GangDotFun"]={
 "address":"0x64af2a4aa164aefec5c09c405ad894065d34633f","name":"GangDotFun","symbol":"GANG","kind":"ERC721",
 "status":"watchlist-only-first-read-2026-11-11","totalMinted":255,"freeMinted":255,"MAX_SUPPLY":1000,"paidMinted":0,"balanceOf_user":0,
 "owner":"0x807d91e505d1ccb5c32f3b7ee66c6d9f3706e9ec","registryBytes":True,
 "firstSeenWib":"2026-11-11 ~01:31 WIB","website":None,
 "baselineNote":"WATCHLIST-ONLY first-read run 0131 (BUKAN early lead: first mint tidak terverifikasi - 255 mint sudah ada saat pertama dibaca; BUKAN strong lead: umur UNVERIFIED). Boltbook EN post (blok 132824318): totalMinted 219/1000, 500 free (1/wallet) + 500 paid 0,0015 BNB, owner dapat withdraw kapan saja; verifikasi on-chain run ini: totalMinted 255, freeMinted 255, paidMinted 0, MAX 1000, REGISTRY() persis 0x60B926...022F, registry-bytes TRUE, balanceOf(user)=0. Free% INFERENSI (bukan terverifikasi): 255/500 = 51% per aturan post - bukan kaki % terverifikasi (tanpa FREE_SUPPLY view). Umur UNVERIFIED (tanpa mintStart). Website UNVERIFIED (contractURI() None; name-search tanpa situs proyek; gang.fun adalah launchpad lain, bukan situs proyek ini). Owner 0x807d... bukan di discards. Baseline velocity dicatat run ini; promosi hanya bila umur terverifikasi <24 jam + % terverifikasi.",
 "runNote0131_1111":"Run 0131: first-read watchlist-only (lihat baselineNote)."}
C["Agentic Gangster"]={
 "address":"0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3","name":"Agentic Gangster","symbol":None,"kind":"ERC721",
 "status":"checked-free-pool-exhausted-2026-11-11","totalSupply":123,"freeMinted":111,"FREE_SUPPLY":111,"MAX_SUPPLY":1111,"balanceOf_user":0,
 "registryBytes":True,
 "baselineNote":"Ditemukan via search-index run 0131 (thecolony.uk, publish 2026-11-09 21:13 UTC): 111 free pass, 19/1111 saat publish. Verifikasi on-chain run ini: totalSupply 123, freeMinted 111/111 FREE_SUPPLY = FREE POOL HABIS, MAX 1111, balanceOf(user)=0, registry-bytes TRUE. BUKAN lead (free pool habis); tidak dilaporkan sebagai lead. Catatan: freeMint butuh voucher challenge EIP-712 via server (32 fragmen) - bukan plain contract mint.",
 "runNote0131_1111":"Run 0131: free pool habis (111/111), bukan lead."}
s["last_run_wib"]="2026-11-11 01:31 WIB"
s["runNote0131_1111"]="Run 0131: 3 EARLY LEAD BARU (Pico Alcazar, Tiling Hammock, Hexel Pantry - seri NP, owner sama 0x08df...); 0 kandidat, 0 strong lead baru; GangDotFun watchlist-only first-read; Agentic Gangster free pool habis; Dragon Agent DITAHAN (launch unverified, preseden 10 Nov) bukan age-excluded; NIGHTFORGE tetap gate-blocked; scan FAST-FAIL Ankr 401; binanceai launched()=0."
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("MERGED contracts:", len(s["contracts"]))
