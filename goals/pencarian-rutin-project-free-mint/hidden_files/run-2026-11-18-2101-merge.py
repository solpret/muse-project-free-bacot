#!/usr/bin/env python3
"""Merge run 2026-11-18 21:01 WIB re-read into onchain-snapshot.json (lean merge).
Salvage merge: the main driver was SIGTERM-killed by a service restart at
~802s, AFTER leg 4 reread + Boltbook ZH but BEFORE feed/shape-check/bridge
(those were completed by run-2026-11-18-2101-salvage.py).
Reread via Quicknode tunnel: 285 calls, 5 chunk errors (calls 65-94,
TimeoutError), elapsed in-script 596s. Block UNKNOWN (eth_blockNumber timed
out) -> interval uses wall-clock 30 min (scheduled cadence 20:31 -> 21:01).
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. 0 perubahan status.
Boltbook ZH: 11 alamat unik, 1 baru (0x8d03...) -> terverifikasi BUKAN kontrak
(eth_getCode '0x', Sourcify not verified, semua view null) -> bukan lead,
log only. Sourcify feed OK via tunnel (20 alamat; 20 shape-checked, semua
S1/S2 false). Scan leg FAST-FAIL pre-flight timeout (egress-wide).
Read-only except snapshot. None/err values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-2101-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-2031-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~21:01 WIB"
BLOCK = reread.get("block")
INTERVAL_MIN = 30.0  # wall-clock: block unknown (eth_blockNumber timeout)
print(f"block {BLOCK} interval {INTERVAL_MIN} min (wall-clock, block unknown)")
addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k
updated, missed, vel_pass = [], [], []
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

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote2101_1118"] = text
    else:
        print("NOTE MISS", key)

note("STOCK AGENT", f"Run 2101 (blok UNKNOWN, interval ~30 mnt vs 2031): totalSupply 794 FLAT, freeLeft 317 (FREE_SUPPLY 1111, inferred free 794/1111 = 71,5% - MELEWATI 70% secara INFERENSI SAJA, freeMinted/freeClaimed revert = bukan counter terverifikasi, jadi BUKAN strong lead; umur + website tetap UNVERIFIED). Velocity GAGAL (+0 <20). Tetap EARLY LEAD.")
note("Lumenhold", f"Run 2101: freeClaimed 1258/1500 = 83,9% FLAT, totalSupply 1263 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Ledgera", f"Run 2101: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note("Vitaliq Scans", f"Run 2101: totalSupply revert (fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~14 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("HIVE Agents", f"Run 2101: totalSupply 1264 FLAT vs 2031, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 2101: freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("Bubblebruin", f"Run 2101: totalSupply 2627 FLAT, freeClaimed 2621/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note("DGF CARD", f"Run 2101: totalMinted 1665->1671 (+6, maks run ini) -> velocity GAGAL (<20). freeMinted/mintOpen revert. Tetap EARLY LEAD.")
note("THE WALL", f"Run 2101: totalSupply 5515->5516 (+1) -> velocity GAGAL; free views revert. Bukan kandidat.")
note("Mine Card", f"Run 2101: totalSupply/totalMinted 1366->1370 (+4) -> velocity GAGAL (<20). Bukan kandidat.")
note("AgentNOVA", f"Run 2101: totalSupply 793->794 (+1) -> velocity GAGAL (<20). Bukan kandidat.")
note("EIM", f"Run 2101: totalMinted 780->781 (+1) -> velocity GAGAL (<20). Bukan kandidat.")
note("PunchCard", f"Run 2101: SEMUA view null (chunk 14-18 timeout, calls 65-94) -> BACA GAGAL, nilai lama dipertahankan (totalSupply 1356, freeMinted 1334/5555), BUKAN perubahan. Bukan kandidat.")
note("MORFO", f"Run 2101: totalMinted/mintOpen null (chunk timeout) -> BACA GAGAL, nilai lama dipertahankan (totalMinted 1132). Bukan kandidat.")
note("ALIEN", f"Run 2101: totalSupply 504 FLAT -> velocity GAGAL. Bukan kandidat.")
note("ARKYN", f"Run 2101: totalMinted 2294->2295 (+1) -> velocity GAGAL (<20). Bukan kandidat.")
note("SPARKS", f"Run 2101: totalSupply 1212 FLAT -> velocity GAGAL. Bukan kandidat.")
note("AgentEcho", f"Run 2101: totalSupply 413 FLAT -> velocity GAGAL. Bukan kandidat.")
note("Stromboat", f"Run 2101: totalMinted 331->332 (+1), freeMinted 332, paidMinted 0 -> velocity GAGAL. Bukan kandidat.")
note("Kageveil Genesis", f"Run 2101: totalSupply 49 FLAT, mintClosed 0 -> velocity GAGAL. Bukan kandidat.")
note("PIXELFROGS", f"Run 2101: SEMUA view null (chunk timeout) -> BACA GAGAL, nilai lama dipertahankan (totalSupply 456). Bukan kandidat.")
note("Flare-bd6f", f"Run 2101: totalSupply null (chunk timeout) -> BACA GAGAL, nilai lama dipertahankan (totalSupply 4900). Bukan kandidat.")

# ---- AONE track-C: views null this run (chunk timeout) -> keep previous ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["lastReadWib"] = NOW
    aone["note2101"] = ("Run 2101: freeMinted/FREE_TOTAL/LAUNCH null (chunk 14-18 timeout) -> BACA GAGAL, "
        "nilai lama dipertahankan (freeMinted 9959/10000, tersisa 41, LAUNCH 18:00 WIB). "
        "Kuota user SUDAH 0 (minted-by-user 18:17 WIB). Tidak ada eksekusi ulang. Belum sold out terkonfirmasi - DIAM sampai sold out.")
    print("AONE note updated (values kept: freeMinted 9959, freeRemaining 41)")
else:
    print("AONE MISSING from track_c!")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote2101"] = ("Run 2101: launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 21:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "0 perubahan status; DRIVER TERBUNUH SIGTERM restart layanan ~802 dtk (setelah leg 4 + Boltbook ZH) - feed/shape-check/bridge diselesaikan via salvage script; "
    "AONE views null (chunk timeout) - nilai lama dipertahankan 9959/10000; STOCK AGENT inferred 71,5% (bukan counter terverifikasi) - tetap EARLY LEAD; "
    "Lumenhold 83,9% tapi umur UNVERIFIED; Boltbook ZH 1 alamat baru 0x8d03... terverifikasi BUKAN kontrak - bukan lead.")
snap["runNote2101_1118"] = (
    "Run 2101 (interval ~30 mnt vs 2031; blok UNKNOWN - eth_blockNumber timeout): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. 0 perubahan status. "
    "DRIVER TERBUNUH: SIGTERM restart layanan ~802 dtk (setelah leg 4 reread + Boltbook ZH, sebelum feed/shape-check/bridge) - "
    "feed + shape-check + verifikasi alamat Boltbook baru diselesaikan via salvage script (58,2 dtk, exit 0). "
    "Scan leg FAST-FAIL: Ankr pre-flight GAGAL setup OSError timeout (egress-wide, BUKAN 401); watermark TIDAK maju. "
    "Reread Quicknode 285 calls, 5 chunk error (calls 65-94 TimeoutError; Flare-bd6f/MORFO/PIXELFROGS/PunchCard null - nilai lama dipertahankan, BUKAN perubahan); elapsed in-script 596 dtk. "
    "Velocity: 0 LOLOS - maks +6 DGF CARD, +4 Mine Card, +2 Foundry Faces, +1 ARKYN/AgentNOVA/EIM/Stromboat/THE WALL/CPASS/Matrix/Kitebots/XCOPY - semua <20 token. "
    "STOCK AGENT inferred 794/1111 = 71,5% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold 1258/1500 = 83,9%. "
    "Ledgera 54,1% FLAT, Bubblebruin 33,7% FLAT, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user). "
    "Vitaliq Scans: genesisStart 07:00 WIB (umur ~14 jam TERVERIFIKASI <24 jam), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "DGF CARD totalMinted 1665->1671 (+6). "
    "AONE track-C: views null (chunk timeout) - nilai lama dipertahankan (freeMinted 9959/10000, tersisa 41, LAUNCH 18:00 WIB); kuota user 0 (minted-by-user 18:17 WIB). DIAM (belum sold out terkonfirmasi). "
    "Boltbook EN GAGAL (file tidak tertulis - driver terbunuh); ZH OK (42.980 byte, 11 alamat unik; 1 baru 0x8d031126123baf88b4017a19f5d5254f61585efa -> terverifikasi BUKAN kontrak: eth_getCode '0x', Sourcify not verified, semua view null -> BUKAN lead, log only). "
    "Sourcify feed OK via tunnel (20 alamat, verifiedAt teratas 2026-11-18T14:24:43Z; 20 shape-checked, semua S1/S2 false - 7 agent_ref tapi tanpa free view). "
    "Sweep EN+ZH + share-sale (browser.search): 0 proyek segar baru - hanya proyek lama yang dikenal (Oathbots age-excluded, Agentic Gangster 9 Nov, LeadLoop/NEXUS CORE/hackou 25 Okt). "
    "Leg 6: Odaily newsflash tanpa item free-mint Agent ID baru; DappBay tidak dipakai (tidak ada proyek baru). "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "Hot-leg 21:04 + 21:09 SILENT (egress degraded 17th/18th straight; Sourcify/Boltbook curl timeout; leg4 reread semua null). "
    "LAPORAN: DIAM (tidak ada yang baru untuk dilaporkan)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
