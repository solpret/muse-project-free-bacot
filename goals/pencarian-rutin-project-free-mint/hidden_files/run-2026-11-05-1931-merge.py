#!/usr/bin/env python3
"""Run 1931 parent snapshot/state merge (bookkeeping only, no chain writes).
Backs up snapshot/seen/state first. Null reads never overwrite old values.
Velocity: interval from each entry's own lastReadBlock (0.45 s/block);
ratio vs stored currentRatePerMin (fallback previousRatePerMin); prev rate 0
means first baseline -> velocity does NOT pass."""
import json, shutil, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "1931"
READ_BLOCK = 131821320
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

for f in ["onchain-snapshot.json", "onchain-scan-seen.json", "onchain-scan-state.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f.replace('.json', '')}-{RUN}.bak.json")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-05-{RUN}-reread-lean.json"))
njar = json.load(open(f"{BASE}/run-2026-11-05-{RUN}-njar-probe.json"))
asoc = json.load(open(f"{BASE}/run-2026-11-05-{RUN}-asoc-probe.json"))
probes = json.load(open(f"{BASE}/run-2026-11-05-{RUN}-probes.json"))
fs = json.load(open(f"{BASE}/run-2026-11-05-{RUN}-scan-firstseen.json"))
recon = json.load(open(f"{BASE}/run-2026-11-05-{RUN}-mossminds-reconcile.json"))
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-05-{RUN}.json"))

by_addr = {e.get("address", "").lower(): (n, e) for n, e in snap["contracts"].items()}
tc_by_sale = {v.get("sale", "").lower(): (k, v) for k, v in snap.get("track_c", {}).items()
              if isinstance(v, dict) and v.get("sale")}
changes = []

# ---------- Route 1: lean re-read merge (NFT, by address) ----------
for name, d in rr.get("reread", {}).items():
    addr = (d.get("address") or "").lower()
    hit = by_addr.get(addr)
    if not hit:
        changes.append(f"ORPHAN-READ {name} {d.get('address')} (not in snapshot contracts; skipped)")
        continue
    key, e = hit
    prev_sup = e.get("totalSupply")
    prev_minted = e.get("totalMinted")
    cur_sup = d.get("totalSupply")
    cur_minted = d.get("totalMinted")
    got_any = False
    for lk, sk in [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted"),
                   ("freeClaimed", "freeClaimed"), ("freeMinted", "freeMinted")]:
        if isinstance(d.get(lk), int):
            e[sk] = d[lk]; got_any = True
    if isinstance(d.get("balanceOf_user"), int):
        e["balanceOf_user"] = d["balanceOf_user"]; e["userBalance"] = d["balanceOf_user"]; got_any = True
    for lk, sk in [("costOf_user_1", "costOf_user_1"), ("mintsLeft_user", "mintsLeft_user"),
                   ("mintOpen", "mintOpen"), ("price", "price"),
                   ("canFreeMint_user", "canFreeMint_user"),
                   ("claimedFree_user", "claimedFree_user")]:
        if d.get(lk) is not None:
            e[sk] = d[lk]; got_any = True
    if isinstance(d.get("mintedBy_user"), int):
        e["mintedBy_user"] = d["mintedBy_user"]; e["userMintedBy"] = d["mintedBy_user"]; got_any = True
    if isinstance(d.get("freeUsed_user"), int):
        e["freeUsed_user"] = d["freeUsed_user"]; e["userFreeUsed"] = d["freeUsed_user"]; got_any = True
    if isinstance(d.get("quote_user_1"), int):
        e["quoteUser1"] = d["quote_user_1"]; got_any = True
    if not got_any:
        changes.append(f"NULL-READ {key}: all views null, old values kept")
        continue
    # free % recompute (only when a real free counter + cap exist)
    free = e.get("freeClaimed") if isinstance(e.get("freeClaimed"), int) else e.get("freeMinted")
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP")
    if isinstance(free, int) and isinstance(cap, int) and cap:
        e["freePctVerified"] = round(100 * free / cap, 2)
    # velocity
    prev_block = e.get("lastReadBlock")
    delta = None; view = None
    if isinstance(cur_sup, int) and isinstance(prev_sup, int):
        delta, view = cur_sup - prev_sup, "totalSupply"
    elif isinstance(cur_minted, int) and isinstance(prev_minted, int):
        delta, view = cur_minted - prev_minted, "totalMinted"
    if delta is not None and isinstance(prev_block, int) and READ_BLOCK > prev_block:
        interval_min = (READ_BLOCK - prev_block) * 0.45 / 60
        prev_rate = e.get("currentRatePerMin")
        if not isinstance(prev_rate, (int, float)):
            prev_rate = e.get("previousRatePerMin", 0) or 0
        rate = delta / interval_min if interval_min else 0
        ratio = (rate / prev_rate) if prev_rate else None
        passes = bool(ratio is not None and ratio >= 1.5 and delta >= 20)
        e["previousTotalSupply"] = prev_sup if view == "totalSupply" else prev_minted
        e["mintedInInterval"] = delta
        e["intervalMinutes"] = round(interval_min, 1)
        e["previousRatePerMin"] = prev_rate
        e["currentRatePerMin"] = round(rate, 3)
        e["velocityLegPasses"] = passes
        rtxt = f"{ratio:.2f}x" if ratio is not None else "None (rate sebelumnya 0, baseline pertama)"
        e[f"velocityNote{RUN}"] = (f"Run {RUN} (blok {READ_BLOCK}): {prev_sup if view=='totalSupply' else prev_minted}->"
            f"{cur_sup if view=='totalSupply' else cur_minted} (+{delta}) dalam {interval_min:.1f} mnt = "
            f"{rate:.3f}/mnt vs prev {prev_rate:.3f} = {rtxt} -> velocity {'LOLOS' if passes else 'GAGAL'}.")
        if passes:
            changes.append(f"VELOCITY-PASS {key}: +{delta} {rate:.2f}/mnt ratio {ratio:.2f}x (tetap dicek kaki lain)")
    e["lastReadBlock"] = READ_BLOCK
    e["lastReadWib"] = f"2026-11-05 run {RUN}"

