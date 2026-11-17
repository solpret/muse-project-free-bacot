#!/usr/bin/env python3
"""Snapshot update for free-mint-search run 2026-11-14 00:01 WIB.
Merges run-2026-11-14-0001-verify.json + -retry.json + -probe-new.json
into onchain-snapshot.json (fresh read, then write). No preview/mint.
Backup saved as onchain-snapshot.json.bak-0001 first."""
import json, shutil, subprocess, os
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
_env=dict(os.environ); _env["TZ"]="Asia/Jakarta"
NOW=subprocess.check_output(["date","+%Y-%m-%d ~%H:%M WIB"],env=_env).decode().strip()
LAST_RUN=subprocess.check_output(["date","+%Y-%m-%dT%H:%M+07:00"],env=_env).decode().strip()
shutil.copy(BASE+"onchain-snapshot.json", BASE+"onchain-snapshot.json.bak-0001")
print("NOW:", NOW)
snap=json.load(open(BASE+"onchain-snapshot.json"))
verify=json.load(open(BASE+"run-2026-11-14-0001-verify.json"))
retry=json.load(open(BASE+"run-2026-11-14-0001-retry.json"))
probe=json.load(open(BASE+"run-2026-11-14-0001-probe-new.json"))
READS={}
for src in (verify,retry,probe):
    for k,v in src["reads"].items():
        if v.get("views") is not None: READS[k]=v
VB=verify.get("block")
RB=retry.get("block")  # 133394739
PB=probe.get("block")  # 133391930
def norm(a): return (a or "").lower()
updated=[]
for key,ent in snap.get("contracts",{}).items():
    a=norm(ent.get("address"))
    hit=None
    for rk,rv in READS.items():
        if norm(rv.get("address"))==a and a:
            hit=(rk,rv); break
    if not hit: continue
    rk,rv=hit
    views=rv["views"]
    for fk,fv in views.items():
        if fk in ("name","symbol"):  # probe-new returns raw ints for strings; never merge
            continue
        if fv is not None: ent[fk]=fv
    ent["lastReadBlock"]= RB if rk in retry.get("reads",{}) else (PB if rk in probe.get("reads",{}) else VB)
    ent["lastReadWib"]=NOW
    updated.append(key)
print("generic-merged:",len(updated), "block RB:", RB)
def note(key,text):
    ent=snap["contracts"].get(key)
    if ent is not None: ent["runNote0001"]=text
    else: print("NOTE-MISS:", key)
