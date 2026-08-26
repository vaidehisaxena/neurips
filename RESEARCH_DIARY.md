# Research diary

This diary records the study phase by phase. It distinguishes observations,
decisions, failures, and human-authorized protocol changes. Scientific results
will only be recorded after they exist in validated artifacts.

## 2026-08-26 — Stage 0: environment inspection

### Repository state

- Workspace: `/Users/vaidehisaxena/Documents/ChatGPT/vaidehi_neurips`
- The workspace was empty at inspection time.
- The workspace was not a Git repository.
- No existing source code, configuration, data, results, or `AGENTS.md` was found.

### Host and runtime

- Host: Apple Silicon (`arm64`) macOS 26.5.2.
- CUDA is unavailable on this host. Per the locked protocol, TabPFN would run on
  CPU unless the full experiment is moved to a CUDA-capable machine.
- Apple Command Line Tools are missing. Login-shell commands invoking the system
  developer toolchain fail with an `xcode-select` error.
- Codex bundled fallbacks remain available:
  - Python 3.12.13
  - bundled Git
- Observed bundled Python packages:
  - NumPy 2.3.5
  - pandas 2.2.3
  - PyTDC, RDKit, TabPFN, scikit-learn, XGBoost, Torch, SciPy, matplotlib,
    and seaborn were not installed.

### Blockers and unresolved protocol questions

- A dedicated environment and all scientific dependencies still need to be
  created and pinned.
- Real dataset access and exact TabPFN checkpoint access have not yet been
  verified.
- The external skills requested in the specification have not yet been
  installed; installation requires network access and writes outside the
  workspace.
- The specification does not fully define the deterministic resampling sequence
  for an initial size-32 set when the first uniform sample contains one class.
- The exact seeded tie-breaking rule for entropy and entropy-diversity rankings
  is not fully defined.
- “Mean within-batch Tanimoto similarity” does not state whether this is the
  mean over all unordered pairs in each acquired batch (the likely reading).
- The deterministic-repeat acceptance test mentions identical metrics, while
  runtime metrics are inherently nondeterministic; it is unclear whether
  runtimes are excluded from this equality check.

### Status

Stage 0 inspection is complete. Stage 1 has not begun. The study is incomplete.

## 2026-08-26 — Human protocol confirmations

The human collaborator explicitly confirmed all five proposed resolutions:

- Initial-set resampling uses consecutive size-32 draws from one
  `numpy.random.Generator(seed)` until both classes are present.
- Acquisition ties use a fixed seed-generated random candidate order.
- Mean within-batch Tanimoto similarity is the arithmetic mean across all
  unordered molecule pairs in each acquired batch.
- Deterministic repeat comparisons exclude runtime values while requiring
  identical query histories and predictive metrics within tolerance.
- Predictive entropy is standard binary entropy:
  `-p log(p) - (1-p) log(1-p)`.

The human supplied `https://github.com/vaidehisaxena/neurips.git` as the Git
remote. The local repository was initialized, but the first remote access
attempt failed because GitHub credentials were unavailable on this host.

## 2026-08-26 — Stage 1: dependency planning (in progress)

- Authoritative TabPFN documentation identifies
  `tabpfn-v2.5-classifier-v2.5_default-2.ckpt` as the best synthetic-only
  TabPFN 2.5 classification checkpoint.
- The package default checkpoint is real-data-finetuned, so the implementation
  will always pass the exact configured synthetic-only checkpoint path.
- Initial direct dependency pins were recorded in `requirements.in`. A complete
  resolved lock file will be generated from the dedicated environment.
- The first installation attempt failed with `ResolutionImpossible`: PyTDC
  1.1.15 requires NumPy `>=1.26.4,<2.0`, conflicting with the initially recorded
  NumPy 2.3.5. The dedicated environment pin was changed to NumPy 1.26.4, the
  newest version allowed by PyTDC. The host runtime remains unchanged.
- PyTDC's pinned `cellxgene-census==1.15.0` has no Python 3.12 distribution.
  A managed Python 3.11.16 runtime was therefore provisioned for `.venv`.
- Dependency resolution then showed that PyTDC requires RDKit
  `>=2023.9.5,<2024.3.1`; the initial RDKit 2025.9.5 pin was replaced with
  compatible RDKit 2023.9.6 rather than overriding PyTDC's declared support.
- Unit-test collection then failed because PyTDC imports `pkg_resources`, which
  is absent from setuptools 84. Setuptools was pinned to 80.9.0, which retains
  that compatibility module.

### Real-data access and observed cleaning statistics

