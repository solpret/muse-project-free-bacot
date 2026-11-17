#!/usr/bin/env python3
"""Finalize run 2026-11-07 05:01 WIB — parent merge (pattern run 0431, values run 0501).
Backs up snapshot + track-c-checked + scan-state + seen, merges reread
(non-None only) + velocity + track_c reread, merges 5c checked (3 completed
not_verified; 1 transport-failed skipped for retry), advances scan watermark
to the scan head 132085454 UNLESS backfill already advanced it further
(never regress), adds scan contracts absent from the seen file, applies the
48h age rule to the 3 candidates (2 sold-out skipped, 1 removed: RigOrb-539e),
adds V20 (watchlist-only, registry-bytes-only, NOT an early lead) to the
snapshot. Agent Test NFT is NOT added (not agent-shaped at all: no registry
hit, Sourcify not_verified, no free evidence — log only).
NO preview/mint/claim/sign/transaction.
"""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0501"
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

# WHALE-B: streak of 2 velocity passes BROKEN this run (+7 in 32.16 min, 0.2177/min,
# ratio 0.67 vs prev 0.3228) -> velocity GAGAL; free% still UNVERIFIED, NOT promotable.
wb = contracts.get("WHALE-B")
if wb:
    wb["runNote0501_whale_b"] = (
        "Run 0501: velocity GAGAL (+7 dalam 32,16 mnt, 0,2177/mnt, ratio 0,67 vs prev 0,3228; "
        "1636->1643/5000) — rentetan 2 lolos (0401, 0431) PUTUS. free% TETAP UNVERIFIED (tidak ada "
        "free counter/cap terbaca, Sourcify unverified, shape unknown); umur ~12 jam, slot open "
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

# 4. 5c checked merge — run 0501 (3 completed not_verified; 1 transport-failed skipped)
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
    onlyai["runNote0501_onlyai"] = (
        f"Run 0501: totalSupply {onlyai_old[0]} -> {onlyai.get('totalSupply')} @ blok {REREAD_BLOCK}; "
        "MAX_SUPPLY 5555. Semua free view TETAP revert, balanceOf(user) 0 — free% + slot user tetap "
        "UNVERIFIED. Velocity GAGAL (+24, ratio 0,04). BUKAN strong lead, BUKAN kandidat. Tetap watchlist-launched.")
ape = contracts.get("Ape Agent")
if ape:
    ape["runNote0501_ape"] = (
        f"Run 0501: totalSupply {ape_old[0]} -> {ape.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+17 interval, MINTS 482/4444 di index 0431); MAX_SUPPLY 4444. Free% UNVERIFIED (tidak ada free "
        "counter terbaca), umur ~11 jam (first mint 2026-11-06 18:34 WIB), website null (MINTS). "
        "BUKAN strong lead, BUKAN kandidat. Tetap watchlist-only.")
volt = contracts.get("AgentVOLT (round 1)")
if volt:
    volt["runNote0501_volt"] = (
        f"Run 0501: totalSupply {volt_old[0]} -> {volt.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+114 interval, rate 6,31/mnt — rate PERTAMA, ratio None, velocity TIDAK lolos). Free% "
        "UNVERIFIED (semua free view revert), website null (MINTS). BUKAN lead/kandidat. Tetap watchlist-only.")
hive = contracts.get("HIVE Agents")
if hive:
    hive["runNote0501"] = (
        f"Run 0501 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 0431 (1255) -> velocity "
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
state["last_scan_wib"] = "2026-11-07 run 0501"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = len(scan.get("erc20_mint_contracts_list", []))
state["skipped_gap"] = ("132084332-132084454 (123 blok; window main scan 132084455-132085454 "
                        "dimulai dari head-999 sementara backfill baru sampai 132084331; gap ini "
                        "dicakup backfill-paralel 132084332-132087124 yang masih berjalan saat finalisasi)")
state["note_0501"] = ("Scan run 0501 SUKSES (preflight 8,9 dtk; 40 Ankr calls, 0 error, partial false; "
                      "97 NFT (91 ERC-721 + 6 ERC-1155, 543 mint) + 278 ERC-20 mint). 2 first-seen "
                      "sejati; V20 registry-bytes-only BUKAN early lead (watchlist-only, log saja); "
                      "Agent Test NFT bukan agent-shaped (log saja). 5c: 3 baru dicek (0 sale-shape), "
                      "1 transport-failed (0x18c08D...000, attempt ke-2, retry run berikut).")
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
# V20 — first-seen in scan window; registry-bytes hit ONLY, Sourcify deep verify
# transport-failed (RemoteDisconnected), no free-mint/free-supply evidence, 1 mint/1 minter.
# Per the firstseen method string ("Sourcify-unverified with no free-mint/AgentGate evidence
# = NOT an early lead (log only)") and the V14 precedent (run 0431), this is NOT an early lead.
contracts["V20"] = {
    "address": "0x5f0CC98E2c9dcB3e9Fb646dA86D65bC5072e9Bc2",
    "status": "watchlist-only-registry-bytes-only-2026-11-07",
    "name": "V20", "symbol": "V90", "kind": "ERC721",
    "totalSupply": None, "freeClaimed": None, "FREE_SUPPLY": None, "MAX_SUPPLY": None,
    "freePctVerified": None, "mintOpen": None, "userBalance": None,
    "firstSeenBlock": 132085064, "scanMints": 1, "scanMinters": 1,
    "scanWindow": "132084455-132085454",
    "lastReadBlock": REREAD_BLOCK, "lastReadWib": f"2026-11-07 run {RUN}",
    "xVerified": False, "velocityVerified": False,
    "baselineNote": ("First-seen run 0501 (1 mint, 1 minter, blok 132085064). BUKAN early lead: "
                     "hanya registry-bytes hit (diketahui lemah diskriminasinya, 81% kontrak template); "
                     "Sourcify deep verify transport-failed (RemoteDisconnected), tidak ada free-mint "
                     "function/free-supply evidence. Nama/simbol V20/V90 tanpa narasi Agent ID. "
                     "Watchlist-only; promosi hanya bila nanti memenuhi kaki strong lead. "
                     "Tidak pernah di-preview/mint."),
}
print("watchlist additions: V20")

# 9. snapshot run notes + save
snap["timestamp_wib"] = "2026-11-07T05:01:00+07:00"
snap["last_run_wib"] = "2026-11-07 05:01 WIB"
snap["runNote0501_1107"] = (
    "Run 0501 (jadwal 05:01 WIB 2026-11-07): 0 kandidat, 0 strong-lead baru, 0 early-lead baru, "
    "0 track-C lead/kandidat baru, 0 sellout baru, 0 slot berubah, 0 auto-mint/claim. Scan route 4: "
    "pre-flight LULUS 8,9 dtk (head 132085418, 159 log/50 blok); window 132084455-132085454 (1000 blok "
    "cap), 40 Ankr calls, 0 error, partial false (97 NFT: 91 ERC-721 + 6 ERC-1155, 543 mint; 278 "
    "ERC-20 mint) — watermark 132084331 -> 132085454; gap 132084332-132084454 (123 blok) dicakup "
    "backfill-paralel 132084332-132087124 yang masih berjalan saat finalisasi. First-seen 2: V20 registry-bytes-only "
    "BUKAN early lead (watchlist-only, log saja); Agent Test NFT bukan agent-shaped (log saja). 5c: 3 "
    "baru dicek (0 sale-shape), 1 transport-failed (0x18c08D...000, attempt ke-2, retry run berikut). "
    "Re-read 457 kontrak + 56 track_c @ blok 132085849 (91 + 32 all-None, RPC degradasi); velocity 0 "
    "lolos (WHALE-B +7, ratio 0,67 — rentetan 2 lolos putus; ONLYAI +24 ratio 0,04; Ape Agent +17; "
    "AgentVOLT round 1 +114, rate pertama 6,31/mnt). Age rule: 1 entri >48 jam DIHAPUS (RigOrb-539e, "
    "first mint 2026-11-05 04:43 WIB, 1430/10000, belum sold out); Agentyyds + Glitchdroid dilewati "
    "(sold-out 600/600). Watchlist baru: V20 0x5f0CC98E... (registry-bytes-only, unverified, bukan lead). "
    "Web: Boltbook en+zh 0 baru; Sourcify 50 kontrak 0 S1/S2 (semua hot-leg-seen); MINTS index refresh "
    "22:04:17Z, 142 proyek/39 free_live, 0 delta; sweep + Odaily/PANews nihil. Binanceai tetap "
    "refund/failed (failed 1, isRefundPhase 1; launched() baca gagal transport); Grove freeOpen 0. "
    "Bridge tidak berubah (115 kontrak, 7 same_owner_discarded, 33 belum di snapshot), 0 temuan "
    "pelengkap baru.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved; contracts now:", len(snap["contracts"]), "| track_c:", len(tc),
      "| excluded:", len(snap.get("excluded", {})))
