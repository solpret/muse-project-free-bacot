#!/usr/bin/env python3
"""Merge run 2026-11-09 1231 WIB — re-read velocity, snapshot updates, Reel early lead,
Minority Pass track_c add, Deltavane/Hexrotta age exclusions (verified first-mint times),
seen appends, track_c updates. PACTA gate: BscScan browser read pending at merge time
(task browser-task:8b18b756-8c27-5783-9925-0ffaab5dcf01); gate stays FAILED unless it finds a site.
Writes: onchain-snapshot.json (atomic), onchain-scan-seen.json (atomic),
run-2026-11-09-1231-merge.json (report). Read-only w.r.t. chain; never mints/previews.
"""
import json, os, shutil
from datetime import datetime, timezone, timedelta

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW = datetime(2026, 11, 9, 13, 30, tzinfo=timezone(timedelta(hours=7)))

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
r1201 = json.load(open(f"{HF}/run-2026-11-09-1201-reread.json"))
r1231 = json.load(open(f"{HF}/run-2026-11-09-1231-reread.json"))
tri = json.load(open(f"{HF}/run-2026-11-09-1231-triage.json"))
disc = json.load(open(f"{HF}/run-2026-11-09-1231-discovery-A.json"))
bna = json.load(open(f"{HF}/run-2026-11-09-1231-binanceai.json"))
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
reel = json.load(open(f"{HF}/run-2026-11-09-1231-deepcheck-b319.json"))

BLOCK_1231 = r1231["block"]
BLOCK_1201 = r1201["block"]
INTERVAL_MIN = (BLOCK_1231 - BLOCK_1201) * 0.45 / 60.0
print(f"interval_minutes (block-based): {INTERVAL_MIN:.2f} blocks {BLOCK_1201}->{BLOCK_1231}")

shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-2026-11-09-1231")
shutil.copy(f"{HF}/onchain-scan-seen.json", f"{HF}/onchain-scan-seen.json.bak-2026-11-09-1231")

report = {"run": "2026-11-09-1231", "interval_minutes": round(INTERVAL_MIN, 2),
          "velocity_pass": [], "sellouts_new": [], "slot_changes": [],
          "age_exclusions": [], "age_candidates_kept": [], "early_leads_new": [],
          "track_c_added": []}

contracts = snap.get("contracts", {})
# ---- 1. re-read velocity + snapshot value updates ----
n_upd = 0
for name, d in r1231.get("reread", {}).items():
    old = contracts.get(name)
    if not isinstance(old, dict):
        continue
    base1201 = r1201.get("reread", {}).get(name, {}).get("totalSupply")
    base_snap = old.get("totalSupply")
    new_ts = d.get("totalSupply")
    prev_rate = old.get("currentRatePerMin")
    vel = {"name": name, "baseline": None, "minted": None, "rate": None, "ratio": None, "passes": False, "note": ""}
    kind = str(old.get("kind") or "")
    st = str(old.get("status") or "")
    is_token = ("ERC20" in kind.upper() or "bridge" in kind.lower() or
                "bridge" in st.lower() or "pelengkap-scan" in st.lower() or
                "scan-complement" in st.lower())
    if new_ts is not None and base1201 is not None and not is_token:
        minted = new_ts - base1201
        rate = minted / INTERVAL_MIN
        ratio = (rate / prev_rate) if (prev_rate not in (None, 0)) else None
        vel.update({"baseline": base1201, "minted": minted, "rate": round(rate, 4),
                    "ratio": round(ratio, 2) if ratio is not None else None,
                    "passes": bool(minted >= 20 and ratio is not None and ratio >= 1.5),
                    "note": "baseline=1201 reread"})
        if vel["passes"]:
            report["velocity_pass"].append(vel)
        old["previousTotalSupply"] = base1201
        old["previousRatePerMin"] = prev_rate
        old["currentRatePerMin"] = round(rate, 4)
        old["velocityRatio"] = vel["ratio"]
    elif new_ts is not None and base_snap is not None and new_ts != base_snap:
        vel.update({"note": "baseline 1201 missing (batch fail) — velocity NOT computed over stale snapshot interval"})
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
    old["lastReadBlock"] = BLOCK_1231
    old["lastReadWib"] = "2026-11-09 13:2x WIB"
    if vel["minted"] is not None:
        old["mintedInInterval"] = vel["minted"]
        old["intervalMinutes"] = round(INTERVAL_MIN, 2)
        old["velocityLegPasses"] = vel["passes"]
        old["runNote1231_1109"] = (f"Run 1231 (blok {BLOCK_1231}, interval {INTERVAL_MIN:.1f} mnt vs run 1201): "
            f"{vel['baseline']}->{new_ts} (+{vel['minted']}, {vel['rate']:.3f}/mnt vs prev {prev_rate} = "
            f"{vel['ratio']}x) -> velocity {'LOLOS' if vel['passes'] else 'GAGAL'}; "
            f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')}; bal_user={d.get('balanceOf_user')}; "
            f"status {old.get('status')}.")
        n_upd += 1
    else:
        old["runNote1231_1109"] = (f"Run 1231 (blok {BLOCK_1231}): totalSupply {new_ts} "
            f"(baseline 1201 gagal baca / snapshot stale — velocity TIDAK dihitung); "
            f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')}; bal_user={d.get('balanceOf_user')}; "
            f"status {old.get('status')}.")
