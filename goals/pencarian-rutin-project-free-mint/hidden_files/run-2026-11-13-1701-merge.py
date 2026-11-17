#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 17:01 WIB.
Fresh reads run-2026-11-13-1701-verify.json (block 133332412, ~17:05 WIB, 25 targets)
+ verify-new.json (INKOI + PROMPTPIRATES, block 133333223) + discovery.json
(feed 20, 2 new checked-not-sale-shape; Boltbook EN 44.599 B / ZH 43.099 B, 1 new ZH: PROMPTPIRATES).
previousRatePerMin stays FROZEN (convention question from run 0931 still undecided).
1 EARLY LEAD to report once: Violet Waybill (first mints verified this run).
No new candidate / strong lead / track-B change / track-C lead. SILENT otherwise.
Read-only on-chain; only writes the snapshot. No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-1701.bak")
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-13-1701-verify.json"))
vnew = json.load(open(BASE + "run-2026-11-13-1701-verify-new.json"))
BLOCK = verify.get("block")
INTERVAL = 30
def find_entry(addr):
    a = addr.lower()
    for top in ("contracts", "track_c"):
        for k, v in snap.get(top, {}).items():
            if isinstance(v, dict) and str(v.get("address", "")).lower() == a:
                return top, k, v
            if isinstance(v, dict) and str(v.get("sale", "")).lower() == a:
                return top, k, v
    return None, None, None
def vel(prev, new, prev_rate):
    if prev is None or new is None: return None, None, None, False
    n = new - prev
    rate = round(n / INTERVAL, 2)
    ratio = round(rate / prev_rate, 2) if prev_rate else None
    return n, rate, ratio, bool(ratio is not None and ratio >= 1.5 and n >= 20)
NOTES = {
 "OBFG": "Run 1701: freeMinted 686->687/1230 = 55,9% (+1, 0,03/mnt) -> velocity GAGAL; slot terbuka (freeAvailable=1); umur ~21 jam (saleStart 2026-11-12 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov. Gate website tetap GAGAL (dilaporkan 12 Nov). TIDAK di-preview/TIDAK di-mint. DIAM.",
 "Agentx": "Run 1701: totalMinted 741->744 (+3, 0,10/mnt vs prev 0,18 = 0,56x, <20 token) -> velocity GAGAL; free 744/1111 = 67,0% (<70% strong lead); slot terbuka. Umur ~17,8 jam (mintOpensAt 2026-11-12 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov. Gate website tetap GAGAL. TIDAK di-preview/TIDAK di-mint. DIAM.",
 "Zero": "Run 1701: totalMinted 289->292 (+3, 0,10/mnt vs prev 2,42 = 0,04x) -> velocity GAGAL; free 292/500 = 58,4%; slot TERBUKA. Umur ~9,2 jam (mintOpensAt 07:55 WIB) <24 jam. Website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.",
 "Royal Rush Agents": "Run 1701: freeMinted 809->832/1000 = 83,2% (+23, 0,77/mnt vs rate 1631 0,43 = 1,79x, >=20 token) -> velocity LOLOS run ini. TAPI umur TETAP UNVERIFIED + X UNVERIFIED -> BUKAN strong lead walau >70% + slot terbuka. DIAM (tanpa promosi).",
 "OLIVER": "Run 1701: totalSupply 999, freeMinted 945->949/1000 = 94,9% (+4), freeRemaining 51. Umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.",
 "Slate": "Run 1701: totalSupply 41->45, freeMinted 40->44/480 = 9,2% (+4, 0,13/mnt vs prev 0,77 = 0,17x) -> velocity GAGAL. Umur ~1,4 jam (buka 15:50:57 WIB). Website/X UNVERIFIED, slot user UNVERIFIED (freeClaimed view null). BUKAN kandidat (<50%), BUKAN strong lead (<70%). TIDAK di-preview/TIDAK di-mint. DIAM.",
 "AgentLabs": "Run 1701: totalSpecimens 2261->2270 (+9, 0,30/mnt vs prev 3,298 = 0,09x, <20 token) -> velocity GAGAL; experiment 2 berjalan; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM.",
 "AgentMuse": "Run 1701: freeClaimed 357->371/888 = 41,8% (+14), bookedOf(user) utuh. <50% -> BUKAN kandidat. DIAM.",
 "MECHA": "Run 1701: freeClaimed 1929->1933/4444 = 43,5% (+4). <50%. DIAM.",
 "Pickgrid": "Run 1701: freeMinted 216 FLAT, umur UNVERIFIED. DIAM.",
 "BC1B": "Run 1701: freeCount 467->469 (15,6%). DIAM.",
 "OUTY": "Run 1701: freeSold 28->29/1500 (+1); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.",
 "PX24": "Run 1701: totalSupply 523->524 (+1); umur UNVERIFIED. DIAM.",
 "SKRR": "Run 1701: totalSupply 511->513 (+2); umur UNVERIFIED. DIAM.",
 "ME30": "Run 1701: totalSupply 289 FLAT; umur UNVERIFIED. DIAM.",
 "CY24": "Run 1701: totalSupply 460 FLAT; umur UNVERIFIED. DIAM.",
 "DragonAgent": "Run 1701: totalSupply 981 FLAT; umur UNVERIFIED. DIAM.",
 "HIVE": "Run 1701: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.",
 "JNTM": "Run 1701: freeClaimed 1000/1000 FREE_LOTS_CAP - SELLOUT free pool terkonfirmasi ulang (sudah dilaporkan sekali) -> TIDAK lapor ulang. DIAM.",
 "Mossbound": "Run 1701: totalSupply 326, freeMinted 325/325 SELLOUT terkonfirmasi ulang (sudah dilaporkan sekali) -> TIDAK lapor ulang. DIAM.",
 "Ochre": "Run 1701: totalSupply 211, freeMinted 210/210 SELLOUT terkonfirmasi ulang (sudah dilaporkan sekali) -> TIDAK lapor ulang. DIAM.",
 "NOTV": "Run 1701: totalSupply 0, FREE_SHARES 2000, freeStart 18:00 WIB 13 Nov - belum buka. DIAM.",
 "BinanceAI-mint": "Run 1701: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM.",
}
VIEWS_TO_COPY = ["totalSupply","totalMinted","freeMinted","freeClaimed","freeRemaining",
 "FREE_SUPPLY","FREE_CAP","MAX_SUPPLY","FREE_PER_WALLET","MAX_PER_WALLET","PRICE",
 "saleStart","saleEnd","mintStart","mintOpensAt","saleOpen","mintOpen","isFreeOpen",
 "mintPrice","paidMinted","FREE_MAX","FREE_SHARES","FREE_LOTS_CAP","TOTAL_LOTS",
 "freeLeft","opened","openTime","DOORS_OPEN","openedAt","FREE_OSK","bookedTotal",
 "totalSpecimens","currentExperiment","genesisStart","genesisOpen","START","FREE_END",
 "FREE_FEE","phase","freeOpen","paidOpen","minted","freeSold","paidSold","PAID_CAP",
 "freeCount","freeStart","agentIdRegistry","token","registry"]
