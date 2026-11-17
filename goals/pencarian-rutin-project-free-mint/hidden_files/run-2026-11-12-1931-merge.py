#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-12 19:31 WIB.
Sources this run ONLY:
- run-2026-11-12-1931-verify.json (34 targets; 22 read, 12 BATCH-FAIL),
- run-2026-11-12-1931-legs.json (feed/Boltbook/bridge),
- sweep EN+ZH + Odaily newsflash (route 3/5b/6).
View-consistent updates only; None never overwrites a stored value.
Batch-fail targets keep stored values (degradation, not zero).
Atomic snapshot write (temp + os.replace); backup to .bak-1931 first.
No preview/mint."""
import json, os, shutil, datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-12 19:31 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1931")
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})

verify = json.load(open(BASE + "run-2026-11-12-1931-verify.json"))
reads = verify["reads"]
block = verify["block"]

addr2key = {}
for k, it in contracts.items():
    if isinstance(it, dict) and it.get("address"):
        addr2key[str(it["address"]).lower()] = k

FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
          "MAX_SUPPLY", "mintOpen", "mintStart", "saleStart", "saleEnd", "mintEnd",
          "freeSharesLeft", "openedAt", "freeSharesRemaining", "launched",
          "freeRemaining", "paidMinted", "FREE_MAX", "MAX_PER_WALLET", "price", "PRICE"]
USER_FIELDS = ["balanceOf_user", "freeClaimed_user", "freeUsed_user", "mintedBy_user",
               "freeMintedBy_user", "freeAvailable_user"]

updated = []
batch_fail = []
skipped_no_key = []
for name, r in reads.items():
    addr = r.get("address", "")
    key = addr2key.get(str(addr).lower())
    views = r.get("views")
    if views is None:
        batch_fail.append(name)
        continue
    if key is None:
        skipped_no_key.append(name)
        continue
    e = contracts[key]
    changes = []
    for f in FIELDS:
        if f in views and views[f] is not None:
            if f == "freeLeft" and isinstance(views[f], int) and views[f] > 10**30:
                continue
            if e.get(f) != views[f]:
                changes.append(f"{f}:{e.get(f)}->{views[f]}")
            e[f] = views[f]
    for f in USER_FIELDS:
        if f in views and views[f] is not None:
            e[f] = views[f]
    e["lastReadWib"] = NOW
    e["lastReadBlock"] = block
    e["runNote1931"] = "Run 1931 verify (blok %d): %s" % (
        block, ("; ".join(changes) if changes else "no change"))
    updated.append(key)

# --- RunicKey: already sold-out-2026-11-12 (hot-leg 1854, reported once there);
#     this run's re-read BATCH-FAIL again; status kept, NOT re-reported.
rk = contracts.get("RunicKey")
if rk is not None:
    rk["status"] = "sold-out-2026-11-12"
    rk["runNote1931"] = ("Run 1931 verify: BATCH-FAIL lagi (RPC terdegradasi) - status TETAP "
        "sold-out-2026-11-12 dari hot-leg 1854 (freeMinted 325/325); TIDAK dilaporkan ulang.")
    rk["lastReadWib"] = NOW
    if "RunicKey" not in updated:
        updated.append("RunicKey")

# --- MECHA velocity + free% ---
m = contracts.get("MECHA")
if m is not None:
    m["freePctVerified"] = round(1827 / 4444 * 100, 1)
    m["velocityNote1931"] = ("Run 1931 verify: totalMinted 1828 / freeClaimed 1827 (vs 1901: 1828/1827) "
        "= +0 token dalam ~30 mnt -> velocity GAGAL (<20 token). free% TERVERIFIKASI 41,1% <50% "
        "(bukan kandidat) dan <70% (bukan strong lead). TETAP watchlist-only.")
    m["lastReadWib"] = NOW
    if "MECHA" not in updated:
        updated.append("MECHA")

# --- SAINTS / BUCKET velocity (verify segar vs 1901) ---
for _nm, _old, _new in (("CRTSAINTS", 148, 149), ("SUDOSAINTS", 704, 705),
                        ("0x2e50", 137, 137), ("MOONDRILL", 123, 123),
                        ("BUCKET", 708, 714)):
    _e = contracts.get(_nm)
    if _e:
        _e["velocityNote1931"] = (f"Run 1931 verify: {_old}->{_new} (+{_new - _old} dalam ~30 mnt) -> "
            "velocity TIDAK lulus (<20 token dalam interval). free% TETAP UNVERIFIED (freeLeft garbage). "
            "Umur terverifikasi <24 jam. BUKAN strong lead/kandidat.")
        _e["lastReadWib"] = NOW
        if _nm not in updated:
            updated.append(_nm)

# --- binanceai pending claim: launched() still 0 ---
ba = None
for k, it in contracts.items():
    if isinstance(it, dict) and str(it.get("address", "")).lower() == "0x46cb1d3efd4307506cda7ebba5a51be64746739e":
        ba = it
        break
if ba is not None:
    ba["runNote1931"] = ("Run 1931 verify: launched() TETAP 0, freeSharesRemaining 0, FREE_SHARES 2888 "
        "- klaim BELUM dibuka; tidak ada perubahan (fase refund per run 1801). Tetap pending.")
    ba["lastReadWib"] = NOW

# --- RigForge (track C): openedAt still 0, freeClaimed flat 338 ---
rg = contracts.get("RigForge")
if rg is not None:
    rg["runNote1931"] = ("Run 1931 verify: freeClaimed TETAP 338, freeSharesLeft 662, "
        "openedAt TETAP 0 (belum buka) - tidak ada perubahan.")
    rg["lastReadWib"] = NOW

# --- NAPPER contractURI pointer (views BATCH-FAIL; pointer only, not gate evidence) ---
np_ = contracts.get("NAPPER")
if np_ is not None:
    np_["runNote1931"] = ("Run 1931 verify: BATCH-FAIL (views tidak terbaca). contractURI() terbaca: "
        "https://dreamcompile.pages.dev/meta/collection.json - POINTER metadata (metode I) saja, "
        "BUKAN bukti website (situs harus mencetak kontrak persis); gate tetap unverified. "
        "Tidak ada promosi.")
    np_["lastReadWib"] = NOW
    if "NAPPER" not in updated:
        updated.append("NAPPER")

def wib(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")

legs = json.load(open(BASE + "run-2026-11-12-1931-legs.json"))
snap["runNote1931"] = (
    "Run 1931 (jadwal 19:31 WIB, eksekusi ~19:32-20:05 WIB): 0 kandidat baru, 0 strong lead baru, "
    "0 early lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. "
    "Pre-flight FAIL (timeout; Ankr outage sejak 9 Nov) - scan leg fast-fail, watermark TETAP 132512564; "
    "5c dilewati (tanpa output scan). Verify: 22/34 target terbaca (blok 133161207, 841 dtk); "
    "12 BATCH-FAIL (OLIVER, Cobalt, NAPPER, DACIT, SYNERGYPASS, DRAGON-0xad0d, AGENT COSMOS, "
    "AGENT ID card, RunicKey, Thor, Vexa, ROBO - nilai lama dipertahankan, BUKAN nol). "
    "Legs: feed 20 kontrak (verifiedAt 11:47:58-12:32:34Z), 4 baru vs hot-leg-seen "
    "(0x8C83..., 0xC83c..., 0x6b34... shape-check S1/S2/early SEMUA false, 8 fns, bukan agent-shaped; "
    "0x8E61... IncompleteRead Sourcify, BUKAN lead, retry run berikut); Boltbook EN 45.590 byte / ZH "
    "43.781 byte (16/18 alamat); 1 'baru' 0x4dd5... ternyata 40 karakter pertama dari tx hash di postingan "
    "WAG (bukan kontrak; shape-check 404). Bridge 116 kontrak, 0 not-in-snapshot, 7 same_owner_discarded "
    "(tidak dipromosikan). Sweep EN+ZH: semua sudah dikenal (Oathbots, Agentic Gangster free pool habis, "
    "RIGBYPASS, MOLT AGENT, AGENT COSMOS, AGENT MAO, BLOB Miner excluded, AgentForge, First-Dollar Grove). "
    "Odaily newsflash: tidak ada pengumuman free-mint Agent ID baru. "
    "binanceai pending claim: launched() TETAP 0 (belum dibuka). RigForge openedAt TETAP 0 "
    "(freeClaimed 338, datar). Velocity: tidak ada kontrak naik >=20 token (BUCKET +6 terbanyak, "
    "CRTSAINTS +1, SUDOSAINTS +1, MECHA +0, Stampooor +0, sisanya 0). Stampooor 924/1200 = 77,0% tapi "
    "slot user sudah terpakai + age-excluded - bukan strong lead. Age-exclusion baru: TIDAK ADA. "
    "Deadline terdekat: CRTSAINTS ~20:50, 0x2e50 ~21:00, MOONDRILL ~21:10, NAPPER ~22:00 WIB hari ini. "
    "NAPPER contractURI pointer baru: dreamcompile.pages.dev/meta/collection.json (metadata saja, "
    "bukan bukti website).")
snap["runNote1931_age_exclusions"] = (
    "Run 1931 AGE-EXCLUSION: TIDAK ADA yang baru. Deadline terdekat (mintStart on-chain): "
    f"CRTSAINTS mintStart {wib(1794405023)} -> tutup ~20:50 WIB hari ini; "
    f"0x2e50 mintStart {wib(1794405623)} -> tutup ~21:00 WIB; "
    f"MOONDRILL mintStart {wib(1794406225)} -> tutup ~21:10 WIB; "
    "NAPPER mintStart 2026-11-11 22:00:30 WIB -> tutup ~22:00 WIB hari ini. "
    "Stampooor sudah age-excluded (deadline 09:00 WIB hari ini lewat; entri dipertahankan sebagai "
    "holding user, balance 1).")
snap["last_run"] = NOW
snap["last_run_note"] = ("Run 1931: 0 kandidat/early/strong/track-B/track-C baru. "
    "Verify 22/34 (841 dtk); 12 BATCH-FAIL; pre-flight timeout fast-fail; watermark tetap 132512564.")

tmp = BASE + "onchain-snapshot.json.tmp-1931"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")

summary = {"run": NOW, "updated": sorted(set(updated)), "n_updated": len(set(updated)),
           "verify_block": block, "verify_batch_fail": sorted(batch_fail),
           "verify_skipped_no_key": skipped_no_key,
           "legs_feed_new": legs.get("feed_new"), "legs_boltbook_new": legs.get("boltbook_new"),
           "legs_bridge": legs.get("bridge")}
json.dump(summary, open(BASE + "run-2026-11-12-1931-merge.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
print("MERGE DONE")