print(f"contracts updated: {n_upd} velocity-pass: {[v['name'] for v in report['velocity_pass']]}")

# ---- 2. track_c re-read updates ----
tc = snap.get("track_c", {})
n_tc = 0
for name, d in r1231.get("track_c", {}).items():
    old = tc.get(name)
    if not isinstance(old, dict):
        continue
    prev_free = old.get("freeSharesRemaining")
    for k in ["freeSharesRemaining", "freeMinted", "totalSupply"]:
        if d.get(k) is not None:
            old[k] = d[k]
    if d.get("balanceOf_user") is not None:
        old["balanceOf_user"] = d["balanceOf_user"]
    if d.get("freeClaimed_user") is not None:
        old["freeClaimed_user"] = d["freeClaimed_user"]
    old["lastReadBlock"] = BLOCK_1231
    n_tc += 1
    if prev_free not in (None, 0) and old.get("freeSharesRemaining") == 0:
        report["sellouts_new"].append({"name": name, "prev_free": prev_free})
    if prev_free == 0 and old.get("freeSharesRemaining") not in (None, 0):
        report["slot_changes"].append({"name": name, "note": "free pool reopened?"})
print(f"track_c updated: {n_tc} sellouts_new: {report['sellouts_new']}")

# ---- 3. Reel — NEW early lead (deep-checked this run) ----
REEL = "0xB31947A80AC2e72390B84e3d503d9148f4A9d1ca"
v = reel["views"]
contracts["Reel"] = {
    "address": REEL,
    "status": "early-lead-reported-2026-11-09",
    "name": "Reel",
    "symbol": "REEL",
    "kind": "ERC721",
    "totalSupply": v.get("totalSupply"),
    "totalMinted": v.get("totalMinted"),
    "freeClaimed": None,
    "freeMinted": None,
    "FREE_SUPPLY": None,
    "MAX_SUPPLY": v.get("MAX_SUPPLY"),
    "freePctVerified": None,
    "mintOpen": v.get("mintOpen"),
    "userBalance": v.get("balanceOf_user"),
    "freeClaimed_user": None,
    "userSlotNote": "Slot UNVERIFIED: no freeClaimed/free view in ABI (all free views revert) — cannot confirm user slot.",
    "firstSeenBlock": reel["first_block"],
    "firstMintWib": reel["first_mint_wib"],
    "firstMintTx": None,
    "lastReadBlock": BLOCK_1231,
    "lastReadWib": "2026-11-09 13:2x WIB",
    "xVerified": False,
    "velocityVerified": False,
    "website": None,
    "gate": "NOT CHECKED (early lead — never previewed/minted; contractURI() empty; address search 0 hits)",
    "launchNote": ("First mint verified on-chain: first Transfer-from-zero at block 132531650, "
                   "2026-11-09 12:51:29 WIB (scan window 132531598-132532597); age ~40 min at report, WITHIN 48h."),
    "baselineNote": ("EARLY lead reported once run 1231: agent-shaped (Sourcify exact_match ABI with agentIdRegistry + "
                     "firstMint/claimedFirst/laneMinted + mint + PRICE; registry bytes in code), first mints verified "
                     "on-chain in run (11 mints/11 minters in scan window, totalMinted 73). Free path UNVERIFIED: NO "
                     "free-mint function and NO free view in ABI (freeMinted/freeClaimed/FREE_SUPPLY all revert); PRICE "
                     "exists (paid lane). Free% UNVERIFIED, user slot UNVERIFIED, X UNVERIFIED, website UNVERIFIED "
                     "(contractURI() empty; raw address search 0 hits). Owner 0x41a192cb1cc16cc1ff98dfa9c338f436b41fa5b3 "
                     "NOT in same-owner-discards. Promotes to strong lead only on all 3 legs (age<=48h + free>=25% "
                     "verified + slot open); to candidate only on ALL criteria + safety. NEVER preview/mint as early lead."),
    "velocityNote": "run 1231: baseline first recorded (totalMinted 73, rate n/a) — velocity NOT passed on baseline alone.",
    "previousTotalSupply": None,
    "mintedInInterval": None,
    "intervalMinutes": None,
    "currentRatePerMin": None,
    "previousRatePerMin": None,
    "velocityLegPasses": False,
    "supplyView": "totalMinted",
    "owner": "0x41a192cb1cc16cc1ff98dfa9c338f436b41fa5b3",
    "PRICE": None,
    "scanWindow": "132531598-132532597",
    "scanMints": 11,
    "scanMinters": 11,
}
report["early_leads_new"].append({"name": "Reel", "address": REEL})

