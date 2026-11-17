import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
re=json.load(open(f"{BASE}/run-2026-11-07-1131-reread.json"))
vel=json.load(open(f"{BASE}/run-2026-11-07-1131-velocity.json"))
BLOCK=re["block"]
vrows={r["name"]:r for r in vel["rows"]}
n_upd=0; n_noread=0
for name,d in re["reread"].items():
    s=snap["contracts"].get(name)
    if s is None: continue
    cur=d.get("totalSupply")
    if cur is None: cur=d.get("totalMinted")
    if isinstance(cur,int):
        s["previousTotalSupply"]=s.get("totalSupply")
        s["totalSupply"]=cur
        s["lastReadBlock"]=BLOCK
        s["lastReadWib"]="2026-11-07 run 1131"
    else:
        n_noread+=1
    vr=vrows.get(name)
    if vr:
        s["mintedInInterval"]=vr.get("mintedInInterval")
        s["intervalMinutes"]=vr.get("intervalMin")
        s["currentRatePerMin"]=vr.get("ratePerMin")
        s["previousRatePerMin"]=vr.get("prevRatePerMin")
        s["velocityLegPasses"]=vr.get("velocityPasses")
        if vr.get("freePct") is not None:
            s["freePctInference"]=vr["freePct"]
    n_upd+=1
# SEAT-f11e newly sold out (5000/5000; was 4977 at 1101). Watchlist-only, never reported as lead -> status update only, no chat report.
seat=snap["contracts"].get("SEAT-f11e")
if seat is not None:
    seat["status"]="sold-out-2026-11-07"
    seat["runNote1131"]="Run 1131: totalSupply 4977 -> 5000/5000 MAX_SUPPLY 5000 = SOLD OUT. Status watchlist-only-boltbookfun (never reported as lead; free views revert, age/website unverified) -> no chat report, status updated only."
# track_c last-read stamps
for name,d in re.get("track_c",{}).items():
    t=snap.get("track_c",{}).get(name)
    if isinstance(t,dict):
        t["lastReadBlock"]=BLOCK
        t["lastReadWib"]="2026-11-07 run 1131"
# MoonAgent fresh re-check (block 132142291): totalMints 92/800 (was 41), slot still open, quote 0 -> NO state change vs hot-leg gate-blocked report 11:52 -> NO re-report.
mo=snap.get("track_c",{}).get("MoonAgent-MOAGT")
if isinstance(mo,dict):
    mo["totalMints"]=92
    mo["lastCheckBlock"]=132142291
    mo["lastCheckWib"]="2026-11-07 run 1131"
    mo["runNote1131"]="Run 1131 re-check block 132142291: totalMints 41 -> 92/800, mintOpen 1, freeLeft(user)=1, mintedBy(user)=0, balanceOf(user)=0, quote(user,1)=0. Slot still open, no sellout -> NO state change vs hot-leg gate-blocked report 11:52 WIB -> NO re-report."
