#!/usr/bin/env python3
"""Merge run 2026-11-05-2231 into the FREE BACOT snapshot + seen file.
Parent merge. Reads: onchain-snapshot.json, run-2026-11-05-2231-reread-lean.json,
run-2026-11-05-2231-ba-deep.json, run-2026-11-05-2231-triage-wave.json,
run-2026-11-05-2231-scan-firstseen.json, run-2026-11-05-2231-leg236.json,
onchain-scan-2026-11-05-2231.json. Writes: snapshot (backup first), seen file.
None = failed read, never zero. Velocity interval: 48 min (2131 read ~22:03 -> 2231 read ~22:51 WIB).
"""
import json, shutil, copy
from datetime import datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL_MIN = 48.0
NOW_WIB = "2026-11-05 23:35 WIB"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot-2231.bak.json")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-05-2231-reread-lean.json"))
ba = json.load(open(f"{BASE}/run-2026-11-05-2231-ba-deep.json"))
wave = json.load(open(f"{BASE}/run-2026-11-05-2231-triage-wave.json"))
firstseen = json.load(open(f"{BASE}/run-2026-11-05-2231-scan-firstseen.json"))
leg236 = json.load(open(f"{BASE}/run-2026-11-05-2231-leg236.json"))
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-05-2231.json"))

# index snapshot contracts by lowercase address
by_addr = {}
for k, v in snap["contracts"].items():
    if isinstance(v, dict) and v.get("address"):
        by_addr[v["address"].lower()] = (k, v)

def primary_counter(entry):
    for f in ("totalSupply", "totalMinted", "freeMinted"):
        if entry.get(f) is not None:
            return f
    return None

print("=== VELOCITY / RE-READ UPDATES ===")
for name, r in reread["reread"].items():
    addr = r["address"].lower()
    if addr not in by_addr:
        print(f"SKIP (not in snapshot): {name} {r['address']}")
        continue
    key, e = by_addr[addr]
    field = primary_counter(e)
    old = e.get(field) if field else None
    new = r.get(field)
    # also update freeMinted / totalSupply / totalMinted / freeClaimed when non-None
    for f in ("totalSupply", "totalMinted", "freeMinted", "freeClaimed"):
        if r.get(f) is not None:
            e[f] = r[f]
    if "balanceOf_user" in r and r["balanceOf_user"] is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    if field and old is not None and new is not None:
        minted = new - old
        rate = minted / INTERVAL_MIN
        prev_rate = e.get("currentRatePerMin") or 0
        e["previousTotalSupply"] = old
        e["mintedInInterval"] = minted
        e["intervalMinutes"] = INTERVAL_MIN
        e["previousRatePerMin"] = prev_rate
        e["currentRatePerMin"] = round(rate, 3)
        passes = minted >= 20 and prev_rate > 0 and rate >= 1.5 * prev_rate
        e["velocityLegPasses"] = passes
        ratio = (rate / prev_rate) if prev_rate else float("inf")
        e["velocityNote2231"] = (
            f"Run 2231 ({NOW_WIB}): {field} {old}->{new} (+{minted}, {rate:.2f}/min vs prev "
            f"{prev_rate}/min = {ratio:.2f}x) -> velocity {'PASSES' if passes else 'FAILS'} "
            f"(butuh >=1.5x DAN >=20 token). {'Tetap early (free %/slot/umur unverified).' if passes else ''}"
            f" Block() None saat baca (RPC degradasi)."
        )
        print(f"{name}: {field} {old}->{new} +{minted} rate {rate:.2f}/min prev {prev_rate} ratio {ratio:.2f}x -> {'PASS' if passes else 'FAIL'}")
    else:
        e["velocityNote2231"] = (
            f"Run 2231 ({NOW_WIB}): baca {field} gagal (None) atau baseline None "
            f"(old={old}, new={new}) - nilai lama dipertahankan, bukan nol. Block() None (RPC degradasi)."
        )
        print(f"{name}: {field} old={old} new={new} -> NO CONCLUSION (read failed)")
    e["lastReadWib"] = "2026-11-05 run 2231"
    # slot fields from reread when non-None
    for f in ("canFreeMint_user", "claimedFree_user", "quote_user_1", "mintedBy_user", "freeUsed_user"):
        if r.get(f) is not None:
            e[f] = r[f]

# near-threshold notes
for key, note in (
    ("Mossminds", "Run 2231: freeMinted 678/2880 = 23.54% (<25%), slot terbuka (canFreeMint=1, claimedFree=0) - DEKAT ambang 25% strong lead, tetap early."),
    ("Cachejack", "Run 2231: freeMinted 470/2000 = 23.5% (<25%), slot terbuka (canFreeMint=1, claimedFree=0) - DEKAT ambang 25% strong lead, tetap early."),
    ("Jolly", "Run 2231: freeMinted 3499/5000 = 69.98%, tetap strong-lead-gate-blocked (tanpa website terverifikasi). Batas umur 48 jam berakhir ~23:27 WIB malam ini (first mint 2026-11-03 23:27:33 WIB) - exclusion dicek run 2331 bila masih belum sold out."),
):
    for k, v in snap["contracts"].items():
        if k == key and isinstance(v, dict):
            v["runNote2231"] = note
            print(f"note {key}: {note[:80]}...")

