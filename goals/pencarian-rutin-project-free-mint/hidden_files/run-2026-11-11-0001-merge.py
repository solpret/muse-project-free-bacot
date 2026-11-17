#!/usr/bin/env python3
"""Merge run 0001 reread+vel+legs into snapshot. Read-only except snapshot +
hot-leg-seen.json (dedupe for the 11 newly shape-checked contracts).
Run 0001 (jadwal 23:31 WIB)."""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-11-0001"
NOW = "2026-11-11 00:01 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
legs = json.load(open(f"{BASE}/run-{TS}-legs.json"))
BLOCK = rr.get("block")
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0001-premerge")

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
        e["runNote0001_1111"] = text

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
    return (f"Run 0001 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
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
    sc["runNote0001_1111"] = (
        f"Run 0001: probe segar (nodereal, blok ~{BLOCK}): totalSupply {p.get('totalSupply')} "
        f"(was 373 run 2331), agentFreeUsed {p.get('agentFreeUsed')}/2000 = "
        f"{(p.get('agentFreeUsed') or 0)/2000*100:.2f}% (masih <25% strong lead). Re-read +24/30 mnt = "
        f"0,8/mnt, velocity ratio 0,33 GAGAL run ini. mintOpen 1, "
        f"mintStart 1794321310 = 2026-11-10 21:35 WIB (umur ~2,5 jam TERVERIFIKASI <24 jam), slot user "
        f"TERBUKA (agentFreeByWallet 0, balanceOf 0). Website SUDAH terverifikasi (metode H, run 2201). "
        f"Tetap early lead; re-read totalSupply 397 (blok {BLOCK}).")
    print("SOLDERCATS updated (still early)")

# ---- NIGHTFORGE: gate rechecked, still failed ----
nf = snap["contracts"].get("NIGHTFORGE")
if isinstance(nf, dict):
    p = legs.get("probe", {}).get("NIGHTFORGE", {})
    if p.get("totalSupply") is not None:
        nf["totalSupply"] = p["totalSupply"]
    if p.get("agentFreeUsed") is not None:
        nf["agentFreeUsed"] = p["agentFreeUsed"]
    nf["runNote0001_1111"] = (
        f"Run 0001: totalSupply {p.get('totalSupply')} (was 671 run 2331), agentFreeUsed "
        f"{p.get('agentFreeUsed')}/2000 = {(p.get('agentFreeUsed') or 0)/2000*100:.1f}% (tetap >=25% strong "
        f"lead). Gate DICEK ULANG run ini (metode H + I + J + G): nightforge.pages.dev home + "
        f"/meta/collection.json + /llms.txt + /skill.md + /launch.json + /agent.json SEMUA tetap halaman "
        f"infografis medis yang sama (23.809 byte, 0 kecocokan kontrak); contractURI() menunjuk domain yang "
        f"sama (metode I, bukan bukti baru); ABI Sourcify exact_match 87 fns tanpa fungsi site/URL "
        f"(metode J, hanya eip712Domain); pencarian nama proyek tanpa hasil situs (metode G) -> gate TETAP "
        f"GAGAL, TIDAK di-preview/TIDAK di-mint. Status tetap strong-lead-gate-blocked-2026-11-10 (sudah "
        f"dilaporkan sekali run 2131; tidak dilaporkan ulang). Deadline umur 2026-11-11 14:36 WIB.")
    print("NIGHTFORGE gate rechecked (still failed)")

note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user-2026-11-02; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") + " Minted-by-user-2026-11-01; tanpa perubahan.")
note("Zapcourier", (dyn_note("Zapcourier") or "") + " Minted-by-user-2026-11-02; free pool habis (712/712); tanpa perubahan.")
note("BYTEBLOOM", (dyn_note("BYTEBLOOM") or "") + " Minted-by-user run 2201 (#508); slot terpakai; tanpa perubahan.")
note("EMBERANVIL", (dyn_note("EMBERANVIL") or "") + " Minted-by-user-2026-11-10 (#946); tanpa perubahan.")
note("KERNELMONK", (dyn_note("KERNELMONK") or "") + " Minted-by-user-2026-11-10 (#509); tanpa perubahan.")
note("Lanternfield", (dyn_note("Lanternfield") or "") + " Minted-by-user-2026-11-10 (#516); tanpa perubahan.")
note("Cosmic Sentinel", (dyn_note("Cosmic Sentinel") or "") +
     " Early lead; freeMinted 358/225.000 = 0,16% (jauh <25%); umur UNVERIFIED; tanpa perubahan.")
note("ORBITJANITOR", (dyn_note("ORBITJANITOR") or "") +
     " PROMOSI early->strong lead + MINT BERHASIL run 0001 (strong-lead direct mint): probe segar "
     "totalSupply 545, agentFreeUsed 545/2000 = 27,25% (>=25%); mintOpen 1, mintStart 1794320692 = "
     "2026-11-10 21:24 WIB (umur ~2,7 jam TERVERIFIKASI <24 jam), slot user TERBUKA; website terverifikasi "
     "(orbitjanitor.pages.dev/llms.txt mencetak kontrak 1x, dicek ulang run ini). Audit Binance: hasResult="
     "false (TIDAK ADA HASIL, bukan pass). Preview bersih (000000000, +1 NFT #552, tanpa authority/allowance/"
     "risk). Tx 0xa05ae38daedb277b2c2292fb8920291fb8f40d615d83793621cd38c872a53879, blok 132813606, gas 280.547 "
     "(~0,000017955 BNB). Verifikasi: ownerOf(552)=agent wallet, balanceOf=1, agentFreeByWallet=1. Rarity: "
     "Tier Mop Unit, Model Dust Mop, Rank 6 (tierOf 5, modelOf 29, revealed). Market: Salvage Bay "
     "0x75b264fdf7566f81367dcb257675fd073c0b3df1 (fee 3%) listedCount 0, sales 0, volume 0 — TIDAK ADA "
     "listing live / floor -> TIDAK di-list (aturan auto-list).")

# ---- ORBITJANITOR: status + mint fields ----
oj = snap["contracts"].get("ORBITJANITOR")
if isinstance(oj, dict):
    oj["status"] = "minted-by-user-2026-11-11"
    oj["mintTx"] = "0xa05ae38daedb277b2c2292fb8920291fb8f40d615d83793621cd38c872a53879"
    oj["mintBlock"] = 132813606
    oj["mintGas"] = 280547
    oj["mintTokenId"] = 552
    oj["userBalance"] = 1
    oj["orderId"] = "26111000002032095228"
    oj["rarity"] = {"tier": "Mop Unit", "model": "Dust Mop", "rank": 6, "tierOf": 5, "modelOf": 29}
    print("ORBITJANITOR minted-by-user-2026-11-11 (#552)")
note("Golden Agents", (dyn_note("Golden Agents") or "") +
     " Early lead; free% UNVERIFIED (tanpa view free); tanpa perubahan.")

# ---- Age exclusions: window 22:31 -> 23:31 WIB (launch epoch 1794238255..1794240055) ----
WIN_LO, WIN_HI = 1794241855, 1794243655
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

# ---- hot-leg-seen dedupe for the 11 shape-checked contracts ----
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
now_iso = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
added = 0
for a, s in legs.get("shape", {}).items():
    if a.lower() in {k.lower() for k in seen}:
        continue
    src = "boltbook-zh-0001" if a.lower() in {"0x88081347e712749a2d01e6c597b13fe0cc2478a5",
                                              "0xf769be14784bf61273028cb66f3e6a34b68eec9f"} else "sourcify-feed-0001"
    if "error" in s:
        note_txt = f"ABI fetch error: {s['error']}"
        status = "checked-abi-unavailable"
    else:
        note_txt = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                    f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"
    seen[a] = {"first_seen_wib": now_iso, "note": note_txt,
               "source": "sourcify-feed-0001", "status": status}
    added += 1
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"))
print(f"hot-leg-seen: +{added} -> {len(seen)}")

# ---- Top-level run notes ----
vel_passes = vel.get("passes", [])
snap["last_run_wib"] = NOW
snap["last_run"] = 1
snap["runNote0001_1111"] = (
    f"Run 0001 (2026-11-11 00:01 WIB, blok re-read {BLOCK}): re-read {updated} kontrak + {tc_updated} "
    f"track_c (bsc-dataseed). SATU MINT BERHASIL: ORBITJANITOR #552 (promosi early->strong lead, "
    f"agentFreeUsed 545/2000 = 27,25%; tx 0xa05ae38daedb277b2c2292fb8920291fb8f40d615d83793621cd38c872a53879, "
    f"blok 132813606, gas 280.547; rarity Tier Mop Unit / Model Dust Mop / Rank 6; Salvage Bay 0 listing "
    f"-> tidak di-list). SOLDERCATS tetap early (probe 395/2000 = 19,75%; re-read 397; velocity GAGAL "
    f"+24, 0,8/mnt, ratio 0,33). NIGHTFORGE gate dicek ulang (H+I+J+G), tetap gagal (nightforge.pages.dev "
    f"masih infografis medis, 0 kecocokan kontrak; strong lead 33,55% TETAP gate-blocked, tidak di-mint). "
    f"0 kandidat baru, 0 early lead baru, 0 track-C lead/kandidat baru, 0 track-B claim. Velocity LOLOS run "
    f"ini: {vel_passes if vel_passes else 'tidak ada'} (hanya artefak ERC-20 ETHBack, bukan sinyal NFT).")
snap["runNote0001_1111_scan"] = (
    "Run 0001 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs (eth_blockNumber) HTTP 401 Unauthorized "
    "(outage sejak ~13:33 WIB 2026-11-09 berlanjut, kini ~34,5 jam; kuota Ankr 0% s.d. 1 Des 2026). Watermark "
    "TIDAK dimajukan (tetap 132512564; gap ke head ~300.657 blok dan tumbuh). Route 5c: tanpa output scan baru "
    "(tidak ada ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote0001_1111_binanceai"] = (
    "Run 0001 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, token balanceOf(user)=0 (direct eth_call, "
    "blok ~132813xxx). Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang. "
    "pending_claims kosong.")
snap["runNote0001_1111_age_exclusions"] = (
    f"Run 0001 age-exclusions (aturan <24 jam): {len(newly_excluded)} BARU {newly_excluded if newly_excluded else ''}. "
    "Tidak ada entri non-terminal lain dengan launch terverifikasi di jendela 2026-11-09 23:31-2026-11-10 00:01 WIB yang "
    "melewati 24 jam run ini.")
snap["runNote0001_1111_discovery"] = (
    "Run 0001 discovery: Sourcify feed 20 terbaru (verified 16:49-17:04Z), 4 kontrak baru di-shape-check "
    "(0x0759c26e, 0x30FF10e4, 0xDE5d2732, 0x00D0121E — semua S1=S2=False, 0 sale-shape; 0x0759c26e punya "
    "fungsi mint tapi tanpa free/quote/agent). Boltbook EN 200 45.158 byte + ZH 200 45.472 byte, 13 alamat "
    "unik, 0 baru (semua sudah di hot-leg-seen; ORBITJANITOR ada di halaman). Sweep: Agentic Gangster free "
    "sold out 111/111 (excluded 1431); Horus AI fase 1 sold out 2.000, fase 2 berbayar; MOLT AGENT free pool "
    "habis; AirdropBuzz: MALTA sudah dimint user, YAMA watchlist, PACTA/NOVRA/BOOB/ORBITA free habis/sold "
    "out; 0 proyek baru. Rute 6: Odaily 200 (264.108 byte) + PANews 200 (119.600 byte), 0 keyword Agent ID/"
    "free mint/free share. Bridge: 116 kontrak, mtime 2026-11-08 18:21 WIB (STALE, tidak berubah); 6 tidak "
    "di snapshot (Ore PAID, ETHBack tracker, Ikigai ERC20, AGC token, Krillfarm #260 finding 1-entity, "
    "PANBA ERC20) — bukan lead, tidak dipromosikan. Track_c: 5 perubahan kecil tanpa promosi (NUSA 382->383, "
    "COSO v2 739->742 — keduanya age-excluded; JINMA 661->659, LUCKY777 382->379 — minted-by-user; 11-11 "
    "573->576 watchlist-only). Cryptlichor free pool tetap habis 1691/1691 (watchlist-only, dicatat saja).")

note("Cryptlichor", (dyn_note("Cryptlichor") or "") +
     " Free pool kini HABIS (freeClaimed 1691/1691); watchlist-only-not-early, tidak pernah dilaporkan "
     "sebagai lead -> dicatat saja, tidak dilaporkan.")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT MERGED run 0001")