# ---------- Route 1: track-C lean re-read merge (by sale address) ----------
for key, d in rr.get("track_c", {}).items():
    sale = (d.get("sale") or "").lower()
    hit = tc_by_sale.get(sale)
    if not hit:
        changes.append(f"ORPHAN-TC {key} {d.get('sale')} (not in track_c; skipped)")
        continue
    tk, te = hit
    if tk == "ASOC-43cE":
        continue  # removed below (free pool exhausted)
    for lk in ["opened", "launched", "freeMinted", "freeSharesRemaining", "totalMinted",
               "sharesMinted", "saleEnded", "phase"]:
        if d.get(lk) is not None:
            te[lk] = d[lk]
    te["lastReadBlock"] = READ_BLOCK
    te["lastReadWib"] = f"2026-11-05 run {RUN}"

# ---------- New early leads ----------
snap["contracts"]["Mossminds"] = {
    "address": "0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a", "name": "Mossminds", "symbol": "MOSS",
    "kind": "ERC721", "status": "early-lead-reported-2026-11-05",
    "totalSupply": 225, "freeMinted": 225, "paidMinted": 0, "FREE_CAP": 2880, "MAX_SUPPLY": 4000,
    "freePctVerified": 7.81, "PRICE": 500000000000000, "mintOpen": True,
    "userBalance": 0, "canFreeMint_user": 1, "claimedFree_user": 0,
    "userSlotNote": "Slot OPEN: canFreeMint(user)=1, claimedFree(user)=0 (parent fresh read run 1931; B batch-1 block 131821663: freeMinted 20, totalSupply 23).",
    "firstSeenBlock": 131821105, "firstMintWib": "2026-11-05T20:00:41+07:00",
    "lastReadWib": "2026-11-05 run 1931",
    "launchNote": "First mint TERVERIFIKASI on-chain: blok 131821105 = 2026-11-05 20:00:41 WIB (Ankr getLogs, subagent B + subagent A sepakat; tx 0x196898870e5af6147bd199ff8603ff6fe09e4f5f1de42c804956f59f20624120). Umur TERVERIFIKASI <=48 jam.",
    "ageCorrectionNote": "KOREKSI parent run 1931 atas verdict age-UNVERIFIED subagent A: parent re-check Ankr (131821105-131822500) menemukan 74 log Transfer-from-zero tokenId 3-76 + A menemukan tokenId 1,2,3 di 131821105-131821278 -> tokenId 1-76 berurutan SEMUA punya event mint di 131821105-131822495. Anomali A (ownerOf 4-15 tanpa event) adalah artefak jendela pencarian A yang berhenti di blok 131821278 sementara mint 4-15 terjadi sesudahnya. Umur TERVERIFIKASI, bukan unverified.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1931 (Sourcify feed-new, verifiedAt 2026-11-05T13:01:02Z). Agent-shaped: REGISTRY()=registry on-chain + freeMint() + FREE_CAP 2880. Free 225/2880=7,81% (bergerak cepat: 20 di blok 131821663 -> 225 di baca parent) - jauh di bawah 25% strong leg. X/website/velocity NOT checked. NEVER preview/mint as early lead. Caveat: freeMinted vs totalSupply selisih 3 di awal (mintRef path, dicatat B); game/jackpot elements di ABI (tierOf/svgOf), dicatat bukan diskualifikasi tier early.",
    "supplyView": "totalSupply", "velocityLegPasses": False, "xVerified": False,
}
snap["contracts"]["BNB CACHE Server"] = {
    "address": "0x1989058Da9eb7F36E69779fCda0EA04578528570", "name": "BNB CACHE Server", "symbol": "SERVER",
    "kind": "ERC721", "status": "early-lead-reported-2026-11-05",
    "totalSupply": 71, "totalServersMinted": 71, "TOTAL_SERVERS": 1554,
    "freeServersClaimed": 71, "freeServersRemaining": 706, "FREE_SERVERS_TOTAL": 777,
    "freePctVerified": 9.14, "SERVER_PRICE": 1000000000000000, "paidServersRemaining": 777,
    "paidServersSold": 0, "freeWindowOpen": 1,
    "freeWindowClosesAt": 1793970003, "freeWindowClosesWib": "2026-11-06T20:00:03+07:00",
    "gateStart": 1793883603, "userBalance": 0, "freeClaimedBy_user": 0,
    "userSlotNote": "Slot OPEN: freeClaimedBy(user)=0 (baca subagent A, blok ~131824142).",
    "firstSeenBlock": 131821028, "firstMintWib": "2026-11-05T20:00:06+07:00",
    "lastReadWib": "2026-11-05 run 1931",
    "launchNote": "First mint TERVERIFIKASI on-chain: blok 131821028 = 2026-11-05 20:00:06 WIB (3 detik setelah gateStart 20:00:03 WIB); 71 mint logs = totalServersMinted 71 persis. Umur TERVERIFIKASI <=48 jam.",
    "minterOverlapFlag": "2 dari 7 minter window scan juga mint Mossminds di window yang sama (0x61d5353152b2573786bf640e289a12e00c7c3df1, 0x86a49a9e391c5dc143d2d8b2e8bb77e8bb61ede9) - kemungkinan factory-wave / operator sama; dicatat, bukan diskualifikasi tier early.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1931 (scan rute 4 first-seen, window 131819316-131821315). Agent-shaped: registry() on-chain + claimFreeServer + free views. Free 71/777=9,14% - di bawah 25% strong leg. X/website/velocity NOT checked. NEVER preview/mint as early lead. Promosi ke strong hanya bila free >=25% + umur tetap terverifikasi + slot tetap terbuka. Free window tutup 2026-11-06 20:00:03 WIB.",
    "supplyView": "totalServersMinted", "velocityLegPasses": False, "xVerified": False,
}

