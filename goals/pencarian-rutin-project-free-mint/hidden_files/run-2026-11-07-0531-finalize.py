#!/usr/bin/env python3
"""Finalize run 2026-11-07 05:31 WIB — parent merge (pattern run 0501, values run 0531).
Backs up snapshot + track-c-checked + scan-state + seen, merges reread
(non-None only) + velocity + track_c reread, merges 5c checked (10 completed:
9 not_verified + 1 not-sale-shape; 0 transport-failed), advances scan watermark
to the scan head 132089404 UNLESS backfill already advanced it further
(never regress), adds scan contracts absent from the seen file, applies the
48h age rule to the 2 candidates (both sold-out -> skipped, 0 removed),
adds V26 (watchlist-only, registry-bytes-only, NOT an early lead per the
V14/V20 precedents) to the snapshot. OneBit Membership Card is NOT added
(not agent-shaped at all: no registry hit, Sourcify not_verified, no free
evidence — log only).
NO preview/mint/claim/sign/transaction.
"""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0531"
for f in ("onchain-snapshot.json", "track-c-scan-checked.json",
          "onchain-scan-state.json", "onchain-scan-seen.json"):
    shutil.copy(f"{HF}/{f}", f"{HF}/{f}.bak-20261107-{RUN}")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-07-{RUN}-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-07-{RUN}-velocity.json"))
fivec = json.load(open(f"{HF}/run-2026-11-07-{RUN}-5c-newscan.json"))
age = json.load(open(f"{HF}/run-2026-11-07-{RUN}-age-candidates.json"))
scan = json.load(open(f"{HF}/onchain-scan-2026-11-07-{RUN}.json"))
REREAD_BLOCK = reread["block"]
contracts = snap["contracts"]
tc = snap.setdefault("track_c", {})

def old_total(name):
    e = contracts.get(name) or {}
    return e.get("totalSupply"), e.get("totalMinted")
onlyai_old = old_total("ONLYAI-Crystals")
ape_old = old_total("Ape Agent")
volt_old = old_total("AgentVOLT (round 1)")
whale_old = old_total("WHALE-B")

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

wb = contracts.get("WHALE-B")
if wb:
    wb["runNote0531_whale_b"] = (
        "Run 0531: velocity GAGAL (+9 dalam 27,27 mnt, 0,3299/mnt, ratio 1,02 vs prev 0,3228; "
        "1643->1652/5000) — tetap di bawah 1,5x DAN <20 token. free% TETAP UNVERIFIED (tidak ada "
        "free counter/cap terbaca, Sourcify unverified, shape unknown); umur ~12,5 jam, slot open "
        "(balance 0). Velocity-only, bukan strong lead, bukan kandidat.")

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

# 4. 5c checked merge — run 0531 (9 not_verified + 1 not-sale-shape; 0 transport-failed)
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
    onlyai["runNote0531_onlyai"] = (
        f"Run 0531: totalSupply {onlyai_old[0]} -> {onlyai.get('totalSupply')} @ blok {REREAD_BLOCK}; "
        "MAX_SUPPLY 5555. Semua free view TETAP revert, balanceOf(user) 0 — free% + slot user tetap "
        "UNVERIFIED. Velocity GAGAL (+14, ratio 0,03). BUKAN strong lead, BUKAN kandidat. Tetap watchlist-launched.")
ape = contracts.get("Ape Agent")
if ape:
    ape["runNote0531_ape"] = (
        f"Run 0531: totalSupply {ape_old[0]} -> {ape.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+9 interval); MAX_SUPPLY 4444. Free% UNVERIFIED (tidak ada free "
        "counter terbaca), website null (MINTS). "
        "BUKAN strong lead, BUKAN kandidat. Tetap watchlist-only.")
volt = contracts.get("AgentVOLT (round 1)")
if volt:
    volt["runNote0531_volt"] = (
        f"Run 0531: totalSupply {volt_old[0]} -> {volt.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+61 interval, rate 2,2357/mnt — rate PERTAMA, ratio None, velocity TIDAK lolos). Free% "
        "UNVERIFIED (semua free view revert), website null (MINTS). BUKAN lead/kandidat. Tetap watchlist-only.")
hive = contracts.get("HIVE Agents")
if hive:
    hive["runNote0531"] = (
        f"Run 0531 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 0501 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")

# 6. scan watermark advance + seen-file update (scan leg did NOT do these).
# NEVER regress: backfill may have advanced the watermark past the scan head.
state = json.load(open(f"{HF}/onchain-scan-state.json"))
prev_wm = state.get("last_scanned_block")
scan_head = scan["to_block"]
new_wm = max(prev_wm or 0, scan_head)
state["last_scanned_block"] = new_wm
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = "2026-11-07 run 0531"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = len(scan.get("erc20_mint_contracts_list", []))
state["skipped_gap"] = ("132085455-132088404 (2950 blok; window main scan 132088405-132089404 "
                        "dimulai dari head-999 karena gap 3907 blok > cap 1000; gap ini ditutup "
                        "bertahap oleh backfill, bukan dengan memperbesar window)")
state["note_0531"] = ("Scan run 0531 SUKSES (preflight 7,4 dtk; 40 Ankr calls, 0 error, partial false; "
                      "99 NFT (97 ERC-721 + 2 ERC-1155) + 218 ERC-20 mint). 2 first-seen "
                      "sejati; V26 registry-bytes-only BUKAN early lead (watchlist-only, log saja, "
                      "preseden V14/V20); OneBit Membership Card bukan agent-shaped (log saja). 5c: 10 "
                      "baru dicek (9 not_verified + 1 not-sale-shape 0x18c08D...000, attempt ke-3), "
                      "0 sale-shape, 0 transport-failed.")
