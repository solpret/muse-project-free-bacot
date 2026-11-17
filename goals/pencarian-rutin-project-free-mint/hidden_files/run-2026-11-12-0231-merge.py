#!/usr/bin/env python3
"""Merge run 0231 (scheduled 2026-11-12 02:31 WIB, executed ~02:40-03:05 WIB)
into onchain-snapshot.json. Generic merge + per-item notes for this run.
Inputs: reread, verify-new, legs, seven, eco, final jsons. No preview/mint."""
import json, shutil, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 02:31 WIB"
NOTE_KEY = "runNote0231_1112"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-12-0231-reread.json"))
vjson = json.load(open(BASE + "run-2026-11-12-0231-verify-new.json"))
verify = vjson["verify"]
legs = json.load(open(BASE + "run-2026-11-12-0231-legs.json"))
final = json.load(open(BASE + "run-2026-11-12-0231-final.json"))
seven = json.load(open(BASE + "run-2026-11-12-0231-seven.json"))
eco_f = json.load(open(BASE + "run-2026-11-12-0231-eco.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0231-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
VBLOCK = vjson.get("block")
FBLOCK = final.get("block")
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
        e[NOTE_KEY] = ("Run 0231 (blok %s): baca batch GAGAL/all-null (transport/degradasi RPC) - "
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
        e[NOTE_KEY] = "Run 0231 (blok %s): %s." % (BLOCK, "; ".join(note_parts))

# --- 2. verify-new: fresh values ---
UPD = ["totalSupply", "totalMinted", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY",
       "mintOpen", "balanceOf_user", "mintStart", "mintOpenedAt", "saleStart",
       "saleEnd", "freeClaimed_user", "mintedBy_user", "freeAvailable_user"]
for name, d in verify.items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    if d.get("_batch_fail"):
        e[NOTE_KEY] = ("Run 0231 verify-new (blok %s): baca batch GAGAL (transport) - nilai lama "
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

# --- 4. SEVEN: PROMOTED to strong lead, GATE-BLOCKED ---
sev = C.get("SEVEN")
if isinstance(sev, dict):
    sev["freeMinted"] = final["SEVEN"]["freeMinted"]
    sev["FREE_CAP"] = 1111
    sev["mintOpensAt"] = 1794415297
    sev["launchNote"] = ("Launch TERVERIFIKASI <24 jam via kontrak mintOpensAt() = 2026-11-11 23:41:37 WIB "
                         "(dibaca segar run 0231, blok 133027326; KOREKSI run 0201 yang menyebut umur UNVERIFIED "
                         "- verify-new run 0201 tidak membaca mintOpensAt, hanya mintStart/mintOpenedAt). "
                         "Sourcify verifiedAt 2026-11-11T16:36:18Z; first-seen job ini run 2331.")
    sev["status"] = "strong-lead-gate-blocked-2026-11-12"
    sev["lastReadBlock"] = FBLOCK
    sev[NOTE_KEY] = (
        "Run 0231 PROMOSI KE STRONG LEAD (3 kaki terverifikasi segar): (a) umur TERVERIFIKASI <24 jam - "
        "mintOpensAt 1794415297 = 2026-11-11 23:41:37 WIB (~3,2 jam saat baca); (b) free 837/1111 = 75,34% "
        "(FREE_CAP 1111, freeMinted 837, blok 133028622 ~03:01 WIB; 826/1111 = 74,35% pada blok 133027326); "
        "(c) slot user TERBUKA (freeCountBy 0, holdsAgentId 1, bal 0). Diskusi terverifikasi: post Boltbook "
        "/p/fS2d7494UphE (ghostagent.ai, 2026-11-11T19:36:07Z). TAPI GATE WEBSITE GAGAL -> TIDAK di-preview/di-mint, "
        "dilaporkan sekali sebagai strong lead gate-blocked. Metode gate yang dicoba: (A) pencarian alamat mentah 0 hasil "
        "relevan; (B) post Boltbook tanpa link situs (hanya bscscan kontrak lain + gang.fun + x.com/bolt_book); "
        "(C) Sourcify exact_match, tanpa URL di metadata; (G/M) pencarian nama + site:vercel/pages/deed 0 situs SEVEN "
        "(hasil lain: Agent Harvest/Grove, Anubis/Osiris, Coracle, Cosmic Sentinel); (H) contractURI null; "
        "(I) tokenURI(1) hanya '1', tanpa URL; (J) ABI tanpa fungsi situs/URL/domain; (K) GitHub search-index 0 hasil "
        "relevan; (N) author ghostagent.ai tanpa link situs/X di bio; (E) owner 0x7f13f050e6fb278d01537b12379b01e8dbadf5f2 "
        "- SAMA dengan Eco (satu deployer, dua proyek, tanpa situs); (L) BscScan via browser DIBLOKIR Cloudflare bot-wall "
        "(3 percobaan gagal 02:54-03:00 WIB, 'Verification failed') - INCONCLUSIVE, bukan bukti ada/tidak ada situs. "
        "Status: strong-lead-gate-blocked-2026-11-12.")
    out["notes"].append("SEVEN promoted to strong lead, gate-blocked")

# --- 5. Eco: PROMOTED to strong lead (crossed 70% during this run), GATE-BLOCKED ---
eco = C.get("Eco")
if isinstance(eco, dict):
    eco["freeWalletCount"] = final["Eco"]["freeWalletCount"]
    eco["freeWalletsLeft"] = 555 - final["Eco"]["freeWalletCount"]
    eco["freeMinted"] = final["Eco"]["freeMinted"]
    eco["totalMinted"] = final["Eco"]["totalMinted"]
    eco["FREE_WALLETS"] = 555
    eco["FREE_PER_WALLET"] = 5
    eco["MAX_SUPPLY"] = 5555
    eco["mintOpensAt"] = 1794420689
    eco["owner"] = "0x7f13f050e6fb278d01537b12379b01e8dbadf5f2"
    eco["status"] = "strong-lead-gate-blocked-2026-11-12"
    eco["lastReadBlock"] = FBLOCK
    eco[NOTE_KEY] = (
        "Run 0231 PROMOSI KE STRONG LEAD (3 kaki terverifikasi segar): (a) umur TERVERIFIKASI <24 jam - "
        "mintOpensAt 1794420689 = 2026-11-12 01:11:29 WIB (~1,8 jam saat baca); (b) free 399/555 wallet = 71,89% "
        "(freeWalletCount 399, blok 133028622 ~03:01 WIB; 373/555 = 67,20% pada blok 133026650 ~02:45 WIB - "
        "ambang 70% DILEWATI selama run ini); freeMinted 839 token (FREE_PER_WALLET 5, max token gratis 2.775); "
        "(c) slot user TERBUKA (freeCountBy 0, holdsAgentId 1, bal 0). Diskusi terverifikasi: post Boltbook "
        "/p/UPX2BOzGb2a4 (gregrichy.ai, 2026-11-11T19:37:24Z). Velocity GAGAL (bukan syarat strong lead, dicatat saja): "
        "rate token 778->839 = +61/~13 mnt ~4,7/mnt vs interval sebelumnya 511->736 ~10,7/mnt = 0,44x. "
        "TAPI GATE WEBSITE GAGAL -> TIDAK di-preview/di-mint, dilaporkan sekali sebagai strong lead gate-blocked. "
        "Metode gate yang dicoba: (A) pencarian alamat mentah 0 hasil relevan; (B) post Boltbook tanpa link situs; "
        "(C) metadata Sourcify tanpa URL; (H) kontrak tanpa contractURI; (I) tokenURI(1) hanya '1'; (J) ABI tanpa "
        "fungsi situs (satu-satunya URL di ABI adalah referensi EIP-165); (K) GitHub search-index 0 hasil relevan; "
        "(N) author gregrichy.ai tanpa link situs/X di bio; (E) owner 0x7f13f050e6fb278d01537b12379b01e8dbadf5f2 "
        "- SAMA dengan SEVEN; (L) BscScan via browser DIBLOKIR Cloudflare bot-wall (terbukti di SEVEN 02:54-03:00 WIB) "
        "- tidak diulang untuk Eco, INCONCLUSIVE. Status: strong-lead-gate-blocked-2026-11-12.")
    out["notes"].append("Eco promoted to strong lead, gate-blocked")

# --- 6. Stampooor / AgentPals / Moonfang / Pickgrid / SOLACE / NAOMI ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["freeMinted"] = 885
    st["lastReadBlock"] = VBLOCK
    st[NOTE_KEY] = ("Run 0231: freeMinted 885/1200 = 73,75% (was 883); mintStart 2026-11-11 09:00 WIB, umur ~18 jam "
                    "<24 jam; slot user terbuka (freeAvailable 1, bal 0). Situs dicek ulang run ini (curl ~02:45 WIB): "
                    "root 000 + /packs 000 + www 000 - DNS/connect fail TETAP -> gate-blocked, sudah dilaporkan sekali "
                    "run 1901 11 Nov -> TIDAK dilaporkan ulang, TIDAK di-preview/di-mint.")
ap = C.get("AgentPals")
if isinstance(ap, dict):
    ap["freeMinted"] = 300
    ap["lastReadBlock"] = VBLOCK
    ap[NOTE_KEY] = ("Run 0231: freeMinted 300/300 = 100% - free pool HABIS (sudah dicatat run 0131); totalMinted 301; "
                    "bal user 1 (#268). Tidak ada perubahan tier.")
mf = C.get("0x79b0")
if isinstance(mf, dict):
    mf[NOTE_KEY] = ("Run 0231: totalSupply 200/200 sold out, bal user 1 - sudah di-mint parent ~01:25 WIB; "
                    "rekonsiliasi saja, TIDAK dilaporkan ulang.")
pg = C.get("Pickgrid")
if isinstance(pg, dict):
    pg[NOTE_KEY] = ("Run 0231: freeMinted 216/300 = 72% (totalSupply 218) - di atas ambang strong lead 70% TAPI umur "
                    "TETAP UNVERIFIED (launchNote: first-mint tidak terverifikasi, Ankr 401; kontrak tanpa "
                    "mintStart/mintOpenedAt; tidak ada di front page Boltbook run ini) -> TIDAK BISA promosi. "
                    "Slot user terbuka (bal 0). Tetap watchlist-only.")
sol = C.get("SOLACE")
if isinstance(sol, dict):
    sol[NOTE_KEY] = ("Run 0231: baca segar verify-new (blok 133026851): totalSupply 5.805e24 (raw, token desimal), "
                     "MAX_SUPPLY 1e27, mintStart 1794333906 = 2026-11-11 19:05 WIB; freeClaimed/freeMinted/free views "
                     "TIDAK ADA (None) - kuota gratis tidak bisa diverifikasi on-chain. Post Agentboard klaim free mint "
                     "live 34/4.444, TAPI tanpa free view on-chain status 'paid-only' DIPERTAHANKAN; bukan lead/kandidat. "
                     "Dicatat sebagai diskrepansi, bukan promosi.")
naomi = C.get("checked-0xC7Ad-2001")
if isinstance(naomi, dict):
    naomi[NOTE_KEY] = ("Run 0231: freeMinted 777/777 = sold out terkonfirmasi segar (totalMinted 782, paid 5, blok "
                      "133026851) - klaim The Colony '338 of 777 free slots remain' BASI/SALAH. Status "
                      "checked-free-pool-sold-out dipertahankan.")

# --- 7. top-level run note ---
summary = (
    "Run 0231 (2026-11-12 02:31 WIB, eksekusi ~02:40-03:05 WIB): 2 STRONG LEAD BARU, keduanya GATE-BLOCKED "
    "(dilaporkan sekali, TIDAK di-preview/di-mint): SEVEN 837/1111 = 75,34% dan Eco 399/555 wallet = 71,89%. "
    "0 kandidat baru, 0 track-B dibuka, 0 track-C lead/kandidat baru, 0 EARLY LEAD BARU. Pre-flight FAIL (Ankr HTTP 401, "
    "outage sejak 9 Nov) - scan leg fast-fail, watermark TIDAK dimajukan (tetap 132512564); 5c dilewati. Reread 62 kontrak "
    "(blok 133026215, 116,1 dtk) + 23 track_c: velocity 0 LOLOS (terbesar BYTEBLOOM +44, minted-by-user; SOLDERCATS +19; "
    "batch-fail/all-null: Stampooor, 0x7Eb9, GangDotFun, Skywe Legion, AgentPals - nilai lama dipertahankan, verify-new menutup). "
    "Track_c: 0x5f76 + VISION totalSupply naik, 11-11 freeMinted 631->646. Verify-new (blok 133026851): MECHA 1022/4444 = 23,0%; "
    "BUCKET 598 (mintOpenedAt 2026-11-11 21:16 WIB, umur terverifikasi); MOONDRILL 71; CRTSAINTS 61; NAOMI 777/777 sold out "
    "(Colony '338 remain' basi); AGCR 2378/2400 = 99,08% umur TETAP UNVERIFIED; WFPASS belum launch (saleStart 06:00 WIB 12 Nov); "
    "S1-6C50 100/100; S1-0895 111; BB-7c71 549; Life Cards 16 (mintStart ~23:29 WIB 11 Nov); Stampooor 885/1200 = 73,75%; "
    "AgentPals 300/300 habis; Moonfang 200/200; Pickgrid 216/300 = 72% tapi umur UNVERIFIED (tidak promosi); SUDOSAINTS 658; "
    "SOLACE tanpa free view (paid-only dipertahankan, post klaim free live tidak terverifikasi on-chain). SEVEN: mintOpensAt "
    "1794415297 = 2026-11-11 23:41:37 WIB (KOREKSI run 0201: umur TERVERIFIKASI, bukan unverified); free 826->837/1111; slot terbuka; "
    "gate GAGAL (A/B/C/G/H/I/J/K/M/N negatif; L BscScan diblokir Cloudflare bot-wall 02:54-03:00 WIB, inconclusive); owner "
    "0x7f13... sama dengan Eco. Eco: freeWalletCount 373->399/555 (67,20% -> 71,89%, lewati 70% selama run); diskusi terverifikasi "
    "(Boltbook /p/UPX2BOzGb2a4); velocity GAGAL (0,44x); gate GAGAL (metode sama, L tidak diulang - bot-wall terbukti). "
    "Sourcify feed 20 kontrak (verified 19:00-19:45 UTC), 2 baru (0x75F4, 0x95CA) - keduanya BUKAN S1/S2/early. Boltbook EN 45.017 "
    "byte/6 alamat, ZH 43.102 byte/7 alamat; 0 baru. Bridge: 0 temuan pelengkap baru (116 kontrak, 7 discarded). Binanceai "
    "launched()=false (tetap refund phase). RigForge: freeSharesLeft 679, openedAt 0 (belum buka), freeClaimed 321, "
    "freeBooked(user) 10000 RIG utuh. Sweep EN+ZH: 0 proyek baru (Solace paid-only di snapshot; NAOMI sold out on-chain; "
    "Agentic Gangster/RIGBYPASS/Horus free pool habis). Route 6: Odaily 200 + PANews 200, 0 item Agent ID/free-mint."
)
snap["runNote0231_1112"] = summary
snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["last_run_note"] = ("Run 0231: 2 strong lead BARU, keduanya GATE-BLOCKED (tidak di-mint): SEVEN 837/1111 = 75,34% "
                         "(umur terverifikasi 23:41 WIB 11 Nov) dan Eco 399/555 wallet = 71,89% (umur terverifikasi "
                         "01:11 WIB 12 Nov). Keduanya tanpa website terverifikasi; owner sama 0x7f13...; BscScan "
                         "diblokir Cloudflare. Stampooor 885/1200 = 73,75% situs tetap DNS fail. Scan FAST-FAIL (Ankr 401). "
                         "RigForge belum buka (679). binanceai launched()=0.")
tmp = BASE + "onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")
json.dump(out, open(BASE + "run-2026-11-12-0231-merge.json", "w"), indent=1)
print("SNAPSHOT WRITTEN, contracts:", len(C), "track_c:", len(TC))
print("MERGE:", json.dumps({k: v for k, v in out.items() if k != "verify_notes"}, indent=1)[:1200])