# Tacotron age-excluded (corrected): first mint on-chain Nov 1 ~13:0x WIB (blocks 130997680-130999050), NOT Nov 7 04:24 as hot-leg verify2 concluded from a wrong 48h cutoff block (assumed 3 s/block; real rate ~0.46 s/block). Age ~6 days > 48h, not sold out (6587/7000 free) -> excluded, never a lead, never reported.
snap.setdefault("excluded",{})["Tacotron"]={
 "address":"0x05debe4445232205ae7e79d02cb5de5aa0641eff",
 "name":"Tacotron","symbol":"TACOTRON","track":"A",
 "status":"excluded-age-over-48h-2026-11-07",
 "note":"First mint on-chain block 130997680-130999050, 2026-11-01 ~13:0x WIB (Transfer-from-zero logs; tokenIds 1799-1801 at 130999050, 2026-11-01 13:13:37 WIB; more mints earlier in [120000000,130999000]). Age ~6 days at run 1131, OVER 48h, not sold out (freeClaimed 6587/7000 = 94.1%, mintOpen 1, user slot open freeLeft=3 quote=0). CORRECTION: hot-leg 1134 verify2 concluded age <=48h from first-mint 132080186 (Nov 7 04:24) using cutoff block 132080731 computed at 3 s/block; BSC real rate ~0.46 s/block makes that cutoff only ~7.5h, not 48h. True 48h cutoff is ~block 13176xxxx. contractURI (base64 JSON) names .ai Agent ID gating but carries NO website URL; gate (A)-(N) not completed because age excludes first. NOT a strong lead, NOT a candidate, NOT previewed/minted, NOT reported as a lead."
}
snap["runNote1131_1107"]=("Run 1131: 0 kandidat, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat baru, 0 pending claim baru/dibuka. "
 "Preflight PASS 0,9 dtk. Reread 463 kontrak + 59 track_c, blok 132140322, 548,9 dtk; 100 kontrak tanpa supply read (degradasi eth_call, sama seperti hot-leg 1109/1114/1129). "
 "Velocity 2 pass (Horus AI +223 ratio 6,96; bridge-0x4673c787 +67 ratio 13,36) - keduanya freePct None -> BUKAN kandidat/strong lead. "
 "Sold out 35 (baru: SEAT-f11e 5000/5000, watchlist-only, tidak pernah dilaporkan -> status update saja, tanpa laporan); near-sellout Dumpster Royalty 632/650. "
 "Scan SUKSES window 132139323-132140322 (1000 blok, cap), 116 NFT + 252 ERC-20 mint, 40 Ankr calls, 0 error; 0 first-seen sejati (semua sudah di seen/snapshot). Gap 132135866-132139322 (3457 blok) dilewati cap, ditutup backfill. "
 "Sourcify feed 20 kontrak (verifiedAt 04:31-04:56 UTC), 1 shape hit = MoonAgent (sudah dikenal). 5c: 44 ERC-20 mint_count>=10, 1 baru dicek (0x00c016d4...), 0 shape hit. "
 "Boltbook KEMBALI (EN/ZH 200, ~46KB): 12 alamat unik, 6 baru vs snapshot, 0 shape hit. Sweep rute 3: tanpa proyek baru (hasil lama Okt 26-28). Komplemen: Odaily + PANews tanpa pengumuman Agent ID free-mint. Bridge: tidak berubah (115 entri, 7 discarded), 0 promosi. Pending claims kosong; BINANCEAI tetap refund/failed. "
 "MoonAgent: re-check blok 132142291 totalMints 92/800, slot user tetap terbuka, quote 0 - TANPA perubahan vs laporan gate-blocked hot-leg 11:52 WIB -> TIDAK dilaporkan ulang. "
 "KOREKSI UMUR Tacotron (0x05debe44...): first mint ~2026-11-01 13:0x WIB (bukan 2026-11-07 04:24) -> umur ~6 hari > 48 jam -> AGE-EXCLUDED, dicatat di snapshot excluded, tidak pernah jadi lead/kandidat, tidak dilaporkan. Penyebab salah hitung hot-leg: cutoff 48 jam dihitung dengan 3 dtk/blok, padahal laju nyata ~0,46 dtk/blok.")
snap["last_run"]="2026-11-07-1131"
snap["last_run_wib"]="2026-11-07 11:31 WIB (dieksekusi ~11:49-12:40 WIB)"
snap["last_run_note"]=snap["runNote1131_1107"]
snap["timestamp_wib"]="2026-11-07 11:31 WIB"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("contracts updated:", n_upd, "no-read:", n_noread)
print("track_c keys:", len(snap["track_c"]))
# scan state
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"]=132140322
st["last_scan_window_from"]=132139323
st["last_scan_window_to"]=132140322
st["last_scan_wib"]="run 2026-11-07-1131"
st["note_1131_scan"]="Run 1131 SUKSES window 132139323-132140322 (1000 blok, cap), 116 NFT + 252 ERC-20 mint, 40 Ankr calls, 0 error; 0 first-seen sejati. Skipped gap 132135866-132139322 (3457 blok, window > cap) ditutup backfill. Preflight PASS 0,9 dtk."
json.dump(st, open(f"{BASE}/onchain-scan-state.json","w"), indent=1)
print("scan state updated -> 132140322")
