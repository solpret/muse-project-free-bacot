import json, sys
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home()/"workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod
def topic(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()
T_TRANSFER=topic("Transfer(address,address,uint256)")
ZERO="0x"+"0"*64
tier=json.load(open(Path.home()/"workspace/narrative-pulse/tier-ab-watch-state.json"))
feed=["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b","0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7","0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq=[]
for w in list(tier["wallets"].keys())+feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked={"0x"+"0"*24+w[2:] for w in uniq}
c="0xc7c171e479f6ad8a728e77b7484bb7d0b4984d0f"
data=ankr_mod.get_logs(c,131590150,131598187)
logs=((data.get("result") or {}).get("logs") or [])
print("NOTBNB all logs in window:",len(logs))
for lg in logs:
    topics=lg.get("topics") or []
    print(lg.get("transactionHash"), lg.get("blockNumber"), topics, lg.get("data"))
    if len(topics)>=3 and topics[1]==ZERO:
        print("  zero-from to:", "0x"+topics[2][-40:], "tracked?" , topics[2] in tracked)
# topic-filtered
data2=ankr_mod.get_logs(c,131590150,131598187,topics=[T_TRANSFER,ZERO,sorted(tracked)])
logs2=((data2.get("result") or {}).get("logs") or [])
print("NOTBNB topic-filtered tracked zero-from logs:",len(logs2))
for lg in logs2:
    print(" ",lg.get("transactionHash"), lg.get("blockNumber"), lg.get("topics"), lg.get("data"))
