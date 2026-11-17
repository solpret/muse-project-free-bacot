#!/usr/bin/env python3
"""Merge run 1201 (scheduled 2026-11-11 12:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1201-reread.json (block 132909899, 59 contracts + 22 track_c),
run-2026-11-11-1201-legs.json (feed + Boltbook urllib FAIL + bridge + binanceai),
boltbook-en-1201b.html/zh-1201.html (curl retry OK), run-2026-11-11-1201-rigforge-verify.json
(tx 0xe766... verified), odaily/panews-1201.html. Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1201-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1201-legs.json"))
rigv = json.load(open(BASE + "run-2026-11-11-1201-rigforge-verify.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1201-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 12:01 WIB"

def vel(name, new_supply, interval=30.0):
    e = C.get(name)
    if not isinstance(e, dict): return None
    old = e.get("totalSupply")
    if old is None or new_supply is None: return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / interval, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = interval
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = round(rate / prev_rate, 2) if prev_rate and prev_rate > 0 else None
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

vel_pass, vel_fail, batch_fail = [], [], []
for name, d in reread["reread"].items():
    if name not in C: continue
    e = C[name]
    if d.get("_batch_fail"):
        batch_fail.append(name)
        e["runNote1201"] = ("Run 1201 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
                            "BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None: ns = d.get("totalMinted")
    if ns is not None:
        r = vel(name, ns)
        if r and e.get("velocityLegPasses"): vel_pass.append((name, r))
        elif r: vel_fail.append((name, r))
    else:
        e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
    for k in ("totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None: e[k] = d[k]
    if d.get("totalSupply") is not None: e["totalSupply"] = d["totalSupply"]

tc_updated = []
tc = reread.get("track_c", {})
if isinstance(tc, dict):
    for name, d in tc.items():
        if name not in TC or not isinstance(TC.get(name), dict): continue
        e = TC[name]
        changed = False
        for k in ("totalSupply","freeMinted","freeClaimed"):
            if d.get(k) is not None and e.get(k) != d[k]:
                e[k] = d[k]; changed = True
        e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
        if changed: tc_updated.append(name)

# --- feed-new: 5 contracts, all S1/S2/early False -> checked-not-sale-shape ---
feed_shapes = legs.get("feed_shape", {}).get("shapes", [])
for s in feed_shapes:
    addr = s.get("address")
    if not addr: continue
    key = "Feed-ERC20-" + addr[:10]
    if key in TC: continue
    TC[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-11",
               "note": ("Run 1201 Sourcify feed (verified 04:19-05:08Z): S1=False S2=False early=False; "
                        "mint=%s quote=%s free_views=%s agent_ref=%s is_nft=%s is_token=%s fns=%s. Bukan lead track-C."
                        % (s.get("has_mint"), s.get("has_quote"), s.get("free_views"), s.get("agent_ref"),
                           s.get("is_nft"), s.get("is_token"), s.get("fn_count"))),
               "lastReadWib": TS}

# --- RigForge: track-C lead MINTED by user (verified this run) ---
TC["RigForge"] = {
    "address": "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
    "token": "0x6c2fbbdbf5b08ba838a6030a992d3abc88860c5b",
    "status": "lead-minted-by-user-2026-11-11",
    "website": "https://rigforge.xyz",
    "note": ("Track-C lead: sale buka 11 Nov 12:00 WIB (SALE_START 1794373200), FREE_SHARES 1000, "
             "SHARES_PER_AGENT 10. Fire 11:47 GAGAL 12:00:30 (preview baw error kosong 30 dtk, tanpa tx); "
             "re-fire 12:06 GAGAL juga (preview error kosong); preview langsung baw ~12:08 NETWORK_ERROR 50001001. "
             "KLAIM BERHASIL via baw preview+execute langsung 12:12 WIB: preview BERSIH (simulationCode 000000000), "
             "tx 0xe766edcbb12cc56f1e4a93e32439942644152d6324949d034b83fb2bdcce1cbc, blok 132910090, status 1, gas 93340. "
             "Verifikasi run 1201 (blok 132910315): freeTaken(agentId)=true, freeBooked(wallet)=10000 RIG, "
             "freeSharesLeft 918/1000, openedAt 0. Marketplace/rarity TIDAK berlaku (bukan NFT)."),
    "tx": "0xe766edcbb12cc56f1e4a93e32439942644152d6324949d034b83fb2bdcce1cbc",
    "txBlock": 132910090, "gasUsed": 93340,
    "lastReadBlock": rigv.get("block_now"), "lastReadWib": TS}

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["last_run_note"] = ("Run 1201: RIGFORGE CLAIM BERHASIL (tx 0xe766..., blok 132910090, freeBooked 10000 RIG, terverifikasi on-chain). "
                         "0 kandidat/strong-lead/early-lead/track-C lead baru. WORKER velocity LOLOS tapi free% UNVERIFIED (bukan promosi). "
                         "Scan FAST-FAIL (Ankr 401). binanceai launched()=0 tetap pending.")
snap["runNote1201"] = ("Run 1201 (blok reread %s): 0 kandidat baru / 0 strong-lead mint / 0 track-B / 0 track-C lead baru / 0 early lead baru. "
    "RIGFORGE MINT BERHASIL (lihat track_c RigForge). Velocity LOLOS: WORKER +55 (2,11x) — free%% UNVERIFIED, BUKAN promosi. "
    "Stampooor 627->648 (54%%, velocity gagal 0,42x) tetap EARLY. AgentPals 79->88 (+9, <20) velocity gagal. NIGHTFORGE 742->743 (37,15%%). "
    "0 sellout baru, 0 slot user berubah, 0 age-exclusion baru. Deadline: NIGHTFORGE 14:37 WIB 11 Nov; ABYSSCABLE ~19:39 WIB 11 Nov." % BLOCK)
snap["runNote1201_scan"] = ("Run 1201 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized. "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh; backfill OFF. Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote1201_rigforge"] = ("RigForge RigSale 0xa1cc: fire 11:47 GAGAL 12:00:30 (trigger T+0,013 dtk + sim eth_call OK T+0,5 dtk, preview baw error kosong 30 dtk, STOP, tanpa tx); "
    "re-fire 12:06 GAGAL (preview #1 error kosong 30 dtk); preview langsung baw ~12:08 NETWORK_ERROR 50001001 'other side closed'. "
    "Klaim BERHASIL via baw preview+execute langsung 12:12 WIB (preview bersih 000000000) — tx 0xe766edcbb12cc56f1e4a93e32439942644152d6324949d034b83fb2bdcce1cbc, "
    "blok 132910090, status 1, gas 93340. Verifikasi run 1201 blok 132910315: freeTaken(agentId)=true, freeBooked=10000 RIG, freeSharesLeft 918/1000, openedAt 0. "
    "Audit 11:55: sale hasResult=false (tanpa hasil, bukan lolos); token riskLevel 3 MID, riskAlert None, tanpa hit RISK. Gate website rigforge.xyz lolos.")
snap["runNote1201_binanceai"] = "Run 1201: launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims: binanceai.fun tetap pending, TIDAK di-preview/diklaim."
snap["runNote1201_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru.")
snap["runNote1201_discovery"] = ("Discovery run 1201: Sourcify feed 20 kontrak (verified 04:19-05:08Z): 5 baru, semuanya bukan sale-shape/early "
    "(0xb5b121e1, 0x6aa16DcA, 0x565291C6, 0x6d02F55f, 0x70bBc22D) -> checked-not-sale-shape. Boltbook EN+ZH curl retry OK "
    "(EN 45.649 byte 12 alamat; ZH 47.069 byte 18 alamat; 0 baru vs snapshot+hot-leg-seen). Sweep EN+ZH: 0 proyek baru "
    "(Agentic Gangster free-pool-exhausted; MOLT AGENT excluded; NOVRA free-pool-exhausted; Golden Agents age-excluded). "
    "Odaily newsflash 200 (277.750 byte) + PANews 200 (122.069 byte): 0 item Agent ID/free-mint.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated)
