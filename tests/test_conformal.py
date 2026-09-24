"""Mondrian conformal prediction, and the guard that refuses to overclaim.

ADR-009. The HTR corpus holds roughly 20 negatives, so a 40% calibration fold contains
about 8. Class-conditional coverage is then quantised in steps of 1/9, and no claim
tighter than ~89% coverage for the negative class carries information.

`min_achievable_alpha` raises rather than warns, because a warning would be filtered or
lost in a log and the report would go on to state a guarantee it cannot support.
"""

from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")

from veridian.ml.conformal import (  # noqa: E402
    MondrianConformalClassifier,
    UnderpoweredCalibrationError,
    check_power,
    min_achievable_alpha,
)


def test_min_achievable_alpha_is_bounded_by_the_smallest_class():
    assert min_achievable_alpha({0: 99, 1: 9}) == pytest.approx(0.1)


def test_min_achievable_alpha_with_a_tiny_negative_class():
    """The realistic HTR case: ~8 negatives in calibration."""
    floor = min_achievable_alpha({0: 120, 1: 8})
    assert floor == pytest.approx(1 / 9)
    assert 1 - floor < 0.9          # cannot honestly claim 90% coverage


def test_empty_class_raises():
    with pytest.raises(ValueError, match="cannot calibrate"):
        min_achievable_alpha({0: 50, 1: 0})


def test_check_power_rejects_an_unachievable_alpha():
    with pytest.raises(UnderpoweredCalibrationError) as excinfo:
        check_power({0: 120, 1: 8}, alpha=0.05)
    message = str(excinfo.value)
    assert "not achievable" in message
    assert "ADR-009" in message      # the error tells you where to read why


def test_check_power_accepts_an_achievable_alpha():
    check_power({0: 120, 1: 40}, alpha=0.10)


def _toy_data(n: int = 400, seed: int = 0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 4))
    y = (X[:, 0] + 0.35 * rng.normal(size=n) > 0).astype(int)
    return X, y


def test_empirical_coverage_is_near_target():
    sklearn = pytest.importorskip("sklearn")
    from sklearn.linear_model import LogisticRegression

    del sklearn
    X, y = _toy_data()
    model = MondrianConformalClassifier(LogisticRegression(max_iter=500), alpha=0.10)
    model.fit(X[:300], y[:300], seed=0)
    report = model.score_report(X[300:], y[300:])

    for cls, coverage in report.per_class_coverage.items():
        assert coverage >= 0.75, f"class {cls} coverage {coverage:.2f} far below target"


def test_prediction_sets_are_subsets_of_the_label_set():
    pytest.importorskip("sklearn")
    from sklearn.linear_model import LogisticRegression

    X, y = _toy_data()
    model = MondrianConformalClassifier(LogisticRegression(max_iter=500), alpha=0.10)
    model.fit(X[:300], y[:300], seed=0)
    for prediction_set in model.predict_set(X[300:]):
        assert prediction_set <= {0, 1}


def test_underpowered_fit_raises_by_default():
    """The behaviour that matters: a tiny negative class blocks a tight alpha."""
    pytest.importorskip("sklearn")
    from sklearn.linear_model import LogisticRegression

    rng = np.random.default_rng(0)
    X = rng.normal(size=(60, 4))
    y = np.zeros(60, dtype=int)
    y[:6] = 1                       # 6 positives; a 40% fold leaves ~2 for calibration

    model = MondrianConformalClassifier(LogisticRegression(max_iter=500), alpha=0.05)
    with pytest.raises(UnderpoweredCalibrationError):
        model.fit(X, y, seed=0)


def test_report_surfaces_uninformative_sets():
    """|set| = 2 means the model said nothing. That number belongs in the report."""
    pytest.importorskip("sklearn")
    from sklearn.linear_model import LogisticRegression

    X, y = _toy_data()
    model = MondrianConformalClassifier(LogisticRegression(max_iter=500), alpha=0.10)
    model.fit(X[:300], y[:300], seed=0)
    report = model.score_report(X[300:], y[300:])
    assert 0.0 <= report.uninformative_fraction <= 1.0
    assert "uninformative" in report.summary()
