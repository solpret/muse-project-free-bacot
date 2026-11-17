#!/usr/bin/env python3
"""Merge run 1231 (2026-11-08 12:31 WIB) into onchain-snapshot.json + onchain-scan-seen.json.
Read-only wrt chain; writes snapshot + seen file only. Run AFTER the HokiBunny
docs browser check; pass --hokibunny gate-failed|gate-passed (default gate-failed).
Gate-failed = strong lead reported once, NO preview/mint. Gate-passed would only
change the status flag; execution itself is a separate parent step, never here.
"""
import json, sys, copy, datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
HB_STATUS = sys.argv[sys.argv.index("--hokibunny") + 1] if "--hokibunny" in sys.argv else "gate-failed"
NOW_WIB = "2026-11-08 13:35 WIB"
BLOCK = 132340101
INTERVAL = 19.6

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

def idx_by_addr():
    m = {}
    for k, v in contracts.items():
        if isinstance(v, dict):
            a = v.get("address") or (k if isinstance(k, str) and k.startswith("0x") else None)
            if a:
                m[a.lower()] = k
    return m

by_addr = idx_by_addr()

def find_entry(name, addr):
    if addr and addr.lower() in by_addr:
        return by_addr[addr.lower()]
    for k, v in contracts.items():
        if isinstance(v, dict) and v.get("name") == name:
            return k
    return None

def setv(entry, key, val):
    if val is not None:
        entry[key] = val

# ---------- 1. Re-read changes (154) + raw readings ----------
changes = json.load(open(f"{BASE}/run-1231-reread.json"))["changes"]
raw = json.load(open(f"{BASE}/run-2026-11-08-1231-reread.json"))["reread"]
raw_by_addr = {}
for _n, r in raw.items():
    if isinstance(r, dict) and r.get("address"):
        raw_by_addr[r["address"].lower()] = r

n_updated = 0
for ch in changes:
    addr = ch.get("address")
    key = find_entry(ch.get("name"), addr)
    if key is None:
        continue
    e = contracts[key]
    if not isinstance(e, dict):
        continue
    r = raw_by_addr.get(addr.lower(), {}) if addr else {}
    old_rate = e.get("currentRatePerMin")
    setv(e, "totalSupply", ch.get("totalSupply_new"))
    setv(e, "totalMinted", r.get("totalMinted"))
    setv(e, "freeClaimed", ch.get("freeClaimed_new") if ch.get("freeClaimed_new") is not None else r.get("freeClaimed"))
    setv(e, "freeMinted", r.get("freeMinted"))
    setv(e, "FREE_SUPPLY", ch.get("FREE_SUPPLY_new") if ch.get("FREE_SUPPLY_new") is not None else r.get("FREE_SUPPLY"))
    setv(e, "MAX_SUPPLY", r.get("MAX_SUPPLY"))
    setv(e, "mintOpen", r.get("mintOpen"))
    if r.get("balanceOf_user") is not None:
        e["userBalance"] = r["balanceOf_user"]
    minted = ch.get("minted_in_interval")
    if minted is not None:
        if old_rate is not None:
            e["previousRatePerMin"] = old_rate
        e["currentRatePerMin"] = round(minted / INTERVAL, 4)
        e["lastMintedInterval"] = minted
    fc, fs = e.get("freeClaimed"), e.get("FREE_SUPPLY")
    if isinstance(fc, (int, float)) and isinstance(fs, (int, float)) and fs:
        e["freePctVerified"] = round(fc / fs * 100, 2)
    fm, fcap = e.get("freeMinted"), e.get("FREE_CAP")
    if e.get("freePctVerified") is None and isinstance(fm, (int, float)) and isinstance(fcap, (int, float)) and fcap:
        e["freePctVerified"] = round(fm / fcap * 100, 2)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    n_updated += 1

# free_new_reads (Pumpkinfarm 35.24%, CHASTLE freeClaimed 17)
analysis = json.load(open(f"{BASE}/run-2026-11-08-1231-analysis.json"))
for fr in analysis.get("free_new_reads", []):
    key = find_entry(fr.get("name"), None)
    if key is None:
        # try raw by name
        for k, v in contracts.items():
            if isinstance(v, dict) and fr.get("name", "").split("-")[0] in str(v.get("name", "")):
                key = k
                break
    if key is None:
        continue
    e = contracts[key]
    if fr.get("freeClaimed") is not None:
        e["freeClaimed"] = fr["freeClaimed"]
    if fr.get("FREE_SUPPLY") is not None:
        e["FREE_SUPPLY"] = fr["FREE_SUPPLY"]
    if fr.get("freePct") is not None:
        e["freePctVerified"] = fr["freePct"]

