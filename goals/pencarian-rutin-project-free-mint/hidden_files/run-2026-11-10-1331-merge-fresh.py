#!/usr/bin/env python3
"""Merge run 1331 (fresh, written for this run). Read-only wrt chain; writes snapshot + backup.
Main events: 2 new EARLY leads (Forge Pass, Lucky Moments LUMO) from Boltbook post 13:20 WIB;
Pickgrid slot resolved OPEN via identity-hash path (agentIdClaimed=0, freeEligible=1, FREE_CAP 300,
free 117/300=39.0% VERIFIED) but age still UNVERIFIED -> still early, not strong lead.
No velocity passes, no candidates, no strong leads, no track-C leads. Scan fast-fail (Ankr 401)."""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1331"
BLOCK = 132728969
NOW = "2026-11-10 13:47 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1331-premerge")

updated = 0
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    row = vel.get("rows", {}).get(name, {})
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    if row.get("minted") is not None:
        entry["previousTotalSupply"] = row.get("prev")
        entry["mintedInInterval"] = row.get("minted")
        entry["intervalMinutes"] = 60.0
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1

tc_updated = 0
for k, v in snap.get("track_c", {}).items():
    if not isinstance(v, dict):
        continue
    f = rr.get("track_c", {}).get(k)
    if not f:
        continue
    for key in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if f.get(key) is not None:
            v[key] = f[key]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW
    tc_updated += 1
print("updated contracts:", updated, "track_c:", tc_updated)

