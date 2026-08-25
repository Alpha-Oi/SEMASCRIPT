(function () {
  function createSnapshotReconcileController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      parseCsvList,
      postJson,
      renderResult,
      setStatus,
      refreshProjectUi,
      renderSupplementaryPanels,
      updateReconcileCommitPackageSelectors,
      renderReconcileCommitPackageList,
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

    function renderSessionHint() {
      if (!els.snapshotReconcileSessionHint) return;
      const guidance = snapshotGuidance();
      const analysis = analyzeSnapshotPackageInput();
      if (analysis.state !== "valid") {
        els.snapshotReconcileSessionHint.textContent = "Load a snapshot package first, then list the snapshot session ids you want to reconcile into the current project.";
        return;
      }
      const sessionText = guidance ? guidance.formatListPreview(analysis.summary?.availableSessionIds) : "none";
      els.snapshotReconcileSessionHint.textContent = `Available snapshot session ids for reconcile: ${sessionText}.`;
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

    function syncCommitAutofill() {
      const reconcileResult = state().currentSnapshotReconcileResult;
      const baseName = reconcileResult?.resolution_name || reconcileResult?.reconcile_name || "";
      if (!baseName) return;
      applySuggestedInputValue(els.snapshotReconcileCommitName, `${baseName}_commit`);
      applySuggestedInputValue(els.snapshotReconcilePromotePointName, `${baseName}_release`);
    }

    function syncProjectStateFromResult(data, patch = {}) {
      setState({
        currentProject: data.project_index,
        currentProjectMap: data.workspace_dependency_map || null,
        currentProjectTimeline: data.workspace_timeline || null,
        currentBranchSummary: data.branch_summary || null,
        currentLineageGraph: data.workspace_lineage_graph || null,
        currentTagSummary: data.tag_point_summary || null,
        currentSnapshotSummary: data.snapshot_export_summary || null,
        currentSnapshotRestoreSummary: data.snapshot_restore_summary || null,
        currentPartialSnapshotImportSummary: data.partial_snapshot_import_summary || null,
        ...patch,
      });
      if (els.projectJson && data.project_index) {
        els.projectJson.value = pretty(data.project_index);
      }
    }

    function parseSnapshotPackage() {
      const analysis = analyzeSnapshotPackageInput();
      if (analysis.state === "empty") {
        setStatus("Snapshot package JSON is empty. Paste a snapshot export package before running reconcile.");
        return null;
      }
      if (analysis.state === "invalid" || analysis.state === "mismatch" || analysis.state === "unknown") {
        setStatus(analysis.message);
        return null;
      }
      return analysis.data;
    }

    function parseSelectedSessionIds(emptyMessage) {
      const analysis = analyzeSnapshotPackageInput();
      const ids = parseCsvList(els.snapshotReconcileSessionIds?.value || "");
      if (!ids.length) {
        const guidance = snapshotGuidance();
        const sessionPreview = guidance ? guidance.formatListPreview(analysis.summary?.availableSessionIds) : "none";
        setStatus(`${emptyMessage}. Available snapshot session ids: ${sessionPreview}.`);
        return null;
      }
      const available = new Set(analysis.summary?.availableSessionIds || []);
      if (available.size) {
        const unknown = ids.filter((value) => !available.has(value));
        if (unknown.length) {
          const guidance = snapshotGuidance();
          const sessionPreview = guidance ? guidance.formatListPreview(analysis.summary?.availableSessionIds) : "none";
          setStatus(`Unknown snapshot session ids: ${unknown.join(", ")}. Available: ${sessionPreview}.`);
          return null;
        }
      }
      return ids;
    }

    function renderDecisionList() {
      if (!els.snapshotReconcileDecisionList) return;
      const preview = state().currentSnapshotReconcilePreview;
      if (!preview?.preview_items?.length) {
        els.snapshotReconcileDecisionList.innerHTML = '<div class="project-map-empty">No reconcile preview decisions</div>';
        return;
      }
      els.snapshotReconcileDecisionList.innerHTML = "";
      for (const item of preview.preview_items) {
        const wrap = document.createElement("div");
        wrap.className = "conflict-item";
        const decision = state().currentSnapshotReconcileDecisions[item.original_session_id] || { choice: "use_snapshot" };
        wrap.innerHTML = `
          <strong>${item.original_session_id} · ${item.session_name || ""}</strong>
          <div class="meta">status: ${item.status} · current head: ${item.current_head_session_id || "-"} · target: ${item.target_branch_name}</div>
        `;

        const row = document.createElement("div");
        row.className = "row";
        const select = document.createElement("select");
        for (const choice of ["use_snapshot", "use_current", "skip", "custom_text"]) {
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
          const decisions = { ...state().currentSnapshotReconcileDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = select.value;
          if (select.value !== "custom_text") {
            delete decisions[item.original_session_id].custom_text;
          }
          setState({ currentSnapshotReconcileDecisions: decisions });
          customInput.style.display = select.value === "custom_text" ? "block" : "none";
        });

        customInput.addEventListener("input", () => {
          const decisions = { ...state().currentSnapshotReconcileDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || { choice: "custom_text" };
          decisions[item.original_session_id].choice = "custom_text";
          decisions[item.original_session_id].custom_text = customInput.value;
          setState({ currentSnapshotReconcileDecisions: decisions });
        });

        row.appendChild(select);
        row.appendChild(customInput);
        wrap.appendChild(row);
        els.snapshotReconcileDecisionList.appendChild(wrap);
      }
    }

    function setDecisionForAll(choice, conflictsOnly = false) {
      const preview = state().currentSnapshotReconcilePreview;
      if (!preview?.preview_items?.length) return;
      const decisions = { ...state().currentSnapshotReconcileDecisions };
      for (const item of preview.preview_items) {
        if (conflictsOnly && !item.conflict_like) continue;
        decisions[item.original_session_id] = { choice };
      }
      setState({ currentSnapshotReconcileDecisions: decisions });
      renderDecisionList();
    }

    async function applyDecisions() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No current project loaded");
        return;
      }
      const snapshotPackage = parseSnapshotPackage();
      if (!snapshotPackage) return;
      const ids = parseSelectedSessionIds("No session ids provided for reconcile decisions");
      if (!ids) return;

      try {
        const data = await postJson("/api/resolve-snapshot-reconcile-conflicts", {
          current_project_index: currentProject,
          snapshot_package: snapshotPackage,
          decisions: state().currentSnapshotReconcileDecisions,
          resolution_name: els.snapshotReconcileName?.value.trim() || undefined,
          selected_session_ids: ids,
          target_branch_name: els.snapshotReconcileTargetBranch?.value.trim() || undefined,
          activate_last_resolved: !!els.activateSnapshotReconcileHead?.checked,
        });
        syncProjectStateFromResult(data, {
          currentSnapshotReconcileSummary: data.snapshot_reconcile_summary || null,
          currentSnapshotReconcilePreview: null,
          currentSnapshotReconcileResult: data.snapshot_reconcile_resolution_result || null,
        });
        refreshProjectUi();
        renderDecisionList();
        renderPreview();
        renderReconcileResult();
        renderResult(data);
        setStatus(`Applied snapshot reconcile resolution ${state().currentSnapshotReconcileResult?.resolution_name || ""}`);
      } catch (err) {
        setStatus(`Snapshot reconcile resolution failed: ${err.message}`);
      }
    }

    function updateSelectors() {
      if (!els.snapshotReconcileTargetBranch) return;
      const branches = state().currentBranchSummary || [];
      els.snapshotReconcileTargetBranch.innerHTML = "";
      for (const branch of branches) {
        const opt = document.createElement("option");
        opt.value = branch.branch_name;
        opt.textContent = branch.branch_name;
        if (branch.is_active_branch) opt.selected = true;
        els.snapshotReconcileTargetBranch.appendChild(opt);
      }
    }

    function updateCommitCompareSelectors() {
      if (!els.compareReconcileCommitLeft || !els.compareReconcileCommitRight) return;
      const items = state().currentSnapshotReconcileCommitSummary || [];
      els.compareReconcileCommitLeft.innerHTML = "";
      els.compareReconcileCommitRight.innerHTML = "";
      for (const item of items) {
        const left = document.createElement("option");
        left.value = item.commit_name;
        left.textContent = item.commit_name;
        els.compareReconcileCommitLeft.appendChild(left);

        const right = document.createElement("option");
        right.value = item.commit_name;
        right.textContent = item.commit_name;
        els.compareReconcileCommitRight.appendChild(right);
      }
      if (items.length >= 1) els.compareReconcileCommitLeft.value = items[0].commit_name;
      if (items.length >= 2) els.compareReconcileCommitRight.value = items[1].commit_name;
      else if (items.length === 1) els.compareReconcileCommitRight.value = items[0].commit_name;
    }

    function renderCommitCompareResult() {
      if (!els.compareReconcileCommitResultText) return;
      const compareResult = state().currentSnapshotReconcileCommitCompareResult;
      els.compareReconcileCommitResultText.textContent = compareResult ? pretty(compareResult) : "";
    }

    async function comparePromotedOutcomes() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const leftCommitName = els.compareReconcileCommitLeft?.value;
      const rightCommitName = els.compareReconcileCommitRight?.value;
      if (!leftCommitName || !rightCommitName) {
        setStatus("Select both promoted reconcile outcomes");
        return;
      }
      try {
        const data = await postJson("/api/compare-snapshot-reconcile-commits", {
          project_index: currentProject,
          left_commit_name: leftCommitName,
          right_commit_name: rightCommitName,
        });
        setState({ currentSnapshotReconcileCommitCompareResult: data });
        renderCommitCompareResult();
        setStatus(`Compared ${leftCommitName} vs ${rightCommitName}`);
      } catch (err) {
        setStatus(`Resolution set compare failed: ${err.message}`);
      }
    }

    function renderCommitList() {
      if (!els.snapshotReconcileCommitList) return;
      els.snapshotReconcileCommitList.innerHTML = "";
      for (const item of (state().currentSnapshotReconcileCommitSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.commit_name}</strong><div class="meta">${item.snapshot_name} · ${item.target_branch_name} · resolved:${item.resolved_session_count}${item.promoted_point_name ? ` · promoted:${item.promoted_point_kind}:${item.promoted_point_name}` : ""}</div>`;
        els.snapshotReconcileCommitList.appendChild(wrap);
      }
      updateCommitCompareSelectors();
      updateReconcileCommitPackageSelectors();
      renderReconcileCommitPackageList();
    }

    function renderCommitResult() {
      if (!els.snapshotReconcileCommitResultText) return;
      const commitResult = state().currentSnapshotReconcileCommitResult;
      els.snapshotReconcileCommitResultText.textContent = commitResult ? pretty(commitResult) : "";
    }

    async function commitResolution() {
      const currentProject = state().currentProject;
      const currentSnapshotReconcileResult = state().currentSnapshotReconcileResult;
      if (!currentProject || !currentSnapshotReconcileResult) {
        setStatus("No resolved snapshot reconcile result to commit");
        return;
      }
      try {
        const data = await postJson("/api/commit-snapshot-reconcile-resolution", {
          project_index: currentProject,
          snapshot_reconcile_resolution_result: currentSnapshotReconcileResult,
          commit_name: els.snapshotReconcileCommitName?.value.trim() || undefined,
          promote_point_name: els.snapshotReconcilePromotePointName?.value.trim() || undefined,
          promote_point_kind: els.snapshotReconcilePromotePointKind?.value || "release",
          note: els.snapshotReconcileCommitNote?.value.trim() || undefined,
        });
        syncProjectStateFromResult(data, {
          currentSnapshotReconcileSummary: data.snapshot_reconcile_summary || null,
          currentSnapshotReconcileCommitSummary: data.snapshot_reconcile_commit_summary || null,
          currentSnapshotReconcileCommitResult: data.snapshot_reconcile_commit_result || null,
        });
        refreshProjectUi();
        renderCommitResult();
        renderCommitCompareResult();
        renderResult(data);
        setStatus(`Committed snapshot reconcile ${state().currentSnapshotReconcileCommitResult?.commit_name || ""}`);
      } catch (err) {
        setStatus(`Snapshot reconcile commit failed: ${err.message}`);
      }
    }

    function renderList() {
      if (!els.snapshotReconcileList) return;
      els.snapshotReconcileList.innerHTML = "";
      for (const item of (state().currentSnapshotReconcileSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.reconcile_name}</strong><div class="meta">${item.snapshot_name} · ${item.target_branch_name} · reconciled:${item.reconciled_session_count} · conflict-like:${item.conflict_like_count}</div>`;
        els.snapshotReconcileList.appendChild(wrap);
      }
    }

    function renderPreview() {
      if (!els.snapshotReconcilePreviewText) return;
      const preview = state().currentSnapshotReconcilePreview;
      els.snapshotReconcilePreviewText.textContent = preview ? pretty(preview) : "";
      renderDecisionList();
    }

    function renderReconcileResult() {
      if (!els.snapshotReconcileResultText) return;
      const reconcileResult = state().currentSnapshotReconcileResult;
      els.snapshotReconcileResultText.textContent = reconcileResult ? pretty(reconcileResult) : "";
      syncCommitAutofill();
    }

    function useCurrentSnapshot() {
      if (!els.snapshotRestoreJson) return;
      const snapshotPackage = state().currentSnapshotPackage;
      els.snapshotRestoreJson.value = snapshotPackage ? pretty(snapshotPackage) : "";
      renderSessionHint();
      setStatus(snapshotPackage ? "Loaded current snapshot package for reconcile" : "No current snapshot package");
    }

    function clearInput() {
      if (els.snapshotReconcileSessionIds) els.snapshotReconcileSessionIds.value = "";
      if (els.snapshotReconcileTargetBranch) els.snapshotReconcileTargetBranch.value = "";
      if (els.snapshotReconcileName) els.snapshotReconcileName.value = "";
      setState({
        currentSnapshotReconcilePreview: null,
        currentSnapshotReconcileDecisions: {},
        currentSnapshotReconcileResult: null,
      });
      renderPreview();
      renderReconcileResult();
      renderCommitResult();
      renderSessionHint();
      setStatus("Cleared snapshot reconcile input");
    }

    async function previewBeforeApply() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No current project loaded");
        return;
      }
      const snapshotPackage = parseSnapshotPackage();
      if (!snapshotPackage) return;
      const ids = parseSelectedSessionIds("No session ids provided for reconcile preview");
      if (!ids) return;

      try {
        const data = await postJson("/api/preview-snapshot-reconcile-in-project", {
          current_project_index: currentProject,
          snapshot_package: snapshotPackage,
          selected_session_ids: ids,
          target_branch_name: els.snapshotReconcileTargetBranch?.value.trim() || undefined,
          reconcile_name: els.snapshotReconcileName?.value.trim() || undefined,
        });
        setState({ currentSnapshotReconcilePreview: data });
        renderPreview();
        setStatus(`Previewed snapshot reconcile ${data.reconcile_name || ""}`);
      } catch (err) {
        setStatus(`Snapshot reconcile preview failed: ${err.message}`);
      }
    }

    async function reconcileIntoLineage() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No current project loaded");
        return;
      }
      const snapshotPackage = parseSnapshotPackage();
      if (!snapshotPackage) return;
      const ids = parseSelectedSessionIds("No session ids provided for snapshot reconcile");
      if (!ids) return;

      try {
        const data = await postJson("/api/reconcile-snapshot-into-project", {
          current_project_index: currentProject,
          snapshot_package: snapshotPackage,
          reconcile_name: els.snapshotReconcileName?.value.trim() || undefined,
          selected_session_ids: ids,
          target_branch_name: els.snapshotReconcileTargetBranch?.value.trim() || undefined,
          activate_last_reconciled: !!els.activateSnapshotReconcileHead?.checked,
        });
        syncProjectStateFromResult(data, {
          currentSnapshotReconcileSummary: data.snapshot_reconcile_summary || null,
          currentSnapshotReconcilePreview: null,
          currentSnapshotReconcileResult: data.snapshot_reconcile_result || null,
        });
        refreshProjectUi();
        renderSupplementaryPanels();
        renderPreview();
        renderReconcileResult();
        renderResult(data);
        setStatus(`Applied snapshot reconcile ${state().currentSnapshotReconcileResult?.reconcile_name || ""}`);
      } catch (err) {
        setStatus(`Snapshot reconcile failed: ${err.message}`);
      }
    }

    return {
      renderDecisionList,
      setDecisionForAll,
      applyDecisions,
      updateSelectors,
      updateCommitCompareSelectors,
      renderCommitCompareResult,
      comparePromotedOutcomes,
      renderCommitList,
      renderCommitResult,
      commitResolution,
      renderList,
      renderPreview,
      renderReconcileResult,
      useCurrentSnapshot,
      clearInput,
      previewBeforeApply,
      reconcileIntoLineage,
      renderSessionHint,
      syncCommitAutofill,
    };
  }

  window.SnapshotReconcileWorkflow = {
    createSnapshotReconcileController,
  };
})();
