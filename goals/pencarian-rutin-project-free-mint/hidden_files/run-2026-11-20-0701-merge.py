#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 07:01 WIB into onchain-snapshot.json.
Main re-read 07:06 WIB (blok 134596488, 49 kontrak) + retry leg ~07:08-07:09 WIB
(blok 134598936, chunk 5, memulihkan bacaan null/transport-error).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama (bukan nol).
Interval velocity 34,0 mnt (0631 ~06:32 -> 0701 ~07:06); TURTLE/LION dari retry ~37 mnt.
Read-only kecuali snapshot + run JSON (tidak ada perubahan started_wib - skrip
0701 sudah memakai zona WIB langsung)."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~07:09 WIB"
MINUTES = 34.0
MINUTES_RETRY = 37.0

snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-20-0701-reread.json"))
interim = json.load(open(BASE + "run-2026-11-20-0701-interim.json"))
prev = json.load(open(BASE + "run-2026-11-20-0631-reread.json"))
retry = json.load(open(BASE + "run-2026-11-20-0701-reread-retry.json"))
verify = json.load(open(BASE + "run-2026-11-20-0701-verify-new.json"))
verifyb = json.load(open(BASE + "run-2026-11-20-0701-verify-new-b.json"))

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
    note = (f"Run 0701 (blok {reread['block']}): {view} {old_sup}->{new_sup} "
            f"(+{delta if delta is not None else '?'}, {round(rate, 4) if rate is not None else '?'} /mnt "
            f"vs prev {prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
            f"{'LOLOS' if vpass else 'GAGAL'}"
            + (f"; free {fp}%." if fp is not None else "; free% UNVERIFIED.")
            + (" DIAM." if not vpass else "."))
    if name == "DGF-CARD":
        note = (f"Run 0701 (blok {reread['block']}): totalMinted {new_sup} (delta {delta}); "
                "age-excluded (first mint 2026-11-04). DIAM.")
    if name == "ARKYN" and vpass:
        note += (" CATATAN: velocity LOLOS run ini (+43, ~9,8x) TAPI free% UNVERIFIED + umur "
                 "UNVERIFIED + X UNVERIFIED -> BUKAN kandidat/strong lead, TIDAK ada promosi/laporan.")
    sv["runNote0701_1120"] = note
    updated.append(name)

