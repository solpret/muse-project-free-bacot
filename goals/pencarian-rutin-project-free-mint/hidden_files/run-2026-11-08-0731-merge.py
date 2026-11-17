#!/usr/bin/env python3
"""Merge run 0731 into onchain-snapshot.json. Writes snapshot (backup first)
+ run-2026-11-08-0731-merge.json (audit record). Also appends JINLI + ART
(first-seen this run) to onchain-scan-seen.json (triage script only computed
new_seen_would_append, did not write)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
re_ = json.load(open(f"{BASE}/run-2026-11-08-0731-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-08-0731-velocity.json"))
vel_rows = {r["name"]: r for r in vel["rows"]}
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261108-0731")
audit = {"run": "0731", "removed": {}, "added": [], "notes": []}

# --- 1. numeric refresh for all re-read contracts ---
n_upd = 0
for name, d in re_["reread"].items():
    c = snap["contracts"].get(name)
    if not isinstance(c, dict):
        continue
    v = vel_rows.get(name, {})
    prev_ts = c.get("totalSupply")
    cur = d.get("totalSupply")
    if cur is None:
        cur = d.get("totalMinted")
    if cur is not None:
        c["previousTotalSupply"] = prev_ts
        c["totalSupply"] = cur
    if d.get("balanceOf_user") is not None:
        c["balanceOf_user"] = d["balanceOf_user"]
    c["lastReadBlock"] = re_["block"]
    c["lastReadWib"] = "2026-11-08 run 0731"
    if v:
        c["mintedInInterval"] = v.get("mintedInInterval")
        c["currentRatePerMin"] = v.get("ratePerMin")
        c["previousRatePerMin"] = v.get("prevRatePerMin")
        c["velocityRatio"] = v.get("ratioVsPrev")
        c["velocityLegPasses"] = v.get("velocityPasses")
    n_upd += 1
audit["notes"].append(f"numeric refresh: {n_upd} contracts from 0731 re-read (block {re_['block']})")

# --- 2. track_c numeric refresh (only non-None fields) ---
n_tc = 0
for name, d in re_.get("track_c", {}).items():
    c = snap.get("track_c", {}).get(name)
    if not isinstance(c, dict):
        continue
    for k in ("totalSupply", "balanceOf_user", "freeMinted",
              "freeSharesRemaining", "freeClaimed_user"):
        if d.get(k) is not None:
            c[k] = d[k]
    c["lastReadBlock"] = re_["block"]
    c["lastReadWib"] = "2026-11-08 run 0731"
    n_tc += 1
audit["notes"].append(f"track_c refresh: {n_tc} entries from 0731 re-read (block {re_['block']})")

# --- 3. Ghostling + Voltoad: NOT removed (sweep 07:19:55 measured <48h) ---
for name, ts0731 in [("Ghostling", 3810), ("Voltoad", 4478)]:
    c = snap["contracts"].get(name)
    if isinstance(c, dict):
        c["totalSupply"] = ts0731
        c["lastReadBlock"] = re_["block"]
        c["lastReadWib"] = "2026-11-08 run 0731"
        mark = "07:27:17 WIB" if name == "Ghostling" else "07:25:59 WIB"
        c["runNote0731"] = (
            f"Run 0731: age sweep 07:19:55 WIB mengukur umur 47,88 jam (Ghostling) / 47,90 jam "
            f"(Voltoad) - MASIH <48 jam saat sweep, jadi TIDAK dihapus run ini (aturan: umur "
            f"dihitung saat sweep). Tanda 48 jam {mark} hari ini; bila belum sold out, "
            f"age-excluded + dihapus di run 0731. totalSupply {ts0731} (blok {re_['block']}). "
            f"Status tetap strong-lead-gate-blocked-2026-11-08; TIDAK di-preview/di-mint.")
audit["notes"].append(
    "Ghostling/Voltoad NOT removed run 0731: sweep 07:19:55 WIB measured 47.88h/47.90h (<48h); "
    "48h marks 07:27:17/07:25:59 WIB today - due for age-exclusion in run 0731 if not sold out.")

# --- 4. Paw Gang: single-call read resolves the Boltbook discrepancy ---
pg = snap["contracts"].get("Paw Gang")
if isinstance(pg, dict):
    pg["totalMinted"] = 1357
    pg["lastReadBlock"] = 132295792
    pg["lastReadWib"] = "2026-11-08 run 0731 (single-call)"
    pg["runNote0731"] = (
        "Run 0731: Boltbook klaim 1.338/3.333 vs snapshot 0601 totalSupply 313 - single-call "
        "read parent (blok 132295792): totalMinted=1357, mintOpen=1, balanceOf(user)=0; "
        "totalSupply()/freeClaimed()/freeMinted()/FREE_SUPPLY()/MAX_SUPPLY()/quote()/freeLeft()/freeFor() "
        "revert (fungsi tidak ada). Jadi klaim Boltbook BENAR (re-read null = artefak batch), tapi "
        "free counter + slot user TETAP UNVERIFIED (40,7% hanya inferensi totalMinted/cap, bukan "
        "verified free counter) -> TIDAK naik jadi strong lead; tetap early-lead-2026-11-07.")
audit["notes"].append("Paw Gang: totalMinted 1357 verified by parent single-call (block 132295792); "
                     "free counter + slot still unverified - stays early-lead, no promotion.")

# --- 5. Add JINLI as early lead (parent-verified) ---
snap["contracts"]["Jinli Agents"] = {
    "address": "0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496",
    "status": "early-lead-reported-2026-11-08-0731",
    "name": "锦鲤 Agents", "symbol": "JINLI", "kind": "ERC721",
    "totalSupply": 132, "freeClaimed": 132, "FREE_SUPPLY": 888, "MAX_SUPPLY": 1888,
    "freePctVerified": 14.86, "mintOpen": True,
    "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
    "userSlotNote": "Slot UNVERIFIED: mintedBy(user)=0, balanceOf(user)=0, mintOpen=1, free pool "
                    "756 tersisa - tapi quote()/freeLeft()/freeUsed()/freeFor() revert (fungsi "
                    "tidak ada di kontrak) sehingga quote=0 tidak bisa diverifikasi.",
    "firstSeenBlock": 132290865,
    "firstMintWib": "2026-11-08 06:44:59 WIB",
    "firstMintNote": "First mint TERVERIFIKASI parent run 0731: chunked Ankr getLogs Transfer-from-zero "
                     "di gap 132290411-132292962 (3 chunk <=1000 blok): 62 mint, earliest blok 132290865 "
                     "= 2026-11-08 06:44:59 WIB (timestamp via dataseed eth_getBlockByNumber). Scan window "
                     "pertama melihat 132292963 - BUKAN first mint sejati.",
    "agentShapedNote": "AGENT_ID()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry); registry bytes di "
                       "bytecode (21.730 byte); selector freeClaimed() + mint(uint256) di bytecode; "
                       "Sourcify NOT verified (404).",
    "owner": "0x23f5cdd233925ea83369a495b95f825ed710fbaa",
    "ownerNote": "Owner sama prefix dengan Agent Goats (0x23f5cdd2... per run 0601) - grup deployer "
                 "sama; TIDAK ada di bridge same_owner_discarded list (7 alamat dicek run 0731).",
    "legs0731": "Umur TERVERIFIKASI ~0,8 jam (<=48h). Free 14,86% <25% -> BUKAN strong lead, BUKAN "
                "kandidat. Velocity: first run (belum ada baseline). X discussion: unverified "
                "(tidak ada di Boltbook front page / sweep run ini). Website gate: belum dicek "
                "(tidak ada eksekusi - early lead TIDAK PERNAH di-preview/di-mint).",
    "runNote0731": "Run 0731: EARLY LEAD dilaporkan sekali (scan route 4 first-seen + verifikasi parent). "
                   "Free 132/888 = 14,86% (blok 132296919).",
    "lastReadBlock": 132296919,
    "lastReadWib": "2026-11-08 run 0731",
}
audit["added"].append("Jinli Agents 0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496 (early-lead-reported-2026-11-08-0731)")

# --- 6. run note + last run ---
snap["runNote0731"] = (
    "Run 0731 (2026-11-08 ~07:31-07:35 WIB): 0 kandidat baru, 0 strong lead baru, 0 track-C "
    "lead/kandidat baru, 0 track-B baru. 1 EARLY LEAD BARU: Jinli Agents (JINLI) 0x0f45... - first mint "
    "terverifikasi 2026-11-08 06:44:59 WIB (blok 132290865), AGENT_ID()=registry, free 132/888=14,86%, "
    "slot unverified, owner grup Agent Goats (bukan discard list). Binance ART 0xfc97... false positive "
    "(bukan agent-shaped, bukan sale-shape). Velocity pass: Sidecoo +376 ratio 94,73, BOT-UNIT +148 "
    "ratio 20,07 - keduanya freePct None + slot unverified (bukan strong lead). Paw Gang totalMinted 1357 "
    "terverifikasi single-call (Boltbook 1.338 benar; free counter + slot tetap unverified, tetap "
    "early-lead). Ghostling/Voltoad TIDAK dihapus (sweep 07:19:55 <48h; 48h 07:25:59/07:27:17 - hapus run "
    "0731 bila belum sold out). Scan window 132292853-132293852 (1000 blok), skipped gap 2.442 blok "
    "(backfill nonaktif), watermark 132293852. Binanceai + Grove tidak berubah. Bridge sha b3f349f1 "
    "tidak berubah, 0 temuan pelengkap.")
snap["last_run"] = "free-mint-search 2026-11-08 0731 WIB"
snap["last_run_wib"] = "2026-11-08 0731 WIB"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
audit["notes"].append("snapshot written (backup onchain-snapshot.json.bak-20261108-0731)")

# --- 7. append JINLI + ART to seen file (triage only computed, did not write) ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen["contracts"]["0x0f45b52f80a3a42e56e66cd8cfd1a65895c34496"] = 132290865
seen["contracts"]["0xfc97f4ab89e73d8873bd0940dff995c8165c3ebb"] = 132293257
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
audit["notes"].append("seen file: appended JINLI (132290865) + ART (132293257); total contracts now "
                     f"{len(seen['contracts'])}")

json.dump(audit, open(f"{BASE}/run-2026-11-08-0731-merge.json", "w"), indent=1)
print("MERGE DONE")
print(json.dumps(audit, indent=1))
