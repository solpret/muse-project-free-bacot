#!/usr/bin/env python3
"""CORRECTED merge for free-mint-search run 2026-11-12 18:31 WIB.
Replaces the sed-cloned merge (which carried hardcoded run-1801 values
mislabeled as 1831 and would have overwritten RunicKey 263/325=80.92%
strong-lead with stale 130/325=40.0% 'BUKAN strong lead').
Sources this run ONLY:
- /tmp/run1831-verify.log (stdout lines; verify.py was killed by its 900s
  timeout BEFORE writing verify.json — readings parsed from the log),
- run-2026-11-12-1831-runic.json (fresh RunicKey re-read, block 133152835),
- run-2026-11-12-1831-legs.json (feed/Boltbook/bridge).
Retry/reread/freepool SKIPPED this run (runtime restart killed the first
verify attempt; re-run verify hit the 900s timeout; next run 19:01 already
starting). Batch-fail targets keep stored values (degradation, not zero).
View-consistent updates only; None never overwrites a stored value.
Atomic snapshot write (temp + os.replace); backup to .bak-1831 first.
No preview/mint."""
import ast, json, os, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-12 18:31 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1831")
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.setdefault("contracts", {})
updated = []

# --- parse verify stdout log ---
reads = {}
for line in open("/tmp/run1831-verify.log"):
    line = line.strip()
    if not line or " BATCH-FAIL " in line or " BATCH-FAIL" in line and " {" not in line:
        continue
    # format: NAME {dict} contractURI: <value>
    try:
        name, rest = line.split(" ", 1)
        dstr = rest[:rest.index("} contractURI:") + 1]
        views = ast.literal_eval(dstr)
        contract_uri = rest[rest.index("} contractURI:") + len("} contractURI:"):].strip()
        reads[name] = {"views": views, "contractURI": contract_uri if contract_uri != "None" else None}
    except Exception:
        continue

FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
          "MAX_SUPPLY", "mintOpen", "mintStart", "saleStart", "saleEnd", "mintEnd",
          "freeSharesLeft", "openedAt", "freeSharesRemaining", "launched",
          "freeRemaining", "paidMinted", "FREE_MAX", "MAX_PER_WALLET", "price", "PRICE"]
USER_FIELDS = ["balanceOf_user", "freeClaimed_user", "freeUsed_user", "mintedBy_user",
               "freeMintedBy_user", "freeAvailable_user"]
NAME_FIX = {"Stampooor": "Stampooor Stamp Packs"}
SKIP_ABSURD = {"freeLeft"}  # garbage huge values from SAINTS freeLeft views

def apply(name, views, note):
    e = contracts.get(name)
    if e is None or not views:
        return
    changes = []
    for f in FIELDS:
        if f in views and views[f] is not None:
            if f in SKIP_ABSURD and isinstance(views[f], int) and views[f] > 10**30:
                continue
            if e.get(f) != views[f]:
                changes.append(f"{f}:{e.get(f)}->{views[f]}")
            e[f] = views[f]
    for f in USER_FIELDS:
        if f in views and views[f] is not None:
            e[f] = views[f]
    e["lastReadWib"] = NOW
    e["runNote1831"] = note + ((" | " + "; ".join(changes)) if changes else " | no change")
    updated.append(name)

for name, r in reads.items():
    if name in ("binanceai-mint", "RigForge"):
        continue
    apply(NAME_FIX.get(name, name), r["views"], "Run 1831 verify (stdout log; script killed at 900s timeout before JSON)")

# binanceai + RigForge handled from their own reads (RigForge views were read)
rg = reads.get("RigForge")
if rg:
    e = contracts.get("RigForge")
    if e:
        for f in ("freeClaimed", "freeSharesLeft", "openedAt", "FREE_SHARES"):
            if rg["views"].get(f) is not None:
                e[f] = rg["views"][f]
        e["runNote1831"] = "Run 1831 verify: openedAt TETAP 0 (belum buka), freeClaimed 337, freeSharesLeft 663 - tidak ada perubahan."
        e["lastReadWib"] = NOW
        updated.append("RigForge")

