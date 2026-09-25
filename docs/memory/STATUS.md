# Project status

**Last updated:** 2026-09-25 22:53 Asia/Jerusalem (+03)  
**Branch:** `feat/initial-workspace` @ `ffe69f2` (local MVP fixes uncommitted)  
**Hardware (local):** Windows · AMD Ryzen / Vega 8 + Intel iGPU · **no NVIDIA CUDA** · webcam index 0  
**Hardware (train):** Colab **Tesla T4** · yolov8n · batch 16 · imgsz 640

---

## Snapshot (now)

| Area | State |
|------|--------|
| Workspace scaffold (uv, package, configs, scripts) | Done |
| Kaggle dataset download + EDA | Done (local `data/raw` gitignored) |
| Train/eval code vs paper Table II | Done |
| Pipeline stubs (VLM / email / desktop) | Stubbed; live path skips VLM |
| GitHub remote + Colab notebook | Done |
| Local smoke train (CPU, fraction) | Done |
| Live webcam + hostable MJPEG web UI | Done; web MVP hardening added |
| Persistent logs + search | Done |
| Colab Drive `sync_artifacts` | Done (in notebook; must be run) |
| Colab **50-epoch** finished `best.pt` | Done: mAP50 0.736, mAP50-95 0.486, recall 0.672 |
| Colab **100-epoch** run | Not started |
| Pull weights to local / Drive verified | 50-epoch ZIP extracted safely; checkpoint loads locally; Drive still unverified |
| Live demo with good boxes | Blocked on finished 50/100 weights |
| Domain-gap dataset mix (webcam-like) | Not started (optional after Table II) |
| Gemini VLM 2-stage | Stub |
| Email / desktop alerts | Stub (logging only) |
| Runtime failure visibility / web cooldown | Done |
| Dataset merge/preprocessing strategy | Documented; no third-party data merged |
| Related research shortlist | Archived in `docs/research/README.md` (links/caveats only) |

---

## Missing (actionable)

1. Sync Colab 50 artifacts to Drive; the current mount cell is waiting for authorization.
2. Run 100 epochs → sync → evaluate.
3. Copy named `best.pt` from Drive to local; serve with `--conf ~0.65`.
4. Optional later: free Roboflow/CCTV mix + own webcam frames for domain gap.
5. Optional later: implement VLM / real alerts.
6. If desired, later download selected datasets after license review.

---

## Bottlenecks (one-liners)

See [`BOTTLENECKS.md`](BOTTLENECKS.md). Primary: **usable live detection quality is bottlenecked by unfinished GPU training**, not by webcam code. Codegraph was requested but is unavailable in the exposed tool catalog.

---

## Paper Table II targets (50 / 100 epochs)

| Metric | 50 ep | 100 ep |
|--------|------:|-------:|
| Precision | 0.862 | 0.857 |
| Recall | 0.676 | 0.757 |
| mAP@0.5 | 0.777 | 0.819 |
| mAP@0.5:0.95 | 0.556 | 0.570 |

Exact match not required; use `scripts/evaluate.py` comparison table.
