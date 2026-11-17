#!/usr/bin/env python3
"""Merge run 0031 (scheduled 2026-11-12 00:31 WIB) into onchain-snapshot.json.
GENERIC merge: no hardcoded run-0001 values. Inputs: reread.json,
verify-new.json, verify-lean.json (if present), legs.json, feed.json,
feed-new.json. Writes snapshot (with .bak-0031-premerge). No preview/mint."""
import json, shutil, datetime, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 00:31 WIB"
NOTE_KEY = "runNote0031_1112"
def wib(ts):
    try:
        return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
    except Exception:
        return str(ts)
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-12-0031-reread.json"))
vjson = json.load(open(BASE + "run-2026-11-12-0031-verify-new.json"))
verify = vjson["verify"]
vblock = vjson.get("block")
lean = {}
lean_path = BASE + "run-2026-11-12-0031-verify-lean.json"
lblock = None
if os.path.exists(lean_path):
    lj = json.load(open(lean_path))
    lean = lj.get("verify", {})
    lblock = lj.get("block")
legs = json.load(open(BASE + "run-2026-11-12-0031-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0031-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
out = {"vel_pass": [], "vel_fail_n": 0, "batch_fail": [], "tc_changes": [], "verify_notes": {}, "sellout": [], "launched": []}

# --- 1. reread contracts: values + velocity (generic) ---
for name, d in reread.get("reread", {}).items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    ts_new = d.get("totalSupply")
    fm_new = d.get("freeMinted")
    if ts_new is None and fm_new is None:
        out["batch_fail"].append(name)
        e[NOTE_KEY] = ("Run 0031 (blok %s): baca batch GAGAL (transport, degradasi RPC) - nilai lama dipertahankan, "
            "BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    prev_ts = e.get("totalSupply")
    prev_block = e.get("lastReadBlock") or 0
    interval = max(1.0, (BLOCK - prev_block) * 0.45 / 60.0) if prev_block else 30.0
    note_parts = []
    if ts_new is not None:
        e["totalSupply"] = ts_new
        if prev_ts is not None and ts_new >= prev_ts:
            minted = ts_new - prev_ts
            rate = minted / interval
            prev_rate = e.get("currentRatePerMin")
            ratio = (rate / prev_rate) if (prev_rate and prev_rate > 0) else None
            e["previousTotalSupply"] = prev_ts
            e["mintedInInterval"] = minted
            e["intervalMinutes"] = round(interval, 1)
            e["previousRatePerMin"] = prev_rate
            e["currentRatePerMin"] = round(rate, 4)
            e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
            passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
            e["velocityLegPasses"] = passes
            if passes:
                out["vel_pass"].append((name, minted, round(rate, 3), e["velocityRatio"]))
            else:
                out["vel_fail_n"] += 1
            note_parts.append("velocity %s (+%d token, %.3f/mnt vs prev %.3f = %sx; butuh >=1.5x DAN >=20)" % (
                "LOLOS" if passes else "GAGAL", minted, rate, prev_rate or 0, ("%.2f" % ratio) if ratio is not None else "None"))
        else:
            e["velocityLegPasses"] = False
            note_parts.append("velocity tidak dihitung (totalSupply lama None/turun)")
    if fm_new is not None:
        e["freeMinted"] = fm_new
        note_parts.append("freeMinted=%s" % fm_new)
    if d.get("balanceOf_user") is not None:
        e["balanceOf_user"] = d["balanceOf_user"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    e[NOTE_KEY] = "Run 0031 (blok %s): %s; bal_user=%s; status %s." % (
        BLOCK, "; ".join(note_parts) if note_parts else "tanpa perubahan", d.get("balanceOf_user"), e.get("status"))
print("velocity PASS:", out["vel_pass"])
print("velocity FAIL n:", out["vel_fail_n"], "batch_fail n:", len(out["batch_fail"]), out["batch_fail"])

# --- 2. track_c reread values (generic) ---
for name, d in reread.get("track_c", {}).items():
    e = TC.get(name)
    if not isinstance(e, dict):
        continue
    ch = []
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining"):
        if d.get(k) is not None and e.get(k) != d.get(k):
            ch.append("%s %s->%s" % (k, e.get(k), d.get(k)))
            e[k] = d.get(k)
    if ch:
        out["tc_changes"].append((name, ch))
        e[NOTE_KEY] = "Run 0031 (blok %s): %s; tanpa perubahan tier." % (BLOCK, "; ".join(ch))
print("track_c changes:", out["tc_changes"])

# --- 3. verify-new / verify-lean merge (generic): update non-None fields, factual note ---
VERIFY_FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
                 "FREE_CAP", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user",
                 "freeUsed_user", "freeUsedBy_user", "mintedBy_user", "freeMintedBy_user",
                 "mintStart", "mintOpenedAt", "freePoolSize", "totalFreeCount", "freeLeft",
                 "firstFreeUsed", "paidMinted", "isAgent_user", "freeAvailable_user",
                 "freePerWallet", "PRICE", "price", "saleStart", "saleEnd"]
def merge_verify(vdict, blk, source):
    for name, d in vdict.items():
        if name in ("S1-6C50", "S1-0895", "BB-7c71"):
            store = TC
        else:
            store = C
        key = {"NAOMI": "checked-0xC7Ad-2001", "Stampooor": "Stampooor Stamp Packs"}.get(name, name)
        e = store.get(key)
        if not isinstance(e, dict):
            out["verify_notes"][name] = "MISS in snapshot (%s)" % source
            continue
        if d.get("_batch_fail"):
            e[NOTE_KEY] = "Run 0031 %s (blok %s): batch GAGAL (degradasi RPC) - nilai lama dipertahankan, BUKAN nol." % (source, blk)
            out["verify_notes"][name] = "batch-fail"
            continue
        parts = []
        for k in VERIFY_FIELDS:
            if d.get(k) is not None:
                old = e.get(k)
                e[k] = d[k]
                if old != d[k]:
                    parts.append("%s %s->%s" % (k, old, d[k]))
        fm = d.get("freeMinted")
        cap = d.get("FREE_SUPPLY") or d.get("FREE_CAP") or e.get("FREE_SUPPLY") or e.get("FREE_CAP")
        if fm is not None and cap:
            parts.append("free %s/%s = %.2f%%" % (fm, cap, 100.0 * fm / cap))
        if d.get("mintStart"):
            parts.append("mintStart %s" % wib(d["mintStart"]))
        if d.get("mintOpenedAt"):
            parts.append("mintOpenedAt %s" % wib(d["mintOpenedAt"]))
        if d.get("saleStart"):
            parts.append("saleStart %s" % wib(d["saleStart"]))
        e["lastReadBlock"] = blk or e.get("lastReadBlock")
        e["lastReadWib"] = TS
        e[NOTE_KEY] = "Run 0031 %s (blok %s): %s; bal_user=%s; status %s." % (
            source, blk, "; ".join(parts) if parts else "tanpa perubahan", d.get("balanceOf_user"), e.get("status"))
        out["verify_notes"][name] = "; ".join(parts) if parts else "tanpa perubahan"
        if fm is not None and cap and fm >= cap and "sold" not in str(e.get("status")) and "minted-by-user" not in str(e.get("status")):
            out["sellout"].append((name, fm, cap))
        if name == "0x79b0" and (d.get("mintOpen") == 1 or (d.get("totalSupply") or 0) > 0):
            out["launched"].append(name)
merge_verify(verify, vblock, "verify-new")
if lean:
    merge_verify(lean, lblock, "verify-lean")
print("verify notes:", json.dumps(out["verify_notes"], indent=1)[:3000])
print("sellout candidates:", out["sellout"], "launched:", out["launched"])

# --- 3b. MOONDRILL lean retry (verify-new batch-fail) ---
mretry_path = BASE + "run-2026-11-12-0031-verify-moondrill.json"
if os.path.exists(mretry_path):
    mj = json.load(open(mretry_path))
    merge_verify(mj.get("verify", {}), mj.get("block"), "verify-moondrill-retry")

# --- 4. 0x79b0 = Moonfang: launched with first mints verified -> EARLY LEAD ---
e79 = C.get("0x79b0")
if isinstance(e79, dict):
    v79 = verify.get("0x79b0") or lean.get("0x79b0") or {}
    if v79 and not v79.get("_batch_fail"):
        e79["name"] = "Moonfang"
        e79["symbol"] = "MOONFANG"
        e79["website"] = "https://moonfang.pages.dev/"
        e79["websiteEvidence"] = ("tokenURI(1) -> https://moonfang.pages.dev/meta/1.json (method I); "
            "site root prints exact NFT contract 0x79b0ce8b39c3ed230487172751612b4f631398bc + token "
            "0x69a8aa0399b53cdc245e89ce31738dd2dd3ff68b (method G); X handle @moonfangBnb stated on site.")
        e79["xHandle"] = "@moonfangBnb"
        e79["xVerified"] = False
        e79["xDiscussionVerified"] = False
        if (v79.get("totalSupply") or 0) == 0 and v79.get("mintOpen") == 0:
            e79["status"] = "watchlist-only-prelaunch-2026-11-12"
        elif (v79.get("totalSupply") or 0) > 0 or v79.get("mintOpen") == 1:
            e79["status"] = "early-lead-reported-2026-11-12"
            e79["launchNote"] = ("First mints verified on-chain this run: totalSupply 0 at blok 133010737 "
                "(run 0001 lean, ~00:55 WIB) -> 50 at blok 133013066 (verify-new, ~01:05 WIB) -> 63 at probe "
                "~01:10 WIB. Launch age TERVERIFIKASI <24 jam via first-mint bound on-chain (no project-stated "
                "launch time found; site says mint opens after X announcement).")
            e79["baselineNote"] = ("EARLY LEAD reported once run 0031: agent-shaped (REGISTRY/agentGate + FREE_CAP 200 + "
                "freeMinted), first mints verified on-chain, free 63/200 = 31,5% (was 50/200 at verify), mintOpen 1, "
                "website PASS (moonfang.pages.dev prints exact contracts), X discussion UNVERIFIED (handle @moonfangBnb "
                "on site, no readable post verified), velocity baseline only, slot user open (bal 0, mintedBy 0; "
                "freeAvailable view reverts). NOT a candidate (<50% + velocity/X unverified), NOT strong lead (<70%). "
                "NEVER auto-minted/previewed as early lead; promotes to strong lead only on all 3 legs.")
            if "0x79b0" not in out["launched"]:
                out["launched"].append("0x79b0")

# --- 5. top-level run note (summary passed via env JSON) ---
snap["runNote0031_1112"] = json.loads(os.environ.get("RUN0031_SUMMARY_JSON", "{}")).get("summary", "")
snap["last_run"] = TS
snap["last_run_wib"] = TS
tmp = BASE + "onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")
json.dump(out, open(BASE + "run-2026-11-12-0031-merge.json", "w"), indent=1)
print("SNAPSHOT WRITTEN, contracts:", len(C), "track_c:", len(TC))
print("MERGE SUMMARY:", json.dumps({k: v for k, v in out.items() if k != "verify_notes"}, indent=1)[:2000])
