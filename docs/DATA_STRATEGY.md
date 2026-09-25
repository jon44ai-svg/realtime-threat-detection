# Dataset and model improvement path

Do this in order; do not merge data before the paper baseline is measured.

## 1. Preserve the paper baseline

- Keep the current 7,959-image dataset and its original train/valid/test split.
- Train/evaluate `yolov8n` for 50 and 100 epochs.
- Record the Table II comparison before adding outside data.

## 2. Add domain data without corrupting evaluation

Use a new training-only dataset variant. Never put merged images into the
paper test split.

Recommended candidates:

1. FiDaSS firearm surveillance frames.
2. The US real-time gun CCTV/mock-attack dataset.
3. CC BY synthetic CCTV weapon images from Simuletic.
4. A small, labeled sample of this project's actual webcam frames.

Keep a manifest with source URL, license, source split, original class, and
mapped class. Reject a source when its license is unclear.

## 3. Label mapping

Map only to the existing classes:

```text
gun / handgun / pistol / rifle -> gun
knife -> knife
bat / stick / rod / blunt object -> blunt_object
person / armed / unarmed / no_gun -> exclude from this detector
```

Do not silently map `armed` or `weapon` to `gun`; those labels do not identify
the object class precisely enough.

## 4. Preprocessing

- Convert source annotations to YOLO normalized `class x_center y_center width height`.
- Verify every box is within `[0, 1]`, has positive width/height, and points to an
  existing image.
- Deduplicate near-identical frames before splitting.
- Split by video or camera source, not random frames, to prevent leakage.
- Resize at training time with Ultralytics; do not permanently squash images to
  640×640.

## 5. Postprocessing for the webcam MVP

- Start at `conf=0.65` for the weak local demo; tune on a held-out webcam clip.
- Keep IoU NMS at the Ultralytics default first.
- Use the existing cooldown and temporal buffer; do not alert on every frame.
- Promote a detection only after it persists across multiple sampled frames.
- Log class, confidence, and `xyxy` coordinates so false positives can be
  reviewed and mined as hard negatives.

## 6. Model escalation

Keep `yolov8n` for the baseline and local CPU deployment. Try `yolov8s` only if
50/100-epoch validation mAP remains materially below the paper target or boxes
are too coarse. A stronger GPU changes training time, not the model's accuracy
unless it enables a larger model or more experiments.
