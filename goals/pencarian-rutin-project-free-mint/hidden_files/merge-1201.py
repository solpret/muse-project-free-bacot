import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
re=json.load(open(f"{BASE}/run-2026-11-07-1201-reread.json"))
vel=json.load(open(f"{BASE}/run-2026-11-07-1201-velocity.json"))
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
        s["lastReadWib"]="2026-11-07 run 1201"
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
# track_c last-read stamps (only items actually read)
for name,d in re.get("track_c",{}).items():
    t=snap.get("track_c",{}).get(name)
    if isinstance(t,dict):
        t["lastReadBlock"]=BLOCK
        t["lastReadWib"]="2026-11-07 run 1201"
# MoonAgent fresh re-check (block 132145622): totalMints 113/800 (was 92 at 1131), slot still open, quote 0 -> NO state change vs hot-leg gate-blocked report 11:52 -> NO re-report.
mo=snap.get("track_c",{}).get("MoonAgent-MOAGT")
if isinstance(mo,dict):
    mo["totalMints"]=113
    mo["lastCheckBlock"]=132145622
    mo["lastCheckWib"]="2026-11-07 run 1201"
    mo["runNote1201"]="Run 1201 re-check block 132145622: totalMints 92 -> 113/800, mintOpen 1, freeLeft(user)=1, mintedBy(user)=0, balanceOf(user)=0, quote(user,1)=0. Slot still open, no sellout -> NO state change vs hot-leg gate-blocked report 11:52 WIB -> NO re-report."
