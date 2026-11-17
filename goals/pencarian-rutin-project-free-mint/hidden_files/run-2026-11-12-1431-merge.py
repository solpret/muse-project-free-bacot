#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-12 14:31 WIB.
Applies readings from legs/verify/retry/reread/pixiu/freepool JSONs + manual
findings (Paw Gang, AGENT COSMOS, AGENT ID card, NAPPER/DACIT website
verification) into onchain-snapshot.json. View-consistent updates only
(same view old vs new); None never overwrites a stored value.
Backs up snapshot to onchain-snapshot.json.bak-1431 first.
Writes run-2026-11-12-1431-merge.json summary. No preview/mint."""
import json, shutil, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-12 14:31 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1431")
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
updated = []

def load(p):
    try: return json.load(open(BASE + p))
    except Exception as e: return {"_err": str(e)}

verify = load("run-2026-11-12-1431-verify.json")
retry = load("run-2026-11-12-1431-retry.json")
reread = load("run-2026-11-12-1431-reread.json")
pixiu = load("run-2026-11-12-1431-pixiu.json")
freepool = load("run-2026-11-12-1431-freepool.json")

FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
          "MAX_SUPPLY", "mintOpen", "mintStart", "saleStart", "saleEnd", "mintEnd",
          "freeSharesLeft", "openedAt", "freeSharesRemaining", "launched",
          "freeRemaining", "paidMinted", "FREE_MAX", "MAX_PER_WALLET", "price", "PRICE"]

def apply(name, views, block, note):
    if not views: return
    e = contracts.get(name)
    if e is None: return
    changes = []
    for f in FIELDS:
        if f in views and views[f] is not None:
            old = e.get(f)
            if old != views[f]:
                changes.append(f"{f}:{old}->{views[f]}")
            e[f] = views[f]
    # user-slot views
    for f in ["balanceOf_user", "freeClaimed_user", "freeUsed_user", "mintedBy_user",
              "freeMintedBy_user", "freeAvailable_user"]:
        if f in views and views[f] is not None:
            e[f] = views[f]
    e["lastReadBlock"] = block
    e["lastReadWib"] = NOW
    e["runNote1431"] = note + ((" | " + "; ".join(changes)) if changes else " | no change")
    updated.append(name)

# --- verify.json targets (block 133121103), then retry.json overrides (block 133122332)
NAME_FIX = {"Stampooor": "Stampooor Stamp Packs", "0x2e50": "0x2e50",
            "Kongtou-AirdropCnNFT": "Kongtou-AirdropCnNFT", "binanceai-mint": None,
            "RigForge": None}
for name, r in (verify.get("reads") or {}).items():
    if name in ("binanceai-mint", "RigForge"): continue
    apply(NAME_FIX.get(name, name), r.get("views") or {}, verify.get("block"),
          "Run 1431 verify")
for name, r in (retry.get("reads") or {}).items():
    apply(name, r.get("views") or {}, retry.get("block"), "Run 1431 retry (lean batch)")

# --- reread.json: 63 contracts (block 133121594) — same-view updates only
for name, d in (reread.get("reread") or {}).items():
    if d.get("_batch_fail"): continue
    apply(name, d, reread.get("block"), "Run 1431 reread")
for name, d in (reread.get("track_c") or {}).items():
    if d.get("_batch_fail"): continue
    e = track_c.get(name)
    if not isinstance(e, dict): continue
    for f in ["totalSupply", "freeMinted", "freeSharesRemaining"]:
        if d.get(f) is not None: e[f] = d[f]
    if d.get("balanceOf_user") is not None: e["balanceOf_user"] = d["balanceOf_user"]
    if d.get("freeClaimed_user") is not None: e["freeClaimed_user"] = d["freeClaimed_user"]
    e["lastReadBlock"] = reread.get("block")
    e["lastReadWib"] = NOW
    updated.append("tc:" + name)

# --- MECHA free-pool (freepool.json): free% VERIFIED 38.5%
m = contracts.get("MECHA", {})
m["freePoolSize"] = 4444
m["freeClaimed"] = 1711
m["totalMinted"] = 1712
m["freePctVerified"] = round(1711 / 4444 * 100, 1)
m["agentShaped"] = "YES via AGENT_ID_REGISTRY() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
m["freeAvailable_user"] = 2
m["freeUsedBy_user"] = 0
m["hasAgentId_user"] = 1
m["velocityNote1431"] = ("Run 1431: totalMinted 1633 (14:01) -> 1712 (~14:52) = +79 in ~51 mnt "
    "= 1.55/mnt vs prev 0.167/mnt = 9.3x AND >=20 token -> velocity LOLOS. "
    "TETAP watchlist-only: free% 38.5% <50% (kaki kandidat gagal), umur UNVERIFIED, website UNVERIFIED.")
m["lastReadBlock"] = retry.get("block")
m["lastReadWib"] = NOW

# --- OLIVER: 736/1000 = 73.6%, age STILL unverified
o = contracts.get("Oliver Agents", {})
o["freeMinted"] = 736
o["totalSupply"] = 736
o["freeRemaining"] = 264
o["freePctInference"] = 73.6
o["ageNote1431"] = ("Run 1431 deep-dive diulang: 5 view waktu SEMUA null "
    "(mintStart/saleStart/START_TIME/startTime/mintOpensAt), contractURI null, "
    "situs oliveragents.pages.dev dicek ulang run ini — TIDAK ada tanggal launch; "
    "Ankr getLogs 401 (first-mint tidak bisa ditarik). UMUR TETAP UNVERIFIED -> "
    "BUKAN strong lead walau >70% + slot terbuka.")
o["lastReadBlock"] = retry.get("block")
o["lastReadWib"] = NOW

# --- NAPPER: website VERIFIED via contractURI -> llms.txt
n = contracts.get("NAPPER", {})
n["totalSupply"] = 555
n["website"] = "https://dreamcompile.pages.dev"
n["websiteEvidence"] = ("VERIFIED run 1431 via method (I)+(G): contractURI() -> "
    "https://dreamcompile.pages.dev/meta/collection.json (external_link https://dreamcompile.pages.dev) "
    "-> /llms.txt prints 'Contract address: 0x3964BFc3354C0d18886dcAD52Abc55C689e6A1d4'. "
    "Site root sendiri TIDAK mencetak kontrak; bukti dari llms.txt situs itu.")
n["ageVerified"] = "YES: mintStart() 1794409230 = 2026-11-11 22:00:30 WIB; jendela 24 jam tutup 2026-11-12 22:00 WIB"
n["freePctNote1431"] = ("free% TETAP UNVERIFIED: freeLeft() nilai sampah, freeClaimed/freeMinted/FREE_SUPPLY null; "
    "totalSupply 555, paidMinted 0. Klaim board ~510/2000 (pihak ketiga) akan jadi ~25.5% — di bawah 50% bila benar.")
n["lastReadBlock"] = retry.get("block")
n["lastReadWib"] = NOW

# --- DACIT: website VERIFIED via contractURI -> dacity-preview.pages.dev
d = contracts.get("DACIT", {})
d["totalMinted"] = 1726
d["agentFreeUsed"] = 1694
d["mintEnd"] = 1794818374
d["website"] = "https://dacity-preview.pages.dev/"
d["websiteEvidence"] = ("VERIFIED run 1431 via method (I): contractURI() external_link "
    "https://dacity-preview.pages.dev/ -> situs (SPA 117.056 byte) mencetak kontrak persis "
    "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd.")
d["agentShaped"] = "YES via AGENT_ID() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
d["ageVerified"] = "YES: mintStart() 1794386374 = 2026-11-11 15:39:34 WIB; jendela 24 jam tutup 2026-11-12 15:39:34 WIB"
d["freePctNote1431"] = ("free% TETAP UNVERIFIED: freeInfo() revert; tidak ada view free-cap di ABI "
    "(freeInfo/freeUsedByHandle/freeUsedByWallet/walletInfo dicoba). agentFreeUsed 1694/1726 totalMinted.")
d["lastReadBlock"] = retry.get("block")
d["lastReadWib"] = NOW

# --- DRAGON-0xad0d: 54.9% verified, age unverified, contractURI has NO external_link
dr = contracts.get("DRAGON-0xad0d", {})
dr["totalSupply"] = 492
dr["freeClaimed"] = 488
dr["freePctVerified"] = round(488 / 888 * 100, 1)
dr["contractURINote1431"] = ("contractURI() base64 JSON ter-decode run 1431: name Dragon Agents, "
    "first 888 free / 0.0002 BNB after — TIDAK ada external_link/website field -> website TETAP UNVERIFIED; umur UNVERIFIED.")
dr["lastReadBlock"] = retry.get("block")
dr["lastReadWib"] = NOW

# --- SYNERGYPASS / Cobalt
sy = contracts.get("SYNERGYPASS", {})
sy["totalMinted"] = 253
sy["freeMinted"] = 253
sy["freePctVerified"] = round(253 / 1111 * 100, 1)
sy["lastReadBlock"] = retry.get("block")
sy["lastReadWib"] = NOW
co = contracts.get("Cobalt Agent", {})
co["totalSupply"] = 4900
co["totalMinted"] = 4900
co["lastReadBlock"] = retry.get("block")
co["lastReadWib"] = NOW

# --- Stampooor: age-excluded (mintStart 2026-11-11 13:00:19 WIB -> 25.5 jam)
st = contracts.get("Stampooor Stamp Packs", {})
st["totalMinted"] = 914
st["freeMinted"] = 914
st["ageNote1431"] = ("mintStart 1794362419 = 2026-11-11 13:00:19 WIB -> umur ~25,5 jam run 1431: AGE-EXCLUDED "
    "(sudah dicatat run 1401); minted-by-user, slot terpakai, bukan promosi.")
st["lastReadBlock"] = verify.get("block")
st["lastReadWib"] = NOW

# --- WFPASS free pool exhausted
wf = contracts.get("WFPASS", {})
if wf:
    wf["totalSupply"] = 502
    wf["totalMinted"] = 502
    wf["freeMinted"] = 500
    wf["FREE_SUPPLY"] = 500
    wf["lastReadBlock"] = verify.get("block")
    wf["lastReadWib"] = NOW

# --- RigForge (track_c) + binanceai note
rg = track_c.get("RigForge", {})
if isinstance(rg, dict):
    rg["freeClaimed"] = 337
    rg["freeSharesLeft"] = 663
    rg["openedAt"] = 0
    rg["lastReadBlock"] = verify.get("block")
    rg["lastReadWib"] = NOW
    rg["runNote1431"] = "Run 1431: openedAt TETAP 0 (belum buka), freeClaimed 337, freeSharesLeft 663 — tidak ada perubahan."
snap["runNote1431_binanceai"] = ("Run 1431 (blok %s): binanceai-mint launched()=0 TETAP, "
    "freeSharesRemaining 0, FREE_SHARES 2888 — pending claim, fase refund; tidak ada perubahan." % verify.get("block"))

# --- NEW: PIXIU Agents (verified on-chain run 1431)
contracts["PIXIU Agents"] = {
    "address": "0x5777c2f59c65003ddebb018517b09f7ba0691202",
    "name": "PIXIU Agents", "symbol": "PIXIU", "kind": "ERC721",
    "status": "watchlist-only-2026-11-12",
    "totalSupply": pixiu.get("summary", {}).get("totalSupply"),
    "freeClaimed": pixiu.get("summary", {}).get("freeClaimed"),
    "FREE_SUPPLY": 888, "MAX_SUPPLY": 1888,
    "freePctVerified": round(325 / 888 * 100, 1),
    "mintOpen": 1, "balanceOf_user": 0, "mintedBy_user": 0,
    "MAX_PER_WALLET": 5, "price": 200000000000000,
    "owner": "0x23f5cdd233925ea83369a495b95f825ed710fbaa",
    "agentShaped": "YES: registry bytes 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F in bytecode (eth_getCode run 1431); same owner as DRAGON-0xad0d",
    "ageNote": ("UNVERIFIED run 1431: 5 view waktu null; contractURI base64 JSON tanpa URL/tanggal; "
        "Sourcify verifiedAt 2026-11-11T22:52:02Z BUKAN launch time (klaim board); Ankr getLogs 401."),
    "website": None,
    "websiteNote": "UNVERIFIED run 1431: tidak ada situs ditemukan (search 'PIXIU Agents' + same-family patterns; poster Boltbook menyatakan tanpa situs resmi/X/pasar terverifikasi).",
    "xNote": "Boltbook discussion EXISTS (agata.ai post h6JU5_m3mHLo ~14:30 WIB, recheck 328/1.888) — discussion evidence ada, akun X proyek belum ditemukan.",
    "velocityNote": "First read run 1431 (329 total / 325 free) — belum ada baseline; pace board ~0,15-0,17/mnt (mendingin).",
    "firstSeenWib": "2026-11-12 14:31 WIB",
    "lastReadBlock": pixiu.get("block"),
    "lastReadWib": NOW,
    "runNote1431": "Run 1431 NEW FINDING (Boltbook front page, agata.ai): watchlist-only — free% 36.6% <50%, umur unverified, website unverified. BUKAN lead/kandidat/strong lead; TIDAK di-preview/di-mint.",
}
# --- NEW: Paw Gang (sold out + age-excluded)
contracts["Paw Gang"] = {
    "address": "0x587C303982187Ec578dF309d27670327b13202F8",
    "name": "Paw Gang", "symbol": "PAWG", "kind": "ERC721",
    "status": "checked-not-lead-age-excluded-sold-out-2026-11-12",
    "totalMinted": 3333, "MAX_SUPPLY": 3333,
    "website": "https://pawgang.pages.dev",
    "ageNote": "AGE-EXCLUDED: mint opened 2026-11-07 13:00 UTC (20:00 WIB, post Colony 2026-11-07T13:19:53Z) -> umur ~4,6 hari run 1431. SOLD OUT: totalMinted 3333/3333 dibaca run 1431.",
    "firstSeenWib": "2026-11-12 14:31 WIB",
    "lastReadBlock": 133122332,
    "lastReadWib": NOW,
    "runNote1431": "Run 1431 sweep EN: dicatat age-excluded + sold out, TIDAK dilaporkan sebagai lead.",
}
# --- NEW: AGENT COSMOS (age-excluded)
contracts["AGENT COSMOS"] = {
    "address": "0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69",
    "name": "AGENT COSMOS", "kind": "ERC721",
    "status": "checked-not-lead-age-excluded-2026-11-12",
    "totalSupply": 5187, "MAX_SUPPLY": 100000, "mintOpen": 1, "balanceOf_user": 0,
    "website": "https://agentcosmos.fun",
    "ageNote": "AGE-EXCLUDED: post launch resmi Colony 2026-11-05T09:03:11Z -> umur ~7 hari run 1431; tidak ada view waktu di kontrak yang terbaca (mintStart null).",
    "firstSeenWib": "2026-11-12 14:31 WIB",
    "lastReadBlock": retry.get("block"),
    "lastReadWib": NOW,
    "runNote1431": "Run 1431 sweep EN: dicatat age-excluded, TIDAK dilaporkan sebagai lead.",
}
# --- NEW: AGENT ID card (sold out)
contracts["AGENT ID card"] = {
    "address": "0x486d0947caa3d70c19e38f6c789489d39291e9e7",
    "name": "AGENT ID", "kind": "ERC721",
    "status": "checked-sold-out-2026-11-12",
    "totalSupply": 3000, "MAX_SUPPLY": 3000, "mintOpen": 1, "balanceOf_user": 0,
    "ageNote": "SOLD OUT run 1431 (3000/3000); post Square 2026-10-25 -> umur ~18 hari, age-excluded juga.",
    "firstSeenWib": "2026-11-12 14:31 WIB",
    "lastReadBlock": retry.get("block"),
    "lastReadWib": NOW,
    "runNote1431": "Run 1431 sweep ZH: dicatat sold out, TIDAK dilaporkan sebagai lead.",
}

snap["last_run_wib"] = NOW
snap["last_run"] = "2026-11-12 14:31 WIB"
snap["last_run_block"] = retry.get("block")
snap["runNote1431"] = (
    "Run 1431 (blok reread %s / retry %s): SILENT — 0 kandidat baru, 0 strong lead baru "
    "(OLIVER 736/1000=73.6%% tapi umur UNVERIFIED; MECHA free%% 38.5%% terverifikasi + velocity LOLOS tapi <50%% + umur/website UNVERIFIED), "
    "0 early lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru, 0 sellout baru. "
    "Preflight Ankr 401 FAST-FAIL (outage sejak 9 Nov); watermark TETAP 132512564. "
    "Feed 20 kontrak, semua shape-checked S1/S2/early false. Boltbook EN 45.468 byte / ZH 43.670 byte, 0 alamat baru. "
    "Bridge 116 kontrak, 0 not-in-snapshot. Temuan baru: PIXIU Agents (watchlist-only, 325/888=36.6%%), "
    "Paw Gang (sold out + age-excluded), AGENT COSMOS (age-excluded), AGENT ID card (sold out). "
    "Website TERVERIFIKASI run ini: NAPPER (llms.txt dreamcompile) + DACIT (dacity-preview.pages.dev). "
    "DACIT jendela 24 jam tutup 15:39:34 WIB hari ini. Tidak ada eksekusi (tidak ada preview/mint)."
    % (reread.get("block"), retry.get("block")))
snap["runNote1431_scan"] = ("Scan run 1431 FAST-FAIL (preflight Ankr HTTP 401 Unauthorized, "
    "kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB; kuota freemium 0 pct s.d. 1 Des 2026). "
    "Scan leg TIDAK dijalankan; watermark TIDAK dimajukan (tetap 132512564); 5c dilewati (tanpa output scan).")
snap["runNote1431_velocity"] = ("Run 1431 velocity: MECHA LOLOS (+79 totalMinted, ~1.55/mnt vs prev 0.167 = 9.3x, >=20 token) "
    "tapi free% 38.5% <50% -> bukan kandidat/strong lead. Cosmic Sentinel flat vs 1401 (510/511, +1). "
    "Skywe Legion FLAT (totalMinted 678 = snapshot 14:01; delta +28 run ini adalah artefak campur view totalSupply-vs-totalMinted, BUKAN kenaikan). "
    "0x7Eb9 flat 1185, Stampooor flat 914 (delta +212/+46 run ini juga artefak campur view; snapshot totalSupply usang). "
    "Semua kontrak lain +0..+3 token -> velocity GAGAL. Track_c tanpa perubahan (DROID 743, FUGUI-set1 423, FUGUI-set2 626, NIUBI 159, 960E 38, Kiko9393 0, Mihao 0, 11-11 692).")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
summary = {"updated_entries": sorted(set(updated)), "n_updated": len(set(updated)),
           "contracts_now": len(contracts), "track_c_now": len(track_c),
           "last_run_block": retry.get("block")}
json.dump(summary, open(BASE + "run-2026-11-12-1431-merge.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