# ---------- 2. Velocity: record ratio (no promotion; free%/age unverified) ----------
reread = json.load(open(f"{BASE}/run-1231-reread.json"))
for v in reread.get("velocity_lolos", []):
    key = find_entry(v.get("name"), v.get("address"))
    if key is None:
        continue
    e = contracts[key]
    e["velocityNote1231"] = (
        f"Run 1231: velocity LOLOS {v['ratio']}x ({v['minted']} token / {INTERVAL} mnt, "
        f"rate {v['rate']}/mnt vs baseline {v['baseline_rate']}) TAPI free% + umur UNVERIFIED "
        f"-> BUKAN promosi, dicatat saja."
    )

# ---------- 3. Age exclusions: 22 + MILLION + Bianren = 24 ----------
age_items = list(reread.get("age_excluded", []))
age_items.append({
    "name": "MILLION", "address": "0xD36B54fbd4c9fA99731b52907713c9e1983aD8a4",
    "status": "early-lead-reported-2026-11-06-run0331",
    "launch_wib": "2026-11-06 03:49:26 WIB", "age_hours": 57.4,
    "totalSupply_now": 239, "MAX_SUPPLY": 5500,
    "freeClaimed_now": None, "FREE_SUPPLY": 500, "totalSupply_snap": 239,
})
age_items.append({
    "name": "Bianren", "address": "0xd24A02198e12B35faDE9DD8334Fb7f6333CD05eF",
    "status": "early-lead-reported-2026-11-06",
    "launch_wib": "2026-11-06 11:03:45 WIB", "age_hours": 50.2,
    "totalSupply_now": 55, "MAX_SUPPLY": 10000,
    "freeClaimed_now": None, "FREE_SUPPLY": None, "totalSupply_snap": 55,
})
age_names = []
for a in age_items:
    key = find_entry(a.get("name"), a.get("address"))
    if key is None:
        continue
    e = contracts[key]
    e["status"] = "age-excluded-2026-11-08"
    e["ageExcludedWib"] = NOW_WIB
    e["ageEvidence"] = (
        f"Run 1231: launch TERVERIFIKASI {a.get('launch_wib')} (umur {a.get('age_hours')} jam > 48 jam), "
        f"belum sold out (totalSupply {a.get('totalSupply_now')} < MAX {a.get('MAX_SUPPLY')}), "
        f"freeClaimed {a.get('freeClaimed_now')}, FREE_SUPPLY {a.get('FREE_SUPPLY')}. "
        f"Dihapus dari watchlist aktif per aturan umur 48 jam."
    )
    age_names.append(a.get("name"))

# Galaxy Agents -> sold out (totalMinted 200 = MAX 200), exempt from age rule
gk = find_entry("Galaxy Agents", "0xa388bba8e4ed07043bae8cc68a00e9aec42f72f4")
if gk:
    contracts[gk]["status"] = "sold-out-2026-11-08"
    contracts[gk]["totalMinted"] = 200
    contracts[gk]["MAX_SUPPLY"] = 200
    contracts[gk]["soldOutNote"] = (
        "Run 1231 (cek parent): totalMinted 200 = MAX_SUPPLY 200 -> SOLD OUT, "
        "dikecualikan dari aturan umur 48 jam."
    )

# AgentBox + Agent Wallet: launch verified >48h but sold-out state unreadable -> keep, flag
for nm, addr, launch in [
    ("AgentBox", "0x08393dad165d90e7258501fE1dfb5F3498644011", "2026-11-05 12:47:33 WIB"),
    ("Agent Wallet", "0x1aeEf8218815F7639eA3544D5c57122675A00805", "2026-11-05 21:56:35 WIB"),
]:
    k = find_entry(nm, addr)
    if k:
        contracts[k]["ageNote1231"] = (
            f"Run 1231: launch TERVERIFIKASI {launch} (>48 jam) TAPI status sold-out TIDAK TERBACA "
            f"(semua view None, degradasi RPC) -> TIDAK di-age-exclude run ini; cek ulang run berikut."
        )

