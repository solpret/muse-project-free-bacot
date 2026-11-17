#!/usr/bin/env python3
"""Merge run 2026-11-09 00:31 WIB. Read-only on-chain done; this writes snapshot + seen + checked files.
Backfill may write the snapshot concurrently: reload fresh, apply changes on top, never clobber new entries."""
import json, shutil, copy
from datetime import datetime, timezone, timedelta
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB=timezone(timedelta(hours=7))
NOW=datetime.now(WIB)
NOW_STR=NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL=51.02
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0031-premerge")
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
rr=json.load(open(f"{BASE}/run-2026-11-09-0031-reread.json"))
C=s["contracts"]; TC=s.get("track_c",{})
NEW_BLOCK=rr.get("block")
updated=0; degraded=0; vel_pass=[]
for name,e in C.items():
    r=rr["reread"].get(name)
    if r is None: continue
    prev_sup=e.get("totalSupply"); new_sup=r.get("totalSupply")
    if new_sup is None:
        degraded+=1
        note=f"Run 0031 (blok {NEW_BLOCK}, 00:48 WIB): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
    else:
        minted=None; rate=None; ratio=None; vpass=False
        if prev_sup is not None:
            minted=new_sup-prev_sup
            rate=minted/INTERVAL
            prev_rate=float(e.get("currentRatePerMin") or e.get("ratePerMin") or 0) or 0.0
            if prev_rate>0: ratio=rate/prev_rate
            vpass=bool(minted>=20 and prev_rate>0 and ratio is not None and ratio>=1.5)
            if vpass: vel_pass.append((name,minted,round(rate,4),round(prev_rate,4),round(ratio,2)))
            e["previousTotalSupply"]=prev_sup; e["mintedInInterval"]=minted
            e["intervalMinutes"]=INTERVAL; e["currentRatePerMin"]=rate
            e["previousRatePerMin"]=prev_rate; e["velocityRatio"]=ratio
            e["velocityLegPasses"]=vpass
        e["totalSupply"]=new_sup
        note=f"Run 0031 (blok {NEW_BLOCK}, 00:48 WIB): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen"):
        if r.get(k) is not None: e[k]=r[k]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"]=r["balanceOf_user"]; e["balanceOf_user"]=r["balanceOf_user"]
    e["lastReadBlock"]=NEW_BLOCK; e["lastReadWib"]="2026-11-09 00:48 WIB"
    e["runNote0031_1109"]=note+f"free={e.get('freeClaimed')}/{e.get('FREE_SUPPLY')}; bal_user={e.get('balanceOf_user')}; status {e.get('status')}."
    updated+=1
# track_c updates
tc_updated=0
for name,e in TC.items():
    if not isinstance(e,dict): continue
    r=rr["track_c"].get(name)
    if r is None: continue
    if r.get("freeMinted") is not None: e["freeMinted"]=r["freeMinted"]
    if r.get("totalSupply") is not None: e["totalSupply"]=r["totalSupply"]
    e["runNote0031_1109"]=f"Run 0031: freeMinted={e.get('freeMinted')}, totalSupply={e.get('totalSupply')} (blok {NEW_BLOCK})."
    tc_updated+=1
# --- Age exclusion: ONLYAI-Crystals (launch stated 2026-11-07 01:00 WIB; >48h at merge ~01:30 WIB; not sold out 2013/5555) ---
removed=[]
if "ONLYAI-Crystals" in C:
    e=C.pop("ONLYAI-Crystals")
    s.setdefault("age_exclusions",[]).append({
        "name":"ONLYAI-Crystals","address":e.get("address"),
        "mintStartWib":"2026-11-07 01:00 WIB","ageHours":"~48,5",
        "evidence":"Launch TERVERIFIKASI: waktu buka dinyatakan proyek sendiri (Boltbook ZH run 0131: buka 2026-11-07 01:00 WIB / 6 Nov 18:00 UTC; totalSupply masih 0 sebelum buka). Umur melewati 48 jam ~01:00 WIB 2026-11-09 (diantisipasi run 2331); pada merge run 0031 (~01:30 WIB) umur ~48,5 jam.",
        "supply":2013,"maxSupply":5555,"free":"free views None (tidak ada freeClaimed view di kontrak)",
        "status_before":e.get("status"),"removed_run":"2026-11-09 run 0031",
        "removed_wib":NOW_STR,
        "reason":"Umur peluncuran terverifikasi ~48,5 jam (>48 jam) dan belum sold out (2013/5555); dihapus dari watchlist aktif per aturan umur 48 jam; dilaporkan sekali run ini."})
    removed.append("ONLYAI-Crystals")
