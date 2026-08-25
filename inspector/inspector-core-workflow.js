(function () {
  function createInspectorCoreController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      hydrateProjectResult,
      renderSvg,
      renderGraph,
      renderers,
      updaters,
    } = config;

    function state() {
      return getState();
    }

    function patch(nextState) {
      setState(nextState);
    }

    function syncActiveSession(activeSession) {
      if (!activeSession) return;

      patch({ currentSession: activeSession });
      if (typeof activeSession.project?.source_text === "string" && els.inputText) {
        els.inputText.value = activeSession.project.source_text;
      }
      if (els.initialState) {
        els.initialState.value = activeSession.project?.initial_state !== undefined
          ? pretty(activeSession.project.initial_state)
          : "";
      }
      if (activeSession.project?.profile && els.profile) {
        els.profile.value = activeSession.project.profile;
      }
      if (els.sessionJson) {
        els.sessionJson.value = pretty(activeSession);
      }
    }

    function refreshProjectUiForSnapshotReconcileWorkflow() {
      renderers.renderProjectSessions();
      renderers.renderProjectMap();
      renderers.renderProjectTimeline();
      renderers.renderBranchList();
      renderers.renderTagPointList();
      renderers.renderSnapshotList();
      renderers.renderSnapshotReconcileList();
      renderers.renderSnapshotReconcileCommitList();
      renderers.renderLineageGraph();
      updaters.updateTagTargetSessions();
      updaters.updateSnapshotSelectors();
      updaters.updateResetSelectors();
      updaters.updateRebaseSelectors();
      updaters.updateCherryPickSelectors();
      updaters.updateSquashSelectors();
      updaters.updatePartialImportSelectors();
      updaters.updateSnapshotReconcileSelectors();
      updaters.updateCompareSelectors();
      updaters.updateMergeSelectors();
    }

    function renderSupplementaryPanelsForSnapshotReconcileWorkflow() {
      renderers.renderTagPointResult();
      renderers.renderSnapshotResult();
      renderers.renderSnapshotRestorePreview();
      renderers.renderSnapshotRestoreResult();
      renderers.renderPartialImportResult();
      renderers.renderCompareResult();
      renderers.renderMergeResult();
    }

    function refreshProjectUiForReconcileCommitPackageWorkflow() {
      renderers.renderProjectSessions();
      renderers.renderProjectMap();
      renderers.renderProjectTimeline();
      renderers.renderBranchList();
      renderers.renderTagPointList();
      renderers.renderLineageGraph();
    }

    function renderLocalOutcomeSetPackagePanels() {
      renderers.renderLocalOutcomeSetPackageList();
      renderers.renderLocalOutcomeSetPackagePreviewResult();
      renderers.renderLocalOutcomeSetPackageDecisionList();
      renderers.renderLocalOutcomeSetPackageResult();
    }

    function refreshProjectHydratedPanels() {
      renderers.renderProjectSessions();
      renderers.renderProjectMap();
      renderers.renderProjectTimeline();
      renderers.renderBranchList();
      renderers.renderTagPointList();
      renderers.renderSnapshotList();
      renderers.renderSnapshotReconcileList();
      renderers.renderSnapshotReconcileCommitList();
      renderers.renderReconcileCommitPackageList();
      renderers.renderReconcileCommitPackagePreview();
      renderers.renderReconcileCommitPackageDecisionList();
      renderers.renderReconcileCommitPackageResult();
      renderers.renderSnapshotReconcileCommitCompareResult();
      renderers.renderLineageGraph();
      updaters.updateTagTargetSessions();
      updaters.updatePartialImportSelectors();
      updaters.updateSnapshotSelectors();
      updaters.updateResetSelectors();
      updaters.updateRebaseSelectors();
      updaters.updateCherryPickSelectors();
      updaters.updateSquashSelectors();
      updaters.updateCompareSelectors();
      updaters.updateMergeSelectors();
      updaters.updateReconcileCommitPackageSelectors();
      updaters.updateLocalOutcomeSetPackageSelectors();
      updaters.updatePortableLocalOutcomeMergeSelectors();
      renderers.renderTagPointResult();
      renderers.renderSnapshotResult();
      renderers.renderSnapshotRestorePreview();
      renderers.renderSnapshotRestoreResult();
      renderers.renderPartialImportResult();
      renderers.renderSnapshotReconcileResult();
      renderers.renderSnapshotReconcileCommitResult();
      renderers.renderCompareResult();
      renderers.renderMergeResult();
      renderers.renderResolvedMergeResult();
      renderers.renderMergeCommitResult();
      renderers.renderBranchResetResult();
      renderers.renderBranchRebaseResult();
      renderers.renderBranchCherryPickResult();
      renderers.renderBranchSquashResult();
      renderLocalOutcomeSetPackagePanels();
      renderers.renderPortableLocalOutcomeThreeWayMergeResult();
      renderers.renderPortableLocalOutcomeMergeDecisionList();
      renderers.renderPortableLocalOutcomeMergeResolutionResult();
      renderers.renderPortableLocalOutcomeMergeCommitResult();
      renderers.renderPortableLocalOutcomeWorkstation();
    }

    function renderResult(result) {
      patch({ currentResult: result });

      if (result.session_name && els.sessionName) {
        els.sessionName.value = result.session_name;
      }
      if (typeof result.source_text === "string" && els.inputText) {
        els.inputText.value = result.source_text;
      }
      if (result.profile && els.profile) {
        els.profile.value = result.profile;
      }

      if (hydrateProjectResult(result)) {
        const activeSession = result.project_index?.sessions?.find(
          (item) => item.session_id === result.project_index.active_session_id,
        )?.session || null;
        syncActiveSession(activeSession);
        refreshProjectHydratedPanels();
      }

      if (result.ui_state?.preview_mode) {
        patch({ previewMode: result.ui_state.preview_mode });
      }

      if (els.normalizedText) {
        els.normalizedText.textContent = [
          `normalized_text:\n${result.normalized_text || ""}`,
          "",
          `slinear:\n${result.slinear || ""}`,
          result.decomposed_slinear ? `\ndecomposed_slinear:\n${result.decomposed_slinear}` : "",
        ].join("\n");
      }
      if (els.validationText) {
        els.validationText.textContent = pretty(result.validation);
      }
      if (els.astText) {
        els.astText.textContent = pretty(result.ast_document);
      }
      if (els.runtimeText) {
        els.runtimeText.textContent = pretty(result.runtime_report);
      }
      if (els.stateText) {
        els.stateText.textContent = pretty(result.state_report);
      }

      if (result.graph_document) {
        const graphDocument = structuredClone(result.graph_document);
        patch({
          graphDoc: graphDocument,
          selectedEntityId: result.ui_state?.selected_entity_id || graphDocument.root_entity_id || null,
        });
        renderGraph();
      }

      renderSvg();
    }

    return {
      refreshProjectUiForSnapshotReconcileWorkflow,
      renderSupplementaryPanelsForSnapshotReconcileWorkflow,
      refreshProjectUiForReconcileCommitPackageWorkflow,
      renderLocalOutcomeSetPackagePanels,
      refreshProjectHydratedPanels,
      renderResult,
    };
  }

  window.InspectorCoreWorkflow = {
    createInspectorCoreController,
  };
})();
