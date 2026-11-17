#!/usr/bin/env python3
"""Run 2331 parent merge: snapshot update + run notes. Run AFTER BscScan (L)
result for BNB CACHE is recorded in run-2026-11-05-2331-bscscan.json.
Backs up the snapshot first. Single writer."""
import json, copy, shutil, os

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-2331"

def load(n):
    with open(f"{BASE}/{n}") as f: return json.load(f)

snap = load("onchain-snapshot.json")
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot-2331.bak.json")
reread = load("run-2026-11-05-2331-reread-lean.json")
triage = load("run-2026-11-05-2331-triage.json")
firstseen = load("run-2026-11-05-2331-scan-firstseen.json")
boltbook = load("run-2026-11-05-2331-boltbook.json")
scan = load("onchain-scan-2026-11-05-2331.json")
f5c = load("run-2026-11-05-2331-5c-shape.json")  # file Subagent A (struktur baru)
try:
    bscscan = load("run-2026-11-05-2331-bscscan.json")
except Exception:
    bscscan = {"website": None, "note": "BscScan (L) result file missing at merge time"}

contracts = snap["contracts"]
track_c = snap.setdefault("track_c", {})

# ---------- 1. Route-1 re-read: overwrite only non-None values; velocity ----------
# interval run 2231 reads (~23:35 WIB) -> run 2331 reads (~00:05 WIB): ~30 min
INTERVAL_MIN = 30.0
def upd(name, reads, view="totalSupply"):
    c = contracts.get(name)
    if c is None: return
    old_ts = c.get("totalSupply")
    new_ts = reads.get("totalSupply")
    if new_ts is None and reads.get("totalMinted") is not None:
        new_ts = reads.get("totalMinted")
        c["supplyView"] = "totalMinted"
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "PRICE", "price", "mintOpen",
              "balanceOf_user", "mintedBy_user", "freeUsed_user",
              "canFreeMint_user", "claimedFree_user", "quote_user_1",
              "costOf_user_1", "mintsLeft_user", "FREE_CAP"):
        if reads.get(k) is not None:
            c[k] = reads[k]
    # velocity on the supply view
    if isinstance(new_ts, int) and isinstance(old_ts, int):
        minted = new_ts - old_ts
        rate = minted / INTERVAL_MIN if INTERVAL_MIN else 0.0
        prev_rate = c.get("currentRatePerMin")
        ratio = (rate / prev_rate) if (prev_rate and prev_rate > 0) else None
        passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        c["previousTotalSupply"] = old_ts
        c["previousRatePerMin"] = prev_rate
        c["currentRatePerMin"] = round(rate, 4)
        c["mintedInInterval"] = minted
        c["intervalMinutes"] = INTERVAL_MIN
        c["velocityLegPasses"] = passes
        c["velocityNote2331"] = (f"Run 2331 (~00:05 WIB, interval ~{INTERVAL_MIN:.0f} mnt vs run 2231): "
            f"{old_ts}->{new_ts} (+{minted}, {rate:.3f}/mnt vs prev {prev_rate} = "
            f"{ratio if ratio is None else round(ratio, 2)}x) -> velocity "
            f"{'LOLOS' if passes else 'GAGAL'}.")
    elif new_ts is None:
        c["velocityNote2331"] = (f"Run 2331: baca {view} gagal (None) - nilai lama dipertahankan, "
            "bukan nol; velocity TIDAK dihitung.")
    c["lastReadBlock"] = reread.get("block") or scan.get("to_block")
    c["lastReadWib"] = "2026-11-06 run 2331"

for name, reads in reread.get("reread", {}).items():
    upd(name, reads)

# velocity for HIVE uses totalSupply 1253 flat (handled by upd)
# ---------- 2. Track-C re-read values (store key fields, non-None only) ----------
for key, reads in reread.get("track_c", {}).items():
    e = track_c.get(key)
    if not isinstance(e, dict):
        continue
    for k in ("freeMinted", "totalMinted", "sharesMinted", "opened", "launched",
              "phase", "saleEnded", "freeSharesRemaining"):
        if reads.get(k) is not None:
            e[k] = reads[k]
    e["lastReadWib"] = "2026-11-06 run 2331"