# ---- 4. Minority Pass — track-C lead (reported once by hot-leg 1239, gate-blocked); add to track_c ----
MINORITY = "0xC4ad3aC9e8994867210a3f6FDb779211187d19Fa"
tc["Minority Pass"] = {
    "name": "Minority Pass",
    "sale": MINORITY,
    "address": MINORITY,
    "token": MINORITY,
    "tokenNote": "Single-contract S1 (sale+token same contract per hot-leg 1239 shape: mint+quote+freeMinted+agent; separate token address unverified).",
    "status": "track-c-lead-gate-blocked-2026-11-09",
    "shape": "S1",
    "sourcifyMatch": "exact_match (hot-leg 1239)",
    "freeMinted": 67,
    "FREE_SUPPLY": 200,
    "freeSharesRemaining": 133,
    "MAX_SUPPLY": None,
    "totalSupply": 67,
    "freeClaimed_user": None,
    "balanceOf_user": 0,
    "userSlotNote": "Slot OPEN per hot-leg 1239 verification (free pool 133 left); freeClaimed(user) not yet read — re-verify next run.",
    "firstSaleWib": "2026-11-09 ~12:17 WIB (age 28 min at hot-leg 12:45)",
    "firstSaleBlock": 132531744,
    "launchNote": "First share mint verified on-chain in run 1231 scan window (9 mints, first block 132531744); Sourcify verifiedAt 2026-11-09 is verification time, NOT launch time.",
    "gate": "FAILED (hot-leg 1239 + run 1231 discovery: methods A,B,C,G,H,I,J,M tried, no verified website; BscScan browser read (L) pending/Cloudflare-blocked). NO preview/mint while gate fails.",
    "lastReadBlock": BLOCK_1231,
    "lastReadWib": "2026-11-09 13:2x WIB",
}
report["track_c_added"].append({"name": "Minority Pass", "address": MINORITY})

# ---- 5. seen appends (triage first-seen only, absent from seen AND snapshot) ----
scan = json.load(open(f"{HF}/run-2026-11-09-1231-scan.json"))
seen_contracts = seen.setdefault("contracts", {})
seen_top_lows = {k.lower() for k in seen}
seen_nested_lows = {k.lower() for k in seen_contracts}
if isinstance(seen.get("known_older_leads"), dict):
    seen_top_lows |= {k.lower() for k in seen["known_older_leads"]}
elif isinstance(seen.get("known_older_leads"), list):
    seen_top_lows |= {str(x).lower() for x in seen["known_older_leads"]}
snap_addrs = {str(vv.get("address", "")).lower() for vv in contracts.values() if isinstance(vv, dict)}
snap_addrs |= {str(vv.get("address", "")).lower() for vv in tc.values() if isinstance(vv, dict) and vv.get("address")}
added = 0
raw_by_addr = {c["address"].lower(): c for c in scan.get("contracts_raw", [])}
for t in tri.get("first_seen_triage", []):
    key = t["address"].lower()
    if key in seen_top_lows or key in seen_nested_lows or key in snap_addrs:
        continue
    seen_contracts[key] = raw_by_addr.get(key, {}).get("first_block", t.get("first_block"))
    added += 1
print(f"seen appended: {added}")
report["seen_appended"] = added

