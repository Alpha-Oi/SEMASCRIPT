(function () {
  function createInspectorPanelController(config) {
    const {
      els,
      getCurrentBranchSummary,
      getProjectOperationsController,
      getProjectWorkspaceController,
      getProjectLifecycleController,
      getSnapshotReconcileController,
      getReconcileCommitPackageController,
      getLocalOutcomeSetPackageController,
      getPortableLocalOutcomeMergeController,
    } = config;

    function updatePartialImportSelectors() {
      if (!els.partialImportTargetBranch) return;
      const branches = getCurrentBranchSummary() || [];
      const previousValue = els.partialImportTargetBranch.value;
      els.partialImportTargetBranch.innerHTML = "";
      for (const branch of branches) {
        const option = document.createElement("option");
        option.value = branch.branch_name;
        option.textContent = branch.branch_name;
        if (branch.branch_name === previousValue || (!previousValue && branch.is_active_branch)) {
          option.selected = true;
        }
        els.partialImportTargetBranch.appendChild(option);
      }
    }

    return {
      renderMergeCommitResult: () => getProjectOperationsController().renderMergeCommitResult(),
      renderResolvedMergeResult: () => getProjectOperationsController().renderResolvedMergeResult(),
      updateMergeSelectors: () => getProjectOperationsController().updateMergeSelectors(),
      renderMergeResult: () => getProjectOperationsController().renderMergeResult(),
      updateCompareSelectors: () => getProjectOperationsController().updateCompareSelectors(),
      renderCompareResult: () => getProjectOperationsController().renderCompareResult(),
      renderProjectTimeline: () => getProjectWorkspaceController().renderProjectTimeline(),
      renderProjectMap: () => getProjectWorkspaceController().renderProjectMap(),
      updateSquashSelectors: () => getProjectOperationsController().updateSquashSelectors(),
      renderBranchSquashResult: () => getProjectOperationsController().renderBranchSquashResult(),
      updateCherryPickSelectors: () => getProjectOperationsController().updateCherryPickSelectors(),
      renderBranchCherryPickResult: () => getProjectOperationsController().renderBranchCherryPickResult(),
      updateResetSelectors: () => getProjectOperationsController().updateResetSelectors(),
      updateResetTargetSessions: () => getProjectOperationsController().updateResetTargetSessions(),
      renderBranchResetResult: () => getProjectOperationsController().renderBranchResetResult(),
      updateRebaseSelectors: () => getProjectOperationsController().updateRebaseSelectors(),
      renderBranchRebaseResult: () => getProjectOperationsController().renderBranchRebaseResult(),
      updateTagTargetSessions: () => getProjectLifecycleController().updateTagTargetSessions(),
      renderPartialImportResult: () => getProjectLifecycleController().renderPartialImportResult(),
      updatePartialImportSelectors,
      renderSnapshotReconcileDecisionList: () => getSnapshotReconcileController().renderDecisionList(),
      updateSnapshotReconcileSelectors: () => getSnapshotReconcileController().updateSelectors(),
      updateSnapshotReconcileCommitCompareSelectors: () => getSnapshotReconcileController().updateCommitCompareSelectors(),
      renderSnapshotReconcileCommitCompareResult: () => getSnapshotReconcileController().renderCommitCompareResult(),
      updateReconcileCommitPackageSelectors: () => getReconcileCommitPackageController().updateSelectors(),
      renderReconcileCommitPackageDecisionList: () => getReconcileCommitPackageController().renderDecisionList(),
      renderReconcileCommitPackagePreview: () => getReconcileCommitPackageController().renderPreview(),
      renderReconcileCommitPackageList: () => getReconcileCommitPackageController().renderList(),
      updateLocalOutcomeSetPackageSelectors: () => getLocalOutcomeSetPackageController().updateSelectors(),
      renderLocalOutcomeSetPackageList: () => getLocalOutcomeSetPackageController().renderList(),
      renderLocalOutcomeSetPackagePreviewResult: () => getLocalOutcomeSetPackageController().renderPreviewResult(),
      renderLocalOutcomeSetPackageDecisionList: () => getLocalOutcomeSetPackageController().renderDecisionList(),
      renderPortableLocalOutcomeWorkstation: () => getPortableLocalOutcomeMergeController().renderWorkstation(),
      updatePortableLocalOutcomeMergeSelectors: () => getPortableLocalOutcomeMergeController().updateSelectors(),
      renderPortableLocalOutcomeThreeWayMergeResult: () => getPortableLocalOutcomeMergeController().renderThreeWayMergeResult(),
      renderPortableLocalOutcomeMergeDecisionList: () => getPortableLocalOutcomeMergeController().renderDecisionList(),
      renderPortableLocalOutcomeMergeResolutionResult: () => getPortableLocalOutcomeMergeController().renderResolutionResult(),
      renderPortableLocalOutcomeMergeCommitResult: () => getPortableLocalOutcomeMergeController().renderCommitResult(),
      renderLocalOutcomeSetPackageResult: () => getLocalOutcomeSetPackageController().renderResultPanel(),
      renderReconcileCommitPackageResult: () => getReconcileCommitPackageController().renderResultPanel(),
      renderSnapshotReconcileCommitList: () => getSnapshotReconcileController().renderCommitList(),
      renderSnapshotReconcileCommitResult: () => getSnapshotReconcileController().renderCommitResult(),
      renderSnapshotReconcileList: () => getSnapshotReconcileController().renderList(),
      renderSnapshotReconcilePreview: () => getSnapshotReconcileController().renderPreview(),
      renderSnapshotReconcileResult: () => getSnapshotReconcileController().renderReconcileResult(),
      renderSnapshotRestorePreview: () => getProjectLifecycleController().renderSnapshotRestorePreview(),
      renderSnapshotRestoreResult: () => getProjectLifecycleController().renderSnapshotRestoreResult(),
      updateSnapshotSelectors: () => getProjectLifecycleController().updateSnapshotSelectors(),
      renderSnapshotList: () => getProjectLifecycleController().renderSnapshotList(),
      renderSnapshotResult: () => getProjectLifecycleController().renderSnapshotResult(),
      renderTagPointList: () => getProjectLifecycleController().renderTagPointList(),
      renderTagPointResult: () => getProjectLifecycleController().renderTagPointResult(),
      renderBranchList: () => getProjectWorkspaceController().renderBranchList(),
      renderLineageGraph: () => getProjectWorkspaceController().renderLineageGraph(),
      renderProjectSessions: () => getProjectWorkspaceController().renderProjectSessions(),
    };
  }

  window.InspectorPanelWorkflow = {
    createInspectorPanelController,
  };
})();
