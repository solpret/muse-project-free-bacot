#!/usr/bin/env python3
"""Merge run 2026-11-09 1301 WIB — re-read velocity, snapshot updates,
Arachnoir same-owner discard (NOT an early lead), Minority Pass pool exhausted,
PACTA gate still FAILED (method L 3rd Cloudflare block), Ankr scan FAST-FAIL (401).
No scan output this run (pre-flight 401 x3); no triage/seen appends.
Writes: onchain-snapshot.json (atomic), run-2026-11-09-1301-merge.json (report).
Read-only w.r.t. chain; never mints/previews.
"""
import json, os, shutil
from datetime import datetime, timezone, timedelta

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW = datetime(2026, 11, 9, 14, 0, tzinfo=timezone(timedelta(hours=7)))

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
r1231 = json.load(open(f"{HF}/run-2026-11-09-1231-reread.json"))
r1301 = json.load(open(f"{HF}/run-2026-11-09-1301-reread.json"))
disc = json.load(open(f"{HF}/run-2026-11-09-1301-discovery-A.json"))
bna = json.load(open(f"{HF}/run-2026-11-09-1301-binanceai.json"))
pacta = json.load(open(f"{HF}/run-2026-11-09-1301-pacta.json"))
arach = json.load(open(f"{HF}/run-2026-11-09-1301-arachnoir.json"))

BLOCK_1301 = r1301["block"]
BLOCK_1231 = r1231["block"]
INTERVAL_MIN = (BLOCK_1301 - BLOCK_1231) * 0.45 / 60.0
print(f"interval_minutes (block-based): {INTERVAL_MIN:.2f} blocks {BLOCK_1231}->{BLOCK_1301}")

shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-2026-11-09-1301")

report = {"run": "2026-11-09-1301", "interval_minutes": round(INTERVAL_MIN, 2),
          "velocity_pass": [], "sellouts_new": [], "slot_changes": [],
          "age_exclusions": [], "age_candidates_kept": [], "early_leads_new": [],
          "discarded_same_owner": [], "track_c_added": [], "track_c_excluded": []}

contracts = snap.get("contracts", {})