# --- RunicKey: FRESH strong-lead promotion, gate BLOCKED ---
rk = json.load(open(BASE + "run-2026-11-12-1831-runic.json"))
rv = rk["views"]
rk_e = contracts.setdefault("RunicKey", {})
rk_e.update({
    "name": "RunicKey",
    "address": "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4",
    "status": "strong-lead-gate-blocked-2026-11-12",
    "source": "hot-leg-1754 early lead; PROMOTED run 1831 to strong lead (gate FAILED, reported once)",
    "totalSupply": rv["totalSupply"], "totalMinted": rv["totalMinted"],
    "freeMinted": rv["freeMinted"], "FREE_SUPPLY": rv["FREE_SUPPLY"],
    "MAX_SUPPLY": rv["MAX_SUPPLY"], "freeRemaining": rv["freeRemaining"],
    "mintOpen": rv["mintOpen"], "isFreeOpen": rv["isFreeOpen"],
    "saleStart": rv["saleStart"], "saleEnd": rv["saleEnd"],
    "balanceOf_user": rv["balanceOf_user"], "freeAvailable_user": rv["freeAvailable_user"],
    "freeMintedBy_user": rv["freeMintedBy_user"], "mintedBy_user": rv["mintedBy_user"],
    "FREE_MODE": rv["FREE_MODE"], "PRICE": rv["PRICE"], "paidMinted": rv["paidMinted"],
    "freePctVerified": rk["freePct"],
    "agentIdRegistry": rk["agentIdRegistry"],
    "lastReadBlock": rk["block"], "lastReadWib": "2026-11-12 18:34 WIB",
})
rk_e["gateNote1831"] = (
    "STRONG LEAD run 1831 (baca segar blok 133152835 ~18:34 WIB): freeMinted 263/325 = 80,92% (>70%), "
    "saleStart 1794481219 = 2026-11-12 18:00:19 WIB (umur ~34 mnt, TERVERIFIKASI <24 jam), slot user TERBUKA "
    "(freeAvailable 1, balanceOf 0, freeMintedBy 0), mintOpen 1, isFreeOpen 1, freeRemaining 62, "
    "agentIdRegistry = registry Binance 0x60B926...22F, audit Binance hasResult=false (tidak ada hasil, "
    "bukan pass; riskLevel LOW, tanpa risk item) per hot-leg 1814. MANDATORY WEBSITE GATE = GAGAL "
    "setelah metode (A)-(N): (A) pencarian alamat kontrak 0 hasil relevan; (B) Boltbook EN+ZH 1814 "
    "tanpa 'Runic'/0ec2; (C) Sourcify sources+metadata (exact_match) tanpa URL proyek (hanya URL "
    "library/dok generik); (D) runickey.pages.dev / runic-key.pages.dev / runickey.vercel.app tidak "
    "terjangkau (HTTP 000), runickey.deed.page + runic-key.vercel.app 404, tidak ada yang mencetak "
    "kontrak; (E) owner() pure -> address(0), 'no owner and no admin function' (source) - tanpa grup "
    "deployer; (F) tidak ada handle X ditemukan di mana pun - n/a (X opsional); (G) pencarian nama "
    "proyek 0 hasil proyek (hanya Oathbots/ENIGMAAGENT/dll.); (H) contractURI base64 JSON: nama + "
    "deskripsi mencetak kontrak persis, TANPA external_link/external_url/website; (I) tokenURI(1) "
    "base64 JSON: sama, tanpa external_url (atribut: Edition Free, Subject Vault key, Palette moss, "
    "Variant 6); (J) grep ABI: hanya contractURI/tokenURI, tanpa fungsi site/URL/domain; (K) GitHub "
    "code search 0 hasil (pencarian kode sejati butuh auth - keterbatasan dicatat); (L) BscScan "
    "token-info via browser: DIBLOKIR Cloudflare bot check (halaman tidak pernah termuat, Ray ID "
    "a59545c37c5debf2 18:42 WIB) - TIDAK dapat diverifikasi, BUKAN bukti tidak ada website; "
    "(M) site:vercel.app/pages.dev 0 hasil; (N) tidak ada post Boltbook -> tanpa author hop; tanpa "
    "handle Agent ID proyek -> profil registry tidak dapat di-resolve. KESIMPULAN: TIDAK ADA website "
    "proyek terverifikasi -> gate GAGAL -> TIDAK di-preview, TIDAK di-mint (aturan gate wajib). "
    "Dilaporkan SEKALI sebagai strong lead gate-blocked run ini. Free-mint entry (bila gate lolos di "
    "run berikut): freeMint() no-arg, value 0, MODE_FREE; costOfMint(user,1,mode) belum dibaca segar.")
