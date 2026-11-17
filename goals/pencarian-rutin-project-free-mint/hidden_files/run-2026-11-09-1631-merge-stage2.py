#!/usr/bin/env python3
"""Merge STAGE 2 run 2026-11-09 1631 WIB — Skunk Hollow strong-lead DIRECT MINT (executed),
Marbleworks early lead, Flare watchlist-only, spot-sale checked-not-leads, final run notes.
Read-only w.r.t. chain except the already-executed Skunk mint (verified on-chain).
Writes: onchain-snapshot.json (atomic), run-2026-11-09-1631-merge-stage2.json."""
import json, os
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
m1=json.load(open(f"{HF}/run-2026-11-09-1631-merge-stage1.json"))
r1631=json.load(open(f"{HF}/run-2026-11-09-1631-reread.json"))
BLOCK=r1631["block"]
contracts=snap.setdefault("contracts",{})
tc=snap.setdefault("track_c",{})
report={"run":"2026-11-09-1631","stage":2,"block":BLOCK,
        "mint_executed":["Skunk Hollow #708"],
        "early_leads_new":["Marbleworks"],
        "watchlist_only_new":["Flare Agent"],
        "checked_not_lead":["0xb79BA612aBe9BB82e727AB394b2c094C6507d76d","0x448f01b6366b333e3e8046645c35181FFF51De5b","0x57cf26c69fC9171937BA47164a3F8F451FD85B20","0x9ecEb8B0081b9df25fF271bF24735d6Dea671D78","0x391D7b854b6152a201A3D83Ec2B83b4FC141C03C"],
        "age_exclusions":m1.get("age_exclusions",[]),
        "promotions":[],"velocity_rulings":{},"track_c_notes":{}}
