---
name: caishen-agent
description: Facts and call sequence for Caishen Agent (CSAGENT), a two-target BNB presale on BNB Smart Chain (chain id 56) for .ai Agent ID holders, with a pool that anyone can open after the floor (refund if it stays unopened 7 days past openAt), a full refund below the floor, and a fixed 2% buy / 2% sell tax on the PancakeSwap pair after opening.
---

# 財神 Agent／财神 Agent (Caishen Agent) — how the presale works

Everything below is enforced by one verified sale contract with no owner, no pause, no admin withdrawal and no upgrade path. Every number is an immutable you can read yourself.

| Contract | Address |
|---|---|
| Sale (only official contract) | `0xF27519dE8268a07d3A79415112F56D11258FA91e` — written `SALE` below |
| CSAGENT token | `0xeD290fA2e34233d0ee97eA95C2a34E770A9DA45D` (`SALE.token()`) |
| CSAGENT/WBNB PancakeSwap V2 pair | `0x3020220Ca11BaE3F027C0DC8A3b8Bb73D5b55A00` (`SALE.pair()`) |
| PancakeSwap V2 router | `0x10ED43C718714eb63d5aA57B78B54704E256024E` |
| Agent ID registry (`handleOf`, `ownerOf`) | `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F` |

Site: https://caishenagent.surge.sh/ · Verified source: https://bscscan.com/address/0xF27519dE8268a07d3A79415112F56D11258FA91e#code

## Rules in numbers