# --- Bonejestra: seen-only age exclusion (never in snapshot, never reported as lead) ---
s.setdefault("age_exclusions",[]).append({
    "name":"Bonejestra","address":"0xcaa6554463a98f9afc966175694cd81ac7c41b41",
    "firstMintWib":"<=2026-11-02 ~12:44 WIB (batas atas: pre-window mints ditemukan run 1301 2026-11-02; 63/770 saat itu)",
    "ageHours":"~156+",
    "evidence":"Run 1301 2026-11-02: Bonejestra 63/770=8,18%, pre-window mints (blok <131187511) ditemukan sehingga first-seen minting TIDAK terverifikasi; tidak pernah masuk snapshot / tidak pernah dilaporkan sebagai lead. Bacaan segar run 0031: totalSupply 561, freeClaimed 548/770=71,2%, MAX 963, mintOpen 1, balanceOf(user)=0.",
    "supply":561,"maxSupply":963,"free":"548/770 = 71,2%",
    "status_before":"seen-only (first-seen scan run 1301, tidak pernah masuk snapshot / tidak pernah dilaporkan sebagai lead)",
    "removed_run":"2026-11-09 run 0031",
    "reason":"Umur peluncuran TERVERIFIKASI >48 jam (first mint pada/sebelum 2026-11-02 ~12:44 WIB, umur ~156+ jam) dan belum sold out (561/963) -> AGE-EXCLUDED per aturan umur 48 jam; bukan lead/kandidat; tidak dilaporkan ke chat (hanya dicatat, preseden PIXEL BOYZ run 1831 / BAYC sale run 1801). Boltbook 2026-11-09 00:47 WIB me-recheck-nya (554/963) seolah baru - arsip run 1301 membuktikan sebaliknya."})
# --- Dragon Agent early lead ---
C["Dragon Agent"]={
    "address":"0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6",
    "status":"early-lead-reported-2026-11-09-0031",
    "name":"Dragon Agent","symbol":"DAGENT","kind":"ERC721",
    "totalSupply":124,"MAX_SUPPLY":3330,"mintOpen":None,
    "freeSlotUserOpen":True,
    "firstSeenBlock":132435150,"firstMintWib":"2026-11-09 00:47:35 WIB",
    "scanWindow":"132435007-132436006","scanMints":10,"scanMinters":10,
    "lastReadBlock":132436006,"lastReadWib":"2026-11-09 01:20 WIB",
    "xVerified":False,"velocityVerified":False,
    "launchNote":"First mint VERIFIED on-chain: blok 132435150 = 2026-11-09 00:47:35 WIB (scan window run 0031, 10 mint/10 minter); walk-back Ankr chain-wide 3000 blok sebelumnya (132432007-132435006, 11.571 log) = 0 mint Dragon Agent. Umur ~33 mnt saat verifikasi - TERVERIFIKASI <=48 jam.",
    "baselineNote":"EARLY lead dilaporkan sekali run 0031. Agent-shaped: Sourcify exact_match (verifiedAt 2026-11-08T17:42:58Z), REGISTRY() persis 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, agentGate()=1, FREE_COUNT()=1, mint + priceOf + canMint. Free path: priceOf(user,1)=0, canMint(user)=1, mintedBy(user)=0, balanceOf(user)=0 (slot TERBUKA); price()=0,000475 BNB (paid lane). Free% UNVERIFIED (tanpa freeClaimed/freeMinted view; FREE_COUNT()=1 kemungkinan jatah free per wallet, bukan pool). X unverified, website unverified, velocity belum terhitung. BUKAN strong lead (free% unverified) dan BUKAN kandidat. TIDAK PERNAH di-preview/di-mint sebagai early lead.",
    "userSlotNote":"Slot TERBUKA: priceOf(user,1)=0, canMint(user)=1, mintedBy(user)=0, balanceOf(user)=0 (baca segar run 0031).",
    "runNote0031_1109":"Run 0031: EARLY LEAD baru - dilaporkan sekali. 10 mint/10 minter di window scan, first mint 00:47:35 WIB terverifikasi (walk-back 3000 blok = 0 mint).",
}
# --- seen file: Dragon Agent + scan window contracts ---
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc=json.load(open(f"{BASE}/run-2026-11-09-0031-scan.json"))
added=0
for c in sc.get("contracts",[]):
    a=(c.get("address") or "").lower()
    if a and a not in seen.get("contracts",{}):
        seen.setdefault("contracts",{})[a]=c.get("first_block") or sc.get("from_block")
        added+=1