# ---- 1. Skunk Hollow: minted-by-user ----
sk=contracts.get("Skunk Hollow",{})
sk.update({
 "status":"minted-by-user-2026-11-09",
 "freeSkunksClaimed":708,"freeSkunksRemaining":1792,"totalSkunksMinted":708,
 "freePctVerified":28.32,
 "website":"https://skunkhollow.netlify.app",
 "websiteVerified":True,
 "websiteEvidence":"Method (I) tokenURI(1) -> https://skunkhollow.netlify.app/meta/1.json (metadata di-host di domain proyek); front page skunkhollow.netlify.app + config.js site-published mencetak kontrak persis: skunks 0x88E4b613609af6C479F11D78e5a696d84B78993B + skunkToken 0x7830E0F23DC6F6f14faF4037ec53Ae139cc64AFB + agentIdRegistry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (preseden Motor Agent: config situs). Metode lain yang dicoba sebelum gate lolos: (A) pencarian alamat kontrak tanpa hasil situs; (G) pencarian nama proyek tanpa situs; (H) contractURI() revert; (J) ABI 58 fns tanpa fungsi situs; (D) skunkhollow.pages.dev / skunk-hollow.pages.dev / skunkhollow.vercel.app (404) / skunkhollow.fun — semua gagal.",
 "xHandle":"@BnbSkunk (https://x.com/BnbSkunk, tercantum di config.js situs proyek; profil X belum dibaca langsung)",
 "xVerified":False,
 "devWallet":"0x7e1c68c63744f85405f581202d69b5d39a1764ab",
 "devWalletInDiscards":False,
 "mintTx":"0xe211754b03124c54be9ecb4fc0555aa94314b34421c09cf7e862283349ccb3d1",
 "mintBlock":132568173,
 "mintGas":223809,
 "mintTokenId":708,
 "mintOrderId":"26110900002029422684",
 "mintPreviewRequestId":"8f4512342cda4d41b0db9231a097ae57",
 "mintAudit":"Binance audit hasResult=false (tidak ada hasil, BUKAN lolos), isSupported=true, riskLevel -1, riskItems=[], riskAlert=null — diungkap sebagai tidak ada hasil; tanpa hit RISK.",
 "mintPreview":"clean: simulationCode 000000000, simulationErrorDetail null, value 0, authorityChanges [], allowanceChanges [], risks kosong; balanceChanges +1 ERC721 tokenId 708 (sesuai ekspektasi).",
 "userBalance":1,"balanceOf_user":1,"freeClaimedBy_user":1,
 "freeWindowClosesAt":1794225615,
 "lastReadBlock":132568298,"lastReadWib":"2026-11-09 17:5x WIB",
 "marketplace":"TIDAK ada own market live terverifikasi: situs menyatakan Skunk ERC-721 bisa ditransfer/dijual tapi tidak menautkan market/marketplace mana pun dan tidak ada kontrak market; TIDAK di-listing (aturan auto-list: tanpa own market live / floor live -> tidak listing). Element hanya opsi fallback manual (bukan auto-listing). SKUNK token tanpa pair (per post Boltbook).",
 "rarity":"Tier #708 TIDAK terverifikasi: tokenURI(708) revert/kosong di 3 RPC (tokenURI(707) juga); metadata token #1 (terbaca) memakai Tier 'Unrevealed' — kosakata tier proyek, BUKAN tier #708. Tidak ada tier yang ditebak.",
 "runNote1631_1109":"Run 1631: STRONG LEAD -> DIRECT MINT BERHASIL. freeSkunksClaimed 706->707 (pre-mint, blok 132565922) -> 708 pasca-mint; 707/2500=28,28% (>=25%); umur terverifikasi gateStart 2026-11-08 19:00:15 WIB (~22,8 jam <=48 jam); slot user TERBUKA (freeClaimedBy=0 pre-mint); website TERverifikasi via tokenURI+config.js. Preview bersih (req 8f451234...), eksekusi claimFree(address(0)) value 0 -> tx 0xe211754b... blok 132568173, gas 223809, receipt 1; tokenId 708 terverifikasi (Transfer 0x0->user, balanceOf=1, freeClaimedBy=1).",
})
contracts["Skunk Hollow"]=sk
# ---- 2. Marbleworks (early lead) ----
contracts["Marbleworks"]={
 "address":"0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0",
 "status":"early-lead-reported-2026-11-09",
 "name":"Marbleworks","symbol":"MWORKS","kind":"ERC721",
 "source":"Sourcify recently-verified feed (verifiedAt 2026-11-09T10:01:23Z = 17:01 WIB), run 1631 discovery",
 "website":"https://marbleworks.surge.sh",
 "websiteVerified":True,
 "websiteEvidence":"Method (I) tokenURI(1) base64 JSON external_url https://marbleworks.surge.sh; front page situs (33.591 byte) mencetak kontrak persis: NFT 0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0 + TOKEN 0x458ba0b810ff314b1d7d41a0f0f209706dcf949b + registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F. Metode lain: (A) pencarian alamat kontrak tanpa hasil; (G) pencarian nama proyek tanpa hasil; (H) contractURI() None.",
 "xHandle":None,"xVerified":False,
 "sourcify":"verified exact_match (ABI: AGENT_ID_REGISTRY, FREE_SUPPLY, freeMinted, freeAvailable, mintStart/End/Open, quote, price, TOKEN, tierOf/tierName/tierReward, claim/claimable)",
 "AGENT_ID_REGISTRY":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
 "TOKEN":"0x458ba0b810ff314b1d7d41a0f0f209706dcf949b",
 "FREE_SUPPLY":1111,"freeMinted":80,"freePctVerified":7.2,
 "MAX_SUPPLY":5555,"totalSupply":90,"totalMinted":90,"paidMinted":10,
 "PRICE":1000000000000000,
 "mintStart":1794218468,"mintStartWib":"2026-11-09 17:01:08 WIB",
 "mintEnd":1794650468,"mintEndWib":"2026-11-14 17:01:08 WIB",
 "mintOpen":1,"soldOut":0,"revealed":0,
 "ageHoursAtTriage":0.3,"ageVerified":True,
 "ageNote":"mintStart on-chain 17:01:08 WIB 2026-11-09 = Sourcify verifiedAt 17:01 WIB; first mints terverifikasi on-chain (totalMinted 90, freeMinted 80, blok 132566185).",
 "freeSlotUserOpen":"kemungkinan terbuka (freeUsed(user)=0, balanceOf(user)=0); quote belum dibaca (signature quote belum dipetakan)",
 "freeUsed_user":0,"balanceOf_user":0,
 "ownerNote":"owner() mengembalikan address(0); deployer belum dipetakan; kontrak TIDAK ada di same-owner-discards.json.",
 "contractInDiscards":False,
 "lastReadBlock":132566185,"lastReadWib":"2026-11-09 17:2x WIB",
 "velocityLegPasses":False,
 "reportedOnceWib":"2026-11-09 ~17:5x WIB (EARLY LEAD, run 1631)",
 "note":"EARLY LEAD run 1631. Agent-shaped TERverifikasi (Sourcify exact_match + AGENT_ID_REGISTRY persis + free views + mintOpen). First mints terverifikasi on-chain (90 total, 80 free). Free 7,2% (<25% -> BUKAN strong lead). Website TERverifikasi (marbleworks.surge.sh). TIDAK pernah preview/mint."}
