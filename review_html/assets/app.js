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

  function systemTheme() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme, persist) {
    const selected = theme === "dark" ? "dark" : "light";
    document.documentElement.dataset.theme = selected;
    el("theme-toggle").setAttribute("aria-pressed", String(selected === "dark"));
    el("theme-label").textContent = selected === "dark" ? "Use light theme" : "Use dark theme";
    el("theme-toggle").setAttribute("aria-label", selected === "dark" ? "Switch to light theme" : "Switch to dark theme");
    if (persist) safeStorageSet("ecg-review-theme", selected);
  }

  function initializeTheme() {
    applyTheme(safeStorageGet("ecg-review-theme") || systemTheme(), false);
    el("theme-toggle").addEventListener("click", () => {
      applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark", true);
    });
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
    const fields = [
      ["Model", run.model],
      ["Granularity", run.granularity],
      ["Mode", run.mode],
      ["Formal run ID", run.formal_run_id, "mono"],
      ["Formal status", statusChip(run.formal_complete ? "Formal complete" : "Not complete")],
      ["Ours AUROC", metric(run.ours_auroc)],
      ["Paper AUROC", metric(run.paper_auroc)],
      ["Difference", metric(run.difference)],
      ["Mapping", statusChip(run.mapping_status)],
      ["Bootstrap", statusChip(run.bootstrap_status)],
      ["Physical sample", statusChip(run.physical_sample_available ? "Sample data available" : "Sample data not packaged", run.physical_sample_available ? "status-info" : "status-neutral")],
      ["Review mode", statusChip(run.review_mode, run.review_mode === "PROVENANCE_ONLY_LIMITED" ? "status-warning" : "status-neutral")],
      ["Record count", run.record_count || "Not packaged"],
      ["Output dimension", run.output_dim || "Not available"]
    ];
    const statusLabels = new Set(["Formal status", "Mapping", "Bootstrap", "Physical sample", "Review mode"]);
    el("run-summary").innerHTML = fields.map(([label, value, extraClass]) => `
      <div class="summary-field">
        <span>${escapeHtml(label)}</span>
        ${statusLabels.has(label) ? value : `<strong class="${extraClass || ""}">${escapeHtml(value)}</strong>`}
      </div>`).join("");
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
        <div><span>Physical sample data</span><strong>NOT PACKAGED</strong></div>
        <div><span>Mapping</span><strong>${escapeHtml(displayStatus(run.mapping_status))}</strong></div>
        <div><span>Review mode</span><strong>${escapeHtml(displayStatus(run.review_mode))}</strong></div>
      </div>
      <p>${limited ? "Record-level aggregation evidence remains available, but highest-grade prediction-to-target group provenance is incomplete." : "The formal result and mapping provenance remain available."} No inference, aggregation, or mapping was rerun solely for packaging.</p>`;
    setLoadStatus("Provenance only", "warning");
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

  async function selectRun(run) {
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
      sampleIndex = 0;
      el("sample-browser").classList.remove("hidden");
      el("comparison-panel").classList.remove("hidden");
      setLoadStatus("Sample data loaded", "good");
      setSampleControlsDisabled(false);
      populateComparisonLabels();
      renderSample();
    } catch (error) {
      setLoadStatus("Local shard load failed", "warning");
      setSampleControlsDisabled(true);
      el("sample-browser").classList.add("hidden");
      el("comparison-panel").classList.add("hidden");
      el("missing-card").classList.remove("hidden");
      el("missing-card").innerHTML = `<p class="eyebrow">Local loading issue</p><h2>Data shard could not be opened</h2><p>${escapeHtml(error.message)}</p><p>Try the optional local HTTP-server method described in <code>review_html/README.md</code>.</p>`;
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
        <td>${escapeHtml(row.label)}</td>
        <td>${row.target === 1 ? '<span class="target-mark">Positive</span>' : "—"}</td>
        <td class="probability-cell mono">${row.probability.toFixed(4)}</td>
        <td><div class="bar-track" aria-label="Probability ${escapeHtml(row.probability.toFixed(4))}"><div class="bar-fill" style="width:${Math.max(0, Math.min(100, row.probability * 100))}%"></div></div></td>
      </tr>`).join("") : '<tr><td colspan="4">No labels match the selected view.</td></tr>';

    renderComparison(ecgId);
  }

  function populateComparisonLabels() {
    const labels = manifest.label_sets[activeRun.granularity];
    const previous = el("comparison-label-select").value;
    setOptions(el("comparison-label-select"), labels, labels.includes(previous) ? previous : labels[0]);
  }

  async function renderComparison(ecgId) {
    if (!activeRun || !activeData) return;
    const comparisonRunKey = activeRun.canonical_experiment_key;
    const selectedLabel = el("comparison-label-select").value;
    const labels = manifest.label_sets[activeRun.granularity];
    const labelIndex = labels.indexOf(selectedLabel);
    const relevantRuns = manifest.mode_order.map((mode) => manifest.runs.find((run) =>
      run.model === activeRun.model && run.granularity === activeRun.granularity && run.mode === mode
    )).filter(Boolean);
    const cards = [];

    for (const run of relevantRuns) {
      if (!run.physical_sample_available) {
        cards.push(`<article class="comparison-card unavailable"><span>${escapeHtml(run.mode)}</span><strong>Not packaged</strong><small>${escapeHtml(displayStatus(run.review_mode))}</small></article>`);
        continue;
      }
      try {
        const data = await loadRunData(run);
        const index = data.ecg_ids.findIndex((value) => String(value) === String(ecgId));
        const probability = index >= 0 && labelIndex >= 0 ? Number(data.predictions[index][labelIndex]) : NaN;
        cards.push(`<article class="comparison-card"><span>${escapeHtml(run.mode)}</span><strong>${Number.isFinite(probability) ? probability.toFixed(4) : "ECG not found"}</strong><small>${escapeHtml(selectedLabel)}</small></article>`);
      } catch (error) {
        cards.push(`<article class="comparison-card unavailable"><span>${escapeHtml(run.mode)}</span><strong>Load unavailable</strong><small>Local shard could not be opened</small></article>`);
      }
    }

    if (activeRun && activeRun.canonical_experiment_key === comparisonRunKey && activeData && String(activeData.ecg_ids[sampleIndex]) === String(ecgId)) {
      el("comparison-grid").innerHTML = cards.join("");
    }
  }

  function renderProvenance(run) {
    const references = (run.provenance_references || []).map((path) => `<a href="../${encodeURI(path)}">${escapeHtml(path)}</a>`).join("<br>") || "Not listed";
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
    el("random-button").addEventListener("click", () => {
      if (!activeData) return;
      sampleIndex = Math.floor(Math.random() * activeData.record_count);
      renderSample();
    });
    ["row-filter-select", "sort-select"].forEach((id) => el(id).addEventListener("change", renderSample));
    el("comparison-label-select").addEventListener("change", () => activeData && renderComparison(String(activeData.ecg_ids[sampleIndex])));
    document.addEventListener("keydown", (event) => {
      if (isTypingTarget(event.target)) return;
      if (event.key === "ArrowLeft") { event.preventDefault(); previousSample(); }
      else if (event.key === "ArrowRight") { event.preventDefault(); nextSample(); }
      else if (event.key === "/") { event.preventDefault(); el("ecg-search").focus(); el("ecg-search").select(); }
    });
  }

  initializeTheme();
  bindEvents();
  refreshSelectors("model");
})();
