# ECG-FM Environment Audit

## Locked benchmark environment

Source: locked `ecg_fm_env.yaml`, SHA256 `7cdd9f5f6a2ad630d105d5cc7aa59ea79108fe762976b375035b9c70c8085945`.

- Python: 3.9.23
- torch: 2.8.0
- fairseq-signals: `1.0.0a0+571a124`
- OmegaConf: 2.1.1
- Hydra Core: 1.3.2

The suffix maps to exact official source commit `571a124042566adf073c7198236f8714d9529772`; `fairseq_signals/version.txt` at that commit is `1.0.0a0`, and setup appends the seven-character commit.

## Actual local availability

- No installed environment matching `ecg_fm_env.yaml` was found.
- Base: Python 3.13.9 / torch 2.11.0; no installed fairseq-signals; torch import probe aborted on duplicate OpenMP runtime.
- Workspace CPU env: Python 3.13.5 / torch 2.7.1+cpu / OmegaConf 2.3.0 / Hydra 1.3.2; no installed fairseq-signals.
- Other Conda prefixes do not provide the locked Python 3.9 + torch 2.8 + exact fairseq-signals combination.
- `conda env list` itself failed with a CP1252 decoding error in the existing Conda metadata; no Conda files were changed.

## Read-only loader probe

Exact fairseq-signals source at `571a124...` was checked out under the provenance directory. Importing it in the existing Python 3.13.5 CPU environment failed before model construction:

`ValueError: mutable default <class 'fairseq_signals.dataclass.configs.CommonConfig'> for field common is not allowed: use default_factory`

No source patch, dependency install, dependency upgrade, environment creation, monkey patch, or compatibility workaround was attempted. Therefore official-loader CPU model construction and runtime model-attribute parameter counting are blocked by environment compatibility. Raw checkpoint structure was safely deserialized with the existing CPU torch solely for metadata/tensor inspection.

