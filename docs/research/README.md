# Threat-detection research index

This folder stores citations, links, and decision notes only. Raw datasets stay
outside git and must be downloaded from their official source after checking
the current terms.

## Detection and CCTV datasets

### FiDaSS — Firearm Dataset for Smart Surveillance

- Paper: <https://doi.org/10.5220/0013177800003912>
- Repository/tools: <https://github.com/FiDaSS/FiDaSS_dataset>
- Why: real-world firearm-threat frames with VOC/YOLO annotations; closest
  match to the CCTV deployment problem.
- Caveat: verify dataset terms separately from the paper's CC BY-NC-ND terms.
- Priority: high.

### US Real-time gun detection in CCTV — mock attack / Unity synthetic

- Repository: <https://github.com/Deepknowledge-US/US-Real-time-gun-detection-in-CCTV-An-open-problem-dataset>
- Dataset: <https://huggingface.co/datasets/jsalazar/US-Real-time-gun-detection-in-CCTV-An-open-problem-dataset>
- Why: CCTV views plus synthetic data; useful for small/occluded gun boxes.
- Caveat: research use is free under CC BY-NC 4.0; contact authors for
  commercial use.
- Priority: high.

### Simuletic CCTV weapon dataset

- Repository: <https://github.com/Simuletic/cctv-weapon-dataset>
- Why: synthetic CCTV images with YOLO annotations for person/weapon.
- Caveat: CC BY 4.0; map the generic `weapon` label conservatively rather than
  silently calling every weapon a gun or knife.
- Priority: medium; useful for augmentation, not sole evaluation.

### YouTube-GDD

- Repository: <https://github.com/ucas-gyx/youtube-gdd>
- Paper: <https://arxiv.org/abs/2203.04129>
- Why: contextual gun/person frames and hard negatives.
- Caveat: source videos are from YouTube and the repository does not clearly
  state a permissive dataset license. Archive metadata first.
- Priority: conditional.

### Mendeley firearm-action dataset

- Dataset: <https://data.mendeley.com/datasets/bbzpxhd22j/2>
- Paper: <https://pmc.ncbi.nlm.nih.gov/articles/PMC10827673/>
- Why: video-derived firearm action frames with JSON boxes.
- Caveat: CC BY-NC 3.0; commercial use requires prior permission.
- Priority: conditional.

## Temporal threat and violence sources

### RWF-2000

- Repository: <https://github.com/mchengny/RWF2000-Video-Database-for-Violence-Detection>
- Paper: <https://arxiv.org/abs/1911.05913>
- Why: surveillance-style fighting/non-fighting clips for a later temporal
  screening stage.
- Caveat: repository restrictions and mirror licensing differ; reconcile terms
  before use.

### UCF-Crime

- Project: <https://www.crcv.ucf.edu/projects/real-world/>
- Paper: <https://arxiv.org/abs/1801.04264>
- Why: long surveillance videos for weakly supervised anomaly detection.
- Caveat: original-video licensing is not clearly stated; retain links and
  instructions rather than redistributing clips.

### XD-Violence

- Project: <https://roc-ng.github.io/XD-Violence/>
- Code: <https://github.com/Roc-Ng/XDVioDet>
- Why: large audiovisual temporal-anomaly benchmark.
- Caveat: official data terms are unclear; do not infer rights from mirrors.

### AI4RISK ViDD

- Dataset: <https://doi.org/10.5281/zenodo.18770490>
- Why: short clips across shooting, throwing, punching, running/pushing, and
  nonviolence from multiple camera perspectives.
- Caveat: verify the current Zenodo license and participant restrictions.

## Methods

### Unsupervised hard-negative mining from videos

- Paper: <https://openaccess.thecvf.com/content_ECCV_2018/papers/SouYoung_Jin_Unsupervised_Hard-Negative_Mining_ECCV_2018_paper.pdf>
- Code: <https://github.com/adiprasad/unsup-hard-negative-mining-mscoco>
- Application: mine temporally isolated false gun/knife detections from
  unlabeled webcam/CCTV video and add them as negatives.
- Caveat: adapt the idea to Ultralytics; do not import the old detector stack.

### SF-YOLO source-free domain adaptation

- Paper: <https://arxiv.org/abs/2409.16538>
- Code: <https://github.com/vs-cv/sf-yolo>
- Application: teacher/student adaptation to webcam lighting, angle, and
  compression without target labels.
- Caveat: YOLOv5-oriented and experimental for this YOLOv8 project.

## Recommended experiment order

1. Finish and record the original 50/100-epoch baseline.
2. Add FiDaSS and US CCTV data to **training only**, with source/video-level
   splits and an explicit class-mapping manifest.
3. Add a small labeled webcam set and measure false positives separately.
4. Mine hard negatives from unlabeled webcam footage.
5. Build temporal screening from RWF-2000/ViDD/UCF-Crime only after spatial
   detection is stable.
