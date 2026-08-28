"""Thin BN-state guard for PTB-XL BN-bearing frozen and linear encoders.

This runner does not instantiate a model, load a checkpoint, read data, or
alter locked source.  It patches only explicitly listed wrappers, then delegates
the received CLI arguments to the benchmark entrypoint.
"""

from __future__ import annotations

import argparse
import os
import runpy
import sys
import unittest
from pathlib import Path
from typing import Type

import torch.nn as nn


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_ROOT = Path(
    os.environ.get(
        "PTBXL_EXECUTION_ROOT",
        str(PROJECT_ROOT / "upstream" / "ecg-fm-benchmarking"),
    )
).resolve()
MAIN_LITE = UPSTREAM_ROOT / "code" / "main_lite.py"
GUARDED_EVAL_MODES = frozenset(("frozen", "linear"))


def _guarded_train(self: nn.Module, mode: bool = True) -> nn.Module:
    """Leave the active head in the requested mode; restore only encoder eval."""
    nn.Module.train(self, mode)
    if getattr(self, "eval_mode", None) in GUARDED_EVAL_MODES:
        self.model.eval()
    return self


def install_bn_guard(wrapper_class: Type[nn.Module]) -> None:
    """Install the guard on one explicitly supplied class only."""
    if getattr(wrapper_class, "_ptbxl_bn_guard_installed", False):
        return
    wrapper_class.train = _guarded_train
    wrapper_class._ptbxl_bn_guard_installed = True


def patch_runtime_wrappers() -> None:
    """Patch only wrappers proven to contain active BatchNorm modules."""
    code_root = str(UPSTREAM_ROOT / "code")
    if code_root not in sys.path:
        sys.path.insert(0, code_root)
    from clinical_ts.models.fm_ecg import ECGFounderWrapper, EcgFmKEDWrapper, MerlWrapper

    install_bn_guard(ECGFounderWrapper)
    install_bn_guard(MerlWrapper)
    install_bn_guard(EcgFmKEDWrapper)


class _MockWrapper(nn.Module):
    def __init__(self, eval_mode: str) -> None:
        super().__init__()
        self.eval_mode = eval_mode
        self.model = nn.Sequential(nn.BatchNorm1d(2))
        self.head = nn.Linear(2, 71)


class _UnpatchedWrapper(_MockWrapper):
    pass


class _BNGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        class MockMerlWrapper(_MockWrapper):
            pass

        class MockKedWrapper(_MockWrapper):
            pass

        self.merl_class = MockMerlWrapper
        self.ked_class = MockKedWrapper
        install_bn_guard(self.merl_class)
        install_bn_guard(self.ked_class)

    def _assert_guarded_mode(self, wrapper_class: Type[_MockWrapper], mode: str) -> None:
        wrapper = wrapper_class(mode)
        wrapper.train(True)
        self.assertFalse(wrapper.model[0].training)
        self.assertTrue(wrapper.head.training)

    def test_frozen_keeps_encoder_bn_eval_and_head_train(self) -> None:
        self._assert_guarded_mode(self.merl_class, "frozen")
        self._assert_guarded_mode(self.ked_class, "frozen")

    def test_linear_keeps_encoder_bn_eval_and_head_train(self) -> None:
        self._assert_guarded_mode(self.merl_class, "linear")
        self._assert_guarded_mode(self.ked_class, "linear")

    def test_finetuning_mode_is_not_changed(self) -> None:
        wrapper = self.merl_class("finetuning_linear")
        wrapper.train(True)
        self.assertTrue(wrapper.model[0].training)
        self.assertTrue(wrapper.head.training)

    def test_only_explicit_classes_are_patched(self) -> None:
        self.assertIs(self.merl_class.train, _guarded_train)
        self.assertIs(self.ked_class.train, _guarded_train)
        self.assertIsNot(_UnpatchedWrapper.train, _guarded_train)


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--self-test", action="store_true")
    args, forwarded_args = parser.parse_known_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(_BNGuardTests)
        result = unittest.TextTestRunner(verbosity=0).run(suite)
        raise SystemExit(0 if result.wasSuccessful() else 1)

    if not MAIN_LITE.is_file():
        raise FileNotFoundError(f"Locked benchmark entrypoint not found: {MAIN_LITE}")
    patch_runtime_wrappers()
    sys.argv = [str(MAIN_LITE), *forwarded_args]
    runpy.run_path(str(MAIN_LITE), run_name="__main__")


if __name__ == "__main__":
    main()
