#!/usr/bin/env python3
"""Finalize run 2026-11-07 02:01 WIB — parent merge (pattern run 0131).
Backs up snapshot + track-c-checked, merges reread (non-None only) + velocity
+ track_c reread + 5c checked (NOT-verified only; transport-failed NOT merged),
adds Jager early lead + FUGUI watchlist-only track_c entries, applies the 48h
age rule to 69 verified candidates (full entries preserved in
run-2026-11-07-0201-age-removed.json), advances scan watermark to 132064294
(scan complete, 40 calls, 0 errors). NO preview/mint/claim/sign/transaction."""
import json, shutil, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "0201"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-20261107-{RUN}")
shutil.copy(f"{HF}/track-c-scan-checked.json", f"{HF}/track-c-scan-checked.json.bak-20261107-{RUN}")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-07-{RUN}-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-07-{RUN}-velocity.json"))
fivec = json.load(open(f"{HF}/run-2026-11-07-{RUN}-5c-newscan.json"))
age = json.load(open(f"{HF}/run-2026-11-07-{RUN}-age-candidates.json"))
REREAD_BLOCK = reread["block"]  # 132064515
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

# 3. fresh parent verification: MoonCat totalSupply + Jager/FUGUI already verified
#    in run-2026-11-07-0201-verify.json (block 132068002); MoonCat here.
try:
    r = _single("https://bsc-dataseed.binance.org/", "eth_call",
                [{"to": "0x045425004b622733ced4139e930c622187ea6c73",
                  "data": "0x18160ddd"}, "latest"], 10, retries=0)
    mc = int(r, 16)
    contracts["MoonCat"][f"runNote{RUN}_fresh"] = (
        f"Verifikasi segar parent via bsc-dataseed eth_call totalSupply(): {mc} "
        f"(reread run ini 1109 @ blok {REREAD_BLOCK}, MAX 1111) — "
        f"{'SOLD OUT' if mc >= 1111 else 'masih BELUM sold out'}.")
    print("MoonCat fresh totalSupply:", mc)
except Exception as e:  # noqa: BLE001
    print("MoonCat fresh check FAILED:", e)

# 4. track_c reread merge (non-None only; inside main reread, block 132064515)
tc = snap.get("track_c", {})
tcmerged = 0; tc_none = 0
for name, rv in reread.get("track_c", {}).items():
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
    e["lastReadBlock"] = REREAD_BLOCK
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

# 6. ONLYAI / Sage / GiraffeValley / HUNT PASS run notes
onlyai = contracts.get("ONLYAI-Crystals")
if onlyai:
    onlyai[f"runNote{RUN}_onlyai"] = (
        "Run 0201: totalSupply 902 -> 1136 @ blok 132064515 (+234, ratio 0,37x vs rate sebelumnya — "
        "velocity GAGAL); MAX_SUPPLY 5555. Semua free view TETAP revert, balanceOf(user) 0 — "
        "free% + slot user tetap UNVERIFIED. BUKAN strong lead, BUKAN early lead (sudah di snapshot). "
        "Tetap watchlist-launched.")
sage = contracts.get("Sage Trials")
if sage:
    sage[f"runNote{RUN}_sage"] = (
        "Run 0201: totalSupply 14 -> 19 @ blok 132064515 (16 @ blok 132064460); MAX_SUPPLY 5000, "
        "mintOpen=1, freeClaimed(user)=0 (slot terbuka), quote(user,0)=(1 token, cost 0) — jalur gratis "
        "tetap terverifikasi; umur ~50 mnt, sisa 4981/5000. Free% unverified + tanpa website -> tetap "
        "early lead saja, BUKAN strong lead. Tidak ada promosi.")