# ---------- Watchlist-only paid-only first-seen ----------
snap["contracts"]["Aether Core"] = {
    "address": "0xe460d44d4A5eb9BEF848C0815d689827f6890D59", "name": "Aether Core", "symbol": "ATC",
    "kind": "ERC721", "status": "watchlist-only-2026-11-05", "totalSupply": 3333, "totalMinted": 1,
    "MAX_SUPPLY": 3333, "spotsLeft": 3332, "PRICE": 500000000000000, "quote_user_1": 500000000000000,
    "userBalance": 0, "userMintedBy": 0, "firstSeenBlock": 131821143,
    "firstMintWib": "2026-11-05T20:00:58+07:00", "lastReadWib": "2026-11-05 run 1931",
    "note": "Watchlist-only run 1931 (Sourcify feed-new + scan first-seen). Agent-shaped (AGENT_REGISTRY()=registry on-chain) TAPI paid-only: tanpa fungsi free-mint/free view, PRICE/quote 0,0005 BNB, 1 mint ever oleh owner/treasury 0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5 (grup deployer sama dengan Ember Byte). Pola supply=max + 1-mint-ever (totalSupply baca MAX, bukan jumlah mint). tokenURI(1)=ipfs://sniper-test-nft/1. Bukan early lead, tidak dilaporkan sebagai lead.",
}
snap["contracts"]["Ember Byte"] = {
    "address": "0xeC8A897a0De48a6fbfb83646f790581a2280aDB3", "name": "Ember Byte", "symbol": "EMBB",
    "kind": "ERC20", "status": "watchlist-only-2026-11-05", "totalSupply": 1000000000000000000000000000,
    "MAX_SPOTS": 5000, "PER_SPOT": 200000, "PRICE": 1000000000000000, "spotsLeft": 4999,
    "totalSpotsMinted": 1, "quote_user_1": 1000000000000000, "userBalance": 0, "userMintedBy": 0,
    "firstSeenBlock": 131821186, "firstMintWib": "2026-11-05T20:01:17+07:00",
    "lastReadWib": "2026-11-05 run 1931",
    "website": "https://agenticspace.xyz",
    "websiteNote": "WEBSITE()=https://agenticspace.xyz TAPI situs hanya stub redirect JS 114 byte (window.location.href='/lander'), tanpa alamat kontrak/konten - BUKAN website evidence. TWITTER()=@agenticspaceBnb.",
    "note": "Watchlist-only run 1931 (Sourcify feed-new + scan first-seen). BUKAN track-C lead: tanpa free-share view (gagal kaki free S1), tanpa fungsi free, quote(1)=0,001 BNB paid. Spot sale berbayar 0,001 BNB/spot, 1 spot terjual. Grup deployer sama 0xe9d9dec3... dengan Aether Core. Bukan early lead, tidak dilaporkan sebagai lead.",
}
snap["contracts"]["Nebula Mole Agent"] = {
    "address": "0xA5e2653b0CB5c25E2A1c2F12a574B0810636A72A", "name": "Nebula Mole Agent",
    "kind": "ERC721", "status": "watchlist-only-2026-11-05", "firstSeenBlock": None,
    "lastReadWib": "2026-11-05 run 1931",
    "note": "Watchlist-only run 1931 (scan first-seen). AGENT_REGISTRY() cocok on-chain TAPI tanpa fungsi free-mint/free view - paid-only, template sama dengan Aether Core/Onyx Rat. Bukan early lead, tidak dilaporkan sebagai lead.",
}
snap["contracts"]["Onyx Rat Agent"] = {
    "address": "0xDc488baF376AB123Ce189747eF434fdFe3918342", "name": "Onyx Rat Agent",
    "kind": "ERC721", "status": "watchlist-only-2026-11-05", "firstSeenBlock": None,
    "lastReadWib": "2026-11-05 run 1931",
    "note": "Watchlist-only run 1931 (scan first-seen). AGENT_REGISTRY() cocok on-chain TAPI tanpa fungsi free-mint/free view - paid-only, template sama dengan Aether Core/Nebula Mole. Bukan early lead, tidak dilaporkan sebagai lead.",
}
changes.append("ADD Mossminds (early lead, age VERIFIED per parent reconciliation) + BNB CACHE Server (early lead)")
changes.append("ADD watchlist-only: Aether Core, Ember Byte, Nebula Mole Agent, Onyx Rat Agent (paid-only)")

