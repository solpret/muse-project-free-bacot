## 2026-11-03 20:32 WIB — hourly run (first run with state file)
- API /launch/campaign: available=true, paused=true, opened=false, totalMinted=0, totalPaid=0, priceCents=100, totalShares=10000, openingAt=10000, block 131441421.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, totalPaid=0; freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR) via selector 0x797cc2c5 (uint256,bytes32 order).
- No material change vs 19:35 WIB baseline → SILENT, no chat report, no execution. State: ~/workspace/agio-watch/state.json.
- Gap: Sourcify full_match metadata.json HTTP 404; not needed, selectors validated directly.

## 2026-11-03 21:32 WIB — hourly run — MATERIAL CHANGE, REPORT ONCE (trigger c)
- API /launch/campaign (block 131449533, re-fetched and stable): available=true, paused=false (was true), opened=false, totalMinted=130 (was 0), totalPaid=130000000000000000000, priceCents=100, totalShares=10000, openingAt=10000, pair CHANGED to 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (was 0x2eb1f345A1460e830ea97835b45fe8fec5d08564).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131449608, NEWER than API block): paused=true, opened=false, totalMinted=0, totalPaid=0; freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR) via selector 0x797cc2c5.
- Verdict: API activity signal only, NOT a confirmed launch opening — opened=false on both sources and the mint contract itself is still paused at 0. Pair change + API/chain divergence reported as unverified, not interpreted. No preview/mint/approve/sign/login performed. State: ~/workspace/agio-watch/state.json (+ goal hidden_files copy).

## 2026-11-03 22:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 130 -> 182, totalPaid 182000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131457438.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131457467, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 00:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 216 -> 242, totalPaid 242000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131473424.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131473479, read-only eth_call; first attempt failed mid-run on RPC connection close, single read-only retry succeeded): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 01:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 242 -> 295, totalPaid 295000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131481418.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131481428, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 03:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 358 -> 468, totalPaid 374000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131497352.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131497427, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 04:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 468 -> 476, totalPaid 376000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131505418.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131505444, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 05:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 476 -> 585, totalPaid 393000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131513485.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131513538, read-only eth_call; first attempt failed mid-run on RPC connection close, single read-only retry succeeded): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 06:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 585 -> 651, totalPaid 395000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131521351.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131521423, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 07:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 651 -> 700, totalPaid 397000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131529417.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131529452, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 08:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 700 -> 816, totalPaid 398000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131537415.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131537436, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 09:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 816 -> 905, totalPaid 405000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131545347.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131545410, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 10:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 905 -> 984, totalPaid 405000000000000000000 -> 417000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131553413.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131553424, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 11:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 984 -> 1043, totalPaid 417000000000000000000 -> 427000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131561346.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131561423, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 12:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 1043 -> 1069, totalPaid 427000000000000000000 -> 428000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131569345.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131569411, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB 2026-11-03; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 13:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 1069 -> 1102, totalPaid 428000000000000000000 -> 430000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131577343.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131577445, read-only eth_call; first attempt failed mid-run on RPC connection close, single read-only retry succeeded): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB 2026-11-03; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 14:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 1102 -> 1128, totalPaid 430000000000000000000 -> 434000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 131585342.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131585558, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR. Note: primary dataseed RPCs returned intermittent HTTP 403 this run; all chain values re-verified via alternate dataseeds (dataseed2/3/4) with retries, so the read is complete.
- Verdict: SILENT. Trigger (c) already reported once at 21:32 WIB 2026-11-03; no trigger (a)/(b) met; on-chain state unchanged. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.

## 2026-11-04 15:32 WIB — SILENT
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted 1128 -> 1165, totalPaid 434e18 -> 437e18, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5, block 131593339.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131593425: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Primary dataseeds failed; alternate dataseeds 2/3/4 succeeded.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent. No preview/mint/approve/sign/login.

## 2026-11-04 16:32 WIB — SILENT
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted 1165 -> 1194, totalPaid 437e18 -> 439e18, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5, block 131601336.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131601397: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent. No preview/mint/approve/sign/login.

## 2026-11-04 17:32 WIB — SILENT
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted 1194 -> 1203, totalPaid unchanged 439e18, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5, block 131609333.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131609407: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent. No preview/mint/approve/sign/login.

## 2026-11-04 18:32 WIB — SILENT
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted 1203 -> 1215, totalPaid 439e18 -> 440e18, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5, block 131617331.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131617391: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent. No preview/mint/approve/sign/login.
- 2026-11-04 19:32 WIB: SILENT. API opened=false, paused=false, available=true, totalMinted 1215->1226, totalPaid 440e18->441e18, block 131625329, pair unchanged. On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB block 131625384: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR). No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. Read-only only; no preview/mint/approve/sign/login.
- 2026-11-04 20:32 WIB: SILENT. API opened=false, paused=false, available=true, totalMinted 1226->1236, totalPaid 441e18->443e18, block 131633394, pair unchanged. On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB block 131633452: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR). No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. Read-only only; no preview/mint/approve/sign/login.
- 2026-11-04 21:32 WIB: SILENT. API opened=false, paused=false, available=true, totalMinted 1236->1246, totalPaid unchanged 443e18, block 131641388, pair unchanged. On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB block 131641415: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR). No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. Read-only only; no preview/mint/approve/sign/login.

## 2026-11-04 22:32 WIB — SILENT, no material change
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 1246 -> 1249, totalPaid unchanged 443000000000000000000, pair unchanged, block 131649383.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true (confirmed on 2 dataseed endpoints after one transient 403), opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so this run stays silent per body. API-vs-chain divergence persists, unexplained. Read-only only; no preview/mint/approve/sign/login. State saved to ~/workspace/agio-watch/state.json.

## 2026-11-04 23:32 WIB — SILENT, no material change
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 1249 -> 1260, totalPaid 443000000000000000000 -> 445000000000000000000, pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5, block 131657314.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131657394, read-only eth_call; first attempt failed mid-run on remote-end-closed-connection, single read-only retry succeeded): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so this run stays silent per body. API-vs-chain divergence persists, unexplained. Read-only only; no preview/mint/approve/sign/login. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copy).

## 2026-11-05 00:32 WIB — SILENT, no material change
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 1260 -> 1268, totalPaid unchanged 445000000000000000000, pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5, block 131665311.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131665384, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so this run stays silent per body. API-vs-chain divergence persists, unexplained. Read-only only; no preview/mint/approve/sign/login. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copy).

## 2026-11-05 01:32 WIB — SILENT, no material change
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 1268 -> 1271, totalPaid unchanged 445000000000000000000, pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5, block 131673378.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131673392, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so this run stays silent per body. API-vs-chain divergence persists, unexplained. Read-only only; no preview/mint/approve/sign/login. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies).

## 2026-11-05 02:32 WIB — SILENT, no material change
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted UNCHANGED at 1271 (was 1271), totalPaid unchanged 445000000000000000000, pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5, block 131681777.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 131681852, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB and API totalMinted did not move this run, so this run stays silent per body. API-vs-chain divergence persists, unexplained. Read-only only; no preview/mint/approve/sign/login. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies).

## 2026-11-05 03:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1271 (unchanged), totalPaid=445000000000000000000 (unchanged), block 131689309.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (eth_call only): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks, block 131689390.
- No trigger (a)/(b)/(c): no material change. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirror). No preview/mint/approve/sign/login.

## 2026-11-05 04:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1271->1272, totalPaid=445000000000000000000->446000000000000000000, block 131697374, pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (eth_call only): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks, block 131697395.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent despite API totalMinted +1. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirrors). No preview/mint/approve/sign/login.

## 2026-11-05 06:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1272 (unchanged), totalPaid=446000000000000000000 (unchanged), block 131713307, pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (eth_call only; first RPC attempt dropped mid-run, retry via alternate dataseeds succeeded): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks, block 131713433.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirror). No preview/mint/approve/sign/login.

## 2026-11-05 07:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1272 (unchanged), totalPaid=446000000000000000000 (unchanged), block 131721371, pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (eth_call only): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks, block 131721396.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirrors). No preview/mint/approve/sign/login.

## 2026-11-05 08:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1272 (unchanged), totalPaid=446000000000000000000 (unchanged), block 131729368, pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (eth_call only): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks, block 131729397.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirror). No preview/mint/approve/sign/login.

## 2026-11-05 09:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1272 (unchanged), totalPaid=446000000000000000000 (unchanged), block 131737296, pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (eth_call only): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks, block 131737360.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirror). No preview/mint/approve/sign/login.

## 2026-11-05 10:32 WIB — agio-free-mint-watch (SILENT)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted=1272, totalPaid=446e18, block 131745294 — unchanged vs 09:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR), block 131745359 — unchanged.
- No trigger (a)/(b)/(c-new) met; trigger (c) already reported once 2026-11-03 21:32 WIB. Read-only only; no preview/mint/approve/sign/login.

## 2026-11-05 11:32 WIB — agio-free-mint-watch (SILENT)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted=1272, totalPaid=446e18, block 131753291 — unchanged vs 10:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR), block 131753350 — unchanged.
- No trigger (a)/(b)/(c-new) met; trigger (c) already reported once 2026-11-03 21:32 WIB. Read-only only; no preview/mint/approve/sign/login.

## 2026-11-05 12:32 WIB — agio-free-mint-watch (SILENT)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted=1272->1273, totalPaid=446e18->447e18, block 131761287 — pair unchanged 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR), block 131761352 — unchanged.
- No trigger (a)/(b) met; trigger (c) already reported once 2026-11-03 21:32 WIB, so silent despite API totalMinted +1. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. Read-only only; no preview/mint/approve/sign/login.
--- run-log ---
2026-11-05 13:32 WIB: SILENT. API totalMinted 1273, totalPaid 447e18, opened=false, available=true (block 131769286). On-chain 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 131769344). No material change; no trigger (a)/(b)/(c-new). Read-only only.
2026-11-05 16:32 WIB: SILENT. API totalMinted 1273 -> 1274 (+1), totalPaid 447e18 unchanged, opened=false, available=true (block 131793277). On-chain 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 131793346). No material change; trigger (c) already reported once 2026-11-03 21:32 WIB, so silent despite API +1. Read-only only.
2026-11-05 19:32 WIB: SILENT. API totalMinted 1284, totalPaid 457e18, opened=false, available=true (block 131817269) — unchanged vs 18:32 run. On-chain 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 131817348). No material change; no trigger (a)/(b)/(c-new). Read-only only.
2026-11-05 20:32 WIB: SILENT. API totalMinted 1284, totalPaid 457e18, opened=false, available=true (block 131825265) — unchanged vs 19:32 run. On-chain 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 131825339). No material change; no trigger (a)/(b)/(c-new). Read-only only.
2026-11-06 00:32 WIB: SILENT. API totalMinted 1284, totalPaid 457e18, opened=false, available=true (block 131857254) — unchanged vs 23:32 run. On-chain 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 131857319). No material change; no trigger (a)/(b)/(c-new). Read-only only.
## 2026-11-06 01:32 WIB — SILENT
- API agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131865254 — tidak berubah vs run 00:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131865404: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — tidak berubah.
- Catatan: RPC Binance dataseed mengembalikan 403 pada eth_call di percobaan pertama; pembacaan berhasil lewat fallback RPC publik (bsc-dataseed.binance.org untuk eth_blockNumber, fallback lain untuk eth_call).
- Tidak ada trigger (a)/(b)/(c) baru; diam sesuai body. Tidak ada preview/mint/approve/sign/login.

## 2026-11-06 02:32 WIB — SILENT
- API agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131873253 — tidak berubah vs run 01:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131873824: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — tidak berubah.
- Catatan: RPC Binance dataseed/dataseed1 403 pada eth_call; percobaan pertama via publicnode/1rpc timeout; pembacaan berhasil lewat bsc-dataseed2.binance.org. Script agio_chain_check.py diperbarui dengan daftar RPC dataseed2/3/4 + bnbchain + publicnode agar run berikutnya lebih tahan gagal.
- Tidak ada trigger (a)/(b)/(c) baru; diam sesuai body. Tidak ada preview/mint/approve/sign/login.

## 2026-11-06 03:32 WIB — SILENT
- API agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131881319 — tidak berubah vs run 02:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131881342: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — tidak berubah.
- Tidak ada trigger (a)/(b)/(c) baru; diam sesuai body. Tidak ada preview/mint/approve/sign/login.
## 2026-11-06 05:32 WIB — agio-free-mint-watch (hourly, SILENT)
- API: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131897251 — unchanged vs 04:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131897337: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Unchanged.
- No trigger (a)/(b)/(c-new) met. SILENT. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-06 06:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: block 131905251, opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, totalShares=10000 — unchanged vs 05:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131905814: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged. First attempt failed (all RPCs closed connection at freeMintDone); retry succeeded.
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json.