giraffe = contracts.get("GiraffeValley")
if giraffe:
    giraffe[f"runNote{RUN}_giraffe"] = (
        "Run 0201: totalMinted tetap 5 @ blok 132064475; MAX_SUPPLY 8000, FREE_POOL 1000, freeRemaining "
        "995, gate()=registry 0x60B926… persis, freeMintCount(user)=0, quote(user,1)=0,000187 BNB (mgmtFee, "
        "bukan gas-only). Tetap early lead saja (free 0,5%, tanpa website), BUKAN strong lead. "
        "Reread batch run ini gagal total untuk kontrak ini (None, bukan nol).")
hunt = contracts.get("HUNT PASS")
if hunt:
    hunt["totalMinted"] = 479
    hunt["freePct"] = 16.0
    hunt["lastReadBlock"] = 132064515
    hunt["lastReadWib"] = f"2026-11-07 run {RUN}"
    hunt[f"runNote{RUN}_huntpass"] = (
        "Run 0201: totalMinted 373 -> 479 (retry dataseed1 setelah HTTP 403; free% 479/3000=16,0% < 25%), "
        "mintedBy(user)=0, balanceOf(user)=0, first mint 02:00:40 WIB. Tetap early lead saja "
        "(free% < 25%, tanpa website), BUKAN strong lead. Tidak ada promosi.")
    print("HUNT PASS updated: totalMinted 479, freePct 16.0")

# 7. Jager Agent Pass — EARLY LEAD, add to snapshot contracts
verify = json.load(open(f"{HF}/run-2026-11-07-{RUN}-verify.json"))
jv = verify["jager"]
contracts["Jager Agent Pass"] = {
    "address": "0x951f705feB9dCc95D58b445BE58b869724E50707",
    "name": "Jager Agent Pass",
    "symbol": "JAP",
    "kind": "ERC721",
    "status": "early-lead-2026-11-07-0201",
    "totalMinted": jv["totalMinted"],
    "MAX_SUPPLY": jv["MAX_SUPPLY"],
    "freeMinted": jv["freeMinted"],
    "balanceOf_user": jv["balanceOf_user"],
    "owner": "0x67230d320f714ac82c6ec253d238cfa309fb1b85",
    "registry_bytes_hit": True,
    "sourcify": "transport-failed (IncompleteRead 2x — ABI tidak diketahui, bukan not_verified)",
    "agent_shaped": True,
    "note": ("EARLY LEAD run 0201 (temuan kaki scan job ini, first-seen sejati). First mint terverifikasi "
             "on-chain blok 132063335, 2026-11-07 02:18:06 WIB, tx "
             "0x9cd29fe3054911bd431322ae022e4ad1f633d594a953687ff48c3d035b81459f, tokenId 4; 31 mint / 31 minter "
             "berbeda dalam window scan 132063295-132064294. totalMinted 98 @ blok 132066224 -> 164 @ blok "
             "132068002 (verifikasi segar parent), MAX 777, freeMinted 164. Jalur gratis + slot user TIDAK "
             "terverifikasi (totalSupply/FREE_SUPPLY/mintOpen/gate/quote/freeClaimed(user) semua revert; "
             "Sourcify transport-failed). Tanpa website. BUKAN strong lead, BUKAN kandidat. "
             "TIDAK pernah di-preview/mint. TokenId 0-3 lahir sebelum blok 132063295 (gap belum dipindai)."),
    "first_seen_block": 132063335,
    "first_seen_wib": "2026-11-07 02:18:06 WIB",
    "lastReadBlock": verify["block"],
    "lastReadWib": f"2026-11-07 run {RUN}",
    "velocityNote": "no-fresh-supply",
    "velocityVerified": False,
}
print("Jager added to snapshot; totalMinted now:", jv["totalMinted"])

