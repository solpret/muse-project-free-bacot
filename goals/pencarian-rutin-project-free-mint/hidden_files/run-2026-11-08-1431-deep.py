import json, urllib.request, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _post as _fr_post
from ankr import ankr_post
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,'0')
def enc_u(n): return format(n,'064x')
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def single(addr, data):
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout=8, retries=0)
            if not isinstance(out,dict): continue
            if out.get("error"): return "ERR"
            r=out.get("result")
            if r is None: return None
            if r=="0x" or r=="0x"+"0"*64: return 0
            if r.startswith("0x") and len(r)<=66: return int(r,16)
            return r
        except Exception:
            continue
    return "ERR:all-fail"
def block_ts(blk):
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]}, timeout=8, retries=0)
            ts=out.get("result",{}).get("timestamp")
            if ts: return int(ts,16)
        except Exception: continue
    return None
# --- Zigzoo paid-only check ---
Z='0x09ada5a12293c30d75b97c56e34967e8a4326a3c'
print("Zigzoo currentPrice:", single(Z, sel('currentPrice()')))
print("Zigzoo priceFor(1):", single(Z, sel('priceFor(uint256)')+enc_u(1)))
print("Zigzoo priceForCount(1):", single(Z, sel('priceForCount(uint256)')+enc_u(1)))
print("Zigzoo mintActive:", single(Z, sel('mintActive()')))
print("Zigzoo mintCount:", single(Z, sel('mintCount()')))
print("Zigzoo agentIdRegistry:", single(Z, sel('agentIdRegistry()')))
# --- 0x1a904Da7 ABI inputs + reads ---
A='0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B'
url=f"https://sourcify.dev/server/v2/contract/56/{A}?fields=abi"
req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
d=json.load(urllib.request.urlopen(req, timeout=20))
for e in d.get("abi",[]):
    if e.get("type")=="function" and e.get("name") in ("freeClaimed","freeMint","isFree","mintPrice","maxSupply","mint","nextId","hashpower","AGENT_ID"):
        print("1a904 ABI", e.get("name"), "inputs:", [(i.get("type"),i.get("name")) for i in e.get("inputs",[])], "stateMutability:", e.get("stateMutability"))
print("1a904 maxSupply:", single(A, sel('maxSupply()')))
print("1a904 mintPrice:", single(A, sel('mintPrice()')))
print("1a904 nextId:", single(A, sel('nextId()')))
print("1a904 freeClaimed(user):", single(A, sel('freeClaimed(address)')+enc_addr(USER)))
print("1a904 isFree(user):", single(A, sel('isFree(address)')+enc_addr(USER)))
print("1a904 isFree(1):", single(A, sel('isFree(uint256)')+enc_u(1)))
# --- Undead reads ---
U='0xC92bEc9160506065E515b225721a749Fad7664E9'
print("Undead AIRDROP_TOTAL:", single(U, sel('AIRDROP_TOTAL()')))
print("Undead remaining:", single(U, sel('remaining()')))
print("Undead remainingSupply:", single(U, sel('remainingSupply()')))
print("Undead MINT_PRICE_BNB:", single(U, sel('MINT_PRICE_BNB()')))
print("Undead mintPriceBNBFor(1):", single(U, sel('mintPriceBNBFor(uint256)')+enc_u(1)))
print("Undead airdropped(user):", single(U, sel('airdropped(address)')+enc_addr(USER)))
print("Undead paidMinted:", single(U, sel('paidMinted()')))
print("Undead X_URL:", single(U, sel('X_URL()')))
print("Undead contractURI:", single(U, sel('contractURI()')))
print("Undead mintOpen:", single(U, sel('mintOpen()')))
# --- walk-back first mint: Jinli + Alchemister ---
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"0"*24+"0"*40
def walkback(addr, first_seen, label, max_chunks=60):
    hi=first_seen; found=None
    for i in range(max_chunks):
        lo=max(0, hi-999)
        try:
            res=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(hi),"address":addr,"topics":[TRANSFER,ZERO],"pageSize":1000}, timeout=55)
            logs=res.get("result",{}).get("logs",[]) if isinstance(res,dict) else []
        except Exception as e:
            print(f"{label} walkback chunk {lo}-{hi} ERROR {e}", flush=True); return None
        n=len(logs)
        print(f"{label} walkback chunk {lo}-{hi}: {n} from-zero logs", flush=True)
        if n==0:
            break
        first_blk=min(int(l.get("blockNumber","0x0"),16) for l in logs)
        found=first_blk
        hi=lo-1
        if n<1000 and lo<=0: break
    if found is None:
        print(label, "walkback: no from-zero logs found at all in probed range")
        return None
    ts=block_ts(found)
    import datetime
    dt=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
    print(label, "FIRST MINT block", found, "ts", ts, dt)
    return found, ts
walkback('0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496', 132290865, "Jinli")
walkback('0xCafEEDDF3C15C5CD9A63D97021efDe845e1781Bc', 132123483, "Alchemister", max_chunks=100)
