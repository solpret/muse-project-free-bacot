#!/usr/bin/env python3
"""Merge run 0031 (2026-11-10 00:31 WIB) reread + triage into onchain-snapshot.json.
INTERVAL 28.9 min (blocks 132621152 -> 132625012, ~0.45s/block). Read-only except snapshot."""
import json, datetime, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL = 28.9
BLOCK = 132625012
NOW_WIB = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0031")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
bak = json.load(open(f"{BASE}/onchain-snapshot.json.bak-0031"))
rr = json.load(open(f"{BASE}/run-2026-11-10-0031-reread.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
n_upd = 0; vel_pass = []; soldout_new = []; soldout_artifact = []; free25 = []
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict):
        continue
    prev_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply")
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4)
        v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if v["velocityLegPasses"]:
            vel_pass.append((name, minted, round(ratio, 2)))
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    fs = v.get("FREE_SUPPLY"); fcl = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fcl, int):
        v["freePctVerified"] = round(100.0 * fcl / fs, 2)
    elif isinstance(fs, int) and fs and isinstance(v.get("freeMinted"), int):
        v["freePctVerified"] = round(100.0 * v["freeMinted"] / fs, 2)
    # sold-out check: only when the free counter CHANGED vs pre-merge backup (artefak view guard)
    if isinstance(fs, int) and fs and isinstance(fcl, int) and fcl >= fs and "sold-out" not in str(v.get("status")):
        old = bak.get("contracts", {}).get(name, {})
        if old.get("freeClaimed") != fcl:
            soldout_new.append((name, fcl, fs))
        else:
            soldout_artifact.append(name)
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW_WIB
    v["runNote0031_1110"] = (f"Run 0031 (blok {BLOCK}, interval {INTERVAL} mnt vs run 0001): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')} fm={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd += 1
    st = str(v.get("status") or "")
    if (isinstance(v.get("freePctVerified"), (int, float)) and v["freePctVerified"] >= 25
        and not any(x in st for x in ("sold-out", "excluded", "minted-by-user", "age-excluded", "discarded"))):
        free25.append((name, v.get("freePctVerified"), v.get("freeClaimed_user"), v.get("balanceOf_user"), st,
                       v.get("startTimeWib"), v.get("launchTime"), v.get("xVerified"), v.get("website"),
                       v.get("mintStartWib"), v.get("firstSeenWib")))
n_tc = 0
for name, v in track_c.items():
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict) or not isinstance(v, dict):
        continue
    if r.get("totalSupply") is not None: v["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None: v["freeMinted"] = r["freeMinted"]
    if r.get("freeSharesRemaining") is not None: v["freeSharesRemaining"] = r["freeSharesRemaining"]
    if r.get("balanceOf_user") is not None: v["balanceOf_user"] = r["balanceOf_user"]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW_WIB
    v["runNote0031_1110"] = f"Run 0031 track_c re-read (blok {BLOCK}): {r}."
    n_tc += 1
# --- PIXEL MONSTERS: free% crossed 25% + age verified -> STRONG LEAD, gate FAILED ---
px = contracts.get("PIXEL MONSTERS")
px_note = ""
if isinstance(px, dict):
    fm = px.get("freeMinted")
    px["freePctVerified"] = round(100.0 * fm / 2000, 2) if isinstance(fm, int) else px.get("freePctVerified")
    px["status"] = "strong-lead-gate-failed-2026-11-10"
    px_note = (f"PIXEL MONSTERS PROMOSI STRONG LEAD run 0031: total {px.get('totalSupply')} (prev {px.get('previousTotalSupply')}, +{px.get('mintedInInterval')}, "
               f"ratio {px.get('velocityRatio')} -> velocity {'LOLOS' if px.get('velocityLegPasses') else 'GAGAL'}); "
               f"freeMinted {fm}/2000 = {px.get('freePctVerified')}% (>=25%); umur TERVERIFIKASI mintStart 2026-11-09 21:35:33 WIB (~3 jam); "
               f"slot user terbuka (freeClaimed_user=0, bal 0). WEBSITE GATE FAILED run 0031 (metode B Boltbook post tanpa link situs; "
               f"C Sourcify metadata tanpa URL; D pixelmonsters.vercel.app = proyek lain 'Community Game Servers', same-name saja; "
               f"H contractURI None; J ABI 48 fungsi tanpa fungsi site/URL; M site: filters nihil; K GitHub butuh auth; L BscScan live tidak dicoba run ini). "
               f"TIDAK preview/mint (gate gagal). Dilaporkan sekali run 0031 sebagai strong lead + alasan blokir.")
    px["runNote0031_1110"] = "Run 0031: " + px_note
# --- STAR CARDS note ---
sc = contracts.get("STAR CARDS")
sc_note = ""
if isinstance(sc, dict):
    sc_note = (f"STAR CARDS: totalSupply {sc.get('totalSupply')}, freeMinted {sc.get('freeMinted')}/5000 "
               f"= {sc.get('freePctVerified')}%; tetap early lead, TIDAK preview/mint.")
# --- STAMP PASS: free pool sold out (verified 2x) ---
st = contracts.get("STAMP PASS")
st_note = ""
if isinstance(st, dict):
    st["totalMinted"] = 112
    st["freeMinted"] = 111
    st["freeRemaining"] = 0
    st["paidMinted"] = 1
    st["canClaimFree_user"] = False
    st["status"] = "sold-out-free-pool-exhausted-2026-11-10"
    st_note = ("STAMP PASS SOLD OUT (free) run 0031: freeMinted 111/111, freeRemaining 0, totalMinted 112 (paid 1), "
               "canClaimFree(user)=0 — terverifikasi 2x (reread blok 132625012 + probe segar blok 132625860). "
               "Early lead run 0001 habis ~30 mnt sesudah dilaporkan. Dilaporkan sekali run 0031; status sold-out, bukan kandidat.")
    st["runNote0031_1110"] = "Run 0031: " + st_note
# --- 0x4Bc1A172 sale note ---
sale = track_c.get("0x4Bc1A172-sale")
sale_note = ""
if isinstance(sale, dict):
    sale_note = (f"0x4Bc1A172 sale: freeMinted {sale.get('freeMinted')} (reread run 0031); "
                 "SALE_START 2026-11-10 12:00 WIB - MASIH BELUM BUKA; tetap watchlist-only-not-open.")
    sale["runNote0031_1110"] = "Run 0031: " + sale_note
# --- Sable Agent: watchlist-only (age unverified + free% unverified + Sourcify unverified + no website) ---
sable = {
    "address": "0x23d356173ff227d5bf6d622f4a8907f208871d76",
    "name": "Sable Agent", "kind": "ERC721",
    "status": "watchlist-only-age-unverified-2026-11-10",
    "totalSupply": 4901, "totalMinted": 4901, "MAX_SUPPLY": 5000,
    "freeClaimed": None, "freeMinted": None, "FREE_SUPPLY": None,
    "mintOpen": None, "owner": "0xe0808a338d96171fa9bde4d4d1897692392a0cbb",
    "balanceOf_user": 0,
    "website": None, "xVerified": False,
    "launchNote": ("Umur peluncuran UNVERIFIED: kontrak tanpa view mintStart/START_TIME; monitor Boltbook pertama mendeteksi "
                   "2026-11-03 17:32 (post dieuxuan50.ai, recheck 00:27 WIB 2026-11-10) — indikasi kuat umur >48 jam, tapi bukan waktu "
                   "launch terverifikasi; koroborasi first-mint via Ankr getLogs tidak bisa (401 sejak 2026-11-09 ~13:33 WIB)."),
    "firstSeenBlock": 132625322, "lastReadBlock": 132625322,
    "lastReadWib": NOW_WIB,
    "baselineNote": ("Boltbook run 0031 (post /p/BvmGnNxZ6k_2, dieuxuan50.ai): 'Sable Agent: 4.901/5.001 free (98,0%)', FREE 1/.ai gas-only "
        "menurut monitor, Sourcify UNVERIFIED. Probe segar blok 132625322: totalSupply=totalMinted=4901, MAX_SUPPLY=5000, "
        "freeClaimed/freeMinted/FREE_SUPPLY/mintOpen/mintStart/START_TIME/agentId() semua revert (template berbeda) — kaki % free UNVERIFIED "
        "(tidak boleh ganti dengan % total supply 4901/5000); balanceOf(user)=0. Owner 0xe080... TIDAK di same-owner-discards.json. "
        "Pencarian nama/kontrak (metode G/A) tanpa situs/launch. BUKAN lead/kandidat/strong (umur + free% unverified, Sourcify unverified, "
        "tanpa website); watchlist-only, TIDAK preview/mint, TIDAK dilaporkan sebagai lead."),
}
contracts["Sable Agent"] = sable
snap["last_run_wib"] = NOW_WIB
snap["runNote0031_1110"] = (f"Run 0031 (2026-11-10 00:31 WIB): reread {n_upd} kontrak + {n_tc} track_c (blok {BLOCK}, interval {INTERVAL} mnt, "
    f"{573.5:.1f} dtk). Velocity LOLOS: {vel_pass}. Sold-out baru: {soldout_new} (+ STAMP PASS free 111/111, verifikasi ganda). "
    f"Artefak freeClaimed==FREE_SUPPLY tak berubah: {len(soldout_artifact)} item. Free>=25%: {free25}. "
    f"PIXEL MONSTERS promosi STRONG LEAD (gate website FAILED -> TIDAK preview/mint, dilaporkan sekali). "
    f"Sable Agent BARU watchlist-only (umur + free% unverified).")
with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print(f"MERGED n_upd={n_upd} n_tc={n_tc} vel_pass={vel_pass}")
print(f"soldout_new={soldout_new} artifact_n={len(soldout_artifact)}")
print(f"free25={free25}")
print("PX:", px_note)
print("SC:", sc_note)
print("STAMP:", st_note)
print("SALE:", sale_note)
