#!/usr/bin/env python3
"""Finalize run 2026-11-07 04:01 WIB — parent merge (pattern run 0331).
Backs up snapshot + track-c-checked + scan-state + seen, merges reread
(non-None only) + velocity + track_c reread, merges 5c checked (7, verdict
not_verified = completed check, no transport-failed), advances scan watermark
to 132077511 (scan leg left it at 132074797), records skipped gap
132074798-132076511 for backfill, adds scan contracts absent from the seen
file, applies the 48h age rule to the 6 candidates (2 sold-out skipped, 4
removed; full entries preserved in run-2026-11-07-0401-age-removed.json).
NO preview/mint/claim/sign/transaction."""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0401"
for f in ("onchain-snapshot.json", "track-c-scan-checked.json",
          "onchain-scan-state.json", "onchain-scan-seen.json"):
    shutil.copy(f"{HF}/{f}", f"{HF}/{f}.bak-20261107-{RUN}")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-07-{RUN}-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-07-{RUN}-velocity.json"))
fivec = json.load(open(f"{HF}/run-2026-11-07-{RUN}-5c-newscan.json"))
age = json.load(open(f"{HF}/run-2026-11-07-{RUN}-age-candidates.json"))
scan = json.load(open(f"{HF}/onchain-scan-2026-11-07-{RUN}.json"))
REREAD_BLOCK = reread["block"]  # 132077487
contracts = snap["contracts"]
tc = snap.setdefault("track_c", {})

# 0. pre-merge deltas for run notes (special items)
def old_total(name):
    e = contracts.get(name) or {}
    return e.get("totalSupply"), e.get("totalMinted")
onlyai_old = old_total("ONLYAI-Crystals")
sage_old = old_total("Sage Trials")

# 1. merge reread (non-None only)
merged = 0; none_only = 0
for name, rv in reread["reread"].items():
    if name not in contracts or not isinstance(rv, dict):
        continue
    e = contracts[name]
    any_val = False
    for k, v in rv.items():
        if k in ("address", "_batch_error", "_batch_v2"):
            continue
        if v is not None:
            e[k] = v; any_val = True
    if not any_val:
        none_only += 1
    e["lastReadBlock"] = REREAD_BLOCK
    e["lastReadWib"] = f"2026-11-07 run {RUN}"
    merged += 1
print("merged reread contracts:", merged, "| all-None:", none_only)

# 2. velocity merge
vmerged = 0
for row in vel.get("rows", []):
    name = row.get("name")
    if name not in contracts:
        continue
    e = contracts[name]
    for k in ("mintedInInterval", "intervalMinutes", "currentRatePerMin", "previousRatePerMin"):
        if row.get(k) is not None:
            e[k] = row[k]
    if row.get("velocityNote"):
        e["velocityNote"] = row["velocityNote"]
    if row.get("velocityPasses") is not None:
        e["velocityVerified"] = bool(row["velocityPasses"])
    vmerged += 1
print("velocity rows merged:", vmerged, "| passes:", len(vel.get("passes", [])),
      "| sellout:", len(vel.get("soldOut", [])), "| slotChanged:", vel.get("slotChanged"))

# WHALE-B: velocity-only pass, free% unverified -> NOT promotable; record plainly
wb = contracts.get("WHALE-B")
if wb:
    wb["runNote0401_whale_b"] = (
        "Run 0401: velocity LOLOS (+24 dalam 30,08 mnt, 0,7978/mnt, 2,47x vs prev 0,3228) "
        "TAPI TIDAK promosi: free% UNVERIFIED (tidak ada free counter/cap terbaca, Sourcify "
        "unverified, shape unknown); umur ~11,7 jam (first mint 2026-11-06 16:22 WIB), slot open "
        "(balance 0), 1594/5000. Velocity-only, bukan strong lead, bukan kandidat.")

