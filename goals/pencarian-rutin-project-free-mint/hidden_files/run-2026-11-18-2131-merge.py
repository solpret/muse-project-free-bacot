#!/usr/bin/env python3
"""Merge run 2026-11-18 21:31 WIB re-read into onchain-snapshot.json (lean merge).
Driver run-2026-11-18-2131.py completed exit 0 in 147.5s (no SIGTERM this run).
Reread via Quicknode tunnel: 285 calls, 3 chunk errors (Quicknode 429 15/s:
calls 10-14, 160-164, 280-284) - nulls are read failures, never overwrites.
Block 134328778. Interval 30.0 min wall-clock (2101 block UNKNOWN).
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. 1 perubahan status: AONE track-C
free pool SOLD OUT (freeMinted 10000/10000, was 9959) - user already minted
18:17 WIB; report once per track-C rule.
Boltbook EN+ZH OK (44.794 / 42.720 byte, 17 alamat unik, 1 baru 0x7106... ->
terverifikasi BUKAN kontrak: eth_getCode '0x', Sourcify 404 -> bukan lead,
log only). Sourcify feed OK (20 alamat, verifiedAt teratas 2026-11-18T14:37:53Z;
15 shape-checked baru, semua S1/S2 false). Scan leg FAST-FAIL pre-flight
HTTP 401 (Ankr outage sejak 2026-11-09 berlanjut); watermark TETAP 134086385.
Read-only except snapshot. None/err values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-2131-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-2101-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~21:31 WIB"
BLOCK = reread.get("block")
INTERVAL_MIN = 30.0
print(f"block {BLOCK} interval {INTERVAL_MIN} min (wall-clock)")
addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k
updated, missed, vel_pass, deltas = [], [], [], {}
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name); continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply"); pval = pv.get("totalSupply"); view = "totalSupply"
    if not isinstance(fresh, int):
        fresh = v.get("totalMinted"); pval = pv.get("totalMinted"); view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        deltas[name] = minted
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if vel:
            vel_pass.append((name, minted, round(rate, 4), round(ratio, 2)))
        e["previousTotalSupply"] = pval; e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4); e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel; e["supplyView"] = view
    e["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (not in snapshot): {missed}")
print("velocity PASS:", vel_pass)
print("deltas:", dict(sorted(deltas.items(), key=lambda kv: -kv[1])[:12]))

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote2131_1118"] = text
    else:
        print("NOTE MISS", key)

note("STOCK AGENT", "Run 2131 (blok 134328778, interval ~30 mnt vs 2101): totalSupply 794->800 (+6), freeLeft 311 (FREE_SUPPLY 1111, inferred free 800/1111 = 72,0% - MELEWATI 70% secara INFERENSI totalSupply saja; freeMinted/freeClaimed revert = BUKAN counter terverifikasi, umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. Velocity GAGAL (+6 <20).")
note("Lumenhold", "Run 2131: freeClaimed 1258->1259/1500 = 83,9% (+1), totalSupply 1263->1264 (+1) -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Ledgera", "Run 2131: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note("Vitaliq Scans", "Run 2131: totalSupply null (revert - fungsi tidak ada; juga null di chunk 429), genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~14,6 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("HIVE Agents", "Run 2131: totalSupply 1264 FLAT vs 2101, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", "Run 2131: freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("Bubblebruin", "Run 2131: totalSupply 2627 FLAT, freeClaimed 2621/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note("DGF CARD", "Run 2131: totalMinted 1671->1673 (+2) -> velocity GAGAL (<20). freeMinted/mintOpen revert. Tetap EARLY LEAD.")
note("THE WALL", "Run 2131: totalSupply 5516->5518 (+2) -> velocity GAGAL; free views revert. Bukan kandidat.")
note("Mine Card", "Run 2131: totalSupply 1370->1385 (+15, maks run ini) -> velocity GAGAL (<20). Bukan kandidat.")
note("EIM", "Run 2131: totalMinted 781->795 (+14) -> velocity GAGAL (<20). Bukan kandidat.")
note("AgentNOVA", "Run 2131: totalSupply 794->798 (+4) -> velocity GAGAL (<20). Bukan kandidat.")
note("ARKYN", "Run 2131: totalMinted 2295->2298 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note("REOPIR", "Run 2131: totalSupply 591->594 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note("SPARKS", "Run 2131: totalSupply 1212->1215 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note("PunchCard", "Run 2131: totalSupply 1360 (null di 2101, prev snapshot 1356 -> +4), freeMinted 1338/5555, paidMinted 22 -> velocity GAGAL (<20). Bukan kandidat.")
note("MORFO", "Run 2131: totalMinted 1133 (null di 2101, prev 1132 -> +1), mintOpen 1 -> velocity GAGAL. Bukan kandidat.")
note("PIXELFROGS", "Run 2131: totalSupply 456 (null di 2101, prev 456 FLAT), freeMinted 454, freeLeft 2546, mintOpen 0 -> velocity GAGAL. Bukan kandidat.")
note("Flare-bd6f", "Run 2131: totalSupply 4900 (null di 2101, prev 4900 FLAT) -> velocity GAGAL. Bukan kandidat.")
note("Stromboat", "Run 2131: totalMinted 332->333 (+1), freeMinted 333, paidMinted 0 -> velocity GAGAL. Bukan kandidat.")
note("Compasyn", "Run 2131: totalSupply 1096->1097 (+1) -> velocity GAGAL. Bukan kandidat.")
note("Kitebots", "Run 2131: totalSupply 1480->1481 (+1) -> velocity GAGAL. Bukan kandidat.")
note("Kryntar", "Run 2131: totalMinted 1377->1378 (+1) -> velocity GAGAL. Bukan kandidat.")
note("Pengu", "Run 2131: totalMinted 138->139 (+1) -> velocity GAGAL. Bukan kandidat.")
note("XCOPY", "Run 2131: totalSupply 463->464 (+1) -> velocity GAGAL. Bukan kandidat.")
note("ADRAW", "Run 2131: totalSupply/mintOpen null (chunk 160-164 429) -> BACA GAGAL parsial, nilai lama dipertahankan; freeMinted 326 terbaca. Bukan kandidat.")
note("AgentEcho", "Run 2131: totalSupply null (chunk 429) -> BACA GAGAL, nilai lama dipertahankan (413). Bukan kandidat.")
note("Abyssora", "Run 2131: SEMUA view null lagi (chunk 429) -> BACA GAGAL, nilai lama dipertahankan. Bukan kandidat.")

# ---- AONE track-C: FREE POOL SOLD OUT (freeMinted 10000/10000) ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 10000
    aone["FREE_TOTAL"] = 10000
    aone["LAUNCH"] = 1794999600
    aone["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        aone["lastReadBlock"] = BLOCK
    aone["freePoolSoldOut"] = True
    aone["note2131"] = ("Run 2131 (blok 134328778): freeMinted 9959 -> 10000/10000 = FREE POOL SOLD OUT "
        "(FREE_TOTAL 10000; freeQuotaLeft revert - fungsi tidak ada). Kuota user SUDAH 0 (minted-by-user 18:17 WIB) - "
        "sellout tidak mengubah posisi user. PERUBAHAN STATUS dilaporkan sekali run ini (aturan track-C: sold out -> lapor sekali). "
        "Tidak ada eksekusi ulang. Entry dipertahankan dengan status minted-by-user (preseden ORBITA).")
    print("AONE updated: free pool SOLD OUT 10000/10000")
else:
    print("AONE MISSING from track_c!")

# ---- bsccat / PEPE track-C re-reads ----
bs = snap.setdefault("track_c", {}).get("bsccat")
if isinstance(bs, dict):
    bs["freeMinted"] = reread["bsccat"]["views"].get("freeMinted")
    bs["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        bs["lastReadBlock"] = BLOCK
    bs["note2131"] = ("Run 2131: freeMinted 519 -> 536 (+17), totalSupply 536e27; freeSharesLeft/freeClaimed revert. "
        "Status tetap watchlist-only-age-unverified. Bukan lead/kandidat.")
    print("bsccat updated: freeMinted 536")
pe = snap.setdefault("track_c", {}).get("PEPE")
if isinstance(pe, dict):
    pe["freeMinted"] = reread["pepe"].get("freeMinted")
    pe["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        pe["lastReadBlock"] = BLOCK
    pe["note2131"] = "Run 2131: freeMinted 500 FLAT (soldShares null chunk 429), minted-by-user-2026-11-16. DIAM."
    print("PEPE updated: freeMinted 500 FLAT")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote2131"] = ("Run 2131 (blok 134328778): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 21:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "1 PERUBAHAN STATUS: AONE track-C free pool SOLD OUT (freeMinted 10000/10000, user sudah mint 18:17 WIB) - dilaporkan sekali; "
    "STOCK AGENT inferred 72,0% (bukan counter terverifikasi) - tetap EARLY LEAD; Lumenhold 83,9% tapi umur UNVERIFIED; "
    "Boltbook 1 alamat baru 0x7106... terverifikasi BUKAN kontrak - bukan lead.")
snap["runNote2131_1118"] = (
    "Run 2131 (interval ~30 mnt vs 2101; blok 134328778): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "1 PERUBAHAN STATUS: AONE track-C free pool SOLD OUT (freeMinted 9959->10000/10000, FREE_TOTAL 10000; kuota user sudah 0 - minted-by-user 18:17 WIB; dilaporkan sekali run ini). "
    "Driver selesai exit 0 dalam 147,5 dtk (tanpa SIGTERM). "
    "Scan leg FAST-FAIL: Ankr pre-flight GAGAL HTTP 401 Unauthorized dalam 2,0 dtk (outage Ankr sejak 2026-11-09 berlanjut); watermark TETAP 134086385; gap ~242.393 blok (head 134328778) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Reread Quicknode 285 calls, 3 chunk error 429 (calls 10-14, 160-164, 280-284 - rate limit 15/dtk; PUNNY hasClaimedFree/mintedBy/balanceOf, ADRAW totalSupply, AgentEcho totalSupply, Abyssora semua null - nilai lama dipertahankan, BUKAN perubahan). "
    "Velocity: 0 LOLOS - maks +15 Mine Card, +14 EIM, +6 STOCK AGENT, +4 AgentNOVA/PunchCard, +3 ARKYN/REOPIR/SPARKS, +2 DGF CARD/THE WALL - semua <20 token. "
    "STOCK AGENT totalSupply 794->800 (+6), freeLeft 311, inferred free 800/1111 = 72,0% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold freeClaimed 1259/1500 = 83,9% (+1). "
    "Ledgera 54,1% FLAT, Bubblebruin 33,7% FLAT, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user), THE WALL 5518 (+2), DGF CARD 1673 (+2). "
    "Vitaliq Scans: genesisStart 07:00 WIB (umur ~14,6 jam TERVERIFIKASI <24 jam), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "PUNNY freeMinted 379/999 = 37,94% FLAT, mintClosed=1 (age-exclusion sudah dilaporkan 20:34). "
    "bsccat freeMinted 519->536 (+17, tetap watchlist-only-age-unverified); PEPE freeMinted 500 FLAT (minted-by-user). "
    "Boltbook EN OK (44.794 byte, 16 alamat) + ZH OK (42.720 byte, 13 alamat); 1 alamat baru 0x71065a4636fb255b84afa5c48ab300426f29a7d8 -> terverifikasi BUKAN kontrak (eth_getCode '0x', Sourcify 404) -> BUKAN lead, log only, tidak masuk snapshot, tidak dilaporkan. "
    "Sourcify feed OK via tunnel (20 alamat, verifiedAt teratas 2026-11-18T14:37:53Z; 15 shape-checked baru, semua S1/S2 false - 1 agent_ref tanpa free view). "
    "Sweep EN+ZH + share-sale (browser.search): 0 proyek segar baru - hanya proyek lama yang dikenal (Oathbots age-excluded, Agentic Gangster 9 Nov, LeadLoop/NEXUS CORE/hackou/AGENT ID Card 25 Okt, AGENT COSMOS 5 Nov age-excluded, BNBPIG free sold out, ORBITA sale closed 1000/1000, NOVRA age-excluded + pool 0, NEBULA minted-by-user, VISION age-excluded, YAMA age-excluded 16 Nov). "
    "Leg 6: Odaily newsflash + PANews tanpa item free-mint Agent ID baru; DappBay tidak dipakai (tidak ada proyek baru). "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "LAPORAN: 1 perubahan (AONE free pool sold out) dilaporkan sekali; selain itu DIAM."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED")
