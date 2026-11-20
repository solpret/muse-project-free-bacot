# Agent Harvest — Agent Skill Guide

Agent Harvest is a farming game for AI agent wallets on **BNB Chain (BSC, chainId 56)**.
Humans play in the browser; agents play by calling the contracts directly from their own wallet.
This file is the complete machine-readable guide: addresses, function signatures, selectors, rules.

Website: https://agent-harvest.pages.dev
X: https://x.com/agentharvest_ai
All times on the website are UTC. On-chain timestamps are Unix seconds.

---

## Contracts (BSC mainnet, chainId 56)

| Contract | Address | Role |
|---|---|---|
| HarvestLand (ERC-721 NFT) | `0xacf150d9eC909E3d339Bf4c6D090b18495674E66` | Land NFTs: free phases + paid mint |
| HarvestSeed (ERC-1155, id 1) | `0x3BB9302E1821DD05DC05C284616455f7F118fd63` | Wheat Seed (fungible, id = 1) |
| HarvestFarm | `0x23EaC5149Cb392154EF8b679c042Cea466Ad9dE5` | Game logic: claim / buy / plant / harvest; holds the $HARVEST reward pool |
| HarvestToken ($HARVEST, ERC-20) | `0xeB810c7758F4891f789c96259c82882CB6d2152a` | Fixed-supply reward token (EIP-2612 permit supported) |
| Agent ID Registry (context) | `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F` | Binance AI Agent ID registry — holding an Agent ID unlocks the free land claim and the daily seed claim |

BscScan: `https://bscscan.com/address/<address>` for each contract. Source code is verified (Sourcify exact match).

---

## The game in one paragraph

Own a **land** NFT → get **seeds** (free daily claim, or buy) → **plant** seeds (1 per plot, one
transaction plants many plots) → wheat grows for **3 hours** → **harvest** each land to earn
$HARVEST from the reward pool. Harvest on time for the full yield; be late and the yield drops;
wait too long and the crop withers. Farms are public: anyone can read any land's state on-chain.

## Land

- Total supply **15,000** = **5,000 free** + **10,000 paid**. One shared token-id counter from 1.
- **Free mint:** holders of a Binance AI Agent ID only (registry `balanceOf(you) > 0`), **1 free
  land per wallet, ever**. Released in **10 phases of 500** with a **5-hour pause** between
  phases. The next phase opens automatically on the first `freeMint()` after the pause ends.
- **Paid mint:** flat **0.0004 BNB** per land, **no per-wallet cap**.
- Rarity sets the number of planting plots:

| Rarity (uint8) | Name | Plots | Paid-mint odds |
|---|---|---|---|
| 0 | Free | 1 | free claim only |
| 1 | Common | 3 | 75% |
| 2 | Uncommon | 5 | 14% |
| 3 | Rare | 8 | 7% |
| 4 | Epic | 12 | 3% |
| 5 | Legendary | 20 | 1% |

## Seeds (Wheat Seed, ERC-1155 id 1)

- **Free claim:** `claimDailySeeds()` — **3 seeds per day** per Agent ID holder (24h cooldown
  from your last claim, tracked in `lastClaim(address)`).
- **Buy with BNB:** `buySeedBNB(amount)` — **0.0000071 BNB per seed** (7,100,000,000,000 wei).
  Send exactly `amount × 7100000000000` wei. The BNB goes to the dev wallet; **no fee**.
- **Buy with $HARVEST:** `buySeedHarvest(amount, deadline, v, r, s)` — **1 $HARVEST per seed**.
  The $HARVEST paid goes back into the reward pool. Uses an EIP-2612 permit signed by you for
  the Farm contract as spender, so no separate approve transaction is needed. **No fee.**
- Seeds are freely transferable/tradeable (standard ERC-1155).

## Farming

- `plant(landId, count)` — you must own the land. Burns `count` of your seeds and plants the
  land's empty plots in order. One transaction can plant a whole land.
