(function () {
  function createGraphSessionWorkspaceController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      parseInitialState,
      entityLabel,
      postJson,
      renderResult,
      setStatus,
      downloadBlob,
      renderProjectSessions,
    } = config;

    const INVALID_STATE = Symbol("invalid-state");
    const PROFILE_GUIDANCE = {
      human: {
        description: "Human-friendly shorthand and aliases.",
        example: "gen(template -> instance)",
      },
      core: {
        description: "Canonical bracket syntax for normalized SEMASCRIPT forms.",
        example: "[PAT:GEN <code=[ENT:TEMPLATE]; dst=[ENT:INSTANCE]>]",
      },
      exec: {
        description: "Executable bracket syntax for runtime-oriented commands.",
        example: "[EXEC:TRANSFER <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]",
      },
    };
    let workspaceSourceMode = "text";
    let workspaceDirty = true;
    let dirtyInputsBound = false;

    function state() {
      return getState();
    }

    function patch(nextState) {
      setState(nextState);
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function currentProfile() {
      return els.profile?.value || "human";
    }

    function currentProfileGuidance() {
      return PROFILE_GUIDANCE[currentProfile()] || PROFILE_GUIDANCE.human;
    }

    function applyProfileGuidance() {
      const guidance = currentProfileGuidance();
      if (els.inputText) {
        els.inputText.placeholder = guidance.example;
        els.inputText.title = `${guidance.description} Example: ${guidance.example}`;
      }
      if (els.profileHint) {
        els.profileHint.innerHTML = `${escapeHtml(guidance.description)} Example: <code>${escapeHtml(guidance.example)}</code>`;
      }
    }

    function looksBracketSyntax(text) {
      return String(text || "").trim().startsWith("[");
    }

    function bracketMismatchHint(message) {
      const text = (els.inputText?.value || "").trim();
      if (!text) return "";

      const bracketExpected = /Expected '\['|Expected "\["|Expected \[/i.test(message || "");
      if ((currentProfile() === "core" || currentProfile() === "exec") && !looksBracketSyntax(text) && bracketExpected) {
        return ` Try profile "human" for shorthand input like ${PROFILE_GUIDANCE.human.example}.`;
      }
      if (currentProfile() === "human" && looksBracketSyntax(text) && message) {
        return ' Input already looks like bracket syntax, so try profile "core" or "exec".';
      }
      return "";
    }

    function formatProfileAwareError(prefix, err) {
      const message = err?.message || String(err);
      return `${prefix}: ${message}${bracketMismatchHint(message)}`;
    }

    function ensureTextProfileCompatible(prefix) {
      const text = (els.inputText?.value || "").trim();
      if (!text) return true;
      if ((currentProfile() === "core" || currentProfile() === "exec") && !looksBracketSyntax(text)) {
        setStatus(
          `${prefix}: profile "${currentProfile()}" expects bracket syntax like ${currentProfileGuidance().example}. ` +
          `Try profile "human" for shorthand input like ${PROFILE_GUIDANCE.human.example}.`
        );
        return false;
      }
      return true;
    }

    function bindDirtyInputs() {
      if (dirtyInputsBound) return;
      dirtyInputsBound = true;

      els.inputText?.addEventListener("input", () => markSessionDirty("text"));
      els.initialState?.addEventListener("input", () => markSessionDirty());
      els.sessionName?.addEventListener("input", () => markSessionDirty());
      els.profile?.addEventListener("change", () => {
        markSessionDirty();
        applyProfileGuidance();
      });
      els.decompose?.addEventListener("change", () => markSessionDirty());
    }

    function markSessionDirty(mode) {
      if (mode) workspaceSourceMode = mode;
      workspaceDirty = true;
      if (state().currentSession) {
        patch({ currentSession: null });
      }
      if (els.sessionJson) {
        els.sessionJson.value = "";
      }
    }

    function parseCurrentInitialState() {
      try {
        return parseInitialState();
      } catch (err) {
        setStatus(`Initial state JSON invalid: ${err.message}`);
        return INVALID_STATE;
      }
    }

    function currentUiState() {
      return {
        preview_mode: state().previewMode || "raw",
        selected_entity_id: state().selectedEntityId || null,
      };
    }

    function normalizeGraphDocument(graphDocument) {
      if (graphDocument && Array.isArray(graphDocument.entities) && Array.isArray(graphDocument.edges)) {
        return graphDocument;
      }
      return {
        graph_version: "SEMASCRIPT_GRAPH_MODEL_v0.1",
        profile: currentProfile(),
        source_text: els.inputText?.value || "",
        root_entity_id: null,
        entities: [],
        edges: [],
      };
    }

    function withGraphMutation(nextGraph, extraPatch = {}) {
      const currentResult = state().currentResult;
      const nextState = {
        graphDoc: nextGraph,
        ...extraPatch,
      };
      if (currentResult) {
        nextState.currentResult = {
          ...currentResult,
          graph_document: structuredClone(nextGraph),
        };
      }
      patch(nextState);
    }

    function nextEntityId(graphDocument) {
      let maxId = 0;
      for (const entity of graphDocument.entities || []) {
        const match = /^e(\d+)$/i.exec(entity.id || "");
        if (match) {
          maxId = Math.max(maxId, Number(match[1]));
        }
      }
      return `e${maxId + 1}`;
    }

    function selectedEntity(graphDocument = state().graphDoc) {
      return (graphDocument?.entities || []).find((entity) => entity.id === state().selectedEntityId) || null;
    }

    function renderSvg() {
      if (!els.svgPanel) return;
      if (!state().currentResult) {
        els.svgPanel.innerHTML = "";
        return;
      }
      const svg = state().previewMode === "decomposed"
        ? (state().currentResult.svg_decomposed || state().currentResult.svg_raw)
        : state().currentResult.svg_raw;
      els.svgPanel.innerHTML = svg || "<div>No SVG available</div>";
    }

    function updateEdgeTargetOptions() {
      if (!els.edgeTargetSelect) return;
      const previousValue = els.edgeTargetSelect.value;
      els.edgeTargetSelect.innerHTML = "";
      for (const entity of (state().graphDoc?.entities || [])) {
        const option = document.createElement("option");
        option.value = entity.id;
        option.textContent = `${entity.id} · ${entityLabel(entity)}`;
        els.edgeTargetSelect.appendChild(option);
      }
      if ((state().graphDoc?.entities || []).some((entity) => entity.id === previousValue)) {
        els.edgeTargetSelect.value = previousValue;
      }
    }

    function fillSelectedEntityForm() {
      const entity = selectedEntity();
      if (!entity) {
        if (els.entityId) els.entityId.value = "";
        if (els.entityKind) els.entityKind.value = "node";
        if (els.entityClass) els.entityClass.value = "";
        if (els.entityRoot) els.entityRoot.value = "";
        if (els.entityValue) els.entityValue.value = "";
        if (els.entityModifiers) els.entityModifiers.value = "";
        return;
      }

      if (els.entityId) els.entityId.value = entity.id || "";
      if (els.entityKind) els.entityKind.value = entity.kind || "node";
      if (els.entityClass) els.entityClass.value = entity.class_name || "";
      if (els.entityRoot) els.entityRoot.value = entity.root || "";
      if (els.entityValue) els.entityValue.value = entity.value == null ? "" : String(entity.value);
      if (els.entityModifiers) els.entityModifiers.value = (entity.modifiers || []).join(" ");
    }

    function edgeLabelSvg(x1, y1, x2, y2, text) {
      const label = String(text ?? "");
      const mx = (x1 + x2) / 2;
      const my = (y1 + y2) / 2 - 6;
      return `<g><rect x="${mx - label.length * 2.6 - 5}" y="${my - 10}" width="${label.length * 5.2 + 10}" height="16" rx="7" ry="7" fill="white" stroke="#d6d9df"/><text class="edge-label" x="${mx}" y="${my + 2}" text-anchor="middle">${escapeHtml(label)}</text></g>`;
    }

    function renderGraph() {
      if (!els.graphNodes || !els.graphEdges || !els.graphJsonText || !els.graphMeta) return;

      els.graphNodes.innerHTML = "";
      els.graphEdges.innerHTML = "";

      const graphDocument = normalizeGraphDocument(state().graphDoc);
      if (!state().graphDoc) {
        els.graphJsonText.textContent = "";
        els.graphMeta.textContent = "No graph loaded";
        updateEdgeTargetOptions();
        fillSelectedEntityForm();
        return;
      }

      const entityIds = new Set((graphDocument.entities || []).map((entity) => entity.id));
      if (!entityIds.has(state().selectedEntityId)) {
        patch({
          selectedEntityId: graphDocument.root_entity_id || graphDocument.entities[0]?.id || null,
        });
      }

      els.graphJsonText.textContent = pretty(graphDocument);
      els.graphMeta.textContent = `entities: ${graphDocument.entities.length} · edges: ${graphDocument.edges.length} · root: ${graphDocument.root_entity_id || "-"}`;
      updateEdgeTargetOptions();
      fillSelectedEntityForm();

      const workspaceRect = els.graphWorkspace?.getBoundingClientRect();
      const edgeParts = [];
      const index = new Map(graphDocument.entities.map((entity) => [entity.id, entity]));

      for (const entity of graphDocument.entities) {
        const node = document.createElement("div");
        const nodeKind = entity.kind === "node" ? (entity.class_name || "node").toLowerCase() : entity.kind;
        node.className = `graph-node kind-${entity.kind}${entity.kind === "node" ? ` ${nodeKind}` : ""}`;
        if (entity.id === state().selectedEntityId) node.classList.add("selected");
        if (entity.id === graphDocument.root_entity_id) node.classList.add("root");
        node.style.left = `${entity.x || 40}px`;
        node.style.top = `${entity.y || 40}px`;
        node.dataset.entityId = entity.id;

        const title = document.createElement("strong");
        title.textContent = entityLabel(entity);
        const meta = document.createElement("div");
        meta.className = "small";
        meta.textContent = entity.id;
        node.appendChild(title);
        node.appendChild(meta);

        node.addEventListener("pointerdown", (event) => {
          patch({
            selectedEntityId: entity.id,
            dragState: {
              id: entity.id,
              startX: event.clientX,
              startY: event.clientY,
              entityX: entity.x || 40,
              entityY: entity.y || 40,
            },
          });
          if (node.setPointerCapture) {
            node.setPointerCapture(event.pointerId);
          }
          renderGraph();
        });

        node.addEventListener("pointermove", (event) => {
          const dragState = state().dragState;
          if (!dragState || dragState.id !== entity.id) return;

          const nextGraph = structuredClone(state().graphDoc);
          const nextEntity = (nextGraph?.entities || []).find((candidate) => candidate.id === entity.id);
          if (!nextEntity) return;

          const dx = event.clientX - dragState.startX;
          const dy = event.clientY - dragState.startY;
          nextEntity.x = Math.max(10, dragState.entityX + dx);
          nextEntity.y = Math.max(10, dragState.entityY + dy);
          markSessionDirty("graph");
          withGraphMutation(nextGraph);
          renderGraph();
        });

        node.addEventListener("pointerup", () => {
          if (state().dragState) {
            patch({ dragState: null });
          }
        });

        node.addEventListener("pointercancel", () => {
          if (state().dragState) {
            patch({ dragState: null });
          }
        });

        node.addEventListener("dblclick", () => {
          patch({ selectedEntityId: entity.id });
          renderGraph();
        });

        els.graphNodes.appendChild(node);
      }

      for (const edge of graphDocument.edges) {
        const from = index.get(edge.from_id);
        const to = index.get(edge.to_id);
        if (!from || !to) continue;
        const x1 = (from.x || 40) + 70;
        const y1 = (from.y || 40) + 28;
        const x2 = (to.x || 40) + 70;
        const y2 = (to.y || 40) + 28;
        edgeParts.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#111827" stroke-width="1.3"/>`);
        edgeParts.push(edgeLabelSvg(x1, y1, x2, y2, edge.role));
      }

      const width = Math.max(1200, workspaceRect?.width || 0);
      const height = Math.max(700, workspaceRect?.height || 0);
      els.graphEdges.setAttribute("viewBox", `0 0 ${width} ${height}`);
      els.graphEdges.innerHTML = edgeParts.join("\n");
    }

    function applyGraphImportResult(result) {
      const graphDocument = structuredClone(result.graph_document || normalizeGraphDocument(null));
      const nextResult = {
        source_text: els.inputText?.value || "",
        profile: els.profile?.value || "core",
        normalized_text: result.normalized_text || "",
        slinear: result.slinear || "",
        decomposed_slinear: null,
        ast_document: result.ast_document || null,
        validation: null,
        runtime_report: null,
        state_report: null,
        graph_document: graphDocument,
        svg_raw: null,
        svg_decomposed: null,
        session_name: els.sessionName?.value.trim() || null,
      };
      patch({
        currentResult: nextResult,
        graphDoc: graphDocument,
        selectedEntityId: graphDocument.root_entity_id || graphDocument.entities[0]?.id || null,
        dragState: null,
        currentSession: null,
      });

      if (els.normalizedText) {
        els.normalizedText.textContent = [
          `normalized_text:\n${nextResult.normalized_text || ""}`,
          "",
          `slinear:\n${nextResult.slinear || ""}`,
        ].join("\n");
      }
      if (els.validationText) els.validationText.textContent = "";
      if (els.astText) els.astText.textContent = result.ast_document ? pretty(result.ast_document) : "";
      if (els.runtimeText) els.runtimeText.textContent = "";
      if (els.stateText) els.stateText.textContent = "";

      renderGraph();
      renderSvg();
    }

    async function analyze() {
      const text = (els.inputText?.value || "").trim();
      if (!text) {
        setStatus("Input is empty");
        return;
      }
      if (!ensureTextProfileCompatible("Analyze blocked")) return;
      const initialState = parseCurrentInitialState();
      if (initialState === INVALID_STATE) return;

      try {
        markSessionDirty("text");
        const result = await postJson("/api/analyze", {
          text: els.inputText.value,
          profile: currentProfile(),
          decompose: !!els.decompose?.checked,
          initial_state: initialState,
        });
        renderResult(result);
        setStatus("Analyzed text input");
      } catch (err) {
        setStatus(formatProfileAwareError("Analyze failed", err));
      }
    }

    async function importTextToGraph() {
      const text = (els.inputText?.value || "").trim();
      if (!text) {
        setStatus("Input is empty");
        return;
      }
      if (!ensureTextProfileCompatible("Text to graph blocked")) return;

      try {
        markSessionDirty("graph");
        const result = await postJson("/api/graph-from-input", {
          text: els.inputText.value,
          profile: currentProfile(),
        });
        applyGraphImportResult(result);
        setStatus("Imported text into editable graph workspace");
      } catch (err) {
        setStatus(formatProfileAwareError("Text to graph failed", err));
      }
    }

    async function analyzeGraph() {
      const graphDocument = state().graphDoc;
      if (!graphDocument || !(graphDocument.entities || []).length) {
        setStatus("No graph loaded");
        return;
      }
      const initialState = parseCurrentInitialState();
      if (initialState === INVALID_STATE) return;

      try {
        markSessionDirty("graph");
        const result = await postJson("/api/analyze-graph", {
          graph_document: graphDocument,
          profile: currentProfile(),
          decompose: !!els.decompose?.checked,
          initial_state: initialState,
        });
        renderResult(result);
        setStatus("Analyzed current graph");
      } catch (err) {
        setStatus(`Graph analyze failed: ${err.message}`);
      }
    }

    function clearAll() {
      workspaceDirty = true;
      workspaceSourceMode = "text";
      patch({
        currentResult: null,
        previewMode: "raw",
        graphDoc: null,
        selectedEntityId: null,
        dragState: null,
        currentSession: null,
      });

      if (els.inputText) els.inputText.value = "";
      if (els.initialState) els.initialState.value = "";
      if (els.sessionName) els.sessionName.value = "";
      if (els.sessionJson) els.sessionJson.value = "";
      if (els.normalizedText) els.normalizedText.textContent = "";
      if (els.validationText) els.validationText.textContent = "";
      if (els.astText) els.astText.textContent = "";
      if (els.runtimeText) els.runtimeText.textContent = "";
      if (els.stateText) els.stateText.textContent = "";

      applyProfileGuidance();
      renderGraph();
      renderSvg();
      setStatus("Cleared current workspace");
    }

    function applySample(sample) {
      if (els.profile && sample.profile) els.profile.value = sample.profile;
      if (els.inputText) els.inputText.value = sample.text || "";
      if (els.initialState) els.initialState.value = sample.initial_state ? pretty(sample.initial_state) : "";
      if (els.sessionName) els.sessionName.value = sample.id || els.sessionName.value;
      applyProfileGuidance();
      markSessionDirty("text");
      setStatus(`Loaded sample ${sample.id}`);
    }

    function sampleCard(sample) {
      const wrapper = document.createElement("div");
      wrapper.className = "sample-item";

      const title = document.createElement("strong");
      title.textContent = sample.id || "sample";
      wrapper.appendChild(title);

      const meta = document.createElement("div");
      meta.className = "meta";
      meta.textContent = `${sample.profile || "core"}${sample.tags?.length ? ` · ${sample.tags.join(", ")}` : ""}`;
      wrapper.appendChild(meta);

      const text = document.createElement("div");
      text.className = "text";
      text.textContent = sample.text || "";
      wrapper.appendChild(text);

      const button = document.createElement("button");
      button.type = "button";
      button.textContent = "Load sample";
      button.addEventListener("click", () => applySample(sample));
      wrapper.appendChild(button);

      return wrapper;
    }

    async function loadSamples() {
      if (!els.samplesList) return;

      try {
        const response = await fetch("/api/samples");
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Request failed");
        }

        const samples = Array.isArray(data.samples) ? data.samples : [];
        els.samplesList.innerHTML = "";
        for (const sample of samples) {
          els.samplesList.appendChild(sampleCard(sample));
        }
        if (!samples.length) {
          els.samplesList.innerHTML = '<div class="project-map-empty">No samples available</div>';
        }
        setStatus(`Loaded ${samples.length} sample${samples.length === 1 ? "" : "s"}`);
      } catch (err) {
        setStatus(`Sample reload failed: ${err.message}`);
      }
    }

    function addEntity() {
      const graphDocument = structuredClone(normalizeGraphDocument(state().graphDoc));
      const kind = els.newEntityKind?.value || "node";
      const entityId = nextEntityId(graphDocument);
      const offset = graphDocument.entities.length;
      const entity = {
        id: entityId,
        kind,
        x: 56 + offset * 28,
        y: 56 + offset * 24,
        modifiers: [],
      };

      if (kind === "node") {
        entity.class_name = "ENT";
        entity.root = "NEW";
      } else if (kind === "typed_literal") {
        entity.class_name = "VAL";
        entity.root = "VALUE";
        entity.value = "";
      } else if (kind === "raw_token") {
        entity.value = "raw_token";
      }

      graphDocument.entities.push(entity);
      if (!graphDocument.root_entity_id) {
        graphDocument.root_entity_id = entityId;
      }

      markSessionDirty("graph");
      withGraphMutation(graphDocument, {
        selectedEntityId: entityId,
        dragState: null,
      });
      renderGraph();
      setStatus(`Added entity ${entityId}`);
    }

    function setRoot() {
      const graphDocument = state().graphDoc;
      const selectedId = state().selectedEntityId;
      if (!graphDocument || !selectedId) {
        setStatus("Select an entity first");
        return;
      }

      const nextGraph = structuredClone(graphDocument);
      nextGraph.root_entity_id = selectedId;
      markSessionDirty("graph");
      withGraphMutation(nextGraph);
      renderGraph();
      setStatus(`Root set to ${selectedId}`);
    }

    function deleteSelected() {
      const graphDocument = state().graphDoc;
      const selectedId = state().selectedEntityId;
      if (!graphDocument || !selectedId) {
        setStatus("Select an entity first");
        return;
      }

      const nextGraph = structuredClone(graphDocument);
      nextGraph.entities = nextGraph.entities.filter((entity) => entity.id !== selectedId);
      nextGraph.edges = nextGraph.edges.filter((edge) => edge.from_id !== selectedId && edge.to_id !== selectedId);
      if (nextGraph.root_entity_id === selectedId) {
        nextGraph.root_entity_id = nextGraph.entities[0]?.id || null;
      }

      markSessionDirty("graph");
      withGraphMutation(nextGraph, {
        selectedEntityId: nextGraph.root_entity_id || nextGraph.entities[0]?.id || null,
        dragState: null,
      });
      renderGraph();
      setStatus(`Deleted ${selectedId}`);
    }

    function saveSelectedEntity() {
      const graphDocument = state().graphDoc;
      const selectedId = state().selectedEntityId;
      if (!graphDocument || !selectedId) {
        setStatus("Select an entity first");
        return;
      }

      const nextGraph = structuredClone(graphDocument);
      const entity = nextGraph.entities.find((candidate) => candidate.id === selectedId);
      if (!entity) {
        setStatus("Selected entity is missing");
        return;
      }

      const nextId = (els.entityId?.value || "").trim() || selectedId;
      if (nextId !== selectedId && nextGraph.entities.some((candidate) => candidate.id === nextId)) {
        setStatus(`Entity id ${nextId} already exists`);
        return;
      }

      if (nextId !== selectedId) {
        entity.id = nextId;
        for (const edge of nextGraph.edges) {
          if (edge.from_id === selectedId) edge.from_id = nextId;
          if (edge.to_id === selectedId) edge.to_id = nextId;
        }
        if (nextGraph.root_entity_id === selectedId) {
          nextGraph.root_entity_id = nextId;
        }
      }

      entity.kind = els.entityKind?.value || entity.kind || "node";
      entity.class_name = (els.entityClass?.value || "").trim() || undefined;
      entity.root = (els.entityRoot?.value || "").trim() || undefined;
      entity.value = (els.entityValue?.value || "").trim();
      entity.modifiers = (els.entityModifiers?.value || "")
        .split(/\s+/)
        .map((token) => token.trim())
        .filter(Boolean);

      if (entity.kind === "list") {
        delete entity.class_name;
        delete entity.root;
        delete entity.value;
      } else if (entity.kind === "raw_token") {
        delete entity.class_name;
        delete entity.root;
      } else if (entity.kind === "node") {
        delete entity.value;
      }

      markSessionDirty("graph");
      withGraphMutation(nextGraph, {
        selectedEntityId: nextId,
      });
      renderGraph();
      setStatus(`Saved ${nextId}`);
    }

    function addEdge() {
      const graphDocument = state().graphDoc;
      const selectedId = state().selectedEntityId;
      const targetId = els.edgeTargetSelect?.value;
      if (!graphDocument || !selectedId) {
        setStatus("Select a source entity first");
        return;
      }
      if (!targetId) {
        setStatus("Select an edge target");
        return;
      }

      const nextGraph = structuredClone(graphDocument);
      const role = (els.edgeRoleInput?.value || "").trim() || "role";
      nextGraph.edges.push({
        id: `edge_${selectedId}_${targetId}_${nextGraph.edges.length}`,
        from_id: selectedId,
        to_id: targetId,
        role,
      });

      markSessionDirty("graph");
      withGraphMutation(nextGraph);
      renderGraph();
      setStatus(`Added edge ${selectedId} -> ${targetId}`);
    }

    async function exportTextSessionInternal(force = false) {
      if (!force && !workspaceDirty && state().currentSession) {
        if (els.sessionJson) {
          els.sessionJson.value = pretty(state().currentSession);
        }
        return state().currentSession;
      }

      const text = (els.inputText?.value || "").trim();
      if (!text) {
        setStatus("Input is empty");
        return null;
      }
      if (!ensureTextProfileCompatible("Text session export blocked")) return null;
      const initialState = parseCurrentInitialState();
      if (initialState === INVALID_STATE) return null;

      const session = await postJson("/api/export-session-text", {
        text: els.inputText.value,
        profile: currentProfile(),
        decompose: !!els.decompose?.checked,
        initial_state: initialState,
        session_name: els.sessionName?.value.trim() || undefined,
      });

      workspaceSourceMode = "text";
      workspaceDirty = false;
      patch({ currentSession: session });
      if (els.sessionJson) {
        els.sessionJson.value = pretty(session);
      }
      return session;
    }

    async function exportGraphSessionInternal(force = false) {
      if (!force && !workspaceDirty && state().currentSession) {
        if (els.sessionJson) {
          els.sessionJson.value = pretty(state().currentSession);
        }
        return state().currentSession;
      }

      const graphDocument = state().graphDoc;
      if (!graphDocument || !(graphDocument.entities || []).length) {
        setStatus("No graph loaded");
        return null;
      }
      const initialState = parseCurrentInitialState();
      if (initialState === INVALID_STATE) return null;

      const session = await postJson("/api/export-session-graph", {
        graph_document: graphDocument,
        profile: currentProfile(),
        decompose: !!els.decompose?.checked,
        initial_state: initialState,
        session_name: els.sessionName?.value.trim() || undefined,
        ui_state: currentUiState(),
      });

      workspaceSourceMode = "graph";
      workspaceDirty = false;
      patch({ currentSession: session });
      if (els.sessionJson) {
        els.sessionJson.value = pretty(session);
      }
      return session;
    }

    async function exportTextSession() {
      try {
        const session = await exportTextSessionInternal(true);
        if (!session) return;
        setStatus(`Exported text session ${session.session_name || ""}`.trim());
      } catch (err) {
        setStatus(formatProfileAwareError("Text session export failed", err));
      }
    }

    async function exportGraphSession() {
      try {
        const session = await exportGraphSessionInternal(true);
        if (!session) return;
        setStatus(`Exported graph session ${session.session_name || ""}`.trim());
      } catch (err) {
        setStatus(`Graph session export failed: ${err.message}`);
      }
    }

    async function importSession() {
      if (!els.sessionJson?.value.trim()) {
        setStatus("Session JSON is empty");
        return;
      }

      let session;
      try {
        session = JSON.parse(els.sessionJson.value);
      } catch (err) {
        setStatus(`Session JSON is invalid: ${err.message}`);
        return;
      }

      try {
        const payload = await postJson("/api/import-session", { session });
        if (els.inputText) els.inputText.value = session.project?.source_text || "";
        if (els.initialState) els.initialState.value = session.project?.initial_state ? pretty(session.project.initial_state) : "";
        if (els.profile && session.project?.profile) els.profile.value = session.project.profile;
        applyProfileGuidance();
        patch({ currentSession: session });
        workspaceSourceMode = session.project?.source_mode || "text";
        workspaceDirty = false;
        renderResult(payload);
        setStatus(`Imported session ${session.session_name || ""}`.trim());
      } catch (err) {
        setStatus(`Session import failed: ${err.message}`);
      }
    }

    async function ensureCurrentSessionFromResult() {
      if (state().currentSession) {
        return state().currentSession;
      }

      if (workspaceSourceMode === "graph" && state().graphDoc && (state().graphDoc.entities || []).length) {
        return exportGraphSessionInternal();
      }

      if ((els.inputText?.value || "").trim()) {
        return exportTextSessionInternal();
      }

      if (state().graphDoc && (state().graphDoc.entities || []).length) {
        return exportGraphSessionInternal();
      }

      return null;
    }

    async function downloadSession() {
      if (workspaceSourceMode !== "graph" && (els.inputText?.value || "").trim() && !ensureTextProfileCompatible("Session download blocked")) {
        return;
      }
      try {
        const session = await ensureCurrentSessionFromResult();
        if (!session) {
          setStatus("No current session to download");
          return;
        }
        const safeName = (session.session_name || "session").replace(/[^a-z0-9_-]+/gi, "_");
        downloadBlob(pretty(session), `${safeName}.json`);
        setStatus("Session downloaded");
      } catch (err) {
        setStatus(formatProfileAwareError("Session download failed", err));
      }
    }

    async function addCurrentToProject() {
      if (workspaceSourceMode !== "graph" && (els.inputText?.value || "").trim() && !ensureTextProfileCompatible("Add current session blocked")) {
        return;
      }
      try {
        const session = await ensureCurrentSessionFromResult();
        if (!session) {
          setStatus("No current session to add");
          return;
        }

        const currentProject = structuredClone(state().currentProject || {
          project_index_version: "SEMASCRIPT_PROJECT_INDEX_v0.1",
          project_name: els.projectName?.value.trim() || "Untitled SEMASCRIPT Project",
          active_session_id: null,
          sessions: [],
          metadata: { workspace_kind: "multi_session" },
        });

        let baseId = (els.sessionName?.value.trim() || "session").replace(/[^a-z0-9_-]+/gi, "_").toLowerCase();
        if (!baseId) baseId = "session";
        let sessionId = baseId;
        let suffix = 2;
        const existingIds = new Set((currentProject.sessions || []).map((item) => item.session_id));
        while (existingIds.has(sessionId)) {
          sessionId = `${baseId}_${suffix}`;
          suffix += 1;
        }

        const entry = {
          session_id: sessionId,
          session_name: session.session_name,
          profile: session.project.profile,
          source_mode: session.project.source_mode,
          file_name: null,
          tags: [],
          session,
        };
        currentProject.sessions.push(entry);
        if (!currentProject.active_session_id) {
          currentProject.active_session_id = entry.session_id;
        }
        if (!currentProject.project_name) {
          currentProject.project_name = els.projectName?.value.trim() || "Untitled SEMASCRIPT Project";
        }

        patch({ currentProject });
        if (els.projectName) {
          els.projectName.value = currentProject.project_name || els.projectName.value;
        }
        if (els.projectJson) {
          els.projectJson.value = pretty(currentProject);
        }
        renderProjectSessions();
        setStatus(`Current session added to project as ${sessionId}`);
      } catch (err) {
        setStatus(formatProfileAwareError("Add current session failed", err));
      }
    }

    applyProfileGuidance();
    bindDirtyInputs();

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
      renderSvg,
      renderGraph,
    };
  }

  window.GraphSessionWorkspace = {
    createGraphSessionWorkspaceController,
  };
})();