# 8. FUGUI — 2 sale deployments, GATE-BLOCKED, watchlist-only in track_c
tc["FUGUI-set1-991"] = {
    "sale": "0x4d6bbbc3129beb54450427dc12011f178c7fb630",
    "token": "0xebcc9431cce0d00143b641ec2650a11a970a2366",
    "status": "watchlist-only-gate-blocked-2026-11-07-0201",
    "saleShape": "PASS (S1): claimFree() no-arg + freeClaimed/freeMinted + AGENT_ID_REGISTRY = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify exact_match",
    "FREE_SHARES": 4444,
    "TOTAL_SHARES": 6666,
    "TOKENS_PER_SHARE": 600000,
    "PRICE_PER_SHARE_USDT": 1,
    "freeMinted": verify["fugui_set1"]["freeMinted"],
    "totalMinted": verify["fugui_set1"]["totalMinted"],
    "paidMinted": 0,
    "finalized": False,
    "deadline_wib": "2026-11-09T21:00:00+07:00",
    "treasury": "0x44994ceb913d4f686f126cbb3f13312311925440",
    "owner": "0xa634bd88789f7670a950e703eaf0a5462f32164a",
    "tradingOpen": False,
    "userSlot": {"freeClaimed": False, "hasAgentId": True, "token_balance": 0},
    "gate": "FAILED — tanpa website resmi (Alphapedia Boltbook: 'The team is anonymous and there is no official website'; pencarian EN+ZH + MINTS nihil). BUKAN lead, BUKAN kandidat; TIDAK pernah di-preview/mint. Keputusan lanjut (informed override / record-only) di parent.",
    "ageNote": "UNVERIFIED — umur peluncuran belum terverifikasi (butuh stated launch time + first-mint corroboration); klaim pertama terlihat blok 132063137 (post 1328.ai). Watchlist-only.",
    "source": "Boltbook post 1328.ai https://boltbook.fun/p/xR78BE1k6zkU ; Alphapedia https://boltbook.fun/alphapedia/fugui",
    "risks": ("Token terkunci sampai sale finalize + deployer buka trading; free share hangus bila tidak sold out; "
              "openTrading() hanya owner token (EOA deployer); tanpa market/harga."),
    "lastReadBlock": verify["block"],
    "lastReadWib": f"2026-11-07 run {RUN}",
}
tc["FUGUI-set2"] = {
    "sale": "0xa0b30b8ff77826e2288a28d2c560ecf3476828f6",
    "token": "0x098efa9227ee4cbb4f9c25da812d6d61a0310230",
    "status": "watchlist-only-gate-blocked-2026-11-07-0201",
    "saleShape": "PASS (S1): claimFree() no-arg + freeClaimed/freeMinted + AGENT_ID_REGISTRY = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify exact_match",
    "FREE_SHARES": 4444,
    "TOTAL_SHARES": 6666,
    "TOKENS_PER_SHARE": 600000,
    "PRICE_PER_SHARE_USDT": 1,
    "freeMinted": verify["fugui_set2"]["freeMinted"],
    "totalMinted": verify["fugui_set2"]["totalMinted"],
    "paidMinted": 5,
    "finalized": False,
    "deadline_wib": "2026-11-08T14:55:00+07:00",
    "treasury": "0x44994ceb913d4f686f126cbb3f13312311925440",
    "owner": "0xa634bd88789f7670a950e703eaf0a5462f32164a",
    "tradingOpen": False,
    "userSlot": {"freeClaimed": False, "hasAgentId": True, "token_balance": 0},
    "gate": "FAILED — tanpa website resmi (Alphapedia Boltbook: 'The team is anonymous and there is no official website'; pencarian EN+ZH + MINTS nihil). BUKAN lead, BUKAN kandidat; TIDAK pernah di-preview/mint. Keputusan lanjut (informed override / record-only) di parent.",
    "ageNote": "UNVERIFIED — umur peluncuran belum terverifikasi (butuh stated launch time + first-mint corroboration). Watchlist-only.",
    "source": "Boltbook post 1328.ai https://boltbook.fun/p/xR78BE1k6zkU ; Alphapedia https://boltbook.fun/alphapedia/fugui",
    "risks": ("Token terkunci sampai sale finalize + deployer buka trading; free share hangus bila tidak sold out; "
              "openTrading() hanya owner token (EOA deployer); tanpa market/harga."),
    "lastReadBlock": verify["block"],
    "lastReadWib": f"2026-11-07 run {RUN}",
}
print("FUGUI set1/set2 added to track_c as watchlist-only gate-blocked; freeMinted:",
      verify["fugui_set1"]["freeMinted"], "/", verify["fugui_set2"]["freeMinted"])

