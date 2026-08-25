
const els = {
  profile: document.getElementById("profile"),
  profileHint: document.getElementById("profileHint"),
  decompose: document.getElementById("decompose"),
  sessionName: document.getElementById("sessionName"),
  projectName: document.getElementById("projectName"),
  inputText: document.getElementById("inputText"),
  initialState: document.getElementById("initialState"),
  sessionJson: document.getElementById("sessionJson"),
  projectJson: document.getElementById("projectJson"),
  analyzeBtn: document.getElementById("analyzeBtn"),
  importGraphBtn: document.getElementById("importGraphBtn"),
  clearBtn: document.getElementById("clearBtn"),
  reloadSamples: document.getElementById("reloadSamples"),
  exportTextSessionBtn: document.getElementById("exportTextSessionBtn"),
  exportGraphSessionBtn: document.getElementById("exportGraphSessionBtn"),
  downloadSessionBtn: document.getElementById("downloadSessionBtn"),
  importSessionBtn: document.getElementById("importSessionBtn"),
  addCurrentToProjectBtn: document.getElementById("addCurrentToProjectBtn"),
  exportProjectBtn: document.getElementById("exportProjectBtn"),
  downloadProjectBtn: document.getElementById("downloadProjectBtn"),
  importProjectBtn: document.getElementById("importProjectBtn"),
  reloadProjectBtn: document.getElementById("reloadProjectBtn"),
  clearProjectBtn: document.getElementById("clearProjectBtn"),
  projectSessionsList: document.getElementById("projectSessionsList"),
  newBranchName: document.getElementById("newBranchName"),
  createBranchBtn: document.getElementById("createBranchBtn"),
  branchList: document.getElementById("branchList"),
  tagPointName: document.getElementById("tagPointName"),
  tagPointKind: document.getElementById("tagPointKind"),
  tagTargetSession: document.getElementById("tagTargetSession"),
  tagPointNote: document.getElementById("tagPointNote"),
  createTagPointBtn: document.getElementById("createTagPointBtn"),
  tagPointList: document.getElementById("tagPointList"),
  tagPointResultText: document.getElementById("tagPointResultText"),
  snapshotSourcePoint: document.getElementById("snapshotSourcePoint"),
  snapshotName: document.getElementById("snapshotName"),
  snapshotNote: document.getElementById("snapshotNote"),
  createSnapshotBtn: document.getElementById("createSnapshotBtn"),
  downloadSnapshotBtn: document.getElementById("downloadSnapshotBtn"),
  refreshSnapshotSelectorsBtn: document.getElementById("refreshSnapshotSelectorsBtn"),
  snapshotList: document.getElementById("snapshotList"),
  snapshotResultText: document.getElementById("snapshotResultText"),
  snapshotRestoreJson: document.getElementById("snapshotRestoreJson"),
  snapshotPackageHint: document.getElementById("snapshotPackageHint"),
  restoredProjectName: document.getElementById("restoredProjectName"),
  snapshotRestoreName: document.getElementById("snapshotRestoreName"),
  activateRestoredAnchor: document.getElementById("activateRestoredAnchor"),
  loadCurrentSnapshotForRestoreBtn: document.getElementById("loadCurrentSnapshotForRestoreBtn"),
  previewSnapshotRestoreBtn: document.getElementById("previewSnapshotRestoreBtn"),
  restoreFromSnapshotBtn: document.getElementById("restoreFromSnapshotBtn"),
  clearSnapshotRestoreBtn: document.getElementById("clearSnapshotRestoreBtn"),
  snapshotRestorePreviewText: document.getElementById("snapshotRestorePreviewText"),
  snapshotRestoreResultText: document.getElementById("snapshotRestoreResultText"),
  partialImportSessionIds: document.getElementById("partialImportSessionIds"),
  partialImportTagNames: document.getElementById("partialImportTagNames"),
  partialImportSnapshotNames: document.getElementById("partialImportSnapshotNames"),
  partialImportSelectionHint: document.getElementById("partialImportSelectionHint"),
  partialImportTargetBranch: document.getElementById("partialImportTargetBranch"),
  partialImportName: document.getElementById("partialImportName"),
  activatePartialImportHead: document.getElementById("activatePartialImportHead"),
  useCurrentSnapshotForPartialBtn: document.getElementById("useCurrentSnapshotForPartialBtn"),
  partialImportFromSnapshotBtn: document.getElementById("partialImportFromSnapshotBtn"),
  clearPartialImportBtn: document.getElementById("clearPartialImportBtn"),
  partialImportResultText: document.getElementById("partialImportResultText"),
  snapshotReconcileSessionIds: document.getElementById("snapshotReconcileSessionIds"),
  snapshotReconcileSessionHint: document.getElementById("snapshotReconcileSessionHint"),
  snapshotReconcileTargetBranch: document.getElementById("snapshotReconcileTargetBranch"),
  snapshotReconcileName: document.getElementById("snapshotReconcileName"),
  activateSnapshotReconcileHead: document.getElementById("activateSnapshotReconcileHead"),
  useCurrentSnapshotForReconcileBtn: document.getElementById("useCurrentSnapshotForReconcileBtn"),
  previewSnapshotReconcileBtn: document.getElementById("previewSnapshotReconcileBtn"),
  reconcileSnapshotBtn: document.getElementById("reconcileSnapshotBtn"),
  clearSnapshotReconcileBtn: document.getElementById("clearSnapshotReconcileBtn"),
  snapshotReconcileList: document.getElementById("snapshotReconcileList"),
  snapshotReconcilePreviewText: document.getElementById("snapshotReconcilePreviewText"),
  snapshotReconcileDecisionList: document.getElementById("snapshotReconcileDecisionList"),
  useSnapshotForAllReconcileBtn: document.getElementById("useSnapshotForAllReconcileBtn"),
  useCurrentForAllConflictsBtn: document.getElementById("useCurrentForAllConflictsBtn"),
  applySnapshotReconcileDecisionsBtn: document.getElementById("applySnapshotReconcileDecisionsBtn"),
  snapshotReconcileResultText: document.getElementById("snapshotReconcileResultText"),
  snapshotReconcileCommitName: document.getElementById("snapshotReconcileCommitName"),
  snapshotReconcilePromotePointName: document.getElementById("snapshotReconcilePromotePointName"),
  snapshotReconcilePromotePointKind: document.getElementById("snapshotReconcilePromotePointKind"),
  snapshotReconcileCommitNote: document.getElementById("snapshotReconcileCommitNote"),
  commitSnapshotReconcileBtn: document.getElementById("commitSnapshotReconcileBtn"),
  snapshotReconcileCommitList: document.getElementById("snapshotReconcileCommitList"),
  snapshotReconcileCommitResultText: document.getElementById("snapshotReconcileCommitResultText"),
  compareReconcileCommitLeft: document.getElementById("compareReconcileCommitLeft"),
  compareReconcileCommitRight: document.getElementById("compareReconcileCommitRight"),
  compareReconcileCommitsBtn: document.getElementById("compareReconcileCommitsBtn"),
  compareReconcileCommitResultText: document.getElementById("compareReconcileCommitResultText"),
  exportReconcileCommitName: document.getElementById("exportReconcileCommitName"),
  exportReconcileCommitPackageName: document.getElementById("exportReconcileCommitPackageName"),
  exportReconcileCommitPackageBtn: document.getElementById("exportReconcileCommitPackageBtn"),
  reconcileCommitPackageCurrentSummary: document.getElementById("reconcileCommitPackageCurrentSummary"),
  importReconcileCommitPackageJson: document.getElementById("importReconcileCommitPackageJson"),
  reconcileCommitPackageHint: document.getElementById("reconcileCommitPackageHint"),
  importReconcileCommitPackageName: document.getElementById("importReconcileCommitPackageName"),
  importReconcileCommitTargetBranch: document.getElementById("importReconcileCommitTargetBranch"),
  activateImportedReconcileCommit: document.getElementById("activateImportedReconcileCommit"),
  useCurrentReconcileCommitPackageBtn: document.getElementById("useCurrentReconcileCommitPackageBtn"),
  previewReconcileCommitPackageBtn: document.getElementById("previewReconcileCommitPackageBtn"),
  importReconcileCommitPackageBtn: document.getElementById("importReconcileCommitPackageBtn"),
  clearReconcileCommitPackageBtn: document.getElementById("clearReconcileCommitPackageBtn"),
  reconcileCommitPackageList: document.getElementById("reconcileCommitPackageList"),
  reconcileCommitPackagePreviewText: document.getElementById("reconcileCommitPackagePreviewText"),
  reconcileCommitPackageDecisionList: document.getElementById("reconcileCommitPackageDecisionList"),
  usePackageForAllImportBtn: document.getElementById("usePackageForAllImportBtn"),
  useCurrentForImportConflictsBtn: document.getElementById("useCurrentForImportConflictsBtn"),
  applyReconcileCommitPackageDecisionsBtn: document.getElementById("applyReconcileCommitPackageDecisionsBtn"),
  reconcileCommitPackageResultText: document.getElementById("reconcileCommitPackageResultText"),
  reconcileCommitPackageCommitName: document.getElementById("reconcileCommitPackageCommitName"),
  reconcileCommitPackagePromotePointName: document.getElementById("reconcileCommitPackagePromotePointName"),
  reconcileCommitPackagePromotePointKind: document.getElementById("reconcileCommitPackagePromotePointKind"),
  reconcileCommitPackageCommitNote: document.getElementById("reconcileCommitPackageCommitNote"),
  commitReconcileCommitPackageBtn: document.getElementById("commitReconcileCommitPackageBtn"),
  exportLocalOutcomeSetCommit: document.getElementById("exportLocalOutcomeSetCommit"),
  localOutcomeSetPackageName: document.getElementById("localOutcomeSetPackageName"),
  localOutcomeSetPackageNote: document.getElementById("localOutcomeSetPackageNote"),
  exportLocalOutcomeSetPackageBtn: document.getElementById("exportLocalOutcomeSetPackageBtn"),
  localOutcomeSetPackageCurrentSummary: document.getElementById("localOutcomeSetPackageCurrentSummary"),
  importLocalOutcomeSetPackageJson: document.getElementById("importLocalOutcomeSetPackageJson"),
  localOutcomeSetPackageHint: document.getElementById("localOutcomeSetPackageHint"),
  importLocalOutcomeSetPackageNameInput: document.getElementById("importLocalOutcomeSetPackageNameInput"),
  importLocalOutcomeSetTargetBranch: document.getElementById("importLocalOutcomeSetTargetBranch"),
  activateImportedLocalOutcomeSet: document.getElementById("activateImportedLocalOutcomeSet"),
  useCurrentLocalOutcomeSetPackageBtn: document.getElementById("useCurrentLocalOutcomeSetPackageBtn"),
  previewLocalOutcomeSetPackageBtn: document.getElementById("previewLocalOutcomeSetPackageBtn"),
  importLocalOutcomeSetPackageBtn: document.getElementById("importLocalOutcomeSetPackageBtn"),
  clearLocalOutcomeSetPackageBtn: document.getElementById("clearLocalOutcomeSetPackageBtn"),
  localOutcomeSetPackageList: document.getElementById("localOutcomeSetPackageList"),
  localOutcomeSetPackagePreviewResultText: document.getElementById("localOutcomeSetPackagePreviewResultText"),
  localOutcomeSetPackageDecisionList: document.getElementById("localOutcomeSetPackageDecisionList"),
  usePackageForAllLocalOutcomeBtn: document.getElementById("usePackageForAllLocalOutcomeBtn"),
  useCurrentForAllLocalOutcomeConflictsBtn: document.getElementById("useCurrentForAllLocalOutcomeConflictsBtn"),
  applyLocalOutcomePackageDecisionsBtn: document.getElementById("applyLocalOutcomePackageDecisionsBtn"),
  localOutcomeSetPackageCommitName: document.getElementById("localOutcomeSetPackageCommitName"),
  localOutcomeSetPackagePromotePointName: document.getElementById("localOutcomeSetPackagePromotePointName"),
  localOutcomeSetPackagePromotePointKind: document.getElementById("localOutcomeSetPackagePromotePointKind"),
  localOutcomeSetPackageCommitNote: document.getElementById("localOutcomeSetPackageCommitNote"),
  commitLocalOutcomeSetPackageBtn: document.getElementById("commitLocalOutcomeSetPackageBtn"),
  localOutcomeSetPackageResultText: document.getElementById("localOutcomeSetPackageResultText"),
  basePortableLocalOutcomeCommit: document.getElementById("basePortableLocalOutcomeCommit"),
  leftPortableLocalOutcomeCommit: document.getElementById("leftPortableLocalOutcomeCommit"),
  rightPortableLocalOutcomeCommit: document.getElementById("rightPortableLocalOutcomeCommit"),
  compareThreeWayPortableLocalOutcomeBtn: document.getElementById("compareThreeWayPortableLocalOutcomeBtn"),
  portableLocalOutcomeThreeWayMergeResultText: document.getElementById("portableLocalOutcomeThreeWayMergeResultText"),
  portableLocalOutcomeMergeResolutionName: document.getElementById("portableLocalOutcomeMergeResolutionName"),
  portableLocalOutcomeMergeTargetBranch: document.getElementById("portableLocalOutcomeMergeTargetBranch"),
  portableLocalOutcomeMergeDecisionList: document.getElementById("portableLocalOutcomeMergeDecisionList"),
  useLeftForAllPortableLocalMergeBtn: document.getElementById("useLeftForAllPortableLocalMergeBtn"),
  useRightForAllPortableLocalMergeConflictsBtn: document.getElementById("useRightForAllPortableLocalMergeConflictsBtn"),
  applyPortableLocalOutcomeMergeDecisionsBtn: document.getElementById("applyPortableLocalOutcomeMergeDecisionsBtn"),
  portableLocalOutcomeMergeResolutionResultText: document.getElementById("portableLocalOutcomeMergeResolutionResultText"),
  portableLocalOutcomeMergeCommitName: document.getElementById("portableLocalOutcomeMergeCommitName"),
  portableLocalOutcomeMergePromotePointName: document.getElementById("portableLocalOutcomeMergePromotePointName"),
  portableLocalOutcomeMergePromotePointKind: document.getElementById("portableLocalOutcomeMergePromotePointKind"),
  portableLocalOutcomeMergeCommitNote: document.getElementById("portableLocalOutcomeMergeCommitNote"),
  commitPortableLocalOutcomeMergeBtn: document.getElementById("commitPortableLocalOutcomeMergeBtn"),
  portableLocalOutcomeMergeCommitResultText: document.getElementById("portableLocalOutcomeMergeCommitResultText"),
  portableMergeOverview: document.getElementById("portableMergeOverview"),
  portableMergeSessionList: document.getElementById("portableMergeSessionList"),
  portableMergeDetail: document.getElementById("portableMergeDetail"),
  portableMergeFocusMeta: document.getElementById("portableMergeFocusMeta"),
  portableMergeDecisionMeta: document.getElementById("portableMergeDecisionMeta"),
  rebaseSourceBranch: document.getElementById("rebaseSourceBranch"),
  rebaseTargetBranch: document.getElementById("rebaseTargetBranch"),
  activateRebasedHead: document.getElementById("activateRebasedHead"),
  rebaseBranchBtn: document.getElementById("rebaseBranchBtn"),
  rebaseResultText: document.getElementById("rebaseResultText"),
  resetBranchName: document.getElementById("resetBranchName"),
  resetTargetSession: document.getElementById("resetTargetSession"),
  activateResetHead: document.getElementById("activateResetHead"),
  resetBranchHeadBtn: document.getElementById("resetBranchHeadBtn"),
  branchResetResultText: document.getElementById("branchResetResultText"),
  cherryPickSessionIds: document.getElementById("cherryPickSessionIds"),
  cherryPickTargetBranch: document.getElementById("cherryPickTargetBranch"),
  activateCherryPickedHead: document.getElementById("activateCherryPickedHead"),
  cherryPickSessionsBtn: document.getElementById("cherryPickSessionsBtn"),
  cherryPickResultText: document.getElementById("cherryPickResultText"),
  squashSessionIds: document.getElementById("squashSessionIds"),
  squashTargetBranch: document.getElementById("squashTargetBranch"),
  squashSessionId: document.getElementById("squashSessionId"),
  squashSessionName: document.getElementById("squashSessionName"),
  activateSquashedHead: document.getElementById("activateSquashedHead"),
  squashSessionsBtn: document.getElementById("squashSessionsBtn"),
  squashResultText: document.getElementById("squashResultText"),
  projectDependencyMap: document.getElementById("projectDependencyMap"),
  projectTimeline: document.getElementById("projectTimeline"),
  projectLineageGraph: document.getElementById("projectLineageGraph"),
  compareLeftSession: document.getElementById("compareLeftSession"),
  compareRightSession: document.getElementById("compareRightSession"),
  compareSessionsBtn: document.getElementById("compareSessionsBtn"),
  compareResultText: document.getElementById("compareResultText"),
  mergeBaseSession: document.getElementById("mergeBaseSession"),
  mergeLeftSession: document.getElementById("mergeLeftSession"),
  mergeRightSession: document.getElementById("mergeRightSession"),
  mergeSessionsBtn: document.getElementById("mergeSessionsBtn"),
  mergeResultText: document.getElementById("mergeResultText"),
  mergeConflictList: document.getElementById("mergeConflictList"),
  useLeftForAllConflictsBtn: document.getElementById("useLeftForAllConflictsBtn"),
  useRightForAllConflictsBtn: document.getElementById("useRightForAllConflictsBtn"),
  applyMergeDecisionsBtn: document.getElementById("applyMergeDecisionsBtn"),
  resolvedMergeText: document.getElementById("resolvedMergeText"),
  mergeCommitSessionId: document.getElementById("mergeCommitSessionId"),
  mergeCommitSessionName: document.getElementById("mergeCommitSessionName"),
  mergeCommitBranchName: document.getElementById("mergeCommitBranchName"),
  activateCommittedSession: document.getElementById("activateCommittedSession"),
  commitMergedSessionBtn: document.getElementById("commitMergedSessionBtn"),
  mergeCommitResultText: document.getElementById("mergeCommitResultText"),
  samplesList: document.getElementById("samplesList"),
  statusText: document.getElementById("statusText"),
  normalizedText: document.getElementById("normalizedText"),
  validationText: document.getElementById("validationText"),
  astText: document.getElementById("astText"),
  graphJsonText: document.getElementById("graphJsonText"),
  runtimeText: document.getElementById("runtimeText"),
  stateText: document.getElementById("stateText"),
  svgPanel: document.getElementById("svgPanel"),
  graphWorkspace: document.getElementById("graphWorkspace"),
  graphEdges: document.getElementById("graphEdges"),
  graphNodes: document.getElementById("graphNodes"),
  graphMeta: document.getElementById("graphMeta"),
  analyzeGraphBtn: document.getElementById("analyzeGraphBtn"),
  newEntityKind: document.getElementById("newEntityKind"),
  addEntityBtn: document.getElementById("addEntityBtn"),
  setRootBtn: document.getElementById("setRootBtn"),
  deleteEntityBtn: document.getElementById("deleteEntityBtn"),
  edgeRoleInput: document.getElementById("edgeRoleInput"),
  edgeTargetSelect: document.getElementById("edgeTargetSelect"),
  addEdgeBtn: document.getElementById("addEdgeBtn"),
  entityId: document.getElementById("entityId"),
  entityKind: document.getElementById("entityKind"),
  entityClass: document.getElementById("entityClass"),
  entityRoot: document.getElementById("entityRoot"),
  entityValue: document.getElementById("entityValue"),
  entityModifiers: document.getElementById("entityModifiers"),
  saveEntityBtn: document.getElementById("saveEntityBtn"),
};

