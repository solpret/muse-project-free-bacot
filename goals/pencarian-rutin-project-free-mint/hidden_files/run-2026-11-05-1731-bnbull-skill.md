---
name: bnbull-mint
description: Mint BNB Bull (BNBULL) on BNB Chain. With a .ai Agent ID - 1 free share per ID through a global rate-limited slot (one free slot every 64 blocks ≈ 28.8 s, first come first served, no PoW) plus up to 20 paid shares at $2 each (BNB via Chainlink, no waiting); paying for ≥1 share lets the free share skip the slot queue. Without an Agent ID - paid only at $2.8 (1.4×), up to 20 per wallet. Read status() first, send only when the slot is open, retry on SlotNotOpen. Each share is a Pass NFT that claims BNBULL after launch (7,000 in total launches instantly; if free + paid reach 6,000 at the deadline the project launches within 7 days; without a launch, ≥ 2,000 paid means a paid Pass refunds 80% of what it paid, under 2,000 paid means no refund), earns BNB + BNBULL dividends and mines. After launch a 3,000-share ladder mint (mintAfter) opens.
---

# BNB Bull (BNBULL) — agent auto-mint guide · AI Agent 自动铸造指南

> **LIVE CONTRACT** 0x0cbc2c5f9c5bdac24d98e71bf173192692050946 on BNB Chain. Always double-check it against https://moomoo.cloud/bnbull/.

## Addresses · 地址 (BNB Smart Chain, chainId 56)

| what | address |
|---|---|
| AgentCoin5 (mint + ERC-20 BNBULL, name "BNB Bull") | `0x0cbc2c5f9c5bdac24d98e71bf173192692050946` |
| AgentPass5 (Pass NFT "BNB Bull Pass", BNBULLPASS) | `AgentCoin5.pass()` |
| .ai Agent ID registry | `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F` |
| Chainlink BNB/USD | `0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE` |

No function needs `approve`, `permit` or a signed message (only selling on PancakeSwap needs the usual router approval). 任何要你 approve / 签名的都是骗局。

## Rules · 规则（合约常量，部署后改不了）

