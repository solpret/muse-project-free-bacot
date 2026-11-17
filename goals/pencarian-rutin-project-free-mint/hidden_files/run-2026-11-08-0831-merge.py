#!/usr/bin/env python3
"""Merge run 0831 (2026-11-08) results into snapshot / seen / scan-state / tc-checked.
Preserves all existing snapshot keys. Run once."""
import json, copy, datetime

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = datetime.timezone(datetime.timedelta(hours=7))
NOW = datetime.datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
rr = json.load(open(f"{HF}/run-2026-11-08-0831-reread.json"))
vv = json.load(open(f"{HF}/run-2026-11-08-0831-velocity.json"))
scan = json.load(open(f"{HF}/onchain-scan-2026-11-08-0831.json"))
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
state = json.load(open(f"{HF}/onchain-scan-state.json"))
tc = json.load(open(f"{HF}/track-c-scan-checked.json"))
f5 = json.load(open(f"{HF}/run-2026-11-08-0831-5c.json"))

REREAD_BLOCK = rr["block"]  # 132307042
contracts = snap["contracts"]

# ---- 1. reread + velocity update for existing entries ----
vel_by_addr = {}
for row in vv.get("rows", []):
    a = (row.get("address") or "").lower()
    if a:
        vel_by_addr[a] = row

updated = 0
for key, entry in contracts.items():
    row = rr["reread"].get(key)
    if row:
        if row.get("totalSupply") is not None:
            entry["totalSupply"] = row["totalSupply"]
        for f in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
                  "MAX_SUPPLY", "mintOpen", "freeClaimed_user", "balanceOf_user"):
            if row.get(f) is not None:
                entry[f] = row[f]
        entry["lastReadBlock"] = REREAD_BLOCK
        entry["lastReadWib"] = "2026-11-08 run 0831"
        updated += 1
    vrow = vel_by_addr.get((entry.get("address") or "").lower())
    if vrow:
        cur = vrow.get("curSupply")
        if cur is not None:
            entry["previousTotalSupply"] = vrow.get("prevSupply")
            entry["currentRatePerMin"] = vrow.get("ratePerMin")
            entry["previousRatePerMin"] = vrow.get("prevRatePerMin")
            entry["velocityRatio"] = vrow.get("ratioVsPrev")
            entry["run0831_velocity"] = (
                f"Run 0831 (blok {REREAD_BLOCK}, interval {vrow.get('intervalMin')} mnt): "
                f"{vrow.get('prevSupply')}->{cur} (+{vrow.get('mintedInInterval')}, "
                f"{vrow.get('ratePerMin')}/mnt vs prev {vrow.get('prevRatePerMin')} = "
                f"{vrow.get('ratioVsPrev')}x) -> velocity "
                f"{'LOLOS' if vrow.get('passes') else 'GAGAL'}."
            )
        else:
            entry["run0831_velocity"] = (
                f"Run 0831 (blok {REREAD_BLOCK}): no fresh supply read "
                f"(degradasi RPC) - nilai lama dipertahankan, BUKAN perubahan state."
            )
print("reread-updated entries:", updated)

# ---- 2. specific updates ----
def set_note(entry, field, text):
    entry[field] = text

# Ink Koi: fresh totals, slot used
ink = contracts.get("0xbd4B4e7189ae9356514664146b0eD683601200A9")
if ink:
    ink["totalSupply"] = 1416
    ink["freeMinted"] = 1409
    ink["freePctVerified"] = 50.74
    ink["freeClaimed_user"] = 1
    ink["balanceOf_user"] = 1
    ink["runNote0831"] = ("Run 0831 (blok 132307042): totalSupply 1.416/5.555, FREE_SUPPLY 2.777, "
        "freeMinted 1.409 = 50,74%, freeClaimed(user)=1 + balanceOf(user)=1 -> slot TERPAKAI. "
        "Tidak ada promosi. Status tetap early-lead-backfill-2026-11-07.")
    ink["userSlotNote"] = ("Slot TERPAKAI: freeClaimed(user)=1, balanceOf(user)=1 (run 0831).")

