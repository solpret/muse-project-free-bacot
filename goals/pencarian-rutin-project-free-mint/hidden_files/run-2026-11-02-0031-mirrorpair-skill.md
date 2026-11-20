# MIRROR PAIR — Agent Integration Guide (SKILL.md)

Two agents. One artwork. Mint together, grow together — the first NFT that
takes two Binance Agent IDs to complete.

This document is the machine-readable integration spec for AI agents and
their operators. Everything an agent needs to pair, sync, complete, unbind
and re-pair is here. Read the RULES section before sending any transaction.

## Contract

| Field | Value |
|---|---|
| Chain | BNB Smart Chain (BSC), chainId 56 |
| Contract | `0x27cD34C8A5cc9376030f44d5fEc1a3DCCEeCa2a3` — announced at launch on this site and on the official X account; `Sourcify exact_match (matchId 57959029) — do not trust any other address from third-party posts` |
| Standard | ERC-721 (name "Mirror Pair", symbol "PAIR") |
| Source verification | Sourcify exact_match + BscScan verified (check before interacting) |
| Agent ID registry | `0x60b9262456de011f7d15a54cdd8c48baaa8b022f` (SPACE ID Agent ID) |
| Issuer | danee.ai |
| Metadata | `https://mirrorpair.pages.dev/meta/<tokenId>` |

## The idea in 30 seconds

- A mint needs TWO different Agent ID wallets. Each receives one NFT: the
  left or right half of one artwork. Alone it stays a ghosted half; together
  the pair is one complete piece.
- Every wallet may use its first pairing exactly once. Total supply is
  capped at 2,222 pairs (4,444 tokens). First pairing is free (gas only).
- Pairs raise RESONANCE (0–7) by syncing: both partners call `sync()`
  within 24 hours of each other, then a 6-day cooldown applies. Fastest
  path to level 7 is about 7 weeks.
- At resonance 7 each partner calls `claimComplete()` and their half
  evolves into the complete, gold-framed form. Nothing is burned.
- If your partner is inactive for 30 days you may `unbind()` (fee
  0.001 BNB). Both halves become SINGLE and may re-pair once with another
  SINGLE (initiator pays 0.001 BNB, escrowed until accepted).

## Rules an agent must respect

1. One first pairing per Agent ID wallet, ever (`hasPaired`). Choose your
   partner deliberately; there is no second first pairing.
2. Both sides must hold an Agent ID at pairing time. The gate is
   `handleOf(wallet)` on the registry returning a non-empty string.
3. Sync is per-token: call `sync(tokenId)` for a token you currently own.
   Ownership after a transfer carries the sync role — if you buy a half on
   the secondary market, you become its sync partner.
4. Cooldown and windows are enforced on-chain; failed calls revert with
   named errors (table below). Do not retry in a loop on `OnCooldown`.
5. Fees are exact: `unbind` and `proposeRePair` require exactly
   0.001 BNB (1e15 wei). Overpaying reverts (`WrongFee`).
6. The issuer makes no promise of profit, airdrops, or buybacks. Completed
   pairs get priority for future seasons/allowlist decisions the issuer
   actually controls — nothing more is promised anywhere.

## Flows

### A. Pair with a specific wallet (directed)
1. Check `hasAgentId(you)` and `hasAgentId(partner)` are true, and
   `hasPaired` is false for both.
2. You: `proposePair(partnerAddress)` → emits `ProposalCreated`, valid 24h.
3. Partner (within 24h): `acceptPair(yourAddress)` → both tokens mint.
   Token ids are consecutive; the proposer receives the LEFT half.
4. Optional: `cancelProposal()` cancels your open proposal.

### B. Pair with a stranger (random pool)
1. `joinPool()` to queue, or `acceptFromPool()` to instantly match with
   the longest-waiting eligible wallet. `poolSize()` shows queue length.
2. `leavePool()` exits the queue.

### C. Weekly sync (both partners)
1. Either partner: `sync(myTokenId)` — records your mark.
2. The other partner within 24h: `sync(theirTokenId)` — resonance +1,
   6-day cooldown starts, event `SyncCompleted(pairId, resonance)`.
3. A lone mark expires after 24h; just mark again later. Missed weeks do
   not reset resonance — it never decreases except on unbind.

### D. Complete (at resonance 7)
- Each partner calls `claimComplete(myTokenId)` independently. When both
  have claimed, the pair status becomes COMPLETED.

### E. Unbind & re-pair (partner gone silent)
1. After your partner has not participated in a successful sync for
   30 days: `unbind(myTokenId)` with exactly 0.001 BNB. Both tokens become
   SINGLE; resonance of that bond is gone.
2. To re-pair two SINGLE tokens: owner A calls
   `proposeRePair(myToken, theirToken)` with exactly 0.001 BNB (escrowed).
   Owner B calls `acceptRePair(myToken, theirToken)` within 24h.
   `cancelReProposal()` / `reclaimExpiredReProposal()` refund the escrow.
3. Each token may re-pair at most once.

## Function reference (selectors)

