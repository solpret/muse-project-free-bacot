#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 07:31 WIB — MERGE (written fresh this run).

Replaces the stale prepared final.py (written pre-mint, claims SILENT).
Merges, in order:
  1. 0704 verify-retry leg4 readings (block 133062991)
  2. 0731 tc-age re-check (CLEPSYDRA / MoonAgent / WNO)
  3. 0731 full reread (63 contracts + 21 track_c, block 133066512)
  4. Fresh Stampooor post-mint verification + mint record (tx 0xf7116b45...)
  5. Fresh SEVEN + Eco reads; Eco free-slot LOST -> entry REMOVED
  6. Run note + run log data.
Read-only wrt chain (one receipt fetch for gas price). Writes snapshot (+ .bak-0731)
and run-2026-11-12-0731-final.json. No preview, no mint.
"""
import json, shutil, subprocess

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
shutil.copy(snap_path, BASE + "onchain-snapshot.json.bak-0731")
snap = json.load(open(snap_path))
retry = json.load(open(BASE + "run-2026-11-12-0704-verify-retry.json"))
tc = json.load(open(BASE + "run-2026-11-12-0731-tc-age.json"))
reread = json.load(open(BASE + "run-2026-11-12-0731-reread.json"))

def index(section):
    out = {}
    v = snap.get(section, {})
    if isinstance(v, dict):
        for k, it in v.items():
            if isinstance(it, dict) and it.get("address"):
                out[it["address"].lower()] = (k, it)
    return out

cidx = index("contracts")
tidx = index("track_c")
updates = {}

def upd(addr, fields, section="contracts", block=None, wib=None):
    idx = cidx if section == "contracts" else tidx
    key = idx.get(addr.lower())
    if key is None:
        updates[addr] = "NOT-IN-SNAPSHOT"
        return
    k, it = key
    for f, val in fields.items():
        if val is not None:
            it[f] = val
    if block:
        it["lastReadBlock"] = block
    if wib:
        it["lastReadWib"] = wib
    updates[addr] = k

R = retry["leg4_reread"]
RB = retry["block"]
# --- 0704 retry leg4 (baseline, block 133062991) ---
upd("0x467696af8c2206B977B24081445104632dc1D459", {  # Stampooor (overridden below)
    "freeMinted": R["Stampooor"].get("freeMinted"),
    "totalMinted": R["Stampooor"].get("totalMinted"),
    "FREE_SUPPLY": R["Stampooor"].get("FREE_SUPPLY"),
    "mintOpen": R["Stampooor"].get("mintOpen"),
    "freeAvailable_user": R["Stampooor"].get("freeAvailable_user"),
    "balanceOf_user": R["Stampooor"].get("balanceOf_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96", {  # SEVEN (overridden below)
    "freeMinted": R["SEVEN"].get("freeMinted"),
    "FREE_CAP": R["SEVEN"].get("FREE_CAP"),
    "mintOpen": R["SEVEN"].get("mintOpen"),
    "balanceOf_user": R["SEVEN"].get("balanceOf_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3", {  # Eco (removed below)
    "freeMinted": R["Eco"].get("freeMinted"),
    "totalMinted": R["Eco"].get("totalMinted"),
    "FREE_WALLETS": R["Eco"].get("FREE_WALLETS"),
    "freeWalletsLeft": R["Eco"].get("freeWalletsLeft"),
    "freeWalletCount": R["Eco"].get("freeWalletCount"),
    "MAX_SUPPLY": R["Eco"].get("MAX_SUPPLY"),
    "mintOpen": R["Eco"].get("mintOpen"),
    "mintOpensAt": R["Eco"].get("mintOpensAt"),
    "FREE_PER_WALLET": R["Eco"].get("FREE_PER_WALLET"),
    "balanceOf_user": R["Eco"].get("balanceOf_user"),
    "freeCountBy_user": R["Eco"].get("freeCountBy_user"),
    "mintsBy_user": R["Eco"].get("mintsBy_user"),
    "holdsAgentId_user": R["Eco"].get("holdsAgentId_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", {  # AGCR
    "totalSupply": R["AGCR"].get("totalSupply"),
    "totalMinted": R["AGCR"].get("totalMinted"),
    "freeMinted": R["AGCR"].get("freeMinted"),
    "FREE_SUPPLY": R["AGCR"].get("FREE_SUPPLY"),
    "MAX_SUPPLY": R["AGCR"].get("MAX_SUPPLY"),
    "balanceOf_user": R["AGCR"].get("balanceOf_user"),
    "mintOpen": R["AGCR"].get("mintOpen")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", {  # MECHA
    "totalMinted": R["MECHA"].get("totalMinted"),
    "freeClaimed": R["MECHA"].get("freeClaimed_user"),
    "freeAvailable_user": R["MECHA"].get("freeAvailable_user"),
    "balanceOf_user": R["MECHA"].get("balanceOf_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0x2b0d3b384C341020aed1d49907b5708C423bA6DA", {  # BUCKET
    "totalSupply": R["BUCKET"].get("totalSupply"),
    "mintOpenedAt": R["BUCKET"].get("mintOpenedAt"),
    "balanceOf_user": R["BUCKET"].get("balanceOf_user"),
    "freeUsed_user": R["BUCKET"].get("freeUsed_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0x87b354E2014D2e418927A1105dD219A2e7b063b0", {  # MOONDRILL
    "totalSupply": R["MOONDRILL"].get("totalSupply"),
    "firstFreeUsed": R["MOONDRILL"].get("firstFreeUsed"),
    "FIRST_FREE_CAP": R["MOONDRILL"].get("FIRST_FREE_CAP"),
    "X_FREE_CAP": R["MOONDRILL"].get("X_FREE_CAP"),
    "paidMinted": R["MOONDRILL"].get("paidMinted"),
    "mintOpen": R["MOONDRILL"].get("mintOpen"),
    "balanceOf_user": R["MOONDRILL"].get("balanceOf_user"),
    "firstFreeByWallet_user": R["MOONDRILL"].get("firstFreeByWallet_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", {  # CRTSAINTS
    "totalSupply": R["CRTSAINTS"].get("totalSupply"),
    "firstFreeUsed": R["CRTSAINTS"].get("firstFreeUsed"),
    "FIRST_FREE_CAP": R["CRTSAINTS"].get("FIRST_FREE_CAP"),
    "X_FREE_CAP": R["CRTSAINTS"].get("X_FREE_CAP"),
    "paidMinted": R["CRTSAINTS"].get("paidMinted"),
    "mintOpen": R["CRTSAINTS"].get("mintOpen"),
    "balanceOf_user": R["CRTSAINTS"].get("balanceOf_user"),
    "firstFreeByWallet_user": R["CRTSAINTS"].get("firstFreeByWallet_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0x869d330bb48e7ab32da16745ef9a36a69d34f12f", {  # SUDOSAINTS
    "totalSupply": R["SUDOSAINTS"].get("totalSupply"),
    "freeMinted": R["SUDOSAINTS"].get("freeMinted"),
    "balanceOf_user": R["SUDOSAINTS"].get("balanceOf_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0", {  # Pickgrid
    "totalSupply": R["Pickgrid"].get("totalSupply"),
    "freeMinted": R["Pickgrid"].get("freeMinted"),
    "FREE_CAP": R["Pickgrid"].get("FREE_CAP"),
    "balanceOf_user": R["Pickgrid"].get("balanceOf_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0xD405C90079c594DA2456F5b37B4158A12f1382e5", {  # Lucky Catch
    "totalSupply": R["LuckyCatch"].get("totalSupply"),
    "totalMinted": R["LuckyCatch"].get("totalMinted"),
    "mintOpen": R["LuckyCatch"].get("mintOpen"),
    "balanceOf_user": R["LuckyCatch"].get("balanceOf_user"),
    "mintStart": R["LuckyCatch"].get("mintStart"),
    "PRICE": R["LuckyCatch"].get("PRICE")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0x4367b86F889014e6fD57fE812B86A581b913C645", {  # Binance Life
    "totalMinted": R["BinanceLife"].get("totalMinted"),
    "freeMinted": R["BinanceLife"].get("freeMinted"),
    "MAX_SUPPLY": R["BinanceLife"].get("MAX_SUPPLY"),
    "balanceOf_user": R["BinanceLife"].get("balanceOf_user"),
    "mintStart": R["BinanceLife"].get("mintStart")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", {  # 0x2e50
    "totalSupply": R["0x2e50"].get("totalSupply"),
    "firstFreeUsed": R["0x2e50"].get("firstFreeUsed"),
    "FIRST_FREE_CAP": R["0x2e50"].get("FIRST_FREE_CAP"),
    "X_FREE_CAP": R["0x2e50"].get("X_FREE_CAP"),
    "paidMinted": R["0x2e50"].get("paidMinted"),
    "mintOpen": R["0x2e50"].get("mintOpen"),
    "balanceOf_user": R["0x2e50"].get("balanceOf_user"),
    "firstFreeByWallet_user": R["0x2e50"].get("firstFreeByWallet_user")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", {  # binanceai mint
    "launched": R["binanceai-mint"].get("launched")}, block=RB, wib="2026-11-12 07:21 WIB")
upd("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", {  # RigForge track_c
    "freeSharesLeft": R["RigForge"].get("freeSharesLeft"),
    "openedAt": R["RigForge"].get("openedAt"),
    "freeClaimed_user": R["RigForge"].get("freeClaimed_user")}, section="track_c", block=RB, wib="2026-11-12 07:21 WIB")
wno = tidx.get("0x8c969a4cd49e4774908e667702c3d7c3ece164d0")
if wno:
    wno[1]["totalShares"] = tc["WNO"].get("totalShares")
    wno[1]["lastReadBlock"] = tc["block"]
    wno[1]["lastReadWib"] = "2026-11-12 07:35 WIB"
    updates["0x8C969a4CD49E4774908e667702C3d7C3ece164D0"] = wno[0]

# --- 0731 reread (block 133066512): non-None fields only, per-item run note ---
RB2 = reread["block"]
for name, d in reread["reread"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    key = cidx.get(d["address"].lower())
    if key is None:
        continue
    k, it = key
    prev_free = it.get("freeMinted")
    prev_ts = it.get("totalSupply")
    for f in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user",
              "freeClaimed_user"):
        if d.get(f) is not None:
            it[f] = d[f]
    it["lastReadBlock"] = RB2
    it["lastReadWib"] = "2026-11-12 07:47 WIB"
    it["runNote0731"] = (
        f"Run 0731 (blok {RB2}): freeMinted {prev_free}->{d.get('freeMinted')}, "
        f"totalSupply {prev_ts}->{d.get('totalSupply')}, bal_user={d.get('balanceOf_user')}.")
    updates[d["address"]] = k
for name, d in reread["track_c"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    key = tidx.get(d["address"].lower())
    if key is None:
        continue
    k, it = key
    for f in ("totalSupply", "freeMinted", "freeSharesRemaining",
              "balanceOf_user", "freeClaimed_user"):
        if d.get(f) is not None:
            it[f] = d[f]
    it["lastReadBlock"] = RB2
    it["lastReadWib"] = "2026-11-12 07:47 WIB"
    updates[d["address"]] = k

# --- Stampooor MINT (strong-lead direct mint, this run) ---
TX = "0xf7116b450ce54984e4dcd55b3b537f09de170aef8751ac550d52f7462f461caf"
gas_price = None
try:
    out = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST",
                          "https://bsc-dataseed.binance.org/",
                          "-H", "Content-Type: application/json",
                          "-d", json.dumps({"jsonrpc": "2.0", "id": 1,
                                            "method": "eth_getTransactionReceipt",
                                            "params": [TX]})],
                         capture_output=True, text=True, timeout=30).stdout
    rc = json.loads(out).get("result") or {}
    gas_price = int(rc.get("effectiveGasPrice", "0x0"), 16) if rc.get("effectiveGasPrice") else None
except Exception:
    pass
gas_used = 177495
gas_bnb = (gas_used * gas_price / 1e18) if gas_price else None
st = cidx.get("0x467696af8c2206b977b24081445104632dc1d459")
if st:
    k, it = st
    it.update({
        "status": "minted-by-user-2026-11-12",
        "freeMinted": 891,
        "totalMinted": 891,
        "FREE_SUPPLY": 1200,
        "mintOpen": 1,
        "freeAvailable_user": 0,
        "freeUsed_user": 1,
        "balanceOf_user": 1,
        "gate": "website_verified_pages_dev_packs_2026-11-12",
        "website": "https://stampooor.pages.dev/packs/",
        "websiteVerified": True,
        "mintTx": TX,
        "mintBlock": 133065781,
        "mintGas": gas_used,
        "mintGasPriceWei": gas_price,
        "mintGasBnb": gas_bnb,
        "mintTokenId": 890,
        "mintOrderId": "26111200002034556225",
        "lastReadBlock": RB2,
        "lastReadWib": "2026-11-12 07:47 WIB",
        "rarity": "tier not verified (no Rarity/Tier trait); Design=Express, Finish=Prized, State=Revealed (tokenURI on-chain)",
        "marketplace": "NO own market verified (project site is a mint page only, no market/trade section); Element asset-page check BLOCKED by Cloudflare (text-fetch 403 + live-browser bot wall, Ray a59184ed0940714e) - floor/listings UNVERIFIED, not absent. NO auto-list (no own market live, no live floor).",
        "runNote0731_mint": (
            "STRONG-LEAD DIRECT MINT run 0731: gate verified live (https://stampooor.pages.dev/packs/ HTTP 200, "
            "17017 byte, contract printed; first verified by gate-blocked-recheck 07:01, re-verified by this run). "
            "Legs: age VERIFIED <24h (mintStart 2026-11-11 09:00:19 WIB, ~22.7h, deadline ~09:00:19 WIB); "
            "free 888/1200=74.0% >70% at preview; slot OPEN (freeAvailable=1, freeUsed=0, bal 0, quote free=true). "
            "Audit Binance hasResult=false (NO RESULT, disclosed, not a pass; riskItems [], riskAlert null, no RISK hit). "
            "Preview CLEAN (requestId 51cd04e427a04590af261495812b75e8, simulationCode 000000000, value 0, "
            "balance +1 STPACK #890, no authority/allowance changes, risks empty). "
            "Execute BROADCASTED order 26111200002034556225, tx 0xf7116b450ce54984e4dcd55b3b537f09de170aef8751ac550d52f7462f461caf, "
            "receipt status 1, blok 133065781, gas 177495, tokenId 890, ownerOf(890)=agent wallet, "
            "freeMinted 888->890 (post-mint read 891 at blok 133066512), freeUsed(user) 0->1, balanceOf(user) 0->1. "
            "Rarity: tier not verified; Design Express, Finish Prized, State Revealed. "
            "Marketplace: no own market; Element blocked by Cloudflare - NO auto-list."),
    })
    updates["0x467696af8c2206B977B24081445104632dc1D459"] = k

# --- SEVEN fresh read (this run, ~07:55 WIB) ---
sv = cidx.get("0xff65cf70a15fa0b06bf8d8ed020cf9f917c80f96")
if sv:
    k, it = sv
    it.update({
        "freeMinted": 1106, "totalMinted": 1106, "FREE_CAP": 1111,
        "mintOpen": 1, "mintOpensAt": 1794415297, "price": 1400000000000000,
        "freeCountBy_user": 0, "balanceOf_user": 0, "holdsAgentId_user": 1,
        "lastReadBlock": 133066615, "lastReadWib": "2026-11-12 07:55 WIB",
        "runNote0731": (
            "Run 0731 fresh: freeMinted 1106/1111 = 99.55% (1038 di 0704, +68) - HANYA 5 slot gratis tersisa; "
            "slot user TERBUKA (freeCountBy 0, holdsAgentId 1, bal 0); umur TERVERIFIKASI <24 jam "
            "(mintOpensAt 2026-11-11 23:41:37 WIB, ~8.2 jam; deadline ~23:41 WIB 12 Nov). "
            "GATE tetap GAGAL run ini: (A) pencarian alamat 0 hasil; (B) Boltbook hanya sensus mamana.ai tanpa tautan situs; "
            "(C) Sourcify sources tanpa URL; (G) pencarian nama hanya MintRadar (bukan situs proyek); "
            "(H) contractURI tidak ada; (I) tokenURI hanya id, tanpa URL; (J) ABI tanpa fungsi situs; "
            "(E) owner 0x7f13f050... sama dengan Eco (deployer-group, bukan bukti situs); "
            "(L) BscScan text-fetch 403 - live-browser read diminta, menunggu hasil. "
            "TIDAK di-preview/di-mint (gate-blocked, sudah dilaporkan sekali)."),
    })
    updates["0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"] = k

# --- Eco: free slot LOST -> REMOVE from snapshot ---
eco = snap["contracts"].pop("Eco", None)
eco_removed = eco is not None
if eco_removed:
    updates["Eco-removed"] = "free-slot-lost-2026-11-12"

# --- WFPASS sellout mark (reported by hot-leg 0654) ---
for name, it in list(snap.get("contracts", {}).items()):
    if name.upper().startswith("WFPASS") and isinstance(it, dict):
        if "sold" not in str(it.get("status", "")).lower():
            it["status"] = "sold-out-2026-11-12"
            it["runNote0731"] = "Run 0731: freeMinted 500/500 SELLOUT (dilaporkan sekali hot-leg 0654); status ditandai sold-out."
            updates[it.get("address", name)] = name

snap["runNote0731"] = (
    "Run 0731 2026-11-12 07:31 WIB (blok ~133066512): STAMPOOOR STRONG-LEAD DIRECT MINT BERHASIL - "
    "token #890, tx 0xf7116b450ce54984e4dcd55b3b537f09de170aef8751ac550d52f7462f461caf, blok 133065781, gas 177495, "
    "receipt status 1, free 888->890/1200, slot user terpakai. Gate verified live pages.dev (HTTP 200, kontrak tercetak); "
    "audit Binance hasResult=false (no result, bukan pass); preview bersih 000000000. "
    "ECO FREE SLOT HILANG: freeWalletsLeft 0/555, sim mint() value 0 revert InsufficientPayment (0xcd1c8867) - "
    "early lead dihapus dari snapshot (dilaporkan sekali run ini). "
    "SEVEN 1106/1111=99.55% (5 slot tersisa), gate TETAP GAGAL (8 metode dicoba; BscScan live-browser pending). "
    "Scan leg FAST-FAIL preflight Ankr HTTP 401 (kuota 0% s.d. 1 Des) - watermark TIDAK maju (132512564). "
    "Legs: feed 20 (4 baru vs seen, 0 S1/S2/early); Boltbook EN/ZH 10 alamat, 0 baru; bridge 116, 0 not-in-snapshot. "
    "Reread 63 kontrak + 21 track_c: 0 crossing 50%/70%, 0 promosi. binanceai launched()=0 (pending/refund, TETAP). "
    "RigForge freeSharesLeft 678, openedAt 0 (belum buka). CLEPSYDRA startTime 2026-11-06 21:24 WIB + MoonAgent 294/800 tetap age-excluded; WNO totalShares 1648. "
    "WFPASS sellout 500/500 (dilaporkan hot-leg 0654). Marketplace Stampooor: no own market; Element diblokir Cloudflare - NO auto-list."
)
snap["last_run"] = "2026-11-12 07:31 WIB"
snap["last_run_wib"] = "2026-11-12 07:31 WIB"
snap["last_run_note"] = snap["runNote0731"]
json.dump(snap, open(snap_path, "w"), indent=1)
out = {"merged_updates": updates, "eco_removed": eco_removed,
       "gas_price_wei": gas_price, "gas_bnb": gas_bnb,
       "run_note": snap["runNote0731"][:300]}
json.dump(out, open(BASE + "run-2026-11-12-0731-final.json", "w"), indent=1)
print(json.dumps(out, indent=1))
