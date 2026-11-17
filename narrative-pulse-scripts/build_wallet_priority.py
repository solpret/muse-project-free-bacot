#!/usr/bin/env python3
"""Build clean, full-address-only wallet priority file (internal use).
Truncated addresses are excluded entirely from the output.
No wallet is promoted to the trusted watchlist by this script.
"""
import re, json
from pathlib import Path

ws = Path.home() / "workspace"
early = (ws / "narrative-pulse/early-call-candidates.md").read_text(errors="ignore")
holder = (ws / "narrative-pulse/holder-watchlist.md").read_text(errors="ignore")
surv = (ws / "research_notes/bsc-survivor-token-wallets-20261031-1349/report.md").read_text(errors="ignore")
pat = re.compile(r"0x[0-9a-fA-F]{40}")
early_holder = set(pat.findall(early + holder))
survivor_all = set(pat.findall(surv))

survivor_non_exchange = {
    # Private EOAs only, after 2026-10-31 linkage audit correction:
    # 9 addresses from the earlier survivor top-holder table were reclassified
    # by OKLink as exchange wallets or contracts and are NO LONGER in Tier A.
    # They are now in Tier E via surv_excluded below.
    "0xda91cefe240175e6fab56271110427a4195ab71f",
    "0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc",
    "0x5b2f11cab406f580a7c6faf620ee35daaf8648a5",
    "0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
    "0x75642756e4ba4cc8fbe76df2239cada046cfc854",
    "0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a",
    "0x892200223bdfb11d2506c5ab1cae9222ce253acc",
    "0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c",
    "0xaab80f45b97d9dc86d9bea56a3e98274ba81026e",
    "0xb787a5603d20e61585e20e7a13a1c0d6c03a1462",
    "0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf",
    "0x13d1e9a96eba7906e1ede348c9bb604a03e46d02",
}
# Survivor non-exchange addresses are matched case-insensitively against
# the report's checksummed forms.
survivor_non_exchange_norm = {a.lower() for a in survivor_non_exchange}
def norm_set(s):
    return {a.lower(): a for a in s}
surv_map = norm_set(survivor_all)
surv_ne = [surv_map[a] for a in survivor_non_exchange_norm if a in surv_map]
surv_excluded = sorted(set(survivor_all) - set(surv_ne))

top8e = "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"
tier_b = "0x2325f175975abdbcde555c79cc8e63381d28551b"
negative = {
    "0xb3466bfccf29e3babb61ca0f1b8984fde6ed728e",
    "0x612add8664aaacefbfa529633fefaf42dd16565a",
    "0xd392967fc834d718f4f9627fc5552881d1048727",
    "0xd9c03f53044bb1dc3b4d59622ce631ceb307a54d",
    "0x318d2aae4c99c2e74f7b5949fa1c34df837789b8",
    "0xf5988713400da6fc8a58ec9515e2b0df9b40b115",
}
token_contracts_early = {
    "0x23214ccbffb6ef479da64d1842b10b5525997777",
    "0xc853d8253f0d8346ca80f3f6af53e49a763e7777",
    "0x21aeddf21ee854f20cb497b0430437c4ab367777",
    "0x9d01d9ca91703b881dc0e585c6b746085b8f7777",
    "0x481f5963bf10cba972d52f138740155b2cda7059",
    "0x872c29369d8446dda5916156403f6a7491847777",
    "0x76219fbdc228a84ad19637ffbb6cdaa95a227777",
    "0x6b2ce31a577d92f73516c7a91febc7672247e694",
    "0x3b056facce631561be371e0bc14f07d826737777",
    "0x0b35285fe783dd3441573b84be4fbdb743457777",
    "0x0c6302401aa5325c2e36f170f52c00b1d220b405",
    "0xe61aad11bf4282fd5a8c584baa4ff2c9c50c7777",
    "0x415aac3e46264c046d103c994a1da71f05c547f9",
    "0xa64e9de168981eafd0b4a281faf543b95f387777",
}
eh_map = norm_set(early_holder)
def get(m, key):
    return m.get(key.lower(), key)
tier_a = [get(eh_map, top8e)] + sorted(surv_ne)
tier_a = sorted(set(tier_a))
tier_b_addr = get(eh_map, tier_b)
neg_addrs = sorted(get(eh_map, a) for a in negative if a.lower() in eh_map)
known_early = {top8e.lower(), tier_b.lower()} | {a.lower() for a in negative} | {a.lower() for a in token_contracts_early}
tier_d = sorted(a for a in early_holder if a.lower() not in known_early)
tier_e = sorted(set(surv_excluded) | {get(eh_map, a) for a in token_contracts_early if a.lower() in eh_map})

