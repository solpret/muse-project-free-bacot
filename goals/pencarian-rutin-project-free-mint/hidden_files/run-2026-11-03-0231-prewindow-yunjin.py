import sys, json, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
ZERO = "0x0000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def topic_addr(a): return "0x000000000000000000000000" + a[2:].lower()
addr="0x6F726D4cF7263f1F7562d5868EC09806d7ef70f8"
body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(131280000), "toBlock": hex(131295677),
                 "address": [addr], "topics": [[TRANSFER, topic_addr(ZERO)]], "pageSize": 100}, timeout=60)
r = body.get("result", body)
logs = r.get("logs", []) if isinstance(r, dict) else []
print("Yunjin pre-window from-zero logs (131280000-131295677):", len(logs))
if logs:
    first = min(logs, key=lambda l: int(l["blockNumber"], 16))
    print(" earliest:", int(first["blockNumber"],16), first["transactionHash"])
json.dump(logs, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0231-prewindow-yunjin.json","w"), indent=1)
# fresh state + first window mint block timestamp
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out={"block": int(_single("https://bsc-dataseed.binance.org/","eth_blockNumber",[],8,retries=0),16)}
for fn,arg in [("totalMinted()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintedBy(address)",enc(USER)),("costFor(uint256)","0"*63+"1"),("owner()",""),("agentIdRegistry()","")]:
    try:
        v=_single("https://bsc-dataseed.binance.org/","eth_call",[{"to":addr,"data":sel(fn)+arg},"latest"],8,retries=0)
        out[fn]=int(v,16) if v and v!="0x" else v
    except Exception as e: out[fn]=f"ERR {e}"
print(out)
b=_single("https://bsc-dataseed.binance.org/","eth_getBlockByNumber",[hex(131295702),False],8,retries=0)
ts=int(b["timestamp"],16)
print("first window block 131295702 WIB:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat())
out["firstWindowBlockWib"]=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat()
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0231-yunjin-verify.json","w"), indent=1)