## 2026-11-06 07:32 WIB
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131913313 — unchanged vs 06:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 131913372: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged.
- No material change; SILENT per body. No preview/mint/approve/sign/login.
- 2026-11-06 08:32 WIB: API unchanged (opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131921246). On-chain unchanged: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks, block 131921320. No material change — SILENT. No preview/mint/approve/sign/login.
- 2026-11-06 09:32 WIB: API unchanged (opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131929245). On-chain unchanged: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks, block 131929306. No material change — SILENT. No preview/mint/approve/sign/login.
- 2026-11-06 10:32 WIB: API ticked +1 (opened=false, paused=false, available=true, totalMinted 1284->1285, totalPaid 457e18->458e18, block 131937242). On-chain unchanged: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks, block 131937320. API tick is a continuation of already-reported API activity, not a new launch opening; trigger (c) already reported once 2026-11-03 21:32 WIB. No material change — SILENT. No preview/mint/approve/sign/login.
- 2026-11-06 13:32 WIB: API unchanged (opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 131961237). On-chain unchanged: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks, block 131961319. No material change — SILENT. No preview/mint/approve/sign/login.
2026-11-06 16:32 WIB — agio-free-mint-watch hourly: SILENT, no material change. API totalMinted 1285, totalPaid 458e18, opened=false (block 131985235). On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 131985299). No trigger (a)/(b); (c) already reported 2026-11-03 21:32 WIB. Read-only; no preview/mint/sign/login.
2026-11-06 17:32 WIB — agio-free-mint-watch hourly: SILENT, no material change. API totalMinted 1285, totalPaid 458e18, opened=false (block 131993234). On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 131993297). No trigger (a)/(b); (c) already reported 2026-11-03 21:32 WIB. Read-only; no preview/mint/sign/login.
2026-11-06 18:32 WIB — agio-free-mint-watch hourly: SILENT, no material change. API totalMinted 1285, totalPaid 458e18, opened=false (block 132001229). On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 132001305). No trigger (a)/(b); (c) already reported 2026-11-03 21:32 WIB. Read-only; no preview/mint/sign/login.
--- run-log ---
2026-11-06 19:32 WIB — SILENT. API unchanged (opened=false, totalMinted 1285, totalPaid 458e18, block 132009228). On-chain unchanged at block 132009288: paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks. No trigger (a)/(b); (c) already reported 2026-11-03 21:32 WIB. Read-only only.
- 2026-11-06 21:32 WIB: SILENT. API opened=false, totalMinted 1285, totalPaid 458e18 (block 132025224). On-chain paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 132025289). No material change vs 20:32 run; no trigger met.
- 2026-11-06 22:32 WIB: SILENT. API opened=false, totalMinted 1285, totalPaid 458e18 (block 132033286). On-chain paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks (block 132033337). No material change vs 21:32 run; no trigger met.

## 2026-11-06 23:32 WIB — agio-free-mint-watch (hourly)
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted 1285, totalPaid 458e18, block 132041218 — UNCHANGED vs 22:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132041296: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-07 01:32 WIB — hourly run
- API: opened=false, paused=false, available=true, totalMinted 1285, totalPaid 458e18 (block 132057175) — unchanged vs 00:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132057261: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged.
- No trigger (a)/(b)/(c-new) met. SILENT. No preview/mint/approve/sign/login.

## 2026-11-07 02:32 WIB — hourly run
- API campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132065174 — unchanged vs 01:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132065268: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged.
- No trigger (a)/(b)/(c-new) met. SILENT per body. No preview/mint/approve/sign/login.

## 2026-11-07 03:32 WIB — hourly run
- API: opened=false, paused=false, available=true, totalMinted 1285, totalPaid 458e18 (block 132073172) — unchanged vs 02:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132073251: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged.
- No trigger (a)/(b)/(c-new) met. SILENT per body. No preview/mint/approve/sign/login.
- 2026-11-07 04:32 WIB — SILENT. API unchanged (opened=false, totalMinted 1285, totalPaid 458e18, block 132081170). On-chain unchanged at block 132081253: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR). No trigger (a)/(b); (c) already reported 2026-11-03 21:32 WIB. Read-only; no preview/mint/sign.
2026-11-07 06:32 WIB — SILENT. API: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132097166. On-chain block 132097264: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks. No trigger (a)/(b)/(c-new). State updated.

## 2026-11-07 08:32 WIB — hourly run
- API: opened=false, paused=false, available=true, totalMinted 1285, totalPaid 458e18 (block 132113163) — unchanged vs 07:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132113237: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged.
- No trigger (a)/(b)/(c-new) met. SILENT per body. No preview/mint/approve/sign/login.
- 2026-11-07 11:32 WIB: SILENT. API unchanged (opened=false, totalMinted 1285, totalPaid 458e18, block 132137156). Chain unchanged at block 132137259: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks. No trigger (a)/(b); (c) already reported 2026-11-03. Read-only only.

## 2026-11-07 13:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted=1285, totalPaid=458e18, block 132153152. Unchanged vs 12:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132153233: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Unchanged.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json and goal hidden_files/agio-watch-state.json. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-07 14:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132161152. UNCHANGED vs 13:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132161231: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- No trigger (a)/(b)/(c-new). SILENT per body. State saved to ~/workspace/agio-watch/state.json. No preview/mint/approve/sign/login.

## 2026-11-07 15:32 WIB
- API: opened=false, paused=false, available=true, totalMinted 1285, totalPaid 458e18 (block 132169149) — unchanged vs 14:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132169210: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged.
- No trigger (a)/(b)/(c-new). SILENT. State updated.
- 2026-11-07 16:32 WIB — SILENT. API unchanged (opened=false, totalMinted 1285, totalPaid 458e18, block 132177149). On-chain unchanged: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks, block 132177235. No trigger (a)/(b)/(c-new). No preview/mint/sign/login.

## 2026-11-07 17:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132185147. UNCHANGED vs 16:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132185270: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- No trigger (a)/(b)/(c-new). SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-07 21:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132217134. UNCHANGED vs 20:35 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132217221: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- No trigger (a)/(b)/(c-new). SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-07 22:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132225132. UNCHANGED vs 21:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132225197: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- No trigger (a)/(b)/(c-new). SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-07 23:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132233132. UNCHANGED vs 22:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132233197: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- No trigger (a)/(b)/(c-new). SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-08 00:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132241130. UNCHANGED vs 23:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132241217: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT. No preview/mint/approve/sign/login; no execution authorised.
- 2026-11-08 01:32 WIB — SILENT. API unchanged (opened=false, paused=false, available=true, totalMinted 1285, totalPaid 458e18, block 132249129). On-chain unchanged at block 132249226: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). No trigger (a)/(b); (c) already reported 2026-11-03 21:32 WIB. Read-only; no preview/mint/sign/login.

## 2026-11-08 03:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132265125. UNCHANGED vs 02:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132265391: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- Note: several public RPCs (bsc-dataseed.binance.org, defibit, ninicoin, publicnode) returned RemoteDisconnected this run; read succeeded via fallback list in agio_chain_check.py.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-08 04:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132273260. UNCHANGED vs 03:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132273293: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- Note: on-chain read took ~80s (several public RPCs slow/timeout this run); succeeded via fallback list in agio_chain_check.py.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; no execution authorised.
- 2026-11-08 05:32 WIB — SILENT. API: opened=false, paused=false, available=true, totalMinted 1285, totalPaid 458e18 (blok 132281126). On-chain (blok 132281282): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false kedua task. Tidak ada perubahan vs run 04:32 WIB; trigger (a)/(b) tidak terpenuhi, (c) sudah dilaporkan 2026-11-03 21:32 WIB. Divergensi API-vs-chain tetap ada, tidak ditafsirkan sebagai pembukaan launch.

## 2026-11-08 06:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132289187. UNCHANGED vs 05:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132289271: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- Note: on-chain read took ~109s (several public RPCs slow/timeout this run); succeeded via fallback list in agio_chain_check.py.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-08 07:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1285, totalPaid=458e18, block 132297185. UNCHANGED vs 06:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132297215: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-08 08:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132305117): available=true, opened=false, paused=false, totalMinted=1285, totalPaid=458e18 — UNCHANGED vs 07:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132305201): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No material change; no trigger (a)/(b)/(c) new. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ hidden_files copy). No preview/mint/approve/sign/login performed.

## 2026-11-08 09:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132313117): available=true, opened=false, paused=false, totalMinted=1285, totalPaid=458e18 — UNCHANGED vs 08:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132313204): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No material change; no trigger (a)/(b)/(c) new. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ hidden_files copies). No preview/mint/approve/sign/login performed.

## 2026-11-08 10:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132321181): available=true, opened=false, paused=false, totalMinted=1285, totalPaid=458e18 — UNCHANGED vs 09:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132321328): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No material change; no trigger (a)/(b)/(c) new. SILENT per body. State saved to ~/workspace/agio-watch/state.json. No preview/mint/approve/sign/login performed.

## 2026-11-08 11:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132329177): available=true, opened=false, paused=false, totalMinted=1285, totalPaid=458e18 — UNCHANGED vs 10:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132329235): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No material change; no trigger (a)/(b)/(c) new. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ hidden_files copies). No preview/mint/approve/sign/login performed.

## 2026-11-08 12:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132337240): available=true, opened=false, paused=false, totalMinted=1285, totalPaid=458e18 — UNCHANGED vs 11:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132337294): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No material change; no trigger (a)/(b)/(c) new. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ hidden_files copies). No preview/mint/approve/sign/login performed.
## 2026-11-08 13:32 WIB — agio-free-mint-watch (hourly)
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted=1285, totalPaid=458e18 (unchanged vs 12:32 WIB run), block 132345102.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB at block 132345218: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c) new. SILENT per body. Read-only; no preview/mint/approve/sign/login.


## 2026-11-08 14:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted=1285, totalPaid=458000000000000000000, block 132353102. UNCHANGED vs 13:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132353231: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. API-vs-chain divergence persists, unexplained by sources read; not treated as launch opening.
- Action: SILENT. No preview/mint/approve/sign/login; monitor authorises no execution.

## 2026-11-08 16:32 WIB
- API: opened=false, paused=false, available=true, totalMinted 1285, totalPaid 458e18 (block 132369090) — unchanged vs 15:32 WIB.
- On-chain (block 132369179): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR) — unchanged.
- No material change; SILENT per body. No preview/mint/approve/sign/login.

## 2026-11-08 17:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted 1286 (+1 vs 1285 @16:32), totalPaid 459e18, block 132377086.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132377163: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b); API counter tick is the known persistent API-vs-chain divergence, not a launch opening; trigger (c) already reported once 2026-11-03 21:32 WIB.
- Action: SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies.
2026-11-08 18:32 WIB — API opened=false/paused=false/available=true, totalMinted 1287 (+1), totalPaid 460e18, block 132385086. On-chain block 132385144: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR). No material change; SILENT, no trigger (a)/(b)/(c-new). Known API-vs-chain divergence persists.

## 2026-11-08 19:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132393074 — UNCHANGED vs 18:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132393211: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json.

## 2026-11-08 20:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132401137 — UNCHANGED vs 19:32 run (first curl returned empty body; retry HTTP 200 confirmed).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132401212: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies.
- 2026-11-08 21:32 WIB: SILENT. API unchanged (opened=false, paused=false, totalMinted 1287, block 132409065). On-chain unchanged (paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks, block 132409152). No trigger (a)/(b)/(c).

## 2026-11-08 22:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132417128 — UNCHANGED vs 21:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132417204: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; no execution authorised.
- 2026-11-08 23:32 WIB: API unchanged (opened=false, paused=false, totalMinted 1287, totalPaid 460e18, block 132425124). On-chain unchanged (paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both, block 132425174). No trigger (a)/(b)/(c). SILENT.

## 2026-11-09 00:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132433124 — UNCHANGED vs 23:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132433175: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. API-vs-chain divergence persists, unexplained by sources read; not treated as a launch opening.
- Action: SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login; monitor authorises no execution.
## 2026-11-09 01:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132441124 — UNCHANGED vs 00:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132441168: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b)/(c) met; trigger (c) already reported once 2026-11-03 21:32 WIB. API-vs-chain divergence persists, unexplained by sources read; not treated as a launch opening.
- Action: SILENT per body. State saved to ~/workspace/agio-watch/state.json. No preview/mint/approve/sign/login; monitor authorises no execution.
--- run log ---
2026-11-09 02:32 WIB — SILENT. On-chain: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (both tasks), block 132449119. API unchanged: totalMinted 1287, totalPaid 460e18, opened=false, paused=false, available=true, block 132449124. No trigger (a)/(b)/(c). No preview/mint/sign/login.

