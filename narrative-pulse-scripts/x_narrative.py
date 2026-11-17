#!/usr/bin/env python3
"""X-search narrative source for the narrative-pulse cron (READ-ONLY).

Wiring approved by the user 2026-11-01 ~11:46 WIB ("Ya, sambungkan
X search ke narasi"). twitterapi.io (custom.twitterapi) is the provider;
the key never appears here (authd surrogate via bin/twitterapi.py).

Role in the pipeline (narrow, and deliberately NOT more):
- This script is ONE narrative source. A fast-layer token that ALSO has
  X discussion becomes a narrative reported_signal under the existing
  multi-source convergence rule (fast layer + X = 2 sources).
- It NEVER confirms money-flow, NEVER changes any gate, score,
  second-sighting rule, or sizing, and NEVER feeds the trading loop
  directly. Feed money-flow rules are untouched: a narrative-only
  signal still enters the feed as snapshot-only and still needs
  second-sighting money-flow confirmation + full gates + score >= 60.
- It NEVER mints, previews, executes, approves, swaps, signs, or
  connects a wallet. Read-only search.

Candidate-triggered, budget-capped (this is what makes the $1 starter
last instead of burning in a day):
- Only tokens first-seen by fast_discovery.py within the last 30
  minutes, never checked before, ordered by h24 volume desc.
- Max 2 searches per run, 1 page each (max 20 tweets = 300 credits).
- Hard daily cap 3.000 credits (~200 tweets/day). At cap, the script
  stops WITHOUT calling the API. At max cap every day, the $1 starter
  (100.000 credits) lasts ~33 days; ongoing cost at cap is ~$0,90/month.
- Untopped accounts are limited to 1 request / 5 s: sleep 5 s between
  searches. A failed API call never fails the cron run (exit 0, the
  worker records "X search unavailable" and continues with other
  sources). A failed call is never counted as discussion.

Verdict:
- Query = the exact contract address (precise, low false positives;
  a symbol/name search would drown in same-symbol tokens).
- x_discussion = True only if >= 2 DISTINCT authors mentioned the CA
  in the last 24 h (from the returned page's createdAt + author).
  Otherwise the token is recorded as X-MISS with honest counts.
- Tweets are evidence, not endorsement: a discussion hit says people
  are talking about the CA, nothing about whether it is safe or a buy.

State: ~/workspace/narrative-pulse/x_narrative_state.json
  {"checked": {ca: {name, checked_at, tweets, authors, x_discussion,
                    newest_url, credits_est}},
   "usage": {YYYY-MM-DD: {searches, tweets, credits_est}}}
Timestamps use explicit WIB (cron workers run with UTC localtime).

Usage:
  python3 x_narrative.py            # normal run (cron worker calls this)
  python3 x_narrative.py --selftest # offline logic test, no API calls
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
BASE = os.path.expanduser("~/workspace/narrative-pulse")
FAST_STATE = os.path.join(BASE, "fast_discovery_state.json")
STATE = os.path.join(BASE, "x_narrative_state.json")

MAX_PER_RUN = 2
WINDOW_MIN = 30
DAILY_CREDIT_CAP = 3000
MIN_AUTHORS = 2
LOOKBACK_H = 24
CREDITS_PER_TWEET = 15
MIN_CREDITS_PER_REQUEST = 15
SLEEP_BETWEEN_CALLS = 5


def now_wib():
    return datetime.now(WIB)


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


def parse_tweet_time(s):
    """'Sun Nov 01 00:18:13 +0000 2026' -> aware datetime, or None."""
    try:
        return datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")
    except Exception:
        return None


def verdict(tweets, now_utc):
    """Pure function: (x_discussion, tweet_count, authors, newest_url)."""
    cutoff = now_utc - timedelta(hours=LOOKBACK_H)
    authors = set()
    newest_url = None
    newest_dt = None
    count = 0
    for t in tweets or []:
        dt = parse_tweet_time(t.get("createdAt", ""))
        if dt is None or dt < cutoff:
            continue
        count += 1
        author = (t.get("author") or {}).get("userName")
        if author:
            authors.add(author)
        if newest_dt is None or dt > newest_dt:
            newest_dt = dt
            newest_url = t.get("url")
    return (len(authors) >= MIN_AUTHORS, count, sorted(authors), newest_url)


def budget_ok(usage, today):
    u = usage.get(today, {"searches": 0, "tweets": 0, "credits_est": 0})
    return u["credits_est"] + CREDITS_PER_TWEET * 20 <= DAILY_CREDIT_CAP


def select_candidates(fast, checked, now):
    """Un-checked tokens first-seen within WINDOW_MIN, volume desc."""
    window_start = now - timedelta(minutes=WINDOW_MIN)
    cands = []
    for ca, info in fast.items():
        if not isinstance(info, dict) or ca in checked:
            continue
        fs = info.get("first_seen", "")
        try:
            fs_dt = datetime.strptime(fs, "%Y-%m-%dT%H:%M:%S+07:00")
            fs_dt = fs_dt.replace(tzinfo=WIB)
        except Exception:
            continue
        if fs_dt < window_start:
            continue
        vol = info.get("volume_h24") or 0
        try:
            vol = float(vol)
        except Exception:
            vol = 0
        cands.append((vol, ca, info))
    cands.sort(key=lambda x: -x[0])
    return [(ca, info) for _, ca, info in cands[:MAX_PER_RUN]]


def main():
    state = load_json(STATE, {"checked": {}, "usage": {}})
    checked = state.setdefault("checked", {})
    usage = state.setdefault("usage", {})
    today = now_wib().strftime("%Y-%m-%d")

    fast = load_json(FAST_STATE, {})
    cands = select_candidates(fast, checked, now_wib())
    if not cands:
        print("X-SKIP no un-checked fast-layer token first-seen within "
              f"{WINDOW_MIN} min")
        return 0

    # Import here so --selftest never touches the connector.
    sys.path.insert(0, os.path.expanduser(
        "~/workspace/custom-connectors/custom.twitterapi/bin"))
    try:
        from twitterapi import advanced_search
    except Exception as e:
        print(f"X-ERROR cannot load twitterapi helper: {e}")
        return 0

    for i, (ca, info) in enumerate(cands):
        if not budget_ok(usage, today):
            print(f"X-SKIP daily credit cap reached "
                  f"({DAILY_CREDIT_CAP}); no API call for {ca}")
            break
        if i > 0:
            time.sleep(SLEEP_BETWEEN_CALLS)
        try:
            res = advanced_search(ca, "Latest")
        except Exception as e:
            print(f"X-ERROR search failed for {ca}: {e}")
            continue
        tweets = res.get("tweets") or []
        disc, count, authors, newest_url = verdict(
            tweets, datetime.now(timezone.utc))
        credits = max(MIN_CREDITS_PER_REQUEST,
                      CREDITS_PER_TWEET * len(tweets))
        u = usage.setdefault(today, {"searches": 0, "tweets": 0,
                                     "credits_est": 0})
        u["searches"] += 1
        u["tweets"] += len(tweets)
        u["credits_est"] += credits
        checked[ca] = {
            "name": info.get("name"),
            "checked_at": now_wib().strftime("%Y-%m-%dT%H:%M:%S+07:00"),
            "tweets_returned": len(tweets),
            "tweets_last_24h": count,
            "authors": authors,
            "x_discussion": disc,
            "newest_url": newest_url,
            "credits_est": credits,
        }
        save_json(STATE, state)
        tag = "X-HIT" if disc else "X-MISS"
        print(f"{tag} {ca} {info.get('name')} authors={len(authors)} "
              f"tweets24h={count} returned={len(tweets)} "
              f"credits={credits} newest={newest_url}")
    return 0


def selftest():
    now = datetime.now(timezone.utc)
    def tw(minutes_ago, author, url):
        dt = now - timedelta(minutes=minutes_ago)
        return {"createdAt": dt.strftime("%a %b %d %H:%M:%S +0000 %Y"),
                "author": {"userName": author}, "url": url}
    # 2 distinct authors in window -> HIT
    assert verdict([tw(10, "a", "u1"), tw(20, "b", "u2")], now)[0] is True
    # 1 author twice -> MISS
    assert verdict([tw(10, "a", "u1"), tw(20, "a", "u2")], now)[0] is False
    # old tweets (>24h) -> MISS
    assert verdict([tw(2000, "a", "u1"), tw(2000, "b", "u2")], now)[0] is False
    # budget: 2900 used + 300 max page > 3000 -> blocked
    assert budget_ok({"2026-11-01": {"credits_est": 2900}}, "2026-11-01") is False
    assert budget_ok({"2026-11-01": {"credits_est": 2600}}, "2026-11-01") is True
    # selection: only un-checked + within window, volume desc
    now_w = now_wib()
    fmt = "%Y-%m-%dT%H:%M:%S+07:00"
    fast = {
        "0xold": {"first_seen": (now_w - timedelta(minutes=90)).strftime(fmt),
                  "volume_h24": 99999, "name": "OLD"},
        "0xchecked": {"first_seen": now_w.strftime(fmt),
                      "volume_h24": 99999, "name": "CHK"},
        "0xlow": {"first_seen": now_w.strftime(fmt),
                  "volume_h24": 10, "name": "LOW"},
        "0xhigh": {"first_seen": now_w.strftime(fmt),
                   "volume_h24": 5000, "name": "HIGH"},
    }
    sel = select_candidates(fast, {"0xchecked": {}}, now_w)
    assert [ca for ca, _ in sel] == ["0xhigh", "0xlow"], sel
    print("SELFTEST OK: verdict, budget, selection all pass")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    sys.exit(main())
