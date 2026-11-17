#!/usr/bin/env python3
"""Merge run 2101 (scheduled 2026-11-11 21:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-2101-reread.json (62 contracts + 23 track_c; head block
132977042), run-2026-11-11-2101-legs.json, run-2026-11-11-2101-triage.json.
Writes snapshot (with .bak). No age-exclusion this run (next deadlines 21:28+).
No new candidate / strong lead / early lead / track-B opening / track-C lead.
Triaged: 0xC3e4923B (no mint), 0x39b57bA7 (mint+quote+agent, no free view),
0xd612a555 (Boltbook, 0 functions) - all checked-not-sale-shape, already
seen+recorded by hot-leg 20:29 run.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-2101-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-2101-legs.json"))
triage = json.load(open(BASE + "run-2026-11-11-2101-triage.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2101-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
TS = "2026-11-11 21:01 WIB"

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
        e["runNote2101_1111"] = ("Run 2101 (blok %s): baca batch GAGAL (transport) - nilai lama "
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
        C[name]["runNote2101_1111"] = text

# --- Stampooor: still strong lead, gate blocked, no tier change -> no re-report ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["status"] = "strong-lead-gate-blocked-2026-11-11"
    note("Stampooor Stamp Packs",
     "Run 2101: freeMinted 852->855/1200 = 71,25% (>70%, tetap strong lead); umur TERVERIFIKASI <24 jam "
     "(mintStart 1794362419 = 11 Nov 09:00:19 WIB; deadline ~09:00 WIB 12 Nov); slot user TERBUKA (balanceOf 0, "
     "mintOpen 1). Velocity +3/30 mnt GAGAL - tidak relevan untuk strong-lead direct mint. GATE WEBSITE tetap "
     "GAGAL (sudah dilaporkan sekali run 1901; gate-blocked-recheck menangani cek ulang situs). TIDAK di-preview, "
     "TIDAK di-mint, TIDAK dilaporkan ulang (tidak ada perubahan tier).")

note("0x7Eb9", "Run 2101: totalMinted 957->960 (+3, <20) velocity GAGAL (rate 0,1000/mnt vs prev 0,5000 = 0,20x); "
     "balanceOf(user)=0. Tetap early-lead-reported; BUKAN promosi.")
note("Kitebots", "Run 2101: totalSupply 1233->1234 (+1, <20) velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED, "
     "X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint.")
note("RIMEVAULT", "Run 2101: totalSupply 1049->1057 (+8, <20) velocity GAGAL (0,267/mnt vs prev 0,2000 = 1,33x); "
     "balanceOf=1 (minted-by-user). Deadline umur ~21:28 WIB hari ini.")
note("MYCELIX", "Run 2101: totalSupply 619->619 (+0) velocity GAGAL; balanceOf(user)=1 (minted-by-user). "
     "Deadline umur ~21:47 WIB hari ini.")
note("SOLDERCATS", "Run 2101: totalSupply 543->543 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:35 WIB hari ini.")
note("LCDSPRITE", "Run 2101: totalSupply 582->582 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:52 WIB hari ini.")
note("REWINDCLUB", "Run 2101: totalSupply 562->562 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:49 WIB hari ini.")
note("RAMRAIDERS", "Run 2101: totalSupply 561->562 (+1) velocity GAGAL; balanceOf(user)=0. "
     "Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur konservatif ~00:30 WIB 12 Nov.")
note("HANAMI BLOOM", "Run 2101: totalSupply 110->110 (+0) velocity GAGAL; balanceOf(user)=0. "
     "Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur ~12:59 WIB 12 Nov.")
note("BYTEBLOOM", "Run 2101: totalSupply 828->830 (+2, <20) velocity GAGAL; balanceOf(user)=1 (minted-by-user).")
note("Dragon Agent", "Run 2101: totalSupply 932->932 (+0) velocity GAGAL; balanceOf(user)=0.")
note("Foundry Faces", "Run 2101: totalSupply tetap None (view revert), totalMinted 1251->1301 (+50 dalam 30 mnt); "
     "velocity TIDAK dihitung (totalSupply() revert + tidak ada baseline rate tersimpan); free% UNVERIFIED; umur "
     "UNVERIFIED; balanceOf(user)=0. BUKAN promosi - tetap watchlist-only-age-unverified.")
note("AgentPals", "Run 2101: totalMinted 300->300 (+0); free pool SOLD OUT 300/300; balanceOf(user)=1 (#268). "
     "Status minted-by-user-2026-11-11; TIDAK dilaporkan ulang. Keputusan gate metode (I) user ~19:36 WIB tetap berlaku "
     "(pantau 3 hari s.d. 14 Nov 2026; metadata worker saja SEMENTARA TIDAK cukup sebagai bukti website).")
note("EMBERANVIL", "Run 2101: totalSupply 1144->1145 (+1, <20) velocity GAGAL; balanceOf(user)=1 (minted-by-user).")

# --- MECHA: NEW EARLY LEAD (first seen this run via Sourcify feed) ---
C["MECHA"] = {
    "address": "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
    "status": "early-lead-reported-2026-11-11",
    "name": "MECHA",
    "symbol": "MECHA",
    "kind": "ERC721",
    "totalSupply": None,
    "totalMinted": 45,
    "freeClaimed": 45,
    "FREE_SUPPLY": 4444,
    "MAX_SUPPLY": 9999,
    "freePerWallet": 2,
    "maxPerWallet": 20,
    "priceWei": 500000000000000,
    "freePctVerified": 1.01,
    "mintOpen": None,
    "userMintedBy": 0,
    "userFreeUsed": 0,
    "userBalance": 0,
    "userSlotNote": "Slot TERBUKA: quote(user,1) freeCount=1 cost=0; freeAvailable(user)=2; freeUsedBy(user)=0; hasAgentId(user)=1; balanceOf(user)=0.",
    "firstSeenBlock": BLOCK,
    "firstSeenWib": "2026-11-11 21:01 WIB",
    "sourcifyVerifiedAt": "2026-11-11T13:55:59Z",
    "owner": "0xe9a232aefaa230a38bc9fec961eea19134903308",
    "AGENT_ID_REGISTRY": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "baseURI": None,
    "lastReadBlock": BLOCK,
    "lastReadWib": TS,
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "Umur peluncuran UNVERIFIED: verifiedAt Sourcify 20:55:59 WIB BUKAN waktu launch; tidak ada waktu launch dinyatakan proyek yang ditemukan; koroborasi first-mint via getLogs TIDAK BISA (Ankr 401, outage sejak 9 Nov).",
    "gateNote": "Website TIDAK DITEMUKAN (metode A: pencarian alamat kontrak 0 hit; B: Boltbook EN+ZH tidak memuat; C: sumber Sourcify tanpa URL proyek; G: pencarian nama MECHA tanpa hit proyek; I: baseURI kosong, tokenURI tanpa external_url). Template factory AgentNFT.sol (sama dengan gelombang factory lain). GATE website GAGAL untuk eksekusi - early lead TIDAK PERNAH di-preview/dimint.",
    "baselineNote": ("EARLY lead dilaporkan sekali run 2101 (temuan feed Sourcify recently-verified, verifiedAt "
        "2026-11-11T13:55:59Z; pertama terlihat job ini di run ini - tidak ada di snapshot/track_c/hot-leg-reported). "
        "Agent-shaped: AGENT_ID_REGISTRY()=registry resmi, hasAgentId(), mint(qty)+quote()+free views, FREE_SUPPLY 4444. "
        "S1 literal PASS (mint+quote+freeAvailable/freeClaimed+registry) TAPI objeknya NFT ERC-721, BUKAN share sale fungible - "
        "diklasifikasikan early lead jalur A, BUKAN track-C lead. Free 45/4444 = 1,01% (jauh di bawah 50% kandidat & >70% strong lead). "
        "Umur UNVERIFIED, X UNVERIFIED, website TIDAK DITEMUKAN, velocity belum terhitung (bacaan pertama). "
        "Promosi ke strong lead hanya bila 3 kaki terpenuhi; ke kandidat hanya bila SEMUA kriteria + safety lolos."),
    "runNote2101_1111": ("Run 2101 (blok %s): EARLY LEAD BARU - MECHA 0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78: "
        "totalMinted 45, freeClaimed 45/4444 = 1,01%%; quote(user,1) freeCount=1 cost=0, slot TERBUKA; "
        "umur UNVERIFIED; X UNVERIFIED; website TIDAK DITEMUKAN (metode A/B/C/G/I); TIDAK di-preview/dimint." % BLOCK),
}

# --- Track C reread: store fresh values, flag material changes ---
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

# --- Triaged / checked (not leads, never reported as leads) ---
def checked(key, addr, note_text):
    C[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-11", "note": note_text}
checked("checked-0x3Fb0-2101", "0x3Fb05875176021f876e86Afe51977ccFb20Eb1bd",
    "Run 2101 triase feed-new (Sourcify verified ~13:5xZ): 33 fns, has_mint True, has_quote True, agent_ref True, "
    "TAPI free_views [] (near-miss S1 - tanpa free-share view). is_token True, is_nft False. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x2e50-2101", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3",
    "Run 2101 triase feed-new: 84 fns, has_mint True, has_quote False, free_views [freeLeft], agent_ref False, "
    "is_token True, is_nft True. BUKAN S1/S2 (tanpa quote + tanpa registry). Dicatat checked; tidak dilaporkan.")
checked("checked-0x7d28-2101", "0x7d28a1C39C8AbF11bdBA35D9Fa5065dc9A81434b",
    "Run 2101 triase feed-new: 17 fns, tanpa mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x3f7C-2101", "0x3f7CD3226A4da27B70F67Cc85795F8d23D8E2cde",
    "Run 2101 triase feed-new: 42 fns, tanpa mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0xf6da-2101", "0xf6da798339DB15569d4ce50faA8d0c7E6B983487",
    "Run 2101 triase feed-new: 8 fns, tanpa mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0xF8E0-2101", "0xF8E0207FCb4F7aea642d52D82f9FFbAA0261d1C5",
    "Run 2101 legs feed-new: 10 fns, tanpa mint/quote/free/agent, is_token True. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0xe500-2101", "0xe500c7Ac94b4d23aD12b8cC6b161331BB3487F89",
    "Run 2101 legs feed-new: 110 fns, tanpa mint/quote/free/agent, is_token True. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x16fA-2101", "0x16fAb8B32a2f35b19fE0E11f4E8C1Ec5B9Eb0659",
    "Run 2101 legs feed-new: 23 fns, tanpa mint/quote/free/agent, is_token True. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0xdc13-2101", "0xdc13d41e21E6e1c9F62faEFEE0D4f92B390FEeDE",
    "Run 2101 legs feed-new: 8 fns, tanpa mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x6F42-2101", "0x6F421584a067b511CEb441C2d5b8534B0C9cdDE7",
    "Run 2101 triage2 feed-retry-new (verifiedAt 14:02:59-14:04:51Z): 25 fns, tanpa mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0xdFab-2101", "0xdFabF87EE3A9A4cEdda43D3f8035C89E1C9438b7",
    "Run 2101 triage2 feed-retry-new: 9 fns, tanpa mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x9De3-2101", "0x9De342bDFFB5da04D9865f4cd9846D22560D253a",
    "Run 2101 triage2 feed-retry-new: 9 fns, tanpa mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0xE381-2101", "0xE381c967c14b0c6ef82944E0e4b4272D24dd8957",
    "Run 2101 triage2 feed-retry-new: 12 fns, tanpa mint/quote/free/agent. BUKAN S1/S2, BUKAN early-shape. Dicatat checked; tidak dilaporkan.")
checked("checked-0x0977-2101", "0x097753bD983973940167977980963Aeef87b25CB",
    "Run 2101 triage2 feed-retry-new: 25 fns, has_mint True, has_quote False, free_views [], agent_ref False, is_token True. "
    "BUKAN S1/S2, BUKAN early-shape (bukan NFT + tanpa registry). Dicatat checked; tidak dilaporkan.")

snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["runNote2101"] = (
    "Run 2101 (blok %s): EARLY LEAD BARU 1: MECHA 0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78 "
    "(Sourcify verifiedAt 13:55:59Z; totalMinted 45, freeClaimed 45/4444 = 1,01%%; quote(user,1) freeCount=1 cost=0, "
    "slot TERBUKA; umur UNVERIFIED; X UNVERIFIED; website TIDAK DITEMUKAN metode A/B/C/G/I; TIDAK di-preview/dimint). "
    "0 kandidat baru, 0 strong lead baru, 0 track-B dibuka, 0 track-C lead baru, 0 age-exclusion. Stampooor tetap strong "
    "lead gate-blocked 855/1200 = 71,25%%, slot terbuka, TIDAK dilaporkan ulang (tanpa perubahan tier). Velocity: 0 lolos "
    "(Foundry Faces totalMinted 1251->1301 +50/30 mnt TAPI velocity tidak dihitung - totalSupply() revert + tanpa baseline rate; "
    "RIMEVAULT +8; 0x7Eb9 +3). Batch fail: 0. Track-C: 11-11 freeMinted 628->630 (+2, bukan promosi); lainnya datar. "
    "Sourcify feed 20 kontrak (verified 13:47:42-14:02:59Z), 10 baru - 1 S1-hit MECHA (NFT, early lead), 1 near-miss S1 (0x3Fb0, "
    "tanpa free view), 8 bukan shape; triase curl retry feed (verified s.d. 14:04:51Z) tambah 5 baru, 0 S1/S2. Boltbook EN 44.627 "
    "byte / ZH 42.788 byte, 14 alamat, 0 baru. Bridge: 116 kontrak, mtime 2026-11-08 18:21 WIB (STALE), 0 not_in_snapshot, "
    "7 same_owner_discarded, 0 temuan pelengkap. Track B: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase). RigForge: "
    "freeSharesLeft 685/1000 (sama 20:31), openedAt 0 (pool BELUM buka), freeClaimed 315, freeBooked(wallet) = 10000 RIG utuh. "
    "Scan (route 4): FAST-FAIL pre-flight Ankr HTTP 401 Unauthorized - outage berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% "
    "s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564); gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM). "
    "Track-C 5c dilewati (tidak ada output scan baru). Sweep EN+ZH: 0 proyek baru (Agentic Gangster free habis; RIGBYPASS excluded; "
    "MOLT AGENT free habis; Horus AI fase gratis sold out; WNO/NOVRA/TINY/Grove/Agentite sudah dikenal; NAOMI GENESIS snippet "
    "'338 free left' BASI vs bacaan on-chain 20:01 freeMinted 777/777 sold out - tetap excluded). Route 6: Odaily newsflash 0 item "
    "Agent ID/free-mint; PANews 0 item. AGE: tidak ada exclusion run ini; deadline berjalan: RIMEVAULT ~21:28, SOLDERCATS ~21:35, "
    "MYCELIX ~21:47, REWINDCLUB ~21:49, LCDSPRITE ~21:52 (11 Nov); RAMRAIDERS konservatif ~00:30 WIB 12 Nov; HANAMI BLOOM "
    "~12:59 WIB 12 Nov; Stampooor ~09:00 WIB 12 Nov." % BLOCK)
snap["runNote2101_scan"] = (
    "Run 2101 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. "
    "Watermark TETAP 132512564; gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM).")
snap["timestamp_wib"] = TS

with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE vel_pass=%s vel_fail=%s batch_fail=%s tc_changes=%s" % (
    vel_pass, len(vel_fail), batch_fail, tc_changes))
print("VEL_FAIL:", vel_fail)
print("TC_CHANGES:", tc_changes)
