#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 07:31 WIB — FINAL merge (fresh script).
Merges the 07:04 attempt's verify-retry readings (block 133062991, completed
07:21 WIB) + this run's tc-age re-check (block 133064139) into
onchain-snapshot.json. Read-only wrt chain; writes snapshot (+ .bak-0731)
and run-2026-11-12-0731-final.json. No preview, no mint.
"""
import json, shutil, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
shutil.copy(snap_path, BASE + "onchain-snapshot.json.bak-0731")
snap = json.load(open(snap_path))
retry = json.load(open(BASE + "run-2026-11-12-0704-verify-retry.json"))
tc = json.load(open(BASE + "run-2026-11-12-0731-tc-age.json"))

# index snapshot contracts + track_c by lowercase address
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
def upd(addr, fields, section="contracts"):
    idx = cidx if section == "contracts" else tidx
    key = idx.get(addr.lower())
    if key is None:
        updates[addr] = "NOT-IN-SNAPSHOT"
        return
    k, it = key
    for f, val in fields.items():
        if val is not None:
            it[f] = val
    it["lastReadBlock"] = retry["block"]
    it["lastReadWib"] = "2026-11-12 07:21 WIB"
    updates[addr] = k

R = retry["leg4_reread"]
upd("0x467696af8c2206B977B24081445104632dc1D459", {  # Stampooor
    "freeMinted": R["Stampooor"].get("freeMinted"),
    "totalMinted": R["Stampooor"].get("totalMinted"),
    "FREE_SUPPLY": R["Stampooor"].get("FREE_SUPPLY"),
    "mintOpen": R["Stampooor"].get("mintOpen"),
    "freeAvailable_user": R["Stampooor"].get("freeAvailable_user"),
    "balanceOf_user": R["Stampooor"].get("balanceOf_user")})
upd("0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96", {  # SEVEN
    "freeMinted": R["SEVEN"].get("freeMinted"),
    "FREE_CAP": R["SEVEN"].get("FREE_CAP"),
    "mintOpen": R["SEVEN"].get("mintOpen"),
    "balanceOf_user": R["SEVEN"].get("balanceOf_user")})
upd("0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3", {  # Eco
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
    "holdsAgentId_user": R["Eco"].get("holdsAgentId_user")})
upd("0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc", {  # AGCR
    "totalSupply": R["AGCR"].get("totalSupply"),
    "totalMinted": R["AGCR"].get("totalMinted"),
    "freeMinted": R["AGCR"].get("freeMinted"),
    "FREE_SUPPLY": R["AGCR"].get("FREE_SUPPLY"),
    "MAX_SUPPLY": R["AGCR"].get("MAX_SUPPLY"),
    "balanceOf_user": R["AGCR"].get("balanceOf_user"),
    "mintOpen": R["AGCR"].get("mintOpen")})
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78", {  # MECHA
    "totalMinted": R["MECHA"].get("totalMinted"),
    "freeClaimed": R["MECHA"].get("freeClaimed_user"),
    "freeAvailable_user": R["MECHA"].get("freeAvailable_user"),
    "balanceOf_user": R["MECHA"].get("balanceOf_user")})
upd("0x2b0d3b384C341020aed1d49907b5708C423bA6DA", {  # BUCKET
    "totalSupply": R["BUCKET"].get("totalSupply"),
    "mintOpenedAt": R["BUCKET"].get("mintOpenedAt"),
    "balanceOf_user": R["BUCKET"].get("balanceOf_user"),
    "freeUsed_user": R["BUCKET"].get("freeUsed_user")})
upd("0x87b354E2014D2e418927A1105dD219A2e7b063b0", {  # MOONDRILL
    "totalSupply": R["MOONDRILL"].get("totalSupply"),
    "firstFreeUsed": R["MOONDRILL"].get("firstFreeUsed"),
    "FIRST_FREE_CAP": R["MOONDRILL"].get("FIRST_FREE_CAP"),
    "X_FREE_CAP": R["MOONDRILL"].get("X_FREE_CAP"),
    "paidMinted": R["MOONDRILL"].get("paidMinted"),
    "mintOpen": R["MOONDRILL"].get("mintOpen"),
    "balanceOf_user": R["MOONDRILL"].get("balanceOf_user"),
    "firstFreeByWallet_user": R["MOONDRILL"].get("firstFreeByWallet_user")})
upd("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", {  # CRTSAINTS
    "totalSupply": R["CRTSAINTS"].get("totalSupply"),
    "firstFreeUsed": R["CRTSAINTS"].get("firstFreeUsed"),
    "FIRST_FREE_CAP": R["CRTSAINTS"].get("FIRST_FREE_CAP"),
    "X_FREE_CAP": R["CRTSAINTS"].get("X_FREE_CAP"),
    "paidMinted": R["CRTSAINTS"].get("paidMinted"),
    "mintOpen": R["CRTSAINTS"].get("mintOpen"),
    "balanceOf_user": R["CRTSAINTS"].get("balanceOf_user"),
    "firstFreeByWallet_user": R["CRTSAINTS"].get("firstFreeByWallet_user")})
upd("0x869d330bb48e7ab32da16745ef9a36a69d34f12f", {  # SUDOSAINTS
    "totalSupply": R["SUDOSAINTS"].get("totalSupply"),
    "freeMinted": R["SUDOSAINTS"].get("freeMinted"),
    "balanceOf_user": R["SUDOSAINTS"].get("balanceOf_user")})
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0", {  # Pickgrid
    "totalSupply": R["Pickgrid"].get("totalSupply"),
    "freeMinted": R["Pickgrid"].get("freeMinted"),
    "FREE_CAP": R["Pickgrid"].get("FREE_CAP"),
    "balanceOf_user": R["Pickgrid"].get("balanceOf_user")})
upd("0xD405C90079c594DA2456F5b37B4158A12f1382e5", {  # Lucky Catch
    "totalSupply": R["LuckyCatch"].get("totalSupply"),
    "totalMinted": R["LuckyCatch"].get("totalMinted"),
    "mintOpen": R["LuckyCatch"].get("mintOpen"),
    "balanceOf_user": R["LuckyCatch"].get("balanceOf_user"),
    "mintStart": R["LuckyCatch"].get("mintStart"),
    "PRICE": R["LuckyCatch"].get("PRICE")})
upd("0x4367b86F889014e6fD57fE812B86A581b913C645", {  # Binance Life
    "totalMinted": R["BinanceLife"].get("totalMinted"),
    "freeMinted": R["BinanceLife"].get("freeMinted"),
    "MAX_SUPPLY": R["BinanceLife"].get("MAX_SUPPLY"),
    "balanceOf_user": R["BinanceLife"].get("balanceOf_user"),
    "mintStart": R["BinanceLife"].get("mintStart")})
upd("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", {  # 0x2e50
    "totalSupply": R["0x2e50"].get("totalSupply"),
    "firstFreeUsed": R["0x2e50"].get("firstFreeUsed"),
    "FIRST_FREE_CAP": R["0x2e50"].get("FIRST_FREE_CAP"),
    "X_FREE_CAP": R["0x2e50"].get("X_FREE_CAP"),
    "paidMinted": R["0x2e50"].get("paidMinted"),
    "mintOpen": R["0x2e50"].get("mintOpen"),
    "balanceOf_user": R["0x2e50"].get("balanceOf_user"),
    "firstFreeByWallet_user": R["0x2e50"].get("firstFreeByWallet_user")})
# binanceai mint (pending claim, launched still 0) — track by address in contracts if present
upd("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", {
    "launched": R["binanceai-mint"].get("launched")})
# RigForge track_c
upd("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", {
    "freeSharesLeft": R["RigForge"].get("freeSharesLeft"),
    "openedAt": R["RigForge"].get("openedAt"),
    "freeClaimed_user": R["RigForge"].get("freeClaimed_user")}, section="track_c")
# WNO totalShares (tc-age, block 133064139)
wno = tidx.get("0x8c969a4cd49e4774908e667702c3d7c3ece164d0")
if wno:
    wno[1]["totalShares"] = tc["WNO"].get("totalShares")
    wno[1]["lastReadBlock"] = tc["block"]
    wno[1]["lastReadWib"] = "2026-11-12 07:35 WIB"
    updates["0x8C969a4CD49E4774908e667702C3d7C3ece164D0"] = wno[0]

snap["runNote0731"] = (
    "Run 0731 SILENT: 0 kandidat/strong-lead/early-lead/track-B/track-C baru. "
    "Pre-flight Ankr FAIL (HTTP 401, kuota 0% s.d. 1 Des) — scan leg fast-fail, watermark TIDAK maju. "
    "Legs 0731: feed 20 (4 baru vs seen, 0 S1/S2/early — 0xD849 + 0x3F46 baru, 0x2307 + 0x7709 ulang dari 0704, semua shape-negatif); "
    "Boltbook EN 44.983 byte/10 alamat, ZH 43.291 byte/10 alamat, 0 baru; bridge 116 kontrak, 0 not-in-snapshot, 7 same_owner_discarded. "
    "Verify-retry 0704 (blok 133062991): Stampooor 888/1200=74,0% (tetap strong-lead gate-blocked, deadline umur ~09:00 WIB); "
    "SEVEN 1038/1111=93,4% (tetap gate-blocked); Eco 1258/2775=45,3% token, wallet 543/555=97,8% (tetap EARLY, velocity GAGAL 0,70 vs 1,09/mnt); "
    "AGCR 2391/2400=99,6% umur UNVERIFIED; MECHA 1300/4444=29,3%; BUCKET 650; Pickgrid 216/300 umur UNVERIFIED; "
    "binanceai launched()=0 (tetap pending/refund); RigForge freeSharesLeft 678, openedAt 0 (belum buka). "
    "tc-age: CLEPSYDRA startTime 1793975074 (2026-11-06 21:24 WIB) + MoonAgent 294/800 tetap age-excluded; WNO totalShares 1648/6000. "
    "Sweep EN+ZH: 0 baru (Oathbots/STAMP PASS/Agentic Gangster/AGENT MAO/AgentForge semua sudah dikenal/dieksklusi). "
    "WFPASS sellout 500/500 sudah dilaporkan hot-leg 0654. Tidak ada eksekusi (tidak ada preview/mint)."
)
snap["last_run"] = "2026-11-12 07:31 WIB"
snap["last_run_wib"] = "2026-11-12 07:31 WIB"
snap["last_run_note"] = snap["runNote0731"]
json.dump(snap, open(snap_path, "w"), indent=1)
out = {"merged_updates": updates, "run_note": snap["runNote0731"][:200]}
json.dump(out, open(BASE + "run-2026-11-12-0731-final.json", "w"), indent=1)
print(json.dumps(out, indent=1))