# ---------- 3. Track-B BINANCEAI ----------
tb = reread.get("track_b", {}).get("BINANCEAI", {})
snap["runNote2331_binanceai"] = (f"Run 2331: BINANCEAI launched={tb.get('launched')} (None=gagal baca), "
    f"isRefundPhase={tb.get('isRefundPhase')}, tokenClaimed(user)={tb.get('tokenClaimed_user')}, "
    f"tokenBalance(user)={tb.get('tokenBalance_user')} - tetap refund/failed, tidak dilaporkan ulang.")

# ---------- 4. Jolly age-exclusion ----------
jolly = contracts.get("Jolly")
if jolly is not None:
    fm = jolly.get("freeMinted")
    snap["runNote2331_jolly_age_exclusion"] = (
        "Run 2331: Jolly AGE-EXCLUDED + DIHAPUS dari snapshot. First mint terverifikasi "
        "2026-11-03 23:27:33 WIB (blok 131464781); batas 48 jam berakhir 2026-11-05 23:27:33 WIB; "
        f"baca segar run ini freeMinted={fm}/5000 (belum sold out). Status sebelumnya "
        "strong-lead-gate-blocked. Dilaporkan sekali ke chat utama run ini.")
    del contracts["Jolly"]

# ---------- 5. Mossminds: promotion discarded (same-owner) + gate FAILED ----------
moss = contracts.get("Mossminds")
if moss is not None:
    moss["status"] = "promotion-discarded-same-owner-2026-11-05"
    moss["totalSupply"] = 760
    moss["owner"] = "0x4e9b1d076fda3605ad63f81a94a8693342a08dba"
    moss["velocityNote2331"] = ("Run 2331: totalSupply 751->760 (+9, <20) -> velocity GAGAL; "
        "freeMinted baca run ini None (gagal RPC; hot-leg 2334: 748/2880 = 25,97%).")
    moss["discardNote2331"] = (
        "PROMOTION DISCARDED run 2331: free 748/2880 = 25,97% (hot-leg 2334; baca main-run None), "
        "umur terverifikasi <=48 jam (first mint 2026-11-05 20:00:41 WIB), slot terbuka "
        "(canFreeMint=1, claimedFree=0) - ketiga kaki strong TERPENUHI, tetapi DISCARDED aturan "
        "same-owner 2026-11-03: owner() 0x4e9b1d076fda3605ad63f81a94a8693342a08dba sama dengan "
        "Thronemind, Hashseers, Layerloom, Cachejack, Tumblebots, Roguefall (factory wave). "
        "Gate website-only JUGA GAGAL: (A) tidak ada hit alamat; (B) Boltbook belum ada post Mossminds; "
        "(C) metadata Sourcify tanpa URL; (D) tidak ada pola same-family; (G) pencarian nama hanya "
        "Moss/MossAI lain yang tidak terkait; (H) contractURI() None; (I) tokenURI(1) None; "
        "(J) ABI tanpa fungsi website; (K) indeks GitHub kosong (code search sejati butuh auth); "
        "(M) site:vercel.app/pages.dev/deed.page kosong; (L) tidak dibaca via browser (hot-leg "
        "BscScan task dibatalkan sebelum selesai); (N) tanpa linkage. TIDAK dipromosikan, "
        "TIDAK di-preview/di-mint, TIDAK dilaporkan sebagai lead (preseden Gourdwick/Vesperfang).")

