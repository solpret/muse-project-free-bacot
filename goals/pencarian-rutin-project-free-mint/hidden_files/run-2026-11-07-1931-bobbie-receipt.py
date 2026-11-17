import json, time, urllib.request
RPC = "https://bsc-dataseed.binance.org"
TX = "0x6813257cfa75abda36407e880073ac45f6bc4bf5b8ecf3d0a5adbd8e01ec536d"
def rpc(method, params, timeout=30):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)
for i in range(20):
    try:
        rc = rpc("eth_getTransactionReceipt", [TX])
        res = rc.get("result")
        if res:
            print("status:", int(res["status"], 16), "block:", int(res["blockNumber"], 16),
                  "gasUsed:", int(res["gasUsed"], 16), "logs:", len(res.get("logs", [])))
            for lg in res.get("logs", []):
                print("  topic0:", lg["topics"][0][:18], "topics:", len(lg["topics"]), "data len:", len(lg.get("data",""))-2)
                # MintRequested(uint256,address,uint256,uint256,uint256,uint256): seq indexed, wallet indexed
                if lg["topics"][0].startswith("0x") and len(lg["topics"]) >= 3:
                    seq = int(lg["topics"][1], 16)
                    wallet = "0x" + lg["topics"][2][-40:]
                    data = lg["data"][2:]
                    words = [int(data[j:j+64], 16) for j in range(0, len(data), 64)]
                    print("  seq:", seq, "wallet:", wallet, "words:", words)
            json.dump(res, open("run-2026-11-07-1931-bobbie-receipt.json", "w"), indent=1)
            break
    except Exception as e:
        print("try", i, "ERR", e)
    time.sleep(3)
else:
    print("receipt not found after 60s")
