import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
ADDR="0x869d330bb48e7ab32da16745ef9a36a69d34f12f"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD="0"*24+USER[2:].lower()
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def dec(h):
    if not h or len(h)<66: return None
    try: return int(h[2:66],16)
    except Exception: return None
def dec_str(h):
    # decode abi string return
    try:
        b=bytes.fromhex(h[2:])
        off=int.from_bytes(b[32:64],'big'); ln=int.from_bytes(b[64:96],'big')
        return b[64+32:64+32+ln].decode()
    except Exception as e: return f"str-decode-err {e}"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
calls=[
 ("name","name()","str"),("symbol","symbol()","str"),("totalSupply","totalSupply()","uint"),
 ("freeMinted","freeMinted()","uint"),("mintActive","mintActive()","bool"),
 ("currentPrice","currentPrice()","uint"),("priceFor_user","priceFor(address)","user"),
 ("quoteBulk_user1","quoteBulk(address,uint256)","user1"),("freeUsed_user","freeUsed(address)","user"),
 ("holdsAgentId_user","holdsAgentId(address)","user"),("MAX_SUPPLY","MAX_SUPPLY()","uint"),
 ("MAX_PER_WALLET","MAX_PER_WALLET()","uint"),("mintCount_user","mintCount(address)","user"),
 ("agentIdRegistry","agentIdRegistry()","addr"),("deckRemaining","deckRemaining()","uint"),
 ("FREE_MINT_BONUS","FREE_MINT_BONUS()","uint"),("baseURI","baseURI()","str"),
]
out={}
for label,sig,kind in calls:
    data=sel(sig)
    if kind=="user": data+=PAD
    elif kind=="user1": data+=PAD+format(1,"064x")
    val=None; err=None
    for ep in EPS:
        try:
            val=_single(ep,"eth_call",[{"to":ADDR,"data":data},"latest"],12,retries=0); break
        except Exception as e: err=str(e)[:120]
    if val is None: out[label]={"error":err}
    elif kind=="str": out[label]=dec_str(val)
    elif kind=="addr": out[label]="0x"+val[26:66]
    else: out[label]=dec(val)
print(json.dumps(out,indent=1))