## 2026-11-09 04:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132465656, read via browser.open fallback after direct curl timed out twice, exit 28): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 03:40 WIB run except block advanced.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132465762 (first attempt failed: all 9 RPCs timed out; retry succeeded): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ hidden_files copy). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-09 05:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132473055, direct curl OK): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 04:38 WIB run except block advanced.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132473162: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ hidden_files copy). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-09 06:32 WIB
- API: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132481120 (unchanged except block).
- On-chain (block 132481167): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change vs 05:32 WIB run; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json.
## 2026-11-09 07:32 WIB — hourly run: SILENT. API opened=false, paused=false, available=true, totalMinted 1287, totalPaid 460e18 (unchanged; block 132489119). On-chain (blok 132489160): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false REPOST_COMMENT + AVATAR. No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained.

## 2026-11-09 08:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132497116, direct curl OK): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 07:32 WIB run except block advanced.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132497241: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-09 09:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132505116. Unchanged except block.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132505192: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b)/(c). SILENT. State updated (3 copies).
- 2026-11-09 10:32 WIB: SILENT — API opened=false/totalMinted 1287 (blok 132513047); on-chain paused=true, opened=false, totalMinted=0, freeMintDone=false x2 (blok 132513161). No trigger.

## 2026-11-09 11:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132521182, direct curl OK): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 10:32 WIB run except block advanced.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132521244: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-09 12:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132529041, direct curl OK after ~13s): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 11:32 WIB run except block advanced.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132529256: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-09 13:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132537102): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 12:32 WIB run (block advanced only).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132537163: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-09 14:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132545098): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 13:32 WIB run (block advanced only).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132545206: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-09 15:33 WIB — hourly run (SILENT)
- API: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132553096 (unchanged except block).
- Chain (block 132553147): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained; not treated as launch opening. State updated; no preview/mint/sign/login.

## 2026-11-09 16:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132561096): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 15:33 WIB run (block advanced only).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132561189: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.
## 2026-11-09 17:32 WIB — hourly run
- API: opened=false, paused=false, available=true, totalMinted=1287 (unchanged), totalPaid=460e18, block 132569092.
- On-chain (block 132569408): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change vs 16:32 run; no trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.
- Note: first on-chain read via agio_chain_check.py returned empty output (exit 0); values verified by second direct RPC read.

## 2026-11-09 18:32 WIB — hourly run
- API: opened=false, paused=false, available=true, totalMinted=1287 (unchanged), totalPaid=460e18, block 132577090.
- On-chain (block 132577136): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change vs 17:32 run; no trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.

## 2026-11-09 19:32 WIB — SILENT
- API: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132585085 (naik dari 132577090).
- On-chain (blok 132585182): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false.
- Tidak ada perubahan material vs run 18:32 WIB; tidak ada trigger (a)/(b)/(c). Divergensi API-vs-chain tetap tidak terjelaskan.
- Tidak ada preview/mint/approve/sign/login.

## 2026-11-09 20:32 WIB — SILENT
- API: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132593079 (naik dari 132585085).
- On-chain (blok 132593134): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false.
- Tidak ada perubahan material vs run 19:32 WIB; tidak ada trigger (a)/(b)/(c). Divergensi API-vs-chain tetap tidak terjelaskan.
- Tidak ada preview/mint/approve/sign/login.
- 2026-11-09 21:32 WIB: API opened=false, paused=false, available=true, totalMinted 1287, totalPaid 460e18, block 132601009. On-chain (block 132601126): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR). No material change; SILENT, no trigger (a)/(b)/(c).

## 2026-11-09 22:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132608931, HTTP 200): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 21:32 WIB run except block advanced (132601009 -> 132608931).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132609002: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-09 23:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132616928, HTTP 200): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 22:32 WIB run except block advanced (132608931 -> 132616928).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132616995: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-10 00:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132624858, HTTP 200): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 23:32 WIB run except block advanced (132616928 -> 132624858).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132624962: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-10 01:32 WIB
- API: opened=false, paused=false, available=true, totalMinted 1287, totalPaid 460e18, block 132632855 (unchanged except block).
- Chain (block 132632965): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json.

## 2026-11-10 02:32 WIB
- API https://agio.family/api/v1/launch/campaign (block 132640921, HTTP 200): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 01:32 WIB run except block advanced (132632855 -> 132640921).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132640992: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-10 03:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 132649321): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18, totalShares=10000, openingAt=10000, priceCents=100. Unchanged vs 02:32 run except block advanced. First curl attempt returned empty (transient); retry via urllib succeeded.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132649010): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR (agentTokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json and goal hidden_files/state.json + agio-watch-state.json.
- API-vs-chain divergence (API totalMinted 1287 vs chain 0) persists, unexplained; not treated as launch opening.

## 2026-11-10 04:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, block 132656918, totalMinted 1287, totalPaid 460e18, totalShares 10000, openingAt 10000, priceCents 100.
- On-chain 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132656963: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR, agent tokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404).
- No change vs 03:32 WIB run; no trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login; monitor does not authorise execution.

## 2026-11-10 05:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 132664919, HTTP 200): available=true, opened=false, paused=false, totalMinted=1287, totalPaid=460e18 — UNCHANGED vs 04:32 WIB run except block advanced (132656918 -> 132664919).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132664964: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — UNCHANGED.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-10 06:32 WIB — agio-free-mint-watch (hourly, read-only)
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132672919. Unchanged vs 05:32 run except block advanced.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132673007: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained. SILENT, no preview/mint/sign/login.

## 2026-11-10 07:32 WIB — agio-free-mint-watch (hourly, read-only)
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1287, totalPaid=460e18, block 132680851. Unchanged vs 06:32 run except block advanced.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132681051: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained. SILENT, no preview/mint/sign/login.
- 2026-11-10 08:32 WIB: SILENT. Chain block 132688964: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR). API block 132688918: opened=false, paused=false, available=true, totalMinted 1288 (was 1287), totalPaid 461e18 (was 460e18). No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained.

## 2026-11-10 09:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted=1288 (unchanged vs 08:32), totalPaid=461e18 (unchanged), block 132696917.
- Chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132697006: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State updated. API-vs-chain divergence persists, unexplained.

## 2026-11-10 10:32 WIB (run hourly)
- API https://agio.family/api/v1/launch/campaign (HTTP 200): available=true, opened=false, paused=false, totalMinted=1288, totalPaid=461e18, block 132704914 — unchanged vs 09:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132704977): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b)/(c) met. SILENT. No preview/mint/approve/sign/login; no execution authorised.
- Gap noted (unchanged): API-vs-chain divergence (API totalMinted 1288 vs chain 0) persists, unexplained by sources read; not treated as launch opening.

## 2026-11-10 11:32 WIB (run hourly)
- API https://agio.family/api/v1/launch/campaign (HTTP 200 on retry; first attempt returned empty, transient): available=true, opened=false, paused=false, totalMinted=1288, totalPaid=461e18, block 132712981 — unchanged vs 10:32 run except block advanced.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132713024; RPCs slow, ~6 min to complete): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b)/(c) met. SILENT. No preview/mint/approve/sign/login; no execution authorised.
- Gap noted (unchanged): API-vs-chain divergence (API totalMinted 1288 vs chain 0) persists, unexplained by sources read; not treated as launch opening.

## 2026-11-10 12:32 WIB — run hourly
- API https://agio.family/api/v1/launch/campaign (HTTP 200, 1st attempt): opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, block 132720846. Tidak berubah vs run 11:32 WIB kecuali blok maju.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (blok 132720990): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Tidak berubah vs run 11:32 WIB.
- Divergensi API-vs-chain tetap ada dan tidak ditafsirkan sebagai pembukaan launch. Tidak ada trigger (a)/(b)/(c). SILENT — tidak ada laporan ke chat utama. Tidak ada preview/mint/approve/sign/login.

## 2026-11-10 13:32 WIB — run hourly
- API https://agio.family/api/v1/launch/campaign (HTTP 200, 1st attempt): opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, block 132728834. Tidak berubah vs run 12:32 WIB kecuali blok maju.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (blok 132728935): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Tidak berubah vs run 12:32 WIB.
- Divergensi API-vs-chain tetap ada dan tidak ditafsirkan sebagai pembukaan launch. Tidak ada trigger (a)/(b)/(c). SILENT — tidak ada laporan ke chat utama. Tidak ada preview/mint/approve/sign/login.

## 2026-11-10 14:32 WIB — run hourly
- API https://agio.family/api/v1/launch/campaign (HTTP 200, 1st attempt): opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, block 132736832. Tidak berubah vs run 13:32 WIB kecuali blok maju.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (blok 132736930): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Tidak berubah vs run 13:32 WIB.
- Divergensi API-vs-chain tetap ada dan tidak ditafsirkan sebagai pembukaan launch. Tidak ada trigger (a)/(b)/(c). SILENT — tidak ada laporan ke chat utama. Tidak ada preview/mint/approve/sign/login.
## 2026-11-10 15:32 WIB — run agio-free-mint-watch (hourly)
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, block 132744899. Tidak berubah vs 14:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ blok 132745002: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. Tidak berubah vs run sebelumnya.
- Trigger (a)/(b)/(c): tidak ada yang terpenuhi. SILENT. Divergensi API-vs-chain tetap ada dan tidak ditafsirkan sebagai pembukaan launch. State disimpan ke ~/workspace/agio-watch/state.json (+ salinan hidden_files/). Tidak ada preview/mint/approve/sign/login.


## 2026-11-10 16:32 WIB — run agio-free-mint-watch (hourly)
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, block 132752892. Tidak berubah vs 15:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ blok 132752934: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. Tidak berubah vs run sebelumnya.
- Trigger (a)/(b)/(c): tidak ada yang terpenuhi. SILENT. Divergensi API-vs-chain tetap ada dan tidak ditafsirkan sebagai pembukaan launch. State disimpan ke ~/workspace/agio-watch/state.json (+ salinan hidden_files/). Tidak ada preview/mint/approve/sign/login.

## 2026-11-10 17:32 WIB
- API: opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, block 132760823 (unchanged vs 16:32 run).
- On-chain (mint 0xeF98407D55b3506275732b94c300866a16D6A3BB, block 132760960): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. API-vs-chain divergence persists, unexplained.

## 2026-11-10 18:32 WIB (hourly)
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted=1288, totalPaid=461e18, block 132768820. Unchanged vs 17:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132768887: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR, agentTokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404).
- No trigger (a)/(b)/(c): no material change. SILENT per body. State saved to ~/workspace/agio-watch/state.json (mirrored to goal hidden_files). API-vs-chain divergence persists, unexplained, not treated as launch opening.

## 2026-11-10 19:32 WIB — hourly check (SILENT)
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, block 132776883. Unchanged vs 18:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132776920): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Unchanged vs 18:32 WIB.
- No trigger (a)/(b)/(c) met. No preview/mint/approve/sign/login performed; no execution authorised.

## 2026-11-10 20:32 WIB — hourly check (SILENT)
- API https://agio.family/api/v1/launch/campaign (HTTP 200): opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, block 132784880. Unchanged vs 19:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132784922): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Unchanged vs 19:32 WIB.
- No trigger (a)/(b)/(c) met. No preview/mint/approve/sign/login performed; no execution authorised.

## 2026-11-10 21:32 WIB — SILENT
- API https://agio.family/api/v1/launch/campaign: available=true, opened=false, paused=false, totalMinted 1288 (unchanged), totalPaid 461e18 (unchanged), pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5, block 132793013.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132793441: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB, so silent. No preview/mint/approve/sign/login.

## 2026-11-10 22:32 WIB — agio-free-mint-watch (hourly)
- API https://agio.family/api/v1/launch/campaign HTTP 200: available=true, opened=false, paused=false, totalMinted=1288 (unchanged vs 21:32), totalPaid=461e18, block 132800877.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132800935: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirror). No preview/mint/approve/sign/login.

## 2026-11-10 23:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted 1288 (unchanged), totalPaid 461000000000000000000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 (unchanged), block 132808808.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132808878, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR.
- Verdict: SILENT. No trigger (a)/(b)/(c) met; on-chain state unchanged since baseline. API-vs-chain divergence persists, unverified, not interpreted as launch opening. No preview/mint/approve/sign/login.
- 2026-11-11 00:32 WIB: AGIO watch — API opened=false, totalMinted 1288 (unchanged), chain paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks. No trigger; silent.

## 2026-11-11 01:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 132824802): available=true, opened=false, paused=false, totalMinted=1288, totalPaid=461e18, openingAt=10000, totalShares=10000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5. Unchanged vs 00:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132824913): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR. Unchanged vs 00:32 run.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json. No preview/mint/approve/sign/login performed.

