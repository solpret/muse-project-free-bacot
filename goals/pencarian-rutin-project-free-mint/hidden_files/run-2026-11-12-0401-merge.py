#!/usr/bin/env python3
"""Merge run 0401 (scheduled 2026-11-12 04:01 WIB, executed ~04:01-04:25 WIB)
into onchain-snapshot.json. Fresh values only - no hardcoded prior-run notes.
Inputs: reread, verify-new, legs, final, tc-age, d405 jsons. No preview/mint.
New this run: Lucky Catch 0xD405 (agent-shaped, website VERIFIED, launch
VERIFIED 04:06 WIB, totalSupply 0 - watchlist-only first read, NOT an early
lead yet: early-lead rule needs first mints verified on-chain).
No age exclusions this run (SEVENFOLD/RAMRAIDERS/CLEPSYDRA/MoonAgent already
removed at run 0331; nothing else crosses 24h this run).
"""
import json, shutil, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 04:01 WIB"
NOTE_KEY = "runNote0401_1112"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-12-0401-reread.json"))
vjson = json.load(open(BASE + "run-2026-11-12-0401-verify-new.json"))
verify = vjson["verify"]
legs = json.load(open(BASE + "run-2026-11-12-0401-legs.json"))
final = json.load(open(BASE + "run-2026-11-12-0401-final.json"))
tcage = json.load(open(BASE + "run-2026-11-12-0401-tc-age.json"))
d405 = json.load(open(BASE + "run-2026-11-12-0401-d405.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0401-premerge")
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
        e[NOTE_KEY] = ("Run 0401 (blok %s): baca batch GAGAL/all-null (transport/degradasi RPC) - "
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
        e[NOTE_KEY] = "Run 0401 (blok %s): %s." % (BLOCK, "; ".join(note_parts))

# --- 2. verify-new: fresh values ---
UPD = ["totalSupply", "totalMinted", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY",
       "mintOpen", "balanceOf_user", "mintStart", "mintOpenedAt", "saleStart",
       "saleEnd", "freeClaimed_user", "mintedBy_user", "freeAvailable_user"]
for name, d in verify.items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    if d.get("_batch_fail"):
        e[NOTE_KEY] = ("Run 0401 verify-new (blok %s): baca batch GAGAL (transport) - nilai lama "
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
    sev["freeMinted"] = 891  # verify-new blok 133037772 (final 888 blok 133037771)
    sev["totalMinted"] = 891
    sev["FREE_CAP"] = 1111
    sev["lastReadBlock"] = VBLOCK
    sev[NOTE_KEY] = ("Run 0401 (blok %s): freeMinted 891/1111 = 80,20%% (was 883); umur TERVERIFIKASI "
                     "<24 jam (mintOpensAt 2026-11-11 23:41:37 WIB); slot user TERBUKA (freeCountBy 0). "
                     "Tetap strong-lead-gate-blocked, SUDAH dilaporkan sekali 02:32 WIB -> TIDAK di-preview/di-mint, "
                     "TIDAK dilaporkan ulang. Deadline umur ~23:36-23:41 WIB 12 Nov." % VBLOCK)

# --- 5. Eco: still EARLY (token-based 37%), NOT a strong lead ---
eco = C.get("Eco")
if isinstance(eco, dict):
    eco["freeWalletCount"] = 461  # hot-leg 0409 leg4 blok 133038089 (final 460 blok 133037771)
    eco["freeWalletsLeft"] = 555 - 461
    eco["freeMinted"] = 1033
    eco["totalMinted"] = 1033
    eco["FREE_WALLETS"] = 555
    eco["FREE_PER_WALLET"] = 5
    eco["MAX_SUPPLY"] = 5555
    eco["lastReadBlock"] = 133038089
    eco[NOTE_KEY] = ("Run 0401 (blok 133038089, hot-leg leg4 04:09): freeMinted 1033/2775 = 37,23%% token "
                     "(was 1000); freeWalletCount 461/555 = 83,06%% wallet. Ukuran TOKEN yang benar: 37%% <50%% "
                     "kandidat dan <70%% strong lead -> tetap EARLY LEAD, BUKAN strong lead. Slot user terbuka "
                     "(freeCountBy 0, bal 0). Gate website GAGAL (dilaporkan 02:32 WIB) -> TIDAK di-preview/di-mint.")

# --- 6. per-item fresh notes from verify-new ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["freeMinted"] = 885
    st["lastReadBlock"] = 133038089  # hot-leg 0409 leg4 confirms 885/1200
    st[NOTE_KEY] = ("Run 0401: freeMinted 885/1200 = 73,75%% (TETAP, was 885); mintStart 2026-11-11 09:00 WIB, "
                    "umur ~19,3 jam <24 jam; slot user terbuka (freeAvailable 1, bal 0). Situs dicek ulang run ini "
                    "(curl ~04:19 WIB): root 000 + /packs 000 + www 000 - DNS/connect fail TETAP -> gate-blocked, "
                    "sudah dilaporkan sekali run 1901 11 Nov -> TIDAK dilaporkan ulang, TIDAK di-preview/di-mint. "
                    "Deadline umur ~09:00 WIB 12 Nov.")
ap = C.get("AgentPals")
if isinstance(ap, dict):
    ap["freeMinted"] = 300
    ap[NOTE_KEY] = ("Run 0401: freeMinted 300/300 = 100%% - free pool HABIS; totalMinted 301; bal user 1 (#268). "
                    "Verify-new batch GAGAL run ini (transport) - nilai lama dipertahankan. Tidak ada perubahan tier.")
mf = C.get("0x79b0")
if isinstance(mf, dict):
    mf[NOTE_KEY] = ("Run 0401: totalSupply 200/200 sold out, bal user 1 - sudah di-mint parent ~01:25 WIB; "
                    "rekonsiliasi saja, TIDAK dilaporkan ulang.")
pg = C.get("Pickgrid")
if isinstance(pg, dict):
    pg[NOTE_KEY] = ("Run 0401: freeMinted 216/300 = 72%% (totalSupply 218) - di atas ambang strong lead 70%% TAPI umur "
                    "TETAP UNVERIFIED -> TIDAK BISA promosi. Slot user terbuka (bal 0). Tetap watchlist-only.")
ag = C.get("AGCR")
if isinstance(ag, dict):
    ag[NOTE_KEY] = ("Run 0401: freeMinted 2385/2400 = 99,38%% (totalSupply 2405) TAPI umur TETAP UNVERIFIED "
                    "(tidak ada mintStart view; site tidak menyatakan launch time) -> TIDAK BISA promosi. "
                    "Website gate PASS (aegiscore.surge.sh). Tetap watchlist-only.")
naomi = C.get("checked-0xC7Ad-2001")
if isinstance(naomi, dict):
    naomi[NOTE_KEY] = ("Run 0401: verify-new batch GAGAL (transport) - nilai lama dipertahankan: freeMinted 777/777 "
                      "sold out terkonfirmasi run 0331; klaim The Colony '338 remain' BASI/SALAH. Status "
                      "checked-free-pool-sold-out dipertahankan.")
me = C.get("MECHA")
if isinstance(me, dict):
    me[NOTE_KEY] = ("Run 0401: totalMinted 1052/4444 = 23,67%% (was 1048; hot-leg leg4 04:09: 1053); freeClaimed 1052; "
                    "freePoolSize 4444; slot user terbuka (freeAvailable 2, bal 0). Umur TETAP UNVERIFIED. Tetap EARLY.")
bu = C.get("BUCKET")
if isinstance(bu, dict):
    bu[NOTE_KEY] = ("Run 0401: verify-new batch GAGAL (transport) - nilai lama dipertahankan: totalSupply 612; "
                    "mintOpenedAt 2026-11-11 21:16 WIB (umur terverifikasi ~6,8 jam); FREE_SUPPLY 3333. Tetap EARLY.")
mo = C.get("MOONDRILL")
if isinstance(mo, dict):
    mo[NOTE_KEY] = ("Run 0401: totalSupply 75 (was 71); mintStart 2026-11-11 21:10 WIB (umur ~7,2 jam); "
                    "paidMinted 0. Tetap EARLY.")
cr = C.get("CRTSAINTS")
if isinstance(cr, dict):
    cr[NOTE_KEY] = ("Run 0401: totalSupply 65 (was 63); mintStart 2026-11-11 20:50 WIB (umur ~7,5 jam); "
                    "paidMinted 0. Tetap EARLY.")
lc = C.get("Binance Life Cards")
if isinstance(lc, dict):
    lc[NOTE_KEY] = ("Run 0401: totalMinted 18 (was 16); freeMinted 18/10000 = 0,18%%; mintStart 2026-11-11 23:22 WIB "
                    "(umur terverifikasi ~4,8 jam). Tetap EARLY.")
su = C.get("SUDOSAINTS")
if isinstance(su, dict):
    su[NOTE_KEY] = ("Run 0401: verify-new batch GAGAL (transport) - nilai lama dipertahankan: totalSupply 660; "
                    "freeMinted 660. Tetap early/watchlist.")
sol = C.get("SOLACE")
if isinstance(sol, dict):
    sol[NOTE_KEY] = ("Run 0401: verify-new batch GAGAL (transport) - nilai lama dipertahankan; free views TETAP None - "
                    "kuota gratis tidak bisa diverifikasi on-chain; status paid-only DIPERTAHANKAN; bukan lead/kandidat.")
x2 = C.get("0x2e50")
if isinstance(x2, dict):
    x2[NOTE_KEY] = ("Run 0401: baca batch GAGAL/all-null lagi (transport) - nilai lama dipertahankan; "
                    "status early-lead-reported-2026-11-11 dipertahankan; retry run berikut.")
wf = C.get("WFPASS")
if isinstance(wf, dict):
    wf[NOTE_KEY] = ("Run 0401: totalSupply 0, mintOpen 0 - BELUM launching; saleStart 1794438000 = 2026-11-12 06:00 WIB; "
                    "FREE_SUPPLY 500. Tetap upcoming/prelaunch, TIDAK di-preview/di-mint.")

# --- 7. NEW: Lucky Catch 0xD405 - watchlist-only first read (0 mints) ---
C["Lucky Catch"] = {
    "address": "0xD405C90079c594DA2456F5b37B4158A12f1382e5",
    "name": "Lucky Catch", "symbol": "LUCKY", "kind": "ERC721",
    "status": "watchlist-only-first-read-2026-11-12",
    "totalSupply": 0, "totalMinted": 0, "freeMinted": 0,
    "FREE_AGENT_CAP": 150, "FREE_X_CAP": 150, "PAID_CAP": 2500, "TOTAL_CAP": 2800,
    "agentFreeCount": 0, "paidSold": 0, "nextId": 1,
    "mintStart": 1794431163, "mintEnd": 1794690363, "mintOpen": 1,
    "agentFreeUsed_user": 0, "balanceOf_user": 0,
    "registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "website": "https://luckycatch-bsc.github.io/luckycatch/",
    "websiteVerified": True,
    "gate": "website_verified",
    "launchNote": ("Launch TERVERIFIKASI <24 jam: mintStart() on-chain = 2026-11-12 04:06:03 WIB "
                   "(blok 1330380xx, dibaca segar run 0401); Sourcify verifiedAt 2026-11-11T21:06:22Z "
                   "(verification time, BUKAN launch time)."),
    "baselineNote": ("Ditemukan run 0401 via Sourcify feed (baru vs seen) + retry curl bentuk: agent-shaped "
                     "TERVERIFIKASI (registry() = 0x60B9...22F persis; claimFreeAgent/claimFreeX + FREE_AGENT_CAP 150 "
                     "+ FREE_X_CAP 150; Sourcify 50 fns). Website TERVERIFIKASI via contractURI (data: JSON, "
                     "image host luckycatch-bsc.github.io) + fetch langsung situs: HTTP 200, 78.970 byte, mencetak "
                     "kontrak persis 4x. TAPI totalSupply = 0 (agentFreeCount 0, paidSold 0) - BELUM ADA first mint "
                     "-> BUKAN early lead run ini (aturan early butuh first mint terverifikasi on-chain); masuk "
                     "watchlist agar run/hot-leg berikut mempromosikan ke EARLY saat first mint muncul. CATATAN: "
                     "free claim butuh signature gateSigner - claimFreeAgent(bytes32 handle, uint256 deadline, "
                     "bytes sig) - slot user TIDAK bisa dicek via quote=0; perlu alur situs saat promosi. "
                     "X/discussion BELUM dicek (bukan kandidat/lead). TIDAK di-preview/di-mint."),
    "firstSeenBlock": 133038022,
    "lastReadBlock": 133038022,
    "lastReadWib": "2026-11-12 04:20 WIB",
    "xVerified": False, "velocityVerified": False,
    "freeSlotUserOpen": None,
    NOTE_KEY: ("Run 0401: first read - totalSupply 0, mintStart 04:06:03 WIB, mintOpen 1, FREE 150+150, "
               "website VERIFIED (github.io mencetak kontrak 4x). Watchlist-only, BUKAN early lead (0 mint)."),
}
out["notes"].append(
    "Lucky Catch 0xD405C90079c594DA2456F5b37B4158A12f1382e5 (LUCKY): agent-shaped + website VERIFIED + launch "
    "VERIFIED 04:06 WIB, TAPI totalSupply 0 (belum ada first mint) -> watchlist-only first read, BUKAN early lead, "
    "TIDAK dilaporkan ke chat run ini; promosi ke EARLY saat first mint terverifikasi run berikut.")

# --- 8. feed retry notes (3 IncompleteRead di legs, dicek ulang via curl) ---
out["notes"].append(
    "Sourcify feed retry via curl (3 IncompleteRead urllib di legs): 0xD405 early_shape TRUE (di atas); "
    "0x255dcad96237E40967B9b378B2586683009AAF6D = kontrak fee/venue (BPS/platform/release, 34 fns, tanpa "
    "mint/quote/free/agent) -> BUKAN agent-shaped; 0xCD4B3eE249431596DC945D68923Ce0c909a346ea = LayerZero OFT "
    "token (57 fns, quoteOFT/quoteSend, tanpa mint/free/agent) -> BUKAN agent-shaped; 0xdb09aa349BF54Af837808CB3722C4263d093a330 "
    "(12 fns, tanpa mint/quote/free/agent/nft/token) -> BUKAN agent-shaped. 0 S1/S2 baru run ini.")
out["notes"].append(
    "Boltbook run ini 0 baru (EN 44.760 byte/10 alamat, ZH 43.071 byte/10 alamat). Hot-leg 0409 menemukan "
    "0x46774b5da2ccbd31e0a5efd478f475c82edf2d77 di front page (muncul sesudah legs run ini): Sourcify ABI kosong, "
    "S1/S2/early_shape false -> BUKAN agent-shaped, sudah ditriase hot-leg (log only).")
out["notes"].append(
    "Bridge: 0 temuan pelengkap baru (116 kontrak, 7 same_owner_discarded, 0 not_in_snapshot). "
    "CLEPSYDRA + MoonAgent: sudah age-excluded + dihapus dari track_c run 0331 (tc-age run ini hanya re-read "
    "konfirmasi: CLEPSYDRA startTime 2026-11-06 21:24 WIB, freeClaimed 580e21; MoonAgent totalMints 294/800, "
    "MINT_DEADLINE 2026-11-14 11:36 WIB) - TIDAK di-re-add, TIDAK dilaporkan ulang.")
out["notes"].append(
    "Binanceai launched()=false (legs) - tetap refund phase, pending claim TIDAK dibuka. RigForge: freeSharesLeft 679, "
    "openedAt 0 (belum buka), freeClaimed 321, freeBooked(user) 10000 RIG utuh.")

# --- 9. top-level run note ---
summary = (
    "Run 0401 (2026-11-12 04:01 WIB, eksekusi ~04:01-04:25 WIB): 0 kandidat baru, 0 strong lead BARU, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 0 EARLY LEAD BARU - DIAM sesuai aturan. "
    "BARU watchlist-only (bukan lead, TIDAK dilaporkan): Lucky Catch 0xD405 (LUCKY) - agent-shaped + website VERIFIED "
    "(luckycatch-bsc.github.io mencetak kontrak 4x) + launch VERIFIED 04:06 WIB, TAPI totalSupply 0 (belum ada first mint) "
    "-> promosi ke EARLY saat first mint terverifikasi. Pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov; kuota 0%% "
    "s.d. 1 Des 2026) - scan leg fast-fail, watermark TIDAK dimajukan (tetap 132512564); 5c dilewati (tanpa output scan). "
    "Reread 62 kontrak (blok 133037011, 145,6 dtk) + 21 track_c: velocity 0 LOLOS (terbesar: BYTEBLOOM +10 token, ratio 0,71x; "
    "Twill Fullery +1 ratio 1,83x tapi <20 token). Batch-fail/all-null (nilai lama dipertahankan): SEVEN, Eco, Pickgrid, "
    "Binance Life Cards, Stampooor, AgentPals (verify-new/final/hot-leg menutup SEVEN/Eco/Stampooor/AgentPals). "
    "Track_c: 11-11 freeMinted 658->675; 0x5f76cAb7-5a-hit + VISION totalSupply ->3486600000000000000000000000. "
    "Verify-new (blok 133037772): MECHA 1052/4444 = 23,67%%; BUCKET batch-fail; MOONDRILL 75; CRTSAINTS 65; NAOMI batch-fail "
    "(777/777 sold out dipertahankan); AGCR 2385/2400 = 99,38%% umur TETAP UNVERIFIED; WFPASS belum launch (saleStart 06:00 WIB "
    "12 Nov); S1-6C50 100/100; S1-0895 111/111; BB-7c71 555; Life Cards 18 (mintStart 23:22 WIB 11 Nov); 0x79b0 200/200 sold out; "
    "Pickgrid 216/300 = 72%% tapi umur UNVERIFIED (tidak promosi); SUDOSAINTS + SOLACE batch-fail; 0x2e50 all-null lagi. "
    "Final (blok 133037771, 04:09 WIB): SEVEN freeMinted 888/1111 (verify-new 891) = ~80%% - tetap strong-lead-gate-blocked, "
    "sudah dilaporkan sekali 02:32 WIB; Eco freeMinted 1032/2775 = 37,19%% token (freeWalletCount 460/555; hot-leg 0409: 461) - "
    "tetap EARLY, BUKAN strong lead. Stampooor 885/1200 = 73,75%% (TETAP, hot-leg leg4 konfirmasi); situs dicek ulang 04:19 WIB: "
    "root + /packs + www semua 000 (DNS/connect fail TETAP) -> gate-blocked, TIDAK dilaporkan ulang. Deadline umur Stampooor "
    "~09:00 WIB 12 Nov; SEVEN ~23:41 WIB 12 Nov. Sourcify feed 20 kontrak (verified 20:17-21:06 UTC 11 Nov), 4 baru - retry curl: "
    "D405 early_shape (di atas), 3 lainnya BUKAN agent-shaped. Boltbook EN 44.760 byte/10 alamat, ZH 43.071 byte/10 alamat; "
    "0 baru run ini (hot-leg 0409: 0x4677 ABI kosong, bukan shaped). Bridge: 0 temuan pelengkap baru (116 kontrak, 7 discarded). "
    "Binanceai launched()=false (tetap refund phase). RigForge: freeSharesLeft 679, openedAt 0 (belum buka), freeClaimed 321, "
    "freeBooked(user) 10000 RIG utuh. 0 AGE-EXCLUSION baru run ini."
)
snap[NOTE_KEY] = summary
snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["last_run_note"] = ("Run 0401: DIAM - 0 kandidat/strong-lead/early/track-B/track-C baru. BARU watchlist-only: Lucky Catch "
                         "0xD405 (agent-shaped + website VERIFIED + launch 04:06 WIB, totalSupply 0 - promosi ke EARLY saat first mint). "
                         "SEVEN 891/1111 = 80,2% tetap gate-blocked (sudah dilaporkan); Eco 1033/2775 = 37,2% tetap EARLY; "
                         "Stampooor 885/1200 tetap, situs 000 (04:19 WIB). Scan FAST-FAIL (Ankr 401). "
                         "RigForge belum buka (679). binanceai launched()=0.")
tmp = BASE + "onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")
json.dump(out, open(BASE + "run-2026-11-12-0401-merge.json", "w"), indent=1)
print("SNAPSHOT WRITTEN, contracts:", len(C), "track_c:", len(TC))
print("VEL_PASS:", out["vel_pass"])
print("BATCH_FAIL:", out["batch_fail"])
print("TC_CHANGES:", out["tc_changes"])
print("VERIFY_NOTES:", json.dumps(out["verify_notes"], indent=1))
