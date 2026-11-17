#!/usr/bin/env python3
"""Snapshot update for free-mint-search run 2026-11-14 02:01 WIB.
Merges run-2026-11-14-0201-verify.json + -retry.json into onchain-snapshot.json,
adds WoozCode (0xfF17) as EARLY lead. No preview/mint.
Backup saved as onchain-snapshot.json.bak-0201 first."""
import json, shutil, subprocess, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
_env = dict(os.environ); _env["TZ"] = "Asia/Jakarta"
NOW = subprocess.check_output(["date", "+%Y-%m-%d ~%H:%M WIB"], env=_env).decode().strip()
LAST_RUN = subprocess.check_output(["date", "+%Y-%m-%dT%H:%M+07:00"], env=_env).decode().strip()
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0201")
print("NOW:", NOW)
snap = json.load(open(BASE + "onchain-snapshot.json"))
verify = json.load(open(BASE + "run-2026-11-14-0201-verify.json"))
retry = json.load(open(BASE + "run-2026-11-14-0201-retry.json"))
READS = {}
for src in (verify, retry):
    for k, v in src["reads"].items():
        if v.get("views") is not None:
            READS[k] = v
VB = verify.get("block")   # 133407263
RB = retry.get("block")    # 133409604

def norm(a):
    return (a or "").lower()

updated = []
for key, ent in snap.get("contracts", {}).items():
    a = norm(ent.get("address"))
    hit = None
    for rk, rv in READS.items():
        if norm(rv.get("address")) == a and a:
            hit = (rk, rv); break
    if not hit:
        continue
    rk, rv = hit
    views = rv["views"]
    for fk, fv in views.items():
        if fk in ("name", "symbol"):
            continue
        if fv is not None:
            ent[fk] = fv
    ent["lastReadBlock"] = RB if rk in retry.get("reads", {}) else VB
    ent["lastReadWib"] = NOW
    updated.append(key)
print("generic-merged:", len(updated), "VB:", VB, "RB:", RB)

def note(key, text):
    ent = snap["contracts"].get(key)
    if ent is not None:
        ent["runNote0201"] = text
    else:
        print("NOTE-MISS:", key)

# Interval 0101->0201: block 133402541 -> 133407263 = 4722 blocks ~35.4 min chain-time.
INTERVAL_MIN = 35.4
def rate(delta):
    return round(delta / INTERVAL_MIN, 3)

def vel(key, delta, prev_rate):
    ent = snap["contracts"].get(key)
    r = rate(delta)
    ratio = (r / prev_rate) if prev_rate else None
    passes = bool(prev_rate and ratio is not None and ratio >= 1.5 and delta >= 20)
    if ent is not None:
        ent["previousRatePerMin"] = r
        ent["currentRatePerMin"] = r
        ent["mintedInInterval"] = delta
        ent["intervalMinutes"] = INTERVAL_MIN
        ent["velocityLegPasses"] = passes
        ent["velocityRatio"] = ratio
    return r, ratio, passes