# ---- 1. re-read velocity + snapshot value updates ----
n_upd = 0
for name, d in r1301.get("reread", {}).items():
    old = contracts.get(name)
    if not isinstance(old, dict) or not isinstance(d, dict):
        continue
    base1231 = r1231.get("reread", {}).get(name, {}).get("totalSupply") if isinstance(r1231.get("reread", {}).get(name), dict) else None
    base_snap = old.get("totalSupply")
    new_ts = d.get("totalSupply")
    prev_rate = old.get("currentRatePerMin")
    vel = {"name": name, "baseline": None, "minted": None, "rate": None, "ratio": None, "passes": False, "note": ""}
    kind = str(old.get("kind") or "")
    st = str(old.get("status") or "")
    is_token = ("ERC20" in kind.upper() or "bridge" in kind.lower() or
                "bridge" in st.lower() or "pelengkap-scan" in st.lower() or
                "scan-complement" in st.lower())
    if new_ts is not None and base1231 is not None and not is_token:
        minted = new_ts - base1231
        rate = minted / INTERVAL_MIN
        ratio = (rate / prev_rate) if (prev_rate not in (None, 0)) else None
        vel.update({"baseline": base1231, "minted": minted, "rate": round(rate, 4),
                    "ratio": round(ratio, 2) if ratio is not None else None,
                    "passes": bool(minted >= 20 and ratio is not None and ratio >= 1.5),
                    "note": "baseline=1231 reread"})
        if vel["passes"]:
            report["velocity_pass"].append(vel)
        old["previousTotalSupply"] = base1231
        old["previousRatePerMin"] = prev_rate
        old["currentRatePerMin"] = round(rate, 4)
        old["velocityRatio"] = vel["ratio"]
    elif new_ts is not None and base_snap is not None and new_ts != base_snap:
        vel.update({"note": "baseline 1231 missing (batch fail) — velocity NOT computed over stale snapshot interval"})
        old["previousTotalSupply"] = base_snap
    for k in ["totalSupply", "freeClaimed", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"]:
        if d.get(k) is not None:
            old[k] = d[k]
    if d.get("totalMinted") is not None:
        old["totalMinted"] = d["totalMinted"]
    if d.get("freeMinted") is not None:
        old["freeMinted"] = d["freeMinted"]
    if d.get("balanceOf_user") is not None:
        old["balanceOf_user"] = d["balanceOf_user"]
        old["userBalance"] = d["balanceOf_user"]
    if d.get("freeClaimed_user") is not None:
        old["freeClaimed_user"] = d["freeClaimed_user"]
    fc, fs = old.get("freeClaimed"), old.get("FREE_SUPPLY")
    if isinstance(fc, (int, float)) and isinstance(fs, (int, float)) and fs:
        old["freePctVerified"] = round(100.0 * fc / fs, 2)
    elif isinstance(old.get("freeMinted"), (int, float)) and isinstance(fs, (int, float)) and fs:
        old["freePctVerified"] = round(100.0 * old["freeMinted"] / fs, 2)
    old["lastReadBlock"] = BLOCK_1301
    old["lastReadWib"] = "2026-11-09 13:5x WIB"
    if vel["minted"] is not None:
        old["mintedInInterval"] = vel["minted"]
        old["intervalMinutes"] = round(INTERVAL_MIN, 2)
        old["velocityLegPasses"] = vel["passes"]
        old["runNote1301_1109"] = (f"Run 1301 (blok {BLOCK_1301}, interval {INTERVAL_MIN:.1f} mnt vs run 1231): "
            f"{vel['baseline']}->{new_ts} (+{vel['minted']}, {vel['rate']:.3f}/mnt vs prev {prev_rate} = "
            f"{vel['ratio']}x) -> velocity {'LOLOS' if vel['passes'] else 'GAGAL'}; "
            f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')}; bal_user={d.get('balanceOf_user')}; "
            f"status {old.get('status')}.")
        n_upd += 1
    else:
        old["runNote1301_1109"] = (f"Run 1301 (blok {BLOCK_1301}): totalSupply {new_ts} "
            f"(baseline 1231 gagal baca / snapshot stale — velocity TIDAK dihitung); "
            f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')}; bal_user={d.get('balanceOf_user')}; "
            f"status {old.get('status')}.")
print(f"contracts updated: {n_upd} velocity-pass: {[v['name'] for v in report['velocity_pass']]}")

# ---- 2. track_c re-read updates ----
tc = snap.get("track_c", {})
n_tc = 0
for name, d in r1301.get("track_c", {}).items():
    old = tc.get(name)
    if not isinstance(old, dict) or not isinstance(d, dict):
        continue
    prev_free = old.get("freeSharesRemaining")
    for k in ["freeSharesRemaining", "freeMinted", "totalSupply"]:
        if d.get(k) is not None:
            old[k] = d[k]
    if d.get("balanceOf_user") is not None:
        old["balanceOf_user"] = d["balanceOf_user"]
    if d.get("freeClaimed_user") is not None:
        old["freeClaimed_user"] = d["freeClaimed_user"]
    old["lastReadBlock"] = BLOCK_1301
    n_tc += 1
    if prev_free not in (None, 0) and old.get("freeSharesRemaining") == 0:
        report["sellouts_new"].append({"name": name, "prev_free": prev_free})
print(f"track_c updated: {n_tc} sellouts_new: {report['sellouts_new']}")

# ---- 3. Minority Pass — free pool EXHAUSTED (discovery + reread) ----
mp = tc.get("Minority Pass")
if isinstance(mp, dict):
    mp_r = r1301.get("track_c", {}).get("Minority Pass", {})
    mp_disc = next((c for c in disc.get("changes", []) if c.get("name") == "Minority Pass"), {})
    mp["freeMinted"] = mp_r.get("freeMinted") if mp_r.get("freeMinted") is not None else mp.get("freeMinted")
    mp["totalSupply"] = mp_r.get("totalSupply") if mp_r.get("totalSupply") is not None else mp.get("totalSupply")
    mp["freeSharesRemaining"] = 0
    mp["status"] = "excluded-free-pool-exhausted-2026-11-09"
    mp["lastReadBlock"] = BLOCK_1301
    mp["lastReadWib"] = "2026-11-09 13:5x WIB"
    report["track_c_excluded"].append({
        "name": "Minority Pass", "address": mp.get("sale"),
        "evidence": "freeMinted 200/200, totalSupply 200 (discovery dataseed ~13:45 WIB; reread TC freeMinted=%s)" % mp_r.get("freeMinted"),
        "note": "Pool habis sejak run 1231 (67/133 tersisa). Gate sudah FAILED sebelumnya; tidak pernah dieksekusi. Dilaporkan sekali sebagai perubahan."})
    print("Minority Pass excluded: pool exhausted")

# ---- 4. Arachnoir — SAME-OWNER DISCARD (NOT an early lead) ----
ARACH = "0xe6ffadcfb8766e6199ec74f896da37f00b0f5bca"
av = arach.get("views", {})
contracts["Arachnoir"] = {
    "address": ARACH,
    "status": "promotion-discarded-same-owner-2026-11-09",
    "name": "Arachnoir",
    "symbol": "ARACHN",
    "kind": "ERC721",
    "totalSupply": av.get("totalSupply"),
    "totalMinted": av.get("totalMinted"),
    "freeClaimed": av.get("freeClaimed"),
    "freeMinted": av.get("freeMinted"),
    "FREE_SUPPLY": av.get("FREE_SUPPLY"),
    "MAX_SUPPLY": av.get("MAX_SUPPLY"),
    "freePctVerified": round(100.0 * av["freeClaimed"] / av["FREE_SUPPLY"], 2) if av.get("freeClaimed") is not None and av.get("FREE_SUPPLY") else None,
    "mintOpen": av.get("mintOpen"),
    "userBalance": av.get("balanceOf_user"),
    "freeLeft_user": av.get("freeLeft_user"),
    "freeUsed_user": av.get("freeUsed_user"),
    "firstSeenBlock": None,
    "lastReadBlock": arach.get("block"),
    "lastReadWib": "2026-11-09 13:5x WIB",
    "xVerified": False,
    "velocityVerified": False,
    "website": None,
    "gate": "NOT CHECKED (discarded before gate; contractURI has no website pointer)",
    "owner": arach.get("owner_raw"),
    "launchNote": ("Age UNVERIFIED: earliest public mention Boltbook post by raca.ai ~13:31 WIB 2026-11-09; "
                   "dataseed eth_getLogs 12000-blok window failed (-32005 limit exceeded); Ankr dead (401). "
                   "First-mint time not verified on-chain this run."),
    "baselineNote": ("DITEMUKAN run 1301 via Boltbook ZH (raca.ai ~13:31 WIB) + Sourcify exact_match; agent-shaped "
                     "terverifikasi parent (AGENT_ID()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, totalSupply 752, "
                     "freeClaimed 739/805 = 91.8%, mintOpen 1, freeLeft(user)=1, slot user TERBUKA). TIDAK DILAPORKAN "
                     "sebagai early lead dan TIDAK PERNAH dipromosikan/dieksekusi: owner 0xd76d5918fb337667b22fe37ae2055b5542cf8dc9 "
                     "ADA di same-owner-discards.json (entri Terragent 2026-11-03: owner 0xd76d sama dengan Mechfarm/Dronegent/Hexagent/dll; "
                     "Krillfarm bridge note: owner sama, same-owner discarded). Preseden: Terragent dibuang tanpa laporan ke user; "
                     "Gourdwick dilaporkan early lead 11-02 SEBELUM discard 11-03. Aturan AGENTS.md 2026-11-09: cek discards WAJIB "
                     "sebelum preview/eksekusi; discard = jangan laporkan sebagai lead + jangan eksekusi. Subagent discovery sempat "
                     "merekomendasikan early lead karena tidak memeriksa discards; parent membatalkan rekomendasi itu."),
    "velocityNote": "run 1301: baseline first recorded (totalSupply 752) — velocity NOT passed on baseline alone; moot (discarded).",
    "previousTotalSupply": None,
    "mintedInInterval": None,
    "intervalMinutes": None,
    "currentRatePerMin": None,
    "previousRatePerMin": None,
    "velocityLegPasses": False,
    "supplyView": "totalSupply",
    "PRICE": None,
}
report["discarded_same_owner"].append({"name": "Arachnoir", "address": ARACH,
    "owner": arach.get("owner_raw"),
    "reason": "owner 0xd76d... in same-owner-discards.json (Terragent entry 2026-11-03; same owner as Mechfarm/Dronegent/Hexagent/Krillfarm)"})

# ---- 5. PACTA — FREE POOL EXHAUSTED (verified fresh this run) + gate still FAILED ----
pa = tc.get("PACTA")
if isinstance(pa, dict):
    pa_r = r1301.get("track_c", {}).get("PACTA", {})
    for k in ["freeMinted", "totalSupply"]:
        if isinstance(pa_r, dict) and pa_r.get(k) is not None:
            pa[k] = pa_r[k]
    # fresh targeted read (run-2026-11-09-1301-pacta-verify): freeMinted 55 = MAX_FREE 55, sharesMinted 55
    pa["freeMinted"] = 55
    pa["sharesMinted"] = 55
    pa["freeSharesRemaining"] = 0
    pa["status"] = "excluded-free-pool-exhausted-2026-11-09"
    pa["lastReadBlock"] = BLOCK_1301
    pa["lastReadWib"] = "2026-11-09 13:5x WIB"
    pa["gate"] = ("FAILED (final run 1231, MOOT now — free pool exhausted run 1301): metode A,B,C,G,H,I,J,K,M nihil + "
                  "(L) BscScan live-browser read dicoba 3x (run 1201 Ray a57a7cc568910a5e, run 1231 Ray a57aa89dcf680a5e, "
                  "run 1301 Ray a57acdec29310a5e) — ketiganya diblokir dinding bot Cloudflare. Bukan bukti tidak ada situs, "
                  "tapi tidak ada bukti website. NO preview/mint selama gate gagal; pool gratis kini 0/55.")
    report["track_c_excluded"].append({
        "name": "PACTA", "address": pa.get("sale"),
        "evidence": "freeMinted 12 -> 55/55 MAX_FREE (sharesMinted 55), freeSharesRemaining 0 — verified fresh targeted read run 1301 + reread TC freeMinted=55",
        "note": "Pool gratis habis sejak run 1231. Gate sudah FAILED sebelumnya; tidak pernah dieksekusi. Dilaporkan sekali sebagai perubahan."})

# ---- 6. generic structured-launch-time age exclusions (same logic as run 1231) ----
def parse_wib(s):
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S+07:00", "%Y-%m-%d %H:%M:%S WIB", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone(timedelta(hours=7)))
            return dt
        except Exception:
            continue
    return None

ACTIVE_OK = ("early-lead", "strong-lead", "watchlist-only")
for name, v in list(contracts.items()):
    st = str(v.get("status", ""))
    if not any(x in st for x in ACTIVE_OK):
        continue
    if any(x in st for x in ["minted-by-user", "excluded", "discarded", "paid-only", "sold-out", "soldout"]):
        continue
    t = None
    for f in ["startTimeWib", "firstMintWib", "launchTimeWib", "saleStartWib"]:
        t = parse_wib(v.get(f))
        if t:
            break
    if not t:
        continue
    age_h = (NOW - t).total_seconds() / 3600.0
    if age_h <= 48:
        continue
    r1301d = r1301.get("reread", {}).get(name, {})
    ts = r1301d.get("totalSupply") if isinstance(r1301d, dict) and r1301d.get("totalSupply") is not None else v.get("totalSupply")
    tm = r1301d.get("totalMinted") if isinstance(r1301d, dict) and r1301d.get("totalMinted") is not None else v.get("totalMinted")
    mx = v.get("MAX_SUPPLY")
    sold_out = bool(mx and ((isinstance(ts, (int, float)) and ts >= mx) or
                            (isinstance(tm, (int, float)) and tm >= mx)))
    if sold_out:
        report["age_candidates_kept"].append({"name": name, "age_h": round(age_h, 1), "reason": "sold out — age rule N/A"})
        continue
    mint_open = r1301d.get("mintOpen") if isinstance(r1301d, dict) and r1301d.get("mintOpen") is not None else v.get("mintOpen")
    reason = "age-over-48h-not-sold-out"
    if mint_open == 0:
        reason = "mint-closed (mintOpen=0), age-over-48h"
    report["age_exclusions"].append({"name": name, "address": v.get("address"), "age_h": round(age_h, 1),
                                      "launch_time": t.isoformat(), "totalSupply": ts, "totalMinted": tm,
                                      "reason": reason, "status_was": st})
    del contracts[name]
print(f"age exclusions: {report['age_exclusions']}")
print(f"age kept (sold out): {report['age_candidates_kept']}")

# ---- 7. velocity-pass promotion screening (no promotion without all legs) ----
vel_notes = []
for vp in report["velocity_pass"]:
    old = contracts.get(vp["name"], {})
    fc, fs = old.get("freeClaimed"), old.get("FREE_SUPPLY")
    pct = round(100.0 * fc / fs, 2) if isinstance(fc, (int, float)) and isinstance(fs, (int, float)) and fs else None
    vel_notes.append(f"{vp['name']}: +{vp['minted']} ({vp['ratio']}x) free%={pct} status={old.get('status')} "
                     f"x={old.get('xVerified')} slot={'open' if old.get('freeSlotUserOpen') else 'unverified'} — "
                     f"{'PROMOTION CHECK NEEDED' if pct is not None and pct >= 25 else 'no promotion (free% <25% or unverified / not strong-lead legs)'}")
report["velocity_notes"] = vel_notes

# ---- 8. run notes ----
snap["runNote1301_1109"] = (
    f"Run 1301: re-read {len(r1301.get('reread', {}))} kontrak + {len(r1301.get('track_c', {}))} track_c "
    f"(blok {BLOCK_1301}, interval {INTERVAL_MIN:.1f} mnt vs run 1231); "
    f"velocity LOLOS {len(report['velocity_pass'])}: {', '.join(v['name'] for v in report['velocity_pass']) or 'tidak ada'} — "
    f"promosi: {'; '.join(vel_notes) if vel_notes else 'tidak ada yang lolos'}. "
    f"ARACHNOIR 0xe6ffadcf = SAME-OWNER DISCARD (owner 0xd76d... di same-owner-discards.json, sama dgn Terragent/Mechfarm/Dronegent/Krillfarm): "
    f"TIDAK dilaporkan sebagai early lead, TIDAK dipromosikan, TIDAK dieksekusi; masuk snapshot sbg promotion-discarded-same-owner. "
    f"Minority Pass 0xC4ad3aC9 = free pool HABIS (200/200) — excluded, dilaporkan sekali sbg perubahan. "
    f"PACTA 0x6Cbf2E38 = free pool JUGA HABIS (55/55 MAX_FREE, dari 12 di run 1231) — excluded; gate FAILED kini moot. "
    f"Scan GAGAL CEPAT: Ankr pre-flight 401 x2 + CLI 401 (credential rejected) — watermark TIDAK dimajukan; backfill ikut terdampak. "
    f"Binanceai tetap refund/failed. Bridge tidak berubah (mtime 2026-11-08 18:21 UTC; 8 temuan lama dibiarkan findings). "
    f"Boltbook EN 302/0B, ZH 46.119 B (17 alamat); Sourcify feed 20 entri, 2 baru, 0 shape S1/S2; sweep + route 6: tidak ada proyek baru.")
snap["runNote1301_1109_scan"] = (
    "Run 1301 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok: ATTEMPT 1 FAIL 9,2 dtk HTTP 401, ATTEMPT 2 FAIL 10,9 dtk HTTP 401; "
    "CLI holders test juga 401; surrogate credential ada (placement url_path_segment benar) tapi ditolak Ankr. "
    "Scan leg TIDAK dijalankan (amendment 2026-11-06: pre-flight gagal = fast-fail, lanjut route lain). Watermark tetap 132512564; "
    "gap ke head ~28rb blok (milik backfill, ikut gagal 401). Tidak ada first-seen baru dari scan; triage tidak dijalankan.")
snap["runNote1301_1109_discovery"] = (
    "Run 1301 discovery (Subagent A): Boltbook EN 302/0B + ZH 46.119 B, 17 alamat unik; Sourcify feed 20 (verifiedAt 05:29-06:35Z), "
    "2 baru vs hotseen, keduanya gagal S1/S2; sweep EN+ZH + Square: BURN (hotseen), NOVRA (track_c, pool habis), BNBmeme (stale 26 Okt, "
    "age-excluded); route 6: Odaily/PANews 0 hit, DappBay tanpa listing proyek terkait. Gryphlume + $BI mint dicek, pool habis, bukan lead. "
    "Arachnoir ditemukan subagent sbg early-lead candidate — parent MEMBATALKAN: owner same-owner-discarded (lihat runNote1301). "
    "Thetavox masih di snapshot; pergerakan Boltbook (+76/32 mnt, 401 free left) tercakup re-read rutin (velocity + free% dihitung merge).")
snap["runNote1301_1109_binanceai"] = (
    f"Run 1301 (blok {bna.get('block')}): binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    f"totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0. Sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote1301_1109_age_exclusions"] = (
    f"Run 1301: age-exclusions baru: {json.dumps(report['age_exclusions'])}; "
    f"kept (sold out, age N/A): {json.dumps(report['age_candidates_kept'])}.")
snap["last_run"] = "1301"
snap["last_run_wib"] = "2026-11-09 ~14:0x WIB"
snap["last_run_note"] = ("Run 1301: Arachnoir same-owner discard (TIDAK dilaporkan sbg lead); Minority Pass + PACTA free pool habis (excluded); "
                         "scan fast-fail Ankr 401; velocity lolos "
                         f"{len(report['velocity_pass'])} tanpa promosi; binanceai tetap refund.")
snap["timestamp_wib"] = "2026-11-09 14:0x WIB"

def save_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)

save_atomic(f"{HF}/onchain-snapshot.json", snap)
json.dump(report, open(f"{HF}/run-2026-11-09-1301-merge.json", "w"), indent=1)
print("MERGE DONE. velocity_pass:", report["velocity_pass"])
print("age_exclusions:", report["age_exclusions"])
print("discarded_same_owner:", report["discarded_same_owner"])
print("track_c_excluded:", report["track_c_excluded"])
