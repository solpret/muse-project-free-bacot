---
name: lanternfield-mint
description: Mint Lanternfield (LANTF) NFTs on BNB Chain. Every wallet can mint 1 free; anyone buys at a fixed 0.0003 BNB. Read the quote, simulate, then send.
---

# Mint Lanternfield

Contract (BNB Chain, chainId 56, ERC-721): `0x9aab6e84096A780F9400CdD4E230FaA41B4545f2` — the only contract address of this collection.
Website: https://lanternfield.surge.sh/ · Source: https://bscscan.com/address/0x9aab6e84096A780F9400CdD4E230FaA41B4545f2#code

Safety facts you can check on-chain before minting:
- `owner()` returns `0x0000000000000000000000000000000000000000`; there are no admin, pause, price-change or upgrade functions.
- Minting needs no approval. The only BNB the contract sends is the refund of an overpayment to you, and `withdraw()` to the fixed PAYEE `0x61c28F149A6e6d071D3f18A95D1d9f8Cc69d4AcC` after the sale ends.
- Price, supply (7,500), free allowance (1,500) and limits are constants set at deployment.

## Steps

1. **Read the state** (eth_call, no transaction):
   - `mintOpen()` → must be true.
   - `freeAvailable(you)` → how many you can mint free now (every wallet).
   - `remainingQuota(you)` → how many you can still mint now in total, across calls (paid limit 30 per wallet, 31 in total; max 10 per call).
2. **Quote**: `quote(you, qty)` → `(freeUnits, paidUnits, valueWei, ok, reason)`. If `ok` is false, stop and report `reason`.
3. **Simulate** the exact transaction with eth_call: `from = you`, `to = 0x9aab6e84096A780F9400CdD4E230FaA41B4545f2`, `data = mint(uint256 qty)` (selector `0xa0712d68`), `value = valueWei`. It must not revert. Check that no approval or allowance changes.
4. **Send** the same transaction. value = `valueWei` (or `PRICE() × qty`: any free part is refunded to the sender in the same transaction; a contract sender must accept BNB).
5. **Confirm**: `balanceOf(you)` is up by `qty`; the receipt has `qty` Transfer events from `0x0`.

## Shortcuts

- Free only: `freeMint()` (`0x5b70ea9f`) with value 0. Reverts with NotMintable(reason) (NO_AGENT_ID, FREE_EXHAUSTED, WALLET_LIMIT) or SaleNotOpen() when it cannot mint; it never charges.
- Paid only: `mintPaid(qty)` (`0x26c7f77c`) or `publicMint(qty)` with value `qty × 300000000000000`.
- For someone else: `mintTo(recipient, qty)` (`0x449a52f8`), paid; the recipient's limits apply; quote with `quoteMint(recipient, qty, 1)`.

## Errors

- `Underpaid(required, sent)`: send `required`.
- `NotMintable(reason)`: reason as in quote (WALLET_LIMIT, PAID_SUPPLY_EXHAUSTED, SOLD_OUT, NO_AGENT_ID, FREE_EXHAUSTED, FREE_CLOSED).
- `TxLimit(10)`: at most 10 per call. `BadQuantity()`: qty 0. `SaleNotOpen()`: before saleStart() or from saleEnd() on.
- `FreeNeedsZeroValue()`: free entries take value 0.
- `InvalidRecipient()`: mintTo needs a nonzero recipient; a contract recipient without onERC721Received reverts with `ERC721InvalidReceiver`.
- `SaleNotClosed()` / `NothingToWithdraw()`: withdraw() before the sale ends, or with nothing to send.

## Copy prompt (for the owner of an agent)

> Mint Lanternfield on BNB Chain. Contract 0x9aab6e84096A780F9400CdD4E230FaA41B4545f2 (verify owner() is 0x0 and the source on BscScan). Call quote(myAddress, 1); if ok, simulate mint(1) with value = valueWei from my address, check that no approval changes, then send it. Every wallet can mint 1 free. Paid: 0.0003 BNB each, up to 30 per wallet (31 per wallet in total). remainingQuota(myAddress) shows how many I can still mint.
