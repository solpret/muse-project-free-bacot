#!/usr/bin/env python3
"""Merge free-mint-search run 2026-11-15 13:31 WIB.
Reads run-2026-11-15-1331-reread.json (baseline) + run-2026-11-15-1401-reread.json,
computes velocity (interval from block diff, 0.45 s/block), updates the snapshot
surgically (per-contract supply/free/rates/notes), handles age-exclusion bookkeeping,
updates track B pending + track C ORBIT/RigForge, writes velocity + summary JSON.
No preview/mint. Snapshot backed up first."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-1401"
NOW = "2026-11-15 ~14:01 WIB"
SUP = {'MORFO': 'totalMinted', 'NOISE': 'totalMinted',
 'AngelEye-77D9': 'totalMinted', 'AngelEye-07bD': 'totalMinted',
 'RaceAgents': 'totalSupply', 'AbsurdAgentNFT': 'totalMinted', 'B77D': 'totalMinted',
 'Zero': 'totalSupply', 'HIVE': 'totalSupply', 'AgentNOVA': 'totalSupply', 'SPARKS': 'totalSupply', 'AgentBubble': 'totalSupply',
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

r31 = json.load(open(BASE + "run-2026-11-15-1331-reread.json"))
r01 = json.load(open(BASE + "run-2026-11-15-1401-reread.json"))
interval_min = (r01["block"] - r31["block"]) * 0.45 / 60.0

shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261115-1401")
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
    ent["runNote1401_1115"] = f"Run 1401 (blok {r01['block']}, interval {interval_min:.1f} mnt vs run 1331): " + "; ".join(note_parts) + "; DIAM." if note_parts else f"Run 1401: tanpa perubahan; DIAM."
    updated.append(name)

# Matrix Agents — early lead baru run 1131 (parent finalize); baseline run 1131 TIDAK
# membaca Matrix (bukan di ITEMS 1131), jadi prev diambil dari snapshot (totalSupply 13,
# dari verifikasi parent ~11:2x WIB). Rate pertama dicatat; velocity TIDAK lolos
# (aturan first-run: tanpa prev_rate, tidak lolos hanya dari velocity).
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
        "note": "prev dari snapshot run 1331 (totalSupply 257, rate 1.5925); velocity vs prev_rate snapshot"}
    _mx["totalSupply"] = _b
    _mx["freeMinted"] = _mxv.get("freeMinted")
    _mx["freeRemaining"] = _mxv.get("freeRemaining")
    _mx["FREE_MAX"] = _mxv.get("FREE_MAX")
    _mx["MAX_SUPPLY"] = _mxv.get("MAX_SUPPLY")
    _mx["paidMinted"] = _mxv.get("paidMinted")
    _mx["mintPrice"] = _mxv.get("mintPrice")
    _mx["mintOpen"] = bool(_mxv.get("mintOpen"))
    _mx["freeClaimedByAgent_masgayut"] = _mxv.get("freeClaimedByAgent_masgayut")
    _mx["freeClaimedByAgent_masgayut_ai"] = _mxv.get("freeClaimedByAgent_masgayut_ai")
    _mx["previousRatePerMin"] = _prev_rate
    _mx["currentRatePerMin"] = round(_rate, 4)
    _mx["velocityLegPasses"] = _passes
    _mx["freePctVerified"] = round(_b / 1000 * 100, 1) if _mxv.get("FREE_MAX") else None
    _mx["lastReadBlock"] = r01["block"]
    _mx["lastReadWib"] = NOW
    _mx["runNote1401_1115"] = (f"Run 1401 (blok {r01['block']}, interval {interval_min:.1f} mnt vs run 1331): "
        f"totalSupply {_a}->{_b} (+{_d}, {_rate:.3f}/mnt, rasio {round(_ratio, 2) if _ratio is not None else None} vs prev {_prev_rate}) -> velocity {'LOLOS' if _passes else 'GAGAL'}; "
        f"freeMinted {_b}/1000 = {round(_b/1000*100, 1)}% (<50%/<70%); "
        f"freeRemaining {_mxv.get('freeRemaining')}, mintOpen 1, paidMinted 0; slot user TERBUKA "
        f"(freeClaimedByAgent masgayut={_mxv.get('freeClaimedByAgent_masgayut')}, masgayut.ai={_mxv.get('freeClaimedByAgent_masgayut_ai')}); "
        f"umur TETAP UNVERIFIED; website terverifikasi matrixagents.pages.dev. Tetap EARLY, TIDAK di-preview/di-mint. DIAM.")
    if "Matrix Agents" not in updated:
        updated.append("Matrix Agents")

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
    g["runNote1401_1115"] = (f"Run 1401 (blok {r01['block']}, interval {interval_min:.1f} mnt vs run 1331): "
        f"totalMinted {a}->{b} (+{d}, {rate:.3f}/mnt, rasio {round(ratio, 2) if ratio else None} vs prev {prev_rate}) -> velocity {'LOLOS' if passes else 'GAGAL'}; "
        f"free {b}/2000 = {round(b/2000*100, 2)}% (<50%/<70%); gate tetap FAILED (metadata host; putusan FINAL user 14 Nov ~20:21 WIB); tetap EARLY, TIDAK di-preview/di-mint. Deadline 24 jam ~19:23 WIB 15 Nov.")
    updated.append("GUARD(PenjagaArusNFT)")


# ForgePass: SOLD OUT run 0201 - removed from reread ITEMS run 1231; no longer read.

# Track B — binanceai.fun (pending_claims + contracts duplicate entry)
bv = (r01["reads"].get("BinanceAI-mint") or {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
pc["launched"] = bv.get("launched")
pc["failed"] = bv.get("failed")
pc["isRefundPhase"] = bv.get("isRefundPhase")
pc["totalShares"] = bv.get("totalShares")
pc["tokenClaimed_user"] = bv.get("tokenClaimed_user")
pc["lastReadWib"] = NOW
pc["runNote1401_1115_binanceai"] = (f"Run 1401 track B: binanceai.fun launched={bv.get('launched')}, failed={bv.get('failed')}, "
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
    tc["ORBIT"]["runNote1401_1115"] = (f"Run 1401: ORBIT freeClaimed {ov.get('freeClaimed')}/888, claimOpen {ov.get('claimOpen')}, "
        f"hasFreeClaimed(user)={ov.get('hasFreeClaimed_user')}; umur UNVERIFIED, website NOT CHECKED -> tetap watchlist-only, DIAM.")
rv = (r01["reads"].get("RigForge") or {}).get("views") or {}
if "RigForge" in tc:
    tc["RigForge"]["freeSharesLeft"] = rv.get("freeSharesLeft")
    tc["RigForge"]["openedAt"] = rv.get("openedAt")
    tc["RigForge"]["freeClaimed"] = rv.get("freeClaimed")
    tc["RigForge"]["freeBooked_user"] = rv.get("freeBooked_user")
    tc["RigForge"]["lastReadWib"] = NOW
    tc["RigForge"]["runNote1401_1115"] = (f"Run 1401: RigForge freeSharesLeft {rv.get('freeSharesLeft')}/1000, openedAt {rv.get('openedAt')} "
        f"(pool BELUM buka bila 0), freeClaimed {rv.get('freeClaimed')}, freeBooked(user) {rv.get('freeBooked_user')}. DIAM.")

# FERO age-exclusion (sudah di-run 2301; tidak dibaca ulang run ini)
fero = contracts.get("FERO")
if fero is not None and fero.get("status") != "age-excluded-2026-11-14":
    fero["status"] = "age-excluded-2026-11-14"
    fero["lastReadWib"] = NOW
    fero["runNote1401_1115"] = "Run 1401 AGE-EXCLUDED (konfirmasi): tetap age-excluded sejak run 2301; tidak dibaca ulang."
elif fero is not None:
    fero["runNote1401_1115"] = "Run 1401: FERO tetap age-excluded sejak run 2301 (silent); tidak dibaca ulang, tidak dilaporkan."

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
        _ent["runNote1401_1115_age"] = f"Run 1401: timestamp blok {r01['block']} gagal dibaca; age-exclusion {_name} DITUNDA ke run berikut."
        continue
    _age_s = blk_ts - _gen
    _age_h = _age_s / 3600.0
    if _age_s >= 86400:
        _sup = _ent.get("totalSnippets") if _name == "WoozCode" else _ent.get("totalRemnants")
        _ent["status"] = "age-excluded-2026-11-15"
        _ent["lastReadWib"] = NOW
        _ent["runNote1401_1115_age"] = (f"Run 1401 AGE-EXCLUDED: umur {_age_h:.2f} jam (>=24 jam) pada blok {r01['block']} "
            f"(ts {blk_ts}); supply terakhir {_sup}; belum sold out; DIHAPUS dari pantauan aktif; dilaporkan sekali run ini.")
        age_excluded_now.append(_name)
    else:
        _ent["runNote1401_1115_age"] = (f"Run 1401: umur {_age_h:.2f} jam (<24 jam) pada blok {r01['block']} (ts {blk_ts}); "
            f"deadline 24 jam {86400 - _age_s:.0f} dtk lagi; MASIH AKTIF.")
# Age check 1301: PIXEL FROGS (mintStart) + GUARD (mintOpenTimestamp) vs blok-ts run ini.
_age_now = []
_pf = (r01["reads"].get("PIXEL FROGS") or {}).get("views") or {}
_gd = (r01["reads"].get("GUARD") or {}).get("views") or {}
for _name, _snapkey, _start in (("PIXEL FROGS", "PIXEL FROGS", _pf.get("mintStart")),
                                ("GUARD", "PenjagaArusNFT", _gd.get("mintOpenTimestamp"))):
    _ent = contracts.get(_snapkey)
    if _ent is None or _ent.get("status", "").startswith("age-excluded"):
        continue
    if blk_ts is None or _start is None:
        _ent["runNote1401_1115_age"] = f"Run 1401: age-check {_name} DITUNDA (blk_ts={blk_ts}, start={_start}); tetap dipantau."
        continue
    _age_h = (blk_ts - _start) / 3600.0
    if blk_ts - _start >= 86400:
        _ent["status"] = "age-excluded-2026-11-15"
        _ent["lastReadWib"] = NOW
        _ent["runNote1401_1115_age"] = (f"Run 1401 AGE-EXCLUDED: umur {_age_h:.2f} jam (>=24 jam) pada blok {r01['block']} "
            f"(ts {blk_ts}); belum sold out; DIHAPUS dari pantauan aktif; dilaporkan sekali run ini.")
        _age_now.append(_name)
    else:
        _ent["runNote1401_1115_age"] = (f"Run 1401: umur {_name} {_age_h:.2f} jam (<24 jam) pada blok {r01['block']} (ts {blk_ts}); "
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
    _mihao["runNote1401_1115_age"] = (f"Run 1401 AGE-EXCLUDED: launch TERVERIFIKASI mintStart 1794554155 "
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
    _n381["runNote1401_1115_age"] = ("Run 1401: status disinkronkan ke age-excluded-2026-11-15 — entri duplikat "
        "kontrak NovaRemnants 0x38C1695eb72B7522c8d6452a4CE27122532A0d69 yang SUDAH di-exclude + dilaporkan sekali "
        "run 0231; TIDAK dilaporkan ulang (silent).")
s["runNote1401_1115_ageex"] = (f"Run 1401 age-exclusion: blok-ts {blk_ts}; baru di-exclude run ini: {age_excluded_now if age_excluded_now else 'tidak ada'} (Frost + Wuyuhive dicatat saja, tidak pernah jadi lead); NovaRemnants-38C1 status disinkronkan (duplikat, sudah dilaporkan run 0231).")

import os as _os
def _sweep_note():
    return "Run 1401 sweep rute-3/6 (web leg): PENDING - web leg ditangani parent/subagen sweep terpisah; lihat run-2026-11-15-1301-sweep.md bila ada."
SWEEP_NOTE = _sweep_note()
COSMIC_NOTE = "Run 1401 Cosmic Sentinel deep-dive umur: tidak ada file cosmic-age baru run ini; umur TETAP UNVERIFIED (lihat run 1231)."
# Feed summary entry (web.json run 1231): web leg pending -> no feed entry this run.
try:
    web = json.load(open(BASE + "run-2026-11-15-1401-web.json"))
    _nw = web.get("sourcify", {}).get("new", 0)
    sf = {"top_verifiedAt": web.get("sourcify", {}).get("top_verifiedAt"),
          "new": _nw if isinstance(_nw, int) else len(_nw),
          "total": web.get("sourcify", {}).get("total")}
    contracts["Feed-2026-11-15-1331"] = {
        "status": "checked-not-sale-shape-2026-11-15",
        "note": (f"Sourcify feed run 1401: top verifiedAt {sf.get('top_verifiedAt')}, {sf.get('new')} benar-benar baru vs seen; "
                 "0 shape hit S1/S2; 0 early lead baru dari feed."),
        "lastReadWib": NOW,
    }
    _feed_note = (f"Run 1401 feed Sourcify: top verifiedAt {sf.get('top_verifiedAt')}, {sf.get('new')} baru vs seen, "
        "0 shape hit S1/S2. 0 early lead baru.")
    _bolt_note = "Run 1401 Boltbook: web leg pending (lihat run-2026-11-15-1401-web.json bila ada)."
except FileNotFoundError:
    web = {}
    _feed_note = "Run 1401 feed Sourcify: web leg PENDING (web.json belum ada saat merge); 0 early lead baru dari kaki on-chain."
    _bolt_note = "Run 1401 Boltbook: web leg PENDING (web.json belum ada saat merge)."


# FROST AGENT + WUYUHIVE — age-excluded baru run 1401 (temuan Boltbook front page run ini,
# keduanya SUDAH di snapshot sejak 9/8 Nov; preseden Nero run 1331: first-detection = batas atas launch):
# Frost Agent 0x09f893bab23d14ad296a17092c6611aac5a0932b — pertama terlihat job run 1731 9 Nov
# (post recheck 17:29 WIB, 4.900/5.000); triase run ini blok 133692641: totalSupply/totalMinted
# tetap 4.900, MAX 5.000, tanpa free view, Sourcify UNVERIFIED, mint selector revert value 0.
# Launch <= 9 Nov 17:29 WIB -> umur >= ~5,8 hari (>=24 jam), belum sold out (100 tersisa).
# Wuyuhive 0x250e800025a9a7861970e253bab6975a57f80567 — temuan pelengkap scan 8 Nov; scan window
# 131461916-131471150 mencatat mint 23:42-23:49 WIB 3 Nov; post Boltbook run ini: "first detected
# 2026-11-07 15:47". Triase run ini blok 133692641: totalSupply 1.964, freeClaimed 1.958/3.000
# = 65,3% terverifikasi, mintOpen 1, slot user terbuka (mintedBy 0, balance 0). Launch <= 3 Nov
# 23:49 WIB -> umur >= ~11,6 hari (>=24 jam), belum sold out. Keduanya TIDAK PERNAH jadi lead/
# kandidat (Frost: watchlist-only-age-unverified; Wuyuhive: watchlist-only-pelengkap-scan, hanya
# dilaporkan scan sebagai 'finding', bukan lead job ini) -> age-excluded, DICATAT SAJA, TIDAK
# dilaporkan (aturan: belum pernah dilaporkan sebagai lead = diam). JANGAN dibaca ulang run berikut.
_frost = contracts.get("Frost Agent")
if _frost is not None and not _frost.get("status", "").startswith("age-excluded"):
    _frost["status"] = "age-excluded-2026-11-15"
    _frost["totalSupply"] = 4900
    _frost["totalMinted"] = 4900
    _frost["lastReadBlock"] = r01["block"]
    _frost["lastReadWib"] = NOW
    _frost["runNote1401_1115_age"] = ("Run 1401 AGE-EXCLUDED: pertama terlihat job run 1731 9 Nov 17:29 WIB "
        "(post recheck); launch <= 9 Nov 17:29 WIB -> umur >= ~5,8 hari (>=24 jam); triase run ini blok "
        "133692641 totalSupply/totalMinted tetap 4.900/5.000, tanpa free view, Sourcify UNVERIFIED, "
        "mint selector revert value 0 (per post); belum sold out; TIDAK PERNAH jadi lead -> dicatat saja, "
        "TIDAK dilaporkan. DIHAPUS dari pantauan aktif.")
    age_excluded_now.append("Frost Agent (recorded only)")
_wuyu = contracts.get("Wuyuhive")
if _wuyu is not None and not _wuyu.get("status", "").startswith("age-excluded"):
    _wuyu["status"] = "age-excluded-2026-11-15"
    _wuyu["totalSupply"] = 1964
    _wuyu["freeClaimed"] = 1958
    _wuyu["freePctVerified"] = round(1958/3000*100, 1)
    _wuyu["lastReadBlock"] = 133692641
    _wuyu["lastReadWib"] = NOW
    _wuyu["runNote1401_1115_age"] = ("Run 1401 AGE-EXCLUDED: temuan pelengkap scan 8 Nov; mint tercatat scan "
        "window 131461916-131471150 pada 23:42-23:49 WIB 3 Nov + post Boltbook 'first detected 2026-11-07 "
        "15:47'; launch <= 3 Nov 23:49 WIB -> umur >= ~11,6 hari (>=24 jam); triase run ini blok 133692641 "
        "totalSupply 1.964, freeClaimed 1.958/3.000 = 65,3% terverifikasi, mintOpen 1, slot user terbuka; "
        "belum sold out; TIDAK PERNAH jadi lead job ini (hanya 'finding' scan) -> dicatat saja, TIDAK "
        "dilaporkan. DIHAPUS dari pantauan aktif.")
    age_excluded_now.append("Wuyuhive (recorded only)")
# PUNCH IN (Punch In Whitelist Pass) — sudah di snapshot (watchlist-only, website punchin.fun
# terverifikasi); triase run ini blok 133692641: totalSupply/totalMinted 173->180, MAX_SUPPLY 500,
# mintOpen 1, tanpa free view (free% UNVERIFIED), AGENT_REGISTRY=registry (agent-shaped).
# Umur TETAP UNVERIFIED (first seen hot leg 14 Nov 16:59 WIB; deadline 24 jam ~16:59 WIB hari ini
# bila launch = first-seen). Tetap watchlist-only; TIDAK di-preview/di-mint. Hot-leg sudah membaca
# ulang kontrak ini; TIDAK ditambahkan ke ITEMS reread utama (hindari duplikasi).
_punch = contracts.get("Punch In")
if _punch is not None:
    _punch["totalSupply"] = 180
    _punch["totalMinted"] = 180
    _punch["lastReadBlock"] = 133692641
    _punch["lastReadWib"] = NOW
    _punch["runNote1401_1115"] = ("Run 1401: totalSupply 173->180 (+7), MAX_SUPPLY 500, mintOpen 1; "
        "tanpa free view (free% UNVERIFIED); umur TETAP UNVERIFIED (first seen 14 Nov 16:59 WIB). "
        "Tetap watchlist-only; TIDAK di-preview/di-mint. DIAM.")

# NERO AGENT — age-excluded baru run ini (temuan Boltbook front page run ini):
# post dieuxuan50.ai 13:30 WIB "9.900/10.000 free (99.0%) — recheck"; full post:
# "Phát hiện lần đầu: 2026-11-10 11:17 (monitor)" -> launch <= 10 Nov 11:17 WIB
# -> umur >= ~5 hari (>=24 jam). On-chain run ini (blok 133688691): name Nero Agent,
# symbol NEROAGENT, totalSupply=totalMinted=9900, MAX_SUPPLY 10000, price 0.001 BNB,
# AGENT_ID()=registry persis 0x60B926...; TANPA satu pun free view (freeMinted/freeClaimed/
# freeLeft/FREE_SUPPLY/FREE_CAP/FREE_MAX semua revert) -> free% UNVERIFIED (klaim "99% free"
# di post = totalSupply/MAX, BUKAN kuota gratis terverifikasi); mintedBy(user)=0, balanceOf(user)=0;
# Sourcify UNVERIFIED. BUKAN strong lead (free% unverified), BUKAN kandidat, BUKAN early lead
# (first mints bukan di run ini; 9.900 sudah terminting). Tidak pernah dilaporkan sebagai lead
# -> age-excluded, DICATAT SAJA, tidak dilaporkan. JANGAN dibaca ulang run berikut.
if "Nero Agent" not in contracts:
    contracts["Nero Agent"] = {
        "address": "0x03c63ecadf8e0da8377a13aacb28a2a2301181ae",
        "status": "age-excluded-2026-11-15",
        "name": "Nero Agent", "symbol": "NEROAGENT",
        "totalSupply": 9900, "MAX_SUPPLY": 10000, "price": 1000000000000000,
        "AGENT_ID": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
        "freePctVerified": None,
        "freePctNote": "UNVERIFIED: tanpa free view; klaim post 9.900/10.000 = totalSupply/MAX, bukan kuota gratis.",
        "launchNote": "First detected 2026-11-10 11:17 WIB (Boltbook post dieuxuan50.ai, full post /p/IecPm3fdbbQz); launch <= first detection -> umur >= ~5 hari.",
        "lastReadBlock": 133688691, "lastReadWib": NOW,
        "ageExclusionEvidence1331": "Boltbook full post /p/IecPm3fdbbQz: 'Phát hiện lần đầu: 2026-11-10 11:17 (monitor)'; on-chain blok 133688691 totalSupply 9900/10000, tanpa free view, Sourcify unverified; umur >= 5 hari; dicatat saja (tidak pernah jadi lead).",
    }
    age_excluded_now.append("Nero Agent (recorded only)")

s["runNote1401_1115_ageex"] = (f"Run 1401 age-exclusion: blok-ts {blk_ts}; baru di-exclude run ini: {age_excluded_now if age_excluded_now else 'tidak ada'} (Frost + Wuyuhive dicatat saja, tidak pernah jadi lead); NovaRemnants-38C1 status disinkronkan (duplikat, sudah dilaporkan run 0231).")
s["last_run_wib"] = NOW
s["last_run_block"] = r01["block"]
vel_pass = [k for k, v in vel.items() if v.get("velocity_pass")]
s["runNote1401_1115"] = (f"Run 1401: re-read {r01['reads_ok']}/{r01['reads_total']} OK, blok {r01['block']}, interval {interval_min:.1f} mnt vs run 1331. "
    f"Velocity LOLOS: {vel_pass if vel_pass else 'tidak ada'} (LumenFindings MOOT: sudah age-excluded 14 Nov + free% UNVERIFIED). "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, "
    "0 eksekusi/preview. AGE-EXCLUDED baru run ini: tidak ada (Mihao sudah di-exclude + dilaporkan run 1001). FERO tetap age-excluded (silent). "
    "NovaRemnants-38C1 tetap age-excluded (duplikat, sudah dilaporkan run 0231).")
s["runNote1401_1115_scan"] = ("Run 1401 scan: TIDAK dijalankan oleh kaki on-chain ini (scan leg ditangani parent/leg terpisah); "
    "watermark tidak disentuh run ini. Outage Ankr 401 sejak 2026-11-09 (sudah dilaporkan sekali 9 Nov - DIAM).")
s["runNote1401_1115_feedshape"] = _feed_note
s["runNote1401_1115_boltbook"] = _bolt_note
s["runNote1401_1115_sweep"] = SWEEP_NOTE
try:
    _br = json.load(open(BASE + "scan-bridge.json"))
    _brc = _br.get("contracts", {}) if isinstance(_br, dict) else {}
    _snap_addrs = {(v.get("address") or "").lower() for v in contracts.values() if isinstance(v, dict)}
    _br_n = len(_brc)
    _br_new = sum(1 for a in _brc if a.lower() not in _snap_addrs)
    _br_disc = sum(1 for v in _brc.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    s["runNote1401_1115_bridge"] = (f"Run 1401 bridge: dibaca read-only, {_br_n} kontrak, "
        f"{_br_new} belum ada di snapshot, {_br_disc} same_owner_discarded. "
        "Tidak ada promosi/perubahan. Job ini tidak menulis bridge.")
except Exception as _e:
    s["runNote1401_1115_bridge"] = f"Run 1401 bridge: GAGAL dibaca ({_e}); lanjut normal, bridge tidak menggagalkan run."
s["runNote1401_1115_cosmic_age"] = COSMIC_NOTE

# ABYSS: already in snapshot from run 1231; NOT re-added run 1231 (no fresh on-chain read for it in this run's ITEMS).
# KOMA track_c: no new info run 1231; status untouched.
# AGCLUB: recompute freePct dari FREE_CAP 888 (FREE_SUPPLY() null di bacaan; snapshot mencatat FREE_CAP 888)
_ag = contracts.get("AGCLUB")
if _ag is not None:
    _fm = _ag.get("freeMinted") or _ag.get("totalMinted")
    if _fm is not None and _ag.get("FREE_CAP"):
        _ag["freePctVerified"] = round(_fm / _ag["FREE_CAP"] * 100, 1)
        _ag["runNote1401_1115_agclub"] = (f"Run 1401 AGCLUB: free {_fm}/FREE_CAP 888 = {_ag['freePctVerified']}% (<50%/<70%); "
            "FREE_SUPPLY() null di bacaan (view tidak ada) — FREE_CAP() ditambahkan ke bacaan run berikut. Umur unverified, tanpa website; tetap watchlist-only.")

json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
json.dump({"run": "free-mint-search 2026-11-15 14:01 WIB", "block": r01["block"],
           "interval_min": round(interval_min, 1), "velocity": vel, "updated": updated},
          open(BASE + "run-2026-11-15-1401-velocity.json", "w"), indent=1)
summary = {"run": "free-mint-search 2026-11-15 14:01 WIB", "block": r01["block"],
           "reads_ok": r01["reads_ok"], "reads_total": r01["reads_total"],
           "velocity_pass": [k for k, v in vel.items() if v.get("velocity_pass")
                             and not (contracts.get(k) or {}).get("status", "").startswith("age-excluded")],
           "velocity_pass_moot_age_excluded": [k for k, v in vel.items() if v.get("velocity_pass")
                             and (contracts.get(k) or {}).get("status", "").startswith("age-excluded")],
           "candidates_new": 0, "strong_leads_new": 0, "early_leads_new": 0,
           "track_b_opened_blocked": 0, "track_c_new": 0, "executions": 0,
           "age_excluded_new": age_excluded_now,
           "fero_age_excluded_silent": True, "sweep": "done - see run-2026-11-15-1401-sweep.md", "scan": "FAST-FAIL pre-flight Ankr HTTP 401 (freemium habis sejak 9 Nov); watermark tetap 132512564",
           "verdict": "DIAM - 0 kandidat/strong/early baru, 0 track-B/C baru, 0 eksekusi; 2 age-exclusion baru (Frost Agent + Wuyuhive, keduanya dicatat saja, TIDAK dilaporkan)"}
json.dump(summary, open(BASE + "run-2026-11-15-1401-summary.json", "w"), indent=1)
print("MERGE OK updated", len(updated), "contracts; velocity_pass:",
      [k for k, v in vel.items() if v.get("velocity_pass")])
print("interval_min", round(interval_min, 1), "block", r01["block"])
