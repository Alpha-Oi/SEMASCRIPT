(function () {
  function createLocalOutcomeSetPackageController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      postJson,
      renderResult,
      setStatus,
      updatePortableLocalOutcomeMergeSelectors,
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
          state: !els.importLocalOutcomeSetPackageJson?.value.trim() ? "empty" : "valid",
          data: null,
          summary: null,
          message: "Package guidance helper is unavailable",
        };
      }
      return guidance.analyzeText(els.importLocalOutcomeSetPackageJson?.value || "", "local_outcome_set_package");
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
      const packageName = analysis.data.package_name || "local_outcome_package";
      const branchName = analysis.data.exported_local_outcome_commit?.target_branch_name || "";
      applySuggestedInputValue(els.importLocalOutcomeSetPackageNameInput, `${packageName}_import`);
      applySuggestedSelectValue(els.importLocalOutcomeSetTargetBranch, branchName);
    }

    function syncExportAutofill() {
      const commitName = els.exportLocalOutcomeSetCommit?.value?.trim() || "";
      if (!commitName) return;
      applySuggestedInputValue(els.localOutcomeSetPackageName, `${commitName}_package`);
    }

    function syncPackageGuidance() {
      const guidance = packageGuidance();
      const analysis = analyzePackageInput();
      if (guidance) {
        guidance.renderHint(els.localOutcomeSetPackageHint, analysis);
      } else if (els.localOutcomeSetPackageHint) {
        els.localOutcomeSetPackageHint.textContent = analysis.message || "";
      }
      syncPackageAutofill(analysis);
      return analysis;
    }

    function syncCommitAutofill() {
      const result = state().currentLocalOutcomeSetPackageResult;
      const resolutionName = result?.resolution_name || "";
      if (!resolutionName) return;
      applySuggestedInputValue(els.localOutcomeSetPackageCommitName, `${resolutionName}_commit`);
      applySuggestedInputValue(els.localOutcomeSetPackagePromotePointName, `${resolutionName}_release`);
    }

    function renderCurrentPackageSummary() {
      if (!els.localOutcomeSetPackageCurrentSummary) return;
      const guidance = packageGuidance();
      if (guidance?.renderPayloadSummary) {
        guidance.renderPayloadSummary(
          els.localOutcomeSetPackageCurrentSummary,
          state().currentLocalOutcomeSetPackage,
          "local_outcome_set_package",
          {
            headline: "Current local outcome package payload",
            emptyMessage: "Export a local outcome package or load one in this flow to see a structured package summary here.",
            note: "Current local outcome package payload. Use current local package to load it into the import textarea.",
          },
        );
        return;
      }
      els.localOutcomeSetPackageCurrentSummary.textContent = state().currentLocalOutcomeSetPackage
        ? pretty(state().currentLocalOutcomeSetPackage)
        : "No current local outcome package payload.";
    }

    function parsePackageInput() {
      const analysis = syncPackageGuidance();
      if (analysis.state === "empty") {
        setStatus("Local outcome package JSON is empty. Paste a portable local outcome package before previewing or importing.");
        return null;
      }
      if (analysis.state === "invalid" || analysis.state === "mismatch" || analysis.state === "unknown") {
        setStatus(analysis.message);
        return null;
      }
      return analysis.data;
    }

    function updateSelectors() {
      if (!els.exportLocalOutcomeSetCommit || !els.importLocalOutcomeSetTargetBranch) return;

      const commitItems = (state().currentSnapshotReconcileCommitPackageCommitSummary?.length
        ? state().currentSnapshotReconcileCommitPackageCommitSummary
        : Object.values(state().currentProject?.snapshot_reconcile_commit_package_commits || {}));

      els.exportLocalOutcomeSetCommit.innerHTML = "";
      for (const item of commitItems) {
        const opt = document.createElement("option");
        opt.value = item.commit_name;
        opt.textContent = item.commit_name;
        els.exportLocalOutcomeSetCommit.appendChild(opt);
      }
      if (els.exportLocalOutcomeSetCommit.options.length && !els.exportLocalOutcomeSetCommit.value) {
        els.exportLocalOutcomeSetCommit.value = els.exportLocalOutcomeSetCommit.options[0].value;
      }

      els.importLocalOutcomeSetTargetBranch.innerHTML = "";
      for (const item of (state().currentBranchSummary || [])) {
        const opt = document.createElement("option");
        opt.value = item.branch_name;
        opt.textContent = item.branch_name;
        if (item.is_active_branch) opt.selected = true;
        els.importLocalOutcomeSetTargetBranch.appendChild(opt);
      }
      syncExportAutofill();
    }

    function renderList() {
      if (!els.localOutcomeSetPackageList) return;
      els.localOutcomeSetPackageList.innerHTML = "";

      for (const item of (state().currentLocalOutcomeSetPackageSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.package_name}</strong><div class="meta">${item.commit_name} · ${item.package_kind} · resolved:${item.resolved_session_count}${item.promoted_point_name ? ` · promoted:${item.promoted_point_kind}:${item.promoted_point_name}` : ""}</div>`;
        els.localOutcomeSetPackageList.appendChild(wrap);
      }

      for (const item of (state().currentLocalOutcomeSetPackageImportSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.import_name}</strong><div class="meta">package:${item.package_name} · imported commit:${item.imported_commit_name} · branch:${item.target_branch_name} · imported:${item.imported_session_count}</div>`;
        els.localOutcomeSetPackageList.appendChild(wrap);
      }

      for (const item of (state().currentLocalOutcomeSetPackageResolutionSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.resolution_name}</strong><div class="meta">package:${item.package_name} · source:${item.source_commit_name} · branch:${item.target_branch_name} · resolved:${item.resolved_session_count} · skipped:${item.skipped_session_count}</div>`;
        els.localOutcomeSetPackageList.appendChild(wrap);
      }

      for (const item of Object.values(state().currentProject?.local_outcome_set_package_commits || {})) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.commit_name}</strong><div class="meta">resolution:${item.resolution_name} · package:${item.package_name} · branch:${item.target_branch_name} · resolved:${(item.resolved_session_ids || []).length}${item.promoted_point_name ? ` · promoted:${item.promoted_point_kind}:${item.promoted_point_name}` : ""}</div>`;
        els.localOutcomeSetPackageList.appendChild(wrap);
      }
    }

    function renderPreviewResult() {
      if (!els.localOutcomeSetPackagePreviewResultText) return;
      els.localOutcomeSetPackagePreviewResultText.textContent = state().currentLocalOutcomeSetPackagePreviewResult ? pretty(state().currentLocalOutcomeSetPackagePreviewResult) : "";
    }

    function renderDecisionList() {
      if (!els.localOutcomeSetPackageDecisionList) return;
      const preview = state().currentLocalOutcomeSetPackagePreviewResult;
      if (!preview?.preview_items?.length) {
        els.localOutcomeSetPackageDecisionList.innerHTML = '<div class="project-map-empty">No local outcome package preview decisions</div>';
        return;
      }

      els.localOutcomeSetPackageDecisionList.innerHTML = "";
      for (const item of preview.preview_items) {
        const wrap = document.createElement("div");
        wrap.className = "conflict-item";
        const decision = state().currentLocalOutcomeSetPackageImportDecisions[item.original_session_id] || { choice: "use_package" };
        wrap.innerHTML = `<strong>${item.original_session_id}</strong><div class="meta">status: ${item.status} · current head: ${item.current_head_session_id || "-"}</div>`;

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
          const decisions = { ...state().currentLocalOutcomeSetPackageImportDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = select.value;
          if (select.value !== "custom_text") delete decisions[item.original_session_id].custom_text;
          setState({ currentLocalOutcomeSetPackageImportDecisions: decisions });
          customInput.style.display = select.value === "custom_text" ? "block" : "none";
        });

        customInput.addEventListener("input", () => {
          const decisions = { ...state().currentLocalOutcomeSetPackageImportDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = "custom_text";
          decisions[item.original_session_id].custom_text = customInput.value;
          setState({ currentLocalOutcomeSetPackageImportDecisions: decisions });
        });

        row.appendChild(select);
        row.appendChild(customInput);
        wrap.appendChild(row);
        els.localOutcomeSetPackageDecisionList.appendChild(wrap);
      }
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
        const data = await postJson("/api/preview-local-outcome-set-package-import", {
          current_project_index: currentProject,
          package_data: pkg,
          import_name: els.importLocalOutcomeSetPackageNameInput?.value.trim() || undefined,
          target_branch_name: els.importLocalOutcomeSetTargetBranch?.value || undefined,
        });
        setState({
          currentLocalOutcomeSetPackagePreviewResult: data,
          currentLocalOutcomeSetPackageImportDecisions: {},
        });
        renderPreviewResult();
        renderDecisionList();
        setStatus(`Previewed local outcome package ${data.package_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package preview failed: ${err.message}`);
      }
    }

    function setDecisionForAll(choice, conflictsOnly = false) {
      const preview = state().currentLocalOutcomeSetPackagePreviewResult;
      if (!preview?.preview_items?.length) return;

      const decisions = { ...state().currentLocalOutcomeSetPackageImportDecisions };
      for (const item of preview.preview_items) {
        if (conflictsOnly && !item.conflict_like) continue;
        decisions[item.original_session_id] = { choice };
      }
      setState({ currentLocalOutcomeSetPackageImportDecisions: decisions });
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
        const data = await postJson("/api/resolve-local-outcome-set-package-import-conflicts", {
          current_project_index: currentProject,
          package_data: pkg,
          decisions: state().currentLocalOutcomeSetPackageImportDecisions,
          resolution_name: els.importLocalOutcomeSetPackageNameInput?.value.trim() || undefined,
          target_branch_name: els.importLocalOutcomeSetTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedLocalOutcomeSet?.checked,
        });
        renderResult(data);
        setState({
          currentLocalOutcomeSetPackagePreviewResult: null,
          currentLocalOutcomeSetPackageImportDecisions: {},
          currentLocalOutcomeSetPackageResult: data.local_outcome_set_package_resolution_result || null,
        });
        renderList();
        renderPreviewResult();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        updatePortableLocalOutcomeMergeSelectors();
        syncCommitAutofill();
        setStatus(`Resolved local outcome package import ${data.local_outcome_set_package_resolution_result?.resolution_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package resolution failed: ${err.message}`);
      }
    }

    function renderResultPanel() {
      if (!els.localOutcomeSetPackageResultText) return;
      if (state().currentLocalOutcomeSetPackage) {
        els.localOutcomeSetPackageResultText.textContent = pretty(state().currentLocalOutcomeSetPackage);
      } else if (state().currentLocalOutcomeSetPackageResult) {
        els.localOutcomeSetPackageResultText.textContent = pretty(state().currentLocalOutcomeSetPackageResult);
      } else {
        els.localOutcomeSetPackageResultText.textContent = "";
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
      const commitName = els.exportLocalOutcomeSetCommit?.value;
      if (!commitName) {
        setStatus("No local outcome set selected");
        return;
      }

      try {
        const data = await postJson("/api/export-local-outcome-set-package", {
          project_index: currentProject,
          commit_name: commitName,
          package_name: els.localOutcomeSetPackageName?.value.trim() || undefined,
          note: els.localOutcomeSetPackageNote?.value.trim() || undefined,
        });
        renderResult(data);
        renderList();
        renderPreviewResult();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        updatePortableLocalOutcomeMergeSelectors();
        setStatus(`Exported local outcome package ${data.local_outcome_set_package_result?.package_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package export failed: ${err.message}`);
      }
    }

    async function commitResolution() {
      const currentProject = state().currentProject;
      const currentResult = state().currentLocalOutcomeSetPackageResult;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      if (!currentResult?.resolved_session_ids) {
        setStatus("No resolved local outcome package result to commit");
        return;
      }

      try {
        const data = await postJson("/api/commit-local-outcome-set-package-resolution", {
          project_index: currentProject,
          local_outcome_set_package_resolution_result: currentResult,
          commit_name: els.localOutcomeSetPackageCommitName?.value.trim() || undefined,
          promote_point_name: els.localOutcomeSetPackagePromotePointName?.value.trim() || undefined,
          promote_point_kind: els.localOutcomeSetPackagePromotePointKind?.value || "release",
          note: els.localOutcomeSetPackageCommitNote?.value.trim() || undefined,
        });
        renderResult(data);
        setState({
          currentLocalOutcomeSetPackageResult: data.local_outcome_set_package_commit_result || null,
        });
        renderList();
        renderPreviewResult();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        updatePortableLocalOutcomeMergeSelectors();
        setStatus(`Committed local outcome package resolution ${data.local_outcome_set_package_commit_result?.commit_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package commit failed: ${err.message}`);
      }
    }

    function useCurrentPackage() {
      if (!els.importLocalOutcomeSetPackageJson) return;
      const currentPackage = state().currentLocalOutcomeSetPackage;
      els.importLocalOutcomeSetPackageJson.value = currentPackage ? pretty(currentPackage) : "";
      syncPackageGuidance();
      setStatus(currentPackage ? "Loaded current local outcome package" : "No current local outcome package");
    }

    function clearInput() {
      if (els.importLocalOutcomeSetPackageJson) els.importLocalOutcomeSetPackageJson.value = "";
      if (els.importLocalOutcomeSetPackageNameInput) els.importLocalOutcomeSetPackageNameInput.value = "";
      if (els.localOutcomeSetPackageCommitName) els.localOutcomeSetPackageCommitName.value = "";
      if (els.localOutcomeSetPackagePromotePointName) els.localOutcomeSetPackagePromotePointName.value = "";
      if (els.localOutcomeSetPackageCommitNote) els.localOutcomeSetPackageCommitNote.value = "";
      setState({
        currentLocalOutcomeSetPackagePreviewResult: null,
        currentLocalOutcomeSetPackageImportDecisions: {},
        currentLocalOutcomeSetPackageResult: null,
      });
      renderPreviewResult();
      renderDecisionList();
      renderResultPanel();
      syncPackageGuidance();
      setStatus("Cleared local outcome package input");
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
        const data = await postJson("/api/import-local-outcome-set-package", {
          current_project_index: currentProject,
          package: pkg,
          import_name: els.importLocalOutcomeSetPackageNameInput?.value.trim() || undefined,
          target_branch_name: els.importLocalOutcomeSetTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedLocalOutcomeSet?.checked,
        });
        renderResult(data);
        setState({
          currentLocalOutcomeSetPackagePreviewResult: null,
          currentLocalOutcomeSetPackageImportDecisions: {},
          currentLocalOutcomeSetPackageResult: data.local_outcome_set_package_import_result || null,
        });
        renderList();
        renderPreviewResult();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        updatePortableLocalOutcomeMergeSelectors();
        setStatus(`Imported local outcome package ${data.local_outcome_set_package_import_result?.import_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package import failed: ${err.message}`);
      }
    }

    return {
      updateSelectors,
      renderList,
      renderPreviewResult,
      renderDecisionList,
      previewImport,
      setDecisionForAll,
      applyDecisions,
      renderResultPanel,
      exportPackage,
      useCurrentPackage,
      clearInput,
      importPackage,
      commitResolution,
      syncPackageGuidance,
      syncExportAutofill,
      syncCommitAutofill,
      renderCurrentPackageSummary,
    };
  }

  window.LocalOutcomeSetPackageWorkflow = {
    createLocalOutcomeSetPackageController,
  };
})();
