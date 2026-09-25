"""Validate a trained YOLO model and compare metrics to paper Table II."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA = PROJECT_ROOT / "configs" / "data.yaml"

# Paper Table II targets (Mandal et al.)
PAPER_TABLE_II: dict[str, dict[str, float]] = {
    "50": {
        "precision": 0.862,
        "recall": 0.676,
        "map50": 0.777,
        "map50_95": 0.556,
        "gun_map50": 0.905,
        "knife_map50": 0.767,
        "blunt_object_map50": 0.658,
    },
    "100": {
        "precision": 0.857,
        "recall": 0.757,
        "map50": 0.819,
        "map50_95": 0.570,
        "gun_map50": 0.919,
        "knife_map50": 0.785,
        "blunt_object_map50": 0.754,
    },
}


def _names_from_data_yaml(data_yaml: Path) -> list[str]:
    with open(data_yaml, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    names = cfg.get("names", [])
    if isinstance(names, dict):
        return [names[i] for i in sorted(names.keys())]
    return list(names)


def extract_metrics(metrics: Any, class_names: list[str]) -> dict[str, float]:
    """Normalize Ultralytics metrics object into a flat dict."""
    box = getattr(metrics, "box", metrics)
    result: dict[str, float] = {
        "precision": float(getattr(box, "mp", getattr(box, "precision", 0.0))),
        "recall": float(getattr(box, "mr", getattr(box, "recall", 0.0))),
        "map50": float(getattr(box, "map50", 0.0)),
        "map50_95": float(getattr(box, "map", 0.0)),
    }

    # Per-class AP@0.5 when available
    maps = getattr(box, "maps", None)  # often mAP50-95 per class
    ap50 = getattr(box, "ap50", None)
    if ap50 is not None:
        for i, name in enumerate(class_names):
            try:
                result[f"{name}_map50"] = float(ap50[i])
            except (IndexError, TypeError, ValueError):
                pass
    elif maps is not None:
        # Fallback: store per-class mAP50-95 under map50_95 key suffix
        for i, name in enumerate(class_names):
            try:
                result[f"{name}_map50_95"] = float(maps[i])
            except (IndexError, TypeError, ValueError):
                pass

    # Ultralytics results.results_dict sometimes has cleaner keys
    results_dict = getattr(metrics, "results_dict", None)
    if isinstance(results_dict, dict):
        key_map = {
            "metrics/precision(B)": "precision",
            "metrics/recall(B)": "recall",
            "metrics/mAP50(B)": "map50",
            "metrics/mAP50-95(B)": "map50_95",
        }
        for src, dst in key_map.items():
            if src in results_dict:
                result[dst] = float(results_dict[src])

    return result


def compare_to_paper(
    measured: dict[str, float], epoch_key: str
) -> list[dict[str, Any]]:
    targets = PAPER_TABLE_II.get(epoch_key, {})
    rows: list[dict[str, Any]] = []
    for key, target in targets.items():
        got = measured.get(key)
        row: dict[str, Any] = {
            "metric": key,
            "paper": target,
            "measured": got,
            "delta": (got - target) if got is not None else None,
        }
        rows.append(row)
    return rows


def format_comparison_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        f"{'Metric':<28} {'Paper':>8} {'Measured':>10} {'Delta':>10}",
        "-" * 60,
    ]
    for row in rows:
        measured = "n/a" if row["measured"] is None else f"{row['measured']:.3f}"
        delta = "n/a" if row["delta"] is None else f"{row['delta']:+.3f}"
        lines.append(
            f"{row['metric']:<28} {row['paper']:>8.3f} {measured:>10} {delta:>10}"
        )
    return "\n".join(lines)


def evaluate(
    weights: Path,
    data_yaml: Path | None = None,
    epoch_key: str = "100",
    device: str | None = None,
    out_dir: Path | None = None,
) -> dict[str, float]:
    from ultralytics import YOLO

    data_yaml = data_yaml or DEFAULT_DATA
    if not Path(weights).exists():
        raise FileNotFoundError(f"Weights not found: {weights}")
    if not data_yaml.exists():
        raise FileNotFoundError(f"data.yaml not found: {data_yaml}")

    class_names = _names_from_data_yaml(data_yaml)
    model = YOLO(str(weights))
    val_kwargs: dict[str, Any] = {
        "data": str(data_yaml),
        "split": "val",
        "plots": True,
        "exist_ok": True,
    }
    if device is not None:
        val_kwargs["device"] = device
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        val_kwargs["project"] = str(out_dir.parent)
        val_kwargs["name"] = out_dir.name

    metrics = model.val(**val_kwargs)
    measured = extract_metrics(metrics, class_names)

    print("\nMeasured metrics:")
    for k, v in measured.items():
        print(f"  {k}: {v:.4f}")

    rows = compare_to_paper(measured, epoch_key)
    print(f"\nComparison to paper Table II ({epoch_key} epochs):")
    print(format_comparison_table(rows))
    print(
        "\nNote: Exact match is not expected (hardware, seed, Ultralytics version differ)."
    )

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "weights": str(weights),
            "epoch_key": epoch_key,
            "measured": measured,
            "paper_table_ii": PAPER_TABLE_II.get(epoch_key, {}),
            "comparison": rows,
        }
        report_path = out_dir / "metrics_vs_paper.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nWrote {report_path}")

    return measured


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate YOLO weights vs paper Table II"
    )
    parser.add_argument(
        "--weights",
        type=Path,
        required=True,
        help="Path to best.pt / last.pt",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA,
        help="YOLO data.yaml",
    )
    parser.add_argument(
        "--epochs",
        type=str,
        choices=["50", "100"],
        default="100",
        help="Which paper Table II column to compare against",
    )
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Directory for metrics JSON and Ultralytics val plots",
    )
    args = parser.parse_args(argv)

    out = args.out
    if out is None:
        out = PROJECT_ROOT / "runs" / "val" / f"compare_{args.epochs}"

    evaluate(
        weights=args.weights,
        data_yaml=args.data,
        epoch_key=args.epochs,
        device=args.device,
        out_dir=out,
    )


if __name__ == "__main__":
    main()
