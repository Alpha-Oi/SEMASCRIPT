(function () {
  function createProjectLifecycleController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      parseCsvList,
      postJson,
      renderResult,
      setStatus,
      refreshProjectHydratedPanels,
      downloadBlob,
    } = config;

    function state() {
      return getState();
    }

    function snapshotGuidance() {
      return window.InspectorPackageGuidance || null;
    }

    function analyzeSnapshotPackageInput() {
      const guidance = snapshotGuidance();
      if (!guidance) {
        return {
          state: !els.snapshotRestoreJson?.value.trim() ? "empty" : "valid",
          data: null,
          summary: null,
          message: "Snapshot guidance helper is unavailable",
        };
      }
      return guidance.analyzeText(els.snapshotRestoreJson?.value || "", "snapshot");
    }

    function applySuggestedInputValue(element, nextValue) {
      if (!element || !nextValue) return;
      const normalized = String(nextValue).trim();
      if (!normalized) return;
      const current = (element.value || "").trim();
      const previous = element.dataset.autofillValue || "";
      if (!current || current === previous) {
        element.value = normalized;
        element.dataset.autofillValue = normalized;
      }
    }

    function applySuggestedSelectValue(element, nextValue) {
      if (!element || !nextValue) return;
      const normalized = String(nextValue).trim();
      if (!normalized) return;
      const options = Array.from(element.options || []);
      if (!options.some((item) => item.value === normalized)) return;
      const current = element.value || "";
      const previous = element.dataset.autofillValue || "";
      if (!current || current === previous || !options.some((item) => item.value === current)) {
        element.value = normalized;
        element.dataset.autofillValue = normalized;
      }
    }

    function syncSnapshotAutofill(analysis) {
      if (analysis.state !== "valid" || !analysis.data) return;
      const snapshotName = analysis.data.snapshot_name || "snapshot_package";
      const branchName =
        analysis.data.anchor?.branch_name ||
        analysis.data.export_state?.active_branch_name ||
        analysis.data.export_state?.branch_summary?.[0]?.branch_name ||
        "";
      applySuggestedInputValue(els.restoredProjectName, `restored_${snapshotName}`);
      applySuggestedInputValue(els.snapshotRestoreName, `${snapshotName}_restore`);
      applySuggestedInputValue(els.partialImportName, `${snapshotName}_partial_import`);
      applySuggestedInputValue(els.snapshotReconcileName, `${snapshotName}_reconcile`);
      applySuggestedSelectValue(els.partialImportTargetBranch, branchName);
      applySuggestedSelectValue(els.snapshotReconcileTargetBranch, branchName);
    }

    function renderPartialImportSelectionHint(analysis = analyzeSnapshotPackageInput()) {
      if (!els.partialImportSelectionHint) return;
      const guidance = snapshotGuidance();
      if (analysis.state !== "valid") {
        els.partialImportSelectionHint.textContent = "Load a snapshot package first. Then you can pick session ids, tag points, and snapshot names from that package.";
        return;
      }
      const sessionText = guidance ? guidance.formatListPreview(analysis.summary?.availableSessionIds) : "none";
      const tagText = guidance ? guidance.formatListPreview(analysis.summary?.availableTagNames) : "none";
      const snapshotText = guidance ? guidance.formatListPreview(analysis.summary?.availableSnapshotNames) : "none";
      els.partialImportSelectionHint.textContent = `Available snapshot selections: sessions ${sessionText}; tag points ${tagText}; snapshot names ${snapshotText}.`;
    }

    function syncSnapshotPackageGuidance() {
      const guidance = snapshotGuidance();
      const analysis = analyzeSnapshotPackageInput();
      if (guidance) {
        guidance.renderHint(els.snapshotPackageHint, analysis);
      } else if (els.snapshotPackageHint) {
        els.snapshotPackageHint.textContent = analysis.message || "";
      }
      syncSnapshotAutofill(analysis);
      renderPartialImportSelectionHint(analysis);
      return analysis;
    }

    function parseSnapshotPackageInput() {
      const analysis = syncSnapshotPackageGuidance();
      if (analysis.state === "empty") {
        setStatus("Snapshot package JSON is empty. Paste a snapshot export package to restore, partially import, or reconcile.");
        return null;
      }
      if (analysis.state === "invalid" || analysis.state === "mismatch" || analysis.state === "unknown") {
        setStatus(analysis.message);
        return null;
      }
      return analysis.data;
    }

    function validateSnapshotSelections(selectionLabel, selectedValues, availableValues) {
      const chosen = parseCsvList(selectedValues || "");
      if (!chosen.length) return true;
      const available = new Set(availableValues || []);
      if (!available.size) return true;
      const unknown = chosen.filter((value) => !available.has(value));
      if (!unknown.length) return true;
      const guidance = snapshotGuidance();
      const preview = guidance ? guidance.formatListPreview(availableValues) : "none";
      setStatus(`${selectionLabel} reference unknown snapshot values: ${unknown.join(", ")}. Available: ${preview}.`);
      return false;
    }

    function validatePartialImportSelections(snapshotAnalysis) {
      const summary = snapshotAnalysis?.summary || {};
      if (!validateSnapshotSelections("Partial import session ids", els.partialImportSessionIds?.value || "", summary.availableSessionIds || [])) {
        return false;
      }
      if (!validateSnapshotSelections("Partial import tag names", els.partialImportTagNames?.value || "", summary.availableTagNames || [])) {
        return false;
      }
      if (!validateSnapshotSelections("Partial import snapshot names", els.partialImportSnapshotNames?.value || "", summary.availableSnapshotNames || [])) {
        return false;
      }
      return true;
    }

    function updateTagTargetSessions() {
      if (!els.tagTargetSession) return;
      els.tagTargetSession.innerHTML = "";
      for (const item of (state().currentProject?.sessions || [])) {
        const opt = document.createElement("option");
        opt.value = item.session_id;
        opt.textContent = `${item.session_id} · ${item.session_name}`;
        els.tagTargetSession.appendChild(opt);
      }
      if (state().currentProject?.active_session_id) {
        els.tagTargetSession.value = state().currentProject.active_session_id;
      }
    }

    function renderPartialImportResult() {
      if (!els.partialImportResultText) return;
      els.partialImportResultText.textContent = state().currentPartialSnapshotImportResult ? pretty(state().currentPartialSnapshotImportResult) : "";
    }

    function useCurrentSnapshotForPartialImport() {
      if (!els.snapshotRestoreJson) return;
      els.snapshotRestoreJson.value = state().currentSnapshotPackage ? pretty(state().currentSnapshotPackage) : "";
      syncSnapshotPackageGuidance();
      setStatus(state().currentSnapshotPackage ? "Loaded current snapshot package for partial import" : "No current snapshot package");
    }

    function clearPartialImportInput() {
      if (els.partialImportSessionIds) els.partialImportSessionIds.value = "";
      if (els.partialImportTagNames) els.partialImportTagNames.value = "";
      if (els.partialImportSnapshotNames) els.partialImportSnapshotNames.value = "";
      if (els.partialImportTargetBranch) els.partialImportTargetBranch.value = "";
      if (els.partialImportName) els.partialImportName.value = "";
      setState({ currentPartialSnapshotImportResult: null });
      renderPartialImportResult();
      renderPartialImportSelectionHint();
      setStatus("Cleared partial import input");
    }

    async function partialImportFromSnapshot() {
      if (!state().currentProject) {
        setStatus("No current project loaded");
        return;
      }
      const snapshotAnalysis = syncSnapshotPackageGuidance();
      const snapshotPackage = parseSnapshotPackageInput();
      if (!snapshotPackage) return;
      if (!validatePartialImportSelections(snapshotAnalysis)) return;

      try {
        const data = await postJson("/api/partial-import-project-from-snapshot", {
          current_project_index: state().currentProject,
          snapshot_package: snapshotPackage,
          import_name: els.partialImportName?.value.trim() || undefined,
          selected_session_ids: parseCsvList(els.partialImportSessionIds?.value || ""),
          selected_tag_point_names: parseCsvList(els.partialImportTagNames?.value || ""),
          selected_snapshot_export_names: parseCsvList(els.partialImportSnapshotNames?.value || ""),
          target_branch_name: els.partialImportTargetBranch?.value.trim() || undefined,
          activate_last_imported: !!els.activatePartialImportHead?.checked,
        });
        renderResult(data);
        setStatus(`Applied partial snapshot import ${data.partial_snapshot_import_result?.import_name || ""}`);
      } catch (err) {
        setStatus(`Partial snapshot import failed: ${err.message}`);
      }
    }

    function renderSnapshotRestorePreview() {
      if (!els.snapshotRestorePreviewText) return;
      els.snapshotRestorePreviewText.textContent = state().currentSnapshotRestorePreview ? pretty(state().currentSnapshotRestorePreview) : "";
    }

    async function previewSnapshotRestoreBeforeApply() {
      if (!state().currentProject) {
        setStatus("No current project loaded for diff preview");
        return;
      }
      const snapshotPackage = parseSnapshotPackageInput();
      if (!snapshotPackage) return;

      try {
        const data = await postJson("/api/preview-project-snapshot-restore", {
          current_project_index: state().currentProject,
          snapshot_package: snapshotPackage,
          restored_project_name: els.restoredProjectName?.value.trim() || undefined,
          activate_anchor: !!els.activateRestoredAnchor?.checked,
        });
        setState({ currentSnapshotRestorePreview: data });
        renderSnapshotRestorePreview();
        setStatus(`Previewed restore diff for ${data.snapshot_name || "snapshot"}`);
      } catch (err) {
        setStatus(`Snapshot restore preview failed: ${err.message}`);
      }
    }

    function renderSnapshotRestoreResult() {
      if (!els.snapshotRestoreResultText) return;
      els.snapshotRestoreResultText.textContent = state().currentSnapshotRestoreResult ? pretty(state().currentSnapshotRestoreResult) : "";
    }

    function useCurrentSnapshotForRestore() {
      if (!els.snapshotRestoreJson) return;
      els.snapshotRestoreJson.value = state().currentSnapshotPackage ? pretty(state().currentSnapshotPackage) : "";
      syncSnapshotPackageGuidance();
      setStatus(state().currentSnapshotPackage ? "Loaded current snapshot package into restore input" : "No current snapshot package");
    }

    function clearSnapshotRestoreInput() {
      if (els.snapshotRestoreJson) els.snapshotRestoreJson.value = "";
      if (els.restoredProjectName) els.restoredProjectName.value = "";
      if (els.snapshotRestoreName) els.snapshotRestoreName.value = "";
      setState({
        currentSnapshotRestorePreview: null,
        currentSnapshotRestoreResult: null,
      });
      renderSnapshotRestorePreview();
      renderSnapshotRestoreResult();
      renderPartialImportResult();
      syncSnapshotPackageGuidance();
      setStatus("Cleared snapshot restore input");
    }

    async function restoreWorkspaceFromSnapshot() {
      const snapshotPackage = parseSnapshotPackageInput();
      if (!snapshotPackage) return;

      try {
        const data = await postJson("/api/restore-project-from-snapshot-export", {
          snapshot_package: snapshotPackage,
          restored_project_name: els.restoredProjectName?.value.trim() || undefined,
          restore_name: els.snapshotRestoreName?.value.trim() || undefined,
          activate_anchor: !!els.activateRestoredAnchor?.checked,
        });
        setState({
          currentSnapshotRestorePreview: null,
          currentSnapshotRestoreResult: null,
          currentSnapshotResult: null,
          currentSnapshotPackage: snapshotPackage,
        });
        renderResult(data);
        setStatus(`Restored workspace from snapshot ${data.snapshot_restore_result?.snapshot_name || ""}`);
      } catch (err) {
        setStatus(`Snapshot restore failed: ${err.message}`);
      }
    }

    function updateSnapshotSelectors() {
      if (!els.snapshotSourcePoint) return;
      els.snapshotSourcePoint.innerHTML = "";
      for (const point of (state().currentTagSummary || [])) {
        const opt = document.createElement("option");
        opt.value = point.tag_name;
        opt.textContent = `${point.tag_name} · ${point.point_kind} · ${point.target_session_id}`;
        els.snapshotSourcePoint.appendChild(opt);
      }
    }

    function renderSnapshotList() {
      if (!els.snapshotList) return;
      els.snapshotList.innerHTML = "";
      for (const snap of (state().currentSnapshotSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${snap.snapshot_name}</strong><div class="meta">${snap.source_point_kind} · ${snap.source_point_name} · ${snap.target_session_id}</div><div class="meta">${snap.note || ""}</div>`;
        els.snapshotList.appendChild(wrap);
      }
    }

    function renderSnapshotResult() {
      if (!els.snapshotResultText) return;
      els.snapshotResultText.textContent = state().currentSnapshotPackage ? pretty(state().currentSnapshotPackage) : (state().currentSnapshotResult ? pretty(state().currentSnapshotResult) : "");
    }

    async function createSnapshotExport() {
      if (!state().currentProject) {
        setStatus("No project loaded");
        return;
      }
      const sourcePointName = els.snapshotSourcePoint?.value;
      const snapshotName = (els.snapshotName?.value || "").trim();
      const note = (els.snapshotNote?.value || "").trim();
      if (!sourcePointName) {
        setStatus("Source tag/release point is missing");
        return;
      }

      try {
        const data = await postJson("/api/create-project-snapshot-export", {
          project_index: state().currentProject,
          source_point_name: sourcePointName,
          snapshot_name: snapshotName || undefined,
          note: note || undefined,
        });
        renderResult(data);
        setStatus(`Created snapshot export ${data.snapshot_export_result?.snapshot_name || snapshotName || sourcePointName}`);
      } catch (err) {
        setStatus(`Snapshot export failed: ${err.message}`);
      }
    }

    function downloadCurrentSnapshot() {
      if (!state().currentSnapshotPackage) {
        setStatus("No snapshot package to download");
        return;
      }
      const safeName = (state().currentSnapshotPackage.snapshot_name || "snapshot").replace(/[^a-z0-9_-]+/gi, "_");
      downloadBlob(pretty(state().currentSnapshotPackage), `${safeName}.json`);
      setStatus("Snapshot downloaded");
    }

    function renderTagPointList() {
      if (!els.tagPointList) return;
      els.tagPointList.innerHTML = "";
      for (const point of (state().currentTagSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "tag-point-item";
        wrap.innerHTML = `<strong>${point.tag_name}</strong><div class="meta">${point.point_kind} · ${point.target_session_id} · ${point.branch_name || "-"}</div><div class="meta">${point.note || ""}</div>`;
        els.tagPointList.appendChild(wrap);
      }
    }

    function renderTagPointResult() {
      if (!els.tagPointResultText) return;
      els.tagPointResultText.textContent = state().currentTagPointResult ? pretty(state().currentTagPointResult) : "";
    }

    async function createTagReleasePoint() {
      if (!state().currentProject) {
        setStatus("No project loaded");
        return;
      }
      const tagName = (els.tagPointName?.value || "").trim();
      const targetSessionId = els.tagTargetSession?.value;
      const pointKind = els.tagPointKind?.value || "tag";
      const note = (els.tagPointNote?.value || "").trim();
      if (!tagName || !targetSessionId) {
        setStatus("Tag/release name or target session missing");
        return;
      }

      try {
        const data = await postJson("/api/create-project-tag-release-point", {
          project_index: state().currentProject,
          tag_name: tagName,
          target_session_id: targetSessionId,
          point_kind: pointKind,
          note: note || undefined,
        });
        renderResult(data);
        setStatus(`Created ${pointKind} point ${tagName}`);
      } catch (err) {
        setStatus(`Tag/release failed: ${err.message}`);
      }
    }

    async function createBranchFromActiveSession() {
      if (!state().currentProject) {
        setStatus("No project loaded");
        return;
      }
      const branchName = (els.newBranchName?.value || "").trim();
      if (!branchName) {
        setStatus("Branch name is empty");
        return;
      }
      const sourceSessionId = state().currentProject.active_session_id;
      if (!sourceSessionId) {
        setStatus("No active session to branch from");
        return;
      }

      try {
        const data = await postJson("/api/create-project-branch", {
          project_index: state().currentProject,
          source_session_id: sourceSessionId,
          branch_name: branchName,
        });
        renderResult(data);
        setStatus(`Created branch ${branchName}`);
      } catch (err) {
        setStatus(`Create branch failed: ${err.message}`);
      }
    }

    function clearProject() {
      setState({
        currentProject: null,
        currentProjectMap: null,
        currentProjectTimeline: null,
        currentBranchSummary: null,
        currentLineageGraph: null,
        currentBranchRebaseResult: null,
        currentBranchResetResult: null,
        currentTagSummary: null,
        currentTagPointResult: null,
        currentSnapshotSummary: null,
        currentSnapshotResult: null,
        currentSnapshotPackage: null,
        currentSnapshotRestoreSummary: null,
        currentSnapshotRestorePreview: null,
        currentSnapshotRestoreResult: null,
        currentPartialSnapshotImportSummary: null,
        currentPartialSnapshotImportResult: null,
        currentSnapshotReconcileSummary: null,
        currentSnapshotReconcilePreview: null,
        currentSnapshotReconcileResult: null,
        currentSnapshotReconcileCommitSummary: null,
        currentSnapshotReconcileCommitResult: null,
        currentSnapshotReconcileCommitCompareResult: null,
        currentSnapshotReconcileCommitPackageSummary: null,
        currentSnapshotReconcileCommitPackageImportSummary: null,
        currentSnapshotReconcileCommitPackagePreview: null,
        currentSnapshotReconcileCommitPackageResolutionSummary: null,
        currentSnapshotReconcileCommitPackageCommitSummary: null,
        currentSnapshotReconcileCommitPackageResult: null,
        currentSnapshotReconcileCommitPackage: null,
        currentLocalOutcomeSetPackageSummary: null,
        currentLocalOutcomeSetPackageImportSummary: null,
        currentLocalOutcomeSetPackageResolutionSummary: null,
        currentLocalOutcomeSetPackage: null,
        currentLocalOutcomeSetPackagePreviewResult: null,
        currentLocalOutcomeSetPackageImportDecisions: {},
        currentLocalOutcomeSetPackageResult: null,
        currentPortableLocalOutcomeThreeWayMergeResult: null,
        currentPortableLocalOutcomeMergeDecisions: {},
        currentPortableLocalOutcomeMergeResolutionSummary: null,
        currentPortableLocalOutcomeMergeResolutionResult: null,
        currentPortableLocalOutcomeMergeCommitResult: null,
        selectedPortableLocalOutcomeMergeItemId: null,
        currentCompareResult: null,
        currentMergeResult: null,
        currentResolvedMergeResult: null,
        currentConflictDecisions: {},
        currentMergeCommitResult: null,
        currentBranchCherryPickResult: null,
        currentBranchSquashResult: null,
      });
      if (els.projectJson) els.projectJson.value = "";
      if (els.projectName) els.projectName.value = "";
      refreshProjectHydratedPanels();
      setStatus("Project cleared");
    }

    async function exportProject() {
      const currentProject = state().currentProject;
      if (!currentProject || !currentProject.sessions?.length) {
        setStatus("Project has no sessions");
        return;
      }

      try {
        const data = await postJson("/api/export-project-index", {
          sessions: currentProject.sessions,
          project_name: els.projectName?.value.trim() || currentProject.project_name || "Untitled SEMASCRIPT Project",
          active_session_id: currentProject.active_session_id,
        });
        setState({ currentProject: data });
        if (els.projectJson) els.projectJson.value = pretty(data);
        if (els.projectName && data.project_name) els.projectName.value = data.project_name;
        refreshProjectHydratedPanels();
        setStatus("Project index exported");
      } catch (err) {
        setStatus(`Project export failed: ${err.message}`);
      }
    }

    async function importProject() {
      const raw = els.projectJson?.value.trim();
      if (!raw) {
        setStatus("Project JSON is empty");
        return;
      }

      try {
        const project = JSON.parse(raw);
        const data = await postJson("/api/import-project-index", { project_index: project });
        renderResult(data);
        setStatus("Project imported");
      } catch (err) {
        setStatus(`Project import failed: ${err.message}`);
      }
    }

    function downloadProject() {
      const raw = els.projectJson?.value.trim();
      if (!raw) {
        setStatus("No project JSON to download");
        return;
      }
      const safeName = (els.projectName?.value.trim() || "semascript_project").replace(/[^a-z0-9_-]+/gi, "_");
      downloadBlob(raw, `${safeName}.json`);
      setStatus("Project downloaded");
    }

    return {
      updateTagTargetSessions,
      renderPartialImportResult,
      useCurrentSnapshotForPartialImport,
      clearPartialImportInput,
      partialImportFromSnapshot,
      renderSnapshotRestorePreview,
      previewSnapshotRestoreBeforeApply,
      renderSnapshotRestoreResult,
      useCurrentSnapshotForRestore,
      clearSnapshotRestoreInput,
      restoreWorkspaceFromSnapshot,
      updateSnapshotSelectors,
      renderSnapshotList,
      renderSnapshotResult,
      createSnapshotExport,
      downloadCurrentSnapshot,
      renderTagPointList,
      renderTagPointResult,
      createTagReleasePoint,
      createBranchFromActiveSession,
      clearProject,
      exportProject,
      importProject,
      downloadProject,
      syncSnapshotPackageGuidance,
    };
  }

  window.ProjectLifecycleWorkflow = {
    createProjectLifecycleController,
  };
})();