let currentResult = null;
let previewMode = "raw";
let graphDoc = null;
let selectedEntityId = null;
let dragState = null;
let currentSession = null;
let currentProject = null;
let currentProjectMap = null;
let currentProjectTimeline = null;
let currentBranchSummary = null;
let currentLineageGraph = null;
let currentBranchRebaseResult = null;
let currentBranchResetResult = null;
let currentTagSummary = null;
let currentTagPointResult = null;
let currentSnapshotSummary = null;
let currentSnapshotResult = null;
let currentSnapshotPackage = null;
let currentSnapshotRestoreSummary = null;
let currentSnapshotRestorePreview = null;
let currentSnapshotRestoreResult = null;
let currentPartialSnapshotImportSummary = null;
let currentPartialSnapshotImportResult = null;
let currentSnapshotReconcileSummary = null;
let currentSnapshotReconcilePreview = null;
let currentSnapshotReconcileDecisions = {};
let currentSnapshotReconcileResult = null;
let currentSnapshotReconcileCommitSummary = null;
let currentSnapshotReconcileCommitResult = null;
let currentSnapshotReconcileCommitCompareResult = null;
let currentSnapshotReconcileCommitPackageSummary = null;
let currentSnapshotReconcileCommitPackageImportSummary = null;
let currentSnapshotReconcileCommitPackagePreview = null;
let currentSnapshotReconcileCommitPackageImportDecisions = {};
let currentSnapshotReconcileCommitPackageResolutionSummary = null;
let currentSnapshotReconcileCommitPackageCommitSummary = null;
let currentSnapshotReconcileCommitPackageResult = null;
let currentSnapshotReconcileCommitPackage = null;
let currentLocalOutcomeSetPackageSummary = null;
let currentLocalOutcomeSetPackageImportSummary = null;
let currentLocalOutcomeSetPackageResolutionSummary = null;
let currentLocalOutcomeSetPackage = null;
let currentLocalOutcomeSetPackagePreviewResult = null;
let currentLocalOutcomeSetPackageImportDecisions = {};
let currentLocalOutcomeSetPackageResult = null;
let currentPortableLocalOutcomeThreeWayMergeResult = null;
let currentPortableLocalOutcomeMergeDecisions = {};
let currentPortableLocalOutcomeMergeResolutionSummary = null;
let currentPortableLocalOutcomeMergeResolutionResult = null;
let currentPortableLocalOutcomeMergeCommitResult = null;
let selectedPortableLocalOutcomeMergeItemId = null;
let portableLocalOutcomeMergeController = null;
let snapshotReconcileWorkflowController = null;
let reconcileCommitPackageWorkflowController = null;
let localOutcomeSetPackageWorkflowController = null;
let projectOperationsWorkflowController = null;
let projectWorkspaceWorkflowController = null;
let projectLifecycleWorkflowController = null;
let graphSessionWorkspaceController = null;
let inspectorBootstrapController = null;
let inspectorCoreController = null;
let inspectorPanelController = null;
let inspectorActionController = null;
let currentBranchCherryPickResult = null;
let currentBranchSquashResult = null;
let currentCompareResult = null;
let currentMergeResult = null;
let currentResolvedMergeResult = null;
let currentConflictDecisions = {};
let currentMergeCommitResult = null;