def wib(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
lumo_start = wib(1794286894); lumo_end = wib(1794891694)
print("LUMO freeStart:", lumo_start, "| freeEnd:", lumo_end)

# --- new EARLY lead: Forge Pass ---
snap["contracts"]["Forge Pass"] = {
    "address": "0x733358348e07c46332a01c76e2bf6ee5d40a6d89",
    "status": "early-lead-reported-2026-11-10",
    "name": "Forge Pass", "symbol": "FORGE", "kind": "ERC721",
    "totalSupply": 335, "totalMinted": None, "freeMinted": 335, "paidMinted": None,
    "FREE_SUPPLY": None, "MAX_SUPPLY": 20000, "MAX_FREE_MINTS": 10000,
    "freePctVerified": 3.35,
    "balanceOf_user": 0, "freeClaimed_user": None, "freeMintUsed_user": 0,
    "owner": "0xa7a9a14c9c7298321283d7f211c64fa93ee80787", "ownerInDiscards": False,
    "agentRegistry": None,
    "sourcify": "exact_match",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "source": "Boltbook front page EN+ZH run 1331 (post 1328.ai 13:20 WIB '13:20 \u8f6e\u4e09\u679a\u514d\u8d39 NFT \u5168\u8df3\u8fc7' — Forge Pass freeMinted 261/10000 saat post) + verifikasi on-chain run ini",
    "launchNote": ("UMUR UNVERIFIED: tidak ada stated launch time proyek; first-mint on-chain TERBLOKIR (Ankr 401); "
        "Sourcify verifiedAt belum dibaca. Pertama terlihat job ini run 1331 (freeMinted 335 saat baca ~13:38 WIB; post Boltbook menyebut 261 pukul 13:20 WIB)."),
    "websiteNote": ("GATE website BELUM TERBUKTI (early lead): methods A (pencarian alamat mentah — hanya hasil Roblox/Raid tak terkait), "
        "G (pencarian nama 'Forge Pass' — tanpa situs proyek), H (contractURI() revert/kosong), I (tokenURI(1)='1.json' relatif, tanpa URL) — "
        "TIDAK ada situs proyek ditemukan. Bila promosi mendekat, gate wajib dinilai penuh (methods A-N) sebelum preview/mint apa pun."),
    "baselineNote": ("EARLY LEAD run 1331: agent-shaped TERVERIFIKASI via fungsi free-mint + konstanta free-supply (freeMint(), freeMintUsed(), "
        "freeMinted(), MAX_FREE_MINTS=10000; Sourcify exact_match); agentRegistry()/registry() TIDAK ada di ABI (bukan bukti tidak ada, tapi registry tidak terverifikasi). "
        "freeMinted 335/10000 = 3,35% TERVERIFIKASI; totalSupply 335 (semua mint gratis sejauh ini); MAX_PER_WALLET 10; PAID_PRICE 0,001 BNB; "
        "slot user TERBUKA (freeMintUsed(user)=0, balanceOf=0); owner 0xa7a9... BUKAN discards. "
        "CATATAN RISIKO (dari ABI + post Boltbook): owner pegang withdraw() + withdrawForge(uint256) + setForgeToken(address) + setBaseURI + transferOwnership — "
        "owner bisa menarik dana/mengubah aturan; penulis Boltbook melewatinya di hard gate sebelum preview. "
        "BUKAN strong lead (free% 3,35% < 25% + umur unverified + website unverified). TIDAK pernah preview/mint."),
    "velocityVerified": False, "xVerified": False,
}
# --- new EARLY lead: Lucky Moments (LUMO) ---
snap["contracts"]["Lucky Moments (LUMO)"] = {
    "address": "0x1e340592665889735c1f871aa13d038fa58bd09e",
    "status": "early-lead-reported-2026-11-10",
    "name": "Lucky Moments", "symbol": "LUMO", "kind": "ERC721",
    "totalSupply": 13, "totalMinted": None, "freeMinted": 13, "paidMinted": None,
    "FREE_SUPPLY": 1500, "MAX_SUPPLY": 5000,
    "freePctVerified": 0.87,
    "balanceOf_user": 0, "freeClaimed_user": 0,
    "owner": None, "ownerInDiscards": False,
    "agentRegistry": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "gateSigner": "0x554eb1b4cae8d477f08da24f10927a7402f54259",
    "sourcify": "exact_match",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "source": "Boltbook front page EN+ZH run 1331 (post 1328.ai 13:20 WIB — LUMO FREE_SUPPLY 1500, baru 1 diklaim, jendela s.d. 2026-11-17 05:01 UTC) + verifikasi on-chain run ini",
    "launchNote": (f"UMUR TERVERIFIKASI <=48 jam via on-chain freeStart() = 1794286894 ({lumo_start}); freeEnd() = 1794891694 ({lumo_end}); "
        "FREE_WINDOW 604800 dtk (7 hari). Umur saat run ~26 menit. First-mint on-chain (Transfer logs) tetap TERBLOKIR (Ankr 401) — freeStart adalah pembuka sale di kontrak sendiri."),
    "websiteNote": ("GATE website BELUM TERBUKTI (early lead): methods A (pencarian alamat mentah — tanpa hasil proyek), "
        "G (pencarian nama 'Lucky Moments' LUMO — hanya Lumira/Lumoria tak terkait), H (contractURI() revert/kosong), "
        "I (tokenURI(1) base64 JSON: name/description/attributes saja — TIDAK ada external_url/website). "
        "Bila promosi mendekat, gate wajib dinilai penuh (methods A-N) sebelum preview/mint apa pun."),
    "baselineNote": ("EARLY LEAD run 1331: agent-shaped TERVERIFIKASI (agentRegistry() = registry Agent ID resmi; Sourcify exact_match; "
        "claimFree() + freeStart/freeEnd/FREE_WINDOW + gateSigner). freeMinted 13/1500 = 0,87% TERVERIFIKASI; totalSupply 13; "
        "slot user on-chain TERBUKA (freeClaimed(user)=0, balanceOf=0). "
        "BLOKIR STRUKTURAL — claimFree butuh izin EIP-712 yang ditandatangani server proyek (gateSigner 0x554e...), dan server hanya memberi tanda tangan ke manusia "
        "yang posting di X + lolos verifikasi (post Boltbook 13:20 WIB) — agen TIDAK BISA mendapatkan tanda tangan itu, jadi free mint ini TIDAK BISA dieksekusi agen "
        "selama gate itu ada. BUKAN strong lead (free% 0,87% < 25% + website unverified). TIDAK pernah preview/mint; promosi ke strong lead mustahil tanpa gate dicabut."),
    "velocityVerified": False, "xVerified": False,
}
# --- Pickgrid deep-dive resolution ---
pg = snap["contracts"].get("Pickgrid Pickaxe")
if isinstance(pg, dict):
    pg["FREE_CAP"] = 300
    pg["freePctVerified"] = 39.0
    pg["agentIdClaimed_user"] = 0
    pg["freeEligible_user"] = 1
    pg["slotVerified"] = "OPEN run 1331"
    pg["runNote1331_1110"] = ("Run 1331 deep-dive slot (identity-hash path SELESAI): Agent ID tokenId user = keccak256('masgayut') = "
        "107187496765866644729837695198686237165740365523485558112864918211974996443404 — handleOf(user)='masgayut' + ownerOf(tokenId)=wallet agent TERVERIFIKASI. "
        "agentIdClaimed(tokenId)=0 (belum klaim), freeEligible(user,tokenId)=1 (ELIGIBLE), isFree(tokenId)=0 (semantik tak jelas, dicatat apa adanya), "
        "quote(tokenId) revert, FREE_CAP()=300, freeMinted 117/300 = 39,0% TERVERIFIKASI (was UNVERIFIED run 1301), paused=0, maxPaid=2000. "
        "Kaki strong lead: free% 39,0% LOLOS (>=25%) + slot user TERBUKA — TAPI umur TETAP UNVERIFIED (tanpa stated launch; first-mint on-chain TERBLOKIR Ankr 401) "
        "-> MASIH early lead, BUKAN strong lead. Website BELUM DINILAI. TIDAK preview/mint. Dilaporkan sekali run ini sebagai perubahan kaki.")
    print("Pickgrid updated: free 117/300 = 39.0%, slot OPEN")

# --- bridge (complementary leg) ---
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", []) if isinstance(bridge, dict) else []
    snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    snap_addrs |= {str(v.get("address", "")).lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict)}
    new_bridge = [a for a in bcontracts if isinstance(a, str) and a.lower() not in snap_addrs]
    snap["runNote1331_bridge"] = (f"Run 1331 bridge: {len(bcontracts)} kontrak, {len(new_bridge)} belum di snapshot — 0 baru vs hot-leg 1324 (8 yang sama); "
        "0 promosi (tidak ada yang memenuhi tier).")