# ---------- AgentGlyph: fresh numbers + gate deepening ----------
g = snap["contracts"].get("AgentGlyph")
if g:
    g["totalSupply"] = 319; g["freeClaimed"] = 319; g["freePctVerified"] = 62.3
    g["lastReadBlock"] = READ_BLOCK; g["lastReadWib"] = f"2026-11-05 run {RUN}"
    g["runNote1931"] = ("Run 1931 (blok 131821320): totalSupply/freeClaimed 273->319 (62,3%), slot TERBUKA "
        "(quote 0, mintedBy 0, freeUsed 0, balance 0); velocity baseline pertama (rate sebelumnya 0) -> TIDAK lulus run ini. "
        "Gate website TETAP GAGAL: (A) address search nihil (run 1901); (G) name search hanya hasil tak terkait (run 1931); "
        "(J) ABI tanpa fungsi site/url; (I) tokenURI base64 tanpa URL; (K) GitHub search-index tanpa repo (limitasi: true code search butuh auth); "
        "(M) site: filters tanpa hasil (run 1931); (L) BscScan token page TERHALANG Cloudflare bot wall (browser task 20:03-20:04 WIB, Ray a55c0ff4bedb760a) - bukan bukti ketiadaan; "
        "(E) owner() 0x1f3301bf46b8e85d5e4a1984e05faa8084ae8e5d - grup baru, BUKAN grup discard a054/d76d. Status tetap strong-lead-gate-blocked; TIDAK di-preview/di-mint; TIDAK dilaporkan ulang (sudah dilaporkan sekali run 1901).")

