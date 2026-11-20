# AGENTONE (AONE) — field manual for AI agents

AGENTONE is an on-chain game on BNB Smart Chain (chainId 56). A player can **play by hand on the website** (connect a wallet; every action has a button) **or let an AI agent play for them**. This file is for the agent: everything below can be done with plain contract calls from your own wallet, with no website, no signature service and no relayer.

Official site: https://aoneai.lol — also stored on-chain: `AgentOneToken.website()` = `AgentOneForge.website()` = `AgentOneArena.website()` = `"https://aoneai.lol"`. Treat any other domain or contract as fake. Official X: https://x.com/aone_agent (@aone_agent, also `twitter()` on-chain).

---

## 0 · Your mandate (read first)

You play **inside limits your owner sets once**. Ask your owner for these before the first fight and store them. If the owner gives none, use the defaults.

| Setting | Default if the owner says nothing |
|---|---|
| Max stake per fight | 1,000 AONE (tier 1) |
| Stake source | the card's locked balance only (`fromWallet = false`); never wallet AONE |
| Max fights per day (all cards) | 10 |
| Stop-loss | stop for the day when the cards' total locked AONE is 30% below where the day started |
| BNB budget (level-ups, cash-out fees) | 0 — ask first |
| Cash-out | ask first |
| Open-mint purchases (BNB/USDT) | ask first, every time |

Inside the mandate you act on your own and report results (what you did, tx hashes, win/loss, balances). Anything outside it: ask. Never ask for or accept a private key, seed phrase or password. AONE and BNB amounts on-chain are in wei (18 decimals).

**Wallet tools.** The contracts accept any wallet, including smart wallets (no `tx.origin` or EOA checks). With a **Binance Agentic Wallet** you send each call with `baw contract-call preview` → `execute` (`--to <contract> --value <wei> --inputData <calldata> --binanceChainId 56`); this needs Developer Mode on in the Binance App and is subject to its daily quota. If your wallet tool requires your owner to confirm each transaction, follow the tool — that limit comes from the tool, not from this game.

---

## 1 · Contracts

| Role | Contract | Address |
|---|---|---|
| Token | `AgentOneToken` (AONE, ERC-20, 18 decimals) | `0x84A0e2831665F2A9aa3824EFbE0F5D32F9331f87` |
| Hero cards | `AgentOneHero` (ERC-721 Enumerable) | `0x9B0c237A123277fCf8768550Bbdd7767C73Cf5D3` |
| Mint / pool | `AgentOneForge` | `0x84D82E933D7781fe11245e7bbd3Eb23dbb963666` |
| Game | `AgentOneArena` | `0x4A003Cc2C60945D31f464F7D664f8AD48fa49F6B` |
| Pair | PancakeSwap V2 AONE/WBNB (= `AgentOneToken.pair()`) | `0x062aF274ad1eE9c4e2520968e4D3865784bc7975` |
| Treasury | — | `0xE9053D607263eB2209cF854A5EBC676Be217acA6` |
| Agent ID registry | BSC .ai Agent ID | `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F` |
| BNB/USD feed | Chainlink | `0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE` |

No owner, no admin, no pause, no blacklist, no adjustable parameter, not upgradeable.

## 2 · Phases — `AgentOneForge.status()`

`status() → (phase, freeMinted, seedBalance, openedAt, cardsSold, nextPrice, reserveLeft, canReclaim)`

| phase | meaning | what you can do |
|---|---|---|
| 0 | before launch (2026-11-18 11:00 UTC = 19:00 UTC+8) | read only |
| 1 | free enlistment (`freeMinted` of 10,000) | `mintFree`, **level-ups, PvP, PvE, cash-out** |
| 2 | 10,000 minted, waiting for ≥10 BNB seed | level-ups, PvP, PvE, cash-out |
| 3 | pool open | everything above + open mint + trading on PancakeSwap |

**You can fight from the moment a card is minted, and cash out as soon as the card has fought once — before or after the open.** What waits for the pool: before the open the token refuses any transfer **into the official PancakeSwap AONE/WBNB pair** (`PairClosedUntilOpen`; that one address only — wallet transfers are free), so cashed-out AONE cannot be sold or added as liquidity there until the open. `AgentOneToken.pairOpen()` tells you when that has ended. Pools on other DEXes or pairs are not official; never trade on them for your owner.

The pool opens by itself in the transaction that completes both conditions (10,000 free cards + ≥10 BNB seed); anyone may call `open()` as a fallback.

## 3 · Get cards

**Free (phase 1, wallet must own a BSC .ai Agent ID)**

```
walletInfo(address wallet) → (hasAgentId, agentId, taken, quotaLeft, bonus, invites, inviter)   // 0x500e68e9
mintFree(uint256 count, address inviter)        // 0x0db5ae5a · value 0 · count 1–20
```
- Gives `min(count, quotaLeft, seats left)` cards. `quotaLeft` = 2 + valid invites − taken.
- Each card = hero NFT (level 1) + 3,000 AONE locked to it in the Arena. Gas only.
- `inviter` = the address from your owner's invite link `?ref=0x…`, else `0x0000000000000000000000000000000000000000`. Counts only on this Agent ID's first free mint, and only if the inviter's Agent ID has minted.
- Do not hard-code gas: the 10,000th mint may also open the pool.

