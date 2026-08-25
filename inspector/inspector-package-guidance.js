(function () {
  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function cleanString(value) {
    return typeof value === "string" && value.trim() ? value.trim() : null;
  }

  function uniqueStrings(values) {
    const seen = new Set();
    const result = [];
    for (const value of values || []) {
      const cleaned = cleanString(value);
      if (!cleaned || seen.has(cleaned)) continue;
      seen.add(cleaned);
      result.push(cleaned);
    }
    return result;
  }

  function formatListPreview(values, limit = 6) {
    const items = uniqueStrings(values);
    if (!items.length) return "none";
    if (items.length <= limit) return items.join(", ");
    return `${items.slice(0, limit).join(", ")} +${items.length - limit} more`;
  }

  function kindLabel(kind) {
    if (kind === "snapshot") return "Snapshot package";
    if (kind === "reconcile_commit_package") return "Standalone outcome package";
    if (kind === "local_outcome_set_package") return "Local outcome package";
    return "SEMASCRIPT package";
  }

  function panelLabel(kind) {
    if (kind === "snapshot") return "Snapshot workflows";
    if (kind === "reconcile_commit_package") return "Standalone outcome package diff / compatibility";
    if (kind === "local_outcome_set_package") return "Local outcome set export / import as portable package";
    return "the matching inspector package panel";
  }

  function inputUsage(kind) {
    if (kind === "snapshot") {
      return "Paste a snapshot export package here to restore a workspace, run partial import, or reconcile selected sessions.";
    }
    if (kind === "reconcile_commit_package") {
      return "Paste a standalone promoted outcome package here to preview compatibility, import it directly, or resolve manual package decisions.";
    }
    if (kind === "local_outcome_set_package") {
      return "Paste a portable local outcome package here to preview local import compatibility, import it directly, or resolve manual local decisions.";
    }
    return "Paste a supported SEMASCRIPT package JSON here.";
  }

  function packageKindAction(kind) {
    if (kind === "snapshot") return "preview restore, apply partial import, or reconcile selected sessions";
    if (kind === "reconcile_commit_package") return "preview compatibility, import directly, or resolve package decisions";
    if (kind === "local_outcome_set_package") return "preview local import, import directly, or resolve local decisions";
    return "continue in the matching inspector package panel";
  }

  function packageGuidanceNextAction(analysis, options = {}) {
    if (options.nextAction) return options.nextAction;
    const state = analysis?.state || "empty";
    const expectedKind = analysis?.expectedKind;
    const detectedKind = analysis?.detectedKind;
    if (state === "valid") return `Next action: ${packageKindAction(detectedKind || expectedKind)}.`;
    if (state === "mismatch") return `Next action: switch to ${panelLabel(detectedKind)} or paste ${kindLabel(expectedKind)} here.`;
    if (state === "invalid") return "Next action: fix the JSON syntax before previewing or importing.";
    if (state === "unknown") return "Next action: paste a supported snapshot, standalone outcome, or local outcome package JSON.";
    return `Next action: paste ${kindLabel(expectedKind).toLowerCase()} JSON here.`;
  }

  function detectKind(payload) {
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) return "unknown";
    if (cleanString(payload.snapshot_version)) return "snapshot";
    if (cleanString(payload.resolution_set_package_version)) return "reconcile_commit_package";
    if (cleanString(payload.local_outcome_set_package_version)) return "local_outcome_set_package";
    return "unknown";
  }

  function summarizeSnapshotPackage(payload) {
    const workspaceSummary = Array.isArray(payload?.export_state?.workspace_summary) ? payload.export_state.workspace_summary : [];
    const frozenSessions = Array.isArray(payload?.export_state?.project_index_frozen?.sessions) ? payload.export_state.project_index_frozen.sessions : [];
    const tagPointSummary = Array.isArray(payload?.export_state?.tag_point_summary) ? payload.export_state.tag_point_summary : [];
    const branchSummary = Array.isArray(payload?.export_state?.branch_summary) ? payload.export_state.branch_summary : [];

    const sessionIds = uniqueStrings([
      ...workspaceSummary.map((item) => item?.session_id),
      ...frozenSessions.map((item) => item?.session_id),
      payload?.target_session_id,
      payload?.anchor?.target_session_id,
    ]);
    const tagNames = uniqueStrings([
      ...tagPointSummary.map((item) => item?.tag_name),
      payload?.anchor?.tag_name,
      payload?.source_point_name,
    ]);
    const snapshotNames = uniqueStrings([payload?.snapshot_name]);
    const branchNames = uniqueStrings([
      payload?.anchor?.branch_name,
      payload?.export_state?.active_branch_name,
      ...branchSummary.map((item) => item?.branch_name),
    ]);
    const primaryName = cleanString(payload?.snapshot_name) || "snapshot";
    const sourcePointKind = cleanString(payload?.source_point_kind);
    const sourcePointName = cleanString(payload?.source_point_name);
    const activeSessionId = cleanString(payload?.export_state?.active_session_id);

    return {
      primaryName,
      meta: [
        sourcePointKind && sourcePointName ? `${sourcePointKind}:${sourcePointName}` : null,
        branchNames[0] ? `branch:${branchNames[0]}` : null,
        activeSessionId ? `active:${activeSessionId}` : null,
      ].filter(Boolean),
      lists: [
        { label: "Sessions", values: sessionIds },
        { label: "Tag points", values: tagNames },
        { label: "Snapshot names", values: snapshotNames },
      ],
      availableSessionIds: sessionIds,
      availableTagNames: tagNames,
      availableSnapshotNames: snapshotNames,
    };
  }

  function summarizeReconcileCommitPackage(payload) {
    const resolvedSessions = Array.isArray(payload?.resolved_sessions) ? payload.resolved_sessions : [];
    const exportedCommit = payload?.exported_commit || {};
    const sessionIds = uniqueStrings([
      ...resolvedSessions.map((item) => item?.session_id),
      ...(Array.isArray(exportedCommit?.resolved_session_ids) ? exportedCommit.resolved_session_ids : []),
    ]);
    const primaryName = cleanString(payload?.package_name) || "standalone_outcome_package";
    const commitName = cleanString(payload?.commit_name) || cleanString(exportedCommit?.commit_name);
    const snapshotName = cleanString(exportedCommit?.snapshot_name);
    const branchName = cleanString(exportedCommit?.target_branch_name);

    return {
      primaryName,
      meta: [
        commitName ? `commit:${commitName}` : null,
        snapshotName ? `snapshot:${snapshotName}` : null,
        branchName ? `branch:${branchName}` : null,
      ].filter(Boolean),
      lists: [
        { label: "Resolved sessions", values: sessionIds },
      ],
      availableSessionIds: sessionIds,
    };
  }

  function summarizeLocalOutcomePackage(payload) {
    const resolvedSessions = Array.isArray(payload?.resolved_sessions) ? payload.resolved_sessions : [];
    const exportedCommit = payload?.exported_local_outcome_commit || {};
    const sessionIds = uniqueStrings([
      ...resolvedSessions.map((item) => item?.session_id),
      ...(Array.isArray(exportedCommit?.resolved_session_ids) ? exportedCommit.resolved_session_ids : []),
    ]);
    const primaryName = cleanString(payload?.package_name) || "local_outcome_package";
    const commitName = cleanString(payload?.commit_name) || cleanString(exportedCommit?.commit_name);
    const sourceCommitName = cleanString(exportedCommit?.source_commit_name);
    const branchName = cleanString(exportedCommit?.target_branch_name);
    const packageKind = cleanString(payload?.package_kind);

    return {
      primaryName,
      meta: [
        commitName ? `commit:${commitName}` : null,
        sourceCommitName ? `source:${sourceCommitName}` : null,
        branchName ? `branch:${branchName}` : null,
        packageKind ? `kind:${packageKind}` : null,
      ].filter(Boolean),
      lists: [
        { label: "Resolved sessions", values: sessionIds },
      ],
      availableSessionIds: sessionIds,
    };
  }

  function summarizePayload(kind, payload) {
    if (kind === "snapshot") return summarizeSnapshotPackage(payload);
    if (kind === "reconcile_commit_package") return summarizeReconcileCommitPackage(payload);
    if (kind === "local_outcome_set_package") return summarizeLocalOutcomePackage(payload);
    return {
      primaryName: "package",
      meta: [],
      lists: [],
      availableSessionIds: [],
      availableTagNames: [],
      availableSnapshotNames: [],
    };
  }

  function buildMismatchMessage(expectedKind, detectedKind, primaryName) {
    const named = primaryName ? ` "${primaryName}"` : "";
    return `This JSON looks like ${kindLabel(detectedKind)}${named}, not ${kindLabel(expectedKind)}. Use ${panelLabel(detectedKind)} instead.`;
  }

  function analyzeText(rawText, expectedKind) {
    const trimmed = typeof rawText === "string" ? rawText.trim() : "";
    const expectedLabel = kindLabel(expectedKind);
    if (!trimmed) {
      return {
        state: "empty",
        expectedKind,
        detectedKind: null,
        data: null,
        summary: null,
        message: inputUsage(expectedKind),
      };
    }

    let data = null;
    try {
      data = JSON.parse(trimmed);
    } catch (error) {
      return {
        state: "invalid",
        expectedKind,
        detectedKind: null,
        data: null,
        summary: null,
        message: `${expectedLabel} JSON is invalid: ${error?.message || "Invalid JSON"}`,
      };
    }

    const detectedKind = detectKind(data);
    const summary = summarizePayload(detectedKind, data);
    if (detectedKind === "unknown") {
      return {
        state: "unknown",
        expectedKind,
        detectedKind,
        data,
        summary,
        message: `JSON parsed, but it does not look like a supported ${expectedLabel.toLowerCase()}.`,
      };
    }

    if (expectedKind && detectedKind !== expectedKind) {
      return {
        state: "mismatch",
        expectedKind,
        detectedKind,
        data,
        summary,
        message: buildMismatchMessage(expectedKind, detectedKind, summary.primaryName),
      };
    }

    return {
      state: "valid",
      expectedKind,
      detectedKind,
      data,
      summary,
      message: `${kindLabel(detectedKind)} ready: ${summary.primaryName || "package"}.`,
    };
  }

  function renderHint(element, analysis) {
    if (!element) return;

    const stateClass = analysis?.state || "empty";
    const headlineByState = {
      empty: `${kindLabel(analysis?.expectedKind)} input`,
      invalid: `${kindLabel(analysis?.expectedKind)} parse error`,
      unknown: "Unsupported SEMASCRIPT JSON",
      mismatch: `${kindLabel(analysis?.detectedKind)} detected`,
      valid: `${kindLabel(analysis?.detectedKind || analysis?.expectedKind)} ready`,
    };
    const summary = analysis?.summary || null;
    const metaText = summary?.meta?.length ? summary.meta.join(" · ") : "";
    const nextAction = packageGuidanceNextAction(analysis);
    const listItems = (summary?.lists || [])
      .filter((item) => Array.isArray(item.values) && item.values.length)
      .map((item) => `<div class="package-guidance-list"><strong>${escapeHtml(item.label)}:</strong> ${escapeHtml(formatListPreview(item.values))}</div>`)
      .join("");

    element.className = `package-guidance ${stateClass === "valid" ? "is-valid" : stateClass === "mismatch" || stateClass === "unknown" ? "is-warning" : stateClass === "invalid" ? "is-error" : ""}`.trim();
    element.innerHTML = `
      <div class="package-guidance-head">${escapeHtml(headlineByState[stateClass] || "Package input")}</div>
      <div class="package-guidance-body">${escapeHtml(analysis?.message || "")}</div>
      <div class="package-guidance-next-action">${escapeHtml(nextAction)}</div>
      ${metaText ? `<div class="package-guidance-meta">${escapeHtml(metaText)}</div>` : ""}
      ${listItems}
    `;
  }

  function renderPayloadSummary(element, payload, expectedKind, options = {}) {
    if (!element) return;

    const emptyHeadline = options.headline || `${kindLabel(expectedKind)} summary`;
    const emptyMessage = options.emptyMessage || `No current ${kindLabel(expectedKind).toLowerCase()} available yet.`;
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      const nextAction = packageGuidanceNextAction({ state: "empty", expectedKind }, options);
      element.className = "package-guidance";
      element.innerHTML = `
        <div class="package-guidance-head">${escapeHtml(emptyHeadline)}</div>
        <div class="package-guidance-body">${escapeHtml(emptyMessage)}</div>
        <div class="package-guidance-next-action">${escapeHtml(nextAction)}</div>
      `;
      return;
    }

    const detectedKind = detectKind(payload);
    const kind = detectedKind === "unknown" ? expectedKind : detectedKind;
    const summary = summarizePayload(kind, payload);
    const metaText = summary?.meta?.length ? summary.meta.join(" · ") : "";
    const nextAction = packageGuidanceNextAction({ state: "valid", expectedKind, detectedKind: kind }, options);
    const listItems = (summary?.lists || [])
      .filter((item) => Array.isArray(item.values) && item.values.length)
      .map((item) => `<div class="package-guidance-list"><strong>${escapeHtml(item.label)}:</strong> ${escapeHtml(formatListPreview(item.values))}</div>`)
      .join("");
    const packageNameLead = summary.primaryName ? `Package: ${summary.primaryName}. ` : "";
    const note = `${packageNameLead}${options.note || `${kindLabel(kind)} ready.`}`.trim();

    element.className = "package-guidance is-valid";
    element.innerHTML = `
      <div class="package-guidance-head">${escapeHtml(options.headline || `${kindLabel(kind)} ready`)}</div>
      <div class="package-guidance-body">${escapeHtml(note)}</div>
      <div class="package-guidance-next-action">${escapeHtml(nextAction)}</div>
      ${metaText ? `<div class="package-guidance-meta">${escapeHtml(metaText)}</div>` : ""}
      ${listItems}
    `;
  }

  window.InspectorPackageGuidance = {
    analyzeText,
    renderHint,
    renderPayloadSummary,
    packageGuidanceNextAction,
    formatListPreview,
    kindLabel,
    panelLabel,
  };
})();
