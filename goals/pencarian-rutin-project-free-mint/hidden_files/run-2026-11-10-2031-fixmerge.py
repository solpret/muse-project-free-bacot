#!/usr/bin/env python3
"""Fix run 2031 merge: the copied 2001 merge.py contained hardcoded 2001 values
(Lanternfield 58/59, per-contract note suffixes, top-level run notes) that
overwrote fresh 2031 readings. Restore 2031 readings from reread/vel/target/probe.
Read-only except onchain-snapshot.json (backup first)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-2031"
BLOCK = 132785256
NOW = "2026-11-10 20:31 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
probe = json.load(open(f"{BASE}/run-{TS}-probe.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2031-fixmerge")

def dyn(name):
    row = vel.get("rows", {}).get(name, {})
    f = rr.get("reread", {}).get(name, {})
    e = snap["contracts"].get(name, {})
    minted, rate, ratio, passes = row.get("minted"), row.get("rate"), row.get("ratio"), row.get("passes")
    fm, fc = f.get("freeMinted"), f.get("freeClaimed")
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP") or e.get("agentFreeCap") or e.get("MAX_SUPPLY")
    freetxt = ""
    if fm is not None and cap and cap < 10**12:
        freetxt = f"; freeMinted {fm}/{cap} = {fm/cap*100:.1f}%"
    elif fc is not None and cap and cap < 10**12:
        freetxt = f"; freeClaimed {fc}/{cap} = {fc/cap*100:.1f}%"
    vtxt = "velocity LOLOS" if passes else "velocity GAGAL"
    return (f"Run 2031 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.")

# ---- Lanternfield: restore 2031 readings (was clobbered to 2001 values 58/59) ----
lf = snap["contracts"]["Lanternfield"]
lf.update({
    "totalSupply": 251, "totalMinted": 251, "freeMinted": 251,
    "freeRemaining": 1249, "freePctVerified": 16.7,
    "previousTotalSupply": 58, "mintedInInterval": 193, "intervalMinutes": 30.0,
    "currentRatePerMin": 6.433, "velocityRatio": None, "velocityLegPasses": False,
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "canFreeMint_user": 1, "freeAvailable_user": 1, "hasAgentId_user": 1,
    "freeRemainingFor_user": 1, "freeMintedBy_user": 0,
    "launchNote": ("Umur TERVERIFIKASI <24 jam: saleStart() on-chain 1794315653 = "
                   "2026-11-10 20:00:53 WIB; totalMinted 58 (run 2001) -> 251 (run 2031, +193)."),
    "baselineNote": ("EARLY lead dilaporkan sekali run 2001 (temuan feed Sourcify "
                     "recently-verified + shape-check S1+S2 PASS), BUKAN run 2031. Agent-shaped: "
                     "AGENT_ID_REGISTRY() = agentIdRegistry() = 0x60B926...22F persis; "
                     "hasAgentId(user)=1; freeMint/mintFree/mintPaid/quote/cost; Sourcify exact_match "
                     "(98 fns). Free 251/1500 = 16,7% run 2031 (<25% strong lead, <50% kandidat). "
                     "Website BELUM TERVERIFIKASI (method H: contractURI external_link "
                     "lanternfield.surge.sh ADA tapi situs mengembalikan placeholder Surge 404 dan "
                     "TIDAK mencetak kontrak). Slot user TERBUKA + GRATIS: canFreeMint=1, "
                     "freeMintedBy=0, freeAvailable=1, hasAgentId=1, freeRemainingFor=1, balanceOf=0. "
                     "X discussion UNVERIFIED. Velocity: ratio None (baseline rate pertama run 2001 "
                     "belum tersimpan), TIDAK lolos run ini. owner() = 0x0 (ownerless). TIDAK ada di "
                     "same-owner-discards.json. TIDAK pernah di-preview/di-mint (early lead). "
                     "KOREKSI run 2031: merge sempat menyalin blok hardcoded run 2001 (58/59) - "
                     "diperbaiki ke bacaan 2031 di fixmerge ini."),
})
lf["runNote2031_1110"] = (
    "Run 2031: Lanternfield re-read: totalSupply/totalMinted/freeMinted 251/1500 = 16,7% "
    "(+193 interval ini, 6,433/mnt); saleStart 20:00:53 WIB, umur <24 jam; slot user terbuka "
    "(canFreeMint=1, freeAvailable=1); website UNVERIFIED; X UNVERIFIED; velocity GAGAL "
    "(ratio None). Tetap early lead (dilaporkan sekali run 2001), bukan strong lead/kandidat. "
    "TIDAK di-preview/di-mint.")

# ---- per-contract notes with 2031 suffixes ----
notes = {
    "Agentic": dyn("Agentic") + (" Velocity GAGAL run ini (+13, 0,65x). freeMinted 940/1000 "
        "terbaca run ini; CATATAN: snapshot menyimpan freePctVerified 18,9% dari run lama - "
        "tidak konsisten dengan freeMinted/FREE_SUPPLY ini, ditandai inkonsisten dan TIDAK dipakai "
        "untuk promosi. Status strong-lead-gate-failed-2026-11-09 (website gate GAGAL, tidak ada "
        "website terverifikasi) + X UNVERIFIED. Tetap gate-failed, bukan kandidat, TIDAK dieksekusi."),
    "Claf Eye": dyn("Claf Eye") + (" Velocity GAGAL run ini (+62, 0,59x). Umur + free% UNVERIFIED "
        "(free views null) + X UNVERIFIED. Tetap early lead."),
    "BYTEBLOOM": dyn("BYTEBLOOM") + (" Early lead run 1931. Targeted read blok 132785465: status "
        "(400 minted, 0 paid, 400 agentFree, 0 xFree); freeLeft agent 1600/2000 -> agentFree "
        "400/2000 = 20,0% (<25% strong lead). Velocity GAGAL run ini (+104, 0,68x). Website "
        "TERVERIFIKASI; slot user terbuka. Tetap early lead; re-read prioritas run berikut."),
    "KERNELMONK": dyn("KERNELMONK") + (" Early lead run 1931. Targeted read blok 132785475: status "
        "(462 minted, 0 paid, 462 agentFree, 0 xFree); freeLeft agent 1538/2000 -> agentFree "
        "462/2000 = 23,1% (<25% strong lead, mendekati ambang). Velocity GAGAL run ini (+93, "
        "0,74x). Website TERVERIFIKASI; slot user terbuka. Tetap early lead; re-read prioritas "
        "run berikut."),
    "STALL": dyn("STALL") + (" Early lead run 1901: +99 interval ini, velocity GAGAL (1,22x). "
        "Free% + umur UNVERIFIED. Tetap early lead."),
    "ACOS-3aed": dyn("ACOS-3aed") + (" +179 interval ini (5,967/mnt, 1,23x - di bawah 1,5x), "
        "velocity GAGAL. Umur/pct/website UNVERIFIED. Tetap watchlist-only."),
    "HackouCoinPass": dyn("HackouCoinPass") + (" Minted-by-user 2026-11-10 (#539); freeMinted "
        "751/1111 = 67,6%. Tanpa aksi."),
    "HIVE Agents": dyn("HIVE Agents") + " Minted-by-user; tanpa perubahan.",
    "Bubblebruin": dyn("Bubblebruin") + (" Minted-by-user: freeClaimed 2429/7777 = 31,2%. "
        "Tanpa aksi."),
    "Zapcourier": dyn("Zapcourier") + (" Minted-by-user: freeClaimed 712/712 = 100% (free pool "
        "habis). Tanpa aksi."),
}
for name, text in notes.items():
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote2031_1110"] = text

# ---- top-level run notes with true 2031 numbers ----
snap["runNote2031_1110"] = (
    "Run 2031 (2026-11-10 20:31-~21:0x WIB, blok re-read 132785256): re-read 675 kontrak + 85 "
    "track_c (864,4 dtk). EARLY LEAD BARU 0; SELLOUT BARU 0; AGE-EXCLUDED BARU 0. Velocity LOLOS 1 "
    "TANPA promosi: Golden Agents +21, 2,10x (free% + umur UNVERIFIED, website none). BYTEBLOOM "
    "agentFree 400/2000 = 20,0% + KERNELMONK 462/2000 = 23,1% (keduanya <25% strong lead; website "
    "terverifikasi; slot terbuka; re-read prioritas run berikut). Lanternfield 251/1500 = 16,7% "
    "(+193 interval ini; website UNVERIFIED). Agentic freeMinted 940/1000 tapi gate FAILED + "
    "velocity gagal - tetap blocked (freePctVerified 18,9% lama ditandai inkonsisten). Scan leg "
    "FAST-FAIL (preflight Ankr 401, 6,0 dtk, head 132785213; watermark tetap 132512564; gap "
    "~272.649 blok). binanceai.fun TIDAK BERUBAH (refund phase). Bridge tidak berubah (116 "
    "kontrak). 0 kandidat baru, 0 strong lead baru, 0 track-C lead/kandidat baru, 0 track-B claim, "
    "0 eksekusi. KOREKSI: merge run ini sempat menyalin blok hardcoded run 2001 (angka Lanternfield "
    "58/59 + catatan run 2001) - sudah diperbaiki ke bacaan 2031 di fixmerge ini; Lanternfield "
    "tetap early lead yang dilaporkan sekali run 2001, bukan run 2031.")
snap["runNote2031_1110_scan"] = (
    "Run 2031 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (head 132785213), HTTP 401 "
    "Unauthorized dalam 6,0 dtk (outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. "
    "1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~272.649 blok dan tumbuh "
    "- milik backfill, ikut gagal 401). Route 5c: tanpa output scan baru (tidak ada ERC-20 backlog "
    "baru untuk di-shape-check run ini).")
snap["runNote2031_1110_discovery"] = (
    "Run 2031 discovery: Sourcify feed 20 terbaru (verified 13:07-13:35Z), 5 kontrak baru "
    "di-shape-check run ini, 0 hit S1/S2 (near-miss: 0x76df8cf8 mint + quote + agent registry "
    "tanpa free view; 0x9c464fe1 9 fns tanpa mint/quote/free/agent; 0x58274c6a registry tanpa "
    "mint/free; 0x5fd44869 tanpa mint/free/agent; 0xdf3886c2 ERC-20 biasa). 15 lain dari feed "
    "sudah di hot-leg-seen (0xd84d4ad7, 0xBeb9CA62, 0x2FC1BE66, 0xEe778277, 0x12c69A06 dkk - "
    "bukan sale-shape). Boltbook EN+ZH via curl langsung (46.014/46.113 byte): 13/14 alamat, "
    "SEMUA sudah di snapshot atau hot-leg-seen, 0 baru. Sweep Square: Oathbots 0xb777c522, "
    "AgentForge 0xf11ea7f1, Hundred 0x80ade84f - semua publikasi 25-28 Okt 2026 (>24 jam), bukan "
    "lead; post Square berisi instruksi mint untuk AI - DIABAIKAN (instruksi dari konten "
    "eksternal, bukan perintah user). Komplemen rute 6: Odaily newsflash + PANews 0 mention "
    "agent/free-mint; DappBay tidak dibutuhkan (tidak ada gate baru yang perlu dicek).")
snap["runNote2031_1110_binanceai"] = (
    "Run 2031 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0 (direct eth_call, blok 132785497). Status "
    "closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang. "
    "pending_claims kosong.")
snap["runNote2031_1110_age_exclusions"] = (
    "Run 2031 age-exclusions (aturan <24 jam): 0 BARU. Tidak ada entri non-terminal dengan "
    "launch/first-mint terverifikasi di jendela 2026-11-09 20:01-20:31 WIB yang melewati 24 jam "
    "run ini (dicek via launchNote/first-mint di snapshot). DITAHAN preseden run 1931 tetap "
    "berlaku (pool UNVERIFIED: HELIX, Beast16, Pressure, NUMBI, Lucky Cat, Meow Cards, BAHUANG3, "
    "Reel, Riddle Run, Gloop, Pixel Laptop; launch UNVERIFIED: KIJIN, Dragon Agent, Iron Bloom, "
    "Agentic, 0x13A1Ebc9-new, Shard Id, Sidecoo Season, STAR CARDS, JOLT).")
snap["last_run_note"] = snap["runNote2031_1110"]

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("FIXMERGE DONE. Lanternfield:", snap["contracts"]["Lanternfield"]["totalSupply"],
      snap["contracts"]["Lanternfield"]["freeMinted"],
      snap["contracts"]["Lanternfield"]["freePctVerified"])