# ---------- 4. Sellout lama baru terbaca (derived): free pool exhausted + 0 minted ----------
# Criterion: fresh free read this run (was None/unset before) shows exhaustion, minted_in_interval == 0.
# Exhaustion = freeClaimed>=FREE_SUPPLY, or freeMinted>=FREE_CAP, or totalSupply>=MAX_SUPPLY (all-free cap).
n_sellout_lama = 0
sellout_lama_names = []
for ch in changes:
    if ch.get("minted_in_interval") not in (0, None):
        continue
    addr = ch.get("address")
    key = find_entry(ch.get("name"), addr)
    if key is None:
        continue
    e = contracts[key]
    if not isinstance(e, dict) or str(e.get("status", "")).startswith(("sold-out", "excluded", "minted-by-user")):
        continue
    fc, fs = e.get("freeClaimed"), e.get("FREE_SUPPLY")
    fm, fcap = e.get("freeMinted"), e.get("FREE_CAP")
    ts, mx = e.get("totalSupply"), e.get("MAX_SUPPLY")
    exhausted = (
        (isinstance(fc, (int, float)) and isinstance(fs, (int, float)) and fs and fc >= fs)
        or (isinstance(fm, (int, float)) and isinstance(fcap, (int, float)) and fcap and fm >= fcap)
        or (isinstance(ts, (int, float)) and isinstance(mx, (int, float)) and mx and ts >= mx)
    )
    if exhausted:
        e["status"] = "sold-out-2026-11-08"
        e["soldOutNote"] = (
            "Run 1231: sellout LAMA yang baru terbaca (free view baru bisa dibaca run ini; "
            "minted_in_interval=0; totalSupply sudah sama dengan snapshot). Bukan sellout baru."
        )
        n_sellout_lama += 1
        sellout_lama_names.append(e.get("name"))

# ---------- 5. Track-C changes (8) ----------
for tc in reread.get("track_c_changes", []):
    name = tc.get("name")
    ent = track_c.get(name)
    if ent is None:
        # find by sale address
        for k, v in track_c.items():
            if isinstance(v, dict) and v.get("sale", "").lower() == (tc.get("sale") or "").lower():
                ent = v
                name = k
                break
    if ent is None:
        continue
    for f, chg in (tc.get("changes") or {}).items():
        if isinstance(chg, dict) and "new" in chg:
            ent[f] = chg["new"]
    ent["lastReadBlock"] = BLOCK
    ent["lastReadWib"] = NOW_WIB

# ---------- 6. New discovery entries ----------
def new_contract(addr, name, symbol, status, **kw):
    e = {
        "address": addr, "status": status, "name": name, "symbol": symbol,
        "kind": "ERC721", "totalSupply": kw.get("totalSupply"),
        "totalMinted": kw.get("totalMinted"), "freeClaimed": kw.get("freeClaimed"),
        "freeMinted": kw.get("freeMinted"), "FREE_SUPPLY": kw.get("FREE_SUPPLY"),
        "FREE_CAP": kw.get("FREE_CAP"), "MAX_SUPPLY": kw.get("MAX_SUPPLY"),
        "freePctVerified": kw.get("freePctVerified"), "mintOpen": kw.get("mintOpen"),
        "userBalance": kw.get("userBalance", 0),
        "firstSeenBlock": kw.get("firstSeenBlock"), "firstMintWib": kw.get("firstMintWib"),
        "discovery": kw.get("discovery", ""), "addedRun": "2026-11-08 run 1231",
    }
    e.update({k: v for k, v in kw.items() if k not in e})
    contracts[addr] = e
    return e

new_contract("0x23ff20cd84d16d7c1ce53a29c7d2c726de8cbb3d", "Onyx Agent", None,
             "watchlist-only-2026-11-08",
             totalSupply=4790, totalMinted=4790, MAX_SUPPLY=5000, freePctVerified=None,
             discovery="Boltbook EN front page 2026-11-08 12:49 WIB: 4790/5000 (95,8%); totalSupply 4790 terverifikasi on-chain (bsc-dataseed batch); Sourcify UNVERIFIED; umur/X/website/slot UNVERIFIED -> watchlist saja.",
             note="Template sama 6799 byte dengan Mira/Nova Agent.")
