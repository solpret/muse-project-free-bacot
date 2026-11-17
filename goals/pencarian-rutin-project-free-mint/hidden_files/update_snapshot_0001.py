#!/usr/bin/env python3
"""Snapshot + seen + scan-state update, run 0001 (2026-11-06 00:01 WIB).
Applies this run's verified reads. Never writes the bridge file.
Failed reads (None) never overwrite stored values."""
import json, copy

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "reread-2026-11-06-0001.json"))["contracts"]
triage = json.load(open(HF + "triage-firstseen-2026-11-06-0001.json"))["triage"]
firstmint = json.load(open(HF + "firstmint-2026-11-06-0001.json"))
wave2 = json.load(open(HF + "firstmint-wave2-2026-11-06-0001.json"))
paid = json.load(open(HF + "paidonly-recheck-2026-11-06-0001.json"))["results"]
scan = json.load(open(HF + "onchain-scan-2026-11-06-0001.json"))
READ_BLOCK = reread.get("block") if isinstance(reread, dict) else None
# reread() in the script stored block at top level of file, not in contracts;
# recover from file directly:
_reread_file = json.load(open(HF + "reread-2026-11-06-0001.json"))
READ_BLOCK = _reread_file.get("block")

def set_if(entry, key, value):
    if value is not None:
        entry[key] = value

def note(entry, key, text):
    entry[key] = text

# ---------- Route 1 re-reads: HIVE + early leads + gate-blocked ----------
# HIVE Agents
h = snap["contracts"]["HIVE Agents"]
h["totalSupply"] = 1253
h["previousTotalSupply"] = 1253
h["mintedInInterval"] = 0
h["intervalMinutes"] = 30.0
h["currentRatePerMin"] = 0.0
h["previousRatePerMin"] = 0.0
h["velocityLegPasses"] = False
h["lastReadBlock"] = READ_BLOCK
h["lastReadWib"] = "2026-11-06 run 0001"
note(h, "velocityNote0001_1106", "Run 0001 (blok %s): totalSupply 1253 flat vs run 2331 (1253) -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat." % READ_BLOCK)

# Moonfall
m = snap["contracts"]["Moonfall"]
set_if(m, "totalSupply", reread["Moonfall"].get("totalSupply"))
set_if(m, "totalMinted", reread["Moonfall"].get("totalMinted"))
set_if(m, "mintedBy_user", reread["Moonfall"].get("mintedBy_user"))
set_if(m, "balanceOf_user", reread["Moonfall"].get("balanceOf_user"))
set_if(m, "owner", reread["Moonfall"].get("owner"))
m["lastReadBlock"] = READ_BLOCK
note(m, "runNote0001_1106", "Run 0001: totalSupply 26->27 (+1), totalMinted 27; freeClaimed/FREE_SUPPLY/quote tetap None (tidak ada free-cap view); mintedBy(user)=0, balance 0; tetap EARLY (free %% unverified, slot unverified, umur unverified).")

# GHOST
g = snap["contracts"]["GHOST"]
prev_ts = g.get("totalSupply")
set_if(g, "totalSupply", reread["GHOST"].get("totalSupply"))
set_if(g, "totalMinted", reread["GHOST"].get("totalMinted"))
set_if(g, "freeMinted", reread["GHOST"].get("freeMinted"))
set_if(g, "MAX_SUPPLY", reread["GHOST"].get("MAX_SUPPLY"))
set_if(g, "mintOpen", reread["GHOST"].get("mintOpen"))
set_if(g, "quote_user_1", reread["GHOST"].get("quote_user_1"))
set_if(g, "balanceOf_user", reread["GHOST"].get("balanceOf_user"))
set_if(g, "owner", reread["GHOST"].get("owner"))
g["previousTotalSupply"] = prev_ts
g["mintedInInterval"] = (g["totalSupply"] or 0) - (prev_ts or 0)
g["velocityLegPasses"] = False
g["lastReadBlock"] = READ_BLOCK
note(g, "runNote0001_1106", "Run 0001 (blok %s): totalSupply %s->%s (+%s, ~0.54/mnt vs prior 1.13/mnt = 0.48x) -> velocity GAGAL; freeMinted 333/17500 = 1,9%% (<25%%); quote(user,1)=0, balance 0; tetap EARLY." % (READ_BLOCK, prev_ts, g["totalSupply"], g["mintedInInterval"]))

