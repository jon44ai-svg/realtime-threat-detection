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
| Live webcam / RTSP capture | **Stub** |
| Gemini 2.5 Flash Lite two-stage VLM | **Stub** |
| Email / desktop alerts | **Stub** (logging works) |

## Setup

Requires **Python ≥ 3.10** (project pins **3.11** via `.python-version`) and [uv](https://github.com/astral-sh/uv).

```powershell
cd ~/Projects/realtime-threat-detection
uv sync --extra dev
copy .env.example .env
```

### Kaggle credentials

1. Create an API token at https://www.kaggle.com/settings → place `kaggle.json` in `%USERPROFILE%\.kaggle\`, **or**
2. Set `KAGGLE_USERNAME` and `KAGGLE_KEY` in `.env`.

Accept the dataset license on Kaggle in the browser if prompted on first download:

https://www.kaggle.com/datasets/gajendramandalcsvtu/custum-dataset-and-public-data-for-model-training

## Reproduce detection results

```powershell
# 1. Download ~274MB consolidated dataset (train/valid/test YOLO layout)
uv run python scripts/download_data.py

# 2. Optional EDA (writes plots under runs/eda/)
uv run python scripts/explore_data.py

# 3. Train (default yolov8n @ 640, batch=8 for ~4GB VRAM)
uv run python scripts/train.py --epochs 50
uv run python scripts/train.py --epochs 100

# Optional larger model if you have more VRAM:
# uv run python scripts/train.py --epochs 100 --model yolov8s.pt

# CPU-only:
# uv run python scripts/train.py --epochs 50 --device cpu

# 4. Evaluate vs paper Table II
uv run python scripts/evaluate.py --weights runs/detect/train_50/weights/best.pt --epochs 50
uv run python scripts/evaluate.py --weights runs/detect/train_100/weights/best.pt --epochs 100
```

Interactive EDA notebook: [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb).

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

## Pipeline stub

```powershell
uv run python scripts/run_pipeline.py --describe-only
```

Stages follow paper Fig. 1 under `src/threat_detection/pipeline/`.

## Tests

```powershell
uv run pytest
```

## Layout

```
configs/          # data.yaml, train_50.yaml, train_100.yaml
src/threat_detection/
  data/           # download + explore
  training/       # train + evaluate
  pipeline/       # live system stubs
scripts/          # CLI entrypoints
notebooks/        # cleaned EDA notebook
docs/             # paper + original notebook
data/raw/         # gitignored dataset
runs/             # gitignored Ultralytics + EDA outputs
```

## License / ethics

This project reproduces a **research** surveillance detector. Use only on data and cameras you are authorized to process. Do not deploy for unlawful monitoring.
