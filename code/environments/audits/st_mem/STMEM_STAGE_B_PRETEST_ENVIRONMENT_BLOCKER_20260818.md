# ST-MEM Stage B pre-test environment blocker

- Locked commit: `238409835ef55358a10bbc3459dfa9aaa91ad5e5`
- Stage A post-patch source SHA256: `e87171a8d254251bc13b3a79b2b2dc1ee68b5551dcba41b777285ed41ea640be`
- Formal interpreter from the preserved command: `/root/miniconda3/bin/python`
- Interpreter version: Python 3.12.3

The formal test was not started. Before test launch, importing `code/main_lite.py` with the preserved interpreter failed at `code/clinical_ts/models/s42.py` because `opt_einsum` is absent: `ModuleNotFoundError: No module named 'opt_einsum'`.

The frozen best checkpoint path, size, and SHA256 match the approved identity. The canonical data manifest SHA256 also matches its preserved value. This is an execution-environment dependency blocker, not a source, checkpoint, dataset, preprocessing, or scientific discrepancy. No dependency was installed and no environment was changed.