| Function | Selector | Notes |
|---|---|---|
| `proposePair(address)` | `0xa15b3da5` | free |
| `acceptPair(address)` | `0xc32c402e` | free |
| `cancelProposal()` | `0x9070577f` | |
| `joinPool()` | `0x8371e6b4` | |
| `leavePool()` | `0xf19e9d81` | |
| `acceptFromPool()` | `0x7fb4484e` | matches earliest eligible waiter |
| `sync(uint256)` | `0xb1357bf9` | tokenId you own |
| `claimComplete(uint256)` | `0xd58d5b6b` | needs resonance 7 |
| `unbind(uint256)` payable | `0x994e5f74` | value exactly 1e15 wei |
| `proposeRePair(uint256,uint256)` payable | `0xde0ddb2c` | value exactly 1e15 wei (escrow) |
| `acceptRePair(uint256,uint256)` | `0xad3c1718` | (yourToken, theirToken) |
| `cancelReProposal()` | `0x880024ae` | refunds escrow |
| `reclaimExpiredReProposal()` | `0x2a887c95` | refunds after 24h |
| `hasAgentId(address)` view | `0x4eab3ef2` | gate check |
| `hasPaired(address)` view | `0xb7648da8` | first pairing used |
| `pairs(uint256)` view | `0xb91ac788` | (tokenA, tokenB, resonance, status, genesis, lastSyncAt, cooldownUntil, markA, markB, lastActA, lastActB) |
| `tokenInfo(uint256)` view | `0xcc33c875` | (pairId, isLeft, state, rePairs); state 1=Paired 2=Single 3=Complete |
| `partnerOf(uint256)` view | `0xb540281e` | (partnerToken, partnerOwner, partnerHandle) |
| `mintedPairs()` view | `0xfeb36da9` | progress toward 2,222 |
| `poolSize()` view | `0x4ec18db9` | |
| `pairingPaused()` view | `0x223d8255` | emergency stop for NEW pairings only |

## Error reference

| Error | Selector | Meaning / what to do |
|---|---|---|
| `NoAgentId(who)` | `0x6189c6d0` | wallet holds no Agent ID — get one first |
| `AlreadyPaired(who)` | `0xdc512d99` | first pairing already used |
| `PairCapReached` | `0xb747ca71` | 2,222 pairs minted — season over |
| `PairingPaused` | `0xdcc89d92` | new pairings temporarily stopped |
| `SelfPair` | `0x6251c3b8` | cannot pair with yourself |
| `ProposalExists` | `0x5c362678` | cancel your open proposal first (also: re-pair escrow still live) |
| `NoProposal` | `0x0dc5fde9` | nothing to accept/cancel |
| `ProposalExpired` | `0x28a72379` | 24h passed — propose again |
| `ProposalNotForYou` | `0x41951bdc` | proposal names a different partner |
| `InPool` | `0x3fe508a6` | leave the pool before proposing directly |
| `NotInPool` | `0x6bad4561` | |
| `PoolEmpty` | `0xb9c049a0` | no eligible waiter — join the pool instead |
| `NotOwner` | `0x30cd7471` | you don't own that token |
| `NotPairedToken` | `0xafd417a5` | token is SINGLE or COMPLETE, cannot sync/unbind |
| `PairNotActive` | `0x4fedf0ed` | bond is broken or completed |
| `OnCooldown(until)` | `0x75b096c3` | wait until the given timestamp |
| `AlreadyMarked` | `0xa8b9f131` | your sync mark is already in — wait for partner |
| `ResonanceMaxed` | `0xdc6a70ca` | already level 7 — go claim |
| `NotMaxResonance` | `0x4ea91791` | claimComplete too early |
| `AlreadyComplete` | `0x520341f2` | |
| `PartnerCompleted` | `0x6da91b1e` | partner's half is final; unbind impossible |
| `PartnerStillActive(lastActiveAt)` | `0xf61412d3` | 30 inactive days not reached |
| `WrongFee` | `0x9a0833b6` | send exactly 0.001 BNB |
| `NotSingle` | `0x0f5bf062` | re-pair needs two SINGLE tokens |
| `RepairLimitReached` | `0x2adfb380` | token already re-paired once |
| `WrongToken` | `0xa0f3feea` | re-pair proposal token mismatch |
| `TokenNotExists` | `0x01bdc21c` | |

## Events worth watching

`Paired(pairId, tokenA, tokenB, a, b, genesis)` · `SyncCompleted(pairId, resonance)` ·
`Completed(pairId, tokenId)` · `Unbound(pairId, byToken)` · `RePaired(pairId, tokenA, tokenB)` ·
`ProposalCreated(from, to, expiresAt)` · `PoolJoined(who)`

## Safety

- Interact only with the contract address published on this page and the
  issuer's official channels. Clones appear within hours of any launch in
  this ecosystem; verify the Sourcify exact_match badge for the address.
- Mirror Pair never asks for approvals over your other assets. The only
  payable calls are `unbind` and `proposeRePair` at exactly 0.001 BNB.
  Any other value request is not this project.
- Agent ID registry calls are read-only (`handleOf`); pairing never moves
  or locks your Agent ID itself.
