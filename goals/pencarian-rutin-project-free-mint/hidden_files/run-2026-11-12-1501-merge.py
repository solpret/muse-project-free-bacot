#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-12 15:01 WIB.
Applies readings from legs/verify/retry/reread/freepool JSONs into
onchain-snapshot.json. View-consistent updates only (same view old vs new);
None never overwrites a stored value.
Backs up snapshot to onchain-snapshot.json.bak-1501 first.
Writes run-2026-11-12-1501-merge.json summary. No preview/mint."""
import json, shutil, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-12 15:01 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1501")
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
updated = []

def load(p):
    try: return json.load(open(BASE + p))
    except Exception as e: return {"_err": str(e)}

verify = load("run-2026-11-12-1501-verify.json")
retry = load("run-2026-11-12-1501-retry.json")
reread = load("run-2026-11-12-1501-reread.json")
freepool = load("run-2026-11-12-1501-freepool.json")
legs = load("run-2026-11-12-1501-legs.json")

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
    e["runNote1501"] = note + ((" | " + "; ".join(changes)) if changes else " | no change")
    updated.append(name)

# --- verify.json targets (block 133124926), then retry.json overrides (block 133125696)
NAME_FIX = {"Stampooor": "Stampooor Stamp Packs", "0x2e50": "0x2e50",
            "Kongtou-AirdropCnNFT": "Kongtou-AirdropCnNFT"}
for name, r in (verify.get("reads") or {}).items():
    if name in ("binanceai-mint", "RigForge"): continue
    apply(NAME_FIX.get(name, name), r.get("views") or {}, verify.get("block"),
          "Run 1501 verify")
for name, r in (retry.get("reads") or {}).items():
    apply(name, r.get("views") or {}, retry.get("block"), "Run 1501 retry (lean batch)")

# --- reread.json: 63 contracts (block 133126087) — same-view updates only
for name, d in (reread.get("reread") or {}).items():
    if d.get("_batch_fail"): continue
    apply(name, d, reread.get("block"), "Run 1501 reread")
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

# --- MECHA free-pool (freepool.json): free% VERIFIED 38.7%
m = contracts.get("MECHA", {})
m["freePoolSize"] = 4444
m["freeClaimed"] = 1719
m["totalMinted"] = 1720
m["freePctVerified"] = round(1719 / 4444 * 100, 1)
m["agentShaped"] = "YES via AGENT_ID_REGISTRY() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
m["freeAvailable_user"] = 2
m["freeUsedBy_user"] = 0
m["hasAgentId_user"] = 1
m["velocityNote1501"] = ("Run 1501: totalMinted 1712 (~14:52) -> 1720 (~15:2x) = +8 in ~30 mnt "
    "= 0.27/mnt vs prev 1.55/mnt = 0.17x AND <20 token -> velocity GAGAL. "
    "TETAP watchlist-only: free% 38.7% <50% (kaki kandidat gagal), umur UNVERIFIED, website UNVERIFIED.")
m["lastReadBlock"] = retry.get("block")
m["lastReadWib"] = NOW

# --- OLIVER: 758/1000 = 75.8%, age STILL unverified -> watchlist-only, NOT strong lead
o = contracts.get("Oliver Agents", {})
o["freeMinted"] = 758
o["totalSupply"] = 758
o["freeRemaining"] = 242
o["freePctVerified"] = 75.8
o["ageNote1501"] = ("Run 1501 deep-dive diulang: 5 view waktu SEMUA null, contractURI null, "
    "situs oliveragents.pages.dev dicek ulang run 1431 - TIDAK ada tanggal launch; "
    "Ankr getLogs 401. UMUR TETAP UNVERIFIED -> MASIH watchlist-only, BUKAN strong lead "
    "(kaki umur gagal) walau free% 75.8% >70% + slot user TERBUKA. TIDAK di-preview/di-mint.")
o["lastReadBlock"] = retry.get("block")
o["lastReadWib"] = NOW

# --- DACIT: window closes 15:39:34 WIB today; free% still UNVERIFIED
d = contracts.get("DACIT", {})
d["totalMinted"] = 1727
d["agentFreeUsed"] = 1695
d["mintStart"] = 1794386374
d["ageNote1501"] = ("mintStart 1794386374 = 2026-11-11 15:39:34 WIB terkonfirmasi; jendela 24 jam "
    "TUTUP 15:39:34 WIB hari ini (~15 mnt sesudah run 1501). Bila free% belum terverifikasi "
    "sampai saat itu, ia age-exclude di run 1531/1601.")
d["freePctNote1501"] = ("free% TETAP UNVERIFIED: freeInfo() revert; tidak ada view free-cap di ABI; "
    "status() = [1727, 9999, 0.00095 BNB, mintStart 1794386374, mintEnd 1794818374, 50]; "
    "AGENT_ID() = registry (agent-shaped TERKONFIRMASI); freeUsedByWallet(user) 0.")
d["lastReadBlock"] = retry.get("block")
d["lastReadWib"] = NOW

# --- NAPPER: 569 (+14), mintStart confirmed, window closes 22:00 WIB today
n = contracts.get("NAPPER", {})
n["totalSupply"] = 569
n["mintStart"] = 1794409230
n["ageNote1501"] = ("mintStart 1794409230 terkonfirmasi (umur <24 jam, jendela tutup 22:00 WIB hari ini). "
    "Website TERVERIFIKASI run 1431 via (I)+(G) — tidak diulang run ini.")
n["lastReadBlock"] = retry.get("block")
n["lastReadWib"] = NOW

# --- DRAGON-0xad0d: 494/490 = 55.2%, age UNVERIFIED
dr = contracts.get("DRAGON-0xad0d", {})
dr["totalSupply"] = 494
dr["freeClaimed"] = 490
dr["freePctVerified"] = round(490 / 888 * 100, 1)
dr["ageNote1501"] = ("Umur TETAP UNVERIFIED run 1501 (contractURI base64 JSON tanpa URL/tanggal; "
    "5 view waktu null run 1431; Ankr 401). Website TETAP UNVERIFIED. Watchlist-only.")
dr["lastReadBlock"] = retry.get("block")
dr["lastReadWib"] = NOW

# --- Stampooor: 914 FLAT, age-excluded already (run 1401)
st = contracts.get("Stampooor Stamp Packs", {})
st["totalMinted"] = 914
st["freeMinted"] = 914
st["ageNote1501"] = ("mintStart 1794362419 = 2026-11-11 13:00:19 WIB -> umur ~26,5 jam run 1501: "
    "AGE-EXCLUDED (sudah dicatat run 1401). Bal user 1, freeUsed 1 (minted-by-user).")
st["lastReadBlock"] = verify.get("block")
st["lastReadWib"] = NOW

# --- binanceai pending claim: launched()=0 still, refund phase
snap["runNote1501_binanceai"] = ("Run 1501 (blok %s): binanceai-mint launched()=0 TETAP, "
    "freeSharesRemaining 0, FREE_SHARES 2888 - pending claim, fase refund; tidak ada perubahan." % verify.get("block"))

# --- RigForge: openedAt still 0
rg = contracts.get("RigForge", {})
if rg:
    rg["freeClaimed"] = 337
    rg["freeSharesLeft"] = 663
    rg["openedAt"] = 0
    rg["runNote1501"] = "Run 1501: openedAt TETAP 0 (belum buka), freeClaimed 337, freeSharesLeft 663 - tidak ada perubahan."
    rg["lastReadBlock"] = verify.get("block")
    rg["lastReadWib"] = NOW

snap["last_run"] = NOW
snap["last_run_note"] = ("Run 1501 SILENT: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. Pre-flight FAIL (Ankr 401) - scan fast-fail, "
    "watermark tetap 132512564. Feed 7 baru, semua S1/S2/early false. Boltbook 0 baru. Bridge 0 baru. "
    "MECHA velocity GAGAL (0.17x); OLIVER 75.8% tapi umur unverified; DACIT jendela tutup 15:39:34 WIB.")
with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
summary = {"run": NOW, "updated": sorted(set(updated)), "n_updated": len(set(updated)),
           "verify_block": verify.get("block"), "retry_block": retry.get("block"),
           "reread_block": reread.get("block"),
           "legs_feed_new": legs.get("feed_new"), "legs_boltbook_new": legs.get("boltbook_new"),
           "legs_bridge": legs.get("bridge")}
json.dump(summary, open(BASE + "run-2026-11-12-1501-merge.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
print("MERGE DONE")
