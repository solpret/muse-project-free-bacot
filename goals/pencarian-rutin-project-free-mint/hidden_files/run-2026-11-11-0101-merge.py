#!/usr/bin/env python3
"""Merge run 0101 reread+vel+legs into snapshot. Read-only except snapshot +
hot-leg-seen.json (dedupe for the 4 new early leads).
Run 0101 (jadwal 01:01 WIB 2026-11-11). Age-excluded entries are kept as
tombstones (status age-excluded-2026-11-11), like prior runs."""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-11-0101"
NOW = "2026-11-11 01:01 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
legs = json.load(open(f"{BASE}/run-{TS}-legs.json"))
BLOCK = rr.get("block")
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0101-premerge")

updated = 0
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    row = vel.get("rows", {}).get(name, {})
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    if row.get("minted") is not None:
        entry["previousTotalSupply"] = row.get("prev")
        entry["mintedInInterval"] = row.get("minted")
        entry["intervalMinutes"] = INTERVAL
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1
print(f"contracts updated: {updated}")

tc_updated = 0
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("track_c", {}).get(name)
    if not f:
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    tc_updated += 1
print(f"track_c updated: {tc_updated}")

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote0101_1111"] = text

def dyn_note(name, extra_txt=""):
    row = vel.get("rows", {}).get(name, {})
    f = rr.get("reread", {}).get(name, {})
    e = snap["contracts"].get(name, {})
    if not row:
        return None
    minted = row.get("minted"); rate = row.get("rate"); ratio = row.get("ratio")
    passes = row.get("passes")
    fm = f.get("freeMinted"); fc = f.get("freeClaimed")
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP") or e.get("agentFreeCap") or e.get("MAX_SUPPLY")
    freetxt = ""
    if fm is not None and cap and cap < 10**12:
        freetxt = f"; freeMinted {fm}/{cap} = {fm/cap*100:.1f}%"
    elif fc is not None and cap and cap < 10**12:
        freetxt = f"; freeClaimed {fc}/{cap} = {fc/cap*100:.1f}%"
    vtxt = "velocity LOLOS" if passes else "velocity GAGAL"
    return (f"Run 0101 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

# ---- SOLDERCATS: probe segar run ini ----
sc = snap["contracts"].get("SOLDERCATS")
if isinstance(sc, dict):
    p = legs.get("probe", {}).get("SOLDERCATS", {})
    if p.get("totalSupply") is not None:
        sc["totalSupply"] = p["totalSupply"]
    if p.get("agentFreeUsed") is not None:
        sc["agentFreeUsed"] = p["agentFreeUsed"]
        sc["agentFree"] = p["agentFreeUsed"]
    sc["runNote0101_1111"] = (
        f"Run 0101: probe segar (nodereal, blok ~{BLOCK}): totalSupply {p.get('totalSupply')} "
        f"(was 414 run 0031), agentFreeUsed {p.get('agentFreeUsed')}/2000 = "
        f"{(p.get('agentFreeUsed') or 0)/2000*100:.2f}% (masih <25% strong lead). Re-read +12/30 mnt = "
        f"0,40/mnt, velocity ratio 0,63 GAGAL run ini. mintOpen 1, "
        f"mintStart 1794321310 = 2026-11-10 21:35 WIB (umur ~3,4 jam TERVERIFIKASI <24 jam), slot user "
        f"TERBUKA (agentFreeByWallet 0, balanceOf 0). Website SUDAH terverifikasi (metode H). "
        f"Tetap early lead; re-read totalSupply 426 (blok {BLOCK}).")
    print("SOLDERCATS updated (still early)")

# ---- NIGHTFORGE: gate rechecked, still failed ----
nf = snap["contracts"].get("NIGHTFORGE")
if isinstance(nf, dict):
    p = legs.get("probe", {}).get("NIGHTFORGE", {})
    if p.get("totalSupply") is not None:
        nf["totalSupply"] = p["totalSupply"]
    if p.get("agentFreeUsed") is not None:
        nf["agentFreeUsed"] = p["agentFreeUsed"]
    nf["runNote0101_1111"] = (
        f"Run 0101: totalSupply {p.get('totalSupply')} (was 678 run 0031), agentFreeUsed "
        f"{p.get('agentFreeUsed')}/2000 = {(p.get('agentFreeUsed') or 0)/2000*100:.1f}% (tetap >=25% strong "
        f"lead). Gate DICEK ULANG run ini (metode H + I + J + G): nightforge.pages.dev home + "
        f"/meta/collection.json + /llms.txt + /skill.md + /launch.json + /agent.json SEMUA tetap halaman "
        f"infografis medis yang sama (23.809 byte, 0 kecocokan kontrak); ABI Sourcify exact_match 87 fns "
        f"tanpa fungsi site/URL (metode J, hanya eip712Domain); pencarian nama proyek tanpa hasil situs "
        f"(metode G) -> gate TETAP GAGAL, TIDAK di-preview/TIDAK di-mint. Status tetap "
        f"strong-lead-gate-blocked-2026-11-10 (sudah dilaporkan sekali run 2131; tidak dilaporkan ulang). "
        f"Deadline umur 2026-11-11 14:36 WIB.")
    print("NIGHTFORGE gate rechecked (still failed)")

note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user-2026-11-02; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") + " Minted-by-user-2026-11-01; tanpa perubahan.")
note("BYTEBLOOM", (dyn_note("BYTEBLOOM") or "") + " Minted-by-user run 2201 (#508); slot terpakai; tanpa perubahan.")
note("EMBERANVIL", (dyn_note("EMBERANVIL") or "") + " Minted-by-user-2026-11-10 (#946); tanpa perubahan.")
note("KERNELMONK", (dyn_note("KERNELMONK") or "") + " Minted-by-user-2026-11-10 (#509); tanpa perubahan.")
note("Lanternfield", (dyn_note("Lanternfield") or "") + " Minted-by-user-2026-11-10 (#516); tanpa perubahan.")
note("Cosmic Sentinel", (dyn_note("Cosmic Sentinel") or "") +
     " Early lead; freeMinted 372/225.000 = 0,17% (jauh <25%); umur UNVERIFIED; tanpa perubahan.")
note("ORBITJANITOR", (dyn_note("ORBITJANITOR") or "") +
     " Minted-by-user run 0001 (#552); re-read 592->605 (+13, velocity GAGAL 0,33x); tanpa perubahan.")
note("Claf Eye", (dyn_note("Claf Eye") or "") +
     " Early lead; +13 interval ini, velocity GAGAL (0,52x). Free% + umur + website UNVERIFIED. Tetap early lead.")
note("STALL", (dyn_note("STALL") or "") +
     " Early lead; +17 interval ini, velocity GAGAL (0,40x). Free% + umur UNVERIFIED. Tetap early lead.")
note("THYRK", (dyn_note("THYRK") or "") +
     " Minted-by-user-2026-11-10 (20 THYRK, pending swap, tanpa pair PCS V2); +11 interval ini, "
     "velocity GAGAL (minted <20). Tanpa perubahan.")

# ---- Age exclusions: window 00:31 -> 01:01 WIB (launch epoch 1794245455..1794247255) ----
WIN_LO, WIN_HI = 1794245455, 1794247255
TERMINAL = ("sold-out", "age-excluded", "minted-by-user", "excluded", "promotion-discarded",
            "same-owner-discarded", "paid-only", "upcoming")
newly_excluded = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    st = str(entry.get("status") or "")
    if any(x in st for x in TERMINAL):
        continue
    launch = entry.get("mintStart") or entry.get("saleStart") or entry.get("launchTime")
    if isinstance(launch, (int, float)) and WIN_LO <= launch <= WIN_HI:
        newly_excluded.append((name, launch))
print(f"age-exclusion window check: {newly_excluded if newly_excluded else '0 baru'}")

# ---- 4 EARLY LEADS BARU run ini (Boltbook nicodart.ai 00:21 WIB + modemeta/nanomind RIMEVAULT) ----
# Semua: template pabrik 87-fn exact_match, AGENT_FREE_CAP 2000, mint(1) value 0 = 1 free/wallet,
# mint(2+) 0.00097 BNB (RIMEVAULT; pola sama di keluarga ini). Umur TERVERIFIKASI <24 jam via
# mintStart on-chain + first mint ~00:20 WIB (blok 132815069-132815095). Free% 18,8-22,5% (<25%),
# slot user TERBUKA (agentFreeByWallet 0, balanceOf 0), website TERVERIFIKASI metode H
# (contractURI -> <project>.pages.dev -> /llms.txt atau /agent.json mencetak kontrak persis).
# Diskusi publik: post Boltbook nicodart.ai 00:21 WIB (4 mint gratis, tx terverifikasi) +
# modemeta.ai + nanomind.ai (RIMEVAULT). BUKAN strong lead (free% <25%), BUKAN kandidat
# (velocity baseline baru dicatat run ini). TIDAK pernah di-preview/di-mint (early lead).
FOUR = {
    "REWINDCLUB": {
        "address": "0x39b451abbd53365e2277084cb60f9a2c5ad6e698",
        "symbol": "DECK", "kind": "ERC721",
        "totalSupply": 376, "agentFreeUsed": 376, "paidMinted": 0,
        "AGENT_FREE_CAP": 2000, "MAX_SUPPLY": 4000, "mintOpen": 1,
        "mintStart": 1794322145, "mintEnd": 1794926945,
        "firstSeenBlock": 132815069, "firstMintTx": "0x7298ced4e12474bdd221bb3eae53d58a244c1af1c44ab33d44e5b61c2f33d2d0",
        "mintTokenId": 278, "website": "https://rewindclub.pages.dev",
        "websiteEvidence": "Metode H: contractURI() -> https://rewindclub.pages.dev/meta/collection.json; /llms.txt mencetak 'Contract address: 0x39b451abbd53365e2277084cb60f9a2c5ad6e698' (952 byte).",
        "launchNote": "VERIFIED <24 jam: mintStart on-chain 1794322145 = 2026-11-10 21:49 WIB; first mint terverifikasi blok 132815069 ~2026-11-11 00:20 WIB (tx nicodart.ai #278). Umur ~3,2 jam saat run 0101.",
        "baselineNote": "EARLY lead dilaporkan sekali run 0101. Free 376/2000 = 18,8% (<25% strong lead). Slot user TERBUKA (agentFreeByWallet 0, balanceOf 0). Website TERVERIFIKASI (H). X discussion: Boltbook nicodart.ai 00:21 WIB. Velocity baseline dicatat run ini (pace Boltbook: #278 ~00:20 -> 376 ~01:25, ~1,5/mnt); perbandingan velocity baru run berikut.",
    },
    "LCDSPRITE": {
        "address": "0xf341806c87b1ae196e67cea3c0dad75021f1ed92",
        "symbol": "SPRITE", "kind": "ERC721",
        "totalSupply": 421, "agentFreeUsed": 421, "paidMinted": 0,
        "AGENT_FREE_CAP": 2000, "MAX_SUPPLY": 3333, "mintOpen": 1,
        "mintStart": 1794322332, "mintEnd": 1794927132,
        "firstSeenBlock": 132815078, "firstMintTx": "0x64ac30f7e91586ab194f49dd714996f4ac1e1a4114c5f3ea7bcb28777efe15fa",
        "mintTokenId": 318, "website": "https://lcdsprite.pages.dev",
        "websiteEvidence": "Metode H: contractURI() -> https://lcdsprite.pages.dev/meta/collection.json; /llms.txt mencetak 'Contract address: 0xf341806c87b1ae196e67cea3c0dad75021f1ed92' (869 byte).",
        "launchNote": "VERIFIED <24 jam: mintStart on-chain 1794322332 = 2026-11-10 21:52 WIB; first mint terverifikasi blok 132815078 ~2026-11-11 00:20 WIB (tx nicodart.ai #318). Umur ~3,1 jam saat run 0101.",
        "baselineNote": "EARLY lead dilaporkan sekali run 0101. Free 421/2000 = 21,1% (<25% strong lead). Slot user TERBUKA (agentFreeByWallet 0, balanceOf 0). Website TERVERIFIKASI (H). X discussion: Boltbook nicodart.ai 00:21 WIB. Velocity baseline dicatat run ini (pace Boltbook: #318 ~00:20 -> 421 ~01:25, ~1,6/mnt); perbandingan velocity baru run berikut.",
    },
    "RIMEVAULT": {
        "address": "0x96e879c79b1191a0954022c7483c44b2ee522ba1",
        "symbol": "VAULT", "kind": "ERC721",
        "totalSupply": 416, "agentFreeUsed": 416, "paidMinted": 0,
        "AGENT_FREE_CAP": 2000, "MAX_SUPPLY": 5555, "mintOpen": 1,
        "mintStart": 1794320879, "mintEnd": 1794925679,
        "firstSeenBlock": 132815086, "firstMintTx": "0x1fc7ce577791fa21d9a9189ff7c9a5e5463db91fa32550fa11f1d7cbf12c488a",
        "mintTokenId": 296, "website": "https://rimevault.pages.dev",
        "websiteEvidence": "Metode H: contractURI() -> https://rimevault.pages.dev/meta/collection.json; /agent.json mencetak '\"contract\": \"0x96e879c79b1191a0954022c7483c44b2ee522ba1\"'. (/llms.txt + home TIDAK mencetak kontrak; identity cocok: supply 5.555, harga 0,00097 BNB, free lane 1/wallet.)",
        "launchNote": "VERIFIED <24 jam: mintStart on-chain 1794320879 = 2026-11-10 21:28 WIB (juga dinyatakan di /llms.txt: mint window 10 Nov 21:28 -> 17 Nov 21:28 WIB); first mint terverifikasi blok 132815086 ~2026-11-11 00:20 WIB (tx nicodart.ai #296). Umur ~3,5 jam saat run 0101.",
        "baselineNote": "EARLY lead dilaporkan sekali run 0101. Free 416/2000 = 20,8% (<25% strong lead). Slot user TERBUKA (agentFreeByWallet 0, balanceOf 0). Website TERVERIFIKASI (H via /agent.json). X discussion: Boltbook nicodart.ai 00:21 WIB + modemeta.ai first read + nanomind.ai follow-up (322->365/30 mnt). Velocity baseline dicatat run ini (pace: 302->322/7 mnt, 322->365/30 mnt, 365->416/~27 mnt); perbandingan velocity baru run berikut. Mint(1) value 0 sims clean (nanomind, 2 RPC); mint(2) value 0 revert WrongPayment 0,00097 BNB.",
    },
    "MYCELIX": {
        "address": "0xb1636010fb87f50574f76f6644b7cd306a6a4d1f",
        "symbol": "SHROOM", "kind": "ERC721",
        "totalSupply": 450, "agentFreeUsed": 450, "paidMinted": 0,
        "AGENT_FREE_CAP": 2000, "MAX_SUPPLY": 5000, "mintOpen": 1,
        "mintStart": 1794322052, "mintEnd": 1794926852,
        "firstSeenBlock": 132815095, "firstMintTx": "0x6d68dfd7fea7082403c8d663e4458884d36d7f5ec13f64470080da68cd6e2bea",
        "mintTokenId": 400, "website": "https://mycelix.pages.dev",
        "websiteEvidence": "Metode H: contractURI() -> https://mycelix.pages.dev/meta/collection.json; /llms.txt mencetak 'Contract address: 0xb1636010fb87f50574f76f6644b7cd306a6a4d1f' (851 byte).",
        "launchNote": "VERIFIED <24 jam: mintStart on-chain 1794322052 = 2026-11-10 21:47 WIB; first mint terverifikasi blok 132815095 ~2026-11-11 00:20 WIB (tx nicodart.ai #400). Umur ~3,2 jam saat run 0101.",
        "baselineNote": "EARLY lead dilaporkan sekali run 0101. Free 450/2000 = 22,5% (<25% strong lead). Slot user TERBUKA (agentFreeByWallet 0, balanceOf 0). Website TERVERIFIKASI (H). X discussion: Boltbook nicodart.ai 00:21 WIB. Velocity baseline dicatat run ini (pace Boltbook: #400 ~00:20 -> 450 ~01:25, ~0,8/mnt); perbandingan velocity baru run berikut.",
    },
}
for name, v in FOUR.items():
    e = {
        "address": v["address"],
        "name": name,
        "symbol": v["symbol"],
        "kind": v["kind"],
        "status": "early-lead-reported-2026-11-11",
        "totalSupply": v["totalSupply"],
        "agentFreeUsed": v["agentFreeUsed"],
        "paidMinted": v["paidMinted"],
        "AGENT_FREE_CAP": v["AGENT_FREE_CAP"],
        "FREE_SUPPLY": v["AGENT_FREE_CAP"],
        "MAX_SUPPLY": v["MAX_SUPPLY"],
        "mintOpen": v["mintOpen"],
        "mintStart": v["mintStart"],
        "mintEnd": v["mintEnd"],
        "balanceOf_user": 0,
        "agentFreeByWallet_user": 0,
        "userSlotNote": "Slot TERBUKA (agentFreeByWallet(user)=0, balanceOf(user)=0, baca segar run 0101).",
        "firstSeenBlock": v["firstSeenBlock"],
        "firstMintTx": v["firstMintTx"],
        "mintTokenId": v["mintTokenId"],
        "website": v["website"],
        "websiteEvidence": v["websiteEvidence"],
        "launchNote": v["launchNote"],
        "baselineNote": v["baselineNote"],
        "xVerified": False,
        "velocityVerified": False,
        "velocityLegPasses": False,
        "previousTotalSupply": None,
        "mintedInInterval": None,
        "intervalMinutes": INTERVAL,
        "currentRatePerMin": None,
        "velocityRatio": None,
        "supplyView": "totalSupply",
        "lastReadBlock": BLOCK,
        "lastReadWib": NOW,
        "runNote0101_1111": f"Run 0101: {v['baselineNote']}",
    }
    snap["contracts"][name] = e
    print(f"added early lead {name} ({v['address']})")

# ---- hot-leg-seen dedupe for the 4 early leads (supaya hot leg tidak melaporkannya lagi) ----
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
now_iso = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
added = 0
for name, v in FOUR.items():
    a = v["address"]
    if a.lower() in {k.lower() for k in seen}:
        continue
    seen[a] = {"first_seen_wib": now_iso,
               "note": f"EARLY lead reported run 0101 (Boltbook nicodart.ai 00:21 WIB + on-chain verify); free {v['agentFreeUsed']}/2000; website verified (H); TIDAK preview/mint (early lead).",
               "source": "free-mint-search-0101", "status": "early-lead-reported-2026-11-11"}
    added += 1
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"))
print(f"hot-leg-seen: +{added} -> {len(seen)}")

# ---- Top-level run notes ----
vel_passes = vel.get("passes", [])
snap["last_run_wib"] = NOW
snap["last_run"] = 1
snap["runNote0101_1111"] = (
    f"Run 0101 (2026-11-11 01:01 WIB, blok re-read {BLOCK}): re-read {updated} kontrak + {tc_updated} "
    f"track_c (bsc-dataseed, 884,5 dtk). EMPAT EARLY LEAD BARU (dilaporkan sekali run ini): REWINDCLUB "
    f"376/2000 = 18,8%, LCDSPRITE 421/2000 = 21,1%, RIMEVAULT 416/2000 = 20,8%, MYCELIX 450/2000 = 22,5% "
    f"(semua <25% strong lead; umur TERVERIFIKASI ~3,1-3,5 jam; slot user TERBUKA; website TERVERIFIKASI "
    f"metode H; diskusi Boltbook 00:21 WIB; velocity baseline dicatat run ini). 0 kandidat baru, 0 strong "
    f"lead baru, 0 track-C lead/kandidat baru, 0 track-B claim. SOLDERCATS tetap early (probe 427/2000 = "
    f"21,35%; re-read +12, velocity GAGAL 0,63x). NIGHTFORGE gate dicek ulang (H+I+J+G), tetap gagal "
    f"(nightforge.pages.dev masih infografis medis 23.809 byte, 0 kecocokan kontrak; strong lead 34,0% "
    f"TETAP gate-blocked, tidak di-mint; deadline umur 2026-11-11 14:36 WIB). Velocity LOLOS run ini: "
    f"{vel_passes} (VOLT token bridge = artefak ERC-20 + BAGENT = token mining, bukan sinyal kandidat). "
    f"AGE-EXCLUSIONS: window 00:31->01:01 WIB: {len(newly_excluded)} baru.")
snap["runNote0101_1111_scan"] = (
    "Run 0101 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs (eth_blockNumber) HTTP 401 Unauthorized "
    "(outage sejak ~13:33 WIB 2026-11-09 berlanjut, kini ~36 jam; kuota Ankr 0% s.d. 1 Des 2026). Watermark "
    f"TIDAK dimajukan (tetap 132512564; gap ke head {BLOCK - 132512564} blok). Route 5c: tanpa output scan "
    "baru (tidak ada ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote0101_1111_binanceai"] = (
    "Run 0101 track-B: binanceai.fun TIDAK BERUBAH - launched()=0 (nodereal), tokenClaimed(user) gagal "
    "baca run ini (execution reverted, degradasi; nilai lama 0 dipertahankan), token balanceOf(user)=0. "
    "Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang. pending_claims kosong.")
snap["runNote0101_1111_age_exclusions"] = (
    f"Run 0101 age-exclusions (aturan <24 jam): window 00:31->01:01 WIB: "
    f"{len(newly_excluded)} BARU {newly_excluded if newly_excluded else ''}. Tidak ada audit backlog baru run ini.")
snap["runNote0101_1111_discovery"] = (
    "Run 0101 discovery: Sourcify feed 20 terbaru (verified 17:35:46-18:04:14Z), 0 baru vs hot-leg-seen "
    "(semua sudah dicek hot leg) -> 0 sale-shape, 0 early lead dari feed. Boltbook EN 44.935 byte + ZH "
    "45.249 byte, 8 alamat unik: 2 tx-hash (bukan kontrak), RIMEVAULT, ORBITJANITOR, Hackou Coin Pass, "
    "BOLT, wallet maranggi.ai. BARU: 4 mint gratis nicodart.ai 00:21 WIB (REWINDCLUB #278, LCDSPRITE #318, "
    "RIMEVAULT #296, MYCELIX #400; semua value 0, receipt 0x1) -> 4 EARLY LEAD (kontrak dari receipt tx, "
    "verifikasi on-chain segar run ini; TIDAK preview/mint). Sweep EN+ZH: Agentic Gangster free sold out "
    "111/111; MOLT free habis; Horus Phase 1 free sold out 2.000; Ptah draw window lewat; AGENT COSMOS sudah "
    "di snapshot (ACOS-3aed); First-Dollar Grove sudah di snapshot (age-excluded); Subsonic Tribe dkk. lama. "
    "DICK = paid-only share sale (0,002 BNB/share, deadline 17 Nov) -> bukan lead, dicatat saja. UFO: claim "
    "butuh signature EIP-712 off-chain (bukan auto-claim), tanpa alamat kontrak di post -> dicatat saja. "
    "AGTC 996/1.000 hampir sold out, tanpa kontrak -> tidak diverifikasi. Rute 6: Odaily 264.108 byte + "
    "PANews 119.552 byte, hanya sebutan 'Binance' generik, 0 keyword Agent ID/free mint/free share. Bridge: "
    "116 kontrak, mtime 2026-11-09 01:21 WIB (STALE); tidak ada temuan pelengkap baru. Track_c: 6 perubahan "
    "kecil tanpa promosi (AGENT MALTA, NUSA 385->387 age-excluded, 0x5f76cAb7, JINMA 658->656 minted-by-user, "
    "VISION, 0x38491597 378->376 minted-by-user).")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT MERGED run 0101")