# 9. AGE RULE — delete 69 verified >48h, not-sold-out, live-status entries.
#    Verification re-done here against the FRESH snapshot + velocity soldOut set
#    + min first-seen across case variants of the seen file.
sold_out_names = {r.get("name") for r in vel.get("soldOut", [])}
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
seen_contracts = seen.get("contracts", {})

def min_first_seen(addr):
    vals = []
    for k, v in seen_contracts.items():
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
print("removed entries preserved in run-2026-11-07-0201-age-removed.json")

# 10. scan state — advance watermark (scan complete, 40 calls, 0 errors)
state = json.load(open(f"{HF}/onchain-scan-state.json"))
state["last_scanned_block"] = 132064294
state["last_scan_window_from"] = 132063295
state["last_scan_window_to"] = 132064294
state["last_scan_wib"] = "2026-11-07 run 0201"
state["ankr_calls"] = 40
state["errors"] = []
state["nft_contracts"] = 110
state["erc20_mint_contracts"] = 226
state["skipped_gap"] = ("132059847-132063294 (3448 blok; window dari watermark 132059846 ke head "
                        "132064294 = 4448 blok > cap 1000; main scan menutup 1000 blok terbaru "
                        "132063295-132064294; backfill sudah menutup 132059847-132063185; sisa "
                        "132063186-132063294 (109 blok) belum dipindai main scan, milik backfill)")
state["runNote0201_scan"] = (
    "Scan 0201: pre-flight LULUS 6,4 dtk (head 132064256, 91 log/50 blok; ankr eth_blockNumber "
    "langsung gagal parse, fallback fast_rpc race); window 132063295-132064294 (1000 blok cap), "
    "20 chunk, 40 Ankr calls, 0 errors, partial false; 107 ERC721 + 3 ERC1155 (529 mint) + 226 ERC-20. "
    "1 first-seen sejati (Jager Agent Pass, EARLY lead). Watermark -> 132064294; skipped gap "
    "132059847-132063294 (3448 blok) milik backfill (132059847-132063185 sudah ditutup backfill).")
json.dump(state, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan state: watermark -> 132064294")

# 11. seen — add Jager only; update _meta
seen_meta = seen.setdefault("_meta", {})
seen_contracts["0x951f705feB9dCc95D58b445BE58b869724E50707"] = 132063335
seen_meta["last_scan_wib"] = "2026-11-07 run 0201"
seen_meta["last_scan_window"] = "132063295-132064294"
seen_meta["last_scan_added"] = 1
seen_meta["note_0201_1107"] = ("Run 0201: 1 first-seen sejati (Jager Agent Pass 0x951f…0707, "
                               "first mint blok 132063335) ditambahkan; total seen 9994 keys "
                               "(+1). Catatan: seen file mengandung 1488 kunci duplikat beda casing "
                               "(9993 kunci, 8505 unik case-insensitive) — belum dibersihkan run ini.")
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)
print("seen updated; Jager added; total keys now:", len(seen_contracts))