# Sonofluidic
sf = snap["contracts"]["Sonofluidic"]
prev_ts = sf.get("totalSupply")
set_if(sf, "totalSupply", reread["Sonofluidic"].get("totalSupply"))
set_if(sf, "totalMinted", reread["Sonofluidic"].get("totalMinted"))
set_if(sf, "freeMinted", reread["Sonofluidic"].get("freeMinted"))
set_if(sf, "FREE_SUPPLY", reread["Sonofluidic"].get("FREE_SUPPLY"))
set_if(sf, "mintOpen", reread["Sonofluidic"].get("mintOpen"))
set_if(sf, "balanceOf_user", reread["Sonofluidic"].get("balanceOf_user"))
set_if(sf, "owner", reread["Sonofluidic"].get("owner"))
sf["previousTotalSupply"] = prev_ts
sf["mintedInInterval"] = (sf["totalSupply"] or 0) - (prev_ts or 0)
sf["velocityLegPasses"] = False
sf["lastReadBlock"] = READ_BLOCK
note(sf, "runNote0001_1106", "Run 0001 (blok %s): totalSupply %s->%s (+%s, ~1.32/mnt vs prior 2.29/mnt = 0.58x) -> velocity GAGAL; free 421/2260 = 18,6%% (<25%%); mintedBy/quote None (slot unverified); tetap EARLY." % (READ_BLOCK, prev_ts, sf["totalSupply"], sf["mintedInInterval"]))

# Mossminds
mm = snap["contracts"]["Mossminds"]
prev_ts = mm.get("totalSupply")
set_if(mm, "totalSupply", reread["Mossminds"].get("totalSupply"))
set_if(mm, "freeMinted", reread["Mossminds"].get("freeMinted"))
set_if(mm, "MAX_SUPPLY", reread["Mossminds"].get("MAX_SUPPLY"))
set_if(mm, "balanceOf_user", reread["Mossminds"].get("balanceOf_user"))
set_if(mm, "owner", reread["Mossminds"].get("owner"))
mm["previousTotalSupply"] = prev_ts
mm["lastReadBlock"] = READ_BLOCK
note(mm, "runNote0001_1106", "Run 0001 (blok %s): totalSupply %s->%s; freeMinted 783/2880 = 27,2%% (>=25%%) tapi PROMOSI TETAP DISCARDED aturan same-owner (owner 0x4e9b1d076fda3605ad63f81a94a8693342a08dba, sama dgn Thronemind/Hashseers/Layerloom/Smeltbots/Tumblebots) + gate website GAGAL run 2331; slot unverified run ini (mintedBy/quote None); Boltbook 00:20 WIB: 782/2880 (27,2%%) konsisten. Tidak dilaporkan sebagai lead." % (READ_BLOCK, prev_ts, mm["totalSupply"]))

# Snail Mail
sm = snap["contracts"]["Snail Mail"]
prev_ts = sm.get("totalSupply")
set_if(sm, "totalSupply", reread["Snail Mail"].get("totalSupply"))
set_if(sm, "MAX_SUPPLY", reread["Snail Mail"].get("MAX_SUPPLY"))
set_if(sm, "mintOpen", reread["Snail Mail"].get("mintOpen"))
set_if(sm, "mintedBy_user", reread["Snail Mail"].get("mintedBy_user"))
set_if(sm, "balanceOf_user", reread["Snail Mail"].get("balanceOf_user"))
sm["previousTotalSupply"] = prev_ts
sm["lastReadBlock"] = READ_BLOCK
note(sm, "runNote0001_1106", "Run 0001: totalSupply %s->%s; paid-only (price 0.0002 BNB run 2231) TETAP — quote(user,1) gagal dibaca run ini (None = gagal baca, bukan bukti gratis); retry run berikut. Bukan promosi." % (prev_ts, sm["totalSupply"]))

# Agent Coffee / Driftnauts / AGENTIC PERP / Agent Wallet
for key, rr in [("Agent Coffee", "Agent Coffee"), ("Driftnauts", "Driftnauts"),
                ("AGENTIC PERP", "AGENTIC PERP"), ("Agent Wallet", "Agent Wallet")]:
    e = snap["contracts"][key]
    prev_ts = e.get("totalSupply")
    for f in ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user"]:
        set_if(e, f, reread[rr].get(f))
    e["previousTotalSupply"] = prev_ts
    e["lastReadBlock"] = READ_BLOCK
note(snap["contracts"]["Agent Coffee"], "runNote0001_1106",
     "Run 0001: totalSupply %s->%s; quote(user,1)=0, mintedBy=0, freeUsed=0, slot TERBUKA; free %% tetap UNVERIFIED (FREE_SUPPLY None); tetap EARLY." % (snap["contracts"]["Agent Coffee"]["previousTotalSupply"], snap["contracts"]["Agent Coffee"]["totalSupply"]))
note(snap["contracts"]["Driftnauts"], "runNote0001_1106",
     "Run 0001: totalSupply %s->%s; freeMinted 628/2640 = 23,8%% (<25%%); tetap EARLY." % (snap["contracts"]["Driftnauts"]["previousTotalSupply"], snap["contracts"]["Driftnauts"]["totalSupply"]))
