(function () {
  function createProjectOperationsController(config) {
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

    function parseCsvList(raw) {
      return (raw || "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
    }

    function guessCustomValue(raw) {
      if (!raw.trim()) return "";
      try {
        return JSON.parse(raw);
      } catch {
        return raw;
      }
    }

    function renderOperationPanels() {
      renderCompareResult();
      renderMergeResult();
      renderResolvedMergeResult();
      renderMergeCommitResult();
      renderBranchRebaseResult();
      renderBranchResetResult();
      renderBranchCherryPickResult();
      renderBranchSquashResult();
    }

    function renderMergeCommitResult() {
      if (!els.mergeCommitResultText) return;
      els.mergeCommitResultText.textContent = state().currentMergeCommitResult ? pretty(state().currentMergeCommitResult) : "";
    }

    async function commitMergedSessionToWorkspace() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }

      const mergeOrResolutionResult =
        (state().currentResolvedMergeResult && state().currentResolvedMergeResult.summary?.finalized)
          ? state().currentResolvedMergeResult
          : (state().currentMergeResult && state().currentMergeResult.summary?.auto_merged ? state().currentMergeResult : null);

      if (!mergeOrResolutionResult || !mergeOrResolutionResult.merged_session) {
        setStatus("No finalized merged session to commit");
        return;
      }

      try {
        const data = await postJson("/api/commit-project-merge-result", {
          project_index: currentProject,
          merge_or_resolution_result: mergeOrResolutionResult,
          session_id: els.mergeCommitSessionId?.value.trim() || undefined,
          session_name: els.mergeCommitSessionName?.value.trim() || undefined,
          activate: !!els.activateCommittedSession?.checked,
          tags: ["merge-commit"],
          branch_name: els.mergeCommitBranchName?.value.trim() || undefined,
        });
        setState({ currentMergeCommitResult: data.project_index });
        renderResult(data);
        renderOperationPanels();
        setStatus("Merged session committed into workspace");
      } catch (err) {
        setStatus(`Merge commit failed: ${err.message}`);
      }
    }

    function renderResolvedMergeResult() {
      if (!els.resolvedMergeText) return;
      els.resolvedMergeText.textContent = state().currentResolvedMergeResult ? pretty(state().currentResolvedMergeResult) : "";
    }

    function setAllConflictChoices(choice) {
      if (!state().currentMergeResult?.conflicts?.length) return;
      const decisions = {};
      for (const conflict of state().currentMergeResult.conflicts) {
        decisions[conflict.path] = { choice };
      }
      setState({ currentConflictDecisions: decisions });
      renderConflictList();
    }

    function renderConflictList() {
      if (!els.mergeConflictList) return;
      const mergeResult = state().currentMergeResult;
      if (!mergeResult || !Array.isArray(mergeResult.conflicts) || !mergeResult.conflicts.length) {
        els.mergeConflictList.innerHTML = '<div class="project-map-empty">No conflicts to resolve</div>';
        return;
      }

      els.mergeConflictList.innerHTML = "";
      for (const conflict of mergeResult.conflicts) {
        const wrap = document.createElement("div");
        wrap.className = "conflict-item";
        const decision = state().currentConflictDecisions[conflict.path] || { choice: "left" };
        wrap.innerHTML = `
          <strong>${conflict.path}</strong>
          <div class="meta">reason: ${conflict.reason}\nbase: ${JSON.stringify(conflict.base)}\nleft: ${JSON.stringify(conflict.left)}\nright: ${JSON.stringify(conflict.right)}</div>
        `;

        const row = document.createElement("div");
        row.className = "row";

        const select = document.createElement("select");
        for (const choice of ["base", "left", "right", "custom"]) {
          const opt = document.createElement("option");
          opt.value = choice;
          opt.textContent = choice;
          if (decision.choice === choice) opt.selected = true;
          select.appendChild(opt);
        }

        const customInput = document.createElement("textarea");
        customInput.className = "small";
        customInput.placeholder = "Custom JSON or raw text";
        customInput.value = decision.choice === "custom" ? JSON.stringify(decision.value ?? "", null, 2) : "";
        customInput.style.display = decision.choice === "custom" ? "block" : "none";

        select.addEventListener("change", () => {
          const decisions = { ...state().currentConflictDecisions };
          decisions[conflict.path] = decisions[conflict.path] || {};
          decisions[conflict.path].choice = select.value;
          if (select.value !== "custom") {
            delete decisions[conflict.path].value;
          }
          setState({ currentConflictDecisions: decisions });
          customInput.style.display = select.value === "custom" ? "block" : "none";
        });

        customInput.addEventListener("input", () => {
          const decisions = { ...state().currentConflictDecisions };
          decisions[conflict.path] = decisions[conflict.path] || { choice: "custom" };
          decisions[conflict.path].choice = "custom";
          decisions[conflict.path].value = guessCustomValue(customInput.value);
          setState({ currentConflictDecisions: decisions });
        });

        row.appendChild(select);
        row.appendChild(customInput);
        wrap.appendChild(row);
        els.mergeConflictList.appendChild(wrap);
      }
    }

    async function applyMergeDecisions() {
      const currentProject = state().currentProject;
      const mergeResult = state().currentMergeResult;
      if (!currentProject || !mergeResult) {
        setStatus("No merge result to resolve");
        return;
      }

      try {
        const data = await postJson("/api/resolve-project-merge-conflicts", {
          project_index: currentProject,
          base_session_id: mergeResult.base_session_id,
          left_session_id: mergeResult.left_session_id,
          right_session_id: mergeResult.right_session_id,
          decisions: state().currentConflictDecisions,
        });
        setState({ currentResolvedMergeResult: data });
        renderResolvedMergeResult();
        setStatus(`Applied ${data.summary.resolved_count} decisions`);
      } catch (err) {
        setStatus(`Resolve failed: ${err.message}`);
      }
    }

    function updateMergeSelectors() {
      if (!els.mergeBaseSession || !els.mergeLeftSession || !els.mergeRightSession) return;
      const sessions = state().currentProject?.sessions || [];
      for (const select of [els.mergeBaseSession, els.mergeLeftSession, els.mergeRightSession]) {
        select.innerHTML = "";
        for (const item of sessions) {
          const opt = document.createElement("option");
          opt.value = item.session_id;
          opt.textContent = `${item.session_id} · ${item.session_name}`;
          select.appendChild(opt);
        }
      }
      if (sessions.length >= 1 && !els.mergeBaseSession.value) {
        els.mergeBaseSession.value = sessions[0].session_id;
      }
      if (sessions.length >= 2 && !els.mergeLeftSession.value) {
        els.mergeLeftSession.value = sessions[1].session_id;
      } else if (sessions.length >= 1) {
        els.mergeLeftSession.value = sessions[0].session_id;
      }
      if (sessions.length >= 3 && !els.mergeRightSession.value) {
        els.mergeRightSession.value = sessions[2].session_id;
      } else if (sessions.length >= 1) {
        els.mergeRightSession.value = sessions[Math.min(1, sessions.length - 1)].session_id;
      }
    }

    function renderMergeResult() {
      if (!els.mergeResultText) return;
      els.mergeResultText.textContent = state().currentMergeResult ? pretty(state().currentMergeResult) : "";
      renderConflictList();
    }

    async function mergeSessionsThreeWay() {
      const currentProject = state().currentProject;
      if (!currentProject || !currentProject.sessions?.length) {
        setStatus("Project has no sessions to merge");
        return;
      }

      const baseSessionId = els.mergeBaseSession?.value;
      const leftSessionId = els.mergeLeftSession?.value;
      const rightSessionId = els.mergeRightSession?.value;
      if (!baseSessionId || !leftSessionId || !rightSessionId) {
        setStatus("Select base / left / right sessions");
        return;
      }

      try {
        const data = await postJson("/api/merge-project-sessions-three-way", {
          project_index: currentProject,
          base_session_id: baseSessionId,
          left_session_id: leftSessionId,
          right_session_id: rightSessionId,
        });
        setState({
          currentMergeResult: data,
          currentResolvedMergeResult: null,
          currentConflictDecisions: {},
        });
        renderMergeResult();
        renderResolvedMergeResult();
        setStatus(`Three-way merge: ${baseSessionId} / ${leftSessionId} / ${rightSessionId}`);
      } catch (err) {
        setStatus(`Merge failed: ${err.message}`);
      }
    }

    function updateCompareSelectors() {
      if (!els.compareLeftSession || !els.compareRightSession) return;
      const sessions = state().currentProject?.sessions || [];
      els.compareLeftSession.innerHTML = "";
      els.compareRightSession.innerHTML = "";
      for (const item of sessions) {
        const left = document.createElement("option");
        left.value = item.session_id;
        left.textContent = `${item.session_id} · ${item.session_name}`;
        els.compareLeftSession.appendChild(left);

        const right = document.createElement("option");
        right.value = item.session_id;
        right.textContent = `${item.session_id} · ${item.session_name}`;
        els.compareRightSession.appendChild(right);
      }
      if (sessions.length >= 1 && !els.compareLeftSession.value) {
        els.compareLeftSession.value = sessions[0].session_id;
      }
      if (sessions.length >= 2 && !els.compareRightSession.value) {
        els.compareRightSession.value = sessions[1].session_id;
      } else if (sessions.length === 1) {
        els.compareRightSession.value = sessions[0].session_id;
      }
    }

    function renderCompareResult() {
      if (!els.compareResultText) return;
      els.compareResultText.textContent = state().currentCompareResult ? pretty(state().currentCompareResult) : "";
    }

    async function compareSessions() {
      const currentProject = state().currentProject;
      if (!currentProject || !currentProject.sessions?.length) {
        setStatus("Project has no sessions to compare");
        return;
      }

      const leftSessionId = els.compareLeftSession?.value;
      const rightSessionId = els.compareRightSession?.value;
      if (!leftSessionId || !rightSessionId) {
        setStatus("Select both sessions");
        return;
      }

      try {
        const data = await postJson("/api/compare-project-sessions", {
          project_index: currentProject,
          left_session_id: leftSessionId,
          right_session_id: rightSessionId,
        });
        setState({ currentCompareResult: data });
        renderCompareResult();
        setStatus(`Compared ${leftSessionId} vs ${rightSessionId}`);
      } catch (err) {
        setStatus(`Compare failed: ${err.message}`);
      }
    }

    function updateSquashSelectors() {
      if (!els.squashTargetBranch) return;
      const branches = state().currentBranchSummary || [];
      els.squashTargetBranch.innerHTML = "";
      for (const branch of branches) {
        const opt = document.createElement("option");
        opt.value = branch.branch_name;
        opt.textContent = branch.branch_name;
        if (branch.is_active_branch) opt.selected = true;
        els.squashTargetBranch.appendChild(opt);
      }
    }

    function renderBranchSquashResult() {
      if (!els.squashResultText) return;
      els.squashResultText.textContent = state().currentBranchSquashResult ? pretty(state().currentBranchSquashResult) : "";
    }

    async function squashSelectedSessions() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }

      const ids = parseCsvList(els.squashSessionIds?.value || "");
      const targetBranch = els.squashTargetBranch?.value;
      if (!ids.length) {
        setStatus("No session ids provided for squash");
        return;
      }
      if (!targetBranch) {
        setStatus("No target branch selected for squash");
        return;
      }

      try {
        const data = await postJson("/api/squash-project-sessions", {
          project_index: currentProject,
          source_session_ids: ids,
          target_branch_name: targetBranch,
          session_id: els.squashSessionId?.value.trim() || undefined,
          session_name: els.squashSessionName?.value.trim() || undefined,
          activate_head: !!els.activateSquashedHead?.checked,
        });
        renderResult(data);
        renderOperationPanels();
        setStatus(`Squashed ${ids.length} sessions into one commit`);
      } catch (err) {
        setStatus(`Squash failed: ${err.message}`);
      }
    }

    function updateCherryPickSelectors() {
      if (!els.cherryPickTargetBranch) return;
      const branches = state().currentBranchSummary || [];
      els.cherryPickTargetBranch.innerHTML = "";
      for (const branch of branches) {
        const opt = document.createElement("option");
        opt.value = branch.branch_name;
        opt.textContent = branch.branch_name;
        if (branch.is_active_branch) opt.selected = true;
        els.cherryPickTargetBranch.appendChild(opt);
      }
    }

    function renderBranchCherryPickResult() {
      if (!els.cherryPickResultText) return;
      els.cherryPickResultText.textContent = state().currentBranchCherryPickResult ? pretty(state().currentBranchCherryPickResult) : "";
    }

    async function cherryPickSelectedSessions() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }

      const ids = parseCsvList(els.cherryPickSessionIds?.value || "");
      const targetBranch = els.cherryPickTargetBranch?.value;
      if (!ids.length) {
        setStatus("No session ids provided for cherry-pick");
        return;
      }
      if (!targetBranch) {
        setStatus("No target branch selected");
        return;
      }

      try {
        const data = await postJson("/api/cherry-pick-project-sessions", {
          project_index: currentProject,
          source_session_ids: ids,
          target_branch_name: targetBranch,
          activate_head: !!els.activateCherryPickedHead?.checked,
        });
        renderResult(data);
        renderOperationPanels();
        setStatus(`Cherry-picked ${ids.length} sessions into ${targetBranch}`);
      } catch (err) {
        setStatus(`Cherry-pick failed: ${err.message}`);
      }
    }

    function updateResetSelectors() {
      if (!els.resetBranchName || !els.resetTargetSession) return;
      const branches = state().currentBranchSummary || [];
      els.resetBranchName.innerHTML = "";
      for (const branch of branches) {
        const opt = document.createElement("option");
        opt.value = branch.branch_name;
        opt.textContent = branch.branch_name;
        els.resetBranchName.appendChild(opt);
      }
      const active = branches.find((branch) => branch.is_active_branch);
      if (active) {
        els.resetBranchName.value = active.branch_name;
      }
      updateResetTargetSessions();
    }

    function updateResetTargetSessions() {
      if (!els.resetBranchName || !els.resetTargetSession) return;
      const branchName = els.resetBranchName.value;
      const sessions = (state().currentProject?.sessions || []).filter(
        (item) => item.entry_metadata?.branching?.branch_name === branchName
      );
      els.resetTargetSession.innerHTML = "";
      for (const item of sessions) {
        const opt = document.createElement("option");
        opt.value = item.session_id;
        opt.textContent = `${item.session_id} · ${item.session_name}`;
        els.resetTargetSession.appendChild(opt);
      }
      const activeHead = (state().currentBranchSummary || []).find((branch) => branch.branch_name === branchName)?.head_session_id;
      if (activeHead) {
        els.resetTargetSession.value = activeHead;
      }
    }

    function renderBranchResetResult() {
      if (!els.branchResetResultText) return;
      els.branchResetResultText.textContent = state().currentBranchResetResult ? pretty(state().currentBranchResetResult) : "";
    }

    async function resetBranchHeadToHistoricalPoint() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }

      const branchName = els.resetBranchName?.value;
      const targetSessionId = els.resetTargetSession?.value;
      if (!branchName || !targetSessionId) {
        setStatus("Select branch and historical session");
        return;
      }

      try {
        const data = await postJson("/api/reset-project-branch-head", {
          project_index: currentProject,
          branch_name: branchName,
          target_session_id: targetSessionId,
          activate_head: !!els.activateResetHead?.checked,
        });
        renderResult(data);
        renderOperationPanels();
        setStatus(`Reset branch ${branchName} to ${targetSessionId}`);
      } catch (err) {
        setStatus(`Branch reset failed: ${err.message}`);
      }
    }

    function updateRebaseSelectors() {
      if (!els.rebaseSourceBranch || !els.rebaseTargetBranch) return;
      const branches = state().currentBranchSummary || [];
      els.rebaseSourceBranch.innerHTML = "";
      els.rebaseTargetBranch.innerHTML = "";
      for (const branch of branches) {
        const source = document.createElement("option");
        source.value = branch.branch_name;
        source.textContent = branch.branch_name;
        els.rebaseSourceBranch.appendChild(source);

        const target = document.createElement("option");
        target.value = branch.branch_name;
        target.textContent = branch.branch_name;
        els.rebaseTargetBranch.appendChild(target);
      }
      const active = branches.find((branch) => branch.is_active_branch);
      if (active) {
        els.rebaseSourceBranch.value = active.branch_name;
      }
      if (branches.length >= 2) {
        const other = branches.find((branch) => branch.branch_name !== els.rebaseSourceBranch.value);
        if (other) els.rebaseTargetBranch.value = other.branch_name;
      } else if (branches.length === 1) {
        els.rebaseTargetBranch.value = branches[0].branch_name;
      }
    }

    function renderBranchRebaseResult() {
      if (!els.rebaseResultText) return;
      els.rebaseResultText.textContent = state().currentBranchRebaseResult ? pretty(state().currentBranchRebaseResult) : "";
    }

    async function rebaseBranchOntoTarget() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }

      const sourceBranchName = els.rebaseSourceBranch?.value;
      const targetBranchName = els.rebaseTargetBranch?.value;
      if (!sourceBranchName || !targetBranchName) {
        setStatus("Select source and target branches");
        return;
      }

      try {
        const data = await postJson("/api/rebase-project-branch", {
          project_index: currentProject,
          source_branch_name: sourceBranchName,
          target_branch_name: targetBranchName,
          activate_head: !!els.activateRebasedHead?.checked,
        });
        renderResult(data);
        renderOperationPanels();
        setStatus(`Rebased ${sourceBranchName} onto ${targetBranchName}`);
      } catch (err) {
        setStatus(`Branch rebase failed: ${err.message}`);
      }
    }

    return {
      renderMergeCommitResult,
      commitMergedSessionToWorkspace,
      renderResolvedMergeResult,
      setAllConflictChoices,
      renderMergeResult,
      applyMergeDecisions,
      updateMergeSelectors,
      mergeSessionsThreeWay,
      updateCompareSelectors,
      renderCompareResult,
      compareSessions,
      updateSquashSelectors,
      renderBranchSquashResult,
      squashSelectedSessions,
      updateCherryPickSelectors,
      renderBranchCherryPickResult,
      cherryPickSelectedSessions,
      updateResetSelectors,
      updateResetTargetSessions,
      renderBranchResetResult,
      resetBranchHeadToHistoricalPoint,
      updateRebaseSelectors,
      renderBranchRebaseResult,
      rebaseBranchOntoTarget,
    };
  }

  window.ProjectOperationsWorkflow = {
    createProjectOperationsController,
  };
})();
