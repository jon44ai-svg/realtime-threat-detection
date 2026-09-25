# Bottlenecks

What is waiting on what. Update when a blocker clears.

| # | Desired outcome | Bottlenecked by | Not bottlenecked by | Severity | Last reviewed |
|---|-----------------|-----------------|---------------------|----------|---------------|
| B1 | Webcam demo with tight boxes / low FPs | Finished **50/100-epoch `best.pt`** (still training on Colab T4) | Webcam code, MJPEG server, logging | High | 2026-09-25 22:16 |
| B2 | Paper Table II comparison numbers | Same as B1 + run `scripts/evaluate.py` | Train/eval code exists | High | 2026-09-25 22:16 |
| B3 | Artifacts survive Colab disconnect | User must **run Drive mount + `sync_artifacts`** after trains | Presence of sync cell in notebook | High | 2026-09-25 22:16 |
| B4 | Full train on this Windows box | **No CUDA**; Vega 8 / Intel don’t accelerate Ultralytics YOLO train | Dataset download, smoke path | High (local) | 2026-09-25 19:37 |
| B5 | Faster wall-clock than T4 | Optional stronger GPU / paid RunPod | Model quality of yolov8n itself | Low | 2026-09-25 22:12 |
| B6 | Higher accuracy than nano plateau | Only if 50/100 mAP stalls ≪ paper → then try **yolov8s** | T4 capacity for nano | Low until proven | 2026-09-25 22:12 |
| B7 | Webcam-domain robustness (blur/distance) | Domain gap of paper stills vs live cam; needs free mix / own frames **after** Table II | Logging verbosity | Medium later | 2026-09-25 22:05 |
| B8 | Paper full pipeline (VLM → alerts) | Unimplemented Gemini + SMTP/desktop stubs | Detection path | Medium later | 2026-09-25 22:16 |
| B9 | Drop-in RunPod = Colab notebook | `google.colab` / Drive APIs; need volume + CLI | Core `scripts/train.py` | Low | 2026-09-25 22:12 |
| B10 | Cleaner live logs | Was thin INFO-only; **mitigated** by persistent verbose log + search | — | Resolved | 2026-09-25 22:05 |
| B11 | Colab imports | Was `ModuleNotFoundError`; **mitigated** by editable install + `sys.path` | — | Resolved | 2026-09-25 20:47 |
| B12 | `data.yaml` path | Ultralytics cwd-relative path; **fixed** to `data/raw` | — | Resolved | 2026-09-25 19:xx |
| B13 | Persistent research folder | Resolved for citations; raw downloads still require license review | Research index exists | Low | 2026-09-25 22:28 |
| B14 | Codegraph request | No codegraph tool is exposed in this Cursor session | Manual dependency/runtime graph audit | Low | 2026-09-25 22:26 |

## Critical path (now)

```
Colab finish 50 → sync_artifacts → evaluate
        ↓
Colab 100 → sync → evaluate
        ↓
Copy best.pt local → serve/run_pipeline --conf 0.65
        ↓
(optional) domain fine-tune / VLM
```

## Dependency install bottleneck (standing)

Any new Python package: **`uv lock` → Trivy → `uv sync`**. Never install first.

## MVP hardening completed 2026-09-25 22:26

The web runtime now propagates custom log directories, reports capture-thread
exceptions in `/status` and the persistent log, and applies the same confidence
gate/cooldown and temporal buffering used by the desktop pipeline.