# --- new entries: Binance Agent (early lead) ---
fs_by_addr = {c["address"].lower(): c for c in firstseen["contracts"]}
ba_fs = fs_by_addr.get("0xe3a382b8e577a58a5540420c11aba287c62e49f4", {})
snap["contracts"]["Binance Agent"] = {
    "address": "0xE3a382B8e577A58A5540420C11ABa287C62e49f4",
    "name": "Binance Agent",
    "symbol": "BA",
    "status": "early-lead-reported-2026-11-05",
    "firstSeenBlock": 131842544,
    "firstSeenWib": "2026-11-05 ~22:51 WIB (run 2231, scan window 131840908-131842907)",
    "mintsInWindow": 7,
    "distinctMintersInWindow": 7,
    "AGENT_REGISTRY": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "sourcifyVerified": True,
    "FREE_SUPPLY": 123,
    "freeMinted": 78,
    "freePct": 63.4,
    "MAX_SUPPLY": 444,
    "MAX_FREE_PER_WALLET": 1,
    "balanceOf_user": 0,
    "launchAge": "UNVERIFIED (first-mint time tidak bisa didatangi: Ankr address-filtered getLogs return 0 bahkan untuk HIVE di rentang HIVE sedang minting; block-timestamp lookup gagal di semua RPC; totalMinted 69 vs 7 mint di jendela menunjukkan aktivitas lebih awal yang tidak bisa didatangi)",
    "userSlot": "UNVERIFIED (quote/freeClaimed(user)/mintedBy(user)/freeUsed(user)/canFreeMint(user) semua None = gagal baca RPC, bukan nol)",
    "website": "UNVERIFIED (contractURI() None)",
    "xDiscussion": "UNVERIFIED",
    "PRICE": None,
    "mintOpen": None,
    "totalSupply": None,
    "velocityVerified": False,
    "xVerified": False,
    "freeSlotUserOpen": None,
    "baselineNote": "EARLY LEAD run 2231: agent-mint-shaped (registry + free views + Sourcify verified), first mints terverifikasi on-chain di run (7 mint / 7 minter, blok pertama 131842544), free 78/123 = 63.4% (>50% dan >25%). BUKAN strong lead (slot + umur unverified), BUKAN kandidat (tanpa website, tanpa diskusi, tanpa velocity). TIDAK PERNAH di-preview/di-mint sebagai early lead. Dilaporkan sekali ke chat utama run 2231.",
    "lastReadWib": "2026-11-05 run 2231",
    "lastReadBlock": 131842907,
}
print("added Binance Agent (early lead)")

# --- new entries: 15 wave contracts, watchlist-only-paid-only ---
paid_prices = {
    "buzzkill": 0.0002, "whale alert": 0.0002, "blend in": 0.0002, "fresh hatch": 0.0002,
    "lion's share": 0.0002, "otter nonsense": 0.0002, "hot springs": 0.0002, "down under": 0.0002,
    "v64": 0.002, "n30": 0.001,
}
for name, w in wave.items():
    addr = w["address"]
    fs = fs_by_addr.get(addr.lower(), {})
    price = paid_prices.get(name.lower())
    if price is None:
        # PRICKLY / unicorn.exe: price read failed, same template as wave; PULQ / NEXH / ALGO: sniper-test factory
        price_note = "price() gagal dibaca (RPC), tapi template sama dengan wave 0.0002 BNB / sniper-test factory"
    else:
        price_note = f"price() = {price} BNB terverifikasi on-chain"
    entry = {
        "address": addr,
        "name": name,
        "status": "watchlist-only-paid-only-2026-11-05",
        "firstSeenBlock": fs.get("first_block"),
        "firstSeenWib": "2026-11-05 run 2231, scan window 131840908-131842907",
        "mintsInWindow": fs.get("mint_count"),
        "distinctMintersInWindow": fs.get("distinct_minters"),
        "totalSupply": w.get("totalSupply"),
        "totalMinted": w.get("totalMinted"),
        "freeClaimed": w.get("freeClaimed"),
        "freeMinted": w.get("freeMinted"),
        "price_BNB": price,
        "sourcifyVerified": "UNVERIFIED-ARTIFACT (triage script run 2231 memakai endpoint Sourcify yang salah /v2/contracts/ - 404; bukan verdict)",
        "baselineNote": (
            f"Run 2231 first-seen, watchlist-only-paid-only: {price_note}; tidak ada free view "
            f"(freeClaimed/freeMinted None). Bukan early lead (bukan free-shaped). "
            f"ALGO/NEXH/Pulse Quokka Agent: factory sniper-test yang sama dengan trio run 2131 "
            f"(Bastion Ibis/Umbra Nomad/Neural Sovereign), BASE_URI ipfs://sniper-test-nft/, totalSupply 3333, totalMinted 1."
            if name in ("ALGO", "NEXH", "Pulse Quokka Agent") else
            f"Run 2231 first-seen, watchlist-only-paid-only: {price_note}; tidak ada free view. Bukan early lead."
        ),
        "lastReadWib": "2026-11-05 run 2231",
        "lastReadBlock": 131842907,
    }
    snap["contracts"][name] = entry
    print(f"added wave: {name} ({addr}) price={price}")

