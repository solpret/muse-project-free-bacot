#!/usr/bin/env python3
"""Merge run 2026-11-08 21:31 WIB (2131) into onchain-snapshot.json.
Route-1 reread + velocity (2031 pattern, totalSupply-based); focus updates;
SHACHO CLUB same-owner-discarded (owner 0x11038f4a... in discards, parent
verified); Jinchan free pool exhausted -> sold-out-free; TRACE website
evidence; Agent World / Agent Zet / Believers -> excluded; 5c checked +4.
Watermark NOT touched (backfill owns it; backfill still running despite user
disabling it 06:28 WIB — flagged, not changed here). Seen file NOT touched
(0 new first-seen after dedupe correction). Track_c reread TOTAL FAIL 72/72
(dataseed) -> no track_c updates. Never touches pending_claims.
Read-only except snapshot + same-owner-discards + track-c-scan-checked writes."""
import json, os, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN_WIB = "2026-11-08 21:31 WIB"
NOW_WIB = "2026-11-08 22:0x WIB"

def load(p):
    with open(p) as f: return json.load(f)
def save(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w") as f: json.dump(obj, f, indent=1)
    os.replace(tmp, p)

shutil.copy(BASE + "/onchain-snapshot.json", BASE + "/onchain-snapshot.json.bak-2131-premerge")
snap = load(BASE + "/onchain-snapshot.json")
rr = load(BASE + "/run-2026-11-08-2131-reread.json")
mi = load(BASE + "/run-2026-11-08-2131-merge-input.json")
tri = load(BASE + "/run-2026-11-08-2131-shacho-triage.json")
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

# ---- Route 1: reread updates + velocity (2031 pattern) ----
changed, degraded, vel_pass = [], 0, []
PREV_BLOCK = 132404126  # run 2031 read block
INTERVAL_MIN = (rr.get("block", 132409469) - PREV_BLOCK) * 0.45 / 60.0
SKIP = {"NUMBI"}  # backfill wrote fresher data (lastReadBlock 132410826 > 132409469)
for name, d in rr.get("reread", {}).items():
    if name in SKIP:
        continue
    old = contracts.get(name)
    if old is None:
        continue
    nts = d.get("totalSupply")
    # always refresh non-null free/balance views + read markers
    for f in ("totalMinted", "freeClaimed", "freeMinted", "balanceOf_user"):
        if d.get(f) is not None:
            old[f] = d[f]
    old["lastReadBlock"] = rr.get("block")
    old["lastReadWib"] = RUN_WIB
    if nts is None:
        degraded += 1
        continue
    ots = old.get("totalSupply")
    if ots is None:
        old["totalSupply"] = nts
        continue
    if nts != ots:
        minted = nts - ots
        old_rate = old.get("currentRatePerMin")
        base = old_rate if old_rate is not None else old.get("previousRatePerMin")
        rate = minted / INTERVAL_MIN if INTERVAL_MIN else 0.0
        ratio = (rate / base) if base else None
        passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        old["previousTotalSupply"] = ots
        old["totalSupply"] = nts
        old["mintedInInterval"] = minted
        old["intervalMinutes"] = round(INTERVAL_MIN, 1)
        if old_rate is not None:
            old["previousRatePerMin"] = old_rate
        old["currentRatePerMin"] = round(rate, 4)
        old["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        old["velocityLegPasses"] = passes
        changed.append((name, ots, nts, minted, passes, old.get("status")))
        if passes:
            vel_pass.append((name, minted, round(ratio, 2)))
    else:
        old["mintedInInterval"] = 0
        old["currentRatePerMin"] = 0.0
        old["velocityLegPasses"] = False

# ---- Focus updates (merge-input, fresher reads) ----
focus = mi.get("updates", {})
for name, u in focus.items():
    old = contracts.get(name)
    if old is None:
        continue
    if u.get("totalMinted") is not None:
        old["totalMinted"] = u["totalMinted"]
    if u.get("freeMinted") is not None:
        old["freeMinted"] = u["freeMinted"]
    if u.get("totalSupply") is not None:
        old["totalSupply"] = u["totalSupply"]
    if u.get("freePct") is not None and isinstance(u.get("freePct"), (int, float)):
        old["freePctVerified"] = u["freePct"]

# BAHUANG2: slot user verified fresh OPEN (focus read)
if "BAHUANG2" in contracts:
    contracts["BAHUANG2"]["freeCount_user_fresh"] = 0
    contracts["BAHUANG2"]["user_slot"] = "OPEN (fresh 2131)"
    contracts["BAHUANG2"]["runNote2131_1108"] = (
        "Run 2131: freeMinted 974->1030/3000 = 34,33% (>=25%), slot user OPEN segar "
        "(freeCount=0), umur ~4,3 jam (mintStart 2026-11-07 17:21:33 WIB). 3 kaki strong lead "
        "TERPENUHI tapi gate website TETAP GAGAL (metode A/G/H/J/M, run 2131) -> tetap "
        "gate-blocked, TIDAK preview/mint.")
# Pokechain / HELIX / Pressure readings
if "Pokechain" in contracts:
    contracts["Pokechain"]["runNote2131_1108"] = (
        "Run 2131: totalMinted 327->1067 (+740); gate website TETAP TERVERIFIKASI "
        "(pokechain.trade /js/app.js MINT_CA persis, re-verifikasi 21:40 WIB); bentuk gratis "
        "TETAP UNVERIFIED on-chain (Sourcify 404, tanpa selector freeMint) -> tetap early lead, bukan kandidat/strong.")
if "HELIX" in contracts:
    contracts["HELIX"]["runNote2131_1108"] = (
        "Run 2131: totalSupply 182->290 (+108), velocity GAGAL (1,02x); free% TETAP UNVERIFIED; "
        "gate website TETAP GAGAL (helixx.live = 0G-chain, bukan BSC) -> tetap early lead, bukan kandidat/strong.")
if "Pressure" in contracts:
    contracts["Pressure"]["runNote2131_1108"] = (
        "Run 2131: freeMinted tetap 5/1000 (0,5%), tanpa perubahan; gate website TETAP GAGAL "
        "(metode A/G/H/J: tanpa contractURI, tanpa fungsi website di ABI) -> tetap early lead.")
if "HIVE Agents" in contracts:
    contracts["HIVE Agents"]["runNote2131_1108"] = (
        "Run 2131: totalSupply tetap 1256, balanceOf(user)=1, status minted-by-user - tanpa perubahan.")
if "402" in contracts:
    contracts["402"]["runNote2131_1108"] = (
        "Run 2131: freeMinted 394/402 = 98% (8 tersisa), user sudah mint - tanpa promosi.")
if "GLOOP" in contracts:
    contracts["GLOOP"]["runNote2131_1108"] = (
        "Run 2131: totalMinted 1828/2000 (fast lane; Boltbook 1796, ~530/jam, tutup dekat 23:00 WIB); "
        "free% UNVERIFIED -> tetap early lead, tanpa promosi. Market resmi: 81 listing live, gloopagent.xyz.")
if "NUMBI" in contracts:
    contracts["NUMBI"]["runNote2131_1108"] = (
        "Run 2131: LAUNCHED (first mint 21:01:34 WIB blok 132405024, terverifikasi Ankr); "
        "freeMinted 64, FREE_POOL 3000 (~2,1% <25%), slot user TERBUKA (freeUsed=0, mintedCount=0); "
        "jalur gratis via freeMint(uint256,bytes) butuh bukti bytes (puzzleSigner) -> quote=0 belum terverifikasi. "
        "Sudah dilaporkan sebagai EARLY LEAD oleh backfill 21:16 WIB (tag temuan backfill) -> TIDAK dilaporkan ulang. "
        "Bukan strong lead/kandidat, TIDAK preview/mint. Bacaan snapshot dipertahankan (backfill 21:47 WIB lebih segar).")

# ---- Jinchan: free pool exhausted -> sold-out-free ----
if "Jinchan" in contracts:
    jc = contracts["Jinchan"]
    jc["totalMinted"] = tri["jinchan"].get("totalMinted") or jc.get("totalMinted")
    jc["FREE_SUPPLY"] = 777
    jc["status"] = "sold-out-free-2026-11-08"
    jc["runNote2131_1108"] = (
        "Run 2131: FREE POOL HABIS (777/777) - Boltbook 777/777 + freeMint() sim revert FreeSoldOut + "
        "totalMinted 838 (777 free + 61 paid); mintOpen MASIH 1 (flag menipu). User pegang 1 (minted-by-user). "
        "Status diubah minted-by-user -> sold-out-free; dilaporkan sekali sebagai perubahan status.")

# ---- TRACE: website evidence (B sweep) ----
if "bridge-0xe5e2c437" in contracts:
    tr = contracts["bridge-0xe5e2c437"]
    tr["websiteEvidence"] = ("tracea.cc + /agent/skill.md + manifest CLI resmi 0.5.1 "
        "(trace-agent-cli-0.5.1.tgz package/config/deployment.json): NFT 0xe5E2c43746F3A5E713C246592095D7cf82E808Cc, "
        "identityRegistry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis. Terverifikasi run 2131.")
    tr["gateWebsite"] = "verified-2026-11-08-2131"
    tr["runNote2131_1108"] = (
        "Run 2131: GATE WEBSITE kini TERVERIFIKASI (tracea.cc -> CLI resmi -> manifest memuat NFT yang sama + "
        "registry persis). totalSupply 2832/21000, balanceOf(user)=1 (sudah dimiliki). Free% 15,32% <25%, umur launch "
        "replacement BELUM terverifikasi -> BUKAN lead baru, hanya update bukti gate untuk item bridge.")

# ---- SHACHO CLUB: same-owner-discarded (parent verified) ----
sh = tri["shacho"]
contracts["SHACHO CLUB"] = {
    "address": sh["address"],
    "status": "promotion-discarded-same-owner-2026-11-08",
    "name": "SHACHO CLUB",
    "symbol": "SHACHO",
    "kind": "ERC721",
    "totalSupply": sh.get("totalSupply"),
    "freeLeft": sh.get("freeLeft"),
    "price": sh.get("price"),
    "agentIds": sh.get("agentIds"),
    "agentRegistry_exact": True,
    "owner": sh.get("owner"),
    "ownerInDiscards": True,
    "firstMintBlock": sh.get("first_mint_block"),
    "firstMintWib": sh.get("first_mint_wib"),
    "costOf_user_1": sh.get("costOf_user_1"),
    "mintedBy_user": sh.get("mintedBy_user"),
    "mintsLeft_user": sh.get("mintsLeft_user"),
    "saleShape": "S1 (mint + costOf/price + freeLeft/freeOf + agentIds registry)",
    "lastReadBlock": 132413846,
    "lastReadWib": RUN_WIB,
    "runNote2131_1108": (
        "Run 2131: SALE-S1 dari feed Sourcify (verifiedAt 14:14:14Z) + triase backfill agent-shaped, TAPI owner "
        "0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd = gelombang 0x1103 (ADA di same-owner-discards sejak 2026-11-06) "
        "-> SAME-OWNER-DISCARDED, TIDAK PERNAH dipromosikan/dilaporkan sebagai lead. First mint terverifikasi parent "
        "21:13:44 WIB blok 132406645 (187 mint), freeLeft 1701, costOf(user,1)=0, mintsLeft(user)=10, price 0,0002 BNB. "
        "Boltbook Batch #43 menyebut SHACHO CLUB #61 (diskusi ada) tapi status discard mengalahkan. TIDAK preview/mint."),
}

# ---- Excluded: Agent World / Agent Zet / Believers ----
ex = snap.setdefault("excluded", {})
ex["Agent World"] = {
    "address": "0x931B026F06D9229a25409dD02C99B8517437cb8c",
    "symbol": "Agent World Heroes",
    "track": "A", "status": "excluded-paid-fee-2026-11-08",
    "note": ("Sweep run 2131: agentworldbnb.com (launch 2026-11-08), X @AgentWorldBNB. 'Free mint' memungut "
             "freeMintFeeWei 0,000675 BNB (terbukti di ABI: claimFree/freeMintFeeWei/event FreeMintFeePaid) -> "
             "gagal kriteria gas-only. Website terverifikasi tapi BUKAN kandidat. Jangan preview/mint sebagai free."),
}
ex["Agent Zet"] = {
    "address": "0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37",
    "symbol": "Agent Zet",
    "track": "A", "status": "excluded-free-pool-exhausted-2026-11-08",
    "note": ("Sweep run 2131: agentzet.vercel.app, free phase SELESAI 4.000/4.000, 0 free slot tersisa, "
             "4.124/4.444 minted, mint kedua berbayar 0,001 BNB. Sudah tercatat di hot-leg-seen sejak 2026-11-02."),
}
ex["Believers"] = {
    "address": None,
    "symbol": "Believers",
    "track": "A", "status": "excluded-sold-out-2026-11-08",
    "note": ("Sweep run 2131: believers-virid.vercel.app, koleksi gratis 1.111 untuk pemegang Agent ID, "
             "SUDAH SOLD OUT 1.111/1.111, mint tutup permanen."),
}

# ---- same-owner-discards.json: append SHACHO CLUB ----
shutil.copy(BASE + "/same-owner-discards.json", BASE + "/same-owner-discards.json.bak-2131-premerge")
disc = load(BASE + "/same-owner-discards.json")
if not any((x.get("contract") or "").lower() == sh["address"].lower() for x in disc):
    disc.append({
        "contract": sh["address"],
        "discarded_wib": "2026-11-08T22:0x:00+07:00",
        "owner": sh["owner"],
        "owner_source": "run log free-mint-search 2026-11-08 21:31 WIB (run 2131) + verifikasi parent owner()",
        "project": "SHACHO CLUB",
        "reason": ("owner 0x1103 sama dengan gelombang costOf/mintsLeft (Toucan Play/jelly.exe/Los Flamingos/dll) "
                   "— SALE-S1 feed Sourcify + triase backfill agent-shaped, first mint terverifikasi 21:13:44 WIB, "
                   "freeLeft 1701, costOf(user,1)=0 — hasil screening dibuang aturan same-owner, tidak dilaporkan ke user"),
    })
    save(BASE + "/same-owner-discards.json", disc)

# ---- track-c-scan-checked.json: append 4 new 5c-checked ----
shutil.copy(BASE + "/track-c-scan-checked.json", BASE + "/track-c-scan-checked.json.bak-2131-premerge")
chk = load(BASE + "/track-c-scan-checked.json")
lst = chk.setdefault("checked", [])
added = 0
for a in mi.get("track_c_5c_new_checked", []):
    if a not in lst:
        lst.append(a)
        added += 1
save(BASE + "/track-c-scan-checked.json", chk)

# ---- Top-level run notes ----
snap["runNote2131_1108"] = (
    "Run 2131 (21:31-~22:0x WIB): 0 kandidat, 0 strong lead baru di-mint, 0 early lead BARU, 0 track-C lead/kandidat, "
    "0 pending claim baru/terbuka/gagal. Scan SUKSES (pre-flight retry; window 132409084-132410083, 40 Ankr calls, "
    "0 error, 128 NFT/1367 mint; 0 first-seen setelah koreksi dedupe). Re-read 541 kontrak blok 132409469 "
    f"({len(changed)} perubahan supply, {degraded} degraded, velocity-pass tanpa promosi: "
    + ", ".join(n for n, _, _ in vel_pass) + "). "
    "SHACHO CLUB 0x26E0... SALE-S1 -> SAME-OWNER-DISCARDED (owner 0x1103, parent verified, TIDAK dilaporkan). "
    "Jinchan free pool HABIS 777/777 -> sold-out-free (dilaporkan sekali). NUMBI launched (sudah dilaporkan backfill 21:16). "
    "BAHUANG2 34,33% gate-blocked; Pokechain gate verified; HELIX/Pressure/NUSA gate tetap gagal. "
    "Agent World berbayar (excluded), Agent Zet pool habis (excluded), Believers sold out (excluded). "
    "TRACE gate website kini terverifikasi (tracea.cc manifest). Track_c re-read GAGAL TOTAL 72/72 (dataseed) -> unverified. "
    "Binanceai tetap refund phase. Backfill MASIH AKTIF (file 21:57 WIB) padahal user perintahkan nonaktifkan 06:28 WIB - perlu penonaktifan oleh main agent/user. "
    "Watermark TIDAK dimajukan (backfill owns it); seen file TIDAK disentuh.")
snap["last_run_wib"] = RUN_WIB
snap["last_run"] = "free-mint-search 2026-11-08 2131 WIB"
snap["last_run_note"] = snap["runNote2131_1108"]

save(BASE + "/onchain-snapshot.json", snap)
print(f"MERGE DONE: contracts={len(contracts)} track_c={len(track_c)} changed={len(changed)} "
      f"degraded={degraded} vel_pass={len(vel_pass)} 5c_added={added}")
print("changed sample:", changed[:8])
print("vel_pass:", vel_pass)
