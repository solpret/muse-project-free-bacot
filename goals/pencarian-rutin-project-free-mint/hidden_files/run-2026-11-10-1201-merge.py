#!/usr/bin/env python3
"""Merge run 1201 reread+vel into snapshot. Read-only wrt chain; writes snapshot + backup.
Adds new watchlist-only entries (Thetavox, SonoWaves, Sora, Kora, Vorn-8c2f),
marks LUCKY777 minted-by-user, updates SEVENFOLD/Sakura/NUSA/BOME notes.
Does NOT re-report anything (reporting is the parent run's final message)."""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1201"
BLOCK = 132717239
NOW = "2026-11-10 12:01 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1201-premerge")

updated = 0
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    row = vel.get("rows", {}).get(name, {})
    prev_ts = entry.get("totalSupply")
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

# per-item notes
def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote1201_1110"] = text

note("SEVENFOLD", "Run 1201 (blok 132717239): totalSupply 1471->1528 (+57, rate 0,95/mnt vs prev 12,18 = 0,08x) velocity GAGAL (burst selesai); freeMinted 1527/3000 = 50,9% (LEWAT 50% tapi velocity gagal -> BUKAN kandidat). Audit MORROW RISK tetap blokir; status strong-lead-reported-2026-11-10-audit-blocked dipertahankan, TIDAK dilaporkan ulang.")
note("Sakura", "Run 1201: totalSupply 1317->1326 (+9, 0,15/mnt, 0,34x) velocity GAGAL; freeMinted 1316/6000 = 21,9% (<25% strong-lead). Tetap early-lead watchlist-only; umur+website unverified.")
note("THYRK", "Run 1201: totalSupply 2724->2829 (+105), freeMinted 2779; bal_user=1 (sudah mint user 08:22 WIB). Tidak ada aksi.")
note("Aura Agents", "Run 1201: totalSupply 5008->5069 (+61, rate 1,017/mnt, 15,96x) velocity LOLOS — tapi umur UNVERIFIED + free% UNVERIFIED (free views None) + slot user UNVERIFIED + website UNVERIFIED -> TIDAK ada promosi, TIDAK dilaporkan.")
note("FCAT Agents", "Run 1201: totalSupply 414->421 (+7, 0,29x) velocity GAGAL; freeClaimed 418/888 = 47,1% (verified free counter), umur UNVERIFIED, website null -> watchlist-only.")
note("JINCHAN Agents", "Run 1201: totalSupply 240->242 (+2, 0,17x) velocity GAGAL; freeClaimed 239/888 = 26,9%, umur UNVERIFIED -> watchlist-only.")
note("Roguefall", "Run 1201: totalSupply 1126->1136 (+10, 0,14x) velocity GAGAL; freeMinted 1130; umur+website UNVERIFIED -> watchlist-only.")
note("ConcheryPass", "Run 1201: freeMinted 1111/1111 (free lane HABIS, dikonfirmasi Boltbook recheck ~12:00 WIB). Sudah age-excluded 2026-11-10 -> status jadi sold-out, TANPA laporan baru (bukan lead aktif).")
snap["contracts"]["ConcheryPass"]["status"] = "checked-not-lead-age-excluded-sold-out-2026-11-10"
note("Cryptlichor", "Run 1201: freeClaimed 1691/1691 (cap) — sudah di cap sejak sebelum run 1101, bukan sellout baru; status watchlist-only dipertahankan, tanpa laporan.")
note("Gachagent", "Run 1201: freeMinted 2343/2343 (cap) — sudah di cap sejak sebelum run 1101, bukan sellout baru; tanpa laporan.")
note("Agent Grove", "Run 1201: freeMinted 2500/2500, freeOpen=0 — tidak berubah (track-B pending_claims tetap kosong).")
note("NEURA", "Run 1201: disebut lagi di Boltbook (claimFree 20.000 NEU, 265 klaim) — status checked-not-lead-2026-11-09 TETAP: tanpa LP pair + bukan agent-shaped. Tidak ada perubahan.")

# track_c updates
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

nusa = snap["track_c"].get("NUSA")
if isinstance(nusa, dict):
    nusa["runNote1201"] = ("Run 1201: freeMinted 365/560 = 65,2% (Boltbook roundup cocok: 365/560, +33 sejak kemarin); "
        "freeClaimed(user)=0; gate website TETAP FAILED (hot-leg 17:04 methods A-H). Umur: first mint 2026-11-08 17:05 WIB -> "
        "deadline 48 jam 2026-11-10 17:05 WIB (kurang ~5 jam). TIDAK preview/mint, TIDAK dilaporkan ulang; bila gate tetap gagal sampai deadline -> age-exclude + lapor sekali.")
bome = snap["track_c"].get("BOME-50CD")
if isinstance(bome, dict):
    bome["runNote1201"] = ("Run 1201: totalSupply tidak berubah; mintOpen=0 (sale BELUM dibuka; Boltbook: buka 14:00 WIB hari ini). "
        "Tetap watchlist-only-not-open; TIDAK preview/mint.")