# --- track_c: Ethereal Mind + Agentidbsc (checked, not leads) ---
snap.setdefault("track_c", {})
snap["track_c"]["Ethereal Mind"] = {
    "sale": "0xa71dACba7c425e2715CfD12E253044D09ceE774e",
    "token": "ETHM",
    "status": "checked-not-lead-2026-11-05",
    "note": "Run 2231 (feed Sourcify via Subagent B): agent-gated token sale, 1 spot minted, spotsLeft 4999, WEBSITE() = https://agenticspace.xyz - PARKED / for sale on GoDaddy, bukan situs proyek live; tanpa free view -> BUKAN lead track-C; gate gagal. Watchlist-only.",
    "lastReadWib": "2026-11-05 run 2231",
}
snap["track_c"]["Agentidbsc"] = {
    "sale": "0x716BFaB3B7b0301D17Af0fF4c50a880C7721F39C",
    "status": "checked-not-lead-2026-11-05",
    "note": "Run 2231 (feed Sourcify via Subagent B): freeLeft ada tapi tanpa registry/AgentGate -> bukan agent-shaped, bukan lead. Watchlist-only.",
    "lastReadWib": "2026-11-05 run 2231",
}
snap["track_c"]["Feed-ERC20-0xB2734719"] = {
    "sale": "0xB2734719",
    "status": "checked-not-sale-shape-2026-11-05",
    "note": "Run 2231 (feed Sourcify via Subagent B): sale ERC-20, mint+quote+agent tapi tanpa free view -> gagal S1/S2. Bukan lead track-C.",
    "lastReadWib": "2026-11-05 run 2231",
}
snap["track_c"]["Feed-ERC20-0x97805a75"] = {
    "sale": "0x97805a75",
    "status": "checked-not-sale-shape-2026-11-05",
    "note": "Run 2231 (feed Sourcify via Subagent B): sale ERC-20, mint+quote+agent tapi tanpa free view -> gagal S1/S2. Bukan lead track-C.",
    "lastReadWib": "2026-11-05 run 2231",
}
print("added track_c checked entries: Ethereal Mind, Agentidbsc, 2 feed ERC-20")

# --- track_c re-read updates ---
tc_updates = {
    "DROID": {"freeMinted": 570, "totalMinted": 570},
    "OSK": {"totalMinted": 2277},
    "IMARS": {"freeMinted": 300, "totalMinted": 624},
    "QAGENT-2": {"sharesMinted": 6702},
    "NIULAI": {"phase": 4},
}
for k, upd in tc_updates.items():
    if k in snap["track_c"] and isinstance(snap["track_c"][k], dict):
        snap["track_c"][k].update(upd)
        snap["track_c"][k]["lastReadWib"] = "2026-11-05 run 2231"
        print(f"track_c updated {k}: {upd}")
    else:
        print(f"track_c {k} NOT FOUND (skipped)")

