# Worklog

Append-only. Newest entries at the **bottom**. Timestamps are Asia/Jerusalem (+03) unless noted.

Format per entry:

```
## YYYY-MM-DD HH:MM — short title
**Status:** …
**Changed:** …
**Missing / blocked:** …
**User ask:** …
**Notes:** …
```

---

## 2026-09-25 18:07 — Project kickoff

**Status:** No repo yet. User wants workspace from paper PDF + inspiration notebook.  
**Changed:** Planning started.  
**Missing / blocked:** Scope not chosen.  
**User ask:** Create workspace reproducing paper; inspire from notebook at Downloads.  
**Notes:** Sources: `real time threat detection from video.pdf`, `Real_Time_Weapon_and_Blunt_Object_Detection_using_YOLOv8.ipynb`.

---

## 2026-09-25 18:11 — Scope locked: long-term / C

**Status:** Scope C selected (full detection now + pipeline stubs for VLM/alerts).  
**Changed:** Direction = long-term, not one-and-done.  
**Missing / blocked:** Implementation.  
**User ask:** “a longer term project, C”.  
**Notes:** Confirms user-rule preference to guess/confirm one-and-done vs long-term.

---

## 2026-09-25 18:15–18:24 — Plan implementation (scaffold)

**Status:** Plan todos executed (do not recreate todos; do not edit plan file).  
**Changed:** Project bootstrap, uv layout, data/EDA, train/eval, pipeline stubs, CLIs/docs.  
**Missing / blocked:** `uv sync` pending Trivy rule; dataset not downloaded yet.  
**User ask:** Implement plan as specified; mark todos in progress → complete.  
**Notes:** `create_project` failed on Windows (`spawn /bin/sh ENOENT`) → PowerShell `git init` workaround.

---

## 2026-09-25 18:28 — Dependency safety rule

**Status:** User rule added: resolve lock → Trivy → then install.  
**Changed:** Remembered in `~/.cursorrules`; `uv.lock` + Trivy path established.  
**Missing / blocked:** Install blocked until scan clean.  
**User ask:** `rem` before uv sync/install: lock then Trivy/verifier.  
**Notes:** Hard constraint for all future dependency work.

---

## 2026-09-25 18:35–18:42 — Lock, Trivy, uv sync

**Status:** Lock scanned (0 HIGH/CRITICAL findings reported in session); `.venv` created.  
**Changed:** `uv.lock`, `scripts/verify_deps.ps1`, sync completed.  
**Missing / blocked:** Dataset download, full train.  
**User ask:** (implicit via rem + continue workflow).  
**Notes:** Git commit of scaffold ~18:39 (`9ffa6f7`).

---

## 2026-09-25 18:49–19:02 — Continue / Kaggle creds

**Status:** Download path unblocked.  
**Changed:** Copied `kaggle (1).json` from Downloads to proper Kaggle location.  
**Missing / blocked:** Training.  
**User ask:** Copy kaggle json; empty username OK — continue pretraining if next.  
**Notes:** **Correction / disapproval of assumption:** agent concerned about empty Kaggle username; user said it still works — do not block on that.

---

## 2026-09-25 19:02–19:34 — Dataset + path fix + smoke reality

**Status:** Dataset validated (4800 / 2182 / 977). Smoke train path fixed (`data.yaml` path relative to cwd).  
**Changed:** Download + yaml fix; CPU smoke slow without CUDA.  
**Missing / blocked:** Full 50/100 epochs on local GPU impossible.  
**User ask:** Continue with pretraining.  
**Notes:** Local device = Intel iGPU / Vega 8 — Ultralytics path is effectively **CPU** for training.

---

## 2026-09-25 19:34–19:37 — GPU capability Q&A

**Status:** Clarified: Intel iGPU / Vega 8 won’t give CUDA Ultralytics acceleration.  
**Changed:** Advice only.  
**Missing / blocked:** Local full train wall-clock.  
**User ask:** “i currently have intel gpu”; “will it not accelerate at all? i have vega 8”.  
**Notes:** Led to Colab plan.

---

## 2026-09-25 19:37–20:31 — Smoke + Colab prep

**Status:** Smoke train done; repo prepared for GitHub → Colab clone.  
**Changed:** `train_smoke` + `fraction`; Colab notebook; README Colab section; data path docs.  
**Missing / blocked:** GitHub remote authorization.  
**User ask:** Smoke test, then push for Colab GPU.  
**Notes:** Commit `d076053`.