function setStatus(text) { els.statusText.textContent = text; }
function pretty(obj) { return JSON.stringify(obj, null, 2); }
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
function parseInitialState() { const raw = els.initialState.value.trim(); if (!raw) return null; return JSON.parse(raw); }
function entityLabel(entity) {
  if (entity.kind === "node") return `${entity.class_name}:${entity.root}`;
  if (entity.kind === "list") return "LIST";
  if (entity.kind === "raw_token") return entity.value || "raw";
  if (entity.kind === "typed_literal") return entity.value ? `${entity.class_name}:${entity.root}=${entity.value}` : `${entity.class_name}:${entity.root}`;
  return entity.id;
}

function renderResult(result) {
  getInspectorCoreController().renderResult(result);
}
function renderSvg() {
  getGraphSessionWorkspaceController().renderSvg();
}
function renderGraph() {
  getGraphSessionWorkspaceController().renderGraph();
}
async function postJson(url, payload) {
  const res = await fetch(url, { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload) });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

function getPortableLocalOutcomeMergeController() {
  if (!portableLocalOutcomeMergeController) {
    const factory = window.PortableLocalOutcomeMergeWorkstation?.createPortableLocalOutcomeMergeController;
    if (!factory) {
      throw new Error("Portable local outcome merge workstation module is not loaded");
    }
    portableLocalOutcomeMergeController = factory({
      els,
      getCurrentProject: () => currentProject,
      getMergeResult: () => currentPortableLocalOutcomeThreeWayMergeResult,
      setMergeResult: (value) => { currentPortableLocalOutcomeThreeWayMergeResult = value; },
      getMergeDecisions: () => currentPortableLocalOutcomeMergeDecisions,
      setMergeDecisions: (value) => { currentPortableLocalOutcomeMergeDecisions = value; },
      setMergeResolutionSummary: (value) => { currentPortableLocalOutcomeMergeResolutionSummary = value; },
      getMergeResolutionResult: () => currentPortableLocalOutcomeMergeResolutionResult,
      setMergeResolutionResult: (value) => { currentPortableLocalOutcomeMergeResolutionResult = value; },
      getMergeCommitResult: () => currentPortableLocalOutcomeMergeCommitResult,
      setMergeCommitResult: (value) => { currentPortableLocalOutcomeMergeCommitResult = value; },
      getSelectedItemId: () => selectedPortableLocalOutcomeMergeItemId,
      setSelectedItemId: (value) => { selectedPortableLocalOutcomeMergeItemId = value; },
      escapeHtml,
      pretty,
      postJson,
      renderResult,
      setStatus,
    });
  }
  return portableLocalOutcomeMergeController;
}

function refreshProjectUiForSnapshotReconcileWorkflow() {
  getInspectorCoreController().refreshProjectUiForSnapshotReconcileWorkflow();
}

