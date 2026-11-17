#!/usr/bin/env python3
"""Snapshot update for free-mint-search run 2026-11-13 21:01 WIB.
Applies 2101 verify + supp reads; removes AgentLabs + HELIX (age-excluded);
adds LNFT (early lead) + APGB (watchlist-only); marks BUILD free pool sold out;
updates GoldVein track_c. Backs up snapshot first."""
import json, shutil, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2101")
s = json.load(open(BASE + "onchain-snapshot.json"))
v = json.load(open(BASE + "run-2026-11-13-2101-verify.json"))
supp = json.load(open(BASE + "run-2026-11-13-2101-supp.json"))
reads = {k: (x.get("views") or {}) for k, x in v["reads"].items()}
BLK = v["block"]
WIB = "2026-11-13 ~21:35 WIB"

def upd(name, **kw):
    e = s["contracts"].setdefault(name, {})
    e.update(kw)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    return e

# --- generic refresh of active items from verify reads ---
def refresh(name, snap_key=None):
    key = snap_key or name
    r = reads.get(name)
    if r is None or key not in s["contracts"]:
        return
    e = s["contracts"][key]
    prev_ts = e.get("totalSupply")
    for f in ("totalSupply", "totalMinted", "freeMinted", "freeClaimed", "freeLeft",
              "freeRemaining", "FREE_SUPPLY", "FREE_CAP", "FREE_MAX", "FREE_SHARES",
              "MAX_SUPPLY", "mintOpen", "saleStart", "saleOpen", "mintOpensAt",
              "openedAt", "opened", "genesisStart", "genesisOpen", "currentExperiment",
              "totalSpecimens", "freeCount", "paidMinted", "freeSold", "paidSold"):
        if f in r and r[f] is not None:
            e[f] = r[f]
    if "balanceOf_user" in r:
        e["balanceOf_user"] = r["balanceOf_user"]
    if "freeClaimed_user" in r:
        e["freeClaimed_user"] = r["freeClaimed_user"]
    if "freeAvailable_user" in r:
        e["freeAvailable_user"] = r["freeAvailable_user"]
    if prev_ts is not None and e.get("totalSupply") is not None:
        e["previousTotalSupply"] = prev_ts
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB

for n in ["OBFG", "NOTV", "JNTM", "AgentMuse", "Agentx", "OUTY", "PX24", "SKRR",
          "ME30", "CY24", "MECHA", "Pickgrid", "HIVE", "Zero", "BC1B", "OLIVER",
          "RoyalRush", "Mossbound", "Slate", "Ochre", "DragonAgent", "VioletWaybill",
          "CinderCrucible", "BUBB", "MossSignal", "AgentCosmos", "HANAMI", "UNRES1",
          "UNRES2", "FROST"]:
    refresh(n, snap_key={"BUBB": "Agent Bubble", "RoyalRush": "Royal Rush Agents"}.get(n, n))
refresh("CinderAgents")

# --- per-item notes (short, one line) ---
def note(name, txt, snap_key=None):
    e = s["contracts"].get(snap_key or name)
    if isinstance(e, dict):
        e["runNote2101"] = txt