# PixelSentinels (PXSNT)
px = contracts.get("0x4e4e43f84E2E80716d03153F3c675e8E715Fa698")
if px:
    px["totalSupply"] = 3675
    px["runNote0831"] = ("Run 0831: totalSupply 3.675/10.000, PRICE 0.0005 BNB, no free views. "
        "Velocity LOLOS run ini (+23, ratio 9,61) tapi free% + umur unverified -> TIDAK promosi. "
        "Status tetap watchlist-only-age-unverified-2026-11-08.")

# DinoAgent: free pool SOLD OUT + gate now passes
dino = contracts.get("DinoAgent")
if dino:
    dino["status"] = "sold-out-free-2026-11-08"
    dino["totalMinted"] = 777
    dino["freeMinted"] = 777
    dino["freeLeft"] = 0
    dino["freePctVerified"] = 100.0
    dino["runNote0831"] = ("Run 0831: GATE KINI LOLOS - situs https://dinoagent-dinos3.vercel.app/ skill.md "
        "kini mencetak kontrak NFT eksak 0xcE19D6A5FF15e088D4bf23614242927139084895 (+ $DINO "
        "0xbcc088f12a11e8b7bf07b6bcd8c7f522552b9d0b, Paid 0xd771631859F0fb8820c288A97141599CDB3bDB0D, "
        "Burn 0xf9fac80c74d1906cda6eef4e82779681d55e2a49, Deploy 0xe9d22f9aa1ceed72c03fbde027c87e268bb1276f). "
        "TAPI free pool HABIS: totalMinted 777, freeMinted 777, freeLeft 0 (blok 132309056, ~09:03 WIB). "
        "Tidak ada mint. $DINO meluncur 3 hari sesudah sellout; burn-to-claim sesudahnya. "
        "Status diubah strong-lead-2026-11-07-gate-blocked -> sold-out-free-2026-11-08.")
    dino["gateNote"] = ("GATE LOLOS run 0831 (sebelumnya GAGAL run 1831 2026-11-07 karena situs belum mencetak "
        "kontrak): https://dinoagent-dinos3.vercel.app/ skill.md mencetak kontrak NFT eksak + token $DINO, "
        "Paid, Burn, Deploy. Free pool habis di run yang sama -> tidak dieksekusi.")

# HokiKoi: minted-by-user already; refresh lastRead
hk = contracts.get("HokiKoi")
if hk:
    hk["runNote0831"] = ("Run 0831: sudah minted-by-user 2026-11-08 (#64, tx "
        "0x862279c5368209e4f369ae37bb722aae3ed6378ab890021b6fa67fae2b0611a2, blok 132305321). "
        "Tidak ada pembacaan supply segar run ini (degradasi RPC, nilai lama dipertahankan).")

# NULLRAID: free phase sold out
for k, e in contracts.items():
    if (e.get("address") or "").lower() == "0x0000000000000000000000000000000000000000":
        pass
    if k.lower().startswith("nullraid") or (e.get("name") or "").lower() == "nullraid":
        e["runNote0831"] = ("Run 0831: free phase SOLD OUT 1.111/1.111 (+244 run ini, 867->1.111). "
            "Status tetap minted-by-user-2026-11-07.")
        print("NULLRAID entry:", k)

# ---- 3. new entries ----
def new_entry(address, status, name, symbol, kind, **kw):
    e = {"address": address, "status": status, "name": name, "symbol": symbol, "kind": kind}
    e.update(kw)
    return e

