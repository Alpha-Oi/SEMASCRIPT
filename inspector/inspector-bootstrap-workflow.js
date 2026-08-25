(function () {
  function createInspectorBootstrapController(config) {
    const {
      els,
      getPreviewMode,
      setPreviewMode,
      renderSvg,
      actions,
      initializers,
    } = config;

    let isBound = false;

    function bind(element, eventName, handler) {
      if (!element || !handler) return;
      element.addEventListener(eventName, handler);
    }

    function bindSvgTabs() {
      document.querySelectorAll(".svg-tab").forEach((button) => {
        bind(button, "click", () => {
          document.querySelectorAll(".svg-tab").forEach((element) => element.classList.remove("active"));
          button.classList.add("active");
          setPreviewMode(button.dataset.preview || getPreviewMode());
          renderSvg();
        });
      });
    }

    function bindEventHandlers() {
      if (isBound) return;
      isBound = true;

      bindSvgTabs();
      bind(els.analyzeBtn, "click", actions.analyze);
      bind(els.importGraphBtn, "click", actions.importTextToGraph);
      bind(els.analyzeGraphBtn, "click", actions.analyzeGraph);
      bind(els.clearBtn, "click", actions.clearAll);
      bind(els.reloadSamples, "click", actions.loadSamples);
      bind(els.addEntityBtn, "click", actions.addEntity);
      bind(els.setRootBtn, "click", actions.setRoot);
      bind(els.deleteEntityBtn, "click", actions.deleteSelected);
      bind(els.saveEntityBtn, "click", actions.saveSelectedEntity);
      bind(els.addEdgeBtn, "click", actions.addEdge);
      bind(els.exportTextSessionBtn, "click", actions.exportTextSession);
      bind(els.exportGraphSessionBtn, "click", actions.exportGraphSession);
      bind(els.importSessionBtn, "click", actions.importSession);
      bind(els.downloadSessionBtn, "click", actions.downloadSession);
      bind(els.addCurrentToProjectBtn, "click", actions.addCurrentToProject);
      bind(els.exportProjectBtn, "click", actions.exportProject);
      bind(els.downloadProjectBtn, "click", actions.downloadProject);
      bind(els.importProjectBtn, "click", actions.importProject);
      bind(els.reloadProjectBtn, "click", actions.renderProjectSessions);
      bind(els.clearProjectBtn, "click", actions.clearProject);
      bind(els.createBranchBtn, "click", actions.createBranchFromActiveSession);
      bind(els.createTagPointBtn, "click", actions.createTagReleasePoint);
      bind(els.createSnapshotBtn, "click", actions.createSnapshotExport);
      bind(els.downloadSnapshotBtn, "click", actions.downloadCurrentSnapshot);
      bind(els.refreshSnapshotSelectorsBtn, "click", actions.updateSnapshotSelectors);
      bind(els.snapshotRestoreJson, "input", actions.updateSnapshotPackageGuidance);
      bind(els.snapshotRestoreJson, "input", actions.updateSnapshotReconcileSessionHint);
      bind(els.partialImportSessionIds, "input", actions.updateSnapshotPackageGuidance);
      bind(els.partialImportTagNames, "input", actions.updateSnapshotPackageGuidance);
      bind(els.partialImportSnapshotNames, "input", actions.updateSnapshotPackageGuidance);
      bind(els.loadCurrentSnapshotForRestoreBtn, "click", actions.useCurrentSnapshotForRestore);
      bind(els.previewSnapshotRestoreBtn, "click", actions.previewSnapshotRestoreBeforeApply);
      bind(els.restoreFromSnapshotBtn, "click", actions.restoreWorkspaceFromSnapshot);
      bind(els.clearSnapshotRestoreBtn, "click", actions.clearSnapshotRestoreInput);
      bind(els.useCurrentSnapshotForPartialBtn, "click", actions.useCurrentSnapshotForPartialImport);
      bind(els.partialImportFromSnapshotBtn, "click", actions.partialImportFromSnapshot);
      bind(els.clearPartialImportBtn, "click", actions.clearPartialImportInput);
      bind(els.snapshotReconcileSessionIds, "input", actions.updateSnapshotReconcileSessionHint);
      bind(els.useCurrentSnapshotForReconcileBtn, "click", actions.useCurrentSnapshotForReconcile);
      bind(els.previewSnapshotReconcileBtn, "click", actions.previewSnapshotReconcileBeforeApply);
      bind(els.reconcileSnapshotBtn, "click", actions.reconcileSnapshotIntoLineage);
      bind(els.clearSnapshotReconcileBtn, "click", actions.clearSnapshotReconcileInput);
      bind(els.applySnapshotReconcileDecisionsBtn, "click", actions.applySnapshotReconcileDecisions);
      bind(els.useSnapshotForAllReconcileBtn, "click", actions.useSnapshotForAllReconcile);
      bind(els.useCurrentForAllConflictsBtn, "click", actions.useCurrentForAllSnapshotConflicts);
      bind(els.commitSnapshotReconcileBtn, "click", actions.commitSnapshotReconcileResolution);
      bind(els.compareReconcileCommitsBtn, "click", actions.comparePromotedReconcileOutcomes);
      bind(els.importReconcileCommitPackageJson, "input", actions.updateReconcileCommitPackageGuidance);
      bind(els.exportReconcileCommitName, "change", actions.syncReconcileCommitPackageExportAutofill);
      bind(els.exportReconcileCommitPackageBtn, "click", actions.exportReconcileCommitPackage);
      bind(els.useCurrentReconcileCommitPackageBtn, "click", actions.useCurrentReconcileCommitPackage);
      bind(els.previewReconcileCommitPackageBtn, "click", actions.previewReconcileCommitPackageImport);
      bind(els.importReconcileCommitPackageBtn, "click", actions.importReconcileCommitPackage);
      bind(els.clearReconcileCommitPackageBtn, "click", actions.clearReconcileCommitPackageInput);
      bind(els.usePackageForAllImportBtn, "click", actions.usePackageForAllImport);
      bind(els.useCurrentForImportConflictsBtn, "click", actions.useCurrentForImportConflicts);
      bind(els.applyReconcileCommitPackageDecisionsBtn, "click", actions.applyReconcileCommitPackageDecisions);
      bind(els.commitReconcileCommitPackageBtn, "click", actions.commitReconcileCommitPackageResolution);
      bind(els.importLocalOutcomeSetPackageJson, "input", actions.updateLocalOutcomeSetPackageGuidance);
      bind(els.exportLocalOutcomeSetCommit, "change", actions.syncLocalOutcomeSetPackageExportAutofill);
      bind(els.exportLocalOutcomeSetPackageBtn, "click", actions.exportLocalOutcomeSetPackage);
      bind(els.useCurrentLocalOutcomeSetPackageBtn, "click", actions.useCurrentLocalOutcomeSetPackage);
      bind(els.previewLocalOutcomeSetPackageBtn, "click", actions.previewLocalOutcomeSetPackageImport);
      bind(els.importLocalOutcomeSetPackageBtn, "click", actions.importLocalOutcomeSetPackage);
      bind(els.clearLocalOutcomeSetPackageBtn, "click", actions.clearLocalOutcomeSetPackageInput);
      bind(els.usePackageForAllLocalOutcomeBtn, "click", actions.usePackageForAllLocalOutcome);
      bind(els.useCurrentForAllLocalOutcomeConflictsBtn, "click", actions.useCurrentForAllLocalOutcomeConflicts);
      bind(els.applyLocalOutcomePackageDecisionsBtn, "click", actions.applyLocalOutcomeSetPackageDecisions);
      bind(els.commitLocalOutcomeSetPackageBtn, "click", actions.commitLocalOutcomeSetPackageResolution);
      bind(els.compareThreeWayPortableLocalOutcomeBtn, "click", actions.compareBaselineOrThreeWayPortableLocalOutcome);
      bind(els.useLeftForAllPortableLocalMergeBtn, "click", actions.useLeftForAllPortableLocalMerge);
      bind(els.useRightForAllPortableLocalMergeConflictsBtn, "click", actions.useRightForAllPortableLocalMerge);
      bind(els.applyPortableLocalOutcomeMergeDecisionsBtn, "click", actions.applyPortableLocalOutcomeMergeDecisions);
      bind(els.commitPortableLocalOutcomeMergeBtn, "click", actions.commitPortableLocalOutcomeMergeResolution);
      bind(els.rebaseBranchBtn, "click", actions.rebaseBranchOntoTarget);
      bind(els.resetBranchHeadBtn, "click", actions.resetBranchHeadToHistoricalPoint);
      bind(els.resetBranchName, "change", actions.updateResetTargetSessions);
      bind(els.cherryPickSessionsBtn, "click", actions.cherryPickSelectedSessions);
      bind(els.squashSessionsBtn, "click", actions.squashSelectedSessions);
      bind(els.compareSessionsBtn, "click", actions.compareSessions);
      bind(els.mergeSessionsBtn, "click", actions.mergeSessionsThreeWay);
      bind(els.applyMergeDecisionsBtn, "click", actions.applyMergeDecisions);
      bind(els.useLeftForAllConflictsBtn, "click", actions.useLeftForAllConflicts);
      bind(els.useRightForAllConflictsBtn, "click", actions.useRightForAllConflicts);
      bind(els.commitMergedSessionBtn, "click", actions.commitMergedSessionToWorkspace);
    }

    function initialize() {
      initializers.loadSamples();
      initializers.renderGraph();
      initializers.renderProjectSessions();
      initializers.renderTagPointList();
      initializers.renderSnapshotList();
      initializers.renderTagPointResult();
      initializers.renderSnapshotResult();
      initializers.renderSnapshotRestorePreview();
      initializers.renderSnapshotRestoreResult();
      initializers.updateSnapshotPackageGuidance();
      initializers.renderPartialImportResult();
      initializers.updateSnapshotReconcileSessionHint();
      initializers.updateTagTargetSessions();
      initializers.updateSnapshotSelectors();
      initializers.renderPortableLocalOutcomeThreeWayMergeResult();
      initializers.renderPortableLocalOutcomeMergeResolutionResult();
      initializers.renderPortableLocalOutcomeMergeCommitResult();
      initializers.renderPortableLocalOutcomeWorkstation();
      initializers.renderSnapshotReconcileCommitCompareResult();
      initializers.updateSnapshotReconcileCommitCompareSelectors();
      initializers.updateReconcileCommitPackageGuidance();
      initializers.updateLocalOutcomeSetPackageGuidance();
    }

    return {
      bindEventHandlers,
      initialize,
    };
  }

  window.InspectorBootstrapWorkflow = {
    createInspectorBootstrapController,
  };
})();
