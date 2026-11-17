#!/usr/bin/env python3
"""Merge run 2026-11-08 20:31 WIB (2031) into onchain-snapshot.json.
Route-1 reread + velocity; ZGS fresh reads; track-C watchlist (NUSA 190,
DROID 733, Kiko9393 baseline); HELIX/Pokechain early-lead-reported flip;
BAHUANG2 strong-lead-reported-gate-blocked flip; Pressure early-lead-reported
(new entry); Ape Agent + Stickman age-excluded REMOVED; Saturnagent
age-excluded + 3 lanes same-owner-discarded + Pilotchrome/Forklings/BMT
age-excluded = log only (never in snapshot); Wisp Agent pending verification
next run. Watermark NOT touched (already 132404141 via backfill — backfill
still running despite user disabling it 06:28 WIB; see runNote). Seen file
NOT touched (backfill already wrote the 2031 window). 5c checked file already
updated by Subagent A (+2). Never touches pending_claims.
Read-only except the snapshot write + this script's own log."""
import json, os, shutil, datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN_WIB = "2026-11-08 20:31 WIB"
NOW_WIB = "2026-11-08 21:3x WIB"

def load(p):
    with open(p) as f: return json.load(f)
def save(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w") as f: json.dump(obj, f, indent=1)
    os.replace(tmp, p)

shutil.copy(BASE + "/onchain-snapshot.json", BASE + "/onchain-snapshot.json.bak-2031-premerge")
snap = load(BASE + "/onchain-snapshot.json")
rr = load(BASE + "/run-2026-11-08-2031-reread.json")
zgs = load(BASE + "/run-2026-11-08-2031-trackc-zgs-binanceai.json")
pv = load(BASE + "/run-2026-11-08-2031-pending-verify.json")
mi = load(BASE + "/run-2026-11-08-2031-merge-input.json")
wf = load(BASE + "/run-2026-11-08-2031-webfind-verify.json")
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

# ---- Route 1: reread updates + velocity ----
changed, degraded, vel_pass = [], 0, []
PREV_BLOCK = 132395502  # run 1931 read block
INTERVAL_MIN = (rr.get("block", 132404126) - PREV_BLOCK) * 0.45 / 60.0
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
        if d.get("freeMinted") is not None:
            old["freeMinted"] = d["freeMinted"]
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
        if d.get("freeMinted") is not None:
            old["freeMinted"] = d["freeMinted"]
        if d.get("balanceOf_user") is not None:
            old["balanceOf_user"] = d["balanceOf_user"]

# ---- Track C reread updates (freeMinted from route-1 TC views) ----
tc_changed = []
for name, d in rr.get("track_c", {}).items():
    old = track_c.get(name)
    if isinstance(old, dict) and d.get("freeMinted") is not None:
        if old.get("freeMinted") != d["freeMinted"]:
            tc_changed.append((name, old.get("freeMinted"), d["freeMinted"]))
            old["freeMinted"] = d["freeMinted"]
            old["lastReadWib"] = RUN_WIB
            old["lastReadBlock"] = rr.get("block")

# ---- ZGS fresh reads ----
z = zgs.get("zgs", {}).get("Zorrie", {})
if "Zorrie" in contracts and z.get("totalMinted") is not None:
    contracts["Zorrie"]["totalMinted"] = z["totalMinted"]
    contracts["Zorrie"]["freeMintedPerWallet_user"] = z.get("freeMintedPerWallet_user")
    contracts["Zorrie"]["userBalance"] = z.get("balanceOf_user")
    contracts["Zorrie"]["lastReadBlock"] = rr.get("block")
    contracts["Zorrie"]["lastReadWib"] = RUN_WIB
    contracts["Zorrie"]["runNote2031_1108"] = ("Run 2031: totalMinted tetap 8/5000 (0,16%), slot user terbuka "
        "(freeMintedPerWallet=0, balanceOf=0). JAUH di bawah 25% -> BUKAN strong lead, tanpa promosi.")
g = zgs.get("zgs", {}).get("Gloop", {})
if "Gloop" in contracts and g.get("totalMinted") is not None:
    contracts["Gloop"]["totalMinted"] = g["totalMinted"]
    contracts["Gloop"]["userBalance"] = g.get("balanceOf_user")
    contracts["Gloop"]["hasMinted_user"] = g.get("hasMinted_user")
    contracts["Gloop"]["lastReadBlock"] = rr.get("block")
    contracts["Gloop"]["lastReadWib"] = RUN_WIB
    contracts["Gloop"]["runNote2031_1108"] = ("Run 2031: totalMinted 43->49/3333, mintOpen 1, MINT_START 1794139200 "
        "(2026-11-08 19:00 WIB, umur terverifikasi <=48 jam). free% TETAP UNVERIFIED (ABI tanpa free view) -> "
        "BUKAN strong lead (butuh >=25% free terverifikasi), tanpa promosi.")
s = zgs.get("zgs", {}).get("Skunk Hollow", {})
if "Skunk Hollow" in contracts and s.get("totalSkunksMinted") is not None:
    contracts["Skunk Hollow"]["totalSkunksMinted"] = s["totalSkunksMinted"]
    contracts["Skunk Hollow"]["freeSkunksRemaining"] = s.get("freeSkunksRemaining")
    contracts["Skunk Hollow"]["freeSkunksClaimed"] = s.get("freeSkunksClaimed")
    contracts["Skunk Hollow"]["freeWindowOpen"] = s.get("freeWindowOpen")
    contracts["Skunk Hollow"]["freeClaimedBy_user"] = s.get("freeClaimedBy_user")
    contracts["Skunk Hollow"]["userBalance"] = s.get("balanceOf_user")
    contracts["Skunk Hollow"]["freePctVerified"] = round(100.0 * s["totalSkunksMinted"] / 2500, 2)
    contracts["Skunk Hollow"]["lastReadBlock"] = rr.get("block")
    contracts["Skunk Hollow"]["lastReadWib"] = RUN_WIB
    contracts["Skunk Hollow"]["runNote2031_1108"] = ("Run 2031: totalSkunksMinted 208->330/2500 (13,2% <25%), "
        "freeWindowOpen 1, slot user terbuka (freeClaimedBy=0). BUKAN strong lead, tanpa promosi.")

# ---- Track-C watchlist fresh updates ----
tw = zgs.get("track_c_watchlist", {})
nusa = track_c.get("NUSA")
if isinstance(nusa, dict):
    n = tw.get("NUSA", {})
    if n.get("freeMinted") is not None:
        nusa["freeMinted"] = n["freeMinted"]
    nusa["lastReadBlock"] = rr.get("block")
    nusa["lastReadWib"] = RUN_WIB
    nusa["runNote2031"] = ("Run 2031: freeMinted 142->190/560 MAX_FREE = 33,9%; freeClaimed(user)=0; quote(user,1) "
        "TETAP REVERT di pembacaan segar -> slot user TIDAK terverifikasi segar; gate website TETAP GAGAL "
        "(kaki web run 2031); tetap lead gate-blocked, TIDAK di-preview/di-mint, TIDAK dilaporkan ulang. "
        "CATATAN BARU (Boltbook post 21:04 WIB, belum verifikasi on-chain): poster melaporkan token NUSA "
        "TERKUNCI/tidak bisa ditransfer sesudah mint gratis.")
malta = track_c.get("AGENT MALTA")
if isinstance(malta, dict):
    m = tw.get("AGENT MALTA", {})
    malta["lastReadBlock"] = rr.get("block")
    malta["lastReadWib"] = RUN_WIB
    malta["runNote2031"] = ("Run 2031: bacaan track-C watchlist DEGRADED (_batch_fail) - nilai lama dipertahankan "
        "(totalFreeShares 434, quote(user,1)=(1 free, 0 cost), slot terbuka). GATE TETAP GAGAL. "
        "TIDAK di-preview/di-mint, TIDAK dilaporkan ulang.")
droid = track_c.get("DROID")
if isinstance(droid, dict):
    dd = tw.get("DROID", {})
    if dd.get("freeMinted") is not None:
        droid["freeMinted"] = dd["freeMinted"]
    droid["lastReadBlock"] = rr.get("block")
    droid["lastReadWib"] = RUN_WIB
    droid["runNote2031"] = "Run 2031: freeMinted 732->733 (+1), freeUsed(user)=0 - tanpa perubahan."
kiko = track_c.get("Kiko9393")
if isinstance(kiko, dict):
    kk = tw.get("Kiko9393", {})
    kiko["lastReadBlock"] = rr.get("block")
    kiko["lastReadWib"] = RUN_WIB
    kiko["runNote2031"] = ("Run 2031 (baseline baru): freeMinted 0, freeClaimed(user)=0, quote reverts - "
        "umur UNVERIFIED, watchlist-only, tanpa promosi.")

# ---- HELIX / Pokechain / BAHUANG2: fresh reads + status flips (reported this run) ----
hx = contracts.get("HELIX", {})
pv_hx = pv.get("HELIX", {})
if hx:
    hx["totalSupply"] = pv_hx.get("totalSupply", hx.get("totalSupply"))
    hx["totalMinted"] = pv_hx.get("totalMinted", hx.get("totalMinted"))
    hx["publicRemaining"] = pv_hx.get("publicRemaining")
    hx["mintActive"] = pv_hx.get("mintActive")
    hx["totalPaidMinted"] = pv_hx.get("totalPaidMinted")
    hx["freeUsed_user"] = pv_hx.get("freeUsed_user")
    hx["balanceOf_user"] = pv_hx.get("balanceOf_user")
    hx["hasAgentId_user"] = pv_hx.get("hasAgentId_user")
    hx["requireAgentId"] = pv_hx.get("requireAgentId")
    hx["status"] = "early-lead-reported-2026-11-08"
    hx["lastReadBlock"] = rr.get("block")
    hx["lastReadWib"] = RUN_WIB
    hx["runNote2031_1108"] = ("Run 2031: totalSupply/totalMinted 57->182 (+125 dlm ~1 jam, minting cepat), "
        "publicRemaining 4149->4040, mintActive=1, totalPaidMinted=0, hasAgentId(user)=1, freeUsed(user)=0. "
        "free% TETAP UNVERIFIED (tanpa FREE_SUPPLY/freeClaimed/freeMinted view). Website gate TETAP GAGAL "
        "(kaki web run 2031: hanya HELIX tak terkait / same-name). Owner 0xcbcadc... = EXCEPTION di discards "
        "(TIDAK dibuang). DILAPORKAN SEKALI run 2031 sebagai EARLY lead (bukan kandidat/strong, TIDAK preview/mint).")
pk = contracts.get("Pokechain", {})
pv_pk = pv.get("Pokechain", {})
if pk:
    pk["totalMinted"] = pv_pk.get("totalMinted", pk.get("totalMinted"))
    pk["balanceOf_user"] = pv_pk.get("balanceOf_user")
    pk["mintedBy_user"] = pv_pk.get("mintedBy_user")
    pk["status"] = "early-lead-reported-2026-11-08"
    pk["websiteGate"] = ("VERIFIED run 2031 (kaki web): pokechain.trade situs proyek (nama, supply 15.555 = "
        "MAX_SUPPLY, harga 0,00035/0,00065 BNB, link x.com/PokechainTrade) DAN bundle JS /js/app.js "
        "mendeklarasi MINT_CA='0x4EF929aF00cB93993c3D01834C4DA79200d31e32' + logika first-mint-free. "
        "Alamat ada di JS bundle, BUKAN di teks HTML statis; /skill.md /launch.json /llms.txt 404.")
    pk["websiteVerified"] = True
    pk["lastReadBlock"] = rr.get("block")
    pk["lastReadWib"] = RUN_WIB
    pk["runNote2031_1108"] = ("Run 2031: totalMinted 113->327 (+214 dlm ~1 jam), MAX_SUPPLY 15555, owner "
        "0xf379... TIDAK di discards. Gate website TERVERIFIKASI (lihat websiteGate). Bentuk gratis TETAP "
        "UNVERIFIED on-chain (Sourcify 404, tanpa selector freeMint, hanya mint(uint256)). DILAPORKAN SEKALI "
        "run 2031 sebagai EARLY lead BORDERLINE (registry-bytes-only) - bukan kandidat/strong, TIDAK preview/mint.")
bh = contracts.get("BAHUANG2", {})
pv_bh = pv.get("BAHUANG2", {})
if bh:
    bh["totalMinted"] = pv_bh.get("totalMinted", bh.get("totalMinted"))
    bh["freeMinted"] = pv_bh.get("freeMinted", bh.get("freeMinted"))
    if bh.get("freeMinted") is not None and bh.get("FREE_CAP"):
        bh["freePctVerified"] = round(100.0 * bh["freeMinted"] / bh["FREE_CAP"], 2)
    bh["freeCount_user"] = pv_bh.get("freeCount_user")
    bh["balanceOf_user"] = pv_bh.get("balanceOf_user")
    bh["status"] = "strong-lead-reported-gate-blocked-2026-11-08"
    bh["lastReadBlock"] = rr.get("block")
    bh["lastReadWib"] = RUN_WIB
    bh["runNote2031_1108"] = ("Run 2031: totalMinted 889->977, freeMinted 886->974/3000 FREE_CAP = 32,47% (tetap "
        ">=25%); umur terverifikasi (mintStart 2026-11-08 17:21:33 WIB, ~3,4 jam); slot user terbuka "
        "(freeCount(user)=0, FREE_PER_WALLET=2, quote(user,1)=[2,20,...]). 3 kaki strong lead TETAP TERPENUHI. "
        "Gate website TETAP GAGAL (kaki web run 2031: tanpa hit nama/alamat). DILAPORKAN SEKALI run 2031 sebagai "
        "STRONG LEAD (promosi early->strong) DENGAN ALASAN BLOKIR gate - TIDAK BISA direct mint, TIDAK preview.")

# ---- Pressure: new early lead entry (reported this run) ----
pr = dict(mi.get("new_snapshot_entries", {}).get("Pressure", {}))
pr["status"] = "early-lead-reported-2026-11-08"
pr["lastReadBlock"] = rr.get("block")
pr["lastReadWib"] = RUN_WIB
pr["runNote2031_1108"] = ("Run 2031: scan first-seen (window 132403128-132404127, 5 mint/1 minter); first mint "
    "blok 132403589 = 2026-11-08 20:50:48 WIB (umur terverifikasi, baru beberapa menit); FREE_POOL 1000, "
    "freeMinted 5 = 0,5% (<25% -> tier EARLY saja); slot user UNVERIFIED (freeOf revert, balanceOf=0); "
    "contractURI kosong (tanpa pointer website); website gate BELUM diverifikasi. DILAPORKAN SEKALI run 2031 "
    "sebagai EARLY lead - bukan kandidat/strong, TIDAK preview/mint.")
contracts["Pressure"] = pr

# ---- Age exclusions: REMOVE Ape Agent + Stickman ----
removed = []
for name in ["Ape Agent", "Stickman"]:
    e = contracts.pop(name, None)
    if e is not None:
        removed.append({"name": name, "address": e.get("address"),
                        "firstMintWib": next((c.get("firstMintWib") for c in mi.get("age_exclusion_candidates_remove_from_snapshot", []) if c.get("name") == name), None),
                        "age_h_at_2031": next((c.get("age_h_at_2031") for c in mi.get("age_exclusion_candidates_remove_from_snapshot", []) if c.get("name") == name), None),
                        "totalSupply_at_removal": e.get("totalSupply"),
                        "MAX_SUPPLY": e.get("MAX_SUPPLY"),
                        "status_before": e.get("status"),
                        "removed_run": "2026-11-08-2031"})
snap["age_exclusions_2031"] = removed
snap["runNote2031_1108_age_exclusions"] = (
    "Run 2031 age sweep: DIHAPUS dari snapshot (umur terverifikasi >48 jam, belum sold out): "
    "Ape Agent 0x8150922eb36b7d5972b6b06254435dd755a7c54c (first mint 2026-11-06 18:34:33 WIB, 50,0 jam, "
    "supply 659/4444) + Stickman 0x345b0eb3180ae510cB2f05EfD49085E79477b330 (first mint 2026-11-06 18:54:01 WIB, "
    "49,6 jam, supply 543/4444). Keduanya watchlist-only-boltbook-noted-2026-11-06; dilaporkan sekali run 2031. "
    "14 kontrak paid-only lain juga >48 jam tapi SUDAH excluded dari kandidasi (daftar di analysis JSON) - tanpa aksi. "
    "KOREKSI UMUR (log saja, ketiganya TIDAK PERNAH masuk snapshot, TIDAK PERNAH dilaporkan sebagai lead): "
    "Pilotchrome 0x3AD8... first mint 2026-11-04 20:59:19 WIB (~95,5 jam, free 63,96%); Forklings 0xD7B3... first mint "
    "2026-11-05 06:25:01 WIB (~86 jam, free 54,85%); BMT Agents 0x7D6e... first mint 2026-11-01 21:27:48 WIB (~167 jam, "
    "free 84,1%) - ketiganya sempat terlihat seperti strong lead di walk awal, DIBATALKAN sesudah cross-check seen record "
    "+ re-query Ankr langsung (walk berhenti di empty chunk hanya membatasi ~25 jam ke belakang). "
    "Saturnagent 0xef870a... (verifikasi parent run 2031): agent-shaped (AGENT_ID()=registry persis, freeClaimed 1266/2000 "
    "= 63,3%, freeLeft(user)=2, quote 0, slot terbuka) TAPI first mint 2026-11-06 19:53:20 WIB (blok 132012083, ~49,6 jam) "
    "-> AGE-EXCLUDED, BUKAN lead, tidak dilaporkan sebagai lead, tidak masuk snapshot. "
    "3 lane wave 0x1103 (ALL ACCESS 0xc3ce..., THE KEY 0xa483..., GOLDEN TICKET 0x1de1...): owner 0x11038f4a... ADA di "
    "same-owner-discards -> SAME-OWNER-DISCARDED, log saja, tidak pernah dipromosikan/dilaporkan (5 kontrak S1 feed yang "
    "sama: AGENT DOSSIER/PASS/CORE/BOTS/TERMINAL, owner yang sama, juga discarded). "
    "Wisp Agent 0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb (klaim post 4.790/5.000 gratis, Sourcify 404): BELUM "
    "terverifikasi on-chain run ini - diteruskan sebagai PENDING VERIFIKASI untuk run berikut (bukan lead). "
    "OBSIDIAN CARD 0x57e3f981791c3be85d74e74a2f402d7d00f6ed9c sold out 1.111/1.111 (temuan web, log saja)."
)

# ---- Run notes ----
an = load(BASE + "/run-2026-11-08-2031-analysis.json")
snap["last_run_wib"] = RUN_WIB
snap["last_run"] = "free-mint-search 2026-11-08 2031 WIB"
snap["runNote2031_1108"] = (
    "Run 2031 (20:31 WIB, parent merge ~21:3x WIB): "
    f"route-1 re-read blok {rr.get('block')}: {len(rr.get('reread', {}))} kontrak + {len(rr.get('track_c', {}))} track_c; "
    f"perubahan supply {len(changed)}, degraded(None) {degraded}; "
    f"velocity LOLOS (merge) {len(vel_pass)} ({', '.join('%s +%d %.2fx' % v for v in vel_pass)}); "
    f"analysis Subagent A: {an.get('velocity_passes')}. "
    "Velocity passers BUKAN kandidat/promosi (ketiganya free% UNVERIFIED - tanpa free view on-chain; OinkHash sudah "
    "early-lead-reported, velocity saja tidak mempromosikan). ETHBack/bridge = delta supply token ERC20, bukan velocity NFT. "
    "Zorrie totalMinted tetap 8 (0,16%), Gloop 43->49 (free% tetap UNVERIFIED), Skunk Hollow 208->330 (13,2% <25%) -> "
    "ketiganya TANPA promosi. GLOOP 18-bit totalMinted 1049->1526 (+477, free% UNVERIFIED) - bukan strong. "
    "MALTA bacaan degraded (nilai lama dipertahankan), gate TETAP GAGAL. NUSA freeMinted 142->190/560 = 33,9%; "
    "quote(user,1) TETAP REVERT -> slot TIDAK terverifikasi segar; gate TETAP GAGAL; tetap lead gate-blocked. "
    "NIULAI launched=0 phase=4 (belum buka); KillZero launched=0 (belum buka); DROID freeMinted 732->733; 960E tetap 38 "
    "state=0; Agentidbsc mintOpen=1 quote=0; CHTCI mintOpen=1; BoxBigem tanpa perubahan; Pacture slot user terpakai; "
    "FABE freeSharesRemaining tetap 2821, launched=0; Kiko9393 baseline baru (freeMinted 0). "
    "Binanceai TIDAK BERUBAH (launched 0, failed 1, isRefundPhase 1, totalShares 3110, tokenClaimed user 0, saldo 0) "
    "- sudah dilaporkan sekali sebagai refund phase, TIDAK dilaporkan ulang. "
    "Bridge: 116 kontrak, 8 tidak ada di snapshot - semuanya reported_as 'finding' (bukan lead), gate "
    "website_no_pointer_found; 1 recent (tracker ERC20 ETHBack 0xf75c...) - tanpa aksi."
)
snap["runNote2031_1108_scan"] = (
    "Scan run 2031: pre-flight OK 9,9 dtk (head 132404108, 467 logs/50 blok); window 132403128-132404127 "
    "(1000 blok, cap), 40 Ankr calls, 0 error, partial=false; 108 NFT ter-enrich + 368 ERC20-mint; first-seen 11 "
    "(dihitung thd baseline seen pra-run 20:15 WIB - live seen file sudah ditimpa backfill 21:04 WIB); "
    "skipped gap 132401212-132403127 (1916 blok) TIDAK di-scan run ini - DITUTUP BACKFILL bersamaan "
    "(backup 20:15/20:44/21:04 WIB, cakupan s.d. blok 132404141). Watermark TIDAK dimajukan run ini (sudah 132404141 "
    "via backfill - JANGAN set ke 132404127). Seen file TIDAK di-update run ini (backfill sudah menulis window 2031). "
    "Triase: 1 early lead baru Pressure; 6 same-owner-discarded (owner 0x1103... AGENT DOSSIER/PASS/CORE/BOTS/TERMINAL "
    "+ ORBIT PASS re-konfirmasi) + Arcadion (0x5304...) + Lycanthrax (0xd76d...) + Bamboo Mafia/Sly Hours (0x293f...); "
    "5 bukan agent-shaped (MiChan, Delveria Gear, Elynance, Aiuki, Brookwood Village Townhomes). "
    "5c: 55 ERC20 mint_count>=10, 53 sudah dicek, 2 baru dicek (0x2fD1... 1000 mint, 0x4fD9... 10 mint) - 0 sale-shape; "
    "track-c-scan-checked.json +2 (sudah ditulis Subagent A, kini 1544 top-level). "
    "FLAG BACKFILL MASIH AKTIF (lihat runNote2031_1108_backfill): cron free-mint-backfill (interval 15 mnt) masih "
    "enabled=true padahal user memerintahkan 'Nonaktifkan backfill' 2026-11-08 ~06:28 WIB; proses backfill-parallel.py "
    "terlihat BERJALAN 21:17 WIB (worker blok 132404142-132407133) dan scan-state watermark kini 132404141 "
    "(last_scan_wib='backfill-parallel 132401212-132404141'). Parent TIDAK menonaktifkan jadwalnya sendiri (di luar "
    "arahan body run ini) - dilaporkan sebagai flag agar main agent/user yang menonaktifkan."
)
snap["runNote2031_1108_backfill"] = (
    "FLAG: backfill MASIH BERJALAN meski user menonaktifkan 2026-11-08 ~06:28 WIB (tap 'Nonaktifkan backfill'). "
    "Bukti run 2031: (1) cron.list: job free-mint-backfill (interval 15m, owner goal:pencarian-rutin-project-free-mint) "
    "enabled=true; (2) proses live 21:17 WIB: backfill-parallel.py --chunks 3 --deadline-secs 600 + worker "
    "backfill-scan.py blok 132404142-132406141 dan 132406142-132407133; (3) backup backfill 20:15/20:44/21:04/21:12 WIB "
    "(132395599-132397513, 132397514-132401211, 132401212-132404141); (4) onchain-scan-state.json last_scanned_block "
    "= 132404141, last_scan_wib='backfill-parallel 132401212-132404141'. Efek: gap scan run ini (132401212-132403127) "
    "tertutup backfill, bukan scan run ini; seen file + watermark sudah dimajukan backfill. Run ini TIDAK backfill "
    "apa pun sendiri. TINDAKAN: parent TIDAK mengubah jadwal (di luar arahan body) - perlu penonaktifan oleh main agent/user."
)
snap["runNote2031_1108_web"] = (
    "Kaki web run 2031 (Subagent B, 20:31-21:10 WIB): Boltbook boltbook.fun EN+ZH dibaca langsung + author pages "
    "(URL author tidak terekspos di text fetch - gap sama spt run 1931); sweep EN+ZH (proyek baru di luar Boltbook: "
    "nihil; AgentID AGI = Ethereum + whitelist penuh -> dikecualikan; agent-launch.ai = testnet); Sourcify feed 20 item "
    "(5 S1 baru = AGENT DOSSIER/PASS/CORE/BOTS/TERMINAL, batch 13:12:21-13:12:32 UTC, ABI identik template 0x1103 - "
    "semuanya same-owner-discarded, BUKAN lead); Odaily 14 flash + PANews = 0 item Agent ID; DappBay = tanpa listing "
    "untuk item-item ini (ketiadaan bukan bukti). x.com fetch DIBLOKIR policy (1 percobaan) - hanya memengaruhi cek X "
    "opsional Pokechain; link X dari situs proyek sendiri tetap jadi linkage; X tidak pernah meng-gate eksekusi. "
    "Gate: Pokechain TERVERIFIKASI (pokechain.trade + /js/app.js MINT_CA persis); HELIX/BAHUANG2/NUSA TETAP GAGAL. "
    "Temuan web BMT Agents + Saturnagent + 3 lane 0x1103 + Wisp Agent: verifikasi on-chain di runNote age exclusions "
    "di atas (BMT/Pilotchrome/Forklings/Saturnagent age-excluded; 3 lane same-owner; Wisp pending verifikasi run berikut)."
)
save(BASE + "/onchain-snapshot.json", snap)
print("MERGE DONE contracts=%d track_c=%d changed=%d degraded=%d vel_pass=%s tc_changed=%s removed=%s" % (
    len(contracts), len(track_c), len(changed), degraded, vel_pass, tc_changed, [r["name"] for r in removed]))
print("CHANGED:", [(n, o, t, m, p, s) for (n, o, t, m, p, s) in changed][:40])
print("VEL_PASS:", vel_pass)
