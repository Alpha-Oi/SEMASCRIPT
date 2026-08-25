(function () {
  function createProjectWorkspaceController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      postJson,
      renderResult,
      setStatus,
    } = config;

    function state() {
      return getState();
    }

    function hydrateProjectResult(result) {
      if (!result.project_index?.project_name) return false;

      if (els.projectName) {
        els.projectName.value = result.project_index.project_name;
      }

      setState({
        currentProject: result.project_index,
        currentProjectMap: result.workspace_dependency_map || null,
        currentProjectTimeline: result.workspace_timeline || null,
        currentBranchSummary: result.branch_summary || null,
        currentLineageGraph: result.workspace_lineage_graph || null,
        currentBranchRebaseResult: result.branch_rebase_result || state().currentBranchRebaseResult,
        currentBranchResetResult: result.branch_reset_result || state().currentBranchResetResult,
        currentTagSummary: result.tag_point_summary || state().currentTagSummary,
        currentTagPointResult: result.tag_release_result || state().currentTagPointResult,
        currentSnapshotSummary: result.snapshot_export_summary || state().currentSnapshotSummary,
        currentSnapshotResult: result.snapshot_export_result || state().currentSnapshotResult,
        currentSnapshotPackage: result.snapshot_export_package || state().currentSnapshotPackage,
        currentSnapshotRestoreSummary: result.snapshot_restore_summary || state().currentSnapshotRestoreSummary,
        currentSnapshotRestoreResult: result.snapshot_restore_result || state().currentSnapshotRestoreResult,
        currentPartialSnapshotImportSummary: result.partial_snapshot_import_summary || state().currentPartialSnapshotImportSummary,
        currentPartialSnapshotImportResult: result.partial_snapshot_import_result || state().currentPartialSnapshotImportResult,
        currentSnapshotReconcileSummary: result.snapshot_reconcile_summary || state().currentSnapshotReconcileSummary,
        currentSnapshotReconcilePreview: result.snapshot_reconcile_preview || state().currentSnapshotReconcilePreview,
        currentSnapshotReconcileResult: result.snapshot_reconcile_result || state().currentSnapshotReconcileResult,
        currentSnapshotReconcileCommitSummary: result.snapshot_reconcile_commit_summary || state().currentSnapshotReconcileCommitSummary,
        currentSnapshotReconcileCommitResult: result.snapshot_reconcile_commit_result || state().currentSnapshotReconcileCommitResult,
        currentSnapshotReconcileCommitCompareResult: result.snapshot_reconcile_commit_compare_result || state().currentSnapshotReconcileCommitCompareResult,
        currentSnapshotReconcileCommitPackageSummary: result.snapshot_reconcile_commit_package_summary || state().currentSnapshotReconcileCommitPackageSummary,
        currentSnapshotReconcileCommitPackageImportSummary: result.snapshot_reconcile_commit_package_import_summary || state().currentSnapshotReconcileCommitPackageImportSummary,
        currentSnapshotReconcileCommitPackagePreview: result.snapshot_reconcile_commit_package_preview || state().currentSnapshotReconcileCommitPackagePreview,
        currentSnapshotReconcileCommitPackageResolutionSummary: result.snapshot_reconcile_commit_package_resolution_summary || state().currentSnapshotReconcileCommitPackageResolutionSummary,
        currentSnapshotReconcileCommitPackageCommitSummary: result.snapshot_reconcile_commit_package_commit_summary || state().currentSnapshotReconcileCommitPackageCommitSummary,
        currentSnapshotReconcileCommitPackageResult:
          result.snapshot_reconcile_commit_package_result
          || result.snapshot_reconcile_commit_package_import_result
          || result.snapshot_reconcile_commit_package_resolution_result
          || result.snapshot_reconcile_commit_package_commit_result
          || state().currentSnapshotReconcileCommitPackageResult,
        currentSnapshotReconcileCommitPackage: result.snapshot_reconcile_commit_package || state().currentSnapshotReconcileCommitPackage,
        currentLocalOutcomeSetPackageSummary: result.local_outcome_set_package_summary || state().currentLocalOutcomeSetPackageSummary,
        currentLocalOutcomeSetPackageImportSummary: result.local_outcome_set_package_import_summary || state().currentLocalOutcomeSetPackageImportSummary,
        currentLocalOutcomeSetPackageResolutionSummary: result.local_outcome_set_package_resolution_summary || state().currentLocalOutcomeSetPackageResolutionSummary,
        currentLocalOutcomeSetPackage: result.local_outcome_set_package || state().currentLocalOutcomeSetPackage,
        currentLocalOutcomeSetPackagePreviewResult: result.local_outcome_set_package_preview_result || state().currentLocalOutcomeSetPackagePreviewResult,
        currentLocalOutcomeSetPackageResult:
          result.local_outcome_set_package_result
          || result.local_outcome_set_package_import_result
          || result.local_outcome_set_package_resolution_result
          || result.local_outcome_set_package_commit_result
          || state().currentLocalOutcomeSetPackageResult,
        currentPortableLocalOutcomeMergeResolutionSummary:
          result.portable_local_outcome_package_merge_resolution_summary || state().currentPortableLocalOutcomeMergeResolutionSummary,
        currentPortableLocalOutcomeMergeResolutionResult:
          result.portable_local_outcome_package_merge_resolution_result || state().currentPortableLocalOutcomeMergeResolutionResult,
        currentPortableLocalOutcomeMergeCommitResult:
          result.portable_local_outcome_package_merge_commit_result || state().currentPortableLocalOutcomeMergeCommitResult,
        currentBranchCherryPickResult: result.branch_cherry_pick_result || state().currentBranchCherryPickResult,
        currentBranchSquashResult: result.branch_squash_result || state().currentBranchSquashResult,
      });

      if (els.projectJson && result.project_index) {
        els.projectJson.value = pretty(result.project_index);
      }

      return true;
    }

    async function activateProjectSession(sessionId, successMessage, failurePrefix) {
      const currentProject = state().currentProject;
      if (!currentProject || !sessionId) return;

      try {
        const data = await postJson("/api/switch-project-session", {
          project_index: currentProject,
          session_id: sessionId,
        });
        renderResult(data);
        setStatus(successMessage);
      } catch (err) {
        setStatus(`${failurePrefix}: ${err.message}`);
      }
    }

    function renderProjectTimeline() {
      if (!els.projectTimeline) return;
      const timeline = state().currentProjectTimeline;
      if (!timeline || !Array.isArray(timeline.events) || !timeline.events.length) {
        els.projectTimeline.innerHTML = '<div class="project-map-empty">No timeline available</div>';
        return;
      }

      const list = document.createElement("div");
      list.className = "timeline-list";
      for (const event of timeline.events) {
        const item = document.createElement("div");
        item.className = "timeline-item" + (event.is_active_session_event ? " active" : "");
        item.innerHTML = `<strong>#${event.seq} · ${event.title}</strong><div class="meta">${event.event_type}${event.session_id ? " · " + event.session_id : ""}</div>`;
        if (event.session_id && state().currentProject) {
          const btn = document.createElement("button");
          btn.textContent = "Activate from event";
          btn.addEventListener("click", async () => {
            await activateProjectSession(event.session_id, `Activated ${event.session_id}`, "Timeline switch failed");
          });
          item.appendChild(btn);
        }
        list.appendChild(item);
      }
      els.projectTimeline.innerHTML = "";
      els.projectTimeline.appendChild(list);
    }

    function renderProjectMap() {
      if (!els.projectDependencyMap) return;
      const projectMap = state().currentProjectMap;
      if (!projectMap || !Array.isArray(projectMap.nodes) || !projectMap.nodes.length) {
        els.projectDependencyMap.innerHTML = '<div class="project-map-empty">No dependency map available</div>';
        return;
      }

      let maxX = 0;
      let maxY = 0;
      for (const node of projectMap.nodes) {
        maxX = Math.max(maxX, node.x || 0);
        maxY = Math.max(maxY, node.y || 0);
      }
      const width = Math.max(760, maxX + 180);
      const height = Math.max(260, maxY + 120);

      const linkParts = [];
      const nodeIndex = new Map(projectMap.nodes.map((node) => [node.session_id, node]));
      for (const link of projectMap.links || []) {
        const from = nodeIndex.get(link.from_session_id);
        const to = nodeIndex.get(link.to_session_id);
        if (!from || !to) continue;
        const x1 = (from.x || 60) + 70;
        const y1 = (from.y || 60) + 24;
        const x2 = (to.x || 60) + 70;
        const y2 = (to.y || 60) + 24;
        const stroke = link.relation === "flow" ? "#2563eb" : "#9ca3af";
        const dash = link.relation === "shared" ? ' stroke-dasharray="5,4"' : "";
        const mx = (x1 + x2) / 2;
        const my = (y1 + y2) / 2 - 8;
        const label = `${link.relation}:${(link.tokens || []).slice(0, 2).join(",")}`;
        linkParts.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="1.6"${dash}/>`);
        linkParts.push(`<text class="project-map-meta" x="${mx}" y="${my}" text-anchor="middle">${label}</text>`);
      }

      const nodeParts = [];
      for (const node of projectMap.nodes) {
        const x = node.x || 60;
        const y = node.y || 60;
        const stroke = node.is_active ? "#10b981" : "#111827";
        const fill = node.is_active ? "#ecfdf5" : "#ffffff";
        const tokens = (node.outputs || []).slice(0, 3).join(", ");
        nodeParts.push(`
          <g class="project-map-node" data-session-id="${node.session_id}">
            <rect x="${x}" y="${y}" width="150" height="54" rx="14" ry="14" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
            <text class="project-map-label" x="${x + 75}" y="${y + 20}" text-anchor="middle">${node.session_name}</text>
            <text class="project-map-meta" x="${x + 75}" y="${y + 36}" text-anchor="middle">${node.profile || "-"} · out:${tokens || "-"}</text>
          </g>
        `);
      }

      els.projectDependencyMap.innerHTML = `<svg viewBox="0 0 ${width} ${height}">${linkParts.join("\n")}${nodeParts.join("\n")}</svg>`;
      els.projectDependencyMap.querySelectorAll(".project-map-node").forEach((el) => {
        el.addEventListener("click", async () => {
          const sessionId = el.getAttribute("data-session-id");
          await activateProjectSession(sessionId, `Activated ${sessionId}`, "Switch failed");
        });
      });
    }

    function renderBranchList() {
      if (!els.branchList) return;
      els.branchList.innerHTML = "";
      const branches = state().currentBranchSummary || [];
      for (const branch of branches) {
        const wrap = document.createElement("div");
        wrap.className = "branch-item" + (branch.is_active_branch ? " active" : "");
        wrap.innerHTML = `<strong>${branch.branch_name}</strong><div class="meta">root: ${branch.root_session_id || "-"} · head: ${branch.head_session_id || "-"} · sessions: ${branch.session_count}</div>`;
        const btn = document.createElement("button");
        btn.textContent = "Activate head";
        btn.addEventListener("click", async () => {
          if (!branch.head_session_id) return;
          await activateProjectSession(branch.head_session_id, `Activated head of ${branch.branch_name}`, "Branch head switch failed");
        });
        wrap.appendChild(btn);
        els.branchList.appendChild(wrap);
      }
    }

    function renderLineageGraph() {
      if (!els.projectLineageGraph) return;
      const lineageGraph = state().currentLineageGraph;
      if (!lineageGraph || !Array.isArray(lineageGraph.nodes) || !lineageGraph.nodes.length) {
        els.projectLineageGraph.innerHTML = '<div class="project-map-empty">No lineage graph available</div>';
        return;
      }

      let maxX = 0;
      let maxY = 0;
      for (const node of lineageGraph.nodes) {
        maxX = Math.max(maxX, node.x || 0);
        maxY = Math.max(maxY, node.y || 0);
      }
      const width = Math.max(760, maxX + 180);
      const height = Math.max(260, maxY + 120);

      const nodeIndex = new Map(lineageGraph.nodes.map((node) => [node.session_id, node]));
      const edgeParts = [];
      for (const edge of lineageGraph.edges || []) {
        const from = nodeIndex.get(edge.from_session_id);
        const to = nodeIndex.get(edge.to_session_id);
        if (!from || !to) continue;
        const x1 = (from.x || 60) + 72;
        const y1 = (from.y || 60) + 24;
        const x2 = (to.x || 60) + 72;
        const y2 = (to.y || 60) + 24;
        const dash = edge.relation === "merge_parent" ? ' stroke-dasharray="5,4"' : "";
        edgeParts.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#111827" stroke-width="1.4"${dash}/>`);
      }

      const nodeParts = [];
      for (const node of lineageGraph.nodes) {
        const x = node.x || 60;
        const y = node.y || 60;
        const fill = node.is_active ? "#ecfdf5" : "#ffffff";
        const stroke = node.is_active ? "#10b981" : "#111827";
        nodeParts.push(`
          <g class="project-map-node" data-session-id="${node.session_id}">
            <rect x="${x}" y="${y}" width="150" height="68" rx="14" ry="14" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
            <text class="project-map-label" x="${x + 75}" y="${y + 18}" text-anchor="middle">${node.session_name}</text>
            <text class="project-map-meta" x="${x + 75}" y="${y + 35}" text-anchor="middle">${node.branch_name} · ${node.lineage_kind}</text>
            <text class="project-map-meta" x="${x + 75}" y="${y + 50}" text-anchor="middle">${(node.attached_points && node.attached_points.length) ? node.attached_points.map((point) => point.tag_name).slice(0, 2).join(", ") : ""}</text>
          </g>
        `);
      }

      els.projectLineageGraph.innerHTML = `<svg viewBox="0 0 ${width} ${height}">${edgeParts.join("\n")}${nodeParts.join("\n")}</svg>`;
      els.projectLineageGraph.querySelectorAll(".project-map-node").forEach((el) => {
        el.addEventListener("click", async () => {
          const sessionId = el.getAttribute("data-session-id");
          await activateProjectSession(sessionId, `Activated ${sessionId}`, "Lineage switch failed");
        });
      });
    }

    function renderProjectSessions() {
      if (!els.projectSessionsList) return;
      els.projectSessionsList.innerHTML = "";
      const currentProject = state().currentProject;
      if (!currentProject || !Array.isArray(currentProject.sessions)) return;

      for (const item of currentProject.sessions) {
        const wrap = document.createElement("div");
        wrap.className = "project-session-item" + (item.session_id === currentProject.active_session_id ? " active" : "");
        wrap.innerHTML = `<strong>${item.session_name}</strong><div class="meta">${item.session_id} · ${item.profile || "-"} · ${item.source_mode || "-"}</div><div class="meta">${(item.tags || []).join(", ")}</div>`;
        const buttons = document.createElement("div");
        buttons.className = "buttons";
        const activate = document.createElement("button");
        activate.textContent = "Activate";
        activate.addEventListener("click", async () => {
          await activateProjectSession(item.session_id, `Activated ${item.session_id}`, "Switch failed");
        });
        buttons.appendChild(activate);
        wrap.appendChild(buttons);
        els.projectSessionsList.appendChild(wrap);
      }
    }

    return {
      hydrateProjectResult,
      renderProjectTimeline,
      renderProjectMap,
      renderBranchList,
      renderLineageGraph,
      renderProjectSessions,
    };
  }

  window.ProjectWorkspaceWorkflow = {
    createProjectWorkspaceController,
  };
})();
