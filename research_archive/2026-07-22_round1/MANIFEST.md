# Snapshot Manifest

## Manuscript and Response

- `revision_package/manuscript/conference_101719_first_submission.{tex,pdf}`: original submission baseline.
- `revision_package/manuscript/conference_101719_targeted_revision_clean.{tex,pdf}`: submission-ready clean manuscript.
- `revision_package/manuscript/conference_101719_targeted_revision_marked.{tex,pdf}`: revision-highlighted manuscript for author checking.
- `revision_package/07_response_to_editor_and_reviewers_revised.{docx,pdf}`: formatted response letter with native Word equations and embedded evidence.
- `revision_package/08_response_to_reviewers_chinese_translation.md`: item-by-item Chinese audit of the English response.
- `revision_package/02_bilingual_manuscript_change_audit.md` and `06_complete_original_vs_revised_bilingual_audit.md`: English/Chinese explanation of manuscript changes.

## Figures and Editable Sources

- `revision_package/figures/`: final manuscript figure PDFs, including the revised Fig. 1, compact evolutionary-optimization panel, CLS sensitivity figure, Stage-I figures, hybrid-initialization figure, and Stage-II DQN comparisons.
- `revision_package/response_evidence/`: response-only evidence for joint optimality, alternate-region generalization, CLS initialization, and DQN comparison.
- `revision_package/source_visio/`: original Visio source copies; source files are preserved and were not overwritten.
- `revision_package/spreadsheets/stage2_five_method_results_editable.xlsx`: editable Stage-II five-method chart workbook.

## Experiment Code

The active implementation is in repository `LocalSearch/`. The snapshot copy in `revision_package/code_repro/` preserves the scripts used when the response package was assembled.

Key active entrypoints:

- `LocalSearch/batch_service_experiments.py`
- `LocalSearch/cls_initialization_sensitivity.py`
- `LocalSearch/dqn_service_baseline.py`
- `LocalSearch/hybrid_anchor_sensitivity.py`
- `LocalSearch/joint_optimality_gap.py`
- `LocalSearch/real_region_generalization.py`
- `LocalSearch/run_real_region_stage2.py`
- `LocalSearch/reviewer6_generalization_summary.py`
- `LocalSearch/build_stage2_paper_comparison.py`
- `LocalSearch/plot_stage2_five_method.py`

## Result Data

The canonical machine-readable outputs remain under repository `output/`. This snapshot additionally preserves the compact response inputs under `revision_package/data/`, `revision_package/evidence/`, and `experiment_inputs/`. The snapshot data include both the seven-configuration Stage-II comparison and the raw CSV/NPZ evidence for the alternate-region DQN run.

See `DATA_MANIFEST.md` for provenance, seeds, interpretation, and exclusions.

## Excluded Transient Files

The archive intentionally excludes:

- `tmp/` and `node_modules/`;
- Office/LaTeX build caches;
- page-by-page Word QA renders;
- map-tile cache files;
- duplicated preview images and inspection logs;
- the restricted full base-station source pool and credentials.

These exclusions do not remove any source, final figure, reported value, selected experiment input, or reproducibility script used by the manuscript or response.
