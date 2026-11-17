#!/usr/bin/env python3
"""Finalize run 1231: update snapshot readings, apply age exclusions (14),
add Dinobyte (age) + KALOS (free sold out) to excluded, update track_c JAGT/MoonAgent,
write run notes. Atomic write (tmp + replace)."""
import json, os, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK=132148622
RUN="2026-11-07 run 1231"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
re=json.load(open(f"{BASE}/run-2026-11-07-1231-reread.json"))
vel=json.load(open(f"{BASE}/run-2026-11-07-1231-velocity.json"))

# --- 1. bulk reading updates (only non-None values) ---
updated=0; none_free=0
for name, d in re["reread"].items():
    c=snap["contracts"].get(name)
    if c is None: continue
    for k in ("totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen"):
        if d.get(k) is not None: c[k]=d[k]
    if d.get("balanceOf_user") is not None: c["balanceOf_user"]=d["balanceOf_user"]
    if d.get("freeClaimed") is None and d.get("freeMinted") is None: none_free+=1
    c["lastReadBlock"]=REREAD_BLOCK
    c["lastReadWib"]=RUN
    updated+=1
# track_c readings
for name, d in re.get("track_c",{}).items():
    tc=snap.get("track_c",{}).get(name)
    if isinstance(tc,dict):
        if d.get("totalSupply") is not None: tc["totalSupply"]=d["totalSupply"]
        if d.get("freeMinted") is not None: tc["freeMinted"]=d["freeMinted"]
        if d.get("freeSharesRemaining") is not None: tc["freeSharesRemaining"]=d["freeSharesRemaining"]
        tc["lastReadBlock"]=REREAD_BLOCK
        tc["lastReadWib"]=RUN

# --- 2. velocity note: Conciergo pass (not a lead: free% 5.55 + same-owner-discarded) ---
cg=snap["contracts"].get("Conciergo")
if cg is not None:
    cg["velocityNote1231"]="Run 1231 (blok 132148622): +31 token, rate 0.8746/mnt, ratio 11.72x -> velocity LOLOS, TAPI TIDAK promosi: free% 5.55 (jauh di bawah 25% strong leg) + status watchlist-only-same-owner-discarded-2026-11-03."
hive=snap["contracts"].get("HIVE Agents")
if hive is not None:
    hv=[r for r in vel["rows"] if r["name"]=="HIVE Agents"]
    hive["runNote1231"]=f"Run 1231 (blok {REREAD_BLOCK}): totalSupply {hv[0]['curSupply'] if hv else '?'}, minted {hv[0].get('mintedInInterval') if hv else '?'} interval; velocity {'LOLOS' if hv and hv[0].get('velocityPasses') else 'GAGAL'}; balanceOf(user)={hv[0].get('balanceOf_user') if hv else '?'}; minted-by-user, bukan kandidat." if hv else f"Run 1231 (blok {REREAD_BLOCK}): reread done."

