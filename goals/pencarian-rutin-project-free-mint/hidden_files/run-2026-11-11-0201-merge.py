#!/usr/bin/env python3
"""Run 0201 merge: update priority reads + WHALE NFT sold-out entry. No executions."""
import json, shutil, datetime
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0201-premerge")
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=s["contracts"]; TC=s.get("track_c", {})
BLOCK=132829343
def wib(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
print("mintStart WIB:", {k: wib(v) for k,v in {
 "REWINDCLUB":1794322145,"LCDSPRITE":1794322332,"RIMEVAULT":1794320879,"MYCELIX":1794322052,
 "SOLDERCATS":1794321310,"NIGHTFORGE":1794296194}.items()})
def upd(name, note, **kw):
    e=C.setdefault(name, {})
    e.update(kw)
    e["runNote0201_1111"]=note
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-11 02:01 WIB"
upd("REWINDCLUB","Run 0201 (blok 132829343): totalSupply 380->398 (+18, ~0,60/mnt vs prev ~0,13/mnt = 4,5x TAPI <20 token) velocity GAGAL; agentFreeUsed 398/2000 = 19,9% (<25%); slot terbuka (agentFreeByWallet 0, balanceOf 0); mintStart 1794322145 = 2026-11-10 21:49 WIB (umur ~4,2 jam, TERVERIFIKASI <24 jam; deadline ~21:49 WIB 11 Nov); website terverifikasi; tetap EARLY, tanpa promosi.",
    totalSupply=398, agentFreeUsed=398, balanceOf_user=0, agentFreeByWallet_user=0, mintStart=1794322145, startTimeWib="2026-11-10T21:49:05+07:00")
upd("LCDSPRITE","Run 0201 (blok 132829343): totalSupply 424->443 (+19, ~0,63/mnt vs prev ~0,10/mnt = 6,3x TAPI <20) velocity GAGAL; agentFreeUsed 443/2000 = 22,15% (<25%); slot terbuka; mintStart 1794322332 = 2026-11-10 21:52 WIB (umur ~4,1 jam, TERVERIFIKASI <24 jam; deadline ~21:52 WIB 11 Nov); website terverifikasi; tetap EARLY, tanpa promosi.",
    totalSupply=443, agentFreeUsed=443, balanceOf_user=0, agentFreeByWallet_user=0, mintStart=1794322332, startTimeWib="2026-11-10T21:52:12+07:00")
upd("RIMEVAULT","Run 0201 (blok 132829343): totalSupply 427->454 (+27, ~0,90/mnt vs prev ~0,37/mnt = 2,45x DAN >=20 token) velocity LOLOS; agentFreeUsed 454/2000 = 22,7% (<25%) - velocity lolos TAPI % belum 25% -> tetap EARLY, TANPA promosi (butuh 46 mint lagi ke 500/2000; pace saat ini ~+27/30 mnt); slot terbuka; mintStart 1794320879 = 2026-11-10 21:27 WIB (umur ~4,6 jam, TERVERIFIKASI <24 jam; deadline ~21:27 WIB 11 Nov); website terverifikasi.",
    totalSupply=454, agentFreeUsed=454, balanceOf_user=0, agentFreeByWallet_user=0, mintStart=1794320879, startTimeWib="2026-11-10T21:27:59+07:00")
upd("MYCELIX","Run 0201 (blok 132829343): totalSupply 452->466 (+14, ~0,47/mnt vs prev ~0,07/mnt = 7,0x TAPI <20) velocity GAGAL; agentFreeUsed 466/2000 = 23,3% (<25%); slot terbuka; mintStart 1794322052 = 2026-11-10 21:47 WIB (umur ~4,2 jam, TERVERIFIKASI <24 jam; deadline ~21:47 WIB 11 Nov); website terverifikasi; tetap EARLY, tanpa promosi.",
    totalSupply=466, agentFreeUsed=466, balanceOf_user=0, agentFreeByWallet_user=0, mintStart=1794322052, startTimeWib="2026-11-10T21:47:32+07:00")
upd("NIGHTFORGE","Run 0201 (blok 132829343): totalSupply 685->687 (+2); agentFreeUsed 684/2000 = 34,2% (tetap >=25% strong-leg %); slot terbuka (agentFreeByWallet 0, balanceOf 0); gate dicek ulang run ini (H+I+J+G): contractURI() -> https://nightforge.pages.dev/meta/c... + tokenURI(1) -> https://nightforge.pages.dev/meta/3... (keduanya menunjuk situs yang sama); site re-fetch 23.857 byte, 0 kecocokan kontrak, tetap infografis medis -> gate TETAP GAGAL, TIDAK di-mint; deadline umur 2026-11-11 14:37 WIB.",
    totalSupply=687, agentFreeUsed=684, balanceOf_user=0, agentFreeByWallet_user=0)
upd("SOLDERCATS","Run 0201 (blok 132829343): totalSupply 435->443 (+8, <20) velocity GAGAL; agentFreeUsed 443/2000 = 22,15% (<25%); slot terbuka; gate website PASSED (metode H); mintStart 1794321310 = 2026-11-10 21:35 WIB (umur ~4,4 jam, TERVERIFIKASI <24 jam; deadline ~21:35 WIB 11 Nov); tetap EARLY, tanpa promosi.",
    totalSupply=443, agentFreeUsed=443, balanceOf_user=0, agentFreeByWallet_user=0, mintStart=1794321310, startTimeWib="2026-11-10T21:35:10+07:00")
upd("Pico Alcazar","Run 0201 (blok 132829343): totalSupply 240->253 (+13, interval velocity pertama - baseline dicatat run ini); mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=253, balanceOf_user=0)
upd("Tiling Hammock","Run 0201 (blok 132829343): totalSupply 237->253 (+16, interval velocity pertama - baseline dicatat run ini); mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=253, balanceOf_user=0)
upd("Hexel Pantry","Run 0201 (blok 132829343): totalSupply 250->265 (+15, interval velocity pertama - baseline dicatat run ini); mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=265, balanceOf_user=0)
upd("STALL","Run 0201 (blok 132829343): totalSupply 1601->1620 (+19, <20) velocity GAGAL; mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=1620, balanceOf_user=0)
upd("Arcane Stones","Run 0201 (blok 132829343): totalSupply 644->647 (+3, <20) velocity GAGAL; balanceOf(user)=0; website terverifikasi; umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=647, balanceOf_user=0)
upd("Cosmic Sentinel","Run 0201 (blok 132829343): totalSupply 383, freeMinted 376->378/225.000 = 0,17%; balanceOf(user)=0; tetap watchlist-only.",
    totalSupply=383, freeMinted=378, balanceOf_user=0)
upd("Dragon Agent","Run 0201 (blok 132829343): totalSupply 904 (tetap); canMint(user)=1, balanceOf(user)=0, slot terbuka; REGISTRY() persis; free% + umur TETAP UNVERIFIED - DITAHAN preseden run 2026-11-10 (launch unverified), BUKAN age-excluded; tetap watchlist-only, tanpa promosi.",
    totalSupply=904, balanceOf_user=0)
upd("GangDotFun","Run 0201 (blok 132829343): totalMinted 255->303 (+48, interval velocity pertama - baseline dicatat run ini); freeMinted 303, paidMinted 0, MAX 1000; balanceOf(user)=0; free% INFERENSI 303/500 = 60,6% (BUKAN terverifikasi, tanpa FREE_SUPPLY view); umur UNVERIFIED; website UNVERIFIED; tetap watchlist-only first-read, tanpa promosi.",
    totalMinted=303, freeMinted=303, balanceOf_user=0)
upd("ORBITJANITOR","Run 0201: totalSupply 618->630 (+12); balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.", totalSupply=630, balanceOf_user=1)
upd("EMBERANVIL","Run 0201: totalSupply 1025->1029 (+4); balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.", totalSupply=1029, balanceOf_user=1)
upd("BYTEBLOOM","Run 0201: totalSupply 566->569 (+3); balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.", totalSupply=569, balanceOf_user=1)
upd("Kitebots","Run 0201 (blok 132829343): totalSupply 983 (tetap vs 01:01), freeMinted 983/4000 = 24,6% (inferensi vs MAX; FREE_SUPPLY view tetap None; post Boltbook ZH recheck 02:06 konfirmasi 983/3.996); paidMinted 0; REGISTRY() persis 0x60B926...022F (registry-bytes FALSE - referensi via view, bukan bytecode); owner 0x4e9b1d076fda3605ad63f81a94a8693342a08dba (BUKAN di same-owner-discards, 12 owner / 60 kontrak); balanceOf(user)=0; velocity GAGAL (+0); umur TETAP UNVERIFIED; status tetap watchlist-only-age-unverified, tanpa promosi.",
    totalSupply=983, freeMinted=983, balanceOf_user=0)
# Hivebyte: no fresh eth_call this run; Boltbook recheck post 02:03 confirms 301 flat
e=C.setdefault("0xaE9d85E7", {})
e["runNote0201_1111"]="Run 0201: tanpa eth_call baru (post Boltbook ZH/EN recheck 02:03 oleh duyenvu75.ai konfirmasi 301/2.007 = 15,0%, +3/437 mnt, Sourcify UNVERIFIED - sama dengan lastRead 01:01 supply 301); pace sangat lambat; status tetap watchlist-only-mature-newly-noticed-2026-11-09, tanpa promosi."
# WHALE NFT contract A - sold out, found via Boltbook post (cyroo.ai, 4m ago)
C["WHALE NFT"]={
 "address":"0x8a3e3eea10e1fa7d6fa768550f8e572a15eb90d0","name":"WHALE NFT","symbol":"WHALE","kind":"ERC721",
 "status":"excluded-sold-out-2026-11-11","totalSupply":5000,"MAX_SUPPLY":5000,"balanceOf_user":0,
 "baselineNote":"Ditemukan via Boltbook EN post run 0201 (cyroo.ai, 'Free mint check: WHALE NFT', ~4 mnt lalu; Sourcify exact_match): free lane mint() value 0 (1/wallet), extra 0,007 BNB. Verifikasi via search-index run ini: totalSupply 5.000/5.000 (blok 132.055.360, 2026-11-07 ~03:10 WIB) = SOLD OUT - BUKAN lead, tidak dilaporkan sebagai lead. Perhatian: ada kontrak WHALE B 0xf81b542c41f982a7d7a8e2ee8cab5feee6203218 (koleksi terpisah, masih minting) - jangan tertukar.",
 "runNote0201_1111":"Run 0201: sold out 5000/5000 terkonfirmasi via search-index; dicatat excluded, bukan lead."}
# track_c re-read bookkeeping (20 items, blok 132829343)
TC_NOTES={
 "11-11":"Run 0201: freeMinted 578->579 (+1); tetap watchlist-only-age-website-unverified.",
 "NIUBI":"Run 0201: freeMinted 159 (tetap); tetap watchlist-only.",
 "DROID":"Run 0201: freeMinted 739 (tetap); tetap watchlist-only-not-open.",
 "FUGUI-set1-991":"Run 0201: freeMinted 423 (tetap); tetap watchlist-only-gate-blocked.",
 "FUGUI-set2":"Run 0201: freeMinted 626 (tetap); tetap watchlist-only-gate-blocked.",
 "960E-sale":"Run 0201: freeMinted 38 (tetap); tetap watchlist-only-age-website-unverified.",
 "YAMA PROJECT":"Run 0201: batch-fail lagi (run ke-9 berturut-turut); state dipertahankan, bukan perubahan.",
 "PESI":"Run 0201: batch None (tetap); tetap track-c-lead-gate-blocked.",
}
for k,v in TC.items():
    if not isinstance(v,dict): continue
    if k in ("PESI","CLEPSYDRA","MoonAgent-MOAGT","YAMA PROJECT","LOWB","11-11","BHTB","AgentGrid","VISION","FairMint Agent","Kiko9393","CHTCI","0x5f76cAb7-5a-hit","FUGUI-set1-991","FUGUI-set2","NIUBI","DROID","0x47529CF66091BeB0E8e0F78D5635e367473D52d5","BelieveBNB","BOME-50CD","960E-sale"):
        v["lastReadBlock"]=BLOCK
        v["lastReadWib"]="2026-11-11 02:01 WIB"
        if k in TC_NOTES: v["runNote0201_1111"]=TC_NOTES[k]
s["last_run_wib"]="2026-11-11 02:01 WIB"
s["runNote0201_1111"]="Run 0201 (2026-11-11 02:01 WIB, blok re-read 132829343): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat baru, 0 track-B claim. RIMEVAULT velocity LOLOS (+27, 2,45x) TAPI free% 22,7% <25% -> tetap early, tanpa promosi. NIGHTFORGE gate dicek ulang (H+I+J+G) tetap gagal (nightforge.pages.dev 23.857 byte, 0 kecocokan kontrak) - strong lead 34,2% TETAP gate-blocked, tidak di-mint; deadline umur 2026-11-11 14:37 WIB. Kitebots 983 (flat), 24,6% inferensi, umur unverified, tetap watchlist-only. Hivebyte 301 (flat, post recheck 02:03). EMBER (bangwi.ai, 528/5.555) TANPA alamat kontrak di post maupun author page -> tidak bisa diverifikasi on-chain, dicatat saja. WHALE NFT sold out 5000/5000 (dicatat excluded). Scan FAST-FAIL Ankr 401; binanceai launched()=0."
s["runNote0201_1111_scan"]="Run 0201 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized dalam 30,4 dtk (head 132829304; kuota Ankr 0% s.d. 1 Des 2026; outage sejak ~13:33 WIB 2026-11-09). Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~316.740 blok dan tumbuh). Route 5c: tanpa output scan baru (tidak ada ERC-20 backlog baru untuk di-shape-check run ini)."
s["runNote0201_1111_discovery"]="Run 0201 discovery: Sourcify feed 20 terbaru (verified 18:17:02-19:05:46Z), 3 baru vs hot-leg-seen (0x96a9B1AcED015A71F77Ea563e6A5B451A320a07a, 0xeA932AA6694425cC9a37878ae2659f231f1bf6c5, 0xD04A2B6d8Bbd001f7d7baE98db569a68846D35a3) - per-contract endpoint v2 404 (pola sama run 0131, BUKAN bukti unverified); probe on-chain: ketiganya TANPA registry-bytes, totalSupply ERC-20 (200 jt / 100 mld token), tanpa mintStart/mintOpen -> bukan agent-shaped, 0 sale-shape, 0 early lead. Boltbook EN 45.752 byte + ZH 46.018 byte (EN berhasil lagi setelah 11x 0-byte di hot leg), 9 alamat unik, 0 baru vs snapshot+hot-leg-seen (6 di snapshot: Wise Owl, GangDotFun, RIMEVAULT, BOLT, QAGENT-2 + Kitebots; 3 lainnya: WHALE NFT sold out, pair BOLT 0x0d2f..., artefak footer 0x8269...). Post baru: Hivebyte recheck 02:03 (301, flat), EMBER 528/5.555 TANPA kontrak (tidak terverifikasi), WHALE NFT free-mint check (sold out). Sweep EN+ZH: Agentic Gangster free habis; GHOST age-excluded; Subsonic Tribe excluded-sold-out; First-Dollar Grove age-excluded; AGENT COSMOS sudah di snapshot; AGENT MAO age-excluded; Pixel Fox/PocketDragons lama. Rute 6: Odaily 264.078 byte + PANews 119.657 byte, 0 keyword Agent ID/free mint/free share. Bridge: 116 kontrak, mtime 2026-11-08 18:21:53 WIB (STALE); tidak ada temuan pelengkap baru."
s["runNote0201_1111_binanceai"]="Run 0201 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, tokenClaimed(user)=0, token balanceOf(user)=0. Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang. pending_claims kosong."
s["runNote0201_1111_age_exclusions"]="Run 0201 age-exclusions (aturan <24 jam): window 01:31->02:01 WIB: 0 BARU. Deadline umur yang masih berjalan: NIGHTFORGE 2026-11-11 14:37 WIB; RIMEVAULT ~21:27 WIB, REWINDCLUB ~21:49 WIB, MYCELIX ~21:47 WIB, LCDSPRITE ~21:52 WIB, SOLDERCATS ~21:35 WIB (11 Nov). Dragon Agent TIDAK di-exclude (launch UNVERIFIED, preseden ditahan 10 Nov)."
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("MERGED contracts:", len(s["contracts"]), "track_c:", len(TC))
