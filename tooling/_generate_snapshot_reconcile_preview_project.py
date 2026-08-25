
from session_model import create_session_from_text, save_session
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_preview,
)
from pathlib import Path
import json

empty_state = {
    "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
    "resources": {},
    "states": {},
    "dependencies": [],
    "observations": [],
    "actions": [],
    "expansions": [],
    "history": [],
    "metadata": {"applied_steps": 0, "last_schedule": None},
}

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Preview Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Preview Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Preview Current Head")

save_session(source_base, "corpus/sample_reconcile_preview_source_base_session.json")
save_session(source_feature, "corpus/sample_reconcile_preview_source_feature_session.json")
save_session(current_head, "corpus/sample_reconcile_preview_current_head_session.json")

source = create_workspace(project_name="Sample Snapshot Reconcile Preview Source")
source = add_session_to_workspace(source, source_base, session_id="preview_recon_base", file_name="sample_reconcile_preview_source_base_session.json", tags=["reconcile-preview"])
source = add_session_to_workspace(source, source_feature, session_id="preview_recon_feature", file_name="sample_reconcile_preview_source_feature_session.json", tags=["reconcile-preview"])
source, _ = create_tag_release_in_project(source, "reconcile_preview_release", "preview_recon_feature", point_kind="release", note="reconcile preview anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "reconcile_preview_release", snapshot_name="snapshot_reconcile_preview_v1", note="frozen reconcile preview source")

current = create_workspace(project_name="Sample Snapshot Reconcile Preview Current")
current = add_session_to_workspace(current, current_head, session_id="preview_recon_current", file_name="sample_reconcile_preview_current_head_session.json", tags=["reconcile-preview"])
preview = create_snapshot_reconcile_preview(
    current_project_index=current,
    snapshot_package=snapshot_package,
    selected_session_ids=["preview_recon_feature"],
    target_branch_name="main",
    reconcile_name="reconcile_preview_v1",
)

Path("corpus/sample_snapshot_reconcile_preview_result.json").write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_preview_package.json").write_text(json.dumps(snapshot_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