| rule | value |
|---|---|
| Money · 钱 | **70% of the raise into the pool** (LP burned to `0x…dEaD`), **30% to the project** (fixed, paid at launch). Referral 5% comes out of the pool's 70% → pool gets 65–70%. If all paid minters sell with no new buyers (after the first 3 h), together they get back ≈ **42–44%** of the raise (fork-tested: 41.8–43.8% for 0–100% referral coverage, the same at a 6,000-total launch and a 7,000 sell-out) · 开池时募集 70% 进池、30% 项目方；推荐 5% 从进池扣；全卖约拿回 42–44% |
| Free · 免费 | 3,000 shares, **1 per Agent ID**, gas only, **no PoW** · 每个 Agent ID 1 份，只付 gas |
| Free pacing · 免费限速 | **1 global slot every 64 blocks** (≈ 28.8 s at 0.45 s/block), FCFS; unused slots do not accumulate · 全网每 64 块 1 个槽 |
| Paid · 付费 | 4,000 shares at **$2** each (one price, no tiers), paid in BNB at the Chainlink price; up to **20 per tx / 20 per Agent ID**, no rate limit · 付费 4,000 份，每份 $2 |
| No Agent ID · 无 ID | `mintPaidNoId`: **$2.8** a share ($2 × 1.4), **20 per wallet** (shared with the no-ID post-launch mint), no free share, no skip-the-queue, can't mine · 每份 $2.8，每钱包 20 份 |
| Skip the queue · 付费插队 | `mintPaidPlusFree` = ≥1 paid share + your free share in one tx, **no free-slot wait** (Agent ID only) |
| Referral · 推荐 | pass a referrer's Agent ID → referrer earns **5%** of your payment (out of the pool's 70%; your price and the project's 30% unchanged), claimable after launch, void if there is no launch. **Bonus**: when an invitee pays for the first time **with an Agent ID they own**, the referrer gets **+1 free share credit** (each Agent ID counts once, max **10** per referrer), minted with `mintRefBonus(qty)` during the mint window without waiting for a slot (comes out of the 3,000 free shares). No-ID payments earn the 5% but no credit · 推荐 5% + 持 ID 被邀请人首付送 1 份额度（上限 10） |
| Window · 时间 | 72 h from `startTime`. When free + paid reach **7,000** (everything sold), the pool launches in that same tx (the last share can be paid, a free slot or a bonus share). |
| Outcome · 结局 | At the deadline (`status.outcome`): free + paid ≥ **6,000** (`LAUNCH_LINE`) → only the project (the `treasury` address) can call `launch()`, within 7 days (outcome 0 until then, 1 after launch). Otherwise (under 6,000, or ≥ 6,000 but the project did not launch within 7 days) there is no pool and no token, and **paid shares** decide: paid ≥ **2,000** (`REFUND_LINE`) → outcome **2**: each paid Pass refunds **80%** of the BNB it paid (`refund`, rounded down, no deadline); the other 20% goes to the treasury via `sweepToTreasury()` (anyone, once). Paid **< 2,000** → outcome **3**: **no refund**; all raised BNB goes to the treasury via `sweepToTreasury()`. Without a launch, free / bonus shares, airdrop and mining give nothing and referral credits are void; no-ID buyers follow the same rules · 截止时满 6,000 份由项目方开池；7 天内未开池则按规则退款；没开池时付费 ≥2,000 份退实付 80%，<2,000 份不退款 |
| Launch · 开池 | PancakeSwap V2 BNBULL/WBNB, 70% of raised BNB minus referrals + tokens at a fixed open price $0.00004, LP burned |
| Each share · 每份 | 1 Pass NFT; paid Pass claims 60,000 BNBULL at launch; free Pass claims its share of 20% of pool tokens over 10 days (max 30,000 per share) |
| Other allocations · 其他 | project 30% of pool tokens (day 7 + 30-day linear) · airdrop 10% of pool tokens (wallet snapshot, 7-day linear) · mining pool 10% of pool tokens · free total 20% of pool tokens |
| Post-launch mint · 开池后铸造 | `mintAfter(agentTokenId or 0, qty)`: **3,000 shares** only (unsold paid shares at launch are void), $2.4 × 1.1^(k/500) per share (k = post-launch share #, so $2.4 → $3.87), × 1.4 without an ID; 60,000 BNBULL per share straight to the wallet, no Pass. 50% of each payment adds liquidity at the current pool price (LP burned), 50% to the project · 开池后只放 3,000 份 |
| Tax · 税 | **buy 2%** always · **sell 10% for the first 24,000 blocks after launch (≈ 3 h at 0.45 s/block, `status.earlyTaxEndBlock`), then 2% forever** · each tax take: **51% project, 24.5% burned, 24.5% to Pass holders in BNBULL** by weight · fixed, no other tax · first hour max sell per tx = 1% of pool tokens · wallet-to-wallet free. Sells must use `swapExactTokensForETHSupportingFeeOnTransferTokens` (or the other …SupportingFeeOnTransferTokens functions) with **≥12% slippage in the first 3 h, ≥3% after**; plain `swapExactTokensForETH` reverts · 买 2%；卖前 3 小时 10%、之后 2%；51% 项目方 / 24.5% 销毁 / 24.5% Pass |
| Mining · 挖矿 | mining pool = 10% of pool tokens, minted only when mined. One epoch = **32,000 blocks ≈ 4 h**; a wallet holding an Agent ID calls `mine(agentTokenId)` once per epoch (each wallet and each Agent ID once); output split by Pass hash power (plain 1, Miner 4; Passes received / fused this epoch count from the next); halves every **84 epochs ≈ 14 days**; epochs nobody mines are void |
| Project wallet · 项目方 | deployer = treasury = `0xD18D4AfB1F354BFf1ea4bcDC7a1799656A88CB93` |
| No owner · 无 owner（项目方只有开池权限） | no owner. The project (`treasury`, fixed at deployment) has exactly one right: `launch()` within 7 days after the deadline when free + paid ≥ 6,000; it cannot launch early, change parameters or take funds · 无 owner，项目方只有一个截止后开池的权限. No pause, blacklist, mint switch, tax / price change, discretionary withdraw, proxy. The only BNB-to-treasury function without a launch is `sweepToTreasury()` with a fixed amount (outcome 2: 20% of the raise; outcome 3: all) |

## agentTokenId

`agentTokenId = uint256(keccak256(bytes(label)))`, label = your name **without** `.ai`, lowercase.
Example `moomo` → `0x7853328984c9dd853b340320f72772c3ec38f8dd2a201852a448d374879faa6e`.
Check `ownerOf(agentTokenId)` on the registry == your sending wallet. No Agent ID → use `0` / the no-ID functions.

## Step 1 — read `status(wallet, agentTokenId)` first · 先读 status

One `eth_call` returns everything (struct of **53 fields**, in this order):

```
open, launched, refunding, currentBlock, startTime, endTime, launchDeadline,
freeMinted, freeSupply, paidSold, paidSupply, freeOpensAt, freeSlotBlocks, maxPaidPerTx,
refBps, refOwedWei, totalMinted, paidLeftAll, priceUsd, priceWei, raisedWei, raisedUsd,
toLaunchLine, refundedWei, eligible, agentIds, freeUsed, paidCount, paidLeft,
mineEpochNo, mineNextBlock, mineEpochReward, mineEpochPower, myPower, myHoldPower, myMinedPower,
minePendingAmt, mineAlloc, mined,
priceWeiNoId, noIdLeft, refBonusLeft, postCap, postSold, postPriceUsd, postPriceWei,
outcome, toRefundLine, refundableWei, sellTaxBps, buyTaxBps, earlyTaxEndBlock, refundBpsNow
```

- `status(address)` (selector `0x645b8b1b`) — global fields + `eligible` = wallet holds any Agent ID.
- `status(address,uint256)` (selector `0xadc25c01`) — also `eligible` for that ID, `freeUsed`, `paidCount`, `paidLeft`, and mining `mineNextBlock` for that ID.
- `freeOpensAt` = first block in which the next free slot can be taken. `currentBlock < freeOpensAt` → not open yet.
- `priceWei` / `priceWeiNoId` = BNB for the next paid share with / without an ID (0 = price feed stale, paid minting paused). For several shares use `quotePaid(qty)` (`0x63608c5c`) or `quotePaidNoId(qty)` (`0xb0007242`) → `(costWei, costUsd)` ($2 / $2.8 a share at the current Chainlink price).
- `noIdLeft` = no-ID shares this wallet can still buy. `refBonusLeft` = bonus free shares this wallet can mint.
- After launch: `postCap` (3,000), `postSold`, `postPriceUsd` / `postPriceWei` = next post-launch share; mining fields are filled.
- `totalMinted` = free + paid minted (the launch line counts this). `paidLeftAll` = paid shares left (4,000 − paidSold).
- `outcome`: 0 in progress (incl. ≥6,000 free + paid after the deadline, waiting for the project to call `launch()`), 1 launched, 2 80% refund, 3 no refund. `toLaunchLine` = free + paid still missing to 6,000; `toRefundLine` = **paid** shares still missing to 2,000. `refunding` = (outcome == 2).
- `refundBpsNow` = refund rate if it ended without a launch at the current paid count: 8,000 (paid ≥ 2,000) or 0 (paid < 2,000); 0 after launch. `refundableWei` = this wallet's paid Passes' paid amount × `refundBpsNow` (0 after launch). Contract view `refundBps()` returns the same rate.
- `sellTaxBps` / `buyTaxBps` = current tax (1,000 / 200 in the first 3 h, then 200 / 200; 0 before launch); `earlyTaxEndBlock` = first block with the 2% sell tax.

cast:
```
cast call 0x0cbc2c5f9c5bdac24d98e71bf173192692050946 "status(address,uint256)((bool,bool,bool,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,bool,uint256,bool,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint8,uint256,uint256,uint256,uint256,uint256))" <WALLET> <AGENT_TOKEN_ID> --rpc-url https://bsc-dataseed.bnbchain.org
```

## Step 2 — wait for the slot, then send · 等到开放的块再发

**Free · 免费** (`eligible && !freeUsed && freeMinted < freeSupply && open`):
1. Read `freeOpensAt` and `block.number`.
2. Sleep `(freeOpensAt − block − 1) × 0.45 s`. When `block ≥ freeOpensAt − 1`, send:
   `mintFree(uint256 agentTokenId, uint256 refAgentId)` selector `0xa6c5b6bc`, value 0, gas limit 300,000 — but if `freeMinted + paidSold ≥ 6,990` use 4,500,000: the 7,000th share (free + paid) launches the pool inside that tx (≈ 4M gas).
3. Receipt reverted with `SlotNotOpen(uint256 opensAtBlock)` (`0x8115c781`) → someone took the slot first. Re-read status and wait for the new `freeOpensAt`. A lost race costs ≈ 42,000 gas (≈ 0.000002 BNB at 0.05 gwei).

**Do not spam.** Send **one** tx per slot. Never send while `block < freeOpensAt − 1`. 每个槽只发一笔，没到块不要发。

**Paid · 付费** (only if your human told you a number · 只在主人给了份数时):
- With an ID: `mintPaid(uint256 agentTokenId, uint256 qty, uint256 refAgentId)` selector `0x2799367b`, value = `quotePaid(qty).costWei` (+1–3% buffer is fine, any excess is refunded in the same tx). No waiting.
- **Skip the free queue · 插队**: `mintPaidPlusFree(uint256 agentTokenId, uint256 qty, uint256 refAgentId)` (`0x7c436b6f`) — same value as `mintPaid`; also mints your free share if this ID has not claimed it and free shares remain. Only if your human agreed to pay.
- **No Agent ID · 无 ID**: `mintPaidNoId(uint256 qty, uint256 refAgentId)` (`0x8d91f630`), value = `quotePaidNoId(qty).costWei` (+buffer). Max 20 per wallet.
- **Referral bonus · 邀请奖励**: if `refBonusLeft > 0` during the mint window, `mintRefBonus(uint256 qty)` (`0x5a781ac6`), value 0, mints that many free Passes without waiting for a slot.

`refAgentId` = the Agent ID of whoever referred you (0 = none). Not your own ID, not an ID in your own wallet (those are ignored).

## Step 3 — errors · 错误

| error | selector | meaning · 意思 | what to do |
|---|---|---|---|
| `SlotNotOpen(uint256)` | `0x8115c781` | free slot not open / taken · 槽没开或被抢 | wait for `freeOpensAt`, retry once |
| `AlreadyFree()` | `0xa78fa27a` | this ID already claimed free · 已领过免费 | stop free |
| `FreeSoldOut()` | `0x236394f4` | 3,000 free gone · 免费抢完 | stop free (paid still open) |
| `NotAgentOwner()` | `0x390772fc` | wallet ≠ ownerOf(id) | use the wallet that owns the ID |
| `QuotaExceeded()` | `0x04e22101` | > 20 paid for this ID / no-ID wallet, or qty 0 | lower qty |
| `TooManyPerTx()` | `0x7275e2eb` | qty > 20 | lower qty |
| `Underpaid()` | `0x949ce241` | value < cost | re-quote |
| `StaleFeed()` | `0xa0cd3bb2` | Chainlink > 1 h old, paid paused | retry later |
| `SoldOut()` | `0x52df9fe5` | 4,000 paid gone / 3,000 post-launch gone | stop |
| `NotStarted()` / `MintClosed()` | `0x6f312cbd` / `0x589ed34b` | before start / after end or launched | check `startTime` / `endTime` |
| `NotLaunched()` | `0x8dda39df` | `mintAfter` before launch | wait for launch |
| `AlreadyMined(uint256)` | `0x51d26824` | this wallet or ID already mined this epoch | wait for the block in the error |
| `NoPower()` | `0xab68ecfc` | no usable hash power this epoch | hold Passes from before this epoch |
| `SellTooLarge()` | `0x8e4d208f` | first-hour sell > 1% of pool tokens | split the sell |
| `NothingToDo()` | `0x5c52a868` | nothing to claim / refund / launch / sweep | stop |
| `NotTreasury()` | `0xb90cdbb1` | `launch()` sent by anyone other than the project (`treasury`) | only the project can launch; wait |
| `MintClosed()` on `refund` | `0x589ed34b` | not in 80%-refund mode (launched, still open / waiting for launch, or < 2,000 paid = no refund) | check `status.outcome` |

## Auto-grab scripts · 自动抢槽脚本

Both scripts: read status → sleep until `freeOpensAt − 1` → send one tx → on `SlotNotOpen` re-read and wait → stop on success, `AlreadyFree`, `FreeSoldOut` or mint closed. They never send more than one tx per slot.
两个脚本：读 status → 睡到 `freeOpensAt − 1` → 发一笔 → 抢输了重新读、等下一个槽 → 成功 / 已领 / 抢完 / 截止就停。每个槽最多一笔。

### A. cast + bash ([`grab.sh`](https://moomoo.cloud/bnbull/grab.sh))

```bash
#!/usr/bin/env bash
# usage: COIN=0x0cbc2c5f9c5bdac24d98e71bf173192692050946 AID=<agentTokenId> ACCOUNT=<cast keystore name> [REF=<refAgentId>] ./grab.sh
# sends only when the slot opens, one tx per slot; stops when minted / already claimed / sold out
set -u
RPC=${RPC:-https://bsc-dataseed.bnbchain.org}
REF=${REF:-0}
while :; do
  live=$(cast call $COIN "isMintLive()(bool)" --rpc-url $RPC) || { sleep 2; continue; }
  [ "$live" = true ] || { echo "mint not live"; sleep 30; continue; }
  [ "$(cast call $COIN 'freeClaimed(uint256)(bool)' $AID --rpc-url $RPC)" = true ] && { echo "free already claimed"; exit 0; }
  fm=$(cast call $COIN "freeMinted()(uint256)" --rpc-url $RPC | cut -d' ' -f1)
  [ "$fm" -ge 3000 ] && { echo "free sold out"; exit 0; }
  opens=$(cast call $COIN "freeOpensAt()(uint256)" --rpc-url $RPC | cut -d' ' -f1)
  blk=$(cast block-number --rpc-url $RPC)
  if [ "$blk" -lt $((opens - 1)) ]; then
    sleep $(echo "($opens - $blk - 1) * 0.45" | bc); continue
  fi
  pd=$(cast call $COIN "paidSold()(uint256)" --rpc-url $RPC | cut -d' ' -f1)
  gl=300000; [ $((fm + pd)) -ge 6990 ] && gl=4500000   # the 7,000th share (free + paid) launches the pool in the same tx (~4M gas)
  out=$(cast send $COIN "mintFree(uint256,uint256)" $AID $REF --account $ACCOUNT --gas-limit $gl --rpc-url $RPC --json 2>&1)
  if echo "$out" | grep -q '"status":"0x1"'; then echo "minted: $(echo "$out" | jq -r .transactionHash)"; exit 0; fi
  echo "lost the slot, waiting for the next one"; sleep 1
done
```

Binance Agentic Wallet users: build calldata with `cast calldata "mintFree(uint256,uint256)" <AID> 0` and send it through your wallet's contract-call preview → execute at the same moment (value 0).
币安 Agentic Wallet：用 `cast calldata` 生成 calldata，到点时走 contract-call preview → execute（value 0）。

### B. ethers v6 ([`grab.mjs`](https://moomoo.cloud/bnbull/grab.mjs))

```js
// npm i ethers ; COIN=.. AID=.. PK=.. node grab.mjs   (PK = the key of the wallet that owns the Agent ID)
import { ethers } from "ethers";
const p = new ethers.JsonRpcProvider(process.env.RPC || "https://bsc-dataseed.bnbchain.org");
const w = new ethers.Wallet(process.env.PK, p);
const S = "tuple(bool open,bool launched,bool refunding,uint256 currentBlock,uint256 startTime,uint256 endTime,uint256 launchDeadline,uint256 freeMinted,uint256 freeSupply,uint256 paidSold,uint256 paidSupply,uint256 freeOpensAt,uint256 freeSlotBlocks,uint256 maxPaidPerTx,uint256 refBps,uint256 refOwedWei,uint256 totalMinted,uint256 paidLeftAll,uint256 priceUsd,uint256 priceWei,uint256 raisedWei,uint256 raisedUsd,uint256 toLaunchLine,uint256 refundedWei,bool eligible,uint256 agentIds,bool freeUsed,uint256 paidCount,uint256 paidLeft,uint256 mineEpochNo,uint256 mineNextBlock,uint256 mineEpochReward,uint256 mineEpochPower,uint256 myPower,uint256 myHoldPower,uint256 myMinedPower,uint256 minePendingAmt,uint256 mineAlloc,uint256 mined,uint256 priceWeiNoId,uint256 noIdLeft,uint256 refBonusLeft,uint256 postCap,uint256 postSold,uint256 postPriceUsd,uint256 postPriceWei,uint8 outcome,uint256 toRefundLine,uint256 refundableWei,uint256 sellTaxBps,uint256 buyTaxBps,uint256 earlyTaxEndBlock,uint256 refundBpsNow)";
const c = new ethers.Contract(process.env.COIN, [
  `function status(address,uint256) view returns (${S})`,
  "function mintFree(uint256,uint256) returns (uint256)",
  "error SlotNotOpen(uint256 opensAtBlock)", "error AlreadyFree()", "error FreeSoldOut()",
], w);
const AID = BigInt(process.env.AID), REF = BigInt(process.env.REF || 0);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
for (;;) {
  const s = await c.status(w.address, AID);
  if (!s.open) { console.log("mint not live"); await sleep(30_000); continue; }
  if (!s.eligible) throw new Error("wallet does not own this Agent ID");
  if (s.freeUsed || s.freeMinted >= s.freeSupply) { console.log("done / sold out"); break; }
  const wait = Number(s.freeOpensAt) - Number(s.currentBlock) - 1;
  if (wait > 0) { await sleep(wait * 450); continue; }
  try {
    // the 7,000th share (free + paid) launches the pool in the same tx (~4M gas): raise the limit near the end
    const gl = s.paidSold + s.freeMinted >= 6990n ? 4_500_000 : 300_000;
    const tx = await c.mintFree(AID, REF, { gasLimit: gl });
    const rc = await tx.wait();
    console.log("minted in block", rc.blockNumber, tx.hash); break;
  } catch (e) {
    const err = c.interface.parseError(e?.data ?? e?.info?.error?.data ?? "0x");
    if (err?.name === "SlotNotOpen") { console.log("lost slot, next opens at", err.args[0].toString()); await sleep(450); continue; }
    if (err?.name === "AlreadyFree" || err?.name === "FreeSoldOut") { console.log(err.name); break; }
    console.log("error, retry in 3 s:", e.shortMessage || e.message); await sleep(3000);
  }
}
```

## After the mint · 铸完之后

**Launch · 开池**
- When free + paid reach 7,000 (`TOTAL_SHARES`), the mint tx with the last share launches the pool; 30% of the raise goes to the treasury in the same tx.
- Otherwise: If free + paid reach 6,000 at the deadline, the project launches the pool; if it does not launch within 7 days, refunds follow the rules. · 截止时满 6,000 份由项目方开池；7 天内未开池则按规则退款。Only the project (`treasury` = `0xD18D4AfB1F354BFf1ea4bcDC7a1799656A88CB93`) may call `launch()` (`0x01339c21`), after `endTime` and before `launchDeadline` (= endTime + 7 days), if `freeMinted + paidSold ≥ 6,000` (`LAUNCH_LINE`); anyone else gets `NotTreasury()`.
- No launch (free + paid < 6,000 at the deadline, or ≥ 6,000 and the project did not launch within 7 days): `outcome == 2` if paid ≥ 2,000 (`REFUND_LINE`) → 80% refund, see below; `outcome == 3` if paid < 2,000 → no refund.

**Claim tokens · 领币（分批）** — `claimTokens(uint256[] passIds)` (`0x2d08265a`), only after launch, no approve.
- Pass ids: `AgentPass5.tokensOf(wallet)` (`0x5a3f2672`). Per Pass: `info(id)` (`0x2e340599`) → `(paid, pShares, fShares, units, miner, fClaimed)`; `listings(id)` (`0xde74e57b`) → `(seller, price, nonce)` (listed Passes can't claim: cancel first).
- Paid shares pay `pShares × 60,000` BNBULL in full; free shares pay `fShares × freeVestedPerShare() − fClaimed` (10-day linear, call again later for the rest).
- **Batch it:** ≈ 15,600 gas per Pass. Send **≤ 200 ids per tx**; 4,000 paid Passes = 20 txs. A Pass with nothing left is skipped, so re-running a batch never pays twice; if a whole batch has nothing it reverts `NothingToDo`.

**Dividends · 分红（BNB + BNBULL）** — `AgentPass5.claim(uint256[] ids)` (`0x6ba4c138`) pays both in one tx: BNB from the 1% Pass market fee (`pendingDividends(id)` `0x67b488a4` + `owed(wallet)` `0xdf18e047`) and BNBULL from 24.5% of every buy / sell tax take (`pendingTokDividends(id)` `0x840d2f1f` + `owedTok(wallet)` `0xe034f3cc`). Weight: plain 1, Miner 4. ≤ 300 ids per tx.

**Post-launch ladder mint · 开池后阶梯铸造** — `quotePost(uint256 qty, bool noId)` (`0x739307a6`) → `(costWei, costUsd)`; `mintAfter(uint256 agentTokenId, uint256 qty)` (`0x9f95f83c`) with value = cost (+buffer). `agentTokenId = 0` → no-ID price ×1.4, shares the 20-per-wallet no-ID cap; with an ID you must own it, no per-ID cap, ≤ 20 per tx. Tokens arrive directly. Compare with the pool price first: if 60,000 BNBULL is cheaper in the pool, buy there.

**Pass mining · Pass 挖矿** — `mine(uint256 agentTokenId)` (`0x4d474898`) from the wallet that owns the ID, once per epoch (read `mineNextBlock` from `status(wallet, id)`; `= currentBlock` means now). It registers `myPower` for this epoch and settles your previous epoch. `claimMined(address wallet)` (`0xbcf283b9`) settles the last epoch for anyone (tokens go to that wallet). `minePending(wallet)` (`0xa83a84f6`), `epochReward(epoch)` (`0x30da5240`), `mineEpoch()` (`0x22c4e1a1`).

**Refund · 退款 80%（分批）** — only when `outcome() == 2` (`0x27793f87`; `refundMode()` is the same check): `refund(uint256[] passIds)` (`0xaa613df5`) pays back 80% of the BNB those paid Passes paid (incl. the 1.4× no-ID price) and burns them. Free Passes return 0 (skip them). **≤ 100 ids per tx.** No deadline. With `outcome == 3` (no launch, paid < 2,000) refund reverts `MintClosed` — there is no refund. In outcome 2 or 3 anyone may call `sweepToTreasury()` (`0x362433ca`) once: it sends 20% of the raise (outcome 2) or all of it (outcome 3) to the treasury; it does not touch the 80% kept for refunds. Referral credits are void without a launch.

**Referral payout · 推荐返佣** — `refOwed(wallet)` (`0x9419e37d`); after launch `claimReferral()` (`0xe02f1ebd`). Bonus credits: `refBonus(wallet)` (`0x4d41d519`), earned so far `refBonusEarned(wallet)` (`0x203b7327`).

**Airdrop · 空投** — 10% of pool tokens, wallet snapshot (Merkle). Look up your entry in `https://moomoo.cloud/bnbull/airdrop.json` (`entries: [{ wallet, share, proof }]`, `share` in 1e18 = 100% of the airdrop; published before deployment), then after launch `claimAirdrop(uint256 share, bytes32[] proof)` (`0x0bcae1ac`). `airdropOf(wallet, share)` (`0x4a4d5afd`) = claimable now (7-day linear). No registration, never expires.

**Pass NFT (AgentPass5 = `AgentCoin5.pass()`)**
- Market (no approvals, Pass stays in your wallet, locked while listed): `list(uint256 id, uint256 priceWei)` (`0x50fd7367`), `cancel(uint256 id)` (`0x40e58ee5`), `buy(uint256 id, uint256 nonce)` (`0xd6febde8`) with `value = price` and the `nonce` you read from `listings(id)` — if the seller relisted (e.g. after claiming), the nonce changes and the buy reverts `ListingChanged` instead of buying an empty Pass. Fee 2%: 1% to Pass holders by weight, 1% to the project. External royalty (ERC-2981) 5%.
- Fuse 3 → 1 Miner: `fuse(uint256[3] ids)` (`0x07565a23`). Dividend weight and hash power 3 → 4; unclaimed shares, free-claim progress, refundable BNB and unclaimed dividends carry over. Miners can't be fused again.

**Selling BNBULL · 卖出** — PancakeSwap V2 router, `swapExactTokensForETHSupportingFeeOnTransferTokens` (or the token→token variant), slippage **≥ 12% while `block.number < earlyTaxEndBlock`** (10% tax for the first 24,000 blocks ≈ 3 h), ≥ 3% after (2% tax + fee + price move); `sellTaxBps()` (`0xcffd129c`) returns the current rate. First hour after launch: one sell ≤ `maxSell()` (`0xb8eb3546`) = 1% of pool tokens. Buys: 2% tax, slippage ≥ 3%.

**Team vesting · 项目方释放** — 30% of pool tokens, 30-day linear starting day 7 after launch; anyone can call `releaseTeam()` (`0x4dbc355a`), tokens go to the treasury.

## Honest notes · 说明

- The slot race only decides **who mints first**. It does not change prices, the 70/30 split or launch rules, and a fast-moving mint counter does not mean the paid shares will sell out.
  抢槽只决定谁先铸到，不改变价格、分成和开池规则；铸造数跳得快不代表付费会卖满。
- The open price is a starting price, not a sell price: paid tokens are 1.7–1.8× the pool's tokens. Selling ≈ 5.3–5.7% of paid tokens drops the price below the $2 cost. The first 3 h sell tax is 10%.
  开盘价不等于可卖价：付费代币卖掉约 5.3–5.7% 就跌破 $2 成本；前 3 小时卖税 10%。
- Without a launch: ≥ 2,000 paid → you get back 80% of what you paid; under 2,000 paid → nothing back, everything goes to the project. 1,999 vs 2,000 paid is a cliff: one more $2 share before the deadline switches every paid minter from 0% to 80%.
  没开池：付费 ≥2,000 份退实付 80%；不足 2,000 份不退款，全部归项目方。1,999 和 2,000 份只差 1 份，截止前补 1 份就能把全体付费者从不退变成退 80%。
- Free shares count toward the 6,000 launch line, so free slots alone (gas only) can push the total over the line. Someone with several Agent IDs can refer themselves from a second wallet for the 5% and the bonus credits.
  免费份算进 6,000 开池线，只靠免费槽（只付 gas）也能把合计推过线。有多个 Agent ID 的人可以从第二个钱包推荐自己，拿 5% 返佣和免费额度。
- The post-launch mint adds up to 180M tokens; arbitrageurs mint and sell whenever the pool is above the ladder.
  开池后铸造最多再加 1.8 亿枚，池子价高于阶梯价时会被套利者铸了就卖。
- Experimental token, not investment advice. 实验性代币，不是投资建议。

## Prompt for humans · 给主人用的一句话

> Read https://moomoo.cloud/bnbull/skill.md and mint BNB Bull for me on BNB Chain. Claim my free share with mintFree() using my Agent ID: read status() first, wait until the free slot opens, send one tx per slot and retry on SlotNotOpen. Only buy paid shares if I give you a number, never more than 20, and never pay more than the quote. If I have no Agent ID, only use mintPaidNoId with the number I give you. Report the tx hash and Pass ids.
>
> 读 https://moomoo.cloud/bnbull/skill.md，用我的 Agent ID 在 BNB Chain 帮我铸 BNB Bull 免费份：先读 status()，等免费槽开放再发，一个槽只发一笔，抢输了等下一个槽。我给了份数才买付费，最多 20 份，付款不超过报价。我没有 Agent ID 时只用 mintPaidNoId，按我给的份数买。告诉我交易哈希和 Pass 编号。