# ---- 6. age exclusions ----
# 6a. Verified first-mint times (deep-dive this run): Deltavane + Hexrotta.
VERIFIED_AGE = [
    {"name": "Deltavane", "address": "0xFcfdC06c85877D3F2D316595882e1AA9E7f2EebC",
     "first_mint_wib": "2026-11-03 15:31:18 WIB", "first_seen_block": 131401297,
     "evidence": "mint existed at block 131401297 (dataseed block timestamp 2026-11-03 15:31:18 WIB) — launch <= that time, age >= ~5d22h at run"},
    {"name": "Hexrotta", "address": "0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9",
     "first_mint_wib": "2026-11-02 14:04:15 WIB", "first_seen_block": 131197748,
     "evidence": "mint existed at block 131197748 (dataseed block timestamp 2026-11-02 14:04:15 WIB) — launch <= that time, age >= ~6d23h at run"},
]
for item in VERIFIED_AGE:
    name = item["name"]
    old = contracts.get(name)
    if not isinstance(old, dict):
        continue
    r1231d = r1231.get("reread", {}).get(name, {})
    ts = r1231d.get("totalSupply") if r1231d.get("totalSupply") is not None else old.get("totalSupply")
    tm = r1231d.get("totalMinted") if r1231d.get("totalMinted") is not None else old.get("totalMinted")
    mx = old.get("MAX_SUPPLY")
    sold_out = bool(mx and ((isinstance(ts, (int, float)) and ts >= mx) or
                            (isinstance(tm, (int, float)) and tm >= mx)))
    if sold_out:
        report["age_candidates_kept"].append({"name": name, "reason": "sold out — age rule N/A"})
        continue
    fc = r1231d.get("freeClaimed") if r1231d.get("freeClaimed") is not None else old.get("freeClaimed")
    fs = r1231d.get("FREE_SUPPLY") if r1231d.get("FREE_SUPPLY") is not None else old.get("FREE_SUPPLY")
    report["age_exclusions"].append({"name": name, "address": item["address"],
                                      "launch_time": item["first_mint_wib"],
                                      "totalSupply": ts, "free": f"{fc}/{fs}",
                                      "reason": "age-over-48h-not-sold-out (verified first-mint time)",
                                      "status_was": old.get("status"), "evidence": item["evidence"]})
    del contracts[name]

# 6b. Generic structured-launch-time scan (same logic as run 1201).
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
    r1231d = r1231.get("reread", {}).get(name, {})
    ts = r1231d.get("totalSupply") if r1231d.get("totalSupply") is not None else v.get("totalSupply")
    tm = r1231d.get("totalMinted") if r1231d.get("totalMinted") is not None else v.get("totalMinted")
    mx = v.get("MAX_SUPPLY")
    sold_out = bool(mx and ((isinstance(ts, (int, float)) and ts >= mx) or
                            (isinstance(tm, (int, float)) and tm >= mx)))
    if sold_out:
        report["age_candidates_kept"].append({"name": name, "age_h": round(age_h, 1), "reason": "sold out — age rule N/A"})
        continue
    mint_open = r1231d.get("mintOpen") if r1231d.get("mintOpen") is not None else v.get("mintOpen")
    reason = "age-over-48h-not-sold-out"
    if mint_open == 0:
        reason = "mint-closed (mintOpen=0), age-over-48h"
    report["age_exclusions"].append({"name": name, "address": v.get("address"), "age_h": round(age_h, 1),
                                      "launch_time": t.isoformat(), "totalSupply": ts, "totalMinted": tm,
                                      "reason": reason, "status_was": st})
    del contracts[name]
print(f"age exclusions: {report['age_exclusions']}")
print(f"age kept (sold out): {report['age_candidates_kept']}")

