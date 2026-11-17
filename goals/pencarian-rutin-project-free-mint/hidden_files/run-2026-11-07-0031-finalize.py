import json
HF = "."
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-07-0031-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-07-0031-velocity.json"))
fivec = json.load(open(f"{HF}/run-2026-11-07-0031-5c-newscan.json"))
REREAD_BLOCK = reread["block"]  # 132050686
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
    if not any_val: none_only += 1
    e["lastReadBlock"] = REREAD_BLOCK
    e["lastReadWib"] = "2026-11-07 run 0031"
    merged += 1
print("merged reread contracts:", merged, "| all-None:", none_only)

# 2. velocity merge
vmerged = 0
for row in vel.get("rows", []):
    name = row.get("name")
    if name not in contracts: continue
    e = contracts[name]
    for k in ("mintedInInterval","intervalMinutes","currentRatePerMin","previousRatePerMin"):
        if row.get(k) is not None: e[k] = row[k]
    if row.get("velocityNote"): e["velocityNote"] = row["velocityNote"]
    if row.get("velocityPasses") is not None: e["velocityVerified"] = bool(row["velocityPasses"])
    vmerged += 1
for p in vel.get("passes", []):
    name = p["name"]
    if name in contracts:
        contracts[name]["runNote0031_velocity"] = (
            f"Run 0031: velocity LOLOS (+{p['mintedInInterval']}, {p['ratePerMin']}/mnt vs prev "
            f"{p['prevRatePerMin']} = {p['ratioVsPrev']}x) TAPI TIDAK promosi: "
            f"free% {p.get('freePct')} + status {contracts[name].get('status')} (14 minted-by-user, "
            f"Gourdwick discarded-same-owner, Pulsekeep early-lead-reported free% UNVERIFIED).")
print("velocity rows merged:", vmerged, "| passes noted:", len(vel.get("passes", [])))
# near-sellout note
for ns in vel.get("nearSellout", []):
    if ns["name"] in contracts:
        contracts[ns["name"]]["runNote0031_nearSellout"] = (
            f"Run 0031: nyaris sold out {ns['curSupply']}/{ns['maxSupply']} "
            f"(sisa {ns['remaining']}), umur UNVERIFIED, tetap watchlist.")
# 3. fresh parent verification: MoonCat 1106 via dataseed ~00:59 WIB (reread 1102 @ blok 132050686)
contracts["MoonCat"]["runNote0031_fresh"] = (
    "Verifikasi segar parent ~00:59 WIB via bsc-dataseed eth_call totalSupply(): 1106 "
    "(reread run ini 1102 @ blok 132050686) — konsisten, masih BELUM sold out (MAX 1111).")
# 4. track_c reread merge (non-None only)
tc = snap.get("track_c", {})
tcmerged = 0
for name, rv in reread.get("track_c", {}).items():
    if name not in tc or not isinstance(rv, dict): continue
    e = tc[name]
    for k, v in rv.items():
        if k == "address": continue
        if v is not None: e[k] = v
    tcmerged += 1
print("track_c merged:", tcmerged)
# 5. 5c checked merge (6 new addresses, 0 hits)
chk = json.load(open(f"{HF}/track-c-scan-checked.json"))
added = 0
for c in fivec["checked"]:
    a = c["address"]
    if a not in chk and a.lower() not in {k.lower() for k in chk if isinstance(k, str) and k.startswith("0x")}:
        chk[a] = {"source": "run-2026-11-07-0031-5c-newscan", "status": "checked-not-sale-shape",
                  "note": f"mint_count window {c['mint_count']}; verified={c.get('verified')}; sale_shape={c['sale_shape']}"}
        added += 1
json.dump(chk, open(f"{HF}/track-c-scan-checked.json","w"), indent=1)
print("5c checked added:", added, "| total now:", len(chk))
# 6. snapshot run note
snap["last_run_wib"] = "2026-11-07 00:31 WIB"
snap["runNote0031_1107"] = (
    "Run 0031 (jadwal 00:31 WIB 2026-11-07): SILENT — 0 kandidat, 0 strong-lead baru, 0 early-lead baru, "
    "0 track-C lead/kandidat baru, 0 sellout baru, 0 age-exclusion baru, 0 slot berubah. "
    "Scan route 4 SUKSES pertama sejak run 0431 (pre-flight lulus 7,7 dtk; window 132049244-132050243, 1000 blok cap, "
    "40 panggilan Ankr, 0 error, ~13,5 mnt; 133 NFT + 327 ERC-20; watermark -> 132050243; seen +162 = 9986; "
    "gap dilewati 132047023-132049243 = 2221 blok milik backfill). First-seen 6, 0 early lead (2 benar-benar baru: "
    "MOLT 0x8EcaFBA8Bf911698C13D5f14D7b7241f4F80BE5B + First-Dollar Grove 0x56466afBcC2FDB847ed2cf5Bf78Ec1B213253611, "
    "keduanya Sourcify unverified, bukan agent-shaped). Re-read 548 kontrak + 54 track_c @ blok 132050686; "
    "105/548 totalSupply None (RPC terdegradasi, gagal baca bukan nol). Velocity 16 lolos, 0 promosi "
    "(14 minted-by-user, Gourdwick discarded, Pulsekeep free% UNVERIFIED). Near-sellout: Chipdroidling 683/700, "
    "Swarmganbei 692/700. BINANCEAI tetap refund/failed (launched 0, failed 1, isRefundPhase 1) — sudah excluded + "
    "dilaporkan sejak 2026-11-02, tanpa perubahan. Grove freeOpen=0. Sourcify feed 20 kontrak, 3 baru, 0 sale-shape; "
    "4 transport-failed run 2331 terselesaikan (0x48b9…, 0x5DB6…, 0xf955…, 0xAE6b…) sebagai not-sale-shape; open transport-failed 0. "
    "Boltbook en+zh 15 alamat, 9 baru, 0 sale-shape. 5c: scan lama 19/19 sudah dicek; scan baru 0031: 6 baru dicek, 0 lolos "
    "(5 unverified, 1 verified 2026-05-26 bukan sale-shape). Bridge tidak berubah, 0 temuan pelengkap. "
    "BNB Guardian tanpa perubahan (tetap gate-blocked). Temuan berbayar saja (log only): BNAGENT + Kernel Agents. "
    "Tidak ada preview/mint/claim/approve/sign/transaksi.")
snap["runNote0031_scan"] = (
    "Scan 0031 SUKSES: window 132049244-132050243 (1000 blok), partial=false, 40 Ankr calls, 0 errors, "
    "133 NFT + 327 ERC-20-mint; skipped gap 132047023-132049243 (2221 blok) untuk backfill; watermark 132050243.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot saved. contracts:", len(snap["contracts"]), "track_c:", len(snap.get("track_c",{})),
      "excluded:", len(snap.get("excluded",{})))