for name, rd in verify["reads"].items():
    top, key, ent = find_entry(rd["address"])
    if ent is None:
        print("NOT FOUND in snapshot:", name, rd["address"]); continue
    vw = rd.get("views", {})
    for f in VIEWS_TO_COPY:
        if f in vw and vw[f] is not None:
            ent[f] = vw[f]
    if "balanceOf_user" in vw and vw["balanceOf_user"] is not None:
        ent["balanceOf_user"] = vw["balanceOf_user"]
    ent["lastReadBlock"] = BLOCK
    ent["lastReadWib"] = "2026-11-13 ~17:05 WIB"
    if name in NOTES:
        ent["runNote1701"] = NOTES[name]
    # velocity on the natural counter
    prev_rate = ent.get("previousRatePerMin")
    if name == "Royal Rush Agents":
        n, rate, ratio, passed = vel(809, vw.get("freeMinted"), 0.43)
        ent.update({"mintedInInterval": n, "currentRatePerMin": rate, "velocityRatio": ratio,
                    "velocityLegPasses": passed, "intervalMinutes": INTERVAL})
    elif name in ("Agentx", "Zero"):
        prev = {"Agentx": 741, "Zero": 289}[name]
        n, rate, ratio, passed = vel(prev, vw.get("totalMinted"), prev_rate)
        ent.update({"mintedInInterval": n, "currentRatePerMin": rate, "velocityRatio": ratio,
                    "velocityLegPasses": passed, "intervalMinutes": INTERVAL})
    elif name == "Slate":
        n, rate, ratio, passed = vel(41, vw.get("totalSupply"), 0.77)
        ent.update({"mintedInInterval": n, "currentRatePerMin": rate, "velocityRatio": ratio,
                    "velocityLegPasses": passed, "intervalMinutes": INTERVAL})
    elif name == "OLIVER":
        n, rate, ratio, passed = vel(945, vw.get("freeMinted"), ent.get("previousRatePerMin"))
        ent.update({"mintedInInterval": n, "currentRatePerMin": rate, "velocityRatio": ratio,
                    "velocityLegPasses": passed, "intervalMinutes": INTERVAL})
    elif name == "AgentLabs":
        n, rate, ratio, passed = vel(2261, vw.get("totalSpecimens"), 3.298)
        ent.update({"mintedInInterval": n, "currentRatePerMin": rate, "velocityRatio": ratio,
                    "velocityLegPasses": passed, "intervalMinutes": INTERVAL})
