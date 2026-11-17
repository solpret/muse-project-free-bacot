#!/usr/bin/env python3
"""Merge run 0131 (scheduled 2026-11-12 01:31 WIB) into onchain-snapshot.json.
GENERIC merge (adapted from run 0031): inputs reread.json, verify-new.json,
verify-extra.json, legs.json, feed.json, feed-new.json. Writes snapshot
(with .bak-0131-premerge). No preview/mint."""
import json, shutil, datetime, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 01:31 WIB"
NOTE_KEY = "runNote0131_1112"
def wib(ts):
    try:
        return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
    except Exception:
        return str(ts)
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-12-0131-reread.json"))
vjson = json.load(open(BASE + "run-2026-11-12-0131-verify-new.json"))
verify = vjson["verify"]
vblock = vjson.get("block")
xjson = json.load(open(BASE + "run-2026-11-12-0131-verify-extra.json"))
extra = xjson["verify"]
xblock = xjson.get("block")
legs = json.load(open(BASE + "run-2026-11-12-0131-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0131-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
out = {"vel_pass": [], "vel_fail_n": 0, "batch_fail": [], "tc_changes": [], "verify_notes": {}, "sellout": [], "launched": []}

# --- 0. Add Eco + Pickgrid to snapshot BEFORE merge_verify (else MISS) ---
if "Eco" not in C:
    C["Eco"] = {
        "address": "0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3",
        "name": "Eco", "symbol": "ECO", "kind": "ERC721",
        "status": "early-lead-reported-2026-11-12",
        "totalMinted": None, "freeMinted": None, "FREE_CAP": None, "MAX_SUPPLY": 5555,
        "mintOpen": 1, "balanceOf_user": 0,
        "firstSeenBlock": 133015561,
        "launchNote": ("Launch TERVERIFIKASI <24 jam: first mints verified on-chain hot-leg 0109 "
            "(71 free mints, blok 133015561), launch 2026-11-12 01:11:29 WIB; Sourcify verifiedAt 2026-11-11T18:11:38Z."),
        "baselineNote": ("EARLY LEAD reported once by hot-leg run 2026-11-12 01:09 WIB (S1 sale-shape pass, "
            "first mints 71 free verified, free 39/555 wallets = 7,03% saat itu, slot user open, website + X UNVERIFIED). "
            "Main run 0131 hanya menambahkan ke snapshot + re-read (totalMinted 163); TIDAK dilaporkan ulang. "
            "Early lead only; never previewed/minted; promotes to strong lead only on all 3 legs."),
        "website": None, "gate": None, "xVerified": False,
    }
    print("ADDED Eco to snapshot", flush=True)
if "Pickgrid" not in C:
    C["Pickgrid"] = {
        "address": "0x7f541bcc33abed0e64455565da723e949c6f76f0",
        "name": "Pickgrid", "kind": "ERC721",
        "status": "watchlist-only-first-read-2026-11-12",
        "totalMinted": None, "freeMinted": None, "FREE_CAP": 300, "MAX_SUPPLY": None,
        "mintOpen": None, "balanceOf_user": 0,
        "launchNote": ("Umur peluncuran UNVERIFIED: dikenal dari hot-leg leg4 sejak 2026-11-10, waktu first-mint "
            "tidak terverifikasi (Ankr 401 memblokir cek log; kontrak tanpa view mintStart/mintOpenedAt)."),
        "baselineNote": ("Watchlist-only first read main run 0131: free 216/300 = 72% (di atas bar strong lead 70%) "
            "TAPI umur UNVERIFIED sehingga TIDAK BISA promosi ke strong lead; slot user terbuka (bal 0). "
            "Tidak dilaporkan sebagai lead (bukan temuan baru run ini)."),
        "website": None, "gate": None, "xVerified": False,
    }
    print("ADDED Pickgrid to snapshot", flush=True)

# --- 1. reread contracts: values + velocity (generic) ---
for name, d in reread.get("reread", {}).items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    ts_new = d.get("totalSupply")
    fm_new = d.get("freeMinted")
    if ts_new is None and fm_new is None:
        out["batch_fail"].append(name)
        e[NOTE_KEY] = ("Run 0131 (blok %s): baca batch GAGAL (transport, degradasi RPC) - nilai lama dipertahankan, "
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
    e[NOTE_KEY] = "Run 0131 (blok %s): %s; bal_user=%s; status %s." % (
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
        e[NOTE_KEY] = "Run 0131 (blok %s): %s; tanpa perubahan tier." % (BLOCK, "; ".join(ch))
print("track_c changes:", out["tc_changes"])

# --- 3. verify-new / verify-extra merge (generic) ---
VERIFY_FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
                 "FREE_CAP", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user",
                 "freeUsed_user", "freeUsedBy_user", "mintedBy_user", "freeMintedBy_user",
                 "mintStart", "mintOpenedAt", "freePoolSize", "totalFreeCount", "freeLeft",
                 "firstFreeUsed", "paidMinted", "isAgent_user", "freeAvailable_user",
                 "freePerWallet", "PRICE", "price", "saleStart", "saleEnd",
                 "holdsAgentId_user", "freeCountBy_user", "mintsBy_user"]
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
            e[NOTE_KEY] = "Run 0131 %s (blok %s): batch GAGAL (degradasi RPC) - nilai lama dipertahankan, BUKAN nol." % (source, blk)
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
        e[NOTE_KEY] = "Run 0131 %s (blok %s): %s; bal_user=%s; status %s." % (
            source, blk, "; ".join(parts) if parts else "tanpa perubahan", d.get("balanceOf_user"), e.get("status"))
        out["verify_notes"][name] = "; ".join(parts) if parts else "tanpa perubahan"
        if fm is not None and cap and fm >= cap and "sold" not in str(e.get("status")) and "minted-by-user" not in str(e.get("status")):
            out["sellout"].append((name, fm, cap))
merge_verify(verify, vblock, "verify-new")
merge_verify(extra, xblock, "verify-extra")
print("verify notes:", json.dumps(out["verify_notes"], indent=1)[:3000])
print("sellout candidates:", out["sellout"])

# --- 4. Moonfang (0x79b0): already minted by parent ~01:25 WIB (track-C lead direct mint) ---
e79 = C.get("0x79b0")
if isinstance(e79, dict):
    e79["status"] = "minted-by-user-2026-11-12"
    e79["mintTx"] = "0x0ac81d20fd179550f8ec90e5f94120fe8c57297cc432c88af91dd66314743b82"
    e79["mintBlock"] = 133015834
    e79["mintGas"] = 150804
    e79["mintTokenId"] = 176
    e79["userBalance"] = 1
    e79["mintNote0131"] = ("Mint dieksekusi PARENT ~01:25 WIB di bawah otorisasi track-C lead direct mint "
        "(probe blok 133015717: freeMinted 167/200, priceOf(user,1)=0, freeLeftFor(user)=1, canMint=true; "
        "website moonfang.pages.dev terverifikasi metode I+G; audit Binance hasResult=false; preview bersih "
        "000000000 requestId e8847a0c). Tx 0x0ac81d20..., blok 133015834, receipt 1, #176 + 10.000 FANG; "
        "verifikasi pasca: balanceOf 0->1, ownerOf(176)=wallet agent, freeMinted 167->182. Post-mint: TIDAK ada "
        "own market (situs hanya mint) -> TIDAK di-list; rarity: no rarity (888 identik). Sudah dilaporkan ke "
        "chat utama oleh parent; run 0131 hanya merekonsiliasi snapshot, TIDAK melaporkan ulang.")
    print("Moonfang reconciled as minted-by-user", flush=True)

# --- 5. SUDOSAINTS age decision note (kept watchlist-only) ---
es = C.get("SUDOSAINTS")
if isinstance(es, dict):
    es["ageNote0131"] = ("Run 0131: TIDAK di-age-exclude. Deadline konservatif berbasis deploy (00:24 WIB 12 Nov) "
        "sudah lewat, TAPI waktu first-mint tetap UNVERIFIED: kontrak tanpa view mintStart/mintOpenedAt/saleStart "
        "(verify-extra blok 133016762) dan Ankr 401 memblokir cek log first-mint. Deploy time BUKAN launch time "
        "(aturan umur) — item umur-unverified tetap watchlist-only, tidak pernah di-drop diam-diam. "
        "First-sighting 13:12 WIB 11 Nov berarti umur saat run ini paling lama ~12,5 jam bila launch = first-sighting. "
        "Keputusan diulang tiap run bila bukti first-mint muncul.")
    print("SUDOSAINTS age decision recorded", flush=True)

# --- 6. top-level run note ---
snap["runNote0131_1112"] = json.loads(os.environ.get("RUN0131_SUMMARY_JSON", "{}")).get("summary", "")
snap["last_run"] = TS
snap["last_run_wib"] = TS
tmp = BASE + "onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")
json.dump(out, open(BASE + "run-2026-11-12-0131-merge.json", "w"), indent=1)
print("SNAPSHOT WRITTEN, contracts:", len(C), "track_c:", len(TC))
print("MERGE SUMMARY:", json.dumps({k: v for k, v in out.items() if k != "verify_notes"}, indent=1)[:2000])