# ---------- 6. Binance Agent: probable sellout, NOT removed (freeMinted unconfirmed) ----------
ba = contracts.get("Binance Agent")
if ba is not None:
    ba["totalMinted"] = 123
    ba["runNote2331"] = ("Run 2331: totalMinted 123 = FREE_SUPPLY 123 (baca sukses) - KEMUNGKINAN "
        "sold out; freeMinted gagal dibaca ulang (None di lean re-read; retry timeout 240 dtk; "
        "Ankr eth_call tidak didukung -32601). Definisi sellout job (free counter == FREE_SUPPLY) "
        "BELUM terverifikasi -> TETAP early lead, TIDAK dihapus, TIDAK dilaporkan sebagai sellout; "
        "konfirmasi freeMinted ditunda ke run berikut.")

# ---------- 7. Snail Mail: price() re-confirm failed ----------
sn = contracts.get("Snail Mail")
if sn is not None:
    sn["runNote2331"] = ("Run 2331: konfirmasi paid-only GAGAL dibaca ulang (price() None di lean "
        "re-read; retry timeout; Ankr tanpa eth_call). Status tetap early-lead-reported; "
        "reklasifikasi ke watchlist-only-paid-only ditunda ke run berikut bila price() "
        "terkonfirmasi 0,0002 BNB. Nilai snapshot price 0,0002 BNB dari run 2231 dipertahankan.")

# ---------- 8. BNB CACHE Server: strong-lead promotion + gate ----------
cache = contracts.get("BNB CACHE Server")
gate_l = bscscan.get("website")
if cache is not None:
    cache["freeServersClaimed"] = 250
    cache["freePctVerified"] = round(250 / 777 * 100, 2)
    cache["lastReadWib"] = "2026-11-06 run 2331 (baca Subagent B blok 131852006)"
    cache["runNote2331"] = (
        "Run 2331: freeServersClaimed 71->250/777 = 32,2% (baca segar Subagent B blok 131852006, "
        "melewati ambang 25% strong lead); umur terverifikasi <=48 jam (first mint 2026-11-05 "
        "20:00:06 WIB); slot terbuka (freeClaimedBy(user)=0, balanceOf(user)=0); free window "
        "tutup 2026-11-06 20:00:03 WIB. KETIGA kaki strong TERPENUHI -> strong lead.")
    if gate_l:
        cache["status"] = "strong-lead-2026-11-05"
        cache["website"] = gate_l
        cache["gateNote2331"] = ("Gate website-only LOLOS via (L) BscScan token-info: " + str(gate_l))
    else:
        cache["status"] = "strong-lead-gate-blocked-2026-11-05"
        cache["gateNote2331"] = (
            "Gate website-only GAGAL run 2331: (A) tidak ada hit alamat; (B) post Boltbook 23:45 WIB "
            "ada (diskusi) tanpa tautan situs; (C) metadata Sourcify tanpa URL; (D) tidak ada pola "
            "same-family; (E) owner() gagal dibaca (None, RPC) - deployer-group TIDAK terverifikasi; "
            "(G) pencarian nama hanya panduan umum/Agent Harvest/Agent Cards/AGENT MAO; "
            "(H) contractURI() None; (I) tokenURI(1)/(250) None (gagal baca); (J) ABI tanpa fungsi "
            "website; (K) indeks GitHub kosong (code search sejati butuh auth); (M) site:vercel.app / "
            "pages.dev / deed.page / surge.sh kosong; (L) BscScan token-info via live browser: "
            + str(bscscan.get("note", "tidak ada website/social tercatat")) + "; (N) tanpa linkage "
            "(author Boltbook/post X bio tidak diketahui). TIDAK di-preview/di-mint. Dilaporkan "
            "sekali sebagai strong lead + alasan gate-blocked.")