## 2026-11-11 02:32 WIB — hourly run
- API (HTTP 200, block 132832799): opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18 — unchanged vs 01:32 WIB.
- Chain (block 132832887): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR) — unchanged vs 01:32 WIB.
- API-vs-chain divergence persists, unexplained; not treated as launch opening. No trigger (a)/(b)/(c). SILENT, no report. State updated.
- 03:32 WIB: SILENT. API opened=false, paused=false, available=true, totalMinted 1288, totalPaid 461e18, block 132840798 (unchanged). On-chain paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks, block 132840928. No trigger (a)/(b)/(c).

## 2026-11-11 04:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 132848798): available=true, opened=false, paused=false, totalMinted=1288, totalPaid=461e18 — unchanged vs 03:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132848878, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — unchanged vs 03:32 WIB.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json. No preview/mint/approve/sign/login performed.

## 2026-11-11 05:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 132856864): available=true, opened=false, paused=false, totalMinted=1288, totalPaid=461e18 — unchanged vs 04:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132856901, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — unchanged vs 04:32 WIB.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json. No preview/mint/approve/sign/login performed.

## 2026-11-11 06:32 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 132864796): available=true, opened=false, paused=false, totalMinted=1288, totalPaid=461e18 — unchanged vs 05:32 WIB.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132864897, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR — unchanged vs 05:32 WIB.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json. No preview/mint/approve/sign/login performed.
--- run-log ---
2026-11-11 08:32 WIB: API opened=false paused=false totalMinted=1288 totalPaid=461e18 (block 132880792); chain block 132880864 paused=true opened=false totalMinted=0 totalPaid=0 freeMintDone=false/false. No change vs 07:32 run. SILENT, no trigger (a)/(b)/(c).

## 2026-11-11 09:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, block 132889122 — UNCHANGED vs 08:32 WIB run. Note: first API fetch this run timed out twice (curl exit 28, HTTP 000); single retry succeeded HTTP 200 with identical values, so state updated from the successful retry only.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132888944: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. API-vs-chain divergence persists, unexplained. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-11 10:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (block 132897187, HTTP 200): opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 — UNCHANGED vs 09:32 WIB run. First fetch returned empty after 30s timeout; single retry succeeded.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132896994 (read-only eth_call, ~153s via fallback RPCs): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-11 11:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (block 132904779, HTTP 200, first try): opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 — UNCHANGED vs 10:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132904878 (read-only eth_call, ~45s via fallback RPCs): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-11 12:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (block 132912844, HTTP 200, first try): opened=false, paused=false, available=true, totalMinted=1288, totalPaid=461e18, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 — UNCHANGED vs 11:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132912885 (read-only eth_call, ~40s via fallback RPCs): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-11 13:33 WIB (run 13:32)
- API https://agio.family/api/v1/launch/campaign HTTP 200 (first attempt timed out 20s, retry OK): available=true, paused=false, opened=false, openingAt=10000, totalMinted=1288, totalPaid=461e18, block 132921042.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132920916: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No change vs 12:32 WIB run. No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.

## 2026-11-11 14:33 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (HTTP 200, first try, block 132928838): available=true, opened=false, paused=false, totalMinted=1289 (ticked +1 from 1288, first API-side move in days), totalPaid=461e18 (unchanged), openingAt=10000, totalShares=10000, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 — unchanged otherwise.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132928878 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED vs 13:33 WIB run.
- No trigger (a)/(b) met; trigger (c) already reported once 2026-11-03 21:32 WIB and on-chain totalMinted still 0. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files mirrors. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-11 15:32 WIB (hourly)
- API https://agio.family/api/v1/launch/campaign (block 132936772): available=true, opened=false, paused=false, totalMinted=1289 (flat vs 14:33 run), totalPaid=461e18 (flat), totalShares=10000, openingAt=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132936941): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State updated in ~/workspace/agio-watch/state.json.
- 2026-11-11 16:33 WIB: SILENT. API opened=false paused=false available=true totalMinted=1289 totalPaid=461e18 (block 132944766). On-chain paused=true opened=false totalMinted=0 totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR), block 132944942. No trigger (a)/(b)/(c). API-vs-chain divergence persists.
- 2026-11-11 17:32 WIB: SILENT. API opened=false, paused=false, available=true, totalMinted 1289 (flat vs 16:33), totalPaid 461e18, block 132952752. On-chain block 132952834: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). No trigger (a)/(b)/(c). Divergence API-vs-chain persists.
- 2026-11-11 18:37 WIB: SILENT. API opened=false, paused=false, available=true, totalMinted 1289 (flat vs 17:32), totalPaid 461e18, block 132960750. On-chain block 132960861: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). No trigger (a)/(b)/(c). Divergence API-vs-chain persists. (Note: chain check took ~5 min — public RPCs slow this run.)

## 2026-11-11 19:37 WIB (hourly run)
- API https://agio.family/api/v1/launch/campaign (block 132968745): opened=false, paused=false, available=true, totalMinted=1289 (flat vs 18:37 run), totalPaid=461e18 (unchanged), totalShares=10000, openingAt=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132968884): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change vs 18:37 run; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json. No preview/mint/approve/sign/login performed.
- Note: API-vs-chain divergence persists (API shows 1289 minted / paused=false while chain shows 0 / paused=true); not interpreted as a launch opening.

## 2026-11-11 20:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1289, totalPaid=461e18, block 132976740 — UNCHANGED vs 19:37 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 132976869: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED. Chain read took ~78s via fallback RPCs.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. No preview/mint/approve/sign/login; no execution authorised.
- 2026-11-11 21:32 WIB: API opened=false, paused=false, available=true, totalMinted 1289 (flat), totalPaid 461e18 (flat), block 132984739. On-chain block 132984826: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). No trigger (a)/(b)/(c). SILENT.

## 2026-11-11 22:32 WIB — hourly run (SILENT)
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 132992738): opened=false, paused=false, available=true, totalMinted=1289, totalPaid=461e18, totalShares=10000, openingAt=10000, priceCents=100. Identical to 21:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 132992862): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR (agentTokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404). Unchanged.
- No trigger (a)/(b)/(c) met. API-vs-chain divergence persists, unexplained; not treated as launch opening. State saved to ~/workspace/agio-watch/state.json. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-11 23:32 WIB — hourly run (SILENT)
- API https://agio.family/api/v1/launch/campaign (HTTP 200 after one 30s timeout retry, block 133001137): opened=false, paused=false, available=true, totalMinted=1289, totalPaid=461e18, totalShares=10000, openingAt=10000, priceCents=100. Identical to 22:32 run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 133000983): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR (agentTokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404). Unchanged. Chain read took ~177s via fallback RPCs.
- No trigger (a)/(b)/(c) met. API-vs-chain divergence persists, unexplained; not treated as launch opening. State saved to ~/workspace/agio-watch/state.json. No preview/mint/approve/sign/login; no execution authorised.
- 2026-11-12 01:32 WIB: SILENT. API opened=false, paused=false, available=true, totalMinted 1289 (flat), totalPaid 461e18, block 133016733. On-chain (block 133016849): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks. No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained.
- 2026-11-12 03:32 WIB: SILENT. API opened=false, paused=false, available=true, totalMinted 1289 (flat vs 02:32), totalPaid 461e18, block 133032726. On-chain (block 133032852): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks. No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained. State saved to ~/workspace/agio-watch/state.json + goal hidden_files mirror.

## 2026-11-12 04:32 WIB
- API: opened=false, paused=false, available=true, totalMinted=1289, totalPaid=461e18 (block 133040992). First curl attempt empty body (transient), retry HTTP 200.
- On-chain (block 133040906): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR).
- No change vs 03:32 WIB. No trigger (a)/(b)/(c). SILENT.

## 2026-11-12 05:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign HTTP 200 (first attempt OK): available=true, opened=false, paused=false, totalMinted=1289 (flat vs 04:32), totalPaid=461e18 (flat), block 133048724, openingAt=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133048806: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR, agentTokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404).
- No trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json and goal hidden_files copies.
- 2026-11-12 06:32 WIB: SILENT. API opened=false paused=false available=true totalMinted=1289 totalPaid=461e18 (flat vs 05:32). On-chain block 133056828: paused=true opened=false totalMinted=0 totalPaid=0 freeMintDone=false both tasks. No trigger (a)/(b)/(c). First API fetch empty-body transient, retry HTTP 200 OK.

## 2026-11-12 07:32 WIB
- API https://agio.family/api/v1/launch/campaign HTTP 200: available=true, opened=false, paused=false, totalMinted=1289 (flat), totalPaid=461e18 (flat), block 133064720.
- On-chain (agio_chain_check.py, block 133064832): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false untuk REPOST_COMMENT dan AVATAR.
- Tidak ada perubahan material vs run 06:32 WIB; trigger (a)/(b)/(c) tidak terpenuhi. SILENT. Tanpa preview/mint/approve/sign/login.

## 2026-11-12 08:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign HTTP 200 (first fetch empty body transient, retry OK): available=true, opened=false, paused=false, totalMinted=1290 (+1 vs 1289 flat since 11 Nov 19:37 WIB), totalPaid=461e18 (flat), block 133072784, openingAt=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133072928: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b) met; trigger (c) already reported once 2026-11-03 21:32 WIB — the +1 API increment with opened=false and on-chain 0 is recorded as part of the known unexplained API-vs-chain divergence, not a launch opening. SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files copies. No preview/mint/approve/sign/login performed; no execution authorised.
- 09:32 WIB agio-free-mint-watch: API opened=false, paused=false, totalMinted 1290 (flat vs 08:32), totalPaid 461 BNB; on-chain block 133080800: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). No trigger (a)/(b)/(c) — SILENT, state updated.
- 2026-11-12 10:32 WIB — AGIO hourly watch: API opened=false, totalMinted flat 1290, totalPaid 461 BNB; on-chain (block 133088838) paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks. No material change, SILENT per body. State updated.

## 2026-11-12 11:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 133096712): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 10:32 run), totalPaid=461 BNB, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 133096847): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json.
2026-11-12 12:32 WIB — SILENT. API: opened=false, paused=false, totalMinted=1290 (flat), totalPaid=461 BNB, block 133104710. Chain @133104799: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained.
2026-11-12 13:32 WIB — SILENT. API: opened=false, paused=false, totalMinted=1290 (flat), totalPaid=461 BNB, block 133112773. Chain @133112813: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained.

## 2026-11-12 14:32 WIB — hourly run (SILENT)
- API https://agio.family/api/v1/launch/campaign HTTP 200: opened=false, paused=false, available=true, totalMinted=1290 (flat vs 13:32), totalPaid=461, totalShares=10000, block 133120770.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133120814: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). No preview/mint/approve/sign/login. State saved to ~/workspace/agio-watch/state.json and goal hidden_files/state.json.

## 2026-11-12 15:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 133128696): available=true, opened=false, paused=false, totalMinted=1290 (flat vs 14:32 WIB), totalPaid=461 BNB, totalShares=10000, priceCents=100, openingAt=10000. Site HTTP 200.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 133128777): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR, agent tokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404).
- No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained; not treated as launch opening. SILENT. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-12 16:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 133136629): available=true, opened=false, paused=false, totalMinted=1290 (flat vs 15:32 run), totalPaid=461000000000000000000, totalShares=10000, openingAt=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 133136782): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR) for agent tokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404.
- No material change vs 15:32 run; no trigger (a)/(b)/(c). SILENT. State updated in ~/workspace/agio-watch/state.json and goal hidden_files/state.json. No preview/mint/approve/sign/login.

## 2026-11-12 17:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 133144627): available=true, opened=false, paused=false, totalMinted=1290 (flat vs 16:32 run), totalPaid=461000000000000000000, totalShares=10000, openingAt=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 133144733): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR) for agent tokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404.
- No material change vs 16:32 run; no trigger (a)/(b)/(c). SILENT. State updated in ~/workspace/agio-watch/state.json and goal hidden_files copies. No preview/mint/approve/sign/login.
- 21:32 WIB agio-free-mint-watch: SILENT. API opened=false, paused=false, totalMinted flat 1290 (block 133176606). On-chain batch read OK (bsc-dataseed3, ~1.1s, block 133176753): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false both tasks. No trigger (a)/(b)/(c). State saved.
- 2026-11-12 22:32 WIB — SILENT. API https://agio.family/api/v1/launch/campaign (block 133184428): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 21:32), totalPaid=461000000000000000000. On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 133184614, read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT and AVATAR. No trigger (a)/(b)/(c). Note: first batch attempt used wrong freeMintDone arg order and reverted; retried with verified selector 0x797cc2c5 (uint256,bytes32) — read complete.
## 2026-11-12 23:32 WIB — SILENT, no material change
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 133192422): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 22:32), totalPaid=461, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 133192520): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for REPOST_COMMENT + AVATAR.
- No trigger (a)/(b)/(c) met. No preview/mint/approve/sign/login. State saved to ~/workspace/agio-watch/state.json.

