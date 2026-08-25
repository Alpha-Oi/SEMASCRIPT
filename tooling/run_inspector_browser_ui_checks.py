from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from inspector_server import InspectorHandler

try:
    from playwright.sync_api import sync_playwright
except Exception as exc:  # pragma: no cover - import guard for optional browser runner
    sync_playwright = None
    PLAYWRIGHT_IMPORT_ERROR = exc
else:
    PLAYWRIGHT_IMPORT_ERROR = None


ARTIFACT_DIR = Path(__file__).parent / "browser_ui_artifacts"
CORPUS_DIR = Path(__file__).parent / "corpus"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def save_screenshot(page, name: str) -> str:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / name
    page.screenshot(path=str(path), full_page=True)
    return str(path)


def open_page(page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle", timeout=20_000)


def run_page_load_check(page, base_url: str, console_errors: list[str], page_errors: list[str]) -> dict:
    open_page(page, base_url)
    screenshot = save_screenshot(page, "inspector_page_load.png")
    title = page.title()
    h1_text = page.locator("h1").first.inner_text()
    profile_value = page.locator("#profile").input_value()
    profile_hint = page.locator("#profileHint").inner_text()
    has_branch_button = page.locator("#createBranchBtn").count() == 1
    has_snapshot_button = page.locator("#createSnapshotBtn").count() == 1
    has_local_preview_button = page.locator("#previewLocalOutcomeSetPackageBtn").count() == 1
    has_standalone_summary = page.locator("#reconcileCommitPackageCurrentSummary").count() == 1
    has_local_summary = page.locator("#localOutcomeSetPackageCurrentSummary").count() == 1
    body_length = len(page.locator("body").inner_text())
    error_overlay = page.evaluate(
        'document.querySelector("[data-nextjs-dialog], .vite-error-overlay, #webpack-dev-server-client-overlay") ? true : false'
    )

    assert_true("SEMASCRIPT Inspector" in title, f"Unexpected title: {title}")
    assert_true(h1_text == "SEMASCRIPT Inspector", f"Unexpected h1 text: {h1_text}")
    assert_true(profile_value == "human", f"Unexpected default profile: {profile_value}")
    assert_true("gen(template -> instance)" in profile_hint, f"Missing human profile guidance: {profile_hint}")
    assert_true(has_branch_button, "Missing createBranchBtn in live UI")
    assert_true(has_snapshot_button, "Missing createSnapshotBtn in live UI")
    assert_true(has_local_preview_button, "Missing previewLocalOutcomeSetPackageBtn in live UI")
    assert_true(has_standalone_summary, "Missing reconcileCommitPackageCurrentSummary in live UI")
    assert_true(has_local_summary, "Missing localOutcomeSetPackageCurrentSummary in live UI")
    assert_true(body_length > 1000, "Inspector page looks suspiciously empty")
    assert_true(error_overlay is False, "Detected browser error overlay on page load")
    assert_true(not console_errors, f"Console errors on page load: {console_errors[:5]}")
    assert_true(not page_errors, f"Page errors on page load: {page_errors[:5]}")

    return {
        "title": title,
        "profile_value": profile_value,
        "profile_hint": profile_hint,
        "body_length": body_length,
        "screenshot": screenshot,
    }


def run_analyze_project_check(page, base_url: str, console_errors: list[str], page_errors: list[str]) -> dict:
    open_page(page, base_url)
    page.locator("#profile").select_option("human")
    page.locator("#sessionName").fill("browser_smoke_session_human")
    page.locator("#projectName").fill("browser_smoke_project_human")
    page.locator("#inputText").fill("gen(template -> instance)")
    page.locator("#analyzeBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#normalizedText");
            return !!el && el.innerText.trim().length > 0;
        }""",
        timeout=10_000,
    )
    normalized_text = page.locator("#normalizedText").inner_text()
    status_after_analyze = page.locator("#statusText").inner_text()

    page.locator("#addCurrentToProjectBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#projectSessionsList");
            return !!el && el.innerText.trim().length > 0;
        }""",
        timeout=10_000,
    )
    project_sessions_text = page.locator("#projectSessionsList").inner_text()
    status_after_add = page.locator("#statusText").inner_text()
    screenshot = save_screenshot(page, "inspector_analyze_add_project.png")

    assert_true(bool(normalized_text.strip()), "Analyze flow did not populate normalizedText")
    assert_true(status_after_analyze == "Analyzed text input", f"Unexpected analyze status: {status_after_analyze}")
    assert_true(
        "browser_smoke_session_human" in project_sessions_text,
        f"Project session list did not include added session: {project_sessions_text[:200]}",
    )
    assert_true(
        "Current session added to project" in status_after_add,
        f"Unexpected add-to-project status: {status_after_add}",
    )
    assert_true(not console_errors, f"Console errors during analyze/project flow: {console_errors[:5]}")
    assert_true(not page_errors, f"Page errors during analyze/project flow: {page_errors[:5]}")

    return {
        "status_after_analyze": status_after_analyze,
        "status_after_add": status_after_add,
        "normalized_preview": normalized_text[:200],
        "project_sessions_preview": project_sessions_text[:200],
        "screenshot": screenshot,
    }


