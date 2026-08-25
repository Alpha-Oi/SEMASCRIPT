(function () {
  function createInspectorActionController(config) {
    const {
      getGraphSessionWorkspaceController,
      getProjectLifecycleController,
      getProjectOperationsController,
      getSnapshotReconcileController,
      getReconcileCommitPackageController,
      getLocalOutcomeSetPackageController,
      getPortableLocalOutcomeMergeController,
      getInspectorPanelController,
    } = config;

    function graph() {
      return getGraphSessionWorkspaceController();
    }

    function lifecycle() {
      return getProjectLifecycleController();
    }

    function operations() {
      return getProjectOperationsController();
    }

    function snapshot() {
      return getSnapshotReconcileController();
    }

    function reconcilePackage() {
      return getReconcileCommitPackageController();
    }

    function localOutcome() {
      return getLocalOutcomeSetPackageController();
    }

    function portableMerge() {
      return getPortableLocalOutcomeMergeController();
    }

    function panels() {
      return getInspectorPanelController();
    }

    async function analyze() {
      await graph().analyze();
    }

    async function importTextToGraph() {
      await graph().importTextToGraph();
    }

    async function analyzeGraph() {
      await graph().analyzeGraph();
    }

    function clearAll() {
      graph().clearAll();
    }

    async function loadSamples() {
      await graph().loadSamples();
    }

    function addEntity() {
      graph().addEntity();
    }

    function setRoot() {
      graph().setRoot();
    }

    function deleteSelected() {
      graph().deleteSelected();
    }

    function saveSelectedEntity() {
      graph().saveSelectedEntity();
    }

    function addEdge() {
      graph().addEdge();
    }

    async function exportTextSession() {
      await graph().exportTextSession();
    }

    async function exportGraphSession() {
      await graph().exportGraphSession();
    }

    async function importSession() {
      await graph().importSession();
    }

    async function downloadSession() {
      await graph().downloadSession();
    }

    async function addCurrentToProject() {
      await graph().addCurrentToProject();
    }

    function renderGraph() {
      graph().renderGraph();
    }

    function renderProjectSessions() {
      panels().renderProjectSessions();
    }

    async function exportProject() {
      await lifecycle().exportProject();
    }

    function downloadProject() {
      lifecycle().downloadProject();
    }

    async function importProject() {
      await lifecycle().importProject();
    }

    function clearProject() {
      lifecycle().clearProject();
    }

    async function createBranchFromActiveSession() {
      await lifecycle().createBranchFromActiveSession();
    }

    function renderTagPointList() {
      panels().renderTagPointList();
    }

    function renderTagPointResult() {
      panels().renderTagPointResult();
    }

    async function createTagReleasePoint() {
      await lifecycle().createTagReleasePoint();
    }

    function renderSnapshotList() {
      panels().renderSnapshotList();
    }

    function renderSnapshotResult() {
      panels().renderSnapshotResult();
    }

    async function createSnapshotExport() {
      await lifecycle().createSnapshotExport();
    }

    function downloadCurrentSnapshot() {
      lifecycle().downloadCurrentSnapshot();
    }

    function updateSnapshotSelectors() {
      panels().updateSnapshotSelectors();
    }

    function updateTagTargetSessions() {
      panels().updateTagTargetSessions();
    }

    function renderSnapshotRestorePreview() {
      panels().renderSnapshotRestorePreview();
    }

    function updateSnapshotPackageGuidance() {
      lifecycle().syncSnapshotPackageGuidance();
    }

    function syncReconcileCommitPackageExportAutofill() {
      reconcilePackage().syncExportAutofill();
    }

    function syncLocalOutcomeSetPackageExportAutofill() {
      localOutcome().syncExportAutofill();
    }

    async function previewSnapshotRestoreBeforeApply() {
      await lifecycle().previewSnapshotRestoreBeforeApply();
    }

    function renderSnapshotRestoreResult() {
      panels().renderSnapshotRestoreResult();
    }

    function useCurrentSnapshotForRestore() {
      lifecycle().useCurrentSnapshotForRestore();
      snapshot().renderSessionHint();
    }

    function clearSnapshotRestoreInput() {
      lifecycle().clearSnapshotRestoreInput();
      snapshot().renderSessionHint();
    }

    async function restoreWorkspaceFromSnapshot() {
      await lifecycle().restoreWorkspaceFromSnapshot();
    }

    function renderPartialImportResult() {
      panels().renderPartialImportResult();
    }

    function useCurrentSnapshotForPartialImport() {
      lifecycle().useCurrentSnapshotForPartialImport();
      snapshot().renderSessionHint();
    }

    function clearPartialImportInput() {
      lifecycle().clearPartialImportInput();
    }

    async function partialImportFromSnapshot() {
      await lifecycle().partialImportFromSnapshot();
    }

    function renderSnapshotReconcileList() {
      panels().renderSnapshotReconcileList();
    }

    function renderSnapshotReconcilePreview() {
      panels().renderSnapshotReconcilePreview();
    }

    function updateSnapshotReconcileSessionHint() {
      snapshot().renderSessionHint();
    }

    function renderSnapshotReconcileResult() {
      panels().renderSnapshotReconcileResult();
    }

    function useCurrentSnapshotForReconcile() {
      snapshot().useCurrentSnapshot();
    }

    function clearSnapshotReconcileInput() {
      snapshot().clearInput();
    }

    async function previewSnapshotReconcileBeforeApply() {
      await snapshot().previewBeforeApply();
    }

    async function reconcileSnapshotIntoLineage() {
      await snapshot().reconcileIntoLineage();
    }

    function useSnapshotForAllReconcile() {
      snapshot().setDecisionForAll("use_snapshot", false);
    }

    function useCurrentForAllSnapshotConflicts() {
      snapshot().setDecisionForAll("use_current", true);
    }

    async function applySnapshotReconcileDecisions() {
      await snapshot().applyDecisions();
    }

    function renderSnapshotReconcileCommitList() {
      panels().renderSnapshotReconcileCommitList();
    }

    function renderSnapshotReconcileCommitResult() {
      panels().renderSnapshotReconcileCommitResult();
    }

    async function commitSnapshotReconcileResolution() {
      await snapshot().commitResolution();
    }

    function renderSnapshotReconcileCommitCompareResult() {
      panels().renderSnapshotReconcileCommitCompareResult();
    }

    function updateSnapshotReconcileCommitCompareSelectors() {
      panels().updateSnapshotReconcileCommitCompareSelectors();
    }

    async function comparePromotedReconcileOutcomes() {
      await snapshot().comparePromotedOutcomes();
    }

    function renderReconcileCommitPackageList() {
      panels().renderReconcileCommitPackageList();
    }

    function renderReconcileCommitPackagePreview() {
      panels().renderReconcileCommitPackagePreview();
    }

    function renderReconcileCommitPackageDecisionList() {
      panels().renderReconcileCommitPackageDecisionList();
    }

    function renderReconcileCommitPackageResult() {
      panels().renderReconcileCommitPackageResult();
    }

    function updateReconcileCommitPackageGuidance() {
      reconcilePackage().syncPackageGuidance();
    }

    async function exportReconcileCommitPackage() {
      await reconcilePackage().exportPackage();
    }

    function useCurrentReconcileCommitPackage() {
      reconcilePackage().useCurrentPackage();
    }

    async function previewReconcileCommitPackageImport() {
      await reconcilePackage().previewImport();
    }

    async function importReconcileCommitPackage() {
      await reconcilePackage().importPackage();
    }

    function clearReconcileCommitPackageInput() {
      reconcilePackage().clearInput();
    }

    function usePackageForAllImport() {
      reconcilePackage().setDecisionForAll("use_package", false);
    }

    function useCurrentForImportConflicts() {
      reconcilePackage().setDecisionForAll("use_current", true);
    }

    async function applyReconcileCommitPackageDecisions() {
      await reconcilePackage().applyDecisions();
    }

    async function commitReconcileCommitPackageResolution() {
      await reconcilePackage().commitResolution();
    }

    function renderLocalOutcomeSetPackageList() {
      panels().renderLocalOutcomeSetPackageList();
    }

    function renderLocalOutcomeSetPackagePreviewResult() {
      panels().renderLocalOutcomeSetPackagePreviewResult();
    }

    function renderLocalOutcomeSetPackageDecisionList() {
      panels().renderLocalOutcomeSetPackageDecisionList();
    }

    function renderLocalOutcomeSetPackageResult() {
      panels().renderLocalOutcomeSetPackageResult();
    }

    function updateLocalOutcomeSetPackageGuidance() {
      localOutcome().syncPackageGuidance();
    }

    async function exportLocalOutcomeSetPackage() {
      await localOutcome().exportPackage();
    }

    function useCurrentLocalOutcomeSetPackage() {
      localOutcome().useCurrentPackage();
    }

    async function previewLocalOutcomeSetPackageImport() {
      await localOutcome().previewImport();
    }

    async function importLocalOutcomeSetPackage() {
      await localOutcome().importPackage();
    }

    function clearLocalOutcomeSetPackageInput() {
      localOutcome().clearInput();
    }

    function usePackageForAllLocalOutcome() {
      localOutcome().setDecisionForAll("use_package", false);
    }

    function useCurrentForAllLocalOutcomeConflicts() {
      localOutcome().setDecisionForAll("use_current", true);
    }

    async function applyLocalOutcomeSetPackageDecisions() {
      await localOutcome().applyDecisions();
    }

    async function commitLocalOutcomeSetPackageResolution() {
      await localOutcome().commitResolution();
    }

    function renderPortableLocalOutcomeThreeWayMergeResult() {
      panels().renderPortableLocalOutcomeThreeWayMergeResult();
    }

    function renderPortableLocalOutcomeMergeDecisionList() {
      panels().renderPortableLocalOutcomeMergeDecisionList();
    }

    function renderPortableLocalOutcomeMergeResolutionResult() {
      panels().renderPortableLocalOutcomeMergeResolutionResult();
    }

    function renderPortableLocalOutcomeMergeCommitResult() {
      panels().renderPortableLocalOutcomeMergeCommitResult();
    }

    function renderPortableLocalOutcomeWorkstation() {
      panels().renderPortableLocalOutcomeWorkstation();
    }

    async function compareBaselineOrThreeWayPortableLocalOutcome() {
      await portableMerge().compareBaselineOrThreeWayPortableLocalOutcome();
    }

    function useLeftForAllPortableLocalMerge() {
      portableMerge().setDecisionForAll("use_left", false);
    }

    function useRightForAllPortableLocalMerge() {
      portableMerge().setDecisionForAll("use_right", true);
    }

    async function applyPortableLocalOutcomeMergeDecisions() {
      await portableMerge().applyDecisions();
    }

    async function commitPortableLocalOutcomeMergeResolution() {
      await portableMerge().commitResolution();
    }

    function renderCompareResult() {
      panels().renderCompareResult();
    }

    async function compareSessions() {
      await operations().compareSessions();
    }

    function renderMergeResult() {
      panels().renderMergeResult();
    }

    async function mergeSessionsThreeWay() {
      await operations().mergeSessionsThreeWay();
    }

    function renderResolvedMergeResult() {
      panels().renderResolvedMergeResult();
    }

    function useLeftForAllConflicts() {
      operations().setAllConflictChoices("left");
    }

    function useRightForAllConflicts() {
      operations().setAllConflictChoices("right");
    }

    async function applyMergeDecisions() {
      await operations().applyMergeDecisions();
    }

    function renderMergeCommitResult() {
      panels().renderMergeCommitResult();
    }

    async function commitMergedSessionToWorkspace() {
      await operations().commitMergedSessionToWorkspace();
    }

    function renderBranchRebaseResult() {
      panels().renderBranchRebaseResult();
    }

    async function rebaseBranchOntoTarget() {
      await operations().rebaseBranchOntoTarget();
    }

    function renderBranchResetResult() {
      panels().renderBranchResetResult();
    }

    function updateResetTargetSessions() {
      panels().updateResetTargetSessions();
    }

    async function resetBranchHeadToHistoricalPoint() {
      await operations().resetBranchHeadToHistoricalPoint();
    }

    function renderBranchCherryPickResult() {
      panels().renderBranchCherryPickResult();
    }

    async function cherryPickSelectedSessions() {
      await operations().cherryPickSelectedSessions();
    }

    function renderBranchSquashResult() {
      panels().renderBranchSquashResult();
    }

    async function squashSelectedSessions() {
      await operations().squashSelectedSessions();
    }

    return {
      analyze,
      importTextToGraph,
      analyzeGraph,
      clearAll,
      loadSamples,
      addEntity,
      setRoot,
      deleteSelected,
      saveSelectedEntity,
      addEdge,
      exportTextSession,
      exportGraphSession,
      importSession,
      downloadSession,
      addCurrentToProject,
      renderGraph,
      renderProjectSessions,
      exportProject,
      downloadProject,
      importProject,
      clearProject,
      createBranchFromActiveSession,
      renderTagPointList,
      renderTagPointResult,
      createTagReleasePoint,
      renderSnapshotList,
      renderSnapshotResult,
      createSnapshotExport,
      downloadCurrentSnapshot,
      updateSnapshotSelectors,
      updateTagTargetSessions,
      renderSnapshotRestorePreview,
      updateSnapshotPackageGuidance,
      syncReconcileCommitPackageExportAutofill,
      syncLocalOutcomeSetPackageExportAutofill,
      previewSnapshotRestoreBeforeApply,
      renderSnapshotRestoreResult,
      useCurrentSnapshotForRestore,
      clearSnapshotRestoreInput,
      restoreWorkspaceFromSnapshot,
      renderPartialImportResult,
      useCurrentSnapshotForPartialImport,
      clearPartialImportInput,
      partialImportFromSnapshot,
      renderSnapshotReconcileList,
      renderSnapshotReconcilePreview,
      updateSnapshotReconcileSessionHint,
      renderSnapshotReconcileResult,
      useCurrentSnapshotForReconcile,
      clearSnapshotReconcileInput,
      previewSnapshotReconcileBeforeApply,
      reconcileSnapshotIntoLineage,
      useSnapshotForAllReconcile,
      useCurrentForAllSnapshotConflicts,
      applySnapshotReconcileDecisions,
      renderSnapshotReconcileCommitList,
      renderSnapshotReconcileCommitResult,
      commitSnapshotReconcileResolution,
      renderSnapshotReconcileCommitCompareResult,
      updateSnapshotReconcileCommitCompareSelectors,
      comparePromotedReconcileOutcomes,
      renderReconcileCommitPackageList,
      renderReconcileCommitPackagePreview,
      renderReconcileCommitPackageDecisionList,
      renderReconcileCommitPackageResult,
      updateReconcileCommitPackageGuidance,
      exportReconcileCommitPackage,
      useCurrentReconcileCommitPackage,
      previewReconcileCommitPackageImport,
      importReconcileCommitPackage,
      clearReconcileCommitPackageInput,
      usePackageForAllImport,
      useCurrentForImportConflicts,
      applyReconcileCommitPackageDecisions,
      commitReconcileCommitPackageResolution,
      renderLocalOutcomeSetPackageList,
      renderLocalOutcomeSetPackagePreviewResult,
      renderLocalOutcomeSetPackageDecisionList,
      renderLocalOutcomeSetPackageResult,
      updateLocalOutcomeSetPackageGuidance,
      exportLocalOutcomeSetPackage,
      useCurrentLocalOutcomeSetPackage,
      previewLocalOutcomeSetPackageImport,
      importLocalOutcomeSetPackage,
      clearLocalOutcomeSetPackageInput,
      usePackageForAllLocalOutcome,
      useCurrentForAllLocalOutcomeConflicts,
      applyLocalOutcomeSetPackageDecisions,
      commitLocalOutcomeSetPackageResolution,
      renderPortableLocalOutcomeThreeWayMergeResult,
      renderPortableLocalOutcomeMergeDecisionList,
      renderPortableLocalOutcomeMergeResolutionResult,
      renderPortableLocalOutcomeMergeCommitResult,
      renderPortableLocalOutcomeWorkstation,
      compareBaselineOrThreeWayPortableLocalOutcome,
      useLeftForAllPortableLocalMerge,
      useRightForAllPortableLocalMerge,
      applyPortableLocalOutcomeMergeDecisions,
      commitPortableLocalOutcomeMergeResolution,
      renderCompareResult,
      compareSessions,
      renderMergeResult,
      mergeSessionsThreeWay,
      renderResolvedMergeResult,
      useLeftForAllConflicts,
      useRightForAllConflicts,
      applyMergeDecisions,
      renderMergeCommitResult,
      commitMergedSessionToWorkspace,
      renderBranchRebaseResult,
      rebaseBranchOntoTarget,
      renderBranchResetResult,
      updateResetTargetSessions,
      resetBranchHeadToHistoricalPoint,
      renderBranchCherryPickResult,
      cherryPickSelectedSessions,
      renderBranchSquashResult,
      squashSelectedSessions,
    };
  }

  window.InspectorActionWorkflow = {
    createInspectorActionController,
  };
})();