# --- top-level run notes ---
snap["last_run"] = "2026-11-05-2231"
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = NOW_WIB
snap["runNote2231"] = (
    "Run 2231 (2026-11-05 22:31 WIB): EARLY LEAD BARU 1: Binance Agent (BA) 0xE3a382B8e577A58A5540420C11ABa287C62e49f4 "
    "- free 78/123 = 63.4%, 7 mint/7 minter di jendela, blok pertama 131842544; umur + slot user UNVERIFIED, website UNVERIFIED; "
    "tidak pernah di-preview/di-mint. 0 kandidat baru, 0 strong lead baru/promosi, 0 kandidat/lead track-C baru, 0 pending claim baru/dibuka. "
    "15 kontrak first-seen lain watchlist-only-paid-only (wave 0.0002 BNB x8, V64 0.002, N30 0.001, PRICKLY/unicorn.exe template sama, "
    "ALGO/NEXH/Pulse Quokka Agent sniper-test factory). Velocity (interval ~48 mnt vs run 2131): LOLOS PassAgentX 3634->3688 (+54, ~1.13/mnt, 2.14x), "
    "Sonofluidic 186->296 (+110, ~2.29/mnt, 6.7x), GHOST 267->321 (+54, ~1.13/mnt, 6.2x) - ketiganya TETAP early (free %/slot/umur unverified); "
    "GAGAL: Forklings 1.21x, Kitebots 0.65x, Thronemind +6, Hashseers +5, Smeltbots +7, Layerloom +9, Tumblebots +12, AGENTIC PERP +5; "
    "HIVE flat 1253, Mummyhive flat 600 (freeClaimed 582/600, bukan sellout). Mossminds 678/2880 = 23.54% dan Cachejack 470/2000 = 23.5%, "
    "keduanya slot terbuka - dekat ambang 25% strong lead, tetap early. Jolly 3499/5000 = 69.98%, strong-lead-gate-blocked; batas umur 48 jam "
    "berakhir ~23:27 WIB malam ini - exclusion dicek run 2331. Track-C re-read: DROID 570, OSK totalMinted 2277, IMARS 300/624, "
    "QAGENT-2 sharesMinted 6702, NIULAI phase 4; NJAR + PRDICT semua view None (RPC gagal, tanpa kesimpulan). Track-B BINANCEAI tetap "
    "refund/failed (launched=0, isRefundPhase=1). Bridge scan-bridge.json tidak berubah (113 kontrak). Tidak ada age-exclusion baru. "
    "Boltbook: hanya MirrorPair post 1163 (known). Route 3: hanya item known. Route 6: Square tanpa link baru; Odaily/PANews hanya makro. "
    "Ethereal Mind (ETHM) WEBSITE agenticspace.xyz = parked GoDaddy, bukan lead; Agentidbsc bukan agent-shaped. "
    "KOREKSI METODOLOGI run ini: (1) seen file punya 1369 kunci duplikat beda case (9017 kunci, 7647 unik lowercase) - dedupe WAJIB case-insensitive; "
    "(2) track-c-scan-checked.json punya dict nested 'checked' (1894) + kunci top-level (53) - skip-list 5c WAJIB cek keduanya; 5c run ini: "
    "3 alamat benar-benar baru (2x 404 dicatat checked, 1x 0x2eA26Bc2 inconclusive remote-closed - retry run berikut), 17 dari 20 'top-20' ternyata recheck; "
    "sisa 64 alamat mint_count>=10 sudah tercakup, remainder dropped = 0. (3) 5 kontrak (Shenlong/No Names/Cosmic Macabre/AGENT GLYPHS/Crown Race Pass) "
    "sempat dikira first-seen karena bug dedupe case-sensitive di skrip parent - faktanya SUDAH ada di seen file (kunci mixed-case), bukan baru; tidak ditambahkan. "
    "(4) triage-wave memakai endpoint Sourcify salah (/v2/contracts/ -> 404) - 'sourcify verified: False' di file itu artefak, bukan verdict; "
    "klasifikasi paid-only bersandar pada price() on-chain. Degradasi RPC berat run ini: banyak view None (block() None; NJAR/PRDICT tidak terbaca). "
    "0 eksekusi (0 preview, 0 mint, 0 approve, 0 swap)."
)
snap["runNote2231_scan"] = (
    "Run 2231 scan (Subagent A): window 131840908-131842907 (cap 2000 blok), gap 131837334-131840907 dilewati (3574 blok; "
    "kumulatif sejak run 1831 ~27263 blok), head 131842907, 80 Ankr calls, 0 errors, 246 NFT + 603 ERC-20 di jendela, durasi 19.7 mnt "
    "(22:44-23:03 WIB). True first-seen 16 (1 early lead BA + 15 watchlist-only). Watermark -> 131842907. "
    "5c: 64 ERC-20 mint_count>=10, 3 benar-benar baru, 0 lolos S1/S2, remainder dropped 0. Sourcify feed 20 kontrak (verifiedAt 15:33-15:43Z), 0 lolos S1/S2."
)

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print(f"\nSnapshot written. contracts: {len(snap['contracts'])}, track_c: {len(snap['track_c'])}")

# --- seen file: append first-seen ERC-20 (NFT 16 already appended by Subagent A) ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_contracts = seen["contracts"]
lowered = {k.lower() for k in seen_contracts.keys()}
snap_addrs = {v["address"].lower() for v in snap["contracts"].values() if isinstance(v, dict) and v.get("address")}
added = 0
for e in scan["erc20_mint_contracts_list"]:
    a = e["address"].lower()
    if a not in lowered and a not in snap_addrs:
        seen_contracts[a] = e.get("first_block")
        lowered.add(a)
        added += 1
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
print(f"Seen file: +{added} ERC-20 first-seen appended (total keys now {len(seen_contracts)})")
print("MERGE DONE")
