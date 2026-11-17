#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-14 21:31 WIB.
Merges run-2026-11-14-2131-reread.json + velocity (vs hot-leg 2119) into
onchain-snapshot.json. Mapping rule (from run 2031 merge v2): address
candidates -> exact name -> name-prefix -> live non-checked entry.
Works directly on the live snapshot (no v1 misroute this run).
GUARD velocity ratio corrected here: prev rate read from PenjagaArusNFT
(2.239/mnt), not from the name-key lookup that missed. No preview/mint."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
WIB = "2026-11-14 ~21:31 WIB"
_r = json.load(open(BASE + "run-2026-11-14-2131-reread.json"))
BLOCK = _r.get("block")
_vel0 = json.load(open(BASE + "run-2026-11-14-2131-velocity.json"))
INT_MIN = round(_vel0.get("interval_min") or 30.0, 2)

shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261114-2131")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-14-2131-reread.json"))
vel = json.load(open(BASE + "run-2026-11-14-2131-velocity.json"))
web = json.load(open(BASE + "run-2026-11-14-2131-web.json"))

contracts = snap["contracts"]

def pick_key(name, addr):
    addr = (addr or "").lower()
    cands = [k for k, v in contracts.items()
             if (v.get("address") or "").lower() == addr] if addr else []
    if len(cands) == 1:
        return cands[0]
    if len(cands) > 1:
        if name in cands:
            return name
        for k in cands:
            if k.startswith(name) or name.startswith(k):
                return k
        live = [k for k in cands
                if not k.startswith("Feed-")
                and not str(contracts[k].get("status", "")).startswith("checked-")]
        if live:
            return live[0]
        return cands[0]
    if name in contracts:
        return name
    return None

vel_by_name = {r["name"]: r for r in vel["rows"]}
FREE_FIELDS = ["freeClaimed", "freeMinted", "freeRemaining", "FREE_SUPPLY", "FREE_MAX",
               "FREE_POOL", "freeLeft", "freeSupply", "totalMinted", "totalSupply"]
updated, skipped = [], []

for name, rd in reread["reads"].items():
    addr = rd.get("address")
    if name == "RigForge":
        continue  # track_c, handled below
    if name == "BinanceAI-mint":
        continue  # track B pending_claims, handled below
    key = pick_key(name, addr)
    if not key:
        skipped.append((name, addr))
        continue
    e = contracts[key]
    vrow = dict(vel_by_name.get(name, {}))
    views = rd.get("views") or {}
    # GUARD ratio correction: prev rate lives on PenjagaArusNFT (2.239/mnt)
    if name == "GUARD":
        prev_rate = contracts.get("PenjagaArusNFT", {}).get("currentRatePerMin")
        if vrow.get("rate") is not None and prev_rate:
            vrow["prev_rate"] = prev_rate
            vrow["ratio"] = round(vrow["rate"] / prev_rate, 2)
            vrow["vel_pass"] = bool(vrow["ratio"] >= 1.5 and (vrow.get("minted") or 0) >= 20)
    sk = vrow.get("supply_key")
    if sk and vrow.get("cur") is not None:
        e["previousTotalSupply"] = vrow.get("prev")
        e[sk] = vrow["cur"]
        e["mintedInInterval"] = vrow.get("minted")
        e["intervalMinutes"] = INT_MIN
        e["currentRatePerMin"] = vrow.get("rate")
        e["previousRatePerMin"] = vrow.get("prev_rate")
        e["velocityRatio"] = vrow.get("ratio")
        e["velocityLegPasses"] = False
    for f in FREE_FIELDS:
        if f in views and views[f] is not None and f != sk:
            e[f] = views[f]
    for f, val in views.items():
        if ("_user" in f or f == "balanceOf_user") and val is not None:
            e[f] = val
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = WIB
    none_views = vrow.get("views_none_2131") or []
    fp = vrow.get("free_pct")
    note = "Run 2131 (blok %d, interval %.2f mnt vs hot-leg 2119): " % (BLOCK, INT_MIN)
    if sk and vrow.get("cur") is not None:
        note += "%s %s->%s (+%s, %.3f/mnt, rasio %s) -> velocity GAGAL; " % (
            sk, vrow.get("prev"), vrow.get("cur"), vrow.get("minted"),
            vrow.get("rate") or 0.0,
            ("%.2fx" % vrow["ratio"]) if vrow.get("ratio") is not None else "None")
    elif sk:
        note += "%s gagal baca (None) - degradasi RPC, nilai lama dipertahankan; " % sk
    else:
        note += "tidak ada supply view; "
    if fp is not None:
        note += "free %s%% (%s); " % (fp, vrow.get("free_basis"))
    if none_views:
        note += "view gagal (None, persisten): %s; " % ", ".join(none_views)
    note += "DIAM."
    e["runNote2131_1114"] = note
    updated.append((name, key))

