#!/usr/bin/env python3
"""Merge v2 for free-mint-search run 2026-11-14 20:31 WIB.
Restores snapshot from pre-merge backup (v1 misrouted 2 entries whose
addresses are shared by 2 snapshot keys: GUARD->Feed-B8b7, AbsurdAgentNFT->HAPPE).
Mapping rule: address candidates -> exact name -> name-prefix -> non-checked
live entry. PX24 uses the fixed re-read (correct address). NOTV -> track_c
age-exclusion. No preview/mint."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 133553157
WIB = "2026-11-14 ~20:31 WIB"
INT_MIN = 11.17

shutil.copy(BASE + "onchain-snapshot.json.bak-20261114-2031", BASE + "onchain-snapshot.json")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-14-2031-reread.json"))
vel = json.load(open(BASE + "run-2026-11-14-2031-velocity.json"))
px24fix = json.load(open(BASE + "run-2026-11-14-2031-px24-fix.json"))

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
    if name == "NOTV":
        continue  # track_c age-exclusion, handled below
    if name == "PX24":
        addr = px24fix["address"]  # corrected address (script had a typo)
    key = pick_key(name, addr)
    if not key:
        skipped.append((name, addr))
        continue
    e = contracts[key]
    vrow = dict(vel_by_name.get(name, {}))
    views = rd.get("views") or {}
    if name == "PX24":
        vrow = {"supply_key": "totalSupply", "prev": 527, "cur": 527, "minted": 0,
                "rate": 0.0, "prev_rate": 0.0, "ratio": 0.0, "vel_pass": False,
                "free_pct": None, "free_basis": "freeClaimed view reverts (None)",
                "views_none_2031": ["freeClaimed"]}
        views = {"totalSupply": 527, "freeClaimed": None}
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
    e["lastReadBlock"] = BLOCK if name != "PX24" else px24fix["block"]
    e["lastReadWib"] = WIB
    none_views = vrow.get("views_none_2031") or []
    fp = vrow.get("free_pct")
    note = "Run 2031 (blok %d, interval %.1f mnt vs run 2001): " % (
        e["lastReadBlock"], INT_MIN)
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
        note += "view gagal (None, persisten sejak 2001): %s; " % ",".join(none_views)
    if name == "PX24":
        note += ("ALAMAT SKRIP DIPERBAIKI: ITEMS reread menulis 0xe712...b133136c (tanpa code, "
                 "eth_getCode 0x) - alamat benar snapshot 0xe712...b123136c (code 14.798 byte); "
                 "dibaca ulang blok 133554016: totalSupply 527 FLAT. Perbaiki ITEMS run berikut. ")
    note += "DIAM."
    e["runNote2031_1114"] = note
    updated.append((name, key))

# Track B — binanceai.fun (unchanged)
pc = snap["pending_claims"]["binanceai.fun"]
pc["runNote2031"] = ("Run 2031: launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                     "tokenClaimed(user)=0 (blok %d) - tetap pending/refund, sudah dilaporkan sekali, DIAM" % BLOCK)
pc["lastReadWib"] = WIB

# Track C — RigForge / ORBIT (unchanged)
tc = snap["track_c"]
if "RigForge" in tc:
    tc["RigForge"]["runNote2031_1114"] = ("Run 2031 (blok %d): freeSharesLeft 659/1000 (tidak berubah), openedAt 0 "
        "(pool BELUM buka), freeClaimed 341, freeBooked(user) 10000 RIG - tidak berubah, DIAM" % BLOCK)
    tc["RigForge"]["lastReadBlock"] = BLOCK
if "ORBIT" in tc:
    tc["ORBIT"]["runNote2031_1114"] = ("Run 2031 (blok %d): freeClaimed 276/888 = 31,1%% (tidak berubah), claimOpen 1, "
        "hasFreeClaimed(user)=0 - tidak berubah, DIAM" % BLOCK)
    tc["ORBIT"]["lastReadBlock"] = BLOCK

# NOTV age-exclusion (track_c NOTV-0415): freeStart 13 Nov 18:00 WIB, umur ~26,7 jam, 0 mint.
# Tidak pernah dilaporkan sebagai lead -> DIAM (silent removal).
if isinstance(tc.get("NOTV-0415"), dict):
    tc["NOTV-0415"]["status"] = "age-excluded-2026-11-14"
    tc["NOTV-0415"]["totalSupply"] = 0
    tc["NOTV-0415"]["totalMinted"] = 0
    tc["NOTV-0415"]["lastReadBlock"] = BLOCK
    tc["NOTV-0415"]["lastReadWib"] = WIB
    tc["NOTV-0415"]["runNote2031_1114"] = (
        "Run 2031 AGE-EXCLUDED: freeStart 1794567600 = 13 Nov 18:00 WIB (terbaca on-chain), umur ~26,7 jam "
        "saat run ini; totalSupply/totalMinted MASIH 0 (blok 133553157), freeClaimed None. Jendela gratis sudah "
        "lewat 24 jam tanpa satu pun mint. Tidak pernah dilaporkan sebagai lead -> DIAM (silent removal). "
        "Keluarkan dari ITEMS reread run berikut.")
if "NOTV" in contracts:
    contracts["NOTV"]["runNote2031_1114"] = (
        "Run 2031: totalSupply 0, totalMinted 0, FREE_SHARES 2000, freeStart 13 Nov 18:00 WIB - "
        "AGE-EXCLUDED (umur ~26,7 jam, 0 mint). Entri track_c NOTV-0415 ditandai age-excluded-2026-11-14. DIAM.")

# Feed shape-check: dgold 0xc00c46... — plain ERC20, not a lead
contracts["Feed-c00c46"] = {
    "address": "0xc00C46A19A4731063e8707d7EE2eb06f1b2f788D",
    "status": "checked-not-sale-shape-2026-11-14",
    "lastReadWib": WIB,
    "lastReadBlock": BLOCK,
    "baselineNote": ("Feed Sourcify run 2031 (verifiedAt 2026-11-14T13:36:48Z): dgold, plain ERC20 "
        "(OpenZeppelin ERC20 + Ownable, DEX-pair/trading-sell controls); S1=False S2=False, "
        "no mint/quote/free views, no registry/AgentGate. BUKAN sale-shape, BUKAN agent-shaped. "
        "Tidak dilaporkan, tidak masuk watchlist aktif."),
    "runNote2031_1114": "Run 2031: feed 0xc00C46 S1=False S2=False -> bukan sale-shape.",
}

# KOMA correction: web leg called it 'genuinely new' — it is NOT.
koma = contracts.get("KOMA")
if koma:
    koma["runNote2031_1114"] = ("Run 2031: ditemukan LAGI via sweep ZH (komaagent.fun) - BUKAN baru: sudah di "
        "snapshot sebagai checked-age-excluded-2026-11-14 (run 1401; sale dibuka 2026-11-11 22:00 WIB, "
        "umur ~71 jam saat run ini). Sale yang sama (berakhir 2026-11-16 22:00 CST), bukan fase baru. "
        "KOREKSI klaim kaki web 'genuinely new' - salah, sudah tercatat. DIAM, tidak dilaporkan ulang.")
if isinstance(tc.get("KOMA"), dict):
    tc["KOMA"]["runNote2031_1114"] = ("Run 2031: sweep ZH menemukan lagi - tetap age-excluded (run 1401, sale 11 Nov "
        "22:00 WIB). Bukan lead baru, DIAM.")

# Top-level run notes
snap["runNote2031_1114"] = (
    "Run 2031 (2026-11-14 ~20:31 WIB, eksekusi ~20:37-20:45 WIB): 0 kandidat baru, 0 strong lead baru/promosi, "
    "0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview. "
    "Re-read 41/41 OK, blok 133553157, 92,5 dtk, interval 11,2 mnt vs run 2001 (blok-ts). Velocity LOLOS 0. "
    "Terbesar: GUARD/PARUS +25 (83->108, 2,24/mnt, rasio None - first-rate, GAGAL), Ledgera +1 (free 52,4%%, "
    "umur/website/X UNVERIFIED - bukan kandidat/strong lead), RaceAgents 570 FLAT (57,0%%). "
    "WANGCAI/YUANBAO free sold out 188/188, tidak berubah. NOTV AGE-EXCLUDED (freeStart 13 Nov 18:00 WIB, "
    "~26,7 jam, 0 mint; tidak pernah dilaporkan -> DIAM). KOMA ditemukan lagi via sweep ZH tapi SUDAH "
    "age-excluded run 1401 - bukan baru, DIAM. PX24 alamat skrip diperbaiki (baca ulang benar, 527 FLAT). "
    "DIAM sesuai aturan.")
snap["runNote2031_1114_scan"] = (
    "Run 2031 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized) dalam 4,1 dtk, head 133553179. "
    "Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati. Outage Ankr 401 sejak 2026-11-09 berlanjut.")
snap["runNote2031_1114_feedshape"] = (
    "Run 2031 feed Sourcify: top verifiedAt 2026-11-14T13:36:48Z, tertua 12:52:45Z, 20 kontrak, 1 benar-benar baru "
    "vs seen = 0xc00C46 (dgold, plain ERC20): S1=False S2=False, bukan sale-shape, bukan agent-shaped. 0 early lead baru.")
snap["runNote2031_1114_boltbook"] = (
    "Run 2031 Boltbook: EN 45.495 byte / 12 alamat, ZH 45.673 byte / 12 alamat, union 12, 0 baru vs hot-leg-seen. "
    "0 alamat kontrak baru dari Boltbook run ini.")
snap["runNote2031_1114_sweep"] = (
    "Run 2031 sweep EN+ZH: 0 proyek baru yang lolos. EN: Substack roundup lama, Agentic Gangster, Pocket Ai "
    "(0 minted, belum launch), Oathbots/LeadLoop/NEXUS CORE (Okt 25-28), AGENT COSMOS - semua dikenal. "
    "ZH: KOMA (SUDAH age-excluded run 1401 - koreksi klaim 'baru' kaki web), Agentic Gangster, First-Dollar Grove, "
    "AGENT ID card 0x486d (Okt 25, stale), BNBmeme 0xdfe8 (Okt 26, stale), Subsonic Tribe (excluded). "
    "Route 6: Odaily newsflash 0 item Agent ID/free-mint; PANews 0 item; DappBay dilewati (tidak ada proyek baru).")
snap["runNote2031_1114_binanceai"] = (
    "Run 2031 track B: binanceai.fun launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 - TIDAK BERUBAH (fase refund, sudah dilaporkan sekali). DIAM.")
snap["runNote2031_1114_bridge"] = (
    "Run 2031 bridge: dibaca read-only, 116 kontrak, 0 belum ada di snapshot, 7 same_owner_discarded. "
    "Tidak ada promosi/perubahan. Job ini tidak menulis bridge.")
snap["runNote2031_1114_ledgera"] = (
    "Run 2031 Ledgera: totalSupply 2628->2629 (+1, 0,09/mnt, 0,25x) velocity GAGAL; freeClaimed 2622/5000 = 52,4%% "
    "(>50%% kaki kandidat) TAPI umur/website/X UNVERIFIED -> BUKAN kandidat, BUKAN strong lead (52,4%% < 70%%). "
    "Tanpa promosi, tanpa preview/mint.")
snap["runNote2031_1114_parus"] = (
    "Run 2031 PenjagaArusNFT (PARUS/GUARD) 0xB8b7: totalMinted 83->108 (+25, 2,24/mnt, rasio None - first-rate), "
    "free 108/2000 = 5,4%%, slot user TERBUKA. Velocity GAGAL (tanpa rate sebelumnya). Gate tetap FAILED "
    "(metadata host parus.fcfs.workers.dev; putusan FINAL user 14 Nov ~20:21 WIB: metadata worker TIDAK dihitung "
    "sebagai bukti website). Tetap EARLY lead; TIDAK di-preview/di-mint.")
snap["runNote2031_1114_pixelfrogs"] = (
    "Run 2031 PIXEL FROGS: totalSupply 303->305 (+2), free 303/3000 = 10,1%%, gate FAILED (sudah dilaporkan 15:35). "
    "Deadline 24 jam 2026-11-15 15:29:57 WIB. Tanpa perubahan tier.")
snap["runNote2031_1114_koma"] = (
    "Run 2031 KOMA: sweep ZH menemukan komaagent.fun lagi; KOREKSI - bukan temuan baru. Sudah di snapshot sejak "
    "run 1401 sebagai checked-age-excluded-2026-11-14 (sale dibuka 2026-11-11 22:00 WIB). Sale yang sama, "
    "bukan fase baru. DIAM.")
snap["runNote2031_1114_notv"] = (
    "Run 2031 NOTV AGE-EXCLUDED: track_c NOTV-0415, freeStart 1794567600 = 13 Nov 18:00 WIB (on-chain), umur "
    "~26,7 jam, totalSupply/totalMinted MASIH 0, freeClaimed None. Tidak pernah dilaporkan sebagai lead -> "
    "DIAM (silent removal). Keluarkan dari ITEMS reread run berikut.")
snap["runNote2031_1114_px24"] = (
    "Run 2031 PX24: ITEMS reread (disalin dari run 2001) menulis alamat salah 0xe712...b133136c (eth_getCode 0x, "
    "bukan kontrak) sehingga baca gagal; alamat benar snapshot 0xe712...b123136c (code 14.798 byte). Dibaca ulang "
    "blok 133554016: totalSupply 527 FLAT, freeClaimed revert (None). Perbaiki ITEMS run berikut.")
snap["runNote2031_1114_merge"] = (
    "Run 2031 KOREKSI MERGE: merge v1 salah rute karena alamat ganda di snapshot - GUARD (0xB8b7) tertulis ke "
    "Feed-B8b7 dan AbsurdAgentNFT (0x72c1) tertulis ke HAPPE AGENTS. Snapshot di-restore dari backup "
    "pre-merge dan di-merge ulang (v2) dengan aturan: kandidat alamat -> nama persis -> awalan nama -> entri "
    "live non-checked. PenjagaArusNFT totalMinted 108 dan AbsurdAgentNFT-72C1 kini benar. Catatan: 2 exec di "
    "kaki on-chain gagal (exit 1) tapi kaki selesai dengan semua file terverifikasi parent.")
snap["last_run_wib"] = WIB
snap["last_run_block"] = BLOCK
snap["last_run_note"] = snap["runNote2031_1114"]

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print("updated:", len(updated))
print("skipped:", skipped)
print("mapping sample:", [u for u in updated if u[0] in ("GUARD", "AbsurdAgentNFT", "PX24", "B77D", "HIVE", "CPASS", "NOISE")])
print("contracts now:", len(snap["contracts"]))
print("NOTV-0415 status:", tc.get("NOTV-0415", {}).get("status"))
print("OK merged v2, block", BLOCK)
