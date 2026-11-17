#!/usr/bin/env python3
"""FREE BACOT main run 2026-11-05 21:01 WIB — parent merge.
Updates onchain-snapshot.json from:
- run-2026-11-05-2101-reread-lean.json (route 1 + track C + NJAR + binanceai)
- run-2026-11-05-2101-firstseen-probe.json / scan-firstseen.json (route 4 first-seen)
- parent fresh verification of GHOST + SONO (run in-process values passed below)
- bridge summary run-2026-11-05-2101-bridge.json
Non-null values only overwrite. No preview/mint/tx.
"""
import json, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
r = json.load(open(f"{BASE}/run-2026-11-05-2101-reread-lean.json"))
probe = json.load(open(f"{BASE}/run-2026-11-05-2101-firstseen-probe.json"))
firstseen = json.load(open(f"{BASE}/run-2026-11-05-2101-scan-firstseen.json"))

INT1931, INT2031, PRIOR_INT = 71.28, 36.50, 34.78
READ_BLOCK = r["block"]  # 131830817 @ 21:13:34 WIB

def nz_update(v, rd, keys):
    for k in keys:
        if rd.get(k) is not None:
            v[k] = rd[k]

# ---------- ROUTE 1 velocity + values ----------
vel = {}
for name, rd in r["reread"].items():
    v = s["contracts"].get(name)
    if v is None:
        continue
    last = str(v.get("lastReadWib", ""))
    interval = INT2031 if "2031" in last else INT1931
    new = rd.get("totalSupply")
    if new is None:
        new = rd.get("totalMinted")
    old = v.get("totalSupply")
    if old is None:
        old = v.get("totalMinted")
    prev = v.get("previousTotalSupply")
    prior_rate = None
    if "2031" in last and prev is not None and old is not None:
        prior_rate = (old - prev) / PRIOR_INT
    elif v.get("currentRatePerMin") is not None:
        prior_rate = v.get("currentRatePerMin")
    cur = ratio = None
    passed = False
    d = None
    if new is not None and old is not None:
        d = new - old
        cur = d / interval
        if prior_rate and prior_rate > 0:
            ratio = cur / prior_rate
        passed = (d >= 20 and ratio is not None and ratio >= 1.5)
    if new is not None:
        v["previousTotalSupply"] = old
        if rd.get("totalSupply") is not None:
            v["totalSupply"] = rd["totalSupply"]
        elif rd.get("totalMinted") is not None:
            v["totalMinted"] = rd["totalMinted"]
        v["mintedInInterval"] = d
        v["intervalMinutes"] = interval
        v["currentRatePerMin"] = round(cur, 3) if cur is not None else None
        v["previousRatePerMin"] = round(prior_rate, 3) if prior_rate is not None else None
        v["velocityLegPasses"] = passed
    nz_update(v, rd, ["freeClaimed", "freeMinted", "balanceOf_user", "mintOpen",
                      "mintedBy_user", "freeUsed_user", "canFreeMint_user",
                      "claimedFree_user", "quote_user_1", "costOf_user_1",
                      "mintsLeft_user", "price"])
    # free % recompute where cap known
    cap = v.get("FREE_SUPPLY") or v.get("FREE_CAP") or v.get("FREE_SERVERS_TOTAL") or v.get("freeCap")
    free_now = v.get("freeMinted") if v.get("freeMinted") is not None else v.get("freeClaimed")
    if isinstance(free_now, (int, float)) and isinstance(cap, (int, float)) and cap:
        v["freePctVerified"] = round(free_now / cap * 100, 2)
    v["lastReadBlock"] = READ_BLOCK
    v["lastReadWib"] = "2026-11-05 run 2101"
    vel[name] = {"d": d, "cur": round(cur, 3) if cur is not None else None,
                 "prior": round(prior_rate, 3) if prior_rate is not None else None,
                 "ratio": round(ratio, 2) if ratio is not None else None, "pass": passed}
    v["velocityNote2101"] = ("Run 2101 (blok %d, interval %.1f mnt): %+d token = %.3f/mnt vs prior %.3f = %.2fx -> velocity %s."
                             % (READ_BLOCK, interval, d if d is not None else 0,
                                cur if cur is not None else 0,
                                prior_rate if prior_rate is not None else 0,
                                ratio if ratio is not None else 0,
                                "LOLOS" if passed else "GAGAL"))
    # interval correction note (2031 run overstated interval 231.7 min; chain timestamps prove 34.8 min)
    if "2031" in last:
        v["velocityNote2101"] += (" Koreksi: interval run 2031 yang tercatat 231,7 mnt SALAH — timestamp blok rantai: "
                                  "blok 131821320 = 20:02:17 WIB, blok 131825953 = 20:37:04 WIB = 34,8 mnt; "
                                  "rate prior dihitung ulang dari (old-prev)/34,78 di run ini.")

