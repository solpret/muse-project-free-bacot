#!/usr/bin/env python3
"""Merge run 2026-11-14 15:01 WIB (free-mint-search run 1501) into onchain-snapshot.json.
v2: baselines come from the 1431 reread JSON (ground truth), NOT from the
snapshot's previousTotalSupply (which lags one run: it holds the 1401 value
while totalMinted holds the 1431 value). Entries are matched by ADDRESS;
the bare reread-name entry is the live one (the older suffixed duplicates
are stale and left untouched). No preview/mint."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-14-1501-reread.json"))
r31 = json.load(open(BASE + "run-2026-11-14-1431-reread.json"))
r01 = json.load(open(BASE + "run-2026-11-14-1401-reread.json"))
BLOCK = reread["block"]  # 133508775
INTERVAL_MIN = (BLOCK - 133504646) * 0.45 / 60.0  # ~31.0 min vs run 1431 block
PREV_MIN = (133504646 - 133500940) * 0.45 / 60.0  # ~27.8 min, 1401 -> 1431
C = snap["contracts"]
SUPPLY_KEY = {
 "WoozCode": "totalSnippets", "MORFO": "totalMinted", "NOISE": "totalMinted",
 "DragonAgents": "totalSupply", "AngelEye-77D9": "totalSupply", "AngelEye-07bD": "totalSupply",
 "NovaRemnants": "totalRemnants", "RaceAgents": "totalSupply", "AbsurdAgentNFT": "totalMinted",
 "B77D": "totalMinted", "Zero": "totalSupply", "HIVE": "totalSupply",
 "AgentZENITH": "totalSupply", "AgentNOVA": "totalSupply", "SPARKS": "totalSupply",
 "AgentBubble": "totalSupply", "WANGCAI": "totalSupply", "YUANBAO": "totalSupply",
 "NOTV": "totalSupply", "PX24": "totalSupply", "Zephyra": "totalMinted",
 "LumenFindings": "totalSpecimens", "Pengu": "totalMinted", "CPASS": "totalMinted",
 "SPEC": "totalSpecimens", "TrashBandits": "totalMinted", "SKRR": "totalSupply",
 "REOPIR": "totalSupply", "FrieAgent-B751": "totalSupply", "FrieAgent-c64d": "totalSupply",
 "Ledgera": "totalSupply", "MAMI": "totalSupply", "INKI": "totalSupply", "OTV": "totalSupply",
 "HashcatDepot": "totalSupply",
}
def _sup(v):
    if not v: return None
    return v.get("totalSupply", v.get("totalMinted", v.get("totalSpecimens", v.get("totalRemnants"))))
# address -> snapshot key (prefer the bare reread-name key = live entry)
addr2key = {}
for k, e in C.items():
    a = (e.get("address") or "").lower()
    if a and (a not in addr2key or k in SUPPLY_KEY):
        addr2key[a] = k
def vel_note(name, new_ts, prev_ts, prev_rate):
    if new_ts is None or prev_ts is None:
        return None, None, None
    minted = new_ts - prev_ts
    rate = minted / INTERVAL_MIN if INTERVAL_MIN else 0.0
    ratio = (rate / prev_rate) if prev_rate else None
    passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
    note = (f"Run 1501 (blok {BLOCK}, interval ~{INTERVAL_MIN:.1f} mnt vs run 1431): "
            f"{prev_ts}->{new_ts} (+{minted}, {rate:.4f}/mnt vs prev {prev_rate} = "
            f"{ratio if ratio is None else round(ratio,2)}x) -> velocity "
            f"{'LOLOS' if passes else 'GAGAL'}")
    return minted, rate, (ratio, passes, note)
notes = {}
for name, item in reread["reads"].items():
    views = item.get("views")
    key = addr2key.get((item.get("address") or "").lower(), name)
    if key not in C:
        C[key] = {"address": item["address"]}
        addr2key[(item.get("address") or "").lower()] = key
    e = C[key]
    if views is None:
        notes[name] = "Run 1501: SEMUA view gagal baca (nilai lama dipertahankan)."
        continue
    sk = SUPPLY_KEY.get(name)
    # baseline = 1431 reread value (ground truth for this interval)
    prev_ts = None
    if sk:
        prev_ts = _sup(r31["reads"].get(name, {}).get("views")) if r31["reads"].get(name, {}).get("views") else None
        # _sup picks totalSupply first; for totalMinted-keyed items use the key directly
        pv = r31["reads"].get(name, {}).get("views") or {}
        prev_ts = pv.get(sk)
    if prev_ts is None:
        prev_ts = e.get("previousTotalSupply")
    prev_rate = None
    if sk:
        a = (r01["reads"].get(name, {}).get("views") or {}).get(sk)
        b = (r31["reads"].get(name, {}).get("views") or {}).get(sk)
        if a is not None and b is not None:
            prev_rate = round((b - a) / PREV_MIN, 4)
    if prev_rate is None:
        prev_rate = e.get("previousRatePerMin")
    new_ts = views.get(sk) if sk else None
    minted, rate, vres = vel_note(name, new_ts, prev_ts, prev_rate)
    for k, v in views.items():
        if v is not None:
            e[k] = v
    if new_ts is not None:
        e["previousTotalSupply"] = new_ts
    if rate is not None:
        e["previousRatePerMin"] = round(rate, 4)
        e["currentRatePerMin"] = round(rate, 4)
    if vres:
        ratio, passes, note = vres
        e["velocityRatio"] = ratio
        e["velocityLegPasses"] = passes
        e["runNote1501_1114"] = note
        notes[name] = note
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-14 ~15:01 WIB"
    if minted is not None:
        e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
# --- item-specific updates ---
w = C["WANGCAI"]
w["free_pct"] = 100.0
w["status"] = "sold-out-2026-11-14"
y = C["YUANBAO"]
y["free_pct"] = 100.0
y["status"] = "sold-out-2026-11-14"
C["Ledgera"]["free_pct"] = round(2438/5000*100, 1)
tc = snap.setdefault("track_c", {})
if "ORBIT" in tc:
    tc["ORBIT"]["freeClaimed"] = 239
    tc["ORBIT"]["lastReadBlock"] = BLOCK
    tc["ORBIT"]["lastReadWib"] = "2026-11-14 ~15:01 WIB"
    tc["ORBIT"]["runNote1501"] = ("Run 1501: freeClaimed 237->239/888 (26,9%), claimOpen=1, "
        "hasFreeClaimed(user)=0, slot terbuka; umur TETAP UNVERIFIED -> watchlist-only, tanpa perubahan.")
pc = snap.setdefault("pending_claims", {}).get("binanceai.fun", {})
pc["lastReadWib"] = "2026-11-14 ~15:01 WIB"
pc["runNote1501"] = ("Run 1501: launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 (blok %d) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM" % BLOCK)
# --- new entries ---
C["RAVE"] = {
 "address": "0x7c40B78992d86EDfFB5553C74dB5EF427100bb95",
 "name": "Rave", "symbol": "RAVE", "kind": "ERC721",
 "status": "early-lead-reported-2026-11-14",
 "totalSupply": 84, "totalMinted": 84, "freeMinted": 84,
 "MAX_SUPPLY": 3000, "MAX_PER_WALLET": 5, "mintOpen": 1, "mintOpensAt": 0,
 "price": 2000000000000000,
 "agentIdRegistry": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
 "holdsAgentId_user": 1, "freeClaimed_user": 0, "mintsBy_user": 0, "balanceOf_user": 0,
 "owner": "0xc3da2a943c48ede26132eac26d9617aed20775b3",
 "firstSeenBlock": BLOCK, "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~15:01 WIB",
 "website": None, "gate": "website_unverified",
 "free_pct": round(84/3000*100, 1),
 "launchNote": ("Umur UNVERIFIED: Sourcify verifiedAt 2026-11-14T08:02:45Z (verifikasi, BUKAN launch time); "
   "first-mint TIDAK terverifikasi — eth_getLogs Transfer-from-zero gagal SEMUA endpoint (publicnode/dataseed/dataseed1 "
   "limit exceeded -32005 pada jendela 2000 blok; dataseed2/3/defibit -32005 + onfinality -32029 pada jendela 500 blok; Ankr 401). "
   "Mint pertama pasti sesudah verifikasi 15:02:45 WIB (84 mint tercatat ~15:05 WIB), tapi blok pertama belum terbukti."),
 "baselineNote": ("EARLY LEAD run 1501 (dilaporkan sekali): BARU dari poll feed Sourcify limit 20 (verifiedAt 08:02:45Z, "
   "1 dari 4 yang baru vs hot-leg-seen). Sourcify exact_match 35 fns: mint() payable no-arg + price() 0,002 BNB + "
   "freeClaimed(address)->bool + freeMinted() + agentIdRegistry()->0x60B9... (registry BENAR) + holdsAgentId + mintOpen + "
   "mintOpensAt + MAX_SUPPLY 3000. On-chain run ini (blok 133508593): totalMinted 84 = freeMinted 84 (SEMUA mint sejauh ini gratis), "
   "mintOpen 1, mintOpensAt 0, holdsAgentId(user)=1, freeClaimed(user)=0 (slot TERBUKA), mintsBy(user)=0. "
   "Free 84/3000 = 2,8% (jauh di bawah 50%/70%). Umur UNVERIFIED + X UNVERIFIED + website UNVERIFIED "
   "(tokenURI(1)='1' tanpa URL; contractURI() revert; pencarian nama/kontrak tanpa hasil) -> BUKAN kandidat/strong lead. "
   "TIDAK PERNAH di-preview/di-mint (early lead). Watchlist-only untuk tracking velocity + umur."),
 "source": "Sourcify feed run 1501",
}
C["Starcore Miners"] = {
 "address": "0xCAc2B707cCf3309aE944a0DB036DFC75aDcC9Be7",
 "name": "Starcore Miners", "symbol": "STAR", "kind": "ERC721",
 "status": "checked-not-agent-shaped-2026-11-14",
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~15:01 WIB",
 "baselineNote": ("BARU dari Boltbook EN+ZH run 1501 (2 post: 9 lalu 14/5.000, freeMint, 'no Agent ID'). "
   "Sourcify exact_match 37 fns: freeMint() + freeUsed + mint() + PRICE 0,001 BNB TAPI TANPA registry/AgentGate "
   "(agent=False; post Boltbook sendiri: 'no Agent ID') -> BUKAN agent-shaped, BUKAN early lead, BUKAN track C. "
   "Tidak dilaporkan sebagai lead, tidak masuk watchlist aktif."),
 "source": "Boltbook EN+ZH run 1501",
}
C["Box Cars Driving Licence"] = {
 "address": "0x4084d67c1D7EdAA609DF0c860C57454f46219217",
 "name": "Box Cars Driving Licence", "symbol": "BOXLIC", "kind": "ERC721",
 "status": "checked-not-agent-shaped-2026-11-14",
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~15:01 WIB",
 "baselineNote": ("BARU dari Boltbook ZH run 1501 (post: 215 minted, first 1.000 get Founder). Sourcify exact_match 38 fns: "
   "mint() + carOf/classCounts/founders/isFounder + mintStart, TANPA free view + TANPA registry/AgentGate -> BUKAN agent-shaped, "
   "BUKAN early lead, BUKAN track C. Tidak dilaporkan sebagai lead, tidak masuk watchlist aktif."),
 "source": "Boltbook ZH run 1501",
}
C["FLICK"] = {
 "address": "0x824e27094492D588FAf9A419EBD2EB363Cd122c9",
 "name": "FLICK", "kind": "ERC20-sale",
 "status": "checked-not-sale-shape-2026-11-14",
 "token": "0x007d0D1811C9d1fbFE53374B517336D027E663F5",
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~15:01 WIB",
 "baselineNote": ("BARU dari sweep ZH run 1501 (thecolony.ai, 11 Nov; launchpad + token Sourcify-verified; 0/10.000 shares saat artikel; "
   "deadline mint 2026-11-14 18:37 UTC). Sourcify launchpad exact_match 62 fns: mint() + costOf() + AGENT_REGISTRY TAPI TANPA SATU PUN "
   "free-share view (free* = []) -> GAGAL bentuk sale S1 (free view wajib); ladder berbayar 0,002->0,0035 BNB/share, tanpa jalur gratis "
   "-> BUKAN track C, BUKAN lead. Tidak dilaporkan sebagai lead, tidak masuk watchlist aktif."),
 "source": "Sweep ZH run 1501",
}
C["Feed-0x511E"] = {
 "address": "0x511E9c9815696F1C04Ffa21E75a66823Bda2cDbF",
 "kind": "unknown", "status": "checked-not-agent-shaped-2026-11-14",
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~15:01 WIB",
 "baselineNote": ("Sourcify feed run 1501 (verifiedAt 2026-11-14T07:53:52Z; hot-leg 1454 shape-check gagal HTTP 400, di-retry run ini). "
   "ABI 6 fns (balanceOfToken/delegatedTransfer/owner/recoverTokens/renounceOwnership/transferOwnership) — helper delegasi/recovery, "
   "TANPA mint/quote/free view/registry -> BUKAN agent-shaped, bukan S1/S2. Tidak dilaporkan, tidak masuk watchlist."),
 "source": "Sourcify feed run 1501",
}
C["Feed-0xE3Ad"] = {
 "address": "0xE3Ad908E4A9680B83A476166b86B852D04ff75Df",
 "kind": "ERC20", "status": "checked-not-agent-shaped-2026-11-14",
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~15:01 WIB",
 "baselineNote": ("Sourcify feed run 1501 (verifiedAt 2026-11-14T08:03:15Z). ABI 9 fns: plain ERC-20 "
   "(allowance/approve/balanceOf/decimals/name/symbol/totalSupply/transfer/transferFrom), TANPA mint/quote/free view/registry "
   "-> BUKAN agent-shaped, bukan S1/S2. Tidak dilaporkan, tidak masuk watchlist."),
 "source": "Sourcify feed run 1501",
}
C["Feed-0x2cc2"] = {
 "address": "0x2cc212f57FBBfD191640655dc6319FFb0E567c1c",
 "kind": "ERC20", "status": "checked-not-sale-shape-2026-11-14",
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~15:01 WIB",
 "baselineNote": ("Sourcify feed run 1501 (verifiedAt 2026-11-14T07:59:00Z). ABI 29 fns: mint() + quote() + AGENT_REGISTRY + registerAgent "
   "TAPI TANPA SATU PUN free-share view (free* = []) -> GAGAL bentuk sale S1 (free view wajib); bukan S2 (bukan single-contract "
   "token+sale dengan free view). BUKAN track C. Tidak dilaporkan sebagai lead, tidak masuk watchlist."),
 "source": "Sourcify feed run 1501",
}
C["Feed-0x0E80"] = {
 "address": "0x0E8010254fD708456A42037f8149B72178af34AA",
 "kind": "unknown", "status": "checked-not-agent-shaped-2026-11-14",
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~15:01 WIB",
 "baselineNote": ("Sourcify feed run 1501 (verifiedAt 2026-11-14T07:58:36Z). ABI 8 fns (ROUTER/USDT/WBNB/admin/beneficiary/operator/sell/setOperator) "
   "— kontrak router/sell, TANPA mint/quote/free view/registry -> BUKAN agent-shaped, bukan S1/S2. Tidak dilaporkan, tidak masuk watchlist."),
 "source": "Sourcify feed run 1501",
}
snap["checkedNotAgentShaped1501"] = [
 "0x511E9c9815696F1C04Ffa21E75a66823Bda2cDbF", "0xE3Ad908E4A9680B83A476166b86B852D04ff75Df",
 "0x2cc212f57FBBfD191640655dc6319FFb0E567c1c", "0x0E8010254fD708456A42037f8149B72178af34AA",
 "0xCAc2B707cCf3309aE944a0DB036DFC75aDcC9Be7", "0x4084d67c1D7EdAA609DF0c860C57454f46219217",
 "0x824e27094492D588FAf9A419EBD2EB363Cd122c9"]
snap["last_run_wib"] = "2026-11-14 ~15:01 WIB"
snap["last_run"] = "run-1501"
snap["runNote1501_1114"] = (
 "Run 1501: reread 37/37 OK blok 133508775 (197,2 dtk, interval ~31,0 mnt vs run 1431, baseline dari reread JSON 1431). "
 "Velocity LOLOS 2 item TAPI free% UNVERIFIED -> BUKAN kandidat/strong lead: NOISE 641->678 (+37, 1,195/mnt, ratio 3,32x); "
 "B77D 994->1036 (+42, 1,356/mnt, ratio 3,77x; umur TERVERIFIKASI first-mint 08:05-08:34 WIB, <24j). "
 "AgentBubble free 1407/2222=63,3% (>=50%) TAPI velocity GAGAL (+4, 0,129/mnt) + umur UNVERIFIED -> bukan kandidat. "
 "RaceAgents free 540/1000=54% TAPI velocity GAGAL (+0). Ledgera free 2438/5000=48,8% (<50%), velocity GAGAL (+19). "
 "CPASS velocity GAGAL (+16 <20). WANGCAI SOLD OUT 129->188 (188/188=100%) — status sold-out-2026-11-14 "
 "(konfirmasi post Boltbook datt.my 14:40 WIB); YUANBAO tetap sold out 188/188. HIVE 1263 FLAT, minted-by-user. "
 "Zero + PX24 totalSupply/freeClaimed gagal baca lagi. EARLY LEAD BARU: RAVE 0x7c40B78992d86EDfFB5553C74dB5EF427100bb95 "
 "(84 mint, semua gratis, slot user terbuka; umur/X/website UNVERIFIED). binanceai tetap refund phase (launched 0, failed 1). "
 "ORBIT track_c freeClaimed 239/888 (26,9%), umur UNVERIFIED. 0 eksekusi/preview. "
 "CATATAN MERGE: baseline velocity run ini diambil dari reread JSON 1431 (previousTotalSupply snapshot ketinggalan satu run); "
 "merge v1 yang salah baseline sudah di-restore dan diganti v2 ini.")
snap["runNote1501_1114_scan"] = (
 "Scan leg FAST-FAIL run 1501: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 16,3 dtk (head 133508309, blok 133508259-133508309). "
 "Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati (tanpa output scan). Outage Ankr 401 sejak 2026-11-09 berlanjut; "
 "perlu reconnect kredensial Ankr (di luar scope job ini).")
snap["runNote1501_1114_feedshape"] = (
 "Feed Sourcify run 1501 (limit 20, verifiedAt 06:53-08:03 UTC): 4 baru vs hot-leg-seen. "
 "RAVE 0x7c40B78992d86EDfFB5553C74dB5EF427100bb95 (08:02:45Z) -> EARLY LEAD (lihat entri RAVE). "
 "0xE3Ad908E4A9680B83A476166b86B852D04ff75Df (08:03:15Z) plain ERC-20, bukan agent-shaped. "
 "0x2cc212f57FBBfD191640655dc6319FFb0E567c1c (07:59:00Z) mint+quote+AGENT_REGISTRY TANPA free view -> bukan S1/S2. "
 "0x0E8010254fD708456A42037f8149B72178af34AA (07:58:36Z) kontrak router/sell, bukan agent-shaped. "
 "0x511E9c9815696F1C04Ffa21E75a66823Bda2cDbF (07:53:52Z, hot-leg 1454 gagal HTTP 400) di-retry: helper delegasi 6 fns, bukan agent-shaped. "
 "16/20 lainnya sudah diproses hot-leg.")
snap["runNote1501_1114_boltbook"] = (
 "Boltbook EN+ZH run 1501 (fetch ~15:07 WIB, EN 25 post + ZH 25 post). BARU: Starcore Miners (STAR) 0xCAc2B707cCf3309aE944a0DB036DFC75aDcC9Be7 "
 "(post EN 15+17: 9 lalu 14/5.000, freeMint, 'no Agent ID') -> dicek: TANPA registry/AgentGate -> BUKAN agent-shaped, bukan lead. "
 "Box Cars Driving Licence (BOXLIC) 0x4084d67c1D7EdAA609DF0c860C57454f46219217 (post ZH 3: 215 minted, first 1.000 Founder) -> dicek: "
 "TANPA free view + TANPA registry -> BUKAN agent-shaped, bukan lead. MAMI 455/885 (post EN 8/ZH 12); "
 "WANGCAI+YUANBAO 188/188 (post EN 23, datt.my 14:40 WIB) — konfirmasi sellout WANGCAI. KRYNT 1.035/1.091 + CPASS 1.507 stalled; "
 "DRAGON freeClaimed 728/888; Trash Bandits 239/1.000; Nero Agent twin 9.900 (FrieAgent). 0 lead baru dari Boltbook selain RAVE (via feed).")
snap["runNote1501_1114_sweep"] = (
 "Sweep EN+ZH run 1501: Agentic Gangster (thecolony.uk, 9 Nov) free mint SOLD OUT 111/111, paid open — excluded; NAOMI GENESIS 0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9 "
 "sudah di snapshot (checked-0xC7Ad-2001), tidak dilaporkan ulang. ZH: AGENT COSMOS 0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69 age-excluded 12 Nov; "
 "Meow Cards 0xb8164afefc53910d7a74cece15a60a9e0c86089e age-excluded 12 Nov; FLICK launchpad 0x824e27094492D588FAf9A419EBD2EB363Cd122c9 "
 "(thecolony.ai, 11 Nov; 0/10.000 shares; deadline 14 Nov 18:37 UTC) -> dicek: mint+costOf+AGENT_REGISTRY TANPA free view -> BUKAN track C (paid-only). "
 "Komplemen 6a/6b: Binance Square + search-index tanpa penyebutan baru; Odaily/PANews tidak dicek rinci run ini (tidak ada sinyal baru dari pencarian). "
 "0 kandidat/lead baru dari sweep.")
snap["runNote1501_1114_bridge"] = (
 "Run 1501: bridge file tidak berubah (mtime 2026-11-08 18:21). Tidak ada kontrak bridge baru untuk re-read rutin pertama; "
 "temuan pelengkap scan tidak ada yang naik tier.")
snap["runNote1501_1114_binanceai"] = (
 "Run 1501: binanceai.fun launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133508775) - "
 "tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge v2 done; interval", round(INTERVAL_MIN, 1), "min; block", BLOCK)
for k in ["NOISE","B77D","AgentBubble","RaceAgents","Ledgera","WANGCAI","YUANBAO","MAMI","INKI","CPASS","Zephyra","DragonAgents","HashcatDepot"]:
    print(k, "->", notes.get(k, "(no velocity note)"))
