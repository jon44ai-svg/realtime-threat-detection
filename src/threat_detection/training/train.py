"""Train YOLOv8 for 50 or 100 epochs (paper Table II checkpoints)."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def load_train_config(config_path: Path) -> dict:
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def resolve_path(path_str: str, base: Path = PROJECT_ROOT) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = (base / p).resolve()
    return p


def train(
    config_path: Path,
    model_override: str | None = None,
    device_override: str | None = None,
    epochs_override: int | None = None,
) -> Path:
    """
    Run Ultralytics YOLO training from a YAML config.

    Returns path to best.pt weights.
    """
    from ultralytics import YOLO

    cfg = load_train_config(config_path)
    model_name = model_override or cfg.get("model", "yolov8n.pt")
    data_yaml = resolve_path(str(cfg["data"]))
    if not data_yaml.exists():
        raise FileNotFoundError(
            f"data.yaml not found at {data_yaml}. Run scripts/download_data.py first."
        )

    train_kwargs = {
        "data": str(data_yaml),
        "epochs": epochs_override or int(cfg.get("epochs", 100)),
        "imgsz": int(cfg.get("imgsz", 640)),
        "batch": int(cfg.get("batch", 8)),
        "project": str(resolve_path(str(cfg.get("project", "runs/detect")))),
        "name": str(cfg.get("name", "train")),
        "exist_ok": bool(cfg.get("exist_ok", True)),
        "patience": int(cfg.get("patience", 50)),
        "seed": int(cfg.get("seed", 0)),
        "save": bool(cfg.get("save", True)),
        "plots": bool(cfg.get("plots", True)),
        "workers": int(cfg.get("workers", 4)),
    }
    device = device_override if device_override is not None else cfg.get("device", "0")
    train_kwargs["device"] = device

    print(f"Training {model_name} with config {config_path}")
    print(f"  data={data_yaml}")
    print(f"  epochs={train_kwargs['epochs']} imgsz={train_kwargs['imgsz']} batch={train_kwargs['batch']}")

    model = YOLO(model_name)
    results = model.train(**train_kwargs)

    # Ultralytics stores best weights under save_dir / weights / best.pt
    save_dir = Path(results.save_dir) if hasattr(results, "save_dir") else (
        Path(train_kwargs["project"]) / train_kwargs["name"]
    )
    best = save_dir / "weights" / "best.pt"
    last = save_dir / "weights" / "last.pt"
    weights = best if best.exists() else last
    print(f"Training complete. Weights: {weights}")
    return weights


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train YOLOv8 weapon detector")
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "configs" / "train_100.yaml",
        help="Training YAML (train_50.yaml or train_100.yaml)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        choices=[50, 100],
        default=None,
        help="Shorthand: pick configs/train_{N}.yaml",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override base model (default yolov8n.pt; optional yolov8s.pt)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Ultralytics device (0, cpu, ...)",
    )
    args = parser.parse_args(argv)

    config = args.config
    if args.epochs is not None:
        config = PROJECT_ROOT / "configs" / f"train_{args.epochs}.yaml"

    train(config, model_override=args.model, device_override=args.device)


if __name__ == "__main__":
    main()
