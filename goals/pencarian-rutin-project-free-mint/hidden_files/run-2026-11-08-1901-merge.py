#!/usr/bin/env python3
"""Merge run 2026-11-08 19:01 WIB into onchain-snapshot.json + seen + scan state.
Route-1 reread updates + velocity, Paw Gang sellout removal, Abyssagent sold-out
mark, Zorrie early-lead entry (if first mint verified), NUMBI upcoming entry,
scan triage, 5c checked update. Read-only except for the state files it owns.
Never touches bridge file. Watermark NOT advanced on partial scan."""
import json, sys, time, datetime, os
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
RUN_WIB = "2026-11-08 19:01 WIB"

def load(p):
    with open(p) as f: return json.load(f)
def save(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w") as f: json.dump(obj, f, indent=1)
    os.replace(tmp, p)

snap = load(BASE + "/onchain-snapshot.json")
rr = load(BASE + "/run-2026-11-08-1901-reread.json")
try:
    scan = load(BASE + "/onchain-scan-2026-11-08-1901.json")
except Exception as e:
    scan = {"contracts": [], "erc20_mint_contracts": {}, "partial": True, "errors": [str(e)]}
seen = load(BASE + "/onchain-scan-seen.json")
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

# ---- Route 1: reread updates + velocity (convention run 1801: base = currentRatePerMin, interval block-based) ----
changed, degraded, vel_pass = [], 0, []
PREV_BLOCK = 132385176  # run 1831 read block
INTERVAL_MIN = (rr.get("block", 132389206) - PREV_BLOCK) * 0.45 / 60.0
for name, d in rr.get("reread", {}).items():
    old = contracts.get(name)
    if old is None:
        continue
    nts = d.get("totalSupply")
    if nts is None:
        degraded += 1
        continue
    ots = old.get("totalSupply")
    if ots is None:
        old["totalSupply"] = nts
        old["lastReadBlock"] = rr.get("block")
        old["lastReadWib"] = RUN_WIB
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
        old["lastReadBlock"] = rr.get("block")
        old["lastReadWib"] = RUN_WIB
        if d.get("freeClaimed") is not None:
            old["freeClaimed"] = d["freeClaimed"]
        if d.get("balanceOf_user") is not None:
            old["balanceOf_user"] = d["balanceOf_user"]
        changed.append((name, ots, nts, minted, passes, old.get("status")))
        if passes:
            vel_pass.append((name, minted, round(ratio, 2)))
    else:
        old["lastReadBlock"] = rr.get("block")
        old["lastReadWib"] = RUN_WIB
        old["mintedInInterval"] = 0
        old["currentRatePerMin"] = 0.0
        old["velocityLegPasses"] = False
        if d.get("freeClaimed") is not None:
            old["freeClaimed"] = d["freeClaimed"]
        if d.get("balanceOf_user") is not None:
            old["balanceOf_user"] = d["balanceOf_user"]

# ---- Track C reread updates ----
for name, d in rr.get("track_c", {}).items():
    old = track_c.get(name)
    if isinstance(old, dict) and d.get("freeMinted") is not None:
        if old.get("freeMinted") != d["freeMinted"]:
            old["freeMinted"] = d["freeMinted"]
            old["lastReadWib"] = RUN_WIB
            old["lastReadBlock"] = rr.get("block")

# ---- Paw Gang sellout: strong lead -> report once + remove ----
paw = contracts.get("Paw Gang")
paw_sold_out = False
if paw is not None:
    paw_total = rr.get("reread", {}).get("Paw Gang", {}).get("totalMinted")
    if paw_total is not None and paw_total >= 3333:
        paw_sold_out = True
        del contracts["Paw Gang"]
print("Paw Gang sold out, removed:", paw_sold_out, flush=True)

# ---- Abyssagent sold out: same-owner-discarded -> mark sold-out, keep entry, no report ----
ab = contracts.get("Abyssagent")
if ab is not None:
    ab_total = rr.get("reread", {}).get("Abyssagent", {}).get("totalSupply")
    ab_free = rr.get("reread", {}).get("Abyssagent", {}).get("freeClaimed")
    if ab_total is not None:
        ab["totalSupply"] = ab_total
    if ab_free is not None:
        ab["freeClaimed"] = ab_free
    ab["lastReadBlock"] = rr.get("block")
    ab["lastReadWib"] = RUN_WIB
    if ab_total == 4444:
        ab["status"] = "sold-out-2026-11-08-discarded"
        ab["selloutNote"] = ("Sold out 4.444/4.444 (freeClaimed 4.438) terverifikasi run 1901 blok "
                             "132389206; Boltbook konfirmasi 2 node blok 132387833/132388690. "
                             "Tetap same-owner-discarded (bukan lead) - TIDAK dilaporkan, hanya ditandai sold-out.")
print("Abyssagent:", ab.get("status") if ab else None, flush=True)

# ---- Zorrie early-lead entry (only if first mint verified on-chain) ----
zorrie_entry = None
try:
    zf = load(BASE + "/run-2026-11-08-1901-zorrie-firstmint.json")
    first_blk = zf.get("first_mint_block")
    first_ts = zf.get("first_mint_ts")
except Exception:
    first_blk, first_ts = None, None
if first_blk:
    def block_time_wib(blk):
        for ep in EPS:
            try:
                r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                  "params": [hex(blk), False]}, timeout=10, retries=0)
                if r and r.get("result"):
                    ts = int(r["result"]["timestamp"], 16)
                    return datetime.datetime.fromtimestamp(
                        ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
            except Exception:
                continue
        return None
    first_wib = block_time_wib(first_blk)
    contracts["Zorrie"] = {
        "address": "0x47feee72353358a61618cE640265F9f406f88E47",
        "name": "Zorrie", "symbol": "ZORRIE", "kind": "ERC721",
        "status": "early-lead-reported-2026-11-08",
        "totalMinted": 6, "maxSupply": 5000, "mintOpen": 1,
        "freeMintedPerWallet_user": 0,
        "firstSeenBlock": first_blk, "firstMintWib": first_wib,
        "owner": "0x394f6bade236789d0a060e4bfd40501cd95345a5",
        "ownerInDiscards": False,
        "signer": "0xC07C2EC9c342F4bc0d883f697c4589aBa55780c2",
        "registryBytesInCode": False, "sourcify": "not_verified",
        "website": "https://zorrie.fun/mint",
        "websiteGate": "PASS (zorrie.fun/mint mencetak kontrak persis 0x47feee72353358a61618cE640265F9f406f88E47 + marketplace 0xa8B78207833AD551b492402c5ffbDE4f55Dbe0Cc)",
        "xVerified": False,
        "freePctVerified": 0.12,
        "freePctNote": "totalMinted 6/5000 = 0,12% (free mint semua; freeMintedPerWallet(user)=0, slot terbuka). JAUH di bawah 25% -> BUKAN strong lead, BUKAN kandidat.",
        "agentShapeNote": ("Agent-shaped via free-mint function: selector mintFree((address,uint256,uint256,bool),bytes)=0xd392ec0c "
                           "ADA di bytecode + freeMintedPerWallet + maxSupply; registry/AgentGate on-chain TIDAK ada (gate Agent ID "
                           "ditegakkan off-chain oleh API puzzle: otorisasi EIP-712 terikat wallet, signer() cocok dengan situs). "
                           "Sourcify BELUM terverifikasi."),
        "gateNote": ("Free path = selesaikan SAT puzzle (250 var, 5.500 klausa) via api.zorrie.fun -> otorisasi EIP-712 (10 mnt) -> "
                     "mintFree(auth, signature), value 0, gas only. Jalur berbayar $1,5 BNB (mintPaid) TIDAK dipakai. "
                     "Early lead TIDAK PERNAH di-preview/di-mint; promosi ke strong lead butuh >=25% free claimed."),
        "userBalance": 0,
        "lastReadBlock": rr.get("block"), "lastReadWib": RUN_WIB,
        "baselineNote": ("Boltbook front page EN+ZH run 1901 (post zorrie, 6 pertama sudah ter-mint) + zorrie.fun/mint "
                         "(kontrak + marketplace + prompt lengkap + ABI minimal). Verifikasi run ini: totalMinted 6, maxSupply 5000, "
                         "freeMintedPerWallet(user)=0, signer() cocok situs, quoteBypassWei 2148800448623692 wei (~$1,5). "
                         "First mint terverifikasi on-chain blok %s (%s)." % (first_blk, first_wib)),
    }
    zorrie_entry = True
print("Zorrie entry added:", zorrie_entry, "first block:", first_blk, flush=True)

# ---- NUMBI upcoming-prelaunch (Sourcify feed) ----
fv = load(BASE + "/run-2026-11-08-1901-feed-verify.json")
numbi = fv.get("0xeEdd6F512Fec64AD5A4aa64722ef6C5689937B50", {})
contracts["NUMBI"] = {
    "address": "0xeEdd6F512Fec64AD5A4aa64722ef6C5689937B50",
    "status": "upcoming-prelaunch-2026-11-08",
    "name": "NUMBI", "symbol": "NUMBI", "kind": "ERC721",
    "totalMinted": 0, "MAX_SUPPLY": 10000, "mintOpen": 0,
    "freeMinted": 0, "freeViews": ["FREE_POOL", "freeMint", "freeMinted", "freeUsed"],
    "agentRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "registryBytesInCode": True,
    "owner": "0x49d45e8a123d0d5e1d2a090a83fedac39c9c85b6",
    "ownerInDiscards": False,
    "sourcifyVerifiedAt": "2026-11-08T11:43:23Z",
    "lastReadWib": RUN_WIB,
    "baselineNote": ("Sourcify feed run 1901 (verifiedAt 11:43:23Z): shape mint + free [FREE_POOL, freeMint, freeMinted, freeUsed] "
                     "+ agentRegistry() = registry persis 0x60B926... + registry bytes. BELUM LAUNCH (totalMinted 0, mintOpen 0) -> "
                     "upcoming watchlist-only, BUKAN kandidat/lead, TIDAK di-preview/di-mint. Dipantau scan/hot-leg untuk first mint."),
}

# ---- Scan triage: newly-seen classification ----
seen_contracts = seen.setdefault("contracts", {})
snap_addrs = {(v.get("address") or "").lower() for v in contracts.values() if isinstance(v, dict)}
new_seen, agent_shaped_new, historic = [], [], 0
for c in scan.get("contracts", []):
    addr = (c.get("address") or "").lower()
    if not addr:
        continue
    if addr in seen_contracts or addr in snap_addrs:
        historic += 1
        continue
    new_seen.append(c)
    seen_contracts[addr] = {"first_seen_block": c.get("first_block"),
                            "first_seen_run": "2026-11-08-1901",
                            "mint_count_window": c.get("mint_count"),
                            "distinct_minters_window": c.get("distinct_minters")}
    if c.get("registry_bytes_hit"):
        agent_shaped_new.append(c)
save(BASE + "/onchain-scan-seen.json", seen)

# ---- Scan state / watermark ----
state = load(BASE + "/onchain-scan-state.json")
partial = bool(scan.get("partial", True))
state["last_scan_partial"] = partial
state["last_scan_wib"] = "2026-11-08 19:01-19:xx WIB"
state["last_scan_window_from"] = scan.get("from_block")
state["last_scan_window_to"] = scan.get("to_block")
state["last_scan_ankr_calls"] = scan.get("ankr_calls")
state["last_scan_errors"] = len(scan.get("errors", []))
state["last_scan_nft"] = len(scan.get("contracts", []))
state["last_scan_erc20_mint"] = scan.get("erc20_mint_contracts")
if not partial:
    state["last_scanned_block"] = scan.get("to_block")
    state["note"] = "Scan run 1901 OK (full); watermark advanced."
else:
    state["last_scan_partial_note"] = ("Scan run 1901 PARTIAL: partial=%s; watermark NOT advanced (tetap %s); "
                                       "run berikut retry window yang sama (cap 1000)." % (scan.get("partial"), state.get("last_scanned_block")))
save(BASE + "/onchain-scan-state.json", state)

# ---- 5c checked update ----
added5c = 0
try:
    five_c = load(BASE + "/run-2026-11-08-1901-5c.json")
    checked = load(BASE + "/track-c-scan-checked.json")
    checked_list = checked.get("checked", []) if isinstance(checked, dict) else checked
    checked_lower = {str(x).lower() for x in checked_list}
    for a in five_c.keys():
        if a.lower() not in checked_lower:
            checked_list.append(a)
            checked_lower.add(a.lower())
            added5c += 1
    if isinstance(checked, dict):
        checked["checked"] = checked_list
        save(BASE + "/track-c-scan-checked.json", checked)
    else:
        save(BASE + "/track-c-scan-checked.json", checked_list)
except Exception as e:
    five_c = {"error": str(e)}

# ---- Jinchan: minted-by-user (strong-lead direct mint, run 1901) ----
contracts["Jinchan"] = {
    "address": "0xccc127D1A7Ef1e385757784a9878F7279BF3B19D",
    "name": "Jinchan", "symbol": "JINCHAN", "kind": "ERC721",
    "status": "minted-by-user-2026-11-08",
    "totalMinted": 308, "freeMintedCount": 308, "freeRemaining": 469,
    "FREE_SUPPLY": 777, "MAX_SUPPLY": 3333, "mintOpen": 1,
    "opensAt": 1794139200, "mintEnd": 1794312000,
    "firstMintWib": "2026-11-08 19:00:00 WIB",
    "owner": "0x094d7a85c55dc117b61983f7b00edcfa7de70b65",
    "ownerInDiscards": False,
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "registryBytesInCode": True, "sourcify": "verified",
    "website": "https://jinchan888.fun/",
    "websiteGate": "PASS (jinchan888.fun mencetak kontrak NFT persis + token + marketplace + registry; dicapai via tokenURI(1) -> jinchan888.fun/metadata/1)",
    "xVerified": False,
    "freePctVerified": 38.2,
    "freePctNote": "freeMintedCount 297/777 = 38,2% saat eksekusi (19:26 WIB); 308/777 = 39,6% pasca-mint.",
    "userBalance": 1, "userTokenId": 305, "userTier": "Common",
    "mintTx": "0x74c508f4cc46b4cb8618d144c0ca972502ac3459d7803e0c40d61ec87f88d103",
    "mintBlock": 132392397, "mintGasUsed": 167477,
    "auditNote": "Binance audit saat mint: hasResult=false (TANPA HASIL, bukan lolos), isSupported=true, riskLevel -1, riskItems kosong, riskAlert null; GoPlus tanpa data (code 1). Tidak ada RISK hit.",
    "previewNote": "Preview bersih 000000000 (+1 ERC721 #305 + 50.000 JINCHAN, tanpa authority/allowance/risk); tokenId simulasi 301, aktual 305 (tier draw block-dependent).",
    "marketNote": ("Own market = marketplace built-in 0x7Cb7Fce1d512A6dF4ACB293B06CA4769484d2cA7 "
                   "(fee list 0,0001 BNB, min price 0,0001 BNB, royalty 5%) TAPI 0 live listings (getListing 1..10 kosong) -> TIDAK di-list."),
    "coinNote": ("Bonus 50.000 JINCHAN (token 0xE2DFa6c6c7189a885bC0919527A303319f4EEffC) diterima di tx mint; "
                 "pair PCS V2 belum ada (getPair = 0x0) -> ditahan, terdaftar PENDING SWAP (pending-swaps.json; LP buka saat sellout atau tutup window 2026-11-10 19:00 WIB)."),
    "lastReadBlock": rr.get("block"), "lastReadWib": RUN_WIB,
    "baselineNote": ("Scan run 1901 first-seen (window 132388446-132389445, 69 mint/69 minter); triase: Sourcify verified, "
                     "agentIdRegistry() = registry persis, freeMint() + FREE_SUPPLY 777; opensAt 1794139200 = 2026-11-08 19:00 WIB; "
                     "strong lead (umur terverifikasi, free% 38,2% >=25%, slot user terbuka) + website gate PASS -> direct mint 19:26 WIB."),
}

# ---- Gloop + Skunk Hollow: early leads (first-seen scan run 1901) ----
contracts["Gloop"] = {
    "address": "0x79d1821bC6E7576Aac4422BEAD0951A4adc7075a",
    "name": "Gloop", "symbol": "GLOOP", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-08",
    "totalMinted": 38, "TOTAL_SUPPLY": 3333, "mintOpen": 1,
    "MINT_START": 1794139200, "difficultyBits": 24,
    "firstSeenBlock": 132388582, "firstMintWib": "2026-11-08 19:00:00 WIB",
    "scanMints": 22, "scanMinters": 22,
    "owner": "0x72b9050747bc33d6fef0d76d49b0c7840da47e3b",
    "ownerInDiscards": False,
    "agentRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "registryBytesInCode": True, "sourcify": "verified",
    "website": None, "websiteVerified": False,
    "xVerified": False,
    "freePctVerified": None,
    "freePctNote": "UNVERIFIED: ABI tanpa free view (tanpa freeClaimed/freeMinted/FREE_SUPPLY); mint PoW-gated (difficultyBits 24, seperti Paw Gang).",
    "userBalance": 0, "hasMinted_user": 0,
    "lastReadBlock": rr.get("block"), "lastReadWib": RUN_WIB,
    "baselineNote": ("Scan run 1901 first-seen (window 132388446-132389445, 22 mint/22 minter); triase: Sourcify verified, "
                     "AGENT_REGISTRY() = registry persis, MINT_START 1794139200 = 2026-11-08 19:00 WIB (umur terverifikasi <=48 jam). "
                     "EARLY lead (dilaporkan sekali): free% UNVERIFIED, website UNVERIFIED; TIDAK di-preview/di-mint."),
}
contracts["Skunk Hollow"] = {
    "address": "0x88E4b613609af6C479F11D78e5a696d84B78993B",
    "name": "Skunk Hollow Skunk", "symbol": "DEN", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-08",
    "totalSkunksMinted": 117, "FREE_SKUNKS_TOTAL": 2500,
    "freeSkunksRemaining": 2383, "freeSkunksClaimed": 117,
    "freeWindowOpen": 1, "freeWindowClosesAt": 1794225615, "gateStart": 1794139215,
    "firstSeenBlock": 132388582, "firstMintWib": "2026-11-08 19:00:00 WIB",
    "scanMints": 12, "scanMinters": 12,
    "registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "registryBytesInCode": True, "sourcify": "verified",
    "website": None, "websiteVerified": False,
    "xVerified": False,
    "freePctVerified": 4.7,
    "freePctNote": "freeSkunksClaimed 117/2500 = 4,7% <25% -> BUKAN strong lead.",
    "userBalance": 0, "freeClaimedBy_user": 0,
    "lastReadBlock": rr.get("block"), "lastReadWib": RUN_WIB,
    "baselineNote": ("Scan run 1901 first-seen (window 132388446-132389445, 12 mint/12 minter); triase: Sourcify verified, "
                     "registry() = registry persis, claimFree + freeSkunksRemaining + freeWindowOpen; gateStart 1794139215 = 2026-11-08 19:00 WIB "
                     "(umur terverifikasi <=48 jam). EARLY lead (dilaporkan sekali): free% 4,7%, website UNVERIFIED; TIDAK di-preview/di-mint."),
}

# ---- MALTA counts update (re-found via 5c; gate-failed stands, no re-report) ----
malta = track_c.get("AGENT MALTA")
if isinstance(malta, dict):
    malta["totalFreeShares"] = 426
    malta["totalShares"] = 426
    malta["freeMinted"] = 426
    malta["totalSupply"] = 766800000000000000000000000
    malta["lastReadBlock"] = rr.get("block")
    malta["lastReadWib"] = RUN_WIB
    malta["runNote1901"] = ("Run 1901: ditemukan ulang via 5c (16 mint/9 minter di window scan); totalFreeShares 137->426, slot user tetap terbuka "
                            "(quote(user,1) = 1 share gratis, freeUsed false); situs agentmalta.pages.dev dicek ulang 19:34 WIB - 'Contract: -' MASIH kosong, "
                            "tidak mencetak alamat kontrak persis -> GATE TETAP GAGAL; TIDAK di-preview/di-mint, TIDAK dilaporkan ulang (sudah dilaporkan run 1231).")

# ---- Run notes ----
snap["last_run_wib"] = RUN_WIB
snap["last_run"] = "free-mint-search 2026-11-08 1901 WIB"
snap["runNote1901_1108"] = (
    "Run 1901 (19:01 WIB): "
    f"route-1 re-read blok {rr.get('block')}: 535 kontrak + 71 track_c; perubahan supply {len(changed)}, degraded(None) {degraded}; "
    f"velocity LOLOS {len(vel_pass)} ({', '.join('%s +%d %.2fx' % v for v in vel_pass)}). "
    f"Paw Gang SELLOUT totalMinted 3333/3333 (strong-lead-pow-blocked) -> dilaporkan sekali + dihapus dari snapshot. "
    f"Abyssagent SELLOUT 4444/4444 (freeClaimed 4438, same-owner-discarded) -> ditandai sold-out, TIDAK dilaporkan. "
    "JINCHAN #305 MINTED (strong-lead direct mint 19:26 WIB): tx 0x74c508f4cc46b4cb8618d144c0ca972502ac3459d7803e0c40d61ec87f88d103, blok 132392397, "
    "gas 167477, receipt 1, ownerOf(305) = wallet agent, tier Common, bonus 50.000 JINCHAN; audit Binance hasResult=false (tanpa hasil), preview bersih 000000000; "
    "own market ada (0x7Cb7...) tapi 0 live listings -> tidak di-list; bonus JINCHAN ditahan sbg PENDING SWAP (pair belum ada). "
    "Gloop + Skunk Hollow = EARLY lead baru (dilaporkan sekali): keduanya launch 2026-11-08 19:00 WIB terverifikasi on-chain, agent-shaped (registry persis); "
    "Gloop free% UNVERIFIED (PoW-gated, difficultyBits 24), Skunk free% 4,7% <25%; website keduanya UNVERIFIED; tidak di-preview/di-mint. "
    "MALTA (track-C, 5c): totalFreeShares 137->426, slot user tetap terbuka; situs dicek ulang - 'Contract: -' masih kosong -> GATE TETAP GAGAL, tidak dilaporkan ulang. "
    f"Zorrie {'EARLY lead (dilaporkan sekali)' if zorrie_entry else 'TIDAK masuk early (first mint belum terverifikasi on-chain)'}: "
    "0x47feee72353358a61618cE640265F9f406f88E47, totalMinted 6/5000, slot user terbuka, website gate PASS (zorrie.fun), "
    "free path = SAT puzzle solve (PoW-gated, bukan plain mint). "
    "NUMBI (feed Sourcify): upcoming, mintOpen 0, totalMinted 0 - watchlist-only. "
    "BHTB 0xffcA (feed): ERC-20, free views revert on-chain, free pool UNVERIFIED - bukan lead, hanya run log. "
    "Beast16 (feed): masih upcoming (totalMinted 0). "
    "NEKART 682/10000 (6,8% <25%), Tigora 969/4444 (21,8% <25%, pace stagnan), Ink Koi slot user terpakai - tanpa promosi. "
    "HIVE Agents totalSupply 1256, balanceOf user 1 - tanpa perubahan tier. "
    "Boltbook EN+ZH: 25 post; AEQ (Aequitas) = refundable-deposit BERBAYAR 0,002 BNB/share - bukan kandidat, hanya run log. "
    "ORBITA (track-C, sudah minted-by-user): sharesSold 1000/1000 sold out, tanpa tindakan. "
    "KAGENT: refund gagal (phase 4, sold 44) - bukan track_c job ini, hanya run log. "
    "Sweep rute 3 EN+ZH: 0 proyek baru (semua post 24-28 Okt, umur >48 jam). "
    "Komplemen rute 6: Binance Square = hasil sweep EN; Odaily 0; PANews 0. "
    "Bridge: kontrak sama seperti run 1831 (ORE, ETHBack, Ikigai, AGC, PANBA, unnamed ERC20) - tanpa promosi. "
    "Binanceai tetap refund phase (failed=1, isRefundPhase=1, launched=0, totalShares 3110, tokenClaimed user 0, saldo 0) - tanpa perubahan."
)
snap["runNote1901_1108_scan"] = (
    f"Scan run 1901: window {scan.get('from_block')}-{scan.get('to_block')} (1000 blok, cap), "
    f"{scan.get('ankr_calls')} Ankr calls, {len(scan.get('errors', []))} error, partial={scan.get('partial')}; "
    f"{len(scan.get('contracts', []))} NFT ter-enrich / {scan.get('erc20_mint_contracts')} ERC20-mint; "
    f"first-seen baru {len(new_seen)} (agent-shaped {len(agent_shaped_new)}), historic/known {historic}; "
    f"watermark {'TIDAK dimajukan (partial)' if partial else 'dimajukan ke ' + str(scan.get('to_block'))}; "
    f"5c: {len(five_c) if isinstance(five_c, dict) else 0} ERC20 dicek, track-c-scan-checked +{added5c}."
)
save(BASE + "/onchain-snapshot.json", snap)
print("MERGE DONE changed=%d degraded=%d vel_pass=%s paw_sold_out=%s zorrie=%s new_seen=%d agent_shaped=%d historic=%d partial=%s" % (
    len(changed), degraded, vel_pass, paw_sold_out, zorrie_entry, len(new_seen), len(agent_shaped_new), historic, partial))
print("CHANGED:", [(n, o, t, m, p, s) for (n, o, t, m, p, s) in changed][:40])