# TURTLE / LION from retry leg (not in the 49-contract view list)
for name in ("Prosperity Turtle Agents", "Guardian Lion Agents"):
    sv = contracts[name]
    cv = retry["reads"].get(name, {}).get("views", {})
    old_sup = sv.get("totalSupply")
    new_sup = num(cv, "totalSupply")
    if new_sup is None:
        sv["runNote0701_1120"] = (f"Run 0701 (retry blok {retry['block']}): baca totalSupply GAGAL "
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
    sv["runNote0701_1120"] = (f"Run 0701 (retry blok {retry['block']}, interval ~37 mnt): totalSupply "
        f"{old_sup}->{new_sup} (+{delta}, {round(rate, 4) if rate is not None else '?'} /mnt vs prev "
        f"{prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
        f"{'LOLOS' if vpass else 'GAGAL'}; free {fp}%. Tetap early lead, jauh di bawah ambang. DIAM.")
    updated.append(name)

# pending claim binanceai (retry values; unchanged)
pc = snap.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
bv = retry["reads"].get("binanceai-mint", {}).get("views", {})
pc["lastReadWib"] = NOW_WIB
pc["runNote0701"] = (f"Run 0701 (retry blok {retry['block']}): launched={bv.get('launched')}, "
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
        v["runNote0701_1120"] = "Run 0701 (retry): freeMinted 564 (tidak berubah), watchlist-only-age-unverified. DIAM."
    if sale == "0x84d82e933d7781fe11245e7bbd3eb23dbb963666":
        v["freeMinted"] = 10000
        v["runNote0701_1120"] = "Run 0701: freeMinted 10000 (sold out, sudah dilaporkan). DIAM."

# rediscoveries (already in snapshot - update fresh reads only, no new report)
pocket = contracts["POCKET"]
pocket["totalMinted"] = 2938
pocket["lastReadBlock"] = verifyb["head"]
pocket["lastReadWib"] = NOW_WIB
pocket["runNote0701_1120"] = ("Run 0701 (verifikasi sweep, blok %d): totalMinted 2302->2938 (+636 sejak 12 Nov), "
    "MAX_SUPPLY 5555, FREE_PRICE 0, PAID_PRICE 0,0001 BNB, MAX_FREE_PER_WALLET 1, freeMintedBy(user)=0, "
    "balanceOf(user)=0 (slot terbuka); free counter view TIDAK ADA (free%% UNVERIFIED); situs mencetak "
    "kontrak persis (sudah diketahui); umur tetap UNVERIFIED; status tetap watchlist-only-age-unverified "
    "(+ entri checked-not-lead-age-excluded 16 Nov). Rediscovery sweep - BUKAN temuan baru, TIDAK dilaporkan."
    % verifyb["head"])

yama = tc["YAMA PROJECT"]
yama["totalFreeShares"] = 3081
yama["totalShares"] = 3083
yama["totalPaidShares"] = 2
yama["freeUsed_user"] = False
yama["quotaOf_user"] = 10
yama["isAgent_user"] = True
yama["lastReadBlock"] = verifyb["head"]
yama["lastReadWib"] = NOW_WIB
yama["runNote0701_1120"] = ("Run 0701 (verifikasi sweep, blok %d): totalFreeShares 2667->3081, totalShares "
    "2669->3083, totalPaidShares 2; freeUsed(user)=false, quotaOf(user)=10, isAgent(user)=1, "
    "agentIdRegistry persis; quote(user,1) mentah dua-word (1, 0) - semantik belum diurai (catatan lama: "
    "quote=0); umur tetap UNVERIFIED + website tetap UNVERIFIED; status tetap "
    "watchlist-only-age-website-unverified (+ entri checked-not-lead-age-excluded-track-c 16 Nov). "
    "Rediscovery sweep - BUKAN temuan baru, TIDAK dilaporkan." % verifyb["head"])

vein = tc["Agent Vein"]
vein["freeClaimed"] = 222
vein["lastReadBlock"] = verifyb["head"]
vein["lastReadWib"] = NOW_WIB
vein["runNote0701_1120"] = ("Run 0701 (verifikasi sweep, blok %d): freeClaimed(sale)=222 (176 pada 18 Nov, "
    "klaim situs 222/1.000 - cocok); situs tetap TIDAK mencetak alamat sale (gate website sale UNVERIFIED); "
    "sale-shape tetap TIDAK terverifikasi (tanpa ABI, tanpa registry bytes); umur tetap UNVERIFIED; status "
    "tetap checked-not-sale-shape-2026-11-18. Rediscovery sweep - BUKAN temuan baru, TIDAK dilaporkan."
    % verifyb["head"])

# newly checked (first read this run): 1 Sourcify-new + 2 Boltbook-new, all not agent-shaped
checked = {
    "0xB0926f6cAc10cdB242eCf1aE6A135C1e9D248500": ("checked-not-lead-2026-11-20",
        "Sourcify feed run 0701 (verifiedAt 2026-11-20T00:06:19Z): token, 17 fns, tanpa mint/quote/free/agent - BUKAN agent-shaped, bukan lead."),
    "0x3b1bab350fc3eb708d0aa66cc0b453d50d50deb5": ("checked-not-lead-2026-11-20",
        "Boltbook EN+ZH front page run 0701: kontrak (code 140 byte), tanpa registry bytes, Sourcify tanpa ABI (n_fns 0) - BUKAN agent-shaped, bukan lead."),
    "0xc5dc1f2aa1d962789f1a06fdb199a25c038d7777": ("checked-not-lead-2026-11-20",
        "Boltbook EN+ZH front page run 0701: minimal proxy (code 92 byte), tanpa registry bytes, Sourcify tanpa ABI (n_fns 0) - BUKAN agent-shaped, bukan lead."),
}
for a, (status, note) in checked.items():
    key = "checked-" + a[:10]
    contracts[key] = {"address": a, "status": status, "lastReadWib": NOW_WIB,
                      "lastReadBlock": reread["block"], "baselineNote": note}

snap["last_run"] = "free-mint-search 2026-11-20 07:01 WIB"
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = NOW_WIB
snap["runNote0701_1120"] = (
    "Run 0701 (blok %s main / %s retry): re-read 49 kontrak, 244 eth_call main (42 dtk) + 169 retry "
    "(91,4 dtk, chunk 5). DEGRADASI TRANSPORT: 24 kontrak baca supply null di main read (dataseed chunk "
    "gagal parse); retry memulihkan HIVE 1267 flat, Bubblebruin 2639 flat (free 33,9%%), binanceai "
    "unchanged, bsccat 564; LION tetap gagal baca (nilai 0631 dipertahankan). Velocity: 1 LOLOS - ARKYN "
    "totalMinted +43 (1,26/mnt vs prev 0,129 = 9,8x) TAPI free%% UNVERIFIED + umur UNVERIFIED + X "
    "UNVERIFIED -> BUKAN kandidat/strong lead, DIAM. Free >70%%: STOCK AGENT 82,2%% (913/1111) + "
    "Lumenhold 85,2%% (1278/1500) - umur + website UNVERIFIED -> BUKAN strong lead. TURTLE 13->21 "
    "(23,9%%), LION baca gagal. binanceai pending/refund tidak berubah. bsccat 564, AONE 10000 sold out. "
    "Sweep: Pocket Ai / YAMA / VEIN SEMUANYA rediscovery (sudah di snapshot sejak 10-12 Nov, "
    "age-excluded) - BUKAN baru, TIDAK dilaporkan; bacaan segar dicatat di entri masing-masing. "
    "Sourcify feed: 1 baru (0xB092 token 17 fns), 0 shape-hit. Boltbook EN+ZH: 2 alamat baru, keduanya "
    "bukan agent-shaped. Bridge: 0 not-in-snapshot. Odaily/PANews: 0 hit. Scan leg: pre-flight Ankr 401 "
    "FAST-FAIL (watermark tetap 134086385). TIDAK ada lead baru - diam."
    % (reread["block"], retry["block"]))
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("updated contracts:", len(updated))
print("velocity_pass:", vel_pass)
print("deltas nonzero:", {k: v for k, v in deltas.items() if v})
print("snapshot contracts now:", len(snap["contracts"]))
print("DONE")
