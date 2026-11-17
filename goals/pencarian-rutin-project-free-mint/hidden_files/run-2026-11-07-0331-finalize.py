#!/usr/bin/env python3
"""Finalize run 2026-11-07 03:31 WIB — parent merge (pattern run 0201).
Backs up snapshot + track-c-checked, merges reread (non-None only) + velocity
+ track_c reread, merges 5c checked from run 0301 (11, never merged) + run 0331
(7 OK; transport-failed 0xDA03... NOT merged, retry next run), restores Jager
Agent (dropped from snapshot by the 0301 merge), records Jager Agent Pass as
FREE-SOLD-OUT (excluded, reported once via run report), applies the 48h age
rule to the 17 candidates (16 unique addresses; full entries preserved in
run-2026-11-07-0331-age-removed.json). Scan watermark already advanced by the
scan leg (132073611) — NOT touched here. NO preview/mint/claim/sign/transaction."""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0331"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-20261107-{RUN}")
shutil.copy(f"{HF}/track-c-scan-checked.json", f"{HF}/track-c-scan-checked.json.bak-20261107-{RUN}")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-07-{RUN}-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-07-{RUN}-velocity.json"))
fivec = json.load(open(f"{HF}/run-2026-11-07-{RUN}-5c-newscan.json"))
fivec0301 = json.load(open(f"{HF}/run-2026-11-07-0301-5c-newscan.json"))
age = json.load(open(f"{HF}/run-2026-11-07-{RUN}-age-candidates.json"))
REREAD_BLOCK = reread["block"]  # 132073476
contracts = snap["contracts"]
tc = snap.setdefault("track_c", {})

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

# 4. 5c checked merge — run 0301 (11, never merged) + run 0331; transport-failed NOT merged
chk = json.load(open(f"{HF}/track-c-scan-checked.json"))
lst = chk.setdefault("checked", [])
have = {a.lower() for a in lst if isinstance(a, str)}
added = 0; skipped_tf = 0
for src in (fivec0301, fivec):
    for res in src.get("results", []):
        a = res.get("address", "")
        if res.get("verdict") == "transport-failed" or res.get("sourcify") is None and res.get("verdict") is None:
            skipped_tf += 1
            continue
        if a and a.lower() not in have:
            lst.append(a); have.add(a.lower()); added += 1
json.dump(chk, open(f"{HF}/track-c-scan-checked.json", "w"), indent=1)
print("5c checked added:", added, "| transport-failed skipped:", skipped_tf,
      "| list total now:", len(lst))

# 5. special-check run notes (fresh parent verification this run)
onlyai = contracts.get("ONLYAI-Crystals")
if onlyai:
    onlyai["runNote0331_onlyai"] = (
        "Run 0331: totalSupply 1234 -> 1257 @ blok 132075930 (reread 132073476); MAX_SUPPLY 5555. "
        "Semua free view TETAP revert, balanceOf(user) 0 — free% + slot user tetap UNVERIFIED. "
        "BUKAN strong lead, BUKAN kandidat. Tetap watchlist-launched.")
sage = contracts.get("Sage Trials")
if sage:
    sage["totalSupply"] = 33
    sage["runNote0331_sage"] = (
        "Run 0331: totalSupply 19 -> 33 @ blok 132075930; MAX_SUPPLY 5000, mintOpen=1, "
        "freeClaimed(user)=0, balanceOf(user)=0, quote(user,1)=(1 token, cost 0), PRICE 0,00008 BNB. "
        "Free% unverified + tanpa website -> tetap early lead saja, BUKAN strong lead. Tidak ada promosi.")
giraffe = contracts.get("GiraffeValley")
if giraffe:
    giraffe["totalMinted"] = 6
    giraffe["freeMinted"] = 6
    giraffe["runNote0331_giraffe"] = (
        "Run 0331: totalMinted 5 -> 6 @ blok 132075937; MAX_SUPPLY 8000, FREE_POOL 1000, "
        "freeRemaining 994, gate()=registry 0x60B926… persis, freeMintCount(user)=0, "
        "quote(user,1)=0,000187 BNB (mgmtFee, bukan gas-only). Tetap early lead saja "
        "(free 0,6%, tanpa website), BUKAN strong lead.")
hunt = contracts.get("HUNT PASS")
if hunt:
    hunt["totalMinted"] = 831
    hunt["lastReadBlock"] = 132075789
    hunt["lastReadWib"] = "2026-11-07 run 0331"
    hunt["runNote0331_huntpass"] = (
        "Run 0331: totalMinted 773 -> 831 @ blok 132075789; FREE_SUPPLY 3000, MAX_SUPPLY 7000, "
        "mintedBy(user)=0, balanceOf(user)=0. freeClaimed()/freeMinted()/quote() TETAP revert "
        "(transport 2x untuk freeMinted/freeLeft) — free% tetap UNVERIFIED; inferensi "
        "totalMinted/FREE_SUPPLY = 27,7% BUKAN free counter terverifikasi (totalPaid belum dibaca). "
        "Umur first-mint ~02:00 WIB 7 Nov (masih <=48 jam) tapi kaki 25% + slot belum terverifikasi "
        "dan tanpa website -> tetap early lead saja, BUKAN strong lead, TIDAK di-preview/mint.")

