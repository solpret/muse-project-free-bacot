#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 06:31 WIB into onchain-snapshot.json.
Fixes the run script's WIB bug (it used system UTC for started_wib; correct wall
time is 2026-11-20 ~06:32 WIB) and recomputes velocity with the true ~31-min
interval (0601 ~06:01 -> 0631 ~06:32 WIB). Read-only except the snapshot + fixes
the two run JSONs' started_wib fields."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~06:32 WIB"
MINUTES = 31.0

snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-20-0631-reread.json"))
interim = json.load(open(BASE + "run-2026-11-20-0631-interim.json"))
prev = json.load(open(BASE + "run-2026-11-20-0601-reread.json"))
follow = json.load(open("/tmp/run0601_followup.json"))

# fix wrong started_wib (UTC bug) in the two run files
reread["started_wib"] = "2026-11-20 06:32 WIB"
reread["prev_started_wib"] = "2026-11-20 06:01 WIB"
reread["interval_minutes_corrected"] = MINUTES
interim["started_wib"] = "2026-11-20 06:32 WIB"
json.dump(reread, open(BASE + "run-2026-11-20-0631-reread.json", "w"), indent=1)
json.dump(interim, open(BASE + "run-2026-11-20-0631-interim.json", "w"), indent=1)

contracts = snap["contracts"]
by_addr = {}
for k, v in contracts.items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)

def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None

def free_pct(cv):
    fc, fs, fl = num(cv, "freeClaimed"), num(cv, "freeSupply") or num(cv, "FREE_SUPPLY"), num(cv, "freeLeft")
    if fc is not None and fs:
        return round(100 * fc / fs, 1)
    if fl is not None and fs:
        return round(100 * (fs - fl) / fs, 1)
    return None

# totalMinted baselines at 0601 (followup file); keys are "<name>:totalMinted()"
tm_base = {}
for k, v in follow.items():
    if k.endswith(":totalMinted()") and isinstance(v, int):
        tm_base[k.split(":totalMinted()")[0]] = v

updated, vel_pass, deltas = [], [], {}
for name, entry in reread["reads"].items():
    addr = entry["address"]
    cv = entry["views"]
    pv = prev["reads"][name]["views"]
    key, sv = by_addr.get(addr.lower(), (None, None))
    if sv is None:
        # new entry keyed by reread name
        key = name
        sv = {"address": addr, "name": name}
        contracts[key] = sv
    # supply: totalSupply preferred, else totalMinted
    old_sup = num(pv, "totalSupply")
    new_sup = num(cv, "totalSupply")
    view = "totalSupply"
    if new_sup is None:
        view = "totalMinted"
        new_sup = num(cv, "totalMinted")
        old_sup = tm_base.get(name)
        if name == "Everything Is Mine (EIM)":
            old_sup = tm_base.get("EIM")
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
    # update fields (keep old values when the new read errored)
    for f in ("totalSupply", "totalMinted", "freeClaimed", "FREE_SUPPLY", "freeSupply",
              "freeLeft", "balanceOf_user", "mintOpen", "name", "symbol", "contractURI",
              "owner", "launched", "failed", "isRefundPhase", "totalShares",
              "tokenClaimed_user", "refundClaimed_user", "freeMinted"):
        if f in cv and not isinstance(cv[f], dict):
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
    sv["lastReadBlock"] = reread["block"]
    sv["lastReadWib"] = NOW_WIB
    note = (f"Run 0631 (blok {reread['block']}): {view} {old_sup}->{new_sup} "
            f"(+{delta if delta is not None else '?'}, {round(rate, 4) if rate is not None else '?'} /mnt "
            f"vs prev {prev_rate} = {round(ratio, 2) if ratio is not None else 'n/a'}x) -> velocity "
            f"{'LOLOS' if vpass else 'GAGAL'}"
            + (f"; free {fp}%." if fp is not None else "; free% UNVERIFIED.")
            + " DIAM." if not vpass else ".")
    if name == "DGF-CARD":
        note = (f"Run 0631 (blok {reread['block']}): totalMinted 1748 (baseline baru; angka 1394 di run 0601 "
                "adalah counter website dgnft.pages.dev, metrik berbeda - delta TIDAK dihitung); "
                "age-excluded (first mint 2026-11-04). DIAM.")
        sv["totalMinted"] = 1748
    sv["runNote0631_1120"] = note
    updated.append(name)

# pending claim binanceai (unchanged)
pc = snap.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
pc["lastReadWib"] = NOW_WIB
pc["runNote0631"] = ("Run 0631 (blok %s): launched=0, failed=1, isRefundPhase=1, totalShares 3110, "
                     "tokenClaimed(user)=0, refundClaimed(user)=0 - tidak berubah; fase refund sudah "
                     "dilaporkan sekali (2026-11-02). DIAM." % reread["block"])