seen.setdefault("_meta",{})["note_0031"]=("Run 0031: scan FULL 132435007-132436006 (partial=false, 40 Ankr calls, 0 error, 93 NFT + 264 ERC-20-mint); "
    f"{added} first-seen appended ke seen['contracts'] (Dragon Agent EARLY LEAD + {added-1} lainnya sudah dikenal/di-snapshot). Watermark TIDAK dimajukan (milik backfill).")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json","w"), indent=1)
# --- track-c-scan-checked.json: 1 newly checked ---
chk=json.load(open(f"{BASE}/track-c-scan-checked.json"))
if isinstance(chk,dict):
    chk["0x48c7671b5e5eD878c8372C4186B4D8A9024Bd47F"]={"run":"2026-11-09-0031-5c","mint_count":21,"shape":"checked-not-sale-shape"}
    json.dump(chk, open(f"{BASE}/track-c-scan-checked.json","w"), indent=1)
# --- top-level run note ---
s["runNote0031_1109"]=(
    f"Run 0031 (00:31 WIB 9 Nov - {NOW_STR}): re-read blok {NEW_BLOCK} (00:48 WIB, interval 51,02 mnt vs blok 132428482 23:57 WIB): {updated} kontrak + {tc_updated} track_c, 0 batch_fail, {degraded} totalSupply=None degraded (nilai lama dipertahankan, bukan nol). "
    "Velocity strict: 0 lolos (>=1,5x DAN >=20 token), 0 promosi. "
    "Scan leg FULL (pre-flight OK 2,6 dtk, head 132435842; window 132435007-132436006, 1000 blok cap, 40 Ankr calls, 0 error, partial=false; 93 NFT + 264 ERC-20-mint; skipped gap 132430438-132435006 milik backfill; watermark TIDAK dimajukan). "
    "EARLY LEAD BARU: Dragon Agent (DAGENT) 0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6 - first mint 00:47:35 WIB terverifikasi (walk-back 3000 blok = 0 mint), REGISTRY() persis + agentGate()=1 + FREE_COUNT()=1, priceOf(user,1)=0 slot terbuka; free% unverified - dilaporkan sekali. "
    "Sourcify feed: 4 kontrak baru sejak hot-leg 00:34, 0 sale-shape (0x73F5/0xaa87/0x91b9/0xF086). 5c: 1 baru dicek (0x48c7...), 0 hit S1/S2. "
    "Boltbook EN+ZH: Bonejestra recheck 554/963 - arsip run 1301 membuktikan first mint <=2026-11-02 ~12:44 WIB (umur ~156+ jam) -> age-excluded seen-only, tanpa laporan chat; BMT free lane CLOSED 1000/1000 (tidak di snapshot); Pokechain 15.061/15.555 (belum sold out); Abyssagent sold out (sudah discarded); Erupt Genesis upcoming (buka 9 Nov ~21:59 WIB). "
    "FF 692/696 + VV 664/675 (belum sold out, gate FAILED tetap). Lucky Cat flat 5 (free views None run ini, nilai lama dipertahankan). "
    "Binanceai tetap refund phase (launched=0, failed=1, isRefundPhase=1). Bridge: 116 kontrak, 0 baru. "
    "Age-exclusion: ONLYAI-Crystals dihapus (launch 2026-11-07 01:00 WIB, umur ~48,5 jam, 2013/5555 belum sold out) - dilaporkan sekali. "
    "0 kandidat, 0 auto-mint.")
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print(f"MERGE DONE updated={updated} degraded={degraded} tc={tc_updated} vel_pass={len(vel_pass)} removed={removed} seen_added={added}")
print("contracts now:", len(s["contracts"]))
