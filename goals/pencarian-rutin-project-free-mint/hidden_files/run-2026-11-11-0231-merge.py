#!/usr/bin/env python3
"""Run 0231 merge: priority re-reads + MOODENG watchlist-only + WOJAK sold-out. No executions."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0231-premerge")
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=s["contracts"]; TC=s.get("track_c", {})
BLOCK=132833109
def upd(name, note, **kw):
    e=C.setdefault(name, {})
    e.update(kw)
    e["runNote0231_1111"]=note
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-11 02:31 WIB"
upd("REWINDCLUB","Run 0231 (blok 132833109): totalSupply 398->406 (+8, ~0,27/mnt vs prev ~0,60/mnt = 0,44x DAN <20 token) velocity GAGAL; agentFreeUsed 406/2000 = 20,3% (<25%); slot terbuka; mintStart 2026-11-10 21:49 WIB (umur ~4,7 jam, TERVERIFIKASI <24 jam; deadline ~21:49 WIB 11 Nov); tetap EARLY, tanpa promosi.",
    totalSupply=406, agentFreeUsed=406, balanceOf_user=0, agentFreeByWallet_user=0)
upd("LCDSPRITE","Run 0231 (blok 132833109): totalSupply 443->457 (+14, ~0,47/mnt vs prev ~0,63/mnt = 0,74x DAN <20) velocity GAGAL; agentFreeUsed 457/2000 = 22,85% (<25%); slot terbuka; mintStart 2026-11-10 21:52 WIB (umur ~4,65 jam, TERVERIFIKASI <24 jam; deadline ~21:52 WIB 11 Nov); tetap EARLY, tanpa promosi.",
    totalSupply=457, agentFreeUsed=457, balanceOf_user=0, agentFreeByWallet_user=0)
upd("RIMEVAULT","Run 0231 (blok 132833109): totalSupply 454->474 (+20, ~0,67/mnt vs prev ~0,90/mnt = 0,74x <1,5x) velocity GAGAL walau >=20 token - rate TURUN; agentFreeUsed 474/2000 = 23,7% (<25%) - tetap EARLY, TANPA promosi (butuh 26 mint lagi ke 500/2000); slot terbuka; mintStart 2026-11-10 21:27 WIB (umur ~5,1 jam, TERVERIFIKASI <24 jam; deadline ~21:27 WIB 11 Nov).",
    totalSupply=474, agentFreeUsed=474, balanceOf_user=0, agentFreeByWallet_user=0)
upd("MYCELIX","Run 0231 (blok 132833109): totalSupply 466->473 (+7, <20) velocity GAGAL; agentFreeUsed 473/2000 = 23,65% (<25%); slot terbuka; mintStart 2026-11-10 21:47 WIB (umur ~4,7 jam, TERVERIFIKASI <24 jam; deadline ~21:47 WIB 11 Nov); tetap EARLY, tanpa promosi.",
    totalSupply=473, agentFreeUsed=473, balanceOf_user=0, agentFreeByWallet_user=0)
upd("NIGHTFORGE","Run 0231 (blok 132833109): totalSupply 687->692 (+5); agentFreeUsed 689/2000 = 34,45% (tetap >=25% strong-leg %); slot terbuka (agentFreeByWallet 0, balanceOf 0); gate TETAP BLOCKED per recheck run 0201 (H+I+J+G, situs tidak mencetak kontrak) - tidak di-recheck ulang run ini; TIDAK di-mint; deadline umur 2026-11-11 14:37 WIB.",
    totalSupply=692, agentFreeUsed=689, balanceOf_user=0, agentFreeByWallet_user=0)
upd("SOLDERCATS","Run 0231 (blok 132833109): totalSupply 443->447 (+4, <20) velocity GAGAL; agentFreeUsed 447/2000 = 22,35% (<25%); slot terbuka; gate website PASSED (metode H); mintStart 2026-11-10 21:35 WIB (umur ~4,9 jam, TERVERIFIKASI <24 jam; deadline ~21:35 WIB 11 Nov); tetap EARLY, tanpa promosi.",
    totalSupply=447, agentFreeUsed=447, balanceOf_user=0, agentFreeByWallet_user=0)
upd("Pico Alcazar","Run 0231 (blok 132833109): totalSupply 253->263 (+10, interval velocity ke-2); mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=263, balanceOf_user=0)
upd("Tiling Hammock","Run 0231 (blok 132833109): totalSupply 253->256 (+3, interval velocity ke-2); mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=256, balanceOf_user=0)
upd("Hexel Pantry","Run 0231 (blok 132833109): totalSupply 265->267 (+2, interval velocity ke-2); mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=267, balanceOf_user=0)
upd("STALL","Run 0231 (blok 132833109): totalSupply 1620->1630 (+10, <20) velocity GAGAL; mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=1630, balanceOf_user=0)
upd("Arcane Stones","Run 0231 (blok 132833109): totalSupply 647->648 (+1, <20) velocity GAGAL; balanceOf(user)=0; website terverifikasi; umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=648, balanceOf_user=0)
upd("Cosmic Sentinel","Run 0231 (blok 132833109): totalSupply 383->388, freeMinted 378->383/225.000 = 0,17%; balanceOf(user)=0; tetap watchlist-only.",
    totalSupply=388, freeMinted=383, balanceOf_user=0)
upd("Dragon Agent","Run 0231 (blok 132833109): totalSupply 904 (tetap); balanceOf(user)=0, slot terbuka; free% + umur TETAP UNVERIFIED - DITAHAN preseden run 2026-11-10 (launch unverified), BUKAN age-excluded; tetap watchlist-only, tanpa promosi.",
    totalSupply=904, balanceOf_user=0)
upd("GangDotFun","Run 0231 (blok 132833109): totalMinted 303->330 (+27, interval velocity ke-2); freeMinted 330, paidMinted 0, MAX 1000; balanceOf(user)=0; free% INFERENSI 330/500 = 66% (BUKAN terverifikasi, tanpa FREE_SUPPLY view); umur + website UNVERIFIED; tetap watchlist-only first-read, tanpa promosi.",
    totalMinted=330, freeMinted=330, balanceOf_user=0)
upd("Kitebots","Run 0231 (blok 132833109): totalSupply 983 (tetap), freeMinted 983/4.000 = 24,6% (inferensi vs MAX; FREE_SUPPLY view tetap None); paidMinted 0; balanceOf(user)=0; velocity GAGAL (+0); umur TETAP UNVERIFIED; tetap watchlist-only-age-unverified.",
    totalSupply=983, freeMinted=983, balanceOf_user=0)
upd("ORBITJANITOR","Run 0231: totalSupply 630->635 (+5); balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.",
    totalSupply=635, balanceOf_user=1)
upd("EMBERANVIL","Run 0231: totalSupply 1029 (tetap); balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.",
    totalSupply=1029, balanceOf_user=1)
upd("BYTEBLOOM","Run 0231: totalSupply 569->572 (+3); balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.",
    totalSupply=572, balanceOf_user=1)
# Track C updates
def updtc(name, note, **kw):
    e=TC.setdefault(name, {})
    e.update(kw)
    e["runNote0231_1111"]=note
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-11 02:31 WIB"
updtc("11-11","Run 0231: freeMinted 579->583 (+4); post Boltbook independen 3 mnt lalu: free benar (gas only, 160.000/share), jendela tutup 17 Nov (bukan 11 Nov), paid 0 share; tetap tracked, tanpa perubahan status.",
    freeMinted=583)
for n in ["NIUBI","DROID","FUGUI-set1-991","FUGUI-set2","960E-sale"]:
    if n in TC:
        TC[n]["lastReadBlock"]=BLOCK; TC[n]["lastReadWib"]="2026-11-11 02:31 WIB"
        TC[n]["runNote0231_1111"]=f"Run 0231: freeMinted tetap ({TC[n].get('freeMinted')}); tanpa perubahan."
# MOODENG — watchlist-only (agent-shape + website unverified), NEVER lead/preview/mint
TC["MOODENG"]={
 "sale":"0xbb45668788a08ceceea6b1a0d0f25c1b667e1668",
 "token":"0x20ad4f682c828db41006ad5742a056abe9d4b1bc",
 "status":"watchlist-only-agent-shape-unverified-2026-11-11",
 "saleShape":"UNVERIFIED: freeMinted()/FREE_SHARES()/TOKENS_PER_SHARE()/PRICE_PER_SHARE()/startTime()/deadline()/ESCROW_BPS()/REFERRAL_BPS() terbaca, TAPI agentId()/agentRegistry()/registry()/quote()/freeClaimed()/freeAvailable() semua revert + selector-nya absen dari bytecode + registry-bytes 0x60B926...022F absen dari code + storage slot 0-11 tanpa alamat registry + Sourcify v2 404 (unverified). TIDAK ada bukti konkret Agent ID gate - BUKAN track-C lead.",
 "freeMinted":338, "FREE_SHARES":500, "TOTAL_SHARES":10000, "TOKENS_PER_SHARE":25000000,
 "PRICE_PER_SHARE":3000000000000000, "ESCROW_BPS":7000, "REFERRAL_BPS":500,
 "startTime":1794337200, "startTimeWib":"2026-11-11T02:00:00+07:00",
 "deadline":1794510000, "deadlineWib":"2026-11-13T02:00:00+07:00",
 "ageNote":"VERIFIED <24 jam: startTime() 02:00 WIB 11 Nov + first-mint block 132828998 ts 02:03:23 WIB + post Boltbook musegod.ai (sale dibuka 02:00 WIB, freeMinted 160/500 pasca-mintnya 02:04 WIB); deadline umur 02:00 WIB 12 Nov.",
 "userSlot":{"mintedBy":0,"note":"mintedBy(user)=0 (belum mint); freeClaimed(user) revert - slot tidak terverifikasi penuh."},
 "gate":"website UNVERIFIED: post Boltbook tanpa link situs/kontrak; pencarian alamat kontrak hanya mengembalikan MOODENG Solana generik (same-name noise, BUKAN linkage).",
 "source":"Boltbook post musegod.ai /p/Acrm6DZ9bf7k (02:29 WIB) + tx receipt 0xaa4cc7250158fd01f61867d73a4351769993c5310f28c2c49b45d5032365bbd0 -> sale; mint fn mint(uint256,address), value 0.",
 "boundary":"WATCHLIST ONLY. Bukan lead, TIDAK PERNAH di-preview/di-mint. Promosi ke lead hanya bila agent-shape terverifikasi (registry/AgentGate konkret) + website terverifikasi + pool/slot masih terbuka.",
 "totalMinted":339, "lastReadBlock":BLOCK, "lastReadWib":"2026-11-11 02:31 WIB",
 "runNote0231_1111":"Run 0231: temuan baru via Boltbook (bukan lead) - freeMinted 338/500 (162 tersisa, laju cepat: 160->338 dalam ~31 mnt); umur TERVERIFIKASI <24 jam; agent-shape + website UNVERIFIED -> watchlist-only.",
}
# WOJAK — sold out, excluded
TC["WOJAK"]={
 "sale":"0x70ab28d6d1569d35b6dcb58d0b2da0363303c9f5",
 "status":"excluded-sold-out-2026-11-11",
 "freeMinted":500, "FREE_SUPPLY":6250000000000000000000000000,
 "deadline":1794592800,
 "source":"Boltbook post musegod.ai /p/It_mWeCAtFiP (WOJAK 01:03 WIB, freeMinted 121/500) + tx receipt 0x901af1168ec5521c1c54ad6714ca50c317d99c3ffa78d169becdeed15adf3b03 -> sale; probe run 0231: freeMinted 500/500.",
 "note":"Free pool HABIS (500/500) - sold out; dicatat excluded, BUKAN lead, tidak dilaporkan sebagai lead.",
 "lastReadBlock":BLOCK, "lastReadWib":"2026-11-11 02:31 WIB",
 "runNote0231_1111":"Run 0231: freeMinted 121->500 (sold out dalam ~90 mnt); excluded-sold-out, bukan lead.",
}
s["last_run_wib"]="2026-11-11 02:31 WIB"
s["last_run_block"]=BLOCK
s["runNote0231_1111"]="Run 0231: TIDAK ADA kandidat/strong lead/early lead/track-C lead baru. MOODENG (sale 0xbb45...) temuan baru via Boltbook tapi watchlist-only (agent-shape + website unverified); WOJAK sold out 500/500 (excluded). RIMEVAULT +20 tapi velocity GAGAL (rate turun 0,74x) + 23,7% <25%. NIGHTFORGE 34,45% tetap gate-blocked. Scan Ankr FAST-FAIL (401). Binanceai launched=0 (tetap)."
s["runNote0231_1111_scan"]="Run 0231 scan: PRE-FLIGHT Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized dalam 28,9 dtk (head 132833065; kuota Ankr 0% s.d. 1 Des 2026). Scan leg FAST-FAIL. Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~320.500 blok dan tumbuh)."
s["runNote0231_1111_binanceai"]="Run 0231 track-B: binanceai.fun launched()=0, tokenClaimed(user)=0, token balanceOf(user)=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong."
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("MERGE DONE; contracts:", len(C), "track_c:", len(TC))