# Track B — binanceai.fun (unchanged)
pc = snap["pending_claims"]["binanceai.fun"]
pc["runNote2131"] = ("Run 2131: launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                     "tokenClaimed(user)=0 (blok %d) - tetap pending/refund, sudah dilaporkan sekali, DIAM" % BLOCK)
pc["lastReadWib"] = WIB

# Track C — RigForge / ORBIT (unchanged)
tc = snap["track_c"]
if "RigForge" in tc:
    tc["RigForge"]["runNote2131_1114"] = ("Run 2131 (blok %d): freeSharesLeft 659/1000 (tidak berubah), openedAt 0 "
        "(pool BELUM buka), freeClaimed 341, freeBooked(user) 10000 RIG - tidak berubah, DIAM" % BLOCK)
    tc["RigForge"]["lastReadBlock"] = BLOCK
if "ORBIT" in tc:
    tc["ORBIT"]["runNote2131_1114"] = ("Run 2131 (blok %d): freeClaimed 276/888 = 31,1%% (tidak berubah), claimOpen 1, "
        "hasFreeClaimed(user)=0 - tidak berubah, DIAM" % BLOCK)
    tc["ORBIT"]["lastReadBlock"] = BLOCK

# Feed shape-check: 8 new Sourcify contracts, all S1=False S2=False
def feed_note(s):
    if s.get("error"):
        return "shape-check error: " + str(s["error"])[:120]
    return ("S1=%s S2=%s mint=%s quote=%s free=%s agent=%s token=%s n_fns=%s" % (
        s.get("S1"), s.get("S2"), s.get("has_mint"), s.get("has_quote"),
        s.get("free_views"), s.get("agent_ref"), s.get("is_token"), s.get("n_fns")))
feed_notes = {s["address"]: feed_note(s) for s in web.get("shape_check", [])}
for s in web.get("shape_check", []):
    a = s["address"]
    short = "Feed-" + a[2:8].lower()
    if short in contracts or a.lower() in [ (v.get("address") or "").lower() for v in contracts.values() ]:
        continue
    contracts[short] = {
        "address": a,
        "status": "checked-not-sale-shape-2026-11-14",
        "lastReadWib": WIB,
        "lastReadBlock": BLOCK,
        "baselineNote": ("Feed Sourcify run 2131 (verifiedAt %s): %s; "
            "bukan sale-shape, bukan agent-shaped (first mints tidak diverifikasi - bukan early lead). "
            "Tidak dilaporkan, tidak masuk watchlist aktif." % (s.get("verifiedAt"), feed_notes.get(a, "checked"))),
        "runNote2131_1114": "Run 2131: feed %s %s -> bukan sale-shape." % (a, feed_notes.get(a, "")),
    }

# Top-level run notes
snap["runNote2131_1114"] = (
    "Run 2131 (2026-11-14 ~21:31 WIB, eksekusi ~21:32-21:38 WIB): 0 kandidat baru, 0 strong lead baru/promosi, "
    "0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview. "
    "Re-read 40/40 OK, blok 133560630, 92,5 dtk, interval 5,42 mnt vs hot-leg 2119 (blok-ts). Velocity LOLOS 0. "
    "Terbesar: GUARD/PARUS +11 (175->186, 2,03/mnt, 1,66x tapi <20 token -> GAGAL; free 186/2000 = 9,3%%, gate FAILED), "
    "LumenFindings +4 (3219->3223, 0,74/mnt, 0,90x -> GAGAL), SPEC +3, REOPIR +3, NOISE +2, NovaRemnants +2, "
    "PIXEL FROGS +1 (325->326, free 324/3000 = 10,8%%, gate FAILED), RAVE 282 FLAT (free 282/3000 = 9,4%%, slot terbuka, umur/website/X UNVERIFIED). "
    "RaceAgents 573/1000 = 57,3%% FLAT (velocity GAGAL); Ledgera 2623/5000 = 52,5%% (+1, velocity GAGAL; "
    "umur/website/X UNVERIFIED - bukan kandidat/strong lead). AgentBubble freeMinted 1447/2222 = 65,1%% (info-only, alokasi free = MAX unverified), velocity GAGAL. "
    "HIVE 1263 FLAT, minted-by-user. WANGCAI/YUANBAO free sold out 188/188, tidak berubah. "
    "DIAM sesuai aturan.")
snap["runNote2131_1114_scan"] = (
    "Run 2131 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized), head 133560454. "
    "Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati. Outage Ankr 401 sejak 2026-11-09 berlanjut.")
snap["runNote2131_1114_feedshape"] = (
    "Run 2131 feed Sourcify: top verifiedAt 2026-11-14T14:33:10Z, 20 kontrak, 2 benar-benar baru "
    "vs seen (0x1EfA05.., 0x9FE2c4..): 0x1EfA05 token (29 fns) + mint + quote, tanpa free views/agent ref; "
    "0x9FE2c4 8 fns, tanpa mint/quote/free/agent/token - semua S1=False S2=False, bukan sale-shape, "
    "bukan agent-shaped (first mints tidak terverifikasi -> bukan early lead). 0 early lead baru. "
    "2 entri Feed-* dicatat di snapshot.")
snap["runNote2131_1114_boltbook"] = (
    "Run 2131 Boltbook: EN 43.893 byte / 10 alamat, ZH 42.216 byte / 10 alamat, union 10. 0 alamat kontrak baru. "
    "Tidak ada lead baru dari Boltbook run ini.")
snap["runNote2131_1114_sweep"] = (
    "Run 2131 sweep EN+ZH: 0 proyek baru yang lolos. EN: Oathbots (Okt 28), Agentic Gangster (9 Nov, di snapshot), "
    "RIGBYPASS (excluded 11 Nov), STAMP PASS (dikenal), AGC, fastmint skill. ZH: Agentic Gangster, UFO/NEBULA "
    "(AirdropBuzz 10 Nov; NEBULA sudah excluded free-pool-exhausted 9 Nov; UFO tutup 12 Nov 15:05 UTC, tidak pernah "
    "dilaporkan - bukan lead), WNO (age-excluded 12 Nov, di track_c), NOVRA (di track_c), Oathbots, AGC, "
    "AGENT COSMOS (age-excluded 12 Nov). Route 6: Square tercakup sweep (tanpa proyek baru); Odaily/PANews tidak "
    "di-fetch run ini (tidak ada proyek baru yang butuh gate-check); DappBay dilewati (tidak ada proyek baru).")
snap["runNote2131_1114_binanceai"] = (
    "Run 2131 track B: binanceai.fun launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 - TIDAK BERUBAH (fase refund, sudah dilaporkan sekali). DIAM.")
snap["runNote2131_1114_bridge"] = (
    "Run 2131 bridge: dibaca read-only, 116 kontrak, 0 belum ada di snapshot, 7 same_owner_discarded. "
    "Tidak ada promosi/perubahan. Job ini tidak menulis bridge.")
snap["runNote2131_1114_parus"] = (
    "Run 2131 PenjagaArusNFT (PARUS/GUARD) 0xB8b7: totalMinted 175->186 (+11, 2,03/mnt, rasio 1,66x vs prev 1,23/mnt - "
    "tetap GAGAL karena <20 token), free 186/2000 = 9,3%%, slot user TERBUKA (freeUsed=0, mintedBy=0). Gate tetap FAILED "
    "(metadata host; putusan FINAL user 14 Nov ~20:21 WIB: metadata worker TIDAK dihitung sebagai bukti website). "
    "Tetap EARLY lead; TIDAK di-preview/di-mint. Deadline 24 jam ~19:23 WIB 15 Nov.")
snap["runNote2131_1114_pixelfrogs"] = (
    "Run 2131 PIXEL FROGS: totalSupply 325->326 (+1, 0,18/mnt, 0,14x -> velocity GAGAL), "
    "free 324/3000 = 10,8%%, gate FAILED (sudah dilaporkan 15:35). Deadline 24 jam 2026-11-15 15:29:57 WIB. "
    "Tanpa perubahan tier.")
snap["runNote2131_1114_rave"] = (
    "Run 2131 RAVE: totalMinted 282 FLAT vs hot-leg 2119 (282), freeMinted 282/3000 = 9,4%%, slot user TERBUKA "
    "(freeClaimed=0, holdsAgentId=1). Umur/website/X masih UNVERIFIED. Jauh di bawah kaki 50%%/70%% - tetap "
    "EARLY lead, tanpa promosi, tanpa preview/mint.")
snap["last_run_wib"] = WIB
snap["last_run_block"] = BLOCK
snap["last_run_note"] = snap["runNote2131_1114"]

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print("updated:", len(updated))
print("skipped:", skipped)
print("mapping sample:", [u for u in updated if u[0] in ("GUARD", "AbsurdAgentNFT", "PX24", "B77D", "HIVE", "CPASS", "NOISE")])
print("contracts now:", len(snap["contracts"]))
print("OK merged 2131, block", BLOCK)
