#!/usr/bin/env python3
"""Merge run 1701 reread+vel+trackc-extra+binanceai into snapshot. FRESH for run 1701 only.
Written fresh by the parent (the sed-copied 1631 merge carried stale 1631 notes/block
and MUST NOT be run). Run 1701 (jadwal 17:01 WIB, dieksekusi 17:14-17:58 WIB).
Block re-read: 132758528. Reread 660 kontrak + 78 track_c (881,2 dtk).
- Velocity LOLOS 1: Skyagent (+131, 18,74x) -> TANPA promosi: status age-excluded-2026-11-06
  (first mint 2026-11-03 05:16:24 WIB, umur ~7 hari); free 3312/3333 = 99,4%.
- Fossil Drawer 591->813 (+222) TAPI prev_rate None -> TIDAK lolos (rate pertama pasca-mint);
  sudah minted-by-user (#581 run 1631).
- SEVENFOLD +9 GAGAL (audit-block MORROW riskLevel 4 HIGH + RISK dipertahankan).
  THYRK +36 (0,95x) GAGAL; DRIFTWIRE +49 (0,69x) GAGAL; Sidecoo +19 (<20) GAGAL.
  HIVE/Bubblebruin/Zapcourier/ELSY flat. Golden Agents +14 (1,0x) GAGAL.
- Sellout: dicek generik (prev free < cap <= fresh free, status belum terminal) -> lihat output.
- Age: scan deadline yang jatuh di jendela run 1631->1701 (16:31-17:55 WIB) -> lihat output.
- Cheems Agent: LAUNCHED 17:00 WIB (totalFreeMinted 165 blok 132758529, currentState 1,
  tradingOpen 0, slot user terbuka) - status TETAP track-c-lead-gate-blocked-2026-11-10
  (dilaporkan sekali run 1631; TIDAK dilaporkan ulang).
- PESI: 46/954 TIDAK BERUBAH vs run 1631. NUSA: 372/379, sudah age-excluded-2026-11-10.
- WNO: pair PCS V2 0x0 (WBNB+USDT) terverifikasi segar dengan token BENAR 0x8C969a...;
  baris 'WNO pair 0x81afde...' di trackc-extra adalah LUCKY777 (token salah di script).
- binanceai.fun: TIDAK BERUBAH (launched 0, failed 1, refund 1, shares 3110).
- Pickgrid Pickaxe #243: MINTED hot-leg 1654 (tx 0xa7d71a83...e1dfa32, blok 132758318,
  receipt 1, gas 167273) - ditambahkan ke contracts sebagai minted-by-user-2026-11-10.
- Caishen Agent: MINTED run ini (track-C lead direct mint, tx 0xf618e485...f2e620,
  blok 132760929, receipt 1, gas 104366) - ditambahkan ke track_c sebagai minted-by-user-2026-11-10.
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1701"
BLOCK = 132758528
NOW = "2026-11-10 17:01 WIB"
INTERVAL = 30.0
NOW_DT = datetime.datetime(2026, 11, 10, 17, 55, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
WIN_START = datetime.datetime(2026, 11, 10, 16, 31, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
extra = json.load(open(f"{BASE}/run-{TS}-trackc-extra.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1701-premerge")

updated = 0
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    row = vel.get("rows", {}).get(name, {})
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    if row.get("minted") is not None:
        entry["previousTotalSupply"] = row.get("prev")
        entry["mintedInInterval"] = row.get("minted")
        entry["intervalMinutes"] = INTERVAL
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote1701_1110"] = text

def dyn_note(name, extra_txt=""):
    row = vel.get("rows", {}).get(name, {})
    f = rr.get("reread", {}).get(name, {})
    e = snap["contracts"].get(name, {})
    if not row:
        return None
    minted = row.get("minted"); rate = row.get("rate"); ratio = row.get("ratio")
    passes = row.get("passes")
    fm = f.get("freeMinted"); fc = f.get("freeClaimed")
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP") or e.get("agentFreeCap") or e.get("MAX_SUPPLY")
    freetxt = ""
    if fm is not None and cap and cap < 10**12:
        freetxt = f"; freeMinted {fm}/{cap} = {fm/cap*100:.1f}%"
    elif fc is not None and cap and cap < 10**12:
        freetxt = f"; freeClaimed {fc}/{cap} = {fc/cap*100:.1f}%"
    vtxt = "velocity LOLOS" if passes else "velocity GAGAL"
    return (f"Run 1701 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

# ---- key watchlist notes ----
note("Skyagent", (dyn_note("Skyagent") or "") +
     " Velocity LOLOS run ini (+131, 18,74x) TAPI TANPA promosi: status age-excluded-2026-11-06 "
     "(first mint 2026-11-03 05:16:24 WIB, umur ~7 hari >48 jam); free 3312/3333 = 99,4% "
     "(hampir sold out). TIDAK preview/mint, TIDAK dilaporkan ulang.")
note("Fossil Drawer", (dyn_note("Fossil Drawer") or "") +
     " +222 run ini tapi prev_rate None (rate pertama pasca-mint run 1631) -> velocity TIDAK lolos. "
     "Sudah minted-by-user (#581 run 1631); tanpa perubahan status.")
note("SEVENFOLD", (dyn_note("SEVENFOLD") or "") +
     " KANDIDAT tetap AUDIT-BLOCKED (dilaporkan 12:03 + 13:30; tidak dilaporkan ulang). "
     "free 1752/3000 = 58,4% >=50% tapi velocity GAGAL run ini (+9, 0,64x). "
     "Audit-block dari run 1431 dipertahankan (token MORROW riskLevel 4 HIGH + RISK); tidak di-audit ulang run ini. TIDAK preview/mint.")
note("THYRK", (dyn_note("THYRK") or "") + " Sudah minted-by-user (#6849 run 1231 + 20 THYRK pending swap) -> velocity GAGAL run ini, tanpa relevansi.")
note("DRIFTWIRE", (dyn_note("DRIFTWIRE") or "") + " Sudah minted-by-user (#745 run 1231) -> velocity GAGAL run ini, tanpa relevansi.")
note("Sidecoo", (dyn_note("Sidecoo") or "") +
     " Velocity GAGAL run ini (+19, 1,73x tapi <20 token). Free views tetap None -> free% UNVERIFIED; bukan strong lead, bukan kandidat, TIDAK preview/mint.")
note("ELSY AGENT", (dyn_note("ELSY AGENT") or "") + " Pasca-mint terverifikasi: bal_user=2 (#880/#881). TIDAK di-auto-list (own market tidak live).")
note("Sakura", (dyn_note("Sakura") or "") + " Tetap early lead; first mint terverifikasi 2026-11-10 01:47 WIB -> deadline 48 jam 2026-11-12 01:47 WIB.")
note("Golden Agents", (dyn_note("Golden Agents") or "") + " Tetap early lead; first mint terverifikasi 2026-11-09 ~02:00 WIB -> deadline 48 jam 2026-11-11 ~02:00 WIB.")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") + " Minted-by-user; tanpa perubahan.")
note("Zapcourier", (dyn_note("Zapcourier") or "") + " Minted-by-user; free pool 712/712 habis; tanpa perubahan.")

# ---- generic NEW-sellout detection (prev free < cap <= fresh free, status not terminal) ----
TERMINAL = ("sold-out", "soldout", "age-excluded", "excluded-", "minted-by-user")
new_sellouts = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name, {})
    cap = entry.get("FREE_SUPPLY") or entry.get("FREE_CAP") or entry.get("agentFreeCap")
    if not cap or cap >= 10**12:
        continue
    st = str(entry.get("status", ""))
    if any(t in st for t in TERMINAL):
        continue
    for key in ("freeMinted", "freeClaimed"):
        prev = entry.get(key)
        fresh = f.get(key)
        if prev is not None and fresh is not None and prev < cap <= fresh:
            new_sellouts.append((name, key, prev, fresh, cap))
            entry["status"] = "sold-out-free-pool-exhausted-2026-11-10"
            entry["runNote1701_1110"] = (f"Run 1701 (blok {BLOCK}): SELLOUT BARU - {key} {prev}->{fresh}/{cap} "
                f"(cap tercapai interval ini). Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali oleh parent.")
            break
print("NEW SELLOUTS:", new_sellouts if new_sellouts else "none")

# ---- age-exclusion scan: deadlines falling inside run 1631 -> 1701 window ----
def parse_wib(s):
    if not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S WIB", "%Y-%m-%dT%H:%M:%S+07:00", "%Y-%m-%d %H:%M WIB"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
        except Exception:
            continue
    return None
new_age_excl = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    st = str(entry.get("status", ""))
    if any(t in st for t in TERMINAL):
        continue
    launch = None
    for k in ("firstMintWib", "startTimeWib", "launchWib"):
        launch = parse_wib(entry.get(k))
        if launch:
            break
    if not launch:
        continue
    deadline = launch + datetime.timedelta(hours=48)
    if WIN_START < deadline <= NOW_DT:
        sold = False
        f = rr.get("reread", {}).get(name, {})
        cap = entry.get("FREE_SUPPLY") or entry.get("FREE_CAP")
        fm = f.get("freeMinted"); fc = f.get("freeClaimed")
        if cap and ((fm is not None and fm >= cap) or (fc is not None and fc >= cap)):
            sold = True
        entry["status"] = "age-excluded-2026-11-10"
        entry["runNote1701_1110"] = (f"Run 1701 (blok {BLOCK}): AGE-EXCLUDED - launch terverifikasi {launch}, "
            f"deadline 48 jam {deadline} lewat; soldOut={sold}. Status -> age-excluded-2026-11-10. Dilaporkan sekali oleh parent.")
        new_age_excl.append((name, str(launch), str(deadline), sold))
print("NEW AGE EXCLUSIONS:", new_age_excl if new_age_excl else "none")

# ---- track_c generic lastRead updates ----
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    if name in rr.get("track_c", {}):
        entry["lastReadBlock"] = BLOCK
        entry["lastReadWib"] = NOW

# ---- Cheems Agent: LAUNCHED 17:00 WIB, gate-blocked (reported once run 1631) ----
tc = snap.get("track_c", {})
if isinstance(tc.get("Cheems Agent"), dict):
    ch = extra["checks"]["Cheems Agent"]["views"]
    tc["Cheems Agent"]["runNote1701_1110"] = (
        f"Run 1701 (blok {BLOCK}): LAUNCHED 17:00 WIB (mintStart {ch.get('mintStart')}), totalMinted {ch.get('totalMinted')}, "
        f"totalFreeMinted {ch.get('totalFreeMinted')} (blok 132758529), currentState {ch.get('currentState')}, "
        f"tradingOpen {ch.get('tradingOpen')}; freeClaimedByWallet(user)={ch.get('freeClaimedByWallet_user')} -> slot terbuka. "
        f"Status TETAP track-c-lead-gate-blocked-2026-11-10 (dilaporkan sekali run 1631) -> TIDAK dilaporkan ulang, TIDAK preview/mint.")
    tc["Cheems Agent"]["lastReadBlock"] = BLOCK
    tc["Cheems Agent"]["lastReadWib"] = NOW
if isinstance(tc.get("PESI"), dict):
    pe = extra["checks"]["PESI"]["views"]
    tc["PESI"]["runNote1701_1110"] = (
        f"Run 1701 (blok {BLOCK}): freeShares {pe.get('freeShares')} (run 1631: 46), freeRemaining {pe.get('freeRemaining')} "
        f"(run 1631: 954), freeCap {pe.get('freeCap')}, paidShares {pe.get('paidShares')}, lpCreated {pe.get('lpCreated')}. "
        f"TIDAK ADA perubahan vs run 1631. Gate GAGAL + audit token RISK TIDAK BERUBAH -> TIDAK dilaporkan ulang, TIDAK preview/mint.")
    tc["PESI"]["lastReadBlock"] = BLOCK
    tc["PESI"]["lastReadWib"] = NOW
if isinstance(tc.get("NUSA"), dict):
    nu = extra["checks"]["NUSA"]["views"]
    tc["NUSA"]["runNote1701_1110"] = (
        f"Run 1701 (blok {BLOCK}): freeMinted {nu.get('freeMinted')} (run 1631: 372), sharesMinted {nu.get('sharesMinted')}, "
        f"soldOut {nu.get('soldOut')}, closed {nu.get('closed')}. Status sudah age-excluded-2026-11-10 (dilaporkan sekali run 1631). "
        f"TIDAK preview/mint, TIDAK dilaporkan ulang.")
    tc["NUSA"]["lastReadBlock"] = BLOCK
    tc["NUSA"]["lastReadWib"] = NOW
if isinstance(tc.get("WNO"), dict):
    tc["WNO"]["runNote1701_1110"] = (
        f"Run 1701 (blok {BLOCK}): pair PCS V2 WNO/WBNB = 0x0 DAN WNO/USDT = 0x0 terverifikasi segar oleh parent "
        f"dengan token BENAR 0x8C969a4CD49E4774908e667702C3d7C3ece164D0 (factory getPair) -> pending-swaps no_pair TIDAK BERUBAH. "
        f"KOREKSI SCRIPT: baris 'WNO pair 0x81afde...' di trackc-extra memakai token LUCKY777 0xc6D4ec8C... (salah) - itu pair LUCKY777/WBNB, bukan WNO. "
        f"Balance WNO user tetap 1.000.000 (1e24).")
    tc["WNO"]["lastReadBlock"] = BLOCK
    tc["WNO"]["lastReadWib"] = NOW
if isinstance(tc.get("CLEPSYDRA"), dict):
    tc["CLEPSYDRA"]["runNote1701_1110"] = "Run 1701: free views tetap None (freeMinted/freeSharesRemaining null), totalSupply 1e27, bal_user=0. Gate-blocked, TIDAK ada perubahan."
if isinstance(tc.get("MoonAgent-MOAGT"), dict):
    tc["MoonAgent-MOAGT"]["runNote1701_1110"] = "Run 1701: free views tetap None, totalSupply 1e27, bal_user=0. Lead-gate-blocked, TIDAK ada perubahan."

# ---- Pickgrid Pickaxe #243 (hot-leg 1654 mint) -> contracts ----
snap["contracts"]["Pickgrid Pickaxe"] = {
    "address": "0xc2BEAaD13Ef2833D976957E41B03b6B2661cFAB0",
    "status": "minted-by-user-2026-11-10",
    "name": "Pickgrid Pickaxe",
    "symbol": "PICKAXE",
    "kind": "ERC721",
    "totalSupply": 248,
    "freeMinted": 246,
    "FREE_CAP": 300,
    "live": 1,
    "firstLiveWib": "2026-11-10 16:59:30 WIB",
    "firstLiveBlock": 132756503,
    "userBalance": 1,
    "mintTokenId": 243,
    "mintTx": "0xa7d71a836c98d5f12bf3f23ed8cb707216d8b3fb50c6e9e7a1f24ff23e1dfa32",
    "mintBlock": 132758318,
    "mintGas": 167273,
    "orderId": "26111000002031312613",
    "isFree": True,
    "lockedUntil": 1794910386,
    "lockedUntilWib": "2026-11-17 17:13:06 WIB",
    "website": "https://pickgrid.xyz",
    "xHandle": "@Pickgrid_xyz",
    "lastReadBlock": 132759389,
    "lastReadWib": "2026-11-10 ~17:30 WIB",
    "runNote1701_1110": ("Run 1701: Pickgrid Pickaxe #243 MINTED oleh hot-leg 1654 (strong-lead direct mint; "
        "live 16:59:30 WIB, free 239/300 = 79,7% saat pre-check, slot terbuka freeEligible=1; website pickgrid.xyz "
        "config mencetak kontrak persis + registry; audit hasResult=false; preview bersih 000000000). "
        "Verifikasi segar parent run 1701 (blok 132759389): ownerOf(243)=wallet agent, balanceOf=1, agentIdClaimed=1, "
        "freeMinted 246/300, isFree=1, lockedUntil 2026-11-17 17:13:06 WIB (transfer-locked 7 hari). "
        "Rarity: tier NOT verified (tokenURI -> https://pickgrid.xyz/meta/free.json shared; Type Agent, Boost 1.1x; tanpa trait Rarity/Tier) - tercatat di nft-rarity-inventory.md. "
        "Marketplace: own market TIDAK live terverifikasi + NFT terkunci 7 hari -> TIDAK di-auto-list (Element fallback manual saja). "
        "PICK tidak di-mint oleh NFT ini (hanya boost 1,1x); tidak ada token untuk pending swap."),
}

# ---- Caishen Agent (run 1701 track-C lead direct mint) -> track_c ----
tc["Caishen Agent"] = {
    "address": "0xF27519dE8268a07d3A79415112F56D11258FA91e",
    "token": "0xeD290fA2e34233d0ee97eA95C2a34E770A9DA45D",
    "pair": "0x3020220Ca11BaE3F027C0DC8A3b8Bb73D5b55A00",
    "status": "minted-by-user-2026-11-10",
    "symbol": "CSAGENT",
    "kind": "track-c-sale",
    "saleStart": 1794305076,
    "saleStartWib": "2026-11-10 17:04:36 WIB",
    "saleEnd": 1794477876,
    "freeShares": 300,
    "freeSoldAtMint": 155,
    "freeSold": 236,
    "paidSoldAtMint": 10,
    "capShares": 10000,
    "floorShares": 3334,
    "priceWei": 3000000000000000,
    "tokensPerShare": 100000,
    "userBalance": 100000,
    "mintTx": "0xf618e48560b669442702e50ad8efb17490769376b15b09055bacc12275f2e620",
    "mintBlock": 132760929,
    "mintGas": 104366,
    "orderId": "26111000002031344556",
    "previewRequestId": "b5a97ced9af8495d865099513ff2145f",
    "website": "https://caishenagent.surge.sh/",
    "lastReadBlock": 132761370,
    "lastReadWib": "2026-11-10 ~17:55 WIB",
    "runNote1701_1110": ("Run 1701: Caishen Agent (CSAGENT) MINTED - track-C lead direct mint. Ditemukan route 5a (Sourcify feed, "
        "verifiedAt 2026-11-10T10:05:01Z). S1 PASS (mint+quote+price+freeAvailable/freeClaimed+claimFree+REGISTRY()=0x60B926...22F). "
        "Lead legs: free pool 300-155=145 tersisa saat pre-check (freeSold 155), slot user terbuka (freeAvailable=1, freeClaimed(agentId)=0), "
        "launch terverifikasi saleStart 2026-11-10 17:04:36 WIB (umur ~45 mnt). Gate website LOLOS (caishenagent.surge.sh skill.md+llms.txt "
        "mencetak sale+token+pair+registry persis; website() on-chain mengembalikan situs). Same-owner-discards dicek (sale+token tidak ada). "
        "Audit Binance segar: sale + token hasResult=false (tanpa hasil, bukan lolos), riskLevel -1, tanpa RISK hit. "
        "Preview bersih 000000000 (+1e23 CSAGENT = 100.000, tanpa authority/allowance/risk). "
        "Verifikasi: receipt 1, blok 132760929, gas 104366; balanceOf(user) 0->100.000 CSAGENT, freeClaimed(agentId) 0->1, freeAvailable 1->0. "
        "Bukan NFT: cek marketplace/rarity TIDAK berlaku. Pair PCS V2 sudah ada tapi cadangan 0/0 (pool belum dibuka, opened()=false) -> "
        "100.000 CSAGENT didaftarkan pending-swaps.json entri ke-18 (no_liquidity_pool_unopened)."),
}

snap["last_run"] = 1
snap["last_run_wib"] = NOW
snap["last_run_block"] = BLOCK
snap["last_run_note"] = ("Run 1701: re-read 660 kontrak + 78 track_c (blok 132758528; 881,2 dtk). "
    "Velocity LOLOS 1 (Skyagent +131, 18,74x) - TANPA promosi (age-excluded 2026-11-06). "
    "Fossil Drawer +222 tanpa lolos (prev_rate None; minted-by-user). SEVENFOLD +9 GAGAL, audit-block dipertahankan. "
    "THYRK +36 (0,95x), DRIFTWIRE +49 (0,69x), Sidecoo +19 (<20) GAGAL. Sellout baru: lihat merge output. Age-exclusion baru: lihat merge output. "
    "Cheems Agent LAUNCHED 17:00 WIB (totalFreeMinted 165) - gate-blocked, sudah dilaporkan sekali run 1631, TIDAK dilaporkan ulang. "
    "PESI 46/954 tanpa perubahan. NUSA 372/379, sudah age-excluded. WNO pair 0x0 terverifikasi segar (token benar); trackc-extra mislabel LUCKY777 dicatat. "
    "binanceai.fun TIDAK BERUBAH (launched 0, failed 1, refund 1, shares 3110). "
    "Bridge: scan-bridge.json TIDAK berubah (mtime 2026-11-08 18:21, 116 kontrak) -> 0 temuan baru. "
    "Boltbook: EN+ZH HTTP 200, 25 kartu, 0 alamat baru. Sweep: 0 proyek baru (rute 3/5b/6); Sourcify feed: 1 baru = Caishen Agent. "
    "MINT 1: Pickgrid Pickaxe #243 (hot-leg 1654, tx 0xa7d71a83...e1dfa32, blok 132758318). "
    "MINT 2: Caishen Agent 100.000 CSAGENT (track-C lead direct mint run ini, tx 0xf618e485...f2e620, blok 132760929).")
snap["runNote1701_1110"] = snap["last_run_note"]

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE 1701 DONE: contracts updated={updated}, block={BLOCK}")
print("track_c count now:", len(snap.get("track_c", {})))
print("contracts count now:", len(snap.get("contracts", {})))
