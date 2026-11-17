#!/usr/bin/env python3
"""Finalize run 2026-11-07 01:31 WIB — parent merge (pattern run 0101).
Backs up snapshot + track-c-checked, merges reread (non-None only) + velocity
+ track_c reread + 5c checked (NOT-verified only; transport-failed NOT merged,
retry next run), advances scan watermark to 132059846 (scan complete, 40 calls,
0 errors), writes run notes. NO preview/mint/claim/sign/transaction."""
import json, shutil, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0131"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-20261107-{RUN}")
shutil.copy(f"{HF}/track-c-scan-checked.json", f"{HF}/track-c-scan-checked.json.bak-20261107-{RUN}")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-07-{RUN}-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-07-{RUN}-velocity.json"))
tc_reread = json.load(open(f"{HF}/run-2026-11-07-{RUN}-reread-tc.json"))
fivec = json.load(open(f"{HF}/run-2026-11-07-{RUN}-5c-newscan.json"))
REREAD_BLOCK = reread["block"]  # 132059916
contracts = snap["contracts"]

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
for ns in vel.get("nearSellout", []):
    if ns["name"] in contracts:
        contracts[ns["name"]][f"runNote{RUN}_nearSellout"] = (
            f"Run {RUN}: nyaris sold out {ns['curSupply']}/{ns['maxSupply']} "
            f"(sisa {ns['remaining']}), tetap watchlist (velocity fail).")

# 3. fresh parent verification: MoonCat totalSupply via bsc-dataseed
try:
    r = _single("https://bsc-dataseed.binance.org/", "eth_call",
                [{"to": "0x045425004b622733ced4139e930c622187ea6c73",
                  "data": "0x18160ddd"}, "latest"], 10, retries=0)
    mc = int(r, 16)
    contracts["MoonCat"][f"runNote{RUN}_fresh"] = (
        f"Verifikasi segar parent via bsc-dataseed eth_call totalSupply(): {mc} "
        f"(reread run ini 1108 @ blok {REREAD_BLOCK}, MAX 1111) — "
        f"{'SOLD OUT' if mc >= 1111 else 'masih BELUM sold out'}.")
    print("MoonCat fresh totalSupply:", mc)
except Exception as e:  # noqa: BLE001
    print("MoonCat fresh check FAILED:", e)

# 4. track_c reread merge (non-None only; block 132061240)
tc = snap.get("track_c", {})
tcmerged = 0; tc_none = 0
for name, rv in tc_reread.get("track_c", {}).items():
    if name not in tc or not isinstance(rv, dict):
        continue
    e = tc[name]
    any_val = False
    for k, v in rv.items():
        if k == "address":
            continue
        if v is not None:
            e[k] = v; any_val = True
    if not any_val:
        tc_none += 1
    e["lastReadBlock"] = tc_reread["block"]
    e["lastReadWib"] = f"2026-11-07 run {RUN}"
    tcmerged += 1
print("track_c merged:", tcmerged, "| all-None:", tc_none)

# 5. 5c checked merge — NOT-verified verdicts ONLY; transport-failed NOT merged
chk = json.load(open(f"{HF}/track-c-scan-checked.json"))
lst = chk.setdefault("checked", [])
have = {a.lower() for a in lst if isinstance(a, str)}
added = 0; skipped_tf = 0
for res in fivec["results"]:
    a = res["address"]
    if res.get("verdict") == "transport-failed":
        skipped_tf += 1
        continue
    if a.lower() not in have:
        lst.append(a); have.add(a.lower()); added += 1
json.dump(chk, open(f"{HF}/track-c-scan-checked.json", "w"), indent=1)
print("5c checked added:", added, "| transport-failed skipped (retry next run):", skipped_tf,
      "| list total now:", len(lst), "| sale-shape:", fivec["sale_shape_hits"],
      "| transport_failed:", fivec["transport_failed"])

# 6. ONLYAI Crystals: run note only (reread merge already set totalSupply 902)
onlyai = contracts.get("ONLYAI-Crystals")
if onlyai:
    onlyai[f"runNote{RUN}_onlyai"] = (
        "Run 0131: totalSupply 568 -> 902 @ blok 132059916 (+334, ratio 0,48x vs rate sebelumnya — "
        "velocity GAGAL); MAX_SUPPLY 5555. Semua free view TETAP revert (FREE_SUPPLY 403/revert, "
        "freeSupply/freeMinted/freeClaimed/freeLeft/totalMinted/totalPaid/quote revert), "
        "balanceOf(user) 0 — free% + slot user tetap UNVERIFIED. BUKAN strong lead, BUKAN early lead "
        "(sudah di snapshot). Tetap watchlist-launched.")
    print("ONLYAI note added; totalSupply now:", onlyai.get("totalSupply"))

# 7. scan state — advance watermark (scan complete, 40 calls, 0 errors)
state = json.load(open(f"{HF}/onchain-scan-state.json"))
state["last_scanned_block"] = 132059846
state["last_scan_window_from"] = 132058847
state["last_scan_window_to"] = 132059846
state["last_scan_wib"] = "2026-11-07 run 0131"
state["ankr_calls"] = 40
state["errors"] = []
state["nft_contracts"] = 134
state["erc20_mint_contracts"] = 281
state["skipped_gap"] = ("132057754-132058846 (1093 blok; window dari watermark 132057753 ke head "
                        "132059846 = 1993 blok > cap 1000; main scan menutup 1000 blok terbaru "
                        "132058847-132059846; gap milik backfill)")