note(snap["contracts"]["AGENTIC PERP"], "runNote0001_1106",
     "Run 0001: totalSupply %s->%s; free %% tetap UNVERIFIED (tidak ada free-cap view); tetap EARLY." % (snap["contracts"]["AGENTIC PERP"]["previousTotalSupply"], snap["contracts"]["AGENTIC PERP"]["totalSupply"]))
note(snap["contracts"]["Agent Wallet"], "runNote0001_1106",
     "Run 0001: SEMUA view gagal dibaca (None) kecuali balanceOf(user)=0 — BUKAN nol; nilai lama dipertahankan; tetap EARLY; retry run berikut.")

# Gate-blocked strong leads (10)
for key in ["Agent Frogs", "WAGagent", "Thronemind", "Hashseers", "Layerloom",
            "Smeltbots", "Tumblebots", "Forklings", "Neurolucha", "BNB CACHE Server"]:
    e = snap["contracts"][key]
    rr = reread.get(key, {})
    prev_ts = e.get("totalSupply")
    prev_fc = e.get("freeClaimed")
    for f in ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user",
              "balanceOf_user", "owner"]:
        set_if(e, f, rr.get(f))
    e["previousTotalSupply"] = prev_ts
    e["lastReadBlock"] = READ_BLOCK
    note(e, "runNote0001_1106", "Run 0001 (blok %s): totalSupply %s->%s, freeClaimed %s->%s; status gate-blocked TETAP (tidak ada sellout, tidak ada slot hilang, tidak ada promosi baru).%s" % (
        READ_BLOCK, prev_ts, e.get("totalSupply"), prev_fc, e.get("freeClaimed"),
        " SEMUA view gagal dibaca run ini (nilai lama dipertahankan)." if key == "BNB CACHE Server" else ""))

# WHALE
w = snap["contracts"]["WHALE"]
prev_ts = w.get("totalSupply")
w["totalSupply"] = 3520
w["previousTotalSupply"] = prev_ts
w["mintedInInterval"] = 3520 - (prev_ts or 0)
w["intervalMinutes"] = 288.0
w["currentRatePerMin"] = round((3520 - (prev_ts or 0)) / 288.0, 3)
w["velocityLegPasses"] = False
w["lastReadBlock"] = READ_BLOCK
w["lastReadWib"] = "2026-11-06 run 0001"
note(w, "runNote0001_1106", "Run 0001: totalSupply %s->3520 (+%s dalam ~288 mnt = ~0.68/mnt vs prior 1.32 = 0.52x) -> velocity GAGAL; free-ness/free %% tetap UNVERIFIED; batas umur 48 jam berakhir 2026-11-06 17:33:19 WIB (first mint 2026-11-04 17:33:19 WIB); tetap watchlist-only." % (prev_ts, 3520 - (prev_ts or 0)))

# ---------- Binance Agent: free pool SOLD OUT -> remove ----------
ba = snap["contracts"].pop("Binance Agent", None)
ba_note = "Binance Agent 0xE3a382B8e577A58A5540420C11ABa287C62e49f4 dihapus dari snapshot run 0001: free pool SELLOUT terverifikasi on-chain (totalMinted=123, freeMinted=123, FREE_SUPPLY=123, MAX_SUPPLY=444, blok %s). Dilaporkan sekali sebagai perubahan. Catatan tambahan: postingan Boltbook Cuprihive menandai MintRadar red flag (alamat hardcoded mengontrol setBaseURI + withdraw) — tidak lagi relevan karena pool habis." % READ_BLOCK

