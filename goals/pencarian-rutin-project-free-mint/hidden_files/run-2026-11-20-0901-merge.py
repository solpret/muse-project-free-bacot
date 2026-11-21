#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 09:01 WIB into onchain-snapshot.json.
Main re-read ~09:02 WIB (blok 134611962, 49 kontrak, 224 eth_call) + retry leg
(blok 134612275, 156 calls, 77 ok). Baseline = EFEKTIF 0831 (main 0831 + retry
0831 overlay). Interval 28,0 mnt (0831 08:34 -> 0901 09:02). Aturan merge: nilai
baru None / dict-error TIDAK menimpa nilai lama. Read-only kecuali snapshot +
run JSON. Plus: Agent Harvest fresh read, Boltbook triage, Contextgraph refresh."""
import json, shutil
from datetime import datetime as _dt

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~09:15 WIB"
MINUTES = 28.0

shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0901")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-20-0901-reread.json"))
interim = json.load(open(BASE + "run-2026-11-20-0901-interim.json"))
prev_main = json.load(open(BASE + "run-2026-11-20-0831-reread.json"))
prev_retry = json.load(open(BASE + "run-2026-11-20-0831-reread-retry.json"))
retry = json.load(open(BASE + "run-2026-11-20-0901-reread-retry.json"))
harvest = json.load(open(BASE + "harvest-0901.json"))
ctx = json.load(open(BASE + "ctx-0901.json"))

def is_transport_err(v):
    return isinstance(v, dict) and ("JSONDecodeError" in str(v.get("error", "")) or
                                    "transport" in str(v.get("error", "")))

def eff(main, ret):
    out = {"reads": {}}
    for _n, _e in main["reads"].items():
        _cv = dict(_e["views"])
        for _k, _v in ret["reads"].get(_n, {}).get("views", {}).items():
            _cur = _cv.get(_k)
            if (_cur is None or is_transport_err(_cur)) and _v is not None and not is_transport_err(_v):
                _cv[_k] = _v
        out["reads"][_n] = {"address": _e["address"], "views": _cv}
    return out

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

prev = eff(prev_main, prev_retry)
cur = eff(reread, retry)
contracts = snap["contracts"]
by_addr = {}
for k, v in contracts.items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)

updated, vel_pass, deltas = [], [], {}
for name, entry in reread["reads"].items():
    addr = entry["address"]
    cv = cur["reads"][name]["views"]
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
    note = (f"Run 0901 (blok {reread['block']}): {view} {old_sup}->{new_sup} "
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
        note += (f" CATATAN: totalMinted 2802->2811 (+10, ~{round(10/MINUTES,2)}/mnt) <20 token -> "
                 "velocity GAGAL; free% UNVERIFIED + umur UNVERIFIED -> BUKAN kandidat/strong lead, DIAM.")
    sv["runNote0901_1120"] = note
    updated.append(name)

# TURTLE / LION from retry leg
for name in ("Prosperity Turtle Agents", "Guardian Lion Agents"):
    sv = contracts[name]
    cv = retry["reads"].get(name, {}).get("views", {})
    old_sup = sv.get("totalSupply")
    new_sup = num(cv, "totalSupply")
    if new_sup is None:
        sv["runNote0901_1120"] = (f"Run 0901 (retry blok {retry['block']}): baca totalSupply GAGAL "
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
    sv["runNote0901_1120"] = (f"Run 0901 (retry blok {retry['block']}, interval ~{MINUTES} mnt): totalSupply "
        f"{old_sup}->{new_sup} (+{delta}, {round(rate, 4) if rate is not None else '?'} /mnt vs prev "
        f"{prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
        f"{'LOLOS' if vpass else 'GAGAL'}; free {fp}%. Tetap early lead, jauh di bawah ambang. DIAM.")
    updated.append(name)

# pending claim binanceai (retry values; unchanged)
pc = snap.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
bv = retry["reads"].get("binanceai-mint", {}).get("views", {})
for f in ("launched", "failed", "isRefundPhase", "totalShares", "tokenClaimed_user", "refundClaimed_user"):
    if f in bv and bv[f] is not None and not isinstance(bv[f], dict):
        pc[f] = bv[f]
pc["lastReadWib"] = NOW_WIB
pc["runNote0901"] = (f"Run 0901 (retry blok {retry['block']}): launched={bv.get('launched')}, "
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
        v["runNote0901_1120"] = f"Run 0901 (retry blok {retry['block']}): freeMinted {v['freeMinted']} (tidak berubah), watchlist-only-age-unverified. DIAM."
    if sale == "0x84d82e933d7781fe11245e7bbd3eb23dbb963666":
        _fm = num(retry["reads"].get("AONE-sale", {}).get("views", {}), "freeMinted")
        v["freeMinted"] = _fm if _fm is not None else 10000
        v["runNote0901_1120"] = f"Run 0901 (retry blok {retry['block']}): freeMinted {v['freeMinted']} (sold out, sudah dilaporkan). DIAM."

# Contextgraph Graph 4 (ctx-0901.json): nodes 286 -> 293 (+7), participants 276 -> 283
rv = ctx.get("views", {})
cg = contracts.get("Contextgraph Graph 4 (Nodes v2)", {})
old_nodes = cg.get("totalNodes", 286)
new_nodes = rv.get("totalNodes")
delta_nodes = (new_nodes - old_nodes) if isinstance(new_nodes, int) and isinstance(old_nodes, int) else None
cg["totalSupply"] = new_nodes if new_nodes is not None else cg.get("totalSupply")
cg["totalNodes"] = new_nodes if new_nodes is not None else cg.get("totalNodes")
cg["nodesInGraph"] = rv.get("nodesInGraph(4)", cg.get("nodesInGraph"))
cg["participantsOf"] = rv.get("participantsOf(4)", cg.get("participantsOf"))
cg["mintOpen"] = rv.get("mintOpen", cg.get("mintOpen"))
cg["isSealed"] = rv.get("isSealed(4)", cg.get("isSealed"))
cg["balanceOf_user"] = rv.get("balanceOf(user)", cg.get("balanceOf_user"))
cg["nodesOf_user_graph4"] = rv.get("nodesOf(user,4)", cg.get("nodesOf_user_graph4"))
cg["holdsAgentId_user"] = rv.get("holdsAgentId(user)", cg.get("holdsAgentId_user"))
cg["priceFor_user"] = rv.get("priceFor(user)", cg.get("priceFor_user"))
cg["claim_v2_open"] = rv.get("claimOpen", cg.get("claim_v2_open"))
cg["status"] = "user-holds-node-2026-11-20"
cg["previousTotalSupply"] = old_nodes
cg["mintedInInterval"] = delta_nodes
cg["intervalMinutes"] = MINUTES
cg["currentRatePerMin"] = round(delta_nodes / MINUTES, 4) if delta_nodes is not None else cg.get("currentRatePerMin")
cg["velocityRatio"] = None
cg["velocityLegPasses"] = False
cg["velocity_note"] = (f"Run 0901: nodes {old_nodes}->{new_nodes} (+{delta_nodes} dalam ~{MINUTES} mnt, "
                       f"{round(delta_nodes / MINUTES, 3) if delta_nodes is not None else '?'} /mnt, <20 token) -> "
                       "velocity GAGAL; free% global tetap TIDAK terukur.")
cg["lastReadBlock"] = ctx.get("block")
cg["lastReadWib"] = NOW_WIB
cg["runNote0901_1120"] = (f"Run 0901 (ctx blok {ctx.get('block')}): totalNodes {old_nodes}->{new_nodes} (+{delta_nodes}), "
    "participants 276->283, mintOpen=1, isSealed(4)=0, seal tetap 16:00 WIB hari ini. User tetap pegang Node #286 "
    "saja (nodesOf(user,4)=1, balanceOf=1, priceFor=0,0002 BNB) - slot free Graph 4 user TETAP TERPAKAI, tidak ada "
    "node baru milik user. Bukan perubahan yang dilaporkan ulang (sudah dilaporkan sekali hot-leg 08:29). DIAM.")
contracts["Contextgraph Graph 4 (Nodes v2)"] = cg

# Agent Harvest (DUA entri, alamat sama) - fresh read blok harvest-0901.json
hv = harvest.get("harvest_land", {})
for key in ("Agent Harvest Land", "Agent Harvest"):
    e = contracts.get(key)
    if not isinstance(e, dict):
        continue
    for f in ("freeMinted", "totalMinted", "FREE_SUPPLY"):
        if isinstance(hv.get(f), int):
            e[f] = hv[f]
    e["currentPhase"] = hv.get("currentPhase")
    e["phaseMinted"] = hv.get("phaseMinted")
    e["freeOpen"] = hv.get("freeOpen")
    e["phasePauseEnd"] = hv.get("phasePauseEnd")
    e["balanceOf_user"] = hv.get("balanceOf_user")
    e["freeClaimed_user"] = hv.get("freeClaimed_user")
    e["lastReadBlock"] = harvest.get("block")
    e["lastReadWib"] = NOW_WIB
    e["websiteNote"] = ("Website TERVERIFIKASI job utama run 0901: agent-harvest.pages.dev/skill.md dibaca langsung "
                        "(crawl 2026-11-20 02:03 UTC) mencetak kontrak persis (HarvestLand, HarvestSeed, HarvestFarm, "
                        "HarvestToken + registry 0x60B9...022F); X https://x.com/agentharvest_ai tercantum di /skill.md "
                        "proyek sendiri. Koreksi catatan 15 Nov ('belum terverifikasi').")
    e["x"] = "https://x.com/agentharvest_ai"
    e["runNote0901_1120"] = (f"Run 0901 (blok {harvest.get('block')}): freeMinted {hv.get('freeMinted')}/5000 FREE_SUPPLY "
        f"(pool gratis HABIS, tidak berubah), totalMinted {hv.get('totalMinted')} (+2 paid), currentPhase 10, "
        f"phaseMinted 500/500, freeOpen=0, phasePauseEnd=0 - fase terakhir selesai, tidak ada pembukaan free baru. "
        f"freeClaimed(user)=1 (jatah free user SUDAH TERPAKAI), balanceOf(user)=0. Sweep run ini salah label 'NEW' - "
        "proyek SUDAH di snapshot sejak 2/3 Nov (bukan discovery baru). Status tetap watchlist-only; free pool sold out. DIAM.")

# Boltbook triage - checked entries
contracts["checked-0x48af-0901"] = {
    "address": "0x48afa54a08ef30e1af87e12c929cf7700ccde983",
    "status": "checked-not-a-contract-2026-11-20",
    "note": ("Run 0901 triage (Boltbook EN/ZH baru): codelen 0 (eth_getCode 0x), semua view null. "
             "EOA/bukan kontrak. Sourcify ABI 0 functions. Bukan lead. Log only."),
    "lastReadBlock": harvest.get("block"), "lastReadWib": NOW_WIB}
contracts["checked-0xd301-0901"] = {
    "address": "0xd301d472f2e469a1aafa1af6f214e312f1858873",
    "status": "checked-not-a-contract-2026-11-20",
    "note": ("Run 0901 triage (Boltbook EN/ZH baru): codelen 0 (eth_getCode 0x), semua view null. "
             "EOA/bukan kontrak. Sourcify ABI 0 functions. Bukan lead. Log only."),
    "lastReadBlock": harvest.get("block"), "lastReadWib": NOW_WIB}
contracts["checked-0x79f5-0901"] = {
    "address": "0x79F55DAa8a3CF2Eb76EE40e26ff6E244a4cC1eD4",
    "status": "checked-not-a-lead-2026-11-20",
    "note": ("Run 0901 triage (Boltbook EN/ZH baru): Forecast League (FCL), totalSupply 201->203 (+2), "
             "codelen 14838. Sourcify ABI 27 fns (agent_ref by name) TAPI agentRegistry()/agentIdRegistry() "
             "revert, semua free view (freeClaimed/FREE_SUPPLY/freeLeft/freeMinted) revert, tanpa quote - "
             "free% UNVERIFIED, bukan sale-shape (S1/S2 false). Bukan lead/kandidat. Log only."),
    "lastReadBlock": harvest.get("block"), "lastReadWib": NOW_WIB}

# Agent Grove - sweep re-check unchanged
ag = contracts.get("Agent Grove")
if isinstance(ag, dict):
    ag["runNote0901_1120"] = ("Run 0901 (sweep): situs MASIH 'Phase 1 250/250 penuh, Phase 2 buka 06:05 UTC "
        "(13:05 WIB hari ini)' - SAMA seperti 6 Nov; tidak berubah. Tetap watchlist-only-upcoming; "
        "pantau bila Phase 2 benar-benar dibuka. DIAM.")

snap["last_run"] = "free-mint-search 2026-11-20 09:01 WIB"
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = NOW_WIB
snap["runNote0901_1120"] = (
    "Run 0901 (blok %s main / %s retry, interval 28,0 mnt): re-read 49 kontrak, 224 eth_call main "
    "(41,3 dtk) + 156 retry (81,9 dtk, 77 ok). DEGRADASI TRANSPORT BERAT berlanjut: main read 175 error "
    "(dataseed JSONDecodeError); retry memulihkan ARKYN totalMinted 2811 (+10), TURTLE 28 (+4, free 31,8%%), "
    "LION 29 flat (free 33,0%%), binanceai unchanged, bsccat 564, AONE 10000. Velocity: 0 LOLOS (delta "
    "terbesar ARKYN +10 <20). Free >70%%: STOCK AGENT 82,4%% + Lumenhold 85,2%% - umur + website UNVERIFIED "
    "-> BUKAN strong lead. Contextgraph Graph 4: totalNodes 286->293 (+7), user tetap Node #286 saja, slot "
    "free tetap terpakai; seal 16:00 WIB hari ini. Agent Harvest: KOREKSI sweep - BUKAN baru (sudah di "
    "snapshot sejak 2/3 Nov); fresh read freeMinted 5000/5000 pool HABIS, totalMinted 5686, fase 10 selesai, "
    "freeOpen=0, freeClaimed(user)=1; website TERVERIFIKASI job utama (skill.md cetak kontrak persis, X "
    "x.com/agentharvest_ai). Sourcify feed: 0 alamat baru, 0 shape hit. Boltbook EN+ZH: 3 alamat baru - "
    "0x48af + 0xd301 EOA (codelen 0), 0x79f5 Forecast League FCL (totalSupply 203, tanpa free view/quote) - "
    "semua bukan lead. Bridge: 116 kontrak, 0 not-in-snapshot. Scan leg: pre-flight Ankr 401 FAST-FAIL "
    "(watermark tetap 134086385). Sweep: Agent Grove unchanged (Fase 2 buka 13:05 WIB), DGF CARD/AgentBadge "
    "unchanged, fanbeimao pre-launch, Square/Odaily/PANews nihil. TIDAK ada kandidat/strong lead/track-C "
    "lead baru - diam."
    % (reread["block"], retry["block"]))
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("updated contracts:", len(updated))
print("velocity_pass:", vel_pass)
print("deltas nonzero:", {k: v for k, v in deltas.items() if v})
print("snapshot contracts now:", len(snap["contracts"]))
print("DONE")
