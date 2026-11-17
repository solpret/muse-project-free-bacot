#!/usr/bin/env python3
"""Finalize run 2026-11-07 06:31 WIB — parent merge, written fresh for THIS run's data.
Merges reread (non-None only) + velocity + track_c reread, merges 5c checked
(3 new: all not_verified, 0 transport-failed), advances scan watermark to the
scan head UNLESS backfill already advanced it further (never regress; backfill
was at 132096338 when this script was written), applies the 48h age rule
(Agentyyds + Glitchdroid both sold out -> skipped, 0 removed),
records OSE first-seen (not agent-shaped, seen-file only, never an early lead).
Adds per-item run notes with THIS run's numbers.
NO preview/mint/claim/sign/transaction.
"""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0631"
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
    onlyai["runNote0631_onlyai"] = (
        f"Run 0631: totalSupply {onlyai_old[0]} -> {onlyai.get('totalSupply')} @ blok {REREAD_BLOCK}; "
        "MAX_SUPPLY 5555. Semua free view TETAP revert, balanceOf(user) 0 — free% + slot user tetap "
        "UNVERIFIED. Velocity GAGAL (+16, rate 1,1538/mnt, ratio 1,42 <1,5). BUKAN strong lead, BUKAN kandidat. Tetap watchlist-launched.")
ape = contracts.get("Ape Agent")
if ape:
    ape["runNote0631_ape"] = (
        f"Run 0631: totalSupply {ape_old[0]} -> {ape.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+4 interval, rate 0,2884/mnt, ratio 1,77 — TAPI <20 token, velocity TIDAK lolos). Free% "
        "UNVERIFIED (tidak ada free counter terbaca), website null (MINTS). "
        "BUKAN strong lead, BUKAN kandidat. Tetap watchlist-only.")
volt = contracts.get("AgentVOLT (round 1)")
if volt:
    volt["runNote0631_volt"] = (
        f"Run 0631: totalSupply {volt_old[0]} -> {volt.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+32 interval, rate 2,3076/mnt, ratio 1,72 — velocity LEG LOLOS (>=1,5x DAN >=20 token) TAPI free% "
        "UNVERIFIED (semua free view revert), website null (MINTS). BUKAN strong lead (kaki 25% free tidak terverifikasi), "
        "BUKAN kandidat. Tetap watchlist-only.")
wb = contracts.get("WHALE-B")
if wb:
    wb["runNote0631_whale_b"] = (
        f"Run 0631: totalSupply {whale_old[0]} -> {wb.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+6 dalam 13,86 mnt, 0,4327/mnt, ratio 5,32 — TAPI <20 token, velocity GAGAL). "
        "free% TETAP UNVERIFIED (tidak ada free counter/cap terbaca, Sourcify unverified, shape unknown); "
        "slot open (balance 0). Velocity-only, bukan strong lead, bukan kandidat.")
tamp = contracts.get("Tampesta-6aA5")
if tamp:
    tamp["runNote0631_tampesta"] = (
        f"Run 0631: totalSupply {tamp_old[0]} -> {tamp.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(+51 interval, rate 3,6777/mnt, ratio 2,7 — velocity LEG LOLOS (>=1,5x DAN >=20 token) TAPI free% "
        "UNVERIFIED. BUKAN strong lead (kaki 25% free tidak terverifikasi), BUKAN kandidat. Tetap watchlist-only.")
vey = contracts.get("Veyanth")
if vey:
    vey["runNote0631_veyanth"] = (
        f"Run 0631: totalSupply {vey_old[0]} -> {vey.get('totalSupply')} @ blok {REREAD_BLOCK} "
        "(flat, 0 mint interval); freePct 65,36 (free counter terbaca); balanceOf(user)=3; minted-by-user, bukan kandidat.")
hive = contracts.get("HIVE Agents")
if hive:
    hive["runNote0631"] = (
        f"Run 0631 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 0601 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")

# 6. AGE RULE — Agentyyds + Glitchdroid are both sold out -> skipped per the sold-out exception.
removed = []
for cand in age.get("candidates", []):
    name = cand.get("name")
    sold = any(r.get("name") == name for r in vel.get("soldOut", []))
    if sold:
        print(f"age: {name} skipped (sold out)")
        continue
    if name in contracts:
        ev = contracts.pop(name)
        removed.append(name)
        print(f"age: REMOVED {name} first_seen={cand.get('first_seen_block')} "
              f"threshold={age.get('threshold_block')} soldOut=False "
              f"totalSupply={ev.get('totalSupply')}")
snap["runNote0631_age_removed"] = {
    "removed": removed,
    "evidence": ("Agentyyds + Glitchdroid keduanya sold out (set sellout 33 identik run 0601) "
                 "-> dilewati per pengecualian sold-out aturan 48 jam; 0 dihapus run 0631."),
    "skipped_sold_out": ["Agentyyds", "Glitchdroid"],
}
print("age removed:", removed)