contracts["0xa8543350e5accacc780c9613bfa2fb9b52d3858e"] = new_entry(
    "0xa8543350e5accacc780c9613bfa2fb9b52d3858e", "strong-lead-2026-11-08-gate-pending",
    "Cabinette", "CABINETTE", "ERC721",
    totalSupply=2582, FREE_SUPPLY=7000, freeClaimed=2577, freePctVerified=36.81,
    mintOpen=True, FREE_PER_WALLET=3, MAX_PER_WALLET=50, PRICE="0.00005 BNB",
    quote_user_1=0, mintedBy_user=0, balanceOf_user=0,
    owner="0x53043412c4F2436f68e56bB9638EbEBB099Fb3C1",
    ownerNote="Owner TIDAK ada di same-owner-discards.json.",
    firstSeenBlock=132302553, firstMintWib="2026-11-08 08:12:40 WIB",
    firstMintNote="First mint TERVERIFIKASI run 0831: blok 132302553 = 2026-11-08 08:12:40 WIB "
        "(timestamp via fast_rpc eth_getBlockByNumber). Umur <=48 jam.",
    sourcify="verified (exact_match, verifiedAt 2026-10-29T13:50:21Z)",
    agentShapedNote="ABI 37 fns, gate fn AGENT_ID; contractURI base64 JSON tanpa external_link; "
        "tokenURI on-chain SVG, traits Season Autumn / Wood Pine / Roof Moss / Lights Smoke.",
    discussionNote="Boltbook post sDxwv9fvElCh oleh tale.ai, 2026-11-08 08:41:54 WIB.",
    gateNote="GATE PENDING run 0831 (browser task 3dac983e): metode A,G,M,C,J,H,I,K,N semua negatif "
        "(cabinette.vercel.app 404). Browser task memeriksa pola same-family + halaman token BscScan. "
        "Bila gate lolos -> strong-lead direct mint (audit + free check segar + preview bersih). "
        "Bila gagal -> lapor sekali + alasan, tanpa eksekusi.",
    runNote0831="Run 0831 STRONG LEAD: freeClaimed 2.577/7.000 = 36,81%, mintOpen=1, slot user TERBUKA "
        "(quote=0, mintedBy=0, balanceOf=0), umur terverifikasi <=48 jam. Gate website PENDING.",
)

contracts["0x1fab92b937572c79550aeee51cee77d3add20367"] = new_entry(
    "0x1fab92b937572c79550aeee51cee77d3add20367", "strong-lead-2026-11-08-gate-pending",
    "Mechfarm", "MECHFARM", "ERC721",
    totalSupply=2162, FREE_SUPPLY=4000, freeClaimed=2110, freePctVerified=52.75,
    mintOpen=True, FREE_PER_WALLET=2, PRICE="0.00007 BNB",
    quote_user_1=0, mintedBy_user=0, balanceOf_user=0,
    owner="0x6f244724f61d8c7fc9af40dd37ff7c82bf2b8f5d",
    ownerNote="Owner TIDAK ada di same-owner-discards.json. BUKAN Mechfarm lama "
        "0xde536232c09ea778b6cb8409328362F7e9182bc9 (promotion-discarded-same-owner-2026-11-03) - jangan tertukar.",
    firstSeenBlock=132302552, firstMintWib="2026-11-08 08:12:39 WIB",
    firstMintNote="First mint TERVERIFIKASI run 0831: blok 132302552 = 2026-11-08 08:12:39 WIB "
        "(satu blok/satu detik sebelum Cabinette; gelombang deploy/template yang sama). Umur <=48 jam.",
    sourcify="verified", agentShapedNote="AGENT_ID gate; contractURI base64 tanpa external_link; tokenURI on-chain base64.",
    discussionNote="Boltbook ZH post 'Eight free Agent ID mints' (blok 132.307.004).",
    gateNote="GATE PENDING run 0831: metode A,G,H,I,J negatif; D (mechfarm.vercel.app 404, pola lain "
        "diperiksa browser task 3dac983e), M (site: tanpa hasil), K, C masih berjalan. "
        "Bila gate lolos -> strong-lead direct mint. Bila gagal -> lapor sekali + alasan.",
    runNote0831="Run 0831 STRONG LEAD: freeClaimed 2.110/4.000 = 52,75%, mintOpen=1, slot user TERBUKA, "
        "umur terverifikasi <=48 jam (0,95 jam). Velocity belum bisa lolos run ini (bacaan pertama = baseline). "
        "Gate website PENDING.",
)