# 6. Jager Agent Pass — FREE SOLD OUT: record as excluded (was dropped from the
#    snapshot by the 0301 merge; free pool 333/333 habis @ blok 132075789).
#    Reported once via the run report; do NOT re-add as a live contract.
excl = snap.setdefault("excluded", {})
excl["Jager Agent Pass"] = {
    "address": "0x951f705feB9dCc95D58b445BE58b869724E50707",
    "symbol": "JAP",
    "track": "A",
    "status": "excluded-free-sold-out-2026-11-07",
    "note": ("EARLY lead run 0201 (temuan kaki scan). Free pool HABIS run 0331: freeMinted 333/333 "
             "MAX_FREE_TOTAL @ blok 132075789 (322 @ run 0301, 33 mint dalam window scan run ini); "
             "totalMinted 334, MAX_SUPPLY 777, paidMinted 1 (MINT_PRICE 0,0015 BNB). First mint blok "
             "132063335, 2026-11-07 02:18:06 WIB. User tidak sempat mint (balanceOf 0, slot tidak "
             "terverifikasi sebelum habis). Dilaporkan sekali sebagai perubahan (sold out) run 0331; "
             "tidak di-preview/mint. Entri sempat hilang dari snapshot pada merge run 0301; dicatat "
             "di sini agar tidak ditemukan ulang sebagai lead."),
}
print("Jager Agent Pass recorded as excluded-free-sold-out")

# 7. Jager Agent — restore to snapshot (dropped by the 0301 merge; still early lead)
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
seen_c = seen.get("contracts", {})
fs = None
for k, v in seen_c.items():
    if k.lower() == "0xd8ebdde362b0a72f7d61b5ed990742b940e30d27":
        fs = v if isinstance(v, int) else v.get("first_seen_block")
contracts["Jager Agent"] = {
    "address": "0xD8EBDDE362B0a72F7D61b5eD990742B940E30D27",
    "name": "Jager Agent",
    "kind": "ERC721",
    "status": "early-lead-backfill-2026-11-07",
    "totalMinted": 32,
    "freeMinted": 32,
    "MAX_SUPPLY": 1110,
    "balanceOf_user": 0,
    "owner": "0x67230d320f714ac82c6ec253d238cfa309fb1b85",
    "note": ("EARLY lead backfill run 0201 (first mint blok 132067118, 2 mint/2 minter; owner sama "
             "0x67230d… dengan Jager Agent Pass — same owner group). Entri sempat hilang dari snapshot "
             "pada merge run 0301; DIPULIHKAN run 0331. Free% + slot user UNVERIFIED "
             "(FREE_SUPPLY/freeClaimed 429/revert; totalSupply() revert). Sourcify not_verified. "
             "Tanpa website. BUKAN strong lead, BUKAN kandidat. TIDAK pernah di-preview/mint."),
    "firstSeenBlock": fs,
    "first_seen_block": fs,
    "lastReadBlock": 132075789,
    "lastReadWib": "2026-11-07 run 0331",
    "velocityNote": "no-fresh-supply",
    "velocityVerified": False,
    "runNote0331_jageragent": (
        "Run 0331: totalMinted 18 -> 32 @ blok 132075789; freeMinted 32 (catatan: freeMinted 1 lebih "
        "tinggi dari totalMinted di run 0301 — counter berbeda, dicatat apa adanya); MAX_SUPPLY 1110; "
        "balanceOf(user) 0. Tetap early lead saja."),
}
print("Jager Agent restored to snapshot; firstSeenBlock:", fs)

# 8. AGE RULE — remove verified >48h live-status entries (same logic as run 0201)
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

# 9. snapshot run notes + save
snap["timestamp_wib"] = "2026-11-07T04:00:00+07:00"
snap["last_run_wib"] = "2026-11-07 03:31 WIB"
snap["runNote0331_1107"] = (
    "Run 0331 (jadwal 03:31 WIB 2026-11-07): 0 kandidat, 0 strong-lead baru, 0 early-lead baru, "
    "0 track-C lead/kandidat baru, 0 sellout baru, 0 slot berubah, 0 auto-mint/claim. Scan route 4: "
    "pre-flight LULUS 13,2 dtk (head 132073573); window 132072612-132073611 (1000 blok cap), 20 chunk, "
    "40 Ankr calls, 0 error (102 ERC721 + 251 ERC-20) — watermark -> 132073611; skipped gap "
    "132070175-132072611 (2437 blok) milik backfill. First-seen 0. Re-read 482 kontrak + 56 track_c @ "
    "blok 132073476; velocity 0 lolos. Jager Agent Pass FREE SOLD OUT 333/333 (dilaporkan sekali, "
    "dicatat excluded). Jager Agent DIPULIHKAN ke snapshot (hilang pada merge 0301). Age rule: 16 alamat "
    "unik (17 entri) >48 jam DIHAPUS. 5c: 8 baru dicek (0 sale-shape; 0xDA03… transport-failed, retry "
    "run berikut) + 11 dari run 0301 yang belum pernah di-merge. Web: Bearlambo bukan sale-shape; "
    "Wezards MAGES user tidak pegang NFT; sweep + Odaily/PANews nihil. Binanceai tetap refund/failed "
    "(launched 0); Grove freeOpen 0. Bridge tidak berubah, 0 temuan pelengkap baru.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved; contracts now:", len(snap["contracts"]), "| track_c:", len(tc),
      "| excluded:", len(snap.get("excluded", {})))
