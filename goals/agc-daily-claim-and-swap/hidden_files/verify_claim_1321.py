import json, urllib.request, time, sys
RPCS = ["https://bsc-dataseed.binance.org","https://bsc-dataseed1.binance.org","https://bsc.publicnode.com"]
TX = "0x78059b2c4ccdff3bde8f49d02165bb2a7cce1ae2334f191ca81a656302b30605"
WALLET = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINTER = "0x6288DFe86f22B53eEB6886aE2D78941de7483743"
AGC = "0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6"
def rpc(method, params):
    last=None
    for u in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req=urllib.request.Request(u,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=20) as r:
                res=json.loads(r.read())
            if "error" in res: raise RuntimeError(res["error"])
            return res["result"]
        except Exception as e:
            last=e; continue
    raise last
from eth_abi import encode, decode
from eth_hash.auto import keccak
def call(to,data):
    return rpc("eth_call",[{"to":to,"data":data},"latest"])
# wait for receipt
rcpt=None
for i in range(20):
    rcpt=rpc("eth_getTransactionReceipt",[TX])
    if rcpt: break
    time.sleep(3)
print("receipt:", json.dumps(rcpt, indent=2)[:2000] if rcpt else "NONE after 60s")
if rcpt:
    print("status:", int(rcpt["status"],16), "block:", int(rcpt["blockNumber"],16), "gasUsed:", int(rcpt["gasUsed"],16))
    # Transfer logs to wallet from minter (AGC Transfer topic)
    topic0="0x"+keccak(b"Transfer(address,address,uint256)").hex()
    wallet_topic="0x000000000000000000000000"+WALLET[2:].lower()
    for lg in rcpt.get("logs",[]):
        if lg["address"].lower()==AGC.lower() and lg["topics"][0]==topic0 and lg["topics"][2]==wallet_topic:
            print("Transfer log to wallet:", int(lg["data"],16)/1e18, "AGC")
# balance after + pending after
bal=int(call(AGC,"0x70a08231"+encode(["address"],[WALLET]).hex()),16)/1e18
print("AGC balance after:", bal)
pend=call(MINTER,"0x"+keccak(b"pending(address)")[:4].hex()+encode(["address"],[WALLET]).hex())
vals=decode(["uint256","uint256","uint256","uint256"], bytes.fromhex(pend[2:]))
print("pending after: freeBnb",vals[0]/1e18,"freeAgc",vals[1]/1e18,"rewardVested",vals[2]/1e18,"lpWithdrawable",vals[3]/1e18)
print("block:", int(rpc("eth_blockNumber",[]),16))
