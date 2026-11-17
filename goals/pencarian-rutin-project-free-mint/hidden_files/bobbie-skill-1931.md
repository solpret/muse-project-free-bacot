---
name: bobbie-bsc
description: Preview and execute user-confirmed BOBBIE mint, settlement, market and reward actions using the live verified protocol.
---

Read [agent.md](/agent.md), [muse.md](/muse.md), `/api/config` and `/api/mint-window`. Require matching live/on-chain protocol3 or4 and matching NFT addresses. Use the user's own Binance Agentic Wallet integration or browser wallet; check signer, chain and real `.ai` eligibility. Never ask for keys, seed phrases or Binance sessions.

Every transaction follows preview → user confirmation → execute. Requote free/paid counts and exactBNB before mint. With v4, retain the confirmed MintRequested sequence, then separately preview/confirm completion against the fixed future-block hash. A commitment is not delivery. Never repeat a confirmed mint. Handle queue delays by preserving the fixed hash before its8,191-block retention expires. No VRF, rerolls or per-request cancellation. Verify Minted and ownerOf after settlement.

v4 paid revenue/referral credits and NFT transfers remain locked until successful finalization. A missed uncaptured hash permits irreversible whole-sale cancellation and principal refunds to original payers; gas is excluded. Check cancellation/expiry before actions. v3 remains legacy sequential/immediate and uses its original reward rules.

NFT base rewards in v4 are100% at TGE and claim once per NFT. Presale400M and Squad20,876,289 are closed reserves; do not prepare a contribution or Squad claim. Use full v4 ABIs under `/abi/v4/` only after live config confirms v4. Market trades must recheck owner, approvals, listing version and unclaimed benefits. Never treat an announcement, button click or oracle/queue request as a successful NFT delivery.