# ---- 7. run notes ----
pacta = tc.get("PACTA", {})
snap["runNote1231_1109"] = (
    "Run 1231: re-read 589/594 kontrak + 80/80 track_c (blok 132532573, interval 48,5 mnt vs run 1201); "
    "velocity LOLOS 3 (Deltavane +70 38,6x, Hexrotta +69 38,1x, Skyagent +67 18,5x) TAPI ketiganya GAGAL promosi: "
    "Deltavane + Hexrotta AGE-EXCLUDED (mint pertama terverifikasi 2026-11-03 15:31 WIB dan 2026-11-02 14:04 WIB, "
    "umur >48 jam, belum sold out — dihapus dari watchlist); Skyagent sudah age-excluded sejak 2026-11-06. "
    "Reel (REEL) 0xB31947A8 = EARLY LEAD BARU (dilaporkan sekali): first mint 12:51:29 WIB, totalMinted 73, "
    "agent-shaped (agentIdRegistry + exact_match), free path UNVERIFIED (tanpa freeMint/free view; PRICE ada). "
    "Minority Pass 0xC4ad3aC9 = track-C lead (sudah dilaporkan sekali hot-leg 1239, gate-blocked) — ditambahkan ke track_c, "
    "TIDAK dilaporkan ulang. PACTA freeMinted 8->12 (pool ~43), gate website tetap FAILED (metode H/I/J/A/K/M nihil; "
    "BscScan browser read (L) pending saat merge). Scan SUKSES: window 132531598-132532597 (1000 blok), 40 panggilan Ankr, "
    "0 error, 96 NFT + 430 ERC20-mint; enrich dihentikan dini (Sourcify lambat, 3/100) — file partial dipakai triage "
    "(contracts_raw lengkap). 8 first-seen (triage: 0 S1/S2; 6 kontrak 1-mint registry-bytes saja = log only). "
    "5c: 5 baru dicek, 0 sale-shape. Binanceai tetap refund/failed. Bridge tidak berubah (mtime 2026-11-08 18:21; 0 baru). "
    "Boltbook EN+ZH dibaca langsung (crawl ~12:59-13:00 WIB): Lenx 128->208 free (reread: 231), Lorith free lane SOLD OUT, "
    "BACKDOOR rug warning (exclude), KIJIN alamat unverified, Sora Agent mint revert (bukan free).")
snap["runNote1231_1109_scan"] = (
    "Run 1231 scan: pre-flight OK 20,3 dtk (head 132532454, 191 log/50 blok). Window 132531598-132532597 (1000 blok, cap amendment), "
    "40 panggilan Ankr, 0 error, 96 NFT + 430 ERC20-mint. Enrich dihentikan setelah 3/100 (Sourcify terdegradasi — "
    "error:JSONDecodeError massal seperti run 1201; file partial dipakai triage, contracts_raw lengkap). "
    "8 first-seen: Reel 0xB31947A8 (11 mint, agent-shaped — EARLY LEAD), Minority Pass 0xC4ad3aC9 (9 mint, track-C lead hot-leg), "
    "6 kontrak 1-mint registry-bytes saja (bentuk unverified, log only). Watermark TIDAK dimajukan (milik backfill; gap ~22,8rb blok). "
    "5c: 5 baru dicek, 0 S1/S2.")
snap["runNote1231_1109_discovery"] = (
    "Run 1231 discovery (Subagent A): NOTHING NEW selain Reel (scan) + Minority Pass (hot-leg). Boltbook EN+ZH dibaca langsung. "
    "Sourcify feed 20 entri: 4 baru vs hot-leg 1239, none sale/agent-shaped (2x template 'spots' sale tanpa free view — "
    "WEBSITE()/TWITTER() getters belum dibaca, flag untuk run berikut). Odaily/PANews 0 mention. Square: hanya MOLT AGENT "
    "(excluded) + panduan lama. Bridge mtime tidak berubah (0 baru); 8 temuan lama tidak-di-snapshot dibiarkan sebagai findings "
    "(1 same-owner-discarded Krillfarm — tidak pernah dipromosikan). PACTA gate tetap FAILED (H/I/J/A/K/M).")
snap["runNote1231_1109_binanceai"] = (
    f"Run 1231 (blok {bna.get('block')}): binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    f"totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0. Sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote1231_1109_age_exclusions"] = (
    f"Run 1231: age-exclusions baru: {json.dumps(report['age_exclusions'])}; "
    f"kept (sold out, age N/A): {json.dumps(report['age_candidates_kept'])}.")
snap["last_run"] = "1231"
snap["last_run_wib"] = "2026-11-09 ~13:3x WIB"
snap["last_run_note"] = ("Run 1231: 1 early lead baru (Reel) + 2 age-exclusions (Deltavane, Hexrotta) + Minority Pass masuk track_c "
                         "(gate-blocked, sudah dilaporkan hot-leg); PACTA gate tetap FAILED (browser BscScan pending); "
                         "velocity lolos 3 tapi tidak ada promosi; scan sukses; binanceai tetap refund.")
snap["timestamp_wib"] = "2026-11-09 13:3x WIB"

def save_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)

save_atomic(f"{HF}/onchain-snapshot.json", snap)
save_atomic(f"{HF}/onchain-scan-seen.json", seen)
json.dump(report, open(f"{HF}/run-2026-11-09-1231-merge.json", "w"), indent=1)
print("MERGE DONE. velocity_pass:", report["velocity_pass"])
print("age_exclusions:", report["age_exclusions"])
print("early_leads_new:", report["early_leads_new"])
print("track_c_added:", report["track_c_added"])
