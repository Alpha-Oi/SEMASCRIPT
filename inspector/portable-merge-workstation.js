(function () {
  function createPortableLocalOutcomeMergeController(config) {
    const {
      els,
      getCurrentProject,
      getMergeResult,
      setMergeResult,
      getMergeDecisions,
      setMergeDecisions,
      setMergeResolutionSummary,
      getMergeResolutionResult,
      setMergeResolutionResult,
      getMergeCommitResult,
      setMergeCommitResult,
      getSelectedItemId,
      setSelectedItemId,
      escapeHtml,
      pretty,
      postJson,
      renderResult,
      setStatus,
    } = config;

    function portableLocalOutcomeRoleText(role) {
      return role?.source_text || "";
    }

    function portableLocalOutcomeDefaultDecision(item) {
      return item?.conflict ? { choice: "use_left" } : { choice: "use_auto" };
    }

    function getPortableLocalOutcomeDecision(item) {
      return getMergeDecisions()[item.original_session_id] || portableLocalOutcomeDefaultDecision(item);
    }

    function setPortableLocalOutcomeDecision(originalSessionId, choice, customText) {
      const decisions = { ...getMergeDecisions() };
      const next = { choice };
      if (choice === "custom_text") next.custom_text = customText || "";
      decisions[originalSessionId] = next;
      setMergeDecisions(decisions);
      renderDecisionList();
      renderWorkstation();
    }

    function portableLocalOutcomeDraftForItem(item) {
      const decision = getPortableLocalOutcomeDecision(item);
      const choice = decision.choice || (item.conflict ? "use_left" : "use_auto");
      const baseText = portableLocalOutcomeRoleText(item.base);
      const leftText = portableLocalOutcomeRoleText(item.left);
      const rightText = portableLocalOutcomeRoleText(item.right);

      if (choice === "skip") {
        return { choice, sourceLabel: "skip", sourceText: "", skipped: true, invalid: false };
      }
      if (choice === "custom_text") {
        const customText = decision.custom_text || "";
        return {
          choice,
          sourceLabel: "custom",
          sourceText: customText,
          skipped: false,
          invalid: !customText.trim(),
        };
      }
      if (choice === "use_base") return { choice, sourceLabel: "base", sourceText: baseText, skipped: false, invalid: !baseText.trim() };
      if (choice === "use_left") return { choice, sourceLabel: "left", sourceText: leftText, skipped: false, invalid: !leftText.trim() };
      if (choice === "use_right") return { choice, sourceLabel: "right", sourceText: rightText, skipped: false, invalid: !rightText.trim() };

      if (item.status === "unchanged") return { choice, sourceLabel: "auto/base", sourceText: baseText, skipped: false, invalid: !baseText.trim() };
      if (item.status === "same_change" || item.status === "left_only_change") return { choice, sourceLabel: "auto/left", sourceText: leftText, skipped: false, invalid: !leftText.trim() };
      if (item.status === "right_only_change") return { choice, sourceLabel: "auto/right", sourceText: rightText, skipped: false, invalid: !rightText.trim() };
      return { choice, sourceLabel: "manual", sourceText: "", skipped: false, invalid: true };
    }

    function portableLocalOutcomeSummary() {
      const items = getMergeResult()?.merge_items || [];
      const summary = { total: items.length, conflicts: 0, ready: 0, skipped: 0, manual: 0, invalid: 0 };
      for (const item of items) {
        if (item.conflict) summary.conflicts += 1;
        const draft = portableLocalOutcomeDraftForItem(item);
        if (draft.skipped) summary.skipped += 1;
        if (draft.choice !== "use_auto") summary.manual += 1;
        if (draft.invalid) summary.invalid += 1;
        if (!draft.invalid && !draft.skipped) summary.ready += 1;
      }
      return summary;
    }

    function portableLocalOutcomeSnippet(text) {
      const value = (text || "").replace(/\s+/g, " ").trim();
      if (!value) return "No source text";
      return value.length > 96 ? `${value.slice(0, 96)}...` : value;
    }

    function portableLocalOutcomeNextAction(summary) {
      if (getMergeCommitResult()?.commit_name) return "Merge committed. Review commit result or start another comparison.";
      if (getMergeResolutionResult()?.resolved_session_ids?.length) return "Ready to commit resolved portable merge.";
      if (summary.invalid) return "Resolve needs-input items before applying merge decisions.";
      return "Review decisions, then apply merge decisions.";
    }

    function portableLocalOutcomeStateLabel(draft) {
      if (draft.invalid) return "Needs input";
      if (draft.skipped) return "Skipped";
      return "Ready";
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
      const resolutionResult = getMergeResolutionResult();
      const resolutionName = resolutionResult?.resolution_name || "";
      if (!resolutionName) return;
      applySuggestedInputValue(els.portableLocalOutcomeMergeCommitName, `${resolutionName}_commit`);
      applySuggestedInputValue(els.portableLocalOutcomeMergePromotePointName, `${resolutionName}_release`);
    }

    function renderWorkstation() {
      if (!els.portableMergeOverview || !els.portableMergeSessionList || !els.portableMergeDetail) return;
      const items = getMergeResult()?.merge_items || [];
      if (!items.length) {
        els.portableMergeOverview.innerHTML = `
          <div class="merge-overview-empty">
            <strong>No active merge preview</strong>
            <span>Select base, left and right committed portable local outcomes, then run compare.</span>
          </div>
        `;
        els.portableMergeSessionList.innerHTML = '<div class="merge-empty-state">Run a portable local three-way merge to populate the queue.</div>';
        els.portableMergeDetail.innerHTML = `
          <div class="merge-detail-empty">
            <div class="merge-next-action">
              <strong>Next action</strong>
              <span>Select base / left / right outcomes, then compare baseline / three-way merge.</span>
            </div>
            <p>Decision Studio will show base, left, right and live merged output here.</p>
          </div>
        `;
        if (els.portableMergeFocusMeta) els.portableMergeFocusMeta.textContent = "";
        if (els.portableMergeDecisionMeta) els.portableMergeDecisionMeta.textContent = "";
        return;
      }

      let selectedItemId = getSelectedItemId();
      if (!selectedItemId || !items.some((item) => item.original_session_id === selectedItemId)) {
        selectedItemId = (items.find((item) => item.conflict) || items[0]).original_session_id;
        setSelectedItemId(selectedItemId);
      }

      const summary = portableLocalOutcomeSummary();
      const selected = items.find((item) => item.original_session_id === selectedItemId) || items[0];
      const draft = portableLocalOutcomeDraftForItem(selected);
      const nextAction = portableLocalOutcomeNextAction(summary);

      els.portableMergeOverview.innerHTML = `
        <div class="merge-stat"><span>Total</span><strong>${summary.total}</strong></div>
        <div class="merge-stat ${summary.conflicts ? "warning" : ""}"><span>Conflicts</span><strong>${summary.conflicts}</strong></div>
        <div class="merge-stat success"><span>Ready</span><strong>${summary.ready}</strong></div>
        <div class="merge-stat ${summary.manual ? "warning" : ""}"><span>Manual decisions</span><strong>${summary.manual}</strong></div>
        <div class="merge-stat ${summary.skipped ? "warning" : ""}"><span>Skipped</span><strong>${summary.skipped}</strong></div>
        <div class="merge-stat ${summary.invalid ? "danger" : ""}"><span>Needs input</span><strong>${summary.invalid}</strong></div>
      `;

      els.portableMergeSessionList.innerHTML = "";
      for (const item of items) {
        const itemDraft = portableLocalOutcomeDraftForItem(item);
        const card = document.createElement("button");
        card.type = "button";
        card.className = [
          "merge-session-card",
          item.original_session_id === selectedItemId ? "active" : "",
          item.conflict ? "conflict" : "",
          itemDraft.invalid ? "needs-input" : "",
          itemDraft.skipped ? "skipped" : "",
        ].filter(Boolean).join(" ");
        card.innerHTML = `
          <div class="merge-session-top">
            <strong>${escapeHtml(item.original_session_id)}</strong>
            <span class="merge-badge merge-status-${item.status}">${escapeHtml(item.status)}</span>
          </div>
          <div class="merge-session-state">${escapeHtml(portableLocalOutcomeStateLabel(itemDraft))}</div>
          <div class="merge-session-meta">choice: ${escapeHtml(itemDraft.choice)} · source: ${escapeHtml(itemDraft.sourceLabel)}</div>
          <div class="merge-session-snippet">${escapeHtml(portableLocalOutcomeSnippet(itemDraft.sourceText))}</div>
        `;
        card.addEventListener("click", () => {
          setSelectedItemId(item.original_session_id);
          renderDecisionList();
          renderWorkstation();
        });
        els.portableMergeSessionList.appendChild(card);
      }

      if (els.portableMergeFocusMeta) {
        els.portableMergeFocusMeta.textContent = `${selected.original_session_id} · ${selected.status}${selected.conflict ? " · conflict" : ""}`;
      }
      if (els.portableMergeDecisionMeta) {
        els.portableMergeDecisionMeta.textContent = `resolution: ${els.portableLocalOutcomeMergeResolutionName?.value.trim() || "auto"} · branch: ${els.portableLocalOutcomeMergeTargetBranch?.value || "main"}`;
      }

      const baseText = portableLocalOutcomeRoleText(selected.base);
      const leftText = portableLocalOutcomeRoleText(selected.left);
      const rightText = portableLocalOutcomeRoleText(selected.right);
      const decisionButtons = [
        ["use_auto", "Auto"],
        ["use_base", "Base"],
        ["use_left", "Left"],
        ["use_right", "Right"],
        ["skip", "Skip"],
        ["custom_text", "Custom"],
      ].map(([choice, label]) => {
        const disabled = selected.conflict && choice === "use_auto" ? " disabled" : "";
        const active = draft.choice === choice ? " active" : "";
        return `<button type="button" class="merge-choice-btn${active}" data-choice="${choice}"${disabled}>${label}</button>`;
      }).join("");

      els.portableMergeDetail.innerHTML = `
        <div class="merge-next-action ${summary.invalid ? "danger" : getMergeResolutionResult()?.resolved_session_ids?.length ? "success" : ""}">
          <strong>Next action</strong>
          <span>${escapeHtml(nextAction)}</span>
        </div>
        <div class="merge-decision-summary">
          <div><span>Selected</span><strong>${escapeHtml(selected.original_session_id)}</strong></div>
          <div><span>Status</span><strong>${escapeHtml(selected.status)}</strong></div>
          <div><span>Decision</span><strong>${escapeHtml(draft.choice)}</strong></div>
          <div><span>Preview source</span><strong>${escapeHtml(draft.sourceLabel)}</strong></div>
        </div>
        <div class="merge-choice-strip">${decisionButtons}</div>
        <div class="merge-role-grid">
          <div class="merge-role-card">
            <div class="merge-role-head"><span>Base</span><button type="button" class="role-pick-btn" data-choice="use_base">Use</button></div>
            <pre class="merge-role-text">${escapeHtml(baseText || "No base source")}</pre>
          </div>
          <div class="merge-role-card">
            <div class="merge-role-head"><span>Left</span><button type="button" class="role-pick-btn" data-choice="use_left">Use</button></div>
            <pre class="merge-role-text">${escapeHtml(leftText || "No left source")}</pre>
          </div>
          <div class="merge-role-card">
            <div class="merge-role-head"><span>Right</span><button type="button" class="role-pick-btn" data-choice="use_right">Use</button></div>
            <pre class="merge-role-text">${escapeHtml(rightText || "No right source")}</pre>
          </div>
        </div>
        <div class="merge-preview-card">
          <div class="merge-preview-head">
            <strong>Live merged result</strong>
            <span class="merge-preview-meta">${escapeHtml(draft.sourceLabel)}${draft.skipped ? " · skipped" : draft.invalid ? " · needs input" : ""}</span>
          </div>
          <pre class="merge-preview-text">${escapeHtml(draft.skipped ? "Skipped from final merge chain." : draft.sourceText || "No resolved source text yet.")}</pre>
        </div>
        <label class="merge-custom-label"${draft.choice === "custom_text" ? "" : ' style="display:none"'}>
          Custom merged source
          <textarea id="portableMergeCustomText" class="small merge-custom-input" spellcheck="false" placeholder="Type custom merged source_text">${escapeHtml(draft.choice === "custom_text" ? (getPortableLocalOutcomeDecision(selected).custom_text || "") : "")}</textarea>
        </label>
      `;

      els.portableMergeDetail.querySelectorAll(".merge-choice-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          const choice = btn.getAttribute("data-choice");
          const current = getPortableLocalOutcomeDecision(selected);
          setPortableLocalOutcomeDecision(selected.original_session_id, choice, current.custom_text || "");
        });
      });
      els.portableMergeDetail.querySelectorAll(".role-pick-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          const choice = btn.getAttribute("data-choice");
          setPortableLocalOutcomeDecision(selected.original_session_id, choice);
        });
      });

      const customInput = document.getElementById("portableMergeCustomText");
      if (customInput) {
        customInput.addEventListener("input", () => {
          setPortableLocalOutcomeDecision(selected.original_session_id, "custom_text", customInput.value);
        });
      }
    }

    function updateSelectors() {
      const currentProject = getCurrentProject();
      const commits = Object.keys(currentProject?.local_outcome_set_package_commits || {});
      for (const el of [els.basePortableLocalOutcomeCommit, els.leftPortableLocalOutcomeCommit, els.rightPortableLocalOutcomeCommit, els.portableLocalOutcomeMergeTargetBranch]) {
        if (!el) continue;
        if (el === els.portableLocalOutcomeMergeTargetBranch) {
          el.innerHTML = "";
          const branches = Object.keys(currentProject?.branches || {});
          for (const branchName of branches) {
            const opt = document.createElement("option");
            opt.value = branchName;
            opt.textContent = branchName;
            el.appendChild(opt);
          }
          if (branches.length && !el.value) el.value = branches[0];
          continue;
        }

        el.innerHTML = "";
        for (const name of commits) {
          const opt = document.createElement("option");
          opt.value = name;
          opt.textContent = name;
          el.appendChild(opt);
        }
      }

      if (commits.length >= 1 && els.basePortableLocalOutcomeCommit) els.basePortableLocalOutcomeCommit.value = commits[0];
      if (commits.length >= 2 && els.leftPortableLocalOutcomeCommit) els.leftPortableLocalOutcomeCommit.value = commits[1];
      if (commits.length >= 3 && els.rightPortableLocalOutcomeCommit) els.rightPortableLocalOutcomeCommit.value = commits[2];
    }

    function renderThreeWayMergeResult() {
      if (!els.portableLocalOutcomeThreeWayMergeResultText) return;
      const mergeResult = getMergeResult();
      els.portableLocalOutcomeThreeWayMergeResultText.textContent = mergeResult ? pretty(mergeResult) : "";
    }

    async function compareBaselineOrThreeWayPortableLocalOutcome() {
      if (!getCurrentProject()) {
        setStatus("No project loaded");
        return;
      }

      const base = els.basePortableLocalOutcomeCommit?.value;
      const left = els.leftPortableLocalOutcomeCommit?.value;
      const right = els.rightPortableLocalOutcomeCommit?.value;
      if (!base || !left || !right) {
        setStatus("Select base, left and right committed portable local outcomes");
        return;
      }

      try {
        const data = await postJson("/api/compare-or-three-way-merge-committed-portable-local-outcomes", {
          project_index: getCurrentProject(),
          base_commit_name: base,
          left_commit_name: left,
          right_commit_name: right,
        });
        setMergeResult(data);
        setMergeDecisions({});
        setMergeResolutionSummary(null);
        setMergeResolutionResult(null);
        setMergeCommitResult(null);
        setSelectedItemId(data.merge_items?.find((item) => item.conflict)?.original_session_id || data.merge_items?.[0]?.original_session_id || null);
        renderThreeWayMergeResult();
        renderResolutionResult();
        renderCommitResult();
        renderDecisionList();
        renderWorkstation();
        setStatus(`Compared baseline/three-way merge ${base} / ${left} / ${right}`);
      } catch (err) {
        setStatus(`Portable local outcome three-way merge failed: ${err.message}`);
      }
    }

    function renderDecisionList() {
      if (!els.portableLocalOutcomeMergeDecisionList) return;
      const mergeItems = getMergeResult()?.merge_items;
      if (!mergeItems?.length) {
        els.portableLocalOutcomeMergeDecisionList.innerHTML = '<div class="project-map-empty">No portable local outcome three-way merge preview</div>';
        renderWorkstation();
        return;
      }

      els.portableLocalOutcomeMergeDecisionList.innerHTML = "";
      for (const item of mergeItems) {
        const wrap = document.createElement("div");
        const current = getPortableLocalOutcomeDecision(item);
        const draft = portableLocalOutcomeDraftForItem(item);
        wrap.className = `conflict-item${item.original_session_id === getSelectedItemId() ? " active" : ""}`;
        wrap.innerHTML = `<strong>${item.original_session_id}</strong><div class="meta">status: ${item.status} · conflict: ${item.conflict ? "yes" : "no"} · source: ${draft.sourceLabel}</div><div class="meta">${portableLocalOutcomeSnippet(draft.sourceText)}</div>`;

        const row = document.createElement("div");
        row.className = "row";
        const select = document.createElement("select");
        for (const choice of ["use_auto", "use_base", "use_left", "use_right", "skip", "custom_text"]) {
          const opt = document.createElement("option");
          opt.value = choice;
          opt.textContent = choice;
          if (current.choice === choice) opt.selected = true;
          if (item.conflict && choice === "use_auto") opt.disabled = true;
          select.appendChild(opt);
        }

        const customInput = document.createElement("textarea");
        customInput.className = "small";
        customInput.placeholder = "Custom source_text";
        customInput.value = current.choice === "custom_text" ? (current.custom_text || "") : "";
        customInput.style.display = current.choice === "custom_text" ? "block" : "none";

        wrap.addEventListener("click", (event) => {
          if (event.target === select || event.target === customInput) return;
          setSelectedItemId(item.original_session_id);
          renderDecisionList();
          renderWorkstation();
        });

        select.addEventListener("change", () => {
          const decisions = { ...getMergeDecisions() };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = select.value;
          if (select.value !== "custom_text") delete decisions[item.original_session_id].custom_text;
          setMergeDecisions(decisions);
          customInput.style.display = select.value === "custom_text" ? "block" : "none";
          renderDecisionList();
          renderWorkstation();
        });

        customInput.addEventListener("input", () => {
          const decisions = { ...getMergeDecisions() };
          decisions[item.original_session_id] = decisions[item.original_session_id] || { choice: "custom_text" };
          decisions[item.original_session_id].choice = "custom_text";
          decisions[item.original_session_id].custom_text = customInput.value;
          setMergeDecisions(decisions);
          renderWorkstation();
        });

        row.appendChild(select);
        row.appendChild(customInput);
        wrap.appendChild(row);
        els.portableLocalOutcomeMergeDecisionList.appendChild(wrap);
      }
      renderWorkstation();
    }

    function renderResolutionResult() {
      if (!els.portableLocalOutcomeMergeResolutionResultText) return;
      const resolutionResult = getMergeResolutionResult();
      els.portableLocalOutcomeMergeResolutionResultText.textContent = resolutionResult ? pretty(resolutionResult) : "";
      syncCommitAutofill();
    }

    function renderCommitResult() {
      if (!els.portableLocalOutcomeMergeCommitResultText) return;
      const commitResult = getMergeCommitResult();
      els.portableLocalOutcomeMergeCommitResultText.textContent = commitResult ? pretty(commitResult) : "";
    }

    function setDecisionForAll(choice, conflictsOnly = false) {
      const mergeItems = getMergeResult()?.merge_items;
      if (!mergeItems?.length) return;
      const decisions = { ...getMergeDecisions() };
      for (const item of mergeItems) {
        if (conflictsOnly && !item.conflict) continue;
        decisions[item.original_session_id] = { choice };
      }
      setMergeDecisions(decisions);
      renderDecisionList();
    }

    async function applyDecisions() {
      if (!getCurrentProject()) {
        setStatus("No project loaded");
        return;
      }
      if (!getMergeResult()) {
        setStatus("No portable local outcome three-way merge preview");
        return;
      }

      try {
        const data = await postJson("/api/resolve-portable-local-outcome-package-three-way-merge-conflicts", {
          project_index: getCurrentProject(),
          merge_result: getMergeResult(),
          decisions: getMergeDecisions(),
          resolution_name: els.portableLocalOutcomeMergeResolutionName?.value.trim() || undefined,
          target_branch_name: els.portableLocalOutcomeMergeTargetBranch?.value || undefined,
          activate_last_resolved: true,
        });
        setMergeResolutionSummary(data.portable_local_outcome_package_merge_resolution_summary || null);
        setMergeResolutionResult(data.portable_local_outcome_package_merge_resolution_result || null);
        setMergeCommitResult(null);
        renderResult(data);
        updateSelectors();
        renderDecisionList();
        renderResolutionResult();
        renderCommitResult();
        renderWorkstation();
        if (els.projectJson && data.project_index) els.projectJson.value = pretty(data.project_index);
        setStatus(`Resolved portable local outcome three-way merge ${data.portable_local_outcome_package_merge_resolution_result?.resolution_name || ""}`);
      } catch (err) {
        setStatus(`Portable local outcome three-way merge resolution failed: ${err.message}`);
      }
    }

    async function commitResolution() {
      if (!getCurrentProject()) {
        setStatus("No project loaded");
        return;
      }
      if (!getMergeResolutionResult()?.resolved_session_ids?.length) {
        setStatus("No resolved portable local outcome merge result to commit");
        return;
      }

      try {
        const data = await postJson("/api/commit-portable-local-outcome-package-three-way-merge-resolution", {
          project_index: getCurrentProject(),
          merge_resolution_result: getMergeResolutionResult(),
          commit_name: els.portableLocalOutcomeMergeCommitName?.value.trim() || undefined,
          promote_point_name: els.portableLocalOutcomeMergePromotePointName?.value.trim() || undefined,
          promote_point_kind: els.portableLocalOutcomeMergePromotePointKind?.value || "release",
          note: els.portableLocalOutcomeMergeCommitNote?.value.trim() || undefined,
        });
        setMergeCommitResult(data.portable_local_outcome_package_merge_commit_result || null);
        renderResult(data);
        updateSelectors();
        renderCommitResult();
        renderWorkstation();
        setStatus(`Committed portable local outcome three-way merge ${data.portable_local_outcome_package_merge_commit_result?.commit_name || ""}`);
      } catch (err) {
        setStatus(`Portable local outcome merge commit failed: ${err.message}`);
      }
    }

    return {
      updateSelectors,
      renderThreeWayMergeResult,
      renderDecisionList,
      renderResolutionResult,
      renderCommitResult,
      renderWorkstation,
      compareBaselineOrThreeWayPortableLocalOutcome,
      setDecisionForAll,
      applyDecisions,
      commitResolution,
      syncCommitAutofill,
    };
  }

  window.PortableLocalOutcomeMergeWorkstation = {
    createPortableLocalOutcomeMergeController,
  };
})();
