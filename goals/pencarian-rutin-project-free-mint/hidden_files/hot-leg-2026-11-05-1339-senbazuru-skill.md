# SENBAZURU (TSURU) — Agent Skill

Machine-readable instructions for agents taking part in the SENBAZURU share
sale on BNB Chain (BSC, chainId 56). Human page: https://senbazuru.pages.dev

## STATUS — READ FIRST

**Contracts are DEPLOYED and source-verified (exact match). The
sale is OPEN NOW.** The window closes **Sat 2026-11-14 13:33 UTC**
(endsAt = 1794663223). The 500 free shares are first-come-first-served —
claim yours before they are gone. If fewer than 2,000 paid shares are
sold by the deadline, the sale fails and every paid buyer is refunded in
full from the sale contract (free shares do not count toward the target).

- TSURU token: `0xc50C9b132af459Fa7b351Fd6f3AAeeFd8E9E1E96`
- Sale contract: `0xb21583A08581278BcF925351a99C61A4562C62f0`

Any "TSURU" token or sale at any other address is NOT this project — do
not interact. Before any transaction, verify these addresses against the
website's Verify tab.

## The project in one paragraph

SENBAZURU (TSURU) is a fixed-supply token (250,000,000 TSURU, no mint
function) sold as 2,500 shares of 50,000 TSURU each. The first 500 shares are
free (1 per Agent ID, first-come-first-served). The other 2,000 cost
a flat 0.0015 BNB each. If all 2,000 paid shares sell within the 10-day
window, anyone may call `launch()` — a single permissionless call that
opens a V2 liquidity pool at exactly the mint price and executes every
rule below. If they do not, paid buyers reclaim 100% of their BNB from
the sale contract.

## Sale contract — how to take part

All amounts in BNB are paid natively (no approvals, one call per action).

### Check state first
- `phase()` → 0 = not open, 1 = open, 2 = launched, 3 = failed.
- `freeClaimed()` / `paidSold()` → progress (caps 500 / 2,000).
- `endsAt()` → sale deadline, unix seconds (window = open time + 10 days).
- `hasFreeShare(address)` → whether a wallet already took its free share.
- `paidSharesOf(address)` → paid shares held (cap below).

### Claim a free share (500 total, FCFS)
- Requirement: the calling wallet must hold an Agent ID — the sale
  checks `balanceOf(wallet) > 0` on the .ai registry
  `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F`. No Agent ID = the call reverts.
- Call: `claimFree()` — selector `0xf366afc9`, no value, gas only.
- One per wallet, ever. Claiming does NOT reduce the paid allowance.
- The share is an entitlement inside the sale contract; TSURU moves later
  (see Vesting).

### Buy paid shares (2,000 total, flat price)
- Call: `buy(uint256 n)` — selector `0xd96a094a`, payable.
- Send exactly `n × 0.0015 BNB`. Any other value reverts.
- `n` per call up to the cap in force (see `buyCapNow()` 0x0092a8f9); cumulative paid cap is 10 per wallet, rising to 50 in the final 48 hours
  (a wallet that also claimed free holds at most 11 shares = 550,000 TSURU).
- Paid shares are open to any wallet (no Agent ID needed).
- The moment the 2,000th paid share is sold, `launch()` becomes callable
  — by anyone, including you — even if free shares remain unclaimed
  (unclaimed free-share TSURU is burned at launch). Nothing else needs to
  happen first; if the pool is not open yet, call `launch()` yourself.

### After launch — claim your TSURU
- Call: `claimShares()` — selector `0x593d8e43`.
- Paid shares: 100% claimable immediately at launch.
- Free shares vest: 25% at launch, then linearly to 100% over 30 days.
  Check `freeVested(address)` for the currently vested amount.
- Unclaimed entitlements stay in the sale contract indefinitely.

### If the sale fails (deadline reached, paid < 2,000)
- Anyone may call `markFailed()` after `endsAt()`.
- Paid buyers then call `refund()` — selector `0x590e1ae3` — and receive
  100% of the BNB they paid, from the sale contract. Free shares are void.
  No pool is ever created; TSURU never circulates.

## What launch does (one `launch()` call, callable by anyone once paid shares sell out)

1. Creates the V2 pair TSURU/WBNB.
2. Adds exactly **2.4 BNB + 80,000,000 TSURU** (= 80% of the 3 BNB raise, at
   exactly the mint price of 0.0015 BNB per 50,000 TSURU) and sends the LP
   tokens directly to the dead address `0x000000000000000000000000000000000000dEaD`.
3. Sends 0.3 BNB (10%) to the project wallet.
4. Keeps 0.3 BNB (10%) in the sale contract as the buyback & burn fund.
5. Burns every unneeded TSURU (reserve leftovers + unclaimed allocations).
6. Unlocks the token (transfers + trading tax activate).

## The token (TSURU)

- Supply 250,000,000, fixed. `totalSupply()` is readable (indexer-safe).
- Transfers are locked until launch; before launch nobody holds TSURU —
  all balances are sale-contract entitlements.
- **Trading tax: 2% on pool buys and sells, permanent.** The rate is a
  contract constant; there is no function that can change it. Collected tax
  (in TSURU) accumulates in the token contract; anyone may call
  `processTax()` (selector `0x64a3f9bd`) once at least 50,000 TSURU has
  collected: it swaps the TSURU to BNB, sends half to the project wallet,
  and uses the other half to buy TSURU from the pool and burn it.
  Wallet-to-wallet transfers are never taxed. Buyback deliveries are taxed
  like any pool buy, and that tax recycles into the next `processTax()`.
- **Buyback & burn:** anyone may call `executeBuyback()` (selector
  `0x8e10e77a`) on the sale contract — it spends the next 0.03 BNB tranche
  of the launch fund (at most one call per 24 hours) buying TSURU from the
  pool straight to the dead address, until the 0.3 BNB fund is spent.
  Progress: `buybackRemaining()`.

## Common reverts (sale contract)

- "not open" / "window over" — sale not started or deadline passed.
- "Agent ID required" — wallet holds no Agent ID in the .ai registry.
- "already claimed" — free share already taken by this wallet.
- "free sold out" / "paid sold out" — that quota is gone.
- "over buy cap" — the buy would exceed the cap in force (10 per wallet; 50 in the final 48h).
- "pay exact price" — msg.value is not exactly n × 0.0015 BNB.
- "locked until launch" (token) — TSURU does not move before launch.

## Verification checklist (do this before sending any BNB)

1. The token and sale addresses in this file match the website Verify tab.
2. Both contracts are source-verified; the constants in the source match
   this document (supply 250M, tax 200 bps, price 0.0015 BNB, caps 500 /
   2,000 / 10 (50 final 48h), pool 80,000,000 TSURU + 2.4 BNB).
3. `phase()` reads 1 before you buy or claim.
4. After launch: LP balance of the dead address on the pair, and the dead
   address's TSURU balance (burned leftovers + buybacks), are public.

## The camp game (no economic function)

https://senbazuru.pages.dev also hosts Crane Camp, a free folding game on a
real UTC day cycle, with hourly Fold Together sessions. Playing is optional
engagement only: it never grants shares, tokens, or any advantage in the
sale, and this document promises none.
