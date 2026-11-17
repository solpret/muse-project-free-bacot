#!/usr/bin/env python3
"""Finalize run 2026-11-07 04:31 WIB — parent merge (pattern run 0401).
Backs up snapshot + track-c-checked + scan-state + seen, merges reread
(non-None only) + velocity + track_c reread, merges 5c checked (4 completed,
1 transport-failed skipped for retry), advances scan watermark to 132081494
(scan leg; backfill had already advanced state to 132080449), records the
45-block gap 132080450-132080494, adds scan contracts absent from the seen
file, applies the 48h age rule to the 11 candidates (2 sold-out skipped, 9
removed; full entries preserved in run-2026-11-07-0431-age-removed.json),
adds V14 (watchlist-only, NOT an early lead: registry-bytes-only) and
AgentVOLT (round 1) (watchlist-only, MINTS-index triage) to the snapshot.
NO preview/mint/claim/sign/transaction."""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0431"
for f in ("onchain-snapshot.json", "track-c-scan-checked.json",
          "onchain-scan-state.json", "onchain-scan-seen.json"):
    shutil.copy(f"{HF}/{f}", f"{HF}/{f}.bak-20261107-{RUN}")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-07-{RUN}-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-07-{RUN}-velocity.json"))
fivec = json.load(open(f"{HF}/run-2026-11-07-{RUN}-5c-newscan.json"))
age = json.load(open(f"{HF}/run-2026-11-07-{RUN}-age-candidates.json"))
scan = json.load(open(f"{HF}/onchain-scan-2026-11-07-{RUN}.json"))
REREAD_BLOCK = reread["block"]  # 132081561
contracts = snap["contracts"]
tc = snap.setdefault("track_c", {})

def old_total(name):
    e = contracts.get(name) or {}
    return e.get("totalSupply"), e.get("totalMinted")
onlyai_old = old_total("ONLYAI-Crystals")
ape_old = old_total("Ape Agent")

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

# WHALE-B: velocity-only pass #2 in a row, free% unverified -> NOT promotable
wb = contracts.get("WHALE-B")
if wb:
    wb["runNote0431_whale_b"] = (
        "Run 0431: velocity LOLOS ke-2 berturut-turut (+42 dalam 30,55 mnt, 1,3746/mnt, 4,26x "
        "vs prev 0,3228; 1594->1636/5000) TAPI TIDAK promosi: free% UNVERIFIED (tidak ada free "
        "counter/cap terbaca, Sourcify unverified, shape unknown); umur ~12 jam (first mint "
        "2026-11-06 16:22 WIB), slot open (balance 0). Velocity-only, bukan strong lead, bukan "
        "kandidat.")

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

# 4. 5c checked merge — run 0431 (4 completed not_verified; 1 transport-failed skipped for retry)
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
    onlyai["runNote0431_onlyai"] = (
        f"Run 0431: totalSupply {onlyai_old[0]} -> {onlyai.get('totalSupply')} @ blok {REREAD_BLOCK}; "
        "MAX_SUPPLY 5555. Semua free view TETAP revert, balanceOf(user) 0 — free% + slot user tetap "
        "UNVERIFIED. BUKAN strong lead, BUKAN kandidat. Tetap watchlist-launched.")
ape = contracts.get("Ape Agent")
if ape:
    ape["runNote0431_ape"] = (
        f"Run 0431: totalSupply {ape_old[0]} -> {ape.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+28 interval, MINTS 482/4444 cocok); MAX_SUPPLY 4444. Free% UNVERIFIED (tidak ada free "
        "counter terbaca), umur ~10 jam (first mint 2026-11-06 18:34 WIB), website null (MINTS). "
        "BUKAN strong lead, BUKAN kandidat. Tetap watchlist-only.")
hive = contracts.get("HIVE Agents")
if hive:
    hive["runNote0431"] = (
        f"Run 0431 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 0401 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")