# ---------- 9. Boltbook discoveries (Subagent B) ----------
track_c["Zero Shark"] = {
    "sale": "0x3ebbed7de6afa9dcc0078a993c581fb50ada5693",
    "token": "0x3ebbed7de6afa9dcc0078a993c581fb50ada5693",
    "name": "Zero Shark", "symbol": "ZERO",
    "status": "age-excluded-discovery-2026-11-05",
    "note": ("Run 2331 (Boltbook.fun post 23:16 WIB + verifikasi on-chain Subagent B blok 131852006): "
        "S1-like (mint + quoteAfterOpen/mintPriceE18 + free views + REGISTRY()=registry), FREE_SHARES "
        "2000, freeClaimed 568/2000 = 28,4%, slot user terbuka (freeClaimedBy=0), pair "
        "0x611f4629c1fbbe97864588ef962671ad135b1095; kontrak tunggal token+sale (name/symbol/decimals/"
        "totalSupply pada kontrak yang sama, S2-like). NAMUN AGE-EXCLUDED: MINT_START_AT 2026-11-03 "
        "17:00 WIB -> umur ~55 jam > 48 jam. Bukan lead/kandidat; dicatat, tidak dilaporkan ulang."),
    "lastReadWib": "2026-11-06 run 2331",
}
track_c["Moon Cat"] = {
    "sale": "0x2c002fa8398e4f55314757c9ee7b35ba850125ec",
    "status": "rejected-bad-address-2026-11-05",
    "note": ("Run 2331 (Boltbook.fun post; verifikasi Subagent B): eth_getCode = 0x di dua RPC - "
        "alamat TIDAK punya kode, bukan kontrak ter-deploy. Alamat post salah/dibuat-buat. Bukan lead."),
    "lastReadWib": "2026-11-06 run 2331",
}
contracts["MORPHA"] = {
    "address": "0xb40e4d3b33c5d70ab31a1dde3c240727691cb738",
    "name": "MORPHA", "symbol": "MORPHA", "kind": "ERC721?",
    "status": "watchlist-only-unverified-shape-2026-11-05",
    "totalSupply": 156,
    "firstSeenBlock": None,
    "launchNote": "Umur peluncuran UNVERIFIED (tidak ada waktu launch terverifikasi).",
    "baselineNote": ("Run 2331 (Boltbook.fun posts + triase parent): Sourcify UNVERIFIED; proxy ERC-1967 "
        "(170 byte); totalSupply 150->156; semua free view None (gagal baca/tidak ada); satu post "
        "mengklaim mint gratis tx 0x6380d031659b60204d1b08149760f9387936c17e5ed42124521a82eebd494c01 - "
        "tx TIDAK ditemukan di RPC (getTransactionByHash + receipt null); post lain menyebut "
        "selector mint/freeMint revert pada value 0. Free lane TIDAK terverifikasi. Bukan early lead "
        "(bukan agent-shaped pada bukti yang ada), bukan kandidat. Watchlist-only sampai bentuk "
        "gratis terverifikasi."),
    "lastReadWib": "2026-11-06 run 2331",
}
track_c["SYMBOL"] = {
    "sale": "0x34e81BfE936af79A64D6cD0Eae14b5de9193bDC9",
    "token": "0x265b2a6b32045af53d142f4e32123b28b0df4d7c",
    "site": "https://symbolai.pages.dev/sale",
    "status": "checked-not-sale-shape-2026-11-05",
    "note": ("Run 2331 (rute 3 Subagent B): Sourcify ABI fns buyShares/quote/eligible/gate/priceForIndex/"
        "sharesOf - TANPA free-share view, TANPA registry fn; situs: Tier 1 = 1,00 USDT/share, "
        "2000 shares, pool buka di share #500 - PAID, tanpa free share. Bukan lead track-C."),
    "lastReadWib": "2026-11-06 run 2331",
}

