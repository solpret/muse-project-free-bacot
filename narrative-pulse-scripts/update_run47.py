# -*- coding: utf-8 -*-
import json, shutil, datetime
p = '/home/hatch/workspace/narrative-pulse/tier-ab-watch-state.json'
shutil.copy(p, p + '.bak-run47')
s = json.load(open(p, encoding='utf-8'))

# (address, bnb, run47_summary)
U = [
("0x13d1e9a96eba7906e1ede348c9bb604a03e46d02", "0 ($0.008)",
 "Run 47: PUBLIC. No Buy; Activity hanya Tx In lama (terbaru 51d), bukan buy baru."),
("0x2325f175975abdbcde555c79cc8e63381d28551b", "1.12 ($791.94)",
 "Run 47: PUBLIC. Symbol-new Buy (CA UNVERIFIED, 1 entity, NOT a signal): 屎壳郎 73,74 $68,36 (33m, pasti dalam jendela) + 15,27 $20,44 (1h) + 48,61 $68,44 (1h, batas tidak pasti). 屎壳郎 now known for this wallet. Buy 雪球 144,17 $20,45 (1h) + 444,2 $68,15 (1h) adalah re-trade token dikenal (run 43), bukan token baru. Buy BURN 1,04K $20,76 (2h) adalah re-trade run 44/46, di luar jendela. BNB 1,12 ($791,94), naik dari run-46 1,06."),
("0x5b2f11cab406f580a7c6faf620ee35daaf8648a5", "0 ($0.014)",
 "Run 47: PUBLIC. No Buy; Activity hanya Tx In lama (terbaru 51d), bukan buy baru."),
("0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7", "0.001 ($1.05)",
 "Run 47: PUBLIC. No Buy; Activity Tx In 7d, bukan buy baru."),
("0x75642756e4ba4cc8fbe76df2239cada046cfc854", "0 ($0.03)",
 "Run 47: PUBLIC. No Buy; Activity hanya Tx In lama (terbaru 38d), bukan buy baru."),
("0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a", "0 ($0.011)",
 "Run 47: PUBLIC. No Buy; Activity hanya Tx In lama (terbaru 71d), bukan buy baru."),
("0x892200223bdfb11d2506c5ab1cae9222ce253acc", "0 ($0.041)",
 "Run 47: PUBLIC. No Buy; Activity Tx In 7d; Buy XPIN terakhir 20d lalu, bukan buy baru."),
("0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6", "0.03 ($21.57)",
 "Run 47: PUBLIC. Symbol-new Buy (CA UNVERIFIED, 1 entity, NOT a signal): 狗 126,7K $1.408 (16m, pasti dalam jendela) — Buy terbesar run ini; 狗 now known for this wallet. Buy 羊王 192,3K $1,38 (1h, batas tidak pasti) juga simbol-baru untuk wallet ini bila dalam jendela; 羊王 now known. Buy 吉祥 200K $1.409 (8h) di luar jendela. BNB 0,03 ($21,57)."),
("0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c", "0 ($0.01)",
 "Run 47: PUBLIC. No Buy; Activity hanya Tx In lama (terbaru 71d), bukan buy baru."),
("0xaab80f45b97d9dc86d9bea56a3e98274ba81026e", "0 ($0)",
 "Run 47: PUBLIC. No Buy; Activity Tx In 10d, bukan buy baru."),
("0xb787a5603d20e61585e20e7a13a1c0d6c03a1462", "0.007 ($4.86)",
 "Run 47: PUBLIC. No Buy; Activity Tx In 17d, bukan buy baru."),
("0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf", "0 ($0)",
 "Run 47: PUBLIC. No Buy; Activity hanya Tx In lama (terbaru 51d), bukan buy baru."),
("0xda91cefe240175e6fab56271110427a4195ab71f", "0.05 ($35.48)",
 "Run 47: PUBLIC. No Buy; Activity Tx In 15d, bukan buy baru."),
("0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc", "0 ($0)",
 "Run 47: PUBLIC. No Buy; Activity Tx In 15d, bukan buy baru. Diskrepansi BNB GMGN-vs-on-chain dari run sebelumnya belum dicek ulang on-chain pada run ini; dibawa maju belum terselesaikan."),
("0x9856bac497634a62a970233bc4b0f5bb52c844c1", "0 ($0)",
 "Run 47: PUBLIC. No Buy; Activity terbaru Tx Out 3d, bukan buy baru."),
("0x3628764a6576b8dfb31fba0aac6a333b64851423", "0.01 ($7.32)",
 "Run 47: PUBLIC. Symbol-new Buys (CA UNVERIFIED, 1 entity, NOT a signal): 打狗 1,13K $0,07 (9m); KARMA 1,13K $0,07 (21m) + 1,13K $0,071 (33m); NEON 1,13K $0,07 (46m); DAK 1,13K $0,07 (1h x2, batas tidak pasti); 来财 1,13K $0,07 (1h x3, batas tidak pasti). CORLA 1,13K $0,07 (57m) adalah re-trade token dikenal (run 43-46), bukan token baru; CORLA 2h di luar jendela. 打狗/KARMA/NEON/DAK/来财 now known for this wallet. Identik menit demi menit dengan dompet 17 (simbol, jumlah, nilai, label waktu sama persis) — pola skrip/operator sama MENGUAT, tapi TIDAK ada pendanaan bersama non-exchange / transfer langsung / pendanaan berantai yang teramati, jadi TIDAK ada runtuhan entitas; kandidat cek pendanaan mendalam. BNB 0,01 ($7,32)."),
("0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e", "0.034 ($24.43)",
 "Run 47: PUBLIC. Symbol-new Buys (CA UNVERIFIED, 1 entity, NOT a signal): 打狗 1,13K $0,07 (9m); KARMA 1,13K $0,07 (21m) + 1,13K $0,071 (33m); NEON 1,13K $0,07 (46m); DAK 1,13K $0,07 (1h x2, batas tidak pasti); 来财 1,13K $0,07 (1h x3, batas tidak pasti). CORLA 1,13K $0,07 (57m) re-trade (dikenal run 43-46). 打狗/KARMA/NEON/DAK/来财 now known. Identik menit demi menit dengan dompet 16 — pola skrip/operator sama MENGUAT, TIDAK ada keterkaitan KUAT terverifikasi (pendanaan/transfer), jadi TIDAK ada runtuhan entitas. BNB 0,034 ($24,43)."),
("0x40a8b422f09fe7f630ccb3dbd07ea258577b784c", "0.056 ($39.99)",
 "Run 47: PUBLIC. No Buy; Activity Tx In 2d, bukan buy baru."),
("0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74", "0.012 ($8.2)",
 "Run 47: PUBLIC. Symbol-new Buys (CA UNVERIFIED, 1 entity, NOT a signal): 打狗 1,13K $0,024 (7m); KARMA 1,13K $0,024 (19m) + (30m); WUKONG 1,13K $0,024 (42m); NEON 1,13K $0,024 (52m); DAK 1,13K $0,024 (1h x2, batas tidak pasti); 来财 1,13K $0,024 (1h x4, batas tidak pasti); 钱来 1,13K $0,024 (1h, batas tidak pasti). CORLA 1,13K $0,024 (1h) re-trade (dikenal run 43-46). 打狗/KARMA/WUKONG/NEON/DAK/来财/钱来 now known. Rotasi token sama dengan dompet 20/21 (jumlah tetap per dompet, selisih waktu ~1 mnt) — pola skrip/operator sama, TIDAK ada keterkaitan KUAT terverifikasi, TIDAK ada runtuhan entitas. BNB 0,012 ($8,2)."),
("0xad94ee77d0e868d299fb3e92b9d67560257f656d", "0.087 ($61.78)",
 "Run 47: PUBLIC. Symbol-new Buys (CA UNVERIFIED, 1 entity, NOT a signal): 打狗 1,13K $0,024 (8m); KARMA 1,13K $0,024 (20m) + (30m); WUKONG 1,13K $0,024 (42m); NEON 1,13K $0,024 (52m); DAK 1,13K $0,024 (1h x2, batas tidak pasti); 来财 1,13K $0,024 (1h x4, batas tidak pasti); 钱来 1,13K $0,024 (1h, batas tidak pasti). CORLA 1,13K $0,024 (1h) re-trade (dikenal run 43-46). 打狗/KARMA/WUKONG/NEON/DAK/来财/钱来 now known. Identik dengan dompet 19 kecuali selisih ~1 mnt — pola skrip/operator sama, TIDAK ada keterkaitan KUAT terverifikasi, TIDAK ada runtuhan entitas. BNB 0,087 ($61,78)."),
("0x38031ca8a54526f9fe90f11f07b55ae5fc01036a", "0.025 ($17.68)",
 "Run 47: PUBLIC. Symbol-new Buys (CA UNVERIFIED, 1 entity, NOT a signal): 打狗 832,25 $0,018 (8m); KARMA 832,25 $0,018 (20m) + (31m); WUKONG 832,25 $0,018 (42m); NEON 832,25 $0,018 (52m); DAK 832,25 $0,018 (1h x2, batas tidak pasti); 来财 832,25 $0,018 (1h x4, batas tidak pasti); 钱来 832,25 $0,018 (1h, batas tidak pasti). CORLA 832,25 $0,018 (1h) re-trade (dikenal run 43-46). 打狗/KARMA/WUKONG/NEON/DAK/来财/钱来 now known. Rotasi token sama dengan dompet 19/20 — pola skrip/operator sama, TIDAK ada keterkaitan KUAT terverifikasi, TIDAK ada runtuhan entitas. BNB 0,025 ($17,68)."),
("0x7488d5da6a6097de0ff88c7492c62c2fd1e56650", "0.01 ($7.16)",
 "Run 47: PUBLIC. Symbol-new Buys (CA UNVERIFIED, 1 entity, NOT a signal): 白小飛 1,1K $0,056 (2m); ZVL 110 $0,062 (19m); VCHAIN 11 $0,058 (36m); 孙悟空 1,1K $0,056 (1h, batas tidak pasti); MEMEBET 110K $0,058 (1h, batas tidak pasti); NEE 11 $0,06 (1h, batas tidak pasti). Douyin 110 $0,058 (52m) adalah re-trade token dikenal (run 46), bukan token baru; GRCO 110 $0,06 (1h) re-trade (run 45). 白小飛/ZVL/VCHAIN/孙悟空/MEMEBET/NEE now known for this wallet. BNB 0,01 ($7,16)."),
("0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b", "0.194 ($138.15)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 6M $187,6 (2h) adalah re-trade token dikenal (run 45-46) dan di luar jendela (label 2h = >=120 mnt)."),
("0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050", "0.306 ($217.8)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 8,4M $167,2 (2h) adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xf795c5250f3d4006283a0d0dbb378dc0e69df923", "0.473 ($336.12)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h ($1.085 dan $1.363) adalah re-trade token dikenal (run 45-46) dan di luar jendela. Ukuran 2h ini jauh di atas pola ~$167-190 dompet GrokBot lain — dicatat, bukan buy baru."),
("0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2", "0.157 ($111.53)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 7,2M $191,5 (2h) adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xaa49e7fec503664a39598645c7a3fbfa0374380d", "0.411 ($292.02)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x82c6085f9ec2722fd6c8fc47577368a156a25b9b", "0.232 ($164.4)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x3154f6949285ee7ac1593bd2bdf974adb6731c32", "0.246 ($174.81)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a", "0.224 ($159.2)",
 "Run 47: PUBLIC. No new Buy in window; Sell GrokBot 2h bukan buy, di luar jendela."),
("0xe9ed24db105a6b15f880025ed9ad024c06783895", "0.195 ($138.56)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x3a39aa05b149141a4bfc7d73611dceb0557b39c4", "0.152 ($107.67)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3", "0.16 ($113.88)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xb940e4cd40ea9e887cbc92879062676e2bc4a924", "0.3 ($212.78)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x4522e661d9c94ec54b37e71896351a7440ec4f07", "0.331 ($234.88)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024", "0.265 ($187.91)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xc6591fde9b44aa081062c9fc6ee48e443d24ef57", "0.209 ($148.39)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x362396125a55d932a09f0a5182140cbbcaf30b70", "0.265 ($187.92)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20", "0.284 ($201.42)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x2cc8192fc62e3640de91e75582cf3dbbd571b970", "0.275 ($194.93)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645", "0.322 ($228.22)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b", "0.171 ($121.27)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xc194efe22e874a3fe666b5de5a8fd369f12c32d5", "0.191 ($135.2)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xa952331ea48ea9c00c4608d8259c186021331f31", "0.263 ($186.29)",
 "Run 47: PUBLIC. No new Buy in window; Sell GrokBot 2h bukan buy, di luar jendela."),
("0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314", "0.329 ($233.56)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a", "0.444 ($315.01)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf", "0.158 ($112)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x64e893a4c5c930b2cc68b054792cbc66344aeb9a", "0.261 ($185.33)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36", "0.006 ($4.01)",
 "Run 47: PUBLIC. No new Buy in window; Sell 蝴蝶金库 1,8M $557,3 (52m) bukan buy; Buy 蝴蝶金库 914,3K $191,4 (2h) re-trade run 44/46, di luar jendela. BNB 0,006 ($4,01)."),
("0x97bd895f8123a7837368df410e7d308246c0b3e9", "0.194 ($137.41)",
 "Run 47: PUBLIC. No new Buy in window; Buy GrokBot 2h adalah re-trade token dikenal (run 45-46) dan di luar jendela."),
("0x341bed5b412968755f3dd6e9946636ac6f97457a", "1.24 ($880.07)",
 "Run 47: PUBLIC. No Buy; Activity terbaru Tx In 3d, bukan buy baru."),
("0xd124dd5825ecaad959acdea6336926eb40aa0c9b", "0.458 ($324.78)",
 "Run 47: PUBLIC. No Buy; Activity terbaru Tx In 1d, bukan buy baru."),
("0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f", "0.97 ($688.59)",
 "Run 47: PUBLIC. No Buy; Activity terbaru Tx In 3d, bukan buy baru."),
("0x355ea9e542b36c645a2dee63b9df079ccb9bf3db", "0.884 ($627.04)",
 "Run 47: PUBLIC. No Buy; Activity terbaru Tx In 1d, bukan buy baru."),
]

