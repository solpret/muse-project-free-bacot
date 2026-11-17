import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s=json.load(open(BASE+"onchain-snapshot.json"))
C=s["contracts"]
BLOCK=133190981
NOW="2026-11-12 23:24 WIB"
def upd(name, **kw):
    if name in C:
        C[name].update(kw)
    else:
        print("MISSING in snapshot:", name)
# SolNFT: PROMOSI early -> strong lead (71.2% > 70%), gate GAGAL (cek ulang run ini)
upd("SolNFT", status="strong-lead-gate-blocked-2026-11-12", totalMinted=237, freeMinted=237,
    freePctVerified=71.2, lastReadBlock=BLOCK, lastReadWib=NOW,
    runNote2301="Run 2301 (blok 133190981): freeMinted 192->237 (+45, ~1,8/mnt vs prior 3,56/mnt = 0,51x) velocity GAGAL; free 237/333 = 71,2% (>70%) + umur terverifikasi (mintOpensAt 21:31:58 WIB) + slot terbuka (freeClaimed(user)=0, balanceOf(user)=0) -> PROMOSI early->STRONG LEAD. GATE website GAGAL cek ulang run ini (A: pencarian alamat kontrak 0 hit proyek; G: pencarian nama SolNFT 0 hit proyek; B: tidak ada di front page Boltbook EN/ZH run ini; I: contractURI() null, tokenURI(1)='1' tanpa URL; C run 2131 tanpa URL) -> DILAPORKAN SEKALI sbg strong lead gate-blocked; TIDAK preview/mint. X UNVERIFIED.")
# AgcNFT: tetap strong-lead-gate-blocked, 85.0%
upd("AgcNFT", totalMinted=283, freeMinted=283, freePctVerified=85.0, lastReadBlock=BLOCK, lastReadWib=NOW,
    runNote2301="Run 2301 (blok 133190981): freeMinted 246->283 (+37, ~1,5/mnt vs prior 3,72/mnt = 0,40x) velocity GAGAL; free 283/333 = 85,0%; slot tetap terbuka (freeClaimed(user)=0, balanceOf(user)=0); gate-blocked sudah dilaporkan run 2231 -> TANPA laporan ulang, TANPA preview/mint.")
# Steady 0x4919-S1: early watchlist, 50.3%
upd("Steady", totalSupply=279, freeClaimed=279, freePctVerified=50.3, lastReadBlock=BLOCK, lastReadWib=NOW,
    runNote2301="Run 2301 (blok 133190981): totalSupply/freeClaimed 181->279 (+98, ~3,9/mnt vs prior ~4,0/mnt = 0,98x) velocity GAGAL; free 279/555 = 50,3% (lewat 50% tapi <70%); umur+website+X tetap UNVERIFIED; slot terbuka -> tetap early-lead watchlist, TANPA promosi, TANPA laporan ulang.")
upd("0x4919-S1", totalSupply=279, freeClaimed=279, lastReadBlock=BLOCK, lastReadWib=NOW) if "0x4919-S1" in C else None
# MECHA
if "MECHA" in C:
    upd("MECHA", totalMinted=1857, freeClaimed=1856, lastReadBlock=BLOCK, lastReadWib=NOW,
        runNote2301="Run 2301: totalMinted 1853->1857 (+4, <20) velocity GAGAL; freeClaimed 1856/4444 = 41,8%; umur+gate UNVERIFIED -> tetap watchlist-only EARLY.")
# OBFG
if "OBFG" in C:
    upd("OBFG", totalMinted=441, freeMinted=441, lastReadBlock=BLOCK, lastReadWib=NOW,
        runNote2301="Run 2301 (blok 133190981): totalMinted/freeMinted 412->441 (+29); free 441/1230 = 35,9% (<70%); saleStart 20:01:16 WIB; slot terbuka (freeAvailable(user)=1) -> tetap gate-blocked lead (dilaporkan 20:18 WIB), TANPA laporan ulang, TANPA preview/mint.")
# BinanceLife: KOREKSI deadline + flag run berikut
if "BinanceLife" in C:
    upd("BinanceLife", totalMinted=18, freeMinted=18, lastReadBlock=BLOCK, lastReadWib=NOW,
        runNote2301="Run 2301: totalMinted/freeMinted tetap 18/10000; mintStart 1794414145 = 2026-11-11 23:22:25 WIB (KOREKSI run 2231 yang menulis 23:29:05 WIB - salah 6m40d); deadline 24 jam = 2026-11-12 23:22:25 WIB. Bacaan run ini diambil SEBELUM deadline (umur ~23h53m, <24 jam) -> BELUM age-excluded run ini; run 23:31 WAJIB age-exclude bila masih 18/10000 + belum sold out.")
# binanceai pending
if "binanceai-mint" in C:
    upd("binanceai-mint", lastReadBlock=BLOCK, lastReadWib=NOW,
        runNote2301="Run 2301: launched() tetap 0, freeSharesRemaining 0, FREE_SHARES 2888 - klaim BELUM dibuka (fase refund); pending_claims tetap kosong.")
# RigForge
if "RigForge" in C:
    upd("RigForge", freeClaimed=338, lastReadBlock=BLOCK, lastReadWib=NOW,
        runNote2301="Run 2301: freeClaimed 338, freeSharesLeft 662, openedAt 0 - BELUM dibuka; bukan lead.")