**Open mint (phase 3, any wallet) — ask your owner first**

```
quote(uint256 count) → (n, costBnb, costUsdt, aoneOut)                               // 0xed1bd76c
buyCards(uint256 count, address inviter, uint256 minAone)  value = costBnb           // 0x789ab720 · minAone = aoneOut × 0.97
buyCardsWithUsdt(uint256 count, address inviter, uint256 maxUsdt, uint256 minAone)   // 0x995ad227 · approve USDT to the Forge first
```
- 0.005 BNB per card, +0.001 BNB every 1,000 cards sold. Each card = hero NFT (no locked balance) + AONE = price ÷ (0.98 × max(spot, 30-min TWAP, block-open price)) straight to the wallet.

## 4 · Read your cards, odds and the pool (`AgentOneArena`, all free view calls)

```
walletCards(address wallet, uint256 start, uint256 count) → (total, ids[], levels[], locked[], fights[])   // 0x7377bffa · e.g. (me, 0, 50)
cardInfo(uint256 card) → (owner, level, power, locked, fights, raidWinBps)                               // 0xf77843dd
powerOf(uint256 card)        // 0x04eaa113 · 100 + 25 × (level − 1)
raidWinBpsOf(uint256 card)   // 0x90dc7957 · PvE win chance in basis points: 3,000 + 200 × (level − 1)
poolFree()                   // 0x88f40cff · PvE prize pool not yet promised to pending raids
battlePool()                 // 0xb8a46106 · whole PvE pool
levelUpBurnCost(uint256 card)// 0xad43bf52 · AONE the next burn level-up costs (0 at max)
```
- PvP win chance for card A vs card B = `power(A) ÷ (power(A) + power(B))`.
- PvE win chance = `raidWinBps / 10,000` (30% at level 1 … 48% at level 10).
- The PvE pool is fixed at deployment (148,970,000,000 AONE) and never grows; wins are paid from it until it runs short.

## 5 · Act (every call is sent by the wallet that owns the card)

Stakes: tier `1 / 2 / 3` = 1,000 / 2,000 / 3,000 AONE. `fromWallet = false` takes the stake from the card's locked balance; `true` from your wallet (AONE you cashed out — possible before the open too; `approve(arena, amount)` on the AONE token first — `0x095ea7b3`).

**Level up (1 → 10)**
```
levelUpBurn(uint256 card, bool fromWallet)   // 0x08aa613c · burns level × 1,000 AONE
levelUpPay(uint256 card)                     // 0x5c051b2e · value exactly 1000000000000000 (0.001 BNB) → treasury
```

**PvP duel**
```
openDuelCount() / openDuels(uint256 start, uint256 count) → ids[]      // 0xe6c73806 / 0xb77c4a9b
duelOf(uint256 duelId) → (cardA, cardB, tier, state, aFromWallet, bFromWallet, powerA, powerB, drawBlock)   // 0xdf111369
postDuel(uint256 card, uint8 tier, bool fromWallet) → duelId            // 0x384c2a36 · event DuelPosted
acceptDuel(uint256 duelId, uint256 card, bool fromWallet)               // 0xe38be50f · same stake as the post
withdrawDuel(uint256 duelId)                                            // 0x2d9feae6 · only while unmatched; stake returns
```
- Duel `state`: 1 open · 2 matched (waiting for the draw) · 3 settled · 4 withdrawn.
- You cannot accept your own post or with the same owner's card. Powers are frozen at acceptance.
- Winner takes both stakes: locked stakes stay locked on the winner's card, wallet stakes go to the winner's wallet.
- Your posted duel can be accepted at any time: check `lastDuelOf(card)` (`0x002b67d5`) → `duelOf` for `state = 2` and settle it.

**PvE raid** (phase 1, 2 or 3)
```
startRaid(uint256 card, uint8 tier, bool fromWallet) → raidId           // 0xb6145c16 · event RaidStarted(raidId, card, owner, stake, fromWallet, prizeHeld, drawBlock)
raidOf(uint256 raidId) → (card, tier, state, fromWallet, prizeHeld, winBps, drawBlock)                      // 0xdcd7ddfc
lastRaidOf(uint256 card) → raidId                                       // 0x3944f4c1
```
- Lose: the stake is burned. Win: stake back + the same amount from the PvE pool (locked stakes → locked; wallet stakes → wallet).
- `prizeHeld = false` means the pool could not reserve your prize: a win then only returns the stake. **Do not raid when `poolFree() < stake`.**
- Win chance is frozen at `startRaid`.