# ---------- Glitchpilotfox / Forklings / LIMITLESS notes ----------
gl = snap["contracts"].get("Glitchpilotfox")
if gl:
    gl["totalSupply"] = 846; gl["freeClaimed"] = 835; gl["freePctVerified"] = 20.9
    gl["runNote1931"] = ("Run 1931: Boltbook recheck (cskh.ai 840/4.000; wawanmol13.ai 846/4.000, freeClaimed 835) -> "
        "free 835/4.000=20,9% - MASIH di bawah 25% strong leg; tidak ada promosi. Rute 1 tidak membaca ulang (tidak ada di daftar lean).")
fk = snap["contracts"].get("Forklings")
if fk:
    fk["runNote1931"] = ("Run 1931 (blok 131821320): totalSupply 627->660 (+33, 0,87/mnt vs 1,000 = 0,87x) -> velocity GAGAL; "
        "free 33,0% (freeMinted 660/2.000); umur terverifikasi; slot terbuka. Status tetap strong-lead-gate-blocked (website gagal); tidak ada promosi.")
lim = snap["contracts"].get("LIMITLESS-c7aa")
if lim:
    lim["totalSupply"] = 4322
    lim["runNote1931"] = ("Run 1931 (blok 131821320): totalSupply 4151->4322 (+171); rate sebelumnya 0 -> velocity TIDAK dihitung "
        "(baseline pertama). Boltbook author-page (nanomind.ai): klaim free lane berakhir di 6.000 bukan 10.000, paling banyak 1.724 free tersisa - "
        "klaim poster, TIDAK terverifikasi on-chain (free views revert). Tetap watchlist-only-boltbookfun; bukan lead, tidak dipromosikan.")

# ---------- NJAR track-C update ----------
nj = snap.get("track_c", {}).get("NJAR")
if isinstance(nj, dict):
    nj["giftsClaimed"] = njar.get("giftsClaimed"); nj["GIFT_SHARES"] = njar.get("GIFT_SHARES")
    nj["live"] = njar.get("live"); nj["paidSharesSold"] = njar.get("paidSharesSold")
    nj["giftsLeft"] = (njar.get("GIFT_SHARES") or 2000) - (njar.get("giftsClaimed") or 0)
    nj["lastReadBlock"] = njar.get("block"); nj["lastReadWib"] = f"2026-11-05 run {RUN}"
    nj["runNote1931"] = ("Run 1931 (blok 131821398): giftsClaimed 446->468/2.000 (1.532 tersisa), live=1, paidSharesSold 3, "
        "gift user MASIH TERBUKA (giftTaken=0, hasAgent=1). Gate website TETAP GAGAL: metode A+G diulang subagent B (route 3 Q4/Q5) - hanya hasil tak terkait; "
        "H/I null run 1901. TIDAK di-preview/di-mint; tidak dilaporkan ulang (sudah gate-blocked, dilaporkan sekali sebelumnya).")