new_contract("0x2a2a3f5d1d1335fc6afa2f2a625934dc3d78dcdc", "Mira Agent", None,
             "watchlist-only-2026-11-08",
             totalSupply=4900, totalMinted=4900, MAX_SUPPLY=5000,
             discovery="Boltbook EN front page 2026-11-08 12:47 WIB: 4900/5000 (98,0%); totalSupply 4900 terverifikasi on-chain; Sourcify UNVERIFIED; umur/X/website/slot UNVERIFIED -> watchlist saja.",
             note="Template sama 6799 byte dengan Onyx/Nova Agent. Snapshot entry 'Mira' 0xa545c7aa... adalah kontrak BERBEDA.")
new_contract("0x0e881e6ba4043156a8da227e917f1015ca70dce1", "Nova Agent", None,
             "watchlist-only-2026-11-08",
             totalSupply=9901, totalMinted=9901, MAX_SUPPLY=10001,
             discovery="Boltbook ZH front page (stale crawl): 9901/10001 (99,0%); totalSupply 9901 terverifikasi on-chain; Sourcify UNVERIFIED; umur/X/website/slot UNVERIFIED -> watchlist saja.",
             note="Template sama 6799 byte dengan Onyx/Mira Agent. Snapshot entry 'NovaAgent' 0xa6909af6... adalah kontrak BERBEDA.")
new_contract("0xdb8a4102c49a41cfaed7673a3f155f19853af5e8", "PANDORA", "PNDR",
             "watchlist-only-2026-11-08",
             totalSupply=263, totalMinted=263,
             firstMintWib="2026-11-08 10:36 WIB",
             discovery="Discovery run 1231: first mint 10:36 WIB, free ~4,7%, pace melemah, gate Agent ID lemah (freeMint lolos tanpa Agent ID) -> watchlist-only, bukan early (agent-shape lemah).",
             note="Age: first mint 10:36 WIB 2026-11-08 (<=48h) tapi % free + slot + website UNVERIFIED.")
new_contract("0x31975837d5c68eea0b66b5fd27de3506c2f109ba", "Ticker Pets", "TPET",
             "watchlist-only-2026-11-08",
             totalSupply=579, totalMinted=579,
             discovery="Discovery run 1231: totalSupply 579; angka free bertentangan antar post; situs tickerpets.xyz belum terverifikasi mencetak kontrak -> watchlist-only.",
             note="Website/slot/umur UNVERIFIED.")
new_contract("0x794ad67a5590c7e5848e49181297f9cc7c6ce00e", "Horus AI", "HORUS",
             "excluded-free-sold-out-2026-11-08",
             totalSupply=2000, totalMinted=2000, FREE_SUPPLY=2000, MAX_SUPPLY=10000, mintOpen=True,
             userBalance=0,
             discovery="Discovery run 1231 + cek parent: totalSupply 2000 = FREE_SUPPLY 2000, mintOpen 1, user belum pernah mint (mintedBy=0) -> free lane PENUH. Dicatat excluded, TIDAK dilaporkan (bukan lead).",
             note="Free pool habis; tidak ada laporan chat.")
new_contract("0xAAEF5BB8A7363B5997F17149d554640DC35f306d", "EMBER", "EMBR",
             "early-lead-reported-2026-11-08",
             totalSupply=41, totalMinted=41, MAX_SUPPLY=5555, mintOpen=None,
             userBalance=0, firstSeenBlock=132339639, firstMintWib="2026-11-08 12:50:54 WIB",
             discovery="Sourcify feed (discovery) + scan window 132339974-132340973 (scan triage): agent-shaped (agentRegistry = registry Agent ID persis, freeMint no-arg, Sourcify exact_match).",
             firstMintNote="First mint TERVERIFIKASI parent run 1231: chunked Ankr getLogs Transfer-from-zero jendela 40000 blok: 41 mint/41 minter, earliest blok 132339639 = 2026-11-08 12:50:54 WIB (timestamp via dataseed). Scan window pertama melihat 12:55:29 - BUKAN first mint sejati.",
             legs1231="Umur TERVERIFIKASI ~20 mnt (<=48h). % free UNVERIFIED (tidak ada free-total view; totalMinted 41). Slot user terbuka (balanceOf 0, mintActive 1). X/website UNVERIFIED. EARLY lead - TIDAK PERNAH di-preview/di-mint.",
             agentShapedNote="agentRegistry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; freeMint() no-arg; Sourcify exact_match.")