---

## 2026-09-25 20:31–20:34 — Origin + SSH

**Status:** Remote set to `jon44ai-svg/realtime-threat-detection.git`; push via deploy key.  
**Changed:** Origin, SSH key `id_ed25519_ai`, branch push.  
**Missing / blocked:** Colab package import bug still ahead.  
**User ask:** Clear to use that origin; has passkey for deploy token.  
**Notes:** Commits `39fec36` etc.

---

## 2026-09-25 20:47 — Colab ModuleNotFoundError fix

**Status:** Train/eval importable in Colab.  
**Changed:** `sys.path` bootstrap in scripts + `pip install -e .` in notebook; pushed `b36c755`.  
**Missing / blocked:** Completed 50-epoch run.  
**User ask:** Fix Colab traceback; give diff.  
**Notes:** User hit error mid-Colab setup — fulfilled with code + push.

---

## 2026-09-25 21:38–21:39 — Interrupted early Colab run

**Status:** User interrupted during early epochs of intended **50**-epoch run (not a 4-epoch config).  
**Changed:** Guidance: resume full 50; ~6MB weights normal for yolov8n.  
**Missing / blocked:** Finished training.  
**User ask:** “is this 4 epochs or 50… good before interrupt?”; “does 6mb make sense?”  
**Notes:** Early mAP low as expected; file size OK.

---

## 2026-09-25 21:50 — Live webcam on this device

**Status:** Webcam + YOLO live path implemented (CPU).  
**Changed:** Real `VideoSource`, orchestrator loop, `run_pipeline.py` CLI.  
**Missing / blocked:** Good weights.  
**User ask:** Given checkpoint, make it work with current webcam.  
**Notes:** VLM still skipped.

---

## 2026-09-25 21:52–21:58 — Hostable website (ponytail)

**Status:** Stdlib HTTP + MJPEG site on `:7860`; committed `62dc941`.  
**Changed:** `threat_detection/web/*`, `scripts/serve.py`.  
**Missing / blocked:** Quality still depends on checkpoint.  
**User ask:** `/ponytail` + package as full hostable website.  
**Notes:** No Gradio/React/Docker (ponytail).

---

## 2026-09-25 21:59 — Epoch-2 live quality complaint

**Status:** Diagnosed from `terminals/31.txt`: mostly CRITICAL (= gun FPs); brief HIGH (= knife); bad boxes.  
**Changed:** Explanation only — undertrained weights, not webcam bug.  
**Missing / blocked:** 50/100 `best.pt`.  
**User ask:** Read logs; knife only after ~1 min; threats before/after; bad boxes; was 2nd-epoch ckpt.  
**Notes:** **User dissatisfaction with demo quality** attributed to epoch-2 model, not pipeline.

---

## 2026-09-25 22:05 — Logs, Drive sync, canvas, domain/GPU thoughts

**Status:** Persistent rotating log + search; Colab Drive `sync_artifacts`; status canvas updated.  
**Changed:** `logging_config.py`, `/logs?q=`, `search_logs.py`, notebook Drive cells; canvas decisions on one log stream, free datasets, T4 vs stronger GPU.  
**Missing / blocked:** Still waiting on Colab finish.  
**User ask:** Verbose persistent logs + search; think log types; dataset similarity (free); GPU upgrade; Colab auto-download cell; update status canvas.  
**Notes:** Decision: **one** log file, many logger names. Commit later as `364dd7a`.

---

## 2026-09-25 22:08–22:11 — Mid-train check (~20/50)

**Status:** On track. mAP50 ~0.47–0.52 by ~epoch 17–19; losses falling; T4 healthy. Target mAP50@50 ≈ 0.777.  
**Changed:** Advice: finish 50 → sync → 100.  
**Missing / blocked:** Remaining ~30 epochs (~45–50 min).  
**User ask:** “am i on track to getting a good result?” + training log paste.  
**Notes:** Commit push of logging/Drive work `364dd7a` at 22:11.

---

## 2026-09-25 22:12 — Nano / T4 / RunPod Q&A

**Status:** Guidance: keep yolov8n; T4 enough; RunPod ≈ CLI not drop-in Colab notebook.  
**Changed:** Advice only.  
**Missing / blocked:** Same — finish train.  
**User ask:** Nano too small/big? Better GPU than T4? RunPod as simple as Colab notebook?  
**Notes:** Don’t pay for RunPod until T4 is the bottleneck.

