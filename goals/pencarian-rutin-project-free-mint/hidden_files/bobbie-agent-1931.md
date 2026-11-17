# BOBBIE — wallet-agent integration

Official site: https://bobbiebsc.com · X: https://x.com/BobbieBSC.

Mainnet v4 is deployed and source-verified. Read `/api/mint-window` for current availability and deadline; this document does not determine whether mint is open. Active NFT: `0x3BF121dC4c5a1Ba567F3eE801d0e447601726207`. Always confirm the live config and chain; this static address alone is not transaction authorization.

## Verify live deployment

Read `/api/config`, `/api/mint-window` and the NFT `PROTOCOL_VERSION()`. Require matching addresses, chain and version. Supported versions are 3 (legacy sequential) and 4 (two-step future-block). Never use an address copied from chat as deployment authority. ABIs: v3 under `/abi/`, v4 under `/abi/v4/`. Stop on unknown versions, RPC failures, cancellation, closed mint or a passed deadline.

Mainnet is BNB Chain 56. A labelled chain97 rehearsal uses test BNB and a simulated registry; it does not issue real Binance IDs. Public mint on mainnet requires the signing wallet itself to hold a real Binance Agent ID `.ai`. The registry is `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F`.

## Preview → user confirmation → execute

Use the official Binance Agentic Wallet integration in the user's own environment. Check actual signing address and chain. Never request or transmit keys, seed phrases, Binance sessions or website session cookies. Connecting a wallet or reading this file is not transaction authorization.

Read `quote(wallet,quantity,includeSocial)`, `mintedBy`, `freeUsed` and the mint window. Lifetime public cap is ten. Shared free pool is 2,000; paid brackets are 4,000 at 0.001 BNB and 3,992 at 0.002 BNB. A batch crossing brackets is priced per NFT. Use exact BNB and expected free count. Stop and requote on changed price/quota. Free mint still needs gas.

Current X mission post: https://x.com/BobbieBSC/status/2118668230118240396. The Missions share button opens a user-reviewed X composer with the prepared project introduction, all five hashtags (#FreeMint #AgentID #BNBChain #NFT #Airdrop) and that post URL. It does not publish or approve a grant automatically.

One base free right needs Agent ID. The extra right needs follow + like + retweet + comment wallet on the official post, then manual team snapshot approval. A signed-in Missions session obtains a ten-minute voucher bound to wallet, campaign, chain and NFT contract. No X OAuth/API is required. At most two free mints per wallet, sharing the global free pool.

## v4 two-step mint (no VRF)

1. Preview `mint(quantity,quotedFree,referrer,voucherDeadline,voucher)` and gas; obtain confirmation and send exact BNB.
2. Verify `MintRequested` from the configured NFT and actual signing wallet. Retain sequence and targetBlock. This receipt is a COMMITMENT, not NFT delivery. Never repeat a confirmed commitment.
3. Read `/api/requests?wallet=...&ids=sequence` and `requests(sequence)`. After the fixed future block, and when `nextToSettle()` equals sequence, preview and confirm `settleMint(sequence)`. It requires gas, no additional mint price.
4. If an earlier request delays the queue, anyone can call `captureEntropy(sequence)` to preserve the exact target hash. BSC retains 8,191 blocks via the pinned EIP-2935 history contract. Capture before expiry. No alternate target, reroll or per-request refund exists.
5. Verify `Minted` and `ownerOf` after settlement; report transaction and token links.

Sparse Fisher–Yates draws without replacement, skipping eight referral reserves. Future-block entropy is unknown at commitment time, but validators can influence block hashes. This is not VRF-level randomness, and `private` storage is not secret. A pool draw needs at most one matrix write; ERC-721 and accounting still require other writes.

Paid revenue and referral credits stay escrowed until the ten-day mint window ends (or all public quota is committed), all requests settle and the sale finalizes. NFT transfers and marketplace trading then open. If any uncaptured hash expires, anyone can irreversibly cancel the WHOLE sale. Original payers can call `refundTo(recipient)` for their paid-mint principal; gas is not refundable. No admin can withdraw escrow before successful finalization. Monitor/capture requests before opening public mint.

## v3 compatibility

v3 is sequential and immediate. Its `Minted` event and `ownerOf` are verified in the mint receipt; no completion request exists. It retains the original 120M NFT reward reserve and old contract rules. Old claim/set controls are removed from the website. Do not describe v4 as active unless live config and on-chain version both confirm 4.

## Rewards and market

v4 supply is fixed at 1B BOBBIE. Allocations: 400M presale reserve; 300M NFT reserve (279,123,711 base + 20,876,289 Squad); 100M liquidity; 100M community/SocialFi; 100M team. NFT BASE rewards unlock 100% at TGE, once per NFT, payable to current owner with `claimBase(uint256[] ids)`, max50. Remainders are exact 18-decimal units, not rounded advertised values. No five-tier set registration exists in v4.

Presale and Squad are CLOSED reserves for future modules. Planned presale: 10 BNB softcap / 20 BNB hardcap, 20M BOBBIE/BNB, 50% TGE + 30-day vesting, first12h >=5 NFTs then >=2, no multiplier. Do not prepare presale payments without a verified actual sale contract. Squad rules are not finalized; funding cannot unlock before TGE+30days. Team has a180-day cliff followed by365-day linear vesting. Liquidity allocation is not proof of a completed LP lock.

After successful sale finalization, admin schedules TGE once at least ten minutes ahead. Base rewards are pre-funded; only provably unissued base allocations may return once to the fixed treasury. Valid NFT claims never expire, including unclaimed referral prizes. Transfers do not reset claimed rights. Native marketplace total fee is10%, paid-mint referrals5%. Check owner, approval, listing version and benefit state immediately before a trade. Offers escrow BNB; cancelled offers create credits withdrawable only by their owner.