# 3. track_c reread merge (non-None only)
tcmerged = 0; tc_none = 0
for name, rv in reread.get("track_c", {}).items():
    if name not in tc or not isinstance(rv, dict):
        continue
    e = tc[name]
    any_val = False
    for k, v in rv.items():
        if k in ("address", "_batch_error", "_batch_v2"):
            continue
        if v is not None:
            e[k] = v; any_val = True
    if not any_val:
        tc_none += 1
    e["lastReadBlock"] = REREAD_BLOCK
    e["lastReadWib"] = f"2026-11-07 run {RUN}"
    tcmerged += 1
print("track_c merged:", tcmerged, "| all-None:", tc_none)

# 4. 5c checked merge — run 0401 (7, verdict not_verified; 0 transport-failed)
chk = json.load(open(f"{HF}/track-c-scan-checked.json"))
lst = chk.setdefault("checked", [])
have = {a.lower() for a in lst if isinstance(a, str)}
added = 0; skipped_tf = 0
for res in fivec.get("results", []):
    a = res.get("address", "")
    if res.get("verdict") == "transport-failed":
        skipped_tf += 1
        continue
    if a and a.lower() not in have:
        lst.append(a); have.add(a.lower()); added += 1
json.dump(chk, open(f"{HF}/track-c-scan-checked.json", "w"), indent=1)
print("5c checked added:", added, "| transport-failed skipped:", skipped_tf,
      "| list total now:", len(lst))

# 5. special-item run notes from reread deltas
onlyai = contracts.get("ONLYAI-Crystals")
if onlyai:
    onlyai["runNote0401_onlyai"] = (
        f"Run 0401: totalSupply {onlyai_old[0]} -> 1279 @ blok {REREAD_BLOCK}; MAX_SUPPLY 5555. "
        "Semua free view TETAP revert, balanceOf(user) 0 — free% + slot user tetap UNVERIFIED. "
        "BUKAN strong lead, BUKAN kandidat. Tetap watchlist-launched.")
sage = contracts.get("Sage Trials")
if sage:
    sage["runNote0401_sage"] = (
        f"Run 0401: totalSupply {sage_old[0]} -> 33 @ blok {REREAD_BLOCK} (flat vs 0331); "
        "MAX_SUPPLY 5000. Free% unverified + tanpa website -> tetap early lead saja, "
        "BUKAN strong lead. Tidak ada promosi.")
for n in ("GiraffeValley", "HUNT PASS", "Jager Agent"):
    e = contracts.get(n)
    if e:
        e[f"runNote{RUN}_{n.lower().replace(' ', '_')}"] = (
            f"Run 0401: semua view gagal baca (None) - degradasi RPC, BUKAN nol; nilai lama "
            f"dipertahankan, velocity TIDAK dihitung; tetap early lead saja.")
hive = contracts.get("HIVE Agents")
if hive:
    hive["runNote0401"] = (
        f"Run 0401 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 0331 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")

# 6. scan watermark advance + seen-file update (scan leg did NOT do these)
state = json.load(open(f"{HF}/onchain-scan-state.json"))
prev_wm = state.get("last_scanned_block")
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = "2026-11-07 run 0401"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = scan.get("erc20_mint_contracts")
state["skipped_gap"] = ("132074798-132076511 (1714 blok; window dari watermark 132074797 ke head "
                        "132077511 = 2714 blok > cap 1000; main scan menutup 1000 blok terbaru "
                        "132076512-132077511; gap milik backfill)")
state["note_0401"] = ("Scan run 0401 SUKSES (preflight 7,9 dtk; 40 Ankr calls, 0 error, ~8,7 mnt). "
                      "0 first-seen sejati, 0 early lead. 5c: 7 baru dicek, 0 sale-shape.")