# ---- 3. Flare Agent (watchlist-only) ----
contracts["Flare Agent"]={
 "address":"0xe2deb47514bbfd19550866c8820bce04e8a8d416",
 "status":"watchlist-only-age-unverified-2026-11-09",
 "name":"Flare Agent","kind":"ERC721",
 "source":"Boltbook front page EN+ZH + post /p/FcZExJK3gUSf (dieuduong369.ai, 16:56 WIB), run 1631 discovery",
 "website":None,"websiteVerified":False,
 "websiteNote":"TIDAK ditemukan: (A) pencarian alamat kontrak tanpa hasil situs; (G) pencarian nama proyek tanpa situs; (H) contractURI() None/revert; post Boltbook tanpa tautan situs.",
 "xHandle":None,"xVerified":False,
 "sourcify":"UNVERIFIED",
 "totalSupply":9901,"totalMinted":9901,"MAX_SUPPLY":10000,
 "freePctInference":99.0,
 "freePctNote":"Inferensi: totalSupply 9901/MAX_SUPPLY 10000; post Boltbook klaim 9.901/10.001 free (cap 10.001 vs MAX on-chain 10.000 — selisih 1 belum dijelaskan). TIDAK ada free view on-chain (freeClaimed/freeMinted/FREE_SUPPLY semua revert).",
 "price":1000000000000000,
 "priceNote":"price() = 0,001 BNB — jalur berbayar ada; fungsi free entry BELUM teridentifikasi (bytecode hanya punya selector mint(uint256) + price() yang dikenal; tanpa freeMint/mintFree/claimFree/freeClaimed).",
 "registryBytesHit":True,
 "ageVerified":False,"ageNote":"mintStart view tidak ada (revert); umur TIDAK terverifikasi.",
 "freeSlotUserOpen":"UNVERIFIED (fungsi klaim gratis belum dipetakan; balanceOf(user)=0)",
 "balanceOf_user":0,
 "lastReadBlock":132565791,"lastReadWib":"2026-11-09 17:1x WIB",
 "velocityLegPasses":False,
 "note":"Watchlist-only run 1631. Agent-shaped via registry bytes, 99% ter-mint, ~99 slot tersisa per post — TAPI umur unverified + slot user unverified + website tidak ditemukan -> BUKAN strong lead/kandidat, TIDAK pernah preview/mint. Pantau: bila sold out, hapus + catat."}
