#!/usr/bin/env python3
"""Merge run 1901 (scheduled 2026-11-11 19:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-1901-reread.json (63 contracts + 23 track_c; head block
132964904), run-2026-11-11-1901-legs.json, run-2026-11-11-1901-gate-stampooor.json
(gate2), interim findings. Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1901-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1901-legs.json"))
gate = json.load(open(BASE + "run-2026-11-11-1901-gate-stampooor.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1901-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
TS = "2026-11-11 19:01 WIB"

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
        e["runNote1901_1111"] = ("Run 1901 (blok %s): baca batch GAGAL (transport) - nilai lama "
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
        C[name]["runNote1901_1111"] = text

# --- Stampooor: strong lead crossed, gate BLOCKED ---
st = C["Stampooor Stamp Packs"]
st["status"] = "strong-lead-gate-blocked-2026-11-11"
st["website"] = "https://stampooor.com/packs/"
st["gate"] = "website_unverified_site_unreachable"
st["websiteVerified"] = False
st["xVerified"] = False
st["xNote"] = ("Akun X @postage27 ditemukan via pencarian (bukan via tautan situs) - linkage "
    "sebagai kanal resmi TIDAK terverifikasi; X opsional, bukan blocker.")
if gate.get("stampooor_freeMinted") is not None:
    st["freeMinted"] = gate["stampooor_freeMinted"]
    st["totalMinted"] = gate["stampooor_freeMinted"]
st["freeAvailable_user"] = gate.get("stampooor_freeAvailable_user")
note("Stampooor Stamp Packs",
 "Run 1901: STRONG LEAD CROSSED - freeMinted 828->841 (reread blok 132964904) -> 848 (gate probe) /1200 = 70,67%% (>70%%); "
 "umur TERVERIFIKASI <24 jam (mintStart 1794362419 = 11 Nov ~09:00 WIB, ~10 jam); slot user TERBUKA (balanceOf 0, freeAvailable(user)=1, "
 "freeUsed(user)=0, mintOpen 1). Velocity: +13 dalam 30 mnt (<20) GAGAL - tidak relevan untuk strong-lead direct mint. "
 "GATE WEBSITE GAGAL: pointer situs ditemukan via tokenURI(1) external_url https://stampooor.com/packs/ + URL sama di Sourcify sources, "
 "TAPI situs TIDAK BISA DIMUAT lewat rute apa pun (curl empty-reply 52; browser DNS ERR_NAME_NOT_RESOLVED; browser.open gagal; "
 "pencarian alamat persis 0 hasil; Boltbook EN+ZH 0 mention; pencarian nama proyek 0 hasil; GitHub/site 0 hasil; BscScan text-fetch gagal) "
 "sehingga TIDAK terverifikasi situs mencetak kontrak persis - standar metode (H)/(I) tidak terpenuhi. TIDAK di-preview, TIDAK di-mint. "
 "Dilaporkan SEKALI run ini sebagai strong lead gate-blocked + alasan; gate-blocked-recheck menangani cek ulang situs.")
note("AgentPals",
 "Run 1901: totalMinted/freeMinted 124->202 (+78, 2,60/mnt vs prev 0,2667 = 9,75x, >=20) -> VELOCITY LOLOS pertama kali; "
 "202/300 = 67,33%% (>50%% kandidat, <70%% strong lead - butuh >210). Slot user TERBUKA (balanceOf 0). Website tetap UNVERIFIED; "
 "X unverified. Tetap watchlist-only; BUKAN kandidat (X+website unverified), BUKAN strong lead. Deadline umur ~06:33 WIB 12 Nov.")
note("ABYSSCABLE",
 "Run 1901: totalSupply 823->828 (+5, <20) velocity GAGAL; agentFreeUsed ~828/2000 = 41,4%%; balanceOf(user)=0. "
 "Umur TERVERIFIKASI <24 jam (mintStart 10 Nov ~19:38 WIB); deadline umur ~19:39 WIB hari ini (~38 mnt lagi). BUKAN promosi.")
note("RIMEVAULT", "Run 1901: totalSupply 1030->1036 (+6, <20) velocity GAGAL; balanceOf=1 (minted-by-user 11 Nov) - BUKAN kandidat/promosi. Deadline umur ~21:28 WIB hari ini.")
note("MYCELIX", "Run 1901: totalSupply 615->616 (+1) velocity GAGAL; balanceOf(user)=1 (minted-by-user 11 Nov); deadline umur ~21:47 WIB hari ini.")
note("SOLDERCATS", "Run 1901: totalSupply 540->541 (+1) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:35 WIB hari ini.")
note("LCDSPRITE", "Run 1901: totalSupply 580->581 (+1) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:52 WIB hari ini.")
note("REWINDCLUB", "Run 1901: totalSupply 560->561 (+1) velocity GAGAL; balanceOf(user)=1; deadline umur ~21:49 WIB hari ini.")
note("RAMRAIDERS", "Run 1901: totalSupply=freeMinted 558->558 (+0) velocity GAGAL; 558/7777 = 7,18%%; balanceOf(user)=0 (slot terbuka). Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur konservatif ~00:30 WIB 12 Nov.")
note("Kitebots", "Run 1901: totalSupply 1206->1217 (+11, <20) velocity GAGAL. Free%% UNVERIFIED, umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint.")
note("HANAMI BLOOM", "Run 1901: totalSupply=freeMinted 109->109 (+0) velocity GAGAL; 109/3.333 = 3,27%%; balanceOf(user)=0; umur ~18 jam (deadline ~12:59 WIB 12 Nov). Tetap EARLY lead; TIDAK di-preview/dimint.")
note("Cosmic Sentinel", "Run 1901: totalSupply 471->471 (+0) velocity GAGAL; freeMinted 466; balanceOf(user)=0.")
note("Skywe Legion", "Run 1901: totalMinted 641->644 (+3) velocity GAGAL. Free%% UNVERIFIED, umur UNVERIFIED, X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint.")
note("AgentRune", "Run 1901: totalSupply 190 (reread); freeMinted 187; balanceOf(user)=0.")
note("SUDOSAINTS", "Run 1901: totalSupply 604 (reread); freeMinted 604; balanceOf(user)=0.")

tc_updated, tc_fail = [], []
tc = reread.get("track_c", {})
if isinstance(tc, dict):
    for name, d in tc.items():
        if name not in TC or not isinstance(TC.get(name), dict): continue
        e = TC[name]
        if d.get("_batch_fail"):
            tc_fail.append(name); continue
        changed = False
        for k in ("totalSupply","freeMinted","freeClaimed"):
            if d.get(k) is not None and e.get(k) != d[k]:
                e[k] = d[k]; changed = True
        e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
        if changed: tc_updated.append(name)

# New discoveries, both already free-sold-out on first verification -> excluded, NOT reported
C["RIGBYPASS"] = {
    "address": "0xe657465f0EB4B55877246026BfAe4EC75ef2E160",
    "name": "RIGBYPASS", "symbol": "RIGB", "kind": "ERC721",
    "status": "excluded-free-sold-out-age-excluded-2026-11-11",
    "totalSupply": None, "totalMinted": 1120, "freeMinted": 1111, "FREE_SUPPLY": 1111, "MAX_SUPPLY": 8888,
    "mintOpen": None, "balanceOf_user": 0,
    "website": "https://ribgypass.pages.dev/",
    "discovery": ("Sweep run 1901 (The Colony, published 2026-11-10T01:02:24Z = 08:02 WIB 10 Nov): 1.111 free dari 8.888. "
      "Verifikasi on-chain run ini: freeMinted 1111/1111 = 100%% FREE SOLD OUT (totalMinted 1120, 9 paid); umur >24 jam "
      "(launch <=08:02 WIB 10 Nov) -> AGE-EXCLUDED juga. Situs ribgypass.pages.dev fetch 0 byte. Dicatat excluded, TIDAK dilaporkan."),
    "firstSeenWib": "2026-11-11 19:01 WIB", "lastReadBlock": BLOCK, "lastReadWib": TS,
}
C["TINY AGENTS"] = {
    "address": "0x83d5e5449CB513A9c0C257808222F1Ba723d0978",
    "name": "TINY AGENTS", "symbol": None, "kind": "ERC721",
    "status": "excluded-free-sold-out-2026-11-11",
    "totalSupply": None, "totalMinted": 38, "freeMinted": 38, "FREE_SUPPLY": 38, "MAX_SUPPLY": 8888,
    "mintOpen": 1, "balanceOf_user": 0,
    "website": "https://tinyagents.pages.dev/",
    "discovery": ("Sweep run 1901 (The Colony, published 2026-11-10T18:05:09Z = 01:05 WIB 11 Nov): 38 free pertama. "
      "Verifikasi on-chain run ini: freeMinted 38/38, freeRemaining 0, canClaimFree(user)=0, paidMinted 0 -> FREE SOLD OUT. "
      "Situs tinyagents.pages.dev TERBACA dan mencetak kontrak persis (website evidence ada) tapi pool gratis habis. "
      "Umur ~18 jam (<24 jam) tapi pool habis -> excluded, TIDAK dilaporkan."),
    "firstSeenWib": "2026-11-11 19:01 WIB", "lastReadBlock": BLOCK, "lastReadWib": TS,
}

# Feed wave 1901 -> track_c checked-only
TC["Feed-wave-1901-2026-11-11"] = {
    "status": "checked-not-agent-shaped-2026-11-11",
    "addresses": legs.get("feed_new", []),
    "note": ("Run 1901 Sourcify feed: 20 kontrak, verified 11:50:35-12:02:12Z, 12 baru - 0 S1/S2. "
      "Loose early_shape 0x8c57 (35 fns, mint+quote, tanpa free view/agent) + retry 0x086F/0xbd1a/0x9e95: triase totalSupply KEEMPATNYA 0 "
      "(belum ada mint pertama) -> BUKAN early lead. 0x503A/0x1E48/0xc20E BUKAN agent-shaped (token biasa). Dicatat checked saja."),
    "lastReadWib": TS,
}
if isinstance(TC.get("RigForge"), dict):
    TC["RigForge"]["runNote1901_1111"] = ("Run 1901 RigForge: freeSharesLeft 692/1000 (695 pukul 18:31), openedAt 0 (pool BELUM buka), "
        "freeClaimed 308, freeBooked(wallet)=10000 RIG utuh.")
    TC["RigForge"]["freeSharesLeft"] = 692
    TC["RigForge"]["freeClaimed"] = 308
    TC["RigForge"]["openedAt"] = 0
    TC["RigForge"]["lastReadWib"] = TS

snap["last_run"] = 1
snap["last_run_wib"] = TS
snap["runNote1901_1111"] = (
    "Run 1901 (blok 132964904): 1 STRONG LEAD BARU - Stampooor 841->848/1200 = 70,67%% (>70%%), umur terverifikasi ~10 jam, slot user terbuka - "
    "TAPI GATE WEBSITE GAGAL (situs stampooor.com/packs/ ditemukan via tokenURI + Sourcify, tidak bisa dimuat rute apa pun: curl empty-reply, "
    "browser DNS ERR_NAME_NOT_RESOLVED) -> TIDAK di-preview/dimint; dilaporkan SEKALI sebagai strong lead gate-blocked. 0 kandidat baru, "
    "0 early lead baru, 0 track-B dibuka, 0 track-C lead baru. Velocity LOLOS: 1 (AgentPals 202/300 = 67,33%%, +78, 9,75x - belum strong lead). "
    "Batch-fail: 0. RIGBYPASS + TINY AGENTS baru ditemukan via sweep tapi free pool SUDAH HABIS (1111/1111 dan 38/38) -> dicatat excluded, TIDAK dilaporkan. "
    "Feed baru 12: 0 S1/S2; 4 loose early_shape, triase totalSupply 0 - BUKAN early lead. RigForge pool belum buka (freeSharesLeft 692/1000, openedAt 0, "
    "booking 10000 RIG utuh). binanceai launched()=0 tetap pending (refund phase). Scan FAST-FAIL pre-flight Ankr HTTP 401 (outage sejak "
    "~13:33 WIB 2026-11-09, kuota 0%% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564). Boltbook EN 44.636 byte / ZH 42.966 byte / 0 baru. "
    "Sweep: Agentic Gangster free habis (dikonfirmasi agentboard 111/111); Lenx sudah sold-out di snapshot; NOVRA/WNO sudah di track_c. "
    "Route 6: Odaily 0, PANews 0. AGE: tidak ada age-exclusion baru (ABYSSCABLE deadline ~19:39 WIB hari ini).")
snap["runNote1901_1111_scan"] = (
    "Run 1901 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized, ~16 dtk) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. "
    "Scan leg TIDAK dijalankan (amendemen 2026-11-06). Watermark tetap 132512564; gap ke head tumbuh (terakhir terukur ~445.080 blok pukul 18:01 WIB, "
    "sudah dilaporkan sekali 9 Nov - DIAM). 5c dilewati (tanpa output scan).")
snap["runNote1901_1111_binanceai"] = (
    "Run 1901 track-B: binanceai.fun launched()=0 (raw 0x00..00) - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong.")
snap["runNote1901_1111_rigforge"] = (
    "Run 1901 RigForge: freeSharesLeft 692/1000 (695 pukul 18:31), openedAt 0 (pool BELUM buka), freeClaimed 308, freeBooked(wallet)=10000 RIG utuh.")

with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE vel_pass=%s vel_fail=%d batch_fail=%s tc_updated=%s" % (vel_pass, len(vel_fail), batch_fail, tc_updated))
