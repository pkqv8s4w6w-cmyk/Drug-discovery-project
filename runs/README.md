# Run outputs

One directory per run, named by `run_id` (a hash of config + git revision + environment).
Contents are gitignored; this file is committed so the directory exists.

    runs/<run_id>/
      manifest.json          provenance: git sha, config hash, input/output hashes,
                             binary versions, per-stage timings, PREREGISTRATION.md hash
      config.snapshot.yaml   the fully resolved config this run used
      report.html            rendered report
      report.json            every metric
      candidates.csv         the deliverable
      figures/               ROC, enrichment, delta-z distributions, pose images
      logs/
      poses/                 top poses, gzipped

`runs/gate/PASS` is a marker written only when all seven pre-registered gate criteria
pass. `make dev` and `make full` depend on it (ADR-001).
