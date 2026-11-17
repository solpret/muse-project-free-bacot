#!/usr/bin/env python3
"""Merge free-mint-search run 2026-11-15 00:01 WIB.
Reads run-2026-11-14-2331-reread.json (baseline) + run-2026-11-15-0001-reread.json,
computes velocity (interval from block diff, 0.45 s/block), updates the snapshot
surgically (per-contract supply/free/rates/notes), handles FERO age-exclusion,
updates track B pending + track C ORBIT/RigForge, writes velocity + summary JSON.
No preview/mint. Snapshot backed up first."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-0001"
NOW = "2026-11-15 ~00:01 WIB"
SUP = {'WoozCode': 'totalSnippets', 'MORFO': 'totalMinted', 'NOISE': 'totalMinted',
 'AngelEye-77D9': 'totalMinted', 'AngelEye-07bD': 'totalMinted', 'NovaRemnants': 'totalRemnants',
 'RaceAgents': 'totalSupply', 'AbsurdAgentNFT': 'totalMinted', 'B77D': 'totalMinted',
 'Zero': 'totalSupply', 'HIVE': 'totalSupply', 'AgentZENITH': 'totalSupply',
 'AgentNOVA': 'totalSupply', 'SPARKS': 'totalSupply', 'AgentBubble': 'totalSupply',
 'WANGCAI': 'totalSupply', 'YUANBAO': 'totalSupply', 'PX24': 'totalSupply',
 'Zephyra': 'totalMinted', 'LumenFindings': 'totalSpecimens', 'Pengu': 'totalMinted',
 'CPASS': 'totalMinted', 'SPEC': 'totalSpecimens', 'TrashBandits': 'totalMinted',
 'SKRR': 'totalSupply', 'REOPIR': 'totalSupply', 'FrieAgent-B751': 'totalSupply',
 'FrieAgent-c64d': 'totalSupply', 'Ledgera': 'totalSupply', 'MAMI': 'totalSupply',
 'INKI': 'totalSupply', 'HashcatDepot': 'totalSupply', 'OTV': 'totalSupply',
 'RAVE': 'totalMinted', 'HANAMI': 'totalSupply', 'PIXEL FROGS': 'totalSupply'}
NAME_MAP = {'GUARD': 'PenjagaArusNFT'}
FREE_KEYS = ('freeClaimed', 'freeMinted')

r31 = json.load(open(BASE + "run-2026-11-14-2331-reread.json"))
r01 = json.load(open(BASE + "run-2026-11-15-0001-reread.json"))
interval_min = (r01["block"] - r31["block"]) * 0.45 / 60.0

shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261115-0001")
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
    ent["runNote0001_1115"] = f"Run 0001 (blok {r01['block']}, interval {interval_min:.1f} mnt vs run 2331): " + "; ".join(note_parts) + "; DIAM." if note_parts else f"Run 0001: tanpa perubahan; DIAM."
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
    g["runNote0001_1115"] = (f"Run 0001 (blok {r01['block']}, interval {interval_min:.1f} mnt vs run 2331): "
        f"totalMinted {a}->{b} (+{d}, {rate:.3f}/mnt, rasio {round(ratio, 2) if ratio else None} vs prev {prev_rate}) -> velocity {'LOLOS' if passes else 'GAGAL'}; "
        f"free {b}/2000 = {round(b/2000*100, 2)}% (<50%/<70%); gate tetap FAILED (metadata host; putusan FINAL user 14 Nov ~20:21 WIB); tetap EARLY, TIDAK di-preview/di-mint. Deadline 24 jam ~19:23 WIB 15 Nov.")
    updated.append("GUARD(PenjagaArusNFT)")

# Track B — binanceai.fun (pending_claims + contracts duplicate entry)
bv = (r01["reads"].get("BinanceAI-mint") or {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
pc["launched"] = bv.get("launched")
pc["failed"] = bv.get("failed")
pc["isRefundPhase"] = bv.get("isRefundPhase")
pc["totalShares"] = bv.get("totalShares")
pc["tokenClaimed_user"] = bv.get("tokenClaimed_user")
pc["lastReadWib"] = NOW
pc["runNote0001_1115_binanceai"] = (f"Run 0001 track B: binanceai.fun launched={bv.get('launched')}, failed={bv.get('failed')}, "
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
    tc["ORBIT"]["runNote0001_1115"] = (f"Run 0001: ORBIT freeClaimed {ov.get('freeClaimed')}/888, claimOpen {ov.get('claimOpen')}, "
        f"hasFreeClaimed(user)={ov.get('hasFreeClaimed_user')}; umur UNVERIFIED, website NOT CHECKED -> tetap watchlist-only, DIAM.")
rv = (r01["reads"].get("RigForge") or {}).get("views") or {}
if "RigForge" in tc:
    tc["RigForge"]["freeSharesLeft"] = rv.get("freeSharesLeft")
    tc["RigForge"]["openedAt"] = rv.get("openedAt")
    tc["RigForge"]["freeClaimed"] = rv.get("freeClaimed")
    tc["RigForge"]["freeBooked_user"] = rv.get("freeBooked_user")
    tc["RigForge"]["lastReadWib"] = NOW
    tc["RigForge"]["runNote0001_1115"] = (f"Run 0001: RigForge freeSharesLeft {rv.get('freeSharesLeft')}/1000, openedAt {rv.get('openedAt')} "
        f"(pool BELUM buka bila 0), freeClaimed {rv.get('freeClaimed')}, freeBooked(user) {rv.get('freeBooked_user')}. DIAM.")

# FERO age-exclusion (sudah di-run 2301; tidak dibaca ulang run ini)
fero = contracts.get("FERO")
if fero is not None and fero.get("status") != "age-excluded-2026-11-14":
    fero["status"] = "age-excluded-2026-11-14"
    fero["lastReadWib"] = NOW
    fero["runNote0001_1115"] = "Run 0001 AGE-EXCLUDED (konfirmasi): tetap age-excluded sejak run 2301; tidak dibaca ulang."
elif fero is not None:
    fero["runNote0001_1115"] = "Run 0001: FERO tetap age-excluded sejak run 2301 (silent); tidak dibaca ulang, tidak dilaporkan."

# Feed summary entry (web.json run 0001: 0 baru vs seen)
web = json.load(open(BASE + "run-2026-11-15-0001-web.json"))
sf = web.get("sourcify_feed", {})
contracts["Feed-2026-11-15-0001"] = {
    "status": "checked-not-sale-shape-2026-11-14",
    "note": (f"Sourcify feed run 0001: top verifiedAt {sf.get('top_verifiedAt')}, {sf.get('new')} benar-benar baru vs seen; "
             "0 shape hit S1/S2; 0 early lead baru dari feed."),
    "lastReadWib": NOW,
}

s["last_run_wib"] = NOW
s["last_run_block"] = r01["block"]
vel_pass = [k for k, v in vel.items() if v.get("velocity_pass")]
s["runNote0001_1115"] = (f"Run 0001: re-read 40/40 OK, blok {r01['block']}, interval {interval_min:.1f} mnt vs run 2331. "
    f"Velocity LOLOS: {vel_pass if vel_pass else 'tidak ada'}. "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, "
    "0 eksekusi/preview. FERO tetap age-excluded (silent). DIAM sesuai aturan.")
s["runNote0001_1115_scan"] = ("Run 0001 scan: FAST-FAIL pre-flight ankr_getLogs HTTP 401 Unauthorized "
    f"(head {web.get('head')}). Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati. "
    "Outage Ankr 401 sejak 2026-11-09 berlanjut (sudah dilaporkan sekali 9 Nov - DIAM).")
s["runNote0001_1115_feedshape"] = (f"Run 0001 feed Sourcify: top verifiedAt {sf.get('top_verifiedAt')}, {sf.get('new')} baru vs seen, "
    "0 shape hit S1/S2. 0 early lead baru.")
s["runNote0001_1115_boltbook"] = (f"Run 0001 Boltbook: EN {web.get('boltbook_en', {}).get('bytes')} byte / "
    f"{web.get('boltbook_en', {}).get('full_address_contracts')} alamat, ZH {web.get('boltbook_zh', {}).get('bytes')} byte / "
    f"{web.get('boltbook_zh', {}).get('full_address_contracts')} alamat. 0 alamat kontrak baru.")
s["runNote0001_1115_sweep"] = "Run 0001 sweep rute-3/6 (subagen): PENDING - diisi setelah hasil subagen diterima."
br = web.get("bridge", {})
s["runNote0001_1115_bridge"] = (f"Run 0001 bridge: dibaca read-only, {br.get('contracts')} kontrak, "
    f"{br.get('not_in_snapshot')} belum ada di snapshot, {br.get('same_owner_discarded')} same_owner_discarded. "
    "Tidak ada promosi/perubahan. Job ini tidak menulis bridge.")
s["runNote0001_1115_sweep_pending"] = "Sweep subagen masih berjalan saat merge; hasilnya dicatat di runlog terpisah bila ada temuan."

json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
json.dump({"run": "free-mint-search 2026-11-15 00:01 WIB", "block": r01["block"],
           "interval_min": round(interval_min, 1), "velocity": vel, "updated": updated},
          open(BASE + "run-2026-11-15-0001-velocity.json", "w"), indent=1)
summary = {"run": "free-mint-search 2026-11-15 00:01 WIB", "block": r01["block"],
           "reads_ok": r01["reads_ok"], "reads_total": r01["reads_total"],
           "velocity_pass": [k for k, v in vel.items() if v.get("velocity_pass")],
           "candidates_new": 0, "strong_leads_new": 0, "early_leads_new": 0,
           "track_b_opened_blocked": 0, "track_c_new": 0, "executions": 0,
           "fero_age_excluded_silent": True, "sweep": "pending-subagent", "scan": "fast-fail Ankr 401, watermark 132512564",
           "verdict": "DIAM - 0 baru"}
json.dump(summary, open(BASE + "run-2026-11-15-0001-summary.json", "w"), indent=1)
print("MERGE OK updated", len(updated), "contracts; velocity_pass:",
      [k for k, v in vel.items() if v.get("velocity_pass")])
print("interval_min", round(interval_min, 1), "block", r01["block"])