# ---- 4. checked-not-lead ----
contracts["0xb79BA612aBe9BB82e727AB394b2c094C6507d76d"]={
 "address":"0xb79BA612aBe9BB82e727AB394b2c094C6507d76d","status":"checked-not-lead-2026-11-09",
 "source":"Sourcify feed run 1631 discovery (verifiedAt 2026-11-09T10:03:02Z)",
 "sourcify":"verified (AGENT_REGISTRY, mint, quote, spotsLeft, totalSpotsMinted, MAX_SPOTS, PRICE, PER_SPOT)",
 "AGENT_REGISTRY":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
 "spotsLeft":4999,"totalSpotsMinted":1,"MAX_SPOTS":5000,"PRICE":500000000000000,"PER_SPOT":200000000000000000000000,
 "note":"Agent-gated spot sale (token, mint+quote, registry persis) TAPI TIDAK ada free-share view -> BUKAN track C (S1 butuh free view), BUKAN track A. Paid-only (0,0005 BNB/spot). Tidak masuk watchlist aktif.",
 "lastReadWib":"2026-11-09 17:2x WIB"}
contracts["0x448f01b6366b333e3e8046645c35181FFF51De5b"]={
 "address":"0x448f01b6366b333e3e8046645c35181FFF51De5b","status":"checked-not-lead-2026-11-09",
 "source":"Sourcify feed run 1631 discovery (verifiedAt 2026-11-09T10:01:14Z)",
 "sourcify":"verified (template sama dengan 0xb79BA612: AGENT_REGISTRY, mint, quote, spotsLeft, MAX_SPOTS, PRICE, PER_SPOT)",
 "AGENT_REGISTRY":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
 "spotsLeft":4999,"totalSpotsMinted":1,"MAX_SPOTS":5000,"PRICE":500000000000000,"PER_SPOT":200000000000000000000000,
 "note":"Agent-gated spot sale, template sama dengan SPOT-A; TIDAK ada free-share view -> BUKAN track C, BUKAN track A. Paid-only (0,0005 BNB/spot). Tidak masuk watchlist aktif.",
 "lastReadWib":"2026-11-09 17:2x WIB"}
contracts["0x57cf26c69fC9171937BA47164a3F8F451FD85B20"]={
 "address":"0x57cf26c69fC9171937BA47164a3F8F451FD85B20","status":"checked-not-lead-2026-11-09",
 "source":"Sourcify feed run 1631 discovery (verifiedAt 2026-11-09T10:02:56Z)",
 "sourcify":"verified (BUY_TAX_BPS, burnFromPair, enableTrading, wbnb — token tax, bukan agent-shaped)",
 "note":"ERC-20 tax/burn, mint tanpa registry/AgentGate/free view -> BUKAN track C, BUKAN track A. Tidak masuk watchlist aktif.",
 "lastReadWib":"2026-11-09 17:2x WIB"}
contracts["0x9ecEb8B0081b9df25fF271bF24735d6Dea671D78"]={
 "address":"0x9ecEb8B0081b9df25fF271bF24735d6Dea671D78","status":"checked-not-lead-2026-11-09",
 "source":"Sourcify feed run 1631 discovery (verifiedAt 2026-11-09T09:59:24Z)",
 "sourcify":"verified (Chainlink ACE factory — *_FACTORY, deploy)",
 "note":"Infrastruktur Chainlink (factory validator), BUKAN proyek mint/sale. Tidak masuk watchlist aktif.",
 "lastReadWib":"2026-11-09 17:2x WIB"}
contracts["0x391D7b854b6152a201A3D83Ec2B83b4FC141C03C"]={
 "address":"0x391D7b854b6152a201A3D83Ec2B83b4FC141C03C","status":"checked-not-lead-2026-11-09",
 "source":"Sourcify feed run 1631 discovery (verifiedAt 2026-11-09T09:57:57Z)",
 "sourcify":"verified (distribute, ratios, usdt — distributor)",
 "note":"Distributor USDT (bukan mint/sale, tanpa registry/free view). Tidak masuk watchlist aktif.",
 "lastReadWib":"2026-11-09 17:2x WIB"}
# ---- 5. track_c notes (unchanged) ----
if "NIBULL" in tc and isinstance(tc["NIBULL"],dict):
    tc["NIBULL"]["note1631_1109"]="Run 1631: tanpa perubahan vs 1601 (totalSupply sama, freeMinted None, freeSharesRemaining None, balanceOf_user 0). opened=0, soldShares tidak dibaca ulang run ini (nilai terakhir 1257). Tetap watchlist-only-upcoming; BUKAN lead."
    report["track_c_notes"]["NIBULL"]="tanpa perubahan vs 1601."