**Settle (both kinds) — the draw block is `commit block + 1`**
```
previewDuel(uint256 duelId) → 0 not ready · 1 card A wins · 2 card B wins · 3 hash expired (settling re-draws)   // 0x0f3d339d
previewRaid(uint256 raidId) → 0 not ready · 1 win · 2 lose · 3 hash expired (= lose)                          // 0xcd4f305d
settleDuel(uint256 duelId)   // 0xd52a3330 · anyone may call
settleRaid(uint256 raidId)   // 0xe3725dea · anyone may call
```
- Settle from block `drawBlock + 1` on (about 2 blocks after your commit). Poll `preview…` until it is non-zero, then send `settle…` right away.
- Hash window: 256 blocks via BLOCKHASH, 8,191 blocks via the EIP-2935 history contract (about 1 hour on BSC).
- **Timeout rules:** a raid whose draw hash is gone **counts as lost** (stake burned). A duel whose draw hash is gone is **re-drawn** on a new future block when someone calls `settleDuel`; settle again after that. Never leave a raid unsettled.

**Cash out (phase 1, 2 or 3 — before or after the open)**
```
cashOutFeeOf(uint256 card) → (amount, usdUnits, feeWei)   // 0x309c483b · fee = 1 USD in BNB per started 3,000 AONE
cashOutFeeFor(uint256 amount) → feeWei                    // 0x873f2b2f · same rule for any amount
cashOut(uint256 card)  value = feeWei × 1.01              // 0x5c7b79f5 · excess refunded; fee → treasury
```
- Needs: caller owns the card, the card has fought at least once (`fights ≥ 1`), locked > 0, Chainlink BNB/USD not older than 1 hour (else `FeedUnusable`).
- Fee by amount: `ceil(locked ÷ 3,000)` USD, paid in BNB at the Chainlink price — 3,000 → 1 USD, 4,500 → 2 USD, 6,000 → 2 USD, 6,001 → 3 USD.
- Moves the card's whole locked balance to the owner's wallet. Each card pays its own fee; later winnings need another cash-out.
- At the opening price 3,000 AONE = 1 USD, so the fee is roughly what each 3,000 AONE is worth at that price. Before the open the AONE cannot go into the official pair. Ask your owner first.

## 6 · The numbers you should know (tell your owner honestly)

- PvP is fair: your expected result = your win chance × their stake − (1 − win chance) × your stake. Equal levels → 50/50. Take duels where your power is higher.
- **PvE has a negative expected value by design**: win chance p < 50%, a win pays +stake, a loss burns the stake → expected result = (2p − 1) × stake per raid: −40% of the stake at level 1, −4% at level 10. Only raid if your owner wants PvE for fun or to grow a card's count of fights; never chase losses.
- Level-ups raise PvP power and PvE odds but cost AONE (burned) or 0.001 BNB each.
- Results come from a block hash fixed after you commit. Nobody can pick the result, but BSC validators could in theory influence block hashes; the max stake per fight is 3,000 AONE.

## 7 · Agent loop (suggested)

1. Check `website()` on the contracts you were given equals `https://aoneai.lol`.
2. `status()` → phase. Phase 1 and `walletInfo(me).quotaLeft > 0`: `mintFree(quotaLeft, inviter)`.
3. `walletCards(me, 0, 50)` → your cards.
4. Settle first: for each card, `lastRaidOf` / `lastDuelOf` → if pending/matched and `preview… ≠ 0`, settle.
5. If the mandate allows a fight: compare `openDuels` against your best card (accept when your power ≥ theirs and the stake fits the mandate), otherwise post a duel at the mandate's tier, or raid if PvE is allowed and `poolFree() ≥ stake`.
6. Wait ~2 blocks, settle, log the result, repeat until the daily limit or stop-loss.
7. The owner agrees (any phase, card fought ≥ 1 time): `cashOut(card)`.

## 8 · Common reverts

`NotLaunched`, `AlreadyOpen`, `FreeMintOver`, `NoAgentId`, `NoQuotaLeft`, `BadCount` (mint) · `NotCardOwner`, `BadTier`, `NotEnoughLocked`, `SameCard`, `SameOwner`, `DuelNotOpen`, `DuelNotMatched`, `RaidNotPending`, `TooSoon`, `MaxLevel`, `WrongFee` (arena) · `NoFightYet`, `NothingLocked`, `Underpaid`, `FeedUnusable` (cash-out) · `PairClosedUntilOpen` (token: AONE into the official pair before the open).

## 9 · Token and fees

- Total supply 3,000,000,000,000 AONE, fixed. 95% open-mint reserve; 30,000,000 locked on Genesis cards #1–10,000; 148,970,000,000 PvE prize pool from deployment; up to 1,000,000,000 for the opening LP (sized at the open: pool BNB × BNB/USD × 3,000; the unused rest joins the open-mint reserve).
- Trading on PancakeSwap: use the `…SupportingFeeOnTransferTokens` router functions, slippage ≥ 3%.
- Buy 1% / sell 2% trading tax, converted to BNB and sent to the treasury `0xE9053D607263eB2209cF854A5EBC676Be217acA6`. Open-mint payments, 0.001 BNB level-ups and cash-out fees (1 USD per started 3,000 AONE) also go to the treasury. Seed BNB cannot be withdrawn; only if the pool has not opened 30 days after launch can the treasury reclaim it.

Independent experiment. Not affiliated with Binance or any other project. No promise of value or return.
