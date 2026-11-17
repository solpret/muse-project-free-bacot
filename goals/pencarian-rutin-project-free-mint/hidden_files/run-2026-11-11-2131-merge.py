#!/usr/bin/env python3
"""Merge run 2131 (scheduled 2026-11-11 21:31 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-2131-reread.json (62 contracts + 23 track_c; head block
132985070), run-2026-11-11-2131-legs.json, run-2026-11-11-2131-shape5.json,
run-2026-11-11-2131-verify-new.json. Writes snapshot (with .bak).
0 kandidat baru, 0 strong lead baru, 0 track-B dibuka, 0 track-C lead baru.
0 early lead BARU dari job ini (BUCKET/MOONDRILL/0x2e50/CRTSAINTS sudah
dilaporkan hot-leg 2114/2049; run ini menambahkan mereka ke snapshot
watchlist pada bacaan pertama job utama + verifikasi segar).
Age: RIMEVAULT (deadline 21:28) + SOLDERCATS (deadline 21:35) melewati 24 jam
run ini TAPI status minted-by-user (sudah dimiliki) -> tetap dilacak seperti
HIVE/Bubblebruin/Zapcourier (praktik mapan: age-exclusion berlaku untuk
watchlist aktif, bukan holdings yang sudah di-mint; preseden ABYSSCABLE
adalah item watchlist non-minted). Dicatat eksplisit di runlog + snapshot.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-2131-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-2131-legs.json"))
shape5 = json.load(open(BASE + "run-2026-11-11-2131-shape5.json"))
verify = json.load(open(BASE + "run-2026-11-11-2131-verify-new.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2131-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
TS = "2026-11-11 21:31 WIB"

def vel(name, new_supply, interval=30.0):
    e = C.get(name)
    if not isinstance(e, dict): return None
    old = e.get("totalSupply")
    if old is None or new_supply is None: return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / interval, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = interval
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = round(rate / prev_rate, 2) if prev_rate and prev_rate > 0 else None
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

vel_pass, vel_fail, batch_fail = [], [], []
for name, d in reread["reread"].items():
    if name not in C: continue
    e = C[name]
    if d.get("_batch_fail"):
        batch_fail.append(name)
        e["runNote2131_1111"] = ("Run 2131 (blok %s): baca batch GAGAL (transport) - nilai lama "
            "dipertahankan, BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None: ns = d.get("totalMinted")
    if ns is not None:
        r = vel(name, ns)
        if r and e.get("velocityLegPasses"): vel_pass.append((name, r))
        elif r: vel_fail.append((name, r))
    else:
        e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
    for k in ("totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None: e[k] = d[k]
    if d.get("totalSupply") is not None: e["totalSupply"] = d["totalSupply"]

def note(name, text):
    if isinstance(C.get(name), dict):
        C[name]["runNote2131_1111"] = text

st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["status"] = "strong-lead-gate-blocked-2026-11-11"
    note("Stampooor Stamp Packs",
     "Run 2131: freeMinted 855->860/1200 = 71,67% (>70%, tetap strong lead); umur TERVERIFIKASI <24 jam "
     "(mintStart 1794362419 = 11 Nov 09:00:19 WIB; deadline ~09:00 WIB 12 Nov); slot user TERBUKA (balanceOf 0, "
     "mintOpen 1). Velocity +5/30 mnt GAGAL - tidak relevan untuk strong-lead direct mint. GATE WEBSITE tetap "
     "GAGAL (sudah dilaporkan sekali run 1901; gate-blocked-recheck menangani cek ulang situs). TIDAK di-preview, "
     "TIDAK di-mint, TIDAK dilaporkan ulang (tidak ada perubahan tier).")

note("0x7Eb9", "Run 2131: totalMinted 960->966 (+6, <20) velocity GAGAL; balanceOf(user)=0. Tetap early-lead-reported; BUKAN promosi.")
note("Kitebots", "Run 2131: totalSupply 1234->1238 (+4, <20) velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint.")
note("RIMEVAULT", "Run 2131: totalSupply 1057->1065 (+8, <20) velocity GAGAL; balanceOf=1 (minted-by-user). "
     "DEADLINE UMUR 24 JAM LEWAT run ini (mintStart 2026-11-10 21:28 WIB -> deadline 21:28 WIB 11 Nov; run 21:31 WIB). "
     "TETAP DILACAK: status minted-by-user (sudah dimiliki, bukan kandidat aktif) - age-exclusion berlaku untuk watchlist aktif, "
     "bukan holdings yang sudah di-mint (praktik mapan: HIVE/Bubblebruin/Zapcourier tetap dibaca ulang berminggu-minggu pasca-launch; "
     "preseden ABYSSCABLE adalah item watchlist non-minted). BUKAN kandidat, TIDAK dilaporkan ulang.")
note("MYCELIX", "Run 2131: totalSupply 619->621 (+2, <20) velocity GAGAL; balanceOf(user)=1 (minted-by-user). Deadline umur ~21:47 WIB hari ini (belum lewat saat run).")
note("SOLDERCATS", "Run 2131: totalSupply 543->546 (+3, <20) velocity GAGAL; balanceOf(user)=1. "
     "DEADLINE UMUR 24 JAM LEWAT run ini (mintStart 2026-11-10 21:35:10 WIB -> deadline 21:35 WIB 11 Nov; run 21:31 WIB baru mendekati - "
     "tepatnya deadline lewat ~4 menit sesudah run dimulai). Sama seperti RIMEVAULT: minted-by-user -> TETAP DILACAK, bukan age-excluded, bukan kandidat.")
note("LCDSPRITE", "Run 2131: totalSupply 582->582 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:52 WIB hari ini.")
note("REWINDCLUB", "Run 2131: totalSupply 562->562 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:49 WIB hari ini.")
note("RAMRAIDERS", "Run 2131: totalSupply 562->565 (+3) velocity GAGAL; balanceOf(user)=0. Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur konservatif ~00:30 WIB 12 Nov.")
note("HANAMI BLOOM", "Run 2131: totalSupply 110->110 (+0) velocity GAGAL; balanceOf(user)=0. Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur ~12:59 WIB 12 Nov.")
note("BYTEBLOOM", "Run 2131: totalSupply 830->834 (+4, <20) velocity GAGAL; balanceOf(user)=1 (minted-by-user).")
note("Dragon Agent", "Run 2131: totalSupply 932->935 (+3, <20) velocity GAGAL; balanceOf(user)=0.")
note("STALL", "Run 2131: totalSupply 1972->1983 (+11, <20) velocity GAGAL; balanceOf(user)=0.")
note("Foundry Faces", "Run 2131: totalSupply tetap None (view revert), totalMinted 1301->1346 (+45 dalam 30 mnt); "
     "velocity TIDAK dihitung (totalSupply() revert + tidak ada baseline rate tersimpan); free% UNVERIFIED; umur "
     "UNVERIFIED; balanceOf(user)=0. BUKAN promosi - tetap watchlist-only-age-unverified.")
note("AgentPals", "Run 2131: totalSupply 300->301 (+1; free pool sebelumnya SOLD OUT 300/300 - kenaikan 1 di luar cap tercatat, "
     "bukan perubahan tier/slot; balanceOf(user)=1 (#268). Status minted-by-user-2026-11-11; TIDAK dilaporkan ulang. "
     "Keputusan gate metode (I) user ~19:36 WIB tetap berlaku (pantau 3 hari s.d. 14 Nov 2026; metadata worker saja SEMENTARA TIDAK cukup sebagai bukti website).")
note("EMBERANVIL", "Run 2131: totalSupply 1145->1148 (+3, <20) velocity GAGAL; balanceOf(user)=1 (minted-by-user).")

# --- MECHA update (verify-new fresh read, block 132985733) ---
m = C.get("MECHA")
if isinstance(m, dict):
    v = verify["verify"]["MECHA"]
    m["totalMinted"] = v.get("totalMinted"); m["freeClaimed"] = v.get("freeClaimed")
    m["freePctVerified"] = round(100*v["freeClaimed"]/4444, 2) if v.get("freeClaimed") is not None else m.get("freePctVerified")
    m["lastReadBlock"] = verify["block"]; m["lastReadWib"] = TS
    m["runNote2131_1111"] = ("Run 2131 (blok %s): totalMinted 138->199, freeClaimed 199/4444 = 4,48%%; slot TERBUKA "
        "(balanceOf 0, freeUsedBy 0, mintedBy 0, freeAvailable 2). Umur MASIH UNVERIFIED; X UNVERIFIED; website TIDAK "
        "DITEMUKAN (run 2101). Tetap EARLY lead, jauh dari 50%% kandidat / >70%% strong lead; TIDAK di-preview/dimint." % verify["block"])

# --- Hot-leg early leads added to snapshot on first main-job read ---
def add_early(key, addr, v, extra):
    C[key] = {
        "address": addr, "status": "early-lead-reported-2026-11-11",
        "name": key, "kind": "ERC721",
        "totalSupply": v.get("totalSupply"), "totalMinted": v.get("totalMinted"),
        "freeClaimed": v.get("freeClaimed"), "freeMinted": v.get("freeMinted"),
        "FREE_SUPPLY": extra.get("FREE_SUPPLY"), "MAX_SUPPLY": v.get("MAX_SUPPLY"),
        "mintOpen": v.get("mintOpen"), "mintStart": v.get("mintStart") or v.get("mintOpenedAt"),
        "userBalance": v.get("balanceOf_user"), "userMintedBy": v.get("mintedBy_user"),
        "lastReadBlock": verify["block"], "lastReadWib": TS,
        "xVerified": False, "velocityVerified": False,
        "launchNote": extra["launchNote"],
        "baselineNote": extra["baselineNote"],
        "runNote2131_1111": extra["runNote"],
    }
add_early("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA", verify["verify"]["BUCKET"], {
    "FREE_SUPPLY": 3333,
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintOpenedAt on-chain 1794406606 = 2026-11-11 21:16:46 WIB (umur ~15 mnt saat run 2131).",
    "baselineNote": "EARLY lead dilaporkan sekali hot-leg run 21:14 WIB (BUCKET, agentIdRegistry + isAgent + freeUsed + totalFreeCount + mintOpenedAt + PRICE); run utama 2131 menambahkan ke snapshot watchlist + verifikasi segar: totalSupply 62->125, totalFreeCount 125 (semua free), freeUsed(user)=0, isAgent(user)=1, balanceOf(user)=0, MAX_SUPPLY 3333. Free% 125/3333 = 3,75% (jauh di bawah 50% kandidat & >70% strong lead). Website + X + diskusi BELUM terverifikasi. TIDAK PERNAH di-preview/dimint (early lead). Promosi hanya bila 3 kaki strong lead terpenuhi.",
    "runNote": "Run 2131 (blok 132985733): ditambahkan ke snapshot (laporan hot-leg 21:14). totalSupply 125, totalFreeCount 125/3333 = 3,75%; mintOpenedAt 21:16:46 WIB (umur TERVERIFIKASI <24 jam); slot TERBUKA (balanceOf 0, freeUsed 0, isAgent 1). Tetap EARLY; TIDAK di-preview/dimint."})
add_early("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", verify["verify"]["MOONDRILL"], {
    "FREE_SUPPLY": 2000,
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintStart on-chain 1794406225 = 2026-11-11 21:10:25 WIB (umur ~21 mnt saat run 2131).",
    "baselineNote": "EARLY lead dilaporkan sekali hot-leg run 21:14 WIB (MOONDRILL/MINER, keluarga freeMintX: freeMintX/freeMintXWithRef + FIRST_FREE_CAP 2000 + X_FREE_CAP 1000 + freeLeft, TANPA registry); run utama 2131 menambahkan ke snapshot watchlist + verifikasi segar: totalSupply 7->22, firstFreeUsed 22, paidMinted 0, mintOpen 1, balanceOf(user)=0. Free% 22/2000 = 1,10%. Website + X + diskusi BELUM terverifikasi. TIDAK PERNAH di-preview/dimint (early lead).",
    "runNote": "Run 2131 (blok 132985733): ditambahkan ke snapshot (laporan hot-leg 21:14). totalSupply 22, firstFreeUsed 22/2000 = 1,10%; mintStart 21:10:25 WIB (umur TERVERIFIKASI <24 jam); slot TERBUKA (balanceOf 0, paidMinted 0). Tetap EARLY; TIDAK di-preview/dimint."})
add_early("0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", verify["verify"]["0x2e50"], {
    "FREE_SUPPLY": 2000,
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintStart on-chain 1794405623 = 2026-11-11 21:00:23 WIB (umur ~31 mnt saat run 2131).",
    "baselineNote": "EARLY lead dilaporkan sekali hot-leg run 21:14 WIB (0x2e50, keluarga freeMintX, pertama terlihat run utama 21:01 sebagai checked-not-sale-shape saat totalSupply masih 0; first mint TERVERIFIKASI hot-leg 21:14); run utama 2131 menambahkan ke snapshot watchlist + verifikasi segar: totalSupply 7->20, firstFreeUsed 20, paidMinted 0, mintOpen 1, balanceOf(user)=0. Free% 20/2000 = 1,00%. Website + X + diskusi BELUM terverifikasi. TIDAK PERNAH di-preview/dimint (early lead).",
    "runNote": "Run 2131 (blok 132985733): ditambahkan ke snapshot (laporan hot-leg 21:14). totalSupply 20, firstFreeUsed 20/2000 = 1,00%; mintStart 21:00:23 WIB (umur TERVERIFIKASI <24 jam); slot TERBUKA (balanceOf 0, paidMinted 0). Tetap EARLY; TIDAK di-preview/dimint."})
add_early("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", verify["verify"]["CRTSAINTS"], {
    "FREE_SUPPLY": 2000,
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintStart on-chain 1794405023 = 2026-11-11 20:50:23 WIB (umur ~41 mnt saat run 2131).",
    "baselineNote": "EARLY lead dilaporkan sekali hot-leg run 20:49 WIB (CRTSAINTS/SAINT, keluarga freeMintX); run utama 2131 menambahkan ke snapshot watchlist + verifikasi segar: totalSupply 21->29, firstFreeUsed 29, paidMinted 0, mintOpen 1, balanceOf(user)=0. Free% 29/2000 = 1,45%. Website + X + diskusi BELUM terverifikasi. TIDAK PERNAH di-preview/dimint (early lead).",
    "runNote": "Run 2131 (blok 132985733): ditambahkan ke snapshot (laporan hot-leg 20:49). totalSupply 29, firstFreeUsed 29/2000 = 1,45%; mintStart 20:50:23 WIB (umur TERVERIFIKASI <24 jam); slot TERBUKA (balanceOf 0, paidMinted 0). Tetap EARLY; TIDAK di-preview/dimint."})

# --- Track C reread ---
tc_changes = []
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict) or not isinstance(d, dict): continue
    e = TC[name]
    if d.get("_batch_fail"): continue
    for k in ("totalSupply","freeMinted","freeSharesRemaining","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None and e.get(k) != d[k]:
            if k in ("freeMinted","freeSharesRemaining"):
                tc_changes.append((name, k, e.get(k), d[k]))
            e[k] = d[k]
    e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS

# --- RigForge re-check (legs) ---
rig = TC.get("RigForge")
if isinstance(rig, dict):
    rig["freeSharesLeft"] = legs.get("rigforge", {}).get("freeSharesLeft")
    rig["openedAt"] = legs.get("rigforge", {}).get("openedAt")
    rig["freeClaimed"] = legs.get("rigforge", {}).get("freeClaimed")
    rig["freeBooked_user"] = 10000
    rig["lastReadBlock"] = BLOCK; rig["lastReadWib"] = TS

# --- Checked (not leads, never reported as leads) ---
def checked(key, addr, note_text):
    C[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-11", "note": note_text}
s5 = shape5
checked("checked-0xD2fb-2131", "0xD2fb74f382b487E942dC5619581EF8BA8fDca446",
    "Run 2131 shape5 feed-new (verifiedAt 14:38:04Z): 29 fns, has_mint True, has_quote True, agent_ref True, TAPI free_views [] (near-miss S1 - tanpa free-share view). is_token True, is_nft False. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x0982-2131", "0x09828DBC579fA803A975f50065c1254850d0b538",
    "Run 2131 shape5 feed-new (verifiedAt 14:34:32Z): 29 fns, has_mint True, has_quote True, agent_ref True, TAPI free_views [] (near-miss S1). is_token True, is_nft False. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x35C4-2131", "0x35C426d21EF51162BDf5F5F49227107B58b91427",
    "Run 2131 shape5 feed-new (verifiedAt 14:33:10Z): 33 fns, has_mint True, has_quote True, agent_ref True, TAPI free_views [] (near-miss S1). is_token True, is_nft False. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x56ec-2131", "0x56ec4a9A0914570EA6F96E0a53d98f6f8854F040",
    "Run 2131 shape5 feed-new (verifiedAt 14:33:07Z): 39 fns, has_mint False, has_quote True, agent_ref True, free_views []. is_token True, is_nft False. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x4362-2131", "0x43621df3f0a215f507ebbe5ecf530714788bf29f",
    "Run 2131 shape5 Boltbook-new: fn_count 0 (ABI tidak tersedia / Sourcify unverified), tanpa mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")

snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["runNote2131"] = (
    "Run 2131 (blok %s): 0 kandidat baru, 0 strong lead baru, 0 track-B dibuka, 0 track-C lead baru, 0 early lead BARU "
    "dari job ini. Early lead hot-leg ditambahkan ke snapshot watchlist pada bacaan pertama job utama + verifikasi segar: "
    "BUCKET 125/3333 = 3,75%% (mintOpenedAt 21:16:46 WIB, umur TERVERIFIKASI), MOONDRILL 22/2000 = 1,10%% (mintStart 21:10:25 WIB), "
    "0x2e50 20/2000 = 1,00%% (mintStart 21:00:23 WIB), CRTSAINTS 29/2000 = 1,45%% (mintStart 20:50:23 WIB) - semuanya tetap EARLY, "
    "slot terbuka, TIDAK di-preview/dimint. MECHA 199/4444 = 4,48%% (umur MASIH UNVERIFIED). Stampooor tetap strong lead "
    "gate-blocked 860/1200 = 71,67%%, slot terbuka, TIDAK dilaporkan ulang (tanpa perubahan tier). Velocity: 0 lolos "
    "(STALL +11, RIMEVAULT +8, 0x7Eb9 +6, Stampooor +5, Foundry Faces totalMinted 1301->1346 +45 TAPI velocity tidak dihitung - "
    "totalSupply() revert + tanpa baseline rate). Batch fail: 0. Track-C: VISION/0x5f76 totalSupply naik (share baru dicetak, bukan "
    "promosi); lainnya datar. Sourcify feed 20 kontrak (verified 14:22:03-14:38:04Z), 4 baru - 0 S1/S2/early (3 near-miss S1 tanpa "
    "free view: 0xD2fb, 0x0982, 0x35C4; 0x56ec tanpa mint); Boltbook EN 45.172 byte / ZH 43.106 byte, 1 alamat baru 0x4362 "
    "(fn_count 0, checked). Bridge: 116 kontrak, mtime 2026-11-08 18:21 WIB (STALE), 0 not_in_snapshot, 7 same_owner_discarded, "
    "0 temuan pelengkap. Track B: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase). RigForge: freeSharesLeft 684/1000 "
    "(was 685), openedAt 0 (pool BELUM buka), freeClaimed 316, freeBooked(wallet) = 10000 RIG utuh. Scan (route 4): FAST-FAIL "
    "pre-flight Ankr HTTP 401 Unauthorized - outage berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark "
    "TIDAK dimajukan (tetap 132512564); gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM). Track-C 5c dilewati (tidak ada "
    "output scan baru). Sweep EN+ZH: 0 proyek baru (Agentic Gangster free habis 111/111; RIGBYPASS excluded; MOLT AGENT free habis; "
    "Horus AI fase gratis sold out; WNO sudah di track_c; Razor Agent NOT DEPLOYED; First-Dollar Grove age-excluded; Agent Zet free "
    "phase complete; AGENT MAO dikenal/paused). Route 6: Odaily newsflash 0 item Agent ID/free-mint; PANews 0 item. AGE: RIMEVAULT "
    "deadline 21:28 + SOLDERCATS ~21:35 lewat run ini - keduanya minted-by-user -> TETAP DILACAK (bukan age-excluded, bukan kandidat; "
    "lihat runNote2131_1111 masing-masing). Deadline berjalan: MYCELIX ~21:47, REWINDCLUB ~21:49, LCDSPRITE ~21:52 (11 Nov); "
    "RAMRAIDERS konservatif ~00:30 WIB 12 Nov; HANAMI BLOOM ~12:59 WIB 12 Nov; Stampooor ~09:00 WIB 12 Nov." % BLOCK)
snap["runNote2131_scan"] = (
    "Run 2131 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. "
    "Watermark TETAP 132512564; gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM).")
snap["timestamp_wib"] = TS

with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE vel_pass=%s vel_fail_n=%s batch_fail=%s tc_changes=%s" % (vel_pass, len(vel_fail), batch_fail, tc_changes))
print("VEL_FAIL:", vel_fail)
print("TC_CHANGES:", tc_changes)