# 7. BLOCK777 (B777) — already in track_c as gate-blocked (hot leg 06:04 WIB).
# This run does NOT re-report it; only note the reread read (totalSupply token units).
B777 = "0x47529CF66091BeB0E8e0F78D5635e367473D52d5"
if B777 in tc:
    tc[B777]["runNote0631"] = (
        f"Run 0631: reread totalSupply token 1e29 (satuan wei token), balanceOf(user)=0; "
        "gate-blocked website (metode A-N) tetap berlaku — TIDAK di-preview/di-mint, TIDAK dilaporkan ulang.")
    print("track_c: BLOCK777 gate-blocked note updated, no re-report")
else:
    print("track_c: BLOCK777 MISSING — unexpected, left as-is")

# 8. scan watermark advance + seen-file update (scan leg did NOT do these).
# NEVER regress: backfill had advanced the watermark to 132096338 already.
state = json.load(open(f"{HF}/onchain-scan-state.json"))
prev_wm = state.get("last_scanned_block")
scan_head = scan["to_block"]
new_wm = max(prev_wm or 0, scan_head)
state["last_scanned_block"] = new_wm
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = "2026-11-07 run 0631"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = len(scan.get("erc20_mint_contracts_list", []))
state["skipped_gap"] = ("132096339-132097121 (783 blok; window main scan 132097122-132098121 "
                        "dimulai dari head-999 karena gap ke watermark 3004 blok > cap 1000; "
                        "backfill sudah menutup 132094118-132096338; sisa gap ini ditutup bertahap "
                        "oleh backfill, bukan dengan memperbesar window)")
state["note_0631"] = ("Scan run 0631 SUKSES (preflight 8,6 dtk, head 132097851, 111 logs/50 blok; "
                      "ankr eth_blockNumber gagal parse seperti biasa, fallback fast_rpc race; "
                      "40 Ankr calls, 1 error (getCode timeout 0xAbF2C4A99a6b1d97989497AddCFDc1D27ECE3557), "
                      "partial false; 99 NFT (96 ERC-721 + 3 ERC-1155) + 299 ERC-20 mint). "
                      "1 first-seen sejati (Obsidian Sovereign Eagle 0xAbF2C4A99a6b1d97989497AddCFDc1D27ECE3557, "
                      "78 mints/64 minters) — Sourcify not_verified, tanpa registry/AgentGate/free-mint evidence "
                      "=> BUKAN agent-shaped, BUKAN early lead (seen-file only). 5c: 3 baru dicek "
                      "(semuanya not_verified), 0 sale-shape, 0 transport-failed. BLOCK777 (B777) "
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
snap["runNote0631_1107"] = (
    "Scan run 0631 SUKSES (preflight 8,6 dtk; 40 Ankr calls, 1 error getCode timeout, partial false; "
    "window 132097122-132098121, 99 NFT (96 ERC-721 + 3 ERC-1155) + 299 ERC-20 mint). "
    "1 first-seen sejati (Obsidian Sovereign Eagle, 78 mints/64 minters) — Sourcify not_verified, tanpa "
    "registry/AgentGate/free-mint evidence => BUKAN agent-shaped, BUKAN early lead. 0 strong lead baru, "
    "0 kandidat baru, 0 track-C lead/kandidat baru. "
    "Velocity: 3 baris lolos di velocity.json — 1 artefak bridge-token (VOLT token, satuan wei) + "
    "2 leg NFT nyata (Tampesta-6aA5 +51 ratio 2,7; AgentVOLT +32 ratio 1,72) TAPI free% keduanya "
    "UNVERIFIED => bukan strong lead/kandidat; ONLYAI +16 ratio 1,42 gagal; WHALE-B +6 ratio 5,32 tapi <20; "
    "HIVE flat 1255; Veyanth flat freePct 65,36. Sellout 33 (set identik 0601), near-sellout 0, slot berubah 0. "
    "Age rule: Agentyyds + Glitchdroid dilewati (sold out); 0 dihapus. "
    "Track B: BINANCEAI tetap refund/failed (launched 0, failed 1, isRefundPhase 1), Grove freeOpen 0 — tidak ada klaim dibuka. "
    "BLOCK777 (B777) gate-blocked, TIDAK dilaporkan ulang, TIDAK di-preview/mint. "
    "5c: 3 baru dicek (not_verified), 0 sale-shape. Web: Boltbook 0 baru (Mirror Pair masih tampil di front page "
    "tapi sudah age-excluded run 2131 2026-11-03), Sourcify 0 shape (20/20 hot-leg-seen), sweep 0 baru "
    "(hanya daftar lama 24 Okt-1 Nov), Odaily/PANews 0 hit, bridge tidak berubah. 0 preview/mint/claim.")
snap["last_run_wib"] = "2026-11-07 06:31 WIB"
snap["last_run_note"] = snap["runNote0631_1107"]
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot contracts now:", len(snap["contracts"]), "| track_c now:", len(snap["track_c"]))
print("FINALIZE DONE")
