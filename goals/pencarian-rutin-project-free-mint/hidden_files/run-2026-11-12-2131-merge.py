#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-12 21:31 WIB.
Reads run-2026-11-12-2131-verify.json + run-2026-11-12-2131-retry-new.json, updates onchain-snapshot.json:
- re-read targets: supply/free/lastRead + runNote2131_1112
- BUCKET age-exclusion (verified launch >=24h, not sold out, reported once as early lead)
- ADD SolNFT + AgcNFT as early-lead-reported-2026-11-12 (agent-shaped + first mints verified
  on-chain via single-call retry; age VERIFIED <24h via mintOpensAt on-chain; free% 2.7%/12.9%)
- RigForge track_c refresh; binanceai claim still closed; OBFG note; NAPPER deadline -> run 22:01.
Backup first. No preview/mint."""
import json, shutil, datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 21:31 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2131")
snap = json.load(open(BASE + "onchain-snapshot.json"))
ver = json.load(open(BASE + "run-2026-11-12-2131-verify.json"))
retry = json.load(open(BASE + "run-2026-11-12-2131-retry-new.json"))
block = ver["block"]

MAP = {
    "WFPASS": "WFPASS", "SEVEN": "SEVEN", "AGCR": "AGCR", "MECHA": "MECHA",
    "SUDOSAINTS": "SUDOSAINTS", "Pickgrid": "Pickgrid",
    "LuckyCatch": "LuckyCatch", "BinanceLife": "BinanceLife",
    "Kongtou-AirdropCnNFT": "Kongtou-AirdropCnNFT", "0x7Eb9": "0x7Eb9",
    "NAOMI": "NAOMI", "AgenticGangster": "AgenticGangster",
    "AIRDROP": "AIRDROP", "Kitebots": "Kitebots", "Dragon Agent": "Dragon Agent",
}
updated = []
for name, key in MAP.items():
    r = ver["reads"].get(name)
    if not r or not r.get("views"):
        continue
    c = snap["contracts"].get(key)
    if c is None:
        continue
    v = r["views"]
    prev = c.get("totalSupply")
    for f in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY"):
        if v.get(f) is not None:
            c[f] = v[f]
    if v.get("balanceOf_user") is not None:
        c["balanceOf_user"] = v["balanceOf_user"]
    c["lastReadBlock"] = block
    c["lastReadWib"] = TS
    new = c.get("totalSupply")
    minted = (new - prev) if (isinstance(new, int) and isinstance(prev, int)) else None
    c["runNote2131_1112"] = (
        f"Run 2131 (blok {block}): totalSupply {prev}->{new} "
        f"(+{minted if minted is not None else '?'}), velocity GAGAL (<20 token); "
        f"freeClaimed={v.get('freeClaimed')}, freeMinted={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; bukan kandidat; tanpa perubahan status.")
    updated.append(key)

m = snap["contracts"].get("MECHA")
if m:
    m["runNote2131_1112"] = (
        "Run 2131 (blok 133177364): totalMinted 1846->1850 (+4, <20 token), "
        "freeClaimed 1845->1849 (41,6% dari FREE_SUPPLY 4444); velocity GAGAL; "
        "umur launch UNVERIFIED; gate website GAGAL -> tetap watchlist-only EARLY, bukan kandidat.")

# --- BUCKET age-exclusion ---
def age_rec(name, addr, mint_start, supply, cap):
    dt = datetime.datetime.fromtimestamp(mint_start, datetime.timezone(datetime.timedelta(hours=7)))
    return {
        "name": name, "address": addr,
        "mintStartWib": dt.strftime("%Y-%m-%d %H:%M:%S WIB"),
        "deadline24hWib": (dt + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S WIB"),
        "readWib": TS, "readBlock": block,
        "totalSupply_at_removal": supply, "freeCap": cap,
        "freePct_approx": round(100.0 * supply / cap, 2) if cap else None,
        "status_before": "early-lead-reported-2026-11-11",
        "reported_as": "age-excluded-once-2026-11-12-2131",
        "evidence": "mintOpenedAt on-chain 1794406606 (baca segar run 2131: totalSupply 718, "
                    "tidak berubah vs run 2101) + totalSupply segar; bukan sold out (718/3333); "
                    "website + X + diskusi tidak pernah terverifikasi; tidak pernah jadi kandidat.",
    }

b = snap["contracts"].pop("BUCKET", None)
bucket_supply = ver["reads"]["BUCKET"]["views"].get("totalSupply") if ver["reads"].get("BUCKET") else None
if bucket_supply is None and b is not None:
    bucket_supply = b.get("totalSupply")
snap["age_exclusions_2131"] = [age_rec("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
                                       1794406606, bucket_supply, 3333)]
snap["runNote2131_1112_age_exclusions"] = (
    "Run 2131: BUCKET (mintOpenedAt 11 Nov 21:16:46 WIB, deadline 12 Nov 21:16:46 WIB) "
    ">=24 jam saat run, belum sold out (totalSupply 718/3333 = 21,5%), dilaporkan sekali "
    "sebagai age-excluded (pernah dilaporkan sekali sebagai EARLY lead 11 Nov). Dihapus dari "
    "contracts. NAPPER deadline 22:00:30 WIB belum lewat saat run ini -> run 22:01; "
    "NAPPER BATCH-FAIL run ini (nilai lama dipertahankan).")

# --- ADD SolNFT + AgcNFT as early leads ---
def wib(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")

sol = retry["reads"]["SolNFT"]["views"]
agc = retry["reads"]["AgcNFT"]["views"]
snap["contracts"]["SolNFT"] = {
    "address": "0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606",
    "status": "early-lead-reported-2026-11-12",
    "name": "Sol", "symbol": "SOL", "kind": "ERC721",
    "totalMinted": sol.get("totalMinted"), "freeMinted": sol.get("freeMinted"),
    "FREE_CAP": sol.get("FREE_CAP"), "MAX_SUPPLY": sol.get("MAX_SUPPLY"),
    "mintOpen": sol.get("mintOpen"), "mintOpensAt": sol.get("mintOpensAt"),
    "priceWei": sol.get("price"),
    "freePctVerified": round(100.0 * sol["freeMinted"] / sol["FREE_CAP"], 1) if sol.get("freeMinted") and sol.get("FREE_CAP") else None,
    "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
    "userSlotNote": "Slot TERBUKA: freeClaimed(user)=0, mintsBy(user)=0, balanceOf(user)=0, holdsAgentId(user)=1.",
    "firstSeenBlock": block, "firstSeenWib": TS,
    "sourcifyVerifiedAt": "2026-11-12T14:33:57Z",
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "lastReadBlock": block, "lastReadWib": TS,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintOpensAt on-chain 1794493918 = 2026-11-12 21:31:58 WIB "
                  "(umur ~menit saat bacaan); dikoroborasi live minting (freeMinted 8->9->11 dalam ~8 mnt, "
                  "hot-leg 2129 + retry run ini). First-mint log timestamp TIDAK tersedia (Ankr 401, outage sejak 9 Nov).",
    "baselineNote": "EARLY lead dilaporkan sekali run 2131 (temuan feed Sourcify recently-verified; pertama "
                    "terlihat job ini di run ini - tidak ada di snapshot/track_c). Agent-shaped: agentIdRegistry()=registry "
                    "resmi, holdsAgentId(), mint+price+freeClaimed/freeMinted, FREE_CAP 333. Free 9/333 = 2,7% "
                    "(jauh di bawah 50% kandidat & >70% strong lead). Hot-leg 2129 menandai watchlist-only-age-unverified "
                    "(batch-nya tidak memuat mintOpensAt); retry single-call run ini memasok mintOpensAt sehingga umur "
                    "terverifikasi. TIDAK PERNAH di-preview/dimint (early lead).",
    "gateNote": "Website TIDAK DITEMUKAN (metode A: pencarian alamat kontrak 0 hit; B: Boltbook EN+ZH tidak memuat; "
                "C: metadata Sourcify tanpa URL proyek; G: pencarian nama SolNFT tanpa hit proyek; I: contractURI() null, "
                "tokenURI(1)='1' tanpa URL/external_url). GATE website GAGAL untuk eksekusi - early lead TIDAK PERNAH "
                "di-preview/dimint.",
    "previousTotalSupply": sol.get("totalMinted"),
    "mintedInInterval": None, "currentRatePerMin": None, "previousRatePerMin": None,
    "velocityLegPasses": False,
    "velocityNote": "Run 2131: bacaan pertama (baseline totalMinted 8); rate belum terhitung -> velocity TIDAK lulus run ini.",
    "freeMintedNote": "freeMinted 9 vs totalMinted 8 (counter berbeda, dicatat apa adanya dari bacaan segar).",
    "supplyView": "totalMinted",
}
snap["contracts"]["AgcNFT"] = {
    "address": "0xdAc222886b887fC5b6262889B189B8eb57e99794",
    "status": "early-lead-reported-2026-11-12",
    "name": "Agc", "symbol": "AGC", "kind": "ERC721",
    "totalMinted": agc.get("totalMinted"), "freeMinted": agc.get("freeMinted"),
    "FREE_CAP": agc.get("FREE_CAP"), "MAX_SUPPLY": agc.get("MAX_SUPPLY"),
    "mintOpen": agc.get("mintOpen"), "mintOpensAt": agc.get("mintOpensAt"),
    "priceWei": agc.get("price"),
    "freePctVerified": round(100.0 * agc["freeMinted"] / agc["FREE_CAP"], 1) if agc.get("freeMinted") and agc.get("FREE_CAP") else None,
    "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
    "userSlotNote": "Slot TERBUKA: freeClaimed(user)=0, mintsBy(user)=0, balanceOf(user)=0, holdsAgentId(user)=1.",
    "firstSeenBlock": block, "firstSeenWib": TS,
    "sourcifyVerifiedAt": "2026-11-12T14:11:03Z",
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "lastReadBlock": block, "lastReadWib": TS,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintOpensAt on-chain 1794494012 = 2026-11-12 21:33:32 WIB "
                  "(umur ~menit saat bacaan); dikoroborasi live minting (freeMinted 38->42->43 dalam ~8 mnt, "
                  "hot-leg 2129 + retry run ini). First-mint log timestamp TIDAK tersedia (Ankr 401, outage sejak 9 Nov).",
    "baselineNote": "EARLY lead dilaporkan sekali run 2131 (temuan feed Sourcify recently-verified; pertama "
                    "terlihat job ini di run ini - tidak ada di snapshot/track_c). Agent-shaped: agentIdRegistry()=registry "
                    "resmi, holdsAgentId(), mint+price+freeClaimed/freeMinted, FREE_CAP 333. Free 43/333 = 12,9% "
                    "(di bawah 50% kandidat & >70% strong lead). Nama 'Agc'/AGC generik, BUKAN linkage ke proyek AGC lain. "
                    "Hot-leg 2129 menandai watchlist-only-age-unverified (batch-nya tidak memuat mintOpensAt); retry "
                    "single-call run ini memasok mintOpensAt sehingga umur terverifikasi. TIDAK PERNAH di-preview/dimint "
                    "(early lead).",
    "gateNote": "Website TIDAK DITEMUKAN (metode A: pencarian alamat kontrak 0 hit; B: Boltbook EN+ZH tidak memuat; "
                "C: metadata Sourcify tanpa URL proyek; G: pencarian nama AgcNFT tanpa hit proyek; I: contractURI() null, "
                "tokenURI(1)='1' tanpa URL/external_url). GATE website GAGAL untuk eksekusi - early lead TIDAK PERNAH "
                "di-preview/dimint.",
    "previousTotalSupply": agc.get("totalMinted"),
    "mintedInInterval": None, "currentRatePerMin": None, "previousRatePerMin": None,
    "velocityLegPasses": False,
    "velocityNote": "Run 2131: bacaan pertama (baseline totalMinted 43); rate belum terhitung -> velocity TIDAK lulus run ini.",
    "supplyView": "totalMinted",
}

# --- RigForge track_c refresh (unchanged) ---
rf = snap.get("track_c", {}).get("RigForge")
if rf:
    rf["freeSharesLeft"] = 662
    rf["openedAt"] = 0
    rf["freeClaimed"] = 338
    rf["lastReadBlock"] = block
    rf["lastReadWib"] = TS

# --- binanceai pending claim: still closed ---
snap["runNote2131_1112_binanceai"] = (
    "Run 2131 (blok 133177364): binanceai-mint launched()=0, freeSharesRemaining=0, "
    "FREE_SHARES=2888 — klaim BELUM dibuka (fase refund); pending_claims tetap kosong; "
    "tidak ada klaim/preview.")

# --- OBFG read (tracked by hot-leg in hot-leg-seen.json; NOT added to main snapshot) ---
snap["runNote2131_1112_obfg"] = (
    "Run 2131 (blok 133177364): OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 "
    "freeMinted 337->376/1230 (30,6%), totalSupply 376, saleStart 1794488476 "
    "(20:01:16 WIB, umur ~97 mnt), freeAvailable(user)=1, quote(user,1) gratis; "
    "gate website tetap GAGAL (dilaporkan sekali 20:18 WIB), masih <70% strong-lead -> "
    "TIDAK preview/mint, tidak dilaporkan ulang; tracking di hot-leg-seen.json, bukan snapshot utama.")

snap["last_run"] = "2026-11-12-2131"
snap["last_run_wib"] = TS
snap["last_run_block"] = block
snap["last_run_note"] = (
    "Run 2131: pre-flight Ankr 401 FAIL (scan fast-fail, watermark tetap 132512564); "
    "feed 20 kontrak, 2 agent-shaped baru (SolNFT, AgcNFT) diverifikasi single-call retry "
    "(batch gagal) -> EARLY lead dilaporkan sekali + masuk snapshot; Boltbook EN+ZH 0 alamat baru; "
    "bridge 116 kontrak 0 not-in-snapshot, 7 same-owner-discarded; verify 37 target (23 terbaca, "
    "14 BATCH-FAIL, nilai lama dipertahankan); BUCKET age-excluded (deadline 21:16:46 lewat, 718/3333) "
    "dilaporkan sekali; OBFG 376/1230 (30,6%) tetap gate-blocked; binanceai masih tutup; "
    "0 kandidat/strong lead/track-B/track-C baru; tidak ada preview/mint/eksekusi.")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("updated:", updated)
print("removed: BUCKET; added: SolNFT, AgcNFT")
print("block:", block)
