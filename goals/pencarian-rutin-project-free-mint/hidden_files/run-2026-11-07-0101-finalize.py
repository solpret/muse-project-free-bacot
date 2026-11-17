#!/usr/bin/env python3
"""Finalize run 2026-11-07 01:01 WIB — parent merge (pattern run 0031).
Backs up snapshot + track-c-checked, merges reread (non-None only) + velocity
+ track_c reread + 5c checked, updates ONLYAI launch state, advances scan
watermark (recovered scan counts as success: chunk phase 40 calls/0 errors +
full re-fetch 40 calls/0 errors, identical counts), writes run notes.
NO preview/mint/claim/sign/transaction."""
import json, shutil, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0101"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-20261107-{RUN}")
shutil.copy(f"{HF}/track-c-scan-checked.json", f"{HF}/track-c-scan-checked.json.bak-20261107-{RUN}")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-07-{RUN}-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-07-{RUN}-velocity.json"))
tc_reread = json.load(open(f"{HF}/run-2026-11-07-{RUN}-reread-tc.json"))
fivec = json.load(open(f"{HF}/run-2026-11-07-{RUN}-5c-newscan.json"))
REREAD_BLOCK = reread["block"]  # 132054853
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
print("velocity rows merged:", vmerged, "| passes:", len(vel.get("passes", [])))
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
        f"(reread run ini 1106 @ blok {REREAD_BLOCK}, MAX 1111) — "
        f"{'SOLD OUT' if mc >= 1111 else 'masih BELUM sold out'}.")
    print("MoonCat fresh totalSupply:", mc)
except Exception as e:  # noqa: BLE001
    print("MoonCat fresh check FAILED:", e)

# 4. track_c reread merge (non-None only; separate file this run, block 132056860)
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

# 5. 5c checked merge — append to the 'checked' LIST (dedup case-insensitive)
chk = json.load(open(f"{HF}/track-c-scan-checked.json"))
lst = chk.setdefault("checked", [])
have = {a.lower() for a in lst if isinstance(a, str)}
added = 0
for res in fivec["results"]:
    a = res["address"]
    if a.lower() not in have:
        lst.append(a); have.add(a.lower()); added += 1
json.dump(chk, open(f"{HF}/track-c-scan-checked.json", "w"), indent=1)
print("5c checked added:", added, "| list total now:", len(lst),
      "| sale-shape:", fivec["sale_shape_hits"], "| transport-failed:", fivec["transport_failed"])

# 6. ONLYAI Crystals: upcoming -> LAUNCHED (mintStart 2026-11-07 01:00 WIB verified)
onlyai = contracts.get("ONLYAI-Crystals")
if onlyai:
    onlyai["status"] = "watchlist-launched-2026-11-07"
    onlyai["totalSupply"] = 568
    onlyai["previousTotalSupply"] = 0
    onlyai["mintedInInterval"] = 568
    onlyai["intervalMinutes"] = 31.25
    onlyai["currentRatePerMin"] = 18.1745
    onlyai["previousRatePerMin"] = None
    onlyai["velocityVerified"] = False
    onlyai["lastReadBlock"] = REREAD_BLOCK
    onlyai["lastReadWib"] = f"2026-11-07 run {RUN}"
    onlyai[f"runNote{RUN}_launch"] = (
        "LAUNCHED sesuai jadwal 2026-11-07 01:00 WIB: totalSupply 0 -> 568 @ blok 132054853 "
        "(18,17/mnt, 203 minter di jendela backfill + 146 di jendela scan utama); verifikasi segar "
        "parent: totalSupply 782, MAX_SUPPLY 5555, balanceOf(user) 0. Free views SEMUA revert "
        "(FREE_SUPPLY/freeSupply/freeMinted/freeClaimed/freeLeft/totalMinted/totalPaid/"
        "freeClaimed(address)/freeMintedBy/hasFreeMint/freeFor/quote) + Sourcify IncompleteRead — "
        "free% UNVERIFIED, slot user UNVERIFIED. BUKAN strong lead (butuh >=25% free terverifikasi + "
        "slot terbuka; 568/5555 = 10,2% pun hanya inferensi) dan BUKAN early lead (sudah ada di "
        "snapshot sebagai upcoming sejak run 0131 + sudah di seen). Tetap watchlist; velocity baru "
        "bisa dihitung run berikutnya.")
    print("ONLYAI updated: launched, 568 @", REREAD_BLOCK)

# 7. scan state — advance watermark (recovered scan = full coverage, identical counts)
state = json.load(open(f"{HF}/onchain-scan-state.json"))
state["last_scanned_block"] = 132054651
state["last_scan_window_from"] = 132053652
state["last_scan_window_to"] = 132054651
state["last_scan_wib"] = "2026-11-07 run 0101 (recovered)"
state["ankr_calls"] = 80
state["errors"] = ["scan process killed mid-enrichment 85/129 ~01:21 WIB; full re-fetch same window "
                   "266.1s, 40 calls, 0 errors, counts identical (126/3/424) — recovered, watermark advanced"]