# Pathwyrm EARLY LEAD (found via Sourcify feed by hot-leg 1204; verified on-chain by hot-leg 1204 + main run 1201).
snap["contracts"]["Pathwyrm"]={
 "address":"0xf100c608913dC07ed268bEA865Fca10004f04657",
 "status":"early-lead-2026-11-07",
 "track":"A",
 "saleShape":"S1: mint(uint256)+quote(address,uint256)+freeClaimed/freeFor/freeLeft/freeUsed + AGENT_ID registry ref (agentIdRequired), Sourcify verified",
 "totalSupply":107,
 "freeClaimed":104,
 "FREE_SUPPLY":1479,
 "MAX_SUPPLY":2114,
 "freePct":7.03,
 "mintOpen":1,
 "PRICE":80000000000000,
 "FREE_PER_WALLET":1,
 "MAX_PER_WALLET":50,
 "AGENT_ID":552192074493313695968015109214105588393044541999,
 "agentIdRequired":1,
 "freeLeft_user":1,
 "freeUsed_user":0,
 "mintedBy_user":0,
 "balanceOf_user":0,
 "quote_user1":0,
 "firstMintWib":"2026-11-07T05:12:32+07:00",
 "firstMintBlock":132086587,
 "ageHoursAtVerify":7.05,
 "ageLe48h":True,
 "lastReadBlock":132144005,
 "lastReadWib":"2026-11-07 run 1201",
 "websiteGate":"unverified (contractURI base64 JSON names .ai Agent ID gating, NO URL - method H; contract-address search (A) no hit; project-name search (G) no Pathwyrm site; tokenURI(1) on-chain SVG only, no external URL - method I)",
 "xDiscussion":"unverified (no public discussion found in run 1201)",
 "velocityLegPasses":None,
 "baselineNote":"EARLY LEAD run 1201: agent-shaped S1, first mints verified on-chain (first mint block 132086587, 2026-11-07 05:12:32 WIB, age ~7h <= 48h). Free 104/1479 = 7.0% < 25% strong-lead threshold -> EARLY, not strong lead, not candidate. User slot open (freeLeft=1, quote=0). Velocity unverified (first run, no baseline). Website + X unverified (see websiteGate). Reported ONCE as EARLY lead in run 1201 chat report; added to snapshot for velocity tracking. NEVER auto-mint/preview as early lead; promotes to strong lead only on 3 strong legs + website gate."
}
snap["runNote1201_1107"]=("Run 1201: 1 EARLY lead baru (Pathwyrm 0xf100c608913dC07ed268bEA865Fca10004f04657); 0 kandidat, 0 strong lead baru, 0 track-C lead/kandidat baru, 0 pending claim baru/dibuka. "
 "Preflight PASS 5,6 dtk (head 132143447). Reread 463 kontrak + 59 track_c, blok 132143896, 725,7 dtk; 100+ kontrak tanpa supply read (degradasi eth_call, sama seperti run 1131). "
 "Velocity 1 pass (bridge-0x4673c787 +140 ratio 2,63) - freePct None -> BUKAN kandidat/strong lead; Horus AI turun dari pass (ratio 0,86), tetap early. Sold out 35 (sama seperti 1131, 0 baru); near-sellout Dumpster Royalty 633/650 (+1). Slot changes 0. "
 "Agent Goats totalSupply 537 -> 540, deadline umur 12:55:17 WIB, free views tak terbaca, tanpa perubahan. Hotpotsage 735 -> 739 (balanceOf user 1). Hackagent 4092 -> 4096. "
 "Scan SUKSES window 132142486-132143485 (1000 blok, cap), 177 NFT + 327 ERC-20 mint, 40 Ankr calls, 0 error, partial=False, 19,3 mnt; 0 first-seen sejati. Gap 132140323-132142485 (2163 blok) dilewati cap, ditutup backfill. "
 "Sourcify feed 20 kontrak (verifiedAt 04:50-05:17 UTC): 2 shape hit - Pathwyrm/f100 (EARLY, di atas) + Agent Souls 0x0343B150 (S1 tapi SAME-OWNER-DISCARD dari triage backfill ~11:05 WIB -> log only, TIDAK dipromosikan/dilaporkan). 2 kontrak baru lain (0xa73E..., 0xf656...) mint+quote tapi TANPA free view -> S1=False. "
 "5c: 45 ERC-20 mint_count>=10, 1 baru dicek (0xb3bDB792...), 0 shape hit; track-c-scan-checked.json 2344 -> 2345. "
 "Boltbook EN+ZH kembali (46,4 KB): 11 alamat unik, 4 baru vs snapshot, 0 shape hit. Sweep rute 3: tanpa proyek baru (hasil lama Okt 26-28; AGENT MAO paused; Agent Periodic Lab + Subsonic sudah di snapshot). "
 "Komplemen: Odaily newsflash + PANews tanpa pengumuman Agent ID free-mint; Binance Square via search-index tanpa site link baru; DappBay tidak ada proyek untuk dicek. Bridge: tidak berubah (115 entri, 7 same_owner_discarded, terakhir diubah 2026-11-06 02:48), 0 promosi/perubahan. Pending claims kosong; BINANCEAI tetap refund/failed. "
 "MoonAgent: re-check blok 132145622 totalMints 92 -> 113/800, mintOpen 1, freeLeft(user)=1, quote(user,1)=0 - TANPA perubahan vs laporan gate-blocked hot-leg 11:52 WIB -> TIDAK dilaporkan ulang. "
 "a900 (hot-leg 1229 S1 baru, 0xa900873E65B5F391B6E37d80a98A6b26D07613B8): verifikasi on-chain run 1201 blok 132146413 - totalMints 45/700, mintOpen 1, freeLeft(user)=1, quote(user,1)=0, AGENT_ID=registry, FACTORY 0xca14... sama dengan MoonAgent; umur dalam verifikasi (lihat age-a900-1201 / run log).")
snap["last_run"]="2026-11-07-1201"
snap["last_run_wib"]="2026-11-07 12:01 WIB (dieksekusi ~12:16-12:45 WIB)"
snap["last_run_note"]=snap["runNote1201_1107"]
snap["timestamp_wib"]="2026-11-07 12:01 WIB"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("contracts updated:", n_upd, "no-read:", n_noread)
print("track_c keys:", len(snap["track_c"]))
# scan state
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"]=132143485
st["last_scan_window_from"]=132142486
st["last_scan_window_to"]=132143485
st["last_scan_wib"]="run 2026-11-07-1201"
st["note_1201_scan"]="Run 1201 SUKSES window 132142486-132143485 (1000 blok, cap), 177 NFT + 327 ERC-20 mint, 40 Ankr calls, 0 error, partial=False, ~19,3 mnt (enrichment lambat: 177 kontrak). 0 first-seen sejati. Skipped gap 132140323-132142485 (2163 blok, window > cap) ditutup backfill. Preflight PASS 5,6 dtk."
json.dump(st, open(f"{BASE}/onchain-scan-state.json","w"), indent=1)
print("scan state updated -> 132143485")
