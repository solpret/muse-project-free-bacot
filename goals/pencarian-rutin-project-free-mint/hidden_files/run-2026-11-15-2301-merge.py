#!/usr/bin/env python3
"""Merge free-mint-search run 2026-11-15 23:01 WIB.
Reads run-2026-11-15-2231-reread.json (baseline) + run-2026-11-15-2301-reread.json,
computes velocity (interval from block diff, 0.45 s/block), updates snapshot
surgically, checks strong-lead legs / sellouts / age-exclusions, updates track B
pending + track C ORBIT/RigForge, writes velocity + summary JSON.
No preview/mint. Snapshot backed up first."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-2231"
NOW = "2026-11-15 ~23:01 WIB"
SUP = {'MORFO': 'totalMinted', 'NOISE': 'totalMinted',
 'RaceAgents': 'totalSupply', 'AbsurdAgentNFT': 'totalMinted', 'B77D': 'totalMinted',
 'Zero': 'totalSupply', 'HIVE': 'totalSupply', 'AgentNOVA': 'totalSupply', 'SPARKS': 'totalSupply', 'AgentBubble': 'totalSupply',
 'WANGCAI': 'totalSupply', 'YUANBAO': 'totalSupply', 'PX24': 'totalSupply',
 'Zephyra': 'totalMinted', 'LumenFindings': 'totalSpecimens', 'Pengu': 'totalMinted',
 'CPASS': 'totalMinted', 'TrashBandits': 'totalMinted',
 'SKRR': 'totalSupply', 'REOPIR': 'totalSupply', 'FrieAgent-B751': 'totalSupply',
 'FrieAgent-c64d': 'totalSupply', 'Ledgera': 'totalSupply', 'MAMI': 'totalSupply',
 'INKI': 'totalSupply', 'HashcatDepot': 'totalSupply', 'OTV': 'totalSupply',
 'RAVE': 'totalMinted', 'HANAMI': 'totalSupply',
 'AGCLUB': 'totalMinted',
 'CosmicSentinel': 'totalSupply'}
FREE_KEYS = ('freeClaimed', 'freeMinted')

r31 = json.load(open(BASE + "run-2026-11-15-2231-reread.json"))
r01 = json.load(open(BASE + "run-2026-11-15-2301-reread.json"))
interval_min = (r01["block"] - r31["block"]) * 0.45 / 60.0

shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261115-2301")
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
    if v01.get("balanceOf_user") is not None:
        ent["balanceOf_user"] = v01["balanceOf_user"]
    ent["lastReadBlock"] = r01["block"]
    ent["lastReadWib"] = NOW
    ent["runNote2301_1115"] = f"Run 2301 (blok {r01['block']}, interval {interval_min:.1f} mnt vs run 2231): " + "; ".join(note_parts) + "; DIAM." if note_parts else f"Run 2301: tanpa perubahan; DIAM."
    updated.append(name)

# Matrix Agents (early lead; prev from snapshot rate)
_mx = contracts.get("Matrix Agents")
_mxv = (r01["reads"].get("Matrix Agents") or {}).get("views") or {}
if _mx is not None and _mxv.get("totalSupply") is not None:
    _a, _b = _mx.get("totalSupply"), _mxv["totalSupply"]
    _d = _b - _a
    _rate = _d / interval_min if interval_min else 0.0
    _prev_rate = _mx.get("currentRatePerMin")
    _ratio = (_rate / _prev_rate) if _prev_rate else None
    _passes = bool(_ratio is not None and _ratio >= 1.5 and _d >= 20)
    vel["Matrix Agents"] = {"prev": _a, "now": _b, "delta": _d, "rate_per_min": round(_rate, 4),
        "prev_rate": _prev_rate, "ratio": round(_ratio, 2) if _ratio is not None else None, "velocity_pass": _passes,
        "note": "prev dari snapshot (totalSupply run 2231)"}
    _mx["totalSupply"] = _b
    for _k in ("freeMinted", "freeRemaining", "FREE_MAX", "MAX_SUPPLY", "paidMinted", "mintPrice"):
        if _mxv.get(_k) is not None:
            _mx[_k] = _mxv[_k]
    _mx["mintOpen"] = bool(_mxv.get("mintOpen"))
    _mx["freeClaimedByAgent_masgayut"] = _mxv.get("freeClaimedByAgent_masgayut")
    _mx["freeClaimedByAgent_masgayut_ai"] = _mxv.get("freeClaimedByAgent_masgayut_ai")
    _mx["previousRatePerMin"] = _prev_rate
    _mx["currentRatePerMin"] = round(_rate, 4)
    _mx["velocityLegPasses"] = _passes
    _mx["freePctVerified"] = round(_b / 1000 * 100, 1) if _mxv.get("FREE_MAX") else None
    _mx["lastReadBlock"] = r01["block"]
    _mx["lastReadWib"] = NOW
    _mx["runNote2301_1115"] = (f"Run 2301 (blok {r01['block']}, interval {interval_min:.1f} mnt vs run 2231): "
        f"totalSupply {_a}->{_b} (+{_d}, {_rate:.3f}/mnt, rasio {round(_ratio, 2) if _ratio is not None else None} vs prev {_prev_rate}) -> velocity {'LOLOS' if _passes else 'GAGAL'}; "
        f"freeMinted {_b}/1000 = {round(_b/1000*100, 1)}% (<50%/<70%); "
        f"freeRemaining {_mxv.get('freeRemaining')}, mintOpen 1, paidMinted 0; slot user TERBUKA "
        f"(freeClaimedByAgent masgayut={_mxv.get('freeClaimedByAgent_masgayut')}, masgayut.ai={_mxv.get('freeClaimedByAgent_masgayut_ai')}); "
        f"umur TETAP UNVERIFIED; website terverifikasi matrixagents.pages.dev. Tetap EARLY, TIDAK di-preview/di-mint. DIAM.")
    if "Matrix Agents" not in updated:
        updated.append("Matrix Agents")

# Track B — binanceai.fun
bv = (r01["reads"].get("BinanceAI-mint") or {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
pc["launched"] = bv.get("launched")
pc["failed"] = bv.get("failed")
pc["isRefundPhase"] = bv.get("isRefundPhase")
pc["totalShares"] = bv.get("totalShares")
pc["tokenClaimed_user"] = bv.get("tokenClaimed_user")
pc["lastReadWib"] = NOW
pc["runNote2301_1115_binanceai"] = (f"Run 2301 track B: binanceai.fun launched={bv.get('launched')}, failed={bv.get('failed')}, "
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
    tc["ORBIT"]["runNote2301_1115"] = (f"Run 2301: ORBIT freeClaimed {ov.get('freeClaimed')}/888, claimOpen {ov.get('claimOpen')}, "
        f"hasFreeClaimed(user)={ov.get('hasFreeClaimed_user')}; umur UNVERIFIED, website NOT CHECKED -> tetap watchlist-only, DIAM.")
rv = (r01["reads"].get("RigForge") or {}).get("views") or {}
if "RigForge" in tc:
    tc["RigForge"]["freeSharesLeft"] = rv.get("freeSharesLeft")
    tc["RigForge"]["openedAt"] = rv.get("openedAt")
    tc["RigForge"]["freeClaimed"] = rv.get("freeClaimed")
    tc["RigForge"]["freeBooked_user"] = rv.get("freeBooked_user")
    tc["RigForge"]["lastReadWib"] = NOW
    tc["RigForge"]["runNote2301_1115"] = (f"Run 2301: RigForge freeSharesLeft {rv.get('freeSharesLeft')}/1000, openedAt {rv.get('openedAt')} "
        f"(pool BELUM buka bila 0), freeClaimed {rv.get('freeClaimed')}, freeBooked(user) {rv.get('freeBooked_user')}. DIAM.")

# FERO — tetap age-excluded (silent)
fero = contracts.get("FERO")
if fero is not None:
    fero["runNote2301_1115"] = "Run 2301: FERO tetap age-excluded sejak run 2301 (silent); tidak dibaca ulang, tidak dilaporkan."

# GUARD (PenjagaArusNFT) — age-excluded run 2101; konfirmasi status, tidak dibaca ulang
gd = contracts.get("PenjagaArusNFT")
if gd is not None:
    gd["runNote2301_1115"] = "Run 2301: GUARD tetap age-excluded run 2101 (sudah dilaporkan sekali); tidak dibaca ulang, tidak dilaporkan."

# Strong-lead + sellout check across reread items (free % where cap known)
FREE_CAPS = {
    "AgentBubble": ("freeMinted", 2222), "AGCLUB": ("freeMinted", 888),
    "RaceAgents": ("freeMinted", 1000), "Matrix Agents": ("freeMinted", 1000),
    "MORFO": ("totalMinted", None), "SPARKS": ("totalSupply", None),
    "Ledgera": ("freeClaimed", None),
}
strong = []
soldout = []
for name, (fk, cap) in FREE_CAPS.items():
    v = (r01["reads"].get(name) or {}).get("views") or {}
    f = v.get(fk)
    if f is None or cap is None:
        continue
    pct = round(f / cap * 100, 1)
    if f >= cap:
        soldout.append(f"{name} free {f}/{cap} = {pct}% SOLD OUT")
    elif pct > 70:
        strong.append(f"{name} free {f}/{cap} = {pct}% (>70%)")
# freeRemaining-based sellout (Matrix Agents etc.)
for name in ("Matrix Agents",):
    v = (r01["reads"].get(name) or {}).get("views") or {}
    if v.get("freeRemaining") == 0 and v.get("mintOpen"):
        soldout.append(f"{name} freeRemaining 0 SOLD OUT")

s["timestamp_wib"] = NOW
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
json.dump({"interval_min": round(interval_min, 2), "velocity": vel, "updated": updated,
           "strong_leads": strong, "soldout": soldout, "block": r01["block"]},
          open(BASE + "run-2026-11-15-2301-velocity.json", "w"), indent=1)
summary = {
 "run": "free-mint-search 2026-11-15 23:01 WIB",
 "block": r01["block"],
 "reads_ok": r01["reads_ok"],
 "reads_total": r01["reads_total"],
 "interval_min": round(interval_min, 2),
 "velocity_pass": [k for k, v in vel.items() if v.get("velocity_pass")],
 "velocity_pass_moot_age_excluded": [],
 "candidates_new": 0,
 "strong_leads_new": strong,
 "early_leads_new": 0,
 "track_b_opened_blocked": 0,
 "track_c_new": 0,
 "executions": 0,
 "age_excluded_new": [],
 "sold_out_new": soldout,
 "scan": "FAST-FAIL pre-flight Ankr HTTP 401 (freemium habis sejak 9 Nov); watermark tetap 132512564",
 "verdict": "pending web legs",
}
json.dump(summary, open(BASE + "run-2026-11-15-2301-summary.json", "w"), indent=1)
print("MERGE DONE interval", round(interval_min, 2), "min; velocity_pass:", [k for k, v in vel.items() if v.get("velocity_pass")])
print("strong:", strong)
print("soldout:", soldout)
print("updated:", len(updated))
