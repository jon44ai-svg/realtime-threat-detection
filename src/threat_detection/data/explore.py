"""Notebook-style dataset exploration: tree, split counts, annotation samples."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET = (
    PROJECT_ROOT / "data" / "raw" / "custum-dataset-and-public-data-for-model-training"
)
DEFAULT_OUT = PROJECT_ROOT / "runs" / "eda"


def print_dir_tree(startpath: Path) -> None:
    """Print a lightweight directory tree with image counts (notebook-inspired)."""
    startpath = Path(startpath)
    print(f"Directory tree for: {startpath}\n")
    for root, _dirs, files in os_walk_sorted(startpath):
        level = len(Path(root).relative_to(startpath).parts)
        indent = "    " * level
        image_files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))]
        other = len(files) - len(image_files)
        name = Path(root).name if Path(root) != startpath else "[Root]"
        print(f"{indent}{name}/ (images: {len(image_files)}, other: {other})")


def os_walk_sorted(startpath: Path):
    for root, dirs, files in __import__("os").walk(startpath):
        dirs.sort()
        files.sort()
        yield root, dirs, files


def count_split_images(dataset_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for split in ("train", "valid", "test"):
        img_dir = dataset_dir / split / "images"
        if img_dir.is_dir():
            counts[split] = sum(
                1 for f in img_dir.iterdir() if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}
            )
        else:
            counts[split] = 0
    return counts


def plot_split_counts(counts: dict[str, int], out_path: Path | None = None) -> Path | None:
    splits = list(counts.keys())
    values = [counts[s] for s in splits]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(splits, values, color=["#2a9d8f", "#e9c46a", "#e76f51"])
    ax.set_title("Image count per split")
    ax.set_xlabel("Split")
    ax.set_ylabel("Count")
    for i, v in enumerate(values):
        ax.text(i, v + max(values) * 0.01, str(v), ha="center")
    fig.tight_layout()
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150)
        print(f"Saved {out_path}")
    plt.close(fig)
    return out_path


def load_class_names(dataset_dir: Path) -> list[str]:
    yaml_path = dataset_dir / "data.yaml"
    if not yaml_path.exists():
        # Fall back to project config
        yaml_path = PROJECT_ROOT / "configs" / "data.yaml"
    with open(yaml_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    names = cfg.get("names", [])
    if isinstance(names, dict):
        return [names[i] for i in sorted(names.keys())]
    return list(names)


def parse_yolo_boxes(label_path: Path) -> list[tuple[int, float, float, float, float]]:
    """Parse YOLO txt labels into (cls_id, xc, yc, w, h) normalized tuples."""
    boxes: list[tuple[int, float, float, float, float]] = []
    if not label_path.exists():
        return boxes
    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        cls_id = int(parts[0])
        xc, yc, bw, bh = map(float, parts[1:])
        boxes.append((cls_id, xc, yc, bw, bh))
    return boxes


def yolo_to_xyxy(
    xc: float, yc: float, bw: float, bh: float, img_w: int, img_h: int
) -> tuple[int, int, int, int]:
    x1 = int((xc - bw / 2) * img_w)
    y1 = int((yc - bh / 2) * img_h)
    x2 = int((xc + bw / 2) * img_w)
    y2 = int((yc + bh / 2) * img_h)
    return x1, y1, x2, y2


def draw_annotations(
    img_path: Path, label_path: Path, class_names: list[str]
) -> tuple[np.ndarray, list[str]]:
    img = cv2.imread(str(img_path))
    if img is None:
        raise FileNotFoundError(f"Could not read image: {img_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, _ = img.shape
    detected: list[str] = []

    for cls_id, xc, yc, bw, bh in parse_yolo_boxes(label_path):
        x1, y1, x2, y2 = yolo_to_xyxy(xc, yc, bw, bh, w, h)
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        name = class_names[cls_id] if cls_id < len(class_names) else f"Class {cls_id}"
        detected.append(name)
        (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x1, y1 - th - 10), (x1 + tw, y1), (255, 0, 0), -1)
        cv2.putText(img, name, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return img, list(dict.fromkeys(detected))


def find_class_examples(
    dataset_dir: Path, class_names: list[str], split: str = "train"
) -> dict[str, tuple[Path, Path] | None]:
    examples: dict[str, tuple[Path, Path] | None] = {n: None for n in class_names}
    img_dir = dataset_dir / split / "images"
    lbl_dir = dataset_dir / split / "labels"
    if not img_dir.is_dir():
        return examples

    for img_file in sorted(img_dir.iterdir()):
        if img_file.suffix.lower() not in {".png", ".jpg", ".jpeg", ".bmp"}:
            continue
        label_path = lbl_dir / f"{img_file.stem}.txt"
        for cls_id, *_ in parse_yolo_boxes(label_path):
            if cls_id < len(class_names):
                name = class_names[cls_id]
                if examples[name] is None:
                    examples[name] = (img_file, label_path)
        if all(v is not None for v in examples.values()):
            break
    return examples


def count_class_instances(dataset_dir: Path, class_names: list[str], split: str = "train") -> Counter:
    counter: Counter = Counter()
    lbl_dir = dataset_dir / split / "labels"
    if not lbl_dir.is_dir():
        return counter
    for label_path in lbl_dir.glob("*.txt"):
        for cls_id, *_ in parse_yolo_boxes(label_path):
            if cls_id < len(class_names):
                counter[class_names[cls_id]] += 1
    return counter


def save_annotation_examples(
    dataset_dir: Path, out_dir: Path, class_names: list[str] | None = None
) -> list[Path]:
    class_names = class_names or load_class_names(dataset_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for name, paths in find_class_examples(dataset_dir, class_names).items():
        if paths is None:
            print(f"No example found for class: {name}")
            continue
        img_path, label_path = paths
        annotated, _ = draw_annotations(img_path, label_path, class_names)
        out_path = out_dir / f"example_{name}.png"
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(annotated)
        ax.set_title(f"Example: {name}")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        saved.append(out_path)
        print(f"Saved {out_path}")
    return saved


def run_eda(dataset_dir: Path, out_dir: Path) -> None:
    dataset_dir = Path(dataset_dir)
    if not dataset_dir.exists():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_dir}. Run: uv run python scripts/download_data.py"
        )

    print_dir_tree(dataset_dir)
    counts = count_split_images(dataset_dir)
    print("\nSplit counts:", counts)
    plot_split_counts(counts, out_dir / "split_counts.png")

    class_names = load_class_names(dataset_dir)
    print("Classes:", class_names)
    for split in ("train", "valid", "test"):
        inst = count_class_instances(dataset_dir, class_names, split)
        print(f"  {split} instances:", dict(inst))

    save_annotation_examples(dataset_dir, out_dir / "annotations", class_names)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Explore YOLO weapon detection dataset")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    run_eda(args.dataset, args.out)


if __name__ == "__main__":
    main()