new_contract("0x5Ba49f092D83ee86AFa993fD457B6e1Cf53a2458", "Proof Of Human", "POH",
             "early-lead-reported-2026-11-08",
             totalSupply=415, totalMinted=415, MAX_SUPPLY=2500, FREE_SUPPLY=None, mintOpen=None,
             userBalance=0, firstSeenBlock=132340760, firstMintWib="2026-11-08 12:59:19 WIB",
             discovery="Scan window 132339974-132340973 (triage scan run 1231): first-seen sejati, agent-shaped.",
             firstMintNote="First mint TERVERIFIKASI parent run 1231: Ankr getLogs Transfer-from-zero jendela 20000 blok (132324088-132344088, mencakup gap watermark): 415 mint/221 minter, earliest blok 132340760 = 2026-11-08 12:59:19 WIB.",
             legs1231="Umur TERVERIFIKASI ~26 mnt (<=48h). % free UNVERIFIED (tidak ada free-total view; totalSupply 415 campuran free+paid; FREE_LIMIT 1000, MAX_FREE_PER_WALLET 3, PRICE 0,002 BNB). Slot user terbuka (balanceOf 0, freeMintedBy(user) 0, hasAgentId(user) true, saleActive true). X/website UNVERIFIED. EARLY lead - TIDAK PERNAH di-preview/di-mint.",
             agentShapedNote="registry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; hasAgentId(); freeMintedBy(); Sourcify verified.")

# HokiBunny (status set by --hokibunny)
hb_gate = (
    "Gate website METODE (A)-(N) run 1231: (A) alamat kontrak tanpa hasil; (B) Boltbook EN/ZH front page tanpa post HokiBunny; "
    "(C) Sourcify metadata tanpa URL; (D) situs netlify.app ditemukan via metaURI kontrak (bukan tebakan); "
    "(E) owner 0x13333df46ab3e95f4166370d571e7b73aad06370 (grup Hoki Series - metadata tokenURI menyebut X https://x.com/Hokiseries + Telegram https://t.me/Hokiseries); "
    "(F) tidak ada handle kandidat lain untuk dikonfirmasi; (G) pencarian nama proyek tanpa situs lain; "
    "(H) metaURI() = https://hokibunny-mint.netlify.app/ ; (I) tokenURI(1) metadata: external_url situs yang sama + deskripsi cocok persis; "
    "(J) ABI tanpa fungsi website/siteURL/domain/external; (K) GitHub code search butuh auth (limitasi dinyatakan); "
    "(L) BscScan tidak dicek - situs sudah teridentifikasi via metaURI kontrak, hasil Info-tab tidak mengubah verdict standar cetak; "
    "(M) site: filter tanpa hasil; (N) tidak ada hop registry/author-bio. "
    "Dokumen agen situs: /skill.md dan /launch.json keduanya 404 (dikonfirmasi live browser 13:29-13:30 WIB) - tidak ada agent docs di situs. "
    "Situs TIDAK mencetak alamat kontrak persis (footer: 'Contract (BNB Chain): To be announced at launch') "
    "-> menurut standar cetak-kontrak metode (H)/(I), BUKAN website evidence -> GATE GAGAL (scope block, bukan safety failure). "
    "Parameter situs cocok persis dengan kontrak (1111/222/1 per wallet/0,00007 BNB, PRICE on-chain 70000000000000 wei) - dicatat agar user bisa override eksplisit bila mau."
)
hb = new_contract("0xb0C14C75E747DD9cf94D907ff5191425059540aD", "HokiBunny", "HBUNNY",
                  "strong-lead-2026-11-08-gate-failed" if HB_STATUS == "gate-failed" else "strong-lead-2026-11-08-gate-passed",
                  totalSupply=141, totalMinted=141, freeMinted=141, FREE_CAP=222, MAX_SUPPLY=1111,
                  freePctVerified=63.5, mintOpen=True, userBalance=0,
                  firstSeenBlock=132339270, firstMintWib="2026-11-08 12:48:08 WIB",
                  discovery="Sourcify feed (discovery) + scan window 132339974-132340973 (triage scan run 1231): first-seen sejati, agent-shaped.",
                  firstMintNote="First mint TERVERIFIKASI parent run 1231: Ankr getLogs Transfer-from-zero jendela 20000 blok: 115 mint/115 minter, earliest blok 132339270 = 2026-11-08 12:48:08 WIB (timestamp via dataseed). Scan window pertama melihat 12:54:10 - BUKAN first mint sejati.",
                  legs1231="STRONG LEAD (3 kaki): umur TERVERIFIKASI ~22 mnt (<=48h); free 141/222 = 63,5% TERVERIFIKASI (>=25% dan >=50%); slot user TERBUKA (freeCount(user)=0, balanceOf=0, mintOpen=1, FREE_PER_WALLET=1). Velocity TIDAK disyaratkan untuk strong lead. X: handle Hokiseries dari metadata tokenURI (belum dikonfirmasi via browser - X opsional, bukan gate).",
                  agentShapedNote="agentIdRegistry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; freeMint(uint256); freeMinted(); freeCount(address); Sourcify exact_match; PRICE 0,00007 BNB.",
                  gateNote=hb_gate,
                  website="https://hokibunny-mint.netlify.app/",
                  bawNote="Sesi baw LOGOUT saat verifikasi awal run (~12:52 WIB 'Not logged in'), LOGIN ULANG BERHASIL ~12:54 WIB, terverifikasi 'Logged in' 13:12 WIB - baw BUKAN penghambat saat laporan; satu-satunya penghambat adalah gate website.")

