#!/usr/bin/env python3
"""Merge run 1301 (scheduled 2026-11-11 13:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1301-reread.json (block 132917000, 59 contracts + 22 track_c),
run-2026-11-11-1301-legs.json (feed + Boltbook ZH urllib OK / EN urllib FAIL + bridge + binanceai),
boltbook-en-1301.html/zh-1301.html (curl OK), run-2026-11-11-1301-rigforge-recheck.json
(re-check read-only), run-2026-11-11-1301-prio.json (CAP7+SHINE), odaily/panews-1301.html,
run-2026-11-11-1301-probe-08df.py (Boltbook-new address: no code on-chain). Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1301-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1301-legs.json"))
rigv = json.load(open(BASE + "run-2026-11-11-1301-rigforge-recheck.json"))
prio = json.load(open(BASE + "run-2026-11-11-1301-prio.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1301-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 13:01 WIB"

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
        e["runNote1301"] = ("Run 1301 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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
               "note": ("Run 1301 Sourcify feed (verified 05:49-05:57Z): S1=False S2=False early=False; "
                        "mint=%s quote=%s free_views=%s agent_ref=%s is_nft=%s is_token=%s fns=%s. Bukan lead track-C."
                        % (s.get("has_mint"), s.get("has_quote"), s.get("free_views"), s.get("agent_ref"),
                           s.get("is_nft"), s.get("is_token"), s.get("fn_count"))),
               "lastReadWib": TS}

# --- RigForge re-check (read-only): pool still closed, booking intact ---
rf = TC.get("RigForge")
if isinstance(rf, dict):
    rf["freeSharesLeft"] = rigv.get("freeSharesLeft")
    rf["openedAt"] = rigv.get("openedAt")
    rf["freeTaken_agentId"] = rigv.get("freeTaken_agentId")
    rf["freeBooked_user"] = rigv.get("freeBooked_user")
    rf["lastReadBlock"] = rigv.get("block_now")
    rf["lastReadWib"] = TS
    rf["note"] = ("Track-C lead MINTED by user 11 Nov 12:12 WIB (tx 0xe766..., blok 132910090, freeBooked 10000 RIG). "
                  "Re-check run 1301 (blok %s): freeSharesLeft %s/1000, openedAt %s (pool BELUM buka - collectShares belum bisa), "
                  "freeTaken(agentId)=%s, freeBooked(wallet)=10000 RIG. Marketplace/rarity TIDAK berlaku (bukan NFT)."
                  % (rigv.get("block_now"), rigv.get("freeSharesLeft"), rigv.get("openedAt"), rigv.get("freeTaken_agentId")))
# --- CAP7 + SHINE priority re-check (read-only) ---
cap7 = prio.get("CAP7") or {}
if isinstance(TC.get("CAP7"), dict):
    e = TC["CAP7"]
    for k in ("freeMinted", "sharesMinted", "paidMinted", "soldOut", "phase", "FREE_SHARES"):
        if cap7.get(k) is not None: e[k] = cap7[k]
    e["lastReadBlock"] = prio.get("block"); e["lastReadWib"] = TS
shine = prio.get("SHINE") or {}
if isinstance(TC.get("SHINE"), dict):
    e = TC["SHINE"]
    for k in ("launch", "launchBlock", "freeClaimed", "sharesSold"):
        if shine.get(k) is not None: e[k] = shine[k]
    e["lastReadBlock"] = prio.get("block"); e["lastReadWib"] = TS

snap["timestamp_wib"] = TS
snap["last_run_wib"] = TS
snap["runNote1301"] = ("Run 1301 (blok reread %s): 0 kandidat baru / 0 strong-lead mint / 0 track-B / 0 track-C lead baru / 0 early lead baru. "
    "RIMEVAULT velocity LOLOS (+103, 34.33x) TAPI status minted-by-user-2026-11-11 + free%% UNVERIFIED - BUKAN promosi. "
    "Jade Vault (0x7Eb9) totalMinted 532->565 (+33, 0.33x) velocity GAGAL run ini (LOLOS 1231); totalSupply view revert, adapter totalMinted. "
    "Stampooor freeMinted 677->695 (+18, 0.62x) velocity GAGAL; 695/1200 = 57,9%% (di atas 50%% track-A tapi di bawah 70%% strong lead; X/website unverified) tetap EARLY. "
    "WORKER 599->635 (+36, 0.68x) velocity GAGAL - free%% + umur UNVERIFIED, BUKAN promosi. "
    "NIGHTFORGE 745 flat (37,1%%) deadline umur 14:37 WIB hari ini; AgentPals deadline ~06:33 WIB 12 Nov; ABYSSCABLE deadline ~19:39 WIB. "
    "0 sellout baru, 0 slot user berubah, 0 age-exclusion baru. Boltbook-new 0x08Df: TIDAK ADA CODE on-chain (bukan kontrak) - bukan lead. "
    "RigForge pool belum buka (freeSharesLeft 813/1000, openedAt 0)." % BLOCK)
snap["runNote1301_scan"] = ("Run 1301 scan: FAST-FAIL pre-flight Ankr ankr_getLogs HTTP 401 Unauthorized. "
    "Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); "
    "gap ke head tumbuh; backfill OFF. Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote1301_rigforge"] = ("RigForge re-check run 1301 (blok %s): freeSharesLeft 813/1000 (870 pukul 12:31, 895 pukul 12:19, 918 pukul 12:12), openedAt 0 (pool BELUM buka), "
    "sharesLeftFor(agentId)=10, agentShares=0, freeTaken(agentId)=1, freeBooked(wallet)=10000 RIG. Booking utuh; collectShares baru bisa sesudah pool buka." % rigv.get("block_now"))
snap["runNote1301_prio"] = ("Run 1301 prio: CAP7 freeMinted 223/640 (34,8%%), phase 1, soldOut 0, slot user balanceOf 0 - gate FAILED (sweep penuh A-N run 1131), TIDAK di-preview/dimint. "
    "SHINE launch=0, freeClaimed=0, sharesSold=0 - masih upcoming (buka 18:00 WIB hari ini).")
snap["runNote1301_binanceai"] = "Run 1301: launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims: binanceai.fun tetap pending, TIDAK di-preview/diklaim."
snap["runNote1301_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE); 116 kontrak, 7 same_owner_discarded; "
    "not_in_snapshot 0 - 0 temuan pelengkap baru run ini. Tidak ada kontrak feed baru di bridge; tidak ada discard baru.")
snap["runNote1301_discovery"] = ("Discovery run 1301: Sourcify feed 20 kontrak (verified 05:49-05:57Z): 4 baru, semuanya bukan sale-shape/early "
    "(0x405D96cd, 0xD40198F0, 0x23ee95aE, 0x51Da504E) -> checked-not-sale-shape. Boltbook EN+ZH curl OK "
    "(EN 45.393 byte 15 alamat; ZH 45.601 byte 15 alamat; 1 baru vs snapshot+hot-leg-seen: 0x08Df7970BB2C632908e3df036d0439420D9cE858 "
    "(post bunnysuny.ai 'LP/NP second wave') - dicek on-chain: eth_getCode 0x (TIDAK ADA CODE, bukan kontrak) + Sourcify 404 -> BUKAN lead, tidak masuk snapshot. "
    "Kit wave-2 kedua 0x1be8268E sudah di hot-leg-seen (bukan temuan baru job ini). Sweep EN+ZH: 0 proyek baru "
    "(Agentic Gangster free-pool-exhausted, sudah tercatat; Horus AI fase 1 gratis sold out 2.000/2.000, fase 2 berbayar; UFO/NEBULA sudah track_c). "
    "Odaily newsflash 200 (266.024 byte) + PANews 200 (121.412 byte): 0 item Agent ID/free-mint.")
snap["runNote1301_boltbook08df"] = ("Boltbook-new 0x08Df7970BB2C632908e3df036d0439420D9cE858 (post bunnysuny.ai, 'LP/NP operators second wave', ~90 mints/kit): "
    "verifikasi on-chain run 1301 - eth_getCode mengembalikan 0x (TIDAK ADA CODE di BSC), semua eth_call view mengembalikan 0x, Sourcify 404 (not verified). "
    "Alamat ini BUKAN kontrak yang ter-deploy: bukan early lead, bukan kandidat, TIDAK masuk snapshot, TIDAK dilaporkan. Dicatat agar tidak di-triase ulang sebagai baru.")
snap["last_run_note"] = ("Run 1301: 0 kandidat/strong-lead/early-lead/track-C lead baru. RIMEVAULT velocity LOLOS tapi minted-by-user + free% UNVERIFIED (bukan promosi). "
                         "Stampooor 57,9% tetap EARLY. Scan FAST-FAIL (Ankr 401). RigForge pool belum buka (813/1000). binanceai launched()=0 tetap pending.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK block", BLOCK, "vel_pass", vel_pass, "vel_fail_n", len(vel_fail), "batch_fail", batch_fail, "tc_updated", tc_updated)
