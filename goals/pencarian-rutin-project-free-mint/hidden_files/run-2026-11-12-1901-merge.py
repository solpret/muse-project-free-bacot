#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-12 19:01 WIB.
Sources this run ONLY:
- run-2026-11-12-1901-verify.json (34 targets; 22 read, 12 BATCH-FAIL),
- run-2026-11-12-1901-legs.json (feed/Boltbook/bridge),
- hot-leg-2026-11-12-1854-runlog.md (RunicKey sellout 325/325, reported once there).
View-consistent updates only; None never overwrites a stored value.
Batch-fail targets keep stored values (degradation, not zero).
Atomic snapshot write (temp + os.replace); backup to .bak-1901 first.
No preview/mint."""
import json, os, shutil, datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-12 19:01 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1901")
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})

verify = json.load(open(BASE + "run-2026-11-12-1901-verify.json"))
reads = verify["reads"]
block = verify["block"]

# address -> contract key
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
    e["runNote1901"] = "Run 1901 verify (blok %d): %s" % (
        block, ("; ".join(changes) if changes else "no change"))
    updated.append(key)

# --- RunicKey: sellout verified by hot-leg 1854 (325/325), reported once there;
#     this run's re-read BATCH-FAIL (RPC degradation), values NOT from this run.
rk = contracts.get("RunicKey")
if rk is not None:
    rk["status"] = "sold-out-2026-11-12"
    rk["totalSupply"] = 325
    rk["totalMinted"] = 325
    rk["freeMinted"] = 325
    rk["freePctVerified"] = 100.0
    rk["freeRemaining"] = 0
    rk["lastReadWib"] = "2026-11-12 18:54 WIB"
    rk["lastReadBlock"] = None
    rk["runNote1901"] = ("Run 1901 verify: BATCH-FAIL (RPC terdegradasi) - nilai segar TIDAK "
        "terbaca run ini. Status diubah ke sold-out-2026-11-12 berdasarkan verifikasi hot-leg 1854 "
        "(freeMinted 325/325 = 100% pada ~18:54 WIB, sudah DILAPORKAN SEKALI sebagai sellout oleh "
        "hot-leg; TIDAK dilaporkan ulang run ini). Slot user TIDAK terambil (freeAvailable=0, "
        "balanceOf=0) - kuota habis oleh minter lain; user tidak pernah mint karena strong lead ini "
        "GATE-BLOCKED (website tidak terverifikasi, vonis 1831).")
    if "RunicKey" not in updated:
        updated.append("RunicKey")

# --- MECHA velocity + free% ---
m = contracts.get("MECHA")
if m is not None:
    m["freePctVerified"] = round(1827 / 4444 * 100, 1)
    m["velocityNote1901"] = ("Run 1901 verify: totalMinted 1828 / freeClaimed 1827 (vs 1831: 1819/1818) "
        "= +9 token dalam ~45 mnt -> velocity GAGAL (<20 token). free% TERVERIFIKASI 41,1% <50% "
        "(bukan kandidat) dan <70% (bukan strong lead). TETAP watchlist-only.")
    m["lastReadWib"] = NOW
    if "MECHA" not in updated:
        updated.append("MECHA")

# --- SAINTS / BUCKET velocity (verify segar vs 1831) ---
for _nm, _old, _new in (("CRTSAINTS", 148, 148), ("0x2e50", 137, 137), ("MOONDRILL", 123, 123),
                        ("BUCKET", 704, 708)):
    _e = contracts.get(_nm)
    if _e:
        _e["velocityNote1901"] = (f"Run 1901 verify: {_old}->{_new} (+{_new - _old} dalam ~45-60 mnt) -> "
            "velocity TIDAK lulus (<20 token dalam interval). free% TETAP UNVERIFIED (freeLeft garbage). "
            "Umur terverifikasi <24 jam. Tetap early-lead-reported, BUKAN strong lead/kandidat.")
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
    ba["runNote1901"] = ("Run 1901 verify: launched() TETAP 0, freeSharesRemaining 0, FREE_SHARES 2888 "
        "- klaim BELUM dibuka; tidak ada perubahan (fase refund per run 1801). Tetap pending.")
    ba["lastReadWib"] = NOW

# --- RigForge (track C): openedAt still 0 ---
rg = contracts.get("RigForge")
if rg is not None:
    rg["runNote1901"] = ("Run 1901 verify: freeClaimed 338 (+1 vs 1831), freeSharesLeft 662, "
        "openedAt TETAP 0 (belum buka) - tidak ada perubahan.")
    rg["lastReadWib"] = NOW

def wib(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")

legs = json.load(open(BASE + "run-2026-11-12-1901-legs.json"))
snap["runNote1901"] = (
    "Run 1901 (jadwal 19:01 WIB, eksekusi ~19:06-19:30 WIB): 0 kandidat baru, 0 strong lead baru, "
    "0 early lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. RunicKey SELLOUT 325/325 "
    "sudah diverifikasi + dilaporkan sekali oleh hot-leg 1854 (run ini BATCH-FAIL saat re-read; "
    "status snapshot diubah ke sold-out-2026-11-12, TIDAK dilaporkan ulang). "
    "Pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov) - scan leg fast-fail, watermark TETAP 132512564; "
    "5c dilewati (tanpa output scan). Verify: 22/34 target terbaca (blok 133157760, 1040 dtk); "
    "12 BATCH-FAIL (OLIVER, Cobalt, NAPPER, DACIT, SYNERGYPASS, DRAGON-0xad0d, AGENT COSMOS, "
    "AGENT ID card, RunicKey, Thor, Vexa, ROBO - nilai lama dipertahankan, BUKAN nol). "
    "Legs: feed 20 kontrak (verifiedAt 11:29-12:08 UTC), 1 baru vs hot-leg-seen (0xF911... - shape-check "
    "GAGAL 4x IncompleteRead Sourcify, BUKAN lead, retry run berikut); Boltbook EN 45.416 byte / ZH "
    "45.629 byte (6 alamat sama, 0 baru); Bridge 116 kontrak, 0 not-in-snapshot, 7 same_owner_discarded "
    "(tidak dipromosikan). Sweep EN+ZH: semua sudah dikenal (Meow Cards age-excluded 12 Nov 14:11, "
    "TINY AGENTS free-sold-out 11 Nov, UFO track-C permit-gate, NEBULA minted-by-user 11 Nov, "
    "NAOMI/Agentic Gangster free pool habis, Burn Agent excluded 9 Nov, Oathbots/RIGBYPASS dikenal). "
    "binanceai pending claim: launched() TETAP 0 (belum dibuka). RigForge openedAt TETAP 0 "
    "(freeClaimed 338, +1). Velocity: tidak ada kontrak naik >=20 token (MECHA +9 terbanyak, "
    "BUCKET +4, Stampooor +1, sisanya 0). Age-exclusion baru: TIDAK ADA. Deadline terdekat: "
    "CRTSAINTS ~20:50, 0x2e50 ~21:00, MOONDRILL ~21:10, NAPPER ~22:00 WIB hari ini.")
snap["runNote1901_age_exclusions"] = (
    "Run 1901 AGE-EXCLUSION: TIDAK ADA yang baru. Deadline terdekat (mintStart on-chain): "
    f"CRTSAINTS mintStart {wib(1794405023)} -> tutup ~20:50 WIB hari ini; "
    f"0x2e50 mintStart {wib(1794405623)} -> tutup ~21:00 WIB; "
    f"MOONDRILL mintStart {wib(1794406225)} -> tutup ~21:10 WIB; "
    "NAPPER mintStart 2026-11-11 22:00:30 WIB -> tutup ~22:00 WIB hari ini. "
    "Stampooor sudah age-excluded (deadline 09:00 WIB hari ini lewat; entri dipertahankan sebagai "
    "holding user, balance 1).")
snap["last_run"] = NOW
snap["last_run_note"] = ("Run 1901: 0 kandidat/early/strong/track-B/track-C baru. RunicKey sellout sudah "
    "dilaporkan hot-leg 1854 (status snapshot -> sold-out, tidak dilaporkan ulang). "
    "Verify 22/34 (1040 dtk); 12 BATCH-FAIL; pre-flight Ankr 401 fast-fail; watermark tetap 132512564.")

tmp = BASE + "onchain-snapshot.json.tmp-1901"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")

summary = {"run": NOW, "updated": sorted(set(updated)), "n_updated": len(set(updated)),
           "verify_block": block, "verify_batch_fail": sorted(batch_fail),
           "verify_skipped_no_key": skipped_no_key,
           "legs_feed_new": legs.get("feed_new"), "legs_boltbook_new": legs.get("boltbook_new"),
           "legs_bridge": legs.get("bridge")}
json.dump(summary, open(BASE + "run-2026-11-12-1901-merge.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
print("MERGE DONE")