json.dump(state, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("watermark:", prev_wm, "->", new_wm, "(scan head:", scan_head, ")")

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

# 7. AGE RULE — remove verified >48h live-status entries.
sold_out_names = {r.get("name") for r in vel.get("soldOut", [])}

def earliest_first_seen(addr, entry):
    vals = []
    for k in ("firstSeenBlock", "firstMintBlock"):
        v = entry.get(k)
        if isinstance(v, int):
            vals.append(v)
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
    m = earliest_first_seen(addr, contracts[name])
    if m is None or m >= TH:
        skipped.append((name, f"earliest first-seen {m} not < threshold {TH}")); continue
    removed[name] = contracts.pop(name)
print("age-rule removed:", len(removed), "| skipped:", skipped)
json.dump({"run": f"2026-11-07-{RUN}", "threshold_block": TH,
           "method": age.get("method"), "removed_count": len(removed),
           "removed": removed, "skipped": skipped},
          open(f"{HF}/run-2026-11-07-{RUN}-age-removed.json", "w"), indent=1)

# 8. Watchlist-only addition (NOT a lead, NOT reported as a lead, never previewed/minted)
# V26 — first-seen in scan window; registry-bytes hit ONLY, Sourcify deep verify
# definitively not_verified (bukan transport-failed), no free-mint/free-supply
# evidence, 1 mint/1 minter. Per the firstseen method string + V14 (run 0431)
# and V20 (run 0501) precedents, registry-bytes-only is NOT an early lead.
contracts["V26"] = {
    "address": "0xdF738E84982d6Ac0d10491363C99A04E2391a77c",
    "status": "watchlist-only-registry-bytes-only-2026-11-07",
    "name": "V26", "symbol": "V96", "kind": "ERC721",
    "totalSupply": None, "freeClaimed": None, "FREE_SUPPLY": None, "MAX_SUPPLY": None,
    "freePctVerified": None, "mintOpen": None, "userBalance": None,
    "firstSeenBlock": 132089090, "scanMints": 1, "scanMinters": 1,
    "scanWindow": "132088405-132089404",
    "lastReadBlock": REREAD_BLOCK, "lastReadWib": f"2026-11-07 run {RUN}",
    "xVerified": False, "velocityVerified": False,
    "baselineNote": ("First-seen run 0531 (1 mint, 1 minter, blok 132089090). BUKAN early lead: "
                     "hanya registry-bytes hit (diketahui lemah diskriminasinya, 81% kontrak template); "
                     "Sourcify deep verify definitively not_verified (bukan transport-failed), tidak ada free-mint "
                     "function/free-supply evidence. Nama/simbol V26/V96 tanpa narasi Agent ID. "
                     "Watchlist-only; promosi hanya bila nanti memenuhi kaki strong lead. "
                     "Tidak pernah di-preview/mint."),
}
print("watchlist additions: V26")

# 9. snapshot run notes + save
snap["timestamp_wib"] = "2026-11-07T05:31:00+07:00"
snap["last_run_wib"] = "2026-11-07 05:31 WIB"
snap["runNote0531_1107"] = (
    "Run 0531 (jadwal 05:31 WIB 2026-11-07): 0 kandidat, 0 strong-lead baru, 0 early-lead baru, "
    "0 track-C lead/kandidat baru, 0 sellout baru, 0 slot berubah, 0 auto-mint/claim. Scan route 4: "
    "pre-flight LULUS 7,4 dtk (head 132089361, 157 log/50 blok); window 132088405-132089404 (1000 blok "
    "cap), 40 Ankr calls, 0 error, partial false (99 NFT: 97 ERC-721 + 2 ERC-1155; 218 "
    "ERC-20 mint) — watermark 132085454 -> 132089404; gap 132085455-132088404 (2950 blok) dicakup "
    "bertahap oleh backfill. First-seen 2: V26 registry-bytes-only BUKAN early lead (watchlist-only, log saja, "
    "preseden V14/V20); OneBit Membership Card bukan agent-shaped (log saja). 5c: 10 "
    "baru dicek (9 not_verified + 1 not-sale-shape 0x18c08D...000 attempt ke-3), 0 sale-shape, "
    "0 transport-failed. Re-read 457 kontrak + 56 track_c @ blok 132089487 (93 + 32 all-None, RPC degradasi); velocity 0 "
    "lolos (WHALE-B +9, ratio 1,02; ONLYAI +14 ratio 0,03; Ape Agent +9; "
    "AgentVOLT round 1 +61, rate pertama 2,24/mnt). Age rule: 2 kandidat (Agentyyds, Glitchdroid) "
    "keduanya sold-out 600/600 -> dilewati, 0 dihapus. Watchlist baru: V26 0xdF738E8... (registry-bytes-only, "
    "Sourcify not_verified, bukan lead). Web: Boltbook en+zh 0 baru; Sourcify 50 kontrak 0 S1/S2 (semua hot-leg-seen); MINTS index "
    "tidak refresh (22:04:17Z), 142 proyek/39 free_live, 0 delta; sweep + Odaily/PANews nihil. Binanceai tetap "
    "refund/failed (failed 1, isRefundPhase 1, launched 0; totalShares 3110); Grove freeOpen 0. "
    "Bridge tidak berubah (115 kontrak, 7 same_owner_discarded, 33 belum di snapshot), 0 temuan "
    "pelengkap baru.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved; contracts now:", len(snap["contracts"]), "| track_c:", len(tc),
      "| excluded:", len(snap.get("excluded", {})))