- 2026-11-13 00:32 WIB: API opened=false, paused=false, totalMinted=1290 (flat), block 133200486; chain block 133200517: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT, AVATAR). No material change vs 23:32 WIB. SILENT, no trigger (a)/(b)/(c).

## 2026-11-13 01:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (HTTP 200, block 133208553): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 00:32), totalPaid=461000000000000000000, totalShares=10000, openingAt=10000, priceCents=100.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 133208609): paused=true, opened=false, totalMinted=0, totalPaid=0; freeMintDone=false for REPOST_COMMENT and AVATAR (agent tokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404).
- No material change vs 00:32 WIB run; no trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json. API-vs-chain divergence persists, unexplained.
## 2026-11-13 02:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: available=true, paused=false, opened=false, totalMinted=1290 (flat vs 01:32 WIB), totalPaid=461e18, block 133216485, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5 unchanged.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133216580 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. No preview/mint/approve/sign/login; no execution authorised. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies).

## 2026-11-13 07:32 WIB — hourly run
- API: opened=false, paused=false, totalMinted=1290 (flat vs 06:32), totalPaid=461 BNB, block 133256411.
- On-chain (block 133256522): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files.

## 2026-11-13 09:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign (block 133272407): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 08:32), totalPaid=461 BNB, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (block 133272542): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No trigger (a)/(b)/(c): SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files (state.json, agio-watch-state.json). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-13 10:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1290 (flat vs 09:32), totalPaid=461000000000000000000, block 133280406.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133280512: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json.

## 2026-11-13 11:32 WIB
- API https://agio.family/api/v1/launch/campaign (200): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 10:32), totalPaid=461000000000000000000, block 133288405.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133288524: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR, agentTokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json.

## 2026-11-13 12:32 WIB
- API https://agio.family/api/v1/launch/campaign (200): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 11:32), totalPaid=461000000000000000000, block 133296471.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133296608: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR, agentTokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json.
- 14:32 WIB: SILENT — no change vs 13:32. API opened=false, totalMinted flat 1290; on-chain paused=true, opened=false, totalMinted=0, freeMintDone=false/false (block 133312459). Selector 0x797cc2c5 re-verified correct via keccak (freeMintDone(uint256,bytes32)). No trigger (a)/(b)/(c).

## 2026-11-13 15:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (block 133320253): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 14:32), totalPaid=461000000000000000000, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133320363 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-13 16:32 WIB
- API https://agio.family/api/v1/launch/campaign: opened=false, paused=false, available=true, totalMinted=1290 (flat vs 15:32), totalPaid=461000000000000000000, block 133328249.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133328404: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State updated.

## 2026-11-13 17:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (200, block 133336247): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 16:32), totalPaid=461000000000000000000, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133336341 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-13 18:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (200, block 133344241): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 17:32), totalPaid=461000000000000000000, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133344378 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-13 19:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (200, block 133352238): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 18:32), totalPaid=461000000000000000000, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133352336 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-13 20:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (200, block 133360369): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 19:32), totalPaid=461000000000000000000, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133360431 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files. No preview/mint/approve/sign/login; no execution authorised.
- 2026-11-13 21:32 WIB: SILENT. API opened=false, paused=false, totalMinted 1290 (flat vs 20:32), block 133368230. On-chain block 133368368: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). No trigger (a)/(b)/(c). API-vs-chain divergence persists, unexplained.

## 2026-11-13 22:32 WIB — hourly run, SILENT (partial read failure)
- API https://agio.family/api/v1/launch/campaign (200, block 133376495): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 21:32), totalPaid=461000000000000000000, totalShares=10000, priceCents=100, pair 0x4bbA5d0F3E19A29d7F6AE3332FDd1a3335a656A5.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: TIDAK TERVERIFIKASI run ini. agio_chain_check.py gagal di totalPaid ("all RPCs failed, last=<urlopen error timed out>") setelah ~5 menit; retry batch ke 10 endpoint BSC (dataseed1-4 binance/bnbchain, publicnode, 1rpc, ankr, omniatech) semua timeout 20-25 dtk; curl eth_blockNumber 60 dtk timeout; curl ulang API pun timeout (http 000). Egress VM flapping — bukan bukti perubahan on-chain.
- Keputusan: state.json TIDAK ditimpa (tetap state 21:32 WIB); tidak ada klaim perubahan on-chain. Sisi API: tidak ada trigger (a) opened=false, (c) totalMinted flat 1290. Trigger (b) freeMintDone tidak bisa dinilai run ini — tunggu run 23:32 WIB.
- No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-13 23:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign (200, block 133384427): opened=false, paused=false, available=true, totalMinted=1290 (flat vs 21:32), totalPaid=461000000000000000000, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133384595 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Read succeeded after the 22:32 WIB RPC failure — confirms no on-chain change.
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files. No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-14 00:32 WIB — hourly run, SILENT (read failure, both sources)
- API https://agio.family/api/v1/launch/campaign: TIDAK TERVERIFIKASI run ini. curl timeout 3x (exit 28, 20-25 dtk tiap percobaan).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB: TIDAK TERVERIFIKASI run ini. agio_chain_check.py gagal di eth_blockNumber ("all RPCs failed, last=<urlopen error timed out>") setelah ~3 menit (9 endpoint BSC); retry curl eth_blockNumber ke bsc-dataseed2.binance.org juga gagal (empty, ~15 dtk).
- Egress VM flapping — bukan bukti perubahan on-chain maupun pembukaan launch.
- Keputusan: state.json TIDAK ditimpa (tetap state 23:32 WIB 13 Nov); tidak ada klaim perubahan. Trigger (a)/(b)/(c) tidak bisa dinilai run ini — tunggu run 01:32 WIB.
- No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-14 01:32 WIB — hourly run, SILENT (API 502, on-chain verified)
- API https://agio.family/api/v1/launch/campaign: TIDAK TERVERIFIKASI run ini (curl mengembalikan "error code: 502"). Last verified API state 23:32 WIB 13 Nov: opened=false, paused=false, totalMinted=1290.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133400690 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Read succeeded after the 00:32 WIB total read failure — confirms no on-chain change.
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files (API marked unverified, last-known values retained as stale). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-14 02:32 WIB — run gagal baca (SILENT, no trigger)
- API https://agio.family/api/v1/launch/campaign: curl kosong (2× percobaan, timeout 20 dtk, tanpa HTTP status/body). Tidak terverifikasi.
- On-chain (agio_chain_check.py): semua 9 RPC gagal, last=timeout (180 dtk). Retry manual 3 endpoint (bsc.publicnode.com, bsc-dataseed1.bnbchain.org, bsc-dataseed2.binance.org) juga kosong/timeout 15 dtk.
- state.json TIDAK ditimpa (tidak ada state baru terverifikasi). State terakhir tetap 01:32 WIB 13/14 Nov: on-chain paused=true, opened=false, totalMinted=0, freeMintDone=false kedua task.
- Tidak ada trigger (a)/(b)/(c) yang bisa dinilai; tidak ada perubahan material terverifikasi. Lanjut run berikutnya.

## 2026-11-14 03:32 WIB — hourly run, SILENT (API 502, on-chain verified)
- API https://agio.family/api/v1/launch/campaign: TIDAK TERVERIFIKASI run ini (curl "error code: 502", HTTP 502 — 502 kedua berturut-turut setelah 01:32 WIB; run 02:32 WIB curl kosong). Last verified API state 23:32 WIB 13 Nov: opened=false, paused=false, totalMinted=1290.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133416401 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Read succeeded after the 02:32 WIB total read failure — confirms no on-chain change.
- No material change; no trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files (API marked unverified, last-known values retained as stale). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-14 04:32 WIB — hourly run
- API https://agio.family/api/v1/launch/campaign: NOT VERIFIED — curl returned empty response (3rd unverified run in last 4: 01:32 502, 02:32 empty, 03:32 OK, 04:32 empty). Last verified API state 23:32 WIB 13 Nov: opened=false, paused=false, available=true, totalMinted=1290, totalPaid=461000000000000000000.
- On-chain (block 133424797, eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR). UNCHANGED vs 03:32 WIB run.
- No trigger (a)/(b)/(c) met. SILENT per body. State saved to ~/workspace/agio-watch/state.json.

## 2026-11-14 05:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: NOT VERIFIED — curl returned HTTP 502 (4th unverified run in last 5: 01:32 WIB 502, 02:32 WIB empty, 03:32 WIB read succeeded, 04:32 WIB empty, 05:32 WIB 502). Last verified API state remains 23:32 WIB 13 Nov: opened=false, paused=false, available=true, totalMinted=1290, totalPaid=461e18, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133432363 (eth_call only): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED vs 04:32 WIB run.
- No trigger (a)/(b)/(c-new) met; on-chain opened=false confirms no launch opening. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirrors). No preview/mint/approve/sign/login; no execution authorised.
- 06:32 WIB 14 Nov: API https://agio.family/api/v1/launch/campaign HTTP 502 (body kosong, 5th unverified run in last 6). On-chain blok 133440452: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Tidak ada perubahan material; SILENT, tanpa trigger (a)/(b)/(c).

## 2026-11-14 07:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: NOT VERIFIED — curl returned HTTP 502 (body kosong, 6th unverified run in last 7: 01:32 WIB 502, 02:32 WIB empty, 03:32 WIB read succeeded, 04:32 WIB empty, 05:32 WIB 502, 06:32 WIB 502, 07:32 WIB 502). Last verified API state 23:32 WIB 13 Nov: opened=false, paused=false, available=true, totalMinted=1290, totalPaid=461e18, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133448739 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED vs 06:32 WIB run.
- No trigger (a)/(b)/(c) met; on-chain opened=false confirms no launch opening. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirrors). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-14 09:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: NOT VERIFIED — curl returned HTTP 502 (body kosong, 8th unverified run in last 9: 01:32 WIB 502, 02:32 WIB empty, 03:32 WIB read succeeded, 04:32 WIB empty, 05:32 WIB 502, 06:32 WIB 502, 07:32 WIB 502, 08:32 WIB 502, 09:32 WIB 502). Last verified API state 23:32 WIB 13 Nov: opened=false, paused=false, available=true, totalMinted=1290, totalPaid=461e18, totalShares=10000.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133464291 (read-only eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED vs 08:32 WIB run.
- No trigger (a)/(b)/(c) met; on-chain opened=false confirms no launch opening. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirrors). No preview/mint/approve/sign/login; no execution authorised.
- 10:32 WIB 14 Nov 2026 — SILENT. On-chain blok 133472312: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API via salinan crawl 10:12 WIB (blok 131898385): opened=false, paused=false, available=true, totalMinted=1284, totalPaid 457e18. Tidak ada perubahan material vs run 09:32 WIB; trigger (a)/(b)/(c) tidak terpenuhi. Divergensi API-vs-chain tetap ada, tidak ditafsir sebagai pembukaan launch. Tanpa preview/mint/sign/login.

## 2026-11-14 11:32 WIB — hourly run
- API (crawled copy 11:13 WIB, blok 131898385, sama seperti run sebelumnya): opened=false, paused=false, available=true, totalMinted=1284, totalPaid 457e18.
- On-chain (blok 133480371): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- Tidak ada perubahan material vs run 10:32 WIB; trigger (a)/(b)/(c) tidak terpenuhi → SILENT per body. State disimpan ke ~/workspace/agio-watch/state.json + hidden_files.
- Gap tetap: API totalMinted 1284 vs on-chain 0 belum terjelaskan; aktivitas API tidak ditafsir sebagai pembukaan launch.

## 2026-11-14 12:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: direct curl returned HTTP 502 this run; values from browser.open crawled copy (crawled 05:17 UTC / 12:17 WIB): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385 — UNCHANGED vs 11:32 WIB run (same block; copy appears stale).
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133488315 (eth_call only): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED.
- No trigger (a)/(b)/(c-new) met; trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. No preview/mint/approve/sign/login; no execution authorised. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies).

## 2026-11-14 13:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: direct curl HTTP 502 again (9th unverified run in last 10: 01:32 502, 02:32 empty, 03:32 OK, 04:32 empty, 05:32 502, 06:32 502, 07:32 502, 08:32 502, 09:32 502, 10:32 copy, 11:32 copy, 12:32 502, 13:32 502). Crawled copy 06:15 UTC / 13:15 WIB, block 131898385 (same, stale): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133496286 (eth_call only): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED vs 12:32 WIB run.
- No trigger (a)/(b)/(c) met. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. No preview/mint/approve/sign/login; no execution authorised. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files mirrors).

