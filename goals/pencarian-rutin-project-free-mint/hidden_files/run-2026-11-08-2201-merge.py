#!/usr/bin/env python3
"""Parent merge run 2026-11-08 2201 — applies Subagent A+B findings to snapshot.
Writes backup onchain-snapshot.json.bak-2201-premerge first. No execution."""
import json, sys, time, shutil
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-2201"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]

# block timestamp for lastReadBlock 132416224
ts = None
for ep in EPS:
    try:
        r = _fr_post(ep, [{"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                           "params": [hex(132416224), False]}], timeout=30)
        ts = int(r[0]["result"]["timestamp"], 16)
        break
    except Exception:
        continue
last_read_wib = time.strftime("%Y-%m-%d %H:%M WIB", time.localtime(ts + 7*3600)) if ts else "2026-11-08 22:52 WIB"
print("lastReadBlock 132416224 =", last_read_wib, flush=True)

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2201-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = s["contracts"]

def upd(name, note, **kw):
    e = C.get(name)
    if e is None:
        print(f"WARN {name} NOT IN SNAPSHOT, skipped")
        return
    e.update(kw)
    e["runNote2201_1108"] = note
    e["lastReadBlock"] = 132416224
    e["lastReadWib"] = last_read_wib

upd("402",
    "Run 2201: FREE POOL HABIS 402/402 (FREE_CAP 402) — freeMinted 394->402 interval ini; user pegang 1. Status diubah minted-by-user -> sold-out-free-2026-11-08. SUDAH dilaporkan hot leg 21:39 WIB (blok 132410960); run ini hanya memperbarui status snapshot, TIDAK lapor ulang.",
    status="sold-out-free-2026-11-08", totalMinted=402, freeMinted=402)
upd("Pokechain",
    "Run 2201: totalMinted 1067->7761 (+6694, same-view, riil); balanceOf(user) 0->1: MINT #5381 dari agent wallet (baw) 2026-11-08 22:11:38 WIB, tx 0x8406b7ae5ac8c2f2e73e3338a2ec17b7b2976b39cbbf0d5d5655a7b0373982e7, blok 132414362, status 1, gas 147455, value 0, selector 0xa0712d68. BUKAN oleh run 2201 (read-only). EKSEKUTOR TERIDENTIFIKASI: order user-named di chat utama 22:04 WIB (link pokechain.trade), dieksekusi subagent mint Pokechain via baw — mint SUDAH dilaporkan ke user; run ini hanya mencatat di snapshot, TIDAK lapor ulang. Listing pasca-mint GAGAL (preview approval 351803, dilaporkan 22:29 WIB); #5381 tetap di wallet, tidak ter-listing.",
    totalMinted=7761, balanceOf_user=1, userBalance=1,
    mintTx="0x8406b7ae5ac8c2f2e73e3338a2ec17b7b2976b39cbbf0d5d5655a7b0373982e7",
    mintBlock=132414362, mintTokenId=5381, mintGas=147455)
upd("GLOOP",
    "Run 2201: totalMinted 1828->2234 (+406); balanceOf(user) 0->1: MINT #2021 oleh HOT LEG 22:05 WIB via strong-lead direct mint (sudah dilaporkan hot leg; hot-leg-reported.json minted-strong-lead-track-a), tx 0x1b397de65c3a8e667548b29fed682d5dd4f43dde4c84638729d96c3b2ba28f8e, blok 132413324 (22:03:51 WIB), status 1, gas 139745, PoW nonce 17535435, audit hasResult=false, preview bersih, hasMinted true. Market own GloopMarket live; LISTING BERHASIL 22:34 WIB di 0,001 BNB per order user 22:29 WIB (tx list 0x63f3e6e5411a960a7b1c78e80c46f7e5580e25eb31ade4e811d7d35fa2c8ec9b, blok 132417335, listing aktif terverifikasi, listedCount 113->114). Tier: JSON Epic vs on-chain Rare (konflik metadata).",
    totalMinted=2234, balanceOf_user=1, userBalance=1,
    mintTx="0x1b397de65c3a8e667548b29fed682d5dd4f43dde4c84638729d96c3b2ba28f8e",
    mintBlock=132413324, mintTokenId=2021, mintGas=139745)
upd("BAHUANG2",
    "Run 2201: freeMinted 1030->1040/3000 = 34,67%, totalMinted 1033->1044, slot user tetap OPEN, gate website tetap GAGAL (re-check B run 2201, metode A) -> tidak mint.",
    freeMinted=1040, totalMinted=1044, balanceOf_user=0)
upd("NUMBI",
    "Run 2201: freeMinted 64->81 (FREE_POOL 3000 = 2,7%), totalSupply 64->81; tetap early lead, tanpa promosi (free% <25%). Sudah dilaporkan sebagai EARLY LEAD oleh backfill 21:16 WIB.",
    freeMinted=81, totalSupply=81, balanceOf_user=0)
upd("HELIX",
    "Run 2201: totalSupply 290->357 (+67); velocity GAGAL lagi (0,69x); free% UNVERIFIED; gate website tetap GAGAL (B: HELI Solana / Injective Helix = same-name). Tetap early lead.",
    totalSupply=357)
upd("Ink Koi",
    "Run 2201: freeMinted 2038->2042/2777 = 73,5% tapi slot user TERTUTUP (balance 1); tanpa promosi.",
    freeMinted=2042, balanceOf_user=1)
upd("NEKART",
    "Run 2201: freeMinted 821->824, totalSupply 822->825 (+3); free% UNVERIFIED (tanpa cap); tetap early lead.",
    freeMinted=824, totalSupply=825)
upd("MONOLITH",
    "Run 2201: totalSupply 138->140 (+2); tetap early lead.",
    totalSupply=140)
upd("HIVE Agents",
    "Run 2201: totalSupply tetap 1256, balanceOf(user)=1; minted-by-user, tanpa perubahan.",
    totalSupply=1256, balanceOf_user=1)
upd("Agentic Bull",
    "Run 2201 KOREKSI: totalMinted 850->850 (0 perubahan); angka +527 di analysis v1 adalah artefak campur view (snapshot totalSupply 323 vs totalMinted baru 850). freeMinted reads 835; snapshot freeClaimed 316 adalah view berbeda, jangan dibandingkan.",
    totalMinted=850)
upd("Jinchan",
    "Run 2201: totalMinted 838, tidak berubah; sudah sold-out-free.",
    totalMinted=838)
upd("Oddlode Drills",
    "Run 2201: freeMinted 1000/1000, tidak berubah; sudah sold-out-free.",
    freeMinted=1000)
upd("Pressure",
    "Run 2201: freeMinted tetap 5/1000 (0,5%), totalSupply 5; gate tetap GAGAL; tetap early lead.",
    freeMinted=5, totalSupply=5)

# all other contracts: refresh lastReadBlock/wib only
for name, e in C.items():
    if "runNote2201_1108" not in e:
        e["lastReadBlock"] = 132416224
        e["lastReadWib"] = last_read_wib

# track_c re-read
TC = s.get("track_c", {})
if "NUSA" in TC:
    TC["NUSA"]["freeMinted"] = 220
    TC["NUSA"]["runNote2201_1108"] = ("Run 2201: freeMinted 190->220/560 = 39,3% (track_c re-read pulih dari gagal total 2131, 72/72 sukses). "
        "B: tradingOpen() = 0 (false) via bsc-dataseed eth_call -> token NUSA 0x6f91Fc7160Dc873b98a0B21Bdd974AE546FCC19a MASIH TERKUNCI, belum bisa ditransfer. Gate website tetap GAGAL.")
if "DROID" in TC:
    TC["DROID"]["runNote2201_1108"] = "Run 2201: re-read track_c sukses; DROID 733->734, tanpa perubahan status."
if "FUGUI-set1-991" in TC:
    TC["FUGUI-set1-991"]["runNote2201_1108"] = "Run 2201: re-read track_c sukses; FUGUI-set1-991 403->408, tanpa perubahan status."

# OUPE -> excluded (free pool exhausted before any report; triaged by parent)
s.setdefault("excluded", {})["OUPE Cards"] = {
    "address": "0x7cd1C2a0EE1DB8Bb3CE82270ec2610Be74A1285d",
    "symbol": "OUPEC",
    "track": "A",
    "status": "excluded-sold-out-free-2026-11-08",
    "note": ("Ditemukan feed Sourcify run 2201 (Subagent B), triase parent: startTime on-chain 2026-11-08 21:44:40 WIB, "
        "first mint blok 132410835 = 21:45:11 WIB (Ankr), freeClaimed 777/777 = 100% HABIS pada head 132420205 (B baca 663/777 ~22:28 WIB). "
        "FREE_CLAIM 44 OUPE, marketOpen 0, website() + contractURI external_link = https://oupe.fun (situs hidup, angka cocok: 777 free cards, 44 OUPE, 10.000 packs) "
        "TAPI teks fetch situs TIDAK menampilkan alamat kontrak (bundle JS tidak diinspeksi) -> gate website tidak lengkap; X/discussion UNVERIFIED. "
        "remainingFor(user)=20 tapi pool habis -> slot tidak relevan. Sourcify metadata endpoint 404 untuk alamat ini. "
        "Tidak pernah dilaporkan sebagai lead (habis sebelum laporan); dicatat excluded agar tidak dilaporkan ulang."),
    "checked_wib": "2026-11-08 23:00 WIB",
}

s["timestamp_wib"] = last_read_wib
s["last_run_wib"] = "2026-11-08 22:01 WIB"
s["last_run_note"] = ("Run 2201: 0 kandidat/lead baru. Sellout 402 (402/402) SUDAH dilaporkan hot leg 21:39 WIB — run ini hanya update status snapshot. Mint: Pokechain #5381 (agent wallet, 22:11:38 WIB, order user-named 22:04 WIB, SUDAH dilaporkan; eksekutor teridentifikasi, background search tidak lagi diperlukan) "
    "+ GLOOP #2021 (hot leg 22:05 WIB, strong-lead direct mint, sudah dilaporkan hot leg; listing 0,001 BNB sukses 22:34 WIB). OUPE Cards free pool habis 777/777 sebelum sempat dilaporkan -> excluded. "
    "Scan 132415273-132416272: 0 first-seen. Binanceai tetap refund phase. Bridge: 0 baru.")
s["runNote2201_1108"] = ("Run 2201 (22:01-23:0x WIB): re-read blok 132416224 (542 kontrak, 0 batch_fail, 26 degraded); scan window 132415273-132416272 (1000 blok, 40 Ankr calls, 0 error, 125 NFT/374 ERC-20 mint, first-seen 0); "
    "watermark TIDAK dimajukan (tetap 132411186, milik backfill); skipped gap 132411187-132415272 (4.086 blok, teritori backfill). 5c: 3 baru dicek, 0 hit S1/S2. Track_c re-read pulih 72/72. Bridge 116 kontrak, 0 baru, 7 same-owner-discarded. "
    "Velocity strict: 2 lolos tanpa promosi (Hackagent discarded; Sidecoo free% UNVERIFIED). BMT free lane mati + BNBFLY umur 48,9 jam: keduanya TIDAK di snapshot -> hanya catatan run log, tanpa laporan.")
s["runNote2201_1108_scan"] = "Scan run 2201 OK: pre-flight retry sukses (percobaan 1 gagal dataseed eth_blockNumber timeout; Ankr probe timeout 30 dtk; retry OK 34,3 dtk). Window 132415273-132416272, 20 chunk, 40 Ankr calls, 0 error, partial=false. 125 NFT / 374 ERC-20 mint. First-seen 0 (dedupe benar: known set 11.656). Watermark tidak dimajukan."
s["runNote2201_1108_binanceai"] = "Run 2201: binanceai tetap refund phase (launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0, saldo TOKEN user 0); tanpa perubahan, sudah dilaporkan sekali."
s["runNote2201_1108_web"] = ("Run 2201 web: Boltbook EN+ZH 0 proyek baru; sweep 0 kandidat baru (JOLT excluded berbayar 0,0002 BNB/klaim; PANDORA bukan Agent-ID-gated + tanpa kontrak). "
    "Route 6: 0 temuan. Sourcify feed 20 item: 0 SALE-S1/S2 baru; 5 UNKNOWN karena timeout fetch (0x356E..., 0x4Ce4..., 0x280f..., 0x7567..., 0x1732...) — cek ulang run berikut/hot-leg. "
    "Gate: BAHUANG2/HELIX/Pressure/Wisp Agent tetap gagal/belum terverifikasi; TRACE + GLOOP tetap terverifikasi; NUSA tradingOpen=0 (terkunci); Pokechain re-verifikasi /js/app.js gagal 2x (kegagalan fetch, bukan bukti situs mati).")
s["runNote2201_1108_oupe"] = ("OUPE Cards 0x7cd1C2a0EE1DB8Bb3CE82270ec2610Be74A1285d: ditemukan feed Sourcify (verifiedAt 14:47:54Z), triase parent via eth_call + Ankr. "
    "startTime 2026-11-08 21:44:40 WIB, first mint 21:45:11 WIB blok 132410835, freeClaimed 777/777 HABIS (head 132420205). FREE_CLAIM 44 OUPE, marketOpen 0, website()/contractURI()=oupe.fun. "
    "Gate tidak lengkap (situs tidak mencetak kontrak di teks fetch; bundle JS tidak diinspeksi); X UNVERIFIED; remainingFor(user)=20 tapi pool habis. -> excluded, tidak dilaporkan sebagai lead.")
s["runNote2201_1108_sellout"] = "Run 2201 sellout: 402 (freeMinted 394->402/402 FREE_CAP 402; user pegang 1). SUDAH dilaporkan hot leg 21:39 WIB (blok 132410960); run ini hanya memperbarui status snapshot, tidak lapor ulang."
s["runNote2201_1108_mints"] = ("Run 2201 mint: GLOOP #2021 (hot leg 22:05 WIB strong-lead direct mint, tx 0x1b397de6..., blok 132413324; sudah dilaporkan hot leg — run ini hanya mencatat di snapshot, tidak lapor ulang; listing 0,001 BNB sukses 22:34 WIB) "
    "dan Pokechain #5381 (agent wallet via baw, 22:11:38 WIB, tx 0x8406b7ae..., blok 132414362, gas 147455, status 1; order user-named 22:04 WIB — eksekutor teridentifikasi, mint sudah dilaporkan — run ini hanya mencatat di snapshot, tidak lapor ulang; listing gagal 351803, dilaporkan 22:29 WIB).")

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(s, f, indent=1, ensure_ascii=False)
print("SNAPSHOT UPDATED: contracts", len(C), "| track_c", len(TC), "| excluded", len(s.get("excluded", {})))
print("402 status:", C["402"]["status"], "| Pokechain balance:", C["Pokechain"]["balanceOf_user"], "| GLOOP balance:", C["GLOOP"]["balanceOf_user"])