# AgentBox: decode tuple returns (saleState 7 words, freeEligible 3 words)
ab = s["contracts"].get("AgentBox")
ab_rd = r["reread"].get("AgentBox", {})
def dec_tuple(val, nwords):
    if not isinstance(val, int):
        return None
    hx = format(val, "x").rjust(64 * nwords, "0")
    return [int(hx[i * 64:(i + 1) * 64], 16) for i in range(nwords)]
if ab is not None:
    ss = dec_tuple(ab_rd.get("saleState"), 7)
    fe = dec_tuple(ab_rd.get("freeEligible_user"), 3)
    if ss:
        ab["saleState2101"] = {"opened": ss[0], "maxBoxes": ss[1], "start": ss[2],
                               "end": ss[3], "priceWei": ss[4], "paused": ss[5], "free_": ss[6]}
        ab["totalOpened"] = ss[0]
    if fe:
        ab["freeEligible_user"] = {"ok": fe[0], "hasAgentId": fe[1], "used": fe[2]}
    if ab_rd.get("totalOpened") is not None:
        ab["totalOpened"] = ab_rd["totalOpened"]
    ab["lastReadBlock"] = READ_BLOCK
    ab["lastReadWib"] = "2026-11-05 run 2101"
    ab["runNote2101"] = ("Run 2101: totalOpened %s (2031: 4117); saleState/freeEligible di-decode dari tuple "
                         "di run ini (bukan giant-int). Free %% tetap UNVERIFIED (tanpa free cap); "
                         "slot user %s; tetap early, TIDAK promosi."
                         % (ab.get("totalOpened"), ab.get("freeEligible_user")))

# ---------- TRACK C re-read ----------
tc = s.setdefault("track_c", {})
for key, rd in r.get("track_c", {}).items():
    v = tc.get(key)
    if v is None:
        continue
    for f in ["opened", "launched", "freeMinted", "freeSharesRemaining",
              "freeSharesClaimed_user", "freeClaimed_user", "hasFreeShare_user",
              "totalMinted", "sharesMinted", "saleEnded", "phase"]:
        if rd.get(f) is not None:
            v[f] = rd[f]
    v["lastReadBlock"] = READ_BLOCK
    v["lastReadWib"] = "2026-11-05 run 2101"
njar = r.get("njar", {})
if "NJAR" in tc:
    for f in ["giftsClaimed", "live", "paidSharesSold"]:
        if njar.get(f) is not None:
            tc["NJAR"][f] = njar[f]
    tc["NJAR"]["lastReadBlock"] = READ_BLOCK
    tc["NJAR"]["lastReadWib"] = "2026-11-05 run 2101"
    tc["NJAR"]["runNote2101"] = ("Run 2101: giftsClaimed 500->%s, live=%s, paidSharesSold=%s; "
                                 "gate TETAP GAGAL (sudah dilaporkan blocked); tidak berubah tier."
                                 % (njar.get("giftsClaimed"), njar.get("live"), njar.get("paidSharesSold")))

# ---------- TRACK B ----------
bai = r.get("binanceai", {})
s["runNote2101_binanceai"] = ("Run 2101: BINANCEAI launched=%s, failed=%s, isRefundPhase=%s, "
                             "tokenClaimed(user)=%s — tetap refund/failed, pending_claims kosong, "
                             "tidak dilaporkan ulang." % (bai.get("launched"), bai.get("failed"),
                                                        bai.get("isRefundPhase"), bai.get("tokenClaimed_user")))