out = []
out.append("# Wallet Priority — alamat lengkap saja (INTERNAL)")
out.append("")
out.append("Dibuat 2026-10-31. File ini HANYA berisi alamat lengkap (42 karakter, 0x + 40 hex).")
out.append("Alamat terpotong DIBUANG dari file ini — jumlah alamat terpotong di file ini: 0.")
out.append("File ini BUKAN daftar pantau terpercaya. `wallet-watchlist.md` tetap 0 alamat.")
out.append("Tidak ada wallet di sini yang dipromosikan: promosi butuh PnL terealisasi 30 hari +")
out.append("minimal 10 trade terealisasi + perilaku holding tercatat + keputusan user.")
out.append("Data GMGN/DexScreener/GeckoTerminal adalah agregat sekunder, bukan bukti on-chain mentah.")
out.append("On-chain menunjukkan APA dan KAPAN, bukan NIAT — tidak ada klaim insider.")
out.append("")
out.append("## Kriteria prioritas (dari kriteria yang sudah dibuat)")
out.append("")
out.append("1. Repeat lintas token, masih memegang, bersih dari tag Sniper/Bundler, bukan exchange.")
out.append("2. Top holder satu token, masih memegang saat snapshot, bukan exchange, diurutkan")
out.append("   berdasarkan porsi kepemilikan di laporan survivor.")
out.append("3. Wallet dengan data PnL sekunder (GMGN) yang menguntungkan, tapi belum terukur")
out.append("   penuh — tetap di bawah Tier A karena pengukurannya belum memenuhi syarat promosi.")
out.append("4. NEGATIF / jangan diikuti: klaster sniper, funder sniper hub, funder tidak aktif")
out.append("   dengan flag phishing — dicatat sebagai filter negatif, bukan sinyal follow.")
out.append("5. Belum terklasifikasi: alamat lengkap lain yang perannya belum terverifikasi")
out.append("   (bisa wallet trader, bisa alamat lain) — JANGAN dipakai sebelum dicek.")
out.append("6. Dikecualikan: kontrak token, kontrak pool, burn, dan wallet exchange/kustodian.")
out.append("")
def section(title, addrs, note):
    out.append(f"## {title} ({len(addrs)} alamat)")
    out.append("")
    if note:
        out.append(note)
        out.append("")
    for a in addrs:
        out.append(f"- {a}")
    out.append("")
section("Tier A — Prioritas tertinggi, repeat / top holder masih memegang", tier_a,
        "Wallet 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 adalah satu-satunya kandidat early-call dengan 2 kaki masih memegang 100% (ok + 旺财). "
        "KOREKSI AUDIT LINKAGE 2026-10-31: repeat survivor yang dulu dicatat sebagai non-exchange (0xed9ab5bc05a0152b9dc2f7902e8369af7bc18771) "
        "ternyata adalah wallet exchange Bitget menurut OKLink, jadi SUDAH dipindah ke Tier E dan TIDAK dihitung sebagai monitor independen. "
        "Tier A di file ini sekarang hanya berisi wallet EOA privat. Sisanya adalah top holder survivor privat, diurutkan alfabetis di file ini; "
        "urutan porsi ada di laporan survivor.")
section("Tier B — Data sekunder menguntungkan, belum terukur penuh", [tier_b_addr],
        "Wallet ini tercatat di review GMGN dengan PnL 7 hari positif dan win rate tinggi, tapi itu data agregat sekunder, "
        "bukan PnL terealisasi 30 hari + 10 trade yang disyaratkan promosi. Tetap di bawah Tier A.")
section("Tier C — NEGATIF, jangan diikuti", neg_addrs,
        "Klaster sniper / funder sniper hub / funder tidak aktif. Dicatat hanya sebagai filter negatif.")
section("Tier D — Belum terklasifikasi, verifikasi dulu sebelum dipakai", tier_d,
        "Alamat lengkap dari koleksi lama yang perannya belum terverifikasi. Jangan dipakai sebagai sinyal follow "
        "sampai dicek: apakah wallet trader atau alamat lain, riwayat trade, dan PnL terealisasi.")
section("Tier E — Dikecualikan (kontrak / pool / burn / exchange)", tier_e,
        "Bukan wallet trader individu. Disimpan di sini hanya agar pengecualiannya bisa diaudit, bukan untuk diikuti.")
total = len(set(tier_a + [tier_b_addr] + neg_addrs + tier_d + tier_e))
out.append(f"## Total")
out.append("")
out.append(f"Total alamat lengkap unik di file ini: {total}")
out.append(f"Tier A: {len(tier_a)}, Tier B: 1, Tier C: {len(neg_addrs)}, Tier D: {len(tier_d)}, Tier E: {len(tier_e)}")
out.append("Alamat terpotong di file ini: 0")
out.append("")
out_path = ws / "narrative-pulse/wallet-priority-full.md"
out_path.write_text("\n".join(out))
print(f"wrote {out_path} total={total} A={len(tier_a)} C={len(neg_addrs)} D={len(tier_d)} E={len(tier_e)} early_holder={len(early_holder)} survivor={len(survivor_all)}")
