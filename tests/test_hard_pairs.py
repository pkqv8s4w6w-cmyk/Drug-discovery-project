"""The project's central difficulty, kept permanently visible.

LSD, lisuride and 2-bromo-LSD are near-identical ergolines with opposite behavioural
labels. LSD and lisuride differ by a single amide-to-urea substitution; 2-bromo-LSD is LSD
plus one bromine. Both non-hallucinogens bind 5-HT2A well.

Gate criteria G6 and G7 require the pipeline to separate them. Any method that separates
the broader reference set while failing these pairs is separating on gross chemotype, not
on the property of interest, and has learned nothing useful.

These tests are marked xfail deliberately. The pipeline is a skeleton, so they fail today.
They stay in the suite, and stay visible in every run, because the day one of them passes
is the day the project has a result -- and if they are ever quietly deleted, the project
has lost the only check that distinguishes it from an expensive similarity search.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.xfail(
    reason="pipeline is a skeleton; separation is not implemented yet (see ADR-001)",
    strict=False,
)


def test_lisuride_separates_from_lsd():
    """Gate criterion G6."""
    from veridian.eval.separation import check_hard_pairs

    verdicts = check_hard_pairs(None, None)
    ergoline = next(v for v in verdicts if v.group == "ergoline_triad")
    assert ergoline.passed, ergoline.detail


def test_2_bromo_lsd_separates_from_lsd():
    """Gate criterion G7."""
    from veridian.eval.separation import check_hard_pairs

    verdicts = check_hard_pairs(None, None)
    assert all(v.passed for v in verdicts)