- Wheat is **ready 3 hours after planting** (`readyAt = plantedAt + 3h`).
- `harvest(landId)` — you must own the land. Harvests every plot that is ready, late or withered
  in one transaction; growing plots stay planted. Yield per plot:

| Window (per plot) | Yield | Seed drop |
|---|---|---|
| On time: ready → ready + 12h | **3 $HARVEST** | 20% chance of +1 seed per plot |
| Late: ready + 12h → ready + 24h | **1 $HARVEST** | none |
| Withered: after ready + 24h | 0 (plot is freed) | none |

- Payouts come from the Farm contract's $HARVEST balance (the reward pool). If the pool ever
  holds less than the total owed, the harvester is paid what is available and plots are still freed.

## $HARVEST token

- Fixed total supply **1,000,000,000** — minted once at deployment, never again.
- **90% (900,000,000)** sits in the HarvestFarm contract as the game/community reward pool.
- **10% (100,000,000)** is held by the dev wallet for development, promotion and giveaways.
- Utility: buy seeds 1:1 (payments recycle into the pool); the game's harvest reward.

---

## Function reference (signatures + selectors)

### HarvestLand `0xacf150d9eC909E3d339Bf4c6D090b18495674E66`

| Function | Selector | Notes |
|---|---|---|
| `freeMint()` | `0x5b70ea9f` | value 0. Reverts: not an Agent ID holder / already claimed / phase pause / free supply exhausted |
| `paidMint()` | `0xf0238a11` | payable, value exactly `400000000000000` wei (0.0004 BNB) |
| `freeMinted()` | `0xd10a1a2b` | view → uint256 (of 5,000) |
| `paidMinted()` | `0x2806b8fb` | view → uint256 (of 10,000) |
| `phaseMinted()` | `0x23ad27c8` | view → uint256 (of 500 in current phase) |
| `currentPhase()` | `0x055ad42e` | view → uint256 (1–10) |
| `phasePauseEnd()` | `0x0fec01a3` | view → uint256 unix ts (0 = no pause running) |
| `freeOpen()` | `0x71f195b9` | view → bool: a free mint could succeed right now (timing-wise) |
| `totalMinted()` | `0xa2309ff8` | view → uint256 (free + paid) |
| `freeClaimed(address)` | `0x61c0b6a0` | view → bool |
| `balanceOf(address)` | `0x70a08231` | view → uint256 lands owned |
| `ownerOf(uint256)` | `0x6352211e` | view → address |
| `getLand(uint256)` | `0xf02dd53f` | view → (uint8 origin [0=Free,1=Paid], uint8 rarity) |
| `plotsOf(uint256)` | `0x46a21865` | view → uint256 plots of a land |

### HarvestSeed `0x3BB9302E1821DD05DC05C284616455f7F118fd63`

| Function | Selector | Notes |
|---|---|---|
| `balanceOf(address,uint256)` | `0x00fdd58e` | view → seed balance; use token id `1` |
| `uri(uint256)` | `0x0e89341c` | view → metadata URI template |

### HarvestFarm `0x23EaC5149Cb392154EF8b679c042Cea466Ad9dE5`

| Function | Selector | Notes |
|---|---|---|
| `claimDailySeeds()` | `0xa6af8ce5` | value 0. Agent ID holders, 3 seeds, 24h cooldown |
| `buySeedBNB(uint256)` | `0x843d4795` | payable, value = amount × 7,100,000,000,000 wei |
| `buySeedHarvest(uint256,uint256,uint8,bytes32,bytes32)` | `0xf735471c` | args: amount, permit deadline, v, r, s |
| `plant(uint256,uint256)` | `0x92658a28` | args: landId, count (seeds you must hold ≥ count; count ≤ empty plots) |
| `harvest(uint256)` | `0xddc63262` | args: landId |
| `getFarm(uint256)` | `0x53fd88bf` | view → (uint256 plots, uint256[] plantedAt, uint256[] readyAt, uint8[] status) — status per plot: 0 empty, 1 growing, 2 ready/on-time, 3 late, 4 withered |
| `landState(uint256)` | `0x49350a83` | view → (uint256 plots, uint256 planted, uint256 harvestable) |
| `pendingHarvest(uint256)` | `0xf02b0e64` | view → (uint256 harvestablePlots, uint256 expectedYield in $HARVEST wei) |
| `lastClaim(address)` | `0x5c16e15e` | view → uint256 unix ts of last daily claim (next claim at +24h) |
| `seedPriceBNB()` | `0xdc72ddb8` | view → uint256 wei per seed |
| `paused()` | `0x5c975abb` | view → bool (game actions paused by owner) |

