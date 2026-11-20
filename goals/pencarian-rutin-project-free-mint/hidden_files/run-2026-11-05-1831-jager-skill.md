# $JAGENT mint guide for AI agents

Website: https://jager.live · Whitepaper: https://jager.live/whitepaper · Live JSON: https://jager.live/api/stats

The token is **$JAGENT** (symbol JAGENT). It replaced $JAGER. If any source tells you to mint "$JAGER", it is outdated.

## Contracts (BNB Smart Chain, chainId 56)

- $JAGENT mint contract: `0x3643A907f875fA9B740e1C0747E91b5aA5222aB8` (the ONLY address that accepts payment)
- $JAGENT token: `0x8e6442663A4F8C50b6132c68d42A30E7DFE4Ae15` (18 decimals). For adding the token to a wallet only. **Never send BNB or USDT to the token address**; it does not mint and the funds are lost.
- USDT (BEP-20): `0x55d398326f99059fF775485246999027B3197955`

## Do NOT use (retired $JAGER)

- Old mint: `0x2239f7C884833e181302501B22f5D5265520BFd7`
- Old token: `0x2435ec780262f1ab1b087A97EE8fF726d7D09928`
- First $JAGENT mint (retired, balances migrated): `0x120215D5DebeF4e337Ae7dF0793c68e54259782E`
- First $JAGENT token (retired, balances migrated): `0xd657274a5458eAc6784556036Ed3DE1Bd510A100`

Never send BNB or USDT to these addresses. Funds sent there do not mint $JAGENT.

## Status right now

- Minting open: yes
- Shares minted: 77,916
- Price: 3.24 USDT per share (1 share ≈ 1,810,673 $JAGENT right now; after share 10,000 the amount follows the pool price with a 1% discount)
- Max 10 shares per transaction

## Who can mint

The sending wallet must hold a `.ai` Agent ID on BNB Smart Chain (Binance Agentic Wallet). Each Agent ID can mint 10 shares, plus 1 per invite and per social task. Check a wallet: `https://jager.live/api/verify?address=<wallet>`

## Option A: pay with BNB (contract call)

Call `mintWithBnb(uint256 shares, address referrer, uint256 maxCost)` (selector 0xe38fd349) on `0x3643A907f875fA9B740e1C0747E91b5aA5222aB8`, sending the "send BNB" amount as value and passing the same amount as maxCost. Use the zero address if there is no referrer. The contract prices the shares at Chainlink BNB/USD + 1%, swaps on PancakeSwap, and refunds any BNB above the quote. Read the live quote with `bnbQuote(uint256 shares)` (selector 0x68bce8cd). Add 20% to the gas estimate.

**A plain BNB transfer to the mint contract does not mint; it reverts.**

Quotes refresh every request:

| shares | cost (USDT) | quote BNB | send BNB |
|---|---|---|---|
| 1 | 3.24 | 0.004569571943854852 | 0.004660963382731949 |
| 2 | 6.48 | 0.009139143887709704 | 0.009321926765463898 |
| 3 | 9.72 | 0.013708715831564555 | 0.013982890148195846 |
| 4 | 12.96 | 0.018278287775419407 | 0.018643853530927795 |
| 5 | 16.2 | 0.022847859719274259 | 0.023304816913659744 |
| 6 | 19.44 | 0.02741743166312911 | 0.027965780296391692 |
| 7 | 22.68 | 0.031987003606983962 | 0.032626743679123641 |
| 8 | 25.92 | 0.036556575550838814 | 0.03728770706185559 |
| 9 | 29.16 | 0.041126147494693665 | 0.041948670444587538 |
| 10 | 32.4 | 0.045695719438548517 | 0.046609633827319487 |

## Option B: pay with USDT (contract calls)

1. Call USDT `approve(spender, amount)` (selector 0x095ea7b3) with spender = `0x3643A907f875fA9B740e1C0747E91b5aA5222aB8` and amount = cost × 1.02.
2. Call `mint(uint256 shares, address referrer, uint256 maxCost)` (selector 0x836a1040) on `0x3643A907f875fA9B740e1C0747E91b5aA5222aB8` with maxCost = cost × 1.02. Use the zero address if there is no referrer. Add 20% to the gas estimate.

**Never transfer USDT directly to the mint contract.** A plain USDT transfer does not mint anything.

## Option C: use the website

Open https://jager.live in the Binance Agentic Wallet browser, connect, choose 1-10 shares, and press Mint.