# ---------- 12 reclassified early leads (paid-only -> early) ----------
FIRSTS_12 = {
    "PRICKLY": ("2026-11-05 22:26:21 WIB", 131840520, 262),
    "unicorn.exe": ("2026-11-05 22:25:39 WIB", 131840426, 244),
    "Blend In": ("2026-11-05 22:30:06 WIB", 131841020, 327),
    "Buzzkill": ("2026-11-05 22:29:06 WIB", 131840887, 320),
    "Whale Alert": ("2026-11-05 22:29:51 WIB", 131840987, 138),
    "Fresh Hatch": ("2026-11-05 22:29:45 WIB", 131840972, 137),
    "Lion's Share": ("2026-11-05 22:28:44 WIB", 131840836, 140),
    "Otter Nonsense": ("2026-11-05 22:29:37 WIB", 131840954, 126),
    "Hot Springs": ("2026-11-05 22:25:36 WIB", 131840420, 130),
    "Down Under": ("2026-11-05 22:30:25 WIB", 131841062, 125),
    "Toucan Play": ("2026-11-05 23:43:55 WIB", 131850858, 36),
    "jelly.exe": ("2026-11-05 23:45:42 WIB", 131851096, 104),
}
for key, (fm_wib, fm_block, nlogs) in FIRSTS_12.items():
    e = snap["contracts"][key]
    pr = paid[key]
    e["status"] = "early-lead-reported-2026-11-06"
    e["totalSupply"] = pr.get("totalSupply")
    e["owner"] = pr.get("owner")
    e["firstMintBlock"] = fm_block
    e["firstMintWib"] = fm_wib
    e["firstMintLogs"] = nlogs
    e["costOf_user_1"] = pr.get("costOf_user_1")
    e["mintsLeft_user"] = pr.get("mintsLeft_user")
    e["mintedBy_user"] = pr.get("mintedBy_user")
    e["lastReadBlock"] = READ_BLOCK
    e["launchNote"] = ("First mint terverifikasi on-chain via Ankr getLogs (Transfer-from-zero): blok %s = %s; "
                       "tidak ada mint lebih awal di [131060000, blok-1]; umur TERVERIFIKASI <=48 jam." % (fm_block, fm_wib))
    e["baselineNote"] = ("EARLY lead dilaporkan sekali run 0001 (KOREKSI klasifikasi run 2231/2331 'paid-only' — klasifikasi itu SALAH: "
                         "didasarkan pada price()=0.0002 BNB, padahal template ini memberi 1 mint pertama GRATIS: costOf(user,1)=0, "
                         "costOf(user,2)=0.0002 BNB, mintsLeft(user)=10, mintedBy(user)=0, diverifikasi on-chain run ini; postingan Boltbook "
                         "Cuprihive mengonfirmasi mint(1) @ 0 BNB + token ID yang cocok dengan trajektori supply). Agent-shaped: registry-bytes "
                         "hit + template ABI terverifikasi Sourcify (PRICKLY/unicorn.exe/Blend In: agentIds + mint + costOf + mintsLeft) "
                         "atau view-set template identik + owner sama. Free %% UNVERIFIED (tidak ada free-cap/free-claimed view — lane gratis "
                         "adalah 1/wallet, bukan pool ber-cap); velocity baseline pertama run ini; website/X UNVERIFIED. Promosi ke strong lead "
                         "DISCARDED aturan same-owner (owner %s, grup multi-kontrak). TIDAK PERNAH di-preview/di-mint (early)." % pr.get("owner"))

# ---------- 8 new scan early leads (0x1103 wave) ----------
for name, t in triage.items():
    if name in ("AgentIdBSC", "Krypt Titan Agent", "Ethereal Bear Agent", "Solar Panda Agent"):
        continue
    snap["contracts"][name] = {
        "address": t["address"],
        "status": "early-lead-reported-2026-11-06",
        "name": name,
        "kind": t.get("kind"),
        "totalSupply": t.get("totalSupply"),
        "MAX_SUPPLY": t.get("MAX_SUPPLY"),
        "mintOpen": t.get("mintOpen"),
        "price": t.get("price"),
        "costOf_user_1": t.get("costOf_user_1"),
        "mintsLeft_user": None,
        "mintedBy_user": t.get("mintedBy_user"),
        "userBalance": t.get("balanceOf_user"),
        "owner": t.get("owner"),
        "firstMintBlock": t.get("earliest_block"),
        "firstMintWib": t.get("earliest_wib"),
        "firstMintLogs": t.get("log_count"),
        "firstSeenBlock": t.get("window_first_block"),
        "scanMints": t.get("window_mints"),
        "scanMinters": t.get("window_minters"),
        "lastReadBlock": READ_BLOCK,
        "lastReadWib": "2026-11-06 run 0001",
        "xVerified": False,
        "velocityVerified": False,
        "launchNote": ("First mint terverifikasi on-chain via Ankr getLogs (Transfer-from-zero, dari blok 130000000): blok %s = %s; "
                       "umur TERVERIFIKASI <=48 jam." % (t.get("earliest_block"), t.get("earliest_wib"))),
        "baselineNote": ("EARLY lead dilaporkan sekali run 0001 (first-seen scan rute 4, jendela 131854448-131856447). Agent-shaped: "
                         "registry-bytes hit + view-set template identik dgn gelombang PRICKLY (costOf(address,uint256), mintedBy, "
                         "mintsLeft, price 0.0002 BNB, mintOpen) + owner 0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd (grup multi-kontrak, "
                         "sama dgn Toucan Play + jelly.exe). Gratis slot pertama: costOf(user,1)=0, mintedBy(user)=0, sample mint tx value 0 "
                         "(2 tx sampel); costOf(user,2)=0.0002 BNB (tidak dibaca run ini — pola template). Free %% UNVERIFIED (tidak ada "
                         "free-cap view); velocity baseline pertama; website/X UNVERIFIED. Promosi ke strong lead DISCARDED aturan same-owner. "
                         "TIDAK PERNAH di-preview/di-mint (early)."),
    }