# MALTA -> track_c
track_c["AGENT MALTA"] = {
    "sale": "0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0",
    "token": "0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0",
    "status": "track-c-lead-gate-failed-2026-11-08",
    "saleShape": "PASS (S1): mint(uint256 shares, address referrer) + quote(buyer,shares)->(freeShares,costBnb) + freeUsed + agentIdRegistry = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify exact_match (verifiedAt 2026-11-08T05:33:17Z)",
    "name": "AGENT MALTA", "symbol": "MALTA", "decimals": 18,
    "sharesMinted": 137, "freeMinted": 137, "paidShares": 0,
    "totalFreeShares": 137, "totalShares": 137, "MAX_SHARES": 100000,
    "PRICE_wei": 1000000000000000, "TOKENS_PER_SHARE": 1000000000000000000000000,
    "LIQ_TOKENS_PER_SHARE": 800000000000000000000000, "BASE_QUOTA": 10,
    "totalRaised_wei": 0, "mintingOpen": True, "poolOpen": True,
    "userSlot": {"freeUsed": False, "sharesOf": 0, "sharesBought": 0, "quotaOf": 10, "isAgent": True, "balanceOf": 0},
    "quote_user_1": {"freeShares": 1, "costBnb_wei": 0},
    "firstMintWib": "2026-11-08 12:57:21 WIB",
    "firstMintBlock": 132340498,
    "ageNote": "Umur TERVERIFIKASI ~40 mnt saat verifikasi scan (first share mint on-chain 12:57:21 WIB, blok 132340498); waktu launch dinyatakan proyek belum terverifikasi.",
    "leadLegs": "Sale-shape S1 PASS + free pool 137/100000 TERBUKA + slot user TERBUKA (quote(user,1) = 1 share gratis biaya 0, freeUsed false) + umur <=48h TERVERIFIKASI -> TRACK-C LEAD.",
    "website": "https://agentmalta.pages.dev/",
    "gateNote": (
        "Gate website METODE (A)-(N) run 1231: (A) alamat kontrak tanpa hasil; (B) Boltbook post ADA - 'AGENT MALTA LIVE on BNB Chain' oleh adamsaja.ai, b/alpha, ~13:00 WIB, 14 upvote/7 komentar, https://boltbook.fun/p/S7yBY3mJuLr4?lang=en - mencetak alamat kontrak persis sebagai teks + tautan sale page; "
        "(C) Sourcify metadata tanpa URL; (D) situs pages.dev ditemukan via post Boltbook (bukan tebakan); (E) tanpa owner() di ABI - grup deployer tidak dicek; "
        "(F) tidak ada handle X untuk dikonfirmasi; (G) pencarian nama proyek tanpa situs lain; (H) tidak ada contractURI; (I) N/A (ERC-20, tanpa tokenURI); "
        "(J) ABI tanpa fungsi website/siteURL/domain/external; (K) GitHub code search butuh auth (limitasi dinyatakan); "
        "(L) BscScan token page via live browser 13:28 WIB - tab Info hanya 'Click here to update the token information', tanpa Website/Social; "
        "(M) site:vercel.app/pages.dev/deed.page tanpa hasil; (N) tidak ada hop registry/author-bio. "
        "Situs agentmalta.pages.dev TIDAK mencetak alamat kontrak persis sebagai teks (hanya '0x7280...29fc0'; alamat lengkap hanya di href tautan BscScan/Sourcify; field 'Contract: -' kosong di /skill.md dan /launch.json) "
        "-> menurut standar cetak-kontrak metode (G)/(H), BUKAN website evidence -> GATE GAGAL (scope block, bukan safety failure). "
        "Parameter situs cocok persis dengan kontrak (1 share = 1.000.000 MALTA, 100.000 share, share pertama gratis, 0,001 BNB, kuota 10, referral +2 maks +20) - dicatat agar user bisa override eksplisit bila mau."
    ),
    "mintNote": "Mint = mint(shares, referrer); referrer opsional (zero address diizinkan pada keluarga pabrik yang sama - preseden Pacture di Boltbook). TIDAK di-preview/di-mint run ini (gate gagal).",
    "xNote": "Tidak ada handle X proyek yang ditemukan di situs (hanya tautan BscScan + Sourcify). X opsional, bukan gate.",
    "addedRun": "2026-11-08 run 1231",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}