# Others read fresh (no change / sold out)
for name, kw in [
 ("WFPASS", dict(totalMinted=502, freeMinted=500)),
 ("SEVEN", dict(totalMinted=1111, freeMinted=1111)),
 ("AGCR", dict(totalMinted=2454, freeMinted=2400)),
 ("SUDOSAINTS", dict(totalSupply=723, freeMinted=723)),
 ("Pickgrid", dict(totalSupply=218, freeMinted=216)),
 ("LuckyCatch", dict(totalMinted=21)),
 ("Kongtou-AirdropCnNFT", dict(totalMinted=112, freeMinted=111)),
 ("0x7Eb9", dict(totalMinted=1196)),
 ("NAOMI", dict(totalMinted=783, freeMinted=777)),
 ("AgenticGangster", dict(totalSupply=124, freeMinted=111)),
 ("AIRDROP", dict(totalMinted=77, freeMinted=77)),
 ("Kitebots", dict(totalSupply=1259, freeMinted=1259)),
 ("Dragon Agent", dict(totalSupply=961)),
]:
    if name in C:
        C[name].update(kw); C[name]["lastReadBlock"]=BLOCK; C[name]["lastReadWib"]=NOW
# Batch-fail targets: nilai lama dipertahankan, catat
for name in ["OLIVER AGENTS","Cobalt Agent","DACIT","SYNERGYPASS","DRAGON-0xad0d","AGENT COSMOS","AGENT ID card","RunicKey","Thor","Vexa","ROBO"]:
    if name in C:
        C[name]["runNote2301"]="Run 2301: BATCH-FAIL (degradasi eth_call) - nilai lama dipertahankan, BUKAN nol; bukan kandidat."
# NOTV-0415 + fa22
if "NOTV-0415" in C:
    upd("NOTV-0415", totalMinted=0, totalSupply=0, lastReadBlock=BLOCK, lastReadWib=NOW,
        runNote2301="Run 2301: totalMinted 0 - BELUM dibuka; watchlist-only di track_c, bukan lead.")
# Home (NEW-fd55) - EARLY LEAD BARU
C["Home"]={
 "address":"0xfd55F5b70F6eb6E59CEb6FF5c449f0cd1A3a5C0F",
 "status":"early-lead-reported-2026-11-12",
 "name":"Home","symbol":"HOME","kind":"ERC721",
 "totalMinted":62,"freeMinted":62,"FREE_CAP":111,"MAX_SUPPLY":1111,
 "freePctVerified":55.9,"mintOpen":1,"mintOpensAt":1794498886,"priceWei":10000000000000000,
 "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot TERBUKA: freeClaimed(user)=0, mintsBy(user)=0, balanceOf(user)=0.",
 "firstSeenBlock":133190981,"firstSeenWib":"2026-11-12 23:24 WIB",
 "sourcifyVerifiedAt":"2026-11-12T15:55:11Z",
 "agentIdRegistry":"0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "lastReadBlock":BLOCK,"lastReadWib":NOW,
 "xVerified":False,"velocityVerified":False,
 "launchNote":"Umur TERVERIFIKASI <24 jam: mintOpensAt on-chain 1794498886 = 2026-11-12 22:54:46 WIB (umur ~30 mnt saat bacaan). First-mint log timestamp TIDAK tersedia (Ankr 401, outage sejak 9 Nov).",
 "baselineNote":"EARLY lead dilaporkan sekali run 2301 (temuan feed Sourcify recently-verified; pertama terlihat job ini run ini - tidak ada di snapshot/track_c). Agent-shaped: agentIdRegistry()=registry resmi, holdsAgentId(), mint+price+freeClaimed/freeMinted, FREE_CAP 111. Free 62/111 = 55,9% (<70% strong lead). X UNVERIFIED, website UNVERIFIED (tanpa contractURI di ABI; tokenURI(1)='1' tanpa URL; pencarian alamat kontrak metode A 0 hit proyek). TIDAK PERNAH preview/mint sbg early lead.",
 "gateNote":"Website UNVERIFIED (metode A 0 hit; tokenURI(1)='1' tanpa URL; tanpa contractURI di ABI). Early lead TIDAK butuh gate; gate wajib dicek sebelum promosi/mint.",
 "supplyView":"totalMinted",
 "runNote2301":"Run 2301 (blok 133190981): bacaan pertama - totalMinted/freeMinted 62, FREE_CAP 111, MAX_SUPPLY 1111, mintOpen 1, slot terbuka, harga berbayar 0,01 BNB. EARLY lead, dilaporkan sekali; masuk snapshot watchlist."
}
s["last_run_wib"]="2026-11-12 23:01 WIB"
s["last_run_note"]="Run 2301: 2 laporan sekali (SolNFT promosi early->strong lead gate-blocked 71,2%; Home EARLY lead baru 55,9%). Pre-flight FAIL Ankr 401 (scan fast-fail, watermark tetap 132512564). BinanceLife deadline terkoreksi 23:22:25 WIB - age-exclusion jatuh ke run 23:31."
json.dump(s, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(C))
# scan state note
st=json.load(open(BASE+"onchain-scan-state.json"))
st["note_2301_scan"]="Run 2301: PRE-FLIGHT FAIL (HTTP 401 Ankr; kelanjutan outage Ankr sejak 9 Nov) - scan leg FAST-FAIL, watermark TIDAK dimajukan (tetap 132512564). 5c dilewati (tanpa output scan). Sudah dilaporkan sekali 9 Nov - DIAM."
json.dump(st, open(BASE+"onchain-scan-state.json","w"), indent=1)
print("scan state noted; watermark:", st.get("last_scanned_block"))