# 6. scan watermark advance + seen-file update (scan leg did NOT do these)
state = json.load(open(f"{HF}/onchain-scan-state.json"))
prev_wm = state.get("last_scanned_block")
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = "2026-11-07 run 0431"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = scan.get("erc20_mint_contracts")
state["skipped_gap"] = ("132080450-132080494 (45 blok; window dari watermark 132080449 ke head "
                        "132081494 = 1045 blok > cap 1000; main scan menutup 1000 blok terbaru "
                        "132080495-132081494; backfill sudah menutup 132078836-132080449)")
state["note_0431"] = ("Scan run 0431 SUKSES (preflight 5,0 dtk; 40 Ankr calls, 0 error, ~8,2 mnt). "
                      "2 first-seen sejati; V14 registry-bytes-only BUKAN early lead (log + watchlist "
                      "saja); Bot Unit bukan agent-shaped. 5c: 4 baru dicek (0 sale-shape), 1 "
                      "transport-failed (0x18c08D...000, retry run berikut).")
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

# 7. AGE RULE — remove verified >48h live-status entries.
# Earliest launch evidence = min(snapshot firstSeenBlock/firstMintBlock, seen-file first_seen_block).
# (Seen file alone is unreliable: Bamboo Mafia-fc4E + Desert Drip-Bf59 carry later seen-file
# blocks 131937578/131933559, but their snapshot firstSeenBlock 131696472/131696508 + baselineNote
# "first mints verified on-chain in scan window 131696145-131698144" prove first mint >48h ago.)
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
           "method": age["method"], "removed_count": len(removed),
           "removed": removed, "skipped": skipped},
          open(f"{HF}/run-2026-11-07-{RUN}-age-removed.json", "w"), indent=1)

# 8. Watchlist-only additions (NOT leads, NOT reported as leads, never previewed/minted)
# 8a. V14 — first-seen in scan window; registry-bytes hit ONLY. Per the firstseen method string
# ("Sourcify-unverified with no free-mint/AgentGate evidence = NOT an early lead (log only)")
# and the body's known-limits clause, this is NOT an early lead. Tracked watchlist-only so it
# is never dropped silently; promotes only if it later meets strong-lead legs.
contracts["V14"] = {
    "address": "0x504D108ad2A2f55248882Ba0A93329455516CC10",
    "status": "watchlist-only-registry-bytes-only-2026-11-07",
    "name": "V14", "symbol": "V94", "kind": "ERC721",
    "totalSupply": None, "freeClaimed": None, "FREE_SUPPLY": None, "MAX_SUPPLY": None,
    "freePctVerified": None, "mintOpen": None, "userBalance": None,
    "firstSeenBlock": 132080924, "scanMints": 1, "scanMinters": 1,
    "scanWindow": "132080495-132081494",
    "lastReadBlock": REREAD_BLOCK, "lastReadWib": f"2026-11-07 run {RUN}",
    "xVerified": False, "velocityVerified": False,
    "baselineNote": ("First-seen run 0431 (1 mint, 1 minter, blok 132080924). BUKAN early lead: "
                     "Sourcify NOT verified, tidak ada free-mint function/free-supply evidence, "
                     "hanya registry-bytes hit (diketahui lemah diskriminasinya, 81% kontrak template). "
                     "Nama/simbol V14/V94 tanpa narasi Agent ID. Watchlist-only; promosi hanya bila "
                     "nanti memenuhi kaki strong lead. Tidak pernah di-preview/mint."),
}
# 8b. AgentVOLT (round 1) — MINTS-index new entry, triaged on-chain this run (blok 132083441):
# name AgentVOLT, symbol AVOLT, totalSupply 1922, MAX_SUPPLY 10000, balanceOf(user) 0;
# FREE_SUPPLY/freeClaimed/freeMinted/totalMinted/mintOpen all revert (view tidak ada di kontrak).
# MINTS: free_live, freeMint(), "1 free per Agent ID (NFT + 5,000 VOLT), paid mint exists",
# website null, added to index 2026-11-06 21:04 UTC. Age/free%/X/velocity UNVERIFIED.
contracts["AgentVOLT (round 1)"] = {
    "address": "0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771",
    "status": "watchlist-only-unverified-2026-11-07",
    "name": "AgentVOLT (round 1)", "symbol": "AVOLT", "kind": "ERC721",
    "totalSupply": 1922, "freeClaimed": None, "FREE_SUPPLY": None, "MAX_SUPPLY": 10000,
    "freePctVerified": None, "mintOpen": None, "userBalance": 0,
    "firstSeenBlock": None, "firstMintWib": None,
    "lastReadBlock": 132083441, "lastReadWib": f"2026-11-07 run {RUN}",
    "xVerified": False, "velocityVerified": False,
    "baselineNote": ("MINTS-index new entry run 0431 (thecolony.ai, added 2026-11-06 21:04 UTC), "
                     "triase on-chain blok 132083441: totalSupply 1922/10000, balanceOf(user) 0; "
                     "semua free view revert (kontrak tanpa FREE_SUPPLY/freeClaimed). MINTS klaim "
                     "free_live + freeMint() '1 free per Agent ID (NFT + 5,000 VOLT)', website null. "
                     "Umur peluncuran UNVERIFIED, free% UNVERIFIED, X UNVERIFIED, velocity belum "
                     "terhitung. BUKAN lead/kandidat; butuh verifikasi first-mint + free-shape + "
                     "gate website (metode A-N) sebelum promosi apa pun. Tidak pernah di-preview/mint."),
}
print("watchlist additions: V14, AgentVOLT (round 1)")

