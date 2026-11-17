#!/usr/bin/env python3
"""Merge run 2026-11-16 16:01 WIB into onchain-snapshot.json. Read-only on chain; writes snapshot only."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE+"onchain-snapshot.json", BASE+"onchain-snapshot.json.bak-1601")
s=json.load(open(BASE+"onchain-snapshot.json"))
r16=json.load(open(BASE+"run-2026-11-16-1601-reread.json"))
r15=json.load(open(BASE+"run-2026-11-16-1531-reread.json"))
r14=json.load(open(BASE+"run-2026-11-16-1501-reread.json"))
feed=json.load(open(BASE+"run-2026-11-16-1601-feedshape.json"))
ver=json.load(open(BASE+"run-2026-11-16-1601-verify.json"))
fm=json.load(open(BASE+"run-2026-11-16-1601-firstmint4.json"))
BLK=r16["block"]; WIB="2026-11-16 ~16:01 WIB"
FRESH_BLK=133902748  # fresh Volta/Punch/HARBOR read ~16:22 WIB
def find_entry(addr):
    for coll in ("contracts","track_c"):
        for k,v in s.get(coll,{}).items():
            if isinstance(v,dict) and (v.get("address") or "").lower()==addr.lower():
                return coll,k,v
    return None,None,None
def cur(v):
    return v.get("totalSupply") if v.get("totalSupply") is not None else v.get("totalMinted")
# prev rates: run 1531 deltas vs run 1501 over ~30 min
prev_rate={}
for name in r15["reads"]:
    c15=cur(r15["reads"][name].get("views") or {})
    c14=cur(r14["reads"].get(name,{}).get("views") or {})
    if c15 is not None and c14 is not None:
        prev_rate[name]=(c15-c14)/30.0
updated=[]
for name,rd in r16["reads"].items():
    v=rd["views"] or {}
    coll,k,ent=find_entry(rd["address"])
    if ent is None:
        print("NO SNAPSHOT ENTRY for",name,rd["address"]); continue
    v15=r15["reads"].get(name,{}).get("views") or {}
    c16,c15=cur(v),cur(v15)
    delta=(c16-c15) if (c16 is not None and c15 is not None) else None
    rate=(delta/30.0) if delta is not None else None
    pr=prev_rate.get(name)
    ratio=(rate/pr) if (rate is not None and pr) else None
    vel = bool(delta is not None and delta>=20 and ratio is not None and ratio>=1.5)
    for f in ("totalSupply","totalMinted","freeMinted","freeClaimed","freeLeft","FREE_SUPPLY","FREE_CAP","MAX_SUPPLY","mintOpen","paused","priceFor_user","freeUsed_user","balanceOf_user","mintedBy_user","freeClaimed_user","freeMintedBy_user","hasAgentId_user","mintedPerWallet_user","freeMintedPerWallet_user","holdsAgentId_user","mintsBy_user","mintCountOf_user","freeSharesLeft","openedAt","freeBooked_user","freeRemaining","FREE_MAX","paidMinted","mintPrice","totalSpecimens","currentExperiment","genesisStart","genesisOpen","priceFor_user_1","mintPriceFor_user_1","cost_user_1","mintsLeft","FREE_MINT_CAP","freeMintsLeft","PRICE","remainingSupply","isFreePhase","TOKEN_PRICE","AGENT_ID","owner","launched","failed","isRefundPhase","totalShares","tokenClaimed_user","claimOpen","hasFreeClaimed_user","freeSupply","maxSupply"):
        if f in v and v[f] is not None:
            ent[f]=v[f]
    ent["lastReadBlock"]=BLK
    ent["lastReadWib"]=WIB
    if delta is not None:
        ent["previousTotalSupply"]=c15
        ent["totalSupply"]=c16 if v.get("totalSupply") is not None else ent.get("totalSupply")
        if v.get("totalMinted") is not None: ent["totalMinted"]=v["totalMinted"]
        ent["mintedInInterval"]=delta
        ent["intervalMinutes"]=30
        ent["currentRatePerMin"]=round(rate,4)
        ent["previousRatePerMin"]=round(pr,4) if pr is not None else None
        ent["velocityRatio"]=round(ratio,2) if ratio is not None else None
        ent["velocityLegPasses"]=vel
    ent["runNote1601_1116"]=f"Run 1601 (blok {BLK}, interval ~30 mnt vs run 1531): {c15}->{c16} (+{delta}, {rate:.3f}/mnt vs prev {pr if pr is not None else 'n/a'}/mnt = {ratio if ratio is not None else 'n/a'}x) -> velocity {'LOLOS' if vel else 'GAGAL'} (butuh >=1.5x DAN >=20 token). DIAM." if delta is not None else f"Run 1601 (blok {BLK}): views tidak lengkap, velocity TIDAK dihitung. DIAM."
    updated.append(name)
print("updated:",len(updated))
# BinanceAI pending claim
pc=s.get("pending_claims",{})
for k,v in pc.items():
    if isinstance(v,dict) and "binanceai" in k.lower():
        v["launched"]=0; v["failed"]=1; v["isRefundPhase"]=1; v["totalShares"]=3110; v["tokenClaimed"]=0
        v["lastCheckWib"]=WIB; v["lastReadBlock"]=BLK
        v["runNote1601_1116"]="Run 1601: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM."
        print("binanceai updated:",k)
# --- Volta Gent: STRONG LEAD, website gate FAILED -> reported once as blocked ---
vvolta=ver["reads"]["Volta Gent"]["views"]
s["contracts"]["Volta Gent"]={
 "address":"0x2703a2be75e0c470d83573badc6a1b1b86d1871e",
 "name":"Volta Gent","symbol":"VLTG","kind":"ERC721",
 "status":"strong-lead-gate-blocked-2026-11-16",
 "totalMinted":1484,"MAX_SUPPLY":2222,"AGENT_LIMIT":1500,
 "AGENT_PRICE":0,"PUBLIC_PRICE":1100000000000000,
 "agentPhaseActive":1,"mintOpen":1,
 "AGENT_ID_REGISTRY":"0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "codeHasRegistry":True,"codeLen":7476,
 "agentMintedByWallet_user":0,"mintedByWallet_user":0,"balanceOf_user":0,"hasAgentId_user":1,
 "freePctInference":98.9,
 "freePctNote":"INFERENCE ONLY: totalMinted 1484 / AGENT_LIMIT 1500 = 98,9% (blok 133902748, ~16:22 WIB). Bukan free counter terverifikasi: kontrak tak punya total-agent-minted view; inferensi dari totalMinted + agentPhaseActive=1 + AGENT_PRICE=0 + sim penulis Boltbook (wallet tanpa Agent ID revert 'agent phase needs Agent ID') - selama fase agen aktif, semua mint adalah mint agen gratis.",
 "launchNote":"Umur TERVERIFIKASI <24 jam: first mint via eth_getLogs publik (bsc-rpc.publicnode.com, Transfer-from-zero) - bracket: probe -24000 blok ada 5 mint, probe -36000 blok 0 mint -> first mint di blok (133866026, 133878026], ~11:55-13:25 WIB 16 Nov 2026. Umur saat run ~2,6-4,1 jam. Sourcify verifiedAt 2026-11-16 06:24 UTC (13:24 WIB) konsisten.",
 "xVerified":False,
 "discussionNote":"Diskusi publik terbaca: Boltbook superhera.ai '2 free lead baru terverifikasi on-chain 16:00 WIB' + Alphapedia volta-gent (Added 2026-11-16) + post 'VLTG sprint' (1.179 pukul 15:19). Akun X resmi proyek TIDAK ditemukan.",
 "websiteVerified":False,
 "websiteGate":"FAILED run 1601: metode (A) pencarian alamat persis -> noise saja; (B) post Boltbook + Alphapedia menyatakan 'No official website or X found'; (C) metadata Sourcify tanpa URL proyek; (D) pola same-family (.pages.dev/.vercel.app) tanpa hasil; (G) pencarian nama 'Volta Gent' -> hanya framework VoltAgent (bukan proyek ini). TIDAK ada website terverifikasi -> TIDAK preview, TIDAK mint (MANDATORY WEBSITE GATE).",
 "velocityVerified":False,
 "velocityNote":"Tidak ada baseline (first read run ini) - velocity TIDAK bisa lolos run ini.",
 "baselineNote":"STRONG LEAD dilaporkan sekali run 1601 sebagai BLOCKED (gate website gagal): umur terverifikasi <24 jam + free 98,9% INFERENCE (>70%) + slot user terbuka (agentMintedByWallet=0, balanceOf=0, hasAgentId=1). TIDAK di-preview/di-mint. Free lane nyaris habis (16 slot tersisa dari 1500 pada 16:22 WIB, pace ~19/mnt) - kemungkinan sudah habis saat laporan dibaca.",
 "lastReadBlock":FRESH_BLK,"lastReadWib":"2026-11-16 ~16:22 WIB",
 "reportedOnce":"strong-lead-gate-blocked run 1601",
}
print("Volta Gent added as strong-lead-gate-blocked")
# --- Punch Card: EARLY LEAD (reported once, never preview/mint) ---
vpunch=ver["reads"]["Punch Card"]["views"]
s["contracts"]["Punch Card"]={
 "address":"0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",
 "name":"Punch Card","symbol":"CARD","kind":"ERC721",
 "status":"early-lead-2026-11-16",
 "totalSupply":487,"totalMinted":487,"freeMinted":486,"paidMinted":1,
 "MAX_SUPPLY":5555,"remaining":5068,"mintOpen":1,
 "MINT_PRICE":500000000000000,"mintPriceFor_user_1":0,"mintedCount_user":0,
 "balanceOf_user":0,
 "AGENT_REGISTRY":"0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "codeHasRegistry":True,"codeLen":9405,
 "freePctVerified":8.75,
 "freePctNote":"freeMinted 486 / MAX_SUPPLY 5555 = 8,75% (blok 133902748, ~16:22 WIB). Di bawah 50% kandidat dan 70% strong lead - early lead saja.",
 "launchNote":"Umur TERVERIFIKASI <24 jam: first mint via eth_getLogs publik - bracket: probe -12000 blok ada 3 mint, probe -18000 blok 0 mint -> first mint di blok (133884026, 133890026], ~14:10-14:55 WIB 16 Nov 2026. Umur saat run ~1,1-1,9 jam. Sourcify verifiedAt 2026-11-16T07:50:40Z (14:50 WIB) konsisten.",
 "xVerified":False,
 "discussionNote":"Diskusi publik terbaca: Boltbook ziwbly.ai 'Punch Card (CARD): 454 of 5,555 minted' ~16:00 WIB. X proyek dari metadata contractURI: https://x.com/PunchInBNB (tambahan, belum diverifikasi via baca X).",
 "website":"https://punchin.fun",
 "websiteVerified":True,
 "websiteNote":"Website TERVERIFIKASI run 1601: contractURI() base64 JSON external_link https://punchin.fun (metode I) + fetch langsung situs mencetak alamat kontrak persis 0x1d4ef0587dd3ff3875a141d4711c60bca40587c4.",
 "velocityVerified":False,
 "velocityNote":"Tidak ada baseline (first read run ini) - velocity TIDAK bisa lolos run ini.",
 "baselineNote":"EARLY LEAD dilaporkan sekali run 1601: agent-shaped (AGENT_REGISTRY + codeHasRegistry + free-mint fn + free views) + first mints terverifikasi on-chain run ini (bracket getLogs) + umur <24 jam terverifikasi + website terverifikasi. TIDAK PERNAH di-preview/di-mint (early lead). Naik jadi strong lead bila free% >70% + slot terbuka; jadi kandidat bila semua syarat + safety lolos.",
 "lastReadBlock":FRESH_BLK,"lastReadWib":"2026-11-16 ~16:22 WIB",
 "reportedOnce":"early-lead run 1601",
}
print("Punch Card added as early-lead")
# --- Fira Agent: AGE-EXCLUDED, remove from contracts ---
if "Fira Agent" in s.get("contracts",{}):
    del s["contracts"]["Fira Agent"]
    print("Fira Agent REMOVED from contracts (age-excluded)")
s["age_exclusion_FiraAgent_1601"]=("Run 1601 AGE-EXCLUDED Fira Agent 0x7d46023bf2c3732f5fd30321cfce1ca91684408d: "
 "pertama terlihat hot-leg 2026-11-09 21:26 WIB (Boltbook frontpage) + totalSupply sudah 4900/5000 pada 2026-11-11 10:31 WIB + "
 "re-read run ini totalSupply tetap 4900/5000 (blok 133901199) -> minting terbuka >=7 hari, >24 jam, belum sold out (100 slot tersisa). "
 "Dihapus dari snapshot contracts. TIDAK pernah dilaporkan ke chat sebagai lead -> DIAM (tidak ada laporan age-exclusion).")
# --- checked-not-lead this run ---
s["checkedNotLead1601"]={
 "Orin Agent":"Run 1601: Boltbook dieuxuan50.ai 15:58 WIB klaim 9.901/10.001 free (99,0%) - verifikasi on-chain: totalSupply 9901, MAX_SUPPLY 10000 (bukan 10.001), balanceOf(user)=0 (blok 133901199). Pertama terdeteksi monitor 2026-11-12 02:32 (dinyatakan di post) -> umur >=4,5 hari, >24 jam -> AGE-EXCLUDED. Sourcify UNVERIFIED. TIDAK masuk snapshot, TIDAK dilaporkan (belum pernah dilaporkan).",
 "HEXCOVEN":"Run 1601: Boltbook nanomind.ai 'new free mint 293/9,999' - verifikasi on-chain: totalSupply 313, MAX_SUPPLY 9999, mintOpen 1, mintStart 1794397822 = 2026-11-11 ~18:51 WIB, mintEnd 1795002622, PRICE 0,00005 BNB, freeLeft 1688, FIRST_FREE_CAP 2000, balanceOf(user)=0 (blok 133901199). Umur ~4,6 hari >24 jam -> AGE-EXCLUDED. BUKAN agent-shaped: tanpa registry/AgentGate (codeHasRegistry False, tanpa fungsi agent), free lane berbasis verifikasi X (freeMintX/xSigner). contractURI -> https://hexcoven.pages.dev/meta/collection.json. TIDAK masuk snapshot, TIDAK dilaporkan.",
 "Glyphs of Xor":"Run 1601: Boltbook agata.ai re-verifikasi 302/1.555, mint(1) value 0, UNGATED, costOf(user,1)=0 - status snapshot sudah checked-age-excluded-2026-11-16 (run 1201); TIDAK ada fase/batch baru terverifikasi -> tetap excluded, TIDAK dilaporkan.",
 "SnakeAgent":"Run 1601: Boltbook bangwi.ai recheck 1.171/4.444, mint(1) value 0 lolos wallet Agent ID, Sourcify unverified, free views revert - status snapshot sudah age-excluded-2026-11-13; TIDAK ada perubahan -> DIAM.",
 "Zephyr Agent":"Run 1601: Boltbook - 'Zephyr's 4,901 is 4,900 team pre-mint, only 1 public mint ever' - status snapshot watchlist-only-2026-11-14 (ts 4901); info dicatat, TIDAK ada promosi (free% publik praktis 0).",
 "Xuanwu Seed":"Run 1601: sweep ZH menemukan Xuanwu Seed 0x05fd19702029c473683d6188cD856e59038278F4 (ERC-1155, 10.000, first free, mint dibuka 25 Okt 01:00 UTC+8) - TIDAK ada di snapshot/seen/hot; umur ~22 hari >24 jam -> age-excluded, TIDAK masuk snapshot, TIDAK dilaporkan (belum pernah dilaporkan).",
 "Meow Cards":"Run 1601: sweep EN menemukan Meow Cards 0xb8164afefc53910d7a74cece15a60a9e0c86089e (10.000 kartu, first free, post 10 Nov) - SUDAH di snapshot + seen + hot; umur >24 jam -> tetap age-excluded, DIAM.",
 "SPEC / LumenFindings":"Run 1601: reread LumenFindings totalSpecimens 6440->6504, currentExperiment 27->28, genesisStart TETAP 1794534187 (=2026-11-13 08:43 WIB, umur ~3,3 hari). Boltbook post 'FIND exp27 SEGEL di 206' + '14:55 recheck: FIND exp27 at 206/300' mengonfirmasi exp27 sealing ~206/300, pace ~0,04/mnt, leg mati. Rollover exp 27->28 dengan genesisStart sama BUKAN fase/batch mint baru. Status tetap age-excluded-2026-11-14. Koreksi: angka run 1531 (totalSpecimens 4713/exp 5/genesisStart 1794492248) adalah angka post Boltbook lama, BUKAN reread on-chain (reread 1501/1531/1601 konsisten 6435-6504/27-28/1794534187) - kesimpulan age-excluded TIDAK berubah.",
}
# --- HARBOR: checked, NOT agent-shaped -> track_c checked entry ---
s["track_c"]["HARBOR"]={"address":"0xa5844f0539e289c9a477672818ee263ef862b517","status":"checked-not-agent-shaped-2026-11-16",
 "note":"Run 1601 Boltbook superhera.ai + Alphapedia harbor: claimFree(address) value 0, FREE_SEATS 1500, freeSold 228, paidSold 0, PRICE 0,006 BNB, SHARE 1.000.000 HRBR, START 1794816000 (=2026-11-16 16:00 CST = 15:00 WIB), POOL_DEADLINE 1794902400, totalSupply 8.000.000.000 HRBR (TOTAL_SUPPLY sama - sengketa post 1,5 miliar SALAH, komentator cod42203.ai BENAR), pair 0, poolOpen 0, freeClaimed(user)=0, hasMinted(user)=0 (blok 133902748). Website https://harbor-hrbr.github.io/harbor/ TERVERIFIKASI (website() + halaman mencetak kontrak persis). BUKAN track-C: tanpa registry/AgentGate (codeHasRegistry False, tanpa fungsi agent di ABI) -> gagal sale-shape S1/S2. BUKAN track-B (user tak pegang entitlement). TIDAK dilaporkan."}
print("HARBOR recorded in track_c as checked-not-agent-shaped")
# --- Feedshape: 6 new checked-not-sale-shape entries ---
n_new=0
for o in feed:
    addr=o["address"]
    exists=any(isinstance(v,dict) and (v.get("address") or "").lower()==addr.lower() for v in s.get("track_c",{}).values())
    if exists: continue
    key="Feed-ERC20-0x"+addr[2:6]
    s["track_c"][key]={"address":addr,"status":"checked-not-sale-shape-2026-11-16",
      "note":f"Run 1601 Sourcify feed (verified {o.get('verifiedAt','?')}): S1={o.get('S1')} S2={o.get('S2')}; mint={o.get('has_mint')} quote={o.get('has_quote')} free_views={o.get('free_views')} agent_ref={o.get('agent_ref')} fns={o.get('n_fns')}. Bukan lead track-C; first-mint tidak terverifikasi."}
    n_new+=1
print("feedshape new track_c entries:",n_new)
# --- run notes ---
s["runNote1601_1116"]="Run 1601 (16:01 WIB): re-read 37/37 OK blok 133900431 (94,1 dtk, interval ~30 mnt vs run 1531). Velocity: TIDAK ADA yang lolos; maks SPARKS +10 (0,333/mnt, 0,77x - melambat); MORFO +4 (4,0x tapi <20); Matrix Agents +4 (4,0x tapi <20); Bold Leonidas +3 (3,0x tapi <20). Matrix Agents freeMinted 551/1000 = 55,1% (naik dari 54,7%), umur tetap UNVERIFIED, velocity gagal -> bukan strong lead, bukan kandidat. HIVE 1263 FLAT, bal_user=1, minted-by-user. BinanceAI-mint: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2 Nov). ALIEN masih BELUM DIBUKA (totalSupply 0, mintOpen=0). RigForge openedAt masih 0, freeSharesLeft 638 (dari 639), freeClaimed 362. JADE 191 flat (free sold out). WANGCAI/YUANBAO 189 flat (sold out). Fira Agent AGE-EXCLUDED (>=7 hari) -> dihapus dari snapshot (diam, belum pernah dilaporkan). LAPORAN RUN INI: 1 strong lead BLOCKED (Volta Gent, gate website gagal) + 1 early lead (Punch Card)."
s["runNote1601_1116_scan"]="Run 1601 SCAN FAST-FAIL (Ankr 401): pre-flight via run-2026-11-16-1601-scanpreflight.py (ankr_getLogs 50 blok 133900328-133900377) gagal deterministik HTTP 401 Unauthorized dalam 1,10 dtk, sama dengan run 2026-11-12, 2026-11-14 00:16, 2026-11-15 07:16 & 12:31, 2026-11-16 03:01, 09:01, 14:01 & 15:31. Driver TIDAK diluncurkan. Watermark TETAP 132512564. Head 133900378, gap 1.387.814 blok dan membesar (~8.000/jam). Triase + 5c dilewati (tidak ada output scan). TAMBAHAN: eth_getLogs via Binance dataseed juga rate-limit -32005 ('limit exceeded') untuk SEMUA rentang (termasuk 10 blok) - verifikasi first-mint dialihkan ke bsc-rpc.publicnode.com yang menjawab."
s["runNote1601_1116_firstmint"]="Run 1601 first-mint via publicnode eth_getLogs (Transfer-from-zero, bracket probe): Volta Gent first mint di blok (133866026, 133878026] = ~11:55-13:25 WIB 16 Nov (umur ~2,6-4,1 jam, <24 jam TERVERIFIKASI). Punch Card first mint di blok (133884026, 133890026] = ~14:10-14:55 WIB 16 Nov (umur ~1,1-1,9 jam, <24 jam TERVERIFIKASI). Probe -48000 blok gagal rate-limit publicnode (-32005) - bracket sudah cukup untuk tes umur; blok first-mint persis tidak dipin-down run ini."
s["runNote1601_1116_boltbook"]="Run 1601 Boltbook EN 200 (45.325 byte) / ZH 200 (45.471 byte): 14 alamat unik, 0 baru vs snapshot+seen+hot di front page; 7 postingan dibaca penuh (Volta Gent+HARBOR, Fira, Orin, HEXCOVEN, Punch Card, Glyphs of Xor, SnakeAgent). Temuan: Volta Gent 0x2703 (strong lead, gate-blocked), Punch Card 0x1d4e (early lead), HARBOR 0xa584 (bukan agent-shaped), Fira age-excluded, Orin age-excluded, HEXCOVEN age-excluded + bukan agent-shaped, Glyphs/SnakeAgent tanpa perubahan."
s["runNote1601_1116_sweep"]="Run 1601 sweep EN+ZH: hanya proyek lama (Meow Cards 10 Nov age-excluded; Agentic Gangster 9 Nov; RIGBYPASS excluded; STAMP PASS 9 Nov; YAMA 10 Nov track_c; WNO 10 Nov track_c; AGENT COSMOS 5 Nov; Xuanwu Seed 25 Okt age-excluded ~22 hari; AGENT ID cards 25 Okt) - 0 proyek baru di luar Boltbook. Komplemen 6a/6b/6c: Odaily newsflash dicek langsung (HTTP 200, 294.565 byte, 0 hit kata kunci Agent ID/free mint/free share); Square/PANews/DappBay tidak menambah di luar sweep+Boltbook+Sourcify."
s["runNote1601_1116_feedshape"]="Run 1601 Sourcify feed: 20 kontrak terbaru (verifiedAt s.d. 09:01:03Z), 0 S1 / 0 S2; 2 kontrak dgn mint+freeMinted (0x1587, 0x1d4E) tanpa quote + tanpa agent_ref -> bukan sale-shape. 6 baru dicatat checked-not-sale-shape di track_c, 14 sudah tercatat."
s["runNote1601_1116_binanceai"]="Run 1601 track-B binanceai.fun: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133900431) - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM."
s["runNote1601_1116_bridge"]="Run 1601 bridge (read-only): 116 kontrak bridge, 116/116 sudah di snapshot, 0 baru, 7 same_owner_discarded. Tidak ada temuan pelengkap baru / promosi run ini. Job ini tidak menulis bridge."
s["runNote1601_1116_volta"]="Run 1601 Volta Gent 0x2703a2be75e0c470d83573badc6a1b1b86d1871e STRONG LEAD (dilaporkan sekali sebagai BLOCKED): umur terverifikasi <24 jam (first-mint bracket ~11:55-13:25 WIB) + free 98,9% INFERENCE (totalMinted 1484/AGENT_LIMIT 1500, blok 133902748 ~16:22 WIB; 16 slot tersisa, pace ~19/mnt) + slot user terbuka (agentMintedByWallet=0, balanceOf=0, hasAgentId=1) + diskusi publik (Boltbook superhera.ai + Alphapedia). Website gate FAILED (metode A/B/C/D/G: tidak ada website/X resmi) -> TIDAK preview, TIDAK mint. Sourcify exact_match; owner EOA; kontrak pegang 0 BNB."
s["runNote1601_1116_punch"]="Run 1601 Punch Card 0x1d4ef0587dd3ff3875a141d4711c60bca40587c4 EARLY LEAD (dilaporkan sekali): agent-shaped (AGENT_REGISTRY + codeHasRegistry + free-mint fn + free views) + first mints terverifikasi on-chain run ini (bracket ~14:10-14:55 WIB) + umur <24 jam terverifikasi + website TERVERIFIKASI (punchin.fun mencetak kontrak persis) + diskusi Boltbook ziwbly.ai. totalSupply 487, freeMinted 486/5555 = 8,75%, mintPriceFor(user,1)=0, slot user terbuka. TIDAK PERNAH di-preview/di-mint (early lead)."
s["last_run_wib"]="2026-11-16 ~16:01 WIB"
s["last_run"]="free-mint-search 2026-11-16 16:01 WIB — LAPOR: 1 strong lead BLOCKED (Volta Gent, gate website gagal) + 1 early lead (Punch Card); 0 eksekusi/preview"
s["last_run_note"]="Run 1601: Volta Gent strong lead tapi gate website gagal (tidak ada website) -> dilaporkan sekali sebagai blocked, tanpa preview/mint; Punch Card early lead (website terverifikasi). Fira Agent age-excluded + dihapus dari snapshot. Ankr 401 berlanjut; watermark scan tertahan di 132512564; getLogs dataseed juga rate-limit, first-mint diverifikasi via publicnode."
json.dump(s,open(BASE+"onchain-snapshot.json","w"),indent=1)
print("SNAPSHOT WRITTEN")