# --- Violet Waybill: upcoming-prelaunch -> EARLY LEAD (first mints verified this run) ---
top, key, vl = find_entry("0x36D9A4392E3d9ff05B6929C82D536367E9c1bc8d")
vw = verify["reads"]["VioletWaybill"]["views"]
vl.update({"status": "early-lead-2026-11-13",
 "totalSupply": vw.get("totalSupply"), "totalMinted": vw.get("totalMinted"),
 "freeMinted": vw.get("freeMinted"), "freeRemaining": vw.get("freeRemaining"),
 "paidMinted": vw.get("paidMinted"), "FREE_SUPPLY": vw.get("FREE_SUPPLY"),
 "FREE_PER_WALLET": vw.get("FREE_PER_WALLET"), "MAX_SUPPLY": vw.get("MAX_SUPPLY"),
 "MAX_PER_WALLET": vw.get("MAX_PER_WALLET"), "PRICE": vw.get("PRICE"),
 "saleStart": vw.get("saleStart"), "saleEnd": vw.get("saleEnd"),
 "saleOpen": vw.get("saleOpen"), "mintOpen": vw.get("mintOpen"),
 "isFreeOpen": vw.get("isFreeOpen"), "isPaidOpen": vw.get("isPaidOpen"),
 "saleClosed": vw.get("saleClosed"),
 "agentIdRegistry": vw.get("agentIdRegistry"),
 "freePct": round(27/1230*100, 1),
 "freeAvailable_user": vw.get("freeAvailable_user"),
 "freeMintedBy_user": vw.get("freeMintedBy_user"),
 "costOf_user_1": vw.get("costOf_user_1"),
 "balanceOf_user": vw.get("balanceOf_user"),
 "hasAgentId_user": vw.get("hasAgentId_user"),
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-13 ~17:05 WIB",
 "mintedInInterval": 27, "currentRatePerMin": None, "velocityRatio": None,
 "velocityLegPasses": False, "intervalMinutes": INTERVAL,
 "firstMintWib": "2026-11-13 ~17:05 WIB (blok 133332412)",
 "note": "Run 1701 EARLY LEAD (dilaporkan sekali run ini): first mints TERVERIFIKASI on-chain run ini (0 di run 1631 -> 27 mint, semua free, blok 133332412; hot-leg 17:06 baca 32). saleStart on-chain 1794563463 = 16:51:03 WIB 13 Nov -> umur ~14 mnt <24 jam TERVERIFIKASI. S1-shape (ABI 77 fns, mint/claimFree/mintFree + quote + free views + agentIdRegistry = registry resmi 0x60B926...22F). Free 27/1230 = 2,2% (BUKAN strong lead <70%, BUKAN kandidat <50%); slot user TERBUKA (freeAvailable=1, costOf=0, freeMintedBy=0, balanceOf=0); velocity: tanpa prev rate -> TIDAK lolos sendirian. Website UNVERIFIED (contractURI base64 tanpa external_link, run 1631); X UNVERIFIED. Early lead TIDAK PERNAH di-preview/di-mint.",
 "runNote1701": "Run 1701: EARLY LEAD dilaporkan sekali (first mints 27 terverifikasi, saleStart 16:51:03 WIB, umur ~14 mnt, free 27/1230 = 2,2%, slot user terbuka, website/X UNVERIFIED). BUKAN kandidat/strong lead. TIDAK di-preview/TIDAK di-mint."})
# --- PROMPTPIRATES: new Boltbook ZH lead, verified on-chain, watchlist-only ---
snap["contracts"]["PROMPTPIRATES"] = {
 "address": "0x5d051572cf9814f613d25d162e914b3c7e2bad05",
 "name": "PROMPTPIRATES", "symbol": "PRMPT", "kind": "ERC721",
 "status": "watchlist-only-2026-11-13",
 "totalSupply": vnew["PROMPTPIRATES"]["views"].get("totalSupply"),
 "freeMinted": vnew["PROMPTPIRATES"]["views"].get("freeMinted"),
 "MAX_SUPPLY": vnew["PROMPTPIRATES"]["views"].get("MAX_SUPPLY"),
 "agentIdRegistry": vnew["PROMPTPIRATES"]["views"].get("agentIdRegistry"),
 "balanceOf_user": vnew["PROMPTPIRATES"]["views"].get("balanceOf_user"),
 "lastReadBlock": vnew.get("block"), "lastReadWib": "2026-11-13 ~17:10 WIB",
 "launchNote": "Umur launch UNVERIFIED (tanpa saleStart/mintOpensAt view; Boltbook ZH post drhmwt.ai 2026-11-13 17:04 WIB: 592/7777, pace ~0,09/mnt). First mint BUKAN run ini (592 sudah termint) -> BUKAN early lead.",
 "baselineNote": "Boltbook ZH lead baru run 1701 (bukan di hot-leg-seen). Agent-shaped (agentIdRegistry = registry resmi 0x60B926...22F + freeMinted counter). Free ~7,6% dari MAX_SUPPLY (FREE_SUPPLY view null, % vs MAX). Slot user UNVERIFIED (freeAvailable/quote view null). BUKAN kandidat (<50%), BUKAN strong lead (<70%), BUKAN early lead. TIDAK dilaporkan sebagai lead; watchlist-only.",
 "runNote1701": "Run 1701: lead Boltbook ZH baru, verifikasi on-chain (totalSupply 593, freeMinted 593, MAX 7777, registry resmi). Umur UNVERIFIED, free ~7,6% MAX, slot user UNVERIFIED -> watchlist-only, TIDAK dilaporkan sebagai lead. DIAM."}
