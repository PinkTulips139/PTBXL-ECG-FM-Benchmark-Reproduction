"use strict";

(function () {
  const manifest = window.ECG_REVIEW_MANIFEST;
  if (!manifest || !Array.isArray(manifest.runs)) {
    document.body.innerHTML = "<main><h1>Reviewer manifest unavailable</h1><p>Expected review_html/data/manifest.js.</p></main>";
    return;
  }

  const byKey = new Map(manifest.runs.map((run) => [run.canonical_experiment_key, run]));
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

  window.ECGReviewRegisterRunData = function (payload) {
    if (!payload || !payload.canonical_experiment_key) return;
    dataCache.set(payload.canonical_experiment_key, payload);
    const pending = loading.get(payload.canonical_experiment_key);
    if (pending) pending.resolve(payload);
  };

  function unique(values) {
    return [...new Set(values)];
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
    const allModels = manifest.model_order.filter((m) => manifest.runs.some((r) => r.model === m));
    if (!modelSelect.options.length) setOptions(modelSelect, allModels, allModels[0]);

    const modelRuns = manifest.runs.filter((r) => r.model === modelSelect.value);
    const grans = manifest.granularity_order.filter((g) => modelRuns.some((r) => r.granularity === g));
    if (changed === "model" || !grans.includes(granularitySelect.value)) setOptions(granularitySelect, grans, grans[0]);

    const granRuns = modelRuns.filter((r) => r.granularity === granularitySelect.value);
    const modes = manifest.mode_order.filter((m) => granRuns.some((r) => r.mode === m));
    if (["model", "granularity"].includes(changed) || !modes.includes(modeSelect.value)) setOptions(modeSelect, modes, modes[0]);

    const runs = filteredRuns();
    setOptions(runSelect, runs.map((r) => r.formal_run_id), runs[0]?.formal_run_id);
    selectRun(runs[0]);
  }

  function setLoadStatus(text, kind) {
    const node = el("load-status");
    node.textContent = text;
    node.className = `status-pill ${kind}`;
  }

  function metric(value, digits = 6) {
    const n = Number(value);
    return Number.isFinite(n) ? n.toFixed(digits) : "Not available";
  }

  function renderRunSummary(run) {
    const items = [
      ["Formal status", run.formal_complete ? "COMPLETE" : "NOT COMPLETE"],
      ["Physical sample", run.physical_sample_available ? "PACKAGED" : "NOT PACKAGED"],
      ["Ours AUROC", metric(run.ours_auroc)],
      ["Paper AUROC", metric(run.paper_auroc)],
      ["Difference", metric(run.difference)],
      ["Review mode", run.review_mode]
    ];
    el("run-summary").innerHTML = items.map(([k, v]) => `<div><span>${escapeHtml(k)}</span><strong>${escapeHtml(v)}</strong></div>`).join("");
  }

  function renderMissing(run) {
    activeData = null;
    el("sample-browser").classList.add("hidden");
    el("comparison-panel").classList.add("hidden");
    const limited = run.review_mode === "PROVENANCE_ONLY_LIMITED";
    el("missing-card").classList.remove("hidden");
    el("missing-card").innerHTML = `
      <p class="eyebrow">Formal run complete</p>
      <h2>Sample data not packaged</h2>
      <p><strong>Physical sample data:</strong> NOT PACKAGED<br>
      <strong>Mapping:</strong> ${escapeHtml(run.mapping_status)}<br>
      <strong>Review mode:</strong> ${escapeHtml(run.review_mode)}</p>
      <p>${limited ? "Record-level aggregation evidence remains available, but highest-grade prediction-to-target group provenance is incomplete." : "Formal result and mapping provenance remain available."} The physical canonical sample bundle was not retained locally. No recomputation was performed solely for packaging.</p>`;
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
    try {
      const payload = await loadRunData(run);
      if (activeRun !== run) return;
      activeData = payload;
      sampleIndex = 0;
      el("sample-browser").classList.remove("hidden");
      el("comparison-panel").classList.remove("hidden");
      setLoadStatus("Sample data loaded", "good");
      populateComparisonLabels();
      renderSample();
    } catch (error) {
      setLoadStatus("Local shard load failed", "warning");
      el("missing-card").classList.remove("hidden");
      el("missing-card").innerHTML = `<h2>Local data shard could not be opened</h2><p>${escapeHtml(error.message)}</p><p>Try the optional local HTTP-server method described in review_html/README.md.</p>`;
    }
  }

  function renderSample() {
    if (!activeData) return;
    const labels = manifest.label_sets[activeRun.granularity];
    const probs = activeData.predictions[sampleIndex];
    const targets = activeData.targets[sampleIndex];
    const id = String(activeData.ecg_ids[sampleIndex]);
    el("sample-position").textContent = `${sampleIndex + 1} / ${activeData.record_count}`;
    el("current-ecg-id").textContent = id;
    el("ecg-search").value = id;
    const positives = labels.filter((_, i) => Number(targets[i]) === 1);
    el("positive-labels").textContent = positives.length ? positives.join(", ") : "None";

    let rows = labels.map((label, i) => ({ label, probability: Number(probs[i]), target: Number(targets[i]) }));
    if (el("positive-only").checked) rows = rows.filter((row) => row.target === 1);
    if (el("sort-select").value === "label") rows.sort((a, b) => a.label.localeCompare(b.label));
    else rows.sort((a, b) => b.probability - a.probability);
    const topK = el("topk-select").value;
    if (topK !== "all") rows = rows.slice(0, Number(topK));
    el("probability-body").innerHTML = rows.map((row) => `
      <tr class="${row.target === 1 ? "target-positive" : ""}">
        <td>${escapeHtml(row.label)}</td>
        <td>${row.target === 1 ? "Positive" : "—"}</td>
        <td class="probability-cell">${row.probability.toFixed(4)}</td>
        <td><div class="bar-track"><div class="bar-fill" style="width:${Math.max(0, Math.min(100, row.probability * 100))}%"></div></div></td>
      </tr>`).join("");
    renderComparison(id);
  }

  function populateComparisonLabels() {
    const labels = manifest.label_sets[activeRun.granularity];
    const previous = el("comparison-label-select").value;
    setOptions(el("comparison-label-select"), labels, labels.includes(previous) ? previous : labels[0]);
  }

  async function renderComparison(ecgId) {
    if (!activeRun || !activeData) return;
    const selectedLabel = el("comparison-label-select").value;
    const labels = manifest.label_sets[activeRun.granularity];
    const labelIndex = labels.indexOf(selectedLabel);
    const relevant = manifest.mode_order.map((mode) => manifest.runs.find((run) =>
      run.model === activeRun.model && run.granularity === activeRun.granularity && run.mode === mode
    )).filter(Boolean);
    const cards = [];
    for (const run of relevant) {
      if (!run.physical_sample_available) {
        cards.push(`<article class="comparison-card unavailable"><span>${escapeHtml(run.mode)}</span><strong>Not packaged</strong><small>${escapeHtml(run.review_mode)}</small></article>`);
        continue;
      }
      try {
        const data = await loadRunData(run);
        const idx = data.ecg_ids.findIndex((value) => String(value) === String(ecgId));
        const probability = idx >= 0 && labelIndex >= 0 ? Number(data.predictions[idx][labelIndex]) : NaN;
        cards.push(`<article class="comparison-card"><span>${escapeHtml(run.mode)}</span><strong>${Number.isFinite(probability) ? probability.toFixed(4) : "ECG not found"}</strong><small>${escapeHtml(selectedLabel)}</small></article>`);
      } catch (error) {
        cards.push(`<article class="comparison-card unavailable"><span>${escapeHtml(run.mode)}</span><strong>Load unavailable</strong></article>`);
      }
    }
    if (activeData && String(activeData.ecg_ids[sampleIndex]) === String(ecgId)) el("comparison-grid").innerHTML = cards.join("");
  }

  function renderProvenance(run) {
    const refs = (run.provenance_references || []).map((path) => `<a href="../${encodeURI(path)}">${escapeHtml(path)}</a>`).join("<br>") || "Not listed";
    const items = [
      ["Canonical key", run.canonical_experiment_key], ["Formal run ID", run.formal_run_id],
      ["Formal status", run.formal_complete ? "COMPLETE" : "NOT COMPLETE"], ["Model", run.model],
      ["Granularity", run.granularity], ["Mode", run.mode], ["Output dimension", run.output_dim],
      ["Record count", run.record_count || "Not packaged"], ["Source sample SHA256", run.source_sample_sha256 || "Not packaged"],
      ["Mapping status", run.mapping_status], ["Bootstrap status", run.bootstrap_status],
      ["Ours AUROC", metric(run.ours_auroc)], ["Paper AUROC", metric(run.paper_auroc)],
      ["Difference", metric(run.difference)], ["Provenance", refs]
    ];
    el("provenance-grid").innerHTML = items.map(([k, v]) => `<div><dt>${escapeHtml(k)}</dt><dd>${k === "Provenance" ? v : escapeHtml(String(v))}</dd></div>`).join("");
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  }

  modelSelect.addEventListener("change", () => refreshSelectors("model"));
  granularitySelect.addEventListener("change", () => refreshSelectors("granularity"));
  modeSelect.addEventListener("change", () => refreshSelectors("mode"));
  runSelect.addEventListener("change", () => selectRun(manifest.runs.find((r) => r.formal_run_id === runSelect.value)));
  el("search-button").addEventListener("click", () => {
    if (!activeData) return;
    const query = el("ecg-search").value.trim();
    const index = activeData.ecg_ids.findIndex((id) => String(id) === query);
    if (index < 0) { el("sample-message").textContent = `ECG ID ${query || "(empty)"} is not present in this run.`; return; }
    el("sample-message").textContent = ""; sampleIndex = index; renderSample();
  });
  el("ecg-search").addEventListener("keydown", (event) => { if (event.key === "Enter") el("search-button").click(); });
  el("previous-button").addEventListener("click", () => { if (activeData) { sampleIndex = (sampleIndex - 1 + activeData.record_count) % activeData.record_count; renderSample(); } });
  el("next-button").addEventListener("click", () => { if (activeData) { sampleIndex = (sampleIndex + 1) % activeData.record_count; renderSample(); } });
  el("random-button").addEventListener("click", () => { if (activeData) { sampleIndex = Math.floor(Math.random() * activeData.record_count); renderSample(); } });
  ["topk-select", "sort-select", "positive-only"].forEach((id) => el(id).addEventListener("change", renderSample));
  el("comparison-label-select").addEventListener("change", () => activeData && renderComparison(String(activeData.ecg_ids[sampleIndex])));

  refreshSelectors("model");
})();