# ---------- Scan first-seen NOT early ----------
snap["contracts"]["AgentIdBSC"] = {
    "address": "0xf8dd1733eefD94990b03afBBe2f58C293BF69C88",
    "status": "watchlist-only-paid-only-2026-11-06",
    "name": "AgentIdBSC", "symbol": "AIDBSC", "kind": "ERC721",
    "totalMinted": 107, "freeMinted": 102, "MAX_SUPPLY": 8000,
    "quote_user_1": 188272096627032, "userBalance": 0,
    "owner": "0xb07b263ffb129575142537fa307f24e6a435f78a",
    "firstMintBlock": 131844366, "firstMintWib": "2026-11-05 22:55:12 WIB",
    "firstMintLogs": 107, "firstSeenBlock": 131844366,
    "lastReadBlock": READ_BLOCK,
    "baselineNote": ("First-seen scan run 0001, BUKAN early: BERBAYAR — sample mint tx value 0.0005 BNB (0x11c37937e08000), "
                     "quote(user,1)=188272096627032 wei (~0.000188 BNB) != 0; 107 mint / 22 minter (batch minting). "
                     "Registry-bytes hit tapi lane gratis tidak terbukti untuk user. Watchlist-only-paid-only."),
}
for nm, addr, fb, fw in [
    ("Krypt Titan Agent", "0xA624cd94EAAe91cCaFA5bE9857F476a76F57f61a", 131854749, "2026-11-06 00:13:07 WIB"),
    ("Ethereal Bear Agent", "0xfE757eA8ce4c5893331c6342E0B5BDc523B3246F", 131855451, "2026-11-06 00:18:23 WIB"),
    ("Solar Panda Agent", "0x78113b5aAe3a9519b670309CDc70d0e461587d5b", 131856155, "2026-11-06 00:23:39 WIB"),
]:
    snap["contracts"][nm] = {
        "address": addr, "status": "watchlist-only-paid-only-2026-11-06",
        "name": nm, "kind": "ERC721", "totalSupply": 3333, "totalMinted": 1, "MAX_SUPPLY": 3333,
        "mintedBy_user": 0, "userBalance": 0,
        "firstMintBlock": fb, "firstMintWib": fw, "firstMintLogs": 1,
        "lastReadBlock": READ_BLOCK,
        "baselineNote": ("First-seen scan run 0001, BUKAN early: BERBAYAR — sample mint tx value 0.0005 BNB (0x1c6bf52634000), "
                         "1 mint / 1 minter. ANOMALI: totalSupply=3333 padahal hanya 1 mint log di [130000000, head] — kemungkinan "
                         "pre-mint sebelum blok 130000000 (kontrak lebih tua) atau mint non-standar; umur launch TIDAK terverifikasi. "
                         "Watchlist-only-paid-only."),
    }
snap["contracts"]["TapeOut Miner"] = {
    "address": "0x355286C54AF4CeCf07e13A0aeF6ad36ee4d27fb8",
    "status": "watchlist-only-not-early-2026-11-06",
    "name": "TapeOut Miner", "symbol": "TMINER", "kind": "ERC721",
    "scanMints": 1, "scanMinters": 1, "lastReadBlock": READ_BLOCK,
    "baselineNote": "First-seen scan run 0001, BUKAN early: registry=False (tidak ada referensi registry Agent ID di bytecode), Sourcify not_verified. Watchlist-only.",
}
snap["contracts"]["Bavarsis Node"] = {
    "address": "0x62B138919d0Da2923e584E6E61fb922e04276A7b",
    "status": "watchlist-only-not-early-2026-11-06",
    "name": "Bavarsis Node", "symbol": "BNODE", "kind": "ERC721",
    "scanMints": 1, "scanMinters": 1, "lastReadBlock": READ_BLOCK,
    "baselineNote": "First-seen scan run 0001, BUKAN early: registry=False, Sourcify error:IncompleteRead. Watchlist-only.",
}