state["nft_contracts"] = 129
state["erc20_mint_contracts"] = 424
state["skipped_gap"] = ("132051227-132053651 (2425 blok; window dari watermark 132051226 ke head "
                        "132054651 > cap 1000; main scan menutup 1000 blok terbaru 132053652-132054651; "
                        "backfill menutup gap: worker 132051227-132053226 SELESAI, 132053227-132053666 berjalan)")
state["runNote0101_scan"] = (
    "Scan 0101: pre-flight LULUS 10,2 dtk (head 132054578, 411 log/50 blok); window 132053652-132054651 "
    "(1000 blok cap), chunk phase 20 chunk, 40 Ankr calls, 0 errors; kill incident mid-enrichment "
    "(85/129) + recovery re-fetch penuh (40 calls, 0 errors, counts identik); partial JSON 84 enriched "
    "+ recover JSON 129 penuh. 0 first-seen sejati, 0 early lead. Watermark -> 132054651.")
json.dump(state, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan state: watermark -> 132054651")

# 8. seen _meta note (0 added this run)
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
meta = seen.setdefault("_meta", {})
meta["last_scan_wib"] = "2026-11-07 run 0101"
meta["last_scan_window"] = "132053652-132054651"
meta["last_scan_added"] = 0
meta["note_0101_1107"] = ("Run 0101: 0 first-seen sejati (129 kontrak window semua sudah dikenal); "
                          "ONLYAI Crystals sudah di seen + snapshot (upcoming -> launched).")
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)
print("seen _meta updated; contracts:", len(seen.get("contracts", {})))

# 9. snapshot run notes
snap["timestamp_wib"] = "2026-11-07T01:40:00+07:00"
snap["last_run_wib"] = "2026-11-07 01:01 WIB"
snap["runNote0101_1107"] = (
    "Run 0101 (jadwal 01:01 WIB 2026-11-07): SILENT — 0 kandidat, 0 strong-lead baru, 0 early-lead baru, "
    "0 track-C lead/kandidat baru, 0 sellout baru, 0 age-exclusion baru, 0 slot berubah. Scan route 4: "
    "pre-flight LULUS 10,2 dtk; window 132053652-132054651 (1000 blok cap), 40 Ankr calls, 0 error chunk phase; "
    "kill incident mid-enrichment 85/129 ~01:21 WIB + recovery re-fetch penuh (40 calls, 0 error, counts identik "
    "126 ERC721/3 ERC1155/424 ERC-20) — watermark dimajukan -> 132054651; skipped gap 132051227-132053651 milik "
    "backfill (worker 132051227-132053226 selesai, 132053227-132053666 berjalan). First-seen 0, early lead 0. "
    "Re-read 548 kontrak + 54 track_c @ blok 132054853/132056860; 104/548 totalSupply None (gagal baca, bukan nol). "
    "Velocity 0 lolos. Near-sellout: Chipdroidling 683/700, Swarmganbei 692/700 (flat). HIVE flat 1255 "
    "(minted-by-user, bal 1). MoonCat 1102 -> 1106 (+4), 5 tersisa dari 1111, velocity 0,56x fail. "
    "ONLYAI Crystals LAUNCHED sesuai jadwal 01:00 WIB (0 -> 568, 18,17/mnt; verifikasi segar 782, MAX 5555) "
    "tapi free% + slot UNVERIFIED (semua free view revert, Sourcify IncompleteRead) — watchlist, bukan lead. "
    "BINANCEAI tetap refund/failed (launched 0, failed 1, isRefundPhase 1) — sudah excluded + dilaporkan sejak "
    "2026-11-02, tanpa perubahan. Grove freeOpen=0. Sourcify feed 20 kontrak, 2 baru, 0 sale-shape; "
    "transport-failed terbuka 0. Boltbook en+zh 9 alamat unik, 3 baru, 0 sale-shape. 5c scan baru: 39 ERC-20 "
    "mint_count>=10, 28 sudah dicek, 11 baru dicek (semua Sourcify not_verified), 0 sale-shape, 0 transport-failed. "
    "Bridge tidak berubah sejak 2026-11-06 09:48, 0 temuan pelengkap baru (4 re-find lama: Agent Panda, Agent Harvest "
    "Land, Botkirin, AGC ERC20 — first_seen 2026-11-03, umur >48 jam, sudah dilaporkan dulu, tidak dipromosikan). "
    "BNB Guardian tanpa perubahan (minted 1438 -> 1441, tetap gate-blocked). MINTS 141 proyek / 38 free_live, identik "
    "run 0031. Tidak ada preview/mint/claim/approve/sign/transaksi.")
snap["runNote0101_scan"] = state["runNote0101_scan"]
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved. contracts:", len(snap["contracts"]), "track_c:", len(snap.get("track_c", {})),
      "excluded:", len(snap.get("excluded", {})))