contracts["0x2728c134d79d34a977d6d35d8a3014abb5c97ed4"] = new_entry(
    "0x2728c134d79d34a977d6d35d8a3014abb5c97ed4", "watchlist-only-2026-11-08",
    "HOPKIN", "HOPKIN GENESIS", "ERC721",
    totalSupply=3692, MAX_SUPPLY=10000, mintOpen=True,
    website="https://hopkinagent.fun",
    websiteNote="WEBSITE TERVERIFIKASI run 0831: hopkinagent.fun -> HopkinGenesis menautkan kontrak eksak "
        "0x2728c134D79D34A977d6D35D8A3014AbB5C97ed4 (dikonfirmasi dari URL outlink itu sendiri; "
        "text-fetch halaman BscScan 403 - BUKAN ketiadaan). Supply situs 3.692 cocok on-chain.",
    freeNote="Free mint 1/agent wallet + PuzzlePass EIP-712 (agent memecahkan puzzle urutan angka, pass 15 menit) "
        "+ 10.000 $BUNNY per mint; own marketplace di situs. free% UNVERIFIED (tidak ada free view).",
    ageNote="Umur peluncuran UNVERIFIED -> watchlist-only.",
    runNote0831="Run 0831: ditemukan via Boltbook/hot-leg. Website lolos, free% + umur unverified -> watchlist-only.",
)

contracts["0xe7a548606eecb32a93b227411b6343b0399dc7c0"] = new_entry(
    "0xe7a548606eecb32a93b227411b6343b0399dc7c0", "watchlist-only-2026-11-08",
    "GOAT", "GOAT", "ERC721",
    totalSupply=3499, MAX_SUPPLY=100000, mintOpen=True, quote_user_1=0, balanceOf_user=0,
    freeNote="Tidak ada free view -> free% UNVERIFIED.",
    ageNote="Umur peluncuran UNVERIFIED -> watchlist-only.",
    runNote0831="Run 0831: ditemukan via scan. free% + umur unverified -> watchlist-only.",
)

contracts["0x56155fd1818b31256E7f435956D6dff5C732f35f"] = new_entry(
    "0x56155fd1818b31256E7f435956D6dff5C732f35f", "watchlist-only-mint-closed-2026-11-08",
    "OinkHash Pigs", "OINK", "ERC721",
    totalSupply=609, mintOpen=False,
    owner="0x615c47be32512f42ff3b8cd1f5f688e93fe3a929",
    ownerNote="Owner sama dengan Ink Koi; TIDAK ada di same-owner-discards.json.",
    tokenURINote="tokenURI -> oinkhash.fun. freeMint revert 'closed'.",
    runNote0831="Run 0831: ditemukan via Boltbook ZH post. Mint TUTUP (mintOpen=0) -> watchlist-only. "
        "Kontrak Pigs BARU 0xf710ebd2... adalah rilis pengganti (migrasi 8 Nov, situs oinkhash.fun).",
)

contracts["0xf710ebd2D129adfA0D49E73824e8F5210Bb638C3"] = new_entry(
    "0xf710ebd2D129adfA0D49E73824e8F5210Bb638C3", "early-lead-reported-2026-11-08",
    "OinkHash Pigs", "OINK", "ERC721",
    totalSupply=841, MAX_SUPPLY=20000, mintOpen=True, mintPrice="0.0015 BNB",
    freeClaimed_user=False, balanceOf_user=0,
    owner="0x615c47be32512f42ff3b8cd1f5f688e93fe3a929",
    ownerNote="Owner sama dengan Ink Koi + Pigs lama 0x56155fd1; TIDAK ada di same-owner-discards.json.",
    firstSeenBlock=132306475, firstMintWib="2026-11-08 08:42:05 WIB",
    firstMintNote="First mint TERVERIFIKASI run 0831: blok 132306475 = 2026-11-08 08:42:05 WIB "
        "(chunked eth_getLogs Transfer from 0x0 via Ankr, timestamp via fast_rpc). "
        "Scan window 132307470-132308469: 29 mints / 29 minters, first_block 132307582 (08:50:23 WIB). "
        "Umur <=48 jam TERVERIFIKASI (rilis hari ini).",
    sourcify="verified (exact_match, verifiedAt 2026-11-08T01:41:00Z)",
    agentShapedNote="AGENT_ID() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, isAgent(), "
        "freeMint() no-arg, freeClaimed(address) bool, registry bytes hit, ABI 76 fns (tierOf, hashpower, "
        "migrate/migrated, truf, payout).",
    freeNote="free% UNVERIFIED: tidak ada global free counter di ABI (tanpa freeMinted/freeSupply/FREE_SUPPLY). "
        "freeClaimed(user)=false, balanceOf(user)=0 -> slot user TERBUKA. "
        "Tidak bisa promosi ke strong lead tanpa free% terverifikasi.",
    websiteNote="Situs proyek oinkhash.fun (via tokenURI meta/0.json, metode I) + pengumuman migrasi "
        "'Moved to new contracts on Nov 8, 2026' di homepage. Homepage/skill.md yang terbaca TIDAK mencetak "
        "kontrak eksak 0xf710ebd2 -> gate website untuk promosi: UNVERIFIED (perlu cek lebih dalam). "
        "Early lead TIDAK PERNAH di-preview/di-mint, jadi gate tidak memblokir laporan ini.",
    runNote0831="Run 0831 EARLY LEAD (temuan scan, first-seen): agent-shaped + first mints terverifikasi on-chain. "
        "Dilaporkan sekali sebagai EARLY; tidak di-preview/di-mint.",
)