# --- 3. age exclusions: 14 active leads, verified first mint >48h, not sold out ---
REMOVALS=[
 ("Agent Goats","2026-11-05 12:55:17 WIB",131764404,48.3),
 ("Agent Owls","2026-11-05T12:54:51+07:00",131764347,48.3),
 ("AgentMiner","2026-11-05T12:59:40+07:00",131764989,48.2),
 ("Thronemind","2026-11-05T12:40:04+07:00",131762375,48.6),
 ("Hashseers","2026-11-05T12:40:55+07:00",131762488,48.6),
 ("Layerloom","2026-11-05T12:42:56+07:00",131762757,48.5),
 ("Cachejack","2026-11-05T12:43:02+07:00",131762770,48.5),
 ("Roguefall","2026-11-05T11:45:17+07:00",131755074,49.5),
 ("Hirelings-A","2026-11-05T12:35:07+07:00",131761715,48.6),
 ("Hirelings-B","2026-11-05T12:34:45+07:00",131761667,48.6),
 ("Forklings","2026-11-05T12:07:30+07:00",131758036,49.1),
 ("Auspibots","2026-11-05T12:17:44+07:00",131759399,48.9),
 ("Neurolucha","2026-11-05T11:48:07+07:00",131755452,49.4),
 ("PERSONA","2026-11-05 01:14:41 WIB",131671016,60.0),
]
removed=[]
for name, fmw, fmb, ageh in REMOVALS:
    c=snap["contracts"].get(name)
    if c is None:
        print("SKIP (not in contracts):", name); continue
    ex=dict(c)
    ex["status"]="excluded-age-over-48h-2026-11-07"
    ex["status_before"]=c.get("status")
    ex["firstMintWib"]=fmw
    ex["firstMintBlock"]=fmb
    ex["ageHoursAtVerify"]=ageh
    ex["totalSupply_at_removal"]=re["reread"].get(name,{}).get("totalSupply")
    ex["ageExclusionNote"]=(f"DIHAPUS dari watchlist aktif run 1231: first mint terverifikasi {fmw} (blok {fmb}) -> umur ~{ageh} jam >48 jam; "
        f"totalSupply segar {ex['totalSupply_at_removal']}/{c.get('MAX_SUPPLY')}, belum sold out; free views gagal dibaca run ini (degradasi RPC, nilai snapshot dipertahankan); balanceOf(user)=0.")
    ex["lastReadBlock"]=REREAD_BLOCK
    ex["lastReadWib"]=RUN
    snap.setdefault("excluded",{})[name]=ex
    del snap["contracts"][name]
    removed.append(name)
print("REMOVED:", len(removed), removed)

# --- 4. Dinobyte -> excluded (age ~139.7h, verified first mint) ---
snap.setdefault("excluded",{})["DINOBYTE"]={
 "address":"0xd713ddfd37b8ff759afaeedaedad632d1985ed9c",
 "status":"excluded-age-over-48h-2026-11-07",
 "track":"A","name":"DINOBYTE","symbol":"DINOBYTE",
 "totalSupply":3302,"freeClaimed":3208,"FREE_SUPPLY":7000,"MAX_SUPPLY":7777,
 "freePct":45.83,"mintOpen":1,
 "owner":"0x53043412c4f2436f68e56bb9638ebebb099fb3c1",
 "AGENT_ID":552192074493313695968015109214105588393044541999,
 "PRICE":50000000000000,"FREE_PER_WALLET":3,
 "freeLeft_user":3,"mintedBy_user":0,"balanceOf_user":0,
 "firstMintWib":"2026-11-01 14:10:35 WIB","firstMintBlock":131006643,
 "firstMintTx":"0xec560bd0901ed344911988d13d2b24cf79bcf9a11eb7ba76972fff15d790fce9",
 "ageHoursAtVerify":139.7,
 "websiteGate":"unverified (pencarian web run 1231: tanpa situs proyek dan tanpa akun X; hanya Boltbook + hit tak terkait; contractURI base64 JSON tanpa URL - method H)",
 "xDiscussion":"unverified (Boltbook membahas hari ini, tapi tanpa akun X proyek; bukan bukti diskusi yang memenuhi syarat kandidat)",
 "ageExclusionNote":"BARU dari web legs run 1231 (Boltbook), diverifikasi on-chain run ini: first mint blok 131006643 = 2026-11-01 14:10:35 WIB (binary-search Ankr getLogs) -> umur ~139,7 jam >>48 jam, belum sold out (3302/7777), free 3208/7000=45,83% (<50% juga). TIDAK pernah dilaporkan sebagai lead; langsung excluded, tidak di-preview/di-mint. Owner sama dengan keluarga Tacotron (template 7777/7000/0,00005 BNB) - juga gagal same-owner bila umur lolos.",
 "lastReadBlock":132149489,"lastReadWib":RUN,
}
# --- 5. KALOS CODE -> excluded (free lane sold out) ---
snap["excluded"]["KALOS CODE"]={
 "address":"0xd45bdd6aa5e4a6c5446a02cd1d3ec662f3ed55e6",
 "status":"excluded-free-sold-out-2026-11-07",
 "track":"A","name":"KALOS CODE","symbol":"KCODE",
 "totalSupply":None,"freeClaimed":100,"FREE_SUPPLY":100,"MAX_SUPPLY":1000,
 "freePct":100.0,"mintOpen":1,
 "ageExclusionNote":"BARU dari web legs run 1231 (Boltbook), diverifikasi on-chain run ini: freeClaimed 100/100 = free lane HABIS (totalSupply gagal baca run ini, degradasi RPC). Free lane mati ~6 mnt setelah launch per Boltbook; paid lane 0,001 BNB masih buka (bukan gratis). TIDAK pernah dilaporkan sebagai lead; langsung excluded, tidak di-preview/di-mint.",
 "lastReadBlock":132149489,"lastReadWib":RUN,
}
# --- 6. track_c JAGT / MoonAgent fresh values ---
jagt=snap.get("track_c",{}).get("JupiterAgent-JAGT")
if isinstance(jagt,dict):
    jagt["totalMints"]=114; jagt["freeLeft_user"]=1; jagt["quote_user_1"]=0
    jagt["runNote1231"]="Run 1231: totalMints 45->114/700, freeLeft(user)=1, quote(user,1)=0, mintOpen 1; gate-blocked (tanpa situs) TETAP, tanpa perubahan -> TIDAK dilaporkan ulang."
