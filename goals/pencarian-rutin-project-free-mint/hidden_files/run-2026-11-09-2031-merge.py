#!/usr/bin/env python3
"""Merge run 2031 reread + targeted + freecounter + grove + binanceai into onchain-snapshot.json.
INTERVAL 33.6 min (block 132589166 ~20:03 WIB -> 132593641 ~20:37 WIB). Read-only except snapshot.
Promotions decided this run (freeMinted = operative free counter; freeClaimed() reverts on these
factory contracts - see runNote2031_freecounter): TIME CARDS / Agentic / BAHUANG3 / Lenx -> strong lead;
MONEY free pool exhausted -> sold-out; AURISLE age-excluded >48h."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL=33.6; BLOCK=132593641; NOW_WIB="2026-11-09 20:37 WIB"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
rr=json.load(open(f"{BASE}/run-2026-11-09-2031-reread.json"))
tg=json.load(open(f"{BASE}/run-2026-11-09-2031-targeted.json"))
fc=json.load(open(f"{BASE}/run-2026-11-09-2031-freecounter.json"))
contracts=snap.setdefault("contracts",{}); track_c=snap.setdefault("track_c",{})
n_upd=0; vel_pass=[]
for name,v in contracts.items():
    r=rr.get("reread",{}).get(name)
    if not isinstance(r,dict): continue
    prev_ts=v.get("totalSupply"); new_ts=r.get("totalSupply")
    minted=None
    if isinstance(prev_ts,int) and isinstance(new_ts,int):
        minted=new_ts-prev_ts
        prev_rate=v.get("currentRatePerMin")
        rate=minted/INTERVAL
        ratio=(rate/prev_rate) if (isinstance(prev_rate,(int,float)) and prev_rate>0) else None
        v["previousTotalSupply"]=prev_ts; v["mintedInInterval"]=minted; v["intervalMinutes"]=INTERVAL
        v["currentRatePerMin"]=round(rate,4); v["previousRatePerMin"]=prev_rate
        v["velocityRatio"]=(round(ratio,2) if ratio is not None else None)
        v["velocityLegPasses"]=bool(ratio is not None and ratio>=1.5 and minted>=20)
        if v["velocityLegPasses"]: vel_pass.append((name,minted,round(ratio,2)))
    for k in ("totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"):
        if r.get(k) is not None: v[k]=r[k]
    fs=v.get("FREE_SUPPLY"); fcl=v.get("freeClaimed")
    if isinstance(fs,int) and fs and isinstance(fcl,int): v["freePctVerified"]=round(100.0*fcl/fs,2)
    v["lastReadBlock"]=BLOCK; v["lastReadWib"]=NOW_WIB
    v["runNote2031_1109"]=(f"Run 2031 (blok {BLOCK}, interval {INTERVAL} mnt vs run 2001): {prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')}; bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd+=1
n_tc=0
for name,v in track_c.items():
    r=rr.get("track_c",{}).get(name)
    if not isinstance(r,dict) or not isinstance(v,dict): continue
    if r.get("totalSupply") is not None: v["totalSupply"]=r["totalSupply"]
    if r.get("freeMinted") is not None: v["freeMinted"]=r["freeMinted"]
    if r.get("freeSharesRemaining") is not None: v["freeSharesRemaining"]=r["freeSharesRemaining"]
    if r.get("balanceOf_user") is not None: v["balanceOf_user"]=r["balanceOf_user"]
    n_tc+=1

# --- targeted overrides (blok 132594409) + freecounter ---
tc=contracts["TIME CARDS Genesis"]
tc["freeMinted"]=tg["TIME_CARDS"]["freeMinted"]; tc["totalSupply"]=tg["TIME_CARDS"]["totalSupply"]
tc["claimedFree_user"]=0; tc["freeStart"]=1794229740
tc["freePctVerified"]=round(100.0*1164/2000,2)
tc["status"]="strong-lead-2026-11-09"
tc["gate"]="NOT PASSED run 2031: no project website found - metode A (address search, 0 hit), B (Boltbook post quyennuong.ai 20:35 WIB, tanpa tautan situs), C (Sourcify stdJson fetch gagal 2x IncompleteRead; ABI tanpa URL), G (name search, hanya hasil 'time card' tak terkait), H (contractURI() null/revert), I (tokenURI(1) base64 on-chain JSON, TANPA external_url; tier COMMON), J (ABI 42 fns, tanpa fungsi site/URL). L/M/N belum dicoba run ini. Gate gagal = scope block eksekusi, BUKAN gagal safety."
tc["gateNote2031"]="Strong lead BARU run 2031 (promosi dari watchlist-only-upcoming): umur TERVERIFIKASI <=48 jam (freeStart on-chain 1794229740 = 2026-11-09 20:09 WIB; supply 0 @20:03 -> 1118 @132593641 -> 1164 @132594409 -> 1333 probe freecounter); free 1164/2000 = 58,2% (66,65% di probe 1333); slot TERBUKA (claimedFree(user)=0, balanceOf(user)=0, blok 132594409); velocity UNVERIFIED (interval pertama berisi minting, prev rate 0 - bukan pass); diskusi: post Boltbook quyennuong.ai 20:35 WIB (public web mention) + claimFree() lolos simulasi; X account UNVERIFIED; website UNVERIFIED -> GATE TIDAK LOLOS -> TIDAK preview/mint. Dilaporkan sekali sebagai strong lead + alasan gate."
tc["lastReadBlock"]=132594409; tc["lastReadWib"]="2026-11-09 20:44 WIB"

ag=contracts["Agentic"]
ag["freeMinted"]=tg["Agentic"]["freeMinted"]; ag["totalMinted"]=tg["Agentic"]["totalMinted"]
ag["hasFreeMinted_user"]=0; ag["freePctVerified"]=round(100.0*372/1000,2)
ag["status"]="strong-lead-gate-failed-2026-11-09"
ag["gateNote2031"]="PROMOSI early->strong lead run 2031: freeMinted 372/1000 = 37,2% (blok 132594409; freecounter 374 = 37,4%); freeClaimed() REVERT di semua baca (bukan counter) - nilai freeClaimed 189 di snapshot adalah freeMinted saat triase 1931 yang salah label + freePctVerified 18,9% sudah basi; umur TERVERIFIKASI <=48 jam (first-seen feed Sourcify 19:29 WIB hari ini); slot TERBUKA (hasFreeMinted(user)=0, balanceOf=0); owner 0x9e07... TIDAK ada di same-owner-discards.json (60 entri); velocity UNVERIFIED (totalSupply() revert, totalMinted-based); X UNVERIFIED; website GATE SUDAH GAGAL run 1931 (metode A-N) -> TIDAK preview/mint. Dilaporkan sekali sebagai promosi strong lead + alasan gate."

bh=contracts["BAHUANG3"]
bh["freeMinted"]=tg["BAHUANG3"]["freeMinted"]; bh["totalMinted"]=tg["BAHUANG3"]["totalMinted"]
bh["freeAllowance_user"]=2; bh["freePctVerified"]=round(100.0*2337/6000,2)
bh["status"]="strong-lead-gate-failed-2026-11-09"
bh["gateNote2031"]="PROMOSI early->strong lead run 2031: freeMinted 2337/6000 = 38,95% (blok 132594409); freeClaimed() REVERT - freePctVerified 24,65% di snapshot sudah basi (dari freeMinted awal ~1479); umur TERVERIFIKASI (mintStart on-chain 1794176990 = 2026-11-09 05:29:50 WIB, first mint 05:40:07); slot TERBUKA (freeAllowance(user)=2, balanceOf=0); owner() REVERT (tanpa owner); payout 0x45e2... TIDAK ada di same-owner-discards.json (60 entri); X UNVERIFIED; website GATE SUDAH GAGAL run 0531 + metode L -> TIDAK preview/mint. Dilaporkan sekali sebagai promosi strong lead + alasan gate."

lx=contracts["Lenx Agent Pass"]
lx["freeMinted"]=fc["Lenx"]["freeMinted()"]; lx["freeRemaining"]=fc["Lenx"]["freeRemaining()"]
lx["freePctVerified"]=round(100.0*792/1000,2)
lx["status"]="strong-lead-gate-unverified-2026-11-09"
lx["gateNote2031"]="PROMOSI early->strong lead run 2031: freeMinted 792/1000 = 79,2% (freecounter run 2031; reread 790 = 79,0% @132593641); freeRemaining 208 mengonfirmasi freeMinted sebagai counter operative (792+208=1000=FREE_CAP) - nilai freeClaimed 128 di snapshot adalah freeMinted saat triase 1201 yang salah label + freePctVerified 12,8% sudah basi; umur TERVERIFIKASI <=48 jam (first mint 2026-11-09 11:38:27 WIB); slot TERBUKA (freeClaimed(user)=0 reread, balanceOf=0); owner 0x9e3b... TIDAK ada di same-owner-discards.json (60 entri); X UNVERIFIED; website UNVERIFIED (metode H/C/G dicoba saat triase 1201, tanpa situs; gate lengkap A-N belum dijalankan) -> TIDAK preview/mint. Dilaporkan sekali sebagai promosi strong lead + alasan gate."

mo=contracts["MONEY"]
mo["freeMinted"]=222; mo["totalMinted"]=223
mo["freePctVerified"]=100.0
mo["status"]="sold-out-2026-11-09"
mo["gateNote2031"]="PERUBAHAN run 2031: free pool HABIS - freeMinted 222/222 = 100% (FREE_CAP 222; totalMinted 223 = 222 free + 1 paid). Early lead berakhir sold-out; dilaporkan sekali + dikeluarkan dari pantauan aktif (status sold-out). Website money-nft-mint.netlify.app sempat terverifikasi, tapi pool sudah habis - tidak ada eksekusi."

au=contracts["AURISLE"]
au["status"]="age-excluded-2026-11-09"
au["gateNote2031"]="PERUBAHAN run 2031: AGE-EXCLUDED - first mint TERVERIFIKASI on-chain 2026-11-07 20:24:21 WIB; umur ~48 jam 21 mnt >48 jam pada run ini; totalSupply 321/1111 belum sold out; free% UNVERIFIED (FREE_SUPPLY tak terbaca); slot UNVERIFIED. Dilaporkan sekali + dikeluarkan dari watchlist aktif (status age-excluded)."

g=contracts.get("Agent Grove")
if g:
    g["freeOpen"]=0; g["freeClaimed_user"]=0; g["lastReadBlock"]=132592990; g["lastReadWib"]="2026-11-09 20:31 WIB"
    g["runNote2031_1109"]="Run 2031 grove-check (blok 132592990): freeOpen=0, freeClaimed(user)=0 - masih belum buka; status watchlist-only-upcoming tetap."

snap["runNote2031"]="Run 2031 (2026-11-09 20:31-21:0x WIB): 4 PROMOSI STRONG LEAD (dilaporkan sekali, SEMUA gate-blocked -> TIDAK preview/mint): (1) TIME CARDS Genesis 0xc5624B61beE1971E6Aa3AB5f403236Ab32C2B6cd - BARU buka 20:09 WIB hari ini, free 1164/2000 = 58,2% (@132594409; probe 1333 = 66,65%), slot terbuka (claimedFree(user)=0), velocity unverified, diskusi post Boltbook 20:35 WIB, website UNVERIFIED (A/B/C/G/H/I/J dicoba, tanpa situs; L/M/N belum dicoba). (2) Agentic 0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5 - free 372/1000 = 37,2%, umur <=48 jam, slot terbuka, gate GAGAL run 1931 (A-N). (3) BAHUANG3 0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591 - free 2337/6000 = 38,95%, umur terverifikasi (mintStart 05:29:50 hari ini), slot terbuka (freeAllowance=2), gate GAGAL run 0531+L. (4) Lenx Agent Pass 0x6E252E3a3584BD6a64C103e4eDFa761f6335980F - free 792/1000 = 79,2%, umur terverifikasi (first mint 11:38:27 hari ini), slot terbuka, gate UNVERIFIED (H/C/G triase, tanpa situs). 2 PERUBAHAN (dilaporkan sekali): MONEY 0x085a493ac880188a69ad38449f505dA9E730C50B free pool HABIS 222/222 -> sold-out; AURISLE 0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D AGE-EXCLUDED (first mint terverifikasi 2026-11-07 20:24:21 WIB, umur >48 jam, totalSupply 321/1111 belum sold out). 0 kandidat track-A baru (velocity: hanya bridge-0xbf3488e4 lolos, tanpa free%/umur terverifikasi - bukan promosi). 0 early lead baru, 0 lead/kandidat track-C baru. Reread 612 kontrak + 83 track_c (blok 132593641, 557,7 dtk). Scan rute 4 FAST-FAIL: Ankr pre-flight HTTP 401 Unauthorized (4,7 dtk, head 132593642) - kelanjutan outage sejak ~13:33 WIB; watermark TETAP 132512564, gap ke head ~81.078 blok dan membesar. 5a: 27 alamat baru feed Sourcify di-shape-check, 0 sale-shape (20 unverified/404, 7 S1/S2 False). 5c: 0 kandidat baru (430 ERC-20 output scan 1231 sudah dicek semua). Boltbook EN 47.861 byte + ZH 47.941 byte rc 200; 10 alamat unik, 0 baru sebagai lead (0x8269... = kontrak rewards BOLT; 0xbc8f... = owner Rose Genesis). Sweep rute 3 EN+ZH: 0 proyek baru (MOLT AGENT sudah habis; Horus Phase 1 sold out; AgentForge sold out; Laser Agents lama). Route 6: Binance Square via sweep (hasil lama); Odaily newsflash 0; PANews 0. Bridge tidak berubah (mtime 2026-11-08 18:21 UTC); 2 kontrak bridge di luar snapshot adalah ERC20 dividend tracker BERBAYAR (bukan lead). Track-B binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund=1, totalShares 3110, tokenClaimed 0, blok 132594018) - sudah dilaporkan sekali. Grove freeOpen=0 (blok 132592990). TEMUAN PROSES: freePctVerified di snapshot untuk kontrak factory (Agentic/BAHUANG3/Lenx) basi karena dihitung dari nilai freeMinted awal yang salah label sebagai freeClaimed; freeClaimed() no-arg REVERT di kontrak-kontrak ini - freeMinted() adalah counter operative (terbukti Lenx: freeMinted 792 + freeRemaining 208 = FREE_CAP 1000). Merge run ini memperbaiki freePctVerified keempat item promosi dari freeMinted/cap."
snap["runNote2031_scan"]="Scan run 2031: PRE-FLIGHT GAGAL CEPAT - ankr_getLogs 1 chunk 50 blok, HTTP 401 Unauthorized dalam 4,7 dtk (head 132593642). Ankr outage berlanjut sejak ~13:33 WIB 2026-11-09 (kredensial ditolak rpc.ankr.com; reconnect belum terverifikasi pulih). Scan leg fast-fail; watermark TETAP 132512564; gap ke head ~81.078 blok (132593642-132512564) dan membesar selama Ankr mati. 0 first-seen, 0 lead dari scan. 5c dilewati dari output scan baru (tidak ada) - memakai output scan 1231 yang sudah habis dicek."
snap["runNote2031_binanceai"]="Run 2031 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (probe dataseed, blok 132594018). Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang."
snap["runNote2031_freecounter"]="Run 2031 resolusi counter gratis: freeClaimed() no-arg REVERT di Agentic, BAHUANG3, Lenx, TIME CARDS (bukan counter total). freeMinted() adalah counter operative: Agentic 374/1000, BAHUANG3 2337/6000, Lenx 792/1000 + freeRemaining 208 (792+208=1000=FREE_CAP, bukti aritmetika), TIME CARDS 1333/2000. Nilai 'freeClaimed' di snapshot untuk Agentic (189), BAHUANG3 (n/a), Lenx (128) adalah freeMinted saat triase yang salah label; freePctVerified terkait (18,9% / 24,65% / 12,8%) sudah basi dan diperbaiki run ini dari freeMinted/cap segar. Cassetto/Retrocam/Hourglas/CAISHEN (gelombang 2026-11-08 14:56, snapFreePct 30-43% dari triase) TIDAK dipromosikan run ini: freeMinted segar None di reread (free% segar UNVERIFIED) - promosi butuh angka segar terverifikasi."
snap["last_run"]="2031"; snap["last_run_wib"]="2026-11-09 20:31 WIB"
snap["last_run_note"]="Run 2031: 612 kontrak + 83 track_c re-read (blok 132593641); 4 PROMOSI STRONG LEAD gate-blocked (TIME CARDS 58,2%, Agentic 37,2%, BAHUANG3 38,95%, Lenx 79,2%) - dilaporkan sekali, TIDAK di-mint (gate website gagal/belum terverifikasi); MONEY free pool habis 222/222 -> sold-out; AURISLE age-excluded >48 jam; 0 kandidat/early baru; scan fast-fail Ankr 401 (watermark 132512564, gap ~81 rb blok); binanceai tetap refund; Grove belum buka."
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
json.dump({"contracts_updated":n_upd,"track_c_updated":n_tc,"velocity_pass":vel_pass,"block":BLOCK}, open(f"{BASE}/run-2026-11-09-2031-merge.json","w"), indent=1)
print("MERGE DONE contracts:",n_upd,"track_c:",n_tc,"velocity_pass:",vel_pass)