def run_branch_tag_snapshot_check(page, base_url: str, console_errors: list[str], page_errors: list[str]) -> dict:
    open_page(page, base_url)
    page.locator("#profile").select_option("human")
    page.locator("#sessionName").fill("browser_branch_snapshot_session")
    page.locator("#projectName").fill("browser_branch_snapshot_project")
    page.locator("#inputText").fill("gen(template -> instance)")
    page.locator("#analyzeBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#normalizedText");
            return !!el && el.innerText.trim().length > 0;
        }""",
        timeout=10_000,
    )
    page.locator("#addCurrentToProjectBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#projectSessionsList");
            return !!el && el.innerText.trim().length > 0;
        }""",
        timeout=10_000,
    )

    page.locator("#newBranchName").fill("browser_branch_smoke")
    page.locator("#createBranchBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#branchList");
            return !!el && el.innerText.includes("browser_branch_smoke");
        }""",
        timeout=10_000,
    )
    branch_text = page.locator("#branchList").inner_text()
    status_after_branch = page.locator("#statusText").inner_text()

    page.locator("#tagPointName").fill("browser_release_smoke")
    page.locator("#tagPointKind").select_option("release")
    page.locator("#tagPointNote").fill("browser release point")
    page.locator("#createTagPointBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#tagPointList");
            return !!el && el.innerText.includes("browser_release_smoke");
        }""",
        timeout=10_000,
    )
    tag_text = page.locator("#tagPointList").inner_text()
    status_after_tag = page.locator("#statusText").inner_text()

    page.locator("#snapshotName").fill("browser_snapshot_smoke")
    page.locator("#snapshotNote").fill("browser snapshot export")
    page.locator("#createSnapshotBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#snapshotList");
            return !!el && el.innerText.includes("browser_snapshot_smoke");
        }""",
        timeout=10_000,
    )
    snapshot_text = page.locator("#snapshotList").inner_text()
    status_after_snapshot = page.locator("#statusText").inner_text()
    screenshot = save_screenshot(page, "inspector_branch_tag_snapshot.png")

    assert_true("browser_branch_smoke" in branch_text, f"Branch list did not update: {branch_text[:200]}")
    assert_true(status_after_branch == "Created branch browser_branch_smoke", f"Unexpected branch status: {status_after_branch}")
    assert_true("browser_release_smoke" in tag_text, f"Tag/release list did not update: {tag_text[:200]}")
    assert_true(status_after_tag == "Created release point browser_release_smoke", f"Unexpected tag status: {status_after_tag}")
    assert_true("browser_snapshot_smoke" in snapshot_text, f"Snapshot list did not update: {snapshot_text[:200]}")
    assert_true(
        status_after_snapshot == "Created snapshot export browser_snapshot_smoke",
        f"Unexpected snapshot status: {status_after_snapshot}",
    )
    assert_true(not console_errors, f"Console errors during branch/tag/snapshot flow: {console_errors[:5]}")
    assert_true(not page_errors, f"Page errors during branch/tag/snapshot flow: {page_errors[:5]}")

    return {
        "status_after_branch": status_after_branch,
        "status_after_tag": status_after_tag,
        "status_after_snapshot": status_after_snapshot,
        "branch_preview": branch_text[:200],
        "tag_preview": tag_text[:200],
        "snapshot_preview": snapshot_text[:200],
        "screenshot": screenshot,
    }


def run_profile_preflight_check(page, base_url: str, console_errors: list[str], page_errors: list[str]) -> dict:
    open_page(page, base_url)
    page.locator("#profile").select_option("core")
    page.locator("#inputText").fill("gen(template -> instance)")
    page.locator("#analyzeBtn").click()
    page.wait_for_timeout(500)

    status_text = page.locator("#statusText").inner_text()
    normalized_text = page.locator("#normalizedText").inner_text()
    screenshot = save_screenshot(page, "inspector_profile_preflight.png")

    assert_true(
        'Analyze blocked: profile "core" expects bracket syntax' in status_text,
        f"Unexpected preflight status: {status_text}",
    )
    assert_true(
        'Try profile "human"' in status_text,
        f"Missing human guidance in preflight status: {status_text}",
    )
    assert_true(not normalized_text.strip(), "Analyze preflight should not populate normalizedText")
    assert_true(not console_errors, f"Console errors during profile preflight check: {console_errors[:5]}")
    assert_true(not page_errors, f"Page errors during profile preflight check: {page_errors[:5]}")

    return {
        "status_text": status_text,
        "screenshot": screenshot,
    }


def run_package_guidance_check(page, base_url: str, console_errors: list[str], page_errors: list[str]) -> dict:
    open_page(page, base_url)
    page.locator("#profile").select_option("human")
    page.locator("#sessionName").fill("browser_package_guidance_session")
    page.locator("#projectName").fill("browser_package_guidance_project")
    page.locator("#inputText").fill("gen(template -> instance)")
    page.locator("#analyzeBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#normalizedText");
            return !!el && el.innerText.trim().length > 0;
        }""",
        timeout=10_000,
    )
    page.locator("#addCurrentToProjectBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#projectSessionsList");
            return !!el && el.innerText.trim().length > 0;
        }""",
        timeout=10_000,
    )

    snapshot_package_text = (CORPUS_DIR / "sample_snapshot_export_package.json").read_text(encoding="utf-8")
    page.locator("#snapshotRestoreJson").fill(snapshot_package_text)
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#snapshotPackageHint");
            return !!el && el.innerText.includes("snapshot_release_v1");
        }""",
        timeout=10_000,
    )
    snapshot_hint = page.locator("#snapshotPackageHint").inner_text()
    snapshot_next_action = page.locator("#snapshotPackageHint .package-guidance-next-action").inner_text()
    partial_hint = page.locator("#partialImportSelectionHint").inner_text()
    reconcile_hint = page.locator("#snapshotReconcileSessionHint").inner_text()
    restored_project_name = page.locator("#restoredProjectName").input_value()
    restore_name = page.locator("#snapshotRestoreName").input_value()
    partial_import_name = page.locator("#partialImportName").input_value()
    reconcile_name = page.locator("#snapshotReconcileName").input_value()

    page.locator("#snapshotReconcileName").fill("manual_snapshot_reconcile")
    page.locator("#snapshotRestoreJson").fill(snapshot_package_text)
    page.wait_for_timeout(250)
    preserved_reconcile_name = page.locator("#snapshotReconcileName").input_value()

    page.locator("#importReconcileCommitPackageJson").fill(snapshot_package_text)
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#reconcileCommitPackageHint");
            return !!el && el.innerText.includes("This JSON looks like Snapshot package");
        }""",
        timeout=10_000,
    )
    reconcile_package_hint = page.locator("#reconcileCommitPackageHint").inner_text()

    standalone_package_text = (CORPUS_DIR / "sample_snapshot_reconcile_commit_package.json").read_text(encoding="utf-8")
    page.locator("#importReconcileCommitPackageJson").fill(standalone_package_text)
    page.wait_for_function(
        """() => {
            const hint = document.querySelector("#reconcileCommitPackageHint");
            const name = document.querySelector("#importReconcileCommitPackageName");
            return !!hint && !!name && hint.innerText.includes("pkg_commit_v1_package") && name.value === "pkg_commit_v1_package_import";
        }""",
        timeout=10_000,
    )
    standalone_import_name = page.locator("#importReconcileCommitPackageName").input_value()
    standalone_next_action = page.locator("#reconcileCommitPackageHint .package-guidance-next-action").inner_text()

    local_package_text = (CORPUS_DIR / "sample_local_outcome_set_package.json").read_text(encoding="utf-8")
    page.locator("#importLocalOutcomeSetPackageJson").fill(local_package_text)
    page.wait_for_function(
        """() => {
            const hint = document.querySelector("#localOutcomeSetPackageHint");
            const name = document.querySelector("#importLocalOutcomeSetPackageNameInput");
            return !!hint && !!name && hint.innerText.includes("lp_local_portable") && name.value === "lp_local_portable_import";
        }""",
        timeout=10_000,
    )
    local_import_name = page.locator("#importLocalOutcomeSetPackageNameInput").input_value()
    local_next_action = page.locator("#localOutcomeSetPackageHint .package-guidance-next-action").inner_text()
    screenshot = save_screenshot(page, "inspector_package_guidance.png")

    assert_true("snapshot_release_v1" in snapshot_hint, f"Snapshot hint missing package name: {snapshot_hint}")
    assert_true("Sessions:" in snapshot_hint, f"Snapshot hint missing session summary: {snapshot_hint}")
    assert_true(
        "preview restore, apply partial import, or reconcile selected sessions" in snapshot_next_action,
        f"Snapshot next action missing workflow guidance: {snapshot_next_action}",
    )
    assert_true("tag_base" in partial_hint and "tag_feature" in partial_hint, f"Partial import hint missing session ids: {partial_hint}")
    assert_true("tag_base" in reconcile_hint and "tag_feature" in reconcile_hint, f"Reconcile session hint missing session ids: {reconcile_hint}")
    assert_true(restored_project_name == "restored_snapshot_release_v1", f"Unexpected restored project autofill: {restored_project_name}")
    assert_true(restore_name == "snapshot_release_v1_restore", f"Unexpected restore name autofill: {restore_name}")
    assert_true(partial_import_name == "snapshot_release_v1_partial_import", f"Unexpected partial import autofill: {partial_import_name}")
    assert_true(reconcile_name == "snapshot_release_v1_reconcile", f"Unexpected reconcile name autofill: {reconcile_name}")
    assert_true(preserved_reconcile_name == "manual_snapshot_reconcile", f"Manual snapshot reconcile name was overwritten: {preserved_reconcile_name}")
    assert_true(
        "This JSON looks like Snapshot package" in reconcile_package_hint,
        f"Standalone package hint did not flag snapshot mismatch: {reconcile_package_hint}",
    )
    assert_true(
        "Snapshot workflows" in reconcile_package_hint,
        f"Standalone package hint did not redirect to snapshot workflows: {reconcile_package_hint}",
    )
    assert_true(standalone_import_name == "pkg_commit_v1_package_import", f"Unexpected standalone import autofill: {standalone_import_name}")
    assert_true(local_import_name == "lp_local_portable_import", f"Unexpected local package import autofill: {local_import_name}")
    assert_true(
        "preview compatibility, import directly, or resolve package decisions" in standalone_next_action,
        f"Standalone next action missing workflow guidance: {standalone_next_action}",
    )
    assert_true(
        "preview local import, import directly, or resolve local decisions" in local_next_action,
        f"Local outcome next action missing workflow guidance: {local_next_action}",
    )
    assert_true(not console_errors, f"Console errors during package guidance check: {console_errors[:5]}")
    assert_true(not page_errors, f"Page errors during package guidance check: {page_errors[:5]}")

    return {
        "snapshot_hint": snapshot_hint,
        "partial_hint": partial_hint,
        "reconcile_hint": reconcile_hint,
        "reconcile_package_hint": reconcile_package_hint,
        "snapshot_next_action": snapshot_next_action,
        "restored_project_name": restored_project_name,
        "restore_name": restore_name,
        "partial_import_name": partial_import_name,
        "reconcile_name": reconcile_name,
        "preserved_reconcile_name": preserved_reconcile_name,
        "standalone_import_name": standalone_import_name,
        "local_import_name": local_import_name,
        "standalone_next_action": standalone_next_action,
        "local_next_action": local_next_action,
        "screenshot": screenshot,
    }


def run_local_outcome_commit_check(page, base_url: str, console_errors: list[str], page_errors: list[str]) -> dict:
    open_page(page, base_url)

    project_index_text = (CORPUS_DIR / "sample_local_outcome_set_package_preview_project_index.json").read_text(encoding="utf-8")
    local_package_text = (CORPUS_DIR / "sample_local_outcome_set_package_preview_package.json").read_text(encoding="utf-8")
    local_package = json.loads(local_package_text)
    package_name = local_package["package_name"]
    import_name = f"{package_name}_import"
    commit_name = f"{import_name}_commit"
    promote_name = f"{import_name}_release"

    page.locator("#projectJson").fill(project_index_text)
    page.locator("#importProjectBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const sessions = document.querySelector("#projectSessionsList");
            return !!status && status.innerText === "Project imported" && !!sessions && sessions.innerText.trim().length > 0;
        }""",
        timeout=10_000,
    )

    page.locator("#importLocalOutcomeSetPackageJson").fill(local_package_text)
    page.wait_for_function(
        f"""() => {{
            const hint = document.querySelector("#localOutcomeSetPackageHint");
            const name = document.querySelector("#importLocalOutcomeSetPackageNameInput");
            return !!hint && !!name && hint.innerText.includes("{package_name}") && name.value === "{import_name}";
        }}""",
        timeout=10_000,
    )

    page.locator("#previewLocalOutcomeSetPackageBtn").click()
    page.wait_for_function(
        """() => {
            const preview = document.querySelector("#localOutcomeSetPackagePreviewResultText");
            return !!preview && preview.innerText.includes("preview_items");
        }""",
        timeout=10_000,
    )

    page.locator("#usePackageForAllLocalOutcomeBtn").click()
    page.locator("#applyLocalOutcomePackageDecisionsBtn").click()
    page.wait_for_function(
        f"""() => {{
            const status = document.querySelector("#statusText");
            const commitName = document.querySelector("#localOutcomeSetPackageCommitName");
            const promoteName = document.querySelector("#localOutcomeSetPackagePromotePointName");
            return !!status
                && status.innerText.includes("Resolved local outcome package import")
                && !!commitName
                && !!promoteName
                && commitName.value === "{commit_name}"
                && promoteName.value === "{promote_name}";
        }}""",
        timeout=10_000,
    )

    resolution_status = page.locator("#statusText").inner_text()
    autofilled_commit_name = page.locator("#localOutcomeSetPackageCommitName").input_value()
    autofilled_promote_name = page.locator("#localOutcomeSetPackagePromotePointName").input_value()
    page.locator("#localOutcomeSetPackageCommitNote").fill("browser local outcome commit")
    page.locator("#commitLocalOutcomeSetPackageBtn").click()
    page.wait_for_function(
        f"""() => {{
            const status = document.querySelector("#statusText");
            const list = document.querySelector("#localOutcomeSetPackageList");
            const baseSelect = document.querySelector("#basePortableLocalOutcomeCommit");
            return !!status
                && status.innerText.includes("Committed local outcome package resolution")
                && !!list
                && list.innerText.includes("{commit_name}")
                && !!baseSelect
                && Array.from(baseSelect.options || []).some((item) => item.value === "{commit_name}");
        }}""",
        timeout=10_000,
    )

    commit_status = page.locator("#statusText").inner_text()
    local_package_list = page.locator("#localOutcomeSetPackageList").inner_text()
    portable_commit_options = page.locator("#basePortableLocalOutcomeCommit option").all_inner_texts()
    screenshot = save_screenshot(page, "inspector_local_outcome_commit.png")

    assert_true(
        "Resolved local outcome package import" in resolution_status,
        f"Unexpected local outcome resolution status: {resolution_status}",
    )
    assert_true(
        autofilled_commit_name == commit_name,
        f"Unexpected local outcome commit autofill: {autofilled_commit_name}",
    )
    assert_true(
        autofilled_promote_name == promote_name,
        f"Unexpected local outcome promote autofill: {autofilled_promote_name}",
    )
    assert_true(
        "Committed local outcome package resolution" in commit_status,
        f"Unexpected local outcome commit status: {commit_status}",
    )
    assert_true(
        commit_name in local_package_list,
        f"Local outcome package list missing committed outcome: {local_package_list[:300]}",
    )
    assert_true(
        commit_name in portable_commit_options,
        f"Portable merge selectors missing committed outcome: {portable_commit_options}",
    )
    assert_true(not console_errors, f"Console errors during local outcome commit check: {console_errors[:5]}")
    assert_true(not page_errors, f"Page errors during local outcome commit check: {page_errors[:5]}")

    return {
        "resolution_status": resolution_status,
        "commit_status": commit_status,
        "autofilled_commit_name": autofilled_commit_name,
        "autofilled_promote_name": autofilled_promote_name,
        "portable_commit_options": portable_commit_options,
        "screenshot": screenshot,
    }