lucky = snap["track_c"].get("0x38491597")
if isinstance(lucky, dict):
    lucky["status"] = "minted-by-user-2026-11-10"
    lucky["freeSharesRemaining"] = 594
    lucky["totalShares"] = 183
    lucky["mintTx"] = "0x0df090120205e8134faf20789a7a855b4d671aa7c2f4ef6df5103a96cbef2834"
    lucky["mintBlock"] = 132719624
    lucky["mintGas"] = 152039
    lucky["mintOrderId"] = "26111000002030867755"
    lucky["tokenBalanceBefore"] = 0
    lucky["tokenBalanceAfter"] = 50000000000000000000000000
    lucky["freeSharesClaimedUser"] = True
    lucky["mintNote1201"] = ("TRACK-C LEAD DIRECT MINT run 1201 (otorisasi user 2026-11-02): lead legs terpenuhi "
        "(S1 PASS + free pool 596 + slot user terbuka quote(user,1)=(1,0,0) + umur terverifikasi <=48 jam: verifiedAt 2026-11-09T20:17:53Z + "
        "first-seen totalShares 11 pukul 03:17 WIB 2026-11-10); website TERVERIFIKASI https://lucky777-mint.pages.dev (mencetak sale+token persis, /skill.md); "
        "audit Binance: sale hasResult=false (tidak ada hasil, bukan pass), token riskLevel 2 LOW, 0 hit RISK (2 CAUTION: Contract Code Not Verified, Newly Created Token), riskAlert null; "
        "preview bersih 000000000 (requestId 205f6808c7804c9ea4c5687a498a182b, balance +5e25 LUCKY777 persis); owner 0x918e4d71337b117c1baee0729d7f371c1fbddc93 TIDAK di same-owner-discards. "
        "CATATAN RISIKO (diungkap di laporan): refund 100% TIDAK terkunci — owner withdraw() bisa menguras pot refund (Boltbook + skill.md situs: dana dipegang operator); "
        "tidak memblokir free mint (value 0, tanpa pembayaran) tapi relevan bagi pembeli paid/refund. Marketplace/rarity TIDAK berlaku (bukan NFT).")