# 12. snapshot run notes
snap["timestamp_wib"] = "2026-11-07T03:00:00+07:00"
snap["last_run_wib"] = "2026-11-07 02:01 WIB"
snap["runNote0201_1107"] = (
    "Run 0201 (jadwal 02:01 WIB 2026-11-07): 1 EARLY LEAD baru (Jager Agent Pass, temuan kaki scan job "
    "ini) + 1 temuan sale-shape GATE-BLOCKED (FUGUI 2 set, watchlist-only di track_c); 0 kandidat, "
    "0 strong-lead baru, 0 track-C lead/kandidat baru yang lolos gate, 0 sellout baru, 0 slot berubah, "
    "0 auto-mint/claim. Scan route 4: pre-flight LULUS 6,4 dtk (head 132064256, 91 log/50 blok); window "
    "132063295-132064294 (1000 blok cap), 20 chunk, 40 Ankr calls, 0 error, partial false (107 ERC721 + "
    "3 ERC1155, 529 mint + 226 ERC-20) — watermark dimajukan -> 132064294; skipped gap 132059847-132063294 "
    "(3448 blok) milik backfill. First-seen 1 (Jager). Re-read 550 kontrak + 54 track_c @ blok 132064515; "
    "105/550 totalSupply None (gagal baca, bukan nol; baru: GiraffeValley). Velocity 0 lolos (interval "
    "~34,49 mnt vs run 0131). Sellout tetap 33, set identik run 0131. Near-sellout: Chipdroidling 683/700, "
    "Swarmganbei 692/700 (flat) — keduanya ikut terhapus aturan umur 48 jam run ini (lihat age-removed). "
    "HIVE flat 1255 (minted-by-user, bal 1). MoonCat 1108 -> 1109 (+2), 2 tersisa dari 1111, velocity 0,13x "
    "fail. ONLYAI 902 -> 1136 (ratio 0,37x, velocity fail); free% + slot tetap UNVERIFIED — watchlist, "
    "bukan lead. Sage Trials 14 -> 19 (slot gratis terbuka, tanpa website) tetap early lead. GiraffeValley "
    "tetap totalMinted 5 (free 0,5%, quote 0,000187 BNB mgmtFee) tetap early lead. HUNT PASS 373 -> 479 "
    "(free% 16,0% < 25%) tetap early lead. Crack 3065 -> 3072 (track_c). BINANCEAI tetap refund/failed "
    "(launched 0, failed 1, isRefundPhase 1) — sudah excluded + dilaporkan sejak 2026-11-02, tanpa "
    "perubahan. Grove freeOpen=0. Age rule: 69 entri live-status terverifikasi >48 jam (first-seen block "
    "sebagai batas bawah umur, ambang blok 131683000) DIHAPUS dari snapshot; entri lengkap tersimpan di "
    "run-2026-11-07-0201-age-removed.json (termasuk Unnamed-E6BA-1401 yang statusnya masih "
    "'chat-report-pending-parent-decision' — keputusan parent tetap terbuka lewat laporan run ini). "
    "Sourcify feed 20 kontrak, 1 baru, 0 sale-shape; transport-failed terbuka 0. Boltbook en+zh 15 alamat "
    "unik, 8 baru, 1 sale-shape (FUGUI set 2; set 1 dari sumber yang sama). 5c scan baru: 22 ERC-20 "
    "mint_count>=10, 15 sudah dicek, 7 baru dicek (semua not_verified, di-merge; 0 transport-failed), "
    "0 sale-shape. Bridge tidak berubah sejak 2026-11-06 09:48, 0 temuan pelengkap baru (7 re-find lama di "
    "jendela scan: Hackagent, Dronegent, Spookagent, Chromagent, Saturnode, Yydsgent, PIXEL BOYZ — tidak "
    "dipromosikan). BNB Guardian tanpa perubahan (minted 1443 -> 1444, tetap gate-blocked). AGENT MAO tetap "
    "paused (farming.ai curl rc 52). MINTS 141 proyek / 38 free_live, identik run 0131 (hanya drift minted: "
    "Tacotron 5.870 -> 5.909, Worldygg 19.722 -> 19.723). Odaily/PANews 0 pengumuman Agent ID; DappBay AI "
    "hanya 'Guardians of the Car'. Tidak ada preview/mint/claim/approve/sign/transaksi.")
snap["runNote0201_scan"] = state["runNote0201_scan"]
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved. contracts:", len(snap["contracts"]), "track_c:", len(snap.get("track_c", {})),
      "excluded:", len(snap.get("excluded", {})))