if "NUSA" in tc and isinstance(tc["NUSA"],dict):
    tc["NUSA"]["note1631_1109"]="Run 1631: freeMinted tetap 348 (sama dengan 1601). Tetap track-c-lead-reported; tanpa perubahan."
    report["track_c_notes"]["NUSA"]="freeMinted tetap 348."
if "ORDIagent" in tc and isinstance(tc["ORDIagent"],dict):
    tc["ORDIagent"]["note1631_1109"]="Run 1631: semua view tetap None (baca gagal/transport); sale buka 17:00 WIB hari ini — sudah lewat, tapi belum ada data; pantau run berikut."
    report["track_c_notes"]["ORDIagent"]="tetap tanpa data; buka 17:00 WIB sudah lewat."
# ---- 6. final run notes ----
snap["runNote1631_1109"]=(
 f"Run 1631 STAGE 2: re-read {len(r1631.get('reread', {}))} kontrak + {len(r1631.get('track_c', {}))} track_c "
 f"(blok {BLOCK}, interval {m1.get('interval_minutes')} mnt vs run 1601); "
 f"velocity LOLOS 0 — promosi 0. "
 f"Age-exclusions baru: 1 (Ink Koi 0xbd4B4e7189ae9356514664146b0eD683601200A9, umur ~48,1 jam, belum sold out, totalSupply 2362 — DIHAPUS dari snapshot, dilaporkan sekali). "
 f"Scan GAGAL CEPAT: Ankr pre-flight gagal 3x (transport + RemoteDisconnected + HTTP 401 6 dtk) — watermark TIDAK dimajukan (tetap 132512564, gap ~52.482 blok ke head 132565046). "
 f"Binanceai tetap refund/failed (launched=0, failed=1, isRefundPhase=1, probe ~17:04 WIB). Bridge tidak berubah (mtime 2026-11-08 18:21 UTC; 116 kontrak; 8 tidak ada di snapshot — sudah ditriase bukan lead). "
 f"Discovery: 1 EARLY LEAD BARU — Marbleworks (free 80/1111 = 7,2%, umur ~0,3 jam, website marbleworks.surge.sh terverifikasi); 1 watchlist-only baru — Flare Agent (99% ter-mint, umur/slot/website unverified); PAWG TERverifikasi sold out 3.333/3.333 (bukan lead job ini, log saja); 5 checked-not-lead dari feed Sourcify. "
 f"EKSEKUSI: 1 — Skunk Hollow #708 strong-lead direct mint BERHASIL (tx 0xe211754b03124c54be9ecb4fc0555aa94314b34421c09cf7e862283349ccb3d1, blok 132568173, receipt 1).")
snap["runNote1631_1109_scan"]=(
 f"Run 1631 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok, 3 attempts: "
 f"ATTEMPT 1 (blok 132564878-132564927) FAIL traceback/transport; ATTEMPT 2 (blok 132564930-132564979) FAIL RemoteDisconnected; "
 f"ATTEMPT 3 (blok 132564997-132565046, head 132565046) FAIL 6 dtk HTTP 401 Unauthorized (credential custom.ankr ditolak rpc.ankr.com; outage sejak ~13:33 WIB). "
 f"Scan leg TIDAK dijalankan (amendment 2026-11-06: pre-flight gagal = fast-fail, lanjut route lain). Watermark tetap 132512564; "
 f"gap ke head 132565046 ~52.482 blok dan tumbuh (milik backfill, ikut gagal 401). Tidak ada first-seen baru dari scan; route 5c tanpa output scan baru (0 sale-shape).")