## 2026-11-14 14:32 WIB — hourly check (SILENT)
- On-chain (blok 133504362): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). TIDAK BERUBAH vs run 13:32 WIB.
- API: curl langsung HTTP 502; salinan crawl browser.open (07:19 UTC / 14:19 WIB, ~13 mnt sebelum run): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457 BNB, blok 131898385 (sama, tampak basi). Divergensi API-vs-chain tetap tidak dijelaskan; bukan pembukaan launch.
- Pemicu (a)/(b)/(c) tidak ada yang terpenuhi. DIAM. Tanpa preview/mint/approve/sign/login.
- 2026-11-14 15:32 WIB: SILENT. On-chain (blok 133512326): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API direct 502; crawled copy 15:23 WIB: opened=false, totalMinted=1284, blok 131898385 (stale, sama seperti run sebelumnya). Tidak ada trigger (a)/(b)/(c).

## 2026-11-14 16:32 WIB — hourly run
- API direct: HTTP 502 (curl). browser.open copy crawled 08:23 UTC / 15:23 WIB, block 131898385, opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18 — same stale copy as prior runs.
- On-chain (block 133520363): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change vs 15:32 WIB run; no trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.
- 2026-11-14 17:32 WIB: on-chain (blok 133528258) UNCHANGED: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API langsung 502 lagi; salinan crawl sama (blok 131898385, opened=false, totalMinted=1284) — stale. Tidak ada trigger (a)/(b)/(c). SILENT.
- 18:32 WIB 14 Nov 2026 — SILENT. On-chain blok 133536297: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API langsung 502 lagi; salinan crawl 18:16 WIB (blok 131898385, opened=false, totalMinted=1284) sama seperti run sebelumnya. Tidak ada trigger (a)/(b)/(c). State diperbarui.
- 19:32 WIB 14 Nov 2026 — SILENT. On-chain (blok 133544291): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API langsung 502 lagi; salinan crawl 18:16 WIB sama (opened=false, totalMinted=1284, blok 131898385). Tidak ada trigger (a)/(b)/(c).
---
2026-11-14 20:32 WIB — SILENT. On-chain block 133552268: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (both tasks). API direct 502; crawled copy 20:15 WIB same block 131898385, opened=false, totalMinted=1284 (stale, divergence persists). No trigger (a)/(b)/(c).

## 2026-11-14 21:32 WIB — agio-free-mint-watch (hourly)
- On-chain (blok 133560289): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false untuk REPOST_COMMENT dan AVATAR. Tidak berubah vs 20:32 WIB.
- API langsung masih HTTP 502; salinan crawled (21:15 WIB, blok 131898385, sama seperti run sebelumnya): opened=false, paused=false, available=true, totalMinted=1284. Divergensi API-vs-chain tetap belum dijelaskan; bukan pembukaan launch.
- Tidak ada trigger (a)/(b)/(c) — SILENT. State disimpan di ~/workspace/agio-watch/state.json.
2026-11-14 22:32 WIB — SILENT. On-chain blok 133568264: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API direct 502 lagi; salinan crawl 22:21 WIB: opened=false, totalMinted=1284, blok 131898385 (sama, tampak basi). Tidak ada trigger (a)/(b)/(c). Divergensi API-vs-chain tetap.

## 2026-11-14 23:32 WIB — hourly run
- On-chain (block 133576331): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED vs 22:32 run.
- API direct fetch HTTP 502 again; browser.open crawled copy unchanged (block 131898385, opened=false, totalMinted 1284). Stale copy; API-vs-chain divergence persists, not treated as launch.
- No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.

## 2026-11-15 00:32 WIB — hourly run
- On-chain (block 133584302): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED vs 23:32 WIB 14 Nov run.
- API direct fetch HTTP 502 again; browser.open crawled copy (00:14 WIB, block 131898385, opened=false, totalMinted 1284) same as prior runs, appears stale. API-vs-chain divergence persists, not treated as launch.
- No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.
- 2026-11-15 01:32 WIB — agio-free-mint-watch hourly: SILENT, no material change. On-chain (block 133592278): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Direct API fetch HTTP 502 again; browser.open copy stale (crawled 17:14 UTC, block 131898385, opened=false, totalMinted 1284) — same as prior runs. No trigger (a)/(b)/(c). No preview/mint/approve/sign/login.
- 2026-11-15 02:32 WIB — agio-free-mint-watch hourly: SILENT, no material change. On-chain (block 133600254): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Direct API fetch HTTP 502 again; browser.open copy crawled 02:20 WIB, same block 131898385, opened=false, totalMinted 1284 — stale, same as prior runs. No trigger (a)/(b)/(c). No preview/mint/approve/sign/login.

## 2026-11-15 03:32 WIB — agio-free-mint-watch (hourly)
- On-chain segar (blok 133608269): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false untuk REPOST_COMMENT dan AVATAR. Tidak berubah vs run 02:32 WIB.
- API langsung: HTTP 502 lagi; salinan crawl browser.open (20:13 UTC / 03:13 WIB) nilai sama: opened=false, paused=false, available=true, totalMinted=1284, blok 131898385. Divergensi API-vs-chain tetap belum terjelaskan; tidak ditafsir sebagai pembukaan launch.
- Tidak ada pemicu (a)/(b)/(c) — DIAM. Tidak ada preview/mint/approve/sign/login.

## 2026-11-15 04:32 WIB
- API direct curl: HTTP 502 (lagi). browser.open crawled copy 21:13 UTC: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385 — sama seperti run sebelumnya, tampak basi.
- On-chain (blok 133616326): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT & AVATAR). TIDAK BERUBAH vs 03:32 WIB.
- Tidak ada pemicu (a)/(b)/(c). SILENT. Tidak ada preview/mint/approve/sign/login.

## 2026-11-15 05:32 WIB (hourly)
- On-chain (blok 133624244): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). TIDAK BERUBAH vs 04:32 WIB.
- API https://agio.family/api/v1/launch/campaign: curl langsung HTTP 502 lagi; salinan crawl browser.open (22:13 UTC / 05:13 WIB) sama seperti run sebelumnya: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, blok 131898385 — tampak basi.
- Divergensi API-vs-chain (1284 vs 0) tetap tidak terjelaskan; tidak ditafsirkan sebagai pembukaan launch.
- Tidak ada trigger (a)/(b)/(c). SILENT. Tanpa preview/mint/approve/sign/login.

## 2026-11-15 06:32 WIB (hourly)
- On-chain (blok 133632275): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). TIDAK BERUBAH vs 05:32 WIB.
- API https://agio.family/api/v1/launch/campaign: curl langsung HTTP 502 lagi; salinan crawl browser.open (23:15 UTC / 06:15 WIB) sama seperti run sebelumnya: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, blok 131898385 — tampak basi.
- Divergensi API-vs-chain (1284 vs 0) tetap tidak terjelaskan; tidak ditafsirkan sebagai pembukaan launch.
- Tidak ada trigger (a)/(b)/(c). SILENT. Tanpa preview/mint/approve/sign/login.
- 2026-11-15 07:32 WIB: SILENT. On-chain (blok 133640274): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API direct curl 502 lagi; crawled copy 00:12 UTC (blok 131898385, opened=false, totalMinted=1284) — sama seperti run sebelumnya, tampak basi. Tidak ada trigger (a)/(b)/(c). State diperbarui di ~/workspace/agio-watch/state.json.
## 2026-11-15 08:32 WIB — agio-free-mint-watch (hourly, SILENT)
- On-chain (blok 133648251): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). TIDAK BERUBAH vs 07:32 WIB.
- API langsung: HTTP 502 lagi (curl). Salinan crawl browser.open 01:14 UTC / 08:14 WIB, blok sama 131898385: opened=false, paused=false, available=true, totalMinted=1284, totalPaid 457e18 — tampak basi, tidak ditafsirkan sebagai pembukaan launch.
- Trigger (a)/(b)/(c): tidak ada yang terpenuhi. DIAM per body. State disimpan ke ~/workspace/agio-watch/state.json (+ salinan hidden_files).


## 2026-11-15 11:32 WIB run
- API direct curl: HTTP 502 again. Crawled copy (04:16 UTC / 11:16 WIB): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457000000000000000000, block 131898385 — same as prior runs.
- On-chain (block 133672256): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false for both tasks (REPOST_COMMENT, AVATAR).
- No material change vs 10:32 WIB run. No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.
- Gap persists: API totalMinted 1284 vs on-chain 0, unexplained; API activity not treated as launch opening.
## 2026-11-15 12:32 WIB — hourly check (SILENT, no material change)
- On-chain (block 133680209, fresh eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Unchanged vs 11:32 WIB run.
- API direct curl: HTTP 502 again. Crawled copy (05:20 UTC / 12:20 WIB, block 131898385): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18 — same values/block as prior runs, stale.
- No trigger (a)/(b)/(c) met. No preview/mint/approve/sign/login; no execution authorised. State saved to ~/workspace/agio-watch/state.json and goal hidden_files copies.

## 2026-11-15 13:32 WIB — hourly check (SILENT, no material change)
- On-chain (block 133688214, fresh eth_call): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Unchanged vs 12:32 WIB run.
- API direct curl: HTTP 502 again. Crawled copy (06:15 UTC / 13:15 WIB, block 131898385): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18 — same values/block as prior runs, stale.
- No trigger (a)/(b)/(c) met. No preview/mint/approve/sign/login; no execution authorised. State saved to ~/workspace/agio-watch/state.json and goal hidden_files copies.


## Run 2026-11-15 14:32 WIB
- API (browser.open crawled copy 07:15 UTC / 14:15 WIB, block 131898385): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18 — same values/block as prior runs, appears stale.
- On-chain (block 133696218): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Unchanged vs 13:32 WIB run.
- No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.

## 2026-11-15 15:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: direct curl fetch returned HTTP 502 this run; values from browser.open crawled copy (crawled 2026-11-15 08:21 UTC / 15:21 WIB): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385 — same values/block as prior runs, appears stale.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133704223: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED vs 14:32 WIB run.
- No trigger (a)/(b)/(c-new) met. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copy). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-15 16:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: direct curl fetch returned HTTP 502 this run; values from browser.open crawled copy (crawled 2026-11-15 09:18 UTC / 16:18 WIB): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385 — same values/block as prior runs, appears stale.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133712201: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED vs 15:32 WIB run.
- No trigger (a)/(b)/(c) met. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-15 17:32 WIB
- On-chain (blok 133720197): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Tidak berubah vs run 16:32 WIB.
- API langsung: HTTP 502. Crawled copy browser.open (10:16 UTC): opened=false, paused=false, available=true, totalMinted=1284, blok 131898385 — sama seperti run sebelumnya, tampak basi.
- Tidak ada trigger (a)/(b)/(c). SILENT. State disimpan ke ~/workspace/agio-watch/state.json.
2026-11-15 18:32 WIB — on-chain UNCHANGED (blok 133728176): paused=true, opened=false, totalMinted=0, freeMintDone=false x2. API direct 502; crawled copy 11:14 UTC opened=false, totalMinted=1284 (stale, same block). No trigger → SILENT.
## 2026-11-15 21:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: direct curl fetch returned HTTP 502 this run; values from browser.open crawled copy (crawled 2026-11-15 14:15 UTC / 21:15 WIB): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385 — same values/block as prior runs, appears stale.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133752213: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — UNCHANGED vs 18:32 WIB run.
- No trigger (a)/(b)/(c) met. SILENT per body. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-15 22:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: direct curl HTTP 502 again; browser.open crawled copy (15:15 UTC / 22:15 WIB, block 131898385): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18 — unchanged vs 21:32 WIB run.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 133760276 (eth_call only): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged.
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. API-vs-chain divergence persists, unexplained, not interpreted as launch opening. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.
- 23:32 WIB 15 Nov: on-chain UNCHANGED (block 133768195): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API direct curl 502; crawled copy 16:14 UTC sama (opened=false, totalMinted=1284, block 131898385). No trigger (a)/(b)/(c). SILENT.
- 00:32 WIB 16 Nov: on-chain UNCHANGED (block 133776206): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API direct curl 502 (also agio.family homepage 502); crawled copy 17:16 UTC sama (opened=false, totalMinted=1284, block 131898385). No trigger (a)/(b)/(c). SILENT.
2026-11-16 01:32 WIB — run hourly: on-chain block 133784186: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). API direct curl HTTP 502; crawled copy 18:16 UTC (01:16 WIB) unchanged: opened=false, totalMinted=1284, block 131898385. No material change — SILENT, no trigger (a)/(b)/(c).

## 2026-11-16 02:32 WIB — hourly run
- On-chain (blok 133792191, segar): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). TIDAK BERUBAH vs run 01:32 WIB.
- API langsung: HTTP 502 (lagi). Crawled copy 19:18 UTC / 02:18 WIB: opened=false, paused=false, available=true, totalMinted=1284, blok 131898385 — nilai/blok sama seperti run sebelumnya, tampak basi.
- Divergensi API-vs-chain (1284 vs 0) tetap tidak terjelaskan; bukan tanda launch dibuka.
- Trigger (a)/(b)/(c): tidak ada. SILENT. Tanpa preview/mint/approve/sign/login.

