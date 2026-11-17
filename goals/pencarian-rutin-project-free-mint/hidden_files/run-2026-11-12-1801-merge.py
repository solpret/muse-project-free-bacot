#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-12 18:01 WIB.
Applies readings from legs/verify/retry/reread/freepool JSONs into
onchain-snapshot.json. View-consistent updates only (same view old vs new);
None never overwrites a stored value.
Backs up snapshot to onchain-snapshot.json.bak-1801 first.
Writes run-2026-11-12-1801-merge.json summary. No preview/mint."""
import json, shutil, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-12 18:01 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1801")
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
updated = []

def load(p):
    try: return json.load(open(BASE + p))
    except Exception as e: return {"_err": str(e)}

verify = load("run-2026-11-12-1801-verify.json")
retry = load("run-2026-11-12-1801-retry.json")
reread = load("run-2026-11-12-1801-reread.json")
freepool = load("run-2026-11-12-1801-freepool.json")
legs = load("run-2026-11-12-1801-legs.json")

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
    for f in ["balanceOf_user", "freeClaimed_user", "freeUsed_user", "mintedBy_user",
              "freeMintedBy_user", "freeAvailable_user"]:
        if f in views and views[f] is not None:
            e[f] = views[f]
    e["lastReadBlock"] = block
    e["lastReadWib"] = NOW
    e["runNote1801"] = note + ((" | " + "; ".join(changes)) if changes else " | no change")
    updated.append(name)

# --- verify.json targets (block 133137634), then retry.json overrides (block 133137634)
NAME_FIX = {"Stampooor": "Stampooor Stamp Packs", "0x2e50": "0x2e50",
            "Kongtou-AirdropCnNFT": "Kongtou-AirdropCnNFT"}
for name, r in (verify.get("reads") or {}).items():
    if name in ("binanceai-mint", "RigForge"): continue
    apply(NAME_FIX.get(name, name), r.get("views") or {}, verify.get("block"),
          "Run 1801 verify")
for name, r in (retry.get("reads") or {}).items():
    apply(name, r.get("views") or {}, retry.get("block"), "Run 1801 retry (lean batch)")

# --- reread.json: 63 contracts (block 133137868) — same-view updates only
for name, d in (reread.get("reread") or {}).items():
    if d.get("_batch_fail"): continue
    apply(name, d, reread.get("block"), "Run 1801 reread")
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

# --- MECHA free-pool (freepool.json): free% VERIFIED 40.5% (run 1801 fresh reads)
m = contracts.get("MECHA", {})
m["freePoolSize"] = 4444
m["freeClaimed"] = 1816
m["totalMinted"] = 1817
m["freePctVerified"] = round(1816 / 4444 * 100, 1)
m["agentShaped"] = "YES via AGENT_ID_REGISTRY() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
m["freeAvailable_user"] = 2
m["freeUsedBy_user"] = 0
m["hasAgentId_user"] = 1
m["velocityNote1801"] = ("Run 1801: verify totalMinted 1815 / freeClaimed 1814 (blok 133149112); "
    "freepool segar freeClaimed 1816 / freePoolSize 4444 = 40,9% (blok ~133150269). Interval 1731 "
    "freepool 1799 -> 1816 = +17 dalam ~35 mnt (~0,49/mnt) vs interval sebelumnya ~0,97/mnt -> "
    "rate TURUN -> velocity GAGAL run ini. free% TERVERIFIKASI 40,9% <50% (kaki kandidat gagal) "
    "dan <70% (bukan strong lead). Umur UNVERIFIED, website UNVERIFIED. TETAP watchlist-only. "
    "TIDAK di-preview/di-mint.")
m["lastReadBlock"] = retry.get("block")
m["lastReadWib"] = NOW

# --- OLIVER: 781/1000 = 78.1%, age STILL unverified -> watchlist-only, NOT strong lead
o = contracts.get("Oliver Agents", {})
o["freeMinted"] = 808
o["totalSupply"] = 858
o["freeRemaining"] = 192
o["freePctVerified"] = 80.8
o["ageNote1801"] = ("Run 1801 retry (blok 133150269): freeMinted 808/1000 = 80,8% TERVERIFIKASI (>70%) "
    "+ slot user TERBUKA (balanceOf 0) + website TERVERIFIKASI (oliveragents.pages.dev, run 1301) — "
    "TAPI UMUR TETAP UNVERIFIED (contractURI null run ini; situs tanpa tanggal launch per cek run "
    "1431; Ankr getLogs 401 sehingga koroborasi first-mint tidak mungkin). MASIH watchlist-only, "
    "BUKAN strong lead (kaki umur gagal), BUKAN kandidat. TIDAK di-preview/di-mint.")
o["lastReadBlock"] = retry.get("block")
o["lastReadWib"] = NOW

# --- AGE-EXCLUSIONS run 1801: TIDAK ADA yang baru. DACIT sudah dihapus run 1531
# (bukan run ini); tidak ada kontrak aktif yang melewati 24 jam dalam run ini.
# Deadline terdekat: CRTSAINTS ~20:50 WIB, 0x2e50 ~21:00 WIB, MOONDRILL ~21:10 WIB,
# NAPPER ~22:00 WIB hari ini; OCTOCODER-0x3a84 ~19:30 WIB (checked-not-agent-shaped).
snap["runNote1801_age_exclusions"] = ("Run 1801 AGE-EXCLUSION (log-only, TIDAK dilaporkan ke chat "
    "karena belum pernah dilaporkan sebagai lead): ROBO 0xf8b6867efa31bbd76e10d0bcefbdb22abc6b07fb - "
    "startTime 1794347475 = 2026-11-11 04:51:15 WIB, umur ~37 jam (>=24 jam), belum sold out "
    "(freeMinted 255/1111 = 23,0%, freeRemaining 856, retry blok 133150269). Tidak ada di snapshot, "
    "tidak ditambahkan. DACIT sudah dihapus dari snapshot run 1531 (bukan run ini). Stampooor: "
    "deadline umur 09:00 WIB hari ini LEWAT (mintStart 1794362419 = 2026-11-11 09:00:19 WIB, umur "
    "~33 jam) - age-excluded, sudah dicatat run 1401; entri dipertahankan sebagai holding user "
    "(balance 1, minted-by-user). Deadline terdekat: CRTSAINTS ~20:50 WIB, 0x2e50 ~21:00 WIB, "
    "MOONDRILL ~21:10 WIB, NAPPER ~22:00 WIB hari ini.")

# --- NAPPER: 595 (+7 vs 588 run 1601), mintStart confirmed, window closes 22:00 WIB today
n = contracts.get("NAPPER", {})
n["totalSupply"] = 609
n["mintStart"] = 1794409230
n["ageNote1801"] = ("mintStart 1794409230 terkonfirmasi = 2026-11-11 22:00:30 WIB (umur ~20,2 jam run 1801, "
    "jendela tutup ~22:00 WIB hari ini). Velocity GAGAL: +2 <20 token (607 -> 609). free% TETAP UNVERIFIED "
    "(freeLeft garbage, freeMinted tidak terbaca). Website TERVERIFIKASI run 1431 via (I)+(G). "
    "Watchlist-only, BUKAN strong lead/kandidat.")
n["lastReadBlock"] = retry.get("block")
n["lastReadWib"] = NOW

# --- DRAGON-0xad0d: 513/509 = 57.3%, age UNVERIFIED
dr = contracts.get("DRAGON-0xad0d", {})
dr["totalSupply"] = 521
dr["freeClaimed"] = 517
dr["freePctVerified"] = round(517 / 888 * 100, 1)
dr["ageNote1801"] = ("Umur TETAP UNVERIFIED run 1801 (contractURI base64 JSON tanpa URL/tanggal; "
    "5 view waktu null run 1431; Ankr 401). Website TETAP UNVERIFIED. Velocity GAGAL: +3 <20 "
    "(514 -> 517). Watchlist-only.")
dr["lastReadBlock"] = retry.get("block")
dr["lastReadWib"] = NOW

# --- Stampooor: 917 (+1 vs 916 run 1601), age-excluded already (run 1401)
st = contracts.get("Stampooor Stamp Packs", {})
st["totalMinted"] = 919
st["freeMinted"] = 919
st["ageNote1801"] = ("mintStart 1794362419 = 2026-11-11 09:00:19 WIB -> umur ~33 jam run 1801: "
    "AGE-EXCLUDED (sudah dicatat run 1401; koreksi jam: 09:00 WIB, bukan 13:00 seperti catatan "
    "run 1631). Bal user 1, freeUsed 1 (minted-by-user).")
st["lastReadBlock"] = verify.get("block")
st["lastReadWib"] = NOW

# --- SAINTS family velocity (verify blok 133149112 vs run 1731, interval ~30 mnt):
# CRTSAINTS 146->146 (+0), 0x2e50 137->137 (+0), MOONDRILL 121->121 (+0). Semua <20 -> velocity GAGAL.
# Ketiganya: previousRatePerMin = None (baseline belum tersimpan) -> velocity TIDAK lulus
# (aturan: tanpa rate sebelumnya, catat baseline, jangan lolos). free% ketiganya TETAP UNVERIFIED
# (freeLeft garbage). Umur terverifikasi <24 jam (mintStart 20:50/21:00/21:10 WIB 11 Nov).
# Status tetap early-lead-reported; BUKAN strong lead/kandidat. TIDAK di-preview/di-mint.
for _nm, _old, _new in (("CRTSAINTS", 146, 146), ("0x2e50", 137, 137), ("MOONDRILL", 121, 121)):
    _e = contracts.get(_nm, {})
    if _e:
        _e["totalSupply"] = _new
        _e["velocityNote1801"] = ("Run 1801 verify (blok 133145009): %s->%s (+%d dalam ~30 mnt, "
            "~%.2f/mnt) -> velocity TIDAK lulus (<20 token dalam interval). free%% TETAP UNVERIFIED; "
            "umur terverifikasi <24 jam. Tetap early-lead-reported, BUKAN strong lead/kandidat." % (_old, _new, _new - _old, (_new - _old) / 30.0))
        _e["lastReadBlock"] = verify.get("block")
        _e["lastReadWib"] = NOW

# --- binanceai pending claim: launched()=0 still, refund phase
snap["runNote1801_binanceai"] = ("Run 1801 (blok %s): binanceai-mint launched()=0 TETAP, "
    "freeSharesRemaining 0, FREE_SHARES 2888 - pending claim, fase refund; tidak ada perubahan." % verify.get("block"))

# --- RigForge: openedAt still 0
rg = contracts.get("RigForge", {})
if rg:
    rg["freeClaimed"] = 337
    rg["freeSharesLeft"] = 663
    rg["openedAt"] = 0
    rg["runNote1801"] = "Run 1801: openedAt TETAP 0 (belum buka), freeClaimed 337, freeSharesLeft 663 - tidak ada perubahan."
    rg["lastReadBlock"] = verify.get("block")
    rg["lastReadWib"] = NOW

# --- NEW entries run 1801: RunicKey (hot-leg early lead), Thor, Vexa (watchlist-only) ---
contracts["RunicKey"] = {
    "name": "RunicKey", "address": "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4",
    "status": "early-lead-reported-2026-11-12",
    "source": "hot-leg-1754 (dilaporkan sekali sebagai EARLY LEAD oleh hot leg ~18:01 WIB; run ini TIDAK lapor ulang)",
    "totalSupply": 130, "totalMinted": 130, "freeMinted": 130, "FREE_SUPPLY": 325,
    "MAX_SUPPLY": 500, "mintOpen": 1, "freeRemaining": 195, "paidMinted": 0,
    "saleStart": 1794481219, "MAX_PER_WALLET": 21, "price": 500000000000000,
    "balanceOf_user": 0, "mintedBy_user": 0, "freeMintedBy_user": 0,
    "freePctVerified": round(130 / 325 * 100, 1),
    "ageNote1801": "saleStart 1794481219 = 2026-11-12 18:00:19 WIB, umur TERVERIFIKASI <24 jam. "
        "Velocity SANGAT CEPAT: 22 free mint ~18:01 (hot leg) -> 130 free mint ~18:12 (retry run ini, "
        "blok 133150269) = +108 dalam ~11 mnt. BUKAN kandidat (40,0% < 50%) dan BUKAN strong lead "
        "(<70%). Website BELUM terverifikasi (contractURI base64 JSON tanpa external_link; metode "
        "A-N belum dijalankan). Early lead TIDAK PERNAH di-preview/di-mint.",
    "lastReadBlock": retry.get("block"), "lastReadWib": NOW}
contracts["Thor"] = {
    "name": "Thor", "address": "0x8aa9d6a09caf475593852e681b58b26dc94edd56",
    "status": "watchlist-only-age-unverified-2026-11-12",
    "source": "boltbook-zh-1801 (baru vs hot-leg-seen; post Boltbook klaim 4.901/5.001 free 98,0%)",
    "totalSupply": 4901, "totalMinted": 4901, "MAX_SUPPLY": 5000, "mintOpen": None,
    "balanceOf_user": 0, "mintedBy_user": 0,
    "freePctNote1801": "free% UNVERIFIED: freeMinted()/free views tidak terbaca (revert/null) di verify+retry; "
        "angka 98% Boltbook TIDAK dipakai sebagai verifikasi. Umur UNVERIFIED (tidak ada saleStart/"
        "mintStart terbaca; Ankr 401). Owner sama dengan Cobalt/Vexa (0xe0808a338d96171fa9bde4d4d1897692392a0cbb) "
        "- Cobalt status watchlist-only-age-unverified, BUKAN discarded. Website UNVERIFIED "
        "(Sourcify UNVERIFIED per post; contractURI null). Watchlist-only, BUKAN strong lead/kandidat.",
    "lastReadBlock": retry.get("block"), "lastReadWib": NOW}
contracts["Vexa"] = {
    "name": "Vexa", "address": "0x6c17af4fac529e5679686e121a75e85b1063cd45",
    "status": "watchlist-only-age-unverified-2026-11-12",
    "source": "boltbook-en-1801 via browser.open (sudah di hot-leg-seen; post Boltbook klaim 4.900/5.000 free 98,0%)",
    "totalSupply": 4900, "totalMinted": 4900, "MAX_SUPPLY": 5000, "mintOpen": None,
    "balanceOf_user": 0, "mintedBy_user": 0,
    "freePctNote1801": "free% UNVERIFIED: freeMinted()/free views tidak terbaca (revert/null) di retry; "
        "angka 98% Boltbook TIDAK dipakai sebagai verifikasi. Umur UNVERIFIED. Owner sama dengan "
        "Cobalt/Thor (0xe0808a338d96171fa9bde4d4d1897692392a0cbb). Website UNVERIFIED. "
        "Watchlist-only, BUKAN strong lead/kandidat.",
    "lastReadBlock": retry.get("block"), "lastReadWib": NOW}

snap["last_run"] = NOW
snap["last_run_note"] = ("Run 1801: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. Pre-flight FAIL (Ankr 401) - scan fast-fail, "
    "watermark tetap 132512564; verify 529,7 dtk (blok 133149112, 13 BATCH-FAIL, RPC terdegradasi), "
    "retry 207,7 dtk (blok 133150269, 13/13 terbaca), reread 180,9 dtk (blok 133151251). Feed 20 "
    "kontrak, 7 baru vs hot-leg-seen (2 ERC20 biasa, 6 shape-check error transport); Boltbook EN "
    "0 byte (fetch gagal 2x, dibaca via browser.open) / ZH 42.233 byte, 13 alamat, 1 baru (Thor); "
    "Bridge 116 kontrak, 0 not-in-snapshot, 7 same_owner_discarded. RunicKey EARLY LEAD sudah "
    "dilaporkan hot-leg 17:54 (130/325 = 40,0%, saleStart 18:00:19 WIB, slot terbuka) - masuk "
    "snapshot, TIDAK dilaporkan ulang; Thor/Vexa watchlist-only (free% + umur UNVERIFIED, total "
    "4901/4900 dari 5000, owner sama dengan Cobalt 0xe0808a33...); ROBO age-excluded ~37 jam "
    "(log-only, belum pernah dilaporkan). MECHA velocity GAGAL (+17, rate turun) dan free% 40,9% "
    "<50%; OLIVER 80,8% tapi umur unverified; NAPPER 609, jendela tutup ~22:00 WIB; SAINTS flat "
    "(+0/+0/+0) -> velocity GAGAL; reread max +5 (Cosmic Sentinel, view-konsisten); track_c: "
    "11-11 freeMinted 692->704 (+12), DROID tetap 748, VISION/0x5f76 naik tipis. Sweep: semua "
    "sudah dikenal (MOLT/RIGBYPASS/PixelFox/Coracle excluded, First-Dollar Grove age-excluded, "
    "LeadLoop watchlist lama, AGENT MAO paused, AGENT COSMOS age-excluded).")
with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
summary = {"run": NOW, "updated": sorted(set(updated)), "n_updated": len(set(updated)),
           "verify_block": verify.get("block"), "retry_block": retry.get("block"),
           "reread_block": reread.get("block"),
           "legs_feed_new": legs.get("feed_new"), "legs_boltbook_new": legs.get("boltbook_new"),
           "legs_bridge": legs.get("bridge")}
json.dump(summary, open(BASE + "run-2026-11-12-1801-merge.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
print("MERGE DONE")