function renderSupplementaryPanelsForSnapshotReconcileWorkflow() {
  getInspectorCoreController().renderSupplementaryPanelsForSnapshotReconcileWorkflow();
}

function getSnapshotReconcileWorkflowState() {
  return {
    currentProject,
    currentProjectMap,
    currentProjectTimeline,
    currentBranchSummary,
    currentLineageGraph,
    currentTagSummary,
    currentSnapshotSummary,
    currentSnapshotPackage,
    currentSnapshotRestoreSummary,
    currentPartialSnapshotImportSummary,
    currentSnapshotReconcileSummary,
    currentSnapshotReconcilePreview,
    currentSnapshotReconcileDecisions,
    currentSnapshotReconcileResult,
    currentSnapshotReconcileCommitSummary,
    currentSnapshotReconcileCommitResult,
    currentSnapshotReconcileCommitCompareResult,
  };
}

function setSnapshotReconcileWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentProjectMap" in patch) currentProjectMap = patch.currentProjectMap;
  if ("currentProjectTimeline" in patch) currentProjectTimeline = patch.currentProjectTimeline;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentLineageGraph" in patch) currentLineageGraph = patch.currentLineageGraph;
  if ("currentTagSummary" in patch) currentTagSummary = patch.currentTagSummary;
  if ("currentSnapshotSummary" in patch) currentSnapshotSummary = patch.currentSnapshotSummary;
  if ("currentSnapshotPackage" in patch) currentSnapshotPackage = patch.currentSnapshotPackage;
  if ("currentSnapshotRestoreSummary" in patch) currentSnapshotRestoreSummary = patch.currentSnapshotRestoreSummary;
  if ("currentPartialSnapshotImportSummary" in patch) currentPartialSnapshotImportSummary = patch.currentPartialSnapshotImportSummary;
  if ("currentSnapshotReconcileSummary" in patch) currentSnapshotReconcileSummary = patch.currentSnapshotReconcileSummary;
  if ("currentSnapshotReconcilePreview" in patch) currentSnapshotReconcilePreview = patch.currentSnapshotReconcilePreview;
  if ("currentSnapshotReconcileDecisions" in patch) currentSnapshotReconcileDecisions = patch.currentSnapshotReconcileDecisions;
  if ("currentSnapshotReconcileResult" in patch) currentSnapshotReconcileResult = patch.currentSnapshotReconcileResult;
  if ("currentSnapshotReconcileCommitSummary" in patch) currentSnapshotReconcileCommitSummary = patch.currentSnapshotReconcileCommitSummary;
  if ("currentSnapshotReconcileCommitResult" in patch) currentSnapshotReconcileCommitResult = patch.currentSnapshotReconcileCommitResult;
  if ("currentSnapshotReconcileCommitCompareResult" in patch) currentSnapshotReconcileCommitCompareResult = patch.currentSnapshotReconcileCommitCompareResult;
}

function getSnapshotReconcileWorkflowController() {
  if (!snapshotReconcileWorkflowController) {
    const factory = window.SnapshotReconcileWorkflow?.createSnapshotReconcileController;
    if (!factory) {
      throw new Error("Snapshot reconcile workflow module is not loaded");
    }
    snapshotReconcileWorkflowController = factory({
      els,
      getState: getSnapshotReconcileWorkflowState,
      setState: setSnapshotReconcileWorkflowState,
      pretty,
      parseCsvList,
      postJson,
      renderResult,
      setStatus,
      refreshProjectUi: refreshProjectUiForSnapshotReconcileWorkflow,
      renderSupplementaryPanels: renderSupplementaryPanelsForSnapshotReconcileWorkflow,
      updateReconcileCommitPackageSelectors: () => getInspectorPanelController().updateReconcileCommitPackageSelectors(),
      renderReconcileCommitPackageList: () => getInspectorPanelController().renderReconcileCommitPackageList(),
    });
  }
  return snapshotReconcileWorkflowController;
}

function refreshProjectUiForReconcileCommitPackageWorkflow() {
  getInspectorCoreController().refreshProjectUiForReconcileCommitPackageWorkflow();
}

function renderLocalOutcomeSetPackagePanels() {
  getInspectorCoreController().renderLocalOutcomeSetPackagePanels();
}

function getReconcileCommitPackageWorkflowState() {
  return {
    currentProject,
    currentProjectMap,
    currentProjectTimeline,
    currentBranchSummary,
    currentLineageGraph,
    currentTagSummary,
    currentSnapshotReconcileCommitSummary,
    currentSnapshotReconcileCommitPackageSummary,
    currentSnapshotReconcileCommitPackageImportSummary,
    currentSnapshotReconcileCommitPackagePreview,
    currentSnapshotReconcileCommitPackageImportDecisions,
    currentSnapshotReconcileCommitPackageResolutionSummary,
    currentSnapshotReconcileCommitPackageCommitSummary,
    currentSnapshotReconcileCommitPackageResult,
    currentSnapshotReconcileCommitPackage,
    currentLocalOutcomeSetPackageSummary,
    currentLocalOutcomeSetPackageImportSummary,
    currentLocalOutcomeSetPackageResolutionSummary,
    currentLocalOutcomeSetPackage,
    currentLocalOutcomeSetPackagePreviewResult,
    currentLocalOutcomeSetPackageImportDecisions,
    currentLocalOutcomeSetPackageResult,
  };
}

function setReconcileCommitPackageWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentProjectMap" in patch) currentProjectMap = patch.currentProjectMap;
  if ("currentProjectTimeline" in patch) currentProjectTimeline = patch.currentProjectTimeline;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentLineageGraph" in patch) currentLineageGraph = patch.currentLineageGraph;
  if ("currentTagSummary" in patch) currentTagSummary = patch.currentTagSummary;
  if ("currentSnapshotReconcileCommitSummary" in patch) currentSnapshotReconcileCommitSummary = patch.currentSnapshotReconcileCommitSummary;
  if ("currentSnapshotReconcileCommitPackageSummary" in patch) currentSnapshotReconcileCommitPackageSummary = patch.currentSnapshotReconcileCommitPackageSummary;
  if ("currentSnapshotReconcileCommitPackageImportSummary" in patch) currentSnapshotReconcileCommitPackageImportSummary = patch.currentSnapshotReconcileCommitPackageImportSummary;
  if ("currentSnapshotReconcileCommitPackagePreview" in patch) currentSnapshotReconcileCommitPackagePreview = patch.currentSnapshotReconcileCommitPackagePreview;
  if ("currentSnapshotReconcileCommitPackageImportDecisions" in patch) currentSnapshotReconcileCommitPackageImportDecisions = patch.currentSnapshotReconcileCommitPackageImportDecisions;
  if ("currentSnapshotReconcileCommitPackageResolutionSummary" in patch) currentSnapshotReconcileCommitPackageResolutionSummary = patch.currentSnapshotReconcileCommitPackageResolutionSummary;
  if ("currentSnapshotReconcileCommitPackageCommitSummary" in patch) currentSnapshotReconcileCommitPackageCommitSummary = patch.currentSnapshotReconcileCommitPackageCommitSummary;
  if ("currentSnapshotReconcileCommitPackageResult" in patch) currentSnapshotReconcileCommitPackageResult = patch.currentSnapshotReconcileCommitPackageResult;
  if ("currentSnapshotReconcileCommitPackage" in patch) currentSnapshotReconcileCommitPackage = patch.currentSnapshotReconcileCommitPackage;
  if ("currentLocalOutcomeSetPackageSummary" in patch) currentLocalOutcomeSetPackageSummary = patch.currentLocalOutcomeSetPackageSummary;
  if ("currentLocalOutcomeSetPackageImportSummary" in patch) currentLocalOutcomeSetPackageImportSummary = patch.currentLocalOutcomeSetPackageImportSummary;
  if ("currentLocalOutcomeSetPackageResolutionSummary" in patch) currentLocalOutcomeSetPackageResolutionSummary = patch.currentLocalOutcomeSetPackageResolutionSummary;
  if ("currentLocalOutcomeSetPackage" in patch) currentLocalOutcomeSetPackage = patch.currentLocalOutcomeSetPackage;
  if ("currentLocalOutcomeSetPackagePreviewResult" in patch) currentLocalOutcomeSetPackagePreviewResult = patch.currentLocalOutcomeSetPackagePreviewResult;
  if ("currentLocalOutcomeSetPackageImportDecisions" in patch) currentLocalOutcomeSetPackageImportDecisions = patch.currentLocalOutcomeSetPackageImportDecisions;
  if ("currentLocalOutcomeSetPackageResult" in patch) currentLocalOutcomeSetPackageResult = patch.currentLocalOutcomeSetPackageResult;
}