rk_e["runNote1831"] = ("Run 1831: PROMOSI early -> strong lead (263/325 = 80,92%), GATE-BLOCKED "
    "(metode A-N, lihat gateNote1831). TIDAK di-preview/di-mint.")
updated.append("RunicKey")

# --- NAPPER: contractURI pointer (H) found, site does NOT print contract ---
np = contracts.get("NAPPER")
if np is not None:
    np["contractURI1831"] = "https://dreamcompile.pages.dev/meta/collection.json"
    np["gateNote1831"] = ("Run 1831 verify: contractURI() -> dreamcompile.pages.dev/meta/collection.json "
        "(nama DREAMCOMPILE, external_link https://dreamcompile.pages.dev). Homepage situs HIDUP "
        "(HTTP 200, 33.115 byte, judul DREAMCOMPILE) TAPI TIDAK mencetak kontrak NAPPER "
        "0x3964BFc3354C0d18886dcAD52Abc55C689e6A1d4 (0 kemunculan; footer 'Collection address: Mint opens "
        "soon'; tanpa alamat 0x di halaman; tanpa sebutan NAPPER). Per standar ketat: external_link saja "
        "tanpa situs mencetak kontrak BUKAN bukti website -> gate NAPPER TETAP UNVERIFIED. "
        "mintStart 1794409230 = 2026-11-11 22:00:30 WIB terkonfirmasi (jendela tutup ~22:00 WIB hari ini); "
        "free% TETAP UNVERIFIED. Watchlist-only, BUKAN strong lead/kandidat.")
    np["lastReadWib"] = NOW
    updated.append("NAPPER")

# --- MECHA velocity + free% (verify segar) ---
m = contracts.get("MECHA", {})
m["freePctVerified"] = round(1818 / 4444 * 100, 1)
m["velocityNote1831"] = ("Run 1831 verify: totalMinted 1819 / freeClaimed 1818 (vs 1801: 1815/1814) = +3-4 "
    "token dalam ~45-60 mnt (~0,07/mnt) -> velocity GAGAL (<20 token, rate turun). free% TERVERIFIKASI "
    "40,9% <50% (bukan kandidat) dan <70% (bukan strong lead). TETAP watchlist-only.")
m["lastReadWib"] = NOW
updated.append("MECHA")

# --- SAINTS velocity (verify segar vs 1801) ---
for _nm, _old, _new in (("CRTSAINTS", 146, 148), ("0x2e50", 137, 137), ("MOONDRILL", 121, 123)):
    _e = contracts.get(_nm)
    if _e:
        _e["velocityNote1831"] = (f"Run 1831 verify: {_old}->{_new} (+{_new - _old} dalam ~45-60 mnt) -> "
            "velocity TIDAK lulus (<20 token dalam interval). free% TETAP UNVERIFIED (freeLeft garbage). "
            "Umur terverifikasi <24 jam. Tetap early-lead-reported, BUKAN strong lead/kandidat.")
        _e["lastReadWib"] = NOW
        updated.append(_nm)