r, ratio, p = vel("Crown Racer Cards", 18, 0.821)
note("Crown Racer Cards", "Run 0201: totalSupply 453->471 (+18, %.2f/mnt vs prev 0.821 = %.2fx, <20 -> velocity GAGAL); freeMinted 469/500 = 93,8%% (>70%%), freeClaimed(user)=0 slot TERBUKA, mintOpen 1. Umur TETAP UNVERIFIED -> BUKAN strong lead, bukan kandidat. Website/X UNVERIFIED. Tetap early-lead-reported. DIAM." % (r, ratio))
r, ratio, p = vel("Race Agents", 3, 0.154)
note("Race Agents", "Run 0201: totalSupply 357->360 (+3, %.2f/mnt, <20 -> velocity GAGAL); freeMinted 360/1000 = 36,0%%, mintOpen 1. Umur TETAP UNVERIFIED. Bukan strong lead/kandidat. DIAM." % r)
r, ratio, p = vel("Feed-5877", 16, 0.99)
note("Feed-5877", "Run 0201: totalMinted 421->437 (+16, %.2f/mnt vs prev 0.99 = %.2fx, <20 -> velocity GAGAL); MAX_SUPPLY 10000, mintOpen 1. QUIZ-GATED (sudah dilaporkan run 2231). DIAM." % (r, ratio))
r, ratio, p = vel("Moon", 0, 0.034)
note("Moon", "Run 0201: totalMinted 490 FLAT (+0 -> velocity GAGAL); MAX_SUPPLY 3333, mintOpen 1; free%% UNVERIFIED. Bukan kandidat. DIAM.")
r, ratio, p = vel("RoyalRush", 1, 0.051)
note("RoyalRush", "Run 0201: totalSupply 919->920 (+1, <20 -> velocity GAGAL); freeMinted 923/1000 = 92,3%% (free>totalSupply: counter tidak konsisten, dicatat apa adanya); umur TETAP UNVERIFIED. Bukan strong lead/kandidat. DIAM.")
r, ratio, p = vel("MORFO", 18, 0.222)
note("MORFO", "Run 0201: totalMinted 477->495 (+18, %.2f/mnt vs prev 0.222 = %.2fx TAPI <20 token -> velocity GAGAL); free%% UNVERIFIED; umur launch tepat UNVERIFIED. Tetap early-lead-reported. DIAM." % (r, ratio))
r, ratio, p = vel("Zero", 0, 0.0)
note("Zero", "Run 0201: totalMinted 315 FLAT (+0 -> velocity GAGAL); freeMinted 315/500 = 63,0%% (<70%%), slot terbuka (freeClaimed_user=0); deadline umur 07:55 WIB 14 Nov. Bukan strong lead. DIAM.")
r, ratio, p = vel("FERO", 1, 0.017)
note("FERO", "Run 0201: totalMinted 20->21 (+1, <20 -> velocity GAGAL); window buka 23:00 WIB 13 Nov; free%% ~21/3333 = 0,6%%. Bukan kandidat/strong lead/early. Tetap watchlist-only. DIAM.")
note("Cinder Crucible", "Run 0201: totalSupply 325 FLAT, freeMinted 325/325 = 100%% SOLD OUT (sudah dilaporkan hot-leg 01:14 WIB, tidak re-report). Status sold-out-2026-11-14 dipertahankan.")
note("Mossbound Key", "Run 0201: totalSupply 329 FLAT, freeMinted 325/325 = 100%% sold out (sudah dilaporkan). DIAM.")
note("Ochre Medallion", "Run 0201: totalSupply 211 FLAT, freeMinted 210/210 = 100%% sold out (sudah dilaporkan). DIAM.")
note("OLIVER", "Run 0201: totalSupply 1034->1036 (+2), freeMinted 986, freeRemaining 14. AGE-EXCLUDED (dilaporkan 21:00). DIAM.")
note("Slate", "Run 0201: totalSupply 91 FLAT, freeMinted 90/480 = 18,8%%, freeRemaining 390, saleOpen 1, mintOpen 1. Bukan kandidat. DIAM.")
note("BUBB", "Run 0201: totalSupply 1410->1415 (+5, <20 -> velocity GAGAL); freeMinted 1274, mintOpen 1. DIAM.")
note("MECHA", "Run 0201: totalMinted 1985->1989 (+4, <20 -> velocity GAGAL); freeClaimed 1988. DIAM.")
note("CY24", "Run 0201: totalSupply 464->465 (+1), MAX_SUPPLY 1703, mintOpen 1, costOf(user,1)=0. DIAM.")
note("MossSignal", "Run 0201: totalSupply 805 FLAT, mintOpen 1. DIAM.")
note("OBFG", "Run 0201: verify OK setelah FAIL 2x run 0101: totalSupply 723, freeMinted 723. AGE-EXCLUDED (sudah dilaporkan 12 Nov). DIAM.")
note("PX24", "Run 0201: verify OK setelah FAIL 2x run 0101: totalSupply 527 FLAT, mintOpen 1, costOf(user,1)=0. DIAM.")
note("ME30", "Run 0201 retry: totalSupply 303->305 (+2), MAX_SUPPLY 1950, mintOpen 1, costOf(user,1)=0. DIAM.")
note("Ponke", "Run 0201 retry: totalMinted 63 FLAT, freeMinted 63, balanceOf(user)=0. DIAM.")
note("PIXELPHARAOH", "Run 0201: verify + retry KEDUANYA transport FAIL - nilai snapshot dipertahankan, BUKAN nol. DIAM.")
note("HIVE Agents", "Run 0201: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("BUILD", "Run 0201: totalMinted 206 FLAT, freeMinted 200/200 = 100%% free pool habis, freeClaimed(user)=1. Minted-by-user. DIAM.")
note("SKRR", "Run 0201: totalSupply 519 FLAT, MAX_SUPPLY 1682, mintOpen 1, costOf(user,1)=0. DIAM.")
note("HANAMI", "Run 0201: totalSupply 132 FLAT, freeMinted 130, MAX_SUPPLY 3333. DIAM.")
note("AgentMuse", "Run 0201: freeClaimed 458 (hot-leg 0204: 459, variasi blok), deadline umur 05:53 WIB 14 Nov. DIAM.")
note("BinanceAI-mint", "Run 0201: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - TIDAK BERUBAH (refund phase sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM.")

# ---- NEW: WoozCode EARLY LEAD ----
snap["contracts"]["WoozCode"] = {
 "address": "0xfF172b79d040faefA1Bf34B47151edc87130246E",
 "status": "early-lead-reported-2026-11-14",
 "name": "WoozCode Snippets",
 "symbol": "SNIP",
 "kind": "ERC721",
 "totalSnippets": 61,
 "participantsOf_1": 57,
 "currentCommit": 1,
 "genesisOpen": 1,
 "genesisStart": 1794596827,
 "genesisStartWib": "2026-11-14 02:07:07 WIB",
 "commitEnd_1": 1794600000,
 "commitEndWib": "2026-11-14 03:00:00 WIB",
 "AGENT_ID": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "holdsAgentId_user": 1,
 "priceFor_user_wei": 0,
 "snippetsOf_1_user": 0,
 "questionFor_user": [73, 61, 0],
 "answerFor_user": 134,
 "website": "https://woozcode.fun",
 "websiteEvidence": "Skill file https://woozcode.fun/woozcode-skill.md mencetak kontrak persis 0xfF17 + Claim 0x5e8A + WOOZ 0x6E34 + registry 0x60B926...22F (metode I tokenURI + G site-doc). Homepage woozcode.fun dibaca langsung.",
 "tokenURI_1": "https://woozcode.fun/metadata/snippet/1",
 "claimContract": "0x5e8A8a4A3ebFde53afcb50722F82359E3586D0bd",
 "woozToken": "0x6E347E325819475d73FD5b3a87DEC2Aaee603478",
 "freePctVerified": None,
 "freePctNote": "Tidak ada free-supply counter (model per-Commit: Snippet pertama tiap Commit gratis per wallet, reset tiap Commit 4 jam). Free% TIDAK TERUKUR - bukan 0%.",
 "xVerified": False,
 "xNote": "Diskusi publik TIDAK ditemukan run ini (search WoozCode: hanya proyek lama Oathbots/Woohood/LeadLoop/dll). Proyek berumur ~30 menit saat dilaporkan.",
 "velocityVerified": False,
 "velocityNote": "Baseline pertama run 0201: totalSnippets 44 -> 50 -> 61 dalam ~28 mnt sejak genesis (02:07 WIB); rate interval belum terhitung (butuh run berikut). totalSupply() tidak ada di ABI - totalSnippets dipakai sebagai counter velocity.",
 "firstSeenBlock": 133407263,
 "firstSeenWib": "2026-11-14 ~02:10 WIB",
 "launchNote": "Launch TERVERIFIKASI: genesisStart() on-chain 1794596827 = 2026-11-14 02:07:07 WIB; Sourcify verifiedAt 2026-11-13T18:57:14Z; Commit 1 dibuka 02:07 WIB, seal 03:00 WIB. Umur ~28 menit saat laporan early lead.",
 "baselineNote": "EARLY lead dilaporkan sekali run 0201 (2026-11-14 ~02:40 WIB). Agent-shaped TERVERIFIKASI: AGENT_ID() = registry Binance 0x60B926...22F, mintFree(answer) + holdsAgentId + quiz questionFor/answerFor. Mint pertama terverifikasi on-chain via totalSnippets 44->61 + participantsOf(1) 46->57 + tokenURI(1) resolve; Transfer-log TIDAK terverifikasi (Ankr 401; dataseed eth_getLogs -32005/timeout; 1rpc + rpc.ankr.com kosong) - dicatat sebagai keterbatasan, bukan bukti tidak ada mint. TIDAK PERNAH auto-mint/preview (early tier). Promosi ke strong lead butuh 3 kaki (umur <24j + >70% free + slot terbuka) - kaki % tidak terukur di model per-Commit ini; ke kandidat butuh SEMUA kriteria + safety. Website TERVERIFIKASI (skill file mencetak kontrak persis). X UNVERIFIED. Slot user TERBUKA (snippetsOf(1,user)=0, priceFor(user)=0).",
 "lastReadBlock": 133409604,
 "lastReadWib": NOW,
 "previousRatePerMin": None,
 "currentRatePerMin": None,
 "mintedInInterval": None,
 "intervalMinutes": None,
 "velocityLegPasses": False,
 "velocityRatio": None,
 "supplyView": "totalSnippets",
 "runNote0201": "Run 0201: EARLY LEAD baru (lihat baselineNote). totalSnippets 61, participants 57, Commit 1 seal 03:00 WIB. Slot user TERBUKA. DIAM sesudah laporan sekali."
}
print("WoozCode added as early lead")

snap["last_run_wib"] = LAST_RUN
snap["last_run_note"] = ("Run 0201: verify 58/61 OK (blok 133407263, 1107,9 dtk) + retry 2/3 (blok 133409604; PIXELPHARAOH FAIL 2x); "
    "EARLY LEAD BARU: WoozCode 0xfF17 (genesis 02:07 WIB, umur ~28 mnt, AGENT_ID()=registry, mintFree quiz-gated, slot user terbuka, website terverifikasi via skill file) - dilaporkan sekali run ini; "
    "0 kandidat baru, 0 strong lead baru; Crown 469/500 = 93,8%% tapi umur UNVERIFIED + velocity GAGAL; MORFO +18 (<20) velocity GAGAL; "
    "binanceai pending TIDAK BERUBAH (refund phase); scan leg fast-fail (pre-flight: no head, dataseed timeout; Ankr 401 sejak 2026-11-09); watermark 132512564; "
    "Sourcify feed: 15 baru, 14 bukan agent-shaped (registry bytes tidak ada) + 1 WoozCode; Boltbook EN+ZH 0 baru; route 6: semua hit sudah ditangani (WNO minted-by-user, NOVRA/RIGBYPASS age-excluded/sold out, UFO window tutup 12 Nov, VISION/HOPKIN umur >24j); Odaily 0 baru.")
snap["timestamp_wib"] = NOW
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot updated; contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
