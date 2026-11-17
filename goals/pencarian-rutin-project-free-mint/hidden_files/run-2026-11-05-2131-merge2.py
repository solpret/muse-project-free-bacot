#!/usr/bin/env python3
"""FREE BACOT main run 2026-11-05 2131 — parent merge PART 2 (scan/B findings).
Run AFTER merge part 1. Adds: PRDICT track-C lead, 2 early leads (APERP,
AWNFT), 4 paid-only watchlist-only, 4 non-agent watchlist-only, MirrorPair
excluded-bookkeeping, scan notes. PRDICT gate verdict is filled in by parent
after the BscScan browser read (method L); edit PRDICT_GATE below first.
No preview/mint. Read-only on-chain except snapshot writes."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"

# --- FILL IN AFTER BscScan (L) RESULT ---
PRDICT_GATE = "FAILED"   # "FAILED" or "PASSED"
PRDICT_GATE_NOTE = (
    "MANDATORY WEBSITE GATE GAGAL run 2131: (A) pencarian alamat kontrak mentah nihil; "
    "(B) Boltbook front page EN+ZH 0 penyebutan Predictagent/PRDICT; (C) Sourcify metadata/source/files "
    "404 semua endpoint v2 yang dicoba (bukan bukti tidak ada repo — keterbatasan endpoint); "
    "(D) pola same-family vercel/pages/deed nihil; (G) pencarian nama 'Predictagent' nihil (hanya proyek "
    "Predict predict.fun yang besar + unrelated); (H) contractURI() tidak ada (None); (I) tokenURI tidak "
    "ada di ABI (ERC-20); (J) grep ABI: tanpa fungsi website/twitter/site/url/domain/external; "
    "(K) GitHub code search via search-index nihil; (L) BscScan token page via live browser (22:29-22:38 WIB, "
    "setelah pemulihan Cloudflare): halaman termuat, token Predictagent (PRDICT) BEP-20, Max Total Supply "
    "1.000.000.000, Holders 138, Transfers 138 — tab Info HANYA menampilkan 'Click here to update the token "
    "information', TIDAK ADA field Website/Social/Official dan TIDAK ADA URL proyek apa pun; tautan X di footer "
    "adalah milik BscScan, bukan proyek; "
    "(M) pencarian alamat owner 0x339df8fa35078dfb947e8cd1e2a85da62cd17ecb nihil; (N) registry balanceOf(owner)=0 "
    "(owner tidak memegang Agent ID, tidak ada hop profil). X tidak dicari (opsional, bukan blocker). "
    "TIDAK di-preview, TIDAK di-mint. Bila website terverifikasi ditemukan kemudian, lead dibuka lagi di bawah "
    "TRACK-C LEAD DIRECT MINT (gate + semua safety segar)."
)
PRDICT_STATUS = "track-c-lead-gate-blocked-2026-11-05"

s = json.load(open(f"{BASE}/onchain-snapshot.json"))
contracts = s.setdefault("contracts", {})
excluded = s.setdefault("excluded", {})
tc = s.setdefault("track_c", {})

# ---- PRDICT track-C S1 lead (gate verdict above) ----
tc["Predictagent-PRDICT"] = {
    "sale": "0x8fF4bd65584882324c44Ee794a23E7791820189b",
    "token": "0x8fF4bd65584882324c44Ee794a23E7791820189b",
    "name": "Predictagent",
    "symbol": "PRDICT",
    "status": PRDICT_STATUS,
    "saleShape": "PASS (S1): mint + quote(address,uint256) + freeLeft(address) + AGENT_ID()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; Sourcify verified (feed run 2131, verifiedAt 2026-11-05T14:50:25Z); kontrak ITU tokennya (ERC-20, totalSupply 1e27 = 1 miliar token)",
    "mintOpen": True,
    "FREE_PER_WALLET": 1,
    "MAX_MINTS": 1000,
    "totalMints": 128,
    "MINT_AMOUNT": 1000000000000000000000000,
    "PRICE": 150000000000000,
    "userSlot": {"freeLeft": 1, "quote1": 0, "quote2": 150000000000000, "mintedBy": 0, "balanceOf": 0},
    "ageNote": "VERIFIED <=48h: first Transfer blok 131835618 = 2026-11-05 21:49:35 WIB (Ankr getLogs, from-zero ke kontrak); umur ~15 mnt saat deteksi, ~45 mnt saat gate check. Sourcify verifiedAt 21:50:25 WIB.",
    "gateNote": PRDICT_GATE_NOTE,
    "gatePassed": PRDICT_GATE == "PASSED",
    "firstSeenBlock": 131835618,
    "firstMintWib": "2026-11-05T21:49:35+07:00",
    "lastReadBlock": 131837412,
    "lastReadWib": "2026-11-05 run 2131",
    "owner": "0x339df8fa35078dfb947e8cd1e2a85da62cd17ecb",
    "boundary": "LEAD (bukan kandidat: tanpa diskusi publik terverifikasi + gate website GAGAL). TIDAK di-preview/di-mint run ini (gate gagal).",
}
print("PRDICT added to track_c, gate:", PRDICT_GATE)

# ---- Early leads (scan first-seen, agent-shaped, first mints verified) ----
contracts["AGENTIC PERP"] = {
    "address": "0xf1CE53a4BA97a9BaE4b6CBd15f917D42983a4fBB",
    "name": "AGENTIC PERP", "symbol": "APERP", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-05",
    "totalSupply": 35, "totalMinted": 35, "MAX_SUPPLY": 5000,
    "FREE_PER_WALLET": 1, "freeMinted_user": 0,
    "freePctVerified": None,
    "mintOpen": None,
    "userBalance": 0,
    "firstSeenBlock": 131835558,
    "firstMintWib": "2026-11-05T21:49:08+07:00",
    "scanWindow": "131835334-131837333",
    "scanMints": 6, "scanMinters": 6,
    "launchNote": "First mint TERVERIFIKASI on-chain blok 131835558 = 2026-11-05 21:49:08 WIB. Umur TERVERIFIKASI <=48 jam.",
    "baselineNote": "EARLY lead dilaporkan sekali run 2131. Agent-shaped STRICT: agentRegistry() on-chain = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F + registry bytes di code. Bukti gratis KUAT: FREE_PER_WALLET=1, freeMinted(user)=0, 3 tx mint sampel value 0 (gas-only), tanpa PRICE/quote fn di bytecode. Free % UNVERIFIED (tidak ada free-cap view yang merespons: FREE_SUPPLY/freeSupply/FREE_CAP/maxFree/dll semua null). Slot user TERBUKA. BUKAN strong lead (free % unverified), BUKAN kandidat (X unverified, velocity baseline pertama). TIDAK PERNAH auto-mint/preview sebagai early.",
    "xVerified": False, "velocityVerified": False,
    "previousTotalSupply": 35, "currentRatePerMin": None, "previousRatePerMin": None,
    "lastReadBlock": 131837412, "lastReadWib": "2026-11-05 run 2131",
}
contracts["Agent Wallet"] = {
    "address": "0x1aeEf8218815F7639eA3544D5c57122675A00805",
    "name": "Agent Wallet", "symbol": "AWNFT", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-05",
    "totalSupply": None, "nextTokenId": 11,
    "freePctVerified": None,
    "userBalance": 0,
    "firstSeenBlock": 131836550,
    "firstMintWib": "2026-11-05T21:56:35 WIB",
    "scanWindow": "131835334-131837333",
    "scanMints": 2, "scanMinters": 2,
    "launchNote": "First mint TERVERIFIKASI on-chain blok 131836550 = 2026-11-05 21:56:35 WIB. Umur TERVERIFIKASI <=48 jam.",
    "baselineNote": "EARLY lead dilaporkan sekali run 2131. Agent-shaped: registry() on-chain = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F + Sourcify verified; ERC-6551 token-bound account NFT; mint(uint256 agentId) NONPAYABLE (gratis, gas-only); agentIdMinted mapping ada. Slot user UNVERIFIED (butuh nomor Agent ID user; registry balanceOf(user)=1 tapi agentIdOf/getAgentId revert). Free % UNVERIFIED (tidak ada free cap). BUKAN strong lead (slot + % unverified), BUKAN kandidat. TIDAK PERNAH auto-mint/preview sebagai early.",
    "xVerified": False, "velocityVerified": False,
    "previousTotalSupply": None, "currentRatePerMin": None, "previousRatePerMin": None,
    "lastReadBlock": 131837412, "lastReadWib": "2026-11-05 run 2131",
}
print("early leads added: AGENTIC PERP, Agent Wallet")

# ---- Paid-only watchlist-only (agent-shaped, no free lane, PRICE>0) ----
PAID_ONLY = [
 ("Crimson Eclipse", "0x0d37F4cc06c5d0F74DDE1C29e4986F3050e85c48", "ECLIPSE", 1111, "2026-11-05T21:50:04+07:00", 131835682,
  "AGENT_ID()=registry; mint() payable, mintPrice ~0,00012-0,00049 BNB (dua bacaan berbeda, keduanya >0), hasMinted(user)=0, tanpa free view; tokenURI(1) SVG on-chain."),
 ("Bastion Ibis Agent", "0x4AF921C0c0ea153490875432D9Ba05FB98Df356D", "BASI", 3333, "2026-11-05T22:01:42+07:00", 131837233,
  "AGENT_REGISTRY()=registry; PRICE/quote(1)=0,0005 BNB, totalMinted 1 (mint tunggal ke owner/treasury 0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5), tanpa free view; BASE_URI ipfs://sniper-test-nft/."),
 ("Umbra Nomad Agent", "0xe43D6AEE91E74a0FC8804d1568d3677014dB51d4", "UMBN", 3333, "2026-11-05T21:56:27+07:00", 131836533,
  "AGENT_REGISTRY()=registry; PRICE/quote(1)=0,0005 BNB, totalMinted 1 (mint tunggal ke owner), tanpa free view; template sama dengan BASI."),
 ("Neural Sovereign", "0x36b099A42FDeC0eF89D1C5752aAB0D3924716067", "NRSV", 3333, "2026-11-05T21:51:12+07:00", 131835834,
  "AGENT_REGISTRY()=registry; PRICE=0,0005 BNB, spotsLeft 3332, totalMinted 1, tanpa free view; template sama dengan BASI."),
]
for name, addr, sym, maxs, fmw, fb, ev in PAID_ONLY:
    contracts[name] = {
        "address": addr, "name": name, "symbol": sym, "kind": "ERC721",
        "status": "watchlist-only-paid-only-2026-11-05",
        "totalMinted": 1, "MAX_SUPPLY": maxs,
        "firstSeenBlock": fb, "firstMintWib": fmw,
        "scanWindow": "131835334-131837333", "scanMints": 1, "scanMinters": 1,
        "launchNote": f"First mint TERVERIFIKASI on-chain blok {fb} = {fmw}. Umur TERVERIFIKASI <=48 jam.",
        "baselineNote": f"BUKAN early lead (PAID-ONLY, preseden run 2101): {ev} BUKAN kandidat, TIDAK di-preview/di-mint.",
        "xVerified": False, "velocityVerified": False,
        "lastReadBlock": 131837412, "lastReadWib": "2026-11-05 run 2131",
    }
print("paid-only watchlist-only added:", len(PAID_ONLY))

# ---- Non-agent-shaped first-seen (watchlist-only, not early) ----
NONAGENT = [
 ("Agent Pirate Ship", "0x9f68B9b69938813aE69166140971034d38CAEA73", "APS", 81, 81, 131835344),
 ("NX-NFT", "0x2e124D168740eb9B0e83c382C37c6D6985de0113", "NX-NFT", 60, 1, 131837023),
 ("Dewata", "0x13628D733A26b942213BA1b3C61471925D4a2165", "DEWA", 19, 19, 131835456),
 ("AIPRO", "0xe86c2E52A5Ebaf4afd18020834D5c771Aff59cDE", "AIPRO", 1, 1, 131835342),
]
for name, addr, sym, mc, dm, fb in NONAGENT:
    contracts[name] = {
        "address": addr, "name": name, "symbol": sym, "kind": "ERC721",
        "status": "watchlist-only-scan-first-read-2026-11-05",
        "firstSeenBlock": fb, "scanWindow": "131835334-131837333",
        "scanMints": mc, "scanMinters": dm,
        "launchNote": f"First-seen scan run 2131 (blok {fb} hanya batas bawah, BUKAN waktu peluncuran). Umur peluncuran UNVERIFIED.",
        "baselineNote": "BUKAN early lead: tanpa registry hit, Sourcify not_verified, tanpa free shape (nama saja bukan bukti agent-shaped). Dicatat watchlist-only agar tidak di-triage ulang.",
        "xVerified": False, "velocityVerified": False,
        "lastReadBlock": 131837412, "lastReadWib": "2026-11-05 run 2131",
    }
print("non-agent watchlist-only added:", len(NONAGENT))

# ---- MirrorPair bookkeeping (reported early 2026-11-02-0031, never entered snapshot) ----
excluded["MirrorPair"] = {
    "address": "0x27cD34C8A5cc9376030f44d5fEc1a3DCCEeCa2a3",
    "name": "MirrorPair", "kind": "pairing-contract",
    "status": "excluded-age-over-48h-2026-11-05",
    "website": "https://mirrorpair.pages.dev/",
    "post": "https://boltbook.ai/post/1163",
    "exclusionNote2131": ("Bookkeeping run 2131: dilaporkan sebagai EARLY lead run 2026-11-02-0031 (post mirrorpair "
        "2026-11-01T14:41:52Z: 2.222 pairs, first pairing free) tapi TIDAK PERNAH masuk snapshot contracts/excluded "
        "(celah bookkeeping run lama). Post 2026-11-01 + first pairings diklaim launch night 2026-11-01 -> umur >48 jam "
        "saat run ini (~4 hari); pairing contract (bukan solo NFT mint); author page dibaca ulang run ini: hanya post 1163, "
        "tanpa post/komentar baru, tanpa fase mint baru terverifikasi. Dicatat di excluded agar tidak dilaporkan ulang. "
        "Verifikasi parent run ini: eth_getCode ada (30.664 byte); totalSupply/free views tidak merespons (bukan kontrak mint NFT)."),
}
print("MirrorPair added to excluded")

s["runNote2131_scan"] = (
    "Scan run 2131 SUKSES: window 131835334-131837333 (2000 blok, cap; head 131837307, watermark 131830889, "
    "window 6418 blok), 80 panggilan Ankr, 0 error, ~16 mnt (22:02-22:18 WIB). 250 kontrak NFT (2036 mint), "
    "788 ERC-20. Watermark 131830889 -> 131837333; seen 8619 -> 9001 (+382 = 10 NFT + 372 ERC-20). "
    "Gap dilewati 131830890-131835333 (4444 blok); gap kumulatif sejak run 1831 ~23.689 blok (struktural, cap 2000/run). "
    "5c: ERC-20 mint_count>=10 ada 90; sudah dicek 49; dicek run ini 20; 0 lolos S1/S2; 21 dibuang sebagai sampling limit. "
    "2 kontrak registry-bytes tapi gagal bentuk: 0x4008a353... (573 mint) dan 0xFB658ADD... (27 mint). "
    "Feed Sourcify: 1 S1 (PRDICT), 0 S2, 3 agent-mint NFT (BASI/UMBN/NRSV — paid-only). "
    "Catatan infra: Ankr public RPC (rpc.ankr.com/bsc) kini menolak tanpa API key (Unauthorized -32000); scan tetap sukses "
    "via modul Ankr get_logs + dataseed Binance untuk eth_blockNumber.")
s["last_run_note"] = "Run 2131: placeholder — parent isi setelah merge part 2."

json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("MERGE PART 2 DONE: contracts now", len(s["contracts"]), "| excluded now", len(s["excluded"]), "| track_c now", len(s["track_c"]))
