# Molecular active-learning benchmark

Reproducible implementation of **Does TabPFN Improve Molecular Active Learning
in the Small-Data Regime?** The protocol is locked in `config.yaml`; scientific
decisions and failures are recorded in `RESEARCH_DIARY.md`.

For the RTX A4000 machine, follow [CUDA_RUNBOOK.md](CUDA_RUNBOOK.md) exactly.

## Environment

Use Python 3.11. On the CUDA host, install the correct CUDA-enabled PyTorch build
first, then install the pinned direct requirements and capture the full lock:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
# Install the CUDA build selected at https://pytorch.org/get-started/locally/
python -m pip install -r requirements.in
python -m pip freeze --all > requirements.lock.txt
```

The experiment refuses to run TabPFN unless this exact file exists:

```text
models/tabpfn-v2.5-classifier-v2.5_default-2.ckpt
```

Download it from the official repository and verify the preregistered hash:

```bash
python fetch_checkpoint.py
```

Record and compare its SHA-256 through `results/manifest.json` before moving
results between machines.

## Staged execution

```bash
python prepare_data.py --config config.yaml
pytest -q
python run_al.py --config config.yaml --smoke
python run_al.py --config config.yaml
python analyze_results.py --config config.yaml
```

On Apple Silicon without Homebrew `libomp`, use the OpenMP runtime already
shipped in the pinned scikit-learn wheel:

```bash
DYLD_LIBRARY_PATH=.venv/lib/python3.11/site-packages/sklearn/.dylibs \
  python run_al.py --config config.yaml --smoke
```

`run_al.py` appends only completed trajectories and skips already complete
dataset/seed/model/acquisition combinations, so interrupted runs resume safely.
Do not copy partially written result files while a process is running.

## CUDA transfer

Either rerun `prepare_data.py` and `fetch_checkpoint.py` on CUDA, or securely
transfer the Git checkout plus these ignored scientific artifacts:

```text
data/processed/*.npz
data/processed/*.json
data/processed/dataset_stats.csv
models/tabpfn-v2.5-classifier-v2.5_default-2.ckpt
```

Do not commit datasets, checkpoints, or results to Git. They carry independent
provenance/licensing concerns and are intentionally ignored.
