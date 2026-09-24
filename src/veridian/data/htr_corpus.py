"""Head-twitch response corpus.

There is no curated public HTR dataset -- PubMed searches this session confirmed the data
is scattered across individual papers. It must be hand-extracted, with a PMID per row.

Realistic yield: Tier A (quantitative rodent HTR only) ~80-140 compounds, of which only
~12-25 are true negatives. Roughly 85% phenethylamine or tryptamine.

See TODO_EXTRACTION.md for the target papers.
"""

from __future__ import annotations

from pathlib import Path


def load_htr_corpus(path: Path | None = None, tier: str = 'A'):
    """Load the hand-curated HTR corpus at the requested quality tier.

    INPUTS:   Optional path; tier 'A' (quantitative rodent HTR), 'B' (+ drug discrimination), 'C' (+
              self-report).
    OUTPUTS:  DataFrame with label_quality per row.
    ACCEPTS:  tests/test_htr_corpus.py -- tier C rows never appear in a tier A load; every row
               carries a PMID.
    EFFORT:   ~0.5 day for the loader. The extraction itself is days of reading.
    """

    raise NotImplementedError(
        "load_htr_corpus is not implemented; see the docstring for its contract."
    )


def chemotype_coverage(df) -> dict[str, int]:
    """Count corpus compounds per chemotype.

    INPUTS:   HTR corpus DataFrame.
    OUTPUTS:  {chemotype: count}. Expected to show near-zero coverage of the scaffolds this project
               enumerates -- which is the finding, not a bug (ADR-008).
    ACCEPTS:  tests/test_htr_corpus.py -- returns a count for every chemotype in the reference set.
    EFFORT:   ~1 h.
    """

    raise NotImplementedError(
        "chemotype_coverage is not implemented; see the docstring for its contract."
    )
