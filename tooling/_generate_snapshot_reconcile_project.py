
from session_model import create_session_from_text, save_session
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_in_project,
    save_project_index,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Recon Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Recon Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Recon Current Head")

save_session(source_base, "corpus/sample_reconcile_source_base_session.json")
save_session(source_feature, "corpus/sample_reconcile_source_feature_session.json")
save_session(current_head, "corpus/sample_reconcile_current_head_session.json")

source = create_workspace(project_name="Sample Snapshot Reconcile Source")
source = add_session_to_workspace(source, source_base, session_id="recon_base", file_name="sample_reconcile_source_base_session.json", tags=["reconcile"])
source = add_session_to_workspace(source, source_feature, session_id="recon_feature", file_name="sample_reconcile_source_feature_session.json", tags=["reconcile"])
source, _ = create_tag_release_in_project(source, "reconcile_release", "recon_feature", point_kind="release", note="reconcile anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "reconcile_release", snapshot_name="snapshot_reconcile_v1", note="frozen reconcile source")

current = create_workspace(project_name="Sample Snapshot Reconcile Current")
current = add_session_to_workspace(current, current_head, session_id="recon_current", file_name="sample_reconcile_current_head_session.json", tags=["reconcile"])
reconciled, reconcile_result = create_snapshot_reconcile_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    reconcile_name="reconcile_v1",
    selected_session_ids=["recon_feature"],
    target_branch_name="main",
    activate_last_reconciled=True,
)

save_project_index(reconciled, "corpus/sample_snapshot_reconcile_project_index.json")
Path("corpus/sample_snapshot_reconcile_result.json").write_text(json.dumps(reconcile_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_package.json").write_text(json.dumps(snapshot_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
