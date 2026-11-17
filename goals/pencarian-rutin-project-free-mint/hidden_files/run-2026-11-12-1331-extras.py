#!/usr/bin/env python3
"""Run 1331 extras (after merge): remove sold-out AIRDROP from snapshot,
update Oliver Agents read, finalize last_run_note + final.json decision.
No preview/mint. Snapshot already backed up by merge (.bak-1331)."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
snap = json.load(open(snap_path))

# --- 1. AIRDROP (0x417d): free pool SOLD OUT 77/77, already reported ONCE by
# hot-leg 13:19 run (hot-leg-reported.json key
# 0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9#sellout-20261112-1329, 13:29 WIB).
# Main job does NOT re-report; remove from snapshot watchlist.
airdrop_addr = "0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9"
supp = json.load(open(BASE + "run-2026-11-12-1331-verify2-supplement.json"))
air = (supp.get("reads", {}).get("AIRDROP") or {}).get("summary") or {}
removed = None
for k, v in list(snap.get("contracts", {}).items()):
    if isinstance(v, dict) and str(v.get("address", "")).lower() == airdrop_addr.lower():
        removed = k
        del snap["contracts"][k]
        break
print("AIRDROP removed:", removed, "freeMinted now:", air.get("freeMinted"),
      "totalMinted:", air.get("totalMinted"), "block:", supp.get("block"))

# --- 2. OLIVER AGENTS: fresh read run 1331 (run-2026-11-12-1331-oliver.json) ---
ol = json.load(open(BASE + "run-2026-11-12-1331-oliver.json"))
entry = snap.get("contracts", {}).get("Oliver Agents")
assert entry is not None, "Oliver Agents missing from snapshot after merge"
v1, v2 = ol.get("v1") or {}, ol.get("v2") or {}
entry["freeMinted"] = v1.get("freeMinted")
entry["freeRemaining"] = v2.get("freeRemaining")
entry["totalSupply"] = v1.get("totalSupply")
entry["paidMinted"] = v2.get("paidMinted")
entry["mintOpen"] = v1.get("mintOpen")
entry["balanceOf_user"] = v1.get("balanceOf_user")
entry["lastReadBlock"] = ol.get("block")
entry["lastReadWib"] = "2026-11-12 13:47 WIB"
entry["previousTotalSupply"] = 649
entry["velocityNote"] = (
    "Run 1331: freeMinted 649 (run 1301, blok 133110998) -> 667 (hot-leg 1319, blok 133111706) "
    "-> 689 (run ini, blok 133114044, ~13:47 WIB) = 68,9% FREE_MAX 1000, laju ~1/mnt; "
    "70% (700) diperkirakan ~13:58 WIB. Velocity ~1,0/mnt vs baseline run 1301 (baca pertama, "
    "rasio belum terhitung) - kaki velocity BELUM lulus sebagai kenaikan 1,5x (baseline 0)."
)
entry["launchNote"] = (
    "Umur TETAP UNVERIFIED run ini: 5 view waktu di kontrak SEMUA revert/null "
    "(mintStart/saleStart/START_TIME/startTime/mintOpensAt); first-mint block tidak bisa ditarik "
    "(Ankr getLogs HTTP 401, outage sejak 9 Nov); Sourcify verifiedAt 2026-11-12T03:52:35Z = "
    "10:52:35 WIB BUKAN launch time. Boltbook post 06:03:11Z (13:03:11 WIB) menyebut 630/1000 - "
    "launch pasti SEBELUM 13:03 WIB, tapi jam pasti tidak terverifikasi."
)
entry["runNote1331"] = (
    "Run 1331: freeMinted 689/1000 = 68,9% (freeRemaining 311), mintOpen 1, paidMinted 0, "
    "slot user TERBUKA (balanceOf 0); website + X TETAP terverifikasi; umur TETAP UNVERIFIED "
    "-> MASIH watchlist-only, BUKAN strong lead (68,9% <70% DAN umur unverified), BUKAN kandidat. "
    "Tidak di-preview/di-mint. Bila menembus 70% TANPA umur terverifikasi, tetap bukan strong lead."
)
print("OLIVER updated: freeMinted", entry["freeMinted"], "block", entry["lastReadBlock"])

# --- 3. Finalize decision: sweep done, 0 new ---
fin_path = BASE + "run-2026-11-12-1331-final.json"
fin = json.load(open(fin_path))
fin["decision"] = "SILENT"
fin["sweep"] = {
    "en": "0 baru - Oathbots (28 Okt, ~375/8000 = 4,7%, umur >24 jam), Agentic Gangster (sold out, sudah di snapshot), "
           "AGENT COSMOS (5 Nov, age-excluded), LeadLoop/Pixel Fox/AgentForge/Chips/PocketDragons (24-27 Okt, age-excluded)",
    "zh": "0 baru - Agentic Gangster, AGENT COSMOS, Oathbots, UFO/NEBULA (sudah di track_c), Agent Periodic Lab (2 Nov, age-excluded)",
}
fin["oliver"] = {"freeMinted": 689, "freeMax": 1000, "pct": 68.9, "age": "unverified",
                 "block": ol.get("block")}
fin["airdrop_removed"] = {"address": airdrop_addr, "freeMinted": air.get("freeMinted"),
                          "reported_by": "hot-leg 1319 sellout 13:29 WIB (no re-report)"}
json.dump(fin, open(fin_path, "w"), indent=1)
snap["last_run_note"] = (
    "Run 1331 SILENT: pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov; scan fast-fail, watermark tidak dimajukan). "
    "Legs: feed 20 (verified 05:55:10-06:30:26Z), 0 baru vs hot-leg-seen, 0 baru Boltbook; bridge 116 kontrak, "
    "0 not-in-snapshot. Verify2 transport-gagal -> supplement curl berhasil (blok 133113684). Reread blok 133112988: "
    "63 kontrak + 21 track_c, delta terbesar totalMinted +1 (0x7Eb9 1183->1184; Stampooor 911->912) - tanpa promosi. "
    "AIRDROP 77/77 SELLOUT (sudah dilaporkan hot-leg 13:29) -> dihapus dari snapshot, tanpa lapor ulang. "
    "OLIVER 689/1000 = 68,9% (blok 133114044), umur TETAP unverified (5 view waktu revert) -> watchlist-only. "
    "RigForge freeClaimed 337 (+1), freeSharesLeft 663, openedAt 0 (belum buka). binanceai launched()=0 TETAP. "
    "Sweep EN+ZH: 0 proyek baru. 0 kandidat, 0 strong lead, 0 early lead, 0 track-B dibuka, 0 track-C baru. "
    "Tidak ada eksekusi."
)
json.dump(snap, open(snap_path, "w"), indent=1)
print("EXTRAS DONE")
