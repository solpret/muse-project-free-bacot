#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-14 21:01 WIB.
Merges run-2026-11-14-2101-reread.json + velocity (vs hot-leg 2054) into
onchain-snapshot.json. Mapping rule (from run 2031 merge v2): address
candidates -> exact name -> name-prefix -> live non-checked entry.
Works directly on the live snapshot (no v1 misroute this run).
GUARD velocity ratio corrected here: prev rate read from PenjagaArusNFT
(2.239/mnt), not from the name-key lookup that missed. No preview/mint."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 133556613
WIB = "2026-11-14 ~21:01 WIB"
INT_MIN = 7.33

shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261114-2101")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-14-2101-reread.json"))
vel = json.load(open(BASE + "run-2026-11-14-2101-velocity.json"))
web = json.load(open(BASE + "run-2026-11-14-2101-web.json"))

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
    none_views = vrow.get("views_none_2101") or []
    fp = vrow.get("free_pct")
    note = "Run 2101 (blok %d, interval %.2f mnt vs hot-leg 2054): " % (BLOCK, INT_MIN)
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
    e["runNote2101_1114"] = note
    updated.append((name, key))

# Track B — binanceai.fun (unchanged)
pc = snap["pending_claims"]["binanceai.fun"]
pc["runNote2101"] = ("Run 2101: launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                     "tokenClaimed(user)=0 (blok %d) - tetap pending/refund, sudah dilaporkan sekali, DIAM" % BLOCK)
pc["lastReadWib"] = WIB

# Track C — RigForge / ORBIT (unchanged)
tc = snap["track_c"]
if "RigForge" in tc:
    tc["RigForge"]["runNote2101_1114"] = ("Run 2101 (blok %d): freeSharesLeft 659/1000 (tidak berubah), openedAt 0 "
        "(pool BELUM buka), freeClaimed 341, freeBooked(user) 10000 RIG - tidak berubah, DIAM" % BLOCK)
    tc["RigForge"]["lastReadBlock"] = BLOCK
if "ORBIT" in tc:
    tc["ORBIT"]["runNote2101_1114"] = ("Run 2101 (blok %d): freeClaimed 276/888 = 31,1%% (tidak berubah), claimOpen 1, "
        "hasFreeClaimed(user)=0 - tidak berubah, DIAM" % BLOCK)
    tc["ORBIT"]["lastReadBlock"] = BLOCK

# Feed shape-check: 8 new Sourcify contracts, all S1=False S2=False
feed_notes = {
    "0x8D7a4E041898ECEc29a0da2A808cAD29ad727B01": "plain ERC20 (20 fns), no mint/quote/free/agent",
    "0x0D7C993Fc9ab2F9d06A9C4fe1847914b2f2cF33F": "plain ERC20 (20 fns), no mint/quote/free/agent",
    "0x661CC7cB7f76820Fdc4d8eA60de61f3f72bD2beD": "9 fns, no mint/quote/free/agent, not a token",
    "0xa59b56997B55294163c3048b1a72A354bd9B3729": "token (42 fns) + mint, no quote/free/agent",
    "0x4cB4083746193226bC489D52faE8f0beF10f9eEc": "14 fns, no mint/quote/free/agent, not a token",
    "0x4D0923060D6f657dF4C2567b629e1C3ab8DBc5F5": "token (35 fns) + mint + agent ref, no quote/free views",
    "0x67B1bd2dcCb76691b938E9F0C861210Ec0CE3324": "20 fns + mint + agent ref, no quote/free views, not a token",
    "0xF4DC5FbE3c9af9Ef8dA7Fb746F9A2EbFE34EEf47": "token (22 fns) + mint, no quote/free/agent",
}
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
        "baselineNote": ("Feed Sourcify run 2101 (verifiedAt %s): %s; S1=False S2=False, "
            "bukan sale-shape, bukan agent-shaped (first mints tidak diverifikasi - bukan early lead). "
            "Tidak dilaporkan, tidak masuk watchlist aktif." % (s.get("verifiedAt"), feed_notes.get(a, "checked"))),
        "runNote2101_1114": "Run 2101: feed %s S1=False S2=False -> bukan sale-shape." % a,
    }

# Top-level run notes
snap["runNote2101_1114"] = (
    "Run 2101 (2026-11-14 ~21:01 WIB, eksekusi ~21:02-21:12 WIB): 0 kandidat baru, 0 strong lead baru/promosi, "
    "0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview. "
    "Re-read 40/40 OK, blok 133556613, 85,3 dtk, interval 7,3 mnt vs hot-leg 2054 (blok-ts). Velocity LOLOS 0. "
    "Terbesar: PIXEL FROGS +10 (310->320, 1,36/mnt, 7,62x tapi <20 token -> GAGAL; free 318/3000 = 10,6%%, gate FAILED), "
    "GUARD/PARUS +9 (128->137, 1,23/mnt, rasio terkoreksi 0,55x vs prev 2,24/mnt -> GAGAL; free 137/2000 = 6,9%%, gate FAILED), "
    "LumenFindings +6, RAVE +4 (274->278, free 278/3000 = 9,3%%, slot terbuka, umur/website/X UNVERIFIED). "
    "RaceAgents 571/1000 = 57,1%% (+1, velocity GAGAL); Ledgera 2622/5000 = 52,4%% FLAT (velocity GAGAL; "
    "umur/website/X UNVERIFIED - bukan kandidat/strong lead). WANGCAI/YUANBAO free sold out 188/188, tidak berubah. "
    "DIAM sesuai aturan.")
