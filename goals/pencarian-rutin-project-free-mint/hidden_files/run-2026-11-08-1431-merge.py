#!/usr/bin/env python3
"""Merge run 1431 results into onchain-snapshot.json. No executions. Values None = keep old."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
r = json.load(open(f"{BASE}/run-2026-11-08-1431-reread.json"))
ana = json.load(open(f"{BASE}/run-2026-11-08-1431-analysis.json"))
tri = json.load(open(f"{BASE}/run-2026-11-08-1431-triage.json"))
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-08-1431.json"))
blk = r["block"]; interval = ana["interval_min"]
n_upd = 0; n_none = 0; n_changed = 0
for name, d in r.get("reread", {}).items():
    s = snap.get("contracts", {}).get(name)
    if not s:
        continue
    ts = d.get("totalSupply")
    if ts is None:
        n_none += 1
    else:
        prev = s.get("totalSupply")
        if prev is not None and ts != prev:
            minted = ts - prev
            rate = minted / interval if interval > 0 else 0
            s["previousTotalSupply"] = prev
            s["mintedInInterval"] = minted
            s["intervalMinutes"] = round(interval, 1)
            s["previousRatePerMin"] = s.get("currentRatePerMin") or 0
            s["currentRatePerMin"] = round(rate, 4)
            pr = s["previousRatePerMin"]
            ratio = (rate / pr) if pr and pr > 0 else None
            s["velocityRatio"] = round(ratio, 2) if ratio is not None else None
            s["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
            rtxt = f"{ratio:.2f}x" if ratio is not None else "None (rate sebelumnya 0)"
            s["runNote1431"] = (f"Run 1431 (blok {blk}, interval {interval:.1f} mnt): {prev}->{ts} (+{minted}, "
                                 f"{rate:.3f}/mnt vs prev {pr} = {rtxt}) -> velocity {'LOLOS' if s['velocityLegPasses'] else 'GAGAL'}.")
            n_changed += 1
        elif prev is not None:
            s["previousTotalSupply"] = prev
            s["mintedInInterval"] = 0
            s["intervalMinutes"] = round(interval, 1)
            s["previousRatePerMin"] = s.get("currentRatePerMin") or 0
            s["currentRatePerMin"] = 0.0
            s["velocityRatio"] = None
            s["velocityLegPasses"] = False
            s["runNote1431"] = f"Run 1431 (blok {blk}, interval {interval:.1f} mnt): {prev} flat -> velocity GAGAL."
        s["totalSupply"] = ts
        n_upd += 1
    bal = d.get("balanceOf_user")
    if bal is not None:
        s["balanceOf_user"] = bal; s["userBalance"] = bal
    fc = d.get("freeClaimed")
    if fc is not None:
        s["freeClaimed"] = fc
        fs = s.get("FREE_SUPPLY")
        if fs:
            s["freePctVerified"] = round(fc / fs * 100, 2)
    tm = d.get("totalMinted")
    if tm is not None:
        s["totalMinted"] = tm
    fm = d.get("freeMinted")
    if fm is not None:
        s["freeMinted"] = fm
    s["lastReadBlock"] = blk
    s["lastReadWib"] = "2026-11-08 14:49 WIB"

# ---- Zigzoo: PAID-ONLY proven -> remove from snapshot ----
ZZ = "Zigzoo"
zz_removed = None
if ZZ in snap["contracts"]:
    zz_removed = snap["contracts"].pop(ZZ)
    snap["removed1431_zigzoo"] = {
        "address": "0x09ada5a12293c30d75b97c56e34967e8a4326a3c",
        "name": "Zigzoo", "symbol": "ZIGZOO",
        "status": "removed-paid-only-2026-11-08-run1431",
        "note": ("Run 1431 deep-dive: PAID-ONLY terbukti — currentPrice 0, priceForCount(1)=0.0002 BNB, "
                 "tidak ada free view di ABI (tier PRICE_2_10/11_20/21_30, MAX_SUPPLY 5000). "
                 "Was early-lead-reported-2026-11-08. Removed from snapshot per body rule; report once."),
        "prior_status": zz_removed.get("status"),
        "totalSupply_at_removal": 1123,
    }

# ---- Status promotions / notes ----
def set_status(key, status):
    e = snap["contracts"].get(key)
    if e:
        e["status"] = status
    return e

j = set_status("Jinli Agents", "strong-lead-2026-11-08-gate-failed")
if j:
    j["gateNote1431"] = ("STRONG LEAD run 1431: umur TERVERIFIKASI first mint blok 132290865 = 2026-11-08 06:44:59 WIB "
        "(~8,25 jam); free 264/888 = 29,7% (counter terverifikasi, FREE_SUPPLY 888, MAX_SUPPLY 1888, totalSupply 267, mintOpen 1); "
        "slot user terbuka (mintedBy(user)=0, balance 0). GATE WEBSITE GAGAL — tidak ada situs terverifikasi setelah metode "
        "(A) address search, (B) Boltbook (hanya Jinli token 2026-11-02, kontrak lain 0xd7a2... — same-name BUKAN linkage), "
        "(C) Sourcify 404, (D) jinliagents.vercel.app/deep.page 404, (E) owner-group 0x23f5... hanya Jinli sendiri, "
        "(G) name search (hanya panduan umum + situs token 2026-11-02), (H) contractURI tanpa URL, (I) tokenURI tanpa URL, "
        "(K) GitHub code search (tanpa hasil; true code search butuh auth), (L) BscScan via browser task: halaman token TIDAK mencantumkan "
        "situs web maupun tautan X, (M) site: filters tanpa hasil, (N) tidak resolvable (tanpa ABI). TIDAK preview/mint. Laporkan sekali.")
    j["firstMintWib"] = "2026-11-08 06:44:59 WIB"
    j["firstMintBlock"] = 132290865

d = set_status("Dafeiyu", "strong-lead-2026-11-08-gate-failed")
if d:
    d["gateNote1431"] = ("STRONG LEAD run 1431: umur TERVERIFIKASI first mint blok 132295499 = 2026-11-08 07:19:44 WIB (~7,75 jam); "
        "free INFERENSI 634/666 = 95,2% (totalSupply 634, FREE_SUPPLY 666, tanpa free counter langsung — freeAgentCount()=1 tidak dijelaskan); "
        "slot user terbuka (freeClaimed(user)=0, mintedBy(user)=0, balance 0, isFreeEligible(user)=1, priceFor(user,1)=0); "
        "priceOf=0.003 BNB (tier berbayar sesudah free pool). GATE WEBSITE GAGAL — tidak ada situs terverifikasi setelah metode "
        "(A) address search tanpa hit proyek, (B) Boltbook (2 post: belski v7_ll98jyf38 + follow-up _oM57q4XivXk — tanpa link situs; "
        "belski eksplisit: 'Dafeiyu has no official web/social I could find (dafeiyu.io NXDOMAIN)'), (C) Sourcify metadata tanpa URL, "
        "(D) dafeiyu.vercel.app = situs陪聊 lain, dafeiyu.pages.dev = 'HORIZON' lain (same-name BUKAN linkage), dafeiyu.deed.page 404, "
        "(E) owner-group 0x0572... (terverifikasi = owner Boltbook) hanya Dafeiyu sendiri, (G) name search bertabrakan karakter DeepSeek, "
        "(L) BscScan via browser task: halaman token TIDAK mencantumkan situs web maupun tautan X. TIDAK preview/mint. Laporkan sekali.")
    d["firstMintWib"] = "2026-11-08 07:19:44 WIB"
    d["firstMintBlock"] = 132295499
    d["owner"] = "0x0572f58673a0af3249e0b2ddf4f53a94fa50da11"

p = set_status("Paw Gang", "strong-lead-2026-11-08-pow-blocked")
if p:
    p["gateNote1431"] = ("STRONG LEAD run 1431: umur TERVERIFIKASI MINT_START 2026-11-07 20:00 WIB (~19 jam); "
        "free 2337/3333 = 70,1% (mint() nonpayable, semua mint gratis); slot user terbuka (hasMinted(user)=0, balance 0, mintOpen 1). "
        "GATE WEBSITE LOLOS: https://pawgang.pages.dev/agent.json mencetak kontrak NFT persis + registry + marketplace. "
        "Binance audit: hasResult=false (TIDAK ADA HASIL, bukan pass), riskLevel -1/LOW, tanpa risk hit — tidak menghentikan mint. "
        "BLOKER: mint butuh PoW nonce — difficultyBits()=30 (fase 3, totalMinted 1670-2503; fase 4 = 33 bit di 2504). "
        "PoW di VM ini TIDAK FEASIBLE: ~42.000 hash/dtk total (4 worker), ekspektasi ~7 jam untuk 2^30; setelah ~16 mnt hanya ~40 jt hash (3,7%). "
        "Pace totalMinted ~3/mnt (2296 blok 132355740 -> 2411 ~15:27 WIB) -> fase 4 (~33 bit) tiba ~30 mnt lagi (~15:57 WIB). "
        "PoW dihentikan run 1431; TIDAK preview/mint tanpa nonce valid. Laporkan sekali sebagai strong lead + blocker PoW. "
        "Run berikutnya JANGAN ulangi PoW di VM ini kecuali ada cara lebih cepat (mesin lebih kencang / nonce dari user).")
    p["totalMinted1431fresh"] = 2411
    p["difficultyBits1431"] = 30
    p["powBlocked1431"] = True

a = snap["contracts"].get("Alchemister-0xCafEEDDF")
if a:
    a["firstMintWib"] = "2026-11-07 09:49:19 WIB"
    a["firstMintBlock"] = 132123483
    a["ageNote1431"] = ("Run 1431: first mint TERVERIFIKASI blok 132123483 = 2026-11-07 09:49:19 WIB (umur ~29,2 jam saat run; "
        "age-exclude 2026-11-09 09:49:19 WIB). Velocity LOLOS (+27, 4,12x) tapi free% UNVERIFIED (semua free view revert) -> tetap early lead, bukan promosi.")

u = snap["contracts"].get("Undead NFTs")
if u:
    u["firstMintWib"] = "2026-11-08 13:03:19 WIB"
    u["firstMintBlock"] = 132341293
    u["ageNote1431"] = ("Run 1431: first mint TERVERIFIKASI blok 132341293 = 2026-11-08 13:03:19 WIB (umur <=48 jam). "
        "freeMinted 153, totalMinted 659, MAX_SUPPLY 5555, AIRDROP_TOTAL 500, MINT_PRICE_BNB 0.0005, paidMinted 6. "
        "contractURI external_url = https://x.com/UndeadNFTs (X saja, tanpa website). free% UNVERIFIED (cap free tidak jelas) -> tetap early lead.")

x = snap["contracts"].get("0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B")
if x:
    x["ageNote1431"] = ("Run 1431 deep-dive: Sourcify verified; freeClaimed(address), freeMint(), isFree(uint256), maxSupply 20000, "
        "mintPrice 0.0015 BNB, nextId 1342, freeClaimed(user)=0, isFree(1)=1. Ukuran pool gratis tidak diketahui -> free% UNVERIFIED, tetap early lead.")

ag = snap["contracts"].get("Agent Grove")
if ag:
    ag["runNote1431"] = ("Run 1431: freeOpen()=0 MASIH TERTUTUP (baca segar ~15:27 WIB; fase 2 belum buka on-chain walau situs menjadwalkan "
        "2026-11-06 06:05 UTC). freeMinted()=2500 terbaca lagi (inkonsisten dgn situs 250/2500, dicurigai, tidak dipakai). "
        "freeClaimed(user)=0, balance 0. Tetap watchlist-only-upcoming; TIDAK ada perubahan status.")

# ---- New entries from triage (values pulled from triage JSON) ----
def tri_entry(addr, key, status, note, extra=None):
    t = tri.get(addr)
    if not t:
        return None
    fc = t.get("freeClaimed")
    fs = t.get("FREE_SUPPLY")
    e = {
        "address": addr,
        "name": t.get("name"),
        "symbol": t.get("symbol"),
        "kind": "ERC721",
        "status": status,
        "firstSeenBlock": t.get("first_block"),
        "firstMintWib": t.get("first_block_wib"),
        "scanMints": t.get("scan_mints"),
        "scanMinters": t.get("scan_minters"),
        "FREE_SUPPLY": fs,
        "freeClaimed": fc,
        "freeMinted": t.get("freeMinted"),
        "totalSupply": t.get("totalSupply"),
        "MAX_SUPPLY": t.get("MAX_SUPPLY"),
        "mintOpen": t.get("mintOpen"),
        "owner": t.get("owner") or t.get("OWNER"),
        "freePctVerified": round(fc / fs * 100, 2) if fc is not None and fs else None,
        "userMintedBy": t.get("mintedBy_user"),
        "balanceOf_user": 0,
        "lastReadBlock": blk,
        "lastReadWib": "2026-11-08 14:49 WIB",
        "source": "On-chain scan run 1431 window 132355528-132356527",
        "runNote1431": note,
    }
    if extra:
        e.update(extra)
    snap["contracts"][key] = e
    return e

WAVE_OWNER = "0x53043412c4f2436f68e56bb9638ebebb099fb3c1"
WAVE_NOTE = ("EARLY lead run 1431 (dilaporkan sekali). Factory wave: 8 kontrak, 1 owner 0x5304..., template sama "
    "(36 fns, FREE_SUPPLY 7000 / MAX_SUPPLY 7777), first mint 14:55-14:57 WIB. Memenuhi 3 kaki strong lead "
    "(umur ~45 mnt, free% 37-42%, slot mintedBy(user)=0) TAPI PROMOSI DIBATALKAN (same-owner wave, pola terbukti dalam run ini) — "
    "TIDAK pernah di-preview/di-mint. Owner ditambahkan ke same-owner-discards.json.")
for addr, key in [
    ("0x1f974998031c6DD8137E8D7aC6c2287357A2ddeb", "Cassetto"),
    ("0x9A67E1FD6409B91BD9751206c81fDf37Fc467aE6", "Candlewick"),
    ("0xF10C1E17ae65e88e34253b951dD8EC274fa3AfEB", "Coralume"),
    ("0x4c895E2eC1FB615d6bd28584644f5e778f64BC36", "Retrocam"),
    ("0x7b601C3D2050B021B3bd9d650D421f3F98436ab3", "Pixpad"),
    ("0xd9D4466342c993b43f02AE2e21D6F125a1Bd937F", "Keyforge"),
    ("0xc2027F9407eA355eeD5845Bb5e653aeed671f212", "Hourglas"),
    ("0x6551529eC146020ee59B41265614b7a00A166A3f", "Compasso"),
]:
    tri_entry(addr, key, "early-lead-reported-2026-11-08", WAVE_NOTE,
              {"promotionDiscarded": "same-owner-2026-11-08 (factory wave 8 kontrak, owner 0x5304...)"})

tri_entry("0xc36FD9884ac52eB406B80D4E91328B39251F54Ab", "Chiphiveowl", "strong-lead-2026-11-08-gate-failed",
    ("STRONG LEAD run 1431: umur TERVERIFIKASI first mint 2026-11-08 14:51:15 WIB; free 549/800 = 68,6% (counter terverifikasi); "
     "slot user terbuka (freeUsed(user)=0, mintedBy(user)=0, balance 0); PRICE 0.00007 BNB (harga berbayar sesudah free pool). "
     "GATE WEBSITE GAGAL — tidak ada situs terverifikasi setelah (A) address search, (B) Boltbook search tanpa hit, "
     "(C) Sourcify metadata tanpa URL, (D) chiphiveowl.vercel.app/pages.dev/deed.page 404/gagal, (E) owner-group 0x6f24... = 9 kontrak "
     "(Drakogent, Orbitagent, Neonagent-2, Ronagent [promotion-discarded 2026-11-03], Agentyyds, Glitchdroid, 0x1fab92b9 [strong-lead gate-failed hari ini], "
     "Chiphiveowl, Farmbuxiang), (G) name search tanpa hit, (H) contractURI base64 JSON tanpa URL (deskripsi: 'Mint is gated to .ai Agent ID holders'), "
     "(I) tokenURI(1) base64 on-chain tanpa external_url, (M) site: filters tanpa hasil; (L) BscScan tidak dijalankan untuk kontrak ini "
     "(check BscScan hanya untuk Jinli/Dafeiyu/Paw Gang/PassAgentX — keempatnya tanpa website/X). TIDAK preview/mint. Laporkan sekali."),
    {"gateFailed1431": True})
tri_entry("0x6810056D235c949f425b394dE590835096dd6AdC", "Farmbuxiang", "strong-lead-2026-11-08-gate-failed",
    ("STRONG LEAD run 1431: umur TERVERIFIKASI first mint 2026-11-08 14:57:27 WIB; free 472/700 = 67,4% (counter terverifikasi); "
     "slot user terbuka (freeUsed(user)=0, mintedBy(user)=0, balance 0); PRICE 0.00007 BNB. "
     "GATE WEBSITE GAGAL — metode sama seperti Chiphiveowl (owner sama 0x6f24..., 9 kontrak): (A)(B)(C)(D) farmbuxiang.* 404/gagal, "
     "(G) tanpa hit, (H) contractURI base64 JSON tanpa URL ('Mint is gated to .ai Agent ID holders'), (I) tokenURI(1) tanpa external_url, "
     "(M) tanpa hasil; (L) BscScan tidak dijalankan untuk kontrak ini. TIDAK preview/mint. Laporkan sekali."),
    {"gateFailed1431": True})
tri_entry("0x85dF79AD6df9BCa9292E73f973ECF49205E62dB8", "CAISHEN", "early-lead-reported-2026-11-08",
    ("EARLY lead run 1431 (dilaporkan sekali). 财神 Agents: first mint 2026-11-08 14:55:43 WIB; free 211/888 = 23,8% (<25% -> BUKAN strong lead); "
     "slot mintedBy(user)=0; owner 0x23f5... = owner yang sama dengan Jinli Agents; Sourcify NOT verified. free% terverifikasi, umur terverifikasi."))
tri_entry("0x273fc2C7705B23eb129E35aC8Da26348E6Fc4980", "Pixel Laptop", "early-lead-reported-2026-11-08",
    ("EARLY lead run 1431 (dilaporkan sekali). Pixel Laptop: first mint 2026-11-08 14:56:36 WIB; totalSupply 1267, MAX_SUPPLY 3333; "
     "free views FREE_SUPPLY 1800 / freeMintedPerWallet ada tapi TANPA counter freeMinted/freeClaimed -> free% UNVERIFIED. Tetap early lead."))
tri_entry("0x3fc442342a5289d10773aE585C6CB3Dc4A37254e", "NEKART", "early-lead-reported-2026-11-08",
    ("EARLY lead run 1431 (dilaporkan sekali). NEKART: first mint 2026-11-08 14:53:45 WIB; freeMinted 670 = totalSupply 670, MAX_SUPPLY 10000, mintOpen 1; "
     "registry bytes hit + freeMinted() terbaca via selector; Sourcify NOT verified (tanpa ABI). Ukuran pool gratis tidak diketahui -> free% UNVERIFIED. Tetap early lead."))
tri_entry("0xED33074b1E7728D8F38d28Bb00E71708c59160F1", "FU", "watchlist-only-2026-11-08-code-gated",
    ("BUKAN lead Free Bacot: mintFree(code: string) — free mint CODE-gated, TANPA satu pun fungsi agent/registry di ABI (94 fns). "
     "FREE_SUPPLY 1000, freeMinted 317, totalSupply 350, first mint 2026-11-08 14:53:44 WIB. Dicatat watchlist-only; TIDAK dilaporkan sebagai lead."))
for addr, key, own in [
    ("0x3B016fC92eF08bDe512065F2Ab5658d524744230", "Glitchronin", "0xd76d5918fb337667b22fe37ae2055b5542cf8dc9"),
    ("0x09BcDD97186F6F37521bD1b281D329E48ac54B89", "Orchidia", "0xa054275580c6d1c9077543907ac5798f2494ecce"),
    ("0x7998Dd32bE1c7bf98d3075C1D0f12De2F0e1d6eC", "Wisps", "0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd"),
    ("0x8F1246Dc5556035a4921658d81A0E06427414aFF", "SIDEWAYS", "0x293fc9e12e5db954aad233f659284f5fb5c970be"),
    ("0xa422fbf16E0e2f81A38f74B1be8b770B97575529", "Extinct Kids", "0x293fc9e12e5db954aad233f659284f5fb5c970be"),
    ("0xbd0e97f1a2b8b192382935A7B69c9514d75A479A", "OMENS", "0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd"),
]:
    tri_entry(addr, key, "watchlist-only-same-owner-discarded-2026-11-08",
        (f"Owner {own} SUDAH di same-owner-discards.json (grup discard terbukti) -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead "
         "(preseden Roninagent/run 2131). Dicatat watchlist-only + run log saja."))
tri_entry("0x4f1bE6E4c73138D706853584BA0Fa4cB923Dcd95", "SOLVED Genesis", "watchlist-only-2026-11-08",
    ("Registry bytes saja, TANPA free view (28 fns) -> bukan free-mint live; watchlist-only per preseden Lumen Fox Agent. TIDAK dilaporkan sebagai lead."))
tri_entry("0xECd0aE8AE79c1e580898480467DfC210143f9FEF", "Orivia", "watchlist-only-2026-11-08",
    ("Registry bytes saja, Sourcify NOT verified, TANPA free view -> free shape tidak diketahui; watchlist-only. TIDAK dilaporkan sebagai lead."))
tri_entry("0xbC2C4A71791fb86d14a2A859B0253aa3BBaEB34c", "MARS PLOTS", "watchlist-only-2026-11-08",
    ("Registry bytes + isFree saja, TANPA free counter/free-mint view (89 fns, ada mintPrice/MACHINE_PRICE/CLAIM_FEE) -> free mechanics UNVERIFIED; "
     "watchlist-only per preseden Lumen Fox Agent. TIDAK dilaporkan sebagai lead."))
tri_entry("0x72D977237f7b3931A08434cEBD0D3814fE13539e", "RigOrb", "watchlist-only-paid-only-2026-11-08",
    ("PAID-ONLY: registry view cocok TAPI struktur harga bertingkat (PRICE_2_TO_10/11_TO_15/16_TO_20/21_TO_30, priceFor), TANPA satu pun free view. "
     "Konsisten dengan temuan PAID-ONLY run sebelumnya. TIDAK dilaporkan sebagai lead."))
tri_entry("0x2ED9E0a6992BA22B48c2fc2def6bB2365301A0D0", "Worldygg Tree", "minted-by-user-2026-11-08",
    ("SUDAH DIMILIKI user: mintedBy(user)=1 (Worldygg Tree #7081 dari kontrak ini). totalSupply 19914, MAX_SUPPLY 99999. "
     "Excluded dari pencarian (sudah dimiliki); TIDAK dilaporkan sebagai lead."))

# ---- NeuroLink (EB71) + Nidavellir ----
snap["contracts"]["NeuroLink"] = {
    "address": "0xEB71a7cbF97e091beBE2175C48E350D1993a04c9",
    "name": "NeuroLink", "symbol": None, "kind": "ERC721",
    "status": "watchlist-only-upcoming-2026-11-08",
    "REGISTRY()": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "MAX_FREE_SUPPLY": 3333, "MAX_PAID_SUPPLY": 6667, "MAX_MINTS_PER_WALLET": 1,
    "freeMinted": 0, "freeRemaining": 3333, "totalSupply": 0, "MAX_SUPPLY": 100000,
    "firstSeenBlock": 132355528,
    "lastReadBlock": blk, "lastReadWib": "2026-11-08 14:49 WIB",
    "source": "Sourcify feed run 1431 (verified 2026-11-08 07:57:13Z = 14:57 WIB) + baca on-chain",
    "runNote1431": ("Agent-shaped, free pool UTUH (0/3333), TAPI NOL mint -> BUKAN early lead (belum ada first mint). "
        "Watchlist-only upcoming/fresh; promosi hanya bila first mint terverifikasi on-chain."),
}
snap["contracts"]["Nidavellir"] = {
    "address": "0xd527109571b039298b65bCB26313dcbED0978c97",
    "name": "Nidavellir", "symbol": "Gull", "kind": "ERC721",
    "status": "excluded-free-pool-exhausted-2026-11-08",
    "site": "https://nidavellirbsc.vercel.app/mint.html",
    "totalSupply": 1122, "MAX_SUPPLY": 4444, "mintOpen": 1, "PRICE": 1000000000000000,
    "mintedBy_user": 0, "balanceOf_user": 0,
    "lastReadBlock": blk, "lastReadWib": "2026-11-08 15:27 WIB",
    "source": "Route-3 search run 1431 (search index) + baca on-chain segar",
    "runNote1431": ("Ditemukan via sapuan web run 1431; situs mencetak kontrak persis (website evidence ADA). "
        "TAPI free lane TUTUP: kuota gratis = token ID <=1000, totalSupply SUDAH 1122 -> mint baru berbayar 0.001 BNB. "
        "Sourcify NOT verified. Excluded; TIDAK dilaporkan sebagai lead."),
}
# 0xbd4B4e71 note (slot used)
b = snap["contracts"].get("0xbd4B4e7189ae9356514664146b0eD683601200A9")
if b:
    b["runNote1431"] = ("Run 1431: FREE_SUPPLY 2777, freeMinted 1501 (54,1%), totalSupply 1509, TAPI balanceOf(user)=1 + "
        "freeClaimed(user)=1 -> slot user SUDAH DIPAKAI -> BUKAN strong lead. Tetap early-lead-backfill.")
# PassAgentX age-excluded record (not added to snapshot)
ex = snap.setdefault("excluded", {})
ex["PassAgentX"] = {
    "address": "0x08b1a979dd997492eecc010fe986ea2e2925e620",
    "track": "A",
    "status": "excluded-age-over-48h-2026-11-08",
    "note": ("Run 1431: Boltbook recheck 14:57 WIB (4.946/6.675 free, 74,1%) + baca on-chain segar: totalSupply 4946, "
        "MAX_SUPPLY 6666, freeMinted 4707, PRICE 0.0015 BNB, mintOpen 1, mintStart=1793836198 = 2026-11-05 06:50 WIB "
        "(umur ~80 jam saat run -> >48 jam), mintEnd ~2026-11-10 06:50 WIB, freeUsedByWallet(user)=0, "
        "contractURI = https://passagentx.xyz/meta/collection.json. AGE-EXCLUDED; tidak ditambahkan ke snapshot, tidak dilaporkan."),
}

# ---- same-owner-discards: add 0x5304 wave owner ----
disc = json.load(open(f"{BASE}/same-owner-discards.json"))
n_disc_before = len(disc)
wave_names = ["Cassetto", "Candlewick", "Coralume", "Retrocam", "Pixpad", "Keyforge", "Hourglas", "Compasso"]
wave_addrs = {
    "Cassetto": "0x1f974998031c6DD8137E8D7aC6c2287357A2ddeb",
    "Candlewick": "0x9A67E1FD6409B91BD9751206c81fDf37Fc467aE6",
    "Coralume": "0xF10C1E17ae65e88e34253b951dD8EC274fa3AfEB",
    "Retrocam": "0x4c895E2eC1FB615d6bd28584644f5e778f64BC36",
    "Pixpad": "0x7b601C3D2050B021B3bd9d650D421f3F98436ab3",
    "Keyforge": "0xd9D4466342c993b43f02AE2e21D6F125a1Bd937F",
    "Hourglas": "0xc2027F9407eA355eeD5845Bb5e653aeed671f212",
    "Compasso": "0x6551529eC146020ee59B41265614b7a00A166A3f",
}
for nm in wave_names:
    disc.append({
        "contract": wave_addrs[nm],
        "discarded_wib": "2026-11-08T15:30:00+07:00",
        "owner": WAVE_OWNER,
        "owner_source": "fresh eth_call owner() run 1431 triage (8 kontrak, 1 owner)",
        "project": f"{nm}",
        "reason": ("owner 0x5304... = factory wave 8 kontrak template sama (FREE_SUPPLY 7000/MAX_SUPPLY 7777), "
            "first mint 2026-11-08 14:55-14:57 WIB; promosi ke strong lead DIBATALKAN run 1431 (preseden Gourdwick); "
            "kontrak baru dari owner ini TIDAK PERNAH dipromosikan/dilaporkan sebagai lead."),
    })
json.dump(disc, open(f"{BASE}/same-owner-discards.json", "w"), indent=1)

# ---- scan state + seen ----
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = "2026-11-08 15:25 WIB"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors")
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = scan.get("erc20_mint_contracts")
state["skipped_gap"] = "132351655-132355527 (3873 blok, backfill off)"
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
n_seen_before = len(seen)
for c in scan.get("contracts", []):
    a = c["address"]
    if a not in seen:
        seen[a] = {"first_block": c.get("first_block"), "kind": c.get("kind"),
                   "mint_count": c.get("mint_count"), "seen_wib": "2026-11-08 15:25 WIB"}
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

# ---- run notes ----
snap["runNote1431"] = (
    "Run 1431 (2026-11-08, blok reread 132355740, interval 33,5 mnt vs run 1401): reread 486 kontrak + 71 track_c; "
    "velocity LOLOS 5 (bridge-0x6eee003e artefak ERC-20 wei — abaikan; Alchemister +27 4,12x free% UNVERIFIED; WAR3 +468 minted-by-user; "
    "0x1a904Da7 +39 2,19x free% UNVERIFIED; Zigzoo +20 3,56x — PAID-ONLY, dihapus). "
    "Sellout_new 13 semuanya minted-by-user lama (freePct 100%) — bukan baru. Degraded 158 kontrak totalSupply=None (nilai lama dipertahankan, BUKAN nol). "
    "STRONG LEAD 4: Jinli + Dafeiyu (gate website GAGAL — laporkan sekali + alasan, TIDAK preview/mint), "
    "Chiphiveowl + Farmbuxiang (gate website GAGAL — laporkan sekali + alasan, TIDAK preview/mint), "
    "Paw Gang (gate LOLOS via pawgang.pages.dev/agent.json, audit Binance hasResult=false tanpa risk hit, TAPI mint BLOKIR PoW — "
    "nonce 30-bit tidak feasible di VM ini ~42 rb hash/dtk, ekspektasi ~7 jam; fase 4 (33 bit) tiba ~15:57 WIB; PoW dihentikan). "
    "EARLY LEAD BARU 11: wave 0x5304 (Cassetto/Candlewick/Coralume/Retrocam/Pixpad/Keyforge/Hourglas/Compasso — promosi DIBATALKAN same-owner wave, "
    "owner 0x5304... masuk same-owner-discards.json) + CAISHEN (23,8% <25%) + Pixel Laptop + NEKART. "
    "Zigzoo PAID-ONLY terbukti -> dihapus dari snapshot, laporkan sekali. "
    "Track-B binanceai tetap refund phase (launched 0/failed 1/refund 1, shares 3110) — sudah dilaporkan, tidak dilaporkan ulang. "
    "Bridge: tidak berubah (115 kontrak, semua temuan lama 2026-11-03 s.d. 06, sudah dilaporkan sebagai finding oleh scan job; tidak ada aksi).")
snap["runNote1431_scan"] = (
    "Run 1431: SCAN OK (pre-flight OK 37,7 dtk; percobaan 1 terbunuh restart service ~14:56 WIB di chunk 17/20; percobaan 2 SUKSES PENUH). "
    "Window 132355528-132356527 (1000 blok terbaru; cap 1000), 148 kontrak (ERC721+ERC1155) + 341 ERC-20-mint, 40 Ankr calls, 0 error, partial=false. "
    "44 first-seen: 13 agent-shaped jelas + 12 triase (25 triase lean) -> 11 early lead baru + 2 strong lead gate-failed + 6 same-owner-discarded "
    "(owner sudah di discards) + FU code-gated + SOLVED/Orivia/MARS PLOTS registry-only + RigOrb paid-only + Worldygg Tree sudah dimiliki. "
    "Watermark 132351654 -> 132356527; skipped gap 132351655-132355527 (3873 blok, backfill off). HIVE Agents tidak ada di window.")
snap["runNote1431_gates"] = (
    "Run 1431 gate checks: Jinli (A-K,M,N + L BscScan: halaman token tanpa website/X) GAGAL; Dafeiyu (A-E,G,C,D + L BscScan tanpa website/X; "
    "Boltbook belski eksplisit 'no official web/social', dafeiyu.io NXDOMAIN) GAGAL; Chiphiveowl/Farmbuxiang (A,B,C,D,G,H,I,M; L tidak dijalankan "
    "untuk keduanya) GAGAL; Paw Gang LOLOS (pawgang.pages.dev/agent.json mencetak kontrak persis). "
    "BscScan browser task browser-task:9f4b3ae3-9078-5992-8ae7-9250396dccab selesai 15:05 WIB: keempat kontrak (Jinli/Dafeiyu/Paw Gang/PassAgentX) "
    "tidak mencantumkan situs web maupun tautan X di BscScan (Cloudflare sempat memblokir, lalu pulih).")
snap["runNote1431_5c"] = (
    "Run 1431 5c: 341 ERC-20 mint_count>=10 total 48, 6 baru dicek (cap 20, 0 dibuang sampling limit), 0 sale-shape S1/S2 "
    "(5 no-abi Sourcify, 1 proxy 0 fungsi); track-c-scan-checked.json 1482 -> 1488 top-level keys.")
snap["runNote1431_binanceai"] = (
    "Run 1431: binanceai tetap fase refund/failed (launched 0, failed 1, isRefundPhase 1, totalShares 3110, tokenClaimed_user 0, "
    "balance 0, token totalSupply 13.688.000.000.000.000.000.000.000.000; claimable() revert). SUDAH dilaporkan — TIDAK dilaporkan ulang.")
snap["runNote1431_discovery"] = (
    "Run 1431 discovery (routes 2/3/5a/6): Boltbook EN+ZH ~14:57-14:58 WIB — PassAgentX, SUOHA, Pacture, Dafeiyu 33 free left, ONI 707/1000, "
    "Sigmora, Gloop (buka 19:00 WIB), REWARD free lane CLOSED 200/200, Goats 735/1111 (kontrak snapshot terkonfirmasi sama), WAR3 free lane CLOSED 14:42 WIB, "
    "Paw Gang 2287-2313/3333, POH/HokiBunny/EMBER (POH + EMBER sudah early-lead-reported di snapshot; HokiBunny sudah dihapus run 1401; "
    "ERC-20 POH 0x3c8f... berbayar 16.800 POH — bukan lead gratis), ZH board (ROSE ~80/jam, PAWG + PANDORA memanas, Zigzoo 1123/5000). "
    "Route-3 sweep: Agent Grove freeOpen()=0 MASIH TERTUTUP (fase 2 belum buka on-chain) — tanpa perubahan; Nidavellir free lane TUTUP "
    "(totalSupply 1122 > cap free 1000) — excluded; Pixel Fox 0x9134... TIDAK di snapshot (post 25 Okt, age-excluded, tidak ditambah); "
    "Agent Periodic Lab 0xfe5a... = bridge contract (scan finding, bukan lead). ONI post tanpa alamat kontrak (kontrak ke-3 tidak terverifikasi; "
    "ONI-74bD freeMinted 137, ONI-d576 freeMinted 1000 = pool penuh — keduanya sudah tercatat). "
    "Sourcify feed 20 -> 5 baru: NeuroLink 0xEB71... (watchlist-only, 0 mint) + 4 bukan agent-shaped. "
    "Square search-index: Agent Grove + Nidavellir (di atas). Odaily/PANews tidak dicek run ini (dilewati, coba lagi run berikut); DappBay tidak dibutuhkan.")
snap["last_run"] = "free-mint-search 2026-11-08 1431 WIB"
snap["last_run_wib"] = "2026-11-08 15:30 WIB"
snap["timestamp_wib"] = "2026-11-08 run 1431"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: contracts updated={n_upd}, none-reads={n_none}, changed={n_changed}, zigzoo_removed={zz_removed is not None}, "
      f"discards {n_disc_before}->{len(disc)}, seen {n_seen_before}->{len(seen)}, snapshot contracts now={len(snap['contracts'])}")
