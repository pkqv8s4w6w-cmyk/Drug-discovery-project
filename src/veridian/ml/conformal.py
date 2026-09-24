"""Mondrian (class-conditional) inductive conformal prediction.

ADR-009. This module exists to make the project's central weakness impossible to ignore.

With an HTR corpus holding roughly 20 negatives in total, a 40% calibration fold contains
about 8. Achievable class-conditional coverage is then quantised in steps of 1/(8+1), so no
coverage claim tighter than ~89% for the negative class carries information. Rather than
print a confident-looking number with a footnote, `min_achievable_alpha` raises.

Why class-conditional rather than marginal: with a heavily imbalanced corpus, marginal
coverage is satisfied almost entirely by the majority class. A model could abstain on every
negative and still report 90% marginal coverage. Mondrian coverage makes that visible.

Why hand-rolled rather than MAPIE: MAPIE's API changed between 0.8.x and 1.x, and a pinned
dependency is fragile for a repository meant to be re-run in a year. MAPIE is retained as a
cross-check in `tests/test_conformal.py`. The algorithm below is short enough to audit.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np


class UnderpoweredCalibrationError(ValueError):
    """Raised when the calibration set is too small to support the requested alpha.

    Deliberately an error and not a warning. A warning would be filtered, ignored, or lost
    in a log, and the resulting report would state a coverage guarantee it cannot support.
    """


class _Estimator(Protocol):
    def fit(self, X: Any, y: Any) -> Any: ...
    def predict_proba(self, X: Any) -> np.ndarray: ...


@dataclass
class CoverageReport:
    """Empirical coverage, measured rather than assumed."""

    alpha: float
    per_class_coverage: dict[int, float]
    per_class_n_cal: dict[int, int]
    mean_set_size: float
    uninformative_fraction: float
    empty_fraction: float

    def summary(self) -> str:
        lines = [f"target coverage {1 - self.alpha:.0%}"]
        for cls, cov in sorted(self.per_class_coverage.items()):
            n_cal = self.per_class_n_cal.get(cls, 0)
            lines.append(f"  class {cls}: {cov:.1%} empirical (n_cal={n_cal})")
        lines.append(f"  mean set size {self.mean_set_size:.2f}")
        lines.append(f"  uninformative (|set|=2) {self.uninformative_fraction:.1%}")
        lines.append(f"  empty (|set|=0) {self.empty_fraction:.1%}")
        return "\n".join(lines)


def min_achievable_alpha(n_cal_per_class: dict[int, int]) -> float:
    """Smallest alpha any class-conditional guarantee can actually support.

    A conformal quantile over `n` calibration points can only take `n + 1` distinct levels,
    so the finest achievable miscoverage is `1 / (n + 1)`. With class-conditional coverage
    the binding constraint is the smallest class.

    Args:
        n_cal_per_class: calibration count per class label.

    Returns:
        The minimum supportable alpha.

    Raises:
        ValueError: if any class has no calibration points at all.
    """
    if not n_cal_per_class:
        raise ValueError("no calibration counts supplied")
    for cls, n in n_cal_per_class.items():
        if n < 1:
            raise ValueError(f"class {cls} has {n} calibration points; cannot calibrate")
    return max(1.0 / (n + 1) for n in n_cal_per_class.values())


def check_power(n_cal_per_class: dict[int, int], alpha: float) -> None:
    """Raise unless `alpha` is achievable given the calibration counts.

    Raises:
        UnderpoweredCalibrationError: when alpha is finer than the data can support.
    """
    floor = min_achievable_alpha(n_cal_per_class)
    if alpha < floor:
        smallest = min(n_cal_per_class.items(), key=lambda kv: kv[1])
        raise UnderpoweredCalibrationError(
            f"alpha={alpha:.3f} is not achievable: class {smallest[0]} has only "
            f"{smallest[1]} calibration points, so the finest supportable alpha is "
            f"{floor:.3f} (coverage {1 - floor:.1%}). Either loosen alpha, enlarge the "
            f"calibration fold, or report that the corpus cannot support this claim. "
            f"See ADR-009 and PREREGISTRATION.md section 2."
        )


def _quantile_level(n: int, alpha: float) -> int:
    """Index of the conformal quantile: ceil((n + 1)(1 - alpha)), clipped to [1, n]."""
    k = math.ceil((n + 1) * (1.0 - alpha))
    return max(1, min(n, k))


@dataclass
class MondrianConformalClassifier:
    """Inductive conformal classifier with class-conditional calibration.

    Nonconformity score: `s(x, y) = 1 - p_hat_y(x)`. For each class `c`, the threshold
    `q_c` is the k-th smallest calibration score among class-`c` points. The prediction set
    is `{c : 1 - p_hat_c(x) <= q_c}`, which may be empty, a singleton, or the full label
    set. An empty set means "this point resembles no class in the calibration data" and is
    a meaningful output, not a bug.
    """

    base: _Estimator
    alpha: float = 0.10
    raise_if_underpowered: bool = True
    classes_: np.ndarray | None = field(default=None, init=False)
    thresholds_: dict[int, float] = field(default_factory=dict, init=False)
    n_cal_: dict[int, int] = field(default_factory=dict, init=False)

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        *,
        cal_frac: float = 0.40,
        groups: np.ndarray | None = None,
        seed: int = 0,
    ) -> MondrianConformalClassifier:
        """Fit the base estimator on a proper training split and calibrate on the rest.

        Args:
            X: feature matrix.
            y: integer class labels.
            cal_frac: fraction held out for calibration.
            groups: optional scaffold ids. When given, the split is group-aware so that no
                scaffold spans both folds -- otherwise calibration leaks and the coverage
                guarantee is decorative.
            seed: RNG seed.

        Raises:
            UnderpoweredCalibrationError: when `raise_if_underpowered` and alpha is
                finer than the calibration counts can support.
        """
        X = np.asarray(X)
        y = np.asarray(y)
        rng = np.random.default_rng(seed)

        cal_mask = self._split(y, groups, cal_frac, rng)
        train_mask = ~cal_mask
        if not train_mask.any() or not cal_mask.any():
            raise ValueError("calibration split left one fold empty; adjust cal_frac")

        self.base.fit(X[train_mask], y[train_mask])
        self.classes_ = np.unique(y)

        y_cal = y[cal_mask]
        self.n_cal_ = {int(c): int((y_cal == c).sum()) for c in self.classes_}

        if self.raise_if_underpowered:
            check_power(self.n_cal_, self.alpha)

        proba_cal = self._proba(X[cal_mask])
        for idx, cls in enumerate(self.classes_):
            member = y_cal == cls
            if not member.any():
                self.thresholds_[int(cls)] = 1.0
                continue
            scores = 1.0 - proba_cal[member, idx]
            scores.sort()
            k = _quantile_level(len(scores), self.alpha)
            self.thresholds_[int(cls)] = float(scores[k - 1])
        return self

    def _split(
        self,
        y: np.ndarray,
        groups: np.ndarray | None,
        cal_frac: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Boolean mask selecting the calibration fold, group-aware when groups are given."""
        n = len(y)
        if groups is None:
            mask = np.zeros(n, dtype=bool)
            # Stratify so each class contributes to calibration -- Mondrian needs all of them.
            for cls in np.unique(y):
                idx = np.flatnonzero(y == cls)
                rng.shuffle(idx)
                take = max(1, round(cal_frac * len(idx)))
                mask[idx[:take]] = True
            return mask

        unique = np.unique(groups)
        rng.shuffle(unique)
        take = max(1, round(cal_frac * len(unique)))
        return np.isin(groups, unique[:take])

    def _proba(self, X: np.ndarray) -> np.ndarray:
        proba = np.asarray(self.base.predict_proba(X), dtype=float)
        if proba.ndim != 2:
            raise ValueError(f"predict_proba must return a 2-D array, got shape {proba.shape}")
        return proba

    def predict_set(self, X: np.ndarray) -> list[frozenset[int]]:
        """Conformal prediction sets, one per row of `X`."""
        if self.classes_ is None:
            raise RuntimeError("fit() must be called before predict_set()")
        proba = self._proba(np.asarray(X))
        out: list[frozenset[int]] = []
        for row in proba:
            members = {
                int(cls)
                for idx, cls in enumerate(self.classes_)
                if (1.0 - row[idx]) <= self.thresholds_[int(cls)]
            }
            out.append(frozenset(members))
        return out

    def score_report(self, X: np.ndarray, y: np.ndarray) -> CoverageReport:
        """Measure empirical class-conditional coverage on held-out data."""
        y = np.asarray(y)
        sets = self.predict_set(X)
        sizes = np.array([len(s) for s in sets])
        n_classes = len(self.classes_) if self.classes_ is not None else 0

        coverage: dict[int, float] = {}
        for cls in np.unique(y):
            member = np.flatnonzero(y == cls)
            hits = sum(1 for i in member if int(cls) in sets[i])
            coverage[int(cls)] = hits / len(member) if len(member) else float("nan")

        return CoverageReport(
            alpha=self.alpha,
            per_class_coverage=coverage,
            per_class_n_cal=dict(self.n_cal_),
            mean_set_size=float(sizes.mean()) if len(sizes) else float("nan"),
            uninformative_fraction=float((sizes == n_classes).mean()) if len(sizes) else 0.0,
            empty_fraction=float((sizes == 0).mean()) if len(sizes) else 0.0,
        )
