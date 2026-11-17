#!/usr/bin/env python3
"""Merge run 1531 reread+vel+new-verify into snapshot. FRESH for run 1531 only.
Main events run 1531:
- YAMA age-excluded (verified first mint 2026-11-08 15:18:20 WIB, 48h deadline
  ~15:18 WIB 2026-11-10 passed during this run; free pool NOT sold out) ->
  removed from track_c, recorded in age_exclusions, reported once.
- NOGENT + Hakuna (Boltbook leads): Sourcify UNVERIFIED, no agentRegistry view,
  registry-bytes only (insufficient per prototype rule) -> NOT early leads;
  added as watchlist-only-unverified, NOT reported as leads.
- BITCAT sale 0x57787441...: already minted by user 12:30 WIB (user order);
  free pool now 1000/1000 exhausted -> track_c entry minted-by-user.
- Velocity passes 5 (AGENT CORE, SonoWaves, DRIFTWIRE, Pickgrid, Arcane Stones)
  -> NO promotion (discarded / minted / % or age unverified).
- Scan fast-fail Ankr 401; feed 20/20 0 S1/0 S2; binanceai still refund/failed.
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1531"
BLOCK = 132745406
NOW = "2026-11-10 15:31 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1531-premerge")

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
        entry["intervalMinutes"] = 30.0
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote1531_1110"] = text

def dyn_note(name, extra=""):
    row = vel.get("rows", {}).get(name, {})
    f = rr.get("reread", {}).get(name, {})
    e = snap["contracts"].get(name, {})
    if not row:
        return None
    minted = row.get("minted"); rate = row.get("rate"); ratio = row.get("ratio")
    passes = row.get("passes")
    fm = f.get("freeMinted"); fc = f.get("freeClaimed")
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP") or e.get("agentFreeCap") or e.get("MAX_SUPPLY")
    freetxt = ""
    if fm is not None and cap:
        freetxt = f"; freeMinted {fm}/{cap} = {fm/cap*100:.1f}%"
    elif fc is not None and cap:
        freetxt = f"; freeClaimed {fc}/{cap} = {fc/cap*100:.1f}%"
    vtxt = "velocity LOLOS" if passes else "velocity GAGAL"
    return (f"Run 1531 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra}")

# ---- SEVENFOLD: velocity fails this run; audit-block stands ----
sev = snap["contracts"]["SEVENFOLD"]
sev["freePctVerified"] = round(1723/3000*100, 1)
note("SEVENFOLD", (dyn_note("SEVENFOLD") or "") +
     " KANDIDAT tetap AUDIT-BLOCKED (dilaporkan 12:03 + 13:30; tidak dilaporkan ulang). "
     "free 1723/3000 = 57,4% >=50% tapi velocity GAGAL run ini (20 token, 0,51x). "
     "Audit-block dari run 1431 dipertahankan (token MORROW riskLevel 4 HIGH + RISK); tidak di-audit ulang run ini. TIDAK preview/mint.")
note("THYRK", (dyn_note("THYRK") or "") + " Sudah minted-by-user (#6849 run 1231 + 20 THYRK pending swap) -> velocity GAGAL run ini, tanpa relevansi.")
note("DRIFTWIRE", (dyn_note("DRIFTWIRE") or "") + " Sudah minted-by-user (#745 run 1231) -> velocity lolos tidak relevan, TANPA promosi.")
note("Pickgrid Pickaxe", (dyn_note("Pickgrid Pickaxe") or "") +
     " Tetap EARLY lead: velocity LOLOS run ini, freeMinted 179 = totalSupply 179 (semua mint gratis sejauh ini) "
     "tapi FREE_SUPPLY/MAX_SUPPLY tetap None -> % kuota gratis TIDAK terverifikasi (angka snapshot 39,0% tanpa catatan pendukung, jangan dipakai sebagai verified); "
     "umur UNVERIFIED + website BELUM DINILAI -> bukan strong lead, TIDAK preview/mint.")
note("Arcane Stones", (dyn_note("Arcane Stones") or "") +
     " Tetap EARLY lead: velocity LOLOS run ini (137 token, 2,25x), totalSupply 416->553; free views tetap None -> free% UNVERIFIED; "
     "umur UNVERIFIED; website TERVERIFIKASI. Bukan strong lead (umur + free% unverified), TIDAK preview/mint.")
note("SonoWaves", (dyn_note("SonoWaves") or "") +
     " Tetap watchlist-only-age-unverified: velocity LOLOS run ini (114 token, 4,95x), freeMinted 333/2260 = 14,7% (<25%); "
     "umur dari first public post 11:19 WIB hari ini (belum koroborasi on-chain). Bukan strong lead, TIDAK preview/mint.")
note("AGENT CORE", (dyn_note("AGENT CORE") or "") +
     " Velocity LOLOS run ini TAPI status promotion-discarded-same-owner-2026-11-09 -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead (aturan same-owner-discards). Log saja.")
note("Cinder Agents", (dyn_note("Cinder Agents") or "") + " Tetap early lead (free% + umur + website unverified).")
note("PanduAGENT Phase 2", (dyn_note("PanduAGENT Phase 2") or "") + " Tetap early lead (free% + umur + website unverified).")
note("Orbit Signal", (dyn_note("Orbit Signal") or "") + " Tetap early lead (umur/free%/website UNVERIFIED).")
note("Claf Eye", (dyn_note("Claf Eye") or "") + " Tetap early lead (totalSupply 2730->~3084 per Boltbook; website UNVERIFIED; umur UNVERIFIED).")
note("Sakura", (dyn_note("Sakura") or "") + " Tetap early lead; first mint terverifikasi 2026-11-10 01:47 WIB -> deadline 48 jam 2026-11-12 01:47 WIB.")
note("Golden Agents", (dyn_note("Golden Agents") or "") + " Tetap early lead; first mint terverifikasi 2026-11-09 ~02:00 WIB -> deadline 48 jam 2026-11-11 ~02:00 WIB.")
note("ELSY AGENT", (dyn_note("ELSY AGENT") or "") + " Pasca-mint terverifikasi: bal_user=2 (#880/#881). TIDAK di-auto-list (own market tidak live).")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")
note("Kappaxis", (dyn_note("Kappaxis") or "") + " Tetap watchlist-only-scan; launch UNVERIFIED (tanpa launchNote) -> tidak age-exclude; free 1413/2309 = 61,2% per Boltbook 15:26 (baca ulang run ini menyusul).")
note("Lambdwyn", (dyn_note("Lambdwyn") or "") + " Tetap watchlist-only-scan; launch UNVERIFIED -> tidak age-exclude; free 718/2324 = 30,9% per Boltbook 15:33.")
note("NEKART", (dyn_note("NEKART") or "") + " Tetap early-lead-reported; supply BEKU 886 (Boltbook 15:3x), pace nyaris nol.")

# ---- NOGENT: Boltbook lead baru, BUKAN early lead (agent-shape unverified) ----
snap["contracts"]["NOVA AGENT"] = {
    "address": "0x1b6e6f62528de674c12bc2c04c159336d3db049e",
    "status": "watchlist-only-unverified-2026-11-10",
    "name": "NOVA AGENT", "symbol": "NOGENT", "kind": "ERC721",
    "totalSupply": 1209, "MAX_SUPPLY": 5555,
    "FREE_PER_WALLET": 2, "MAX_PER_WALLET": 10, "mintOpen": 1,
    "mintPrice": 500000000000000,
    "owner": "0xc53efe7b6dc421fe198fe619a889e4ce1fc25e6d",
    "freePctVerified": None,
    "freePctNote": "UNVERIFIED: tanpa free view (freeMinted/freeClaimed/freeLeft/FREE_SUPPLY semua None); 1209/5555 = 21,8% adalah % total-supply, BUKAN % kuota gratis.",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur UNVERIFIED: pertama terlihat di feed Boltbook 23:43 UTC (~06:43 WIB 10 Nov); tidak ada stated launch time; first-mint on-chain TERBLOKIR (Ankr 401).",
    "websiteNote": "Website UNVERIFIED: WEBSITE()/X()/contractURI() on-chain = None; tidak ada situs ditemukan run ini.",
    "baselineNote": ("BARU run 1531 (Boltbook front page EN+ZH, post 'NOVA AGENT (NOGENT)': totalSupply 1.208/5.555, FREE_PER_WALLET 2, "
        "mintPrice 0,0005 BNB, mintOpen true; Sourcify tidak terverifikasi). Verifikasi on-chain run ini (run-2026-11-10-1531-new-verify.json): "
        "totalSupply 1209/5555, FREE_PER_WALLET 2, MAX_PER_WALLET 10, mintPrice 0,0005 BNB, mintOpen 1; free views None; costOf/costFor/priceOf None; "
        "agentRegistry()/agentId() None; Sourcify 404 NOT VERIFIED; registry_bytes=True TAPI itu saja TIDAK cukup (prototipe: 81% kontrak factory-template "
        "mengandung registry bytes) -> agent-shape TIDAK terverifikasi -> BUKAN early lead, TIDAK dilaporkan sebagai lead. "
        "Owner 0xc53e... TIDAK di same-owner-discards. Slot user belum terverifikasi (tanpa cost view)."),
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "currentRatePerMin": None, "velocityLegPasses": False,
}

# ---- Hakuna: Boltbook lead baru, BUKAN early lead (agent-shape unverified) ----
snap["contracts"]["Hakuna"] = {
    "address": "0x75f9e01af66a6b3b5f169d1d9c88e6f356a01e2f",
    "status": "watchlist-only-unverified-2026-11-10",
    "name": "Hakuna Agent", "symbol": "HAKUNA", "kind": "ERC721",
    "totalSupply": 377, "MAX_SUPPLY": 4444,
    "freeMinted": 377,
    "FREE_PER_WALLET": 1, "MAX_PER_WALLET": 44, "mintOpen": 1,
    "owner": "0x36f3d56ead5d1d6c2434f94defcef732c5c3cbd2",
    "freePctVerified": None,
    "freePctNote": "UNVERIFIED: freeMinted 377 = totalSupply 377 (semua mint gratis sejauh ini, paidMinted 0 per Boltbook) tapi FREE_SUPPLY None -> % kuota gratis tidak terverifikasi; 377/4444 = 8,5% adalah % total-supply.",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur UNVERIFIED: tidak ada stated launch time; first-mint on-chain TERBLOKIR (Ankr 401). Pertama terlihat job ini run 1531 (Boltbook front page).",
    "websiteNote": "Website UNVERIFIED: WEBSITE()/X()/contractURI() on-chain = None; tidak ada situs ditemukan run ini.",
    "baselineNote": ("BARU run 1531 (Boltbook front page EN+ZH, post 'Hakuna': totalSupply 376/4.444, freeMinted 376, FREE_PER_WALLET 1, mintOpen 1; "
        "klaim konflik sim lolos vs revert). Verifikasi on-chain run ini (run-2026-11-10-1531-new-verify.json): totalSupply 377/4444, freeMinted 377, "
        "FREE_PER_WALLET 1, MAX_PER_WALLET 44, mintOpen 1; costOf/costFor/priceOf None; agentRegistry()/agentId() None; Sourcify 404 NOT VERIFIED; "
        "registry_bytes=True saja TIDAK cukup -> agent-shape TIDAK terverifikasi -> BUKAN early lead, TIDAK dilaporkan sebagai lead. "
        "Owner 0x36f3... = owner yang sama dengan SonoWaves + Sakura (grup deployer sama, BUKAN same-owner-discards). Slot user belum terverifikasi (tanpa cost view)."),
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "currentRatePerMin": None, "velocityLegPasses": False,
}

# ---- YAMA: age-excluded (verified first mint 2026-11-08 15:18:20 WIB; deadline ~15:18 WIB passed) ----
yama = snap.get("track_c", {}).pop("YAMA", None)
if yama is not None:
    snap.setdefault("age_exclusions", []).append({
        "name": "YAMA", "sale": "0x86d779fc4d83044cceccb53639f9a98e367d6e46",
        "token": "0xa84ea20a667b3b1859ab9a9984ff5f03d8688ae2",
        "firstMintWib": "2026-11-08 15:18:20 WIB (blok 132359287, first Minted event, Ankr getLogs)",
        "ageHours": 48.6,
        "supply": "totalFreeShares 2591/100000 (terakhir terverifikasi run 1431b ~14:53 WIB; baca ulang run 1531 gagal transport, semua None)",
        "free": "2,59% free pool terpakai; 97.409 free tersisa; TIDAK sold out",
        "status_before": "lead-reported-audit-blocked-2026-11-10",
        "removed_run": "2026-11-10 run 1531",
        "removed_wib": "2026-11-10 15:51 WIB",
        "reason": "Umur peluncuran terverifikasi 48,6 jam (>48 jam) dan belum sold out; lead audit-blocked (token RISK 'Contract Not Renounced') yang tidak pernah di-mint; dihapus dari track_c aktif per aturan umur 48 jam; dilaporkan sekali run ini.",
    })

# ---- BITCAT: user-minted 12:30 WIB (user order); free pool now exhausted ----
snap.setdefault("track_c", {})["BITCAT"] = {
    "sale": "0x577874415214780b37eb8966c41563954b76a8b8",
    "token": "0x8708ee82fa34c58431532323530592ee3953e9d5",
    "name": "BITCAT", "symbol": "BITCAT", "kind": "ERC20-sale-S1",
    "status": "minted-by-user-2026-11-10",
    "saleShape": "PASS (S1): claimFree() + quote + freeClaimed + agentIdOf/agentIds, Sourcify exact_match",
    "website": "bitcat (situs + /skill.md + /config.json mencetak kontrak sale+token persis — terverifikasi perintah user 12:30 WIB)",
    "freeClaimed": 1000,
    "freePoolNote": "Free pool HABIS 1000/1000 (terverifikasi run 1531, new-verify); user sudah mint 1 share -> 37.777.776.000 BITCAT 12:30 WIB.",
    "pair": "0x8dD64bb9F614D58716eB0e343e1F794B2E7A04f4 (cadangan 0/0, transfer terkunci s.d. open; pending-swaps.json entri ke-14)",
    "baselineNote": "Mint perintah user 12:30 WIB (bukan run rutin). Run 1531 memverifikasi ulang: freeClaimed 1000/1000 (pool habis), priceOf(1)=0, Sourcify exact_match. Slot user sudah terpakai; tidak ada aksi rutin.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
}

# ---- track_c lastRead updates ----
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    if name in rr.get("track_c", {}):
        entry["lastReadBlock"] = BLOCK
        entry["lastReadWib"] = NOW
tc = snap.get("track_c", {})
if isinstance(tc.get("NUSA"), dict):
    tc["NUSA"]["runNote1531_1110"] = ("Run 1531: freeMinted 370 (tetap), freeClaimed(user)=0, gate FAILED (website tidak terverifikasi); "
        "deadline umur 48 jam 2026-11-10 17:05 WIB (~1 jam lagi dari run ini). TIDAK preview/mint, TIDAK dilaporkan ulang.")
if isinstance(tc.get("FOUNT"), dict):
    tc["FOUNT"]["runNote1531_1110"] = "Run 1531: freeMinted 1000 (tetap), totalSupply 1e27, bal_user=0. Tetap watchlist-only-boltbook; umur UNVERIFIED. TIDAK ada perubahan."
if isinstance(tc.get("WNO"), dict):
    tc["WNO"]["runNote1531_1110"] = ("Run 1531: pasca-mint terverifikasi — balanceOf(user) 1.000.000 WNO (1e24) tetap; totalSupply 6e27; "
        "freeClaimed(user) belum terbaca ulang (transport). Pair PCS V2 tetap 0x0 (belum ada) -> tetap di pending-swaps.json (no_pair).")

snap["last_run"] = 1
snap["last_run_wib"] = NOW
snap["last_run_block"] = BLOCK
snap["last_run_note"] = ("Run 1531: re-read 657 kontrak + 76 track_c (blok 132745406; run terpotong restart runtime, dilanjutkan resume). "
    "Velocity LOLOS 5 (AGENT CORE, SonoWaves, DRIFTWIRE, Pickgrid Pickaxe, Arcane Stones) — TANPA promosi "
    "(discarded / minted / free% atau umur unverified). SEVENFOLD velocity GAGAL, free 57,4%, audit-block dipertahankan. "
    "BARU watchlist-only (BUKAN lead): NOVA AGENT + Hakuna (Boltbook; Sourcify unverified, agent-shape tidak terverifikasi). "
    "BITCAT: free pool habis 1000/1000 (sudah di-mint user 12:30 WIB). AGE-EXCLUDE 1: YAMA (first mint 2026-11-08 15:18:20 WIB, >48 jam, pool tidak habis) "
    "-> dihapus dari track_c, dilaporkan sekali. NUSA deadline 17:05 WIB (~1 jam lagi). "
    "Scan fast-fail Ankr 401 (preflight 11,0 dtk); watermark TIDAK dimajukan. Feed Sourcify 20/20, 0 S1/0 S2. "
    "binanceai.fun tetap refund/failed (sudah dilaporkan sekali). Bridge: 116 kontrak, 8 belum di snapshot (pola mint ERC20, bukan lead agent-mint; dicatat di run log).")
snap["runNote1531_1110"] = snap["last_run_note"]

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE 1531 DONE: contracts updated={updated}, block={BLOCK}")
print("YAMA removed:", yama is not None)
print("track_c count now:", len(snap.get("track_c", {})))
print("contracts count now:", len(snap.get("contracts", {})))
