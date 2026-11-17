#!/usr/bin/env python3
"""Finalize run 2026-11-07 07:01 WIB — parent merge, written fresh for THIS run's data.
Merges reread (non-None only) + velocity + track_c reread, merges 5c checked
(5 new: all not_verified, 0 transport-failed), advances scan watermark to the
scan head UNLESS backfill already advanced it further (never regress; backfill
was at 132098931 when this script was written), applies the 48h age rule
(REMOVES PassAgentX + Bathybots; Agentyyds + Glitchdroid both sold out -> skipped),
records 0 true first-seen in the scan window (96 contracts, all known-seen/snapshot).
Adds per-item run notes with THIS run's numbers.
NO preview/mint/claim/sign/transaction.
"""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0701"
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
vey_old = old_total("Veyanth")

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
    onlyai["runNote0701_onlyai"] = (
        f"Run 0701: totalSupply {onlyai_old[0]} -> {onlyai.get('totalSupply')} @ blok {REREAD_BLOCK}; "
        "MAX_SUPPLY 5555. Semua free view TETAP revert, balanceOf(user) 0 — free% + slot user tetap "
        "UNVERIFIED. Velocity GAGAL (+21, rate 0,8023/mnt, ratio 0,70 <1,5). BUKAN strong lead, BUKAN kandidat. Tetap watchlist-launched.")
ape = contracts.get("Ape Agent")
if ape:
    ape["runNote0701_ape"] = (
        f"Run 0701: totalSupply {ape_old[0]} -> {ape.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+3 interval, rate 0,1146/mnt, ratio 0,40 — velocity TIDAK lolos). Free% "
        "UNVERIFIED (tidak ada free counter terbaca), website null (MINTS). "
        "BUKAN strong lead, BUKAN kandidat. Tetap watchlist-only.")
volt = contracts.get("AgentVOLT (round 1)")
if volt:
    volt["runNote0701_volt"] = (
        f"Run 0701: totalSupply {volt_old[0]} -> {volt.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+14 interval, rate 0,5349/mnt, ratio 0,23 — velocity GAGAL). Free% "
        "UNVERIFIED (semua free view revert), website null (MINTS). BUKAN strong lead (kaki 25% free tidak terverifikasi), "
        "BUKAN kandidat. Tetap watchlist-only.")
wb = contracts.get("WHALE-B")
if wb:
    wb["runNote0701_whale_b"] = (
        f"Run 0701: totalSupply {whale_old[0]} -> {wb.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+16 dalam 26,18 mnt, 0,6113/mnt, ratio 1,41 <1,5 — TAPI <20 token, velocity GAGAL). "
        "free% TETAP UNVERIFIED (tidak ada free counter/cap terbaca, Sourcify unverified, shape unknown); "
        "slot open (balance 0). Velocity-only, bukan strong lead, bukan kandidat.")
tamp = contracts.get("Tampesta-6aA5")
if tamp:
    tamp["runNote0701_tampesta"] = (
        f"Run 0701: totalSupply {tamp_old[0]} -> {tamp.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+37 interval, rate 1,4136/mnt, ratio 0,38 — velocity GAGAL). Free% "
        "UNVERIFIED. BUKAN strong lead (kaki 25% free tidak terverifikasi), BUKAN kandidat. Tetap watchlist-only.")
vey = contracts.get("Veyanth")
if vey:
    vey["runNote0701_veyanth"] = (
        f"Run 0701: totalSupply {vey_old[0]} -> {vey.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(flat, 0 mint interval); freePct 65,36 (free counter terbaca); balanceOf(user)=3; minted-by-user, bukan kandidat.")
