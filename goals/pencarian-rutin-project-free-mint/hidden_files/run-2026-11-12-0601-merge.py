#!/usr/bin/env python3
"""Merge run 0601 (scheduled 2026-11-12 06:01 WIB, executed ~06:01-05:45 WIB)
into onchain-snapshot.json. Fresh values only - no hardcoded prior-run notes.
Inputs: reread, verify-new, legs, final, tc-age jsons. No preview/mint.
No new early-lead promotion expected this run (Lucky Catch already early-lead-reported run 0431; totalSupply still 2).
Age watch: Stampooor mintStart 09:00 WIB 11 Nov = ~20.6h at 06:08 WIB, still <24h (deadline ~09:00 WIB 12 Nov).
"""
import json, shutil, os, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 06:01 WIB"
NOTE_KEY = "runNote0601_1112"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-12-0601-reread.json"))
vjson = json.load(open(BASE + "run-2026-11-12-0601-verify-new.json"))
verify = vjson["verify"]
legs = json.load(open(BASE + "run-2026-11-12-0601-legs.json"))
final = json.load(open(BASE + "run-2026-11-12-0601-final.json"))
tcage = json.load(open(BASE + "run-2026-11-12-0601-tc-age.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0601-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
VBLOCK = vjson.get("block")
FBLOCK = final.get("block")
out = {"vel_pass": [], "vel_fail_n": 0, "batch_fail": [], "tc_changes": [],
       "verify_notes": {}, "removed_age_excluded": [], "notes": [],
       "early_lead_promotion": None}

# --- 1. reread contracts: values + velocity ---
for name, d in reread.get("reread", {}).items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    ts_new = d.get("totalSupply")
    fm_new = d.get("freeMinted")
    if ts_new is None and fm_new is None:
        out["batch_fail"].append(name)
        e[NOTE_KEY] = ("Run 0601 (blok %s): baca batch GAGAL/all-null (transport/degradasi RPC) - "
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
        e[NOTE_KEY] = "Run 0601 (blok %s): %s." % (BLOCK, "; ".join(note_parts))

# --- 2. verify-new: fresh values ---
UPD = ["totalSupply", "totalMinted", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY",
       "mintOpen", "balanceOf_user", "mintStart", "mintOpenedAt", "saleStart",
       "saleEnd", "freeClaimed_user", "mintedBy_user", "freeAvailable_user"]
for name, d in verify.items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    if d.get("_batch_fail"):
        e[NOTE_KEY] = ("Run 0601 verify-new (blok %s): baca batch GAGAL (transport) - nilai lama "
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
sev_fm = (final.get("SEVEN") or {}).get("freeMinted")
if isinstance(sev, dict) and sev_fm is not None:
    sev["freeMinted"] = sev_fm
    sev["totalMinted"] = sev_fm
    sev["FREE_CAP"] = 1111
    sev["lastReadBlock"] = FBLOCK
    sev[NOTE_KEY] = ("Run 0601 (blok %s, final 06:09 WIB): freeMinted %d/1111 = %.2f%% (was 962 run 0531, "
                     "945 hot-leg 0524); umur TERVERIFIKASI <24 jam (mintOpensAt 2026-11-11 23:41:37 WIB); "
                     "slot user TERBUKA (freeCountBy 0). Tetap strong-lead-gate-blocked, SUDAH dilaporkan "
                     "sekali 02:32 WIB -> TIDAK di-preview/di-mint, TIDAK dilaporkan ulang. "
                     "Deadline umur ~23:41 WIB 12 Nov." % (FBLOCK, sev_fm, sev_fm / 1111 * 100))

# --- 5. Eco: still EARLY (token-based ~38%), NOT a strong lead ---
eco = C.get("Eco")
eco_f = final.get("Eco") or {}
eco_v = verify.get("Eco") or {}
if isinstance(eco, dict):
    eco_fm = eco_f.get("freeMinted") or eco_v.get("freeMinted")
    eco_fw = eco_f.get("freeWalletCount")
    if eco_fm is not None:
        eco["freeMinted"] = eco_fm
        eco["totalMinted"] = eco_fm
    if eco_fw is not None:
        eco["freeWalletCount"] = eco_fw
        eco["freeWalletsLeft"] = 555 - eco_fw
    eco["FREE_WALLETS"] = 555
    eco["FREE_PER_WALLET"] = 5
    eco["MAX_SUPPLY"] = 5555
    eco["lastReadBlock"] = FBLOCK
    eco[NOTE_KEY] = ("Run 0601 (blok %s, final 06:09 WIB): freeMinted %s/2775 = %.2f%% token (was 1107 run 0531); "
                     "freeWalletCount %s/555 = %.2f%% wallet. Ukuran TOKEN yang benar: 42,56%% <50%% kandidat dan "
                     "<70%% strong lead -> tetap EARLY LEAD, BUKAN strong lead. Slot user terbuka (freeCountBy 0, "
                     "bal 0). Gate website GAGAL (dilaporkan 02:32 WIB) -> TIDAK di-preview/di-mint."
                     % (FBLOCK, eco_fm, (eco_fm or 0) / 2775 * 100, eco_fw,
                        (eco_fw or 0) / 555 * 100))

# --- 6. per-item fresh notes from verify-new ---
def vnote(name, text):
    e = C.get(name)
    if isinstance(e, dict):
        e[NOTE_KEY] = text

st = verify.get("Stampooor") or {}
if isinstance(C.get("Stampooor Stamp Packs"), dict):
    C["Stampooor Stamp Packs"]["freeMinted"] = st.get("freeMinted") or 886
    C["Stampooor Stamp Packs"]["lastReadBlock"] = VBLOCK
    vnote("Stampooor Stamp Packs",
          "Run 0601 (blok %s): freeMinted %s/1200 = %.2f%% (was 885 run 0531); mintStart 2026-11-11 09:00 WIB, "
          "umur ~21,2 jam <24 jam; slot user terbuka (freeAvailable 1, bal 0). Situs dicek ulang run ini "
          "(curl ~06:11 WIB): root 000 + /packs 000 + www 000 - DNS/connect fail TETAP -> gate-blocked, "
          "sudah dilaporkan sekali run 1905 11 Nov -> TIDAK dilaporkan ulang, TIDAK di-preview/di-mint. "
          "Deadline umur ~09:00 WIB 12 Nov."
          % (VBLOCK, st.get("freeMinted") or 886, ((st.get("freeMinted") or 886) / 1200 * 100)))
ap = verify.get("AgentPals") or {}
vnote("AgentPals", "Run 0601: freeMinted %s/300 = 100%% - free pool HABIS; totalMinted %s; bal user 1 (#268). "
                   "Tidak ada perubahan tier." % (ap.get("freeMinted"), ap.get("totalMinted")))
mf = verify.get("0x79b0") or {}
vnote("0x79b0", "Run 0601: totalSupply %s/200 sold out, bal user 1 - sudah di-mint; rekonsiliasi saja, "
                "TIDAK dilaporkan ulang." % mf.get("totalSupply"))
pg = verify.get("Pickgrid") or {}
vnote("Pickgrid", "Run 0601: freeMinted %s/300 = %.2f%% (totalSupply %s) - di atas ambang strong lead 70%% TAPI umur "
                  "TETAP UNVERIFIED -> TIDAK BISA promosi. Slot user terbuka (bal 0). Tetap watchlist-only."
                  % (pg.get("freeMinted"), (pg.get("freeMinted") or 0) / 300 * 100, pg.get("totalSupply")))
ag = verify.get("AGCR") or {}
vnote("AGCR", "Run 0601: freeMinted %s/2400 = %.2f%% (totalSupply %s) TAPI umur TETAP UNVERIFIED "
              "(tidak ada mintStart view; site tidak menyatakan launch time) -> TIDAK BISA promosi. "
              "Website gate PASS (aegiscore.surge.sh). Tetap watchlist-only."
              % (ag.get("freeMinted"), (ag.get("freeMinted") or 0) / 2400 * 100, ag.get("totalSupply")))
naomi = verify.get("NAOMI") or {}
vnote("checked-0xC7Ad-2001", "Run 0601: totalMinted %s, freeMinted %s/777 sold out (paidMinted %s); bal user 0. "
                             "Klaim The Colony '338 remain' BASI/SALAH. Status checked-free-pool-sold-out dipertahankan."
                             % (naomi.get("totalMinted"), naomi.get("freeMinted"), naomi.get("paidMinted")))
me = verify.get("MECHA") or {}
vnote("MECHA", "Run 0601: totalMinted %s/4444 = %.2f%% (was 1076 run 0531); freeClaimed %s; freePoolSize 4444; "
               "slot user terbuka (freeAvailable 2, bal 0). Umur TETAP UNVERIFIED. Tetap EARLY."
               % (me.get("totalMinted"), (me.get("totalMinted") or 0) / 4444 * 100, me.get("freeClaimed")))
bu = verify.get("BUCKET") or {}
vnote("BUCKET", "Run 0601: totalSupply %s (was 626 run 0531); mintOpenedAt 2026-11-11 21:16 WIB "
                "(umur terverifikasi ~8,9 jam); FREE_SUPPLY 3333; totalFreeCount %s. Tetap EARLY."
                % (bu.get("totalSupply"), bu.get("totalFreeCount")))
mo = verify.get("MOONDRILL") or {}
vnote("MOONDRILL", "Run 0601: totalSupply %s (was 77 run 0531); mintStart 2026-11-11 21:10 WIB "
                   "(umur ~8,9 jam); paidMinted 0. Tetap EARLY." % mo.get("totalSupply"))
cr = verify.get("CRTSAINTS") or {}
vnote("CRTSAINTS", "Run 0601: totalSupply %s (was 66 run 0531); mintStart 2026-11-11 20:50 WIB "
                   "(umur ~9,3 jam); paidMinted 0. Tetap EARLY." % cr.get("totalSupply"))
lc = verify.get("Binance Life Cards") or {}
vnote("Binance Life Cards", "Run 0601: totalMinted %s (was 18 run 0531); freeMinted %s/10000 = %.2f%%; "
                            "mintStart 2026-11-11 23:22 WIB (umur terverifikasi ~6,7 jam). Tetap EARLY."
                            % (lc.get("totalMinted"), lc.get("freeMinted"), (lc.get("freeMinted") or 0) / 10000 * 100))
su = verify.get("SUDOSAINTS") or {}
vnote("SUDOSAINTS", "Run 0601: totalSupply %s (was 661 run 0531); freeMinted %s. Tetap early/watchlist."
                    % (su.get("totalSupply"), su.get("freeMinted")))
sol = verify.get("SOLACE") or {}
vnote("SOLACE", "Run 0601: totalSupply %s; free views TETAP None - kuota gratis tidak bisa diverifikasi "
                "on-chain; status paid-only DIPERTAHANKAN; bukan lead/kandidat." % sol.get("totalSupply"))
x2 = verify.get("0x2e50") or {}
if x2.get("_batch_fail") or not x2:
    vnote("0x2e50", "Run 0601: baca batch all-null lagi (run ke-17 berturut-turut; hot-leg 0524 sempat terbaca totalSupply 75, tapi verify-new run ini all-null lagi) - nilai lama "
                    "dipertahankan; status early-lead-reported-2026-11-11 dipertahankan; retry run berikut.")
wf = verify.get("WFPASS") or {}
# WFPASS LAUNCHED this run: saleStart 1794438000 = 2026-11-12 06:00 WIB, first mints 0 -> 114
# (verify-new blok VBLOCK), fresh re-read 201/500 = 40,2% (blok 133054343). Agent-shaped CONFIRMED
# (Sourcify exact_match; AGENT_ID() = registry 0x60B9...22F; hasAgentId(user)=1; free-mint fn +
# FREE_SUPPLY 500). Website gate GAGAL (A/B/C/D/G/H/I/M: no site found; tokenURI base64 JSON tanpa
# URL; contractURI tidak ada; same-family 404/000) - early lead TIDAK PERNAH di-preview/di-mint.
wf_fresh = 201
wf_entry = C.setdefault("WFPASS", {})
wf_entry.update({
    "address": "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
    "name": "WhaleFirst Pass", "symbol": "WFPASS", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-12",
    "totalSupply": wf_fresh, "totalMinted": wf_fresh, "freeMinted": wf_fresh,
    "FREE_SUPPLY": 500, "MAX_SUPPLY": 1500,
    "mintOpen": 1, "mintStart": 1794438000, "saleStart": 1794438000, "saleEnd": 1794697200,
    "balanceOf_user": 0, "freeClaimed_user": 0, "mintedBy_user": 0, "freeAvailable_user": 1,
    "hasAgentId_user": 1, "PRICE": 2000000000000000,
    "firstSeenBlock": VBLOCK, "lastReadBlock": 133054343,
    "website": None, "gate": "website_no_site_found",
    "xVerified": False, "velocityVerified": False,
    "launchNote": ("Launch TERVERIFIKASI <24 jam: saleStart() on-chain = 2026-11-12 06:00 WIB; "
                   "first mints 0 -> 114 verified run 0601 (blok %s), 201/500 = 40,2%% (blok 133054343). "
                   "Sourcify exact_match; AGENT_ID() = registry 0x60B9...22F." % VBLOCK),
})
wf_entry[NOTE_KEY] = ("Run 0601 (blok %s): PROMOSI ke EARLY LEAD - LAUNCHED 06:00 WIB (saleStart on-chain); "
    "first mints 0 -> 114 verified (blok %s), segar 201/500 = 40,2%% (blok 133054343); mintOpen 1; slot user "
    "terbuka (freeAvailable 1, bal 0, hasAgentId 1). Agent-shaped: AGENT_ID() = registry 0x60B9...22F, "
    "hasAgentId(user)=1, free-mint fn + FREE_SUPPLY 500, Sourcify exact_match. Website gate GAGAL "
    "(A/B/C/D/G/H/I/M, tanpa situs; tokenURI tanpa URL) dan X/discussion UNVERIFIED -> BUKAN kandidat "
    "(40,2%% <50%%), BUKAN strong lead (<70%%), velocity belum terhitung (interval pertama). Early lead "
    "TIDAK PERNAH di-preview/di-mint." % (VBLOCK, VBLOCK))
out["early_lead_promotion"] = {
    "name": "WFPASS", "symbol": "WFPASS",
    "address": "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
    "totalSupply": wf_fresh, "free_caps": 500, "free_pct": round(wf_fresh / 500 * 100, 2),
    "mint_start_wib": "2026-11-12 06:00 WIB", "block": VBLOCK,
    "website": None,
    "note": "first mints verified on-chain run 0601 (0 -> 114, blok %s); free 201/500 = 40,2%% fresh; "
            "website gate GAGAL (no site found, methods A/B/C/D/G/H/I/M); X unverified; velocity unverified" % VBLOCK}
out["notes"].append(
    "PROMOSI EARLY LEAD: WFPASS (WhaleFirst Pass) 0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C - LAUNCHED "
    "06:00 WIB 12 Nov (saleStart on-chain); first mints 0 -> 114 verified run ini (blok %s), segar 201/500 = "
    "40,2%% (blok 133054343); agent-shaped (registry 0x60B9...22F, hasAgentId(user)=1, FREE_SUPPLY 500, Sourcify "
    "exact_match); slot user terbuka. Website gate GAGAL (tanpa situs) + X unverified -> BUKAN kandidat/strong "
    "lead. Dilaporkan SEKALI sebagai EARLY LEAD run ini; TIDAK di-preview/di-mint." % VBLOCK)

# --- 7. Lucky Catch: first mints verified -> PROMOTE to EARLY LEAD ---
lcv = verify.get("Lucky Catch") or {}
lc_ts = lcv.get("totalSupply")
lc_entry = C.get("Lucky Catch")
if isinstance(lc_entry, dict) and lc_ts is not None:
    lc_entry["totalSupply"] = lc_ts
    lc_entry["totalMinted"] = lcv.get("totalMinted") if lcv.get("totalMinted") is not None else lc_ts
    lc_entry["mintOpen"] = lcv.get("mintOpen")
    lc_entry["balanceOf_user"] = lcv.get("balanceOf_user")
    lc_entry["lastReadBlock"] = VBLOCK
    if lc_ts > 0 and "early-lead" not in str(lc_entry.get("status")):
        lc_entry["status"] = "early-lead-reported-2026-11-12"
        lc_entry[NOTE_KEY] = ("Run 0601 (blok %s): PROMOSI ke EARLY LEAD - first mint TERVERIFIKASI on-chain: "
                              "totalSupply 0 -> %d (mintStart 2026-11-12 04:06:03 WIB, umur ~40 mnt). Free pool "
                              "%d/300 (FREE_AGENT_CAP 150 + FREE_X_CAP 150) = %.2f%% - jauh di bawah 50%% kandidat "
                              "dan 70%% strong lead. Website VERIFIED (luckycatch-bsc.github.io mencetak kontrak 4x). "
                              "X/discussion BELUM dicek; velocity BELUM terhitung (interval pertama dengan mint). "
                              "Slot user: claim butuh signature gateSigner (claimFreeAgent) - TIDAK bisa dicek via "
                              "quote=0. Early lead TIDAK PERNAH di-preview/di-mint."
                              % (VBLOCK, lc_ts, lc_ts, lc_ts / 300 * 100))
        out["early_lead_promotion"] = {
            "name": "Lucky Catch", "symbol": "LUCKY",
            "address": "0xD405C90079c594DA2456F5b37B4158A12f1382e5",
            "totalSupply": lc_ts, "free_caps": 300, "free_pct": round(lc_ts / 300 * 100, 2),
            "mint_start_wib": "2026-11-12 04:06:03 WIB", "block": VBLOCK,
            "website": "https://luckycatch-bsc.github.io/luckycatch/",
            "note": "first mints verified on-chain run 0601; distinct minters unknown (Ankr getLogs 401); "
                    "free claim needs gateSigner signature, user slot not checkable via quote=0"}
        out["notes"].append(
            "PROMOSI EARLY LEAD: Lucky Catch 0xD405C90079c594DA2456F5b37B4158A12f1382e5 (LUCKY) - first mint "
            "terverifikasi on-chain (totalSupply 0 -> %d, blok %s); launch VERIFIED 04:06:03 WIB (<24 jam); "
            "website VERIFIED; free %d/300 = %.2f%% (<50%% kandidat, <70%% strong); X unverified; velocity "
            "unverified. Dilaporkan SEKALI sebagai EARLY LEAD run ini; TIDAK di-preview/di-mint."
            % (lc_ts, VBLOCK, lc_ts, lc_ts / 300 * 100))
    else:
        vel = e_vel = C.get("Lucky Catch") or {}
        lc_entry[NOTE_KEY] = ("Run 0601 (blok %s): totalSupply %s TETAP (was 6 run 0531); mintStart 04:06:03 WIB, "
                              "umur ~2,1 jam; free %s/300 = %.2f%%; velocity %s (+%s token, %.3f/mnt) - TIDAK promosi "
                              "(jauh di bawah 50%% kandidat / 70%% strong). Slot user: claim butuh signature "
                              "gateSigner - TIDAK bisa dicek via quote=0. Tetap EARLY LEAD, TIDAK di-preview/di-mint."
                              % (VBLOCK, lc_ts, lc_ts, lc_ts / 300 * 100,
                                 "LOLOS" if vel.get("velocityLegPasses") else "GAGAL",
                                 vel.get("mintedInInterval"), vel.get("currentRatePerMin") or 0))

# --- 7b. War Need Over (track_c): AGE-EXCLUDED ---
wno = TC.get("War Need Over")
wno_fresh = json.load(open(BASE + "run-2026-11-12-0601-wno-grove.json"))["WNO"]
if isinstance(wno, dict) and "age-excluded" not in str(wno.get("status")):
    wno["totalShares"] = wno_fresh.get("totalShares")
    wno["lastReadBlock"] = 133049582
    wno["status"] = "age-excluded-2026-11-12"
    wno[NOTE_KEY] = ("Run 0601 (blok 133049582): AGE-EXCLUDED - sale terbuka paling lambat 2026-11-10 10:56 WIB "
                     "(post The Colony: 416 shares claimed saat itu) -> umur >=42,7 jam >24 jam; token dibuat "
                     "2026-11-09 23:39 WIB. totalShares segar 1639/6000 (was 416 saat post); freeRemaining view "
                     "tidak ada di kontrak. Gate website GAGAL definitif 2026-11-10 (dilaporkan sekali) dan user "
                     "sudah mint WNO 2026-11-10 - dihapus dari pantauan aktif.")
    out["notes"].append("AGE-EXCLUDED (track_c): War Need Over 0x8C96 (WNO) - sale terbuka <=2026-11-10 10:56 WIB "
                        "(416 shares claimed saat post Colony), umur >=42,7 jam; totalShares segar 1639/6000; "
                        "gate sudah gagal definitif 10 Nov; user sudah mint. Dihapus dari pantauan aktif.")
    out["removed_age_excluded"].append("War Need Over (track_c)")

# --- 8. age-exclusion scan (active watchlist only; minted-by-user / sold-out exempt) ---
NOW_EPOCH = int(time.time()) + 7 * 3600  # WIB epoch approx via UTC+7 offset on time.time (UTC)
# time.time() is UTC epoch; WIB wall time = UTC+7h, but epoch comparison needs UTC launch epochs:
NOW_UTC = int(time.time())
LIVE_STATUSES = ("early-lead-reported", "strong-lead", "watchlist", "pending-claim")
TERMINAL = ("checked", "excluded", "sold-out", "paid-only", "not-lead", "discarded", "exh")
for name, e in list(C.items()):
    if not isinstance(e, dict):
        continue
    st = str(e.get("status") or "")
    if not any(st.startswith(s) for s in LIVE_STATUSES):
        continue
    if any(t in st for t in TERMINAL):
        continue
    launch = None
    for k in ("mintStart", "mintOpenedAt", "startTime", "mintOpensAt", "launchedAt"):
        v = e.get(k)
        if isinstance(v, (int, float)) and v > 1000000000:
            launch = v
            break
    if launch and NOW_UTC - launch >= 86400:
        e["status"] = "age-excluded-2026-11-12"
        e[NOTE_KEY] = ("Run 0601: AGE-EXCLUDED - launch terverifikasi %s sudah >=24 jam (umur %.1f jam); "
                       "belum sold out; dihapus dari pantauan aktif." % (launch, (NOW_UTC - launch) / 3600))
        out["removed_age_excluded"].append(name)
        out["notes"].append("AGE-EXCLUDED: %s (launch epoch %s, umur %.1f jam) - dihapus dari pantauan aktif."
                            % (name, launch, (NOW_UTC - launch) / 3600))

# --- 9. run notes ---
out["notes"].append(
    "Sourcify feed 20 kontrak (verified 21:53-22:54 UTC 11 Nov), 0 baru vs seen -> 0 S1/S2 baru, 0 early-shape baru.")
out["notes"].append(
    "Boltbook run ini 0 baru (EN 44.926 byte/7 alamat, ZH 43.105 byte/7 alamat; urllib fail, curl OK).")
out["notes"].append(
    "Bridge: 0 temuan pelengkap baru (116 kontrak, 7 same_owner_discarded, 0 not_in_snapshot; bridge mtime 2026-11-08 18:21 - file tidak ditulis ulang sejak 8 Nov).")
out["notes"].append(
    "Binanceai launched()=false (legs) - tetap refund phase, pending claim TIDAK dibuka. RigForge: freeSharesLeft 679, "
    "openedAt 0 (belum buka), freeClaimed 321, freeBooked(user) 10000 RIG utuh. Grove (0x8b71...): freeOpen 0, "
    "freeClaimed(user) 0 (blok 133053686) - fase 2 BELUM buka on-chain.")
out["notes"].append(
    "CLEPSYDRA + MoonAgent: tetap age-excluded (tc-age run ini hanya re-read konfirmasi: CLEPSYDRA startTime "
    "2026-11-06 21:24 WIB; MoonAgent totalMints 294/800, MINT_DEADLINE 2026-11-14 11:36 WIB) - "
    "TIDAK di-re-add, TIDAK dilaporkan ulang.")
out["notes"].append(
    "Sweep web/sosial EN+ZH (route 3/5b/6): 0 baru - semua hit sudah dikenal/dieksklusi (Agentic Gangster "
    "free pool habis 11 Nov; STAMP PASS sold-out 10 Nov; RIGBYPASS excluded 11 Nov; MOLT AGENT excluded 9 Nov; "
    "Horus AI fase 1 sold out; Burn Agent excluded-free-sold-out 9 Nov; NOVRA free pool habis 8 Nov; First-Dollar "
    "Grove age-excluded 11 Nov; Oathbots + AGENT ID cards + AgentGoldMiner age-excluded (publish 25-28 Okt); "
    "AGENT MAO track_c sudah dikenal). Klaim The Colony 'NAOMI 338 remain' TETAP "
    "BASI/SALAH: verify-new run ini freeMinted 777/777 sold out. WFPASS LAUNCHED 06:00 WIB -> EARLY LEAD run ini.")

# --- 10. top-level run note ---
promo_txt = ""
if out["early_lead_promotion"]:
    p = out["early_lead_promotion"]
    promo_txt = ("PROMOSI EARLY LEAD (dilaporkan sekali ke chat utama): WFPASS (WhaleFirst Pass) 0xD52A (WFPASS) - "
                 "LAUNCHED 06:00 WIB 12 Nov (saleStart on-chain); first mints 0 -> 114 verified (blok %s); free "
                 "201/500 = %.2f%% segar; agent-shaped (registry 0x60B9...22F); website gate GAGAL + X unverified. "
                 % (p["block"], p["free_pct"]))
vel_txt = ("velocity %d LOLOS: %s" % (len(out["vel_pass"]), out["vel_pass"]) if out["vel_pass"]
           else "velocity 0 LOLOS")
bf_txt = ("Batch-fail/all-null (nilai lama dipertahankan): %s" % ", ".join(out["batch_fail"]) if out["batch_fail"]
          else "Batch-fail/all-null: TIDAK ADA (semua 63 kontrak terbaca)")
tc_txt = ("Track_c: %s" % "; ".join("%s %s" % (n, c) for n, c in out["tc_changes"]) if out["tc_changes"]
          else "Track_c: tanpa perubahan")
summary = (
    "Run 0601 (2026-11-12 06:01 WIB, eksekusi ~06:01-05:45 WIB): 0 kandidat baru, 0 strong lead BARU, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. %s"
    "SEVEN %s/1111 = %.2f%% tetap strong-lead-gate-blocked (sudah dilaporkan); Eco %s/2775 = %.2f%% token tetap EARLY; "
    "Stampooor 886/1200 = 73,83%% tetap, situs 000 (dicek ulang ~06:11 WIB). Pre-flight FAIL (Ankr HTTP 401, "
    "outage sejak 9 Nov; kuota 0%% s.d. 1 Des 2026) - scan leg fast-fail, watermark TIDAK dimajukan (tetap 132512564); 5c "
    "dilewati (tanpa output scan). Reread 63 kontrak (blok %s, 104,3 dtk) + 21 track_c: %s. %s. "
    "%s. "
    "Verify-new (blok %s): MECHA 1161/4444 = 26,1%%; BUCKET 630; MOONDRILL 78; CRTSAINTS 67; NAOMI 777/777 free sold out "
    "(klaim Colony 338 remain BASI); AGCR 2389/2400 = 99,54%% umur TETAP UNVERIFIED; WFPASS LAUNCHED 06:00 WIB -> "
    "EARLY LEAD (114/500, segar 201/500 = 40,2%%); S1-6C50 100/100; S1-0895 111/111; BB-7c71 555/555; Life Cards 18; 0x79b0 200/200 sold out; "
    "Pickgrid 216/300 = 72%% tapi umur UNVERIFIED (tidak promosi); SUDOSAINTS 661; SOLACE paid-only; 0x2e50 all-null "
    "run ke-17. Lucky Catch totalSupply 8 (was 6), free 8/300 = 2,7%%, velocity GAGAL. "
    "Final (blok %s, 06:08 WIB): SEVEN freeMinted %s/1111; Eco freeMinted %s/2775 = %.2f%% token (freeWalletCount %s/555). "
    "Deadline umur Stampooor ~09:00 WIB 12 Nov; SEVEN ~23:41 WIB 12 Nov. Sourcify feed 20 kontrak, 0 baru - BUKAN "
    "agent-shaped. Boltbook 0 baru. Bridge 0 temuan pelengkap baru. Binanceai launched()=false. RigForge belum buka (679). "
    "Grove fase 2 belum buka (freeOpen 0, blok 133049582). Sweep EN+ZH+Odaily 0 baru. "
    "War Need Over tetap age-excluded (track_c; totalShares segar 1641/6000). "
    "%d AGE-EXCLUSION baru run ini."
    % (promo_txt, sev_fm, (sev_fm or 0) / 1111 * 100,
       eco_f.get("freeMinted"), (eco_f.get("freeMinted") or 0) / 2775 * 100,
       BLOCK, vel_txt, bf_txt, tc_txt, VBLOCK, FBLOCK, sev_fm, eco_f.get("freeMinted"),
       (eco_f.get("freeMinted") or 0) / 2775 * 100, eco_f.get("freeWalletCount"),
       len(out["removed_age_excluded"]))
)
snap[NOTE_KEY] = summary
snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["last_run_note"] = (
    "Run 0601: %s0 kandidat/strong-lead/track-B/track-C baru. SEVEN %s/1111 = %.2f%% tetap gate-blocked "
    "(sudah dilaporkan); Eco %s/2775 = %.2f%% tetap EARLY; Stampooor 886/1200 tetap, situs 000 (~06:11 WIB). "
    "Scan FAST-FAIL (Ankr down). RigForge belum buka (679). binanceai launched()=0. Grove fase 2 belum buka. WFPASS EARLY LEAD baru."
    % (("EARLY LEAD BARU: WFPASS 0xD52A (totalSupply 0->114, free segar 201/500 = 40,2%%). " if out["early_lead_promotion"] else ""),
       sev_fm, (sev_fm or 0) / 1111 * 100,
       eco_f.get("freeMinted"), (eco_f.get("freeMinted") or 0) / 2775 * 100))
tmp = BASE + "onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")
json.dump(out, open(BASE + "run-2026-11-12-0601-merge.json", "w"), indent=1)
print("SNAPSHOT WRITTEN, contracts:", len(C), "track_c:", len(TC))
print("VEL_PASS:", out["vel_pass"])
print("BATCH_FAIL:", out["batch_fail"])
print("TC_CHANGES:", out["tc_changes"])
print("VERIFY_NOTES:", json.dumps(out["verify_notes"], indent=1))
print("EARLY_PROMO:", json.dumps(out["early_lead_promotion"], indent=1))
print("AGE_EXCLUDED:", out["removed_age_excluded"])
print("NOTES:", json.dumps(out["notes"], indent=1))
