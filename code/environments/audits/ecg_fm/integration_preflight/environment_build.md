# ECG-FM Independent Environment Build Record

- Build host: WSL2 Ubuntu.
- Task-specific Miniconda prefix: `/home/curcumin/ecg_fm_preflight/miniconda3`.
- Miniconda installer SHA256: `80bc27f13c4de90f10e387aa45e864de4f0860692c1221aef5900009a2b55302`.
- Intended task-specific environment prefix: `/home/curcumin/ecg_fm_preflight/envs/ecg_fm_env`.
- Immutable environment specification: `/mnt/d/桌面文件/ECG/upstream/ecg-fm-benchmarking/ecg_fm_env.yaml`.
- Environment specification SHA256: `7cdd9f5f6a2ad630d105d5cc7aa59ea79108fe762976b375035b9c70c8085945`.

## Blocker

`conda env create` stopped before environment resolution because current Miniconda requires explicit Terms of Service acceptance for:

- `https://repo.anaconda.com/pkgs/main`
- `https://repo.anaconda.com/pkgs/r`

No Terms of Service were accepted on the user's behalf. No channel was changed and no enforcement mechanism was bypassed. The requested environment was therefore not created, and checkpoint loading, forward, loss, backward, gradient coverage, and optimizer step were not executed.

## Continuation verification

The user reported manual acceptance, but the task-specific WSL Miniconda still reports `path: "None"` for both locked channels and `conda env create` again fails with `CondaToSNonInteractiveError`. Acceptance must be recorded in the execution context used here: WSL Ubuntu user `curcumin`, with the task-specific conda executable `/home/curcumin/ecg_fm_preflight/miniconda3/bin/conda`.

## ToS resolution and locked-YAML build result

The user subsequently accepted both Terms of Service in the exact task-specific WSL Miniconda. Verification returned `tos_accepted: true` with a concrete record path for each channel. The locked YAML SHA256 remained `7cdd9f5f6a2ad630d105d5cc7aa59ea79108fe762976b375035b9c70c8085945`.

Conda successfully solved and installed the YAML's conda package layer, but the YAML pip layer stopped at its exact requirement `fairseq-signals==1.0.0a0+571a124`: the configured pip index reports `No matching distribution found`. No dependency was upgraded, substituted, or manually installed from a source repository. This prevents construction of the exact locked environment; no checkpoint load or preflight execution occurred.

## Approved official-source remediation attempt

Classification: `NON_SCIENTIFIC_EXACT_SOURCE_DISTRIBUTION_REMEDIATION`.

Under `APPROVE_ECG_FM_EXACT_FAIRSEQ_SIGNALS_SOURCE_INSTALL_FROM_OFFICIAL_COMMIT_571A124_AS_LOCKED_YAML_EQUIVALENT`, the remaining 141 exact YAML pip pins were installed with `--no-deps`; the sole omitted YAML requirement was `fairseq-signals==1.0.0a0+571a124`.

Official source was cloned to the task-specific path `/home/curcumin/ecg_fm_preflight/fairseq-signals-571a124` with origin `https://github.com/Jwoo5/fairseq-signals.git` and detached HEAD `571a124042566adf073c7198236f8714d9529772`. Source installation used `pip install --no-deps` and stopped while compiling the package's Cython extension because no C++ compiler (`g++`, `c++`, or `clang++`) is installed in WSL. `fairseq-signals` is therefore not installed and cannot yet be imported. No compiler was installed, no dependency version was substituted, and no model execution occurred.

## Completion of approved source distribution remediation

After the user installed the approved minimal WSL toolchain, `/usr/bin/gcc`, `/usr/bin/g++`, and `/usr/bin/make` were verified. The exact official source was installed with `pip install --no-deps --no-build-isolation` using the locked environment's Cython `3.1.3` and NumPy `2.0.2`.

- Source HEAD: `571a124042566adf073c7198236f8714d9529772`
- Origin: `https://github.com/Jwoo5/fairseq-signals.git`
- `fairseq_signals.__version__`: `1.0.0a0+571a124`
- torch: `2.8.0+cu128`; CUDA available: `true`

This completes `NON_SCIENTIFIC_EXACT_SOURCE_DISTRIBUTION_REMEDIATION` without changing `ecg_fm_env.yaml` or substituting a fairseq-signals version.

## PTB-XL path-binding gate

Under `APPROVE_ECG_FM_VERIFIED_EXISTING_PTBXL_RECORDS500_PATH_BINDING_FOR_PREFLIGHT_ONLY`, only read-only path discovery was performed. No existing processed PTB-XL root or `records500` directory was located.

- Windows `D:\` recursive `records500` search: no result.
- Windows `C:\Users\86151` recursive `records500` search: no result.
- Existing project, download, document, and file roots were searched for `df_memmap.pkl` and `records500`; only `D:\桌面文件\ECG\data\processed\ptb\df_memmap.pkl` was found.
- That local dataset loads as 549 samples and is PTB, not PTB-XL(all); it was not used.
- WSL `/home`, `/mnt/d`, and `/mnt/c` recursive `records500` scan returned no candidate before the 5-minute scan limit; readable WSL root filesystem (`find / -xdev`) likewise returned none. Restricted system directories were not accessed.

No symlink, bind mount, dataset modification, preprocessing, checkpoint operation, forward, backward, or optimizer step was performed. A verified existing PTB-XL processed source path is still required.