- All five datasets downloaded successfully through PyTDC 1.1.15.
- DILI: 475 raw/final; prevalence 0.496842; pool/test 379/96.
- HIA_Hou: 578 raw/final; prevalence 0.865052; pool/test 461/117.
- Bioavailability_Ma: 640 raw/final; prevalence 0.768750; pool/test 512/128.
- Pgp_Broccatelli: 1,218 raw, 1,212 final after six identical duplicate rows;
  prevalence 0.533828; pool/test 969/243.
- BBB_Martins: 2,030 raw, 1,965 final after 45 identical duplicate rows and
  removal of 20 rows in 10 conflicting canonical-SMILES groups; prevalence
  0.763359; pool/test 1,571/394.
- No invalid molecule was observed. Pool/test scaffold disjointness and the
  both-classes assertions passed for every dataset.
- Exact detailed statistics are stored in `data/processed/dataset_stats.csv`
  and per-dataset JSON sidecars.
- The exact synthetic-only checkpoint downloaded successfully from the official
  `Prior-Labs/tabpfn_2_5` Hugging Face repository.
- Checkpoint SHA-256:
  `2d0fbd257a5a274f2a219836d5a68e9c27224845936b4685d85dd42e2b8092aa`.

## 2026-08-26 — Stages 3–6: local validation (partial)

- Five protocol unit tests passed.
- A real DILI TabPFN size-32 fit and probability prediction passed using the
  exact checkpoint; all probabilities were finite and within `[0,1]`.
- The two-round smoke matrix completed for random forest and TabPFN across all
  five datasets and all three acquisitions: 30 complete trajectories, three
  budgets each, 16 unique queries per non-final round, and finite metrics.
- Random acquisition histories were identical between RF and TabPFN for each
  dataset/seed, as required.
- Repeating a DILI RF entropy-diversity trajectory produced identical queries
  and identical non-runtime metrics.
- Aggregate local smoke timing: RF fit 7.93 s, test prediction 0.92 s, pool
  prediction 0.52 s; TabPFN fit 5.98 s, test prediction 475.59 s, pool
  prediction 515.66 s.
- XGBoost could not be imported locally because `libomp.dylib` is missing.
  It has not been substituted or skipped in the required CUDA smoke matrix.
- Stage 6 is incomplete until all 15 XGBoost smoke trajectories pass on the
  CUDA/Linux host.
- After the local smoke run, query-history output was strengthened to include
  the 32 initial labeled molecules (`round=0`, `is_initial=true`) so every
  trajectory records all 256 labeled identities. The earlier smoke CSVs and
  manifest used the acquisition-only schema and were deleted as stale. Unit
  tests and a fresh RF trajectory-history check passed after this correction;
  the CUDA smoke run must regenerate all smoke artifacts.

## 2026-08-26 — Apple Silicon smoke-test continuation

- The human requested local XGBoost and TabPFN smoke execution and supplied an
  Apple Silicon TabPFN example.
- The environment already contained `libomp.dylib` in scikit-learn and PyTorch.
  Launching Python with scikit-learn's bundled OpenMP directory in
  `DYLD_LIBRARY_PATH` resolved the macOS dynamic-library error. A toy XGBoost
  fit and probability prediction passed. An attempted in-process `ctypes`
  preload did not satisfy XGBoost's `@rpath` lookup and was removed after the
  integrated smoke run captured the exact failure. No model parameters or
  package versions changed.
- The supplied TabPFN article uses MPS but reports CPU faster on its smaller
  Apple Silicon tests. The study continues to resolve `device: auto` as CUDA
  when CUDA exists and CPU otherwise; MPS is not silently introduced.
- The corrected full two-round smoke matrix completed on the M5 Mac: five
  datasets × three models × three acquisitions × seed 0 = 45 trajectories.
  Every trajectory contains budgets 32, 48, and 64 and 64 recorded labeled
  identities (32 initial plus two batches of 16). All numeric metrics were
  finite, batches had no repeated molecule, batch sizes were exact, initial
  sets matched across every model/acquisition, and random acquisition histories
  matched across all three models.
- Repeated DILI random trajectories for TabPFN and XGBoost produced identical
  query histories and non-runtime metrics. Together with the earlier RF repeat,
  model-level deterministic smoke acceptance passed.
- Aggregate corrected smoke timings were: RF 8.45 s fit / 0.89 s test predict /
  0.53 s acquisition predict; TabPFN 6.14 s / 512.81 s / 563.89 s; XGBoost
  1.63 s / 0.02 s / 0.01 s.
- Stage 6 is complete. The full 450-trajectory Stage 7 benchmark has not begun.
