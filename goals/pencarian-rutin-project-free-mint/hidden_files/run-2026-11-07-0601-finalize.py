#!/usr/bin/env python3
"""Finalize run 2026-11-07 06:01 WIB — parent merge, written fresh for THIS run's data.
Merges reread (non-None only) + velocity + track_c reread, merges 5c checked
(2 new: both not_verified, 0 transport-failed), advances scan watermark to the
scan head UNLESS backfill already advanced it further (never regress; backfill
was concurrently at 132094117 when this script was written), applies the 48h
age rule (Agent Frogs removed: first_seen 131711844 < threshold 131712288,
NOT sold out 533/2222; Agentyyds + Glitchdroid skipped as sold-out),
records BLOCK777 (B777) in track_c as gate-blocked — found + reported ONCE by
the hot leg 06:04 WIB (gate website FAILED methods A-N, no preview/mint);
this run does NOT re-report it. Adds per-item run notes with THIS run's numbers.
NO preview/mint/claim/sign/transaction.
"""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0601"
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
tamp_old = old_total("Tampesta-6aA5")

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

# 2. velocity merge (velocity.json keys: intervalMin/ratePerMin/ratioVsPrev/mintedInInterval)
vmerged = 0
vel_by_name = {r.get("name"): r for r in vel.get("rows", [])}
for name, row in vel_by_name.items():
    if name not in contracts:
        continue
    e = contracts[name]
    if row.get("mintedInInterval") is not None:
        e["mintedInInterval"] = row["mintedInInterval"]
    if row.get("intervalMin") is not None:
        e["intervalMinutes"] = row["intervalMin"]
    if row.get("ratePerMin") is not None:
        e["previousRatePerMin"] = e.get("currentRatePerMin")
        e["currentRatePerMin"] = row["ratePerMin"]
    if row.get("ratioVsPrev") is not None:
        e["velocityRatio"] = row["ratioVsPrev"]
    if row.get("velocityPasses") is not None:
        e["velocityVerified"] = bool(row["velocityPasses"])
    vmerged += 1
print("velocity rows merged:", vmerged, "| passes:", len(vel.get("passes", [])),
      "| sellout:", len(vel.get("soldOut", [])), "| slotChanged:", vel.get("slotChanged"))

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

# 4. 5c checked merge
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

# 5. special-item run notes from reread deltas (THIS run's numbers)
onlyai = contracts.get("ONLYAI-Crystals")
if onlyai:
    onlyai["runNote0601_onlyai"] = (
        f"Run 0601: totalSupply {onlyai_old[0]} -> {onlyai.get('totalSupply')} @ blok {REREAD_BLOCK}; "
        "MAX_SUPPLY 5555. Semua free view TETAP revert, balanceOf(user) 0 — free% + slot user tetap "
        "UNVERIFIED. Velocity GAGAL (+40, rate 0,8136/mnt, ratio 0,04). BUKAN strong lead, BUKAN kandidat. Tetap watchlist-launched.")
ape = contracts.get("Ape Agent")
if ape:
    ape["runNote0601_ape"] = (
        f"Run 0601: totalSupply {ape_old[0]} -> {ape.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+8 interval, rate 0,1627/mnt — rate PERTAMA, ratio None, velocity TIDAK lolos). Free% "
        "UNVERIFIED (tidak ada free counter terbaca), website null (MINTS). "
        "BUKAN strong lead, BUKAN kandidat. Tetap watchlist-only.")
volt = contracts.get("AgentVOLT (round 1)")
if volt:
    volt["runNote0601_volt"] = (
        f"Run 0601: totalSupply {volt_old[0]} -> {volt.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+66 interval, rate 1,3425/mnt — rate PERTAMA, ratio None, velocity TIDAK lolos). Free% "
        "UNVERIFIED (semua free view revert), website null (MINTS). BUKAN lead/kandidat. Tetap watchlist-only.")
wb = contracts.get("WHALE-B")
if wb:
    wb["runNote0601_whale_b"] = (
        f"Run 0601: totalSupply {whale_old[0]} -> {wb.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+4 dalam 49,16 mnt, 0,0814/mnt, ratio 0,25 — velocity GAGAL, di bawah 1,5x DAN <20 token). "
        "free% TETAP UNVERIFIED (tidak ada free counter/cap terbaca, Sourcify unverified, shape unknown); "
        "slot open (balance 0). Velocity-only, bukan strong lead, bukan kandidat.")
