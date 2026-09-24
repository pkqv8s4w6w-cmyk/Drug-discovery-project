# Data provenance and schemas

## Sources

| Source | Used for | Verified |
|---|---|---|
| RCSB PDB | 16 receptor structures | all 16 confirmed present, 2026-09-24 |
| ChEMBL (EMBL-EBI) | bioactivity | counts below confirmed live |
| PubChem (NCBI) | reference compound structures | all resolved by CID |
| Enamine | building blocks | registration-gated; a sample ships in `data/external/` |

### ChEMBL record counts (2026-09-24)

| Target | ChEMBL ID | Ki | IC50 | EC50 |
|---|---|---|---|---|
| 5-HT2A | CHEMBL224 | 7,897 | 2,414 | 1,456 |
| 5-HT2B | CHEMBL1833 | 3,024 | — | 1,022 |
| 5-HT2C | CHEMBL225 | 4,671 | — | — |
| 5-HT1A | CHEMBL214 | 6,971 | — | — |

## Schemas

### `data/processed/chembl_activities.parquet` (raw)

`molecule_chembl_id, canonical_smiles, standard_inchi_key, target_chembl_id,
target_pref_name, target_organism, assay_chembl_id, assay_type, assay_description,
bao_format, bao_label, standard_type, standard_relation, standard_value, standard_units,
pchembl_value, activity_comment, data_validity_comment, potential_duplicate,
document_chembl_id, src_id, confidence_score, fetched_at, chembl_release`

### `data/processed/activities_curated.parquet`

`inchikey, smiles_std, target, endpoint, assay_mode, assay_readout, pchembl_median,
pchembl_mad, n_records, n_documents, relation_flag, emax_pct, emax_reference,
source_doc_ids, murcko_scaffold, split_group, is_reference_compound`

`assay_mode` and `assay_readout` are load-bearing, not decoration. The 2,414 IC50 and
1,456 EC50 records for 5-HT2A mix agonist and antagonist functional assays, and
Gq-versus-arrestin readout is central to the partial-agonism proxy (ADR-007). Parse
`assay_description` with a curated regex table and keep the raw text alongside.

### `data/results/docking/{receptor_id}/{tier}.parquet`

`ligand_id, inchikey, smiles_std, receptor_id, pdb_id, engine, engine_version,
scoring_function, pose_rank, affinity_kcal_mol, rmsd_lb, rmsd_ub, num_torsions, seed,
exhaustiveness, box_center_x, box_center_y, box_center_z, box_size_x, box_size_y,
box_size_z, runtime_s, salt_bridge_d332_min_dist, salt_bridge_present,
n_contacts_orthosteric, frac_buried, ifp_bits, ifp_tanimoto_to_native, contact_L5_39,
contact_W6_48, contact_F6_51, contact_F6_52, contact_S5_43, contact_Y7_43, score_z,
pose_path, run_id`

Note `score_z` alongside `affinity_kcal_mol`: cross-receptor comparison uses the z-score
only (ADR-006).

### `runs/<run_id>/candidates.csv` — the deliverable

`rank_final, candidate_id, smiles, inchikey, chemotype, scaffold_cluster_id,
scaffold_smiles, enumeration_route, bb_ids, vina_6wha, z_6wha, mean_z_nonhallu,
mean_z_hallu, delta_z, delta_z_percentile, delta_z_perm_p, delta_ifp,
sim_to_native_nonhallu, sim_to_native_hallu, partial_delta_z, salt_bridge_present,
salt_bridge_dist, pred_h2a_pki, pred_h2a_pki_lo95, pred_h2a_pki_hi95, pred_h2a_in_domain,
pred_h2a_emax, pred_h2b_pec50, pred_h2b_emax, h2b_flag, htr_pred_label, htr_pred_proba,
htr_conformal_set, htr_alpha, htr_in_domain, htr_ad_distance, mw, clogp, tpsa, hbd, hba,
rotb, pka_basic_est, qed, cns_mpo, cns_mpo_components, bbb_proxy, sa_score, n_synth_steps,
pains_alerts, brenk_alerts, nearest_chembl_neighbor, nearest_chembl_tanimoto, pose_png,
rationale, flags`

**`flags`** is a semicolon-joined list of per-compound caveats — `htr_out_of_domain`,
`delta_z_within_permutation_null`, `high_sim_to_native_ligand`, `2b_abstain` — printed in
the report. Nothing is silently dropped or silently promoted.

## Licensing

Code is MIT. RCSB data is public domain (CC0). ChEMBL is CC BY-SA 3.0 and requires
attribution. PubChem is public domain. Enamine catalogue data is subject to their terms and
is **not** redistributed in this repository.
