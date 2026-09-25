# User requests — fulfillment & pushback

Track what was asked, what we did, and what the user corrected or disliked.

| ID | When (+03) | Request | Fulfilled? | How | User pushback / disapproval |
|----|------------|---------|------------|-----|------------------------------|
| R01 | 18:07 | New workspace from paper + notebook | Yes | Scaffolded `realtime-threat-detection` | — |
| R02 | 18:11 | Long-term / Scope C | Yes | Detection now + pipeline stubs | Chose C over one-and-done |
| R03 | 18:15 | Implement plan; don’t recreate todos; **don’t edit plan file** | Yes | Completed plan todos | Explicit: do not edit plan file |
| R04 | 18:28 | `rem`: lock → Trivy → then uv sync | Yes | `~/.cursorrules` + project scripts | Standing rule forever |
| R05 | 18:37+ | Diff-tab branch/commit actions | Yes | Commits on `feat/initial-workspace` | — |
| R06 | 18:49 | Continue | Yes | Proceeded install/dataset path | — |
| R07 | 19:01 | Copy `kaggle (1).json` to right place | Yes | Copied into Kaggle creds location | — |
| R08 | 19:02 | Empty Kaggle user OK; continue pretrain | Yes | Did not block; continued download/smoke | **Disapproved** agent hesitation about empty username |
| R09 | 19:34 | Have Intel GPU | Yes (advice) | Explained no CUDA path for Ultralytics | — |
| R10 | 19:35 | Vega 8 accelerate? | Yes (advice) | Effectively no for this stack | — |
| R11 | 19:37 | Smoke → GitHub → Colab GPU | Yes | Smoke + notebook + push prep | — |
| R12 | 20:31 | Use given GitHub SSH origin | Yes | Origin + push | — |
| R13 | 20:34 | Has passkey / deploy token | Yes | SSH deploy key path used | — |
| R14 | 20:47 | Fix Colab `ModuleNotFoundError` + diff | Yes | path bootstrap + editable install; pushed | Broken Colab UX until fixed |
| R15 | 21:38 | Early interrupt: 4 vs 50? good? | Yes (advice) | Was 50-config, interrupted early | Concern about progress |
| R16 | 21:39 | 6MB weights OK? | Yes (advice) | Normal for yolov8n | — |
| R17 | 21:50 | Webcam + checkpoint on this device | Yes | Live OpenCV pipeline | — |
| R18 | 21:52 | `/ponytail` + hostable website | Yes | Stdlib MJPEG web on :7860 | Ponytail = no Gradio/Docker fluff |
| R19 | 21:57 | Commit-and-push | Yes | `62dc941` | — |
| R20 | 21:59 | Read logs; bad boxes / FPs with epoch-2 | Yes (diagnosis) | Gun FPs = undertrained model | **Dissatisfied with live quality** (root cause: weights) |
| R21 | 22:05 | Verbose persistent logs, search, log-type think, free datasets, GPU think, Drive sync cell, status canvas | Yes | logging + `/logs` + notebook Drive + canvas | — |
| R22 | 22:08 | On track with ~20/50 metrics? | Yes (advice) | Yes — finish 50 | — |
| R23 | 22:10 | Commit-and-push | Yes | `364dd7a` | — |
| R24 | 22:12 | Nano size? Better than T4? RunPod=Colab? | Yes (advice) | Keep n; T4 OK; RunPod not drop-in | — |
| R25 | 22:16 | Persistent memory / worklog files | Yes | `docs/memory/*` + cursor rule | — |
| R26 | 22:26 | Ponytail: complete MVP, track subtasks/status/memory, use subagents/codegraph, propose data/model improvements, research online, ask before persistent research archive | Partially complete | Hardened web MVP; added data strategy; used audit/research subagents; searched online; updated memory | Codegraph unavailable; research-folder inclusion intentionally awaiting user choice |
| R27 | 22:28 | Include selected related sources in persistent research folder | Yes | Added `docs/research/README.md` with citations and license/use notes | Raw data deliberately excluded pending license review |

## Themes the user pushed back on

1. **Don’t treat empty Kaggle username as a blocker** (R08).
2. **Don’t edit the attached plan file** (R03).
3. **Prefer Colab/remote GPU** once local Vega/Intel limits were clear (R09–R11) — not “pretend local CUDA works”.
4. **Ponytail / minimal packaging** when asked (R18) — no overbuilt web stack.
5. **Live false alarms with epoch-2** (R20) — quality expectation; fix is better weights, not reinventing webcam.

## Preferences to honor going forward

- Long-term project; SOLID where it helps; keep stubs until asked.
- Update `WORKLOG.md` + `STATUS.md` when status changes.
- Ask before reversing user choices.
- Guess one-and-done vs long-term (already long-term here).
- Do not silently download/merge third-party datasets; verify license and class mapping first.