tamp = contracts.get("Tampesta-6aA5")
if tamp:
    tamp["runNote0601_tampesta"] = (
        f"Run 0601: totalSupply {tamp_old[0]} -> {tamp.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+67 interval, rate 1,3628/mnt — rate PERTAMA, ratio None, velocity TIDAK lolos). Free% "
        "UNVERIFIED. BUKAN strong lead, BUKAN kandidat. Tetap watchlist-only.")
hive = contracts.get("HIVE Agents")
if hive:
    hive["runNote0601"] = (
        f"Run 0601 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 0531 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")

# 6. AGE RULE — remove Agent Frogs (verified >48h, NOT sold out).
# Agentyyds + Glitchdroid are sold out -> skipped per the sold-out exception.
removed = []
for cand in age.get("candidates", []):
    name = cand.get("name")
    addr = (cand.get("address") or "").lower()
    sold = any(r.get("name") == name for r in vel.get("soldOut", []))
    if sold:
        print(f"age: {name} skipped (sold out)")
        continue
    if name in contracts:
        ev = contracts.pop(name)
        removed.append(name)
        print(f"age: REMOVED {name} ({addr}) first_seen={cand.get('first_seen_block')} "
              f"threshold={age.get('threshold_block')} soldOut=False "
              f"totalSupply={ev.get('totalSupply')} freeClaimed={ev.get('freeClaimed')}/FREE_SUPPLY {ev.get('FREE_SUPPLY')}")
snap["runNote0601_age_removed"] = {
    "removed": removed,
    "evidence": ("Agent Frogs 0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31: first_seen block 131711844 "
                 "(scan window 131711709-131713708, run 0631 2026-11-05) < threshold 131712288 "
                 "(head 132096288 - 384000); launch >48h terjamin via lower bound. NOT sold out: "
                 "totalSupply 533/2222, freeClaimed 512/FREE_SUPPLY 1111 = 46,08%, 0 mint interval run 0601 "
                 f"(read blok {REREAD_BLOCK}). Status sebelumnya strong-lead-gate-blocked-2026-11-05; "
                 "dihapus dari watchlist aktif run 0601."),
    "skipped_sold_out": ["Agentyyds", "Glitchdroid"],
}
print("age removed:", removed)

# 7. BLOCK777 (B777) — track-C lead found + reported ONCE by hot leg 06:04 WIB.
# Record in track_c as gate-blocked so later runs never re-report or re-try it.
# Facts from the hot-leg record (MEMORY.md): sale 0x47529CF66091BeB0E8e0F78D5635e367473D52d5,
# S1 passed, totalMints 24/777, user slot open (freeLeft=1, quote=0), first mint 06:01:39 WIB,
# website gate FAILED methods A-N incl. (L) BscScan via live browser 06:21-06:22 WIB
# (Info tab empty, no website/social; source verified Exact Match, 63 holders, 64 transfers,
# Reputation UNKNOWN). NOT previewed/minted; reported once by hot leg.
B777 = "0x47529CF66091BeB0E8e0F78D5635e367473D52d5"
if B777 not in tc:
    tc[B777] = {
        "name": "BLOCK777 (B777)",
        "address": B777,
        "shape": "S1",
        "status": "gate-blocked-website-2026-11-07",
        "sale_shape": "S1 passed (mint + quote + free-share view + registry/AgentGate)",
        "free_pool": "totalMints 24/777 at hot-leg check 06:04 WIB; freeLeft=1",
        "user_quote": 0,
        "user_slot_open": True,
        "first_mint_wib": "2026-11-07 06:01:39 WIB",
        "first_mint_block_in_main_scan": 132093129,
        "gate": "website FAILED, methods A-N complete incl. (L) BscScan via live browser 06:21-06:22 WIB (Info tab empty, no website/social; source verified Exact Match, 63 holders, 64 transfers, Reputation UNKNOWN)",
        "reported_by": "hot-leg 06:04 WIB (reported once; this run does NOT re-report)",
        "executed": False,
        "note": "Main run 0601: B777 appeared in this run's Sourcify feed (skipped as hot-leg-seen) and in this run's scan ERC-20 list (mint_count=1 in window 132092512-132093511, below the 5c >=10 threshold, not shape-checked by this leg). Gate-blocked => NEVER preview/mint unless the user gives an explicit informed override for this specific case.",
    }
    print("track_c: BLOCK777 added as gate-blocked (hot-leg reported, no re-report)")
