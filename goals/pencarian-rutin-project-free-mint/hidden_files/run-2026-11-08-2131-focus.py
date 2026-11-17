import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import _post as fr_post
from Crypto.Hash import keccak
import onchain_nft_scan as scan
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(addr,data,tag):
    for ep in EPS:
        try:
            out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=8,retries=0)
            r=out.get("result")
            if r is None: return None
            if r=="0x": return None
            return int(r,16)
        except Exception as e:
            continue
    return None
def call_raw(addr,data):
    for ep in EPS:
        try:
            out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=8,retries=0)
            return out.get("result")
        except Exception:
            continue
    return None
out={}
# --- BAHUANG2: find per-user free view from Sourcify ABI
BAHU="0x57CC350b844484Eac0DE444526d295C90F9cCbB5"
st,abi=scan.sourcify_abi(BAHU)
print("BAHUANG2 sourcify:",st,flush=True)
fns=[]
if isinstance(abi,list):
    for it in abi:
        if it.get("type")=="function": fns.append(it.get("name")+str([i.get("type") for i in it.get("inputs",[])]))
print("BAHUANG2 fns:",fns,flush=True)
out["bahuang2_abi_status"]=st; out["bahuang2_fns"]=fns
# try candidate per-user views
for sig in ["freeCount(address)","freeMintedBy(address)","freeClaimed(address)","freeMinted(address)","mintedFree(address)","freeMints(address)","claimedFree(address)"]:
    v=call(BAHU, sel(sig)+enc(USER), sig)
    print(f"BAHUANG2 {sig}(user) = {v}",flush=True)
    out["bahuang2_"+sig]=v
for sig in ["freeMinted()","freeClaimed()","mintOpen()","totalMinted()","MAX_SUPPLY()","FREE_CAP()","FREE_PER_WALLET()","mintStart()","mintEnd()"]:
    v=call(BAHU, sel(sig), sig)
    print(f"BAHUANG2 {sig} = {v}",flush=True)
    out["bahuang2_"+sig]=v
# quote for 1 (costWei_1 in snapshot was 430744843984217) - try quote/cost fns if in ABI
for sig in ["quote(uint256)","cost(uint256)","price(uint256)","getPrice(uint256)","mintPrice()"]:
    try:
        data=sel(sig)+(str(1).rjust(64,"0") if "(uint256)" in sig else "")
        v=call(BAHU,data,sig)
        print(f"BAHUANG2 {sig} = {v}",flush=True); out["bahuang2_"+sig]=v
    except Exception as e:
        print(f"BAHUANG2 {sig} err {e}",flush=True)
# --- binanceai.fun pending claim re-check
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"; TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
for addr,sigs in [(MINT,["launched()","failed()","isRefundPhase()","totalShares()","tokenClaimed(address)"]), (TOKEN,["balanceOf(address)"])]:
    for sig in sigs:
        data=sel(sig)+(enc(USER) if "(address)" in sig else "")
        v=call(addr,data,sig)
        print(f"BINANCEAI {addr[:10]} {sig} = {v}",flush=True)
        out[f"binanceai_{addr[:6]}_{sig}"]=v
# also tokenClaimed on MINT without user? already user. claimable? try claimable(address)/claimAmount(address)
for sig in ["claimable(address)","claimAmount(address)","pendingClaim(address)"]:
    v=call(MINT, sel(sig)+enc(USER), sig)
    print(f"BINANCEAI MINT {sig}(user) = {v}",flush=True); out["binanceai_"+sig]=v
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-08-2131-focus.json","w"),indent=1)
print("focus done",flush=True)