# ---------- 10. Scan first-seen (10) -> snapshot watchlist-only ----------
FS_CLASS = {
    # Klasifikasi final Subagent A (run-2026-11-05-2331-scan-triage.json) - mengikat.
    # Moonfall = EARLY LEAD (bytecode berisi registry + mint tx value 0 + first mints terverifikasi).
    "0x4232308c31927e493e96FdB05134Fa39C26c24D0": ("Moonfall", "MOONFALL", "early-lead-reported-2026-11-05",
        "EARLY LEAD run 2331: 21 mint/11 minter di jendela, blok 131849595-131850981; bytecode (eth_getCode, 21784 byte) berisi alamat registry Agent ID 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; mint tx 0x6e90595ea5e4b676361735dff088670bdee838006cca2f9ef70a93d4181875f7 value 0 BNB (minting gratis terverifikasi); totalSupply 26, MAX_SUPPLY 1001 (2,6%); selector mint 0x484b973c ada di code. KAKI BELUM TERVERIFIKASI: Sourcify NOT verified (404) - nama fungsi mint tak teridentifikasi; umur peluncuran UNVERIFIED (totalSupply 26 vs 21 mint di jendela = 5 mint pra-window, kemungkinan di gap 131842908-131849105); free-quota views tidak diketahui; gate website/X BELUM dicek. Early lead TIDAK PERNAH di-preview/mint."),
    "0x5ABe8974d554Ea0c797fBC4c6B01EA4446616B2f": ("Toucan Play", "TCAN", "watchlist-only-paid-only-2026-11-05",
        "5 mint/5 minter; triase A: price() = 0,0002 BNB terverifikasi (wave paid 0,0002 BNB). PAID-ONLY."),
    "0x78eDD42101e889cC3Ce4B24CBb0Fc774082BcAee": ("BEWORK", "BEWORK", "watchlist-only-shape-unverified-2026-11-05",
        "2 mint/1 minter, mint tx value 0 BNB TETAPI tanpa bukti agent-shape (no registry bytes, Sourcify 404, fungsi mint tak teridentifikasi). Bukan agent-shaped -> BUKAN early lead."),
    "0xA224bb6B4B89D9c22C140Ea8d37D2290E99AECAc": ("Synthetic Ghost", "SGHT", "watchlist-only-paid-only-2026-11-05",
        "1 mint; Sourcify VERIFIED template agent-mint (AGENT_REGISTRY() = registry on-chain, MAX_SUPPLY, PRICE, quote, spotsLeft, mint, registerForRewards); PRICE() = quote(1) = 0,0005 BNB; MAX_SUPPLY 3333, spotsLeft 3332, totalMinted 1; tanpa fungsi free. PAID-ONLY (factory sniper-test, minter/ownerOf(1) = 0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5)."),
    "0x2Fb4598Cc4c0758d9a541CAe813E81f0b138024A": ("Not Financial Advice39", "NFA39", "watchlist-only-paid-only-2026-11-05",
        "1 mint; triase A: mint tx value 0,001 BNB terverifikasi (minter sama dengan Cope Harder). PAID-ONLY."),
    "0x282885b50ee2B8e539d695f859A87B1A18F2B66e": ("Delta Yeti Agent", "DELY", "watchlist-only-paid-only-2026-11-05",
        "1 mint; Sourcify VERIFIED template agent-mint; AGENT_REGISTRY() = registry; PRICE() = quote(1) = 0,0005 BNB; MAX_SUPPLY 3333, spotsLeft 3332, totalMinted 1; tanpa fungsi free. PAID-ONLY (ownerOf(1) = 0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5)."),
    "0x4D0e44744baF36Ad27f736BA023bdFbB0B9823Eb": ("Void Quokka Agent", "VOIQ", "watchlist-only-paid-only-2026-11-05",
        "1 mint; Sourcify VERIFIED template agent-mint; AGENT_REGISTRY() = registry; PRICE() = quote(1) = 0,0005 BNB; MAX_SUPPLY 3333, spotsLeft 3332, totalMinted 1; tanpa fungsi free. PAID-ONLY (ownerOf(1) = 0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5)."),
    "0xD9A49dF66443bA35e7A96bEE63b0B8913F47c22c": ("Cope Harder39", "COPE39", "watchlist-only-paid-only-2026-11-05",
        "1 mint; triase A: mint tx value 0,001 BNB terverifikasi (minter sama dengan NFA39). PAID-ONLY."),
    "0x759a2c237ee454004aA1029622483954a248c320": ("SENSHI", "SENSHI", "watchlist-only-paid-only-2026-11-05",
        "1 mint; triase A: mint tx value ~0,0007 BNB terverifikasi. PAID-ONLY."),
    "0x807E86F6d1bc8fc5E8f53052DAC5d379D4efc120": ("jelly.exe", "JELLY", "watchlist-only-paid-only-2026-11-05",
        "1 mint; triase A + parent: price() = 0,0002 BNB terverifikasi, mintOpen 1, totalSupply 19. PAID-ONLY (wave 0,0002 BNB)."),
}
for e in firstseen.get("first_seen", []):
    addr = e["address"]
    name, sym, status, note = FS_CLASS.get(addr, (e.get("name"), e.get("symbol"),
        "watchlist-only-2026-11-05", "First-seen run 2331, belum diklasifikasi."))
    key = name or addr[:10]
    if key not in contracts:
        contracts[key] = {
            "address": addr, "name": name, "symbol": sym, "kind": e.get("kind"),
            "status": status,
            "totalSupply": None,
            "firstSeenBlock": e.get("first_block"),
            "scanMints": e.get("mint_count"), "scanMinters": e.get("distinct_minters"),
            "lastReadBlock": scan.get("to_block"),
            "lastReadWib": "2026-11-06 run 2331",
            "xVerified": False, "velocityVerified": False,
            "launchNote": "First-seen run 2331 via scan rute 4; umur peluncuran UNVERIFIED.",
            "baselineNote": f"Run 2331 scan first-seen (jendela {scan.get('from_block')}-{scan.get('to_block')}): {note}",
            "supplyView": "totalSupply",
        }

