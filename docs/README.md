# SEMASCRIPT Project Pack v0.1

Это complete baseline-пакет проекта SEMASCRIPT для сохранения, переноса и дальнейшей реализации.

## Состав
- `00_PROJECT_IDENTITY.md`
- `01_ARCHITECTURE_MAP.md`
- `02_CURRENT_STATUS.md`
- `03_ROADMAP.md`
- `04_SCOPE_V0_1.md`
- `SEMASCRIPT_0_SEMANTIC_BASELINE.md`
- `SEMASCRIPT_CORE_SPEC_v0.1.md`
- `SEMASCRIPT_PATTERN_TIME_INVARIANT_PACK_v0.1.md`
- `SEMASCRIPT_PROFILE_MATRIX_v0.1.md`
- `SEMASCRIPT_IMPLEMENTATION_PLAN_v0.1.md`
- `SEMASCRIPT_TESTPACK_v0.1.md`
- `SEMASCRIPT_HUMAN_PROFILE_v0.1.md`
- `SEMASCRIPT_EXEC_PROFILE_v0.1.md`
- `SEMASCRIPT_GLYPH_ARCHITECTURE_v0.1.md`
- `SEMASCRIPT_REFERENCE_CORPUS_STARTER_v0.1.md`
- `SEMASCRIPT_TOOLING_MVP_PLAN_v0.1.md`
- `SEMASCRIPT_MANIFEST_v0.1.md`

## Роль пакета
Этот pack нужен как baseline:
- для продолжения проекта без потери контекста;
- для handoff в новый чат или новому инженеру;
- для перехода от идей к спецификации, валидации и реализации.

## Следующий сильный шаг
Начать либо parser/validator MVP, либо расширение corpus и test fixtures.


## Expanded alignment
Starter corpus и test pack синхронизированы с текущим tooling MVP.

- `SEMASCRIPT_HUMAN_NORMALIZER_MVP_v0.1.md` — описание Human normalizer MVP и его границ

- `SEMASCRIPT_GRAMMAR_EXPANSION_v0.1.md` — grammar expansion: list-scope + richer human scene forms

- `SEMASCRIPT_AST_INTEGRATION_PACK_v0.1.md` — AST integration layer for tooling
- `SEMASCRIPT_CORPUS_PIPELINE_v0.1.md` — batch normalization/validation pipeline for corpus

- `SEMASCRIPT_PATTERN_DECOMPOSITION_SPEC_v0.1.md` — первый operational decomposition layer для `SPR/GEN/PAL`

- `SEMASCRIPT_EXEC_RUNTIME_RULES_v0.1.md` — restricted exec runtime semantics for v0.1

- `SEMASCRIPT_STATE_MODEL_v0.1.md` — execution state container and state transition rules

- `SEMASCRIPT_BATCH_RUNTIME_STATE_CORPUS_v0.1.md` — batch runtime/state corpus pipeline and reporting

- `SEMASCRIPT_SVG_RENDERER_SPEC_v0.1.md` — SVG prototype renderer and layout rules

- `SEMASCRIPT_V0_2_HARDENING_SPEC.md` — priority rationale and hardening scope
- `SEMASCRIPT_HARDENING_REGRESSION_SUITE_v0.2.md` — unified hardening regression suite

- `SEMASCRIPT_EDITOR_VISUAL_INSPECTOR_SPEC_v0.1.md` — local editor / visual inspector layer

- `SEMASCRIPT_EDITABLE_VISUAL_GRAPH_MODE_v0.1.md` — graph model + editable visual graph mode

- `SEMASCRIPT_PERSISTED_PROJECT_SESSION_FORMAT_v0.1.md` — persisted project/session format and inspector import/export

- `SEMASCRIPT_MULTI_SESSION_PROJECT_WORKSPACE_v0.1.md` — multi-session workspace and project index

- `SEMASCRIPT_WORKSPACE_NAVIGATION_DEPENDENCY_MAP_v0.1.md` — workspace navigation and dependency map between sessions

- `SEMASCRIPT_WORKSPACE_TIMELINE_SESSION_HISTORY_v0.1.md` — workspace timeline and session evolution history

- `SEMASCRIPT_CROSS_SESSION_COMPARE_DIFF_MODE_v0.1.md` — cross-session compare and diff mode

- `SEMASCRIPT_THREE_WAY_SESSION_MERGE_CONFLICT_DETECTION_v0.1.md` — three-way session merge and conflict detection

- `SEMASCRIPT_INTERACTIVE_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md` — interactive conflict resolution and manual merge decisions

- `SEMASCRIPT_MERGE_COMMIT_RESOLVED_SESSION_INSERTION_v0.1.md` — merge commit and resolved session insertion into workspace

- `SEMASCRIPT_BRANCHING_NAMED_MERGE_LINEAGE_GRAPH_v0.1.md` — branching and named merge lineage graph