# ---------- Age-excluded tombstones (never reported as leads) ----------
for nm, addr, fb, fw, why in [
    ("Night Shift", "0x427aed3f7427b48e45f5e648105aa1b77724cf14", 130000129, "2026-10-27 08:18:11 WIB",
     "First mint <= 2026-10-27 08:18:11 WIB (binary search mentok di floor 130000000 — kemungkinan lebih tua lagi); umur >10 hari, jauh >48 jam; totalSupply 9179/10000 belum sold out; slot user TERBUKA (quote(user,1)=0, mintedBy=0) tapi umur gugur. Ditemukan via postingan audit Boltbook run 0001; Sourcify exact_match menurut postingan (fetch ABI run ini retry-exhausted). BUKAN lead, BUKAN kandidat."),
    ("Cuprihive", "0x1e9460475825a3218cd36b8d35a0698d6939aaec", 131437305, "2026-11-03 20:01:26 WIB",
     "First mint 2026-11-03 20:01:26 WIB (tidak ada mint lebih awal di [131060000, blok-1]); umur ~52,8 jam >48 jam; totalSupply 677, free 672/3333 = 20,2%%; slot TERBUKA (quote 0, mintedBy 0, freeUsed 0); owner grup d76d. Ditemukan via postingan Boltbook Cuprihive run 0001. BUKAN lead (age-excluded)."),
    ("Skyagent", "0x83decf8076d04d59da771da6bb298132164be55b", 131319337, "2026-11-03 05:16:24 WIB",
     "First mint 2026-11-03 05:16:24 WIB (tidak ada mint lebih awal); umur ~67,5 jam >48 jam; totalSupply 886, free 881/3333 = 26,4%%; slot TERBUKA (quote 0, mintedBy 0, freeUsed 0); owner grup d76d. Sempat memenuhi 2 kaki strong lead (%% + slot) tapi umur gugur + promosi juga discarded same-owner. Ditemukan via postingan Boltbook Cuprihive run 0001. BUKAN lead (age-excluded)."),
    ("Rookling", "0xe76a5bf585f9378b065d48f1a49d90ecf71ebeba", 130530223, "2026-10-30 02:36:32 WIB",
     "First mint 2026-10-30 02:36:32 WIB (binary search dari 131060447); umur ~6,9 hari >48 jam; totalSupply 4485, free 4385/7000 = 62,6%%; slot TERBUKA (quote 0, mintedBy 0, freeUsed 0); owner grup a054. Ditemukan via postingan Boltbook Cuprihive run 0001. BUKAN lead (age-excluded)."),
]:
    snap["contracts"][nm] = {
        "address": addr, "status": "age-excluded-2026-11-06",
        "name": nm, "kind": "ERC721",
        "firstMintBlock": fb, "firstMintWib": fw,
        "lastReadBlock": READ_BLOCK,
        "baselineNote": why,
    }

# FYINU -> age-excluded (track C)
fy = snap["contracts"].get("Flyingsquirrelai")
if fy:
    fy["status"] = "age-excluded-2026-11-06"
    fy["firstMintBlock"] = 131446462
    fy["firstMintWib"] = "2026-11-03 21:10:07 WIB"
    fy["totalSupply"] = 867000000000000000000000
    fy["totalMinted"] = 289
    fy["lastReadBlock"] = READ_BLOCK
    note(fy, "runNote0001_1106", "Run 0001: first mint 2026-11-03 21:10:07 WIB (tidak ada mint lebih awal); umur ~51,7 jam >48 jam -> AGE-EXCLUDED track C. mint() disperses 3.000 FYINU (postingan Boltbook); registry-bytes True tapi Sourcify not_verified; bentuk S2 TIDAK terkonfirmasi (tanpa ABI terverifikasi + tanpa free views); totalSupply 867.000 FYINU, totalMinted 289. BUKAN lead.")

# Agent Grove -> upcoming watchlist
snap["contracts"]["Agent Grove"] = {
    "address": "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c",
    "status": "watchlist-only-upcoming-2026-11-06",
    "name": "Agent Grove", "kind": "ERC721",
    "site": "https://agent-grove.pages.dev/",
    "FREE_SUPPLY": 2500, "MAX_SUPPLY": 12500,
    "freeOpen": False, "freeClaimed_user": 0, "userBalance": 0,
    "owner": "0x41a192cb1cc16cc1ff98dfa9c338f436b41fa5b3",
    "lastReadBlock": READ_BLOCK,
    "baselineNote": ("Ditemukan via sapuan web run 0001 (search index). Free mint bertahap: 2.500 pohon gratis dalam 10 fase x 250, jeda 10 jam; "
                     "fase 1 penuh (250/250); fase 2 dibuka 2026-11-06 06:05 UTC (13:05 WIB) — BELUM DIBUKA saat run ini (freeOpen=False). "
                     "Maks 1 pohon gratis/wallet selamanya; freeClaimed(user)=0, balance 0. Situs agent-grove.pages.dev ADA (website evidence). "
                     "UPCOMING watchlist-only — bukan kandidat/lead; cek ulang saat fase 2 dibuka."),
}

