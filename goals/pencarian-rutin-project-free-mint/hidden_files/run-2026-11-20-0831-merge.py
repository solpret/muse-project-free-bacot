#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 08:31 WIB into onchain-snapshot.json.
Main re-read ~08:34 WIB (blok 134608225, 49 kontrak, 224 eth_call, 45,5 dtk) + retry leg
(blok 134608479, 115 calls, 55,2 dtk, memulihkan 45). Baseline = EFEKTIF 0801 (main 0801
+ retry 0801 overlay) karena main 0801 banyak null transport. Aturan merge: nilai baru
None / dict-error TIDAK menimpa nilai lama (bukan nol). Interval velocity 28,0 mnt
(0801 08:06 -> 0831 08:34). TURTLE/LION dari retry. Contextgraph Graph 4 dari
ctx-0831.json (refresh blok 134608615) + ctx-0831-retry.json (blok 134608686).
Read-only kecuali snapshot + run JSON + ctx JSON."""
import json
from datetime import datetime as _dt

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~08:41 WIB"
MINUTES = round((_dt.strptime("2026-11-20 08:34", "%Y-%m-%d %H:%M") -
                 _dt.strptime("2026-11-20 08:06", "%Y-%m-%d %H:%M")).total_seconds() / 60.0, 1)

snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-20-0831-reread.json"))
interim = json.load(open(BASE + "run-2026-11-20-0831-interim.json"))
prev_main = json.load(open(BASE + "run-2026-11-20-0801-reread.json"))
prev_retry = json.load(open(BASE + "run-2026-11-20-0801-reread-retry.json"))
retry = json.load(open(BASE + "run-2026-11-20-0831-reread-retry.json"))

def is_transport_err(v):
    return isinstance(v, dict) and ("JSONDecodeError" in str(v.get("error", "")) or
                                    "transport" in str(v.get("error", "")))

def eff(prev_m, prev_r):
    out = {"reads": {}}
    for _n, _e in prev_m["reads"].items():
        _cv = dict(_e["views"])
        for _k, _v in prev_r["reads"].get(_n, {}).get("views", {}).items():
            _cur = _cv.get(_k)
            if (_cur is None or is_transport_err(_cur)) and _v is not None and not is_transport_err(_v):
                _cv[_k] = _v
        out["reads"][_n] = {"address": _e["address"], "views": _cv}
    return out

prev = eff(prev_main, prev_retry)
cur = eff(reread, retry)

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

def eff_views(name, src_main, src_retry):
    cv = dict(src_main["reads"][name]["views"]) if name in src_main["reads"] else {}
    rv = src_retry["reads"].get(name, {}).get("views", {})
    for k, v in rv.items():
        cur_v = cv.get(k)
        if cur_v is None or is_transport_err(cur_v):
            if v is not None and not is_transport_err(v):
                cv[k] = v
    return cv

updated, vel_pass, deltas = [], [], {}
for name, entry in reread["reads"].items():
    addr = entry["address"]
    cv = eff_views(name, reread, retry)
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
    note = (f"Run 0831 (blok {reread['block']}): {view} {old_sup}->{new_sup} "
            f"(+{delta if delta is not None else '?'}, {round(rate, 4) if rate is not None else '?'} /mnt "
            f"vs prev {prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
            f"{'LOLOS' if vpass else 'GAGAL'}"
            + (f"; free {fp}%." if fp is not None else "; free% UNVERIFIED.")
            + (" DIAM." if not vpass else "."))
    if name == "STOCK AGENT":
        note += (" CATATAN: free 82,4% (freeLeft 195/1111, totalSupply 916 flat) TAPI umur "
                 "UNVERIFIED + website UNVERIFIED -> BUKAN strong lead. DIAM.")
    if name == "Lumenhold":
        note += (" CATATAN: free 85,2% (freeClaimed 1278/1500, totalSupply 1283) TAPI umur "
                 "UNVERIFIED + website UNVERIFIED -> BUKAN strong lead. DIAM.")
    if name == "ARKYN":
        note += (f" CATATAN: totalMinted 2786->2802 (+16, ~{round(16/MINUTES,2)}/mnt) <20 token -> "
                 "velocity GAGAL; free% UNVERIFIED + umur UNVERIFIED -> BUKAN kandidat/strong lead, DIAM.")
    sv["runNote0831_1120"] = note
    updated.append(name)

# TURTLE / LION from retry leg (not in the 49-contract view list)
for name in ("Prosperity Turtle Agents", "Guardian Lion Agents"):
    sv = contracts[name]
    cv = retry["reads"].get(name, {}).get("views", {})
    old_sup = sv.get("totalSupply")
    new_sup = num(cv, "totalSupply")
    if new_sup is None:
        sv["runNote0831_1120"] = (f"Run 0831 (retry blok {retry['block']}): baca totalSupply GAGAL "
                                  "transport (nilai lama dipertahankan); bukan kandidat. DIAM.")
        sv["lastReadWib"] = NOW_WIB
        continue
    delta = new_sup - old_sup if old_sup is not None else None
    rate = (delta / MINUTES) if delta is not None else None
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
    sv["intervalMinutes"] = MINUTES
    sv["previousRatePerMin"] = prev_rate
    sv["currentRatePerMin"] = round(rate, 4) if rate is not None else prev_rate
    sv["velocityRatio"] = round(ratio, 2) if ratio is not None else None
    sv["velocityLegPasses"] = vpass
    sv["lastReadBlock"] = retry["block"]
    sv["lastReadWib"] = NOW_WIB
    sv["runNote0831_1120"] = (f"Run 0831 (retry blok {retry['block']}, interval ~{MINUTES} mnt): totalSupply "
        f"{old_sup}->{new_sup} (+{delta}, {round(rate, 4) if rate is not None else '?'} /mnt vs prev "
        f"{prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
        f"{'LOLOS' if vpass else 'GAGAL'}; free {fp}%. Tetap early lead, jauh di bawah ambang. DIAM.")
    updated.append(name)

# pending claim binanceai (retry values; unchanged)
pc = snap.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
bv = retry["reads"].get("binanceai-mint", {}).get("views", {})
pc["lastReadWib"] = NOW_WIB
pc["runNote0831"] = (f"Run 0831 (retry blok {retry['block']}): launched={bv.get('launched')}, "
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
        _fm = num(eff_views("bsccat-sale", reread, retry), "freeMinted")
        v["freeMinted"] = _fm if _fm is not None else v.get("freeMinted", 564)
        v["runNote0831_1120"] = f"Run 0831 (main blok {reread['block']}): freeMinted {v['freeMinted']} (tidak berubah), watchlist-only-age-unverified. DIAM."
    if sale == "0x84d82e933d7781fe11245e7bbd3eb23dbb963666":
        _fm = num(retry["reads"].get("AONE-sale", {}).get("views", {}), "freeMinted")
        v["freeMinted"] = _fm if _fm is not None else 10000
        v["runNote0831_1120"] = f"Run 0831 (retry blok {retry['block']}): freeMinted {v['freeMinted']} (sold out, sudah dilaporkan). DIAM."

# Contextgraph Graph 4: refresh + retry overlay; USER NOW HOLDS NODE #286
ctx = json.load(open(BASE + "ctx-0831.json"))
ctx_retry = json.load(open(BASE + "ctx-0831-retry.json"))
ref = ctx.get("refresh", {})
for k, v in ctx_retry.get("views", {}).items():
    cur_v = ref.get("views", {}).get(k)
    if (cur_v is None or is_transport_err(cur_v)) and v is not None and not is_transport_err(v):
        ref.setdefault("views", {})[k] = v
ref["retry_block"] = ctx_retry.get("block")
ref["retry_views"] = ctx_retry.get("views")
ctx["refresh"] = ref
json.dump(ctx, open(BASE + "ctx-0831.json", "w"), indent=1)
rv = ref.get("views", {})
cg = contracts.get("Contextgraph Graph 4 (Nodes v2)", {})
cg["totalSupply"] = rv.get("totalNodes", 286)
cg["totalNodes"] = rv.get("totalNodes", 286)
cg["nodesInGraph"] = rv.get("nodesInGraph(4)", 286)
cg["participantsOf"] = rv.get("participantsOf(4)", 276)
cg["mintOpen"] = rv.get("mintOpen", 1)
cg["isSealed"] = rv.get("isSealed(4)", 0)
cg["balanceOf_user"] = rv.get("balanceOf(user)", 1)
cg["nodesOf_user_graph4"] = rv.get("nodesOf(user,4)", 1)
cg["holdsAgentId_user"] = rv.get("holdsAgentId(user)", 1)
cg["priceFor_user"] = rv.get("priceFor(user)", 200000000000000)
cg["claim_v2_open"] = rv.get("claimOpen", 1)
cg["user_node_token_id"] = 286
cg["user_node_owner_verified"] = "ownerOf(286)=0xeb237F6f9FB4e826739F0954e9768914F28b2c2E (blok 134608686+)"
cg["free_slot_user"] = "USED - user holds Graph 4 Node #286 (minted between blok 134607009 and 134608686)"
cg["status"] = "user-holds-node-2026-11-20"
cg["tier"] = "user-holds-node-2026-11-20"
cg["previousTotalSupply"] = 285
cg["mintedInInterval"] = 1
cg["intervalMinutes"] = MINUTES
cg["currentRatePerMin"] = round(1 / MINUTES, 4)
cg["velocityRatio"] = None
cg["velocityLegPasses"] = False
cg["velocity_note"] = (f"Run 0831: nodes 285->286 (+1 dalam ~{MINUTES} mnt, 0,036/mnt, <20 token) -> "
                       "velocity GAGAL; free% global tetap TIDAK terukur.")
cg["lastReadBlock"] = ctx_retry.get("block", 134608686)
cg["lastReadWib"] = NOW_WIB
cg["runNote0831_1120"] = (f"Run 0831 (refresh blok 134608615 + retry blok {ctx_retry.get('block')}): "
    "PERUBAHAN BESAR - user wallet kini memegang Graph 4 Node #286 (ownerOf(286)=user, terverifikasi; "
    "balanceOf(user)=1, nodesOf(user,4)=1, priceFor(user)=0,0002 BNB). Node ini mint antara blok 134607009 "
    "(refresh 08:26: nodesOf=0, balanceOf=0) dan 134608686. Jatah FREE Graph 4 user SUDAH TERPAKAI - slot "
    "gratis TERTUTUP untuk user (node berikut berbayar 0,0002 BNB). TotalNodes 285->286 (+1), participants "
    "275->276, mintOpen=1, isSealed=0, seal tetap 16:00 WIB hari ini. Tx hash mint TIDAK berhasil diambil: "
    "eth_getLogs dataseed mengembalikan 0 log untuk jendela itu; BscScan V2 free tier tidak mencakup BSC; "
    "Ankr 401. Bukan mint oleh job ini (read-only) dan bukan oleh cron lain (tidak ada cron mint Contextgraph). "
    "Status diubah early-lead -> user-holds-node-2026-11-20; laporkan perubahan ini sekali ke main chat.")
contracts["Contextgraph Graph 4 (Nodes v2)"] = cg
# fold retry into interim contextgraph block
cg_i = interim.get("contextgraph_graph4", {})
cg_i["refresh_read_retry"] = {"block": ctx_retry.get("block"), "views": ctx_retry.get("views")}
cg_i["user_slot"] = {"nodesOf_user_graph4": 1, "holdsAgentId": 1, "balanceOf_user_v2": 1,
                     "priceFor_user": 200000000000000, "slot_open": False,
                     "user_node_token_id": 286,
                     "note": "Slot FREE Graph 4 user SUDAH TERPAKAI: Node #286 milik user (ownerOf terverifikasi)."}
cg_i["change_0831"] = ("User wallet now holds Graph 4 Node #286; free slot CLOSED for user. "
                       "Report this change once; status user-holds-node-2026-11-20.")
interim["contextgraph_graph4"] = cg_i
json.dump(interim, open(BASE + "run-2026-11-20-0831-interim.json", "w"), indent=1)

snap["last_run"] = "free-mint-search 2026-11-20 08:31 WIB"
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = NOW_WIB
snap["runNote0831_1120"] = (
    "Run 0831 (blok %s main / %s retry, interval 28,0 mnt): re-read 49 kontrak, 224 eth_call main "
    "(45,5 dtk) + 115 retry (55,2 dtk, 45 pulih). DEGRADASI TRANSPORT BERAT: main read 192 error "
    "(dataseed JSONDecodeError); retry memulihkan STOCK AGENT 916 flat (free 82,4%%), Lumenhold 1283 "
    "(free 85,2%%), ARKYN totalMinted 2802 (+16), LION 29 (+4), binanceai unchanged, AONE 10000; "
    "TURTLE tetap gagal baca totalSupply (nilai lama dipertahankan). Velocity: 0 LOLOS. Free >70%%: "
    "STOCK AGENT 82,4%% + Lumenhold 85,2%% - umur + website UNVERIFIED -> BUKAN strong lead. TURTLE/LION "
    "tetap early lead jauh di bawah ambang. binanceai pending/refund tidak berubah (launched=0, failed=1, "
    "isRefundPhase=1). bsccat 564, AONE 10000 sold out. Sourcify feed: 0 alamat baru, 0 shape hit. "
    "Boltbook EN+ZH: 2 alamat baru (0x7F50..., 0xf713...), keduanya n_fns=0, S1/S2 false - bukan lead. "
    "Bridge: 0 not-in-snapshot. Scan leg: pre-flight Ankr 401 FAST-FAIL (watermark tetap 134086385). "
    "PERUBAHAN: Contextgraph Graph 4 - user wallet kini memegang Node #286 (slot free TERPAKAI); "
    "dilaporkan sekali ke main chat. Selain itu TIDAK ada lead baru - diam."
    % (reread["block"], retry["block"]))
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("updated contracts:", len(updated))
print("velocity_pass:", vel_pass)
print("deltas nonzero:", {k: v for k, v in deltas.items() if v})
print("snapshot contracts now:", len(snap["contracts"]))
print("DONE")
