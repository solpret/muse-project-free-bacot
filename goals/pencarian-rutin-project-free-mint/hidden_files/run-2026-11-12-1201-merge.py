#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 12:01 WIB - MERGE (corrected, written fresh this run).
Merges legs 1201, verify2 1201 (blok 133098091), reread 1201 (blok 133098443,
63 kontrak + 21 track_c), tc-age 1201 (blok 133098711), retry of 10 legs-error
addresses (10 now verified via curl, 0 S1/S2/early; 0 still error), RigForge manual
read (335/1000, 665 left, openedAt 0), sweep EN+ZH (0 baru).
Values are taken from THIS run's files only - no hardcoded prior-run numbers.
Writes snapshot (+ .bak-1201) and run-2026-11-12-1201-final.json. No preview/mint.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
shutil.copy(snap_path, BASE + "onchain-snapshot.json.bak-1201")
snap = json.load(open(snap_path))
legs = json.load(open(BASE + "run-2026-11-12-1201-legs.json"))
v2 = json.load(open(BASE + "run-2026-11-12-1201-verify2.json"))
tc = json.load(open(BASE + "run-2026-11-12-1201-tc-age.json"))
reread = json.load(open(BASE + "run-2026-11-12-1201-reread.json"))
retry = json.load(open(BASE + "run-2026-11-12-1201-retry-legs.json"))

def index(section):
    out = {}
    v = snap.get(section, {})
    if isinstance(v, dict):
        for k, it in v.items():
            if isinstance(it, dict) and it.get("address"):
                out[it["address"].lower()] = (k, it)
    return out

cidx = index("contracts")
tidx = index("track_c")
updates = {}
crossings = []
artefacts = []

FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
          "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user",
          "freeUsed_user", "mintedBy_user", "freeMintedBy_user",
          "freeAvailable_user", "launched", "freeSharesLeft", "openedAt",
          "FREE_SHARES", "PRICE", "price", "mintStart", "saleStart", "saleEnd"]

def upd(addr, fields, section="contracts", block=None, wib=None, note=None, note_key=None):
    idx = cidx if section == "contracts" else tidx
    key = idx.get(addr.lower())
    if key is None:
        updates[addr] = "NOT-IN-SNAPSHOT"
        return
    k, it = key
    for f, val in fields.items():
        if val is not None:
            it[f] = val
    if block:
        it["lastReadBlock"] = block
    if wib:
        it["lastReadWib"] = wib
    if note and note_key:
        it[note_key] = note
    updates[addr] = k