# interval 2331->0001: blok 133388727 -> 133394739 = 6012 blok ~ 45,1 mnt chain-time
note("Crown Racer Cards","Run 0001: totalSupply 299->405 (+106), freeMinted 403/500 = 80,6% (>70%), freeClaimed(user)=0 slot TERBUKA, mintOpen 1. Rate 2,35/mnt = baseline pertama (tanpa prev rate -> velocity TIDAK dihitung lolos). Umur TETAP UNVERIFIED: semua view waktu (saleStart/mintStart/startTime/launchTime/freeStart) null/revert; verifiedAt Sourcify 23:03 WIB BUKAN launch time. Bukan strong lead (umur unverified), bukan kandidat. Website/X UNVERIFIED. Tetap early-lead-reported. DIAM.")
note("Race Agents","Run 0001: totalSupply 323->348 (+25), freeMinted 348/1000 = 34,8%, mintOpen 1, balanceOf 0. Rate 0,55/mnt = baseline pertama (tanpa prev rate -> velocity TIDAK dihitung lolos). Umur TETAP UNVERIFIED (first-seen bound ~20:25 WIB). Bukan strong lead/kandidat. DIAM.")
note("Cinder Crucible","Run 0001: totalSupply 221->316 (+95), freeMinted 316/325 = 97,2%, freeRemaining 9, mintOpen 1. Rate 2,11/mnt vs prev 0,0 -> rasio tak terhitung, velocity TIDAK dihitung lolos. Status lead-gate-blocked (dilaporkan hot-leg 23:51 WIB); BELUM sellout (9 free tersisa), slot diasumsikan terbuka. Bukan sellout/slot-lost -> TIDAK re-report. DIAM.")
note("Early5877","Run 0001: totalMinted 257->363 (+106), MAX_SUPPLY 10000, mintOpen 1. QUIZ-GATED (sudah dilaporkan run 2231). Rate 2,35/mnt baseline pertama. DIAM.")
note("Moon","Run 0001: totalMinted 452->488 (+36), MAX_SUPPLY 3333, mintOpen 1. Rate 0,80/mnt baseline pertama; free% UNVERIFIED. Bukan kandidat. DIAM.")
note("RoyalRush","Run 0001: totalSupply 897->916 (+19, <20) -> velocity GAGAL; freeMinted 919/1000 = 91,9% (free>totalSupply: counter tidak konsisten, dicatat apa adanya); umur TETAP UNVERIFIED. Bukan strong lead/kandidat. DIAM.")
note("OBFG","Run 0001: totalSupply 707->720 (+13, <20) -> velocity GAGAL; free 720/1230 = 58,5%. AGE-EXCLUDED. DIAM.")
note("JNTM","Run 0001: totalMinted 1202->1212 (+10). Free pool TETAP habis. DIAM.")
note("MECHA","Run 0001: totalMinted 1969->1978 (+9, <20) -> velocity GAGAL. DIAM.")
note("MORFO","Run 0001: totalMinted 455->464 (+9, <20) -> velocity GAGAL; free% UNVERIFIED; umur launch tepat UNVERIFIED. Tetap early-lead-reported. DIAM.")
note("Zero","Run 0001: totalMinted 307->315 (+8, <20) -> velocity GAGAL; freeMinted 315/500 = 63,0% (<70%), slot terbuka; deadline umur 07:55 WIB 14 Nov. Bukan strong lead. DIAM.")
note("FERO","Run 0001: totalMinted 13->19 (+6), window buka 23:00 WIB 13 Nov; free% ~19/3333 = 0,6%. Bukan kandidat/strong lead/early. Tetap watchlist-only. DIAM.")
note("Fossil Drawer","Run 0001: totalSupply 1121->1124 (+3), freeMinted 1111, FREE_SUPPLY 1111, MAX_SUPPLY 5555, mintOpen 1, balanceOf(user)=1. Status minted-by-user-2026-11-10. Website terverifikasi fossildrawer.surge.sh. DIAM.")
note("Cobalt Agent","Run 0001: totalSupply 4900 FLAT (Boltbook recheck 00:20 WIB: 4.900/5.000 = 98,0% cocok), mintOpen null, balanceOf 0. Umur TETAP UNVERIFIED (Sourcify 404). Bukan strong lead. DIAM.")
note("HIVE Agents","Run 0001: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("AgentMuse","Run 0001: tidak terbaca ulang run ini (verify views null; nilai snapshot dipertahankan). Deadline umur 05:53 WIB 14 Nov. DIAM.")
note("Mossbound Key","Run 0001: totalSupply 327 FLAT, freeMinted 325/325 = 100% sold out (sudah dilaporkan). DIAM.")
note("Ochre Medallion","Run 0001: totalSupply 211 FLAT, freeMinted 210/210 = 100% sold out (sudah dilaporkan). DIAM.")
note("BUILD","Run 0001: totalMinted 204->206 (+2), freeMinted 200/200 = 100% free pool habis, freeClaimed(user)=1. Minted-by-user. DIAM.")
note("SKRR","Run 0001 (retry): totalSupply 518 FLAT, MAX_SUPPLY 1682, mintOpen 1, costOf(user,1)=0. DIAM.")
note("HANAMI","Run 0001 (retry): totalSupply 130->132 (+2), freeMinted 130, MAX_SUPPLY 3333. DIAM.")
note("UNRES1","Run 0001 (retry): totalSupply 128 FLAT, freeMinted 128, mintOpen 1. Tidak masuk snapshot (identitas belum jelas). DIAM.")
# velocity baselines for movers (rate per menit, interval ~45,1 mnt)
rates = {"Crown Racer Cards": 2.35, "Race Agents": 0.55, "Cinder Crucible": 2.11,
         "Early5877": 2.35, "Moon": 0.80, "RoyalRush": 0.42, "OBFG": 0.29,
         "JNTM": 0.22, "MECHA": 0.20, "MORFO": 0.20, "Zero": 0.18, "FERO": 0.13}
for k, r in rates.items():
    ent = snap["contracts"].get(k)
    if ent is not None:
        ent["previousRatePerMin"] = r
        ent["currentRatePerMin"] = r
        ent["velocityLegPasses"] = False
# Voxel Sector: age-excluded (first mint 12 Nov 15:24 WIB, blok 133127657, tx Boltbook)
snap["contracts"]["Voxel Sector"] = {
    "address": "0x2c93e68462f0d20ccc54a19d39d9ed25d9f3b9be",
    "name": "Voxel Sector", "symbol": "PX23", "kind": "ERC721",
    "status": "age-excluded-2026-11-14",
    "totalSupply": 276, "MAX_SUPPLY": 1689, "mintOpen": 1, "balanceOf_user": 0,
    "agentShaped": True,
    "firstSeenWib": "2026-11-14 ~00:44 WIB (Boltbook ZH front page)",
    "launchNote": "AGE-EXCLUDED: mint pertama terverifikasi 2026-11-12 15:24 WIB (blok 133127657, tx 0x1762bb065a068659c860df924d7f35e0a591680337b72ca6ca3f48e76e4e4f95, bukti tx dari postingan Boltbook sendiri; receipt status 1, to = kontrak ini) -> umur ~33 jam > 24 jam. Agent-shaped (registry bytes 0x60B9...022F di bytecode, code 7.398 byte); free views null (free% UNVERIFIED); website/X UNVERIFIED. Dicatat diam sebagai age-excluded (preseden run 2201), TIDAK dilaporkan sebagai early lead.",
    "lastReadBlock": PB, "lastReadWib": NOW,
}
# pending claim binanceai.fun
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["runNote0001"] = "Run 0001: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM."
    pc["lastReadWib"] = NOW
snap["last_run_wib"] = "2026-11-14 ~01:00 WIB"
snap["last_run"] = LAST_RUN
snap["last_run_note"] = ("Run 0001: verify 57/61 OK (blok 133394739, 1454,5 dtk) + retry 4/4; "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru; Voxel Sector age-excluded diam (first mint 12 Nov 15:24 WIB); "
    "Crown Racer 403/500 = 80,6% tapi umur UNVERIFIED (semua view waktu null) -> tetap early lead; "
    "Cinder Crucible 316/325 = 97,2% (9 free tersisa, belum sellout, gate-blocked, DIAM); "
    "binanceai pending TIDAK BERUBAH (refund phase); scan leg fast-fail (Ankr 401); watermark 132512564.")
snap["runNote0001"] = ("Run 0001 (2026-11-14 00:01 WIB, selesai ~01:00 WIB): verify 57/61 OK + retry 4/4 (blok 133394739). "
    "Velocity: TIDAK ADA yang lolos (butuh rate >=1,5x prev DAN >=20 token; semua penggerak +20 tidak punya prev rate -> baseline pertama). "
    "Early lead baru: 0. Strong lead baru: 0. Kandidat baru: 0. Track-B baru/dibuka: 0. Track-C lead baru: 0. "
    "Age-excluded baru: 1 (Voxel Sector, dicatat diam). Sold-out baru: 0.")
snap["runNote0001_scan"] = ("Scan leg run 0001: FAST-FAIL. Pre-flight Ankr getLogs HTTP 401 Unauthorized (head 133391221, 37,4 dtk; "
    "percobaan pertama gagal ambil head/d ataseed timeout 30 dtk, percobaan kedua head OK lalu 401). Ankr 401 sejak 2026-11-09, outage berlanjut. "
    "Watermark TETAP 132512564 (tidak maju). Track-C 5c dilewati (tanpa output scan).")
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("SNAPSHOT WRITTEN contracts:", len(snap["contracts"]), "track_c:", len(snap.get("track_c",{})))
