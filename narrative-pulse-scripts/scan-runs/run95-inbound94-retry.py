#!/usr/bin/env python3
"""Run 95: retry of the 32 failed inbound contracts from run 94.
Run-94 window 132125940-132134019.
Topic-filtered: Transfer from zero address to a tracked wallet. Read-only."""
import json, sys
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
ZERO_PAD = "0x" + "0" * 64
HOME = Path.home()
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = sorted({"0x" + "0" * 24 + w[2:] for w in uniq})
CONTRACTS = ["0x071f76c1868039e2f042dca1890ecb0364d8494a", "0x0834648da9229ad33ed17e47b6dab04134bf79a3", "0x08393dad165d90e7258501fe1dfb5f3498644011", "0x1c89acab7a497f537f988b5f20055fd11b062f50", "0x1cf9e60218493149ace7dc953497c07175aa625e", "0x29ee92a8d6dc62035d0c2b4d53b5df504d3ebe91", "0x2a2463d243e5c4df850e48f350392ad23b494132", "0x2a91b304ee74162007730cf1da24c1d8c137c627", "0x681d1f88dd93465f17cab905be299b34ea2c414f", "0x683085af799ce53a5e2682440788724b6f2910c2", "0x6834a0b5d3bab31a6d9a5505c2a9534daf46dbaf", "0x7eb3a26f895d4d1b8fcd38a67e9689cb2693661f", "0x7fa142c23805387c94fbc4adebf1168a7145f528", "0x8a4e6a11789507f39898b840b351c9b102e4c3e7", "0x8a6a0931fd0bf0f54501134db616587d2d27b2e0", "0x8aaa14b24e71cc93672939ba3e3c3e9de2674d27", "0x9cc4d56e6ce5c0ddade134b932023b5cab2458d8", "0x9d78b216ae96060895837c60df84893cd5ac34f2", "0x9da90fe302a987d979c21d7c3ae421cb0b2cf8b0", "0xa624cd94eaae91ccafa5be9857f476a76f57f61a", "0xb594b29360bd45975608c92dbdba764c508b5c99", "0xb5a083bd9e8e330085e8f459f13f080d4f8fe5b4", "0xbf3488e453c68e9771c26d448e99d0ec5395135f", "0xbfbde67707d00a759e55ee158abfcb3b33f375fd", "0xbfccd7de6ef1b3d81632412600a933cd6de14b77", "0xcee93a5bfad6172358f6012a08d83f0d6d7bad46", "0xcfa79d53e2b9451f4792a475a5e6ac39602b1e21", "0xd0079025a9bb66a7a1de991de2e4326faba35729", "0xe3f0085fd94d4fb2ae9acb4b49f6c0504e3546a0", "0xe41b54504aa171d92e01384ae3ab3007e170aa70", "0xf1822144176ad13c5bccfe33a23129c37ca5bdcd", "0xf1968d3f690b2327afef1b8aa87a4fe9e1090591"]
FROM, TO = 132125940, 132134019
out = {"window": [FROM, TO], "contracts": []}
for C in CONTRACTS:
    entry = {"contract": C, "from": FROM, "to": TO, "ok": False}
    try:
        data = ankr_mod.get_logs(C, FROM, TO)
        logs = ((data.get("result") or {}).get("logs") or [])
        print(f"{C} unfiltered logs={len(logs)}", flush=True)
        hits = []
        if len(logs) >= 1000:
            data2 = ankr_mod.get_logs(C, FROM, TO, topics=[T_TRANSFER, ZERO_PAD, tracked_padded])
            logs2 = ((data2.get("result") or {}).get("logs") or [])
            print(f"{C} truncated; topic-filtered logs={len(logs2)}", flush=True)
            logs = logs2
        for lg in logs:
            topics = lg.get("topics") or []
            if not topics: continue
            if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
                hits.append({"contract": C, "kind": "ERC721/20 Transfer", "to": "0x" + topics[2][-40:],
                             "token_id": int(topics[3], 16) if len(topics) >= 4 else None,
                             "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
            elif topics[0] == T_SINGLE and len(topics) >= 4 and topics[2] == ZERO_PAD and topics[3] in tracked_padded:
                hits.append({"contract": C, "kind": "ERC1155 TransferSingle", "to": "0x" + topics[3][-40:],
                             "token_id": int(topics[4], 16) if len(topics) >= 5 else None,
                             "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
        entry.update({"ok": True, "logs": len(logs), "hits": hits})
        print(f"{C} RETRY DONE logs={len(logs)} hits={len(hits)}", flush=True)
        for h in hits: print("HIT", h, flush=True)
    except Exception as e:
        entry.update({"ok": False, "error": str(e)[:300]})
        print(f"{C} RETRY FAILED {e}", flush=True)
    out["contracts"].append(entry)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run95-inbound94-retry.json", "w"), indent=1)
print("saved run95-inbound94-retry.json")
