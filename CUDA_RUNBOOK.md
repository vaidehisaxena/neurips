# CUDA runbook (NVIDIA RTX A4000)

Run these commands from a Linux shell on the CUDA machine. The scripts are
resumable: rerunning `run_al.py` skips every complete trajectory already in the
corresponding result CSVs.

## 1. Clone and create the environment

```bash
git clone https://github.com/vaidehisaxena/neurips.git
cd neurips
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install the stable CUDA 12.6 build matching the locally validated Torch version,
then the study dependencies:

```bash
python -m pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cu126
python -m pip install -r requirements.in
python -m pip freeze --all > requirements.cuda.lock.txt
```

If the installed NVIDIA driver cannot support CUDA 12.6, stop and use the
official PyTorch selector rather than installing a CPU build or changing Torch
silently: https://pytorch.org/get-started/locally/

## 2. Verify CUDA before downloading data

```bash
nvidia-smi
python - <<'PY'
import torch
assert torch.cuda.is_available(), "PyTorch cannot see CUDA"
print("torch:", torch.__version__)
print("CUDA runtime:", torch.version.cuda)
print("GPU:", torch.cuda.get_device_name(0))
print("VRAM GiB:", torch.cuda.get_device_properties(0).total_memory / 2**30)
PY
```

The GPU line must identify the RTX A4000. Do not continue if the assertion fails.

## 3. Recreate and verify scientific inputs

```bash
python prepare_data.py --config config.yaml
python fetch_checkpoint.py
python -m pytest -q
```

Confirm the five rows in `data/processed/dataset_stats.csv` match the committed
reference file. `fetch_checkpoint.py` refuses a checkpoint whose SHA-256 differs
from the preregistered synthetic-only checkpoint.

## 4. Run and validate the complete smoke matrix

```bash
python run_al.py --config config.yaml --smoke --seeds 0
python analyze_results.py --config config.yaml --smoke --validate-only
```

Expected validation: 45 trajectories, three budgets per trajectory. Also inspect
`results/manifest.json` and confirm `cuda_available` is `true`, the GPU name is
correct, and the checkpoint hash is populated.

## 5. Run the full benchmark

```bash
python run_al.py --config config.yaml
```

Safe resume after interruption uses the identical command. Do not edit
`config.yaml` between attempts: its hash is recorded in the manifest.

For a durable unattended run, use the machine's normal job scheduler or `tmux`:

```bash
tmux new -s neurips-al
source .venv/bin/activate
python run_al.py --config config.yaml
```

Detach with `Ctrl-b d`; reattach with `tmux attach -t neurips-al`.

## 6. Validate, analyze, and archive

```bash
python analyze_results.py --config config.yaml --validate-only
python analyze_results.py --config config.yaml
tar -czf neurips-results.tar.gz results data/processed requirements.cuda.lock.txt config.yaml
sha256sum neurips-results.tar.gz
```

Full validation must report 450 trajectories and 15 budgets per trajectory
before analysis outputs are used. Copy the archive and its printed SHA-256 back
to the analysis machine. Do not commit datasets, model weights, or result files
to GitHub.

## Expected generated artifacts

```text
data/processed/{dataset}.npz
data/processed/{dataset}.json
results/metrics.csv
results/queries.csv
results/manifest.json
results/validation.json
results/figures/*.pdf
results/figures/*.png
results/tables/*.csv
results/tables/*.tex
```