snap["runNote1831"] = (
    "Run 1831 (jadwal 18:31 WIB, eksekusi ~18:31-19:05 WIB): 1 STRONG LEAD BARU = RunicKey (263/325 = 80,92%, "
    "umur terverifikasi ~34 mnt, slot terbuka) TAPI GATE-BLOCKED (metode A-N, tanpa website terverifikasi; "
    "BscScan diblokir Cloudflare) -> dilaporkan SEKALI sebagai strong lead gate-blocked, TIDAK di-preview/di-mint. "
    "0 kandidat baru, 0 early lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. "
    "Pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov) - scan leg fast-fail, watermark TETAP 132512564; "
    "5c dilewati (tanpa output scan). Verify: 16/23 target terbaca dari stdout log SEBELUM script mati timeout 900 dtk "
    "(JSON tidak tertulis); 7 BATCH-FAIL (binanceai-mint, 0x7Eb9, AgenticGangster, OLIVER, AIRDROP, Cobalt, NAPPER "
    "- nilai lama dipertahankan, BUKAN nol). Retry/reread/freepool DILEWATI run ini (restart runtime mematikan verify "
    "percobaan pertama tanpa output; verify ulang kena timeout 900 dtk; run 19:01 sudah mulai). "
    "Legs: feed 20 kontrak (verifiedAt 11:18-11:40 UTC), 20 baru vs hot-leg-seen, 4 ter-shape-check (semua bukan S1/S2/early), "
    "16 ERROR transport Sourcify (IncompleteRead/RemoteDisconnected - diserahkan ke retry-404 hot leg); Boltbook EN "
    "44.622 byte / ZH 43.163 byte, 1 baru (0xc98c... Sourcify 404, bukan lead); Bridge 116 kontrak, 0 not-in-snapshot, "
    "7 same_owner_discarded (tidak dipromosikan). Sweep EN+ZH: semua sudah dikenal (Agentite age-excluded 10 Nov, "
    "STAMP PASS free pool habis 10 Nov, RIGBYPASS/NAOMI/Agentic Gangster/Oathbots/Laser Agents/AGENT ID card/Pixel Pets "
    "dikenal). NAPPER: pointer (H) baru dreamcompile.pages.dev - situs hidup tapi TIDAK mencetak kontrak -> gate tetap "
    "unverified. binanceai pending claim: BATCH-FAIL run ini, status terakhir launched()=0 (fase refund, run 1801). "
    "RigForge openedAt TETAP 0. Velocity: tidak ada kontrak naik >=20 token (MECHA +3, SAINTS +2/0/+2, Stampooor +4, "
    "BUCKET +1). Age-exclusion baru: TIDAK ADA. Deadline terdekat: CRTSAINTS ~20:50, 0x2e50 ~21:00, MOONDRILL ~21:10, "
    "NAPPER ~22:00 WIB hari ini.")
snap["runNote1831_runic_gate"] = contracts["RunicKey"]["gateNote1831"]
snap["runNote1831_verify_timeout"] = (
    "Run 1831 verify: percobaan pertama MATI oleh restart runtime (~18:46 WIB, tanpa output); percobaan kedua "
    "dijalankan ulang 18:46-19:01 WIB dan MATI oleh timeout 900 dtk (exit 124) pada target NAPPER (target ke-23 dari 26) "
    "sebelum menulis JSON. Pembacaan 16 target diselamatkan dari stdout log (/tmp/run1831-verify.log) dan di-merge di sini; "
    "7 BATCH-FAIL tidak di-retry run ini (retry/reread/freepool dilewati karena run 19:01 sudah mulai). RPC terdegradasi "
    "parah sepanjang run (batch eth_call sering gagal; Sourcify IncompleteRead berulang).")
snap["runNote1831_age_exclusions"] = (
    "Run 1831 AGE-EXCLUSION: TIDAK ADA yang baru. ROBO sudah log-only run 1801. Stampooor deadline 09:00 WIB hari ini "
    "LEWAT (age-excluded, dicatat run 1401; entri dipertahankan sebagai holding user, balance 1). Deadline terdekat: "
    "CRTSAINTS ~20:50 WIB, 0x2e50 ~21:00 WIB, MOONDRILL ~21:10 WIB, NAPPER ~22:00 WIB hari ini.")
snap["last_run"] = NOW
snap["last_run_note"] = ("Run 1831: 1 strong lead baru (RunicKey 80,92%) GATE-BLOCKED -> lapor sekali, tanpa eksekusi; "
    "0 kandidat/early/track-B/track-C baru. Verify timeout 900 dtk (16/23 terbaca via stdout log); "
    "retry/reread/freepool dilewati; pre-flight Ankr 401 fast-fail; watermark tetap 132512564.")

tmp = BASE + "onchain-snapshot.json.tmp-1831"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")

legs = json.load(open(BASE + "run-2026-11-12-1831-legs.json"))
summary = {"run": NOW, "updated": sorted(set(updated)), "n_updated": len(set(updated)),
           "verify_reads_from_log": sorted(reads.keys()),
           "verify_batch_fail": ["binanceai-mint", "0x7Eb9", "AgenticGangster", "OLIVER AGENTS",
                                 "AIRDROP", "Cobalt Agent", "NAPPER"],
           "runic_block": rk["block"], "runic_freePct": rk["freePct"],
           "legs_feed_new": legs.get("feed_new"), "legs_boltbook_new": legs.get("boltbook_new"),
           "legs_bridge": legs.get("bridge")}
json.dump(summary, open(BASE + "run-2026-11-12-1831-merge.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
print("MERGE DONE (corrected)")
