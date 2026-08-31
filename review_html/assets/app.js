"use strict";

(function () {
  const manifest = window.ECG_REVIEW_MANIFEST;
  if (!manifest || !Array.isArray(manifest.runs)) {
    document.body.innerHTML = "<main><h1>Reviewer manifest unavailable</h1><p>Expected review_html/data/manifest.js.</p></main>";
    return;
  }

  const dataCache = new Map();
  const loading = new Map();
  let activeRun = null;
  let activeData = null;
  let sampleIndex = 0;

  const el = (id) => document.getElementById(id);
  const modelSelect = el("model-select");
  const granularitySelect = el("granularity-select");
  const modeSelect = el("mode-select");
  const runSelect = el("run-select");
  const sampleControlIds = ["ecg-search", "search-button", "previous-button", "next-button", "random-button", "row-filter-select", "sort-select"];

  window.ECGReviewRegisterRunData = function (payload) {
    if (!payload || !payload.canonical_experiment_key) return;
    dataCache.set(payload.canonical_experiment_key, payload);
    const pending = loading.get(payload.canonical_experiment_key);
    if (pending) pending.resolve(payload);
  };

  function escapeHtml(value) {
    return String(value).replace(/[&<>"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[character]));
  }

  function safeStorageGet(key) {
    try { return window.localStorage.getItem(key); } catch (error) { return null; }
  }

  function safeStorageSet(key, value) {
    try { window.localStorage.setItem(key, value); } catch (error) { /* Local preference storage is optional. */ }
  }

  function savedSelection() {
    try { return JSON.parse(safeStorageGet("ecg-review-selection") || "{}"); } catch (error) { return {}; }
  }

  function initialReviewState() {
    const hash = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    const stored = savedSelection();
    return {
      model: hash.get("model") || stored.model,
      granularity: hash.get("granularity") || stored.granularity,
      mode: hash.get("mode") || stored.mode,
      run: hash.get("run"),
      ecg: hash.get("ecg"),
      label: hash.get("label")
    };
  }

  function updateReviewState() {
    if (!activeRun) return;
    const params = new URLSearchParams({
      model: activeRun.model,
      granularity: activeRun.granularity,
      mode: activeRun.mode,
      run: activeRun.formal_run_id
    });
    if (activeData) params.set("ecg", String(activeData.ecg_ids[sampleIndex]));
    const selectedLabel = el("comparison-label-select").value;
    if (selectedLabel) params.set("label", selectedLabel);
    safeStorageSet("ecg-review-selection", JSON.stringify({
      model: activeRun.model,
      granularity: activeRun.granularity,
      mode: activeRun.mode
    }));
    try { window.history.replaceState(null, "", `#${params.toString()}`); } catch (error) { /* Hash persistence is optional for local files. */ }
  }

  function applyTheme(theme, persist) {
    const modes = ["system", "light", "dark"];
    const selected = modes.includes(theme) ? theme : "system";
    document.documentElement.dataset.theme = selected;
    el("theme-select").value = selected;
    if (persist) safeStorageSet("ecg-review-theme", selected);
  }

  function initializeTheme() {
    const modes = ["system", "light", "dark"];
    const stored = safeStorageGet("ecg-review-theme");
    applyTheme(modes.includes(stored) ? stored : "system", false);
    el("theme-select").addEventListener("change", () => applyTheme(el("theme-select").value, true));
  }

  function setOptions(select, values, selected) {
    select.textContent = "";
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      option.selected = value === selected;
      select.appendChild(option);
    });
  }

  function filteredRuns() {
    return manifest.runs.filter((run) =>
      run.model === modelSelect.value &&
      run.granularity === granularitySelect.value &&
      run.mode === modeSelect.value
    );
  }

  function refreshSelectors(changed) {
    const allModels = manifest.model_order.filter((model) => manifest.runs.some((run) => run.model === model));
    if (!modelSelect.options.length) setOptions(modelSelect, allModels, allModels[0]);

    const modelRuns = manifest.runs.filter((run) => run.model === modelSelect.value);
    const granularities = manifest.granularity_order.filter((granularity) => modelRuns.some((run) => run.granularity === granularity));
    if (changed === "model" || !granularities.includes(granularitySelect.value)) {
      setOptions(granularitySelect, granularities, granularities[0]);
    }

    const granularityRuns = modelRuns.filter((run) => run.granularity === granularitySelect.value);
    const modes = manifest.mode_order.filter((mode) => granularityRuns.some((run) => run.mode === mode));
    if (["model", "granularity"].includes(changed) || !modes.includes(modeSelect.value)) {
      setOptions(modeSelect, modes, modes[0]);
    }

    const runs = filteredRuns();
    setOptions(runSelect, runs.map((run) => run.formal_run_id), runs[0] ? runs[0].formal_run_id : "");
    selectRun(runs[0]);
  }

  function initializeSelection() {
    const desired = initialReviewState();
    const models = manifest.model_order.filter((model) => manifest.runs.some((run) => run.model === model));
    const model = models.includes(desired.model) ? desired.model : models[0];
    setOptions(modelSelect, models, model);

    const modelRuns = manifest.runs.filter((run) => run.model === model);
    const granularities = manifest.granularity_order.filter((granularity) => modelRuns.some((run) => run.granularity === granularity));
    const granularity = granularities.includes(desired.granularity) ? desired.granularity : granularities[0];
    setOptions(granularitySelect, granularities, granularity);

    const granularityRuns = modelRuns.filter((run) => run.granularity === granularity);
    const modes = manifest.mode_order.filter((mode) => granularityRuns.some((run) => run.mode === mode));
    const mode = modes.includes(desired.mode) ? desired.mode : modes[0];
    setOptions(modeSelect, modes, mode);

    const runs = manifest.runs.filter((run) => run.model === model && run.granularity === granularity && run.mode === mode);
    const run = runs.find((candidate) => candidate.formal_run_id === desired.run) || runs[0];
    setOptions(runSelect, runs.map((candidate) => candidate.formal_run_id), run ? run.formal_run_id : "");
    selectRun(run, { ecgId: desired.ecg, label: desired.label });
  }

  function classForStatus(value) {
    const status = String(value || "").toUpperCase();
    if (["PASS", "COMPLETE", "FORMAL COMPLETE", "PACKAGED", "SAMPLE DATA AVAILABLE"].includes(status)) return "status-good";
    if (["HISTORICAL_BLOCKED", "HISTORICAL BLOCKER", "PROVENANCE_BLOCKED", "PROVENANCE BLOCKED"].includes(status)) return "status-warning";
    if (["FAILED", "FAIL"].includes(status)) return "status-danger";
    if (["AVAILABLE"].includes(status)) return "status-info";
    return "status-neutral";
  }

  function displayStatus(value) {
    return String(value || "Not available").replaceAll("_", " ");
  }

  function statusChip(value, forcedClass) {
    const text = displayStatus(value);
    return `<span class="status-chip ${forcedClass || classForStatus(value)}">${escapeHtml(text)}</span>`;
  }

  function setLoadStatus(text, kind) {
    const node = el("load-status");
    node.textContent = text;
    node.className = `status-chip status-${kind}`;
  }

  function setSampleControlsDisabled(disabled) {
    sampleControlIds.forEach((id) => { if (el(id)) el(id).disabled = Boolean(disabled); });
    el("sample-browser").setAttribute("aria-busy", String(Boolean(disabled)));
  }

  function metric(value, digits = 6) {
    const number = Number(value);
    return Number.isFinite(number) ? number.toFixed(digits) : "Not available";
  }

  function renderRunSummary(run) {
    el("run-summary").innerHTML = `
      <div class="run-identity-strip">
        <div><span>Model</span><strong>${escapeHtml(run.model)}</strong></div>
        <div><span>Granularity</span><strong>${escapeHtml(run.granularity)}</strong></div>
        <div><span>Mode</span><strong>${escapeHtml(run.mode)}</strong></div>
        <div><span>Formal status</span>${statusChip(run.formal_complete ? "Formal complete" : "Not complete")}</div>
      </div>
      <div class="run-metric-strip">
        <div><span>Ours AUROC</span><strong class="mono" title="${metric(run.ours_auroc)}">${metric(run.ours_auroc, 4)}</strong></div>
        <div><span>Paper AUROC</span><strong class="mono" title="${metric(run.paper_auroc)}">${metric(run.paper_auroc, 4)}</strong></div>
        <div><span>Δ</span><strong class="mono" title="${metric(run.difference)}">${metric(run.difference, 4)}</strong></div>
      </div>
      <div class="run-status-strip">
        <div><span>Mapping</span>${statusChip(run.mapping_status)}</div>
        <div><span>Bootstrap</span>${statusChip(run.bootstrap_status)}</div>
        <div><span>Sample availability</span>${statusChip(run.physical_sample_available ? "Sample data available" : "Sample data not packaged", run.physical_sample_available ? "status-info" : "status-neutral")}</div>
      </div>
      <div class="run-meta-strip">
        <div><span>Formal run ID</span><strong class="mono">${escapeHtml(run.formal_run_id)}</strong></div>
        <div><span>Records</span><strong>${escapeHtml(run.record_count || "Not packaged")}</strong></div>
        <div><span>Outputs</span><strong>${escapeHtml(run.output_dim || "Not available")}</strong></div>
      </div>`;
  }

  function renderMissing(run) {
    activeData = null;
    el("sample-browser").classList.add("hidden");
    el("comparison-panel").classList.add("hidden");
    const limited = run.review_mode === "PROVENANCE_ONLY_LIMITED";
    el("missing-card").classList.remove("hidden");
    el("missing-card").innerHTML = `
      <p class="eyebrow">Packaging limitation · formal run complete</p>
      <h2>Sample data not packaged</h2>
      <p><strong>${escapeHtml(run.model)} / ${escapeHtml(run.granularity)} / ${escapeHtml(run.mode)}</strong> remains part of the finalized 78-run benchmark, but its physical canonical sample bundle was not retained locally.</p>
      <div class="packaging-grid">
        <div><span>Formal run</span>${statusChip("Formal complete")}</div>
        <div><span>Sample bundle</span>${statusChip("Sample data not packaged", "status-neutral")}</div>
        <div><span>Mapping</span>${statusChip(run.mapping_status)}</div>
        <div><span>Review</span>${statusChip(run.review_mode, limited ? "status-warning" : "status-neutral")}</div>
      </div>
      <p>${limited ? "Record-level aggregation evidence remains available, but highest-grade prediction-to-target group provenance is incomplete." : "The formal result and mapping provenance remain available."} No inference, aggregation, or mapping was rerun solely for packaging.</p>`;
    setLoadStatus("Provenance only", "warning");
    updateReviewState();
  }

  function loadRunData(run) {
    if (!run.physical_sample_available || !run.data_shard_path) return Promise.resolve(null);
    if (dataCache.has(run.canonical_experiment_key)) return Promise.resolve(dataCache.get(run.canonical_experiment_key));
    if (loading.has(run.canonical_experiment_key)) return loading.get(run.canonical_experiment_key).promise;

    let resolvePromise;
    let rejectPromise;
    const promise = new Promise((resolve, reject) => { resolvePromise = resolve; rejectPromise = reject; });
    loading.set(run.canonical_experiment_key, { promise, resolve: resolvePromise, reject: rejectPromise });

    const script = document.createElement("script");
    script.src = run.data_shard_path;
    script.async = true;
    script.onload = () => {
      loading.delete(run.canonical_experiment_key);
      if (!dataCache.has(run.canonical_experiment_key)) rejectPromise(new Error("Shard loaded without registration"));
    };
    script.onerror = () => {
      loading.delete(run.canonical_experiment_key);
      rejectPromise(new Error(`Could not load ${run.data_shard_path}`));
    };
    document.head.appendChild(script);
    return promise;
  }

  async function selectRun(run, desiredState = {}) {
    if (!run) return;
    activeRun = run;
    renderRunSummary(run);
    renderProvenance(run);

    if (!run.physical_sample_available) {
      renderMissing(run);
      return;
    }

    el("missing-card").classList.add("hidden");
    setLoadStatus("Loading local shard…", "neutral");
    setSampleControlsDisabled(true);
    try {
      const payload = await loadRunData(run);
      if (activeRun !== run) return;
      activeData = payload;
      const requestedIndex = desiredState.ecgId == null ? -1 : payload.ecg_ids.findIndex((value) => String(value) === String(desiredState.ecgId));
      sampleIndex = requestedIndex >= 0 ? requestedIndex : 0;
      el("sample-browser").classList.remove("hidden");
      el("comparison-panel").classList.remove("hidden");
      setLoadStatus("Sample data loaded", "good");
      setSampleControlsDisabled(false);
      el("row-filter-select").value = run.granularity === "super" ? "all" : "top10";
      populateComparisonLabels(desiredState.label);
      renderSample();
    } catch (error) {
      console.error("Review shard load failed", error);
      setLoadStatus("Unable to load sample data", "warning");
      setSampleControlsDisabled(true);
      el("sample-browser").classList.add("hidden");
      el("comparison-panel").classList.add("hidden");
      el("missing-card").classList.remove("hidden");
      el("missing-card").innerHTML = `<p class="eyebrow">Review data unavailable</p><h2>Unable to load this review shard</h2><p>Try the optional local HTTP-server method described in <code>review_html/README.md</code>.</p>`;
    }
  }

  function sortedAndFilteredRows(labels, probabilities, targets) {
    let rows = labels.map((label, index) => ({
      label,
      probability: Number(probabilities[index]),
      target: Number(targets[index])
    }));

    const sort = el("sort-select").value;
    if (sort === "label") rows.sort((a, b) => a.label.localeCompare(b.label));
    else if (sort === "target") rows.sort((a, b) => (b.target - a.target) || (b.probability - a.probability));
    else rows.sort((a, b) => b.probability - a.probability);

    const view = el("row-filter-select").value;
    if (view === "positive") rows = rows.filter((row) => row.target === 1);
    else if (view === "top5") rows = rows.slice(0, 5);
    else if (view === "top10") rows = rows.slice(0, 10);
    return rows;
  }

  function renderSample() {
    if (!activeData) return;
    const labels = manifest.label_sets[activeRun.granularity];
    const probabilities = activeData.predictions[sampleIndex];
    const targets = activeData.targets[sampleIndex];
    const ecgId = String(activeData.ecg_ids[sampleIndex]);

    el("sample-position").textContent = `${sampleIndex + 1} / ${activeData.record_count}`;
    el("current-ecg-id").textContent = ecgId;
    el("ecg-search").value = ecgId;
    el("sample-message").textContent = "";

    const positives = labels.filter((label, index) => Number(targets[index]) === 1);
    el("positive-labels").textContent = positives.length ? positives.join(", ") : "None";

    const rows = sortedAndFilteredRows(labels, probabilities, targets);
    el("probability-body").innerHTML = rows.length ? rows.map((row) => `
      <tr class="${row.target === 1 ? "target-positive" : ""}">
        <td><button class="label-selector" type="button" data-label="${escapeHtml(row.label)}" title="Compare ${escapeHtml(row.label)} across modes">${escapeHtml(row.label)}</button></td>
        <td>${row.target === 1 ? '<span class="target-mark">Positive</span>' : "—"}</td>
        <td class="probability-cell mono" title="${escapeHtml(String(row.probability))}">${row.probability.toFixed(4)}</td>
        <td><div class="bar-track" aria-label="Probability ${escapeHtml(row.probability.toFixed(4))}"><div class="bar-fill" style="width:${Math.max(0, Math.min(100, row.probability * 100))}%"></div></div></td>
      </tr>`).join("") : '<tr><td colspan="4">No labels match the selected view.</td></tr>';

    renderComparison(ecgId);
    updateReviewState();
  }

  function populateComparisonLabels(preferredLabel) {
    const labels = manifest.label_sets[activeRun.granularity];
    const previous = preferredLabel || el("comparison-label-select").value;
    setOptions(el("comparison-label-select"), labels, labels.includes(previous) ? previous : labels[0]);
  }

  async function renderComparison(ecgId) {
    if (!activeRun || !activeData) return;
    const comparisonRunKey = activeRun.canonical_experiment_key;
    const selectedLabel = el("comparison-label-select").value;
    el("comparison-heading-label").textContent = selectedLabel || "Selected label";
    const labels = manifest.label_sets[activeRun.granularity];
    const labelIndex = labels.indexOf(selectedLabel);
    const relevantRuns = manifest.mode_order.map((mode) => manifest.runs.find((run) =>
      run.model === activeRun.model && run.granularity === activeRun.granularity && run.mode === mode
    )).filter(Boolean);
    const cards = [];

    for (const run of relevantRuns) {
      if (!run.physical_sample_available) {
        cards.push(`<article class="comparison-card unavailable"><span>${escapeHtml(run.mode)}</span><strong>Not packaged</strong><small>Sample bundle unavailable</small><div class="comparison-target">Review <b>${escapeHtml(displayStatus(run.review_mode))}</b></div></article>`);
        continue;
      }
      try {
        const data = await loadRunData(run);
        const index = data.ecg_ids.findIndex((value) => String(value) === String(ecgId));
        const probability = index >= 0 && labelIndex >= 0 ? Number(data.predictions[index][labelIndex]) : NaN;
        const target = index >= 0 && labelIndex >= 0 ? Number(data.targets[index][labelIndex]) : NaN;
        cards.push(`<article class="comparison-card"><span>${escapeHtml(run.mode)}</span><strong title="${Number.isFinite(probability) ? escapeHtml(String(probability)) : ""}">${Number.isFinite(probability) ? probability.toFixed(4) : "ECG not found"}</strong><small>Prediction probability</small><div class="comparison-target">Ground truth <b>${target === 1 ? "● Positive" : Number.isFinite(target) ? "—" : "Unavailable"}</b></div></article>`);
      } catch (error) {
        cards.push(`<article class="comparison-card unavailable"><span>${escapeHtml(run.mode)}</span><strong>Load unavailable</strong><small>Local shard could not be opened</small></article>`);
      }
    }

    if (activeRun && activeRun.canonical_experiment_key === comparisonRunKey && activeData && String(activeData.ecg_ids[sampleIndex]) === String(ecgId)) {
      el("comparison-grid").innerHTML = cards.join("");
      updateReviewState();
    }
  }

  function renderProvenance(run) {
    const references = (run.provenance_references || []).map((path) => window.location.protocol === "file:"
      ? `<a href="../${encodeURI(path)}">${escapeHtml(path)}</a>`
      : `<code>${escapeHtml(path)}</code>`).join("<br>") || "Not listed";
    const fields = [
      ["Canonical key", run.canonical_experiment_key],
      ["Formal run ID", run.formal_run_id],
      ["Formal status", run.formal_complete ? "COMPLETE" : "NOT COMPLETE"],
      ["Model", run.model],
      ["Granularity", run.granularity],
      ["Mode", run.mode],
      ["Output dimension", run.output_dim],
      ["Record count", run.record_count || "Not packaged"],
      ["Source sample SHA256", run.source_sample_sha256 || "Not packaged"],
      ["Mapping status", displayStatus(run.mapping_status)],
      ["Bootstrap status", displayStatus(run.bootstrap_status)],
      ["Ours AUROC", metric(run.ours_auroc)],
      ["Paper AUROC", metric(run.paper_auroc)],
      ["Difference", metric(run.difference)],
      ["Provenance", references]
    ];
    el("provenance-grid").innerHTML = fields.map(([label, value]) => `<div><dt>${escapeHtml(label)}</dt><dd>${label === "Provenance" ? value : escapeHtml(String(value))}</dd></div>`).join("");
  }

  function findEcg() {
    if (!activeData) return;
    const query = el("ecg-search").value.trim();
    const index = activeData.ecg_ids.findIndex((id) => String(id) === query);
    if (index < 0) {
      el("sample-message").textContent = `ECG ID ${query || "(empty)"} is not present in this run.`;
      return;
    }
    sampleIndex = index;
    renderSample();
  }

  function previousSample() {
    if (!activeData) return;
    sampleIndex = (sampleIndex - 1 + activeData.record_count) % activeData.record_count;
    renderSample();
  }

  function nextSample() {
    if (!activeData) return;
    sampleIndex = (sampleIndex + 1) % activeData.record_count;
    renderSample();
  }

  function randomSample() {
    if (!activeData) return;
    sampleIndex = Math.floor(Math.random() * activeData.record_count);
    renderSample();
  }

  function isTypingTarget(target) {
    if (!target) return false;
    const tag = String(target.tagName || "").toLowerCase();
    return ["input", "select", "textarea", "button"].includes(tag) || target.isContentEditable;
  }

  function bindEvents() {
    modelSelect.addEventListener("change", () => refreshSelectors("model"));
    granularitySelect.addEventListener("change", () => refreshSelectors("granularity"));
    modeSelect.addEventListener("change", () => refreshSelectors("mode"));
    runSelect.addEventListener("change", () => selectRun(manifest.runs.find((run) => run.formal_run_id === runSelect.value)));
    el("search-button").addEventListener("click", findEcg);
    el("ecg-search").addEventListener("keydown", (event) => { if (event.key === "Enter") findEcg(); });
    el("previous-button").addEventListener("click", previousSample);
    el("next-button").addEventListener("click", nextSample);
    el("random-button").addEventListener("click", randomSample);
    ["row-filter-select", "sort-select"].forEach((id) => el(id).addEventListener("change", renderSample));
    el("comparison-label-select").addEventListener("change", () => {
      if (!activeData) return;
      renderComparison(String(activeData.ecg_ids[sampleIndex]));
      updateReviewState();
    });
    el("probability-body").addEventListener("click", (event) => {
      const button = event.target.closest(".label-selector");
      if (!button || !activeData) return;
      const label = button.dataset.label;
      if (!Array.from(el("comparison-label-select").options).some((option) => option.value === label)) return;
      el("comparison-label-select").value = label;
      renderComparison(String(activeData.ecg_ids[sampleIndex]));
      updateReviewState();
    });
    document.addEventListener("keydown", (event) => {
      if (isTypingTarget(event.target)) return;
      if (event.key === "ArrowLeft") { event.preventDefault(); previousSample(); }
      else if (event.key === "ArrowRight") { event.preventDefault(); nextSample(); }
      else if (event.key.toLowerCase() === "r") { event.preventDefault(); randomSample(); }
      else if (event.key === "/") { event.preventDefault(); el("ecg-search").focus(); el("ecg-search").select(); }
    });
  }

  initializeTheme();
  bindEvents();
  initializeSelection();
})();
