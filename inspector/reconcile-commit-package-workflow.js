(function () {
  function createReconcileCommitPackageController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      postJson,
      renderResult,
      setStatus,
      refreshProjectUi,
      updateLocalOutcomeSetPackageSelectors,
      renderLocalOutcomeSetPackagePanels,
    } = config;

    function state() {
      return getState();
    }

    function packageGuidance() {
      return window.InspectorPackageGuidance || null;
    }

    function analyzePackageInput() {
      const guidance = packageGuidance();
      if (!guidance) {
        return {
          state: !els.importReconcileCommitPackageJson?.value.trim() ? "empty" : "valid",
          data: null,
          summary: null,
          message: "Package guidance helper is unavailable",
        };
      }
      return guidance.analyzeText(els.importReconcileCommitPackageJson?.value || "", "reconcile_commit_package");
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

    function syncPackageAutofill(analysis) {
      if (analysis.state !== "valid" || !analysis.data) return;
      const packageName = analysis.data.package_name || "standalone_package";
      const branchName = analysis.data.exported_commit?.target_branch_name || "";
      applySuggestedInputValue(els.importReconcileCommitPackageName, `${packageName}_import`);
      applySuggestedSelectValue(els.importReconcileCommitTargetBranch, branchName);
    }

    function syncExportAutofill() {
      const commitName = els.exportReconcileCommitName?.value?.trim() || "";
      if (!commitName) return;
      applySuggestedInputValue(els.exportReconcileCommitPackageName, `${commitName}_package`);
    }

    function syncCommitAutofill() {
      const currentResult = state().currentSnapshotReconcileCommitPackageResult;
      const resolutionName = currentResult?.resolution_name || "";
      if (!resolutionName) return;
      applySuggestedInputValue(els.reconcileCommitPackageCommitName, `${resolutionName}_commit`);
      applySuggestedInputValue(els.reconcileCommitPackagePromotePointName, `${resolutionName}_release`);
    }

    function renderCurrentPackageSummary() {
      if (!els.reconcileCommitPackageCurrentSummary) return;
      const guidance = packageGuidance();
      if (guidance?.renderPayloadSummary) {
        guidance.renderPayloadSummary(
          els.reconcileCommitPackageCurrentSummary,
          state().currentSnapshotReconcileCommitPackage,
          "reconcile_commit_package",
          {
            headline: "Current standalone package payload",
            emptyMessage: "Export a standalone package or load one in this flow to see a structured package summary here.",
            note: "Current standalone package payload. Use current exported package to load it into the import textarea.",
          },
        );
        return;
      }
      els.reconcileCommitPackageCurrentSummary.textContent = state().currentSnapshotReconcileCommitPackage
        ? pretty(state().currentSnapshotReconcileCommitPackage)
        : "No current standalone package payload.";
    }

    function syncPackageGuidance() {
      const guidance = packageGuidance();
      const analysis = analyzePackageInput();
      if (guidance) {
        guidance.renderHint(els.reconcileCommitPackageHint, analysis);
      } else if (els.reconcileCommitPackageHint) {
        els.reconcileCommitPackageHint.textContent = analysis.message || "";
      }
      syncPackageAutofill(analysis);
      return analysis;
    }

    function parsePackageInput() {
      const analysis = syncPackageGuidance();
      if (analysis.state === "empty") {
        setStatus("Standalone package JSON is empty. Paste a standalone promoted outcome package before previewing or importing.");
        return null;
      }
      if (analysis.state === "invalid" || analysis.state === "mismatch" || analysis.state === "unknown") {
        setStatus(analysis.message);
        return null;
      }
      return analysis.data;
    }

    function updateProjectState(data, patch = {}) {
      setState({
        currentProject: data.project_index,
        currentProjectMap: data.workspace_dependency_map || null,
        currentProjectTimeline: data.workspace_timeline || null,
        currentBranchSummary: data.branch_summary || null,
        currentLineageGraph: data.workspace_lineage_graph || null,
        currentTagSummary: data.tag_point_summary || null,
        ...patch,
      });
      if (els.projectJson && data.project_index) {
        els.projectJson.value = pretty(data.project_index);
      }
    }

    function updateSelectors() {
      if (els.exportReconcileCommitName) {
        els.exportReconcileCommitName.innerHTML = "";
        for (const item of (state().currentSnapshotReconcileCommitSummary || [])) {
          const opt = document.createElement("option");
          opt.value = item.commit_name;
          opt.textContent = `${item.commit_name} · ${item.snapshot_name}`;
          els.exportReconcileCommitName.appendChild(opt);
        }
      }
      if (els.importReconcileCommitTargetBranch) {
        els.importReconcileCommitTargetBranch.innerHTML = "";
        for (const item of (state().currentBranchSummary || [])) {
          const opt = document.createElement("option");
          opt.value = item.branch_name;
          opt.textContent = item.branch_name;
          if (item.is_active_branch) opt.selected = true;
          els.importReconcileCommitTargetBranch.appendChild(opt);
        }
      }
      syncExportAutofill();
    }

    function renderDecisionList() {
      if (!els.reconcileCommitPackageDecisionList) return;
      const preview = state().currentSnapshotReconcileCommitPackagePreview;
      if (!preview?.preview_items?.length) {
        els.reconcileCommitPackageDecisionList.innerHTML = '<div class="project-map-empty">No package import decisions</div>';
        return;
      }
      els.reconcileCommitPackageDecisionList.innerHTML = "";
      for (const item of preview.preview_items) {
        const wrap = document.createElement("div");
        wrap.className = "conflict-item";
        const decision = state().currentSnapshotReconcileCommitPackageImportDecisions[item.original_session_id] || { choice: "use_package" };
        wrap.innerHTML = `<strong>${item.original_session_id} · ${item.session_name || ""}</strong><div class="meta">status: ${item.status} · compare: ${item.compare_session_id || "-"} · target: ${item.target_branch_name}</div>`;

        const row = document.createElement("div");
        row.className = "row";
        const select = document.createElement("select");
        for (const choice of ["use_package", "use_current", "skip", "custom_text"]) {
          const opt = document.createElement("option");
          opt.value = choice;
          opt.textContent = choice;
          if (decision.choice === choice) opt.selected = true;
          select.appendChild(opt);
        }

        const customInput = document.createElement("textarea");
        customInput.className = "small";
        customInput.placeholder = "Custom source_text";
        customInput.value = decision.choice === "custom_text" ? (decision.custom_text || "") : "";
        customInput.style.display = decision.choice === "custom_text" ? "block" : "none";

        select.addEventListener("change", () => {
          const decisions = { ...state().currentSnapshotReconcileCommitPackageImportDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = select.value;
          if (select.value !== "custom_text") delete decisions[item.original_session_id].custom_text;
          setState({ currentSnapshotReconcileCommitPackageImportDecisions: decisions });
          customInput.style.display = select.value === "custom_text" ? "block" : "none";
        });

        customInput.addEventListener("input", () => {
          const decisions = { ...state().currentSnapshotReconcileCommitPackageImportDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = "custom_text";
          decisions[item.original_session_id].custom_text = customInput.value;
          setState({ currentSnapshotReconcileCommitPackageImportDecisions: decisions });
        });

        row.appendChild(select);
        row.appendChild(customInput);
        wrap.appendChild(row);
        els.reconcileCommitPackageDecisionList.appendChild(wrap);
      }
    }

    function setDecisionForAll(choice, conflictsOnly = false) {
      const preview = state().currentSnapshotReconcileCommitPackagePreview;
      if (!preview?.preview_items?.length) return;
      const decisions = { ...state().currentSnapshotReconcileCommitPackageImportDecisions };
      for (const item of preview.preview_items) {
        if (conflictsOnly && !item.conflict_like) continue;
        decisions[item.original_session_id] = { choice };
      }
      setState({ currentSnapshotReconcileCommitPackageImportDecisions: decisions });
      renderDecisionList();
    }

    async function applyDecisions() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const pkg = parsePackageInput();
      if (!pkg) return;

      try {
        const data = await postJson("/api/resolve-snapshot-reconcile-commit-package-import", {
          current_project_index: currentProject,
          package: pkg,
          decisions: state().currentSnapshotReconcileCommitPackageImportDecisions,
          resolution_name: els.importReconcileCommitPackageName?.value.trim() || undefined,
          target_branch_name: els.importReconcileCommitTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedReconcileCommit?.checked,
        });
        updateProjectState(data, {
          currentSnapshotReconcileCommitSummary: data.snapshot_reconcile_commit_summary || null,
          currentSnapshotReconcileCommitPackageSummary: data.snapshot_reconcile_commit_package_summary || null,
          currentSnapshotReconcileCommitPackageImportSummary: data.snapshot_reconcile_commit_package_import_summary || null,
          currentSnapshotReconcileCommitPackageResolutionSummary: data.snapshot_reconcile_commit_package_resolution_summary || null,
          currentSnapshotReconcileCommitPackagePreview: null,
          currentSnapshotReconcileCommitPackageResult: data.snapshot_reconcile_commit_package_resolution_result || null,
          currentSnapshotReconcileCommitPackage: pkg,
        });
        refreshProjectUi();
        renderList();
        renderPreview();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        setStatus(`Resolved standalone package import ${data.snapshot_reconcile_commit_package_resolution_result?.resolution_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package resolution failed: ${err.message}`);
      }
    }

    function renderPreview() {
      if (!els.reconcileCommitPackagePreviewText) return;
      const preview = state().currentSnapshotReconcileCommitPackagePreview;
      els.reconcileCommitPackagePreviewText.textContent = preview ? pretty(preview) : "";
      renderDecisionList();
    }

    async function commitResolution() {
      const currentProject = state().currentProject;
      const currentResult = state().currentSnapshotReconcileCommitPackageResult;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      if (!currentResult?.resolved_session_ids) {
        setStatus("No resolved package import result to commit");
        return;
      }

      try {
        const data = await postJson("/api/commit-snapshot-reconcile-commit-package-resolution", {
          project_index: currentProject,
          snapshot_reconcile_commit_package_resolution_result: currentResult,
          commit_name: els.reconcileCommitPackageCommitName?.value.trim() || undefined,
          promote_point_name: els.reconcileCommitPackagePromotePointName?.value.trim() || undefined,
          promote_point_kind: els.reconcileCommitPackagePromotePointKind?.value || "release",
          note: els.reconcileCommitPackageCommitNote?.value.trim() || undefined,
        });
        updateProjectState(data, {
          currentSnapshotReconcileCommitSummary: data.snapshot_reconcile_commit_summary || null,
          currentSnapshotReconcileCommitPackageSummary: data.snapshot_reconcile_commit_package_summary || null,
          currentSnapshotReconcileCommitPackageImportSummary: data.snapshot_reconcile_commit_package_import_summary || null,
          currentSnapshotReconcileCommitPackageResolutionSummary: data.snapshot_reconcile_commit_package_resolution_summary || null,
          currentSnapshotReconcileCommitPackageCommitSummary: data.snapshot_reconcile_commit_package_commit_summary || null,
          currentSnapshotReconcileCommitPackageResult: data.snapshot_reconcile_commit_package_commit_result || null,
        });
        refreshProjectUi();
        renderList();
        renderPreview();
        renderDecisionList();
        renderResultPanel();
        renderResult(data);
        setStatus(`Committed imported package resolution ${state().currentSnapshotReconcileCommitPackageResult?.commit_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package commit failed: ${err.message}`);
      }
    }

    function renderList() {
      if (!els.reconcileCommitPackageList) return;
      els.reconcileCommitPackageList.innerHTML = "";
      const commitItems = (state().currentSnapshotReconcileCommitPackageCommitSummary?.length
        ? state().currentSnapshotReconcileCommitPackageCommitSummary
        : Object.values(state().currentProject?.snapshot_reconcile_commit_package_commits || {}));
      for (const item of (state().currentSnapshotReconcileCommitPackageSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.package_name}</strong><div class="meta">${item.commit_name} · ${item.snapshot_name} · resolved:${item.resolved_session_count}${item.promoted_point_name ? ` · promoted:${item.promoted_point_kind}:${item.promoted_point_name}` : ""}</div>`;
        els.reconcileCommitPackageList.appendChild(wrap);
      }
      for (const item of (state().currentSnapshotReconcileCommitPackageImportSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.import_name}</strong><div class="meta">package:${item.package_name} · imported commit:${item.imported_commit_name} · branch:${item.target_branch_name} · imported:${item.imported_session_count}</div>`;
        els.reconcileCommitPackageList.appendChild(wrap);
      }
      for (const item of (state().currentSnapshotReconcileCommitPackageResolutionSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.resolution_name}</strong><div class="meta">package:${item.package_name} · source commit:${item.source_commit_name} · branch:${item.target_branch_name} · resolved:${item.resolved_session_count} · skipped:${item.skipped_session_count}</div>`;
        els.reconcileCommitPackageList.appendChild(wrap);
      }
      for (const item of commitItems) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.commit_name}</strong><div class="meta">resolution:${item.resolution_name} · package:${item.package_name} · branch:${item.target_branch_name} · resolved:${item.resolved_session_count}${item.promoted_point_name ? ` · promoted:${item.promoted_point_kind}:${item.promoted_point_name}` : ""}</div>`;
        els.reconcileCommitPackageList.appendChild(wrap);
      }
      updateLocalOutcomeSetPackageSelectors();
    }

    function renderResultPanel() {
      if (!els.reconcileCommitPackageResultText) return;
      const currentPackage = state().currentSnapshotReconcileCommitPackage;
      const currentResult = state().currentSnapshotReconcileCommitPackageResult;
      if (currentPackage) {
        els.reconcileCommitPackageResultText.textContent = pretty(currentPackage);
      } else if (currentResult) {
        els.reconcileCommitPackageResultText.textContent = pretty(currentResult);
      } else {
        els.reconcileCommitPackageResultText.textContent = "";
      }
      renderCurrentPackageSummary();
      syncCommitAutofill();
    }

    async function exportPackage() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const commitName = els.exportReconcileCommitName?.value;
      if (!commitName) {
        setStatus("No reconcile commit selected");
        return;
      }

      try {
        const data = await postJson("/api/export-snapshot-reconcile-commit-package", {
          project_index: currentProject,
          commit_name: commitName,
          package_name: els.exportReconcileCommitPackageName?.value.trim() || undefined,
          note: "standalone promoted outcome package",
        });
        updateProjectState(data, {
          currentSnapshotReconcileCommitSummary: data.snapshot_reconcile_commit_summary || null,
          currentSnapshotReconcileCommitPackageSummary: data.snapshot_reconcile_commit_package_summary || null,
          currentSnapshotReconcileCommitPackageImportSummary: data.snapshot_reconcile_commit_package_import_summary || null,
          currentSnapshotReconcileCommitPackageResolutionSummary: data.snapshot_reconcile_commit_package_resolution_summary || null,
          currentSnapshotReconcileCommitPackageImportDecisions: {},
          currentSnapshotReconcileCommitPackagePreview: null,
          currentSnapshotReconcileCommitPackageResult: data.snapshot_reconcile_commit_package_result || null,
          currentSnapshotReconcileCommitPackage: data.snapshot_reconcile_commit_package || null,
        });
        renderList();
        renderPreview();
        renderResultPanel();
        updateSelectors();
        setStatus(`Exported standalone package ${state().currentSnapshotReconcileCommitPackageResult?.package_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package export failed: ${err.message}`);
      }
    }

    function useCurrentPackage() {
      if (!els.importReconcileCommitPackageJson) return;
      const currentPackage = state().currentSnapshotReconcileCommitPackage;
      els.importReconcileCommitPackageJson.value = currentPackage ? pretty(currentPackage) : "";
      syncPackageGuidance();
      setStatus(currentPackage ? "Loaded current standalone package" : "No exported standalone package");
    }

    function clearInput() {
      if (els.importReconcileCommitPackageJson) els.importReconcileCommitPackageJson.value = "";
      if (els.importReconcileCommitPackageName) els.importReconcileCommitPackageName.value = "";
      setState({
        currentSnapshotReconcileCommitPackagePreview: null,
        currentSnapshotReconcileCommitPackageResult: null,
        currentSnapshotReconcileCommitPackage: null,
        currentLocalOutcomeSetPackageSummary: null,
        currentLocalOutcomeSetPackageImportSummary: null,
        currentLocalOutcomeSetPackageResolutionSummary: null,
        currentLocalOutcomeSetPackage: null,
        currentLocalOutcomeSetPackagePreviewResult: null,
        currentLocalOutcomeSetPackageImportDecisions: {},
        currentLocalOutcomeSetPackageResult: null,
      });
      renderPreview();
      renderResultPanel();
      renderLocalOutcomeSetPackagePanels();
      syncPackageGuidance();
      setStatus("Cleared standalone package input");
    }

    async function previewImport() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const pkg = parsePackageInput();
      if (!pkg) return;

      try {
        const data = await postJson("/api/preview-snapshot-reconcile-commit-package-import", {
          current_project_index: currentProject,
          package: pkg,
          import_name: els.importReconcileCommitPackageName?.value.trim() || undefined,
          target_branch_name: els.importReconcileCommitTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedReconcileCommit?.checked,
        });
        setState({
          currentSnapshotReconcileCommitPackageImportDecisions: {},
          currentSnapshotReconcileCommitPackagePreview: data,
        });
        renderPreview();
        setStatus(`Previewed standalone package compatibility ${data.package_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package preview failed: ${err.message}`);
      }
    }

    async function importPackage() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const pkg = parsePackageInput();
      if (!pkg) return;

      try {
        const data = await postJson("/api/import-snapshot-reconcile-commit-package", {
          current_project_index: currentProject,
          package: pkg,
          import_name: els.importReconcileCommitPackageName?.value.trim() || undefined,
          target_branch_name: els.importReconcileCommitTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedReconcileCommit?.checked,
        });
        updateProjectState(data, {
          currentSnapshotReconcileCommitSummary: data.snapshot_reconcile_commit_summary || null,
          currentSnapshotReconcileCommitPackageSummary: data.snapshot_reconcile_commit_package_summary || null,
          currentSnapshotReconcileCommitPackageImportSummary: data.snapshot_reconcile_commit_package_import_summary || null,
          currentSnapshotReconcileCommitPackageResolutionSummary: data.snapshot_reconcile_commit_package_resolution_summary || null,
          currentSnapshotReconcileCommitPackageImportDecisions: {},
          currentSnapshotReconcileCommitPackagePreview: null,
          currentSnapshotReconcileCommitPackageResult: data.snapshot_reconcile_commit_package_import_result || null,
          currentSnapshotReconcileCommitPackage: pkg,
        });
        refreshProjectUi();
        renderList();
        renderPreview();
        renderResultPanel();
        updateSelectors();
        setStatus(`Imported standalone package ${data.snapshot_reconcile_commit_package_import_result?.import_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package import failed: ${err.message}`);
      }
    }

    return {
      updateSelectors,
      renderDecisionList,
      setDecisionForAll,
      applyDecisions,
      renderPreview,
      commitResolution,
      renderList,
      renderResultPanel,
      exportPackage,
      useCurrentPackage,
      clearInput,
      previewImport,
      importPackage,
      syncPackageGuidance,
      syncExportAutofill,
      syncCommitAutofill,
      renderCurrentPackageSummary,
    };
  }

  window.ReconcileCommitPackageWorkflow = {
    createReconcileCommitPackageController,
  };
})();
