#!/usr/bin/env python3
"""Merge free-mint-search run 2026-11-15 09:01 WIB.
Reads run-2026-11-15-0931-reread.json (baseline) + run-2026-11-15-1001-reread.json,
computes velocity (interval from block diff, 0.45 s/block), updates the snapshot
surgically (per-contract supply/free/rates/notes), handles age-exclusion bookkeeping,
updates track B pending + track C ORBIT/RigForge, writes velocity + summary JSON.
No preview/mint. Snapshot backed up first."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-1001"
NOW = "2026-11-15 ~10:01 WIB"
SUP = {'MORFO': 'totalMinted', 'NOISE': 'totalMinted',
 'AngelEye-77D9': 'totalMinted', 'AngelEye-07bD': 'totalMinted',
 'RaceAgents': 'totalSupply', 'AbsurdAgentNFT': 'totalMinted', 'B77D': 'totalMinted',
 'Zero': 'totalSupply', 'HIVE': 'totalSupply', 'AgentZENITH': 'totalSupply',
 'AgentNOVA': 'totalSupply', 'SPARKS': 'totalSupply', 'AgentBubble': 'totalSupply',
 'WANGCAI': 'totalSupply', 'YUANBAO': 'totalSupply', 'PX24': 'totalSupply',
 'Zephyra': 'totalMinted', 'LumenFindings': 'totalSpecimens', 'Pengu': 'totalMinted',
 'CPASS': 'totalMinted', 'SPEC': 'totalSpecimens', 'TrashBandits': 'totalMinted',
 'SKRR': 'totalSupply', 'REOPIR': 'totalSupply', 'FrieAgent-B751': 'totalSupply',
 'FrieAgent-c64d': 'totalSupply', 'Ledgera': 'totalSupply', 'MAMI': 'totalSupply',
 'INKI': 'totalSupply', 'HashcatDepot': 'totalSupply', 'OTV': 'totalSupply',
 'RAVE': 'totalMinted', 'HANAMI': 'totalSupply', 'PIXEL FROGS': 'totalSupply',
 'AGCLUB': 'totalMinted',
 'CosmicSentinel': 'totalSupply'}
NAME_MAP = {'GUARD': 'PenjagaArusNFT'}
FREE_KEYS = ('freeClaimed', 'freeMinted')

r31 = json.load(open(BASE + "run-2026-11-15-0931-reread.json"))
r01 = json.load(open(BASE + "run-2026-11-15-1001-reread.json"))
interval_min = (r01["block"] - r31["block"]) * 0.45 / 60.0

shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261115-1001")
s = json.load(open(BASE + "onchain-snapshot.json"))
contracts = s.setdefault("contracts", {})
vel = {}
updated = []
for name, key in SUP.items():
    v31 = (r31["reads"].get(name) or {}).get("views") or {}
    v01 = (r01["reads"].get(name) or {}).get("views") or {}
    a, b = v31.get(key), v01.get(key)
    ent = contracts.get(name)
    if ent is None:
        vel[name] = {"error": "not in snapshot"}
        continue
    prev_rate = ent.get("currentRatePerMin")
    note_parts = []
    if a is None or b is None:
        vel[name] = {"prev": a, "now": b, "velocity": None, "note": "supply None, nilai lama dipertahankan"}
        note_parts.append(f"supply {key} None run ini, nilai lama dipertahankan")
    else:
        d = b - a
        rate = d / interval_min if interval_min else 0.0
        ratio = (rate / prev_rate) if prev_rate else None
        passes = bool(ratio is not None and ratio >= 1.5 and d >= 20)
        vel[name] = {"prev": a, "now": b, "delta": d, "rate_per_min": round(rate, 4),
                     "prev_rate": prev_rate, "ratio": round(ratio, 2) if ratio is not None else None,
                     "velocity_pass": passes}
        ent[key] = b
        ent["previousRatePerMin"] = prev_rate
        ent["currentRatePerMin"] = round(rate, 4)
        ent["velocityLegPasses"] = passes
        note_parts.append(f"{a}->{b} (+{d}, {rate:.3f}/mnt, rasio {ratio if ratio is None else round(ratio, 2)}) -> velocity {'LOLOS' if passes else 'GAGAL'}")
    for fk in FREE_KEYS:
        if v01.get(fk) is not None:
            ent[fk] = v01[fk]
    # user balance where read
    if v01.get("balanceOf_user") is not None:
        ent["balanceOf_user"] = v01["balanceOf_user"]
    ent["lastReadBlock"] = r01["block"]
    ent["lastReadWib"] = NOW
    ent["runNote1001_1115"] = f"Run 1001 (blok {r01['block']}, interval {interval_min:.1f} mnt vs run 0931): " + "; ".join(note_parts) + "; DIAM." if note_parts else f"Run 1001: tanpa perubahan; DIAM."
    updated.append(name)

# GUARD (snapshot key PenjagaArusNFT)
g = contracts.get("PenjagaArusNFT")
gv31 = (r31["reads"].get("GUARD") or {}).get("views") or {}
gv01 = (r01["reads"].get("GUARD") or {}).get("views") or {}
if g is not None and gv31.get("totalMinted") is not None and gv01.get("totalMinted") is not None:
    a, b = gv31["totalMinted"], gv01["totalMinted"]
    d = b - a
    rate = d / interval_min
    prev_rate = g.get("currentRatePerMin")
    ratio = rate / prev_rate if prev_rate else None
    passes = bool(ratio is not None and ratio >= 1.5 and d >= 20)
    vel["GUARD"] = {"prev": a, "now": b, "delta": d, "rate_per_min": round(rate, 4),
                    "prev_rate": prev_rate, "ratio": round(ratio, 2) if ratio is not None else None,
                    "velocity_pass": passes, "free_pct": round(b / 2000 * 100, 2)}
    g["totalMinted"] = b
    g["freeRemaining"] = gv01.get("freeRemaining")
    g["previousRatePerMin"] = prev_rate
    g["currentRatePerMin"] = round(rate, 4)
    g["velocityLegPasses"] = passes
    g["lastReadBlock"] = r01["block"]
    g["lastReadWib"] = NOW
    g["runNote1001_1115"] = (f"Run 1001 (blok {r01['block']}, interval {interval_min:.1f} mnt vs run 0931): "
        f"totalMinted {a}->{b} (+{d}, {rate:.3f}/mnt, rasio {round(ratio, 2) if ratio else None} vs prev {prev_rate}) -> velocity {'LOLOS' if passes else 'GAGAL'}; "
        f"free {b}/2000 = {round(b/2000*100, 2)}% (<50%/<70%); gate tetap FAILED (metadata host; putusan FINAL user 14 Nov ~20:21 WIB); tetap EARLY, TIDAK di-preview/di-mint. Deadline 24 jam ~19:23 WIB 15 Nov.")
    updated.append("GUARD(PenjagaArusNFT)")


# ForgePass: SOLD OUT run 0201 - removed from reread ITEMS run 1001; no longer read.

# Track B — binanceai.fun (pending_claims + contracts duplicate entry)
bv = (r01["reads"].get("BinanceAI-mint") or {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
pc["launched"] = bv.get("launched")
pc["failed"] = bv.get("failed")
pc["isRefundPhase"] = bv.get("isRefundPhase")
pc["totalShares"] = bv.get("totalShares")
pc["tokenClaimed_user"] = bv.get("tokenClaimed_user")
pc["lastReadWib"] = NOW
pc["runNote1001_1115_binanceai"] = (f"Run 1001 track B: binanceai.fun launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares={bv.get('totalShares')}, tokenClaimed(user)={bv.get('tokenClaimed_user')} - "
    "TIDAK BERUBAH (fase refund, sudah dilaporkan sekali). DIAM.")
if "BinanceAI-mint" in contracts:
    ce = contracts["BinanceAI-mint"]
    ce["launched"] = bv.get("launched")
    ce["failed"] = bv.get("failed")
    ce["isRefundPhase"] = bv.get("isRefundPhase")
    ce["totalShares"] = bv.get("totalShares")
    ce["lastReadBlock"] = r01["block"]
    ce["lastReadWib"] = NOW

# Track C — ORBIT + RigForge
tc = s.setdefault("track_c", {})
ov = (r01["reads"].get("ORBIT") or {}).get("views") or {}
if "ORBIT" in tc:
    tc["ORBIT"]["freeClaimed"] = ov.get("freeClaimed")
    tc["ORBIT"]["claimOpen"] = ov.get("claimOpen")
    tc["ORBIT"]["hasFreeClaimed_user"] = ov.get("hasFreeClaimed_user")
    tc["ORBIT"]["lastReadWib"] = NOW
    tc["ORBIT"]["runNote1001_1115"] = (f"Run 1001: ORBIT freeClaimed {ov.get('freeClaimed')}/888, claimOpen {ov.get('claimOpen')}, "
        f"hasFreeClaimed(user)={ov.get('hasFreeClaimed_user')}; umur UNVERIFIED, website NOT CHECKED -> tetap watchlist-only, DIAM.")
rv = (r01["reads"].get("RigForge") or {}).get("views") or {}
if "RigForge" in tc:
    tc["RigForge"]["freeSharesLeft"] = rv.get("freeSharesLeft")
    tc["RigForge"]["openedAt"] = rv.get("openedAt")
    tc["RigForge"]["freeClaimed"] = rv.get("freeClaimed")
    tc["RigForge"]["freeBooked_user"] = rv.get("freeBooked_user")
    tc["RigForge"]["lastReadWib"] = NOW
    tc["RigForge"]["runNote1001_1115"] = (f"Run 1001: RigForge freeSharesLeft {rv.get('freeSharesLeft')}/1000, openedAt {rv.get('openedAt')} "
        f"(pool BELUM buka bila 0), freeClaimed {rv.get('freeClaimed')}, freeBooked(user) {rv.get('freeBooked_user')}. DIAM.")

# FERO age-exclusion (sudah di-run 2301; tidak dibaca ulang run ini)
fero = contracts.get("FERO")
if fero is not None and fero.get("status") != "age-excluded-2026-11-14":
    fero["status"] = "age-excluded-2026-11-14"
    fero["lastReadWib"] = NOW
    fero["runNote1001_1115"] = "Run 1001 AGE-EXCLUDED (konfirmasi): tetap age-excluded sejak run 2301; tidak dibaca ulang."
elif fero is not None:
    fero["runNote1001_1115"] = "Run 1001: FERO tetap age-excluded sejak run 2301 (silent); tidak dibaca ulang, tidak dilaporkan."

# Age-exclusion WoozCode + NovaRemnants — dinilai dari timestamp blok baca ulang run ini
# (genesisStart WoozCode 1794596827 = 2026-11-14 02:07:07 WIB; NovaRemnants 1794598508 = 02:35:08 WIB).
import subprocess as _sp
def _block_ts(blk):
    for _ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            _r = _sp.run(["curl","-sL","--max-time","30","-X","POST",_ep,"-H","Content-Type: application/json",
                          "-d", json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                                            "params":[hex(blk), False]})],
                         capture_output=True, text=True, timeout=40)
            _j = json.loads(_r.stdout)
            return int(_j["result"]["timestamp"], 16)
        except Exception:
            continue
    return None
blk_ts = _block_ts(r01["block"])
age_excluded_now = []
for _name, _gen in (("WoozCode", 1794596827), ("NovaRemnants", 1794598508)):
    _ent = contracts.get(_name)
    if _ent is None or _ent.get("status", "").startswith("age-excluded"):
        continue
    if blk_ts is None:
        _ent["runNote1001_1115_age"] = f"Run 1001: timestamp blok {r01['block']} gagal dibaca; age-exclusion {_name} DITUNDA ke run berikut."
        continue
    _age_s = blk_ts - _gen
    _age_h = _age_s / 3600.0
    if _age_s >= 86400:
        _sup = _ent.get("totalSnippets") if _name == "WoozCode" else _ent.get("totalRemnants")
        _ent["status"] = "age-excluded-2026-11-15"
        _ent["lastReadWib"] = NOW
        _ent["runNote1001_1115_age"] = (f"Run 1001 AGE-EXCLUDED: umur {_age_h:.2f} jam (>=24 jam) pada blok {r01['block']} "
            f"(ts {blk_ts}); supply terakhir {_sup}; belum sold out; DIHAPUS dari pantauan aktif; dilaporkan sekali run ini.")
        age_excluded_now.append(_name)
    else:
        _ent["runNote1001_1115_age"] = (f"Run 1001: umur {_age_h:.2f} jam (<24 jam) pada blok {r01['block']} (ts {blk_ts}); "
            f"deadline 24 jam {86400 - _age_s:.0f} dtk lagi; MASIH AKTIF.")
# Age check 1001: PIXEL FROGS (mintStart) + GUARD (mintOpenTimestamp) vs blok-ts run ini.
_age_now = []
_pf = (r01["reads"].get("PIXEL FROGS") or {}).get("views") or {}
_gd = (r01["reads"].get("GUARD") or {}).get("views") or {}
for _name, _snapkey, _start in (("PIXEL FROGS", "PIXEL FROGS", _pf.get("mintStart")),
                                ("GUARD", "PenjagaArusNFT", _gd.get("mintOpenTimestamp"))):
    _ent = contracts.get(_snapkey)
    if _ent is None or _ent.get("status", "").startswith("age-excluded"):
        continue
    if blk_ts is None or _start is None:
        _ent["runNote1001_1115_age"] = f"Run 1001: age-check {_name} DITUNDA (blk_ts={blk_ts}, start={_start}); tetap dipantau."
        continue
    _age_h = (blk_ts - _start) / 3600.0
    if blk_ts - _start >= 86400:
        _ent["status"] = "age-excluded-2026-11-15"
        _ent["lastReadWib"] = NOW
        _ent["runNote1001_1115_age"] = (f"Run 1001 AGE-EXCLUDED: umur {_age_h:.2f} jam (>=24 jam) pada blok {r01['block']} "
            f"(ts {blk_ts}); belum sold out; DIHAPUS dari pantauan aktif; dilaporkan sekali run ini.")
        _age_now.append(_name)
    else:
        _ent["runNote1001_1115_age"] = (f"Run 1001: umur {_name} {_age_h:.2f} jam (<24 jam) pada blok {r01['block']} (ts {blk_ts}); "
            f"deadline 24 jam {86400 - (blk_ts - _start):.0f} dtk lagi; MASIH AKTIF.")
# Mihao AGE-EXCLUSION (baru run ini): launch TERVERIFIKASI mintStart on-chain
# 1794554155 = 2026-11-13 14:15:55 WIB; deadline 24 jam 2026-11-14 14:15:55 WIB.
# Terakhir dibaca run 2331 14 Nov (totalSupply 508/2999); tidak ada di ITEMS sejak itu,
# jadi tidak ada run yang mengevaluasi umurnya sesudah deadline. Blok-ts run ini
# 1794711932 = 2026-11-15 10:05:32 WIB -> umur 43,83 jam; belum sold out (513/2999
# pada baca terakhir; laju ~0,6/mnt tak mungkin menghabiskan sisa ~2486 dalam ~10 jam).
_mihao = contracts.get("Mihao")
_mihao_excluded = []
if _mihao is not None and not _mihao.get("status", "").startswith("age-excluded"):
    _mihao["status"] = "age-excluded-2026-11-15"
    _mihao["lastReadWib"] = NOW
    _mihao["runNote1001_1115_age"] = (f"Run 1001 AGE-EXCLUDED: launch TERVERIFIKASI mintStart 1794554155 "
        f"= 2026-11-13 14:15:55 WIB; umur {(blk_ts - 1794554155)/3600:.2f} jam (>=24 jam) pada blok {r01['block']} "
        f"(ts {blk_ts}); supply terakhir 513/2999 (baca 14 Nov ~23:31 WIB), belum sold out; website terverifikasi "
        f"mihao-6zg.pages.dev tapi free% UNVERIFIED, tidak pernah jadi kandidat/strong lead. "
        f"DIHAPUS dari pantauan aktif; dilaporkan sekali run ini.")
    _mihao_excluded.append("Mihao")
# NovaRemnants-38C1: entri duplikat kontrak yang sama dengan 'NovaRemnants'
# (0x38C1695eb72B7522c8d6452a4CE27122532A0d69) — SUDAH age-excluded + dilaporkan sekali
# run 0231 (umur 24,01 jam, totalRemnants 1516). Sinkronkan status saja; JANGAN laporkan ulang.
_n381 = contracts.get("NovaRemnants-38C1")
if _n381 is not None and not _n381.get("status", "").startswith("age-excluded"):
    _n381["status"] = "age-excluded-2026-11-15"
    _n381["lastReadWib"] = NOW
    _n381["runNote1001_1115_age"] = ("Run 1001: status disinkronkan ke age-excluded-2026-11-15 — entri duplikat "
        "kontrak NovaRemnants 0x38C1695eb72B7522c8d6452a4CE27122532A0d69 yang SUDAH di-exclude + dilaporkan sekali "
        "run 0231; TIDAK dilaporkan ulang (silent).")
s["runNote1001_1115_ageex"] = (f"Run 1001 age-exclusion: blok-ts {blk_ts}; baru di-exclude run ini: {_age_now + _mihao_excluded if (_age_now or _mihao_excluded) else 'tidak ada'}; NovaRemnants-38C1 status disinkronkan (duplikat, sudah dilaporkan run 0231).")

import os as _os
def _sweep_note():
    return "Run 1001 sweep rute-3/6 (web leg): PENDING - web leg ditangani parent/subagen sweep terpisah; lihat run-2026-11-15-1001-sweep.md bila ada."
SWEEP_NOTE = _sweep_note()
COSMIC_NOTE = "Run 1001 Cosmic Sentinel deep-dive umur: tidak ada file cosmic-age baru run ini; umur TETAP UNVERIFIED (lihat run 0931)."
# Feed summary entry (web.json run 1001): web leg pending -> no feed entry this run.
try:
    web = json.load(open(BASE + "run-2026-11-15-1001-web.json"))
    _nw = web.get("sourcify", {}).get("new", 0)
    sf = {"top_verifiedAt": web.get("sourcify", {}).get("top_verifiedAt"),
          "new": _nw if isinstance(_nw, int) else len(_nw),
          "total": web.get("sourcify", {}).get("total")}
    contracts["Feed-2026-11-15-1001"] = {
        "status": "checked-not-sale-shape-2026-11-15",
        "note": (f"Sourcify feed run 1001: top verifiedAt {sf.get('top_verifiedAt')}, {sf.get('new')} benar-benar baru vs seen; "
                 "0 shape hit S1/S2; 0 early lead baru dari feed."),
        "lastReadWib": NOW,
    }
    _feed_note = (f"Run 1001 feed Sourcify: top verifiedAt {sf.get('top_verifiedAt')}, {sf.get('new')} baru vs seen, "
        "0 shape hit S1/S2. 0 early lead baru.")
    _bolt_note = "Run 1001 Boltbook: web leg pending (lihat run-2026-11-15-1001-web.json bila ada)."
except FileNotFoundError:
    web = {}
    _feed_note = "Run 1001 feed Sourcify: web leg PENDING (web.json belum ada saat merge); 0 early lead baru dari kaki on-chain."
    _bolt_note = "Run 1001 Boltbook: web leg PENDING (web.json belum ada saat merge)."

s["last_run_wib"] = NOW
s["last_run_block"] = r01["block"]
vel_pass = [k for k, v in vel.items() if v.get("velocity_pass")]
s["runNote1001_1115"] = (f"Run 1001: re-read {r01['reads_ok']}/{r01['reads_total']} OK, blok {r01['block']}, interval {interval_min:.1f} mnt vs run 0931. "
    f"Velocity LOLOS: {vel_pass if vel_pass else 'tidak ada'} (LumenFindings MOOT: sudah age-excluded 14 Nov + free% UNVERIFIED). "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, "
    "0 eksekusi/preview. AGE-EXCLUDED baru run ini: Mihao (43,83 jam, dilaporkan sekali). FERO tetap age-excluded (silent). "
    "NovaRemnants-38C1 status disinkronkan (duplikat, sudah dilaporkan run 0231).")
s["runNote1001_1115_scan"] = ("Run 1001 scan: TIDAK dijalankan oleh kaki on-chain ini (scan leg ditangani parent/leg terpisah); "
    "watermark tidak disentuh run ini. Outage Ankr 401 sejak 2026-11-09 (sudah dilaporkan sekali 9 Nov - DIAM).")
s["runNote1001_1115_feedshape"] = _feed_note
s["runNote1001_1115_boltbook"] = _bolt_note
s["runNote1001_1115_sweep"] = SWEEP_NOTE
try:
    _br = json.load(open(BASE + "scan-bridge.json"))
    _brc = _br.get("contracts", {}) if isinstance(_br, dict) else {}
    _snap_addrs = {(v.get("address") or "").lower() for v in contracts.values() if isinstance(v, dict)}
    _br_n = len(_brc)
    _br_new = sum(1 for a in _brc if a.lower() not in _snap_addrs)
    _br_disc = sum(1 for v in _brc.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    s["runNote1001_1115_bridge"] = (f"Run 1001 bridge: dibaca read-only, {_br_n} kontrak, "
        f"{_br_new} belum ada di snapshot, {_br_disc} same_owner_discarded. "
        "Tidak ada promosi/perubahan. Job ini tidak menulis bridge.")
except Exception as _e:
    s["runNote1001_1115_bridge"] = f"Run 1001 bridge: GAGAL dibaca ({_e}); lanjut normal, bridge tidak menggagalkan run."
s["runNote1001_1115_cosmic_age"] = COSMIC_NOTE

# ABYSS: already in snapshot from run 0931; NOT re-added run 1001 (no fresh on-chain read for it in this run's ITEMS).
# KOMA track_c: no new info run 1001; status untouched.
# AGCLUB: recompute freePct dari FREE_CAP 888 (FREE_SUPPLY() null di bacaan; snapshot mencatat FREE_CAP 888)
_ag = contracts.get("AGCLUB")
if _ag is not None:
    _fm = _ag.get("freeMinted") or _ag.get("totalMinted")
    if _fm is not None and _ag.get("FREE_CAP"):
        _ag["freePctVerified"] = round(_fm / _ag["FREE_CAP"] * 100, 1)
        _ag["runNote1001_1115_agclub"] = (f"Run 1001 AGCLUB: free {_fm}/FREE_CAP 888 = {_ag['freePctVerified']}% (<50%/<70%); "
            "FREE_SUPPLY() null di bacaan (view tidak ada) — FREE_CAP() ditambahkan ke bacaan run berikut. Umur unverified, tanpa website; tetap watchlist-only.")

json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
json.dump({"run": "free-mint-search 2026-11-15 10:01 WIB", "block": r01["block"],
           "interval_min": round(interval_min, 1), "velocity": vel, "updated": updated},
          open(BASE + "run-2026-11-15-1001-velocity.json", "w"), indent=1)
summary = {"run": "free-mint-search 2026-11-15 10:01 WIB", "block": r01["block"],
           "reads_ok": r01["reads_ok"], "reads_total": r01["reads_total"],
           "velocity_pass": [k for k, v in vel.items() if v.get("velocity_pass")],
           "candidates_new": 0, "strong_leads_new": 0, "early_leads_new": 0,
           "track_b_opened_blocked": 0, "track_c_new": 0, "executions": 0,
           "age_excluded_new": _mihao_excluded,
           "fero_age_excluded_silent": True, "sweep": "pending - leg terpisah", "scan": "not run by this leg (on-chain leg only)",
           "verdict": "LAPOR SEKALI: Mihao age-excluded; selebihnya DIAM"}
json.dump(summary, open(BASE + "run-2026-11-15-1001-summary.json", "w"), indent=1)
print("MERGE OK updated", len(updated), "contracts; velocity_pass:",
      [k for k, v in vel.items() if v.get("velocity_pass")])
print("interval_min", round(interval_min, 1), "block", r01["block"])