# Moonfall totals (baca Subagent A)
mf = contracts.get("Moonfall")
if mf is not None:
    mf["totalSupply"] = 26
    mf["MAX_SUPPLY"] = 1001

# ---------- 11. Scan state + seen + 5c-checked ----------
# SUDAH dikerjakan Subagent A sebelum merge ini: scan-state watermark -> 131851105
# (ankr_calls 85, gap 131842908-131849105 dicatat), seen nested contracts 9250 -> 9260,
# track-c-scan-checked nested 1894 -> 1900. Merge ini TIDAK menulis ulang state/checked
# (hindari last-writer-wins); hanya menambah ERC-20 first-seen yang belum ada di seen.
state = load("onchain-scan-state.json")
assert state["last_scanned_block"] == scan.get("to_block"), "watermark A != scan to_block"
assert state["last_scan_window_from"] == scan.get("from_block")
print("scan-state OK (A): watermark", state["last_scanned_block"], "ankr_calls", state["ankr_calls"])

seen = load("onchain-scan-seen.json")
seen_contracts = seen.get("contracts", {}) if isinstance(seen, dict) else {}
for e in firstseen.get("first_seen", []):
    seen_contracts[e["address"].lower()] = {"first_seen_block": e.get("first_block"), "run": "2331"}
n_erc20_added = 0
for c in scan.get("erc20_mint_contracts_list", []):
    a = (c.get("address") or "").lower()
    if a and a not in seen_contracts:
        seen_contracts[a] = {"first_seen_block": scan.get("to_block"), "run": "2331", "kind": "erc20"}
        n_erc20_added += 1
if isinstance(seen, dict):
    seen["contracts"] = seen_contracts
    with open(f"{BASE}/onchain-scan-seen.json", "w") as f:
        json.dump(seen, f, indent=1)
print("seen: +erc20", n_erc20_added, "| total contracts keys:", len(seen_contracts))

checked = load("track-c-scan-checked.json")
print("track-c-scan-checked nested (A):", len(checked.get("checked", {})),
      "| 5c run ini (file A): semua 6 = Sourcify 404, 0 lolos S1/S2")

