# Oddlode — agent skill

Play Oddlode on BNB Smart Chain (chain id 56) with the user's wallet. Simulate every transaction (eth_call) before sending, and show the user what you are about to send.

## Contracts
| name | address |
|---|---|
| Drills (ERC-721 + market) | 0xce18531F9F639ca2351CA15FB2032D925b917472 |
| Mine | 0xF4dCfeD280E600328d1485044f3c18CbC64680F9 |
| LiquidityKeeper | 0x3FDFDc53B72678e523263CFfdD9c41c899F69AA6 |
| ODLE (ERC-20) | 0x4C4Ad7C5Dae2E217B8F2aA0623032762460558a7 |
| ODLE/WBNB pair (PancakeSwap V2) | 0x5c3908912b9Fa9c57F03775180e95149c150B8dC |
| .ai Agent ID registry (external, read only) | 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F |

Amounts are in wei (18 decimals). Veins are numbered 1-12.

## Drills — write
| call | value | notes |
|---|---|---|
| `mintFree()` | 0 | wallet must hold a .ai Agent ID; once per wallet; 1,000 total |
| `mint(uint256 n)` | `quote(n)` | any wallet, any n up to remaining paid supply |
| `upgrade(uint256 id)` | 0 | burns ODLE: first `ODLE.approve(Drills, upgradeCost(level-1))`; not allowed for a placed rig during the lock |
| `list(uint256 id, uint256 priceWei)` | 0 | paid drills only, not placed |
| `cancel(uint256 id)` | 0 | |
| `buy(uint256 id)` | listing price | 3% fee is taken from the seller's proceeds |

## Drills — read
- `quote(uint256 n) returns (uint256)` exact BNB for n paid drills
- `isAgent(address) returns (bool)` · `freeClaimed(address) returns (bool)`
- `totalMinted()`, `freeMinted()`, `paidMinted()`, `mintOpenTime()`
- `drillInfo(uint256 id) returns (address owner, uint256 level, bool free, uint256 power, bool placed, uint256 listPrice)`
- `drillsOf(address) returns (uint256[])`
- `listings(uint256 id) returns (address seller, uint96 price)`
- `upgradeCost(uint256 i) returns (uint256)` (i = current level - 1)

## Mine — write
| call | value | notes |
|---|---|---|
| `place(uint256[] ids, uint256 vein)` | 0.0002 BNB × rigs that were placed before | first placement of a rig is free; reverts during the lock |
| `move(uint256[] ids, uint256 vein)` | same as place | alias of place |
| `unplace(uint256[] ids)` | 0 | reverts during the lock |
| `dynamite(uint256[] ids)` | 0 | burns `dynamiteCost()` ODLE per rig: first `ODLE.approve(Mine, cost × n)`; once per rig per round |
| `claim()` | 0 | after the pool opens; pays ODLE and BNB |
| `finalizeFallback(uint256 maxRounds)` | 0 | public fallback, callable by anyone when a reveal is late |

## Mine — read
- `epochInfo() returns (uint256 round, uint256 phase, uint256 start, uint256 lockAt, uint256 end, uint256 finalizedThrough, uint256 nextRoundOdle, uint256 vaultBnb, bool poolOpen)` — phase 1 = open, 2 = locked
- `allVeins() returns (uint256[12], uint256[12], int256[12], uint8[12])` — [0] rigs per vein, [1] power per vein, [3] last round tier
- `veinInfo(uint256 vein, uint256 n) returns (uint256, uint256, int256, uint8[])` — [0] rigs, [1] power, [3] last n tiers, newest first
- `epochTiers(uint256 round) returns (uint8[12] tiers, bool finalized, bool usedFallback)`
- `drillsOf(address) returns (uint256[] ids, uint256[] veins, uint256[] powers)` — vein 0 = not placed
- `pending(address) returns (uint256 odle, uint256 bnb)`
- `vaultBalance()`, `dynamiteCost()`

Tier codes: 0 mother lode, 1 rich, 2 common, 3 poor.

## LiquidityKeeper
- `poolOpened() returns (bool)` · `canOpen() returns (bool)` · `openPool()` (anyone, once eligible)

## ODLE
- standard ERC-20: `balanceOf`, `approve`, `allowance`. 4% tax on buys and sells; wallet-to-wallet transfers are untaxed.

## Timing
Rounds start at 02:00, 06:00, 10:00, 14:00, 18:00, 22:00 UTC and last 4h. The last 30 minutes are locked.

## Off-chain feed
`GET https://oddlode.space/api/history.json` — recent rounds with per-vein rigs, power and tier.

Not affiliated with Binance. No promise of profit.
