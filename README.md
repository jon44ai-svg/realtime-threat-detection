# Real-Time Threat Detection

Long-term workspace to reproduce **YOLOv8 weapon / blunt-object detection** results from:

> Mandal, Patra, Mahant — *Real-Time Threat Detection from Surveillance Cameras using Machine Learning*

and to grow into the paper’s full live pipeline (temporal buffer → Gemini VLM → threat levels → alerts).

Reference copies live in [`docs/`](docs/) (paper PDF + original Colab notebook). The notebook is used for **EDA inspiration only** — it does not train YOLO; this repo does.

## What’s implemented vs stubbed

| Area | Status |
|------|--------|
| Kaggle dataset download + `data.yaml` | Implemented |
| EDA (tree, split counts, annotation viz) | Implemented |
| YOLOv8 train 50 / 100 epochs @ 640 | Implemented |
| Val metrics vs paper Table II | Implemented |
| Live webcam / RTSP capture | Implemented (desktop + hostable web MJPEG) |
| Gemini 2.5 Flash Lite two-stage VLM | **Stub** |
| Email / desktop alerts | **Stub** (logging works) |

## Setup

Requires **Python ≥ 3.10** (project pins **3.11** via `.python-version`), [uv](https://github.com/astral-sh/uv), and [Trivy](https://trivy.dev/) for dependency verification.

**Install order (resolve → verify → install):** never `uv sync` until the lockfile has been scanned.

```powershell
cd ~/Projects/realtime-threat-detection

# 1. Resolve versions only (no install)
uv lock --python 3.11

# 2. Scan lockfile / project with Trivy (HIGH+CRITICAL)
pwsh scripts/verify_deps.ps1

# 3. Install only after a clean (or accepted) scan
uv sync --extra dev

copy .env.example .env
```

### Kaggle credentials

1. Create an API token at https://www.kaggle.com/settings → place `kaggle.json` in `%USERPROFILE%\.kaggle\`, **or**
2. Set `KAGGLE_USERNAME` and `KAGGLE_KEY` in `.env`.

Accept the dataset license on Kaggle in the browser if prompted on first download:

https://www.kaggle.com/datasets/gajendramandalcsvtu/custum-dataset-and-public-data-for-model-training

## Reproduce detection results

### Local smoke test (CPU / Vega — no CUDA)

```powershell
uv run python scripts/download_data.py
uv run python scripts/train.py --smoke --device cpu
```

Full 50/100-epoch runs are **slow on CPU**. Prefer Colab GPU below.

### Local full train (if you have NVIDIA CUDA)

```powershell
uv run python scripts/train.py --epochs 50 --device 0
uv run python scripts/train.py --epochs 100 --device 0
uv run python scripts/evaluate.py --weights runs/detect/train_100/weights/best.pt --epochs 100
```

Configs default to `device: cpu` for this machine. Override with `--device 0` on Colab/NVIDIA.

### Colab GPU (recommended for Table II)

1. Push this repo to GitHub (see below).
2. Open [`notebooks/colab_train.ipynb`](notebooks/colab_train.ipynb) in Colab **or** File → Upload notebook.
3. Runtime → Change runtime type → **GPU**.
4. Set `REPO_URL` / `BRANCH` in the first cell; upload `kaggle.json` to `/content/`.
5. Run all cells (download → train 50 → eval → train 100 → eval).

Interactive EDA: [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb).

### Paper Table II targets (100 epochs)

| Metric | Paper |
|--------|------:|
| Precision | 0.857 |
| Recall | 0.757 |
| mAP@0.5 | 0.819 |
| mAP@0.5:0.95 | 0.570 |
| Gun mAP@0.5 | 0.919 |
| Knife mAP@0.5 | 0.785 |
| Blunt object mAP@0.5 | 0.754 |

Exact numeric match is **not** expected (GPU, seed, Ultralytics version). Use the comparison table from `evaluate.py` as a guide.

Classes in `configs/data.yaml`: `blunt_object`, `gun`, `knife`.

## Push to GitHub (then open in Colab)

`gh` must be logged in once: `gh auth login`

```powershell
cd ~/Projects/realtime-threat-detection
git add -A
git status   # confirm data/raw and .env are NOT listed
git commit -m "Prepare Colab GPU training workflow and local smoke config."
# first push — creates repo under your account
gh repo create realtime-threat-detection --private --source=. --remote=origin --push
# later pushes
git push -u origin HEAD
```

Then in Colab, clone:

`https://github.com/jon44ai-svg/realtime-threat-detection.git` branch `feat/initial-workspace`

SSH remote: `git@github.com:jon44ai-svg/realtime-threat-detection.git`

Do **not** commit `data/raw/`, `runs/`, `.env`, or `kaggle.json` (already gitignored).

## Live webcam (this machine)

Desktop OpenCV window:

```powershell
uv run python scripts/run_pipeline.py --weights path\to\best.pt --source 0 --device cpu
```

Hostable website (LAN: bind `0.0.0.0:7860`):

```powershell
uv run python scripts/serve.py --weights path\to\best.pt --source 0 --device cpu
```

Open http://127.0.0.1:7860/ — press Ctrl+C in the terminal to stop. VLM stays stubbed; detections still label threat levels on the stream.

## Tests

```powershell
uv run pytest
```

## Layout

```
configs/          # data.yaml, train_50/100/smoke.yaml
src/threat_detection/
  data/           # download + explore
  training/       # train + evaluate
  pipeline/       # live system stubs
scripts/          # CLI entrypoints + verify_deps.ps1
notebooks/        # 01_eda.ipynb + colab_train.ipynb
docs/             # paper + original notebook
data/raw/         # gitignored dataset
runs/             # gitignored Ultralytics + EDA outputs
```

## License / ethics

This project reproduces a **research** surveillance detector. Use only on data and cameras you are authorized to process. Do not deploy for unlawful monitoring.