except Exception as e:
    snap["runNote1331_bridge"] = f"Run 1331 bridge: baca gagal ({e}); lanjut normal, bridge tidak menggagalkan run."

snap["runNote1331_1110"] = ("Run 1331 (2026-11-10 13:31-13:47 WIB, blok 132728969, interval nominal 60 mnt vs run 1301): re-read 651 kontrak + 75 track_c (620,0 dtk). "
    "Velocity LOLOS: [] — tanpa promosi. EARLY LEAD BARU 2 (Boltbook post 1328.ai 13:20 WIB): Forge Pass (free 335/10000=3,35%, Sourcify exact_match, owner pegang withdraw/setForgeToken — dilewati penulis di hard gate) "
    "dan Lucky Moments LUMO (free 13/1500=0,87%, registry resmi, umur TERVERIFIKASI via freeStart ~13:21 WIB, TAPI claimFree butuh tanda tangan server EIP-712 khusus manusia — agen tidak bisa klaim). "
    "Keduanya agent-shaped, pertama terlihat run ini, TIDAK pernah preview/mint; website keduanya UNVERIFIED (methods A/G/H/I). "
    "Pickgrid Pickaxe: slot user TERVERIFIKASI TERBUKA via jalur identity-hash (agentIdClaimed=0, freeEligible=1, FREE_CAP 300, free 117/300=39,0%) — kaki strong lead 2/3, umur tetap UNVERIFIED -> MASIH early lead. "
    "Kora Agent: sudah di snapshot (watchlist-only-unverified run 1201); post Boltbook konfirmasi owner sama dengan Zephyr Agent — tanpa perubahan status. "
    "BoltRewards 0x8269ea16... adalah link footer Boltbook, bukan proyek mint. NUSA freeMinted 369/560, gate tetap FAILED, deadline 17:05 WIB hari ini. "
    "SEVENFOLD freeMinted 1651/3000=55,0% tapi velocity 0,97x GAGAL -> BUKAN kandidat; audit MORROW RISK tetap blokir. "
    "PIXEL MONSTERS 693/2000=34,7% — kaki strong-lead terpenuhi tapi gate website FAILED (dilaporkan 00:29). YAMA: baca ulang track_c GAGAL run ini (semua field null) — status audit-blocked dipertahankan, tanpa perubahan. "
    "Feed Sourcify 20/20 dicek, 0 S1/0 S2. Boltbook EN 200 45.702 B / ZH 200 45.859 B. Ankr 401 fast-fail (preflight 6,1 dtk, head 132728969); watermark tetap 132512564; gap ~216.405 blok. "
    "Scan leg GAGAL CEPAT; 5c: tanpa output scan baru -> 0 dicek run ini. Sweep web EN+ZH + Square/Odaily/PANews: MOLT AGENT sudah di snapshot (free pool habis, excluded 09 Nov); AgentForge 0xf11e... umur ~14 hari -> bukan lead; 0 baru. "
    "Kandidat baru 0; strong lead baru 0; early lead baru 2; track-C lead/kandidat baru 0; sellout baru 0.")