def run_package_pipeline_check(page, base_url: str, console_errors: list[str], page_errors: list[str]) -> dict:
    open_page(page, base_url)

    standalone_package_text = (CORPUS_DIR / "sample_snapshot_reconcile_commit_package_commit_package.json").read_text(encoding="utf-8")
    standalone_package = json.loads(standalone_package_text)
    standalone_package_name = standalone_package["package_name"]

    page.locator("#profile").select_option("human")
    page.locator("#sessionName").fill("browser_full_pipeline_session")
    page.locator("#projectName").fill("browser_full_pipeline_project")
    page.locator("#inputText").fill("spr(seed -> portable_current)")
    page.locator("#analyzeBtn").click()
    page.wait_for_function(
        """() => {
            const el = document.querySelector("#normalizedText");
            return !!el && el.innerText.trim().length > 0;
        }""",
        timeout=10_000,
    )
    page.locator("#addCurrentToProjectBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const el = document.querySelector("#projectSessionsList");
            return !!status
                && status.innerText.includes("Current session added to project")
                && !!el
                && el.innerText.includes("browser_full_pipeline_session");
        }""",
        timeout=10_000,
    )

    page.locator("#importReconcileCommitPackageJson").fill(standalone_package_text)
    page.wait_for_function(
        f"""() => {{
            const hint = document.querySelector("#reconcileCommitPackageHint");
            return !!hint && hint.innerText.includes("{standalone_package_name}");
        }}""",
        timeout=10_000,
    )

    page.locator("#importReconcileCommitPackageName").fill("browser_standalone_resolution")
    page.locator("#previewReconcileCommitPackageBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const preview = document.querySelector("#reconcileCommitPackagePreviewText");
            return !!status
                && status.innerText.includes("Previewed standalone package compatibility")
                && !!preview
                && preview.innerText.includes("preview_items");
        }""",
        timeout=10_000,
    )

    page.locator("#usePackageForAllImportBtn").click()
    page.locator("#applyReconcileCommitPackageDecisionsBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const commitName = document.querySelector("#reconcileCommitPackageCommitName");
            const promoteName = document.querySelector("#reconcileCommitPackagePromotePointName");
            return !!status
                && status.innerText === "Resolved standalone package import browser_standalone_resolution"
                && !!commitName
                && !!promoteName
                && commitName.value === "browser_standalone_resolution_commit"
                && promoteName.value === "browser_standalone_resolution_release";
        }""",
        timeout=10_000,
    )

    autofilled_standalone_commit = page.locator("#reconcileCommitPackageCommitName").input_value()
    autofilled_standalone_promote = page.locator("#reconcileCommitPackagePromotePointName").input_value()
    page.locator("#reconcileCommitPackageCommitName").fill("browser_local_outcome_commit")
    page.locator("#reconcileCommitPackagePromotePointName").fill("browser_local_outcome_release")
    page.locator("#reconcileCommitPackageCommitNote").fill("browser standalone commit")
    page.locator("#commitReconcileCommitPackageBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const select = document.querySelector("#exportLocalOutcomeSetCommit");
            return !!status
                && status.innerText === "Committed imported package resolution browser_local_outcome_commit"
                && !!select
                && Array.from(select.options || []).some((item) => item.value === "browser_local_outcome_commit");
        }""",
        timeout=10_000,
    )

    page.locator("#exportLocalOutcomeSetCommit").select_option("browser_local_outcome_commit")
    page.wait_for_function(
        """() => {
            const packageName = document.querySelector("#localOutcomeSetPackageName");
            return !!packageName && packageName.value === "browser_local_outcome_commit_package";
        }""",
        timeout=10_000,
    )
    autofilled_local_package_name = page.locator("#localOutcomeSetPackageName").input_value()
    page.locator("#localOutcomeSetPackageName").fill("browser_local_package")
    page.locator("#localOutcomeSetPackageNote").fill("browser portable local package")
    page.locator("#exportLocalOutcomeSetPackageBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const list = document.querySelector("#localOutcomeSetPackageList");
            const summary = document.querySelector("#localOutcomeSetPackageCurrentSummary");
            return !!status
                && status.innerText === "Exported local outcome package browser_local_package"
                && !!list
                && list.innerText.includes("browser_local_package")
                && !!summary
                && summary.innerText.includes("browser_local_package")
                && summary.innerText.includes("browser_local_outcome_commit");
        }""",
        timeout=10_000,
    )

    page.locator("#useCurrentLocalOutcomeSetPackageBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const textarea = document.querySelector("#importLocalOutcomeSetPackageJson");
            return !!status
                && status.innerText === "Loaded current local outcome package"
                && !!textarea
                && textarea.value.trim().length > 0;
        }""",
        timeout=10_000,
    )

    def run_local_commit_round(resolution_name: str, note: str, custom_text: str | None = None) -> None:
        commit_name = f"{resolution_name}_commit"
        promote_name = f"{resolution_name}_release"
        page.locator("#importLocalOutcomeSetPackageNameInput").fill(resolution_name)
        page.locator("#previewLocalOutcomeSetPackageBtn").click()
        page.wait_for_function(
            """() => {
                const status = document.querySelector("#statusText");
                const preview = document.querySelector("#localOutcomeSetPackagePreviewResultText");
                return !!status
                    && status.innerText.includes("Previewed local outcome package")
                    && !!preview
                    && preview.innerText.includes("preview_items");
            }""",
            timeout=10_000,
        )

        if custom_text is None:
            page.locator("#usePackageForAllLocalOutcomeBtn").click()
        else:
            page.locator("#localOutcomeSetPackageDecisionList select").first.select_option("custom_text")
            page.locator("#localOutcomeSetPackageDecisionList textarea").first.fill(custom_text)

        page.locator("#applyLocalOutcomePackageDecisionsBtn").click()
        page.wait_for_function(
            f"""() => {{
                const status = document.querySelector("#statusText");
                const commitName = document.querySelector("#localOutcomeSetPackageCommitName");
                const promoteName = document.querySelector("#localOutcomeSetPackagePromotePointName");
                return !!status
                    && status.innerText === "Resolved local outcome package import {resolution_name}"
                    && !!commitName
                    && !!promoteName
                    && commitName.value === "{commit_name}"
                    && promoteName.value === "{promote_name}";
            }}""",
            timeout=10_000,
        )

        page.locator("#localOutcomeSetPackageCommitNote").fill(note)
        page.locator("#commitLocalOutcomeSetPackageBtn").click()
        page.wait_for_function(
            f"""() => {{
                const status = document.querySelector("#statusText");
                const baseSelect = document.querySelector("#basePortableLocalOutcomeCommit");
                return !!status
                    && status.innerText === "Committed local outcome package resolution {commit_name}"
                    && !!baseSelect
                    && Array.from(baseSelect.options || []).some((item) => item.value === "{commit_name}");
            }}""",
            timeout=10_000,
        )

    run_local_commit_round("browser_base_resolution", "browser base outcome")
    run_local_commit_round("browser_left_resolution", "browser left outcome", "spr(seed -> left_browser_form)")
    run_local_commit_round("browser_right_resolution", "browser right outcome", "spr(seed -> right_browser_form)")

    page.locator("#basePortableLocalOutcomeCommit").select_option("browser_base_resolution_commit")
    page.locator("#leftPortableLocalOutcomeCommit").select_option("browser_left_resolution_commit")
    page.locator("#rightPortableLocalOutcomeCommit").select_option("browser_right_resolution_commit")
    page.locator("#portableLocalOutcomeMergeResolutionName").fill("browser_portable_merge_resolution")
    page.locator("#compareThreeWayPortableLocalOutcomeBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const queue = document.querySelector("#portableMergeSessionList");
            const overview = document.querySelector("#portableMergeOverview");
            const detail = document.querySelector("#portableMergeDetail");
            return !!status
                && status.innerText === "Compared baseline/three-way merge browser_base_resolution_commit / browser_left_resolution_commit / browser_right_resolution_commit"
                && !!queue
                && queue.innerText.trim().length > 0
                && !!overview
                && overview.innerText.includes("Manual decisions")
                && overview.innerText.includes("Skipped")
                && !!detail
                && detail.innerText.includes("Review decisions, then apply merge decisions.");
        }""",
        timeout=10_000,
    )
    portable_merge_guidance = page.locator("#portableMergeDetail").inner_text()
    portable_merge_overview = page.locator("#portableMergeOverview").inner_text()

    page.locator("#useRightForAllPortableLocalMergeConflictsBtn").click()
    page.locator("#applyPortableLocalOutcomeMergeDecisionsBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const result = document.querySelector("#portableLocalOutcomeMergeResolutionResultText");
            const commitName = document.querySelector("#portableLocalOutcomeMergeCommitName");
            const promoteName = document.querySelector("#portableLocalOutcomeMergePromotePointName");
            const detail = document.querySelector("#portableMergeDetail");
            return !!status
                && status.innerText === "Resolved portable local outcome three-way merge browser_portable_merge_resolution"
                && !!result
                && result.innerText.includes("browser_portable_merge_resolution")
                && !!commitName
                && !!promoteName
                && commitName.value === "browser_portable_merge_resolution_commit"
                && promoteName.value === "browser_portable_merge_resolution_release"
                && !!detail
                && detail.innerText.includes("Ready to commit resolved portable merge.");
        }""",
        timeout=10_000,
    )

    autofilled_merge_commit = page.locator("#portableLocalOutcomeMergeCommitName").input_value()
    autofilled_merge_promote = page.locator("#portableLocalOutcomeMergePromotePointName").input_value()
    portable_merge_resolution_guidance = page.locator("#portableMergeDetail").inner_text()
    page.locator("#portableLocalOutcomeMergeCommitNote").fill("browser portable merge commit")
    page.locator("#commitPortableLocalOutcomeMergeBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const result = document.querySelector("#portableLocalOutcomeMergeCommitResultText");
            return !!status
                && status.innerText === "Committed portable local outcome three-way merge browser_portable_merge_resolution_commit"
                && !!result
                && result.innerText.includes("browser_portable_merge_resolution_commit");
        }""",
        timeout=10_000,
    )

    final_status = page.locator("#statusText").inner_text()
    local_package_list = page.locator("#localOutcomeSetPackageList").inner_text()
    merge_commit_result = page.locator("#portableLocalOutcomeMergeCommitResultText").inner_text()
    screenshot = save_screenshot(page, "inspector_package_pipeline.png")

    assert_true(
        "browser_base_resolution_commit" in local_package_list
        and "browser_left_resolution_commit" in local_package_list
        and "browser_right_resolution_commit" in local_package_list,
        f"Local package list missing base/left/right committed outcomes: {local_package_list[:500]}",
    )
    assert_true(
        autofilled_standalone_commit == "browser_standalone_resolution_commit",
        f"Unexpected standalone resolution commit autofill: {autofilled_standalone_commit}",
    )
    assert_true(
        autofilled_standalone_promote == "browser_standalone_resolution_release",
        f"Unexpected standalone resolution promote autofill: {autofilled_standalone_promote}",
    )
    assert_true(
        autofilled_local_package_name == "browser_local_outcome_commit_package",
        f"Unexpected local outcome export package autofill: {autofilled_local_package_name}",
    )
    assert_true(
        autofilled_merge_commit == "browser_portable_merge_resolution_commit",
        f"Unexpected portable merge commit autofill: {autofilled_merge_commit}",
    )
    assert_true(
        autofilled_merge_promote == "browser_portable_merge_resolution_release",
        f"Unexpected portable merge promote autofill: {autofilled_merge_promote}",
    )
    assert_true(
        "Manual decisions" in portable_merge_overview and "Skipped" in portable_merge_overview,
        f"Portable merge overview missing decision-density stats: {portable_merge_overview[:300]}",
    )
    assert_true(
        "Review decisions, then apply merge decisions." in portable_merge_guidance,
        f"Portable merge guidance missing review/apply next action: {portable_merge_guidance[:300]}",
    )
    assert_true(
        "Ready to commit resolved portable merge." in portable_merge_resolution_guidance,
        f"Portable merge guidance missing commit next action: {portable_merge_resolution_guidance[:300]}",
    )
    assert_true(
        final_status == "Committed portable local outcome three-way merge browser_portable_merge_resolution_commit",
        f"Unexpected final pipeline status: {final_status}",
    )
    assert_true(
        "browser_portable_merge_resolution_commit" in merge_commit_result,
        f"Portable merge commit result missing commit name: {merge_commit_result[:300]}",
    )
    assert_true(not console_errors, f"Console errors during package pipeline check: {console_errors[:5]}")
    assert_true(not page_errors, f"Page errors during package pipeline check: {page_errors[:5]}")

    return {
        "final_status": final_status,
        "autofilled_standalone_commit": autofilled_standalone_commit,
        "autofilled_local_package_name": autofilled_local_package_name,
        "autofilled_merge_commit": autofilled_merge_commit,
        "portable_merge_guidance_preview": portable_merge_guidance[:200],
        "merge_commit_result_preview": merge_commit_result[:200],
        "local_package_list_preview": local_package_list[:300],
        "screenshot": screenshot,
    }


def run_snapshot_to_portable_pipeline_check(page, base_url: str, console_errors: list[str], page_errors: list[str]) -> dict:
    open_page(page, base_url)

    source_project_text = (CORPUS_DIR / "sample_snapshot_reconcile_project_index.json").read_text(encoding="utf-8")
    snapshot_package_text = (CORPUS_DIR / "sample_snapshot_reconcile_package.json").read_text(encoding="utf-8")
    target_project_text = (CORPUS_DIR / "sample_snapshot_reconcile_commit_package_project_index.json").read_text(encoding="utf-8")

    page.locator("#projectJson").fill(source_project_text)
    page.locator("#importProjectBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const sessions = document.querySelector("#projectSessionsList");
            return !!status
                && status.innerText === "Project imported"
                && !!sessions
                && sessions.innerText.includes("recon_current");
        }""",
        timeout=10_000,
    )

    page.locator("#snapshotRestoreJson").fill(snapshot_package_text)
    page.wait_for_function(
        """() => {
            const hint = document.querySelector("#snapshotPackageHint");
            return !!hint && hint.innerText.includes("snapshot_reconcile_v1");
        }""",
        timeout=10_000,
    )

    page.locator("#snapshotReconcileSessionIds").fill("recon_feature")
    page.locator("#snapshotReconcileName").fill("browser_snapshot_pipeline_reconcile")
    page.locator("#previewSnapshotReconcileBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const preview = document.querySelector("#snapshotReconcilePreviewText");
            return !!status
                && status.innerText === "Previewed snapshot reconcile browser_snapshot_pipeline_reconcile"
                && !!preview
                && preview.innerText.includes("preview_items");
        }""",
        timeout=10_000,
    )

    page.locator("#useSnapshotForAllReconcileBtn").click()
    page.locator("#applySnapshotReconcileDecisionsBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const result = document.querySelector("#snapshotReconcileResultText");
            const commitName = document.querySelector("#snapshotReconcileCommitName");
            const promoteName = document.querySelector("#snapshotReconcilePromotePointName");
            return !!status
                && status.innerText === "Applied snapshot reconcile resolution browser_snapshot_pipeline_reconcile"
                && !!result
                && result.innerText.includes("browser_snapshot_pipeline_reconcile")
                && !!commitName
                && !!promoteName
                && commitName.value === "browser_snapshot_pipeline_reconcile_commit"
                && promoteName.value === "browser_snapshot_pipeline_reconcile_release";
        }""",
        timeout=10_000,
    )

    autofilled_snapshot_commit = page.locator("#snapshotReconcileCommitName").input_value()
    autofilled_snapshot_promote = page.locator("#snapshotReconcilePromotePointName").input_value()
    page.locator("#snapshotReconcileCommitName").fill("browser_snapshot_pipeline_commit")
    page.locator("#snapshotReconcilePromotePointName").fill("browser_snapshot_pipeline_release")
    page.locator("#snapshotReconcileCommitNote").fill("browser snapshot pipeline commit")
    page.locator("#commitSnapshotReconcileBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const list = document.querySelector("#snapshotReconcileCommitList");
            return !!status
                && status.innerText === "Committed snapshot reconcile browser_snapshot_pipeline_commit"
                && !!list
                && list.innerText.includes("browser_snapshot_pipeline_commit");
        }""",
        timeout=10_000,
    )

    page.locator("#exportReconcileCommitName").select_option("browser_snapshot_pipeline_commit")
    page.wait_for_function(
        """() => {
            const packageName = document.querySelector("#exportReconcileCommitPackageName");
            return !!packageName && packageName.value === "browser_snapshot_pipeline_commit_package";
        }""",
        timeout=10_000,
    )
    autofilled_snapshot_package_name = page.locator("#exportReconcileCommitPackageName").input_value()
    page.locator("#exportReconcileCommitPackageName").fill("browser_snapshot_pipeline_package")
    page.locator("#exportReconcileCommitPackageBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const result = document.querySelector("#reconcileCommitPackageResultText");
            const summary = document.querySelector("#reconcileCommitPackageCurrentSummary");
            return !!status
                && status.innerText === "Exported standalone package browser_snapshot_pipeline_package"
                && !!result
                && result.innerText.includes("browser_snapshot_pipeline_package")
                && !!summary
                && summary.innerText.includes("browser_snapshot_pipeline_package")
                && summary.innerText.includes("browser_snapshot_pipeline_commit");
        }""",
        timeout=10_000,
    )
    source_snapshot_commit_list = page.locator("#snapshotReconcileCommitList").inner_text()
    standalone_package_text = page.locator("#reconcileCommitPackageResultText").inner_text()
    standalone_package = json.loads(standalone_package_text)

    page.locator("#projectJson").fill(target_project_text)
    page.locator("#importProjectBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const sessions = document.querySelector("#projectSessionsList");
            return !!status
                && status.innerText === "Project imported"
                && !!sessions
                && sessions.innerText.includes("pkg_current");
        }""",
        timeout=10_000,
    )

    page.locator("#importReconcileCommitPackageJson").fill(standalone_package_text)
    page.wait_for_function(
        """() => {
            const hint = document.querySelector("#reconcileCommitPackageHint");
            return !!hint && hint.innerText.includes("browser_snapshot_pipeline_package");
        }""",
        timeout=10_000,
    )

    page.locator("#importReconcileCommitPackageName").fill("browser_snapshot_pipeline_import")
    page.locator("#previewReconcileCommitPackageBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const preview = document.querySelector("#reconcileCommitPackagePreviewText");
            return !!status
                && status.innerText === "Previewed standalone package compatibility browser_snapshot_pipeline_package"
                && !!preview
                && preview.innerText.includes("exact_match");
        }""",
        timeout=10_000,
    )

    page.locator("#usePackageForAllImportBtn").click()
    page.locator("#applyReconcileCommitPackageDecisionsBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const list = document.querySelector("#reconcileCommitPackageList");
            const commitName = document.querySelector("#reconcileCommitPackageCommitName");
            const promoteName = document.querySelector("#reconcileCommitPackagePromotePointName");
            return !!status
                && status.innerText === "Resolved standalone package import browser_snapshot_pipeline_import"
                && !!list
                && list.innerText.includes("browser_snapshot_pipeline_import")
                && !!commitName
                && !!promoteName
                && commitName.value === "browser_snapshot_pipeline_import_commit"
                && promoteName.value === "browser_snapshot_pipeline_import_release";
        }""",
        timeout=10_000,
    )

    autofilled_snapshot_local_commit = page.locator("#reconcileCommitPackageCommitName").input_value()
    autofilled_snapshot_local_promote = page.locator("#reconcileCommitPackagePromotePointName").input_value()
    page.locator("#reconcileCommitPackageCommitName").fill("browser_snapshot_pipeline_local_commit")
    page.locator("#reconcileCommitPackagePromotePointName").fill("browser_snapshot_pipeline_local_release")
    page.locator("#reconcileCommitPackageCommitNote").fill("browser snapshot pipeline standalone commit")
    page.locator("#commitReconcileCommitPackageBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const select = document.querySelector("#exportLocalOutcomeSetCommit");
            return !!status
                && status.innerText === "Committed imported package resolution browser_snapshot_pipeline_local_commit"
                && !!select
                && Array.from(select.options || []).some((item) => item.value === "browser_snapshot_pipeline_local_commit");
        }""",
        timeout=10_000,
    )

    page.locator("#exportLocalOutcomeSetCommit").select_option("browser_snapshot_pipeline_local_commit")
    page.wait_for_function(
        """() => {
            const packageName = document.querySelector("#localOutcomeSetPackageName");
            return !!packageName && packageName.value === "browser_snapshot_pipeline_local_commit_package";
        }""",
        timeout=10_000,
    )
    autofilled_snapshot_local_package_name = page.locator("#localOutcomeSetPackageName").input_value()
    page.locator("#localOutcomeSetPackageName").fill("browser_snapshot_local_package")
    page.locator("#localOutcomeSetPackageNote").fill("browser snapshot local package")
    page.locator("#exportLocalOutcomeSetPackageBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const result = document.querySelector("#localOutcomeSetPackageResultText");
            const summary = document.querySelector("#localOutcomeSetPackageCurrentSummary");
            return !!status
                && status.innerText === "Exported local outcome package browser_snapshot_local_package"
                && !!result
                && result.innerText.includes("browser_snapshot_local_package")
                && !!summary
                && summary.innerText.includes("browser_snapshot_local_package")
                && summary.innerText.includes("browser_snapshot_pipeline_local_commit");
        }""",
        timeout=10_000,
    )

    page.locator("#useCurrentLocalOutcomeSetPackageBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const textarea = document.querySelector("#importLocalOutcomeSetPackageJson");
            return !!status
                && status.innerText === "Loaded current local outcome package"
                && !!textarea
                && textarea.value.trim().length > 0;
        }""",
        timeout=10_000,
    )

    def run_local_commit_round(resolution_name: str, note: str, custom_text: str | None = None) -> None:
        commit_name = f"{resolution_name}_commit"
        promote_name = f"{resolution_name}_release"
        page.locator("#importLocalOutcomeSetPackageNameInput").fill(resolution_name)
        page.locator("#previewLocalOutcomeSetPackageBtn").click()
        page.wait_for_function(
            """() => {
                const status = document.querySelector("#statusText");
                const preview = document.querySelector("#localOutcomeSetPackagePreviewResultText");
                return !!status
                    && status.innerText.includes("Previewed local outcome package")
                    && !!preview
                    && preview.innerText.includes("preview_items");
            }""",
            timeout=10_000,
        )

        if custom_text is None:
            page.locator("#usePackageForAllLocalOutcomeBtn").click()
        else:
            page.locator("#localOutcomeSetPackageDecisionList select").first.select_option("custom_text")
            page.locator("#localOutcomeSetPackageDecisionList textarea").first.fill(custom_text)

        page.locator("#applyLocalOutcomePackageDecisionsBtn").click()
        page.wait_for_function(
            f"""() => {{
                const status = document.querySelector("#statusText");
                const commitName = document.querySelector("#localOutcomeSetPackageCommitName");
                const promoteName = document.querySelector("#localOutcomeSetPackagePromotePointName");
                return !!status
                    && status.innerText === "Resolved local outcome package import {resolution_name}"
                    && !!commitName
                    && !!promoteName
                    && commitName.value === "{commit_name}"
                    && promoteName.value === "{promote_name}";
            }}""",
            timeout=10_000,
        )

        page.locator("#localOutcomeSetPackageCommitNote").fill(note)
        page.locator("#commitLocalOutcomeSetPackageBtn").click()
        page.wait_for_function(
            f"""() => {{
                const status = document.querySelector("#statusText");
                const baseSelect = document.querySelector("#basePortableLocalOutcomeCommit");
                return !!status
                    && status.innerText === "Committed local outcome package resolution {commit_name}"
                    && !!baseSelect
                    && Array.from(baseSelect.options || []).some((item) => item.value === "{commit_name}");
            }}""",
            timeout=10_000,
        )

    run_local_commit_round("browser_snapshot_base_resolution", "browser snapshot base outcome")
    run_local_commit_round("browser_snapshot_left_resolution", "browser snapshot left outcome", "spr(seed -> left_browser_form)")
    run_local_commit_round("browser_snapshot_right_resolution", "browser snapshot right outcome", "spr(seed -> right_browser_form)")

    page.locator("#basePortableLocalOutcomeCommit").select_option("browser_snapshot_base_resolution_commit")
    page.locator("#leftPortableLocalOutcomeCommit").select_option("browser_snapshot_left_resolution_commit")
    page.locator("#rightPortableLocalOutcomeCommit").select_option("browser_snapshot_right_resolution_commit")
    page.locator("#portableLocalOutcomeMergeResolutionName").fill("browser_snapshot_portable_merge_resolution")
    page.locator("#compareThreeWayPortableLocalOutcomeBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const queue = document.querySelector("#portableMergeSessionList");
            const overview = document.querySelector("#portableMergeOverview");
            const detail = document.querySelector("#portableMergeDetail");
            return !!status
                && status.innerText === "Compared baseline/three-way merge browser_snapshot_base_resolution_commit / browser_snapshot_left_resolution_commit / browser_snapshot_right_resolution_commit"
                && !!queue
                && queue.innerText.trim().length > 0
                && !!overview
                && overview.innerText.includes("Manual decisions")
                && overview.innerText.includes("Skipped")
                && !!detail
                && detail.innerText.includes("Review decisions, then apply merge decisions.");
        }""",
        timeout=10_000,
    )
    snapshot_portable_merge_guidance = page.locator("#portableMergeDetail").inner_text()
    snapshot_portable_merge_overview = page.locator("#portableMergeOverview").inner_text()

    page.locator("#useRightForAllPortableLocalMergeConflictsBtn").click()
    page.locator("#applyPortableLocalOutcomeMergeDecisionsBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const result = document.querySelector("#portableLocalOutcomeMergeResolutionResultText");
            const commitName = document.querySelector("#portableLocalOutcomeMergeCommitName");
            const promoteName = document.querySelector("#portableLocalOutcomeMergePromotePointName");
            const detail = document.querySelector("#portableMergeDetail");
            return !!status
                && status.innerText === "Resolved portable local outcome three-way merge browser_snapshot_portable_merge_resolution"
                && !!result
                && result.innerText.includes("browser_snapshot_portable_merge_resolution")
                && !!commitName
                && !!promoteName
                && commitName.value === "browser_snapshot_portable_merge_resolution_commit"
                && promoteName.value === "browser_snapshot_portable_merge_resolution_release"
                && !!detail
                && detail.innerText.includes("Ready to commit resolved portable merge.");
        }""",
        timeout=10_000,
    )

    autofilled_snapshot_merge_commit = page.locator("#portableLocalOutcomeMergeCommitName").input_value()
    autofilled_snapshot_merge_promote = page.locator("#portableLocalOutcomeMergePromotePointName").input_value()
    snapshot_portable_merge_resolution_guidance = page.locator("#portableMergeDetail").inner_text()
    page.locator("#portableLocalOutcomeMergeCommitNote").fill("browser snapshot portable merge commit")
    page.locator("#commitPortableLocalOutcomeMergeBtn").click()
    page.wait_for_function(
        """() => {
            const status = document.querySelector("#statusText");
            const result = document.querySelector("#portableLocalOutcomeMergeCommitResultText");
            return !!status
                && status.innerText === "Committed portable local outcome three-way merge browser_snapshot_portable_merge_resolution_commit"
                && !!result
                && result.innerText.includes("browser_snapshot_portable_merge_resolution_commit");
        }""",
        timeout=10_000,
    )

    final_status = page.locator("#statusText").inner_text()
    local_package_list = page.locator("#localOutcomeSetPackageList").inner_text()
    merge_commit_result = page.locator("#portableLocalOutcomeMergeCommitResultText").inner_text()
    screenshot = save_screenshot(page, "inspector_snapshot_to_portable_pipeline.png")

    assert_true(
        standalone_package["package_name"] == "browser_snapshot_pipeline_package",
        f"Unexpected standalone package export payload: {standalone_package.get('package_name')}",
    )
    assert_true(
        autofilled_snapshot_commit == "browser_snapshot_pipeline_reconcile_commit",
        f"Unexpected snapshot reconcile commit autofill: {autofilled_snapshot_commit}",
    )
    assert_true(
        autofilled_snapshot_promote == "browser_snapshot_pipeline_reconcile_release",
        f"Unexpected snapshot reconcile promote autofill: {autofilled_snapshot_promote}",
    )
    assert_true(
        autofilled_snapshot_package_name == "browser_snapshot_pipeline_commit_package",
        f"Unexpected standalone export package autofill: {autofilled_snapshot_package_name}",
    )
    assert_true(
        autofilled_snapshot_local_commit == "browser_snapshot_pipeline_import_commit",
        f"Unexpected imported standalone commit autofill: {autofilled_snapshot_local_commit}",
    )
    assert_true(
        autofilled_snapshot_local_promote == "browser_snapshot_pipeline_import_release",
        f"Unexpected imported standalone promote autofill: {autofilled_snapshot_local_promote}",
    )
    assert_true(
        autofilled_snapshot_local_package_name == "browser_snapshot_pipeline_local_commit_package",
        f"Unexpected snapshot local package export autofill: {autofilled_snapshot_local_package_name}",
    )
    assert_true(
        "browser_snapshot_pipeline_commit" in source_snapshot_commit_list,
        f"Snapshot reconcile commit list missing committed outcome before handoff: {source_snapshot_commit_list[:300]}",
    )
    assert_true(
        "browser_snapshot_base_resolution_commit" in local_package_list
        and "browser_snapshot_left_resolution_commit" in local_package_list
        and "browser_snapshot_right_resolution_commit" in local_package_list,
        f"Local package list missing browser snapshot commit chain: {local_package_list[:500]}",
    )
    assert_true(
        autofilled_snapshot_merge_commit == "browser_snapshot_portable_merge_resolution_commit",
        f"Unexpected snapshot portable merge commit autofill: {autofilled_snapshot_merge_commit}",
    )
    assert_true(
        autofilled_snapshot_merge_promote == "browser_snapshot_portable_merge_resolution_release",
        f"Unexpected snapshot portable merge promote autofill: {autofilled_snapshot_merge_promote}",
    )
    assert_true(
        "Manual decisions" in snapshot_portable_merge_overview and "Skipped" in snapshot_portable_merge_overview,
        f"Snapshot portable merge overview missing decision-density stats: {snapshot_portable_merge_overview[:300]}",
    )
    assert_true(
        "Review decisions, then apply merge decisions." in snapshot_portable_merge_guidance,
        f"Snapshot portable merge guidance missing review/apply next action: {snapshot_portable_merge_guidance[:300]}",
    )
    assert_true(
        "Ready to commit resolved portable merge." in snapshot_portable_merge_resolution_guidance,
        f"Snapshot portable merge guidance missing commit next action: {snapshot_portable_merge_resolution_guidance[:300]}",
    )
    assert_true(
        final_status == "Committed portable local outcome three-way merge browser_snapshot_portable_merge_resolution_commit",
        f"Unexpected final snapshot pipeline status: {final_status}",
    )
    assert_true(
        "browser_snapshot_portable_merge_resolution_commit" in merge_commit_result,
        f"Snapshot portable merge result missing final commit: {merge_commit_result[:300]}",
    )
    assert_true(not console_errors, f"Console errors during snapshot-to-portable pipeline check: {console_errors[:5]}")
    assert_true(not page_errors, f"Page errors during snapshot-to-portable pipeline check: {page_errors[:5]}")

    return {
        "final_status": final_status,
        "standalone_package_name": standalone_package["package_name"],
        "autofilled_snapshot_commit": autofilled_snapshot_commit,
        "autofilled_snapshot_package_name": autofilled_snapshot_package_name,
        "autofilled_snapshot_merge_commit": autofilled_snapshot_merge_commit,
        "snapshot_portable_merge_guidance_preview": snapshot_portable_merge_guidance[:200],
        "merge_commit_result_preview": merge_commit_result[:200],
        "local_package_list_preview": local_package_list[:300],
        "screenshot": screenshot,
    }


