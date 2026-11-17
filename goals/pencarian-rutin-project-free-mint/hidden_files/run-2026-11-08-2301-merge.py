#!/usr/bin/env python3
"""Parent merge run 2301 — applies Subagent A+B + parent triage to snapshot.
Writes backup onchain-snapshot.json.bak-2301-premerge first. No execution.
Also: backup + append 8 new 5c addresses to track-c-scan-checked.json;
append run note to onchain-scan-state.json (watermark NOT advanced)."""
import json, sys, time, shutil
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _post as fr_post
import ankr as ankr_mod
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
NOW_WIB = "2026-11-08 23:50 WIB"

def block_ts(num):
    for ep in EPS:
        try:
            r = fr_post(ep, [{"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(num), False]}], timeout=25)
            return int(r[0]["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

def wib(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S WIB", time.localtime(ts + 7 * 3600)) if ts else None

def probe_first_mint(addr, chunks):
    """Return earliest from-zero Transfer block found in given [from,to] chunks."""
    earliest = None
    for frm, to in chunks:
        try:
            resp = ankr_mod.get_logs(addr, frm, to, topics=[TRANSFER])
            res = resp.get("result", resp) if isinstance(resp, dict) else resp
            logs = res.get("logs", []) if isinstance(res, dict) else []
            for lg in logs:
                topics = lg.get("topics", [])
                if len(topics) >= 2 and topics[1].lower() == ("0x" + "0" * 64):
                    b = int(lg.get("blockNumber", "0x0"), 16)
                    if earliest is None or b < earliest:
                        earliest = b
        except Exception as e:
            print(f"probe chunk {frm}-{to} error: {str(e)[:120]}", flush=True)
    return earliest

# --- narrow first-mint bounds (cheap Ankr probes) ---
print("Probing DRAGON first-mint gap (132416000-132420336] ...", flush=True)
d_first = probe_first_mint("0x7F00b3Aa3A3e41dc145180C4ED8a24eE568eaED4",
                           [(132419000, 132419999), (132418000, 132418999),
                            (132417000, 132417999), (132416000, 132416999)])
print("DRAGON earliest in gap probes:", d_first, wib(block_ts(d_first)) if d_first else None, flush=True)
print("Probing HOURGLASS first-mint (deploy ~23:01:48 WIB) ...", flush=True)
h_first = probe_first_mint("0xD743c793b23D1adE2099892B010d4F4530d44E0a",
                           [(132421000, 132421999), (132422000, 132422999),
                            (132423000, 132423999), (132424000, 132424999)])
print("HOURGLASS earliest in probes:", h_first, wib(block_ts(h_first)) if h_first else None, flush=True)

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2301-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = s["contracts"]
TC = s.get("track_c", {})

HEAD_REREAD = 132423557
LAST_READ_WIB = "2026-11-08 23:35 WIB"

def upd(name, note, **kw):
    e = C.get(name)
    if e is None:
        print(f"WARN {name} NOT IN SNAPSHOT, skipped")
        return
    e.update(kw)
    e["runNote2301_1108"] = note
    e["lastReadBlock"] = HEAD_REREAD
    e["lastReadWib"] = LAST_READ_WIB

# --- A focus changes ---
upd("Pokechain",
    "Run 2301: totalMinted 7761->11359 (+3598, 73.0% of MAX 15555); balanceOf(user)=1 (mint #5381 already reported 2201). Gate RE-TERVERIFIKASI run ini (B: /js/app.js HTTP 200, MINT_CA persis). Bukan kandidat baru.",
    totalMinted=11359, balanceOf_user=1, userBalance=1)
upd("GLOOP",
    "Run 2301: totalMinted 2234->2563 (+329); balanceOf(user)=1 (mint #2021 hot leg, sudah dilaporkan). Gate tetap terverifikasi (B: gloopagent.xyz HTTP 200).",
    totalMinted=2563, balanceOf_user=1, userBalance=1)
upd("HELIX",
    "Run 2301: totalMinted 290->392 (+102); gate tetap GAGAL (B: name search hanya panduan generik, tidak ada situs HELIX BSC).",
    totalMinted=392)
upd("BAHUANG2",
    "Run 2301: freeMinted 1040->1086/3000 = 36.2%; slot user OPEN; gate tetap GAGAL (B: raw-address search nol hit; contractURI/tokenURI revert). Tetap strong-lead gate-blocked.",
    freeMinted=1086)
upd("NUMBI",
    "Run 2301: freeMinted 81->93/3000 = 3.1%; early lead (backfill 21:16), tidak ada info baru.",
    freeMinted=93)
upd("DRONEGENT",
    "Run 2301 (B, Boltbook): free lane HABIS 5.555/5.555 (totalSupply = FREE_SUPPLY); sudah promotion-discarded-same-owner, tidak dilaporkan sebagai sellout lead.",
    totalSupply=5555)

# --- track_c changes ---
def tc_upd(name, note, **kw):
    e = TC.get(name)
    if e is None:
        print(f"WARN track_c {name} NOT IN SNAPSHOT, skipped")
        return
    e.update(kw)
    e["runNote2301_1108"] = note

tc_upd("NUSA",
    "Run 2301: freeMinted 220->236/560; tradingOpen()=0 (false) DIKONFIRMASI ULANG run ini (B, eth_call) — token NUSA masih TERKUNCI; gate website tetap GAGAL.",
    freeMinted=236)
tc_upd("DROID", "Run 2301: freeMinted 733->734; tetap watchlist-only-not-open.", freeMinted=734)
tc_upd("FUGUI-set1-991", "Run 2301: freeMinted 403->420; tetap watchlist-only-gate-blocked.", freeMinted=420)
tc_upd("Crack", "Run 2301: totalSupply 3811->3866; minted-by-user.", totalSupply=3866)
tc_upd("FABE", "Run 2301: freeSharesRemaining 2821/3333 tidak berubah; 1 share HELD.", freeSharesRemaining=2821)
tc_upd("AGENT MALTA", "Run 2301: totalSupply token bergerak; freeMinted None run ini (nilai lama dipertahankan).")
if "FUGUI-set2" in TC:
    TC["FUGUI-set2"]["runNote2301_1108"] = ("Run 2301 (B, Boltbook): sale FINALIZED (finalized()=true) — 631/6.666, free 626 + paid 5; "
        "pair PCS masih 0, yang sudah klaim belum bisa jual. Tetap watchlist-only-gate-blocked.")
if "Pacture" in TC:
    TC["Pacture"]["runNote2301_1108"] = ("Run 2301 (B, Boltbook): free lane PENUH 7.700/7.700, sharesMinted flat 9.978. "
        "Tetap watchlist-only-slot-used-2026-11-05.")

# --- BNBFly age-exclusion: remove from active watchlist, preserve in excluded ---
bnbfly = C.pop("BNBFLY Agent Pass", None)
if bnbfly is not None:
    s.setdefault("excluded", {})["BNBFLY Agent Pass"] = {
        "address": "0x7fe03C055588bd5018825175D791103c5CBEd8be",
        "symbol": "BFLY-PASS",
        "track": "A",
        "status": "age-excluded-2026-11-08",
        "note": ("Dihapus dari watchlist aktif run 2301 per aturan umur 48 jam: CLAIM_START on-chain 2026-11-06 21:27:09 WIB, "
            "first mint blok 132024991 = 2026-11-06 21:30:09 WIB; umur ~50,4 jam pada 23:50 WIB 2026-11-08 (>48 jam), "
            "totalSupply 49->50, belum sold out. Early lead sudah dilaporkan sekali 2026-11-06; penghapusan ini dilaporkan sekali run 2301. "
            "Catatan: slot user memang tidak terbuka (claim() butuh saldo >= MIN_BALANCE 0,044 BNB; wallet 0,001048 BNB)."),
        "checked_wib": NOW_WIB,
    }
    print("BNBFLY removed from contracts -> excluded (age-excluded).")
else:
    print("WARN BNBFly not in contracts (already removed?)")

# --- Hexrotta: never reported, age-excluded + same-owner -> excluded record only ---
s.setdefault("excluded", {})["Hexrotta"] = {
    "address": "0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9",
    "symbol": "HEXRTA",
    "track": "A",
    "status": "age-excluded-same-owner-2026-11-08",
    "note": ("Ditemukan Boltbook run 2301 (~23:21 WIB) + triase parent: totalSupply 623, freeClaimed 610/896 = 68,1%, mintOpen=true, "
        "quote(user,1)=0, freeUsed(user)=0, freeLeft(user)=1 (slot user TERBUKA), AGENT_ID()=registry persis — TAPI first mint "
        "blok 131197748 = 2026-11-02 14:04:15 WIB (Ankr getLogs, 3 mint from-zero di chunk itu; juga tercatat di scan 2026-11-02 1301/1401) "
        "-> umur ~6 hari >48 jam = AGE-EXCLUDED; DAN owner() 0xd76d5918fb337667b22fe37ae2055b5542cf8dc9 ADA di same-owner-discards.json "
        "(grup factory Cryptlichor). TIDAK PERNAH dilaporkan sebagai lead; tidak di-preview/di-mint."),
    "checked_wib": NOW_WIB,
}

# --- HOURGLASS: free pool exhausted 50/50 -> excluded record only ---
s.setdefault("excluded", {})["HOURGLASS"] = {
    "address": "0xD743c793b23D1adE2099892B010d4F4530d44E0a",
    "symbol": "HOUR",
    "track": "A",
    "status": "excluded-free-pool-exhausted-2026-11-08",
    "note": ("Ditemukan feed Sourcify run 2301 (verifiedAt 16:04:45Z) + triase parent: deployTime on-chain 1794153708 = 2026-11-08 23:01:48 WIB, "
        "free window 1 jam (FREE_WINDOW 3600, freeWindowEnd 2026-11-09 00:01:48 WIB), totalSupply 50, freeMintedTotal 50 = FREE_CAP 50 "
        "-> free pool 50/50 HABIS sebelum sempat dilaporkan; paid price ~0,00717 BNB. agentRegistry()=registry persis. "
        "First mint tidak terverifikasi penuh (probe Ankr 132421000-132424999: "
        f"{'ditemukan blok ' + str(h_first) + ' (' + (wib(block_ts(h_first)) or '?') + ')' if h_first else 'tidak ditemukan di chunk probe — mints tanpa event Transfer teramati atau di luar chunk'}). "
        "Website UNVERIFIED (contractURI tanpa external_link). TIDAK PERNAH dilaporkan sebagai lead."),
    "checked_wib": NOW_WIB,
}

# --- DRAGON: user already holds #91 (mint 23:16:47 WIB, executor unattributed) ---
d_first_wib = wib(block_ts(d_first)) if d_first else None
C["DRAGON"] = {
    "address": "0x7F00b3Aa3A3e41dc145180C4ED8a24eE568eaED4",
    "name": "DRAGON",
    "symbol": "DRAGON",
    "kind": "ERC721",
    "status": "minted-by-user-2026-11-08",
    "totalSupply": None,
    "totalSupplyNote": "totalSupply() reverts on-chain (view tidak tersedia); freeMinted dipakai sebagai ukuran pool.",
    "freeMinted": 141,
    "FREE_CAP": 222,
    "freePctVerified": 63.5,
    "mintOpen": True,
    "FREE_PER_WALLET": 1,
    "PRICE": 70000000000000,
    "userBalance": 1,
    "balanceOf_user": 1,
    "userSlotNote": "Slot user TERPAKAI: balanceOf(user)=1, FREE_PER_WALLET=1 — tidak ada free mint kedua.",
    "mintTx": "0x93fe1af689d8b1e5bd63586df60c6f49a1a497023bbfa1fc9f8a19894e642a64",
    "mintBlock": 132423043,
    "mintGas": 150090,
    "mintTokenId": 91,
    "mintWib": "2026-11-08 23:16:47 WIB",
    "mintValue": 0,
    "mintReceiptStatus": 1,
    "mintSelector": "0x7c928fe9",
    "firstMintBlock": d_first if d_first else 132420336,
    "firstMintWib": d_first_wib or "2026-11-08 22:56:28 WIB",
    "launchNote": ("First mint terverifikasi on-chain di antara blok 132416000-132420336 (probe Ankr: 0 mint di chunk 132415000-132415999, "
        "7 mint from-zero di chunk 132420000-132420999, pertama blok 132420336 = 2026-11-08 22:56:28 WIB); umur ~1 jam saat mint user, <=48 jam."),
    "gateNote": ("Website UNVERIFIED (tanpa contractURI/website() di ABI; pencarian nama + DappBay nol hit). Mint ini BUKAN oleh run 2301 "
        "dan BUKAN oleh hot leg (hot-leg-reported.json terakhir ditulis 22:07 WIB, tanpa entri 0x7F00.../tx ini) — eksekutor tidak "
        "teridentifikasi dari file job ini (kemungkinan order user di chat utama / sesi agent lain). Dilaporkan sekali run 2301 sebagai "
        "mint yang belum dilaporkan; TIDAK di-mint ulang (slot terpakai)."),
    "agentShaped": True,
    "agentShapeNote": "agentIdRegistry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis; owner() 0x13333df46ab3e95f4166370d571e7b73aad06370 tidak ada di same-owner-discards.json.",
    "sourcify": "exact_match verifiedAt 2026-11-08T15:56:08Z",
    "lastReadBlock": HEAD_REREAD,
    "lastReadWib": LAST_READ_WIB,
    "runNote2301_1108": ("Run 2301: DRAGON ditemukan feed Sourcify (S1) + triase parent. User SUDAH pegang #91 — mint 23:16:47 WIB, tx "
        "0x93fe1af6..., blok 132423043, value 0, receipt status 1, gas 150090; eksekutor tidak tercatat di file job ini. "
        "freeMinted 132->141/222 (63,5%) dalam ~7 menit; slot user terpakai (FREE_PER_WALLET=1). Dilaporkan sekali run ini."),
}

# --- OUPE excluded note: re-verified sold out ---
if "OUPE Cards" in s.get("excluded", {}):
    s["excluded"]["OUPE Cards"]["note"] += (" Verifikasi ulang run 2301 (B, ~23:36 WIB): freeClaimed 777/777 TETAP HABIS; "
        "Boltbook post #15: claimFree() revert FreeGone.")

# --- refresh lastRead for all other contracts ---
for name, e in C.items():
    if "runNote2301_1108" not in e:
        e["lastReadBlock"] = HEAD_REREAD
        e["lastReadWib"] = LAST_READ_WIB

s["timestamp_wib"] = LAST_READ_WIB
s["last_run_wib"] = "2026-11-08 23:01 WIB"
s["last_run_note"] = ("Run 2301: 0 kandidat, 0 strong lead baru, 0 early lead BARU. Mint baru: DRAGON #91 (agent wallet, 23:16:47 WIB, "
    "eksekutor tidak tercatat di file job — dilaporkan sekali run ini). Age-exclusion: BNBFLY Agent Pass dihapus dari watchlist "
    "(~50,4 jam; dilaporkan sekali). Triase baru ditutup tanpa lead: Hexrotta (first mint 2026-11-02, umur ~6 hari + same-owner discard), "
    "HOURGLASS (free 50/50 habis). Scan PARTIAL (enrichment mati 30/155, 126 NFT tidak tertriase). Binanceai tetap refund phase. Bridge: 0 baru.")
s["runNote2301_1108"] = ("Run 2301 (23:01-23:5x WIB): re-read blok 132423557 (542 kontrak + 72 track_c, 0 batch_fail, 40 degraded — naik dari 26 di 2201); "
    "scan window 132422545-132423544 PARTIAL (pre-flight OK 11,9 dtk; 40 Ankr calls, 0 error; enrichment killed 700s timeout di 30/155, "
    "partial=true, 29 NFT + 282 ERC-20; 126 NFT di window TIDAK tertriase — coverage gap, bukan bukti kosong). Watermark TIDAK dimajukan "
    "run ini (milik backfill; backfill memajukan ke 132422005 selama run; skipped gap 132422006-132422544). 5c: 8 baru dicek, 0 hit S1/S2. "
    "Velocity strict: 11 lolos, 0 promosi. Track_c re-read: NUSA 220->236 (tradingOpen=0 re-konfirmasi), DROID 733->734, FUGUI-set1-991 403->420, "
    "Crack 3811->3866. Bridge 116 kontrak, 0 baru, 7 same-owner-discarded. BMT: koreksi 2201 — free lane via agentMint() hidup (947/1.000) "
    "tapi AGE-EXCLUDED ~167 jam, bukan kandidat. DRONEGENT free lane habis 5.555/5.555. FUGUI sale FINALIZED. PACTURE free penuh 7.700/7.700.")
s["runNote2301_1108_scan"] = ("Scan run 2301 PARTIAL: pre-flight OK 11,9 dtk (head 132423518, 359 logs/50 blok). Window 132422545-132423544 (1000 blok, cap), "
    "log collection lengkap 20/20 chunk, 40 Ankr calls, 0 error; enrichment terhenti di 30/155 oleh timeout 700 dtk (SCAN_EXIT=124). "
    "Partial JSON terselamatkan: 29 NFT + 282 ERC-20-mint. First-seen di antara 29 yang ter-enrich: 0. 126 NFT window tidak tertriase "
    "(alamat tidak tercatat di log) — gap cakupan. Watermark tidak dimajukan.")
s["runNote2301_1108_binanceai"] = ("Run 2301: binanceai tetap refund phase (launched=0, failed=1, isRefundPhase=1, totalShares 3.110, "
    "tokenClaimed(user)=0, saldo TOKEN user 0); tanpa perubahan, sudah dilaporkan sekali.")
s["runNote2301_1108_web"] = ("Run 2301 web: Boltbook EN+ZH 1 proyek baru (Hexrotta — ditutup triase: umur ~6 hari + same-owner); sweep 0 situs proyek baru "
    "yang kandidat (AlphaPulse BERBAYAR 1 USDT/share -> excluded). Route 6: 0 temuan. Sourcify feed 20 item: 2 SALE-S1 baru (HOURGLASS — free "
    "50/50 habis; DRAGON — user sudah pegang #91) + Hexrotta S1; 5 UNKNOWN run 2201 semua terjawab NOT-AGENT-SHAPED; Wisp Sourcify masih 404 "
    "(ke-5). Gap sampling feed: verifiedAt 15:09:07-15:44:58Z tidak pernah di-poll (limit-20). Gate: BAHUANG2/HELIX/Pressure/Kitebots/Lambdwyn/"
    "NUSA/Wisp tetap gagal/belum terverifikasi; Pokechain RE-TERVERIFIKASI (/js/app.js 200, MINT_CA persis); TRACE + GLOOP tetap hidup.")
s["runNote2301_1108_triage_new"] = ("Triase parent 3 kontrak S1 baru: Hexrotta 0x25256e... (totalSupply 623, free 610/896=68,1%, slot user TERBUKA, AGENT_ID=registry; "
    "first mint blok 131197748 = 2026-11-02 14:04:15 WIB -> umur ~6 hari AGE-EXCLUDED; owner 0xd76d... ADA di same-owner-discards.json -> "
    "double-disqualifier, TIDAK dilaporkan sebagai lead); HOURGLASS 0xD743... (deploy 2026-11-08 23:01:48 WIB, free window 1 jam s.d. 00:01:48 WIB, "
    "freeMintedTotal 50 = FREE_CAP 50 -> free HABIS; agentRegistry=registry); DRAGON 0x7F00... (freeMinted 132->141/222=63,5%, mintOpen, "
    "FREE_PER_WALLET=1, agentIdRegistry=registry; first mint 22:56 WIB; user pegang #91 via mint 23:16:47 WIB tx 0x93fe1af6... value 0 status 1).")

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(s, f, indent=1, ensure_ascii=False)
print("SNAPSHOT UPDATED: contracts", len(C), "| track_c", len(TC), "| excluded", len(s.get("excluded", {})))
print("BNBFLY in contracts:", "BNBFLY Agent Pass" in C, "| DRAGON in contracts:", "DRAGON" in C,
      "| Hexrotta excluded:", "Hexrotta" in s.get("excluded", {}), "| HOURGLASS excluded:", "HOURGLASS" in s.get("excluded", {}))

# --- 5c checked file: backup + append 8 new addresses as top-level keys ---
tc5 = json.load(open(f"{BASE}/track-c-scan-checked.json"))
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-2301-premerge")
new5c = ["0x1347a165A8E630daff88c73Cc4A8187615b22160", "0x9A7392EFcd711e485e13968e63bb9e134959CdD7",
         "0xCed29AD5026e2a5B807c7061f310E0a1B3C8fc89", "0xf75cf7f9Be878cf487d5aEAcd5560d96737b63f8",
         "0x281915f736010De0e786B847eC5C2a2160FD8eA7", "0x15DFC17c5e39e0968eD498f5fC93A91348F78A4e",
         "0x28b653e43bC32aD068146c8c91A4A8edD6f76023", "0x64920E7f4f270f302e8b728f69B5a9Fc24Fda2D3"]
checked = tc5.get("checked", {}) if isinstance(tc5, dict) else {}
already = 0
for a in new5c:
    if a in tc5 or a.lower() in {k.lower() for k in checked}:
        already += 1
    tc5[a] = {"checked_wib": NOW_WIB, "run": "2301-5c", "shape": "not-sale-shape"}
with open(f"{BASE}/track-c-scan-checked.json", "w") as f:
    json.dump(tc5, f, indent=1)
print(f"track-c-scan-checked: +{len(new5c) - already} baru ({already} sudah ada), total top-level keys now:",
      sum(1 for k in tc5 if isinstance(k, str) and k.startswith("0x")))

# --- scan-state note (watermark NOT advanced by this run) ---
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["runNote2301_1108_scan"] = s["runNote2301_1108_scan"]
st["runNote2301_1108"] = ("Run 2301: watermark TIDAK dimajukan run ini (milik backfill; backfill memajukan ke 132422005 selama run). "
    "Skipped gap 132422006-132422544 (539 blok) + 126 NFT window tidak tertriase (scan partial).")
with open(f"{BASE}/onchain-scan-state.json", "w") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
print("SCAN-STATE noted (watermark untouched by this run):", st.get("last_scanned_block"))

# --- add DRAGON + HOURGLASS first-seen blocks to seen file (Hexrotta already there) ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = seen.setdefault("contracts", {})
added = []
if "0x7f00b3aa3a3e41dc145180c4ed8a24ee568eaed4" not in sc:
    sc["0x7f00b3aa3a3e41dc145180c4ed8a24ee568eaed4"] = d_first if d_first else 132420336
    added.append("DRAGON")
if h_first and "0xd743c793b23d1ade2099892b010d4f4530d44e0a" not in sc:
    sc["0xd743c793b23d1ade2099892b010d4f4530d44e0a"] = h_first
    added.append("HOURGLASS")
with open(f"{BASE}/onchain-scan-seen.json", "w") as f:
    json.dump(seen, f, indent=1)
print("seen file: added", added, "| Hexrotta already present:", "0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9" in sc)
print("MERGE 2301 DONE")