snap["runNote1631_1109_binanceai"]=(
 "Run 1631 (probe dataseed ~17:04 WIB): binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
 "totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0. Sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote1631_1109_age_exclusions"]=(
 f"Run 1631 stage 1: age-exclusions baru: {json.dumps(m1.get('age_exclusions',[]))}; "
 f"kept (sold out, age N/A): {json.dumps(m1.get('age_candidates_kept',[]))}. Ink Koi (early lead backfill 2026-11-07, dilaporkan ~18:0x WIB 7 Nov) "
 f"melewati 48 jam pada ~17:13 WIB hari ini dan belum sold out (totalSupply 2362/2777) -> DIHAPUS dari snapshot sesuai aturan umur; dilaporkan sekali.")
snap["runNote1631_1109_early_leads"]=(
 "Run 1631 EARLY LEAD (dilaporkan sekali ke main chat): Marbleworks (MWORKS) 0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0 — "
 "free 80/1111 (7,2%), mintStart 17:01:08 WIB 2026-11-09 (umur ~0,3 jam, terverifikasi on-chain + Sourcify verifiedAt 17:01 WIB), "
 "slot user kemungkinan terbuka (freeUsed=0), website marbleworks.surge.sh TERverifikasi (tokenURI external_url + situs mencetak kontrak persis), "
 "Sourcify exact_match + AGENT_ID_REGISTRY persis, X belum diketahui. BUKAN strong lead (7,2% < 25%). TIDAK pernah preview/mint.")
snap["runNote1631_1109_mint"]=(
 "Run 1631 MINT — Skunk Hollow #708 (STRONG-LEAD DIRECT MINT, otorisasi 2026-11-02): "
 "free 707/2500 (28,28% >=25%), umur terverifikasi gateStart 2026-11-08 19:00:15 WIB (~22,8 jam), slot user TERBUKA (freeClaimedBy=0), "
 "website TERverifikasi skunkhollow.netlify.app (tokenURI -> meta host + config.js mencetak kontrak persis), X @BnbSkunk (dari config situs, profil belum dibaca). "
 "Audit Binance: hasResult=false (tidak ada hasil, BUKAN lolos), tanpa hit RISK. Same-owner: kontrak + devWallet 0x7e1c68c6... TIDAK ada di discards. "
 "Preview bersih (simulationCode 000000000, value 0, tanpa authority/allowance/risk; +1 ERC721 tokenId 708). "
 "Eksekusi claimFree(address(0)) value 0: tx 0xe211754b03124c54be9ecb4fc0555aa94314b34421c09cf7e862283349ccb3d1, blok 132568173, gas 223.809, receipt status 1; "
 "verifikasi: balanceOf(user)=1, freeClaimedBy(user)=1, freeSkunksClaimed 708, tokenOfOwnerByIndex(user,0)=708. "
 "Pasca-mint: TIDAK ada own market live (situs tidak menautkan market; NFT bisa ditransfer/dijual tapi tanpa venue) -> TIDAK di-listing (aturan auto-list); "
 "rarity #708 TIDAK terverifikasi (tokenURI(708) revert; metadata #1 bertier 'Unrevealed'). Jendela free tutup 19:00:15 WIB hari ini.")
snap["last_run"]="1631"
snap["last_run_wib"]="2026-11-09 ~17:5x WIB"
snap["last_run_note"]=("Run 1631: 1 mint berhasil (Skunk Hollow #708, strong-lead direct mint); 1 early lead baru (Marbleworks); "
                       "1 age-exclusion (Ink Koi, dihapus); Flare Agent watchlist-only; scan fast-fail Ankr 401 (watermark tetap 132512564); "
                       "binanceai tetap refund; PAWG sold out (bukan lead).")
snap["timestamp_wib"]="2026-11-09 17:5x WIB"
def save_atomic(path,obj):
    tmp=path+".tmp"
    with open(tmp,"w") as f: json.dump(obj,f,indent=1)
    os.replace(tmp,path)
save_atomic(f"{HF}/onchain-snapshot.json",snap)
json.dump(report,open(f"{HF}/run-2026-11-09-1631-merge-stage2.json","w"),indent=1)
print("MERGE STAGE 2 DONE. contracts now:",len(snap["contracts"]))
print("mint:",report["mint_executed"],"early:",report["early_leads_new"],"watchlist:",report["watchlist_only_new"])