function getReconcileCommitPackageWorkflowController() {
  if (!reconcileCommitPackageWorkflowController) {
    const factory = window.ReconcileCommitPackageWorkflow?.createReconcileCommitPackageController;
    if (!factory) {
      throw new Error("Reconcile commit package workflow module is not loaded");
    }
    reconcileCommitPackageWorkflowController = factory({
      els,
      getState: getReconcileCommitPackageWorkflowState,
      setState: setReconcileCommitPackageWorkflowState,
      pretty,
      postJson,
      renderResult,
      setStatus,
      refreshProjectUi: refreshProjectUiForReconcileCommitPackageWorkflow,
      updateLocalOutcomeSetPackageSelectors: () => getInspectorPanelController().updateLocalOutcomeSetPackageSelectors(),
      renderLocalOutcomeSetPackagePanels,
    });
  }
  return reconcileCommitPackageWorkflowController;
}

function getLocalOutcomeSetPackageWorkflowState() {
  return {
    currentProject,
    currentBranchSummary,
    currentSnapshotReconcileCommitPackageCommitSummary,
    currentLocalOutcomeSetPackageSummary,
    currentLocalOutcomeSetPackageImportSummary,
    currentLocalOutcomeSetPackageResolutionSummary,
    currentLocalOutcomeSetPackage,
    currentLocalOutcomeSetPackagePreviewResult,
    currentLocalOutcomeSetPackageImportDecisions,
    currentLocalOutcomeSetPackageResult,
  };
}

function setLocalOutcomeSetPackageWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentSnapshotReconcileCommitPackageCommitSummary" in patch) currentSnapshotReconcileCommitPackageCommitSummary = patch.currentSnapshotReconcileCommitPackageCommitSummary;
  if ("currentLocalOutcomeSetPackageSummary" in patch) currentLocalOutcomeSetPackageSummary = patch.currentLocalOutcomeSetPackageSummary;
  if ("currentLocalOutcomeSetPackageImportSummary" in patch) currentLocalOutcomeSetPackageImportSummary = patch.currentLocalOutcomeSetPackageImportSummary;
  if ("currentLocalOutcomeSetPackageResolutionSummary" in patch) currentLocalOutcomeSetPackageResolutionSummary = patch.currentLocalOutcomeSetPackageResolutionSummary;
  if ("currentLocalOutcomeSetPackage" in patch) currentLocalOutcomeSetPackage = patch.currentLocalOutcomeSetPackage;
  if ("currentLocalOutcomeSetPackagePreviewResult" in patch) currentLocalOutcomeSetPackagePreviewResult = patch.currentLocalOutcomeSetPackagePreviewResult;
  if ("currentLocalOutcomeSetPackageImportDecisions" in patch) currentLocalOutcomeSetPackageImportDecisions = patch.currentLocalOutcomeSetPackageImportDecisions;
  if ("currentLocalOutcomeSetPackageResult" in patch) currentLocalOutcomeSetPackageResult = patch.currentLocalOutcomeSetPackageResult;
}

function getLocalOutcomeSetPackageWorkflowController() {
  if (!localOutcomeSetPackageWorkflowController) {
    const factory = window.LocalOutcomeSetPackageWorkflow?.createLocalOutcomeSetPackageController;
    if (!factory) {
      throw new Error("Local outcome set package workflow module is not loaded");
    }
    localOutcomeSetPackageWorkflowController = factory({
      els,
      getState: getLocalOutcomeSetPackageWorkflowState,
      setState: setLocalOutcomeSetPackageWorkflowState,
      pretty,
      postJson,
      renderResult,
      setStatus,
      updatePortableLocalOutcomeMergeSelectors: () => getInspectorPanelController().updatePortableLocalOutcomeMergeSelectors(),
    });
  }
  return localOutcomeSetPackageWorkflowController;
}

function getProjectOperationsWorkflowState() {
  return {
    currentProject,
    currentBranchSummary,
    currentCompareResult,
    currentMergeResult,
    currentResolvedMergeResult,
    currentConflictDecisions,
    currentMergeCommitResult,
    currentBranchRebaseResult,
    currentBranchResetResult,
    currentBranchCherryPickResult,
    currentBranchSquashResult,
  };
}

function setProjectOperationsWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentCompareResult" in patch) currentCompareResult = patch.currentCompareResult;
  if ("currentMergeResult" in patch) currentMergeResult = patch.currentMergeResult;
  if ("currentResolvedMergeResult" in patch) currentResolvedMergeResult = patch.currentResolvedMergeResult;
  if ("currentConflictDecisions" in patch) currentConflictDecisions = patch.currentConflictDecisions;
  if ("currentMergeCommitResult" in patch) currentMergeCommitResult = patch.currentMergeCommitResult;
  if ("currentBranchRebaseResult" in patch) currentBranchRebaseResult = patch.currentBranchRebaseResult;
  if ("currentBranchResetResult" in patch) currentBranchResetResult = patch.currentBranchResetResult;
  if ("currentBranchCherryPickResult" in patch) currentBranchCherryPickResult = patch.currentBranchCherryPickResult;
  if ("currentBranchSquashResult" in patch) currentBranchSquashResult = patch.currentBranchSquashResult;
}

function getProjectOperationsWorkflowController() {
  if (!projectOperationsWorkflowController) {
    const factory = window.ProjectOperationsWorkflow?.createProjectOperationsController;
    if (!factory) {
      throw new Error("Project operations workflow module is not loaded");
    }
    projectOperationsWorkflowController = factory({
      els,
      getState: getProjectOperationsWorkflowState,
      setState: setProjectOperationsWorkflowState,
      pretty,
      postJson,
      renderResult,
      setStatus,
    });
  }
  return projectOperationsWorkflowController;
}

function getProjectWorkspaceWorkflowState() {
  return {
    currentProject,
    currentProjectMap,
    currentProjectTimeline,
    currentBranchSummary,
    currentLineageGraph,
    currentBranchRebaseResult,
    currentBranchResetResult,
    currentTagSummary,
    currentTagPointResult,
    currentSnapshotSummary,
    currentSnapshotResult,
    currentSnapshotPackage,
    currentSnapshotRestoreSummary,
    currentSnapshotRestoreResult,
    currentPartialSnapshotImportSummary,
    currentPartialSnapshotImportResult,
    currentSnapshotReconcileSummary,
    currentSnapshotReconcilePreview,
    currentSnapshotReconcileResult,
    currentSnapshotReconcileCommitSummary,
    currentSnapshotReconcileCommitResult,
    currentSnapshotReconcileCommitCompareResult,
    currentSnapshotReconcileCommitPackageSummary,
    currentSnapshotReconcileCommitPackageImportSummary,
    currentSnapshotReconcileCommitPackagePreview,
    currentSnapshotReconcileCommitPackageResolutionSummary,
    currentSnapshotReconcileCommitPackageCommitSummary,
    currentSnapshotReconcileCommitPackageResult,
    currentSnapshotReconcileCommitPackage,
    currentLocalOutcomeSetPackageSummary,
    currentLocalOutcomeSetPackageImportSummary,
    currentLocalOutcomeSetPackageResolutionSummary,
    currentLocalOutcomeSetPackage,
    currentLocalOutcomeSetPackagePreviewResult,
    currentLocalOutcomeSetPackageResult,
    currentPortableLocalOutcomeMergeResolutionSummary,
    currentPortableLocalOutcomeMergeResolutionResult,
    currentPortableLocalOutcomeMergeCommitResult,
    currentBranchCherryPickResult,
    currentBranchSquashResult,
  };
}

function setProjectWorkspaceWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentProjectMap" in patch) currentProjectMap = patch.currentProjectMap;
  if ("currentProjectTimeline" in patch) currentProjectTimeline = patch.currentProjectTimeline;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentLineageGraph" in patch) currentLineageGraph = patch.currentLineageGraph;
  if ("currentBranchRebaseResult" in patch) currentBranchRebaseResult = patch.currentBranchRebaseResult;
  if ("currentBranchResetResult" in patch) currentBranchResetResult = patch.currentBranchResetResult;
  if ("currentTagSummary" in patch) currentTagSummary = patch.currentTagSummary;
  if ("currentTagPointResult" in patch) currentTagPointResult = patch.currentTagPointResult;
  if ("currentSnapshotSummary" in patch) currentSnapshotSummary = patch.currentSnapshotSummary;
  if ("currentSnapshotResult" in patch) currentSnapshotResult = patch.currentSnapshotResult;
  if ("currentSnapshotPackage" in patch) currentSnapshotPackage = patch.currentSnapshotPackage;
  if ("currentSnapshotRestoreSummary" in patch) currentSnapshotRestoreSummary = patch.currentSnapshotRestoreSummary;
  if ("currentSnapshotRestoreResult" in patch) currentSnapshotRestoreResult = patch.currentSnapshotRestoreResult;
  if ("currentPartialSnapshotImportSummary" in patch) currentPartialSnapshotImportSummary = patch.currentPartialSnapshotImportSummary;
  if ("currentPartialSnapshotImportResult" in patch) currentPartialSnapshotImportResult = patch.currentPartialSnapshotImportResult;
  if ("currentSnapshotReconcileSummary" in patch) currentSnapshotReconcileSummary = patch.currentSnapshotReconcileSummary;
  if ("currentSnapshotReconcilePreview" in patch) currentSnapshotReconcilePreview = patch.currentSnapshotReconcilePreview;
  if ("currentSnapshotReconcileResult" in patch) currentSnapshotReconcileResult = patch.currentSnapshotReconcileResult;
  if ("currentSnapshotReconcileCommitSummary" in patch) currentSnapshotReconcileCommitSummary = patch.currentSnapshotReconcileCommitSummary;
  if ("currentSnapshotReconcileCommitResult" in patch) currentSnapshotReconcileCommitResult = patch.currentSnapshotReconcileCommitResult;
  if ("currentSnapshotReconcileCommitCompareResult" in patch) currentSnapshotReconcileCommitCompareResult = patch.currentSnapshotReconcileCommitCompareResult;
  if ("currentSnapshotReconcileCommitPackageSummary" in patch) currentSnapshotReconcileCommitPackageSummary = patch.currentSnapshotReconcileCommitPackageSummary;
  if ("currentSnapshotReconcileCommitPackageImportSummary" in patch) currentSnapshotReconcileCommitPackageImportSummary = patch.currentSnapshotReconcileCommitPackageImportSummary;
  if ("currentSnapshotReconcileCommitPackagePreview" in patch) currentSnapshotReconcileCommitPackagePreview = patch.currentSnapshotReconcileCommitPackagePreview;
  if ("currentSnapshotReconcileCommitPackageResolutionSummary" in patch) currentSnapshotReconcileCommitPackageResolutionSummary = patch.currentSnapshotReconcileCommitPackageResolutionSummary;
  if ("currentSnapshotReconcileCommitPackageCommitSummary" in patch) currentSnapshotReconcileCommitPackageCommitSummary = patch.currentSnapshotReconcileCommitPackageCommitSummary;
  if ("currentSnapshotReconcileCommitPackageResult" in patch) currentSnapshotReconcileCommitPackageResult = patch.currentSnapshotReconcileCommitPackageResult;
  if ("currentSnapshotReconcileCommitPackage" in patch) currentSnapshotReconcileCommitPackage = patch.currentSnapshotReconcileCommitPackage;
  if ("currentLocalOutcomeSetPackageSummary" in patch) currentLocalOutcomeSetPackageSummary = patch.currentLocalOutcomeSetPackageSummary;
  if ("currentLocalOutcomeSetPackageImportSummary" in patch) currentLocalOutcomeSetPackageImportSummary = patch.currentLocalOutcomeSetPackageImportSummary;
  if ("currentLocalOutcomeSetPackageResolutionSummary" in patch) currentLocalOutcomeSetPackageResolutionSummary = patch.currentLocalOutcomeSetPackageResolutionSummary;
  if ("currentLocalOutcomeSetPackage" in patch) currentLocalOutcomeSetPackage = patch.currentLocalOutcomeSetPackage;
  if ("currentLocalOutcomeSetPackagePreviewResult" in patch) currentLocalOutcomeSetPackagePreviewResult = patch.currentLocalOutcomeSetPackagePreviewResult;
  if ("currentLocalOutcomeSetPackageResult" in patch) currentLocalOutcomeSetPackageResult = patch.currentLocalOutcomeSetPackageResult;
  if ("currentPortableLocalOutcomeMergeResolutionSummary" in patch) currentPortableLocalOutcomeMergeResolutionSummary = patch.currentPortableLocalOutcomeMergeResolutionSummary;
  if ("currentPortableLocalOutcomeMergeResolutionResult" in patch) currentPortableLocalOutcomeMergeResolutionResult = patch.currentPortableLocalOutcomeMergeResolutionResult;
  if ("currentPortableLocalOutcomeMergeCommitResult" in patch) currentPortableLocalOutcomeMergeCommitResult = patch.currentPortableLocalOutcomeMergeCommitResult;
  if ("currentBranchCherryPickResult" in patch) currentBranchCherryPickResult = patch.currentBranchCherryPickResult;
  if ("currentBranchSquashResult" in patch) currentBranchSquashResult = patch.currentBranchSquashResult;
}

function getProjectWorkspaceWorkflowController() {
  if (!projectWorkspaceWorkflowController) {
    const factory = window.ProjectWorkspaceWorkflow?.createProjectWorkspaceController;
    if (!factory) {
      throw new Error("Project workspace workflow module is not loaded");
    }
    projectWorkspaceWorkflowController = factory({
      els,
      getState: getProjectWorkspaceWorkflowState,
      setState: setProjectWorkspaceWorkflowState,
      pretty,
      postJson,
      renderResult,
      setStatus,
    });
  }
  return projectWorkspaceWorkflowController;
}

function refreshProjectHydratedPanels() {
  getInspectorCoreController().refreshProjectHydratedPanels();
}

function getInspectorCoreWorkflowState() {
  return {
    currentResult,
    previewMode,
    graphDoc,
    selectedEntityId,
    currentSession,
  };
}

function setInspectorCoreWorkflowState(patch) {
  if ("currentResult" in patch) currentResult = patch.currentResult;
  if ("previewMode" in patch) previewMode = patch.previewMode;
  if ("graphDoc" in patch) graphDoc = patch.graphDoc;
  if ("selectedEntityId" in patch) selectedEntityId = patch.selectedEntityId;
  if ("currentSession" in patch) currentSession = patch.currentSession;
}