contracts["0x6c724401f0c99e63d0119c17c97665f07c978ef3"] = new_entry(
    "0x6c724401f0c99e63d0119c17c97665f07c978ef3", "watchlist-only-same-owner-discarded-2026-11-08",
    "SPACE ROT", "SROT", "ERC721",
    totalSupply=391, MAX_SUPPLY=3333, freeLeft=2945, mintOpen=True,
    owner="0x11038f4a",
    ownerNote="Owner 0x11038f4a ADA di same-owner-discards.json -> SAME-OWNER DISCARDED, "
        "tidak pernah dipromosi/dilaporkan sebagai lead.",
    tokenURINote="tokenURI -> space-rot.pages.dev.",
    runNote0831="Run 0831: ditemukan via scan. Same-owner discarded; hanya dicatat, tidak dilaporkan.",
)

contracts["0x62EC413381B74387b57F1E2734cdd2E5b96a57B7"] = new_entry(
    "0x62EC413381B74387b57F1E2734cdd2E5b96a57B7", "age-excluded-2026-11-08",
    "WOJAGENT", "WOJAGENT", "ERC20",
    totalShares=186, FREE_SHARES=1000, MAX_SHARES=50000, FREE_TOKENS_PER_SHARE=41175000,
    saleStartWib="2026-11-05 09:32:58 WIB", ageHours=71.54,
    freeClaimed_user=False, pair="0x0",
    runNote0831="Run 0831 TRACK C: sale shape S1 (mintFree(agentId), REGISTRY(), free views). "
        "saleStart 2026-11-05 09:32:58 WIB -> umur 71,54 jam >48 jam -> AGE-EXCLUDED, bukan lead. "
        "Slot user terbuka tapi tidak relevan.",
)
snap.setdefault("age_exclusions", []).append(
    {"address": "0x62EC413381B74387b57F1E2734cdd2E5b96a57B7", "project": "WOJAGENT",
     "excluded_wib": NOW, "run": "0831",
     "reason": "saleStart 2026-11-05 09:32:58 WIB, umur 71,54 jam >48 jam, belum sold out"})

contracts["0xdb51Dcc2D8cAf9942D9A975a2e68e023aB5E1fcA"] = new_entry(
    "0xdb51Dcc2D8cAf9942D9A975a2e68e023aB5E1fcA", "excluded-free-sold-out-2026-11-08",
    "HokiCat", "HCAT", "ERC721",
    totalMinted=236, freeMinted=222, FREE_CAP=222,
    runNote0831="Run 0831: free pool HABIS 222/222 (totalMinted 236). S1 shape true tapi pool habis. "
        "Dicatat excluded; tidak dilaporkan.",
)

