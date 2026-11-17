#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 01:01 WIB.
Address-exact matching only (lesson run 0001). Updates numeric fields +
lastReadWib; adds Agentx (early lead), GAME (strong-lead-gate-blocked,
reported by hot-leg 01:08), OUTY (upcoming); removes AgcNFT (sold out,
reported once this run); records MUTPHO checked. Top-level runNotes added.
Backup: /tmp/onchain-snapshot-2026-11-13-0101.bak (taken before run)."""
import json, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-13 ~01:40 WIB"
BLOCK = 133205288
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
def by_addr(addr):
    for k, v in contracts.items():
        if isinstance(v, dict) and (v.get("address") or "").lower() == addr.lower():
            return k, v
    return None, None
def upd(addr, fields):
    k, v = by_addr(addr)
    if v is None:
        print("WARN not in snapshot:", addr); return None
    old_ts = v.get("totalSupply"); old_tm = v.get("totalMinted")
    v.update(fields); v["lastReadWib"] = NOW
    return k
verify = json.load(open(BASE + "run-2026-11-13-0101-verify.json"))["reads"]
INTERVAL_MIN = 12.5  # block delta 133205288-133203617 = 1671 blocks x ~0.45 dtk
def vel(name, old_total, new_total):
    if old_total is None or new_total is None: return {}
    minted = new_total - old_total
    rate = round(minted / INTERVAL_MIN, 3) if INTERVAL_MIN else 0
    return {"previousTotalSupply": old_total, "mintedInInterval": minted,
            "intervalMinutes": INTERVAL_MIN, "currentRatePerMin": rate,
            "velocityLegPasses": False}
# --- route-1 re-reads (old totals from run 0031 runlog) ---
upd("0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606", {"totalMinted": 297, "freeMinted": 297,
    "FREE_CAP": 333, "mintOpen": 1, "freeClaimed_user": 0, "balanceOf_user": 0,
    **vel("SolNFT", 293, 297)})
# AgcNFT SELLOUT 333/333 -> remove (reported once this run; not in hot-leg-reported)
k, v = by_addr("0xdAc222886b887fC5b6262889B189B8eb57e99794")
if v is not None:
    print("REMOVING AgcNFT (sold out 333/333):", k); del contracts[k]
else:
    print("AgcNFT already absent")
upd("0xD405C90079c594DA2456F5b37B4158A12f1382e5", {"totalSupply": 21, "agentFreeCount": 20,
    "paidSold": 1, "mintOpen": 1, "balanceOf_user": 0})
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", {"totalMinted": 1872, "freeClaimed": 1871,
    "freeAvailable_user": 2, "balanceOf_user": 0})
upd("0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf", {"totalSupply": 398, "freeClaimed": 398,
    "FREE_SUPPLY": 555, "mintOpen": 1, "freeUsed_user": 0, "balanceOf_user": 0,
    **vel("Steady", 387, 398)})
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6", {"totalSupply": 962, "balanceOf_user": 0})
upd("0x11986f3DF799a28bB97921F49406a7197b1d34d2", {"totalSupply": 92, "mintOpen": 1, "balanceOf_user": 0})
upd("0x467696af8c2206B977B24081445104632dc1D459", {"totalMinted": 930, "freeMinted": 930,
    "FREE_SUPPLY": 1200, "balanceOf_user": 1, "freeAvailable_user": 0})
upd("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", {"totalMinted": 301, "freeMinted": 300,
    "FREE_SUPPLY": 300, "balanceOf_user": 1})
upd("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467", {"freeUsed": 226, "FREE_QUOTA": 555,
    "mintEnd": 1794570281, "freeClaimed_user": 0, "balanceOf_user": 0})
upd("0x651302C0043040D48EaAF85605E12F0549aD6D89", {"FREE_SHARES": 500, "freeUsed": 21})
# retries (address-exact; totals only)
for addr, ts in [("0xad86e4d52e55709d1bda08f922853d4b109e0810", 922),
                ("0x7ef49be2a9ade4fae0888f4065c8f122a146f6d0", 4900),
                ("0xb8a990e16fd66d398cc27d0c8bdb11524bc0dc8e", None),
                ("0xad0d8ac3d61fc8ab397b7136c69fcbf1281a4998", 561),
                ("0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69", 5288),
                ("0x486d0947caa3d70c19e38f6c789489d39291e9e7", 3000),
                ("0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4", 327),
                ("0x8aa9d6a09caf475593852e681b58b26dc94edd56", 4901),
                ("0x6c17af4fac529e5679686e121a75e85b1063cd45", 4900)]:
    if ts is not None: upd(addr, {"totalSupply": ts})
# AgentLabs: specimens 723 -> 761 (+38 in ~13.9 min by block delta, ~2.7/mnt baseline)
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7", {"totalSpecimens": 761, "participantsOf": 739,
    "genesisOpen": 1, "isSealed": 0, "experimentEnd": 1794528000, "priceFor_user": 0,
    "specimensOf_user": 0, "holdsAgentId_user": 1, "balanceOf_user": 0,
    "previousTotalSpecimens": 723, "specimensInInterval": 38, "intervalMinutes": 13.9,
    "currentRatePerMin": 2.7, "velocityLegPasses": False})
# RESUME-BC1B (track_c): freeCount unchanged 446
for k, v in track_c.items():
    if isinstance(v, dict) and (v.get("address") or v.get("sale") or "").lower() == "0xbc1b62550d69fc02683cd4836f24cbf5d90be053":
        v["freeCount"] = 446; v["lastReadWib"] = NOW; print("BC1B updated:", k)
# --- NEW: Agentx early lead ---
contracts["Agentx"] = {
    "address": "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
    "name": "Agentx", "symbol": "AGENTX",
    "status": "early-lead-reported-2026-11-13",
    "totalMinted": 292, "freeMinted": 292, "FREE_CAP": 1111, "MAX_SUPPLY": 2222,
    "mintOpen": 1, "mintOpensAt": 1794499865, "mintOpensAtWib": "2026-11-12 23:11:05 WIB",
    "price": 5000000000000000, "freeClaimed_user": 0, "balanceOf_user": 0,
    "holdsAgentId_user": 1, "mintsBy_user": 0, "nextTokenId": 293,
    "owner": "0xd314d0b0d204cd6dd7a5b8c9cda1cadc59984344",
    "freePct": 26.3, "freePctNote": "292/1111 FREE_CAP (verified on-chain this run)",
    "ageVerified": True, "ageHours": 2.2,
    "ageNote": "mintOpensAt on-chain 1794499865 = 23:11:05 WIB 12 Nov; Boltbook post 2026-11-12T18:06:16Z (01:06:16 WIB 13 Nov) cites freeMinted 287 at block 133204790; this run 292 at block 133205922 - konsisten.",
    "agentShaped": True,
    "agentShapeNote": "Sourcify ABI 64 fns: mint(), mintFree? no - mint(), price(), freeClaimed/freeMinted, agentIdRegistry(), holdsAgentId(); bytecode contains registry bytes 0x60B926...; constructor (registry_, treasury_, mintOpensAt_). S1 PASS (mint+price-as-quote+free views+agent ref).",
    "discussion": "Boltbook post gregrichy.ai 2026-11-12T18:06:16Z 'Agentx is the new free Agent ID mint tonight, 824 of 1111 free left' (https://boltbook.fun/p/gki4iDBTpTe0). Public web/social mention - counts as discussion evidence.",
    "website": None, "gate": "website_unverified",
    "gateNote": "Gate methods tried run 0101: (A) contract-address search 0 site hits; (B) Boltbook post links only BscScan + gang.fun (unrelated) + x.com/bolt_book, author profile gregrichy.ai no site link; (C) Sourcify metadata no project URLs; (D) agentx.pages.dev HTTP 200 9919 byte no contract print, agentx.fun HTTP 200 no print, agentx.vercel.app HTTP 200 no print (same-name pages do not print the contract - NOT evidence); (E) owner 0xd314... no linkage in snapshot; (G) name search no site; (H) no contractURI fn; (I) tokenURI returns bare token id ('1'/'292'), no URL; (J) no site fns in ABI; (K) GitHub search no repo for this contract; (L) BscScan token page via live browser NOT attempted (same limitation as prior runs); (M) site: filters covered by A/D - no hit. X unverified (optional, never gates).",
    "xVerified": False,
    "velocityNote": "First read this run (baseline): 292 minted. Velocity cannot pass yet (no previous rate).",
    "velocityLegPasses": False, "previousRatePerMin": None, "currentRatePerMin": None,
    "previousTotalSupply": 292, "mintedInInterval": 0,
    "lastReadWib": NOW, "lastReadBlock": 133205922,
    "baselineNote": "EARLY lead dilaporkan sekali run 0101 13 Nov (temuan Boltbook front page EN+ZH). BUKAN kandidat (26,3% <50%), BUKAN strong lead (<70%), website UNVERIFIED -> TIDAK di-preview/TIDAK di-mint. Slot user terbuka (freeClaimed 0, holdsAgentId 1).",
}
# --- NEW: GAME strong-lead-gate-blocked (reported by hot-leg 01:08; main job tracks from now) ---
contracts["Game"] = {
    "address": "0x9c204b333538F853cD5FD8306277130514B86F04",
    "name": "Game", "symbol": "GAME",
    "status": "strong-lead-gate-blocked-2026-11-13",
    "totalMinted": 330, "freeMinted": 330, "FREE_CAP": 333, "mintOpen": 1,
    "mintOpensAt": 1794498624, "mintOpensAtWib": "2026-11-12 22:50:24 WIB",
    "price": 1400000000000000, "freeClaimed_user": 0, "balanceOf_user": 0,
    "quote_user_1": None,
    "freePct": 99.1,
    "ageVerified": True, "ageHours": 2.6,
    "ageNote": "mintOpensAt on-chain 1794498624 = 22:50:24 WIB 12 Nov; first mint corroborated 6 minted ~22:53 (hot-leg).",
    "website": None, "gate": "website_unverified",
    "gateNote": "Hot-leg re-verified gate ~01:00 WIB 13 Nov: FAILED. This run: contract-address search 0 site hits (unrelated games only). quote(user,1) null 2 runs (must be 0 before any preview if site verifies later).",
    "xVerified": False,
    "velocityNote": "325/333 at ~01:00 -> 330/333 this run (+5, <20) - velocity FAILS; sellout imminent (3 slots left).",
    "velocityLegPasses": False,
    "lastReadWib": NOW,
    "baselineNote": "STRONG LEAD gate-blocked dilaporkan sekali oleh hot-leg 01:08 WIB 13 Nov (freeMinted 325/333 = 97,6%). Main job TIDAK melapor ulang; entry ini agar main job melacak perubahan (sellout/slot hilang). TIDAK di-preview/TIDAK di-mint (gate gagal).",
}
# --- NEW: OUTY upcoming (START future, 0 mints) ---
contracts["OUTY"] = {
    "address": "0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412",
    "name": "OUTY", "symbol": "OUTY",
    "status": "watchlist-only-upcoming-2026-11-13",
    "minted": 0, "freeSold": 0, "paidSold": 0, "FREE_SUPPLY": 1500, "PAID_CAP": 15000,
    "START": 1794510227, "startWib": "2026-11-13 02:03:47 WIB",
    "FREE_END": 1794596627, "FREE_FEE": 100000000000000, "PRICE": 3000000000000000,
    "phase": 0, "freeOpen": 0, "paidOpen": 0,
    "freeQuotaOf_user": 1, "quotaOf_user": 10, "balanceOf_user": 0,
    "agentShaped": True,
    "agentShapeNote": "Sourcify ABI: REGISTRY + mintFree() + free views (freeSold/freeQuotaOf); bytecode contains registry bytes. No quote fn; S1 fails (no quote), S2 fails (not a token contract). Early-shape TRUE but 0 mints + not open -> upcoming, NOT early lead.",
    "website": None, "gate": "website_unverified",
    "lastReadWib": NOW, "lastReadBlock": 133205922,
    "baselineNote": "Upcoming-watchlist run 0101 (temuan feed Sourcify). Dibuka 02:03:47 WIB 13 Nov (START on-chain); freeOpen 0, minted 0. TIDAK dilaporkan sebagai lead; promosi ke early lead bila first mint terverifikasi + bentuk lolos.",
}
# --- MUTPHO checked (feed; not agent-shaped, 0 mints) ---
track_c["Feed-0x52B3"] = {
    "address": "0x52B3442FE4AfDe958285fDc9c8d8D5283C9c36e1",
    "name": "Mutex Phoenixes", "symbol": "MUTPHO",
    "status": "checked-not-agent-shaped-2026-11-13",
    "note": "Run 0101 Sourcify feed: totalSupply 0, FREE_SUPPLY 7000, MAX 7777, PRICE 0.00005 BNB, mintOpen 1; ABI has mint+quote+free views + contractURI/externalUrl (https://mutex-phoenixes.668823.xyz) BUT no agent fn and bytecode has NO registry bytes -> NOT agent-shaped, NOT Free Bacot. 0 mints -> not launched. Dicatat checked saja.",
    "lastReadWib": NOW,
}
# --- top-level run notes ---
snap["runNote0101_1113"] = ("Run 0101 (blok 133205288, verify 76,0 dtk): 1 EARLY LEAD BARU (Agentx) + 1 SELLOUT (AgcNFT 333/333, dilaporkan sekali + dihapus dari snapshot). "
    "0 kandidat baru, 0 strong lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. GAME 330/333 = 99,1% (3 slot tersisa) tetap strong-lead-gate-blocked - DIAM (dilaporkan hot-leg 01:08, main job mulai melacak via snapshot). "
    "SolNFT 297/333 = 89,2% tetap strong-lead-gate-blocked - DIAM. OBFG 500/1230 = 40,7% tetap track-C lead gate-blocked - DIAM. BC1B 446/3000 tetap - DIAM. "
    "Steady 398/555 = 71,7% (melewati 70%) TAPI umur MASIH UNVERIFIED (pencarian indeks run ini 0 hasil baru) -> tidak promosi, tetap early - DIAM. "
    "AgentLabs 761 spesimen (+38, ~2,7/mnt baseline baru; velocity tidak lolos - belum ada previous rate) - DIAM. "
    "Velocity: 0 lolos. Scan leg fast-fail (Ankr 401); watermark tetap 132512564. Feed 20 kontrak (verifiedAt 17:42:05-18:09:39Z), 11 baru vs hot-leg-seen; Boltbook EN 45.327 byte / ZH 43.627 byte (curl retry sesudah urllib IncompleteRead), 12 alamat masing-masing, 2 baru (Agentx + tx-hash 0x4983... yang ternyata hash tx MORPHA, bukan kontrak). "
    "Bridge 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded. Binanceai tetap refund/failed. Odaily 0 item Agent ID. Sweep EN+ZH: 0 proyek baru (semua dikenal/age-excluded: Oathbots, AGENT MAO paused, Agentic Gangster, Lenx, AGENT COSMOS, RIGBYPASS, MOLT AGENT, Subsonic Tribe, Pixel Fox).")
snap["runNote0101_1113_scan"] = ("Run 0101 route 4: SCAN FAST-FAIL - pre-flight ankr_getLogs (50 blok) HTTP 401 Unauthorized (~25 dtk). Watermark TIDAK dimajukan (tetap 132512564); gap ke head terus tumbuh (head ~133,21 juta saat run). Route 5c dilewati (tanpa output scan baru). Ankr outage sejak 9 Nov.")
snap["runNote0101_1113_binanceai"] = ("Run 0101 track-B: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, tokenClaimed(user)=0, tokenBalance(user)=0, TOKEN totalSupply 13.688.000.000.000.000.000.000.000.000 (blok 133205288) - tetap refund/failed, tidak dilaporkan ulang.")
snap["runNote0101_1113_agentx"] = ("Run 0101 Agentx EARLY LEAD BARU: 0x64a5e5f475defdf9b7302cc40641a1cbcb94e492, freeMinted 292/1111 = 26,3% (Boltbook 287 di blok 133204790 -> 292 di blok 133205922), mintOpen 1, mintOpensAt 1794499865 = 23:11:05 WIB 12 Nov (umur ~2,2 jam, terverifikasi <24 jam), slot user terbuka (freeClaimed 0, holdsAgentId 1, balanceOf 0), price 0,005 BNB (jalur berbayar), S1 PASS + registry bytes di bytecode. Diskusi: post Boltbook gregrichy.ai 2026-11-12T18:06:16Z. Website UNVERIFIED (metode A-K/M/N dicoba, L tidak dicoba - butuh browser live; lihat entry snapshot). TIDAK di-preview/TIDAK di-mint (early lead tidak pernah auto-mint). First-seen: tidak ada di snapshot/scan-seen/hot-leg-seen/hot-leg-reported.")
snap["runNote0101_1113_obfg"] = ("Run 0101 (blok 133205288): OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 freeMinted 495->500/1230 (40,7%), totalSupply 500, saleStart 1794488476 (20:01:16 WIB 12 Nov), saleOpen=1, freeAvailable(user)=1. Tetap track-C lead gate-blocked - DIAM. (Tetap tanpa entri terstruktur, hanya runNote per run.)")
snap["runNote0101_1113_game"] = ("Run 0101 GAME re-read: 0x9c204b333538F853cD5FD8306277130514B86F04 freeMinted 325->330/333 = 99,1% (3 slot tersisa), mintOpen 1, slot user terbuka, quote(user,1) null (2 run berturut-turut). BELUM sellout - tidak ada laporan perubahan. Tetap strong-lead-gate-blocked - DIAM (dilaporkan hot-leg 01:08 WIB). Entry snapshot dibuat run ini agar main job melacaknya.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED. contracts:", len(contracts), "track_c:", len(track_c))
# --- scan-seen: add Agentx first-seen block (Boltbook-cited block 133204790) ---
try:
    seen = json.load(open(BASE + "onchain-scan-seen.json"))
    if isinstance(seen, dict):
        seen["0x64a5e5f475defdf9b7302cc40641a1cbcb94e492"] = 133204790
        json.dump(seen, open(BASE + "onchain-scan-seen.json", "w"), indent=1)
        print("SCAN-SEEN Agentx added (block 133204790). n =", len(seen))
    else:
        print("SCAN-SEEN not a dict, skipped:", type(seen).__name__)
except Exception as e:
    print("SCAN-SEEN err:", type(e).__name__, str(e)[:120])