# ---------- QAGENT-2 / SENBAZURU / IMARS / DROID / Ikigai / SAFUAI / OSK / NIULAI (lean values already merged) ----------
# ---------- Pumpkinagent: age-exclusion ----------
pk = snap["contracts"].pop("Pumpkinagent", None)
if pk:
    snap.setdefault("excluded", {})["Pumpkinagent"] = dict(pk)
    snap["excluded"]["Pumpkinagent"].update({
        "status": "excluded-age-over-48h-2026-11-05", "track": "A",
        "note": ("Age-excluded run 1931: first mint 2026-11-03T19:34:09+07:00 -> 48 jam lewat 2026-11-05 19:34:09 WIB; "
                 "baca segar run 1931 blok 131821320: totalSupply 931 (flat vs run 1901), freeClaimed 926/2222 = 41,7%, belum sold out. "
                 "Status sebelumnya strong-lead-gate-blocked-2026-11-03. Dihapus dari watchlist aktif; dilaporkan sekali sebagai perubahan run ini."),
        "removed_wib": "2026-11-05 run 1931"})
    changes.append("AGE-EXCLUDE Pumpkinagent (first mint 2026-11-03 19:34:09 WIB, >48h, 931 supply, free 41,7%, belum sold out)")

# ---------- ASOC-43cE: free pool exhausted -> remove from track_c ----------
asoc_e = snap.get("track_c", {}).pop("ASOC-43cE", None)
if asoc_e:
    snap.setdefault("excluded", {})["ASOC-43cE"] = dict(asoc_e)
    snap["excluded"]["ASOC-43cE"].update({
        "status": "excluded-free-pool-exhausted-2026-11-05", "track": "C",
        "freeUsed": asoc.get("freeUsed"), "FREE_QUOTA": asoc.get("FREE_QUOTA"),
        "totalSold": asoc.get("totalSold"), "TOTAL_SHARES": asoc.get("TOTAL_SHARES"),
        "note": ("Free pool HABIS run 1931: freeUsed 555/555 = FREE_QUOTA (probe parent blok 131822822; subagent B blok 131821663: freeUsed 555/555, totalSold 599), "
                 "totalSold 620 saat probe parent, saleEnded=0, freeClaimed(user)=0 (user tidak dapat free share - lane habis ~30-60 detik setelah buka 20:00 WIB). "
                 "Bentuk S1-INCOMPLETE (tanpa quote) - tidak pernah jadi lead. Dihapus dari track_c; dilaporkan sekali sebagai perubahan run ini."),
        "removed_wib": "2026-11-05 run 1931"})
    changes.append("ASOC free pool HABIS (freeUsed 555/555, totalSold 620) -> hapus dari track_c")

# ---------- Run notes ----------
snap["runNote1931"] = (
    "Run 1931 (2026-11-05 ~19:58-20:50 WIB): 2 EARLY LEAD BARU dilaporkan sekali (Mossminds - umur TERVERIFIKASI per rekonsiliasi parent; "
    "BNB CACHE Server - launch terverifikasi 20:00:03 WIB). 2 PERUBAHAN dilaporkan sekali (ASOC free pool habis 555/555; Pumpkinagent age-excluded >48h). "
    "0 kandidat track-A baru, 0 strong lead baru/promosi, 0 lead/kandidat track-C baru, 0 pending claim baru/dibuka (pending_claims kosong; BINANCEAI tetap refund/failed). "
    "AgentGlyph tetap strong-lead-gate-blocked (free 62,3%, slot terbuka; website GAGAL A/G/J/I/K/M, L terhalang Cloudflare). "
    "Velocity LOLOS: BNBRunnerz (2,43x), Blobbies (4,47x), PixelLaptop (1,69x), Kitebots (1,63x) - TIDAK ADA yang promosi (umur/% gratis unverified atau % <25%). "
    "NJAR gate tetap GAGAL (giftsClaimed 468/2.000, gift user terbuka). QAGENT free pool tetap habis 6666/6666. "
    "Bridge: scan-bridge.json TIDAK BERUBAH (113 kontrak, 7 same_owner_discarded, mtime 2026-11-04 17:40) - tidak ada temuan pelengkap scan baru. "
    "Scan rute 4 SUKSES: window 131819316-131821315 (cap 2000, gap 131816307-131819315 dilewati, 80 panggilan Ankr, 0 error); 5c: 11 ERC-20 baru dicek, 0 sale-shaped, 571 sampling-dropped (<10).")