# new watchlist-only entries
snap["contracts"]["Thetavox"] = {
    "address": "0x37d39fcc21addbb753e9366216e494d7956bd859",
    "status": "watchlist-only-age-website-unverified-2026-11-10",
    "name": "Thetavox", "symbol": "THVX", "kind": "ERC721",
    "totalSupply": 1320, "freeClaimed": 1315, "FREE_SUPPLY": 1632, "MAX_SUPPLY": 2332,
    "mintOpen": 1, "balanceOf_user": 0, "freeClaimed_user": None,
    "freePctVerified": 80.6, "quote_user1": 0, "freeLeft_user": 1, "freeUsed_user": 0,
    "mintedBy_user": 0, "agentRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "owner": "0xee8d9edfeecfc175a76387a25581c2dc9f5f85f5", "ownerInDiscards": False,
    "lastReadBlock": 132717747, "lastReadWib": "2026-11-10 12:1x WIB",
    "source": "Boltbook front page EN run 1201 (post /p/WAepViWROAa7, 'two verified free mints today, Nov 10') + verifikasi on-chain run ini",
    "launchNote": ("UMUR UNVERIFIED: Sourcify verifiedAt 2026-11-03T08:30:05Z (7 hari lalu) BUKAN launch time; "
        "tidak ada stated launch time proyek; first-mint on-chain TERBLOKIR (Ankr 401 + dataseed eth_getLogs -32005 + tanpa archive). "
        "Postingan Boltbook 'today Nov 10' adalah klaim pihak ketiga, bukan stated launch proyek."),
    "websiteNote": ("GATE website FAILED (methods A-G + H + I): contractURI tanpa URL (fragment base64 fee_basis_points saja); "
        "tokenURI tanpa external_url; pencarian web 'Thetavox' tanpa situs proyek; postingan Boltbook tanpa link situs; Sourcify metadata tanpa URL; "
        "tidak ada pola same-family; owner 0xee8d...f5f5 bukan discards tapi grup tidak dikenal. X: tidak ditemukan handle proyek (opsional)."),
    "xNote": "Diskusi publik ADA (Boltbook post + recheck ZH 12:06 WIB) tapi BUKAN kandidat: umur unverified + gate website gagal.",
    "baselineNote": ("BARU run 1201: agent-shaped terverifikasi (Sourcify exact match; AGENT_ID()=registry resmi; freeClaimed/freeLeft/freeUsed/freeFor/mint/quote); "
        "free 1315/1632 = 80,6% TERVERIFIKASI; slot user TERBUKA (freeLeft=1, quote(user,1)=0, mintedBy=0); PRICE 0,00008 BNB (jalur berbayar). "
        "BUKAN early lead (first mint bukan di run ini), BUKAN strong lead (umur unverified), BUKAN kandidat (umur unverified + gate website gagal + velocity belum ada baseline). "
        "Watchlist-only; promosi hanya bila umur terverifikasi <=48 jam + website terverifikasi + velocity lolos. TIDAK pernah preview/mint run ini."),
    "velocityVerified": False, "xVerified": False,
}
snap["contracts"]["SonoWaves"] = {
    "address": "0x8d8d7a02f7d02c6fbadc33e5efd7ccac7a2c8a6b",
    "status": "watchlist-only-age-unverified-2026-11-10",
    "name": "SonoWaves", "symbol": "SONOWAVES", "kind": "ERC721",
    "totalSupply": 162, "totalMinted": 162, "freeMinted": 162, "FREE_SUPPLY": 2260, "MAX_SUPPLY": 6666,
    "mintOpen": 1, "balanceOf_user": 0, "freeClaimed_user": 0,
    "freePctVerified": 7.2, "registryBytes": True,
    "owner": "0x36f3d56ead5d1d6c2434f94defcef732c5c3cbd2", "ownerInDiscards": False,
    "lastReadBlock": 132718094, "lastReadWib": "2026-11-10 12:1x WIB",
    "source": "Boltbook front page ZH run 1201 (post 'Sakura owner's second drop', 04:19 UTC)",
    "launchNote": ("Umur dari first public post 2026-11-10 11:19 WIB (Boltbook) — first-mint on-chain TERBLOKIR (Ankr 401); "
        "launch <=48 jam didukung post + totalSupply kecil (115 saat post, 162 saat baca), tapi first-mint on-chain belum terverifikasi -> dicatat unverified-on-chain."),
    "websiteNote": "Website BELUM dicari (bukan lead; Sourcify UNVERIFIED, tanpa ABI). Gate belum dinilai.",
    "baselineNote": ("BARU run 1201: drop kedua owner Sakura (0x36f3...cbd2, bukan discards); 64 dari 115 minter pertama sudah pegang Sakura (klaim Boltbook); "
        "freeMinted 162/2260 = 7,2% (<25%); Sourcify UNVERIFIED (404) — agent-shape HANYA registry bytes + klaim Boltbook, tanpa ABI/registry view; "
        "slot user: freeClaimed(user)=0, balanceOf=0 (quote/freeLeft revert — nama fungsi berbeda, tanpa ABI). BUKAN early lead (first mint tidak terverifikasi on-chain run ini), "
        "BUKAN strong lead. Watchlist-only; promosi bila free% >=25% + umur/website terverifikasi. TIDAK pernah preview/mint."),
    "velocityVerified": False, "xVerified": False,
}
for nm, addr, ts, mx in [
    ("SoraAgent", "0x5aaa9dcae9d548cf7118b1d2c21be27313f1ae1d", 9900, 10000),
    ("KoraAgent", "0x5c32d38ca59cdc469cd7f064a41f3b845614bd2b", 9900, 10000),
    ("VornAgent-8c2f", "0x8c2f7bec2d7b31d9c706d25eb4d008f0754ce255", 4900, 5000),
]:
    snap["contracts"][nm] = {
        "address": addr, "status": "watchlist-only-unverified-2026-11-10",
        "name": nm, "kind": "ERC721", "totalSupply": ts, "MAX_SUPPLY": mx,
        "freeClaimed": None, "freeMinted": None, "FREE_SUPPLY": None,
        "balanceOf_user": 0, "registryBytes": True,
        "owner": "0x69a130b5c5433e55091433bf2e622fede819a1ad" if nm != "VornAgent-8c2f" else "0xe0808a338d96171fa9bde4d4d1897692392a0cbb",
        "lastReadBlock": 132717747, "lastReadWib": "2026-11-10 12:1x WIB",
        "source": "Boltbook front page EN/ZH run 1201 (99%-club recheck posts)",
        "launchNote": "UMUR UNVERIFIED: tidak ada stated launch; first-mint on-chain TERBLOKIR (Ankr 401).",
        "websiteNote": "Website belum terverifikasi (Sourcify UNVERIFIED).",
        "baselineNote": (f"BARU run 1201: {ts}/{mx} claimed (~{round(ts/mx*100,1)}%) tapi TANPA free view (freeClaimed/freeMinted revert) -> free% UNVERIFIED "
            "(tidak boleh ganti dengan % total supply); Sourcify UNVERIFIED; agent-shape HANYA registry bytes. Pola template 99%-club (sama seperti Nero/Vorn lama). "
            "BUKAN early lead (first mint bukan di run ini), BUKAN strong lead. Watchlist-only. TIDAK pernah preview/mint."),
        "velocityVerified": False, "xVerified": False,
    }

# age-exclusion sweep: entries with explicit verified launch older than 48h at 12:01 WIB
# (checked: SEVENFOLD launch 07:33 WIB 11-10 -> deadline 11-12; Sakura first mint 01:47 11-10 -> deadline 11-12;
#  NUSA first mint 17:05 11-08 -> deadline 17:05 11-10 (masih ~5 jam); tidak ada deadline yang lewat pada run ini.)
snap["last_run_wib"] = NOW
snap["last_run_block"] = BLOCK
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: contracts updated={updated} track_c updated={tc_updated} total contracts={len(snap['contracts'])} track_c={len(snap.get('track_c',{}))}")