# ---------- NEW EARLY LEADS (parent-verified fresh) ----------
s["contracts"]["GHOST"] = {
    "address": "0x474949EBCee9E3A425B6d8033f1E2c8DD3Ae755e",
    "status": "early-lead-reported-2026-11-05",
    "name": "GHOST", "symbol": "GHOST", "kind": "ERC721",
    "totalSupply": 258, "freeMinted": 224, "MAX_SUPPLY": 17500,
    "FREE_SUPPLY": None, "freePctVerified": None,
    "freePctNote": "UNVERIFIED: FREE_SUPPLY() tidak merespons; freeMinted 224 adalah counter, bukan % vs cap.",
    "mintOpen": True, "userBalance": 0, "freeClaimed_user": 0,
    "userSlotNote": "Slot TERBUKA (freeClaimed(user)=0, balance 0) — verifikasi parent run 2101; TIDAK di-preview (early lead).",
    "firstSeenBlock": 131828914, "scanWindow": "131828890-131830889",
    "scanMints": 55, "scanMinters": 55,
    "firstMintBlock": 131826097, "firstMintWib": "2026-11-05 20:38:08 WIB",
    "launchNote": "First mint terverifikasi on-chain blok 131826097 = 2026-11-05 20:38:08 WIB (Ankr getLogs address-filtered; blok jatuh di gap scan run ini, diverifikasi langsung). Umur ~1,3 jam saat lapor, TERVERIFIKASI <=48 jam. Sourcify unverified.",
    "baselineNote": "EARLY lead dilaporkan sekali run 2101. Agent-shape STRICT: REGISTRY() on-chain = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, free views merespons. BUKAN strong lead (free % unverified), BUKAN kandidat (X unverified, velocity belum terhitung — baseline pertama). Naik ke strong hanya bila 3 kaki strong terpenuhi; ke kandidat hanya bila SEMUA kriteria + safety lolos. TIDAK PERNAH auto-mint/preview sebagai early.",
    "xVerified": False, "velocityVerified": False,
    "previousTotalSupply": 258, "mintedInInterval": None, "intervalMinutes": None,
    "currentRatePerMin": None, "previousRatePerMin": None, "velocityLegPasses": False,
    "supplyView": "totalSupply", "lastReadBlock": READ_BLOCK,
    "lastReadWib": "2026-11-05 run 2101",
}
s["contracts"]["Sonofluidic"] = {
    "address": "0x1eF7588Dff561b7390D3AF23d06E684D64217419",
    "status": "early-lead-reported-2026-11-05",
    "name": "Sonofluidic", "symbol": "SONO", "kind": "ERC721",
    "totalSupply": 169, "freeMinted": 169, "FREE_SUPPLY": 2260, "MAX_SUPPLY": 6666,
    "freePctVerified": 7.48,
    "mintOpen": True, "userBalance": 0, "freeClaimed_user": 0,
    "userSlotNote": "Slot TERBUKA (freeClaimed(user)=0, balance 0) — verifikasi parent run 2101; TIDAK di-preview (early lead).",
    "firstSeenBlock": 131829128, "scanWindow": "131828890-131830889",
    "scanMints": 54, "scanMinters": 54,
    "firstMintBlock": 131826574, "firstMintWib": "2026-11-05 20:41:43 WIB",
    "launchNote": "First mint terverifikasi on-chain blok 131826574 = 2026-11-05 20:41:43 WIB (Ankr getLogs address-filtered; blok jatuh di gap scan run ini, diverifikasi langsung). Umur ~1,2 jam saat lapor, TERVERIFIKASI <=48 jam. Sourcify unverified. PRICE 0,00085 BNB (paid lane ada).",
    "baselineNote": "EARLY lead dilaporkan sekali run 2101. Agent-shape STRICT: AGENT_ID() on-chain = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, free views merespons. Free 169/2260 = 7,48% < 25% -> BUKAN strong lead; X unverified; velocity belum terhitung (baseline pertama). Naik ke strong hanya bila 3 kaki strong terpenuhi. TIDAK PERNAH auto-mint/preview sebagai early.",
    "xVerified": False, "velocityVerified": False,
    "previousTotalSupply": 169, "mintedInInterval": None, "intervalMinutes": None,
    "currentRatePerMin": None, "previousRatePerMin": None, "velocityLegPasses": False,
    "supplyView": "totalSupply", "lastReadBlock": READ_BLOCK,
    "lastReadWib": "2026-11-05 run 2101",
}

