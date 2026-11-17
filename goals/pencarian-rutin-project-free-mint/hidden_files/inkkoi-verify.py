import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single, batch
from Crypto.Hash import keccak
TX = "0x82334d34defe362bfc8a06d275b10cd1ab9239a33f42c43970e047c928ca3b0e"
ADDR = "0xbd4B4e7189ae9356514664146b0eD683601200A9"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return v
def rpc(method, params, ep):
    return _single(ep, method, params, 15, retries=0)
receipt = None
for i in range(12):
    for ep in EPS:
        try:
            r = rpc("eth_getTransactionReceipt", [TX], ep)
            if r: receipt = r; break
        except Exception:
            continue
    if receipt: break
    time.sleep(5)
print("RECEIPT:", json.dumps(receipt, indent=1) if receipt else "NOT FOUND after retries")
if receipt:
    blk = int(receipt["blockNumber"], 16)
    print("block:", blk, "status:", int(receipt["status"], 16), "gasUsed:", int(receipt["gasUsed"], 16))
    # block timestamp via dataseed (Ankr returns fake timestamps - use dataseed)
    for ep in EPS:
        try:
            b = rpc("eth_getBlockByNumber", [hex(blk), False], ep)
            print("block time:", b.get("timestamp"), int(b["timestamp"], 16))
            break
        except Exception as e:
            print("block read err", ep, e)
def single(sig, arg=""):
    data = sel(sig) + arg
    for ep in EPS:
        try:
            return to_int(_single(ep, "eth_call", [{"to": ADDR, "data": data}, "latest"], 8, retries=0))
        except Exception:
            continue
    return None
out = {"block_after": int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16),
       "totalSupply": single("totalSupply()"), "freeMinted": single("freeMinted()"),
       "freeClaimed_user": single("freeClaimed(address)", enc(USER)),
       "balanceOf_user": single("balanceOf(address)", enc(USER)),
       "ownerOf_711": single("ownerOf(uint256)", enc_uint(711))}
print(json.dumps(out, indent=1))
json.dump({"receipt": receipt, "after": out}, open("inkkoi-verify.json","w"), indent=1)