note("Agentx", "Run 2101 (blok 133367040): freeMinted 771/1111 = 69,4% (+5), slot terbuka, deadline umur 23:11:05 WIB 13 Nov. Override DITOLAK user — jalur tertutup. DIAM.")
note("Zero", "Run 2101: totalMinted/freeMinted 305/500 = 61,0% (+3), slot terbuka, umur <24 jam (deadline 07:55:03 WIB 14 Nov); gate website GAGAL (metode A,B,C,D,G,J,K,L,M). Watchlist-only. DIAM.")
note("RoyalRush", "Run 2101: totalSupply 893, freeMinted 896/1000 = 89,6%, freeRemaining 104, website LOLOS (run 1031); umur BELUM terverifikasi (deadline estimasi ~10:31 WIB 14 Nov). Monitor-only. DIAM.", snap_key="Royal Rush Agents")
note("BUBB", "Run 2101: totalSupply 1156 (+151 vs 2031), freeMinted 1052 (+151) — velocity LOLOS (~3,8/mnt vs prev ~0,54/mnt, ~7x, >=20 token) TAPI % kuota gratis tetap UNVERIFIED (tanpa FREE cap view) -> BUKAN kandidat/strong lead. Watchlist-only. DIAM.", snap_key="Agent Bubble")
note("BUILD", "Run 2101: FREE POOL SOLD OUT — freeMinted 200/200, freeLeft 0, totalMinted 202 (200 free + 2 paid). User pegang #118 (mint 21:05 WIB). Dilaporkan sekali run ini sebagai sellout perubahan; slot user terpakai.")
note("Moon", "Run 2101: totalMinted 415/3333 (+43), mintOpen 1, agentIdRegistry = registry persis; TANPA free view -> % gratis UNVERIFIED; umur UNVERIFIED. Watchlist-only. DIAM.")
note("Zora", "Run 2101: totalSupply/totalMinted 4900/5000 = 98%, free views null, Sourcify UNVERIFIED -> % UNVERIFIED, bukan lead. DIAM.")
note("D8DA", "Run 2101: SEMUA view standar null — tidak terverifikasi. BUKAN lead. DIAM.")
note("CinderCrucible", "Run 2101: totalMinted/freeMinted 107/325 = 32,9% (+5), freeAvailable(user)=1; gate-blocked lead (dilaporkan 18:01). DIAM.")
note("CinderAgents", "Run 2101: totalSupply 297, freeMinted 166/500 = 33,2%; umur UNVERIFIED (first-mint terblokir Ankr 401) -> watchlist-only, bukan promosi. DIAM.")
note("MossSignal", "Run 2101: totalSupply 805/805, mintOpen masih 1 (jebakan) — sold out, sudah dicatat run 2031; tanpa perubahan run ini. DIAM.")
note("BinanceAI-mint", "Run 2101: launched=0, tokenClaimed(user)=0, isRefundPhase=1, failed=1 — refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, DIAM.")
note("HIVE", "Run 2101: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("OBFG", "Run 2101: totalSupply/freeMinted 703/1230 = 57,1% (+3); age-excluded 20:02 (sudah dilaporkan). DIAM.")
note("AgentMuse", "Run 2101: freeClaimed 416/888 (+8), openedAt 0 (belum buka). DIAM.")
note("AgentLabs", "Run 2101: AGE-EXCLUDED — genesisStart 1794492248 = 21:04:08 WIB 12 Nov (on-chain), umur 24 jam 31 mnt >24 jam; totalSpecimens 2377, priceFor(user)=0, belum sold out. Dilaporkan sekali run ini; dihapus dari snapshot.")
note("HELIX", "Run 2101: AGE-EXCLUDED — first mint blok 132394604 = 8 Nov 19:43:23 WIB (terverifikasi), umur ~97,9 jam >24 jam; totalSupply 738/4444 (+1), freeUsed(user)=0, mintActive=1, belum sold out. Dilaporkan sekali run ini; dihapus dari snapshot.")

# --- BUBB velocity fields ---
bubb = s["contracts"].get("Agent Bubble")
if isinstance(bubb, dict):
    bubb["previousTotalSupply"] = 1005
    bubb["mintedInInterval"] = 151
    bubb["currentRatePerMin"] = 3.8
    bubb["previousRatePerMin"] = 0.54
    bubb["velocityRatio"] = 7.0
    bubb["velocityLegPasses"] = True
    bubb["velocityNote"] = "run 2101: 1005->1156 (+151, ~3,8/mnt vs prev ~0,54 = ~7x) -> velocity LOLOS; % gratis UNVERIFIED -> bukan kandidat/strong lead."

# --- BUILD sold-out status ---
b = s["contracts"].get("BUILD")
if isinstance(b, dict):
    b["totalMinted"] = 202
    b["freeMinted"] = 200
    b["freeLeft"] = 0
    b["FREE_CAP"] = 200
    b["status"] = "minted-by-user-2026-11-13-free-pool-sold-out-2026-11-13"

# --- GoldVein track_c ---
tc = s.setdefault("track_c", {})
gv = tc.get("GoldVein")
if isinstance(gv, dict):
    gv["freeSold"] = 487
    gv["freePool"] = 13
    gv["lastReadWib"] = WIB
    gv["lastReadBlock"] = BLK
    gv["runNote2101"] = "Run 2101: freeSold 487/500 = 97,4% (+20), pool tersisa 13, slot terbuka, gate-blocked (dilaporkan sekali 2031). Belum sold out — pantau sellout run berikut. DIAM."

# --- pending claim ---
pc = s.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(pc, dict):
    pc["lastReadWib"] = WIB
    pc["runNote2101"] = "Run 2101: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1 — refund phase TIDAK BERUBAH. Tetap pending, DIAM."

# --- LNFT (early lead) + APGB (watchlist-only) ---
s["contracts"]["Laptop NFT"] = {
    "address": "0xb2ac84b0d2c9684436f2cf2dc7dfc8e80be78657",
    "status": "early-lead-reported-2026-11-13",
    "name": "Laptop NFT", "symbol": "LNFT", "kind": "ERC721",
    "totalSupply": 245, "MAX_SUPPLY": 4444,
    "MAX_FREE_PER_WALLET": 1, "MAX_PER_WALLET": 100,
    "TOKENS_PER_FREE_MINT": 10000, "TOKENS_PER_MINT": 100000,
    "TOKEN_PRICE": 500000000000000,
    "freeMintedPerWallet_user": 0, "mintedPerWallet_user": 0,
    "balanceOf_user": 0, "pixelReserve": 397650000000000000000000000,
    "AGENT_ID_registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "firstSeenBlock": 133368002, "lastReadBlock": BLK, "lastReadWib": WIB,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur peluncuran UNVERIFIED: tanpa stated launch time; first-mint on-chain TERBLOKIR (Ankr 401 + historical eth_call dataseed prune/missing trie node); pertama terlihat job ini run 2101 (post Boltbook 21:18 WIB, totalSupply 210 -> 245 selama run).",
    "baselineNote": "EARLY lead dilaporkan sekali run 2101 (temuan Boltbook EN+ZH). Agent-shaped TERVERIFIKASI: Sourcify exact_match (32 fns) + AGENT_ID() = registry persis + registry bytes di bytecode + mint(1) value 0 lolos sim wallet Agent ID / revert 'agent ID required' tanpa ID (2 post Boltbook). Semua 235 mint pertama gratis (rekonsiliasi ZH: 235x10.000 LPX). Slot user TERBUKA (freeMintedPerWallet 0/1). % kuota gratis UNVERIFIED (tanpa FREE cap view); website TIDAK DITEMUKAN (poster: no official site/socials); X unverified. RISIKO: LPX tanpa pair/harga (PCS V2/V3 0); withdrawPixel() owner bisa tarik 397,65 jt LPX reserve kapan saja; owner bisa ganti baseURI/treasury. TIDAK PERNAH auto-mint/preview (early tier + tanpa website).",
    "runNote2101": "Run 2101: totalSupply 245/4444 (+10 vs post ZH 235), minting berjalan; EARLY lead dilaporkan sekali.",
}
s["contracts"]["AlphaPulse Genesis Badge"] = {
    "address": "0x14E429947AFc932802d1fb404fb81fdC01E92A6E",
    "status": "watchlist-only-agent-shape-unverified-2026-11-13",
    "name": "AlphaPulse Genesis Badge", "kind": "ERC721",
    "totalSupply": 218, "MAX_SUPPLY": 10000, "mintOpen": 1,
    "balanceOf_user": 0,
    "website": "https://alphapulseapls.github.io/alphapulse/badge.html",
    "firstSeenBlock": 133368002, "lastReadBlock": BLK, "lastReadWib": WIB,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur peluncuran UNVERIFIED (tanpa stated launch time; pertama terlihat job ini run 2101 via post Boltbook).",
    "baselineNote": "First-read run 2101 (temuan post Boltbook 'Your Agent ID Is Already a Mining Rig'). Website ADA: badge page mencetak kontrak BADGE + MARKET + MINING + registry. TAPI agent-shape UNVERIFIED: Sourcify no-abi (tidak terverifikasi) + registry bytes TIDAK ada di bytecode BADGE maupun MINING (0xf9cD9B0d9FFbfB41BE3017D8C8Dde6315feD51F4). BUKAN early lead (butuh agent-shaped). Watchlist-only; verifikasi ulang bila Sourcify terverifikasi.",
    "runNote2101": "Run 2101: totalSupply 218/10000, mintOpen 1; agent-shape unverified -> bukan lead, DIAM.",
}

# --- removals (age-excluded, reported once) ---
for dead in ("AgentLabs", "HELIX"):
    s["contracts"].pop(dead, None)

s["last_run_wib"] = WIB
s["last_run_note"] = ("Run 2101: 39/39 re-read OK (blok 133367040) + supp 3/3 (blok 133368002). "
    "LNFT EARLY lead baru (dilaporkan sekali). AgentLabs + HELIX AGE-EXCLUDED (dilaporkan sekali, dihapus). "
    "BUILD free pool SOLD OUT 200/200 (dilaporkan sekali). GoldVein 487/500 (13 tersisa), gate-blocked. "
    "Ankr pre-flight 401 GAGAL CEPAT; watermark tetap 132512564. Tanpa kandidat/strong lead baru.")
s["runNote2101"] = s["last_run_note"]
s["timestamp_wib"] = WIB

json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)

