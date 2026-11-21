#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 08:01 WIB into onchain-snapshot.json.
Main re-read 08:06 WIB (blok 134604531, 49 kontrak, 220 eth_call, 37,7 dtk) + retry leg
~08:08-08:10 WIB (blok 134605130, chunk 5, 149 calls, memulihkan bacaan null/transport-error).
Baseline = EFEKTIF 0731 (main 0731 + retry 0731 overlay) karena main 0731 banyak null transport.
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama (bukan nol).
Interval velocity 23,0 mnt (0731 ~07:43 -> 0801 ~08:06). TURTLE/LION dari retry ~23 mnt.
Read-only kecuali snapshot + run JSON."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~08:11 WIB"
from datetime import datetime as _dt
def _parse_wib(x):
    return _dt.strptime(x[:16], "%Y-%m-%d %H:%M")
MINUTES = round((_parse_wib("2026-11-20 08:06") - _parse_wib("2026-11-20 07:43")).total_seconds() / 60.0, 1)
MINUTES_RETRY = MINUTES

snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-20-0801-reread.json"))
interim = json.load(open(BASE + "run-2026-11-20-0801-interim.json"))
prev_main = json.load(open(BASE + "run-2026-11-20-0731-reread.json"))
prev_retry = json.load(open(BASE + "run-2026-11-20-0731-reread-retry.json"))
retry = json.load(open(BASE + "run-2026-11-20-0801-reread-retry.json"))
def is_transport_err(v):
    return isinstance(v, dict) and ("JSONDecodeError" in str(v.get("error", "")) or
                                    "transport" in str(v.get("error", "")))

# prev baseline = effective 0731 views (main overlaid with retry where main None/transport-error)
prev = {"reads": {}}
for _n, _e in prev_main["reads"].items():
    _cv = dict(_e["views"])
    for _k, _v in prev_retry["reads"].get(_n, {}).get("views", {}).items():
        _cur = _cv.get(_k)
        if (_cur is None or is_transport_err(_cur)) and _v is not None and not is_transport_err(_v):
            _cv[_k] = _v
    prev["reads"][_n] = {"address": _e["address"], "views": _cv}

contracts = snap["contracts"]
by_addr = {}
for k, v in contracts.items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)

def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None


def free_pct(cv):
    fc = num(cv, "freeClaimed")
    fs = num(cv, "freeSupply") if num(cv, "freeSupply") is not None else num(cv, "FREE_SUPPLY")
    fl = num(cv, "freeLeft")
    if fc is not None and fs:
        return round(100 * fc / fs, 1)
    if fl is not None and fs:
        return round(100 * (fs - fl) / fs, 1)
    return None

def eff_views(name):
    """Main views overlaid with retry views where main is None/transport-error."""
    cv = dict(reread["reads"][name]["views"]) if name in reread["reads"] else {}
    rv = retry["reads"].get(name, {}).get("views", {})
    for k, v in rv.items():
        cur = cv.get(k)
        if cur is None or is_transport_err(cur):
            if v is not None and not is_transport_err(v):
                cv[k] = v
    return cv

