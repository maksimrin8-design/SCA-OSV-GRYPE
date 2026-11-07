# Ground truth

This directory contains the independently curated expected-vulnerability set used to score scanner results.

## Rules

- A row is scored only when `status=verified`.
- Each verified row identifies a repository, package, exact version, ecosystem, vulnerability ID, and evidence URL.
- Findings not listed in the verified set are **unadjudicated**, not automatically false positives. The CSV is intentionally not treated as a complete list until each project's dependency inventory has been reviewed.
- Do not generate this file from OSV-Scanner or Grype output. That would make the evaluation circular.
- Record the upstream commit SHA, scanner versions, and database timestamps with every run. The workflow saves the upstream SHA and scanner versions as artifacts.
- For an academically defensible full benchmark, verify every expected row against the upstream lockfile and the advisory's affected-version range. Add a negative-control set before reporting precision.

## Current verified seed

`P001` uses the committed fixture at [coder/osv-test](https://github.com/coder/osv-test/blob/main/fixtures/vulnerable/package-lock.json), which pins `minimist@0.0.8`. The corresponding advisory is [GHSA-xvch-5gv4-984h](https://github.com/advisories/GHSA-xvch-5gv4-984h).

At this stage, the corpus contains 30 unique upstream repositories, but only this seed record is marked verified. The other repositories are scan candidates and must not be counted as known-vulnerable until their exact commit and dependency/advisory evidence has been checked.