# ---------- 7. binanceai re-check (unchanged) + HIVE ----------
if "binanceai_claim" in snap and isinstance(snap["binanceai_claim"], dict):
    snap["binanceai_claim"]["verified_run"] = "2026-11-08 run 1231"
    snap["binanceai_claim"]["verified_wib"] = NOW_WIB
    snap["binanceai_claim"]["note"] = (
        "Re-check run 1231: tetap fase refund/failed (failed=1, isRefundPhase=1, launched=0, "
        "totalShares 3110, tokenClaimed user 0, saldo TOKEN user 0). SUDAH dilaporkan sekali - TIDAK dilaporkan ulang."
    )
hk = find_entry("HIVE Agents", None)
if hk and isinstance(contracts[hk], dict):
    contracts[hk]["totalSupply"] = 1256
    contracts[hk]["lastReadBlock"] = BLOCK
    contracts[hk]["lastReadWib"] = NOW_WIB

# ---------- 8. Run notes ----------
snap["last_run"] = "free-mint-search 2026-11-08 1231 WIB"
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = NOW_WIB
snap["runNote1231"] = (
    "Run 1231 (2026-11-08, blok reread 132340101, interval 19,6 mnt vs run 1201): "
    "1 STRONG LEAD BARU HokiBunny (free 141/222 = 63,5%, first mint 12:48:08 WIB, slot terbuka) - "
    "dilaporkan sekali; GATE WEBSITE GAGAL (situs hokibunny-mint.netlify.app via metaURI kontrak, parameter cocok persis, "
    "TAPI situs tidak mencetak alamat kontrak - 'Contract: To be announced at launch') -> TIDAK preview/mint. "
    "2 EARLY LEAD BARU: EMBER (first mint 12:50:54 WIB, 41 mint/41 minter) + Proof Of Human (first mint 12:59:19 WIB, 415 mint/221 minter) - dilaporkan sekali, tanpa preview/mint. "
    "1 TRACK-C LEAD BARU AGENT MALTA (quote(user,1) = 1 share gratis biaya 0, pool 137/100000, first mint 12:57:21 WIB) - "
    "GATE WEBSITE GAGAL (situs agentmalta.pages.dev tidak mencetak alamat kontrak - 'Contract: -' di /skill.md dan /launch.json; alamat lengkap hanya di href) -> TIDAK preview/mint. "
    "8 proyek baru watchlist-only (Onyx/Mira/Nova ~96-99%, PANDORA, Ticker Pets) + Horus AI free lane penuh (dicatat sold out, tanpa laporan). "
    "Velocity lolos 5 (Rose Genesis, Sidecoo, MORPHA, AgentVOLT, Alchemister) - semuanya free%+umur UNVERIFIED, bukan promosi. "
    "Sellout baru 0; slot berubah 0; HIVE Agents tetap 1256. "
    f"Age-exclude 24 (22 gelombang 5 Nov + MILLION + Bianren); Galaxy Agents sold out (200/200); AgentBox + Agent Wallet ditahan (sold-out tak terbaca). "
    f"Sellout lama baru terbaca: {n_sellout_lama} ditandai ({', '.join(sellout_lama_names[:10])}{'...' if len(sellout_lama_names) > 10 else ''}). "
    "Track-C: 8 perubahan supply (BNBbaby freeMinted 10338->12456, NIUBI, DROID, 960E-sale, Crack, FUGUI-set1/set2, ORBITA) - bukan perubahan lead. "
    "BinanceAI tetap closed-refund-phase, tidak dilaporkan ulang. Bridge tidak berubah (115 kontrak, 33 seeded Nov 3 sudah dilaporkan; 2 website-pointer Monke Agents/PixelTrump tidak ditambahkan - launch Nov 3 >48 jam, akan age-exclude). "
    "RPC terdegradasi: 127 kontrak + 32 track_c totalSupply None (nilai lama dipertahankan, BUKAN nol). "
    "baw: LOGOUT ~12:39, cek parent 12:52 'Not logged in', LOGIN ULANG BERHASIL ~12:54 WIB, terverifikasi 'Logged in' 13:12 WIB - baw BUKAN penghambat; satu-satunya penghambat eksekusi adalah gate website. "
    "Bug preflight scan: skrip baca body['logs'] padahal bentuk benar body['result']['logs'] (angka 0 artefak parse; panggilan Ankr-nya sukses - pre-flight tetap LULUS). "
    "Catatan deep-dive parent: eth_call historis di endpoint publik BSC gagal 'missing trie node' (state ter-prune) - first-mint HARUS via Ankr getLogs; Ankr getLogs mengembalikan newest-first, pakai min(blockNumber)."
)
snap["runNote1231_scan"] = (
    "Run 1231 scan: pre-flight LULUS 38,5 dtk (head 132340249; angka log 0 = artefak parse skrip, bukan hasil kosong). "
    "Percobaan 1 mati diam-diam saat runtime teardown, percobaan 2 gagal chunk 1 (Ankr connection reset) - keduanya TIDAK memajukan watermark. "
    "Retry ke-3 SUKSES PENUH: window 132339974-132340973 (1000 blok), 20/20 chunk + 167/167 enrich, 167 NFT (163 ERC721 + 4 ERC1155, 652 mint) + 340 ERC-20, 40 panggilan Ankr, 0 error. "
    "Watermark maju 132328744 -> 132340973; skipped gap 132328745-132339973 (11.229 blok; backfill dinonaktifkan user). "
    "Triage 3 first-seen sejati, ketiganya agent-shaped = EARLY lead (HokiBunny, POH, EMBER). Jinli tidak ada di window - tanpa perubahan. "
    "5c: 42 ERC-20 mint_count>=10, 38 sudah dicek, 4 baru dicek, 0 dibuang, 1 HIT S1 (AGENT MALTA); checked 1466 -> 1470."
)

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)

# ---------- 9. Append early leads to scan-seen ----------
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
for addr, src in [
    ("0xb0C14C75E747DD9cf94D907ff5191425059540aD", "scan-1231"),
    ("0x5Ba49f092D83ee86AFa993fD457B6e1Cf53a2458", "scan-1231"),
    ("0xAAEF5BB8A7363B5997F17149d554640DC35f306d", "scan-1231"),
]:
    if addr not in seen:
        seen[addr] = {"first_seen_block": None, "source": src, "run": "2026-11-08-1231"}
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

print(f"MERGE OK: contracts updated={n_updated}, age_excluded={len(age_names)}, sellout_lama={n_sellout_lama}, "
      f"new_contracts=9, track_c_malta=added, seen+3")
print("age_excluded:", ", ".join(age_names))
print("sellout_lama:", ", ".join(sellout_lama_names))
