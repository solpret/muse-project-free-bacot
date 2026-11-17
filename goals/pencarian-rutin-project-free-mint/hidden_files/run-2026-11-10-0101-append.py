#!/usr/bin/env python3
"""Append run 0101 new watchlist items (Zigzoo, VISION) + PXMON free% fix to snapshot.
No status changes to reported items; no deletions."""
import json, datetime
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
# --- Zigzoo (Boltbook baru run ini) ---
snap.setdefault("contracts",{})["Zigzoo"]={
 "address":"0x09ada5a12293c30d75b97c56e34967e8a4326a3c","name":"Zigzoo","symbol":"ZIGZOO","kind":"ERC721",
 "status":"watchlist-only-age-unverified-2026-11-10",
 "totalSupply":1214,"totalMinted":None,"freeClaimed":None,"freeMinted":None,"FREE_SUPPLY":None,"FREE_CAP":None,
 "MAX_SUPPLY":5000,"mintOpen":None,"mintActive":1,"currentPrice":0,"priceForCount_1":200000000000000,
 "mintCount_user":0,"holdsAgentId_user":True,
 "agentIdRegistry":"0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "owner":"0x262e8e5e4584d8ab840fd950a6e2e0a414d4097","owner_in_discards":False,
 "balanceOf_user":0,"freeClaimed_user":None,"freePctVerified":None,
 "website":None,"xVerified":False,
 "sourcifyVerifiedAt":"2026-11-06T13:28:21Z",
 "firstSeenBlock":132629446,"lastReadBlock":132629446,"lastReadWib":NOW_WIB,
 "discovery":"Boltbook front page run 0101 (post raulzyan.ai ~01:00 WIB 2026-11-10): 'Zigzoo (ZIGZOO, BSC): 5,000 cap, 1 per wallet, mint at 0 BNB, gas only, behind an Agent-ID gate. Contract 0x09ada5... No official site turned up in our research'. Pace 1,2/jam.",
 "launchNote":("Umur peluncuran UNVERIFIED: kontrak tanpa view mintStart/START_TIME; Sourcify verifiedAt 2026-11-06T13:28:21Z (bukan launch time); "
   "koroborasi first-mint via Ankr getLogs tidak bisa (401 sejak 2026-11-09 ~13:33 WIB) dan via historical eth_call/eth_getCode tidak bisa (dataseed publik 'missing trie node' - pruned). "
   "Pace 1,2/jam di post vs 1214 minted tidak konsisten dengan launch baru."),
 "gateNote":("Website gate FAILED (sementara): tidak ada situs proyek ditemukan - post Boltbook sendiri menyatakan tidak ada situs; metode A/G tanpa hasil. "
   "BUKAN lead/kandidat/strong (umur + free% unverified, tanpa website); watchlist-only, TIDAK preview/mint, TIDAK dilaporkan sebagai lead."),
 "runNote0101_1110":"Run 0101: BARU di snapshot (Boltbook). totalSupply 1214/5000, mintActive 1, currentPrice 0, priceForCount(1) 0,0002 BNB, mintCount(user)=0, holdsAgentId(user)=1, registry Binance persis. Free% UNVERIFIED (tanpa free view). Website TIDAK ditemukan. Watchlist-only."
}
# --- VISION (track_c, AirdropBuzz + route 3) ---
snap.setdefault("track_c",{})["VISION"]={
 "sale":"0x5f76cab7b054e088563d5098e17bd0dc430e61ae","token":"0x5f76cab7b054e088563d5098e17bd0dc430e61ae",
 "address":"0x5f76cab7b054e088563d5098e17bd0dc430e61ae","name":"VISION","symbol":"VSN",
 "shape":"S1+S2 (single-contract token+sale)","status":"watchlist-only-age-unverified-2026-11-10",
 "MAX_SHARES":100000,"totalShares":393,"totalFreeShares":393,"totalPaidShares":0,"totalSupply":709200000000000000000000000,
 "TOKENS_PER_SHARE":1000000,"PRICE":1000000000000000,"BASE_QUOTA":10,"MAX_PER_TX":10,"totalRaised":0,
 "agentIdRegistry":"0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "isAgent_user":True,"freeUsed_user":0,"sharesOf_user":0,"quotaOf_user":10,"balanceOf_user":0,
 "quote_user_1":{"freeShares":1,"costBnb":0},
 "freePoolRemaining":99607,
 "website":"https://vision-vsn.pages.dev",
 "websiteGate":"PASSED - situs proyek sendiri mencetak kontrak persis 0x5f76cab7b054e088563d5098e17bd0dc430e61ae di /skill.md dan config.js (+ registry 0x60B926...22F).",
 "xVerified":False,
 "sourcifyMatch":"exact_match","sourcifyVerifiedAt":"2026-11-09T13:41:15Z",
 "firstSeenBlock":132630094,"lastReadBlock":132630094,"lastReadWib":NOW_WIB,
 "discovery":"Route 3 sweep run 0101: AirdropBuzz 'Free Agent ID Mints: VISION & JOLT Checks' (checked 9 Nov 2026, blok 132621755, 182 shares, semua free). Site vision-vsn.pages.dev (mint page + /skill.md + config.js).",
 "launchNote":("Umur peluncuran UNVERIFIED: kontrak tanpa view start/end time; Sourcify verifiedAt 2026-11-09T13:41:15Z (bukan launch time); "
   "observasi pertama AirdropBuzz 9 Nov ~17:05 UTC (182 shares) bukan waktu launch proyek; koroborasi first-mint via Ankr getLogs tidak bisa (401) "
   "dan via historical eth_call/eth_getCode tidak bisa (dataseed publik 'missing trie node' - pruned, terverifikasi 3 node). "
   "Jendela batas: deploy ~13:41 UTC 9 Nov s.d. observasi 17:05 UTC 9 Nov - keduanya <48 jam dari run, TAPI bukan waktu launch terverifikasi."),
 "gateNote":("Semua kaki lead KECUALI umur TERVERIFIKASI: S1+S2 lolos (mint+quote+freeUsed/totalFreeShares+agentIdRegistry), free pool 99.607 tersisa, "
   "quote(user,1) = 1 free share / cost 0, website gate PASSED. HANYA umur yang unverified -> watchlist-only-age-unverified, BUKAN lead, TIDAK preview/mint. "
   "Bila umur terverifikasi <=48 jam di run berikut (Ankr pulih / proyek menyatakan launch time), promosi ke lead + direct mint mengikuti aturan track-C."),
 "runNote0101_1110":"Run 0101: BARU di track_c (watchlist-only, umur unverified). totalShares 393/100000 (semua free), quote(user,1) free 1 / cost 0, isAgent(user)=1, freeUsed(user)=0. Website gate PASSED. TIDAK preview/mint (umur unverified)."
}
# --- PIXEL MONSTERS free% fix (freeMinted 530/2000; FREE_SUPPLY tidak terbaca LEAN) ---
px=snap.get("contracts",{}).get("PIXEL MONSTERS")
if isinstance(px,dict) and isinstance(px.get("freeMinted"),int):
    px["freePctVerified"]=round(100.0*px["freeMinted"]/2000,2)
    px["runNote0101_1110"]=(px.get("runNote0101_1110","")+" freePct dikoreksi 26,5% (freeMinted 530/2000). Status tetap strong-lead-gate-failed-2026-11-10 (sudah dilaporkan run 0031; TIDAK dilaporkan ulang).")
snap["runNote0101_1110_append"]=(f"Run 0101 append ({NOW_WIB}): Zigzoo BARU watchlist-only (contracts); VISION BARU watchlist-only-age-unverified (track_c); "
  "PIXEL MONSTERS freePct 26,5% (530/2000). Arachnoir free sold out 805/805 - status promotion-discarded-same-owner dipertahankan, log saja.")
with open(f"{BASE}/onchain-snapshot.json","w") as f: json.dump(snap,f,indent=1)
print("APPENDED Zigzoo + VISION; PXMON freePct =", snap["contracts"]["PIXEL MONSTERS"].get("freePctVerified"))