hive = contracts.get("HIVE Agents")
if hive:
    hive["runNote0701"] = (
        f"Run 0701 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 0631 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
    side = contracts.get("Sidecoo")
    if side:
        side["runNote0701_sidecoo"] = (
            f"Run 0701: totalSupply 15749 -> {side.get('totalSupply')} @ blok {REREAD_BLOCK} "
            "(+311 interval, rate 11,8816/mnt, ratio 41,2 — velocity LEG LOLOS (>=1,5x DAN >=20 token) "
            "TAPI free% UNVERIFIED (freeMinted/freeClaimed null, MAX_SUPPLY tak terbatas, quote user garbage) "
            "dan umur/website/X UNVERIFIED. BUKAN strong lead, BUKAN kandidat. Tetap watchlist-only.")
    ore = contracts.get("Ore Raiders SHIP (checked-2026-11-05)")
    if ore:
        ore["runNote0701_ore"] = (
            f"Run 0701: totalSupply 1004 -> {ore.get('totalSupply')} @ blok {REREAD_BLOCK} "
            "(+202 interval, rate 7,7173/mnt, ratio None (rate sebelumnya 0) — velocity TIDAK lolos "
            "(rasio tak terhitung). freePct 8,33 (500/6000) — jauh di bawah 25% kaki strong lead. "
            "BUKAN strong lead, BUKAN kandidat. Tetap watchlist-only.")

# 6. AGE RULE — PassAgentX + Bathybots NOT sold out and first_seen < threshold
# -> REMOVED. Agentyyds + Glitchdroid both sold out -> skipped per the exception.
removed = []
removed_evidence = {}
for cand in age.get("candidates", []):
    name = cand.get("name")
    sold = any(r.get("name") == name for r in vel.get("soldOut", []))
    if sold:
        print(f"age: {name} skipped (sold out)")
        continue
    if name in contracts:
        ev = contracts.pop(name)
        removed.append(name)
        removed_evidence[name] = {
            "address": ev.get("address"),
            "first_seen_block": cand.get("first_seen_block"),
            "threshold_block": age.get("threshold_block"),
            "totalSupply_at_removal": ev.get("totalSupply"),
            "launch_note": ev.get("launchNote"),
            "status_before": ev.get("status"),
        }
        print(f"age: REMOVED {name} first_seen={cand.get('first_seen_block')} "
              f"threshold={age.get('threshold_block')} soldOut=False "
              f"totalSupply={ev.get('totalSupply')}")
snap["runNote0701_age_removed"] = {
    "removed": removed,
    "evidence": ("PassAgentX 0x08b1A979Dd997492EEcc010fe986eA2e2925e620: mintStart() terverifikasi "
                 "2026-11-05 06:49:58 WIB -> umur 48j11m saat run 07:01 WIB (>48j); totalSupply 4750/6666, "
                 "tidak sold out; first_seen 131715736 < threshold 131719119. "
                 "Bathybots 0x9610195ac5304B697080ea1252C70613a098E388: first_seen 131716195 < threshold "
                 "131719119 (batas bawah umur >48j terjamin); totalSupply 285/4000, tidak sold out; "
                 "launch time tetap UNVERIFIED (first_block scan hanya batas bawah). "
                 "Keduanya early-lead-reported 2026-11-05, dihapus dari watchlist aktif run 0701; "
                 "perubahan ini dilaporkan sekali ke chat utama (age-exclusion)."),
    "removed_evidence": removed_evidence,
    "skipped_sold_out": ["Agentyyds", "Glitchdroid"],
}
print("age removed:", removed)

# 7. BLOCK777 (B777) — already in track_c as gate-blocked (hot leg 06:04 WIB).
# This run does NOT re-report it; only note the reread read (totalSupply token units).
B777 = "0x47529CF66091BeB0E8e0F78D5635e367473D52d5"
if B777 in tc:
    tc[B777]["runNote0701"] = (
        f"Run 0701: reread totalSupply token 1e29 (satuan wei token), balanceOf(user)=0; "
        "gate-blocked website (metode A-N) tetap berlaku — TIDAK di-preview/di-mint, TIDAK dilaporkan ulang.")
    print("track_c: BLOCK777 gate-blocked note updated, no re-report")
else:
    print("track_c: BLOCK777 MISSING — unexpected, left as-is")

# 8. scan watermark advance + seen-file update (scan leg did NOT do these).
# NEVER regress: backfill had advanced the watermark to 132098931 already.
state = json.load(open(f"{HF}/onchain-scan-state.json"))
prev_wm = state.get("last_scanned_block")
scan_head = scan["to_block"]
new_wm = max(prev_wm or 0, scan_head)
state["last_scanned_block"] = new_wm
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = "2026-11-07 run 0701"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = len(scan.get("erc20_mint_contracts_list", []))
state["skipped_gap"] = ("132098932-132100343 (1412 blok; window main scan 132100344-132101343 "
                        "dimulai dari head-999 karena gap ke watermark 2376 blok > cap 1000; "
                        "sisa gap ini ditutup bertahap oleh backfill, bukan dengan memperbesar window)")
state["note_0701"] = ("Scan run 0701 SUKSES (preflight 4,8 dtk, head 132101307, 273 logs/50 blok; "
                      "ankr eth_blockNumber gagal parse seperti biasa, fallback fast_rpc race; "
                      "40 Ankr calls, 0 errors, partial false; 96 NFT + 366 ERC-20 mint). "
                      "0 first-seen sejati di window (96 kontrak semua known-seen/snapshot) => 0 EARLY lead. "
                      "5c: 5 baru dicek (semuanya not_verified), 0 sale-shape, 0 transport-failed. BLOCK777 (B777) "
                      "gate-blocked, tidak dilaporkan ulang run ini.")
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
snap["runNote0701_1107"] = (
    "Scan run 0701 SUKSES (preflight 4,8 dtk; 40 Ankr calls, 0 errors, partial false; "
    "window 132100344-132101343, 96 NFT + 366 ERC-20 mint). "
    "0 first-seen sejati => 0 EARLY lead baru. 0 strong lead baru, "
    "0 kandidat baru, 0 track-C lead/kandidat baru. "
    "Velocity: 1 baris lolos — Sidecoo +311 ratio 41,2 TAPI free% UNVERIFIED => bukan strong lead/kandidat; "
    "Ore Raiders +202 ratio tak terhitung (rate sebelumnya 0), freePct 8,33; ONLYAI +21 ratio 0,70 gagal; "
    "Tampesta +37 ratio 0,38 gagal; AgentVOLT +14 ratio 0,23 gagal; WHALE-B +16 ratio 1,41 gagal; "
    "HIVE flat 1255; Veyanth flat freePct 65,36. Sellout 33 (set identik 0631), near-sellout 0, slot berubah 0. "
    "Age rule: PassAgentX + Bathybots DIHAPUS (umur >48j, tidak sold out) — dilaporkan sekali; "
    "Agentyyds + Glitchdroid dilewati (sold out). "
    "Track B: BINANCEAI tetap refund/failed (launched 0, failed 1, isRefundPhase 1), Grove freeOpen 0 — tidak ada klaim dibuka. "
    "BLOCK777 (B777) gate-blocked, TIDAK dilaporkan ulang, TIDAK di-preview/mint. "
    "5c: 5 baru dicek (not_verified), 0 sale-shape. Web: Boltbook 0 baru (Mirror Pair masih tampil di front page "
    "tapi sudah age-excluded run 2131 2026-11-03), Sourcify 2 baru dicek shape (0xd3bE54.. S1/S2 false, 0x0b3e7c.. S1/S2 false), "
    "sweep 0 baru (hanya item lama: AGENT MAO paused, daftar 22 proyek 30 Okt, cek 8 mint 2 Nov), Odaily/PANews 0 hit, "
    "bridge tidak berubah (115 entri, terakhir diubah 2026-11-06 02:48). 0 preview/mint/claim.")
snap["last_run_wib"] = "2026-11-07 07:01 WIB"
snap["last_run_note"] = snap["runNote0701_1107"]
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot contracts now:", len(snap["contracts"]), "| track_c now:", len(snap["track_c"]))
print("FINALIZE DONE")