# ---- 4. run notes ----
snap["runNote0831"] = (
    "Run 0831 (2026-11-08, blok reread 132307042, ~580 dtk): reread 461 kontrak + 70 track_c; "
    "velocity 5 pass, 0 promotable (NULLRAID minted-by-user; Rimeagent same-owner-discarded 16,62%; "
    "Skyagent age-excluded; PixelSentinels age-unverified; WAR3-1aa9 minted-by-user); soldOut 35, "
    "nearSellout 0, slotChanged 0. NULLRAID +244 (867->1.111; free phase sold out). Dafeiyu +93 (baseline). "
    "Age-sweep: remove=0, kept=56, unverified-launch=400. Track B binanceai tidak berubah "
    "(launched=0, failed=1, isRefundPhase=1, tokenClaimed_user=0, balance 0; sudah dilaporkan run 1701 2026-11-07). "
    "STRONG LEAD x2 (gate website PENDING, browser task 3dac983e): Cabinette 36,81% + MECHFARM-1fab 52,75%, "
    "keduanya first mint 08:12:39-40 WIB, slot user terbuka. DinoAgent: gate KINI LOLOS tapi free pool HABIS "
    "777/777 (~09:03 WIB) -> tidak ada mint; status sold-out-free-2026-11-08. EARLY LEAD x1 (temuan scan): "
    "OinkHash Pigs 0xf710ebd2 (first mint 08:42:05 WIB, 29 mints/29 minters di window, agent-shaped, "
    "free% unverified, slot terbuka). Watchlist-only baru: HOPKIN (website terverifikasi, free%/umur unverified), "
    "GOAT (free%/umur unverified), OinkHash Pigs 0x56155fd1 (mint tutup), SPACE ROT (same-owner discarded). "
    "WOJAGENT age-excluded 71,54 jam. HokiCat free sold out 222/222. V20 V90 (scan first-seen, 1 mint, "
    "Sourcify unverified, tanpa free shape) -> bukan agent-shaped, tidak masuk snapshot, tidak dilaporkan. "
    "Bridge: 115 kontrak, tidak ada entri baru; 7 same_owner_discarded. Boltbook EN+ZH + author tale.ai dibaca. "
    "Gap scan 132293853-132307469 dilewati (backfill dinonaktifkan user).")
snap["runNote0831_scan"] = (
    "Run 0831 SCAN SUKSES (partial=false): pre-flight OK 4,0 dtk (head 132308414, 304 logs/50 blok). "
    "Window 132307470-132308469 (1000 blok), 20/20 chunk + 188/188 enrich, 40 panggilan Ankr, 0 error. "
    "188 NFT + 339 ERC-20 mint. True first-seen: 2 (OinkHash Pigs f710 = EARLY lead; V20 V90 bukan agent-shaped). "
    "Watermark 132293852 -> 132308469. Gap 132293853-132307469 dilewati (backfill dinonaktifkan user). "
    "5c: 339 ERC20, 47 mint_count>=10, 41 sudah dicek, 6 baru dicek (cap tidak tercapai, 0 dibuang sampling limit), "
    "0 hit S1/S2 (semua Sourcify not_verified, registry_bytes=True tapi tanpa ABI).")
snap["last_run"] = "free-mint-search 2026-11-08 0831 WIB"

json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot contracts now:", len(snap["contracts"]))

# ---- 5. seen file: append all scan contracts ----
added = 0
for c in scan["contracts"]:
    a = (c.get("address") or "").lower()
    if a and a not in seen.get("contracts", {}):
        seen["contracts"][a] = c.get("first_block")
        added += 1
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)
print("seen appended:", added, "| seen total:", len(seen["contracts"]))

# ---- 6. scan-state watermark ----
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = NOW
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan["contracts"])
state["erc20_mint_contracts"] = len(scan.get("erc20_mint_contracts_list", []))
state["skipped_gap"] = "132293853-132307469 (backfill dinonaktifkan user; window scan hanya 1000 blok terbaru)"
state["note_0831_scan"] = snap["runNote0831_scan"]
json.dump(state, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("watermark ->", scan["to_block"])

# ---- 7. track-c-scan-checked merge (5c) ----
checked_list = {a.lower() for a in tc.get("checked", [])}
top_keys = {k.lower() for k in tc.keys() if k != "checked"}
merged = 0
for c in f5["checked"]:
    a = c["address"]
    if a.lower() in checked_list or a.lower() in top_keys:
        continue
    tc[a] = {"source": "run-2026-11-08-0831-5c", "status": "checked-not-sale-shape",
             "mint_count": c.get("mint_count"),
             "note": f"S1=False S2=False (Sourcify {c.get('sourcify')}, registry_bytes={c.get('registry_bytes')}, fns={c.get('fns')})"}
    merged += 1
json.dump(tc, open(f"{HF}/track-c-scan-checked.json", "w"), indent=1)
print("tc-checked merged:", merged)
print("MERGE DONE")