# ---------- First-seen lainnya: paid-only / free-habis / bukan lead ----------
probe_by_addr = {e["address"].lower(): e for e in probe}
fs_by_addr = {e["address"].lower(): e for e in firstseen.get("nft_first_seen", [])}
PAID_ONLY = ["Gale Sprite Agent", "Obsidian Owl Agent", "Cosmic Rat Agent", "Hex Warden Agent",
             "Logic Node", "OWLORD", "Mirage Raven Agent", "Matrix Core", "BSRC20 Invite Pass"]
FREE_EXHAUSTED = ["Chiguachipmunk", "Cerberuscorgi", "Cablecobra", "Bluetoothbison"]
NOT_EARLY = ["Tampesta", "Proof of Epoch", "Nine Lives", "Wraith Vellum", "erate", "GUARD Card"]

def entry_from_probe(name, addr, status, note):
    e = probe_by_addr.get(addr.lower(), {})
    fs = fs_by_addr.get(addr.lower(), {})
    ent = {"address": addr, "status": status, "name": name,
           "kind": "ERC721", "firstSeenBlock": e.get("first_block_window") or fs.get("first_block"),
           "scanMints": fs.get("mint_count"), "scanMinters": fs.get("distinct_minters"),
           "lastReadBlock": READ_BLOCK, "lastReadWib": "2026-11-05 run 2101",
           "xVerified": False, "velocityVerified": False, "baselineNote": note}
    nv = (e.get("common_selector_probe") or e.get("noarg_views") or {})
    def u(k):
        v = nv.get(k)
        return v.get("uint") if isinstance(v, dict) else None
    for f in ["totalSupply", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY"]:
        if u(f + "()") is not None:
            ent[f] = u(f + "()")
    return ent

for name in PAID_ONLY:
    addr = next((e["address"] for e in probe if e.get("name_scan") == name), None)
    if addr and name not in s["contracts"]:
        s["contracts"][name] = entry_from_probe(
            name, addr, "watchlist-only-paid-only-2026-11-05",
            "Paid-only dari scan run 2101: registry cocok, tanpa free lane (PRICE 0,0005 BNB, template RUNB/SIGI; OWLORD agent 0,0014/public 0,0021 BNB). Bukan lead, bukan kandidat; dicatat agar tidak ditemukan ulang sebagai baru.")
for name in FREE_EXHAUSTED:
    addr = next((e["address"] for e in probe if e.get("name_scan") == name), None)
    if addr:
        ex = s.setdefault("excluded", {})
        if name not in ex:
            ent = entry_from_probe(name, addr, "excluded-free-exhausted-2026-11-05",
                                   "Free pool habis (freeClaimed == FREE_SUPPLY) + umur >48 jam (0 log Transfer di 131773400-131826008, chunked). Bukan lead; dicatat excluded agar tidak ditemukan ulang.")
            ex[name] = ent
for name in NOT_EARLY:
    addr = next((e["address"] for e in probe if e.get("name_scan") == name), None)
    if addr and name not in s["contracts"]:
        extra = ""
        if name == "Tampesta":
            extra = " Free via EIP-712 allowlist (FREE_MINT_TYPEHASH), bukan Agent-ID free lane."
        if name == "Proof of Epoch":
            extra = " mintFreeTo digerbang role minter; ada EXTERNAL_URL di ABI (bahan gate metode H, belum diverifikasi sebagai website evidence)."
        if name == "GUARD Card":
            extra = " Free views merespons tapi tanpa bukti registry -> gagal STRICT."
        s["contracts"][name] = entry_from_probe(
            name, addr, "watchlist-only-not-early-2026-11-05",
            "Bukan early lead (run 2101)." + extra + " Dicatat watchlist-only agar tidak ditemukan ulang sebagai baru.")

# Fleet Genesis suspect (Boltbook post mevy.ai; parent-verified EOA, bukan kontrak)
s.setdefault("excluded", {})["Fleet Genesis"] = {
    "address": "0x5bc4fb61270c2628c93bf507c4ba125b868d37a5",
    "status": "excluded-suspect-not-a-contract-2026-11-05",
    "name": "Fleet Genesis",
    "note": ("Diposting mevy.ai di Boltbook sebagai '512/1.000, free 1 mint per Agent ID'. "
             "Parent-verifikasi run 2101: eth_getCode = 0x (tidak ada kode kontrak), saldo 0 BNB — "
             "alamat EOA biasa, BUKAN kontrak. Angka 512/1.000 tidak terverifikasi. Bukan lead; "
             "dicatat excluded agar tidak muncul lagi sebagai baru."),
    "lastReadWib": "2026-11-05 run 2101",
}

# ---------- Run notes ----------
s["runNote2101"] = (
    "Run 2101 (dijadwalkan 21:01, dieksekusi ~21:11-21:58 WIB). 2 EARLY LEAD BARU (dilaporkan sekali): "
    "GHOST 0x474949EBCee9E3A425B6d8033f1E2c8DD3Ae755e (first mint 20:38:08 WIB, totalSupply 258, freeMinted 224, "
    "FREE_SUPPLY tak merespons -> free % UNVERIFIED, slot user terbuka) + Sonofluidic 0x1eF7588Dff561b7390D3AF23d06E684D64217419 "
    "(first mint 20:41:43 WIB, free 169/2260 = 7,48% <25%, slot terbuka). Keduanya agent-shaped STRICT (registry getter on-chain), "
    "TIDAK di-preview/di-mint (early). 0 kandidat, 0 strong lead baru/promosi, 0 lead track-C, 0 pending claim. "
    "KOREKSI INTERVAL: run 2031 mencatat interval 231,7 mnt — SALAH; timestamp blok rantai: 131821320=20:02:17 WIB, "
    "131825953=20:37:04 WIB (34,8 mnt), 131830817=21:13:34 WIB. Rate prior dihitung ulang dari (old-prev)/34,78; "
    "velocity GAGAL semua run ini (terdekat Forklings 1,21x, PassAgentX 1,13x; Roguefall 3,71x tapi +14 <20; "
    "Driftnauts +233 baseline pertama). AgentGlyph 504/512 = 98,44% (mendekati sellout, slot terbuka, gate tetap FAILED — "
    "tidak dilaporkan ulang). Jolly 69,08%, age-exclude 23:27 WIB malam ini (belum). NJAR giftsClaimed 511. "
    "BINANCEAI tetap refund/failed. Bridge: tidak ada temuan pelengkap baru. Fleet Genesis = EOA, bukan kontrak (excluded suspect). "
    "Scan: window 131828890-131830889 (2000 blok), gap 131826009-131828889 (2881 blok) dilewati; gap kumulatif ~19.245 blok sejak run 1831. "
    "5c: 9 baru dicek, 0 sale-shaped. Feed: 0 sale-shaped. 0 preview/mint/transaksi run ini.")
s["runNote2101_scan"] = (
    "Scan run 2101 SUKSES: window 131828890-131830889 (2000 blok, cap), 80 panggilan Ankr, 0 error, ~15 mnt. "
    "260 kontrak NFT (2247 mint), 673 ERC-20. Watermark 131826008 -> 131830889; seen 8292 -> 8619 (+327). "
    "Gap dilewati 131826009-131828889 (2881 blok); gap kumulatif sejak run 1831 ~19.245 blok (struktural, cap 2000/run).")
s["timestamp_wib"] = "2026-11-05 run 2101"
s["last_run_wib"] = "2026-11-05 run 2101"
s["last_run"] = "2026-11-05-2101"
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(s["contracts"]), "| excluded:", len(s.get("excluded", {})),
      "| track_c:", len(s.get("track_c", {})), "| pending_claims:", len(s.get("pending_claims", {})))
print("GHOST in snapshot:", "GHOST" in s["contracts"], "| SONO:", "Sonofluidic" in s["contracts"])
print("velocity passes:", [k for k, v in vel.items() if v["pass"]])
print("AgentBox freeEligible:", s["contracts"]["AgentBox"].get("freeEligible_user"),
      "| totalOpened:", s["contracts"]["AgentBox"].get("totalOpened"))