# ---------- track_c updates ----------
tc = snap.get("track_c", {})
if "NJAR" in tc:
    tc["NJAR"]["giftsClaimed"] = 561
    tc["NJAR"]["runNote0001_1106"] = "Run 0001: giftsClaimed 530->561 (+31); status track-c-lead-gate-blocked TETAP (tidak ada perubahan tier)."
if "Predictagent-PRDICT" in tc:
    tc["Predictagent-PRDICT"]["totalMints"] = 158
    tc["Predictagent-PRDICT"]["mintOpen"] = True
    tc["Predictagent-PRDICT"]["quote_user_1"] = 0
    tc["Predictagent-PRDICT"]["runNote0001_1106"] = "Run 0001: totalMints 128->158 (+30), mintOpen=True, quote(user,1)=0; status track-c-lead-gate-blocked TETAP."
if "DROID" in tc:
    tc["DROID"]["runNote0001_1106"] = "Run 0001: SEMUA view sale gagal dibaca (None) — BUKAN nol; nilai lama dipertahankan; tetap watchlist-only-age-slot-unverified."
if "OSK" in tc:
    tc["OSK"]["opened"] = 0
    tc["OSK"]["runNote0001_1106"] = "Run 0001: opened=False (tetap belum dibuka)."
if "IMARS" in tc:
    tc["IMARS"]["opened"] = 1
    tc["IMARS"]["runNote0001_1106"] = "Run 0001: opened=1 (sudah tercatat terbuka sejak run 1231), freeMinted 300/300 FREE_SHARES (pool gratis habis) — tetap BUKAN lead."
if "NIULAI" in tc:
    tc["NIULAI"]["launched"] = 0
    tc["NIULAI"]["phase"] = 4
    tc["NIULAI"]["freeClaimed"] = 4444
    tc["NIULAI"]["runNote0001_1106"] = "Run 0001: launched=False, phase=4, freeClaimed=4444 — tetap belum dibuka."

# ---------- top-level run note ----------
snap["runNote0001_1106"] = (
    "Run 0001 (dijadwalkan 2026-11-06 00:01 WIB, eksekusi ~00:24-01:35 WIB). "
    "20 EARLY LEAD BARU dilaporkan sekali (gelombang template costOf/mintsLeft, mint pertama gratis): 12 koreksi dari paid-only "
    "(PRICKLY, unicorn.exe, Blend In, Buzzkill, Whale Alert, Fresh Hatch, Lion's Share, Otter Nonsense, Hot Springs, Down Under, "
    "Toucan Play, jelly.exe — klasifikasi paid-only run 2231/2331 SALAH, didasarkan pada price()=0.0002 BNB; costOf(user,1)=0 + "
    "mintsLeft(user)=10 + sample mint tx value 0 terverifikasi on-chain run ini) + 8 first-seen scan (Los Flamingos, Moonhowlers, "
    "Counting Sheep, Tusk & Trunk, getpuffr, Hippo Social Club, LLAMA DRAMA, Danger Noodles). Semua: first mint terverifikasi "
    "2026-11-05 22:25-23:52 WIB (umur ~1-2,5 jam), registry-bytes hit, slot user TERBUKA, free %% UNVERIFIED (tanpa free-cap view), "
    "velocity baseline pertama, website/X UNVERIFIED, promosi DISCARDED aturan same-owner (grup 0x293f... x10 + 0x1103... x10). "
    "TIDAK di-preview/di-mint (early). "
    "PERUBAHAN: Binance Agent free pool SELLOUT (123/123) -> dilaporkan sekali + DIHAPUS dari snapshot (juga ada MintRadar red flag di postingan Boltbook, moot). "
    "AGE-EXCLUDED (log-only + tombstone, bukan lead): Night Shift (first mint <=2026-10-27 08:18, >10 hari), Cuprihive (2026-11-03 20:01, 52,8 jam), "
    "Skyagent (2026-11-03 05:16, 67,5 jam), Rookling (2026-10-30 02:36, ~6,9 hari), FYINU track C (2026-11-03 21:10, 51,7 jam). "
    "0 kandidat track-A baru, 0 strong lead baru/promosi, 0 lead/kandidat track-C baru, 0 pending claim baru/dibuka (pending_claims kosong; BINANCEAI tetap refund/failed: launched=False, isRefundPhase=True). "
    "RUTE 1: HIVE flat 1253; Moonfall 27; GHOST 370 (free 1,9%%, velocity GAGAL 0.48x); Sonofluidic 421 (free 18,6%%, velocity GAGAL 0.58x); "
    "Mossminds 786 (free 27,2%%, promosi tetap discarded same-owner + gate gagal); Snail Mail 287 (paid-only tetap, quote gagal baca); "
    "Agent Coffee 613; Driftnauts 628 (23,8%%); AGENTIC PERP 61; Agent Wallet semua view gagal; WHALE 3520 (velocity GAGAL 0.52x; deadline umur 2026-11-06 17:33 WIB); "
    "gate-blocked x10 tanpa perubahan (deadline umur 2026-11-07 11:48-20:00 WIB; BNB CACHE semua view gagal); NJAR giftsClaimed 561; PRDICT totalMints 158; "
    "DROID semua view gagal; OSK belum dibuka; IMARS terbuka + pool gratis habis; NIULAI belum dibuka phase 4. "
    "SCAN rute 4 SUKSES: jendela 131854448-131856447 (2000 blok, cap), gap dilewati 131851106-131854447 (3342 blok; gap kumulatif sejak run 1831 ~36.800 blok); "
    "245 NFT + 470 ERC-20, 80 panggilan Ankr, 0 error; 14 first-seen (12 registry=True -> 8 early + AgentIdBSC paid + 3 paid 0.0005; 2 registry=False not-early). "
    "5c: 8 ERC-20 baru dicek, 0 lolos S1/S2 (semua Sourcify not_verified); 49 sudah terperiksa; 0 dibuang sampling limit. "
    "Feed Sourcify: 20 kontrak, 0 lolos S1/S2 (10 sudah hot-leg-seen; 4 retry-exhausted = inconclusive). "
    "Boltbook en+zh: postingan Cuprihive (sumber gelombang 0.0002), koreksi Fleet Genesis (kontrak asli sold out 1000/1000), Night Shift audit, "
    "Mossminds 782, GHOST 369, DEWATA 209 (bukan agent-shaped), AgentGlyph free pool habis (sudah dilaporkan + dihapus run 2131), Piggy sold out (known), "
    "Jolly age-excluded (sudah dihapus run 2331), Agent Panda PoW-gated + excluded. "
    "Sapuan web: hanya daftar lama 26-28 Okt; Agent Grove BARU (upcoming, fase 2 dibuka 13:05 WIB hari ini) ditambahkan watchlist-only-upcoming; "
    "CodexNFT BUKAN gratis (creator fee 0.000075 BNB); Celiuz berbayar per skill.md (known). "
    "Komplemen (6): Odaily hanya makro; Square hanya daftar lama. Bridge scan-bridge.json TIDAK BERUBAH (113 kontrak, mtime 2026-11-04 17:40 UTC) — tidak ada temuan pelengkap scan baru. "
    "twitterapi.io TIDAK dipanggil. 0 eksekusi (0 preview, 0 mint, 0 approve, 0 swap). "
    + ba_note
)
snap["timestamp_wib"] = "2026-11-06 run 0001"

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("snapshot updated; contracts now:", len(snap["contracts"]))