moon=snap.get("track_c",{}).get("MoonAgent-MOAGT")
if isinstance(moon,dict):
    moon["totalMints"]=153; moon["freeLeft_user"]=1; moon["quote_user_1"]=0
    moon["runNote1231"]="Run 1231: totalMints 113->153, freeLeft(user)=1, quote(user,1)=0, mintOpen 1; gate-blocked TETAP, tanpa perubahan -> TIDAK dilaporkan ulang."

# --- 7. run notes ---
snap["last_run"]="2026-11-07-1231"
snap["last_run_wib"]="2026-11-07 12:31 WIB (dieksekusi ~12:53-13:30 WIB)"
snap["timestamp_wib"]="2026-11-07 12:31 WIB"
snap["runNote1231_1107"]=(
 "Run 1231: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru, 0 track-C lead/kandidat baru, 0 pending claim baru/dibuka. "
 "Preflight PASS 5,4 dtk (head 132148563; ankr eth_blockNumber mengembalikan non-string, fallback fast_rpc race). "
 "Reread 463 kontrak + 60 track_c, blok 132148622, 541,6 dtk; free views (freeClaimed/freeMinted) banyak None (degradasi eth_call, sama seperti run 1131/1201) - nilai snapshot dipertahankan, BUKAN nol. "
 "Velocity 1 pass (Conciergo +31 ratio 11,72) - freePct 5,55% + same-owner-discarded -> BUKAN kandidat/strong lead; bridge-0x4673c787 +245 ratio 1,32 (turun dari pass); Horus AI +91 ratio 0,45. "
 "Sold out 35 (sama, 0 baru); near-sellout Dumpster Royalty 633/650 (tetap); slot changes 0. "
 "Scan SUKSES window 132147622-132148621 (1000 blok, cap), 99 NFT + 312 ERC-20 mint, 40 Ankr calls, 0 error, partial=False; 0 first-seen sejati. Gap 132146457-132147621 (1166 blok) dilewati cap, ditutup backfill (backfill-parallel 132146457-132148737 berjalan). Watermark bersama TIDAK dimajukan (tetap 132146456, milik backfill). "
 "Sourcify feed 20 kontrak (verifiedAt 04:52-05:56 UTC): 0 shape hit (Pathwyrm + Agent Souls sudah dikenal dari run 1201; 0xd45bDd6a=KALOS free lane habis; 0xa900873E=JAGT sudah track_c gate-blocked run 1201; 0x9A020F20 ERC20 tanpa registry). "
 "5c: 45 ERC-20 mint_count>=10 di window, 0 baru (semua sudah di track-c-scan-checked.json), 0 shape hit. "
 "Boltbook EN+ZH + author pages: DINOBYTE baru dari web (0xd713ddfd...) TAPI age-excluded (first mint 2026-11-01 14:10:35 WIB, ~139,7 jam) -> excluded, tidak dilaporkan sebagai lead; KALOS CODE free lane 100/100 habis -> excluded. "
 "Web sweep rute 3/5b: tanpa proyek baru (Xigo free pool habis; SYMBOL/SAFUAI/SWARM paid-only; AgentRob bukan BSC). "
 "Komplemen: Binance Square tanpa site link baru; Odaily + PANews tanpa pengumuman Agent ID free-mint; DappBay tanpa proyek yang dicek. "
 "Bridge: tidak berubah (115 entri, 7 same_owner_discarded, terakhir diubah 2026-11-06 02:48); 33 entri tidak di snapshot (temuan lama, semua first-seen Nov 3-6, 1-entitas, sudah ditriase finding-only; 11 di antaranya tidak pernah masuk snapshot - tidak ditambahkan: umur >48 jam / bukan agent-shaped, sesuai praktik run sebelumnya). "
 "Pending claims kosong; BINANCEAI tetap refund/failed (launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, tokenBalance(user)=0). "
 "JAGT totalMints 45->114/700 + MoonAgent 113->153, freeLeft(user)=1, quote=0, gate-blocked TETAP -> tidak dilaporkan ulang.")