snap["runNote1331_1110_scan"] = ("Run 1331 scan: PRE-FLIGHT GAGAL (Ankr 401 Unauthorized, 6,1 dtk, head 132728969) — outage Ankr sejak 2026-11-09 ~13:33 WIB BERLANJUT. "
    "Scan leg FAST-FAIL per amandemen 2026-11-06; watermark TETAP 132512564; gap ke head ~216.405 blok (backfill OFF atas perintah user).")
snap["runNote1331_1110_discovery"] = ("Run 1331 discovery (routes 2/3/5a/6): Boltbook EN+ZH front page — post 1328.ai 13:20 WIB 'tiga free NFT semua dilewati' -> Forge Pass + LUMO (EARLY lead baru, 2x) + Kora Agent (sudah di snapshot); "
    "MOLT AGENT (sweep EN, 06 Nov, sudah di snapshot, free pool habis); AgentForge (sweep EN, 27 Okt, umur ~14 hari, bukan lead); AirdropBuzz ZH (YAMA/AGENT MALTA sudah diketahui; free pool MOLT AGENT/PATRA GENESYS/BOOB habis; ORBITA sold out); "
    "AgentIDeth ($AGI) adalah Ethereum L1 — di luar scope BSC. Sourcify feed 20 -> 0 S1/0 S2. Odaily + PANews newsflash: 0 mention Agent ID. twitterapi.io tidak pernah dipanggil.")
snap["runNote1331_1110_5c"] = ("Run 1331 5c: scan leg fast-fail (Ankr 401) -> TIDAK ADA output scan baru -> 0 ERC-20 baru dicek run ini (bukan 0 hasil shape-check; "
    "tidak ada backlog baru). track-c-scan-checked.json tidak berubah.")
snap["runNote1331_1110_age_exclusions"] = ("Run 1331 age-exclusion sweep: TIDAK ADA exclusion baru. Deadline terdekat: NUSA 2026-11-10 17:05 WIB (~3,3 jam lagi, gate tetap FAILED); "
    "Sakura deadline 2026-11-12 01:47 WIB; SEVENFOLD deadline 2026-11-12 07:33 WIB; LUMO deadline 2026-11-17 ~13:21 WIB (freeEnd on-chain). "
    "Item lama dengan firstMintWib >48 jam TIDAK di-exclude: launch UNVERIFIED, exclusion butuh umur TERVERIFIKASI >48 jam (preseden Rose Genesis run 1231).")
snap["runNote1331_binanceai"] = ("Run 1331 binanceai (fresh read): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 — IDENTIK dengan run 1301/1931. "
    "Fase refund/failed, SUDAH dilaporkan sekali - TIDAK dilaporkan ulang.")
snap["runNote1331_grove"] = ("Run 1331 Agent Grove fase 2: cron grove-watch 13:31 WIB — freeOpen=0, freeClaimed(user)=false; fase 2 belum dibuka, tanpa perubahan.")
snap["last_run_wib"] = NOW
snap["last_run_block"] = BLOCK
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT WRITTEN. contracts:", len(snap["contracts"]), "track_c:", len(snap.get("track_c", {})))
