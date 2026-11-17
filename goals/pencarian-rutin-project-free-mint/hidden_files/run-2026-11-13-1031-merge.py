#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 10:31 WIB.
Reads run-2026-11-13-1031-verify.json + discovery.json + triage*.json,
updates onchain-snapshot.json (backup first).
REPORTABLE CHANGE: 1 new EARLY lead - Royal Rush Agents 0x2e34 (agent-shaped,
website verified, slot open, free 6/1000 = 0.6%; age + first-mint block/time
UNVERIFIED - log sources down). No candidate / strong lead / track-B change /
track-C lead this run. No preview/mint (early leads never preview/mint).
Velocity convention: same as run 0931/1001 (previousRatePerMin frozen as
stored; question flagged for parent, NOT changed here)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "1031"
v = json.load(open(BASE + f"run-2026-11-13-{RUN}-verify.json"))
d = json.load(open(BASE + f"run-2026-11-13-{RUN}-discovery.json"))
reads = v["reads"]
block = v.get("block")
snap = json.load(open(BASE + "onchain-snapshot.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + f"onchain-snapshot-2026-11-13-{RUN}.bak")
C = snap["contracts"]
TC = snap["track_c"]
NOTE = "Run 1031 (blok %s): " % block

def vel(prev_ts, new_ts, prev_rate, minutes=30.0):
    minted = (new_ts - prev_ts) if (prev_ts is not None and new_ts is not None) else None
    rate = (minted / minutes) if minted is not None else None
    ratio = (rate / prev_rate) if (rate is not None and prev_rate) else None
    passes = bool(minted is not None and minted >= 20 and ratio is not None and ratio >= 1.5)
    return minted, rate, ratio, passes

# --- Agentx ---
a = C["Agentx"]
new_tm = reads["Agentx"]["summary"].get("totalMinted")
minted, rate, ratio, passes = vel(668, new_tm, a.get("previousRatePerMin") or 0.18)
a["previousTotalSupply"] = 668
a["totalSupply"] = new_tm
a["freeClaimed"] = reads["Agentx"]["summary"].get("freeMinted")
a["mintedInInterval"] = minted
a["intervalMinutes"] = 30.0
a["currentRatePerMin"] = round(rate, 3) if rate is not None else None
a["velocityRatio"] = round(ratio, 2) if ratio is not None else None
a["velocityLegPasses"] = passes
a["lastReadBlock"] = block
a["lastReadWib"] = "2026-11-13 ~10:32 WIB"
a["runNote1031"] = (NOTE + "totalMinted 668->%s (+%s, %.2f/mnt vs prev 0.18 = %.2fx, <20 token) -> velocity GAGAL; "
                    "free %s/1111 = %.1f%% (<70%% strong lead); slot terbuka (freeClaimed_user=0); "
                    "umur ~11,3 jam (mintOpensAt 2026-11-12 23:11 WIB) <24 jam; gate-blocked SUDAH dilaporkan 13 Nov 08:01 - DIAM." %
                    (new_tm, minted, rate, ratio if ratio else 0, a["freeClaimed"],
                     100.0 * a["freeClaimed"] / 1111))

# --- Zero ---
z = C["Zero"]
new_tm = reads["Zero"]["summary"].get("totalMinted")
minted, rate, ratio, passes = vel(217, new_tm, z.get("previousRatePerMin") or 2.42)
z["previousTotalSupply"] = 217
z["totalSupply"] = new_tm
z["freeClaimed"] = reads["Zero"]["summary"].get("freeMinted")
z["mintedInInterval"] = minted
z["intervalMinutes"] = 30.0
z["currentRatePerMin"] = round(rate, 3) if rate is not None else None
z["velocityRatio"] = round(ratio, 2) if ratio is not None else None
z["velocityLegPasses"] = passes
z["lastReadBlock"] = block
z["lastReadWib"] = "2026-11-13 ~10:32 WIB"
z["runNote1031"] = (NOTE + "totalMinted 217->%s (+%s, %.2f/mnt vs prev 2.42 = %.2fx, <20 token) -> velocity GAGAL; "
                    "free %s/500 = %.1f%% (<50%% kandidat, <70%% strong lead); slot TERBUKA; "
                    "umur ~2,7 jam (mintOpensAt 2026-11-13 07:55 WIB) <24 jam; "
                    "website tetap UNVERIFIED. BUKAN kandidat, BUKAN strong lead. DIAM." %
                    (new_tm, minted, rate, ratio or 0, z["freeClaimed"],
                     100.0 * z["freeClaimed"] / 500))

# --- Oliver Agents ---
o = C["Oliver Agents"]
new_ts = reads["OLIVER"]["summary"].get("totalSupply")
new_free = reads["OLIVER"]["summary"].get("freeMinted")
minted, rate, ratio, passes = vel(955, new_ts, o.get("previousRatePerMin") or 0.0)
o["previousTotalSupply"] = 955
o["totalSupply"] = new_ts
o["freeClaimed"] = new_free
o["mintedInInterval"] = minted
o["intervalMinutes"] = 30.0
o["currentRatePerMin"] = round(rate, 3) if rate is not None else None
o["velocityRatio"] = ratio
o["velocityLegPasses"] = False
o["lastReadBlock"] = block
o["lastReadWib"] = "2026-11-13 ~10:32 WIB"
o["runNote1031"] = (NOTE + "totalSupply 955->%s (+%s), freeMinted %s/1000 = %.1f%%, freeRemaining %s, paid beku 50; "
                    "velocity TIDAK lulus (<20 token); umur launch TETAP UNVERIFIED "
                    "-> TIDAK BISA promosi ke strong lead walau >70%% + website lolos + slot terbuka. Watchlist-only, DIAM." %
                    (new_ts, minted, new_free, 100.0 * new_free / 1000,
                     reads["OLIVER"]["summary"].get("freeRemaining")))

# --- track_c: JNTM / OBFG / NOTV / AgentMuse ---
j = TC["JNTM"]
jr = reads["JNTM"]["summary"]
j["freeClaimed"] = jr.get("freeClaimed")
j["totalMinted"] = jr.get("totalMinted")
j["paidMinted"] = jr.get("paidMinted")
j["lastReadBlock"] = block
j["lastReadWib"] = "2026-11-13 ~10:32 WIB"
j["runNote1031"] = (NOTE + "free 370->430/1000 = 43,0%%; paidMinted 68 FLAT (totalMinted 498); quote NULL TETAP; "
                    "slot terbuka; umur ~4,3 jam (mintStart 2026-11-13 06:13 WIB) <24 jam. Gate PENDING (L) + quote NULL - tanpa perubahan tier. DIAM.")
ob = TC["OBFG"]
obr = reads["OBFG"]["summary"]
ob["totalSupply"] = obr.get("totalSupply")
ob["freeClaimed"] = obr.get("freeMinted")
ob["lastReadBlock"] = block
ob["lastReadWib"] = "2026-11-13 ~10:32 WIB"
ob["runNote1031"] = (NOTE + "totalSupply 643->646/1230 = 52,5%%; slot terbuka (freeAvailable=1); umur ~14,5 jam (saleStart 2026-11-12 20:01 WIB) <24 jam. "
                    "Gate-blocked SUDAH dilaporkan 12 Nov. DIAM.")
nt = TC["NOTV"]
nt["totalSupply"] = reads["NOTV"]["summary"].get("totalSupply")
nt["lastReadBlock"] = block
nt["lastReadWib"] = "2026-11-13 ~10:32 WIB"
nt["runNote1031"] = (NOTE + "totalSupply 0, freeStart 1794567600 = 18:00 WIB 13 Nov - BELUM BUKA. DIAM.")
am = TC["AgentMuse"]
amr = reads["AgentMuse"]["summary"]
am["freeClaimed"] = amr.get("freeClaimed")
am["bookedOf_user"] = amr.get("bookedOf_user")
am["lastReadBlock"] = block
am["lastReadWib"] = "2026-11-13 ~10:32 WIB"
am["runNote1031"] = (NOTE + "freeClaimed 244->261/888 = 29,4%%; bookedOf(user)=FREE_OSK utuh; minted-by-user. DIAM.")

# --- NEW EARLY LEAD: Royal Rush Agents ---
C["Royal Rush Agents"] = {
    "address": "0x2e34d33256C920C33b2a03FEC132A2c74061d5D3",
    "name": "Royal Rush Agents",
    "symbol": "RRAGENTS",
    "kind": "ERC721",
    "status": "early-lead-reported-2026-11-13",
    "totalSupply": 6,
    "totalMinted": 6,
    "freeMinted": 6,
    "freeRemaining": 994,
    "FREE_MAX": 1000,
    "MAX_SUPPLY": 5000,
    "mintOpen": 1,
    "mintPrice": 1000000000000000,
    "paidMinted": 0,
    "mintedCount": 56,
    "FREE_TOKEN_REWARD": 3000000000000000000000,
    "AGENT_ID_REGISTRY": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "token": "0xcD39001B6D2b8f6f1F99cA756F6CdDd833cfb666",
    "owner": "0xbc8f04b7fd68bbe4c2c298a63d20da0962879ced",
    "freeClaimedByAgent_user": 0,
    "balanceOf_user": 0,
    "userSlotNote": "Slot TERBUKA: freeClaimedByAgent(user bytes32)=0, balanceOf(user)=0, mintOpen=1.",
    "website": "https://royalrushagents.pages.dev",
    "websiteNote": "VERIFIED run 1031 via tokenURI (meta/5.json external_url) + config.js site mencetak CONTRACT_ADDRESS 0x2e34... + TOKEN_ADDRESS 0xcD39... persis; site live HTTP 200 37.808 byte (fetch pertama 522 transient).",
    "tokenURI_1": "https://royalrushagents.pages.dev/meta/5.json",
    "tokenURI_note": "Token #5 Mythic, Power 1000, Rarity Odds 3%, external_url = site.",
    "firstSeenBlock": 133281880,
    "firstSeenWib": "2026-11-13 ~10:36 WIB",
    "sourcifyVerifiedAt": "2026-11-13T03:35:49Z",
    "ageVerified": False,
    "ageNote": "Umur launch UNVERIFIED: tidak ada mintStart/mintOpensAt view; first-mint block/time unverified (Ankr 401 + dataseed eth_getLogs limit-exceeded/timeout); Sourcify verifiedAt BUKAN launch time; tidak ada stated launch time di site. TIDAK BISA promosi ke strong lead/kandidat sampai umur terverifikasi.",
    "firstMintNote": "First mints terverifikasi parsial: totalSupply/freeMinted = 6 dibaca live on-chain run ini (minting berjalan, first-seen run ini); blok/waktu first mint TIDAK terverifikasi (log sources down).",
    "xDiscussion": "unverified",
    "xNote": "Tidak ada akun X di site (tanpa link x.com/twitter); pencarian 'Royal Rush Agents' tidak menemukan postingan/diskusi proyek (hanya game Rush Royale dll + proyek lain yang sudah dikenal). X unverified - bukan blocker untuk tier EARLY.",
    "freePct": 0.6,
    "freePctNote": "6/1000 FREE_MAX (verified on-chain run 1031, blok 133280683).",
    "velocityLegPasses": False,
    "velocityNote": "Baseline pertama run 1031 (totalSupply 6); velocity belum bisa dihitung - butuh bacaan run berikut.",
    "previousTotalSupply": 6,
    "previousRatePerMin": None,
    "currentRatePerMin": None,
    "lastReadBlock": block,
    "lastReadWib": "2026-11-13 ~10:32 WIB",
    "runNote1031": (NOTE + "EARLY LEAD BARU (dilaporkan sekali run ini): Royal Rush Agents 0x2e34, Sourcify verifiedAt 10:35:49 WIB (dalam run), "
                    "agent-shaped (AGENT_ID_REGISTRY = registry, mintFree + free views), totalSupply/freeMinted 6/1000 = 0,6%%, slot user TERBUKA, "
                    "website VERIFIED (royalrushagents.pages.dev, config.js mencetak kedua kontrak persis). Umur + first-mint block/time UNVERIFIED (log sources down). "
                    "BUKAN kandidat (0,6%% << 50%%, velocity belum ada baseline, umur unverified, X unverified), BUKAN strong lead. TIDAK di-preview / TIDAK di-mint (early lead tidak pernah).")
}

# --- top-level run note ---
snap["runNote1031"] = (
    NOTE + "AgentLabs totalSpecimens 1732->1822 (exp 2 berjalan); OUTY freeSold 20 FLAT/1500, FREE_FEE 0,0001 BNB TETAP bukan gas-only; "
    "MECHA freeClaimed 1909->1914/4444=43,1%% (<50%%); Pickgrid freeMinted 216/300 FLAT, umur UNVERIFIED; "
    "PX24/SKRR/ME30/CY24 totalSupply 520/509/270/456, umur TETAP UNVERIFIED; HIVE 1263 flat, bal_user=1; "
    "DragonAgent 967->968, free views NULL; BC1B freeCount 462 FLAT; binanceai.fun launched()=0, tokenClaimed(user)=0 - tetap pending. "
    "EARLY LEAD BARU: Royal Rush Agents (lihat entry snapshot; dilaporkan sekali run ini). "
    "Sourcify feed 20, SEMUA 20 baru vs hot-leg-seen (verifiedAt 03:35:01-03:35:50Z, burst 50 detik): 17 shape-check via Sourcify ABI OK (rute singular PULIH run ini - hot-leg 1014 'rusak' ternyata transient; 16x template 28 fns mint-only tanpa free/agent + 0x2e34 Royal Rush 83 fns agent-shaped; 0xC291 26 fns mint-only), "
    "3 gagal parse Sourcify -> selector-probe: 0xcD39 = token reward Royal Rush (token() NFT, mint(address,uint256) saja), 0xeD67/0xe43C probe-negative (22962 byte, tanpa mint/quote/free/agent). 0 sale-shape S1/S2 baru. "
    "Boltbook EN 43216 byte / ZH 41680 byte, 15/15 alamat, 1 'baru' vs hot-leg-seen TAPI false positive: 0x3071... = 40 hex pertama hash tx penjualan RUNE di post rizeiki.ai (BUKAN alamat kontrak). 0 lead baru dari Boltbook. "
    "Bridge (cek manual inline, struktur {seeded,writer,contracts}): 116 kontrak, 0 not-in-snapshot (by address), 7 same-owner-discarded - tanpa promosi. "
    "Scan leg FAST-FAIL: Ankr pre-flight HTTP 401 (outage sejak 9 Nov, ~4,5 hari); watermark TETAP 132512564; gap ke head 768.119 blok (head 133280683); 5c dilewati. "
    "Sweep EN+ZH: 0 baru <24 jam (Agentic Gangster/STAMP PASS/RIGBYPASS/AGENT COSMOS/TINY AGENTS/Burn Agent semua sudah dikenal dan/atau >24 jam). "
    "Odaily newsflash: tanpa item Agent ID free-mint (hanya berita market/BTC). "
    "LAPOR: 1 EARLY lead baru (Royal Rush Agents); selebihnya DIAM."
)
snap["timestamp_wib"] = "2026-11-13 ~10:47 WIB"
snap["last_run_wib"] = "2026-11-13 ~10:47 WIB"
snap["last_run_note"] = "Run 1031: 1 EARLY lead baru Royal Rush Agents (dilaporkan sekali); selebihnya diam. Scan Ankr 401 fast-fail (watermark 132512564, gap 768.119 blok)."
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; block", block, "; snapshot ts 10:47 WIB")
print("Agentx free", C["Agentx"]["freeClaimed"], "Zero free", C["Zero"]["freeClaimed"],
      "Oliver free", C["Oliver Agents"]["freeClaimed"], "JNTM free", TC["JNTM"]["freeClaimed"],
      "OBFG", TC["OBFG"]["totalSupply"], "RRA free", C["Royal Rush Agents"]["freeMinted"])