# track_c: bsccat + AONE (freeMinted unchanged)
tc = snap.get("track_c", {})
for k, v in tc.items():
    if not isinstance(v, dict):
        continue
    sale = (v.get("sale") or "").lower()
    if sale == "0x9dd4c7d3276609892cf723a90a5af3f8df40c79a":
        v["freeMinted"] = 564
        v["runNote0631_1120"] = "Run 0631: freeMinted 564 (tidak berubah), watchlist-only-age-unverified. DIAM."
    if sale == "0x84d82e933d7781fe11245e7bbd3eb23dbb963666":
        v["freeMinted"] = 10000
        v["runNote0631_1120"] = "Run 0631: freeMinted 10000 (sold out, sudah dilaporkan). DIAM."

# newly checked (first read): 4 Sourcify-new (not agent-shaped) + Boltbook 0x2b50 (not a contract)
checked = {
    "0x7Bc8887fB5515301Fc2721B03D3a23e9b4daCF0f": ("checked-not-lead-2026-11-20",
        "Sourcify feed run 0631 (verifiedAt 2026-11-19T23:38:30Z): token, 17 fns, tanpa mint/quote/free/agent - BUKAN agent-shaped, bukan lead."),
    "0xa31327253236062549E059758DabEA27dA9621FE": ("checked-not-lead-2026-11-20",
        "Sourcify feed run 0631: token, 17 fns, tanpa mint/quote/free/agent - BUKAN agent-shaped, bukan lead."),
    "0x962e149ff8c244c76Bef1D6Abc6DcDcc2AD7bA73": ("checked-not-lead-2026-11-20",
        "Sourcify feed run 0631: NFT, 75 fns, ada mint TAPI tanpa quote/free view/agent ref - BUKAN agent-shaped, bukan lead."),
    "0x2BCB80ddea9D21f4Dea2323c51EB4B2931c405d1": ("checked-not-lead-2026-11-20",
        "Sourcify feed run 0631: token, 17 fns, tanpa mint/quote/free/agent - BUKAN agent-shaped, bukan lead."),
    "0x2b50a42084d502e9091502b2a2f4bb1b9eb112e3": ("checked-not-a-contract-2026-11-20",
        "Boltbook EN+ZH front page run 0631: eth_getCode 0x + balance 0 (blok %s) - BUKAN kontrak (kemungkinan alamat wallet/author di post), bukan lead; dicatat agar tidak di-triase ulang." % reread["block"]),
}
for a, (status, note) in checked.items():
    key = "checked-" + a[:10]
    contracts[key] = {"address": a, "status": status, "lastReadWib": NOW_WIB,
                      "lastReadBlock": reread["block"], "baselineNote": note}

snap["last_run"] = "free-mint-search 2026-11-20 06:31 WIB"
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = NOW_WIB
snap["runNote0631_1120"] = (
    "Run 0631 (blok %s): re-read 49 kontrak, 286 eth_call, 38,6 dtk, 0 transport failure "
    "(153 view-revert yang sudah dikenal). Velocity: 0 lolos (delta maks +4: Lumenhold +4, "
    "TURTLE +4, ARKYN totalMinted +4, LION +3; sisanya 0/+1/+2). Free >70%%: STOCK AGENT 82,2%% "
    "(913/1111) + Lumenhold 85,2%% (1278/1500) - TAPI umur UNVERIFIED + website UNVERIFIED -> "
    "BUKAN strong lead. TURTLE 13/88 (14,8%%), LION 14/88 (15,9%%) - tetap early lead. "
    "binanceai pending/refund tidak berubah. bsccat 564, AONE 10000 sold out - tidak berubah. "
    "Sourcify feed: 4 baru, 0 shape-hit. Boltbook EN+ZH: 1 alamat baru 0x2b50... (BUKAN kontrak: "
    "code 0x, balance 0). Bridge: 0 not-in-snapshot. Sweep: Oathbots/PACTURE/AGENT COSMOS/"
    "AgentForge/RIGBYPASS/JINCHAN semua sudah di snapshot (age-excluded/sold out). Odaily: 0 hit. "
    "Scan leg: pre-flight Ankr 401 FAST-FAIL (watermark tetap 134086385). TIDAK ada lead - diam."
    % reread["block"])
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("updated contracts:", len(updated))
print("velocity_pass:", vel_pass)
print("deltas nonzero:", {k: v for k, v in deltas.items() if v})
print("snapshot contracts now:", len(snap["contracts"]))
print("DONE")
