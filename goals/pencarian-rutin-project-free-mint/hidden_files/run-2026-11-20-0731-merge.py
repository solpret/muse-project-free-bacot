#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 07:31 WIB into onchain-snapshot.json.
Main re-read 07:06 WIB (blok 134596488, 49 kontrak) + retry leg ~07:08-07:09 WIB
(blok 134598936, chunk 5, memulihkan bacaan null/transport-error).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama (bukan nol).
Interval velocity 34,0 mnt (0631 ~06:32 -> 0701 ~07:06); TURTLE/LION dari retry ~37 mnt.
Read-only kecuali snapshot + run JSON (tidak ada perubahan started_wib - skrip
0701 sudah memakai zona WIB langsung)."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~07:48 WIB"
MINUTES = 37.0
MINUTES_RETRY = 39.0

snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-20-0731-reread.json"))
interim = json.load(open(BASE + "run-2026-11-20-0731-interim.json"))
prev = json.load(open(BASE + "run-2026-11-20-0701-reread.json"))
retry = json.load(open(BASE + "run-2026-11-20-0731-reread-retry.json"))

contracts = snap["contracts"]
by_addr = {}
for k, v in contracts.items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)

def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None

def is_transport_err(v):
    return isinstance(v, dict) and ("JSONDecodeError" in str(v.get("error", "")) or
                                    "transport" in str(v.get("error", "")))

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
    note = (f"Run 0731 (blok {reread['block']}): {view} {old_sup}->{new_sup} "
            f"(+{delta if delta is not None else '?'}, {round(rate, 4) if rate is not None else '?'} /mnt "
            f"vs prev {prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
            f"{'LOLOS' if vpass else 'GAGAL'}"
            + (f"; free {fp}%." if fp is not None else "; free% UNVERIFIED.")
            + (" DIAM." if not vpass else "."))
    if name == "DGF-CARD":
        note = (f"Run 0731 (blok {reread['block']}): totalMinted {new_sup} (delta {delta}); "
                "age-excluded (first mint 2026-11-04). DIAM.")
    if name == "ARKYN" and vpass:
        note += (" CATATAN: velocity LOLOS run ini (+85, ~1,82x) TAPI free% UNVERIFIED + umur "
                 "UNVERIFIED + X UNVERIFIED -> BUKAN kandidat/strong lead, TIDAK ada promosi/laporan.")
    sv["runNote0731_1120"] = note
    updated.append(name)

# TURTLE / LION from retry leg (not in the 49-contract view list)
for name in ("Prosperity Turtle Agents", "Guardian Lion Agents"):
    sv = contracts[name]
    cv = retry["reads"].get(name, {}).get("views", {})
    old_sup = sv.get("totalSupply")
    new_sup = num(cv, "totalSupply")
    if new_sup is None:
        sv["runNote0731_1120"] = (f"Run 0731 (retry blok {retry['block']}): baca totalSupply GAGAL "
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
    sv["runNote0731_1120"] = (f"Run 0731 (retry blok {retry['block']}, interval ~37 mnt): totalSupply "
        f"{old_sup}->{new_sup} (+{delta}, {round(rate, 4) if rate is not None else '?'} /mnt vs prev "
        f"{prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
        f"{'LOLOS' if vpass else 'GAGAL'}; free {fp}%. Tetap early lead, jauh di bawah ambang. DIAM.")
    updated.append(name)

# pending claim binanceai (retry values; unchanged)
pc = snap.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
bv = retry["reads"].get("binanceai-mint", {}).get("views", {})
pc["lastReadWib"] = NOW_WIB
pc["runNote0731"] = (f"Run 0731 (retry blok {retry['block']}): launched={bv.get('launched')}, "
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
        v["freeMinted"] = num(retry["reads"].get("bsccat-sale", {}).get("views", {}), "freeMinted") or 564
        v["runNote0731_1120"] = "Run 0731 (retry): freeMinted 564 (tidak berubah), watchlist-only-age-unverified. DIAM."
    if sale == "0x84d82e933d7781fe11245e7bbd3eb23dbb963666":
        v["freeMinted"] = 10000
        v["runNote0731_1120"] = "Run 0731: freeMinted 10000 (sold out, sudah dilaporkan). DIAM."

snap["last_run"] = "free-mint-search 2026-11-20 07:31 WIB"
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = NOW_WIB
snap["runNote0731_1120"] = (
    "Run 0731 (blok %s main / %s retry): re-read 49 kontrak, 204 eth_call main (44,9 dtk) + 157 retry "
    "(77,7 dtk, chunk 5). DEGRADASI TRANSPORT: 18 kontrak baca supply null di main read (dataseed chunk "
    "gagal parse JSON); retry memulihkan HIVE 1267 flat, Bubblebruin 2639 flat (free 33,9%%), binanceai "
    "unchanged, bsccat 564, TURTLE 21 flat, LION 22 flat; ADRAW + ARKYN-retry tetap gagal baca (nilai main/"
    "lama dipertahankan). Velocity: 1 LOLOS - ARKYN totalMinted +85 (2,30/mnt vs prev 1,26 = 1,82x) TAPI "
    "free%% UNVERIFIED + umur UNVERIFIED + X UNVERIFIED -> BUKAN kandidat/strong lead, DIAM. Free >70%%: "
    "STOCK AGENT 82,4%% (916/1111) + Lumenhold 85,2%% (1278/1500) - umur + website UNVERIFIED -> BUKAN "
    "strong lead. TURTLE 21/88 = 23,9%%, LION 22/88 = 25,0%% - tetap early lead, jauh di bawah ambang. "
    "binanceai pending/refund tidak berubah (launched=0, failed=1, isRefundPhase=1). bsccat 564, AONE "
    "10000 sold out. Sweep subagent: 0 temuan baru (Square 25 Okt-2 Nov semua age-excluded; AI frog "
    "berbayar; fanbeimao pre-launch) + rediscovery lama; Odaily/PANews 0 hit. Sourcify feed: 0 baru. "
    "Boltbook EN+ZH: 0 alamat baru. Bridge: 0 not-in-snapshot. Scan leg: pre-flight Ankr 401 FAST-FAIL "
    "(watermark tetap 134086385). TIDAK ada lead baru - diam."
    % (reread["block"], retry["block"]))
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("updated contracts:", len(updated))
print("velocity_pass:", vel_pass)
print("deltas nonzero:", {k: v for k, v in deltas.items() if v})
print("snapshot contracts now:", len(snap["contracts"]))
print("DONE")