json.dump(state, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("watermark:", prev_wm, "->", scan["to_block"])

seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
seen_c = seen.setdefault("contracts", {})
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
added_seen = 0
for c in scan.get("contracts", []):
    a = c.get("address", "")
    if not a or a.lower() == REGISTRY.lower():
        continue
    if a not in seen_c and a.lower() not in {k.lower() for k in seen_c}:
        seen_c[a] = {"first_seen_block": c.get("first_block", scan["from_block"]),
                     "first_seen_run": f"2026-11-07-{RUN}"}
        added_seen += 1
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)
print("seen file: added", added_seen, "new contracts; total now:", len(seen_c))

# 7. AGE RULE — remove verified >48h live-status entries
sold_out_names = {r.get("name") for r in vel.get("soldOut", [])}

def min_first_seen(addr):
    vals = []
    for k, v in seen_c.items():
        if k.lower() == addr.lower():
            if isinstance(v, int):
                vals.append(v)
            elif isinstance(v, dict) and isinstance(v.get("first_seen_block"), int):
                vals.append(v["first_seen_block"])
    return min(vals) if vals else None

TH = age["threshold_block"]
removed = {}
skipped = []
for c in age["candidates"]:
    name, addr = c["name"], c["address"]
    if name not in contracts:
        skipped.append((name, "not-in-snapshot")); continue
    st = contracts[name].get("status", "")
    if "minted-by-user" in st:
        skipped.append((name, "minted-by-user")); continue
    if name in sold_out_names:
        skipped.append((name, "sold-out")); continue
    m = min_first_seen(addr)
    if m is None or m >= TH:
        skipped.append((name, f"first-seen {m} not < threshold {TH}")); continue
    removed[name] = contracts.pop(name)
print("age-rule removed:", len(removed), "| skipped:", skipped)
json.dump({"run": f"2026-11-07-{RUN}", "threshold_block": TH,
           "method": age["method"], "removed_count": len(removed),
           "removed": removed, "skipped": skipped},
          open(f"{HF}/run-2026-11-07-{RUN}-age-removed.json", "w"), indent=1)

# 8. snapshot run notes + save
snap["timestamp_wib"] = "2026-11-07T04:30:00+07:00"
snap["last_run_wib"] = "2026-11-07 04:01 WIB"
snap["runNote0401_1107"] = (
    "Run 0401 (jadwal 04:01 WIB 2026-11-07): 0 kandidat, 0 strong-lead baru, 0 early-lead baru, "
    "0 track-C lead/kandidat baru, 0 sellout baru, 0 slot berubah, 0 auto-mint/claim. Scan route 4: "
    "pre-flight LULUS 7,9 dtk (head 132077471, 344 log/50 blok); window 132076512-132077511 (1000 blok "
    "cap), 40 Ankr calls, 0 error (107 ERC721 + 220 ERC-20) — watermark -> 132077511; skipped gap "
    "132074798-132076511 (1714 blok) milik backfill. First-seen 0. Re-read 468 kontrak + 56 track_c @ "
    "blok 132077487 (91 + 32 all-None, RPC degradasi); velocity 1 lolos (WHALE-B, free% UNVERIFIED — "
    "tidak promosi). Age rule: 4 entri >48 jam DIHAPUS (Sly Hours-F19A, AgentLattice-5b9e, Lucky Charm "
    "Atlas II-5812, SoulAgent); Agentyyds + Glitchdroid dilewati (sold-out). 5c: 7 baru dicek "
    "(0 sale-shape). Web: Boltbook en+zh 0 baru; Sourcify 50 kontrak 0 S1/S2 (2 kontrak 0x33Ff…/"
    "0xbdB9… sudah triase hot leg sebagai checked-not-sale-shape, tidak dilaporkan ulang); sweep + "
    "Odaily/PANews nihil. Binanceai tetap refund/failed (launched 0, isRefundPhase 1); Grove freeOpen 0. "
    "Bridge tidak berubah, 0 temuan pelengkap baru.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved; contracts now:", len(snap["contracts"]), "| track_c:", len(tc),
      "| excluded:", len(snap.get("excluded", {})))
