#!/usr/bin/env python3
"""Merge run 0201 (scheduled 2026-11-12 02:01 WIB) into onchain-snapshot.json.
GENERIC merge (adapted from run 0131): inputs reread.json, verify-new.json,
legs.json, feed.json. Writes snapshot (with .bak-0201-premerge) + merge json.
No preview/mint. Read-only on-chain otherwise."""
import json, shutil, datetime, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 02:01 WIB"
NOTE_KEY = "runNote0201_1112"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-12-0201-reread.json"))
vjson = json.load(open(BASE + "run-2026-11-12-0201-verify-new.json"))
verify = vjson["verify"]
legs = json.load(open(BASE + "run-2026-11-12-0201-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0201-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
VBLOCK = vjson.get("block")
out = {"vel_pass": [], "vel_fail_n": 0, "batch_fail": [], "tc_changes": [],
       "verify_notes": {}, "sellout": [], "notes": []}

# --- 1. reread contracts: values + velocity ---
for name, d in reread.get("reread", {}).items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    ts_new = d.get("totalSupply")
    fm_new = d.get("freeMinted")
    if ts_new is None and fm_new is None:
        out["batch_fail"].append(name)
        e[NOTE_KEY] = ("Run 0201 (blok %s): baca batch GAGAL/all-null (transport/degradasi RPC) - "
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
        e[NOTE_KEY] = "Run 0201 (blok %s): %s." % (BLOCK, "; ".join(note_parts))

# --- 2. verify-new: fresh values for early leads / key items ---
UPD = ["totalSupply", "totalMinted", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY",
       "mintOpen", "balanceOf_user", "mintStart", "mintOpenedAt", "saleStart",
       "saleEnd", "freeClaimed_user", "mintedBy_user", "freeAvailable_user"]
for name, d in verify.items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    if d.get("_batch_fail"):
        e[NOTE_KEY] = ("Run 0201 verify-new (blok %s): baca batch GAGAL (transport) - nilai lama "
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

# --- 4. Eco unit correction + gate attempt (recorded, no promotion) ---
eco = C.get("Eco")
if isinstance(eco, dict):
    eco["runNote0201_1112"] = (
        "Run 0201 KOREKSI SATUAN: free quota Eco = FREE_WALLETS 555 WALLET (bukan 555 token). "
        "Bacaan segar ~02:13 WIB (blok 133021903+): freeWalletCount 273/555 = 49,19% (di bawah 50% kandidat "
        "dan 70% strong lead); freeMinted 511 token; FREE_PER_WALLET 5 -> max free token 2775, jadi "
        "511/2775 = 18,4% token-based. Catatan hot-leg 0159 '335/555 freeMinted = 60,4%' MENCAMPUR SATUAN "
        "(token vs cap wallet) dan SALAH - jangan dipakai. Velocity wallet +110 (163->273) dalam ~14 mnt, "
        "tapi kaki % belum lolos sehingga bukan kandidat/strong lead. Umur TERVERIFIKASI <24 jam "
        "(mintOpensAt 1794420689 = 2026-11-12 01:11:29 WIB); slot user terbuka (freeCountBy 0, holdsAgentId 1). "
        "Gate: website TETAP UNVERIFIED - (A) pencarian alamat mentah 0 hasil relevan; (H) kontrak tanpa "
        "contractURI; (I) tokenURI(1) hanya mengembalikan '1', tanpa URL; (C) metadata Sourcify hanya "
        "source OpenZeppelin + src/EcoNFT.sol, tanpa URL situs; owner 0x7f13f050e6fb278d01537b12379b01e8dbadf5f2 "
        "(bukan grup factory 0x11038f4a... yang dikenal). Tetap EARLY, dipantau ketat run berikut.")
    eco["freeWalletCount"] = 273
    eco["freeWalletsLeft"] = 282
    eco["FREE_WALLETS"] = 555
    eco["FREE_PER_WALLET"] = 5
    eco["MAX_PER_WALLET"] = 10
    eco["owner"] = "0x7f13f050e6fb278d01537b12379b01e8dbadf5f2"
    eco["lastReadBlock"] = VBLOCK

# --- 5. SEVEN: crossed 70% but age still unverified -> NO promotion ---
sev = C.get("SEVEN")
if isinstance(sev, dict):
    sev["runNote0201_1112"] = (
        "Run 0201: freeMinted 778/1111 = 70,03% - MELEWATI ambang strong lead 70%, TAPI umur "
        "TETAP UNVERIFIED sehingga TIDAK BISA promosi ke strong lead (kaki umur wajib terverifikasi <24 jam). "
        "Upaya verifikasi umur run ini: (a) mintStart/mintOpenedAt tidak ada di kontrak (view revert/tidak "
        "mengembalikan nilai); (b) pencarian alamat mentah 0 hasil relevan; (c) first-mint via Ankr getLogs "
        "TETAP diblokir (HTTP 401, outage sejak 9 Nov). Tetap EARLY/watchlist-only; bukan kandidat, bukan "
        "strong lead, TIDAK di-preview/di-mint, TIDAK dilaporkan ulang.")

# --- 6. Stampooor: unchanged, site still DNS-fail -> gate-blocked, no re-report ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["runNote0201_1112"] = (
        "Run 0201: freeMinted 883/1200 = 73,58% TIDAK BERUBAH (blok 133021903); mintStart 2026-11-11 "
        "09:00 WIB, umur ~17 jam <24 jam; slot user terbuka (freeAvailable 1, bal 0). Situs dicek ulang run "
        "ini (curl ~02:05 WIB): root 000 + /packs 000 + www 000 - DNS/connect fail TETAP -> gate-blocked, "
        "sudah dilaporkan sekali run 1901 11 Nov -> TIDAK dilaporkan ulang, TIDAK di-preview/di-mint.")

# --- 7. AgentPals / Moonfang reconciliation notes ---
ap = C.get("AgentPals")
if isinstance(ap, dict):
    ap["runNote0201_1112"] = ("Run 0201: freeMinted 300/300 = 100% - free pool HABIS (sudah dicatat run 0131); "
                              "totalMinted 301; bal user 1 (#268). Tidak ada perubahan tier.")
mf = C.get("0x79b0")
if isinstance(mf, dict):
    mf["runNote0201_1112"] = ("Run 0201: totalSupply 200/200 sold out, bal user 1 - sudah di-mint parent "
                              "~01:25 WIB; rekonsiliasi saja, TIDAK dilaporkan ulang.")

# --- 8. top-level run note ---
summary = (
    "Run 0201 (2026-11-12 02:01 WIB, eksekusi ~02:01-02:25 WIB): 0 kandidat baru, 0 strong lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 0 EARLY LEAD BARU - DIAM sesuai aturan. "
    "Pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov; kuota freemium 0% s.d. 1 Des 2026) - scan leg "
    "fast-fail, watermark TIDAK dimajukan (tetap 132512564); 5c dilewati. Reread 62 kontrak (blok 133021665, "
    "107,3 dtk) + 23 track_c: velocity 0 LOLOS (terbesar SOLDERCATS +13; semua <20 token; batch-fail: Yew "
    "Manor - nilai lama dipertahankan). Verify-new (blok 133021903): MECHA 988/4444 = 22,2%; BUCKET 583 "
    "(mintOpenedAt 2026-11-11 21:16 WIB, umur terverifikasi); MOONDRILL 71; CRTSAINTS 61; SEVEN 778/1111 = "
    "70,03% (LEWATI 70% tapi umur TETAP UNVERIFIED -> TIDAK promosi); AGCR 2377/2400 = 99,04% umur TETAP "
    "UNVERIFIED; Pickgrid batch-fail (nilai lama 216/300 dipertahankan); NAOMI batch-fail (nilai lama "
    "free 777/777 sold out dipertahankan); 0x2e50 all-null (nilai lama 69 dipertahankan); SUDOSAINTS 648 "
    "(umur UNVERIFIED, TIDAK di-age-exclude - deploy bukan launch time); WFPASS belum launch (saleStart "
    "06:00 WIB 12 Nov); S1-6C50 100/100; S1-0895 111; BB-7c71 534; Binance Life Cards 16 (mintStart "
    "2026-11-11 ~23:29 WIB). Eco KOREKSI SATUAN: freeWalletCount 273/555 = 49,19% (bukan 60,4% - catatan "
    "hot-leg 0159 mencampur satuan token vs cap wallet); FREE_PER_WALLET 5; website TETAP UNVERIFIED "
    "(metode A/H/I/C: 0 hasil); tetap EARLY. Stampooor 883/1200 = 73,58% TIDAK BERUBAH; situs root/packs/www "
    "tetap 000 (DNS fail) -> gate-blocked, TIDAK dilaporkan ulang. AgentPals free 300/300 habis (diketahui "
    "0131); Moonfang 200/200 sold out (minted-by-user). Sourcify feed 20 kontrak (verified 18:41-19:06 UTC), "
    "2 baru vs seen (0xbC7c, 0x4D5A) - keduanya BUKAN S1/S2/early. Boltbook EN 44.044 byte/11 alamat, ZH "
    "43.129 byte/10 alamat; 2 'baru' = tx-hash BOLT 0xe567... (bukan kontrak) + long-agent 0x827e... "
    "(excluded) -> 0 lead baru. Bridge: 0 temuan pelengkap baru (116 kontrak, 7 discarded). Binanceai "
    "launched()=false (tetap refund phase). RigForge: freeSharesLeft 679, openedAt 0 (belum buka), "
    "freeClaimed 321, freeBooked(user) 10000 RIG utuh. Sweep EN+ZH: 0 proyek baru (MOLT/BURN/AGNS/RIGBYPASS/"
    "NOVRA/WNO semua sudah excluded/minted-by-user di snapshot). Route 6: Odaily + PANews 0 item Agent "
    "ID/free-mint."
)
snap["runNote0201_1112"] = summary
snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["last_run_note"] = ("Run 0201: 0 kandidat/strong/early/track-C lead baru. Eco 273/555 wallet = 49,19% "
                         "(koreksi satuan; bukan strong lead). Stampooor 883/1200 = 73,58% gate-blocked "
                         "(situs tetap DNS fail). SEVEN 778/1111 = 70,03% tapi umur unverified. "
                         "Scan FAST-FAIL (Ankr 401). RigForge belum buka (679). binanceai launched()=0.")
tmp = BASE + "onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")
json.dump(out, open(BASE + "run-2026-11-12-0201-merge.json", "w"), indent=1)
print("SNAPSHOT WRITTEN, contracts:", len(C), "track_c:", len(TC))
print("MERGE SUMMARY:", json.dumps({k: v for k, v in out.items() if k != "verify_notes"}, indent=1)[:1500])