state["runNote0131_scan"] = (
    "Scan 0131: pre-flight LULUS 16,6 dtk (head 132059793, 151 log/50 blok; ankr eth_blockNumber "
    "langsung gagal parse, fallback fast_rpc race); window 132058847-132059846 (1000 blok cap), "
    "20 chunk, 40 Ankr calls, 0 errors, partial false; 129 ERC721 + 5 ERC1155 (887 mint) + 281 ERC-20. "
    "0 first-seen sejati (89 known-seen, 44 known-snapshot, 1 registry), 0 early lead. "
    "Watermark -> 132059846; skipped gap 132057754-132058846 (1093 blok) milik backfill.")
json.dump(state, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan state: watermark -> 132059846")

# 8. seen _meta note (0 added this run; total 9988 incl. 1 backfill first-seen)
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
meta = seen.setdefault("_meta", {})
meta["last_scan_wib"] = "2026-11-07 run 0131"
meta["last_scan_window"] = "132058847-132059846"
meta["last_scan_added"] = 0
meta["note_0131_1107"] = ("Run 0131: 0 first-seen sejati (134 kontrak window semua sudah dikenal); "
                          "total seen 9988 (1 dari backfill 132055915-132057753).")
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)
print("seen _meta updated; contracts:", len(seen.get("contracts", {})))

# 9. snapshot run notes
snap["timestamp_wib"] = "2026-11-07T02:10:00+07:00"
snap["last_run_wib"] = "2026-11-07 01:31 WIB"
snap["runNote0131_1107"] = (
    "Run 0131 (jadwal 01:31 WIB 2026-11-07): SILENT — 0 kandidat, 0 strong-lead baru, 0 early-lead baru, "
    "0 track-C lead/kandidat baru, 0 sellout baru, 0 age-exclusion baru, 0 slot berubah. Scan route 4: "
    "pre-flight LULUS 16,6 dtk (head 132059793); window 132058847-132059846 (1000 blok cap), 20 chunk, "
    "40 Ankr calls, 0 error, partial false (129 ERC721 + 5 ERC1155 + 281 ERC-20) — watermark dimajukan -> "
    "132059846; skipped gap 132057754-132058846 (1093 blok) milik backfill. First-seen 0, early lead 0. "
    "Re-read 548 kontrak + 54 track_c @ blok 132059916/132061240; 104/548 totalSupply None (gagal baca, bukan nol). "
    "Velocity 0 lolos (interval ~37,97 mnt vs run 0101). Sellout tetap 33, set identik run 0101. Near-sellout: "
    "Chipdroidling 683/700, Swarmganbei 692/700 (flat). HIVE flat 1255 (minted-by-user, bal 1). MoonCat 1106 -> 1108 "
    "(+2), 3 tersisa dari 1111, velocity 0,23x fail. ONLYAI 568 -> 902 (ratio 0,48x, velocity fail); free% + slot "
    "tetap UNVERIFIED (semua free view revert) — watchlist, bukan lead. Crack 3046 -> 3065 (track_c). "
    "BINANCEAI tetap refund/failed (launched 0, failed 1, isRefundPhase 1) — sudah excluded + dilaporkan sejak "
    "2026-11-02, tanpa perubahan. Grove freeOpen=0. Sourcify feed 20 kontrak, 2 baru, 0 sale-shape; "
    "transport-failed terbuka 0. Boltbook en+zh 7 alamat unik, 3 baru, 0 sale-shape (Mizukairo recheck 314/5.555; "
    "0xcd98… bukan kontrak ter-deploy, eth_getCode 0x di 4 endpoint — bukan early lead). 5c scan baru: 33 ERC-20 "
    "mint_count>=10, 23 sudah dicek, 10 baru dicek (7 not_verified di-merge; 3 transport-failed TIDAK di-merge, "
    "retry run berikut), 0 sale-shape. Bridge tidak berubah sejak 2026-11-06 09:48, 0 temuan pelengkap baru "
    "(7 re-find lama di jendela scan: DGF CARD, M3MO, Saturnode, Hackagent, Ghostpilotcat, Jolly, 0xfe5a… — "
    "tidak dipromosikan). BNB Guardian tanpa perubahan (minted 1441 -> 1443, tetap gate-blocked). AGENT MAO tetap "
    "paused (farming.ai curl rc 52). MINTS 141 proyek / 38 free_live, identik run 0101 (hanya drift minted: "
    "Tacotron 5.846 -> 5.870, Worldygg 19.721 -> 19.722). Odaily/PANews 0 pengumuman Agent ID; DappBay AI hanya "
    "'Guardians of the Car'. Tidak ada preview/mint/claim/approve/sign/transaksi.")
snap["runNote0131_scan"] = state["runNote0131_scan"]
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved. contracts:", len(snap["contracts"]), "track_c:", len(snap.get("track_c", {})),
      "excluded:", len(snap.get("excluded", {})))