def main() -> None:
    total = 8
    passed = 0

    if sync_playwright is None:
        print(f"FAILED: playwright unavailable: {PLAYWRIGHT_IMPORT_ERROR}")
        print(f"inspector_browser_ui: passed={passed} failed={total} total={total}")
        raise SystemExit(1)

    server = ThreadingHTTPServer(("127.0.0.1", 0), InspectorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    console_errors: list[str] = []
    page_errors: list[str] = []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1800})
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            check_1 = run_page_load_check(page, base_url, console_errors, page_errors)
            print(f"CHECK page_load OK: {check_1}")
            passed += 1

            console_errors.clear()
            page_errors.clear()
            check_2 = run_analyze_project_check(page, base_url, console_errors, page_errors)
            print(f"CHECK analyze_add_project OK: {check_2}")
            passed += 1

            console_errors.clear()
            page_errors.clear()
            check_3 = run_branch_tag_snapshot_check(page, base_url, console_errors, page_errors)
            print(f"CHECK branch_tag_snapshot OK: {check_3}")
            passed += 1

            console_errors.clear()
            page_errors.clear()
            check_4 = run_profile_preflight_check(page, base_url, console_errors, page_errors)
            print(f"CHECK profile_preflight OK: {check_4}")
            passed += 1

            console_errors.clear()
            page_errors.clear()
            check_5 = run_package_guidance_check(page, base_url, console_errors, page_errors)
            print(f"CHECK package_guidance OK: {check_5}")
            passed += 1

            console_errors.clear()
            page_errors.clear()
            check_6 = run_local_outcome_commit_check(page, base_url, console_errors, page_errors)
            print(f"CHECK local_outcome_commit OK: {check_6}")
            passed += 1

            console_errors.clear()
            page_errors.clear()
            check_7 = run_package_pipeline_check(page, base_url, console_errors, page_errors)
            print(f"CHECK package_pipeline OK: {check_7}")
            passed += 1

            console_errors.clear()
            page_errors.clear()
            check_8 = run_snapshot_to_portable_pipeline_check(page, base_url, console_errors, page_errors)
            print(f"CHECK snapshot_to_portable_pipeline OK: {check_8}")
            passed += 1

            browser.close()
    except Exception as exc:
        print(f"FAILED: inspector browser ui check crashed: {exc}")
        server.shutdown()
        server.server_close()
        print(f"inspector_browser_ui: passed={passed} failed={total - passed} total={total}")
        raise SystemExit(1)
    finally:
        server.shutdown()
        server.server_close()

    print(f"inspector_browser_ui: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