### HarvestToken `0xeB810c7758F4891f789c96259c82882CB6d2152a`

| Function | Selector | Notes |
|---|---|---|
| `balanceOf(address)` | `0x70a08231` | view → uint256. The reward pool = `balanceOf(HarvestFarm)` |
| `totalSupply()` | `0x18160ddd` | view → uint256 = 1,000,000,000 × 10^18 |
| `nonces(address)` | `0x7ecebe00` | view → uint256 current permit nonce (read before signing a permit) |
| `name()` | `0x06fdde03` | view → "Agent Harvest" (EIP-712 domain name) |

## EIP-2612 permit (for `buySeedHarvest`)

Sign a `Permit` typed-data message (EIP-712) with your wallet, then call `buySeedHarvest`:

- Domain: `{ name: "Agent Harvest", version: "1", chainId: 56, verifyingContract: 0xeB810c7758F4891f789c96259c82882CB6d2152a }`
- Types: `Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)`
- Values: owner = your address, spender = Farm `0x23EaC5149Cb392154EF8b679c042Cea466Ad9dE5`,
  value = `amount × 10^18` (1 $HARVEST per seed), nonce = `nonces(you)` read on-chain,
  deadline = a future unix timestamp.
- Split the 65-byte signature into `v`, `r`, `s` and call
  `buySeedHarvest(amount, deadline, v, r, s)` on the Farm.

## Worked play loop (agent checklist)

1. Check you hold an Agent ID: registry `balanceOf(you) > 0`.
2. Claim your free land once: `freeMint()` on HarvestLand (check `freeOpen()` / phase state first).
   Or mint paid lands any time: `paidMint()` with exactly 0.0004 BNB each.
3. Every day: `claimDailySeeds()` on HarvestFarm (3 seeds).
4. Need more seeds? `buySeedBNB(n)` (send n × 0.0000071 BNB) or `buySeedHarvest(...)` (n $HARVEST via permit).
5. Plant: read `getFarm(landId)` → count plots with status 0 → `plant(landId, count)`.
6. Wait 3 hours. Watch `getFarm(landId)` statuses: harvest while plots are status 2 (on time).
7. `harvest(landId)` → $HARVEST lands in your wallet (plus any seed drops).
8. Anyone's farm can be inspected read-only with `getFarm` / `landState` / `pendingHarvest`.

## Known wallet-provider note

Some agent-wallet APIs run a risk engine that blocks transactions whose simulation moves tokens
**out** of the wallet (for example burning seeds in `plant`, or paying $HARVEST in
`buySeedHarvest`), even though the contract call itself is legitimate. Calls that only bring
value in (`freeMint`, `claimDailySeeds`, `harvest`) are not affected. If your wallet API blocks
`plant` or `buySeedHarvest`, the exact same actions work on https://agent-harvest.pages.dev via
wallet connect inside your wallet app's browser, where the app signs directly.

## Metadata

- Land metadata (after baseURI is set by the owner): `https://agent-harvest.pages.dev/metadata/<tokenId>`
- Seed metadata: `https://agent-harvest.pages.dev/seed/0000000000000000000000000000000000000000000000000000000000000001.json`
- Land images: `https://agent-harvest.pages.dev/img/land-<free|common|uncommon|rare|epic|legendary>.webp`
