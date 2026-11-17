#!/usr/bin/env python3
"""Merge run 1731 reread+vel into snapshot. FRESH for run 1731 only.
Run 1731 (jadwal 17:31 WIB, dieksekusi 17:41-~18:15 WIB). Block re-read: 132762894.
Reread 661 kontrak + 79 track_c (563,6 dtk).
- Velocity LOLOS 2: Aura Agents (+35, 35,35x) + THYRK (+63, 1,75x) -> TANPA promosi
  (Aura: watchlist-only-not-early sejak 2026-11-03, umur >>48 jam + free% UNVERIFIED;
   THYRK: sudah minted-by-user #6849, slot user terpakai).
- SEVENFOLD +16 (1,78x tapi <20 token) GAGAL; Claf Eye +390 (0,76x) GAGAL;
  Fossil Drawer +76 (0,34x) GAGAL; BEWORK +230 prev_rate None GAGAL.
- Scan leg FAST-FAIL: preflight Ankr 401 (13,1 dtk) - outage sejak 2026-11-09 ~13:33 WIB
  berlanjut; watermark tetap 132512564; 5c dilewati (tanpa output scan).
- EKSEKUSI TRACK-C LEAD DIRECT MINT 1: CHEEMSA (lihat bawah).
- Boltbook/feed triage: POTION SHOP + ONI-new = paid-only 0,0002 BNB (checked-not-lead);
  JagentMintV2/JAGENT = paid share sale, kuota habis; feed-f1b9 = bukan sale-shape.
- Agentic Gangster: free pool HABIS 111/111 (excluded run 1431, dilaporkan sekali) - hasil
  search hari ini basi (artikel 9 Nov); TIDAK dilaporkan ulang.
- AgentForge: excluded (14 hari, lewat 48 jam); Golden Agents: sudah di snapshot (early lead).
- binanceai.fun: TIDAK BERUBAH (launched 0, failed 1, refund 1, shares 3110, blok 132763122).
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1731"
BLOCK = 132762894
NOW = "2026-11-10 17:31 WIB"
INTERVAL = 30.0
NOW_DT = datetime.datetime(2026, 11, 10, 18, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
WIN_START = datetime.datetime(2026, 11, 10, 17, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1731-premerge")

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
        entry["intervalMinutes"] = INTERVAL
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1
print(f"contracts updated: {updated}")

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote1731_1110"] = text

def dyn_note(name, extra_txt=""):
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
    if fm is not None and cap and cap < 10**12:
        freetxt = f"; freeMinted {fm}/{cap} = {fm/cap*100:.1f}%"
    elif fc is not None and cap and cap < 10**12:
        freetxt = f"; freeClaimed {fc}/{cap} = {fc/cap*100:.1f}%"
    vtxt = "velocity LOLOS" if passes else "velocity GAGAL"
    return (f"Run 1731 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

note("Aura Agents", (dyn_note("Aura Agents") or "") +
     " Velocity LOLOS run ini (+35, 35,35x) TAPI TANPA promosi: status watchlist-only-not-early-2026-11-03 "
     "(di watchlist sejak 3 Nov, umur >>48 jam) + free% UNVERIFIED (free views None). Bukan strong lead, bukan kandidat, TIDAK preview/mint.")
note("THYRK", (dyn_note("THYRK") or "") +
     " Velocity LOLOS run ini (+63, 1,75x) TAPI TANPA promosi: sudah minted-by-user (#6849 run 1231, bal_user=1, slot gratis terpakai).")
note("SEVENFOLD", (dyn_note("SEVENFOLD") or "") +
     " Velocity GAGAL (+16 <20 token walau 1,78x). KANDIDAT tetap AUDIT-BLOCKED (token MORROW riskLevel 4 HIGH + RISK). TIDAK preview/mint.")
note("Claf Eye", (dyn_note("Claf Eye") or "") + " Velocity GAGAL (0,76x). Tetap early lead, tanpa promosi.")
note("Fossil Drawer", (dyn_note("Fossil Drawer") or "") + " Velocity GAGAL (0,34x). Sudah minted-by-user (#581 run 1631).")
note("BEWORK", (dyn_note("BEWORK") or "") + " +230 tapi prev_rate None (rate pertama) -> velocity TIDAK lolos.")
note("Golden Agents", (dyn_note("Golden Agents") or "") + " Tetap early lead; first mint terverifikasi 2026-11-09 ~02:00 WIB -> deadline 48 jam 2026-11-11 ~02:00 WIB.")
note("Sakura", (dyn_note("Sakura") or "") + " Tetap early lead; first mint terverifikasi 2026-11-10 01:47 WIB -> deadline 48 jam 2026-11-12 01:47 WIB.")
note("DRIFTWIRE", (dyn_note("DRIFTWIRE") or "") + " Sudah minted-by-user (#745 run 1231) -> tanpa relevansi.")

# ---- generic NEW-sellout detection (prev free < cap <= fresh free, status not terminal) ----
TERMINAL = ("sold-out", "soldout", "age-excluded", "excluded-", "minted-by-user")
new_sellouts = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name, {})
    cap = entry.get("FREE_SUPPLY") or entry.get("FREE_CAP") or entry.get("agentFreeCap")
    if not cap or cap >= 10**12:
        continue
    st = str(entry.get("status", ""))
    if any(t in st for t in TERMINAL):
        continue
    for key in ("freeMinted", "freeClaimed"):
        prev = entry.get(key)
        fresh = f.get(key)
        if prev is not None and fresh is not None and prev < cap <= fresh:
            new_sellouts.append((name, key, prev, fresh, cap))
            entry["status"] = "sold-out-free-pool-exhausted-2026-11-10"
            entry["runNote1731_1110"] = (f"Run 1731 (blok {BLOCK}): SELLOUT BARU - {key} {prev}->{fresh}/{cap} "
                f"(cap tercapai interval ini). Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali oleh parent.")
            break
print("NEW SELLOUTS:", new_sellouts if new_sellouts else "none")

# ---- age-exclusion scan: deadlines falling inside run 1701 -> 1731 window ----
def parse_wib(s):
    if not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S WIB", "%Y-%m-%dT%H:%M:%S+07:00", "%Y-%m-%d %H:%M WIB"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
        except Exception:
            continue
    return None
new_age_excl = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    st = str(entry.get("status", ""))
    if any(t in st for t in TERMINAL):
        continue
    launch = None
    for k in ("firstMintWib", "startTimeWib", "launchWib"):
        launch = parse_wib(entry.get(k))
        if launch:
            break
    if not launch:
        continue
    deadline = launch + datetime.timedelta(hours=48)
    if WIN_START < deadline <= NOW_DT:
        sold = False
        f = rr.get("reread", {}).get(name, {})
        cap = entry.get("FREE_SUPPLY") or entry.get("FREE_CAP")
        fm = f.get("freeMinted"); fc = f.get("freeClaimed")
        if cap and ((fm is not None and fm >= cap) or (fc is not None and fc >= cap)):
            sold = True
        entry["status"] = "age-excluded-2026-11-10"
        entry["runNote1731_1110"] = (f"Run 1731 (blok {BLOCK}): AGE-EXCLUDED - launch terverifikasi {launch}, "
            f"deadline 48 jam {deadline} lewat; soldOut={sold}. Status -> age-excluded-2026-11-10. Dilaporkan sekali oleh parent.")
        new_age_excl.append((name, str(launch), str(deadline), sold))
print("NEW AGE EXCLUSIONS:", new_age_excl if new_age_excl else "none")

# ---- track_c generic lastRead updates + free values ----
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("track_c", {}).get(name, {})
    if not f:
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW

# ---- CHEEMSA: TRACK-C LEAD DIRECT MINT run ini ----
tc = snap.get("track_c", {})
if isinstance(tc.get("Cheems Agent"), dict):
    ch = tc["Cheems Agent"]
    ch["status"] = "minted-by-user-2026-11-10"
    ch["freeMinted"] = 977
    ch["lastReadBlock"] = 132764194
    ch["lastReadWib"] = NOW
    ch["runNote1731_1110"] = (
        "Run 1731: TRACK-C LEAD DIRECT MINT - 1 share gratis -> 5.000.000 CHEEMSA. "
        "tx 0xbfc5a0482699ea2eae61954e81b03e7202df4966b7174b9dedaea3b90611d939, orderId 26111000002031382646, "
        "blok 132764116, receipt status 1, gas 125586. Verifikasi: balanceOf(user) 0 -> 5.000.000 CHEEMSA (5e24, "
        "= FREE_TOKENS_PER_SHARE x 1, cocok dengan preview); freeClaimedByWallet(user) 0 -> 1; totalFreeMinted 976 -> 977. "
        "Lead legs segar: S1 PASS + free pool 52 tersisa (948/1000, blok 132763329) + slot user terbuka + umur ~55 mnt (mintStart 17:00 WIB). "
        "GATE WEBSITE LOLOS (BERUBAH vs run 1631): https://cheemsagent.lol/ - bundle JS /assets/index-MFs41wVB.js mencetak "
        "VITE_CONTRACT_ADDRESS 0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2 persis + FREE_SHARES/claimFree/mintStart (metode D/G); "
        "judul 'Cheems Agent · $CHEEMSA', meta '持 Agent ID 铸造，每份 0.003 BNB'. Audit Binance segar run ini: hasResult=true, "
        "riskLevel 2 LOW, riskAlert null, 0 hit RISK (hanya CAUTION 'Newly Created Token'). Preview bersih requestId "
        "34007a4cc97049e4acb7a2b6e07e9ee6 (code 000000000, value 0, tanpa authority/allowance/risk, balance +5e24 tepat). "
        "Same-owner-discards: 0x00b4 TIDAK ada di 60 entri. Sesi baw login. Bukan NFT: cek marketplace/rarity TIDAK berlaku. "
        "Swap: pair PCS V2 0x0 (WBNB+USDT), tradingOpen()=false -> TIDAK bisa di-swap; 5.000.000 CHEEMSA didaftarkan "
        "pending-swaps.json entri ke-19 (no_pair).")

# ---- new checked entries (triage run 1731) ----
snap["contracts"]["POTION SHOP"] = {
    "address": "0x7f92593905facb51d9566520b4e6fa8c2997ab0c",
    "name": "POTION SHOP", "symbol": "POTION", "kind": "ERC721",
    "status": "checked-not-lead-2026-11-10",
    "totalSupply": 226, "MAX_SUPPLY": 1111, "mintOpen": 1,
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "note": "Boltbook front page run 1731 (post drhmwt.ai, mempool telemetry: 220/1111, +27 mints/11 mnt). "
            "Sourcify exact_match, ABI agentIds/mintWithAgentTokenId/mintedByAgent (agent-gated) TAPI price() = 0,0002 BNB, "
            "tanpa fungsi/view free-mint, tanpa referensi registry -> PAID-ONLY, bukan Free Bacot. Bukan lead, bukan kandidat, TIDAK preview/mint."}
snap["contracts"]["ONI-new"] = {
    "address": "0x852f80b92112f94342c4687f30fde2d849961daa",
    "name": "Oni", "symbol": "ONI", "kind": "ERC721",
    "status": "checked-not-lead-2026-11-10",
    "totalSupply": 795, "MAX_SUPPLY": 1620, "mintOpen": 1,
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "note": "Boltbook ZH front page run 1731 (post amarboon.ai: 793/1620, Sourcify exact_match). Kontrak BERBEDA dari ONI-d576 di snapshot. "
            "Template sama dengan POTION SHOP (ABI identik), price() = 0,0002 BNB, tanpa fungsi/view free-mint, tanpa referensi registry -> "
            "PAID-ONLY, bukan Free Bacot. Bukan lead, bukan kandidat, TIDAK preview/mint."}
snap["track_c"]["JagentMintV2"] = {
    "sale": "0x3643A907f875fA9B740e1C0747E91b5aA5222aB8",
    "token": "0x8e6442663A4F8C50b6132c68d42A30E7DFE4Ae15",
    "name": "Jager", "symbol": "JAGENT",
    "status": "checked-not-lead-2026-11-10",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "note": "Boltbook front page run 1731 (post ffridoy.ai: 'wallet 5 ran the same 10 rounds - 5.0 USDT in, 5.2164 out, quota now used up'). "
            "JagentMintV2: paid share-sale (mint USDT/BNB, quota/import, totalMinted 168967), tanpa free-share view; JAGENT token trading-enabled. "
            "Kuota habis per post + tidak ada jalur gratis terverifikasi -> PAID-ONLY, bukan track-C lead. Bukan lead, TIDAK preview/mint."}
snap["track_c"]["feed-f1b9"] = {
    "sale": "0xf1b9D0b2Fac297AAD0A9eA858Dea805A49a0140a",
    "status": "checked-not-sale-shape-2026-11-10",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "note": "Sourcify recently-verified feed run 1731 (verifiedAt 2026-11-10T10:42:48Z). Hanya 6 fungsi (UniswapV2/generateUSDT/restoreBNB/tokenName/"
            "tokenSymbol/withdrawUSDT) -> bukan mint/sale, bukan agent-shaped. Bukan lead."}
snap["contracts"]["bridge-0x636fdfa9"] = {
    "address": "0x636fdfa9bc3db42c690c09e87b9017d05b36c743",
    "status": "watchlist-only-pelengkap-scan-2026-11-10",
    "source": "scan",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "note": "Temuan pelengkap scan (scan-bridge.json): Unnamed ERC20, mint-pattern, 1 entity only - finding, NOT a signal/lead. "
            "Ditambahkan ke snapshot watchlist run 1731 (sumber scan); bukan NFT agent-mint, tidak memenuhi tier Free Bacot."}
snap["contracts"]["bridge-0xf75cf7f9"] = {
    "address": "0xf75cf7f9be878cf487d5aeacd5560d96737b63f8",
    "status": "watchlist-only-pelengkap-scan-2026-11-10",
    "source": "scan",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "note": "Temuan pelengkap scan (scan-bridge.json): ETHBack_Dividend_Tracker ERC20, mint-pattern, 1 entity only - finding, NOT a signal/lead. "
            "Ditambahkan ke snapshot watchlist run 1731 (sumber scan); bukan NFT agent-mint, tidak memenuhi tier Free Bacot."}

# ---- binanceai.fun: unchanged ----
if isinstance(snap.get("binanceai_claim"), dict):
    snap["binanceai_claim"]["verified_run"] = "2026-11-10 run 1731"
    snap["binanceai_claim"]["verified_wib"] = "2026-11-10 ~18:0x WIB"
    snap["binanceai_claim"]["block"] = 132763122
    snap["binanceai_claim"]["verify_method"] = ("binanceai re-read run 1731: launched 0, failed 1, isRefundPhase 1, "
        "totalShares 3110, tokenClaimed user 0, saldo TOKEN user 0 - TIDAK BERUBAH vs run 1701. Status tetap closed-refund-phase-2026-11-07, TIDAK dilaporkan ulang.")

# ---- top-level run note ----
snap["runNote1731_1110"] = (
    "Run 1731 (2026-11-10 17:31-~18:15 WIB, blok re-read 132762894): re-read 661 kontrak + 79 track_c (563,6 dtk). "
    "Velocity LOLOS 2 (Aura Agents +35 35,35x; THYRK +63 1,75x) - TANPA promosi (Aura umur >>48 jam + free% UNVERIFIED; THYRK sudah minted-by-user). "
    "SEVENFOLD +16 GAGAL (<20); Claf Eye +390 GAGAL (0,76x); Fossil Drawer +76 GAGAL; BEWORK +230 prev_rate None GAGAL. "
    "EKSEKUSI TRACK-C LEAD DIRECT MINT 1: CHEEMSA - 1 share gratis -> 5.000.000 CHEEMSA, tx 0xbfc5a0482699ea2eae61954e81b03e7202df4966b7174b9dedaea3b90611d939, "
    "blok 132764116, receipt 1, gas 125586 (gate website LOLOS via cheemsagent.lol bundle; audit LOW 0 RISK; preview bersih; pool 948/1000 saat eksekusi). "
    "Scan leg FAST-FAIL (preflight Ankr 401, 13,1 dtk; outage berlanjut; watermark tetap 132512564). "
    "Boltbook/feed triage: POTION SHOP + ONI-new paid-only 0,0002 BNB; JagentMintV2 paid/quota habis; feed-f1b9 bukan sale-shape. "
    "Agentic Gangster free pool HABIS (excluded run 1431) - hasil search basi, tidak dilaporkan ulang. "
    "binanceai.fun TIDAK BERUBAH (refund phase). Bridge: 2 ERC20 ditambahkan ke snapshot watchlist (pelengkap scan); file bridge tidak berubah sejak 2026-11-08.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = snap["runNote1731_1110"]

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