# --- INKOI: known age-excluded (early lead 7 Nov, user holds 1) -> record in age_exclusions ---
ae = snap.setdefault("age_exclusions", [])
if not any("bd4b" in json.dumps(x).lower() for x in ae):
    ae.append({"name": "Ink Koi (INKOI)",
     "address": "0xbd4b4e7189ae9356514664146b0ed683601200a9",
     "track": "A", "reason": "age-excluded",
     "evidence": "Run 1701: post Boltbook ZH vibibiy.ai 17:04 WIB (2.750/2.777 free, 27 tersisa) adalah re-read proyek LAMA, bukan launch baru. Early lead dilaporkan hot-leg 2026-11-07 18:10 WIB; crossed 25% strong-lead lama 2026-11-07 19:32 WIB (697/2777). Umur kini ~6 hari >> 24 jam -> AGE-EXCLUDED. Verifikasi on-chain run ini (blok 133333223): totalSupply 2761, freeMinted 2752/2777 = 99,1%, mintOpen 1; user SUDAH pegang 1 (freeClaimed(user)=1, balanceOf=1) -> slot terpakai. contractURI https://www.inkkoi.ink/contract.json + tokenURI external_url https://www.inkkoi.ink (website pointer ada, belum diverifikasi mencetak kontrak - moot karena umur gugur). TIDAK dilaporkan ulang, TIDAK ditambahkan ke watchlist aktif.",
     "reported_once": False, "removed_wib": "2026-11-13 ~17:10 WIB"})
# --- Sourcify feed new: checked-not-sale-shape ---
for addr, n, va in [("0xc429F18687AcBdE06cF349b1f4DF213c26d499Ff", 6, "2026-11-13T10:03:07Z"),
                    ("0x9e33A9af2fE4010aaFdFB35687b347EA107A2D08", 9, "2026-11-13T10:02:46Z")]:
    key = "Feed-0x" + addr[2:6]
    snap["track_c"][key] = {"address": addr, "name": key,
     "status": "checked-not-sale-shape-2026-11-13",
     "note": f"Run 1701 discovery: Sourcify feed baru (verifiedAt {va}), ABI {n} fns, S1 false (tanpa mint fn, tanpa quote, tanpa free view, tanpa agent ref) - BUKAN lead track-C / early lead. Dicatat saja.",
     "lastReadWib": "2026-11-13 ~17:05 WIB"}
# --- binanceai pending claim note ---
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["runNote1701"] = "Run 1701: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM."
    pc["lastReadWib"] = "2026-11-13 ~17:05 WIB"
snap["timestamp_wib"] = "2026-11-13 ~17:15 WIB"
snap["last_run_wib"] = "2026-11-13 ~17:15 WIB"
snap["runNote1701_1113"] = ("Run 1701: 1 EARLY LEAD baru dilaporkan sekali (Violet Waybill, first mints 27 terverifikasi, "
 "umur ~14 mnt, free 2,2%, slot terbuka, website/X UNVERIFIED). 0 kandidat baru, 0 strong lead baru/promosi, "
 "0 pending claim baru/dibuka. RoyalRush velocity LOLOS run ini (+23, 1,79x) tapi umur UNVERIFIED -> tanpa promosi. "
 "INKOI (post Boltbook 17:04 WIB) adalah re-read proyek lama age-excluded 7 Nov (user sudah pegang 1) -> dicatat age_exclusions, tanpa laporan. "
 "PROMPTPIRATES lead Boltbook ZH baru -> watchlist-only (umur UNVERIFIED, free ~7,6%). "
 "Preflight Ankr 401 (outage sejak 9 Nov); watermark TETAP 132512564; gap ke head ~819.848 blok. "
 "Sourcify feed 20, 2 baru dicek (0xc429, 0x9e33 - bukan sale-shape). Boltbook EN 44.599 B / ZH 43.099 B. "
 "OBFG deadline umur 20:01 WIB, AgentLabs 21:04 WIB, Agentx 23:11 WIB - semua belum lewat.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; snapshot timestamp", snap["timestamp_wib"])