- `SEMASCRIPT_BRANCH_REBASE_REPLAY_TARGET_LINEAGE_v0.1.md` — branch rebase and replay onto target lineage

- `SEMASCRIPT_CHERRY_PICK_SELECTIVE_SESSION_REPLAY_ACROSS_BRANCHES_v0.1.md` — cherry-pick and selective session replay across branches

- `SEMASCRIPT_SQUASH_FOLD_MULTIPLE_SESSIONS_INTO_ONE_LINEAGE_COMMIT_v0.1.md` — squash/fold multiple sessions into one lineage commit

- `SEMASCRIPT_RESET_RESTORE_BRANCH_HEAD_TO_HISTORICAL_SESSION_OR_LINEAGE_POINT_v0.1.md` — reset / restore branch head to historical session or lineage point

- `SEMASCRIPT_TAG_RELEASE_POINTS_OVER_SESSIONS_AND_LINEAGE_STATES_v0.1.md` — tag / release points over sessions and lineage states

- `SEMASCRIPT_SNAPSHOT_IMMUTABLE_WORKSPACE_STATE_EXPORT_BY_TAG_OR_RELEASE_POINT_v0.1.md` — snapshot / immutable workspace state export by tag or release point

- `SEMASCRIPT_SNAPSHOT_IMPORT_WORKSPACE_RESTORE_FROM_IMMUTABLE_EXPORT_v0.1.md` — snapshot import / workspace restore from immutable export

- `SEMASCRIPT_SNAPSHOT_DIFF_RESTORE_PREVIEW_BEFORE_APPLY_v0.1.md` — snapshot diff / restore preview before apply

- `SEMASCRIPT_PARTIAL_SNAPSHOT_RESTORE_SELECTIVE_WORKSPACE_STATE_IMPORT_v0.1.md` — partial snapshot restore / selective workspace state import

- `SEMASCRIPT_SNAPSHOT_MERGE_RECONCILE_IMPORTED_STATE_WITH_CURRENT_WORKSPACE_LINEAGE_v0.1.md` — snapshot merge / reconcile imported state with current workspace lineage

- `SEMASCRIPT_SNAPSHOT_CONFLICT_DETECTION_RECONCILE_PREVIEW_BEFORE_APPLY_v0.1.md` — snapshot conflict detection / reconcile preview before apply

- `SEMASCRIPT_SNAPSHOT_CONFLICT_RESOLUTION_MANUAL_RECONCILE_DECISIONS_v0.1.md` — snapshot conflict resolution / manual reconcile decisions

- `SEMASCRIPT_SNAPSHOT_RECONCILE_COMMIT_PROMOTE_RESOLUTION_SET_OR_RELEASE_LINEAGE_POINT_v0.1.md` — snapshot reconcile commit / promote resolved decisions into named resolution set or release lineage point

- `SEMASCRIPT_RESOLUTION_SET_DIFF_COMPARE_BETWEEN_PROMOTED_RECONCILE_OUTCOMES_v0.1.md` — resolution set diff / compare between promoted reconcile outcomes

- `SEMASCRIPT_RESOLUTION_SET_EXPORT_IMPORT_AS_STANDALONE_PROMOTED_OUTCOME_PACKAGE_v0.1.md` — resolution set export/import as standalone promoted outcome package

- `SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md` — standalone outcome package diff / compatibility check before import

- `SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md` — standalone outcome package conflict resolution / manual import decisions

- `SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_INTO_LOCAL_NAMED_OUTCOME_SET_OR_RELEASE_POINT_v0.1.md` — standalone outcome package commit / promote imported resolution into local named outcome set or release point

- `SEMASCRIPT_LOCAL_OUTCOME_SET_DIFF_COMPARE_BETWEEN_IMPORTED_PROMOTED_RESOLUTIONS_v0.1.md` — local outcome set diff / compare between imported promoted resolutions

- `SEMASCRIPT_LOCAL_OUTCOME_SET_EXPORT_IMPORT_AS_PORTABLE_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1.md` — local outcome set export / import as portable local promoted resolution package

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_CHECK_BEFORE_IMPORT_v0.1.md` — portable local outcome package diff / compatibility check before import

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_MANUAL_IMPORT_DECISIONS_v0.1.md` — portable local outcome package conflict resolution / manual import decisions

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_COMMIT_PROMOTE_IMPORTED_RESOLUTION_v0.1.md` — portable local outcome package commit / promote imported resolution

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_DIFF_COMPARE_COMMITTED_IMPORTED_OUTCOMES_v0.1.md` — portable local outcome package diff / compare between committed imported outcomes

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_EXPORT_IMPORT_COMPARE_BASELINE_OR_THREE_WAY_MERGE_BETWEEN_COMMITTED_IMPORTED_OUTCOMES_v0.1.md` — portable local outcome package export / import compare baseline or three-way merge

- `SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_CONFLICT_RESOLUTION_MANUAL_MERGE_DECISIONS_v0.1.md` — portable local outcome package three-way conflict resolution / manual merge decisions