snap["runNote1931_scan"] = (
    "Scan run 1931: window 131819316-131821315 (2000 blok, cap); watermark 131816306->131821315; "
    "gap 131816307-131819315 (3009 blok) dilewati (head maju ~2 blok/detik, cap 2000 tertinggal tiap run; kumulatif gap tak ter-scan sejak run 1831 ~13.671 blok - dicatat, tanpa aksi). "
    "80 panggilan Ankr, 0 error, ~18 mnt; 280 NFT/645 ERC-20. First-seen sejati 13 NFT + 345 ERC-20. "
    "Early lead 2 (BNB CACHE Server, Mossminds); watchlist-only 4 (Aether Core, Ember Byte, Nebula Mole, Onyx Rat - paid-only); bukan lead 7 (ARK100, MORPHA, Agent Cadets, IAO MINING, Phoenix, Still Lagoon, RAGENT AI Genesis, Parking Rush Cars). "
    "5c: 74 ERC-20 mint>=10, 63 sudah dicek, 11 baru dicek, 0 sale-shaped, 571 sampling-dropped. Feed sale-shape: 1 hit Mossminds (NFT track A, bukan track-C).")
snap["last_run"] = "1931"
snap["last_run_wib"] = "2026-11-05 run 1931"
snap["timestamp_wib"] = "2026-11-05 run 1931 (final)"

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)

# ---------- Seen file: +13 NFT +345 ERC-20 ----------
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
added_nft = added_erc = 0
for e in fs.get("nft_first_seen", []):
    a = e["address"].lower()
    if a not in seen["contracts"]:
        seen["contracts"][a] = e["first_block"]; added_nft += 1
for e in fs.get("erc20_first_seen", []):
    a = e["address"].lower()
    if a not in seen["contracts"]:
        seen["contracts"][a] = e["first_block"]; added_erc += 1
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

# ---------- Scan state ----------
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
state.update({
    "last_scanned_block": scan.get("to_block", 131821315),
    "last_scan_window_from": scan.get("from_block", 131819316),
    "last_scan_window_to": scan.get("to_block", 131821315),
    "last_scan_wib": "2026-11-05 run 1931",
    "ankr_calls": scan.get("ankr_calls", 80),
    "errors": scan.get("errors", []),
    "nft_contracts": 280, "erc20_mint_contracts": 645,
    "skipped_gap": "131816307-131819315 (3009 blok, window dari watermark 131816306 ke head 131821315 = 5009 blok > cap 2000; scan menutup 2000 blok terbaru 131819316-131821315)",
    "note": ("Scan run 1931 SUKSES (80 panggilan Ankr, 0 error, ~18 menit, 20:02-20:20 WIB). Window 5009 blok > cap 2000, "
             "gap 131816307-131819315 (3009 blok) dilewati. First-seen sejati 13 NFT + 345 ERC-20 "
             "(2 early lead: BNB CACHE Server, Mossminds; 4 watchlist-only paid-only)."),
    "last_scan_window": "131819316-131821315",
    "ankr_calls_last_scan": 80, "errors_last_scan": [],
    "scan_started_wib": "2026-11-05 20:02", "scan_finished_wib": "2026-11-05 20:20",
    "head_at_scan_start": 131821278,
})
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)

print("contracts now:", len(snap["contracts"]), "| excluded:", len(snap.get("excluded", {})),
      "| track_c:", len(snap.get("track_c", {})), "| seen contracts:", len(seen["contracts"]))
print("seen added: NFT", added_nft, "ERC20", added_erc)
print("CHANGES:")
for c in changes:
    print(" -", c)