snap["runNote1231_1107_age_exclusions"]=(
 "Run 1231 AGE-EXCLUSIONS (14 item, dilaporkan sekali sebagai perubahan): Agent Goats (first mint 2026-11-05 12:55:17 WIB, 545/2222), Agent Owls (12:54:51, 161/2222), AgentMiner (12:59:40, 889/4444), Thronemind (12:40:04, 820/4000), Hashseers (12:40:55, 680/4000), Layerloom (12:42:56, 790/4000), Cachejack (12:43:02, 611/4000), Roguefall (11:45:17, 293/4000), Hirelings-A (12:35:07, 146/4000), Hirelings-B (12:34:45, 103/4000), Forklings (12:07:30, 1054/8000), Auspibots (12:17:44, 163/4000), Neurolucha (11:48:07, 455/4000), PERSONA (01:14:41, 1155/3333) — semuanya first mint terverifikasi >48 jam (48,2-60,0 jam) dan belum sold out per bacaan segar blok 132148622 -> DIHAPUS dari kontrak aktif, dipindah ke excluded (status excluded-age-over-48h-2026-11-07). "
 "DIPERTAHANKAN: semua minted-by-user (grandfathered), semua promotion-discarded-same-owner (penanda discard-suppression, preseden run 1401), semua sold-out (pengecualian aturan 48 jam), semua watchlist-only latar belakang yang launch-nya UNVERIFIED (tanpa first mint terverifikasi; first-seen block saja bukan vonis hapus untuk tier itu). "
 "DINOBYTE + KALOS CODE juga masuk excluded run ini (lihat entri masing-masing; DINOBYTE umur ~139,7 jam, KALOS free lane habis).")
snap["runNote1231_binanceai"]=(
 "Run 1231: BINANCEAI launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, tokenBalance(user)=0 - tetap refund/failed, pending_claims kosong, tidak dilaporkan ulang.")
snap["last_run_note"]=snap["runNote1231_1107"]

with open(f"{BASE}/onchain-snapshot.json.tmp","w") as f:
    json.dump(snap,f,indent=1)
os.replace(f"{BASE}/onchain-snapshot.json.tmp", f"{BASE}/onchain-snapshot.json")
print(f"FINALIZE DONE updated={updated} none_free_views={none_free} removed={len(removed)} contracts_now={len(snap['contracts'])} excluded_now={len(snap.get('excluded',{}))}")
