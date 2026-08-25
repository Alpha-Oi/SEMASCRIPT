# SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_COMMIT_PROMOTE_v0.1

## Purpose
This document describes the layer that follows:
- portable local outcome package baseline / three-way merge preview
- portable local outcome package three-way conflict resolution / manual merge decisions

The new layer is:
**portable local outcome package three-way merge commit / promote resolved outcome**

## What it adds
- turns a resolved portable local three-way merge into a committed reusable outcome
- records the committed merge in project lineage/history
- allows optional promote into a `release` or `tag` point
- re-exposes the committed result through `local_outcome_set_package_commits` so it can participate in later compare/merge cycles

## Added tooling
- `tooling/project_local_outcome_set_package_commit_merge_commit.py`
- project wrapper in `tooling/project_model.py`
- inspector service entry for merge commit/promote
- server route: `/api/commit-portable-local-outcome-package-three-way-merge-resolution`
- inspector controls for commit name / promote point / note
- `tooling/run_portable_local_outcome_package_merge_commit_checks.py`

## Result shape
The committed result stores:
- `commit_name`
- `resolution_name`
- `base_commit_name`
- `left_commit_name`
- `right_commit_name`
- `target_branch_name`
- `resolved_session_ids`
- `skipped_session_ids`
- `merge_pairs`
- `resolution_pairs`
- optional `promoted_point_name`
- optional `promoted_point_kind`

## Outcome
Portable local outcome package three-way merge is now a complete workflow:
1. compare baseline / three-way merge committed outcomes
2. resolve conflicts with manual decisions
3. commit/promote resolved merge into lineage