# ---------- seen file: add the 14 scan first-seen ----------
seen = json.load(open(HF + "onchain-scan-seen.json"))
added = 0
for c in scan["contracts"]:
    k = c["address"].lower()
    if k not in seen["contracts"]:
        seen["contracts"][k] = c.get("first_block")
        added += 1
seen["_meta"]["last_updated_wib"] = "2026-11-06 run 0001"
seen["_meta"]["last_scan_window"] = "131854448-131856447"
json.dump(seen, open(HF + "onchain-scan-seen.json", "w"), indent=1)
print("seen file: +%d addresses (now %d)" % (added, len(seen["contracts"])))

# ---------- scan state ----------
state = json.load(open(HF + "onchain-scan-state.json"))
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = "2026-11-06 run 0001"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan["contracts"])
state["erc20_mint_contracts"] = scan.get("erc20_mint_contracts")
state["skipped_gap"] = "131851106-131854447 (3342 blok, window dari watermark 131851105 ke head 131856447 = 5342 blok > cap 2000; scan menutup 2000 blok terbaru 131854448-131856447)"
state["note"] = ("Scan run 0001 SUKSES (80 panggilan Ankr, 0 error). 14 first-seen: 8 EARLY baru (gelombang 0x1103), "
                 "AgentIdBSC paid-only, 3 paid 0.0005 (Krypt Titan/Ethereal Bear/Solar Panda), 2 not-early (TapeOut Miner/Bavarsis Node). "
                 "Gap kumulatif sejak run 1831 ~36.800 blok tak ter-scan.")
state["last_scan_window"] = "131854448-131856447"
state["ankr_calls_last_scan"] = scan.get("ankr_calls")
state["errors_last_scan"] = scan.get("errors", [])
state["scan_started_wib"] = "2026-11-06 00:25"
state["scan_finished_wib"] = "2026-11-06 00:42"
state["head_at_scan_start"] = 131856422
json.dump(state, open(HF + "onchain-scan-state.json", "w"), indent=1)
print("scan state updated; watermark ->", scan["to_block"])