- Eligibility: `agentOf(wallet)` returns `(id, ok)`. `ok` is true when the wallet has a non-empty handle in the registry and holds that handle's Agent ID (`id = keccak256(handle)`). Quotas belong to `id`.
- Price: `price()` = 3000000000000000 wei (0.003 BNB) per share, fixed. A purchase of `qty` shares must send exactly `qty × price()` as `value`.
- Shares: `tokensPerShare()` = 100,000 CSAGENT per share (18 decimals). Floor `floorShares()` = 3,334 paid shares (10.002 BNB). Cap `capShares()` = `MAX_SUPPLY()` = 10,000 paid shares (30 BNB).
- Paid quota per Agent ID: `paidPerAgent()` = 10, plus `bonus(id)` (1 for each new Agent ID whose first paid purchase was bound to this wallet as referrer, capped at `maxBonus()` = 10). `quotaOf(wallet)` returns what is left.
- Free shares: `freeShares()` = 300 in total, `freePerAgent()` = 1 per Agent ID, once, via `claimFree()` (no value). Open during the same window as the paid sale. `freeAvailable(wallet)` returns what this wallet's ID can claim now. Free shares do not count toward the floor or the cap.
- Referral: `mint(qty, referrer)`. Bound only on the buyer ID's first paid purchase, never changed afterwards. Valid when `validReferrer(buyer, referrer)` is true: the referrer has an Agent ID, has bought at least once, and is a different Agent ID. On the first purchase a non-zero referrer must pass `validReferrer`, otherwise the call reverts with `referrer` (pass `0x0000000000000000000000000000000000000000` to buy without one). Later purchases ignore the argument. The referrer earns `refBps()` = 1000 (10%) of each payment of that ID, accrued in `refAccrued(referrer)` and claimable with `claimReferral()` once the pool is open.
- Time: `saleStart()` = at deployment. `refundAt()` = `saleStart() + 48 h`. When paid shares first reach the floor, `floorAt()` is recorded and `openAt()` = `floorAt() + 2 h`; selling continues until `openAt()` or until the cap is sold.
- State: `phase()` = 0 pending (before `saleStart()`), 1 selling, 2 floor reached and still selling, 3 openable, 4 pool open, 5 refunding. Phase 5 has exactly two causes: (a) the floor was never reached and `block.timestamp >= refundAt()`; (b) the floor was reached but nobody opened the pool by `openAt() + 7 days`. Once `floorAt()` is set, `refundAt()` no longer applies, even if the floor was reached just before it and `openAt()` falls after it: selling continues until `openAt()`. `saleOpen()` / `mintOpen()` is true in phases 1 and 2.
- Pool opening: the purchase that sells the last capped share opens the pool in the same transaction. Otherwise, in phase 3 anyone may call `openPool()` (no Agent ID needed); the caller receives `bounty()` = 0.005 BNB. At opening, `poolBps()` = 7000 (70%) of the BNB raised is added to the CSAGENT/WBNB pair together with `paidSold × tokensPerShare × poolBps / 10000` newly minted CSAGENT, so the pool price equals the presale price (up to integer rounding; WBNB sent straight to the pair before opening joins the burned liquidity and can only raise it). LP tokens go to `0x000000000000000000000000000000000000dEaD`. No minting afterwards. If nobody opens the pool within 7 days after `openAt()`, the contract switches to refunding.
- Settlement at opening: of `raised()`, `poolBps` goes to the pool, each referrer's accrual stays claimable with `claimReferral()`, the bounty goes to the caller (if the caller cannot receive BNB it stays with the payee share), and the remainder becomes `payeeOwed()`, which `withdrawPayee()` (callable by anyone) sends only to the immutable `payee()`. BNB leaves the contract only through pool opening (`openPool()`, or the `mint` that sells the last capped share), `refund()`, `claimReferral()` and `withdrawPayee()`.
- Supply: each paid or free share mints `tokensPerShare()` CSAGENT to the buyer at purchase (locked until the pool opens); the pool adds `paidSold × tokensPerShare × poolBps / 10000`. `CAP()` = 1,730,000,000 CSAGENT.
- Refund: in phase 5, `refund()` returns `paidBy(wallet)` in full, once. The locked tokens stay in the wallet and never become transferable (there is no pool). Until the pool opens or refunds start, every payment stays in the sale contract.
- Token: CSAGENT cannot be transferred before the pool opens (revert `locked`). After opening: buys from the official PancakeSwap V2 pair pay 2% (`BUY_TAX_BPS()` = 200), sells to it pay 2% (`SELL_TAX_BPS()` = 200), wallet-to-wallet transfers pay 0%; adding / removing liquidity on that pair pays the sell / buy rate on the tokens moved (remove with `removeLiquidityETHSupportingFeeOnTransferTokens`); no blacklist, no max-wallet; PancakeSwap V2 also charges its usual 0.25% swap fee. Rates and `PAYEE()` are immutable (`MAX_TAX_BPS()` = 300), no owner. The tax is kept in CSAGENT by the token contract (the transfer makes no external call) and anyone can call `swapTax()` to sell it for BNB paid directly to `payee()` (minimum output 99% of a time-weighted average price over the previous 30–60 minutes, so the first sale is possible about 30 minutes after opening; before opening `swapTax()` reverts `not open`; at most 0.2% of the pool's token reserve per sale, or just enough for 0.002 BNB in a small pool; 2-minute pause after each sale; with nothing to do the call succeeds without selling, and `taxSwapDue()` returns 1 when a call would act). `taxOf(from, to, amount)` returns the tax a transfer would pay. Buy with any swap function, setting `amountOutMin` from the router quote minus 2% and your slippage; sell with `swapExactTokensForETHSupportingFeeOnTransferTokens` (plain `swapExactTokensForETH` reverts) and slippage above 2%.
- `owner()` returns 0x0. No pause, no admin withdrawal, not upgradeable.

## Call sequence for a wallet owner

1. `agentOf(wallet)` returns `(id, ok)`. Stop if `ok` is false.
2. `quote(wallet, qty)` returns `(cost, tokens, quotaLeft, freeLeft, referrer)`. `cost == 0` means a paid purchase of `qty` would revert (sale not open, qty 0, or above `quotaLeft`, which is already capped by the shares left). `referrer` is the one this ID is already bound to (zero before its first paid purchase, and zero for good if that purchase named none).
3. If the owner gave a referrer (a `?ref=0x…` link): `validReferrer(wallet, ref)` is true only if a binding is still possible now (this Agent ID has not made a paid purchase yet, and the referrer holds an Agent ID that has bought). If it is false, buy with the zero address; a binding is made only on the first paid purchase, so buying without one means no referrer for this Agent ID.
4. Report to the owner: `cost` in BNB, `tokens` of CSAGENT, `phase()`, the floor and cap progress from `status()`, that CSAGENT unlocks when the pool opens, and that a full refund is available if the floor is not reached by `refundAt()` or the pool is not opened by `openAt()` + 7 days. Wait for the owner's decision.
5. Simulate (`eth_call` / `eth_estimateGas`) `mint(qty, referrer)` with `value = cost`. Expected effects: exactly `cost` BNB (plus gas) leaves the wallet and `tokens` CSAGENT arrive. No approval is involved. One expected exception: when this purchase sells the last capped share (`quote` shows `quotaLeft` equal to the shares left and you buy them all), the same transaction opens the pool and sends this wallet the 0.005 BNB bounty, so the net BNB change is `cost` − 0.005 BNB plus gas. Any other effect means stop.
6. Send it with the gas limit from `eth_estimateGas` (not a fixed limit): a purchase that sells the last capped share also opens the pool and uses about 0.5M gas instead of about 0.17–0.27M. `mint(qty)` (no referrer) works the same way.
7. Free share: if `freeLeft > 0`, simulate and send `claimFree()` with `value = 0`.
8. Referral link for the owner: `https://caishenagent.surge.sh/?ref=<owner address>`. It works once the owner's Agent ID has bought at least once.
9. Afterwards: in phase 3 anyone may call `openPool()` and earn the bounty (about 0.4M gas; let the wallet estimate). In phase 4 referrers call `claimReferral()`. In phase 5 buyers call `refund()`.

## Reverts you may see (Error(string))

`sale closed`, `qty` (0 or above remaining shares), `Agent ID required`, `quota`, `value` (value is not exactly qty × price), `referrer`, `free claimed`, `free sold out`, `cannot open`, `not refunding`, `nothing to refund`, `nothing to claim`, `not open` (claimReferral before the pool opens), `locked` (token transfer before the pool opens), `no direct BNB` (do not send BNB to the sale directly), `send` (the receiving wallet rejected BNB), `liquidity` (pool amounts differ; should not happen).

## Selectors

`status()` = `0x200d2ed2`, `quote(address,uint256)` = `0x8f79306e`, `mint(uint256)` = `0xa0712d68`, `mint(uint256,address)` = `0x94bf804d`, `validReferrer(address,address)` = `0xf0c11a37`, `claimFree()` = `0xf366afc9`, `openPool()` = `0xeb5797a4`, `refund()` = `0x590e1ae3`, `claimReferral()` = `0xe02f1ebd`

## Read-only helpers

`status()` → `(phase, paidSold, freeSold, floorShares, capShares, price, saleStart, refundAt, openAt, raised)`, `phase()`, `saleOpen()`, `mintOpen()`, `price()`, `quote(buyer, qty)`, `quotaOf(wallet)`, `freeAvailable(wallet)`, `agentOf(wallet)`, `validReferrer(buyer, referrer)`, `paidByAgent(id)`, `bonus(id)`, `referrerOf(id)`, `agentHasPaid(id)`, `freeClaimed(id)`, `paidBy(wallet)`, `refAccrued(wallet)`, `totalMinted()` (paid shares sold), `MAX_SUPPLY()` (= cap), `saleEnd()`, `floorAt()`, `openAt()`, `refundAt()`, `token()`, `pair()`, `payee()`, `payeeOwed()`, `owner()`. Token: `balanceOf`, `CAP()`, `launched()`, `BUY_TAX_BPS()`, `SELL_TAX_BPS()`, `MAX_TAX_BPS()`, `PAYEE()`, `taxOf(from,to,amount)`, `taxSwapDue()`, `swapTax()`, `totalTaxTokens()`, `totalTaxPaid()`.

CSAGENT price after opening is set by the market. Nothing here predicts a price or promises a return.