# ---------- 12. Run notes ----------
snap["last_run"] = "2026-11-05-2331"
snap["last_run_wib"] = "2026-11-06 run 2331"
snap["runNote2331"] = (
    "Run 2331 (2026-11-05 23:31 WIB, eksekusi 23:43-00:15 WIB): 0 kandidat baru, 0 strong lead "
    "BARU yang bisa di-mint, 0 early lead baru, 0 track-C lead/kandidat baru, 0 pending claim "
    "baru/dibuka. PERUBAHAN: (1) Jolly AGE-EXCLUDED + DIHAPUS (first mint 2026-11-03 23:27:33 WIB, "
    "48 jam berakhir 23:27:33 WIB 2026-11-05; freeMinted segar 3565/5000 belum sold out) - dilaporkan "
    "sekali. (2) BNB CACHE Server PROMOSI ke strong lead (free 250/777 = 32,2%, umur terverifikasi "
    "<=48 jam, slot terbuka) tetapi GATE website-only GAGAL (metode A-N; (L) BscScan: "
    f"{bscscan.get('note', 'tidak ada website/social tercatat')}) - TIDAK di-mint, dilaporkan sekali "
    "sebagai strong lead + alasan gate-blocked. (3) Mossminds promosi DISCARDED aturan same-owner "
    "(owner 0x4e9b... sama dengan 6 kontrak wave) + gate gagal - tidak dilaporkan sebagai lead. "
    "(4) Binance Agent kemungkinan sold out (totalMinted 123 = FREE_SUPPLY) tetapi freeMinted gagal "
    "dibaca ulang - tetap early lead, konfirmasi tertunda. (5) Snail Mail konfirmasi paid-only gagal "
    "dibaca ulang - tetap early, retry run berikut. (6) Zero Shark (Boltbook) AGE-EXCLUDED (>48 jam). "
    "(7) Scan: 10 first-seen, 1 EARLY LEAD baru (Moonfall, dilaporkan sekali), 9 NOT-EARLY "
    "(8 paid-only + 1 shape-unverified). (8) 5c: 6 alamat baru, "
    "0 lolos S1/S2 (semua Sourcify 404 setelah retry Subagent A; checked file 1894->1900). (9) Sourcify feed 20 kontrak, "
    "0 lolos S1/S2. (10) Boltbook: Moon Cat alamat tanpa kode (ditolak), MORPHA bentuk unverified "
    "(tx klaim tidak ditemukan). (11) Track-B BINANCEAI tetap refund/failed. (12) Bridge tidak "
    "berubah (113 kontrak). RPC SANGAT terdegradasi run ini: block() None, banyak view None "
    "(None = gagal baca, bukan nol); Ankr eth_call tidak didukung (-32601). 0 eksekusi (0 preview, "
    "0 mint, 0 approve, 0 swap).")
snap["runNote2331_scan"] = (
    "Run 2331 scan (rute 4): window 131849106-131851105 (cap 2000 blok), gap 131842908-131849105 "
    "dilewati (6198 blok; kumulatif sejak run 1831 ~33.461 blok), head 131851105, 80 Ankr calls, "
    "0 errors, 279 NFT + 520 ERC-20 di jendela. True first-seen 10 (1 early lead Moonfall; 8 paid-only; 1 shape-unverified). Watermark -> "
    "131851105. 5c (Subagent A): 57 ERC-20 mint_count>=10, 6 benar-benar baru, 0 lolos S1/S2 (semua "
    "Sourcify 404); remainder dropped 0 (51 sudah tercakup checked file). Sourcify feed 20 kontrak (verifiedAt s.d. 16:45Z), "
    "0 lolos S1/S2.")

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE: contracts =", len(contracts), "| track_c =", len(track_c))
print("Jolly in snapshot:", "Jolly" in contracts)
print("Mossminds status:", contracts.get("Mossminds", {}).get("status"))
print("BNB CACHE status:", contracts.get("BNB CACHE Server", {}).get("status"))
print("watermark:", state["last_scanned_block"])
