"""Molecule standardisation.

Stereochemistry is preserved throughout. (R)-69 and (S)-69 differ in activity, and the
ergoline reference compounds are all single stereoisomers -- a pipeline that strips
stereo would merge LSD with its inactive epimer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StdResult:
    smiles: str
    inchikey: str
    ok: bool
    reason: str | None = None



def standardize_smiles(smiles: str, *, keep_stereo: bool = True) -> StdResult:
    """Run the RDKit standardisation pipeline over one SMILES.

    INPUTS:   SMILES string; keep_stereo (must default True).
    OUTPUTS:  StdResult with canonical parent SMILES and InChIKey, or ok=False plus a reason.
    ACCEPTS:  tests/test_standardize.py -- salts strip to the parent, tautomers canonicalise
               consistently, and every reference-set SMILES round-trips to its committed InChIKey.
    EFFORT:   ~1 day. Cleanup -> FragmentParent -> Uncharger -> Normalizer -> TautomerEnumerator.
    """

    raise NotImplementedError(
        "standardize_smiles is not implemented; see the docstring for its contract."
    )


def standardize_frame(df, smiles_col: str, n_jobs: int = 4):
    """Standardise a DataFrame column in parallel.

    INPUTS:   DataFrame, column name, worker count.
    OUTPUTS:  DataFrame with smiles_std, inchikey, std_ok, std_reason appended.
    ACCEPTS:  tests/test_standardize.py -- failures are flagged in std_reason, never dropped.
    EFFORT:   ~0.5 day.
    """

    raise NotImplementedError(
        "standardize_frame is not implemented; see the docstring for its contract."
    )