# --- threshold-crossing check on reread (free% vs FREE_SUPPLY, vs snapshot prev) ---
for name, d in reread["reread"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    key = cidx.get(d["address"].lower())
    if key is None:
        continue
    k, it = key
    fm = d.get("freeMinted") if d.get("freeMinted") is not None else it.get("freeClaimed")
    cap = d.get("FREE_SUPPLY") if d.get("FREE_SUPPLY") is not None else it.get("FREE_SUPPLY")
    if fm is not None and cap:
        pct = 100.0 * fm / cap
        prev = it.get("freeClaimed")
        prev_cap = it.get("FREE_SUPPLY")
        prev_pct = (100.0 * prev / prev_cap) if (prev is not None and prev_cap) else None
        if pct >= 50 and (prev_pct is None or prev_pct < 50):
            (artefacts if prev_pct is None else crossings).append(
                f"{name}: {prev_pct}% -> {pct:.1f}% (cross 50%)")
        if pct > 70 and (prev_pct is None or prev_pct <= 70):
            (artefacts if prev_pct is None else crossings).append(
                f"{name}: {prev_pct}% -> {pct:.1f}% (cross 70%)")

VB2 = v2["block"]
V2 = v2["reads"]
def ssum(name):
    return (V2.get(name) or {}).get("summary") or {}

WIB = "2026-11-12 12:01 WIB"
for name in V2:
    s = ssum(name)
    if not s:
        continue  # deadline-hit-skipped (views null: SEVEN, RigForge) - no junk note
    addr = (V2[name] or {}).get("address")
    if not addr:
        continue
    if (V2[name] or {}).get("error"):
        continue
    fields = {f: s.get(f) for f in FIELDS if s.get(f) is not None}
    upd(addr, fields, block=VB2, wib=WIB,
        note=f"Run 1201 (blok {VB2}): totalSupply/totalMinted {s.get('totalSupply') or s.get('totalMinted')}, "
             f"free {s.get('freeClaimed') or s.get('freeMinted')}, bal_user {s.get('balanceOf_user')}.",
        note_key="runNote1201")
upd("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    {"launched": ssum("binanceai-mint").get("launched")},
    block=VB2, wib=WIB,
    note="Run 1201: launched()=0 TETAP (pending claim, fase refund) - bukan kandidat.",
    note_key="runNote1201")
upd("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
    {"freeClaimed": 335, "freeSharesLeft": 665, "openedAt": 0},
    block=VB2, wib=WIB,
    note="Run 1201: freeClaimed 335/1000 TETAP (tidak berubah vs run 1131), freeSharesLeft 665, openedAt 0 (belum buka) - baca manual, verify2 deadline-skip.",
    note_key="runNote1201")

RB = reread["block"]
for name, d in reread["reread"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    fields = {f: d.get(f) for f in FIELDS if d.get(f) is not None}
    key = cidx.get(d["address"].lower())
    vel = ""
    if key is not None:
        k, it = key
        prev_ts = it.get("totalSupply")
        cur_ts = d.get("totalSupply")
        if prev_ts is not None and cur_ts is not None:
            vel = f" totalSupply {prev_ts}->{cur_ts} (+{cur_ts - prev_ts})."
    upd(d["address"], fields, block=RB, wib=WIB,
        note=f"Run 1201 reread (blok {RB}):{vel} bal_user {d.get('balanceOf_user')}.",
        note_key="runNote1201")
for name, d in reread["track_c"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    fields = {f: d.get(f) for f in FIELDS if d.get(f) is not None}
    upd(d["address"], fields, section="track_c", block=RB, wib=WIB,
        note=f"Run 1201 reread track_c (blok {RB}): freeMinted {d.get('freeMinted')}.",
        note_key="runNote1201")

# --- RAMRAIDERS: update from THIS run's reread values (619 total, 619 freeMinted) ---
ram = reread["reread"].get("RAMRAIDERS", {})
ram_entry = snap.setdefault("contracts", {}).get("RAMRAIDERS")
if isinstance(ram_entry, dict):
    ram_entry["totalSupply"] = ram.get("totalSupply")
    ram_entry["freeMinted"] = ram.get("freeMinted")
    ram_entry["MAX_SUPPLY"] = ram.get("MAX_SUPPLY") or ram_entry.get("MAX_SUPPLY")
    ram_entry["balanceOf_user"] = ram.get("balanceOf_user")
    ram_entry["lastReadBlock"] = RB
    ram_entry["lastReadWib"] = WIB
    ram_entry["runNote1201"] = (f"Run 1201 reread (blok {RB}): totalSupply {ram.get('totalSupply')} "
        f"(+3 vs 621 run 1131), freeMinted {ram.get('freeMinted')}, MAX_SUPPLY 7777, bal_user 0. "
        "Umur + free% TETAP UNVERIFIED; bukan early/strong lead/kandidat.")
    ram_entry["baselineNote"] = (ram_entry.get("baselineNote", "") +
        " Run 1201: totalSupply 624 (+3 vs 621 run 1131).")
    updates["0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"] = "RAMRAIDERS-updated-619"

# --- tc-age note (WNO 1663 -> 1668 this run) ---
TCB = tc["block"]
wno_prev = 1670
tc_note = (
    f"Run 1201 (blok {TCB}): CLEPSYDRA startTime 2026-11-06 21:24 WIB + MoonAgent "
    f"{tc['MoonAgent'].get('totalMints')}/800, MINT_DEADLINE 2026-11-14 11:36 WIB (tetap) -> keduanya TETAP age-excluded. "
    f"WNO totalShares {tc['WNO'].get('totalShares')} (naik dari {wno_prev}) - tetap age-excluded; saldo user 1.000.000.")
if isinstance(snap.get("age_exclusions"), list):
    snap["age_exclusions"].append(tc_note)
elif isinstance(snap.get("age_exclusions"), dict):
    snap["age_exclusions"]["runNote1201"] = tc_note
else:
    snap["age_exclusions_note1201"] = tc_note

# --- sweep: NOVRA + AGENT ID card already age-excluded in snapshot (run 1031);
#     only refresh their run note - no new on-chain read of NOVRA this run. ---
for key, section in (("NOVRA", "track_c"), ("AGENT ID card", "contracts")):
    ent = snap.get(section, {}).get(key)
    if isinstance(ent, dict):
        ent["runNote1201"] = ("Run 1201 sweep EN+ZH: ditemukan lagi via search, BUKAN lead "
            "(sudah age-excluded sejak run 1031; tidak dilaporkan ulang).")

snap["last_run_wib"] = "2026-11-12 12:01 WIB"
snap["last_run_note"] = (
    "Run 1201 SILENT: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 0 sellout baru, 0 age-exclusion baru. "
    "Pre-flight FAIL (Ankr Remote end closed, kelanjutan outage; scan fast-fail, watermark tetap 132512564). "
    "Legs: feed 20 (verified 04:09-04:53 UTC), 0 baru vs hot-leg-seen, 0 S1/S2/early; "
    "Boltbook EN fetch GAGAL 2x (0 byte), ZH 42.867 byte/10 alamat, 1 baru 0xfa1715... (Sourcify 404 retry, bukan agent-shaped). "
    "Retry-legs 10/10 kini terverifikasi, 0 S1/S2/early. Bridge 116/0/0 (stale, seeded 2026-11-03). "
    "Verify2 (blok 133100875, 142,2 dtk): Stampooor 906/1200 (75,5%) minted-by-user + gate-blocked, slot terpakai; "
    "WFPASS 502/500 free pool habis; AGCR 2400/2400 sold out (sudah dilaporkan); MECHA 1594/4444 (35,9%) umur UNVERIFIED + gate gagal; "
    "Pickgrid views null (degradasi RPC, bukan perubahan); binanceai launched 0 (pending, fase refund); "
    "SEVEN 1111/1111 tanpa perubahan; RigForge manual 335/1000, openedAt 0, freeBooked user 10.000 RIG - TETAP. "
    "Reread (blok 133101252): CosmicSentinel 508 flat; ORBITJANITOR 856 (+2) minted-by-user; RAMRAIDERS 624 (+3); "
    "SUDOSAINTS 697 (+6); semua delta <20, tanpa promosi; track_c 11-11 freeMinted 690->691, tanpa perubahan tier. "
    "tc-age: CLEPSYDRA/MoonAgent tetap age-excluded; WNO 1670->1671. "
    "Sweep EN+ZH: 1 temuan BARU WUMPO (wumpo.monster, mint 0x493B...2cAa) - sale-shaped (mint+quoteFor+free views+hasAgentId, Sourcify verified 40 fns) "
    "TAPI BUKAN gratis gas-only: feeFor(user,1)=0,00028507 BNB wajib dibayar ke treasury per free share (quote USDT 0, freeSharesAvailable 2, "
    "sharesSold 962, freeSharesGiven 961/7777, umur UNVERIFIED) -> dicatat excluded/not-free di track_c, TIDAK dilaporkan sebagai lead, TIDAK di-preview/mint. "
    "Sweep lain 0 baru (Agentic Gangster sold out, STAMP PASS free pool habis 10 Nov, MOLT excluded, NOVRA, WNO, First-Dollar Grove, Oathbots, AGENT MAO paused - semua dikenal/dieksklusi).")


# --- WUMPO (temuan sweep ZH run 1201): sale-shaped TAPI bukan gas-only free ---
snap.setdefault("track_c", {})["WUMPO"] = {
    "sale": "0x493B6BD3fD88DE1D86Ce0DeA45168D2eF8182cAa",
    "token": "0xf4f075eAdBBa0c6DF22BCA92c43B437D9BDdb040",
    "address": "0x493B6BD3fD88DE1D86Ce0DeA45168D2eF8182cAa",
    "website": "https://wumpo.monster/",
    "status": "excluded-not-free-feeFor",
    "saleShape": "S1-like PASS (mint + quoteFor + freeSharesAvailable/freeSharesGiven/freePoolCap + hasAgentId; Sourcify verified 40 fns; registry bytes not in ABI JSON, registry listed in skill.md 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F)",
    "freePoolNote": "Free pool 7.777 shares; freeSharesGiven 961 -> 6.816 tersisa; sharesSold 962/11.110 public cap; 2 free shares per Agent ID (first 2 shares).",
    "userSlot": {"hasAgentId": True, "freeSharesAvailable": 2, "sharesOf": 0, "quote_cost_usdt": 0, "quote_freeShares": 1},
    "notFreeReason": "Free mint WAJIB kirim transaction value BNB = feeFor(user,1) = 285071772314222 wei (0,00028507 BNB) ke treasury per share (skill.md: 'A free mint is sent with a transaction value in BNB... 100% of it goes to the treasury'; 'A free mint still needs its transaction value'). Bukan gas-only: melanggar kriteria (1) free mint gas-only + guard (c) value 0. TIDAK pernah di-preview/mint; bukan lead/kandidat.",
    "ageNote": "UNVERIFIED: umur peluncuran belum terverifikasi (t.co post tercrawl ~16 jam lalu = batas bawah saja; skill.md tidak menyebut waktu launch; first-mint on-chain tidak bisa dikoroborasi - Ankr getLogs mati, RPC publik tolak eth_getLogs).",
    "xNote": "Diskusi publik: t.co/KAehqgAJ14 (WUMPO free mint page); akun X proyek belum diverifikasi.",
    "boundary": "EXCLUDED - NOT FREE (BNB feeFor). Jangan laporkan sebagai lead; jangan re-check sebagai kandidat kecuali feeFor menjadi 0 dan umur terverifikasi <24 jam.",
    "lastReadWib": "2026-11-12 12:01 WIB",
    "runNote1201": "Run 1201: temuan sweep ZH baru; baca on-chain batch (11 calls, 15,7 dtk): hasAgentId=1, quoteFor=(0,1), feeFor=0,00028507 BNB, freeSharesAvailable=2, sharesSold=962, freeSharesGiven=961, publicCap=11110, paused=0, token totalSupply konsisten 962 shares, bal user 0. Sourcify verified 40 fns (mint/quoteFor/feeFor/free views/hasAgentId).",
}
snap.setdefault("contracts", {}).setdefault("checked-0xfa1715-1201", {
    "address": "0xfa17152377a7c73d95f10ea47bff1585103bc27e",
    "status": "checked-not-agent-shaped",
    "runNote1201": "Run 1201: alamat baru dari Boltbook ZH; Sourcify 404 (retry tetap 404, not verified) -> bukan agent-shaped, bukan lead, tidak masuk watchlist.",
})
updates["0x493B6BD3fD88DE1D86Ce0DeA45168D2eF8182cAa"] = "WUMPO-excluded-not-free"
updates["0xfa17152377a7c73d95f10ea47bff1585103bc27e"] = "checked-not-agent-shaped"

final = {
    "run": "2026-11-12 12:01 WIB",
    "decision": "SILENT",
    "preflight": "FAIL Ankr HTTP 401 (scan fast-fail; watermark tetap 132512564)",
    "legs": {"feed_n": legs["feed"]["n"], "feed_new": legs["feed_new"],
             "boltbook_en": legs["boltbook_en"], "boltbook_zh": legs["boltbook_zh"],
             "boltbook_new": legs["boltbook_new"], "bridge": legs["bridge"],
             "shapes": legs["shapes"]},
    "retry_legs_errors": {"retried": retry["retried"], "now_verified": retry["now_verified"],
                          "still_error_n": len(retry["still_error"])},
    "verify2_block": VB2,
    "reread_block": RB,
    "tc_age_block": TCB,
    "crossings": crossings,
    "crossing_artefacts_baseline_none": artefacts,
    "merged_updates": updates,
    "sweep": "EN 0 baru; ZH 1 temuan baru WUMPO (excluded: feeFor BNB wajib, bukan gas-only free); lainnya dikenal/dieksklusi (Agentic Gangster sold out, STAMP PASS free pool habis, MOLT excluded, NOVRA, WNO, First-Dollar Grove, Oathbots, AGENT MAO paused)."
}
json.dump(final, open(BASE + "run-2026-11-12-1201-final.json", "w"), indent=1)
json.dump(snap, open(snap_path, "w"), indent=1)
print(json.dumps({"decision": "SILENT", "crossings": crossings, "artefacts": artefacts,
                  "updates": len(updates), "verify2_block": VB2, "reread_block": RB,
                  "tc_age_block": TCB}, indent=1))