missing = [a for a, _, _ in U if a not in s['wallets']]
assert not missing, missing
assert len(U) == 54, len(U)
for a, bnb, summ in U:
    s['wallets'][a]['bnb'] = bnb
    s['wallets'][a]['run47_summary'] = summ

s['last_checked'] = "2026-11-05T21:36:00+07:00"
s['last_run'] = "2026-11-05 21:23-21:36 WIB (run 47; browser task harness-measured 21:23-21:36 WIB)"
s['last_run_note'] = ("Run 47 PUBLIC: 54/54 GMGN BSC pages loaded public, 0 login-gated. 74 Buy events in window from 8 wallets "
 "(31 certain in-window, labels <60m; 43 labelled '1h', boundary-uncertain vs 19:36 WIB). No CA verified for any token (symbol only), so NO verified-CA token bought by >=14 entities. "
 "Symbol-only window observations (CA UNVERIFIED, NOT signals): 打狗/KARMA/NEON/DAK/来财 5 entities each (micro-bot cluster 16/17/19/20/21; CORLA excluded as re-trade known since run 43); "
 "WUKONG/钱来 3 entities (19/20/21, 钱来 all '1h'); 屎壳郎 1 (wallet 2, symbol-new for that wallet), 狗 1 (wallet 8, $1.408, largest buy this run), 羊王 1 (wallet 8, '1h'), "
 "白小飛/ZVL/VCHAIN/孙悟空/MEMEBET/NEE 1 each (wallet 22); 雪球 re-trade (wallet 2, known run 43); Douyin/GRCO re-trade (wallet 22). "
 "Micro-bot cluster pattern STRENGTHENED: wallets 16 vs 17 identical minute-by-minute (same symbols, amounts 1,13K, $0,07, time labels); 19 vs 20 identical (~1 min shift); 21 same rotation at 832,25/$0,018 — same script/operator pattern, but NO shared non-exchange funding / direct transfer / chain funding observed on GMGN pages (Tx In sources truncated/unmatchable), so NO entity collapse under the strong-linkage rule; flagged for deeper funding check. "
 "GrokBot cluster (wallets 23-50) now shows 2h-labelled buys only — out of window, re-trade of run 45-46; wallet 25's 2h GrokBot buys ($1.085/$1.363) are far above the ~$167-190 pattern, noted. "
 "Caveats: browser task was not given the run-46 trade list, so no amount+$ duplicate matching against run 46 was done by the browser; duplicate/new-token checks in this note were done by the parent against state (see per-wallet run47_summary). "
 "'1h'-labelled buys may straddle the 19:36 WIB window boundary by a few minutes. Holdings tab NOT opened this run, holdings fields unchanged. "
 "GMGN-vs-on-chain BNB discrepancy for 0xf6a8... not re-checked on-chain this run; carried forward unresolved. Next run must re-read all 54 wallets.")
json.dump(s, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("OK updated", len(U), "wallets; last_checked", s['last_checked'])