## 2026-11-16 03:32 WIB
- API (crawled copy 20:22 UTC): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385 — same as prior runs, stale.
- On-chain (block 133800175): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR).
- No material change vs 02:32 WIB run. No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.

## 2026-11-16 04:32 WIB
- On-chain (block 133808166): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED vs 03:32 WIB.
- API: direct curl HTTP 502; browser.open crawled copy 21:17 UTC (04:17 WIB) — opened=false, paused=false, available=true, totalMinted=1284, block 131898385 (same stale block/values as prior runs).
- No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.

## 2026-11-16 05:32 WIB — hourly run
- On-chain (block 133816175): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Unchanged vs 04:32 run.
- API direct curl: HTTP 502 again. browser.open crawled copy (2026-11-15 21:17 UTC) identical to prior runs: opened=false, paused=false, totalMinted=1284, block 131898385 — stale, not live.
- API-vs-chain divergence persists (1284 vs 0), unexplained; not treated as launch opening.
- No trigger (a)/(b)/(c). SILENT. State updated at ~/workspace/agio-watch/state.json.

## 2026-11-16 07:32 WIB — hourly run
- API direct curl: HTTP 502 (still). Crawled copy 00:17 UTC / 07:17 WIB: opened=false, paused=false, available=true, block 131898385, totalMinted 1284, totalPaid 457e18 — same as prior runs.
- On-chain (block 133832185): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). Unchanged vs 06:32 WIB run.
- No trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json (+ hidden_files mirror).

## 2026-11-16 08:32 WIB — hourly run
- API: direct curl HTTP 502 (again); crawled copy 01:16 UTC / 08:16 WIB — opened=false, paused=false, available=true, block 131898385, totalMinted 1284, totalPaid 4.57e20. Same block/values as prior runs (stale).
- On-chain (block 133840191): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR). UNCHANGED vs 07:32 WIB run.
- No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login; no execution authorised.
- 2026-11-16 09:32 WIB run: on-chain UNCHANGED (block 133848201, paused=true, opened=false, totalMinted=0, freeMintDone=false both tasks). API direct curl HTTP 502 again; crawled copy 02:25 UTC same values (opened=false, totalMinted 1284, block 131898385, stale). No trigger (a)/(b)/(c). SILENT.

## 2026-11-16 10:32 WIB — hourly run
- READ FAILURE: direct API curl HTTP 000 (timeout 20s); on-chain check failed — all 9 BSC RPC endpoints timed out (~180s), 3 curl spot-checks empty. Egress degraded.
- API via browser.open crawled copy (03:16 UTC / 10:16 WIB): opened=false, paused=false, available=true, block 131898385, totalMinted 1284, totalPaid 457e18 — identical to prior runs, stale.
- On-chain NOT re-verified this run; prior values preserved in state.json (paused=true, opened=false, totalMinted=0, freeMintDone=false both). No trigger (a)/(b)/(c) confirmable from fresh data.
- Action: SILENT. No preview/mint/approve/sign/login. State preserved, not overwritten from empty.

## 2026-11-16 11:32 WIB — hourly run
- API: direct curl HTTP 502 (Cloudflare); crawled copy 03:16 UTC (stale ~8h): opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385 — unchanged vs prior runs.
- On-chain FRESH (block 133864610): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. Egress recovered (dataseed1.bnbchain + dataseed.binance OK; publicnode rate-limited -32005).
- No trigger (a)/(b)/(c). SILENT. State updated in ~/workspace/agio-watch/state.json. No preview/mint/approve/sign/login.
--- run-log ---
2026-11-16 12:32 WIB: SILENT. On-chain block 133872142: paused=true, opened=false, totalMinted=0, freeMintDone false (both tasks). API direct 502; crawled copy 04:35 UTC unchanged (opened=false, totalMinted 1284, block 131898385). No trigger (a)/(b)/(c).

## 2026-11-16 13:32 WIB
- API: direct curl empty (Cloudflare); crawled copy 04:35 UTC, unchanged: opened=false, paused=false, available=true, totalMinted 1284, block 131898385.
- On-chain (block 133880246): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false (REPOST_COMMENT + AVATAR).
- No material change vs 12:32 WIB run. SILENT, no trigger (a)/(b)/(c). No preview/mint/sign.

## 2026-11-16 14:32 WIB
- API: direct curl HTTP 502 (Cloudflare/edge); crawled copy 04:35 UTC, unchanged: opened=false, paused=false, available=true, totalMinted 1284, block 131898385.
- On-chain (block 133888145): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false (REPOST_COMMENT + AVATAR).
- No material change vs 13:32 WIB run. SILENT, no trigger (a)/(b)/(c). No preview/mint/sign.

## 2026-11-16 16:32 WIB — hourly run
- API direct curl: HTTP 502 (lagi). browser.open: salinan crawled 04:35 UTC (11:35 WIB), opened=false, paused=false, totalMinted 1284, block 131898385 — sama seperti run sebelumnya, stale.
- On-chain SEGAR (blok 133904155): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false.
- Tidak ada perubahan material vs run 15:32 WIB. Tidak ada trigger (a)/(b)/(c). SILENT. State disimpan ke ~/workspace/agio-watch/state.json (+ mirror hidden_files).

## 2026-11-16 17:32 WIB
- API: direct curl HTTP 502 (lagi); fallback browser.open copy crawled 04:35 UTC (11:35 WIB) — opened=false, totalMinted 1284, block 131898385, sama seperti run sebelumnya (stale).
- On-chain segar (blok 133912138): paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR).
- Tidak ada perubahan material vs run 16:32 WIB. SILENT, tanpa trigger (a)/(b)/(c). Tanpa preview/mint/sign/login.
- 2026-11-16 18:32 WIB: SILENT, no material change. On-chain fresh (block 133920446): paused=true, opened=false, totalMinted=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. API direct curl empty body (edge 502 pattern); crawled copy stale ~7h, unchanged (opened=false, totalMinted 1284, block 131898385). No trigger (a)/(b)/(c). No preview/mint/sign/login.
- 2026-11-16 19:32 WIB: SILENT. On-chain fresh (blok 133928142): paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502; crawled copy stale 04:35 UTC, unchanged (opened=false, totalMinted 1284). No trigger (a)/(b)/(c). No preview/mint/approve/sign/login.
- 2026-11-16 20:32 WIB — SILENT. On-chain segar blok 133936256: paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502 (pola sama); salinan crawled 04:35 UTC tidak berubah (opened=false, totalMinted 1284, blok 131898385, ~9 jam). Tanpa trigger (a)/(b)/(c). Tanpa preview/mint/approve/sign/login.
- 21:32 WIB 16 Nov 2026 — AGIO hourly watch: SILENT, no material change. On-chain fresh @ block 133944141: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502 (same pattern); crawled copy unchanged (opened=false, totalMinted 1284, block 131898385, ~10h old). No trigger (a)/(b)/(c). State saved to ~/workspace/agio-watch/state.json + goal hidden_files copy.
- 22:32 WIB AGIO watch: on-chain fresh block 133952156 — paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502 (same as prior runs); crawled copy stale ~11h (block 131898385, opened=false, totalMinted 1284). No material change, no trigger (a)/(b)/(c). SILENT.

## 2026-11-16 23:32 WIB
- API direct curl: 502 (same as prior runs). browser.open crawled copy still 2026-11-16 04:35 UTC, unchanged: opened=false, paused=false, available=true, totalMinted 1284, block 131898385.
- On-chain FRESH (block 133960140): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. No change vs 22:32 run.
- No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.
2026-11-17 00:32 WIB | on-chain block 133968133: paused=true, opened=false, totalMinted=0, freeMintDone false x2. API direct 502; crawled copy stale (block 131898385, opened=false, totalMinted 1284). No material change — SILENT.
--- run-log ---
- 2026-11-17 01:32 WIB: SILENT. On-chain (blok 133976111) paused=true, opened=false, totalMinted=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. API direct 502; crawled copy stale 2026-11-16 04:35 UTC (opened=false, totalMinted 1284) unchanged. No trigger (a)/(b)/(c).
- 02:32 WIB agio-free-mint-watch: on-chain segar blok 133984104 — paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API langsung curl 502 (pola sama); salinan crawled 2026-11-16 04:35 UTC tidak berubah (opened=false, totalMinted 1284, blok 131898385). Tidak ada perubahan material vs 01:32 WIB; DIAM, tanpa preview/mint/sign/login.
- 2026-11-17 03:32 WIB — AGIO watch hourly: SILENT, no material change. On-chain fresh @ block 133992119: paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502 (same pattern); crawled copy unchanged (opened=false, totalMinted 1284, block 131898385, ~16h old). No trigger (a)/(b)/(c). No preview/mint/approve/sign/login.
- 2026-11-17 04:32 WIB — AGIO watch hourly: SILENT, no material change. On-chain fresh @ block 134000159: paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502 (same pattern); crawled copy unchanged (opened=false, totalMinted 1284, block 131898385, ~17h old). No trigger (a)/(b)/(c). No preview/mint/approve/sign/login.
- 2026-11-17 05:32 WIB — AGIO watch hourly: SILENT, no material change. On-chain fresh @ block 134008115: paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502 (same pattern); crawled copy unchanged (opened=false, totalMinted 1284, block 131898385, ~18h old). No trigger (a)/(b)/(c). No preview/mint/approve/sign/login.
- 2026-11-17 06:32 WIB: SILENT. On-chain fresh block 134016139: paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502; crawled copy ~19h old unchanged (opened=false, totalMinted 1284, block 131898385). No trigger (a)/(b)/(c).

## 2026-11-17 07:32 WIB — hourly check (SILENT)
- On-chain fresh (block 134024111): paused=true, opened=false, totalMinted=0, totalPaid=0; freeMintDone false for REPOST_COMMENT and AVATAR.
- API direct curl 502 (same as prior runs); browser.open crawled copy unchanged, ~20h old (block 131898385, opened=false, totalMinted 1284).
- No material change vs 06:32 WIB run; no trigger (a)/(b)/(c). No preview/mint/approve/sign/login; no execution authorised.
- 2026-11-17 08:32 WIB: on-chain segar blok 134032107 — paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct 502 (pola lama); salinan crawled ~21 jam (blok 131898385, opened=false, totalMinted 1284) tidak berubah. Tidak ada perubahan material, DIAM.
- 09:32 WIB 17 Nov 2026 — AGIO watch hourly: SILENT. On-chain fresh blok 134040127: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502 (pola sama); salinan crawl 2026-11-16 04:35 UTC tidak berubah (opened=false, totalMinted 1284, blok 131898385). Tidak ada trigger (a)/(b)/(c). State: ~/workspace/agio-watch/state.json

## 2026-11-17 10:32 WIB — hourly check (SILENT)
- API https://agio.family/api/v1/launch/campaign: direct curl 502 (same pattern as prior runs). browser.open crawled copy still 2026-11-16 04:35 UTC (~23h old): available=true, opened=false, paused=false, totalMinted=1284, totalPaid 4.57e20, block 131898385 — unchanged, stale.
- On-chain FRESH (block 134048116): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. Unchanged vs 09:32 WIB run (block 134040127).
- No trigger (a)/(b)/(c). State saved to ~/workspace/agio-watch/state.json. No preview/mint/approve/sign/login; no execution authorised.
--- run log ---
- 2026-11-17 11:32 WIB: on-chain fresh block 134056134 — paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502; crawled copy unchanged (block 131898385, opened=false, totalMinted 1284, ~24h old). No material change — SILENT.
- 2026-11-17 12:32 WIB: on-chain segar blok 134064112 — paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false (REPOST_COMMENT + AVATAR). API langsung curl 502 (pola sama); salinan crawl browser.open tetap 2026-11-16 04:35 UTC (blok 131898385, opened=false, totalMinted 1284). Tidak ada perubahan material vs 11:32 WIB — DIAM, tanpa trigger (a)/(b)/(c). Tidak ada preview/mint/approve/sign/login.

## 2026-11-17 13:32 WIB — agio-free-mint-watch (hourly)
- On-chain segar (blok 134072106): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. Tidak ada perubahan vs run 12:32 WIB.
- API langsung: curl 502 (pola sama seperti run sebelumnya). Salinan crawled browser.open tetap 2026-11-16 04:35 UTC: opened=false, paused=false, totalMinted=1284, block 131898385 (~29 jam basi). On-chain otoritatif.
- Trigger (a)/(b)/(c): tidak ada. SILENT per body. Tidak ada preview/mint/approve/sign/login.
- 2026-11-17 14:32 WIB — on-chain segar blok 134080094: paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API langsung 502 (pola sama); salinan crawled 2026-11-16 04:35 UTC tidak berubah (opened=false, totalMinted 1284). Tidak ada perubahan material, DIAM.
- 2026-11-17 15:32 WIB: on-chain fresh block 134088102 — paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl 502; crawled copy unchanged (block 131898385, totalMinted 1284, opened=false, ~35h old). No material change vs 14:32 run; SILENT, no trigger (a)/(b)/(c).