else:
    print("track_c: BLOCK777 already present, left as-is")

# 8. scan watermark advance + seen-file update (scan leg did NOT do these).
# NEVER regress: backfill may have advanced the watermark past the scan head.
state = json.load(open(f"{HF}/onchain-scan-state.json"))
prev_wm = state.get("last_scanned_block")
scan_head = scan["to_block"]
new_wm = max(prev_wm or 0, scan_head)
state["last_scanned_block"] = new_wm
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = "2026-11-07 run 0601"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = len(scan.get("erc20_mint_contracts_list", []))
state["skipped_gap"] = ("132090150-132092511 (2362 blok; window main scan 132092512-132093511 "
                        "dimulai dari head-999 karena gap 3328 blok > cap 1000; gap ini ditutup "
                        "bertahap oleh backfill — backfill paralel sudah berjalan 132092418-132094324 "
                        "saat finalisasi, menutup sebagian gap; bukan dengan memperbesar window)")
state["note_0601"] = ("Scan run 0601 SUKSES (preflight 10,8 dtk, head 132093477, 181 logs/50 blok; "
                      "ankr eth_blockNumber gagal parse seperti biasa, fallback fast_rpc race; "
                      "40 Ankr calls, 0 error, partial false; 111 NFT (109 ERC-721 + 2 ERC-1155) + "
                      "215 ERC-20 mint). 0 first-seen sejati (74 known-seen + 36 known-snapshot + "
                      "1 registry). 5c: 2 baru dicek (keduanya not_verified), 0 sale-shape, "
                      "0 transport-failed. BLOCK777 (B777) gate-blocked via hot leg, dicatat di track_c, "
                      "tidak dilaporkan ulang run ini.")
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

# 9. run note + last-run pointers
snap["runNote0601_1107"] = (
    "Scan run 0601 SUKSES (preflight 10,8 dtk; 40 Ankr calls, 0 error, partial false; "
    "window 132092512-132093511, 111 NFT (109 ERC-721 + 2 ERC-1155) + 215 ERC-20 mint). "
    "0 first-seen sejati, 0 early lead, 0 strong lead baru, 0 kandidat baru, 0 track-C lead/kandidat baru. "
    "Velocity: 0 lolos (Tampesta-6aA5 +67 dan AgentVOLT +66 rate pertama, ratio None; ONLYAI +40 ratio 0,04; "
    "WHALE-B +4 ratio 0,25; HIVE flat 1255). Sellout 33 (set identik 0531), near-sellout 0, slot berubah 0. "
    "Age rule: Agent Frogs DIHAPUS (>48h, 533/2222, belum sold out); Agentyyds + Glitchdroid dilewati (sold out). "
    "Track B: BINANCEAI tetap refund/failed (launched 0, failed 1), Grove freeOpen 0 — tidak ada klaim dibuka. "
    "BLOCK777 (B777) track-C lead ditemukan + dilaporkan sekali oleh hot leg 06:04 WIB, gate website GAGAL "
    "(metode A-N); dicatat gate-blocked di track_c, TIDAK dilaporkan ulang, TIDAK di-preview/mint. "
    "5c: 2 baru dicek (not_verified), 0 sale-shape. Web: Boltbook 0 baru, Sourcify 0 shape, sweep 0 baru, "
    "Odaily/PANews 0 hit, MINTS 0 perubahan status, bridge tidak berubah. 0 preview/mint/claim.")
snap["last_run_wib"] = "2026-11-07 06:01 WIB"
snap["last_run_note"] = snap["runNote0601_1107"]
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot contracts now:", len(snap["contracts"]), "| track_c now:", len(snap["track_c"]))
print("FINALIZE DONE")