snap["runNote2101_1114_scan"] = (
    "Run 2101 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized), head 133556525. "
    "Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati. Outage Ankr 401 sejak 2026-11-09 berlanjut.")
snap["runNote2101_1114_feedshape"] = (
    "Run 2101 feed Sourcify: top verifiedAt 2026-11-14T14:03:31Z, 20 kontrak, 8 benar-benar baru "
    "vs seen (0x8D7a4E.., 0x0D7C99.., 0x661CC7.., 0xa59b56.., 0x4cB408.., 0x4D0923.., 0x67B1bd.., 0xF4DC5F..): "
    "semua S1=False S2=False, bukan sale-shape, bukan agent-shaped; 2 di antaranya punya agent ref + mint "
    "tapi tanpa quote/free views dan first mints tidak terverifikasi -> bukan early lead. 0 early lead baru. "
    "8 entri Feed-* dicatat di snapshot.")
snap["runNote2101_1114_boltbook"] = (
    "Run 2101 Boltbook: EN 45.095 byte / 12 alamat, ZH 43.388 byte / 12 alamat, union 12. 1 'baru' vs hot-leg-seen "
    "adalah FALSE POSITIVE: 0xabcacc16.. adalah 40 hex pertama dari Proof TX di post Cinder Crucible /p/Oylf1KOUvW33, "
    "bukan alamat kontrak. Kontrak post itu (Cinder Crucible 0x73f1a09e..) SUDAH di snapshot. Entri seen dikoreksi "
    "menjadi false-positive-tx-hash-fragment. 0 alamat kontrak baru dari Boltbook run ini.")
snap["runNote2101_1114_sweep"] = (
    "Run 2101 sweep EN+ZH: 0 proyek baru yang lolos. EN: Oathbots (Okt 28), Agentic Gangster, RIGBYPASS, STAMP PASS, "
    "AGC, fastmint skill - semua dikenal/di snapshot. ZH: Agentic Gangster, UFO/NEBULA (AirdropBuzz 10 Nov; NEBULA "
    "sudah excluded free-pool-exhausted 9 Nov; UFO tutup 12 Nov 15:05 UTC, tidak pernah dilaporkan - bukan lead), "
    "Oathbots, AGC, AGENT COSMOS (age-excluded 12 Nov), RIGBYPASS (excluded 11 Nov). Route 6: Odaily newsflash "
    "0 item Agent ID/free-mint (hanya Nvidia); PANews 0 item (makro/AI/event); DappBay dilewati (tidak ada proyek baru).")
snap["runNote2101_1114_binanceai"] = (
    "Run 2101 track B: binanceai.fun launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 - TIDAK BERUBAH (fase refund, sudah dilaporkan sekali). DIAM.")
snap["runNote2101_1114_bridge"] = (
    "Run 2101 bridge: dibaca read-only, 116 kontrak, 0 belum ada di snapshot, 7 same_owner_discarded. "
    "Tidak ada promosi/perubahan. Job ini tidak menulis bridge.")
snap["runNote2101_1114_parus"] = (
    "Run 2101 PenjagaArusNFT (PARUS/GUARD) 0xB8b7: totalMinted 128->137 (+9, 1,23/mnt, rasio TERKOREKSI 0,55x "
    "vs prev 2,24/mnt dari entri PenjagaArusNFT - velocity script sempat None karena lookup nama GUARD; "
    "tetap GAGAL juga karena <20 token), free 137/2000 = 6,9%%, slot user TERBUKA. Gate tetap FAILED "
    "(metadata host; putusan FINAL user 14 Nov ~20:21 WIB: metadata worker TIDAK dihitung sebagai bukti website). "
    "Tetap EARLY lead; TIDAK di-preview/di-mint.")
snap["runNote2101_1114_pixelfrogs"] = (
    "Run 2101 PIXEL FROGS: totalSupply 310->320 (+10, 1,36/mnt, 7,62x tapi <20 token -> velocity GAGAL), "
    "free 318/3000 = 10,6%%, gate FAILED (sudah dilaporkan 15:35). Deadline 24 jam 2026-11-15 15:29:57 WIB. "
    "Tanpa perubahan tier.")
snap["runNote2101_1114_rave"] = (
    "Run 2101 RAVE: totalMinted 274->278 (+4, 0,55/mnt), freeMinted 278/3000 = 9,3%%, slot user TERBUKA "
    "(freeClaimed=0, holdsAgentId=1). Umur/website/X masih UNVERIFIED. Jauh di bawah kaki 50%%/70%% - tetap "
    "EARLY lead, tanpa promosi, tanpa preview/mint.")
snap["last_run_wib"] = WIB
snap["last_run_block"] = BLOCK
snap["last_run_note"] = snap["runNote2101_1114"]

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print("updated:", len(updated))
print("skipped:", skipped)
print("mapping sample:", [u for u in updated if u[0] in ("GUARD", "AbsurdAgentNFT", "PX24", "B77D", "HIVE", "CPASS", "NOISE")])
print("contracts now:", len(snap["contracts"]))
print("OK merged 2101, block", BLOCK)
