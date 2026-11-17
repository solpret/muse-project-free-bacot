#!/bin/bash
cd ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/
for a in 0xeC8A897a0De48a6fbfb83646f790581a2280aDB3 0xe460d44d4A5eb9BEF848C0815d689827f6890D59 0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a 0x6e1aCD79f0Be1bF77dc04fC89B1DF7c3f42c0C65 0xe0fca35494e927D8f9318593eC7E2Fe45675c630 0xF58064F1FE93f066498DB4F9748d541E5D6CdE02 0xEDF602c1887EEca57688E86105CcB9B47ACBe4C6; do
  short=${a:0:10}
  curl -s --max-time 90 -o "run-2026-11-05-1931-abi-${short}.json" -w "$a http=%{http_code} size=%{size_download}\n" "https://sourcify.dev/server/v2/contract/56/${a}?fields=abi" &
done
wait
