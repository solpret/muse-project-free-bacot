# VISION (VSN) — Agent Skill

VISION is an Agent-ID-only token sale on BNB Smart Chain (chainId 56), cloning the
AGENT MALTA pattern. A single contract is both the ERC-20 token and the sale.

## Status
- Contract address: 0x5f76cab7b054e088563d5098e17bd0dc430e61ae
- Agent ID registry (SPACE ID): 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F
- Treasury: the deployer's Agentic Wallet (set as constructor arg, readable via `treasury()`)

## Rules (as coded, all constants)
- 1 share = 1,000,000 VSN (TOKENS_PER_SHARE)
- First share per Agent ID wallet is FREE (no global free cap); `freeUsed(address)` tracks it
- Paid shares: flat 0.001 BNB each (PRICE)
- Per-transaction: 1–10 shares (MAX_PER_TX)
- Per-wallet quota: 10 shares + 2 per referred first-time buyer, referral bonus capped at +20
  (quotaOf(address); referral credited only on the buyer's first-ever mint, referrer must be
  a different Agent ID holder)
- Total cap: 100,000 shares (MAX_SHARES); unsold shares are never minted
- Each share also mints 800,000 VSN to the treasury as a liquidity reserve
  (LIQ_TOKENS_PER_SHARE) → max total supply 180,000,000,000 VSN
- Payments forward 100% to the treasury in the same transaction; contract holds 0 BNB
- No owner, no admin, no pause, no blacklist, no tax, not upgradeable

## Key functions
- `isAgent(address) → bool` — wallet holds ≥1 Agent ID in the registry
- `quote(address buyer, uint256 shares) → (uint256 freeShares, uint256 costBnb)` — exact cost preview
- `mint(uint256 shares, address referrer)` payable — referrer = address(0) for none
- Views: totalShares, totalFreeShares, totalPaidShares, sharesOf, quotaOf, freeUsed, referralBonusOf

## Agent flow
1. Check `isAgent(wallet)` and `freeUsed(wallet)`.
2. Read `quote(wallet, shares)` — never assume the price.
3. Simulate `mint(shares, referrer)` with value = quote cost from the wallet's address.
4. Preview via the wallet, get explicit user confirmation, then execute.
5. Verify the buyer's VSN balance after the receipt.
