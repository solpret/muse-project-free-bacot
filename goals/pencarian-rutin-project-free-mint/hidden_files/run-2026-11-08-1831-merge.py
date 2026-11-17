#!/usr/bin/env python3
"""Merge run 2026-11-08 18:31 WIB into onchain-snapshot.json + seen + scan state.
Route-1 reread updates, BRAINROT ZOO same-owner discard entry, Beast16 upcoming
entry, scan triage (newly-seen classification), NUSA track_c update.
Read-only except for the state files it owns. Never touches bridge file."""
import json, sys, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
RUN_WIB = "2026-11-08 18:31 WIB"

def load(p):
    with open(p) as f: return json.load(f)
def save(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w") as f: json.dump(obj, f, indent=1)
    import os; os.replace(tmp, p)

snap = load(BASE + "/onchain-snapshot.json")
rr = load(BASE + "/run-2026-11-08-1831-reread.json")
scan = load(BASE + "/onchain-scan-2026-11-08-1831.json")
seen = load(BASE + "/onchain-scan-seen.json")
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

# ---- Route 1: reread updates + velocity (convention run 1801: base = currentRatePerMin, interval block-based) ----
changed, degraded, vel_pass, vel_note = [], 0, [], []
PREV_BLOCK = 132381403  # run 1801 read block
INTERVAL_MIN = (rr.get("block", 132385176) - PREV_BLOCK) * 0.45 / 60.0
for name, d in rr.get("reread", {}).items():
    old = contracts.get(name)
    if old is None:
        continue
    nts = d.get("totalSupply")
    if nts is None:
        degraded += 1
        continue
    ots = old.get("totalSupply")
    if ots is None:
        old["totalSupply"] = nts
        old["lastReadBlock"] = rr.get("block")
        old["lastReadWib"] = RUN_WIB
        continue
    if nts != ots:
        minted = nts - ots
        old_rate = old.get("currentRatePerMin")
        base = old_rate if old_rate is not None else old.get("previousRatePerMin")
        rate = minted / INTERVAL_MIN if INTERVAL_MIN else 0.0
        ratio = (rate / base) if base else None
        passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        old["previousTotalSupply"] = ots
        old["totalSupply"] = nts
        old["mintedInInterval"] = minted
        old["intervalMinutes"] = round(INTERVAL_MIN, 1)
        if old_rate is not None:
            old["previousRatePerMin"] = old_rate
        old["currentRatePerMin"] = round(rate, 4)
        old["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        old["velocityLegPasses"] = passes
        old["lastReadBlock"] = rr.get("block")
        old["lastReadWib"] = RUN_WIB
        if d.get("freeClaimed") is not None:
            old["freeClaimed"] = d["freeClaimed"]
        if d.get("balanceOf_user") is not None:
            old["balanceOf_user"] = d["balanceOf_user"]
        changed.append((name, ots, nts, minted, passes, old.get("status")))
        if passes:
            vel_pass.append((name, minted, round(ratio, 2)))
    else:
        old["lastReadBlock"] = rr.get("block")
        old["lastReadWib"] = RUN_WIB
        old["mintedInInterval"] = 0
        old["currentRatePerMin"] = 0.0
        old["velocityLegPasses"] = False
        if d.get("freeClaimed") is not None:
            old["freeClaimed"] = d["freeClaimed"]
        if d.get("balanceOf_user") is not None:
            old["balanceOf_user"] = d["balanceOf_user"]

# ---- Track C reread: NUSA freeMinted ----
for name, d in rr.get("track_c", {}).items():
    old = track_c.get(name)
    if isinstance(old, dict) and d.get("freeMinted") is not None:
        if old.get("freeMinted") != d["freeMinted"]:
            old["freeMinted"] = d["freeMinted"]
            old["lastReadWib"] = RUN_WIB
            old["lastReadBlock"] = rr.get("block")

# ---- BRAINROT ZOO: same-owner discard entry ----
def block_time_wib(blk):
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(blk), False]}, timeout=10, retries=0)
            if r and r.get("result"):
                ts = int(r["result"]["timestamp"], 16)
                return datetime.datetime.fromtimestamp(
                    ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception:
            continue
    return None

first_mint_wib = block_time_wib(132198224)
contracts["BRAINROT ZOO"] = {
    "address": "0x3c7d328027ca0068e7cd8709d64d9161bc35de93",
    "status": "promotion-discarded-same-owner-2026-11-08",
    "name": "BRAINROT ZOO", "symbol": "ROT", "kind": "ERC721",
    "totalSupply": 544, "MAX_SUPPLY": 1667, "mintOpen": 1,
    "priceWei": 200000000000000,
    "firstSeenBlock": 132198224, "firstMintWib": first_mint_wib,
    "firstMintTx": "0x55c58d8fc5512c50982443f860ca18ab58961045d984b74b613238bab2f95948",
    "lastReadBlock": 132385462, "lastReadWib": RUN_WIB,
    "owner": "0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd",
    "registryBytesInCode": True,
    "sourcify": "not_verified",
    "website": "https://brainrot-zoo.pages.dev/",
    "websiteGate": "PASS (footer situs mencetak kontrak persis + tautan BscScan; dicapai via tokenURI(1))",
    "xVerified": False,
    "freePctVerified": None,
    "freePctNote": "UNVERIFIED: freeClaimed/freeMinted/FREE_SUPPLY/freeLeft semua revert; totalSupply 544/1667 = 32,6% dari MAX bukan ukuran kuota gratis.",
    "userBalance": 0,
    "discardNote": "DISCARDED run 1831 aturan same-owner: owner() 0x11038f4a... SAMA dengan gelombang 10 kontrak yang dibuang 2026-11-06 01:40 WIB (Toucan Play, jelly.exe, Los Flamingos, Moonhowlers, Counting Sheep, Tusk & Trunk, getpuffr, Hippo Social Club, LLAMA DRAMA, Danger Noodles; pola sama: mint pertama gratis, price()=0.0002 BNB utk mint ke-2+). Sudah dikenal scan-seen sejak 2026-11-07 20:20 WIB (first_seen block 132198224) dan sudah ditriase BUKAN lead oleh run sebelumnya (pace lambat +27/~9.000 blok, free% post-implied 23,6% <25%). TIDAK dilaporkan sebagai lead, TIDAK dipromosikan, TIDAK di-preview/di-mint.",
    "baselineNote": "Boltbook EN/ZH front-page run 1831 (post BRAINROT ZOO 537/1.667, mint(1) 0 BNB terverifikasi poster). Verifikasi run ini: totalSupply 544, MAX 1667, mintOpen 1, price 0.0002 BNB, tokenURI(1) https://brainrot-zoo.pages.dev/meta/1.json, registry-bytes hit, Sourcify tidak terverifikasi, umur terverifikasi ~23 jam (first mint blok 132198224).",
}

# ---- Beast16: upcoming (not launched) ----
contracts["Beast16"] = {
    "address": "0xaCeF3B62B958ED7F49dFc73885609b4d270B9bD0",
    "status": "upcoming-prelaunch-2026-11-08",
    "name": "Beast16", "symbol": "BEAST16", "kind": "ERC721",
    "totalMinted": 0, "MAX_SUPPLY": 4444, "mintOpen": 0,
    "freeViews": ["freeUsed"],
    "agentIdView": "AGENT_ID()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis",
    "registryBytesInCode": True,
    "owner": "0xd1c14248730bd7cccdf9be9ae47ee272109e53cf",
    "ownerInDiscards": False,
    "sourcifyVerifiedAt": "2026-11-08T11:23:45Z",
    "lastReadWib": RUN_WIB,
    "baselineNote": "Sourcify feed run 1831 (verifiedAt 11:23:45Z): shape S1-like (mint + quote + freeUsed + registry). BELUM LAUNCH (totalMinted 0, mintOpen 0) -> upcoming watchlist-only, BUKAN kandidat/lead, TIDAK di-preview/di-mint. Dipantau scan/hot-leg untuk first mint.",
}

# ---- Scan triage: newly-seen classification ----
seen_contracts = seen.setdefault("contracts", {})
snap_addrs = {(v.get("address") or "").lower() for v in contracts.values() if isinstance(v, dict)}
new_seen, agent_shaped_new, historic = [], [], 0
for c in scan.get("contracts", []):
    addr = (c.get("address") or "").lower()
    if not addr:
        continue
    if addr in seen_contracts or addr in snap_addrs:
        historic += 1
        continue
    new_seen.append(c)
    seen_contracts[addr] = {"first_seen_block": c.get("first_block"),
                            "first_seen_run": "2026-11-08-1831",
                            "mint_count_window": c.get("mint_count"),
                            "distinct_minters_window": c.get("distinct_minters")}
    if c.get("registry_bytes_hit"):
        agent_shaped_new.append(c)
save(BASE + "/onchain-scan-seen.json", seen)

# ---- Scan state / watermark (PARTIAL scan: do NOT advance watermark; next run retries window) ----
state = load(BASE + "/onchain-scan-state.json")
state["last_scan_partial"] = True
state["last_scan_partial_note"] = ("Scan run 1831 PARTIAL: chunk phase 20/20 OK (0 errors, 40 Ankr calls) but "
    "enrichment process died at 88/147 contracts (no completion, last log enrich 88/147); "
    "59 contracts unenriched/unexamined; watermark NOT advanced so run berikut retry window yang sama.")
state["last_scan_window_from"] = scan.get("from_block")
state["last_scan_window_to"] = scan.get("to_block")
state["last_scan_wib"] = "2026-11-08 18:31-18:5x WIB"
state["last_scan_gap_skipped"] = "132381479-132385056 (3578 blocks; window from watermark to head 4579 blocks > cap 1000; scan covered most recent 1000 only; backfill OFF)"
state["last_scan_ankr_calls"] = scan.get("ankr_calls")
state["last_scan_errors"] = len(scan.get("errors", []))
state["last_scan_nft"] = len(scan.get("contracts", []))
state["last_scan_erc20_mint"] = scan.get("erc20_mint_contracts")
save(BASE + "/onchain-scan-state.json", state)

# ---- 5c checked update ----
five_c = load(BASE + "/run-2026-11-08-1831-5c.json")
checked = load(BASE + "/track-c-scan-checked.json")
checked_list = checked.get("checked", []) if isinstance(checked, dict) else checked
checked_lower = {str(x).lower() for x in checked_list}
added5c = 0
for a in five_c.keys():
    if a.lower() not in checked_lower:
        checked_list.append(a)
        checked_lower.add(a.lower())
        added5c += 1
if isinstance(checked, dict):
    checked["checked"] = checked_list
    save(BASE + "/track-c-scan-checked.json", checked)
else:
    save(BASE + "/track-c-scan-checked.json", checked_list)

# ---- Run notes ----
snap["last_run_wib"] = RUN_WIB
snap["last_run"] = "free-mint-search 2026-11-08 1831 WIB"
snap["runNote1831_1108"] = (
    "Run 1831 (18:31 WIB): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 pending claim baru, "
    "0 lead track-C baru - DIAM per aturan. ROUTE 1 re-read blok 132385176: 533 kontrak + 71 track_c; "
    f"perubahan supply {len(changed)}, degraded(None) {degraded}; velocity LOLOS {len(vel_pass)} "
    f"({', '.join('%s +%d %.2fx' % v for v in vel_pass)}) - tanpa promosi (UNKNOWN-1Aeb free%/umur UNVERIFIED; "
    "Ink Koi 0xbd4B slot user terpakai; ACOS-3aed free%/umur/website UNVERIFIED; MONOLITH rate pertama = baseline, "
    "bukan rasio). NUSA track-C freeMinted 40->80 (14,3% <25%, gate gagal, tanpa perubahan). "
    "BRAINROT ZOO (Boltbook lead): DISCARDED same-owner (owner 0x1103... = gelombang 10 kontrak 2026-11-06; "
    "website gate LOLOS via footer situs, umur ~23 jam terverifikasi) - TIDAK dilaporkan sebagai lead. "
    "Beast16 (Sourcify feed): upcoming, mintOpen 0, totalMinted 0 - watchlist-only. "
    "GDOG Synth (feed): BUKAN agent-shaped (tanpa registry bytes, AGENT_ID revert) - tidak masuk snapshot. "
    "Chipmunks 0xB262... (Boltbook): BUKAN agent-shaped per bytecode (tanpa registry bytes, AGENT_ID revert), "
    "free% 853/6666=12,8%, sudah seen (blok 132355605) - tanpa tindakan. "
    "PANDORA 0xdb8a...: Boltbook mengonfirmasi TANPA gate Agent ID (mint(1)@0 lolos dari plain wallet) - tetap watchlist-only, tidak pernah promosi. "
    "Sweep rute 3: 0 proyek baru (AgentForge/Pixel Fox/PocketDragons/Subsonic Tribe/BNBmeme/Black Hole semua dari post 24-28 Okt, umur >48 jam = age-excluded). "
    "Komplemen rute 6: Binance Square = hasil sweep EN; Odaily 0; PANews 0. "
    "Bridge: 7 kontrak tidak di snapshot = 6 ERC20 (ORE, ETHBack, Ikigai, AGC, PANBA, unnamed) + 1 same-owner-discarded (Krillfarm) - dilewati, bukan lead. "
    "Binanceai tetap refund phase (failed=1, isRefundPhase=1, launched=0, totalShares 3110, tokenClaimed user 0, saldo 0) - tanpa perubahan."
)
snap["runNote1831_1108_scan"] = (
    "Scan run 1831 PARTIAL: pre-flight LULUS 11,7 dtk (50 blok, 311 log, head 132386037); window 132385057-132386056 "
    f"(1000 blok, cap), {scan.get('ankr_calls')} Ankr calls, {len(scan.get('errors', []))} error, partial={scan.get('partial')}; "
    f"chunk phase 20/20 selesai; enrichment MATI di 88/147 kontrak (proses hilang, tanpa completion) - 59 kontrak tidak terperiksa; "
    f"{len(scan.get('contracts', []))} NFT ter-enrich / {scan.get('erc20_mint_contracts')} ERC20-mint (daftar ERC20 lengkap); "
    f"first-seen baru {len(new_seen)} (agent-shaped {len(agent_shaped_new)}), historic/known {historic}; "
    "watermark TIDAK dimajukan (tetap 132381478) - run berikut retry window yang sama; "
    "skipped gap 132381479-132385056 (3.578 blok, backfill OFF). "
    f"5c: 9 ERC20 baru dicek (dari 48 mint_count>=10; 39 sudah dicek), 0 hit S1/S2; track-c-scan-checked +{added5c}."
)
save(BASE + "/onchain-snapshot.json", snap)

print("ROUTE1 changed=%d degraded=%d vel_pass=%s" % (len(changed), degraded, vel_pass))
print("SCAN contracts=%d erc20=%d new_seen=%d agent_shaped_new=%d historic=%d" % (
    len(scan.get("contracts", [])), scan.get("erc20_mint_contracts"), len(new_seen), len(agent_shaped_new), historic))
for c in agent_shaped_new:
    print("AGENT-SHAPED-NEW:", c.get("address"), c.get("name"), "mint_count", c.get("mint_count"),
          "minters", c.get("distinct_minters"), "first_block", c.get("first_block"))
for c in new_seen:
    print("NEW-SEEN:", c.get("address"), c.get("name"), c.get("symbol"), "mint", c.get("mint_count"),
          "registry", c.get("registry_bytes_hit"), "free", c.get("free_functions"), "mint_fns", c.get("mint_functions"))
print("MERGE DONE")