# hot-leg-reported.json: dedupe markers for once-reports this run
hlr_path = BASE + "hot-leg-reported.json"
hlr = json.load(open(hlr_path))
hlr["0x639329f5dc4317c44D9Fed961a1217ba845012F7#age-excluded-20261113"] = {
    "name": "AgentLabs", "event": "age-excluded", "reported_wib": WIB,
    "note": "Genesis 21:04:08 WIB 12 Nov (genesisStart on-chain); umur 24j31m >24j; totalSpecimens 2377; dilaporkan sekali run 2101."}
hlr["0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665#age-excluded-20261113"] = {
    "name": "HELIX", "event": "age-excluded", "reported_wib": WIB,
    "note": "First mint blok 132394604 = 8 Nov 19:43:23 WIB; umur ~97,9j >24j; totalSupply 738/4444; dilaporkan sekali run 2101."}
hlr["0xC43f7Ab11728FC884662B35AD974ff703cb4221d#free-sold-out-20261113"] = {
    "name": "BUILD", "event": "free-pool-sold-out", "reported_wib": WIB,
    "note": "freeMinted 200/200, freeLeft 0; user pegang #118; dilaporkan sekali run 2101."}
hlr["0xb2ac84b0d2c9684436f2cf2dc7dfc8e80be78657#early-lead-20261113"] = {
    "name": "Laptop NFT", "event": "early-lead", "reported_wib": WIB,
    "note": "Agent-shaped terverifikasi; totalSupply 245/4444; umur + % gratis UNVERIFIED; website tidak ditemukan; dilaporkan sekali run 2101."}
json.dump(hlr, open(hlr_path, "w"), indent=1)
print("SNAPSHOT UPDATED; contracts now:", len(s["contracts"]), "; removals done; hlr markers added.")