## 2026-11-17 16:32 WIB — hourly run
- API direct curl: 502 (same pattern as prior runs). browser.open crawled copy unchanged (2026-11-16 04:35 UTC, block 131898385, opened=false, totalMinted 1284) — stale ~36h, not authoritative.
- On-chain FRESH (block 134096089): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. No change vs 15:32 WIB run.
- No trigger (a)/(b)/(c). SILENT. State updated in ~/workspace/agio-watch/state.json.
- 2026-11-17 17:32 WIB — SILENT. On-chain segar blok 134104088: paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. API langsung curl 502 (pola sama); salinan crawl browser.open tetap 2026-11-16 04:35 UTC (opened=false, totalMinted 1284, blok 131898385) — stale ~37 jam. Tidak ada perubahan vs run 16:32 WIB; trigger (a)/(b)/(c) tidak ada. State disimpan ke ~/workspace/agio-watch/state.json.
2026-11-17 18:32 WIB | block 134112087 | paused=true opened=false totalMinted=0 freeMintDone=false/false | API curl 502, crawled copy stale ~37h (opened=false, totalMinted 1284) | NO CHANGE, SILENT
2026-11-17 19:32 WIB | block 134120076 | on-chain paused=true opened=false totalMinted=0 freeMintDone false/false | API curl 502, crawled copy unchanged (2026-11-16 04:35 UTC, totalMinted 1284) | NO MATERIAL CHANGE -> SILENT
2026-11-17 20:32 WIB | block 134128074 | on-chain paused=true opened=false totalMinted=0 freeMintDone false/false | API curl 502, crawled copy unchanged (2026-11-16 04:35 UTC, totalMinted 1284) | NO MATERIAL CHANGE -> SILENT
2026-11-17 21:32 WIB | block 134136085 | on-chain paused=true opened=false totalMinted=0 freeMintDone=false/false | API curl 502, crawled copy unchanged (2026-11-16 04:35 UTC, totalMinted 1284) | NO MATERIAL CHANGE -> SILENT
2026-11-17 22:32 WIB | block 134144080 | on-chain paused=true opened=false totalMinted=0 freeMintDone=false/false | API curl 502, crawled copy unchanged (2026-11-16 04:35 UTC, totalMinted 1284) | NO MATERIAL CHANGE -> SILENT
2026-11-17 23:32 WIB — SILENT. On-chain fresh blok 134152067: paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct 502; crawled copy stale ~43h (blok 131898385, opened=false, totalMinted 1284). No trigger (a)/(b)/(c). No preview/mint/sign.
- 2026-11-18 00:32 WIB: SILENT. On-chain segar blok 134160085: paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT + AVATAR). API curl 502 (pola sama); salinan crawled 2026-11-16 04:35 UTC tidak berubah (opened=false, totalMinted 1284). Tanpa perubahan material; tanpa trigger (a)/(b)/(c).
2026-11-17 18:33:15 UTC | block 134168070 | paused=true opened=false totalMinted=0 | freeMintDone false/false | API curl 502, crawled copy stale ~45h (opened=false, totalMinted 1284) | NO MATERIAL CHANGE -> SILENT
- 2026-11-18 02:32 WIB: SILENT. On-chain fresh block 134176059: paused=true, opened=false, totalMinted=0, freeMintDone false (REPOST_COMMENT, AVATAR). API direct curl 502 (same pattern); crawled copy unchanged (2026-11-16 04:35 UTC, opened=false, totalMinted 1284, block 131898385). No trigger (a)/(b)/(c). State updated.

## 2026-11-18 03:32 WIB — hourly run
- On-chain FRESH (block 134184065): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. No change vs 02:32 WIB run (block 134176059 -> 134184065).
- API direct curl: 502 (same as prior runs). browser.open crawled copy unchanged (crawled 2026-11-16 04:35 UTC): opened=false, totalMinted=1284, block 131898385 — ~48h stale, not authoritative.
- No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login. State saved to ~/workspace/agio-watch/state.json (mirrored to hidden_files/state.json).

## 2026-11-18 04:32 WIB — hourly run
- On-chain FRESH (block 134192094): paused=true, opened=false, totalMinted=0, totalPaid=0; freeMintDone false for both tasks (REPOST_COMMENT, AVATAR).
- API direct curl: 502 (same as prior runs). browser.open crawled copy unchanged (crawled 2026-11-16 04:35 UTC): opened=false, totalMinted=1284, block 131898385 — ~2 days stale, not authoritative.
- No change vs 03:32 WIB run (block 134184065 -> 134192094). No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login. State saved to ~/workspace/agio-watch/state.json (mirrored to hidden_files/state.json + agio-watch-state.json).

## 2026-11-18 05:32 WIB — hourly check (SILENT)
- API direct curl: 502 (same as prior runs). Crawled copy (2026-11-16 04:35 UTC): opened=false, paused=false, available=true, totalMinted=1284, block 131898385 — unchanged, stale ~2 days.
- On-chain fresh (block 134200051): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false for both tasks (REPOST_COMMENT, AVATAR).
- No change vs 04:32 WIB run. No trigger (a)/(b)/(c). No preview/mint/approve/sign/login.

## 2026-11-18 06:32 WIB — hourly check (SILENT)
- API direct curl: 502 (same as prior runs). Crawled copy (2026-11-16 04:35 UTC): opened=false, paused=false, available=true, totalMinted=1284, block 131898385 — unchanged, stale ~2 days.
- On-chain fresh (block 134208087): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false for both tasks (REPOST_COMMENT, AVATAR).
- No change vs 05:32 WIB run (block 134200051 -> 134208087). No trigger (a)/(b)/(c). No preview/mint/approve/sign/login.
--- 2026-11-18 07:32 WIB ---
On-chain fresh (block 134216063): paused=true, opened=false, totalMinted=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. API direct curl 502 (same as before); crawled copy stale 2026-11-16 04:35 UTC, unchanged (opened=false, totalMinted 1284). No material change, no trigger (a)/(b)/(c). SILENT.
--- 2026-11-18 08:32 WIB ---
On-chain fresh (block 134224098): paused=true, opened=false, totalMinted=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. API direct curl 502 (same as before); crawled copy stale 2026-11-16 04:35 UTC, unchanged (opened=false, totalMinted 1284). No material change, no trigger (a)/(b)/(c). SILENT.

## 2026-11-18 09:32 WIB
- On-chain (block 134232049): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false (REPOST_COMMENT + AVATAR). Fresh read OK.
- API direct curl 502 (same pattern); crawled copy unchanged (2026-11-16 04:35 UTC, block 131898385, opened=false, totalMinted 1284, available=true).
- No material change vs 08:32 WIB run. No trigger (a)/(b)/(c). SILENT.

## 2026-11-18 10:32 WIB
- On-chain (block 134240063): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. No change vs 09:32 WIB run.
- API direct curl 502 (same pattern); crawled copy still 2026-11-16 04:35 UTC, opened=false, totalMinted 1284 — stale, unchanged.
- No trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json.

## 2026-11-18 11:32 WIB — hourly run
- On-chain fresh (block 134248035): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. No change vs 10:32 WIB run.
- API direct curl 502 (same pattern); browser.open crawled copy unchanged (2026-11-16 04:35 UTC, block 131898385, opened=false, totalMinted 1284) — stale ~2 days, on-chain authoritative.
- No trigger (a)/(b)/(c). SILENT, no report. State saved to agio-watch/state.json + goal hidden_files.

## 2026-11-18 12:32 WIB — hourly run
- On-chain fresh (block 134256161): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone REPOST_COMMENT=false, AVATAR=false. No change vs 11:32 WIB run.
- API direct curl HTTP 000 this run (connection failed; prior runs 502) — no fresh API data; crawled copy unchanged (2026-11-16 04:35 UTC, block 131898385, opened=false, totalMinted 1284) — stale ~2 days, on-chain authoritative.
- No trigger (a)/(b)/(c). SILENT, no report. State saved to agio-watch/state.json + goal hidden_files.

## 2026-11-18 13:32 WIB — hourly run
- On-chain (fresh, block 134264028): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false (REPOST_COMMENT + AVATAR).
- API direct curl: HTTP 502 (same as prior runs). Crawled copy (2026-11-16 04:35 UTC) unchanged: opened=false, totalMinted 1284, block 131898385 — stale ~2 days, on-chain authoritative.
- No material change vs 12:32 WIB run. No trigger (a)/(b)/(c). SILENT. No preview/mint/approve/sign/login.

## 2026-11-18 14:32 WIB — RUN GAGAL BACA (tidak ada data segar, state TIDAK ditimpa)
- API https://agio.family/api/v1/launch/campaign: curl timeout 20 dtk, HTTP 0 (tidak ada respons).
- On-chain via agio_chain_check.py: 9 RPC dataseed (urllib) SEMUA timeout (~180 dtk).
- Retry curl: bsc-dataseed1.bnbchain.org timeout 25 dtk; bsc.publicnode.com timeout 25 dtk (exit 28); bsc-dataseed2.binance.org timeout 15 dtk (exit 28).
- Quicknode helper (CONNECT tunnel): TimeoutError di sock.recv (~120 dtk).
- Kesimpulan: egress VM sedang flapping luas, bukan kegagalan AGIO spesifik. TIDAK ADA bukti perubahan status launch — juga TIDAK ADA bukti "tidak berubah". State terakhir yang terverifikasi tetap run 13:32 WIB (on-chain paused=true, opened=false, totalMinted=0, freeMintDone false keduanya; API crawled copy 16 Nov: opened=false, totalMinted 1284). State.json TIDAK ditimpa dari kosong, sesuai body. Tidak ada preview/mint/approve/sign/login. Lanjut run berikutnya.
- 2026-11-18 15:32 WIB: SILENT. On-chain fresh (blok 134280052): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false (REPOST_COMMENT + AVATAR). API direct curl HTTP 502 (same as prior runs); crawled copy ~2 days old unchanged (opened=false, totalMinted 1284, blok 131898385). No trigger (a)/(b)/(c). No preview/mint/sign/login.

## 2026-11-18 16:32 WIB — hourly run
- API direct curl: HTTP 000 (connection failed, no response; prior runs 502). browser.open: same stale crawled copy 2026-11-16 04:35 UTC (opened=false, paused=false, available=true, totalMinted 1284, block 131898385). No fresh API data.
- On-chain fresh (block 134288041, ~256s): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone false (REPOST_COMMENT + AVATAR).
- No change vs 15:32 WIB run. No trigger (a)/(b)/(c). SILENT. State saved to ~/workspace/agio-watch/state.json + goal hidden_files/state.json + goal agio-watch-state.json.

## 2026-11-18 18:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: direct curl TIMED OUT (HTTP 000, 30s) — no fresh data. browser.open crawled copy (2026-11-16 04:35 UTC) unchanged: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 134304436 (first attempt failed: all RPCs timed out ~181s; read-only retry succeeded ~271s): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged vs 17:32 WIB run (block 134296180 -> 134304436).
- No trigger (a)/(b); trigger (c) already reported once 2026-11-03 21:32 WIB. SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-18 19:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: direct curl TIMED OUT (HTTP 000, 30s) — no fresh data. browser.open crawled copy (2026-11-16 04:35 UTC) unchanged: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 134312615 (1st attempt: all RPCs timed out ~181s; 2nd attempt lost to service restart, outcome unknown; 3rd attempt succeeded in ~13s): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged vs 18:32 WIB run (block 134304436 -> 134312615).
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.

## 2026-11-18 20:32 WIB — hourly run, SILENT
- API https://agio.family/api/v1/launch/campaign: direct curl TIMED OUT (HTTP 000, 20s) — no fresh data. browser.open crawled copy (2026-11-16 04:35 UTC) unchanged: opened=false, paused=false, available=true, totalMinted=1284, totalPaid=457e18, block 131898385.
- On-chain mint 0xeF98407D55b3506275732b94c300866a16D6A3BB @ block 134320611 via Quicknode (7/7 calls, ~162s): paused=true, opened=false, totalMinted=0, totalPaid=0, freeMintDone=false (REPOST_COMMENT + AVATAR) — unchanged vs 19:32 WIB run (block 134312615 -> 134320611).
- Default dataseed path FAILED this run: agio_chain_check.py all 9 RPCs timed out (~180s); single curl to bsc.publicnode.com also timed out (15s). Egress to public BSC dataseeds flapping; Quicknode CONNECT tunnel unaffected — used as fallback this run.
- No trigger (a)/(b)/(c). SILENT per body. State saved to ~/workspace/agio-watch/state.json (+ goal hidden_files copies). No preview/mint/approve/sign/login; no execution authorised.