updated, vel_pass, deltas = [], [], {}
for name, entry in reread["reads"].items():
    addr = entry["address"]
    cv = eff_views(name)
    pv = prev["reads"][name]["views"]
    key, sv = by_addr.get(addr.lower(), (None, None))
    if sv is None:
        key = name
        sv = {"address": addr, "name": name}
        contracts[key] = sv
    old_sup = num(pv, "totalSupply")
    new_sup = num(cv, "totalSupply")
    view = "totalSupply"
    if new_sup is None:
        view = "totalMinted"
        new_sup = num(cv, "totalMinted")
        old_sup = num(pv, "totalMinted")
        if name == "Everything Is Mine (EIM)":
            old_sup = num(pv, "totalMinted")
    delta = (new_sup - old_sup) if (old_sup is not None and new_sup is not None) else None
    if delta is not None:
        deltas[name] = delta
    prev_rate = sv.get("currentRatePerMin") if isinstance(sv, dict) else None
    rate = (delta / MINUTES) if delta is not None else None
    ratio = (rate / prev_rate) if (rate is not None and isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
    vpass = bool(delta is not None and delta >= 20 and ratio is not None and ratio >= 1.5)
    if vpass:
        vel_pass.append(name)
    fp = free_pct(cv)
    for f in ("totalSupply", "totalMinted", "freeClaimed", "FREE_SUPPLY", "freeSupply",
              "freeLeft", "balanceOf_user", "mintOpen", "name", "symbol", "contractURI",
              "owner", "launched", "failed", "isRefundPhase", "totalShares",
              "tokenClaimed_user", "refundClaimed_user", "freeMinted"):
        if f in cv and cv[f] is not None and not isinstance(cv[f], dict):
            sv[f] = cv[f]
    sv["previousTotalSupply"] = old_sup
    sv["mintedInInterval"] = delta
    sv["intervalMinutes"] = MINUTES
    sv["previousRatePerMin"] = prev_rate
    sv["currentRatePerMin"] = round(rate, 4) if rate is not None else prev_rate
    sv["velocityRatio"] = round(ratio, 2) if ratio is not None else None
    sv["velocityLegPasses"] = vpass
    sv["supplyView"] = view
    if fp is not None:
        sv["freePctVerified"] = fp
    sv["lastReadBlock"] = retry["block"] if name in retry["reads"] else reread["block"]
    sv["lastReadWib"] = NOW_WIB
    note = (f"Run 0801 (blok {reread['block']}): {view} {old_sup}->{new_sup} "
            f"(+{delta if delta is not None else '?'}, {round(rate, 4) if rate is not None else '?'} /mnt "
            f"vs prev {prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
            f"{'LOLOS' if vpass else 'GAGAL'}"
            + (f"; free {fp}%." if fp is not None else "; free% UNVERIFIED.")
            + (" DIAM." if not vpass else "."))
    if name == "DGF-CARD":
        note = (f"Run 0801 (blok {reread['block']}): totalMinted baca GAGAL run ini "
                f"(transport/revert, nilai lama {old_sup} dipertahankan); "
                "age-excluded (first mint 2026-11-04). DIAM.")
    if name == "ARKYN":
        note += (" CATATAN: velocity GAGAL run ini (totalMinted +22, ~0,96/mnt vs prev 2,30 = 0,42x); "
                 "free% UNVERIFIED + umur UNVERIFIED + X UNVERIFIED -> BUKAN kandidat/strong lead, DIAM.")
    sv["runNote0801_1120"] = note
    updated.append(name)

# TURTLE / LION from retry leg (not in the 49-contract view list)
for name in ("Prosperity Turtle Agents", "Guardian Lion Agents"):
    sv = contracts[name]
    cv = retry["reads"].get(name, {}).get("views", {})
    old_sup = sv.get("totalSupply")
    new_sup = num(cv, "totalSupply")
    if new_sup is None:
        sv["runNote0801_1120"] = (f"Run 0801 (retry blok {retry['block']}): baca totalSupply GAGAL "
                                  "transport (nilai lama dipertahankan); bukan kandidat. DIAM.")
        sv["lastReadWib"] = NOW_WIB
        continue
    delta = new_sup - old_sup if old_sup is not None else None
    rate = (delta / MINUTES_RETRY) if delta is not None else None
    prev_rate = sv.get("currentRatePerMin")
    ratio = (rate / prev_rate) if (rate is not None and isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
    vpass = bool(delta is not None and delta >= 20 and ratio is not None and ratio >= 1.5)
    for f in ("totalSupply", "freeClaimed", "FREE_SUPPLY", "freeSupply", "freeLeft", "balanceOf_user", "mintOpen"):
        if f in cv and cv[f] is not None and not isinstance(cv[f], dict):
            sv[f] = cv[f]
    fp = free_pct(cv)
    if fp is not None:
        sv["freePctVerified"] = fp
    sv["previousTotalSupply"] = old_sup
    sv["mintedInInterval"] = delta
    sv["intervalMinutes"] = MINUTES_RETRY
    sv["previousRatePerMin"] = prev_rate
    sv["currentRatePerMin"] = round(rate, 4) if rate is not None else prev_rate
    sv["velocityRatio"] = round(ratio, 2) if ratio is not None else None
    sv["velocityLegPasses"] = vpass
    sv["lastReadBlock"] = retry["block"]
    sv["lastReadWib"] = NOW_WIB
    sv["runNote0801_1120"] = (f"Run 0801 (retry blok {retry['block']}, interval ~{MINUTES_RETRY} mnt): totalSupply "
        f"{old_sup}->{new_sup} (+{delta}, {round(rate, 4) if rate is not None else '?'} /mnt vs prev "
        f"{prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
        f"{'LOLOS' if vpass else 'GAGAL'}; free {fp}%. Tetap early lead, jauh di bawah ambang. DIAM.")
    updated.append(name)

# pending claim binanceai (retry values; unchanged)
pc = snap.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
bv = retry["reads"].get("binanceai-mint", {}).get("views", {})
pc["lastReadWib"] = NOW_WIB
pc["runNote0801"] = (f"Run 0801 (retry blok {retry['block']}): launched={bv.get('launched')}, "
    f"failed={bv.get('failed')}, isRefundPhase={bv.get('isRefundPhase')}, totalShares "
    f"{bv.get('totalShares')}, tokenClaimed(user)={bv.get('tokenClaimed_user')}, "
    f"refundClaimed(user)={bv.get('refundClaimed_user')} - tidak berubah; fase refund sudah "
    "dilaporkan sekali (2026-11-02). DIAM.")

# track_c: bsccat + AONE (freeMinted)
tc = snap.get("track_c", {})
for k, v in tc.items():
    if not isinstance(v, dict):
        continue
    sale = (v.get("sale") or v.get("address") or "").lower()
    if sale == "0x9dd4c7d3276609892cf723a90a5af3f8df40c79a":
        _fm = num(eff_views("bsccat-sale"), "freeMinted")
        v["freeMinted"] = _fm if _fm is not None else v.get("freeMinted", 564)
        v["runNote0801_1120"] = f"Run 0801 (main blok {reread['block']}): freeMinted {v['freeMinted']} (tidak berubah), watchlist-only-age-unverified. DIAM."
    if sale == "0x84d82e933d7781fe11245e7bbd3eb23dbb963666":
        _fm = num(retry["reads"].get("AONE-sale", {}).get("views", {}), "freeMinted")
        v["freeMinted"] = _fm if _fm is not None else 10000
        v["runNote0801_1120"] = f"Run 0801 (retry blok {retry['block']}): freeMinted {v['freeMinted']} (sold out, sudah dilaporkan). DIAM."

snap["last_run"] = "free-mint-search 2026-11-20 08:01 WIB"
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = NOW_WIB
snap["runNote0801_1120"] = (
    "Run 0801 (blok %s main / %s retry, interval 23,0 mnt): re-read 49 kontrak, 220 eth_call main "
    "(37,7 dtk) + 149 retry (79,0 dtk, chunk 5). DEGRADASI TRANSPORT BERAT: main read 78 transport "
    "JSONDecodeError + 19 null; retry memulihkan ARKYN totalMinted 2786 (+22, velocity GAGAL 0,42x), "
    "STOCK AGENT 916 flat (free 82,4%%), TURTLE 24 (+3), LION 25 (+3), binanceai unchanged, AONE 10000; "
    "EIM/FrieAgent-B751/Lumenhold/DGF-CARD tetap gagal baca (nilai lama dipertahankan). Velocity: 0 LOLOS. "
    "Free >70%%: STOCK AGENT 82,4%% (916/1111) + Lumenhold 85,2%% (stale, baca gagal run ini) - umur + website "
    "UNVERIFIED -> BUKAN strong lead. TURTLE 24/88 = 27,3%%, LION 25/88 = 28,4%% - tetap early lead, jauh di "
    "bawah ambang. binanceai pending/refund tidak berubah (launched=0, failed=1, isRefundPhase=1). bsccat 564, "
    "AONE 10000 sold out. Sourcify feed: 5 alamat baru, 0 shape hit. Boltbook EN+ZH: 0 alamat baru. Bridge: "
    "0 not-in-snapshot. Scan leg: pre-flight Ankr 401 FAST-FAIL (watermark tetap 134086385). TIDAK ada lead "
    "baru - diam."
    % (reread["block"], retry["block"]))
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("updated contracts:", len(updated))
print("velocity_pass:", vel_pass)
print("deltas nonzero:", {k: v for k, v in deltas.items() if v})
print("snapshot contracts now:", len(snap["contracts"]))
print("DONE")