function getInspectorCoreController() {
  if (!inspectorCoreController) {
    const factory = window.InspectorCoreWorkflow?.createInspectorCoreController;
    if (!factory) {
      throw new Error("Inspector core workflow module is not loaded");
    }
    inspectorCoreController = factory({
      els,
      getState: getInspectorCoreWorkflowState,
      setState: setInspectorCoreWorkflowState,
      pretty,
      hydrateProjectResult: (result) => getProjectWorkspaceWorkflowController().hydrateProjectResult(result),
      renderSvg,
      renderGraph,
      renderers: {
        renderProjectSessions: () => getInspectorPanelController().renderProjectSessions(),
        renderProjectMap: () => getInspectorPanelController().renderProjectMap(),
        renderProjectTimeline: () => getInspectorPanelController().renderProjectTimeline(),
        renderBranchList: () => getInspectorPanelController().renderBranchList(),
        renderTagPointList: () => getInspectorPanelController().renderTagPointList(),
        renderSnapshotList: () => getInspectorPanelController().renderSnapshotList(),
        renderSnapshotReconcileList: () => getInspectorPanelController().renderSnapshotReconcileList(),
        renderSnapshotReconcileCommitList: () => getInspectorPanelController().renderSnapshotReconcileCommitList(),
        renderReconcileCommitPackageList: () => getInspectorPanelController().renderReconcileCommitPackageList(),
        renderReconcileCommitPackagePreview: () => getInspectorPanelController().renderReconcileCommitPackagePreview(),
        renderReconcileCommitPackageDecisionList: () => getInspectorPanelController().renderReconcileCommitPackageDecisionList(),
        renderReconcileCommitPackageResult: () => getInspectorPanelController().renderReconcileCommitPackageResult(),
        renderSnapshotReconcileCommitCompareResult: () => getInspectorPanelController().renderSnapshotReconcileCommitCompareResult(),
        renderLineageGraph: () => getInspectorPanelController().renderLineageGraph(),
        renderTagPointResult: () => getInspectorPanelController().renderTagPointResult(),
        renderSnapshotResult: () => getInspectorPanelController().renderSnapshotResult(),
        renderSnapshotRestorePreview: () => getInspectorPanelController().renderSnapshotRestorePreview(),
        renderSnapshotRestoreResult: () => getInspectorPanelController().renderSnapshotRestoreResult(),
        renderPartialImportResult: () => getInspectorPanelController().renderPartialImportResult(),
        renderSnapshotReconcileResult: () => getInspectorPanelController().renderSnapshotReconcileResult(),
        renderSnapshotReconcileCommitResult: () => getInspectorPanelController().renderSnapshotReconcileCommitResult(),
        renderCompareResult: () => getInspectorPanelController().renderCompareResult(),
        renderMergeResult: () => getInspectorPanelController().renderMergeResult(),
        renderResolvedMergeResult: () => getInspectorPanelController().renderResolvedMergeResult(),
        renderMergeCommitResult: () => getInspectorPanelController().renderMergeCommitResult(),
        renderBranchResetResult: () => getInspectorPanelController().renderBranchResetResult(),
        renderBranchRebaseResult: () => getInspectorPanelController().renderBranchRebaseResult(),
        renderBranchCherryPickResult: () => getInspectorPanelController().renderBranchCherryPickResult(),
        renderBranchSquashResult: () => getInspectorPanelController().renderBranchSquashResult(),
        renderLocalOutcomeSetPackageList: () => getInspectorPanelController().renderLocalOutcomeSetPackageList(),
        renderLocalOutcomeSetPackagePreviewResult: () => getInspectorPanelController().renderLocalOutcomeSetPackagePreviewResult(),
        renderLocalOutcomeSetPackageDecisionList: () => getInspectorPanelController().renderLocalOutcomeSetPackageDecisionList(),
        renderLocalOutcomeSetPackageResult: () => getInspectorPanelController().renderLocalOutcomeSetPackageResult(),
        renderPortableLocalOutcomeThreeWayMergeResult: () => getInspectorPanelController().renderPortableLocalOutcomeThreeWayMergeResult(),
        renderPortableLocalOutcomeMergeDecisionList: () => getInspectorPanelController().renderPortableLocalOutcomeMergeDecisionList(),
        renderPortableLocalOutcomeMergeResolutionResult: () => getInspectorPanelController().renderPortableLocalOutcomeMergeResolutionResult(),
        renderPortableLocalOutcomeMergeCommitResult: () => getInspectorPanelController().renderPortableLocalOutcomeMergeCommitResult(),
        renderPortableLocalOutcomeWorkstation: () => getInspectorPanelController().renderPortableLocalOutcomeWorkstation(),
      },
      updaters: {
        updateTagTargetSessions: () => getInspectorPanelController().updateTagTargetSessions(),
        updatePartialImportSelectors: () => getInspectorPanelController().updatePartialImportSelectors(),
        updateSnapshotSelectors: () => getInspectorPanelController().updateSnapshotSelectors(),
        updateResetSelectors: () => getInspectorPanelController().updateResetSelectors(),
        updateRebaseSelectors: () => getInspectorPanelController().updateRebaseSelectors(),
        updateCherryPickSelectors: () => getInspectorPanelController().updateCherryPickSelectors(),
        updateSquashSelectors: () => getInspectorPanelController().updateSquashSelectors(),
        updateCompareSelectors: () => getInspectorPanelController().updateCompareSelectors(),
        updateMergeSelectors: () => getInspectorPanelController().updateMergeSelectors(),
        updateReconcileCommitPackageSelectors: () => getInspectorPanelController().updateReconcileCommitPackageSelectors(),
        updateLocalOutcomeSetPackageSelectors: () => getInspectorPanelController().updateLocalOutcomeSetPackageSelectors(),
        updatePortableLocalOutcomeMergeSelectors: () => getInspectorPanelController().updatePortableLocalOutcomeMergeSelectors(),
        updateSnapshotReconcileSelectors: () => getInspectorPanelController().updateSnapshotReconcileSelectors(),
      },
    });
  }
  return inspectorCoreController;
}

function getProjectLifecycleWorkflowState() {
  return {
    currentProject,
    currentProjectMap,
    currentProjectTimeline,
    currentBranchSummary,
    currentLineageGraph,
    currentBranchRebaseResult,
    currentBranchResetResult,
    currentTagSummary,
    currentTagPointResult,
    currentSnapshotSummary,
    currentSnapshotResult,
    currentSnapshotPackage,
    currentSnapshotRestoreSummary,
    currentSnapshotRestorePreview,
    currentSnapshotRestoreResult,
    currentPartialSnapshotImportSummary,
    currentPartialSnapshotImportResult,
    currentSnapshotReconcileSummary,
    currentSnapshotReconcilePreview,
    currentSnapshotReconcileResult,
    currentSnapshotReconcileCommitSummary,
    currentSnapshotReconcileCommitResult,
    currentSnapshotReconcileCommitCompareResult,
    currentSnapshotReconcileCommitPackageSummary,
    currentSnapshotReconcileCommitPackageImportSummary,
    currentSnapshotReconcileCommitPackagePreview,
    currentSnapshotReconcileCommitPackageResolutionSummary,
    currentSnapshotReconcileCommitPackageCommitSummary,
    currentSnapshotReconcileCommitPackageResult,
    currentSnapshotReconcileCommitPackage,
    currentLocalOutcomeSetPackageSummary,
    currentLocalOutcomeSetPackageImportSummary,
    currentLocalOutcomeSetPackageResolutionSummary,
    currentLocalOutcomeSetPackage,
    currentLocalOutcomeSetPackagePreviewResult,
    currentLocalOutcomeSetPackageImportDecisions,
    currentLocalOutcomeSetPackageResult,
    currentPortableLocalOutcomeThreeWayMergeResult,
    currentPortableLocalOutcomeMergeDecisions,
    currentPortableLocalOutcomeMergeResolutionSummary,
    currentPortableLocalOutcomeMergeResolutionResult,
    currentPortableLocalOutcomeMergeCommitResult,
    selectedPortableLocalOutcomeMergeItemId,
    currentCompareResult,
    currentMergeResult,
    currentResolvedMergeResult,
    currentConflictDecisions,
    currentMergeCommitResult,
    currentBranchCherryPickResult,
    currentBranchSquashResult,
  };
}

function setProjectLifecycleWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentProjectMap" in patch) currentProjectMap = patch.currentProjectMap;
  if ("currentProjectTimeline" in patch) currentProjectTimeline = patch.currentProjectTimeline;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentLineageGraph" in patch) currentLineageGraph = patch.currentLineageGraph;
  if ("currentBranchRebaseResult" in patch) currentBranchRebaseResult = patch.currentBranchRebaseResult;
  if ("currentBranchResetResult" in patch) currentBranchResetResult = patch.currentBranchResetResult;
  if ("currentTagSummary" in patch) currentTagSummary = patch.currentTagSummary;
  if ("currentTagPointResult" in patch) currentTagPointResult = patch.currentTagPointResult;
  if ("currentSnapshotSummary" in patch) currentSnapshotSummary = patch.currentSnapshotSummary;
  if ("currentSnapshotResult" in patch) currentSnapshotResult = patch.currentSnapshotResult;
  if ("currentSnapshotPackage" in patch) currentSnapshotPackage = patch.currentSnapshotPackage;
  if ("currentSnapshotRestoreSummary" in patch) currentSnapshotRestoreSummary = patch.currentSnapshotRestoreSummary;
  if ("currentSnapshotRestorePreview" in patch) currentSnapshotRestorePreview = patch.currentSnapshotRestorePreview;
  if ("currentSnapshotRestoreResult" in patch) currentSnapshotRestoreResult = patch.currentSnapshotRestoreResult;
  if ("currentPartialSnapshotImportSummary" in patch) currentPartialSnapshotImportSummary = patch.currentPartialSnapshotImportSummary;
  if ("currentPartialSnapshotImportResult" in patch) currentPartialSnapshotImportResult = patch.currentPartialSnapshotImportResult;
  if ("currentSnapshotReconcileSummary" in patch) currentSnapshotReconcileSummary = patch.currentSnapshotReconcileSummary;
  if ("currentSnapshotReconcilePreview" in patch) currentSnapshotReconcilePreview = patch.currentSnapshotReconcilePreview;
  if ("currentSnapshotReconcileResult" in patch) currentSnapshotReconcileResult = patch.currentSnapshotReconcileResult;
  if ("currentSnapshotReconcileCommitSummary" in patch) currentSnapshotReconcileCommitSummary = patch.currentSnapshotReconcileCommitSummary;
  if ("currentSnapshotReconcileCommitResult" in patch) currentSnapshotReconcileCommitResult = patch.currentSnapshotReconcileCommitResult;
  if ("currentSnapshotReconcileCommitCompareResult" in patch) currentSnapshotReconcileCommitCompareResult = patch.currentSnapshotReconcileCommitCompareResult;
  if ("currentSnapshotReconcileCommitPackageSummary" in patch) currentSnapshotReconcileCommitPackageSummary = patch.currentSnapshotReconcileCommitPackageSummary;
  if ("currentSnapshotReconcileCommitPackageImportSummary" in patch) currentSnapshotReconcileCommitPackageImportSummary = patch.currentSnapshotReconcileCommitPackageImportSummary;
  if ("currentSnapshotReconcileCommitPackagePreview" in patch) currentSnapshotReconcileCommitPackagePreview = patch.currentSnapshotReconcileCommitPackagePreview;
  if ("currentSnapshotReconcileCommitPackageResolutionSummary" in patch) currentSnapshotReconcileCommitPackageResolutionSummary = patch.currentSnapshotReconcileCommitPackageResolutionSummary;
  if ("currentSnapshotReconcileCommitPackageCommitSummary" in patch) currentSnapshotReconcileCommitPackageCommitSummary = patch.currentSnapshotReconcileCommitPackageCommitSummary;
  if ("currentSnapshotReconcileCommitPackageResult" in patch) currentSnapshotReconcileCommitPackageResult = patch.currentSnapshotReconcileCommitPackageResult;
  if ("currentSnapshotReconcileCommitPackage" in patch) currentSnapshotReconcileCommitPackage = patch.currentSnapshotReconcileCommitPackage;
  if ("currentLocalOutcomeSetPackageSummary" in patch) currentLocalOutcomeSetPackageSummary = patch.currentLocalOutcomeSetPackageSummary;
  if ("currentLocalOutcomeSetPackageImportSummary" in patch) currentLocalOutcomeSetPackageImportSummary = patch.currentLocalOutcomeSetPackageImportSummary;
  if ("currentLocalOutcomeSetPackageResolutionSummary" in patch) currentLocalOutcomeSetPackageResolutionSummary = patch.currentLocalOutcomeSetPackageResolutionSummary;
  if ("currentLocalOutcomeSetPackage" in patch) currentLocalOutcomeSetPackage = patch.currentLocalOutcomeSetPackage;
  if ("currentLocalOutcomeSetPackagePreviewResult" in patch) currentLocalOutcomeSetPackagePreviewResult = patch.currentLocalOutcomeSetPackagePreviewResult;
  if ("currentLocalOutcomeSetPackageImportDecisions" in patch) currentLocalOutcomeSetPackageImportDecisions = patch.currentLocalOutcomeSetPackageImportDecisions;
  if ("currentLocalOutcomeSetPackageResult" in patch) currentLocalOutcomeSetPackageResult = patch.currentLocalOutcomeSetPackageResult;
  if ("currentPortableLocalOutcomeThreeWayMergeResult" in patch) currentPortableLocalOutcomeThreeWayMergeResult = patch.currentPortableLocalOutcomeThreeWayMergeResult;
  if ("currentPortableLocalOutcomeMergeDecisions" in patch) currentPortableLocalOutcomeMergeDecisions = patch.currentPortableLocalOutcomeMergeDecisions;
  if ("currentPortableLocalOutcomeMergeResolutionSummary" in patch) currentPortableLocalOutcomeMergeResolutionSummary = patch.currentPortableLocalOutcomeMergeResolutionSummary;
  if ("currentPortableLocalOutcomeMergeResolutionResult" in patch) currentPortableLocalOutcomeMergeResolutionResult = patch.currentPortableLocalOutcomeMergeResolutionResult;
  if ("currentPortableLocalOutcomeMergeCommitResult" in patch) currentPortableLocalOutcomeMergeCommitResult = patch.currentPortableLocalOutcomeMergeCommitResult;
  if ("selectedPortableLocalOutcomeMergeItemId" in patch) selectedPortableLocalOutcomeMergeItemId = patch.selectedPortableLocalOutcomeMergeItemId;
  if ("currentCompareResult" in patch) currentCompareResult = patch.currentCompareResult;
  if ("currentMergeResult" in patch) currentMergeResult = patch.currentMergeResult;
  if ("currentResolvedMergeResult" in patch) currentResolvedMergeResult = patch.currentResolvedMergeResult;
  if ("currentConflictDecisions" in patch) currentConflictDecisions = patch.currentConflictDecisions;
  if ("currentMergeCommitResult" in patch) currentMergeCommitResult = patch.currentMergeCommitResult;
  if ("currentBranchCherryPickResult" in patch) currentBranchCherryPickResult = patch.currentBranchCherryPickResult;
  if ("currentBranchSquashResult" in patch) currentBranchSquashResult = patch.currentBranchSquashResult;
}

function getProjectLifecycleWorkflowController() {
  if (!projectLifecycleWorkflowController) {
    const factory = window.ProjectLifecycleWorkflow?.createProjectLifecycleController;
    if (!factory) {
      throw new Error("Project lifecycle workflow module is not loaded");
    }
    projectLifecycleWorkflowController = factory({
      els,
      getState: getProjectLifecycleWorkflowState,
      setState: setProjectLifecycleWorkflowState,
      pretty,
      parseCsvList,
      postJson,
      renderResult,
      setStatus,
      refreshProjectHydratedPanels,
      downloadBlob,
    });
  }
  return projectLifecycleWorkflowController;
}

function getGraphSessionWorkspaceState() {
  return {
    currentResult,
    previewMode,
    graphDoc,
    selectedEntityId,
    dragState,
    currentSession,
    currentProject,
  };
}

function setGraphSessionWorkspaceState(patch) {
  if ("currentResult" in patch) currentResult = patch.currentResult;
  if ("previewMode" in patch) previewMode = patch.previewMode;
  if ("graphDoc" in patch) graphDoc = patch.graphDoc;
  if ("selectedEntityId" in patch) selectedEntityId = patch.selectedEntityId;
  if ("dragState" in patch) dragState = patch.dragState;
  if ("currentSession" in patch) currentSession = patch.currentSession;
  if ("currentProject" in patch) currentProject = patch.currentProject;
}

function getGraphSessionWorkspaceController() {
  if (!graphSessionWorkspaceController) {
    const factory = window.GraphSessionWorkspace?.createGraphSessionWorkspaceController;
    if (!factory) {
      throw new Error("Graph session workspace module is not loaded");
    }
    graphSessionWorkspaceController = factory({
      els,
      getState: getGraphSessionWorkspaceState,
      setState: setGraphSessionWorkspaceState,
      pretty,
      parseInitialState,
      entityLabel,
      postJson,
      renderResult,
      setStatus,
      downloadBlob,
      renderProjectSessions: () => getInspectorPanelController().renderProjectSessions(),
    });
  }
  return graphSessionWorkspaceController;
}

function getInspectorPanelController() {
  if (!inspectorPanelController) {
    const factory = window.InspectorPanelWorkflow?.createInspectorPanelController;
    if (!factory) {
      throw new Error("Inspector panel workflow module is not loaded");
    }
    inspectorPanelController = factory({
      els,
      getCurrentBranchSummary: () => currentBranchSummary,
      getProjectOperationsController: getProjectOperationsWorkflowController,
      getProjectWorkspaceController: getProjectWorkspaceWorkflowController,
      getProjectLifecycleController: getProjectLifecycleWorkflowController,
      getSnapshotReconcileController: getSnapshotReconcileWorkflowController,
      getReconcileCommitPackageController: getReconcileCommitPackageWorkflowController,
      getLocalOutcomeSetPackageController: getLocalOutcomeSetPackageWorkflowController,
      getPortableLocalOutcomeMergeController: getPortableLocalOutcomeMergeController,
    });
  }
  return inspectorPanelController;
}

function getInspectorActionController() {
  if (!inspectorActionController) {
    const factory = window.InspectorActionWorkflow?.createInspectorActionController;
    if (!factory) {
      throw new Error("Inspector action workflow module is not loaded");
    }
    inspectorActionController = factory({
      getGraphSessionWorkspaceController,
      getProjectLifecycleController: getProjectLifecycleWorkflowController,
      getProjectOperationsController: getProjectOperationsWorkflowController,
      getSnapshotReconcileController: getSnapshotReconcileWorkflowController,
      getReconcileCommitPackageController: getReconcileCommitPackageWorkflowController,
      getLocalOutcomeSetPackageController: getLocalOutcomeSetPackageWorkflowController,
      getPortableLocalOutcomeMergeController,
      getInspectorPanelController,
    });
  }
  return inspectorActionController;
}

function getInspectorBootstrapController() {
  if (!inspectorBootstrapController) {
    const factory = window.InspectorBootstrapWorkflow?.createInspectorBootstrapController;
    if (!factory) {
      throw new Error("Inspector bootstrap workflow module is not loaded");
    }
    const actionController = getInspectorActionController();
    inspectorBootstrapController = factory({
      els,
      getPreviewMode: () => previewMode,
      setPreviewMode: (value) => { previewMode = value; },
      renderSvg,
      actions: actionController,
      initializers: actionController,
    });
  }
  return inspectorBootstrapController;
}
function downloadBlob(text, filename) {
  const blob = new Blob([text], {type: "application/json"});
  const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
}
function parseCsvList(raw) {
  return (raw || "")
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
}
getInspectorBootstrapController().bindEventHandlers();
getInspectorBootstrapController().initialize();