---

## 2026-09-25 22:16 — Persistent memory files created

**Status:** This memory pack added under `docs/memory/` + `.cursor/rules/project-memory.mdc`.  
**Changed:** STATUS, WORKLOG, REQUESTS, BOTTLENECKS, always-apply rule.  
**Missing / blocked:** Unchanged (Colab 50 still in flight).  
**User ask:** Write persistent memory files with worklog, status timestamps, missing, bottlenecks, requests/fulfillment, disapprovals.  
**Notes:** Agents should append WORKLOG and refresh STATUS after meaningful updates.

---

## 2026-09-25 22:26 — MVP hardening and research shortlist

**Status:** Minimum local MVP is operational with a checkpoint; runtime gaps hardened.  
**Changed:** Web capture now uses confidence/cooldown gating and temporal buffering; custom log directories reach `/logs`; capture-thread failures update status and persist tracebacks. Added `docs/DATA_STRATEGY.md`.  
**Missing / blocked:** No trained checkpoint is committed; Colab 50/100 completion remains the quality bottleneck. VLM and external alerts remain intentionally stubbed.  
**User ask:** Implement missing MVP pieces with subtasks/subagents, use codegraph, propose dataset/model improvements, search related projects/papers, and ask before adding them to persistent research.  
**Notes:** Used two subagents for MVP audit and research. No codegraph tool exists in the exposed catalog. Research candidates are not archived yet pending user choice. Search findings include FiDaSS, US CCTV/mock-attack, Simuletic CCTV, Mendeley firearm-action data, RWF-2000, UCF-Crime, XD-Violence, ViDD, hard-negative mining, and SF-YOLO.

---

## 2026-09-25 22:28 — Research folder approved

**Status:** User selected detection, temporal, and method candidates for persistent research notes.  
**Changed:** Added `docs/research/README.md` with links, license caveats, use cases, and experiment order; no raw datasets downloaded.  
**Missing / blocked:** Dataset acquisition still requires per-source license review and should happen after the paper baseline.  
**User ask:** Include the researched related projects/papers in the persistent research folder.  
**Notes:** Selected: FiDaSS, US CCTV/mock-attack, Simuletic, YouTube-GDD, Mendeley firearm-action, RWF-2000, UCF-Crime, XD-Violence, ViDD, hard-negative mining, and SF-YOLO.

---

## 2026-09-25 22:53 — Colab 50-epoch baseline completed

**Status:** 50 epochs completed successfully on Tesla T4 in 1.212 hours.  
**Changed:** `best.pt` and `last.pt` produced; evaluation completed. Overall precision 0.7434, recall 0.6720, mAP50 0.7359, mAP50-95 0.4861. Per-class mAP50: blunt 0.6015, gun 0.8769, knife 0.7292.  
**Missing / blocked:** Drive persistence cell is waiting at `drive.mount()` or its authorization prompt. 100-epoch run has not started.  
**User ask:** Reported completed training output and asked whether the Drive cell hanging over one minute is normal.  
**Notes:** Recall is essentially at the paper 50-epoch target; mAP50 is 0.041 below target. This is a good baseline, not a failure.

---

## 2026-09-25 22:59 — 50-epoch backup secured

**Status:** User has the `train50_backup` archive in local Downloads.  
**Changed:** 50-epoch checkpoint/results are no longer dependent on the current Colab runtime.  
**Missing / blocked:** Google Drive credential propagation still fails; 100-epoch persistence method remains to be secured.  
**User ask:** Confirmed the train-50 backup was downloaded.  
**Notes:** Do not restart the Colab runtime until 100-epoch work is either backed up or a persistence path succeeds.

---

## 2026-09-25 23:02 — Train-50 checkpoint extracted locally

**Status:** Backup extracted without replacing existing files.  
**Changed:** New ignored path: `runs/colab_train50_backup/detect/train_50/weights/best.pt`; Ultralytics loaded it successfully with classes `blunt_object`, `gun`, `knife`.  
**Missing / blocked:** 100-epoch checkpoint and Drive authorization.  
**User ask:** Unzip the Downloads backup and use it without replacing existing files.  
**Notes:** Use this checkpoint for the local webcam/web test.
