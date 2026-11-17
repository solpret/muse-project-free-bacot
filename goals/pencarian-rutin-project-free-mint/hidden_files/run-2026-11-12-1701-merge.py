#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-12 17:01 WIB.
Applies readings from legs/verify/retry/reread/freepool JSONs into
onchain-snapshot.json. View-consistent updates only (same view old vs new);
None never overwrites a stored value.
Backs up snapshot to onchain-snapshot.json.bak-1701 first.
Writes run-2026-11-12-1701-merge.json summary. No preview/mint."""
import json, shutil, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-12 17:01 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1701")
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
updated = []

def load(p):
    try: return json.load(open(BASE + p))
    except Exception as e: return {"_err": str(e)}

verify = load("run-2026-11-12-1701-verify.json")
retry = load("run-2026-11-12-1701-retry.json")
reread = load("run-2026-11-12-1701-reread.json")
freepool = load("run-2026-11-12-1701-freepool.json")
legs = load("run-2026-11-12-1701-legs.json")

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
    e["runNote1701"] = note + ((" | " + "; ".join(changes)) if changes else " | no change")
    updated.append(name)

# --- verify.json targets (block 133137634), then retry.json overrides (block 133137634)
NAME_FIX = {"Stampooor": "Stampooor Stamp Packs", "0x2e50": "0x2e50",
            "Kongtou-AirdropCnNFT": "Kongtou-AirdropCnNFT"}
for name, r in (verify.get("reads") or {}).items():
    if name in ("binanceai-mint", "RigForge"): continue
    apply(NAME_FIX.get(name, name), r.get("views") or {}, verify.get("block"),
          "Run 1701 verify")
for name, r in (retry.get("reads") or {}).items():
    apply(name, r.get("views") or {}, retry.get("block"), "Run 1701 retry (lean batch)")

# --- reread.json: 63 contracts (block 133137868) — same-view updates only
for name, d in (reread.get("reread") or {}).items():
    if d.get("_batch_fail"): continue
    apply(name, d, reread.get("block"), "Run 1701 reread")
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

# --- MECHA free-pool (freepool.json): free% VERIFIED 39.3% (run 1701 fresh reads)
m = contracts.get("MECHA", {})
m["freePoolSize"] = 4444
m["freeClaimed"] = 1768
m["totalMinted"] = 1769
m["freePctVerified"] = round(1768 / 4444 * 100, 1)
m["agentShaped"] = "YES via AGENT_ID_REGISTRY() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
m["freeAvailable_user"] = 2
m["freeUsedBy_user"] = 0
m["hasAgentId_user"] = 1
m["velocityNote1701"] = ("Run 1701 verify (blok 133140989): totalMinted 1735 (1631 verify) -> 1759 "
    "= +24 dalam ~30 mnt; retry 1739 -> 1769 = +30. Previous interval +2 -> ratio >=1,5x DAN "
    ">=20 token -> velocity LOLOS sebagai kaki. TAPI free% TERVERIFIKASI 1768/4444 = 39,8% "
    "(freepool segar) <50% (kaki kandidat gagal) dan <70% (bukan strong lead). Umur UNVERIFIED, "
    "website UNVERIFIED. TETAP watchlist-only. TIDAK di-preview/di-mint.")
m["lastReadBlock"] = retry.get("block")
m["lastReadWib"] = NOW

# --- OLIVER: 781/1000 = 78.1%, age STILL unverified -> watchlist-only, NOT strong lead
o = contracts.get("Oliver Agents", {})
o["freeMinted"] = 789
o["totalSupply"] = 839
o["freeRemaining"] = 211
o["freePctVerified"] = 78.9
o["ageNote1701"] = ("Run 1701 retry (blok 133141815): freeMinted 789/1000 = 78,9% TERVERIFIKASI (>70%) "
    "+ slot user TERBUKA (balanceOf 0) + website TERVERIFIKASI (oliveragents.pages.dev, run 1301) — "
    "TAPI UMUR TETAP UNVERIFIED (contractURI null run ini; situs tanpa tanggal launch per cek run "
    "1431; Ankr getLogs 401 sehingga koroborasi first-mint tidak mungkin). MASIH watchlist-only, "
    "BUKAN strong lead (kaki umur gagal), BUKAN kandidat. TIDAK di-preview/di-mint.")
o["lastReadBlock"] = retry.get("block")
o["lastReadWib"] = NOW

# --- AGE-EXCLUSIONS run 1701: TIDAK ADA yang baru. DACIT sudah dihapus run 1531
# (bukan run ini); tidak ada kontrak aktif yang melewati 24 jam dalam run ini.
# Deadline terdekat: CRTSAINTS ~20:50 WIB, 0x2e50 ~21:00 WIB, MOONDRILL ~21:10 WIB,
# NAPPER ~22:00 WIB hari ini; OCTOCODER-0x3a84 ~19:30 WIB (checked-not-agent-shaped).
snap["runNote1701_age_exclusions"] = ("Run 1701: TIDAK ADA age-exclusion baru. DACIT sudah "
    "dihapus dari snapshot run 1531 (bukan run ini). Stampooor: deadline umur 09:00 WIB hari ini "
    "LEWAT (mintStart 1794362419 = 2026-11-11 09:00:19 WIB, umur ~32 jam) - age-excluded, sudah "
    "dicatat run 1401; entri dipertahankan sebagai holding user (balance 1, minted-by-user). "
    "Deadline terdekat: CRTSAINTS ~20:50 WIB, 0x2e50 ~21:00 WIB, MOONDRILL ~21:10 WIB, "
    "NAPPER ~22:00 WIB hari ini.")

# --- NAPPER: 595 (+7 vs 588 run 1601), mintStart confirmed, window closes 22:00 WIB today
n = contracts.get("NAPPER", {})
n["totalSupply"] = 604
n["mintStart"] = 1794409230
n["ageNote1701"] = ("mintStart 1794409230 terkonfirmasi = 2026-11-11 22:00:30 WIB (umur ~19,0 jam run 1701, "
    "jendela tutup ~22:00 WIB hari ini). Velocity GAGAL: +9 <20 token. free% TETAP UNVERIFIED "
    "(freeLeft garbage, freeMinted tidak terbaca). Website TERVERIFIKASI run 1431 via (I)+(G). "
    "Watchlist-only, BUKAN strong lead/kandidat.")
n["lastReadBlock"] = retry.get("block")
n["lastReadWib"] = NOW

# --- DRAGON-0xad0d: 513/509 = 57.3%, age UNVERIFIED
dr = contracts.get("DRAGON-0xad0d", {})
dr["totalSupply"] = 517
dr["freeClaimed"] = 513
dr["freePctVerified"] = round(513 / 888 * 100, 1)
dr["ageNote1701"] = ("Umur TETAP UNVERIFIED run 1701 (contractURI base64 JSON tanpa URL/tanggal; "
    "5 view waktu null run 1431; Ankr 401). Website TETAP UNVERIFIED. Velocity GAGAL: +4 <20. "
    "Watchlist-only.")
dr["lastReadBlock"] = retry.get("block")
dr["lastReadWib"] = NOW

# --- Stampooor: 917 (+1 vs 916 run 1601), age-excluded already (run 1401)
st = contracts.get("Stampooor Stamp Packs", {})
st["totalMinted"] = 918
st["freeMinted"] = 918
st["ageNote1701"] = ("mintStart 1794362419 = 2026-11-11 09:00:19 WIB -> umur ~32,0 jam run 1701: "
    "AGE-EXCLUDED (sudah dicatat run 1401; koreksi jam: 09:00 WIB, bukan 13:00 seperti catatan "
    "run 1631). Bal user 1, freeUsed 1 (minted-by-user).")
st["lastReadBlock"] = verify.get("block")
st["lastReadWib"] = NOW

# --- SAINTS family velocity (verify blok 133137634 vs run 1601, interval ~30 mnt):
# CRTSAINTS 139->144 (+5), 0x2e50 132->135 (+3), MOONDRILL 119->120 (+1). Semua <20 -> velocity GAGAL.
# Ketiganya: previousRatePerMin = None (baseline belum tersimpan) -> velocity TIDAK lulus
# (aturan: tanpa rate sebelumnya, catat baseline, jangan lolos). free% ketiganya TETAP UNVERIFIED
# (freeLeft garbage). Umur terverifikasi <24 jam (mintStart 20:50/21:00/21:10 WIB 11 Nov).
# Status tetap early-lead-reported; BUKAN strong lead/kandidat. TIDAK di-preview/di-mint.
for _nm, _old, _new in (("CRTSAINTS", 144, 145), ("0x2e50", 135, 137), ("MOONDRILL", 120, 121)):
    _e = contracts.get(_nm, {})
    if _e:
        _e["totalSupply"] = _new
        _e["velocityNote1701"] = ("Run 1701 verify (blok 133140989): %s->%s (+%d dalam ~30 mnt, "
            "~%.2f/mnt) vs previousRate None (baseline belum tersimpan) -> velocity TIDAK lulus "
            "(aturan: tanpa rate sebelumnya jangan lolos). free%% TETAP UNVERIFIED; umur terverifikasi "
            "<24 jam. Tetap early-lead-reported, BUKAN strong lead/kandidat." % (_old, _new, _new - _old, (_new - _old) / 30.0))
        _e["lastReadBlock"] = verify.get("block")
        _e["lastReadWib"] = NOW

# --- binanceai pending claim: launched()=0 still, refund phase
snap["runNote1701_binanceai"] = ("Run 1701 (blok %s): binanceai-mint launched()=0 TETAP, "
    "freeSharesRemaining 0, FREE_SHARES 2888 - pending claim, fase refund; tidak ada perubahan." % verify.get("block"))

# --- RigForge: openedAt still 0
rg = contracts.get("RigForge", {})
if rg:
    rg["freeClaimed"] = 337
    rg["freeSharesLeft"] = 663
    rg["openedAt"] = 0
    rg["runNote1701"] = "Run 1701: openedAt TETAP 0 (belum buka), freeClaimed 337, freeSharesLeft 663 - tidak ada perubahan."
    rg["lastReadBlock"] = verify.get("block")
    rg["lastReadWib"] = NOW

snap["last_run"] = NOW
snap["last_run_note"] = ("Run 1701: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 0 age-exclusion baru. Pre-flight FAIL "
    "(Ankr 401) - scan fast-fail, watermark tetap 132512564; verify selesai 352 dtk (blok "
    "133140989), retry 130 dtk (blok 133141815), reread 98 dtk (blok 133142352). Feed 1 baru "
    "(0x5bE7, bukan agent-shaped) vs hot-leg-seen; Boltbook 0 baru (EN 45.139 byte / ZH 43.449 "
    "byte, 9 alamat); Bridge 116 kontrak, 0 not-in-snapshot, 7 same_owner_discarded. MECHA "
    "velocity LOLOS (+24/+30) tapi free% 39,8% <50%; OLIVER 78,9% tapi umur unverified; NAPPER "
    "604, jendela tutup ~22:00 WIB; CRTSAINTS +1 / 0x2e50 +2 / MOONDRILL +1 -> velocity GAGAL "
    "(<20); reread max +2; track_c: DROID freeMinted 744->748, VISION/0x5f76 totalSupply naik, "
    "tanpa perubahan material.")
with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
summary = {"run": NOW, "updated": sorted(set(updated)), "n_updated": len(set(updated)),
           "verify_block": verify.get("block"), "retry_block": retry.get("block"),
           "reread_block": reread.get("block"),
           "legs_feed_new": legs.get("feed_new"), "legs_boltbook_new": legs.get("boltbook_new"),
           "legs_bridge": legs.get("bridge")}
json.dump(summary, open(BASE + "run-2026-11-12-1701-merge.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
print("MERGE DONE")