# 9. snapshot run notes + save
snap["timestamp_wib"] = "2026-11-07T04:30:00+07:00"
snap["last_run_wib"] = "2026-11-07 04:31 WIB"
snap["runNote0431_1107"] = (
    "Run 0431 (jadwal 04:31 WIB 2026-11-07): 0 kandidat, 0 strong-lead baru, 0 early-lead baru, "
    "0 track-C lead/kandidat baru, 0 sellout baru, 0 slot berubah, 0 auto-mint/claim. Scan route 4: "
    "pre-flight LULUS 5,0 dtk (head 132081439, 125 log/50 blok); window 132080495-132081494 (1000 blok "
    "cap), 40 Ankr calls, 0 error (87 NFT + 195 ERC-20) — watermark 132080449 -> 132081494; gap "
    "132080450-132080494 (45 blok) belum ter-scan. First-seen 2: V14 registry-bytes-only BUKAN early "
    "lead (watchlist-only, log saja); Bot Unit bukan agent-shaped. 5c: 4 baru dicek (0 sale-shape), 1 "
    "transport-failed (0x18c08D...000, retry run berikut). Re-read 464 kontrak + 56 track_c @ blok "
    "132081561 (91 + 32 all-None, RPC degradasi); velocity 1 lolos (WHALE-B +42, 4,26x, ke-2 "
    "berturut-turut — free% UNVERIFIED, tidak promosi). Age rule: 9 entri >48 jam DIHAPUS (Bamboo "
    "Mafia-fc4E, Lotl Lagoon-57Dc, Desert Drip-Bf59, Upside Down-BE59, FIN-TECH-4DeD, Mud Money-7C89, "
    "Night Shift-3034, Eight Arms Deep-644a, Honeycomb Bureau-4c80); Agentyyds + Glitchdroid dilewati "
    "(sold-out). Watchlist baru: AgentVOLT (round 1) 0xe0DEB1A7... (MINTS free_live, totalSupply 1922/"
    "10000, free view revert, website null — unverified, bukan lead) dan V14. Ape Agent sudah di "
    "snapshot (watchlist-only, +28 interval). Web: Boltbook en+zh 0 baru; Sourcify 50 kontrak 0 S1/S2 "
    "(koreksi: endpoint list menolak ?fields=abi, HTTP 400 — fields=abi hanya per-kontrak); sweep + "
    "Odaily/PANews/Square nihil. Binanceai tetap refund/failed (launched 0, isRefundPhase 1); Grove "
    "freeOpen 0. Bridge tidak berubah (115 kontrak, 7 same_owner_discarded, 33 belum di snapshot), 0 "
    "temuan pelengkap baru.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved; contracts now:", len(snap["contracts"]), "| track_c:", len(tc),
      "| excluded:", len(snap.get("excluded", {})))
