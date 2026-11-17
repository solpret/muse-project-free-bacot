#!/usr/bin/env python3
"""Run 2026-11-06 1401 WIB finalize (parent).
Outcome: SILENT (0 kandidat/lead/promosi baru). Velocity PASS 2x tapi non-actionable:
CantonTron +50 (track-C gate-failed) dan Mossminds freeMinted +40 (same-owner discarded).
- Leg 1 re-read blok 131965602; interval vs run 1331 (blok 131962334) ~24,51 mnt
  (estimasi 3268 blok x 0,45 dtk; timestamp blok tak terbaca, RPC degradasi 403/disconnect).
- PassAgentX CORRECTION: reread totalSupply 3836 adalah corrupt read (nilai freeMinted
  tertukar); direct re-check ~14:15 WIB (dataseed1+2 sepakat): totalSupply 4058,
  freeMinted 3838 -> delta +3, velocity FAILS. Bukan burn.
- Leg 2 Boltbook: front page en+zh identik, hanya MIRROR PAIR + registry, 0 mention;
  Lemmy API newest tetap 2026-11-05T09:20:52Z, 0 keyword hit.
- Leg 3 sweep + Leg 6: tidak ada proyek baru. Vault Agent / $VAGENT
  (0xec4f41F60EC868742DE65CAbE6bF9bEA8607b599, vault.vgent.workers.dev) ditemukan via
  MINTS index cross-check: situsnya mencetak "Free shares left: 0 of 1,000" ->
  free-exhausted, dicatat excluded, BUKAN lead/kandidat, tidak dilaporkan ke chat.
  Square 0 link baru; Odaily 13 item + PANews ~7 item: 0 mention.
- Leg 4 SCAN GAGAL ke-3 berturut-turut (1301, 1331, 1401): pre-flight OK 6,8 dtk
  (head 131965546); chunk 20/20 selesai 131964584-131965583 (ERC721 147, ERC1155 4,
  ERC20-mint 449), lalu stall di fase enrichment pasca-chunk (tanpa progress logging),
  di-kill manual SCAN_EXIT=143, TIDAK ADA onchain-scan-2026-11-06-1401.json.
  Triase + 5c dilewati. Watermark bersama TIDAK dimajukan (tetap 131933548, milik backfill).
  Gap: window 131964584-131965583 (data hilang) + backfill gap 131933549-131964583.
- Leg 5a: 2 alamat baru Sourcify, 0 sale shape (0xF720a9c5... tanpa free views;
  0x06ecAE09... ABI retry-exhausted, shape unverified, bukan lead).
- Track B binanceai tetap refund/failed. Bridge 0 baru. Track-C tanpa perubahan
  status (DROID freeMinted 613->614, masih unopened).
- Never touches scan-bridge.json. Dated run-note keys (runNote1401_1106) dipakai
  agar tidak menimpa runNote1401 lama (2026-11-03) di snapshot.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1401"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1401")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = snap.setdefault("contracts", {})
RR = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
BLK = RR["block"]
def setv(e, k, v):
    if v is not None:
        e[k] = v
NUMMAP = {
 "HIVE Agents": [("totalSupply", "totalSupply")],
 "KING Agent": [("totalMinted", "totalMinted"), ("remainingFree", "remainingFree")],
 "Mummyhive": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "Thronemind": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Hashseers": [("freeMinted", "freeMinted")],
 "Smeltbots": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Forklings": [("freeMinted", "freeMinted")],
 "Agent Frogs": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "PassAgentX": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "SEAT-f11e": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "LuckyBox-d08e": [("totalSupply", "totalSupply")],
 "Tumblebots": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Mossminds": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Jolly": [("totalMinted", "totalMinted"), ("freeMinted", "freeMinted")],
 "AgentGlyph": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "Layerloom": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Pacture": [("freeMinted", "freeMinted")],
 "MILLION": [("totalMinted", "totalMinted")],
 "FOD Agent": [("totalMinted", "totalMinted")],
 "StarAgent-7d39": [("totalSupply", "totalSupply")],
 "SnailMail": [("totalSupply", "totalSupply")],
 "wheelz": [("totalSupply", "totalSupply")],
 "Cipher Mind": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Cyber Lynx Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "CantonTron": [("totalMinted", "totalMinted")],
 "Bianren": [("totalMinted", "totalMinted"), ("freeMinted", "freeMinted"),
             ("freeRemaining", "freeRemaining")],
 "Crack": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted"),
           ("publicRemaining", "publicRemaining")],
 "Cipher Wraith Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Data Synth": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Nebula Ape Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Shadow Yeti Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Silent Hydra Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Umbra Lynx Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Storm Sprite Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Void Jaguar Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Zero Genesis": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Neurolucha": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "BNB CACHE Server": [("totalSupply", "totalSupply")],
}
updated, skipped_absent = [], []
for name, pairs in NUMMAP.items():
    if name not in C:
        skipped_absent.append(name); continue
    if name not in RR.get("reread", {}):
        continue
    for snapk, rrk in pairs:
        setv(C[name], snapk, RR["reread"][name].get(rrk))
    C[name]["lastReadBlock"] = BLK
    C[name]["lastReadWib"] = "2026-11-06 run 1401"
    updated.append(name)
# PassAgentX correction (direct re-check ~14:15 WIB, dataseed1+2 agree):
# reread totalSupply 3836 was a corrupt read (freeMinted value swapped in).
C["PassAgentX"]["totalSupply"] = 4058
C["PassAgentX"]["freeMinted"] = 3838
C["PassAgentX"]["runNote1401_1106"] = ("Run 1401 (blok 131965602): totalSupply reread 3836 adalah CORRUPT read "
 "(nilai freeMinted tertukar); direct re-check ~14:15 WIB (dataseed1+2 sepakat): totalSupply 4058, "
 "freeMinted 3838 -> delta +3 vs run 1331 (4055/3836), velocity FAILS. Bukan burn.")
C["HIVE Agents"]["runNote1401_1106"] = ("Run 1401 (blok 131965602): totalSupply gagal baca (None) - degradasi RPC, "
 "BUKAN nol; nilai lama (1253) dipertahankan, velocity TIDAK dihitung; balanceOf(user) gagal baca run ini "
 "(nilai lama 1 dipertahankan); minted-by-user, bukan kandidat.")
C["KING Agent"]["runNote1401_1106"] = ("Run 1401: totalMinted 875->883 (+8, 0,326/mnt vs prev 0,357 = 0,91x, <20) -> "
 "velocity GAGAL; free 883/3333 = 26,5% >=25%; slot terbuka (costOf 0, mintedBy 0, balance 0). "
 "Tetap strong-lead-gate-blocked.")
C["StarAgent-7d39"]["runNote1401_1106"] = ("Run 1401: totalSupply 1489->1504 (+15, 0,612/mnt vs prev 1,653 = 0,37x) -> "
 "velocity GAGAL. Umur terverifikasi ~40,7 jam (first mint blok 131640557, est. 2026-11-04 21:26 WIB) -> "
 "tetap <=48 jam, TIDAK age-excluded; free % tetap UNVERIFIED -> tetap EARLY watchlist-only.")
C["SEAT-f11e"]["runNote1401_1106"] = ("Run 1401: totalMinted 4102->4134 (+32, 1,306/mnt vs prev 1,072 = 1,22x) -> "
 "velocity GAGAL; free % tetap UNVERIFIED -> watchlist-only.")
C["CantonTron"]["runNote1401_1106"] = ("Run 1401: totalMinted 464->514 (+50, 2,040/mnt vs prev 1,117 = 1,83x, >=20) -> "
 "velocity track-A LOLOS secara matematika, TAPI ia track-C gate-failed: kaki velocity tidak meng-gate "
 "track C dan gate sudah gagal -> TIDAK ada promosi/aksi. Dicatat saja.")
C["Mossminds"]["runNote1401_1106"] = ("Run 1401: freeMinted 996->1036 (+40, 1,632/mnt vs prev 0,223 = 7,32x, >=20) -> "
 "velocity LOLOS secara matematika, TAPI status promotion-discarded-same-owner -> TIDAK PERNAH "
 "dipromosikan/dilaporkan sebagai lead (aturan bridge); log only.")
if "Crack" in C:
    C["Crack"]["runNote1401_1106"] = ("Run 1401: totalMinted 1835->1953 (+118, 4,814/mnt vs prev 6,029 = 0,80x) -> "
     "velocity GAGAL; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 - mint berikutnya BERBAYAR, "
     "TIDAK diotorisasi.")
# Track C updates (non-None only)
TC = snap.setdefault("track_c", {})
for name, vals in RR.get("track_c", {}).items():
    if name not in TC:
        continue
    for k, v in vals.items():
        if v is not None and k != "address":
            TC[name][k] = v
    TC[name]["lastReadBlock"] = BLK
    TC[name]["lastReadWib"] = "2026-11-06 run 1401"
if "Crack" in TC:
    TC["Crack"]["runNote1401_1106"] = ("Run 1401: totalMinted 1835->1953 (+118, 4,814/mnt vs prev 6,029 = 0,80x) -> "
     "velocity GAGAL; freeUsed(user)=1, mintedBy(user)=1, balanceOf(user)=1 - mint berikutnya BERBAYAR, "
     "TIDAK diotorisasi.")
    for _k in ("totalSupply", "totalMinted", "publicRemaining"):
        _v = RR.get("reread", {}).get("Crack", {}).get(_k)
        if _v is not None:
            TC["Crack"][_k] = _v
# Vault Agent / $VAGENT -> excluded (free pool exhausted per its own site)
EX = snap.setdefault("excluded", {})
EX["Vault Agent"] = {
 "address": "0xec4f41F60EC868742DE65CAbE6bF9bEA8607b599",
 "symbol": "VAGENT",
 "track": "C",
 "status": "excluded-free-pool-exhausted-2026-11-06",
 "site": "https://vault.vgent.workers.dev/",
 "note": ("Sweep run 1401 (MINTS index cross-check): situs proyek sendiri mencetak "
  "'Free shares left: 0 of 1,000 - Tier 1 complete' (1.085/40.000 shares termint; Tier 2+ berbayar "
  "0,0014 BNB); /skill.md 404. Free pool HABIS -> bukan lead/kandidat, tidak dilaporkan ke chat, "
  "tidak ditambahkan ke snapshot contracts. Tidak ada verifikasi on-chain di leg sweep; bila "
  "ditemukan lagi, tetap excluded kecuali fase free baru terverifikasi.")
}
snap["runNote1401_1106"] = ("Run 1401 SILENT: 0 kandidat baru, 0 early lead baru, 0 promosi strong lead, "
 "0 pending claim baru/dibuka, 0 lead/kandidat track-C baru, 0 age-exclusion, 0 sellout, 0 slot user hilang. "
 "Velocity PASS 2x non-actionable (CantonTron track-C gate-failed; Mossminds same-owner discarded). "
 "Leg 1 blok 131965602, interval ~24,51 mnt (estimasi). Boltbook 0 hit. Sweep 0 proyek baru "
 "(Vault Agent free-exhausted -> excluded). Sourcify 0 sale shape. Track B binanceai tetap refund/failed. "
 "Bridge 0 baru. Scan leg 4 GAGAL (lihat runNote1401_scan_1106).")
snap["runNote1401_scan_1106"] = ("Run 1401: SCAN GAGAL ke-3 berturut-turut (1301, 1331, 1401). Pre-flight OK 6,8 dtk "
 "(head 131965546, 50 blok, 326 logs). Chunk 20/20 selesai 131964584-131965583 (ERC721 147, ERC1155 4, "
 "ERC20-mint 449), lalu STALL di fase enrichment pasca-chunk (eth_getCode + Sourcify ABI + name/symbol "
 "per kontrak, tanpa progress logging di fase itu): tidak ada output log 3 mnt 35 dtk, CPU ~2 dtk, "
 "di-kill manual SCAN_EXIT=143; TIDAK ADA onchain-scan-2026-11-06-1401.json. Triase + 5c dilewati. "
 "Watermark bersama TIDAK dimajukan scan ini (tetap 131933548, posisi backfill). Gap: window "
 "131964584-131965583 (data hilang) + backfill gap 131933549-131964583 belum ter-cover. Pelajaran diulang: "
 "fase enrichment butuh progress logging + penulisan parsial agar data chunk tidak hilang saat stall.")
snap["last_run_wib"] = "2026-11-06 run 1401"
snap["last_run_note"] = snap["runNote1401_1106"]
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
# Scan state: append note only; watermark untouched (backfill owns it)
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["note_1401_scan"] = snap["runNote1401_scan_1106"]
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1, ensure_ascii=False)
# Seen file: meta note only, 0 additions
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen.setdefault("_meta", {})["note_1401"] = ("Run 1401: scan GAGAL (enrichment stall, no JSON) -> 0 first-seen "
 "ditambahkan; triase + 5c dilewati.")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1, ensure_ascii=False)
print("updated contracts:", len(updated))
print("skipped absent from snapshot:", skipped_absent)
print("excluded now:", len(EX), "| track_c:", len(TC))
print("snapshot contracts:", len(C))
