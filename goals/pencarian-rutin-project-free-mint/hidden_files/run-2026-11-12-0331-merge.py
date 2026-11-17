#!/usr/bin/env python3
"""Merge run 0331 (scheduled 2026-11-12 03:31 WIB, executed ~03:31-03:45 WIB)
into onchain-snapshot.json. Generic merge + per-item notes for this run.
Inputs: reread, verify-new, legs, final, bbnew jsons. No preview/mint.
Age exclusions this run: SEVENFOLD (verified mintStart 10 Nov 07:33, age 44h)
and RAMRAIDERS (conservative deadline ~00:30 WIB 12 Nov passed; launch bound
(00:30, 17:33] 11 Nov) - entries DELETED from snapshot contracts per the age
rule (ABYSSCABLE precedent: deleted outright), removal recorded in run note.
"""
import json, shutil, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 03:31 WIB"
NOTE_KEY = "runNote0331_1112"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-12-0331-reread.json"))
vjson = json.load(open(BASE + "run-2026-11-12-0331-verify-new.json"))
verify = vjson["verify"]
legs = json.load(open(BASE + "run-2026-11-12-0331-legs.json"))
final = json.load(open(BASE + "run-2026-11-12-0331-final.json"))
bbnew = json.load(open(BASE + "run-2026-11-12-0331-bbnew.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0331-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
VBLOCK = vjson.get("block")
FBLOCK = final.get("block")
out = {"vel_pass": [], "vel_fail_n": 0, "batch_fail": [], "tc_changes": [],
       "verify_notes": {}, "removed_age_excluded": [], "notes": []}

# --- 1. reread contracts: values + velocity ---
for name, d in reread.get("reread", {}).items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    ts_new = d.get("totalSupply")
    fm_new = d.get("freeMinted")
    if ts_new is None and fm_new is None:
        out["batch_fail"].append(name)
        e[NOTE_KEY] = ("Run 0331 (blok %s): baca batch GAGAL/all-null (transport/degradasi RPC) - "
                       "nilai lama dipertahankan, BUKAN nol; velocity TIDAK dihitung run ini; status %s."
                       % (BLOCK, e.get("status")))
        continue
    prev_ts = e.get("totalSupply")
    prev_block = e.get("lastReadBlock") or 0
    interval = max(1.0, (BLOCK - prev_block) * 0.45 / 60.0) if prev_block else 30.0
    note_parts = []
    if ts_new is not None:
        e["totalSupply"] = ts_new
        if prev_ts is not None and ts_new >= prev_ts:
            minted = ts_new - prev_ts
            rate = minted / interval
            prev_rate = e.get("currentRatePerMin")
            ratio = (rate / prev_rate) if (prev_rate and prev_rate > 0) else None
            e["previousTotalSupply"] = prev_ts
            e["mintedInInterval"] = minted
            e["intervalMinutes"] = round(interval, 1)
            e["previousRatePerMin"] = prev_rate
            e["currentRatePerMin"] = round(rate, 4)
            e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
            passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
            e["velocityLegPasses"] = passes
            if passes:
                out["vel_pass"].append((name, minted, round(rate, 3), e["velocityRatio"]))
            else:
                out["vel_fail_n"] += 1
            note_parts.append("velocity %s (+%d token, %.3f/mnt vs prev %.3f = %sx; butuh >=1.5x DAN >=20)"
                              % ("LOLOS" if passes else "GAGAL", minted, rate, prev_rate or 0,
                                 ("%.2f" % ratio) if ratio is not None else "None"))
    if fm_new is not None:
        e["freeMinted"] = fm_new
    if d.get("FREE_SUPPLY") is not None:
        e["FREE_SUPPLY"] = d["FREE_SUPPLY"]
    if d.get("MAX_SUPPLY") is not None:
        e["MAX_SUPPLY"] = d["MAX_SUPPLY"]
    if d.get("mintOpen") is not None:
        e["mintOpen"] = d["mintOpen"]
    if d.get("balanceOf_user") is not None:
        e["balanceOf_user"] = d["balanceOf_user"]
    e["lastReadBlock"] = BLOCK
    if note_parts:
        e[NOTE_KEY] = "Run 0331 (blok %s): %s." % (BLOCK, "; ".join(note_parts))

# --- 2. verify-new: fresh values ---
UPD = ["totalSupply", "totalMinted", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY",
       "mintOpen", "balanceOf_user", "mintStart", "mintOpenedAt", "saleStart",
       "saleEnd", "freeClaimed_user", "mintedBy_user", "freeAvailable_user"]
for name, d in verify.items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    if d.get("_batch_fail"):
        e[NOTE_KEY] = ("Run 0331 verify-new (blok %s): baca batch GAGAL (transport) - nilai lama "
                       "dipertahankan, BUKAN nol; status %s." % (VBLOCK, e.get("status")))
        out["verify_notes"][name] = "batch_fail"
        continue
    changed = []
    for k in UPD:
        if d.get(k) is not None and e.get(k) != d[k]:
            changed.append("%s %s->%s" % (k, e.get(k), d[k]))
            e[k] = d[k]
    if d.get("totalMinted") is not None:
        e["totalMinted"] = d["totalMinted"]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    e["lastReadBlock"] = VBLOCK
    out["verify_notes"][name] = "; ".join(changed) if changed else "unchanged"

# --- 3. track_c reread ---
for name, d in reread.get("track_c", {}).items():
    e = TC.get(name)
    if not isinstance(e, dict):
        continue
    if d.get("_batch_fail"):
        continue
    ch = []
    for k in ("totalSupply", "freeMinted"):
        if d.get(k) is not None and e.get(k) != d[k]:
            ch.append("%s %s->%s" % (k, e.get(k), d[k]))
            e[k] = d[k]
    if ch:
        out["tc_changes"].append((name, "; ".join(ch)))

# --- 4. SEVEN: still strong lead, gate-blocked (already reported once) ---
sev = C.get("SEVEN")
if isinstance(sev, dict):
    sev["freeMinted"] = final["SEVEN"]["freeMinted"]
    sev["FREE_CAP"] = 1111
    sev["lastReadBlock"] = FBLOCK
    sev[NOTE_KEY] = ("Run 0331 (blok %s): freeMinted 883/1111 = 79,46%% (was 837); umur TERVERIFIKASI "
                     "<24 jam (mintOpensAt 2026-11-11 23:41:37 WIB); slot user TERBUKA (freeCountBy 0). "
                     "Tetap strong-lead-gate-blocked, SUDAH dilaporkan sekali 02:32 WIB -> TIDAK di-preview/di-mint, "
                     "TIDAK dilaporkan ulang. Deadline umur ~23:36-23:41 WIB 12 Nov." % FBLOCK)

# --- 5. Eco: still EARLY (token-based 36%), NOT a strong lead ---
eco = C.get("Eco")
if isinstance(eco, dict):
    eco["freeWalletCount"] = final["Eco"]["freeWalletCount"]
    eco["freeWalletsLeft"] = 555 - final["Eco"]["freeWalletCount"]
    eco["freeMinted"] = final["Eco"]["freeMinted"]
    eco["totalMinted"] = final["Eco"]["totalMinted"]
    eco["FREE_WALLETS"] = 555
    eco["FREE_PER_WALLET"] = 5
    eco["MAX_SUPPLY"] = 5555
    eco["lastReadBlock"] = FBLOCK
    eco[NOTE_KEY] = ("Run 0331 (blok %s): freeMinted 1000/2775 = 36,04%% token (was 839); freeWalletCount "
                     "451/555 = 81,26%% wallet. Ukuran TOKEN yang benar: 36%% <50%% kandidat dan <70%% strong lead "
                     "-> tetap EARLY LEAD, BUKAN strong lead (koreksi run 0231 sudah dicatat). Slot user terbuka "
                     "(freeCountBy 0, bal 0). Gate website GAGAL (dilaporkan 02:32 WIB) -> TIDAK di-preview/di-mint." % FBLOCK)

# --- 6. Stampooor / AgentPals / Moonfang / Pickgrid / AGCR / NAOMI / MECHA / BUCKET ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["freeMinted"] = 885
    st["lastReadBlock"] = VBLOCK
    st[NOTE_KEY] = ("Run 0331: freeMinted 885/1200 = 73,75%% (TETAP, was 885); mintStart 2026-11-11 09:00 WIB, "
                    "umur ~18,5 jam <24 jam; slot user terbuka (freeAvailable 1, bal 0). Situs dicek ulang run ini "
                    "(curl ~03:44 WIB): root 000 + /packs 000 + www 000 - DNS/connect fail TETAP -> gate-blocked, "
                    "sudah dilaporkan sekali run 1901 11 Nov -> TIDAK dilaporkan ulang, TIDAK di-preview/di-mint. "
                    "Deadline umur ~09:00 WIB 12 Nov.")
ap = C.get("AgentPals")
if isinstance(ap, dict):
    ap["freeMinted"] = 300
    ap["lastReadBlock"] = VBLOCK
    ap[NOTE_KEY] = ("Run 0331: freeMinted 300/300 = 100%% - free pool HABIS; totalMinted 301; bal user 1 (#268). "
                    "Tidak ada perubahan tier.")
mf = C.get("0x79b0")
if isinstance(mf, dict):
    mf[NOTE_KEY] = ("Run 0331: totalSupply 200/200 sold out, bal user 1 - sudah di-mint parent ~01:25 WIB; "
                    "rekonsiliasi saja, TIDAK dilaporkan ulang.")
pg = C.get("Pickgrid")
if isinstance(pg, dict):
    pg[NOTE_KEY] = ("Run 0331: freeMinted 216/300 = 72%% (totalSupply 218) - di atas ambang strong lead 70%% TAPI umur "
                    "TETAP UNVERIFIED -> TIDAK BISA promosi. Slot user terbuka (bal 0). Tetap watchlist-only.")
ag = C.get("AGCR")
if isinstance(ag, dict):
    ag[NOTE_KEY] = ("Run 0331: freeMinted 2385/2400 = 99,38%% (totalSupply 2405) TAPI umur TETAP UNVERIFIED "
                    "(tidak ada mintStart view; site tidak menyatakan launch time) -> TIDAK BISA promosi. "
                    "Website gate PASS (aegiscore.surge.sh). Tetap watchlist-only.")
naomi = C.get("checked-0xC7Ad-2001")
if isinstance(naomi, dict):
    naomi[NOTE_KEY] = ("Run 0331: freeMinted 777/777 = sold out terkonfirmasi segar (totalMinted 782, paid 5, blok "
                      "%s) - klaim The Colony '338 remain' BASI/SALAH. Status checked-free-pool-sold-out dipertahankan."
                      % VBLOCK)
me = C.get("MECHA")
if isinstance(me, dict):
    me[NOTE_KEY] = ("Run 0331: totalMinted 1048/4444 = 23,58%% (was 1022); freePoolSize 4444; slot user terbuka "
                    "(freeAvailable 2, bal 0). Umur TETAP UNVERIFIED. Tetap EARLY.")
bu = C.get("BUCKET")
if isinstance(bu, dict):
    bu[NOTE_KEY] = ("Run 0331: totalSupply 612 (was 598); totalFreeCount 612; mintOpenedAt 2026-11-11 21:16 WIB "
                    "(umur terverifikasi ~6,3 jam); FREE_SUPPLY 3333. Free %% tidak bisa dihitung pasti tanpa "
                    "free cap terpisah (totalFreeCount = totalSupply). Tetap EARLY.")
mo = C.get("MOONDRILL")
if isinstance(mo, dict):
    mo[NOTE_KEY] = ("Run 0331: totalSupply 75 (was 71); mintStart 2026-11-11 21:10 WIB (umur ~6,4 jam); "
                    "paidMinted 0. Tetap EARLY.")
cr = C.get("CRTSAINTS")
if isinstance(cr, dict):
    cr[NOTE_KEY] = ("Run 0331: totalSupply 63 (was 61); mintStart 2026-11-11 20:50 WIB (umur ~6,7 jam); "
                    "paidMinted 0. Tetap EARLY.")
lc = C.get("Binance Life Cards")
if isinstance(lc, dict):
    lc[NOTE_KEY] = ("Run 0331: totalMinted 18 (was 16); freeMinted 18/10000 = 0,18%%; mintStart 2026-11-11 23:22 WIB "
                    "(umur terverifikasi ~4,2 jam). Tetap EARLY.")
su = C.get("SUDOSAINTS")
if isinstance(su, dict):
    su[NOTE_KEY] = ("Run 0331: totalSupply 660 (was 658); freeMinted 660. Tetap early/watchlist.")
sol = C.get("SOLACE")
if isinstance(sol, dict):
    sol[NOTE_KEY] = ("Run 0331: totalSupply raw 5.805e24 (token desimal), MAX 1e27, mintStart 2026-11-11 19:05 WIB; "
                     "free views TETAP None - kuota gratis tidak bisa diverifikasi on-chain; status paid-only "
                     "DIPERTAHANKAN; bukan lead/kandidat.")
x2 = C.get("0x2e50")
if isinstance(x2, dict):
    x2[NOTE_KEY] = ("Run 0331: baca batch GAGAL/all-null lagi (transport) - nilai lama dipertahankan; "
                    "status early-lead-reported-2026-11-11 dipertahankan; retry run berikut.")
wf = C.get("WFPASS")
if isinstance(wf, dict):
    wf[NOTE_KEY] = ("Run 0331: totalSupply 0, mintOpen 0 - BELUM launching; saleStart 1794438000 = 2026-11-12 06:00 WIB; "
                    "FREE_SUPPLY 500. Tetap upcoming/prelaunch, TIDAK di-preview/di-mint.")

# --- 7. AGE EXCLUSIONS: delete entries, record evidence ---
rm = C.pop("SEVENFOLD", None)
if isinstance(rm, dict):
    out["removed_age_excluded"].append(
        "SEVENFOLD 0x4ca724a354db4f743607ecc1a5f117b2e617c8ae: mintStart() on-chain = 2026-11-10 07:33:08 WIB "
        "(launchNote terverifikasi run 0901 10 Nov); umur 44,0 jam pada 03:31 WIB 12 Nov (>24 jam); "
        "freeMinted 1902, totalSupply 1903, MAX 7777, mintEnd 2026-11-15 - BELUM sold out; status lama "
        "candidate-reported-2026-11-10-audit-blocked. Entri DIHAPUS dari snapshot contracts (preseden ABYSSCABLE); "
        "tidak dilaporkan ulang ke chat (sudah dilaporkan sekali sebagai kandidat 10 Nov); re-add hanya bila "
        "fase/batch mint baru terverifikasi.")
rm2 = C.pop("RAMRAIDERS", None)
if isinstance(rm2, dict):
    out["removed_age_excluded"].append(
        "RAMRAIDERS 0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b: launch dalam (00:30, 17:33] WIB 11 Nov "
        "(pre-launch 00:30 WIB totalSupply 0; 549 mint per Boltbook recheck 17:33 WIB; first-mint eksak UNVERIFIED, "
        "Ankr getLogs 401); deadline umur KONSERVATIF ~00:30 WIB 12 Nov (ditetapkan run-run sebelumnya) SUDAH LEWAT "
        "pada 03:31 WIB 12 Nov; free 591/7777 = 7,6%% (totalSupply 591, blok 133033552) - BELUM sold out; status lama "
        "early-lead-reported-2026-11-11. Entri DIHAPUS dari snapshot contracts (preseden ABYSSCABLE); tidak "
        "dilaporkan ulang ke chat; re-add hanya bila fase/batch mint baru terverifikasi.")

# --- 8. ACAT 0xfa07 (Boltbook-new): NOT agent-shaped, log only ---
out["notes"].append(
    "ACAT agentvoxcat 0xfa07e35e9fb5bd3dc030e61c1709b9dfe3525da5 (Boltbook b/alpha bunnysuny.ai, 3 mnt lalu): "
    "Sourcify verified (31 fns, freeMint + hasFreeMinted + TOKENS_PER_FREE_MINT), totalSupply 411, MAX 7777, "
    "bal user 0 - TAPI TANPA registry Agent ID / AgentGate / free views / quote; post Boltbook sendiri menyatakan "
    "'freeMint() has no Agent-ID gate, deployer holds 80% of VCAT'. BUKAN agent-shaped -> BUKAN early lead, "
    "TIDAK dilaporkan, TIDAK masuk snapshot (log only; sudah ada di hot-leg-seen.json untuk dedupe).")

# --- 9. top-level run note ---
summary = (
    "Run 0331 (2026-11-12 03:31 WIB, eksekusi ~03:31-03:45 WIB): 0 kandidat baru, 0 strong lead BARU, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 0 EARLY LEAD BARU - DIAM sesuai aturan. "
    "AGE-EXCLUSION (entri dihapus dari snapshot, preseden ABYSSCABLE; dicatat di run log, TIDAK dilaporkan ulang ke chat): "
    "(1) SEVENFOLD - mintStart terverifikasi 2026-11-10 07:33:08 WIB, umur 44,0 jam, free 1902/3000-ish, belum sold out; "
    "(2) RAMRAIDERS - deadline konservatif ~00:30 WIB 12 Nov lewat (launch bound (00:30, 17:33] 11 Nov), free 591/7777 = 7,6%%. "
    "Pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov; kuota 0%% s.d. 1 Des 2026) - scan leg fast-fail, watermark TIDAK "
    "dimajukan (tetap 132512564); 5c dilewati (tanpa output scan). Reread 62 kontrak (blok 133033552, 93,7 dtk) + 23 track_c: "
    "velocity 0 LOLOS (terbesar: lihat merge json; batch-fail/all-null: Stampooor, 0x7Eb9, GangDotFun, Skywe Legion, "
    "Foundry Faces, AgentPals - nilai lama dipertahankan, verify-new menutup Stampooor/AgentPals). "
    "Track_c: 11-11 freeMinted 646->658; DROID 743; FUGUI-set1 423, set2 626; NIUBI 159; 960E-sale 38. "
    "Verify-new (blok 133033823): MECHA 1048/4444 = 23,6%%; BUCKET 612 (mintOpenedAt 21:16 WIB 11 Nov); MOONDRILL 75; "
    "CRTSAINTS 63; NAOMI 777/777 sold out (Colony '338 remain' basi); AGCR 2385/2400 = 99,38%% umur TETAP UNVERIFIED; "
    "WFPASS belum launch (saleStart 06:00 WIB 12 Nov); S1-6C50 100/100; S1-0895 111/111; BB-7c71 555; Life Cards 18 "
    "(mintStart 23:22 WIB 11 Nov); Stampooor 885/1200 = 73,75%% (TETAP); AgentPals 300/300 habis; Moonfang 200/200; "
    "Pickgrid 216/300 = 72%% tapi umur UNVERIFIED (tidak promosi); SUDOSAINTS 660; SOLACE tanpa free view (paid-only "
    "dipertahankan); 0x2e50 batch-fail lagi. Final (blok 133033982, 03:41 WIB): SEVEN 883/1111 = 79,46%% (was 837) - "
    "tetap strong-lead-gate-blocked, sudah dilaporkan sekali 02:32 WIB; Eco freeMinted 1000/2775 = 36,04%% token "
    "(freeWalletCount 451/555) - tetap EARLY, BUKAN strong lead. "
    "Sourcify feed 20 kontrak (verified 19:18-20:33 UTC 11 Nov), 2 baru (0x403C, 0xEAc9) - keduanya BUKAN S1/S2/early. "
    "Boltbook EN 44.340 byte/12 alamat, ZH 42.744 byte/10 alamat; 1 baru: ACAT 0xfa07 - BUKAN agent-shaped (freeMint tanpa "
    "Agent-ID gate, deployer pegang 80%% VCAT) -> log only. Bridge: 0 temuan pelengkap baru (116 kontrak, 7 discarded). "
    "Binanceai launched()=false (tetap refund phase). RigForge: freeSharesLeft 679, openedAt 0 (belum buka), freeClaimed 321, "
    "freeBooked(user) 10000 RIG utuh. Sweep EN+ZH: 0 proyek baru (Agentic Gangster/RIGBYPASS/MOLT free pool habis; STAMP PASS "
    "sold out; UFO/NEBULA/NOVRA/Burn Agent/NAOMI sudah dikenal; AGENT MAO site down). Route 6: Odaily 258.554 byte + PANews "
    "124.685 byte, 0 item Agent ID/free-mint."
)
snap["runNote0331_1112"] = summary
snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["last_run_note"] = ("Run 0331: DIAM - 0 kandidat/strong-lead/early/track-B/track-C baru. SEVEN 883/1111 = 79,46% "
                         "tetap gate-blocked (sudah dilaporkan); Eco 1000/2775 = 36% tetap EARLY; Stampooor 885/1200 "
                         "tetap, situs DNS fail. AGE-EXCLUDED + dihapus: SEVENFOLD (44 jam), RAMRAIDERS (deadline "
                         "konservatif lewat). Scan FAST-FAIL (Ankr 401). ACAT 0xfa07 bukan agent-shaped. "
                         "RigForge belum buka (679). binanceai launched()=0.")
tmp = BASE + "onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")
json.dump(out, open(BASE + "run-2026-11-12-0331-merge.json", "w"), indent=1)
print("SNAPSHOT WRITTEN, contracts:", len(C), "track_c:", len(TC))
print("MERGE:", json.dumps({k: v for k, v in out.items() if k != "verify_notes"}, indent=1)[:2000])
